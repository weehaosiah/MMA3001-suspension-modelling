# Student report review notes

Updated: 25 October 2026 | Status: R1-R7 incorporated; final reading remains

## Latest revision: contribution, oversight and responsibility

The student supplied their name/student ID and asked that the narrative show
their responsibility for conclusions and decisions through judgement. The
identity is entered and no report review marker remains. Section 9 was revised
using Responsible Use of AI cells4-6 and brief pages6/15: student purpose,
primary output, post-bump priorities and scope now lead the account.

Oversight is illustrated by the recorded physics/numerical/data-role discussion,
reconsideration of stiffness against competing metrics and fixed-bump limits.
The student accepts responsibility for the submitted conclusions and decisions.
Substantial AI implementation, checks and drafting remain clearly attributed;
the narrative does not invent independent manual verification or mastery.
The revised prose is AI-authored from student input and is for final reading.

The report remains nine main pages plus references. All ten pages pass visual
review; scientific equations/tables are unchanged. E9 points to records046.
No new scientific execution, upload or submission occurred. Older R-status
statements below are historical and superseded by this current checkpoint.

Latest provenance clarification: the student reports using Claude to cross-check
all physics-related walkthrough questions. The responses recorded below remain
evidence of an AI-assisted learning/review process, not an unaided assessment
or independent manual verification. No Claude transcripts or exact model/session
details were inspected.

## R3 responses and completed clarification

After the assistant's explanation, the student supplied these responses:

1. Correctly used Hooke's law for the body's dynamic spring contribution,
   -ks(zs-zu), with relative displacement0.01m and upward positive. Identified
   downward force and zero damping force when body/wheel velocities are equal.
   At the recorded nominal stiffness this contribution is-240N; this numerical
   substitution is explanatory arithmetic, not a new simulation.
2. Correctly explained that gravity is accounted for in static equilibrium and
   spring preload. Subtracting the equilibrium force balance cancels constant
   terms, leaving the forces associated with departures from that equilibrium.
   The student described adding gravity again to the already-subtracted equations
   as double counting. This is correct for the adopted coordinate formulation.
3. Offered the general argument that a new bump height might be acceptable inside
   the training/validation range and unreliable outside it. The caution about
   unfamiliar conditions is sound, but this dataset has no varied height range:
   every setup uses height0.050m and duration0.50s, with only ks/cs as ML inputs.

Assistant clarification: identical ks/cs inputs give the same model prediction
even if someone intends a different bump. The current model cannot represent
that change. Existing evidence does not establish validity at another height;
any adaptation needs a separately justified and checked method. No expansion of
the dataset, model or project scope is proposed.

The student then correctly restated the limitation:

> No, because bump height is not an input to our model, changing it while keeping stiffness and damping the same produces the original 50 mm bump prediction, which cannot be assumed valid for the new bump without separate adaptation and validation.

Incorporated the student's force/equilibrium reasoning and corrected ML-input
distinction into Section2 of the report. Removed the R3 prompt and changed the
review-table range to R4-R6. R1 and R4-R7 remain. The concise report wording is
AI-edited from the student's responses after teaching; it does not establish
unassisted understanding of the entire project.

Read the unchanged rhs, ML guide and actual generation/frozen-plan metadata;
independent static review confirmed the distinctions. This records specific
reasoning after teaching, not whole-project mastery. After the corrected answer,
the DOCX was edited and rendered read-only in Word. All ten pages were inspected;
the report remains nine main pages plus references. No scientific run, model call,
test or upload occurred.

## R4 response and energy clarification

The student supplied the following answer after the preceding explanation:

