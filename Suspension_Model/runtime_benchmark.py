"""Run or audit the bounded P009 warm-query benchmark without fitting models.

Usage: python runtime_benchmark.py run|audit --output runtime_benchmark_v2
Existing result folders are preserved. Audit reads saved timing observations only.
"""

import argparse
import ctypes
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter, get_clock_info

import joblib
import numpy as np
from threadpoolctl import threadpool_info, threadpool_limits

from dataset_design import sha256_file, safe_json
from final_evaluation import verify_seal
from generate_dataset import row_result
from ml_development import load_development, predict_checked, validate_features, write_json
from quarter_car import Bump, Parameters, SolverSettings, simulate

ROOT = Path(__file__).resolve().parent
CASE_IDS = [f"train_{i:03d}" for i in (1, 8, 15, 106, 113, 120, 211, 218, 225)]
METHODS = ("simulation", "linear", "svr")


class QueryFailure(RuntimeError):
    """Query failure with completed/attempted integration work retained."""
    def __init__(self, message, integrations=0, nfev=0, attempts=0):
        super().__init__(message)
        self.integrations, self.nfev, self.attempts = integrations, nfev, attempts


def simulate_peak(X):
    """Return fresh baseline full-response peaks [mm] and solver work for X[n,2].

    Includes feature checks, parameter creation, solves and 1 ms observations.
    Excludes contact/tail/settling classification. QueryFailure retains known work.
    """
    X = validate_features(X)
    values, nfev, completed, attempts = [], 0, 0, 0
    try:
        for ks, cs in X:
            attempts += 1
            trajectory = simulate(Parameters(ks=float(ks), cs=float(cs)), Bump(), 5., SolverSettings())
            completed += 1
            nfev += trajectory.nfev
            _, q = trajectory.sample(.001)
            values.append(float(1000*np.max(np.abs(q[0]-q[2]))))
        if not np.isfinite(values).all():
            raise ValueError("nonfinite peak")
    except Exception as exc:
        raise QueryFailure(str(exc), completed, nfev, attempts) from exc
    return {"values_mm": values, "integrations": completed, "nfev": nfev, "attempts": attempts}


def diagnostic_peak(X, setups):
    """Return fresh full-diagnostic peaks/work; refuse any invalid setup or result.

    X must match setup coefficients. Calls the existing row workflow with no cache.
    Full diagnostics have no equivalent output from the two scalar regressors.
    """
    X = validate_features(X)
    if len(setups) != len(X) or any([s["ks_N_m"], s["cs_N_s_m"]] != x.tolist() for s, x in zip(setups, X)):
        raise ValueError("diagnostic input identities disagree")
    values, nfev, completed, attempts = [], 0, 0, 0
    for setup in setups:
        attempts += 1
        try:
            record, exported = row_result(setup, cached=None)
            completed += int(record["new_solver_completed"])
            nfev += record["new_derivative_evaluations"] or 0
            if (record["origin"] != "new_integration" or record["new_solver_completed"] is not True
                    or not exported["target_valid"]
                    or record["validity"]["settling_status"] != "resolved_under_adopted_settings"):
                raise RuntimeError(f"invalid full diagnostic result: {record.get('exception')}")
            values.append(float(exported["A_mm"]))
        except Exception as exc:
            raise QueryFailure(str(exc), completed, nfev, attempts) from exc
    return {"values_mm": values, "integrations": completed, "nfev": nfev, "attempts": attempts}


def make_schedule():
    """Predeclare warm-ups and five rotating measured rounds; 162 integrations."""
    jobs = []
    for workload, groups, methods in (("single_A", [[i] for i in CASE_IDS], METHODS),
            ("batch_A", [CASE_IDS], METHODS),
            ("full_diagnostic", [[i] for i in CASE_IDS], ("full_diagnostic",))):
        for round_index in range(6):
            order = list(methods)
            shift = max(0, round_index-1) % len(order)
            order = order[shift:] + order[:shift]
            for ids in groups:
                for method in order:
                    ml = method in ("linear", "svr")
                    jobs.append({"phase": "warmup" if round_index == 0 else "timed", "workload": workload,
                        "method": method, "case_ids": list(ids), "round": round_index,
                        "loops": (3 if round_index == 0 else 1000) if ml else 1})
    return jobs


