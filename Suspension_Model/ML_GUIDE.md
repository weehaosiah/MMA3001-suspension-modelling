# Understanding the ML development comparison

This guide explains the implemented training/validation workflow. Actual results
belong in [CHECK_RESULTS.md](ml_development_v1/CHECK_RESULTS.md) and
[summary.json](ml_development_v1/summary.json), including the final `complete`
flag. The first development run completed on 5 October 2026, with all 19 fits
converged and 343 tests passing. Validation RMSE was **0.199456 mm for linear
regression** and **0.031088 mm for the selected SVR** (C=100, gamma=1,
epsilon=0.05 mm, 49 support vectors). These are development scores, not final-test
accuracy. The leading SVR settings were close, so a separate tighter-reference
check is documented below.

## What is being predicted?

One sample is one full suspension setup, with stiffness `ks_N_m` and damping
`cs_N_s_m` as its only prediction inputs. The target `A_mm` is the largest absolute
body-minus-wheel displacement over the complete checked response, including after
the bump. It is measured from static equilibrium and expressed in millimetres.
It excludes static sag and is not peak-to-peak travel.

The simulations supply the target values. Learning to reproduce them does not
validate the model against a real car. Post-bump peak, settling, tyre force and
energy remain supporting diagnostics; they do not become prediction inputs or
extra ML targets. See [DATASET.md](DATASET.md) for the row and unit definitions.

## Two ways to learn the relationship

**Linear regression** fits a plane: `A_hat = b0 + b1*ks + b2*cs`. The coefficients
are learned from the training data. This is the simple comparison model. Although
the physical motion equations are linear in displacement and velocity, that does
not make their maximum response linear in stiffness and damping. Changing a
coefficient changes the whole motion, and the time of the largest peak can change.

**RBF support-vector regression (SVR)** fits a curved relationship using similarity
between input pairs. A support vector is a training row retained in the fitted
solution. The recorded count describes how many of the 225 rows are retained; it
is not an accuracy score or uncertainty estimate. Smooth predictions alone do not
establish physical correctness or justify extrapolation.

Each model is a **pipeline**: a reusable sequence consisting of an input scaler
followed by a regressor. `StandardScaler` subtracts each input's training mean and
divides by its training standard deviation. Otherwise, numerical units could
dominate the RBF distance calculation. Both models get their own scaler, fitted
only on the same 225 training rows. Prediction reuses that scaler without fitting
it again. The target stays in millimetres; it is not standardised.

## How settings are selected

The code fits one linear model and all 18 predeclared SVR combinations:

| Setting | Values | Meaning |
|---|---|---|
| `C` | 1, 10, 100 | Trade-off between a flatter fit and errors outside the tube |
| `gamma` | 0.1, 1, 10 | How rapidly similarity falls with scaled input distance |
| `epsilon` | 0.05, 0.20 mm | Half-width of the training loss's no-penalty tube |

Epsilon is not a guaranteed prediction error, solver tolerance or settling band.
The solver settings, including SVR tolerance 0.001, are saved in the development
plan. Every candidate uses the same 75 validation rows for comparison. None fits
those rows. The lowest validation RMSE selects the preferred development model.
Exact ties favour linear regression; SVR ties use ascending C, gamma, then epsilon.
Failed candidates are recorded and block selection until investigated.

The selected candidate is best within this limited search and validation sample,
not a global optimum. The code does not expand the search or add model families.
Small differences need cautious interpretation: the pilot 0.05 mm numerical
agreement criterion is not a certified error bar on every simulation label.

## Reading the errors and figures

A **residual** here is `simulated A - predicted A`; positive means underprediction.

| Measure | Interpretation |
|---|---|
| MAE [mm] | Mean absolute difference; a typical error size |
| RMSE [mm] | Square root of mean squared error; larger errors count more heavily |
| Maximum absolute error [mm] | Largest difference among the inspected cases |
| Maximum underprediction [mm] | Largest positive residual, or zero if none |
| Mean residual [mm] | Average signed error; helps show bias |
| R² | Supplementary comparison with the evaluation-set mean; not an error tolerance |

Training errors describe fit to already-seen cases. Validation errors support
development choices at new coefficient pairs. Neither is an independent final-test
result, and a sampled maximum is not a guarantee over the entire input rectangle.

- [Validation comparison](ml_development_v1/validation_comparison.png): predictions
  versus simulated peaks and residuals against each input, with shared error limits.
- [Error locations](ml_development_v1/validation_error_locations.png): the same
  validation residuals across the two-input domain, using one colour scale.
- [Training physics](ml_development_v1/training_physics.png): simulated primary peak,
  post-bump peak and settling from the existing 225-row grid. Contours visually
  interpolate between samples; they are not extra simulations or trained targets.

