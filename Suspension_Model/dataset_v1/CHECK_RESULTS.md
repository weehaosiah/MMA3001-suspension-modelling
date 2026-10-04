# Simulation dataset checkpoint

Working data/check documentation, not the assessed report.

Dataset readiness: **PASS**.

| Role | Declared rows | Eligible targets | Reused pilots | Unresolved settling |
|---|---:|---:|---:|---:|
| train | 225 | 225 | 9 | 0 |
| validation | 75 | 75 | 0 | 0 |
| test | 100 | 100 | 0 | 0 |

## Actual checks

- 400 unique setup IDs and coefficient pairs; declared split counts and finite input domain checked before simulation.
- Setup manifest and exact RNG/sampling/configuration/source details saved before generating outputs.
- Original nine baseline pilot outputs reused in training; 391 new integrations.
- Every row checked for complete finite solution, exit-state continuity, peak consistency, contact, energy and adequate tail.
- Primary-target eligibility is separate from settling resolution. Failed rows retain their IDs/splits and have empty ML targets.
- Saved CSV/JSON identities, full-precision input round trips and metre-to-millimetre target conversion checked mechanically.
- Minimum sampled tyre force across generated/reused rows: 2398.808926 N; required screening margin >1 N.
- Largest remaining-motion bound: 0.011530651 mm; checked against each row's adopted peak/tail margins.
- Largest positive sampled post-bump energy increment: 0 J.
- Failure reasons/counts: {}.
- Exact regression-test output is in unit_tests.txt; source/artifact hashes are recorded in the manifests.

## Reproduce and use

Run `python generate_dataset.py --output dataset_recheck` from the project folder for a fresh independent version. Existing output folders are never overwritten.
One data row is a complete setup, not a trajectory time sample. Model inputs are ONLY ks_N_m and cs_N_s_m; the sole target is A_mm.
Raw A in metres and supporting post-bump/settling/physical diagnostics are in role-specific JSONL files; they must not become prediction features.
Training and validation outputs are at this directory's top level. Final-test outputs are under heldout_test/; do not inspect them for model choices.
Input locations and predeclared numerical/physical validity checks may be inspected for all splits; no held-out response distribution, prediction error or response plot was inspected.

## Limits and next stage

Settings were verified on nine pilots. Each later row receives its own validity screening, not a new full refinement/RK4 programme. Settling is labelled resolved_under_adopted_settings to preserve that distinction.
Sampled physical consistency and numerical checks do not validate a real car or prove the entire continuous domain. Sample sufficiency and ML performance remain unknown.
No preprocessing was fitted, no ML model trained, no final-test prediction evaluated and no assessed report written.
