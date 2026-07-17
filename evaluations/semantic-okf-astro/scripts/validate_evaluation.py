#!/usr/bin/env python3
"""Independently validate the frozen Astro corpus, benchmark, identities, and plans."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping


REPO_ROOT = Path(__file__).resolve().parents[3]
EVALUATION = REPO_ROOT / "evaluations" / "semantic-okf-astro"
CORPUS = EVALUATION / "corpus"
BENCHMARK = EVALUATION / "benchmark"
PLANS = EVALUATION / "plans"
EXPECTED_COMMIT = "5c37be52c5038e1174be1e838d3dd5852db26a21"
EXPECTED_DOCUMENTS = 416
HEX64_RE = re.compile(r"[0-9a-f]{64}")
SOURCE_ID_RE = re.compile(r"astro-doc-[0-9a-f]{16}")
QUESTION_ID_RE = re.compile(r"q\d{3}")
HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$", re.MULTILINE)


class EvaluationError(RuntimeError):
    """Describe one or more closed-contract evaluation failures."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json(payload: str, label: str) -> Any:
    try:
        return json.loads(payload, object_pairs_hook=_object_without_duplicates)
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"{label} is invalid JSON: {exc}") from exc


def read_json(path: Path) -> Any:
    try:
        return strict_json(path.read_text(encoding="utf-8"), path.as_posix())
    except OSError as exc:
        raise EvaluationError(f"cannot read {path}: {exc}") from exc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvaluationError(f"cannot read {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            raise EvaluationError(f"{path}:{number} is blank")
        value = strict_json(line, f"{path}:{number}")
        if not isinstance(value, dict):
            raise EvaluationError(f"{path}:{number} must be an object")
        rows.append(value)
    return rows


def exact_keys(value: Any, expected: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be an object")
    observed = set(value)
    if observed != expected:
        raise EvaluationError(
            f"{label} uses a closed schema; missing={sorted(expected - observed)}, "
            f"unknown={sorted(observed - expected)}"
        )
    return value


def nonempty_strings(value: Any, label: str, *, minimum: int = 1) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) < minimum
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise EvaluationError(f"{label} must contain at least {minimum} non-empty strings")
    return value


def sorted_unique_strings(value: Any, label: str, *, minimum: int = 1) -> list[str]:
    result = nonempty_strings(value, label, minimum=minimum)
    if result != sorted(set(result)):
        raise EvaluationError(f"{label} must be sorted and unique")
    return result


def safe_relative(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise EvaluationError(f"{label} must be a portable relative path")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise EvaluationError(f"{label} escapes its root")
    target = (root / Path(*pure.parts)).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise EvaluationError(f"{label} escapes its root") from exc
    return target


def route_for(relative: str) -> str:
    without_suffix = relative.removesuffix(".mdx")
    if without_suffix == "index":
        without_suffix = ""
    elif without_suffix.endswith("/index"):
        without_suffix = without_suffix.removesuffix("/index")
    suffix = f"{without_suffix.strip('/')}/" if without_suffix else ""
    return f"/en/{suffix}"


def source_id_for(document_id: str) -> str:
    return f"astro-doc-{sha256_bytes(document_id.encode('utf-8'))[:16]}"


def validate_corpus() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], set[str]]:
    acquisition = exact_keys(
        read_json(CORPUS / "acquisition-manifest.json"),
        {
            "authority",
            "documents",
            "know",
            "repository",
            "schema_version",
            "section_counts",
            "total_bytes",
            "tree_sha256",
        },
        "acquisition manifest",
    )
    if acquisition["schema_version"] != "semantic-okf-astro-acquisition/1.0":
        raise EvaluationError("unsupported acquisition schema")
    authority = exact_keys(acquisition["authority"], {"contract", "language", "preservation"}, "authority")
    if authority["language"] != "en":
        raise EvaluationError("the authoritative corpus must be English")
    repository = exact_keys(acquisition["repository"], {"commit", "content_root", "url"}, "repository")
    if repository != {
        "commit": EXPECTED_COMMIT,
        "content_root": "src/content/docs/en",
        "url": "https://github.com/withastro/docs.git",
    }:
        raise EvaluationError("repository binding does not match the accepted Astro snapshot")
    know = exact_keys(
        acquisition["know"],
        {"accepted_export", "export_is_append_only_and_ignored", "key", "source_id", "source_type"},
        "Know binding",
    )
    export = exact_keys(know["accepted_export"], {"bytes", "path", "sha256"}, "Know export binding")
    if (
        know["key"] != "astro-technical-docs-2026-07"
        or know["source_id"] != "github-docs.git"
        or know["source_type"] != "github"
        or know["export_is_append_only_and_ignored"] is not True
        or export["bytes"] != 22663290
        or export["sha256"] != "5a49689fb5775c5f03717cbc11af0389d1014082b9f4c44fd21e4a03ffe71bec"
    ):
        raise EvaluationError("Know acquisition binding differs from the accepted export")

    inventory = exact_keys(
        read_json(CORPUS / "input-inventory.json"),
        {"authoritative_tree_sha256", "document_count", "documents", "schema_version", "total_bytes"},
        "input inventory",
    )
    if inventory["schema_version"] != "semantic-okf-astro-input-inventory/1.0":
        raise EvaluationError("unsupported inventory schema")
    documents = inventory["documents"]
    if not isinstance(documents, list) or len(documents) != EXPECTED_DOCUMENTS:
        raise EvaluationError(f"inventory must contain exactly {EXPECTED_DOCUMENTS} documents")
    if inventory["document_count"] != EXPECTED_DOCUMENTS or acquisition["documents"] != EXPECTED_DOCUMENTS:
        raise EvaluationError("document counts disagree")

    by_source: dict[str, dict[str, Any]] = {}
    by_document: dict[str, dict[str, Any]] = {}
    upstreams: list[str] = []
    tree_entries: list[dict[str, str]] = []
    section_counts: Counter[str] = Counter()
    total_bytes = 0
    for number, row in enumerate(documents, start=1):
        row = exact_keys(
            row,
            {
                "bytes",
                "canonical_url",
                "document_id",
                "path",
                "record_id",
                "section",
                "sha256",
                "source_id",
                "title",
                "upstream_path",
            },
            f"inventory document {number}",
        )
        upstream = row["upstream_path"]
        prefix = "src/content/docs/en/"
        if not isinstance(upstream, str) or not upstream.startswith(prefix) or not upstream.endswith(".mdx"):
            raise EvaluationError(f"inventory document {number} has an invalid upstream path")
        relative = upstream.removeprefix(prefix)
        expected_path = f"corpus/sources/mdx/{relative}"
        expected_record = f"sources/mdx/{relative}".removesuffix(".mdx")
        expected_document = route_for(relative)
        expected_source = source_id_for(expected_document)
        expected_url = f"https://docs.astro.build{expected_document}"
        expected_section = relative.split("/", 1)[0] if "/" in relative else "(root)"
        if row["path"] != expected_path:
            raise EvaluationError(f"inventory document {number} has a non-derived corpus path")
        if row["record_id"] != expected_record:
            raise EvaluationError(f"inventory document {number} has a non-derived record ID")
        if row["document_id"] != expected_document or row["canonical_url"] != expected_url:
            raise EvaluationError(f"inventory document {number} has a non-canonical route identity")
        if row["source_id"] != expected_source or SOURCE_ID_RE.fullmatch(row["source_id"]) is None:
            raise EvaluationError(f"inventory document {number} has a non-derived source ID")
        if row["section"] != expected_section:
            raise EvaluationError(f"inventory document {number} has a non-derived section")
        if not isinstance(row["title"], str) or not row["title"].strip():
            raise EvaluationError(f"inventory document {number} has no title")
        path = safe_relative(EVALUATION, row["path"], f"inventory document {number}.path")
        if not path.is_file():
            raise EvaluationError(f"authoritative file is missing: {path}")
        payload = path.read_bytes()
        if row["bytes"] != len(payload) or row["sha256"] != sha256_bytes(payload):
            raise EvaluationError(f"authoritative file binding differs: {path}")
        if HEX64_RE.fullmatch(row["sha256"]) is None:
            raise EvaluationError(f"inventory document {number} has an invalid digest")
        if row["source_id"] in by_source or row["document_id"] in by_document:
            raise EvaluationError("source and document identities must be unique")
        by_source[row["source_id"]] = dict(row)
        by_document[row["document_id"]] = dict(row)
        upstreams.append(upstream)
        tree_entries.append({"path": upstream, "sha256": row["sha256"]})
        section_counts[row["section"]] += 1
        total_bytes += len(payload)
    if upstreams != sorted(upstreams) or len(set(upstreams)) != EXPECTED_DOCUMENTS:
        raise EvaluationError("inventory documents must be uniquely sorted by upstream path")
    tree_sha256 = sha256_bytes(canonical_json(tree_entries).encode("utf-8"))
    if not (
        inventory["authoritative_tree_sha256"]
        == acquisition["tree_sha256"]
        == tree_sha256
    ):
        raise EvaluationError("authoritative tree digests disagree")
    if not (inventory["total_bytes"] == acquisition["total_bytes"] == total_bytes):
        raise EvaluationError("authoritative byte totals disagree")
    if acquisition["section_counts"] != dict(sorted(section_counts.items())):
        raise EvaluationError("section counts do not match the frozen files")

    manifest = exact_keys(
        read_json(CORPUS / "manifest.json"),
        {"bundle", "ontology", "rules", "schema_version", "sources"},
        "Semantic OKF manifest",
    )
    if manifest["schema_version"] != "1.0" or manifest["rules"] != []:
        raise EvaluationError("Semantic OKF manifest must use the minimal schema with no rules")
    exact_keys(
        manifest["bundle"],
        {"base_iri", "description", "ontology_iri", "owl_profile", "prefix", "title", "version_iri"},
        "Semantic OKF bundle",
    )
    ontology = exact_keys(manifest["ontology"], {"classes", "properties"}, "Semantic OKF ontology")
    if ontology["classes"] != [{"label": "documentation page", "name": "DocumentationPage"}]:
        raise EvaluationError("Semantic OKF ontology class differs from the minimal projection")
    sources = manifest["sources"]
    if not isinstance(sources, list) or len(sources) != EXPECTED_DOCUMENTS:
        raise EvaluationError("Semantic OKF manifest must select exactly 416 sources")
    for number, source in enumerate(sources, start=1):
        source = exact_keys(
            source,
            {"concept_type", "fields", "id", "kind", "ontology_class", "path"},
            f"Semantic OKF source {number}",
        )
        inventory_row = by_source.get(source["id"])
        if inventory_row is None:
            raise EvaluationError(f"Semantic OKF source {number} is absent from inventory")
        if source != {
            "concept_type": "Astro Documentation Page",
            "fields": {"description": "pageDescription", "title": "pageTitle"},
            "id": inventory_row["source_id"],
            "kind": "markdown",
            "ontology_class": "DocumentationPage",
            "path": inventory_row["path"].removeprefix("corpus/"),
        }:
            raise EvaluationError(f"Semantic OKF source {number} differs from inventory")

    identity = exact_keys(
        read_json(CORPUS / "source-combination.json"),
        {
            "documents",
            "identity_kind",
            "records",
            "schema_version",
            "source_ids_to_document_ids",
            "source_record_to_document_ids",
        },
        "source combination",
    )
    if (
        identity["schema_version"] != "semantic-okf-astro-source-identity/1.1"
        or identity["identity_kind"] != "canonical-route"
    ):
        raise EvaluationError("unsupported source identity schema")
    identity_keys = {"canonical_url", "document_id", "path", "record_id", "source_id", "upstream_path"}
    expected_identity_rows = [
        {key: row[key] for key in sorted(identity_keys)} for row in documents
    ]
    for collection in ("documents", "records"):
        rows = identity[collection]
        if not isinstance(rows, list) or len(rows) != EXPECTED_DOCUMENTS:
            raise EvaluationError(f"source combination {collection} must contain 416 rows")
        for number, row in enumerate(rows, start=1):
            exact_keys(row, identity_keys, f"source combination {collection} row {number}")
        if rows != expected_identity_rows:
            raise EvaluationError(f"source combination {collection} differs from inventory")
    expected_sources = {row["source_id"]: row["document_id"] for row in documents}
    expected_records = {
        canonical_json([row["source_id"], row["record_id"]]): row["document_id"]
        for row in documents
    }
    if identity["source_ids_to_document_ids"] != expected_sources:
        raise EvaluationError("source-to-document identity map is not total and exact")
    if identity["source_record_to_document_ids"] != expected_records:
        raise EvaluationError("source-record-to-document identity map is not total and exact")
    return by_source, by_document, set(expected_records)


