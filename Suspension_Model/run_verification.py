"""Reproduce nine pilot checks before any parameter dataset or ML work.

Only the adopted low/nominal/high stiffness-damping combinations are simulated.
Course adaptation and physical sources remain in Project_Setup/EVIDENCE.md.
"""

from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from quarter_car import Bump, Parameters, SolverSettings, simulate, summarise
from rk4_check import simulate_rk4
from run_nominal import compare
from verify_reduced_case import run_reduced_check


BASE = SolverSettings()
TIGHT = SolverSettings(rtol=1e-8, atol=(1e-11, 1e-10, 1e-11, 1e-10), max_step_s=0.0025)
BANDS_M = (0.0005, 0.001, 0.002)


def comparison_pass(comparison):
    """Return whether both peaks and resolved-candidate settling agree."""
    return comparison["peaks_pass"] and comparison["settling_pass"]


def verify_pilot(parameters, horizon_s):
    """Run a single setup's refinements and return evidence plus its reference.

    horizon_s [s] is checked against twice that duration. Each RK4 solution is
    compared against RK45 at its own native observation spacing, without creating
    artificial finer RK4 samples. Exceptions propagate for the caller to record.
    """
    bump = Bump()
    base = simulate(parameters, bump, horizon_s, BASE)
    tight = simulate(parameters, bump, horizon_s, TIGHT)
    extended = simulate(parameters, bump, 2 * horizon_s, TIGHT)
    coarse_rk4 = simulate_rk4(parameters, bump, horizon_s, 0.0005)
    fine_rk4 = simulate_rk4(parameters, bump, horizon_s, 0.00025)
    runs = {
        "base_1ms": (base, 0.001),
        "tight_1ms": (tight, 0.001),
        "tight_0p5ms": (tight, 0.0005),
        "tight_0p25ms": (tight, 0.00025),
        "extended_0p25ms": (extended, 0.00025),
        "rk4_0p5ms": (coarse_rk4, 0.0005),
        "rk4_0p25ms": (fine_rk4, 0.00025),
    }
    pairs = {
        "solver": ("base_1ms", "tight_1ms"),
        "grid_1_to_0p5ms": ("tight_1ms", "tight_0p5ms"),
        "grid_0p5_to_0p25ms": ("tight_0p5ms", "tight_0p25ms"),
        "horizon": ("tight_0p25ms", "extended_0p25ms"),
        "rk4_coarse_vs_rk45": ("rk4_0p5ms", "tight_0p5ms"),
        "rk4_fine_vs_rk45": ("rk4_0p25ms", "tight_0p25ms"),
        "rk4_step_halving": ("rk4_0p5ms", "rk4_0p25ms"),
        "selected_vs_reference": ("base_1ms", "extended_0p25ms"),
    }
    by_band = {}
    for band_m in BANDS_M:
        summaries = {key: summarise(trajectory, step, band_m=band_m)
                     for key, (trajectory, step) in runs.items()}
        comparisons = {key: compare(summaries[a], summaries[b]) for key, (a, b) in pairs.items()}
        by_band[f"{band_m * 1000:g}"] = {"runs": summaries, "comparisons": comparisons}

    main = by_band["1"]
    contact_delta = max(c["contact_minimum_difference_N"] for c in main["comparisons"].values())
    contact_margin = max(1.0, 10 * contact_delta)
    continuity_error = max(float(np.max(abs(tr.segments[0].y[:, -1] - tr.segments[1].y[:, 0])))
                           for tr in (base, tight, extended, coarse_rk4, fine_rk4))
    sample_grid_error = max(float(np.max(abs(tight.sample(dt)[0] - rk.sample(dt)[0])))
                            for dt, rk in ((0.0005, coarse_rk4), (0.00025, fine_rk4)))
    checks = {
        "finite_complete_solutions": all(s["finite_states"] and s["solver_success"] for s in main["runs"].values()),
        "full_exit_state_continuity": continuity_error == 0.0,
        "matched_rk4_comparison_times": sample_grid_error <= 1e-12,
        "energy_nonincrease": all(s["energy_pass"] for s in main["runs"].values()),
        "tail_margin": all(s["tail_pass"] for s in main["runs"].values()),
        "positive_contact_with_margin": all(s["minimum_contact_N"] > contact_margin for s in main["runs"].values()),
        "solver_peak_agreement": main["comparisons"]["solver"]["peaks_pass"],
        "grid_peak_agreement": all(main["comparisons"][key]["peaks_pass"] for key in ("grid_1_to_0p5ms", "grid_0p5_to_0p25ms")),
        "horizon_peak_agreement": main["comparisons"]["horizon"]["peaks_pass"],
        "rk4_peak_agreement": all(main["comparisons"][key]["peaks_pass"] for key in ("rk4_coarse_vs_rk45", "rk4_fine_vs_rk45", "rk4_step_halving")),
        "selected_peak_agreement": main["comparisons"]["selected_vs_reference"]["peaks_pass"],
        "settling_agreement_all_bands": all(c["settling_pass"] for band in by_band.values() for c in band["comparisons"].values()),
    }
    # Keep peak validity separate from unresolved settling or invalid tyre contact.
    numerical_checks = [value for key, value in checks.items()
                        if key not in ("positive_contact_with_margin", "settling_agreement_all_bands")]
    peak_ok = all(numerical_checks)
    final = dict(main["runs"]["extended_0p25ms"])
    final["primary_peak_numerically_resolved"] = peak_ok
    final["physical_contact_consistent"] = checks["positive_contact_with_margin"]
    band_results = {}
    for label, band in by_band.items():
        summary = band["runs"]["extended_0p25ms"]
        resolved = peak_ok and all(c["settling_pass"] for c in band["comparisons"].values())
        band_results[label] = {
            "status": "resolved" if resolved else "unresolved",
            "after_exit_s": summary["settling_after_exit_s"] if resolved else None,
        }
    final["settling_status"] = band_results["1"]["status"]
    final["settling_after_exit_s"] = band_results["1"]["after_exit_s"]
    if final["settling_status"] != "resolved":
        final["settling_entry_s"] = None
    horizon_adequate = all(
        comparison_pass(band["comparisons"]["horizon"])
        and band["runs"]["tight_0p25ms"]["tail_pass"]
        and band["runs"]["extended_0p25ms"]["tail_pass"]
        for band in by_band.values())
    return {
        "parameters": asdict(parameters), "horizon_s": horizon_s,
        "checks": checks, "passed": all(checks.values()),
        "horizon_adequate": horizon_adequate,
        "contact_margin_N": contact_margin, "continuity_error": continuity_error,
        "rk4_comparison_time_difference_s": sample_grid_error,
        "bands": by_band, "final": final, "settling_sensitivity": band_results,
    }, extended


