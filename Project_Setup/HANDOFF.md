# MMA3001 new-chat handoff

Revision: 001 | Prepared: 2026-10-04, Australia/Sydney | Status: handoff prepared; project coding not yet authorised

This is a continuation note, not the assessed report. It does not itself authorise implementation or record acceptance of all proposed settings. The student requested next steps and a handoff after being advised to use a new chat for the baseline implementation stage. No new chat has been created by the assistant.

## Read first

Workspace: C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks

Read and follow Project_Setup/PROJECT_GUIDE.md revision 003. Read Project_Setup/PROJECT_STATE.md, EVIDENCE.md and AI_USE_LOG.md, expected revision 013. Read the workspace MMA3001_2026_Project_Brief.pdf and the relevant course notebook cells before adapting their methods. Identify the actual versions accessible and flag missing or conflicting files. If newer local records exist, inspect and reconcile them rather than forcing these expected versions.

The local records are authoritative working files. Uploaded copies and GitHub have not been synchronised by these edits. The brief has 15 pages; no printed revision/date was identified in the earlier full audit, and its filename identifies 2026. The brief and 30 notebooks were reviewed previously; notebook code was not executed. Written topic approval and the course schedule were not inspected, but the student's reported approval and deadline are recorded and must not be requested again.

## Confirmed direction and present status

- Student is a beginner with coding and GitHub: explain new concepts as they arise and connect code to the model.
- Suspension topic selected and approval reported. Submission: 23 October 2026 at 23:59, Australia/Sydney. Presentation-date planning remains deferred.
- Primary output: A = max over the entire checked response of abs(z_s-z_u), measured from each setup's static equilibrium, including motion after bump exit. Positive relative displacement means extension; negative means compression. Simulation units are metres; report travel and ML errors in millimetres.
- Post-bump behaviour has greater priority than peak-to-peak detail. Proposed supporting diagnostics are post-bump peak and sustained suspension-relative settling within +/-1 mm, timed from bump exit. They are not extra ML targets, measures of all vehicle motion, or safety/comfort standards.
- Complete starting specification has been reviewed for consistency. Concrete settings remain working proposals; no project implementation, simulation, dataset, fitted model or report has begun. Do not confuse source reading or illustrative arithmetic with experiments.

The complete physical/numerical/dataset/ML proposals are in PROJECT_STATE (P001-P003 and P005-P008); do not restart topic selection. In brief: passive linear quarter-car; m_s = 365.4 kg, m_u = 43 kg, k_t = 350,000 N/m; nominal k_s = 24,000 N/m and c_s = 2,126.4 N s/m. Raised-cosine road input h = 0.050 m, tau = 0.50 s; start at equilibrium. Proposed solver is adaptive RK45, initially 0-5 s checked against 0-10 s. Future study varies k_s and c_s by +/-25%, with 225 training/75 validation/100 test setups and linear regression versus RBF SVR. Those wider stages are not part of the first coding task.

Source provenance is in EVIDENCE: S002 equations; S003 bump shape/height (our crossing duration differs); S004 generic vehicle baseline; S006 settling convention; S007 solver; S008-S011 ML guidance. Parameter ranges, thresholds and sample counts are project choices. This is not Ferrari calibration or real-vehicle validation.

## Permission boundary

The original instruction was: "Do not begin coding or report writing yet." Preparing this handoff does not lift it. If the student's new message includes the optional approval sentence below, record adoption of the starting specification and permission for the nominal simulation and initial checks, then proceed without asking again. That acceptance makes the values starting decisions, not verified facts. It does not authorise report drafting or the full dataset/ML stage.

If the new message contains no such authorisation or equivalent direct instruction, ask one combined question about adopting the starting specification and beginning the nominal simulation/initial checks. Explain that the question comes from the student's earlier no-coding instruction. Do not request individual approval of every parameter or repeat topic/deadline questions.

## First implementation stage, once authorised

1. Inspect the existing Python environment, dependencies and Git status. Preserve course originals and existing user work. Establish an authored project area; check for an existing repository before creating one, avoiding an accidental nested repository. Explain local Git history versus online GitHub hosting. Do not claim a remote repository exists or publish one without a corresponding request.
2. Implement one nominal quarter-car case with clear functions, units and comments. Use the four-state order and equations in P006. Carry the full state through bump exit; do not reset the motion when the road becomes flat.
3. Produce readable plots of road height and suspension-relative displacement, marking bump exit, equilibrium and the proposed +/-1 mm band. Calculate A, A_post and a resolved/unresolved settling status with a time only when justified.
4. Complete initial checks: zero-road equilibrium; finite states and solver success; force/sign/unit review; tyre-contact consistency; post-bump energy behaviour; nominal solver/output-grid refinement and extended observation. Use P006's proposed agreement criteria and explicitly report failures or unresolved tails. Defer the remaining nine-pilot programme, full RK4 comparison and wider data generation to the subsequent verification stage.
5. Save a reproducible checkpoint: authored files, environment/dependency versions, instructions to run, relevant outputs and check results. Update state, evidence and AI-use records. Explain what was implemented, what actually passed, what remains unverified, and the next step. Do not invent a result or an overall AI-contribution percentage.

Done for this stage means a reproducible nominal simulation with understandable outputs and recorded initial-check outcomes. It does not mean the entire parameter domain, dataset budget or ML method has been validated. If checks fail, investigate and report the limitation rather than proceeding to 400 simulations.

## Copyable opening message

Continue my MMA3001 suspension-modelling project in this workspace. First read Project_Setup/HANDOFF.md revision 001, follow PROJECT_GUIDE.md revision 003, and read PROJECT_STATE.md, EVIDENCE.md and AI_USE_LOG.md (expected revision 013), plus the project brief. Identify accessible versions and flag missing files or conflicts; use newer authoritative records if present.

Preserve the confirmed primary output max abs(z_s-z_u), measured from static equilibrium over the full bump and post-bump response. Keep post-bump analysis ahead of peak-to-peak detail. I am a beginner with coding and GitHub; explain unfamiliar concepts clearly. My deadline is 23 October 2026 at 23:59 Sydney time; leave presentation-date planning aside.

The specification review is complete, but no implementation or experiment has begun. Continue from the recorded proposals without reopening topic selection. The next stage is one nominal simulation and its initial checks, as described in HANDOFF.md. Respect the recorded coding boundary unless I explicitly authorise that stage in this message. Keep sources, decisions and material AI assistance up to date, and do not start report writing or the full dataset/ML stage.

Optional sentence for the student to append only when ready to authorise coding:

I adopt the consolidated specification as the starting plan and authorise coding the nominal simulation and its initial checks. Proceed with that stage without asking for the same approval again.
