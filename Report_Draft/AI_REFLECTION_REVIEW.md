# AI reflection and human responsibility review

Updated: 25 October 2026 | Status: Current Section 9 incorporated; final student reading remains

The student requested a clearer account of their contribution, oversight and
responsibility. The earlier reflection devoted disproportionate space to AI
execution and limits on personal checks. This revision leads with the student's
purpose, scope, judgement and accountability while retaining clear disclosure
of substantial AI assistance. It follows the course notebook's human-oversight
framework and uses documented project examples.

## Cross-check with the course requirements

Sources actually read:

- Course file `MMA3001_Notes_Week01_4_Responsible_Use_of_AI.ipynb`
  (available through authorised course access; excluded from the public repository),
  all 14 cells, particularly cells 4-6 and 8/11/13. Cell numbers are one-based
  JSON positions. The notebook is nbformat 4.0 and has no numbered revision
  identified. SHA-256:
  `11f8aed9e9f1a6e5503a06a466424aaddf0eb78818eb50c1b796381a800daef6`.
- Course file `MMA3001_2026_Project_Brief.pdf`
  (available through authorised course access; excluded from the public repository), pages 6 and 15. The
  15-page brief matches the recorded version; SHA-256:
  `1029cf7c7c2844161af0c3727bbcbf40fac3913575683defe34ee942f9a9550c`.
- [AI-use log](../Project_Setup/AI_USE_LOG.md) and
  [student review notes](STUDENT_REVIEW_NOTES.md), initially read at records043 and revisited at records045.
  Cells4-6 and brief pages6/15 were reread for the latest revision.

The brief requires tools, tasks, approximate contribution, reasons, checks,
student decisions, errors/limitations and effects on understanding/workflow.
It does not prescribe an exact percentage. The notebook additionally asks for
known versions/access dates, iteration history, relevant bias/limitations,
actual human oversight and attention to privacy/ownership. Unknown versions or
Claude session details must remain unknown rather than be reconstructed by
guessing. Provider policies linked in the notebook were not freshly checked;
this is a review of the course material, not a claim about current legal terms.
The linked video was not viewed and no notebook cell was executed.

## From course guidance to the student's contribution

| Course guidance | Documented student role and example | How it appears in Section 9 |
| --- | --- | --- |
| Notebook cell4: keep human direction and explain why AI is used. | Chose the suspension question from personal interests; retained full-response max abs(zs-zu) and post-bump priorities. | Opens with purpose and scope, followed by reasons for AI support. |
| Notebook cell5: state human oversight and responsibility for final decisions and conclusions. | Adopted the specification, authorised bounded stages and requested brief checks; supplied engineering judgement. | Names these decisions and explicitly accepts accountability. |
| Notebook cells5-6: explain validation efforts and use evidence beyond fluent AI answers. | Worked through force/equilibrium, numerical-check and data-role reasoning; used Claude for physics questions. | Gives concrete review examples and distinguishes them from AI-run computational checks. |
| Brief p15: show the student driving the process and critically interpreting work. | Reconsidered the stiffness expectation after observing competing peak/settling outcomes; recognised the fixed-bump limit. | Explains what conclusions are justified and why a single smaller metric is insufficient. |
| Brief p6: explain tasks, contribution, decisions, errors and learning. | Supplied motivation and technical responses, selected MIT and performed recorded GitHub steps; corrected misconceptions through feedback. | Discloses substantial AI work while recognising student direction, learning and judgement. |

The division of work is qualitative: AI supported detailed design and performed
most implementation, automated checking, execution, analysis and initial writing.
The student's contribution includes directing the question, adopting the scope,
reviewing meaning, communicating personal judgement and accepting responsibility
for submission. Responsibility is broader than keyboard execution; it still
requires an accurate account of who did the technical work.

## Current report wording

I chose suspension modelling because of my interest in motorsport, sim racing and vehicle dynamics. My role was to define what the project should explain and take responsibility for the final interpretation. I retained max |zs − zu| over the whole response as the primary output and gave post-bump motion and settling particular importance. I adopted the proposed specification, authorised bounded stages and requested checks against the brief. These decisions set the purpose and scope against which I reviewed the work. [E9]

