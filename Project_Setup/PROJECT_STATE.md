# MMA3001 project state

Revision: 016 | Updated: 2026-10-05 | Status: 400-setup dataset generated and checked; ML not started

## Current stage

The nominal simulation, bounded nine-pilot verification and first 400-setup dataset are complete. These records document implementation and numerical evidence, not the assessed report. No learned preprocessing, ML training or final-test prediction evaluation has begun.

D003 / U010, 2026-10-04: the student explicitly adopted the consolidated specification as the starting plan and authorised coding the nominal simulation and initial checks, without another approval request. D004 later authorised bounded verification; D006 below authorises dataset generation. ML training, assessed report writing and GitHub publication remain outside this completed stage. Adoption makes the values starting decisions, not verified physical facts or a validated parameter domain.

Historical sections below retain their original proposal/review chronology. Their statements about unaccepted settings, unrun checks and missing permission describe those earlier stages; this current-stage section and D003-D007 supersede them. PROJECT_GUIDE 003 and HANDOFF 001 are preserved as read. Their historical boundaries yield to the student's current instructions.

## Dataset checkpoint, 2026-10-05

D006 / U012 - Following completion of the nine-pilot verification and the proposed next dataset stage, the student said "proceed". Implemented the adopted P007 design and per-row checks. This authorises dataset generation, not ML fitting, assessed report writing or GitHub publication. D002's full-response max abs(zs-zu), static-equilibrium convention and post-bump priority are unchanged.

D007 - Recorded implementation details before response generation: 15 by 15 endpoint-inclusive training grid, stiffness outer loop and damping inner loop; separate NumPy Generator(PCG64(seed)) instances for validation seed 3001 and test seed 3002; one uniform draw of shape (count,2) per split, columns [ks,cs], retained draw order. Fixed IDs train_001-225, validation_001-075 and test_001-100. No noise, redraw, reshuffling, dropped rows or role changes. Counts/seeds/domain come from the adopted P007 starting plan; the explicit traversal/generator/serialization rules make it reproducible, not an empirically optimal design.

- Read guide 003, handoff 001 and current state/evidence/AI log 015. The newer local records supersede the handoff's expected 013 and historical no-implementation status. No required source was missing or newly conflicting. Reread actual Week05_6 row/split/leakage cells and Week05_5 evaluation-role/final-test cells before adaptation. Original brief and numerical-course source hashes remain unchanged; no fresh complete brief reread or notebook execution is claimed.
- Generated `Suspension_Model/dataset_v1/`: 225 training, 75 validation and 100 reserved test rows; all 400 input pairs and IDs are unique and in the declared domain. The nine original baseline pilot summaries are reused only in training at 5 s / 1 ms. Completed 391 new dataset integrations; verification/test solves are not extra dataset samples.
- All 400 primary targets pass the prescribed solve/finite/continuity, peak consistency, contact, energy and tail screening. All 400 relative settling times are resolved under adopted settings, with no unresolved entries. These rows did not each receive the complete refinement/RK4 programme; that evidence remains the nine pilots.
- Minimum sampled tyre force: 2398.808925801 N, above the fixed 1 N screening guard. Maximum 5 s remaining-motion bound: 0.011530650542 mm, below every row's tail/peak margins. Maximum positive sampled post-bump energy increment: 0 J. No failure reasons recorded. The baseline-grid contact minimum differs slightly from the pilot tight-reference figure; they are different numerical observations, not conflicting records.
- Saved-file audit verifies identities, splits, physical parameters, exact input round trips, independently recomputed validity decisions and metre-to-millimetre target conversion. Source files and the plan/setup manifests remained byte-identical throughout generation. The combined test suite passes 280 cases, including deliberately corrupted exports, stale caches, missing diagnostics and retained failed rows. Input-only coverage plot was visually inspected.
- Exact configuration, environment, source/output hashes, raw SI summaries, post-bump/settling diagnostics and measured work are saved. New integrations used 2,423,152 derivative evaluations and 78.963229 s of summed integration time; the row-generation loop took 86.702437 s. These are one-run laptop timings, not a benchmark or ML speed comparison. Historical reused pilot integration time is recorded separately, not counted as new work.
- Final-test response files are segregated under `heldout_test/`. Only predefined physical/numerical checks, input identity, unit checks and counts were inspected for that split; no target distribution, response plot or prediction error was used for development. No scaler or ML model has been fitted.

Start with `Suspension_Model/DATASET.md` and `dataset_v1/CHECK_RESULTS.md`. For a fresh reproduction in the recorded environment, run `generate_dataset.py --output dataset_recheck` from `Suspension_Model/`. Existing output directories are refused. This command recipe is saved; a second full generation and a clean-environment installation were not executed. Exact Python build and NumPy/SciPy checks protect pilot reuse; changing environment needs reviewed verification/artifact refresh, not bypassing provenance guards.

Remaining uncertainties: exact continuous-time label error at each nonpilot row, contact between sample times and at unsampled parameter values, real-vehicle validity and travel clearances, dataset sufficiency and ML accuracy/cost. Student understanding and overall AI contribution remain unassessed. The original nominal/pilot results and governing-model code remain unchanged. Local checkpoint is AI-attributed; no packages installed, global Git identity changed or remote published. Submission remains 23 October 2026 at 23:59 Australia/Sydney; presentation-date planning stays deferred.

## Verification checkpoint, 2026-10-05

D004 / U011 - After the assistant proposed a nominal walkthrough followed by the bounded verification programme, the student said "ok proceed". This authorises that next stage. It does not extend the task to the full dataset, ML training, assessed report or GitHub publication. The walkthrough is saved in `Suspension_Model/WALKTHROUGH.md`; explanations were also given in chat. No student understanding or independent rerun is inferred.

