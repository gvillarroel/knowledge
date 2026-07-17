#!/usr/bin/env python3
"""Audit Harbor benchmark identities and hard-evidence joins end to end."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ASTRO = REPO / "evaluations/semantic-okf-astro"
BENCHMARK = ASTRO / "benchmark"
TASKS = HERE / "generated/tasks"
REPORT_JSON = HERE / "reports/benchmark-id-audit.json"
REPORT_MD = HERE / "reports/benchmark-id-audit.md"
EXPECTED_IDS = [f"q{number:03d}" for number in range(1, 41)]
EXPECTED_HARD_IDS = EXPECTED_IDS[30:]
EXPECTED_COUNTS = {
    "questions": 40,
    "direct": 20,
    "cross-document": 10,
    "hard": 10,
    "hard_evidence_bindings": 46,
}
SOURCE_ID = re.compile(r"^astro-doc-[0-9a-f]{16}$")


class AuditError(ValueError):
    """Raised when a checked identity or locator invariant is false."""


def require(condition: bool, message: str) -> None:
    """Raise a concise audit error when an invariant fails."""

    if not condition:
        raise AuditError(message)


def load_json(path: Path) -> Any:
    """Load a UTF-8 JSON document."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load non-empty rows from a UTF-8 JSON Lines document."""

    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_bytes(payload: bytes) -> str:
    """Return the lowercase SHA-256 digest of bytes."""

    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file."""

    return sha256_bytes(path.read_bytes())


def source_id_for(document_id: str) -> str:
    """Derive the opaque source identity from its canonical route."""

    return f"astro-doc-{sha256_bytes(document_id.encode('utf-8'))[:16]}"


def expected_record_id(upstream_path: str) -> str:
    """Derive the Semantic OKF record identity from the pinned upstream path."""

    prefix = "src/content/docs/en/"
    require(upstream_path.startswith(prefix) and upstream_path.endswith(".mdx"), "invalid upstream path")
    return f"sources/mdx/{upstream_path.removeprefix(prefix).removesuffix('.mdx')}"


def import_real_grader() -> ModuleType:
    """Load the exact checked grader used in every generated Harbor task."""

    path = HERE / "grader/score.py"
    spec = importlib.util.spec_from_file_location("semantic_okf_harbor_real_grader", path)
    require(spec is not None and spec.loader is not None, "cannot load real Harbor grader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task_directories() -> dict[str, tuple[str, Path]]:
    """Return the generated task directory for every question identity."""

    result: dict[str, tuple[str, Path]] = {}
    for split in ("train", "dev", "holdout"):
        split_dir = TASKS / split
        require(split_dir.is_dir(), f"missing generated split directory: {split}")
        for path in sorted(item for item in split_dir.iterdir() if item.is_dir()):
            require(path.name not in result, f"duplicate generated task: {path.name}")
            result[path.name] = (split, path)
    return result


def hard_evidence_mapping(
    grader: ModuleType,
    truth: Mapping[str, Any],
    task_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Exercise real-grader mapping and return compact per-binding receipts."""

    ledger_rows = grader.load_jsonl(task_dir / "tests/records.jsonl")
    ledger = {(str(row["source_id"]), str(row["record_id"])): row for row in ledger_rows}
    require(len(ledger) == len(ledger_rows), f"{truth['id']}: duplicate ledger identity")
    mapped = grader.authoritative_ranges(truth, task_dir / "tests/authority", ledger)
    expected_evidence_ids = [str(row["id"]) for row in truth["authoritative_evidence"]]
    require(list(mapped) == expected_evidence_ids, f"{truth['id']}: real grader returned incomplete evidence mapping")

    receipts: list[dict[str, Any]] = []
    normalized_count = 0
    eof_trim_count = 0
    for row in truth["authoritative_evidence"]:
        evidence_id = str(row["id"])
        source_id = str(row["source_id"])
        matching_records = [record for key, record in ledger.items() if key[0] == source_id]
        require(len(matching_records) == 1, f"{evidence_id}: source must join one ledger record")
        body = str(matching_records[0]["body"])

        authority_path = task_dir / "tests/authority" / str(row["path"])
        payload = authority_path.read_bytes()
        require(sha256_bytes(payload) == row["file_sha256"], f"{evidence_id}: file hash mismatch")
        text = payload.decode("utf-8-sig")
        start, end = int(row["start_char"]), int(row["end_char"])
        require(0 <= start < end <= len(text), f"{evidence_id}: invalid character range")
        selected = text[start:end]
        require(
            sha256_bytes(selected.encode("utf-8")) == row["text_sha256"],
            f"{evidence_id}: selected-text hash mismatch",
        )

        normalized = selected.replace("\r\n", "\n").replace("\r", "\n")
        line_endings_normalized = normalized != selected
        direct_offset = body.find(normalized)
        mapped_text = normalized
        eof_trimmed = False
        if direct_offset < 0 and normalized.endswith("\n"):
            mapped_text = normalized.rstrip("\n")
            direct_offset = body.find(mapped_text)
            eof_trimmed = True
        require(mapped_text and direct_offset >= 0, f"{evidence_id}: normalized body passage absent")
        require(body.find(mapped_text, direct_offset + 1) < 0, f"{evidence_id}: body passage is not unique")
        grader_source, grader_interval = mapped[evidence_id]
        require(grader_source == source_id, f"{evidence_id}: real grader source mismatch")
        require(
            grader_interval == (direct_offset, direct_offset + len(mapped_text)),
            f"{evidence_id}: real grader interval mismatch",
        )
        normalized_count += int(line_endings_normalized)
        eof_trim_count += int(eof_trimmed)
        receipts.append(
            {
                "question_id": truth["id"],
                "evidence_id": evidence_id,
                "source_id": source_id,
                "document_id": row["document_id"],
                "path": row["path"],
                "authoritative_range": [start, end],
                "record_body_range": [grader_interval[0], grader_interval[1]],
                "line_endings_normalized": line_endings_normalized,
                "terminal_newlines_trimmed_for_body_join": eof_trimmed,
                "unique_record_body_match": True,
            }
        )
    return receipts, {
        "line_endings_normalized": normalized_count,
        "terminal_newlines_trimmed_for_body_join": eof_trim_count,
    }


