"""Focused physical and failure-path checks for the nominal implementation.

Hand-calculated forces and an energy balance independently check the governing
equations. Synthetic settling histories deliberately include misleading early
band entries. These checks do not validate a real car or the later study domain.
"""

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest
import quarter_car

from quarter_car import (
    Bump,
    Parameters,
    SolverSettings,
    contact_force,
    post_bump_energy,
    rhs,
    road_height,
    settling_candidate,
    simulate,
    summarise,
)


@pytest.fixture(scope="module")
def nominal():
    return simulate()


def test_road_height_units_shape_and_flat_endpoints():
    bump = Bump()
    times = np.array([-1.0, 0.0, 0.125, 0.25, 0.375, 0.5, 1.0])
    np.testing.assert_allclose(
        road_height(times, bump), [0, 0, 0.025, 0.050, 0.025, 0, 0], atol=1e-16
    )
    # Approaching each endpoint also approaches a horizontal road slope.
    tiny = 1e-7
    assert road_height(tiny, bump) / tiny < 1e-6
    assert road_height(bump.duration_s - tiny, bump) / tiny < 1e-6
    assert road_height(0.25, bump) == pytest.approx(0.050)


@pytest.mark.parametrize(
    "state, expected_body_force_N, expected_wheel_force_N",
    [
        ([0.01, 0, 0, 0], -240.0, 240.0),
        ([0, 0.1, 0, 0], -212.64, 212.64),
        ([0, 0, 0.01, 0], 240.0, -3740.0),
        ([0, 0, 0, 0.1], 212.64, -212.64),
    ],
)
def test_independent_force_signs_and_state_order(
    state, expected_body_force_N, expected_wheel_force_N
):
    p = Parameters()
    derivative = rhs(1.0, state, p, Bump())
    # Each acceleration is force / mass, in N/kg = m/s^2.
    np.testing.assert_allclose(
        derivative,
        [state[1], expected_body_force_N / p.ms,
         state[3], expected_wheel_force_N / p.mu],
        rtol=1e-14, atol=1e-14,
    )


def test_internal_forces_cancel_in_total_momentum_balance():
    p, bump = Parameters(), Bump()
    state = np.array([0.012, -0.13, 0.008, 0.09])
    derivative = rhs(0.25, state, p, bump)
    # Only the dynamic tyre force is external to the two-mass system.
    assert p.ms * derivative[1] + p.mu * derivative[3] == pytest.approx(
        350000.0 * (0.050 - 0.008), rel=1e-14
    )
    np.testing.assert_array_equal(
        derivative, rhs(0.25, state, replace(p, g=1.62), bump)
    )  # Static-equilibrium coordinates remove gravity from the ODE.


def test_energy_units_and_flat_road_dissipation_identity():
    p, bump = Parameters(), Bump()
    state = np.array([0.013, 0.2, -0.004, -0.1])
    assert post_bump_energy(state, p) == pytest.approx(13.791, abs=1e-12)
    derivative = rhs(1.0, state, p, bump)
    # A centred directional derivative checks the implemented energy formula
    # against the physical rate -c_s*(v_s-v_u)^2, in joules per second.
    delta = 1e-7
    rate = (post_bump_energy(state + delta * derivative, p)
            - post_bump_energy(state - delta * derivative, p)) / (2 * delta)
    assert rate == pytest.approx(-191.376, abs=1e-6)


def test_contact_includes_weight_and_never_clips_tension():
    p, bump = Parameters(), Bump()
    weight = 408.4 * 9.81
    assert contact_force(1.0, np.zeros(4), p, bump) == pytest.approx(weight)
    assert contact_force(0.25, np.zeros(4), p, bump) == pytest.approx(weight + 17500.0)
    lifted = [0, 0, 0.02, 0]
    assert contact_force(1.0, lifted, p, bump) == pytest.approx(weight - 7000.0)
    assert contact_force(1.0, lifted, p, bump) < 0


def test_zero_road_remains_at_equilibrium():
    trajectory = simulate(bump=Bump(height_m=0.0), end_time_s=2.0)
    time, state = trajectory.sample(0.002)
    assert time[0] == 0.0 and time[-1] == 2.0
    np.testing.assert_array_equal(state, np.zeros_like(state))
    result = summarise(trajectory)
    assert result["A_m"] == result["A_post_m"] == 0.0
    assert result["tail_pass"] and result["energy_pass"]
    assert result["settling_status"] == "candidate"
    assert result["settling_after_exit_s"] == 0.0
    assert result["solver_success"] and result["finite_states"]


