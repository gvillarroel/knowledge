from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "evaluations" / "semantic-okf-ensemble" / "scripts"


def _load_validator() -> ModuleType:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "semantic_okf_ensemble_scaffold_validator",
        SCRIPTS / "validate_scaffold.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def validator() -> ModuleType:
    return _load_validator()


def test_final_scaffold_and_integrity_reports_pass(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    answer_json = tmp_path / "answer-output-comparison-final.json"
    answer_markdown = tmp_path / "answer-output-comparison-final.md"
    attestation_json = tmp_path / "skill-arena-mcp-runtime-attestation-final.json"
    attestation_markdown = tmp_path / "skill-arena-mcp-runtime-attestation-final.md"
    answer_json.write_text("{}\n", encoding="utf-8", newline="\n")
    answer_markdown.write_text("fixture\n", encoding="utf-8", newline="\n")
    attestation_json.write_text("{}\n", encoding="utf-8", newline="\n")
    attestation_markdown.write_text("fixture\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(validator, "ANSWER_OUTPUT_REPORT", answer_json)
    monkeypatch.setattr(validator, "ANSWER_OUTPUT_MARKDOWN", answer_markdown)
    monkeypatch.setattr(validator, "MCP_RUNTIME_ATTESTATION", attestation_json)
    monkeypatch.setattr(
        validator, "MCP_RUNTIME_ATTESTATION_MARKDOWN", attestation_markdown
    )
    monkeypatch.setattr(
        validator,
        "validate_checked_answer_output_report",
        lambda: {"answer_count": 90},
    )
    monkeypatch.setattr(
        validator,
        "validate_checked_mcp_runtime_attestation",
        lambda _answer_report: {"aggregates": {"trace_count": 90}},
    )

    report = validator.validate()
    assert report["status"] == "pass"
    assert report["candidate_count"] == 10
    assert report["answer_output_answer_count"] == 90
    assert report["answer_output_report_sha256"] == validator.sha256(answer_json)
    assert report["answer_output_markdown_sha256"] == validator.sha256(answer_markdown)
    assert report["mcp_runtime_attested_trace_count"] == 90
    assert report["mcp_runtime_attestation_sha256"] == validator.sha256(
        attestation_json
    )
    assert report["frozen_benchmark_sha256"] == validator.validate_frozen()[
        "manifest_sha256"
    ]


def _install_checked_answer_fixture(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    json_text: str | None = None,
    markdown_text: str | None = None,
    validation_error: str | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    report: dict[str, object] = {
        "schema_version": "fixture/1.0",
        "answer_count": 90,
        "manifest": {"sha256": "a" * 64},
    }
    expected_markdown = "# Fixture answer report\n"
    report_path = tmp_path / "answer-output-comparison-final.json"
    markdown_path = tmp_path / "answer-output-comparison-final.md"
    report_path.write_text(
        json_text
        if json_text is not None
        else json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        markdown_text if markdown_text is not None else expected_markdown,
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "ANSWER_OUTPUT_REPORT", report_path)
    monkeypatch.setattr(validator, "ANSWER_OUTPUT_MARKDOWN", markdown_path)
    monkeypatch.setattr(
        validator,
        "load_answer_output_contract",
        lambda _path: {"contract": "fixture"},
    )

    observed: dict[str, object] = {}
    aggregate = ModuleType("fixture_answer_output_aggregator")

    def validate_summary(value: object, contract: object) -> object:
        observed["report"] = value
        observed["contract"] = contract
        if validation_error is not None:
            raise ValueError(validation_error)
        return value

    aggregate.validate_summary = validate_summary  # type: ignore[attr-defined]
    aggregate.render_markdown = lambda _value: expected_markdown  # type: ignore[attr-defined]
    monkeypatch.setattr(validator, "module_from_path", lambda _name, _path: aggregate)
    return report, observed


def test_checked_answer_report_delegates_schema_and_binding_validation(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    report, observed = _install_checked_answer_fixture(
        validator, monkeypatch, tmp_path
    )

    assert validator.validate_checked_answer_output_report() == report
    assert observed == {
        "report": report,
        "contract": {"contract": "fixture"},
    }


@pytest.mark.parametrize("missing", ["json", "markdown"])
def test_checked_answer_report_fails_clearly_when_publication_is_missing(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing: str,
) -> None:
    report_path = tmp_path / "answer-output-comparison-final.json"
    markdown_path = tmp_path / "answer-output-comparison-final.md"
    if missing != "json":
        report_path.write_text("{}\n", encoding="utf-8")
    if missing != "markdown":
        markdown_path.write_text("# Fixture\n", encoding="utf-8")
    monkeypatch.setattr(validator, "ANSWER_OUTPUT_REPORT", report_path)
    monkeypatch.setattr(validator, "ANSWER_OUTPUT_MARKDOWN", markdown_path)

    label = "JSON" if missing == "json" else "Markdown"
    with pytest.raises(validator.EvaluationError, match=f"{label} is missing"):
        validator.validate_checked_answer_output_report()


def test_checked_answer_report_rejects_duplicate_json_keys(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_checked_answer_fixture(
        validator,
        monkeypatch,
        tmp_path,
        json_text='{"answer_count":90,"answer_count":91}\n',
    )

    with pytest.raises(validator.EvaluationError, match="duplicate JSON key: answer_count"):
        validator.validate_checked_answer_output_report()


def test_checked_answer_report_rejects_noncanonical_publication_bytes(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    report, _ = _install_checked_answer_fixture(validator, monkeypatch, tmp_path)
    validator.ANSWER_OUTPUT_REPORT.write_text(
        json.dumps(report, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(validator.EvaluationError, match="canonical publication bytes"):
        validator.validate_checked_answer_output_report()


def test_checked_answer_report_rejects_markdown_drift(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_checked_answer_fixture(
        validator,
        monkeypatch,
        tmp_path,
        markdown_text="# Drifted report\n",
    )

    with pytest.raises(validator.EvaluationError, match="Markdown differs"):
        validator.validate_checked_answer_output_report()


def test_checked_answer_report_surfaces_aggregate_binding_failures(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_checked_answer_fixture(
        validator,
        monkeypatch,
        tmp_path,
        validation_error="compact Skill Arena manifest binding differs",
    )

    with pytest.raises(
        validator.EvaluationError,
        match="checked answer-output comparison is invalid: compact Skill Arena manifest binding differs",
    ):
        validator.validate_checked_answer_output_report()


def _install_checked_attestation_fixture(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    json_text: str | None = None,
    markdown_text: str | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    report: dict[str, object] = {
        "schema_version": "fixture/1.0",
        "aggregates": {"trace_count": 90},
    }
    expected_markdown = "# Fixture trace attestation\n"
    report_path = tmp_path / "skill-arena-mcp-runtime-attestation-final.json"
    markdown_path = tmp_path / "skill-arena-mcp-runtime-attestation-final.md"
    report_path.write_text(
        json_text
        if json_text is not None
        else json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        markdown_text if markdown_text is not None else expected_markdown,
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "MCP_RUNTIME_ATTESTATION", report_path)
    monkeypatch.setattr(
        validator, "MCP_RUNTIME_ATTESTATION_MARKDOWN", markdown_path
    )
    monkeypatch.setattr(
        validator,
        "load_answer_output_contract",
        lambda _path: {"contract": "fixture"},
    )
    observed: dict[str, object] = {}
    module = ModuleType("fixture_trace_attestor")

    def validate_report(value: object, contract: object, **kwargs: object) -> object:
        observed["report"] = value
        observed["contract"] = contract
        observed["answer_report"] = kwargs["answer_report"]
        return value

    module.validate_report = validate_report  # type: ignore[attr-defined]
    module.render_markdown = lambda _value: expected_markdown  # type: ignore[attr-defined]
    monkeypatch.setattr(validator, "module_from_path", lambda _name, _path: module)
    return report, observed


def test_checked_trace_attestation_delegates_schema_and_answer_binding(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    report, observed = _install_checked_attestation_fixture(
        validator, monkeypatch, tmp_path
    )
    answer_report = {"answer_count": 90, "status": "pass"}

    assert validator.validate_checked_mcp_runtime_attestation(answer_report) == report
    assert observed == {
        "report": report,
        "contract": {"contract": "fixture"},
        "answer_report": answer_report,
    }


@pytest.mark.parametrize("missing", ["json", "markdown"])
def test_checked_trace_attestation_fails_clearly_when_publication_is_missing(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing: str,
) -> None:
    json_path = tmp_path / "attestation.json"
    markdown_path = tmp_path / "attestation.md"
    if missing != "json":
        json_path.write_text("{}\n", encoding="utf-8")
    if missing != "markdown":
        markdown_path.write_text("# Fixture\n", encoding="utf-8")
    monkeypatch.setattr(validator, "MCP_RUNTIME_ATTESTATION", json_path)
    monkeypatch.setattr(
        validator, "MCP_RUNTIME_ATTESTATION_MARKDOWN", markdown_path
    )

    label = "JSON" if missing == "json" else "Markdown"
    with pytest.raises(validator.EvaluationError, match=f"attestation {label} is missing"):
        validator.validate_checked_mcp_runtime_attestation({})


def test_checked_trace_attestation_rejects_markdown_drift(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_checked_attestation_fixture(
        validator,
        monkeypatch,
        tmp_path,
        markdown_text="# Drifted trace report\n",
    )

    with pytest.raises(validator.EvaluationError, match="Markdown differs"):
        validator.validate_checked_mcp_runtime_attestation({"answer_count": 90})


def test_rejected_finalizer_diagnostic_fails_closed_on_count_drift(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(validator.FINALIZER_COPY_DIAGNOSTIC.read_text(encoding="utf-8"))
    source["completed_rows"]["knowledge-only-control"] = 17
    tampered = tmp_path / "finalizer-copy-integrity-diagnostic.json"
    tampered.write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "FINALIZER_COPY_DIAGNOSTIC", tampered)

    with pytest.raises(validator.EvaluationError, match="completed-row counts"):
        validator.validate_finalizer_copy_integrity_diagnostic()


def test_rejected_host_publication_diagnostic_is_closed_and_nonbenchmark(
    validator: ModuleType,
) -> None:
    report = validator.validate_host_publication_mutation_diagnostic()

    assert report["status"] == "rejected"
    assert report["evidence_class"] == "diagnostic-only-non-benchmark"
    assert report["comparison"]["benchmark_eligible"] is False
    assert report["aggregates"]["host_publication_mutation_row_count"] == 3
    assert report["aggregates"]["mutated_field_count"] == 6


def test_rejected_host_publication_diagnostic_fails_on_false_copy_integrity(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(
        validator.HOST_PUBLICATION_DIAGNOSTIC.read_text(encoding="utf-8")
    )
    source["rows"][0]["host_published_output"][
        "matches_confirmed_candidate"
    ] = True
    tampered = tmp_path / "host-publication-mutation-diagnostic.json"
    tampered.write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "HOST_PUBLICATION_DIAGNOSTIC", tampered)

    with pytest.raises(validator.EvaluationError, match="publication identity"):
        validator.validate_host_publication_mutation_diagnostic()


def test_rejected_source_provenance_diagnostic_is_closed_and_nonbenchmark(
    validator: ModuleType,
) -> None:
    report = validator.validate_source_provenance_drift_diagnostic()

    assert report["status"] == "rejected"
    assert report["evidence_class"] == "diagnostic-only-non-benchmark"
    assert report["comparison"]["benchmark_eligible"] is False
    assert report["persisted_rows"] == {
        "total": 12,
        "by_profile": {
            "knowledge-only-control": 4,
            "adaptive-consult-control": 4,
            "ensemble-consult-treatment": 4,
        },
        "quality_metrics_published": False,
    }


def test_rejected_source_provenance_diagnostic_cannot_publish_metrics(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(
        validator.SOURCE_PROVENANCE_DIAGNOSTIC.read_text(encoding="utf-8")
    )
    source["persisted_rows"]["quality_metrics_published"] = True
    tampered = tmp_path / "source-provenance-drift-diagnostic.json"
    tampered.write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "SOURCE_PROVENANCE_DIAGNOSTIC", tampered)

    with pytest.raises(validator.EvaluationError, match="persisted rows"):
        validator.validate_source_provenance_drift_diagnostic()


def test_rejected_candidate_copy_diagnostic_is_closed_and_nonbenchmark(
    validator: ModuleType,
) -> None:
    report = validator.validate_candidate_copy_failure_diagnostic()

    assert report["status"] == "rejected"
    assert report["comparison"]["benchmark_eligible"] is False
    assert report["observed_failure"]["classification"] == (
        "long-candidate-confirmation-copy-failure"
    )
    assert report["replacement_protocol"]["confirmation_argument"] == (
        "response_sha256"
    )
    assert report["persisted_rows"]["quality_metrics_published"] is False


def test_rejected_candidate_copy_diagnostic_rejects_digest_protocol_drift(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(
        validator.CANDIDATE_COPY_DIAGNOSTIC.read_text(encoding="utf-8")
    )
    source["replacement_protocol"]["confirmation_argument"] = "candidate_json"
    tampered = tmp_path / "candidate-copy-confirmation-failure-diagnostic.json"
    tampered.write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "CANDIDATE_COPY_DIAGNOSTIC", tampered)

    with pytest.raises(validator.EvaluationError, match="replacement protocol"):
        validator.validate_candidate_copy_failure_diagnostic()


def _write_mutated_json(source: Path, target: Path, mutation: object) -> None:
    report = json.loads(source.read_text(encoding="utf-8"))
    assert callable(mutation)
    mutation(report)
    target.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def test_rejected_skill_bootstrap_isolation_diagnostic_is_closed_and_noncausal(
    validator: ModuleType,
) -> None:
    report = validator.validate_skill_bootstrap_isolation_diagnostic()

    assert report["status"] == "rejected-diagnostic"
    assert report["scope"]["persisted_rows_at_stop"] == 17
    assert report["persisted_rows"] == {
        "knowledge-only-control": 6,
        "adaptive-consult-control": 6,
        "ensemble-consult-treatment": 5,
        "provider_response_errors": 0,
    }
    assert report["scope"]["accepted_benchmark_rows"] == 0
    assert report["scope"]["quality_metrics_published"] is False
    assert report["trigger"]["profile_id"] == "ensemble-consult-treatment"
    assert report["trigger"]["question_id"] == "q032-incremental-update-maturity"
    assert report["trigger"]["classification"] == (
        "uncontracted-skill-bootstrap-shell-read"
    )
    assert report["decision"]["causal_use"].startswith("None.")


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda report: report["persisted_rows"].__setitem__(
                "ensemble-consult-treatment", 6
            ),
            "row accounting",
        ),
        (
            lambda report: report["trigger"].__setitem__(
                "command_shape", "Get-Content C:/unisolated/SKILL.md"
            ),
            "q032 treatment shell-read",
        ),
        (
            lambda report: report["decision"].__setitem__(
                "causal_use", "Allowed in the aggregate."
            ),
            "causal-use decision",
        ),
    ],
)
def test_rejected_skill_bootstrap_isolation_diagnostic_fails_closed_on_mutation(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    mutation: object,
    message: str,
) -> None:
    tampered = tmp_path / "skill-bootstrap-isolation-diagnostic.json"
    _write_mutated_json(
        validator.SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC,
        tampered,
        mutation,
    )
    monkeypatch.setattr(
        validator, "SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC", tampered
    )

    with pytest.raises(validator.EvaluationError, match=message):
        validator.validate_skill_bootstrap_isolation_diagnostic()


def test_bootstrap_isolation_technical_preflight_is_closed_and_noncausal(
    validator: ModuleType,
) -> None:
    report = validator.validate_bootstrap_isolation_technical_preflight()

    assert report["status"] == "pass"
    assert report["evidence_class"] == "non-causal-technical-preflight"
    assert report["scope"]["causal_or_portfolio_metric"] is False
    assert report["scope"]["requested_answers"] == 1
    assert report["scope"]["completed_answers"] == 1
    assert report["runtime"]["command_execution_count"] == 0
    assert report["runtime"]["semantic_tool_order"] == [
        "semantic_okf_bootstrap_skill",
        "semantic_okf_inspect",
        *("semantic_okf_coverage_brief" for _ in range(5)),
        "semantic_okf_prepare_answer",
        "semantic_okf_confirm_answer",
    ]
    assert report["runtime"]["shell_isolation"]["shell_tool_disabled"] is True
    assert report["publication"]["published_equals_prepared_candidate"] is True
    assert report["publication"]["host_publication_correction_applied"] is True
    assert set(report["promptfoo_assertions"].values()) == {1}
    assert report["retained_raw_bindings"]["raw_artifacts_ignored"] is True
    assert not Path(
        report["retained_raw_bindings"]["promptfoo_results_path"]
    ).is_absolute()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda report: report["runtime"].__setitem__(
                "command_execution_count", 1
            ),
            "runtime counts",
        ),
        (
            lambda report: report["runtime"]["semantic_tool_order"].pop(2),
            "tool order",
        ),
        (
            lambda report: report["runtime"]["shell_isolation"].__setitem__(
                "shell_tool_disabled", False
            ),
            "shell receipt",
        ),
        (
            lambda report: report["publication"].__setitem__(
                "published_output_sha256", "0" * 64
            ),
            "publication digest binding",
        ),
        (
            lambda report: report["publication"].__setitem__(
                "host_publication_correction_applied", False
            ),
            "publication digest binding",
        ),
        (
            lambda report: report["promptfoo_assertions"].__setitem__(
                "atomic_answer_completeness", 0
            ),
            "assertions",
        ),
        (
            lambda report: report["retained_raw_bindings"].__setitem__(
                "promptfoo_results_path", "C:/private/raw/promptfoo-results.json"
            ),
            "raw bindings",
        ),
    ],
)
def test_bootstrap_isolation_technical_preflight_fails_closed_on_mutation(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    mutation: object,
    message: str,
) -> None:
    tampered = tmp_path / "bootstrap-isolation-technical-preflight.json"
    _write_mutated_json(
        validator.BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT,
        tampered,
        mutation,
    )
    monkeypatch.setattr(
        validator, "BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT", tampered
    )

    with pytest.raises(validator.EvaluationError, match=message):
        validator.validate_bootstrap_isolation_technical_preflight()


def test_bootstrap_compact_reports_reject_machine_absolute_paths(
    validator: ModuleType,
) -> None:
    with pytest.raises(validator.EvaluationError, match="absolute path"):
        validator._reject_absolute_paths(
            {"raw": {"path": "C:/private/raw/result.json"}},
            "bootstrap fixture",
        )


def test_reviewed_answer_benchmark_rebuild_is_exact_and_complete(
    validator: ModuleType,
) -> None:
    reviewed = validator.validate_reviewed_benchmark()

    assert reviewed["manifest"]["benchmark_id"] == (
        "semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1"
    )
    assert reviewed["manifest"]["audit_summary"]["reviewed_expected_id_links"] == 113
    assert reviewed["manifest"]["audit_summary"][
        "reviewed_unique_expected_claim_ids"
    ] == 68
    assert len(reviewed["ground_truth"]) == 10


def test_final_build_report_schema_fails_closed(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(validator.BUILD_VALIDATION.read_text(encoding="utf-8"))
    source["unexpected"] = True
    tampered = tmp_path / "build-validation.json"
    tampered.write_text(json.dumps(source), encoding="utf-8")
    monkeypatch.setattr(validator, "BUILD_VALIDATION", tampered)

    plan = validator.validate_builder_plan()
    with pytest.raises(validator.EvaluationError, match="closed schema"):
        validator.validate_final_integrity_reports(plan)


def test_manual_report_rejects_changed_draft_binding(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(validator.MANUAL_VERIFICATION.read_text(encoding="utf-8"))
    source["finalizer"]["draft_sha256"] = "0" * 64
    tampered = tmp_path / "manual-verification.json"
    tampered.write_text(json.dumps(source), encoding="utf-8")
    monkeypatch.setattr(validator, "MANUAL_VERIFICATION", tampered)

    plan = validator.validate_builder_plan()
    with pytest.raises(validator.EvaluationError, match="draft binding"):
        validator.validate_final_integrity_reports(plan)


def test_skill_arena_manifest_rejects_stale_skill_tree_binding(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(validator.SKILL_ARENA_MANIFEST.read_text(encoding="utf-8"))
    source["consult_skills"][1]["tree_sha256"] = "0" * 64
    tampered = tmp_path / "config-manifest.json"
    tampered.write_text(json.dumps(source), encoding="utf-8")
    monkeypatch.setattr(validator, "SKILL_ARENA_MANIFEST", tampered)

    with pytest.raises(validator.EvaluationError, match="skill tree SHA-256"):
        validator.validate_skill_arena_manifest()


def test_accepted_coverage_report_rejects_stale_runtime_tree_binding(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(validator.COVERAGE_REPORT.read_text(encoding="utf-8"))
    source["inputs"]["runtime_tree_sha256"] = "0" * 64
    tampered = tmp_path / "coverage-report.json"
    tampered.write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "COVERAGE_REPORT", tampered)

    with pytest.raises(validator.EvaluationError, match="runtime tree SHA-256"):
        validator.validate_accepted_coverage_report(validator.validate_builder_plan())


def test_accepted_coverage_report_rejects_changed_historical_runtime_binding(
    validator: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = json.loads(validator.COVERAGE_REPORT.read_text(encoding="utf-8"))
    source["inputs"]["runtime_sha256"] = "0" * 64
    tampered = tmp_path / "coverage-report.json"
    tampered.write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(validator, "COVERAGE_REPORT", tampered)

    with pytest.raises(validator.EvaluationError, match="runtime SHA-256"):
        validator.validate_accepted_coverage_report(validator.validate_builder_plan())


def test_accepted_diversified_coverage_report_closes_all_reviewed_groups(
    validator: ModuleType,
) -> None:
    report = validator.validate_accepted_coverage_report(
        validator.validate_builder_plan()
    )

    assert report["candidate"] == (
        "definitive-ensemble-quality-paper-diversified-publication-gate-v1"
    )
    assert report["metrics"]["group_counts"]["answer_claims"] == {
        "total": 44,
        "adaptive_covered": 39,
        "graph_covered": 24,
        "embedding_covered": 39,
        "union_covered": 44,
    }
    assert report["metrics"]["group_counts"]["important_negatives"] == {
        "total": 13,
        "adaptive_covered": 13,
        "graph_covered": 11,
        "embedding_covered": 13,
        "union_covered": 13,
    }
