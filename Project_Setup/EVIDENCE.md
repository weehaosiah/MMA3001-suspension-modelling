# MMA3001 evidence register

Revision: 016 | Updated: 2026-10-05 | Status: 400-setup dataset and generation-check evidence recorded

## First simulation dataset, 2026-10-05

U012 / D006 - The student's "proceed" followed the completed nine-pilot stage and proposed dataset generation. Implemented that stage only. No preprocessing fit, ML training, final-test prediction evaluation, assessed report writing or GitHub publication occurred. D002's full-response primary target and post-bump priority remain unchanged. D007 records exact sampling/traversal details that implement adopted P007; they are project choices, not assessment requirements or demonstrated optimal settings.

R005 - Read guide 003, handoff 001 and current records 015. The accessible records are newer than the handoff's expected 013 and explicitly document completed nominal/pilot work; their chronology supersedes its historical no-coding status. No new missing required source or material record conflict was found. Before adaptation, reread actual Week05_6 cells 4, 13-15, 19 and 28-30 (one-row prediction contract, duplicate identity, suitable splits and training-only preprocessing) and Week05_5 cells 6, 9, 16-17, with independent review of 36-37 and main-assistant reread of those final-test cells. Cell numbers are one-based JSON positions. Notebook code was not executed or altered. The original 15-page brief and numerical-source bytes match the prior reading; a fresh complete brief reread is not claimed. No new external source or dependency installation was needed.

M007 - Actual dataset generation. `Suspension_Model/generate_dataset.py` completed one full generation into `dataset_v1/`, using `dataset_design.py` for sampling/identity and validity. The plan and 400-row setup manifest were saved before numerical output generation and verified unchanged afterward. A 15 by 15 endpoint-inclusive grid gives 225 training pairs; separate PCG64 generators with seeds 3001 and 3002 provide 75 validation and 100 test pairs. Each generator makes one (count,2) uniform draw with columns [ks,cs]. All 400 IDs and coefficient pairs are unique, finite and within the adopted domain. No noise, redraw, drop or role reassignment occurred.

Exactly nine baseline pilot summaries were reused within training at D005 settings: RK45 rtol=1e-6, component atol=[1e-9,1e-8,1e-9,1e-8], max_step=0.005 s, 5 s horizon and 1 ms observations. The reuse guard checks physical parameters, initial state, road, settings, numerical environment, model-source bytes and successful pilot verification. The tight 10 s reference was not substituted. Completed 391 new dataset integrations; the test suite's verification solves are additional check work, not dataset rows.

| Role | Unique rows | Eligible primary targets | Reused pilot labels | Unresolved settling |
|---|---:|---:|---:|---:|
| Training | 225 | 225 | 9 | 0 |
| Validation | 75 | 75 | 0 | 0 |
| Reserved final test | 100 | 100 | 0 | 0 |

All rows pass complete finite solve, full exit-state continuity, peak consistency, sampled tyre contact, post-bump energy and tail screening. Minimum sampled tyre force across all rows is 2398.808925801 N, above the fixed 1 N guard. Largest 5 s remaining-motion bound is 0.011530650542 mm, below each row's min(0.5 mm, A/2, A_post/2) criterion. Maximum positive sampled energy increment is 0 J. These are permitted predeclared validity aggregates, not an inspection of final-test target distributions. No failure reasons were recorded. Settling is labelled `resolved_under_adopted_settings`; full independent refinement was performed on nine pilots, not repeated at every new pair. Numerical and contact validity remain separate; unresolved settling alone would not erase an independently valid primary target.

New label integrations used 2,423,152 derivative evaluations and 78.963228600 s summed integration time. The row-generation loop took 86.702437200 s, excluding its preceding tests and subsequent audit/plot. Historical reused-pilot integration time 1.809784600 s is recorded separately. These are one-run measurements on the existing laptop environment, not a speed benchmark. Original nominal/pilot artifacts and physical-model module are unchanged.

M008 - Generation checks and preservation. Combined suite: 280 tests pass (178 prior tests plus 77 design/cache/classification tests and 25 generator/export/failure tests); saved generation-run output reports 4.16 s. New tests use mutated prior summaries or synthetic records, not new physical experiments. They check frozen sampling, duplicate/identity/domain rejection, missing/nonfinite diagnostics, separate primary/contact/settling decisions, stale/incorrect caches, exception retention and unknown failed-solver cost, corrupted exports, manifest changes and refusal to overwrite existing outputs. Initial new design tests exposed eight guard failures; corrections were made before full generation. Focused and complete reruns then passed.

The export audit rechecks all CSV/JSON setup identities, physical parameters, round-trip inputs, validity from raw checks and A_mm=1000*A_m. Final independent assistant audit found zero mismatches across 18 source hashes, 12 output hashes and two pre-generation manifest hashes; hashes were read mechanically without exposing reserved test responses. Source files and manifests remained unchanged during the run. CSV/JSONL line endings are explicitly stable for Git. The three-panel plot shows only stiffness/damping input locations; it was visually inspected. Outputs include raw SI and post-bump/settling summaries, configuration, environment, work and provenance. Full traces for each of the 400 rows are not saved; nominal/pilot traces remain available.

Reproduction instructions are in `Suspension_Model/DATASET.md`. Existing output folders are never overwritten; a fresh run uses `--output dataset_recheck`. No second full dataset run or fresh-environment installation was performed. Exact Python version/build and numerical versions protect cached pilot reuse; a changed environment requires reviewed verification/artifact refresh. Local Git records an AI-authored checkpoint; no student/global identity or remote was changed.

Limits: the 400 sampled cases passing does not prove exact continuous-time label accuracy, continuous contact throughout the whole parameter rectangle, real-vehicle validity, physical travel clearance, adequate sample size or any ML performance. Final-test responses remain segregated and were not explored for model selection, target distributions or response plots. Only predefined identity/unit/physical/numerical checks were applied. State/evidence/AI log are saved at revision 016; student understanding and overall AI contribution remain to be reviewed.

## Bounded simulator verification, 2026-10-05

U011 / D004 - The student said "ok proceed" after the proposed nominal walkthrough and bounded verification programme. Implemented those activities while preserving D002's full-response maximum and post-bump priority. No full parameter dataset, ML training, report prose or GitHub publication was begun. D005 records the resulting numerical settings decision; it is a choice supported by the nine pilots, not a physical standard.

