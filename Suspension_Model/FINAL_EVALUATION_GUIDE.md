# Final evaluation guide

This is working project documentation to help you understand and reproduce the code, not assessed report prose.

See [REPRODUCING.md](REPRODUCING.md) for current saved-result commands, the Windows
environment and excluded course originals required by strict source checks.

The final comparison is complete. Two models were fitted on the same 300 development cases and evaluated on the 100 previously reserved test cases. The test set has now been used; it is no longer an unseen set for future model choices.

Start with [the saved check results](final_evaluation_v1/CHECK_RESULTS.md) and [the comparison figure](final_evaluation_v1/final_test_comparison.png). The [machine-readable summary](final_evaluation_v1/summary.json) preserves the full results. Function documentation is available for [final_evaluation.py](docs/final_evaluation.html) and [final_plots.py](docs/final_plots.html).

## What the models predict

One input row describes one suspension setup: spring stiffness `ks` in N/m and damping coefficient `cs` in N s/m. The other physical parameters and road bump remain fixed as recorded in [the dataset guide](DATASET.md).

The output is `A_mm = 1000 * max(abs(zs - zu))`: the greatest magnitude of relative body-to-wheel movement, measured from static equilibrium, across the whole simulated response, including after the bump. `zs` is body displacement and `zu` is wheel displacement. Multiplying metres by 1000 expresses the answer in millimetres.

The post-bump peak and settling time remain important physics diagnostics. They help explain what happens after the wheel leaves the bump; they are not extra input features or prediction targets. Their saved plots and checks remain in the earlier checkpoints.

## What was fixed before opening the test

Decision D009 selected RBF support-vector regression (SVR), development candidate `svr_15`, with `C=100`, `gamma=1`, and `epsilon=0.05 mm`. These settings control the fitted curve's error penalty, local influence, and error-insensitive band. They were selected from the original 18-setting comparison using validation evidence; they are not a claim of globally optimal settings.

The final stage retained that preferred method and a linear-regression comparator. It did not search again. The linear model describes a plane across the two inputs; SVR can describe a curved relationship. A linear differential equation in displacement does not imply that its largest response varies linearly with spring and damping coefficients.

Both models received fresh fits using the original 225 training rows followed by the original 75 validation rows. The tighter validation simulations were numerical-sensitivity checks; their labels did not replace the original dataset labels.

Each model is a pipeline: a saved sequence containing a `StandardScaler` followed by its regressor. The scaler learns means and scales from the same 300 development rows. The target remains in millimetres. Test prediction reuses these learned quantities without updating them. Earlier 225-row models and result folders remain preserved. Errors on the refitted 300 rows are fitting errors, not new validation scores.

## The three commands

| Command | What it does | Test-response access |
|---|---|---|
| `prepare` | Checks the recorded choice and environment, saves the plan, runs tests, fits two fresh 300-row pipelines, checks model reloads, and saves their fingerprints. | Does not read reserved response files. |
| `evaluate` | Checks the frozen plan and fitted models, records first access, validates all 100 rows, predicts once, and saves scores and the figure. | Opens the original reserved responses after preparation. |
| `audit` | Checks fingerprints and recalculates saved aggregate scores from saved targets and predictions. | Does not reopen the original reserved response files or refit models. |

A fingerprint is a SHA-256 checksum: a value used to detect changed file contents. The plan binds the evaluation to specific code, data, settings, and model files. It is a reproducibility check, not proof that the physical model is correct.

Before opening test responses, `evaluate` creates `test_access.json`. This marker remains even if a later check fails, preserving evidence that access began. A second evaluation in that folder is refused. Do not delete the marker to make the test appear unused. Preserve a failed checkpoint and investigate its cause.

The workflow checks all test identities, units, physical parameters, and saved numerical eligibility. It stops on inconsistent or invalid data instead of silently dropping a case. The preferred model stays the one selected during development, even if a final comparison were to favour the linear model.

## Actual checkpoint results

All 385 implementation tests passed. The final evaluation's five checks passed: all 100 cases matched and were valid; scalers stayed unchanged; predictions were finite; predictions were positive on these cases; and frozen sources, inputs, and models remained unchanged. The separate saved-artifact audit passed.

| Model | Test RMSE (mm) | Test MAE (mm) | Largest absolute error (mm) | Largest underprediction (mm) |
|---|---:|---:|---:|---:|
| Linear comparator | 0.199436 | 0.161225 | 0.435026 | 0.435026 |
| Development-selected SVR | 0.029796 | 0.026311 | 0.051826 | 0.051696 |

MAE is the average absolute prediction error. RMSE squares errors before averaging and taking a square root, so larger errors have greater influence. A residual is simulated `A` minus predicted `A`; a positive residual means the prediction is too small. The saved summary also includes mean residual, R-squared, and results in the four predeclared parameter regions.

These checks establish that the declared evaluation completed consistently. They are not a universal engineering acceptance threshold. The largest observed error describes these 100 cases; it is not a guaranteed maximum across every possible setup.