- Read guide 003 and current records 014; existing repository was clean at nominal checkpoint `4228532`. No newer conflicting record or missing required source was found. Reread actual Week07_4 RK4/refinement cells and Week07_5 analytical-oscillator cells before adapting. The original brief remains byte-identical to the previously read copy; no fresh full brief reread is claimed. Course originals and original nominal result files remain unchanged.
- Completed all nine low/nominal/high combinations of ks={18000,24000,30000} N/m and cs={1594.8,2126.4,2658.0} N s/m. Each compares baseline RK45, tighter RK45, 1/0.5/0.25 ms observations, 5 versus 10 s, and classical RK4 at 0.5/0.25 ms. RK4 carries all exit states and evaluates the road at every intermediate stage time. Repeated runs/grids are verification work, not extra parameter samples.
- All nine pilots pass. Direct baseline 1 ms / 5 s versus tight 0.25 ms / 10 s maximum differences: A 0.000464923531 mm; A_post 7.47171516e-7 mm; settling across all three bands 8.86295923e-6 s. All are below the adopted 0.05 mm and 0.01 s limits. Extending 5 to 10 s changed no sampled peak or settling result. No 20 s extension was needed.
- Same-grid RK4/RK45 maximum A discrepancy: 2.24514157e-8 mm; maximum A_post discrepancy: 1.57725152e-8 mm. RK4 step-halving peak changes also include changes in observation spacing, so they are not claimed as pure integration error or a measured convergence order.
- Tyre contact, energy, tails, finite complete solves and full exit-state continuity pass separately for all runs. Minimum tight-reference sampled contact force across pilots is 2398.782752 N. Largest tight 5 s future-movement bound is 0.01080601534 mm, below 0.5 mm and the peak margins. This is numerical/model-consistency evidence, not an exact continuous-time bound or full-domain proof.
- Reduced analytical check: wheel deliberately fixed at zero; existing body-force function compared with the unforced underdamped closed-form solution from initial x=0.010 m and v=0.020 m/s. Maximum errors: 3.80071e-13 m in position and 3.05054e-12 m/s in velocity, below diagnostic limits 1e-7 m and 1e-6 m/s. This clamp does not replace the full study model.
- Settling-band sensitivity is resolved for all nine setups. Nominal times after exit: 1.644586 s at +/-0.5 mm; 1.269332 s at +/-1 mm; 1.174273 s at +/-2 mm. The +/-1 mm band and full-response A remain unchanged. Nominal A, A_post and +/-1 mm settling exactly reproduce the original checkpoint in this environment.
- The combined test suite passes 178 cases, including failure-classification tests: contact failure remains separate from numerical peak resolution; unresolved narrow-band/tail/horizon outcomes and accumulated comparison errors cannot silently pass. Independent assistant review found and corrected a plot limit that would have hidden a required horizon extension; final outputs were regenerated.

D005 - Numerical settings decision from these pilot results: retain baseline RK45 rtol=1e-6, atol=[1e-9 m,1e-8 m/s,1e-9 m,1e-8 m/s], max internal step=0.005 s, 1 ms observations and a common 5 s observation as starting settings for later simulations. Every later setup still needs contact/tail checks and separate output-validity flags; unresolved primary labels must not be used. The 10 s tight solution remains the verification reference, not evidence of a new study input or extra row.

Reproduce with `Suspension_Model/run_verification.py`. Actual tables, plots, all per-run comparisons, band results, derivative counts, single-run timings, source hashes, environment versions and compressed traces are saved in `Suspension_Model/verification_results/`. New modules and tests are documented in generated HTML. Existing dependencies are unchanged; no packages installed. Local Git checkpoint uses explicit AI authorship; no GitHub remote, student identity or global Git settings changed.

Remaining uncertainties: unsampled parameter combinations, real-vehicle/telemetry validity, physical travel clearances, later dataset sufficiency, ML accuracy/cost and student understanding/AI contribution. Nine checked locations do not certify the whole rectangle. GitHub hosting and licence selection remain future repository work. Submission remains 23 October 2026 at 23:59 Australia/Sydney; presentation-date planning stays deferred.

## Nominal checkpoint, 2026-10-04

- Access audit: read HANDOFF 001, guide 003, and state/evidence/AI log 013; all requested files and all 30 course notebooks were accessible, with no newer setup records discovered. Read the complete 15-page 2026 brief and relevant course cells. Workspace and Downloads brief copies are byte-identical; no numbered brief revision/date was identified. No separate written topic-approval or course-schedule file was found in the inspected inventory; student-reported approval/deadline remain accepted context.
- Implemented in `Suspension_Model/`: four-state passive quarter-car, raised-cosine road, piecewise RK45 with full exit state retained, full-response A, post-bump A_post, sustained relative settling and explicit tail/contact flags. Original course materials were read but not edited or executed.
- Actual nominal results: A = 40.571154769 mm at 0.442 s (extension); A_post = 31.891620180 mm at 0.500 s (exit included); settled within +/-1 mm from 1.769331763 s, or 1.269331763 s after exit. Settling is resolved under the initial numerical criteria, not certified for an exact continuous trajectory or all vehicle motion.
- Initial checks pass: exact zero-road equilibrium, finite successful complete solves, all four exit-state components retained, independent force/sign/unit checks, solver/output-grid/horizon agreement, sampled positive contact and post-bump energy/tail checks. Focused pytest suite: 96 cases pass. The check runner records 10 passed check groups and actual outputs in `Suspension_Model/results/CHECK_RESULTS.md` and `summary.json`.
- Solver refinement changed A by 1.061e-7 mm and A_post by 4.471e-7 mm. The largest settling comparison difference was 8.515e-9 s. Output-grid peak differences and 5-to-10 s changes were zero at the sampled resolutions. Criteria remain <=0.05 mm and <=0.01 s; agreement is not an exact-error bound.
- Minimum sampled tyre force: 2626.595547 N; refinement-based ambiguity margin: 1 N. No sampled post-bump energy increase. Tail bound at 5 s: 0.000368731156 mm, below the 0.5 mm criterion; at 10 s: 7.333e-10 mm. Five seconds was adequate for this nominal case under the initial checks; a common domain-wide duration remains unselected.
- Reproducibility: existing Anaconda Python 3.12.7, NumPy 1.26.4, SciPy 1.13.1, Matplotlib 3.9.2, pytest 7.4.4. No packages installed. The app's bundled runtime lacked SciPy/Matplotlib; the existing course-capable Anaconda environment was used. README instructions, pinned dependencies, environment/configuration/source hashes, time histories, plots, test output and generated HTML function documentation are saved with authored work.
- No pre-existing Git repository was found. A single local repository was initialised at the workspace root, with course originals and temporary/cache files excluded. No GitHub remote was configured or published. Initial checkpoint attribution is explicitly AI-authored because no student Git identity was configured; no global identity was changed. Check current `git log` for the saved checkpoint identifier.
- Still unverified: remaining nine-pilot programme, RK4 comparison, reduced analytical oscillator, 0.5/1/2 mm band sensitivity, full-domain contact/tails, dataset adequacy and ML accuracy/cost. No physical travel clearance, real-vehicle validation or Ferrari calibration established. Student understanding and overall AI contribution remain to be reviewed.

The submission deadline remains 23 October 2026 at 23:59 Australia/Sydney. Presentation-date planning remains deferred.

## Complete specification review, 2026-10-02

Review status: read guide 003 and state/evidence/AI log 011; all four records and the 2026 brief are accessible. The brief's earlier full-reading/version audit remains the source of requirements; it was not reread in full for this consolidation. No printed brief revision was previously identified. No new missing file or material contradiction was found. Two independent assistant reviews checked the physical/numerical and data/ML sections. This is a consistency review, not a numerical test or physical validation.

The confirmed question is about the largest dynamic departure from suspension equilibrium, including motion after the bump. The proposed project studies how spring stiffness and damping affect that response and post-bump settling, then compares regression methods for predicting the primary peak at unseen setups.

