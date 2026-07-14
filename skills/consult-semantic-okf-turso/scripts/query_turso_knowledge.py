#!/usr/bin/env python3
"""Query a Turso-backed Semantic OKF database without mutating it."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _turso_read import (  # noqa: E402
    TABLE_COLUMNS,
    TursoQueryError,
    canonical_json,
    connect_read_only,
    database_file_state,
    json_value,
    parse_parameters,
    require_valid_database,
    validate_read_only_sql,
)


def _configure_utf8_output() -> None:
    """Use deterministic UTF-8 output on Windows and redirected consoles."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def _positive_limit(args: argparse.Namespace) -> int | None:
    if getattr(args, "all", False):
        return None
    limit = int(getattr(args, "limit", 100))
    if limit < 1:
        raise TursoQueryError("invalid-arguments", "--limit must be at least 1")
    return limit


def _bounded_rows(cursor: Any, limit: int | None) -> tuple[list[tuple[Any, ...]], bool]:
    rows: list[tuple[Any, ...]] = []
    while limit is None or len(rows) <= limit:
        row = cursor.fetchone()
        if row is None:
            return rows, False
        rows.append(tuple(row))
    return rows[:limit], True


def _record_query(connection: Any, args: argparse.Namespace) -> dict[str, Any]:
    clauses: list[str] = []
    parameters: list[Any] = []
    exact = {
        "r.concept_id": args.concept_id,
        "r.subject_iri": args.subject_iri,
        "r.source_id": args.source_id,
        "r.record_id": args.record_id,
        "r.concept_type": args.concept_type,
    }
    for field, value in exact.items():
        if value is not None:
            clauses.append(f"{field} = ?")
            parameters.append(value)
    for name, raw_value in args.attribute or []:
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            value = raw_value
        clauses.append(
            """
            EXISTS (
                SELECT 1 FROM record_attributes AS a
                WHERE a.concept_id = r.concept_id AND a.name = ? AND a.value_json = ?
            )
            """
        )
        parameters.extend((name, canonical_json(value)))
    if args.contains:
        clauses.append(
            "instr(lower(r.title || char(10) || r.body || char(10) || r.record_json), lower(?)) > 0"
        )
        parameters.append(args.contains)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    select_content = ", c.content" if args.show_content else ""
    limit = _positive_limit(args)
    sql = (
        "SELECT r.record_json"
        + select_content
        + " FROM records AS r JOIN concepts AS c ON c.concept_id = r.concept_id"
        + where
        + " ORDER BY r.concept_id"
    )
    cursor = connection.execute(sql, parameters)
    rows, truncated = _bounded_rows(cursor, limit)
    records: list[dict[str, Any]] = []
    for row in rows:
        try:
            record = json.loads(row[0])
        except json.JSONDecodeError as exc:
            raise TursoQueryError(
                "database-invalid", f"invalid record JSON in database: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise TursoQueryError("database-invalid", "record JSON must be an object")
        if not args.show_body:
            record.pop("body", None)
        if args.show_content:
            record["content"] = row[1]
        records.append(record)
    return {
        "status": "pass",
        "mode": "records",
        "returned": len(records),
        "truncated": truncated,
        "records": records,
    }


def _triple_query(connection: Any, args: argparse.Namespace) -> dict[str, Any]:
    clauses: list[str] = []
    parameters: list[Any] = []
    for field, value in (
        ("graph_name", args.graph),
        ("subject", args.subject),
        ("predicate", args.predicate),
        ("object_type", args.object_type),
    ):
        if value is not None:
            clauses.append(f"{field} = ?")
            parameters.append(value)
    if args.object is not None:
        clauses.append("object = ?")
        parameters.append(args.object)
    if args.contains is not None:
        clauses.append("instr(lower(object), lower(?)) > 0")
        parameters.append(args.contains)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    limit = _positive_limit(args)
    cursor = connection.execute(
        """
        SELECT graph_name, subject_type, subject, predicate, object_type, object, datatype, language
        FROM rdf_statements
        """
        + where
        + " ORDER BY graph_name, subject, predicate, object, datatype, language",
        parameters,
    )
    rows, truncated = _bounded_rows(cursor, limit)
    names = (
        "graph",
        "subject_type",
        "subject",
        "predicate",
        "object_type",
        "object",
        "datatype",
        "language",
    )
    return {
        "status": "pass",
        "mode": "triples",
        "returned": len(rows),
        "truncated": truncated,
        "statements": [dict(zip(names, row, strict=True)) for row in rows],
    }


def _artifact_query(connection: Any, args: argparse.Namespace) -> dict[str, Any]:
    row = connection.execute(
        "SELECT path, media_type, sha256, content FROM artifacts WHERE path = ?",
        (args.path,),
    ).fetchone()
    if row is None:
        raise TursoQueryError(
            "not-found", f"artifact is not stored in the database: {args.path}"
        )
    return {
        "status": "pass",
        "mode": "artifact",
        "artifact": dict(
            zip(("path", "media_type", "sha256", "content"), row, strict=True)
        ),
    }


def _stats_query(connection: Any) -> dict[str, Any]:
    validation = require_valid_database(connection, full=False)
    by_source = [
        {"source_id": row[0], "kind": row[1], "records": row[2]}
        for row in connection.execute(
            "SELECT source_id, kind, record_count FROM sources ORDER BY source_id"
        ).fetchall()
    ]
    by_type = [
        {"concept_type": row[0], "records": row[1]}
        for row in connection.execute(
            "SELECT concept_type, COUNT(*) FROM records GROUP BY concept_type ORDER BY concept_type"
        ).fetchall()
    ]
    return {
        "status": "pass",
        "mode": "stats",
        "logical_sha256": validation["logical_sha256"],
        "summary": validation["summary"],
        "by_source": by_source,
        "by_type": by_type,
    }


def _schema_query(connection: Any) -> dict[str, Any]:
    tables = []
    for table in TABLE_COLUMNS:
        columns = [
            {
                "position": row[0],
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "primary_key_position": row[5],
            }
            for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
        ]
        tables.append({"name": table, "columns": columns})
    return {"status": "pass", "mode": "schema", "tables": tables}


def _sql_text(args: argparse.Namespace) -> str:
    if args.query is not None:
        return args.query
    try:
        return args.query_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TursoQueryError(
            "query-invalid", f"cannot read SQL query file: {exc}", exit_code=3
        ) from exc


def _sql_query(connection: Any, args: argparse.Namespace) -> dict[str, Any]:
    sql = validate_read_only_sql(_sql_text(args))
    parameters = parse_parameters(args.param)
    try:
        cursor = connection.execute(sql, parameters)
    except Exception as exc:
        raise TursoQueryError(
            "query-failed", f"Turso SQL query failed: {exc}", exit_code=3
        ) from exc
    description = cursor.description or ()
    columns = [str(item[0]) for item in description]
    if len(columns) != len(set(columns)):
        raise TursoQueryError(
            "query-rejected",
            "SQL result columns must have unique names; add explicit aliases",
            exit_code=3,
        )
    rows, truncated = _bounded_rows(cursor, _positive_limit(args))
    return {
        "status": "pass",
        "mode": "sql",
        "columns": columns,
        "returned": len(rows),
        "truncated": truncated,
        "rows": [
            {
                column: json_value(value)
                for column, value in zip(columns, row, strict=True)
            }
            for row in rows
        ],
    }


def _verify_query(connection: Any) -> dict[str, Any]:
    report = require_valid_database(connection, full=True)
    return {"status": "pass", "mode": "verify", **report}


def _write_delimited(payload: Mapping[str, Any], delimiter: str) -> None:
    rows = payload.get("rows")
    columns = payload.get("columns")
    if not isinstance(rows, list) or not isinstance(columns, list):
        raise TursoQueryError(
            "invalid-format", "CSV and TSV output are available only for sql mode"
        )
    writer = csv.writer(sys.stdout, delimiter=delimiter, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row.get(column) for column in columns])


