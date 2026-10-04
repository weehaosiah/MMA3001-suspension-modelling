# Suspension simulation, verification and evaluated ML models

The nominal checkpoint is preserved below. Begin with the
[physical/code walkthrough](WALKTHROUGH.md), then see the
[nine-pilot check results](verification_results/CHECK_RESULTS.md).

## Final evaluation stage

Both declared models have now been refitted on the same 300 development cases
and evaluated once on all 100 reserved test cases. Read the
[final evaluation guide](FINAL_EVALUATION_GUIDE.md) and
[actual final check results](final_evaluation_v1/CHECK_RESULTS.md).
Test RMSE is 0.199436 mm for linear regression and 0.029796 mm for the
development-selected SVR. Its largest observed absolute test error is 0.051826 mm.
These measure agreement with numerical labels, not real-vehicle accuracy or a
guarantee over every possible setup. No model choice was changed after test access.

All 385 tests pass. The saved-result audit reproduces every final metric without
refitting or reopening the original test responses. The test set has now been
used; it cannot serve as a fresh independent test for changes chosen after seeing
these scores. Original development models and data remain preserved.

## ML development stage

Read [ML_GUIDE.md](ML_GUIDE.md) for the linear-regression versus RBF-SVR comparison.
The [actual development results](ml_development_v1/CHECK_RESULTS.md) use only
225 training and 75 validation setups. That stage kept the final-test responses reserved.
Every development-stage scaler learned from its 225 training inputs only; the sole target is full-response
peak travel in millimetres. Post-bump movement and settling remain supporting
physical diagnostics. The later 300-row refits are saved separately in the final checkpoint.

`requirements-ml.txt` adds the installed ML versions to the unchanged simulation
requirements. Use it for an environment intended to run the current complete
test suite. No package installation was needed on this laptop. A clean-environment
installation has not been tested.

## Dataset stage

Read [DATASET.md](DATASET.md) for the 225 training / 75 validation / 100 reserved
test design, file meanings and reproduction instructions. The
[dataset check results](dataset_v1/CHECK_RESULTS.md) record the generation outcome.
Each row is one complete spring-and-damper setup. Its primary target is still
the largest absolute body-to-wheel movement over the full response, including
after the bump. Post-bump peak and settling remain separate saved diagnostics.

The new modules are `dataset_design.py` (fixed setup identities and validity)
and `generate_dataset.py` (simulation, exports, checks and provenance). They
reuse nine verified baseline pilot runs only within training and integrate the
remaining 391 setups. Existing dataset folders are preserved; reruns use a new
output name. The dataset generator itself does not fit preprocessing or regression;
the subsequent ML development stage is separate.

## Reproduce the bounded verification stage

From this folder in PowerShell:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' run_verification.py
```

This runs the focused tests, the analytical clamped-wheel diagnostic and the nine
low/nominal/high stiffness-damping combinations. Each pilot compares baseline and
tighter RK45, three observation grids, 5 versus 10 seconds, and classical RK4 at
0.5 and 0.25 ms. If the horizon/tail is inadequate, the programme checks a common
10-second observation against 20 seconds. It records failures instead of creating
usable labels silently. Contact loss requires a physical-model/domain review;
longer observation cannot fix it.

The three settling bands (±0.5, ±1 and ±2 mm) are checked separately. The primary
output remains the full-response maximum absolute relative displacement.
`verification_results/summary.json` records every comparison and configuration;
the accompanying Markdown table, PNGs and compressed time histories make the
results inspectable. This command regenerates only `verification_results/`,
leaving the original nominal results in `results/` intact.

Additional source files:

- `rk4_check.py`: adapts Week07_4 cells 12/17 to a four-state fixed-step comparator.
  RK4 evaluates the changing road input at each intermediate stage time.
- `verify_reduced_case.py`: adapts Week07_5 cells 19–21 to a deliberately clamped
  wheel. It checks the existing body equation against a known formula; the wheel
  clamp is only a diagnostic and does not replace the full study model.
- `run_verification.py`: the bounded nine-pilot runner, including separate physical
  contact and numerical output-validity checks.

Verification settings must be selected using these recorded comparisons. Nine
successful sample locations do not guarantee every location in the domain;
every later run still needs its own contact and tail checks. These pilot outputs
are not the full parameter dataset, and no ML fitting occurs in this command.

## Original nominal checkpoint

This is the first implementation checkpoint, authorised on 4 October 2026. It
implements the adopted starting specification in `Project_Setup/PROJECT_STATE.md`.
It is working code and check documentation, not the assessed report.

## Start with the result

Open [the response plot](results/nominal_response.png), then
[the actual check results](results/CHECK_RESULTS.md).
The nominal full-response maximum is **40.571 mm**, the post-bump maximum is
**31.892 mm**, and sustained entry into the ±1 mm band occurs **1.269 s after
bump exit**. These values passed the recorded initial numerical checks; they are
not measurements from a real vehicle.

The road becomes flat at 0.50 s. The body and wheel are still moving, so the
simulation carries their positions AND velocities forward. The post-bump maximum
includes the exit instant; here it occurs exactly at that boundary. Motion then
swings into compression and decays. Settling refers only to the difference in
body and wheel positions, not every kind of vehicle motion.

## Run it on this laptop

Open PowerShell in this folder and run:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' run_nominal.py
```

