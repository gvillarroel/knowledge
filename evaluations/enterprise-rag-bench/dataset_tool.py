#!/usr/bin/env python3
"""Acquire pinned EnterpriseRAG bytes and prepare an evaluator-free local corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import tempfile
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parent
DOC_ID = re.compile(r"^(dsid_[0-9a-f]{32})__.+\.txt$")


def sha256(path: Path) -> str:
    """Hash a file without loading an archive into memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def json_bytes(value: Any) -> bytes:
    """Serialize portable deterministic JSON."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def read_descriptor() -> dict[str, Any]:
    """Read the versioned acquisition and selection contract."""
    return json.loads((ROOT / "descriptor.json").read_text(encoding="utf-8"))


def download(url: str, target: Path, expected: str, size: int | None = None) -> None:
    """Download atomically and reject unexpected bytes, including cached drift."""
    if target.exists():
        if sha256(target) != expected or (size is not None and target.stat().st_size != size):
            raise ValueError(f"cached input digest or size mismatch: {target.name}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "knowledge-enterpriserag/1.0"})
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        pending = Path(stream.name)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                shutil.copyfileobj(response, stream, length=4 * 1024 * 1024)
        except BaseException:
            stream.close()
            pending.unlink(missing_ok=True)
            raise
    try:
        if sha256(pending) != expected or (size is not None and pending.stat().st_size != size):
            raise ValueError(f"download digest or size mismatch: {target.name}")
        pending.rename(target)
    finally:
        pending.unlink(missing_ok=True)


def acquire(root: Path, descriptor: dict[str, Any]) -> None:
    """Fetch the pinned corpus, evaluator questions, and upstream license."""
    upstream = descriptor["upstream"]
    base = ("https://raw.githubusercontent.com/onyx-dot-app/EnterpriseRAG-Bench/"
            + upstream["commit"] + "/")
    archive = upstream["archive"]
    download(archive["url"], root / "raw/all_documents.zip", archive["sha256"], archive["bytes"])
    download(base + "questions.jsonl", root / "raw/questions.jsonl", upstream["questions_sha256"])
    download(base + "LICENSE", root / "raw/LICENSE", upstream["license_sha256"])


def load_questions(path: Path, descriptor: dict[str, Any]) -> list[dict[str, Any]]:
    """Check source question identities and the exact retrieval eligibility boundary."""
    if sha256(path) != descriptor["upstream"]["questions_sha256"]:
        raise ValueError("upstream questions digest mismatch")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != descriptor["upstream"]["question_count"]:
        raise ValueError("upstream question count mismatch")
    seen: set[str] = set()
    selected = descriptor["selection"]
    for row in rows:
        key = row.get("question_id")
        ids = row.get("expected_doc_ids")
        category = row.get("question_type")
        if (not isinstance(key, str) or key in seen
                or not isinstance(row.get("question"), str) or not row["question"].strip()
                or not isinstance(ids, list)
                or any(not isinstance(x, str) or not re.fullmatch(r"dsid_[0-9a-f]{32}", x) for x in ids)):
            raise ValueError("invalid upstream question or duplicate identity")
        if category in selected["categories"] and not ids:
            raise ValueError("retrieval category has no reference documents")
        if category in selected["excluded_categories"] and ids:
            raise ValueError("unscored category unexpectedly has reference documents")
        if category not in selected["categories"] + selected["excluded_categories"]:
            raise ValueError("unknown upstream category")
        seen.add(key)
    return rows


def selection_key(seed: str, domain: str, identity: str) -> str:
    """Select by a domain-separated digest, independently of enumeration order."""
    return hashlib.sha256(f"{seed}\0{domain}\0{identity}".encode()).hexdigest()


def select_questions(rows: list[dict[str, Any]], selection: dict[str, Any]) -> list[dict[str, Any]]:
    """Take a fixed quota from each grounded category before any strategy runs."""
    chosen: list[dict[str, Any]] = []
    for category in selection["categories"]:
        eligible = [row for row in rows if row["question_type"] == category]
        if len(eligible) < selection["questions_per_category"]:
            raise ValueError("insufficient category coverage")
        chosen.extend(sorted(eligible, key=lambda row: (
            selection_key(selection["seed"], "question", row["question_id"]), row["question_id"]
        ))[:selection["questions_per_category"]])
    return sorted(chosen, key=lambda row: row["question_id"])


def inventory(archive: zipfile.ZipFile, sources: list[str]) -> tuple[dict[str, zipfile.ZipInfo], dict[str, int]]:
    """Inventory safe document members; never expose the ZIP's embedded questions."""
    result: dict[str, zipfile.ZipInfo] = {}
    ambiguous: set[str] = set()
    count = 0
    for info in archive.infolist():
        path = PurePosixPath(info.filename)
        if (path.is_absolute() or ".." in path.parts or "\\" in info.filename
                or ":" in info.filename or stat.S_ISLNK(info.external_attr >> 16)):
            raise ValueError("unsafe archive member")
        if info.is_dir() or info.filename == "questions.jsonl":
            continue
        match = DOC_ID.fullmatch(path.name)
        if not match or path.parts[0] not in sources or info.file_size > 20 * 1024 * 1024:
            raise ValueError("unknown or oversized document member")
        identity = match[1]
        count += 1
        if identity in result:
            ambiguous.add(identity)
        result[identity] = info
    summary = {"document_count": count, "unique_document_ids": len(result),
               "ambiguous_document_ids": len(ambiguous)}
    return {key: info for key, info in result.items() if key not in ambiguous}, summary