def _print_text(payload: Mapping[str, Any]) -> None:
    mode = payload.get("mode")
    if mode == "artifact":
        print(payload["artifact"]["content"], end="")
        return
    if mode == "records":
        for record in payload["records"]:
            print(
                "\t".join(
                    str(record.get(field, ""))
                    for field in (
                        "concept_id",
                        "source_id",
                        "record_id",
                        "title",
                        "concept_path",
                    )
                )
            )
        return
    if mode == "triples":
        for statement in payload["statements"]:
            print(
                "\t".join(
                    str(statement[field])
                    for field in (
                        "graph",
                        "subject",
                        "predicate",
                        "object",
                        "datatype",
                        "language",
                    )
                )
            )
        return
    if mode == "sql":
        columns = payload["columns"]
        print("\t".join(columns))
        for row in payload["rows"]:
            print("\t".join(str(row.get(column, "")) for column in columns))
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _emit(payload: Mapping[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    elif output_format == "jsonl":
        rows: Iterable[Any]
        if payload.get("mode") == "records":
            rows = payload["records"]
        elif payload.get("mode") == "triples":
            rows = payload["statements"]
        elif payload.get("mode") == "sql":
            rows = payload["rows"]
        else:
            rows = [payload]
        for row in rows:
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))
    elif output_format == "csv":
        _write_delimited(payload, ",")
    elif output_format == "tsv":
        _write_delimited(payload, "\t")
    elif output_format == "paths":
        if payload.get("mode") != "records":
            raise TursoQueryError(
                "invalid-format", "paths output is available only for records mode"
            )
        for record in payload["records"]:
            print(record["concept_path"])
    else:
        _print_text(payload)


