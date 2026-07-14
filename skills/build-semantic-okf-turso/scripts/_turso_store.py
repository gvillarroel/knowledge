#!/usr/bin/env python3
"""Materialize and validate the Turso Database projection of a Semantic OKF bundle."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import shutil
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


STORE_CONTRACT = "semantic-okf-turso/1.0"
DATABASE_RELATIVE_PATH = "semantic/knowledge.db"
INDEXED_GRAPHS = {
    "data": "semantic/data.ttl",
    "ontology": "semantic/ontology.ttl",
    "provenance": "semantic/provenance.ttl",
}
REQUIRED_CORE_ARTIFACTS = {
    "semantic/ontology.ttl",
    "semantic/data.ttl",
    "semantic/shapes.ttl",
    "semantic/provenance.ttl",
    "semantic/records.jsonl",
    "semantic/semantic-plan.json",
    "semantic/validation-report.ttl",
}

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE bundle_metadata (
        key TEXT PRIMARY KEY,
        value_json TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE artifacts (
        path TEXT PRIMARY KEY,
        media_type TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE sources (
        source_id TEXT PRIMARY KEY,
        kind TEXT NOT NULL,
        declared_path TEXT NOT NULL,
        content_sha256 TEXT NOT NULL,
        records_sha256 TEXT NOT NULL,
        record_count INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE records (
        concept_id TEXT PRIMARY KEY,
        concept_path TEXT NOT NULL UNIQUE,
        subject_iri TEXT NOT NULL UNIQUE,
        source_id TEXT NOT NULL REFERENCES sources(source_id),
        record_id TEXT NOT NULL,
        concept_type TEXT NOT NULL,
        title TEXT NOT NULL,
        source_kind TEXT NOT NULL,
        source_path TEXT NOT NULL,
        source_content_sha256 TEXT NOT NULL,
        record_sha256 TEXT NOT NULL,
        ontology_class_iri TEXT NOT NULL,
        origin_iri TEXT NOT NULL,
        body TEXT NOT NULL,
        record_json TEXT NOT NULL,
        UNIQUE(source_id, record_id)
    )
    """,
    """
    CREATE TABLE concepts (
        concept_id TEXT PRIMARY KEY REFERENCES records(concept_id),
        concept_path TEXT NOT NULL UNIQUE,
        sha256 TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE record_attributes (
        concept_id TEXT NOT NULL REFERENCES records(concept_id),
        name TEXT NOT NULL,
        ordinal INTEGER NOT NULL,
        value_type TEXT NOT NULL,
        value_text TEXT NOT NULL,
        value_json TEXT NOT NULL,
        PRIMARY KEY(concept_id, name, ordinal)
    )
    """,
    """
    CREATE TABLE rdf_statements (
        statement_id TEXT PRIMARY KEY,
        graph_name TEXT NOT NULL,
        subject_type TEXT NOT NULL,
        subject TEXT NOT NULL,
        predicate TEXT NOT NULL,
        object_type TEXT NOT NULL,
        object TEXT NOT NULL,
        datatype TEXT NOT NULL,
        language TEXT NOT NULL
    )
    """,
    "CREATE INDEX records_source_idx ON records(source_id, record_id)",
    "CREATE INDEX records_type_idx ON records(concept_type, title)",
    "CREATE INDEX records_title_idx ON records(title)",
    "CREATE INDEX attributes_lookup_idx ON record_attributes(name, value_text, concept_id)",
    "CREATE INDEX statements_spo_idx ON rdf_statements(graph_name, subject, predicate, object)",
    "CREATE INDEX statements_pos_idx ON rdf_statements(graph_name, predicate, object, subject)",
)

TABLE_COLUMNS = {
    "bundle_metadata": ("key", "value_json"),
    "artifacts": ("path", "media_type", "sha256", "content"),
    "sources": (
        "source_id",
        "kind",
        "declared_path",
        "content_sha256",
        "records_sha256",
        "record_count",
    ),
    "records": (
        "concept_id",
        "concept_path",
        "subject_iri",
        "source_id",
        "record_id",
        "concept_type",
        "title",
        "source_kind",
        "source_path",
        "source_content_sha256",
        "record_sha256",
        "ontology_class_iri",
        "origin_iri",
        "body",
        "record_json",
    ),
    "concepts": ("concept_id", "concept_path", "sha256", "content"),
    "record_attributes": (
        "concept_id",
        "name",
        "ordinal",
        "value_type",
        "value_text",
        "value_json",
    ),
    "rdf_statements": (
        "statement_id",
        "graph_name",
        "subject_type",
        "subject",
        "predicate",
        "object_type",
        "object",
        "datatype",
        "language",
    ),
}


