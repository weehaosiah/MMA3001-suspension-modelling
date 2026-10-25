"""Render saved nominal profiling evidence; no simulation or ML calls.

Run: python profile_outputs.py --output profiling_v1
Regenerates only derived analysis.json, CHECK_RESULTS.md and self_time.png after
the recorded source/raw-data audit passes. Raw profiles and trial data are untouched.
"""

import argparse
import json
import os
from pathlib import Path
import statistics

from profile_nominal import ROOT, audit, digest, write_json


def analyse(output):
    """Return per-function medians/ranges from the three saved profiler exports.

    Self shares use the sum of self times for that profile. Cumulative shares use
    the same denominator but overlap between caller and callee; do not add them.
    Missing identities across runs raise ValueError.
    """
    output = Path(output)
    tables = [json.loads((output / f"pair_{i}_functions.json").read_text()) for i in (1, 2, 3)]
    grouped = {}
    totals = []
    for rows in tables:
        total = sum(r["self_s"] for r in rows)
        totals.append(total)
        for r in rows:
            key = (r["source"], r["line"], r["function"])
            grouped.setdefault(key, []).append(dict(**r, self_percent=100*r["self_s"]/total,
                                                    cumulative_percent=100*r["cumulative_s"]/total))
    functions = []
    for (source, line, name), rows in grouped.items():
        if len(rows) != 3:
            raise ValueError(f"Profile function identity changed: {source}:{line}:{name}")
        item = dict(source=source, line=line, function=name)
        for field in ("self_s", "cumulative_s", "self_percent", "cumulative_percent", "calls"):
            values = [r[field] for r in rows]
            item[field] = dict(median=statistics.median(values), min=min(values), max=max(values))
        functions.append(item)
    return dict(profile_self_totals_s=totals, functions=functions,
                source_sha256={f"pair_{i}_functions.json": digest(output / f"pair_{i}_functions.json")
                               for i in (1, 2, 3)})


