# Project progress review

Updated: 12 October 2026 | Revision: 002 | Administrative progress review, not the assessed report

The core computational stages and bounded nominal profiling study are complete,
with saved verification evidence. The project is not yet ready for final
submission: student explanation, the assessed report/AI reflection, assessor
reproduction/access and final packaging remain.

## Current update, 12 October 2026

The authorised profiler study repeated the unchanged nominal full-diagnostic
simulation seven times: one warmup and three alternating unprofiled/profiled
pairs. All five study checks pass. Every non-timing summary exactly matches the
saved baseline, including 6196 derivative evaluations per solve, and all 120
protected scientific/course files remain unchanged. No new dataset rows, ML
fitting/prediction or consumed-test tuning occurred. See
[actual profiling results](../Suspension_Model/profiling_v1/CHECK_RESULTS.md) and
[the profiling guide](../Suspension_Model/PROFILING_GUIDE.md).

Thirteen focused bookkeeping tests passed in 0.90 s; the historical 433-test
suite was not rerun. The [test record](../Suspension_Model/profiling_v1/TEST_RESULTS.md)
retains the initial temporary-directory setup failure and subsequent corrections.
The saved-profile audit also passes without another solve. Local HTML
documentation now contains 19 pages with 108 local links checked. This is a local
check, distinct from the earlier clone's 17 pages and 98 links.

Unprofiled median wall time was 413.608 ms and profiled median 524.979 ms; the
median paired ratio was 1.328338. Instrumentation overhead and timing noise are
included. These nominal full-diagnostic observations must not be combined with
the earlier nine-case peak-query benchmark into a speedup or regression claim.
The road-height function had the largest self-time share in all three profiles.
A specialised scalar path is a possible future optimisation, not a tested
improvement. The decision is to retain the correct implementation, precision,
tolerances and post-bump diagnostics. No memory/FLOPS measurement or general
performance guarantee is claimed.

The first two student walkthrough replies show limited understanding of
inertia/velocity continuity and why displacement alone cannot establish motion.
The notation was corrected: zs = zu = 20 mm gives zs - zu = 0 mm; it does not
establish that either velocity is zero. These replies do not establish full
understanding of the model, code, checks or AI contribution.
In a third example, the student correctly chose 40 mm as the primary peak from
+30 mm during the bump and -40 mm afterward, and recognised that stopping at bump
exit would miss the true peak. The 70 mm difference was clarified as the
peak-to-peak range, not accumulated travel. This is specific evidence of the
full-response definition, not broader mastery.

This stage read guide003 and current records031, reread brief p6 and relevant
Week02_1 timing/profiling cells, and read the saved profiling evidence. It did not
repeat the full 15-page brief review described below. The course teaches
line_profiler and Scalene; built-in cProfile is a documented extension.
No remote check, commit or push occurred. The last remotely verified checkpoint
remains the dated 11 October result below; subsequent evidence is still local.
No assessed report was written.

## Basis of the 11 October review

On 11 October, reread all 15 pages of the original [project brief](../MMA3001_2026_Project_Brief.pdf),
HANDOFF001, PROJECT_GUIDE003 and the current sections of state/evidence/AI027.
The brief has no visible numbered revision. Its SHA-256 is unchanged:
`1029cf7c7c2844161af0c3727bbcbf40fac3913575683defe34ee942f9a9550c`.
An independent assistant rechecked pp6,8,9 and the requirements mapping.
No newer brief was found in the visible project files. The Unit Overview
Spreadsheet, current Moodle form and a separate written approval/clarification
record remain unavailable. Topic approval and the deadline remain student-reported.

The old handoff's revision013/no-implementation description is historical. Later
authorised stages and records027 superseded it. That review updated records to028
and corrected stale undated summaries near the bottom of PROJECT_STATE.

## Completed work and actual evidence: 11 October snapshot

This table retains the earlier checkpoint. The profiling, focused-test and local
HTML additions are recorded in the dated current update above; no fresh remote
or clone verification is implied.

