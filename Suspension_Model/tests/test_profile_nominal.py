"""Profiler bookkeeping safeguards; these tests perform no physical integrations."""

import copy
import json
from pathlib import Path

import pytest
import profile_nominal as profile


@pytest.mark.parametrize("key,value", [("A_m", 9.0), ("derivative_evaluations", 0),
                                      ("settling_status", "resolved"), ("tail_pass", False)])
def test_physics_drift_is_not_hidden_by_timing_exclusion(key, value):
    reference = json.loads((profile.ROOT / "results/summary.json").read_text())["runs"]["baseline_5s_1ms"]
    changed = copy.deepcopy(reference)
    changed["integration_runtime_s"] = 99.0
    profile.require_equivalent(changed, reference)
    changed[key] = value
    with pytest.raises(ValueError):
        profile.require_equivalent(changed, reference)


def test_pair_ratios_use_matching_pair_and_ignore_warmup():
    times = [900, 2, 6, 12, 4, 8, 40]
    records = [dict(pair=p, mode=m, wall_s=t) for (p, m), t in zip(profile.SCHEDULE, times)]
    result = profile.timing_summary(records)
    assert result["unprofiled"]["median_s"] == 4
    assert result["profiled"]["median_s"] == 12
    assert result["paired_profile_to_unprofiled_ratios"] == [3, 3, 5]
    assert result["median_paired_ratio"] == 3


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf")])
def test_invalid_wall_time_is_rejected(bad):
    records = [dict(pair=p, mode=m, wall_s=1) for p, m in profile.SCHEDULE]
    records[2]["wall_s"] = bad
    with pytest.raises(ValueError):
        profile.timing_summary(records)


def test_missing_or_reordered_call_is_rejected():
    records = [dict(pair=p, mode=m, wall_s=1) for p, m in profile.SCHEDULE]
    with pytest.raises(ValueError):
        profile.timing_summary(records[:-1])
    records[1], records[2] = records[2], records[1]
    with pytest.raises(ValueError):
        profile.timing_summary(records)


def test_same_function_name_in_other_module_does_not_inflate_count():
    rows = [dict(source="project/quarter_car.py", function="rhs", calls=6196),
            dict(source="other.py", function="rhs", calls=90)]
    assert profile.call_count(rows, "project/quarter_car.py", "rhs") == 6196
    with pytest.raises(ValueError):
        profile.call_count(rows, "absent.py", "rhs")


def test_existing_output_refused_before_work(tmp_path, monkeypatch):
    marker = tmp_path / "keep.txt"
    marker.write_text("preserve")
    def forbidden():
        pytest.fail("No workload allowed when output exists")
    monkeypatch.setattr(profile, "nominal_workload", forbidden)
    with pytest.raises(FileExistsError):
        profile.run(tmp_path)
    assert marker.read_text() == "preserve"
    assert list(tmp_path.iterdir()) == [marker]


def test_custom_output_is_excluded_from_preservation(tmp_path, monkeypatch):
    root = tmp_path / "Suspension_Model"
    root.mkdir()
    (root / "physics.py").write_text("preserve")
    output = root / "custom_output"
    output.mkdir()
    monkeypatch.setattr(profile, "ROOT", root)
    before = profile.protected_files(output)
    (output / "new.json").write_text("new result")
    assert profile.protected_files(output) == before
    assert list(before) == ["Suspension_Model/physics.py"]
