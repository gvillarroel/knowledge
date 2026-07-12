#!/usr/bin/env python3
"""Build a coherent OKF + OWL + SHACL bundle from heterogeneous sources with PySpark."""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import html
import json
import math
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import unquote, urlsplit

from _semantic_okf import (
    BundleError,
    CSV_READER_OPTIONS,
    JSON_READER_OPTIONS,
    ManifestError,
    STRUCTURED_INTERNAL_COLUMNS,
    canonical_json,
    configure_utf8_output,
    finalize_record,
    load_manifest,
    materialize_bundle,
    normalize_text,
    sha256_json,
    source_by_id,
)


NORMALIZED_COLUMNS = (
    "source_id",
    "source_kind",
    "source_path",
    "record_id",
    "subject_iri",
    "title",
    "body",
    "attributes",
    "normalization_error",
)
CSV_OPTIONS = CSV_READER_OPTIONS
JSON_OPTIONS = JSON_READER_OPTIONS
INTERNAL_SOURCE_PATH = "__semantic_okf_source_path__"
INTERNAL_NORMALIZATION_ERROR = "__semantic_okf_normalization_error__"
assert {INTERNAL_SOURCE_PATH, INTERNAL_NORMALIZATION_ERROR} == STRUCTURED_INTERNAL_COLUMNS


def _local_path_from_uri(value: str) -> Path:
    parsed = urlsplit(value)
    if parsed.scheme == "file":
        raw = unquote(parsed.path)
        if re.match(r"^/[A-Za-z]:", raw):
            raw = raw[1:]
        return Path(raw)
    return Path(value)


def _strip_markdown_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    import yaml

    lines = normalize_text(content).splitlines()
    if not lines or lines[0] != "---":
        return {}, normalize_text(content)
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("Markdown frontmatter is unterminated") from exc
    try:
        payload = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Markdown frontmatter is invalid YAML: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Markdown frontmatter must be an object")
    return payload, "\n".join(lines[end + 1 :]).lstrip("\n")


def _markdown_table_cell(value: Any) -> str:
    """Escape one untrusted RDF term for a generated Markdown table cell."""

    escaped = html.escape(normalize_text(str(value)), quote=False)
    return escaped.replace("`", "&#96;").replace("|", "\\|").replace("\n", " ↵ ")


def _frontmatter_scalar(value: Any, field_name: str) -> str | int | float | bool:
    """Normalize a mapped YAML scalar to deterministic JSON-compatible data."""

    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"mapped Markdown field {field_name!r} must be finite")
    if isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError(f"mapped Markdown field {field_name!r} must be a scalar")


def _markdown_record(row: Any, source: Mapping[str, Any]) -> tuple[str, ...]:
    metadata, body = _strip_markdown_frontmatter(row.value)
    path = _local_path_from_uri(row.source_path)
    manifest_root = Path(str(source["_manifest_root"])).resolve()
    try:
        relative = path.resolve().relative_to(manifest_root).as_posix()
    except (OSError, ValueError) as exc:
        raise ValueError(f"Markdown source {source['id']} escapes the manifest directory") from exc
    heading = next(
        (line[2:].strip() for line in body.splitlines() if line.startswith("# ") and line[2:].strip()),
        "",
    )
    title = str(metadata.get("title") or heading or path.stem)
    record_id = relative.removesuffix(path.suffix)
    attributes = {
        input_name: _frontmatter_scalar(metadata[input_name], input_name)
        for input_name in sorted(source.get("fields", {}))
        if input_name in metadata and metadata[input_name] is not None
    }
    return (
        source["id"],
        source["kind"],
        row.source_path,
        record_id,
        "",
        title,
        body or f"# {title}",
        canonical_json(attributes),
        "",
    )


