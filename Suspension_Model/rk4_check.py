"""Classical fixed-step RK4 comparator for the quarter-car model (SI units).

Course adaptation: MMA3001_Notes_Week07_4_Runge_Kutta_Methods.ipynb,
one-based cells 12 and 17 (zero-based 11 and 16). The taught four stage rates
and 1:2:2:1 weights are unchanged. Its scalar step/loop are extended to a
four-component state, with explicit bump-exit splitting, finite-value checks
and stored grid output. Each segment's final step may be shortened to land
exactly on its endpoint; there is no adaptive error estimate or dense output.

The governing forces are shared through quarter_car.rhs, so agreement with
RK45 cross-checks the integration method, not the physical equations themselves.
This is bounded simulator verification, not an ML dataset generator.
"""

from dataclasses import dataclass
from time import perf_counter

import numpy as np

from quarter_car import Bump, Parameters, rhs


def _finite_scalar(name, value, positive=False):
    """Validate a real scalar and return float; otherwise raise ValueError."""
    number = np.asarray(value, dtype=float)
    if number.ndim != 0 or not np.isfinite(number) or (positive and number <= 0):
        requirement = "finite and positive" if positive else "finite"
        raise ValueError(f"{name} must be a {requirement} scalar")
    return float(number)


def rk4_step(derivative, time_s, state, step_s):
    """Advance one classical RK4 step, returning (new_state, 4).

    Parameters
    ----------
    derivative : callable
        Function f(time_s, state) returning a same-shaped 1-D derivative.
        Its physical units are each state component's units per second.
    time_s : float
        Finite starting time [s].
    state : array-like
        Nonempty finite 1-D vector. The returned vector has the same shape.
    step_s : float
        Finite positive step length [s].

    Raises
    ------
    ValueError
        For an invalid starting time, state or step length.
    RuntimeError
        For malformed/nonfinite derivative output or nonfinite evolved states.

    Notes
    -----
    Evaluate f at both midpoint trial states and the endpoint. This also
    evaluates time-dependent road forcing at each stage's own time.
    """
    time_s = _finite_scalar("time_s", time_s)
    step_s = _finite_scalar("step_s", step_s, positive=True)
    q = np.asarray(state, dtype=float)
    if q.ndim != 1 or not q.size or not np.all(np.isfinite(q)):
        raise ValueError("state must be a nonempty finite 1-D vector")
    if not np.isfinite(time_s + step_s) or time_s + step_s <= time_s:
        raise ValueError("step_s must advance to a finite distinct time")

    def rate(t, trial):
        value = np.asarray(derivative(t, trial), dtype=float)
        if value.shape != q.shape or not np.all(np.isfinite(value)):
            raise RuntimeError("RK4 derivative must be finite and match the state shape")
        return value

    try:
        with np.errstate(over="raise", invalid="raise"):
            k1 = rate(time_s, q)
            k2 = rate(time_s + step_s / 2, q + step_s * k1 / 2)
            k3 = rate(time_s + step_s / 2, q + step_s * k2 / 2)
            k4 = rate(time_s + step_s, q + step_s * k3)
            next_state = q + step_s * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    except FloatingPointError as error:
        raise RuntimeError("RK4 produced a nonfinite intermediate state") from error
    if not np.all(np.isfinite(next_state)):
        raise RuntimeError("RK4 produced a nonfinite state")
    return next_state, 4


def _segment_times(start_s, end_s, dt_s):
    """Build fixed nominal steps with a possible shortened endpoint step."""
    span_steps = (end_s - start_s) / dt_s
    if not np.isfinite(span_steps):
        raise ValueError("dt_s is too small for this time interval")
    whole_steps = int(np.floor(span_steps))
    time = start_s + dt_s * np.arange(whole_steps + 1, dtype=float)
    endpoint_tolerance = 16 * np.finfo(float).eps * max(1.0, abs(end_s))
    if time.size > 1 and abs(time[-1] - end_s) <= endpoint_tolerance:
        time[-1] = end_s
    else:
        time = np.append(time, end_s)
    if np.any(np.diff(time) <= 0):
        raise ValueError("dt_s cannot produce distinct increasing time samples")
    return time


@dataclass(frozen=True)
class RK4Segment:
    """One completed segment; t [s], y [m,m/s,m,m/s], and work count."""

    t: np.ndarray
    y: np.ndarray
    nfev: int
    success: bool = True
    status: int = 0


