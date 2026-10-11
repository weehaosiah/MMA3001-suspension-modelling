# Brief reconciliation and submission checklist

Revision: 002 | Checked: 2026-10-11 | Scope: requirements audit, not assessed report text

## Sources and current checkpoint

Read all 15 pages of the local MMA3001_2026_Project_Brief.pdf. The source has no
numbered revision visible in its text; its SHA-256 remains
`1029cf7c7c2844161af0c3727bbcbf40fac3913575683defe34ee942f9a9550c`.
Pages 6, 8 and 11 were also rendered and visually checked by the main assistant;
an independent assistant reread the complete brief and checked relevant page images.
Page numbers below are the printed PDF page numbers.

Also read PROJECT_GUIDE003 and current records024, the upload/publication notes,
README, reproduction instructions and repository-review evidence. The original
HANDOFF001 and revision013 description are historical; later authorised work is
recorded in the current state. This audit does not reopen topic selection.

Verified GitHub repository: https://github.com/weehaosiah/MMA3001-suspension-modelling.
It is private, owned by weehaosiah, with default branch main. Local and remote head
both equal `db1532988a5d5c1409431318367316d45befd28b`, tree
`8253661c7392d87c51f2a492c3c2a0597cff0ba6`. There are 136 tracked files and 11 local
commits. The previous 10-commit upload was verified in full; this new commit has
that verified head as its parent and changes only four project-record files.
Local status was clean before this audit's documentation edits.

The Unit Overview Spreadsheet, current Moodle submission form and any separate
teaching-team clarification/approval record were not found among the visible
project files. The working deadline remains the student's explicit
**23 October 2026 at 23:59 Australia/Sydney**. The brief itself directs readers to
the Unit Overview Spreadsheet for dates; this audit cannot independently confirm
that date, the Moodle URL field, upload format/size limits or later instructions.
Topic approval remains user-reported, without a separately inspected approval record.

## Requirements compared with existing work

| Brief requirement | Current evidence/status | Remaining action |
|---|---|---|
| Appropriate engineering problem and approved student-proposed scope/data (pp1-3) | Suspension scope and approval are student-reported; simulations are explicitly allowed on p3. | Preserve the approval record if available; no new topic selection. |
| Clear context, intended use, inputs/outputs, units/domains and unsupported-input handling (pp4,10) | Model guides, code guards and working records exist. Primary target remains full-response max abs(zs-zu), from static equilibrium, including after the bump. | Explain these clearly in the final report and in the student's own words. Post-bump/settling diagnostics remain separate. |
| At least one numerical and/or ML method taught in the unit; functioning reproducible workflow (pp2,4,7) | RK45/RK4 verification, linear regression and SVR, saved data/models and pinned direct dependencies exist. | Complete a final-clone reproduction check and document prerequisites/limits. No requirement to execute every course notebook. |
| Credible alternative/baseline and justified comparison (pp5,6,14) | Linear versus SVR accuracy evidence and bounded runtime comparison exist. | Explain why the selected method suits the question and its trade-offs. Do not invent a requirement to test every model/metric. |
| Justified validation, acceptance criteria, selection influence and limits (pp5,13) | Numerical checks, physical consistency, training/validation split and once-only final test are recorded. | Explain that simulated labels are not real-vehicle measurements; preserve the consumed-test boundary and avoid tuning against test results. |
| Performance analysis and relevant improvement (pp6,14) | Timing, numerical refinement and model comparison exist. No saved profiler study identified. | Address p6's recommendation to use profilers and timing routines through a bounded later task or teaching clarification. FLOPS/arithmetic-intensity estimates are conditional on relevance, not an automatic requirement for every project. |
| README, logical structure and meaningful history (pp8,11) | Root/stage READMEs and 11 local commits; current upload verified. | Correct stale upload wording and keep committing/pushing during remaining work. Do not claim GitHub was hosted throughout earlier local development. |
| HTML source documentation, comments and docstrings (pp8,12) | 17 tracked HTML pages in total, including the index; comments/docstrings and generation instructions exist. | Final check that documentation stays consistent with source and opens from the clone. The brief does not require a public documentation website or a specific generator. |
| Licensing agreement (p8) | Student selected MIT; standard LICENSE prepared locally with configured Git name weehaosiah. | Review, commit and push it. Scope is original software and associated authored documentation; third-party/course material retains its own terms. MIT is a student choice, not a course mandate. |
| Source code on a functional main branch (p8) | Main exists and matches GitHub. Earlier implementation checks are saved. | A matching Git commit does not itself establish a fresh-environment execution; check final-clone usability. |
| Test functions and test report (p8) | Ten tracked test modules, seven stage CHECK_RESULTS reports and pytest logs. Latest saved result is 433 passed in 6.15 s. | Present the existing evidence and any later checks accurately. No new full test run occurred in this audit; no specific TEST_REPORT.md filename is required. |
| Accessible final GitHub link (p8) | Private repository and authenticated assistant access confirmed. | Confirm the actual assessor access method and verify it. The brief does not explicitly require public visibility. |
| Individual written documentation, 5-10 pages maximum (p8) | No assessed report exists. | Aim for 5-10 main-text pages; the explicit cap is 10 pages excluding references/appendices. The wording does not clearly establish a strict five-page minimum. No LaTeX/Word/PDF, font or margin rule was found in this brief; check Moodle for file-format instructions. |
| Material AI disclosure and critical reflection (pp6,15) | Detailed AI_USE_LOG exists; substantial implementation and documentation assistance is recorded. | Student reviews approximate contribution, reasons, decisions, verification, mistakes and effects on understanding. The log does not replace the required final reflection or independent understanding. |
| Report and zipped clone through Moodle, plus accessible repository link (p8) | Initial upload and one student update are verified; no final clone ZIP or Moodle completion evidence exists. | Follow the final packaging/submission sequence below. Uploading to GitHub alone is not final submission. |
| Individual presentation/demonstration and questions (pp6,9) | Still required: 5-minute presentation plus 3 minutes of questions; preparation not claimed. | Retain the demonstration/attendance requirement and student's ability to explain the work without AI during questions. Presentation-date planning remains deferred. |

