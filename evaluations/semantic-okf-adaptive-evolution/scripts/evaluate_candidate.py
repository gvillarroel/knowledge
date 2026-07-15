#!/usr/bin/env python3
"""Score one adaptive skill candidate against the immutable benchmark."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


SCHEMA_VERSION = "semantic-okf-adaptive-candidate-fitness/1.0"
FROZEN_MANIFEST_SHA256 = (
    "2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414"
)
LOCATOR_RE = re.compile(r"PDF-page-([1-9][0-9]*)")
TOLERANCE = 1e-8


class EvaluationError(ValueError):
    """Describe an invalid candidate or evaluation input."""


def _module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise EvaluationError(f"cannot load module: {path}")
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvaluationError(f"expected JSON object: {path}")
    return value


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not all(isinstance(row, dict) for row in rows):
        raise EvaluationError(f"expected JSON objects: {path}")
    return rows


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _safe_file(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise EvaluationError(f"invalid {label} path: {relative!r}")
    path = root.joinpath(*relative.split("/"))
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise EvaluationError(f"unsafe or missing {label} path: {relative}") from exc
    if not resolved.is_file():
        raise EvaluationError(f"{label} path is not a file: {relative}")
    return resolved


def _mean(rows: Iterable[float]) -> float:
    values = list(rows)
    return statistics.fmean(values) if values else 0.0


def _expected_claims(ground_truth: dict[str, Any], key: str) -> set[str]:
    groups = ground_truth.get(key)
    if not isinstance(groups, list):
        raise EvaluationError(f"ground truth {key} must be an array")
    result: set[str] = set()
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("evidence_claim_ids"), list):
            raise EvaluationError(f"ground truth {key} contains an invalid claim group")
        result.update(group["evidence_claim_ids"])
    return result


def _recall(returned: set[str], expected: set[str]) -> float:
    if not expected:
        return 1.0
    return len(returned & expected) / len(expected)


def _validate_pack(
    bundle: Path,
    source_root: Path,
    pack: dict[str, Any],
    binding_by_id: dict[str, dict[str, Any]],
) -> tuple[set[str], set[str], list[str]]:
    issues: list[str] = []
    ranked = pack.get("ranked_bindings")
    if not isinstance(ranked, list):
        raise EvaluationError("evidence pack ranked_bindings must be an array")
    seen_bindings: set[str] = set()
    expected_claim_rows: list[dict[str, Any]] = []
    pages_by_paper: defaultdict[str, set[int]] = defaultdict(set)
    returned_claims: set[str] = set()
    returned_papers: set[str] = set()
    copied_fields = (
        "source_id",
        "record_id",
        "record_sha256",
        "concept_id",
        "concept_type",
        "concept_path",
        "source_path",
        "paper_id",
        "review_state",
        "locator_tokens",
        "citation_pages",
        "evidence_paths",
        "authoritative_text",
        "authoritative_text_sha256",
    )
    for rank, row in enumerate(ranked, 1):
        if not isinstance(row, dict) or row.get("rank") != rank:
            issues.append(f"rank {rank}: invalid rank or row")
            continue
        binding_id = row.get("binding_id")
        binding = binding_by_id.get(binding_id)
        if binding is None or binding_id in seen_bindings:
            issues.append(f"rank {rank}: unknown or duplicate binding")
            continue
        seen_bindings.add(binding_id)
        for field in copied_fields:
            if row.get(field) != binding.get(field):
                issues.append(f"rank {rank}: {field} differs from derived binding")
        text = row.get("authoritative_text")
        if not isinstance(text, str) or hashlib.sha256(text.encode("utf-8")).hexdigest() != row.get(
            "authoritative_text_sha256"
        ):
            issues.append(f"rank {rank}: authoritative text hash differs")
        locators = row.get("locator_tokens")
        pages = row.get("citation_pages")
        if (
            not isinstance(locators, list)
            or not isinstance(pages, list)
            or any(not isinstance(locator, str) or LOCATOR_RE.fullmatch(locator) is None for locator in locators)
            or any(isinstance(page, bool) or not isinstance(page, int) or page < 1 for page in pages)
            or [int(LOCATOR_RE.fullmatch(locator).group(1)) for locator in locators] != pages
        ):
            issues.append(f"rank {rank}: locator strings and integer pages disagree")
        try:
            _safe_file(bundle, row.get("concept_path"), "bundle concept")
        except EvaluationError as exc:
            issues.append(f"rank {rank}: {exc}")
        try:
            _safe_file(source_root, row.get("source_path"), "authoritative source")
        except EvaluationError as exc:
            issues.append(f"rank {rank}: {exc}")
        for relative in row.get("evidence_paths", []):
            try:
                _safe_file(source_root, relative, "authoritative evidence")
            except EvaluationError as exc:
                issues.append(f"rank {rank}: {exc}")
        paper_id = row.get("paper_id")
        if isinstance(paper_id, str):
            returned_papers.add(paper_id)
            if isinstance(pages, list):
                pages_by_paper[paper_id].update(page for page in pages if isinstance(page, int))
        if isinstance(row.get("concept_type"), str) and "claim" in row["concept_type"].casefold():
            claim_id = row.get("record_id")
            if isinstance(claim_id, str):
                returned_claims.add(claim_id)
                expected_claim_rows.append(
                    {
                        "claim_id": claim_id,
                        "concept_path": row["concept_path"],
                        "paper_id": row["paper_id"],
                        "source_path": row["source_path"],
                        "locators": row["locator_tokens"],
                    }
                )
    expected_claim_rows.sort(key=lambda row: row["claim_id"])
    if pack.get("claim_evidence") != expected_claim_rows:
        issues.append("claim_evidence is not the exact sorted projection of ranked bindings")
    expected_citations = [
        {"paper_id": paper_id, "pages": sorted(pages)}
        for paper_id, pages in sorted(pages_by_paper.items())
    ]
    if pack.get("citations") != expected_citations:
        issues.append("citations are not the exact typed aggregation of ranked bindings")
    return returned_claims, returned_papers, issues


def _render(report: dict[str, Any]) -> str:
    gates = report["hard_gates"]
    metrics = report["metrics"]
    lines = [
        "# Adaptive Candidate Offline Fitness",
        "",
        f"Candidate: `{report['candidate']}`. Frozen benchmark: `{report['benchmark']['benchmark_id']}`.",
        "",
        f"Hard-gate status: **{gates['status']}**. Fitness: **{report['fitness']['score']:.2f}/100**.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| All-40 paper Recall@10 | {metrics['retrieval']['recall_at_10']:.6f} |",
        f"| All-40 paper nDCG@10 | {metrics['retrieval']['ndcg_at_10']:.6f} |",
        f"| Hard-10 atomic answer-claim Recall@30 | {metrics['answer_claim_recall_at_30']:.6f} |",
        f"| Hard-10 important-negative claim Recall@30 | {metrics['important_negative_recall_at_30']:.6f} |",
        f"| Hard-10 required-paper Recall@30 | {metrics['required_paper_recall_at_30']:.6f} |",
        f"| Evidence-contract validity | {metrics['evidence_contract_validity']:.6f} |",
        f"| Mean evidence-pack latency (ms) | {metrics['evidence_pack_latency_ms']['mean']:.3f} |",
        "",
        "## Gate checks",
        "",
    ]
    lines.extend(
        f"- {'PASS' if item['pass'] else 'FAIL'} — {name}: {item['detail']}"
        for name, item in gates["checks"].items()
    )
    lines.extend(["", "## Per-question exact retrieval", "", "| Question | Answer claims | Negatives | Papers | Contract |", "| --- | ---: | ---: | ---: | ---: |"])
    for row in report["questions"]:
        lines.append(
            f"| {row['id']} | {row['answer_claim_recall_at_30']:.3f} | "
            f"{row['important_negative_recall_at_30']:.3f} | "
            f"{row['required_paper_recall_at_30']:.3f} | "
            f"{row['evidence_contract_validity']:.3f} |"
        )
    lines.append("")
    return "\n".join(lines)


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo_root.resolve(strict=True)
    bundle = args.bundle.resolve(strict=True)
    source_root = (repo / "evaluations/graphrag-cross-paper").resolve(strict=True)
    frozen_path = repo / "evaluations/semantic-okf-adaptive-evolution/frozen-benchmark.json"
    frozen_module = _module(
        "semantic_okf_adaptive_frozen_validator",
        repo / "evaluations/semantic-okf-adaptive-evolution/scripts/validate_frozen_benchmark.py",
    )
    frozen = frozen_module.validate(repo, frozen_path)
    if frozen["manifest_sha256"] != FROZEN_MANIFEST_SHA256:
        raise EvaluationError("frozen manifest identity differs")
    questions = _load_jsonl(args.questions.resolve(strict=True))
    truth_rows = _load_jsonl(args.ground_truth.resolve(strict=True))
    if [row["id"] for row in questions] != [row["id"] for row in truth_rows]:
        raise EvaluationError("hard question and ground-truth IDs differ")
    runtime_path = args.runtime.resolve(strict=True)
    runtime = _module("semantic_okf_adaptive_candidate_runtime", runtime_path)
    before = _tree(bundle)
    snapshot = runtime.load_snapshot(bundle, deep_validation=True)
    binding_by_id = {row["binding_id"]: row for row in snapshot.answer_bindings}
    per_question: list[dict[str, Any]] = []
    latencies: list[float] = []
    total_rows = 0
    invalid_rows = 0
    for question, truth_row in zip(questions, truth_rows, strict=True):
        packs: list[dict[str, Any]] = []
        for _ in range(args.repetitions):
            started = time.perf_counter()
            packs.append(
                runtime.build_evidence_pack(snapshot, question["question"], args.top_k)
            )
            latencies.append((time.perf_counter() - started) * 1000.0)
        if any(candidate != packs[0] for candidate in packs[1:]):
            raise EvaluationError(
                f"evidence-pack output is nondeterministic for {question['id']}"
            )
        pack = packs[0]
        returned_claims, returned_papers, issues = _validate_pack(
            bundle, source_root, pack, binding_by_id
        )
        expected_answers = _expected_claims(truth_row["ground_truth"], "answer_claims")
        expected_negatives = _expected_claims(truth_row["ground_truth"], "important_negatives")
        expected_papers = set(truth_row["ground_truth"]["required_paper_ids"])
        returned = len(pack["ranked_bindings"])
        total_rows += returned
        invalid_rows += returned if issues else 0
        per_question.append(
            {
                "id": question["id"],
                "returned": returned,
                "answer_claim_recall_at_30": _recall(returned_claims, expected_answers),
                "important_negative_recall_at_30": _recall(returned_claims, expected_negatives),
                "required_paper_recall_at_30": _recall(returned_papers, expected_papers),
                "evidence_contract_validity": 0.0 if issues else 1.0,
                "issues": issues,
            }
        )
    after = _tree(bundle)
    retrieval = _load_json(args.retrieval_report.resolve(strict=True))
    incumbent = _load_json(args.incumbent_summary.resolve(strict=True))
    adaptive_route = next(route for route in retrieval["routes"] if route["name"] == "adaptive_fusion")
    incumbent_route = incumbent["routes"]["adaptive_fusion"]
    candidate_recall = float(adaptive_route["paper_metrics"]["recall_at_10"])
    candidate_ndcg = float(adaptive_route["paper_metrics"]["ndcg_at_10"])
    incumbent_recall = float(incumbent_route["all_40"]["recall_at_10"])
    incumbent_ndcg = float(incumbent_route["all_40"]["ndcg_at_10"])
    question_ids = [row["id"] for row in _load_jsonl(repo / "evaluations/semantic-okf-adaptive/retrieval-questions.jsonl")]
    adaptive_bytes = b"\n".join(path.read_bytes() for path in sorted((bundle / "adaptive").glob("*")) if path.is_file())
    leaked_ids = [identifier for identifier in question_ids if identifier.encode("utf-8") in adaptive_bytes]
    contract_validity = 1.0 - (invalid_rows / total_rows if total_rows else 1.0)
    answer_recall = _mean(row["answer_claim_recall_at_30"] for row in per_question)
    negative_recall = _mean(row["important_negative_recall_at_30"] for row in per_question)
    paper_recall = _mean(row["required_paper_recall_at_30"] for row in per_question)
    candidate_latency = _mean(latencies)
    incumbent_latency = float(incumbent_route["timing_ms"]["mean"])
    checks = {
        "frozen_benchmark": {"pass": True, "detail": frozen["manifest_sha256"]},
        "read_only": {"pass": before == after, "detail": f"{len(before)} files unchanged"},
        "question_id_isolation": {"pass": not leaked_ids, "detail": f"leaked IDs: {leaked_ids}"},
        "core_parity": {
            "pass": retrieval["core_semantic_parity"]["status"] == "pass",
            "detail": retrieval["core_semantic_parity"]["status"],
        },
        "retrieval_recall_no_regression": {
            "pass": candidate_recall + TOLERANCE >= incumbent_recall,
            "detail": f"candidate {candidate_recall:.9f}; incumbent {incumbent_recall:.9f}",
        },
        "retrieval_ndcg_no_regression": {
            "pass": candidate_ndcg + TOLERANCE >= incumbent_ndcg,
            "detail": f"candidate {candidate_ndcg:.9f}; incumbent {incumbent_ndcg:.9f}",
        },
        "retrieval_evidence_validity": {
            "pass": adaptive_route["evidence_validity"]["ratio"] == 1.0,
            "detail": str(adaptive_route["evidence_validity"]["ratio"]),
        },
        "answer_evidence_validity": {
            "pass": math.isclose(contract_validity, 1.0),
            "detail": f"{contract_validity:.9f}",
        },
    }
    gate_pass = all(item["pass"] for item in checks.values())
    components = {
        "retrieval_recall": 10.0 * min(1.0, candidate_recall / incumbent_recall),
        "retrieval_ndcg": 10.0 * min(1.0, candidate_ndcg / incumbent_ndcg),
        "answer_claim_recall": 30.0 * answer_recall,
        "important_negative_recall": 15.0 * negative_recall,
        "required_paper_recall": 15.0 * paper_recall,
        "evidence_contract_validity": 15.0 * contract_validity,
        "operational_efficiency": 5.0 * min(1.0, incumbent_latency / candidate_latency),
    }
    score = sum(components.values()) if gate_pass else 0.0
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate": args.candidate,
        "benchmark": frozen,
        "inputs": {
            "bundle": str(bundle.relative_to(repo)).replace("\\", "/"),
            "runtime": str(runtime_path.relative_to(repo)).replace("\\", "/"),
            "questions_sha256": _sha256(args.questions.resolve(strict=True)),
            "ground_truth_sha256": _sha256(args.ground_truth.resolve(strict=True)),
            "retrieval_report_sha256": _sha256(args.retrieval_report.resolve(strict=True)),
            "top_k": args.top_k,
            "repetitions_per_question": args.repetitions,
            "answer_binding_count": len(binding_by_id),
        },
        "hard_gates": {"status": "pass" if gate_pass else "fail", "checks": checks},
        "metrics": {
            "retrieval": {
                "recall_at_10": candidate_recall,
                "ndcg_at_10": candidate_ndcg,
                "incumbent_recall_at_10": incumbent_recall,
                "incumbent_ndcg_at_10": incumbent_ndcg,
            },
            "answer_claim_recall_at_30": answer_recall,
            "important_negative_recall_at_30": negative_recall,
            "required_paper_recall_at_30": paper_recall,
            "evidence_contract_validity": contract_validity,
            "evidence_pack_latency_ms": {
                "mean": candidate_latency,
                "median": statistics.median(latencies),
                "maximum": max(latencies),
                "incumbent_adaptive_search_mean": incumbent_latency,
            },
        },
        "fitness": {"score": score, "maximum": 100.0, "components": components},
        "questions": per_question,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--retrieval-report", type=Path, required=True)
    parser.add_argument("--incumbent-summary", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=30)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()
    if args.top_k != 30 or args.repetitions != 3:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "error": "the frozen fitness contract requires top-k 30 and three repetitions",
                }
            )
        )
        return 2
    try:
        report = evaluate(args)
    except (EvaluationError, OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_markdown.write_text(_render(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["hard_gates"]["status"],
                "candidate": report["candidate"],
                "fitness": round(report["fitness"]["score"], 6),
                "answer_claim_recall_at_30": round(
                    report["metrics"]["answer_claim_recall_at_30"], 8
                ),
            },
            sort_keys=True,
        )
    )
    return 0 if report["hard_gates"]["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
