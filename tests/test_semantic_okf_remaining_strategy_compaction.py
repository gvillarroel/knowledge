from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SKILLS = (
    "build-semantic-okf-graphify-next",
    "build-semantic-okf-harbor-graphify",
    "build-semantic-okf-rust-mallet",
    "build-semantic-okf-rust-mallet-evolved",
    "build-semantic-okf-tantivy",
    "build-semantic-okf-tika-mallet",
)
CONSULT_SNAPSHOTS = (
    "consult-semantic-okf-graphify/scripts/_graphify_snapshot.py",
    "consult-semantic-okf-harbor-graphify/scripts/_graphify_snapshot.py",
    "consult-semantic-okf-rust-mallet/scripts/_rust_mallet_snapshot.py",
    "consult-semantic-okf-rust-mallet-evolved/scripts/_rust_mallet_snapshot.py",
    "consult-semantic-okf-tantivy/scripts/_tantivy_snapshot.py",
    "consult-semantic-okf-tika-mallet/scripts/_tika_mallet_snapshot.py",
    "consult-semantic-okf-tika-mallet-bounded/scripts/_tika_mallet_snapshot.py",
    "consult-semantic-okf-tika-mallet-tantivy/scripts/_tika_mallet_tantivy_snapshot.py",
)
GRAPHIFY_STRATEGIES = (
    (
        "build-semantic-okf-graphify",
        "consult-semantic-okf-graphify/scripts/_graphify_snapshot.py",
    ),
    (
        "build-semantic-okf-graphify-next",
        "consult-semantic-okf-graphify/scripts/_graphify_snapshot.py",
    ),
    (
        "build-semantic-okf-harbor-graphify",
        "consult-semantic-okf-harbor-graphify/scripts/_graphify_snapshot.py",
    ),
)
SEMANTIC_ARTIFACTS = (
    "semantic/records.jsonl",
    "semantic/semantic-plan.json",
    "semantic/ontology.ttl",
    "semantic/data.ttl",
    "semantic/shapes.ttl",
    "semantic/provenance.ttl",
    "semantic/validation-report.ttl",
)


def _load_module(path: Path, name: str, *, import_root: Path | None = None) -> ModuleType:
    if import_root is not None:
        sys.path.insert(0, str(import_root))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if import_root is not None:
            sys.path.remove(str(import_root))


def _load_builder(skill_name: str) -> tuple[ModuleType, ModuleType]:
    scripts = REPO_ROOT / "skills" / skill_name / "scripts"
    sys.modules.pop("_semantic_okf", None)
    core = _load_module(scripts / "_semantic_okf.py", "_semantic_okf")
    builder = _load_module(
        scripts / "_build_semantic_okf_core.py",
        f"test_compaction_{skill_name.replace('-', '_')}",
        import_root=scripts,
    )
    return core, builder


def _write_structured_fixture(root: Path) -> Path:
    sources = root / "sources"
    sources.mkdir(parents=True)
    (sources / "records.csv").write_text(
        "id,name\nrow-2,Beta evidence\nrow-1,Alpha evidence\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Remaining strategy compaction fixture",
            "description": "Two structured records with complete evidence bodies.",
            "base_iri": "https://example.org/remaining-compaction/",
            "ontology_iri": "https://example.org/ontology/remaining-compaction",
            "version_iri": "https://example.org/ontology/remaining-compaction/1.0.0",
            "prefix": "compact",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "EvidenceRecord", "label": "evidence record"}],
            "properties": [
                {
                    "name": "name",
                    "kind": "datatype",
                    "domain": "EvidenceRecord",
                    "range": "xsd:string",
                }
            ],
        },
        "rules": [
            {
                "name": "EvidenceNameRule",
                "target_class": "EvidenceRecord",
                "path": "name",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Every evidence record requires a name.",
                "basis": {
                    "kind": "operational-policy",
                    "references": ["COMPACTION-1"],
                },
            }
        ],
        "sources": [
            {
                "id": "records",
                "kind": "csv",
                "path": "sources/records.csv",
                "concept_type": "Evidence Record",
                "ontology_class": "EvidenceRecord",
                "id_field": "id",
                "title_field": "name",
                "fields": {"name": "name"},
                "schema": {"id": "string", "name": "string"},
                "options": {"header": "true", "enforceSchema": "false"},
            }
        ],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