def build_audit() -> dict[str, Any]:
    """Validate all requested joins and return a deterministic audit artifact."""

    harbor_manifest = load_json(HERE / "benchmark-manifest.json")
    astro_manifest = load_json(BENCHMARK / "benchmark-manifest.json")
    generated_manifest = load_json(TASKS / "manifest.json")
    splits = load_json(HERE / "splits.json")
    questions = load_jsonl(BENCHMARK / "retrieval-questions.jsonl")
    hard_questions = load_jsonl(BENCHMARK / "hard-questions.jsonl")
    truths = load_jsonl(BENCHMARK / "hard-ground-truth.jsonl")
    specs_value = load_json(BENCHMARK / "question-specs.json")
    specs = specs_value.get("questions")
    combination = load_json(ASTRO / "corpus/source-combination.json")
    grader = import_real_grader()

    require([row.get("id") for row in questions] == EXPECTED_IDS, "questions are not exactly q001-q040 in order")
    require(harbor_manifest["questions"]["ordered_ids"] == EXPECTED_IDS, "Harbor manifest question IDs differ")
    require(len(questions) == EXPECTED_COUNTS["questions"], "question count differs")
    type_counts = Counter(str(row.get("question_type")) for row in questions)
    require(
        type_counts == Counter({"direct": 20, "cross-document": 10, "hard": 10}),
        "question type counts differ",
    )
    questions_by_id = {str(row["id"]): row for row in questions}
    require(len(questions_by_id) == len(questions), "duplicate question identity")

    require(isinstance(specs, list), "question specs must contain a questions array")
    require([row.get("id") for row in specs] == EXPECTED_IDS, "question spec IDs differ")
    specs_by_id = {str(row["id"]): row for row in specs}
    require([row.get("id") for row in hard_questions] == EXPECTED_HARD_IDS, "hard subset IDs differ")
    require(hard_questions == [questions_by_id[qid] for qid in EXPECTED_HARD_IDS], "hard subset rows differ")
    require([row.get("id") for row in truths] == EXPECTED_HARD_IDS, "hard ground-truth IDs differ")
    truths_by_id = {str(row["id"]): row for row in truths}

    for path_text, expected_hash in harbor_manifest["frozen_files"].items():
        require(sha256_file(REPO / path_text) == expected_hash, f"frozen file hash differs: {path_text}")
    require(
        sha256_file(BENCHMARK / "question-specs.json") == harbor_manifest["question_specs_sha256"],
        "question-spec hash differs",
    )
    require(
        astro_manifest["question_specs_sha256"] == harbor_manifest["question_specs_sha256"],
        "Astro and Harbor question-spec hashes differ",
    )

    declared_cohorts = splits["cohorts"]
    split_sets = {name: set(declared_cohorts[name]) for name in ("train", "dev", "holdout")}
    require(not (split_sets["train"] & split_sets["dev"]), "train and dev overlap")
    require(not (split_sets["train"] & split_sets["holdout"]), "train and holdout overlap")
    require(not (split_sets["dev"] & split_sets["holdout"]), "dev and holdout overlap")
    require(set().union(*split_sets.values()) == set(EXPECTED_IDS), "split union differs from q001-q040")
    split_counts = {name: len(values) for name, values in split_sets.items()}
    require(split_counts == {"train": 24, "dev": 8, "holdout": 8}, "split counts differ")
    for name, values in split_sets.items():
        actual_types = Counter(questions_by_id[qid]["question_type"] for qid in values)
        declared = {
            question_type: splits["counts"][question_type][name]
            for question_type in ("direct", "cross-document", "hard")
        }
        require(actual_types == Counter(declared), f"{name} question-type counts differ")

    generated_tasks = task_directories()
    require(set(generated_tasks) == set(EXPECTED_IDS), "generated tasks are not exactly q001-q040")
    question_copy_hashes: set[str] = set()
    ledger_copy_hashes: set[str] = set()
    crosswalk_copy_hashes: set[str] = set()
    for qid in EXPECTED_IDS:
        split, task_dir = generated_tasks[qid]
        require(qid in split_sets[split], f"{qid}: generated task is in the wrong split")
        copied_question = load_json(task_dir / "tests/question.json")
        require(copied_question == questions_by_id[qid], f"{qid}: generated question copy differs")
        question_copy_hashes.add(sha256_file(task_dir / "tests/question.json"))
        ledger_copy_hashes.add(sha256_file(task_dir / "tests/records.jsonl"))
        crosswalk_copy_hashes.add(sha256_file(task_dir / "tests/source-combination.json"))
        require(f"Question: {questions_by_id[qid]['question']}" in (task_dir / "instruction.md").read_text(encoding="utf-8"), f"{qid}: instruction question differs")
        require(f"Set `question_id` to `{qid}`" in (task_dir / "instruction.md").read_text(encoding="utf-8"), f"{qid}: response ID differs")
        hard_copy = task_dir / "tests/hard-ground-truth.json"
        require(hard_copy.exists() == (qid in truths_by_id), f"{qid}: hard truth presence differs")
        if hard_copy.exists():
            require(load_json(hard_copy) == truths_by_id[qid], f"{qid}: generated hard truth differs")
    require(len(ledger_copy_hashes) == 1, "generated task ledgers differ")
    require(len(crosswalk_copy_hashes) == 1, "generated task crosswalks differ")
    require(next(iter(ledger_copy_hashes)) == generated_manifest["source_hashes"]["records"], "generated ledger hash differs")
    require(next(iter(crosswalk_copy_hashes)) == generated_manifest["source_hashes"]["source_combination"], "generated crosswalk hash differs")
    require(generated_manifest["question_count"] == 40, "generated manifest question count differs")
    require(generated_manifest["cohort_counts"] == split_counts, "generated manifest split counts differ")

    representative_task = generated_tasks["q001"][1]
    ledger_rows = grader.load_jsonl(representative_task / "tests/records.jsonl")
    crosswalk_rows = combination.get("records")
    require(isinstance(crosswalk_rows, list), "crosswalk records are absent")
    ledger_by_key = {(str(row["source_id"]), str(row["record_id"])): row for row in ledger_rows}
    require(len(ledger_by_key) == len(ledger_rows), "ledger identities are not unique")
    ledger_by_source: dict[str, list[Mapping[str, Any]]] = {}
    for row in ledger_rows:
        ledger_by_source.setdefault(str(row["source_id"]), []).append(row)
    crosswalk_by_source: dict[str, list[Mapping[str, Any]]] = {}
    crosswalk_by_document: dict[str, list[Mapping[str, Any]]] = {}
    for row in crosswalk_rows:
        crosswalk_by_source.setdefault(str(row["source_id"]), []).append(row)
        crosswalk_by_document.setdefault(str(row["document_id"]), []).append(row)

    qrel_source_ids = sorted({str(source) for row in questions for source in row["qrels"]["source_ids"]})
    qrel_document_ids = sorted({str(document) for row in questions for document in row["qrels"]["document_ids"]})
    qrel_edges = sum(len(row["qrels"]["source_ids"]) for row in questions)
    joins: list[dict[str, str]] = []
    for source_id in qrel_source_ids:
        require(SOURCE_ID.fullmatch(source_id) is not None, f"invalid qrel source ID: {source_id}")
        source_crosswalk = crosswalk_by_source.get(source_id, [])
        source_ledger = ledger_by_source.get(source_id, [])
        require(len(source_crosswalk) == 1, f"{source_id}: crosswalk join is not one-to-one")
        require(len(source_ledger) == 1, f"{source_id}: ledger join is not one-to-one")
        crosswalk_row = source_crosswalk[0]
        ledger_row = source_ledger[0]
        document_id = str(crosswalk_row["document_id"])
        record_id = str(crosswalk_row["record_id"])
        require(source_id_for(document_id) == source_id, f"{source_id}: source ID derivation differs")
        require(record_id == expected_record_id(str(crosswalk_row["upstream_path"])), f"{source_id}: record ID derivation differs")
        require((source_id, record_id) in ledger_by_key, f"{source_id}: source-record pair is absent from ledger")
        require(str(ledger_row["record_id"]) == record_id, f"{source_id}: ledger and crosswalk record IDs differ")
        joins.append({"source_id": source_id, "record_id": record_id, "document_id": document_id})
    for document_id in qrel_document_ids:
        require(len(crosswalk_by_document.get(document_id, [])) == 1, f"{document_id}: document crosswalk is not one-to-one")
    for qid in EXPECTED_IDS:
        question = questions_by_id[qid]
        mapped_documents = sorted(
            str(crosswalk_by_source[source][0]["document_id"])
            for source in question["qrels"]["source_ids"]
        )
        require(mapped_documents == question["qrels"]["document_ids"], f"{qid}: source and document qrels differ")
        spec = specs_by_id[qid]
        require(spec["question"] == question["question"], f"{qid}: question text differs from spec")
        require(spec["question_type"] == question["question_type"], f"{qid}: question type differs from spec")
        spec_documents = sorted(
            str(row["document_id"])
            for upstream in spec["documents"]
            for row in crosswalk_rows
            if row["upstream_path"] == upstream
        )
        require(spec_documents == question["qrels"]["document_ids"], f"{qid}: spec documents differ from qrels")

    hard_rows: list[dict[str, Any]] = []
    evidence_receipts: list[dict[str, Any]] = []
    line_ending_count = 0
    eof_trim_count = 0
    for qid in EXPECTED_HARD_IDS:
        question = questions_by_id[qid]
        truth = truths_by_id[qid]
        require(truth["question"] == question["question"], f"{qid}: ground-truth question text differs")
        ground = truth["ground_truth"]
        require(ground["required_source_ids"] == question["qrels"]["source_ids"], f"{qid}: required source IDs differ")
        require(ground["required_document_ids"] == question["qrels"]["document_ids"], f"{qid}: required document IDs differ")
        evidence = truth["authoritative_evidence"]
        expected_evidence_ids = [f"{qid}-e{number}" for number in range(1, len(evidence) + 1)]
        require([row["id"] for row in evidence] == expected_evidence_ids, f"{qid}: evidence IDs are not scoped ordinals")
        evidence_ids = set(expected_evidence_ids)
        for prefix, rows in (("a", ground["answer_claims"]), ("n", ground["important_negatives"])):
            require(
                [row["id"] for row in rows] == [f"{qid}-{prefix}{number}" for number in range(1, len(rows) + 1)],
                f"{qid}: {prefix} IDs are not scoped ordinals",
            )
            require(
                all(set(row["evidence_ids"]).issubset(evidence_ids) for row in rows),
                f"{qid}: claim references an unknown evidence ID",
            )
        claim_ids = {row["id"] for row in ground["answer_claims"]}
        require(
            all(set(row["inputs"]).issubset(claim_ids) for row in ground["derivation"]),
            f"{qid}: derivation references an unknown answer claim",
        )
        require(
            all(row["source_id"] in question["qrels"]["source_ids"] for row in evidence),
            f"{qid}: evidence source falls outside qrels",
        )
        require(
            all(row["document_id"] in question["qrels"]["document_ids"] for row in evidence),
            f"{qid}: evidence document falls outside qrels",
        )
        receipts, normalization = hard_evidence_mapping(grader, truth, generated_tasks[qid][1])
        evidence_receipts.extend(receipts)
        line_ending_count += normalization["line_endings_normalized"]
        eof_trim_count += normalization["terminal_newlines_trimmed_for_body_join"]
        hard_rows.append(
            {
                "question_id": qid,
                "required_source_ids_match_qrels": True,
                "required_document_ids_match_qrels": True,
                "evidence_bindings": len(evidence),
                "real_grader_unique_mappings": len(receipts),
                "line_endings_normalized": normalization["line_endings_normalized"],
                "terminal_newlines_trimmed_for_body_join": normalization[
                    "terminal_newlines_trimmed_for_body_join"
                ],
            }
        )
    require(len(evidence_receipts) == EXPECTED_COUNTS["hard_evidence_bindings"], "hard evidence count differs")
    require(len({row["evidence_id"] for row in evidence_receipts}) == len(evidence_receipts), "evidence IDs are not globally unique")

    input_hashes = {
        "retrieval_questions": sha256_file(BENCHMARK / "retrieval-questions.jsonl"),
        "hard_questions": sha256_file(BENCHMARK / "hard-questions.jsonl"),
        "hard_ground_truth": sha256_file(BENCHMARK / "hard-ground-truth.jsonl"),
        "question_specs": sha256_file(BENCHMARK / "question-specs.json"),
        "source_combination": sha256_file(ASTRO / "corpus/source-combination.json"),
        "generated_records": next(iter(ledger_copy_hashes)),
        "real_grader": sha256_file(HERE / "grader/score.py"),
    }
    return {
        "schema_version": "semantic-okf-harbor-benchmark-id-audit/1.0",
        "status": "pass",
        "benchmark_id": harbor_manifest["benchmark_id"],
        "inputs": input_hashes,
        "summary": {
            "question_ids": len(questions),
            "question_id_range": [EXPECTED_IDS[0], EXPECTED_IDS[-1]],
            "question_types": dict(sorted(type_counts.items())),
            "split_counts": split_counts,
            "split_pairwise_overlap": 0,
            "generated_tasks": len(generated_tasks),
            "qrel_assignments": qrel_edges,
            "distinct_qrel_source_ids": len(qrel_source_ids),
            "distinct_qrel_document_ids": len(qrel_document_ids),
            "qrel_source_ledger_crosswalk_joins": len(qrel_source_ids),
            "hard_questions": len(truths),
            "hard_required_id_sets_matching_qrels": len(truths),
            "authoritative_evidence_bindings": len(evidence_receipts),
            "real_grader_unique_record_body_mappings": len(evidence_receipts),
            "line_ending_normalizations": line_ending_count,
            "eof_terminal_newline_normalizations": eof_trim_count,
        },
        "invariants": {
            "questions_are_exactly_q001_through_q040": True,
            "splits_are_disjoint_and_exhaustive": True,
            "generated_tasks_match_checked_questions": True,
            "source_ids_are_route_derived": True,
            "record_ids_are_upstream_path_derived": True,
            "every_distinct_qrel_source_joins_one_ledger_record_and_crosswalk_document": True,
            "every_question_qrel_source_set_maps_exactly_to_its_document_set": True,
            "hard_required_ids_equal_qrels": True,
            "question_spec_hard_subset_ground_truth_and_generated_texts_align": True,
            "all_authoritative_bindings_map_uniquely_via_real_grader": True,
        },
        "qrel_joins": joins,
        "hard_question_audit": hard_rows,
        "authoritative_evidence_audit": evidence_receipts,
    }


