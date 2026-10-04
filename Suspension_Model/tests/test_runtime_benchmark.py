"""P009 guards with synthetic responses and fake clocks; no physical runs or fits."""

from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import json
from types import SimpleNamespace

import numpy as np
import pytest

import runtime_benchmark as runtime


@pytest.fixture(autouse=True)
def forbid_physical_work(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("This test must replace expensive physical work")
    monkeypatch.setattr(runtime, "simulate", forbidden)
    monkeypatch.setattr(runtime, "row_result", forbidden)


@pytest.fixture
def cases():
    pairs = [(k, c) for k in (18000., 24000., 30000.) for c in (1594.8, 2126.4, 2658.)]
    return {ident: {"X": list(pair), "A_mm": 30.+j,
                   "setup": {"setup_id": ident, "split": "train", "ks_N_m": pair[0],
                             "cs_N_s_m": pair[1], "sampling": "15x15_grid", "seed": None}}
            for j, (ident, pair) in enumerate(zip(runtime.CASE_IDS, pairs))}


def expected_predictions(cases):
    return {method: {workload: {ident: case["A_mm"] for ident, case in cases.items()}
                     for workload in ("single_A", "batch_A")}
            for method in ("linear", "svr")}


def diagnostic_record(value=40.):
    return ({"new_solver_completed": True, "new_derivative_evaluations": 11,
             "origin": "new_integration",
             "validity": {"settling_status": "resolved_under_adopted_settings"}},
            {"target_valid": True, "A_mm": value})


def test_schedule_has_exact_case_coverage_and_physical_call_budget():
    jobs = runtime.make_schedule()
    assert len(jobs) == 234
    solve_counts = Counter()
    ml_calls = 0
    for job in jobs:
        assert job["phase"] == ("warmup" if job["round"] == 0 else "timed")
        if job["method"] in ("linear", "svr"):
            ml_calls += job["loops"]
        else:
            solve_counts[job["workload"]] += len(job["case_ids"])*job["loops"]
    assert solve_counts == {"single_A": 54, "batch_A": 54, "full_diagnostic": 54}
    assert ml_calls == 100060
    for method in ("simulation", "linear", "svr", "full_diagnostic"):
        for ident in runtime.CASE_IDS:
            workload = "full_diagnostic" if method == "full_diagnostic" else "single_A"
            selected = [j for j in jobs if j["workload"] == workload and j["method"] == method
                        and j["case_ids"] == [ident]]
            assert [j["round"] for j in selected] == list(range(6))


def test_schedule_rotates_methods_and_batch_keeps_fixed_nine_order():
    jobs = runtime.make_schedule()
    first_methods = []
    for round_index in range(1, 6):
        selected = [j for j in jobs if j["workload"] == "single_A"
                    and j["round"] == round_index and j["case_ids"] == [runtime.CASE_IDS[0]]]
        first_methods.append(selected[0]["method"])
        assert {j["method"] for j in selected} == {"simulation", "linear", "svr"}
    assert first_methods == ["simulation", "linear", "svr", "simulation", "linear"]
    assert all(j["case_ids"] == runtime.CASE_IDS for j in jobs if j["workload"] == "batch_A")


def test_peak_uses_fresh_baseline_whole_relative_response_and_mm(monkeypatch):
    calls = []
    state = np.array([[0, .002, -.006, .001], [0, 1, 2, 3],
                      [0, .004, .002, -.003], [0, 3, 2, 1]])
    def solve(parameters, bump, horizon, settings):
        calls.append((asdict(parameters), asdict(bump), horizon, asdict(settings)))
        def sample(dt):
            assert dt == .001
            return np.array([0., .2, .6, 5.]), state
        return SimpleNamespace(nfev=7, sample=sample)
    monkeypatch.setattr(runtime, "simulate", solve)
    result = runtime.simulate_peak([[18000., 1594.8], [30000., 2658.]])
    assert result == {"values_mm": [8., 8.], "integrations": 2, "nfev": 14, "attempts": 2}
    assert [c[0]["ks"] for c in calls] == [18000., 30000.]
    for _, bump, horizon, settings in calls:
        assert bump == {"height_m": .05, "duration_s": .5}
        assert horizon == 5.
        assert settings == {"rtol": 1e-6, "atol": (1e-9, 1e-8, 1e-9, 1e-8), "max_step_s": .005}


@pytest.mark.parametrize("X", [[], [24000., 2126.4], [[24000., np.inf]],
                              [[17999., 2126.4]], [[24000., 2659.]]])
def test_peak_rejects_invalid_query_before_any_solve(X):
    with pytest.raises(ValueError):
        runtime.simulate_peak(X)


def test_partial_batch_failure_retains_known_solver_work(monkeypatch):
    calls = []
    def solve(*args):
        calls.append(args)
        if len(calls) == 2:
            raise RuntimeError("synthetic second solve failure")
        return SimpleNamespace(nfev=7, sample=lambda dt: (np.array([0., 5.]), np.zeros((4, 2))))
    monkeypatch.setattr(runtime, "simulate", solve)
    with pytest.raises(runtime.QueryFailure, match="second solve") as failure:
        runtime.simulate_peak([[18000., 1594.8], [24000., 2126.4]])
    assert (failure.value.integrations, failure.value.nfev, failure.value.attempts) == (1, 7, 2)


def test_nonfinite_extracted_peak_fails_with_completed_solve_count(monkeypatch):
    monkeypatch.setattr(runtime, "simulate", lambda *a: SimpleNamespace(
        nfev=7, sample=lambda dt: (np.array([0., 5.]), np.full((4, 2), np.nan))))
    with pytest.raises(runtime.QueryFailure) as failure:
        runtime.simulate_peak([[24000., 2126.4]])
    assert (failure.value.integrations, failure.value.nfev, failure.value.attempts) == (1, 7, 1)


def test_diagnostics_explicitly_disable_pilot_cache(monkeypatch, cases):
    setup = cases[runtime.CASE_IDS[0]]["setup"]
    calls = []
    def row(value, cached):
        calls.append((value, cached))
        return diagnostic_record()
    monkeypatch.setattr(runtime, "row_result", row)
    result = runtime.diagnostic_peak([cases[runtime.CASE_IDS[0]]["X"]], [setup])
    assert calls == [(setup, None)]
    assert result == {"values_mm": [40.], "integrations": 1, "nfev": 11, "attempts": 1}


def test_diagnostic_parameter_mismatch_rejected_before_work(cases):
    setup = cases[runtime.CASE_IDS[0]]["setup"]
    with pytest.raises(ValueError, match="identities"):
        runtime.diagnostic_peak([[24000., 2126.4]], [setup])


@pytest.mark.parametrize("problem", ["cached", "invalid_target", "unresolved"])
def test_diagnostics_refuse_invalid_physical_work(monkeypatch, cases, problem):
    record, exported = diagnostic_record()
    if problem == "cached":
        record["origin"] = "verified_pilot_baseline"
    elif problem == "invalid_target":
        exported["target_valid"] = False
    else:
        record["validity"]["settling_status"] = "unresolved"
    monkeypatch.setattr(runtime, "row_result", lambda *a, **kw: (record, exported))
    with pytest.raises(runtime.QueryFailure) as failure:
        runtime.diagnostic_peak([cases[runtime.CASE_IDS[0]]["X"]], [cases[runtime.CASE_IDS[0]]["setup"]])
    assert (failure.value.integrations, failure.value.nfev, failure.value.attempts) == (1, 11, 1)


def test_diagnostic_unexpected_failure_preserves_completed_batch_work(monkeypatch, cases):
    count = 0
    def row(*args, **kwargs):
        nonlocal count
        count += 1
        if count == 2:
            raise RuntimeError("synthetic row failure")
        return diagnostic_record()
    monkeypatch.setattr(runtime, "row_result", row)
    selected = [cases[i] for i in runtime.CASE_IDS[:2]]
    with pytest.raises(runtime.QueryFailure, match="row failure") as failure:
        runtime.diagnostic_peak([c["X"] for c in selected], [c["setup"] for c in selected])
    assert (failure.value.integrations, failure.value.nfev, failure.value.attempts) == (1, 11, 2)


def test_timer_brackets_every_actual_call_and_keeps_last_result():
    events, ticks = [], iter([10., 12.])
    def clock():
        events.append("clock")
        return next(ticks)
    def function():
        events.append("call")
        return events.count("call")
    result = runtime.timed_call(function, 3, clock=clock)
    assert events == ["clock", "call", "call", "call", "clock"]
    assert result == {"elapsed_s": 2., "completed_loops": 3, "result": 3, "error": None}


def test_timer_preserves_failure_and_completed_calls():
    count, ticks = 0, iter([10., 12.5])
    def function():
        nonlocal count
        count += 1
        if count == 3:
            raise RuntimeError("synthetic callback failure")
        return count
    result = runtime.timed_call(function, 5, clock=lambda: next(ticks))
    assert count == 3 and result["completed_loops"] == 2 and result["result"] == 2
    assert result["elapsed_s"] == 2.5 and isinstance(result["error"], RuntimeError)


@pytest.mark.parametrize("loops", [0, -1, 1.5])
def test_timer_rejects_invalid_repetition_count(loops):
    with pytest.raises(ValueError):
        runtime.timed_call(lambda: pytest.fail("must not call"), loops)


def test_statistics_keep_slow_observation_and_use_declared_quantiles():
    assert runtime.statistics([1., 2., 3., 4., 100.]) == {
        "count": 5, "median_s": 3., "min_s": 1., "max_s": 100., "q25_s": 2., "q75_s": 4., "iqr_s": 2.}


@pytest.mark.parametrize("durations", [[], [0.], [-1.], [np.nan], [np.inf], [[1.]]])
def test_statistics_reject_missing_or_invalid_measurements(durations):
    with pytest.raises(ValueError):
        runtime.statistics(durations)


def synthetic_rows():
    rows = []
    for job in runtime.make_schedule():
        ml = job["method"] in ("linear", "svr")
        duration = {"simulation": 2., "linear": .01, "svr": .02, "full_diagnostic": 3.}[job["method"]]
        if job["workload"] == "batch_A":
            duration *= 9
        work = 0 if ml else len(job["case_ids"])
        elapsed = duration*job["loops"]
        rows.append({**job, "status": "ok", "completed_loops": job["loops"],
                     "elapsed_s": elapsed, "seconds_per_call": elapsed/job["loops"],
                     "integrations": work, "attempts": work, "nfev": work*10,
                     "ml_calls": job["loops"] if ml else 0,
                     "checks": {"input_unchanged": True, "outputs_reproduce": True, "positive_duration": True}})
    return rows


def test_summary_distinguishes_batch_time_and_excludes_full_diagnostics_from_ratios():
    result = runtime.summarise_timings(synthetic_rows())
    assert result["work"] == {"simulation_integrations": 162, "derivative_evaluations": 1620,
                              "ml_calls": 100060, "measured_simulation_integrations": 135,
                              "measured_ml_calls": 100000}
    assert result["batch_A"]["simulation"]["median_s"] == 18.
    assert result["batch_A"]["simulation"]["median_seconds_per_case"] == 2.
    assert result["batch_A"]["simulation"]["median_cases_per_second"] == .5
    assert result["warm_speed_ratios"]["single_A"] == pytest.approx({"linear": 200., "svr": 100.})
    assert set(result["warm_speed_ratios"]) == {"single_A", "batch_A"}


def test_summary_uses_mean_of_case_medians_and_excludes_warmups():
    rows = synthetic_rows()
    for row in rows:
        if row["workload"] == "single_A" and row["method"] == "simulation":
            value = 91. if row["case_ids"] == [runtime.CASE_IDS[-1]] else 1.
            if row["phase"] == "warmup":
                value = 9999.
            row["elapsed_s"] = row["seconds_per_call"] = value
    result = runtime.summarise_timings(rows)
    assert result["single_query"]["simulation"]["equal_case_mean_of_medians_s"] == 11.
    assert result["single_query"]["simulation"]["per_case"][runtime.CASE_IDS[-1]]["count"] == 5


@pytest.mark.parametrize("problem", ["missing_job", "reordered", "failed", "cached_work", "partial_loops", "wrong_units", "failed_check"])
def test_summary_rejects_incomplete_or_misreported_work(problem):
    rows = synthetic_rows()
    if problem == "missing_job":
        rows.pop()
    elif problem == "reordered":
        rows[0], rows[1] = rows[1], rows[0]
    elif problem == "failed":
        rows[0]["status"] = "failed"
    elif problem == "cached_work":
        rows[0]["integrations"] = 0
    elif problem == "partial_loops":
        rows[1]["completed_loops"] = 1
    elif problem == "wrong_units":
        rows[1]["seconds_per_call"] *= 1000
    else:
        rows[0]["checks"]["outputs_reproduce"] = False
    with pytest.raises(ValueError):
        runtime.summarise_timings(rows)


def fake_clock_executor(monkeypatch):
    real = runtime.timed_call
    def timed(function, loops):
        ticks = iter([10., 11.])
        return real(function, loops, clock=lambda: next(ticks))
    monkeypatch.setattr(runtime, "timed_call", timed)


def test_executor_really_calls_every_synthetic_query_without_mutating_inputs(monkeypatch, tmp_path, cases):
    fake_clock_executor(monkeypatch)
    original = deepcopy(cases)
    calls = Counter()
    by_X = {tuple(c["X"]): c["A_mm"] for c in cases.values()}
    def query(X):
        assert X.flags.writeable is False
        calls["integrations"] += len(X)
        return {"values_mm": [by_X[tuple(x)] for x in X], "integrations": len(X), "attempts": len(X), "nfev": 10*len(X)}
    def predict(model, X):
        assert X.flags.writeable is False
        calls[model] += 1
        return np.array([by_X[tuple(x)] for x in X])
    monkeypatch.setattr(runtime, "simulate_peak", query)
    monkeypatch.setattr(runtime, "diagnostic_peak", lambda X, setups: query(X))
    monkeypatch.setattr(runtime, "predict_checked", predict)
    rows = runtime.execute_jobs(runtime.make_schedule(), cases, {"linear": "linear", "svr": "svr"}, expected_predictions(cases), tmp_path)
    assert calls == {"integrations": 162, "linear": 50030, "svr": 50030}
    assert cases == original and len(rows) == 234
    assert all(row["status"] == "ok" for row in rows)
    assert len((tmp_path/"raw_timings.jsonl").read_text().splitlines()) == 234


def test_integrity_predictions_keep_single_and_batch_reference_shapes(monkeypatch, cases):
    calls = []
    def predict(model, X):
        calls.append((model, X.shape))
        return np.full(len(X), 30. if len(X) == 1 else 30.000000000000004)
    monkeypatch.setattr(runtime, "predict_checked", predict)
    result = runtime.integrity_predictions({"linear": "linear", "svr": "svr"}, cases)
    assert len(calls) == 20
    for method in ("linear", "svr"):
        assert calls.count((method, (1, 2))) == 9 and calls.count((method, (9, 2))) == 1
        assert result[method]["single_A"][runtime.CASE_IDS[0]] == 30.
        assert result[method]["batch_A"][runtime.CASE_IDS[0]] > 30.


@pytest.mark.parametrize("failure", ["solver", "changed_output", "mutated_input"])
def test_executor_retains_first_failure_and_stops(monkeypatch, tmp_path, cases, failure):
    fake_clock_executor(monkeypatch)
    calls = []
    def query(X):
        calls.append(X)
        if failure == "solver":
            raise runtime.QueryFailure("synthetic solver stop", integrations=0, nfev=0, attempts=1)
        if failure == "mutated_input":
            X.setflags(write=True)
            X[0, 0] += 1
        return {"values_mm": [-99.], "integrations": 1, "attempts": 1, "nfev": 10}
    monkeypatch.setattr(runtime, "simulate_peak", query)
    with pytest.raises(RuntimeError, match="preserved raw"):
        runtime.execute_jobs(runtime.make_schedule(), cases, {}, expected_predictions(cases), tmp_path)
    saved = [json.loads(s) for s in (tmp_path/"raw_timings.jsonl").read_text().splitlines()]
    assert len(calls) == len(saved) == 1 and saved[0]["status"] == "failed"
    if failure == "solver":
        assert saved[0]["attempts"] == 1 and saved[0]["integrations"] == 0
        assert saved[0]["failed_solver_work_may_be_unknown"] is True
    elif failure == "mutated_input":
        assert saved[0]["checks"]["input_unchanged"] is False
    else:
        assert saved[0]["checks"]["outputs_reproduce"] is False


def test_existing_output_refused_before_loading_or_mutation(monkeypatch, tmp_path):
    marker = tmp_path/"keep.txt"
    marker.write_text("original")
    monkeypatch.setattr(runtime, "verify_seal", lambda *a: pytest.fail("must reject before loading"))
    with pytest.raises(FileExistsError):
        runtime.run(tmp_path)
    assert marker.read_text() == "original" and list(tmp_path.iterdir()) == [marker]


def test_frozen_input_mutation_rejected_before_model_seal_check(monkeypatch, tmp_path):
    source = tmp_path/"source.txt"
    source.write_text("before")
    digest = runtime.sha256_file(source)
    source.write_text("after")
    monkeypatch.setattr(runtime, "ROOT", tmp_path/"project")
    monkeypatch.setattr(runtime, "verify_seal", lambda *a: pytest.fail("file drift must fail first"))
    with pytest.raises(ValueError, match="input changed"):
        runtime.verify_inputs({"input_sha256": {"source.txt": digest}})


@pytest.mark.parametrize("work_raises", [False, True])
def test_thread_context_discovers_lazy_pool_before_controller_and_restores(monkeypatch, work_raises):
    events = []
    pools = [{"prefix": "first", "num_threads": 8}, {"prefix": "second", "num_threads": 8}]
    def inspect():
        events.append("inspect")
        snapshot = deepcopy(pools)
        if len(pools) == 2:
            # First inspection loads a runtime too late to appear in its snapshot.
            pools.append({"prefix": "lazy", "num_threads": 16})
        return snapshot
    class Limit:
        def __init__(self, limits):
            events.append("controller")
            assert limits == 1 and len(pools) == 3
            self.saved = [pool["num_threads"] for pool in pools]
        def __enter__(self):
            events.append("enter")
            for pool in pools:
                pool["num_threads"] = 1
        def __exit__(self, *args):
            events.append("restore")
            for pool, count in zip(pools, self.saved):
                pool["num_threads"] = count
    monkeypatch.setattr(runtime, "threadpool_info", inspect)
    monkeypatch.setattr(runtime, "threadpool_limits", Limit)
    def perform():
        with runtime.single_thread_context() as snapshots:
            events.append("work")
            assert len(snapshots["before"]) == 2 and len(snapshots["limited"]) == 3
            assert all(pool["num_threads"] == 1 for pool in pools)
            if work_raises:
                raise RuntimeError("synthetic work failure")
    if work_raises:
        with pytest.raises(RuntimeError, match="synthetic work failure"):
            perform()
    else:
        perform()
    assert events == ["inspect", "controller", "enter", "inspect", "work", "restore"]
    assert [pool["num_threads"] for pool in pools] == [8, 8, 16]


@pytest.mark.parametrize("limited", [[], [{"prefix": "unrestricted", "num_threads": 16}]])
def test_thread_context_fails_closed_before_work_for_missing_or_unlimited_pools(monkeypatch, limited):
    snapshots = iter([[{"prefix": "before", "num_threads": 8}], limited])
    restored = []
    class Limit:
        def __init__(self, limits):
            assert limits == 1
        def __enter__(self):
            return self
        def __exit__(self, *args):
            restored.append(True)
    monkeypatch.setattr(runtime, "threadpool_info", lambda: next(snapshots))
    monkeypatch.setattr(runtime, "threadpool_limits", Limit)
    with pytest.raises(RuntimeError, match="thread limit"):
        with runtime.single_thread_context():
            pytest.fail("work must not start without verified thread limits")
    assert restored == [True]