| Item | Consolidated starting specification | Status/provenance |
| --- | --- | --- |
| Primary output | A = max over [0,T] of abs(z_s-z_u), about each setup's static equilibrium; report mm | Confirmed D002; includes bump and post-bump movement, not peak-to-peak |
| Post-bump interpretation | A_post from bump exit onward; sustained settling within +/-1 mm timed from exit; retain representative motion curves | Priority confirmed; numerical definitions/band are P005 proposals |
| Physical model | Passive linear vertical two-mass front quarter-car; start from rest at equilibrium | Proposed, equations S002 |
| Fixed parameters | m_s = 365.4 kg; m_u = 43 kg; k_t = 350,000 N/m | Proposed use of sourced generic baseline S004 |
| Varied parameters | k_s = 18,000-30,000 N/m; c_s = 1,594.8-2,658.0 N s/m | Proposed +/-25% domain around 24,000 N/m and 2,126.4 N s/m |
| Road input | Raised-cosine bump, h = 50 mm, tau = 0.50 s; r = h/2*[1-cos(2*pi*t/tau)] during crossing, zero otherwise | Shape/height supported by S003; our crossing duration corresponds to 2.5 m at 18 km/h |
| Numerical solution | Adaptive RK45; 0-5 s initial observation, checked against 0-10 s and extended if necessary | P006 proposal; preserve the exit state and continuing motion after the road returns flat |
| Numerical checks | Nine pilot setups, solver/output-grid/horizon refinement and RK4 comparison; <=0.05 mm peak and <=0.01 s settling agreement; zero-input, analytical reduced-case, energy and contact checks | Planned comparisons, not achieved accuracy or certified true-error bounds |
| Dataset | Initially 225 grid training + 75 independent uniform validation + 100 independent uniform test setups | P007 starting budget; pilots reused within training only at final verified settings |
| ML comparison | Linear regression versus RBF SVR; k_s and c_s inputs, A in mm as the only target | P008 proposal; train-only scaling and development-based selection; linear model may win |
| Evaluation | Validation RMSE chooses settings; report MAE, RMSE and observed extreme errors; refit on 300 development cases and test once on 100 held-out cases | Planned, no accuracy or runtime measured |

Assumptions and limits: no tyre damping, travel stops, pitch, roll or aerodynamics; equal suspension damping coefficient in both directions; tyre contact must be checked. Sourced values describe a generic model, not the Ferrari telemetry. The 50 mm input is road height, not known suspension travel. Smaller A alone does not establish faster settling or better ride/handling. Keep peak-to-peak as lower-priority supporting detail, with no extra ML target.

Stage order after coding is authorised: establish a separate authored project area and local version-control setup while preserving course originals; implement the nominal physical case and initial checks; complete pilot refinement/contact/tail checks; only then generate the wider dataset and compare ML models. Starting with one case keeps the model understandable and exposes mistakes before they are repeated. No part of that implementation sequence has begun.

Remaining uncertainty is chiefly empirical: whether the proposed domain maintains contact, the required observation/resolution, sufficient sample count, and model accuracy/cost. These should be resolved by the planned work rather than asserted during specification. Adoption of starting settings would not convert proposals into verified facts. The deadline remains 23 October 2026 at 23:59 Sydney; presentation-date planning remains deferred.

## Confirmed by the student

- Topic area selected: suspension modelling.
- Primary output confirmed on 2026-10-02 and retained for now after comparison (D002): largest dynamic suspension movement in either direction (compression or extension), including the post-bump response. Peak-to-peak is a supporting measure; understanding motion after the bump has higher priority.
- The student stated that the topic is approved. This is recorded as user-reported approval; no separate teaching-team approval document has been inspected.
- Interests: motorsports, sim-racing, vehicle dynamics and some aerodynamics.
- Wants a moderate challenge and to learn how machine learning is used in engineering.
- Beginner with coding and GitHub; has studied numerical methods and regression methods covered by MMA3001.
- Uses a laptop and ChatGPT Plus; currently using the ChatGPT desktop app.
- Has ACC telemetry from the Ferrari 296 at Spa in MoTeC log format. Conditions and setups are reported to be similar; fuel sometimes varies. Lap count is unknown. No telemetry file has been inspected.
- The student supplied the report/repository submission deadline on 2026-10-02: Friday, 23 October 2026 at 23:59 (11:59 pm), Sydney time (Australia/Sydney). The scheduling page itself has not been inspected. Presentation-date planning is explicitly deferred at the student's request. This supersedes the earlier relative description of three weeks away.

## Proposed technical direction — not a frozen specification

Working title: Predicting peak suspension travel using a quarter-car simulation and machine learning.

Proposed research question: How do spring stiffness and damping affect peak dynamic suspension travel over one prescribed bump, and how accurately can regression predict that peak for unseen stiffness/damping combinations within the studied ranges?

A quarter-car model represents one wheel assembly and its associated share of the vehicle body. The proposed scope is a simplified passive suspension model, simulated numerically, with an ML regression model predicting a selected output from simulation inputs.

Proposals discussed include varying spring stiffness and damping while fixing masses, tyre stiffness and a defined road bump/crossing condition. The exact physical parameters, input ranges and bump remain proposals.

## Consolidated working physical specification, 2026-10-02

Status: assistant-recommended defaults for onward specification work under the student's instruction to continue. The confirmed output and interests are student decisions; the concrete physical settings remain proposals rather than source requirements or individually confirmed student choices. Avoid repeatedly reopening each value while developing the complete reviewable specification.

- Scenario: one front corner of a generic passenger vehicle, passive linear two-mass vertical model, using the coherent S004 front-corner baseline in P002.
- Fixed quantities: m_s = 365.4 kg, m_u = 43 kg, k_t = 350,000 N/m.
- Reference setup: k_s = 24,000 N/m and c_s = 2,126.4 N s/m. A baseline here means a reference physical setup; it is distinct from the later baseline ML method.
- Proposed independent input domain: k_s = 18,000-30,000 N/m and c_s = 1,594.8-2,658.0 N s/m (P003, +/-25% of each reference value). The coefficients stay constant during each run; only their selected values change between runs. This is a local study domain chosen by the assistant, not a range measured or guaranteed by S004. The eventual ML inputs would be these two coefficients.
- Fixed road: P001 raised-cosine bump, h = 0.050 m and tau = 0.50 s, interpreted as length 2.5 m crossed at constant 5 m/s (18 km/h). At t = 0 the bump begins; at 0.25 s it reaches 50 mm; at 0.50 s the road becomes flat again. The 0.50 s duration and length/speed interpretation are our design settings, not copied from S003's 0.25 s example.
- Initial state: z_s = z_u = z_s' = z_u' = 0 at t = 0, defined about each setup's own static equilibrium. Start from rest before the raised-cosine input grows.
- Output: D002's full-response max |z_s-z_u| remains primary. Carry P005 post-bump peak and +/-1 mm suspension-relative settling forward as provisional supporting diagnostics. Peak-to-peak is lower priority. No additional ML target is selected.
- Simplifications: linear effective vertical stiffness and damping, equal damper coefficient in both directions, no tyre damping, assumed tyre contact, no travel stops, pitch, roll or aerodynamic loading. Physical-domain validity still needs checking.

