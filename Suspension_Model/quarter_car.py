"""Passive quarter-car about static equilibrium; all calculations use SI units.

Sources: Project_Setup/EVIDENCE.md S002 (forces), S003 (bump shape), S004
(nominal parameters), C001/C002 (vector RK45). Original course files are intact.
State order is ALWAYS [body position, body velocity, wheel position, wheel velocity].
"""

from dataclasses import dataclass
from time import perf_counter

import numpy as np
from scipy.integrate import solve_ivp


def _positive(name, value):
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class Parameters:
    """Masses [kg], stiffnesses [N/m], damping [N s/m], gravity [m/s²].

    Positive finite values are required; invalid values raise ValueError.
    These defaults describe a generic vehicle corner, not the Ferrari telemetry.
    """

    ms: float = 365.4
    mu: float = 43.0
    ks: float = 24000.0
    cs: float = 2126.4
    kt: float = 350000.0
    g: float = 9.81

    def __post_init__(self):
        for name, value in vars(self).items():
            _positive(name, value)


@dataclass(frozen=True)
class Bump:
    """Raised-cosine height [m] and crossing duration [s].

    Height may be zero for the equilibrium check; negative/nonfinite heights or
    nonpositive/nonfinite durations raise ValueError.
    """

    height_m: float = 0.050
    duration_s: float = 0.50

    def __post_init__(self):
        if not np.isfinite(self.height_m) or self.height_m < 0:
            raise ValueError("height_m must be finite and nonnegative")
        _positive("duration_s", self.duration_s)


@dataclass(frozen=True)
class SolverSettings:
    """RK45 controls: dimensionless rtol, state-unit atol, max step [s].

    atol follows [m, m/s, m, m/s]. Invalid settings raise ValueError.
    These are local-error controls, not certified errors on the reported peaks.
    """

    rtol: float = 1e-6
    atol: tuple = (1e-9, 1e-8, 1e-9, 1e-8)
    max_step_s: float = 0.005

    def __post_init__(self):
        _positive("rtol", self.rtol)
        _positive("max_step_s", self.max_step_s)
        values = np.asarray(self.atol)
        if values.shape != (4,) or not np.all(np.isfinite(values)) or np.any(values <= 0):
            raise ValueError("atol must contain four finite positive tolerances")


def road_height(time_s, bump):
    """Return road height [m] for scalar/array time [s] and a Bump.

    The road is flat outside [0, duration_s]. Nonfinite times raise ValueError.
    """
    t = np.asarray(time_s, dtype=float)
    if not np.all(np.isfinite(t)):
        raise ValueError("time_s must be finite")
    # Evaluate only within the bump; h is its peak height, hence the factor 1/2.
    r = np.zeros_like(t)
    inside = (t >= 0) & (t <= bump.duration_s)
    r[inside] = 0.5 * bump.height_m * (1 - np.cos(2 * np.pi * t[inside] / bump.duration_s))
    return float(r) if r.ndim == 0 else r


def rhs(time_s, state, parameters, bump):
    """Return [vs, as, vu, au] in [m/s, m/s², m/s, m/s²].

    state must be a finite four-vector [zs, vs, zu, vu]; time is in seconds.
    Invalid state/time raises ValueError. Positive zs-zu means extension.
    Gravity is absent here because positions are measured from static equilibrium.
    """
    q = np.asarray(state, dtype=float)
    if q.shape != (4,) or not np.all(np.isfinite(q)):
        raise ValueError("state must be a finite four-vector")
    zs, vs, zu, vu = q
    p = parameters
    # This force acts downward on the body and equally upward on the wheel.
    suspension_force = p.ks * (zs - zu) + p.cs * (vs - vu)
    tyre_dynamic_force = p.kt * (road_height(time_s, bump) - zu)
    return np.array([vs, -suspension_force / p.ms, vu,
                     (suspension_force + tyre_dynamic_force) / p.mu])


