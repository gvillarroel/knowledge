#!/usr/bin/env python3
"""Run replicated, isolated semantic answer-quality audits with Pi and Luna.

Each model call sees one frozen answer, one self-contained quality contract, and
no competing answers or solution mechanics. Three criterion-order presentations
are majority-adjudicated before component-wise comparison with the cohort's
canonical answer. The workflow is retrospective and never promotes a skill.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Mapping, Sequence

import answer_quality_review as legacy


SCHEMA_VERSION = "isolated-answer-quality-review/2.0"
MANIFEST_VERSION = "isolated-answer-quality-manifest/2.0"
REPORT_VERSION = "isolated-answer-quality-report/2.0"
CONSOLIDATED_VERSION = "isolated-answer-quality-consolidated/2.0"
PROMPT_RENDERER = "single-answer-three-order-majority-v1"
EXPECTED_MODEL = "openai-codex/gpt-5.6-luna"
EXPECTED_THINKING = "high"
REVIEW_PASSES = ("forward", "reverse", "rotate")
REQUIRED_STATUSES = ("satisfied", "partial", "missing", "contradicted")
NEGATIVE_STATUSES = ("respected", "violated")
CORRECTNESS_STATUSES = ("correct", "minor-error", "major-error")
STATUS_RANK = {"contradicted": 0, "missing": 1, "partial": 2, "satisfied": 3}
STATUS_VALUE = {"contradicted": 0.0, "missing": 0.0, "partial": 0.5, "satisfied": 1.0}
NEGATIVE_RANK = {"violated": 0, "respected": 1}
CORRECTNESS_RANK = {"major-error": 0, "minor-error": 1, "correct": 2}
RATIONALE_LIMIT = 360
MAX_INVALID_ATTEMPTS = 3
EXECUTION_POLICY = "capture-invalid-output-and-retry-total-cap-v1"


ReviewError = legacy.ReviewError
canonical_json_bytes = legacy.canonical_json_bytes
sha256_bytes = legacy.sha256_bytes
sha256_file = legacy.sha256_file
load_json = legacy.load_json


def _write_exclusive(path: Path, value: Mapping[str, Any] | str) -> None:
    """Write one append-only UTF-8 artifact."""

    payload = value.encode("utf-8") if isinstance(value, str) else canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise ReviewError(f"Refusing to overwrite append-only artifact: {path}") from exc


def _required_string(value: Any, label: str) -> str:
    return legacy._required_string(value, label)


def _statements(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if allow_empty and (value is None or value == []):
        return []
    return legacy._required_statements(value, label)


def _normalize_text(value: Any, label: str) -> str:
    """Normalize whitespace while retaining every visible semantic token."""

    return " ".join(_required_string(value, label).split())


def project_answer(response: Mapping[str, Any]) -> dict[str, Any]:
    """Project only visible answer prose without deleting citation-like numbers."""

    body = response.get("answer")
    if not isinstance(body, Mapping):
        body = response if any(key in response for key in ("summary", "claims")) else None
    if not isinstance(body, Mapping):
        marker = "No semantic answer content was emitted."
        return {"summary": marker, "claims": [{"ordinal": 1, "statement": marker}]}
    raw_claims = body.get("claims")
    if not isinstance(raw_claims, list) or not raw_claims:
        summary = _normalize_text(body.get("summary"), "answer.summary")
        return {"summary": summary, "claims": [{"ordinal": 1, "statement": summary}]}
    claims: list[dict[str, Any]] = []
    for ordinal, claim in enumerate(raw_claims, 1):
        if not isinstance(claim, Mapping):
            raise ReviewError(f"answer.claims[{ordinal}] must be an object")
        claims.append(
            {
                "ordinal": ordinal,
                "statement": _normalize_text(
                    claim.get("statement"), f"answer.claims[{ordinal}].statement"
                ),
            }
        )
    return {
        "summary": _normalize_text(body.get("summary"), "answer.summary"),
        "claims": claims,
    }


def _job_trial_dirs(job: Path) -> list[Path]:
    return sorted(
        path
        for path in job.iterdir()
        if path.is_dir() and re.fullmatch(r"q\d{3}__[A-Za-z0-9]+", path.name)
    )


def collect_frozen_job(job: Path) -> dict[str, Any]:
    """Collect a complete frozen job and fail on missing native result fields."""

    job = job.resolve()
    lock_path = job / "lock.json"
    lock = load_json(lock_path)
    locked_trials = lock.get("trials")
    if not isinstance(locked_trials, list) or not locked_trials:
        raise ReviewError(f"Job lacks locked trials: {job}")
    trial_dirs = _job_trial_dirs(job)
    if len(trial_dirs) != len(locked_trials):
        raise ReviewError(
            f"Job has {len(trial_dirs)} trial artifacts for {len(locked_trials)} locked trials: {job}"
        )
    answers: dict[str, dict[str, Any]] = {}
    native_rows: list[dict[str, Any]] = []
    observed_contracts: set[tuple[str, str, str]] = set()
    for trial_dir in trial_dirs:
        result = load_json(trial_dir / "result.json")
        if result.get("exception_info") is not None:
            raise ReviewError(f"Errored trial is not answer evidence: {trial_dir}")
        question_id = trial_dir.name.split("__", 1)[0]
        if question_id in answers:
            raise ReviewError(f"Duplicate question in job: {question_id}")
        verifier = result.get("verifier_result")
        rewards = verifier.get("rewards") if isinstance(verifier, Mapping) else None
        agent_result = result.get("agent_result")
        agent_info = result.get("agent_info")
        config = result.get("config")
        agent_config = config.get("agent") if isinstance(config, Mapping) else None
        kwargs = agent_config.get("kwargs") if isinstance(agent_config, Mapping) else None
        model_info = agent_info.get("model_info") if isinstance(agent_info, Mapping) else None
        reward = rewards.get("reward") if isinstance(rewards, Mapping) else None
        input_tokens = agent_result.get("n_input_tokens") if isinstance(agent_result, Mapping) else None
        output_tokens = agent_result.get("n_output_tokens") if isinstance(agent_result, Mapping) else None
        if not isinstance(reward, (int, float)):
            raise ReviewError(f"Completed trial lacks native reward: {trial_dir}")
        if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
            raise ReviewError(f"Completed trial lacks complete token usage: {trial_dir}")
        provider = model_info.get("provider") if isinstance(model_info, Mapping) else None
        model = model_info.get("name") if isinstance(model_info, Mapping) else None
        version = agent_info.get("version") if isinstance(agent_info, Mapping) else None
        thinking = kwargs.get("thinking") if isinstance(kwargs, Mapping) else None
        observed_contracts.add((f"{provider}/{model}", str(version), str(thinking)))
        response = legacy.extract_final_response(trial_dir / "artifacts" / "pi.jsonl")
        projected = project_answer(response)
        answers[question_id] = {
            "taskChecksum": _required_string(
                result.get("task_checksum"), f"{question_id}.task_checksum"
            ),
            "rawAnswerSha256": sha256_bytes(canonical_json_bytes(response)),
            "projectedAnswerSha256": sha256_bytes(canonical_json_bytes(projected)),
            "answer": projected,
        }
        native_rows.append(
            {
                "reward": float(reward),
                "totalTokens": input_tokens + output_tokens,
                "allEvidenceValid": float(rewards.get("all_evidence_valid", 0.0)),
            }
        )
    if observed_contracts != {(EXPECTED_MODEL, "0.84.2", EXPECTED_THINKING)}:
        raise ReviewError(f"Unexpected answer-generation contract in {job}: {observed_contracts}")
    return {
        "jobPath": str(job),
        "jobLockSha256": sha256_file(lock_path),
        "answers": answers,
        "nativeRows": native_rows,
    }


def _record_titles(records_path: Path, expected_ids: Sequence[str]) -> dict[str, str]:
    """Read only record metadata needed to name qrel identities."""

    wanted = set(expected_ids)
    titles: dict[str, str] = {}
    try:
        with records_path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ReviewError(f"Invalid records JSONL line {number}: {records_path}") from exc
                if not isinstance(record, Mapping):
                    continue
                attributes = record.get("attributes")
                candidates = {
                    str(record.get("record_id", "")),
                    str(record.get("source_id", "")),
                }
                if isinstance(attributes, Mapping):
                    candidates.add(str(attributes.get("paper_id", "")))
                matched = wanted.intersection(candidates)
                if matched:
                    title = _required_string(record.get("title"), "record.title")
                    for item in matched:
                        titles[item] = title
                if wanted.issubset(titles):
                    break
    except OSError as exc:
        raise ReviewError(f"Cannot read qrel records: {records_path}") from exc
    missing = wanted.difference(titles)
    if missing:
        raise ReviewError(f"Qrel document titles are missing from records: {sorted(missing)}")
    return titles


def task_contract(task_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build a hard-truth or explicitly qrel-grounded semantic contract."""

    question_path = task_dir / "tests" / "question.json"
    truth_path = task_dir / "tests" / "hard-ground-truth.json"
    records_path = task_dir / "tests" / "records.jsonl"
    question = load_json(question_path)
    rubric = question.get("semantic_rubric")
    if not isinstance(rubric, Mapping):
        raise ReviewError(f"Task lacks semantic rubric: {task_dir}")
    required = _statements(rubric.get("required_points"), "semantic_rubric.required_points")
    required_points = [
        {"criterionId": f"rp-{ordinal:03d}", "criterion": statement}
        for ordinal, statement in enumerate(required, 1)
    ]
    truth = load_json(truth_path) if truth_path.is_file() else None
    expected_sources: list[dict[str, Any]] = []
    if truth is not None:
        if _required_string(truth.get("id"), "truth.id") != _required_string(
            question.get("id"), "question.id"
        ):
            raise ReviewError("Question and hard-ground-truth IDs differ")
        ground_truth = truth.get("ground_truth")
        if not isinstance(ground_truth, Mapping):
            raise ReviewError("Hard ground truth lacks ground_truth")
        reference_statements = _statements(
            ground_truth.get("answer_claims"), "ground_truth.answer_claims"
        )
        negative_statements = _statements(
            ground_truth.get("important_negatives"), "ground_truth.important_negatives"
        )
        basis = "semantic-rubric-plus-hard-ground-truth"
        strength = "hard-ground-truth"
    else:
        qrels = question.get("qrels")
        document_ids = qrels.get("document_ids") if isinstance(qrels, Mapping) else None
        if not isinstance(document_ids, list) or not document_ids:
            raise ReviewError(f"Rubric-only task lacks qrel identities: {task_dir}")
        document_ids = [
            _required_string(item, f"qrels.document_ids[{ordinal}]")
            for ordinal, item in enumerate(document_ids, 1)
        ]
        titles = _record_titles(records_path, document_ids)
        expected_sources = [
            {
                "sourceId": f"src-{ordinal:03d}",
                "documentId": document_id,
                "title": titles[document_id],
            }
            for ordinal, document_id in enumerate(document_ids, 1)
        ]
        # A qrel identifies the intended evidence neighborhood, but it is not
        # itself an answer claim. Keep those identities in expectedSources and
        # use the frozen semantic rubric as the explicit content contract.
        # This avoids grading an answer on whether it recites storage-facing
        # document identifiers or titles.
        reference_statements = list(required)
        raw_negatives = rubric.get("important_negatives", question.get("important_negatives"))
        negative_statements = _statements(
            raw_negatives, "semantic_rubric.important_negatives", allow_empty=True
        )
        basis = "semantic-rubric-plus-qrel-identities"
        strength = "qrel-grounded-rubric"
    contract = {
        "schemaVersion": SCHEMA_VERSION,
        "contractBasis": basis,
        "contractStrength": strength,
        "question": _required_string(question.get("question"), "question.question"),
        "requiredPoints": required_points,
        "referenceClaims": [
            {"claimId": f"ref-{ordinal:03d}", "statement": statement}
            for ordinal, statement in enumerate(reference_statements, 1)
        ],
        "importantNegatives": [
            {"negativeId": f"neg-{ordinal:03d}", "statement": statement}
            for ordinal, statement in enumerate(negative_statements, 1)
        ],
        "expectedSources": expected_sources,
        "qrelScope": (
            question.get("evaluation_policy", {}).get("qrel_scope")
            if isinstance(question.get("evaluation_policy"), Mapping)
            else None
        ),
    }
    bindings = {
        "questionSha256": sha256_file(question_path),
        "recordsSha256": sha256_file(records_path),
        "groundTruthSha256": sha256_file(truth_path) if truth is not None else None,
        "contractSha256": sha256_bytes(canonical_json_bytes(contract)),
        "contractBasis": basis,
        "contractStrength": strength,
    }
    return contract, bindings


