# Runtime comparison guide

This guide explains P009's bounded timing experiment and the implemented `runtime_benchmark.py run` / `audit` workflow. It is working project documentation, not assessed report prose. The prescribed work counts below do not by themselves show that a run completed. Use the saved [runtime checkpoint](runtime_benchmark_v2/) for execution status, check results, and actual timings; no measured speed ratio is invented here.

The full protocol is in [RUNTIME_PLAN.md](RUNTIME_PLAN.md). Its opening describes the earlier planning-only stage. The student's subsequent instruction authorises implementing and running that protocol. The physical interpretation remains in [PHYSICS_REVIEW.md](PHYSICS_REVIEW.md), and the completed accuracy comparison remains in [FINAL_EVALUATION_GUIDE.md](FINAL_EVALUATION_GUIDE.md).

## Completed result, 5 October 2026

All **433 tests** and **seven benchmark checks** pass. The prescribed schedule completed 162 fresh integrations (including 27 warm-up integrations), 1,003,968 derivative evaluations and 100,060 guarded ML calls. Forty additional integrity prediction calls compared matching array shapes before/after; no model was fitted. Every simulation peak reproduced its saved baseline value exactly in this run. The saved-result audit reproduces the timings, work counts and ratios without another measurement.

| Method | Mean of nine single-case medians [ms/query] | Median batch of nine [ms/batch] |
|---|---:|---:|
| Simulator, A only | 222.637844 | 2014.271000 |
| Linear comparator | 0.126471 | 0.127570 |
| Frozen selected SVR | 0.163470 | 0.182364 |

The corresponding warm ratios are about 1760 (linear) and 1362 (SVR) for a single query, and 15790/11045 for one nine-case batch. They compare the specified scalar task with imports/models already loaded. A batch returns nine peaks in one call; its average per-case cost does not describe nine separately arriving requests. The previously frozen SVR choice and final accuracy scores are unchanged.

The full diagnostic workflow averages 222.277811 ms across its nine case medians. Its small difference from A-only timing should not be interpreted as the cost of diagnostics being negative: these are separate noisy observations/phases, not a controlled subtraction of the extra operations. Both are approximately 0.22 s per setup here. No profiling or optimisation claim is made.

The laptop reported AC power and 100% battery at the start and end. MKL, Microsoft OpenMP and Intel OpenMP all reported one thread before and after measurement. Other assistant experiments were idle, but user/OS background load was not comprehensively measured or controlled. The shortest measured 1000-call ML block was 0.1238523 s, compared with a recorded timer resolution of 1e-7 s. The schedule took 50.9708593 s including between-query bookkeeping; this is not a model build time.

The first attempt stopped before benchmark calls because a lazily loaded Intel OpenMP pool escaped the initial thread-limit discovery. Its 429 passing tests, plan, failure note and exact old-runner snapshot remain in [runtime_benchmark_v1](runtime_benchmark_v1/FAILURE_NOTE.md). Explicit library discovery before applying the limit, plus four new guard tests, fixed this without changing physical/model settings or repetitions. Older short timing records requested a one-thread limit but lack these complete before/after pool snapshots; they remain a separate historical cost ledger, not a controlled comparison with this run.

## What question does this answer?

How long does it take to return the full-response peak suspension movement for an already specified setup, using the simulator, saved linear model, or saved SVR?

The requested number is `A_mm = 1000 * max(abs(zs - zu))`. Body displacement `zs` and wheel displacement `zu` are measured from static equilibrium. The maximum includes the bump and the response afterward. The factor 1000 converts metres to millimetres. This definition is unchanged by the timing work.

The benchmark uses nine previously verified combinations of spring stiffness and damping. It repeatedly calculates those cases; it does not add 162 new physical setups to the dataset. The nine inputs are the low/nominal/high combinations of `ks = 18000, 24000, 30000 N/m` and `cs = 1594.8, 2126.4, 2658 N s/m`, in stiffness-outer, damping-inner order.

The simulator keeps baseline RK45 settings, float64 arithmetic, a 5 s horizon, and 1 ms observations. The two fitted models remain the final 300-row pipelines. The preferred SVR still has `C=100`, `gamma=1`, and `epsilon=0.05 mm`. Nothing is fitted again and the accuracy-based model preference is unchanged. The benchmark runner does not open the original final-test response files; separate preservation review checked their checksums without parsing responses or evaluating predictions.

## Three workloads, with different meanings

| Workload | Simulator | Fitted models |
|---|---|---|
| One setup, A only | Check the input, construct physical parameters, integrate fresh, sample the full response, extract A, convert to mm, and check finite output. | Check the input, apply the saved scaler, predict A in mm, and check finite output. |
| A batch of nine setups, A only | Perform nine fresh integrations and return nine values. | Pass the nine rows through one guarded prediction call. |
| One setup, full diagnostics | Perform a fresh solve and calculate A, post-bump peak, settling, contact, energy and tail checks, and the result record. | No equivalent output from the current regressors. |

