"""Fixed split identity, per-row validity, and pilot-cache provenance tests.

No simulations or model fitting occur here. Cached verification results supply
one known diagnostic record; mutated copies check rejection and failure reasons.
"""

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest

from dataset_design import (
    classify_summary, load_verified_pilots, make_setups, safe_json,
    sha256_file, validate_setups,
)


ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "verification_results" / "summary.json"
MODEL = ROOT / "quarter_car.py"


@pytest.fixture(scope="module")
def pilot_record():
    return json.loads(VERIFICATION.read_text(encoding="utf-8"))


@pytest.fixture
def valid_summary(pilot_record):
    return deepcopy(pilot_record["pilots"][0]["bands"]["1"]["runs"]["base_1ms"])


def test_setup_counts_roles_and_unique_identities():
    rows = make_setups()
    assert len(rows) == 400
    assert Counter(row["split"] for row in rows) == {"train": 225, "validation": 75, "test": 100}
    assert len({row["setup_id"] for row in rows}) == 400
    assert len({(row["ks_N_m"], row["cs_N_s_m"]) for row in rows}) == 400
    assert rows[0]["setup_id"] == "train_001"
    assert rows[224]["setup_id"] == "train_225"
    assert rows[225]["setup_id"] == "validation_001"
    assert rows[299]["setup_id"] == "validation_075"
    assert rows[300]["setup_id"] == "test_001"
    assert rows[-1]["setup_id"] == "test_100"
    assert validate_setups(rows)["duplicates"] == 0


def test_training_grid_includes_all_nine_pilots_in_declared_traversal():
    rows = make_setups()
    train = rows[:225]
    pairs = [(row["ks_N_m"], row["cs_N_s_m"]) for row in train]
    assert pairs == sorted(pairs)
    axes = [sorted({pair[index] for pair in pairs}) for index in (0, 1)]
    assert [len(axis) for axis in axes] == [15, 15]
    assert (axes[0][0], axes[0][-1]) == (18000.0, 30000.0)
    assert (axes[1][0], axes[1][-1]) == (1594.8, 2658.0)
    for axis in axes:
        np.testing.assert_allclose(np.diff(axis), (axis[-1] - axis[0]) / 14, rtol=1e-14)
    pilots = {(ks, cs) for ks in (18000.0, 24000.0, 30000.0)
              for cs in (1594.8, 2126.4, 2658.0)}
    assert len(pilots & set(pairs)) == 9
    assert all((row["ks_N_m"], row["cs_N_s_m"]) not in pilots for row in rows[225:])


def test_random_split_seeds_and_rowwise_column_order_are_frozen():
    rows = make_setups()
    # Golden values fix the declared PCG64 seeds and [ks,cs] draw ordering.
    # This guards against a silent columnwise draw or shared-generator change.
    expected = {
        "validation": [[29012.4182468208, 2477.183552259908],
                       [27528.587142035787, 2359.8941124305015]],
        "test": [[19780.82324226933, 2159.670880105612],
                 [25420.26289335621, 2037.9863235919706]],
    }
    for split, seed in (("validation", 3001), ("test", 3002)):
        selected = [row for row in rows if row["split"] == split]
        assert {row["seed"] for row in selected} == {seed}
        assert {row["sampling"] for row in selected} == {"independent_uniform_PCG64"}
        np.testing.assert_allclose(
            [[row["ks_N_m"], row["cs_N_s_m"]] for row in selected[:2]],
            expected[split], rtol=0, atol=1e-11,
        )


def test_sampling_neither_uses_nor_changes_global_numpy_rng():
    previous = np.random.get_state()
    try:
        np.random.seed(17)
        expected_next = np.random.random(3)
        np.random.seed(17)
        first = make_setups()
        np.testing.assert_array_equal(np.random.random(3), expected_next)
        np.random.seed(9811)
        np.random.random(100)
        assert make_setups() == first
    finally:
        np.random.set_state(previous)


@pytest.mark.parametrize("field,bad", [
    ("ks_N_m", np.nan), ("ks_N_m", np.inf), ("ks_N_m", 17999.0),
    ("cs_N_s_m", -np.inf), ("cs_N_s_m", 2658.01),
    ("split", "development"), ("split", "validation"),
    ("setup_id", "train_999"),
])
def test_setup_validation_rejects_invalid_input_or_role(field, bad):
    rows = make_setups()
    rows[0][field] = bad
    with pytest.raises(ValueError):
        validate_setups(rows)