def _rotate(values: Sequence[Any]) -> list[Any]:
    if len(values) < 2:
        return list(values)
    return list(values[1:]) + [values[0]]


def ordered_contract(contract: Mapping[str, Any], review_pass: str) -> dict[str, Any]:
    """Present identical criteria in three deterministic orders."""

    if review_pass not in REVIEW_PASSES:
        raise ReviewError(f"Unknown review pass: {review_pass}")
    result = dict(contract)
    for key in ("requiredPoints", "referenceClaims", "importantNegatives", "expectedSources"):
        values = list(contract.get(key, []))
        if review_pass == "reverse":
            values.reverse()
        elif review_pass == "rotate":
            values = _rotate(values)
        result[key] = values
    return result


def _criterion_to_assertion(statement: str) -> str:
    """Turn common rubric instructions into declarative calibration prose."""

    text = statement.strip()
    explain = re.match(r"^Explain that\s+(.+)$", text, flags=re.IGNORECASE)
    if explain:
        body = explain.group(1)
        return body[:1].upper() + body[1:]
    describe = re.match(r"^(?:Identify|Describe)\s+(.+)$", text, flags=re.IGNORECASE)
    if describe:
        body = describe.group(1)
        if " as " in body:
            subject, predicate = body.split(" as ", 1)
            return f"{subject[:1].upper() + subject[1:]} is {predicate}"
        return f"The following description holds: {body}"
    negative = re.match(r"^Do not\s+(.+)$", text, flags=re.IGNORECASE)
    if negative:
        return f"It is invalid to {negative.group(1)}"
    return text


