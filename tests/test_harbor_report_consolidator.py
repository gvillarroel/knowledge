from __future__ import annotations

import copy
import importlib.util
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "skills"
    / "harbor-author-evaluation-datasets"
    / "scripts"
    / "consolidate_harbor_reports.py"
)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("harbor_report_consolidator", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


def metric(values: list[float | None]) -> dict[str, float | int] | None:
    observed = [value for value in values if value is not None]
    if not observed:
        return None
    total = math.fsum(observed)
    return {"count": len(observed), "total": total, "average": total / len(observed)}


def trial(
    *,
    passed: bool = True,
    error: str | None = None,
    reward: float | None = 1.0,
    input_tokens: float | None = 100.0,
    cached_tokens: float | None = 20.0,
    output_tokens: float | None = 25.0,
    reasoning_tokens: float | None = None,
    cost: float | None = 0.01,
    latency_ms: float | None = 1_000.0,
) -> dict[str, object]:
    total_tokens = (
        input_tokens + output_tokens
        if input_tokens is not None and output_tokens is not None
        else None
    )
    return {
        "passed": passed,
        "error": error,
        "reward": reward,
        "costUsd": cost,
        "agentLatencyMs": latency_ms,
        "tokens": {
            "input": input_tokens,
            "cachedInput": cached_tokens,
            "output": output_tokens,
            "reasoning": reasoning_tokens,
            "total": total_tokens,
        },
    }


def job(
    job_id: str,
    trials: list[dict[str, object]],
    *,
    label: str = "SEALED_NATIVE_JOB_LABEL",
    requested: int | None = None,
    complete: bool = True,
) -> dict[str, object]:
    completed = len(trials)
    passed = sum(row["passed"] is True for row in trials)
    errored = sum(row["error"] is not None for row in trials)
    verifier_failed = completed - passed - errored
    rewards = [row["reward"] for row in trials]
    token_totals = [row["tokens"]["total"] for row in trials]
    costs = [row["costUsd"] for row in trials]
    latencies = [row["agentLatencyMs"] for row in trials]
    return {
        "label": label,
        "jobId": job_id,
        "startedAt": "2026-01-01T00:00:00Z",
        "finishedAt": "2026-01-01T00:01:00Z",
        "complete": complete,
        "completenessProblems": [],
        "summary": {
            "requestedTrials": completed if requested is None else requested,
            "completedTrials": completed,
            "passedTrials": passed,
            "verifierFailedTrials": verifier_failed,
            "erroredTrials": errored,
            "passRate": passed / completed if completed else 0,
            "reward": metric(rewards),
            "totalTokens": metric(token_totals),
            "agentLatencyMs": metric(latencies),
            "costUsd": metric(costs),
        },
        "trials": trials,
    }


def report(
    jobs: list[dict[str, object]],
    *,
    generated_at: str = "2026-01-01T00:00:00Z",
    native_title: str = "SEALED_NATIVE_REPORT_TITLE",
    warning: str | None = "SEALED_NATIVE_WARNING",
) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "source": "harbor",
        "title": native_title,
        "generatedAt": generated_at,
        "comparison": {
            "enabled": True,
            "fairnessBasis": "trial-results",
            "warning": warning,
        },
        "jobs": jobs,
    }