@pytest.mark.parametrize("skill_name", BUILD_SKILLS)
def test_remaining_builder_cores_pack_files_without_logical_drift(
    tmp_path: Path, skill_name: str
) -> None:
    core, builder = _load_builder(skill_name)
    fixture = tmp_path / skill_name
    manifest = _write_structured_fixture(fixture)
    legacy = fixture / "legacy"
    packed = fixture / "packed"

    legacy_report = builder.build(manifest, legacy)
    packed_report = builder.build(
        manifest,
        packed,
        concept_layout=core.CONCEPT_LAYOUT_SOURCE_PACKED,
    )

    assert legacy_report["summary"]["records"] == 2
    assert packed_report["summary"] == {
        **legacy_report["summary"],
        "concepts": 1,
    }
    assert len(list((legacy / "concepts").rglob("*.md"))) == 2
    assert list((packed / "concepts").rglob("*.md")) == [
        packed / "concepts" / "records.md"
    ]
    for relative in SEMANTIC_ARTIFACTS:
        assert (legacy / relative).read_bytes() == (packed / relative).read_bytes()
    assert core.validate_semantic_bundle(packed).valid is True

    records = [
        json.loads(line)
        for line in (packed / "semantic" / "records.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    collection = (packed / "concepts" / "records.md").read_text(encoding="utf-8")
    for record in records:
        assert record["body"] in collection
        assert f'<a id="record-{record["record_sha256"][:16]}"></a>' in collection


@pytest.mark.parametrize("relative", CONSULT_SNAPSHOTS)
def test_remaining_consultants_reject_packed_anchor_or_body_drift(
    tmp_path: Path, relative: str
) -> None:
    path = REPO_ROOT / "skills" / relative
    module = _load_module(
        path,
        f"test_packed_consult_{path.parent.parent.name.replace('-', '_')}_{path.stem}",
        import_root=path.parent,
    )
    digest = "a" * 64
    body = "# Exact evidence\n\nThe complete authoritative record body."
    marker = f'<a id="record-{digest[:16]}"></a>'
    concept = tmp_path / f"{path.parent.parent.name}.md"
    concept.write_text(
        f"---\ntype: Semantic OKF Record Collection\n---\n\n{marker}\n\n{body}\n",
        encoding="utf-8",
    )
    record = {"record_sha256": digest, "body": body, "title": "Exact evidence"}

    module._validate_packed_record(concept, record, "test record")

    concept.write_text(
        f"---\ntype: Semantic OKF Record Collection\n---\n\n{marker}\n\nTampered.\n",
        encoding="utf-8",
    )
    with pytest.raises(module.SnapshotError, match="body differs"):
        module._validate_packed_record(concept, record, "test record")


@pytest.mark.parametrize(("build_skill", "consult_snapshot"), GRAPHIFY_STRATEGIES)
def test_graphify_compaction_preserves_projection_and_query_rankings(
    tmp_path: Path, build_skill: str, consult_snapshot: str
) -> None:
    fixture = tmp_path / build_skill
    manifest = _write_structured_fixture(fixture)
    scripts = REPO_ROOT / "skills" / build_skill / "scripts"
    legacy = fixture / "legacy-projection"
    packed = fixture / "packed-projection"
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    for output, layout in ((legacy, "record-per-file-v1"), (packed, "source-packed-v1")):
        result = subprocess.run(
            [
                sys.executable,
                str(scripts / "build_semantic_okf_graphify.py"),
                str(manifest),
                str(output),
                "--concept-layout",
                layout,
                "--output-format",
                "json",
            ],
            cwd=scripts,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
            env=environment,
        )
        assert result.returncode == 0, result.stderr or result.stdout

    assert (legacy / "retrieval" / "graphify" / "graph.json").read_bytes() == (
        packed / "retrieval" / "graphify" / "graph.json"
    ).read_bytes()
    assert len(list((legacy / "concepts").rglob("*.md"))) == 2
    assert len(list((packed / "concepts").rglob("*.md"))) == 1
    assert not (packed / ".graphify-views").exists()

    snapshot_path = REPO_ROOT / "skills" / consult_snapshot
    module = _load_module(
        snapshot_path,
        f"test_graphify_compaction_{build_skill.replace('-', '_')}",
        import_root=snapshot_path.parent,
    )
    legacy_snapshot = module.Snapshot(legacy)
    packed_snapshot = module.Snapshot(packed)
    legacy_results = legacy_snapshot.search("Alpha evidence", top_k=10)["records"]
    packed_results = packed_snapshot.search(
        "Alpha evidence", top_k=10, show_content=True
    )["records"]

    def stable(result: dict[str, object]) -> tuple[object, ...]:
        return (
            result["source_id"],
            result["record_id"],
            result["record_sha256"],
            result["concept_path"],
            result["distance"],
            result["graphify_node_id"],
            result["graphify_score"],
        )

    assert [stable(result) for result in legacy_results] == [
        stable(result) for result in packed_results
    ]
    assert packed_results
    assert all(result["evidence"]["kind"] == "concept-collection" for result in packed_results)
    records = {
        (record["source_id"], record["record_id"]): record
        for record in packed_snapshot.records
    }
    for result in packed_results:
        record = records[(result["source_id"], result["record_id"])]
        assert result["content"] == record["body"].rstrip() + "\n"
