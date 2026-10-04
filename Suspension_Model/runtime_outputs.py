"""Display completed warm-query timing evidence, without running any workload."""

import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


METHODS = (("simulation", "Simulator: A only", "#45546b"),
           ("linear", "Linear comparator", "#a75d28"),
           ("svr", "Frozen selected SVR", "#176b9b"))


def _milliseconds(value):
    """Format elapsed seconds as milliseconds, retaining short ML call detail."""
    return f"{1000 * value:.6f}"


def _statistics_row(label, stats):
    return (f"| {label} | {stats['count']} | {_milliseconds(stats['median_s'])} | "
            f"{_milliseconds(stats['min_s'])} | {_milliseconds(stats['max_s'])} | "
            f"{_milliseconds(stats['q25_s'])} | {_milliseconds(stats['q75_s'])} | "
            f"{_milliseconds(stats['iqr_s'])} |")


def create_outputs(output: Path, summary: dict):
    """Save the figure and readable checks from a completed benchmark summary.

    This function only formats already recorded evidence. In particular, it
    does not load source responses or models, call predictions, or time work.
    """
    if summary.get("complete") is not True:
        raise ValueError("Readable completed results require a complete benchmark.")
    if not summary.get("checks") or not all(value is True for value in summary["checks"].values()):
        raise ValueError("All benchmark checks must pass before completed results are displayed.")
    single = summary["single_query"]
    batch = summary["batch_A"]
    full = summary["full_diagnostic"]
    for key, _, _ in METHODS:
        for value in (single[key]["equal_case_mean_of_medians_s"], batch[key]["median_s"]):
            if not math.isfinite(value) or value <= 0:
                raise ValueError("Plotting requires finite positive elapsed times.")

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.7), layout="constrained")
    panels = (("One A query\nMean of the nine case medians", single, "equal_case_mean_of_medians_s"),
              ("Batch of nine A queries\nMedian batch time; whiskers show quartiles", batch, "median_s"))
    for column, (title, results, field) in enumerate(panels):
        ax = axes[column]
        values = [results[key][field] * 1000 for key, _, _ in METHODS]
        for position, (key, _, color) in enumerate(METHODS):
            value = values[position]
            if column == 1:
                lo = value - results[key]["q25_s"] * 1000
                hi = results[key]["q75_s"] * 1000 - value
                ax.errorbar(value, position, xerr=[[lo], [hi]], fmt="o", color=color,
                            markersize=8, capsize=4, linewidth=1.5)
            else:
                ax.plot(value, position, "o", color=color, markersize=8)
            ax.annotate(f"{value:.4f} ms", (value, position), xytext=(0, 12),
                        textcoords="offset points", ha="center", fontsize=10, color=color)
        ax.set_xscale("log")
        ax.set(xlim=(min(values) / 2.5, max(values) * 2.5), ylim=(2.55, -.55),
               yticks=range(3), yticklabels=[label for _, label, _ in METHODS],
               xlabel="Elapsed time [ms, logarithmic scale]", title=title)
        ax.grid(axis="x", alpha=.22)
    fig.suptitle("Warm queries at the same nine verified setups | guards and scaling included", fontsize=13)
    fig.supxlabel("Five measured rounds. Simulator: individual calls. ML: averages of 1000 real calls per block.", fontsize=10)
    fig.savefig(output / "runtime_comparison.png", dpi=150)
    plt.close(fig)

    lines = ["# Bounded runtime comparison: actual checks", "",
             "Working computation evidence, not the assessed report.", "",
             "This experiment returns the full-response peak A = max abs(zs-zu), in mm, measured from static equilibrium and including after the bump. It reuses the nine prescribed input locations with fresh timed integrations and the existing frozen models.", "",
             "## Warm A-only query times", "",
             "A warm query starts with Python and the fitted models already loaded. Input checks, saved feature scaling and finite-output checks are included. File export, plotting, startup and model loading are outside these query timers.", "",
             "| Method | Mean of nine single-case medians [ms/query] | Median nine-case batch [ms/batch] | Median batch time / 9 [ms/case] | Batch throughput [cases/s] |",
             "|---|---:|---:|---:|---:|"]
    for key, label, _ in METHODS:
        lines.append(f"| {label} | {_milliseconds(single[key]['equal_case_mean_of_medians_s'])} | "
                     f"{_milliseconds(batch[key]['median_s'])} | {_milliseconds(batch[key]['median_seconds_per_case'])} | "
                     f"{batch[key]['median_cases_per_second']:.3f} |")
    lines += ["", "The single-query aggregate gives each of these nine cases equal weight; it is the mean of their medians, not the median of every observation pooled together. Batch throughput describes one nine-row request, not the latency of an individual request.", "",
              "| Guarded model | A-only single-query warm ratio | A-only nine-case batch warm ratio |",
              "|---|---:|---:|"]
    for key, label in (("linear", "Linear comparator"), ("svr", "Frozen selected SVR")):
        lines.append(f"| {label} | {summary['warm_speed_ratios']['single_A'][key]:.2f} | "
                     f"{summary['warm_speed_ratios']['batch_A'][key]:.2f} |")
    lines += ["", "Each ratio divides simulator A-only time by guarded model time for the same workload. These are warm query ratios on this machine, not overall project speedups or a guarantee on other hardware. Timing does not change the frozen accuracy-based preference for the SVR.", "",
              "## Repeated single-query observations", "",
              "Each simulator observation is one fresh integration. Each ML observation is a block duration divided by 1000 actual guarded prediction calls. There are five measured observations per condition; ML block-to-block spread does not estimate variation among individual requests. No slow measurement is discarded.", "",
              "All elapsed times in the following table are milliseconds. Q25 and Q75 are the lower and upper quartiles; the interquartile range (IQR = Q75 - Q25) describes the middle half of the recorded observations.", "",
              "| Method / case | Observations | Median [ms] | Minimum [ms] | Maximum [ms] | Q25 [ms] | Q75 [ms] | IQR [ms] |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key, label, _ in METHODS:
        for setup_id, stats in single[key]["per_case"].items():
            lines.append(_statistics_row(f"{label} / {setup_id}", stats))
    lines += ["", "## Repeated nine-case batch observations", "",
              "| Method | Observations | Median [ms] | Minimum [ms] | Maximum [ms] | Q25 [ms] | Q75 [ms] | IQR [ms] |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key, label, _ in METHODS:
        lines.append(_statistics_row(label, batch[key]))
    lines += ["", "## Full diagnostic simulation, kept separate", "",
              f"The mean of the nine per-case medians is **{_milliseconds(full['equal_case_mean_of_medians_s'])} ms per setup**. This path also calculates post-bump movement, relative settling, contact, energy and tail checks. The regressors return A only, so there is no equivalent-output ML speed ratio for this richer workflow.", "",
              "| Case | Observations | Median [ms] | Minimum [ms] | Maximum [ms] | Q25 [ms] | Q75 [ms] | IQR [ms] |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for setup_id, stats in full["per_case"].items():
        lines.append(_statistics_row(setup_id, stats))
    work = summary["work"]
    lines += ["", "## Actual checks and work", ""]
    lines += [f"- {name}: **{'PASS' if passed else 'FAIL'}**." for name, passed in summary["checks"].items()]
    lines += [f"- Fresh simulation integrations, including warm-ups: **{work['simulation_integrations']:,}**.",
              f"- Recorded derivative evaluations: **{work['derivative_evaluations']:,}**; these count state-derivative calculations, not floating-point operations.",
              f"- Guarded ML calls in the prescribed warm-ups and timing blocks: **{work['ml_calls']:,}**.",
              "- These are repeats of existing verified inputs, not new dataset rows, new fits or additional final-test evaluation.", "",
              "## Limits and reproduction", "",
              "The A-only simulation path omits contact, tail and settling classification inside its timer. Its use here rests on prior verification of these nine locations; a new arbitrary input still needs physical and numerical checks. Fast A prediction does not supply the post-bump trajectory or settling time.", "",
              "The five-round experiment records local elapsed times. Background load, power conditions and scheduling can affect them, and the saved environment/context must accompany comparisons. Raw block durations, loop counts and method order are preserved with the benchmark outputs.", "",
              "Historical simulation, development and verification costs remain in the separate partial ledger in [RUNTIME_PLAN.md](../RUNTIME_PLAN.md). Do not add a nested integration time to its enclosing row-processing time, or count reused pilot results twice. This stage has not measured a complete new build or established a numeric end-to-end break-even point.", "",
              "See [RUNTIME_GUIDE.md](../RUNTIME_GUIDE.md) for the saved-artifact audit and reproduction procedure. Repeating a benchmark requires fresh computation and can produce different elapsed times. The final accuracy evidence and frozen SVR settings are unchanged.", ""]
    (output / "CHECK_RESULTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
