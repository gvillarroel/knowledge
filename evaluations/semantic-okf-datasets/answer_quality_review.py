#!/usr/bin/env python3
"""Run solution-agnostic semantic answer-quality reviews with Pi and Luna.

The reviewer sees only a frozen task-quality contract and normalized answer text.
It never sees answer-selected citations, retrieval traces, paths, hashes, locators,
strategy labels, job names, token counts, or native mechanical rewards.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "solution-agnostic-answer-quality-review/1.0"
MANIFEST_VERSION = "solution-agnostic-answer-quality-manifest/1.0"
REPORT_VERSION = "solution-agnostic-answer-quality-report/1.0"
CONSOLIDATED_REPORT_VERSION = "solution-agnostic-answer-quality-population/1.0"
EXPECTED_MODEL = "openai-codex/gpt-5.6-luna"
EXPECTED_THINKING = "high"
REQUIRED_STATUSES = ("satisfied", "partial", "missing", "contradicted")
NEGATIVE_STATUSES = ("respected", "violated")
CORRECTNESS_STATUSES = ("correct", "minor-error", "major-error")
STATUS_VALUE = {
    "satisfied": 1.0,
    "partial": 0.5,
    "missing": 0.0,
    "contradicted": 0.0,
}
STATUS_RANK = {
    "contradicted": 0,
    "missing": 1,
    "partial": 2,
    "satisfied": 3,
}
CORRECTNESS_RANK = {"major-error": 0, "minor-error": 1, "correct": 2}
DEFECT_CODE = re.compile(r"^[a-z]+(?:-[a-z]+)*$")
NUMERIC_CITATION = re.compile(r"\s*\[(?:\d+)(?:\s*,\s*\d+)*\]")


class ReviewError(ValueError):
    """Describe an invalid review input, output, or immutable artifact."""


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes."""

    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    """Return the lowercase SHA-256 digest of bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file."""

    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object from a file."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewError(f"Cannot load JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ReviewError(f"Expected a JSON object: {path}")
    return value


def _write_exclusive(path: Path, payload: bytes) -> None:
    """Create one append-only artifact and reject an existing target."""

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise ReviewError(f"Refusing to overwrite append-only artifact: {path}") from exc


def _required_string(value: Any, label: str) -> str:
    """Return a non-empty stripped string or fail closed."""

    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{label} must be a non-empty string")
    return value.strip()


def _required_statements(value: Any, label: str) -> list[str]:
    """Return a non-empty ordered array of statement strings."""

    if not isinstance(value, list) or not value:
        raise ReviewError(f"{label} must be a non-empty array")
    statements: list[str] = []
    for ordinal, item in enumerate(value, 1):
        if isinstance(item, Mapping):
            item = item.get("statement")
        statements.append(_required_string(item, f"{label}[{ordinal}]"))
    return statements


