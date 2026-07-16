#!/usr/bin/env python3
"""Run one real read-only CLI query against every compatible consultation family."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from _retrieval_eval import (
    AuthoritativeLedger,
    EvaluationError,
    RetrievalHit,
    load_json,
    parse_search_payload,
    sha256_bytes,
)


REPOSITORY = Path(__file__).resolve().parents[3]
EVALUATION = Path(__file__).resolve().parents[1]
DEFAULT_QUESTION_ID = "q030-causal-evidence-map"
JSON_OUTPUT = EVALUATION / "reports/manual-query-verification.json"
MARKDOWN_OUTPUT = EVALUATION / "reports/manual-query-verification.md"


class VerificationError(RuntimeError):
    """Describe a failed manual CLI verification contract."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def tree_sha256(root: Path) -> str:
    rows: list[bytes] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if not path.is_file() or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        rows.append(
            relative.as_posix().encode("utf-8")
            + b"\0"
            + hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii")
            + b"\n"
        )
    if not rows:
        raise VerificationError(f"bundle is empty: {root}")
    return hashlib.sha256(b"".join(rows)).hexdigest()


def load_question(identifier: str) -> str:
    path = EVALUATION / "benchmark/hard-questions.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    matches = [row["question"] for row in rows if row.get("id") == identifier]
    if len(matches) != 1:
        raise VerificationError(f"expected exactly one question {identifier}")
    return matches[0]


def paper_id(source_id: object) -> str | None:
    if not isinstance(source_id, str):
        return None
    for prefix in ("paper-", "claims-"):
        if source_id.startswith(prefix + "pmc"):
            return source_id.removeprefix(prefix).upper()
    return None


def _legacy_hits(payload: Mapping[str, Any], identity_by_source: Mapping[str, str]) -> list[RetrievalHit]:
    """Normalize ledger rows into the exact discovery-hit contract used by other CLIs."""

    rows = payload.get("records")
    if not isinstance(rows, list):
        raise VerificationError("legacy CLI payload has no records array")
    hits: list[RetrievalHit] = []
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise VerificationError(f"legacy record {number} is not an object")
        source_id = row.get("source_id") if isinstance(row.get("source_id"), str) else None
        body = row.get("body") if isinstance(row.get("body"), str) else None
        hits.append(
            RetrievalHit(
                source_id=source_id,
                paper_id=identity_by_source.get(source_id) if source_id else None,
                record_id=row.get("record_id") if isinstance(row.get("record_id"), str) else None,
                record_sha256=(
                    row.get("record_sha256") if isinstance(row.get("record_sha256"), str) else None
                ),
                concept_id=row.get("concept_id") if isinstance(row.get("concept_id"), str) else None,
                concept_path=(
                    row.get("concept_path").replace("\\", "/")
                    if isinstance(row.get("concept_path"), str)
                    else None
                ),
                source_path=(
                    row.get("source_path").replace("\\", "/")
                    if isinstance(row.get("source_path"), str)
                    else None
                ),
                locator={"kind": "record"},
                text=body,
                text_sha256=sha256_bytes(body.encode("utf-8")) if body is not None else None,
                score=None,
                retrieval_id=f"legacy-ledger-row-{number}",
            )
        )
    return hits


def normalize_hits(
    family: str,
    payload: Mapping[str, Any],
    identity_by_source: Mapping[str, str],
    ledger: AuthoritativeLedger,
) -> tuple[list[RetrievalHit], set[int]]:
    if family == "legacy":
        return _legacy_hits(payload, identity_by_source), set()
    try:
        hits = parse_search_payload(payload, identity_by_source)
    except EvaluationError as exc:
        raise VerificationError(f"{family} CLI returned an invalid search payload: {exc}") from exc
    rebound: set[int] = set()
    if family == "embeddings":
        normalized: list[RetrievalHit] = []
        for number, hit in enumerate(hits, 1):
            identity = (hit.source_id, hit.record_id)
            record = ledger.by_identity.get(identity) if all(isinstance(value, str) for value in identity) else None
            if hit.record_sha256 is None and record is not None:
                hit = replace(hit, record_sha256=record["record_sha256"])
                rebound.add(number)
            normalized.append(hit)
        hits = normalized
    return hits, rebound