def timed_call(function, loops, clock=perf_counter):
    """Time real calls only; return elapsed seconds, last output and any failure.

    Correctness comparisons and file writes occur in the caller after the clock.
    The wrapper loop overhead is included; no guessed overhead is subtracted.
    """
    if not isinstance(loops, int) or loops < 1:
        raise ValueError("loops must be a positive integer")
    completed, result, error = 0, None, None
    started = clock()
    try:
        for _ in range(loops):
            result = function()
            completed += 1
    except Exception as exc:
        error = exc
    elapsed = clock()-started
    return {"elapsed_s": elapsed, "completed_loops": completed, "result": result, "error": error}


def statistics(samples):
    """Summarise positive finite elapsed seconds; reject missing/invalid samples."""
    a = np.asarray(samples, dtype=float)
    if a.ndim != 1 or len(a) == 0 or not np.isfinite(a).all() or np.any(a <= 0):
        raise ValueError("durations must be a nonempty positive finite vector")
    q25, q75 = np.percentile(a, [25, 75])
    return {"count": len(a), "median_s": float(np.median(a)), "min_s": float(a.min()),
            "max_s": float(a.max()), "q25_s": float(q25), "q75_s": float(q75), "iqr_s": float(q75-q25)}


def summarise_timings(rows):
    """Validate exact planned jobs/work, then summarise without executing queries."""
    schedule = make_schedule()
    if len(rows) != len(schedule) or any(any(row.get(k) != job[k] for k in job) for row, job in zip(rows, schedule)):
        raise ValueError("timing jobs differ from the complete fixed schedule")
    for row in rows:
        if (row.get("status") != "ok" or row.get("completed_loops") != row["loops"]
                or not row.get("checks") or not all(v is True for v in row["checks"].values())):
            raise ValueError("failed or incomplete timing call")
        statistics([row["elapsed_s"]])
        ml = row["method"] in ("linear", "svr")
        expected_work = 0 if ml else len(row["case_ids"])
        if (row["integrations"] != expected_work or row["attempts"] != expected_work
                or row["ml_calls"] != (row["loops"] if ml else 0)
                or row["seconds_per_call"] != row["elapsed_s"]/row["loops"]
                or (row["nfev"] != 0 if ml else row["nfev"] <= 0)):
            raise ValueError("inconsistent measured work or per-call time")
    timed = [r for r in rows if r["phase"] == "timed"]
    singles, batches = {}, {}
    for method in METHODS:
        cases = {ident: statistics([r["seconds_per_call"] for r in timed if r["workload"] == "single_A"
                   and r["method"] == method and r["case_ids"] == [ident]]) for ident in CASE_IDS}
        singles[method] = {"per_case": cases,
            "equal_case_mean_of_medians_s": float(np.mean([s["median_s"] for s in cases.values()]))}
        batch = statistics([r["seconds_per_call"] for r in timed if r["workload"] == "batch_A" and r["method"] == method])
        batches[method] = {**batch, "batch_rows": 9, "median_seconds_per_case": batch["median_s"]/9,
                           "median_cases_per_second": 9/batch["median_s"]}
    full = {ident: statistics([r["seconds_per_call"] for r in timed if r["workload"] == "full_diagnostic"
                              and r["case_ids"] == [ident]]) for ident in CASE_IDS}
    return {"single_query": singles, "batch_A": batches,
        "full_diagnostic": {"per_case": full, "equal_case_mean_of_medians_s": float(np.mean([s["median_s"] for s in full.values()]))},
        "warm_speed_ratios": {"single_A": {m: singles["simulation"]["equal_case_mean_of_medians_s"]/singles[m]["equal_case_mean_of_medians_s"] for m in METHODS[1:]},
                              "batch_A": {m: batches["simulation"]["median_s"]/batches[m]["median_s"] for m in METHODS[1:]}},
        "work": {"simulation_integrations": sum(r["integrations"] for r in rows),
                 "derivative_evaluations": sum(r["nfev"] for r in rows), "ml_calls": sum(r["ml_calls"] for r in rows),
                 "measured_simulation_integrations": sum(r["integrations"] for r in timed),
                 "measured_ml_calls": sum(r["ml_calls"] for r in timed)}}


