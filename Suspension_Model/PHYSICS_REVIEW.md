# Reading the suspension results

Saved-data review, 5 October 2026. This is a learning note, not assessed report prose. It uses existing simulations and the frozen final evaluation; no new physical runs, fitting or benchmark were performed.

## Three questions about one response

| Measure | Question it answers | Refined nominal result |
|---|---|---:|
| Full-response A | How far does the suspension depart from static equilibrium at its largest excursion, in either direction? | 40.571155 mm at 0.442 s |
| Post-bump A_post | What is the largest remaining relative movement from bump exit onward, including the exit instant? | 31.891620 mm at 0.500 s |
| Relative settling | How long after exit until displacement stays within the selected +/-1 mm band, under the recorded checks? | 1.269332 s after exit |

The primary target remains A = max abs(zs-zu) across the entire response. The other two measures explain behaviour that one peak cannot describe. The road is flat from 0.500 s, so nominal sustained entry is at 1.769332 s measured from the start. All positions are relative to the statically loaded equilibrium; static sag is excluded.

At exit, the springs still store energy and both masses still have velocity. The code therefore carries all four state values `[zs, vs, zu, vu]` onward. Setting them to zero at exit would erase the motion we want to understand. The saved refined trace later reaches about -20.427 mm in compression at 0.77075 s; a zero crossing is not the end of the response.

On flat road the exact model obeys

\[
H=\tfrac12m_sv_s^2+\tfrac12m_uv_u^2+\tfrac12k_s(z_s-z_u)^2+\tfrac12k_tz_u^2,
\qquad \dot H=-c_s(v_s-v_u)^2\leq0.
\]

Here H is the kinetic plus elastic energy relative to equilibrium. The damper removes energy while it opposes relative velocity. Total energy can fall while displacement continues to oscillate: energy transfers between spring deformation and mass motion. This explains why another excursion outside the settling band can follow an earlier zero crossing. The numerical energy/tail checks support the computed response; the formula alone does not certify numerical accuracy or contact at every instant.

## A smaller post-bump peak can still take longer to settle

These three saved baseline dataset rows hold damping at 2126.4 N s/m:

| Stiffness [N/m] | Full A [mm] | A_post [mm] | Settling after exit [s] |
|---:|---:|---:|---:|
| 18000 | 39.343201 | 33.663539 | 1.376665 |
| 24000 | 40.571155 | 31.891621 | 1.269332 |
| 30000 | 40.848021 | 28.673449 | 1.445348 |

Going from 24000 to 30000 N/m reduces the post-bump maximum but increases both the full-response maximum and settling time. Stiffness changes the response frequencies and the timing of excursions as well as the spring force. The last excursion outside a fixed band determines settling, so peak height alone cannot rank it. This is a clear sampled example, not a claim that increasing stiffness always has these effects.

The nominal table above uses the refined 10 s / 0.25 ms result. This comparison uses the preserved 5 s / 1 ms dataset labels. Their tiny differences are expected numerical-reference differences; they are not conflicting output definitions.

## What the existing 225-point grid shows

The [training physics maps](ml_development_v1/training_physics.png) show these saved samples. Colours between points are interpolated for display; they are not extra simulations.

- All 225 full peaks are positive extension before exit. All 225 post-bump maxima occur exactly at the inclusive exit boundary. Thus A_post here includes displacement already present when the road becomes flat; it is not specifically the largest later rebound.
- At each fixed stiffness, every one of 210 adjacent increases in damping reduces A, A_post and the recorded settling time. This is evidence within this grid and fixed bump, not a general rule for arbitrary damping or roads.
- At fixed damping, all 210 adjacent stiffness increases reduce A_post. Full A increases in 197 pairs and decreases in 13; settling increases in 32 pairs and decreases in 178. The small A downturns are at most about 0.02535 mm, below the adopted 0.05 mm numerical agreement criterion and without individual refinement at every row; do not overinterpret those details.
- The sampled minimum A is at ks=18000, cs=2658 (35.442282 mm). The minimum A_post is at ks=30000, cs=2658 (24.324843 mm). The shortest recorded settling is at ks=24000, cs=2658 (0.889807 s). These are different sample locations, illustrating different questions. They are not continuous-domain optima or recommendations for a real vehicle.

The +/-1 mm band is a project definition, not a safety or comfort standard. Nominal settling changes to approximately 1.644586 s with a +/-0.5 mm band and 1.174273 s with a +/-2 mm band. This sensitivity was already checked in the nine-pilot stage. Settling of zs-zu does not say that both masses, body acceleration or every aspect of the vehicle have settled.

## What the ML result adds

The frozen SVR predicts A from stiffness and damping. On the 100 final cases its RMSE is 0.029796 mm, versus 0.199436 mm for linear regression. It approximates the numerical input-to-peak relationship well on this test sample. It does not predict the trajectory, A_post, settling, comfort, contact margin or physical travel clearance.

A linear force law still permits a curved relationship between coefficients and the maximum of a time response. This makes a curved regressor plausible, while the actual final comparison supplies the evidence for this sample. Good peak prediction does not replace the physical checks. The final test remains consumed, and none of this interpretation changes the model choice or settings.

## Reproduce and review

The small [saved-result reader](interpretation_v1/review_saved.py), with [function documentation](interpretation_v1/review_saved.html), reads existing JSON/CSV files, checks their identities and units, and recomputes the grid comparisons. It contains no solver or model-fitting/prediction call. Its [saved facts](interpretation_v1/review.json) include six passing data checks and source fingerprints.

From the Suspension_Model folder:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' interpretation_v1/review_saved.py
```

This verifies the saved facts without changing them. The final-evaluation audit remains `python final_evaluation.py audit` using the same recorded interpreter. The existing 385-test result belongs to that checkpoint; it was not presented as a newly run test suite for this documentation review.

For your own explanation, practise describing why velocity survives bump exit, why the final band entry differs from the first zero crossing, and why a lower post-bump peak can accompany longer settling. Reading this note does not establish that you can yet explain those points independently.

Sources: `results/summary.json` (final refined nominal); `results/nominal_trace_0p25ms.npz`; `verification_results/summary.json` (nominal band sensitivity and pilot checks); `dataset_v1/train_diagnostics.jsonl` (225 baseline rows); `final_evaluation_v1/summary.json`; the existing force/energy implementation in `quarter_car.py`. Material AI assistance and review are recorded in Project_Setup revision 019. See [the proposed runtime plan](RUNTIME_PLAN.md) for the next bounded experiment.