def test_setup_validation_never_silently_drops_duplicate_pairs_or_ids():
    rows = make_setups()
    rows[-1].update(ks_N_m=rows[0]["ks_N_m"], cs_N_s_m=rows[0]["cs_N_s_m"])
    with pytest.raises(ValueError):
        validate_setups(rows)
    rows = make_setups()
    rows[-1]["setup_id"] = rows[0]["setup_id"]
    with pytest.raises(ValueError):
        validate_setups(rows)
    with pytest.raises(ValueError):
        validate_setups(make_setups()[:-1])


@pytest.mark.parametrize("field", ["setup_id", "split", "ks_N_m", "cs_N_s_m"])
def test_setup_validation_rejects_missing_required_field(field):
    rows = make_setups()
    del rows[0][field]
    with pytest.raises(ValueError):
        validate_setups(rows)


def test_valid_summary_preserves_primary_units_and_resolution_basis(valid_summary):
    classified = classify_summary(valid_summary)
    assert classified["target_valid"] and classified["numerical_primary_valid"]
    assert classified["A_mm"] == pytest.approx(valid_summary["A_m"] * 1000)
    assert classified["failure_reasons"] == []
    assert classified["settling_status"] == "resolved_under_adopted_settings"
    assert "no separate per-row refinement" in classified["resolution_basis"]


def test_unresolved_settling_does_not_discard_valid_primary_target(valid_summary):
    valid_summary.update(settling_status="unresolved", settling_entry_s=None,
                         settling_after_exit_s=None)
    classified = classify_summary(valid_summary)
    assert classified["target_valid"] and classified["numerical_primary_valid"]
    assert classified["A_mm"] is not None
    assert classified["settling_status"] == "unresolved"
    assert classified["settling_after_exit_s"] is None


@pytest.mark.parametrize("contact", [-10.0, 0.0, 0.5, 1.0])
def test_invalid_contact_nulls_target_but_preserves_numerical_primary_flag(valid_summary, contact):
    valid_summary["minimum_contact_N"] = contact
    classified = classify_summary(valid_summary)
    assert classified["numerical_primary_valid"]
    assert not classified["contact_consistent"] and not classified["target_valid"]
    assert classified["A_mm"] is None
    assert "contact_nonpositive_or_ambiguous" in classified["failure_reasons"]


@pytest.mark.parametrize("field,bad", [
    ("tail_pass", False), ("tail_bound_m", 0.001), ("tail_bound_m", -1.0),
    ("tail_limit_m", 0.001), ("energy_pass", False),
    ("maximum_energy_increase_J", 1.0), ("energy_increase_allowance_J", 1.0),
    ("solver_success", False), ("finite_states", False),
    ("end_time_s", 10.0), ("observation_dt_s", 0.00025),
    ("band_m", 0.0005), ("confirmation_s", 0.5),
    ("A_m", -0.01), ("A_m", 0.0), ("A_post_m", 0.5),
    ("A_post_m", -1.0), ("A_signed_m", 0.0),
    ("A_time_s", 5.1), ("A_post_time_s", 0.4),
    ("A_m", np.nan), ("A_m", np.inf), ("A_post_m", None),
    ("post_bump_energy_start_J", None),
])
def test_invalid_numerics_or_settings_disable_target_with_recorded_reason(valid_summary, field, bad):
    valid_summary[field] = bad
    classified = classify_summary(valid_summary)
    assert not classified["numerical_primary_valid"]
    assert not classified["target_valid"] and classified["A_mm"] is None
    assert classified["failure_reasons"]
    assert classified["settling_status"] == "unresolved"
    assert classified["settling_after_exit_s"] is None


@pytest.mark.parametrize("error", [1e-12, np.nan, np.inf, None])
def test_exit_state_continuity_failure_is_retained_without_target(valid_summary, error):
    classified = classify_summary(valid_summary, continuity_error=error)
    assert not classified["target_valid"] and classified["A_mm"] is None
    assert "exit_state_discontinuity" in classified["failure_reasons"]


def test_missing_summary_fields_fail_closed_with_reasons():
    classified = classify_summary({})
    assert not classified["target_valid"]
    assert classified["A_mm"] is None
    assert "missing_or_nonfinite_diagnostic" in classified["failure_reasons"]


