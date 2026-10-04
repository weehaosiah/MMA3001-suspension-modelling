"""Generate the declared 225/75/100 simulation dataset, without any ML fitting.

Run once with: python generate_dataset.py
For an independent rerun: python generate_dataset.py --output dataset_recheck
An existing output directory is never overwritten. Failed rows remain present.
Final-test response files stay in heldout_test/; common outputs reveal only its
inputs and predeclared validity checks, never response distributions or scores.
"""

import argparse
from collections import Counter
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
import csv
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

import numpy as np

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dataset_design import (BAND_M, CONFIRMATION_S, CONTACT_MARGIN_N, COUNTS,
                            CS_RANGE, HORIZON_S, KS_RANGE, OBSERVATION_DT_S, SEEDS,
                            classify_summary, load_verified_pilots, make_setups,
                            safe_json, sha256_file, validate_setups)
from quarter_car import Bump, Parameters, SolverSettings, simulate, summarise


TARGET_COLUMNS = ("setup_id", "split", "ks_N_m", "cs_N_s_m", "A_mm", "target_valid")
MANIFEST_COLUMNS = ("setup_id", "split", "ks_N_m", "cs_N_s_m", "sampling", "seed", "pilot_id")


def write_json(path, payload):
    """Save strict JSON, converting nonfinite diagnostics to null in failure data."""
    Path(path).write_text(json.dumps(safe_json(payload), indent=2, allow_nan=False) + "\n",
                          encoding="utf-8", newline="\n")


def frozen_manifests_unchanged(output, initial_hashes):
    """Check saved plan/setup bytes against their identities from before simulation."""
    return all(sha256_file(Path(output) / name) == digest for name, digest in initial_hashes.items())