The primary ratio compares the A-only paths. Even here the simulator calculates a trajectory while ML approximates its scalar result; the established prediction error remains relevant. A-only timing omits contact/tail/settling classification and is restricted to these previously verified timing inputs. It does not establish that an arbitrary query is physically valid.

The full diagnostic path is timed separately. It remains necessary when the question includes movement after the bump, settling, or physical validity. Its time must not be presented as the cost of an equivalent ML output that the current model cannot supply.

## Warm timings and exactly what is counted

“Warm” means Python, libraries, and fitted models are already loaded. The timer measures elapsed wall-clock time: the time a person would wait for the callable, including interruptions by the operating system. It is not a count of floating-point operations.

Input-array allocation is outside the timer for all methods. Input guards, parameter construction where needed, and ML scaling are inside. Imports, model loading, logging, output files, figures, and correctness comparisons are outside the primary timing boundary. The experiment therefore measures repeated in-memory use, not application startup or a complete project build.

The prescribed budget is:

| Simulation workload | Warm-up integrations | Measured integrations | Total |
|---|---:|---:|---:|
| Nine separate A-only cases | 9 | 45 | 54 |
| Nine-case A-only batch | 9 | 45 | 54 |
| Nine separate full-diagnostic cases | 9 | 45 | 54 |
| **Benchmark total** | **27** | **135** | **162** |

There are five measured rounds, with method order rotated deterministically. The batch comprises nine integrations on each simulator call. Pilot answers are not cached or substituted for calculations; saved labels are used only for correctness comparisons outside the timed region. Automated-test work, if any, must be distinguished from this benchmark budget.

ML calls are much shorter, so one timing observation is a block of 1000 real guarded calls. For each model and condition, three calls warm it up, followed by five measured blocks. Divide each block's elapsed seconds by 1000 to obtain average seconds per call. There are ten conditions per model: nine single cases and one nine-row batch. Thus the prescribed measured blocks contain 100,000 model calls in total, plus warm-ups and separately recorded integrity checks. A batch call returns nine predictions, so calls and predicted cases are different counts.

Every loop must execute the actual pipeline. Reusing an already computed answer would measure lookup cost instead. No guessed empty-loop or timer overhead is subtracted. If short-block resolution is inadequate, record that limitation rather than silently changing the workload. Warm-up elapsed durations are retained for work/failure bookkeeping but excluded from every reported timing statistic; this is how the implementation treats the plan's untimed warm-up phase. Forty separate untimed integrity predictions compare the same single-row/batch shapes before and after timing, because those shapes can differ in their last floating-point bits.

## How to read the results

For each single case, compare median time, minimum, maximum, and interquartile range across the five observations. The median is the middle value; the interquartile range is the spread of the middle half. For simulation, each observation times one call. For ML, each observation is an average over 1000 calls. Variation between five block averages is not variation between individual ML requests.

The summary for the nine-case single-query mixture is the mean of the nine per-case medians, giving each setup equal weight. It does not assume that every real workload uses that same mix. Batch summaries have a separate median time for all nine cases, an average time per case, and throughput in cases per second.

- `1 millisecond (ms) = 0.001 second`.
- `1 microsecond (us) = 0.000001 second`.
- Nine-case throughput is `9 / batch_time_seconds`.
- The warm A-only speed ratio is `simulator_time / ML_time`, using the same workload and summary rule.

A ratio above one means that ML returned the requested scalar sooner under that measured boundary. It is not an end-to-end project speedup or a guarantee on another laptop. Report linear and SVR separately. Faster linear prediction would not justify changing the already frozen accuracy-based preference after final testing.

## Checks that accompany timing

Before measurement, check the exact input identities, frozen model/source fingerprints, numerical settings, and recorded environment. A fingerprint is a checksum that detects changed file contents. Save the timing plan before work starts.

Warm-up A values are compared with saved baseline values using the planned `1e-8 mm` absolute reproduction tolerance. This tests reproduction under the same algorithm and environment; it is not a physical accuracy standard, an ML-error tolerance, or a replacement for the earlier `0.05 mm` refinement criterion.

The full diagnostic path must pass the existing validity checks. Every timed solve must complete with finite outputs, and derivative-evaluation counts are recorded as work counts, not FLOPs. Preserve all valid durations, including slow ones. A failed solve or integrity check prevents a completed benchmark claim; retain partial evidence rather than removing a difficult case.

After timing, compare the saved models, scalers, predictions, sources, and original data fingerprints with their starting values. Save raw durations, method order, checks, work counts, units, and machine/software context. None of these repetitions is a fresh independent accuracy test.

The checkpoint files are:

