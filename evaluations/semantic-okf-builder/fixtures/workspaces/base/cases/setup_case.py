#!/usr/bin/env python3
"""Materialize one deterministic Semantic OKF lifecycle benchmark case."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Callable


XSD_STRING = "xsd:string"


def write_text(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(root: Path, relative: str, payload: Any) -> None:
    write_text(root, relative, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def bundle(slug: str, version: str, title: str) -> dict[str, str]:
    return {
        "title": title,
        "description": f"Deterministic lifecycle fixture for {slug}.",
        "base_iri": f"https://example.org/{slug}/",
        "ontology_iri": f"https://example.org/ontology/{slug}",
        "version_iri": f"https://example.org/ontology/{slug}/{version}",
        "prefix": slug.replace("-", ""),
        "owl_profile": "rl",
    }


def datatype_property(name: str, domain: str) -> dict[str, str]:
    return {"name": name, "kind": "datatype", "domain": domain, "range": XSD_STRING}


def required_rule(name: str, target: str, path: str) -> dict[str, Any]:
    return {
        "name": name,
        "target_class": target,
        "path": path,
        "min_count": 1,
        "datatype": XSD_STRING,
        "message": f"Each {target} requires {path}.",
        "basis": {"kind": "operational-policy", "references": [f"FIXTURE-{name}"]},
    }


def person_source(path: str = "sources/people.csv") -> dict[str, Any]:
    return {
        "id": "people",
        "kind": "csv",
        "path": path,
        "concept_type": "Person",
        "ontology_class": "Person",
        "id_field": "id",
        "title_field": "name",
        "fields": {"name": "name", "role": "role"},
        "schema": {"id": "string", "name": "string", "role": "string"},
    }


def project_source(path: str = "sources/projects.jsonl") -> dict[str, Any]:
    return {
        "id": "projects",
        "kind": "json",
        "path": path,
        "concept_type": "Project",
        "ontology_class": "Project",
        "id_field": "id",
        "title_field": "title",
        "fields": {"status": "status"},
        "schema": {"id": "string", "title": "string", "status": "string"},
    }


def manifest(
    slug: str,
    version: str,
    title: str,
    classes: list[dict[str, str]],
    properties: list[dict[str, str]],
    rules: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "bundle": bundle(slug, version, title),
        "ontology": {"classes": classes, "properties": properties},
        "rules": rules,
        "sources": sources,
    }


PERSON_CLASSES = [{"name": "Person", "label": "person"}]
PERSON_PROPERTIES = [datatype_property("name", "Person"), datatype_property("role", "Person")]
PERSON_RULES = [required_rule("PersonNameRule", "Person", "name")]
PROJECT_CLASS = {"name": "Project", "label": "project"}
PROJECT_PROPERTY = datatype_property("status", "Project")
PROJECT_RULE = required_rule("ProjectStatusRule", "Project", "status")


def setup_create(root: Path) -> None:
    classes = [
        {"name": "PolicyDocument", "label": "policy document"},
        *PERSON_CLASSES,
        PROJECT_CLASS,
        {"name": "VocabularyResource", "label": "vocabulary resource"},
    ]
    properties = [
        datatype_property("policyCode", "PolicyDocument"),
        *PERSON_PROPERTIES,
        PROJECT_PROPERTY,
        datatype_property("prefLabel", "VocabularyResource"),
    ]
    rules = [
        required_rule("PolicyCodeRule", "PolicyDocument", "policyCode"),
        *PERSON_RULES,
        PROJECT_RULE,
        required_rule("VocabularyLabelRule", "VocabularyResource", "prefLabel"),
    ]
    sources = [
        {
            "id": "policies",
            "kind": "markdown",
            "path": "sources/policies/*.md",
            "concept_type": "Policy",
            "ontology_class": "PolicyDocument",
            "fields": {"code": "policyCode"},
        },
        person_source(),
        project_source(),
        {
            "id": "vocabulary",
            "kind": "rdf",
            "path": "sources/vocabulary.ttl",
            "format": "turtle",
            "concept_type": "Vocabulary Resource",
            "ontology_class": "VocabularyResource",
            "title_predicate": "http://www.w3.org/2000/01/rdf-schema#label",
            "fields": {"http://www.w3.org/2004/02/skos/core#prefLabel": "prefLabel"},
        },
    ]
    write_json(root, "manifest.json", manifest("create", "1.0.0", "Heterogeneous fixture", classes, properties, rules, sources))
    write_text(
        root,
        "sources/policies/retention.md",
        "---\ntitle: Retention policy\ncode: POL-1\n---\n\n# Retention policy\n\nRetain reviewed records for seven years.",
    )
    write_text(root, "sources/people.csv", "id,name,role\nperson-1,Alice,Engineer\nperson-2,Bob,Reviewer")
    write_text(root, "sources/projects.jsonl", '{"id":"project-1","title":"Atlas","status":"active"}')
    write_text(
        root,
        "sources/vocabulary.ttl",
        "@prefix ex: <https://example.org/vocabulary/> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n\n"
        'ex:sharing a skos:Concept ; rdfs:label "Knowledge sharing" ; skos:prefLabel "Knowledge sharing" .',
    )


def setup_augment(root: Path) -> None:
    v1 = manifest("augment", "1.0.0", "Augment fixture", PERSON_CLASSES, PERSON_PROPERTIES, PERSON_RULES, [person_source()])
    v2 = manifest(
        "augment",
        "1.1.0",
        "Augment fixture",
        [*PERSON_CLASSES, PROJECT_CLASS],
        [*PERSON_PROPERTIES, PROJECT_PROPERTY],
        [*PERSON_RULES, PROJECT_RULE],
        [person_source(), project_source()],
    )
    write_json(root, "manifest-v1.json", v1)
    write_json(root, "manifest-v2.json", v2)
    write_text(root, "sources/people.csv", "id,name,role\nperson-1,Alice,Engineer\nperson-2,Bob,Reviewer")
    write_text(root, "sources/projects.jsonl", '{"id":"project-1","title":"Atlas","status":"active"}')


def setup_refresh(root: Path) -> None:
    write_json(
        root,
        "manifest.json",
        manifest("refresh", "1.0.0", "Refresh fixture", PERSON_CLASSES, PERSON_PROPERTIES, PERSON_RULES, [person_source("live/people.csv")]),
    )
    first = "id,name,role\nperson-1,Alice,Engineer"
    second = "id,name,role\nperson-1,Alice,Architect\nperson-2,Bob,Reviewer"
    write_text(root, "live/people.csv", first)
    write_text(root, "seeds/people-v1.csv", first)
    write_text(root, "seeds/people-v2.csv", second)


def setup_remove(root: Path) -> None:
    v1 = manifest(
        "remove",
        "1.0.0",
        "Removal fixture",
        [*PERSON_CLASSES, PROJECT_CLASS],
        [*PERSON_PROPERTIES, PROJECT_PROPERTY],
        [*PERSON_RULES, PROJECT_RULE],
        [person_source(), project_source()],
    )
    reused = manifest("remove", "1.0.0", "Removal fixture", PERSON_CLASSES, PERSON_PROPERTIES, PERSON_RULES, [person_source()])
    approved = manifest("remove", "2.0.0", "Removal fixture", PERSON_CLASSES, PERSON_PROPERTIES, PERSON_RULES, [person_source()])
    write_json(root, "manifest-v1.json", v1)
    write_json(root, "manifest-v2-reused-version.json", reused)
    write_json(root, "manifest-v2.json", approved)
    write_text(root, "sources/people.csv", "id,name,role\nperson-1,Alice,Engineer")
    write_text(root, "sources/projects.jsonl", '{"id":"project-1","title":"Atlas","status":"active"}')


def setup_topology(root: Path) -> None:
    write_json(
        root,
        "topology-request.json",
        {
            "crm-support": {
                "facts": ["different authorities", "overlapping local IDs", "one shared release", "must retain source identity"]
            },
            "regional-partitions": {
                "facts": ["same authority", "same schema and mapping", "global IDs", "append-only partitions"]
            },
            "tenant-isolation": {
                "facts": ["different tenants", "hard access boundary", "independent deletion and release"]
            },
            "vendor-entity-fusion": {
                "facts": ["records describe the same entities", "field precedence required", "multi-origin lineage required"]
            },
        },
    )


def setup_atomic(root: Path) -> None:
    valid = manifest("atomic", "1.0.0", "Atomic fixture", PERSON_CLASSES, PERSON_PROPERTIES, PERSON_RULES, [person_source("valid/people.csv")])
    invalid = manifest("atomic", "1.0.0", "Atomic fixture", PERSON_CLASSES, PERSON_PROPERTIES, PERSON_RULES, [person_source("invalid/people.csv")])
    write_json(root, "manifest-valid.json", valid)
    write_json(root, "manifest-invalid.json", invalid)
    write_text(root, "valid/people.csv", "id,name,role\nperson-1,Alice,Engineer")
    write_text(root, "invalid/people.csv", "id,name,role\nperson-1,Alice,Engineer\nperson-1,Mallory,Manager")


def setup_tamper(root: Path) -> None:
    write_json(
        root,
        "manifest.json",
        manifest("tamper", "1.0.0", "Tamper fixture", PERSON_CLASSES, PERSON_PROPERTIES, PERSON_RULES, [person_source()]),
    )
    write_text(root, "sources/people.csv", "id,name,role\nperson-1,Alice,Engineer")


SETUP: dict[str, Callable[[Path], None]] = {
    "create": setup_create,
    "augment": setup_augment,
    "refresh": setup_refresh,
    "remove": setup_remove,
    "topology": setup_topology,
    "atomic": setup_atomic,
    "tamper": setup_tamper,
}


def reset_target(target: Path, *, force: bool) -> Path:
    workspace = Path.cwd().resolve()
    resolved = target.resolve()
    if resolved == workspace or workspace not in resolved.parents:
        raise ValueError(f"output must be a child of the current workspace: {resolved}")
    if resolved.exists():
        if not force:
            raise FileExistsError(f"output already exists: {resolved}")
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=tuple(SETUP))
    parser.add_argument("output", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--reset-deliverable", type=Path)
    args = parser.parse_args()
    output = reset_target(args.output, force=args.force)
    if args.reset_deliverable is not None:
        reset_target(args.reset_deliverable, force=True)
    SETUP[args.case](output)
    print(json.dumps({"case": args.case, "output": str(output), "status": "ready"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
