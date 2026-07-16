#!/usr/bin/env python3
"""Publish a checked, secret-free summary of accepted q040 Skill Arena runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
REPORTS = EVALUATION / "reports"
DEFAULT_BUNDLES_ROOT = (
    EVALUATION / "results" / "runs" / "20260716-astro-generic-01" / "bundles"
)
DEFAULT_SOURCE_COMBINATION = EVALUATION / "corpus" / "source-combination.json"
SCHEMA = "semantic-okf-astro-skill-arena-q040-paired-runs/1.0"
SUPPORTED_FAMILIES = (
    "legacy",
    "embeddings",
    "classical",
    "adaptive",
    "entity-graph",
    "ensemble",
)
FROZEN_ACCEPTED_RUN_IDS = {
    "legacy": "2026-07-16T11-50-44-330Z-compare",
    "embeddings": "2026-07-16T11-50-43-971Z-compare",
    "classical": "2026-07-16T11-55-25-736Z-compare",
    "adaptive": "2026-07-16T11-55-26-061Z-compare",
    "entity-graph": "2026-07-16T11-59-19-741Z-compare",
    "ensemble": "2026-07-16T11-38-31-783Z-compare",
}
EXPECTED_PROMPT = "q040"
EXPECTED_VARIANT = "pi-luna-only"
CONTROL = "knowledge-only-control"
EXPECTED_ASSERTIONS = ("response-format", "response-contract", "grounded-answer")
EVIDENCE_KEYS = (
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
)


class SummaryError(RuntimeError):
    """Describe malformed or unexpected Skill Arena output."""


def benchmark_id(family: str) -> str:
    """Return the only compatible q040 paired benchmark ID for one family."""

    if family not in SUPPORTED_FAMILIES:
        raise SummaryError(f"unsupported consultation family: {family}")
    return f"semantic-okf-astro-q040-{family}-paired"


def treatment_profile(family: str) -> str:
    """Return the family-specific treatment profile ID."""

    benchmark_id(family)
    return f"{family}-consult-treatment"


def expected_profiles(family: str) -> tuple[str, str]:
    """Return the control/treatment profile IDs in their required order."""

    return CONTROL, treatment_profile(family)


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON object members."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SummaryError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    """Load one strict JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SummaryError(f"cannot load JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SummaryError(f"expected JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load strict, nonblank JSONL objects."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SummaryError(f"cannot load JSONL {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            raise SummaryError(f"blank JSONL row at {path}:{number}")
        try:
            value = json.loads(line, object_pairs_hook=strict_object)
        except json.JSONDecodeError as exc:
            raise SummaryError(f"invalid JSONL at {path}:{number}: {exc}") from exc
        if not isinstance(value, dict):
            raise SummaryError(f"expected JSON object at {path}:{number}")
        rows.append(value)
    if not rows:
        raise SummaryError(f"empty JSONL file: {path}")
    return rows


class AuthoritativeLedger:
    """Validate model-emitted evidence without normalizing any response field."""

    def __init__(self, records_path: Path, source_combination_path: Path) -> None:
        self.records_path = records_path.resolve()
        self.source_combination_path = source_combination_path.resolve()
        combination = load_json(self.source_combination_path)
        records = combination.get("records")
        if (
            combination.get("schema_version") != "semantic-okf-astro-source-identity/1.1"
            or not isinstance(records, list)
            or not records
            or any(not isinstance(row, dict) for row in records)
        ):
            raise SummaryError("source-combination violates its frozen schema")
        self.document_by_identity: dict[tuple[str, str], str] = {}
        for row in records:
            source_id, record_id, document_id = (
                row.get("source_id"),
                row.get("record_id"),
                row.get("document_id"),
            )
            if not all(isinstance(value, str) and value for value in (source_id, record_id, document_id)):
                raise SummaryError("source-combination contains an invalid identity")
            key = (source_id, record_id)
            if key in self.document_by_identity:
                raise SummaryError(f"duplicate source-record identity: {key}")
            self.document_by_identity[key] = document_id
        self.by_identity: dict[tuple[str, str], dict[str, Any]] = {}
        for number, record in enumerate(load_jsonl(self.records_path), 1):
            required = (
                "source_id",
                "record_id",
                "record_sha256",
                "concept_path",
                "source_path",
                "body",
            )
            if any(not isinstance(record.get(key), str) or not record[key] for key in required):
                raise SummaryError(f"authoritative ledger row {number} is incomplete")
            key = (record["source_id"], record["record_id"])
            if key in self.by_identity or key not in self.document_by_identity:
                raise SummaryError(f"authoritative ledger identity is duplicate or unmapped: {key}")
            self.by_identity[key] = record
        if set(self.by_identity) != set(self.document_by_identity):
            raise SummaryError("authoritative ledger and source-combination identities differ")

    def validate(self, evidence: Any, index: int) -> dict[str, Any]:
        """Reconstruct one evidence row exactly and return every independent issue."""

        issues: list[str] = []
        if not isinstance(evidence, dict):
            return {
                "index": index,
                "valid": False,
                "document_id": None,
                "issues": ["evidence row is not an object"],
            }
        if tuple(evidence) != EVIDENCE_KEYS:
            issues.append("evidence keys/order differ from the closed response contract")
        source_id, record_id = evidence.get("source_id"), evidence.get("record_id")
        if not isinstance(source_id, str) or not isinstance(record_id, str):
            issues.append("source_id or record_id is not a string")
            key = None
        else:
            key = (source_id, record_id)
        record = self.by_identity.get(key) if key is not None else None
        document_id = self.document_by_identity.get(key) if key is not None else None
        if record is None:
            issues.append("source_id + record_id is absent from the frozen identity crosswalk/ledger")
        else:
            for field in ("record_sha256", "concept_path", "source_path"):
                if evidence.get(field) != record[field]:
                    issues.append(f"{field} differs from the authoritative ledger")
            locator = evidence.get("locator")
            retained: str | None = None
            if not isinstance(locator, dict):
                issues.append("locator is not an object")
            else:
                kind = locator.get("kind")
                body = record["body"]
                if kind == "record":
                    retained = body
                elif kind == "character-range":
                    start, end = locator.get("start"), locator.get("end")
                    if (
                        isinstance(start, bool)
                        or isinstance(end, bool)
                        or not isinstance(start, int)
                        or not isinstance(end, int)
                        or not 0 <= start < end <= len(body)
                    ):
                        issues.append("character-range locator is out of bounds")
                    else:
                        retained = body[start:end]
                    target = locator.get("target")
                    if target is not None and target not in {
                        "record-body",
                        "record.body",
                        "source-body",
                    }:
                        issues.append("locator target is not an authoritative record body")
                else:
                    issues.append("locator kind is unsupported")
            text_sha = evidence.get("text_sha256")
            if not isinstance(text_sha, str) or len(text_sha) != 64:
                issues.append("text_sha256 is not a 64-character string")
            elif retained is not None and sha256_bytes(retained.encode("utf-8")) != text_sha:
                issues.append("text_sha256 does not match the reconstructed authoritative passage")
        return {
            "index": index,
            "valid": not issues,
            "document_id": document_id,
            "issues": issues,
        }


def validate_response_evidence(
    response: Mapping[str, Any],
    ledger: AuthoritativeLedger,
) -> dict[str, Any]:
    """Keep response-contract scoring separate from authoritative evidence validity."""

    evidence = response.get("evidence")
    if not isinstance(evidence, list):
        return {
            "status": "fail",
            "returned": 0,
            "valid": 0,
            "invalid": 1,
            "all_valid": False,
            "rows": [
                {
                    "index": 0,
                    "valid": False,
                    "document_id": None,
                    "issues": ["response evidence is not an array"],
                }
            ],
        }
    rows = [ledger.validate(row, index) for index, row in enumerate(evidence)]
    valid = sum(row["valid"] for row in rows)
    if not rows:
        status, all_valid = "not-applicable", None
    else:
        all_valid = valid == len(rows)
        status = "pass" if all_valid else "fail"
    return {
        "status": status,
        "returned": len(rows),
        "valid": valid,
        "invalid": len(rows) - valid,
        "all_valid": all_valid,
        "rows": rows,
    }


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash one source artifact without retaining its potentially sensitive content."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    """Serialize a value for deterministic identity hashes."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pretty_json(value: Any) -> str:
    """Serialize the report while preserving the response's original key order."""

    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def atomic_write(path: Path, content: str) -> None:
    """Atomically replace one compact checked report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def repository_path(path: Path) -> str:
    """Return a portable repository-relative path and reject external input."""

    try:
        return path.resolve().relative_to(REPO).as_posix()
    except ValueError as exc:
        raise SummaryError(f"accepted artifacts must remain inside the repository: {path}") from exc


def artifact(path: Path) -> dict[str, Any]:
    """Bind one raw source by path, byte length, and hash only."""

    if not path.is_file():
        raise SummaryError(f"missing Skill Arena artifact: {path}")
    return {
        "path": repository_path(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def parse_response(output: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Parse exactly one leading JSON response and disclose any trailing-data defect."""

    if not isinstance(output, str) or not output:
        raise SummaryError("profile response must be a nonempty string")
    decoder = json.JSONDecoder(object_pairs_hook=strict_object)
    try:
        parsed, end = decoder.raw_decode(output)
    except json.JSONDecodeError as exc:
        raise SummaryError(f"profile response has no leading JSON object: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SummaryError("profile response must begin with a JSON object")
    trailing = output[end:]
    strict_json = not trailing.strip()
    metadata = {
        "output_bytes": len(output.encode("utf-8")),
        "output_sha256": sha256_bytes(output.encode("utf-8")),
        "strict_json": strict_json,
        "trailing_character_count": len(trailing),
        "trailing_text_sha256": sha256_bytes(trailing.encode("utf-8")) if trailing else None,
        "top_level_key_order": list(parsed),
    }
    return parsed, metadata


def validate_parsed_response(
    value: Mapping[str, Any], expected_prompt: str = EXPECTED_PROMPT
) -> None:
    """Require the exact response contract without altering its content."""

    if list(value) != ["question_id", "answer", "evidence"]:
        raise SummaryError("response top-level key order differs from the closed contract")
    if value.get("question_id") != expected_prompt:
        raise SummaryError(f"response question_id differs from {expected_prompt}")
    answer, evidence = value.get("answer"), value.get("evidence")
    if answer is None:
        if evidence != []:
            raise SummaryError("a null response answer must have empty evidence")
        return
    if not isinstance(answer, dict) or list(answer) != ["summary", "claims"]:
        raise SummaryError("response answer violates its closed schema")
    if not isinstance(answer.get("summary"), str) or not answer["summary"].strip():
        raise SummaryError("response answer summary is empty")
    claims = answer.get("claims")
    if not isinstance(claims, list) or not claims:
        raise SummaryError("response claims are empty")
    if not isinstance(evidence, list) or not evidence:
        raise SummaryError("response evidence is empty")


def assertion_row(component: Mapping[str, Any]) -> dict[str, Any]:
    """Retain exact assertion outcomes while hashing verbose executable definitions."""

    assertion = component.get("assertion")
    if not isinstance(assertion, dict):
        raise SummaryError("grading component has no assertion object")
    metric = assertion.get("metric")
    assertion_type = assertion.get("type")
    passed, score, reason = component.get("pass"), component.get("score"), component.get("reason")
    if (
        not isinstance(metric, str)
        or not isinstance(assertion_type, str)
        or not isinstance(passed, bool)
        or isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not isinstance(reason, str)
    ):
        raise SummaryError("grading component contains invalid outcome fields")
    return {
        "metric": metric,
        "type": assertion_type,
        "pass": passed,
        "score": score,
        "reason_summary": reason.splitlines()[0],
        "reason_sha256": sha256_bytes(reason.encode("utf-8")),
        "definition_sha256": sha256_bytes(canonical_json(assertion).encode("utf-8")),
    }


def exact_profiles(
    family: str,
    promptfoo: Mapping[str, Any],
    summary: Mapping[str, Any],
    *,
    expected_benchmark: str | None = None,
    expected_prompt: str = EXPECTED_PROMPT,
    profiles_expected: tuple[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Cross-check both artifacts and extract the two accepted comparison cells."""

    result_root = promptfoo.get("results")
    if not isinstance(result_root, dict) or not isinstance(result_root.get("results"), list):
        raise SummaryError("promptfoo-results has no result cells")
    expected_benchmark = expected_benchmark or benchmark_id(family)
    profiles_expected = profiles_expected or expected_profiles(family)
    raw_rows = result_root["results"]
    if len(raw_rows) != 2 or any(not isinstance(row, dict) for row in raw_rows):
        raise SummaryError("accepted comparison must contain exactly two result cells")
    by_profile: dict[str, dict[str, Any]] = {}
    for row in raw_rows:
        provider = row.get("provider")
        profile = provider.get("id") if isinstance(provider, dict) else None
        if not isinstance(profile, str) or profile in by_profile:
            raise SummaryError("result cells have invalid or duplicate profile IDs")
        by_profile[profile] = row
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            raise SummaryError(f"{profile} result has no metadata")
        if metadata.get("benchmarkId") != expected_benchmark:
            raise SummaryError(f"{profile} benchmark ID differs")
        if metadata.get("promptId") != expected_prompt:
            raise SummaryError(f"{profile} prompt ID differs")
        if metadata.get("variantId") != EXPECTED_VARIANT:
            raise SummaryError(f"{profile} variant ID differs")
    if tuple(by_profile) != profiles_expected:
        raise SummaryError(f"profile IDs/order differ: {tuple(by_profile)}")

    matrix = summary.get("matrix")
    if not isinstance(matrix, dict) or matrix.get("benchmarkId") != expected_benchmark:
        raise SummaryError("summary matrix benchmark ID differs")
    columns, matrix_rows = matrix.get("columns"), matrix.get("rows")
    if (
        not isinstance(columns, list)
        or [row.get("id") for row in columns if isinstance(row, dict)] != list(profiles_expected)
        or not isinstance(matrix_rows, list)
        or len(matrix_rows) != 1
        or not isinstance(matrix_rows[0], dict)
    ):
        raise SummaryError("summary matrix does not contain the exact paired profiles")
    matrix_row = matrix_rows[0]
    if matrix_row.get("promptId") != expected_prompt or matrix_row.get("variantId") != EXPECTED_VARIANT:
        raise SummaryError("summary matrix row identity differs")
    cells = matrix_row.get("cells")
    if not isinstance(cells, dict) or tuple(cells) != profiles_expected:
        raise SummaryError("summary matrix cells differ from expected profiles")

    profiles: list[dict[str, Any]] = []
    for profile in profiles_expected:
        raw = by_profile[profile]
        cell = cells[profile]
        if not isinstance(cell, dict):
            raise SummaryError(f"{profile} summary cell is malformed")
        grading = raw.get("gradingResult")
        response = raw.get("response")
        if not isinstance(grading, dict) or not isinstance(response, dict):
            raise SummaryError(f"{profile} result lacks grading or response")
        components = grading.get("componentResults")
        if not isinstance(components, list) or any(not isinstance(row, dict) for row in components):
            raise SummaryError(f"{profile} assertion results are malformed")
        assertions = [assertion_row(component) for component in components]
        if tuple(row["metric"] for row in assertions) != EXPECTED_ASSERTIONS:
            raise SummaryError(f"{profile} assertion metrics/order differ")
        output = response.get("output")
        if not isinstance(output, str):
            raise SummaryError(f"{profile} response output is not text")
        parsed, response_metadata = parse_response(output)
        validate_parsed_response(parsed, expected_prompt)
        success, score, latency = raw.get("success"), raw.get("score"), raw.get("latencyMs")
        if (
            not isinstance(success, bool)
            or isinstance(score, bool)
            or not isinstance(score, (int, float))
            or isinstance(latency, bool)
            or not isinstance(latency, int)
            or latency < 0
        ):
            raise SummaryError(f"{profile} outcome fields are invalid")
        if grading.get("pass") is not success or grading.get("score") != score:
            raise SummaryError(f"{profile} raw grading fields disagree")
        if cell.get("passRate") != (1 if success else 0):
            raise SummaryError(f"{profile} summary pass rate disagrees")
        if cell.get("latency", {}).get("averageLatencyMs") != latency:
            raise SummaryError(f"{profile} summary latency disagrees")
        expected_named = {row["metric"]: row["score"] for row in assertions}
        if raw.get("namedScores") != expected_named or grading.get("namedScores") != expected_named:
            raise SummaryError(f"{profile} named assertion scores disagree")
        profiles.append(
            {
                "profile_id": profile,
                "causal_role": "passive-control" if profile == CONTROL else "treatment",
                "skill_enabled": profile != CONTROL,
                "pass": success,
                "pass_rate": cell["passRate"],
                "score": score,
                "latency_ms": latency,
                "assertions": assertions,
                "response_metadata": response_metadata,
                "parsed_response": parsed,
            }
        )
    return profiles


def developmental_traces(compare_dir: Path) -> list[dict[str, Any]]:
    """List earlier append-only directories only as non-accepted diagnostics."""

    traces: list[dict[str, Any]] = []
    for path in sorted(compare_dir.parent.glob("*-compare")):
        if path.name >= compare_dir.name:
            continue
        row: dict[str, Any] = {
            "run_id": path.name,
            "accepted": False,
            "classification": "developmental trace only; excluded from accepted metrics",
        }
        summary_path = path / "summary.json"
        if summary_path.is_file():
            payload = load_json(summary_path)
            stats = payload.get("stats")
            if isinstance(stats, dict):
                row.update(
                    {
                        "summary_available": True,
                        "eval_id": payload.get("evalId"),
                        "successes": stats.get("successes"),
                        "failures": stats.get("failures"),
                        "errors": stats.get("errors"),
                    }
                )
            else:
                row["summary_available"] = False
        else:
            row["summary_available"] = False
        traces.append(row)
    return traces


def summarize_run(
    family: str,
    compare_dir: Path,
    *,
    bundles_root: Path = DEFAULT_BUNDLES_ROOT,
    source_combination: Path = DEFAULT_SOURCE_COMBINATION,
) -> dict[str, Any]:
    """Validate one explicitly selected family compare run."""

    expected_benchmark = benchmark_id(family)
    profiles_expected = expected_profiles(family)
    compare_dir = compare_dir.resolve()
    if not compare_dir.is_dir():
        raise SummaryError(f"compare directory does not exist: {compare_dir}")
    frozen_run_id = FROZEN_ACCEPTED_RUN_IDS.get(family)
    if frozen_run_id is not None and compare_dir.name != frozen_run_id:
        raise SummaryError(
            f"the frozen accepted {family} run is {frozen_run_id}; found {compare_dir.name}"
        )
    promptfoo_path = compare_dir / "promptfoo-results.json"
    config_path = compare_dir / "promptfooconfig.yaml"
    summary_path = compare_dir / "summary.json"
    promptfoo, summary = load_json(promptfoo_path), load_json(summary_path)
    eval_id = promptfoo.get("evalId")
    if not isinstance(eval_id, str) or not eval_id or summary.get("evalId") != eval_id:
        raise SummaryError("promptfoo and normalized summaries disagree on eval ID")
    if summary.get("benchmarkId") != expected_benchmark:
        raise SummaryError(f"accepted {family} summary benchmark ID differs")
    providers = summary.get("providers")
    if (
        not isinstance(providers, list)
        or [row.get("profileId") for row in providers if isinstance(row, dict)] != list(profiles_expected)
    ):
        raise SummaryError(f"accepted {family} summary provider IDs/order differ")
    if summary.get("unsupportedCells") != []:
        raise SummaryError("accepted comparison contains unsupported cells")
    records_path = bundles_root.resolve() / f"{family}-a" / "semantic" / "records.jsonl"
    ledger = AuthoritativeLedger(records_path, source_combination)
    profiles = exact_profiles(family, promptfoo, summary)
    for profile in profiles:
        profile["evidence_validation"] = validate_response_evidence(
            profile["parsed_response"], ledger
        )
    control, treatment = profiles
    raw_control_output = promptfoo["results"]["results"][0]["response"]["output"]
    _, control_end = json.JSONDecoder(object_pairs_hook=strict_object).raw_decode(raw_control_output)
    trailing_control = raw_control_output[control_end:]
    if family == "ensemble" and (
        trailing_control != "}"
        or control["pass"]
        or control["score"] != 0
        or control["response_metadata"]["strict_json"]
        or any(row["pass"] for row in control["assertions"])
    ):
        raise SummaryError("accepted ensemble control no longer matches its audited 0/3 trailing-brace result")
    if family == "ensemble" and (
        not treatment["pass"]
        or treatment["score"] != 1
        or not treatment["response_metadata"]["strict_json"]
        or not all(row["pass"] for row in treatment["assertions"])
    ):
        raise SummaryError("accepted ensemble treatment must pass all assertions with score 1 and strict JSON")
    stats = promptfoo.get("results", {}).get("stats")
    expected_successes = sum(row["pass"] for row in profiles)
    expected_failures = len(profiles) - expected_successes
    if not isinstance(stats, dict) or (
        stats.get("successes"), stats.get("failures"), stats.get("errors")
    ) != (expected_successes, expected_failures, 0):
        raise SummaryError("accepted aggregate Promptfoo stats disagree with profile outcomes")
    control_rate, treatment_rate = float(control["pass"]), float(treatment["pass"])
    return {
        "family": family,
        "accepted_run": {
            "accepted": True,
            "run_id": compare_dir.name,
            "compare_directory": repository_path(compare_dir),
            "eval_id": eval_id,
            "benchmark_id": expected_benchmark,
            "prompt_id": EXPECTED_PROMPT,
            "variant_id": EXPECTED_VARIANT,
        },
        "source_artifacts": {
            "promptfoo_results": artifact(promptfoo_path),
            "promptfoo_config": artifact(config_path),
            "skill_arena_summary": artifact(summary_path),
            "authoritative_records": artifact(records_path),
            "source_combination": artifact(source_combination.resolve()),
        },
        "outcome": {
            "control_pass_rate": control_rate,
            "treatment_pass_rate": treatment_rate,
            "absolute_percentage_point_delta": 100.0 * (treatment_rate - control_rate),
            "control_evidence_status": control["evidence_validation"]["status"],
            "treatment_evidence_status": treatment["evidence_validation"]["status"],
            "prompt_count": 1,
            "causal_scope": "one paired q040 boundary diagnostic; not an aggregate 40-question result",
        },
        "harness_interpretation": {
            "derived_overall_status": "PASSED" if expected_failures == 0 else "FAILED",
            "all_cells_passed": expected_failures == 0,
            "successes": expected_successes,
            "failures": expected_failures,
            "errors": 0,
            "accepted_pairwise_result": True,
            "explanation": (
                "The overall status applies an all-cells rule. Pairwise interpretation uses the "
                "separate control and treatment outcomes and does not override independent "
                "authoritative evidence validation."
            ),
        },
        "profiles": profiles,
        "non_accepted_traces": developmental_traces(compare_dir),
    }


def summarize(
    compare_dirs: Mapping[str, Path],
    *,
    bundles_root: Path = DEFAULT_BUNDLES_ROOT,
    source_combination: Path = DEFAULT_SOURCE_COMBINATION,
) -> dict[str, Any]:
    """Aggregate compatible family runs without merging their causal cells."""

    if not compare_dirs:
        raise SummaryError("at least one family compare directory is required")
    unknown = sorted(set(compare_dirs) - set(SUPPORTED_FAMILIES))
    if unknown:
        raise SummaryError(f"unsupported consultation families: {unknown}")
    ordered = [
        summarize_run(
            family,
            compare_dirs[family],
            bundles_root=bundles_root,
            source_combination=source_combination,
        )
        for family in SUPPORTED_FAMILIES
        if family in compare_dirs
    ]
    return {
        "schema_version": SCHEMA,
        "status": "pass",
        "family_count": len(ordered),
        "families": ordered,
        "aggregate_interpretation": {
            "accepted_runs_only": True,
            "paired_result_count": len(ordered),
            "all_treatments_passed": all(row["outcome"]["treatment_pass_rate"] == 1 for row in ordered),
            "all_controls_failed": all(row["outcome"]["control_pass_rate"] == 0 for row in ordered),
            "all_treatment_evidence_valid": all(
                row["profiles"][1]["evidence_validation"]["all_valid"] is True
                for row in ordered
            ),
            "scope": "each family remains a separate one-prompt paired q040 diagnostic",
        },
        "privacy": {
            "raw_environment_copied": False,
            "raw_workspace_paths_copied": False,
            "source_files_represented_by_hashes_only": True,
            "parsed_model_responses_retained_exactly": True,
        },
    }


def pct(value: Any) -> str:
    """Render a ratio as a percentage."""

    return f"{100.0 * float(value):.0f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render a compact human audit with exact parsed response objects."""

    lines = [
        "# Accepted Skill Arena q040 Paired Results",
        "",
        f"This report contains {report['family_count']} explicitly selected final compare run(s). Every family remains an independent paired control/treatment diagnostic.",
        "",
        "| Family | Control | Treatment | Delta | Treatment evidence | Harness | Accepted run |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for family in report["families"]:
        outcome, accepted, harness = (
            family["outcome"],
            family["accepted_run"],
            family["harness_interpretation"],
        )
        lines.append(
            f"| {family['family']} | {pct(outcome['control_pass_rate'])} | "
            f"{pct(outcome['treatment_pass_rate'])} | +{outcome['absolute_percentage_point_delta']:.0f} pp | "
            f"{outcome['treatment_evidence_status']} | {harness['derived_overall_status']} | `{accepted['run_id']}` |"
        )
    lines.extend(
        [
            "",
            "An overall harness status of `FAILED` is compatible with an accepted pair because the all-cells rule includes the intentionally failing control. Each result covers one frozen q040 prompt, not the aggregate 40-question benchmark.",
            "Promptfoo contract pass and authoritative evidence validity are separate gates. Evidence validity below is reconstructed independently from the frozen source-record crosswalk and authoritative ledger; response fields are never normalized.",
            "",
        ]
    )
    for family in report["families"]:
        accepted = family["accepted_run"]
        lines.extend(
            [
                f"## {family['family']}",
                "",
                f"Accepted run: `{accepted['run_id']}` (`{accepted['eval_id']}`), benchmark `{accepted['benchmark_id']}`. The metrics and responses in this section bind only that directory.",
                "",
                "### Source bindings",
                "",
                "| Artifact | Bytes | SHA-256 |",
                "|---|---:|---|",
            ]
        )
        for name, source in family["source_artifacts"].items():
            lines.append(f"| {name} | {source['bytes']} | `{source['sha256']}` |")
        lines.extend(
            [
                "",
                "### Profile outcomes",
                "",
                "| Profile | Role | Pass | Score | Assertions | Time | Strict JSON | Evidence valid |",
                "|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for profile in family["profiles"]:
            passed = sum(assertion["pass"] for assertion in profile["assertions"])
            lines.append(
                f"| {profile['profile_id']} | {profile['causal_role']} | "
                f"{'yes' if profile['pass'] else 'no'} | {profile['score']} | "
                f"{passed}/{len(profile['assertions'])} | {profile['latency_ms']} ms | "
                f"{'yes' if profile['response_metadata']['strict_json'] else 'no'} | "
                f"{profile['evidence_validation']['valid']}/{profile['evidence_validation']['returned']} "
                f"({profile['evidence_validation']['status']}) |"
            )
        if family["family"] == "ensemble":
            lines.extend(
                [
                    "",
                    "The ensemble control's leading JSON object is recoverable, but its raw output has one extra closing brace. Therefore it fails strict JSON parsing and all three assertions. The treatment is strict JSON and passes `response-format`, `response-contract`, and `grounded-answer`.",
                ]
            )
        invalid_rows = [
            (profile["profile_id"], evidence)
            for profile in family["profiles"]
            for evidence in profile["evidence_validation"]["rows"]
            if not evidence["valid"]
        ]
        if invalid_rows:
            lines.extend(["", "Authoritative evidence failures:", ""])
            for profile_id, evidence in invalid_rows:
                lines.append(
                    f"- `{profile_id}` evidence {evidence['index']}: "
                    + "; ".join(evidence["issues"])
                )
        lines.extend(
            [
                "",
                "### Exact parsed responses",
                "",
                "The objects below are parsed directly from each raw response without changing any answer, claim, evidence identity, locator, or hash. Raw environment metadata and temporary workspace paths are excluded.",
                "",
            ]
        )
        for profile in family["profiles"]:
            lines.extend(
                [
                    f"#### {profile['profile_id']}",
                    "",
                    "```json",
                    json.dumps(profile["parsed_response"], ensure_ascii=False, indent=2, allow_nan=False),
                    "```",
                    "",
                ]
            )
        lines.extend(
            [
                "### Non-accepted developmental traces",
                "",
                "Earlier append-only directories below are audit traces only. They are excluded from accepted metrics and responses.",
                "",
                "| Run | Summary | Successes | Failures | Errors |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for trace in family["non_accepted_traces"]:
            lines.append(
                f"| {trace['run_id']} | {'yes' if trace['summary_available'] else 'no'} | "
                f"{trace.get('successes', 'N/A')} | {trace.get('failures', 'N/A')} | {trace.get('errors', 'N/A')} |"
            )
        lines.append("")
    lines.extend(["", "No MCP runtime participates in this comparison or summary.", ""])
    return "\n".join(lines)


def infer_family(compare_dir: Path) -> str:
    """Infer a family only from the exact benchmark directory name."""

    parent = compare_dir.resolve().parent.name
    prefix, suffix = "semantic-okf-astro-q040-", "-paired"
    if not parent.startswith(prefix) or not parent.endswith(suffix):
        raise SummaryError(
            "a plain --compare-dir must live under semantic-okf-astro-q040-<family>-paired; "
            "use family=path otherwise"
        )
    family = parent[len(prefix) : -len(suffix)]
    benchmark_id(family)
    return family


def parse_compare_dirs(values: Sequence[str]) -> dict[str, Path]:
    """Parse repeatable plain paths or explicit family=path bindings."""

    result: dict[str, Path] = {}
    for value in values:
        if "=" in value:
            family, raw_path = value.split("=", 1)
            family, path = family.strip(), Path(raw_path.strip()).resolve()
            benchmark_id(family)
        else:
            path = Path(value).resolve()
            family = infer_family(path)
        if family in result:
            raise SummaryError(f"duplicate compare directory for family: {family}")
        result[family] = path
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the accepted compare directory and checked-report paths."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compare-dir",
        action="append",
        required=True,
        metavar="[FAMILY=]PATH",
        help="repeat for compatible family runs; a plain path infers its family from its parent benchmark directory",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--bundles-root",
        type=Path,
        default=DEFAULT_BUNDLES_ROOT,
        help="published family bundles containing the frozen authoritative ledgers",
    )
    parser.add_argument(
        "--source-combination",
        type=Path,
        default=DEFAULT_SOURCE_COMBINATION,
        help="frozen source-record-to-document crosswalk",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=REPORTS / "skill-arena-q040-comparison.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPORTS / "skill-arena-q040-comparison.md",
    )
    args = parser.parse_args(argv)
    try:
        args.compare_dirs = parse_compare_dirs(args.compare_dir)
    except SummaryError as exc:
        parser.error(str(exc))
    args.json_output = args.json_output.resolve()
    args.markdown_output = args.markdown_output.resolve()
    args.bundles_root = args.bundles_root.resolve()
    args.source_combination = args.source_combination.resolve()
    return args


def check_content(path: Path, expected: str) -> None:
    """Require one checked report to be byte-identical to a fresh derivation."""

    if not path.is_file():
        raise SummaryError(f"checked report is missing: {path}")
    try:
        observed = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SummaryError(f"cannot read checked report {path}: {exc}") from exc
    if observed != expected:
        raise SummaryError(f"checked report differs from accepted raw artifacts: {path}")


def main(argv: Sequence[str] | None = None) -> int:
    """Write or check the two deterministic accepted-result reports."""

    args = parse_args(argv)
    try:
        report = summarize(
            args.compare_dirs,
            bundles_root=args.bundles_root,
            source_combination=args.source_combination,
        )
        json_content, markdown_content = pretty_json(report), render_markdown(report)
        if args.check:
            check_content(args.json_output, json_content)
            check_content(args.markdown_output, markdown_content)
        else:
            atomic_write(args.json_output, json_content)
            atomic_write(args.markdown_output, markdown_content)
    except (SummaryError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "check" if args.check else "write",
                "families": {
                    row["family"]: {
                        "eval_id": row["accepted_run"]["eval_id"],
                        "control": pct(row["outcome"]["control_pass_rate"]),
                        "treatment": pct(row["outcome"]["treatment_pass_rate"]),
                        "delta_percentage_points": row["outcome"][
                            "absolute_percentage_point_delta"
                        ],
                        "treatment_evidence": row["outcome"][
                            "treatment_evidence_status"
                        ],
                    }
                    for row in report["families"]
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
