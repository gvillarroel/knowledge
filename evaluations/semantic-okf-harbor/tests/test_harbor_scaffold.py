"""Unit tests for the isolated Semantic OKF Harbor scaffold."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
from argparse import Namespace
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(name: str, path: Path) -> ModuleType:
    """Load one scaffold module without requiring a package name."""

    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


SCORE = module("semantic_okf_harbor_score", ROOT / "grader/score.py")
GENERATOR = module("semantic_okf_harbor_generator", ROOT / "generate_tasks.py")
VALIDATOR = module("semantic_okf_harbor_validator", ROOT / "validate_tasks.py")
RUNNER = module("semantic_okf_harbor_runner", ROOT / "run_harbor.py")
SUMMARY = module("semantic_okf_harbor_summary", ROOT / "summarize_results.py")
SNAPSHOT = module("semantic_okf_harbor_snapshot", ROOT / "snapshot_skills.py")


def dump(path: Path, value: object) -> None:
    """Write one compact JSON fixture."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def fixture(tmp_path: Path, *, hard: bool = False) -> Namespace:
    """Create a minimal exact-ledger scoring fixture."""

    body = "Exact authoritative evidence."
    record = {
        "source_id": "source-a",
        "record_id": "record-a",
        "concept_path": "concepts/source-a/record-a.md",
        "source_path": "sources/a.md",
        "record_sha256": "a" * 64,
        "body": body,
    }
    (tmp_path / "records.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    dump(
        tmp_path / "source-combination.json",
        {"records": [{"source_id": "source-a", "record_id": "record-a", "document_id": "/doc/a/"}]},
    )
    dump(
        tmp_path / "question.json",
        {"id": "q001", "question": "What is supported?", "question_type": "hard" if hard else "direct", "qrels": {"document_ids": ["/doc/a/"], "source_ids": ["source-a"]}},
    )
    answer = {
        "question_id": "q001",
        "answer": {"summary": "The cited record supplies exact support.", "claims": [{"statement": "The answer is supported.", "evidence_indices": [0]}]},
        "evidence": [{
            "source_id": "source-a",
            "record_id": "record-a",
            "concept_path": "concepts/source-a/record-a.md",
            "source_path": "sources/a.md",
            "record_sha256": "a" * 64,
            "locator": {"kind": "record", "target": "record.body"},
            "text_sha256": hashlib.sha256(body.encode()).hexdigest(),
        }],
    }
    dump(tmp_path / "pi.txt", answer)
    truth_path = None
    authority = tmp_path / "authority"
    if hard:
        raw = "front matter\n" + body + "\nfooter"
        raw_path = authority / "source.mdx"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw.encode("utf-8"))
        start = raw.index(body)
        truth = {
            "id": "q001",
            "authoritative_evidence": [{
                "id": "e1",
                "source_id": "source-a",
                "path": "source.mdx",
                "start_char": start,
                "end_char": start + len(body),
                "file_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                "text_sha256": hashlib.sha256(body.encode()).hexdigest(),
            }],
            "ground_truth": {
                "required_document_ids": ["/doc/a/"],
                "answer_claims": [{"id": "a1", "evidence_ids": ["e1"]}],
                "important_negatives": [{"id": "n1", "evidence_ids": ["e1"]}],
            },
        }
        truth_path = tmp_path / "truth.json"
        dump(truth_path, truth)
    return Namespace(
        pi_log=tmp_path / "pi.txt",
        question=tmp_path / "question.json",
        ledger=tmp_path / "records.jsonl",
        crosswalk=tmp_path / "source-combination.json",
        ground_truth=truth_path,
        authority_root=authority,
        reward=tmp_path / "reward.json",
        diagnostics=tmp_path / "diagnostics.json",
    )


def test_valid_direct_answer_passes_non_compensating_gate(tmp_path: Path) -> None:
    rewards, diagnostics = SCORE.score(fixture(tmp_path))
    assert rewards["reward"] == 1.0
    assert rewards["quality_gate"] == 1.0
    assert rewards["evidence_recall"] == 1.0
    assert diagnostics["invalid_evidence_indices"] == []


def test_hard_answer_maps_raw_evidence_to_record_body(tmp_path: Path) -> None:
    rewards, diagnostics = SCORE.score(fixture(tmp_path, hard=True))
    assert rewards["authoritative_evidence_completeness"] == 1.0
    assert rewards["atomic_claim_evidence_completeness"] == 1.0
    assert rewards["important_negative_evidence_completeness"] == 1.0
    assert diagnostics["covered_hard_evidence_count"] == 1