def _validate_claims(
    rows: Any,
    label: str,
    evidence_ids: set[str],
    *,
    minimum: int,
) -> set[str]:
    if not isinstance(rows, list) or len(rows) < minimum:
        raise EvaluationError(f"{label} must contain at least {minimum} rows")
    ids: set[str] = set()
    for number, row in enumerate(rows, start=1):
        row = exact_keys(row, {"evidence_ids", "id", "statement"}, f"{label} row {number}")
        if not isinstance(row["id"], str) or not row["id"] or row["id"] in ids:
            raise EvaluationError(f"{label} row {number} has a duplicate or empty ID")
        if not isinstance(row["statement"], str) or not row["statement"].strip():
            raise EvaluationError(f"{label} row {number} has no statement")
        bindings = nonempty_strings(row["evidence_ids"], f"{label} row {number}.evidence_ids")
        if len(bindings) != len(set(bindings)) or not set(bindings).issubset(evidence_ids):
            raise EvaluationError(f"{label} row {number} has invalid evidence bindings")
        ids.add(row["id"])
    return ids


def validate_benchmark(
    by_source: Mapping[str, Mapping[str, Any]],
    by_document: Mapping[str, Mapping[str, Any]],
) -> dict[str, int]:
    questions = read_jsonl(BENCHMARK / "retrieval-questions.jsonl")
    if len(questions) != 40:
        raise EvaluationError("retrieval benchmark must contain exactly 40 questions")
    expected_ids = [f"q{number:03d}" for number in range(1, 41)]
    type_counts: Counter[str] = Counter()
    by_id: dict[str, dict[str, Any]] = {}
    all_source_ids = set(by_source)
    all_document_ids = set(by_document)
    all_upstream_paths = {row["upstream_path"] for row in by_source.values()}
    for number, row in enumerate(questions, start=1):
        row = exact_keys(row, {"id", "qrels", "question", "question_type"}, f"question {number}")
        expected_id = expected_ids[number - 1]
        if row["id"] != expected_id:
            raise EvaluationError(f"question {number} must use ID {expected_id}")
        if row["question_type"] not in {"direct", "cross-document", "hard"}:
            raise EvaluationError(f"{expected_id} has an unsupported type")
        if not isinstance(row["question"], str) or not row["question"].strip():
            raise EvaluationError(f"{expected_id} has an empty prompt")
        qrels = exact_keys(row["qrels"], {"document_ids", "source_ids"}, f"{expected_id}.qrels")
        documents = sorted_unique_strings(qrels["document_ids"], f"{expected_id}.document_ids")
        sources = sorted_unique_strings(qrels["source_ids"], f"{expected_id}.source_ids")
        if not set(documents).issubset(all_document_ids) or not set(sources).issubset(all_source_ids):
            raise EvaluationError(f"{expected_id} qrels name unknown corpus identities")
        if sorted(by_source[source]["document_id"] for source in sources) != documents:
            raise EvaluationError(f"{expected_id} source and document qrels do not map exactly")
        minimum = 2 if row["question_type"] in {"cross-document", "hard"} else 1
        if len(documents) < minimum:
            raise EvaluationError(f"{expected_id} does not meet its multi-document contract")
        prompt = row["question"]
        if QUESTION_ID_RE.search(prompt) or HEX64_RE.search(prompt) or SOURCE_ID_RE.search(prompt):
            raise EvaluationError(f"{expected_id} prompt leaks an evaluator identity or digest")
        if any(path in prompt for path in all_upstream_paths) or any(route in prompt for route in all_document_ids):
            raise EvaluationError(f"{expected_id} prompt leaks an authoritative path or qrel route")
        type_counts[row["question_type"]] += 1
        by_id[expected_id] = dict(row)
    if dict(type_counts) != {"direct": 20, "cross-document": 10, "hard": 10}:
        raise EvaluationError(f"question type counts differ: {dict(type_counts)}")

    hard_questions = read_jsonl(BENCHMARK / "hard-questions.jsonl")
    expected_hard = [by_id[f"q{number:03d}"] for number in range(31, 41)]
    if hard_questions != expected_hard:
        raise EvaluationError("hard question subset differs from q031 through q040")
    truths = read_jsonl(BENCHMARK / "hard-ground-truth.jsonl")
    if len(truths) != 10:
        raise EvaluationError("hard ground truth must contain exactly ten rows")
    evidence_count = 0
    claim_count = 0
    negative_count = 0
    for offset, truth in enumerate(truths, start=31):
        qid = f"q{offset:03d}"
        truth = exact_keys(
            truth,
            {"authoritative_evidence", "ground_truth", "id", "question", "schema_version"},
            f"{qid} ground truth",
        )
        if (
            truth["schema_version"] != "semantic-okf-astro-hard-ground-truth/1.0"
            or truth["id"] != qid
            or truth["question"] != by_id[qid]["question"]
        ):
            raise EvaluationError(f"{qid} ground truth identity differs from the question")
        evidence = truth["authoritative_evidence"]
        if not isinstance(evidence, list) or len(evidence) < 2:
            raise EvaluationError(f"{qid} needs evidence from multiple sections")
        evidence_ids: set[str] = set()
        evidence_documents: set[str] = set()
        evidence_sources: set[str] = set()
        evidence_paths: set[str] = set()
        for number, row in enumerate(evidence, start=1):
            row = exact_keys(
                row,
                {
                    "document_id",
                    "end_char",
                    "file_sha256",
                    "heading",
                    "heading_path",
                    "id",
                    "locator",
                    "path",
                    "role",
                    "source_id",
                    "start_char",
                    "text_sha256",
                    "upstream_path",
                },
                f"{qid} evidence {number}",
            )
            if not isinstance(row["id"], str) or row["id"] in evidence_ids:
                raise EvaluationError(f"{qid} has a duplicate evidence ID")
            evidence_ids.add(row["id"])
            document = by_source.get(row["source_id"])
            if document is None or document["document_id"] != row["document_id"]:
                raise EvaluationError(f"{qid} evidence {number} has inconsistent identities")
            expected_repo_path = f"evaluations/semantic-okf-astro/{document['path']}"
            if row["path"] != expected_repo_path or row["upstream_path"] != document["upstream_path"]:
                raise EvaluationError(f"{qid} evidence {number} has an inconsistent path")
            path = safe_relative(REPO_ROOT, row["path"], f"{qid} evidence {number}.path")
            payload = path.read_bytes()
            if row["file_sha256"] != sha256_bytes(payload) or row["file_sha256"] != document["sha256"]:
                raise EvaluationError(f"{qid} evidence {number} file digest differs")
            text = payload.decode("utf-8-sig")
            start, end = row["start_char"], row["end_char"]
            if (
                isinstance(start, bool)
                or isinstance(end, bool)
                or not isinstance(start, int)
                or not isinstance(end, int)
                or not 0 <= start < end <= len(text)
            ):
                raise EvaluationError(f"{qid} evidence {number} has an invalid character interval")
            selected = text[start:end]
            if row["text_sha256"] != sha256_bytes(selected.encode("utf-8")):
                raise EvaluationError(f"{qid} evidence {number} selected-text digest differs")
            expected_locator = f"heading={row['heading']};chars={start}-{end}"
            if row["locator"] != expected_locator:
                raise EvaluationError(f"{qid} evidence {number} locator differs")
            if (
                not isinstance(row["heading_path"], list)
                or not row["heading_path"]
                or row["heading_path"][-1] != row["heading"]
            ):
                raise EvaluationError(f"{qid} evidence {number} heading path is invalid")
            match = HEADING_RE.match(selected)
            if match is None or match.group(2).strip() != row["heading"]:
                raise EvaluationError(f"{qid} evidence {number} interval does not begin at its heading")
            if not isinstance(row["role"], str) or not row["role"].strip():
                raise EvaluationError(f"{qid} evidence {number} has no role")
            evidence_documents.add(row["document_id"])
            evidence_sources.add(row["source_id"])
            evidence_paths.add(row["upstream_path"])
        if len(evidence_documents) < 2 or len(evidence_paths) < 2:
            raise EvaluationError(f"{qid} evidence must span at least two authoritative documents")

        ground = exact_keys(
            truth["ground_truth"],
            {
                "acceptable_variants",
                "answer_claims",
                "derivation",
                "failure_conditions",
                "important_negatives",
                "required_document_ids",
                "required_source_ids",
            },
            f"{qid}.ground_truth",
        )
        required_documents = sorted_unique_strings(ground["required_document_ids"], f"{qid}.required_document_ids", minimum=2)
        required_sources = sorted_unique_strings(ground["required_source_ids"], f"{qid}.required_source_ids", minimum=2)
        if required_documents != by_id[qid]["qrels"]["document_ids"]:
            raise EvaluationError(f"{qid} required documents differ from qrels")
        if required_sources != by_id[qid]["qrels"]["source_ids"]:
            raise EvaluationError(f"{qid} required sources differ from qrels")
        if not evidence_documents.issubset(set(required_documents)) or not evidence_sources.issubset(set(required_sources)):
            raise EvaluationError(f"{qid} evidence falls outside its required identities")
        claims = _validate_claims(ground["answer_claims"], f"{qid}.answer_claims", evidence_ids, minimum=4)
        negatives = _validate_claims(ground["important_negatives"], f"{qid}.important_negatives", evidence_ids, minimum=2)
        derivation = ground["derivation"]
        if not isinstance(derivation, list) or len(derivation) < 2:
            raise EvaluationError(f"{qid}.derivation needs at least two explicit operations")
        used_claims: set[str] = set()
        for number, row in enumerate(derivation, start=1):
            row = exact_keys(row, {"conclusion", "inputs", "operation"}, f"{qid}.derivation {number}")
            inputs = nonempty_strings(row["inputs"], f"{qid}.derivation {number}.inputs")
            if not set(inputs).issubset(claims):
                raise EvaluationError(f"{qid}.derivation {number} references unknown claims")
            if not isinstance(row["operation"], str) or not row["operation"].strip():
                raise EvaluationError(f"{qid}.derivation {number} has no operation")
            if not isinstance(row["conclusion"], str) or not row["conclusion"].strip():
                raise EvaluationError(f"{qid}.derivation {number} has no conclusion")
            used_claims.update(inputs)
        if used_claims != claims:
            raise EvaluationError(f"{qid} derivation does not consume every atomic answer claim")
        nonempty_strings(ground["acceptable_variants"], f"{qid}.acceptable_variants")
        nonempty_strings(ground["failure_conditions"], f"{qid}.failure_conditions", minimum=2)
        evidence_count += len(evidence_ids)
        claim_count += len(claims)
        negative_count += len(negatives)

    manifest = exact_keys(
        read_json(BENCHMARK / "benchmark-manifest.json"),
        {"contracts", "counts", "files", "question_specs_sha256", "schema_version"},
        "benchmark manifest",
    )
    if manifest["schema_version"] != "semantic-okf-astro-benchmark-manifest/1.0":
        raise EvaluationError("unsupported benchmark manifest schema")
    exact_keys(manifest["contracts"], {"authority", "evidence_locator", "prompt_isolation", "qrels"}, "benchmark contracts")
    expected_counts = {
        "answer_claims": claim_count,
        "cross_document": 10,
        "direct": 20,
        "evidence_bindings": evidence_count,
        "hard": 10,
        "important_negatives": negative_count,
        "questions": 40,
    }
    if manifest["counts"] != expected_counts:
        raise EvaluationError("benchmark manifest counts differ from validated rows")
    question_specs = BENCHMARK / "question-specs.json"
    if manifest["question_specs_sha256"] != sha256_bytes(question_specs.read_bytes()):
        raise EvaluationError("question-spec digest differs")
    files = manifest["files"]
    expected_files = {"hard-ground-truth.jsonl", "hard-questions.jsonl", "retrieval-questions.jsonl"}
    if not isinstance(files, dict) or set(files) != expected_files:
        raise EvaluationError("benchmark file manifest is incomplete")
    for name, row in files.items():
        row = exact_keys(row, {"path", "row_count", "sha256"}, f"benchmark file {name}")
        path = BENCHMARK / name
        payload = path.read_bytes()
        if row["path"] != f"evaluations/semantic-okf-astro/benchmark/{name}":
            raise EvaluationError(f"benchmark file {name} has an invalid path binding")
        if row["row_count"] != payload.count(b"\n") or row["sha256"] != sha256_bytes(payload):
            raise EvaluationError(f"benchmark file {name} binding differs")
    return expected_counts