R004 - Read guide 003 and current state/evidence/AI log 014; Git was clean at `4228532`. Reread actual Week07_4 cells 12, 17, 21-23, 32-33 (classical RK4, convergence and cost) and Week07_5 cells 19-21 (known underdamped oscillator and limits of verification). Cell numbering remains one-based JSON position. The brief and course-source hashes are recorded with outputs and agree with earlier copies; the full brief was not reread this session. Course originals were neither edited nor executed. No new external technical source or package was needed.

M003 - Nine-pilot programme. `run_verification.py` runs each of nine low/nominal/high stiffness/damping pairs with baseline RK45 to 5 s, tight RK45 to 5 s, tight RK45 to 10 s, and classical RK4 to 5 s at 0.5/0.25 ms. This is 45 full quarter-car integrations per programme execution; grid/band summaries reuse those trajectories. The programme was regenerated after display/failure-test additions, not used to create extra sample rows. The nominal centre's A, A_post and 1 mm settling exactly matched the original checkpoint. All nine pass; no horizon extension to 20 s was required.

| ks [N/m] | cs [N s/m] | A [mm] | A_post [mm] | +/-1 mm settling after exit [s] | Reference minimum contact [N] |
|---|---:|---:|---:|---:|---:|
| 18000 | 1594.8 | 44.093828 | 39.623735 | 1.873319 | 2922.138 |
| 18000 | 2126.4 | 39.343321 | 33.663538 | 1.376666 | 2831.415 |
| 18000 | 2658.0 | 35.442747 | 28.785418 | 1.004290 | 2744.095 |
| 24000 | 1594.8 | 45.491905 | 37.808798 | 1.987777 | 2670.127 |
| 24000 | 2126.4 | 40.571155 | 31.891620 | 1.269332 | 2626.596 |
| 24000 | 2658.0 | 36.522937 | 27.115903 | 0.889807 | 2574.116 |
| 30000 | 1594.8 | 45.685298 | 34.092912 | 1.841485 | 2418.829 |
| 30000 | 2126.4 | 40.848131 | 28.673449 | 1.445349 | 2417.877 |
| 30000 | 2658.0 | 36.841515 | 24.324843 | 1.095702 | 2398.783 |

Table uses tight RK45 / 10 s / 0.25 ms reference summaries. Both peaks include their relevant interval boundaries. Exact values and timings remain in `Suspension_Model/verification_results/summary.json`.

Maximum direct base 5 s / 1 ms versus reference 10 s / 0.25 ms differences: A 0.000464923531 mm, A_post 7.47171516e-7 mm, settling 8.86295923e-6 s across all three bands. Same-grid RK45 tolerance refinement: A 5.75289982e-7 mm and A_post 7.47171516e-7 mm. Same-grid RK4 versus RK45: A 2.24514157e-8 mm and A_post 1.57725152e-8 mm. All satisfy the 0.05 mm / 0.01 s comparison criteria. Horizon extension changed no sampled peaks/settling. Equal outputs do not prove zero continuous-time error.

RK4 adaptation keeps the taught four stages/1:2:2:1 weights, extends scalar state to a four-vector, lands at bump exit and carries the full state onward. It calls the existing physical RHS and evaluates road forcing at each intermediate time. Native samples only are used; finer interpolation of RK4 output is rejected. RK4 step-halving also refines observation spacing, so its peak difference is not a pure integration-error estimate. A separate focused known-solution test checks RK4 convergence; no convergence order is inferred from the pilot peak table.

Every compared trajectory passes finite/complete solve, all-state exit continuity, sampled energy allowance, tail margin and sampled contact consistency. Minimum reference contact across pilots is 2398.782752 N; largest tight 5 s tail bound is 0.01080601534 mm. No positive sampled post-bump energy increment was observed. The contact numerical ambiguity rule and energy allowance remain those documented in M002. The runner independently retains numerical peak and physical-contact flags; failed contact cannot be repaired by waiting longer. A failed narrow-band result does not silently invalidate an independently resolved primary peak, but blocks the all-band verification claim.

M004 - Analytical reduced-case diagnostic. The wheel is deliberately clamped at zu = vu = 0, and the existing body RHS is integrated from x0 = 0.010 m, v0 = 0.020 m/s over 0–5 s. The known unforced underdamped solution from C001 cells 19–21 independently supplies both state references on a 1 ms grid. RK45 settings: rtol = 1e-9, atol = [1e-11 m, 1e-10 m/s], max_step = 0.005 s. Predeclared diagnostic criteria: position discrepancy <=1e-7 m and velocity <=1e-6 m/s. Measured maxima 3.80070975e-13 m and 3.05053552e-12 m/s both pass; 6008 derivative evaluations. The clamp checks the body force/integration only, does not check the tyre equation or exact full quarter-car solution, and does not alter the physical study model.

M005 - Settling-band interpretation. All nine setups resolve 0.5/1/2 mm bands under solver/grid/horizon/RK4 agreement. Nominal after-exit times are 1.644585983 s, 1.269331763 s and 1.174272850 s respectively. These are alternative measurements of the same motion, not extra ML targets. The 1 mm band remains adopted; its value is a project tolerance, not a safety/comfort standard.

M006 - Tests and reproducibility. 178 focused tests pass in the complete suite: original 96, RK4 comparator 38, reduced diagnostic 34, verification-classification 10. Classification tests inject contact loss, unresolved narrow-band/tails/horizons, accumulated comparison differences and numerical failures without generating more pilot data. Known-solution, force/sign/units, invalid-input and solver-failure checks complement solver agreement. Original `quarter_car.py`, `run_nominal.py` and nominal result artifacts remain unchanged.

Reproducible artifacts: new RK4/reduced-case/verification modules and tests; WALKTHROUGH.md; README commands; generated HTML; `verification_results/CHECK_RESULTS.md`, summary.json, unit_tests.txt, two PNGs and compressed 1 ms pilot traces. Plotted traces show the complete selected observation window, including an extended window if needed. Final input hashes and saved traces are checked for consistency; plotting/source documents were visually/read-only reviewed. Runtime and derivative counts are recorded for all integrations; no repeated timing benchmark or performance optimisation is claimed. Python and four package versions remain those in revision 014; no installation was performed.

Decision D005: baseline RK45 with 1 ms observations and 5 s horizon is adequate as a starting setting at these nine pilots under the agreed criteria. Every later setup still requires contact/tail checks and unresolved-label handling. Remaining uncertainty includes unsampled combinations, real-car validity, travel clearances, future dataset sufficiency and ML accuracy/cost. No evidence in these pilots establishes an optimum suspension for comfort, grip or lap time.

## Current-stage evidence, 2026-10-04

