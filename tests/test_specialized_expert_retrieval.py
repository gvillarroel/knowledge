"""Tests for replicated direct retrieval from generated specialized experts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_EXPERT = (
    REPO_ROOT
    / "skills"
    / "build-specialized-skill"
    / "scripts"
    / "build_specialized_skill.py"
)
EVALUATE = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "scripts"
    / "evaluate_direct_retrieval.py"
)
AUDIT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "scripts"
    / "audit_direct_retrieval.py"
)
TRACE_QUERY_TEMPLATE = (
    REPO_ROOT
    / "skills"
    / "build-specialized-skill"
    / "assets"
    / "expert-template"
    / "query_expert_knowledge_trace_bm25.py"
)
IMPROVED_AUDIT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "scripts"
    / "audit_improved_retrieval.py"
)


def _run(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *map(str, arguments)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _write_knowledge(root: Path) -> Path:
    knowledge = root / "knowledge"
    concept = (
        knowledge
        / "concepts"
        / "paper-2404-16130v2"
        / "sources-markdown-2404-16130v2.md"
    )
    concept.parent.mkdir(parents=True)
    body = (
        "# Graph retrieval evidence\n\n"
        "Graph retrieval uses hierarchical evidence for global questions. "
        "The evidence mechanism preserves source identity.\n"
    )
    claim_body = (
        "# Reviewed graph retrieval claim\n\n"
        "Graph retrieval preserves evidence identity in the reviewed claim set.\n"
    )
    concept.write_text(body, encoding="utf-8", newline="\n")
    claim_concept = (
        knowledge
        / "concepts"
        / "claims-2404-16130v2"
        / "sources-claims-2404-16130v2.md"
    )
    claim_concept.parent.mkdir(parents=True)
    claim_concept.write_text(claim_body, encoding="utf-8", newline="\n")
    (knowledge / "index.md").write_text(
        "# Test GraphRAG knowledge\n",
        encoding="utf-8",
        newline="\n",
    )
    semantic = knowledge / "semantic"
    semantic.mkdir()
    (semantic / "build-report.json").write_text(
        json.dumps(
            {
                "status": "pass",
                "valid": True,
                "summary": {"records": 2},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    records = [
        {
            "source_id": "paper-2404-16130v2",
            "record_id": "sources/markdown/2404.16130v2",
            "concept_id": "concepts/paper-2404-16130v2/test",
            "concept_path": concept.relative_to(knowledge).as_posix(),
            "concept_type": "Research Paper",
            "source_path": "sources/markdown/2404.16130v2.md",
            "record_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "title": "Graph retrieval evidence",
            "body": body,
        },
        {
            "source_id": "claims-2404-16130v2",
            "record_id": "sources/claims/2404.16130v2",
            "concept_id": "concepts/claims-2404-16130v2/test",
            "concept_path": claim_concept.relative_to(knowledge).as_posix(),
            "concept_type": "Reviewed Research Claims",
            "source_path": "sources/claims/2404.16130v2.jsonl",
            "record_sha256": hashlib.sha256(
                claim_body.encode("utf-8")
            ).hexdigest(),
            "title": "Reviewed graph retrieval claim",
            "body": claim_body,
        },
    ]
    (semantic / "records.jsonl").write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )
    return knowledge


def _write_guidance(path: Path, *, label: str) -> None:
    path.write_text(
        f"""# {label}

## Scope

Answer GraphRAG mechanism questions only from the bundled research record.

## Application workflow

Verify the expert, search with the complete question, open the selected record,
and cite the exact concept path beside the answer.

## Decision rules

Prefer direct mechanism evidence, retain source identity, and distinguish quoted
facts from comparisons or other inferences.

## Evidence and limits

