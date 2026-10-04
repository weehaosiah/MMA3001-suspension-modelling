"""Display the predeclared final-test comparison, without fitting any model."""

import os
from pathlib import Path

import numpy as np

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def create_outputs(output, test, predictions, result):
    """Save parity/residual plots and readable final evaluation evidence."""
    x, y = test["X"], test["y"]
    values = np.concatenate([y, *predictions.values()])
    limits = (values.min()-.3, values.max()+.3)
    residual_limit = max(1e-9, max(np.max(abs(y-p)) for p in predictions.values())*1.12)
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 7.3), layout="constrained")
    for row, (key, title, color) in enumerate((("linear", "Linear comparator", "#a75d28"),
                                               ("svr", "Development-selected SVR", "#176b9b"))):
        p = predictions[key]
        ax = axes[row, 0]
        ax.scatter(y, p, s=22, color=color, alpha=.8)
        ax.plot(limits, limits, "k--", lw=1)
        ax.set(xlim=limits, ylim=limits, xlabel="Simulated peak A [mm]", ylabel="Predicted peak A [mm]",
               title=f"{title} | test RMSE {result['test_metrics'][key]['RMSE_mm']:.4f} mm")
        for col, values, xlabel in ((1, x[:, 0]/1000, "Stiffness [kN/m]"), (2, x[:, 1], "Damping [N s/m]")):
            ax = axes[row, col]
            ax.scatter(values, y-p, s=22, color=color, alpha=.8)
            ax.axhline(0, color="black", lw=1)
            ax.set(xlabel=xlabel, ylabel="Simulation - prediction [mm]", ylim=(-residual_limit, residual_limit))
    for ax in axes.flat:
        ax.grid(alpha=.18)
    fig.suptitle("Final evaluation: same 100 reserved setups | both models refitted on 300 development rows", fontsize=13)
    fig.savefig(output / "final_test_comparison.png", dpi=150)
    plt.close(fig)
    lines = ["# Final evaluation checkpoint", "", "Working check documentation, not the assessed report.", "",
             "Model choices were frozen before test access. Both pipelines were fitted on the same 300 original development rows and scored on all 100 reserved test cases.", "",
             "The preferred model remains the development-selected RBF SVR: C=100, gamma=1, epsilon=0.05 mm. Test results did not select new settings.", "",
             "The target is max abs(zs-zu) from static equilibrium over the full bump and post-bump response, in millimetres.", "",
             "| Model | Test RMSE [mm] | Test MAE [mm] | Largest absolute error [mm] | Largest underprediction [mm] | R2 |",
             "|---|---:|---:|---:|---:|---:|"]
    for key, label in (("linear", "Linear comparator"), ("svr", "Development-selected SVR")):
        m = result["test_metrics"][key]
        r2 = "undefined (constant target)" if m["R2"] is None else f"{m['R2']:.9f}"
        lines.append(f"| {label} | {m['RMSE_mm']:.6f} | {m['MAE_mm']:.6f} | {m['max_absolute_error_mm']:.6f} | {m['max_underprediction_mm']:.6f} | {r2} |")
    lines += ["", "## Actual checks", ""]
    lines += [f"- {key}: **{'PASS' if passed else 'FAIL'}**." for key, passed in result["checks"].items()]
    lines += ["- Each new scaler used 300 development rows. Validation is now part of fitting, so development-fit errors are not new validation scores.",
              "- Test identities, unit conversion, physical parameters, per-row eligibility and file fingerprints were checked; no row was omitted.",
              "- The plan, two fitted models and refit completion were saved before first test-response access. test_access.json preserves the access time.",
              "- Exact test output, fit/support counts, regional metrics, target spread and fingerprints are saved alongside these results.",
              "- Model reload checks and timing used development inputs before opening the test; the test was not used for tuning or repeated benchmarking.",
              "", "## Interpretation and reproduction", "",
              "Residual = simulated A minus predicted A, so positive means underprediction. The largest observed test error is not a worst-case guarantee over all possible setups.",
              "These scores measure agreement with the existing numerical dataset, not vehicle measurements. Numerical/model assumptions and physical travel clearances remain separate uncertainties.",
              "Post-bump peak and settling remain supporting physics diagnostics; see the preserved training-physics plots. They were not added as ML targets/features.",
              "Run `python final_evaluation.py audit` to verify saved final artifacts and recompute scores, without refitting or reopening original test responses.",
              "The reserved test has now been used. Further changes chosen after seeing these scores are development; they cannot reuse this set as a fresh independent final test.", ""]
    (output / "CHECK_RESULTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