U010 / D003 - The student explicitly adopted the consolidated starting specification and authorised coding the nominal simulation and its initial checks. Earlier unaccepted/no-coding wording below is historical and is superseded for this stage. No full parameter dataset, ML training, report writing or online publication was authorised or performed.

R003 - Access/version audit: HANDOFF 001, guide 003, and state/evidence/AI log 013 were read before implementation; all were present and no newer record was discovered. The 15-page workspace brief and Downloads copy are byte-identical (211,498 bytes), SHA256 `1029cf7c7c2844161af0c3727bbcbf40fac3913575683defe34ee942f9a9550c`. No printed revision/date was identified. An assistant read all pages and inspected existing renders of pp4-6 and p8. Separate written approval and the course schedule were not found in the inspected workspace inventory. User-reported approval/deadline remain context, not re-requested.

Course adaptation audit: main assistant read Week07_4 cells 27-31 and Week07_5 cells 9-10, 13-15, 28-30, 47-48; course-audit assistant additionally read the indexed RK4/refinement and analytical-oscillator cells and relevant Week01 testing/documentation/version-control/AI sections. No course code executed or originals modified. Week07_4/5 are nbformat 4.5 with Python 3.12.13 metadata and no numbered revision found; file hashes are saved in the simulation summary. C001/C002 cell references remain valid. Week01_2 cell 9 inaccurately implies merging removes a branch; that statement was not adopted. Week01_5 cell 4's real-world-only description of test data is too narrow and does not override the simulation-data plan.

S007 follow-up: reopened official SciPy stable documentation and the installed-version page, https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.integrate.solve_ivp.html , on 2026-10-04. Checked RK45, dense output, state tolerances, max_step, success/status and endpoint coverage. Installed SciPy is 1.13.1; the earlier recorded 1.18.0 referred to online documentation, not the environment. Reopened S002 equation source to confirm the force mapping. No new physical baseline or bump was substituted; S003/S004 provenance and their previously recorded retrieval limitations remain.

M001 - Measured nominal experiment and initial checks. Reproduce using `Suspension_Model/README.md`; code, configuration, exact package versions and source hashes are preserved. Final run: ms=365.4 kg, mu=43 kg, ks=24000 N/m, cs=2126.4 N s/m, kt=350000 N/m, g=9.81 m/s²; raised-cosine h=0.05 m, tau=0.50 s; equilibrium initial state. Baseline RK45 to 5 s and tight RK45 to 5/10 s follow P006. Tight 5 s trajectory sampled separately at 1/0.5/0.25 ms. A zero-road run and focused tests supplement the comparisons. An exploratory baseline run preceded the saved complete runner; repeated runs are checks, not distinct dataset rows.

| Actual nominal result | Measured value |
|---|---:|
| Full-response maximum A | 40.571154769 mm at 0.442 s, extension |
| Post-bump maximum A_post | 31.891620180 mm at 0.500 s |
| Sustained +/-1 mm entry | 1.769331763 s from bump start |
| Settling time after bump exit | 1.269331763 s; resolved under initial criteria |
| Minimum sampled total tyre force | 2626.595547 N at 0.366 s |
| Tight 5 s tail bound | 0.000368731156 mm |
| Tight 10 s tail bound | 7.333127453e-10 mm |
| Largest positive sampled post-bump energy increment | 0 J |

M002 - Actual checks: 96 focused pytest cases pass; 10 check groups pass in the runner. Independent hand arithmetic verifies 240 N spring and 212.64 N damper cases, force cancellation, a 13.791 J energy example and -191.376 J/s dissipation rate. Tests also cover full state continuity, relative/full-response target, settling recrossing/unresolved tails, invalid inputs, and failed/incomplete/nonfinite solver rejection. Zero-road states remain exactly zero. Full exit-state difference between integration segments is exactly zero.

Solver refinement differences: A 1.06057649e-7 mm; A_post 4.47123921e-7 mm; settling 3.34416939e-11 s. Grid 1-to-0.5 ms and 0.5-to-0.25 ms differences in A/A_post are zero at sampled maxima; settling differences are 8.51494275e-9 and 2.49508036e-9 s. The 5-to-10 s peak/settling differences are zero. All satisfy the adopted 0.05 mm / 0.01 s criteria with matching candidate status. The same time 0.442 s wins on all tested grids; this does not establish the exact extremum time or zero sampling error.

Energy/contact acceptance details added for implementation: maximum positive post-bump energy increment must not exceed `1e-10 * max(1 J, exit energy)`, allowing numerical noise. Contact must exceed `max(1 N, 10 * largest observed refinement change in sampled minimum)`; this evaluated to 1 N. These are transparent project numerical checks, not physical standards. All tested nominal summaries pass. The tail limit remains min(0.5 mm, A/2, A_post/2); zero-road equilibrium is handled separately. Numerical resolution flags also require successful finite solves, force/unit tests, continuity and energy checks; physical contact has its own flag.

Artifacts: `Suspension_Model/results/CHECK_RESULTS.md`, `summary.json`, `environment.json`, `unit_tests.txt`, response/physical-check PNGs, a readable 1 ms CSV and a compressed 0.25 ms NPZ time history. Runtime/derivative counts are measured and saved; grid variants reuse integrations, not independent timing trials. These numerical histories are not the proposed parameter-to-peak ML dataset.

Environment/setup: the existing Anaconda interpreter supplied Python 3.12.7, NumPy 1.26.4, SciPy 1.13.1, Matplotlib 3.9.2 and pytest 7.4.4. The bundled app runtime lacked SciPy/Matplotlib; no dependencies were installed. An optional Python-program-directory listing was access-denied; the existing Anaconda path was accessible. No prior Git repository/identity was found; one local workspace-root repository was initialised, excluding course originals and temporary/cache files. No remote/GitHub publication was performed. README, pinned versions and generated function HTML document reproducibility; a fresh-environment installation has not been tested.

Limits: nominal agreement/contact/energy checks support this implementation of the ideal model. They do not verify the entire parameter domain, real-vehicle behaviour, travel clearance, eventual dataset sufficiency or ML performance. Remaining pilot/RK4/reduced analytical/band-sensitivity checks are deferred as required by HANDOFF. No additional physical source or calibration claim was invented.

## Evidence labels

- Requirement: supported by the brief or documented teaching-team clarification.
- Source-supported: checked against an identified source; keep its scope and limitations.
- User-reported: supplied by the student, without independent verification.
- Assumption/proposal: adopted provisionally or suggested; not an established fact.
- Measured result: supported by a recorded calculation/experiment and its saved inputs/outputs.
- Open question: not yet resolved.

## Primary source