> **1. Sampling at 0.25 ms instead of 1 ms.** Finer sampling reduces observation error: with coarse spacing the true maximum can fall between samples, and a brief excursion outside the settling band can begin and end between samples, so the reported peak is biased low and the settling time biased early. It does not, however, test the numerical solution itself, because the underlying trajectory is unchanged and only its read-out is denser. If integration error has distorted the amplitude, phase, or effective damping, finer sampling merely resolves the erroneous solution more accurately. Establishing solver accuracy requires recomputing with tighter tolerances or smaller steps and confirming that the trajectory and the derived peak and settling metrics are insensitive to these changes.
>
> **2. Near-zero displacement with large velocity at termination.** Settling requires |z(t)| to remain within the band for all t >= t_s, not merely at t_end, and near-zero displacement with large velocity indicates passage through equilibrium rather than rest: the state (z, zdot) is far from the phase-space origin, so a later excursion beyond the band is possible. A longer simulation tests this directly by showing whether the response re-exits the band after t_end and whether the reported peak or settling time changes. The remaining-energy bound provides a guarantee beyond the simulated interval: with E = 0.5*m*zdot^2 + 0.5*k*z^2 for the relative motion and dissipative damping, E is non-increasing, and since 0.5*k*z^2 <= E, it follows that |z(t)| <= sqrt(2*E(t_end)/k) for all t >= t_end. If this bound lies within the settling band, no later excursion can occur and settling is justified. Because E depends on both z and zdot, the bound correctly rejects the large-velocity case, and it remains valid even though z itself is non-monotone, since E decreases monotonically while z oscillates.

Mathematical symbols in the second quoted paragraph are transcribed in ASCII;
the substantive wording is retained. The student correctly distinguishes
observation refinement from integration refinement, explains the risk at a zero
crossing with substantial velocity, and identifies the roles of a longer run and
an energy bound. Agreement under refinement supports numerical accuracy rather
than proving exact accuracy. A missed excursion can make settling appear early;
coarse-grid/interpolated settling error is not invariably in that direction.

Assistant correction: write d = zs - zu and use the entire quarter-car energy
after the road returns to zero:
H = (ms*vs^2 + mu*vu^2 + ks*d^2 + kt*zu^2)/2.
The proposed single-relative-coordinate energy omits the full two-mass kinetic
energy and tyre spring energy, and is not generally non-increasing in this
coupled model. The full energy obeys Hdot = -cs*(vs-vu)^2 <= 0. Consequently
|d(t)| <= sqrt(2*H(T)/ks) for t >= T in the exact flat-road model. Applied to
computed states, this is supporting numerical evidence, not a certified bound
on numerical error or real-vehicle validation. The project also checks observed
band residence, solver/grid/horizon agreement and a stricter tail margin.

A bound inside the band is sufficient to rule out a later crossing for the exact
model; a bound outside the band is inconclusive, not proof of a later crossing.
Large velocity can raise the bound enough to prevent acceptance, but the word
"large" alone does not establish that a particular threshold is exceeded.

The student then supplied this corrected restatement:

> We use the full quarter-car energy H = ½m_s v_s² + ½m_u v_u² + ½k_s d² + ½k_t z_u², with d = z_s − z_u, which includes both masses' kinetic energy, the suspension spring energy and the tyre spring energy. On flat road Ḣ = −c_s(v_s − v_u)² ≤ 0, so for the exact model |d(t)| ≤ √(2H(T)/k_s) for all t ≥ T. If this bound lies inside the settling band, no later excursion of the suspension deflection is possible, but because H is evaluated from computed states with unbounded numerical error, it supports the settling result only together with the refinement and longer-run checks and is not a certified guarantee. A bound above the band is merely inconclusive, not evidence that another excursion will occur.

This correctly resolves the full-system-energy and guarantee distinctions after
teaching. AI refined "unbounded numerical error" to "numerical state error has
not been rigorously bounded": the project lacks a certified bound, rather than
establishing that errors grow without limit. No additional approval was needed
for this wording clarification within the already authorised report review.

Incorporated the student's sampling/solver/horizon reasoning and corrected
energy explanation into Section 3, removed R4 and narrowed the review-table
range to R5-R6. Condensed repeated diagnostic prose and set Section 3 paragraph
spacing to 4 pt after, retaining font sizes and margins. The numerical result
table and three native equations are unchanged. The edited report renders as
ten pages, nine main pages plus references. These are AI-edited explanations
based on responses after teaching, not evidence of an unassisted derivation or
whole-project mastery. No new simulation or scientific test was performed.

## R5 completed data-role explanation

The next discussion distinguishes 225 training rows, 75 validation rows used
for selecting candidates, and 100 reserved test rows. Each candidate scaler
learned its mean and standard deviation only from the 225 training inputs;
validation inputs used that same learned transformation. After selection was
frozen, each final model and scaler were fitted on the 300 original development
rows, with the 100 test rows still excluded. That test has now been consumed;
it must not become a tuning source. Refined validation labels were numerical
references and were not substituted into final fitting.

This teaching was based on the unchanged report, ML guides and fitting code.
The student then supplied these responses:

> **1. Scaler during candidate selection.** Only the 225 training rows determine the mean and standard deviation of each input (stiffness and damping), and these statistics are fitted afresh for each candidate model. The 75 validation rows are transformed with those same training-derived statistics, x' = (x − μ_train)/σ_train, and are never used to compute or update μ or σ. Fitting a separate scaler on the validation rows would map the same physical stiffness or damping value to a different scaled number than the model saw during training, so the validation error would no longer measure how the fitted model performs on new setups. It would also let information from the validation inputs influence the preprocessing.
>
> **2. Final fit on 300 rows versus tuning on test results.** Fitting the final models and fresh scalers on the 300 development rows was acceptable because the settings were already frozen, so no choice was made using the test rows, and more training data generally improves the fit without altering the selection procedure. The 100 test rows stayed excluded from fitting, scaling and selection, which keeps the test error an unbiased estimate of performance on unseen setups. If the test results were used to choose new settings, the test rows would become part of the selection process: the reported error would be optimistically biased, because the chosen settings would partly reflect noise specific to those 100 rows, and no untouched data would remain to check the revised choice. The final test is therefore a one-time assessment, and any further adjustment would need a new, untouched evaluation set.

The core reasoning matches the implementation: a fresh scaler in each candidate
pipeline is fitted on the same 225 inputs, so its learned statistics are the
same for this common training set; validation only uses the learned transform.
After choices were frozen, both final pipelines and scalers used the same 300
original development rows, with the test excluded throughout fitting/selection.

AI qualifications: more fitting data does not guarantee better prediction
accuracy. The independent test gives an assessment under the recorded sampling
design, with finite sample uncertainty; independence alone does not make every
reported metric statistically unbiased (in particular RMSE). Test-driven
selection risks optimism by adapting to sample-specific errors even though the
physical response labels are deterministic. These qualifiers do not change the
existing fitting or evaluation procedure.

Incorporated the student's explanation with those qualifications in Sections
4-5, removed R5 and changed its review-table row to R6. Preserved the distinction
between original fitting labels and refined validation references. A two-line
overflow in the first render was corrected by setting Section 5 paragraph
spacing after to 4 pt; fonts, margins, figures and scientific tables were not
changed. Final rendering has nine main pages plus one reference page.

The report wording is AI-refined from responses after teaching. No broad claim
of independent mastery, new model fit, prediction or test evaluation is made.

## R6 completed engineering judgement

The saved comparison at nominal damping contrasts stiffness 24,000 and
30,000 N/m. Increasing stiffness lowers the post-bump peak from 31.891621 to
28.673449 mm, but increases the full-response peak from 40.571155 to
40.848021 mm and settling after exit from 1.269332 to 1.445348 s. These specific
cases do not establish a universal stiffness rule or real-car optimum.

The student supplied the following response:

> **1. Expectation versus result.** I would have expected the stiffer suspension to reduce suspension deflection and body motion in general, so the smaller post-bump peak (28.673 mm versus 31.892 mm) is consistent with that. The larger full-response peak (40.848 mm versus 40.571 mm) and longer settling (1.445 s versus 1.269 s) did not fit the simple picture, so the comparison partly confirmed and partly refined my expectation. A plausible reading is that raising k_s at fixed c_s lowers the damping ratio, so the response is less well damped and rings longer, while the stiffer spring transmits more force to the body. This is a hypothesis consistent with the numbers, not something these two cases demonstrate. The primary-peak difference is also small (0.277 mm, under 1%), so I would not interpret its direction until it is shown to exceed numerical and sampling error. For judging "better", the metrics measure different things and trade off, so no single stiffness is better without a stated criterion, such as the weighting of peak versus settling time and the relevant input profile. Two stiffness values at one damping and one excitation cannot establish a universal rule, since the ranking could change with damping, bump geometry or speed, or the chosen performance measure.
>
> **2. Defensibility of a five-second run.** Exact stopping is not required for the reported quantities to be correct. What is required is that the peaks and the settling time are determined before the end of the run and cannot change afterwards. The longer-run comparison tests this empirically: if extending the simulation leaves the peak and settling time unchanged, the five-second window has captured them. The remaining-energy bound addresses the time beyond the window. With H(T) evaluated at the end and Ḣ = −c_s(v_s − v_u)² ≤ 0 on flat road, |d(t)| ≤ √(2H(T)/k_s) for t ≥ T in the exact model, so if that bound lies inside the settling band, no later excursion of the suspension deflection is possible. Neither check establishes more than that. The longer run only covers the extended horizon it actually simulated. The bound covers the suspension deflection d, not every quantity of interest (body displacement, for instance, would need its own bound), and it is inconclusive if it exceeds the band. Both are evaluated from computed states whose numerical error has not been rigorously bounded, so they support the settling result alongside the refinement checks but do not certify it, and neither applies if the road input is not flat after the bump.

