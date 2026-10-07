# GitHub setup decisions

Revision: 002 | Updated: 2026-10-07 | Status: student-led upload guide prepared; choices pending

The student authorised continuing after the repository review, then requested an
explanation of licence alternatives before choosing. No licence has been selected
or added. Project display name, preferred commit email and visibility remain open.
The connected account is known; its verified/primary school-email status still
needs checking in account settings.

The student now wants to understand Git and upload independently. Follow
[GITHUB_SELF_UPLOAD_GUIDE.md](GITHUB_SELF_UPLOAD_GUIDE.md) using the required
school-linked account. No automatic upload or identity change is implied by this
teaching task. The connected profile reports a Monash student email but does not
expose verified/primary flags.

## Prepared repository details

| Setting | Proposed value / current status |
|---|---|
| Repository name | `mma3001-suspension-modelling` — proposed |
| Description | MMA3001 quarter-car suspension simulation, numerical verification and machine-learning comparison for full-response peak suspension travel. |
| Owner/account | Authenticated GitHub account confirmed as `weehaosiah`; proposed owner |
| Visibility | Awaiting choice: private initially with assessor access, or public |
| Licence | Awaiting choice after the comparison below |
| Git name / email | Awaiting the student's chosen name and exact account-associated email; GitHub noreply is available |
| Existing local checkpoint | `82bda94`, clean at the start of this setup stage |
| Connection | GitHub plugin was initially absent, then installed during this turn; authenticated profile read confirms the connection. GitHub CLI not found on PATH. No remote configured. |

At the starting checkpoint there are 134 tracked files totalling 10,443,724 bytes
and eight local commits. No course PDF/notebook or licence file is tracked.
This inventory predates this setup note and its record updates. It is not a
publication or a new scientific verification result.

Publishing the existing repository would include authored source, data/results,
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

Once the choices and account access are available, add the chosen licence/identity,
create the agreed repository, upload the reviewed local history, verify access and
clone it for the submission ZIP. Those actions have not occurred. The final ZIP
must not be described as a clone of GitHub until a real remote clone exists.
No report drafting, new fitting or experiments are part of this setup stage.