Beginner force interpretation (arithmetic examples, not simulated outputs): at nominal k_s, 0.010 m additional relative spring deflection produces 240 N restoring-force magnitude; at nominal c_s, 0.10 m/s relative velocity produces 212.64 N damping-force magnitude. The spring opposes deflection and the damper opposes relative motion. These concern dynamic force changes about the statically loaded equilibrium. The effective coefficients belong to the simplified vertical model and need not equal unconverted coil-spring/damper hardware settings.

Why this scope: one sourced baseline and a local two-input domain keep the study interpretable. Varying both inputs independently allows later investigation of their combined effect; P007 now proposes the sample design. Conclusions would apply to this idealised bump and vehicle baseline, not all roads/speeds or a Ferrari. No claim is made that increasing either coefficient must improve peak travel or settling. P006 proposes the numerical layer; its adequacy has not been tested.

## P006 - Proposed numerical specification, 2026-10-02

Status: recommendation for later implementation and verification, not a tested configuration or newly accepted student decision. Sources: course C001/C002 (specific cells in EVIDENCE), official SciPy documentation S007, and the governing equations S002. Exact installed package versions remain to be recorded during implementation.

Solver and state:

- Primary: SciPy solve_ivp with adaptive RK45, matching the course's vector mass-spring-damper example. It adjusts internal steps using an error estimate; it is not classical fixed-step RK4.
- State order q = [z_s, v_s, z_u, v_u], with velocities v_s = z_s' and v_u = z_u'. Let d = z_s-z_u and v_rel = v_s-v_u. Then q' = [v_s, (-k_s*d-c_s*v_rel)/m_s, v_u, (k_s*d+c_s*v_rel-k_t*(z_u-r))/m_u]. Initial state is all zeros at each setup's equilibrium.
- Initial solver settings: relative tolerance rtol = 1e-6; component absolute tolerances [1e-9 m, 1e-8 m/s, 1e-9 m, 1e-8 m/s]; maximum internal step 0.005 s. These control estimated local integration error, not guaranteed output accuracy or physical model error.
- Integrate up to the known bump exit tau = 0.50 s, then continue on flat road with the complete exit state carried forward. Do not reset the state at bump exit. Treat the boundary explicitly so no step crosses the change of road formula.
- Examine the continuous interpolated solution initially every 0.001 s, including 0, tau and T. These are observation times, not the solver's internal steps. A sampled maximum approximates the continuous maximum and requires its own refinement check.

Observation and tail:

- Initial trial interval: 0-5 s, including 4.5 s after bump exit. Five seconds is a starting choice, not a verified sufficient duration.
- On the pilot cases, compare with 0-10 s. Extend to 20 s if peaks or settling change beyond the criteria below, settling remains unresolved, or the tail remains inadequate. If still unresolved, investigate/extend or revise the specification; do not silently declare settling at the cutoff.
- Adopt one sufficiently checked observation duration across the eventual dataset. Every later run still needs tail/contact checks; nine pilots cannot establish correctness for every combination. Preserve separate validity flags for the primary peak and the settling diagnostic; do not invent missing settling times or use unresolved primary peaks as ML labels.
- Require at least 1 s observed inside the +/-1 mm band after the candidate settling entry as an initial confirmation rule. Also require agreement on extension; a quiet final second alone is not proof that no later excursion is possible.
- Proposed stronger tail check: for t >= tau, define energy H = 0.5*m_s*v_s^2 + 0.5*m_u*v_u^2 + 0.5*k_s*d^2 + 0.5*k_t*z_u^2. The equations give H' = -c_s*(v_s-v_u)^2 <= 0. Hence future |d| <= B(T) = sqrt(2*H(T)/k_s) in the exact ideal model. For nonzero bump runs, seek B(T) < min(0.0005 m, A/2, A_post/2), in addition to extension/refinement checks. This provides margin for remaining motion and protects both reported peaks; zero-road/zero-state cases must be handled separately. With approximate numerical states this is a strong consistency check, not a rigorous error-certified bound. Failure means more tail investigation, not proof the physics is wrong.

Refinement and comparison:

- Start with nine pilot setups: all combinations of minimum/reference/maximum k_s and c_s. This is a verification set, not the ML training/test split.
- First tighten RK45's relative and component absolute tolerances by a factor of 100 and halve the maximum internal step to 0.0025 s, while holding observation times fixed. Continue refinement if results do not agree.
- Separately evaluate the same tightly solved continuous trajectory on 0.001, 0.0005 and 0.00025 s grids to check missed peaks and settling crossings. Check the crossing of the settling band after the last outside-band excursion; linear crossing interpolation may be used but must pass refinement. Retain matching settled/unresolved status.
- Compare the tightly solved results with classical RK4 at fixed steps of 0.0005 and 0.00025 s on the same pilots. This uses a second taught numerical method and is a numerical cross-check, not exact truth or experimental validation. RK4 must evaluate r(t) at its intermediate stage times.
- Proposed agreement limits: full-response and post-bump peak differences <= 0.05 mm; settling-time differences <= 0.01 s with matching resolved status. If peak-to-peak is reported, also check its difference <= 0.05 mm. Apply these to solver, output-grid and horizon comparisons as appropriate. These are project-selected acceptance criteria, not published standards or guaranteed true-error bounds. The 0.05 mm allowance is twenty times smaller than the proposed 1 mm settling band; settling still needs its own check.
- Record runtime and derivative-evaluation counts for the pilot comparisons to show the accuracy/cost trade-off. These measurements are planned, not available; choose adequate settings from evidence before any performance tuning.

Complementary verification and physical checks:

- Flat road plus equilibrium initial state should remain at zero. Reject nonfinite inputs/states, invalid masses/stiffness/damping and unsuccessful/incomplete solver runs. Distinguish the positive-parameter study domain from deliberately simplified verification cases.
- Use the course's analytical unforced damped single-mass oscillator as a reduced-case solver/body-equation check; it is not an exact solution of the full quarter-car. Review force signs and state units separately, because two solvers can share the same wrong model equations.
- Extend the course's energy check to both masses and both springs: total mechanical energy should not materially increase after bump exit, allowing numerical error and checking refinement. No such monotonic-energy requirement applies while the road is supplying energy during the bump.
- Check total tyre contact force N = (m_s+m_u)*g + k_t*(r-z_u), using g = 9.81 m/s^2 as a working gravity convention. N <= 0 or a numerically ambiguous near-zero result flags the contact assumption for review; a longer simulation does not fix contact loss. Do not silently clip the tyre force or feed an invalid-contact run into the stated physical study. An adopted change to domain or contact model would require discussion and logging.

