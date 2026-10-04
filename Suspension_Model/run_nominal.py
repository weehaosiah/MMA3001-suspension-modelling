"""Reproduce the authorised nominal simulation and initial checks only.

Run: python run_nominal.py
Outputs go to results/. No parameter-domain dataset or ML fitting is performed.
"""

from dataclasses import asdict
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
# Keep the plotting cache in the project instead of changing the user's profile.
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")  # Save figures without opening desktop windows.
import matplotlib.pyplot as plt

from quarter_car import (Bump, Parameters, SolverSettings, contact_force,
                         post_bump_energy, road_height, simulate, summarise)


def compare(left, right):
    """Compare output summaries against adopted 0.05 mm / 0.01 s limits."""
    a_diff = abs(left["A_m"] - right["A_m"]) * 1000
    post_diff = abs(left["A_post_m"] - right["A_post_m"]) * 1000
    same_status = left["settling_status"] == right["settling_status"]
    times = [left["settling_after_exit_s"], right["settling_after_exit_s"]]
    time_diff = abs(times[0] - times[1]) if all(t is not None for t in times) else None
    return {
        "A_difference_mm": a_diff, "A_post_difference_mm": post_diff,
        "settling_difference_s": time_diff, "matching_status": same_status,
        "peaks_pass": bool(max(a_diff, post_diff) <= 0.05),
        # Matching unresolved statuses never establish a resolved settling time.
        "settling_pass": bool(same_status and time_diff is not None and time_diff <= 0.01),
        "contact_minimum_difference_N": abs(left["minimum_contact_N"] - right["minimum_contact_N"]),
    }


def make_plots(trajectory, final, output):
    """Save readable response and physical-check figures from the checked run."""
    t, q = trajectory.sample(0.00025)
    d_mm = (q[0] - q[2]) * 1000
    tau = trajectory.bump.duration_s
    blue, orange = "#176b9b", "#c55c25"
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 130})
    fig, axes = plt.subplots(3, 1, figsize=(10, 10), layout="constrained")
    axes[0].plot(t, road_height(t, trajectory.bump) * 1000, color=orange, lw=2)
    axes[0].set(xlim=(0, 1.0), ylim=(-3, 56), ylabel="Road height [mm]",
                title="Prescribed road: 50 mm bump, crossing lasts 0.50 s")
    axes[1].plot(t, d_mm, color=blue, lw=1.8, label="Body minus wheel: zs − zu")
    axes[1].set(xlim=(0, 5), ylabel="Relative movement [mm]",
                title="Whole response: positive = extension; negative = compression")
    axes[1].scatter([final["A_time_s"]], [final["A_signed_m"] * 1000], color=orange, zorder=4)
    axes[1].annotate(f"Largest departure {final['A_m'] * 1000:.3f} mm",
                     (final["A_time_s"], final["A_signed_m"] * 1000),
                     xytext=(1.15, 32), arrowprops={"arrowstyle": "->", "color": orange})
    axes[2].plot(t, d_mm, color=blue, lw=1.8)
    axes[2].set(xlim=(0.5, 4), ylim=(-5, 5), xlabel="Time since bump starts [s]",
                ylabel="Relative movement [mm]",
                title="Post-bump settling: vertical scale enlarged; earlier peaks are clipped")
    for ax in axes:
        ax.axhline(0, color="#555555", lw=0.7)
        ax.axvline(tau, color="#6f577d", ls="--", lw=1.1, label="Bump exit (0.50 s)")
        ax.grid(alpha=0.2)
    for ax in axes[1:]:
        ax.axhspan(-1, 1, color="#63a875", alpha=0.2, label="±1 mm settling band")
    if final["settling_status"] == "resolved":
        entry = final["settling_entry_s"]
        axes[2].axvline(entry, color="#257345", ls=":", lw=1.5)
        entry_state = trajectory.state_at(np.array([entry]))[:, 0]
        entry_mm = (entry_state[0] - entry_state[2]) * 1000
        axes[2].annotate(f"Sustained entry at {entry:.3f} s\n"
                         f"= {final['settling_after_exit_s']:.3f} s after exit",
                         (entry, entry_mm), xytext=(2.15, 3.0),
                         arrowprops={"arrowstyle": "->", "color": "#257345"})
    axes[0].legend(loc="upper right")
    axes[1].legend(loc="lower right", fontsize=9)
    axes[2].legend(loc="lower right", fontsize=9)
    fig.suptitle("Nominal quarter-car | motion measured from static equilibrium", fontsize=15)
    fig.savefig(output / "nominal_response.png")
    plt.close(fig)

    post = t >= tau
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), layout="constrained")
    axes[0].plot(t, contact_force(t, q, trajectory.parameters, trajectory.bump), color=blue)
    axes[0].axhline(0, color=orange, ls="--", label="Contact-loss threshold")
    axes[0].set(ylabel="Total tyre force [N]", xlim=(0, 5),
                title=f"Nominal contact check: sampled minimum {final['minimum_contact_N']:.1f} N")
    axes[0].legend()
    axes[1].semilogy(t[post], post_bump_energy(q[:, post], trajectory.parameters), color=blue)
    axes[1].set(xlabel="Time since bump starts [s]", ylabel="Mechanical energy [J]",
                title="On flat road, damping removes mechanical energy")
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.savefig(output / "nominal_physical_checks.png")
    plt.close(fig)


