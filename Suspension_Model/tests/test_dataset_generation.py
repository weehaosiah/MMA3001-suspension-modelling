"""Synthetic generator guards: no full dataset, simulations or ML execution."""

from copy import deepcopy
import csv
from dataclasses import asdict
import json
from types import SimpleNamespace

import numpy as np
import pytest

import generate_dataset
from dataset_design import classify_summary, sha256_file
from quarter_car import Parameters


@pytest.fixture
def summary():
    """A coherent diagnostic example; no physical simulation is implied."""
    return {
        "A_m": 0.04, "A_post_m": 0.03, "A_signed_m": 0.04,
        "A_time_s": 0.44, "A_post_time_s": 0.5,
        "end_time_s": 5.0, "observation_dt_s": 0.001,
        "band_m": 0.001, "confirmation_s": 1.0,
        "finite_states": True, "solver_success": True,
        "tail_bound_m": 1e-6, "tail_limit_m": 0.0005, "tail_pass": True,
        "minimum_contact_N": 2500.0,
        "post_bump_energy_start_J": 10.0, "maximum_energy_increase_J": 0.0,
        "energy_increase_allowance_J": 1e-9, "energy_pass": True,
        "settling_status": "candidate", "settling_entry_s": 2.0,
        "settling_after_exit_s": 1.5, "integration_runtime_s": 0.2,
        "derivative_evaluations": 6200,
    }


@pytest.fixture
def setup():
    return {"setup_id": "train_113", "split": "train", "ks_N_m": 24000.0,
            "cs_N_s_m": 2126.4, "sampling": "15x15_grid", "seed": None,
            "pilot_id": "kN_cN"}


@pytest.fixture
def cached(summary):
    return {"pilot_id": "kN_cN", "parameters": asdict(Parameters()),
            "summary": summary, "continuity_error": 0.0, "source_sha256": "a" * 64}


def fail_if_simulated(*args, **kwargs):
    raise AssertionError("This test must not integrate a model")


def test_matching_training_cache_is_reused_without_new_work(monkeypatch, setup, cached):
    monkeypatch.setattr(generate_dataset, "simulate", fail_if_simulated)
    diagnostic, exported = generate_dataset.row_result(setup, cached)
    assert diagnostic["setup"] == setup
    assert diagnostic["origin"] == "verified_pilot_baseline"
    assert diagnostic["pilot_artifact_sha256"] == "a" * 64
    assert diagnostic["new_integration_runtime_s"] == 0.0
    assert diagnostic["new_derivative_evaluations"] == 0
    assert diagnostic["original_pilot_integration_runtime_s"] == 0.2
    assert diagnostic["new_solver_completed"] is False
    assert exported["A_mm"] == 40.0 and exported["target_valid"] is True


@pytest.mark.parametrize("split", ["validation", "test"])
def test_cache_reuse_is_restricted_to_training(monkeypatch, setup, cached, split):
    monkeypatch.setattr(generate_dataset, "simulate", fail_if_simulated)
    setup.update(split=split, setup_id=f"{split}_001")
    with pytest.raises(ValueError, match="training"):
        generate_dataset.row_result(setup, cached)


@pytest.mark.parametrize("field", ["ks", "cs", "ms"])
def test_swapped_or_physically_different_cache_is_rejected(monkeypatch, setup, cached, field):
    monkeypatch.setattr(generate_dataset, "simulate", fail_if_simulated)
    cached["parameters"][field] += 1
    with pytest.raises(ValueError, match="parameters"):
        generate_dataset.row_result(setup, cached)


def test_simulation_exception_keeps_identity_and_unknown_solver_cost(monkeypatch, setup):
    def rejected_solver(*args, **kwargs):
        raise RuntimeError("injected incomplete solve")
    monkeypatch.setattr(generate_dataset, "simulate", rejected_solver)
    diagnostic, exported = generate_dataset.row_result(setup)
    assert diagnostic["setup"] == setup
    assert diagnostic["raw_summary"] is None
    assert diagnostic["new_solver_completed"] is False
    assert diagnostic["new_integration_runtime_s"] is None
    assert diagnostic["new_derivative_evaluations"] is None
    assert diagnostic["row_processing_runtime_s"] >= 0
    assert "injected incomplete solve" in diagnostic["exception"]
    assert diagnostic["validity"]["failure_reasons"] == ["simulation_or_diagnostic_exception"]
    assert exported["setup_id"] == setup["setup_id"] and exported["split"] == setup["split"]
    assert exported["A_mm"] is None and exported["target_valid"] is False


