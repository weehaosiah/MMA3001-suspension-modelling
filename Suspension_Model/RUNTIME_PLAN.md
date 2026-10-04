# Proposed bounded runtime comparison

P009, revision 001, 5 October 2026. **Planning only: no new benchmark has been implemented or run.** The student authorised physical interpretation and planning after final evaluation. This document fixes a concrete proposed experiment for the next stage; it is not measured performance or assessed report prose.

## Question and comparison boundary

How much elapsed computation time is needed to return the existing full-response peak A for one setup, or for a batch of nine setups, using the baseline simulator, frozen linear model and frozen SVR?

Keep the frozen 300-row fitted pipelines and the numerical definition of A unchanged. Compare warm in-memory queries, with imports and fitted models already loaded. A warm query represents repeated use in an open Python session. Process startup/model loading, file export and plotting are outside this timing boundary. No overall application or cold-start speedup is implied.

| Workload | Simulator work inside timer | ML work inside timer | Permitted conclusion |
|---|---|---|---|
| Primary: A-only query | Validate input, create parameters, integrate fresh to 5 s, sample at 1 ms including bump exit, take max abs(zs-zu), convert to mm and check finite output. | Validate input, apply saved scaling, predict A in mm, check finite output. | Time to produce the same requested scalar on these already checked setups, allowing the documented approximation error. |
| Secondary: full diagnostic query | Existing `row_result(setup, cached=None)`: fresh solve, observations, A/A_post/settling, contact/energy/tail checks and record construction. | No equivalent current ML output. | Cost of the richer simulator workflow, reported separately without an equivalent-output speedup ratio. |

Even the A-only simulator necessarily integrates motion; the regressor approximates its scalar result. A-only timing omits per-query contact/tail/settling classification, so it is suitable here for the nine previously verified inputs. It cannot establish that an arbitrary new query has physically valid contact or adequate tail behaviour. Users needing post-bump movement, settling or validity diagnostics still require the physical workflow.

## Fixed cases and settings

Use the nine existing low/nominal/high combinations, in stiffness-outer/damping-inner order:

- ks = 18000, 24000, 30000 N/m; cs = 1594.8, 2126.4, 2658 N s/m.
- Training IDs: 001, 008, 015, 106, 113, 120, 211, 218, 225 with the `train_` prefix. They are already verified pilot locations; do not choose cases from final-test errors.
- Existing masses, tyre stiffness and raised-cosine bump: h=0.05 m, duration=0.5 s; initial equilibrium rest; complete exit state retained.
- Baseline RK45: rtol=1e-6, component atol=[1e-9,1e-8,1e-9,1e-8], max_step=0.005 s; horizon 5 s and observation spacing 0.001 s. Retain float64, not a cheaper precision or different target calculation.
- Use the saved final linear and SVR models. No fitting, target/feature change, new search, test evaluation or dataset regeneration.
- Record existing Python/package/platform versions and one numerical-library thread, power state and material competing workload. Keep the laptop under similar conditions throughout. Do not install a profiler or change system settings as part of this bounded experiment.

The nine inputs are fixed timing probes, not new independent accuracy cases or evidence of generalisation. Saved labels may check outputs outside the timed region; they must never substitute for a timed integration.

## Repetitions and exact work budget

Use five measured rounds. Rotate method order deterministically across rounds to reduce a fixed-order advantage; retain every valid duration. Do not discard a slow measurement merely because it weakens a speed claim.

1. For A-only single-query latency, time each of the nine cases separately for simulator, linear and SVR. Each simulation case gets one untimed warm-up plus five measured fresh integrations: 54 integrations total.
2. For A-only batch latency, use one nine-row batch in the same order. The simulator performs nine fresh integrations per call; ML uses one nine-row prediction call. One untimed batch plus five measured batches: another 54 integrations.
3. For the full diagnostic workflow, use the nine individual cases, one warm-up and five timed calls each, with pilot caching explicitly disabled: another 54 integrations. Keep this separate from the primary ratio.
4. For the short ML calls in steps 1-2, use three untimed warm-up calls per model/condition, then five measured blocks of 1000 calls each. Divide each block duration by 1000 to obtain time per call. Record the raw block times and loop count. Each loop must call the actual guarded pipeline; do not memoise outputs. If blocks prove too short to resolve reliably, report that limitation before changing the predeclared loop budget.

This plan has **162 fresh simulation integrations**, all repeats of nine existing setups. They are timing work, not new dataset rows. There are no fits or extra reference solves. Avoid concurrent model calculations or background experiments during measurement. A failed simulation or integrity check stops completion; save failures and any work already done instead of silently omitting cases.

Use elapsed wall-clock timing around the complete callable, following the existing `perf_counter` pattern in this project's scripts. Keep input-array allocation outside the timer equally across methods, but include guards and required parameter construction. Keep logging, file writes and correctness comparisons outside the primary timer. Do not subtract a guessed timer or empty-loop cost.

## Correctness before a timing conclusion