def _selection_from_plan(name: str, value: Mapping[str, Any]) -> list[str]:
    if name == "ensemble-plan.json":
        if value.get("schema_version") != "2.0":
            raise EvaluationError("ensemble plan must use source-generic schema 2.0")
        adaptive = exact_keys(value.get("adaptive"), set(value["adaptive"]), "ensemble adaptive plan")
        graph = exact_keys(value.get("entity_graph"), set(value["entity_graph"]), "ensemble graph plan")
        embedding = exact_keys(value.get("embedding"), set(value["embedding"]), "ensemble embedding plan")
        selections = [
            adaptive.get("selection", {}).get("source_ids"),
            graph.get("selection", {}).get("source_ids"),
            embedding.get("selection", {}).get("source_ids"),
        ]
        if selections[0] != selections[1] or selections[0] != selections[2]:
            raise EvaluationError("ensemble child selections differ")
        identity = exact_keys(value.get("identity"), {"default_grouping", "overrides"}, "ensemble identity")
        if identity != {"default_grouping": "source-record-v1", "overrides": []}:
            raise EvaluationError("Astro ensemble must use exact default source-record identity")
        return selections[0]
    selection = exact_keys(value.get("selection"), {"source_ids"}, f"{name} selection")
    return selection["source_ids"]