def execute_jobs(jobs, cases, models, expected_ml, output):
    """Execute the fixed plan, retaining each raw job or failed/partial observation.

    Arrays, callbacks and expected values are prepared before each timing interval.
    Failure stops further jobs after saving the failed record. No fitting occurs.
    """
    if jobs != make_schedule():
        raise ValueError("refusing changed runtime schedule")
    rows = []
    with (Path(output)/"raw_timings.jsonl").open("x", encoding="utf-8", newline="\n") as handle:
        for number, job in enumerate(jobs):
            ids, method = job["case_ids"], job["method"]
            X = np.array([cases[i]["X"] for i in ids], dtype=np.float64)
            original_X = X.copy()
            X.setflags(write=False)
            setups = [cases[i]["setup"] for i in ids]
            ml = method in ("linear", "svr")
            expected = np.array([expected_ml[method][job["workload"]][i] if ml else cases[i]["A_mm"] for i in ids])
            if method == "simulation":
                function = lambda: simulate_peak(X)
            elif method == "full_diagnostic":
                function = lambda: diagnostic_peak(X, setups)
            else:
                function = lambda: predict_checked(models[method], X)
            observation = timed_call(function, job["loops"])
            error, value = observation["error"], observation["result"]
            work = {"integrations": 0, "nfev": 0, "attempts": 0}
            if not ml and value is not None:
                work = {k: value[k] for k in work}
            if isinstance(error, QueryFailure):
                work = {"integrations": error.integrations, "nfev": error.nfev, "attempts": error.attempts}
            actual = np.asarray(value if ml else value["values_mm"], dtype=float) if value is not None else None
            checks = {"input_unchanged": np.array_equal(X, original_X),
                "outputs_reproduce": actual is not None and actual.shape == expected.shape and bool(np.isfinite(actual).all())
                    and (np.array_equal(actual, expected) if ml else np.allclose(actual, expected, rtol=0, atol=1e-8)),
                "positive_duration": bool(np.isfinite(observation["elapsed_s"]) and observation["elapsed_s"] > 0)}
            ok = error is None and all(checks.values()) and observation["completed_loops"] == job["loops"]
            row = {**job, "job_index": number, "status": "ok" if ok else "failed", **work,
                "elapsed_s": observation["elapsed_s"], "seconds_per_call": observation["elapsed_s"]/job["loops"] if ok else None,
                "completed_loops": observation["completed_loops"], "ml_calls": observation["completed_loops"] if ml else 0,
                "checks": {k: bool(v) for k,v in checks.items()}, "values_mm": actual.tolist() if actual is not None else None,
                "maximum_output_difference_mm": float(np.max(abs(actual-expected))) if actual is not None and actual.shape == expected.shape else None,
                "error": f"{type(error).__name__}: {error}" if error else None,
                "failed_solver_work_may_be_unknown": error is not None and not ml}
            handle.write(json.dumps(safe_json(row), allow_nan=False)+"\n")
            handle.flush()
            rows.append(row)
            if not ok:
                raise RuntimeError(f"job {number} failed; preserved raw observation")
    return rows


def power_status():
    """Read Windows AC/battery state without changing power settings; else unknown."""
    class Status(ctypes.Structure):
        _fields_ = [("ac", ctypes.c_ubyte), ("flag", ctypes.c_ubyte), ("percent", ctypes.c_ubyte),
                    ("reserved", ctypes.c_ubyte), ("life", ctypes.c_ulong), ("full", ctypes.c_ulong)]
    try:
        status = Status()
        if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            return {"available": False}
        return {"available": True, "ac_line_status": status.ac, "battery_percent": status.percent, "battery_flag": status.flag}
    except (AttributeError, OSError):
        return {"available": False}


def verify_inputs(plan):
    """Check every declared source/data/model fingerprint without test-file access."""
    for name, digest in plan["input_sha256"].items():
        if sha256_file(ROOT.parent/name) != digest:
            raise ValueError(f"benchmark input changed: {name}")
    verify_seal(ROOT/"final_evaluation_v1")


def integrity_predictions(models, cases):
    """Make 20 untimed guarded calls, preserving each workload's array shape.

    Single-row and batched floating-point evaluation can differ in last bits;
    each measured workload is compared with its own exact pre-timing output.
    """
    X = np.asarray([cases[i]["X"] for i in CASE_IDS], dtype=np.float64)
    return {m: {"single_A": {i: float(predict_checked(model, X[j:j+1])[0]) for j,i in enumerate(CASE_IDS)},
                "batch_A": dict(zip(CASE_IDS, predict_checked(model,X).tolist()))} for m,model in models.items()}


