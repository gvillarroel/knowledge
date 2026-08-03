"""Tests for retrospective supervised-profile expert construction."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
)
BUILD_PROFILE = EVALUATION_ROOT / "scripts" / "build_supervised_profile_index.py"
QUERY_TEMPLATE = (
    EVALUATION_ROOT
    / "adapters"
    / "query_expert_knowledge_supervised_profiles.py"
)
BUILD_EXPERT = (
    REPO_ROOT
    / "skills"
    / "build-specialized-skill"
    / "scripts"
    / "build_specialized_skill.py"
)
EVALUATE = EVALUATION_ROOT / "scripts" / "evaluate_definitive_expert.py"


def _run(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *map(str, arguments)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _write_knowledge(root: Path) -> Path:
    knowledge = root / "knowledge"
    concepts = knowledge / "concepts"
    concepts.mkdir(parents=True)
    rows = []
    fixtures = (
        (
            "astro-doc-server",
            "guides/on-demand-rendering",
            "On-demand rendering",
            (
                "Configure server output and install a deployment adapter before "
                "using request-time APIs."
            ),
        ),
        (
            "astro-doc-content",
            "guides/content-collections",
            "Content collections",
            (
                "Define a content collection loader and schema, then query entries "
                "through the content APIs."
            ),
        ),
    )
    for source_id, record_id, title, body in fixtures:
        concept_path = f"concepts/{source_id}.md"
        (knowledge / concept_path).write_text(
            f"# {title}\n\n{body}\n",
            encoding="utf-8",
            newline="\n",
        )
        rows.append(
            {
                "source_id": source_id,
                "record_id": record_id,
                "title": title,
                "body": body,
                "concept_id": f"concepts/{source_id}",
                "concept_path": concept_path,
                "concept_type": "Astro Documentation Page",
                "source_path": f"sources/{record_id}.mdx",
                "record_sha256": hashlib.sha256(body.encode()).hexdigest(),
            }
        )
    (knowledge / "index.md").write_text(
        "# Fixture knowledge\n",
        encoding="utf-8",
        newline="\n",
    )
    semantic = knowledge / "semantic"
    semantic.mkdir()
    (semantic / "build-report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
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
    (semantic / "records.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    return knowledge


def _write_questions(path: Path) -> None:
    rows = []
    for index in range(1, 41):
        server = index % 2 == 1
        rows.append(
            {
                "id": f"q{index:03d}",
                "question": (
                    "How do I configure server output and a deployment adapter?"
                    if server
                    else "How do content collection loaders and schemas work?"
                ),
                "question_type": "direct" if index <= 30 else "hard",
                "qrels": {
                    "document_ids": [
                        "/en/guides/on-demand-rendering/"
                        if server
                        else "/en/guides/content-collections/"
                    ],
                    "source_ids": [
                        "astro-doc-server"
                        if server
                        else "astro-doc-content"
                    ],
                },
            }
        )
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _write_guidance(path: Path) -> None:
    path.write_text(
        """# Astro Fixture Expert

## Scope

Answer only server-rendering and content-collection questions from the fixture.

## Application workflow

Search with the complete question, select an exact record, and cite its concept.

## Decision rules

Keep server output separate from content loaders and preserve source identity.

## Evidence and limits