@dataclass
class Trajectory:
    """Two successful RK45 segments sharing the same full state at bump exit."""

    parameters: Parameters
    bump: Bump
    settings: SolverSettings
    end_time_s: float
    segments: tuple
    elapsed_s: float

    @property
    def nfev(self):
        """Total derivative evaluations across both segments [count]."""
        return sum(segment.nfev for segment in self.segments)

    def state_at(self, times_s):
        """Return states (4,n) at a finite 1-D array of times within the run.

        Dense output interpolates the solver's trajectory without integrating again.
        Out-of-range or malformed times raise ValueError; nonfinite output raises
        RuntimeError. No extrapolation beyond the observed run is allowed.
        """
        t = np.asarray(times_s, dtype=float)
        if t.ndim != 1 or not np.all(np.isfinite(t)) or np.any(t < 0) or np.any(t > self.end_time_s):
            raise ValueError("times must be a finite 1-D array within the simulation")
        q = np.empty((4, t.size))
        first = t <= self.bump.duration_s
        for mask, segment in ((first, self.segments[0]), (~first, self.segments[1])):
            if np.any(mask):
                q[:, mask] = segment.sol(t[mask])
        if not np.all(np.isfinite(q)):
            raise RuntimeError("nonfinite interpolated states")
        return q

    def sample(self, dt_s):
        """Return time [s] and state (4,n) on a grid no coarser than dt_s.

        Each segment includes its endpoints, including exact bump exit. dt_s must
        be finite and positive, otherwise ValueError is raised.
        """
        _positive("dt_s", dt_s)
        tau = self.bump.duration_s
        first = np.linspace(0, tau, int(np.ceil(tau / dt_s)) + 1)
        second = np.linspace(tau, self.end_time_s,
                             int(np.ceil((self.end_time_s - tau) / dt_s)) + 1)
        t = np.concatenate((first, second[1:]))
        return t, self.state_at(t)


def simulate(parameters=Parameters(), bump=Bump(), end_time_s=5.0,
             settings=SolverSettings(), initial_state=None):
    """Integrate one setup, returning a Trajectory with time/work measurements.

    end_time_s [s] must exceed bump duration. initial_state defaults to equilibrium
    rest and otherwise must be a finite four-vector in [m,m/s,m,m/s]. Invalid
    inputs raise ValueError; failed/incomplete/nonfinite solves raise RuntimeError.
    The complete exit state is passed unchanged to the flat-road segment.
    """
    _positive("end_time_s", end_time_s)
    if end_time_s <= bump.duration_s:
        raise ValueError("end_time_s must exceed bump duration")
    q = np.zeros(4) if initial_state is None else np.asarray(initial_state, dtype=float)
    if q.shape != (4,) or not np.all(np.isfinite(q)):
        raise ValueError("initial_state must be a finite four-vector")
    segments = []
    started = perf_counter()
    for start, end in ((0.0, bump.duration_s), (bump.duration_s, end_time_s)):
        solution = solve_ivp(rhs, (start, end), q, args=(parameters, bump),
                             method="RK45", dense_output=True, rtol=settings.rtol,
                             atol=settings.atol, max_step=settings.max_step_s)
        if not solution.success or solution.status != 0 or solution.t[-1] != end:
            raise RuntimeError(f"incomplete RK45 solve: {solution.message}")
        if not np.all(np.isfinite(solution.y)):
            raise RuntimeError("nonfinite solver states")
        segments.append(solution)
        q = solution.y[:, -1].copy()  # positions AND velocities survive bump exit
    return Trajectory(parameters, bump, settings, end_time_s, tuple(segments),
                      perf_counter() - started)


def post_bump_energy(state, parameters):
    """Return flat-road mechanical energy [J] for state (4,) or (4,n).

    Valid only when road height is zero. Includes both masses and both springs.
    """
    zs, vs, zu, vu = np.asarray(state)
    p = parameters
    return 0.5 * (p.ms * vs**2 + p.mu * vu**2 + p.ks * (zs - zu)**2 + p.kt * zu**2)


def contact_force(time_s, state, parameters, bump):
    """Return total tyre normal force [N], including the static weight.

    time_s and state may describe one state or matching arrays. A nonpositive
    force flags a failed contact assumption; it is never silently clipped.
    """
    p = parameters
    return (p.ms + p.mu) * p.g + p.kt * (road_height(time_s, bump) - np.asarray(state)[2])


