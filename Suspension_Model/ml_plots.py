"""Development-only figures and check tables; no dataset or test-file loading."""

import csv
import os
from pathlib import Path

import numpy as np

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from ml_development import metrics, predict_checked


def create_outputs(output, data, records, models, decision):
    """Save honest validation comparisons and training-only physics maps.

    Residual sign is simulation minus prediction. Each map uses already-simulated
    training summaries, not an extra target/model or a fresh simulation.
    """
    best_id = decision["best_svr_id"]
    selected = [("linear", "Linear regression", "#a75d28"),
                (best_id, "Selected RBF SVR", "#176b9b")]
    validation = data["validation"]
    x, y = validation["X"], validation["y"]
    predictions = {key: predict_checked(models[key], x) for key, _, _ in selected}
    all_values = np.concatenate([y, *predictions.values()])
    limits = (all_values.min() - 0.3, all_values.max() + 0.3)
    residual_limit = max(np.max(abs(y - p)) for p in predictions.values()) * 1.12
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 7.3), layout="constrained")
    for row, (key, label, color) in enumerate(selected):
        p = predictions[key]
        axes[row, 0].scatter(y, p, s=22, color=color, alpha=0.8)
        axes[row, 0].plot(limits, limits, "k--", lw=1)
        score = metrics(y, p)
        axes[row, 0].set(xlim=limits, ylim=limits, xlabel="Simulated peak A [mm]",
                         ylabel="Predicted peak A [mm]", title=f"{label} | RMSE {score['RMSE_mm']:.4f} mm")
        for col, values, xlabel in ((1, x[:, 0] / 1000, "Stiffness [kN/m]"),
                                    (2, x[:, 1], "Damping [N s/m]")):
            axes[row, col].scatter(values, y-p, s=22, color=color, alpha=0.8)
            axes[row, col].axhline(0, color="black", lw=1)
            axes[row, col].set(xlabel=xlabel, ylabel="Simulation - prediction [mm]",
                               ylim=(-residual_limit, residual_limit))
    for ax in axes.flat:
        ax.grid(alpha=0.18)
    fig.suptitle("75 validation setups | positive residual means underprediction", fontsize=14)
    fig.savefig(output / "validation_comparison.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.3, 4.3), layout="constrained", sharex=True, sharey=True)
    norm = Normalize(vmin=-residual_limit, vmax=residual_limit)
    for ax, (key, label, _) in zip(axes, selected):
        sc = ax.scatter(x[:, 0]/1000, x[:, 1], c=y-predictions[key], cmap="coolwarm", norm=norm, s=42)
        ax.set(title=label, xlabel="Stiffness [kN/m]", ylabel="Damping [N s/m]")
        ax.grid(alpha=0.15)
    fig.colorbar(sc, ax=axes, label="Simulation - prediction [mm]")
    fig.suptitle("Validation errors across the two-input domain | same colour scale")
    fig.savefig(output / "validation_error_locations.png", dpi=150)
    plt.close(fig)

    train = data["train"]
    raw = [d["raw_summary"] for d in train["diagnostics"]]
    fields = [(train["y"], "Full-response peak A", "mm"),
              (np.array([d["A_post_m"] * 1000 for d in raw]), "Post-bump peak", "mm"),
              (np.array([d["validity"]["settling_after_exit_s"] for d in train["diagnostics"]], dtype=float),
               "Relative settling after exit", "s")]
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2), layout="constrained", sharex=True, sharey=True)
    for ax, (values, label, unit) in zip(axes, fields):
        # Mask unresolved settling instead of replacing it with a cutoff time.
        grid = np.ma.masked_invalid(values.reshape(15, 15))
        plot = ax.contourf(train["X"][:, 0].reshape(15, 15)/1000,
                           train["X"][:, 1].reshape(15, 15), grid, levels=14, cmap="viridis")
        ax.set(title=label, xlabel="Stiffness [kN/m]")
        fig.colorbar(plot, ax=ax, label=unit)
    axes[0].set_ylabel("Damping [N s/m]")
    fig.suptitle("225 simulated training setups | post-bump outputs remain supporting diagnostics")
    fig.savefig(output / "training_physics.png", dpi=150)
    plt.close(fig)

    columns = ["model_id", "family", "C", "gamma", "epsilon_mm", "train_RMSE_mm", "validation_RMSE_mm",
               "validation_MAE_mm", "validation_max_absolute_error_mm", "validation_max_underprediction_mm",
               "support_vectors", "fit_seconds"]
    with (output / "candidate_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for r in records:
            writer.writerow([r["model_id"], r["family"], r.get("C"), r.get("gamma"), r.get("epsilon"),
                             r["training"]["RMSE_mm"], r["validation"]["RMSE_mm"], r["validation"]["MAE_mm"],
                             r["validation"]["max_absolute_error_mm"], r["validation"]["max_underprediction_mm"],
                             r["support_vectors"], r["fit_seconds"]])
    regional = {}
    for key, _, _ in selected:
        regional[key] = {}
        for klow, clow in ((True, True), (True, False), (False, True), (False, False)):
            mask = ((x[:, 0] < 24000) if klow else (x[:, 0] >= 24000)) & (
                    (x[:, 1] < 2126.4) if clow else (x[:, 1] >= 2126.4))
            name = f"ks_{'lower' if klow else 'upper'}_cs_{'lower' if clow else 'upper'}"
            regional[key][name] = metrics(y[mask], predictions[key][mask]) if mask.any() else {"n": 0}
    by_id = {r["model_id"]: r for r in records}
    lines = ["# ML development check results", "", "Working experiment documentation, not the assessed report.", "",
             "This comparison fits 225 training setups and selects using 75 validation setups. Final-test responses remain reserved.", "",
             "The only target is the full-response max abs(zs-zu), from static equilibrium, in millimetres, including post-bump motion.", "",
             "| Model | Training RMSE [mm] | Validation RMSE [mm] | Validation MAE [mm] | Largest absolute error [mm] | Largest underprediction [mm] |",
             "|---|---:|---:|---:|---:|---:|"]
    for key, label, _ in selected:
        r, m = by_id[key], by_id[key]["validation"]
        lines.append(f"| {label} | {r['training']['RMSE_mm']:.6f} | {m['RMSE_mm']:.6f} | {m['MAE_mm']:.6f} | {m['max_absolute_error_mm']:.6f} | {m['max_underprediction_mm']:.6f} |")
    settings = decision["best_svr_settings"]
    lines += ["", f"Selected SVR: C={settings['C']:g}, gamma={settings['gamma']:g}, epsilon={settings['epsilon']:g} mm; {by_id[best_id]['support_vectors']} support vectors from 225 training rows.",
              f"Preferred development model by predeclared validation RMSE: **{decision['preferred_model_id']}**.", "",
              "## Checks and interpretation", "",
              "- All 19 pipelines fit the same 225 training rows; each scaler is checked against those rows and unchanged after prediction.",
              "- All 18 declared SVR settings are retained in candidates.json/candidate_comparison.csv; no search expansion or extra model family.",
              "- Dataset hashes, identities, units and raw validity are checked before fitting. Failure is not repaired by dropping a row.",
              "- Saved linear and selected-SVR pipelines reproduce validation predictions exactly after reload.",
              "- Exact check flags, training/validation target spread, regional errors, convergence and measured work are in summary.json; test output is in unit_tests.txt.",
              "- Residual = simulation minus prediction. Positive values mean underprediction; the largest observed error is not a bound over all possible setups.",
              "- Selection uses this validation split and limited search. No universal engineering accuracy threshold or independent final-test result is claimed.",
              "- The 0.05 mm numerical agreement criterion is not a certified label-error bar. The saved pilot comparisons are the numerical evidence.",
              "- Training physics maps retain post-bump peak and settling as supporting diagnostics, not features or extra ML targets.", "",
              "## Reproduction and next stage", "",
              "Run `python ml_development.py --output ml_development_recheck` from Suspension_Model with requirements-ml.txt's recorded environment. Existing output folders are refused.",
              "No scaler/model was refitted on all 300 development rows, no final-test responses were read or predictions made, and no assessed report was written.",
              "Review this development choice before the later refit and one-time final evaluation. Prediction timings include scaling but exclude simulation/data-generation costs; no overall speedup is established.", ""]
    (output / "CHECK_RESULTS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return regional