To enter the folder from anywhere:

```powershell
Set-Location -LiteralPath 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\Suspension_Model'
```

The command runs the nominal comparisons and tests, and replaces the generated
files in `results/`. It prints the outcomes and returns a failure code if a required
check fails. Runtime measurements and generation timestamps naturally vary between
runs. No internet connection is needed with the existing packages.

To run only the focused tests:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' -m pytest -q tests
```

For another computer with Python 3.12, create a separate environment and install
the recorded versions (installation needs internet access):

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe run_nominal.py
```

This clean-environment recipe has not been executed here. The actual environment
used is Python 3.12.7, NumPy 1.26.4, SciPy 1.13.1, Matplotlib 3.9.2 and pytest 7.4.4.
Exact platform and interpreter details are in `results/environment.json`.

## How the code represents the physical model

A **function** is a named, reusable calculation. `road_height` supplies the bump,
`rhs` calculates the rates of change from Newton's force balances, and `simulate`
advances the motion through time. `summarise` measures the outputs afterward.

The **state** stores everything needed to continue the motion at one instant:

| State component | Physical quantity | Unit |
|---|---|---|
| `zs` | Body displacement from its static equilibrium | m |
| `vs` | Body vertical velocity | m/s |
| `zu` | Wheel displacement from its static equilibrium | m |
| `vu` | Wheel vertical velocity | m/s |

Upward is positive. Relative movement is `d = zs - zu`: positive is extension and
negative is compression. The primary output is `A = max(abs(d))` over the entire
checked response. It excludes static sag and is not peak-to-peak travel.
All calculations use metres; plots and reported travel use millimetres.

With `vrel = vs - vu`, the two force balances are:

```text
ms * body_acceleration  = -ks*d - cs*vrel
mu * wheel_acceleration =  ks*d + cs*vrel + kt*(road - zu)
```

The spring pulls back against displacement, and the damper opposes relative
velocity. Their forces act equally and oppositely on the two masses. The tyre
connects the wheel to the road. Gravity is already balanced in these equilibrium
coordinates; it is added back as static weight when checking total tyre force.

| Parameter | Nominal value |
|---|---:|
| Body share `ms` | 365.4 kg |
| Wheel assembly `mu` | 43 kg |
| Suspension stiffness `ks` | 24,000 N/m |
| Suspension damping `cs` | 2,126.4 N s/m |
| Tyre stiffness `kt` | 350,000 N/m |
| Gravity for contact check | 9.81 m/s² |
| Bump height / crossing duration | 0.050 m / 0.50 s |

The road is `h/2 * (1 - cos(2*pi*t/tau))` during crossing and zero otherwise.
Initial state is `[0, 0, 0, 0]`. A generic passenger-vehicle corner is modelled;
this is not a Ferrari calibration. There is no tyre damping, stop/contact-loss
model, pitch, roll or aerodynamic load.

## What the initial checks establish

**RK45** is the taught adaptive numerical method: it adjusts its internal time
steps to control an estimated local error. The times at which we inspect its
interpolated solution are separate. Making the output grid finer alone does not
make the underlying integration more accurate.

The runner performs four integrations: baseline nominal to 5 s, tighter nominal
to 5 s, tighter nominal to 10 s, and zero-road equilibrium to 5 s. The focused
tests also integrate a nominal fixture and a zero-road case; these are checks of
the same setup, not extra dataset rows. Three observation grids reuse the tight
5 s trajectory: 1, 0.5 and 0.25 ms. The baseline uses `rtol=1e-6`, state-specific
`atol=[1e-9,1e-8,1e-9,1e-8]`, and maximum internal step 0.005 s. The tight run
reduces both tolerances by 100 and uses maximum step 0.0025 s.

