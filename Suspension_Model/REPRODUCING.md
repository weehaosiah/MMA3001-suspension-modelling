# Checking and reproducing the saved project

Start by checking the saved evidence. An **audit** reads existing files, verifies
their fingerprints and recalculates saved summaries. It does not repeat a physical
simulation, train a model or run another timing experiment. A **fresh run** performs
those calculations again and creates new outputs. Keep those tasks separate so
the original evidence remains available.

The primary output is full-response `max(abs(zs - zu))` from static equilibrium,
including after the bump. The regressors return that peak in millimetres; they do
not return the post-bump trajectory or settling time.

## Check saved results on this laptop

The existing interpreter already has the required packages. In PowerShell:

```powershell
Set-Location -LiteralPath 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\Suspension_Model'
& 'C:\Users\dedvu\anaconda3\python.exe' interpretation_v1/review_saved.py
& 'C:\Users\dedvu\anaconda3\python.exe' final_evaluation.py audit
& 'C:\Users\dedvu\anaconda3\python.exe' runtime_benchmark.py audit
```

Each successful command prints `Audit passed` and exits with code zero. Stop and
investigate a failure; do not regenerate or change saved records to make a failed
fingerprint check disappear. A fingerprint (SHA-256) checks the exact file bytes,
including line endings. Five original nominal text outputs use CRLF line endings;
the exact `.gitattributes` exceptions preserve them because later records hash them.

| Command | Checks | Does not do |
|---|---|---|
| Interpretation reader | Six saved-data checks, grid comparisons and input fingerprints | Solve equations or call an ML model |
| Final audit | Frozen source/model/input identities and metrics from the saved prediction table | Refit models, make new predictions or reopen original held-out responses |
| Runtime audit | Saved schedule, counts, statistics, ratios and fingerprints | Measure new timings or repeat integrations |

These audits cover their declared saved evidence, not every possible scientific
error. The latest implementation test evidence remains 433 passing tests in
`runtime_benchmark_v2/unit_tests.txt`; the repository review does not claim a new
full-suite execution. Actual relocation-check outcomes are in
[the repository review](../Project_Setup/REPOSITORY_REVIEW.md).

A real GitHub Desktop clone was subsequently checked on 11 October 2026 at
commit `8ba9808`. All three saved-output audits passed in that separate copy using
the existing Anaconda environment; strict final/runtime checks required the four
course originals below. Tracked files remained unchanged. See the
[clone check results](../Project_Setup/clone_review_v1/CHECK_RESULTS.md) for exact
commands, file hashes and limitations. This was not a clean dependency installation
or full scientific rebuild.

## Course files required for a strict audit

The later nominal profiling study is documented separately in
[PROFILING_GUIDE.md](PROFILING_GUIDE.md). Its saved-only audit is
`python profile_nominal.py audit --output profiling_v1`; this does not solve the
model. `python profile_outputs.py --output profiling_v1` audits then recreates
the derived table/plot. Its new audit records absent excluded course originals
explicitly and checks them if present. The older final/runtime audit prerequisites
below are unchanged. Profiling run mode performs seven repeated solves in a new
output directory; it is not a full-project rebuild or model training.

On 12 October its audit passed in a separate local working snapshot with all 31
excluded originals absent. Git byte-preservation checks also pass after exact
line-ending exceptions for the three sealed profiler text exports. See the
[profiler reproduction record](profiling_v1/REPRODUCTION_CHECK.md). That check
used the existing environment; it was not a remote clone or clean installation.

The Git repository intentionally excludes the original course PDF and notebooks.
Obtain the following matching copies through your authorised course access and
place them at the repository root, alongside the top-level README. They are needed
for the historical source fingerprints, even though their notebook cells are never
executed by the saved-result audits. Without them, final/runtime strict audits stop
with a missing-file error. The interpretation reader needs only tracked files.

| Exact filename | Required by | SHA-256 |
|---|---|---|
| `MMA3001_2026_Project_Brief.pdf` | Final/runtime audits | `1029cf7c7c2844161af0c3727bbcbf40fac3913575683defe34ee942f9a9550c` |
| `MMA3001_Notes_Week02_1_Optimisation_and_Profiling.ipynb` | Runtime audit | `42166ad53117029e35108461b3a4c6607cd2ec38c7aac5ba30e323a3e1640749` |
| `MMA3001_Notes_Week05_5_Evaluating_Regression_Performance.ipynb` | Final audit | `b3dd29a48eea8b871d2410cdf5e59b90d623553e2605991b7a00f1f7e8796155` |
| `MMA3001_Notes_Week05_6_Training_Data_Evaluation_and_Selection.ipynb` | Final audit | `94a81726e26ba53b665f8ed29dabf9ebf089b2975808f30242f25f4a98684fc0` |

