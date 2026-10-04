"""Analytical check of the body equation with the wheel deliberately clamped.

The study still uses the full two-mass quarter-car. This diagnostic holds wheel
position and velocity at zero and checks the existing body's force equation
against the closed-form unforced damped oscillator. It is not an approximation
of the full quarter-car trajectory or a check against a real vehicle.

Adapted from MMA3001_Notes_Week07_5_Higher_Order_ODEs.ipynb, one-based JSON
cells 19-21 (analytical response and verification versus validation), read on
2026-10-05. Course notebooks are neither imported nor executed.
"""

from dataclasses import asdict
from time import perf_counter

import numpy as np
from scipy.integrate import solve_ivp

import quarter_car


# These are diagnostic acceptance choices, declared before running the check.
# They are distinct from the project's peak/settling comparison criteria.
POSITION_ACCEPTANCE_M = 1e-7
VELOCITY_ACCEPTANCE_M_S = 1e-6
FLAT_ROAD = quarter_car.Bump(height_m=0.0)


def underdamped_exact(time_s, initial_position_m=0.010,
                      initial_velocity_m_s=0.020, mass_kg=365.4,
                      damping_n_s_m=2126.4, stiffness_n_m=24000.0):
    """Return analytical displacement [m] and velocity [m/s] from time zero.

    Parameters follow ``m*x'' + c*x' + k*x = 0`` about static equilibrium.
    ``time_s`` may be a scalar or an array of finite nonnegative seconds; each
    returned value has its shape. Mass and stiffness must be positive; damping
    must be nonnegative with damping ratio below one. The zero-damping limit is
    supported for an independent check. Initial position/velocity must be finite.
    Unsupported or nonfinite numeric inputs raise ValueError.

    This formula has no forcing and does not describe the two moving masses of
    the full model. It supplies an independent reference for the clamped case.
    """
    times = np.asarray(time_s, dtype=float)
    if not np.all(np.isfinite(times)) or np.any(times < 0):
        raise ValueError("time_s must contain finite nonnegative times")
    values = np.asarray([initial_position_m, initial_velocity_m_s, mass_kg,
                         damping_n_s_m, stiffness_n_m], dtype=float)
    if values.shape != (5,) or not np.all(np.isfinite(values)):
        raise ValueError("initial conditions and parameters must be finite scalars")
    if mass_kg <= 0 or stiffness_n_m <= 0 or damping_n_s_m < 0:
        raise ValueError("mass/stiffness must be positive and damping nonnegative")
    omega_n = np.sqrt(stiffness_n_m / mass_kg)
    alpha = damping_n_s_m / (2 * mass_kg)
    damping_ratio = alpha / omega_n
    if not np.isfinite(damping_ratio) or not 0 <= damping_ratio < 1:
        raise ValueError("analytical formula requires damping ratio below one")
    omega_d = omega_n * np.sqrt(1 - damping_ratio**2)
    a = initial_position_m
    b = (initial_velocity_m_s + alpha * a) / omega_d
    cosine, sine = np.cos(omega_d * times), np.sin(omega_d * times)
    envelope = np.exp(-alpha * times)
    position = envelope * (a * cosine + b * sine)
    velocity = envelope * ((-a * omega_d * sine + b * omega_d * cosine)
                           - alpha * (a * cosine + b * sine))
    return position, velocity


def clamped_wheel_rhs(time_s, body_state, parameters):
    """Return body [velocity, acceleration] with wheel [position, velocity]=0.

    ``body_state`` is a finite two-vector [m, m/s], and parameters is the
    existing quarter-car Parameters object. The original ``quarter_car.rhs``
    computes the derivatives, so a mistake in its body force equation can be
    detected. The clamp supplies a reaction force: its wheel acceleration is
    deliberately discarded instead of integrated. Invalid state raises ValueError.
    """
    body = np.asarray(body_state, dtype=float)
    if body.shape != (2,) or not np.all(np.isfinite(body)):
        raise ValueError("body_state must be a finite two-vector")
    return quarter_car.rhs(time_s, [body[0], body[1], 0.0, 0.0],
                           parameters, FLAT_ROAD)[:2]