def positive_control(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Build a complete contract-backed positive calibration answer."""

    if contract.get("contractStrength") != "hard-ground-truth":
        raise ReviewError("Positive calibration requires hard ground truth")
    statements = [
        _criterion_to_assertion(str(item["criterion"]))
        for item in contract["requiredPoints"]
    ]
    statements.extend(str(item["statement"]) for item in contract["referenceClaims"])
    statements.extend(
        _criterion_to_assertion(str(item["statement"]))
        for item in contract["importantNegatives"]
    )
    statements = list(dict.fromkeys(statements))
    return {
        "summary": " ".join(statements),
        "claims": [
            {"ordinal": ordinal, "statement": statement}
            for ordinal, statement in enumerate(statements, 1)
        ],
    }


def negative_control() -> dict[str, Any]:
    marker = "No semantic answer content was emitted."
    return {"summary": marker, "claims": [{"ordinal": 1, "statement": marker}]}


def review_packet(
    contract: Mapping[str, Any], response: Mapping[str, Any], review_pass: str
) -> dict[str, Any]:
    """Build one single-answer reviewer packet."""

    return {
        "schemaVersion": SCHEMA_VERSION,
        "reviewPass": review_pass,
        "qualityContract": ordered_contract(contract, review_pass),
        "response": dict(response),
    }


def render_prompt(packet: Mapping[str, Any]) -> str:
    """Render an isolated review prompt with privately auditable rationales."""

    contract = packet["qualityContract"]
    packet_sha = sha256_bytes(canonical_json_bytes(packet))
    output_shape = {
        "schemaVersion": SCHEMA_VERSION,
        "packetSha256": packet_sha,
        "requiredPointJudgments": [
            {
                "criterionId": item["criterionId"],
                "status": "satisfied-or-partial-or-missing-or-contradicted",
                "rationale": "brief contract-grounded reason",
                "claimOrdinals": [],
            }
            for item in contract["requiredPoints"]
        ],
        "importantNegativeJudgments": [
            {
                "negativeId": item["negativeId"],
                "status": "respected-or-violated",
                "rationale": "brief contract-grounded reason",
                "claimOrdinals": [],
            }
            for item in contract["importantNegatives"]
        ],
        "materialCorrectness": {
            "status": "correct-or-minor-error-or-major-error",
            "rationale": "brief reason",
        },
    }
    return f"""You are an independent semantic answer-quality reviewer.

Evaluate exactly one anonymized response. No competing response is present. Use only the frozen contract and response below; do not use tools or outside knowledge. Ignore style, length, citation markers, and presumed retrieval strategy.

Rules:
- Treat required points and reference claims as authoritative semantic targets.
- Expected sources are minimum attribution anchors, not an exhaustive source list.
- Judge every criterion independently; improvement on one criterion cannot compensate for loss on another.
- `satisfied` means the full point is explicit and correct; `partial` means materially incomplete or imprecise; `missing` means not established; `contradicted` means materially conflicting.
- A scope conflation, false attribution, adjacent-result substitution, or wrong numerical target is a `major-error`; a bounded imprecision is a `minor-error`.
- Give a short private rationale and list only response claim ordinals that support the judgment. Do not invent claim ordinals.
- Return the judgments in the exact order shown below even though criterion presentation order intentionally varies across independent passes.

Return exactly one JSON object, without a markdown fence, matching this shape:
{json.dumps(output_shape, ensure_ascii=False, indent=2)}

Frozen single-answer packet:
{json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True)}
"""


def _validate_rationale(value: Any, label: str) -> str:
    text = _required_string(value, label)
    if len(text) > RATIONALE_LIMIT:
        raise ReviewError(f"{label} exceeds {RATIONALE_LIMIT} characters")
    return text


def _validate_claim_ordinals(value: Any, claim_count: int, label: str) -> list[int]:
    if not isinstance(value, list) or any(not isinstance(item, int) for item in value):
        raise ReviewError(f"{label} must be an integer array")
    if len(value) != len(set(value)) or any(item < 1 or item > claim_count for item in value):
        raise ReviewError(f"{label} contains invalid or duplicate claim ordinals")
    return list(value)


def validate_judgment(result: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one isolated judgment against exact criterion identifiers."""

    if set(result) != {
        "schemaVersion",
        "packetSha256",
        "requiredPointJudgments",
        "importantNegativeJudgments",
        "materialCorrectness",
    }:
        raise ReviewError("Isolated judgment has missing or unknown top-level keys")
    if result.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewError("Isolated judgment schema mismatch")
    expected_sha = sha256_bytes(canonical_json_bytes(packet))
    contract = packet["qualityContract"]
    claim_count = len(packet["response"]["claims"])
    normalized_required: list[dict[str, Any]] = []
    raw_required = result.get("requiredPointJudgments")
    expected_required = [str(item["criterionId"]) for item in contract["requiredPoints"]]
    if not isinstance(raw_required, list) or len(raw_required) != len(expected_required):
        raise ReviewError("Required-point judgment count mismatch")
    for expected_id, item in zip(expected_required, raw_required, strict=True):
        if not isinstance(item, Mapping) or set(item) != {
            "criterionId",
            "status",
            "rationale",
            "claimOrdinals",
        }:
            raise ReviewError("Required-point judgment shape mismatch")
        if item.get("criterionId") != expected_id or item.get("status") not in REQUIRED_STATUSES:
            raise ReviewError("Required-point judgment identifier or status mismatch")
        normalized_required.append(
            {
                "criterionId": expected_id,
                "status": str(item["status"]),
                "rationale": _validate_rationale(item.get("rationale"), "required rationale"),
                "claimOrdinals": _validate_claim_ordinals(
                    item.get("claimOrdinals"), claim_count, "required claimOrdinals"
                ),
            }
        )
    normalized_negatives: list[dict[str, Any]] = []
    raw_negatives = result.get("importantNegativeJudgments")
    expected_negatives = [str(item["negativeId"]) for item in contract["importantNegatives"]]
    if not isinstance(raw_negatives, list) or len(raw_negatives) != len(expected_negatives):
        raise ReviewError("Important-negative judgment count mismatch")
    for expected_id, item in zip(expected_negatives, raw_negatives, strict=True):
        if not isinstance(item, Mapping) or set(item) != {
            "negativeId",
            "status",
            "rationale",
            "claimOrdinals",
        }:
            raise ReviewError("Important-negative judgment shape mismatch")
        if item.get("negativeId") != expected_id or item.get("status") not in NEGATIVE_STATUSES:
            raise ReviewError("Important-negative identifier or status mismatch")
        normalized_negatives.append(
            {
                "negativeId": expected_id,
                "status": str(item["status"]),
                "rationale": _validate_rationale(item.get("rationale"), "negative rationale"),
                "claimOrdinals": _validate_claim_ordinals(
                    item.get("claimOrdinals"), claim_count, "negative claimOrdinals"
                ),
            }
        )
    correctness = result.get("materialCorrectness")
    if not isinstance(correctness, Mapping) or set(correctness) != {"status", "rationale"}:
        raise ReviewError("Material-correctness judgment shape mismatch")
    if correctness.get("status") not in CORRECTNESS_STATUSES:
        raise ReviewError("Material-correctness status mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "packetSha256": expected_sha,
        "requiredPointJudgments": normalized_required,
        "importantNegativeJudgments": normalized_negatives,
        "materialCorrectness": {
            "status": str(correctness["status"]),
            "rationale": _validate_rationale(correctness.get("rationale"), "correctness rationale"),
        },
    }


def _native_report_index(path: Path) -> tuple[dict[str, Any], str]:
    report = load_json(path)
    comparison = report.get("comparison")
    if not isinstance(comparison, Mapping) or comparison.get("fairnessBasis") != "lock-and-trial-results":
        raise ReviewError(f"Native comparison lacks lock-and-trial-results fairness: {path}")
    jobs = report.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ReviewError(f"Native comparison lacks jobs: {path}")
    index: dict[str, Any] = {}
    for job in jobs:
        if not isinstance(job, Mapping) or job.get("complete") is not True:
            raise ReviewError(f"Native comparison contains an incomplete job: {path}")
        index[str(Path(str(job["jobDirectory"])).resolve())] = job
    return index, sha256_file(path)


def _native_metrics(job: Mapping[str, Any]) -> dict[str, Any]:
    summary = job["summary"]
    return {
        "meanNativeReward": summary["reward"]["average"],
        "meanAgentTokens": summary["totalTokens"]["average"],
        "meanCostUsd": summary["costUsd"]["average"],
        "meanAgentLatencyMs": summary["agentLatencyMs"]["average"],
        "trialCount": summary["completedTrials"],
        "evidenceValidCaseCount": sum(
            float(trial["rewards"].get("all_evidence_valid", 0.0)) >= 1.0
            for trial in job["trials"]
        ),
    }


def _fallback_native_metrics(collected: Mapping[str, Any]) -> dict[str, Any]:
    rows = collected["nativeRows"]
    return {
        "meanNativeReward": sum(row["reward"] for row in rows) / len(rows),
        "meanAgentTokens": sum(row["totalTokens"] for row in rows) / len(rows),
        "meanCostUsd": None,
        "meanAgentLatencyMs": None,
        "trialCount": len(rows),
        "evidenceValidCaseCount": sum(row["allEvidenceValid"] >= 1.0 for row in rows),
    }


