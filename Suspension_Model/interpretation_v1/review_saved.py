"""Recompute interpretation facts from saved results; no simulations or ML calls.

Run without arguments to check review.json, or use --write once to create it.
The source datasets, models, and earlier artifacts are never modified.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def calculate():
    """Return exact saved-data comparisons, checks, and input fingerprints."""
    files = ["results/summary.json", "dataset_v1/summary.json", "dataset_v1/train.csv",
             "dataset_v1/train_diagnostics.jsonl", "dataset_v1/validation_diagnostics.jsonl",
             "final_evaluation_v1/summary.json"]
    contents = {name: (ROOT / name).read_bytes() for name in files}
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in contents.items()}
    dataset = json.loads(contents["dataset_v1/summary.json"])
    for name in ("train.csv", "train_diagnostics.jsonl", "validation_diagnostics.jsonl"):
        assert hashes["dataset_v1/" + name] == dataset["artifact_sha256"][name], name
    train = [json.loads(s) for s in contents["dataset_v1/train_diagnostics.jsonl"].splitlines()]
    validation = [json.loads(s) for s in contents["dataset_v1/validation_diagnostics.jsonl"].splitlines()]
    table = list(csv.DictReader(contents["dataset_v1/train.csv"].decode().splitlines()))
    nominal = json.loads(contents["results/summary.json"])["final"]
    final = json.loads(contents["final_evaluation_v1/summary.json"])
    values = [{"id": r["setup"]["setup_id"], "ks": r["parameters"]["ks"], "cs": r["parameters"]["cs"],
               "A_mm": 1000*r["raw_summary"]["A_m"],
               "A_post_mm": 1000*r["raw_summary"]["A_post_m"],
               "settling_after_exit_s": r["validity"]["settling_after_exit_s"]} for r in train]
    checks = {
        "225_ordered_unique_training_ids": [v["id"] for v in values] == [f"train_{i:03d}" for i in range(1, 226)],
        "all_training_targets_valid": all(r["validity"]["target_valid"] is True for r in train),
        "all_training_settling_resolved": all(r["validity"]["settling_status"] == "resolved_under_adopted_settings" for r in train),
        "post_peak_not_above_full_peak": all(0 <= v["A_post_mm"] <= v["A_mm"] for v in values),
        "training_csv_targets_match_diagnostics": len(table) == 225 and all(
            r["setup_id"] == v["id"] and float(r["A_mm"]) == v["A_mm"] for r, v in zip(table, values)),
        "225_unique_training_pairs": len({(v["ks"], v["cs"]) for v in values}) == 225,
    }
    assert all(checks.values()), checks
    trends = {}
    for varied, fixed in (("cs", "ks"), ("ks", "cs")):
        pairs = []
        for level in sorted({v[fixed] for v in values}):
            line = sorted((v for v in values if v[fixed] == level), key=lambda v: v[varied])
            pairs.extend(zip(line[:-1], line[1:]))
        assert len(pairs) == 210
        trends[varied] = {}
        for metric in ("A_mm", "A_post_mm", "settling_after_exit_s"):
            increases = [(a, b) for a, b in pairs if b[metric] > a[metric]]
            decreases = [(a, b) for a, b in pairs if b[metric] < a[metric]]
            largest = max(pairs, key=lambda pair: pair[1][metric]-pair[0][metric])
            trends[varied][metric] = {"increases": len(increases), "decreases": len(decreases),
                "equal": 210-len(increases)-len(decreases), "pair_at_largest_signed_change": list(largest),
                "largest_signed_change": largest[1][metric]-largest[0][metric]}
    development = train + validation
    return {"scope": "saved-data interpretation; no new simulation, training, prediction or benchmark",
        "input_sha256": hashes, "checks": checks,
        "training_peak_timing": {
            "positive_full_peak_before_exit_count": sum(r["raw_summary"]["A_signed_m"] > 0 and
                r["raw_summary"]["A_time_s"] < .5 for r in train),
            "post_peak_at_exit_count": sum(r["raw_summary"]["A_post_time_s"] == .5 for r in train)},
        "nominal_refined": {"A_mm": 1000*nominal["A_m"], "A_time_s": nominal["A_time_s"],
            "A_signed_mm": 1000*nominal["A_signed_m"], "A_post_mm": 1000*nominal["A_post_m"],
            "A_post_time_s": nominal["A_post_time_s"], "settling_after_exit_s": nominal["settling_after_exit_s"],
            "settling_entry_s": nominal["settling_entry_s"]},
        "nine_baseline_examples": [v for v in values if v["ks"] in (18000., 24000., 30000.)
                                   and v["cs"] in (1594.8, 2126.4, 2658.)],
        "training_extrema": {metric: {"minimum": min(values, key=lambda v: v[metric]),
                                      "maximum": max(values, key=lambda v: v[metric])}
                             for metric in ("A_mm", "A_post_mm", "settling_after_exit_s")},
        "adjacent_grid_changes": trends,
        "historical_development_costs": {"rows": len(development),
            "new_integrations": sum(r["new_solver_completed"] for r in development),
            "new_integration_seconds": sum(r["new_integration_runtime_s"] for r in development),
            "row_processing_seconds": sum(r["row_processing_runtime_s"] for r in development),
            "reused_original_integration_seconds": sum(r["original_pilot_integration_runtime_s"] or 0 for r in development)},
        "saved_final_test_metrics": final["test_metrics"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = calculate()
    path = HERE / "review.json"
    if args.write:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, allow_nan=False)
            handle.write("\n")
        print("Saved interpretation facts; all six saved-data checks passed.")
    else:
        assert result == json.loads(path.read_text(encoding="utf-8")), "saved review facts or inputs changed"
        print("Audit passed: all six checks and all saved interpretation facts reproduce exactly.")
