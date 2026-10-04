# Preserved preflight failure

This attempt stopped before any benchmark warm-up, timed job or integrity
prediction. All 429 tests passed in 6.03 s, then the numerical-thread check
rejected an incompletely applied one-thread limit. No raw timing file exists.

Fresh-process diagnosis found MKL and Microsoft OpenMP limited to one thread,
but newly loaded Intel OpenMP reported 16 after the first limits context. A
second fresh controller reported one for all three. Initial library inspection
can load the additional runtime after the first discovery list has been made.

The correction explicitly inspects libraries before constructing the limits
controller, checks all detected pools before work, and checks them again after
work. It preserves the prescribed one-thread condition, queries and repetitions.
No numerical/model setting, fitted model, system setting or dependency changed.

`runner_at_failed_preflight.py` preserves the original runner bytes identified by
this attempt's plan. The live runner subsequently changes to implement the fix,
so this failed folder is not expected to pass the completed-run artifact audit.
The next attempt uses a new folder, `runtime_benchmark_v2`; this evidence is kept.
