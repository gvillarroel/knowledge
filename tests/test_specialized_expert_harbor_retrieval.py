"""Tests for Harbor-native specialized-expert retrieval evaluation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "scripts"
    / "generate_harbor_retrieval_tasks.py"
)
SCORER = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "harbor"
    / "grader"
    / "score.py"
)


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _run(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *map(str, arguments)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _record(index: int) -> dict[str, Any]:
    paper_id = f"paper-{index:02d}"
    body = f"Authoritative body for {paper_id}."
    return {
        "source_id": f"paper-{paper_id}",
        "record_id": f"records/{paper_id}",
        "concept_id": f"concepts/{paper_id}/record",
        "concept_path": f"concepts/{paper_id}/record.md",
        "concept_type": "Research Paper",
        "source_path": f"sources/{paper_id}.md",
        "record_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "title": f"Paper {index:02d}",
        "body": body,
    }


def _result(record: dict[str, Any], score: float) -> dict[str, Any]:
    return {
        field: record[field]
        for field in (
            "concept_id",
            "concept_path",
            "concept_type",
            "record_id",
            "record_sha256",
            "source_id",
            "source_path",
            "title",
        )
    } | {"score": score}


def _write_expert(root: Path) -> tuple[Path, list[dict[str, Any]]]:
    expert = root / "fixture-expert"
    ledger = expert / "references" / "knowledge" / "semantic" / "records.jsonl"
    ledger.parent.mkdir(parents=True)
    records = [_record(index) for index in range(1, 11)]
    ledger.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )
    (expert / "expert-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "semantic-okf-expert-skill/1.0",
                "skill_name": expert.name,
                "knowledge": {
                    "record_count": len(records),
                    "tree": {
                        "file_count": 1,
                        "sha256": "a" * 64,
                    },
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return expert, records


def _write_questions(path: Path) -> None:
    rows = [
        {
            "id": "q001-first",
            "question": "Which papers support the first mechanism?",
            "qrels": {"paper_ids": ["paper-01", "paper-03"], "source_ids": []},
        },
        {
            "id": "q002-second",
            "question": "Which papers support the second mechanism?",
            "qrels": {"paper_ids": ["paper-02"], "source_ids": []},
        },
        {
            "id": "q003-holdout",
            "question": "Which paper is reserved for the holdout?",
            "qrels": {"paper_ids": ["paper-04"], "source_ids": []},
        },
    ]
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def test_generator_seals_disjoint_tasks_and_rebuilds_exactly(tmp_path: Path) -> None:
    """The native task tree is complete, disjoint, and deterministic."""

    expert, _ = _write_expert(tmp_path)
    questions = tmp_path / "questions.jsonl"
    _write_questions(questions)
    output = tmp_path / "tasks"
    arguments: list[object] = [
        GENERATOR,
        "--expert",
        expert,
        "--questions",
        questions,
        "--development-id",
        "q001",
        "--development-id",
        "q002",
        "--holdout-id",
        "q003",
        "--output",
        output,
    ]

    generated = _run(*arguments)

    assert generated.returncode == 0, generated.stdout + generated.stderr
    assert (output / "dataset-manifest.json").is_file()
    assert (
        output
        / "development"
        / "q001-first"
        / "tests"
        / "score.py"
    ).is_file()
    instruction = (
        output / "development" / "q001-first" / "instruction.md"
    ).read_text(encoding="utf-8")
    assert "qrels" not in instruction
    assert "/root/.agents/skills/fixture-expert/" in instruction
    assert "> /logs/agent/retrieval.json" in instruction
    task_toml = (
        output / "development" / "q001-first" / "task.toml"
    ).read_text(encoding="utf-8")
    assert "/logs/agent/retrieval.json" in task_toml

    checked = _run(*arguments, "--check")

    assert checked.returncode == 0, checked.stdout + checked.stderr


def test_generator_rejects_development_holdout_overlap(tmp_path: Path) -> None:
    """One task cannot enter both optimizer-visible and holdout cohorts."""

    expert, _ = _write_expert(tmp_path)
    questions = tmp_path / "questions.jsonl"
    _write_questions(questions)
    result = _run(
        GENERATOR,
        "--expert",
        expert,
        "--questions",
        questions,
        "--development-id",
        "q001",
        "--holdout-id",
        "q001",
        "--output",
        tmp_path / "tasks",
    )

    assert result.returncode == 2
    assert "development and holdout overlap" in result.stdout


def test_scorer_emits_case_metrics_and_closed_qualification_gates(
    tmp_path: Path,
) -> None:
    """Exact bound hits receive nDCG reward and invalid evidence is gated out."""

    scorer = _load_module("specialized_expert_harbor_scorer", SCORER)
    assert scorer.paper_identity("claims-2503-13804v1") == "2503.13804v1"
    assert scorer.paper_identity("paper-2408.04187v2") == "2408.04187v2"
    assert scorer.paper_identity("paper-1208-0928v2") == "1208.0928v2"
    _, records = _write_expert(tmp_path)
    question = {
        "id": "q001-first",
        "question": "Which papers support the first mechanism?",
        "qrels": {"paper_ids": ["paper-01", "paper-03"]},
        "top_k": 10,
        "expected": {
            "skill_name": "fixture-expert",
            "knowledge_tree_sha256": "a" * 64,
            "knowledge_file_count": 1,
            "record_count": 10,
        },
    }
    output = {
        "verification": {
            "status": "pass",
            "skill_name": "fixture-expert",
            "knowledge_tree_sha256": "a" * 64,
            "knowledge_file_count": 1,
            "record_count": 10,
            "retrieval": {"id": "fixture-retrieval-v1"},
        },
        "results": [
            _result(record, 10.0 - index)
            for index, record in enumerate(records)
        ],
    }

    rewards, diagnostics = scorer.evaluate_output(output, question, records)

    assert rewards["recall_at_10"] == 1.0
    assert rewards["mrr_at_10"] == 1.0
    assert 0.0 < rewards["ndcg_at_10"] <= 1.0
    assert rewards["reward"] == rewards["ndcg_at_10"]
    assert rewards["manifest_binding_gate"] == 1.0
    assert rewards["evidence_contract_gate"] == 1.0
    assert diagnostics["status"] == "scored-retrieval"

    output["results"][0]["record_sha256"] = "b" * 64
    invalid_rewards, invalid_diagnostics = scorer.evaluate_output(
        output,
        question,
        records,
    )

    assert invalid_rewards["reward"] == 0.0
    assert invalid_rewards["evidence_contract_gate"] == 0.0
    assert invalid_diagnostics["status"] == "agent-invalid-response"


def test_scorer_cli_reads_the_raw_retrieval_artifact(
    tmp_path: Path,
) -> None:
    """The verifier scores helper bytes, independent of the compact final answer."""

    expert, records = _write_expert(tmp_path)
    question = tmp_path / "question.json"
    question.write_text(
        json.dumps(
            {
                "id": "q001-first",
                "question": "Which papers support the first mechanism?",
                "qrels": {"paper_ids": ["paper-01", "paper-03"]},
                "top_k": 10,
                "expected": {
                    "skill_name": "fixture-expert",
                    "knowledge_tree_sha256": "a" * 64,
                    "knowledge_file_count": 1,
                    "record_count": 10,
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    retrieval = tmp_path / "retrieval.json"
    retrieval.write_text(
        json.dumps(
            {
                "verification": {
                    "status": "pass",
                    "skill_name": "fixture-expert",
                    "knowledge_tree_sha256": "a" * 64,
                    "knowledge_file_count": 1,
                    "record_count": 10,
                    "retrieval": {"id": "fixture-retrieval-v1"},
                },
                "results": [
                    _result(record, 10.0 - index)
                    for index, record in enumerate(records)
                ],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    pi_log = tmp_path / "pi.jsonl"
    pi_log.write_text(
        json.dumps(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": '{"status":"retrieval-written"}'}
                    ],
                    "stopReason": "stop",
                },
            }
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    reward = tmp_path / "reward.json"
    diagnostics = tmp_path / "diagnostics.json"

    result = _run(
        SCORER,
        "--pi-log",
        pi_log,
        "--retrieval",
        retrieval,
        "--question",
        question,
        "--ledger",
        expert / "references" / "knowledge" / "semantic" / "records.jsonl",
        "--reward",
        reward,
        "--diagnostics",
        diagnostics,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    rewards = json.loads(reward.read_text(encoding="utf-8"))
    scored = json.loads(diagnostics.read_text(encoding="utf-8"))
    assert rewards["evidence_contract_gate"] == 1.0
    assert rewards["reward"] == rewards["ndcg_at_10"]
    assert scored["status"] == "scored-retrieval"
