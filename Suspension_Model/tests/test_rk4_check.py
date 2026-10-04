"""Analytical, forcing-stage, boundary and failure checks for vector RK4."""

import numpy as np
import pytest

import rk4_check
from quarter_car import Bump, Parameters, SolverSettings, rhs, road_height, simulate, summarise
from rk4_check import rk4_step, simulate_rk4


def integrate_helper(derivative, initial, steps):
    """Use the public one-step method on [0,1] for an analytical test."""
    state = np.array(initial, dtype=float)
    for index in range(steps):
        state, calls = rk4_step(derivative, index / steps, state, 1 / steps)
        assert calls == 4
    return state


def test_rk4_matches_exact_time_forcing_integral():
    # y'=[1,t,t^2,t^3] has an elementary exact integral through fourth order.
    result = integrate_helper(lambda t, q: np.array([1, t, t**2, t**3]), [0] * 4, 4)
    np.testing.assert_allclose(result, [1, 1/2, 1/3, 1/4], atol=1e-15, rtol=0)


def test_rk4_fourth_order_convergence_against_vector_analytical_solution():
    derivative = lambda t, q: np.array([-2 * q[0], -q[1]])
    exact = np.exp([-2.0, -1.0])
    coarse = integrate_helper(derivative, [1, 1], 10)
    fine = integrate_helper(derivative, [1, 1], 20)
    ratio = np.max(abs(coarse - exact)) / np.max(abs(fine - exact))
    assert 14 < ratio < 19  # Halving h should reduce global fourth-order error ~16x.
    assert np.max(abs(fine - exact)) < 3e-7


def test_zero_road_equilibrium_and_summary_interface():
    trajectory = simulate_rk4(Parameters(), Bump(height_m=0), 2.0, 0.0005)
    time, state = trajectory.sample(0.0005)
    np.testing.assert_array_equal(state, np.zeros((4, time.size)))
    assert trajectory.nfev == 4 * (time.size - 1)
    assert trajectory.elapsed_s > 0
    result = summarise(trajectory, 0.0005)
    assert result["A_m"] == result["A_post_m"] == 0
    assert result["tail_pass"] and result["energy_pass"] and result["solver_success"]
    assert result["settling_after_exit_s"] == 0


def test_road_forcing_is_evaluated_at_all_stage_times(monkeypatch):
    times, heights = [], []
    def recorded(time, state, parameters, bump):
        times.append(time)
        heights.append(road_height(time, bump))
        return rhs(time, state, parameters, bump)
    monkeypatch.setattr(rk4_check, "rhs", recorded)
    simulate_rk4(Parameters(), Bump(duration_s=0.001), 0.002, 0.0005)
    np.testing.assert_allclose(times[:8], [0, 0.00025, 0.00025, 0.0005,
                                          0.0005, 0.00075, 0.00075, 0.001], atol=1e-18)
    np.testing.assert_allclose(heights[:4], [0, 0.025, 0.025, 0.05], atol=1e-15)
    assert len(times) == 16


@pytest.fixture(scope="module")
def nominal_pair():
    p, bump = Parameters(), Bump()
    coarse = simulate_rk4(p, bump, 0.8, 0.0005)
    fine = simulate_rk4(p, bump, 0.8, 0.00025)
    return coarse, fine


def test_bump_exit_preserves_full_state_and_native_endpoints(nominal_pair):
    for trajectory in nominal_pair:
        first, second = trajectory.segments
        np.testing.assert_array_equal(first.y[:, -1], second.y[:, 0])
        assert first.t[-1] == second.t[0] == 0.5
        assert np.linalg.norm(second.y[[1, 3], 0]) > 1e-3
        time, state = trajectory.sample(trajectory.dt_s)
        assert time[0] == 0 and time[-1] == 0.8
        assert np.count_nonzero(time == 0.5) == 1
        assert np.all(np.diff(time) > 0)
        assert np.max(np.diff(time)) <= trajectory.dt_s + 1e-15
        assert state.shape == (4, time.size)
        assert np.all(np.isfinite(state))
        assert trajectory.nfev == 4 * (time.size - 1)


