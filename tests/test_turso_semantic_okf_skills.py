from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SKILL = REPO_ROOT / "skills" / "build-semantic-okf-turso"
CONSULT_SKILL = REPO_ROOT / "skills" / "consult-semantic-okf-turso"


def load_reader() -> ModuleType:
    """Load the standalone read-only support module for unit checks."""

    path = CONSULT_SKILL / "scripts" / "_turso_read.py"
    spec = importlib.util.spec_from_file_location("test_turso_read_support", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_fixture(root: Path) -> Path:
    """Write one reviewed Markdown source and a minimal semantic manifest."""

    sources = root / "sources"
    sources.mkdir(parents=True)
    (sources / "alpha.md").write_text(
        "---\ntitle: Alpha Document\ncode: DOC-1\n---\n\n"
        "# Alpha Document\n\nThe alpha document explains local-first knowledge retrieval.\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Turso semantic fixture",
            "description": "One deterministic document stored in Turso Database.",
            "base_iri": "https://example.org/turso-fixture/",
            "ontology_iri": "https://example.org/ontology/turso-fixture",
            "version_iri": "https://example.org/ontology/turso-fixture/1.0.0",
            "prefix": "fixture",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "Document", "label": "document"}],
            "properties": [
                {
                    "name": "code",
                    "kind": "datatype",
                    "domain": "Document",
                    "range": "xsd:string",
                }
            ],
        },
        "rules": [
            {
                "name": "DocumentCodeRule",
                "target_class": "Document",
                "path": "code",
                "min_count": 1,
                "max_count": 1,
                "datatype": "xsd:string",
                "message": "Each accepted document requires one code.",
                "basis": {"kind": "operational-policy", "references": ["DOC-1"]},
            }
        ],
        "sources": [
            {
                "id": "documents",
                "kind": "markdown",
                "path": "sources/*.md",
                "concept_type": "Document",
                "ontology_class": "Document",
                "fields": {"code": "code"},
            }
        ],
    }
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def run_script(
    skill: Path,
    script: str,
    *args: str,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    """Run one copied skill entry point without repository import paths."""

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(skill / "scripts" / script), *args],
        cwd=skill,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
        env=environment,
    )


