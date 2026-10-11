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
| [Repository review](Project_Setup/REPOSITORY_REVIEW.md) | Actual reproduction checks and outstanding submission work |

The latest implementation checkpoint records 433 passing tests. See each stage's
saved check report for its actual results; checking saved records does not rerun
the experiments. No assessed report has been written.
Submission deadline supplied by the student: **23 October 2026, 23:59 Australia/Sydney**.
Presentation-date planning remains deferred.

The student has published the project to the private
[GitHub repository](https://github.com/weehaosiah/MMA3001-suspension-modelling).
On 11 October 2026, local and remote main matched at `db15329`; existing
AI-created commits retain their attribution. A commit saves a local checkpoint;
a push uploads it. Verified assessor access, the final report and clone ZIP remain
outstanding. See the [brief reconciliation and submission checklist](Project_Setup/SUBMISSION_CHECKLIST.md)
for requirements, current evidence and the remaining steps.

The project's original software and associated authored documentation are licensed
under the [MIT licence](LICENSE), selected by the student on 11 October 2026.
The notice uses the student's configured Git author name, `weehaosiah`. Course
originals, cited external material and third-party dependencies retain their own
terms; this licence does not relicense them. AI assistance remains disclosed in
the project records.
Current decisions, source evidence and material AI assistance are recorded in
[Project_Setup](Project_Setup/PROJECT_STATE.md).