Use only exact embedded evidence and state when the fixture lacks an answer.
The retrospective profile is a discovery aid and is not holdout evidence.
""",
        encoding="utf-8",
        newline="\n",
    )


def _write_graph_knowledge(root: Path) -> Path:
    knowledge = root / "graph-knowledge"
    rows = []
    for paper_id, topic in (
        ("2404.16130v2", "community reports for global questions"),
        ("2402.07630v3", "connected subgraphs for local questions"),
    ):
        for prefix in ("claims", "paper"):
            source_id = f"{prefix}-{paper_id}"
            record_id = f"sources/{prefix}/{paper_id}"
            concept_path = f"concepts/{source_id}.md"
            body = f"{paper_id} uses {topic}."
            target = knowledge / concept_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                f"# {paper_id} {prefix}\n\n{body}\n",
                encoding="utf-8",
                newline="\n",
            )
            rows.append(
                {
                    "source_id": source_id,
                    "record_id": record_id,
                    "title": f"{paper_id} {prefix}",
                    "body": body,
                    "concept_id": f"concepts/{source_id}",
                    "concept_path": concept_path,
                    "concept_type": (
                        "Reviewed Research Claims"
                        if prefix == "claims"
                        else "Research Paper"
                    ),
                    "source_path": f"{record_id}.md",
                    "record_sha256": hashlib.sha256(body.encode()).hexdigest(),
                }
            )
    (knowledge / "index.md").write_text(
        "# Graph fixture\n",
        encoding="utf-8",
        newline="\n",
    )
    semantic = knowledge / "semantic"
    semantic.mkdir()
    (semantic / "build-report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "pass",
                "valid": True,
                "summary": {"records": 4},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (semantic / "records.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    return knowledge


def _write_graph_questions(path: Path) -> None:
    rows = []
    for index in range(1, 41):
        community = index % 2 == 1
        paper_id = "2404.16130v2" if community else "2402.07630v3"
        rows.append(
            {
                "id": f"q{index:03d}",
                "question": (
                    "Which method uses community reports for global questions?"
                    if community
                    else "Which method retrieves connected local subgraphs?"
                ),
                "qrels": {
                    "paper_ids": [paper_id],
                    "source_ids": [
                        f"claims-{paper_id}",
                        f"paper-{paper_id}",
                    ],
                },
            }
        )
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def test_profile_index_is_reproducible_and_has_no_exact_question_lookup(
    tmp_path: Path,
) -> None:
    """The all-exposed profile is explicit, deterministic, and feature based."""

    knowledge = _write_knowledge(tmp_path)
    questions = tmp_path / "questions.jsonl"
    _write_questions(questions)
    output = tmp_path / "expert_routing_index.json"
    built = _run(
        BUILD_PROFILE,
        "--dataset-id",
        "astro-40",
        "--knowledge",
        knowledge,
        "--questions",
        questions,
        "--output",
        output,
    )
    assert built.returncode == 0, built.stdout + built.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["candidate_state"] == (
        "retrospective-all-exposed-supervised-profile"
    )
    assert payload["promotion_eligible"] is False
    assert payload["retrieval"]["exact_question_lookup"] is False
    assert payload["summary"]["profile_count"] == 2
    assert payload["summary"]["supervised_profile_count"] == 2
    assert not any("question" in key for key in payload if key == "lookup")

    checked = _run(
        BUILD_PROFILE,
        "--dataset-id",
        "astro-40",
        "--knowledge",
        knowledge,
        "--questions",
        questions,
        "--output",
        output,
        "--check",
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert json.loads(checked.stdout)["status"] == "pass"


def test_packaged_profile_expert_ranks_and_verifies_exact_evidence(
    tmp_path: Path,
) -> None:
    """A packaged profile expert ranks the right record and rejects index drift."""

    knowledge = _write_knowledge(tmp_path)
    questions = tmp_path / "questions.jsonl"
    _write_questions(questions)
    profile = tmp_path / "expert_routing_index.json"
    assert _run(
        BUILD_PROFILE,
        "--dataset-id",
        "astro-40",
        "--knowledge",
        knowledge,
        "--questions",
        questions,
        "--output",
        profile,
    ).returncode == 0
    guidance = tmp_path / "guidance.md"
    _write_guidance(guidance)
    expert = tmp_path / "astro-fixture-profile-expert"
    built = _run(
        BUILD_EXPERT,
        knowledge,
        expert,
        "--name",
        expert.name,
        "--description",
        "Answer Astro fixture questions through supervised lexical profiles.",
        "--guidance",
        guidance,
        "--query-template",
        QUERY_TEMPLATE,
        "--query-support",
        profile,
    )
    assert built.returncode == 0, built.stdout + built.stderr

    queried = _run(
        expert / "scripts" / "query_expert_knowledge.py",
        "search",
        "--contains",
        "How do content collection loaders and schemas work?",
        "--limit",
        2,
        "--show-content",
    )
    assert queried.returncode == 0, queried.stdout + queried.stderr
    payload = json.loads(queried.stdout)
    assert payload["verification"]["promotion_eligible"] is False
    assert payload["results"][0]["source_id"] == "astro-doc-content"
    assert payload["results"][0]["score"] > 0
    assert payload["results"][0]["locator"] == {"kind": "record"}

    support = expert / "scripts" / "expert_routing_index.json"
    support.write_text(
        support.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
        newline="\n",
    )
    rejected = _run(
        expert / "scripts" / "query_expert_knowledge.py",
        "verify",
    )
    assert rejected.returncode == 2
    assert "digest drift" in rejected.stdout


def test_graphrag_helper_deduplicates_papers_and_matches_harbor_fields(
    tmp_path: Path,
) -> None:
    """Normal GraphRAG CLI output contains unique papers and no debug fields."""

    knowledge = _write_graph_knowledge(tmp_path)
    questions = tmp_path / "graph-questions.jsonl"
    _write_graph_questions(questions)
    profile = tmp_path / "expert_routing_index.json"
    generated = _run(
        BUILD_PROFILE,
        "--dataset-id",
        "graphrag-papers-40",
        "--knowledge",
        knowledge,
        "--questions",
        questions,
        "--output",
        profile,
    )
    assert generated.returncode == 0, generated.stdout + generated.stderr
    guidance = tmp_path / "graph-guidance.md"
    _write_guidance(guidance)
    expert = tmp_path / "graph-fixture-profile-expert"
    built = _run(
        BUILD_EXPERT,
        knowledge,
        expert,
        "--name",
        expert.name,
        "--description",
        "Answer GraphRAG fixture questions through supervised lexical profiles.",
        "--guidance",
        guidance,
        "--query-template",
        QUERY_TEMPLATE,
        "--query-support",
        profile,
    )
    assert built.returncode == 0, built.stdout + built.stderr

    query = _run(
        expert / "scripts" / "query_expert_knowledge.py",
        "search",
        "--contains",
        "Which method uses community reports for global questions?",
        "--limit",
        2,
    )
    assert query.returncode == 0, query.stdout + query.stderr
    results = json.loads(query.stdout)["results"]
    assert len(results) == 2
    paper_ids = {
        result["source_id"].split("-", 1)[1]
        for result in results
    }
    assert paper_ids == {"2404.16130v2", "2402.07630v3"}
    assert all(
        set(result)
        == {
            "concept_id",
            "concept_path",
            "concept_type",
            "record_id",
            "record_sha256",
            "score",
            "source_id",
            "source_path",
            "title",
        }
        for result in results
    )


def test_improvement_gate_requires_quality_latency_and_exact_evidence() -> None:
    """The final gate rejects regressions, slowdowns, and evidence loss."""

    module = _load_module("definitive_evaluator_fixture", EVALUATE)
    baseline = {
        "metrics": {
            "recall_at_10": 0.8,
            "mrr_at_10": 0.9,
            "ndcg_at_10": 0.85,
        },
        "p95_ms": 1000.0,
    }
    passing = module._improvement_gate(
        {
            "recall_at_10": 0.9,
            "mrr_at_10": 0.9,
            "ndcg_at_10": 0.9,
        },
        100.0,
        1.0,
        baseline,
    )
    assert passing["status"] == "pass"
    assert passing["latency_ms"]["ratio"] == 0.1

    for metrics, p95_ms, evidence in (
        (
            {
                "recall_at_10": 0.7,
                "mrr_at_10": 1.0,
                "ndcg_at_10": 0.9,
            },
            100.0,
            1.0,
        ),
        (
            {
                "recall_at_10": 0.9,
                "mrr_at_10": 0.9,
                "ndcg_at_10": 0.9,
            },
            1000.0,
            1.0,
        ),
        (
            {
                "recall_at_10": 0.9,
                "mrr_at_10": 0.9,
                "ndcg_at_10": 0.9,
            },
            100.0,
            0.99,
        ),
    ):
        assert module._improvement_gate(
            metrics,
            p95_ms,
            evidence,
            baseline,
        )["status"] == "fail"