def prepare_audit(
    task_root: Path,
    jobs: Sequence[tuple[str, Path]],
    native_report_path: Path,
    output_dir: Path,
    *,
    trial_results_only_arms: Sequence[str] = (),
) -> dict[str, Any]:
    """Prepare complete arm bindings and isolated three-pass prompts."""

    arm_ids = [name for name, _ in jobs]
    if len(jobs) < 2 or len(set(arm_ids)) != len(arm_ids):
        raise ReviewError("At least two distinctly named jobs are required")
    allowed_fallback = set(trial_results_only_arms)
    if not allowed_fallback.issubset(arm_ids):
        raise ReviewError("Unknown trial-results-only arm")
    native_index, native_report_sha = _native_report_index(native_report_path.resolve())
    collected = [
        (arm_id, path.resolve(), collect_frozen_job(path.resolve())) for arm_id, path in jobs
    ]
    question_ids = sorted(collected[0][2]["answers"])
    baseline_checksums = {
        question_id: collected[0][2]["answers"][question_id]["taskChecksum"]
        for question_id in question_ids
    }
    for arm_id, _, job_data in collected[1:]:
        if sorted(job_data["answers"]) != question_ids:
            raise ReviewError(f"Question-set drift for arm {arm_id}")
        for question_id in question_ids:
            if job_data["answers"][question_id]["taskChecksum"] != baseline_checksums[question_id]:
                raise ReviewError(f"Task checksum drift for {arm_id}/{question_id}")
    arms: list[dict[str, Any]] = []
    for arm_id, path, job_data in collected:
        native_job = native_index.get(str(path))
        if native_job is None and arm_id not in allowed_fallback:
            raise ReviewError(f"Arm is absent from native lock-comparable report: {arm_id}")
        arms.append(
            {
                "armId": arm_id,
                "jobPath": str(path),
                "jobLockSha256": job_data["jobLockSha256"],
                "nativeReportPath": str(native_report_path.resolve()),
                "nativeReportSha256": native_report_sha,
                "nativeFairnessBasis": (
                    "lock-and-trial-results"
                    if native_job is not None
                    else "trial-results-with-documented-environment-wrapper-drift"
                ),
                "nativeMetrics": (
                    _native_metrics(native_job)
                    if native_job is not None
                    else _fallback_native_metrics(job_data)
                ),
            }
        )
    manifest: dict[str, Any] = {
        "schemaVersion": MANIFEST_VERSION,
        "reviewSchemaVersion": SCHEMA_VERSION,
        "promptRenderer": PROMPT_RENDERER,
        "model": EXPECTED_MODEL,
        "thinking": EXPECTED_THINKING,
        "promotionEligible": False,
        "method": {
            "answersPerCall": 1,
            "replicatesPerSubject": 3,
            "criterionOrders": list(REVIEW_PASSES),
            "consensus": "per-cell-majority-with-unresolved-state",
            "comparison": "component-wise-no-compensation",
            "answerEvidenceVisible": False,
            "retrievalTraceVisible": False,
            "strategyIdentityVisible": False,
            "jobIdentityVisible": False,
            "mechanicalRewardVisible": False,
            "tokenUsageVisible": False,
            "invalidOutputPolicy": EXECUTION_POLICY,
            "maximumInvalidAttemptsPerPrompt": MAX_INVALID_ATTEMPTS,
            "validResultReusePolicy": "exact-packet-and-prompt-digests-only",
            "packetBindingAuthority": "runner-prompt-process-association",
            "modelPacketDigestEcho": "diagnostic-only",
            "packetEchoMismatchPolicy": "accept-normalize-and-record",
        },
        "reviewerScriptSha256": sha256_file(Path(__file__).resolve()),
        "taskRoot": str(task_root.resolve()),
        "arms": arms,
        "cases": [],
        "prompts": [],
    }
    for case_ordinal, question_id in enumerate(question_ids, 1):
        contract, bindings = task_contract(task_root / question_id)
        answer_bindings = {
            arm_id: {
                "rawAnswerSha256": job_data["answers"][question_id]["rawAnswerSha256"],
                "projectedAnswerSha256": job_data["answers"][question_id][
                    "projectedAnswerSha256"
                ],
            }
            for arm_id, _, job_data in collected
        }
        controls = ["empty-answer-negative"]
        if contract["contractStrength"] == "hard-ground-truth":
            controls.append("contract-derived-positive")
        manifest["cases"].append(
            {
                "ordinal": case_ordinal,
                "questionId": question_id,
                "taskChecksum": baseline_checksums[question_id],
                **bindings,
                "answers": answer_bindings,
                "controls": controls,
            }
        )
        subjects = [
            ("arm", arm_id, job_data["answers"][question_id]["answer"])
            for arm_id, _, job_data in collected
        ]
        subjects.append(("control", "empty-answer-negative", negative_control()))
        if contract["contractStrength"] == "hard-ground-truth":
            subjects.append(
                ("control", "contract-derived-positive", positive_control(contract))
            )
        for subject_kind, subject_id, response in subjects:
            response_sha = sha256_bytes(canonical_json_bytes(response))
            for review_pass in REVIEW_PASSES:
                packet = review_packet(contract, response, review_pass)
                prompt = render_prompt(packet)
                stem = f"case-{case_ordinal:03d}-{subject_kind}-{subject_id}-{review_pass}"
                packet_path = output_dir / "packets" / f"{stem}.json"
                prompt_path = output_dir / "prompts" / f"{stem}.md"
                _write_exclusive(packet_path, packet)
                _write_exclusive(prompt_path, prompt)
                manifest["prompts"].append(
                    {
                        "caseOrdinal": case_ordinal,
                        "subjectKind": subject_kind,
                        "subjectId": subject_id,
                        "responseSha256": response_sha,
                        "reviewPass": review_pass,
                        "packetPath": packet_path.relative_to(output_dir).as_posix(),
                        "packetSha256": sha256_file(packet_path),
                        "promptPath": prompt_path.relative_to(output_dir).as_posix(),
                        "promptSha256": sha256_file(prompt_path),
                        "resultPath": f"results/{stem}.json",
                        "rawResultPath": f"raw/{stem}.txt",
                    }
                )
    manifest_path = output_dir / "manifest.json"
    _write_exclusive(manifest_path, manifest)
    return {
        "manifestPath": str(manifest_path.resolve()),
        "manifestSha256": sha256_file(manifest_path),
        "caseCount": len(manifest["cases"]),
        "armCount": len(arms),
        "reviewCallCount": len(manifest["prompts"]),
    }