def test_hard_answer_hashes_crlf_before_normalized_body_join(tmp_path: Path) -> None:
    """Authoritative offsets/hash use raw CRLF text; ledger ranges use LF text."""

    body = "Exact authoritative\nevidence."
    record = {
        "source_id": "source-a",
        "record_id": "record-a",
        "concept_path": "concepts/source-a/record-a.md",
        "source_path": "sources/a.md",
        "record_sha256": "a" * 64,
        "body": body,
    }
    (tmp_path / "records.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    dump(
        tmp_path / "source-combination.json",
        {"records": [{"source_id": "source-a", "record_id": "record-a", "document_id": "/doc/a/"}]},
    )
    dump(
        tmp_path / "question.json",
        {"id": "q001", "question": "What is supported?", "question_type": "hard", "qrels": {"document_ids": ["/doc/a/"], "source_ids": ["source-a"]}},
    )
    answer = {
        "question_id": "q001",
        "answer": {"summary": "The cited record supplies exact support.", "claims": [{"statement": "The answer is supported.", "evidence_indices": [0]}]},
        "evidence": [{
            "source_id": "source-a",
            "record_id": "record-a",
            "concept_path": "concepts/source-a/record-a.md",
            "source_path": "sources/a.md",
            "record_sha256": "a" * 64,
            "locator": {"kind": "record", "target": "record.body"},
            "text_sha256": hashlib.sha256(body.encode()).hexdigest(),
        }],
    }
    dump(tmp_path / "pi.txt", answer)
    selected = body.replace("\n", "\r\n")
    raw = "front matter\r\n" + selected + "\r\nfooter"
    authority = tmp_path / "authority"
    raw_path = authority / "source.mdx"
    raw_path.parent.mkdir(parents=True)
    raw_path.write_bytes(raw.encode("utf-8"))
    start = raw.index(selected)
    dump(
        tmp_path / "truth.json",
        {
            "id": "q001",
            "authoritative_evidence": [{
                "id": "e1",
                "source_id": "source-a",
                "path": "source.mdx",
                "start_char": start,
                "end_char": start + len(selected),
                "file_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                "text_sha256": hashlib.sha256(selected.encode()).hexdigest(),
            }],
            "ground_truth": {
                "required_document_ids": ["/doc/a/"],
                "answer_claims": [{"id": "a1", "evidence_ids": ["e1"]}],
                "important_negatives": [{"id": "n1", "evidence_ids": ["e1"]}],
            },
        },
    )
    args = Namespace(
        pi_log=tmp_path / "pi.txt",
        question=tmp_path / "question.json",
        ledger=tmp_path / "records.jsonl",
        crosswalk=tmp_path / "source-combination.json",
        ground_truth=tmp_path / "truth.json",
        authority_root=authority,
        reward=tmp_path / "reward.json",
        diagnostics=tmp_path / "diagnostics.json",
    )
    rewards, diagnostics = SCORE.score(args)
    assert rewards["authoritative_evidence_completeness"] == 1.0
    assert rewards["quality_gate"] == 1.0
    assert diagnostics["covered_hard_evidence_count"] == 1


def test_hard_eof_span_maps_publication_blank_lines_omitted_by_record(tmp_path: Path) -> None:
    body = "## Last section\n\nExact support."
    raw = body.replace("\n", "\r\n") + "\r\n\r\n\r\n"
    authority = tmp_path / "authority"
    authority.mkdir()
    (authority / "source.mdx").write_bytes(raw.encode("utf-8"))
    truth = {
        "authoritative_evidence": [{
            "id": "e1",
            "source_id": "source-a",
            "path": "source.mdx",
            "start_char": 0,
            "end_char": len(raw),
            "file_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "text_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        }]
    }
    ledger = {("source-a", "record-a"): {"source_id": "source-a", "record_id": "record-a", "body": body}}
    assert SCORE.authoritative_ranges(truth, authority, ledger) == {
        "e1": ("source-a", (0, len(body)))
    }


def test_invalid_evidence_cannot_be_compensated(tmp_path: Path) -> None:
    args = fixture(tmp_path)
    answer = json.loads(args.pi_log.read_text(encoding="utf-8"))
    answer["evidence"][0]["source_path"] = "sources/not-real.md"
    dump(args.pi_log, answer)
    rewards, diagnostics = SCORE.score(args)
    assert rewards["reward"] == 0.0
    assert rewards["quality_gate"] == 0.0
    assert diagnostics["invalid_evidence_indices"] == [0]


def test_duplicate_json_members_are_rejected() -> None:
    try:
        SCORE.strict_json('{"question_id":"q001","question_id":"q002"}')
    except SCORE.ScoreError as exc:
        assert str(exc) == "duplicate-json-member"
    else:
        raise AssertionError("duplicate JSON member was accepted")


