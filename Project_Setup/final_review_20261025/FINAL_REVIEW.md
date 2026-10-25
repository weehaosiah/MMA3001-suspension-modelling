# Final project-brief and submission review

Date: 25 October 2026. Student: Wee Hao Siah, 33567735.
Reviewed published revision: 1c1ad1f2563779be0bef4adc3c833e1c3274870e,
followed by the bounded local corrections described below. A new publication
and matching clone ZIP are required before submitting the corrected pair.

## Decision and scope

The reviewed project contains the required written-report content and repository
artifact types. The final independent figure check found one factual caption
error: Figure 2 uses the refined 10-second trace, but named a five-second response.
This was corrected locally; the plotted interval and numerical conclusions were
already correct. The remaining draft wording and three supporting links to
excluded originals were also corrected. No material numerical contradiction,
missing primary deliverable, damaged archive or blocking layout defect was found.

Recommendation: publish these bounded corrections, verify the new revision and
make its matching clone ZIP, then submit. The old 1c1ad1f archive is preserved as
historical evidence and does not contain these changes. This is not a claim that
every rubric descriptor is excellent, that the work has been rebuilt in a clean
environment, or that submission is complete. The student explicitly confirmed:
not submitted yet.

The review reread the original 15-page brief, all 14 responsible-AI notebook
cells, current guide003/state051 and the exact final 10-page PDF. Three independent
review tasks covered requirements/AI, scientific evidence, and repository/docs.
Root checked current GitHub metadata, archive integrity, source references,
Python syntax without execution, report metadata and visual layout.

## Authoritative sources and versions

- MMA3001_2026_Project_Brief.pdf, 15 pages, no printed revision identified.
  SHA-256: 1029cf7c7c2844161af0c3727bbcbf40fac3913575683defe34ee942f9a9550c.
  Requirements pp1-8, presentation p9, rubric pp10-15. The file matches the
  previously audited source; no newer authoritative brief was found locally.
- MMA3001_Notes_Week01_4_Responsible_Use_of_AI.ipynb, 14 cells, no numbered
  revision identified. SHA-256:
  11f8aed9e9f1a6e5503a06a466424aaddf0eb78818eb50c1b796381a800daef6.
- PROJECT_GUIDE revision003; working state/evidence/AI log051 and checklist022
  at the start. Published clone records remain050/checklist021.
- The 25 October 2026, 23:59 Australia/Sydney extension and PDF-plus-ZIP Moodle
  directions are student-reported. The brief refers dates to the Unit Overview
  Spreadsheet; no authoritative schedule/extension notice or live Moodle form
  was inspected. Earlier 23 October records are superseded by the student's
  reported extension. School-email verification was previously student-confirmed;
  it is not an explicit requirement in the inspected brief.

## Requirement-by-requirement result

| Brief requirement | Final evidence | Result and qualification |
| --- | --- | --- |
| Engineering relevance, question, purpose and scope, pp2/4/7 | Report pp1-2: passive quarter-car, simulated-setup comparison, fixed bump and two-parameter domain | Present; no identified-vehicle validation claimed |
| Input format, units, domain, output meaning and invalid inputs, p4 | Report p2 and interface/source documentation | Present: nonempty N by 2 stiffness/damping arrays, finite/in-domain guards, output in mm |
| Numerical/ML approach, assumptions and settings, pp2/4/7 | Report pp2-4; quarter_car.py and stage modules | Present: equations, equilibrium coordinates, RK45 and regression; taught-method/source attribution recorded |
| Credible alternative and justified selection, pp5-6 | Report pp4-5/7; development and final saved evidence | Present: linear baseline versus bounded SVR selection, frozen refit and test; no universal optimum claim |
| Verification/validation design, criteria and limits, p5 | Report pp3-6/8; numerical, dataset and final evaluation records | Present: analytical diagnostic, RK4/refinement/horizon/physical checks, separate data roles and error metrics |
| Performance analysis, timing/profiling and appropriate optimisation, p6 | Report p7; runtime_benchmark_v2 and profiling_v1 | Present: comparable output timing, profiler overhead/cost paths and accuracy/runtime trade-offs; future optimisation clearly unmeasured |
| AI tools, tasks, approximate contribution, reasons, checks, decisions, errors and learning, p6 | Report p9 and dated AI/student-review records | All eight points present; substantial AI implementation/execution remains disclosed |
| Individual report, 5-10 main pages and references, p8 | Exact submission PDF: nine main pages plus one reference page | Pass for length/content; identity correct; no unresolved review markers, comments or tracked changes |
| README, HTML documentation, licence, source/main, inline comments/docstrings, tests and test report, p8 | Fixed main clone, MIT licence, generated docs, 11 test modules and saved transcripts | All artifact types present; function depth and clean-environment reproduction have limits below |
| Version-controlled workflow and accessible final repository, pp2/8 | Public main at reviewed commit; 14 meaningful commits with retained attribution | Present; current remote/local/clone agree |
| ZIP of an actual clone through Moodle, p8 | Published 1c1ad1f clone ZIP passes all integrity checks | Replacement ZIP required after the final caption correction is published; Moodle remains pending |
| Presentation/demo and questions, pp8-9 | Five-minute presentation plus three-minute questions required | Still required; preparation/date planning deferred at student's instruction; not claimed complete |
| Prior discussion/approval of student-proposed topic/data, pp1-2 | Student-reported approval in project history | Independent teaching-team record not inspected; retain actual approval evidence if available |

