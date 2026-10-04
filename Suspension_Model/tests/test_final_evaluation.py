"""Final-stage guards using synthetic test responses only; no real test access."""

from copy import deepcopy
import csv
from dataclasses import asdict
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np
import pytest
from sklearn.preprocessing import StandardScaler

import final_evaluation as final
from dataset_design import classify_summary, sha256_file
from quarter_car import Parameters


ROOT = Path(__file__).resolve().parents[1]
SPECS = [{"model_id": "linear", "family": "linear"},
         {"model_id": "svr", "family": "rbf_svr", "C": 100., "gamma": 1., "epsilon": .05}]


@pytest.fixture
def synthetic_development():
    rng = np.random.default_rng(91)
    result = {}
    for role, count, low, high in [
        ("train", 225, [18000, 1594.8], [25000, 2300]),
        ("validation", 75, [26000, 2400], [30000, 2658]),
    ]:
        X = rng.uniform(low, high, (count, 2))
        result[role] = {"ids": [f"{role}_{i:03d}" for i in range(1, count+1)], "X": X,
                        "y": 40 + (X[:, 0]-24000)/6000 - (X[:, 1]-2126.4)/531.6}
    return result


def test_two_fresh_scalers_and_regressors_use_all_300_original_labels(monkeypatch, synthetic_development):
    X = np.vstack([synthetic_development[r]["X"] for r in ("train", "validation")])
    y = np.concatenate([synthetic_development[r]["y"] for r in ("train", "validation")])
    seen = []
    real_fit = StandardScaler.fit
    def tracked_fit(self, values, labels=None, **kwargs):
        seen.append((id(self), np.array(values), np.array(labels)))
        return real_fit(self, values, labels, **kwargs)
    monkeypatch.setattr(StandardScaler, "fit", tracked_fit)
    models, records = final.refit_models(synthetic_development, deepcopy(SPECS))
    assert set(models) == set(records) == {"linear", "svr"}
    assert len(seen) == len({item[0] for item in seen}) == 2
    for _, fit_X, fit_y in seen:
        np.testing.assert_array_equal(fit_X, X)
        np.testing.assert_array_equal(fit_y, y)
    for key, model in models.items():
        scaler = model.named_steps["scale"]
        assert scaler.n_samples_seen_ == records[key]["training_count"] == 300
        np.testing.assert_allclose(scaler.mean_, X.mean(axis=0), rtol=0, atol=1e-10)
        assert not np.allclose(scaler.mean_, synthetic_development["train"]["X"].mean(axis=0))


@pytest.mark.parametrize("failure", ["wrong_spec", "missing_row", "duplicate_pair", "wrong_ids", "invalid_target"])
def test_refit_rejects_scope_or_development_data_changes(monkeypatch, synthetic_development, failure):
    specs = deepcopy(SPECS)
    if failure == "wrong_spec":
        specs[1]["C"] = 10.
    elif failure == "missing_row":
        synthetic_development["validation"]["ids"].pop()
    elif failure == "duplicate_pair":
        synthetic_development["validation"]["X"][0] = synthetic_development["train"]["X"][0]
    elif failure == "wrong_ids":
        synthetic_development["validation"]["ids"][0] = "test_001"
    else:
        synthetic_development["validation"]["y"][0] = np.nan
    monkeypatch.setattr(final, "build_pipeline", lambda spec: pytest.fail("bad inputs reached fitting"))
    with pytest.raises(ValueError):
        final.refit_models(synthetic_development, specs)


def test_failed_refit_is_not_converted_to_a_frozen_model(monkeypatch, synthetic_development):
    def failed_fit(*args):
        raise RuntimeError("injected fit failure")
    monkeypatch.setattr(final, "build_pipeline", lambda spec: SimpleNamespace(fit=failed_fit))
    with pytest.raises(RuntimeError, match="injected fit failure"):
        final.refit_models(synthetic_development, SPECS)


@pytest.fixture
def synthetic_test():
    rows, diagnostics, manifest = [], [], []
    for index in range(1, 101):
        setup = {"setup_id": f"test_{index:03d}", "split": "test",
                 "ks_N_m": 18000.0+100*index, "cs_N_s_m": 1800.0+5*index}
        A = 0.040 + (index % 5)*0.0002
        raw = {"A_m": A, "A_post_m": .03, "A_signed_m": A, "A_time_s": .44,
               "A_post_time_s": .5, "end_time_s": 5., "observation_dt_s": .001,
               "band_m": .001, "confirmation_s": 1., "solver_success": True, "finite_states": True,
               "tail_bound_m": 1e-6, "tail_limit_m": .0005, "tail_pass": True,
               "minimum_contact_N": 2500., "post_bump_energy_start_J": 1.,
               "maximum_energy_increase_J": 0., "energy_increase_allowance_J": 1e-10,
               "energy_pass": True, "settling_status": "candidate", "settling_entry_s": 2.,
               "settling_after_exit_s": 1.5}
        diagnostics.append({"setup": deepcopy(setup), "parameters": asdict(Parameters(ks=setup["ks_N_m"], cs=setup["cs_N_s_m"])),
                            "raw_summary": raw, "exit_state_difference": 0., "validity": classify_summary(raw, 0.)})
        manifest.append(deepcopy(setup))
        rows.append({**{k: str(v) for k, v in setup.items()}, "A_mm": str(1000*A), "target_valid": "True"})
    return rows, diagnostics, manifest