def run_reduced_check():
    """Run the nominal clamped-wheel analytical check and return JSON-ready data.

    Compares both states on a 1 ms output grid over 0-5 s. RK45's internal steps
    are separate from this grid. Returns configuration, sampled maximum absolute
    errors, predeclared acceptance, pass/fail, solve work and source references.
    Failed, incomplete or nonfinite solutions produce a failed result with null
    errors. No output files are written and no full-study parameters are changed.
    """
    parameters = quarter_car.Parameters()
    initial_state = np.array([0.010, 0.020])
    end_s, comparison_dt_s = 5.0, 0.001
    rtol, atol, max_step_s = 1e-9, (1e-11, 1e-10), 0.005
    times = np.linspace(0.0, end_s, 5001)
    expected = np.asarray(underdamped_exact(
        times, *initial_state, parameters.ms, parameters.cs, parameters.ks))
    started = perf_counter()
    solution = solve_ivp(clamped_wheel_rhs, (0.0, end_s), initial_state,
                         args=(parameters,), method="RK45", dense_output=True,
                         rtol=rtol, atol=atol, max_step=max_step_s)
    elapsed_s = perf_counter() - started
    complete = bool(solution.success and solution.status == 0
                    and solution.t[0] == 0.0 and solution.t[-1] == end_s)
    finite_internal = bool(np.all(np.isfinite(solution.y)))
    sampled = solution.sol(times) if complete and finite_internal else None
    finite_samples = bool(sampled is not None and sampled.shape == expected.shape
                          and np.all(np.isfinite(sampled)))
    errors = np.max(np.abs(sampled - expected), axis=1) if finite_samples else None
    position_error = float(errors[0]) if errors is not None else None
    velocity_error = float(errors[1]) if errors is not None else None
    passed = bool(complete and finite_internal and finite_samples
                  and position_error <= POSITION_ACCEPTANCE_M
                  and velocity_error <= VELOCITY_ACCEPTANCE_M_S)
    return {
        "check": "clamped_wheel_analytical_body_oscillator",
        "configuration": {
            "quarter_car_parameters": asdict(parameters),
            "clamped_wheel_position_m": 0.0,
            "clamped_wheel_velocity_m_s": 0.0,
            "road_height_m": 0.0,
            "initial_body_position_m": float(initial_state[0]),
            "initial_body_velocity_m_s": float(initial_state[1]),
            "start_time_s": 0.0, "end_time_s": end_s,
            "comparison_dt_s": comparison_dt_s,
            "comparison_points": int(times.size),
            "method": "RK45", "rtol": rtol,
            "atol_m_m_s": list(atol), "max_step_s": max_step_s,
            "damping_ratio": float(parameters.cs /
                                   (2 * np.sqrt(parameters.ms * parameters.ks))),
        },
        "max_errors": {"position_m": position_error,
                       "velocity_m_s": velocity_error},
        "acceptance": {"position_m": POSITION_ACCEPTANCE_M,
                       "velocity_m_s": VELOCITY_ACCEPTANCE_M_S,
                       "comparison": "sampled maximum absolute discrepancy <= limit",
                       "basis": "predeclared diagnostic choices; not certified bounds"},
        "passed": passed,
        "solver": {"success": bool(solution.success),
                   "status": int(solution.status), "message": str(solution.message),
                   "complete_interval": complete,
                   "finite_internal_states": finite_internal,
                   "finite_comparison_states": finite_samples,
                   "accepted_points": int(solution.t.size),
                   "nfev": int(solution.nfev), "integration_runtime_s": elapsed_s},
        "sources": [{"notebook": "MMA3001_Notes_Week07_5_Higher_Order_ODEs.ipynb",
                     "one_based_json_cells": [19, 20, 21],
                     "adaptation": "closed-form unforced damped oscillator; wheel clamp diagnostic"}],
        "limitations": [
            "Deliberately constrained wheel: verifies the body equation and integration only.",
            "Does not verify the full coupled quarter-car, road forcing or tyre equation.",
            "Grid discrepancies are observed errors, not a continuous-time error bound.",
            "Does not validate the model against a real vehicle or change the study model.",
        ],
    }
