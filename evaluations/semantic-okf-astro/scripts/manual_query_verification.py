#!/usr/bin/env python3
"""Repeat the frozen q040 query through every selected no-MCP consult family."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
REPORTS = EVALUATION / "reports"
DEFAULT_RUN = EVALUATION / "results" / "runs" / "20260716-astro-generic-01"
SCHEMA = "semantic-okf-astro-manual-query-verification/1.0"
QUESTION_ID = "q040"
ANSWER_EVIDENCE_LIMIT = 5
SELECTED_ROUTES = {
    "legacy": "legacy_tfidf",
    "embeddings": "lexical",
    "classical": "association",
    "adaptive": "association",
    "entity-graph": "entity",
    "ensemble": "quality",
}


class VerificationError(RuntimeError):
    """Describe an invalid input or a failed manual-query quality gate."""


def load_script(name: str, path: Path) -> ModuleType:
    """Load a colocated evaluation script through its real file boundary."""

    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise VerificationError(f"cannot import evaluation helper: {path}")
    module = importlib.util.module_from_spec(specification)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        specification.loader.exec_module(module)
    except Exception:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
        raise
    return module


RETRIEVAL = load_script(
    "astro_manual_retrieval_helpers", SCRIPT.with_name("evaluate_retrieval.py")
)
ANSWERS = load_script(
    "astro_manual_answer_helpers", SCRIPT.with_name("compare_hard_answers.py")
)


def strict_selected_routes(path: Path) -> dict[str, str]:
    """Bind the manual check to the checked retrieval report's best routes."""

    report = RETRIEVAL.load_json(path)
    if report.get("schema_version") != RETRIEVAL.SCHEMA or report.get("status") != "pass":
        raise VerificationError("retrieval comparison is not a passing schema-1.0 report")
    rows = report.get("families")
    if not isinstance(rows, list):
        raise VerificationError("retrieval comparison has no families array")
    selected: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise VerificationError("retrieval comparison contains a malformed family")
        family, route = row.get("family"), row.get("best_route")
        if not isinstance(family, str) or not isinstance(route, str):
            raise VerificationError("retrieval comparison family selection is incomplete")
        if family in selected:
            raise VerificationError(f"duplicate retrieval family: {family}")
        selected[family] = route
    if selected != SELECTED_ROUTES:
        raise VerificationError(
            f"selected routes changed; expected {SELECTED_ROUTES}, found {selected}"
        )
    return selected


def signature_rows(hits: Sequence[Any], *, evidence: bool) -> list[dict[str, Any]]:
    """Project normalized hits into ranking or independently checkable evidence."""

    rows: list[dict[str, Any]] = []
    for rank, hit in enumerate(hits, 1):
        if evidence:
            rows.append(
                {
                    "rank": rank,
                    "source_id": hit.source_id,
                    "record_id": hit.record_id,
                    "document_id": hit.document_id,
                    "record_sha256": hit.record_sha256,
                    "source_path": hit.source_path,
                    "locator": hit.locator,
                    "text_sha256": hit.text_sha256,
                }
            )
        else:
            rows.append(
                {
                    "rank": rank,
                    "source_id": hit.source_id,
                    "record_id": hit.record_id,
                    "document_id": hit.document_id,
                    "retrieval_id": hit.retrieval_id,
                    "score": hit.score,
                }
            )
    return rows


def signature(hits: Sequence[Any], *, evidence: bool) -> str:
    """Hash a complete ordered candidate pool without retaining its full text."""

    return RETRIEVAL.sha256_bytes(
        RETRIEVAL.canonical_json(signature_rows(hits, evidence=evidence)).encode("utf-8")
    )