This supplies a personal expectation and explains how the comparison refined
it, rather than attributing an invented lesson to the student. The judgement
that metrics require stated priorities and do not establish a universal rule
is sound. The full-response primary target remains unchanged; no new weighted
objective or road-speed study is introduced.

AI checked and clarified three points before editing:

- Both stiffness values at nominal damping are verified pilots. The observed
  baseline-to-tight-reference A differences are about 0.000000106 mm and
  0.000110198 mm, far below the approximately 0.276867 mm increase. The refined
  pair also increases (approximately 0.276977 mm). The saved checks therefore
  already support its direction for these cases; they do not provide certified
  error bars, engineering significance or a universal trend.
- A is relative suspension travel, not body motion alone. A single oscillator's
  damping ratio decreases as stiffness increases at fixed mass/damping, but
  its underdamped exponential decay rate remains c/(2m). Lower ratio alone
  cannot establish a longer decay time. The coupled quarter-car requires
  separate response/modal analysis to establish the proposed mechanism; none
  was performed. A stiffer spring gives greater force at the same deflection,
  but the response deflection itself changes. The report leaves causation
  unestablished instead of adopting that mechanism.
- Agreement through ten seconds supplies numerical evidence over that horizon,
  not proof about all later times. The remaining relative-displacement bound
  protects settling only when below the band; preserving the peaks also needs
  it below the already recorded peaks. The implementation uses the stricter
  min(0.5 mm, A/2, A_post/2) tail limit plus the selected band. Flat-road energy
  decay does not apply during new forcing, though longer simulation can still
  be used to investigate a specified forced response.

Sources reread: PHYSICS_REVIEW, verification_results/summary.json,
quarter_car.py and Week07_5_Higher_Order_ODEs cells 17 and 19 (one-based JSON
positions). The course single-oscillator formula was used only to explain the
limitation, not to replace the quarter-car or run a new analysis. Independent
static review agreed. No notebook cells or scientific calculations were rerun;
comparisons above are read from or calculated from saved results.

Inserted the AI-refined personal interpretation in Section 6 and expanded the
existing finite-horizon discussion in Section 8. Removed R6 from the prompt and
review table. The report retains nine main pages plus references; all ten pages
pass visual review, with scientific tables and native equations preserved.
The original response and AI corrections are distinguished here; the revised
wording does not assert that the student independently derived the corrections.

## R7 personal reflection and R1 identity next

The student requested additional points and refinements for all five reflection
answers, explicitly asking for a cross-check against Responsible Use of AI.
They confirmed ChatGPT as the main tool and Claude for verification/cross-checks,
and asked AI to reconstruct contributions, personal physics checks and retained
decisions. They invited emphasis on human oversight, including exaggeration.
No unsupported exaggeration was added; actual decisions and explained examples
provide the basis of the stronger wording.

Their supplied learning account describes faster brainstorming/background
summaries/drafts, AI tutoring, restating ideas, improved explanation of concepts,
remaining dependence on notes for technical details, concern about overreliance,
responsibility and transparency. It also makes broad claims about explaining
without notes, personally verifying facts/citations, reviewing every output,
avoiding all sensitive inputs and attempting problems before using AI. The
current record supports specific guided explanations, rather than independent
confirmation of all these broader activities.

Created [AI_REFLECTION_REVIEW.md](AI_REFLECTION_REVIEW.md) containing the source
cross-check, a proposed first-person reflection, a qualitative contribution
table and explicit provenance/remaining factual gaps. It distinguishes AI-led
code/tests/source audits from student reasoning and actual topic/output/licence
choices and GitHub actions. Known AI-caught errors are not attributed to the
student. The reflection recognises substantial AI authorship and explains that
another AI response is not independent physical validation.

