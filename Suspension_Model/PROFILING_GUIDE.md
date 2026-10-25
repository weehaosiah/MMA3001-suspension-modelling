# Profiling the nominal simulation

Prepared 12 October 2026. This is a bounded performance study and learning guide,
not assessed report prose. The actual outcome belongs in
[profiling_v1/CHECK_RESULTS.md](profiling_v1/CHECK_RESULTS.md).

Completed: seven repeated solves, all five study checks pass, 13 focused tests pass
and all 120 pre-existing protected files are unchanged. Unprofiled median wall
time is 413.608 ms; profiled median is 524.979 ms. Median paired profiler overhead
ratio is 1.32834. These are local instrumented/uninstrumented full-diagnostic
observations, not comparable speedup evidence against the earlier nine-case study.
The integration path accounts for 90.82-92.32% of each profile's total self time
when measured cumulatively; road_height has the largest self-time share, 25.55-25.83%.
The saved result table and [plot](profiling_v1/self_time.png) explain overlap and limits.

The recorded decision is to retain the frozen implementation at this stage.
A scalar road-height path is a possible future optimisation target, not a tested
improvement. Post-bump diagnostics and precision remain intact.

## Question and source

Which functions account for the work in one unchanged nominal simulation with
post-bump diagnostics? The primary output remains full-response max abs(zs-zu),
measured from static equilibrium. The body and wheel keep moving after bump exit;
both integration segments and the post-bump checks are included.

Course basis: Week02_1, zero-based cells75-84 (repeated/warm timing), 91-116
(profiling, overhead and short-workload limits), 127-129 (comparable conditions
and preserving precision). Cells72-73 distinguish profiling from hardware-counter
measurements. The notebook teaches line_profiler and Scalene. Neither is installed
here. We use built-in cProfile as an explicitly documented extension, following
[Python 3.12's profiler documentation](https://docs.python.org/3.12/library/profile.html).
No package or course notebook is installed, changed or executed.

## Fixed workload and checks

The new runner calls existing `simulate` then `summarise`, with nominal parameters,
unchanged RK45 controls, 5 s duration, 1 ms observations and the +/-1 mm settling
band. Parameter construction, imports, file reading/writing and profiler-result
formatting are outside the measured callable. Full diagnostics are included.
This differs from the prior peak-only comparison with ML.

One warmup and three pairs of unprofiled/profiled calls give exactly seven new
integrations of the same setup. Pair order alternates U/P, P/U, U/P. Each pair
has one observation per mode; all observations are retained. The run sets detected
numerical library pools to one thread and checks them before/after each workload.
Other assistant experiments are idle during measurement; background OS/user load
is not comprehensively controlled. Three pairs support local diagnosis, not a
precise general performance estimate.

Every output field except integration time must exactly reproduce the saved
`results/summary.json` baseline. This includes 6196 derivative calls per solve,
contact/energy/tail flags and raw settling status `candidate`. The original
nominal refinement study established resolution; the profiler does not add a
new resolution proof. Calls counted by cProfile must also match the expected
solver and physical-function counts. All prior scientific files and original
course sources are hashed before/after; bytes of held-out files are hashed for
preservation without reading response values. No fitted model is loaded.

## Reading the evidence

- **Self time:** time attributed to a function excluding functions it calls.
- **Cumulative time:** time in a function including its callees. Parent and child
  rows overlap; do not sum them or interpret their percentages as separate pieces.
- **Call count:** repeated force evaluations are how RK45 advances/checks motion;
  they are not floating-point operation counts or extra dataset rows.
- **Profiler overhead:** instrumentation itself slows execution, unevenly across
  Python and native code. Use the paired wall-time ratio only to illustrate that
  overhead plus noise. Keep unprofiled runtime separate from instrumented costs.

The study identifies expensive call paths. It does not measure peak memory,
arithmetic intensity, FLOPS, hardware saturation or why an underlying native
operation is slow. These require additional relevant measurements; the brief does
not require every possible optimisation. Do not weaken checks, reduce precision,
change tolerances or remove post-bump analysis to manufacture a faster result.

## Reproduction

Start with the saved checkpoint. On the student's laptop:

```powershell
Set-Location -LiteralPath 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\Suspension_Model'
& 'C:\Users\dedvu\anaconda3\python.exe' -B profile_nominal.py audit --output profiling_v1
```

For an assessor's copy, replace the directory with that clone's `Suspension_Model`
folder and the interpreter path with their compatible Python installation. The
recorded direct packages are in `requirements-ml.txt`; see [REPRODUCING.md](REPRODUCING.md)
for installation and environment limits. A successful audit prints `Audit passed`
and exits with code zero. It checks saved evidence without a new solve, fit,
prediction or timing measurement.

Only for an intentional fresh seven-solve reproduction, from `Suspension_Model`:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' -B profile_nominal.py run --output profiling_recheck
& 'C:\Users\dedvu\anaconda3\python.exe' -B profile_nominal.py audit --output profiling_recheck
```

Use an absent output folder; the runner refuses overwrite. Run mode performs the
seven solves. Audit mode checks saved fingerprints, profiles, outputs, counts and
summary arithmetic.
Keep failed attempts and use a different folder for a deliberate retry.

For the existing checkpoint, use `audit --output profiling_v1`. Course sources
are checked if present; their absence is explicitly reported and does not prevent
this new saved-profile audit. The older final/runtime audits retain their strict
source requirements. Authored scientific files must still match the recorded
fingerprints. Binary `.prof` compatibility depends on the Python profiler version;
plain JSON function tables and text exports are also provided. This is not a
clean-installation or complete-project rebuild check.

The three saved pstats text exports use CRLF line endings. Exact .gitattributes
exceptions preserve their sealed bytes across commits/clones; .prof files are
explicitly binary. Do not normalise those exports. Before publishing any future
profiling checkpoint, check that Git preserves all of its sealed artifact bytes.
The [recorded local checks](profiling_v1/REPRODUCTION_CHECK.md) include Git byte
preservation and a relocated saved-only audit without course originals. They do
not replace a fresh clone of the eventual upload.
