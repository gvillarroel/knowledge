from __future__ import annotations

import copy
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-semantic-okf"
SCRIPTS = SKILL_ROOT / "scripts"


def load_core() -> ModuleType:
    """Load the shared semantic module under its runtime import name."""

    pytest.importorskip("rdflib")
    pytest.importorskip("pyshacl")
    path = SCRIPTS / "_semantic_okf.py"
    spec = importlib.util.spec_from_file_location("_semantic_okf", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_script(name: str) -> ModuleType:
    """Load one standalone skill script for dependency-free unit checks."""

    if name in {"build_semantic_okf.py", "validate_semantic_okf.py"}:
        load_core()
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(f"test_semantic_okf_{path.stem}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixture_manifest() -> dict[str, object]:
    """Return the reviewed semantic plan shared by unit and integration tests."""

    return {
        "schema_version": "1.0",
        "bundle": {
            "title": "Semantic knowledge fixture",
            "description": "A deterministic heterogeneous knowledge bundle.",
            "base_iri": "https://example.org/knowledge/",
            "ontology_iri": "https://example.org/ontology/research",
            "version_iri": "https://example.org/ontology/research/1.0.0",
            "prefix": "research",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [
                {"name": "PolicyDocument", "label": "policy document"},
                {"name": "Person", "label": "person"},
                {"name": "Project", "label": "project"},
                {"name": "VocabularyResource", "label": "vocabulary resource"},
            ],
            "properties": [
                {
                    "name": "policyCode",
                    "kind": "datatype",
                    "domain": "PolicyDocument",
                    "range": "xsd:string",
                },
                {"name": "name", "kind": "datatype", "domain": "Person", "range": "xsd:string"},
                {"name": "role", "kind": "datatype", "domain": "Person", "range": "xsd:string"},
                {
                    "name": "status",
                    "kind": "datatype",
                    "domain": "Project",
                    "range": "xsd:string",
                },
                {
                    "name": "prefLabel",
                    "kind": "datatype",
                    "domain": "VocabularyResource",
                    "range": "xsd:string",
                },
            ],
        },
        "rules": [
            {
                "name": "PolicyCodeRule",
                "target_class": "PolicyDocument",
                "path": "policyCode",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Each policy requires a code.",
                "basis": {"kind": "operational-policy", "references": ["POLICY-1"]},
            },
            {
                "name": "PersonNameRule",
                "target_class": "Person",
                "path": "name",
                "min_count": 1,
                "max_count": 1,
                "datatype": "xsd:string",
                "message": "Each person requires one name.",
                "basis": {"kind": "operational-policy", "references": ["PEOPLE-1"]},
            },
            {
                "name": "PersonRoleRule",
                "target_class": "Person",
                "path": "role",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Each person requires a role.",
                "basis": {"kind": "operational-policy", "references": ["PEOPLE-2"]},
            },
            {
                "name": "ProjectStatusRule",
                "target_class": "Project",
                "path": "status",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Each project requires a status.",
                "basis": {"kind": "operational-policy", "references": ["PROJECT-1"]},
            },
            {
                "name": "VocabularyLabelRule",
                "target_class": "VocabularyResource",
                "path": "prefLabel",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Each vocabulary resource requires a label.",
                "basis": {"kind": "evidence", "references": ["VOCAB-1"]},
            },
        ],
        "sources": [
            {
                "id": "policies",
                "kind": "markdown",
                "path": "sources/policies/*.md",
                "concept_type": "Policy",
                "ontology_class": "PolicyDocument",
                "fields": {"code": "policyCode"},
            },
            {
                "id": "people",
                "kind": "csv",
                "path": "sources/people.csv",
                "concept_type": "Person",
                "ontology_class": "Person",
                "id_field": "id",
                "title_field": "name",
                "fields": {"name": "name", "role": "role"},
                "schema": {"id": "string", "name": "string", "role": "string"},
                "options": {"header": "true", "enforceSchema": "false"},
            },
            {
                "id": "projects",
                "kind": "json",
                "path": "sources/projects.jsonl",
                "concept_type": "Project",
                "ontology_class": "Project",
                "id_field": "id",
                "title_field": "title",
                "fields": {"status": "status"},
                "schema": {"id": "string", "title": "string", "status": "string"},
            },
            {
                "id": "vocabulary",
                "kind": "rdf",
                "path": "sources/vocabulary.ttl",
                "format": "turtle",
                "concept_type": "Vocabulary Resource",
                "ontology_class": "VocabularyResource",
                "title_predicate": "http://www.w3.org/2000/01/rdf-schema#label",
                "fields": {"http://www.w3.org/2000/01/rdf-schema#label": "prefLabel"},
            },
        ],
    }


def write_fixture(root: Path) -> Path:
    """Write Markdown, CSV, JSONL, RDF, and their semantic plan."""

    policies = root / "sources" / "policies"
    policies.mkdir(parents=True)
    (policies / "retention.md").write_text(
        "---\ntitle: Retention Policy\ncode: POL-1\n---\n\n"
        "# Retention Policy\n\nKeep accepted records for seven years.\n",
        encoding="utf-8",
    )
    (root / "sources" / "people.csv").write_text(
        "id,name,role\nperson-2,Bob,Reviewer\nperson-1,Alice,Engineer\n",
        encoding="utf-8",
    )
    (root / "sources" / "projects.jsonl").write_text(
        '{"id":"project-2","title":"Beta","status":"paused"}\n'
        '{"id":"project-1","title":"Alpha","status":"active"}\n',
        encoding="utf-8",
    )
    (root / "sources" / "vocabulary.ttl").write_text(
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n"
        '<https://example.org/vocab/term-one> a skos:Concept ; rdfs:label "Term One" .\n',
        encoding="utf-8",
    )
    manifest = root / "manifest.json"
    manifest.write_text(json.dumps(fixture_manifest(), indent=2) + "\n", encoding="utf-8")
    return manifest


def source_combination_manifest() -> dict[str, object]:
    """Return a plan that exercises separation and homogeneous partition union."""

    source_contract = {
        "kind": "csv",
        "concept_type": "Person",
        "ontology_class": "Person",
        "id_field": "id",
        "title_field": "name",
        "fields": {"name": "name", "role": "role"},
        "schema": {"id": "string", "name": "string", "role": "string"},
        "options": {"header": "true", "mode": "FAILFAST"},
    }
    return {
        "schema_version": "1.0",
        "bundle": {
            "title": "Source combination fixture",
            "description": "Separate authorities and one homogeneous partition union.",
            "base_iri": "https://example.org/combine/",
            "ontology_iri": "https://example.org/ontology/combine",
            "version_iri": "https://example.org/ontology/combine/1.0.0",
            "prefix": "combine",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "Person", "label": "person"}],
            "properties": [
                {"name": "name", "kind": "datatype", "domain": "Person", "range": "xsd:string"},
                {"name": "role", "kind": "datatype", "domain": "Person", "range": "xsd:string"},
            ],
        },
        "rules": [
            {
                "name": "PersonNameRule",
                "target_class": "Person",
                "path": "name",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Each accepted person requires a name.",
                "basis": {"kind": "operational-policy", "references": ["COMBINE-1"]},
            },
            {
                "name": "PersonRoleRule",
                "target_class": "Person",
                "path": "role",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Each accepted person requires a role.",
                "basis": {"kind": "operational-policy", "references": ["COMBINE-2"]},
            },
        ],
        "sources": [
            {"id": "crm-east", "path": "sources/separate/east.csv", **source_contract},
            {"id": "crm-west", "path": "sources/separate/west.csv", **source_contract},
            {"id": "directory", "path": "sources/combined/*.csv", **source_contract},
        ],
    }