S001 — MMA3001_2026_Project_Brief.pdf

Original user-supplied location: C:\Users\dedvu\Downloads\MMA3001_2026_Project_Brief.pdf

Workspace copy: C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\MMA3001_2026_Project_Brief.pdf

Role: assessment requirements. All 15 pages were read again during the setup audit on 2026-10-02; relevant rendered pages 6, 8 and 9 were also inspected. PROJECT_STATE.md contains a working checklist; the original controls exact requirements. Calendar deadlines are in separate course scheduling material. The student supplied the submission deadline below; that scheduling material has not been independently inspected.

U001 - User-reported submission deadline, received 2026-10-02: Friday, 23 October 2026 at 23:59 (11:59 pm), Sydney time (Australia/Sydney). The weekday agrees with the calendar date. The student subsequently confirmed Sydney time and explicitly deferred presentation-date planning. This is user-reported scheduling information, not a date printed in S001.

Requirement locations, checked against the workspace copy during setup:

- p1: project worth 25% of the unit, assessment emphasis on individual learning/evaluation/justification/communication, and coordinator discussion for self-selected projects.
- p2: topic selection by the end of Week 5, teaching-team approval for student-proposed projects/datasets before substantial work, and no formal milestones. Approval considerations include data ownership, licensing and privacy.
- p3: simulation projects are explicitly permitted; external experimental or telemetry data are not universally required.
- p4: engineering context, scope, top-level and function-level inputs/outputs, units/formats/domains, invalid inputs, reproducibility and method explanation.
- p5: credible alternative/baseline comparison and justified validation, including metrics, influence on model selection and limits of evidence.
- p6: required performance analysis, appropriate improvements, advice on timing/profiling, and comparison with the selected/improved solution. Material AI-use disclosure must include approximate contribution and the reasons for using AI; exact percentages are not specified. Also covers responsibility and the prohibition on AI answering presentation/interview questions.
- p7: at least one numerical and/or ML method taught in the unit; it does not require using both.
- p8: report length/content, GitHub requirements, test functions/test report, report and ZIP-of-clone submission via Moodle, accessible repository link, and referral to the Unit Overview Spreadsheet for dates. The link's submission location is not explicitly specified.
- p9: presentation duration, content, appointment booking/attendance and Week 14 examination-period timing.
- p10-15: rubric categories are problem/inputs/outputs; repository structure, commits and README; inline comments/docstrings/HTML documentation; validation and engineering credibility; computational-approach justification; and critical reflection on AI use. These quality descriptors are distinct from a demand to add every possible technique.

## Setup audit findings, 2026-10-02

- Corrected AI_USE_LOG.md: the approximate AI contribution level is required by p6, although not yet assessed. Added the reason for using AI to its entry template.
- Clarified that the baseline must be compared using evidence, not merely identified.
- Added missing presentation content, assessment emphasis, repository/documentation quality guidance and page references to PROJECT_STATE.md.
- Preserved the report-length ambiguity: "5-10 pages maximum" with an explicit 10-page cap excluding references/appendices. A strict five-page minimum is not unambiguously stated.
- Preserved unknowns: submission time zone, presentation/booking dates, repository-link submission location and final technical selections. The student supplied the report/repository submission date and time during the audit (U001). No new approval, experiment or result was inferred.

Follow-up: the student subsequently confirmed Sydney time and asked to ignore presentation-date planning for now. The historical audit finding above is superseded for the time zone.

## Initial technical source

S002 - Peter Slaets, Computer Aided Simulation, "1.6. A quarter car suspension," KU Leuven teaching material (site copyright 2021; publication/update date not verified).

URL: https://fet-edu-em.pages.gitlab.kuleuven.be/computer-aided-simulation/course-material/t42cms-cas-book/t42cms-cas-lectures/Examples/Quarter_car_suspension/Quarter_car_suspension_model.html

Accessed: 2026-10-02. Inspected section 1.6.2, Mathematical model, including equation (1.11).

Supports a simplified two-mass model with vertical body/wheel motion, suspension spring and viscous damper, tyre elasticity, road displacement input and displacements measured from static equilibrium. The model omits tyre damping. Its equations provide a basis for the proposed physical formulation.

Limitations: a teaching model is not Ferrari 296 calibration or experimental validation. This source has not been used to select numerical parameter values, a road profile, output acceptance criteria or ML settings. Peak absolute dynamic relative displacement is a project choice accepted by the student (D001), not a requirement imposed by this source.

U002 / D001 - Explicit student decision, 2026-10-02: use the recommended largest dynamic movement in both directions. Adopt y = max over 0 <= t <= T of |zs(t) - zu(t)|, including the response after the bump. Static-equilibrium offsets and the observation duration must be handled consistently.

U003 - Subsequent student request, 2026-10-02: explore peak-to-peak travel as well, then evaluate which option is more suitable. This reopens comparison of D001 without selecting a replacement. Earlier statements that D001 was settled describe the prior stage.

U004 / D002 - Later student decision, 2026-10-02: follow the assistant recommendation for now, with much stronger interest in motion after the bump than peak-to-peak travel. Retain full-response maximum absolute travel as primary and peak-to-peak as a lower-priority supporting measure. No restriction to a post-bump-only primary maximum, new ML target, accepted bump/parameter set or implementation permission follows from this message.

Proposed equation mapping from S002 equation (1.11): source y maps to zs (body), source x to zu (wheel), m2 to ms, m1 to mu, b to cs and kw to kt. With d = zs - zu and road displacement r:

- ms * zs'' = -ks * d - cs * d'
- mu * zu'' = ks * d + cs * d' - kt * (zu - r)

These are two coupled second-order equations for a linear passive model measured about static equilibrium, so the constant gravitational terms have already been balanced. Their spring/damper forces are equal and opposite between the masses. This is an algebraic/source consistency check, not numerical verification or evidence of real-car validity.

## Bump and parameter research, 2026-10-02

Access audit: read PROJECT_GUIDE revision 003, PROJECT_STATE revision 004, this register revision 004 and AI_USE_LOG revision 004 before this update. Read all 15 pages of S001 again and visually inspected existing renders of pp4-6. S001 has no printed revision/date identified; its filename contains 2026. All requested files were present. Separate written teaching-team approval and the Unit Overview Spreadsheet/Moodle schedule were not present among the project files inspected. Topic approval and the 23 October 2026, 23:59 Sydney deadline remain user-reported, not reopened. Presentation-date planning remains deferred. The 30 course notebooks were present but not executed or re-reviewed this session.