Peak differences must be at most 0.05 mm and settling differences at most 0.01 s.
Settling uses the last outside-band excursion, not the first zero crossing, and
requires at least one second observed inside the band. It is marked resolved
only after solver, grid, horizon and tail agreement. Missing confirmation is
recorded as unresolved with no settling time.

On flat road, energy in the masses and springs can only decrease through damping:
`H' = -cs*(vs-vu)^2`. The associated future relative-movement bound
`sqrt(2*H(T)/ks)` supplies a tail check. Applying it to approximate numerical
states is a strong consistency check, not a certified mathematical error bound.
Sampled contact minima are compared under refinement; the additional ambiguity
margin is `max(1 N, 10 times the largest observed change in the minimum)`.
This numerical margin and the energy allowance are project choices, not standards.

The original nominal check outcomes are in `results/CHECK_RESULTS.md`; full precision,
configuration and source hashes are in `results/summary.json`. Five seconds was
sufficient for this nominal case under the initial criteria. The subsequent
nine-pilot verification adopted five seconds with continued per-row tail checks;
see the dataset results for the later sampled setups.

## Files and provenance

| File | Purpose |
|---|---|
| `quarter_car.py` | Physical model, integration and output definitions |
| `run_nominal.py` | Reproducible comparisons, plots and saved evidence |
| `tests/test_quarter_car.py` | Independent force/energy checks and failure cases |
| `requirements.txt` | Exact package versions used |
| `docs/quarter_car.html` | Generated documentation of model functions |
| `results/nominal_trace_1ms.csv` | Readable time history in SI units |
| `results/nominal_trace_0p25ms.npz` | Compressed full-resolution final time/state arrays |

The CSV contains time samples from one physical setup; it is not the future
parameter-to-peak ML dataset. The final metrics use the 0.25 ms data.

The code adapts the position/velocity and RK45 patterns in local Week07_5 cells
9–15 and 47–48, Week07_4 cells 27–33, and the energy idea in Week07_5 cells 28–30.
Cell references mean one-based JSON positions. Course notebooks were read, not
executed or modified. Model/source details are in `Project_Setup/EVIDENCE.md`:

- S002: [KU Leuven quarter-car force equations](https://fet-edu-em.pages.gitlab.kuleuven.be/computer-aided-simulation/course-material/t42cms-cas-book/t42cms-cas-lectures/Examples/Quarter_car_suspension/Quarter_car_suspension_model.html).
- S003: [MathWorks bump shape](https://www.mathworks.com/help/robust/gs/active-suspension-control-design.html); our 0.50 s duration differs from its example.
- S004: [Soong et al. 2017, Table 2](https://doi.org/10.1371/journal.pone.0179485) for the generic front-corner parameters.
- S007: [SciPy 1.13.1 solve_ivp documentation](https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.integrate.solve_ivp.html).

Codex wrote the implementation, initial-check runner, tests and explanatory
documentation with independent assistant review. The student adopted the starting
specification and authorised this stage. See `Project_Setup/AI_USE_LOG.md` for
assistance, checking, corrections and learning still to be reviewed.

## Checkpoint and remaining scope

A **Git commit** is a saved local version of the tracked files. **GitHub** hosts
a repository online; a local commit does not upload anything. Course originals,
temporary files and caches are excluded from the local repository. No remote has
been configured. No student Git identity was configured at discovery; any initial
AI-created commit is explicitly attributed to the assistant, not to the student.

This workspace's repository was created inside the app sandbox. If Windows Git
reports differing ownership when inspecting it, this command trusts only this
known folder for that command; no global setting is changed:

```powershell
git -c safe.directory='C:/Users/dedvu/OneDrive/Documents/MMA3001 Jupiter notebooks' log --oneline
```

To regenerate the function documentation after later model edits, run from this folder:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' -c "import pathlib,pydoc,quarter_car; p=pathlib.Path('docs'); p.mkdir(exist_ok=True); s=pydoc.html.page('quarter_car',pydoc.html.document(quarter_car)); (p/'quarter_car.html').write_text('\n'.join(line.rstrip() for line in s.splitlines())+'\n',encoding='utf-8')"
```

The subsequent nine-setup verification stage is documented above and in
`verification_results/`; dataset generation and per-row contact/tail checks
are documented in `DATASET.md` and `dataset_v1/`. The later trained development
models are documented in `ML_GUIDE.md`; the final comparison is documented in
`FINAL_EVALUATION_GUIDE.md` and `final_evaluation_v1/`. No telemetry validation
or assessed report prose exists.
Licence selection, GitHub hosting and final submission packaging remain later work.
Student understanding and overall project AI contribution remain to be assessed.