def test_exit_preserves_all_four_states_and_post_bump_motion(nominal):
    entering, leaving = nominal.segments
    np.testing.assert_array_equal(entering.y[:, -1], leaving.y[:, 0])
    assert entering.t[-1] == leaving.t[0] == 0.5
    assert np.linalg.norm(leaving.y[[1, 3], 0]) > 1e-3
    around_exit = nominal.state_at(np.array([0.5 - 1e-8, 0.5, 0.5 + 1e-8]))
    np.testing.assert_allclose(around_exit[:, 0], around_exit[:, 2], atol=1e-6, rtol=0)
    after_exit = nominal.state_at(np.array([0.5, 0.7, 1.0]))
    assert np.max(np.abs(after_exit[0] - after_exit[2])) > 0.001
    assert not np.array_equal(after_exit[:, 0], after_exit[:, -1])
    assert all(segment.success and segment.status == 0 for segment in nominal.segments)


def test_sampling_includes_exit_and_horizon_without_duplicates(nominal):
    time, state = nominal.sample(0.003)
    assert time[0] == 0.0 and time[-1] == nominal.end_time_s
    assert np.count_nonzero(time == 0.5) == 1
    assert np.all(np.diff(time) > 0)
    assert np.max(np.diff(time)) <= 0.003 + 1e-15
    assert state.shape == (4, time.size)
    assert np.all(np.isfinite(state))


def test_settling_uses_last_excursion_and_signed_boundary():
    time = [0, 0.5, 0.7, 1.0, 1.1, 2.0, 3.0]
    # An early entry is followed by a negative excursion. Its final crossing
    # from -2 mm to +0.5 mm reaches -1 mm at 1.46 s, not at a zero crossing.
    displacement = [0, 0, 0.002, 0, -0.002, 0.0005, 0]
    assert settling_candidate(time, displacement, 0.5) == pytest.approx(1.46)


def test_settling_rejects_short_confirmation_and_last_outside_sample():
    assert settling_candidate([0.5, 1.0, 1.2], [0.002, 0, 0], 0.5) is None
    assert settling_candidate([0.5, 1.0, 3.0], [0, 0, 0.002], 0.5) is None
    assert settling_candidate([0.5, 1.0, 1.49], [0, 0, 0], 0.5) is None


def test_settling_all_in_band_starts_clock_at_exit():
    assert settling_candidate([0, 0.5, 1.0, 1.5], [0.1, 0.001, -0.001, 0], 0.5) == 0.5


def test_primary_output_is_relative_displacement_over_entire_response():
    time = np.array([0, 0.5, 1.0, 2.0, 3.0])
    state = np.zeros((4, time.size))
    state[0] = [0, 0.04, 0.003, 0, 0]
    state[2] = [0, 0.04, 0.010, 0, 0]
    # Shared body/wheel motion at exit is not suspension travel; the largest
    # relative departure is a 7 mm compression after the road has become flat.
    trajectory = SimpleNamespace(
        parameters=Parameters(), bump=Bump(), end_time_s=3.0,
        sample=lambda _: (time, state), nfev=0, elapsed_s=0,
        segments=[SimpleNamespace(success=True, status=0)],
    )
    result = summarise(trajectory)
    assert result["A_m"] == result["A_post_m"] == pytest.approx(0.007)
    assert result["A_signed_m"] == pytest.approx(-0.007)
    assert result["A_time_s"] == result["A_post_time_s"] == 1.0


def test_quiet_displacement_without_energy_margin_is_unresolved():
    time = np.array([0, 0.5, 1.0, 2.0])
    state = np.zeros((4, time.size))
    state[0, 1] = 0.0005
    state[1, -1] = 0.1  # In-band position with appreciable final kinetic energy.
    trajectory = SimpleNamespace(
        parameters=Parameters(), bump=Bump(), end_time_s=2.0,
        sample=lambda _: (time, state), nfev=0, elapsed_s=0,
        segments=[SimpleNamespace(success=True, status=0)],
    )
    result = summarise(trajectory)
    assert result["settling_status"] == "unresolved"
    assert result["settling_after_exit_s"] is None
    assert result["settling_entry_s"] is None
    assert not result["tail_pass"]


