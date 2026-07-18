#!/usr/bin/env python3
"""Deterministically score one source-generic Semantic OKF answer."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from trace_status import classify_pi_trace

TOP_KEYS = ["question_id", "answer", "evidence"]
ANSWER_KEYS = ["summary", "claims"]
CLAIM_KEYS = ["statement", "evidence_indices"]
EVIDENCE_KEYS = [
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
]
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ScoreError(ValueError):
    """Raised for a closed-contract scoring input error."""


def sha256_text(value: str) -> str:
    """Hash one Unicode string as UTF-8."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def strict_json(text: str) -> Any:
    """Parse JSON while rejecting duplicate members and non-standard numbers."""

    def pairs(rows: list[tuple[str, Any]]) -> OrderedDict[str, Any]:
        result: OrderedDict[str, Any] = OrderedDict()
        for key, value in rows:
            if key in result:
                raise ScoreError("duplicate-json-member")
            result[key] = value
        return result

    def invalid_constant(_: str) -> None:
        raise ScoreError("non-standard-json-number")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def load_json(path: Path) -> Any:
    """Load one strict UTF-8 JSON file."""

    return strict_json(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[Mapping[str, Any]]:
    """Load a strict JSON Lines file."""

    rows: list[Mapping[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = strict_json(line)
        if not isinstance(value, Mapping):
            raise ScoreError(f"non-object-jsonl-row:{number}")
        rows.append(value)
    return rows


def ratio(numerator: int, denominator: int, empty: float = 0.0) -> float:
    """Return a bounded, total-safe ratio."""

    return numerator / denominator if denominator else empty


def validate_contract(value: Any, expected_id: str) -> tuple[bool, bool, list[str]]:
    """Validate the exact source-generic response contract."""

    errors: list[str] = []
    if not isinstance(value, Mapping) or list(value.keys()) != TOP_KEYS:
        return False, False, ["top-level-contract"]
    if value.get("question_id") != expected_id:
        errors.append("question-id")
    evidence = value.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence-array")
        evidence = []
    answer = value.get("answer")
    if answer is None:
        if evidence:
            errors.append("null-answer-evidence")
        return not errors, False, errors
    if not isinstance(answer, Mapping) or list(answer.keys()) != ANSWER_KEYS:
        return False, True, errors + ["answer-contract"]
    summary = answer.get("summary")
    claims = answer.get("claims")
    if not isinstance(summary, str) or not summary.strip() or not 1 <= len(summary.split()) <= 450:
        errors.append("summary")
    if not isinstance(claims, list) or not claims:
        errors.append("claims")
        claims = []
    for claim in claims:
        if not isinstance(claim, Mapping) or list(claim.keys()) != CLAIM_KEYS:
            errors.append("claim-contract")
            continue
        statement, indices = claim.get("statement"), claim.get("evidence_indices")
        if not isinstance(statement, str) or not statement.strip():
            errors.append("claim-statement")
        if (
            not isinstance(indices, list)
            or not indices
            or any(isinstance(index, bool) or not isinstance(index, int) for index in indices)
        ):
            errors.append("claim-indices")
    for row in evidence:
        if not isinstance(row, Mapping) or set(row) != set(EVIDENCE_KEYS):
            errors.append("evidence-contract")
            continue
        if any(not isinstance(row.get(key), str) or not row[key] for key in EVIDENCE_KEYS[:4]):
            errors.append("evidence-identity")
        if not isinstance(row.get("record_sha256"), str) or not HEX64.fullmatch(row["record_sha256"]):
            errors.append("record-sha256")
        if not isinstance(row.get("locator"), Mapping):
            errors.append("locator")
        if not isinstance(row.get("text_sha256"), str) or not HEX64.fullmatch(row["text_sha256"]):
            errors.append("text-sha256")
    return not errors, True, sorted(set(errors))


def reference_validity(value: Mapping[str, Any]) -> bool:
    """Require in-range references and evidence in deterministic first-use order."""

    answer, evidence = value.get("answer"), value.get("evidence")
    if answer is None:
        return isinstance(evidence, list) and not evidence
    if not isinstance(answer, Mapping) or not isinstance(evidence, list):
        return False
    claims = answer.get("claims")
    if not isinstance(claims, list):
        return False
    first_use: list[int] = []
    seen: set[int] = set()
    for claim in claims:
        if not isinstance(claim, Mapping) or not isinstance(claim.get("evidence_indices"), list):
            return False
        for index in claim["evidence_indices"]:
            if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(evidence):
                return False
            if index not in seen:
                seen.add(index)
                first_use.append(index)
    return first_use == list(range(len(evidence)))


def locator_text(locator: Mapping[str, Any], body: str) -> str | None:
    """Reconstruct text selected by a closed source-generic locator."""

    kind = locator.get("kind")
    if kind == "record":
        if set(locator) - {"kind", "target", "fragment"}:
            return None
        return body
    if kind != "character-range" or set(locator) - {"kind", "target", "fragment", "start", "end"}:
        return None
    start, end = locator.get("start"), locator.get("end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or not 0 <= start < end <= len(body)
    ):
        return None
    return body[start:end]


def evidence_validity(
    rows: Sequence[Any], ledger: Mapping[tuple[str, str], Mapping[str, Any]]
) -> tuple[list[bool], list[tuple[int, int] | None]]:
    """Validate evidence fields and return reconstructed body intervals."""

    valid: list[bool] = []
    intervals: list[tuple[int, int] | None] = []
    for row in rows:
        if not isinstance(row, Mapping):
            valid.append(False)
            intervals.append(None)
            continue
        record = ledger.get((str(row.get("source_id")), str(row.get("record_id"))))
        body = record.get("body") if isinstance(record, Mapping) else None
        locator = row.get("locator")
        selected = locator_text(locator, body) if isinstance(locator, Mapping) and isinstance(body, str) else None
        expected = {
            "concept_path": record.get("concept_path") if record else None,
            "source_path": record.get("source_path") if record else None,
            "record_sha256": record.get("record_sha256") if record else None,
        }
        ok = (
            selected is not None
            and all(row.get(key) == expected_value for key, expected_value in expected.items())
            and row.get("text_sha256") == sha256_text(selected)
        )
        valid.append(bool(ok))
        if ok and isinstance(locator, Mapping) and locator.get("kind") == "character-range":
            intervals.append((int(locator["start"]), int(locator["end"])))
        elif ok and isinstance(body, str):
            intervals.append((0, len(body)))
        else:
            intervals.append(None)
    return valid, intervals


def ranked_documents(
    evidence: Sequence[Any], crosswalk: Mapping[tuple[str, str], str]
) -> list[str]:
    """Map first-use evidence to unique authoritative document identities."""

    result: list[str] = []
    for row in evidence:
        if not isinstance(row, Mapping):
            continue
        document = crosswalk.get((str(row.get("source_id")), str(row.get("record_id"))))
        if document is not None and document not in result:
            result.append(document)
    return result


def retrieval_metrics(ranking: Sequence[str], relevant: set[str]) -> dict[str, float]:
    """Score cited evidence identities as the answer's used retrieval ranking."""

    hits = [1 if document in relevant else 0 for document in ranking]
    precision = ratio(sum(hits), len(ranking))
    recall = ratio(len(set(ranking) & relevant), len(relevant), empty=1.0)
    first = next((index for index, hit in enumerate(hits, 1) if hit), None)
    dcg = sum(hit / math.log2(index + 1) for index, hit in enumerate(hits, 1))
    ideal = sum(1.0 / math.log2(index + 1) for index in range(1, len(relevant) + 1))
    return {
        "evidence_precision": precision,
        "evidence_recall": recall,
        "mrr": 1.0 / first if first else 0.0,
        "ndcg": ratio(dcg, ideal, empty=1.0),
        "complete_qrel_coverage": 1.0 if relevant.issubset(set(ranking)) else 0.0,
    }


def authoritative_ranges(
    truth: Mapping[str, Any] | None,
    authority_root: Path,
    ledger: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, tuple[str, tuple[int, int]]]:
    """Validate exact hard evidence and map it to normalized record-body ranges."""

    if truth is None:
        return {}
    result: dict[str, tuple[str, tuple[int, int]]] = {}
    for row in truth.get("authoritative_evidence", []):
        if not isinstance(row, Mapping):
            raise ScoreError("hard-evidence-contract")
        source_id, path = row.get("source_id"), row.get("path")
        if not isinstance(source_id, str) or not isinstance(path, str):
            raise ScoreError("hard-evidence-identity")
        authority_path = (authority_root / path).resolve()
        if authority_root.resolve() not in authority_path.parents:
            raise ScoreError("unsafe-hard-evidence-path")
        payload = authority_path.read_bytes()
        text = payload.decode("utf-8-sig")
        if hashlib.sha256(payload).hexdigest() != row.get("file_sha256"):
            raise ScoreError("hard-evidence-file-hash")
        start, end = row.get("start_char"), row.get("end_char")
        if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(text):
            raise ScoreError("hard-evidence-range")
        selected = text[start:end]
        if sha256_text(selected) != row.get("text_sha256"):
            raise ScoreError("hard-evidence-text-hash")
        matches = [record for key, record in ledger.items() if key[0] == source_id]
        if len(matches) != 1 or not isinstance(matches[0].get("body"), str):
            raise ScoreError("hard-evidence-ledger-join")
        body = matches[0]["body"]
        # The frozen authoritative corpus retains CRLF bytes, while normalized
        # Semantic OKF record bodies use LF. Validate the authoritative hash
        # before this deterministic normalization, then map the same passage
        # into the derived record body.
        normalized_selected = selected.replace("\r\n", "\n").replace("\r", "\n")
        # Semantic OKF record bodies omit terminal file blank lines. A hard
        # locator that intentionally reaches EOF still binds the same raw
        # bytes, but its normalized range must exclude those publication-only
        # newlines before joining to the derived record body.
        mapped_selected = normalized_selected
        offset = body.find(mapped_selected)
        if offset < 0 and mapped_selected.endswith("\n"):
            mapped_selected = mapped_selected.rstrip("\n")
            offset = body.find(mapped_selected)
        if not mapped_selected or offset < 0 or body.find(mapped_selected, offset + 1) >= 0:
            raise ScoreError("hard-evidence-body-map")
        result[str(row["id"])] = (source_id, (offset, offset + len(mapped_selected)))
    return result


def group_completeness(groups: Any, covered: set[str]) -> float:
    """Score groups that require all declared evidence anchors."""

    if not isinstance(groups, list):
        return 1.0
    outcomes = []
    for row in groups:
        evidence_ids = row.get("evidence_ids") if isinstance(row, Mapping) else None
        outcomes.append(isinstance(evidence_ids, list) and set(evidence_ids).issubset(covered))
    return ratio(sum(outcomes), len(outcomes), empty=1.0)


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    """Write stable JSON after creating the parent directory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def score(args: argparse.Namespace) -> tuple[dict[str, float], dict[str, Any]]:
    """Score one answer and return rewards plus redacted diagnostics."""

    question = load_json(args.question)
    ledger_rows = load_jsonl(args.ledger)
    ledger = {(str(row.get("source_id")), str(row.get("record_id"))): row for row in ledger_rows}
    if len(ledger) != len(ledger_rows):
        raise ScoreError("duplicate-ledger-identity")
    combination = load_json(args.crosswalk)
    records = combination.get("records")
    if not isinstance(records, list):
        raise ScoreError("crosswalk-records")
    crosswalk = {
        (str(row.get("source_id")), str(row.get("record_id"))): str(row.get("document_id"))
        for row in records
        if isinstance(row, Mapping)
    }
    trace = classify_pi_trace(args.pi_log)
    output_text = trace.get("answer_text")
    parse_error: str | None = None
    if not isinstance(output_text, str):
        output = OrderedDict()
        parse_error = "assistant-output-absent"
    else:
        try:
            output = strict_json(output_text)
        except (json.JSONDecodeError, ScoreError) as exc:
            output = OrderedDict()
            parse_error = type(exc).__name__
    contract, non_null, contract_errors = validate_contract(output, str(question["id"]))
    references = reference_validity(output) if contract and isinstance(output, Mapping) else False
    evidence = output.get("evidence", []) if isinstance(output, Mapping) else []
    evidence = evidence if isinstance(evidence, list) else []
    valid_rows, intervals = evidence_validity(evidence, ledger)
    all_evidence_valid = bool(evidence) and all(valid_rows)
    ranking = ranked_documents(evidence, crosswalk)
    relevant = set(question.get("qrels", {}).get("document_ids", []))
    metrics = retrieval_metrics(ranking, relevant)
    minimum = question.get("minimum_document_count")
    if minimum is not None and (
        isinstance(minimum, bool) or not isinstance(minimum, int) or not 1 <= minimum <= len(relevant)
    ):
        raise ScoreError("minimum-document-count")
    covered_relevant = len(set(ranking) & relevant)
    minimum_coverage = (
        min(1.0, ratio(covered_relevant, minimum)) if isinstance(minimum, int) else 1.0
    )
    minimum_gate = minimum is None or covered_relevant >= minimum
    truth = load_json(args.ground_truth) if args.ground_truth and args.ground_truth.exists() else None
    hard_ranges = authoritative_ranges(truth, args.authority_root, ledger)
    covered: set[str] = set()
    for identifier, (source_id, required_range) in hard_ranges.items():
        for row, interval, is_valid in zip(evidence, intervals, valid_rows):
            if (
                is_valid
                and isinstance(row, Mapping)
                and row.get("source_id") == source_id
                and interval is not None
                and interval[0] <= required_range[0]
                and interval[1] >= required_range[1]
            ):
                covered.add(identifier)
                break
    ground = truth.get("ground_truth", {}) if isinstance(truth, Mapping) else {}
    required_docs = set(ground.get("required_document_ids", relevant)) if isinstance(ground, Mapping) else relevant
    rewards: dict[str, float] = {
        "response_contract": float(contract),
        "non_null_answer": float(non_null),
        "reference_validity": float(references),
        "evidence_validity": ratio(sum(valid_rows), len(valid_rows)),
        "all_evidence_valid": float(all_evidence_valid),
        **metrics,
        "required_document_coverage": ratio(len(set(ranking) & required_docs), len(required_docs), empty=1.0),
        "authoritative_evidence_anchor_coverage": ratio(len(covered), len(hard_ranges), empty=1.0),
        "answer_claim_anchor_coverage": group_completeness(ground.get("answer_claims"), covered) if isinstance(ground, Mapping) else 1.0,
        "important_negative_anchor_coverage": group_completeness(ground.get("important_negatives"), covered) if isinstance(ground, Mapping) else 1.0,
        "minimum_document_coverage": minimum_coverage,
        "minimum_document_gate": float(minimum_gate),
    }
    terminal_ok = trace["outcome"] == "answer-emitted"
    gate = terminal_ok and contract and non_null and references and all_evidence_valid
    rewards["evidence_contract_gate"] = float(gate)
    rewards["mechanical_qualification_gate"] = float(gate and minimum_gate)
    if truth is None:
        utility = (
            0.35 * rewards["evidence_recall"]
            + 0.15 * rewards["evidence_precision"]
            + 0.20 * rewards["mrr"]
            + 0.30 * rewards["ndcg"]
        )
    else:
        utility = (
            0.15 * rewards["evidence_recall"]
            + 0.10 * rewards["ndcg"]
            + 0.15 * rewards["required_document_coverage"]
            + 0.15 * rewards["authoritative_evidence_anchor_coverage"]
            + 0.30 * rewards["answer_claim_anchor_coverage"]
            + 0.15 * rewards["important_negative_anchor_coverage"]
        )
    rewards["mechanical_utility"] = utility
    rewards["reward"] = rewards["mechanical_qualification_gate"] * utility
    rubric = question.get("semantic_rubric")
    required_points = rubric.get("required_points") if isinstance(rubric, Mapping) else None
    if trace.get("failure_domain") == "provider":
        status = "provider-failure"
    elif not terminal_ok:
        status = "agent-failure"
    elif not contract:
        status = "agent-invalid-response"
    else:
        status = "scored-response"
    diagnostics = {
        "schema_version": "semantic-okf-harbor-redacted-diagnostics/2.0",
        "status": status,
        "question_id": question.get("id"),
        "parse_error": parse_error,
        "contract_errors": contract_errors,
        "evidence_count": len(evidence),
        "invalid_evidence_indices": [index for index, valid in enumerate(valid_rows) if not valid],
        "cited_document_count": len(ranking),
        "covered_qrel_count": covered_relevant,
        "minimum_document_count": minimum,
        "minimum_document_gate": minimum_gate,
        "covered_hard_evidence_count": len(covered),
        "expected_hard_evidence_count": len(hard_ranges),
        "semantic_required_point_count": len(required_points) if isinstance(required_points, list) else 0,
        "semantic_correctness": (
            "manual-review-required" if terminal_ok and required_points else "not-scored"
        ),
        "terminal_outcome": trace["outcome"],
        "failure_domain": trace.get("failure_domain"),
        "error_code": trace.get("error_code"),
    }
    return rewards, diagnostics


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse verifier paths."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pi-log", type=Path, default=Path("/logs/agent/pi.txt"))
    parser.add_argument("--question", type=Path, default=Path("/tests/question.json"))
    parser.add_argument("--ledger", type=Path, default=Path("/tests/records.jsonl"))
    parser.add_argument("--crosswalk", type=Path, default=Path("/tests/source-combination.json"))
    parser.add_argument("--ground-truth", type=Path)
    parser.add_argument("--authority-root", type=Path, default=Path("/tests/authority"))
    parser.add_argument("--reward", type=Path, default=Path("/logs/verifier/reward.json"))
    parser.add_argument("--diagnostics", type=Path, default=Path("/logs/verifier/diagnostics.json"))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run scoring, emitting zero rewards on answer failures and failing on corrupt gold."""

    args = parse_args(argv)
    try:
        rewards, diagnostics = score(args)
    except (OSError, UnicodeError, ScoreError, KeyError, TypeError, ValueError) as exc:
        rewards = {
            "reward": 0.0,
            "evidence_contract_gate": 0.0,
            "mechanical_qualification_gate": 0.0,
        }
        diagnostics = {
            "schema_version": "semantic-okf-harbor-redacted-diagnostics/2.0",
            "status": "verifier-error",
            "error_type": type(exc).__name__,
        }
    write_json(args.reward, rewards)
    write_json(args.diagnostics, diagnostics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