- Before measurement, verify the frozen final model/source fingerprints and exact nine input identities, settings and environment. Keep previous artifact folders unchanged. Save the benchmark plan before timing.
- Use warm-up outputs to check A-only extraction and full diagnostics against each case's saved baseline A. A proposed 1e-8 mm absolute reproduction tolerance allows tiny representation differences under the same algorithm/environment; it is not a physical or ML accuracy tolerance and does not replace the 0.05 mm numerical-refinement criterion.
- The full path must pass the existing row validity checks. All repeated simulations must finish with finite outputs; record derivative-evaluation counts as computational work, not FLOPs.
- Both fitted pipelines must retain their parameter/scaler fingerprints and reproduce their pre-timing predictions after timing. Check that every timed call really executes the intended operation and no case is dropped. No acceptance threshold is imposed on ML errors at these training locations; final accuracy evidence stays the already completed test.
- Compare source, original data and model fingerprints afterward. Save raw timings, flags, method order, software/hardware context and units. Keep failed/partial results distinguishable from a completed benchmark.

## Summaries to save

Report single-query per-case medians with min/max and interquartile ranges over five measured rounds. Simulator observations are individual-call durations; ML observations are five block-average times per call. Label that distinction: the spread between ML block averages does not measure variation among individual requests. For the equal-weight mixture of these nine cases, use the mean of their per-case median times and label that aggregation explicitly. It is not a claim about a different real-use distribution. For batches, report median seconds per nine-case batch, seconds per case and cases per second; batch throughput is distinct from single-query latency.

The primary warm speed ratio is `simulator A-only time / guarded ML A-only time`, using the same workload and aggregation. Report separate linear and SVR ratios; do not present a faster linear prediction as a reason to alter the frozen accuracy-based preference. These ratios are not overall project speedups, and five rounds do not establish a portable statistical guarantee.

No profiling result is required for this first bounded timing experiment. If the measured breakdown identifies a useful question about where time is spent, plan a separate profiler run. The notebook's profilers add overhead and must not be mixed into the uninstrumented comparison. No optimisation is proposed before the timing evidence exists.

## Preparation costs and break-even limits

The model becomes quick to query only after simulations and model development have been paid for. Keep these historical quantities visible, with their original timing boundaries:

| Saved work | Time [s] | Accounting rule |
|---|---:|---|
| 291 new integrations for the 300 development rows | 58.827379 | Included inside their row-processing total below. |
| Row processing for those 300 development rows | 64.383299 | Includes diagnostics but not every export/outer-loop operation; nine rows reuse pilot labels. |
| Nine reused baseline integrations, historical | 1.809785 | Already performed in pilot verification; count once, according to the chosen cost boundary. |
| All 391 new dataset integrations | 78.963229 | Includes the 100 final-test cases; included inside the 86.702437 s dataset-generation loop. Do not add these nested times. |
| Development fitting/scoring loop | 0.114501 | Includes the 0.073261 s spent fitting 19 candidates. |
| 75 tighter validation-reference integrations | 60.116821 | Verification cost, not extra training rows; excludes some orchestration. |
| Final two refits | 0.012923 | Preserve the original measurements; do not refit merely to time them in this stage. |

These were recorded on earlier runs and are a partial cost ledger, not a contemporaneous complete build benchmark. Do not add the development subset to the whole-dataset total, or fit-only time to its enclosing fitting/scoring loop. Pilot verification totals already include the reused baselines; observation-grid/band summaries can reuse the same trajectory and must not be counted as new solves.

For an already built model, report online query time with build costs described as previously incurred. For a new build, define extra preparation cost C relative to the same verified-simulator baseline. State whether C includes development labels, search, reference verification, final assessment, startup/export and other overhead. Shared simulator verification and already available data need explicit treatment; neither automatically disappears nor gets charged twice.

For an explicitly chosen cost boundary and matching single-query workload, the conditional break-even estimate is

\[
N_{\rm break-even}\approx\frac{C}{t_{\rm simulation}-t_{\rm ML}},
\]

only when the denominator is positive. Use batch costs and batch counts for a batch workload. Current timings do not establish the full C or matching query costs. Therefore **no numeric break-even or end-to-end speedup is claimed now**. A later sensitivity calculation using partial historical costs must be labelled conditional; measuring a complete new-build cost would require a separately bounded experiment.

## Course and brief basis

Read before adaptation: Week02_1 `Optimisation_and_Profiling`, one-based cells 76-80 (wall time, repeated runs and loops), 82-85 (whole-block timing and warm execution), 87-90 (workload sizes), 92/94/100 (profiling overhead), 102/104/115 (sampling limits), and 128-130 (system load and precision changes). The notebook has 131 cells, format 4.0, no identified explicit revision; SHA256 `42166ad53117029e35108461b3a4c6607cd2ec38c7aac5ba30e323a3e1640749`.

Source caveat: cell 90 labels its throughput examples as Gvalues/s, but the printed counts/times imply Mvalues/s, a factor of 1000. The example numbers are not copied into this plan. The cell 104 sampling suggestion is not a universal profiler requirement. Notebook installation commands, large arrays and Colab/Linux shell examples were not executed.

The brief pp5-7 requires credible comparisons, relevant performance analysis, engineering interpretation and reproducibility. It recommends timing/profiling and makes hardware-operation analysis conditional on suitability; it does not require a speedup or optimisation of every characteristic. Exact repetition counts, the nine timing inputs and this accounting boundary are project proposals, not assignment requirements. Existing software/data/model fingerprints and source/AI records remain authoritative.
