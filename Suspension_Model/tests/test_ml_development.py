"""Leakage, selection, metric and input guards for development-only regression.

Synthetic fits are deliberately small. Real file access is limited to the
training/validation artifacts and common metadata; final-test files are unused.
"""

import csv
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import joblib
import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

import ml_development as ml
from dataset_design import sha256_file


DATASET = Path(__file__).resolve().parents[1] / "dataset_v1"


@pytest.fixture
def small_data():
    train_x = np.array([[18000, 1594.8], [19000, 1700], [20000, 1850],
                        [21000, 2000], [22000, 2200], [23000, 2300]], dtype=float)
    validation_x = np.array([[28000, 2500], [30000, 2658], [24000, 2126.4]], dtype=float)
    def target(x):
        return 30 + (x[:, 0] - 18000) / 1200 - 0.005 * (x[:, 1] - 1600)
    return ({"X": train_x, "y": target(train_x)},
            {"X": validation_x, "y": target(validation_x)})


def test_candidate_budget_and_order_match_predeclared_search():
    specs = ml.candidate_specs()
    assert len(specs) == 18 and len({s["model_id"] for s in specs}) == 18
    assert {s["family"] for s in specs} == {"rbf_svr"}
    settings = [(s["C"], s["gamma"], s["epsilon"]) for s in specs]
    assert len(set(settings)) == 18 and settings == sorted(settings)
    assert {s[0] for s in settings} == {1, 10, 100}
    assert {s[1] for s in settings} == {0.1, 1, 10}
    assert {s[2] for s in settings} == {0.05, 0.2}


@pytest.mark.parametrize("spec", [ml.LINEAR_SPEC, ml.candidate_specs()[0]])
def test_pipeline_contains_only_feature_scaler_and_expected_regressor(spec):
    pipeline = ml.build_pipeline(spec)
    assert list(pipeline.named_steps) == ["scale", "regressor"]
    assert isinstance(pipeline.named_steps["scale"], StandardScaler)
    if spec["family"] == "linear":
        assert isinstance(pipeline.named_steps["regressor"], LinearRegression)
    else:
        svr = pipeline.named_steps["regressor"]
        assert isinstance(svr, SVR) and svr.kernel == "rbf"
        assert svr.epsilon == 0.05  # Target is in mm, with no learned target scaling.


def test_metrics_known_errors_preserve_mm_and_underprediction_sign():
    result = ml.metrics([10, 20, 30], [12, 17, 29])
    assert result["n"] == 3
    assert result["MAE_mm"] == 2
    assert result["RMSE_mm"] == pytest.approx(np.sqrt(14/3))
    assert result["max_absolute_error_mm"] == 3
    assert result["max_underprediction_mm"] == 3
    assert result["mean_residual_mm"] == pytest.approx(2/3)
    assert result["R2"] == pytest.approx(0.93)


def test_all_overpredictions_have_zero_underprediction_and_constant_r2_is_undefined():
    result = ml.metrics([10, 10], [11, 12])
    assert result["max_underprediction_mm"] == 0
    assert result["mean_residual_mm"] == -1.5
    assert result["R2"] is None


@pytest.mark.parametrize("truth,prediction", [
    ([], []), ([1, 2], [1]), ([[1, 2]], [[1, 2]]),
    ([np.nan], [1]), ([1], [np.inf]),
])
def test_metrics_reject_invalid_vectors(truth, prediction):
    with pytest.raises(ValueError):
        ml.metrics(truth, prediction)


def selection_records():
    linear = {**ml.LINEAR_SPEC, "status": "ok", "validation": {"RMSE_mm": 1.0}}
    svrs = [{**spec, "status": "ok", "validation": {"RMSE_mm": 1.0}}
            for spec in ml.candidate_specs()]
    return [linear, *svrs]