All above checks are planned only. Numerical agreement would support accurate solution of this idealised model; it would not establish real-vehicle validity. The 0.5/1/2 mm settling-band sensitivity comparison in P005 remains a separate interpretation check.

## P007 - Proposed dataset design, 2026-10-02

Status: an initial study budget and evaluation design, not a generated dataset, proven sufficient sample count or new student decision. Sources: course Week05 material and S009/S010; the exact counts, grid and seeds are project choices.

One row represents one unique (k_s, c_s) setup simulated over the full checked response. Its single ML target is A = max |z_s-z_u|, preserving D002. The thousands of time samples within a trajectory are not independent training examples. The only prediction inputs are k_s and c_s; post-bump peak, settling and other simulation-derived outputs must not become input features.

| Role | Initial count | Proposed selection |
| --- | ---: | --- |
| Training | 225 | All combinations of 15 equally spaced k_s values and 15 equally spaced c_s values, including domain endpoints |
| Validation | 75 | Independent uniform draws of each coefficient within P003; proposed sampling seed 3001 |
| Final test | 100 | A separate uniform sample from the same domain; proposed sampling seed 3002 |

- Total initial budget: 400 distinct setups. The grid contains the nine numerical pilot setups, including the nominal centre. Reuse only their final verified outputs at the adopted settings; repeated/refined runs of the same setup are not extra examples or test cases.
- The regular grid provides easily explained coverage, including corners and edges, for this two-input problem. Uniform random training is a credible alternative but can leave uneven coverage. The off-grid validation/test samples assess predictions at new combinations. These counts are a manageable starting proposal, not a published rule or evidence of adequacy.
- Before fitting, save setup IDs, exact inputs, split labels, seeds, sampling method and relevant package/configuration versions. Check for duplicate pairs across roles without inspecting test prediction errors. Do not add artificial measurement noise to this deterministic study or reshuffle seeds to obtain favourable scores.
- Uniform sampling gives equal weight per area of the coefficient rectangle, not an observed distribution of real suspension settings. It chiefly assesses interior interpolation; it does not establish accuracy at every boundary point. If explicit edge-accuracy claims are later needed, predeclare separate off-grid edge checks and report them separately.
- Numerical success, adequate primary-peak observation and contact checks from P006 apply to every row. Preserve failure records and reasons. If the proposed domain is not physically valid, review it before ML work; do not silently discard difficult cases and claim the original domain was tested. An unresolved settling diagnostic alone does not invalidate a separately resolved primary peak.
- Use validation evidence and measured simulation cost to decide whether more training setups are needed before final evaluation. No sample sufficiency or runtime is known. Keep the final-test outcomes out of these decisions. One held-out validation set is the initial bounded plan; if model rankings appear unstable, consider taught cross-validation within development data, with preprocessing inside each fold, and record any revision before opening test results.

## P008 - Proposed regression comparison and evaluation, 2026-10-02

Status: recommendation based on taught methods and official documentation S008-S011; no model has been fitted or selected by performance.

- Baseline: ordinary multiple linear regression, A_hat = b0 + b1*k_s + b2*c_s. This fits a plane and tests whether a simple relationship is already adequate. It does not require the response to be a linear function of these parameters just because the mechanical equations are linear in motion.
- Nonlinear candidate: support-vector regression with a radial-basis-function (RBF) kernel. It compares nearby scaled input combinations to fit a curved response. It is taught in Week05_3, has a manageable search at this proposed dataset size, and avoids adding a neural-network study. A decision tree is another taught option but its piecewise-constant predictions are a less natural first candidate for continuous parameter changes. This is a method-selection rationale, not evidence that SVR will outperform either method. The maximum can have corners when the controlling peak changes, so global smoothness is not assumed.
- Put feature standardisation and regression in a pipeline: learn the input means/scales from training rows only, then apply those same transformations to validation/test rows. If cross-validation is used later, fit the entire pipeline anew within each training fold.
- Preserve raw simulated A in metres; explicitly convert to millimetres for the ML target and all dimensional ML error metrics. This is only a unit conversion. Proposed SVR search: C in {1, 10, 100}, gamma in {0.1, 1, 10}, epsilon in {0.05, 0.20} mm, giving 18 candidate combinations. Values are project starting choices. C balances fitting error against regularisation; gamma sets how local the RBF influence is; epsilon is the training loss's no-penalty half-width. Epsilon is neither the ODE tolerance, the 1 mm settling band nor a guaranteed prediction-error bound. The default epsilon = 0.1 would mean 100 mm if targets were supplied in metres, so target units must be explicit.
- Primary model-selection metric: validation RMSE in mm, chosen in advance to give larger prediction errors more weight. Also inspect MAE, maximum observed absolute error, maximum observed underprediction max(0, A-A_hat), and residuals across both input ranges. R-squared is supplementary, with target range/spread reported; it is not an engineering tolerance. Avoid percentage error as the primary metric, since small denominators can dominate.
- Freeze method/settings/data budget using validation evidence; linear regression may be the preferred model. Any justified expansion of the limited SVR search must happen during development. Refit the chosen SVR settings and the declared linear comparator on the same 300 development rows (training plus validation), refitting each scaler on these 300 rows. Then evaluate both once on the same untouched 100 test setups. Declare the preferred method from development evidence; the test comparison reports how that decision held up, without further tuning on test results. Keep test labels, prediction errors and response maps out of development inspection, apart from the predefined numerical/physical validity checks. If final results disappoint, report them honestly; further development consumes that test set as development evidence and requires a fresh final evaluation for a new claim.
- Exact ties in validation RMSE favour the linear model; ties within the SVR search use ascending C, then ascending gamma, then ascending epsilon, not test performance. If improvements are negligible compared with label numerical uncertainty or validation variability, report that no meaningful superiority is established. The current 0.05 mm numerical agreement criterion is not a certified label-error bound; tighten numerical checks if ML differences approach that scale.
- Report final MAE/RMSE and largest observed test error in mm, with prediction-versus-simulation and residual plots. A finite test maximum is not a worst-case guarantee over the full domain. No universal ML pass/fail accuracy threshold is claimed: this is a comparison study against simulated references, not a safety-certified predictor. Numerical agreement, ML generalisation and real-vehicle validation are separate issues.
- Later compare simulator runtime, ML fitting/tuning cost and prediction time on the same hardware, including data-generation cost. A useful speed advantage or break-even number of predictions is an open question, not an assumed benefit of ML.