def validate_manifest(manifest_path: Path, *, source_bindings: bool = True) -> dict[str, Any]:
    """Validate all prompt, packet, job, task, answer, and native-report bindings."""

    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != MANIFEST_VERSION:
        raise ReviewError("Isolated audit manifest schema mismatch")
    if manifest.get("promptRenderer") != PROMPT_RENDERER:
        raise ReviewError("Isolated audit prompt renderer mismatch")
    if manifest.get("model") != EXPECTED_MODEL or manifest.get("thinking") != EXPECTED_THINKING:
        raise ReviewError("Isolated audit is not pinned to Luna/high")
    if manifest.get("promotionEligible") is not False:
        raise ReviewError("Retrospective audit cannot be promotion eligible")
    method = manifest.get("method")
    if not isinstance(method, Mapping):
        raise ReviewError("Isolated audit method is missing")
    if method.get("invalidOutputPolicy") != EXECUTION_POLICY:
        raise ReviewError("Isolated audit invalid-output policy mismatch")
    if method.get("maximumInvalidAttemptsPerPrompt") != MAX_INVALID_ATTEMPTS:
        raise ReviewError("Isolated audit invalid-attempt cap mismatch")
    if method.get("validResultReusePolicy") != "exact-packet-and-prompt-digests-only":
        raise ReviewError("Isolated audit result-reuse policy mismatch")
    if method.get("packetBindingAuthority") != "runner-prompt-process-association":
        raise ReviewError("Isolated audit packet-binding authority mismatch")
    if method.get("modelPacketDigestEcho") != "diagnostic-only":
        raise ReviewError("Isolated audit model digest-echo policy mismatch")
    if method.get("packetEchoMismatchPolicy") != "accept-normalize-and-record":
        raise ReviewError("Isolated audit packet echo-mismatch policy mismatch")
    if manifest.get("reviewerScriptSha256") != sha256_file(Path(__file__).resolve()):
        raise ReviewError("Isolated audit reviewer implementation drift")
    arms = manifest.get("arms")
    cases = manifest.get("cases")
    prompts = manifest.get("prompts")
    if not isinstance(arms, list) or len(arms) < 2:
        raise ReviewError("Isolated audit lacks arms")
    arm_ids = [str(item.get("armId")) for item in arms if isinstance(item, Mapping)]
    if len(arm_ids) != len(arms) or len(set(arm_ids)) != len(arm_ids):
        raise ReviewError("Isolated audit arm identifiers are invalid")
    if not isinstance(cases, list) or not cases or not isinstance(prompts, list):
        raise ReviewError("Isolated audit lacks cases or prompts")
    root = manifest_path.parent
    seen: set[tuple[int, str, str, str]] = set()
    for item in prompts:
        if not isinstance(item, Mapping):
            raise ReviewError("Prompt entry must be an object")
        key = (
            int(item.get("caseOrdinal", 0)),
            str(item.get("subjectKind")),
            str(item.get("subjectId")),
            str(item.get("reviewPass")),
        )
        if key in seen or key[3] not in REVIEW_PASSES:
            raise ReviewError("Prompt subject/pass is invalid or duplicated")
        seen.add(key)
        packet_path = root / _required_string(item.get("packetPath"), "packetPath")
        prompt_path = root / _required_string(item.get("promptPath"), "promptPath")
        if sha256_file(packet_path) != item.get("packetSha256"):
            raise ReviewError(f"Packet digest drift: {packet_path}")
        if sha256_file(prompt_path) != item.get("promptSha256"):
            raise ReviewError(f"Prompt digest drift: {prompt_path}")
        packet = load_json(packet_path)
        if sha256_bytes(canonical_json_bytes(packet["response"])) != item.get(
            "responseSha256"
        ):
            raise ReviewError(f"Prompt response binding drift: {packet_path}")
        if prompt_path.read_text(encoding="utf-8") != render_prompt(packet):
            raise ReviewError(f"Prompt rendering drift: {prompt_path}")
    expected_prompt_count = sum(
        (len(arms) + len(case.get("controls", []))) * len(REVIEW_PASSES)
        for case in cases
    )
    if len(prompts) != expected_prompt_count:
        raise ReviewError("Isolated audit prompt count mismatch")
    if source_bindings:
        task_root = Path(_required_string(manifest.get("taskRoot"), "taskRoot"))
        by_arm = {str(item["armId"]): item for item in arms}
        recollected = {
            arm_id: collect_frozen_job(Path(str(item["jobPath"])))
            for arm_id, item in by_arm.items()
        }
        for arm_id, item in by_arm.items():
            if recollected[arm_id]["jobLockSha256"] != item.get("jobLockSha256"):
                raise ReviewError(f"Job lock drift for arm {arm_id}")
            report_path = Path(str(item["nativeReportPath"]))
            if sha256_file(report_path) != item.get("nativeReportSha256"):
                raise ReviewError(f"Native report drift for arm {arm_id}")
        for case in cases:
            question_id = str(case["questionId"])
            contract, bindings = task_contract(task_root / question_id)
            for key in (
                "questionSha256",
                "recordsSha256",
                "groundTruthSha256",
                "contractSha256",
                "contractBasis",
                "contractStrength",
            ):
                if case.get(key) != bindings.get(key):
                    raise ReviewError(f"Task contract binding drift for {question_id}/{key}")
            for arm_id in arm_ids:
                source = recollected[arm_id]["answers"].get(question_id)
                expected = case["answers"].get(arm_id)
                if source is None or not isinstance(expected, Mapping):
                    raise ReviewError(f"Missing answer binding for {arm_id}/{question_id}")
                for key in ("rawAnswerSha256", "projectedAnswerSha256"):
                    if source[key] != expected.get(key):
                        raise ReviewError(f"Answer binding drift for {arm_id}/{question_id}/{key}")
                if source["taskChecksum"] != case.get("taskChecksum"):
                    raise ReviewError(f"Task checksum drift for {arm_id}/{question_id}")
            del contract
    return manifest


def _decode_result(text: str, label: str) -> dict[str, Any]:
    return legacy._decode_json_object(text, label)


def _run_one(
    executable: str, root: Path, item: Mapping[str, Any]
) -> dict[str, Any]:
    packet_path = root / str(item["packetPath"])
    prompt_path = root / str(item["promptPath"])
    result_path = root / str(item["resultPath"])
    raw_path = root / str(item["rawResultPath"])
    packet = load_json(packet_path)
    if result_path.is_file():
        validate_judgment(load_json(result_path), packet)
        return {"status": "reused", "resultPath": str(result_path)}
    if result_path.exists() or raw_path.exists():
        raise ReviewError(f"Incomplete append-only result target: {result_path}")
    invalid_dir = root / "invalid"
    prior_attempts = sorted(invalid_dir.glob(f"{result_path.stem}-attempt-*.json"))
    if len(prior_attempts) >= MAX_INVALID_ATTEMPTS:
        raise ReviewError(f"Invalid-attempt cap already exhausted: {prompt_path.name}")
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
    for attempt in range(len(prior_attempts) + 1, MAX_INVALID_ATTEMPTS + 1):
        completed = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=900,
            check=False,
        )
        validated: dict[str, Any] | None = None
        decoded: dict[str, Any] | None = None
        error: str | None = None
        if completed.returncode != 0:
            error = f"Pi exited with {completed.returncode}"
        else:
            try:
                decoded = _decode_result(
                    completed.stdout, f"Pi output for {prompt_path.name}"
                )
                validated = validate_judgment(decoded, packet)
            except ReviewError as exc:
                error = f"{type(exc).__name__}: {exc}"
        if error is None and validated is not None and decoded is not None:
            expected_packet_sha = sha256_bytes(canonical_json_bytes(packet))
            decoded_packet_sha = decoded.get("packetSha256")
            echo_mismatch = decoded_packet_sha != expected_packet_sha
            if echo_mismatch:
                warning_path = root / "warnings" / f"{result_path.stem}.json"
                _write_exclusive(
                    warning_path,
                    {
                        "schemaVersion": "isolated-answer-quality-warning/1.0",
                        "warning": "model-packet-digest-echo-mismatch",
                        "bindingAuthority": "runner-prompt-process-association",
                        "promptPath": item["promptPath"],
                        "promptSha256": item["promptSha256"],
                        "expectedPacketSha256": expected_packet_sha,
                        "modelReportedPacketSha256": decoded_packet_sha,
                    },
                )
            _write_exclusive(raw_path, completed.stdout)
            _write_exclusive(result_path, validated)
            return {
                "status": "created",
                "resultPath": str(result_path),
                "invalidAttemptsBeforeSuccess": attempt - 1,
                "packetEchoMismatch": echo_mismatch,
            }
        invalid_raw = invalid_dir / f"{result_path.stem}-attempt-{attempt:02d}.txt"
        invalid_receipt = invalid_dir / f"{result_path.stem}-attempt-{attempt:02d}.json"
        _write_exclusive(invalid_raw, completed.stdout)
        _write_exclusive(
            invalid_receipt,
            {
                "schemaVersion": "isolated-answer-quality-invalid-attempt/1.0",
                "executionPolicy": EXECUTION_POLICY,
                "attempt": attempt,
                "promptPath": item["promptPath"],
                "promptSha256": item["promptSha256"],
                "packetSha256": item["packetSha256"],
                "returnCode": completed.returncode,
                "error": error,
                "stdoutPath": invalid_raw.relative_to(root).as_posix(),
                "stdoutSha256": sha256_file(invalid_raw),
                "stderrTail": completed.stderr.strip().replace("\n", " ")[-800:],
            },
        )
    raise ReviewError(f"Invalid-attempt cap exhausted: {prompt_path.name}")


def run_reviews(
    manifest_path: Path, *, max_workers: int = 4, executable: str | None = None
) -> dict[str, Any]:
    """Run every missing isolated review call."""

    if max_workers < 1 or max_workers > 4:
        raise ReviewError("max_workers must be between 1 and 4")
    manifest = validate_manifest(manifest_path)
    selected = executable or shutil.which("pi")
    if selected is None:
        raise ReviewError("Cannot find the pi executable")
    outcomes: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_run_one, selected, manifest_path.parent, item): item
            for item in manifest["prompts"]
        }
        failures: list[str] = []
        for future in as_completed(futures):
            try:
                outcomes.append(future.result())
            except Exception as exc:  # noqa: BLE001 - aggregate all bounded calls
                item = futures[future]
                failures.append(f"{item['promptPath']}: {type(exc).__name__}: {exc}")
    if failures:
        raise ReviewError(
            f"{len(failures)} isolated review prompts failed after bounded attempts: "
            + " | ".join(failures)
        )
    counts = Counter(item["status"] for item in outcomes)
    return {
        "status": "complete",
        "reviewCallCount": len(outcomes),
        "created": counts["created"],
        "reused": counts["reused"],
        "model": EXPECTED_MODEL,
        "thinking": EXPECTED_THINKING,
        "invalidAttemptCount": sum(
            int(item.get("invalidAttemptsBeforeSuccess", 0)) for item in outcomes
        ),
        "packetEchoMismatchCount": sum(
            bool(item.get("packetEchoMismatch")) for item in outcomes
        ),
    }


