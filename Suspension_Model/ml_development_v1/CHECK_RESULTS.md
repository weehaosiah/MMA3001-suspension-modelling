# ML development check results

Working experiment documentation, not the assessed report.

This comparison fits 225 training setups and selects using 75 validation setups. Final-test responses remain reserved.

The only target is the full-response max abs(zs-zu), from static equilibrium, in millimetres, including post-bump motion.

| Model | Training RMSE [mm] | Validation RMSE [mm] | Validation MAE [mm] | Largest absolute error [mm] | Largest underprediction [mm] |
|---|---:|---:|---:|---:|---:|
| Linear regression | 0.220778 | 0.199456 | 0.159690 | 0.485281 | 0.485281 |
| Selected RBF SVR | 0.034579 | 0.031088 | 0.027277 | 0.059600 | 0.059600 |

Selected SVR: C=100, gamma=1, epsilon=0.05 mm; 49 support vectors from 225 training rows.
Preferred development model by predeclared validation RMSE: **svr_15**.

## Checks and interpretation

- All 19 pipelines fit the same 225 training rows; each scaler is checked against those rows and unchanged after prediction.
- All 18 declared SVR settings are retained in candidates.json/candidate_comparison.csv; no search expansion or extra model family.
- Dataset hashes, identities, units and raw validity are checked before fitting. Failure is not repaired by dropping a row.
- Saved linear and selected-SVR pipelines reproduce validation predictions exactly after reload.
- Exact check flags, training/validation target spread, regional errors, convergence and measured work are in summary.json; test output is in unit_tests.txt.
- Residual = simulation minus prediction. Positive values mean underprediction; the largest observed error is not a bound over all possible setups.
- Selection uses this validation split and limited search. No universal engineering accuracy threshold or independent final-test result is claimed.
- The 0.05 mm numerical agreement criterion is not a certified label-error bar. The saved pilot comparisons are the numerical evidence.
- Training physics maps retain post-bump peak and settling as supporting diagnostics, not features or extra ML targets.

## Reproduction and next stage

Run `python ml_development.py --output ml_development_recheck` from Suspension_Model with requirements-ml.txt's recorded environment. Existing output folders are refused.
No scaler/model was refitted on all 300 development rows, no final-test responses were read or predictions made, and no assessed report was written.
Review this development choice before the later refit and one-time final evaluation. Prediction timings include scaling but exclude simulation/data-generation costs; no overall speedup is established.