def _rdf_records(row: Any, source: Mapping[str, Any]) -> Iterable[tuple[str, ...]]:
    from rdflib import BNode, Graph, URIRef
    from rdflib.namespace import RDFS

    graph = Graph()
    path = _local_path_from_uri(row.source_path)
    rdf_format = source["format"]
    graph.parse(data=row.value, format=rdf_format, publicID=path.resolve().as_uri())
    blank_nodes = {
        term
        for triple in graph
        for term in triple
        if isinstance(term, BNode)
    }
    if blank_nodes:
        raise ValueError(
            f"RDF source {source['id']} contains blank nodes; skolemize them before ingestion"
        )
    title_predicate = URIRef(source.get("title_predicate") or str(RDFS.label))
    field_map = {URIRef(key): value for key, value in source.get("fields", {}).items()}
    for subject in sorted({item for item in graph.subjects() if isinstance(item, URIRef)}, key=str):
        title_values = sorted(graph.objects(subject, title_predicate), key=lambda value: value.n3())
        title_value = title_values[0] if title_values else None
        title = str(title_value) if title_value is not None else str(subject).rstrip("/#").rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        attributes: dict[str, Any] = {}
        for predicate in sorted(field_map, key=str):
            values = [str(value) for value in sorted(graph.objects(subject, predicate), key=lambda value: value.n3())]
            if values:
                attributes[str(predicate)] = values[0] if len(values) == 1 else values
        statements = sorted(
            (str(predicate), str(value)) for predicate, value in graph.predicate_objects(subject)
        )
        body_lines = [f"# {_markdown_table_cell(title)}", "", "| Predicate | Value |", "|---|---|"]
        for predicate, value in statements:
            body_lines.append(f"| {_markdown_table_cell(predicate)} | {_markdown_table_cell(value)} |")
        yield (
            source["id"],
            source["kind"],
            row.source_path,
            str(subject),
            str(subject),
            title,
            "\n".join(body_lines),
            canonical_json(attributes),
            "",
        )


def _load_pyspark() -> dict[str, Any]:
    try:
        import pyspark.cloudpickle as cloudpickle
        from pyspark.sql import SparkSession, functions as F
        from pyspark.sql.types import (
            BooleanType,
            DateType,
            DoubleType,
            IntegerType,
            LongType,
            StringType,
            StructField,
            StructType,
            TimestampType,
        )
    except ImportError as exc:
        requirements = Path(__file__).with_name("requirements.txt")
        raise BundleError(
            f"PySpark is missing; install the locked environment with "
            f"`python -m pip install -r {requirements}`"
        ) from exc
    cloudpickle.register_pickle_by_value(sys.modules["_semantic_okf"])
    if __name__ != "__main__":
        cloudpickle.register_pickle_by_value(sys.modules[__name__])
    return {
        "SparkSession": SparkSession,
        "F": F,
        "types": {
            "string": StringType,
            "integer": IntegerType,
            "long": LongType,
            "double": DoubleType,
            "boolean": BooleanType,
            "date": DateType,
            "timestamp": TimestampType,
        },
        "StructField": StructField,
        "StructType": StructType,
        "StringType": StringType,
    }


def _normalized_schema(pyspark: Mapping[str, Any]) -> Any:
    return pyspark["StructType"](
        [pyspark["StructField"](name, pyspark["StringType"](), False) for name in NORMALIZED_COLUMNS]
    )


def _source_schema(
    source: Mapping[str, Any],
    pyspark: Mapping[str, Any],
    field_order: Iterable[str] | None = None,
) -> Any:
    fields = []
    names = list(field_order) if field_order is not None else list(source["schema"])
    for name in names:
        type_name = source["schema"][name]
        factory = pyspark["types"].get(type_name)
        if factory is None:
            raise BundleError(f"source {source['id']!r} uses unsupported schema type {type_name!r}")
        fields.append(pyspark["StructField"](name, factory(), True))
    return pyspark["StructType"](fields)


def _csv_header(path: Path, source: Mapping[str, Any], options: Mapping[str, str]) -> list[str]:
    """Read one physical CSV header without Spark's duplicate-name rewriting."""

    delimiter = options.get("sep", ",")
    quote = options.get("quote", '"')
    escape = options.get("escape", "\\")
    for option_name, value, allow_empty in (
        ("sep", delimiter, False),
        ("quote", quote, True),
        ("escape", escape, True),
    ):
        if (not value and not allow_empty) or len(value) > 1:
            raise ValueError(
                f"CSV source {source['id']!r} option {option_name} must be one character"
            )
    encoding = options.get("encoding", "UTF-8")
    if encoding.lower().replace("-", "").replace("_", "") == "utf8":
        encoding = "utf-8-sig"
    reader_options: dict[str, Any] = {"delimiter": delimiter}
    if quote:
        reader_options.update({"quotechar": quote, "quoting": csv.QUOTE_MINIMAL})
    else:
        reader_options.update({"quotechar": None, "quoting": csv.QUOTE_NONE})
    if escape:
        reader_options["escapechar"] = escape
    try:
        with path.open("r", encoding=encoding, newline="") as handle:
            header = next(csv.reader(handle, **reader_options), None)
    except (LookupError, UnicodeError, csv.Error, OSError) as exc:
        raise ValueError(f"CSV source {source['id']!r} header cannot be read from {path}: {exc}") from exc
    if header is None:
        raise ValueError(f"CSV source {source['id']!r} is empty and has no header: {path}")
    return header