def validate_plans(source_ids: set[str]) -> None:
    manifest = exact_keys(
        read_json(PLANS / "plan-manifest.json"),
        {"authority", "files", "schema_version", "selected_sources", "selection_sha256"},
        "plan manifest",
    )
    if manifest["schema_version"] != "semantic-okf-astro-plan-manifest/1.0":
        raise EvaluationError("unsupported plan manifest schema")
    expected_selection = sorted(source_ids)
    if manifest["selected_sources"] != EXPECTED_DOCUMENTS:
        raise EvaluationError("plan manifest selected source count differs")
    if manifest["selection_sha256"] != sha256_bytes(canonical_json(expected_selection).encode("utf-8")):
        raise EvaluationError("plan selection digest differs")
    expected_names = {
        "adaptive-plan.json",
        "classical-plan.json",
        "embedding-plan.json",
        "ensemble-plan.json",
        "entity-graph-plan.json",
    }
    files = manifest["files"]
    if not isinstance(files, dict) or set(files) != expected_names:
        raise EvaluationError("plan manifest file set differs")
    for name in sorted(expected_names):
        binding = exact_keys(files[name], {"path", "sha256"}, f"plan binding {name}")
        path = PLANS / name
        payload = path.read_bytes()
        if binding["path"] != f"evaluations/semantic-okf-astro/plans/{name}":
            raise EvaluationError(f"plan {name} path binding differs")
        if binding["sha256"] != sha256_bytes(payload):
            raise EvaluationError(f"plan {name} digest differs")
        if QUESTION_ID_RE.search(payload.decode("utf-8")):
            raise EvaluationError(f"plan {name} leaks a benchmark question ID")
        value = read_json(path)
        if not isinstance(value, dict):
            raise EvaluationError(f"plan {name} must be an object")
        selection = _selection_from_plan(name, value)
        if selection != expected_selection:
            raise EvaluationError(f"plan {name} does not select the complete frozen corpus")


def validate() -> dict[str, Any]:
    by_source, by_document, record_keys = validate_corpus()
    counts = validate_benchmark(by_source, by_document)
    validate_plans(set(by_source))
    return {
        "answer_claims": counts["answer_claims"],
        "documents": len(by_document),
        "evidence_bindings": counts["evidence_bindings"],
        "hard_questions": counts["hard"],
        "questions": counts["questions"],
        "source_record_mappings": len(record_keys),
        "status": "pass",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = validate()
        print(json.dumps(result, sort_keys=True) if args.json else "Astro evaluation: pass")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, EvaluationError) as exc:
        result = {"error": str(exc), "status": "fail"}
        print(json.dumps(result, sort_keys=True) if args.json else f"Astro evaluation: fail: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