def task_quality_contract(
    question: Mapping[str, Any], truth: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Build the fixed task contract without source or solution mechanics."""

    question_id = _required_string(question.get("id"), "question.id")
    rubric = question.get("semantic_rubric")
    if not isinstance(rubric, Mapping):
        raise ReviewError("Task lacks a semantic rubric")
    required_points = _required_statements(
        rubric.get("required_points"), "semantic_rubric.required_points"
    )
    if truth is None:
        reference_claims = list(required_points)
        important_negatives: list[str] = []
        contract_basis = "semantic-rubric-only"
    else:
        truth_id = _required_string(truth.get("id"), "truth.id")
        if question_id != truth_id:
            raise ReviewError("Question and ground-truth IDs differ")
        ground_truth = truth.get("ground_truth")
        if not isinstance(ground_truth, Mapping):
            raise ReviewError("Task lacks ground truth")
        reference_claims = _required_statements(
            ground_truth.get("answer_claims"), "ground_truth.answer_claims"
        )
        important_negatives = _required_statements(
            ground_truth.get("important_negatives"), "ground_truth.important_negatives"
        )
        contract_basis = "semantic-rubric-plus-hard-ground-truth"
    return {
        "schemaVersion": SCHEMA_VERSION,
        "contractBasis": contract_basis,
        "question": _required_string(question.get("question"), "question.question"),
        "requiredPoints": [
            {"ordinal": ordinal, "criterion": statement}
            for ordinal, statement in enumerate(required_points, 1)
        ],
        "referenceClaims": [
            {"ordinal": ordinal, "statement": statement}
            for ordinal, statement in enumerate(reference_claims, 1)
        ],
        "importantNegatives": [
            {"ordinal": ordinal, "statement": statement}
            for ordinal, statement in enumerate(important_negatives, 1)
        ],
    }


def load_task_quality_contract(task_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and digest-bind a frozen task-quality contract."""

    question_path = task_dir / "tests" / "question.json"
    truth_path = task_dir / "tests" / "hard-ground-truth.json"
    truth = load_json(truth_path) if truth_path.is_file() else None
    contract = task_quality_contract(load_json(question_path), truth)
    return contract, {
        "questionSha256": sha256_file(question_path),
        "groundTruthSha256": sha256_file(truth_path) if truth is not None else None,
        "contractSha256": sha256_bytes(canonical_json_bytes(contract)),
        "contractBasis": contract["contractBasis"],
    }


def _clean_answer_text(value: Any, label: str) -> str:
    """Normalize answer prose and remove numeric citation markers."""

    text = _required_string(value, label)
    return " ".join(NUMERIC_CITATION.sub("", text).split())


def normalized_answer(answer: Mapping[str, Any]) -> dict[str, Any]:
    """Project a response to prose only, excluding all solution mechanics."""

    body = answer.get("answer")
    if not isinstance(body, Mapping):
        body = answer if any(key in answer for key in ("summary", "claims")) else None
    if not isinstance(body, Mapping):
        marker = "No semantic answer content was emitted."
        return {
            "summary": marker,
            "claims": [{"ordinal": 1, "statement": marker}],
        }
    raw_claims = body.get("claims")
    if not isinstance(raw_claims, list) or not raw_claims:
        summary = _clean_answer_text(body.get("summary"), "answer.summary")
        return {
            "summary": summary,
            "claims": [{"ordinal": 1, "statement": summary}],
        }
    claims: list[dict[str, Any]] = []
    for ordinal, claim in enumerate(raw_claims, 1):
        if not isinstance(claim, Mapping):
            raise ReviewError(f"answer.claims[{ordinal}] must be an object")
        claims.append(
            {
                "ordinal": ordinal,
                "statement": _clean_answer_text(
                    claim.get("statement"), f"answer.claims[{ordinal}].statement"
                ),
            }
        )
    return {
        "summary": _clean_answer_text(body.get("summary"), "answer.summary"),
        "claims": claims,
    }


def _assistant_text(message: Mapping[str, Any]) -> str:
    """Join visible assistant text blocks from a Pi message."""

    content = message.get("content")
    if not isinstance(content, list):
        return ""
    return "".join(
        str(block.get("text", ""))
        for block in content
        if isinstance(block, Mapping) and block.get("type") == "text"
    )


def _decode_json_object(text: str, label: str) -> dict[str, Any]:
    """Decode one possibly fenced JSON object."""

    stripped = text.strip()
    if stripped.startswith("```json"):
        stripped = stripped[7:].lstrip()
    elif stripped.startswith("```"):
        stripped = stripped[3:].lstrip()
    try:
        value, end = json.JSONDecoder().raw_decode(stripped)
    except json.JSONDecodeError as exc:
        raise ReviewError(f"{label} is not a JSON object") from exc
    remainder = stripped[end:].strip()
    if remainder == "```":
        remainder = ""
    if remainder or not isinstance(value, dict):
        raise ReviewError(f"{label} must contain exactly one JSON object")
    return value


def _decode_first_json_object(text: str, label: str) -> dict[str, Any]:
    """Decode the first JSON object while tolerating non-semantic trailing text."""

    stripped = text.strip()
    if stripped.startswith("```json"):
        stripped = stripped[7:].lstrip()
    elif stripped.startswith("```"):
        stripped = stripped[3:].lstrip()
    try:
        value, _ = json.JSONDecoder().raw_decode(stripped)
    except json.JSONDecodeError as exc:
        raise ReviewError(f"{label} does not begin with a JSON object") from exc
    if not isinstance(value, dict):
        raise ReviewError(f"{label} must begin with a JSON object")
    return value


def extract_final_response(trace_path: Path) -> dict[str, Any]:
    """Extract the last visible assistant JSON response from a Pi trace."""

    final_text: str | None = None
    try:
        with trace_path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if '"message_end"' not in line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ReviewError(f"Invalid Pi JSONL at line {number}: {trace_path}") from exc
                message = event.get("message")
                if (
                    isinstance(message, Mapping)
                    and message.get("role") == "assistant"
                ):
                    text = _assistant_text(message)
                    if text.strip():
                        final_text = text
    except OSError as exc:
        raise ReviewError(f"Cannot read Pi trace: {trace_path}") from exc
    if final_text is None:
        raise ReviewError(f"Pi trace lacks a final assistant response: {trace_path}")
    return _decode_first_json_object(final_text, "Final response")


def aggregate_job_metrics(job: Path) -> dict[str, Any]:
    """Derive native mechanical and efficiency metrics from completed trials."""

    rewards: list[float] = []
    total_tokens: list[int] = []
    costs: list[float] = []
    latencies: list[float] = []
    evidence_valid = 0
    trial_count = 0
    for trial_dir in sorted(path for path in job.iterdir() if path.is_dir()):
        if re.fullmatch(r"q\d{3}__[A-Za-z0-9]+", trial_dir.name) is None:
            continue
        result = load_json(trial_dir / "result.json")
        trial_count += 1
        verifier = result.get("verifier_result")
        reward_map = verifier.get("rewards") if isinstance(verifier, Mapping) else None
        if isinstance(reward_map, Mapping) and isinstance(reward_map.get("reward"), (int, float)):
            rewards.append(float(reward_map["reward"]))
            evidence_valid += float(reward_map.get("all_evidence_valid", 0.0)) >= 1.0
        agent = result.get("agent_result")
        if isinstance(agent, Mapping):
            input_tokens = agent.get("n_input_tokens")
            output_tokens = agent.get("n_output_tokens")
            if isinstance(input_tokens, int) and isinstance(output_tokens, int):
                total_tokens.append(input_tokens + output_tokens)
            if isinstance(agent.get("cost_usd"), (int, float)):
                costs.append(float(agent["cost_usd"]))
        timing = result.get("agent_execution")
        if (
            isinstance(timing, Mapping)
            and isinstance(timing.get("started_at"), str)
            and isinstance(timing.get("finished_at"), str)
        ):
            try:
                started = datetime.fromisoformat(
                    timing["started_at"].replace("Z", "+00:00")
                )
                finished = datetime.fromisoformat(
                    timing["finished_at"].replace("Z", "+00:00")
                )
            except ValueError:
                pass
            else:
                latencies.append((finished - started).total_seconds() * 1000)
        elif isinstance(timing, (int, float)):
            latencies.append(float(timing))

    def mean(values: Sequence[int | float]) -> float | None:
        return round(sum(values) / len(values), 6) if values else None

    return {
        "trialCount": trial_count,
        "meanNativeReward": mean(rewards),
        "meanAgentTokens": mean(total_tokens),
        "meanCostUsd": mean(costs),
        "meanAgentLatencyMs": mean(latencies),
        "evidenceValidCaseCount": evidence_valid,
    }


def collect_job(job: Path) -> dict[str, dict[str, Any]]:
    """Collect completed task responses from a locked Luna Harbor job."""

    lock = load_json(job / "lock.json")
    trials = lock.get("trials")
    if not isinstance(trials, list) or not trials:
        raise ReviewError(f"Job lacks locked trials: {job}")
    collected: dict[str, dict[str, Any]] = {}
    for trial_dir in sorted(path for path in job.iterdir() if path.is_dir()):
        if re.fullmatch(r"q\d{3}__[A-Za-z0-9]+", trial_dir.name) is None:
            continue
        result = load_json(trial_dir / "result.json")
        if result.get("exception_info") is not None:
            raise ReviewError(f"Errored trial is not answer evidence: {trial_dir}")
        question_id = trial_dir.name.split("__", 1)[0]
        if question_id in collected:
            raise ReviewError(f"Duplicate question in job: {question_id}")
        response = extract_final_response(trial_dir / "artifacts" / "pi.jsonl")
        collected[question_id] = {
            "answer": normalized_answer(response),
            "answerSha256": sha256_bytes(canonical_json_bytes(response)),
            "taskChecksum": _required_string(
                result.get("task_checksum"), f"{question_id}.task_checksum"
            ),
        }
    if len(collected) != len(trials):
        raise ReviewError(
            f"Collected {len(collected)} responses for {len(trials)} locked trials: {job}"
        )
    return collected


def _answer_labels(count: int) -> list[str]:
    """Return stable anonymous labels for a pair or larger population."""

    if count == 2:
        return ["answer-a", "answer-b"]
    return [f"answer-{ordinal:03d}" for ordinal in range(1, count + 1)]


def review_packet(
    contract: Mapping[str, Any], answers: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Build one reviewer-visible packet from truth and anonymized prose."""

    if len(answers) < 2:
        raise ReviewError("A counterbalanced review packet requires at least two answers")
    labels = _answer_labels(len(answers))
    normalized = []
    for label, answer in zip(labels, answers, strict=True):
        if not isinstance(answer, Mapping):
            raise ReviewError("Review answers must be objects")
        normalized.append(
            {
                "answerLabel": label,
                "response": dict(answer),
            }
        )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "qualityContract": dict(contract),
        "answers": normalized,
    }


def render_prompt(packet: Mapping[str, Any]) -> str:
    """Render a no-tools independent review prompt bound to one packet."""

    packet_sha256 = sha256_bytes(canonical_json_bytes(packet))
    required_count = len(packet["qualityContract"]["requiredPoints"])
    negative_count = len(packet["qualityContract"]["importantNegatives"])
    output_judgments = [
        {
            "answerLabel": answer["answerLabel"],
            "requiredPointStatuses": ["status-for-each-required-point"],
            "importantNegativeStatuses": ["status-for-each-important-negative"],
            "materialCorrectness": "correct-or-minor-error-or-major-error",
            "defectCodes": [],
        }
        for answer in packet["answers"]
    ]
    output_shape = {
        "schemaVersion": SCHEMA_VERSION,
        "packetSha256": packet_sha256,
        "judgments": output_judgments,
    }
    return f"""You are an independent semantic answer-quality reviewer.

Evaluate each anonymized response independently against the same frozen quality contract. Do not compare response wording, style, length, citations, retrieval behavior, or presumed strategy. Use only the question, required points, reference claims, important negatives, and response prose in the packet. Do not use tools or outside knowledge.

For every response:
- Treat the reference claims as the authoritative semantic interpretation of the question and required points, not as optional examples or a required wording template.
- Equivalent wording and logically equivalent synthesis receive full credit. However, a true but adjacent result, experiment, code distance, noise model, or numerical quantity does not substitute for the concrete target fixed by the relevant reference claim.
- When a response replaces a target result with a different result from the same broader topic, mark the affected required point `partial` or `missing`; also use `major-error` when the substitution materially misidentifies the requested experiment or conclusion.
- Return exactly {required_count} required-point statuses in contract order.
- `satisfied`: the response correctly and explicitly covers the full required point.
- `partial`: relevant correct content is present, but a material part of the point is absent or imprecise.
- `missing`: the point is not established.
- `contradicted`: the response materially conflicts with the point or fixed reference claims.
- Return exactly {negative_count} important-negative statuses in contract order: `respected` or `violated`.
- Set material correctness to `correct`, `minor-error`, or `major-error`. A scope conflation, false attribution, or substantive contradiction is a major error; a bounded imprecision that does not change a required conclusion is minor.
- Use only generic lowercase kebab-case defect codes. Do not return explanations, quotes, task identifiers, source names, or answer text.

Return exactly one JSON object with these keys and no markdown fence. Replace
every placeholder with an allowed status and preserve every answer label and
its order:
{json.dumps(output_shape, ensure_ascii=False, indent=2)}

Frozen review packet:
{json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True)}
"""


def validate_judgment(
    result: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate one reviewer result and derive no model-authored score."""

    expected_packet_sha = sha256_bytes(canonical_json_bytes(packet))
    expected_top_keys = {"schemaVersion", "packetSha256", "judgments"}
    if set(result) != expected_top_keys:
        raise ReviewError("Review result has missing or unknown top-level keys")
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewError("Review schema version mismatch")
    if result.get("packetSha256") != expected_packet_sha:
        raise ReviewError("Review packet digest mismatch")
    required_count = len(packet["qualityContract"]["requiredPoints"])
    negative_count = len(packet["qualityContract"]["importantNegatives"])
    judgments = result.get("judgments")
    expected_labels = [str(answer["answerLabel"]) for answer in packet["answers"]]
    if not isinstance(judgments, list) or len(judgments) != len(expected_labels):
        raise ReviewError("Review must contain exactly one judgment per answer")
    normalized: list[dict[str, Any]] = []
    exact_keys = {
        "answerLabel",
        "requiredPointStatuses",
        "importantNegativeStatuses",
        "materialCorrectness",
        "defectCodes",
    }
    for label, judgment in zip(expected_labels, judgments, strict=True):
        if not isinstance(judgment, Mapping) or set(judgment) != exact_keys:
            raise ReviewError("Review judgment has missing or unknown keys")
        if judgment.get("answerLabel") != label:
            raise ReviewError("Review answer labels are missing or reordered")
        required_statuses = judgment.get("requiredPointStatuses")
        negative_statuses = judgment.get("importantNegativeStatuses")
        correctness = judgment.get("materialCorrectness")
        codes = judgment.get("defectCodes")
        if (
            not isinstance(required_statuses, list)
            or len(required_statuses) != required_count
            or any(status not in REQUIRED_STATUSES for status in required_statuses)
        ):
            raise ReviewError("Invalid required-point statuses")
        if (
            not isinstance(negative_statuses, list)
            or len(negative_statuses) != negative_count
            or any(status not in NEGATIVE_STATUSES for status in negative_statuses)
        ):
            raise ReviewError("Invalid important-negative statuses")
        if correctness not in CORRECTNESS_STATUSES:
            raise ReviewError("Invalid material-correctness status")
        if (
            not isinstance(codes, list)
            or len(codes) > 12
            or any(not isinstance(code, str) or DEFECT_CODE.fullmatch(code) is None for code in codes)
        ):
            raise ReviewError("Defect codes must be bounded lowercase kebab-case labels")
        normalized.append(
            {
                "answerLabel": label,
                "requiredPointStatuses": list(required_statuses),
                "importantNegativeStatuses": list(negative_statuses),
                "materialCorrectness": correctness,
                "defectCodes": list(codes),
            }
        )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetSha256": expected_packet_sha,
        "judgments": normalized,
    }


