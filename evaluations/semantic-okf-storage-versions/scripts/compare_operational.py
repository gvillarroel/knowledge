#!/usr/bin/env python3
"""Build and compare file-backed, embedding-backed, and Turso Semantic OKF releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


class ComparisonError(RuntimeError):
    """Describe an invalid input or failed comparison command."""


def canonical_json(value: Any) -> str:
    """Serialize a value with deterministic JSON ordering."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    """Return the physical SHA-256 digest of one file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    """Load one JSON object or raise a comparison error."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"Expected a JSON object for {label}: {path}")
    return value


def load_records(bundle: Path) -> list[dict[str, Any]]:
    """Load the canonical record ledger from a Semantic OKF bundle."""

    path = bundle / "semantic" / "records.jsonl"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines if line.strip()]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ComparisonError(
            f"Cannot read the record ledger at {path}: {exc}"
        ) from exc
    if not records or not all(isinstance(record, dict) for record in records):
        raise ComparisonError(f"Record ledger is empty or malformed: {path}")
    return records


def run_json_command(
    argv: Sequence[str], *, cwd: Path, timeout: float
) -> tuple[dict[str, Any], float]:
    """Run one command, parse its JSON stdout, and return elapsed milliseconds."""

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=timeout,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        raise ComparisonError(
            f"Command could not run: {' '.join(argv)}: {exc}"
        ) from exc
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if completed.returncode != 0:
        detail = (
            completed.stderr.strip()
            or completed.stdout.strip()
            or f"exit {completed.returncode}"
        )
        raise ComparisonError(f"Command failed: {' '.join(argv)}: {detail}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ComparisonError(
            f"Command emitted invalid JSON: {' '.join(argv)}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"Command did not emit a JSON object: {' '.join(argv)}")
    return value, elapsed_ms


def percentile(values: Sequence[float], fraction: float) -> float:
    """Return a linearly interpolated percentile for a non-empty sample."""

    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile requires at least one value")
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def measure_json_command(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout: float,
    iterations: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Warm one command, measure repeated subprocess runs, and retain the final payload."""

    payload, _ = run_json_command(argv, cwd=cwd, timeout=timeout)
    timings: list[float] = []
    for _ in range(iterations):
        payload, elapsed_ms = run_json_command(argv, cwd=cwd, timeout=timeout)
        timings.append(elapsed_ms)
    return payload, {
        "iterations": iterations,
        "scope": "fresh CLI subprocess including startup, validation, query, serialization, and parsing",
        "mean_ms": statistics.fmean(timings),
        "median_ms": statistics.median(timings),
        "p95_ms": percentile(timings, 0.95),
        "min_ms": min(timings),
        "max_ms": max(timings),
        "samples_ms": timings,
    }


def ordinary_tree_entries(
    root: Path, *, exclude_database: bool = False
) -> list[dict[str, Any]]:
    """Fingerprint sorted regular files below a bundle root."""

    entries: list[dict[str, Any]] = []
    for path in sorted(
        candidate for candidate in root.rglob("*") if candidate.is_file()
    ):
        relative = path.relative_to(root).as_posix()
        if relative.endswith(("-wal", "-shm", "-journal")):
            raise ComparisonError(f"Published database sidecar is not allowed: {path}")
        if exclude_database and relative == "semantic/knowledge.db":
            continue
        entries.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return entries


def tree_fingerprint(
    root: Path,
    *,
    exclude_database: bool = False,
    database_logical_sha256: str | None = None,
) -> dict[str, Any]:
    """Return one reproducible bundle fingerprint."""

    entries = ordinary_tree_entries(root, exclude_database=exclude_database)
    if database_logical_sha256 is not None:
        database = root / "semantic" / "knowledge.db"
        entries.append(
            {
                "path": "semantic/knowledge.db",
                "bytes": database.stat().st_size,
                "logical_sha256": database_logical_sha256,
            }
        )
        entries.sort(key=lambda item: item["path"])
    digest_entries = [
        {key: value for key, value in entry.items() if key != "bytes"}
        for entry in entries
    ]
    return {
        "file_count": len(entries),
        "total_bytes": sum(int(entry["bytes"]) for entry in entries),
        "logical_tree_sha256": hashlib.sha256(
            canonical_json(digest_entries).encode("utf-8")
        ).hexdigest(),
    }


