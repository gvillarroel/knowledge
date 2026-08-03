#!/usr/bin/env python3
"""Smoke-test a QEC expert with the native Harbor retrieval grader."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCHEMA_VERSION = "qec-native-harbor-retrieval-smoke/1.0"
SCRIPT_PATH = Path(__file__).resolve()
EVALUATION_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_QUESTIONS = EVALUATION_ROOT / "benchmark" / "retrieval-questions.jsonl"
DEFAULT_SCORER = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "harbor"
    / "grader"
    / "score.py"
)
DEFAULT_QUESTION_IDS = (
    "q001-surface-code-braiding",
    "q031-lifted-product-progression",
)


class SmokeError(RuntimeError):
    """Describe an invalid artifact or failed native-grader smoke case."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _fingerprint(path: Path) -> dict[str, Any]:
    return {
        "path": _portable_path(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SmokeError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SmokeError(f"{label} must be a JSON object: {path}")
    return value


def _load_questions(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SmokeError(f"Cannot read questions at {path}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SmokeError(f"Invalid question line {number}: {exc}") from exc
        identifier = row.get("id") if isinstance(row, dict) else None
        if not isinstance(identifier, str) or not identifier or identifier in rows:
            raise SmokeError(f"Invalid or duplicate question ID on line {number}")
        rows[identifier] = row
    return rows


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _run(command: Sequence[object], *, label: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(item) for item in command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise SmokeError(f"{label} failed with exit {result.returncode}: {detail}")
    return result


def _expected(manifest: Mapping[str, Any]) -> dict[str, Any]:
    knowledge = manifest.get("knowledge")
    tree = knowledge.get("tree") if isinstance(knowledge, Mapping) else None
    skill_name = manifest.get("skill_name")
    if (
        not isinstance(skill_name, str)
        or not isinstance(knowledge, Mapping)
        or not isinstance(tree, Mapping)
        or not isinstance(knowledge.get("record_count"), int)
        or not isinstance(tree.get("file_count"), int)
        or not isinstance(tree.get("sha256"), str)
    ):
        raise SmokeError("Expert manifest lacks the native grader binding fields")
    return {
        "skill_name": skill_name,
        "knowledge_tree_sha256": tree["sha256"],
        "knowledge_file_count": tree["file_count"],
        "record_count": knowledge["record_count"],
    }


def _score_case(
    *,
    expert: Path,
    scorer: Path,
    question: Mapping[str, Any],
    expected: Mapping[str, Any],
    temp_root: Path,
) -> dict[str, Any]:
    identifier = str(question["id"])
    case_root = temp_root / identifier
    case_root.mkdir()
    retrieval = case_root / "retrieval.json"
    reward = case_root / "reward.json"
    diagnostics = case_root / "diagnostics.json"
    frozen_question = case_root / "question.json"
    pi_log = case_root / "pi.jsonl"

    helper = expert / "scripts" / "query_expert_knowledge.py"
    result = _run(
        (
            sys.executable,
            "-B",
            helper,
            "search",
            "--contains",
            question["question"],
            "--limit",
            "10",
        ),
        label=f"expert retrieval for {identifier}",
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SmokeError(f"Expert emitted invalid JSON for {identifier}: {exc}") from exc
    _write_json(retrieval, output)
    _write_json(
        frozen_question,
        {
            "id": identifier,
            "question": question["question"],
            "qrels": {"paper_ids": question["qrels"]["paper_ids"]},
            "top_k": 10,
            "expected": expected,
        },
    )
    pi_log.write_text(
        json.dumps(
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": '{"status":"retrieval-written"}',
                        }
                    ],
                    "stopReason": "stop",
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _run(
        (
            sys.executable,
            "-B",
            scorer,
            "--pi-log",
            pi_log,
            "--retrieval",
            retrieval,
            "--question",
            frozen_question,
            "--ledger",
            expert
            / "references"
            / "knowledge"
            / "semantic"
            / "records.jsonl",
            "--reward",
            reward,
            "--diagnostics",
            diagnostics,
        ),
        label=f"native Harbor grader for {identifier}",
    )
    rewards = _load_json(reward, label=f"{identifier} reward")
    scored = _load_json(diagnostics, label=f"{identifier} diagnostics")
    required_rewards = (
        "recall_at_10",
        "mrr_at_10",
        "ndcg_at_10",
        "manifest_binding_gate",
        "evidence_contract_gate",
        "mechanical_qualification_gate",
        "reward",
    )
    if (
        scored.get("status") != "scored-retrieval"
        or any(rewards.get(key) != 1.0 for key in required_rewards)
        or scored.get("errors") != []
        or scored.get("missed_relevant_paper_ids") != []
        or scored.get("invalid_evidence_indices") != []
    ):
        raise SmokeError(
            f"Native Harbor grading failed for {identifier}: "
            f"{json.dumps({'rewards': rewards, 'diagnostics': scored}, sort_keys=True)}"
        )
    return {
        "question_id": identifier,
        "question_type": question.get("question_type"),
        "qrels": list(question["qrels"]["paper_ids"]),
        "ranking": scored["ranking"],
        "rewards": {key: rewards[key] for key in required_rewards},
        "diagnostics_status": scored["status"],
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    expert = args.expert.resolve()
    scorer = args.scorer.resolve()
    questions_path = args.questions.resolve()
    helper = expert / "scripts" / "query_expert_knowledge.py"
    manifest_path = expert / "expert-manifest.json"
    ledger = expert / "references" / "knowledge" / "semantic" / "records.jsonl"
    for path, label in (
        (helper, "expert helper"),
        (manifest_path, "expert manifest"),
        (ledger, "expert ledger"),
        (scorer, "native Harbor scorer"),
        (questions_path, "questions"),
    ):
        if not path.is_file():
            raise SmokeError(f"{label} is absent: {path}")

    manifest = _load_json(manifest_path, label="expert manifest")
    profile = manifest.get("retrieval_profile")
    if (
        manifest.get("schema_version") != "semantic-okf-expert-skill/1.1"
        or not isinstance(profile, Mapping)
        or profile.get("dataset_id") != "quantum-error-correction-papers-40"
        or profile.get("promotion_eligible") is not False
    ):
        raise SmokeError("Expert is not the non-promotable supervised QEC treatment")
    questions = _load_questions(questions_path)
    missing = [identifier for identifier in args.question_id if identifier not in questions]
    if missing:
        raise SmokeError(f"Unknown question IDs: {', '.join(missing)}")

    with tempfile.TemporaryDirectory(prefix="qec-native-harbor-smoke-") as raw:
        cases = [
            _score_case(
                expert=expert,
                scorer=scorer,
                question=questions[identifier],
                expected=_expected(manifest),
                temp_root=Path(raw),
            )
            for identifier in args.question_id
        ]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": "quantum-error-correction-papers-40",
        "evaluation_scope": (
            "Representative native-grader compatibility smoke only; "
            "the all-40 replicated report is the quality authority."
        ),
        "promotion_eligible": False,
        "all_qrels_exposed": True,
        "expert": {
            "skill_name": manifest["skill_name"],
            "manifest": _fingerprint(manifest_path),
            "helper": _fingerprint(helper),
            "ledger": _fingerprint(ledger),
        },
        "questions": _fingerprint(questions_path),
        "native_harbor_scorer": _fingerprint(scorer),
        "case_count": len(cases),
        "cases": cases,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expert", type=Path, required=True)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--scorer", type=Path, default=DEFAULT_SCORER)
    parser.add_argument(
        "--question-id",
        action="append",
        default=None,
        help="Repeat for additional cases; defaults to one development and one hard case.",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.question_id is None:
        args.question_id = list(DEFAULT_QUESTION_IDS)
    if len(args.question_id) != len(set(args.question_id)):
        print("native Harbor smoke failed: duplicate question ID", file=sys.stderr)
        return 2
    try:
        report = validate(args)
        if args.output is not None:
            _write_json(args.output.resolve(), report)
    except (OSError, UnicodeError, KeyError, TypeError, SmokeError) as exc:
        print(f"native Harbor smoke failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
