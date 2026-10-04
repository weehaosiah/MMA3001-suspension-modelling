"""Check development selection against tighter validation simulations only.

P008 requests closer numerical checks for small ML differences. Preserve the
original dataset and fitted models. No held-out response files are opened.
"""

import argparse
import csv
from dataclasses import asdict
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from dataset_design import sha256_file
from ml_development import ROOT, load_development, metrics, select_models, write_json
from quarter_car import Bump, Parameters, SolverSettings, simulate, summarise


def ranking_check(records, baseline, refined):
    """Bound score changes under replacement of the numerical reference.

    For fixed prediction vectors, reverse triangle inequality gives
    |RMSE(old)-RMSE(new)| <= RMS(new_label-old_label). A strict gap above twice
    this value preserves the winner between these two numerical references.
    This does not bound error against an exact physical solution.
    """
    baseline, refined = np.asarray(baseline, dtype=float), np.asarray(refined, dtype=float)
    if baseline.ndim != 1 or baseline.size == 0 or baseline.shape != refined.shape or not (
            np.isfinite(baseline).all() and np.isfinite(refined).all()):
        raise ValueError("reference targets must be matching nonempty finite vectors")
    select_models(records)  # Enforce valid scores before using the ranking argument.
    delta = refined - baseline
    bound = float(np.sqrt(np.mean(delta ** 2)))
    scores = sorted(r["validation"]["RMSE_mm"] for r in records)
    svr_scores = sorted(r["validation"]["RMSE_mm"] for r in records if r["family"] == "rbf_svr")
    if len(svr_scores) < 2:
        raise ValueError("need at least two SVR candidates to check their separation")
    best_gap, overall_gap = float(svr_scores[1]-svr_scores[0]), float(scores[1]-scores[0])
    return {"label_change_rms_mm": bound, "label_change_max_mm": float(np.max(abs(delta))),
            "best_svr_gap_mm": best_gap, "preferred_gap_mm": overall_gap,
            "best_svr_stable": bool(best_gap > 2*bound),
            "preferred_stable": bool(overall_gap > 2*bound),
            "basis": "fixed predictions; strict original score gap > 2*RMS reference-label change"}


def reference_checks(raw, continuity, base):
    """Return the adopted physical/numerical checks for a 10 s tight reference."""
    keys = ("A_m", "A_post_m", "tail_bound_m", "minimum_contact_N",
            "maximum_energy_increase_J", "energy_increase_allowance_J", "post_bump_energy_start_J")
    finite = all(isinstance(raw.get(k), (int, float)) and np.isfinite(raw[k]) for k in keys)
    peak_ok = finite and 0 < raw["A_post_m"] <= raw["A_m"]
    tail_ok = bool(peak_ok and raw.get("tail_pass") and 0 <= raw["tail_bound_m"] <
                   min(0.0005, raw["A_m"]/2, raw["A_post_m"]/2))
    energy_ok = bool(finite and raw.get("energy_pass") and raw["post_bump_energy_start_J"] >= 0
                     and raw["energy_increase_allowance_J"] == 1e-10*max(1, raw["post_bump_energy_start_J"])
                     and 0 <= raw["maximum_energy_increase_J"] <= raw["energy_increase_allowance_J"])
    times = (raw.get("settling_after_exit_s"), base.get("settling_after_exit_s"))
    settling = (raw.get("settling_status") == "candidate" and base.get("settling_status") == "candidate"
                and all(isinstance(v, (int, float)) and np.isfinite(v) and v >= 0 for v in times))
    return {"finite_complete": bool(finite and raw.get("solver_success") and raw.get("finite_states")),
            "reference_settings": raw.get("end_time_s") == 10 and raw.get("observation_dt_s") == .00025
                                  and raw.get("band_m") == .001 and raw.get("confirmation_s") == 1,
            "full_state_continuity": isinstance(continuity, (int, float)) and np.isfinite(continuity) and continuity == 0,
            "contact": bool(finite and raw["minimum_contact_N"] > 1),
            "tail": tail_ok, "energy": energy_ok,
            "primary_peak_agreement": bool(peak_ok and abs(raw["A_m"]-base["A_m"]) <= .00005),
            "post_peak_agreement": bool(peak_ok and abs(raw["A_post_m"]-base["A_post_m"]) <= .00005),
            "settling_agreement": bool(settling and abs(times[0]-times[1]) <= .01)}