def source_tree_fingerprint(root: Path) -> dict[str, Any]:
    """Fingerprint source files while excluding interpreter cache artifacts."""

    entries: list[dict[str, Any]] = []
    for path in sorted(
        candidate for candidate in root.rglob("*") if candidate.is_file()
    ):
        relative_path = path.relative_to(root)
        if "__pycache__" in relative_path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        entries.append(
            {
                "path": relative_path.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "file_count": len(entries),
        "total_bytes": sum(int(entry["bytes"]) for entry in entries),
        "logical_tree_sha256": hashlib.sha256(
            canonical_json(
                [
                    {"path": entry["path"], "sha256": entry["sha256"]}
                    for entry in entries
                ]
            ).encode("utf-8")
        ).hexdigest(),
    }


def validate_turso_database(
    repo_root: Path,
    bundle: Path,
    python_executable: str,
    timeout: float,
) -> tuple[dict[str, Any], float]:
    """Run the independent Turso relational validator."""

    script = (
        repo_root
        / "skills"
        / "build-semantic-okf-turso"
        / "scripts"
        / "validate_turso_store.py"
    )
    return run_json_command(
        [
            python_executable,
            str(script),
            str(bundle / "semantic" / "knowledge.db"),
            "--bundle",
            str(bundle),
            "--output-format",
            "json",
        ],
        cwd=repo_root,
        timeout=timeout,
    )


def build_pair(
    repo_root: Path,
    manifest: Path,
    work_root: Path,
    version: str,
    python_executable: str,
    timeout: float,
) -> dict[str, Any]:
    """Build two independent releases for one storage version."""

    if version not in {"file-backed", "turso-backed"}:
        raise ValueError(f"Unsupported build version: {version}")
    skill = (
        "build-semantic-okf" if version == "file-backed" else "build-semantic-okf-turso"
    )
    script = repo_root / "skills" / skill / "scripts" / "build_semantic_okf.py"
    outputs = [work_root / f"{version}-a", work_root / f"{version}-b"]
    timings: list[float] = []
    payloads: list[dict[str, Any]] = []
    for output in outputs:
        payload, elapsed_ms = run_json_command(
            [
                python_executable,
                str(script),
                str(manifest),
                str(output),
                "--output-format",
                "json",
            ],
            cwd=repo_root,
            timeout=timeout,
        )
        payloads.append(payload)
        timings.append(elapsed_ms)
    result: dict[str, Any] = {
        "outputs": [
            str(path.relative_to(repo_root)).replace("\\", "/") for path in outputs
        ],
        "build_ms": {
            "samples": timings,
            "mean": statistics.fmean(timings),
            "min": min(timings),
            "max": max(timings),
        },
        "builder_statuses": [payload.get("status") for payload in payloads],
    }
    if version == "file-backed":
        fingerprints = [tree_fingerprint(output) for output in outputs]
        result["logical_sha256"] = [
            item["logical_tree_sha256"] for item in fingerprints
        ]
        result["deterministic_rebuild"] = (
            fingerprints[0]["logical_tree_sha256"]
            == fingerprints[1]["logical_tree_sha256"]
        )
    else:
        validations: list[dict[str, Any]] = []
        validation_ms: list[float] = []
        fingerprints = []
        for output in outputs:
            validation, elapsed_ms = validate_turso_database(
                repo_root, output, python_executable, timeout
            )
            validations.append(validation)
            validation_ms.append(elapsed_ms)
            fingerprints.append(
                tree_fingerprint(
                    output,
                    exclude_database=True,
                    database_logical_sha256=str(validation["logical_sha256"]),
                )
            )
        result["database_logical_sha256"] = [
            item["logical_sha256"] for item in validations
        ]
        result["validation_ms"] = validation_ms
        result["logical_sha256"] = [
            item["logical_tree_sha256"] for item in fingerprints
        ]
        result["deterministic_rebuild"] = (
            fingerprints[0]["logical_tree_sha256"]
            == fingerprints[1]["logical_tree_sha256"]
        )
    result["bundles"] = outputs
    return result


def normalized_exact_record(record: dict[str, Any]) -> dict[str, Any]:
    """Select the shared exact-record contract returned by both consultants."""

    keys = (
        "attributes",
        "body",
        "concept_id",
        "concept_path",
        "concept_type",
        "ontology_class_iri",
        "origin_iri",
        "origins",
        "record_id",
        "record_sha256",
        "source_content_sha256",
        "source_id",
        "source_kind",
        "source_path",
        "source_refs",
        "subject_iri",
        "title",
    )
    return {key: record.get(key) for key in keys}


def normalize_legacy_aggregates(
    payload: dict[str, Any],
    records: Sequence[dict[str, Any]],
) -> list[tuple[str, str, int]]:
    """Convert typed SPARQL rows into source, concept type, and count tuples."""

    class_to_type = {
        str(record["ontology_class_iri"]): str(record["concept_type"])
        for record in records
    }
    result: list[tuple[str, str, int]] = []
    for row in payload.get("rows", []):
        result.append(
            (
                str(row["source_id"]["value"]),
                class_to_type[str(row["concept_type"]["value"])],
                int(row["record_count"]["value"]),
            )
        )
    return sorted(result)


def normalize_turso_aggregates(payload: dict[str, Any]) -> list[tuple[str, str, int]]:
    """Convert Turso SQL result rows into comparable tuples."""

    return sorted(
        (
            str(row["source_id"]),
            str(row["concept_type"]),
            int(row["record_count"]),
        )
        for row in payload.get("rows", [])
    )


def embedding_evidence(
    report_path: Path, run_manifest_path: Path, repo_root: Path
) -> dict[str, Any]:
    """Extract checked-in embedding quality, size, determinism, and build timing evidence."""

    report = load_json(report_path, "embedding comparison report")
    manifest = load_json(run_manifest_path, "embedding run manifest")
    routes: dict[str, Any] = {}
    for route in report.get("routes", []):
        paper = route["paper_metrics"]
        timing = route["timing_ms"]
        routes[str(route["name"])] = {
            "recall_at_10": paper["recall_at_10"],
            "mrr_at_10": paper["mrr_at_10"],
            "ndcg_at_10": paper["ndcg_at_10"],
            "evidence_validity": route["evidence_validity"]["ratio"],
            "mean_ms": timing["mean"],
            "p95_ms": timing["p95"],
            "errors": route["error_count"],
        }
    build_samples = [
        float(command["elapsed_ms"])
        for command in manifest.get("commands", [])
        if str(command.get("name", "")).startswith("build-embedding-")
    ]
    output = manifest["outputs"]["embedding_a"]
    return {
        "status": manifest.get("status"),
        "model": manifest.get("model"),
        "bundle": {
            "file_count": output["file_count"],
            "total_bytes": output["total_bytes"],
            "logical_tree_sha256": output["logical_tree_sha256"],
        },
        "build_ms": {
            "samples": build_samples,
            "mean": statistics.fmean(build_samples),
            "min": min(build_samples),
            "max": max(build_samples),
        },
        "deterministic_rebuild": manifest["deterministic_rebuild"]["status"] == "pass",
        "core_semantic_parity": report["core_semantic_parity"]["status"],
        "routes": routes,
        "timing_warning": report["timing_methodology"]["interpretation"],
        "evidence_paths": {
            "report": {
                "path": str(report_path.relative_to(repo_root)).replace("\\", "/"),
                "sha256": sha256_file(report_path),
            },
            "run_manifest": {
                "path": str(run_manifest_path.relative_to(repo_root)).replace(
                    "\\", "/"
                ),
                "sha256": sha256_file(run_manifest_path),
            },
        },
    }


def format_ms(value: float | None) -> str:
    """Format an optional millisecond value for Markdown."""

    return "n/a" if value is None else f"{value:.1f}"


def render_markdown(report: dict[str, Any]) -> str:
    """Render the machine-readable comparison as a concise decision report."""

    versions = report["versions"]
    operational = report["operational_queries"]
    embedding = versions["embedding-backed"]
    file_build_ms = float(versions["file-backed"]["build_ms"]["mean"])
    turso_build_ms = float(versions["turso-backed"]["build_ms"]["mean"])
    turso_build_overhead = (turso_build_ms / file_build_ms - 1.0) * 100.0
    turso_size_multiple = float(
        versions["turso-backed"]["bundle"]["total_bytes"]
    ) / float(versions["file-backed"]["bundle"]["total_bytes"])
    file_exact_ms = float(operational["exact_record"]["file-backed"]["median_ms"])
    turso_exact_ms = float(operational["exact_record"]["turso-backed"]["median_ms"])
    turso_exact_overhead = (turso_exact_ms / file_exact_ms - 1.0) * 100.0
    file_aggregate_ms = float(operational["aggregate"]["file-backed"]["median_ms"])
    turso_aggregate_ms = float(operational["aggregate"]["turso-backed"]["median_ms"])
    turso_aggregate_gain = (1.0 - turso_aggregate_ms / file_aggregate_ms) * 100.0
    lines = [
        "# Semantic OKF Storage Version Comparison",
        "",
        f"Status: **{report['status']}**. Corpus: {report['corpus']['records']} records from "
        f"{report['corpus']['sources']} sources.",
        "",
        "## Outcome",
        "",
        "No version dominates every workload. The file-backed release remains the smallest and most portable baseline. "
        "The embedding-backed release uniquely exposes vector and hybrid discovery, but its measured routes did not beat "
        "the legacy lexical baseline on recall or nDCG in this corpus. The Turso-backed release adds bounded SQL and indexed "
        "relational rows while preserving byte-identical authoritative Semantic OKF files.",
        "",
        "## Build and storage",
        "",
        "| Version | Files | Bytes | Mean build ms | Deterministic rebuild | Authoritative core parity |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("file-backed", "embedding-backed", "turso-backed"):
        item = versions[name]
        lines.append(
            f"| {name} | {item['bundle']['file_count']} | {item['bundle']['total_bytes']} | "
            f"{format_ms(item['build_ms']['mean'])} | "
            f"{'pass' if item['deterministic_rebuild'] else 'fail'} | {item['core_semantic_parity']} |"
        )
    lines.extend(
        [
            "",
            "Build timings are fresh CLI subprocess measurements for file-backed and Turso-backed releases. "
            "Embedding build timings come from its append-only, offline SentenceTransformers run manifest because "
            "that model-backed evaluation already performed two verified builds on the same manifest.",
            "",
            f"Relative to the file-backed baseline, Turso used {turso_size_multiple:.2f}x the storage and its build "
            f"was {turso_build_overhead:.1f}% slower in this run.",
            "",
            "## Exact and aggregate consultation",
            "",
            "| Operation | File-backed median ms | Turso-backed median ms | Result parity |",
            "| --- | ---: | ---: | ---: |",
            f"| Exact `(source_id, record_id)` lookup | {format_ms(operational['exact_record']['file-backed']['median_ms'])} | "
            f"{format_ms(operational['exact_record']['turso-backed']['median_ms'])} | "
            f"{'pass' if operational['exact_record']['result_parity'] else 'fail'} |",
            f"| Group by source and type | {format_ms(operational['aggregate']['file-backed']['median_ms'])} | "
            f"{format_ms(operational['aggregate']['turso-backed']['median_ms'])} | "
            f"{'pass' if operational['aggregate']['result_parity'] else 'fail'} |",
            "",
            "Each latency is a fresh end-to-end CLI subprocess, including startup and the version's integrity checks. "
            "It is not an in-process engine microbenchmark.",
            "",
            f"For this corpus, Turso's single exact lookup was {turso_exact_overhead:.1f}% slower, while its grouped "
            f"aggregation was {turso_aggregate_gain:.1f}% faster. Batch related structured work into one bounded SQL "
            "query instead of paying the verification boundary for many small CLI calls.",
            "",
            "## Embedding retrieval evidence",
            "",
            "| Route | Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Mean ms |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for route_name in ("legacy_lexical", "new_lexical", "vector", "hybrid"):
        route = embedding["routes"][route_name]
        lines.append(
            f"| {route_name} | {route['recall_at_10']:.4f} | {route['mrr_at_10']:.4f} | "
            f"{route['ndcg_at_10']:.4f} | {route['evidence_validity']:.4f} | {route['mean_ms']:.1f} |"
        )
    lines.extend(
        [
            "",
            f"Timing caveat: {embedding['timing_warning']}",
            "",
            "## Capability decision matrix",
            "",
            "| Need | Preferred version | Reason |",
            "| --- | --- | --- |",
            "| Lowest dependency and storage overhead | file-backed | JSONL, Markdown, and RDF remain directly inspectable and require no additional index engine. |",
            "| Single exact record lookup on this corpus | file-backed | Its end-to-end CLI median was lower while returning the same authoritative record. |",
            "| Paraphrase-oriented candidate discovery | embedding-backed, after quality tuning | It uniquely offers vector and hybrid retrieval, but the measured vector and hybrid routes trailed legacy lexical recall and nDCG. |",
            "| Joins, grouping, and batched structured queries | Turso-backed | Prepared filters and one bounded SQL statement operate over indexed relational rows; grouping was faster in this run. |",
            "| Direct standards-based graph queries | file-backed or embedding-backed | Their consultation path exposes local SPARQL over the authoritative RDF graphs. |",
            "| SQL-oriented agent tooling with preserved evidence | Turso-backed | Records, attributes, concepts, artifacts, and selected RDF statements are queryable while original files remain authoritative. |",
            "| Smallest distributable artifact | file-backed | It avoids both vectors and the duplicated relational projection. |",
            "",
            "## Integrity findings",
            "",
            f"- File/Turso record-ledger parity: **{'pass' if report['parity']['records'] else 'fail'}**.",
            f"- File/Turso authoritative core byte parity: **{'pass' if report['parity']['authoritative_core'] else 'fail'}**.",
            f"- Query result parity: **{'pass' if report['parity']['queries'] else 'fail'}**.",
            f"- Published release bytes unchanged by consultation: **{'pass' if report['parity']['read_only'] else 'fail'}**.",
            f"- Turso logical database digest: `{versions['turso-backed']['database_logical_sha256']}`.",
            "",
            "## Interpretation",
            "",
            "Keep file-backed as the default portability and minimum-footprint release. Choose Turso when the workload can "
            "benefit from batched relational joins, grouping, or agent-authored bounded SQL; it is not automatically faster "
            "for one exact lookup because every CLI call preserves a full verification boundary. Choose embeddings only "
            "when paraphrase-oriented candidate discovery is required, and retune or re-evaluate its retrieval plan before "
            "assuming the additional model, build time, and storage improve quality.",
            "",
        ]
    )
    return "\n".join(lines)


def compare(args: argparse.Namespace) -> dict[str, Any]:
    """Run the complete operational comparison and return its report."""

    repo_root = args.repo_root.resolve()
    manifest = args.manifest.resolve()
    query_file = args.aggregate_query.resolve()
    work_root = args.work_root.resolve()
    if work_root.exists():
        raise ComparisonError(f"Work root must not already exist: {work_root}")
    work_root.mkdir(parents=True)

    file_build = build_pair(
        repo_root,
        manifest,
        work_root,
        "file-backed",
        args.python_executable,
        args.timeout_seconds,
    )
    turso_build = build_pair(
        repo_root,
        manifest,
        work_root,
        "turso-backed",
        args.python_executable,
        args.timeout_seconds,
    )
    file_bundle = file_build.pop("bundles")[0]
    turso_bundle = turso_build.pop("bundles")[0]
    file_records = load_records(file_bundle)
    turso_records = load_records(turso_bundle)

    file_core_entries = ordinary_tree_entries(file_bundle)
    turso_core_entries = ordinary_tree_entries(turso_bundle, exclude_database=True)
    authoritative_core_parity = file_core_entries == turso_core_entries
    record_parity = file_records == turso_records

    turso_validation, turso_validation_ms = validate_turso_database(
        repo_root, turso_bundle, args.python_executable, args.timeout_seconds
    )
    turso_logical_sha256 = str(turso_validation["logical_sha256"])
    file_fingerprint_before = tree_fingerprint(file_bundle)
    turso_database = turso_bundle / "semantic" / "knowledge.db"
    turso_database_sha256_before = sha256_file(turso_database)
    turso_fingerprint_before = tree_fingerprint(
        turso_bundle,
        exclude_database=True,
        database_logical_sha256=turso_logical_sha256,
    )

    sample = file_records[0]
    file_query_script = (
        repo_root
        / "skills"
        / "consult-semantic-okf"
        / "scripts"
        / "query_semantic_okf.py"
    )
    turso_query_script = (
        repo_root
        / "skills"
        / "consult-semantic-okf-turso"
        / "scripts"
        / "query_turso_knowledge.py"
    )
    file_exact_argv = [
        args.python_executable,
        str(file_query_script),
        str(file_bundle),
        "ledger",
        "--source-id",
        str(sample["source_id"]),
        "--record-id",
        str(sample["record_id"]),
        "--show-content",
        "--format",
        "json",
    ]
    turso_exact_argv = [
        args.python_executable,
        str(turso_query_script),
        str(turso_bundle / "semantic" / "knowledge.db"),
        "records",
        "--source-id",
        str(sample["source_id"]),
        "--record-id",
        str(sample["record_id"]),
        "--show-body",
        "--format",
        "json",
    ]
    file_exact, file_exact_timing = measure_json_command(
        file_exact_argv,
        cwd=repo_root,
        timeout=args.timeout_seconds,
        iterations=args.iterations,
    )
    turso_exact, turso_exact_timing = measure_json_command(
        turso_exact_argv,
        cwd=repo_root,
        timeout=args.timeout_seconds,
        iterations=args.iterations,
    )
    exact_parity = (
        file_exact.get("returned") == 1
        and turso_exact.get("returned") == 1
        and normalized_exact_record(file_exact["records"][0])
        == normalized_exact_record(turso_exact["records"][0])
    )

    sql = (
        "SELECT source_id, concept_type, COUNT(*) AS record_count FROM records "
        "GROUP BY source_id, concept_type ORDER BY source_id, concept_type"
    )
    file_aggregate_argv = [
        args.python_executable,
        str(file_query_script),
        str(file_bundle),
        "sparql",
        "--query-file",
        str(query_file),
        "--graph",
        "data",
        "--format",
        "json",
    ]
    turso_aggregate_argv = [
        args.python_executable,
        str(turso_query_script),
        str(turso_bundle / "semantic" / "knowledge.db"),
        "sql",
        "--query",
        sql,
        "--all",
        "--format",
        "json",
    ]
    file_aggregate, file_aggregate_timing = measure_json_command(
        file_aggregate_argv,
        cwd=repo_root,
        timeout=args.timeout_seconds,
        iterations=args.iterations,
    )
    turso_aggregate, turso_aggregate_timing = measure_json_command(
        turso_aggregate_argv,
        cwd=repo_root,
        timeout=args.timeout_seconds,
        iterations=args.iterations,
    )
    expected_aggregate = sorted(
        (source_id, concept_type, count)
        for (source_id, concept_type), count in Counter(
            (str(record["source_id"]), str(record["concept_type"]))
            for record in file_records
        ).items()
    )
    legacy_aggregate = normalize_legacy_aggregates(file_aggregate, file_records)
    database_aggregate = normalize_turso_aggregates(turso_aggregate)
    aggregate_parity = legacy_aggregate == database_aggregate == expected_aggregate

    file_fingerprint_after = tree_fingerprint(file_bundle)
    turso_validation_after, _ = validate_turso_database(
        repo_root, turso_bundle, args.python_executable, args.timeout_seconds
    )
    turso_fingerprint_after = tree_fingerprint(
        turso_bundle,
        exclude_database=True,
        database_logical_sha256=str(turso_validation_after["logical_sha256"]),
    )
    turso_database_sha256_after = sha256_file(turso_database)
    read_only = (
        file_fingerprint_before == file_fingerprint_after
        and turso_fingerprint_before == turso_fingerprint_after
        and turso_database_sha256_before == turso_database_sha256_after
    )

    embedding = embedding_evidence(
        args.embedding_report.resolve(),
        args.embedding_run_manifest.resolve(),
        repo_root,
    )
    file_bundle_fingerprint = tree_fingerprint(file_bundle)
    turso_bundle_fingerprint = tree_fingerprint(
        turso_bundle,
        exclude_database=True,
        database_logical_sha256=turso_logical_sha256,
    )
    file_version = {
        "bundle": file_bundle_fingerprint,
        "build_ms": file_build["build_ms"],
        "deterministic_rebuild": file_build["deterministic_rebuild"],
        "core_semantic_parity": "baseline",
    }
    turso_version = {
        "bundle": turso_bundle_fingerprint,
        "build_ms": turso_build["build_ms"],
        "deterministic_rebuild": turso_build["deterministic_rebuild"],
        "core_semantic_parity": "pass" if authoritative_core_parity else "fail",
        "database_logical_sha256": turso_logical_sha256,
        "database_validation_ms": turso_validation_ms,
        "database_summary": turso_validation["summary"],
    }
    all_pass = all(
        (
            file_build["deterministic_rebuild"],
            turso_build["deterministic_rebuild"],
            embedding["deterministic_rebuild"],
            embedding["core_semantic_parity"] == "pass",
            authoritative_core_parity,
            record_parity,
            exact_parity,
            aggregate_parity,
            read_only,
        )
    )
    return {
        "schema_version": "1.0",
        "status": "pass" if all_pass else "fail",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "inputs": {
            "manifest": {
                "path": str(manifest.relative_to(repo_root)).replace("\\", "/"),
                "sha256": sha256_file(manifest),
            },
            "aggregate_query": {
                "path": str(query_file.relative_to(repo_root)).replace("\\", "/"),
                "sha256": sha256_file(query_file),
            },
            "iterations": args.iterations,
            "comparator": {
                "path": str(Path(__file__).resolve().relative_to(repo_root)).replace(
                    "\\", "/"
                ),
                "sha256": sha256_file(Path(__file__).resolve()),
            },
            "skill_packages": {
                version: {
                    authority: source_tree_fingerprint(
                        repo_root / "skills" / skill_name
                    )
                    for authority, skill_name in skills.items()
                }
                for version, skills in {
                    "file-backed": {
                        "build": "build-semantic-okf",
                        "consult": "consult-semantic-okf",
                    },
                    "embedding-backed": {
                        "build": "build-semantic-okf-embeddings",
                        "consult": "consult-semantic-okf-embeddings",
                    },
                    "turso-backed": {
                        "build": "build-semantic-okf-turso",
                        "consult": "consult-semantic-okf-turso",
                    },
                }.items()
            },
        },
        "corpus": {
            "records": len(file_records),
            "sources": len({str(record["source_id"]) for record in file_records}),
            "sample": {
                "source_id": sample["source_id"],
                "record_id": sample["record_id"],
                "concept_id": sample["concept_id"],
            },
        },
        "versions": {
            "file-backed": file_version,
            "embedding-backed": embedding,
            "turso-backed": turso_version,
        },
        "operational_queries": {
            "exact_record": {
                "file-backed": file_exact_timing,
                "turso-backed": turso_exact_timing,
                "result_parity": exact_parity,
            },
            "aggregate": {
                "file-backed": file_aggregate_timing,
                "turso-backed": turso_aggregate_timing,
                "result_parity": aggregate_parity,
                "groups": len(expected_aggregate),
            },
        },
        "parity": {
            "authoritative_core": authoritative_core_parity,
            "records": record_parity,
            "queries": exact_parity and aggregate_parity,
            "read_only": read_only,
            "turso_database_sha256_before": turso_database_sha256_before,
            "turso_database_sha256_after": turso_database_sha256_after,
        },
        "work_root": str(work_root.relative_to(repo_root)).replace("\\", "/"),
    }


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    script = Path(__file__).resolve()
    repo_root = script.parents[3]
    evaluation = script.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root / "evaluations" / "graphrag-cross-paper" / "manifest.json",
    )
    parser.add_argument(
        "--aggregate-query",
        type=Path,
        default=evaluation / "queries" / "count-by-source-and-type.rq",
    )
    parser.add_argument(
        "--embedding-report",
        type=Path,
        default=repo_root
        / "evaluations"
        / "semantic-okf-embeddings"
        / "comparison-report.json",
    )
    parser.add_argument(
        "--embedding-run-manifest",
        type=Path,
        default=(
            repo_root
            / "evaluations"
            / "semantic-okf-embeddings"
            / "results"
            / "runs"
            / "20260713-compact-final"
            / "run-manifest.json"
        ),
    )
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument(
        "--output-json", type=Path, default=evaluation / "operational-report.json"
    )
    parser.add_argument(
        "--output-markdown", type=Path, default=evaluation / "operational-report.md"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the comparison and write JSON plus Markdown reports."""

    args = build_parser().parse_args(argv)
    if args.iterations < 1:
        print("comparison error: --iterations must be at least 1", file=sys.stderr)
        return 2
    try:
        report = compare(args)
    except ComparisonError as exc:
        print(f"comparison error: {exc}", file=sys.stderr)
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
    print(
        canonical_json(
            {"status": report["status"], "records": report["corpus"]["records"]}
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
