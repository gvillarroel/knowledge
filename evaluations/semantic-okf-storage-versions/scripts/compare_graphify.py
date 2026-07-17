#!/usr/bin/env python3
"""Compare Graphify-backed Semantic OKF with the checked-in storage baselines."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence


EXPECTED_MANIFEST_SHA256 = "a4e83ce7d9630bf57ce4b3c2bf2cb445e34032c3ec46673b4bbed585885b0c37"
EXPECTED_QRELS_SHA256 = "fc583fc4cfdb8c392b8e53e929b5b052a86b0d288297a1d73723ee53feec175a"
EXPECTED_PRIOR_REPORT_SHA256 = "6fe835c258e643052975dc4a4382383711cca2102074a7d9295ff29297f34cce"
EXPECTED_RECORDS = 874
EXPECTED_SOURCES = 31
RECORD_DIGEST_FIELDS = (
    "source_id",
    "source_kind",
    "source_path",
    "record_id",
    "subject_iri",
    "ontology_class_iri",
    "concept_type",
    "title",
    "body",
    "attributes",
)


class ComparisonError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"{label} must contain a JSON object")
    return value


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ComparisonError(f"cannot read {label}: {exc}") from exc
    for number, line in enumerate(lines, 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ComparisonError(f"invalid JSON at {label}:{number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ComparisonError(f"{label}:{number} must contain an object")
        result.append(value)
    return result


def tree_entries(root: Path, *, exclude_graphify: bool = False) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(
        (candidate for candidate in root.rglob("*") if candidate.is_file()),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root).as_posix()
        if exclude_graphify and (
            relative == "retrieval/graphify" or relative.startswith("retrieval/graphify/")
        ):
            continue
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return entries


def tree_fingerprint(root: Path, *, exclude_graphify: bool = False) -> dict[str, Any]:
    entries = tree_entries(root, exclude_graphify=exclude_graphify)
    digest_entries = [{"path": item["path"], "sha256": item["sha256"]} for item in entries]
    return {
        "file_count": len(entries),
        "logical_tree_sha256": hashlib.sha256(
            canonical_json(digest_entries).encode("utf-8")
        ).hexdigest(),
        "total_bytes": sum(int(item["bytes"]) for item in entries),
    }


def source_tree_fingerprint(root: Path) -> dict[str, Any]:
    entries = [
        item
        for item in tree_entries(root)
        if "__pycache__" not in Path(item["path"]).parts
        and not item["path"].endswith((".pyc", ".pyo"))
    ]
    return {
        "file_count": len(entries),
        "logical_tree_sha256": hashlib.sha256(
            canonical_json(
                [{"path": item["path"], "sha256": item["sha256"]} for item in entries]
            ).encode("utf-8")
        ).hexdigest(),
        "total_bytes": sum(int(item["bytes"]) for item in entries),
    }
def run_json(
    argv: Sequence[str], *, cwd: Path, timeout: int
) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    process = subprocess.run(
        list(argv),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=timeout,
        check=False,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if process.returncode != 0:
        raise ComparisonError(
            f"command failed ({process.returncode}): {' '.join(argv)}\n{process.stderr or process.stdout}"
        )
    lines = [line for line in process.stdout.splitlines() if line.strip()]
    if not lines:
        raise ComparisonError(f"command emitted no JSON: {' '.join(argv)}")
    try:
        value = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise ComparisonError(f"command did not end in JSON: {' '.join(argv)}") from exc
    if not isinstance(value, dict):
        raise ComparisonError("command JSON result must be an object")
    return value, elapsed_ms


def percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        raise ComparisonError("cannot calculate a percentile of no values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower))


def timing_summary(values: Sequence[float]) -> dict[str, Any]:
    return {
        "max_ms": max(values),
        "mean_ms": statistics.fmean(values),
        "median_ms": statistics.median(values),
        "min_ms": min(values),
        "p95_ms": percentile(values, 0.95),
        "samples_ms": list(values),
    }


def measure_json(
    argv: Sequence[str], *, cwd: Path, timeout: int, iterations: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload: dict[str, Any] | None = None
    timings: list[float] = []
    for _ in range(iterations):
        current, elapsed = run_json(argv, cwd=cwd, timeout=timeout)
        if payload is not None:
            stable_payload = {key: value for key, value in payload.items() if key != "read_only_sha256"}
            stable_current = {key: value for key, value in current.items() if key != "read_only_sha256"}
            if stable_payload != stable_current:
                raise ComparisonError("repeated query returned different logical JSON")
        payload = current
        timings.append(elapsed)
    assert payload is not None
    return payload, timing_summary(timings)


def recall_at_k(ranked: Sequence[str], relevant: set[str], k: int = 10) -> float:
    return len(set(ranked[:k]) & relevant) / len(relevant) if relevant else 0.0


def mrr_at_k(ranked: Sequence[str], relevant: set[str], k: int = 10) -> float:
    for index, item in enumerate(ranked[:k], 1):
        if item in relevant:
            return 1.0 / index
    return 0.0


def ndcg_at_k(ranked: Sequence[str], relevant: set[str], k: int = 10) -> float:
    dcg = sum(
        1.0 / math.log2(index + 1)
        for index, item in enumerate(ranked[:k], 1)
        if item in relevant
    )
    ideal = sum(1.0 / math.log2(index + 1) for index in range(1, min(k, len(relevant)) + 1))
    return dcg / ideal if ideal else 0.0


def deduplicate(values: Iterable[str | None]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def iter_scalars(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, (bool, int)):
        yield str(value)
    elif isinstance(value, float) and math.isfinite(value):
        yield str(value)
    elif isinstance(value, list):
        for item in value:
            yield from iter_scalars(item)


def derive_paper_id(
    record: dict[str, Any], subject_records: dict[str, dict[str, Any]]
) -> str | None:
    attributes = record.get("attributes")
    if isinstance(attributes, dict):
        direct = attributes.get("paper_id")
        if isinstance(direct, str) and direct:
            return direct
        for value in attributes.values():
            for scalar in iter_scalars(value):
                target = subject_records.get(scalar)
                target_attributes = target.get("attributes") if target else None
                candidate = (
                    target_attributes.get("paper_id")
                    if isinstance(target_attributes, dict)
                    else None
                )
                if isinstance(candidate, str) and candidate:
                    return candidate
    match = re.search(
        r"(?:^|[-/])(\d{4}\.\d{5}v\d+)(?:$|[-/])", str(record.get("source_id", ""))
    )
    return match.group(1) if match else None


def record_digest(record: dict[str, Any]) -> str:
    try:
        payload = {field: record[field] for field in RECORD_DIGEST_FIELDS}
    except KeyError as exc:
        raise ComparisonError(f"ledger record omits digest field: {exc.args[0]}") from exc
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_hit_evidence(
    bundle: Path,
    hit: dict[str, Any],
    ledger_by_identity: dict[tuple[str, str], dict[str, Any]],
    subject_records: dict[str, dict[str, Any]],
) -> tuple[bool, str | None, list[str]]:
    issues: list[str] = []
    source_id = hit.get("source_id")
    record_id = hit.get("record_id")
    ledger = (
        ledger_by_identity.get((source_id, record_id))
        if isinstance(source_id, str) and isinstance(record_id, str)
        else None
    )
    if ledger is None:
        return False, None, ["no authoritative ledger record matches source_id and record_id"]

    expected_paper_id = derive_paper_id(ledger, subject_records)
    expected_fields = {
        "attributes": ledger.get("attributes"),
        "concept_id": ledger.get("concept_id"),
        "concept_path": ledger.get("concept_path"),
        "concept_type": ledger.get("concept_type"),
        "paper_id": expected_paper_id,
        "record_id": ledger.get("record_id"),
        "record_sha256": ledger.get("record_sha256"),
        "source_id": ledger.get("source_id"),
        "source_path": ledger.get("source_path"),
        "title": ledger.get("title"),
    }
    for field, expected in expected_fields.items():
        if hit.get(field) != expected:
            issues.append(f"{field} does not match the authoritative ledger")
    if ledger.get("record_sha256") != record_digest(ledger):
        issues.append("authoritative record_sha256 does not hash the normalized record")

    concept_path = hit.get("concept_path")
    concept: Path | None = None
    if not isinstance(concept_path, str) or not concept_path:
        issues.append("concept_path is missing")
    else:
        pure = PurePosixPath(concept_path)
        if (
            pure.is_absolute()
            or ".." in pure.parts
            or "\\" in concept_path
            or not pure.parts
            or pure.parts[0] != "concepts"
        ):
            issues.append("concept_path is outside the safe concepts/ scope")
        else:
            concept = bundle / pure
            if not concept.is_file() or concept.is_symlink():
                issues.append("concept_path does not resolve to a regular concept file")
                concept = None
    if concept is not None:
        actual_sha256 = sha256_file(concept)
        if hit.get("concept_sha256") != actual_sha256:
            issues.append("concept_sha256 does not match the concept file")
        evidence = hit.get("evidence")
        if evidence != {
            "kind": "concept-file",
            "path": concept_path,
            "sha256": actual_sha256,
        }:
            issues.append("evidence locator does not identify the exact concept file")
        try:
            content = concept.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append(f"concept file cannot be read as UTF-8: {exc}")
        else:
            if hit.get("content") != content:
                issues.append("returned content is not the exact concept file")
            marker = "\n---\n\n"
            boundary = content.find(marker, 4) if content.startswith("---\n") else -1
            expected_body = str(ledger.get("body") or f"# {ledger.get('title', '')}").rstrip() + "\n"
            if boundary < 0 or content[boundary + len(marker) :] != expected_body:
                issues.append("concept body is not the exact authoritative ledger body")
    return not issues, expected_paper_id, issues


def evaluate_graphify_queries(
    query_script: Path,
    bundle: Path,
    questions: list[dict[str, Any]],
    *,
    python: str,
    repo_root: Path,
    timeout: int,
) -> dict[str, Any]:
    ledger_records = load_jsonl(bundle / "semantic/records.jsonl", "Graphify record ledger")
    ledger_by_identity = {
        (str(record.get("source_id")), str(record.get("record_id"))): record
        for record in ledger_records
    }
    if len(ledger_by_identity) != len(ledger_records):
        raise ComparisonError("Graphify ledger contains duplicate source/record identities")
    subject_records = {
        str(record.get("subject_iri")): record
        for record in ledger_records
        if isinstance(record.get("subject_iri"), str) and record.get("subject_iri")
    }
    cases: list[dict[str, Any]] = []
    errors = 0
    timings: list[float] = []
    evidence_total = 0
    evidence_valid = 0
    for question in questions:
        argv = [
            python,
            str(query_script),
            str(bundle),
            "search",
            str(question["question"]),
            "--depth",
            "2",
            "--top-k",
            "10",
            "--show-content",
        ]
        try:
            payload, elapsed = run_json(argv, cwd=repo_root, timeout=timeout)
        except ComparisonError as exc:
            errors += 1
            cases.append({"id": question.get("id"), "error": str(exc)})
            continue
        timings.append(elapsed)
        records = payload.get("records")
        if not isinstance(records, list):
            errors += 1
            cases.append({"id": question.get("id"), "error": "records is not an array"})
            continue
        relevant = set(question["qrels"]["paper_ids"])
        valid_case = True
        case_issues: list[dict[str, Any]] = []
        validated_paper_ids: list[str | None] = []
        for record in records:
            evidence_total += 1
            if not isinstance(record, dict):
                valid_case = False
                case_issues.append({"rank": len(case_issues) + 1, "issues": ["hit is not an object"]})
                continue
            valid, paper_id, issues = validate_hit_evidence(
                bundle, record, ledger_by_identity, subject_records
            )
            validated_paper_ids.append(paper_id if valid else None)
            if valid:
                evidence_valid += 1
            else:
                valid_case = False
                case_issues.append({"rank": len(validated_paper_ids), "issues": issues})
        ranked = deduplicate(validated_paper_ids)
        cases.append(
            {
                "evidence_valid": valid_case,
                "evidence_issues": case_issues,
                "id": question["id"],
                "latency_ms": elapsed,
                "mrr_at_10": mrr_at_k(ranked, relevant),
                "ndcg_at_10": ndcg_at_k(ranked, relevant),
                "paper_ids": ranked,
                "recall_at_10": recall_at_k(ranked, relevant),
                "returned_records": len(records),
            }
        )
    successful = [case for case in cases if "error" not in case]
    return {
        "cases": cases,
        "errors": errors,
        "evidence_total": evidence_total,
        "evidence_valid": evidence_valid,
        "evidence_validity": evidence_valid / evidence_total if evidence_total else 0.0,
        "mean_ms": statistics.fmean(timings) if timings else None,
        "mrr_at_10": statistics.fmean(case["mrr_at_10"] for case in successful) if successful else 0.0,
        "ndcg_at_10": statistics.fmean(case["ndcg_at_10"] for case in successful) if successful else 0.0,
        "p95_ms": percentile(timings, 0.95) if timings else None,
        "questions": len(questions),
        "recall_at_10": statistics.fmean(case["recall_at_10"] for case in successful) if successful else 0.0,
        "scope": "fresh validated CLI subprocess; Graphify lexical scoring plus BFS depth 2; authoritative concept hydration",
        "top_k": 10,
    }


def render_markdown(report: dict[str, Any]) -> str:
    versions = report["versions"]
    operations = report["operational_queries"]
    graphify = versions["graphify-backed"]
    routes = report["retrieval_routes"]
    lines = [
        "# Semantic OKF Graphify Storage Comparison",
        "",
        f"Status: **{report['status']}**. Corpus: {report['corpus']['records']} records from {report['corpus']['sources']} sources; retrieval set: {report['corpus']['questions']} questions.",
        "",
        "## Build and artifact cost",
        "",
        "| Version | Files | Bytes | Mean build (ms) | Deterministic |",
        "|---|---:|---:|---:|---|",
    ]
    for name in ("file-backed", "embedding-backed", "turso-backed", "graphify-backed"):
        value = versions[name]
        build = value["build_ms"]
        mean = build.get("mean", build.get("mean_ms"))
        lines.append(
            f"| {name} | {value['bundle']['file_count']} | {value['bundle']['total_bytes']} | {mean:.1f} | {'pass' if value['deterministic_rebuild'] else 'fail'} |"
        )
    lines.extend(
        [
            "",
            "Graphify build time includes the unchanged Semantic OKF build, deterministic temporary-view generation, structural extraction, canonical serialization, and full validation. Historical embedding timing uses its append-only offline model run.",
            "",
            "## Authoritative operations",
            "",
            "| Operation | File median (ms) | Turso median (ms) | Graphify median (ms) |",
            "|---|---:|---:|---:|",
            f"| Exact record | {operations['exact_record']['file-backed']['median_ms']:.1f} | {operations['exact_record']['turso-backed']['median_ms']:.1f} | {operations['exact_record']['graphify-backed']['median_ms']:.1f} |",
            f"| Group by source/type | {operations['aggregate']['file-backed']['median_ms']:.1f} | {operations['aggregate']['turso-backed']['median_ms']:.1f} | {operations['aggregate']['graphify-backed']['median_ms']:.1f} |",
            "",
            "Graphify exact lookup and aggregation intentionally use `records.jsonl`; their extra time is the fail-closed validation of the core and derived graph in each fresh process.",
            "",
            "## Retrieval on the identical 30 questions",
            "",
            "| Route | Recall@10 | MRR@10 | nDCG@10 | Evidence validity | Mean (ms) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name in ("legacy_lexical", "new_lexical", "vector", "hybrid", "graphify_structural"):
        route = routes[name]
        lines.append(
            f"| {name} | {route['recall_at_10']:.4f} | {route['mrr_at_10']:.4f} | {route['ndcg_at_10']:.4f} | {route['evidence_validity']:.4f} | {route['mean_ms']:.1f} |"
        )
    lines.extend(
        [
            "",
            "Latency scopes differ: legacy lexical reuses an in-process index, while Graphify, new lexical, vector, and hybrid figures include fresh validated subprocess boundaries. Quality metrics use the same paper-level qrels and first-rank deduplication.",
            "",
            "## Integrity findings",
            "",
            f"- Authoritative core parity with file-backed: **{graphify['core_semantic_parity']}**.",
            f"- Independent graph rebuild: **{'pass' if graphify['deterministic_rebuild'] else 'fail'}** (`{graphify['projection']['logical_sha256']}`).",
            f"- Exact and aggregate result parity: **{'pass' if report['parity']['queries'] else 'fail'}**.",
            f"- Full ledger, record-digest, paper-ID, locator, and concept-body evidence binding: **{'pass' if report['parity']['evidence'] else 'fail'}**.",
            f"- Snapshot unchanged by all consultation calls: **{'pass' if report['parity']['read_only'] else 'fail'}**.",
            f"- Graph: {graphify['projection']['nodes']} nodes, {graphify['projection']['edges']} edges, {graphify['projection']['orphans']} orphans.",
            "",
            "## Decision",
            "",
            "Keep file-backed as the default minimum-footprint release. Choose Turso for repeated structured SQL-style aggregation. Choose embeddings when tuned paraphrase retrieval is required. Choose Graphify when linked-heading orientation and bounded Markdown-neighborhood traversal are useful and the additional graph size, build time, and validation latency are acceptable. Graphify did not become a factual authority: every returned record was hydrated from unchanged OKF concepts.",
            "",
        ]
    )
    return "\n".join(lines)


def compare(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    manifest = args.manifest.resolve()
    qrels_path = args.questions.resolve()
    prior_path = args.prior_report.resolve()
    if sha256_file(manifest) != EXPECTED_MANIFEST_SHA256:
        raise ComparisonError("frozen manifest digest changed")
    if sha256_file(qrels_path) != EXPECTED_QRELS_SHA256:
        raise ComparisonError("retrieval-question digest changed")
    prior_sha256 = sha256_file(prior_path)
    if prior_sha256 != EXPECTED_PRIOR_REPORT_SHA256:
        raise ComparisonError("frozen prior operational report digest changed")
    prior = load_json(prior_path, "prior operational report")
    prior_corpus = prior.get("corpus")
    if not isinstance(prior_corpus, dict) or (
        prior_corpus.get("records") != EXPECTED_RECORDS
        or prior_corpus.get("sources") != EXPECTED_SOURCES
    ):
        raise ComparisonError("prior report does not describe the frozen corpus")
    if prior.get("status") != "pass":
        raise ComparisonError("prior operational report did not pass")
    prior_manifest = prior.get("inputs", {}).get("manifest", {})
    if not isinstance(prior_manifest, dict) or prior_manifest.get("sha256") != EXPECTED_MANIFEST_SHA256:
        raise ComparisonError("prior report is not bound to the frozen manifest")
    questions = load_jsonl(qrels_path, "retrieval questions")
    if len(questions) != 30:
        raise ComparisonError("retrieval question set must contain exactly 30 cases")
    work_root = args.work_root.resolve()
    if work_root.exists():
        raise ComparisonError(f"work root already exists: {work_root}")
    work_root.mkdir(parents=True)
    build_script = repo_root / "skills/build-semantic-okf-graphify/scripts/build_semantic_okf_graphify.py"
    query_script = repo_root / "skills/consult-semantic-okf-graphify/scripts/query_semantic_okf_graphify.py"
    bundles = [work_root / "graphify-a", work_root / "graphify-b"]
    build_times: list[float] = []
    build_reports: list[dict[str, Any]] = []
    for bundle in bundles:
        payload, elapsed = run_json(
            [
                args.python_executable,
                str(build_script),
                str(manifest),
                str(bundle),
                "--output-format",
                "json",
            ],
            cwd=repo_root,
            timeout=args.timeout_seconds,
        )
        build_reports.append(payload)
        build_times.append(elapsed)
    bundle = bundles[0]
    records = load_jsonl(bundle / "semantic/records.jsonl", "Graphify record ledger")
    sources = {str(record.get("source_id")) for record in records}
    if len(records) != EXPECTED_RECORDS or len(sources) != EXPECTED_SOURCES:
        raise ComparisonError("Graphify build does not reproduce the frozen corpus")
    before = tree_fingerprint(bundle)
    sample = records[0]
    exact_argv = [
        args.python_executable,
        str(query_script),
        str(bundle),
        "records",
        "--source-id",
        str(sample["source_id"]),
        "--record-id",
        str(sample["record_id"]),
    ]
    exact, exact_timing = measure_json(
        exact_argv,
        cwd=repo_root,
        timeout=args.timeout_seconds,
        iterations=args.iterations,
    )
    aggregate, aggregate_timing = measure_json(
        [args.python_executable, str(query_script), str(bundle), "aggregate"],
        cwd=repo_root,
        timeout=args.timeout_seconds,
        iterations=args.iterations,
    )
    route = evaluate_graphify_queries(
        query_script,
        bundle,
        questions,
        python=args.python_executable,
        repo_root=repo_root,
        timeout=args.timeout_seconds,
    )
    verification, validation_ms = run_json(
        [args.python_executable, str(query_script), str(bundle), "verify"],
        cwd=repo_root,
        timeout=args.timeout_seconds,
    )
    if verification.get("status") != "pass":
        raise ComparisonError("Graphify verification did not pass")
    after = tree_fingerprint(bundle)
    expected_groups = [
        {"source_id": source, "concept_type": kind, "records": count}
        for (source, kind), count in sorted(
            Counter(
                (str(record.get("source_id")), str(record.get("concept_type")))
                for record in records
            ).items()
        )
    ]
    exact_records = exact.get("records")
    query_parity = bool(
        exact.get("returned") == 1
        and isinstance(exact_records, list)
        and len(exact_records) == 1
        and isinstance(exact_records[0], dict)
        and exact_records[0].get("record_sha256") == sample["record_sha256"]
        and aggregate.get("groups") == expected_groups
    )
    graph_a = load_json(bundles[0] / "retrieval/graphify/index.json", "Graphify index A")
    graph_b = load_json(bundles[1] / "retrieval/graphify/index.json", "Graphify index B")
    deterministic = (
        graph_a["graph"]["logical_sha256"] == graph_b["graph"]["logical_sha256"]
        and (bundles[0] / "retrieval/graphify/graph.json").read_bytes()
        == (bundles[1] / "retrieval/graphify/graph.json").read_bytes()
        and (bundles[0] / "retrieval/graphify/index.json").read_bytes()
        == (bundles[1] / "retrieval/graphify/index.json").read_bytes()
    )
    core_fingerprint = tree_fingerprint(bundle, exclude_graphify=True)
    core_parity = (
        core_fingerprint["logical_tree_sha256"]
        == prior["versions"]["file-backed"]["bundle"]["logical_tree_sha256"]
    )
    projection_summary = build_reports[0].get("graphify", {}).get("summary", {})
    if not isinstance(projection_summary, dict):
        raise ComparisonError("Graphify build report omits projection summary")
    if projection_summary.get("orphans") != 0:
        raise ComparisonError("Graphify validation reports orphan nodes")
    evidence_parity = (
        route["evidence_total"] > 0
        and route["evidence_valid"] == route["evidence_total"]
        and route["evidence_validity"] == 1.0
        and all(case.get("evidence_valid") is True for case in route["cases"] if "error" not in case)
    )
    graphify_version = {
        "build_ms": timing_summary(build_times),
        "bundle": tree_fingerprint(bundle),
        "core_bundle": core_fingerprint,
        "core_semantic_parity": "pass" if core_parity else "fail",
        "deterministic_rebuild": deterministic,
        "projection": {
            "edges": graph_a["graph"]["edges"],
            "logical_sha256": graph_a["graph"]["logical_sha256"],
            "nodes": graph_a["graph"]["nodes"],
            "orphans": projection_summary.get("orphans"),
            "package": "graphifyy",
            "path": "retrieval/graphify/graph.json",
            "physical_sha256": graph_a["graph"]["sha256"],
            "validation_ms": validation_ms,
            "version": "0.9.17",
        },
        "routes": {"graphify_structural": route},
        "status": (
            "pass"
            if deterministic and core_parity and route["errors"] == 0 and evidence_parity
            else "fail"
        ),
    }
    versions = dict(prior["versions"])
    versions["graphify-backed"] = graphify_version
    retrieval_routes = dict(prior["versions"]["embedding-backed"]["routes"])
    retrieval_routes["graphify_structural"] = route
    parity = {
        "authoritative_core": core_parity,
        "deterministic": deterministic,
        "evidence": evidence_parity,
        "queries": query_parity,
        "read_only": before == after,
    }
    status = "pass" if all(parity.values()) and route["errors"] == 0 else "fail"
    return {
        "corpus": {
            "questions": len(questions),
            "records": len(records),
            "sources": len(sources),
        },
        "inputs": {
            "graphify_skills": {
                "build": source_tree_fingerprint(repo_root / "skills/build-semantic-okf-graphify"),
                "consult": source_tree_fingerprint(repo_root / "skills/consult-semantic-okf-graphify"),
            },
            "manifest": {"path": str(manifest.relative_to(repo_root)).replace("\\", "/"), "sha256": sha256_file(manifest)},
            "prior_report": {"path": str(prior_path.relative_to(repo_root)).replace("\\", "/"), "sha256": prior_sha256},
            "questions": {"path": str(qrels_path.relative_to(repo_root)).replace("\\", "/"), "sha256": sha256_file(qrels_path)},
        },
        "methodology": {
            "builds": "two fresh independent Graphify-backed builds",
            "operations": f"{args.iterations} fresh validated CLI subprocesses per authoritative operation",
            "retrieval": "one fresh validated Graphify CLI subprocess per existing retrieval question",
            "evidence": "every hit must match ledger identity and recomputed record digest, derive the same paper ID from the ledger, resolve through a safe exact concept-file locator, return byte-identical concept content, and contain the exact authoritative ledger body",
            "timing_warning": "latency scopes differ across historical routes; compare quality directly and latency only with the stated process boundary",
        },
        "operational_queries": {
            "aggregate": {
                **prior["operational_queries"]["aggregate"],
                "graphify-backed": aggregate_timing,
            },
            "exact_record": {
                **prior["operational_queries"]["exact_record"],
                "graphify-backed": exact_timing,
            },
        },
        "parity": parity,
        "retrieval_routes": retrieval_routes,
        "schema_version": "1.0",
        "status": status,
        "versions": versions,
    }


def build_parser() -> argparse.ArgumentParser:
    script = Path(__file__).resolve()
    repo_root = script.parents[3]
    evaluation = script.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument(
        "--manifest", type=Path, default=repo_root / "evaluations/graphrag-cross-paper/manifest.json"
    )
    parser.add_argument(
        "--questions", type=Path, default=repo_root / "evaluations/semantic-okf-embeddings/retrieval-questions.jsonl"
    )
    parser.add_argument("--prior-report", type=Path, default=evaluation / "operational-report.json")
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument("--output-json", type=Path, default=evaluation / "graphify-operational-report.json")
    parser.add_argument("--output-markdown", type=Path, default=evaluation / "graphify-operational-report.md")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.iterations < 1:
        print("comparison error: --iterations must be at least 1", file=sys.stderr)
        return 2
    try:
        report = compare(args)
    except (ComparisonError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"comparison error: {exc}", file=sys.stderr)
        return 2
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    args.output_markdown.write_text(
        render_markdown(report), encoding="utf-8", newline="\n"
    )
    print(json.dumps({"status": report["status"], **report["corpus"]}, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
