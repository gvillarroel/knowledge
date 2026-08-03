#!/usr/bin/env python3
"""Score one Harbor-native specialized-expert retrieval result."""

from __future__ import annotations

import argparse
from collections import OrderedDict
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Mapping, Sequence


try:
    from trace_status import classify_pi_trace
except ModuleNotFoundError:
    LOCAL_TRACE_ROOT = (
        Path(__file__).resolve().parents[4]
        / "evaluations"
        / "semantic-okf-harbor"
        / "grader"
    )
    sys.path.insert(0, str(LOCAL_TRACE_ROOT))
    from trace_status import classify_pi_trace


HEX64 = re.compile(r"^[0-9a-f]{64}$")
PAPER_ID_RE = re.compile(
    r"(?<!\d)(\d{4})[.-](\d{4,5}v\d+)(?!\d)",
    re.IGNORECASE,
)
RESULT_FIELDS = {
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


class ScoreError(ValueError):
    """Raised when frozen verifier input is invalid."""


def strict_json(text: str) -> Any:
    """Parse strict JSON with duplicate members and special numbers rejected."""

    def pairs(rows: list[tuple[str, Any]]) -> OrderedDict[str, Any]:
        result: OrderedDict[str, Any] = OrderedDict()
        for key, value in rows:
            if key in result:
                raise ScoreError("duplicate-json-member")
            result[key] = value
        return result

    def invalid_constant(_: str) -> None:
        raise ScoreError("non-standard-json-number")

    return json.loads(
        text,
        object_pairs_hook=pairs,
        parse_constant=invalid_constant,
    )


def load_json(path: Path) -> Mapping[str, Any]:
    """Load one strict JSON object."""

    value = strict_json(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ScoreError(f"non-object-json:{path.name}")
    return value


def load_jsonl(path: Path) -> list[Mapping[str, Any]]:
    """Load strict JSON Lines objects."""

    rows: list[Mapping[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = strict_json(line)
        if not isinstance(value, Mapping):
            raise ScoreError(f"non-object-jsonl-row:{number}")
        rows.append(value)
    return rows


def paper_identity(source_id: str) -> str | None:
    """Return the authoritative paper identity for one record source."""

    match = PAPER_ID_RE.search(source_id)
    if match:
        return f"{match.group(1)}.{match.group(2).lower()}"
    for prefix in ("claims-", "paper-"):
        if source_id.startswith(prefix) and len(source_id) > len(prefix):
            return source_id[len(prefix) :]
    return None


def retrieval_metrics(
    ranking: Sequence[str],
    relevant: set[str],
    *,
    cutoff: int,
) -> dict[str, float]:
    """Compute binary Recall, MRR, and nDCG at one cutoff."""

    selected = list(ranking[:cutoff])
    gains = [1.0 if item in relevant else 0.0 for item in selected]
    recall = sum(gains) / len(relevant) if relevant else 0.0
    reciprocal_rank = next(
        (1.0 / rank for rank, gain in enumerate(gains, 1) if gain),
        0.0,
    )
    dcg = sum(gain / math.log2(rank + 1) for rank, gain in enumerate(gains, 1))
    ideal_count = min(len(relevant), cutoff)
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_count + 1))
    return {
        "recall_at_10": recall,
        "mrr_at_10": reciprocal_rank,
        "ndcg_at_10": dcg / ideal if ideal else 0.0,
    }


def _safe_concept_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and "\\" not in value
        and ".." not in path.parts
        and bool(path.parts)
        and path.parts[0] == "concepts"
    )


def evaluate_output(
    output: Any,
    question: Mapping[str, Any],
    ledger_rows: Sequence[Mapping[str, Any]],
    *,
    terminal_outcome: str = "answer-emitted",
    failure_domain: str | None = None,
    error_code: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Validate one helper response and return Harbor rewards and diagnostics."""

    expected = question.get("expected")
    qrels = question.get("qrels")
    if not isinstance(expected, Mapping) or not isinstance(qrels, Mapping):
        raise ScoreError("question-contract")
    relevant_raw = qrels.get("paper_ids")
    if (
        not isinstance(relevant_raw, list)
        or not relevant_raw
        or any(not isinstance(item, str) or not item for item in relevant_raw)
    ):
        raise ScoreError("question-qrels")
    relevant = set(relevant_raw)
    if len(relevant) != len(relevant_raw):
        raise ScoreError("duplicate-question-qrel")
    top_k = question.get("top_k")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k != 10:
        raise ScoreError("question-top-k")

    ledger = {
        (str(row.get("source_id")), str(row.get("record_id"))): row
        for row in ledger_rows
    }
    if len(ledger) != len(ledger_rows):
        raise ScoreError("duplicate-ledger-identity")

    errors: list[str] = []
    if not isinstance(output, Mapping):
        output = {}
        errors.append("top-level-object")
    verification = output.get("verification")
    results = output.get("results")
    if not isinstance(verification, Mapping):
        verification = {}
        errors.append("verification-object")
    if not isinstance(results, list):
        results = []
        errors.append("results-array")

    manifest_binding = (
        verification.get("status") == "pass"
        and verification.get("skill_name") == expected.get("skill_name")
        and verification.get("knowledge_tree_sha256")
        == expected.get("knowledge_tree_sha256")
        and verification.get("knowledge_file_count")
        == expected.get("knowledge_file_count")
        and verification.get("record_count") == expected.get("record_count")
    )
    retrieval = verification.get("retrieval")
    retrieval_contract = (
        retrieval.get("id")
        if isinstance(retrieval, Mapping) and isinstance(retrieval.get("id"), str)
        else None
    )
    if not manifest_binding:
        errors.append("manifest-binding")
    if retrieval_contract is None:
        errors.append("retrieval-contract")

    result_count_ok = len(results) == top_k
    if not result_count_ok:
        errors.append("result-count")
    evidence_valid: list[bool] = []
    ranking: list[str] = []
    seen_records: set[tuple[str, str]] = set()
    seen_papers: set[str] = set()
    previous_score = math.inf
    for row in results:
        if not isinstance(row, Mapping):
            evidence_valid.append(False)
            errors.append("result-object")
            continue
        source_id = row.get("source_id")
        record_id = row.get("record_id")
        score = row.get("score")
        identity = (
            (source_id, record_id)
            if isinstance(source_id, str) and isinstance(record_id, str)
            else None
        )
        record = ledger.get(identity) if identity is not None else None
        paper_id = paper_identity(source_id) if isinstance(source_id, str) else None
        finite_score = (
            not isinstance(score, bool)
            and isinstance(score, (int, float))
            and math.isfinite(float(score))
            and float(score) <= previous_score + 1e-12
        )
        if finite_score:
            previous_score = float(score)
        exact = (
            set(row) == RESULT_FIELDS
            and record is not None
            and paper_id is not None
            and identity not in seen_records
            and paper_id not in seen_papers
            and finite_score
            and _safe_concept_path(row.get("concept_path"))
            and isinstance(row.get("record_sha256"), str)
            and HEX64.fullmatch(str(row.get("record_sha256"))) is not None
            and all(
                row.get(field) == record.get(field)
                for field in (
                    "concept_id",
                    "concept_path",
                    "concept_type",
                    "record_sha256",
                    "source_path",
                    "title",
                )
            )
        )
        evidence_valid.append(exact)
        if identity is not None:
            seen_records.add(identity)
        if paper_id is not None:
            seen_papers.add(paper_id)
            ranking.append(paper_id)

    all_evidence_valid = bool(results) and all(evidence_valid)
    if not all_evidence_valid:
        errors.append("evidence-contract")
    unique_ranking = len(ranking) == len(set(ranking)) == len(results)
    if not unique_ranking:
        errors.append("paper-deduplication")

    terminal_ok = terminal_outcome == "answer-emitted"
    mechanical_gate = terminal_ok and result_count_ok and unique_ranking
    evidence_gate = mechanical_gate and manifest_binding and all_evidence_valid
    metrics = retrieval_metrics(ranking, relevant, cutoff=top_k)
    rewards = {
        **metrics,
        "manifest_binding_gate": float(manifest_binding),
        "evidence_contract_gate": float(evidence_gate),
        "mechanical_qualification_gate": float(evidence_gate),
        "reward": float(evidence_gate) * metrics["ndcg_at_10"],
    }

    if failure_domain == "provider":
        status = "provider-failure"
    elif not terminal_ok:
        status = "agent-failure"
    elif not evidence_gate:
        status = "agent-invalid-response"
    else:
        status = "scored-retrieval"
    diagnostics = {
        "schema_version": "specialized-expert-harbor-retrieval-diagnostics/1.0",
        "status": status,
        "question_id": question.get("id"),
        "retrieval_contract": retrieval_contract,
        "ranking": ranking[:top_k],
        "missed_relevant_paper_ids": sorted(relevant - set(ranking[:top_k])),
        "nonrelevant_paper_ids": [
            paper_id for paper_id in ranking[:top_k] if paper_id not in relevant
        ],
        "invalid_evidence_indices": [
            index for index, valid in enumerate(evidence_valid) if not valid
        ],
        "errors": sorted(set(errors)),
        "terminal_outcome": terminal_outcome,
        "failure_domain": failure_domain,
        "error_code": error_code,
    }
    return rewards, diagnostics


def score(args: argparse.Namespace) -> tuple[dict[str, float], dict[str, Any]]:
    """Load one agent-written retrieval artifact and score frozen task data."""

    question = load_json(args.question)
    ledger_rows = load_jsonl(args.ledger)
    trace = classify_pi_trace(args.pi_log)
    output = load_json(args.retrieval)
    return evaluate_output(
        output,
        question,
        ledger_rows,
        terminal_outcome=str(trace.get("outcome")),
        failure_domain=(
            str(trace["failure_domain"])
            if trace.get("failure_domain") is not None
            else None
        ),
        error_code=(
            str(trace["error_code"]) if trace.get("error_code") is not None else None
        ),
    )


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    """Write deterministic verifier output."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the verifier command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pi-log", type=Path, default=Path("/logs/agent/pi.txt"))
    parser.add_argument(
        "--retrieval",
        type=Path,
        default=Path("/logs/agent/retrieval.json"),
    )
    parser.add_argument("--question", type=Path, default=Path("/tests/question.json"))
    parser.add_argument("--ledger", type=Path, default=Path("/tests/records.jsonl"))
    parser.add_argument(
        "--reward",
        type=Path,
        default=Path("/logs/verifier/reward.json"),
    )
    parser.add_argument(
        "--diagnostics",
        type=Path,
        default=Path("/logs/verifier/diagnostics.json"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Score one task while preserving verifier failures as diagnostics."""

    args = build_parser().parse_args(argv)
    try:
        rewards, diagnostics = score(args)
    except (OSError, UnicodeError, ScoreError, KeyError, TypeError, ValueError) as exc:
        rewards = {
            "reward": 0.0,
            "manifest_binding_gate": 0.0,
            "evidence_contract_gate": 0.0,
            "mechanical_qualification_gate": 0.0,
        }
        diagnostics = {
            "schema_version": "specialized-expert-harbor-retrieval-diagnostics/1.0",
            "status": "verifier-error",
            "failure_domain": "evaluator",
            "terminal_outcome": "verifier-error",
            "error_code": type(exc).__name__,
        }
    write_json(args.reward, rewards)
    write_json(args.diagnostics, diagnostics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
