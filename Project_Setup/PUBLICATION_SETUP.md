# GitHub setup decisions

Revision: 007 | Updated: 2026-10-25 | Status: Remote checkpoint reverified; final local work awaits student upload

Fresh authenticated reads on25 October confirm private repository and main at
8ba9808f10dcdc84330135870d8b7f92c189f0a8, matching local HEAD. The completed report,
later profiling supplement and updated records remain local changes awaiting
student commit/push. No remote setting, access, identity or licence was changed.
The supplied full name was entered in the report; the existing licence notice
retains the previously accepted Git identifier. Use
[FINAL_UPLOAD_CHECK.md](FINAL_UPLOAD_CHECK.md) for the current upload handoff.

The student selected MIT on 11 October 2026 and confirmed that their school email
is verified. Added the standard root LICENSE locally, using the existing
repository-local Git author name `weehaosiah` in its 2026 copyright notice. The
student was unsure which name to use; the assistant used that configured public
identifier and explained the choice, without inventing a legal name. The email
verification is student-confirmed; no verification flag was independently read.
The student uploaded the licence and prior documentation as 8ba9808; that commit
is verified on GitHub. The subsequent clone-check records are new local edits.

The student now wants to understand Git and upload independently. Follow
[GITHUB_SELF_UPLOAD_GUIDE.md](GITHUB_SELF_UPLOAD_GUIDE.md) using the required
school-linked account. No automatic upload or identity change is implied by this
teaching task. The connected profile reports a Monash student email but does not
expose verified/primary flags. Primary-address status remains uninspected and is
not an extra requirement established by the project brief.

## Current repository details

| Setting | Verified value / current status |
|---|---|
| Repository name | `MMA3001-suspension-modelling` |
| Repository URL | https://github.com/weehaosiah/MMA3001-suspension-modelling |
| Description | Suggested during guidance: MMA3001 quarter-car suspension modelling and machine-learning comparison. Actual remote description not independently checked. |
| Owner/account | `weehaosiah`, confirmed by remote metadata |
| Visibility | Private, confirmed; assessor access still needs verification |
| Licence | MIT selected and uploaded; root LICENSE present in the verified clone |
| Git name / email | Local author name read as `weehaosiah`; exact commit email not read or recorded. Student confirms school email verified. |
| Verified uploaded checkpoint | `8ba9808f10dcdc84330135870d8b7f92c189f0a8`, default branch `main` |
| Connection | Authenticated remote reads succeed; local origin points to the repository URL with `.git` suffix |

At the first-upload check on 11 October 2026, all 136 tracked file entries (path, blob identifier and mode)
and all 10 commit identifiers matched between local Git and GitHub. Local status
was clean before this record update. Course originals remain excluded. The student
performed the upload; the assistant made read-only remote checks. These new record
edits were then committed and pushed by the student as db15329, verified against
GitHub. The full brief has now been reread; see [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md).
This later audit's documentation edits are local and not yet committed or pushed.
See EVIDENCE M021-M022.

At the historical starting checkpoint 82bda94 there were 134 tracked files totalling 10,443,724 bytes
and eight local commits. No course PDF/notebook or licence file is tracked.
This inventory predates this setup note and its record updates. It is not a
publication or a new scientific verification result.

The uploaded repository includes authored source, data/results,
documentation, project/AI-use records and Git history. Some preserved environment
records contain the original local Windows paths. Course originals and temporary
working copies stay excluded. Licence scope must not imply ownership or relicensing
of external references, course materials or dependency packages.

## Licence choices explained before selection

A licence sets reuse conditions. Visibility controls who can access the repository.
They are separate choices. The brief p8 asks for a licensing agreement and an
accessible repository link; it names no specific licence and does not explicitly
demand a public repository. Assessor access would need checking if private.

| Choice | Practical meaning |
|---|---|
| [MIT](https://choosealicense.com/licenses/mit/) | Others may reuse, modify and sell the software while retaining copyright/licence notices. They may distribute modified versions without disclosing their source. Short and straightforward. |
| [BSD 3-Clause](https://choosealicense.com/licenses/bsd-3-clause/) | Broad reuse similar to MIT, with an explicit restriction on using contributors' names to endorse derived products without permission. |
| [Apache 2.0](https://choosealicense.com/licenses/apache-2.0/) | Broad reuse with an express contributor patent grant, preservation of applicable notices and marking of modified files. More detailed terms. |
| [GPLv3](https://choosealicense.com/licenses/gpl-3.0/) | Distributed modified versions must meet GPL requirements, including corresponding source and the same licence for covered works. Private modifications need not be published. Commercial distribution is still allowed. |

The assistant recommended MIT for broad, simple reuse, and the student has now
selected it. The root LICENSE covers the project's original software and associated
authored documentation. It does not determine ownership or relicense course
originals, cited external material or dependency packages. Their own terms remain.

## Identity and access

A Git author name is the label on a saved commit; it is not necessarily the GitHub
login. A GitHub-provided noreply email can associate commits with the account while
avoiding a personal email in commit metadata. Use the exact account-provided value,
not a guessed address. Any configuration will be repository-local; historical
AI-attributed commits retain their attribution. Sources:
[Git author name](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git),
[commit email](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address).

Public means anyone on the internet can view the repository. Private limits access
to authorised people; access must be arranged for assessors. Source:
[GitHub repository visibility](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories).

Next, verify assessor access and later clone the final uploaded revision for the
submission ZIP. Initial upload, MIT publication and same-environment saved-result
checks in a real Desktop clone are complete. See [clone results](clone_review_v1/CHECK_RESULTS.md).
Earlier command-line clone attempts failed, but the student's Desktop clone
succeeded. The student also reported a second local clone; it was left untouched.
The verification copy contains four restored, ignored course originals, so final
packaging needs a new clean clone. The final ZIP
must not be described as a clone of GitHub until a real remote clone exists.
No report drafting, new fitting or experiments are part of this setup stage.