| Area | Completed work and evidence |
|---|---|
| Physical model and output | Passive two-mass quarter-car model, starting from static equilibrium. The primary output remains the largest absolute suspension-relative displacement over the full response: max abs(zs-zu), including after the bump. Post-bump movement and relative settling remain supporting priorities. |
| Nominal simulation | Initial checks pass. Full-response peak 40.571155 mm; post-bump peak 31.891620 mm; relative settling 1.269332 s after bump exit within the adopted +/-1 mm band. [Saved results](../Suspension_Model/results/CHECK_RESULTS.md). |
| Numerical verification | Bounded nine-setup verification, alternative numerical/analytical comparisons and resolution/tail checks completed. These test the implementation and adopted numerical choices; they do not validate a real vehicle. [Verification record](../Suspension_Model/verification_results/CHECK_RESULTS.md). |
| Dataset | 400 simulated suspension setups, varying spring stiffness and damping: 225 training, 75 validation and 100 reserved final-test cases. All 400 pass the adopted row checks. These are generated model outputs, not measured car data. [Dataset checks](../Suspension_Model/dataset_v1/CHECK_RESULTS.md). |
| ML comparison | Linear regression compared with support vector regression (SVR), a fitted predictor of the simulated peak. Selection used development data; both final models were fitted on 300 development rows, then evaluated once on the 100 reserved cases. Final RMSE: linear 0.199436 mm; SVR 0.029796 mm. RMSE summarises prediction error and weights larger errors more strongly. [Final results](../Suspension_Model/final_evaluation_v1/CHECK_RESULTS.md). |
| Physical interpretation | Saved analysis distinguishes maximum post-bump movement from how long relative movement takes to settle. A lower post-bump peak need not mean faster settling. Neither output alone establishes comfort, clearance or safety. [Interpretation checks](../Suspension_Model/interpretation_v1/CHECK_RESULTS.md). |
| Runtime comparison | Seven recorded benchmark checks pass. Warm single-query means of nine case medians: simulation 222.637844 ms; SVR 0.163470 ms. Warm means software/models already loaded; startup, dataset generation and training are excluded. [Runtime evidence](../Suspension_Model/runtime_benchmark_v2/CHECK_RESULTS.md). |
| Tests and documentation | Latest saved test log: 433 passed in 6.15 s. README, source comments/docstrings, reproduction instructions and HTML documentation exist. Real-clone static checks found zero broken links among 98 links in 17 HTML pages. Link checks do not establish the quality of every explanation. |
| GitHub and licence | Private repository on main; MIT licence uploaded; school-email verification student-confirmed. Fresh local/remote check agrees at 8ba9808f10dcdc84330135870d8b7f92c189f0a8, with 12 local commits. [Uploaded checkpoint](https://github.com/weehaosiah/MMA3001-suspension-modelling/commit/8ba9808f10dcdc84330135870d8b7f92c189f0a8). |
| Real-clone verification | Three saved-output audits and all nine declared clone checks passed in the preceding stage. Same existing Windows/Anaconda environment; two audits needed four excluded course originals restored locally. [Actual clone checks](clone_review_v1/CHECK_RESULTS.md). |

The final test has already been used. It cannot be reused as an unseen test after
changing settings in response to its results. Accuracy means agreement with the
simulation within the sampled scope, not demonstrated real-vehicle accuracy.
A clean installation, other operating system and complete rebuild have not been
verified. No scientific tests, simulations, fitting or timing were rerun for the
11 October administrative review. The later seven profiling repeats and focused
tests are recorded separately above.

## Next steps, updated 12 October

1. Continue the student's walkthrough of the model, data splits, checks and
   results, including the profiler findings. Review actual AI contribution,
   student decisions, verification, mistakes and learning. The first three replies
   and the AI log support this work but do not replace a fuller explanation.
   Preserve the consumed final test; do not tune models against its results.
2. Review how an assessor can reproduce the documented work and access the
   private repository and required course sources. The assistant's authenticated
   access is not proof of assessor access. Check current Moodle/Unit Overview
   instructions for report format, link location and later teaching instructions.
   The older final/runtime audits retain their source prerequisites; the new
   profile audit reports absent course files and can inspect saved results without
   them. Neither establishes a clean installation or complete rebuild.
3. Student reviews, commits and pushes pending evidence from the original project
   folder. A commit saves a named local snapshot; a push uploads those commits to
   GitHub. The latest work remains local; no assistant commit/push or new remote
   verification occurred in this stage. Leave both extra local copies alone.
4. Only when report writing is explicitly authorised, prepare the individual report: aim for
   5-10 main-text pages, with a clear maximum of 10 excluding references and
   appendices. Cover the eight p8 areas, including baseline comparison,
   limitations and the required AI reflection. No assessed report exists yet.
5. Review final consistency, check relevant changes, commit/push the final revision
   and make a new clean clone for the submission ZIP. Do not ZIP the current
   verification clone: it contains ignored course originals. Submit the report,
   clone ZIP and accessible repository link as directed by Moodle; verify the
   uploaded files and submission confirmation.

Working deadline: **23 October 2026 at 23:59 Sydney time**, supplied by the student.
The brief points elsewhere for dates and does not independently confirm this one.
The five-minute presentation plus three-minute questions remains required;
presentation-date planning stays deferred.

See [the requirement-by-requirement checklist](SUBMISSION_CHECKLIST.md) for the
complete mapping. This update records the completed bounded profiling stage and
limited walkthrough evidence; it does not authorise further experiments,
report drafting or submission.
