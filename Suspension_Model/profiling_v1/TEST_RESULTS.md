# Focused profiler checks

12 October 2026. These bookkeeping tests perform no physical integrations or ML work.

Initial invocation: 11 passed, one test setup error in 4.09 s. Pytest could not
create its default sandbox temporary folder, so the overwrite-refusal test never
ran. This was not a simulation failure. Repeated the focused suite with an absent
workspace-local --basetemp folder: 12 passed in 0.86 s.

Independent static review then caught two issues before measurement: numerical
pool discovery needed to precede creation of the limits controller; the actual
custom output folder needed to be excluded from file-preservation scans. Both
were corrected before any profiled simulation. Added a regression check for the
custom-output case. Final focused result: **13 passed in 0.90 s**.

Final command, from Suspension_Model:

```powershell
& 'C:\Users\dedvu\anaconda3\python.exe' -B -m pytest -q tests/test_profile_nominal.py --basetemp 'C:\Users\dedvu\OneDrive\Documents\MMA3001 Jupiter notebooks\tmp\profiling_pytest_20261012_v2'
```

That temporary folder now exists; use another absent folder for a deliberate
repeat. Pytest owns/cleans its basetemp folder, so never point it at project data.

Coverage: changes to physical outputs/work/status are detected despite timing
exclusion; correct pair arithmetic and warmup exclusion; zero/negative/nonfinite
timings and wrong schedules rejected; function names distinguished by module;
existing outputs refused before work; custom output excluded from preservation.

The prior full project suite remains the historical 433-pass run. It was not
rerun for this new, separate profiler module. Actual workload checks additionally
confirmed unchanged physical results, expected function counts, one-thread pools
and all 120 protected files unchanged across seven new nominal integrations.
