# MMA3001 suspension modelling

Start with [the reproduction guide](Suspension_Model/REPRODUCING.md) to check
saved results, then [the physical/code walkthrough](Suspension_Model/WALKTHROUGH.md)
to connect the calculations to the suspension. The
[function documentation index](Suspension_Model/docs/index.html) explains the code.

The authored project is in `Suspension_Model/`; decisions, sources and AI assistance
are in `Project_Setup/`. The original course notebooks and brief are preserved in
this folder but excluded from version control to avoid redistributing course material.

The primary output is **max |zs(t) - zu(t)|** over the full response, measured from
static equilibrium and including after the bump. Post-bump movement and settling
remain separate physical diagnostics; the fitted models predict the primary peak only.

The nominal simulation, nine-pilot verification, 400-setup dataset, development
comparison, final evaluation and bounded runtime comparison are complete.
The selected SVR and linear comparator were refitted on 300 development rows and
evaluated once on 100 reserved cases. Those test cases are now consumed and cannot
be used to tune models while retaining an independent-test claim.

| Read | Purpose |
|---|---|
| [Simulation guide](Suspension_Model/README.md) | Model, nominal checks and original implementation |
| [Dataset guide](Suspension_Model/DATASET.md) | 225 training / 75 validation / 100 test setup design |
| [ML development](Suspension_Model/ML_GUIDE.md) | Training, scaling and validation-based model choice |
| [Final evaluation](Suspension_Model/FINAL_EVALUATION_GUIDE.md) | Frozen models and once-only accuracy results |
| [Physical interpretation](Suspension_Model/PHYSICS_REVIEW.md) | Post-bump peak versus settling |
| [Runtime guide](Suspension_Model/RUNTIME_GUIDE.md) | Measured warm query costs and their limits |
| [Nominal profiling](Suspension_Model/PROFILING_GUIDE.md) | Where the unchanged full-diagnostic simulation spends time; profiler overhead |
| [Repository review](Project_Setup/REPOSITORY_REVIEW.md) | Actual reproduction checks and outstanding submission work |

The latest implementation checkpoint records 433 passing tests. See each stage's
saved check report for its actual results; checking saved records does not rerun
the experiments. A [report draft](Report_Draft/MMA3001_suspension_report_draft.docx)
was prepared on 22 October 2026 with nine main pages and one reference page.
The supplied identity, student explanations, engineering judgement and personal
AI reflection were incorporated on25 October; no R1-R7 prompts remain. The
[submission PDF](output/pdf/MMA3001_suspension_report.pdf) is prepared for the
student-confirmed Moodle format. Final personal reading remains. The report and later local work
are awaiting student commit/push; GitHub main was rechecked on25 October and
still points to8ba9808. See the [final upload check](Project_Setup/FINAL_UPLOAD_CHECK.md).
The separate 12 October profiling stage adds 13 passing focused tests and seven
nominal repeats with five study checks passed; it does not rerun that full suite.
All prior scientific results remain unchanged. See [actual profiling results](Suspension_Model/profiling_v1/CHECK_RESULTS.md).
Extended submission deadline confirmed by the student on24 October: **25 October 2026, 23:59 Australia/Sydney**.
Presentation-date planning remains deferred.

The student has published the project to the private
[GitHub repository](https://github.com/weehaosiah/MMA3001-suspension-modelling).
The published checkpoint `8ba9808` passed all three saved-output audits in a real
GitHub Desktop clone on 11 October 2026, using the existing environment and the
documented course prerequisites. See [clone check results](Project_Setup/clone_review_v1/CHECK_RESULTS.md).
Existing AI-created commits retain their attribution. A commit saves a local checkpoint;
a push uploads it. Verified assessor access, final publication, the clone ZIP and
Moodle submission remain outstanding. See the [brief reconciliation and submission checklist](Project_Setup/SUBMISSION_CHECKLIST.md)
for requirements, current evidence and the remaining steps.

The project's original software and associated authored documentation are licensed
under the [MIT licence](LICENSE), selected by the student on 11 October 2026.
The notice uses the student's configured Git author name, `weehaosiah`. Course
originals, cited external material and third-party dependencies retain their own
terms; this licence does not relicense them. AI assistance remains disclosed in
the project records.
Current decisions, source evidence and material AI assistance are recorded in
[Project_Setup](Project_Setup/PROJECT_STATE.md).