def json_output(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    """Parse the single JSON payload emitted by a skill command."""

    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    return payload


def file_sha256(path: Path) -> str:
    """Return one file digest for immutability checks."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_turso_skills_declare_distinct_standalone_authorities() -> None:
    build = (BUILD_SKILL / "SKILL.md").read_text(encoding="utf-8")
    consult = (CONSULT_SKILL / "SKILL.md").read_text(encoding="utf-8")
    build_requirements = (BUILD_SKILL / "scripts" / "requirements.in").read_text(
        encoding="utf-8"
    )
    consult_requirements = (CONSULT_SKILL / "scripts" / "requirements.in").read_text(
        encoding="utf-8"
    )

    assert "name: build-semantic-okf-turso" in build
    assert "name: consult-semantic-okf-turso" in consult
    assert "## Standalone boundary" in build
    assert "## Standalone boundary" in consult
    assert "knowledge.db" in build and "knowledge.db" in consult
    assert "pyturso==0.6.1" in build_requirements
    assert consult_requirements.strip() == "pyturso==0.6.1"
    assert "PRAGMA query_only=1" in consult
    assert "materialize_turso_store.py" in build
    assert "refresh_semantic_okf.py" not in consult
    assert "TODO" not in build and "TODO" not in consult
    assert "import sqlite3" not in "\n".join(
        path.read_text(encoding="utf-8")
        for root in (BUILD_SKILL, CONSULT_SKILL)
        for path in (root / "scripts").glob("*.py")
    )


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM records",
        "WITH removed AS (DELETE FROM records RETURNING *) SELECT * FROM removed",
        "SELECT * FROM records; SELECT * FROM sources",
        "PRAGMA integrity_check",
        "SELECT readfile('secret.txt')",
        "SELECT load_extension('extension')",
    ],
)
def test_sql_guard_rejects_mutation_admin_and_file_surfaces(sql: str) -> None:
    reader = load_reader()

    with pytest.raises(reader.TursoQueryError) as raised:
        reader.validate_read_only_sql(sql)

    assert raised.value.code == "query-rejected"
    assert raised.value.exit_code == 3


def test_sql_guard_accepts_read_queries_comments_literals_and_parameters() -> None:
    reader = load_reader()

    assert reader.validate_read_only_sql("-- discovery\nSELECT 'DELETE' AS label")
    assert reader.validate_read_only_sql(
        "WITH selected AS (SELECT * FROM records) SELECT * FROM selected;"
    ).endswith("selected")
    assert reader.parse_parameters(
        ['source="documents"', "minimum=2", "active=true"]
    ) == {
        "source": "documents",
        "minimum": 2,
        "active": True,
    }
    with pytest.raises(reader.TursoQueryError, match="duplicate SQL parameter"):
        reader.parse_parameters(["source=1", "source=2"])


def test_copied_turso_skills_build_validate_query_refresh_and_detect_tampering(
    tmp_path: Path,
) -> None:
    pytest.importorskip("turso")
    packages = tmp_path / "packages"
    copied_build = packages / BUILD_SKILL.name
    copied_consult = packages / CONSULT_SKILL.name
    shutil.copytree(
        BUILD_SKILL, copied_build, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    shutil.copytree(
        CONSULT_SKILL,
        copied_consult,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    fixture = tmp_path / "fixture"
    manifest = write_fixture(fixture)
    first = tmp_path / "release-one"
    second = tmp_path / "release-two"

    build = run_script(
        copied_build,
        "build_semantic_okf.py",
        str(manifest),
        str(first),
        "--output-format",
        "json",
    )
    assert build.returncode == 0, build.stderr or build.stdout
    build_payload = json_output(build)
    database = first / "semantic" / "knowledge.db"
    assert build_payload["turso"]["summary"] == {
        "artifacts": 10,
        "attributes": 1,
        "concepts": 1,
        "records": 1,
        "sources": 1,
        "statements": 39,
    }
    assert database.is_file()
    assert [path.name for path in database.parent.glob("*knowledge.db*")] == [
        "knowledge.db"
    ]

    validation = run_script(
        copied_build,
        "validate_turso_store.py",
        str(database),
        "--bundle",
        str(first),
        "--output-format",
        "json",
    )
    assert validation.returncode == 0, validation.stderr or validation.stdout
    validation_payload = json_output(validation)
    assert validation_payload["valid"] is True

    before = file_sha256(database)
    records = run_script(
        copied_consult,
        "query_turso_knowledge.py",
        str(database),
        "records",
        "--attribute",
        "code",
        '"DOC-1"',
        "--show-content",
        "--format",
        "json",
    )
    assert records.returncode == 0, records.stderr or records.stdout
    records_payload = json_output(records)
    assert records_payload["returned"] == 1
    record = records_payload["records"][0]
    assert record["title"] == "Alpha Document"
    assert "local-first knowledge retrieval" in record["content"]

    sql = run_script(
        copied_consult,
        "query_turso_knowledge.py",
        str(database),
        "sql",
        "--query",
        "SELECT title, concept_path FROM records WHERE source_id = :source",
        "--param",
        'source="documents"',
        "--format",
        "json",
    )
    assert sql.returncode == 0, sql.stderr or sql.stdout
    assert json_output(sql)["rows"] == [
        {
            "title": "Alpha Document",
            "concept_path": record["concept_path"],
        }
    ]

    rejected = run_script(
        copied_consult,
        "query_turso_knowledge.py",
        str(database),
        "sql",
        "--query",
        "DELETE FROM records",
        "--format",
        "json",
    )
    assert rejected.returncode == 3
    assert "query-rejected" in rejected.stderr
    assert file_sha256(database) == before
    assert [path.name for path in database.parent.glob("*knowledge.db*")] == [
        "knowledge.db"
    ]

    rebuild = run_script(
        copied_build,
        "build_semantic_okf.py",
        str(manifest),
        str(second),
        "--output-format",
        "json",
    )
    assert rebuild.returncode == 0, rebuild.stderr or rebuild.stdout
    assert (
        json_output(rebuild)["turso"]["logical_sha256"]
        == build_payload["turso"]["logical_sha256"]
    )

    refresh = run_script(
        copied_build,
        "refresh_semantic_okf.py",
        "update",
        str(manifest),
        str(first),
        "--check",
        "--output-format",
        "json",
    )
    assert refresh.returncode == 0, refresh.stderr or refresh.stdout
    refresh_payload = json_output(refresh)
    assert refresh_payload["status"] == "unchanged"
    assert (
        refresh_payload["previous"]["tree_sha256"]
        == refresh_payload["current"]["tree_sha256"]
    )

    tampered = tmp_path / "tampered.db"
    shutil.copy2(database, tampered)
    turso = importlib.import_module("turso")
    connection = turso.connect(str(tampered))
    connection.execute("UPDATE records SET title = ?", ("Tampered",))
    connection.commit()
    connection.close()
    for suffix in ("-wal", "-shm", ".wal", ".shm"):
        sidecar = Path(f"{tampered}{suffix}")
        if sidecar.exists():
            assert sidecar.stat().st_size == 0
            sidecar.unlink()
    invalid = run_script(
        copied_build,
        "validate_turso_store.py",
        str(tampered),
        "--output-format",
        "json",
    )
    assert invalid.returncode == 2
    invalid_payload = json_output(invalid)
    assert invalid_payload["valid"] is False
    assert any("digest mismatch" in error for error in invalid_payload["errors"])
