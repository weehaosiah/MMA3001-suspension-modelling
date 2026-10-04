# Nine-pilot verification checkpoint

Technical check record, not the assessed report. Regenerate with `python run_verification.py`.

Overall: **PASS**. Common trial duration: 5 s, checked against 10 s.

## Measured reference results

Reference values use tight RK45, 0.25 ms observations and the longer horizon. Exit at 0.50 s is included in A_post.

| Setup | ks [N/m] | cs [N s/m] | A [mm] | A_post [mm] | Settling after exit [s] | Min tyre force [N] | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| kL_cL | 18000 | 1594.8 | 44.093828 | 39.623735 | 1.873319 | 2922.138 | PASS |
| kL_cN | 18000 | 2126.4 | 39.343321 | 33.663538 | 1.376666 | 2831.415 | PASS |
| kL_cH | 18000 | 2658.0 | 35.442747 | 28.785418 | 1.004290 | 2744.095 | PASS |
| kN_cL | 24000 | 1594.8 | 45.491905 | 37.808798 | 1.987777 | 2670.127 | PASS |
| kN_cN | 24000 | 2126.4 | 40.571155 | 31.891620 | 1.269332 | 2626.596 | PASS |
| kN_cH | 24000 | 2658.0 | 36.522937 | 27.115903 | 0.889807 | 2574.116 | PASS |
| kH_cL | 30000 | 1594.8 | 45.685298 | 34.092912 | 1.841485 | 2418.829 | PASS |
| kH_cN | 30000 | 2126.4 | 40.848131 | 28.673449 | 1.445349 | 2417.877 | PASS |
| kH_cH | 30000 | 2658.0 | 36.841515 | 24.324843 | 1.095702 | 2398.783 | PASS |

L/N/H denote low/nominal/high; k is stiffness and c is damping. No interpolation over unsampled setups is claimed.

## Largest observed comparison differences

Limits: both peaks <=0.05 mm; settling <=0.01 s with matching resolved candidates.

| Comparison | max ΔA [mm] | max ΔA_post [mm] | max Δsettling, all bands [s] |
|---|---:|---:|---:|
| solver | 5.75289982e-07 | 7.47171516e-07 | 2.576654445363147e-10 |
| grid_1_to_0p5ms | 0.000464872857 | 0 | 7.839202305071069e-06 |
| grid_0p5_to_0p25ms | 0.000182127832 | 0 | 2.5852565146422535e-06 |
| horizon | 0 | 0 | 0.0 |
| rk4_coarse_vs_rk45 | 2.24514157e-08 | 1.57725152e-08 | 8.226064274197142e-11 |
| rk4_fine_vs_rk45 | 1.28042854e-08 | 6.00107811e-09 | 8.986589250525867e-12 |
| rk4_step_halving | 0.000182112883 | 2.12274504e-08 | 2.5851710789837057e-06 |
| selected_vs_reference | 0.000464923531 | 7.47171516e-07 | 8.862959230526712e-06 |

## Complementary checks

- Unit-test suite: **PASS**; exact output in `unit_tests.txt`.
- Analytical clamped-wheel body diagnostic: **PASS**. Details and exact errors are in `summary.json` under `reduced_case`.
- Tyre contact, post-bump energy, tail bound and full state continuity were checked separately for each pilot and solver run.
- The reduced diagnostic holds the wheel at zero and checks the existing body-force implementation against a known formula. It is not an exact solution of the two-mass model.
- RK4 and RK45 share the physical force function; agreement cannot rule out a shared modelling error.
- RK4 step halving changes both integration and observation spacing. Its peak difference must not be treated as a pure integration-error estimate; the same-grid RK4/RK45 comparisons separate this effect.
- Reduced-case maximum position discrepancy: 3.8007097469261453e-13 m (limit 1e-07 m).
- Reduced-case maximum velocity discrepancy: 3.050535518633879e-12 m/s (limit 1e-06 m/s).

## Settling-band sensitivity

| Setup | ±0.5 mm [s] | ±1 mm [s] | ±2 mm [s] |
|---|---:|---:|---:|
| kL_cL | 1.967551 | 1.873319 | 1.444221 |
| kL_cN | 1.496162 | 1.376666 | 0.999528 |
| kL_cH | 1.071173 | 1.004290 | 0.849075 |
| kN_cL | 2.350398 | 1.987777 | 1.601452 |
| kN_cN | 1.644586 | 1.269332 | 1.174273 |
| kN_cH | 1.258308 | 0.889807 | 0.833672 |
| kH_cL | 2.208870 | 1.841485 | 1.474098 |
| kH_cN | 1.774063 | 1.445349 | 1.100822 |
| kH_cH | 1.360865 | 1.095702 | 0.760576 |

The ±1 mm band remains the adopted diagnostic. Band sensitivity is interpretation of the same trajectories, not new ML targets.

## Settings decision

Adopt RK45 rtol=1e-6, atol=[1e-9 m,1e-8 m/s,1e-9 m,1e-8 m/s], max_step=0.005 s, 1 ms observations and 5 s duration as the starting settings for later runs. All nine pilots agree with the tighter/longer reference within the declared limits. Every later setup must still pass contact and tail checks; unresolved runs must be investigated, not silently used as labels.

## Measured computational work

Totals below cover nine integrations per method/duration. They are single-run measurements, not repeated performance benchmarks.

| Method/run | Total derivative calls | Total integration time [s] |
|---|---:|---:|
| base_1ms | 55776 | 1.809785 |
| tight_0p25ms | 114504 | 3.730987 |
| extended_0p25ms | 222504 | 7.227590 |
| rk4_0p5ms | 360000 | 12.132857 |
| rk4_0p25ms | 720000 | 24.102059 |

## Reproducibility and limits

`summary.json` retains every comparison, solver/grid/band setting, success flag, energy/contact/tail result, derivative count, integration timing, dependency version and source hash. Time histories for plotting are in `pilot_traces_1ms.npz`.
Timings are single-run measurements on this laptop; re-evaluating a trajectory on a different grid does not create an independent integration benchmark.
The nine pilots include the nominal case. Repeated refinements of a setup are not independent dataset rows. No full parameter dataset, ML fitting or report writing was performed.
These checks support the ideal model at the sampled setups. They do not prove every point in the parameter rectangle, certify exact continuous-time errors, establish real-car validity or establish physical travel clearance.