def test_diagnostic_failure_retains_known_completed_solver_cost(monkeypatch, setup):
    trajectory = SimpleNamespace(
        elapsed_s=0.123, nfev=40,
        segments=(SimpleNamespace(y=np.zeros((4, 2))), SimpleNamespace(y=np.zeros((4, 2)))),
    )
    monkeypatch.setattr(generate_dataset, "simulate", lambda *args: trajectory)
    def rejected_summary(*args):
        raise ValueError("injected diagnostic failure")
    monkeypatch.setattr(generate_dataset, "summarise", rejected_summary)
    diagnostic, exported = generate_dataset.row_result(setup)
    assert diagnostic["new_solver_completed"] is True
    assert diagnostic["new_integration_runtime_s"] == 0.123
    assert diagnostic["new_derivative_evaluations"] == 40
    assert exported["A_mm"] is None
    assert exported["target_valid"] is False


def write_synthetic_exports(tmp_path, monkeypatch, summary, mutation=None):
    """Write one fake row per role to exercise the real file audit cheaply."""
    monkeypatch.setattr(generate_dataset, "COUNTS", {"train": 1, "validation": 1, "test": 1})
    (tmp_path / "heldout_test").mkdir()
    expected = []
    for index, split in enumerate(("train", "validation", "test")):
        setup = {"setup_id": f"{split}_001", "split": split,
                 "ks_N_m": 24000.0 + index, "cs_N_s_m": 2126.4,
                 "sampling": "synthetic_test", "seed": None, "pilot_id": None}
        expected.append(deepcopy(setup))
        raw = deepcopy(summary)
        diagnostic = {"setup": deepcopy(setup), "parameters": asdict(Parameters(ks=setup["ks_N_m"])),
                      "raw_summary": raw, "exit_state_difference": 0.0,
                      "validity": classify_summary(raw, 0.0)}
        exported = {key: setup[key] for key in ("setup_id", "split", "ks_N_m", "cs_N_s_m")}
        exported.update(A_mm=40.0, target_valid=True)
        if mutation is not None and split == "train":
            mutation(diagnostic, exported)
        folder = tmp_path / "heldout_test" if split == "test" else tmp_path
        with (folder / f"{split}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=generate_dataset.TARGET_COLUMNS)
            writer.writeheader()
            writer.writerow(exported)
        (folder / f"{split}_diagnostics.jsonl").write_text(json.dumps(diagnostic) + "\n", encoding="utf-8")
    return expected


def test_export_audit_accepts_coherent_files_without_exposing_targets(tmp_path, monkeypatch, summary):
    expected = write_synthetic_exports(tmp_path, monkeypatch, summary)
    audit = generate_dataset.audit_exports(tmp_path, expected)
    assert set(audit) == {"train", "validation", "test"}
    assert all(value == {"rows": 1, "eligible_targets": 1, "failed_targets": 0,
                         "identity_and_units_pass": True} for value in audit.values())


@pytest.mark.parametrize("failure", ["energy", "tail", "continuity", "contact", "parameters", "input_identity"])
def test_export_audit_rejects_stale_valid_flags_or_mismatched_physics(
    tmp_path, monkeypatch, summary, failure
):
    def corrupted(diagnostic, exported):
        if failure == "energy":
            diagnostic["raw_summary"]["energy_pass"] = False
        elif failure == "tail":
            diagnostic["raw_summary"]["tail_pass"] = False
        elif failure == "continuity":
            diagnostic["exit_state_difference"] = 1e-6
        elif failure == "contact":
            diagnostic["raw_summary"]["minimum_contact_N"] = -1.0
        elif failure == "parameters":
            diagnostic["parameters"]["ms"] += 1
        else:
            diagnostic["setup"]["ks_N_m"] += 1
    expected = write_synthetic_exports(tmp_path, monkeypatch, summary, corrupted)
    with pytest.raises(ValueError):
        generate_dataset.audit_exports(tmp_path, expected)


@pytest.mark.parametrize("failure", ["wrong_units", "nonfinite_target", "undeclared_id", "stale_csv_flag"])
def test_export_audit_rejects_corrupt_csv(tmp_path, monkeypatch, summary, failure):
    def corrupted(diagnostic, exported):
        if failure == "wrong_units":
            exported["A_mm"] = 0.04
        elif failure == "nonfinite_target":
            exported["A_mm"] = float("inf")
        elif failure == "undeclared_id":
            exported["setup_id"] = "train_999"
        else:
            exported["target_valid"] = False
    expected = write_synthetic_exports(tmp_path, monkeypatch, summary, corrupted)
    with pytest.raises(ValueError):
        generate_dataset.audit_exports(tmp_path, expected)


def test_export_audit_retains_failed_rows_with_blank_targets(tmp_path, monkeypatch, summary):
    def failed_row(diagnostic, exported):
        diagnostic["raw_summary"]["tail_pass"] = False
        diagnostic["validity"] = classify_summary(diagnostic["raw_summary"], 0.0)
        exported.update(A_mm=None, target_valid=False)
    expected = write_synthetic_exports(tmp_path, monkeypatch, summary, failed_row)
    audit = generate_dataset.audit_exports(tmp_path, expected)
    assert audit["train"]["rows"] == 1
    assert audit["train"]["eligible_targets"] == 0 and audit["train"]["failed_targets"] == 1


def test_export_audit_accepts_preserved_simulation_exception(tmp_path, monkeypatch, summary):
    def failed_row(diagnostic, exported):
        diagnostic["raw_summary"] = None
        diagnostic["exit_state_difference"] = None
        diagnostic["validity"] = classify_summary({}, None)
        exported.update(A_mm=None, target_valid=False)
    expected = write_synthetic_exports(tmp_path, monkeypatch, summary, failed_row)
    audit = generate_dataset.audit_exports(tmp_path, expected)
    assert audit["train"]["failed_targets"] == 1


def test_export_audit_rejects_target_filled_for_failed_row(tmp_path, monkeypatch, summary):
    def failed_row(diagnostic, exported):
        diagnostic["raw_summary"]["tail_pass"] = False
        diagnostic["validity"] = classify_summary(diagnostic["raw_summary"], 0.0)
        exported.update(A_mm=40.0, target_valid=False)
    expected = write_synthetic_exports(tmp_path, monkeypatch, summary, failed_row)
    with pytest.raises(ValueError, match="empty ML target"):
        generate_dataset.audit_exports(tmp_path, expected)


@pytest.mark.parametrize("changed", ["generation_plan.json", "setup_manifest.csv"])
def test_frozen_manifest_check_detects_byte_changes(tmp_path, changed):
    names = ("generation_plan.json", "setup_manifest.csv")
    for name in names:
        (tmp_path / name).write_text("original bytes\n", encoding="utf-8")
    hashes = {name: sha256_file(tmp_path / name) for name in names}
    assert generate_dataset.frozen_manifests_unchanged(tmp_path, hashes)
    (tmp_path / changed).write_text("changed bytes\n", encoding="utf-8")
    assert not generate_dataset.frozen_manifests_unchanged(tmp_path, hashes)


def test_existing_output_is_refused_before_any_mutation(tmp_path, monkeypatch):
    sentinel = tmp_path / "keep.txt"
    sentinel.write_bytes(b"existing user data")
    before = list(tmp_path.iterdir())
    monkeypatch.setattr(generate_dataset, "make_setups", fail_if_simulated)
    monkeypatch.setattr(generate_dataset, "simulate", fail_if_simulated)
    with pytest.raises(FileExistsError):
        generate_dataset.generate(tmp_path)
    assert list(tmp_path.iterdir()) == before
    assert sentinel.read_bytes() == b"existing user data"
