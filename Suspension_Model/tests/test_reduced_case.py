"""Independent analytical identities and coupling checks for the reduced diagnostic."""

import json
from types import SimpleNamespace

import numpy as np
import pytest

import quarter_car
import verify_reduced_case
from verify_reduced_case import clamped_wheel_rhs, run_reduced_check, underdamped_exact


def test_analytical_response_preserves_both_initial_conditions():
    x, v = underdamped_exact([0.0], initial_position_m=-0.013,
                            initial_velocity_m_s=0.027)
    assert x[0] == pytest.approx(-0.013, abs=1e-16)
    assert v[0] == pytest.approx(0.027, abs=1e-16)


def test_independent_known_damped_response():
    # x=e^-t cos(t), v=-e^-t[cos(t)+sin(t)] solves x''+2x'+2x=0.
    times = np.array([0.0, 0.4, np.pi / 2, np.pi, 5.0])
    x, v = underdamped_exact(times, 1.0, -1.0, 1.0, 2.0, 2.0)
    np.testing.assert_allclose(x, np.exp(-times) * np.cos(times), atol=1e-15)
    np.testing.assert_allclose(v, -np.exp(-times) * (np.cos(times) + np.sin(times)),
                               atol=1e-15)


def test_undamped_limit_has_known_quarter_period_states():
    x, v = underdamped_exact([0.0, np.pi / 4, np.pi / 2], 1.0, 0.0, 1.0, 0.0, 4.0)
    np.testing.assert_allclose(x, [1.0, 0.0, -1.0], atol=1e-15)
    np.testing.assert_allclose(v, [0.0, -2.0, 0.0], atol=1e-15)


def test_clamped_derivative_has_independent_body_force_and_correct_order():
    actual = clamped_wheel_rhs(1.0, [0.010, 0.020], quarter_car.Parameters())
    # Body force = -(240 + 42.528) N. The clamp supplies the wheel reaction.
    np.testing.assert_allclose(actual, [0.020, -282.528 / 365.4], atol=1e-15)


def test_clamp_reuses_actual_quarter_car_rhs(monkeypatch):
    calls = []

    def recording_rhs(time, state, parameters, bump):
        calls.append((time, state, parameters, bump))
        return np.array([7.0, -3.0, 99.0, 100.0])

    monkeypatch.setattr(quarter_car, "rhs", recording_rhs)
    p = quarter_car.Parameters()
    np.testing.assert_array_equal(clamped_wheel_rhs(0.3, [0.01, -0.02], p), [7, -3])
    time, state, supplied, bump = calls[0]
    assert time == 0.3 and supplied is p and bump.height_m == 0.0
    np.testing.assert_array_equal(state, [0.01, -0.02, 0.0, 0.0])


def test_nominal_reduced_check_meets_predeclared_limits_and_is_json_ready():
    result = run_reduced_check()
    assert result["passed"]
    assert result["max_errors"]["position_m"] <= 1e-7
    assert result["max_errors"]["velocity_m_s"] <= 1e-6
    assert result["solver"]["complete_interval"]
    assert result["solver"]["nfev"] > 0
    assert result["solver"]["integration_runtime_s"] >= 0
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("name", ["mass_kg", "stiffness_n_m"])
@pytest.mark.parametrize("bad", [0.0, -1.0, np.inf, np.nan])
def test_analytical_formula_rejects_bad_mass_or_stiffness(name, bad):
    with pytest.raises(ValueError):
        underdamped_exact([0.0], **{name: bad})


@pytest.mark.parametrize("damping", [-1.0, np.nan, np.inf, 2.0, 3.0])
def test_analytical_formula_rejects_invalid_critical_or_overdamped_cases(damping):
    with pytest.raises(ValueError):
        underdamped_exact([0.0], mass_kg=1.0, stiffness_n_m=1.0,
                          damping_n_s_m=damping)


@pytest.mark.parametrize("bad", [-1.0, np.nan, np.inf, [0.0, np.nan]])
def test_analytical_formula_rejects_invalid_times(bad):
    with pytest.raises(ValueError):
        underdamped_exact(bad)


@pytest.mark.parametrize("name", ["initial_position_m", "initial_velocity_m_s"])
@pytest.mark.parametrize("bad", [np.nan, np.inf])
def test_analytical_formula_rejects_nonfinite_initial_states(name, bad):
    with pytest.raises(ValueError):
        underdamped_exact([0.0], **{name: bad})


@pytest.mark.parametrize("state", [[0.0], [[0.0, 0.0]], [np.nan, 0.0], [0.0, np.inf]])
def test_clamp_rejects_invalid_body_state(state):
    with pytest.raises(ValueError):
        clamped_wheel_rhs(0.0, state, quarter_car.Parameters())


@pytest.mark.parametrize("failure", ["failed", "incomplete", "nonfinite"])
def test_failed_reduced_solution_cannot_pass(monkeypatch, failure):
    y = np.zeros((2, 2))
    if failure == "nonfinite":
        y[0, -1] = np.nan
    solution = SimpleNamespace(
        success=failure != "failed", status=-1 if failure == "failed" else 0,
        t=np.array([0.0, 4.0 if failure == "incomplete" else 5.0]),
        y=y, nfev=1, message="Injected diagnostic failure",
    )
    monkeypatch.setattr(verify_reduced_case, "solve_ivp", lambda *args, **kwargs: solution)
    result = run_reduced_check()
    assert not result["passed"]
    assert result["max_errors"] == {"position_m": None, "velocity_m_s": None}
    json.dumps(result, allow_nan=False)
