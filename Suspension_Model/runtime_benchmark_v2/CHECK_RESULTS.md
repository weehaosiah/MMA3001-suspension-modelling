# Bounded runtime comparison: actual checks

Working computation evidence, not the assessed report.

This experiment returns the full-response peak A = max abs(zs-zu), in mm, measured from static equilibrium and including after the bump. It reuses the nine prescribed input locations with fresh timed integrations and the existing frozen models.

## Warm A-only query times

A warm query starts with Python and the fitted models already loaded. Input checks, saved feature scaling and finite-output checks are included. File export, plotting, startup and model loading are outside these query timers.

| Method | Mean of nine single-case medians [ms/query] | Median nine-case batch [ms/batch] | Median batch time / 9 [ms/case] | Batch throughput [cases/s] |
|---|---:|---:|---:|---:|
| Simulator: A only | 222.637844 | 2014.271000 | 223.807889 | 4.468 |
| Linear comparator | 0.126471 | 0.127570 | 0.014174 | 70549.392 |
| Frozen selected SVR | 0.163470 | 0.182364 | 0.020263 | 49351.738 |

The single-query aggregate gives each of these nine cases equal weight; it is the mean of their medians, not the median of every observation pooled together. Batch throughput describes one nine-row request, not the latency of an individual request.

| Guarded model | A-only single-query warm ratio | A-only nine-case batch warm ratio |
|---|---:|---:|
| Linear comparator | 1760.39 | 15789.51 |
| Frozen selected SVR | 1361.95 | 11045.31 |

Each ratio divides simulator A-only time by guarded model time for the same workload. These are warm query ratios on this machine, not overall project speedups or a guarantee on other hardware. Timing does not change the frozen accuracy-based preference for the SVR.

## Repeated single-query observations

Each simulator observation is one fresh integration. Each ML observation is a block duration divided by 1000 actual guarded prediction calls. There are five measured observations per condition; ML block-to-block spread does not estimate variation among individual requests. No slow measurement is discarded.

All elapsed times in the following table are milliseconds. Q25 and Q75 are the lower and upper quartiles; the interquartile range (IQR = Q75 - Q25) describes the middle half of the recorded observations.

| Method / case | Observations | Median [ms] | Minimum [ms] | Maximum [ms] | Q25 [ms] | Q75 [ms] | IQR [ms] |
|---|---:|---:|---:|---:|---:|---:|---:|
| Simulator: A only / train_001 | 5 | 224.115700 | 222.967800 | 225.840300 | 223.365400 | 224.672100 | 1.306700 |
| Simulator: A only / train_008 | 5 | 221.184100 | 218.200700 | 227.646600 | 220.190600 | 222.701100 | 2.510500 |
| Simulator: A only / train_015 | 5 | 221.381300 | 218.726800 | 224.285500 | 221.193000 | 223.516000 | 2.323000 |
| Simulator: A only / train_106 | 5 | 225.117400 | 220.156700 | 231.659700 | 222.455300 | 226.454700 | 3.999400 |
| Simulator: A only / train_113 | 5 | 223.849100 | 220.577200 | 229.341300 | 223.562300 | 227.706900 | 4.144600 |
| Simulator: A only / train_120 | 5 | 223.273700 | 218.813100 | 233.747100 | 221.197300 | 224.049800 | 2.852500 |
| Simulator: A only / train_211 | 5 | 221.044700 | 219.736300 | 226.521700 | 220.537300 | 225.505800 | 4.968500 |
| Simulator: A only / train_218 | 5 | 220.995400 | 220.229400 | 231.467800 | 220.353800 | 225.289500 | 4.935700 |
| Simulator: A only / train_225 | 5 | 222.779200 | 222.077200 | 228.632500 | 222.604700 | 225.697900 | 3.093200 |
| Linear comparator / train_001 | 5 | 0.125394 | 0.125132 | 0.131661 | 0.125230 | 0.129046 | 0.003815 |
| Linear comparator / train_008 | 5 | 0.125549 | 0.125183 | 0.126833 | 0.125484 | 0.126122 | 0.000638 |
| Linear comparator / train_015 | 5 | 0.126985 | 0.125691 | 0.128108 | 0.125997 | 0.126996 | 0.001000 |
| Linear comparator / train_106 | 5 | 0.126400 | 0.125210 | 0.131247 | 0.125394 | 0.126483 | 0.001089 |
| Linear comparator / train_113 | 5 | 0.126395 | 0.125199 | 0.131662 | 0.125769 | 0.128198 | 0.002429 |
| Linear comparator / train_120 | 5 | 0.125630 | 0.124352 | 0.134428 | 0.125324 | 0.127458 | 0.002134 |
| Linear comparator / train_211 | 5 | 0.130568 | 0.125098 | 0.135485 | 0.129708 | 0.133050 | 0.003343 |
| Linear comparator / train_218 | 5 | 0.125086 | 0.123852 | 0.126304 | 0.124497 | 0.126070 | 0.001572 |
| Linear comparator / train_225 | 5 | 0.126228 | 0.124600 | 0.129660 | 0.125790 | 0.128623 | 0.002833 |
| Frozen selected SVR / train_001 | 5 | 0.162226 | 0.161935 | 0.163595 | 0.162134 | 0.162245 | 0.000111 |
| Frozen selected SVR / train_008 | 5 | 0.163266 | 0.160606 | 0.166399 | 0.162786 | 0.164746 | 0.001960 |
| Frozen selected SVR / train_015 | 5 | 0.161808 | 0.160621 | 0.165615 | 0.161206 | 0.164169 | 0.002964 |
| Frozen selected SVR / train_106 | 5 | 0.164880 | 0.161384 | 0.165079 | 0.164636 | 0.164941 | 0.000306 |
| Frozen selected SVR / train_113 | 5 | 0.162755 | 0.161796 | 0.167874 | 0.162654 | 0.163997 | 0.001343 |
| Frozen selected SVR / train_120 | 5 | 0.164376 | 0.160326 | 0.177757 | 0.162088 | 0.166975 | 0.004887 |
| Frozen selected SVR / train_211 | 5 | 0.162212 | 0.161932 | 0.163014 | 0.162072 | 0.162255 | 0.000183 |
| Frozen selected SVR / train_218 | 5 | 0.162416 | 0.161637 | 0.184615 | 0.161790 | 0.162607 | 0.000817 |
| Frozen selected SVR / train_225 | 5 | 0.167289 | 0.161720 | 0.170191 | 0.162056 | 0.169302 | 0.007247 |