Post-bump emphasis is retained through A_post and settling diagnostics and selected trajectory comparisons, especially the nominal and nine pilot setups. These remain supporting physics analysis rather than additional prediction targets. No prediction is supported for new masses, bumps, speeds or coefficients outside the defined domain. All data generation, fitting, evaluation and plots remain future work.

## Accepted output and implementation conventions

D001 (accepted, 2026-10-02): the student selected peak movement in both directions. Define d(t) = zs(t) - zu(t), with both displacements measured upward from each configuration's static equilibrium. Positive d means extension; negative d means compression. The output is y = max over 0 <= t <= T of |d(t)|, including movement after leaving the bump. T must later be selected and checked to capture the relevant response.

D002 (accepted for now, 2026-10-02): after explicitly reopening comparison, the student said to follow the recommendation and emphasised motion after the bump over peak-to-peak travel. Retain D001's full-response maximum as the primary ML target and peak-to-peak as a supporting measure. This does not restrict the primary maximum to times after the bump or add another ML target. The final modelling specification remains open to refinement.

Calculate in metres and report travel in millimetres as a working unit convention. The output excludes static sag; it is neither peak-to-peak travel nor a measure of available clearance to a travel stop. Illustrative arithmetic only: peak compression of 32 mm and peak extension of 18 mm produce y = 32 mm, not 50 mm. These numbers are not simulation results.

Rationale: this captures the largest departure from the resting suspension position regardless of direction and matches the selected learning task. Neither smaller travel nor low ML prediction error alone establishes better grip, comfort, handling or lap time.

## Output comparison requested on 2026-10-02

Both candidate measures use the same d(t), about static equilibrium, over the same interval from initial rest through the bump and subsequent motion. Let C = -min d(t) be peak compression and E = max d(t) be peak extension. Because the interval includes initial d(0) = 0, both C and E are nonnegative.

- Maximum absolute dynamic travel A = max |d(t)| = max(C, E): the largest departure from equilibrium in either direction.
- Peak-to-peak dynamic travel P = max d(t) - min d(t) = C + E: the full observed range between greatest compression and greatest extension. It is not accumulated distance travelled, a measure of oscillation count, or necessarily a single-cycle excursion.
- A <= P <= 2*A. P equals 2*A only when the two extreme magnitudes are equal; do not assume this for a transient bump response.

Illustrative numbers only, not simulation results:

| Hypothetical setup | C (mm) | E (mm) | A (mm) | P (mm) |
| --- | ---: | ---: | ---: | ---: |
| A | 32 | 18 | 32 | 50 |
| B | 28 | 26 | 28 | 54 |

Setup B has the smaller largest departure, while setup A has the smaller total range. Neither therefore becomes the better suspension overall. Likewise, C/E = 40/10 and 25/25 mm both give P = 50 mm but have different maximum excursions and clearance demands.

Engineering interpretation: A directly answers the existing largest-departure question; P directly answers a question about the full movement range used during the event. Both lose the split between compression and extension. Neither alone establishes clearance to asymmetric travel stops: that would require separate C and E plus available compression/extension clearances at the relevant static equilibrium. Neither describes comfort, grip, accumulated travel, fatigue or settling time on its own. A constant coordinate offset cancels from P, but a changed stiffness also changes the dynamics and static clearances; offset invariance does not remove the physical role of sag.

P004 (recommendation subsequently accepted for now in D002): retain A as primary and P as a supporting result from the same eventual simulation. C and E provide the underlying compression/extension detail. Peak-to-peak has lower priority than post-bump interpretation. No additional ML model has been accepted. Relative ML accuracy and numerical adequacy remain unknown until tested.

## Post-bump emphasis, 2026-10-02

The student prioritises understanding the motion after the wheel leaves the bump. In the proposed profile this begins at t = tau, when r(t) returns to zero. The masses can still have nonzero positions/velocities, so flat road does not mean the suspension immediately stops moving. This follows from S002's dynamic equations; no response has been simulated.

P005 (supporting diagnostics proposed, not additional accepted ML targets): use the eventual d(t) time trace to interpret the post-bump response through:

- Post-bump peak A_post = max over tau <= t <= T of |d(t)|, answering how large the remaining suspension movement becomes. A_post <= A over the same adequately resolved observation. The primary target A still covers 0 <= t <= T.
- Settling time of suspension relative movement: elapsed time after tau until |d(t)| enters and stays within a chosen small absolute band epsilon for the remaining observation. The refinement below proposes epsilon = 1 mm; P006 proposes observation/tail checks. These recommendations remain untested. A zero crossing or first entry into the band is not sufficient. A truncated observation cannot establish eventual settling; classify unresolved cases rather than forcing a value. This concerns d(t), not all body/wheel motion, body acceleration or ride comfort.

These are suggestions for physical interpretation, not accepted extra ML targets or permission to begin coding. The proposed absolute threshold and P006's trial duration now have explicit rationales and checks; they are not yet adopted or demonstrated adequate. A percentage of the zero final displacement would be meaningless.

P005 refinement after the student's "ok" to continuing the settling discussion, 2026-10-02 (proposal, not an accepted numerical setting):

- Recommend an absolute band of -1 mm <= d(t) <= +1 mm (epsilon = 0.001 m), measured about static equilibrium, as an initial working tolerance for suspension-relative settling. It defines how small remaining deflection must become, not zero velocity or an entirely stationary vehicle.
- Start the settling clock when the wheel leaves the bump, at tau. The observed settling time is t_entry - tau, where t_entry >= tau is the earliest time after which the response stays inside the band through a sufficiently long remaining observation. If already inside at tau and never subsequently outside, the value is zero.
- If another excursion leaves the band, the earlier entry does not count. If the observation is too short or the tail is unresolved, report settling as unresolved within the observation rather than invent a duration. P006 now proposes horizon/tail confirmation and threshold-crossing refinement; their adequacy still needs verification.
- Illustrative arithmetic only: with bump exit at 0.50 s and sustained entry from 2.10 s, settling time after the bump would be 1.60 s. These are not simulated results.
- Rationale: the same physically interpretable tolerance can be applied to every setup. A band based on each run's own peak would allow a larger residual displacement in a run with a larger peak. A 1 mm band is a project proposal, not a measured tolerance, safety/comfort standard or the conventional 2% step-response criterion. It is small relative to the proposed 50 mm road bump, but road height and suspension travel are distinct quantities.
- Later test sensitivity to 0.5, 1 and 2 mm bands and numerical resolution; no such checks have been run. This refines a supporting diagnostic only; D002's full-response maximum remains the primary ML target.

## Technical choices still proposed

P006 recommends adaptive RK45 with classical RK4 as a numerical cross-check. P007 proposes 225 grid training cases, 75 independent validation cases and 100 independent final-test cases. P008 recommends linear regression versus RBF SVR, validation RMSE for selection and dimensional error reporting. These extend the physical/numerical proposals; none has been implemented or verified. All settings remain reviewable working proposals, with no demonstrated best model, adequate sample count or accuracy.