def _relative_path(path: Path, root: Path) -> str:
    """Return a portable path relative to an artifact root."""

    return path.resolve().relative_to(root.resolve()).as_posix()


def prepare_review(
    task_root: Path,
    jobs: Sequence[tuple[str, Path]],
    output_dir: Path,
) -> dict[str, Any]:
    """Create an append-only counterbalanced review manifest and prompts."""

    if len(jobs) < 2 or len({name for name, _ in jobs}) != len(jobs):
        raise ReviewError("At least two distinctly named jobs are required")
    collected = [(name, path.resolve(), collect_job(path.resolve())) for name, path in jobs]
    question_ids = sorted(collected[0][2])
    if set(question_ids) != set(collected[1][2]):
        raise ReviewError("Jobs do not contain the same question set")
    manifest: dict[str, Any] = {
        "schemaVersion": MANIFEST_VERSION,
        "reviewSchemaVersion": SCHEMA_VERSION,
        "model": EXPECTED_MODEL,
        "thinking": EXPECTED_THINKING,
        "promptRenderer": "counterbalanced-population-v2",
        "isolation": {
            "answerEvidenceVisible": False,
            "retrievalTraceVisible": False,
            "strategyIdentityVisible": False,
            "jobIdentityVisible": False,
            "mechanicalRewardVisible": False,
            "tokenUsageVisible": False,
            "scoringMode": "independent-fixed-contract-counterbalanced",
        },
        "arms": [
            {
                "armId": name,
                "jobPath": str(path),
                "jobLockSha256": sha256_file(path / "lock.json"),
                "nativeMetrics": aggregate_job_metrics(path),
            }
            for name, path, _ in collected
        ],
        "cases": [],
        "prompts": [],
    }
    for case_ordinal, question_id in enumerate(question_ids, 1):
        first = collected[0][2][question_id]
        second = collected[1][2][question_id]
        if first["taskChecksum"] != second["taskChecksum"]:
            raise ReviewError(f"Task checksum drift between arms: {question_id}")
        contract, contract_bindings = load_task_quality_contract(task_root / question_id)
        case = {
            "ordinal": case_ordinal,
            "questionId": question_id,
            "taskChecksum": first["taskChecksum"],
            **contract_bindings,
            "answers": {
                collected[0][0]: first["answerSha256"],
                collected[1][0]: second["answerSha256"],
            },
        }
        manifest["cases"].append(case)
        forward_order = tuple(range(len(collected)))
        orientations = (
            ("forward", forward_order),
            ("reverse", tuple(reversed(forward_order))),
        )
        for orientation, order in orientations:
            answer_values = [collected[index][2][question_id]["answer"] for index in order]
            packet = review_packet(contract, answer_values)
            prompt = render_prompt(packet)
            prompt_path = output_dir / "prompts" / f"case-{case_ordinal:03d}-{orientation}.md"
            packet_path = output_dir / "packets" / f"case-{case_ordinal:03d}-{orientation}.json"
            _write_exclusive(prompt_path, prompt.encode("utf-8"))
            _write_exclusive(packet_path, canonical_json_bytes(packet))
            label_map = {
                answer["answerLabel"]: collected[index][0]
                for answer, index in zip(packet["answers"], order, strict=True)
            }
            manifest["prompts"].append(
                {
                    "caseOrdinal": case_ordinal,
                    "orientation": orientation,
                    "promptPath": _relative_path(prompt_path, output_dir),
                    "promptSha256": sha256_file(prompt_path),
                    "packetPath": _relative_path(packet_path, output_dir),
                    "packetSha256": sha256_file(packet_path),
                    "labelMap": label_map,
                    "resultPath": f"results/case-{case_ordinal:03d}-{orientation}.json",
                    "rawResultPath": f"raw/case-{case_ordinal:03d}-{orientation}.txt",
                }
            )
    manifest_path = output_dir / "manifest.json"
    _write_exclusive(manifest_path, canonical_json_bytes(manifest))
    return {
        "manifestPath": str(manifest_path.resolve()),
        "manifestSha256": sha256_file(manifest_path),
        "caseCount": len(manifest["cases"]),
        "reviewCallCount": len(manifest["prompts"]),
    }