| File | Purpose |
|---|---|
| [plan.json](runtime_benchmark_v2/plan.json) | Frozen workloads, repetitions, environment, and input/source identities. |
| [raw_timings.jsonl](runtime_benchmark_v2/raw_timings.jsonl) | Individual recorded timing blocks/calls and their work counts, one record per line. |
| [summary.json](runtime_benchmark_v2/summary.json) | Completion status, checks, aggregated times, and permitted ratios. |
| [CHECK_RESULTS.md](runtime_benchmark_v2/CHECK_RESULTS.md) | Readable results and their interpretation limits. |
| [runtime_comparison.png](runtime_benchmark_v2/runtime_comparison.png) | Visual comparison using the saved measurements. |
| [unit_tests.txt](runtime_benchmark_v2/unit_tests.txt) | Recorded implementation-test output. |
| [integrity_predictions.json](runtime_benchmark_v2/integrity_predictions.json) | Matching single-case and batch predictions before and after timing. |

These links identify the completed checkpoint. Its summary records all seven checks passing. The earlier preflight failure is preserved separately in runtime_benchmark_v1; it contains no benchmark timings.

## Commands on this laptop

See [REPRODUCING.md](REPRODUCING.md) for the Windows environment and local course
files required by strict source checks. A repository copy alone omits those originals.

The command interface is below. The default checkpoint already exists, so use audit for its saved results; run will refuse to overwrite it. Use a fresh output folder for an intentional repeat. No package installation is part of this stage.

```powershell
Set-Location 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\Suspension_Model'
& 'C:\Users\dedvu\anaconda3\python.exe' runtime_benchmark.py audit
```

The default output folder is `runtime_benchmark_v2`. `run` must preserve existing outputs and refuse a folder that already exists. Once a run is complete, use `audit` to check the saved records and calculations without another timed simulation or model fit. The audit's implementation and saved check results are authoritative for the checks it performs.

Generated function documentation is available for the [benchmark runner](docs/runtime_benchmark.html) and [saved-results presentation](docs/runtime_outputs.html). The Python source remains authoritative.

For a deliberate repeat, choose an unused folder:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' runtime_benchmark.py run --output runtime_benchmark_recheck
& 'C:\Users\dedvu\anaconda3\python.exe' runtime_benchmark.py audit --output runtime_benchmark_recheck
```

Run the audit after the run succeeds. Keep every earlier checkpoint. An audit checks saved evidence; a repeat run performs the workload again and may produce different durations. A command recipe is not evidence that a repeat or fresh-environment reproduction has been executed.

During measurements, avoid concurrent simulations, tests, or other substantial work. Record the laptop's power state and competing workload; do not change system settings to force a favourable result. Numerical libraries use one thread for this comparison. The recorded environment is Python 3.12.7 with the versions in [requirements-ml.txt](requirements-ml.txt), which includes [requirements.txt](requirements.txt). Cross-environment reproduction remains unverified.

## Preparation cost and break-even remain separate

Quick predictions become possible only after the simulation labels and model development exist. The historical cost ledger in [RUNTIME_PLAN.md](RUNTIME_PLAN.md) includes data generation, reused pilot calculations, model search, tighter validation verification, and final fits, with their original timing boundaries.

Do not add an integration time to a row-processing total that already contains it. Likewise, a fit-only time is already inside its fitting/scoring loop. Reused pilot labels were calculated earlier; they were not free. Shared verification and final-assessment costs need an explicit accounting choice.

For a specified extra preparation cost `C` and comparable single-query times, the conditional break-even estimate is `C / (simulation_time - ML_time)`, provided the denominator is positive. The result is a number of queries; use whole batches and batch costs for a batch calculation. The complete extra preparation cost has not been measured, so this bounded benchmark does not establish a numeric break-even or total project speedup. Profiling, changing code or numerical settings, and measuring a complete fresh build would be separate work.

## Source basis and limitations

Read for this guide: PROJECT_GUIDE revision003, PROJECT_STATE revision019, P009 revision001, and actual Week02_1 cells 76, 78, 80, 82, 85, 92, 94, 102, 104, 128 and 130. These cover repeated timing, wall time, loops versus observations, warm execution, profiler overhead, sampling limits, and similar system conditions. Cells are numbered from one in the saved notebook. The project's timed callable/block approach adapts these ideas to Python scripts; the exact nine cases and repetition counts are project choices.

The notebook's SHA-256 remains `42166ad53117029e35108461b3a4c6607cd2ec38c7aac5ba30e323a3e1640749`. Earlier review identified a factor-of-1000 error in cell90's throughput heading, which labels Mvalues/s examples as Gvalues/s. Those examples are not used here. Its sampling-profiler suggestions are not universal requirements. No course code or linked video was executed for this guide.

The project brief's verified hash is unchanged from the earlier complete-page reading of pp5-7; no fresh full brief reading is claimed. It requires relevant performance analysis, credible comparisons, and limitations. It recommends timing routines and profilers, with arithmetic-intensity/FLOP estimates where appropriate; it does not require a speedup or optimisation of every characteristic. This benchmark provides timing evidence only; it adds no profiler measurement, parameter tuning, final-test evaluation, assessed report writing, or publication. The runner does not open original reserved-response files; independent preservation review checks their file checksums without inspecting their responses. Material source and AI assistance records remain in [EVIDENCE.md](../Project_Setup/EVIDENCE.md) and [AI_USE_LOG.md](../Project_Setup/AI_USE_LOG.md).