def compact_hit(
    ledger: AuthoritativeLedger,
    hit: RetrievalHit,
    rank: int,
    rebound_hit_numbers: set[int],
) -> dict[str, Any]:
    identity = (hit.source_id, hit.record_id)
    record = ledger.by_identity.get(identity) if all(isinstance(value, str) for value in identity) else None
    if record is None:
        raise VerificationError(f"validated hit no longer binds a ledger record: {identity!r}")
    attributes = record.get("attributes") if isinstance(record.get("attributes"), dict) else {}
    return {
        "rank": rank,
        "record_id": hit.record_id,
        "source_id": hit.source_id,
        "paper_id": hit.paper_id or paper_id(hit.source_id),
        "record_sha256": hit.record_sha256,
        "record_sha256_origin": (
            "authoritative-ledger-rebound" if rank in rebound_hit_numbers else "cli"
        ),
        "concept_id": hit.concept_id,
        "concept_path": hit.concept_path,
        "source_path": hit.source_path,
        "locator": hit.locator,
        "retained_text_sha256": hit.text_sha256,
        "evidence_locator": attributes.get("evidence_locator"),
        "evidence_text_sha256": attributes.get("evidence_text_sha256"),
        "interpretation": attributes.get("interpretation"),
        "evidence_valid": True,
    }