def make_plots(pilots, trajectories, output):
    """Plot only the nine verified sample locations, with no fitted response surface."""
    fig, axes = plt.subplots(3, 3, figsize=(13, 10), sharex=True, sharey=True, layout="constrained")
    for ax, pilot, trajectory in zip(axes.flat, pilots, trajectories):
        if trajectory is None:
            ax.set_title(pilot["id"] + ": unresolved")
            continue
        t, q = trajectory.sample(0.001)
        ax.plot(t, 1000 * (q[0] - q[2]), color="#176b9b", lw=1.2)
        ax.axvline(0.5, color="#8b648d", ls="--", lw=0.9)
        ax.axhline(0, color="grey", lw=0.5)
        ax.axhspan(-1, 1, color="#6fad7b", alpha=0.22)
        f, p = pilot["final"], pilot["parameters"]
        settling = f["settling_after_exit_s"]
        settling_label = "unresolved" if settling is None else f"{settling:.3f} s"
        ax.set_title(f"ks={p['ks']/1000:g} kN/m; cs={p['cs']:.1f} N s/m\n"
                     f"A={f['A_m']*1000:.2f} mm; settling={settling_label}", fontsize=10)
        ax.set_xlim(0, pilot["horizon_s"])
        ax.grid(alpha=0.15)
    for ax in axes[-1, :]:
        ax.set_xlabel("Time from bump start [s]")
    for ax in axes[:, 0]:
        ax.set_ylabel("Body − wheel [mm]")
    fig.suptitle("Nine pilot setups | complete selected observation | green band ±1 mm\n"
                 "Settling is timed from the 0.50 s bump exit", fontsize=14)
    fig.savefig(output / "pilot_responses.png", dpi=140)
    plt.close(fig)

    valid = [p for p in pilots if "final" in p]
    fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")
    positions = np.arange(len(valid))
    for label, color in (("0.5", "#b15822"), ("1", "#176b9b"), ("2", "#348453")):
        values = [p["settling_sensitivity"][label]["after_exit_s"] for p in valid]
        ax.plot(positions, [np.nan if x is None else x for x in values], "o-", color=color,
                label=f"±{label} mm band")
    ax.set_xticks(positions, [p["id"] for p in valid], rotation=25, ha="right")
    ax.set(ylabel="Settling time after bump exit [s]", xlabel="Pilot setup (L=low, N=nominal, H=high)",
           title="Settling depends on the chosen band; primary peak A is unchanged")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.savefig(output / "settling_band_sensitivity.png", dpi=140)
    plt.close(fig)