def _spark_column(F: Any, name: str) -> Any:
    """Address a top-level Spark column literally, including dots in legal names."""

    return F.col(f"`{name}`")


def discover_source_files(manifest_root: Path, source: Mapping[str, Any]) -> list[Path]:
    """Resolve a local source glob without allowing traversal outside the manifest tree."""

    raw_path = str(source["path"])
    if "\\" in raw_path or Path(raw_path).is_absolute() or Path(raw_path).drive or ".." in Path(raw_path).parts:
        raise BundleError(f"source {source['id']!r} path must be manifest-relative and cannot traverse")
    pattern = str((manifest_root / raw_path).resolve(strict=False))
    matches = sorted(Path(item).resolve() for item in glob.glob(pattern, recursive=True) if Path(item).is_file())
    safe: list[Path] = []
    for path in matches:
        try:
            path.relative_to(manifest_root.resolve())
        except ValueError as exc:
            raise BundleError(f"source {source['id']!r} escapes the manifest directory: {path}") from exc
        safe.append(path)
    if not safe and not source.get("allow_empty", False):
        raise BundleError(f"source {source['id']!r} path matched no files")
    return safe


def _filter_options(source: Mapping[str, Any], allowed: frozenset[str]) -> dict[str, str]:
    options = source.get("options", {})
    if not isinstance(options, dict):
        raise BundleError(f"source {source['id']!r} options must be an object")
    unknown = set(options) - allowed
    if unknown:
        raise BundleError(f"source {source['id']!r} uses unsupported options: {', '.join(sorted(unknown))}")
    return {str(key): str(value).lower() if isinstance(value, bool) else str(value) for key, value in options.items()}