@contextmanager
def single_thread_context():
    """Initialise lazy thread runtimes, then limit and verify every detected pool.

    The first MKL inspection can load Intel OpenMP after discovery has started.
    A fresh limits controller must therefore enumerate after that inspection.
    Original limits are restored on exit, including when work raises an error.
    """
    before = threadpool_info()
    with threadpool_limits(limits=1):
        limited = threadpool_info()
        if not limited or any(p["num_threads"] != 1 for p in limited):
            raise RuntimeError("numerical thread limit not applied")
        yield {"before": before, "limited": limited}


def run(output):
    """Create one checkpoint: verify, test, benchmark, preserve failures and outputs."""
    output = Path(output)
    if output.exists():
        raise FileExistsError("preserving existing benchmark; use audit or a fresh output name")
    frozen, _ = verify_seal(ROOT/"final_evaluation_v1")
    if sys.version != frozen["environment"]["python"] or any(importlib.metadata.version(n) != v for n,v in frozen["environment"]["packages"].items()):
        raise ValueError("environment differs from the frozen final models")
    data = load_development(ROOT/"dataset_v1")["train"]
    cases = {ident: {"X": data["X"][j].tolist(), "A_mm": float(data["y"][j]), "setup": data["diagnostics"][j]["setup"]}
             for j,ident in enumerate(data["ids"]) if ident in CASE_IDS}
    if list(cases) != CASE_IDS or [c["X"] for c in cases.values()] != [[k,c] for k in (18000.,24000.,30000.) for c in (1594.8,2126.4,2658.)]:
        raise ValueError("nine fixed input identities changed")
    models = {m: joblib.load(ROOT/f"final_evaluation_v1/{m}.joblib") for m in METHODS[1:]}
    model_hashes = {m: joblib.hash(model) for m,model in models.items()}
    files = [ROOT/n for n in ("runtime_benchmark.py", "runtime_outputs.py", "tests/test_runtime_benchmark.py", "RUNTIME_PLAN.md",
        "generate_dataset.py", "quarter_car.py", "dataset_design.py", "ml_development.py", "final_evaluation.py",
        "requirements.txt", "requirements-ml.txt", "dataset_v1/summary.json", "dataset_v1/train.csv", "dataset_v1/train_diagnostics.jsonl",
        "final_evaluation_v1/frozen_plan.json", "final_evaluation_v1/refit.json", "final_evaluation_v1/linear.joblib", "final_evaluation_v1/svr.joblib")]
    files += [ROOT.parent/n for n in ("MMA3001_2026_Project_Brief.pdf", "MMA3001_Notes_Week02_1_Optimisation_and_Profiling.ipynb")]
    jobs = make_schedule()
    plan = {"created_utc": datetime.now(timezone.utc).isoformat(), "protocol": "P009 revision 001, adopted for this run",
        "cases": cases, "jobs": jobs, "physical_parameters": asdict(Parameters()), "bump": asdict(Bump()),
        "solver": asdict(SolverSettings()), "horizon_s": 5., "observation_dt_s": .001, "reproduction_atol_mm": 1e-8,
        "dtype": "float64", "untimed_pre_post_integrity_prediction_calls": 40,
        "input_sha256": {str(p.relative_to(ROOT.parent)): sha256_file(p) for p in files},
        "environment": {**frozen["environment"], "platform": platform.platform(), "processor": platform.processor(),
            "logical_cpus": os.cpu_count(), "timer": vars(get_clock_info("perf_counter"))},
        "power_before": power_status(), "background_work": "Other assistant experiments stopped; user/OS processes not controlled or comprehensively measured.",
        "comparison": "warm in-memory A-only queries; full diagnostics separately; no fits or test-response access",
        "warmup_bookkeeping": "Warm-up elapsed durations are retained for work/failure records and excluded from all reported timing statistics.",
        "scope_excludes": ["imports", "model loading", "input-array allocation", "logging", "file export", "plotting"],
        "historical_costs": "See preserved RUNTIME_PLAN.md; partial historical ledger is not a complete contemporaneous build cost."}
    output.mkdir(parents=True)
    write_json(output/"plan.json", plan)
    initial_plan_hash = sha256_file(output/"plan.json")
    write_json(output/"summary.json", {"complete": False, "stage": "testing"})
    try:
        tests = subprocess.run([sys.executable,"-m","pytest","-q","tests"], cwd=ROOT, capture_output=True, text=True)
        (output/"unit_tests.txt").write_text(tests.stdout+tests.stderr, encoding="utf-8", newline="\n")
        if tests.returncode:
            raise RuntimeError("implementation tests failed before benchmark")
        verify_inputs(plan)
        with single_thread_context() as pool_context:
            pools = pool_context["limited"]
            expected = integrity_predictions(models, cases)
            write_json(output/"integrity_predictions.json", {"before": expected})
            print("Starting fixed timing schedule; no fitting or held-out response access.", flush=True)
            started = perf_counter()
            rows = execute_jobs(jobs, cases, models, expected, output)
            schedule_wall = perf_counter()-started
            after_predictions = integrity_predictions(models, cases)
            unchanged_predictions = after_predictions == expected
            write_json(output/"integrity_predictions.json", {"before": expected, "after": after_predictions})
            pools_after = threadpool_info()
        after_hashes = {m: joblib.hash(model) for m,model in models.items()}
        verify_inputs(plan)
        if sha256_file(output/"plan.json") != initial_plan_hash:
            raise RuntimeError("plan changed")
        summary = summarise_timings(rows)
        checks = {"all_calls_valid_and_reproduced": all(all(r["checks"].values()) for r in rows),
            "exactly_162_integrations": summary["work"]["simulation_integrations"] == 162,
            "exactly_100060_benchmark_ml_calls": summary["work"]["ml_calls"] == 100060,
            "models_unchanged": model_hashes == after_hashes, "pre_post_predictions_equal": bool(unchanged_predictions),
            "frozen_inputs_unchanged": True, "one_numerical_thread": bool(pools_after) and all(p["num_threads"] == 1 for p in pools+pools_after)}
        summary.update(complete=all(checks.values()), checks=checks, completed_utc=datetime.now(timezone.utc).isoformat(),
            stage="completed", plan_sha256=sha256_file(output/"plan.json"), schedule_wall_seconds=schedule_wall,
            model_memory_hashes=model_hashes, threadpools=pools, threadpools_after=pools_after,
            threadpools_before_limit=pool_context["before"], power_after=power_status(),
            maximum_simulation_reproduction_difference_mm=max(r["maximum_output_difference_mm"] for r in rows if r["method"] not in METHODS[1:]),
            pre_post_integrity_prediction_calls=40, historical_costs=plan["historical_costs"],
            limits=["Simulated-peak approximation at nine previously verified training/pilot inputs, not new accuracy evidence.",
                "Five ML block-average durations do not measure individual-request timing variability.",
                "Warm query ratios exclude offline preparation and startup; no total speedup or numeric break-even claim.",
                "Full diagnostic workflow supplies extra outputs; no equivalent-output ML ratio.",
                "No profiler, optimisation, new fitting or final-test evaluation in this stage."])
        if not summary["complete"]:
            write_json(output/"summary.json", summary)
            return 1
        from runtime_outputs import create_outputs
        create_outputs(output, summary)
        summary["artifact_sha256"] = {p.name:sha256_file(p) for p in output.iterdir() if p.is_file() and p.name != "summary.json"}
        write_json(output/"summary.json", summary)
        print(json.dumps({"checks":checks,"work":summary["work"],"warm_speed_ratios":summary["warm_speed_ratios"]}, indent=2))
        return 0
    except Exception as exc:
        write_json(output/"summary.json", {"complete":False,"stage":"failed","error":f"{type(exc).__name__}: {exc}",
            "note":"Partial raw observations preserved; do not discard or overwrite this checkpoint."})
        raise


def audit(output):
    """Check saved hashes and recompute timing summaries without new timed work."""
    output = Path(output)
    summary = json.loads((output/"summary.json").read_text(encoding="utf-8"))
    if summary.get("complete") is not True:
        raise ValueError("no completed benchmark to audit")
    plan = json.loads((output/"plan.json").read_text(encoding="utf-8"))
    verify_inputs(plan)
    if sha256_file(output/"plan.json") != summary["plan_sha256"]:
        raise ValueError("saved plan changed")
    for name,digest in summary["artifact_sha256"].items():
        if sha256_file(output/name) != digest:
            raise ValueError("saved benchmark artifact changed")
    rows = [json.loads(line) for line in (output/"raw_timings.jsonl").read_text(encoding="utf-8").splitlines()]
    recalculated = summarise_timings(rows)
    if any(summary[k] != v for k,v in recalculated.items()):
        raise ValueError("saved timing summaries do not reproduce")
    print("Audit passed: saved timings, work counts, ratios and fingerprints reproduce; no new timing or fitting.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run","audit"))
    parser.add_argument("--output", type=Path, default=Path("runtime_benchmark_v2"))
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else ROOT/args.output
    raise SystemExit({"run":run,"audit":audit}[args.action](destination))