def write_markdown(result, output):
    """Write the measured checkpoint, making failures and limits visible."""
    lines = ["# Nine-pilot verification checkpoint", "",
             "Technical check record, not the assessed report. Regenerate with `python run_verification.py`.", "",
             f"Overall: **{'PASS' if result['passed'] else 'FAIL / unresolved'}**. "
             f"Common trial duration: {result['horizon_s']:g} s, checked against {2*result['horizon_s']:g} s.", "",
             "## Measured reference results", "",
             "Reference values use tight RK45, 0.25 ms observations and the longer horizon. Exit at 0.50 s is included in A_post.", "",
             "| Setup | ks [N/m] | cs [N s/m] | A [mm] | A_post [mm] | Settling after exit [s] | Min tyre force [N] | Status |",
             "|---|---:|---:|---:|---:|---:|---:|---|"]
    for p in result["pilots"]:
        if "final" not in p:
            lines.append(f"| {p['id']} | | | | | | | ERROR: {p.get('error')} |")
            continue
        f = p["final"]
        settling = "unresolved" if f["settling_after_exit_s"] is None else f"{f['settling_after_exit_s']:.6f}"
        lines.append(f"| {p['id']} | {p['parameters']['ks']:.0f} | {p['parameters']['cs']:.1f} | "
                     f"{f['A_m']*1000:.6f} | {f['A_post_m']*1000:.6f} | {settling} | "
                     f"{f['minimum_contact_N']:.3f} | {'PASS' if p['passed'] else 'FAIL'} |")
    lines += ["", "L/N/H denote low/nominal/high; k is stiffness and c is damping. No interpolation over unsampled setups is claimed.",
              "", "## Largest observed comparison differences", "",
              "Limits: both peaks <=0.05 mm; settling <=0.01 s with matching resolved candidates.", "",
              "| Comparison | max ΔA [mm] | max ΔA_post [mm] | max Δsettling, all bands [s] |",
              "|---|---:|---:|---:|"]
    for name, values in result["comparison_maxima"].items():
        lines.append(f"| {name} | {values['A_mm']:.9g} | {values['A_post_mm']:.9g} | {values['settling_s']} |")
    reduced = result["reduced_case"]
    lines += ["", "## Complementary checks", "",
              f"- Unit-test suite: **{'PASS' if result['unit_tests_passed'] else 'FAIL'}**; exact output in `unit_tests.txt`.",
              f"- Analytical clamped-wheel body diagnostic: **{'PASS' if reduced['passed'] else 'FAIL'}**. Details and exact errors are in `summary.json` under `reduced_case`.",
              "- Tyre contact, post-bump energy, tail bound and full state continuity were checked separately for each pilot and solver run.",
              "- The reduced diagnostic holds the wheel at zero and checks the existing body-force implementation against a known formula. It is not an exact solution of the two-mass model.",
              "- RK4 and RK45 share the physical force function; agreement cannot rule out a shared modelling error.",
              "- RK4 step halving changes both integration and observation spacing. Its peak difference must not be treated as a pure integration-error estimate; the same-grid RK4/RK45 comparisons separate this effect.",
              f"- Reduced-case maximum position discrepancy: {reduced['max_errors']['position_m']} m (limit {reduced['acceptance']['position_m']} m).",
              f"- Reduced-case maximum velocity discrepancy: {reduced['max_errors']['velocity_m_s']} m/s (limit {reduced['acceptance']['velocity_m_s']} m/s).",
              "", "## Settling-band sensitivity", "",
              "| Setup | ±0.5 mm [s] | ±1 mm [s] | ±2 mm [s] |", "|---|---:|---:|---:|"]
    for p in result["pilots"]:
        if "settling_sensitivity" in p:
            values = [p["settling_sensitivity"][label]["after_exit_s"] for label in ("0.5", "1", "2")]
            lines.append("| " + p["id"] + " | " + " | ".join("unresolved" if value is None else f"{value:.6f}" for value in values) + " |")
    lines += ["", "The ±1 mm band remains the adopted diagnostic. Band sensitivity is interpretation of the same trajectories, not new ML targets.",
              "", "## Settings decision", "", result["decision"], "",
              "## Measured computational work", "",
              "Totals below cover nine integrations per method/duration. They are single-run measurements, not repeated performance benchmarks.", "",
              "| Method/run | Total derivative calls | Total integration time [s] |", "|---|---:|---:|"]
    for key in ("base_1ms", "tight_0p25ms", "extended_0p25ms", "rk4_0p5ms", "rk4_0p25ms"):
        summaries = [p["bands"]["1"]["runs"][key] for p in result["pilots"] if "bands" in p]
        lines.append(f"| {key} | {sum(s['derivative_evaluations'] for s in summaries)} | "
                     f"{sum(s['integration_runtime_s'] for s in summaries):.6f} |")
    lines += ["",
              "## Reproducibility and limits", "",
              "`summary.json` retains every comparison, solver/grid/band setting, success flag, energy/contact/tail result, derivative count, integration timing, dependency version and source hash. Time histories for plotting are in `pilot_traces_1ms.npz`.",
              "Timings are single-run measurements on this laptop; re-evaluating a trajectory on a different grid does not create an independent integration benchmark.",
              "The nine pilots include the nominal case. Repeated refinements of a setup are not independent dataset rows. No full parameter dataset, ML fitting or report writing was performed.",
              "These checks support the ideal model at the sampled setups. They do not prove every point in the parameter rectangle, certify exact continuous-time errors, establish real-car validity or establish physical travel clearance.", ""]
    (output / "CHECK_RESULTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main():
    """Run this bounded verification programme and return nonzero on failure."""
    output = ROOT / "verification_results"
    output.mkdir(exist_ok=True)
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT,
                           capture_output=True, text=True)
    (output / "unit_tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8", newline="\n")
    reduced = run_reduced_check()
    prerequisites = tests.returncode == 0 and reduced["passed"]
    attempts = []
    levels_k = (18000.0, 24000.0, 30000.0)
    levels_c = (1594.8, 2126.4, 2658.0)
    for horizon in (5.0, 10.0):
        pilots, trajectories = [], []
        for i, ks in enumerate(levels_k):
            for j, cs in enumerate(levels_c):
                name = f"k{'LNH'[i]}_c{'LNH'[j]}"
                parameters = replace(Parameters(), ks=ks, cs=cs)
                try:
                    pilot, trajectory = verify_pilot(parameters, horizon)
                    pilot["id"] = name
                    pilot["checks"]["unit_and_reduced_prerequisites"] = prerequisites
                    pilot["passed"] = pilot["passed"] and prerequisites
                    if not prerequisites:
                        pilot["final"]["primary_peak_numerically_resolved"] = False
                        pilot["final"]["settling_status"] = "unresolved"
                        pilot["final"]["settling_after_exit_s"] = None
                        pilot["final"]["settling_entry_s"] = None
                        for band in pilot["settling_sensitivity"].values():
                            band.update(status="unresolved", after_exit_s=None)
                except (ValueError, RuntimeError, FloatingPointError) as error:
                    pilot = {"id": name, "parameters": asdict(parameters), "passed": False,
                             "horizon_adequate": False, "error": str(error)}
                    trajectory = None
                pilots.append(pilot)
                trajectories.append(trajectory)
                print(f"{name}, {horizon:g} s: {'PASS' if pilot['passed'] else 'FAIL/unresolved'}", flush=True)
        attempts.append({"horizon_s": horizon, "pilots": pilots})
        # Extend observation only for an inadequate tail/horizon, not to conceal contact loss.
        if all(p["horizon_adequate"] for p in pilots) or any("error" in p for p in pilots):
            break

    valid = [p for p in pilots if "bands" in p]
    maxima = {}
    for pilot in valid:
        for band in pilot["bands"].values():
            for key, c in band["comparisons"].items():
                m = maxima.setdefault(key, {"A_mm": 0.0, "A_post_mm": 0.0, "settling_s": 0.0})
                m["A_mm"] = max(m["A_mm"], c["A_difference_mm"])
                m["A_post_mm"] = max(m["A_post_mm"], c["A_post_difference_mm"])
                if c["settling_difference_s"] is None:
                    m["settling_s"] = None
                elif m["settling_s"] is not None:
                    m["settling_s"] = max(m["settling_s"], c["settling_difference_s"])
    passed = prerequisites and len(pilots) == 9 and all(p["passed"] for p in pilots)
    decision = (
        f"Adopt RK45 rtol=1e-6, atol=[1e-9 m,1e-8 m/s,1e-9 m,1e-8 m/s], max_step=0.005 s, "
        f"1 ms observations and {horizon:g} s duration as the starting settings for later runs. "
        "All nine pilots agree with the tighter/longer reference within the declared limits. "
        "Every later setup must still pass contact and tail checks; unresolved runs must be investigated, not silently used as labels."
        if passed else
        "No production-settings decision: one or more checks failed or remain unresolved. Inspect saved failures before any wider data generation."
    )
    source_files = list(ROOT.glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    source_files += [ROOT.parent / name for name in (
        "MMA3001_Notes_Week07_4_Runge_Kutta_Methods.ipynb",
        "MMA3001_Notes_Week07_5_Higher_Order_ODEs.ipynb", "MMA3001_2026_Project_Brief.pdf")]
    hashes = {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    env = {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
           "packages": {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "matplotlib", "pytest")}}
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(), "stage_date_sydney": "2026-10-05",
              "scope": "nine-pilot verification, RK4 comparison, reduced analytic case and band sensitivity",
              "passed": passed, "unit_tests_passed": tests.returncode == 0,
              "horizon_s": horizon, "initial_state": [0.0] * 4, "bump": asdict(Bump()),
              "baseline_solver": asdict(BASE), "tight_solver": asdict(TIGHT),
              "bands_m": BANDS_M, "rk4_steps_s": [0.0005, 0.00025],
              "acceptance": {"peak_difference_mm": 0.05, "settling_difference_s": 0.01,
                             "confirmation_s": 1.0, "maximum_tail_m": 0.0005,
                             "energy_rule": "1e-10 * max(1 J, exit energy)",
                             "contact_margin_rule": "max(1 N, 10 times largest compared sampled minimum difference)"},
              "pilots": pilots, "earlier_horizon_attempts": attempts[:-1],
              "comparison_maxima": maxima, "reduced_case": reduced,
              "decision": decision, "selected_settings": {"solver": asdict(BASE), "observation_dt_s": 0.001, "horizon_s": horizon} if passed else None,
              "environment": env, "input_sha256": hashes}
    (output / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    traces = {}
    for pilot, trajectory in zip(pilots, trajectories):
        if trajectory is not None:
            t, q = trajectory.sample(0.001)
            traces[pilot["id"] + "_time_s"] = t
            traces[pilot["id"] + "_state"] = q
    np.savez_compressed(output / "pilot_traces_1ms.npz", **traces)
    make_plots(pilots, trajectories, output)
    write_markdown(result, output)
    print(json.dumps({"passed": passed, "horizon_s": horizon,
                      "comparison_maxima": maxima, "decision": decision}, indent=2), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
