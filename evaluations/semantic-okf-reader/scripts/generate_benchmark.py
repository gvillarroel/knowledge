#!/usr/bin/env python3
"""Generate the 300-question isolated Semantic OKF reader benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


EVALUATION_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_ROOT = (
    EVALUATION_ROOT / "fixtures" / "workspaces" / "reader-v2-overlay" / "knowledge"
)
SKILL_SNAPSHOT_ROOT = (
    EVALUATION_ROOT
    / "fixtures"
    / "workspaces"
    / "reader-v2-overlay"
    / "skills"
    / "consult-semantic-okf"
)
QUESTION_COUNT = 300
PINNED_SNAPSHOT_TREE_SHA256 = "d1071f6f53b8df9bef5e1ea37b69b9efdb3ed8d5fe5ec4d9496ad7e28259fe43"
PINNED_SKILL_SNAPSHOT_TREE_SHA256 = (
    "5d4f0f3eafa9d68d82dfa698b53b281cb6930d05bc1ef7f0c12bd44eaacaf73a"
)
CATEGORY_COUNTS = {
    "typed-fact": 40,
    "relation-traversal": 40,
    "multi-hop-join": 50,
    "typed-filter": 40,
    "aggregation": 45,
    "provenance-lineage": 40,
    "ontology-shacl": 20,
    "integrity-negative": 15,
    "bundle-inventory": 10,
}


class LiteralString(str):
    """Request YAML literal-block rendering for long prompt and JavaScript text."""


class BenchmarkDumper(yaml.SafeDumper):
    """Render benchmark YAML without lossy Unicode conversion."""


def _represent_literal(dumper: BenchmarkDumper, value: LiteralString) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")


BenchmarkDumper.add_representer(LiteralString, _represent_literal)


def canonical_json(value: Any) -> str:
    """Return compact, stable JSON used by hidden assertions and JSONL output."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def semantic_signature(descriptor: dict[str, Any]) -> str:
    """Hash a canonical query descriptor that is independent of prompt wording."""

    return hashlib.sha256(canonical_json(descriptor).encode("utf-8")).hexdigest()


def javascript_json_value(value: Any) -> Any:
    """Normalize values to the representation produced by JavaScript JSON.stringify."""

    if isinstance(value, str):
        if re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
            value,
        ):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return (
                parsed.astimezone(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z")
            )
        return value
    if isinstance(value, bool) or value is None or isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, list):
        return [javascript_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): javascript_json_value(item) for key, item in value.items()}
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def result_sha256(value: Any) -> str:
    """Hash a value using the same canonical JSON representation as the JS assertions."""

    normalized = javascript_json_value(value)
    return hashlib.sha256(canonical_json(normalized).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object or fail with a useful generator error."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def load_records(bundle: Path) -> list[dict[str, Any]]:
    """Load and validate the normalized record ledger."""

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        (bundle / "semantic" / "records.jsonl").read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"records.jsonl line {line_number} is not an object")
        records.append(value)
    if len(records) != 60:
        raise ValueError(f"the pinned fixture must contain 60 records, found {len(records)}")
    return sorted(records, key=lambda item: str(item["concept_id"]))


def local_name(iri: str) -> str:
    """Return the local fragment of one ontology IRI."""

    return re.split(r"[/#]", iri.rstrip("/#"))[-1]