def write_source_combination_fixture(root: Path) -> Path:
    """Write two separate authorities and two partitions of one logical source."""

    separate = root / "sources" / "separate"
    combined = root / "sources" / "combined"
    separate.mkdir(parents=True)
    combined.mkdir(parents=True)
    (separate / "east.csv").write_text(
        "id,name,role\nshared-1,Alice East,Sales\n", encoding="utf-8"
    )
    (separate / "west.csv").write_text(
        "id,name,role\nshared-1,Alice West,Support\n", encoding="utf-8"
    )
    (combined / "a.csv").write_text(
        "id,name,role\nemployee-1,Carol,Engineer\n", encoding="utf-8"
    )
    (combined / "b.csv").write_text(
        "role,id,name\nReviewer,employee-2,Dan\n", encoding="utf-8"
    )
    manifest = root / "manifest.json"
    manifest.write_text(
        json.dumps(source_combination_manifest(), indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def make_source_combination_records(
    core: ModuleType, manifest: dict[str, object], root: Path
) -> tuple[list[object], list[dict[str, object]]]:
    """Create records for both source-combination modes."""

    summaries = [
        {
            "id": source["id"],
            "kind": source["kind"],
            "path": source["path"],
            "content_sha256": core.sha256_json({"fixture": source["id"]}),
            "allow_empty": False,
        }
        for source in manifest["sources"]
    ]
    summary_by_id = {summary["id"]: summary for summary in summaries}
    source_by_id = core.source_by_id(manifest)
    rows = [
        ("crm-east", "sources/separate/east.csv", "shared-1", "Alice East", "Sales"),
        ("crm-west", "sources/separate/west.csv", "shared-1", "Alice West", "Support"),
        ("directory", "sources/combined/a.csv", "employee-1", "Carol", "Engineer"),
        ("directory", "sources/combined/b.csv", "employee-2", "Dan", "Reviewer"),
    ]
    records = []
    for source_id, relative_path, record_id, name, role in rows:
        source = source_by_id[source_id]
        raw = {
            "source_id": source_id,
            "source_kind": "csv",
            "source_path": (root / relative_path).as_uri(),
            "record_id": record_id,
            "subject_iri": "",
            "title": name,
            "body": f"# {name}\n\n- **name**: {name}\n- **role**: {role}",
            "attributes": {"name": name, "role": role},
        }
        records.append(
            core.finalize_record(raw, source, summary_by_id[source_id], manifest, root)
        )
    return records, summaries


def make_records(core: ModuleType, manifest: dict[str, object], root: Path) -> tuple[list[object], list[dict[str, object]]]:
    """Create the six normalized fixture records."""

    source_specs = core.source_by_id(manifest)
    summaries = [
        {
            "id": source["id"],
            "kind": source["kind"],
            "path": source["path"],
            "content_sha256": core.sha256_json({"fixture": source["id"]}),
            "allow_empty": False,
        }
        for source in manifest["sources"]
    ]
    summary_by_id = {summary["id"]: summary for summary in summaries}
    rows = [
        {
            "source_id": "policies",
            "source_kind": "markdown",
            "source_path": (root / "sources" / "policies" / "retention.md").as_uri(),
            "record_id": "sources/policies/retention",
            "subject_iri": "",
            "title": "Retention Policy",
            "body": "# Retention Policy\n\nKeep accepted records for seven years.",
            "attributes": {"code": "POL-1"},
        },
        *[
            {
                "source_id": "people",
                "source_kind": "csv",
                "source_path": (root / "sources" / "people.csv").as_uri(),
                "record_id": identifier,
                "subject_iri": "",
                "title": name,
                "body": f"# {name}\n\n- **name**: {name}\n- **role**: {role}",
                "attributes": {"name": name, "role": role},
            }
            for identifier, name, role in (
                ("person-2", "Bob", "Reviewer"),
                ("person-1", "Alice", "Engineer"),
            )
        ],
        *[
            {
                "source_id": "projects",
                "source_kind": "json",
                "source_path": (root / "sources" / "projects.jsonl").as_uri(),
                "record_id": identifier,
                "subject_iri": "",
                "title": title,
                "body": f"# {title}\n\n- **status**: {status}",
                "attributes": {"status": status},
            }
            for identifier, title, status in (
                ("project-2", "Beta", "paused"),
                ("project-1", "Alpha", "active"),
            )
        ],
        {
            "source_id": "vocabulary",
            "source_kind": "rdf",
            "source_path": (root / "sources" / "vocabulary.ttl").as_uri(),
            "record_id": "https://example.org/vocab/term-one",
            "subject_iri": "https://example.org/vocab/term-one",
            "title": "Term One",
            "body": "# Term One\n\nVocabulary fixture.",
            "attributes": {"http://www.w3.org/2000/01/rdf-schema#label": "Term One"},
        },
    ]
    records = [
        core.finalize_record(
            row,
            source_specs[row["source_id"]],
            summary_by_id[row["source_id"]],
            manifest,
            root,
        )
        for row in rows
    ]
    return records, summaries


def run_skill_script(script: str, *args: str, timeout: int = 240) -> subprocess.CompletedProcess[str]:
    """Run one skill command in the current isolated Python environment."""

    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def json_line(output: str) -> dict[str, object]:
    """Parse the last JSON object emitted by a skill command."""

    for line in reversed(output.splitlines()):
        if line.lstrip().startswith("{"):
            value = json.loads(line)
            assert isinstance(value, dict)
            return value
    raise AssertionError(f"no JSON object found in output: {output!r}")


def processor_info(records: int, sources: int) -> dict[str, object]:
    """Return the stable pure-Python processor contract metadata."""

    return {
        "name": "semantic-okf-python",
        "contract_version": "1.0",
        "records": records,
        "sources": sources,
    }


def test_skill_metadata_and_locked_dependencies_are_complete() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    direct = (SCRIPTS / "requirements.in").read_text(encoding="utf-8").splitlines()
    compiled = (SCRIPTS / "requirements.txt").read_text(encoding="utf-8")

    assert "name: build-semantic-okf" in skill
    assert "semantic-plan.json" in skill
    assert "refresh_semantic_okf.py" in skill
    assert "query_semantic_okf.py" not in skill
    assert "$consult-semantic-okf" in skill
    assert "source-combination.md" in skill
    assert "partition union" in skill
    assert "$build-semantic-okf" in metadata
    assert "Create and refresh semantic knowledge snapshots" in metadata
    assert (SKILL_ROOT / "references" / "refreshing.md").is_file()
    assert (SKILL_ROOT / "references" / "python-runtime.md").is_file()
    assert (SCRIPTS / "runtime_smoke.py").is_file()
    assert not (SCRIPTS / "query_semantic_okf.py").exists()
    assert not (SKILL_ROOT / "references" / "querying.md").exists()
    assert not (SKILL_ROOT / "references" / "cross-source-synthesis.md").exists()
    combination = SKILL_ROOT / "references" / "source-combination.md"
    assert combination.is_file()
    protocol = combination.read_text(encoding="utf-8")
    assert "Separate bundles" in protocol
    assert "homogeneous partition union" in protocol
    assert "Consultation handoff" in protocol
    assert "upstream canonicalization" in protocol
    assert direct == [
        "PyYAML==6.0.3",
        "rdflib==7.6.0",
        "pyshacl==0.40.0",
        "owlrl==7.6.2",
    ]
    for requirement in ("pyyaml==6.0.3", "rdflib==7.6.0", "pyshacl==0.40.0", "owlrl==7.6.2"):
        assert requirement in compiled.lower()


def test_production_skill_has_no_distributed_runtime_implementation_tokens() -> None:
    """Keep the GPT model nickname unrelated to this local ingestion runtime."""

    forbidden = re.compile(
        r"apache\s+spark|pyspark|py4j|sparkcontext|sparksession|"
        r"spark[_-]?pi|spark-runtime|--master|\bspark\b|\bjava\b|\bjdk\b",
        re.IGNORECASE,
    )
    text_suffixes = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}
    violations: list[str] = []
    for path in sorted(SKILL_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        match = forbidden.search(path.read_text(encoding="utf-8"))
        if match:
            violations.append(f"{path.relative_to(SKILL_ROOT).as_posix()}: {match.group(0)}")
    assert violations == []


def test_manifest_rejects_semantically_unsafe_plans() -> None:
    core = load_core()
    valid = fixture_manifest()
    assert core.validate_manifest(valid) == []

    bad_count = copy.deepcopy(valid)
    bad_count["rules"][0]["min_count"] = "one"
    assert any("min_count" in error for error in core.validate_manifest(bad_count))

    bad_domain = copy.deepcopy(valid)
    bad_domain["sources"][3]["fields"] = {
        "http://www.w3.org/2000/01/rdf-schema#label": "name"
    }
    assert any("different domain" in error for error in core.validate_manifest(bad_domain))

    bad_range = copy.deepcopy(valid)
    bad_range["rules"][1]["datatype"] = "xsd:integer"
    assert any("differs from the path property range" in error for error in core.validate_manifest(bad_range))

    bad_path = copy.deepcopy(valid)
    bad_path["sources"][0]["path"] = "../outside/*.md"
    assert any("manifest-relative" in error for error in core.validate_manifest(bad_path))

    bad_rdf = copy.deepcopy(valid)
    bad_rdf["sources"][3]["format"] = "json-ld"
    assert any("format must be" in error for error in core.validate_manifest(bad_rdf))

    collision = copy.deepcopy(valid)
    collision["ontology"]["properties"][0]["name"] = "okfConceptId"
    assert any("reserved" in error for error in core.validate_manifest(collision))

    lossy = copy.deepcopy(valid)
    lossy["sources"][1]["options"]["mode"] = "PERMISSIVE"
    assert any("FAILFAST" in error for error in core.validate_manifest(lossy))

    reserved_source = copy.deepcopy(valid)
    reserved_source["sources"][0]["id"] = "con"
    assert any("reserved on Windows" in error for error in core.validate_manifest(reserved_source))

    reserved_column = copy.deepcopy(valid)
    reserved_column["sources"][1]["schema"]["__semantic_okf_source_path__"] = "string"
    assert any("schema field" in error and "reserved" in error for error in core.validate_manifest(reserved_column))

    advanced_fields = [
        ("classes", 0, "equivalent_to"),
        ("classes", 0, "disjoint_with"),
        ("properties", 0, "key"),
    ]
    for section, index, field in advanced_fields:
        unsupported = copy.deepcopy(valid)
        unsupported["ontology"][section][index][field] = "UnsafeAxiom"
        assert any("unsupported fields" in error for error in core.validate_manifest(unsupported))
    unsupported_cardinality = copy.deepcopy(valid)
    unsupported_cardinality["rules"][0]["max_cardinality"] = 1
    assert any("unsupported fields" in error for error in core.validate_manifest(unsupported_cardinality))


def test_markdown_frontmatter_errors_are_not_silently_discarded() -> None:
    builder = load_script("build_semantic_okf.py")

    with pytest.raises(ValueError, match="unterminated"):
        builder._strip_markdown_frontmatter("---\ntitle: Broken\n# Body\n")
    with pytest.raises(ValueError, match="invalid YAML"):
        builder._strip_markdown_frontmatter("---\ntitle: [broken\n---\n# Body\n")
    with pytest.raises(ValueError, match="must be an object"):
        builder._strip_markdown_frontmatter("---\n- item\n---\n# Body\n")
    assert builder._frontmatter_scalar(date(2026, 7, 10), "created") == "2026-07-10"
    assert builder._markdown_table_cell("<script>|`\n") == "&lt;script&gt;\\|&#96; ↵ "


def test_datatype_encoder_rejects_invalid_lexical_forms() -> None:
    core = load_core()

    assert core._validate_xsd_lexical("2026-07-10Z", "xsd:date", "created") == "2026-07-10Z"
    assert core._validate_xsd_lexical("2026-07-10T12:30:00-04:00", "xsd:dateTime", "created")
    with pytest.raises(core.BundleError, match="xsd:integer"):
        core._validate_xsd_lexical("3.2", "xsd:integer", "count")
    with pytest.raises(core.BundleError, match="xsd:dateTime"):
        core._validate_xsd_lexical("2026-07-10 12:30:00", "xsd:dateTime", "created")
    with pytest.raises(core.BundleError, match="timezone"):
        core._validate_xsd_lexical("2026-07-10+15:00", "xsd:date", "created")


def test_materializer_builds_exact_reproducible_okf_owl_shacl_bundle(tmp_path: Path) -> None:
    core = load_core()
    manifest_path = write_fixture(tmp_path / "fixture")
    manifest = core.load_manifest(manifest_path)
    records, summaries = make_records(core, manifest, manifest_path.parent)
    processor = processor_info(records=6, sources=4)
    first = tmp_path / "bundle-a"
    second = tmp_path / "bundle-b"

    report = core.materialize_bundle(first, manifest, records, summaries, processor)
    core.materialize_bundle(second, manifest, list(reversed(records)), summaries, processor)

    assert report["valid"] is True
    assert report["summary"] == {
        "concepts": 6,
        "records": 6,
        "data_subjects": 6,
        "sources": 4,
        "ontology_classes": 4,
        "owl_profile": "not_checked",
        "owl_consistency": "not_checked",
        "shacl": "conformant",
    }
    expected = {
        "index.md",
        "semantic/ontology.ttl",
        "semantic/data.ttl",
        "semantic/shapes.ttl",
        "semantic/provenance.ttl",
        "semantic/validation-report.ttl",
        "semantic/semantic-plan.json",
        "semantic/source-manifest.json",
        "semantic/records.jsonl",
        "semantic/build-report.json",
    }
    assert expected.issubset(
        {path.relative_to(first).as_posix() for path in first.rglob("*") if path.is_file()}
    )
    assert core.validate_semantic_bundle(first).valid is True

    first_files = {path.relative_to(first).as_posix(): path.read_bytes() for path in first.rglob("*") if path.is_file()}
    second_files = {
        path.relative_to(second).as_posix(): path.read_bytes() for path in second.rglob("*") if path.is_file()
    }
    assert first_files == second_files

    okf = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "skills" / "open-knowledge-format" / "scripts" / "validate_okf_bundle.py"),
            str(first),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert okf.returncode == 0, okf.stderr


def test_source_combination_modes_preserve_identity_provenance_and_queries(
    tmp_path: Path,
) -> None:
    core = load_core()
    manifest_path = write_source_combination_fixture(tmp_path / "fixture")
    manifest = core.load_manifest(manifest_path)
    records, summaries = make_source_combination_records(core, manifest, manifest_path.parent)
    output = tmp_path / "combined-bundle"

    report = core.materialize_bundle(
        output,
        manifest,
        records,
        summaries,
        processor_info(records=4, sources=3),
    )

    assert report["summary"]["sources"] == 3
    assert report["summary"]["records"] == 4
    ledger = [
        json.loads(line)
        for line in (output / "semantic" / "records.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert {record["concept_id"] for record in ledger} == {
        "concepts/crm-east/shared-1-f3a3cc0537",
        "concepts/crm-west/shared-1-f3a3cc0537",
        "concepts/directory/employee-1-92de5a850f",
        "concepts/directory/employee-2-b8d8a8551f",
    }
    shared = [record for record in ledger if record["record_id"] == "shared-1"]
    assert {record["source_id"] for record in shared} == {"crm-east", "crm-west"}
    assert {record["subject_iri"] for record in shared} == {
        "https://example.org/combine/resource/crm-east/shared-1",
        "https://example.org/combine/resource/crm-west/shared-1",
    }
    directory = [record for record in ledger if record["source_id"] == "directory"]
    assert {record["source_path"] for record in directory} == {
        "sources/combined/a.csv",
        "sources/combined/b.csv",
    }

    source_manifest = json.loads(
        (output / "semantic" / "source-manifest.json").read_text(encoding="utf-8")
    )
    assert {
        source["id"]: source["record_count"] for source in source_manifest["sources"]
    } == {"crm-east": 1, "crm-west": 1, "directory": 2}

    provenance = core.Graph().parse(output / "semantic" / "provenance.ttl", format="turtle")
    locations = {str(value) for value in provenance.objects(None, core.PROV.atLocation)}
    assert {
        "sources/separate/east.csv",
        "sources/separate/west.csv",
        "sources/combined/*.csv",
        "sources/combined/a.csv",
        "sources/combined/b.csv",
    }.issubset(locations)

    assert len(shared) == 2
    assert len(directory) == 2


def test_source_combination_duplicate_id_and_subject_fail_atomically(tmp_path: Path) -> None:
    core = load_core()
    manifest_path = write_source_combination_fixture(tmp_path / "fixture")
    manifest = core.load_manifest(manifest_path)
    records, summaries = make_source_combination_records(core, manifest, manifest_path.parent)
    source = core.source_by_id(manifest)["directory"]
    summary = next(item for item in summaries if item["id"] == "directory")
    duplicate = core.finalize_record(
        {
            "source_id": "directory",
            "source_kind": "csv",
            "source_path": (manifest_path.parent / "sources" / "combined" / "c.csv").as_uri(),
            "record_id": "employee-1",
            "subject_iri": "",
            "title": "Mallory",
            "body": "# Mallory",
            "attributes": {"name": "Mallory", "role": "Manager"},
        },
        source,
        summary,
        manifest,
        manifest_path.parent,
    )
    duplicate_output = tmp_path / "duplicate-bundle"

    with pytest.raises(core.BundleError, match="duplicate concept IDs were produced") as failure:
        core.materialize_bundle(
            duplicate_output,
            manifest,
            [*records, duplicate],
            summaries,
            processor_info(records=5, sources=3),
        )
    assert "directory:employee-1@sources/combined/a.csv" in str(failure.value)
    assert "directory:employee-1@sources/combined/c.csv" in str(failure.value)
    assert not duplicate_output.exists()
    assert not list(tmp_path.glob(".duplicate-bundle-*"))

    repeated_subject = "https://example.org/entity/shared-1"
    subject_records = [
        replace(records[0], subject_iri=repeated_subject),
        replace(records[1], subject_iri=repeated_subject),
        *records[2:],
    ]
    subject_output = tmp_path / "subject-collision-bundle"
    with pytest.raises(core.BundleError, match="duplicate subject IRIs were produced") as subject_failure:
        core.materialize_bundle(
            subject_output,
            manifest,
            subject_records,
            summaries,
            processor_info(records=4, sources=3),
        )
    assert repeated_subject in str(subject_failure.value)
    assert "crm-east:shared-1" in str(subject_failure.value)
    assert "crm-west:shared-1" in str(subject_failure.value)
    assert not subject_output.exists()
    assert not list(tmp_path.glob(".subject-collision-bundle-*"))


def test_materializer_is_atomic_when_shacl_rejects_data(tmp_path: Path) -> None:
    core = load_core()
    manifest_path = write_fixture(tmp_path / "fixture")
    manifest = core.load_manifest(manifest_path)
    records, summaries = make_records(core, manifest, manifest_path.parent)
    project = next(record for record in records if record.record_id == "project-1")
    invalid = core.NormalizedRecord(
        **{**project.__dict__, "attributes": {}, "record_sha256": "0" * 64}
    )
    records[records.index(project)] = invalid
    output = tmp_path / "invalid-bundle"

    with pytest.raises(core.BundleError, match="SHACL non-conformant") as failure:
        core.materialize_bundle(
            output,
            manifest,
            records,
            summaries,
            processor_info(records=6, sources=4),
        )
    assert "ProjectStatusRuleShape" in str(failure.value)
    assert "MinCountConstraintComponent" in str(failure.value)
    assert "project-1" in str(failure.value)

    assert not output.exists()
    assert not list(tmp_path.glob(".invalid-bundle-*"))


def test_validator_detects_coordinated_graph_and_report_tampering(tmp_path: Path) -> None:
    core = load_core()
    manifest_path = write_fixture(tmp_path / "fixture")
    manifest = core.load_manifest(manifest_path)
    records, summaries = make_records(core, manifest, manifest_path.parent)
    original = tmp_path / "bundle"
    core.materialize_bundle(
        original,
        manifest,
        records,
        summaries,
        processor_info(records=6, sources=4),
    )

    data_tamper = tmp_path / "data-tamper"
    shutil.copytree(original, data_tamper)
    data_path = data_tamper / "semantic" / "data.ttl"
    data = core.Graph().parse(data_path, format="turtle")
    triple = next(data.triples((None, core.DCTERMS.title, None)))
    data.remove(triple)
    core._write_canonical_graph(data_path, data)
    source_manifest_path = data_tamper / "semantic" / "source-manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    source_manifest["artifacts"]["data"]["sha256"] = core.file_sha256(data_path)
    source_manifest_path.write_text(json.dumps(source_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = core.validate_semantic_bundle(data_tamper)
    assert not result.valid
    assert any("data graph differs" in error["message"] for error in result.errors)

    report_tamper = tmp_path / "report-tamper"
    shutil.copytree(original, report_tamper)
    report_path = report_tamper / "semantic" / "validation-report.ttl"
    report_graph = core.Graph().parse(report_path, format="turtle")
    report_graph.add(
        (
            core.URIRef("https://example.org/tampered"),
            core.RDF.type,
            core.URIRef("https://example.org/FabricatedReport"),
        )
    )
    core._write_canonical_graph(report_path, report_graph)
    source_manifest_path = report_tamper / "semantic" / "source-manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    source_manifest["artifacts"]["validation_report"]["sha256"] = core.file_sha256(report_path)
    source_manifest_path.write_text(json.dumps(source_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = core.validate_semantic_bundle(report_tamper)
    assert not result.valid
    assert result.summary["shacl"] == "conformant"
    assert any("stored SHACL report differs" in error["message"] for error in result.errors)


def test_validator_requires_complete_index_and_build_report(tmp_path: Path) -> None:
    core = load_core()
    manifest_path = write_fixture(tmp_path / "fixture")
    manifest = core.load_manifest(manifest_path)
    records, summaries = make_records(core, manifest, manifest_path.parent)
    original = tmp_path / "bundle"
    core.materialize_bundle(
        original,
        manifest,
        records,
        summaries,
        processor_info(records=6, sources=4),
    )

    incomplete = tmp_path / "incomplete-index"
    shutil.copytree(original, incomplete)
    index = incomplete / "index.md"
    lines = index.read_text(encoding="utf-8").splitlines()
    index.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    result = core.validate_semantic_bundle(incomplete)
    assert any("index and concept document sets differ" in error["message"] for error in result.errors)

    missing_report = tmp_path / "missing-report"
    shutil.copytree(original, missing_report)
    (missing_report / "semantic" / "build-report.json").unlink()
    result = core.validate_semantic_bundle(missing_report)
    assert not result.valid
    assert any("required artifact is missing" in error["message"] for error in result.errors)


def test_runtime_smoke_reports_pure_python_dependencies() -> None:
    result = run_skill_script("runtime_smoke.py")

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    payload = json_line(result.stdout)
    assert payload["status"] == "pass"
    assert payload["processor"] == "python"
    assert payload["python_implementation"]
    assert payload["python_version"]
    assert payload["dependencies"] == {
        "pyshacl": "0.40.0",
        "pyyaml": "6.0.3",
        "rdflib": "7.6.0",
    }


def test_python_builder_processes_all_sources_and_is_deterministic(tmp_path: Path) -> None:
    manifest = write_fixture(tmp_path / "fixture")
    first = tmp_path / "python-a"
    second = tmp_path / "python-b"

    first_run = run_skill_script(
        "build_semantic_okf.py",
        str(manifest),
        str(first),
        "--output-format",
        "json",
    )
    assert first_run.returncode == 0, f"{first_run.stdout}\n{first_run.stderr}"
    report = json_line(first_run.stdout)
    assert report["summary"]["concepts"] == 6
    assert report["processor"] == processor_info(records=6, sources=4)

    second_run = run_skill_script(
        "build_semantic_okf.py",
        str(manifest),
        str(second),
        "--output-format",
        "json",
    )
    assert second_run.returncode == 0, f"{second_run.stdout}\n{second_run.stderr}"

    first_files = {path.relative_to(first).as_posix(): path.read_bytes() for path in first.rglob("*") if path.is_file()}
    second_files = {
        path.relative_to(second).as_posix(): path.read_bytes() for path in second.rglob("*") if path.is_file()
    }
    assert first_files == second_files

    ledger = [
        json.loads(line)
        for line in (first / "semantic" / "records.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert {record["source_kind"] for record in ledger} == {"markdown", "csv", "json", "rdf"}
    assert all(not Path(record["source_path"]).is_absolute() for record in ledger)

    core = load_core()
    data = core.Graph().parse(first / "semantic" / "data.ttl", format="turtle")
    namespace = core.Namespace("https://example.org/ontology/research#")
    people = {
        str(subject)
        for subject in data.subjects(core.RDF.type, namespace.Person)
        if str(data.value(subject, namespace.name)) == "Alice"
    }
    active_projects = {
        str(subject)
        for subject in data.subjects(core.RDF.type, namespace.Project)
        if str(data.value(subject, namespace.status)) == "active"
    }
    assert people == {"https://example.org/knowledge/resource/people/person-1"}
    assert active_projects == {"https://example.org/knowledge/resource/projects/project-1"}


def test_python_source_combination_protocol(tmp_path: Path) -> None:
    manifest = write_source_combination_fixture(tmp_path / "fixture")
    output = tmp_path / "source-combination"

    build = run_skill_script(
        "build_semantic_okf.py",
        str(manifest),
        str(output),
        "--output-format",
        "json",
    )
    assert build.returncode == 0, f"{build.stdout}\n{build.stderr}"
    report = json_line(build.stdout)
    assert report["summary"]["sources"] == 3
    assert report["summary"]["records"] == 4

    source_manifest = json.loads(
        (output / "semantic" / "source-manifest.json").read_text(encoding="utf-8")
    )
    assert {
        source["id"]: source["record_count"] for source in source_manifest["sources"]
    } == {"crm-east": 1, "crm-west": 1, "directory": 2}
    ledger = [
        json.loads(line)
        for line in (output / "semantic" / "records.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len([record for record in ledger if record["record_id"] == "shared-1"]) == 2
    assert {
        record["source_path"] for record in ledger if record["source_id"] == "directory"
    } == {"sources/combined/a.csv", "sources/combined/b.csv"}

    counts = {
        source_id: sum(record["source_id"] == source_id for record in ledger)
        for source_id in {record["source_id"] for record in ledger}
    }
    assert counts == {"crm-east": 1, "crm-west": 1, "directory": 2}

    (manifest.parent / "sources" / "combined" / "c.csv").write_text(
        "id,name,role\nemployee-1,Mallory,Manager\n", encoding="utf-8"
    )
    duplicate_output = tmp_path / "source-combination-duplicate"
    duplicate = run_skill_script(
        "build_semantic_okf.py",
        str(manifest),
        str(duplicate_output),
        "--output-format",
        "json",
    )
    assert duplicate.returncode == 2
    failure = json_line(duplicate.stdout)
    assert failure["code"] == "semantic-error"
    assert "duplicate concept IDs were produced" in failure["error"]
    assert "sources/combined/a.csv" in failure["error"]
    assert "sources/combined/c.csv" in failure["error"]
    assert not duplicate_output.exists()
    assert not list(tmp_path.glob(".source-combination-duplicate-*"))


def test_python_csv_schema_is_name_based_and_casts_are_strict(tmp_path: Path) -> None:
    builder = load_script("build_semantic_okf.py")
    source = {
        "id": "people",
        "kind": "csv",
        "id_field": "id",
        "title_field": "name",
        "fields": {
            "active": "active",
            "joined_on": "joinedOn",
            "score": "score",
        },
        # Deliberately different from the physical header order.
        "schema": {
            "score": "double",
            "id": "string",
            "joined_on": "date",
            "name": "string",
            "active": "boolean",
        },
        "options": {"header": "true", "enforceSchema": "false"},
    }
    valid = tmp_path / "valid.csv"
    valid.write_text(
        "id,name,joined_on,active,score\n"
        "person-1,Alice,2026-07-11,true,9.5\n",
        encoding="utf-8",
    )
    invalid = tmp_path / "invalid.csv"
    invalid.write_text(
        "id,name,joined_on,active,score\n"
        "person-2,Bob,2026-02-30,maybe,not-a-number\n",
        encoding="utf-8",
    )
    mismatch = tmp_path / "mismatch.csv"
    mismatch.write_text("id,name\nperson-3,Casey\n", encoding="utf-8")
    reordered = tmp_path / "reordered.csv"
    reordered.write_text(
        "score,active,name,id,joined_on\n8.25,false,Bob,person-2,2026-07-10\n",
        encoding="utf-8",
    )
    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text("id,name,name\nperson-3,Casey,Duplicate\n", encoding="utf-8")
    non_finite = tmp_path / "non-finite.csv"
    non_finite.write_text(
        "id,name,joined_on,active,score\nperson-4,Dana,2026-07-11,true,NaN\n",
        encoding="utf-8",
    )
    dotted = tmp_path / "dotted.csv"
    dotted.write_text("id,person.name\nperson-5,Élodie\n", encoding="utf-8")

    rows = builder._csv_records(source, [valid, reordered])
    rows.sort(key=lambda item: item["record_id"])
    row = rows[0]
    assert row["record_id"] == "person-1"
    assert row["title"] == "Alice"
    assert row["attributes"] == {
        "active": True,
        "joined_on": "2026-07-11",
        "score": 9.5,
    }
    assert rows[1]["record_id"] == "person-2"
    assert rows[1]["attributes"]["score"] == 8.25

    with pytest.raises(ValueError, match="strict double"):
        builder._csv_records(source, [non_finite])
    with pytest.raises(ValueError, match="header/schema mismatch"):
        builder._csv_records(source, [mismatch])
    with pytest.raises(ValueError, match="duplicate header"):
        builder._csv_records(source, [duplicate])

    dotted_source = {
        "id": "dotted",
        "kind": "csv",
        "id_field": "id",
        "title_field": "person.name",
        "fields": {"person.name": "name"},
        "schema": {"person.name": "string", "id": "string"},
        "options": {"header": "true"},
    }
    dotted_row = builder._csv_records(dotted_source, [dotted])[0]
    assert dotted_row["title"] == "Élodie"
    assert dotted_row["attributes"] == {"person.name": "Élodie"}

    with pytest.raises(ValueError, match="strict double"):
        builder._csv_records(source, [invalid])


def test_python_json_adapter_rejects_ambiguous_and_non_scalar_values(
    tmp_path: Path,
) -> None:
    builder = load_script("build_semantic_okf.py")
    source = {
        "id": "projects",
        "kind": "json",
        "id_field": "id",
        "title_field": "title",
        "fields": {"active": "active", "score": "score"},
        "schema": {
            "id": "string",
            "title": "string",
            "active": "boolean",
            "score": "double",
        },
        "options": {"multiLine": "false", "mode": "FAILFAST"},
    }
    valid = tmp_path / "valid.jsonl"
    valid.write_text(
        '{"id":"p-1","title":"Alpha","active":true,"score":9.5}\n'
        '{"score":8.25,"active":false,"title":"Beta","id":"p-2"}\n',
        encoding="utf-8",
    )
    rows = builder._json_records(source, [valid])
    assert [(row["record_id"], row["attributes"]) for row in rows] == [
        ("p-1", {"active": True, "score": 9.5}),
        ("p-2", {"active": False, "score": 8.25}),
    ]

    duplicate = tmp_path / "duplicate.jsonl"
    duplicate.write_text(
        '{"id":"p-1","id":"p-2","title":"Alpha","active":true,"score":1}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate JSON member 'id'"):
        builder._json_records(source, [duplicate])

    nonstandard = tmp_path / "nonstandard.jsonl"
    nonstandard.write_text(
        '{"id":"p-1","title":"Alpha","active":true,"score":NaN}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="non-standard JSON number 'NaN'"):
        builder._json_records(source, [nonstandard])

    scalar = tmp_path / "scalar.jsonl"
    scalar.write_text('"not-an-object"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="must be an object"):
        builder._json_records(source, [scalar])

    nested = tmp_path / "nested.jsonl"
    nested.write_text(
        '{"id":"p-1","title":"Alpha","active":true,"score":{"value":1}}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="field 'score' must be a scalar double"):
        builder._json_records(source, [nested])

    multiline_source = {**source, "options": {"multiLine": "true"}}
    multiline = tmp_path / "multiline.json"
    multiline.write_text(
        "[\n"
        '  {"id":"p-3","title":"Gamma","active":true,"score":7},\n'
        '  {"id":"p-4","title":"Delta","active":false,"score":6}\n'
        "]\n",
        encoding="utf-8",
    )
    assert [
        row["record_id"] for row in builder._json_records(multiline_source, [multiline])
    ] == ["p-3", "p-4"]


def test_python_build_shacl_failure_is_atomic(tmp_path: Path) -> None:
    manifest = write_fixture(tmp_path / "fixture")
    (manifest.parent / "sources" / "projects.jsonl").write_text(
        '{"id":"project-1","title":"Alpha"}\n', encoding="utf-8"
    )
    output = tmp_path / "python-invalid"

    result = run_skill_script(
        "build_semantic_okf.py",
        str(manifest),
        str(output),
        "--output-format",
        "json",
    )

    assert result.returncode == 2
    payload = json_line(result.stdout)
    assert "SHACL non-conformant" in payload["error"]
    assert not output.exists()
    assert not list(tmp_path.glob(".python-invalid-*"))


def refresh_fixture(
    tmp_path: Path,
) -> tuple[ModuleType, ModuleType, Path, dict[str, object], list[object], list[dict[str, object]], Path]:
    """Materialize a source-fresh bundle suitable for refresh unit tests."""

    core = load_core()
    refresher = load_script("refresh_semantic_okf.py")
    manifest_path = write_fixture(tmp_path / "fixture")
    manifest = core.load_manifest(manifest_path)
    records, summaries = make_records(core, manifest, manifest_path.parent)
    source_hashes = refresher._source_snapshot(manifest_path, manifest)
    summaries = [
        {**summary, "content_sha256": source_hashes[summary["id"]]}
        for summary in summaries
    ]
    records = [
        replace(record, source_content_sha256=source_hashes[record.source_id])
        for record in records
    ]
    output = tmp_path / "bundle"
    core.materialize_bundle(
        output,
        manifest,
        records,
        summaries,
        processor_info(records=len(records), sources=len(summaries)),
    )
    return core, refresher, manifest_path, manifest, records, summaries, output


def materializer_build(
    core: ModuleType,
    manifest: dict[str, object],
    records: list[object],
    summaries: list[dict[str, object]],
) -> object:
    """Return a deterministic build function for refresh transaction tests."""

    def build_candidate(_manifest_path: Path, output: Path) -> dict[str, object]:
        return core.materialize_bundle(
            output,
            manifest,
            records,
            summaries,
            processor_info(records=len(records), sources=len(summaries)),
        )

    return build_candidate


def test_refresh_noop_is_detected_without_replacing_current_tree(tmp_path: Path) -> None:
    core, refresher, manifest_path, manifest, records, summaries, output = refresh_fixture(tmp_path)
    before = refresher._tree_sha256(output)

    report = refresher.refresh_bundle(
        manifest_path,
        output,
        build_fn=materializer_build(core, manifest, records, summaries),
    )

    assert report["status"] == "unchanged"
    assert report["changes"]["records"] == {
        "added": [],
        "removed": [],
        "changed": [],
        "unchanged_count": 6,
    }
    assert refresher._tree_sha256(output) == before
    assert not list(tmp_path.glob(".sokf-*"))
    assert not list(tmp_path.glob(".*.refresh.*"))


def test_refresh_reports_and_guards_record_add_change_remove(tmp_path: Path) -> None:
    core, refresher, manifest_path, manifest, records, summaries, output = refresh_fixture(tmp_path)
    before = refresher._tree_sha256(output)
    people_path = manifest_path.parent / "sources" / "people.csv"
    people_path.write_text(
        "id,name,role\nperson-1,Alice,Architect\nperson-3,Carol,Analyst\n",
        encoding="utf-8",
    )
    source_hashes = refresher._source_snapshot(manifest_path, manifest)
    candidate_summaries = [
        {**summary, "content_sha256": source_hashes[summary["id"]]}
        for summary in summaries
    ]
    summary_by_id = {summary["id"]: summary for summary in candidate_summaries}
    source_specs = core.source_by_id(manifest)
    retained = [record for record in records if record.source_id != "people"]

    def person(record_id: str, name: str, role: str) -> object:
        return core.finalize_record(
            {
                "source_id": "people",
                "source_kind": "csv",
                "source_path": people_path.as_uri(),
                "record_id": record_id,
                "subject_iri": "",
                "title": name,
                "body": f"# {name}\n\n- **name**: {name}\n- **role**: {role}",
                "attributes": {"name": name, "role": role},
            },
            source_specs["people"],
            summary_by_id["people"],
            manifest,
            manifest_path.parent,
        )

    candidate_records = [*retained, person("person-1", "Alice", "Architect"), person("person-3", "Carol", "Analyst")]
    candidate_build = materializer_build(
        core, manifest, candidate_records, candidate_summaries
    )

    check = refresher.refresh_bundle(
        manifest_path,
        output,
        check=True,
        build_fn=candidate_build,
    )
    assert check["status"] == "changes-pending"
    assert check["changes"]["records"]["removed"] == [
        "concepts/people/person-2-aa7334ec51"
    ]
    assert {item["code"] for item in check["blockers"]} == {
        "record-removal-not-allowed"
    }
    assert refresher._tree_sha256(output) == before

    with pytest.raises(refresher.RefreshError, match="allow-record-removals") as blocked:
        refresher.refresh_bundle(
            manifest_path,
            output,
            build_fn=candidate_build,
        )
    assert blocked.value.code == "record-removal-not-allowed"
    assert refresher._tree_sha256(output) == before

    with pytest.raises(refresher.RefreshError, match="reviewed preview") as diverged:
        refresher.refresh_bundle(
            manifest_path,
            output,
            allow_record_removals=True,
            expected_current_tree_sha256=before,
            expected_candidate_tree_sha256="0" * 64,
            build_fn=candidate_build,
        )
    assert diverged.value.code == "candidate-diverged"
    assert refresher._tree_sha256(output) == before

    report = refresher.refresh_bundle(
        manifest_path,
        output,
        allow_record_removals=True,
        expected_current_tree_sha256=check["previous"]["tree_sha256"],
        expected_candidate_tree_sha256=check["current"]["tree_sha256"],
        build_fn=candidate_build,
    )
    assert report["status"] == "updated"
    assert report["changes"]["records"]["added"] == [
        "concepts/people/person-3-04852fea64"
    ]
    assert report["changes"]["records"]["changed"] == [
        "concepts/people/person-1-57496249fe"
    ]
    assert core.validate_semantic_bundle(output).valid
    ledger = refresher._records_by_id(output)
    assert {
        "concepts/people/person-1-57496249fe",
        "concepts/people/person-3-04852fea64",
    }.issubset(ledger)
    assert "concepts/people/person-2-aa7334ec51" not in ledger


def test_refresh_requires_new_version_iri_for_semantic_plan_change(tmp_path: Path) -> None:
    core, refresher, manifest_path, manifest, records, summaries, output = refresh_fixture(tmp_path)
    changed = copy.deepcopy(manifest)
    changed["rules"][0]["message"] = "A revised reviewed policy code rule."
    manifest_path.write_text(json.dumps(changed, indent=2) + "\n", encoding="utf-8")
    candidate = materializer_build(core, changed, records, summaries)

    check = refresher.refresh_bundle(
        manifest_path,
        output,
        check=True,
        build_fn=candidate,
    )
    assert {item["code"] for item in check["blockers"]} == {
        "plan-change-not-allowed",
        "ontology-version-reuse",
    }
    with pytest.raises(refresher.RefreshError) as blocked:
        refresher.refresh_bundle(
            manifest_path,
            output,
            allow_plan_change=True,
            build_fn=candidate,
        )
    assert blocked.value.code == "ontology-version-reuse"


def test_refresh_adds_new_declared_source_after_reviewed_plan_change(tmp_path: Path) -> None:
    core, refresher, manifest_path, manifest, records, summaries, output = refresh_fixture(tmp_path)
    changed = copy.deepcopy(manifest)
    changed["bundle"]["version_iri"] = "https://example.org/ontology/research/1.1.0"
    added_source = copy.deepcopy(next(source for source in changed["sources"] if source["id"] == "people"))
    added_source["id"] = "reviewers"
    added_source["path"] = "sources/reviewers.csv"
    changed["sources"].append(added_source)
    reviewers_path = manifest_path.parent / "sources" / "reviewers.csv"
    reviewers_path.write_text("id,name,role\nreviewer-1,Dana,Approver\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(changed, indent=2) + "\n", encoding="utf-8")
    source_hash = refresher._source_snapshot(manifest_path, changed)["reviewers"]
    summary = {
        "id": "reviewers",
        "kind": "csv",
        "path": "sources/reviewers.csv",
        "content_sha256": source_hash,
        "allow_empty": False,
    }
    added_record = core.finalize_record(
        {
            "source_id": "reviewers",
            "source_kind": "csv",
            "source_path": reviewers_path.as_uri(),
            "record_id": "reviewer-1",
            "subject_iri": "",
            "title": "Dana",
            "body": "# Dana\n\n- **name**: Dana\n- **role**: Approver",
            "attributes": {"name": "Dana", "role": "Approver"},
        },
        added_source,
        summary,
        changed,
        manifest_path.parent,
    )
    candidate_records = [*records, added_record]
    candidate_summaries = [*summaries, summary]
    candidate = materializer_build(core, changed, candidate_records, candidate_summaries)

    check = refresher.refresh_bundle(manifest_path, output, check=True, build_fn=candidate)

    assert {item["code"] for item in check["blockers"]} == {"plan-change-not-allowed"}
    assert check["changes"]["records"]["added"] == [
        "concepts/reviewers/reviewer-1-3b73583306"
    ]
    report = refresher.refresh_bundle(
        manifest_path,
        output,
        allow_plan_change=True,
        expected_current_tree_sha256=check["previous"]["tree_sha256"],
        expected_candidate_tree_sha256=check["current"]["tree_sha256"],
        build_fn=candidate,
    )

    assert report["status"] == "updated"
    assert core.validate_semantic_bundle(output).valid
    source_manifest = json.loads(
        (output / "semantic" / "source-manifest.json").read_text(encoding="utf-8")
    )
    ledger = refresher._records_by_id(output)
    assert "reviewers" in {source["id"] for source in source_manifest["sources"]}
    assert "concepts/reviewers/reviewer-1-3b73583306" in ledger


def test_refresh_removes_declared_source_without_leaving_stale_artifacts(tmp_path: Path) -> None:
    core, refresher, manifest_path, manifest, records, summaries, output = refresh_fixture(tmp_path)
    changed = copy.deepcopy(manifest)
    changed["bundle"]["version_iri"] = "https://example.org/ontology/research/1.1.0"
    changed["sources"] = [source for source in changed["sources"] if source["id"] != "projects"]
    manifest_path.write_text(json.dumps(changed, indent=2) + "\n", encoding="utf-8")
    candidate_records = [record for record in records if record.source_id != "projects"]
    candidate_summaries = [summary for summary in summaries if summary["id"] != "projects"]
    candidate = materializer_build(core, changed, candidate_records, candidate_summaries)

    check = refresher.refresh_bundle(manifest_path, output, check=True, build_fn=candidate)

    assert {item["code"] for item in check["blockers"]} == {
        "plan-change-not-allowed",
        "record-removal-not-allowed",
    }
    report = refresher.refresh_bundle(
        manifest_path,
        output,
        allow_plan_change=True,
        allow_record_removals=True,
        expected_current_tree_sha256=check["previous"]["tree_sha256"],
        expected_candidate_tree_sha256=check["current"]["tree_sha256"],
        build_fn=candidate,
    )

    assert report["status"] == "updated"
    assert report["changes"]["records"]["removed"] == [
        "concepts/projects/project-1-a33e35d302",
        "concepts/projects/project-2-2d1eec846f",
    ]
    assert core.validate_semantic_bundle(output).valid
    plan = json.loads((output / "semantic" / "semantic-plan.json").read_text(encoding="utf-8"))
    ledger = refresher._records_by_id(output)
    data = (output / "semantic" / "data.ttl").read_text(encoding="utf-8")
    assert "projects" not in {source["id"] for source in plan["sources"]}
    assert not any(concept_id.startswith("concepts/projects/") for concept_id in ledger)
    assert "resource/projects/" not in data
    assert not (output / "concepts" / "projects").exists()


def test_recovery_restores_old_snapshot_after_first_rename(tmp_path: Path) -> None:
    core, refresher, manifest_path, manifest, records, summaries, output = refresh_fixture(tmp_path)
    old_hash = refresher._tree_sha256(output)
    token = "a" * 32
    candidate = output.parent / f".sokf-{token}.stage"
    materializer_build(core, manifest, records, summaries)(manifest_path, candidate)
    new_hash = refresher._tree_sha256(candidate)
    backup = output.parent / f".sokf-{token}.backup"
    journal = refresher._journal_path(output)
    refresher._write_json_atomic(
        journal,
        {
            "schema_version": refresher.TRANSACTION_SCHEMA_VERSION,
            "output": output.name,
            "candidate": candidate.name,
            "backup": backup.name,
            "old_tree_sha256": old_hash,
            "new_tree_sha256": new_hash,
            "state": "old_moved",
        },
    )
    output.replace(backup)

    report = refresher.recover_bundle(output)

    assert report["status"] == "recovered"
    assert report["resolution"] == "rollback"
    assert refresher._tree_sha256(output) == old_hash
    assert not candidate.exists()
    assert not backup.exists()
    assert not journal.exists()


def test_python_refresh_reprocesses_sources_and_publishes_new_record(tmp_path: Path) -> None:
    manifest = write_fixture(tmp_path / "fixture")
    output = tmp_path / "bundle"
    built = run_skill_script(
        "build_semantic_okf.py",
        str(manifest),
        str(output),
        "--output-format",
        "json",
    )
    assert built.returncode == 0, f"{built.stdout}\n{built.stderr}"
    people = manifest.parent / "sources" / "people.csv"
    people.write_text(
        "id,name,role\nperson-2,Bob,Reviewer\nperson-1,Alice,Engineer\nperson-3,Carol,Analyst\n",
        encoding="utf-8",
    )

    refreshed = run_skill_script(
        "refresh_semantic_okf.py",
        "update",
        str(manifest),
        str(output),
        "--output-format",
        "json",
    )
    assert refreshed.returncode == 0, f"{refreshed.stdout}\n{refreshed.stderr}"
    report = json_line(refreshed.stdout)
    assert report["status"] == "updated"
    assert report["changes"]["records"]["added"] == [
        "concepts/people/person-3-04852fea64"
    ]
    records = [
        json.loads(line)
        for line in (output / "semantic" / "records.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    added = next(record for record in records if record["record_id"] == "person-3")
    assert added["attributes"] == {"name": "Carol", "role": "Analyst"}
    assert not refresher_artifacts(output)


def refresher_artifacts(output: Path) -> list[Path]:
    """Return refresh transaction artifacts left next to one output."""

    return [
        path
        for path in output.parent.iterdir()
        if path.name.startswith(".sokf-") or path.name.startswith(f".{output.name}.refresh")
    ]