def _structured_dataframe(
    spark: Any,
    source: Mapping[str, Any],
    paths: list[Path],
    pyspark: Mapping[str, Any],
) -> Any:
    F = pyspark["F"]
    path_values = [path.as_posix() for path in paths]
    if source["kind"] == "csv":
        configured = _filter_options(source, CSV_OPTIONS)
        if configured.get("mode", "FAILFAST").upper() != "FAILFAST":
            raise BundleError(f"source {source['id']!r} must use Spark mode FAILFAST")
        if configured.get("header", "true").lower() != "true":
            raise ValueError(f"CSV source {source['id']!r} must use header=true")
        options = {
            "header": "true",
            "encoding": "UTF-8",
            "mode": "FAILFAST",
            "enforceSchema": "false",
            **configured,
        }
        expected_columns = set(source["schema"])
        frames = []
        for path in paths:
            observed_columns = _csv_header(path, source, options)
            if len(observed_columns) != len(set(observed_columns)):
                raise ValueError(f"CSV source {source['id']!r} has duplicate header names in {path}")
            observed = set(observed_columns)
            if observed != expected_columns:
                missing = ", ".join(sorted(expected_columns - observed)) or "none"
                extra = ", ".join(sorted(observed - expected_columns)) or "none"
                raise ValueError(
                    f"CSV source {source['id']!r} header/schema mismatch in {path}: "
                    f"missing={missing}; extra={extra}"
                )
            schema = _source_schema(source, pyspark, observed_columns)
            current = spark.read.schema(schema).options(**options).csv(path.as_posix())
            current = current.withColumn(INTERNAL_SOURCE_PATH, F.input_file_name())
            invalid_fields = []
            for name in sorted(source["schema"]):
                if source["schema"][name] != "double":
                    continue
                value = _spark_column(F, name)
                non_finite = value.isNotNull() & (
                    F.isnan(value) | (F.abs(value) == F.lit(float("inf")))
                )
                invalid_fields.append(
                    F.when(non_finite, F.lit(f"field {name!r} must be a finite double"))
                )
            error_value = (
                F.concat_ws("; ", *invalid_fields) if invalid_fields else F.lit("")
            )
            current = current.withColumn(INTERNAL_NORMALIZATION_ERROR, error_value).select(
                *[_spark_column(F, name) for name in observed_columns],
                F.col(INTERNAL_SOURCE_PATH),
                F.col(INTERNAL_NORMALIZATION_ERROR),
            )
            frames.append(current)
        raw = frames[0]
        for frame in frames[1:]:
            raw = raw.unionByName(frame)
    else:
        schema = _source_schema(source, pyspark)
        configured = _filter_options(source, JSON_OPTIONS)
        if configured.get("mode", "FAILFAST").upper() != "FAILFAST":
            raise BundleError(f"source {source['id']!r} must use Spark mode FAILFAST")
        options = {
            "multiLine": "false",
            "encoding": "UTF-8",
            "mode": "FAILFAST",
            "allowComments": "false",
            "allowSingleQuotes": "false",
            "allowUnquotedFieldNames": "false",
            "allowNonNumericNumbers": "false",
            **configured,
        }
        raw = spark.read.schema(schema).options(**options).json(path_values)
        raw = raw.withColumn(INTERNAL_SOURCE_PATH, F.input_file_name()).withColumn(
            INTERNAL_NORMALIZATION_ERROR, F.lit("")
        )
    missing = {source["id_field"], source["title_field"], *source.get("fields", {}).keys()} - set(raw.columns)
    if missing:
        raise BundleError(f"source {source['id']!r} is missing columns: {', '.join(sorted(missing))}")
    selected_fields = sorted(source.get("fields", {}))
    attributes = (
        F.to_json(
            F.struct(*[_spark_column(F, name).alias(name) for name in selected_fields]),
            options={"ignoreNullFields": "false"},
        )
        if selected_fields
        else F.lit("{}")
    )
    def markdown_safe(column: Any) -> Any:
        value = F.coalesce(column.cast("string"), F.lit(""))
        value = F.regexp_replace(value, "&", "&amp;")
        value = F.regexp_replace(value, "<", "&lt;")
        value = F.regexp_replace(value, ">", "&gt;")
        return F.regexp_replace(value, r"[\r\n]+", " ↵ ")

    body_parts = [
        F.concat(F.lit(f"- **{name}**: "), markdown_safe(_spark_column(F, name)))
        for name in selected_fields
    ]
    body = F.concat(
        F.lit("# "),
        markdown_safe(_spark_column(F, source["title_field"])),
        F.lit("\n\n"),
        F.concat_ws("\n", *body_parts) if body_parts else F.lit(""),
    )
    return raw.select(
        F.lit(source["id"]).alias("source_id"),
        F.lit(source["kind"]).alias("source_kind"),
        F.col(INTERNAL_SOURCE_PATH).alias("source_path"),
        _spark_column(F, source["id_field"]).cast("string").alias("record_id"),
        F.lit("").alias("subject_iri"),
        _spark_column(F, source["title_field"]).cast("string").alias("title"),
        body.alias("body"),
        attributes.alias("attributes"),
        F.col(INTERNAL_NORMALIZATION_ERROR).alias("normalization_error"),
    )


def _whole_text_dataframe(
    spark: Any,
    source: Mapping[str, Any],
    paths: list[Path],
    manifest_root: Path,
    pyspark: Mapping[str, Any],
) -> Any:
    return _whole_text_sources_dataframe(
        spark, [(source, paths)], manifest_root, pyspark
    )


def _whole_text_records(
    row: Any,
    worker_sources: Mapping[str, list[Mapping[str, Any]]],
) -> list[tuple[str, ...]]:
    key = os.path.normcase(str(_local_path_from_uri(row.source_path).resolve()))
    sources = worker_sources.get(key)
    if not sources:
        raise ValueError(f"whole-text Spark input has no declared source mapping: {row.source_path}")
    records: list[tuple[str, ...]] = []
    for source in sources:
        if source["kind"] == "markdown":
            records.append(_markdown_record(row, source))
        else:
            records.extend(_rdf_records(row, source))
    return records