## Repeated nine-case batch observations

| Method | Observations | Median [ms] | Minimum [ms] | Maximum [ms] | Q25 [ms] | Q75 [ms] | IQR [ms] |
|---|---:|---:|---:|---:|---:|---:|---:|
| Simulator: A only | 5 | 2014.271000 | 2000.202900 | 2035.733500 | 2000.831500 | 2023.379900 | 22.548400 |
| Linear comparator | 5 | 0.127570 | 0.126145 | 0.129251 | 0.126527 | 0.127794 | 0.001267 |
| Frozen selected SVR | 5 | 0.182364 | 0.182042 | 0.186560 | 0.182281 | 0.182852 | 0.000571 |

## Full diagnostic simulation, kept separate

The mean of the nine per-case medians is **222.277811 ms per setup**. This path also calculates post-bump movement, relative settling, contact, energy and tail checks. The regressors return A only, so there is no equivalent-output ML speed ratio for this richer workflow.

| Case | Observations | Median [ms] | Minimum [ms] | Maximum [ms] | Q25 [ms] | Q75 [ms] | IQR [ms] |
|---|---:|---:|---:|---:|---:|---:|---:|
| train_001 | 5 | 222.430000 | 221.480800 | 231.456300 | 222.077700 | 224.760600 | 2.682900 |
| train_008 | 5 | 222.230600 | 220.932700 | 229.992300 | 221.688500 | 222.279100 | 0.590600 |
| train_015 | 5 | 220.551100 | 218.803300 | 229.279700 | 219.828500 | 222.364900 | 2.536400 |
| train_106 | 5 | 225.016500 | 220.382000 | 231.620900 | 221.939900 | 231.354400 | 9.414500 |
| train_113 | 5 | 221.511600 | 218.972900 | 226.586800 | 220.468500 | 225.962000 | 5.493500 |
| train_120 | 5 | 223.390700 | 222.097100 | 224.463900 | 222.895800 | 224.384800 | 1.489000 |
| train_211 | 5 | 220.486700 | 218.383000 | 225.544300 | 220.325700 | 225.495600 | 5.169900 |
| train_218 | 5 | 221.128400 | 219.935600 | 223.316300 | 220.230700 | 221.645400 | 1.414700 |
| train_225 | 5 | 223.754700 | 216.947500 | 227.213800 | 221.346300 | 224.360700 | 3.014400 |

## Actual checks and work

- all_calls_valid_and_reproduced: **PASS**.
- exactly_162_integrations: **PASS**.
- exactly_100060_benchmark_ml_calls: **PASS**.
- models_unchanged: **PASS**.
- pre_post_predictions_equal: **PASS**.
- frozen_inputs_unchanged: **PASS**.
- one_numerical_thread: **PASS**.
- Fresh simulation integrations, including warm-ups: **162**.
- Recorded derivative evaluations: **1,003,968**; these count state-derivative calculations, not floating-point operations.
- Guarded ML calls in the prescribed warm-ups and timing blocks: **100,060**.
- These are repeats of existing verified inputs, not new dataset rows, new fits or additional final-test evaluation.

## Limits and reproduction

The A-only simulation path omits contact, tail and settling classification inside its timer. Its use here rests on prior verification of these nine locations; a new arbitrary input still needs physical and numerical checks. Fast A prediction does not supply the post-bump trajectory or settling time.

The five-round experiment records local elapsed times. Background load, power conditions and scheduling can affect them, and the saved environment/context must accompany comparisons. Raw block durations, loop counts and method order are preserved with the benchmark outputs.

Historical simulation, development and verification costs remain in the separate partial ledger in [RUNTIME_PLAN.md](../RUNTIME_PLAN.md). Do not add a nested integration time to its enclosing row-processing time, or count reused pilot results twice. This stage has not measured a complete new build or established a numeric end-to-end break-even point.

See [RUNTIME_GUIDE.md](../RUNTIME_GUIDE.md) for the saved-artifact audit and reproduction procedure. Repeating a benchmark requires fresh computation and can produce different elapsed times. The final accuracy evidence and frozen SVR settings are unchanged.