I used ChatGPT, including Codex for implementation and project files, and Claude to cross-check physics questions. AI connected taught methods to the problem and supported unfamiliar coding and GitHub tasks. Its contribution was substantial: detailed specification, most code and automated tests, computational execution, audits, analysis, documentation and initial report drafting. I supplied motivation, technical responses and engineering judgement, selected MIT and performed the recorded upload and clone steps. This qualitative account recognises both my direction and the technical work delegated to AI. [E9]

### Human oversight and engineering judgement

My oversight focused on whether the model and outputs answered the intended question. Through explanations and follow-up questions, I worked through relative spring and damper forces, static-equilibrium coordinates, motion after bump exit and the distinction between peak travel, peak-to-peak range and settling. I used Claude as an additional check during these physics discussions. Agreement between tools does not prove correctness; the explanations still need to agree with the governing equations and recorded evidence. [E9]

I reviewed why solver refinement, finer observations, a longer horizon and the remaining-energy bound address different uncertainties, and why validation and final testing have different roles. AI implemented and ran the computational checks, including source comparisons, physical consistency checks, an analytical diagnostic and saved-result audits. My contribution was to question their meaning and judge the limits of the conclusions: numerical consistency supports this simulation study, while real-vehicle behaviour remains unvalidated. [E1, E2, E8, E9]

The stiffness comparison refined my expectation that greater stiffness would generally reduce motion. A smaller post-bump peak accompanied a larger full-response peak and longer settling. I therefore judge a setup against stated priorities, rather than treating one smaller value as sufficient. My conclusion is limited to the model and tested conditions: the peak predictor does not replace trajectory analysis, and changing the bump requires separate justification and validation. These are limits I must preserve when communicating the results. [E3, E5, E9]

Review exposed mistakes as well as progress. Feedback corrected my initial assumptions about changing bump height and using single-oscillator energy for the quarter-car. AI-led checks separately found runtime thread-control and Git line-ending problems. Restating ideas helped expose gaps and refine my reasoning. AI accelerated the workflow, but coding details and reproducing the implementation independently remain learning needs. Recognising those limits helps me avoid treating fluent output as sufficient evidence. [E9]

I remain accountable for the final conclusions and decisions, and for the submitted code, results and references. That includes explaining how the evidence supports my judgement, acknowledging uncertainty, and considering privacy and ownership of uploaded material. The report began as an AI draft on 22 October and was revised through review on 25 October; exact historical model versions were not consistently recorded. AI supported the work, while responsibility for what I submit remains mine. Disclosure does not replace verification. [E9]

## Provenance and remaining uncertainties

- ChatGPT-main and Claude physics-cross-checking use are student-confirmed.
  Claude's reported scope covers all physics-related walkthrough questions;
  transcripts, exact versions and session dates have not been inspected.
  Codex review assistants are not attributed to Claude.
- The wording is AI-authored from student input and project records. It makes
  genuine direction and judgement explicit without claiming the student
  independently chose all numerical/ML settings, ran the automated test suite
  or audited every source. The walkthrough is an AI-assisted learning process.
- Specific corrections and the stiffness interpretation are recorded in
  [student review notes](STUDENT_REVIEW_NOTES.md). The student selected MIT and
  performed the recorded upload/clone actions. Code reproduction and detailed
  implementation remain learning needs, rather than completed mastery.
- The current revision does not assert unrecorded note-free mastery, universal
  fact/citation checking, independent outside-chat calculations, or provider
  policy compliance. Privacy and ownership are stated as responsibilities.
- The supplied identity is entered and all R1-R7 markers are resolved. The
  student should still read the final narrative for personal accuracy before
  submission. Unknown Claude session details do not require invented answers.
- The earlier longer reflection is preserved locally at
  `tmp/report_responsibility_20261025/reflection_review_before.md` as a dated
  precursor. The current report and this review supersede it.