The summary also groups validation errors into four regions divided at the nominal
stiffness and damping. Counts accompany regional metrics; no final-test responses
are used. The physical interpretation remains limited to the fixed generic model,
bump and coefficient domain.

## Saved outputs and checks

| File in `ml_development_v1/` | Purpose |
|---|---|
| [development_plan.json](ml_development_v1/development_plan.json) | Settings and source/data/environment identities saved before fitting |
| [candidates.json](ml_development_v1/candidates.json), [candidate_comparison.csv](ml_development_v1/candidate_comparison.csv) | All 19 fits, metrics, support counts and measured fitting work |
| [development_decision.json](ml_development_v1/development_decision.json) | Selected SVR and preferred development model |
| `train_predictions.csv`, `validation_predictions.csv` | IDs, inputs, simulated targets, predictions and signed residuals |
| `linear.joblib`, `svr_XX.joblib` | Saved fitted pipelines; XX identifies the selected SVR |
| [summary.json](ml_development_v1/summary.json), `unit_tests.txt` | Completion/check flags, exact metrics, work and test output |

The loader checks development-file hashes, identities, units and eligibility. It
does not repair failures by dropping rows. Checks cover convergence, training-only
scaling, unchanged scaling during prediction, finite predictions, positivity on
validation cases and identical predictions after reloading the saved pipelines.
Source, dataset and predeclared-plan fingerprints are checked again at completion.
Use the checked prediction helper to reject queries outside the adopted domain.

Fitting time includes scaling. Prediction timing uses three warm-ups and 30 timed
75-row validation batches, with numerical thread pools limited to one. It includes
input checks, scaling and regression, but excludes file reading and simulation
costs. These timings do not establish an overall speed advantage or break-even cost.

## Reproduce on this laptop

From PowerShell, use the existing Anaconda environment:

```powershell
Set-Location -LiteralPath 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\Suspension_Model'
& 'C:\Users\dedvu\anaconda3\python.exe' ml_development.py --output ml_development_recheck
```

Choose a new output directory each time; existing folders are refused. The input
dataset is preserved. [requirements-ml.txt](requirements-ml.txt) records the existing
simulation packages plus scikit-learn 1.5.1, joblib 1.4.2 and threadpoolctl 3.5.0.
This recipe is not evidence of a second run or a fresh-environment installation.
The recorded official scikit-learn 1.5 documentation displays version 1.5.2; the
installed package is 1.5.1. Preserve that distinction in source and runtime records.

## Stage boundary and course basis

`ml_reference_check.py` follows P008's instruction to check numerical sensitivity
when model scores are close. It recalculates only the 75 validation responses at
tighter RK45 tolerances, a 10 s horizon and 0.25 ms observations. The original
dataset and fitted models are preserved; these are verification runs, not new
training rows. See [the supplementary check](ml_reference_v1/summary.json) for
actual completion, target changes and results. Reproduce in a fresh folder with:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' ml_reference_check.py --output ml_reference_recheck
```

For fixed predictions, changing the reference labels can change RMSE by at most
the root-mean-square label change. If the original gap between the two best
scores is greater than twice that change, their ranking survives this reference
replacement. This checks sensitivity to two numerical approximations, not an
exact continuous-time error bound or statistical confidence interval.

The supplementary run completed with **353 tests passing** and all 75 reference
checks passing. Maximum peak-label change was 0.000678 mm; RMS change was
0.0003104 mm. The 0.0013984 mm gap to the next candidate exceeds twice that RMS
change, so the same fitted SVR remains preferred under the refined reference.
Its refined-reference RMSE is 0.031081 mm, versus 0.199469 mm for linear regression.
This does not test retraining with refined training labels or a different split.

The production loader opens training/validation responses and common input metadata.
It does not open reserved final-test response files. The saved models remain fitted
on 225 rows: there is no 300-row refit or final-test evaluation in this stage.
Review the development evidence before that later step. These are working code,
data and check documents, not the assessed report.

The actual local course sections were read before adaptation: Week05_1 cells 4,
14-15 and 25-26; Week05_3 cells 5, 13-15, 18, 22, 27-31, 34, 41 and 45;
Week05_5 cells 6, 9, 16-17, 23-24, 28, 31-32 and 36-37; Week05_6 cells 4,
13, 15, 19, 28 and 30. These are one-based JSON cell positions, not execution
counts. Original notebooks were not executed or changed. Implementation lives in
[ml_development.py](ml_development.py) and [ml_plots.py](ml_plots.py); decisions and
material assistance belong in the [project records](../Project_Setup/PROJECT_STATE.md).