def import_valid_results(source_manifest_path: Path, target_manifest_path: Path) -> dict[str, Any]:
    """Reuse only fully validated results for byte-identical prompts and packets."""

    source_manifest = load_json(source_manifest_path)
    target_manifest = validate_manifest(target_manifest_path)
    source_root = source_manifest_path.parent
    target_root = target_manifest_path.parent
    source_prompts = {
        (
            int(item["caseOrdinal"]),
            str(item["subjectKind"]),
            str(item["subjectId"]),
            str(item["reviewPass"]),
        ): item
        for item in source_manifest.get("prompts", [])
    }
    imported: list[dict[str, Any]] = []
    for target in target_manifest["prompts"]:
        key = (
            int(target["caseOrdinal"]),
            str(target["subjectKind"]),
            str(target["subjectId"]),
            str(target["reviewPass"]),
        )
        source = source_prompts.get(key)
        if source is None:
            continue
        if source.get("packetSha256") != target.get("packetSha256") or source.get(
            "promptSha256"
        ) != target.get("promptSha256"):
            continue
        source_result = source_root / str(source["resultPath"])
        source_raw = source_root / str(source["rawResultPath"])
        if not source_result.is_file() or not source_raw.is_file():
            continue
        target_result = target_root / str(target["resultPath"])
        target_raw = target_root / str(target["rawResultPath"])
        if target_result.exists() or target_raw.exists():
            raise ReviewError(f"Target result already exists during import: {target_result}")
        packet = load_json(target_root / str(target["packetPath"]))
        normalized = validate_judgment(load_json(source_result), packet)
        raw_text = source_raw.read_text(encoding="utf-8")
        raw_normalized = validate_judgment(
            _decode_result(raw_text, f"imported raw result {source_raw}"), packet
        )
        if canonical_json_bytes(raw_normalized) != canonical_json_bytes(normalized):
            raise ReviewError(f"Imported raw/result semantic drift: {source_result}")
        _write_exclusive(target_raw, raw_text)
        _write_exclusive(target_result, normalized)
        imported.append(
            {
                "key": list(key),
                "sourceResultSha256": sha256_file(source_result),
                "targetResultSha256": sha256_file(target_result),
                "sourceRawSha256": sha256_file(source_raw),
                "targetRawSha256": sha256_file(target_raw),
            }
        )
    receipt_path = target_root / "import-receipt.json"
    _write_exclusive(
        receipt_path,
        {
            "schemaVersion": "isolated-answer-quality-import-receipt/1.0",
            "policy": "exact-packet-and-prompt-digests-only",
            "sourceManifestPath": str(source_manifest_path.resolve()),
            "sourceManifestSha256": sha256_file(source_manifest_path),
            "targetManifestSha256": sha256_file(target_manifest_path),
            "importedResultCount": len(imported),
            "imports": imported,
        },
    )
    return {
        "importedResultCount": len(imported),
        "receiptPath": str(receipt_path.resolve()),
        "receiptSha256": sha256_file(receipt_path),
    }


def _majority(values: Sequence[str]) -> tuple[str, bool, bool]:
    """Return value, resolved flag, and unanimous flag for three observations."""

    if len(values) != 3:
        raise ReviewError("Majority consensus requires exactly three observations")
    counts = Counter(values)
    value, count = counts.most_common(1)[0]
    return (value if count >= 2 else "unresolved", count >= 2, count == 3)


