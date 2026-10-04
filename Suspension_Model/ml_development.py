"""Training/validation comparison for P008; never open final-test responses.

One sample is a full suspension setup. X=[ks,cs] in SI units, y=A in mm.
Course adaptations: Week05_1 metrics; Week05_3 scaler/SVR pipeline;
Week05_5 validation selection; Week05_6 leakage and fixed data roles.
Run: python ml_development.py --output ml_development_v1
"""

import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import importlib.metadata
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter
import warnings

import joblib
import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from threadpoolctl import threadpool_limits

from dataset_design import classify_summary, sha256_file, validate_setups
from quarter_car import Parameters

ROOT = Path(__file__).resolve().parent
FEATURES = ("ks_N_m", "cs_N_s_m")
LINEAR_SPEC = {"model_id": "linear", "family": "linear"}
DEVELOPMENT_FILES = ("generation_plan.json", "setup_manifest.csv", "train.csv",
                     "validation.csv", "train_diagnostics.jsonl", "validation_diagnostics.jsonl")


def write_json(path, data):
    """Write finite JSON with stable line endings; invalid numbers raise errors."""
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n",
                          encoding="utf-8", newline="\n")


def candidate_specs():
    """Return exactly P008's 18 RBF settings in its declared tie-break order."""
    return [dict(model_id=f"svr_{i:02d}", family="rbf_svr", C=c, gamma=g, epsilon=e)
            for i, (c, g, e) in enumerate(itertools.product(
                (1.0, 10.0, 100.0), (0.1, 1.0, 10.0), (0.05, 0.20)), 1)]


def metrics(y, prediction):
    """Dimensional errors, with residual = simulated A minus predicted A.

    Positive residual means underprediction. R2 is undefined (None) for a
    constant reference; extrema describe these samples, not a domain guarantee.
    """
    y, prediction = np.asarray(y, dtype=float), np.asarray(prediction, dtype=float)
    if y.ndim != 1 or y.size == 0 or y.shape != prediction.shape or not (
            np.isfinite(y).all() and np.isfinite(prediction).all()):
        raise ValueError("metrics require matching nonempty finite vectors")
    residual = y - prediction
    total = float(np.sum((y - y.mean()) ** 2))
    return {"n": int(y.size), "MAE_mm": float(np.mean(abs(residual))),
            "RMSE_mm": float(np.sqrt(np.mean(residual ** 2))),
            "max_absolute_error_mm": float(np.max(abs(residual))),
            "max_underprediction_mm": float(max(0.0, np.max(residual))),
            "mean_residual_mm": float(residual.mean()),
            "R2": float(1 - np.sum(residual ** 2) / total) if total > 0 else None}


def validate_features(X):
    """Reject malformed/out-of-domain queries; do not silently extrapolate/clip."""
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != 2 or len(X) == 0 or not np.isfinite(X).all():
        raise ValueError("features must be a nonempty finite (n,2) array in [ks,cs] order")
    if np.any(X < [18000.0, 1594.8]) or np.any(X > [30000.0, 2658.0]):
        raise ValueError("query outside the adopted coefficient domain")
    return X


def predict_checked(pipeline, X):
    """Predict mm inside the study domain, rejecting nonfinite model output."""
    X = validate_features(X)
    predicted = np.asarray(pipeline.predict(X), dtype=float)
    if predicted.shape != (len(X),) or not np.isfinite(predicted).all():
        raise ValueError("model returned invalid predictions")
    return predicted


def build_pipeline(spec):
    """Create an unfitted input-scaler/regressor pipeline; targets stay in mm."""
    if spec["family"] == "linear":
        regressor = LinearRegression(fit_intercept=True)
    elif spec["family"] == "rbf_svr":
        regressor = SVR(kernel="rbf", C=spec["C"], gamma=spec["gamma"],
                        epsilon=spec["epsilon"], tol=0.001, shrinking=True,
                        cache_size=200, max_iter=-1)
    else:
        raise ValueError("unsupported model family")
    return Pipeline([("scale", StandardScaler()), ("regressor", regressor)])