def test_nominal_rk4_refines_toward_independent_tight_solver(nominal_pair):
    coarse, fine = nominal_pair
    reference = simulate(Parameters(), Bump(), 0.8,
                         SolverSettings(rtol=1e-11, atol=(1e-13,) * 4, max_step_s=0.001))
    time, coarse_state = coarse.sample(0.0005)
    fine_time, fine_state = fine.sample(0.0005)
    np.testing.assert_allclose(fine_time, time, atol=1e-15, rtol=0)
    exactish = reference.state_at(time)
    coarse_error = np.max(abs(coarse_state - exactish), axis=1)
    fine_error = np.max(abs(fine_state - exactish), axis=1)
    assert np.all(fine_error < coarse_error / 8)
    assert np.max(fine_error[[0, 2]]) < 1e-8  # Positions in m, not mixed-unit norm.
    assert np.max(fine_error[[1, 3]]) < 1e-7  # Velocities in m/s.


def test_nondivisible_steps_land_on_exit_and_horizon_without_interpolation():
    trajectory = simulate_rk4(Parameters(), Bump(height_m=0, duration_s=0.51), 0.83, 0.07)
    time, _ = trajectory.sample(0.07)
    assert np.count_nonzero(time == 0.51) == 1
    assert time[-1] == 0.83
    assert np.all(np.diff(time) <= 0.07 + 1e-15)
    coarser_time, _ = trajectory.sample(0.14)
    assert np.count_nonzero(coarser_time == 0.51) == 1
    assert coarser_time[-1] == 0.83
    assert np.all(np.isin(coarser_time, time))
    with pytest.raises(ValueError):
        trajectory.sample(0.035)
    with pytest.raises(ValueError):
        trajectory.sample(0.10)


@pytest.mark.parametrize("bad", [0, -1, np.nan, np.inf, -np.inf, [0.0005]])
def test_rejects_invalid_time_step(bad):
    with pytest.raises(ValueError):
        simulate_rk4(Parameters(), Bump(), 1.0, bad)
    with pytest.raises(ValueError):
        rk4_step(lambda t, q: q, 0, [1], bad)


@pytest.mark.parametrize("bad", [0, 0.5, -1, np.nan, np.inf, -np.inf, [1.0]])
def test_rejects_invalid_end_time(bad):
    with pytest.raises(ValueError):
        simulate_rk4(Parameters(), Bump(), bad, 0.0005)


@pytest.mark.parametrize("bad", [[], [[1]], [np.nan], [np.inf]])
def test_step_rejects_invalid_initial_state(bad):
    with pytest.raises(ValueError):
        rk4_step(lambda t, q: q, 0, bad, 0.01)


@pytest.mark.parametrize("bad", [np.nan, np.inf, [0]])
def test_step_rejects_invalid_initial_time(bad):
    with pytest.raises(ValueError):
        rk4_step(lambda t, q: q, bad, [1], 0.01)


@pytest.mark.parametrize("derivative", [lambda t, q: [np.nan], lambda t, q: [np.inf], lambda t, q: [1, 2]])
def test_step_rejects_nonfinite_or_wrong_shape_derivative(derivative):
    with pytest.raises(RuntimeError):
        rk4_step(derivative, 0, [1], 0.01)


def test_simulation_rejects_nonfinite_evolution(monkeypatch):
    monkeypatch.setattr(rk4_check, "rhs", lambda *args: np.full(4, np.inf))
    with pytest.raises(RuntimeError):
        simulate_rk4(Parameters(), Bump(), 1, 0.0005)


def test_rejects_wrong_model_input_types():
    with pytest.raises(ValueError):
        simulate_rk4(None, Bump(), 1, 0.0005)
    with pytest.raises(ValueError):
        simulate_rk4(Parameters(), None, 1, 0.0005)


@pytest.mark.parametrize("bad", [0, -1, np.nan, np.inf, 0.000125, 0.00075])
def test_sampling_rejects_invalid_or_unavailable_resolution(nominal_pair, bad):
    with pytest.raises(ValueError):
        nominal_pair[0].sample(bad)