Use only the embedded record and stop when it does not support the requested
conclusion. Never replace missing evidence with external knowledge.
""",
        encoding="utf-8",
        newline="\n",
    )


def _write_questions(path: Path) -> None:
    rows = [
        {
            "id": f"q{index:03d}",
            "question": "How does graph retrieval preserve evidence identity?",
            "qrels": {
                "paper_ids": ["2404.16130v2"],
                "source_ids": ["paper-2404-16130v2"],
            },
        }
        for index in range(1, 41)
    ]
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _build_expert(
    knowledge: Path,
    guidance: Path,
    output: Path,
    *,
    query_template: Path | None = None,
) -> None:
    arguments: list[object] = [
        BUILD_EXPERT,
        knowledge,
        output,
        "--name",
        output.name,
        "--description",
        "Answer GraphRAG mechanism questions from bundled evidence.",
        "--guidance",
        guidance,
    ]
    if query_template is not None:
        arguments.extend(("--query-template", query_template))
    result = _run(*arguments)
    assert result.returncode == 0, result.stderr


def _evaluate(
    *,
    expert: Path,
    builder: Path,
    questions: Path,
    trace_evidence: Path,
    top_k: int,
    root: Path,
    stem: str,
) -> Path:
    output_json = root / f"{stem}.json"
    output_markdown = root / f"{stem}.md"
    result = _run(
        EVALUATE,
        "--expert",
        expert,
        "--builder-skill",
        builder,
        "--trace-evidence",
        trace_evidence,
        "--questions",
        questions,
        "--top-k",
        top_k,
        "--output-json",
        output_json,
        "--output-markdown",
        output_markdown,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["selected_metrics"]["evidence_validity"]["ratio"] == 1.0
    assert payload["selected_metrics"]["all_40"]["recall_at_10"] == 1.0
    assert all(row["hit_count"] == 1 for row in payload["routes"][0]["queries"])
    assert not any(
        path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
        for path in expert.rglob("*")
    )
    return output_json


def test_replicated_experts_are_rankable_under_the_same_direct_contract(
    tmp_path: Path,
) -> None:
    """Two guidance variants reproduce exact retrieval and one table position."""

    knowledge = _write_knowledge(tmp_path)
    guidance_v39 = tmp_path / "guidance-v39.md"
    guidance_v42 = tmp_path / "guidance-v42.md"
    _write_guidance(guidance_v39, label="GraphRAG Expert v39")
    _write_guidance(guidance_v42, label="GraphRAG Expert v42")
    expert_v39 = tmp_path / "graphrag-expert-v39"
    expert_v42 = tmp_path / "graphrag-expert-v42"
    _build_expert(knowledge, guidance_v39, expert_v39)
    _build_expert(knowledge, guidance_v42, expert_v42)

    builder = tmp_path / "builder"
    builder.mkdir()
    (builder / "SKILL.md").write_text(
        "---\nname: fixture-builder\ndescription: Fixture builder.\n---\n",
        encoding="utf-8",
        newline="\n",
    )
    questions = tmp_path / "questions.jsonl"
    _write_questions(questions)
    trace_v39 = tmp_path / "trace-v39.json"
    trace_v42 = tmp_path / "trace-v42.json"
    trace_v39.write_text('{"proposal": "v39"}\n', encoding="utf-8", newline="\n")
    trace_v42.write_text('{"proposal": "v42"}\n', encoding="utf-8", newline="\n")
    runs = tmp_path / "runs"
    runs.mkdir()
    v39_top10 = _evaluate(
        expert=expert_v39,
        builder=builder,
        questions=questions,
        trace_evidence=trace_v39,
        top_k=10,
        root=runs,
        stem="v39-top10",
    )
    v42_top10 = _evaluate(
        expert=expert_v42,
        builder=builder,
        questions=questions,
        trace_evidence=trace_v42,
        top_k=10,
        root=runs,
        stem="v42-top10",
    )
    v39_pool100 = _evaluate(
        expert=expert_v39,
        builder=builder,
        questions=questions,
        trace_evidence=trace_v39,
        top_k=100,
        root=runs,
        stem="v39-pool100",
    )
    v42_pool100 = _evaluate(
        expert=expert_v42,
        builder=builder,
        questions=questions,
        trace_evidence=trace_v42,
        top_k=100,
        root=runs,
        stem="v42-pool100",
    )

    reference = tmp_path / "reference-comparison.json"
    reference.write_text(
        json.dumps(
            {
                "schema_version": "final-report-comparison/1.0",
                "report": "reference.md",
                "heading": "## Direct comparison",
                "dataset_scope": {
                    "candidate_budget": "top-10",
                    "cohort": "all-40",
                    "dataset_id": "graphrag-papers-40",
                    "identity_grouping": "authoritative-paper",
                    "metric_contract": "graphrag-direct-retrieval/1.0",
                },
                "metrics": [
                    {
                        "id": "recall_at_10",
                        "label": "Recall@10",
                        "aggregation": "mean",
                        "unit": "percent",
                        "direction": "higher",
                        "display_precision": 2,
                    },
                    {
                        "id": "ndcg_at_10",
                        "label": "nDCG@10",
                        "aggregation": "mean",
                        "unit": "percent",
                        "direction": "higher",
                        "display_precision": 2,
                    },
                    {
                        "id": "p95_latency_ms",
                        "label": "P95",
                        "aggregation": "percentile_95",
                        "unit": "ms",
                        "direction": "lower",
                        "display_precision": 2,
                    },
                ],
                "alternatives": [
                    {
                        "id": "fixture-baseline",
                        "label": "Fixture baseline",
                        "metrics": {
                            "recall_at_10": 50.0,
                            "ndcg_at_10": 50.0,
                            "p95_latency_ms": 1.0,
                        },
                    },
                    {
                        "id": "specialized-expert-lexical",
                        "label": "Specialized expert lexical",
                        "metrics": {
                            "recall_at_10": 0.0,
                            "ndcg_at_10": 0.0,
                            "p95_latency_ms": 999.0,
                        },
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    audit_json = tmp_path / "audit.json"
    audit_markdown = tmp_path / "audit.md"
    comparison = tmp_path / "audit.comparison.json"
    result = _run(
        AUDIT,
        "--v39-top10",
        v39_top10,
        "--v42-top10",
        v42_top10,
        "--v39-pool100",
        v39_pool100,
        "--v42-pool100",
        v42_pool100,
        "--reference-comparison",
        reference,
        "--output-json",
        audit_json,
        "--output-markdown",
        audit_markdown,
        "--output-comparison",
        comparison,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(audit_json.read_text(encoding="utf-8"))
    assert payload["position"] == 1
    assert payload["alternative_count"] == 2
    assert payload["replication"]["exact_top10_across_experts"] is True


def test_trace_bm25_expert_supports_a_noncanonical_development_scope(
    tmp_path: Path,
) -> None:
    """Subset evaluation reports its frozen adapter and stays ranking-ineligible."""

    knowledge = _write_knowledge(tmp_path)
    guidance = tmp_path / "guidance.md"
    _write_guidance(guidance, label="GraphRAG Trace BM25 Expert")
    expert = tmp_path / "graphrag-trace-bm25-expert"
    _build_expert(
        knowledge,
        guidance,
        expert,
        query_template=TRACE_QUERY_TEMPLATE,
    )
    builder = tmp_path / "builder"
    builder.mkdir()
    (builder / "SKILL.md").write_text(
        "---\nname: fixture-builder\ndescription: Fixture builder.\n---\n",
        encoding="utf-8",
        newline="\n",
    )
    questions = tmp_path / "questions.jsonl"
    _write_questions(questions)
    development_questions = tmp_path / "development-questions.jsonl"
    development_questions.write_text(
        "\n".join(questions.read_text(encoding="utf-8").splitlines()[:2]) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    output_json = tmp_path / "development.json"
    output_markdown = tmp_path / "development.md"

    result = _run(
        EVALUATE,
        "--expert",
        expert,
        "--builder-skill",
        builder,
        "--questions",
        development_questions,
        "--expected-question-count",
        2,
        "--question-id",
        "q001",
        "--question-id",
        "q002",
        "--scope-label",
        "trace-development-2",
        "--top-k",
        10,
        "--output-json",
        output_json,
        "--output-markdown",
        output_markdown,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["query_count"] == 2
    assert payload["ranking_eligible"] is False
    assert payload["evaluation_scope"]["label"] == "trace-development-2"
    assert payload["selected_route"] == "specialized_expert_trace_bm25"
    assert payload["metric_contract"]["retrieval_contract_id"] == (
        "trace-bm25-field-fusion-v1"
    )
    assert payload["selected_metrics"]["scope"]["recall_at_10"] == 1.0

    trace_first = tmp_path / "trace-first.json"
    trace_second = tmp_path / "trace-second.json"
    trace_first.write_text('{"proposal": "first"}\n', encoding="utf-8", newline="\n")
    trace_second.write_text(
        '{"proposal": "second"}\n',
        encoding="utf-8",
        newline="\n",
    )

    def run_canonical(top_k: int, stem: str) -> Path:
        report_json = tmp_path / f"{stem}.json"
        report_markdown = tmp_path / f"{stem}.md"
        evaluated = _run(
            EVALUATE,
            "--expert",
            expert,
            "--builder-skill",
            builder,
            "--packager-skill",
            builder,
            "--trace-evidence",
            trace_first,
            "--trace-evidence",
            trace_second,
            "--questions",
            questions,
            "--top-k",
            top_k,
            "--output-json",
            report_json,
            "--output-markdown",
            report_markdown,
        )
        assert evaluated.returncode == 0, evaluated.stdout + evaluated.stderr
        return report_json

    top10 = run_canonical(10, "trace-top10")
    pool100 = run_canonical(100, "trace-pool100")
    reference = tmp_path / "improved-reference.json"
    reference.write_text(
        json.dumps(
            {
                "schema_version": "final-report-comparison/1.0",
                "report": "reference.md",
                "heading": "## Direct comparison",
                "dataset_scope": {
                    "candidate_budget": "top-10",
                    "cohort": "all-40",
                    "dataset_id": "graphrag-papers-40",
                    "identity_grouping": "authoritative-paper",
                    "metric_contract": "graphrag-direct-retrieval/1.0",
                },
                "metrics": [
                    {
                        "id": "recall_at_10",
                        "label": "Recall@10",
                        "aggregation": "mean",
                        "unit": "percent",
                        "direction": "higher",
                        "display_precision": 2,
                    },
                    {
                        "id": "ndcg_at_10",
                        "label": "nDCG@10",
                        "aggregation": "mean",
                        "unit": "percent",
                        "direction": "higher",
                        "display_precision": 2,
                    },
                    {
                        "id": "p95_latency_ms",
                        "label": "P95",
                        "aggregation": "percentile_95",
                        "unit": "ms",
                        "direction": "lower",
                        "display_precision": 2,
                    },
                ],
                "alternatives": [
                    {
                        "id": "fixture-baseline",
                        "label": "Fixture baseline",
                        "metrics": {
                            "recall_at_10": 90.0,
                            "ndcg_at_10": 90.0,
                            "p95_latency_ms": 1.0,
                        },
                    },
                    {
                        "id": "specialized-expert-lexical",
                        "label": "Specialized expert lexical",
                        "metrics": {
                            "recall_at_10": 50.0,
                            "ndcg_at_10": 50.0,
                            "p95_latency_ms": 2.0,
                        },
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    audit_json = tmp_path / "improved-audit.json"
    audit_markdown = tmp_path / "improved-audit.md"
    comparison = tmp_path / "improved-audit.comparison.json"
    audited = _run(
        IMPROVED_AUDIT,
        "--candidate-top10",
        top10,
        "--candidate-pool100",
        pool100,
        "--reference-comparison",
        reference,
        "--output-json",
        audit_json,
        "--output-markdown",
        audit_markdown,
        "--output-comparison",
        comparison,
    )
    assert audited.returncode == 0, audited.stdout + audited.stderr
    audit_payload = json.loads(audit_json.read_text(encoding="utf-8"))
    assert audit_payload["position"] == 1
    assert audit_payload["previous_position"] == 2
    assert audit_payload["validation"]["exact_top10_prefix_in_pool100"] is True

    custom_audit_json = tmp_path / "custom-improved-audit.json"
    custom_audit_markdown = tmp_path / "custom-improved-audit.md"
    custom_comparison = tmp_path / "custom-improved-audit.comparison.json"
    custom = _run(
        IMPROVED_AUDIT,
        "--candidate-top10",
        top10,
        "--candidate-pool100",
        pool100,
        "--reference-comparison",
        reference,
        "--candidate-id",
        "specialized-expert-v44-fixture",
        "--candidate-label",
        "Specialized expert v44 fixture",
        "--superseded-id",
        "specialized-expert-lexical",
        "--expected-route",
        "specialized_expert_trace_bm25",
        "--expected-retrieval-contract",
        "trace-bm25-field-fusion-v1",
        "--output-json",
        custom_audit_json,
        "--output-markdown",
        custom_audit_markdown,
        "--output-comparison",
        custom_comparison,
    )
    assert custom.returncode == 0, custom.stdout + custom.stderr
    custom_payload = json.loads(custom_audit_json.read_text(encoding="utf-8"))
    assert custom_payload["candidate_id"] == "specialized-expert-v44-fixture"
    assert custom_payload["candidate_label"] == "Specialized expert v44 fixture"