def test_synthetic_test_loader_preserves_all_100_ids_features_and_mm_targets(synthetic_test):
    result = final.validate_test_rows(*synthetic_test)
    assert result["X"].shape == (100, 2) and result["y"].shape == (100,)
    assert result["ids"] == [f"test_{i:03d}" for i in range(1, 101)]
    assert result["y"][0] == synthetic_test[1][0]["raw_summary"]["A_m"] * 1000


@pytest.mark.parametrize("failure", ["count", "duplicate_id", "order", "role", "features", "units", "nonfinite", "flag", "physics", "raw_tail"])
def test_test_validation_rejects_bad_rows_without_dropping_any(synthetic_test, failure):
    rows, diagnostics, manifest = synthetic_test
    if failure == "count": rows.pop()
    elif failure == "duplicate_id": rows[1]["setup_id"] = rows[0]["setup_id"]
    elif failure == "order": rows[0], rows[1] = rows[1], rows[0]
    elif failure == "role": rows[0]["split"] = "validation"
    elif failure == "features": rows[0]["A_post_m"] = "0.03"
    elif failure == "units": rows[0]["A_mm"] = "0.0402"
    elif failure == "nonfinite": rows[0]["A_mm"] = "nan"
    elif failure == "flag": rows[0]["target_valid"] = "False"
    elif failure == "physics": diagnostics[0]["parameters"]["ms"] += 1
    else: diagnostics[0]["raw_summary"]["tail_pass"] = False
    with pytest.raises(ValueError):
        final.validate_test_rows(rows, diagnostics, manifest)


@pytest.fixture
def synthetic_seal(tmp_path, monkeypatch):
    project, checkpoint = tmp_path / "project", tmp_path / "checkpoint"
    project.mkdir()
    checkpoint.mkdir()
    monkeypatch.setattr(final, "ROOT", project)
    (project / "source.py").write_text("# synthetic source\n", encoding="utf-8")
    (project / "development.json").write_text("{}\n", encoding="utf-8")
    plan = {"selection": {"preferred_model": "svr", "selected_development_id": "svr_15", "specs": deepcopy(SPECS)},
            "refit_rows": 300, "test_rows": 100, "features": list(final.FEATURES),
            "source_sha256": {"project/source.py": sha256_file(project / "source.py")},
            "pretest_input_sha256": {"development.json": sha256_file(project / "development.json")},
            "expected_test_sha256": {name: "a" * 64 for name in final.TEST_FILES}}
    final.write_json(checkpoint / "frozen_plan.json", plan)
    for key in ("linear", "svr"):
        (checkpoint / f"{key}.joblib").write_bytes(b"synthetic sealed bytes, not a fitted model")
    refit = {"stage": "models_frozen", "training_count": 300, "model_ids": ["linear", "svr"],
             "plan_sha256": sha256_file(checkpoint / "frozen_plan.json"),
             "fits": {key: {"training_count": 300, "fit_status": 0, "spec": deepcopy(SPECS[i])}
                      for i, key in enumerate(("linear", "svr"))},
             "model_sha256": {key: sha256_file(checkpoint / f"{key}.joblib") for key in ("linear", "svr")}}
    final.write_json(checkpoint / "refit.json", refit)
    return project, checkpoint, plan, refit


def test_seal_checks_hashes_and_300_row_state_without_loading_model_bytes(synthetic_seal):
    _, checkpoint, plan, refit = synthetic_seal
    assert final.verify_seal(checkpoint) == (plan, refit)


@pytest.mark.parametrize("failure", ["old_225", "model_bytes", "changed_plan", "empty_provenance", "wrong_frozen_spec"])
def test_invalid_seal_fails_closed_before_test_access(synthetic_seal, failure):
    _, checkpoint, plan, refit = synthetic_seal
    if failure == "old_225":
        refit["fits"]["svr"]["training_count"] = 225
        final.write_json(checkpoint / "refit.json", refit)
    elif failure == "model_bytes":
        (checkpoint / "svr.joblib").write_bytes(b"changed")
    else:
        if failure == "empty_provenance":
            plan["source_sha256"] = {}
            plan["pretest_input_sha256"] = {}
        elif failure == "wrong_frozen_spec":
            plan["selection"]["specs"][1]["C"] = 10
        else:
            plan["refit_rows"] = 400
        final.write_json(checkpoint / "frozen_plan.json", plan)
        if failure != "changed_plan":
            refit["plan_sha256"] = sha256_file(checkpoint / "frozen_plan.json")
            final.write_json(checkpoint / "refit.json", refit)
    with pytest.raises(ValueError):
        final.verify_seal(checkpoint)


