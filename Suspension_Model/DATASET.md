# Using the suspension simulation dataset

This is a working guide to the adopted P007 dataset design and its generator. It
explains the files and checks; it is not the assessed report. The first generation
completed on 5 October 2026: all 400 targets passed the adopted checks and the
combined test suite passed 280 cases. Read the
[dataset check record](dataset_v1/CHECK_RESULTS.md) and
[machine-readable status](dataset_v1/summary.json) for exact outcomes and limitations.
Links in this guide refer to that preserved `dataset_v1` output folder.

The current stage generates and checks simulation data. Fitting preprocessing,
training ML models and evaluating final-test predictions require the later ML
stage; they are not authorised by this dataset-generation step.

## What one row means

One row represents **one suspension setup**: one spring stiffness `ks_N_m` and one
damping coefficient `cs_N_s_m`. These coefficients stay constant during that
simulation. The body mass, wheel mass, tyre stiffness, road bump and starting
state remain fixed at the adopted values.

The model calculates body and wheel motion from rest at static equilibrium. Its
single prediction target is:

```text
A_mm = 1000 * maximum(abs(body_position - wheel_position))
```

The maximum covers the whole checked 0-5 second response, including movement
after the bump ends at 0.50 seconds. Positions are measured from static
equilibrium, so the target excludes static sag. It measures the largest departure
in either direction; it is not peak-to-peak travel. Calculations use metres and
the exported target uses millimetres.

The thousands of time samples used to describe one motion history do not become
thousands of independent training rows. The generator saves setup-level outputs
and diagnostic summaries. It does not save a full motion-history file for each
dataset row. The existing nominal and pilot traces remain separate verification
artifacts; their repeated solver runs do not add extra dataset rows.

## Why there are three groups

A **split** assigns each setup a role before its output is generated.

| Split | Setups | Selection | Intended later use |
|---|---:|---|---|
| Training | 225 | All combinations of 15 stiffness and 15 damping values | Fit the regression model |
| Validation | 75 | Separate uniform random input pairs, seed 3001 | Compare methods and settings |
| Final test | 100 | Separate uniform random input pairs, seed 3002 | Evaluate once after modelling choices are fixed |

These are 400 distinct coefficient pairs. The grid includes the domain endpoints:
stiffness 18,000-30,000 N/m and damping 1,594.8-2,658.0 N s/m. Its traversal uses
ascending stiffness in the outer loop and ascending damping in the inner loop.
Stable identifiers run from `train_001` to `train_225`, `validation_001` to
`validation_075`, and `test_001` to `test_100`.

A **random seed** fixes the starting state of the number generator so that the
declared inputs can be reproduced. Each random split uses its own NumPy
`Generator(PCG64(seed))`. Each generator makes one call:

```python
generator.uniform(
    low=[18000.0, 1594.8],
    high=[30000.0, 2658.0],
    size=(count, 2),
)
```

The two columns are stiffness then damping, and rows retain the draw order.
There is no added measurement noise, reshuffling, redraw for favourable results
or use of a shared global random generator. The saved NumPy version and input
manifest also form part of the reproduction record.

The [input coverage plot](dataset_v1/input_coverage.png) shows only coefficient
locations. Uniform sampling gives equal weight per area of the chosen rectangle;
it does not reproduce the distribution of real vehicle settings. The random
evaluation points mainly assess interpolation inside the rectangle. They do not
guarantee accuracy at every edge or establish that 400 rows are sufficient.

## Reusing the nine pilots

The grid contains all nine previously checked low/nominal/high pilot setups.
For those training rows, the generator reuses the baseline output at **1 ms
observations and a 5 second horizon**, from the verification record's
`bands["1"]["runs"]["base_1ms"]`. The tighter, longer reference is not substituted
for these labels.

The saved dataset therefore uses nine existing baseline results and **391 new
label integrations**. Regression tests also perform small verification solves;
those are not new dataset setups. Actual attempted and completed integrations,
new runtime and historical pilot runtime are recorded separately in the output
summary. Historical runtime is not counted as new generation work.

Reuse requires matching physical inputs, initial state, numerical settings,
model-source bytes, Python version and installed NumPy/SciPy versions, together
with successful pilot verification. A **hash** is a fingerprint of a file's bytes;
matching source hashes help prevent stale pilot results being silently reused
after the model changes. A mismatch stops generation. It should be investigated
and the verification checkpoint renewed when appropriate, rather than bypassed.