FLOPS and arithmetic intensity are qualified by where appropriate in the brief.
It does not require every possible optimisation, a PINN, experimental telemetry,
an exact AI percentage or a specific licence. Public visibility is a valid way
to meet accessibility; the brief does not specifically demand public visibility.

## Six rubric criteria

| Criterion | Evidence and honest assessment |
| --- | --- |
| Engineering problem, inputs and outputs, p10 | Concrete definitions, units, ranges, purpose and limitations in report pp1-2. Primary output remains whole-response max abs(zs-zu), from equilibrium. |
| Repository structure, commits and README, p11 | Logical code/results/records structure, meaningful staged history, environment and workflow instructions. Clean installation and full rebuild are not established. |
| Inline comments, docstrings and HTML, p12 | 96 public functions across 18 documented modules have docstrings and HTML anchors. Some helpers have short descriptions; uniform comprehensive parameter/return/exception/usage coverage is not established. |
| Validation and engineering credibility, p13 | Quantitative numerical and ML checks, stated criteria and physical/domain limits. Nine pilots received full refinement; no certified error bound or real-vehicle validation. |
| Computational justification, p14 | Credible baseline, bounded candidate search, resolution choices, sampled sensitivity, timing and profiling. No unsupported end-to-end speedup or implemented future optimisation claim. |
| AI use and critical reflection, p15 | Student direction and judgement, substantial AI contribution, checks, corrections and learning limits are explicit. Written reflection does not establish unaided oral mastery. |

No grade or numeric rubric score is assigned. The brief gives the project an
overall 25% weighting but no separate weights for these six rows.

## Actual checks of the published 1c1ad1f package

- Fresh GitHub metadata confirms public main at 1c1ad1f; local Git and fixed
  clone match. All 189 tracked files and 14 commit identities agree.
- A new extraction of the unchanged ZIP passes Git integrity checks and has a
  clean working tree. CRC and all 217 member bytes pass, including 28 Git
  metadata files. No course originals, temporary renders or unexpected project
  files are included.
- ZIP SHA-256:
  489375f470a20c1a16a680aff3d910f07ac5bf5450ac5eb6f5a979f768faac2e.
  Size: 15,696,966 bytes.
- PDF SHA-256:
  0c5f3158ed3c295224c7f8f6af017ae7a16c51d7d65bae0da30f074008b4ab0a.
  It is byte-identical to the reviewed PDF inside the clone and ZIP.
- DOCX SHA-256:
  9e253d0aa3ee89e0757c29974e243d8b2a8bc4bd41330ae5ca1030ca2dcb6ecb.
  No tracked insertions/deletions or comment anchors. Name and ID are correct.
- All 10 PDF pages were newly rendered and inspected as complete page overviews;
  equations, plots, results and references also received enlarged inspection.
  No clipped content, overlap, missing symbols or blocking layout issue found.
- Static parsing passes for all 32 Python files. This checks syntax without
  importing project modules, running tests or claiming functional execution.
- All 108 local links across 19 HTML pages pass. Primary README/reproduction
  links and local Markdown heading anchors work. Of 223 local Markdown targets
  in 41 files, three refer to deliberately excluded original course files;
  these are identified below.
- Saved evidence includes 433 passing implementation tests and the separate
  13 passing profiler tests, from distinct dated scopes. These were inspected,
  not rerun or added together as a new full-suite result.
- Protected heldout_test/README.md still matches the dataset manifest. The
  current DATASET.md clarification explains that final evaluation subsequently
  consumed the test cases. Historical records were not rewritten.

The first comparison against an older extraction noticed a Git index stat-cache
refresh caused by a status read. No archive or project content changed. The
reviewer corrected the checker to disable optional Git writes and validated a
fresh extraction: all 217 member bytes remain identical after Git checks. See
package_checks.json and verify_package.py for the actual receipt and procedure.

## Source references

