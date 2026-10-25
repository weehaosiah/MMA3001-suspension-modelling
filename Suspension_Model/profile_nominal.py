"""Profile unchanged nominal integration plus physical diagnostics.

Run: python profile_nominal.py run --output profiling_v1
Read-only check: python profile_nominal.py audit --output profiling_v1
Uses cProfile as a standard-library extension to Week02_1 profiling principles.
No model loading, fitting, dataset generation or original test-response parsing.
"""

import argparse
import cProfile
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import math
from pathlib import Path
import platform
import pstats
import statistics
import sys
from time import perf_counter, get_clock_info

from threadpoolctl import threadpool_info, threadpool_limits
from quarter_car import Bump, Parameters, SolverSettings, simulate, summarise

ROOT = Path(__file__).resolve().parent
PARAMETERS, BUMP, SETTINGS = Parameters(), Bump(), SolverSettings()
SCHEDULE = [(0, "warmup"), (1, "unprofiled"), (1, "profiled"),
            (2, "profiled"), (2, "unprofiled"), (3, "unprofiled"), (3, "profiled")]


def write_json(path, value):
    """Write readable finite JSON to a new checkpoint file."""
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n",
                          encoding="utf-8", newline="\n")


def digest(path):
    """Return SHA-256 of file bytes, without interpreting their contents."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def protected_files(exclude=None):
    """Fingerprint existing scientific files and original local course sources.

    Excludes documentation, caches, this new runner/test and profiling outputs.
    Held-out files are read only as uninterpreted bytes for preservation hashes.
    """
    excluded = Path(exclude).resolve() if exclude is not None else None
    paths = []
    for path in ROOT.rglob("*"):
        parts = path.relative_to(ROOT).parts
        if (not path.is_file() or (excluded is not None and path.resolve().is_relative_to(excluded))
                or any(p.startswith(".") or p == "__pycache__"
                                     or p.startswith("profiling_") for p in parts)
                or path.suffix in (".md", ".html")
                or path.name in ("profile_nominal.py", "test_profile_nominal.py", "build_docs.py")):
            continue
        paths.append(path)
    paths += list(ROOT.parent.glob("MMA3001_*.ipynb"))
    paths += list(ROOT.parent.glob("MMA3001_*.pdf"))
    return {p.relative_to(ROOT.parent).as_posix(): digest(p) for p in sorted(paths)}


def nominal_workload():
    """Return the unchanged 5 s nominal summary at 1 ms observation spacing.

    Includes integration, dense sampling, peak, post-bump, settling/contact/energy
    diagnostics. Parameter construction, imports and file I/O are outside this call.
    Exceptions from the existing simulation/diagnostics propagate unchanged.
    """
    return summarise(simulate(PARAMETERS, BUMP, 5.0, SETTINGS),
                     dt_s=0.001, band_m=0.001, confirmation_s=1.0)


def physics_only(result):
    """Exclude only variable integration time; retain every physical/work field."""
    return {k: v for k, v in result.items() if k != "integration_runtime_s"}


def require_equivalent(result, reference):
    """Raise on any non-timing discrepancy, including work counts or status."""
    if physics_only(result) != physics_only(reference):
        raise ValueError("Nominal non-timing results differ from the saved baseline")
    for key in ("solver_success", "finite_states", "tail_pass", "energy_pass",
                "contact_positive_on_grid"):
        if result[key] is not True:
            raise ValueError(f"Failed physical/numerical check: {key}")


def source_label(filename):
    """Make profiler identities readable without publishing absolute host paths."""
    name = filename.replace("\\", "/")
    for marker, prefix in (("/Suspension_Model/", "project/"),
                           ("/site-packages/", "packages/"), ("/Lib/", "stdlib/")):
        if marker in name:
            return prefix + name.split(marker, 1)[1]
    return name if not Path(name).is_absolute() else "external/" + Path(name).name


def profile_rows(stats):
    """Export function identity, call counts and self/cumulative seconds.

    Cumulative time includes callees; its rows overlap and must not be summed.
    """
    rows = []
    for (filename, line, name), (primitive, calls, own, cumulative, _) in stats.stats.items():
        rows.append(dict(source=source_label(filename), line=line, function=name,
                         primitive_calls=primitive, calls=calls, self_s=own,
                         cumulative_s=cumulative))
    return sorted(rows, key=lambda r: (r["source"], r["line"], r["function"]))


def call_count(rows, source, function):
    """Count calls using both module identity and name; reject an absent function."""
    matches = [r for r in rows if r["source"] == source and r["function"] == function]
    if len(matches) != 1:
        raise ValueError(f"Missing/ambiguous profile identity: {source}:{function}")
    return matches[0]["calls"]


def validate_profile(rows, nfev):
    """Check actual profiler counts against the prescribed physical workload."""
    expected = {"simulate": 1, "summarise": 1, "rhs": nfev,
                "road_height": nfev + 1, "sample": 1, "state_at": 1,
                "post_bump_energy": 1, "contact_force": 1, "settling_candidate": 1}
    for name, count in expected.items():
        if call_count(rows, "project/quarter_car.py", name) != count:
            raise ValueError(f"Unexpected profile work count for {name}")
    if call_count(rows, "packages/scipy/integrate/_ivp/ivp.py", "solve_ivp") != 2:
        raise ValueError("Expected two RK45 segments per nominal solve")


def timing_summary(records):
    """Compute medians/ranges and pair-specific profiler wall-time ratios.

    The ratios describe instrumentation overhead plus timing noise, not speedup.
    Requires the exact seven-call schedule and positive finite wall times.
    """
    if [(r["pair"], r["mode"]) for r in records] != SCHEDULE:
        raise ValueError("Unexpected workload schedule")
    if any(not math.isfinite(r["wall_s"]) or r["wall_s"] <= 0 for r in records):
        raise ValueError("Wall times must be finite and positive")
    result = {}
    for mode in ("unprofiled", "profiled"):
        values = [r["wall_s"] for r in records if r["mode"] == mode]
        result[mode] = dict(median_s=statistics.median(values), min_s=min(values),
                            max_s=max(values), observations=len(values))
    pairs = []
    for pair in (1, 2, 3):
        values = {r["mode"]: r["wall_s"] for r in records if r["pair"] == pair}
        pairs.append(values["profiled"] / values["unprofiled"])
    result["paired_profile_to_unprofiled_ratios"] = pairs
    result["median_paired_ratio"] = statistics.median(pairs)
    return result


def one_thread(pools):
    """Require at least one discovered numerical pool and one thread in each."""
    return bool(pools) and all(p["num_threads"] == 1 for p in pools)


def run(output):
    """Create one bounded checkpoint; refuse overwrite and retain failed attempts.

    Seven actual integrations are prescribed. Existing output raises FileExistsError
    before any workload. Any failure writes failure.json and is re-raised.
    """
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    records = []
    try:
        baseline = json.loads((ROOT / "results/summary.json").read_text())["runs"]["baseline_5s_1ms"]
        before = protected_files(output)
        write_json(output / "preservation_before.json", before)
        # Discover libraries before creating a fresh controller: MKL discovery can
        # itself load an OpenMP pool that a prematurely created controller misses.
        discovered_pools = threadpool_info()
        with threadpool_limits(limits=1):
            plan = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                        parameters=asdict(PARAMETERS), bump=asdict(BUMP), settings=asdict(SETTINGS),
                        end_time_s=5.0, observation_dt_s=.001, band_m=.001, confirmation_s=1.0,
                        schedule=SCHEDULE, python=sys.version, platform=platform.platform(),
                        packages={n: importlib.metadata.version(n) for n in
                                  ("numpy", "scipy", "threadpoolctl")},
                        timer=vars(get_clock_info("perf_counter")),
                        discovered_pools=discovered_pools, threadpools_before=threadpool_info(),
                        runner_sha256=digest(__file__), baseline=baseline,
                        course_basis="Week02_1 cells75-84,91-116,127-129; cProfile is an extension",
                        profiler_api="https://docs.python.org/3.12/library/profile.html",
                        comparison_rule="All summary fields exactly equal except integration_runtime_s")
            write_json(output / "plan.json", plan)
            if not one_thread(plan["threadpools_before"]):
                raise ValueError("Numerical thread preflight failed")
            for pair, mode in SCHEDULE:
                profiler = cProfile.Profile() if mode == "profiled" else None
                started = perf_counter()
                try:
                    if profiler:
                        profiler.enable()
                    result = nominal_workload()
                finally:
                    if profiler:
                        profiler.disable()
                elapsed = perf_counter() - started
                record = dict(pair=pair, mode=mode, wall_s=elapsed, result=result,
                              threadpools=threadpool_info())
                records.append(record)
                write_json(output / "trials.json", records)
                if profiler:
                    profiler.dump_stats(str(output / f"pair_{pair}.prof"))
                    stream = io.StringIO()
                    stats = pstats.Stats(profiler, stream=stream)
                    rows = profile_rows(stats)
                    write_json(output / f"pair_{pair}_functions.json", rows)
                    stats.strip_dirs().sort_stats("cumulative").print_stats(25)
                    stats.sort_stats("tottime").print_stats(25)
                    (output / f"pair_{pair}_pstats.txt").write_text(stream.getvalue(), encoding="utf-8")
                    validate_profile(rows, result["derivative_evaluations"])
                require_equivalent(result, baseline)
                if not one_thread(record["threadpools"]):
                    raise ValueError("A numerical pool escaped the thread limit")
            pools_after = threadpool_info()
        after = protected_files(output)
        write_json(output / "preservation_after.json", after)
        checks = dict(seven_completed_integrations=len(records) == 7,
                      exact_saved_physics_and_work=True, expected_profile_call_counts=True,
                      numerical_pools_one_thread=one_thread(pools_after),
                      protected_files_unchanged=before == after)
        if not all(checks.values()):
            raise ValueError(f"Failed checks: {checks}")
        artifacts = {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()}
        summary = dict(complete=True, checks=checks, timing=timing_summary(records),
                       integrations=7, derivative_evaluations=sum(
                           r["result"]["derivative_evaluations"] for r in records),
                       threadpools_after=pools_after, artifact_sha256=artifacts)
        write_json(output / "summary.json", summary)
        print(f"Profile complete: seven integrations; {len(checks)} checks pass; {len(before)} protected files unchanged.")
    except Exception as exc:
        write_json(output / "failure.json", dict(complete=False, completed_calls=len(records),
                   error_type=type(exc).__name__, error=str(exc)))
        raise


def audit(output):
    """Check saved profiles/results without simulation, timing, fitting or prediction.

    Requires this runner, unchanged authored scientific files and saved checkpoint.
    Course originals are checked if present; absence is disclosed, not hidden.
    Binary .prof files need a compatible Python profiler version; JSON exports remain
    readable independently. Missing/changed evidence raises an exception.
    """
    output = Path(output)
    if (output / "failure.json").exists():
        raise ValueError("Failed checkpoint cannot pass audit")
    plan = json.loads((output / "plan.json").read_text())
    summary = json.loads((output / "summary.json").read_text())
    records = json.loads((output / "trials.json").read_text())
    if not summary["complete"] or not all(summary["checks"].values()):
        raise ValueError("Incomplete/failed checkpoint")
    if digest(__file__) != plan["runner_sha256"]:
        raise ValueError("Profiling runner changed")
    for name, value in summary["artifact_sha256"].items():
        if digest(output / name) != value:
            raise ValueError(f"Changed checkpoint artifact: {name}")
    before = json.loads((output / "preservation_before.json").read_text())
    after = json.loads((output / "preservation_after.json").read_text())
    if before != after:
        raise ValueError("Original files changed during profiling")
    unavailable = []
    for name, value in before.items():
        path = ROOT.parent / name
        if not path.exists() and name.startswith("MMA3001_"):
            unavailable.append(name)
        elif digest(path) != value:
            raise ValueError(f"Changed protected source/result: {name}")
    for r in records:
        require_equivalent(r["result"], plan["baseline"])
        if not one_thread(r["threadpools"]):
            raise ValueError("A recorded trial exceeded the thread limit")
        if r["mode"] == "profiled":
            pair = r["pair"]
            rows = profile_rows(pstats.Stats(str(output / f"pair_{pair}.prof")))
            if rows != json.loads((output / f"pair_{pair}_functions.json").read_text()):
                raise ValueError("Raw profile and function export disagree")
            validate_profile(rows, r["result"]["derivative_evaluations"])
    if timing_summary(records) != summary["timing"]:
        raise ValueError("Saved timing summary does not reproduce")
    if (summary["integrations"] != len(records) or summary["derivative_evaluations"] !=
            sum(r["result"]["derivative_evaluations"] for r in records)):
        raise ValueError("Saved work totals do not reproduce")
    if not all(one_thread(x) for x in (plan["threadpools_before"], summary["threadpools_after"])):
        raise ValueError("Recorded numerical pools were not all one thread")
    print(f"Audit passed: saved profiles, physics, timing and work reproduce; no new solve. {len(unavailable)} excluded course originals unavailable for current-file hashing.")


def main():
    """Parse run/audit mode and checkpoint path; propagate failures as nonzero exit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "audit"))
    parser.add_argument("--output", type=Path, default=ROOT / "profiling_v1")
    args = parser.parse_args()
    (run if args.mode == "run" else audit)(args.output)


if __name__ == "__main__":
    main()