def compact_answer_pack(
    question: Any,
    hits: Sequence[Any],
    validations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Create a small, ground-truth-blind extractive answer and exact citations."""

    retained = [
        RETRIEVAL.compact_hit(hit, validation, rank)
        for rank, (hit, validation) in enumerate(zip(hits, validations), 1)
    ]
    generated = ANSWERS.make_answer(
        question.identifier,
        question.text,
        retained,
        ANSWER_EVIDENCE_LIMIT,
    )
    answer = generated.get("answer")
    if isinstance(answer, dict) and isinstance(answer.get("claims"), list):
        claims: list[dict[str, Any]] = []
        for claim in answer["claims"]:
            if not isinstance(claim, dict):
                continue
            statement = claim.get("statement")
            if isinstance(statement, str) and len(statement) > 280:
                statement = statement[:279].rstrip() + "…"
            claims.append(
                {
                    "id": claim.get("id"),
                    "statement": statement,
                    "document_id": claim.get("document_id"),
                    "evidence_rank": claim.get("evidence_rank"),
                }
            )
        answer = {
            "summary": " ".join(
                f"[{claim['document_id']}] {claim['statement']}"
                for claim in claims
                if isinstance(claim.get("statement"), str)
            )
            or None,
            "claims": claims,
            "document_ids": sorted(
                {
                    claim["document_id"]
                    for claim in claims
                    if isinstance(claim.get("document_id"), str)
                }
            ),
        }
    return {
        "method": "ground-truth-blind diversified query-overlap extract",
        "answer": answer,
        "evidence": generated.get("evidence", []),
    }


def verify_family(
    family: str,
    route: str,
    question: Any,
    bundle: Path,
    ledger: Any,
    search: Callable[[str], Sequence[Any]],
) -> dict[str, Any]:
    """Run one selected route twice and apply determinism, evidence, and read-only gates."""

    before = RETRIEVAL.bundle_identity(bundle)
    runs: list[dict[str, Any]] = []
    first_hits: list[Any] = []
    first_validations: list[dict[str, Any]] = []
    for run_number in (1, 2):
        hits = list(search(question.text))
        validations = [ledger.validate(hit) for hit in hits]
        if run_number == 1:
            first_hits = hits
            first_validations = validations
        documents = RETRIEVAL.deduplicate(hit.document_id for hit in hits)
        metrics = RETRIEVAL.ranking_metrics(documents, set(question.document_ids))
        runs.append(
            {
                "run": run_number,
                "returned": len(hits),
                "valid_evidence": sum(row.get("valid") is True for row in validations),
                "invalid_evidence": sum(row.get("valid") is not True for row in validations),
                "ranking_signature_sha256": signature(hits, evidence=False),
                "evidence_signature_sha256": signature(hits, evidence=True),
                "required_document_recall_at_10": metrics["recall_at_10"],
                "top_10_document_ids": documents[:10],
            }
        )
    after = RETRIEVAL.bundle_identity(bundle)
    ranking_deterministic = (
        runs[0]["ranking_signature_sha256"] == runs[1]["ranking_signature_sha256"]
    )
    evidence_deterministic = (
        runs[0]["evidence_signature_sha256"] == runs[1]["evidence_signature_sha256"]
    )
    bundle_unchanged = before == after
    all_evidence_valid = all(row["invalid_evidence"] == 0 for row in runs)
    status = (
        "pass"
        if ranking_deterministic
        and evidence_deterministic
        and bundle_unchanged
        and all_evidence_valid
        else "fail"
    )
    return {
        "family": family,
        "route": route,
        "status": status,
        "execution": (
            "two repeated warm in-process reads of one deep-validated published bundle; "
            "no route fallback"
            if family != "legacy"
            else "two repeated reads of one evaluator-side deterministic TF-IDF index"
        ),
        "run_count": 2,
        "ranking_deterministic": ranking_deterministic,
        "evidence_deterministic": evidence_deterministic,
        "all_evidence_valid": all_evidence_valid,
        "bundle_unchanged": bundle_unchanged,
        "bundle_identity_before": before,
        "bundle_identity_after": after,
        "runs": runs,
        "answer_pack": compact_answer_pack(question, first_hits, first_validations),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the gates and concise answer packs for human review."""

    question = report["question"]
    lines = [
        "# Astro q040 Manual Query Verification",
        "",
        f"Question: {question['text']}",
        "",
        "Each selected route was executed twice against the same published bundle. Ranking and evidence signatures cover the complete route result, up to the 100-hit candidate-pool limit. Every retained locator and text hash was independently checked against the authoritative ledger, and the bundle tree was hashed before and after consultation.",
        "",
        "| Family | Route | Returned | Valid evidence | Rank deterministic | Evidence deterministic | Bundle unchanged | Required-doc R@10 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["families"]:
        first = row["runs"][0]
        lines.append(
            f"| {row['family']} | {row['route']} | {first['returned']} | "
            f"{first['valid_evidence']}/{first['returned']} | "
            f"{'yes' if row['ranking_deterministic'] else 'no'} | "
            f"{'yes' if row['evidence_deterministic'] else 'no'} | "
            f"{'yes' if row['bundle_unchanged'] else 'no'} | "
            f"{100.0 * first['required_document_recall_at_10']:.1f}% |"
        )
    lines.extend(
        [
            "",
            "The extracts below are deterministic, ground-truth-blind evidence packs. They demonstrate what each route exposes; they are not a semantic correctness judgment and may be incomplete even when every citation is valid.",
            "",
        ]
    )
    for row in report["families"]:
        answer = row["answer_pack"].get("answer")
        lines.extend([f"## {row['family']} / {row['route']}", ""])
        if not isinstance(answer, Mapping) or not answer.get("summary"):
            lines.append("No extractive answer was produced.")
        else:
            lines.append(str(answer["summary"]))
        lines.append("")
    lines.extend(
        [
            "All execution is local and offline. The active verification has no MCP dependency.",
            "",
        ]
    )
    rendered = "\n".join(lines)
    return "\n".join(line.rstrip() for line in rendered.split("\n"))


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Load the frozen q040 inputs and verify all six selected alternatives."""

    selected = strict_selected_routes(args.retrieval_report)
    identity, documents = RETRIEVAL.load_identity_map(args.source_combination)
    questions = RETRIEVAL.load_questions(args.questions, documents)
    question = next((row for row in questions if row.identifier == QUESTION_ID), None)
    if question is None:
        raise VerificationError(f"missing frozen question {QUESTION_ID}")
    families: list[dict[str, Any]] = []
    for family, route in selected.items():
        bundle = args.run_dir / "bundles" / f"{family}-a"
        if not bundle.is_dir():
            raise VerificationError(f"missing published bundle: {bundle}")
        ledger = RETRIEVAL.Ledger(bundle, identity)
        if family == "legacy":
            index = RETRIEVAL.LegacyIndex(ledger)
            search = lambda query, active=index: active.search(query, RETRIEVAL.RAW_POOL)
        else:
            searchers = RETRIEVAL.warm_searchers(family, bundle, ledger)
            if route not in searchers:
                raise VerificationError(f"selected route does not exist: {family}/{route}")
            search = searchers[route]
        families.append(verify_family(family, route, question, bundle, ledger, search))
        print(f"[astro-manual] {family}/{route}: {families[-1]['status']}", file=sys.stderr, flush=True)
    status = "pass" if all(row["status"] == "pass" for row in families) else "fail"
    return {
        "schema_version": SCHEMA,
        "status": status,
        "execution_contract": {
            "question_id": QUESTION_ID,
            "repeat_count": 2,
            "candidate_pool": RETRIEVAL.RAW_POOL,
            "route_selection": "best family routes frozen by retrieval-comparison schema 1.0",
            "answer_method": "ground-truth-blind diversified query-overlap extract",
            "network": "offline",
            "mcp_dependency": False,
        },
        "question": {
            "id": question.identifier,
            "type": question.cohort,
            "text": question.text,
            "sha256": RETRIEVAL.sha256_bytes(question.text.encode("utf-8")),
            "required_document_ids": list(question.document_ids),
            "required_source_ids": list(question.source_ids),
        },
        "inputs": {
            "run_dir": args.run_dir.relative_to(REPO).as_posix(),
            "questions": {
                "path": args.questions.relative_to(REPO).as_posix(),
                "sha256": RETRIEVAL.sha256_file(args.questions),
            },
            "source_combination": {
                "path": args.source_combination.relative_to(REPO).as_posix(),
                "sha256": RETRIEVAL.sha256_file(args.source_combination),
            },
            "retrieval_report": {
                "path": args.retrieval_report.relative_to(REPO).as_posix(),
                "sha256": RETRIEVAL.sha256_file(args.retrieval_report),
            },
        },
        "families": families,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse reproducible input and compact-report paths."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument(
        "--questions",
        type=Path,
        default=EVALUATION / "benchmark" / "retrieval-questions.jsonl",
    )
    parser.add_argument(
        "--source-combination",
        type=Path,
        default=EVALUATION / "corpus" / "source-combination.json",
    )
    parser.add_argument(
        "--retrieval-report",
        type=Path,
        default=REPORTS / "retrieval-comparison.json",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=REPORTS / "manual-query-verification.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPORTS / "manual-query-verification.md",
    )
    args = parser.parse_args(argv)
    for name in (
        "run_dir",
        "questions",
        "source_combination",
        "retrieval_report",
        "json_output",
        "markdown_output",
    ):
        setattr(args, name, getattr(args, name).resolve())
    for name in ("run_dir", "questions", "source_combination", "retrieval_report"):
        if not getattr(args, name).exists():
            parser.error(f"{name.replace('_', ' ')} does not exist: {getattr(args, name)}")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Run all gates and publish deterministic compact reports atomically."""

    args = parse_args(argv)
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    try:
        report = evaluate(args)
        RETRIEVAL.atomic_write(args.json_output, RETRIEVAL.pretty_json(report))
        RETRIEVAL.atomic_write(args.markdown_output, render_markdown(report))
    except (VerificationError, RETRIEVAL.EvaluationError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": report["status"],
                "families": len(report["families"]),
                "json": str(args.json_output),
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