No Ferrari-specific calibration has been established. ACC telemetry is available background material; its use in the core model has not been decided. Agreement with simulated data must be distinguished from validation against a real vehicle.

## Sourced proposals discussed on 2026-10-02 - not accepted decisions

P001 - Single raised-cosine bump, pending student review:

- Road height r(t) = (h/2) * [1 - cos(2*pi*t/tau)] for 0 <= t <= tau, and zero otherwise. Set t = 0 at the start of the bump.
- Proposed h = 0.050 m (50 mm), tau = 0.50 s. The crest occurs at 0.25 s; flat road resumes at 0.50 s. Tau is the crossing duration, not the simulation end time T.
- One physical interpretation is length L = 2.5 m crossed at constant speed v = 5 m/s (18 km/h), giving tau = L/v. These are proposed test settings, not a measured road or a road-design standard. In this model L and v affect the excitation only through their ratio.
- S003 supports the raised-cosine shape and 50 mm height, but its own crossing lasts 0.25 s. The proposed 0.50 s is a deliberate slower excitation: for fixed height it halves peak road vertical velocity and quarters peak road vertical acceleration. This does not guarantee a smaller suspension response, because response depends on the system dynamics.
- Road height and slope meet flat ground continuously. Curvature changes abruptly at the ends; the profile is an idealisation. Compared with a step, there is no instantaneous height jump; compared with a finite half-sine bump, the entry and exit slopes are zero.
- Holding this excitation fixed isolates the effect of k_s and c_s. Conclusions would apply to this crossing condition, not all roads or speeds.

P002 - Use the front quarter-vehicle baseline from Soong, Ramli and Saifizul (2017), S004 Table 2, pending student review:

| Quantity | Proposed baseline | Intended role |
| --- | ---: | --- |
| Sprung mass m_s | 365.4 kg | Fixed body mass supported at this corner |
| Unsprung mass m_u | 43 kg | Fixed effective wheel assembly mass |
| Tyre stiffness k_t | 350,000 N/m | Fixed vertical tyre spring |
| Suspension stiffness k_s | 24,000 N/m | Reference value; later varied |
| Suspension damping c_s | 2,126.4 N s/m | Reference value; later varied |

These are one coherent published modelling set for a generic midsized passenger vehicle, with damping linearised from a nonlinear curve. They are not Ferrari/ACC parameters or experimentally validated specifications of an identified car. Use the source's front values together; its rear values form a different corner model. Interpret suspension stiffness/damping as effective vertical coefficients of the simplified model, not unconverted hardware settings.

P003 - Possible later study domain: independently vary k_s and c_s by +/-25% around P002 (18,000-30,000 N/m and 1,594.8-2,658.0 N s/m), holding masses, tyre stiffness and P001 fixed. This is an assistant-proposed local sensitivity domain, not an empirical range claimed by S004. P007 now proposes sampling within it; the domain and sample adequacy remain to be checked after the baseline is understood.

Proposed supporting assumptions: passive vertical two-mass model; linear springs; constant viscous suspension damping with the same coefficient in compression and extension; no tyre damping; continuous tyre contact; no travel stops, pitch, roll or aerodynamic loading. Start with both dynamic displacements and velocities zero, separately relative to each configuration's static equilibrium. Changing stiffness changes static sag but D001 excludes it. The source's enhanced models and tyre-damping parameter are not being adopted by selecting its linear baseline.

Later checks, not performed: numerical accuracy of the peak, enough post-bump duration T, and consistency of tyre contact. With this model's upward displacement convention and no tyre damping, the proposed contact diagnostic is N(t) = (m_s + m_u)*g + k_t*[r(t) - z_u(t)]; N <= 0 would flag failure of the assumed continuous contact. This diagnostic would not replace or add an ML target to D001. No physical travel-stop clearance has been sourced, so no claim about avoiding bottoming out is possible. P006-P008 now propose numerical checks and ML methods; their adequacy remains open.

## Assignment requirements to track

Primary authority: MMA3001_2026_Project_Brief.pdf. The checklist below is a working summary; consult the original for exact wording.

- Individual mechanical/aerospace engineering project worth 25% of the unit mark, using at least one numerical and/or ML method taught in the unit (p1, p7). Both numerical methods and ML are not compulsory; combining them is our proposed direction. Simulation projects are explicitly allowed (p3).
- Self-selected projects require coordinator discussion before commencement and teaching-team approval before substantial work (p1-2). The student has already reported approval; no renewed approval is being requested. Topic selection was due by the end of Week 5. The brief sets no formal project milestones (p2).
- Define the engineering problem, inputs/outputs, units, domains, data, assumptions, methods, implementation and limitations, including handling unsuitable inputs.
- Include verification/validation with justified metrics or acceptance criteria. Explain what it establishes, whether validation influenced model selection, and what it cannot establish (p5).
- Compare at least one credible baseline/alternative with the selected or improved solution using relevant evidence and justify the final design (p5-6). Merely naming a baseline is insufficient.
- Analyse performance and improve it where appropriate. The brief encourages profilers and timing routines, with operation-count estimates where appropriate; it does not require optimising every performance characteristic. Include sensitivity/optimisation where appropriate (p6-7).
- Written report: brief wording is "5–10 pages maximum"; references and appendices are excluded. The 10-page cap is clear; whether five pages is a strict minimum is ambiguous.
- Report content covers problem definition; inputs/outputs/data; approach; validation/results; comparison/optimisation; limitations/lessons; AI reflection; and references.
- Maintain a GitHub repository during development. Required contents include a README, HTML source documentation, a licence, functional main branch, code comments/docstrings, test functions and a test report.
- For strong assessment evidence, provide meaningful development history, clear setup/usage/dependency instructions and reproducibility (p11); keep consistent function documentation, including parameters, return values and exceptions, in sync with code and generated HTML (p12). pdoc/pytest are examples, not compulsory tools (p8).
- Submit the report and a ZIP of a repository clone through Moodle. Also provide an accessible repository link; the brief does not explicitly specify where that link must be submitted (p8).
- Presentation: five minutes plus three minutes of questions, in the Week 14 examination period. Book and attend the required presentation; marks are withheld until it is completed (p9). AI must not answer presentation questions for the student (p6).
- The presentation should explain the problem and primary inputs/outputs, demonstrate the GitHub structure and code documentation, show validation/testing evidence, justify the chosen approach, discuss principal limitations/lessons, and evaluate AI use (p9).
- Disclose all material AI assistance. The reflection must explain tools, uses, approximate contribution, why AI was used, verification, student decisions, errors/limitations and effects on learning/workflow (p6). An exact percentage is not specified.
- Assessment emphasises individual learning, organised computational work, valid evaluation, justified decisions, lessons and clear communication (p1). The brief states that the mark is based on the presentation and answers about the work (p8); it supplies no separate report/repository/presentation percentage split.
- Check the separate Unit Overview Spreadsheet/Moodle for exact dates and presentation arrangements.

