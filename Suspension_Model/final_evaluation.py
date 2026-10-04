"""Freeze, refit on 300 development rows, then evaluate the reserved 100 once.

Commands: python final_evaluation.py prepare / evaluate / audit
Preparation writes a plan and fitted-model seal before any test-response read.
Evaluation refuses a second access within that checkpoint. An audit recomputes
saved scores without refitting or opening the original held-out response files.
"""

import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
import warnings

import joblib
import numpy as np
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits

from dataset_design import classify_summary, sha256_file
from ml_development import (ROOT, FEATURES, LINEAR_SPEC, DEVELOPMENT_FILES,
                            build_pipeline, load_development, metrics,
                            predict_checked, prediction_timing, select_models,
                            validate_features, write_json)
from quarter_car import Parameters

TEST_FILES = ("heldout_test/test.csv", "heldout_test/test_diagnostics.jsonl")
CSV_COLUMNS = ["setup_id", "split", *FEATURES, "A_mm", "target_valid"]
FINAL_SPECS = [dict(LINEAR_SPEC), {"model_id": "svr", "family": "rbf_svr", "C": 100., "gamma": 1., "epsilon": .05}]


def read_json(path):
    """Read a local UTF-8 JSON record."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def frozen_selection(development, reference):
    """Check stored development evidence and retain D009, never select on test."""
    development, reference = Path(development), Path(reference)
    summary = read_json(development / "summary.json")
    refined = read_json(reference / "summary.json")
    if summary.get("complete") is not True or refined.get("complete") is not True:
        raise ValueError("complete development and reference checks are required")
    if not summary.get("checks") or not all(v is True for v in summary["checks"].values()):
        raise ValueError("development checks did not pass")
    if not refined.get("checks") or not all(v is True for v in refined["checks"].values()):
        raise ValueError("reference checks did not pass")
    for name in ("development_decision.json", "candidates.json", "development_plan.json"):
        if sha256_file(development / name) != summary.get("artifact_sha256", {}).get(name):
            raise ValueError("development decision/score/plan fingerprint mismatch")
    for name in ("plan.json", "validation_references.jsonl"):
        if sha256_file(reference / name) != refined.get("artifact_sha256", {}).get(name):
            raise ValueError("refined-reference fingerprint mismatch")
    reference_sources = {k.replace("\\", "/"): v for k, v in
                         read_json(reference / "plan.json").get("source_sha256", {}).items()}
    required_reference_sources = {"ml_reference_check.py", "quarter_car.py", "ml_development.py",
        "tests/test_ml_reference.py", "ml_development_v1/summary.json", "ml_development_v1/candidates.json",
        "ml_development_v1/validation_predictions.csv", "dataset_v1/validation.csv",
        "dataset_v1/validation_diagnostics.jsonl"}
    if set(reference_sources) != required_reference_sources or any(
            sha256_file(ROOT / name) != digest for name, digest in reference_sources.items()):
        raise ValueError("reference evidence is not bound to the current development checkpoint")
    decision = read_json(development / "development_decision.json")
    records = read_json(development / "candidates.json")
    if len(records) != 19 or select_models(records) != decision or summary.get("decision") != decision:
        raise ValueError("saved decision disagrees with development scores")
    if (decision["best_svr_id"] != "svr_15" or decision["preferred_model_id"] != "svr_15"
            or decision["best_svr_settings"] != {"C": 100.0, "gamma": 1.0, "epsilon": .05}):
        raise ValueError("development choice differs from the recorded D009 freeze")
    plan = read_json(development / "development_plan.json")
    for name in ("python",):
        if plan["environment"][name] != sys.version:
            raise ValueError("Python environment differs from development")
    for name in ("numpy", "scipy", "scikit-learn", "joblib", "threadpoolctl"):
        if plan["environment"]["packages"].get(name) != importlib.metadata.version(name):
            raise ValueError("numerical/ML environment differs from development")
    return {"preferred_model": "svr", "selected_development_id": "svr_15",
            "specs": [dict(LINEAR_SPEC), {"model_id": "svr", "family": "rbf_svr", **decision["best_svr_settings"]}],
            "basis": "D009 validation selection, confirmed against tighter validation scoring references"}


def combined_development(data):
    """Concatenate original training then original validation; no refined labels."""
    for role, count in (("train", 225), ("validation", 75)):
        part = data[role]
        if len(part["ids"]) != count or part["ids"] != [f"{role}_{i:03d}" for i in range(1, count+1)]:
            raise ValueError("development row identities/counts changed")
        if np.asarray(part["X"]).shape != (count, 2) or np.asarray(part["y"]).shape != (count,):
            raise ValueError("development array shapes changed")
    X = validate_features(np.vstack([data["train"]["X"], data["validation"]["X"]]))
    y = np.concatenate([data["train"]["y"], data["validation"]["y"]]).astype(float)
    if not np.isfinite(y).all() or np.any(y <= 0) or len({tuple(x) for x in X}) != 300:
        raise ValueError("development targets or unique coefficient pairs are invalid")
    return X, y, data["train"]["ids"] + data["validation"]["ids"]


def refit_models(data, specs):
    """Fit only two new scaler/regressor pipelines on all 300 original labels."""
    if specs != FINAL_SPECS:
        raise ValueError("final refit must use the frozen two comparators")
    X, y, _ = combined_development(data)
    models, records = {}, {}
    for spec in specs:
        model = build_pipeline(spec)
        start = perf_counter()
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            model.fit(X, y)
        elapsed = perf_counter() - start
        scaler, reg = model.named_steps["scale"], model.named_steps["regressor"]
        if (int(scaler.n_samples_seen_) != 300 or getattr(reg, "fit_status_", 0) != 0
                or not np.allclose(scaler.mean_, X.mean(axis=0), rtol=0, atol=1e-10)
                or not np.allclose(scaler.var_, X.var(axis=0), rtol=1e-13, atol=1e-10)):
            raise RuntimeError("final fit/convergence/scaler check failed")
        models[spec["model_id"]] = model
        records[spec["model_id"]] = {"spec": spec, "training_count": 300, "fit_seconds": elapsed,
                "fit_status": int(getattr(reg, "fit_status_", 0)), "scaler_mean": scaler.mean_.tolist(),
                "scaler_scale": scaler.scale_.tolist(), "scaler_variance": scaler.var_.tolist(),
                "development_fit_metrics": metrics(y, predict_checked(model, X)),
                "support_vectors": int(reg.n_support_[0]) if spec["family"] == "rbf_svr" else None}
    return models, records


def verify_seal(checkpoint):
    """Validate the saved pre-test plan, fitted models and source/data identities."""
    checkpoint = Path(checkpoint)
    plan = read_json(checkpoint / "frozen_plan.json")
    refit = read_json(checkpoint / "refit.json")
    selection = plan.get("selection", {})
    if (selection.get("specs") != FINAL_SPECS or selection.get("selected_development_id") != "svr_15"
            or selection.get("preferred_model") != "svr" or plan.get("features") != list(FEATURES)
            or plan.get("refit_rows") != 300 or plan.get("test_rows") != 100
            or not plan.get("source_sha256") or not plan.get("pretest_input_sha256")
            or set(plan.get("expected_test_sha256", {})) != set(TEST_FILES)
            or any("heldout_test" in name.replace("\\", "/").split("/")
                   for name in plan["pretest_input_sha256"])):
        raise ValueError("incomplete or changed frozen plan contract")
    if (refit.get("stage") != "models_frozen" or refit.get("training_count") != 300
            or refit.get("plan_sha256") != sha256_file(checkpoint / "frozen_plan.json")
            or refit.get("model_ids") != ["linear", "svr"]
            or plan.get("selection", {}).get("preferred_model") != "svr"):
        raise ValueError("a matching frozen plan and completed 300-row refit are required")
    if any(refit.get("fits", {}).get(k, {}).get("training_count") != 300
           or refit["fits"][k].get("fit_status") != 0
           or refit["fits"][k].get("spec") != spec
           for k, spec in zip(("linear", "svr"), FINAL_SPECS)):
        raise ValueError("invalid refit counts/status/specification")
    for key in ("linear", "svr"):
        if sha256_file(checkpoint / f"{key}.joblib") != refit.get("model_sha256", {}).get(key):
            raise ValueError("frozen model bytes changed")
    for name, digest in plan["source_sha256"].items():
        if sha256_file(ROOT.parent / name) != digest:
            raise ValueError("source changed after final plan was frozen")
    # This list contains only common/development inputs, never test responses.
    for name, digest in plan["pretest_input_sha256"].items():
        if sha256_file(ROOT / name) != digest:
            raise ValueError("development input changed after final plan was frozen")
    return plan, refit


def validate_test_rows(rows, diagnostics, manifest):
    """Check all 100 frozen test identities, SI features, mm targets and flags."""
    if len(rows) != 100 or len(diagnostics) != 100:
        raise ValueError("exactly 100 test rows and diagnostics are required")
    declared = {r["setup_id"]: r for r in manifest if r["split"] == "test"}
    if len(declared) != 100:
        raise ValueError("test manifest has wrong identities/count")
    X, y, ids = [], [], []
    for i, (row, diag) in enumerate(zip(rows, diagnostics), 1):
        ident = f"test_{i:03d}"
        if set(row) != set(CSV_COLUMNS) or row["setup_id"] != ident or row["split"] != "test":
            raise ValueError("test identity, order, role or feature schema mismatch")
        pair = [float(row[k]) for k in FEATURES]
        source = declared.get(ident)
        if source is None or pair != [float(source[k]) for k in FEATURES]:
            raise ValueError("test coefficients differ from frozen manifest")
        if (diag.get("setup", {}).get("setup_id") != ident or diag["setup"].get("split") != "test"
                or pair != [diag["setup"].get(k) for k in FEATURES]
                or diag.get("parameters") != asdict(Parameters(ks=pair[0], cs=pair[1]))):
            raise ValueError("test diagnostic identity or physical parameters disagree")
        validity = classify_summary(diag.get("raw_summary") or {}, diag.get("exit_state_difference"))
        if row["target_valid"] != "True" or not validity["target_valid"] or diag.get("validity") != validity:
            raise ValueError("ineligible or inconsistent test target; do not drop a row")
        target = float(row["A_mm"])
        if not np.isfinite(target) or target <= 0 or target != validity["A_mm"]:
            raise ValueError("test target is not the saved full-response A in mm")
        ids.append(ident)
        X.append(pair)
        y.append(target)
    if len({tuple(x) for x in X}) != 100:
        raise ValueError("duplicate test coefficient pairs")
    return {"ids": ids, "X": validate_features(X), "y": np.asarray(y), "diagnostics": diagnostics}


def load_heldout(dataset, checkpoint):
    """Read test responses only after verifying a completed frozen refit."""
    plan, _ = verify_seal(checkpoint)
    dataset = Path(dataset)
    for name in TEST_FILES:
        if sha256_file(dataset / name) != plan["expected_test_sha256"][name]:
            raise ValueError("reserved test file differs from predeclared fingerprint")
    with (dataset / TEST_FILES[0]).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CSV_COLUMNS:
            raise ValueError("test target table has unexpected columns/order")
        rows = list(reader)
    diagnostics = [json.loads(line) for line in (dataset / TEST_FILES[1]).read_text(encoding="utf-8").splitlines()]
    with (dataset / "setup_manifest.csv").open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    return validate_test_rows(rows, diagnostics, manifest)


def prepare(output):
    """Save final choices, test the implementation and refit, without test access."""
    output = Path(output)
    if output.exists():
        raise FileExistsError("preserving existing checkpoint; use another output name for reproduction")
    selection = frozen_selection(ROOT / "ml_development_v1", ROOT / "ml_reference_v1")
    data = load_development(ROOT / "dataset_v1")
    X, y, ids = combined_development(data)
    summary = read_json(ROOT / "dataset_v1/summary.json")
    expected = {k.replace("\\", "/"): v for k, v in summary["artifact_sha256"].items()}
    paths = sorted(ROOT.glob("*.py")) + sorted((ROOT / "tests").glob("*.py"))
    paths += [ROOT / "requirements-ml.txt", ROOT / "requirements.txt"]
    paths += [ROOT.parent / n for n in ("MMA3001_2026_Project_Brief.pdf",
        "MMA3001_Notes_Week05_5_Evaluating_Regression_Performance.ipynb",
        "MMA3001_Notes_Week05_6_Training_Data_Evaluation_and_Selection.ipynb")]
    inputs = [ROOT / "dataset_v1" / n for n in ("summary.json", *DEVELOPMENT_FILES)]
    inputs += [ROOT / "ml_development_v1" / n for n in ("summary.json", "development_decision.json",
                                                       "candidates.json", "development_plan.json")]
    inputs += [ROOT / "ml_reference_v1" / n for n in ("summary.json", "plan.json", "validation_references.jsonl")]
    plan = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "selection": selection,
            "features": list(FEATURES), "target": "A_mm = 1000*max(abs(zs-zu)) over full bump and post-bump response",
            "refit_rows": 300, "test_rows": 100, "development_ids": ids,
            "refit_labels": "original dataset_v1 train then validation; refined validation labels are verification only",
            "scaling": "fresh StandardScaler on 300 development rows, targets remain mm",
            "svr_solver": {"tol": .001, "shrinking": True, "cache_size": 200, "max_iter": -1},
            "metrics": ["MAE_mm", "RMSE_mm", "max_absolute_error_mm", "max_underprediction_mm", "mean_residual_mm", "R2"],
            "residual": "simulated A minus predicted A; positive means underprediction",
            "regions": {"stiffness_split_N_m": 24000, "damping_split_N_s_m": 2126.4},
            "test_use": "score the two frozen refits on the same 100 cases; report without retuning or changing preference",
            "accuracy_threshold": None, "new_simulations_or_reference_changes": False,
            "source_sha256": {str(p.relative_to(ROOT.parent)): sha256_file(p) for p in paths},
            "pretest_input_sha256": {str(p.relative_to(ROOT)): sha256_file(p) for p in inputs},
            "expected_test_sha256": {n: expected[n] for n in TEST_FILES},
            "environment": {"python": sys.version, "executable": sys.executable,
                "packages": {n: importlib.metadata.version(n) for n in
                    ("numpy", "scipy", "scikit-learn", "joblib", "threadpoolctl", "matplotlib", "pytest")}},
            "timing": "two refits plus 30 warmed 300-row development prediction batches at one numerical thread; no total speedup claim"}
    output.mkdir(parents=True)
    write_json(output / "frozen_plan.json", plan)
    write_json(output / "summary.json", {"stage": "preparing", "complete": False, "test_opened": False})
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT, capture_output=True, text=True)
    (output / "unit_tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8", newline="\n")
    if tests.returncode:
        write_json(output / "summary.json", {"stage": "failed_tests", "complete": False, "test_opened": False})
        return 1
    with threadpool_limits(limits=1):
        models, fits = refit_models(data, selection["specs"])
        timing = {k: prediction_timing(m, X) for k, m in models.items()}
    model_hashes, reload_errors = {}, {}
    for key, model in models.items():
        path = output / f"{key}.joblib"
        joblib.dump(model, path)
        reload_errors[key] = float(np.max(abs(predict_checked(joblib.load(path), X)-predict_checked(model, X))))
        if reload_errors[key] != 0:
            raise RuntimeError("saved refit does not reproduce development predictions")
        model_hashes[key] = sha256_file(path)
    write_json(output / "refit.json", {"stage": "models_frozen", "refit_finished_utc": datetime.now(timezone.utc).isoformat(),
                "training_count": 300, "model_ids": ["linear", "svr"], "fits": fits,
                "model_sha256": model_hashes, "plan_sha256": sha256_file(output / "frozen_plan.json"),
                "reload_max_difference_mm": reload_errors, "prediction_timing_on_development": timing})
    verify_seal(output)
    write_json(output / "summary.json", {"stage": "prepared", "complete": False, "test_opened": False,
                                        "message": "plan and both 300-row refits frozen; ready for one final evaluation"})
    print("Prepared two frozen 300-row refits. Reserved responses have not been read.")
    return 0


def evaluate(output):
    """Open the reserved responses once for this checkpoint and report both models."""
    output = Path(output)
    if (output / "test_access.json").exists():
        raise FileExistsError("test access already recorded; audit saved results instead of rerunning evaluation")
    plan, refit = verify_seal(output)
    models = {k: joblib.load(output / f"{k}.joblib") for k in ("linear", "svr")}
    # Preserve the first access time even if validation subsequently fails.
    write_json(output / "test_access.json", {"first_access_started_utc": datetime.now(timezone.utc).isoformat(),
                "frozen_plan_sha256": refit["plan_sha256"], "frozen_model_sha256": refit["model_sha256"],
                "purpose": "one final comparison; no later test-driven tuning"})
    test = load_heldout(ROOT / "dataset_v1", output)
    predictions = {k: predict_checked(m, test["X"]) for k, m in models.items()}
    scores = {k: metrics(test["y"], p) for k, p in predictions.items()}
    unchanged = all(int(m.named_steps["scale"].n_samples_seen_) == 300 and
        np.array_equal(m.named_steps["scale"].mean_, refit["fits"][k]["scaler_mean"]) and
        np.array_equal(m.named_steps["scale"].scale_, refit["fits"][k]["scaler_scale"])
        for k, m in models.items())
    with (output / "test_predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["setup_id", *FEATURES, "A_mm", "linear_prediction_mm", "svr_prediction_mm", "linear_residual_mm", "svr_residual_mm"])
        for i, x, y, l, s in zip(test["ids"], test["X"], test["y"], predictions["linear"], predictions["svr"]):
            writer.writerow([i, *x, y, l, s, y-l, y-s])
    regional = {}
    for key, p in predictions.items():
        regional[key] = {}
        for lowk, lowc in ((True, True), (True, False), (False, True), (False, False)):
            mask = ((test["X"][:, 0] < 24000) if lowk else (test["X"][:, 0] >= 24000)) & (
                    (test["X"][:, 1] < 2126.4) if lowc else (test["X"][:, 1] >= 2126.4))
            name = f"ks_{'lower' if lowk else 'upper'}_cs_{'lower' if lowc else 'upper'}"
            regional[key][name] = metrics(test["y"][mask], p[mask]) if mask.any() else {"n": 0}
    verify_seal(output)
    checks = {"all_100_rows_valid_and_matched": len(test["ids"]) == 100,
              "scalers_unchanged_after_test": bool(unchanged),
              "predictions_finite": all(np.isfinite(p).all() for p in predictions.values()),
              "predictions_positive_on_test": all(bool(np.all(p > 0)) for p in predictions.values()),
              "frozen_sources_inputs_models_unchanged": True}
    checks = {k: bool(v) for k, v in checks.items()}
    result = {"stage": "evaluated", "complete": all(checks.values()), "evaluated_utc": datetime.now(timezone.utc).isoformat(),
              "preferred_from_development": plan["selection"]["preferred_model"],
              "preference_changed_after_test": False, "refit_rows": 300, "test_rows": 100,
              "test_metrics": scores, "regional_test_metrics": regional, "checks": checks,
              "test_target_spread_mm": {"min": float(test["y"].min()), "max": float(test["y"].max()),
                    "mean": float(test["y"].mean()), "population_std": float(test["y"].std())},
              "test_files_sha256": plan["expected_test_sha256"], "refit": refit,
              "limits": ["Final test now consumed; do not tune against these results and call it a new independent test.",
                    "Errors are relative to simulated labels, not real-vehicle measurements.",
                    "Observed maxima are not guarantees for every point in the continuous parameter domain.",
                    "No new numerical refinement, data generation or speedup claim in this stage."]}
    from final_plots import create_outputs
    create_outputs(output, test, predictions, result)
    result["artifact_sha256"] = {p.name: sha256_file(p) for p in output.iterdir() if p.is_file() and p.name != "summary.json"}
    write_json(output / "summary.json", result)
    print(json.dumps({"complete": result["complete"], "checks": checks, "test_metrics": scores}, indent=2))
    return 0 if result["complete"] else 1


def audit(output):
    """Recompute saved final scores and hashes, without refitting or new test access."""
    output = Path(output)
    summary = read_json(output / "summary.json")
    if summary.get("complete") is not True or summary.get("stage") != "evaluated":
        raise ValueError("no complete final evaluation to audit")
    verify_seal(output)
    for name, digest in summary["artifact_sha256"].items():
        if sha256_file(output / name) != digest:
            raise ValueError("saved final artifact fingerprint changed")
    with (output / "test_predictions.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 100 or [r["setup_id"] for r in rows] != [f"test_{i:03d}" for i in range(1, 101)]:
        raise ValueError("saved test identities changed")
    for key in ("linear", "svr"):
        calculated = metrics([float(r["A_mm"]) for r in rows], [float(r[f"{key}_prediction_mm"]) for r in rows])
        if calculated != summary["test_metrics"][key]:
            raise ValueError("saved test metrics do not reproduce")
    print("Audit passed: fixed artifacts and all saved final metrics reproduce; no refit or new test read.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "evaluate", "audit"))
    parser.add_argument("--output", type=Path, default=Path("final_evaluation_v1"))
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    raise SystemExit({"prepare": prepare, "evaluate": evaluate, "audit": audit}[args.action](destination))