S003 - MathWorks, "Robust Control of Active Suspension," official Robust Control Toolbox example, displayed release R2026b (original publication date not established).

URL: https://www.mathworks.com/help/robust/gs/active-suspension-control-design.html

Sections checked: "Quarter-Car Suspension Model" and "Time-Domain Evaluation."

Claim supported: the example uses a 50 mm cosine-shaped road bump, r(t) = 0.025*[1-cos(8*pi*t)] over 0-0.25 s, zero afterwards. Its model includes a passive spring/damper, tyre spring and optional active force. Setting active force to zero gives a passive model consistent with S002. The example also provides a complete alternative parameter set: 300 kg sprung mass, 60 kg unsprung mass, 16,000 N/m suspension stiffness, 1,000 N s/m damping and 190,000 N/m tyre stiffness. These alternative parameters are not P002's proposed baseline.

Applicability/limits: official simulation example, not a measured road profile or vehicle calibration. Its active controller, actuator constraints, time step and one-second plotting window are not being adopted. The general raised-cosine form h/2*[1-cos(2*pi*t/tau)] is an algebraic reparameterisation. P001's tau = 0.50 s, L = 2.5 m and v = 5 m/s are our proposed test design, not settings attributed to MathWorks.

Verification: read the source equation/code without executing it; checked peak height, finite support and zero endpoint slope algebraically. No source result reproduced. Saved source file: none; URL and relevant details recorded here. Access date: 2026-10-02. Used by: P001; alternative parameter-set provenance only.

S004 - Ming Foong Soong, Rahizar Ramli and Ahmad Saifizul (2017), "Between simplicity and accuracy: Effect of adding modeling details on quarter vehicle model accuracy," PLOS ONE 12(6), e0179485. Published 15 June 2017.

DOI: https://doi.org/10.1371/journal.pone.0179485

Publisher: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179485

Full-text archive: https://pmc.ncbi.nlm.nih.gov/articles/PMC5472327/

Table reference: Table 2, "Parameters relevant to quarter vehicle model," journal PDF p8 of 23; https://doi.org/10.1371/journal.pone.0179485.t002 . Context: "An insight into quarter vehicle model" and "Method of study."

Claim supported: the front-corner values are m_s = 365.4 kg, m_u = 43 kg, k_s = 24,000 N/m, c_s = 2,126.4 N s/m and k_t = 350,000 N/m. The authors obtained a generic midsized passenger-vehicle dataset from commercial simulation software; the damping coefficient is linearised. Their base representation omits tyre damping. The nonzero tyre-damping value also listed in Table 2 belongs to enhanced cases.

Applicability/limits: a coherent published modelling baseline, not measured specifications for an identified car, Ferrari/ACC calibration or validation of this project's output. The paper uses other road profiles; P001 is a separate choice. Its extra decimal places do not establish physical precision. No empirical +/-25% stiffness/damping range is claimed: P003 is our proposed local study domain.

Verification: parent and research sub-agent independently checked the table values in indexed primary full text from PMC; read the publisher's narrative to check provenance and base-model assumptions. The publisher table-image retrieval failed; it was not visually inspected. An indexed university PDF corroborated the table/page reference, but opening that old repository URL redirected to a repository migration notice; no local PDF was saved. No paper simulation or dataset was executed. Access date: 2026-10-02. Used by: P002 and the reference point for P003.

Proposal checks, not experimental results:

- For P001, substituting t = 0, tau/2 and tau gives heights 0, h and 0. The derivative is (h*pi/tau)*sin(2*pi*t/tau), zero at the joins; curvature is discontinuous there. The division by two is necessary for h to mean peak height.
- tau = L/v = 2.5/5 = 0.50 s; v = 5 m/s = 18 km/h. Doubling tau at fixed h halves peak road velocity and quarters peak road acceleration; no monotonic suspension-response claim follows.
- P003 is obtained by multiplying P002's k_s and c_s by 0.75 and 1.25. It has not been accepted or shown physically adequate across the domain.
- S002's equilibrium convention supports zero dynamic initial displacements at each setup's own equilibrium. Proposed initial velocities are also zero. Gravity remains relevant to a future tyre-contact diagnostic N = (m_s + m_u)*g + k_t*(r - z_u), even though static gravity terms cancel in the dynamic equations. Contact positivity has not been checked numerically.
- D001 is unchanged: max absolute dynamic body-wheel displacement including after the road returns to zero, excluding sag and distinct from peak-to-peak movement. A bump ending at tau does not establish that the observation period T is long enough.

## Output-measure comparison, 2026-10-02

S005 - James Mackey, Pico Technology, "Maximum, minimum and peak to peak measurements and math channels," updated 28 August 2025.

URL: https://www.picotech.com/library/knowledge-bases/oscilloscopes/maximum-minimum-and-peak-to-peak-measurements-and-math-channels

Sections checked: Introduction, Background, Calculation and algorithm. Access date: 2026-10-02. Saved source file: none.

Claim supported: peak-to-peak is maximum minus minimum over the chosen observation, including extrema due to transients. Applicability/limits: primary instrument-manufacturer explanation of a general signal measurement, not a suspension-design standard, vehicle validation or endorsement of a primary ML target. The following suspension comparison is our algebraic application to d(t), not a result claimed by this source.

T001 - Algebraic comparison (not a numerical experiment): for the proposed observation beginning at initial equilibrium, C = -min d >= 0 and E = max d >= 0. Then A = max |d| = max(C,E), P = max d - min d = C+E and A <= P <= 2*A. Equality P = 2*A requires C = E. Include bump and post-bump response in both measures; final T is unselected.

Hypothetical examples checked by arithmetic: (C,E) = (32,18) mm gives (A,P) = (32,50) mm; (28,26) gives (28,54) mm. The two measures can therefore reverse the ranking of setups. Equal P also hides different extremes: (40,10) and (25,25) both give P = 50 mm. These examples are invented for explanation and do not claim such responses for the proposed model or parameter domain.

Engineering deductions: neither summary preserves both signed extrema, oscillation count or accumulated travel. Physical stop clearance requires separate compression and extension checks against actual available clearances; those have not been sourced. Peak-to-peak cancels a constant coordinate offset, while A requires the equilibrium reference to be correct. This does not establish that changed stiffness leaves sag, clearance or dynamics unchanged. ML difficulty, actual setup rankings and sufficient observation/peak-resolution settings have not been tested.

P004 originally recommended recording C, E, A and P from the same simulation with one primary ML target. U004/D002 subsequently accepted the recommendation for now: A primary, P supporting, with post-bump behaviour of greater interest. No coding or report writing was begun.