def _add_limit(parser: argparse.ArgumentParser, default: int = 100) -> None:
    parser.add_argument("--limit", type=int, default=default)
    parser.add_argument("--all", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    """Build the Turso knowledge query command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="Path to semantic/knowledge.db.")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Recompute the complete logical database digest before querying.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    records = subparsers.add_parser(
        "records", help="Filter normalized knowledge records."
    )
    records.add_argument("--concept-id")
    records.add_argument("--subject-iri")
    records.add_argument("--source-id")
    records.add_argument("--record-id")
    records.add_argument("--type", dest="concept_type")
    records.add_argument(
        "--attribute", nargs=2, action="append", metavar=("NAME", "JSON_VALUE")
    )
    records.add_argument("--contains")
    records.add_argument("--show-body", action="store_true")
    records.add_argument("--show-content", action="store_true")
    _add_limit(records, 50)
    records.add_argument(
        "--format", choices=("text", "json", "jsonl", "paths"), default="text"
    )

    triples = subparsers.add_parser("triples", help="Filter indexed RDF statements.")
    triples.add_argument("--graph", choices=("data", "ontology", "provenance"))
    triples.add_argument("--subject")
    triples.add_argument("--predicate")
    triples.add_argument("--object")
    triples.add_argument("--object-type", choices=("uri", "literal"))
    triples.add_argument(
        "--contains", help="Case-insensitive fixed substring in RDF object values."
    )
    _add_limit(triples, 100)
    triples.add_argument("--format", choices=("text", "json", "jsonl"), default="text")

    artifact = subparsers.add_parser("artifact", help="Read one stored core artifact.")
    artifact.add_argument("--path", required=True)
    artifact.add_argument("--format", choices=("text", "json"), default="text")

    stats = subparsers.add_parser("stats", help="Show database and source counts.")
    stats.add_argument("--format", choices=("text", "json"), default="text")

    schema = subparsers.add_parser(
        "schema", help="Inspect the supported SQL tables and columns."
    )
    schema.add_argument("--format", choices=("text", "json"), default="text")

    sql = subparsers.add_parser(
        "sql", help="Run one parameterized read-only SQL query."
    )
    query_source = sql.add_mutually_exclusive_group(required=True)
    query_source.add_argument("--query")
    query_source.add_argument("--query-file", type=Path)
    sql.add_argument("--param", action="append", metavar="NAME=JSON")
    _add_limit(sql, 1000)
    sql.add_argument(
        "--format", choices=("text", "json", "jsonl", "csv", "tsv"), default="text"
    )

    verify = subparsers.add_parser(
        "verify", help="Run full logical and relational validation."
    )
    verify.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one immutable Turso consultation command."""

    _configure_utf8_output()
    args = build_parser().parse_args(argv)
    database = args.database.expanduser().resolve()
    before = database_file_state(database) if database.is_file() else {}
    connection = None
    temporary_directory: tempfile.TemporaryDirectory[str] | None = None
    try:
        sidecars = sorted(name for name in before if name != database.name)
        if sidecars:
            raise TursoQueryError(
                "database-invalid",
                "published database is not quiescent; sidecars are present: "
                + ", ".join(sidecars),
            )
        temporary_directory = tempfile.TemporaryDirectory(
            prefix="consult-semantic-okf-turso-"
        )
        working_database = Path(temporary_directory.name) / database.name
        try:
            shutil.copy2(database, working_database)
        except OSError as exc:
            raise TursoQueryError(
                "database-invalid", f"cannot create read-only working copy: {exc}"
            ) from exc
        connection = connect_read_only(working_database)
        require_valid_database(connection, full=args.validate)
        if args.command == "records":
            payload = _record_query(connection, args)
        elif args.command == "triples":
            payload = _triple_query(connection, args)
        elif args.command == "artifact":
            payload = _artifact_query(connection, args)
        elif args.command == "stats":
            payload = _stats_query(connection)
        elif args.command == "schema":
            payload = _schema_query(connection)
        elif args.command == "sql":
            payload = _sql_query(connection, args)
        else:
            payload = _verify_query(connection)
        connection.close()
        connection = None
        after = database_file_state(database)
        if before != after:
            raise TursoQueryError(
                "immutability-failed",
                "database or sidecar bytes changed during consultation",
            )
        _emit(payload, getattr(args, "format", "text"))
        return 0
    except TursoQueryError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return exc.exit_code
    except Exception as exc:
        print(f"query-failed: {exc}", file=sys.stderr)
        return 3
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
        if temporary_directory is not None:
            temporary_directory.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