@pytest.mark.parametrize("field,bad", [
    ("settling_entry_s", 4.5), ("settling_after_exit_s", -0.1),
    ("settling_entry_s", None), ("settling_after_exit_s", np.nan),
])
def test_invalid_settling_metadata_does_not_erase_valid_peak(valid_summary, field, bad):
    valid_summary[field] = bad
    classified = classify_summary(valid_summary)
    assert classified["target_valid"]
    assert classified["settling_status"] == "unresolved"
    assert classified["settling_after_exit_s"] is None


def test_cache_reuses_baseline_values_and_records_artifact_identity(pilot_record):
    cache = load_verified_pilots(VERIFICATION, MODEL)
    assert len(cache) == 9
    assert len({row["pilot_id"] for row in cache.values()}) == 9
    for pilot in pilot_record["pilots"]:
        pair = (pilot["parameters"]["ks"], pilot["parameters"]["cs"])
        assert cache[pair]["summary"] == pilot["bands"]["1"]["runs"]["base_1ms"]
        assert cache[pair]["summary"]["end_time_s"] == 5.0
        assert cache[pair]["summary"]["observation_dt_s"] == 0.001
        assert cache[pair]["source_sha256"] == sha256_file(VERIFICATION)


@pytest.mark.parametrize("mutation", [
    "source_hash", "numpy_version", "scipy_version", "python_version",
    "selected_settings", "baseline_settings", "overall_failed", "tests_failed",
    "bump", "initial_state", "pilot_failed", "pilot_check_failed", "empty_checks",
    "pilot_mass", "pilot_horizon", "baseline_tail", "baseline_grid",
    "missing_pilot", "duplicate_pilot",
])
def test_cache_rejects_stale_conflicting_or_failed_provenance(tmp_path, pilot_record, mutation):
    data = deepcopy(pilot_record)
    first = data["pilots"][0]
    baseline = first["bands"]["1"]["runs"]["base_1ms"]
    if mutation == "source_hash":
        key = next(key for key in data["input_sha256"] if key.replace("\\", "/") == "Suspension_Model/quarter_car.py")
        data["input_sha256"][key] = "0" * 64
    elif mutation in ("numpy_version", "scipy_version"):
        data["environment"]["packages"][mutation.removesuffix("_version")] = "0.0.0"
    elif mutation == "python_version":
        data["environment"]["python"] = "different Python"
    elif mutation == "selected_settings":
        data["selected_settings"]["solver"]["rtol"] = 1e-3
    elif mutation == "baseline_settings":
        data["baseline_solver"]["rtol"] = 1e-3
    elif mutation == "overall_failed":
        data["passed"] = False
    elif mutation == "tests_failed":
        data["unit_tests_passed"] = False
    elif mutation == "bump":
        data["bump"]["height_m"] = 0.06
    elif mutation == "initial_state":
        data["initial_state"][1] = 0.01
    elif mutation == "pilot_failed":
        first["passed"] = False
    elif mutation == "pilot_check_failed":
        first["checks"]["solver_peak_agreement"] = False
    elif mutation == "empty_checks":
        first["checks"] = {}
    elif mutation == "pilot_mass":
        first["parameters"]["ms"] += 1
    elif mutation == "pilot_horizon":
        first["horizon_s"] = 10.0
    elif mutation == "baseline_tail":
        baseline["tail_pass"] = False
    elif mutation == "baseline_grid":
        baseline["observation_dt_s"] = 0.00025
    elif mutation == "missing_pilot":
        data["pilots"].pop()
    else:
        data["pilots"][-1] = deepcopy(first)
    altered = tmp_path / "altered_verification.json"
    altered.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_verified_pilots(altered, MODEL)


def test_nonfinite_failure_diagnostics_are_json_null_without_losing_identity():
    failure = {"setup_id": "test_017", "split": "test", "A_m": np.inf,
               "trace_diagnostic": [np.float64(np.nan), -np.inf, 1.25],
               "target_valid": False, "failure_reasons": ["solver_failure"]}
    safe = safe_json(failure)
    assert safe["setup_id"] == "test_017" and safe["split"] == "test"
    assert safe["A_m"] is None and safe["trace_diagnostic"] == [None, None, 1.25]
    assert safe["target_valid"] is False
    assert safe["failure_reasons"] == ["solver_failure"]
    json.dumps(safe, allow_nan=False)