def test_exact_ties_favour_linear_and_declared_svr_order_independent_of_record_order():
    records = selection_records()[::-1]
    result = ml.select_models(records)
    assert result["preferred_model_id"] == "linear"
    assert result["best_svr_id"] == "svr_01"
    assert result["best_svr_settings"] == {"C": 1.0, "gamma": 0.1, "epsilon": 0.05}


def test_selection_uses_unrounded_validation_rmse_not_training_error():
    records = selection_records()
    records[7]["validation"]["RMSE_mm"] = 1 - 1e-12
    records[7]["training"] = {"RMSE_mm": 999.0}
    records[0]["training"] = {"RMSE_mm": 0.0}
    result = ml.select_models(records)
    assert result["preferred_model_id"] == records[7]["model_id"]


@pytest.mark.parametrize("failure", ["failed", "nan", "inf", "missing_metric"])
def test_selection_refuses_failed_or_nonfinite_candidate(failure):
    records = selection_records()
    if failure == "failed":
        records[-1]["status"] = "failed"
    elif failure == "missing_metric":
        records[-1]["validation"] = {}
    else:
        records[-1]["validation"]["RMSE_mm"] = float(failure)
    with pytest.raises(ValueError):
        ml.select_models(records)


@pytest.mark.parametrize("failure", ["negative_rmse", "duplicate_id"])
def test_selection_rejects_impossible_error_or_duplicate_candidate_identity(failure):
    records = selection_records()
    if failure == "negative_rmse":
        records[-1]["validation"]["RMSE_mm"] = -0.1
    else:
        records[-1]["model_id"] = records[-2]["model_id"]
    with pytest.raises(ValueError):
        ml.select_models(records)


def test_each_pipeline_fits_training_only_and_validation_does_not_refit_scaler(monkeypatch, small_data):
    train, validation = small_data
    seen_scalers, seen_regressors = [], []
    real_scale_fit = StandardScaler.fit
    def recorded_scale_fit(self, X, y=None, **kwargs):
        seen_scalers.append(np.asarray(X).copy())
        return real_scale_fit(self, X, y, **kwargs)
    monkeypatch.setattr(StandardScaler, "fit", recorded_scale_fit)
    for cls in (LinearRegression, SVR):
        original = cls.fit
        def recorded_regressor_fit(self, X, y, _original=original, **kwargs):
            seen_regressors.append((np.asarray(X).copy(), np.asarray(y).copy()))
            return _original(self, X, y, **kwargs)
        monkeypatch.setattr(cls, "fit", recorded_regressor_fit)
    records, models = ml.fit_candidates(train, validation)
    assert len(records) == len(models) == len(seen_scalers) == len(seen_regressors) == 19
    assert all(record["status"] == "ok" for record in records)
    for X in seen_scalers:
        np.testing.assert_array_equal(X, train["X"])
    for X, y in seen_regressors:
        assert X.shape == train["X"].shape
        np.testing.assert_array_equal(y, train["y"])
    for model in models.values():
        scaler = model.named_steps["scale"]
        assert scaler.n_samples_seen_ == len(train["X"])
        np.testing.assert_allclose(scaler.mean_, train["X"].mean(axis=0), rtol=0, atol=1e-10)
        before = [scaler.mean_.copy(), scaler.scale_.copy(), scaler.var_.copy()]
        ml.predict_checked(model, validation["X"])
        for previous, current in zip(before, [scaler.mean_, scaler.scale_, scaler.var_]):
            np.testing.assert_array_equal(previous, current)


def test_fit_failure_is_recorded_and_cannot_silently_select_remaining_models(monkeypatch, small_data):
    def rejected_build(spec):
        raise RuntimeError("injected model failure")
    monkeypatch.setattr(ml, "build_pipeline", rejected_build)
    records, models = ml.fit_candidates(*small_data)
    assert len(records) == 19 and models == {}
    assert all(r["status"] == "failed" and "injected model failure" in r["error"] for r in records)
    with pytest.raises(ValueError):
        ml.select_models(records)