def validate_manifest(manifest_path: Path) -> dict[str, Any]:
    """Validate prompt and packet digests in a prepared review."""

    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != MANIFEST_VERSION:
        raise ReviewError("Review manifest schema mismatch")
    if manifest.get("model") != EXPECTED_MODEL or manifest.get("thinking") != EXPECTED_THINKING:
        raise ReviewError("Review manifest is not pinned to Luna with high thinking")
    isolation = manifest.get("isolation")
    if not isinstance(isolation, Mapping) or any(
        isolation.get(key) is not False
        for key in (
            "answerEvidenceVisible",
            "retrievalTraceVisible",
            "strategyIdentityVisible",
            "jobIdentityVisible",
            "mechanicalRewardVisible",
            "tokenUsageVisible",
        )
    ):
        raise ReviewError("Review manifest does not enforce solution isolation")
    root = manifest_path.parent
    prompts = manifest.get("prompts")
    if not isinstance(prompts, list) or not prompts:
        raise ReviewError("Review manifest lacks prompts")
    seen: set[tuple[int, str]] = set()
    for item in prompts:
        if not isinstance(item, Mapping):
            raise ReviewError("Review prompt entry must be an object")
        key = (int(item.get("caseOrdinal", 0)), str(item.get("orientation")))
        if key in seen or key[1] not in {"forward", "reverse"}:
            raise ReviewError("Review prompt orientation is invalid or duplicated")
        seen.add(key)
        prompt_path = root / _required_string(item.get("promptPath"), "promptPath")
        packet_path = root / _required_string(item.get("packetPath"), "packetPath")
        if sha256_file(prompt_path) != item.get("promptSha256"):
            raise ReviewError(f"Review prompt digest drift: {prompt_path}")
        if sha256_file(packet_path) != item.get("packetSha256"):
            raise ReviewError(f"Review packet digest drift: {packet_path}")
        packet = load_json(packet_path)
        if manifest.get("promptRenderer") == "counterbalanced-population-v2":
            expected_prompt = render_prompt(packet).encode("utf-8")
            if prompt_path.read_bytes() != expected_prompt:
                raise ReviewError(f"Review prompt content drift: {prompt_path}")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(prompts) != len(cases) * 2:
        raise ReviewError("Every review case must have two counterbalanced prompts")
    return manifest