class TursoStoreError(RuntimeError):
    """A deterministic Turso projection or validation failure."""


def canonical_json(value: Any) -> str:
    """Return compact canonical JSON for hashing and exact SQL comparisons."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    """Return the lowercase SHA-256 digest for *value*."""

    return hashlib.sha256(value).hexdigest()


def _read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TursoStoreError(f"cannot read {label} at {path}: {exc}") from exc


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(_read_text(path, label))
    except json.JSONDecodeError as exc:
        raise TursoStoreError(f"invalid {label} at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise TursoStoreError(f"{label} at {path} must be a JSON object")
    return payload


def _safe_relative_path(root: Path, value: Any, *, prefix: str | None = None) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise TursoStoreError(f"unsafe bundle-relative path: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        raise TursoStoreError(f"unsafe bundle-relative path: {value!r}")
    if prefix is not None and (not pure.parts or pure.parts[0] != prefix):
        raise TursoStoreError(f"path must remain under {prefix}/: {value!r}")
    path = root.joinpath(*pure.parts)
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root.resolve())
    except (OSError, ValueError) as exc:
        raise TursoStoreError(
            f"bundle-relative path is missing or escapes the bundle: {value!r}"
        ) from exc
    if path.is_symlink():
        raise TursoStoreError(
            f"bundle-relative path cannot be a symbolic link: {value!r}"
        )
    return path


def _records(root: Path) -> list[dict[str, Any]]:
    path = root / "semantic" / "records.jsonl"
    records: list[dict[str, Any]] = []
    for number, line in enumerate(
        _read_text(path, "record ledger").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TursoStoreError(
                f"invalid records.jsonl line {number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise TursoStoreError(f"records.jsonl line {number} must be an object")
        records.append(record)
    if not records:
        raise TursoStoreError("record ledger cannot be empty")
    return records


def _connect(database: Path) -> Any:
    try:
        turso = importlib.import_module("turso")
    except ImportError as exc:
        raise TursoStoreError(
            "pyturso is required; install this skill's scripts/requirements.txt"
        ) from exc
    try:
        return turso.connect(str(database))
    except Exception as exc:
        raise TursoStoreError(f"cannot open Turso database {database}: {exc}") from exc


def _media_type(path: str) -> str:
    if path.endswith(".json"):
        return "application/json"
    if path.endswith(".jsonl"):
        return "application/x-ndjson"
    if path.endswith(".ttl"):
        return "text/turtle"
    if path.endswith(".md"):
        return "text/markdown"
    return "text/plain"


def _attribute_values(value: Any) -> Iterable[tuple[int, Any]]:
    if isinstance(value, list):
        yield from enumerate(value)
    else:
        yield 0, value


def _value_parts(value: Any) -> tuple[str, str, str]:
    if value is None:
        value_type = "null"
        value_text = ""
    elif isinstance(value, bool):
        value_type = "boolean"
        value_text = "true" if value else "false"
    elif isinstance(value, int):
        value_type = "integer"
        value_text = str(value)
    elif isinstance(value, float):
        value_type = "number"
        value_text = canonical_json(value)
    elif isinstance(value, str):
        value_type = "string"
        value_text = value
    elif isinstance(value, list):
        value_type = "array"
        value_text = canonical_json(value)
    elif isinstance(value, dict):
        value_type = "object"
        value_text = canonical_json(value)
    else:
        raise TursoStoreError(
            f"unsupported attribute value type: {type(value).__name__}"
        )
    return value_type, value_text, canonical_json(value)


def _rdf_rows(root: Path) -> list[tuple[str, ...]]:
    try:
        from rdflib import BNode, Graph, Literal, URIRef
    except ImportError as exc:
        raise TursoStoreError(
            "rdflib is required; install this skill's scripts/requirements.txt"
        ) from exc

    rows: list[tuple[str, ...]] = []
    for graph_name, relative in sorted(INDEXED_GRAPHS.items()):
        graph = Graph()
        try:
            graph.parse(root / relative, format="turtle")
        except Exception as exc:
            raise TursoStoreError(
                f"cannot parse {relative} for Turso indexing: {exc}"
            ) from exc
        for subject, predicate, obj in graph:
            if isinstance(subject, BNode) or isinstance(obj, BNode):
                raise TursoStoreError(
                    f"indexed graph {relative} contains a blank node; only stable RDF terms are indexed"
                )
            if not isinstance(subject, URIRef) or not isinstance(predicate, URIRef):
                raise TursoStoreError(
                    f"indexed graph {relative} contains an unsupported RDF statement"
                )
            if isinstance(obj, URIRef):
                object_type = "uri"
                object_value = str(obj)
                datatype = ""
                language = ""
            elif isinstance(obj, Literal):
                object_type = "literal"
                object_value = str(obj)
                datatype = str(obj.datatype or "")
                language = str(obj.language or "")
            else:
                raise TursoStoreError(
                    f"indexed graph {relative} contains an unsupported RDF object"
                )
            identity = (
                graph_name,
                "uri",
                str(subject),
                str(predicate),
                object_type,
                object_value,
                datatype,
                language,
            )
            statement_id = sha256_bytes(canonical_json(identity).encode("utf-8"))
            rows.append((statement_id, *identity))
    return sorted(rows)


def _schema_sha256() -> str:
    return sha256_bytes(canonical_json(SCHEMA_STATEMENTS).encode("utf-8"))


def _logical_sha256(connection: Any) -> str:
    digest = hashlib.sha256()
    for table, columns in TABLE_COLUMNS.items():
        select = ", ".join(columns)
        where = " WHERE key <> 'logical_sha256'" if table == "bundle_metadata" else ""
        order = ", ".join(columns)
        query = f"SELECT {select} FROM {table}{where} ORDER BY {order}"
        digest.update(table.encode("utf-8"))
        digest.update(b"\0")
        for row in connection.execute(query).fetchall():
            digest.update(canonical_json(list(row)).encode("utf-8"))
            digest.update(b"\n")
    return digest.hexdigest()


def _insert_metadata(connection: Any, values: Mapping[str, Any]) -> None:
    connection.executemany(
        "INSERT INTO bundle_metadata(key, value_json) VALUES (?, ?)",
        [(key, canonical_json(value)) for key, value in sorted(values.items())],
    )


def _artifact_rows(
    root: Path, source_manifest: Mapping[str, Any]
) -> list[tuple[str, ...]]:
    artifacts = source_manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise TursoStoreError("source manifest has no artifact map")
    paths = {
        value.get("path")
        for value in artifacts.values()
        if isinstance(value, dict) and isinstance(value.get("path"), str)
    }
    if paths != REQUIRED_CORE_ARTIFACTS:
        raise TursoStoreError(
            "source manifest core artifact set is incomplete or unexpected"
        )
    paths.update(
        {"index.md", "semantic/source-manifest.json", "semantic/build-report.json"}
    )
    rows: list[tuple[str, ...]] = []
    for relative in sorted(paths):
        path = _safe_relative_path(root, relative)
        content = _read_text(path, relative)
        rows.append(
            (
                relative,
                _media_type(relative),
                sha256_bytes(content.encode("utf-8")),
                content,
            )
        )
    return rows


def _source_rows(source_manifest: Mapping[str, Any]) -> list[tuple[Any, ...]]:
    values = source_manifest.get("sources")
    if not isinstance(values, list) or not values:
        raise TursoStoreError("source manifest has no sources")
    rows: list[tuple[Any, ...]] = []
    for source in values:
        if not isinstance(source, dict):
            raise TursoStoreError("source manifest contains a non-object source")
        try:
            rows.append(
                (
                    str(source["id"]),
                    str(source["kind"]),
                    str(source["path"]),
                    str(source["content_sha256"]),
                    str(source["records_sha256"]),
                    int(source["record_count"]),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise TursoStoreError(f"invalid source manifest entry: {source!r}") from exc
    return sorted(rows)


def _record_rows(
    root: Path, records: Sequence[Mapping[str, Any]]
) -> tuple[list[tuple[str, ...]], list[tuple[str, ...]], list[tuple[Any, ...]]]:
    required = {
        "concept_id",
        "concept_path",
        "subject_iri",
        "source_id",
        "record_id",
        "concept_type",
        "title",
        "source_kind",
        "source_path",
        "source_content_sha256",
        "record_sha256",
        "ontology_class_iri",
        "origin_iri",
        "body",
        "attributes",
    }
    record_rows: list[tuple[str, ...]] = []
    concept_rows: list[tuple[str, ...]] = []
    attribute_rows: list[tuple[Any, ...]] = []
    for record in sorted(records, key=lambda item: str(item.get("concept_id", ""))):
        missing = sorted(required - set(record))
        if missing:
            raise TursoStoreError(f"record omits required fields: {', '.join(missing)}")
        attributes = record["attributes"]
        if not isinstance(attributes, dict):
            raise TursoStoreError(
                f"record {record['concept_id']!r} attributes must be an object"
            )
        concept_path = str(record["concept_path"])
        concept_file = _safe_relative_path(root, concept_path, prefix="concepts")
        concept_content = _read_text(concept_file, concept_path)
        record_json = canonical_json(record)
        record_rows.append(
            tuple(
                str(record[field])
                for field in (
                    "concept_id",
                    "concept_path",
                    "subject_iri",
                    "source_id",
                    "record_id",
                    "concept_type",
                    "title",
                    "source_kind",
                    "source_path",
                    "source_content_sha256",
                    "record_sha256",
                    "ontology_class_iri",
                    "origin_iri",
                    "body",
                )
            )
            + (record_json,)
        )
        concept_rows.append(
            (
                str(record["concept_id"]),
                concept_path,
                sha256_bytes(concept_content.encode("utf-8")),
                concept_content,
            )
        )
        for name, value in sorted(attributes.items()):
            for ordinal, item in _attribute_values(value):
                value_type, value_text, value_json = _value_parts(item)
                attribute_rows.append(
                    (
                        str(record["concept_id"]),
                        str(name),
                        ordinal,
                        value_type,
                        value_text,
                        value_json,
                    )
                )
    return record_rows, concept_rows, attribute_rows


def _sidecar_paths(path: Path) -> tuple[Path, ...]:
    return tuple(Path(f"{path}{suffix}") for suffix in ("-wal", "-shm", ".wal", ".shm"))


def _cleanup_sidecars(path: Path) -> None:
    for sidecar in _sidecar_paths(path):
        sidecar.unlink(missing_ok=True)


def _cleanup_database(path: Path) -> None:
    path.unlink(missing_ok=True)
    _cleanup_sidecars(path)


def materialize_turso_store(
    bundle_root: Path, database: Path | None = None
) -> dict[str, Any]:
    """Build a complete Turso projection and publish it through one file replacement."""

    root = bundle_root.expanduser().resolve()
    if not root.is_dir():
        raise TursoStoreError(f"bundle root must be an existing directory: {root}")
    build_report = _json_object(root / "semantic" / "build-report.json", "build report")
    if build_report.get("status") != "pass" or build_report.get("valid") is not True:
        raise TursoStoreError("bundle build report is not passing")
    source_manifest = _json_object(
        root / "semantic" / "source-manifest.json", "source manifest"
    )
    records = _records(root)
    target = (database or (root / DATABASE_RELATIVE_PATH)).expanduser().resolve()
    if target.exists():
        raise TursoStoreError(f"database already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    connection = None
    try:
        connection = _connect(temporary)
        connection.execute("PRAGMA foreign_keys=1")
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)

        artifact_rows = _artifact_rows(root, source_manifest)
        source_rows = _source_rows(source_manifest)
        record_rows, concept_rows, attribute_rows = _record_rows(root, records)
        rdf_rows = _rdf_rows(root)
        package_version = importlib.metadata.version("pyturso")
        _insert_metadata(
            connection,
            {
                "contract": STORE_CONTRACT,
                "engine": {
                    "distribution": "pyturso",
                    "engine": "Turso Database",
                    "version": package_version,
                },
                "schema_sha256": _schema_sha256(),
                "source_manifest_sha256": sha256_bytes(
                    (root / "semantic" / "source-manifest.json").read_bytes()
                ),
                "counts": {
                    "artifacts": len(artifact_rows),
                    "attributes": len(attribute_rows),
                    "concepts": len(concept_rows),
                    "records": len(record_rows),
                    "sources": len(source_rows),
                    "statements": len(rdf_rows),
                },
                "indexed_graphs": INDEXED_GRAPHS,
            },
        )
        connection.executemany(
            "INSERT INTO artifacts(path, media_type, sha256, content) VALUES (?, ?, ?, ?)",
            artifact_rows,
        )
        connection.executemany(
            """
            INSERT INTO sources(
                source_id, kind, declared_path, content_sha256, records_sha256, record_count
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            source_rows,
        )
        connection.executemany(
            """
            INSERT INTO records(
                concept_id, concept_path, subject_iri, source_id, record_id, concept_type,
                title, source_kind, source_path, source_content_sha256, record_sha256,
                ontology_class_iri, origin_iri, body, record_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            record_rows,
        )
        connection.executemany(
            "INSERT INTO concepts(concept_id, concept_path, sha256, content) VALUES (?, ?, ?, ?)",
            concept_rows,
        )
        if attribute_rows:
            connection.executemany(
                """
                INSERT INTO record_attributes(
                    concept_id, name, ordinal, value_type, value_text, value_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                attribute_rows,
            )
        if rdf_rows:
            connection.executemany(
                """
                INSERT INTO rdf_statements(
                    statement_id, graph_name, subject_type, subject, predicate,
                    object_type, object, datatype, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rdf_rows,
            )
        connection.commit()
        logical_sha256 = _logical_sha256(connection)
        connection.execute(
            "INSERT INTO bundle_metadata(key, value_json) VALUES (?, ?)",
            ("logical_sha256", canonical_json(logical_sha256)),
        )
        connection.commit()
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if integrity != [("ok",)]:
            raise TursoStoreError(f"Turso integrity check failed: {integrity!r}")
        connection.close()
        connection = None
        _cleanup_sidecars(temporary)

        validation = validate_turso_store(temporary, bundle_root=root)
        if not validation["valid"]:
            raise TursoStoreError(
                "generated Turso store is invalid: " + "; ".join(validation["errors"])
            )
        _cleanup_sidecars(temporary)
        temporary.replace(target)
        return {
            "status": "pass",
            "database": str(target),
            "contract": STORE_CONTRACT,
            "logical_sha256": logical_sha256,
            "summary": validation["summary"],
        }
    except Exception:
        if connection is not None:
            try:
                connection.rollback()
                connection.close()
            except Exception:
                pass
        _cleanup_database(temporary)
        raise


def _metadata(connection: Any, errors: list[str]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    try:
        rows = connection.execute(
            "SELECT key, value_json FROM bundle_metadata ORDER BY key"
        ).fetchall()
    except Exception as exc:
        errors.append(f"cannot read bundle_metadata: {exc}")
        return values
    for key, value_json in rows:
        try:
            values[str(key)] = json.loads(value_json)
        except (TypeError, json.JSONDecodeError) as exc:
            errors.append(f"metadata {key!r} is not valid JSON: {exc}")
    return values


def _table_names(connection: Any) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return {str(row[0]) for row in rows if not str(row[0]).startswith("sqlite_")}


def _count(connection: Any, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def validate_turso_store(
    database: Path, *, bundle_root: Path | None = None
) -> dict[str, Any]:
    """Validate schema, logical hashes, relational coherence, and optional bundle parity."""

    path = database.expanduser().resolve()
    errors: list[str] = []
    if not path.is_file():
        return {
            "valid": False,
            "status": "error",
            "errors": [f"database is missing: {path}"],
            "summary": {},
        }
    sidecars = [sidecar for sidecar in _sidecar_paths(path) if sidecar.exists()]
    if sidecars:
        return {
            "valid": False,
            "status": "error",
            "errors": [
                "published database is not quiescent; sidecars are present: "
                + ", ".join(sidecar.name for sidecar in sidecars)
            ],
            "summary": {},
        }
    connection = None
    temporary_directory: tempfile.TemporaryDirectory[str] | None = None
    summary: dict[str, int] = {}
    try:
        temporary_directory = tempfile.TemporaryDirectory(
            prefix="validate-semantic-okf-turso-"
        )
        working = Path(temporary_directory.name) / path.name
        shutil.copy2(path, working)
        connection = _connect(working)
        connection.execute("PRAGMA query_only=1")
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if integrity != [("ok",)]:
            errors.append(f"Turso integrity check failed: {integrity!r}")
        tables = _table_names(connection)
        expected_tables = set(TABLE_COLUMNS)
        if tables != expected_tables:
            errors.append(
                f"table set mismatch: expected {sorted(expected_tables)}, observed {sorted(tables)}"
            )
        for table, columns in TABLE_COLUMNS.items():
            if table not in tables:
                continue
            observed = tuple(
                str(row[1])
                for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            )
            if observed != columns:
                errors.append(f"column set mismatch for {table}: {observed!r}")
        metadata = _metadata(connection, errors)
        if metadata.get("contract") != STORE_CONTRACT:
            errors.append("unsupported or missing Turso store contract")
        if metadata.get("schema_sha256") != _schema_sha256():
            errors.append("database schema digest mismatch")

        if expected_tables <= tables:
            summary = {
                "artifacts": _count(connection, "artifacts"),
                "attributes": _count(connection, "record_attributes"),
                "concepts": _count(connection, "concepts"),
                "records": _count(connection, "records"),
                "sources": _count(connection, "sources"),
                "statements": _count(connection, "rdf_statements"),
            }
            if metadata.get("counts") != summary:
                errors.append("stored row counts do not match database contents")
            observed_digest = _logical_sha256(connection)
            if metadata.get("logical_sha256") != observed_digest:
                errors.append("logical database digest mismatch")
            orphan_records = connection.execute(
                """
                SELECT COUNT(*) FROM records AS r
                LEFT JOIN sources AS s ON s.source_id = r.source_id
                WHERE s.source_id IS NULL
                """
            ).fetchone()[0]
            if orphan_records:
                errors.append(
                    f"records contain {orphan_records} missing source references"
                )
            missing_concepts = connection.execute(
                """
                SELECT COUNT(*) FROM records AS r
                LEFT JOIN concepts AS c ON c.concept_id = r.concept_id
                WHERE c.concept_id IS NULL
                """
            ).fetchone()[0]
            if missing_concepts or summary["concepts"] != summary["records"]:
                errors.append("records and concepts are not one-to-one")
            bad_record_json = 0
            for row in connection.execute(
                """
                SELECT concept_id, concept_path, subject_iri, source_id, record_id,
                       concept_type, title, record_sha256, record_json
                FROM records ORDER BY concept_id
                """
            ).fetchall():
                try:
                    payload = json.loads(row[8])
                except (TypeError, json.JSONDecodeError):
                    bad_record_json += 1
                    continue
                expected = row[:8]
                observed = tuple(
                    payload.get(name)
                    for name in (
                        "concept_id",
                        "concept_path",
                        "subject_iri",
                        "source_id",
                        "record_id",
                        "concept_type",
                        "title",
                        "record_sha256",
                    )
                )
                if observed != expected:
                    bad_record_json += 1
            if bad_record_json:
                errors.append(
                    f"{bad_record_json} record JSON payloads disagree with indexed columns"
                )

        if bundle_root is not None and expected_tables <= tables:
            root = bundle_root.expanduser().resolve()
            if not root.is_dir():
                errors.append(f"bundle root is missing: {root}")
            else:
                artifact_rows = connection.execute(
                    "SELECT path, sha256, content FROM artifacts ORDER BY path"
                ).fetchall()
                for relative, stored_sha256, stored_content in artifact_rows:
                    try:
                        source = _safe_relative_path(root, relative)
                        content = _read_text(source, str(relative))
                    except TursoStoreError as exc:
                        errors.append(str(exc))
                        continue
                    if (
                        content != stored_content
                        or sha256_bytes(content.encode("utf-8")) != stored_sha256
                    ):
                        errors.append(
                            f"database artifact differs from bundle: {relative}"
                        )
                for (
                    concept_id,
                    relative,
                    stored_sha256,
                    stored_content,
                ) in connection.execute(
                    "SELECT concept_id, concept_path, sha256, content FROM concepts ORDER BY concept_id"
                ).fetchall():
                    try:
                        source = _safe_relative_path(root, relative, prefix="concepts")
                        content = _read_text(source, str(relative))
                    except TursoStoreError as exc:
                        errors.append(str(exc))
                        continue
                    if (
                        content != stored_content
                        or sha256_bytes(content.encode("utf-8")) != stored_sha256
                    ):
                        errors.append(
                            f"database concept differs from bundle: {concept_id}"
                        )
                manifest_digest = sha256_bytes(
                    (root / "semantic" / "source-manifest.json").read_bytes()
                )
                if metadata.get("source_manifest_sha256") != manifest_digest:
                    errors.append("source manifest digest differs from the bundle")
        return {
            "valid": not errors,
            "status": "pass" if not errors else "error",
            "errors": errors,
            "summary": summary,
            "logical_sha256": metadata.get("logical_sha256"),
        }
    except Exception as exc:
        errors.append(f"cannot validate Turso database: {exc}")
        return {"valid": False, "status": "error", "errors": errors, "summary": summary}
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
        if temporary_directory is not None:
            temporary_directory.cleanup()


def remove_turso_store(path: Path) -> None:
    """Remove an unpublished temporary database and its possible sidecars."""

    _cleanup_database(path)


def copy_without_database(source: Path, destination: Path) -> None:
    """Copy a bundle tree while excluding an existing Turso projection."""

    shutil.copytree(
        source,
        destination,
        ignore=lambda directory, names: {
            name
            for name in names
            if Path(directory, name).resolve()
            == (source / DATABASE_RELATIVE_PATH).resolve()
        },
    )