def settling_candidate(time_s, displacement_m, exit_s, band_m=0.001, confirmation_s=1.0):
    """Find sustained sampled band entry; return absolute entry time [s] or None.

    time_s must increase strictly and contain exit_s exactly; displacement_m must
    be a matching finite 1-D array [m]. Use the last outside-band excursion,
    interpolating its signed boundary crossing. Require confirmation_s inside
    the band after entry. Invalid inputs raise ValueError. This alone does not
    certify settling: summarise adds an energy tail check, and the runner checks
    grid, solver and horizon agreement.
    """
    t, d = np.asarray(time_s), np.asarray(displacement_m)
    _positive("band_m", band_m)
    _positive("confirmation_s", confirmation_s)
    if (t.ndim != 1 or t.size < 2 or d.shape != t.shape
            or not np.all(np.isfinite(t)) or not np.all(np.isfinite(d))
            or np.any(np.diff(t) <= 0) or not np.any(t == exit_s)):
        raise ValueError("invalid time/displacement arrays or missing bump exit")
    post = t >= exit_s
    t, d = t[post], d[post]
    outside = np.flatnonzero(np.abs(d) > band_m)
    if outside.size == 0:
        entry = float(exit_s)
    else:
        j = int(outside[-1])
        if j == t.size - 1:
            return None
        boundary = np.copysign(band_m, d[j])
        fraction = (boundary - d[j]) / (d[j + 1] - d[j])
        entry = float(t[j] + fraction * (t[j + 1] - t[j]))
    return entry if t[-1] - entry >= confirmation_s else None


def summarise(trajectory, dt_s=0.001, band_m=0.001, confirmation_s=1.0):
    """Return JSON-ready peak/contact/energy/settling diagnostics for one run.

    Peaks are sampled estimates in metres (including the complete post-bump
    response). Settling stays 'candidate' until independent refinement/extension
    checks pass. An unresolved time is None, never the observation cutoff.
    Tail bound B=sqrt(2H/ks) follows H'=-cs*(vs-vu)^2 for the exact flat-road model;
    evaluated on numerical states, it is a consistency check, not certification.
    """
    t, q = trajectory.sample(dt_s)
    p, bump = trajectory.parameters, trajectory.bump
    d = q[0] - q[2]
    post_indices = np.flatnonzero(t >= bump.duration_s)
    j = int(np.argmax(np.abs(d)))
    jp = int(post_indices[np.argmax(np.abs(d[post_indices]))])
    a, ap = float(abs(d[j])), float(abs(d[jp]))
    energy = post_bump_energy(q[:, post_indices], p)
    bound = float(np.sqrt(2 * energy[-1] / p.ks))
    exact_zero = bool(np.all(q == 0) and bump.height_m == 0)
    tail_limit = min(0.0005, a / 2, ap / 2)
    tail_ok = exact_zero or bound < tail_limit
    entry = settling_candidate(t, d, bump.duration_s, band_m, confirmation_s)
    # A stricter user-selected band also needs its own future-motion bound.
    candidate = entry is not None and tail_ok and bound < band_m
    normal_force = contact_force(t, q, p, bump)
    energy_allowance = 1e-10 * max(1.0, float(energy[0]))
    maximum_increase = float(max(0.0, np.max(np.diff(energy))))
    return {
        "end_time_s": trajectory.end_time_s, "observation_dt_s": dt_s,
        "A_m": a, "A_time_s": float(t[j]), "A_signed_m": float(d[j]),
        "A_post_m": ap, "A_post_time_s": float(t[jp]),
        "settling_status": "candidate" if candidate else "unresolved",
        "settling_after_exit_s": float(entry - bump.duration_s) if candidate else None,
        "settling_entry_s": entry if candidate else None,
        "band_m": band_m, "confirmation_s": confirmation_s,
        "tail_bound_m": bound, "tail_limit_m": tail_limit, "tail_pass": bool(tail_ok),
        "minimum_contact_N": float(np.min(normal_force)),
        "minimum_contact_time_s": float(t[np.argmin(normal_force)]),
        "contact_positive_on_grid": bool(np.min(normal_force) > 0),
        "post_bump_energy_start_J": float(energy[0]), "final_energy_J": float(energy[-1]),
        "maximum_energy_increase_J": maximum_increase,
        "energy_increase_allowance_J": energy_allowance,
        "energy_pass": bool(maximum_increase <= energy_allowance),
        "finite_states": bool(np.all(np.isfinite(q))),
        "solver_success": bool(all(s.success and s.status == 0 for s in trajectory.segments)),
        "derivative_evaluations": trajectory.nfev, "integration_runtime_s": trajectory.elapsed_s,
    }