T002 / P005 - Post-bump interpretation, 2026-10-02: reopened S002 section 1.6.2 and equation (1.11). Setting road input r to zero after the bump leaves dynamic equations that can continue evolving from nonzero body/wheel positions and velocities. This is a deduction from the source model, not a measured result. Proposed A_post = max over [tau,T] |d(t)| is no greater than the full-response A over [0,T]. A proposed settling diagnostic would measure elapsed time from tau until |d| stays within an as-yet-unselected absolute band for the remaining, sufficiently long observation. It measures suspension-relative settling only; it does not establish that all vehicle motion has settled. Avoid a relative band based on final d = 0 and do not mistake first zero crossing for settling. These definitions, the threshold, tail adequacy and any extra ML target have not been accepted or tested. No new external source or numerical experiment was added.

## Settling-definition refinement, 2026-10-02

S006 - MathWorks, "stepinfo - Rise time, settling time, and other step-response characteristics," official Control System Toolbox documentation, displayed release R2026b.

URL: https://www.mathworks.com/help/control/ref/dynamicsystem.stepinfo.html

Sections checked: Description (SettlingTimeThreshold), "Specify Percentage for Settling Time or Rise Time," and Algorithms. Accessed 2026-10-02; no local source copy saved.

Supports the distinction between first entering a band and subsequently staying inside it. Its default step-response settling band is 2% of the initial-to-final output change; its separately defined transient time uses peak error as the reference. Applicability/limits: official response-analysis convention, not a suspension tolerance standard or instruction to use MATLAB. For this project's full bump response, initial and final equilibrium d are both zero, so blindly using a percentage of their difference gives a zero-width band. This motivates explicitly specifying our own tolerance; it does not establish 1 mm as an industry requirement.

T003 / P005 refinement (proposal): epsilon = 1 mm, measured about d = 0, with elapsed time counted after bump exit tau until the deflection stays within the band for the remaining adequately observed response. Unlike a per-run peak-normalised band, this uses the same residual-deflection tolerance for every setup. Illustrative timing only: 2.10 - 0.50 = 1.60 s. Suggested later sensitivity bands: 0.5, 1 and 2 mm. These numbers are assistant-proposed study choices, not source measurements or completed tests. The student's "ok" authorised continuing the explanation; the numerical band had not yet been presented and was not marked accepted. Observation horizon, tail verification and threshold-crossing accuracy remain unresolved. Primary target D002 is unchanged.

## Consolidated physical specification check, 2026-10-02

U005 - Student instruction "ok lets do it" followed the proposal to return to the bump and vehicle parameters before observation duration. Used as authorisation to continue specification work; no project coding/report writing or explicit individual approval of all parameter values is inferred.

T004 - Rechecked S004's front values in indexed primary PMC Table 2 and S003's road-input expression; no new external source added. Consolidated the existing P001-P003 and P005 into assistant-selected provisional working defaults in PROJECT_STATE. Source-backed values (S004 baseline, S003 bump shape/height) remain distinguished from chosen domain (+/-25%), crossing duration (0.50 s) and settling band (1 mm).

Checks: 0.75/1.25 times 24,000 gives 18,000/30,000 N/m; the same factors times 2,126.4 give 1,594.8/2,658.0 N s/m. The illustrative nominal dynamic force magnitudes are 24,000 * 0.010 = 240 N and 2,126.4 * 0.10 = 212.64 N. Both are algebraic illustrations, not model response results. An independent assistant review checked the units, passive interpretation, static-equilibrium convention and use of effective vertical coefficients. Values are held constant during a run and varied only between runs. Numerical adequacy, physical validity of the full domain and ML difficulty remain untested.

## Numerical specification sources and checks, 2026-10-02

U006 - Student request "ok proceed" authorised the next numerical-specification discussion. The prior instruction against project coding/report writing remains active. No future experiment or numerical outcome is implied by that authorisation.

S007 - SciPy developers, "scipy.integrate.solve_ivp," official documentation, displayed SciPy v1.18.0. This is the documentation version, not a verified installed version for the project.

URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

Accessed 2026-10-02. Sections read: initial-value system, methods (RK45), t_eval/dense_output, events, max_step, rtol/atol, and result status. No local source copy saved.

Claims supported: RK45 uses an embedded 5(4) Runge-Kutta pair; output evaluation times differ from internal steps; absolute tolerances can differ by state component; local error scales use atol + rtol*abs(state). Event sign changes may be missed when several occur inside a step. Applicability/limits: official numerical-library behaviour, not proof of accurate peaks, a quarter-car calibration, or a source for our chosen time window/tolerances. No SciPy call solving a model was run.

T005 / P006 - Proposed numerical plan in PROJECT_STATE: RK45 as primary, explicit four-state order, a 5 s trial window checked against 10 s (and 20 s if required), separate solver/output-grid refinement, nine low/reference/high pilot combinations, and refined classical RK4 comparison. The 0.05 mm peak-agreement and 0.01 s settling-agreement limits, reference grids, tolerance settings, 1 s confirmation period and window schedule are assistant-selected criteria, not source requirements or observed accuracies. Pilot cases do not prove the whole parameter domain; later runs require validity checks. Runtime and derivative counts are planned measurements only.

Algebraic post-bump energy check, derived here from S002: H = (m_s*v_s^2 + m_u*v_u^2 + k_s*d^2 + k_t*z_u^2)/2 for r = 0. Differentiate and substitute the two equations: H' = -c_s*(v_s-v_u)^2. For positive parameters, H cannot increase and k_s*d^2/2 <= H, so future |d| <= sqrt(2*H(T)/k_s). This is an analytical property of the exact linear model, not a simulated result. P006's numerical tail test uses a factor-of-two margin and includes A_post as well as A; it must not be called rigorous certification unless state uncertainty is bounded. Zero-response cases need separate handling. Independent assistant review checked the derivation and the need to protect the post-bump peak separately. Energy can increase during road forcing, so the monotonicity check is restricted to after bump exit.

Verification boundaries: analytical single-mass checks verify a reduced case, not the entire quarter-car; shared model errors can survive agreement between two solvers. Positive tyre contact is a physical-assumption check. No physical validity or actual accuracy has yet been established by the planned checks.

## Dataset and regression specification sources, 2026-10-02

U007 - Student instruction "ok proceed" followed the proposed next step of dataset sampling and ML selection. It authorises continuing specification; it does not lift the explicit boundary against project coding/report writing. Read guide 003 and state/evidence/AI log 010 for this task. No requested record was missing; the earlier brief access/version audit remains applicable.