## Clarifications to earlier guidance

- **Licence:** p8 explicitly asks for a licensing agreement. It does not prescribe
  MIT or even a named open-source licence. GitHub itself allows repositories without
  a licence, but that does not remove this assignment's requirement. See
  [GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
- **Account:** using a school-email account remains the student's instruction.
  No such rule was found in the brief. The student now confirms the school email is
  verified; the tool does not independently expose that flag or primary status. The brief
  does not require exposing the school email in public commit metadata.
- **Visibility/access:** private hosting is the student's current setting and was
  recommended for work in progress. It is not a substitute for assessor access.
  Agree the assessor's username/access procedure before adding anyone. Accepted
  invitations grant collaborator access, as described in
  [GitHub's access instructions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository).
- **Desktop/branches:** GitHub Desktop is a beginner-friendly choice, not a required
  application. The rubric allows branching and/or insightful commits; it does not
  require a new branch or pull request for every change. Preserve genuine history.
- **ZIP:** the brief explicitly says a zipped clone. Retaining the clone's hidden
  .git folder is our recommendation to preserve history; .git is not separately
  named in the brief. Ordinary GitHub Download ZIP provides a snapshot without
  full history, as explained in [GitHub's archive documentation](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).
- **Reproducibility:** the prior relocated-copy check used the existing Windows/
  Anaconda environment and restored authorised course sources. It was not a fresh
  GitHub clone or clean installation. Strict final/runtime audits require excluded
  course files; historical tests/runners have further source/environment guards.
  Follow [REPRODUCING.md](../Suspension_Model/REPRODUCING.md). Do not remove checks or
  redistribute course originals merely to hide these limitations.

## Reconfirmed order of remaining work

1. School-email verification is now student-confirmed. Check the current Moodle/
   Unit Overview instructions and record any actual course clarification separately.
   Determine how the assessor should access the private repository.
2. MIT is now selected and prepared using configured author name weehaosiah. Review
   the licence and documentation corrections, then let the student commit and push.
3. Review the student's understanding of the model, primary peak, post-bump/settling
   outputs, data splits, validation limits and AI contribution. Address the profiler
   recommendation without silently rerunning the full dataset or tuning models.
4. Check the repository from a separate real clone, preserving the original
   scientific checkpoint. Check instructions, required environment/source access,
   HTML and relevant tests/audits. Record failures honestly. A clean installation
   is a useful stronger check, not wording explicitly demanded by the brief.
5. When report writing is authorised, prepare the 5-10-page individual report with
   the eight p8 content areas: engineering problem; inputs/outputs/data; approach;
   validation/results; comparison/optimisation; limitations/lessons; AI reflection;
   references. Keep the source documentation and report consistent.
6. Review the final code, documentation, licence, saved tests, report, references
   and access. Save, commit and push the final repository changes. Confirm the
   final local and GitHub commit agree.
7. Make a new clone of that final remote revision in a separate empty folder.
   Check its files/history, then ZIP the clone. Retain .git as the documented
   history-preservation recommendation. Inspect the ZIP; do not ZIP the mixed
   OneDrive workspace, because manual ZIP tools do not apply .gitignore rules.
8. Submit the written report and clone ZIP through Moodle and provide the accessible
   repository link in the location required by the current submission form.
   Check uploaded files and submission confirmation before the recorded deadline.

The original audit did not change licence, identity, visibility, collaborators or
remote files. In the subsequent authorised continuation, the student selected MIT
and a local LICENSE was added. The assistant attempted a separate GitHub clone;
the restricted attempt failed at network resolution, and an allowed network retry
could not authenticate non-interactively. No clone or audit result is claimed;
use GitHub Desktop for the verification copy. No simulation, dataset generation,
ML fitting/prediction, profiler run, full test suite or report writing occurred.
Source originals remain unchanged. Licence and records await student commit/push.