@pytest.mark.parametrize("bad", [np.nan, np.inf, 0.0, -1.0])
def test_invalid_training_target_is_rejected_before_fit(monkeypatch, small_data, bad):
    train, validation = small_data
    train["y"][0] = bad
    monkeypatch.setattr(ml, "build_pipeline", lambda spec: pytest.fail("fit started with bad target"))
    with pytest.raises(ValueError):
        ml.fit_candidates(train, validation)


@pytest.mark.parametrize("bad", [np.nan, np.inf, 0.0, -1.0])
def test_invalid_validation_target_is_rejected_before_fit(monkeypatch, small_data, bad):
    train, validation = small_data
    validation["y"][0] = bad
    monkeypatch.setattr(ml, "build_pipeline", lambda spec: pytest.fail("fit started with bad validation target"))
    with pytest.raises(ValueError):
        ml.fit_candidates(train, validation)


@pytest.mark.parametrize("query", [
    [], [24000, 2126.4], [[24000]], [[24000, 2126.4, 1]],
    [[np.nan, 2126.4]], [[24000, np.inf]], [[17999, 2126.4]],
    [[30000.1, 2126.4]], [[24000, 1594.7]], [[24000, 2658.1]],
])
def test_prediction_rejects_invalid_queries_before_calling_model(query):
    model = SimpleNamespace(predict=lambda X: pytest.fail("invalid query reached model"))
    with pytest.raises(ValueError):
        ml.predict_checked(model, query)


@pytest.mark.parametrize("result", [[np.nan, 1], [np.inf, 1], [1], [[1], [1]]])
def test_prediction_rejects_nonfinite_or_wrong_shape_model_output(result):
    model = SimpleNamespace(predict=lambda X: result)
    with pytest.raises(ValueError):
        ml.predict_checked(model, [[18000, 1594.8], [30000, 2658]])


def test_prediction_includes_domain_endpoints_without_clipping_negative_model_values():
    model = SimpleNamespace(predict=lambda X: [-0.25, 40.0])
    result = ml.predict_checked(model, [[18000, 1594.8], [30000, 2658]])
    np.testing.assert_array_equal(result, [-0.25, 40.0])


def test_saved_fitted_pipeline_preserves_predictions(tmp_path, small_data):
    train, validation = small_data
    model = ml.build_pipeline(ml.candidate_specs()[0])
    model.fit(train["X"], train["y"])
    path = tmp_path / "synthetic_pipeline.joblib"
    joblib.dump(model, path)
    restored = joblib.load(path)  # Only the file created by this test is loaded.
    np.testing.assert_array_equal(ml.predict_checked(model, validation["X"]),
                                  ml.predict_checked(restored, validation["X"]))


def test_loader_never_opens_heldout_files_and_uses_exact_two_features(monkeypatch):
    original_open = Path.open
    accessed = []
    def guarded_open(path, *args, **kwargs):
        assert "heldout_test" not in path.parts, "Development read a reserved test file"
        accessed.append(path.name)
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded_open)
    data = ml.load_development(DATASET)
    assert set(data) == {"train", "validation"}
    assert data["train"]["X"].shape == (225, 2)
    assert data["validation"]["X"].shape == (75, 2)
    assert data["train"]["ids"][0] == "train_001"
    for part in data.values():
        for index in (0, len(part["ids"]) - 1):
            diagnostic = part["diagnostics"][index]
            np.testing.assert_array_equal(part["X"][index],
                                          [diagnostic["setup"]["ks_N_m"], diagnostic["setup"]["cs_N_s_m"]])
            assert part["y"][index] == diagnostic["raw_summary"]["A_m"] * 1000
    assert set(accessed) <= {"summary.json", *ml.DEVELOPMENT_FILES}


@pytest.fixture
def development_copy(tmp_path):
    # Copy no held-out path, even for failure tests. All values remain synthetic
    # mutations or already-authorised training/validation data.
    for name in ("summary.json", *ml.DEVELOPMENT_FILES):
        shutil.copyfile(DATASET / name, tmp_path / name)
    return tmp_path