S008 - Scikit-learn developers, "SVR," official API documentation, displayed version 1.9.1.

URL: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html

Inspected: class description, kernel/gamma/C/epsilon parameters and fit status. Supports epsilon-SVR, RBF kernel controls, epsilon's no-penalty band and increasing training cost with sample count. P008's target-unit choice and candidate values are our application, not source recommendations for suspension modelling. Documentation version is not the locally installed version. Accessed 2026-10-02; read only, no example executed or local source copy saved.

S009 - Scikit-learn developers, "Common pitfalls and recommended practices," official documentation, displayed version 1.9.1.

URL: https://scikit-learn.org/stable/common_pitfalls.html

Inspected: inconsistent preprocessing and data leakage sections. Supports fitting preprocessing on training data only and carrying the same transformation into predictions; pipelines help maintain that separation. Applied to P008's scaling and any future cross-validation. Does not endorse our physical inputs or dataset size. Accessed 2026-10-02; no source example executed or local copy saved.

S010 - Scikit-learn developers, "Cross-validation: evaluating estimator performance," official documentation, displayed version 1.9.1.

URL: https://scikit-learn.org/stable/modules/cross_validation.html

Inspected: opening discussion of held-out test data, validation for tuning, and k-fold cross-validation. Supports separate training, selection and final-evaluation roles and the danger of repeatedly tuning on test results. P007's 225/75/100 grid/random design, seeds and bounded initial holdout strategy are our choices, not a prescribed source split. Five-fold development-only CV is an available taught extension if needed. Accessed 2026-10-02; no source example executed or local copy saved.

S011 - Scikit-learn developers, "Metrics and scoring: quantifying the quality of predictions," official documentation, displayed version 1.9.1.

URL: https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics

Inspected: regression metrics, R-squared, MAE, MSE/RMSE and MAPE. Supports dimensional error measures, squared-error weighting, the dataset-dependent meaning of R-squared and percentage error's target denominator. Selecting validation RMSE and reporting finite-sample extremes are project choices. No source supplies a suspension-specific ML pass threshold. Accessed 2026-10-02; no example executed or local source copy saved.

T006 / P007-P008 - Specification checks only: 15*15 = 225; 225+75+100 = 400; training plus validation = 300; 3*3*2 = 18 proposed SVR settings. Fifteen equally spaced levels have fourteen intervals; the middle level is the nominal midpoint, so the minimum/reference/maximum nine pilots are included. Repeated numerical runs provide one final label per setup. Converting epsilon 0.1 m to millimetres gives 100 mm, illustrating why the ML target units must be explicit. None of these arithmetic checks generated data pairs, labels or predictions.

Modelling/evaluation inference: linearity in the motion variables does not imply that the maximum response is linear in stiffness or damping. An RBF surface is a reasonable candidate, but changes in the controlling peak can introduce corners. A two-input grid is simple to explain and includes endpoints; independent off-grid validation/test points assess new combinations under an artificial uniform distribution. Good interpolation scores do not establish accuracy for new bumps, parameter ranges or a real vehicle. Numerical label accuracy must be evaluated separately.

Alternative considered: shuffled five-fold CV on development data is directly taught and can reduce dependence on one validation split, but adds repeated fitting and explanation. The initial recommendation uses explicit training/validation/test roles and reserves CV for justified follow-up within development data. Uniform random training is valid but has less predictable coverage than a small two-input grid. These are scope/teaching judgements, not benchmark outcomes.

## Complete-specification review, 2026-10-02

U008 - Student instruction "ok lets do it" followed the assistant's offer of a concise complete-specification review before implementation. It authorises that review. The original instruction "Do not begin coding or report writing yet" remains the reason to seek one explicit scope change before baseline coding, not a new requirement invented from the guide.

R001 - Read guide 003 and working records 011; confirmed all four records and the workspace 2026 brief remain accessible. Used the already-recorded full brief audit rather than claiming a fresh complete PDF reading. Two independent assistant reviews found the force signs, units, parameter bounds, initial state, primary/supporting outputs, tail checks, sample counts, target units and train/validation/test roles internally consistent. No new external source was added, notebook executed, input sample generated, numerical check run or model fitted. Consistency is not verification of an implementation or validation of a real vehicle.

Record correction: historical T002/T003 and the original P005 text described choices still unspecified at those earlier stages. Later P005 refinement and P006 now propose a 1 mm band, initial five-second window and explicit tail/refinement checks. PROJECT_STATE wording was clarified to distinguish these current proposals from untested adequacy. The historical entries retain their chronology; no prior proposal is retroactively marked accepted.

Review outcome: assemble the current recommendations into a single starting specification, preserve D002 and the post-bump emphasis, and stage future work beginning with the nominal physical simulation and initial checks. The full 400-case dataset and ML comparison come after simulator verification. No claim of adequate duration, contact preservation, sufficient data, predictive accuracy or speed benefit follows from this review.

## Handoff preparation and workflow guidance, 2026-10-04

U009 - The student asked whether a new chat or the existing one would provide better context, then requested next steps and an appropriate handoff. This requests guidance and a handoff artifact, not automatic chat creation or new implementation permission. Current files were checked at guide 003 and state/evidence/AI log 012 before saving revision 013 and HANDOFF revision 001.

S012 - OpenAI, "Best practices," official documentation, section "Organize long-running chats."

URL: https://learn.chatgpt.com/guides/best-practices#organize-long-running-chats

Accessed 2026-10-04 in the preceding chat-organisation exchange using the OpenAI Docs skill; opened the page and read the relevant section. Supports using one chat for a coherent unit of work, retaining the same chat for related work, and the existence of context compaction. Recommending a new chat at this project's specification-to-implementation boundary is our workflow judgement, not an assurance that a new chat has superior recall or automatically inherits this conversation. The handoff explicitly names the local records to read. No app setting or chat was changed.

R002 - Handoff checks: matched current file revisions, confirmed the primary output/post-bump preference, kept proposed settings distinct from verified results, and identified the unresolved adoption/coding boundary. A course-audit assistant reviewed the bounded first-stage completion criteria. The optional authorisation sentence is proposed text for the student to send, not a recorded decision. No new physical/numerical source or experiment was added.

## Course-method index

The previous review inspected 30 local notebooks; it did not execute their code. This index records relevant coverage, not new experimental verification.