## Files to read

| File under `dataset_v1/` | Purpose |
|---|---|
| [CHECK_RESULTS.md](dataset_v1/CHECK_RESULTS.md) | Readable actual check outcomes and limitations |
| [generation_plan.json](dataset_v1/generation_plan.json) | Frozen design, units, seeds, draw order, settings, environment and source identities |
| [setup_manifest.csv](dataset_v1/setup_manifest.csv) | All 400 IDs, split assignments and exact input pairs, saved before label generation |
| [summary.json](dataset_v1/summary.json) | Readiness, counts, failure reasons, workload, audits and file hashes |
| [input_coverage.png](dataset_v1/input_coverage.png) | Input locations by split; no response values |
| `train.csv`, `validation.csv` | Input columns and eligible primary targets for later development |
| `train_diagnostics.jsonl`, `validation_diagnostics.jsonl` | Detailed per-setup checks and raw outputs for development rows |
| `heldout_test/test.csv`, `heldout_test/test_diagnostics.jsonl` | Reserved final-test targets and diagnostics |
| `heldout_test/README.md` | Final-test handling rules |
| `unit_tests.txt` | Actual test-suite output from the generation run |

CSV is a table stored as text. JSON stores named values; JSONL stores one JSON
record per line, here one setup per line. The input manifest is saved before
simulation, and its fingerprint and the generation plan's fingerprint are checked
again before the dataset can be marked ready. Each finished row is flushed to
its output files. An interrupted run remains incomplete and must not be treated
as ready.

### Target-table dictionary

| Column | Meaning | Unit/type |
|---|---|---|
| `setup_id` | Stable identity of this coefficient pair | Text |
| `split` | `train`, `validation` or `test` | Text |
| `ks_N_m` | Effective vertical suspension spring stiffness | N/m |
| `cs_N_s_m` | Effective vertical viscous suspension damping | N s/m |
| `A_mm` | Eligible full-response maximum absolute relative displacement | mm; empty if invalid |
| `target_valid` | Whether this primary label passes the declared eligibility checks | `True` or `False` |

Only `ks_N_m` and `cs_N_s_m` are intended prediction features. A **feature** is an
input supplied to the future regression model. IDs, split names, validity flags
and outputs calculated by the simulation must not be used as prediction features.

The manifest adds `sampling` (grid or independent uniform), `seed` (empty for the
deterministic grid) and `pilot_id` (present only for the nine reused training rows).
Python's round-trip float text preserves the stored numerical inputs; do not round
the working CSV values merely to make the table shorter.

### Supporting diagnostics

Each JSONL record includes the setup and physical parameters, result origin,
pilot provenance when applicable, `raw_summary`, `validity`, any exception, and
work measurements. Raw summaries retain `A_m` in metres as well as:

| Diagnostic | Interpretation |
|---|---|
| `A_post_m` | Largest absolute relative movement from bump exit onward; exit is included |
| `settling_after_exit_s` | Time from exit to the last sustained entry into the +/-1 mm band, when resolved |
| `minimum_contact_N` | Minimum sampled total tyre force, including static weight |
| `tail_bound_m` | Energy-based check on the remaining relative movement at the final time |
| Energy and solver fields | Post-bump energy behaviour, successful completion, finite states and work |

Post-bump motion and settling remain important engineering diagnostics. They are
not additional ML targets or features. Settling concerns the difference between
body and wheel positions; it does not mean every part of the vehicle is stationary.

## What makes a label eligible

New rows use the pilot-supported settings: RK45 with `rtol=1e-6`, component
absolute tolerances `[1e-9, 1e-8, 1e-9, 1e-8]` in state units, maximum internal
step 0.005 seconds, 1 ms observations and a common 5 second horizon. Internal
integration steps and the observation grid are different things.

Each row must have a successful finite complete solution, unchanged full state
at bump exit, consistent peak values and times, acceptable post-bump energy
behaviour and an adequate remaining-motion check. The sampled tyre-force minimum
must exceed the fixed 1 N screening margin. That margin is a numerical screening
choice supported by the pilot comparisons, not a physical safety standard.

The remaining-motion check uses the energy of both masses and both springs. It
requires the estimated bound to be below the smallest of 0.5 mm, half the primary
peak and half the post-bump peak. With numerical states this remains a consistency
check, not a certified continuous-time error bound.