def run(output):
    """Generate a new supplementary reference check; never replace original data."""
    output = Path(output)
    if output.exists():
        raise FileExistsError("preserving existing reference check; use a new output folder")
    data = load_development(ROOT / "dataset_v1")["validation"]
    ml = ROOT / "ml_development_v1"
    summary = json.loads((ml / "summary.json").read_text(encoding="utf-8"))
    if summary.get("complete") is not True:
        raise ValueError("development run must be complete")
    for name in ("candidates.json", "validation_predictions.csv"):
        if sha256_file(ml / name) != summary["artifact_sha256"][name]:
            raise ValueError("saved development predictions/scores changed")
    records = json.loads((ml / "candidates.json").read_text(encoding="utf-8"))
    with (ml / "validation_predictions.csv").open(newline="", encoding="utf-8") as handle:
        predictions = list(csv.DictReader(handle))
    if len(predictions) != 75 or any(r["setup_id"] != i or float(r["A_mm"]) != y
                                    for r, i, y in zip(predictions, data["ids"], data["y"])):
        raise ValueError("prediction identity/reference mismatch")
    settings = SolverSettings(rtol=1e-8, atol=(1e-11, 1e-10, 1e-11, 1e-10), max_step_s=.0025)
    sources = [Path(__file__), ROOT / "quarter_car.py", ROOT / "ml_development.py",
               ROOT / "tests/test_ml_reference.py", ml / "summary.json", ml / "candidates.json",
               ml / "validation_predictions.csv", ROOT / "dataset_v1/validation.csv",
               ROOT / "dataset_v1/validation_diagnostics.jsonl"]
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    output.mkdir(parents=True)
    write_json(output / "plan.json", {"purpose": "P008 close-score numerical-reference sensitivity",
                "validation_rows": 75, "solver": asdict(settings), "horizon_s": 10, "observation_dt_s": .00025,
                "physical_model": asdict(Parameters()), "bump": asdict(Bump()), "initial_state": [0]*4,
                "source_sha256": hashes, "environment": {"python": sys.version, "executable": sys.executable,
                     "packages": {n: version(n) for n in ("numpy", "scipy", "scikit-learn", "pytest")}},
                "new_training_or_tuning": False, "heldout_responses_read": False,
                "comparison_limits": {"peak_mm": .05, "settling_s": .01},
                "ranking_rule": "fixed-prediction RMSE change <= RMS reference-label change; strict gap > twice bound"})
    plan_hash = sha256_file(output / "plan.json")
    write_json(output / "summary.json", {"complete": False, "status": "running"})
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT, capture_output=True, text=True)
    (output / "unit_tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8", newline="\n")
    if tests.returncode:
        write_json(output / "summary.json", {"complete": False, "status": "failed_tests"})
        return 1
    results = []
    with (output / "validation_references.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for ident, x, base in zip(data["ids"], data["X"], data["diagnostics"]):
            trajectory = simulate(Parameters(ks=x[0], cs=x[1]), Bump(), 10, settings)
            raw = summarise(trajectory, .00025)
            continuity = float(np.max(abs(trajectory.segments[0].y[:, -1]-trajectory.segments[1].y[:, 0])))
            checks = reference_checks(raw, continuity, base["raw_summary"])
            row = {"setup_id": ident, "ks_N_m": float(x[0]), "cs_N_s_m": float(x[1]),
                   "raw_summary": raw, "checks": checks,
                   "A_change_mm": float((raw["A_m"]-base["raw_summary"]["A_m"])*1000),
                   "A_post_change_mm": float((raw["A_post_m"]-base["raw_summary"]["A_post_m"])*1000),
                   "settling_change_s": (float(raw["settling_after_exit_s"]-base["raw_summary"]["settling_after_exit_s"])
                                         if checks["settling_agreement"] else None)}
            # Python's bool is JSON serializable; numpy.bool_ is not.
            row["checks"] = {k: bool(v) for k, v in checks.items()}
            handle.write(json.dumps(row, allow_nan=False) + "\n")
            handle.flush()
            results.append(row)
            if len(results) % 15 == 0:
                print(f"Refined validation references: {len(results)}/75", flush=True)
    refined = np.array([r["raw_summary"]["A_m"]*1000 for r in results])
    ranking = ranking_check(records, data["y"], refined)
    checks = {"all_75_reference_checks": all(all(r["checks"].values()) for r in results),
              "ranking_preserved_between_references": ranking["best_svr_stable"] and ranking["preferred_stable"],
              "sources_unchanged": all(sha256_file(ROOT / n) == h for n, h in hashes.items()),
              "plan_unchanged": sha256_file(output / "plan.json") == plan_hash}
    refined_metrics = {name: metrics(refined, [float(r[f"{name}_prediction_mm"]) for r in predictions])
                       for name in ("linear", "svr")}
    result = {"complete": all(checks.values()), "checks": checks, "ranking": ranking,
              "refined_reference_metrics": refined_metrics,
              "maximum_post_peak_change_mm": max(abs(r["A_post_change_mm"]) for r in results),
              "maximum_settling_change_s": (max(abs(r["settling_change_s"]) for r in results)
                                             if all(r["settling_change_s"] is not None for r in results) else None),
              "minimum_sampled_contact_N": min(r["raw_summary"]["minimum_contact_N"] for r in results),
              "maximum_tail_bound_mm": 1000*max(r["raw_summary"]["tail_bound_m"] for r in results),
              "verification_integrations_not_new_dataset_rows": 75,
              "summed_integration_seconds": sum(r["raw_summary"]["integration_runtime_s"] for r in results),
              "derivative_evaluations": sum(r["raw_summary"]["derivative_evaluations"] for r in results),
              "heldout_responses_read": False, "models_retrained": False,
              "limits": "Agreement of approximate references is not a certified continuous-time/real-vehicle error bound.",
              "artifact_sha256": {p.name: sha256_file(p) for p in output.iterdir() if p.name != "summary.json"}}
    write_json(output / "summary.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("ml_reference_v1"))
    args = parser.parse_args()
    raise SystemExit(run(args.output if args.output.is_absolute() else ROOT / args.output))
