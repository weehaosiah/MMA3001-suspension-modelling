# Final local upload check

Prepared: 25 October 2026 | Status: local preparation; student commit/push pending

The current report includes identity and all R1-R7 review contributions. It has
nine main pages plus one reference page. The report and the12 October profiling
supplement are still local. Fresh authenticated GitHub reads on25 October show
private `main` at `8ba9808f10dcdc84330135870d8b7f92c189f0a8`, matching local HEAD.
The deadline remains the student-confirmed25 October2026 at23:59 Australia/Sydney.

## Files intended for the update

| Group | Include |
| --- | --- |
| Root | README, .gitignore and .gitattributes changes. Existing LICENSE remains MIT. |
| Project_Setup | Updated state/evidence/AI records, publication/upload/checklist guidance, historical progress and clone-check evidence, and this final upload record. |
| Report_Draft | The current DOCX, README, reflection/review notes, .gitignore and the initial drafting helpers. The helpers preserve initial drafting history; do not run build_report.py to regenerate the reviewed document. |
| output/pdf | The final PDF report requested by the current Moodle instructions, as confirmed by the student. |
| Suspension_Model | Profiling code, its focused tests, saved profiling results, related guides and generated HTML documentation. Existing simulation/data/ML results remain unchanged. |

Course originals, tmp, rendered report checks, caches and generated report figures
are excluded by ignore rules. The embedded figures are already inside the DOCX.
Root course PDF names containing spaces are now covered as well. A manual ZIP of
the original workspace does not apply these rules and is unsuitable.

## Actual checks and their limits

The final editable DOCX SHA-256 is
`8c9df0aa7924a8f5b50d6bd374f6e6913e214101412b78ee4cc65206d972c239`.
The [submission PDF](../output/pdf/MMA3001_suspension_report.pdf) SHA-256 is
`1e424555f3abf839893aff9f297b2bd841054946323cf1f54e44490e7541e8b5`.
Only the first-page subtitle's draft label/date changed during PDF preparation.
The revised first page passes visual review; pages2-10 match the previously
reviewed render pixel for pixel. Scientific conclusions and final-test status
are unchanged; the final test remains consumed. No new simulation, fitting,
prediction, benchmark or test-suite execution is part of this preparation.

Current package inventory and static checks are saved in
[upload_review_20261025](upload_review_20261025/CHECK_RESULTS.md). A static check
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
   including both ignore files. Course PDFs/notebooks, tmp and rendered pages
   should not appear as upload changes. If unexpected files appear, resolve
   those before committing.
3. Click **Fetch origin**. The verified remote matches the current local
   checkpoint; if Desktop shows unexpected remote changes, review them before
   proceeding rather than overwriting either version.
4. Enter the summary `Complete report review and add profiling evidence`.
   Click **Commit to main** to save the selected changes on this computer.
5. Click **Push origin** to upload that commit. Check that the report and new
   records appear on GitHub at the new commit. The assistant can then compare
   the local and remote revision and verify the report bytes.

These steps follow the official GitHub
[commit/push](https://docs.github.com/en/desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project-in-github-desktop)
and [sync](https://docs.github.com/en/desktop/working-with-your-remote-repository-on-github-or-github-enterprise/syncing-your-branch-in-github-desktop)
instructions, revisited25 October. No commit or push was performed by the assistant.

## After the verified push

- Use the PDF report and clone ZIP, as the student confirmed Moodle requires.
  Check any upload fields/size limits and assessor access. In GitHub, open this
  repository's **Settings > Collaborators** and look for the intended assessor.
  If absent, obtain the exact course-specified username/access procedure. An
  invitation only grants access after acceptance. No invitation or public-access
  change has been made here. See the official
  [collaborator instructions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository).
- Clone the final online revision into a new separate folder using Desktop's
  **File > Clone repository**. The earlier verification clone contains restored
  course originals and must not become the submission archive.
- Check files/history against the final online revision, then ZIP the clean
  clone. Retaining its hidden .git folder is our history-preservation recommendation;
  the brief explicitly requires a zipped clone but does not separately name .git.
- Submit the report and clone ZIP through Moodle, provide the repository link
  where requested and retain the submission confirmation.

See the official [cloning guide](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop)
and [submission checklist](SUBMISSION_CHECKLIST.md). Moodle format is now
student-confirmed; assessor access remains unconfirmed. A final clone/ZIP
depends on the final uploaded revision and has not
been created. No public-access change, invitation or submission has occurred.