## Check the saved results on this laptop

Open PowerShell and run these commands. The leading `&` tells PowerShell to run the program at the quoted path.

```powershell
Set-Location 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\Suspension_Model'
& 'C:\Users\dedvu\anaconda3\python.exe' final_evaluation.py audit
```

This is the appropriate command for checking the completed checkpoint again. It reads the saved evaluation artifacts; it does not train again or request another final-test evaluation. Changed frozen source files or artifacts make the audit fail rather than silently accept a different checkpoint.

For an intentional reproduction in a new folder, the commands are:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' final_evaluation.py prepare --output final_evaluation_recheck
& 'C:\Users\dedvu\anaconda3\python.exe' final_evaluation.py evaluate --output final_evaluation_recheck
& 'C:\Users\dedvu\anaconda3\python.exe' final_evaluation.py audit --output final_evaluation_recheck
```

Run each command only after the previous command succeeds. `prepare` refuses an existing output folder. Keep `final_evaluation_v1` and all earlier folders intact. These commands reproduce results using known test data; a new folder does not create a new independent test. The once-only marker applies within a checkpoint, while the scientific restriction on reusing an exposed test applies across checkpoints too. This fresh-folder recipe has not been executed as a second full final run.

The recorded environment is the existing Anaconda Python 3.12.7 with NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.5.1, joblib 1.4.2, threadpoolctl 3.5.0, Matplotlib 3.9.2, and pytest 7.4.4. [requirements-ml.txt](requirements-ml.txt) includes [the simulation requirements](requirements.txt). No new package installation or fresh-environment reproduction is claimed. Preparation checks the exact saved Python version and numerical/ML package versions; a changed environment needs a reviewed artifact-refresh workflow, not bypassed guards.

## Where the evidence is saved

| File in `final_evaluation_v1` | Purpose |
|---|---|
| [frozen_plan.json](final_evaluation_v1/frozen_plan.json) | Declared models, inputs, target, metrics, row identities, environment, and fingerprints before test access. |
| [refit.json](final_evaluation_v1/refit.json) | Both 300-row fits, scaler statistics, support-vector count, reload checks, model fingerprints, and measured timings. |
| `linear.joblib`, `svr.joblib` | Saved fitted pipelines; local trusted project artifacts. |
| [test_access.json](final_evaluation_v1/test_access.json) | First-access time and the frozen plan/model identities. |
| [test_predictions.csv](final_evaluation_v1/test_predictions.csv) | Every test input, simulated target, prediction, and signed residual. |
| [summary.json](final_evaluation_v1/summary.json) | Full aggregate and regional scores, checks, limits, and artifact fingerprints. |
| [unit_tests.txt](final_evaluation_v1/unit_tests.txt) | Saved implementation-test output. |
| [CHECK_RESULTS.md](final_evaluation_v1/CHECK_RESULTS.md) and [figure](final_evaluation_v1/final_test_comparison.png) | Readable results and visual comparison. |

Prediction timing used 30 warmed batches of all 300 development inputs at one numerical thread, before test access. The reused timing helper's generic scope text says “validation batch”; the actual count, `prediction_timing_on_development` field, and frozen plan specify the 300-row development batch. These timings do not establish overall speedup or break-even cost against simulation.

## Limits and what follows

These errors compare predictions with the existing numerical quarter-car labels, not measurements from a real car. The studied rectangle is `ks = 18,000–30,000 N/m` and `cs = 1,594.8–2,658.0 N s/m`, with the other model and bump settings fixed. The result does not establish accuracy outside that domain or for different physical assumptions.

The earlier nine-pilot verification and 75 tighter validation calculations remain supporting numerical evidence. The latter did not certify numerical errors at all final-test locations. Continuous-domain behaviour, real-vehicle validity, physical clearances, and end-to-end runtime benefits remain open questions.

Further settings chosen after seeing these test scores count as development. Reusing these same 100 cases would not provide a fresh independent final assessment. This stage adds no test-driven retuning, new dataset generation, or assessed report writing.

## Source basis

The workflow follows the actual local Week05_5 notebook, cells 16 and 36–37, on split roles, freezing a choice, refitting development data, and final testing; and Week05_6, cells 28–30, on keeping learned preprocessing inside the fitted pipeline. Cell numbers are one-based positions in the saved notebooks. Project-specific decisions are P008/D009 and the authorised final-stage checkpoint recorded in [PROJECT_STATE.md](../Project_Setup/PROJECT_STATE.md), revision 018.

The 15-page local project brief, especially pages 5–6, requires credible baseline evidence, justified evaluation and limitations, and disclosure of material AI assistance. The notebooks have no separately stated revision number; frozen-plan fingerprints identify the versions used. Earlier scikit-learn API review used the installed 1.5.1 package; the archived official 1.5 documentation displays 1.5.2. The implementation, source audit, checks, and material AI assistance are recorded separately in [EVIDENCE.md](../Project_Setup/EVIDENCE.md) and [AI_USE_LOG.md](../Project_Setup/AI_USE_LOG.md).