def render(output):
    """Audit and save derived Markdown/table/plot evidence from an existing run."""
    output = Path(output)
    audit(output)
    data = analyse(output)
    summary = json.loads((output / "summary.json").read_text())
    trials = json.loads((output / "trials.json").read_text())
    write_json(output / "analysis.json", data)
    timing = summary["timing"]
    rows = sorted(data["functions"], key=lambda r: r["self_s"]["median"], reverse=True)
    own = {r["function"]: r for r in rows if r["source"] == "project/quarter_car.py"}
    lines = ["# Nominal profiling: actual results", "", "Completed 12 October 2026. Working performance evidence, not assessed report prose.", "",
             "Seven repetitions of one existing nominal setup: one warmup and three alternating unprofiled/profiled pairs. No new dataset rows or ML calls.", "",
             "## Checks", "", "| Check | Actual outcome |", "|---|---|"]
    lines += [f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in summary["checks"].items()]
    protected_count = len(json.loads((output / "preservation_before.json").read_text()))
    lines += ["", f"All {protected_count} previously existing protected scientific/course files remain byte-identical. All seven non-timing summaries exactly equal the saved nominal baseline, including 6196 derivative evaluations each. Total: 43372 evaluations and 14 solver segments. Raw settling status stays `candidate`; earlier refinement established the nominal resolved result.", "",
              "Thirteen new focused bookkeeping tests passed in 0.90 s; the old 433-test suite was not rerun. Saved-profile audit passes without a new solve. See TEST_RESULTS.md for test scope and the initial temporary-directory failure.", "",
              "## Wall time and instrumentation", "", "| Mode | Observations | Median [ms] | Minimum [ms] | Maximum [ms] |", "|---|---:|---:|---:|---:|"]
    for mode in ("unprofiled", "profiled"):
        r = timing[mode]
        lines.append(f"| {mode} | {r['observations']} | {r['median_s']*1000:.6f} | {r['min_s']*1000:.6f} | {r['max_s']*1000:.6f} |")
    lines += ["", "| Pair | Execution order | Profiled / unprofiled wall time |", "|---|---|---:|"]
    for pair, ratio in enumerate(timing["paired_profile_to_unprofiled_ratios"], 1):
        order = " then ".join(r["mode"] for r in trials if r["pair"] == pair)
        lines.append(f"| {pair} | {order} | {ratio:.6f} |")
    lines += ["", f"Median paired ratio: **{timing['median_paired_ratio']:.6f}**. This includes profiler overhead and timing noise, not a performance improvement. Warmup ({trials[0]['wall_s']*1000:.3f} ms) is excluded from these statistics.", "",
              "The earlier nine-case benchmark and today's nominal full-diagnostic measurements have different workload/conditions. Their times must not be combined into a regression or speedup claim. Background OS/user load was not comprehensively controlled; three observations are a limited local sample.", "",
              "## Largest self-time contributors", "", "Self time excludes called functions. Percentages are per-profile shares, then summarised by their median; medians need not add to 100%.", "",
              "| Function identity | Median calls | Median self time [ms] | Median self share [%] |", "|---|---:|---:|---:|"]
    for r in rows[:10]:
        label = f"{r['source']}:{r['line']} {r['function']}".replace("|", "\\|")
        lines.append(f"| {label} | {r['calls']['median']} | {r['self_s']['median']*1000:.3f} | {r['self_percent']['median']:.2f} |")
    lines += ["", "![Ten largest self-time contributors](self_time.png)", "", "## Physical call paths (overlapping cumulative time)", "",
              "Cumulative time includes callees. These rows overlap: simulate calls the solver, which calls rhs, which calls road_height. Do not add their shares.", "",
              "| Function | Median cumulative [ms] | Median share [%] | Share range [%] |", "|---|---:|---:|---:|"]
    for name in ("simulate", "rhs", "road_height", "summarise", "state_at", "settling_candidate", "contact_force", "post_bump_energy"):
        r = own[name]; c = r["cumulative_percent"]
        lines.append(f"| {name} | {r['cumulative_s']['median']*1000:.3f} | {c['median']:.2f} | {c['min']:.2f}-{c['max']:.2f} |")
    lines += ["", "## Interpretation and decision", "",
              "Most instrumented time lies in advancing the motion, with a smaller part evaluating the saved trajectory and diagnostics. RK45 repeatedly asks rhs for velocities/accelerations. rhs obtains the road height at each stage; one additional vector road-height call is used by the contact check. This explains 6197 road calls versus 6196 derivative calls.", "",
              "road_height is the leading self-time function in all three profiles. Static source inspection shows that its general scalar/array interface performs NumPy conversion, finite checks, allocation and masking on each call, including flat-road times. This makes a specialised scalar path a candidate for a separately tested future optimisation. The profile does not measure the benefit of that proposed change, and profiler overhead can distort relative Python/native costs.", "",
              "Decision for this stage: retain the frozen correct implementation, tolerances, precision and diagnostics. Existing validation remains applicable; no speedup is claimed. Any later optimisation should preserve scalar/array behaviour and all physical outputs, be checked separately and be measured without the profiler. Do not tune on the consumed final test.", "",
              "No memory, FLOPS, arithmetic-intensity or hardware-counter measurement was made. Function-call counts are not operation counts; this evidence cannot classify the workload as compute-bound or bandwidth-bound.", "",
              "## Reproduce and inspect", "",
              "Run `python profile_nominal.py audit --output profiling_v1` to check raw saved evidence. Run `python profile_outputs.py --output profiling_v1` to recreate this presentation and plot; neither command solves the model. Run mode is described in [PROFILING_GUIDE.md](../PROFILING_GUIDE.md) and requires a new output folder.", "",
              "Raw evidence: plan.json, trials.json, three pair_*.prof files, three function JSON tables, three pstats text files, preservation_before/after.json and summary.json. Profiler source hashes and environment are recorded. JSON exports are readable without relying on cross-version binary profiler compatibility.", ""]
    (output / "CHECK_RESULTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    top = rows[:10][::-1]
    labels = [(r["function"].replace("<method 'reduce' of 'numpy.ufunc' objects>", "NumPy reduce")
               .replace("<method 'all' of 'numpy.generic' objects>", "NumPy scalar all")
               + "  [" + Path(r["source"]).name + "]") for r in top]
    values = [r["self_s"]["median"]*1000 for r in top]
    errors = [[(r["self_s"]["median"]-r["self_s"]["min"])*1000 for r in top],
              [(r["self_s"]["max"]-r["self_s"]["median"])*1000 for r in top]]
    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")
    ax.barh(labels, values, xerr=errors, color="#246c8a", capsize=3)
    ax.set(xlabel="Self time per profiled nominal run [ms]", title="Where the nominal simulation spends self time")
    ax.grid(axis="x", alpha=.2); ax.set_axisbelow(True)
    fig.suptitle("Median of three profiles; whiskers show min-max. Instrumented costs include profiler distortion.", fontsize=10)
    fig.savefig(output / "self_time.png", dpi=150)
    plt.close(fig)
    print("Rendered saved-profile analysis, check report and self-time plot; no new numerical work.")


def main():
    """Select the completed checkpoint; render only its derived presentation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "profiling_v1")
    render(parser.parse_args().output)


if __name__ == "__main__":
    main()