@pytest.mark.parametrize("failure", ["failed", "incomplete", "nonfinite"])
def test_unsuccessful_incomplete_or_nonfinite_solver_is_rejected(monkeypatch, failure):
    state = np.zeros((4, 2))
    if failure == "nonfinite":
        state[0, -1] = np.nan
    solution = SimpleNamespace(
        success=failure != "failed", status=-1 if failure == "failed" else 0,
        t=np.array([0.0, 0.4 if failure == "incomplete" else 0.5]),
        y=state, message="Deliberately injected failure for guard testing",
    )
    monkeypatch.setattr(quarter_car, "solve_ivp", lambda *args, **kwargs: solution)
    with pytest.raises(RuntimeError):
        simulate()


@pytest.mark.parametrize("field", ["ms", "mu", "ks", "cs", "kt", "g"])
@pytest.mark.parametrize("bad", [0, -1, np.nan, np.inf, -np.inf])
def test_parameters_reject_invalid_physical_values(field, bad):
    with pytest.raises(ValueError):
        Parameters(**{field: bad})


@pytest.mark.parametrize("bad", [-1, np.nan, np.inf, -np.inf])
def test_bump_rejects_invalid_height(bad):
    with pytest.raises(ValueError):
        Bump(height_m=bad)


@pytest.mark.parametrize("bad", [0, -1, np.nan, np.inf, -np.inf])
def test_bump_and_solver_reject_invalid_positive_controls(bad):
    with pytest.raises(ValueError):
        Bump(duration_s=bad)
    with pytest.raises(ValueError):
        SolverSettings(rtol=bad)
    with pytest.raises(ValueError):
        SolverSettings(max_step_s=bad)
    with pytest.raises(ValueError):
        SolverSettings(atol=(1e-9, bad, 1e-9, 1e-8))


@pytest.mark.parametrize("bad", [(1e-9,), (1e-9, 1e-8, 1e-9), [[1e-9] * 4]])
def test_solver_requires_four_component_absolute_tolerances(bad):
    with pytest.raises(ValueError):
        SolverSettings(atol=bad)


@pytest.mark.parametrize("bad", [0, 0.5, -1, np.nan, np.inf, -np.inf])
def test_simulation_rejects_invalid_horizon(bad):
    with pytest.raises(ValueError):
        simulate(end_time_s=bad)


@pytest.mark.parametrize("bad", [[0, 0, 0], [[0, 0, 0, 0]], [0, np.nan, 0, 0], [0, 0, np.inf, 0]])
def test_simulation_and_rhs_reject_invalid_state(bad):
    with pytest.raises(ValueError):
        simulate(initial_state=bad)
    with pytest.raises(ValueError):
        rhs(0.0, bad, Parameters(), Bump())


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_road_time_rejected(bad):
    with pytest.raises(ValueError):
        road_height(bad, Bump())
    with pytest.raises(ValueError):
        rhs(bad, np.zeros(4), Parameters(), Bump())


@pytest.mark.parametrize("bad", [0, -1, np.nan, np.inf])
def test_sampling_rejects_invalid_resolution(nominal, bad):
    with pytest.raises(ValueError):
        nominal.sample(bad)


@pytest.mark.parametrize("bad", [[-0.001], [5.001], [np.inf], [np.nan], [[0.5]], 0.5])
def test_state_queries_reject_extrapolation_or_invalid_times(nominal, bad):
    with pytest.raises(ValueError):
        nominal.state_at(bad)


@pytest.mark.parametrize(
    "time, displacement, exit_s",
    [
        ([0.5, 0.5, 2], [0, 0, 0], 0.5),
        ([0.5, 0.4, 2], [0, 0, 0], 0.5),
        ([0.5, 2], [0], 0.5),
        ([0.5, np.inf], [0, 0], 0.5),
        ([0.5, 2], [0, np.nan], 0.5),
        ([0, 2], [0, 0], 0.5),
        ([0.5, 2], [0, 0], np.inf),
        ([0.5], [0], 0.5),
    ],
)
def test_settling_rejects_invalid_histories(time, displacement, exit_s):
    with pytest.raises(ValueError):
        settling_candidate(time, displacement, exit_s)


@pytest.mark.parametrize("bad", [0, -1, np.inf, np.nan])
def test_settling_rejects_invalid_band_or_confirmation(bad):
    with pytest.raises(ValueError):
        settling_candidate([0.5, 2], [0, 0], 0.5, band_m=bad)
    with pytest.raises(ValueError):
        settling_candidate([0.5, 2], [0, 0], 0.5, confirmation_s=bad)
