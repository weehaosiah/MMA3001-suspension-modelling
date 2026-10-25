# Profiler checkpoint reproduction review

12 October 2026. This review does not rerun the seven integrations.

An independent static review found that the three sealed pair_*_pstats.txt
exports contain CRLF endings, while the general Git text rule would convert
them to LF. That would invalidate their summary.json fingerprints after upload.
Added exact .gitattributes exceptions preserving those three files and explicitly
marked .prof files binary. The sealed runner, raw files and hashes were unchanged.

Read-only Git hash-object comparisons, with and without clean filtering, confirm
that the runner and all 13 sealed artifacts retain identical stored bytes.
No Git object was written; no staging, commit, push or remote clone occurred.
Actual output: [git_bytes_check.txt](git_bytes_check.txt).

Copied the 172 Git-visible working files returned by git ls-files -co
--exclude-standard at that point, byte-for-byte, into the initially absent
tmp/profiling_relocation_check_20261012 folder. This working snapshot includes
then-current uncommitted files; it has no Git metadata and no excluded course
originals. It is not a GitHub clone or a clean dependency installation.

From that copy's Suspension_Model directory, ran:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' -B profile_nominal.py audit --output profiling_v1
```

Actual result: exit0, Audit passed, with all 31 absent course originals explicitly
reported. All 172 original/copy files stayed byte-identical through the audit.
No solve, model load/fit/prediction, timing experiment or scientific test suite
ran. Later documentation edits lie outside this preservation interval.
Actual output: [relocation_audit.txt](relocation_audit.txt).

This confirms saved profiler evidence can be checked after local relocation on
the existing Windows/Anaconda environment without course originals. Earlier
final/runtime audits still require their four exact authorised course sources.
Newcomer instructions now put the saved audit first, explain replacing laptop
paths, and distinguish fresh runs and derived-output rendering.

Remaining: upload the reviewed local stage, verify a fresh remote clone of the
eventual submitted revision, and confirm actual assessor access/dependencies.
Other operating systems, clean installation and full scientific rebuilding remain
unverified. No new private-repository access or current Moodle instruction was
independently checked here.