def test_instruction_does_not_include_qrels_or_ground_truth() -> None:
    question = {
        "id": "q001",
        "question": "How does the feature work?",
        "question_type": "direct",
        "qrels": {"document_ids": ["/secret/document/"], "source_ids": ["secret-source-id"]},
    }
    truth = {
        "authoritative_evidence": [{"path": "secret/path.mdx", "text_sha256": "b" * 64}],
        "ground_truth": {"answer_claims": [{"statement": "Secret expected answer."}], "important_negatives": []},
    }
    rendered = GENERATOR.instruction(question)
    assert question["question"] in rendered
    assert "You must use the sole installed consultation skill." in rendered
    assert not any(value in rendered for value in VALIDATOR.forbidden_fragments(question, truth))


def test_checked_split_is_complete_and_contamination_aware() -> None:
    split = GENERATOR.split_map(ROOT / "splits.json")
    assert len(split) == 40
    assert split["q039"] == "train"
    assert split["q040"] == "train"
    assert split["q034"] == "holdout"
    assert split["q036"] == "holdout"


def test_runner_config_has_one_skill_bundle_and_ephemeral_auth_mount(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    (bundle / "semantic").mkdir(parents=True)
    (bundle / "semantic/records.jsonl").write_text("{}\n", encoding="utf-8")
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: test\ndescription: test\n---\n", encoding="utf-8")
    auth = tmp_path / "auth"
    auth.mkdir()
    (auth / "auth.json").write_text("super-secret", encoding="utf-8")
    args = Namespace(
        family="legacy",
        generation="baseline",
        split="train",
        bundle=bundle,
        hf_cache=None,
        attempts=1,
    )
    config = RUNNER.job_config(args, tmp_path / "job", auth, skill, ["q001"])
    assert len(config["agents"]) == 1
    assert config["agents"][0]["skills"] == [str(skill)]
    assert config["agents"][0]["name"] == "pi"
    assert config["agents"][0]["kwargs"]["version"] == "0.73.1"
    assert [mount["target"] for mount in config["environment"]["mounts"]] == ["/knowledge", "/root/.pi/agent"]
    assert "super-secret" not in json.dumps(config)


def test_runner_rejects_empty_pi_auth_before_starting_harbor(tmp_path: Path) -> None:
    auth_file = tmp_path / "auth.json"
    auth_file.write_text("{}\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="no openai-codex credential"):
        RUNNER.create_auth_dir(auth_file)


def test_runner_copies_valid_pi_auth_to_private_ephemeral_directory(tmp_path: Path) -> None:
    auth_file = tmp_path / "auth.json"
    auth_file.write_text('{"openai-codex":{"access":"test"}}\n', encoding="utf-8")
    copied = RUNNER.create_auth_dir(auth_file)
    try:
        assert json.loads((copied / "auth.json").read_text(encoding="utf-8"))["openai-codex"]
        if os.name == "posix":
            assert copied.stat().st_mode & 0o077 == 0
            assert (copied / "auth.json").stat().st_mode & 0o077 == 0
    finally:
        shutil.rmtree(copied)


def test_summarizer_reports_paired_metric_delta(tmp_path: Path) -> None:
    for generation, reward in (("baseline", 0.25), ("evolved", 0.75)):
        trial = tmp_path / generation / "trial-q001"
        trial.mkdir(parents=True)
        dump(
            trial / "result.json",
            {
                "task_name": "knowledge/semantic-okf-harbor__q001",
                "trial_name": "attempt-1",
                "config": {},
                "verifier_result": {"rewards": {"reward": reward, "quality_gate": 1.0}},
                "agent_result": {"n_input_tokens": 10, "n_output_tokens": 5, "cost_usd": 0.01},
                "agent_execution": {"started_at": "2026-01-01T00:00:00+00:00", "finished_at": "2026-01-01T00:00:01+00:00"},
            },
        )
        dump(trial / "lock.json", {"frozen": True})
    report = SUMMARY.compare(tmp_path / "baseline", tmp_path / "evolved", "train", False)
    assert report["paired_trials"] == 1
    assert report["evolved_minus_baseline"]["reward"] == 0.5
    assert report["baseline"]["mean_latency_seconds"] == 1.0


def test_snapshot_tree_hash_ignores_generated_bytecode(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text("skill", encoding="utf-8")
    before = SNAPSHOT.tree_sha256(tmp_path)
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "ignored.pyc").write_bytes(b"ignored")
    assert SNAPSHOT.tree_sha256(tmp_path) == before