## Progress and evidence status

- Project brief explained in the previous discussion.
- Topic selection completed at the broad level of suspension modelling.
- Previous review covered the markdown and code in 30 available course notebooks. They were not executed as part of that review; linked videos were not reviewed.
- Review conclusion: the taught ODE and regression methods are sufficient for the proposed narrow modelling project. Physical assumptions and suitable parameter sources still require work.
- Workflow design discussed; four setup records prepared. The student explicitly requested use of PROJECT_GUIDE.md in this conversation.
- Setup audit on 2026-10-02: read all four revision 001 records and all 15 pages of the brief; visually checked relevant pages 6, 8 and 9. Corrected conditional AI-contribution wording, strengthened comparison wording and added assessment details to revision 002. This was a document audit, not a new notebook execution or model check.
- On 2026-10-02 the student confirmed Sydney time, deferred presentation-date planning and authorised continuing. Began a plain-language model-definition discussion and inspected a university teaching source for the two-mass quarter-car model (S002 in EVIDENCE.md). Exact parameter values and final methods remain unselected.
- On 2026-10-02 the student accepted output decision D001 (both directions). Recorded the mathematical definition, sign/unit conventions and distinction from peak-to-peak travel. The next explanation develops the proposed force balances from S002; this does not select parameter values or establish a verified implementation.
- No simulation, dataset, trained ML model or project results are established by this record. Repository setup has not been verified.
- Continuation review on 2026-10-02: read PROJECT_GUIDE revision 003 and the other three records at revision 004, plus all 15 pages of the workspace brief; visually inspected existing brief renders of pp4-6. No requested file was missing. No printed brief revision/date was identified (filename identifies 2026). Separate written topic approval and course scheduling documents were not found among project files; user-reported approval/deadline remain sufficient recorded context, with presentation-date planning deferred. Reopened S002 and researched S003/S004. Saved P001-P003 as proposals only. No course notebooks or project simulations were executed and no report was drafted.
- Output comparison on 2026-10-02: read guide 003 and working records 005; checked a primary measurement reference S005 and independently reviewed the algebra and hypothetical examples. Recorded the student's request to revisit D001, the peak-to-peak alternative and P004. No new output selection, coding, simulation or report writing occurred.
- Follow-up on 2026-10-02: read state/AI log 006 and relevant evidence entries; recorded D002 retaining the recommended primary/supporting measures for now with post-bump emphasis. Revisited S002 and proposed P005 for discussion. No simulation, coding, report writing or empirical verification performed.
- Settling-definition follow-up on 2026-10-02: read relevant revision 007 records; interpreted "ok" as agreement to continue the explanation, not acceptance of a numerical setting not yet presented. Checked S006 and proposed a 1 mm absolute band with an illustrative timing example and later sensitivity checks. No numerical experiments or new implementation performed.
- Physical-specification consolidation on 2026-10-02: read state 008 and relevant source/log entries; rechecked S003 bump and S004 table provenance. Consolidated P001-P003/P005 as provisional working settings, explained constant coefficients within runs, and checked the simple force arithmetic with independent assistant review. No new student-specific numerical acceptance, simulation, coding or report writing claimed.
- Numerical-specification discussion on 2026-10-02: read guide 003, state 009 and relevant evidence/log entries; reread selected cells of Week07_4 and Week07_5 without execution and checked official SciPy documentation. Proposed P006 with RK45, a trial five-second window, explicit refinement/extension checks and complementary physical tests. Independently reviewed the two-mass energy derivation and tail bound. No proposed check has been run and no project code or report created.
- Dataset/ML-specification discussion on 2026-10-02: read guide 003 and records 010; audited relevant Week05 notebooks without executing them and checked official scikit-learn documentation. Proposed P007/P008 with 400 distinct setups, a grid/off-grid evaluation design, linear/SVR comparison, training-only scaling and explicit target units. Independently reviewed split roles, pilot reuse and metric interpretation. No data pairs, simulations, models, plots or assessed report were generated.
- Complete-specification review on 2026-10-02: read guide 003 and records 011, checked availability of the brief and used its existing requirements audit. Independent assistant reviews found no material physical/numerical/ML conflict. Consolidated the existing choices and corrected stale P005 wording that predated the later proposals. Preserved the coding boundary and identified one nominal simulation plus initial checks as the first stage after authorisation. No implementation or experiment begun.
- Handoff preparation on 2026-10-04: read guide 003 and records 012, verified brief availability, and prepared HANDOFF revision 001 with current context, next-stage completion criteria and an optional user-sent coding-authorisation sentence. Advice to use a new chat for the implementation stage was informed by official OpenAI guidance; this is an organisational recommendation. No new chat, implementation, experiment or report was created.

## Current setup files

- PROJECT_GUIDE.md — revision 003: working instructions and opening prompt.
- PROJECT_STATE.md — revision 016: nominal, verification and dataset checkpoints, decisions, historical specification and next actions.
- EVIDENCE.md — revision 016: source index, course references, numerical verification and dataset evidence.
- AI_USE_LOG.md — revision 016: implementation, dataset/checking assistance and outstanding student contribution review.
- HANDOFF.md — revision 001: new-chat reading instructions, scope, completion criteria and copyable prompt; does not grant coding permission.

These local files are in Project_Setup under the existing MMA3001 notebook folder. Uploaded copies must be refreshed when their authoritative local versions change.

## Open questions

1. All 400 sampled setups pass the adopted per-row checks; exact label error and contact between sampled times are not certified. Further sampled setups still need their own checks.
2. Will P003 maintain tyre contact throughout the continuous domain, and will P007's 400 setups be sufficient for ML? These remain open despite the completed dataset screening.
3. Will P008's RBF SVR improve accuracy or speed enough to justify its cost relative to linear regression/direct simulation? No ML evidence exists.
4. Can the student explain the state, force signs, equilibrium convention, full-response maximum, settling rule and checks independently? Understanding and the overall AI contribution estimate remain to be reviewed.
5. Licence choice, student Git identity and GitHub publication remain future repository work; no remote has been created.

## Next three actions

1. Review the dataset guide and results with the student: one row versus time samples, features versus diagnostics, and training/validation/test roles. Student-independent reproduction and understanding remain unassessed.
2. The next implementation stage, when requested, is P008's linear-regression/RBF-SVR development comparison using training and validation only. Fit scaling only within the training workflow and preserve the reserved final test until choices are fixed; keep post-bump interpretation alongside the primary-target comparison.
3. Arrange student Git identity, licence and GitHub publication as separate repository work when requested; continue source/decision/AI records. ML fitting, assessed report writing and presentation-date planning were outside this completed dataset stage.