| ID | Notebook(s) | Relevant coverage |
| --- | --- | --- |
| C001 | MMA3001_Notes_Week07_5_Higher_Order_ODEs.ipynb | Mass-spring-damper equations, first-order state systems, numerical solution and analytical checks |
| C002 | MMA3001_Notes_Week07_4_Runge_Kutta_Methods.ipynb | RK4, adaptive RK methods, accuracy/convergence and computational cost |
| C003 | MMA3001_Notes_Week07_2_ODEs_and_Initial_Value_Problems.ipynb; MMA3001_Notes_Week07_3_Eulers_Method.ipynb | Initial-value problems and a simple numerical integration method |
| C004 | MMA3001_Notes_Week03_6_Interpolation_in_Machine_Learning.ipynb | Surrogate modelling using simulated or experimental data |
| C005 | MMA3001_Notes_Week05_1_Linear_Regression.ipynb | A regression baseline and prediction errors |
| C006 | MMA3001_Notes_Week05_2_Decision_Tree_Regression.ipynb; MMA3001_Notes_Week05_3_Support_Vector_Regression.ipynb | Candidate nonlinear regression methods; complexity control and scaling where relevant |
| C007 | MMA3001_Notes_Week05_5_Evaluating_Regression_Performance.ipynb; MMA3001_Notes_Week05_6_Training_Data_Evaluation_and_Selection.ipynb | Evaluation, data splitting, overfitting and leakage prevention |
| C008 | MMA3001_Notes_Week02_1_Optimisation_and_Profiling.ipynb; MMA3001_Notes_Week02_2_Numerical_Errors.ipynb | Performance measurement and numerical errors |
| C009 | Week01 notebooks on Data_Management_and_Version_Control, Documenting_and_Communicating_Code, Responsible_Use_of_AI, Testing_and_Debugging | Repository management, documentation, testing and responsible AI use |

All notebooks are in the existing MMA3001 notebook folder. Consult the actual notebook before adapting its examples; record cell references for claims used in the final report.

Focused reread on 2026-10-02 for P006: a course-audit assistant inspected Week07_4 and Week07_5, and the main assistant reread the specific tolerance/state/analytical/energy cells below. No notebook cells were executed. Indices are one-based JSON notebook cell positions, not displayed execution counts; these refer to the current workspace copies, whose future edits could change indexing.

| Notebook | Cells | Evidence used |
| --- | --- | --- |
| Week07_4_Runge_Kutta_Methods | 12, 17, 21-23 | Classical RK4 stages/implementation and fixed-step convergence, supporting a cross-check |
| Week07_4_Runge_Kutta_Methods | 27-31 | Adaptive RK45, local-error tolerances, solve_ivp contract, internal steps versus output interpolation |
| Week07_4_Runge_Kutta_Methods | 32-33 | Tolerance refinement against an analytical reference and computational work |
| Week07_5_Higher_Order_ODEs | 9-10, 13-15 | Position/velocity state reduction, state order and vector RK45 mechanical example |
| Week07_5_Higher_Order_ODEs | 19-21 | Analytical damped-oscillator verification and distinction from physical validation |
| Week07_5_Higher_Order_ODEs | 28-30 | Single-mass energy balance, extended algebraically to both masses and springs for P006 |
| Week07_5_Higher_Order_ODEs | 47-48 | Component tolerances and complementary model/numerical checks |

Rationale for the recommendation: primary RK45 follows the taught vector mechanical example and reduces custom solver maintenance for a beginner. Classical RK4 remains a taught, independently implemented numerical comparator. Neither a finer sample grid nor tighter solver tolerance alone guarantees accurate output extrema; check both.

Focused reread on 2026-10-02 for P007/P008: a course-audit assistant inspected Week05_1/2/3/5/6. The main assistant reread Week05_3 cells 5, 13-15, 18, 22, 34, 41 and 45, and Week05_5 cells 6, 9, 16-17, 23-24, 28, 31 and 36. Notebook contents were read as JSON/text only; no cells or saved results were executed/reproduced. Cell positions remain one-based JSON indices.

| Notebook | Cells | Evidence used |
| --- | --- | --- |
| Week05_1_Linear_Regression | 4, 14-15, 25-26 | Samples/features/target, linear baseline and validation |
| Week05_2_Decision_Tree_Regression | 14-15, 22-28 | Tree complexity and overfitting; alternative considered |
| Week05_3_Support_Vector_Regression | 5, 13-15, 18, 22 | RBF interpretation, training-only scaling, C/epsilon/gamma and target units |
| Week05_3_Support_Vector_Regression | 27-31, 34, 41, 45 | Tuning interactions, extrapolation, gamma versus feature scaling and limitations |
| Week05_5_Evaluating_Regression_Performance | 6, 9, 16-17, 23-24 | Metric choice, separate data roles and linear/tree/RBF response shapes |
| Week05_5_Evaluating_Regression_Performance | 28-33, 36-37 | Regional/directional errors, optional CV, refit and final-test discipline |
| Week05_6_Training_Data_Evaluation_and_Selection | 4, 13-15, 19, 28-30 | Row identity, prediction domain, duplicates/groups and preprocessing leakage |

The Week05_5 example starts with a random 60/20/20 split and later cross-validates on development data. P007's grid training plus independent validation/test sets is a project-specific adaptation of the same role separation, not a reproduction of the example's split proportions.

## Current conclusions and limits

- Taught ODE and regression methods support the proposed narrow quarter-car/ML project.
- Extending a single mass-spring-damper example to a quarter-car requires a correctly formulated physical model; course-method coverage alone does not validate that extension.
- RK4 and adaptive RK45 are different algorithms and should not be used interchangeably in descriptions.
- The numerical simulator needs verification separately from evaluating ML agreement with simulated outputs.
- A published generic parameter set and raised-cosine road input have now been sourced (S003/S004). Their proposed use and exact test settings remain unaccepted. No vehicle-specific calibration, telemetry validation or project performance result has been established.

## Technical research still required

- Review and adopt or revise the sourced model assumptions, nominal parameters and road proposal.
- Review P003's candidate domain and P007's grid/off-grid sampling proposal; their physical validity and sample sufficiency remain unverified.
- Review the full P001-P003/P005-P008 specification together. Implement and test only after the coding boundary is lifted. Solver accuracy, sample adequacy, regression performance and computational benefit remain unknown.

## New source entry template

ID:
Author/title/year:
URL or DOI:
Saved file:
Page/section/equation/notebook cell:
Claim supported:
Applicability and limitations:
Verification performed:
Access date:
Decision or report section using it:

## Future numerical-result entry template

Run ID/date:
Code version:
Inputs/configuration/data version:
Random seed, if applicable:
Checks performed:
Output files and result:
Limitations/unresolved issues:

No simulation or ML run is recorded yet.
