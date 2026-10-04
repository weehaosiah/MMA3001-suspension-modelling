"""Fixed setup identities and validity rules for the first simulation dataset.

Applies PROJECT_STATE P007/D005. One row is one (stiffness, damping) setup;
time samples are not independent ML rows. No fitting/preprocessing occurs here.
Course basis: Week05_6 cells 4, 13-15, 19, 28-30; Week05_5 cells 16-17, 36-37.
"""

from dataclasses import asdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

import numpy as np

from quarter_car import Bump, Parameters, SolverSettings


COUNTS = {"train": 225, "validation": 75, "test": 100}
SEEDS = {"validation": 3001, "test": 3002}
KS_RANGE = (18000.0, 30000.0)
CS_RANGE = (1594.8, 2658.0)
HORIZON_S = 5.0
OBSERVATION_DT_S = 0.001
BAND_M = 0.001
CONFIRMATION_S = 1.0
CONTACT_MARGIN_N = 1.0  # Fixed sampled screening guard; not a physical safety limit.


def sha256_file(path):
    """Return a file's SHA256 identity; missing/unreadable files raise OSError."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_setups():
    """Return the predeclared 400 setup dictionaries, with stable IDs and splits.

    Training traversal: ascending stiffness outer loop, damping inner loop.
    Each random split has its own PCG64 generator and one (count,2) uniform draw;
    columns are [ks,cs]. No redraws, noise, shuffle or global RNG state are used.
    Validation of identity, counts and finite domain values occurs before return.
    """
    rows = []
    for ks in np.linspace(*KS_RANGE, 15):
        for cs in np.linspace(*CS_RANGE, 15):
            rows.append({"setup_id": f"train_{len(rows)+1:03d}", "split": "train",
                         "ks_N_m": float(ks), "cs_N_s_m": float(cs),
                         "sampling": "15x15_grid", "seed": None})
    for split in ("validation", "test"):
        generator = np.random.Generator(np.random.PCG64(SEEDS[split]))
        pairs = generator.uniform([KS_RANGE[0], CS_RANGE[0]],
                                  [KS_RANGE[1], CS_RANGE[1]], size=(COUNTS[split], 2))
        for index, (ks, cs) in enumerate(pairs, 1):
            rows.append({"setup_id": f"{split}_{index:03d}", "split": split,
                         "ks_N_m": float(ks), "cs_N_s_m": float(cs),
                         "sampling": "independent_uniform_PCG64", "seed": SEEDS[split]})
    validate_setups(rows)
    return rows


def validate_setups(rows):
    """Reject missing/duplicate identities, wrong roles/counts or invalid inputs.

    Raises ValueError on any violation. Exact duplicate coefficient pairs are
    rejected across all roles. No failed or duplicated row is silently removed.
    """
    if len(rows) != sum(COUNTS.values()):
        raise ValueError("expected exactly 400 declared setups")
    ids, pairs = set(), set()
    counts = dict.fromkeys(COUNTS, 0)
    for row in rows:
        if not isinstance(row, dict) or not {"setup_id", "split", "ks_N_m", "cs_N_s_m"}.issubset(row):
            raise ValueError("setup is missing required identity/role/input fields")
        if row["split"] not in counts:
            raise ValueError("unsupported split")
        if row["setup_id"] in ids:
            raise ValueError("duplicate setup identity")
        ids.add(row["setup_id"])
        pair = (row["ks_N_m"], row["cs_N_s_m"])
        if not all(isinstance(value, (int, float)) and np.isfinite(value) for value in pair) or not (KS_RANGE[0] <= pair[0] <= KS_RANGE[1]
                                             and CS_RANGE[0] <= pair[1] <= CS_RANGE[1]):
            raise ValueError("setup outside finite declared domain")
        if pair in pairs:
            raise ValueError("duplicate coefficient pair within/across splits")
        pairs.add(pair)
        counts[row["split"]] += 1
    if counts != COUNTS:
        raise ValueError("split counts differ from the frozen plan")
    for split, count in COUNTS.items():
        expected = {f"{split}_{index:03d}" for index in range(1, count + 1)}
        actual = {row["setup_id"] for row in rows if row["split"] == split}
        if actual != expected:
            raise ValueError("setup IDs disagree with assigned role")
    return {"rows": len(rows), "unique_ids": len(ids), "unique_pairs": len(pairs),
            "split_counts": counts, "duplicates": 0, "finite_in_domain": True}


def classify_summary(summary, continuity_error=0.0):
    """Return independent numerical, contact, target and settling validity.

    Uses the adopted nominal units/settings. Nonfinite, incomplete, wrong-setting,
    inadequate-tail, inconsistent-peak or energy/continuity failures prevent a
    primary ML target. Unresolved settling alone does NOT erase a valid A.
    A finite raw estimate is retained in diagnostics even if the target is null.
    This applies pilot-verified settings plus per-row checks; it does not assert
    a separate refinement/horizon comparison or exact error bound for every row.
    Missing required fields fail closed; no exception is needed for missing data.
    """
    reasons = []
    numeric_fields = ("A_m", "A_post_m", "A_time_s", "A_post_time_s", "A_signed_m",
                      "tail_bound_m", "tail_limit_m", "minimum_contact_N",
                      "maximum_energy_increase_J", "energy_increase_allowance_J",
                      "post_bump_energy_start_J")
    finite = all(isinstance(summary.get(key), (int, float))
                 and np.isfinite(summary[key]) for key in numeric_fields)
    if not finite:
        reasons.append("missing_or_nonfinite_diagnostic")
    config_ok = (summary.get("end_time_s") == HORIZON_S
                 and summary.get("observation_dt_s") == OBSERVATION_DT_S
                 and summary.get("band_m") == BAND_M
                 and summary.get("confirmation_s") == CONFIRMATION_S)
    if not config_ok:
        reasons.append("unexpected_numerical_settings")
    if not summary.get("solver_success", False) or not summary.get("finite_states", False):
        reasons.append("unsuccessful_or_nonfinite_solution")
    if not isinstance(continuity_error, (int, float)) or not np.isfinite(continuity_error) or continuity_error != 0:
        reasons.append("exit_state_discontinuity")
    if finite:
        a, ap = summary["A_m"], summary["A_post_m"]
        consistent = (a > 0 and 0 < ap <= a
                      and abs(abs(summary["A_signed_m"]) - a) <= 1e-14
                      and 0 <= summary["A_time_s"] <= HORIZON_S
                      and Bump().duration_s <= summary["A_post_time_s"] <= HORIZON_S)
        if not consistent:
            reasons.append("inconsistent_primary_or_post_peak")
        expected_tail_limit = min(0.0005, a / 2, ap / 2)
        if not (summary.get("tail_pass", False)
                and 0 <= summary["tail_bound_m"] < expected_tail_limit
                and summary["tail_limit_m"] == expected_tail_limit):
            reasons.append("inadequate_tail")
        expected_energy_allowance = 1e-10 * max(1.0, summary.get("post_bump_energy_start_J", float("nan")))
        if not (np.isfinite(summary.get("post_bump_energy_start_J", float("nan")))
                and summary["post_bump_energy_start_J"] >= 0
                and summary.get("energy_pass", False)
                and summary["energy_increase_allowance_J"] == expected_energy_allowance
                and 0 <= summary["maximum_energy_increase_J"] <= expected_energy_allowance):
            reasons.append("post_bump_energy_failure")
    numerical_ok = not reasons
    contact = summary.get("minimum_contact_N", float("nan"))
    contact_ok = isinstance(contact, (int, float)) and np.isfinite(contact) and contact > CONTACT_MARGIN_N
    if not contact_ok:
        reasons.append("contact_nonpositive_or_ambiguous")
    entry = summary.get("settling_entry_s")
    after = summary.get("settling_after_exit_s")
    settling_ok = bool(numerical_ok and summary.get("settling_status") == "candidate"
                       and isinstance(entry, (int, float)) and np.isfinite(entry)
                       and isinstance(after, (int, float)) and np.isfinite(after)
                       and Bump().duration_s <= entry <= HORIZON_S - CONFIRMATION_S
                       and after >= 0 and abs(entry - Bump().duration_s - after) <= 1e-12
                       and summary["tail_bound_m"] < BAND_M)
    target_valid = bool(numerical_ok and contact_ok)
    return {
        "numerical_primary_valid": bool(numerical_ok), "contact_consistent": bool(contact_ok),
        "target_valid": target_valid,
        "A_mm": float(summary["A_m"] * 1000) if target_valid else None,
        "settling_status": "resolved_under_adopted_settings" if settling_ok else "unresolved",
        "settling_after_exit_s": float(after) if settling_ok else None,
        "failure_reasons": reasons,
        "resolution_basis": "pilot refinement evidence plus per-row checks; no separate per-row refinement claim",
    }


def load_verified_pilots(summary_path, model_path):
    """Load exactly nine eligible baseline pilot summaries, rejecting stale cache.

    Requires matching model bytes, installed numerical versions, exact physical
    parameters, bump, equilibrium start, adopted settings and successful pilot
    verification. Only base_1ms is reused, never the tight/extended final result.
    Returns {(ks,cs): {pilot_id, parameters, summary, continuity_error, source_sha256}}.
    Raises ValueError for inconsistent/unverified inputs, OSError for bad paths.
    """
    path = Path(summary_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    expected_solver = asdict(SolverSettings())
    expected_solver["atol"] = list(expected_solver["atol"])
    selected = {"solver": expected_solver, "observation_dt_s": OBSERVATION_DT_S,
                "horizon_s": HORIZON_S}
    if (not data.get("passed") or not data.get("unit_tests_passed")
            or not data.get("reduced_case", {}).get("passed")
            or data.get("selected_settings") != selected
            or data.get("baseline_solver") != expected_solver):
        raise ValueError("pilot verification/settings do not support this dataset")
    if data.get("bump") != asdict(Bump()) or data.get("initial_state") != [0.0] * 4:
        raise ValueError("pilot physical input or initial state changed")
    model_hashes = [v for k, v in data.get("input_sha256", {}).items()
                    if k.replace("\\", "/") == "Suspension_Model/quarter_car.py"]
    if model_hashes != [sha256_file(model_path)]:
        raise ValueError("model source differs from verified pilot source")
    packages = data.get("environment", {}).get("packages", {})
    if any(packages.get(name) != importlib.metadata.version(name) for name in ("numpy", "scipy")):
        raise ValueError("numerical package versions differ from pilot environment")
    if data.get("environment", {}).get("python") != sys.version:
        raise ValueError("Python version differs from pilot environment")
    expected_pairs = {(k, c) for k in (18000.0, 24000.0, 30000.0)
                      for c in (1594.8, 2126.4, 2658.0)}
    cache = {}
    artifact_hash = sha256_file(path)
    required_checks = (
        "finite_complete_solutions", "full_exit_state_continuity", "matched_rk4_comparison_times",
        "energy_nonincrease", "tail_margin", "positive_contact_with_margin",
        "solver_peak_agreement", "grid_peak_agreement", "horizon_peak_agreement",
        "rk4_peak_agreement", "selected_peak_agreement", "settling_agreement_all_bands",
        "unit_and_reduced_prerequisites")
    for pilot in data.get("pilots", []):
        p = pilot["parameters"]
        pair = (p["ks"], p["cs"])
        expected_parameters = asdict(Parameters(ks=pair[0], cs=pair[1]))
        summary = pilot["bands"]["1"]["runs"]["base_1ms"]
        continuity = pilot.get("continuity_error", float("nan"))
        if (pair not in expected_pairs or pair in cache or p != expected_parameters
                or not pilot.get("passed") or not pilot.get("horizon_adequate")
                or not all(pilot.get("checks", {}).get(name) is True for name in required_checks)
                or pilot.get("horizon_s") != HORIZON_S
                or not classify_summary(summary, continuity)["target_valid"]):
            raise ValueError("pilot row is inconsistent or invalid for reuse")
        cache[pair] = {"pilot_id": pilot["id"], "parameters": p, "summary": summary,
                       "continuity_error": continuity, "source_sha256": artifact_hash}
    if set(cache) != expected_pairs:
        raise ValueError("expected nine distinct verified pilots")
    return cache


def safe_json(value):
    """Replace nonfinite numbers with null for a failure record, preserving keys."""
    if isinstance(value, dict):
        return {key: safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value
