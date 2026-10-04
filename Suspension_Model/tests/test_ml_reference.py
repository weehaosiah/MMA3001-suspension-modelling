"""Small, simulation-free checks for fixed-prediction reference sensitivity."""

from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest

from ml_reference_check import ranking_check, reference_checks


def scores(linear=0.5, first=0.1, second=0.2):
    return [
        {"model_id": "linear", "family": "linear", "status": "ok",
         "validation": {"RMSE_mm": linear}},
        {"model_id": "a", "family": "rbf_svr", "C": 1, "gamma": 0.1,
         "epsilon": 0.05, "status": "ok", "validation": {"RMSE_mm": first}},
        {"model_id": "b", "family": "rbf_svr", "C": 10, "gamma": 1,
         "epsilon": 0.05, "status": "ok", "validation": {"RMSE_mm": second}},
    ]


def test_reference_label_rms_gives_expected_stability_bound():
    check = ranking_check(scores(), [10, 20], [10.03, 20.04])
    assert check["label_change_rms_mm"] == pytest.approx(np.sqrt((0.03**2 + 0.04**2)/2))
    assert check["label_change_max_mm"] == pytest.approx(0.04)
    assert check["best_svr_gap_mm"] == pytest.approx(0.1)
    assert check["preferred_gap_mm"] == pytest.approx(0.1)
    assert check["best_svr_stable"] and check["preferred_stable"]


def test_nearby_svr_can_undermine_specific_winner_even_with_large_linear_gap():
    check = ranking_check(scores(linear=1, first=0.1, second=0.11), [10, 20], [10.02, 20.02])
    assert not check["best_svr_stable"]
    assert not check["preferred_stable"]
    assert check["preferred_gap_mm"] == pytest.approx(0.01)


def test_zero_change_and_exact_ties_follow_the_strict_gap_rule():
    unchanged = ranking_check(scores(), [10, 20], [10, 20])
    assert unchanged["label_change_rms_mm"] == unchanged["label_change_max_mm"] == 0
    assert unchanged["best_svr_stable"] and unchanged["preferred_stable"]
    tied = ranking_check(scores(linear=0.1, first=0.1, second=0.1), [10, 20], [10.01, 20.01])
    assert tied["best_svr_gap_mm"] == tied["preferred_gap_mm"] == 0
    assert not tied["best_svr_stable"] and not tied["preferred_stable"]


def test_ranking_rejects_invalid_reference_vectors():
    for baseline, refined in [([], []), ([1, 2], [1]), ([np.nan], [1]), ([1], [np.inf]), ([[1]], [[1]])]:
        with pytest.raises(ValueError):
            ranking_check(scores(), baseline, refined)


def test_ranking_rejects_failed_scores_and_insufficient_svr_comparison():
    bad = scores()
    bad[1]["status"] = "failed"
    with pytest.raises(ValueError):
        ranking_check(bad, [10], [10])
    bad = scores()
    bad[1]["validation"]["RMSE_mm"] = np.inf
    with pytest.raises(ValueError):
        ranking_check(bad, [10], [10])
    with pytest.raises(ValueError):
        ranking_check(scores()[:2], [10], [10])


@pytest.fixture
def references():
    # Only an authorised validation record is read; no test responses or
    # integrations are needed to exercise the classification branches.
    path = Path(__file__).resolve().parents[1] / "dataset_v1/validation_diagnostics.jsonl"
    with path.open(encoding="utf-8") as handle:
        baseline = json.loads(handle.readline())["raw_summary"]
    refined = deepcopy(baseline)
    refined.update(end_time_s=10, observation_dt_s=0.00025)
    return baseline, refined


def test_coherent_tight_reference_passes_all_flags(references):
    baseline, refined = references
    assert all(reference_checks(refined, 0, baseline).values())


def test_physical_and_energy_tail_failures_cannot_pass_on_boolean_claim_alone(references):
    baseline, refined = references
    changes = [("minimum_contact_N", 1.0, "contact"),
               ("maximum_energy_increase_J", 1.0, "energy"),
               ("tail_bound_m", 0.001, "tail")]
    for field, value, flag in changes:
        changed = deepcopy(refined)
        changed[field] = value
        check = reference_checks(changed, 0, baseline)
        assert not check[flag] and not all(check.values())


def test_wrong_settings_incomplete_solve_and_continuity_failures_are_visible(references):
    baseline, refined = references
    for field, value, flag in [("end_time_s", 5, "reference_settings"),
                               ("observation_dt_s", 0.001, "reference_settings"),
                               ("solver_success", False, "finite_complete"),
                               ("finite_states", False, "finite_complete"),
                               ("A_m", np.nan, "finite_complete")]:
        changed = deepcopy(refined)
        changed[field] = value
        assert not reference_checks(changed, 0, baseline)[flag]
    for error in (1e-12, None, np.inf):
        assert not reference_checks(refined, error, baseline)["full_state_continuity"]


def test_disagreement_in_either_peak_fails_its_comparison(references):
    baseline, refined = references
    for field, flag in [("A_m", "primary_peak_agreement"), ("A_post_m", "post_peak_agreement")]:
        changed = deepcopy(refined)
        changed[field] += 0.0001  # 0.1 mm, above the adopted 0.05 mm agreement limit.
        assert not reference_checks(changed, 0, baseline)[flag]


def test_unresolved_or_changed_settling_never_passes_agreement(references):
    baseline, refined = references
    unresolved = deepcopy(refined)
    unresolved.update(settling_status="unresolved", settling_after_exit_s=None)
    assert not reference_checks(unresolved, 0, baseline)["settling_agreement"]
    changed = deepcopy(refined)
    changed["settling_after_exit_s"] += 0.02
    assert not reference_checks(changed, 0, baseline)["settling_agreement"]