def _run_one_prompt(
    executable: str,
    root: Path,
    item: Mapping[str, Any],
) -> dict[str, Any]:
    """Run and validate one isolated Pi/Luna review call."""

    packet_path = root / str(item["packetPath"])
    prompt_path = root / str(item["promptPath"])
    raw_path = root / str(item["rawResultPath"])
    result_path = root / str(item["resultPath"])
    packet = load_json(packet_path)
    if result_path.is_file():
        validated = validate_judgment(load_json(result_path), packet)
        return {"resultPath": str(result_path), "status": "reused", "result": validated}
    if raw_path.exists() or result_path.exists():
        raise ReviewError(f"Incomplete append-only review result target: {result_path}")
    command = [
        executable,
        "--model",
        EXPECTED_MODEL,
        "--thinking",
        EXPECTED_THINKING,
        "--no-session",
        "--no-tools",
        "--no-skills",
        "--no-prompt-templates",
        "--no-extensions",
        "--no-context-files",
        "--mode",
        "text",
        "--print",
        f"@{prompt_path.resolve()}",
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=900,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip().replace("\n", " ")[-800:]
        raise ReviewError(
            f"Pi review failed for {prompt_path.name} with exit {completed.returncode}: {stderr}"
        )
    result = _decode_json_object(completed.stdout, f"Pi output for {prompt_path.name}")
    validated = validate_judgment(result, packet)
    _write_exclusive(raw_path, completed.stdout.encode("utf-8"))
    _write_exclusive(result_path, canonical_json_bytes(validated))
    return {"resultPath": str(result_path), "status": "created", "result": validated}


def run_reviews(
    manifest_path: Path, *, max_workers: int = 2, executable: str | None = None
) -> dict[str, Any]:
    """Execute all missing counterbalanced reviews with isolated Pi/Luna calls."""

    if max_workers < 1 or max_workers > 4:
        raise ReviewError("max_workers must be between 1 and 4")
    manifest = validate_manifest(manifest_path)
    selected_executable = executable or shutil.which("pi")
    if selected_executable is None:
        raise ReviewError("Cannot find the pi executable")
    outcomes: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_run_one_prompt, selected_executable, manifest_path.parent, item): item
            for item in manifest["prompts"]
        }
        for future in as_completed(futures):
            outcomes.append(future.result())
    counts = Counter(outcome["status"] for outcome in outcomes)
    return {
        "status": "complete",
        "model": EXPECTED_MODEL,
        "thinking": EXPECTED_THINKING,
        "reviewCallCount": len(outcomes),
        "created": counts["created"],
        "reused": counts["reused"],
    }


