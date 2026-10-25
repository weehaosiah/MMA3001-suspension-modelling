# Final upload and replacement package check

Updated: 25 October 2026 | Scope: status corrections following verified public1385cf6

The report and profiling supplement were published in1385cf6 on25 October.
That public revision and its clean clone ZIP were verified. The student then
requested a content walkthrough and authorised correction of outdated status
wording. This correction changes documentation and report publication notes;
scientific code, data, fitted models and results are preserved. It requires an
updated PDF and a matching replacement clone ZIP after the new commit/push.
The deadline remains25 October2026 at23:59 Australia/Sydney.

## Files in the documentation correction

| Group | Include |
| --- | --- |
| Root | README clarifies public publication and the final-test history. |
| Project_Setup | Current status/evidence/AI/checklist/publication/upload notes and this correction's check record. Earlier dated histories stay intact. |
| Report_Draft | DOCX publication-status paragraphs and evidence references, plus README. Section9's student/AI contribution narrative is preserved. Do not rerun the initial report builder. |
| output/pdf | Refreshed PDF from the corrected editable report. |
| Suspension_Model | README and DATASET.md add the dated test-status explanation. The fingerprinted README inside heldout_test remains unchanged. |

Course originals, tmp, rendered report checks, caches and generated report figures
are excluded by ignore rules. The embedded figures are already inside the DOCX.
Root course PDF names containing spaces are now covered as well. A manual ZIP of
the original workspace does not apply these rules and is unsuitable.

## Actual checks and their limits

The [submission PDF](../output/pdf/MMA3001_suspension_report.pdf) and editable
DOCX receive new fingerprints after the publication-status correction. Actual
rendering, preservation and link-check results are recorded in
[the status-correction check](status_review_20261025/CHECK_RESULTS.md).
Scientific conclusions and final-test status are unchanged; the final test
remains consumed. No new simulation, fitting, prediction, benchmark or test-suite
execution is part of this correction.

The earlier pre-publication inventory and static checks are preserved in
[upload_review_20261025](upload_review_20261025/CHECK_RESULTS.md). They describe
that earlier file set and are not rewritten as if it included this correction.
A static check
reads files and verifies consistency; it does not demonstrate a fresh installation
or rerun the scientific experiments. The earlier clone audits used the existing
Windows/Anaconda environment. Strict final/runtime audits require separately
obtained course sources as explained in
[REPRODUCING.md](../Suspension_Model/REPRODUCING.md).

## Your next steps in GitHub Desktop

1. Open the original working repository. Use **Repository > Show in Explorer**
   to confirm it is `C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks`.
   The duplicate clones are not the editing folder.
2. Read the final report and inspect **Changes**. Include the groups above,
   while retaining the existing ignore rules. Course PDFs/notebooks, tmp and rendered pages
   should not appear as upload changes. If unexpected files appear, resolve
   those before committing.
3. Click **Fetch origin**. The verified remote matches the current local
   checkpoint; if Desktop shows unexpected remote changes, review them before
   proceeding rather than overwriting either version.
4. Enter the summary `Clarify final-test and publication status`.
   Click **Commit to main** to save the selected changes on this computer.
5. Click **Push origin** to upload that commit. Check that the report and new
   records appear on GitHub at the new commit. The assistant can then compare
   the local and remote revision and verify the report bytes.

These steps follow the official GitHub
[commit/push](https://docs.github.com/en/desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project-in-github-desktop)
and [sync](https://docs.github.com/en/desktop/working-with-your-remote-repository-on-github-or-github-enterprise/syncing-your-branch-in-github-desktop)
instructions, revisited25 October. No commit or push was performed by the assistant.

## After the verified push

- Use the reviewed PDF and clone ZIP, as the student confirmed Moodle requires.
  Public readability was verified for1385cf6 by a successful anonymous clone;
  the assistant made no visibility change or invitation. Verify the new revision
  and follow Moodle's actual fields/size limits.
- Clone the final online revision into a new separate folder using Desktop's
  **File > Clone repository**. The earlier verification clone contains restored
  course originals and must not become the submission archive.
- Check files/history against the final online revision, then ZIP the clean
  clone. Retaining its hidden .git folder is our history-preservation recommendation;
  the brief explicitly requires a zipped clone but does not separately name .git.
- Submit the report and clone ZIP through Moodle, provide the repository link
  where requested and retain the submission confirmation.

See the official [cloning guide](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop)
and [submission checklist](SUBMISSION_CHECKLIST.md). The earlier1385cf6 archive
remains an exact historical copy of that revision. It does not include these
later corrections. Prepare and check a replacement archive after the corrected
commit is uploaded; do not mix its older PDF with the refreshed report. Moodle
submission remains unconfirmed.