def main():
    """Run checks, save actual evidence, and exit nonzero if a required check fails."""
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    parameters, bump = Parameters(), Bump()
    base = SolverSettings()
    tight = SolverSettings(rtol=1e-8, atol=(1e-11, 1e-10, 1e-11, 1e-10), max_step_s=0.0025)
    baseline5 = simulate(parameters, bump, 5.0, base)
    refined5 = simulate(parameters, bump, 5.0, tight)
    extended10 = simulate(parameters, bump, 10.0, tight)
    zero5 = simulate(parameters, Bump(height_m=0.0), 5.0, base)
    diagnostics = {
        "baseline_5s_1ms": summarise(baseline5, 0.001),
        "tight_5s_1ms": summarise(refined5, 0.001),
        "tight_5s_0.5ms": summarise(refined5, 0.0005),
        "tight_5s_0.25ms": summarise(refined5, 0.00025),
        "tight_10s_0.25ms": summarise(extended10, 0.00025),
        "zero_5s_1ms": summarise(zero5, 0.001),
    }
    comparisons = {
        "solver_refinement": compare(diagnostics["baseline_5s_1ms"], diagnostics["tight_5s_1ms"]),
        "grid_1_to_0.5ms": compare(diagnostics["tight_5s_1ms"], diagnostics["tight_5s_0.5ms"]),
        "grid_0.5_to_0.25ms": compare(diagnostics["tight_5s_0.5ms"], diagnostics["tight_5s_0.25ms"]),
        "horizon_5_to_10s": compare(diagnostics["tight_5s_0.25ms"], diagnostics["tight_10s_0.25ms"]),
    }
    all_trajectories = [baseline5, refined5, extended10, zero5]
    exit_state_errors = [float(np.max(abs(tr.segments[0].y[:, -1] - tr.segments[1].y[:, 0])))
                         for tr in all_trajectories]
    maximum_zero_state = float(np.max(abs(zero5.sample(0.001)[1])))
    contact_change = max(c["contact_minimum_difference_N"] for c in comparisons.values())
    # Additional numerical ambiguity rule, selected for this check (not a standard).
    contact_margin = max(1.0, 10.0 * contact_change)
    nominal_keys = [key for key in diagnostics if not key.startswith("zero")]
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"],
                           cwd=ROOT, capture_output=True, text=True)
    (output / "unit_tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    checks = {
        "independent_unit_tests": tests.returncode == 0,
        "zero_road_equilibrium": maximum_zero_state == 0.0,
        "solver_success_and_finite_states": all(d["solver_success"] and d["finite_states"] for d in diagnostics.values()),
        "full_exit_state_continuity": max(exit_state_errors) == 0.0,
        "solver_refinement": comparisons["solver_refinement"]["peaks_pass"] and comparisons["solver_refinement"]["settling_pass"],
        "output_grid_refinement": all(comparisons[k]["peaks_pass"] and comparisons[k]["settling_pass"] for k in ("grid_1_to_0.5ms", "grid_0.5_to_0.25ms")),
        "extended_observation": comparisons["horizon_5_to_10s"]["peaks_pass"] and comparisons["horizon_5_to_10s"]["settling_pass"],
        "nominal_positive_contact_with_margin": all(diagnostics[k]["minimum_contact_N"] > contact_margin for k in nominal_keys),
        "post_bump_energy": all(diagnostics[k]["energy_pass"] for k in nominal_keys),
        "nominal_tail": all(diagnostics[k]["tail_pass"] for k in nominal_keys),
    }
    final = dict(diagnostics["tight_10s_0.25ms"])
    numerical_prerequisites = all(checks[name] for name in (
        "independent_unit_tests", "zero_road_equilibrium", "solver_success_and_finite_states",
        "full_exit_state_continuity", "post_bump_energy", "nominal_tail"))
    peaks_resolved = numerical_prerequisites and all(c["peaks_pass"] for c in comparisons.values())
    settling_resolved = (numerical_prerequisites and final["settling_status"] == "candidate"
                         and all(c["settling_pass"] for c in comparisons.values())
                         and checks["nominal_tail"])
    final["primary_peak_numerically_resolved"] = bool(peaks_resolved)
    final["settling_status"] = "resolved" if settling_resolved else "unresolved"
    if not settling_resolved:
        final["settling_after_exit_s"] = final["settling_entry_s"] = None
    final["nominal_contact_consistent"] = checks["nominal_positive_contact_with_margin"]
    final["all_initial_checks_pass"] = all(checks.values())

    versions = {package: importlib.metadata.version(package)
                for package in ("numpy", "scipy", "matplotlib", "pytest")}
    environment = {"python": sys.version, "executable": sys.executable,
                   "platform": platform.platform(), "packages": versions}
    source_paths = [ROOT / "quarter_car.py", ROOT / "run_nominal.py", ROOT / "tests/test_quarter_car.py",
                    ROOT.parent / "MMA3001_2026_Project_Brief.pdf",
                    ROOT.parent / "MMA3001_Notes_Week07_4_Runge_Kutta_Methods.ipynb",
                    ROOT.parent / "MMA3001_Notes_Week07_5_Higher_Order_ODEs.ipynb"]
    hashes = {str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in source_paths if path.exists()}
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "one nominal setup and initial checks; no dataset or ML",
              "parameters": asdict(parameters), "bump": asdict(bump),
              "initial_state": [0.0] * 4,
              "baseline_solver": asdict(base), "refined_solver": asdict(tight),
              "acceptance": {"peak_difference_mm": 0.05, "settling_difference_s": 0.01,
                             "contact_margin_N": contact_margin,
                             "contact_margin_rule": "max(1 N, 10 times largest observed refined minimum difference)",
                             "energy_increment_rule": "1e-10 * max(1 J, energy at exit)"},
              "checks": checks, "comparisons": comparisons, "runs": diagnostics, "final": final,
              "zero_max_abs_state": maximum_zero_state,
              "exit_state_max_abs_difference": max(exit_state_errors),
              "environment": environment, "input_sha256": hashes}
    (output / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (output / "environment.json").write_text(json.dumps(environment, indent=2) + "\n", encoding="utf-8")
    # Readable 1 ms trace, with separate full-resolution data for the final metrics.
    t, q = extended10.sample(0.001)
    np.savetxt(output / "nominal_trace_1ms.csv",
               np.column_stack((t, road_height(t, bump), q.T, q[0] - q[2], contact_force(t, q, parameters, bump))),
               delimiter=",", header="time_s,road_m,zs_m,vs_m_s,zu_m,vu_m_s,relative_m,contact_N", comments="")
    fine_t, fine_q = extended10.sample(0.00025)
    np.savez_compressed(output / "nominal_trace_0p25ms.npz", time_s=fine_t, state=fine_q)
    make_plots(extended10, final, output)

    peak_direction = "extension" if final["A_signed_m"] >= 0 else "compression"
    lines = ["# Nominal simulation: initial check results", "",
             "Generated by `python run_nominal.py`. This is a technical checkpoint, not the assessed report.", "",
             f"Overall initial checks: **{'PASS' if all(checks.values()) else 'FAIL'}**.", "",
             f"- Full-response A: **{final['A_m']*1000:.6f} mm**, at {final['A_time_s']:.5f} s ({peak_direction}).",
             f"- Post-bump A_post: **{final['A_post_m']*1000:.6f} mm**, at {final['A_post_time_s']:.5f} s.",
             f"- Settling status: **{final['settling_status']}**; after-exit time [s]: {final['settling_after_exit_s']}.",
             "- Settling refers only to zs-zu within ±1 mm, with at least 1 s confirmation plus tail/refinement/extension checks.",
             f"- Minimum sampled total contact force: **{final['minimum_contact_N']:.6f} N**; numerical margin {contact_margin:.6f} N.",
             "", "## Actual checks", "", "| Check | Result |", "|---|---|"]
    lines += [f"| {name} | {'PASS' if passed else 'FAIL'} |" for name, passed in checks.items()]
    lines += ["", "Unit-test output: [unit_tests.txt](unit_tests.txt).", "",
              "## Refinement comparisons", "",
              "Limits: peak differences ≤0.05 mm; settling differences ≤0.01 s with matching candidate status.", "",
              "| Comparison | ΔA [mm] | ΔA_post [mm] | Δsettling [s] |", "|---|---:|---:|---:|"]
    lines += [f"| {name} | {c['A_difference_mm']:.9g} | {c['A_post_difference_mm']:.9g} | {c['settling_difference_s']} |"
              for name, c in comparisons.items()]
    lines += ["", "## Tail, energy and work", "",
              "Energy increment allowance is 1e-10 times max(1 J, exit energy); it allows numerical noise, not physical energy growth.", "",
              "| Run | Tail bound [mm] | Max positive energy increment [J] | Derivative calls | Integration [s] |",
              "|---|---:|---:|---:|---:|"]
    lines += [f"| {name} | {d['tail_bound_m']*1000:.9g} | {d['maximum_energy_increase_J']:.9g} | {d['derivative_evaluations']} | {d['integration_runtime_s']:.6f} |"
              for name, d in diagnostics.items()]
    lines += ["", "Grid variants reuse the same integrated trajectory; their integration timings are the same measurement, not independent benchmarks.",
              ("Both nonzero peaks exceed twice the final tail bound. The 5 s nominal observation was sufficient under these initial checks; 10 s is retained as confirmation."
               if numerical_prerequisites and checks["extended_observation"]
               else "Tail/horizon confirmation failed: extend or investigate before using unresolved outputs."),
              "", "## Limits and next checks", "",
              "These are numerical and nominal model-consistency checks, not real-vehicle validation or certified continuous-time error bounds.",
              "Remaining: the nine-setup pilot programme, classical RK4 comparison, reduced analytical oscillator, settling-band sensitivity, full-domain contact and per-run tail checks.",
              "No full dataset, ML fitting, telemetry calibration or assessed report has been started.",
              "The 1 ms CSV is for easy inspection; the final metrics use 0.25 ms samples saved in the NPZ file.",
              "Exact configuration, package versions, source hashes and all values are in summary.json.", ""]
    (output / "CHECK_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"checks": checks, "final": final}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