def semantic_properties(
    record: dict[str, Any], source_specs: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Translate ledger input-field keys into reviewed ontology property names."""

    source = source_specs[str(record["source_id"])]
    mappings = source.get("fields", {})
    attributes = record.get("attributes", {})
    if not isinstance(mappings, dict) or not isinstance(attributes, dict):
        raise ValueError(f"invalid mapping or attributes for {record['concept_id']}")
    result: dict[str, Any] = {}
    for input_name, value in attributes.items():
        property_name = mappings.get(input_name)
        if not isinstance(property_name, str):
            raise ValueError(
                f"record {record['concept_id']} contains unmapped attribute {input_name!r}"
            )
        result[property_name] = value
    return dict(sorted(result.items()))


def snapshot_tree_sha256(bundle: Path) -> str:
    """Hash the logical snapshot deterministically across Git EOL configurations."""

    members = []
    for path in sorted(item for item in bundle.rglob("*") if item.is_file()):
        content = path.read_bytes()
        if b"\x00" not in content:
            content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        members.append(
            {
                "path": path.relative_to(bundle).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return hashlib.sha256(canonical_json(members).encode("utf-8")).hexdigest()


def bundle_artifact_paths(bundle: Path) -> list[str]:
    """List every file that a grounded answer may cite from the pinned snapshot."""

    return sorted(
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file()
    )


def accepted_evidence_sets(
    category: str,
    query_layer: str,
    operation: str,
    semantics: dict[str, Any],
) -> list[list[str]]:
    """Return alternative minimal artifact sets that are sufficient for one query."""

    ledger = ["semantic/records.jsonl"]
    data = ["semantic/data.ttl"]
    data_with_provenance = ["semantic/data.ttl", "semantic/provenance.ttl"]

    if category == "provenance-lineage":
        return [ledger, data_with_provenance]
    if category in {
        "typed-fact",
        "relation-traversal",
        "multi-hop-join",
        "typed-filter",
        "aggregation",
    }:
        return [ledger, data]
    if query_layer == "ontology":
        return [["semantic/semantic-plan.json"], ["semantic/ontology.ttl"]]
    if query_layer == "shapes":
        return [["semantic/shapes.ttl"]]
    if query_layer == "validation":
        if operation == "validate":
            return [
                ["semantic/build-report.json"],
                ["semantic/validation-report.ttl"],
            ]
        return [["semantic/build-report.json"]]
    if query_layer in {"data", "ledger+data"}:
        return [ledger, data]
    if query_layer in {"ledger", "ledger+provenance"}:
        return [ledger]
    if query_layer == "manifest":
        entity = semantics.get("entity")
        if entity == "normalized-record":
            return [
                ["semantic/build-report.json"],
                ledger,
                ["semantic/source-manifest.json"],
            ]
        if entity == "logical-source":
            return [["semantic/source-manifest.json"]]
        return [["semantic/build-report.json"]]
    raise ValueError(
        f"no accepted evidence strategy for {category}/{query_layer}/{operation}"
    )


def exact_answer_assertion(question_id: str, expected_answer: Any) -> LiteralString:
    """Build a deterministic hash assertion without embedding the canonical answer."""

    expected_sha256 = json.dumps(result_sha256(expected_answer))
    identifier = json.dumps(question_id, ensure_ascii=False)
    return LiteralString(
        "const stable = (value) => {\n"
        "  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;\n"
        "  if (value && typeof value === 'object') {\n"
        "    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(',')}}`;\n"
        "  }\n"
        "  if (typeof value === 'string' && /^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:\\d{2})$/.test(value)) {\n"
        "    const parsed = new Date(value);\n"
        "    if (!Number.isNaN(parsed.valueOf())) return JSON.stringify(parsed.toISOString());\n"
        "  }\n"
        "  return JSON.stringify(value);\n"
        "};\n"
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        "  const crypto = process.getBuiltinModule('node:crypto');\n"
        "  const digest = crypto.createHash('sha256').update(stable(actual.answer)).digest('hex');\n"
        f"  return actual.question_id === {identifier}\n"
        f"    && digest === {expected_sha256};\n"
        "} catch {\n"
        "  return false;\n"
        "}\n"
    )


def exact_evidence_assertion(
    question_id: str, expected_evidence_sets: list[list[str]]
) -> LiteralString:
    """Require one sufficient evidence subset, or an empty list for abstentions."""

    expected = json.dumps(expected_evidence_sets, ensure_ascii=False, separators=(",", ":"))
    identifier = json.dumps(question_id, ensure_ascii=False)
    return LiteralString(
        "const normalizePath = (value) => value.replaceAll('\\\\', '/').replace(/^\\.\\//, '').replace(/^knowledge\\//, '');\n"
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        f"  if (actual.question_id !== {identifier}) return false;\n"
        "  if (actual.answer === null) return actual.evidence.length === 0;\n"
        "  const evidence = actual.evidence.map(normalizePath);\n"
        f"  const accepted = {expected};\n"
        "  return actual.evidence.length > 0\n"
        "    && new Set(evidence).size === evidence.length\n"
        "    && JSON.stringify([...evidence].sort()) === JSON.stringify(evidence)\n"
        "    && accepted.some((required) => required.every((item) => evidence.includes(item)));\n"
        "} catch {\n"
        "  return false;\n"
        "}\n"
    )


def evidence_path_assertion(known_paths: list[str]) -> LiteralString:
    """Reject evidence paths that do not identify files in the pinned snapshot."""

    known = json.dumps(sorted(known_paths), ensure_ascii=False, separators=(",", ":"))
    return LiteralString(
        "const normalizePath = (value) => value.replaceAll('\\\\', '/').replace(/^\\.\\//, '').replace(/^knowledge\\//, '');\n"
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        f"  const known = new Set({known});\n"
        "  return actual.evidence.every((item) => known.has(normalizePath(item)));\n"
        "} catch {\n"
        "  return false;\n"
        "}\n"
    )


def question_prompt(question_id: str, question: str) -> LiteralString:
    """Create one isolated prompt with a strict machine-gradeable response contract."""

    return LiteralString(
        "Answer one isolated semantic knowledge question. The authoritative Semantic OKF "
        "snapshot is available only when your declared capabilities provide it at `knowledge/`. "
        "Use only that snapshot; do not use the web, prior knowledge, or guesses.\n\n"
        "For joins, filters, missingness, and aggregates, inspect the complete authoritative "
        "artifact, do not stop at the first match, and verify the result before answering. "
        "Use every requested JSON key exactly as written; never rename or prefix keys.\n\n"
        f"Question: {question}\n\n"
        "Return JSON only with exactly these keys in this order: "
        f'{{"question_id":"{question_id}","answer":<JSON value>,"evidence":[<one or more '
        "artifact paths>]}. Return a sufficient evidence set, prefer the smallest useful set, "
        "and cite only files that exist in the snapshot. Paths may be relative to the bundle "
        "root (`semantic/...` or `concepts/...`) or the workspace (`knowledge/...`). Do not "
        "duplicate paths; sort evidence and every set-valued answer array lexicographically. "
        "Preserve JSON booleans, numbers, arrays, and objects. If the "
        "snapshot is unavailable, return null for `answer` and an empty evidence array."
    )


def _build_initial_questions(bundle: Path) -> list[dict[str, Any]]:
    """Reproduce the superseded lookup-heavy draft for migration diagnostics."""

    records = load_records(bundle)
    plan = load_json(bundle / "semantic" / "semantic-plan.json")
    source_manifest = load_json(bundle / "semantic" / "source-manifest.json")
    source_specs = {
        str(source["id"]): source
        for source in plan.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
    by_subject = {str(record["subject_iri"]): record for record in records}
    projects = [record for record in records if local_name(str(record["ontology_class_iri"])) == "Project"]
    documents = [record for record in records if local_name(str(record["ontology_class_iri"])) == "Document"]
    vocabulary = [
        record
        for record in records
        if local_name(str(record["ontology_class_iri"])) == "VocabularyResource"
    ]
    people = [record for record in records if local_name(str(record["ontology_class_iri"])) == "Person"]
    questions: list[dict[str, Any]] = []

    def add(
        category: str,
        question: str,
        answer: Any,
        evidence: list[str],
        *,
        difficulty: str,
        query_layer: str,
    ) -> None:
        number = len(questions) + 1
        question_id = f"q{number:03d}-{category}"
        questions.append(
            {
                "id": question_id,
                "category": category,
                "difficulty": difficulty,
                "query_layer": query_layer,
                "question": question,
                "prompt": str(question_prompt(question_id, question)),
                "expected_answer": answer,
                "canonical_evidence": evidence,
            }
        )

    for record in records:
        add(
            "title-lookup",
            f"What is the exact title of normalized record ID `{record['record_id']}`?",
            record["title"],
            [str(record["concept_id"])],
            difficulty="direct",
            query_layer="ledger",
        )

    for record in records:
        add(
            "provenance-lookup",
            f"For concept `{record['concept_id']}`, return source_id, source_kind, and source_path.",
            {
                "source_id": record["source_id"],
                "source_kind": record["source_kind"],
                "source_path": record["source_path"],
            },
            [str(record["concept_id"]), "semantic/provenance.ttl"],
            difficulty="provenance",
            query_layer="ledger+provenance",
        )

    for record in records:
        add(
            "typed-facts",
            (
                f"For RDF subject `{record['subject_iri']}`, return an object with `ontology_class` "
                "as the class local name and `semantic_properties` as the complete reviewed mapped-property object."
            ),
            {
                "ontology_class": local_name(str(record["ontology_class_iri"])),
                "semantic_properties": semantic_properties(record, source_specs),
            },
            [str(record["concept_id"]), "semantic/data.ttl"],
            difficulty="typed",
            query_layer="ledger+data",
        )

    for project in sorted(projects, key=lambda item: str(item["record_id"])):
        owner_iri = semantic_properties(project, source_specs)["owner"]
        owner = by_subject[str(owner_iri)]
        add(
            "project-owner",
            (
                f"Which accepted person owns project record `{project['record_id']}`? "
                "Return owner_subject_iri and owner_name."
            ),
            {"owner_name": owner["title"], "owner_subject_iri": owner["subject_iri"]},
            [str(project["concept_id"]), str(owner["concept_id"])],
            difficulty="relational",
            query_layer="data",
        )

    for project in sorted(projects, key=lambda item: str(item["record_id"])):
        project_properties = semantic_properties(project, source_specs)
        owner = by_subject[str(project_properties["owner"])]
        owner_properties = semantic_properties(owner, source_specs)
        add(
            "owner-role-join",
            (
                f"Join project record `{project['record_id']}` to its accepted owner and return "
                "project_status, owner_name, and owner_role."
            ),
            {
                "owner_name": owner["title"],
                "owner_role": owner_properties["role"],
                "project_status": project_properties["status"],
            },
            [str(project["concept_id"]), str(owner["concept_id"]), "semantic/data.ttl"],
            difficulty="multi-hop",
            query_layer="data",
        )

    for document in sorted(documents, key=lambda item: str(item["title"])):
        properties = semantic_properties(document, source_specs)
        add(
            "document-semantics",
            (
                f"For the document titled `{document['title']}`, return category, published date, "
                "and integer priority."
            ),
            {
                "category": properties["category"],
                "priority": properties["priority"],
                "published": properties["published"],
            },
            [str(document["concept_id"])],
            difficulty="typed",
            query_layer="data",
        )

    for term in sorted(vocabulary, key=lambda item: str(item["title"])):
        properties = semantic_properties(term, source_specs)
        add(
            "vocabulary-semantics",
            (
                f"Which vocabulary resource has notation `{properties['notation']}`? "
                "Return subject_iri and prefLabel."
            ),
            {"prefLabel": properties["prefLabel"], "subject_iri": term["subject_iri"]},
            [str(term["concept_id"])],
            difficulty="inverse-lookup",
            query_layer="data",
        )

    source_rows = source_manifest.get("sources", [])
    for source in sorted(source_rows, key=lambda item: str(item["id"])):
        source_id = str(source["id"])
        source_records = sorted(
            str(record["record_id"]) for record in records if record["source_id"] == source_id
        )
        add(
            "source-cardinality",
            (
                f"For logical source `{source_id}`, return record_count and the complete sorted "
                "record_ids array."
            ),
            {"record_count": len(source_records), "record_ids": source_records},
            ["semantic/source-manifest.json", "semantic/records.jsonl"],
            difficulty="aggregation",
            query_layer="ledger",
        )

    class_counts = Counter(local_name(str(record["ontology_class_iri"])) for record in records)
    status_counts = Counter(
        semantic_properties(record, source_specs)["status"] for record in projects
    )
    role_counts = Counter(semantic_properties(record, source_specs)["role"] for record in people)
    priority_counts = Counter(
        semantic_properties(record, source_specs)["priority"] for record in documents
    )
    aggregate_specs: list[tuple[str, Any]] = [
        ("How many accepted normalized records are in the snapshot?", len(records)),
        ("How many distinct logical source IDs are represented?", len(source_rows)),
        ("How many accepted Document instances are present?", class_counts["Document"]),
        ("How many accepted Person instances are present?", class_counts["Person"]),
        ("How many accepted Project instances are present?", class_counts["Project"]),
        (
            "How many accepted VocabularyResource instances are present?",
            class_counts["VocabularyResource"],
        ),
        (
            "How many Person instances have active equal to true?",
            sum(bool(semantic_properties(item, source_specs)["active"]) for item in people),
        ),
        (
            "How many Person instances have active equal to false?",
            sum(not bool(semantic_properties(item, source_specs)["active"]) for item in people),
        ),
        (
            "How many Project instances have featured equal to true?",
            sum(bool(semantic_properties(item, source_specs)["featured"]) for item in projects),
        ),
        (
            "How many Project instances have featured equal to false?",
            sum(not bool(semantic_properties(item, source_specs)["featured"]) for item in projects),
        ),
        ("How many projects have status `active`?", status_counts["active"]),
        ("How many projects have status `paused`?", status_counts["paused"]),
        ("How many projects have status `planned`?", status_counts["planned"]),
        ("How many documents have priority 1?", priority_counts[1]),
        ("How many documents have priority 2?", priority_counts[2]),
        (
            "How many documents were published on or after 2026-06-01?",
            sum(
                semantic_properties(item, source_specs)["published"] >= "2026-06-01"
                for item in documents
            ),
        ),
        (
            "What is the total project budget across all accepted projects? Return a JSON number.",
            sum(float(semantic_properties(item, source_specs)["budget"]) for item in projects),
        ),
        (
            "What is the average of all non-null person scores, rounded to three decimal places?",
            round(
                sum(
                    float(score)
                    for item in people
                    if (score := semantic_properties(item, source_specs)["score"]) is not None
                )
                / sum(
                    semantic_properties(item, source_specs)["score"] is not None
                    for item in people
                ),
                3,
            ),
        ),
        ("How many people have role `Engineer`?", role_counts["Engineer"]),
        ("How many people have role `Reviewer`?", role_counts["Reviewer"]),
    ]
    for question, answer in aggregate_specs:
        add(
            "aggregate-reasoning",
            question,
            answer,
            ["semantic/records.jsonl", "semantic/data.ttl"],
            difficulty="aggregation",
            query_layer="ledger+data",
        )

    return questions


def validate_questions(questions: list[dict[str, Any]]) -> None:
    """Enforce the closed-set benchmark counts and uniqueness invariants."""

    if len(questions) != QUESTION_COUNT:
        raise ValueError(f"expected {QUESTION_COUNT} questions, found {len(questions)}")
    ids = [str(question["id"]) for question in questions]
    texts = [str(question["question"]) for question in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("question IDs are not unique")
    if len(texts) != len(set(texts)):
        raise ValueError("question texts are not unique")
    signatures = [str(question["semantic_signature"]) for question in questions]
    if len(signatures) != len(set(signatures)):
        raise ValueError("semantic signatures are not unique")
    descriptors = [question["semantic_descriptor"] for question in questions]
    if len({canonical_json(item) for item in descriptors}) != len(descriptors):
        raise ValueError("semantic descriptors are not unique")
    for question, descriptor in zip(questions, descriptors, strict=True):
        if "question" in canonical_json(descriptor):
            raise ValueError(f"semantic descriptor depends on wording: {question['id']}")
        if semantic_signature(descriptor) != question["semantic_signature"]:
            raise ValueError(f"semantic signature drift: {question['id']}")
    observed = dict(sorted(Counter(str(item["category"]) for item in questions).items()))
    if observed != dict(sorted(CATEGORY_COUNTS.items())):
        raise ValueError(f"category counts differ: {observed}")
    difficulty_counts = Counter(str(item["difficulty"]) for item in questions)
    if difficulty_counts != Counter({"easy": 80, "medium": 120, "hard": 100}):
        raise ValueError(f"difficulty counts differ: {dict(difficulty_counts)}")
    for question in questions:
        if not question["accepted_evidence_sets"]:
            raise ValueError(f"question {question['id']} has no canonical evidence")


def build_questions(bundle: Path) -> list[dict[str, Any]]:
    """Build a balanced semantic battery with joins, filters, contracts, and negatives."""

    records = load_records(bundle)
    plan = load_json(bundle / "semantic" / "semantic-plan.json")
    source_manifest = load_json(bundle / "semantic" / "source-manifest.json")
    build_report = load_json(bundle / "semantic" / "build-report.json")
    source_specs = {
        str(source["id"]): source
        for source in plan.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
    source_rows = [item for item in source_manifest.get("sources", []) if isinstance(item, dict)]
    source_summary = {str(item["id"]): item for item in source_rows}
    by_subject = {str(record["subject_iri"]): record for record in records}
    by_source: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_source.setdefault(str(record["source_id"]), []).append(record)
    for values in by_source.values():
        values.sort(key=lambda item: str(item["subject_iri"]))
    documents = sorted(
        (item for item in records if local_name(str(item["ontology_class_iri"])) == "Document"),
        key=lambda item: str(item["subject_iri"]),
    )
    people = sorted(
        (item for item in records if local_name(str(item["ontology_class_iri"])) == "Person"),
        key=lambda item: str(item["subject_iri"]),
    )
    projects = sorted(
        (item for item in records if local_name(str(item["ontology_class_iri"])) == "Project"),
        key=lambda item: str(item["subject_iri"]),
    )
    vocabulary = sorted(
        (
            item
            for item in records
            if local_name(str(item["ontology_class_iri"])) == "VocabularyResource"
        ),
        key=lambda item: str(item["subject_iri"]),
    )
    properties_for = {
        str(item["subject_iri"]): semantic_properties(item, source_specs) for item in records
    }
    project_by_owner = {
        str(properties_for[str(project["subject_iri"])]["owner"]): project for project in projects
    }
    questions: list[dict[str, Any]] = []

    def answer_kind(value: Any) -> str:
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "number"
        if isinstance(value, list):
            return "set"
        if isinstance(value, dict):
            return "tuple"
        return "scalar"

    def add(
        category: str,
        question: str,
        answer: Any,
        review_locators: list[str],
        *,
        difficulty: str,
        query_layer: str,
        operation: str,
        graph_scope: list[str],
        semantics: dict[str, Any],
        concept_evidence: bool = False,
    ) -> None:
        if isinstance(answer, dict):
            exact_keys = ", ".join(f"`{key}`" for key in sorted(answer))
            question = (
                f"{question} Return a JSON object with exactly these keys: {exact_keys}."
            )
        number = len(questions) + 1
        question_id = f"q{number:03d}-{category}"
        signature_payload = {
            "graph_scope": graph_scope,
            "operation": operation,
            "semantics": semantics,
        }
        signature = semantic_signature(signature_payload)
        result_sha = result_sha256(answer)
        evidence_sets = accepted_evidence_sets(category, query_layer, operation, semantics)
        if concept_evidence:
            concept_set = sorted(
                f"{locator}.md"
                for locator in review_locators
                if locator.startswith("concepts/")
            )
            if concept_set and concept_set not in evidence_sets:
                evidence_sets.append(concept_set)
        evidence_sha256 = sorted(result_sha256(sorted(items)) for items in evidence_sets)
        for locator in review_locators:
            artifact = bundle / (f"{locator}.md" if locator.startswith("concepts/") else locator)
            if not artifact.is_file():
                raise ValueError(f"missing review locator for {question_id}: {locator}")
        questions.append(
            {
                "id": question_id,
                "category": category,
                "difficulty": difficulty,
                "query_layer": query_layer,
                "question": question,
                "prompt": str(question_prompt(question_id, question)),
                "expected_answer": answer,
                "accepted_evidence_sets": evidence_sets,
                "accepted_evidence_sha256": evidence_sha256,
                "semantic_descriptor": signature_payload,
                "semantic_signature": signature,
                "oracle": {
                    "graph_scope": graph_scope,
                    "entailment": "none",
                    "operation": operation,
                },
                "expected": {
                    "kind": answer_kind(answer),
                    "value": answer,
                    "cardinality": len(answer) if isinstance(answer, list) else 1,
                    "ordering": "subject-iri-ascending" if isinstance(answer, list) else "none",
                },
                "result_sha256": result_sha,
            }
        )

    # TYP: exact typed tuples across all four ontology classes.
    for document in documents:
        props = properties_for[str(document["subject_iri"])]
        add(
            "typed-fact",
            f"For document `{document['title']}`, return priority and published.",
            {"priority": props["priority"], "published": props["published"]},
            [str(document["concept_id"]), "semantic/data.ttl"],
            difficulty="easy",
            query_layer="data",
            operation="select",
            graph_scope=["data"],
            semantics={
                "entity": document["subject_iri"],
                "projection": ["priority", "published"],
            },
        )
    active_people = [item for item in people if properties_for[str(item["subject_iri"])]["active"]]
    for person in active_people:
        props = properties_for[str(person["subject_iri"])]
        add(
            "typed-fact",
            f"For active person subject `{person['subject_iri']}`, return active, score, and joinedOn.",
            {"active": props["active"], "joinedOn": props["joinedOn"], "score": props["score"]},
            [str(person["concept_id"]), "semantic/data.ttl"],
            difficulty="easy",
            query_layer="data",
            operation="select",
            graph_scope=["data"],
            semantics={
                "entity": person["subject_iri"],
                "projection": ["active", "joinedOn", "score"],
            },
            concept_evidence=True,
        )
    featured_projects = [
        item for item in projects if properties_for[str(item["subject_iri"])]["featured"]
    ]
    for project in featured_projects:
        props = properties_for[str(project["subject_iri"])]
        add(
            "typed-fact",
            (
                f"For featured project subject `{project['subject_iri']}`, return featured, budget, "
                "startDate, and updatedAt."
            ),
            {
                "budget": props["budget"],
                "featured": props["featured"],
                "startDate": props["startDate"],
                "updatedAt": props["updatedAt"],
            },
            [str(project["concept_id"]), "semantic/data.ttl"],
            difficulty="easy",
            query_layer="data",
            operation="select",
            graph_scope=["data"],
            semantics={
                "entity": project["subject_iri"],
                "projection": ["budget", "featured", "startDate", "updatedAt"],
            },
            concept_evidence=True,
        )
    for term in vocabulary:
        props = properties_for[str(term["subject_iri"])]
        add(
            "typed-fact",
            f"What notation is asserted for vocabulary subject `{term['subject_iri']}`?",
            props["notation"],
            [str(term["concept_id"]), "semantic/data.ttl"],
            difficulty="easy",
            query_layer="data",
            operation="select",
            graph_scope=["data"],
            semantics={"entity": term["subject_iri"], "projection": ["notation"]},
            concept_evidence=True,
        )

    # REL: traverse the owner relation in both directions.
    for project in projects:
        owner_iri = str(properties_for[str(project["subject_iri"])]["owner"])
        add(
            "relation-traversal",
            f"Which person subject IRI owns project subject `{project['subject_iri']}`?",
            owner_iri,
            [str(project["concept_id"]), str(by_subject[owner_iri]["concept_id"])],
            difficulty="easy",
            query_layer="data",
            operation="select",
            graph_scope=["data"],
            semantics={
                "entity": project["subject_iri"],
                "path": ["owner"],
                "projection": ["subject_iri"],
            },
            concept_evidence=True,
        )
    for person in people:
        project = project_by_owner[str(person["subject_iri"])]
        add(
            "relation-traversal",
            f"Which project subject IRI is owned by person subject `{person['subject_iri']}`?",
            project["subject_iri"],
            [str(person["concept_id"]), str(project["concept_id"])],
            difficulty="easy",
            query_layer="data",
            operation="select",
            graph_scope=["data"],
            semantics={
                "entity": person["subject_iri"],
                "inverse_path": ["owner"],
                "projection": ["subject_iri"],
            },
            concept_evidence=True,
        )

    # JOIN: two-hop projections in both directions plus featured-owner details.
    for project in projects:
        owner = by_subject[str(properties_for[str(project["subject_iri"])]["owner"])]
        owner_props = properties_for[str(owner["subject_iri"])]
        add(
            "multi-hop-join",
            f"For project `{project['title']}`, return the owner's role and active state.",
            {"active": owner_props["active"], "role": owner_props["role"]},
            [str(project["concept_id"]), str(owner["concept_id"]), "semantic/data.ttl"],
            difficulty="medium",
            query_layer="data",
            operation="join",
            graph_scope=["data"],
            semantics={
                "entity": project["subject_iri"],
                "path": ["owner"],
                "projection": ["active", "role"],
            },
            concept_evidence=True,
        )
    for person in people:
        project = project_by_owner[str(person["subject_iri"])]
        project_props = properties_for[str(project["subject_iri"])]
        add(
            "multi-hop-join",
            f"For person `{person['title']}`, return the owned project's status and budget.",
            {"budget": project_props["budget"], "status": project_props["status"]},
            [str(person["concept_id"]), str(project["concept_id"]), "semantic/data.ttl"],
            difficulty="medium",
            query_layer="data",
            operation="join",
            graph_scope=["data"],
            semantics={
                "entity": person["subject_iri"],
                "inverse_path": ["owner"],
                "projection": ["budget", "status"],
            },
            concept_evidence=True,
        )
    for project in featured_projects:
        owner = by_subject[str(properties_for[str(project["subject_iri"])]["owner"])]
        owner_props = properties_for[str(owner["subject_iri"])]
        add(
            "multi-hop-join",
            f"For featured project `{project['title']}`, return the owner's score and joinedOn.",
            {"joinedOn": owner_props["joinedOn"], "score": owner_props["score"]},
            [str(project["concept_id"]), str(owner["concept_id"]), "semantic/data.ttl"],
            difficulty="medium",
            query_layer="data",
            operation="join",
            graph_scope=["data"],
            semantics={
                "entity": project["subject_iri"],
                "path": ["owner"],
                "projection": ["joinedOn", "score"],
            },
            concept_evidence=True,
        )

    # FIL: complete typed result sets, including cross-entity filters.
    roles = sorted({str(properties_for[str(item["subject_iri"])]["role"]) for item in people})
    for role in roles:
        matches = sorted(
            str(item["subject_iri"])
            for item in people
            if properties_for[str(item["subject_iri"])]["role"] == role
        )
        add(
            "typed-filter",
            f"Return the complete sorted subject-IRI array for people with role `{role}`.",
            matches,
            ["semantic/data.ttl"],
            difficulty="medium",
            query_layer="data",
            operation="filter",
            graph_scope=["data"],
            semantics={
                "class": "Person",
                "filters": {"role": role},
                "projection": ["subject_iri"],
            },
        )
    statuses = sorted({str(properties_for[str(item["subject_iri"])]["status"]) for item in projects})
    for status in statuses:
        for featured in (False, True):
            matches = sorted(
                str(item["subject_iri"])
                for item in projects
                if properties_for[str(item["subject_iri"])]["status"] == status
                and properties_for[str(item["subject_iri"])]["featured"] is featured
            )
            if not matches:
                raise ValueError(f"empty status/featured filter: {status}/{featured}")
            add(
                "typed-filter",
                (
                    f"Return the complete sorted project subject-IRI array for status `{status}` "
                    f"and featured equal to `{str(featured).lower()}`."
                ),
                matches,
                ["semantic/data.ttl"],
                difficulty="medium",
                query_layer="data",
                operation="filter",
                graph_scope=["data"],
                semantics={
                    "class": "Project",
                    "filters": {"featured": featured, "status": status},
                    "projection": ["subject_iri"],
                },
            )
    for month in range(1, 11):
        prefix = f"2026-{month:02d}-"
        matches = sorted(
            str(item["subject_iri"])
            for item in projects
            if properties_for[str(item["subject_iri"])]["featured"]
            and str(properties_for[str(item["subject_iri"])]["startDate"]).startswith(prefix)
        )
        add(
            "typed-filter",
            (
                f"Return featured project subject IRIs with a startDate in 2026-{month:02d}, "
                "sorted ascending."
            ),
            matches,
            ["semantic/data.ttl"],
            difficulty="medium",
            query_layer="data",
            operation="filter",
            graph_scope=["data"],
            semantics={
                "class": "Project",
                "filters": {"featured": True, "startDate_prefix": prefix},
                "projection": ["subject_iri"],
            },
        )
    for priority in range(1, 6):
        matches = sorted(
            str(item["subject_iri"])
            for item in documents
            if properties_for[str(item["subject_iri"])]["priority"] == priority
        )
        add(
            "typed-filter",
            f"Return all document subject IRIs with integer priority {priority}, sorted ascending.",
            matches,
            ["semantic/data.ttl"],
            difficulty="medium",
            query_layer="data",
            operation="filter",
            graph_scope=["data"],
            semantics={
                "class": "Document",
                "filters": {"priority": priority},
                "projection": ["subject_iri"],
            },
        )
    cross_conditions = [
        (True, "Engineer", "planned"),
        (False, "Engineer", "active"),
        (False, "Reviewer", "paused"),
        (True, "Reviewer", "active"),
        (True, "Analyst", "paused"),
        (False, "Analyst", "planned"),
        (False, "Architect", "active"),
        (True, "Architect", "planned"),
        (True, "Operator", "active"),
        (False, "Operator", "paused"),
    ]
    for active, role, status in cross_conditions:
        matches = []
        for project in projects:
            project_props = properties_for[str(project["subject_iri"])]
            owner = by_subject[str(project_props["owner"])]
            owner_props = properties_for[str(owner["subject_iri"])]
            if owner_props["active"] is active and owner_props["role"] == role and project_props["status"] == status:
                matches.append(str(project["subject_iri"]))
        matches.sort()
        if not matches:
            raise ValueError(f"empty cross-entity filter: {active}/{role}/{status}")
        add(
            "typed-filter",
            (
                f"Return sorted project subject IRIs whose owner has active `{str(active).lower()}` "
                f"and role `{role}`, and whose project status is `{status}`."
            ),
            matches,
            ["semantic/data.ttl"],
            difficulty="medium",
            query_layer="data",
            operation="join-filter",
            graph_scope=["data"],
            semantics={
                "class": "Project",
                "filters": {
                    "owner.active": active,
                    "owner.role": role,
                    "status": status,
                },
                "projection": ["subject_iri"],
            },
        )

    # AGG: grouping, per-source arithmetic, missing-aware averages, and global metrics.
    aggregate_index = 0

    def add_aggregate(question: str, answer: Any, semantics: dict[str, Any]) -> None:
        nonlocal aggregate_index
        aggregate_index += 1
        add(
            "aggregation",
            question,
            answer,
            ["semantic/records.jsonl", "semantic/data.ttl"],
            difficulty="medium" if aggregate_index <= 30 else "hard",
            query_layer="ledger+data",
            operation="aggregate",
            graph_scope=["data"],
            semantics=semantics,
        )

    for role in roles:
        add_aggregate(
            (
                f"How many accepted people have role `{role}`? Count every accepted Person "
                "record with that role, including inactive people and people whose score is "
                "null; do not apply any other filter."
            ),
            sum(properties_for[str(item["subject_iri"])]["role"] == role for item in people),
            {
                "aggregate": "count",
                "class": "Person",
                "filters": {"role": role},
            },
        )
    for status in statuses:
        for featured in (False, True):
            add_aggregate(
                (
                    f"How many projects have status `{status}` and featured equal to "
                    f"`{str(featured).lower()}`?"
                ),
                sum(
                    properties_for[str(item["subject_iri"])]["status"] == status
                    and properties_for[str(item["subject_iri"])]["featured"] is featured
                    for item in projects
                ),
                {
                    "aggregate": "count",
                    "class": "Project",
                    "filters": {"featured": featured, "status": status},
                },
            )
    project_source_ids = sorted(item for item in by_source if item.startswith("projects-"))
    for source_id in project_source_ids:
        add_aggregate(
            f"What is the exact sum of project budgets in logical source `{source_id}`?",
            sum(float(properties_for[str(item["subject_iri"])]["budget"]) for item in by_source[source_id]),
            {
                "aggregate": "sum",
                "class": "Project",
                "field": "budget",
                "filters": {"source_id": source_id},
            },
        )
    people_source_ids = sorted(item for item in by_source if item.startswith("people-"))
    for source_id in people_source_ids:
        scores = [
            properties_for[str(item["subject_iri"])]["score"]
            for item in by_source[source_id]
            if properties_for[str(item["subject_iri"])]["score"] is not None
        ]
        add_aggregate(
            (
                f"What is the average recorded person score in logical source `{source_id}`? "
                "Ignore missing scores and round to three decimal places."
            ),
            round(sum(float(value) for value in scores) / len(scores), 3),
            {
                "aggregate": "average",
                "class": "Person",
                "field": "score",
                "filters": {"source_id": source_id},
                "missing": "ignore",
                "round": 3,
            },
        )
    for priority in range(1, 6):
        add_aggregate(
            f"How many documents have integer priority {priority}?",
            sum(properties_for[str(item["subject_iri"])]["priority"] == priority for item in documents),
            {
                "aggregate": "count",
                "class": "Document",
                "filters": {"priority": priority},
            },
        )
    budgets = [float(properties_for[str(item["subject_iri"])]["budget"]) for item in projects]
    add_aggregate(
        "What is the total budget across all accepted projects?",
        sum(budgets),
        {"aggregate": "sum", "class": "Project", "field": "budget"},
    )
    add_aggregate(
        "What is the average budget across all accepted projects?",
        sum(budgets) / len(budgets),
        {"aggregate": "average", "class": "Project", "field": "budget"},
    )
    add_aggregate(
        "What is the total budget of featured projects?",
        sum(
            float(properties_for[str(item["subject_iri"])]["budget"])
            for item in projects
            if properties_for[str(item["subject_iri"])]["featured"]
        ),
        {
            "aggregate": "sum",
            "class": "Project",
            "field": "budget",
            "filters": {"featured": True},
        },
    )
    add_aggregate(
        "What is the total budget of nonfeatured projects?",
        sum(
            float(properties_for[str(item["subject_iri"])]["budget"])
            for item in projects
            if not properties_for[str(item["subject_iri"])]["featured"]
        ),
        {
            "aggregate": "sum",
            "class": "Project",
            "field": "budget",
            "filters": {"featured": False},
        },
    )
    add_aggregate(
        "How many distinct project status values are asserted?",
        len(statuses),
        {"aggregate": "count-distinct", "class": "Project", "field": "status"},
    )

    # PROV: direct lineage, source membership, and cross-entity lineage joins.
    for record in documents:
        add(
            "provenance-lineage",
            f"For document subject `{record['subject_iri']}`, return source_id and physical source_path.",
            {"source_id": record["source_id"], "source_path": record["source_path"]},
            [str(record["concept_id"]), "semantic/provenance.ttl"],
            difficulty="hard",
            query_layer="data+provenance",
            operation="provenance-select",
            graph_scope=["data", "provenance"],
            semantics={
                "entity": record["subject_iri"],
                "projection": ["source_id", "source_path"],
            },
            concept_evidence=True,
        )
    for record in vocabulary:
        add(
            "provenance-lineage",
            (
                f"For vocabulary subject `{record['subject_iri']}`, return source_id and physical "
                "source_path."
            ),
            {"source_id": record["source_id"], "source_path": record["source_path"]},
            [str(record["concept_id"]), "semantic/provenance.ttl"],
            difficulty="hard",
            query_layer="data+provenance",
            operation="provenance-select",
            graph_scope=["data", "provenance"],
            semantics={
                "entity": record["subject_iri"],
                "projection": ["source_id", "source_path"],
            },
            concept_evidence=True,
        )
    for source_id in project_source_ids:
        members = by_source[source_id]
        add(
            "provenance-lineage",
            (
                f"For project source `{source_id}`, return physical source_path and all derived "
                "project subject IRIs sorted ascending."
            ),
            {
                "source_path": str(members[0]["source_path"]),
                "subjects": sorted(str(item["subject_iri"]) for item in members),
            },
            ["semantic/source-manifest.json", "semantic/provenance.ttl"],
            difficulty="hard",
            query_layer="ledger+provenance",
            operation="provenance-group",
            graph_scope=["provenance"],
            semantics={
                "filters": {"source_id": source_id},
                "projection": ["source_path", "subjects"],
            },
        )
    for project in featured_projects:
        owner = by_subject[str(properties_for[str(project["subject_iri"])]["owner"])]
        add(
            "provenance-lineage",
            (
                f"For featured project `{project['title']}`, return project_source_id, "
                "project_source_path, owner_source_id, and owner_source_path."
            ),
            {
                "owner_source_id": owner["source_id"],
                "owner_source_path": owner["source_path"],
                "project_source_id": project["source_id"],
                "project_source_path": project["source_path"],
            },
            [str(project["concept_id"]), str(owner["concept_id"]), "semantic/provenance.ttl"],
            difficulty="hard",
            query_layer="data+provenance",
            operation="provenance-join",
            graph_scope=["data", "provenance"],
            semantics={
                "entity": project["subject_iri"],
                "path": ["owner"],
                "projection": [
                    "owner.source_id",
                    "owner.source_path",
                    "project.source_id",
                    "project.source_path",
                ],
            },
            concept_evidence=True,
        )

    # SCH: reviewed ontology signatures plus the generated SHACL acceptance contract.
    ontology = plan["ontology"]
    for class_spec in sorted(ontology["classes"], key=lambda item: str(item["name"])):
        add(
            "ontology-shacl",
            f"What label is declared for ontology class `{class_spec['name']}`?",
            class_spec["label"],
            ["semantic/ontology.ttl", "semantic/semantic-plan.json"],
            difficulty="hard",
            query_layer="ontology",
            operation="schema-select",
            graph_scope=["ontology"],
            semantics={
                "entity": {"class": class_spec["name"]},
                "projection": ["label"],
            },
        )
    property_by_name = {str(item["name"]): item for item in ontology["properties"]}
    signature_properties = [
        "published",
        "priority",
        "joinedOn",
        "active",
        "score",
        "status",
        "budget",
        "featured",
        "updatedAt",
        "owner",
    ]
    for name in signature_properties:
        spec = property_by_name[name]
        add(
            "ontology-shacl",
            f"Return kind, domain, and range for ontology property `{name}`.",
            {"domain": spec["domain"], "kind": spec["kind"], "range": spec["range"]},
            ["semantic/ontology.ttl", "semantic/semantic-plan.json"],
            difficulty="hard",
            query_layer="ontology",
            operation="schema-select",
            graph_scope=["ontology"],
            semantics={
                "entity": {"property": name},
                "projection": ["domain", "kind", "range"],
            },
        )
    rules_by_name = {str(item["name"]): item for item in plan["rules"]}
    rule_names = [
        "DocumentCategoryRule",
        "PersonRoleRule",
        "ProjectOwnerRule",
        "ProjectStatusRule",
        "VocabularyLabelRule",
    ]
    for name in rule_names:
        rule = rules_by_name[name]
        summary = {
            key: rule[key]
            for key in (
                "target_class",
                "path",
                "min_count",
                "max_count",
                "datatype",
                "class",
                "node_kind",
                "pattern",
            )
            if key in rule
        }
        summary["basis_kind"] = rule["basis"]["kind"]
        add(
            "ontology-shacl",
            f"Return the complete generated constraint summary for SHACL shape `{name}Shape`.",
            summary,
            ["semantic/shapes.ttl", "semantic/semantic-plan.json"],
            difficulty="hard",
            query_layer="shapes",
            operation="shape-select",
            graph_scope=["shapes"],
            semantics={
                "entity": {"shape": f"{name}Shape"},
                "projection": sorted(summary),
            },
        )
    add(
        "ontology-shacl",
        "Return target and required_paths for the generated `SemanticMappingShape`.",
        {
            "required_paths": ["okfConceptId", "recordSha256", "sourceContentSha256", "sourceId"],
            "target": "subjects-of-okfConceptId",
        },
        ["semantic/shapes.ttl"],
        difficulty="hard",
        query_layer="shapes",
        operation="shape-select",
        graph_scope=["shapes"],
        semantics={
            "entity": {"shape": "SemanticMappingShape"},
            "projection": ["required_paths", "target"],
        },
    )

    # INT: missingness, asserted ASK results, and validation integrity.
    missing_scores = [
        item for item in people if properties_for[str(item["subject_iri"])]["score"] is None
    ]
    add(
        "integrity-negative",
        "Which person subject IRI lacks an asserted score in this snapshot?",
        missing_scores[0]["subject_iri"],
        [str(missing_scores[0]["concept_id"]), "semantic/data.ttl"],
        difficulty="hard",
        query_layer="data",
        operation="missingness",
        graph_scope=["data"],
        semantics={
            "class": "Person",
            "filters": {"missing": "score"},
            "projection": ["subject_iri"],
        },
        concept_evidence=True,
    )
    missing_specs = [
        ("people", "score", people),
        ("projects", "owner", projects),
        ("projects", "status", projects),
        ("documents", "category", documents),
    ]
    for label, property_name, members in missing_specs:
        add(
            "integrity-negative",
            (
                f"In the asserted snapshot, how many {label} lack property `{property_name}`? "
                "Do not interpret absence beyond this snapshot."
            ),
            sum(
                property_name not in properties_for[str(item["subject_iri"])]
                or properties_for[str(item["subject_iri"])][property_name] is None
                for item in members
            ),
            ["semantic/data.ttl"],
            difficulty="hard",
            query_layer="data",
            operation="missingness-count",
            graph_scope=["data"],
            semantics={
                "aggregate": "count",
                "class": label,
                "filters": {"missing": property_name},
            },
        )
    person_a = by_subject["https://example.org/forty-source/resource/people-01/person-01-a"]
    person_b = by_subject["https://example.org/forty-source/resource/people-01/person-01-b"]
    project_a = by_subject["https://example.org/forty-source/resource/projects-01/project-01-a"]
    term = by_subject["https://example.org/vocabulary/knowledge-sharing"]
    ask_specs = [
        (
            f"Is `{person_a['subject_iri']}` asserted as a Person in this snapshot?",
            True,
            {"entity": person_a["subject_iri"], "predicate": "rdf:type", "object": "Person"},
        ),
        (
            f"Is `{project_a['subject_iri']}` asserted to have owner `{person_a['subject_iri']}`?",
            True,
            {
                "entity": project_a["subject_iri"],
                "predicate": "owner",
                "object": person_a["subject_iri"],
            },
        ),
        (
            f"Does `{term['subject_iri']}` have asserted prefLabel `Knowledge sharing`?",
            True,
            {
                "entity": term["subject_iri"],
                "predicate": "prefLabel",
                "object": "Knowledge sharing",
            },
        ),
        (
            f"Does `{project_a['subject_iri']}` have asserted status `active`?",
            False,
            {"entity": project_a["subject_iri"], "predicate": "status", "object": "active"},
        ),
        (
            f"Does `{person_b['subject_iri']}` have asserted active value `true`?",
            False,
            {"entity": person_b["subject_iri"], "predicate": "active", "object": True},
        ),
    ]
    for question, answer, semantics in ask_specs:
        add(
            "integrity-negative",
            question + " Answer only for the asserted snapshot.",
            answer,
            ["semantic/data.ttl"],
            difficulty="hard",
            query_layer="data",
            operation="ask",
            graph_scope=["data"],
            semantics=semantics,
        )
    add(
        "integrity-negative",
        "Does the stored SHACL validation report conform?",
        build_report["summary"]["shacl"] == "conformant",
        ["semantic/validation-report.ttl", "semantic/build-report.json"],
        difficulty="hard",
        query_layer="validation",
        operation="validate",
        graph_scope=["validation-report"],
        semantics={
            "entity": "validation-report",
            "projection": ["conforms"],
        },
    )
    add(
        "integrity-negative",
        "How many build errors are recorded in the stored build report?",
        len(build_report["errors"]),
        ["semantic/build-report.json"],
        difficulty="hard",
        query_layer="validation",
        operation="integrity-count",
        graph_scope=["build-report"],
        semantics={
            "aggregate": "count",
            "entity": "build-report",
            "field": "errors",
        },
    )
    add(
        "integrity-negative",
        "How many build warnings are recorded in the stored build report?",
        len(build_report["warnings"]),
        ["semantic/build-report.json"],
        difficulty="hard",
        query_layer="validation",
        operation="integrity-count",
        graph_scope=["build-report"],
        semantics={
            "aggregate": "count",
            "entity": "build-report",
            "field": "warnings",
        },
    )
    add(
        "integrity-negative",
        "How many accepted ledger subjects lack a non-empty OKF concept ID?",
        sum(not item.get("concept_id") for item in records),
        ["semantic/records.jsonl"],
        difficulty="hard",
        query_layer="ledger",
        operation="integrity-count",
        graph_scope=["ledger"],
        semantics={
            "aggregate": "count",
            "entity": "accepted-ledger-subject",
            "filters": {"missing_or_empty": "concept_id"},
        },
    )
    add(
        "integrity-negative",
        "How many accepted ledger subjects lack a provenance source reference?",
        sum(not item.get("source_refs") for item in records),
        ["semantic/records.jsonl", "semantic/provenance.ttl"],
        difficulty="hard",
        query_layer="ledger+provenance",
        operation="integrity-count",
        graph_scope=["ledger", "provenance"],
        semantics={
            "aggregate": "count",
            "entity": "accepted-ledger-subject",
            "filters": {"missing_or_empty": "source_refs"},
        },
    )

    # BND: fixed bundle and logical-source boundary counts.
    source_kind_counts = Counter(str(item["kind"]) for item in source_rows)
    inventory_specs = [
        (
            "How many logical sources are declared in the snapshot?",
            len(source_rows),
            {"aggregate": "count", "entity": "logical-source"},
        ),
        (
            "How many normalized records are in the snapshot?",
            len(records),
            {"aggregate": "count", "entity": "normalized-record"},
        ),
        (
            "How many generated concepts are reported?",
            build_report["summary"]["concepts"],
            {"aggregate": "count", "entity": "generated-concept"},
        ),
        (
            "How many accepted data subjects are reported?",
            build_report["summary"]["data_subjects"],
            {"aggregate": "count", "entity": "accepted-data-subject"},
        ),
        (
            "How many Markdown logical sources are declared?",
            source_kind_counts["markdown"],
            {"aggregate": "count", "entity": "logical-source", "filters": {"kind": "markdown"}},
        ),
        (
            "How many CSV logical sources are declared?",
            source_kind_counts["csv"],
            {"aggregate": "count", "entity": "logical-source", "filters": {"kind": "csv"}},
        ),
        (
            "How many JSON logical sources are declared?",
            source_kind_counts["json"],
            {"aggregate": "count", "entity": "logical-source", "filters": {"kind": "json"}},
        ),
        (
            "How many RDF logical sources are declared?",
            source_kind_counts["rdf"],
            {"aggregate": "count", "entity": "logical-source", "filters": {"kind": "rdf"}},
        ),
        (
            "How many logical sources contain exactly one normalized record?",
            sum(int(item["record_count"]) == 1 for item in source_rows),
            {
                "aggregate": "count",
                "entity": "logical-source",
                "filters": {"record_count": 1},
            },
        ),
        (
            "How many logical sources contain exactly two normalized records?",
            sum(int(item["record_count"]) == 2 for item in source_rows),
            {
                "aggregate": "count",
                "entity": "logical-source",
                "filters": {"record_count": 2},
            },
        ),
    ]
    for question, answer, semantics in inventory_specs:
        add(
            "bundle-inventory",
            question,
            answer,
            ["semantic/source-manifest.json", "semantic/build-report.json"],
            difficulty="hard",
            query_layer="manifest",
            operation="inventory-count",
            graph_scope=["source-manifest", "build-report"],
            semantics=semantics,
        )

    validate_questions(questions)
    return questions


def shared_response_assertion() -> LiteralString:
    """Validate the response envelope independently of the hidden answer."""

    return LiteralString(
        "try {\n"
        "  const parsed = JSON.parse(output.trim());\n"
        "  const keys = Object.keys(parsed);\n"
        "  return JSON.stringify(keys) === JSON.stringify(['question_id', 'answer', 'evidence'])\n"
        "    && typeof parsed.question_id === 'string'\n"
        "    && Array.isArray(parsed.evidence)\n"
        "    && parsed.evidence.every((item) => typeof item === 'string')\n"
        "    && (parsed.answer === null ? parsed.evidence.length === 0 : parsed.evidence.length > 0);\n"
        "} catch {\n"
        "  return false;\n"
        "}\n"
    )


def build_evaluation(
    questions: list[dict[str, Any]], known_artifacts: list[str]
) -> dict[str, Any]:
    """Create the Skill Arena compare manifest for two isolated PI profiles."""

    prompts = []
    for question in questions:
        prompts.append(
            {
                "id": question["id"],
                "description": f"Isolated semantic question {question['id'].split('-', 1)[0]}",
                "prompt": LiteralString(str(question["prompt"])),
                "evaluation": {
                    "assertions": [
                        {
                            "type": "javascript",
                            "metric": "semantic-accuracy",
                            "value": exact_answer_assertion(
                                str(question["id"]), question["expected_answer"]
                            ),
                        },
                        {
                            "type": "javascript",
                            "metric": "evidence-grounding",
                            "value": exact_evidence_assertion(
                                str(question["id"]), question["accepted_evidence_sets"]
                            ),
                        },
                    ]
                },
            }
        )
    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": "semantic-okf-reader-v2-300-compare",
            "description": (
                "Compare isolated PI semantic QA with no knowledge access against the "
                "dedicated consult-semantic-okf skill plus a pinned 60-entity snapshot, "
                "using GPT-5.6 Luna for every active v2 request."
            ),
            "tags": [
                "semantic-okf",
                "knowledge",
                "retrieval",
                "pi",
                "compare",
                "300-questions",
                "v2",
                "luna-only",
            ],
        },
        "task": {"prompts": prompts},
        "workspace": {
            "sources": [
                {
                    "id": "isolated-base",
                    "type": "local-path",
                    "path": "evaluations/semantic-okf-reader/fixtures/workspaces/base-v2",
                    "target": "/",
                }
            ],
            "setup": {
                "initializeGit": True,
                "env": {"SEMANTIC_OKF_BUNDLE": "$WORKSPACE/knowledge"},
            },
        },
        "evaluation": {
            "assertions": [
                {"type": "is-json", "metric": "response-format"},
                {
                    "type": "javascript",
                    "metric": "response-contract",
                    "value": shared_response_assertion(),
                },
                {
                    "type": "javascript",
                    "metric": "evidence-path-validity",
                    "value": evidence_path_assertion(known_artifacts),
                },
            ],
            "requests": 1,
            "timeoutMs": 600000,
            "tracing": False,
            "maxConcurrency": 4,
            "noCache": True,
        },
        "comparison": {
            "profiles": [
                {
                    "id": "no-skill",
                    "description": "Strictly isolated control with neither the reader skill nor the snapshot.",
                    "isolation": {"inheritSystem": False},
                    "capabilities": {},
                    "output": {
                        "tags": ["control", "knowledge-off"],
                        "labels": {"skill_state": "off", "knowledge_access": "off"},
                    },
                },
                {
                    "id": "skill",
                    "description": (
                        "Strictly isolated profile with the dedicated consult-semantic-okf skill "
                        "and pinned knowledge snapshot supplied by the active v2 overlay."
                    ),
                    "isolation": {"inheritSystem": False},
                    "capabilities": {
                        "skills": [
                            {
                                "source": {
                                    "type": "local-path",
                                    "path": (
                                        "evaluations/semantic-okf-reader/fixtures/workspaces/reader-v2-overlay"
                                    ),
                                    "skillId": "consult-semantic-okf",
                                },
                                "install": {"strategy": "workspace-overlay"},
                            }
                        ]
                    },
                    "output": {
                        "tags": ["skill", "knowledge-on"],
                        "labels": {"skill_state": "on", "knowledge_access": "on"},
                    },
                },
            ],
            "variants": [
                {
                    "id": "pi-luna-only",
                    "description": "PI with GPT-5.6 Luna for every active v2 answer request.",
                    "agent": {
                        "adapter": "pi",
                        "model": "openai-codex/gpt-5.6-luna",
                        "executionMethod": "command",
                        "commandPath": "bin/pi-luna.ps1",
                        "sandboxMode": "read-only",
                        "approvalPolicy": "never",
                        "webSearchEnabled": False,
                        "networkAccessEnabled": True,
                        "reasoningEffort": "medium",
                        "additionalDirectories": [],
                        "cliEnv": {
                            "PI_MODEL_TIMEOUT_SECONDS": "240",
                        },
                        "config": {},
                    },
                    "output": {
                        "tags": ["pi", "gpt-5.6-luna", "luna-only", "isolated", "v2"],
                        "labels": {
                            "variantDisplayName": "PI GPT-5.6 Luna",
                            "adapter_family": "pi",
                            "model": "openai-codex/gpt-5.6-luna",
                            "routing": "luna-only",
                            "benchmark_generation": "v2",
                        },
                    },
                }
            ],
        },
    }


def render_outputs(bundle: Path) -> dict[Path, str]:
    """Render every generated benchmark artifact in memory."""

    tree_sha256 = snapshot_tree_sha256(bundle)
    if tree_sha256 != PINNED_SNAPSHOT_TREE_SHA256:
        raise ValueError(
            "benchmark snapshot drifted: "
            f"expected {PINNED_SNAPSHOT_TREE_SHA256}, found {tree_sha256}"
        )
    skill_tree_sha256 = snapshot_tree_sha256(SKILL_SNAPSHOT_ROOT)
    if skill_tree_sha256 != PINNED_SKILL_SNAPSHOT_TREE_SHA256:
        raise ValueError(
            "benchmark skill snapshot drifted: "
            f"expected {PINNED_SKILL_SNAPSHOT_TREE_SHA256}, found {skill_tree_sha256}"
        )
    questions = build_questions(bundle)
    known_artifacts = bundle_artifact_paths(bundle)
    evaluation = build_evaluation(questions, known_artifacts)
    smoke_ids = {
        "q006-typed-fact",
        "q081-multi-hop-join",
        "q171-aggregation",
        "q216-provenance-lineage",
        "q276-integrity-negative",
    }
    smoke_questions = [item for item in questions if item["id"] in smoke_ids]
    if len(smoke_questions) != len(smoke_ids):
        raise ValueError("smoke question selection drifted")
    smoke_evaluation = build_evaluation(smoke_questions, known_artifacts)
    smoke_evaluation["benchmark"]["id"] = "semantic-okf-reader-v2-smoke-compare"
    smoke_evaluation["benchmark"]["description"] = (
        "Five-question Luna-only smoke comparison for the active v2 Semantic OKF reader benchmark."
    )
    smoke_evaluation["benchmark"]["tags"] = [
        "semantic-okf",
        "knowledge",
        "pi",
        "compare",
        "smoke",
        "v2",
        "luna-only",
    ]
    smoke_evaluation["evaluation"]["maxConcurrency"] = 4
    category_counts = Counter(str(item["category"]) for item in questions)
    difficulty_counts = Counter(str(item["difficulty"]) for item in questions)
    layer_counts = Counter(str(item["query_layer"]) for item in questions)
    source_manifest = load_json(bundle / "semantic" / "source-manifest.json")
    coverage = {
        "schema_version": "2.0",
        "benchmark_generation": "v2",
        "question_count": len(questions),
        "category_counts": dict(sorted(category_counts.items())),
        "difficulty_counts": dict(sorted(difficulty_counts.items())),
        "query_layer_counts": dict(sorted(layer_counts.items())),
        "profiles": ["no-skill", "skill"],
        "variants": ["pi-luna-only"],
        "requests_per_cell": 1,
        "expanded_executions": len(questions) * 2,
        "smoke_question_ids": sorted(smoke_ids),
        "smoke_expanded_executions": len(smoke_questions) * 2,
        "snapshot": {
            "record_count": 60,
            "source_count": 40,
            "plan_sha256": source_manifest["plan_sha256"],
            "tree_sha256": tree_sha256,
        },
        "skill_snapshot": {
            "skill_id": "consult-semantic-okf",
            "tree_sha256": skill_tree_sha256,
        },
    }
    questions_text = "".join(
        canonical_json(
            {
                "id": item["id"],
                "category": item["category"],
                "difficulty": item["difficulty"],
                "query_layer": item["query_layer"],
                "question": item["question"],
                "oracle": item["oracle"],
                "expected": item["expected"],
                "evidence": {
                    "accepted_sets": item["accepted_evidence_sets"],
                    "accepted_set_sha256": item["accepted_evidence_sha256"],
                    "result_sha256": item["result_sha256"],
                },
                "semantic_descriptor": item["semantic_descriptor"],
                "semantic_signature": item["semantic_signature"],
            }
        )
        + "\n"
        for item in questions
    )
    evaluation_text = yaml.dump(
        evaluation,
        Dumper=BenchmarkDumper,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    smoke_evaluation_text = yaml.dump(
        smoke_evaluation,
        Dumper=BenchmarkDumper,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )
    return {
        EVALUATION_ROOT / "questions.jsonl": questions_text,
        EVALUATION_ROOT / "evaluation.yaml": evaluation_text,
        EVALUATION_ROOT / "smoke-evaluation.yaml": smoke_evaluation_text,
        EVALUATION_ROOT / "coverage.json": json.dumps(
            coverage, ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=BUNDLE_ROOT)
    parser.add_argument("--check", action="store_true", help="Fail when generated files drift.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = args.bundle.expanduser().resolve()
    outputs = render_outputs(bundle)
    if args.check:
        drift = [
            path.relative_to(EVALUATION_ROOT).as_posix()
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if drift:
            print(f"Generated benchmark drift: {', '.join(drift)}")
            return 1
        print(f"Semantic benchmark is current: {QUESTION_COUNT} questions")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated {QUESTION_COUNT} semantic questions and evaluation.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
