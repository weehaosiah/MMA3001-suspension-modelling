# Real GitHub clone verification

Checked: 11 October 2026 | Result: all nine declared checks pass

The student created this copy using GitHub Desktop:
`tmp/github_clone_check_20261011`. The separately reported clone in a default
GitHub directory was not inspected, changed or deleted.

Verified original workspace, GitHub main and clone head:
`8ba9808f10dcdc84330135870d8b7f92c189f0a8`.
Tree: `d2e55b3f1f309f9d38cf5d7561c88a356cfa4869`.
All 138 tracked paths and all 12 commit identifiers agree between the original
and clone. Both working folders were clean before recording this review.

## Actual results

| Check | Result |
|---|---|
| Expected commit and remote | Pass; original/clone match the independently read GitHub head |
| Tracked paths and complete history | Pass; 138 paths and 12 commits agree |
| Initial working-file bytes | Pass with one explained exception: LICENSE is LF in the original and CRLF in the clone; the text is identical after line-ending normalisation. All other 137 files are byte-identical. No scientific difference. |
| Three saved-output audits | Pass; all return code 0, with transcripts linked below |
| Clone tracked files unchanged by audits | Pass; all 138 before/after SHA-256 values agree |
| Original tracked files unchanged by audits | Pass; all 138 original SHA-256 values agree before the subsequent record edits |
| Four restored course originals preserved | Pass; source and copy hashes match the documented expected values |
| Clone Git status | Clean after audits; locally restored course originals/caches are ignored |
| HTML links and required entry files | Pass; 17 HTML pages, 98 local links including 32 anchor links, zero broken targets/anchors or links escaping the clone. Seven expected README/reproduction/dependency/licence/index files are tracked and present. |

The complete check dictionary, before/after file fingerprints, exact commands,
clone path and source hashes are in [checks.json](checks.json).

## Commands and transcripts

From the clone's `Suspension_Model` directory, using the existing Windows/Anaconda
interpreter:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' -B interpretation_v1/review_saved.py
& 'C:\Users\dedvu\anaconda3\python.exe' -B final_evaluation.py audit
& 'C:\Users\dedvu\anaconda3\python.exe' -B runtime_benchmark.py audit
```

- [Interpretation](interpretation_audit.txt): all six checks and saved facts
  reproduce exactly. Ran before any course originals were added, using tracked
  files alone.
- [Final evaluation](final_saved_evaluation_audit.txt): fixed artifacts and saved
  metrics reproduce; no refit or new test read.
- [Runtime](runtime_saved_results_audit.txt): saved timings, work counts, ratios
  and fingerprints reproduce; no new timing or fitting. Matplotlib created an
  ignored font cache, without changing tracked files.

Before the last two commands, copied the exact authorised local brief and
Week02_1, Week05_5 and Week05_6 notebooks to the clone root, after checking their
SHA-256 values against [REPRODUCING.md](../../Suspension_Model/REPRODUCING.md).
No course notebook code was executed. The audit modes were independently inspected
before running: they hash/read saved artifacts and recompute summaries; they do
not simulate, fit, predict, load fitted models, perform new timing, run pytest or
read original held-out response contents. Checks of file preservation read bytes
for hashes only.

## Limits and next use

This establishes saved-artifact reproducibility in a real remote clone on the
existing Windows/Anaconda environment. It does not establish a clean installation,
another operating system, a complete end-to-end rebuild, fresh physical validation
or a new 433-test run. Static HTML checks do not establish browser rendering or
the quality of every explanation.

This verification copy now contains four ignored course originals. Keep it
separate from the final submission ZIP: create another clean clone of the final
uploaded revision for packaging, because ZIP tools also include ignored files.
Continue editing the original project folder. No remote mutation or extra-clone
cleanup occurred. Assessor access, profiling, report/AI reflection and final
submission remain separate work.