def test_failed_seal_prevents_even_hashing_a_reserved_path(tmp_path, monkeypatch):
    def rejected(checkpoint):
        raise ValueError("incomplete frozen refit")
    monkeypatch.setattr(final, "verify_seal", rejected)
    monkeypatch.setattr(final, "sha256_file", lambda p: pytest.fail("reserved bytes hashed before seal validation"))
    with pytest.raises(ValueError, match="incomplete frozen refit"):
        final.load_heldout(tmp_path / "synthetic_dataset", tmp_path / "checkpoint")


def test_synthetic_reserved_reads_occur_only_after_seal_check(tmp_path, monkeypatch, synthetic_test):
    rows, diagnostics, manifest = synthetic_test
    reserved = tmp_path / "heldout_test"
    reserved.mkdir()
    with (reserved / "test.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=final.CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    (reserved / "test_diagnostics.jsonl").write_text("".join(json.dumps(d) + "\n" for d in diagnostics), encoding="utf-8")
    with (tmp_path / "setup_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)
    plan = {"expected_test_sha256": {name: sha256_file(tmp_path / name) for name in final.TEST_FILES}}
    events = []
    def approved(checkpoint):
        events.append("seal")
        return plan, {"training_count": 300}
    def guarded_hash(path):
        assert events and events[0] == "seal"
        events.append("hash")
        return sha256_file(path)
    monkeypatch.setattr(final, "verify_seal", approved)
    monkeypatch.setattr(final, "sha256_file", guarded_hash)
    assert len(final.load_heldout(tmp_path, tmp_path / "checkpoint")["ids"]) == 100
    assert events == ["seal", "hash", "hash"]


@pytest.fixture
def selection_copy(tmp_path):
    development, reference = tmp_path / "development", tmp_path / "reference"
    development.mkdir()
    reference.mkdir()
    for name in ("summary.json", "development_decision.json", "candidates.json", "development_plan.json", "validation_predictions.csv"):
        shutil.copyfile(ROOT / "ml_development_v1" / name, development / name)
    for name in ("summary.json", "plan.json", "validation_references.jsonl"):
        shutil.copyfile(ROOT / "ml_reference_v1" / name, reference / name)
    return development, reference


def test_selection_retains_the_predeclared_two_models(selection_copy):
    selection = final.frozen_selection(*selection_copy)
    assert selection["preferred_model"] == "svr"
    assert selection["selected_development_id"] == "svr_15"
    assert selection["specs"] == SPECS


@pytest.mark.parametrize("failure", ["failed_reference", "decision_bytes", "reference_from_other_development"])
def test_selection_rejects_failed_or_unlinked_evidence(selection_copy, failure):
    development, reference = selection_copy
    if failure == "failed_reference":
        summary = final.read_json(reference / "summary.json")
        summary["complete"] = False
        final.write_json(reference / "summary.json", summary)
    elif failure == "decision_bytes":
        with (development / "development_decision.json").open("a", encoding="utf-8") as handle:
            handle.write("\n")
    else:
        plan = final.read_json(reference / "plan.json")
        key = next(k for k in plan["source_sha256"] if k.replace("\\", "/") == "ml_development_v1/candidates.json")
        plan["source_sha256"][key] = "0" * 64
        final.write_json(reference / "plan.json", plan)
        summary = final.read_json(reference / "summary.json")
        summary["artifact_sha256"]["plan.json"] = sha256_file(reference / "plan.json")
        final.write_json(reference / "summary.json", summary)
    with pytest.raises(ValueError):
        final.frozen_selection(development, reference)


def test_existing_checkpoint_and_recorded_access_block_repetition(tmp_path, monkeypatch):
    monkeypatch.setattr(final, "frozen_selection", lambda *args: pytest.fail("existing output reached selection"))
    with pytest.raises(FileExistsError):
        final.prepare(tmp_path)
    (tmp_path / "test_access.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(final, "verify_seal", lambda *args: pytest.fail("recorded test access reached re-evaluation"))
    with pytest.raises(FileExistsError):
        final.evaluate(tmp_path)


def test_evaluation_seal_failure_blocks_marker_and_response_access(tmp_path, monkeypatch):
    def rejected(*args):
        raise ValueError("failed frozen refit")
    monkeypatch.setattr(final, "verify_seal", rejected)
    monkeypatch.setattr(final, "load_heldout", lambda *args: pytest.fail("test responses were reached"))
    with pytest.raises(ValueError):
        final.evaluate(tmp_path)
    assert not (tmp_path / "test_access.json").exists()