def _whole_text_sources_dataframe(
    spark: Any,
    sources_with_paths: list[tuple[Mapping[str, Any], list[Path]]],
    manifest_root: Path,
    pyspark: Mapping[str, Any],
) -> Any:
    """Normalize every Markdown/RDF source through one reusable PythonRDD."""

    F = pyspark["F"]
    schema = _normalized_schema(pyspark)
    paths = sorted(
        {path.resolve() for _, source_paths in sources_with_paths for path in source_paths},
        key=lambda path: path.as_posix(),
    )
    raw = spark.read.text([path.as_posix() for path in paths], wholetext=True).withColumn(
        "source_path", F.input_file_name()
    ).select("source_path", "value")
    worker_sources: dict[str, list[Mapping[str, Any]]] = {}
    for source, source_paths in sources_with_paths:
        worker_source = {**source, "_manifest_root": str(manifest_root.resolve())}
        for path in source_paths:
            key = os.path.normcase(str(path.resolve()))
            worker_sources.setdefault(key, []).append(worker_source)
    rows = raw.rdd.flatMap(lambda row: _whole_text_records(row, worker_sources))
    return spark.createDataFrame(rows, schema=schema)


def source_dataframe(
    spark: Any,
    source: Mapping[str, Any],
    paths: list[Path],
    manifest_root: Path,
    pyspark: Mapping[str, Any],
) -> Any:
    """Load one source through its real PySpark adapter."""

    if source["kind"] in {"csv", "json"}:
        return _structured_dataframe(spark, source, paths, pyspark)
    return _whole_text_dataframe(spark, source, paths, manifest_root, pyspark)


def _source_content_digests(
    spark: Any,
    paths_by_source: Mapping[str, list[Path]],
    manifest_root: Path,
    pyspark: Mapping[str, Any],
) -> dict[str, str]:
    """Hash a deterministic driver-side source snapshot without result sockets."""

    del spark, pyspark
    observed = {
        path.resolve(): hashlib.sha256(path.read_bytes()).hexdigest()
        for paths in paths_by_source.values()
        for path in paths
    }
    digests: dict[str, str] = {}
    root = manifest_root.resolve()
    for source_id, paths in paths_by_source.items():
        payload = [
            {
                "path": path.resolve().relative_to(root).as_posix(),
                "sha256": observed[path.resolve()],
            }
            for path in paths
        ]
        digests[source_id] = sha256_json(sorted(payload, key=lambda item: item["path"]))
    return digests


def _source_content_digest(
    spark: Any,
    paths: list[Path],
    manifest_root: Path,
    pyspark: Mapping[str, Any],
) -> str:
    """Compatibility wrapper for one source digest."""

    return _source_content_digests(
        spark, {"source": paths}, manifest_root, pyspark
    )["source"]


def create_spark(master: str, app_name: str, pyspark: Mapping[str, Any]) -> Any:
    """Create a deterministic local/cluster Spark session."""

    builder = (
        pyspark["SparkSession"].builder.master(master)
        .appName(app_name)
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.caseSensitive", "true")
        .config("spark.python.worker.reuse", "true")
        # This governs authenticated result sockets. Worker-process startup has
        # a separate fixed window in Spark 4.1.2, handled by the warm-up below.
        .config("spark.python.authenticate.socketTimeout", "120s")
    )
    if master.startswith("local"):
        os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
        os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
        os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
        builder = builder.config("spark.driver.host", "127.0.0.1").config(
            "spark.driver.bindAddress", "127.0.0.1"
        )
    return builder.getOrCreate()


def warm_python_workers(spark: Any) -> None:
    """Start reusable Python workers before a large heterogeneous plan is built."""

    partitions = max(1, min(2, spark.sparkContext.defaultParallelism))
    observed_count = (
        spark.sparkContext.parallelize(range(partitions), partitions)
        .map(lambda value: value)
        .count()
    )
    if observed_count != partitions:
        raise BundleError("Spark Python worker warm-up returned an unexpected result")