def load_development(dataset):
    """Load only verified training/validation labels and common input metadata.

    Explicit paths prevent reads of heldout_test response files. Check saved
    hashes, role identities, physics/validity and mm conversion; reject a bad
    dataset rather than dropping, imputing, rounding or reassigning rows.
    """
    dataset = Path(dataset)
    summary = json.loads((dataset / "summary.json").read_text(encoding="utf-8"))
    if summary.get("dataset_ready") is not True or summary.get("status") != "completed":
        raise ValueError("dataset is not ready")
    for name in DEVELOPMENT_FILES:
        if sha256_file(dataset / name) != summary.get("artifact_sha256", {}).get(name):
            raise ValueError(f"dataset artifact hash mismatch: {name}")
    plan = json.loads((dataset / "generation_plan.json").read_text(encoding="utf-8"))
    if (plan.get("counts") != {"train": 225, "validation": 75, "test": 100}
            or plan.get("prediction_contract", {}).get("features") != list(FEATURES)
            or plan.get("prediction_contract", {}).get("target") !=
            "A_mm = 1000 * max over full response of abs(zs-zu)"):
        raise ValueError("dataset contract differs from P007/P008")
    with (dataset / "setup_manifest.csv").open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    declared = [{"setup_id": r["setup_id"], "split": r["split"],
                 **{k: float(r[k]) for k in FEATURES}} for r in manifest]
    validate_setups(declared)
    identities = {r["setup_id"]: r for r in declared}
    data = {}
    for role, count in (("train", 225), ("validation", 75)):
        with (dataset / f"{role}.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != ["setup_id", "split", *FEATURES, "A_mm", "target_valid"]:
                raise ValueError("unexpected target table columns/order")
            rows = list(reader)
        diagnostics = [json.loads(line) for line in
                       (dataset / f"{role}_diagnostics.jsonl").read_text(encoding="utf-8").splitlines()]
        if len(rows) != count or len(diagnostics) != count:
            raise ValueError("development role count mismatch")
        X, y, ids = [], [], []
        for i, (r, d) in enumerate(zip(rows, diagnostics), 1):
            ident = f"{role}_{i:03d}"
            pair = [float(r[k]) for k in FEATURES]
            source = identities[ident]
            if (r["setup_id"] != ident or r["split"] != role
                    or pair != [source[k] for k in FEATURES]
                    or d.get("setup", {}).get("setup_id") != ident
                    or d["setup"].get("split") != role
                    or pair != [d["setup"].get(k) for k in FEATURES]
                    or d.get("parameters") != asdict(Parameters(ks=pair[0], cs=pair[1]))):
                raise ValueError("development identity, role or physical inputs disagree")
            valid = classify_summary(d.get("raw_summary") or {}, d.get("exit_state_difference"))
            if (r["target_valid"] != "True" or not valid["target_valid"]
                    or d.get("validity") != valid):
                raise ValueError("ineligible or inconsistent development target")
            target = float(r["A_mm"])
            if not np.isfinite(target) or target <= 0 or target != valid["A_mm"]:
                raise ValueError("target must be the verified full-response A in mm")
            X.append(pair)
            y.append(target)
            ids.append(ident)
        data[role] = {"ids": ids, "X": validate_features(X), "y": np.asarray(y),
                      "diagnostics": diagnostics}
    return data


def fit_candidates(train, validation):
    """Fit 19 separate pipelines on training only; return records and models.

    Record failed candidates rather than quietly selecting around a failure.
    The selection step refuses any failure until investigated. Fit time includes
    scaling; scoring time is a one-call diagnostic, not a speed benchmark.
    """
    X = validate_features(train["X"])
    Xv = validate_features(validation["X"])
    y = np.asarray(train["y"], dtype=float)
    if y.shape != (len(X),) or not np.isfinite(y).all() or np.any(y <= 0):
        raise ValueError("training targets must be finite positive mm")
    yv = np.asarray(validation["y"], dtype=float)
    if yv.shape != (len(Xv),) or not np.isfinite(yv).all() or np.any(yv <= 0):
        raise ValueError("validation targets must be finite positive mm")
    records, models = [], {}
    for spec in [LINEAR_SPEC, *candidate_specs()]:
        record = {**spec, "status": "failed"}
        started = perf_counter()
        try:
            model = build_pipeline(spec)
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                model.fit(X, y)
            record["fit_seconds"] = perf_counter() - started
            scaler, regressor = model.named_steps["scale"], model.named_steps["regressor"]
            if (int(scaler.n_samples_seen_) != len(X)
                    or not np.allclose(scaler.mean_, X.mean(axis=0), rtol=0, atol=1e-10)
                    or not np.allclose(scaler.var_, X.var(axis=0), rtol=1e-13, atol=1e-10)):
                raise RuntimeError("scaler did not use exactly the training inputs")
            before = (scaler.mean_.copy(), scaler.scale_.copy(), scaler.var_.copy())
            train_prediction = predict_checked(model, X)
            prediction_started = perf_counter()
            validation_prediction = predict_checked(model, Xv)
            record["validation_prediction_seconds_single_call"] = perf_counter() - prediction_started
            unchanged = all(np.array_equal(a, b) for a, b in
                            zip(before, (scaler.mean_, scaler.scale_, scaler.var_)))
            if not unchanged:
                raise RuntimeError("validation prediction modified preprocessing")
            if getattr(regressor, "fit_status_", 0) != 0:
                raise RuntimeError("SVR did not converge")
            record.update(status="ok", training=metrics(y, train_prediction),
                          validation=metrics(validation["y"], validation_prediction),
                          scaler_mean=scaler.mean_.tolist(), scaler_scale=scaler.scale_.tolist(),
                          scaler_training_count=int(scaler.n_samples_seen_),
                          scaler_unchanged_after_prediction=unchanged,
                          validation_predictions_positive=bool(np.all(validation_prediction > 0)),
                          support_vectors=int(regressor.n_support_[0]) if spec["family"] == "rbf_svr" else None,
                          support_fraction=float(regressor.n_support_[0] / len(X)) if spec["family"] == "rbf_svr" else None,
                          fit_status=int(getattr(regressor, "fit_status_", 0)))
            models[spec["model_id"]] = model
        except (ValueError, RuntimeError, FloatingPointError, ConvergenceWarning) as error:
            record["error"] = f"{type(error).__name__}: {error}"
            record["elapsed_seconds_until_failure"] = perf_counter() - started
        records.append(record)
    return records, models


def select_models(records):
    """Select by validation RMSE; exact ties follow the recorded P008 rule."""
    if not records or any(r.get("status") != "ok" or not np.isfinite(
            r.get("validation", {}).get("RMSE_mm", np.nan)) for r in records):
        raise ValueError("investigate failed/nonfinite candidates before selection")
    if (len({r["model_id"] for r in records}) != len(records)
            or any(r["validation"]["RMSE_mm"] < 0 for r in records)):
        raise ValueError("candidate identities or errors are invalid")
    linears = [r for r in records if r["family"] == "linear"]
    svrs = [r for r in records if r["family"] == "rbf_svr"]
    if len(linears) != 1 or not svrs:
        raise ValueError("comparison needs one linear model and SVR candidates")
    best = min(svrs, key=lambda r: (r["validation"]["RMSE_mm"], r["C"], r["gamma"], r["epsilon"]))
    linear = linears[0]
    preferred = linear if linear["validation"]["RMSE_mm"] <= best["validation"]["RMSE_mm"] else best
    return {"best_svr_id": best["model_id"], "preferred_model_id": preferred["model_id"],
            "criterion": "validation RMSE in mm; exact ties favour linear, then ascending C/gamma/epsilon",
            "best_svr_settings": {k: best[k] for k in ("C", "gamma", "epsilon")},
            "scope": "development selection only; no 300-row refit or final-test evaluation"}


def prediction_timing(model, X, repeats=30):
    """Warm up three times, then time checked whole-pipeline validation batches."""
    for _ in range(3):
        predict_checked(model, X)
    elapsed = []
    for _ in range(repeats):
        start = perf_counter()
        predict_checked(model, X)
        elapsed.append(perf_counter() - start)
    return {"batch_rows": len(X), "repeats": repeats, "warmups": 3,
            "median_batch_seconds": float(np.median(elapsed)),
            "minimum_batch_seconds": min(elapsed), "maximum_batch_seconds": max(elapsed),
            "scope": "in-memory validation batch, including input guard, scaling and regression; no I/O"}


def run(output, dataset=ROOT / "dataset_v1"):
    """Save a new development checkpoint without modifying data or test responses."""
    output, dataset = Path(output), Path(dataset)
    if output.exists():
        raise FileExistsError("preserving existing ML output; choose another --output folder")
    data = load_development(dataset)
    source_paths = [ROOT / name for name in ("ml_development.py", "ml_plots.py", "requirements-ml.txt",
                                            "dataset_design.py", "quarter_car.py")]
    source_paths += sorted((ROOT / "tests").glob("test_ml*.py"))
    source_paths += [ROOT.parent / name for name in (
        "MMA3001_2026_Project_Brief.pdf", "MMA3001_Notes_Week05_1_Linear_Regression.ipynb",
        "MMA3001_Notes_Week05_3_Support_Vector_Regression.ipynb",
        "MMA3001_Notes_Week05_5_Evaluating_Regression_Performance.ipynb",
        "MMA3001_Notes_Week05_6_Training_Data_Evaluation_and_Selection.ipynb")]
    sources = {str(p.relative_to(ROOT.parent)): sha256_file(p) for p in source_paths}
    dataset_hashes = {name: sha256_file(dataset / name) for name in ("summary.json", *DEVELOPMENT_FILES)}
    output.mkdir(parents=True)
    plan = {"created_utc": datetime.now(timezone.utc).isoformat(), "stage": "training/validation only",
            "features": list(FEATURES), "target": "A_mm; full bump and post-bump response from static equilibrium",
            "training_rows": 225, "validation_rows": 75, "heldout_response_reads": False,
            "target_scaled": False, "scaler": "StandardScaler, fit on training only per pipeline",
            "linear": LINEAR_SPEC, "svr_candidates": candidate_specs(),
            "svr_solver": {"kernel": "rbf", "tol": 0.001, "shrinking": True, "cache_size": 200, "max_iter": -1},
            "selection": "minimum validation RMSE; exact ties linear then ascending C/gamma/epsilon",
            "region_boundaries": {"ks_N_m": 24000, "cs_N_s_m": 2126.4},
            "prediction_timing": {"warmups": 3, "repeats": 30, "batch_rows": 75, "threadpool_limit": 1},
            "no_extra_tuning_or_models": True, "no_final_refit_or_test": True,
            "source_sha256": sources, "dataset_files_read_sha256": dataset_hashes,
            "environment": {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
                            "packages": {name: importlib.metadata.version(name) for name in
                                         ("numpy", "scipy", "matplotlib", "pytest", "scikit-learn", "joblib", "threadpoolctl")}}}
    write_json(output / "development_plan.json", plan)
    plan_hash = sha256_file(output / "development_plan.json")
    write_json(output / "summary.json", {"status": "running", "complete": False})
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT, capture_output=True, text=True)
    (output / "unit_tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8", newline="\n")
    if tests.returncode:
        write_json(output / "summary.json", {"status": "failed_tests", "complete": False})
        return 1
    with threadpool_limits(limits=1):
        start = perf_counter()
        records, models = fit_candidates(data["train"], data["validation"])
        fit_score_elapsed = perf_counter() - start
        write_json(output / "candidates.json", records)
        if any(r["status"] != "ok" for r in records):
            write_json(output / "summary.json", {"status": "failed_candidates", "complete": False})
            return 1
        decision = select_models(records)
        chosen = ("linear", decision["best_svr_id"])
        timing = {key: prediction_timing(models[key], data["validation"]["X"]) for key in chosen}
    write_json(output / "development_decision.json", decision)
    # Preserve both comparators at their 225-row state. Reload only files created here.
    reload_errors = {}
    for key in chosen:
        path = output / f"{key}.joblib"
        joblib.dump(models[key], path)
        loaded = joblib.load(path)
        reload_errors[key] = float(np.max(abs(predict_checked(loaded, data["validation"]["X"])
                                              - predict_checked(models[key], data["validation"]["X"]))))
        if reload_errors[key] != 0:
            raise RuntimeError("reloaded fitted pipeline changed predictions")
    columns = ["setup_id", "split", *FEATURES, "A_mm", "linear_prediction_mm", "svr_prediction_mm",
               "linear_residual_mm", "svr_residual_mm"]
    for role in ("train", "validation"):
        part = data[role]
        pl = predict_checked(models["linear"], part["X"])
        ps = predict_checked(models[decision["best_svr_id"]], part["X"])
        with (output / f"{role}_predictions.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(columns)
            for ident, x, y, l, s in zip(part["ids"], part["X"], part["y"], pl, ps):
                writer.writerow([ident, role, *x, y, l, s, y-l, y-s])
    scaler = models["linear"].named_steps["scale"]
    linear = models["linear"].named_steps["regressor"]
    coefficients = linear.coef_ / scaler.scale_
    equation = {"intercept_mm": float(linear.intercept_ - coefficients @ scaler.mean_),
                "coefficient_mm_per_N_m": float(coefficients[0]),
                "coefficient_mm_per_N_s_m": float(coefficients[1])}
    from ml_plots import create_outputs
    regional = create_outputs(output, data, records, models, decision)
    checks = {
        "all_19_candidates_converged": len(records) == 19 and all(r["fit_status"] == 0 for r in records),
        "all_scalers_training_only": all(r["scaler_training_count"] == 225 and r["scaler_unchanged_after_prediction"] for r in records),
        "all_validation_predictions_positive": all(r["validation_predictions_positive"] for r in records),
        "saved_models_reproduce_predictions": all(v == 0 for v in reload_errors.values()),
        "dataset_files_unchanged": all(sha256_file(dataset / n) == h for n, h in dataset_hashes.items()),
        "source_files_unchanged": all(sha256_file(ROOT.parent / n) == h for n, h in sources.items()),
        "predeclared_plan_unchanged": sha256_file(output / "development_plan.json") == plan_hash,
    }
    selected_records = {key: next(r for r in records if r["model_id"] == key) for key in chosen}
    result = {"status": "completed" if all(checks.values()) else "failed_checks", "complete": all(checks.values()),
              "completed_utc": datetime.now(timezone.utc).isoformat(), "checks": checks, "decision": decision,
              "comparison": selected_records, "regional_validation_metrics": regional,
              "linear_equation_original_input_units": equation, "saved_model_max_prediction_difference_mm": reload_errors,
              "target_spread_mm": {role: {"min": float(p["y"].min()), "max": float(p["y"].max()),
                                          "mean": float(p["y"].mean()), "population_std": float(p["y"].std())}
                                   for role, p in data.items()},
              "work": {"total_19_pipeline_fit_seconds": sum(r["fit_seconds"] for r in records),
                       "fit_and_score_loop_seconds": fit_score_elapsed, "prediction_timing": timing},
              "heldout_responses_opened": False, "refit_on_300_rows": False,
              "plan_sha256": plan_hash,
              "limits": ["Selected on 75 validation cases; this is not final-test accuracy.",
                         "Best within the declared 18 settings, not a globally optimal model.",
                         "Sampled errors are not domain-wide bounds or real-vehicle validation.",
                         "Pilot numerical agreement is not a certified per-label error bound.",
                         "Prediction timing excludes simulation/data-generation costs; no speedup claim."]}
    result["artifact_sha256"] = {str(p.relative_to(output)): sha256_file(p) for p in output.iterdir()
                                 if p.is_file() and p.name != "summary.json"}
    write_json(output / "summary.json", result)
    print(json.dumps({"complete": result["complete"], "checks": checks, "decision": decision,
                      "validation": {key: r["validation"] for key, r in selected_records.items()}}, indent=2))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("ml_development_v1"))
    args = parser.parse_args()
    raise SystemExit(run(args.output if args.output.is_absolute() else ROOT / args.output))