def refresh_hash(dataset, name):
    path = dataset / "summary.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    summary["artifact_sha256"][name] = sha256_file(dataset / name)
    path.write_text(json.dumps(summary), encoding="utf-8")


def rewrite_first_csv_row(path, field, value):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns, rows = reader.fieldnames, list(reader)
    rows[0][field] = value
    if field not in columns:
        columns.append(field)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_loader_rejects_stale_development_file_hash(development_copy):
    with (development_copy / "train.csv").open("a", encoding="utf-8") as handle:
        handle.write("\n")
    with pytest.raises(ValueError, match="hash"):
        ml.load_development(development_copy)


@pytest.mark.parametrize("field,value", [
    ("target_valid", "False"), ("A_mm", ""), ("A_mm", "nan"), ("A_mm", "inf"),
    ("A_mm", "0.04"), ("setup_id", "train_002"), ("split", "test"),
    ("ks_N_m", "24000"), ("A_post_m", "0.03"),
])
def test_loader_rejects_bad_identity_units_validity_or_feature_schema(development_copy, field, value):
    rewrite_first_csv_row(development_copy / "train.csv", field, value)
    refresh_hash(development_copy, "train.csv")
    with pytest.raises(ValueError):
        ml.load_development(development_copy)


@pytest.mark.parametrize("mutation", ["physical", "tail", "stale_flag", "count"])
def test_loader_recomputes_diagnostic_validity_and_physics(development_copy, mutation):
    path = development_copy / "validation_diagnostics.jsonl"
    diagnostics = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if mutation == "physical":
        diagnostics[0]["parameters"]["ms"] += 1
    elif mutation == "tail":
        diagnostics[0]["raw_summary"]["tail_pass"] = False
    elif mutation == "stale_flag":
        diagnostics[0]["validity"]["numerical_primary_valid"] = False
    else:
        diagnostics.pop()
    path.write_text("".join(json.dumps(d) + "\n" for d in diagnostics), encoding="utf-8")
    refresh_hash(development_copy, path.name)
    with pytest.raises(ValueError):
        ml.load_development(development_copy)


@pytest.mark.parametrize("mutation", ["not_ready", "wrong_features", "duplicate_input"])
def test_loader_rejects_invalid_common_contract(development_copy, mutation):
    if mutation == "not_ready":
        path = development_copy / "summary.json"
        summary = json.loads(path.read_text(encoding="utf-8"))
        summary["dataset_ready"] = False
        path.write_text(json.dumps(summary), encoding="utf-8")
    elif mutation == "wrong_features":
        path = development_copy / "generation_plan.json"
        plan = json.loads(path.read_text(encoding="utf-8"))
        plan["prediction_contract"]["features"].append("settling_after_exit_s")
        path.write_text(json.dumps(plan), encoding="utf-8")
        refresh_hash(development_copy, path.name)
    else:
        path = development_copy / "setup_manifest.csv"
        # First two training points share stiffness, so replacing damping makes
        # their coefficient pairs duplicate while retaining different IDs.
        # Use the actual next stored damping to avoid hardcoded rounding here.
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rewrite_first_csv_row(path, "cs_N_s_m", rows[1]["cs_N_s_m"])
        refresh_hash(development_copy, path.name)
    with pytest.raises(ValueError):
        ml.load_development(development_copy)


def test_existing_ml_output_is_refused_before_data_access_or_mutation(tmp_path, monkeypatch):
    sentinel = tmp_path / "keep.txt"
    sentinel.write_bytes(b"existing checkpoint")
    monkeypatch.setattr(ml, "load_development", lambda path: pytest.fail("existing output allowed data access"))
    with pytest.raises(FileExistsError):
        ml.run(tmp_path)
    assert list(tmp_path.iterdir()) == [sentinel]
    assert sentinel.read_bytes() == b"existing checkpoint"
