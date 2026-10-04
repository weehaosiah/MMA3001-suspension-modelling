"""Failure classification for pilot verification, without running the pilots.

Synthetic summaries isolate decisions from numerical integration. The real
comparison function is retained, so accumulated errors and unresolved statuses
must be handled by the runner rather than hidden behind mocked pass flags.
"""

from types import SimpleNamespace

import numpy as np
import pytest

import run_verification
from quarter_car import Parameters


def mocked_pilot(monkeypatch, alteration=None):
    """Run classification with cheap trajectories and controlled diagnostics."""
    def trajectory(kind, end):
        return SimpleNamespace(
            kind=kind, end_time_s=end,
            segments=(SimpleNamespace(y=np.zeros((4, 2))),
                      SimpleNamespace(y=np.zeros((4, 2)))),
            sample=lambda dt: (np.array([0, 0.5, end]), np.zeros((4, 3))),
        )

    def fake_rk45(parameters, bump, end, settings):
        kind = "base" if settings is run_verification.BASE else "tight"
        if end > 5:
            kind = "extended"
        return trajectory(kind, end)

    def fake_rk4(parameters, bump, end, dt):
        return trajectory("rk4_coarse" if dt == 0.0005 else "rk4_fine", end)

    def fake_summary(tr, dt, band_m):
        result = {
            "A_m": 0.040, "A_post_m": 0.030,
            "settling_status": "candidate", "settling_after_exit_s": 1.5,
            "settling_entry_s": 2.0, "minimum_contact_N": 2500.0,
            "finite_states": True, "solver_success": True,
            "energy_pass": True, "tail_pass": True,
        }
        if alteration is not None:
            alteration(tr.kind, dt, band_m, result)
        return result

    monkeypatch.setattr(run_verification, "simulate", fake_rk45)
    monkeypatch.setattr(run_verification, "simulate_rk4", fake_rk4)
    monkeypatch.setattr(run_verification, "summarise", fake_summary)
    result, _ = run_verification.verify_pilot(Parameters(), 5.0)
    return result


def test_confirmed_numerical_and_physical_checks_allow_resolution(monkeypatch):
    result = mocked_pilot(monkeypatch)
    assert result["passed"] and result["horizon_adequate"]
    assert result["final"]["primary_peak_numerically_resolved"]
    assert result["final"]["physical_contact_consistent"]
    assert result["final"]["settling_status"] == "resolved"
    assert result["final"]["settling_after_exit_s"] == 1.5


def test_contact_failure_is_distinct_from_numerical_accuracy(monkeypatch):
    def loss_of_contact(kind, dt, band, summary):
        summary["minimum_contact_N"] = -50.0
    result = mocked_pilot(monkeypatch, loss_of_contact)
    assert not result["passed"]
    assert not result["checks"]["positive_contact_with_margin"]
    assert not result["final"]["physical_contact_consistent"]
    assert result["final"]["primary_peak_numerically_resolved"]
    # The mathematical linear-model trajectory can be resolved even when its
    # assumed tyre contact has failed; it must not be accepted as a valid pilot.
    assert result["final"]["settling_status"] == "resolved"


def test_unresolved_narrow_band_does_not_invalidate_primary_or_one_mm_result(monkeypatch):
    def unresolved_half_mm(kind, dt, band, summary):
        if band == 0.0005:
            summary.update(settling_status="unresolved", settling_after_exit_s=None,
                           settling_entry_s=None)
    result = mocked_pilot(monkeypatch, unresolved_half_mm)
    assert not result["passed"]
    assert not result["checks"]["settling_agreement_all_bands"]
    assert result["final"]["primary_peak_numerically_resolved"]
    assert result["final"]["settling_status"] == "resolved"
    assert result["settling_sensitivity"]["0.5"] == {"status": "unresolved", "after_exit_s": None}
    assert result["settling_sensitivity"]["1"]["status"] == "resolved"
    assert not result["horizon_adequate"]


@pytest.mark.parametrize("failure", ["tail", "horizon_peak", "horizon_settling"])
def test_unconfirmed_tail_or_horizon_requests_further_observation(monkeypatch, failure):
    def insufficient_observation(kind, dt, band, summary):
        if kind != "extended":
            return
        if failure == "tail":
            summary["tail_pass"] = False
        elif failure == "horizon_peak":
            summary["A_m"] += 0.0001  # Additional 0.1 mm peak on extension.
        else:
            summary["settling_after_exit_s"] += 0.1
            summary["settling_entry_s"] += 0.1
    result = mocked_pilot(monkeypatch, insufficient_observation)
    assert not result["horizon_adequate"]
    assert not result["passed"]
    assert result["final"]["settling_status"] == "unresolved"
    assert result["final"]["settling_after_exit_s"] is None
    assert result["final"]["settling_entry_s"] is None


def test_accumulated_refinement_error_must_pass_direct_selected_reference_comparison(monkeypatch):
    def small_increment_at_each_refinement(kind, dt, band, summary):
        if kind == "base":
            increment = 0
        elif kind == "tight" and dt == 0.001:
            increment = 0.00004
        elif kind == "rk4_coarse" or (kind == "tight" and dt == 0.0005):
            increment = 0.00008
        else:
            increment = 0.00012
        summary["A_m"] += increment
    result = mocked_pilot(monkeypatch, small_increment_at_each_refinement)
    # Each adjacent comparison differs by at most 0.04 mm; the selected cheap
    # result differs from the reference by 0.12 mm, exceeding the 0.05 mm limit.
    comparisons = result["bands"]["1"]["comparisons"]
    assert all(c["peaks_pass"] for name, c in comparisons.items() if name != "selected_vs_reference")
    assert not result["checks"]["selected_peak_agreement"]
    assert not result["final"]["primary_peak_numerically_resolved"]
    assert not result["passed"]


@pytest.mark.parametrize("failed_field", ["finite_states", "solver_success", "energy_pass"])
def test_failed_numerical_prerequisite_prevents_resolved_labels(monkeypatch, failed_field):
    def false_prerequisite(kind, dt, band, summary):
        if kind == "base":
            summary[failed_field] = False
    result = mocked_pilot(monkeypatch, false_prerequisite)
    assert not result["passed"]
    assert not result["final"]["primary_peak_numerically_resolved"]
    assert result["final"]["settling_status"] == "unresolved"
    assert result["final"]["settling_after_exit_s"] is None
    assert result["final"]["settling_entry_s"] is None
    assert all(band["status"] == "unresolved" and band["after_exit_s"] is None
               for band in result["settling_sensitivity"].values())
