from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "extract-ontologies"
SCRIPTS = SKILL_ROOT / "scripts"


def load_script(name: str) -> ModuleType:
    """Load a repo-local skill script without requiring a Python package name."""

    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(f"test_{path.stem}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_skill_metadata_is_prebuild_ontology_authoring_only() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    frontmatter = skill.split("---", 2)[1]

    assert "name: extract-ontologies" in frontmatter
    assert "before Semantic OKF materialization" in frontmatter
    assert "ontology learning" in frontmatter
    assert "Do not use it to create, expand, refresh, or repair a Semantic OKF snapshot" in frontmatter
    assert "or to consult an existing knowledge bundle" in frontmatter
    assert 'short_description: "Author reviewed RDF/OWL ontologies"' in metadata
    assert "before Semantic OKF materialization" in metadata
    assert "$build-semantic-okf" not in metadata
    assert "$consult-semantic-okf" not in metadata


def test_scaffold_builds_complete_bundle_without_overwriting(tmp_path: Path) -> None:
    scaffold = load_script("scaffold_ontology_bundle.py")
    parser = scaffold.build_parser()
    args = parser.parse_args(
        [
            str(tmp_path / "permit-model"),
            "--ontology-iri",
            "https://example.org/ontology/permits",
            "--version-iri",
            "https://example.org/ontology/permits/1.0.0",
            "--prefix",
            "permit",
            "--title",
            'Permit "review" ontology',
            "--owl-profile",
            "rl",
        ]
    )
    payloads = scaffold.build_files(args, created=date(2026, 7, 10))
    output = args.output

    scaffold.write_bundle(output, payloads, force=False)

    assert {path.name for path in output.iterdir()} == set(scaffold.TARGET_FILES)
    ontology = (output / "ontology.ttl").read_text(encoding="utf-8")
    assert "owl:versionIRI <https://example.org/ontology/permits/1.0.0>" in ontology
    assert 'dcterms:title "Permit \\"review\\" ontology"' in ontology
    assert 'dcterms:created "2026-07-10"^^xsd:date' in ontology
    header = (output / "evidence.csv").read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("assertion_id,kind,subject,predicate,object")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        scaffold.write_bundle(output, payloads, force=False)


@pytest.mark.parametrize(
    "value",
    ["relative/path", "ftp://example.org/model", "https://bad host/model", ""],
)
def test_scaffold_rejects_nonportable_ontology_iris(value: str) -> None:
    scaffold = load_script("scaffold_ontology_bundle.py")

    with pytest.raises(Exception, match="IRI"):
        scaffold.absolute_iri(value)


def test_scaffold_uses_conservative_prefixes_and_escapes_literals() -> None:
    scaffold = load_script("scaffold_ontology_bundle.py")

    assert scaffold.PREFIX_RE.fullmatch("model-v1")
    assert not scaffold.PREFIX_RE.fullmatch("model.")
    assert scaffold.turtle_literal('A\t"quoted" value') == 'A\\t\\"quoted\\" value'


def test_validator_rejects_remote_paths_and_dataset_union(tmp_path: Path) -> None:
    validator = load_script("validate_semantic_artifacts.py")
    graph = tmp_path / "model.trig"
    graph.write_text("@prefix ex: <https://example.org/> . ex:g { ex:s ex:p ex:o . }", encoding="utf-8")

    with pytest.raises(validator.ValidationInputError, match="remote input"):
        validator.local_file("https://example.org/data.ttl")
    with pytest.raises(validator.ValidationInputError, match="RDF dataset"):
        validator.resolve_rdf_format(graph, "auto", lambda _name: "trig")


def test_validator_blocks_external_jsonld_contexts() -> None:
    validator = load_script("validate_semantic_artifacts.py")

    assert validator.contains_external_jsonld_context(
        {"@context": "https://example.org/context.jsonld", "name": "Example"}
    )
    assert validator.contains_external_jsonld_context(
        {"@context": {"@import": "context.jsonld", "name": "https://schema.org/name"}}
    )
    assert not validator.contains_external_jsonld_context(
        {"@context": {"name": "https://schema.org/name"}, "name": "Example"}
    )


def test_validator_json_error_contract_needs_no_optional_dependencies(capsys: pytest.CaptureFixture[str]) -> None:
    validator = load_script("validate_semantic_artifacts.py")

    exit_code = validator.main(["--output-format", "json"])

    result = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert result["schema_version"] == "1.0"
    assert result["status"] == "error"
    assert result["errors"] == ["provide at least one --data, --ontology, or --shapes file"]


def test_validator_dependencies_are_exactly_pinned() -> None:
    direct = (SCRIPTS / "requirements.in").read_text(encoding="utf-8").splitlines()
    compiled = (SCRIPTS / "requirements.txt").read_text(encoding="utf-8")

    assert direct == [
        "rdflib[html]==7.6.0",
        "pyshacl==0.40.0",
        "owlrl==7.6.2",
    ]
    for requirement in ("rdflib==7.6.0", "pyshacl==0.40.0", "owlrl==7.6.2"):
        assert requirement in compiled


def test_validator_runs_conforming_and_nonconforming_shacl(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rdflib = pytest.importorskip("rdflib")
    pytest.importorskip("pyshacl")
    validator = load_script("validate_semantic_artifacts.py")
    ontology = tmp_path / "ontology.ttl"
    data = tmp_path / "data.ttl"
    shapes = tmp_path / "shapes.ttl"
    report = tmp_path / "report.ttl"
    ontology.write_text(
        "@prefix ex: <https://example.org/> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "ex:Person a owl:Class .\n",
        encoding="utf-8",
    )
    data.write_text(
        "@prefix ex: <https://example.org/> .\n"
        'ex:alice a ex:Person ; ex:name "Alice" .\n',
        encoding="utf-8",
    )
    shapes.write_text(
        "@prefix ex: <https://example.org/> .\n"
        "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
        "ex:PersonShape a sh:NodeShape ; sh:targetClass ex:Person ;\n"
        "  sh:property [ sh:path ex:name ; sh:minCount 1 ] .\n",
        encoding="utf-8",
    )

    conforming_code = validator.main(
        [
            "--data",
            str(data),
            "--ontology",
            str(ontology),
            "--shapes",
            str(shapes),
            "--report",
            str(report),
            "--output-format",
            "json",
        ]
    )
    conforming = json.loads(capsys.readouterr().out)

    assert conforming_code == 0
    assert conforming["status"] == "conformant"
    assert conforming["summary"]["conforms"] is True
    assert len(rdflib.Graph().parse(report, format="turtle")) > 0

    data.write_text(
        "@prefix ex: <https://example.org/> .\nex:alice a ex:Person .\n",
        encoding="utf-8",
    )
    nonconforming_code = validator.main(
        [
            "--data",
            str(data),
            "--ontology",
            str(ontology),
            "--shapes",
            str(shapes),
            "--output-format",
            "json",
        ]
    )
    nonconforming = json.loads(capsys.readouterr().out)

    assert nonconforming_code == 1
    assert nonconforming["status"] == "nonconformant"
    assert nonconforming["summary"]["violations"] == 1
    assert nonconforming["results"][0]["focus_node"] == {
        "type": "iri",
        "value": "https://example.org/alice",
    }