def markdown_report(audit: Mapping[str, Any]) -> str:
    """Render the compact human-readable audit report."""

    summary = audit["summary"]
    hard_rows = audit["hard_question_audit"]
    lines = [
        "# Semantic OKF Harbor benchmark ID and locator audit",
        "",
        "Status: **PASS**.",
        "",
        "## Conclusion",
        "",
        "The expected IDs are coherent and all evaluator joins are valid. Question IDs are stable scoped ordinals (`q001`-`q040`); document IDs are canonical English Astro routes; source IDs are deterministic opaque IDs derived as `astro-doc-` plus the first 16 hexadecimal characters of SHA-256 over the document ID; and record IDs are derived from the pinned upstream MDX path. Qrel source and document arrays are validated as sets through the crosswalk, not paired by list position.",
        "",
        "Hard evidence IDs, answer-claim IDs, and negative IDs are question-scoped ordinals (`qNNN-eK`, `qNNN-aK`, and `qNNN-nK`). Every reference resolves within its question.",
        "",
        "## Coverage",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Ordered question IDs | {summary['question_ids']} (`{summary['question_id_range'][0]}`-`{summary['question_id_range'][1]}`) |",
        f"| Split membership | {summary['split_counts']['train']} train / {summary['split_counts']['dev']} dev / {summary['split_counts']['holdout']} holdout; {summary['split_pairwise_overlap']} overlap |",
        f"| Generated tasks matching benchmark rows | {summary['generated_tasks']} / 40 |",
        f"| Qrel assignments | {summary['qrel_assignments']} |",
        f"| Distinct qrel source-to-ledger-to-crosswalk joins | {summary['qrel_source_ledger_crosswalk_joins']} / {summary['distinct_qrel_source_ids']} |",
        f"| Hard required ID sets equal to qrels | {summary['hard_required_id_sets_matching_qrels']} / 10 |",
        f"| Real-grader unique evidence mappings | {summary['real_grader_unique_record_body_mappings']} / {summary['authoritative_evidence_bindings']} |",
        f"| CRLF/CR line-ending normalizations used | {summary['line_ending_normalizations']} |",
        f"| EOF terminal-newline trims used | {summary['eof_terminal_newline_normalizations']} |",
        "",
        "The file and selected-text hashes are checked against raw authoritative bytes before newline normalization. The real Harbor grader then maps the normalized selection uniquely into the corresponding ledger record body. EOF-only publication newlines are trimmed only when the direct normalized join fails.",
        "",
        "## Hard-question locator audit",
        "",
        "| Question | Evidence | Unique grader mappings | Line-ending normalized | EOF trimmed | Required IDs = qrels |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in hard_rows:
        lines.append(
            f"| {row['question_id']} | {row['evidence_bindings']} | {row['real_grader_unique_mappings']} | {row['line_endings_normalized']} | {row['terminal_newlines_trimmed_for_body_join']} | yes |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The IDs are evaluator identities, not relevance scores. A source ID is intentionally opaque, while its crosswalk document ID remains human-readable. Because each qrel source resolves to exactly one source-scoped ledger record and exactly one canonical document, the expected IDs are suitable for deterministic scoring. This audit validates identity, hashing, range integrity, and join uniqueness; it does not independently judge whether a benchmark question is pedagogically ideal or whether an answer semantically entails every claim.",
            "",
            "The machine-readable companion contains every distinct qrel join and all 46 per-binding real-grader mapping receipts.",
        ]
    )
    return "\n".join(lines) + "\n"


def encoded_json(value: Mapping[str, Any]) -> str:
    """Serialize the deterministic machine-readable report."""

    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse report write/check mode."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when checked reports differ from a fresh audit.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the audit and atomically write or verify its reports."""

    args = parse_args(argv)
    try:
        audit = build_audit()
    except (AuditError, KeyError, OSError, TypeError, ValueError) as exc:
        print(f"benchmark ID audit failed: {exc}", file=sys.stderr)
        return 1
    json_text = encoded_json(audit)
    md_text = markdown_report(audit)
    if args.check:
        if not REPORT_JSON.is_file() or REPORT_JSON.read_text(encoding="utf-8") != json_text:
            print("benchmark ID audit JSON report drift detected", file=sys.stderr)
            return 1
        if not REPORT_MD.is_file() or REPORT_MD.read_text(encoding="utf-8") != md_text:
            print("benchmark ID audit Markdown report drift detected", file=sys.stderr)
            return 1
    else:
        REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
        REPORT_JSON.write_text(json_text, encoding="utf-8", newline="\n")
        REPORT_MD.write_text(md_text, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", **audit["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