def build(manifest_path: Path, output: Path, master: str) -> dict[str, Any]:
    """Execute all Spark adapters and atomically materialize one bundle."""

    manifest_path = manifest_path.expanduser().resolve()
    manifest = load_manifest(manifest_path)
    root = manifest_path.parent
    pyspark = _load_pyspark()
    spark = create_spark(master, "build-semantic-okf", pyspark)
    spark.sparkContext.setLogLevel("ERROR")
    try:
        warm_python_workers(spark)
        frames = []
        whole_text_sources: list[tuple[Mapping[str, Any], list[Path]]] = []
        summaries = []
        paths_by_source: dict[str, list[Path]] = {}
        for source in manifest["sources"]:
            paths = discover_source_files(root, source)
            paths_by_source[source["id"]] = paths
            summaries.append(
                {
                    "id": source["id"],
                    "kind": source["kind"],
                    "path": source["path"],
                    "content_sha256": "",
                    "allow_empty": bool(source.get("allow_empty", False)),
                }
            )
            if paths:
                if source["kind"] in {"markdown", "rdf"}:
                    whole_text_sources.append((source, paths))
                else:
                    frames.append(source_dataframe(spark, source, paths, root, pyspark))
        if whole_text_sources:
            frames.append(
                _whole_text_sources_dataframe(spark, whole_text_sources, root, pyspark)
            )
        initial_digests = _source_content_digests(spark, paths_by_source, root, pyspark)
        for summary in summaries:
            summary["content_sha256"] = initial_digests[summary["id"]]
        if not frames:
            raise BundleError("no source produced a Spark DataFrame")
        normalized = frames[0]
        for frame in frames[1:]:
            normalized = normalized.unionByName(frame)
        # Whole-text adapters use Python workers. Cache the normalized relation so
        # validation and ordered collection do not execute every adapter twice.
        # This also keeps large heterogeneous plans reliable on local Windows
        # Spark, where repeatedly starting workers can exhaust the callback window.
        normalized = normalized.persist()
        normalization_failures = (
            normalized.filter(pyspark["F"].length(pyspark["F"].col("normalization_error")) > 0)
            .select("source_id", "record_id", "source_path", "normalization_error")
            .orderBy("source_id", "record_id", "source_path", "normalization_error")
        )
        # count() returns a scalar through Py4J and avoids opening an extra
        # authenticated result socket for the overwhelmingly common empty case.
        if normalization_failures.limit(1).count():
            failure = normalization_failures.first()
            raise ValueError(
                f"source {failure.source_id!r} record {failure.record_id!r} failed normalization: "
                f"{failure.normalization_error} ({failure.source_path})"
            )
        normalized = normalized.drop("normalization_error")
        normalized = normalized.orderBy("source_id", "record_id", "source_path")
        source_specs = source_by_id(manifest)
        summary_by_id = {item["id"]: item for item in summaries}
        # DataFrame.toLocalIterator uses a separate callback socket per ordered
        # iterator on classic Spark and is unreliable on local Windows. The
        # materializer is intentionally driver-side, so collect the already
        # cached, normalized projection in one bounded result transfer.
        normalized_rows = normalized.collect()
        records = [
            finalize_record(
                row.asDict(recursive=True),
                source_specs[row.source_id],
                summary_by_id[row.source_id],
                manifest,
                root,
            )
            for row in normalized_rows
        ]
        final_digests = _source_content_digests(spark, paths_by_source, root, pyspark)
        for summary in summaries:
            if final_digests[summary["id"]] != summary["content_sha256"]:
                raise BundleError(f"source {summary['id']!r} changed while Spark was normalizing it")
        spark_info = {
            "version": spark.version,
            "master": spark.sparkContext.master,
            "default_parallelism": spark.sparkContext.defaultParallelism,
            "records": len(records),
            "sources": len(summaries),
        }
        return materialize_bundle(output, manifest, records, summaries, spark_info)
    finally:
        spark.stop()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a coherent OKF/OWL/SHACL bundle through real PySpark adapters.",
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--master", default="local[2]")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def _error_code(exc: Exception) -> str:
    """Classify a user-facing build failure without importing optional Spark errors."""

    if isinstance(exc, ManifestError):
        return "manifest-error"
    if isinstance(exc, BundleError):
        return "shacl-nonconformant" if "SHACL non-conformant" in str(exc) else "semantic-error"
    if isinstance(exc, (OSError, ValueError)):
        return "source-error"
    module = type(exc).__module__
    if module.startswith(("pyspark", "py4j", "pyshacl", "rdflib")):
        return "processor-failure"
    return ""


def main(argv: list[str] | None = None) -> int:
    configure_utf8_output()
    args = build_parser().parse_args(argv)
    try:
        report = build(args.manifest, args.output, args.master)
    except Exception as exc:
        code = _error_code(exc)
        if not code:
            raise
        if args.output_format == "json":
            print(json.dumps({"status": "error", "code": code, "error": str(exc)}, sort_keys=True))
        else:
            print(f"{code}: {exc}", file=sys.stderr)
        return 2
    if args.output_format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Semantic OKF build passed: {args.output.resolve()}")
        print(f"Concepts: {report['summary']['concepts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
