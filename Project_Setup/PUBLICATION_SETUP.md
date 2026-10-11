# GitHub setup decisions

Revision: 003 | Updated: 2026-10-11 | Status: student upload verified; licence and final access checks pending

The student authorised continuing after the repository review, then requested an
explanation of licence alternatives before choosing. No licence has been selected
or added. The student has now published the project privately and reported saving
their local author settings. The exact chosen author details were not independently
inspected. Verified/primary school-email status still needs checking in account
settings.

The student now wants to understand Git and upload independently. Follow
[GITHUB_SELF_UPLOAD_GUIDE.md](GITHUB_SELF_UPLOAD_GUIDE.md) using the required
school-linked account. No automatic upload or identity change is implied by this
teaching task. The connected profile reports a Monash student email but does not
expose verified/primary flags.

## Current repository details

| Setting | Verified value / current status |
|---|---|
| Repository name | `MMA3001-suspension-modelling` |
| Repository URL | https://github.com/weehaosiah/MMA3001-suspension-modelling |
| Description | Suggested during guidance: MMA3001 quarter-car suspension modelling and machine-learning comparison. Actual remote description not independently checked. |
| Owner/account | `weehaosiah`, confirmed by remote metadata |
| Visibility | Private, confirmed; assessor access still needs verification |
| Licence | Awaiting choice after the comparison below |
| Git name / email | Student reports local settings saved; exact values not inspected or recorded |
| Verified uploaded checkpoint | `73b1a02fd8f5bc2006a1ab481cf2a1cd348772f4`, default branch `main` |
| Connection | Authenticated remote reads succeed; local origin points to the repository URL with `.git` suffix |

On 11 October 2026, all 136 tracked file entries (path, blob identifier and mode)
and all 10 commit identifiers matched between local Git and GitHub. Local status
was clean before this record update. Course originals remain excluded. The student
performed the upload; the assistant made read-only remote checks. These new record
edits are local and require the student's next commit and push. See EVIDENCE M021.

At the historical starting checkpoint 82bda94 there were 134 tracked files totalling 10,443,724 bytes
and eight local commits. No course PDF/notebook or licence file is tracked.
This inventory predates this setup note and its record updates. It is not a
publication or a new scientific verification result.

The uploaded repository includes authored source, data/results,
documentation, project/AI-use records and Git history. Some preserved environment
records contain the original local Windows paths. Course originals and temporary
working copies stay excluded. Licence scope must not imply ownership or relicensing
of external references, course materials or dependency packages.

## Licence choices in plain language

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

For this small teaching project, MIT is the assistant's recommendation if the
student wants broad, simple reuse. GPLv3 suits a preference that distributed
derivatives retain source-sharing obligations. That recommendation is not a student
decision or a determination that every external source is available for relicensing.
No licence file is added while the choice remains open.

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

Next, select and add the project licence, verify school-account and assessor access,
and later clone the final uploaded revision for the submission ZIP. Initial upload
is complete; licence selection, access verification and final packaging remain. The final ZIP
must not be described as a clone of GitHub until a real remote clone exists.
No report drafting, new fitting or experiments are part of this setup stage.