def manifest(sources: list[str], dataset_id: str) -> dict[str, Any]:
    """Reproduce v1 declarations; fulltext_projection adds its missing body mapping."""
    return {
        "schema_version": "1.0",
        "bundle": {"title": "EnterpriseRAG reduced enterprise corpus",
                   "description": "Nine independent source declarations from pinned Redwood Inference documents.",
                   "base_iri": f"https://example.org/knowledge/{dataset_id}/",
                   "ontology_iri": f"https://example.org/ontology/{dataset_id}",
                   "version_iri": f"https://example.org/ontology/{dataset_id}/1.0.0",
                   "prefix": "enterprise", "owl_profile": "rl"},
        "ontology": {"classes": [{"name": "EnterpriseDocument", "label": "enterprise document"}],
                     "properties": []},
        "rules": [],
        "sources": [{"id": source.replace("_", "-"), "kind": "json",
                     "path": f"documents/{source}.jsonl", "concept_type": "Enterprise document",
                     "ontology_class": "EnterpriseDocument", "id_field": "id", "title_field": "title",
                     "schema": {"id": "string", "title": "string", "body": "string",
                                "upstream_path": "string", "upstream_sha256": "string"}}
                    for source in sources],
    }


def materialize(root: Path, destination: Path, descriptor: dict[str, Any]) -> dict[str, Any]:
    """Render a deterministic dataset with physically separate input and evaluator trees."""
    archive_path = root / "raw/all_documents.zip"
    if sha256(archive_path) != descriptor["upstream"]["archive"]["sha256"]:
        raise ValueError("archive digest mismatch")
    all_questions = load_questions(root / "raw/questions.jsonl", descriptor)
    selection = descriptor["selection"]
    questions = select_questions(all_questions, selection)
    required = {identity for row in questions for identity in row["expected_doc_ids"]}
    with zipfile.ZipFile(archive_path) as archive:
        documents, audit = inventory(archive, selection["sources"])
        if any(value != descriptor["upstream"][key] for key, value in audit.items()):
            raise ValueError("archive inventory count mismatch")
        if not required <= documents.keys():
            raise ValueError("selected reference document is missing or ambiguous")
        distractors: set[str] = set()
        for source in selection["sources"]:
            eligible = [key for key, info in documents.items()
                        if info.filename.startswith(source + "/") and key not in required]
            if len(eligible) < selection["distractors_per_source"]:
                raise ValueError("insufficient distractor coverage")
            distractors.update(sorted(eligible, key=lambda key: (
                selection_key(selection["seed"], "distractor", key), key
            ))[:selection["distractors_per_source"]])
        by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
        replacement_characters = 0
        for identity in sorted(required | distractors):
            info = documents[identity]
            raw = archive.read(info)
            body = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
            if not body.strip():
                raise ValueError("empty document")
            replacement_characters += body.count("\ufffd")
            source = info.filename.split("/")[0]
            by_source[source].append({"id": identity, "title": body.splitlines()[0].strip() or identity,
                                      "body": body, "upstream_path": info.filename,
                                      "upstream_sha256": hashlib.sha256(raw).hexdigest()})
    input_root = destination / "input"
    (input_root / "documents").mkdir(parents=True)
    (destination / "evaluator").mkdir()
    for source, rows in sorted(by_source.items()):
        data = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
        (input_root / "documents" / f"{source}.jsonl").write_text(data, encoding="utf-8", newline="\n")
    (input_root / "manifest.json").write_bytes(json_bytes(manifest(selection["sources"], descriptor["dataset_id"])))
    shutil.copyfile(root / "raw/LICENSE", input_root / "LICENSE")
    evaluator = [{"id": row["question_id"], "question": row["question"],
                  "category": row["question_type"], "cohort": "retrospective-diagnostic",
                  "relevant": sorted(set(row["expected_doc_ids"])),
                  "gold_answer": row["gold_answer"], "answer_facts": row["answer_facts"]}
                 for row in questions]
    (destination / "evaluator/questions.json").write_bytes(json_bytes(evaluator))
    summary = {"schema_version": "enterprise-rag-preparation/1.0", "dataset_id": descriptor["dataset_id"],
               "upstream_document_count": audit["document_count"], "upstream_question_count": len(all_questions),
               "upstream_ambiguous_document_ids_quarantined": audit["ambiguous_document_ids"],
               "question_count": len(questions), "document_count": len(required | distractors),
               "reference_document_count": len(required), "distractor_count": len(distractors),
               "source_counts": {key: len(rows) for key, rows in sorted(by_source.items())},
               "category_counts": dict(sorted(Counter(row["category"] for row in evaluator).items())),
               "unscored_upstream_questions": len(all_questions) - len(questions),
               "upstream_duplicate_qrel_entries": sum(len(row["expected_doc_ids"]) - len(set(row["expected_doc_ids"])) for row in all_questions),
               "upstream_replacement_characters_preserved": replacement_characters,
               "descriptor_sha256": hashlib.sha256(json_bytes(descriptor)).hexdigest(),
               "promotion_eligible": False, "semantic_family_count": 1}
    (destination / "preparation.json").write_bytes(json_bytes(summary))
    return summary