@dataclass(frozen=True)
class RK4Trajectory:
    """Native-grid RK4 result compatible with quarter_car.summarise.

    nfev is four derivative calls per accepted step; elapsed_s measures only
    integration and its required checks, excluding output analysis and plots.
    """

    parameters: Parameters
    bump: Bump
    end_time_s: float
    dt_s: float
    segments: tuple
    elapsed_s: float

    @property
    def nfev(self):
        """Return the total number of evaluated derivative vectors."""
        return sum(segment.nfev for segment in self.segments)

    def sample(self, dt_s):
        """Return (t, q) from stored nodes, with q shaped (4, n).

        dt_s [s] must equal the native step or be an integer multiple of it.
        Coarser sampling takes that stride separately in each segment and keeps
        bump exit and the final endpoint. Short endpoint intervals can therefore
        remain. No interpolation is performed: finer or nonmultiple requests,
        and nonfinite/nonpositive intervals, raise ValueError.
        """
        dt_s = _finite_scalar("dt_s", dt_s, positive=True)
        ratio = dt_s / self.dt_s
        if not np.isfinite(ratio):
            raise ValueError("requested sampling stride is not finite")
        stride = int(round(ratio))
        if stride < 1 or not np.isclose(ratio, stride, rtol=1e-12, atol=1e-12):
            raise ValueError("sample step must be the native RK4 step or an integer multiple")
        times, states = [], []
        for number, segment in enumerate(self.segments):
            indices = np.arange(0, segment.t.size, stride)
            if indices[-1] != segment.t.size - 1:
                indices = np.append(indices, segment.t.size - 1)
            if number:
                indices = indices[1:]  # Bump exit is already in the first segment.
            times.append(segment.t[indices])
            states.append(segment.y[:, indices])
        return np.concatenate(times), np.concatenate(states, axis=1)


def simulate_rk4(parameters, bump, end_time_s, dt_s):
    """Integrate one equilibrium-start quarter-car with classical vector RK4.

    Parameters
    ----------
    parameters : quarter_car.Parameters
        Positive finite masses, stiffnesses, damping and gravity in SI units.
    bump : quarter_car.Bump
        Prescribed raised-cosine road; zero height is allowed for verification.
    end_time_s : float
        Finite end time [s], strictly later than bump exit.
    dt_s : float
        Positive finite nominal integration step [s]. Planned comparisons use
        0.0005 and 0.00025 s. A large step can be unstable; finite output alone
        is not evidence of accuracy or stability.

    Returns
    -------
    RK4Trajectory
        Two segments starting from [0,0,0,0], with the complete four-state exit
        vector carried forward. Use sample(dt_s) for stored native output.

    Raises
    ------
    ValueError
        For wrong parameter/bump types, invalid physical values or time controls.
    RuntimeError
        If the step calculation produces nonfinite states or derivatives.

    Notes
    -----
    Custom initial states and dense interpolation are deliberately unsupported.
    Use rk4_step for separate generic-ODE verification with an initial vector.
    """
    if not isinstance(parameters, Parameters) or not isinstance(bump, Bump):
        raise ValueError("parameters and bump must be Parameters and Bump instances")
    # Recheck values at this entry point as well as the dataclass constructors.
    for name, value in vars(parameters).items():
        _finite_scalar(name, value, positive=True)
    height = _finite_scalar("height_m", bump.height_m)
    if height < 0:
        raise ValueError("height_m must be nonnegative")
    tau = _finite_scalar("duration_s", bump.duration_s, positive=True)
    end_time_s = _finite_scalar("end_time_s", end_time_s, positive=True)
    dt_s = _finite_scalar("dt_s", dt_s, positive=True)
    if end_time_s <= tau:
        raise ValueError("end_time_s must exceed bump duration")
    grids = (_segment_times(0.0, tau, dt_s), _segment_times(tau, end_time_s, dt_s))
    state = np.zeros(4)
    segments = []

    def derivative(time_s, current_state):
        return rhs(time_s, current_state, parameters, bump)

    started = perf_counter()
    for time in grids:
        values = np.empty((4, time.size))
        values[:, 0] = state
        evaluations = 0
        for index in range(time.size - 1):
            step = time[index + 1] - time[index]
            state, calls = rk4_step(derivative, time[index], state, step)
            values[:, index + 1] = state
            evaluations += calls
        segments.append(RK4Segment(time, values, evaluations))
        state = values[:, -1].copy()
    elapsed_s = perf_counter() - started
    return RK4Trajectory(parameters, bump, end_time_s, dt_s, tuple(segments), elapsed_s)
