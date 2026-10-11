# Local repository readiness review

Revision: 002 | Scientific checks: 2026-10-05 | Status note updated: 2026-10-11

This document preserves the 5 October local review and its actual results. The
student subsequently uploaded the repository and a record update; local/remote
main were verified at db15329 on 11 October. Historical outstanding items below
are not all current. Use [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) for the
reconfirmed requirements and remaining work. No scientific check was rerun for
this status update.

The local review is complete. Saved scientific results pass their existing audits
in a relocated Windows copy after restoring the documented local course files.
The repository is not yet a complete submission: licence choice, student Git
identity, accessible GitHub hosting, the required final ZIP and assessed report
remain outstanding. This review does not claim a new experiment or full test run.

## What was corrected

- Updated the root README and dataset guide to reflect completed final evaluation
  and runtime work. The 100 final cases have been consumed.
- Added [REPRODUCING.md](../Suspension_Model/REPRODUCING.md) as the current starting
  point, separating saved-result audits from commands that regenerate results.
  Historical nominal and pilot runners overwrite canonical folders, so intentional
  repetitions belong in a separate disposable copy.
- Corrected current environment instructions to use `requirements-ml.txt`. All
  seven direct third-party imports are covered; the original simulation-only pins
  are preserved. No package was installed.
- Documented four excluded course originals required by final/runtime audits,
  plus two ODE notebooks needed for historical numerical workflows. These files
  are available locally but intentionally absent from version control.
- Fixed Git's byte preservation for five original nominal outputs. Their working
  files used CRLF line endings, while the previous Git snapshot stored LF endings.
  That changed a fingerprint used by later interpretation. Exact `.gitattributes`
  exceptions and restaging preserve original bytes; no numerical value, source
  algorithm, frozen fingerprint or working scientific output was rewritten.
- Added [build_docs.py](../Suspension_Model/build_docs.py) and a
  [documentation index](../Suspension_Model/docs/index.html). The generated HTML
  covers all current modules, including the previously undocumented nominal runner.
  Source links are relative; missing dependency documentation links are plain text.
  Runtime paths displayed in HTML are explicitly abbreviated. Historical JSON
  environment/provenance records retain their original recorded paths.

## Checks actually performed

| Check | Actual outcome |
|---|---|
| Original committed snapshot `478139c`, relocated using Git archive | Failed as preserved in [attempt 1](../Suspension_Model/repository_review_v1/checks.json) |
| Cause of original failure | Final/runtime audits lacked excluded course files; interpretation fingerprint differed because of Git line-ending conversion |
| Five nominal files compared with old Git bytes | All differences were exactly CRLF versus LF; numerical/text content otherwise identical |
| Corrected staged scientific snapshot, 126 files, folder containing spaces | [Attempt 2](../Suspension_Model/repository_review_v2/checks.json): all seven repository checks pass |
| Interpretation before course originals were restored | Passed all six saved-data checks and exact saved facts |
| Final and runtime audits after four originals were restored locally | Both passed, with no fitting, prediction or measurement |
| Snapshot integrity after audits | All 126 staged file hashes unchanged; no source originals staged |
| Existing installed dependencies | All seven direct versions match the pinned files |
| Generated documentation | 17 pages; 98 local links/anchors valid; all 78 public function anchors covered; no absolute local path/file URL in HTML |
| Documentation regeneration | Independent invocations produced identical content; source edits regenerate pages without scientific calculations |
| Final packaging checks | All 36 changed/staged files match working bytes; 87 protected scientific files match the corrected snapshot; no tracked course files; all reviewed Markdown links resolve; whitespace checks pass |

Both attempts and their exact command outputs/fingerprints are preserved. Attempt 2
checks the scientific snapshot with only the six byte-preservation repairs staged;
documentation changes made in this review are checked separately. The snapshot
contained no `.git` directory and the initial archive contained no course PDF or
notebook. It was an exported/copied snapshot, not a GitHub clone or a new environment.

These checks use the existing Windows/Anaconda interpreter. They do not establish
a clean installation, another operating system, an end-to-end rebuild, or a fresh
student reproduction. Some saved guards require the complete original Python
build string and use Windows path separators. A separate portable audit/rebuild
workflow has not been added. Original reserved-response files were copied/hashed
for preservation, not parsed or used for new predictions; the final audit reads
the already saved prediction table.

The previous **433 passing tests** remain implementation evidence from the runtime
checkpoint. No additional full test-suite execution, dataset generation, simulation,
model fit, tuning, final-test evaluation or timing experiment occurred in this review.

## Brief and source basis

Read PROJECT_GUIDE 003 and records 020 before work. The current state supersedes
the historical boundaries in HANDOFF 001 and the guide's old stage description.
No required source is missing from the workspace. The stale root README was a
conflicting summary and has been corrected using the newer authoritative records.

The course-audit assistant reread actual brief pages 8 and 10–13; its recorded
15-page file hash is unchanged. Page 8 requires a populated README, generated HTML,
licensing agreement, functional main branch, test functions/report, accessible GitHub
repository and a ZIP of a clone. The rubric rewards organisation, meaningful
history, understandable functions and documentation. An index and saved-result
entry point are project improvements, not additional assessment requirements.

Actual Week01_3 cells 10, 12, 14, 16, 27, 29–34, 39–42 were read for docstrings,
README and generated documentation. The notebook distinguishes built-in `pydoc`
from the optional `pdoc` package. This project retains built-in pydoc and adds
relative-link checks; it does not install pdoc or execute course examples/videos.
Exact source fingerprints and assistance are in [EVIDENCE.md](EVIDENCE.md) and
[AI_USE_LOG.md](AI_USE_LOG.md).

## Decisions and limitations recorded on 5 October 2026

1. Review the physical/code walkthrough and saved results with the student.
   Independent understanding and an honest approximate AI contribution remain
   unassessed; AI supplied most implementation and documentation.
2. Choose the project's licence and the student's Git author identity before
   publication. No licence, personal identity or public-access choice is invented.
3. Create the requested accessible GitHub repository and final ZIP of its clone
   in a later authorised publication/packaging stage. Keep course originals excluded
   and disclose that strict source audits require authorised local copies.
4. Complete the assessed report separately. Numerical verification and ML agreement
   with simulated labels do not establish real-car accuracy, physical clearances,
   continuous-domain guarantees or total preparation-cost benefits.

Submission remains **23 October 2026 at 23:59 Australia/Sydney**. Presentation-date
planning is deferred. Local Git checkpoints do not upload or synchronise the
project with GitHub or previously uploaded copies.