def run_cli(
    bundles: Path,
    identity_by_source: Mapping[str, str],
    family: str,
    bundle_name: str,
    script: str,
    arguments: Sequence[str],
) -> dict[str, Any]:
    bundle = (bundles / bundle_name).resolve(strict=True)
    script_path = (REPOSITORY / script).resolve(strict=True)
    before = tree_sha256(bundle)
    command = [sys.executable, "-B", str(script_path), str(bundle), *arguments]
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=REPOSITORY,
        env=environment,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=180,
        check=False,
    )
    after = tree_sha256(bundle)
    if completed.returncode != 0:
        raise VerificationError(f"{family} CLI failed: {completed.stderr.strip() or completed.stdout.strip()}")
    try:
        value = json.loads(completed.stdout.strip())
    except json.JSONDecodeError as exc:
        raise VerificationError(f"{family} CLI did not return one JSON document") from exc
    if value.get("status") != "pass":
        raise VerificationError(f"{family} CLI returned non-pass status")
    if before != after:
        raise VerificationError(f"{family} bundle changed during consultation")
    ledger = AuthoritativeLedger(bundle)
    hits, rebound_hit_numbers = normalize_hits(family, value, identity_by_source, ledger)
    if not hits:
        raise VerificationError(f"{family} CLI returned no results")
    declared_returned = value.get("returned")
    if isinstance(declared_returned, bool) or not isinstance(declared_returned, int):
        raise VerificationError(f"{family} CLI did not declare an integer returned count")
    if declared_returned != len(hits):
        raise VerificationError(
            f"{family} CLI returned-count mismatch: declared {declared_returned}, parsed {len(hits)}"
        )
    validations = [ledger.validate_hit(hit) for hit in hits]
    invalid = [
        {"rank": number, "issues": validation["issues"]}
        for number, validation in enumerate(validations, 1)
        if not validation["valid"]
    ]
    if invalid:
        raise VerificationError(
            f"{family} CLI returned evidence that failed independent ledger validation: "
            f"{canonical_json(invalid)}"
        )
    display_command = ["python", "-B", Path(script).as_posix(), f"BUNDLE/{bundle_name}", *arguments]
    return {
        "family": family,
        "status": "pass",
        "command": display_command,
        "requested_mode": value.get("requested_mode") or value.get("mode"),
        "effective_mode": value.get("effective_mode") or value.get("mode"),
        "returned": len(hits),
        "bundle_tree_sha256_before": before,
        "bundle_tree_sha256_after": after,
        "bundle_unchanged": True,
        "evidence_valid": True,
        "evidence_validation": {
            "validator": "AuthoritativeLedger.validate_hit",
            "checked": len(validations),
            "valid": len(validations),
            "invalid": 0,
            "record_sha256_rebound_hit_count": len(rebound_hit_numbers),
            "record_sha256_rebound_unique_record_count": len(
                {
                    (hit.source_id, hit.record_id)
                    for number, hit in enumerate(hits, 1)
                    if number in rebound_hit_numbers
                }
            ),
            "fields": [
                "source_id+record_id",
                "record_sha256",
                "concept_id+concept_path+source_path",
                "retained_text+text_sha256",
                "locator",
            ],
        },
        "top_results": [
            compact_hit(ledger, hit, number, rebound_hit_numbers)
            for number, hit in enumerate(hits[:5], 1)
        ],
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Manual CLI query verification",
        "",
        f"This is a real read-only smoke query for hard question `{report['question_id']}`. It is separate from the 30-question evaluator and does not use MCP. The legacy CLI supports deterministic ledger filtering rather than ranked free-text retrieval, so its `phthalate` check is a functionality and integrity verification, not the evaluator-side TF-IDF baseline.",
        "",
        "| Family | CLI mode | Returned | First record | First paper | Evidence valid | Bundle unchanged |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for row in report["compatible_families"]:
        first = row["top_results"][0]
        lines.append(
            f"| {row['family']} | {row['effective_mode']} | {row['returned']} | "
            f"`{first['record_id']}` | {first['paper_id'] or 'N/A'} | "
            f"{'yes' if row['evidence_valid'] else 'no'} | yes |"
        )
    for row in report["incompatible_families"]:
        lines.append(f"| {row['family']} | N/A | N/A | N/A | N/A | N/A | N/A |")
    lines.extend(
        [
            "",
            "Entity-graph and ensemble have no query output because their builders fail closed on the honest PMCID/BioC corpus. Their exact diagnostics are retained in the machine-readable report and the build comparison.",
            "",
            "Every returned hit—not only the displayed top five—was independently rebound to `semantic/records.jsonl`. The check covers the record identity, canonical record digest, retained body slice and digest, locator, concept path, and source path. The embeddings CLI does not currently project `record_sha256`, so the verifier transparently reconstructs that digest only after binding the returned source/record identity; the JSON records the rebound count and per-hit digest origin. The compact JSON report records the exact command arguments, validation counts, first five results, and before/after bundle tree hashes.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Completed build-run directory containing bundles/; no build ID is hardcoded.",
    )
    parser.add_argument("--question-id", default=DEFAULT_QUESTION_ID)
    parser.add_argument(
        "--source-combination",
        type=Path,
        default=EVALUATION / "corpus/source-combination.json",
    )
    parser.add_argument("--json-output", type=Path, default=JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=MARKDOWN_OUTPUT)
    args = parser.parse_args(argv)
    args.run_dir = args.run_dir.resolve(strict=True)
    args.source_combination = args.source_combination.resolve(strict=True)
    args.json_output = args.json_output.resolve()
    args.markdown_output = args.markdown_output.resolve()
    if not (args.run_dir / "bundles").is_dir():
        parser.error("--run-dir must contain bundles/")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    question = load_question(args.question_id)
    combination = load_json(args.source_combination)
    identity_by_source = combination.get("identity_by_source")
    if not isinstance(identity_by_source, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in identity_by_source.items()
    ):
        raise VerificationError("source combination has no valid identity_by_source map")
    bundles = args.run_dir / "bundles"
    compatible = [
        run_cli(
            bundles,
            identity_by_source,
            "legacy",
            "legacy-a",
            "skills/consult-semantic-okf/scripts/query_semantic_okf.py",
            [
                "ledger",
                "--contains",
                "phthalate",
                "--limit",
                "10",
                "--show-content",
                "--validate",
                "--format",
                "json",
            ],
        ),
        run_cli(
            bundles,
            identity_by_source,
            "embeddings",
            "embeddings-a",
            "skills/consult-semantic-okf-embeddings/scripts/query_semantic_okf_embeddings.py",
            ["search", "--query", question, "--mode", "lexical", "--top-k", "10"],
        ),
        run_cli(
            bundles,
            identity_by_source,
            "classical",
            "classical-a",
            "skills/consult-semantic-okf-classical/scripts/query_semantic_okf_classical.py",
            ["search", "--query", question, "--mode", "bm25", "--top-k", "10"],
        ),
        run_cli(
            bundles,
            identity_by_source,
            "adaptive",
            "adaptive-a",
            "skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py",
            ["search", "--query", question, "--mode", "bm25", "--top-k", "10"],
        ),
    ]
    incompatible = [
        {
            "family": "entity-graph",
            "status": "not-applicable",
            "reason": "paper record sources/markdown/PMC11764522 has no PDF page headings",
        },
        {
            "family": "ensemble",
            "status": "not-applicable",
            "reason": "ensemble component plan adaptive is invalid: paper identity mappings must contain canonical versioned arXiv IDs",
        },
    ]
    report = {
        "schema_version": "semantic-okf-endocrine-hygiene-manual-query-verification/1.1",
        "status": "pass",
        "question_id": args.question_id,
        "question": question,
        "build_run_id": args.run_dir.name,
        "execution_contract": {
            "read_only": True,
            "mcp_used": False,
            "all_returned_hits_independently_validated": True,
            "compatible_family_count": len(compatible),
            "not_applicable_family_count": len(incompatible),
        },
        "compatible_families": compatible,
        "incompatible_families": incompatible,
    }
    atomic_write(args.json_output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    atomic_write(args.markdown_output, render_markdown(report))
    print(canonical_json({"status": "pass", "compatible": len(compatible), "not_applicable": len(incompatible)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