def majority_consensus(judgments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Derive per-cell majority consensus without synthetic worst-case merging."""

    if len(judgments) != 3:
        raise ReviewError("Consensus requires three isolated judgments")
    required_ids = [item["criterionId"] for item in judgments[0]["requiredPointJudgments"]]
    negative_ids = [item["negativeId"] for item in judgments[0]["importantNegativeJudgments"]]
    required_by_judgment = [
        {item["criterionId"]: item for item in judgment["requiredPointJudgments"]}
        for judgment in judgments
    ]
    negative_by_judgment = [
        {item["negativeId"]: item for item in judgment["importantNegativeJudgments"]}
        for judgment in judgments
    ]
    consensus_required: list[dict[str, Any]] = []
    consensus_negatives: list[dict[str, Any]] = []
    unanimous_cells = 0
    resolved_cells = 0
    for criterion_id in required_ids:
        rows = [mapping[criterion_id] for mapping in required_by_judgment]
        value, resolved, unanimous = _majority([str(row["status"]) for row in rows])
        resolved_cells += resolved
        unanimous_cells += unanimous
        consensus_required.append(
            {
                "criterionId": criterion_id,
                "status": value,
                "rationales": [str(row["rationale"]) for row in rows],
                "claimOrdinals": sorted(
                    {ordinal for row in rows for ordinal in row["claimOrdinals"]}
                ),
                "unanimous": unanimous,
            }
        )
    for negative_id in negative_ids:
        rows = [mapping[negative_id] for mapping in negative_by_judgment]
        value, resolved, unanimous = _majority([str(row["status"]) for row in rows])
        resolved_cells += resolved
        unanimous_cells += unanimous
        consensus_negatives.append(
            {
                "negativeId": negative_id,
                "status": value,
                "rationales": [str(row["rationale"]) for row in rows],
                "claimOrdinals": sorted(
                    {ordinal for row in rows for ordinal in row["claimOrdinals"]}
                ),
                "unanimous": unanimous,
            }
        )
    correctness_rows = [judgment["materialCorrectness"] for judgment in judgments]
    correctness, resolved, unanimous = _majority(
        [str(row["status"]) for row in correctness_rows]
    )
    resolved_cells += resolved
    unanimous_cells += unanimous
    total_cells = len(consensus_required) + len(consensus_negatives) + 1
    unresolved = any(item["status"] == "unresolved" for item in consensus_required)
    unresolved = unresolved or any(
        item["status"] == "unresolved" for item in consensus_negatives
    ) or correctness == "unresolved"
    coverage = (
        None
        if unresolved
        else sum(STATUS_VALUE[item["status"]] for item in consensus_required)
        / len(consensus_required)
    )
    return {
        "requiredPointJudgments": consensus_required,
        "importantNegativeJudgments": consensus_negatives,
        "materialCorrectness": {
            "status": correctness,
            "rationales": [str(row["rationale"]) for row in correctness_rows],
            "unanimous": unanimous,
        },
        "unresolved": unresolved,
        "requiredPointCoverage": round(coverage, 6) if coverage is not None else None,
        "casePass": (
            not unresolved
            and all(item["status"] == "satisfied" for item in consensus_required)
            and all(item["status"] == "respected" for item in consensus_negatives)
            and correctness == "correct"
        ),
        "unanimousCellCount": unanimous_cells,
        "resolvedCellCount": resolved_cells,
        "judgmentCellCount": total_cells,
    }


def component_outcome(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any]
) -> str:
    """Compare every semantic component without within-case compensation."""

    if baseline.get("unresolved") or candidate.get("unresolved"):
        return "indeterminate"
    baseline_required = {
        str(item["criterionId"]): STATUS_RANK[str(item["status"])]
        for item in baseline["requiredPointJudgments"]
    }
    candidate_required = {
        str(item["criterionId"]): STATUS_RANK[str(item["status"])]
        for item in candidate["requiredPointJudgments"]
    }
    baseline_negatives = {
        str(item["negativeId"]): NEGATIVE_RANK[str(item["status"])]
        for item in baseline["importantNegativeJudgments"]
    }
    candidate_negatives = {
        str(item["negativeId"]): NEGATIVE_RANK[str(item["status"])]
        for item in candidate["importantNegativeJudgments"]
    }
    if baseline_required.keys() != candidate_required.keys():
        raise ReviewError("Required-point identity drift in component comparison")
    if baseline_negatives.keys() != candidate_negatives.keys():
        raise ReviewError("Important-negative identity drift in component comparison")
    baseline_values = [baseline_required[key] for key in sorted(baseline_required)]
    candidate_values = [candidate_required[key] for key in sorted(baseline_required)]
    baseline_values.extend(baseline_negatives[key] for key in sorted(baseline_negatives))
    candidate_values.extend(candidate_negatives[key] for key in sorted(baseline_negatives))
    baseline_values.append(
        CORRECTNESS_RANK[str(baseline["materialCorrectness"]["status"])]
    )
    candidate_values.append(
        CORRECTNESS_RANK[str(candidate["materialCorrectness"]["status"])]
    )
    movements = [after - before for before, after in zip(baseline_values, candidate_values, strict=True)]
    better = any(value > 0 for value in movements)
    worse = any(value < 0 for value in movements)
    if better and worse:
        return "mixed"
    if worse:
        return "regressed"
    if better:
        return "improved"
    return "tie"


def _control_pass(subject_id: str, consensus: Mapping[str, Any]) -> bool:
    if consensus.get("unresolved"):
        return False
    if subject_id == "empty-answer-negative":
        return (
            all(
                item["status"] in {"missing", "contradicted"}
                for item in consensus["requiredPointJudgments"]
            )
            and consensus["materialCorrectness"]["status"] == "major-error"
            and not consensus["casePass"]
        )
    if subject_id == "contract-derived-positive":
        return bool(consensus["casePass"])
    raise ReviewError(f"Unknown calibration control: {subject_id}")


def build_report(manifest_path: Path) -> dict[str, Any]:
    """Build a private rationale-preserving isolated audit report."""

    manifest = validate_manifest(manifest_path)
    root = manifest_path.parent
    observations: dict[tuple[int, str, str], list[dict[str, Any]]] = {}
    for item in manifest["prompts"]:
        packet = load_json(root / item["packetPath"])
        judgment = validate_judgment(load_json(root / item["resultPath"]), packet)
        key = (int(item["caseOrdinal"]), str(item["subjectKind"]), str(item["subjectId"]))
        observations.setdefault(key, []).append(judgment)
    arm_ids = [str(item["armId"]) for item in manifest["arms"]]
    case_rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        ordinal = int(case["ordinal"])
        arms = {
            arm_id: majority_consensus(observations[(ordinal, "arm", arm_id)])
            for arm_id in arm_ids
        }
        outcomes = {
            arm_id: (
                "baseline"
                if arm_id == arm_ids[0]
                else component_outcome(arms[arm_ids[0]], arms[arm_id])
            )
            for arm_id in arm_ids
        }
        case_rows.append(
            {
                "ordinal": ordinal,
                "questionId": case["questionId"],
                "contractBasis": case["contractBasis"],
                "contractStrength": case["contractStrength"],
                "arms": arms,
                "armOutcomes": outcomes,
            }
        )
        for control_id in case["controls"]:
            consensus = majority_consensus(observations[(ordinal, "control", control_id)])
            control_rows.append(
                {
                    "ordinal": ordinal,
                    "questionId": case["questionId"],
                    "controlId": control_id,
                    "passed": _control_pass(control_id, consensus),
                    "consensus": consensus,
                }
            )
    calibration_passed = all(row["passed"] for row in control_rows)
    native_metrics = {
        str(item["armId"]): item["nativeMetrics"] for item in manifest["arms"]
    }
    fairness = {
        str(item["armId"]): item["nativeFairnessBasis"] for item in manifest["arms"]
    }
    aggregates: dict[str, Any] = {}
    for arm_id in arm_ids:
        rows = [case["arms"][arm_id] for case in case_rows]
        required_statuses = Counter(
            item["status"] for row in rows for item in row["requiredPointJudgments"]
        )
        negative_statuses = Counter(
            item["status"] for row in rows for item in row["importantNegativeJudgments"]
        )
        correctness = Counter(row["materialCorrectness"]["status"] for row in rows)
        resolved_coverages = [
            float(row["requiredPointCoverage"])
            for row in rows
            if row["requiredPointCoverage"] is not None
        ]
        aggregates[arm_id] = {
            "caseCount": len(rows),
            "casePassCount": sum(bool(row["casePass"]) for row in rows),
            "unresolvedCaseCount": sum(bool(row["unresolved"]) for row in rows),
            "meanRequiredPointCoverage": (
                round(sum(resolved_coverages) / len(resolved_coverages), 6)
                if len(resolved_coverages) == len(rows)
                else None
            ),
            "requiredPointStatuses": dict(sorted(required_statuses.items())),
            "importantNegativeStatuses": dict(sorted(negative_statuses.items())),
            "materialCorrectness": dict(sorted(correctness.items())),
            "unanimousCellRate": round(
                sum(row["unanimousCellCount"] for row in rows)
                / sum(row["judgmentCellCount"] for row in rows),
                6,
            ),
            "nativeMetrics": native_metrics[arm_id],
            "nativeFairnessBasis": fairness[arm_id],
        }
    paired = {
        arm_id: dict(
            sorted(Counter(case["armOutcomes"][arm_id] for case in case_rows).items())
        )
        for arm_id in arm_ids[1:]
    }
    gates = {
        arm_id: (
            "baseline"
            if arm_id == arm_ids[0]
            else (
                "non-regressed"
                if calibration_passed
                and not any(
                    paired[arm_id].get(status, 0)
                    for status in ("regressed", "mixed", "indeterminate")
                )
                else "reject"
            )
        )
        for arm_id in arm_ids
    }
    return {
        "schemaVersion": REPORT_VERSION,
        "manifestSha256": sha256_file(manifest_path),
        "model": manifest["model"],
        "thinking": manifest["thinking"],
        "promotionEligible": False,
        "method": manifest["method"],
        "armOrder": arm_ids,
        "contractBases": sorted({case["contractBasis"] for case in manifest["cases"]}),
        "calibration": {
            "passed": calibration_passed,
            "controlCount": len(control_rows),
            "passedControlCount": sum(row["passed"] for row in control_rows),
            "controls": control_rows,
        },
        "aggregates": aggregates,
        "pairedOutcomesByArm": paired,
        "semanticGates": gates,
        "cases": case_rows,
    }


def _fmt(value: Any, digits: int = 2) -> str:
    if not isinstance(value, (int, float)):
        return "-"
    return f"{value:,.{digits}f}"


def render_report_table(report: Mapping[str, Any], cohort: str) -> str:
    """Render a reviewed aggregate table without task text or rationales."""

    arms = report["armOrder"]
    baseline_tokens = report["aggregates"][arms[0]]["nativeMetrics"]["meanAgentTokens"]
    lines = [
        f"# Isolated semantic answer-quality audit: {cohort}",
        "",
        "Retrospective only; not promotion eligible. Each answer was judged alone in three criterion orders. Per-cell majority and component-wise comparison prevent response-order contamination, synthetic worst-case consensus, and within-case compensation.",
        "",
        f"Calibration controls: {report['calibration']['passedControlCount']}/{report['calibration']['controlCount']} passed.",
        "",
        "| Strategy | Native reward | Mean tokens | Token delta | Evidence valid | Full quality | Required coverage | Unanimous cells | Paired vs canonical | Semantic gate | Native fairness |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for arm_id in arms:
        aggregate = report["aggregates"][arm_id]
        native = aggregate["nativeMetrics"]
        tokens = native["meanAgentTokens"]
        delta = (
            (tokens / baseline_tokens - 1.0) * 100.0
            if isinstance(tokens, (int, float)) and baseline_tokens
            else None
        )
        outcomes = report["pairedOutcomesByArm"].get(arm_id, {})
        paired = "baseline" if arm_id == arms[0] else ", ".join(
            f"{key}={value}" for key, value in sorted(outcomes.items())
        )
        coverage = aggregate["meanRequiredPointCoverage"]
        lines.append(
            "| "
            + " | ".join(
                (
                    arm_id,
                    _fmt(native["meanNativeReward"], 3),
                    _fmt(tokens, 1),
                    f"{delta:+.2f}%" if delta is not None else "-",
                    f"{native['evidenceValidCaseCount']}/{aggregate['caseCount']}",
                    f"{aggregate['casePassCount']}/{aggregate['caseCount']}",
                    f"{coverage * 100:.1f}%" if coverage is not None else "unresolved",
                    f"{aggregate['unanimousCellRate'] * 100:.1f}%",
                    paired,
                    report["semanticGates"][arm_id],
                    aggregate["nativeFairnessBasis"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "`qrel-grounded-rubric` cohorts remain retrospective rubric-compliance evidence. `hard-ground-truth` is the stronger consumed-validation re-adjudication. No cross-cohort ranking is permitted.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    manifest_path: Path, report_path: Path, table_path: Path, cohort: str
) -> dict[str, Any]:
    report = build_report(manifest_path)
    _write_exclusive(report_path, report)
    _write_exclusive(table_path, render_report_table(report, cohort))
    return {
        "reportPath": str(report_path.resolve()),
        "reportSha256": sha256_file(report_path),
        "tablePath": str(table_path.resolve()),
        "tableSha256": sha256_file(table_path),
        "calibrationPassed": report["calibration"]["passed"],
        "pairedOutcomesByArm": report["pairedOutcomesByArm"],
    }


def build_consolidated_report(cohorts: Sequence[tuple[str, Path]]) -> dict[str, Any]:
    if not cohorts or len({name for name, _ in cohorts}) != len(cohorts):
        raise ReviewError("Consolidation requires distinct cohorts")
    rows: list[dict[str, Any]] = []
    calibration: dict[str, Any] = {}
    for cohort, manifest_path in cohorts:
        report = build_report(manifest_path)
        calibration[cohort] = report["calibration"]
        baseline = report["armOrder"][0]
        baseline_tokens = report["aggregates"][baseline]["nativeMetrics"]["meanAgentTokens"]
        for arm_id in report["armOrder"]:
            aggregate = report["aggregates"][arm_id]
            native = aggregate["nativeMetrics"]
            tokens = native["meanAgentTokens"]
            rows.append(
                {
                    "cohort": cohort,
                    "contractBasis": report["contractBases"][0],
                    "strategy": arm_id,
                    "nativeReward": native["meanNativeReward"],
                    "meanAgentTokens": tokens,
                    "tokenDeltaPercent": (
                        (tokens / baseline_tokens - 1.0) * 100.0
                        if isinstance(tokens, (int, float)) and baseline_tokens
                        else None
                    ),
                    "evidenceValidCaseCount": native["evidenceValidCaseCount"],
                    "caseCount": aggregate["caseCount"],
                    "fullQualityCaseCount": aggregate["casePassCount"],
                    "requiredPointCoverage": aggregate["meanRequiredPointCoverage"],
                    "unanimousCellRate": aggregate["unanimousCellRate"],
                    "pairedOutcome": (
                        "baseline"
                        if arm_id == baseline
                        else ", ".join(
                            f"{key}={value}"
                            for key, value in sorted(
                                report["pairedOutcomesByArm"][arm_id].items()
                            )
                        )
                    ),
                    "semanticGate": report["semanticGates"][arm_id],
                    "nativeFairnessBasis": aggregate["nativeFairnessBasis"],
                }
            )
    return {
        "schemaVersion": CONSOLIDATED_VERSION,
        "model": EXPECTED_MODEL,
        "thinking": EXPECTED_THINKING,
        "promotionEligible": False,
        "crossCohortRankingAllowed": False,
        "cohortCount": len(cohorts),
        "strategyRowCount": len(rows),
        "calibrationByCohort": calibration,
        "rows": rows,
    }


def render_consolidated_table(report: Mapping[str, Any]) -> str:
    lines = [
        "# Superseding isolated Classical answer-quality audit",
        "",
        "This append-only retrospective correction supersedes population-review semantic counts. Frozen answer generations were not rerun. Luna judged one answer per call in three criterion orders; majority consensus, calibration controls, complete arm bindings, native Harbor validation, and component-wise comparison were applied.",
        "",
        "| Cohort | Contract | Strategy | Native reward | Mean tokens | Token delta | Evidence valid | Full quality | Required coverage | Unanimous cells | Paired vs canonical | Semantic gate | Native fairness |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    basis_labels = {
        "semantic-rubric-plus-qrel-identities": "qrel-grounded-rubric",
        "semantic-rubric-plus-hard-ground-truth": "hard-ground-truth",
    }
    for row in report["rows"]:
        coverage = row["requiredPointCoverage"]
        delta = row["tokenDeltaPercent"]
        lines.append(
            "| "
            + " | ".join(
                (
                    row["cohort"],
                    basis_labels.get(row["contractBasis"], row["contractBasis"]),
                    row["strategy"],
                    _fmt(row["nativeReward"], 3),
                    _fmt(row["meanAgentTokens"], 1),
                    f"{delta:+.2f}%" if delta is not None else "-",
                    f"{row['evidenceValidCaseCount']}/{row['caseCount']}",
                    f"{row['fullQualityCaseCount']}/{row['caseCount']}",
                    f"{coverage * 100:.1f}%" if coverage is not None else "unresolved",
                    f"{row['unanimousCellRate'] * 100:.1f}%",
                    row["pairedOutcome"],
                    row["semanticGate"],
                    row["nativeFairnessBasis"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "All cohorts are exposed retrospective evidence. The q047-q052 contract retains hard ground truth but is consumed validation, not a fresh gate. No row is promotion eligible and no cross-cohort winner is declared.",
            "",
        ]
    )
    return "\n".join(lines)


def write_consolidated(
    cohorts: Sequence[tuple[str, Path]], report_path: Path, table_path: Path
) -> dict[str, Any]:
    report = build_consolidated_report(cohorts)
    _write_exclusive(report_path, report)
    _write_exclusive(table_path, render_consolidated_table(report))
    return {
        "cohortCount": report["cohortCount"],
        "strategyRowCount": report["strategyRowCount"],
        "reportPath": str(report_path.resolve()),
        "reportSha256": sha256_file(report_path),
        "tablePath": str(table_path.resolve()),
        "tableSha256": sha256_file(table_path),
    }


def parse_cohort(value: str) -> tuple[str, Path]:
    name, separator, path = value.partition("=")
    if not separator or re.fullmatch(r"q\d{3}-q\d{3}", name) is None or not path:
        raise argparse.ArgumentTypeError("cohort must have the form qNNN-qNNN=MANIFEST")
    return name, Path(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--task-root", type=Path, required=True)
    prepare.add_argument("--job", action="append", type=legacy.parse_job, required=True)
    prepare.add_argument("--native-report", type=Path, required=True)
    prepare.add_argument("--trial-results-only-arm", action="append", default=[])
    prepare.add_argument("--output-dir", type=Path, required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--max-workers", type=int, default=4)
    run.add_argument("--pi-executable")
    import_results = subparsers.add_parser("import-results")
    import_results.add_argument("--source-manifest", type=Path, required=True)
    import_results.add_argument("--target-manifest", type=Path, required=True)
    report = subparsers.add_parser("report")
    report.add_argument("--manifest", type=Path, required=True)
    report.add_argument("--cohort", required=True)
    report.add_argument("--report", type=Path, required=True)
    report.add_argument("--table", type=Path, required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--manifest", type=Path, required=True)
    validate.add_argument("--results", action="store_true")
    consolidate = subparsers.add_parser("consolidate")
    consolidate.add_argument("--cohort", action="append", type=parse_cohort, required=True)
    consolidate.add_argument("--report", type=Path, required=True)
    consolidate.add_argument("--table", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prepare":
        outcome = prepare_audit(
            args.task_root,
            args.job,
            args.native_report,
            args.output_dir,
            trial_results_only_arms=args.trial_results_only_arm,
        )
    elif args.command == "run":
        outcome = run_reviews(
            args.manifest,
            max_workers=args.max_workers,
            executable=args.pi_executable,
        )
    elif args.command == "import-results":
        outcome = import_valid_results(args.source_manifest, args.target_manifest)
    elif args.command == "report":
        outcome = write_report(args.manifest, args.report, args.table, args.cohort)
    elif args.command == "consolidate":
        outcome = write_consolidated(args.cohort, args.report, args.table)
    else:
        manifest = validate_manifest(args.manifest)
        if args.results:
            report = build_report(args.manifest)
            outcome = {
                "status": "valid",
                "caseCount": len(report["cases"]),
                "armCount": len(report["armOrder"]),
                "reviewCallCount": len(manifest["prompts"]),
                "calibrationPassed": report["calibration"]["passed"],
            }
        else:
            outcome = {
                "status": "valid",
                "caseCount": len(manifest["cases"]),
                "armCount": len(manifest["arms"]),
                "reviewCallCount": len(manifest["prompts"]),
            }
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