def write_report(path: Path, value: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def output_bytes(root: Path) -> dict[str, bytes]:
    return {name: (root / name).read_bytes() for name in MODULE.OUTPUT_FILES}


def test_happy_path_is_opaque_relocatable_deterministic_and_parseable(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    first = report(
        [job("job-a", [trial(reward=-0.25)])],
        generated_at="2026-01-01T00:30:00+01:00",
    )
    second = report(
        [job("job-b", [trial(reward=0.75)])],
        generated_at="2026-01-01T00:00:00Z",
    )
    source_a = write_report(tmp_path / "SEALED_PATH_A" / "a.json", first)
    source_b = write_report(tmp_path / "SEALED_PATH_B" / "b.json", second)
    moved_a = write_report(tmp_path / "OTHER_LOCATION" / "x.json", first)
    moved_b = write_report(tmp_path / "OTHER_LOCATION" / "y.json", second)
    out_a = tmp_path / "out-a"
    out_b = tmp_path / "out-b"

    assert MODULE.main([str(source_a), str(source_b), "--output-dir", str(out_a)]) == 0
    first_status = json.loads(capsys.readouterr().out)
    assert "outputDirectory" not in first_status
    assert MODULE.main([str(moved_a), str(moved_b), "--output-dir", str(out_b)]) == 0
    capsys.readouterr()

    assert output_bytes(out_a) == output_bytes(out_b)
    payloads = output_bytes(out_a)
    for forbidden in (
        b"SEALED_PATH",
        b"OTHER_LOCATION",
        b"SEALED_NATIVE_JOB_LABEL",
        b"SEALED_NATIVE_REPORT_TITLE",
        b"SEALED_NATIVE_WARNING",
        b"trial-results",
    ):
        assert all(forbidden not in payload for payload in payloads.values())

    structured = json.loads(payloads["comparison-report.json"])
    assert structured["generatedAt"] == "2026-01-01T00:00:00Z"
    assert all(run["label"].startswith("run-") for run in structured["runs"])
    assert set(structured["sourceReports"][0]) == {
        "comparisonWarningCode",
        "comparabilityCode",
        "generatedAt",
        "inputIndex",
        "sha256",
        "sourceReportId",
    }
    assert structured["sourceReports"][0]["comparabilityCode"] == "trial-evidence-only"
    for name in (
        "quality-comparison.svg",
        "resource-comparison.svg",
        "efficiency-frontier.svg",
    ):
        root = ET.fromstring(payloads[name])
        assert root.tag.endswith("svg")
        assert root.find("{http://www.w3.org/2000/svg}title") is not None
        assert root.find("{http://www.w3.org/2000/svg}desc") is not None


def test_markdown_escapes_explicit_public_title_markup(tmp_path: Path) -> None:
    source = write_report(tmp_path / "input.json", report([job("j", [trial()])]))
    prepared = MODULE.preflight_report_paths([source])
    normalized = [MODULE.read_report(path, index, size) for index, (path, size) in enumerate(prepared)]
    consolidated = MODULE.build_report(
        normalized,
        title="<img src=https://tracker.invalid> [click](javascript:alert(1)) `code`",
        baseline_selector=None,
        generated_at=None,
    )

    markdown = MODULE.render_markdown(consolidated)

    assert "<img" not in markdown
    assert "[click](" not in markdown
    assert "javascript:alert" in markdown
    assert "\\[click\\]\\(" in markdown


def test_native_job_timestamp_pair_may_consistently_omit_timezone(tmp_path: Path) -> None:
    value = report([job("j", [trial()])])
    native_job = value["jobs"][0]
    native_job["startedAt"] = "2026-01-01T00:00:00"
    native_job["finishedAt"] = "2026-01-01T00:01:00"
    source = write_report(tmp_path / "input.json", value)

    assert MODULE.main([str(source), "--output-dir", str(tmp_path / "out")]) == 0


def test_partial_metrics_show_coverage_and_never_drive_efficiency(
    tmp_path: Path,
) -> None:
    baseline = job("baseline", [trial(), trial()])
    candidate = job(
        "candidate",
        [
            trial(),
            trial(
                passed=False,
                error="provider failure",
                reward=None,
                input_tokens=None,
                cached_tokens=None,
                output_tokens=None,
                cost=None,
                latency_ms=None,
            ),
        ],
    )
    source = write_report(tmp_path / "input.json", report([baseline, candidate]))
    out = tmp_path / "out"

    assert MODULE.main([str(source), "--output-dir", str(out)]) == 0

    structured = json.loads((out / "comparison-report.json").read_text(encoding="utf-8"))
    partial = structured["runs"][1]
    assert partial["rewardObservedTrials"] == 1
    assert partial["tokens"]["total"]["complete"] is False
    assert partial["tokensPerTrial"] is None
    assert partial["costPerTrialUsd"] is None
    assert partial["costPerPassUsd"] is None
    assert partial["agentSecondsPerTrial"] is None
    delta = structured["deltas"][0]["metrics"]
    assert delta["averageReward"]["absolute"] is None
    assert delta["tokensPerTrial"]["absolute"] is None
    assert delta["costPerTrialUsd"]["absolute"] is None
    assert delta["agentSecondsPerTrial"]["absolute"] is None
    markdown = (out / "comparison-report.md").read_text(encoding="utf-8")
    assert markdown.count("(1/2)") >= 7


@pytest.mark.parametrize(
    "summary_field",
    ["reward", "costUsd", "agentLatencyMs"],
)
def test_scalar_summaries_must_match_native_trial_rows(
    summary_field: str,
    tmp_path: Path,
) -> None:
    value = report([job("j", [trial()])])
    summary = value["jobs"][0]["summary"][summary_field]
    summary["total"] = 99.0
    summary["average"] = 99.0
    source = write_report(tmp_path / f"{summary_field}.json", value)

    assert MODULE.main([str(source), "--output-dir", str(tmp_path / "out")]) == 2
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("case", ["compensated-total", "compensated-cache"])
def test_token_accounting_is_validated_per_trial(case: str, tmp_path: Path) -> None:
    rows = [
        trial(input_tokens=10, cached_tokens=2, output_tokens=10),
        trial(input_tokens=10, cached_tokens=2, output_tokens=10),
    ]
    if case == "compensated-total":
        rows[0]["tokens"]["total"] = 25
        rows[1]["tokens"]["total"] = 15
    else:
        rows[0]["tokens"]["cachedInput"] = 11
        rows[1]["tokens"]["cachedInput"] = 0
    source = write_report(tmp_path / f"{case}.json", report([job("j", rows)]))

    assert MODULE.main([str(source), "--output-dir", str(tmp_path / "out")]) == 2
    assert not (tmp_path / "out").exists()


def test_partial_reasoning_coverage_is_visible_in_resource_svg(tmp_path: Path) -> None:
    source = write_report(
        tmp_path / "input.json",
        report([job("j", [trial(reasoning_tokens=10), trial()])]),
    )
    out = tmp_path / "out"

    assert MODULE.main([str(source), "--output-dir", str(out)]) == 0

    resource = (out / "resource-comparison.svg").read_text(encoding="utf-8")
    assert re.search(r"reasoning 10 \(1/2\)", resource)


def test_partial_cache_coverage_is_visible_and_not_drawn_as_fresh(tmp_path: Path) -> None:
    source = write_report(
        tmp_path / "input.json",
        report([job("j", [trial(cached_tokens=20), trial(cached_tokens=None)])]),
    )
    out = tmp_path / "out"

    assert MODULE.main([str(source), "--output-dir", str(out)]) == 0

    resource = (out / "resource-comparison.svg").read_text(encoding="utf-8")
    assert re.search(r"cache 20 \(1/2\)", resource)


@pytest.mark.parametrize("partial_field", ["tokens", "agent-time", "incomplete-run"])
def test_frontier_requires_complete_token_cost_and_agent_time_coverage(
    partial_field: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate_trials = [trial(), trial()]
    if partial_field == "tokens":
        candidate_trials[1]["tokens"] = {
            "input": None,
            "cachedInput": None,
            "output": None,
            "reasoning": None,
            "total": None,
        }
    else:
        if partial_field == "agent-time":
            candidate_trials[1]["agentLatencyMs"] = None
    candidate_job = job(
        "candidate",
        candidate_trials,
        requested=3 if partial_field == "incomplete-run" else None,
        complete=partial_field != "incomplete-run",
    )
    if partial_field == "incomplete-run":
        candidate_job["completenessProblems"] = ["one requested trial is missing"]
    source = write_report(
        tmp_path / "input.json",
        report(
            [
                job("baseline", [trial(), trial()]),
                candidate_job,
            ]
        ),
    )
    observed_points: list[str] = []
    original_pareto = MODULE.pareto_runs

    def capture_points(points: list[tuple[dict[str, object], float, float]]) -> set[str]:
        observed_points.extend(point[0]["runId"] for point in points)
        return original_pareto(points)

    monkeypatch.setattr(MODULE, "pareto_runs", capture_points)
    out = tmp_path / "out"

    assert MODULE.main([str(source), "--output-dir", str(out)]) == 0

    structured = json.loads((out / "comparison-report.json").read_text(encoding="utf-8"))
    assert observed_points == [structured["runs"][0]["runId"]]


@pytest.mark.parametrize("passed", [True, False])
def test_complete_non_error_trial_requires_primary_reward(
    passed: bool,
    tmp_path: Path,
) -> None:
    source = write_report(
        tmp_path / "input.json",
        report([job("j", [trial(passed=passed, reward=None)])]),
    )

    assert MODULE.main([str(source), "--output-dir", str(tmp_path / "out")]) == 2
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("bad_text", ["\ud800", "\ufffe", "\ufdd0"])
def test_unsafe_unicode_is_rejected_before_publication(
    bad_text: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    value = report([job("j", [trial()], label=bad_text)])
    source = write_report(tmp_path / "input.json", value)

    assert MODULE.main([str(source), "--output-dir", str(tmp_path / "out")]) == 2
    captured = capsys.readouterr()
    assert "Traceback" not in captured.err
    assert not (tmp_path / "out").exists()


def test_oversized_json_integer_fails_closed_without_traceback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    raw = json.dumps(report([job("j", [trial()])]))
    marker = '"requestedTrials": 1'
    assert marker in raw
    raw = raw.replace(marker, '"requestedTrials": ' + "9" * 5_000, 1)
    source = tmp_path / "huge-integer.json"
    source.write_text(raw, encoding="utf-8")

    assert MODULE.main([str(source), "--output-dir", str(tmp_path / "out")]) == 2
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "Traceback" not in captured.err
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    "case",
    [
        "schema-bool",
        "complete-mismatch",
        "missing-trials",
        "metric-count",
        "invalid-timestamp",
        "invalid-started-timestamp",
        "mixed-job-timezones",
        "incomplete-without-problem",
        "unhashable-alias",
        "huge-integer",
    ],
)
def test_invalid_native_reports_fail_closed_without_traceback(
    case: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    value = report([job("j", [trial()])])
    native_job = value["jobs"][0]
    if case == "schema-bool":
        value["schemaVersion"] = True
    elif case == "complete-mismatch":
        native_job["summary"]["requestedTrials"] = 2
    elif case == "missing-trials":
        native_job["trials"] = []
    elif case == "metric-count":
        native_job["summary"]["costUsd"]["count"] = 2
    elif case == "invalid-timestamp":
        value["generatedAt"] = "not-a-timestamp"
    elif case == "invalid-started-timestamp":
        native_job["startedAt"] = "not-a-timestamp"
        native_job["finishedAt"] = None
        native_job["complete"] = False
        native_job["completenessProblems"] = ["job has no finished timestamp"]
    elif case == "mixed-job-timezones":
        native_job["startedAt"] = "2026-01-01T00:00:00"
        native_job["finishedAt"] = "2026-01-01T00:01:00Z"
    elif case == "incomplete-without-problem":
        native_job["complete"] = False
    elif case == "unhashable-alias":
        native_job["trials"][0]["tokens"]["cache"] = []
    elif case == "huge-integer":
        native_job["summary"]["requestedTrials"] = 10**400
    source = write_report(tmp_path / f"{case}.json", value)
    out = tmp_path / "out"

    assert MODULE.main([str(source), "--output-dir", str(out)]) == 2
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "Traceback" not in captured.err
    assert not out.exists()


@pytest.mark.parametrize("payload", ["duplicate", "nan", "infinity", "float-overflow"])
def test_json_parser_rejects_duplicate_keys_and_nonfinite_constants(
    payload: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    value = report([job("j", [trial()])])
    raw = json.dumps(value)
    if payload == "duplicate":
        raw = raw.replace('"schemaVersion": 1', '"schemaVersion": 1, "schemaVersion": 1', 1)
    elif payload == "nan":
        raw = raw.replace('"warning": "SEALED_NATIVE_WARNING"', '"warning": NaN', 1)
    elif payload == "infinity":
        raw = raw.replace('"warning": "SEALED_NATIVE_WARNING"', '"warning": Infinity', 1)
    else:
        raw = raw[:-1] + ', "ignoredFutureField": 1e9999}'
    source = tmp_path / f"{payload}.json"
    source.write_text(raw, encoding="utf-8")

    assert MODULE.main([str(source), "--output-dir", str(tmp_path / "out")]) == 2
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "Traceback" not in captured.err


def test_limits_are_checked_before_loading_or_normalizing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    too_many = [tmp_path / f"missing-{index}.json" for index in range(MODULE.MAX_REPORTS + 1)]
    with pytest.raises(MODULE.ReportError, match="input reports"):
        MODULE.preflight_report_paths(too_many)

    monkeypatch.setattr(
        MODULE,
        "normalize_job",
        lambda *args, **kwargs: pytest.fail("normalization should not start"),
    )
    with pytest.raises(MODULE.ReportError, match="at most"):
        MODULE.build_report(
            [{"jobs": [{}] * (MODULE.MAX_RUNS + 1)}],
            title="safe",
            baseline_selector=None,
            generated_at=None,
        )


def test_dirty_output_directory_is_rejected_without_writes(
    tmp_path: Path,
) -> None:
    source = write_report(tmp_path / "input.json", report([job("j", [trial()])]))
    out = tmp_path / "out"
    out.mkdir()
    sensitive = out / "raw-trials.json"
    sensitive.write_text("SEALED", encoding="utf-8")

    assert MODULE.main([str(source), "--output-dir", str(out), "--overwrite"]) == 2

    assert sensitive.read_text(encoding="utf-8") == "SEALED"
    assert not any((out / name).exists() for name in MODULE.OUTPUT_FILES)


def test_output_appearing_during_new_publication_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = write_report(tmp_path / "input.json", report([job("j", [trial()])]))
    out = tmp_path / "out"
    original_write_bytes = Path.write_bytes
    writes = 0

    def create_competing_output(self: Path, data: bytes) -> int:
        nonlocal writes
        result = original_write_bytes(self, data)
        writes += 1
        if writes == len(MODULE.OUTPUT_FILES):
            out.mkdir()
            (out / "sentinel").write_text("COMPETING", encoding="utf-8")
        return result

    monkeypatch.setattr(Path, "write_bytes", create_competing_output)

    assert MODULE.main([str(source), "--output-dir", str(out)]) == 2
    assert (out / "sentinel").read_text(encoding="utf-8") == "COMPETING"
    assert not any((out / name).exists() for name in MODULE.OUTPUT_FILES)


def test_overwrite_rolls_back_the_whole_generation_on_commit_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_source = write_report(
        tmp_path / "first.json", report([job("first", [trial(reward=0.1)])])
    )
    second_source = write_report(
        tmp_path / "second.json", report([job("second", [trial(reward=0.9)])])
    )
    out = tmp_path / "out"
    assert MODULE.main([str(first_source), "--output-dir", str(out)]) == 0
    original = output_bytes(out)
    original_replace = Path.replace
    calls = 0

    def fail_new_generation(self: Path, target: Path) -> Path:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated commit failure")
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", fail_new_generation)

    assert (
        MODULE.main(
            [str(second_source), "--output-dir", str(out), "--overwrite"]
        )
        == 2
    )
    assert output_bytes(out) == original


def test_extreme_finite_geometry_and_negative_reward_remain_valid(
    tmp_path: Path,
) -> None:
    huge = 1e300
    source = write_report(
        tmp_path / "input.json",
        report(
            [
                job(
                    "huge",
                    [
                        trial(
                            reward=-huge,
                            input_tokens=huge * 0.4,
                            cached_tokens=huge * 0.1,
                            output_tokens=huge * 0.6,
                            cost=huge,
                            latency_ms=huge,
                        )
                    ],
                )
            ]
        ),
    )
    out = tmp_path / "out"

    assert MODULE.main([str(source), "--output-dir", str(out)]) == 0

    for name in (
        "quality-comparison.svg",
        "resource-comparison.svg",
        "efficiency-frontier.svg",
    ):
        text = (out / name).read_text(encoding="utf-8")
        ET.fromstring(text)
        assert re.search(r"(?<![A-Za-z])(nan|inf)(?![A-Za-z])", text, re.I) is None