Official pages were reopened on 25 October 2026: [KU Leuven model](https://fet-edu-em.pages.gitlab.kuleuven.be/computer-aided-simulation/course-material/t42cms-cas-book/t42cms-cas-lectures/Examples/Quarter_car_suspension/Quarter_car_suspension_model.html),
[MathWorks bump example](https://www.mathworks.com/help/robust/gs/active-suspension-control-design.html),
[SciPy 1.13.1](https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.integrate.solve_ivp.html),
[scikit-learn 1.5 documentation](https://scikit-learn.org/1.5/modules/generated/sklearn.svm.SVR.html),
and [Python 3.12 profiler documentation](https://docs.python.org/3.12/library/profile.html).
They support the equations/equilibrium convention, adapted bump, RK45 controls,
SVR settings/loss interpretation and profiling caveats respectively.

The [PLOS primary article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179485)
is accessible and matches the title/authors/date and generic-vehicle context.
Direct DOI/table-image access failed in the browsing tool and PMC direct access
returned a challenge/cache miss. The indexed primary PMC article was visible,
but a full fresh visual Table 2 check is not claimed. The previously recorded
Table 2 checks remain the provenance for the five nominal coefficients. Tool
retrieval failure alone does not establish that the published citation is broken.

## Remaining issues and disposition

1. **Moodle submission: outstanding.** Student says not submitted yet. Upload the
   matching pair, supply the accessible repository link where requested, check
   the actual form/limits and obtain final submitted confirmation before the
   student-confirmed deadline. No assistant submission or declaration made.
2. **Reproducibility: qualified and disclosed.** Strict final/runtime audits
   require four exact excluded course originals; some historical runners/tests
   also require two ODE notebooks. Existing Windows/Anaconda checks are saved.
   Clean installation, other OS and a complete fresh rebuild are unverified.
   REPRODUCING.md and report p8 explain this. Do not claim standalone portability.
3. **Supporting course links: corrected locally.** The three links in
   PROGRESS_REPORT.md and AI_REFLECTION_REVIEW.md now use explicit original
   filenames and authorised-access/exclusion notes. Source names and hashes
   remain available. Current tracked-file checks find zero broken Markdown or
   HTML links. No course original was redistributed.
4. **Documentation depth: remaining rubric weakness.** Docstrings/HTML cover
   the checked public functions, but some helper descriptions are short.
   Presence is verified; the highest rubric descriptor is not asserted.
5. **Approval, AI traceability and mastery: evidence limits.** Topic approval
   and the extension are student-reported; exact historical AI model versions
   and Claude session details are unavailable. The report discloses unknown
   model versions and does not claim independent coding mastery or that AI
   agreement proves physics. Preserve actual records; do not invent evidence.
6. **Presentation: separate outstanding requirement.** Required by the brief,
   including questions without AI assistance. Date planning remains deferred.
7. **Figure 2 and final wording: corrected locally.** Figure 2 now accurately
   identifies the refined 10-second source; report p8 now says report rather
   than draft. Earlier dated working-stage records retain their history. These
   edits preserve scientific results and the full student/AI reflection.

## Correction verification

- Source evidence: run_nominal.py samples extended10 when writing
  results/nominal_trace_1ms.csv, whose last timestamp is 10 s. The graph shows
  only 0-2.5 s; the correction concerns source duration, not plotted values.
- Two report paragraphs changed. All six tables, three native equations,
  embedded figures, 20 other DOCX package parts and Section 9 are unchanged.
- All 155 files under Suspension_Model are byte-identical to the verified clone.
  No new simulation, fitting, prediction, benchmark or test suite was run.
- Corrected DOCX SHA-256:
  4bfc7aa7e5330fec839cbdbc05d254fbc8385f9bf323b0c2152f327277da8d32.
- Corrected PDF SHA-256:
  22102e2d34a61667adccd28f11ea6ca7c80453d77a1eb882c20c09a5e3d20524.
- Ten pages remain: nine main pages and references. Pages 6 and 8 pass visual
  review; the other eight pages are pixel-identical to the reviewed published
  report. All pages were inspected. The PDF in output/pdf matches the export.
- Packaged DOCX rendering failed because bundled soffice was unavailable;
  the established read-only Word export and PDF rendering fallback succeeded.
  The DOCX bytes were unchanged during export. No desktop LibreOffice was used.
- Final current-file check after saving this review: 42 Markdown files
  (41 existing tracked files plus this receipt), 222 local targets, zero missing
  paths/anchors; 19 HTML pages, 108 local links, zero failures. Upload wording
  consistently requires the new student push and matching ZIP before Moodle.
- All reported nominal, pilot, development, final-test, interpretation, runtime
  and profiling values match the saved summaries to stated rounding. Examples:
  nominal A 40.571155 mm; post-bump peak 31.891620 mm; settling 1.269332 s;
  largest pilot A comparison 0.000464924 mm; final RMSE 0.029796 mm for SVR
  and 0.199436 mm for linear regression. No raw held-out reanalysis occurred.

No model/code/result edit, new prediction, benchmark, dataset generation,
test-suite execution, commit/push or access change occurred. The final
documentation correction requires a new student commit/push and matching ZIP;
the assistant preserves that student-led publication boundary.

## Files to submit

- Corrected report: output/pdf/MMA3001_suspension_report.pdf.
- Clone ZIP: prepare from the new published revision after the student's push.
- Repository link: https://github.com/weehaosiah/MMA3001-suspension-modelling

Submit the PDF and ZIP as the student confirmed Moodle requests. The review
receipt, machine-readable check file and preview images are not extra assessed
deliverables. Do not pair the corrected PDF with the old 1c1ad1f ZIP. Preserve
the old pair as history, use the replacement pair after verification and save
the Moodle receipt.