def conservative_consensus(judgments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Combine counterbalanced judgments conservatively and report agreement."""

    if len(judgments) != 2:
        raise ReviewError("Consensus requires exactly two orientation judgments")
    required_lengths = {len(item["requiredPointStatuses"]) for item in judgments}
    negative_lengths = {len(item["importantNegativeStatuses"]) for item in judgments}
    if len(required_lengths) != 1 or len(negative_lengths) != 1:
        raise ReviewError("Counterbalanced judgment dimensions differ")
    required = [
        min(
            (str(item["requiredPointStatuses"][index]) for item in judgments),
            key=STATUS_RANK.__getitem__,
        )
        for index in range(next(iter(required_lengths)))
    ]
    negatives = [
        "violated"
        if any(item["importantNegativeStatuses"][index] == "violated" for item in judgments)
        else "respected"
        for index in range(next(iter(negative_lengths)))
    ]
    correctness = min(
        (str(item["materialCorrectness"]) for item in judgments),
        key=CORRECTNESS_RANK.__getitem__,
    )
    exact_cells = sum(
        judgments[0]["requiredPointStatuses"][index]
        == judgments[1]["requiredPointStatuses"][index]
        for index in range(len(required))
    ) + sum(
        judgments[0]["importantNegativeStatuses"][index]
        == judgments[1]["importantNegativeStatuses"][index]
        for index in range(len(negatives))
    ) + (judgments[0]["materialCorrectness"] == judgments[1]["materialCorrectness"])
    total_cells = len(required) + len(negatives) + 1
    coverage = sum(STATUS_VALUE[status] for status in required) / len(required)
    return {
        "requiredPointStatuses": required,
        "importantNegativeStatuses": negatives,
        "materialCorrectness": correctness,
        "defectCodes": sorted(
            {str(code) for item in judgments for code in item["defectCodes"]}
        ),
        "requiredPointCoverage": round(coverage, 6),
        "casePass": (
            all(status == "satisfied" for status in required)
            and all(status == "respected" for status in negatives)
            and correctness == "correct"
        ),
        "orientationAgreement": round(exact_cells / total_cells, 6),
        "agreementCells": exact_cells,
        "agreementCellCount": total_cells,
    }


def _comparison_outcome(first: Mapping[str, Any], second: Mapping[str, Any]) -> str:
    """Classify the second arm against the first using derived quality states."""

    first_vector = (
        float(first["requiredPointCoverage"]),
        -sum(status == "violated" for status in first["importantNegativeStatuses"]),
        CORRECTNESS_RANK[str(first["materialCorrectness"])],
        int(bool(first["casePass"])),
    )
    second_vector = (
        float(second["requiredPointCoverage"]),
        -sum(status == "violated" for status in second["importantNegativeStatuses"]),
        CORRECTNESS_RANK[str(second["materialCorrectness"])],
        int(bool(second["casePass"])),
    )
    if second_vector == first_vector:
        return "tie"
    if all(after >= before for before, after in zip(first_vector, second_vector, strict=True)):
        return "improved"
    if all(after <= before for before, after in zip(first_vector, second_vector, strict=True)):
        return "regressed"
    return "mixed"


def build_report(manifest_path: Path) -> dict[str, Any]:
    """Validate all outputs and derive arm-level and paired quality metrics."""

    manifest = validate_manifest(manifest_path)
    root = manifest_path.parent
    observations: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for item in manifest["prompts"]:
        packet = load_json(root / item["packetPath"])
        result = validate_judgment(load_json(root / item["resultPath"]), packet)
        for judgment in result["judgments"]:
            arm = item["labelMap"][judgment["answerLabel"]]
            observations.setdefault((int(item["caseOrdinal"]), arm), []).append(judgment)
    arm_ids = [str(item["armId"]) for item in manifest["arms"]]
    case_rows: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        ordinal = int(case["ordinal"])
        arms = {
            arm: conservative_consensus(observations[(ordinal, arm)])
            for arm in arm_ids
        }
        case_rows.append(
            {
                "ordinal": ordinal,
                "questionId": case["questionId"],
                "arms": arms,
                "armOutcomes": {
                    arm: (
                        "baseline"
                        if arm == arm_ids[0]
                        else _comparison_outcome(arms[arm_ids[0]], arms[arm])
                    )
                    for arm in arm_ids
                },
            }
        )
        if len(arm_ids) == 2:
            case_rows[-1]["secondArmOutcome"] = case_rows[-1]["armOutcomes"][arm_ids[1]]
    native_metrics = {
        str(item["armId"]): item.get("nativeMetrics", {}) for item in manifest["arms"]
    }
    aggregates: dict[str, Any] = {}
    for arm in arm_ids:
        rows = [case["arms"][arm] for case in case_rows]
        statuses = Counter(
            status for row in rows for status in row["requiredPointStatuses"]
        )
        negatives = Counter(
            status for row in rows for status in row["importantNegativeStatuses"]
        )
        correctness = Counter(row["materialCorrectness"] for row in rows)
        agreement_cells = sum(row["agreementCells"] for row in rows)
        agreement_total = sum(row["agreementCellCount"] for row in rows)
        aggregates[arm] = {
            "caseCount": len(rows),
            "casePassCount": sum(bool(row["casePass"]) for row in rows),
            "meanRequiredPointCoverage": round(
                sum(float(row["requiredPointCoverage"]) for row in rows) / len(rows), 6
            ),
            "requiredPointStatuses": dict(sorted(statuses.items())),
            "importantNegativeStatuses": dict(sorted(negatives.items())),
            "materialCorrectness": dict(sorted(correctness.items())),
            "orientationAgreement": round(agreement_cells / agreement_total, 6),
            "nativeMetrics": native_metrics.get(arm, {}),
        }
    paired_outcomes_by_arm = {
        arm: dict(
            sorted(Counter(row["armOutcomes"][arm] for row in case_rows).items())
        )
        for arm in arm_ids[1:]
    }
    report = {
        "schemaVersion": REPORT_VERSION,
        "reviewSchemaVersion": SCHEMA_VERSION,
        "manifestSha256": sha256_file(manifest_path),
        "model": manifest["model"],
        "thinking": manifest["thinking"],
        "method": manifest["isolation"],
        "armOrder": arm_ids,
        "aggregates": aggregates,
        "pairedOutcomesByArm": paired_outcomes_by_arm,
        "cases": case_rows,
    }
    if len(arm_ids) == 2:
        report["pairedSecondArmOutcomes"] = paired_outcomes_by_arm[arm_ids[1]]
    return report


def render_report_table(report: Mapping[str, Any]) -> str:
    """Render a reviewed aggregate Markdown table without private task content."""

    arms = report["armOrder"]
    if len(arms) > 2:
        return render_population_report_table(report)
    lines = [
        "# Solution-agnostic answer-quality audit",
        "",
        "The same completed answers were re-adjudicated independently against the frozen semantic rubric and ground-truth claim contract. Answer-selected evidence, retrieval traces, strategies, paths, hashes, locators, native rewards, and token counts were hidden. Each case was reviewed twice by Pi with GPT-5.6 Luna at high thinking, with answer order reversed; the published score is the conservative consensus.",
        "",
        "| Metric | " + " | ".join(arms) + " |",
        "| --- | " + " | ".join("---:" for _ in arms) + " |",
    ]
    metric_rows = (
        ("Full-quality cases", "casePassCount"),
        ("Mean required-point coverage", "meanRequiredPointCoverage"),
        ("Orientation agreement", "orientationAgreement"),
    )
    for label, key in metric_rows:
        values = []
        for arm in arms:
            value = report["aggregates"][arm][key]
            values.append(
                f"{value * 100:.2f}%"
                if isinstance(value, float)
                else f"{value}/{report['aggregates'][arm]['caseCount']}"
            )
        lines.append(f"| {label} | " + " | ".join(values) + " |")
    lines.extend(
        [
            "",
            "| Required-point status | " + " | ".join(arms) + " |",
            "| --- | " + " | ".join("---:" for _ in arms) + " |",
        ]
    )
    for status in REQUIRED_STATUSES:
        lines.append(
            f"| {status} | "
            + " | ".join(
                str(report["aggregates"][arm]["requiredPointStatuses"].get(status, 0))
                for arm in arms
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "| Case | " + " | ".join(arms) + " | Second-arm result |",
            "| ---: | " + " | ".join("---" for _ in arms) + " | --- |",
        ]
    )
    for case in report["cases"]:
        values = []
        for arm in arms:
            row = case["arms"][arm]
            values.append(
                f"{'pass' if row['casePass'] else 'fail'}; "
                f"{float(row['requiredPointCoverage']) * 100:.1f}%; "
                f"{row['materialCorrectness']}"
            )
        lines.append(
            f"| {case['ordinal']} | "
            + " | ".join(values)
            + f" | {case['secondArmOutcome']} |"
        )
    outcomes = report["pairedSecondArmOutcomes"]
    lines.extend(
        [
            "",
            "Second-arm paired outcomes: "
            + ", ".join(f"{key}={value}" for key, value in sorted(outcomes.items()))
            + ".",
            "",
            "This semantic table supersedes native mechanical reward for quality claims. Native reward remains valid only for contract compliance and focus/evidence-anchor coverage; efficiency measurements remain separate.",
            "",
        ]
    )
    return "\n".join(lines)


def _metric(value: Any, digits: int = 2) -> str:
    """Format a finite aggregate metric or an unavailable marker."""

    if not isinstance(value, (int, float)):
        return "-"
    return f"{float(value):,.{digits}f}"


def render_population_report_table(report: Mapping[str, Any]) -> str:
    """Render a row-oriented aggregate table for a strategy population."""

    arms = report["armOrder"]
    lines = [
        "# Solution-agnostic population answer-quality audit",
        "",
        "Every completed response was adjudicated independently against the same frozen semantic contract. Answer-selected evidence, retrieval traces, strategies, paths, hashes, locators, native rewards, and token counts were hidden from Pi/GPT-5.6 Luna. Each case was reviewed twice with the full strategy order reversed; semantic metrics use conservative consensus.",
        "",
        "| Strategy | Native reward | Mean tokens | Evidence valid | Full-quality | Required-point coverage | Satisfied points | Major-error cases | Negative violations | Orientation agreement | Paired result vs baseline |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    case_count = report["aggregates"][arms[0]]["caseCount"]
    for arm in arms:
        aggregate = report["aggregates"][arm]
        native = aggregate.get("nativeMetrics", {})
        outcomes = report["pairedOutcomesByArm"].get(arm)
        paired = "baseline" if arm == arms[0] else ", ".join(
            f"{key}={value}" for key, value in sorted(outcomes.items())
        )
        correctness = aggregate["materialCorrectness"]
        negatives = aggregate["importantNegativeStatuses"]
        lines.append(
            "| "
            + " | ".join(
                (
                    arm,
                    _metric(native.get("meanNativeReward"), 3),
                    _metric(native.get("meanAgentTokens"), 1),
                    f"{native.get('evidenceValidCaseCount', 0)}/{case_count}",
                    f"{aggregate['casePassCount']}/{case_count}",
                    f"{aggregate['meanRequiredPointCoverage'] * 100:.2f}%",
                    str(aggregate["requiredPointStatuses"].get("satisfied", 0)),
                    str(correctness.get("major-error", 0)),
                    str(negatives.get("violated", 0)),
                    f"{aggregate['orientationAgreement'] * 100:.2f}%",
                    paired,
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Native reward and evidence validity are mechanical metrics, not semantic quality. Mean tokens are Harbor input plus output tokens; cached input is already included in Harbor input and is not added twice.",
            "",
        ]
    )
    return "\n".join(lines)


def _contract_basis(case: Mapping[str, Any]) -> str:
    """Return an explicit or backward-compatible task contract basis."""

    basis = case.get("contractBasis")
    if isinstance(basis, str):
        return basis
    return (
        "semantic-rubric-plus-hard-ground-truth"
        if isinstance(case.get("groundTruthSha256"), str)
        else "semantic-rubric-only"
    )


def build_consolidated_report(
    cohorts: Sequence[tuple[str, Path]],
) -> dict[str, Any]:
    """Combine comparable cohort reports without ranking across cohorts."""

    if not cohorts or len({name for name, _ in cohorts}) != len(cohorts):
        raise ReviewError("Consolidation requires distinctly named cohorts")
    cohort_rows: list[dict[str, Any]] = []
    for cohort_id, manifest_path in cohorts:
        manifest = validate_manifest(manifest_path)
        quality = build_report(manifest_path)
        bases = sorted({_contract_basis(case) for case in manifest["cases"]})
        if len(bases) != 1:
            raise ReviewError(f"Cohort mixes quality contract bases: {cohort_id}")
        arm_manifest = {str(item["armId"]): item for item in manifest["arms"]}
        baseline_id = quality["armOrder"][0]
        baseline = quality["aggregates"][baseline_id]
        baseline_native = baseline.get("nativeMetrics") or aggregate_job_metrics(
            Path(arm_manifest[baseline_id]["jobPath"])
        )
        baseline_tokens = baseline_native.get("meanAgentTokens")
        for arm in quality["armOrder"]:
            aggregate = quality["aggregates"][arm]
            native = aggregate.get("nativeMetrics") or aggregate_job_metrics(
                Path(arm_manifest[arm]["jobPath"])
            )
            outcomes = quality["pairedOutcomesByArm"].get(arm, {})
            if arm == baseline_id:
                semantic_gate = "baseline"
                paired = "baseline"
            else:
                semantic_gate = (
                    "non-regressed"
                    if not outcomes.get("regressed") and not outcomes.get("mixed")
                    else "reject"
                )
                paired = ", ".join(
                    f"{key}={value}" for key, value in sorted(outcomes.items())
                )
            tokens = native.get("meanAgentTokens")
            token_delta = (
                round((tokens / baseline_tokens - 1.0) * 100.0, 6)
                if isinstance(tokens, (int, float))
                and isinstance(baseline_tokens, (int, float))
                and baseline_tokens
                else None
            )
            status_counts = aggregate["requiredPointStatuses"]
            point_count = sum(int(value) for value in status_counts.values())
            cohort_rows.append(
                {
                    "cohort": cohort_id,
                    "contractBasis": bases[0],
                    "caseCount": aggregate["caseCount"],
                    "strategy": arm,
                    "nativeReward": native.get("meanNativeReward"),
                    "meanAgentTokens": tokens,
                    "tokenDeltaPercent": token_delta,
                    "evidenceValidCaseCount": native.get("evidenceValidCaseCount"),
                    "fullQualityCaseCount": aggregate["casePassCount"],
                    "requiredPointCoverage": aggregate["meanRequiredPointCoverage"],
                    "coverageDeltaPoints": round(
                        (
                            aggregate["meanRequiredPointCoverage"]
                            - baseline["meanRequiredPointCoverage"]
                        )
                        * 100.0,
                        6,
                    ),
                    "satisfiedPointCount": status_counts.get("satisfied", 0),
                    "requiredPointCount": point_count,
                    "majorErrorCaseCount": aggregate["materialCorrectness"].get(
                        "major-error", 0
                    ),
                    "negativeViolationCount": aggregate[
                        "importantNegativeStatuses"
                    ].get("violated", 0),
                    "orientationAgreement": aggregate["orientationAgreement"],
                    "pairedOutcome": paired,
                    "semanticGate": semantic_gate,
                }
            )
    return {
        "schemaVersion": CONSOLIDATED_REPORT_VERSION,
        "reviewSchemaVersion": SCHEMA_VERSION,
        "model": EXPECTED_MODEL,
        "thinking": EXPECTED_THINKING,
        "crossCohortRankingAllowed": False,
        "cohortCount": len(cohorts),
        "strategyRowCount": len(cohort_rows),
        "rows": cohort_rows,
    }


def render_consolidated_table(report: Mapping[str, Any]) -> str:
    """Render one complete cohort-grouped strategy comparison table."""

    lines = [
        "# Complete solution-agnostic Classical knowledge-generation strategy audit",
        "",
        "The table covers every completed strategy job in the Classical chunking program. Semantic review used Pi with GPT-5.6 Luna at high thinking, two full-order-reversed judgments per case, and conservative consensus. Reviewer-visible inputs excluded answer-selected evidence, retrieval traces, strategy and job names, paths, hashes, locators, native rewards, and token usage.",
        "",
        "Rows are comparable only within the same cohort. `rubric-only` means the historical task predates separate hard-ground-truth claims; `rubric+truth` uses both authored required points and hard-ground-truth claims. Native reward remains mechanical, not semantic quality.",
        "",
        "| Cohort | Contract | Strategy | Native reward | Mean tokens | Token delta | Evidence valid | Full-quality | Required coverage | Coverage delta | Satisfied points | Major-error cases | Order agreement | Paired result vs canonical | Semantic gate |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    basis_labels = {
        "semantic-rubric-only": "rubric-only",
        "semantic-rubric-plus-hard-ground-truth": "rubric+truth",
    }
    for row in report["rows"]:
        token_delta = row["tokenDeltaPercent"]
        coverage_delta = row["coverageDeltaPoints"]
        lines.append(
            "| "
            + " | ".join(
                (
                    row["cohort"],
                    basis_labels.get(row["contractBasis"], row["contractBasis"]),
                    row["strategy"],
                    _metric(row["nativeReward"], 3),
                    _metric(row["meanAgentTokens"], 1),
                    f"{token_delta:+.2f}%" if isinstance(token_delta, (int, float)) else "-",
                    f"{row['evidenceValidCaseCount']}/{row['caseCount']}",
                    f"{row['fullQualityCaseCount']}/{row['caseCount']}",
                    f"{row['requiredPointCoverage'] * 100:.2f}%",
                    f"{coverage_delta:+.2f} pp",
                    f"{row['satisfiedPointCount']}/{row['requiredPointCount']}",
                    f"{row['majorErrorCaseCount']}/{row['caseCount']}",
                    f"{row['orientationAgreement'] * 100:.2f}%",
                    row["pairedOutcome"],
                    row["semanticGate"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "The semantic gate is strict paired non-regression within a cohort. A mixed or regressed case rejects the treatment even when aggregate coverage or efficiency improves. No cross-cohort winner is declared.",
            "",
        ]
    )
    return "\n".join(lines)


def write_consolidated_report(
    cohorts: Sequence[tuple[str, Path]], report_path: Path, table_path: Path
) -> dict[str, Any]:
    """Write append-only consolidated private JSON and public aggregate Markdown."""

    report = build_consolidated_report(cohorts)
    _write_exclusive(report_path, canonical_json_bytes(report))
    _write_exclusive(table_path, render_consolidated_table(report).encode("utf-8"))
    return {
        "cohortCount": report["cohortCount"],
        "strategyRowCount": report["strategyRowCount"],
        "reportPath": str(report_path.resolve()),
        "reportSha256": sha256_file(report_path),
        "tablePath": str(table_path.resolve()),
        "tableSha256": sha256_file(table_path),
    }


def write_report(
    manifest_path: Path, report_path: Path, table_path: Path
) -> dict[str, Any]:
    """Create append-only private JSON and reviewed aggregate Markdown outputs."""

    report = build_report(manifest_path)
    _write_exclusive(report_path, canonical_json_bytes(report))
    _write_exclusive(table_path, render_report_table(report).encode("utf-8"))
    return {
        "reportPath": str(report_path.resolve()),
        "reportSha256": sha256_file(report_path),
        "tablePath": str(table_path.resolve()),
        "tableSha256": sha256_file(table_path),
        "pairedOutcomesByArm": report["pairedOutcomesByArm"],
    }


def parse_job(value: str) -> tuple[str, Path]:
    """Parse an ARM_ID=PATH command-line job binding."""

    name, separator, path = value.partition("=")
    if not separator or re.fullmatch(r"[a-z][a-z0-9-]*", name) is None or not path:
        raise argparse.ArgumentTypeError("job must have the form arm-id=PATH")
    return name, Path(path)


def parse_cohort(value: str) -> tuple[str, Path]:
    """Parse a COHORT_ID=MANIFEST command-line binding."""

    name, separator, path = value.partition("=")
    if not separator or re.fullmatch(r"q\d{3}-q\d{3}", name) is None or not path:
        raise argparse.ArgumentTypeError(
            "cohort must have the form qNNN-qNNN=MANIFEST"
        )
    return name, Path(path)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare", help="Build immutable review packets.")
    prepare.add_argument("--task-root", type=Path, required=True)
    prepare.add_argument("--job", action="append", type=parse_job, required=True)
    prepare.add_argument("--output-dir", type=Path, required=True)
    run = subparsers.add_parser("run", help="Run missing isolated Pi/Luna reviews.")
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--max-workers", type=int, default=2)
    run.add_argument("--pi-executable")
    report = subparsers.add_parser("report", help="Derive the aggregate quality report.")
    report.add_argument("--manifest", type=Path, required=True)
    report.add_argument("--report", type=Path, required=True)
    report.add_argument("--table", type=Path, required=True)
    consolidate = subparsers.add_parser(
        "consolidate", help="Combine cohort reports into one strategy table."
    )
    consolidate.add_argument(
        "--cohort", action="append", type=parse_cohort, required=True
    )
    consolidate.add_argument("--report", type=Path, required=True)
    consolidate.add_argument("--table", type=Path, required=True)
    validate = subparsers.add_parser("validate", help="Validate a prepared or completed review.")
    validate.add_argument("--manifest", type=Path, required=True)
    validate.add_argument("--results", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the solution-agnostic quality-review CLI."""

    args = build_parser().parse_args(argv)
    if args.command == "prepare":
        if len(args.job) < 2:
            raise ReviewError("prepare requires at least two --job bindings")
        outcome = prepare_review(args.task_root, args.job, args.output_dir)
    elif args.command == "run":
        outcome = run_reviews(
            args.manifest,
            max_workers=args.max_workers,
            executable=args.pi_executable,
        )
    elif args.command == "report":
        outcome = write_report(args.manifest, args.report, args.table)
    elif args.command == "consolidate":
        outcome = write_consolidated_report(args.cohort, args.report, args.table)
    else:
        manifest = validate_manifest(args.manifest)
        if args.results:
            report = build_report(args.manifest)
            outcome = {
                "status": "valid",
                "caseCount": len(report["cases"]),
                "reviewCallCount": len(manifest["prompts"]),
            }
        else:
            outcome = {
                "status": "valid",
                "caseCount": len(manifest["cases"]),
                "reviewCallCount": len(manifest["prompts"]),
            }
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
