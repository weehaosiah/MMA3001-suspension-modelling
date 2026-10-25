# Final upload preparation checks

Checked: 25 October 2026 | Scope: local files and read-only GitHub checks

This is a working-file review before the student's final commit/push. It is not
a final remote clone, clean dependency installation or new scientific execution.
The exact candidate inventory and SHA-256 fingerprints are in
[inventory.json](inventory.json). That inventory excludes this metadata directory
to avoid circular self-hashes; include this directory in the documentation upload.

| Check | Actual result |
| --- | --- |
| Local and freshly read remote main | Both8ba9808f10dcdc84330135870d8b7f92c189f0a8; later work still uncommitted locally |
| Repository visibility | Private; assessor access remains unconfirmed |
| Report | Only subtitle draft/date changed; final DOCX SHA-2568c9df0aa7924a8f5b50d6bd374f6e6913e214101412b78ee4cc65206d972c239; nine main pages plus references |
| Required PDF | SHA-2561e424555f3abf839893aff9f297b2bd841054946323cf1f54e44490e7541e8b5; revised page1 visually checked, pages2-10 pixel-identical to the preceding reviewed pages |
| Scientific preservation |426 SHA-256 comparisons across140 unique files: zero mismatches;109 authored files and31 recorded course originals |
| Profiling evidence | All120 protected files,13 sealed artifacts and frozen runner included in those comparisons |
| Git byte preservation | Read-only Git clean-filter hashes equal raw file hashes for all109 checked authored files; no Git objects written |
| HTML documentation |19 pages;108 local link/anchor checks; zero missing targets/anchors or absolute-path/file-URI leaks |

The source scan confirms course originals and temporary report renders are absent
from the candidate package. The root ignore correction covers the four additional
course PDFs whose names contain spaces. Core Markdown links, whitespace and
current report identity are checked in the recorded inventory. Current-facing
README/checklist/upload statements now reflect completed R1-R7 inputs and the
student-confirmed25 October deadline; dated history remains preserved.

The scientific hash/HTML checks were performed by an independent AI assistant
using file reads and read-only Git filtering. No scientific module, solver,
model, profiler or audit entry point was imported or executed. Held-out response
files were hashed as opaque bytes. The historical failed runtime checkpoint was
compared with its preserved runner, rather than the later corrected runner.

Recheck the new commit after the student pushes. Then verify the final clean
clone/archive and actual assessor access. The student confirmed Moodle requires
a PDF report and clone ZIP; the PDF is prepared. Exact upload fields/limits and
submission status remain unconfirmed. The original brief p8 requires a written
report, accessible repository link and zipped clone, without naming PDF versus DOCX.
No commit/push, visibility change, invitation or submission occurred here.
