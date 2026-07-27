#!/usr/bin/env python3
"""Measure Tika extraction fidelity against the pinned canonical paper text."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import unicodedata
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "semantic-okf-tika-mallet-extraction-fidelity/1.0"
HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent
REPO = EVALUATION.parents[1]
SPEC = EVALUATION / "canonical" / "graphrag-papers-40"
PAGE_HEADING = re.compile(r"(?m)^## PDF page \d+\s*$")
TOKEN = re.compile(r"[^\W_]+", re.UNICODE)


class FidelityError(RuntimeError):
    """Describe invalid inputs or an incomplete fidelity evaluation."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FidelityError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FidelityError(f"{path} must contain one JSON object")
    return value


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise FidelityError(
                        f"{path}:{line_number} must contain one JSON object"
                    )
                rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FidelityError(f"cannot read {path}: {exc}") from exc
    return rows


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _fingerprint(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(REPO).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _tree_inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        if path.is_symlink():
            raise FidelityError(f"bundle contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    return rows


def _bundle_file(bundle: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise FidelityError(f"{label} must be a nonempty relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise FidelityError(f"unsafe {label}: {value}")
    path = bundle.joinpath(*pure.parts)
    if not path.is_file() or path.is_symlink():
        raise FidelityError(f"{label} is absent or not a regular file: {value}")
    try:
        path.resolve().relative_to(bundle.resolve())
    except ValueError as exc:
        raise FidelityError(f"{label} escapes the bundle: {value}") from exc
    return path


def _canonical_body(markdown: str, path: Path) -> tuple[str, int]:
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", markdown, re.DOTALL)
    if frontmatter is None:
        raise FidelityError(f"canonical Markdown lacks frontmatter: {path}")
    page_match = re.search(
        r"(?m)^page_count:\s*(\d+)\s*$", frontmatter.group(1)
    )
    if page_match is None:
        raise FidelityError(f"canonical Markdown lacks page_count: {path}")
    first_page = re.search(r"(?m)^## PDF page 1\s*$", markdown)
    if first_page is None:
        raise FidelityError(f"canonical Markdown lacks PDF page 1: {path}")
    body = PAGE_HEADING.sub("\n", markdown[first_page.end() :])
    return body, int(page_match.group(1))


def _tokens(value: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = normalized.replace("\u00ad", "")
    normalized = re.sub(r"(?<=\w)-\s+(?=\w)", "", normalized)
    return tuple(TOKEN.findall(normalized))


def _multiset_overlap(
    reference: Sequence[str], candidate: Sequence[str]
) -> tuple[float, float]:
    if not reference:
        raise FidelityError("reference text contains no comparable tokens")
    overlap = sum((Counter(reference) & Counter(candidate)).values())
    recall = overlap / len(reference)
    precision = overlap / len(candidate) if candidate else 0.0
    return recall, precision


def _ngrams(tokens: Sequence[str], width: int) -> set[tuple[str, ...]]:
    return {
        tuple(tokens[index : index + width])
        for index in range(max(0, len(tokens) - width + 1))
    }


def _ngram_recall(
    reference: Sequence[str], candidate: Sequence[str], width: int = 5
) -> float:
    expected = _ngrams(reference, width)
    if not expected:
        raise FidelityError(f"reference text contains no {width}-grams")
    return len(expected & _ngrams(candidate, width)) / len(expected)


def _index_unique(rows: Iterable[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str) or not value:
            raise FidelityError(f"row has an invalid {key}")
        if value in result:
            raise FidelityError(f"duplicate {key}: {value}")
        result[value] = row
    return result


def _source_id(inventory_path: str) -> str:
    name = PurePosixPath(inventory_path).name
    if not name.endswith(".pdf"):
        raise FidelityError(f"inventory source is not a PDF: {inventory_path}")
    return f"paper-{name[:-4].replace('.', '-')}"


def _verify_contract(contract: dict[str, Any]) -> None:
    expected_exact = {
        "raw_sha256",
        "raw_bytes",
        "media_type_application_pdf",
        "source_locator",
        "page_count",
    }
    if (
        contract.get("schema_version")
        != "semantic-okf-tika-mallet-extraction-fidelity-contract/1.0"
        or contract.get("dataset_id") != "graphrag-papers-40"
        or contract.get("frozen_before_fidelity_measurement") is not True
        or set(contract.get("exact_gates", [])) != expected_exact
    ):
        raise FidelityError("unsupported or incomplete extraction fidelity contract")
    for name in (
        "macro_token_recall_minimum",
        "macro_five_gram_recall_minimum",
        "hard_anchor_mean_five_gram_recall_minimum",
        "hard_anchor_pass_threshold",
        "hard_anchor_pass_rate_minimum",
    ):
        value = contract.get(name)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise FidelityError(f"contract threshold is invalid: {name}")
        if not 0.0 <= float(value) <= 1.0:
            raise FidelityError(f"contract threshold is outside [0, 1]: {name}")


def _hard_anchors(
    hard_ground_truth: Path,
    tika_tokens: dict[str, tuple[str, ...]],
) -> list[dict[str, Any]]:
    questions = _load_jsonl(hard_ground_truth)
    if len(questions) != 10:
        raise FidelityError(
            f"hard ground truth must contain 10 questions, found {len(questions)}"
        )
    unique: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for question in questions:
        question_id = question.get("id")
        evidence_rows = question.get("authoritative_evidence")
        if not isinstance(evidence_rows, list):
            raise FidelityError(f"hard question {question_id} lacks evidence")
        for evidence in evidence_rows:
            if not isinstance(evidence, dict):
                raise FidelityError(f"hard question {question_id} has invalid evidence")
            paper_id = evidence.get("paper_id")
            if not isinstance(paper_id, str) or paper_id not in tika_tokens:
                raise FidelityError(
                    f"hard question {question_id} references an unknown paper"
                )
            paper_evidence = evidence.get("paper_evidence")
            if not isinstance(paper_evidence, list) or not paper_evidence:
                raise FidelityError(
                    f"hard question {question_id} has no paper evidence"
                )
            for anchor in paper_evidence:
                if not isinstance(anchor, dict):
                    raise FidelityError(
                        f"hard question {question_id} has an invalid anchor"
                    )
                path_value = anchor.get("path")
                start = anchor.get("char_start")
                end = anchor.get("char_end")
                expected_sha = anchor.get("text_sha256")
                if (
                    not isinstance(path_value, str)
                    or not isinstance(start, int)
                    or isinstance(start, bool)
                    or not isinstance(end, int)
                    or isinstance(end, bool)
                    or not isinstance(expected_sha, str)
                    or start < 0
                    or end <= start
                ):
                    raise FidelityError(
                        f"hard question {question_id} has an invalid anchor contract"
                    )
                key = (path_value, start, end, expected_sha)
                unique.setdefault(
                    key,
                    {
                        "paper_id": paper_id,
                        "path": path_value,
                        "char_start": start,
                        "char_end": end,
                        "text_sha256": expected_sha,
                        "question_ids": set(),
                    },
                )["question_ids"].add(str(question_id))
    rows: list[dict[str, Any]] = []
    for key, anchor in sorted(unique.items()):
        path_value, start, end, expected_sha = key
        path = REPO / path_value
        if not path.is_file() or path.is_symlink():
            raise FidelityError(f"hard anchor source is absent: {path_value}")
        source = path.read_text(encoding="utf-8")
        if end > len(source):
            raise FidelityError(f"hard anchor exceeds its source: {path_value}")
        excerpt = source[start:end]
        if len(excerpt) != end - start or _sha256_text(excerpt) != expected_sha:
            raise FidelityError(f"hard anchor content drift: {path_value}:{start}")
        excerpt_tokens = _tokens(excerpt)
        recall = _ngram_recall(excerpt_tokens, tika_tokens[anchor["paper_id"]])
        rows.append(
            {
                "paper_id": anchor["paper_id"],
                "path": path_value,
                "char_start": start,
                "char_end": end,
                "text_sha256": expected_sha,
                "question_ids": sorted(anchor["question_ids"]),
                "reference_tokens": len(excerpt_tokens),
                "five_gram_recall": recall,
            }
        )
    if not rows:
        raise FidelityError("hard ground truth produced no unique extraction anchors")
    return rows


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Evaluate exact ingestion gates and normalized textual fidelity."""

    bundle = args.bundle.resolve()
    if not bundle.is_dir() or bundle.is_symlink():
        raise FidelityError(f"bundle is absent or invalid: {bundle}")
    inventory_path = args.inventory.resolve()
    contract_path = args.contract.resolve()
    hard_ground_truth = args.hard_ground_truth.resolve()
    for path, label in (
        (inventory_path, "source inventory"),
        (contract_path, "fidelity contract"),
        (hard_ground_truth, "hard ground truth"),
    ):
        if not path.is_file() or path.is_symlink():
            raise FidelityError(f"{label} is absent or invalid: {path}")
    inventory = _load_json(inventory_path)
    contract = _load_json(contract_path)
    _verify_contract(contract)
    if (
        inventory.get("schema_version")
        != "semantic-okf-tika-mallet-canonical-input/1.0"
        or inventory.get("dataset_id") != "graphrag-papers-40"
    ):
        raise FidelityError("unsupported source inventory")
    hard_contract = inventory.get("hard_ground_truth")
    if (
        not isinstance(hard_contract, dict)
        or hard_contract.get("path") != hard_ground_truth.relative_to(REPO).as_posix()
        or hard_contract.get("sha256") != _sha256_file(hard_ground_truth)
        or hard_contract.get("count") != 10
    ):
        raise FidelityError("hard ground truth does not match the source inventory")

    before = _tree_inventory(bundle)
    documents = _index_unique(
        _load_jsonl(bundle / "tika" / "documents.jsonl"), "source_id"
    )
    records = _index_unique(
        _load_jsonl(bundle / "semantic" / "records.jsonl"), "source_id"
    )
    source_root = REPO / str(inventory.get("source_root"))
    source_rows = inventory.get("files")
    if not isinstance(source_rows, list) or len(source_rows) != 15:
        raise FidelityError("source inventory must contain exactly 15 PDFs")

    paper_rows: list[dict[str, Any]] = []
    tika_tokens: dict[str, tuple[str, ...]] = {}
    for source in source_rows:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            raise FidelityError("source inventory contains an invalid row")
        inventory_relative = source["path"]
        source_id = _source_id(inventory_relative)
        paper_id = PurePosixPath(inventory_relative).name.removesuffix(".pdf")
        if source_id not in documents or source_id not in records:
            raise FidelityError(f"bundle is missing {source_id}")
        document = documents[source_id]
        record = records[source_id]
        pdf = source_root.joinpath(*PurePosixPath(inventory_relative).parts)
        if not pdf.is_file() or pdf.is_symlink():
            raise FidelityError(f"pinned source PDF is absent: {inventory_relative}")
        canonical_path = source_root / "sources" / "markdown" / f"{paper_id}.md"
        if not canonical_path.is_file() or canonical_path.is_symlink():
            raise FidelityError(f"canonical paper Markdown is absent: {paper_id}")
        canonical_markdown = canonical_path.read_text(encoding="utf-8")
        canonical_text, expected_pages = _canonical_body(
            canonical_markdown, canonical_path
        )
        metadata_path = _bundle_file(
            bundle, document.get("metadata_path"), f"{source_id} metadata"
        )
        metadata = _load_json(metadata_path)
        markdown_path = _bundle_file(
            bundle, document.get("markdown_path"), f"{source_id} Markdown"
        )
        if _canonical_digest(metadata) != document.get("metadata_sha256"):
            raise FidelityError(f"metadata hash drift for {source_id}")
        if _sha256_file(markdown_path) != document.get("markdown_sha256"):
            raise FidelityError(f"extracted Markdown hash drift for {source_id}")
        body = record.get("body")
        if not isinstance(body, str) or not body:
            raise FidelityError(f"semantic record has no extracted body: {source_id}")
        if _sha256_text(body) != document.get("body_sha256"):
            raise FidelityError(f"extracted body hash drift for {source_id}")

        expected_locator = inventory_relative
        exact = {
            "raw_sha256": (
                source.get("sha256") == _sha256_file(pdf)
                and document.get("raw_sha256") == source.get("sha256")
            ),
            "raw_bytes": (
                source.get("bytes") == pdf.stat().st_size
                and document.get("raw_bytes") == source.get("bytes")
            ),
            "media_type_application_pdf": (
                document.get("media_type") == "application/pdf"
                and metadata.get("Content-Type") == "application/pdf"
            ),
            "source_locator": document.get("source_locator") == expected_locator,
            "page_count": str(metadata.get("xmpTPg:NPages"))
            == str(expected_pages),
        }
        reference_tokens = _tokens(canonical_text)
        candidate_tokens = _tokens(body)
        token_recall, token_precision = _multiset_overlap(
            reference_tokens, candidate_tokens
        )
        five_gram_recall = _ngram_recall(reference_tokens, candidate_tokens)
        tika_tokens[paper_id] = candidate_tokens
        paper_rows.append(
            {
                "paper_id": paper_id,
                "source_id": source_id,
                "exact_gates": exact,
                "canonical_pages": expected_pages,
                "tika_pages": int(metadata["xmpTPg:NPages"]),
                "canonical_tokens": len(reference_tokens),
                "tika_tokens": len(candidate_tokens),
                "token_recall": token_recall,
                "token_precision": token_precision,
                "five_gram_recall": five_gram_recall,
            }
        )

    if set(documents) != {row["source_id"] for row in paper_rows}:
        raise FidelityError("Tika documents contain unexpected sources")
    if set(records) != {row["source_id"] for row in paper_rows}:
        raise FidelityError("semantic records contain unexpected sources")
    anchors = _hard_anchors(hard_ground_truth, tika_tokens)
    anchor_threshold = float(contract["hard_anchor_pass_threshold"])
    for row in anchors:
        row["passes_threshold"] = row["five_gram_recall"] >= anchor_threshold

    macro_token_recall = statistics.fmean(
        row["token_recall"] for row in paper_rows
    )
    macro_token_precision = statistics.fmean(
        row["token_precision"] for row in paper_rows
    )
    macro_five_gram_recall = statistics.fmean(
        row["five_gram_recall"] for row in paper_rows
    )
    anchor_mean = statistics.fmean(row["five_gram_recall"] for row in anchors)
    anchor_pass_rate = statistics.fmean(
        float(row["passes_threshold"]) for row in anchors
    )
    exact_pass = all(
        value for row in paper_rows for value in row["exact_gates"].values()
    )
    gates = {
        "exact_ingestion": {
            "value": exact_pass,
            "minimum": True,
            "pass": exact_pass,
        },
        "macro_token_recall": {
            "value": macro_token_recall,
            "minimum": float(contract["macro_token_recall_minimum"]),
            "pass": macro_token_recall
            >= float(contract["macro_token_recall_minimum"]),
        },
        "macro_five_gram_recall": {
            "value": macro_five_gram_recall,
            "minimum": float(contract["macro_five_gram_recall_minimum"]),
            "pass": macro_five_gram_recall
            >= float(contract["macro_five_gram_recall_minimum"]),
        },
        "hard_anchor_mean_five_gram_recall": {
            "value": anchor_mean,
            "minimum": float(
                contract["hard_anchor_mean_five_gram_recall_minimum"]
            ),
            "pass": anchor_mean
            >= float(contract["hard_anchor_mean_five_gram_recall_minimum"]),
        },
        "hard_anchor_pass_rate": {
            "value": anchor_pass_rate,
            "minimum": float(contract["hard_anchor_pass_rate_minimum"]),
            "pass": anchor_pass_rate
            >= float(contract["hard_anchor_pass_rate_minimum"]),
        },
    }
    after = _tree_inventory(bundle)
    if before != after:
        raise FidelityError("fidelity evaluation modified the candidate bundle")
    status = "pass" if all(row["pass"] for row in gates.values()) else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dataset_id": "graphrag-papers-40",
        "candidate_id": "tika-mallet",
        "contract_frozen_before_measurement": True,
        "normalization": {
            "unicode": "NFKC casefold",
            "tokens": "Unicode alphanumeric runs; underscores excluded",
            "line_wrap": "soft hyphens removed; hyphen-plus-whitespace joined",
            "canonical_scope": "content beginning after the PDF page 1 heading; page headings removed",
            "five_grams": "sets of five normalized consecutive tokens",
        },
        "inputs": {
            "source_inventory": _fingerprint(inventory_path),
            "fidelity_contract": _fingerprint(contract_path),
            "hard_ground_truth": _fingerprint(hard_ground_truth),
            "evaluator_script": _fingerprint(Path(__file__).resolve()),
        },
        "bundle": {
            "path": str(bundle),
            "file_count": len(before),
            "inventory_sha256": _canonical_digest(before),
            "unchanged_after_evaluation": True,
        },
        "summary": {
            "paper_count": len(paper_rows),
            "exact_gate_checks": len(paper_rows)
            * len(contract["exact_gates"]),
            "exact_gate_failures": sum(
                not value
                for row in paper_rows
                for value in row["exact_gates"].values()
            ),
            "macro_token_recall": macro_token_recall,
            "macro_token_precision": macro_token_precision,
            "macro_five_gram_recall": macro_five_gram_recall,
            "hard_anchor_count": len(anchors),
            "hard_anchor_mean_five_gram_recall": anchor_mean,
            "hard_anchor_pass_rate": anchor_pass_rate,
        },
        "gates": gates,
        "papers": paper_rows,
        "hard_anchors": anchors,
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.1f}%"


def render_markdown(report: dict[str, Any]) -> str:
    """Render the immutable contract result and per-paper diagnostics."""

    summary = report["summary"]
    lines = [
        "# Tika Extraction Fidelity Evaluation",
        "",
        f"Status: **{report['status']}**. The contract was frozen before "
        "measurement.",
        "",
        "| Gate | Observed | Required | Status |",
        "|---|---:|---:|---:|",
    ]
    for name, gate in report["gates"].items():
        observed = (
            str(gate["value"]).lower()
            if isinstance(gate["value"], bool)
            else _percent(gate["value"])
        )
        required = (
            str(gate["minimum"]).lower()
            if isinstance(gate["minimum"], bool)
            else _percent(gate["minimum"])
        )
        lines.append(
            f"| `{name}` | {observed} | {required} | "
            f"{'pass' if gate['pass'] else 'fail'} |"
        )
    lines.extend(
        [
            "",
            f"All {summary['exact_gate_checks']} exact checks covered raw hashes, "
            "byte counts, PDF media types, source locators, and page counts. "
            f"The evaluation measured {summary['hard_anchor_count']} unique "
            "reviewed hard-question evidence passages.",
            "",
            "| Paper | Token recall | Token precision | 5-gram recall | Exact |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["papers"]:
        lines.append(
            f"| `{row['paper_id']}` | {_percent(row['token_recall'])} | "
            f"{_percent(row['token_precision'])} | "
            f"{_percent(row['five_gram_recall'])} | "
            f"{'pass' if all(row['exact_gates'].values()) else 'fail'} |"
        )
    lines.extend(
        [
            "",
            f"The read-only {report['bundle']['file_count']}-file bundle retained "
            f"inventory SHA-256 `{report['bundle']['inventory_sha256']}`.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument(
        "--inventory", type=Path, default=SPEC / "source-inventory.json"
    )
    parser.add_argument(
        "--contract", type=Path, default=SPEC / "extraction-fidelity-contract.json"
    )
    parser.add_argument(
        "--hard-ground-truth",
        type=Path,
        default=REPO
        / "evaluations"
        / "semantic-okf-adaptive"
        / "hard-ground-truth.jsonl",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if any(
        path.exists() or path.is_symlink()
        for path in (args.output_json, args.output_markdown)
    ):
        print(json.dumps({"status": "error", "error": "output already exists"}))
        return 2
    try:
        report = evaluate(args)
    except (
        FidelityError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.output_markdown.write_text(
        render_markdown(report), encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "paper_count": report["summary"]["paper_count"],
                "hard_anchor_count": report["summary"]["hard_anchor_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