Historical nominal/verification runners and checkpoint-dependent tests also need:

| Exact filename | SHA-256 |
|---|---|
| `MMA3001_Notes_Week07_4_Runge_Kutta_Methods.ipynb` | `fb9f0bba532333deae424ad9874cfc3e326129d098912d16f1f836d05601dd7b` |
| `MMA3001_Notes_Week07_5_Higher_Order_ODEs.ipynb` | `f28d5f5923c66b68dd8199bc286f8fc4eeaf04a5715a60fde46b85d57f9b96c8` |

The source PDF/notebooks are available locally, not missing from this workspace.
An updated course copy may have a different checksum. Preserve it separately and
document the difference rather than rewriting old fingerprint records. Readers
without course access can still inspect the authored code, explanations, plots and
saved check reports. The repository is not a fully self-contained strict-audit bundle.

## Environment and portability

The verified environment is Windows with **Anaconda Python 3.12.7** and seven pinned
direct packages in [requirements-ml.txt](requirements-ml.txt): NumPy 1.26.4,
SciPy 1.13.1, Matplotlib 3.9.2, pytest 7.4.4, scikit-learn 1.5.1, joblib 1.4.2 and
threadpoolctl 3.5.0. It includes [requirements.txt](requirements.txt).

These files record direct dependency versions; they are not a complete lock of
every transitive package or numerical-library build. Original environment details
are in [environment.json](results/environment.json), and runtime context is in
[plan.json](runtime_benchmark_v2/plan.json).

For a future isolated installation, from `Suspension_Model` in a separate copy:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
```

This installation has not been executed in the readiness review. Some run/test
guards compare the complete original Anaconda build string, not just `3.12.7`.
Saved fingerprint keys also contain Windows path separators. Other operating
systems and a clean installation are unverified; the current strict-audit workflow
is documented for Windows. Preserve source checks rather than disabling them to
force a different environment through.

## Which commands change results?

| Entry point | Behaviour |
|---|---|
| `run_nominal.py` | Recalculates the nominal comparisons and overwrites `results/` |
| `run_verification.py` | Recalculates pilot comparisons and overwrites `verification_results/` |
| `generate_dataset.py --output NEW_FOLDER` | Generates the fixed dataset; refuses an existing output folder |
| `ml_development.py --output NEW_FOLDER` | Fits development candidates; refuses an existing output folder |
| `ml_reference_check.py --output NEW_FOLDER` | Repeats refined validation calculations; refuses an existing output folder |
| `final_evaluation.py prepare/evaluate` | Fits/evaluates the fixed final models with checkpoint guards; use the stage guide |
| `runtime_benchmark.py run --output NEW_FOLDER` | Performs the timing workload; refuses an existing output folder |
| `profile_nominal.py run --output NEW_FOLDER` | Repeats the existing nominal simulation seven times; refuses an existing output folder |
| `profile_nominal.py audit --output profiling_v1` | Checks the saved profiler records without a new solve or timing experiment |
| `profile_outputs.py --output profiling_v1` | Audits saved profiles and rewrites only derived tables/plot; no simulation |
| `python -m pytest -q tests` | Runs all current tests, including small numerical/synthetic fits and checkpoint-dependent checks |
| `build_docs.py` | Regenerates function HTML; no simulation, fitting or saved scientific output changes |

Do not execute the first two commands in the preserved checkpoint. Work in a
separate disposable copy for an intentional new reproduction, and retain outputs
with their new timestamps/environment. Changing earlier results can invalidate
later fingerprints; historical scripts are not a single end-to-end rebuild pipeline.
The guides for [datasets](DATASET.md), [development](ML_GUIDE.md),
[final evaluation](FINAL_EVALUATION_GUIDE.md) and [runtime](RUNTIME_GUIDE.md)
describe their boundaries. The final test has been consumed: repetition cannot
turn known test cases into a fresh independent test or authorise tuning against them.

Use the [HTML index](docs/index.html) for functions. Source files are authoritative;
the [walkthrough](WALKTHROUGH.md) connects the code to the physical model. No course
notebook execution or package installation is needed to read these documents.