def tree_hashes(root: Path) -> dict[str, str]:
    """Return a portable complete file inventory for deterministic checks."""
    if any(path.is_symlink() for path in root.rglob("*")):
        raise ValueError("symlinks are not allowed in prepared inputs")
    return {path.relative_to(root).as_posix(): sha256(path)
            for path in sorted(root.rglob("*")) if path.is_file()}


def prepare(root: Path, descriptor: dict[str, Any], check: bool = False) -> dict[str, Any]:
    """Publish once or verify all bytes by independent deterministic regeneration."""
    parent = root / "processed"
    parent.mkdir(parents=True, exist_ok=True)
    destination = parent / descriptor["dataset_id"]
    if destination.exists() and not check:
        raise ValueError("prepared dataset exists; use --check or a new dataset version")
    if check and not destination.is_dir():
        raise ValueError("prepared dataset is missing")
    with tempfile.TemporaryDirectory(prefix=".prepare-", dir=parent) as temporary:
        pending = Path(temporary) / "dataset"
        summary = materialize(root, pending, descriptor)
        if check:
            if tree_hashes(pending) != tree_hashes(destination):
                raise ValueError("deterministic regeneration detected dataset drift")
        else:
            pending.rename(destination)
    return summary


def main() -> int:
    """Run pinned acquisition or deterministic preparation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["acquire", "prepare"])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        descriptor = read_descriptor()
        if args.command == "acquire":
            if args.check:
                raise ValueError("--check applies to prepare")
            acquire(args.root, descriptor)
            result = {"status": "pass", "operation": "acquire"}
        else:
            result = prepare(args.root, descriptor, args.check)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
