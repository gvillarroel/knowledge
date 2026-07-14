#!/usr/bin/env python3
"""Read-only validation helpers for a Turso-backed Semantic OKF database."""

from __future__ import annotations

import hashlib
import importlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


STORE_CONTRACT = "semantic-okf-turso/1.0"
MAX_SQL_BYTES = 64 * 1024
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
FORBIDDEN_SQL_TOKENS = {
    "ALTER",
    "ANALYZE",
    "ATTACH",
    "BEGIN",
    "COMMIT",
    "CREATE",
    "DELETE",
    "DETACH",
    "DROP",
    "INSERT",
    "PRAGMA",
    "REINDEX",
    "RELEASE",
    "REPLACE",
    "ROLLBACK",
    "SAVEPOINT",
    "UPDATE",
    "VACUUM",
}
FORBIDDEN_SQL_FUNCTIONS = {"load_extension", "readfile", "writefile"}
WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class TursoQueryError(RuntimeError):
    """A classified read-only database or query failure."""

    def __init__(self, code: str, message: str, *, exit_code: int = 2) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def canonical_json(value: Any) -> str:
    """Return compact canonical JSON."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    """Hash one database file without changing it."""

    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise TursoQueryError(
            "database-invalid", f"cannot hash database {path}: {exc}"
        ) from exc
    return digest.hexdigest()


def database_file_state(path: Path) -> dict[str, str]:
    """Hash the database and any known sidecar files for an immutability check."""

    candidates = [
        path,
        *(Path(f"{path}{suffix}") for suffix in ("-wal", "-shm", ".wal", ".shm")),
    ]
    return {
        candidate.name: sha256_file(candidate)
        for candidate in candidates
        if candidate.is_file()
    }


def connect_read_only(database: Path) -> Any:
    """Open Turso Database and enable its connection-level query-only guard."""

    path = database.expanduser().resolve()
    if not path.is_file():
        raise TursoQueryError("database-missing", f"database is missing: {path}")
    try:
        turso = importlib.import_module("turso")
    except ImportError as exc:
        raise TursoQueryError(
            "runtime-missing",
            "pyturso is required; install this skill's scripts/requirements.txt",
        ) from exc
    try:
        connection = turso.connect(str(path))
        connection.execute("PRAGMA query_only=1")
        observed = connection.execute("PRAGMA query_only").fetchone()
    except Exception as exc:
        raise TursoQueryError(
            "database-invalid", f"cannot open database in query-only mode: {exc}"
        ) from exc
    if observed != (1,):
        connection.close()
        raise TursoQueryError(
            "read-only-unavailable", "Turso query_only mode did not activate"
        )
    return connection


def _metadata(connection: Any) -> dict[str, Any]:
    values: dict[str, Any] = {}
    try:
        rows = connection.execute(
            "SELECT key, value_json FROM bundle_metadata ORDER BY key"
        ).fetchall()
    except Exception as exc:
        raise TursoQueryError(
            "database-invalid", f"cannot read bundle metadata: {exc}"
        ) from exc
    for key, value_json in rows:
        try:
            values[str(key)] = json.loads(value_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise TursoQueryError(
                "database-invalid", f"metadata {key!r} is not valid JSON: {exc}"
            ) from exc
    return values


def _table_names(connection: Any) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return {str(row[0]) for row in rows if not str(row[0]).startswith("sqlite_")}


def _logical_sha256(connection: Any) -> str:
    digest = hashlib.sha256()
    for table, columns in TABLE_COLUMNS.items():
        select = ", ".join(columns)
        where = " WHERE key <> 'logical_sha256'" if table == "bundle_metadata" else ""
        order = ", ".join(columns)
        digest.update(table.encode("utf-8"))
        digest.update(b"\0")
        for row in connection.execute(
            f"SELECT {select} FROM {table}{where} ORDER BY {order}"
        ).fetchall():
            digest.update(canonical_json(list(row)).encode("utf-8"))
            digest.update(b"\n")
    return digest.hexdigest()


def validate_database(connection: Any, *, full: bool) -> dict[str, Any]:
    """Validate the read surface; recompute all logical hashes when *full* is true."""

    errors: list[str] = []
    try:
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
        metadata = _metadata(connection) if "bundle_metadata" in tables else {}
        if metadata.get("contract") != STORE_CONTRACT:
            errors.append("unsupported or missing Turso store contract")
        summary: dict[str, int] = {}
        if expected_tables <= tables:
            summary = {
                "artifacts": int(
                    connection.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]
                ),
                "attributes": int(
                    connection.execute(
                        "SELECT COUNT(*) FROM record_attributes"
                    ).fetchone()[0]
                ),
                "concepts": int(
                    connection.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
                ),
                "records": int(
                    connection.execute("SELECT COUNT(*) FROM records").fetchone()[0]
                ),
                "sources": int(
                    connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
                ),
                "statements": int(
                    connection.execute(
                        "SELECT COUNT(*) FROM rdf_statements"
                    ).fetchone()[0]
                ),
            }
            if metadata.get("counts") != summary:
                errors.append("stored row counts do not match database contents")
            missing_concepts = connection.execute(
                """
                SELECT COUNT(*) FROM records AS r
                LEFT JOIN concepts AS c ON c.concept_id = r.concept_id
                WHERE c.concept_id IS NULL
                """
            ).fetchone()[0]
            if missing_concepts or summary["concepts"] != summary["records"]:
                errors.append("records and concepts are not one-to-one")
            if full and metadata.get("logical_sha256") != _logical_sha256(connection):
                errors.append("logical database digest mismatch")
        return {
            "valid": not errors,
            "status": "pass" if not errors else "error",
            "errors": errors,
            "summary": summary,
            "logical_sha256": metadata.get("logical_sha256"),
            "engine": metadata.get("engine"),
            "validation": "full" if full else "read-surface",
        }
    except TursoQueryError:
        raise
    except Exception as exc:
        raise TursoQueryError(
            "database-invalid", f"database validation failed: {exc}"
        ) from exc


def require_valid_database(connection: Any, *, full: bool) -> dict[str, Any]:
    """Return a validation report or raise a stable database error."""

    report = validate_database(connection, full=full)
    if not report["valid"]:
        raise TursoQueryError("database-invalid", "; ".join(report["errors"]))
    return report


def _mask_sql(sql: str) -> str:
    """Mask comments and quoted values while preserving executable token positions."""

    result: list[str] = []
    index = 0
    length = len(sql)
    while index < length:
        current = sql[index]
        following = sql[index + 1] if index + 1 < length else ""
        if current == "-" and following == "-":
            end = sql.find("\n", index + 2)
            if end == -1:
                result.extend(" " * (length - index))
                break
            result.extend(" " * (end - index))
            index = end
            continue
        if current == "/" and following == "*":
            end = sql.find("*/", index + 2)
            if end == -1:
                raise TursoQueryError(
                    "query-invalid", "unterminated SQL block comment", exit_code=3
                )
            end += 2
            result.extend(" " * (end - index))
            index = end
            continue
        if current in {"'", '"', "`"}:
            quote = current
            result.append(" ")
            index += 1
            while index < length:
                result.append(" ")
                if sql[index] == quote:
                    if index + 1 < length and sql[index + 1] == quote:
                        result.append(" ")
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            else:
                raise TursoQueryError(
                    "query-invalid", "unterminated SQL quoted value", exit_code=3
                )
            continue
        if current == "[":
            end = sql.find("]", index + 1)
            if end == -1:
                raise TursoQueryError(
                    "query-invalid", "unterminated SQL bracket identifier", exit_code=3
                )
            end += 1
            result.extend(" " * (end - index))
            index = end
            continue
        result.append(current)
        index += 1
    return "".join(result)


def validate_read_only_sql(sql: str) -> str:
    """Accept one bounded SELECT/WITH/EXPLAIN query and reject mutation surfaces."""

    if not isinstance(sql, str) or not sql.strip():
        raise TursoQueryError("query-invalid", "SQL query cannot be empty", exit_code=3)
    if len(sql.encode("utf-8")) > MAX_SQL_BYTES:
        raise TursoQueryError(
            "query-rejected", "SQL query exceeds the 64 KiB limit", exit_code=3
        )
    masked = _mask_sql(sql).strip()
    semicolons = [index for index, character in enumerate(masked) if character == ";"]
    if semicolons:
        if len(semicolons) != 1 or masked[semicolons[0] + 1 :].strip():
            raise TursoQueryError(
                "query-rejected", "only one SQL statement is allowed", exit_code=3
            )
        masked = masked[: semicolons[0]].rstrip()
        sql = sql[: semicolons[0]].rstrip()
    tokens = [match.group(0) for match in WORD_RE.finditer(masked)]
    if not tokens or tokens[0].upper() not in {"SELECT", "WITH", "EXPLAIN"}:
        raise TursoQueryError(
            "query-rejected",
            "only SELECT, WITH, or EXPLAIN queries are allowed",
            exit_code=3,
        )
    upper_tokens = {token.upper() for token in tokens}
    forbidden = sorted(upper_tokens & FORBIDDEN_SQL_TOKENS)
    if forbidden:
        raise TursoQueryError(
            "query-rejected",
            "SQL contains disabled operation tokens: " + ", ".join(forbidden),
            exit_code=3,
        )
    lower_tokens = {token.casefold() for token in tokens}
    functions = sorted(lower_tokens & FORBIDDEN_SQL_FUNCTIONS)
    if functions:
        raise TursoQueryError(
            "query-rejected",
            "SQL contains disabled file or extension functions: "
            + ", ".join(functions),
            exit_code=3,
        )
    return sql


def parse_parameters(values: list[str] | None) -> Mapping[str, Any]:
    """Parse repeated NAME=JSON values into named SQL parameters."""

    parameters: dict[str, Any] = {}
    for value in values or []:
        name, separator, raw = value.partition("=")
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise TursoQueryError(
                "invalid-arguments",
                f"SQL parameter must use NAME=JSON: {value!r}",
                exit_code=3,
            )
        if name in parameters:
            raise TursoQueryError(
                "invalid-arguments", f"duplicate SQL parameter: {name}", exit_code=3
            )
        try:
            parameters[name] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TursoQueryError(
                "invalid-arguments",
                f"parameter {name!r} is not valid JSON: {exc}",
                exit_code=3,
            ) from exc
    return parameters


def json_value(value: Any) -> Any:
    """Convert one Turso scalar into a JSON-safe representation."""

    if isinstance(value, bytes):
        return {"type": "blob", "hex": value.hex()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