The `validity` record keeps separate flags for `numerical_primary_valid`,
`contact_consistent` and `target_valid`. Failed primary labels remain in their
original split with an empty CSV target; raw estimates and failure reasons remain
available in diagnostics. The generator does not drop, replace or relabel them.

Settling has a separate decision. It requires the last sustained band entry,
at least one observed second inside the band and an adequate tail. Its status is
`resolved_under_adopted_settings` or `unresolved`. An unresolved settling time is
null; it is never replaced by the observation cutoff. Unresolved settling alone
does not erase an independently eligible primary peak. A numerical settling
result should still be interpreted alongside the separate contact flag.

The saved export audit checks identities, input round trips, validity decisions
and the metre-to-millimetre target conversion. `dataset_ready: true` additionally
requires all declared targets to be eligible and the frozen manifests and source
files to remain unchanged. If readiness is false or missing, investigate the
saved status before using the dataset for fitting.

Every row receives these checks; the complete solver/grid/horizon/RK4 refinement
programme was performed on the nine pilots. The generator does not claim a new
full refinement study or a proven 0.05 mm exact error for every row. Numerical
agreement and sampled contact consistency do not establish real-car validity,
physical travel clearance, Ferrari calibration or correctness everywhere between
the sampled setups.

## Generate or reproduce the files on this laptop

Open PowerShell and enter the authored project folder:

```powershell
Set-Location -LiteralPath 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\Suspension_Model'
```

The completed first generation used this command (its output now exists, so a
repeat of this exact command will be refused):

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' generate_dataset.py
```

For a fresh reproduction in a different folder:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' generate_dataset.py --output dataset_recheck
```

The generator refuses to overwrite an existing output directory, including a
partly completed one. Keep earlier outputs and choose another new folder name
for another attempt. The design and input pairs stay the same; timestamps and
measured runtimes naturally change. This is a reproducibility recipe, not a claim
that a second generation has already been executed.

Use the existing Anaconda environment recorded for the pilots: Python 3.12.7,
NumPy 1.26.4 and SciPy 1.13.1, with Matplotlib 3.9.2 and pytest 7.4.4. Exact package
requirements are in [requirements.txt](requirements.txt). The reuse guard is
environment-sensitive: it compares the complete saved Python version/build string
as well as the NumPy and SciPy versions. Another environment may correctly stop
with a provenance mismatch. Reproduction in a fresh environment is unverified.
Changing environments needs a reviewed workflow for refreshing the verification
artifacts and their cache-dependent tests; simply rerunning a command is not a
guarantee that the old results are reusable. No dependency installation is part of
these commands.

## Keep the final test reserved

Training and validation outputs are for later model development. Final-test
response files are segregated under `heldout_test/`. They are reserved for the
one-time evaluation after the methods, settings and data budget have been fixed.
Do not inspect their response distributions, plots or prediction errors to choose
a model. The generator may mechanically check their predefined numerical and
physical validity, input identities and target-unit conversion. Shared summaries
expose those checks and counts, not test-target distributions.

This folder arrangement is a workflow rule rather than encryption. The input
locations can be inspected for all splits. Later learned preprocessing, such as
feature scaling, must be fitted using the appropriate training data only; nothing
in this generation step fits a scaler or an ML model.

## Sources and implementation

The adopted design is recorded in [PROJECT_STATE.md](../Project_Setup/PROJECT_STATE.md),
P007/P008 and the numerical settings decision D005. The exact row counts, grid,
seeds and pilot reuse are project choices applying the course principles.

Before adaptation, the local notebook sections were read without execution:

- Week05_6, cells 4, 13-15 and 19: row/target definition, duplicate identity and
  split design suited to the prediction question.
- Week05_6, cells 28-30: training-only learned preprocessing, fixed engineering
  unit conversions and reservation of the final test.
- Week05_5, cells 16-17 and 36-37: training/validation/test roles and final
  evaluation after choices are fixed.

Cell numbers are one-based positions in the notebook JSON, not execution counts.
Course originals remain separate from authored project work. The implementation
is in [dataset_design.py](dataset_design.py) and
[generate_dataset.py](generate_dataset.py); material assistance and subsequent
checking are recorded in [AI_USE_LOG.md](../Project_Setup/AI_USE_LOG.md).