Read all14 cells of the Responsible Use of AI notebook and brief pages6/15;
the brief hash matches the recorded original. Notebook cells4-6 ask for
acknowledgement, tools/known versions/dates/iterations, actual oversight and
verification. Cells8/11/13 discuss privacy and ownership; provider policies and
the linked video were not freshly reviewed. The brief requires approximate
contribution, but no exact percentage. Unknown versions and Claude details
remain unknown.

The student answered the factual question: "all the physics related questions.
allow yourself to find wherever most suitable and use it there". This confirms
the reported scope of Claude's supplementary checking and authorises placing
that information in the reflection. It does not confirm independent personal
source checks, calculations or code execution outside the chat. The report
therefore retains conservative attribution without another approval request.

Incorporated a condensed reflection in Section 9, including ChatGPT/Codex and
Claude roles, substantial AI implementation/checking/drafting, actual student
decisions and guided reasoning, recorded corrections, learning limits and
responsibility. Removed R7 and updated R1 to request identity and final review.
The administrative checklist and deadline note were removed from the report
after they spilled across a page; all those tasks and the deadline remain in
SUBMISSION_CHECKLIST and README. Updated E9 to records045. The final report is
nine main pages plus references, with all scientific tables/equations intact.
The student can enter R1 name/student ID directly into the DOCX. Access, final
upload, fresh clone ZIP and Moodle submission still require completion.

These notes distinguish the student's supplied ideas from AI-refined wording and
optional extrapolations. The approved R2 wording is now in the editable report.
Do not treat a proposed motivation, learning outcome or personal reflection as
approved simply because it appears here.

## R2: motivation

Student's supplied words:

> Personal interest: My passion for motorsports, sim racing, and car/vehicle dynamics. I seek to understand suspension behavior.
> learning aspect: learning about the future of AI and ML. learning about numerical methods of representing a dynamic mechanical system through physics and PINNs.

The student explicitly invited extra points/extrapolations, then replied
"agreed, add points 1 and 2". The wording below incorporates that selection.
Point3 remains unselected. The student approved the motivation; AI refined and
integrated the wording.

### Approved wording inserted into the report

I chose suspension modelling because of my passion for motorsport, sim racing and
vehicle dynamics. I wanted to understand how spring stiffness and damping affect
suspension movement, and why limiting peak displacement does not necessarily
mean the oscillations settle more quickly.

A second motivation was to learn how numerical methods represent a dynamic
mechanical system. A simplified quarter-car model allows me to examine stiffness
and damping under controlled conditions while learning how modelling assumptions
limit the conclusions. It also provides a manageable example of translating
equations of motion into a simulation and interpreting the resulting response.

I am also interested in the future role of AI and machine learning in engineering.
Working with simulation-generated data provides an opportunity to explore how an
ML model can approximate a defined output from the simulation. My broader learning
interests include physics-informed neural networks (PINNs), which I see as a
possible direction for further study beyond the methods used here.

### Addition history

1. Connecting settings to motion: "I wanted to understand how spring stiffness
   and damping affect suspension movement, and why limiting peak displacement
   does not necessarily mean the oscillations settle more quickly."
2. Justifying the restricted model: "A simplified quarter-car model allows me
   to examine stiffness and damping under controlled conditions while learning
   how modelling assumptions limit the conclusions."
3. Comparing methods: "I wanted to explore the trade-off between prediction
   accuracy and computational cost when an ML model approximates the output of
   a physics-based simulation."

The student accepted points1 and2. They connect the personal interest to the
specific engineering question and explain why the restricted scope is useful.
Point3 was not selected and was not added as a separate aim.

### Scope check

Existing methods are RK45 simulation, linear regression and RBF support vector
regression. No PINN was implemented. PINNs are recorded as the student's future
learning interest, not a new method commitment or a completed learning result.
Motorsport/sim racing motivate the topic; no lap-time, grip, comfort or actual-car
performance improvement is established by this simplified simulation study.

The initial suggestion used guide003/records035, the R2 prompt and ML_GUIDE.
After approval, read records036 and edited the existing DOCX in place. Removed
the R2 prompt, updated the review table and corrected the stale deadline to the
already confirmed extension. Condensed repeated introductory wording and adjusted
first-page spacing to retain nine main pages plus one reference page. Independent
content and visual reviews checked the result. No scientific experiment, model
change, commit/push or submission occurred. The adopted output and consumed test
remain unchanged.
