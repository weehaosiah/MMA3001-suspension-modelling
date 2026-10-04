# Final evaluation checkpoint

Working check documentation, not the assessed report.

Model choices were frozen before test access. Both pipelines were fitted on the same 300 original development rows and scored on all 100 reserved test cases.

The preferred model remains the development-selected RBF SVR: C=100, gamma=1, epsilon=0.05 mm. Test results did not select new settings.

The target is max abs(zs-zu) from static equilibrium over the full bump and post-bump response, in millimetres.

| Model | Test RMSE [mm] | Test MAE [mm] | Largest absolute error [mm] | Largest underprediction [mm] | R2 |
|---|---:|---:|---:|---:|---:|
| Linear comparator | 0.199436 | 0.161225 | 0.435026 | 0.435026 | 0.994253867 |
| Development-selected SVR | 0.029796 | 0.026311 | 0.051826 | 0.051696 | 0.999871739 |

## Actual checks

- all_100_rows_valid_and_matched: **PASS**.
- scalers_unchanged_after_test: **PASS**.
- predictions_finite: **PASS**.
- predictions_positive_on_test: **PASS**.
- frozen_sources_inputs_models_unchanged: **PASS**.
- Each new scaler used 300 development rows. Validation is now part of fitting, so development-fit errors are not new validation scores.
- Test identities, unit conversion, physical parameters, per-row eligibility and file fingerprints were checked; no row was omitted.
- The plan, two fitted models and refit completion were saved before first test-response access. test_access.json preserves the access time.
- Exact test output, fit/support counts, regional metrics, target spread and fingerprints are saved alongside these results.
- Model reload checks and timing used development inputs before opening the test; the test was not used for tuning or repeated benchmarking.

## Interpretation and reproduction

Residual = simulated A minus predicted A, so positive means underprediction. The largest observed test error is not a worst-case guarantee over all possible setups.
These scores measure agreement with the existing numerical dataset, not vehicle measurements. Numerical/model assumptions and physical travel clearances remain separate uncertainties.
Post-bump peak and settling remain supporting physics diagnostics; see the preserved training-physics plots. They were not added as ML targets/features.
Run `python final_evaluation.py audit` to verify saved final artifacts and recompute scores, without refitting or reopening original test responses.
The reserved test has now been used. Further changes chosen after seeing these scores are development; they cannot reuse this set as a fresh independent final test.