def input_coverage_plot(rows, output):
    """Plot only coefficient inputs for the three roles, never test responses."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharex=True, sharey=True, layout="constrained")
    for ax, (split, count), color in zip(axes, COUNTS.items(), ("#176b9b", "#c55c25", "#665091")):
        points = [row for row in rows if row["split"] == split]
        ax.scatter([p["ks_N_m"] / 1000 for p in points], [p["cs_N_s_m"] for p in points],
                   s=15, color=color, alpha=0.8)
        ax.set(title=f"{split.capitalize()}: {count} setups", xlabel="Stiffness [kN/m]")
        ax.grid(alpha=0.15)
    axes[0].set_ylabel("Damping [N s/m]")
    fig.suptitle("Frozen dataset inputs | one point = one full suspension simulation", fontsize=13)
    fig.savefig(output / "input_coverage.png", dpi=140)
    plt.close(fig)


def row_result(setup, cached=None):
    """Return one complete diagnostic record plus safe ML export fields.

    Reuse is allowed only for training and a matching already-verified pilot.
    New integrations use D005 settings. Numerical exceptions become preserved
    failed rows; unresolved settling alone does not prevent a valid primary A.
    """
    if cached is not None and setup["split"] != "train":
        raise ValueError("pilot reuse is restricted to training rows")
    parameters = Parameters(ks=setup["ks_N_m"], cs=setup["cs_N_s_m"])
    if cached is not None and cached.get("parameters") != asdict(parameters):
        raise ValueError("cached pilot parameters do not match this setup")
    origin = "verified_pilot_baseline" if cached is not None else "new_integration"
    summary, error, continuity = None, None, None
    new_runtime, new_nfev = 0.0, 0
    new_solver_completed = False
    row_started = perf_counter()
    try:
        if cached is not None:
            summary = dict(cached["summary"])
            continuity = cached["continuity_error"]
        else:
            trajectory = simulate(parameters, Bump(), HORIZON_S, SolverSettings())
            new_solver_completed = True
            new_runtime, new_nfev = trajectory.elapsed_s, trajectory.nfev
            continuity = float(np.max(abs(trajectory.segments[0].y[:, -1]
                                          - trajectory.segments[1].y[:, 0])))
            summary = summarise(trajectory, OBSERVATION_DT_S, BAND_M, CONFIRMATION_S)
        validity = classify_summary(summary, continuity)
    except (ValueError, RuntimeError, FloatingPointError) as exception:
        error = f"{type(exception).__name__}: {exception}"
        if cached is None and not new_solver_completed:
            new_runtime, new_nfev = None, None  # Unknown failed-solver work is not zero.
        validity = {"numerical_primary_valid": False, "contact_consistent": False,
                    "target_valid": False, "A_mm": None, "settling_status": "unresolved",
                    "settling_after_exit_s": None, "failure_reasons": ["simulation_or_diagnostic_exception"],
                    "resolution_basis": "no valid numerical output"}
    diagnostic = {"setup": setup, "parameters": asdict(parameters), "origin": origin,
                  "pilot_id": cached["pilot_id"] if cached else None,
                  "pilot_artifact_sha256": cached["source_sha256"] if cached else None,
                  "raw_summary": summary, "exit_state_difference": continuity,
                  "validity": validity, "exception": error,
                  "new_solver_completed": new_solver_completed,
                  "row_processing_runtime_s": perf_counter() - row_started,
                  "new_integration_runtime_s": new_runtime,
                  "new_derivative_evaluations": new_nfev,
                  "original_pilot_integration_runtime_s": summary["integration_runtime_s"] if cached else None}
    exported = {key: setup[key] for key in ("setup_id", "split", "ks_N_m", "cs_N_s_m")}
    exported.update(A_mm=validity["A_mm"], target_valid=validity["target_valid"])
    return diagnostic, exported


def audit_exports(output, expected_rows):
    """Check saved row identities, round-trip inputs and target validity/units.

    All roles are checked mechanically. Only counts/check outcomes are returned;
    held-out target values or descriptive response statistics are not exposed.
    Raises ValueError for mismatches or a missing/nonfinite eligible label.
    """
    result = {}
    expected = {row["setup_id"]: row for row in expected_rows}
    all_ids = set()
    for split, count in COUNTS.items():
        folder = output / "heldout_test" if split == "test" else output
        with (folder / f"{split}.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        with (folder / f"{split}_diagnostics.jsonl").open(encoding="utf-8") as handle:
            diagnostics = [json.loads(line) for line in handle]
        if len(rows) != count or len(diagnostics) != count:
            raise ValueError("saved split row count mismatch")
        valid_count = 0
        for row, diagnostic in zip(rows, diagnostics):
            if row.get("setup_id") not in expected:
                raise ValueError("saved setup identity was not declared")
            source = expected[row["setup_id"]]
            if (row["setup_id"] in all_ids or row["split"] != split or source["split"] != split
                    or diagnostic["setup"] != source
                    or float(row["ks_N_m"]) != source["ks_N_m"]
                    or float(row["cs_N_s_m"]) != source["cs_N_s_m"]):
                raise ValueError("saved identity/split/input mismatch")
            if diagnostic.get("parameters") != asdict(Parameters(ks=source["ks_N_m"], cs=source["cs_N_s_m"])):
                raise ValueError("saved physical parameters differ from manifest")
            recalculated = classify_summary(diagnostic.get("raw_summary") or {}, diagnostic.get("exit_state_difference"))
            for key in ("numerical_primary_valid", "contact_consistent", "target_valid", "A_mm",
                        "settling_status", "settling_after_exit_s"):
                if diagnostic["validity"].get(key) != recalculated[key]:
                    raise ValueError("saved validity disagrees with raw numerical/physical checks")
            all_ids.add(row["setup_id"])
            valid = diagnostic["validity"]["target_valid"]
            if row["target_valid"] != str(valid):
                raise ValueError("saved validity flag mismatch")
            if valid:
                target = float(row["A_mm"])
                if (not np.isfinite(target) or target <= 0
                        or target != diagnostic["raw_summary"]["A_m"] * 1000):
                    raise ValueError("saved target is nonfinite, nonpositive or has wrong units")
                valid_count += 1
            elif row["A_mm"] != "":
                raise ValueError("failed row must retain its identity with an empty ML target")
        result[split] = {"rows": count, "eligible_targets": valid_count,
                         "failed_targets": count - valid_count,
                         "identity_and_units_pass": True}
    if len(all_ids) != sum(COUNTS.values()):
        raise ValueError("incomplete exported identities")
    return result


def generate(output):
    """Create a new versioned dataset directory; return zero only when ready.

    Existing output raises FileExistsError before writing. Source/setup manifests
    precede simulation. Failed checks retain rows and reasons and block readiness;
    they do not trigger redrawing, split reassignment, silent dropping or ML work.
    """
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"Preserving existing data at {output}; use a new --output directory")
    setups = make_setups()
    manifest_check = validate_setups(setups)
    pilot_path = ROOT / "verification_results/summary.json"
    pilots = load_verified_pilots(pilot_path, ROOT / "quarter_car.py")
    for setup in setups:
        pair = (setup["ks_N_m"], setup["cs_N_s_m"])
        setup["pilot_id"] = pilots[pair]["pilot_id"] if setup["split"] == "train" and pair in pilots else None
    if sum(row["pilot_id"] is not None for row in setups) != 9:
        raise ValueError("training manifest must contain exactly nine reusable pilots")
    source_paths = list(ROOT.glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    source_paths += [pilot_path, ROOT / "requirements.txt"]
    source_paths += [ROOT.parent / name for name in (
        "MMA3001_2026_Project_Brief.pdf", "MMA3001_Notes_Week05_5_Evaluating_Regression_Performance.ipynb",
        "MMA3001_Notes_Week05_6_Training_Data_Evaluation_and_Selection.ipynb")]
    hashes = {str(path.relative_to(ROOT.parent)): sha256_file(path) for path in source_paths}
    plan = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "stage_date_sydney": "2026-10-05",
        "prediction_contract": {"row": "one unique full suspension setup", "features": ["ks_N_m", "cs_N_s_m"],
                                "target": "A_mm = 1000 * max over full response of abs(zs-zu)",
                                "diagnostics_not_features": ["A_post_m", "settling_after_exit_s", "contact", "energy", "tail"]},
        "counts": COUNTS, "ks_range_N_m": KS_RANGE, "cs_range_N_s_m": CS_RANGE,
        "training": "np.linspace endpoints inclusive, 15 each; ks outer loop, cs inner loop",
        "random_splits": {"generator": "numpy.random.Generator(numpy.random.PCG64(seed))", "seeds": SEEDS,
                          "draw": "one uniform(low=[ks_min,cs_min], high=[ks_max,cs_max], size=(count,2)) per split",
                          "columns": ["ks_N_m", "cs_N_s_m"], "independent_generators": True},
        "units_and_serialization": "SI inputs/raw diagnostics; mm ML target; Python round-trip float text in CSV/JSON",
        "fixed_parameters": asdict(Parameters()), "bump": asdict(Bump()), "initial_state": [0.0] * 4,
        "solver": asdict(SolverSettings()), "horizon_s": HORIZON_S, "observation_dt_s": OBSERVATION_DT_S,
        "settling_band_m": BAND_M, "confirmation_s": CONFIRMATION_S, "contact_screening_margin_N": CONTACT_MARGIN_N,
        "contact_basis": "sampled fixed numerical guard supported by pilot comparisons; not a safety standard or per-row refined minimum",
        "verification_basis": "D005 pilot settings; each row checks solve/finite/continuity/energy/tail/contact/output consistency",
        "heldout_policy": "separate response files; no target distribution, response plot or prediction inspection before choices freeze",
        "pilot_reuse": {"count": 9, "role": "train only", "summary_key": "bands.1.runs.base_1ms",
                        "source": str(pilot_path.relative_to(ROOT)), "sha256": sha256_file(pilot_path)},
        "input_sha256": hashes, "manifest_checks": manifest_check,
        "environment": {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
                        "packages": {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "matplotlib", "pytest")}},
    }
    output.mkdir(parents=True)
    (output / "heldout_test").mkdir()
    write_json(output / "generation_plan.json", plan)
    with (output / "setup_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(setups)
    frozen_hashes = {name: sha256_file(output / name) for name in ("generation_plan.json", "setup_manifest.csv")}
    write_json(output / "summary.json", {"status": "running", "dataset_ready": False,
                                        "frozen_manifest_sha256": frozen_hashes})
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT,
                           capture_output=True, text=True)
    (output / "unit_tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8", newline="\n")
    if tests.returncode != 0:
        write_json(output / "summary.json", {"status": "failed_unit_tests", "dataset_ready": False,
                                            "completed_rows": 0, "manifest_checks": manifest_check})
        return 1
    counts = {split: Counter() for split in COUNTS}
    failure_counts = Counter()
    min_contact, max_tail, max_energy_increase = float("inf"), 0.0, 0.0
    new_runtime, new_nfev, reused_original_runtime = 0.0, 0, 0.0
    started = perf_counter()
    with ExitStack() as stack:
        writers, diagnostics, targets = {}, {}, {}
        for split in COUNTS:
            folder = output / "heldout_test" if split == "test" else output
            targets[split] = stack.enter_context((folder / f"{split}.csv").open("w", newline="", encoding="utf-8"))
            writers[split] = csv.DictWriter(targets[split], fieldnames=TARGET_COLUMNS, lineterminator="\n")
            writers[split].writeheader()
            diagnostics[split] = stack.enter_context((folder / f"{split}_diagnostics.jsonl").open("w", encoding="utf-8", newline="\n"))
        for number, setup in enumerate(setups, 1):
            pair = (setup["ks_N_m"], setup["cs_N_s_m"])
            cached = pilots.get(pair) if setup["split"] == "train" else None
            record, exported = row_result(setup, cached)
            split = setup["split"]
            writers[split].writerow(exported)
            diagnostics[split].write(json.dumps(safe_json(record), allow_nan=False) + "\n")
            # Each finished row is durable; an interrupted run remains incomplete, never 'ready'.
            targets[split].flush()
            diagnostics[split].flush()
            counts[split]["rows"] += 1
            counts[split]["eligible_targets"] += int(record["validity"]["target_valid"])
            counts[split]["settling_unresolved"] += int(record["validity"]["settling_status"] == "unresolved")
            counts[split][record["origin"]] += 1
            counts[split]["new_solver_completed"] += int(record["new_solver_completed"])
            failure_counts.update(record["validity"]["failure_reasons"])
            new_runtime += record["new_integration_runtime_s"] or 0.0
            new_nfev += record["new_derivative_evaluations"] or 0
            reused_original_runtime += record["original_pilot_integration_runtime_s"] or 0.0
            summary = record["raw_summary"]
            if summary is not None:
                for key, variable in (("minimum_contact_N", "min"), ("tail_bound_m", "tail"), ("maximum_energy_increase_J", "energy")):
                    value = summary.get(key)
                    if isinstance(value, (int, float)) and np.isfinite(value):
                        if variable == "min": min_contact = min(min_contact, value)
                        elif variable == "tail": max_tail = max(max_tail, value)
                        else: max_energy_increase = max(max_energy_increase, value)
            if number % 25 == 0:
                print(f"Completed {number}/400; eligible targets so far: "
                      f"{sum(c['eligible_targets'] for c in counts.values())}", flush=True)
    generation_elapsed = perf_counter() - started
    audit = audit_exports(output, setups)
    ready = all(audit[split]["eligible_targets"] == count for split, count in COUNTS.items())
    source_unchanged = all(sha256_file(ROOT.parent / path) == digest for path, digest in hashes.items())
    manifests_unchanged = frozen_manifests_unchanged(output, frozen_hashes)
    ready = ready and source_unchanged and manifests_unchanged
    if not source_unchanged:
        failure_counts["source_changed_during_generation"] += 1
    if not manifests_unchanged:
        failure_counts["frozen_manifest_changed_during_generation"] += 1
    input_coverage_plot(setups, output)
    artifacts = [path for path in output.rglob("*") if path.is_file() and path.name != "summary.json"]
    result = {
        "status": "completed" if ready else "completed_with_failures", "dataset_ready": ready,
        "completed_utc": datetime.now(timezone.utc).isoformat(), "manifest_checks": manifest_check,
        "source_unchanged_during_generation": source_unchanged,
        "frozen_manifests_unchanged": manifests_unchanged, "frozen_manifest_sha256": frozen_hashes,
        "counts": {key: dict(value) for key, value in counts.items()}, "export_audit": audit,
        "failure_counts": dict(failure_counts),
        "predeclared_validity_aggregates": {"minimum_sampled_contact_N": min_contact,
                                           "maximum_tail_bound_mm": max_tail * 1000,
                                           "maximum_positive_energy_increment_J": max_energy_increase},
        "work": {"new_integrations": sum(c["new_solver_completed"] for c in counts.values()),
                 "new_integration_attempts": sum(c["new_integration"] for c in counts.values()),
                 "reused_pilots": sum(c["verified_pilot_baseline"] for c in counts.values()),
                 "known_new_integration_runtime_s": new_runtime, "known_new_derivative_evaluations": new_nfev,
                 "failure_work_note": "Failed solves may have unknown solver cost; row processing time is retained in each diagnostic.",
                 "row_generation_elapsed_s": generation_elapsed,
                 "reused_historical_runtime_s_not_new_work": reused_original_runtime},
        "artifact_sha256": {str(path.relative_to(output)): sha256_file(path) for path in artifacts},
        "no_ml_fitted": True, "heldout_response_statistics_inspected": False,
        "limits": ["Pilot refinement plus per-row validity does not certify each label's exact error.",
                   "Unresolved settling is independent of primary-label eligibility.",
                   "Sampled contact consistency is not continuous-contact proof or real-vehicle validation.",
                   "400 is the adopted initial sample budget, not demonstrated ML sufficiency."],
    }
    write_json(output / "summary.json", result)
    lines = ["# Simulation dataset checkpoint", "", "Working data/check documentation, not the assessed report.", "",
             f"Dataset readiness: **{'PASS' if ready else 'FAIL / investigate'}**.", "",
             "| Role | Declared rows | Eligible targets | Reused pilots | Unresolved settling |",
             "|---|---:|---:|---:|---:|"]
    for split, count in COUNTS.items():
        c = counts[split]
        lines.append(f"| {split} | {count} | {c['eligible_targets']} | {c['verified_pilot_baseline']} | {c['settling_unresolved']} |")
    lines += ["", "## Actual checks", "",
              "- 400 unique setup IDs and coefficient pairs; declared split counts and finite input domain checked before simulation.",
              "- Setup manifest and exact RNG/sampling/configuration/source details saved before generating outputs.",
              f"- Original nine baseline pilot outputs reused in training; {result['work']['new_integrations']} new integrations.",
              "- Every row checked for complete finite solution, exit-state continuity, peak consistency, contact, energy and adequate tail.",
              "- Primary-target eligibility is separate from settling resolution. Failed rows retain their IDs/splits and have empty ML targets.",
              "- Saved CSV/JSON identities, full-precision input round trips and metre-to-millimetre target conversion checked mechanically.",
              f"- Minimum sampled tyre force across generated/reused rows: {min_contact:.6f} N; required screening margin >{CONTACT_MARGIN_N:g} N.",
              f"- Largest remaining-motion bound: {max_tail*1000:.9f} mm; checked against each row's adopted peak/tail margins.",
              f"- Largest positive sampled post-bump energy increment: {max_energy_increase:.9g} J.",
              f"- Failure reasons/counts: {dict(failure_counts)}.",
              "- Exact regression-test output is in unit_tests.txt; source/artifact hashes are recorded in the manifests.",
              "", "## Reproduce and use", "",
              "Run `python generate_dataset.py --output dataset_recheck` from the project folder for a fresh independent version. Existing output folders are never overwritten.",
              "One data row is a complete setup, not a trajectory time sample. Model inputs are ONLY ks_N_m and cs_N_s_m; the sole target is A_mm.",
              "Raw A in metres and supporting post-bump/settling/physical diagnostics are in role-specific JSONL files; they must not become prediction features.",
              "Training and validation outputs are at this directory's top level. Final-test outputs are under heldout_test/; do not inspect them for model choices.",
              "Input locations and predeclared numerical/physical validity checks may be inspected for all splits; no held-out response distribution, prediction error or response plot was inspected.",
              "", "## Limits and next stage", "",
              "Settings were verified on nine pilots. Each later row receives its own validity screening, not a new full refinement/RK4 programme. Settling is labelled resolved_under_adopted_settings to preserve that distinction.",
              "Sampled physical consistency and numerical checks do not validate a real car or prove the entire continuous domain. Sample sufficiency and ML performance remain unknown.",
              "No preprocessing was fitted, no ML model trained, no final-test prediction evaluated and no assessed report written.", ""]
    (output / "CHECK_RESULTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    (output / "heldout_test/README.md").write_text(
        "# Reserved final-test responses\n\nThese 100 setups use seed 3002. Their targets are saved for one final evaluation after modelling choices are fixed.\n\n"
        "Do not use these responses for plots, response statistics, feature/model selection or tuning. Predeclared numerical/physical checks and input identity checks are allowed.\n\n"
        "This separation is a workflow boundary, not encryption or an access-control system. No predictions or test performance have been evaluated.\n",
        encoding="utf-8", newline="\n")
    for path in (output / "CHECK_RESULTS.md", output / "heldout_test/README.md"):
        result["artifact_sha256"][str(path.relative_to(output))] = sha256_file(path)
    write_json(output / "summary.json", result)
    print(json.dumps({"dataset_ready": ready, "counts": result["counts"],
                      "new_integrations": result["work"]["new_integrations"],
                      "reused_pilots": result["work"]["reused_pilots"],
                      "failure_counts": dict(failure_counts)}, indent=2), flush=True)
    return 0 if ready else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dataset_v1"), help="New output folder; existing folders are preserved")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    raise SystemExit(generate(destination))
