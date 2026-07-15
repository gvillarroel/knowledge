#!/usr/bin/env python3
"""Aggregate mechanical and blinded-review metrics for the live 90-answer run."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from _answer_output import (
    DEFAULT_CONTRACT,
    AnswerEvaluationError,
    exact_keys,
    load_contract,
    validate_preparation,
    validate_review_report,
)
from _evaluation import REPO_ROOT, canonical_json, display_path, load_json, sha256, write_new


ABSOLUTE_WINDOWS = re.compile(r"^[A-Za-z]:[\\/]")
EVALUATION_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = EVALUATION_ROOT.parents[1]
SKILL_ARENA_CONFIG = EVALUATION_ROOT / "skill-arena/ensemble-hard10.yaml"
SKILL_ARENA_MANIFEST = EVALUATION_ROOT / "skill-arena/config-manifest.json"
IMPLEMENTATION_FILES = {
    "mechanical_runtime": EVALUATION_ROOT / "scripts/_answer_output.py",
    "preparer": EVALUATION_ROOT / "scripts/prepare_answer_output_evaluation.py",
    "reviewer": EVALUATION_ROOT / "scripts/run_blinded_answer_reviews.py",
    "aggregator": Path(__file__).resolve(),
}


def _mean(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def _rounded(value: float) -> float:
    return round(float(value), 8)


def _semantic_metrics(review: Mapping[str, Any]) -> dict[str, float]:
    fidelity = [float(item["score"]) for item in review["claim_fidelity"]]
    atomic = [float(value) for value in review["atomic_scores"].values()]
    negatives = [float(value) for value in review["negative_scores"].values()]
    return {
        "claim_correctness": _rounded(_mean(fidelity)),
        "semantic_completeness": _rounded(_mean(atomic)),
        "important_negative_coverage": _rounded(_mean(negatives)),
    }


def _metric_mean(rows: Sequence[Mapping[str, Any]], metrics: Sequence[str]) -> dict[str, float]:
    return {
        metric: _rounded(_mean(float(row["metrics"][metric]) for row in rows))
        for metric in metrics
    }


def _metric_stddev(rows: Sequence[Mapping[str, Any]], metrics: Sequence[str]) -> dict[str, float]:
    return {
        metric: _rounded(
            statistics.pstdev([float(row["metrics"][metric]) for row in rows])
            if len(rows) > 1
            else 0.0
        )
        for metric in metrics
    }


def _hash_output_identities(rows: Sequence[Mapping[str, Any]]) -> str:
    values = sorted(
        [
            {"answer_id": row["answer_id"], "output_sha256": row["output_sha256"]}
            for row in rows
        ],
        key=lambda item: item["answer_id"],
    )
    return hashlib.sha256(canonical_json(values).encode("utf-8")).hexdigest()


def _repository_binding(path: Path) -> dict[str, str]:
    resolved = path.resolve(strict=True)
    return {
        "path": resolved.relative_to(PROJECT_ROOT.resolve(strict=True)).as_posix(),
        "sha256": sha256(resolved),
    }


def _publication_bindings(
    contract: Mapping[str, Any],
    manifest: Mapping[str, Any],
    review_report: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    config_manifest = load_json(SKILL_ARENA_MANIFEST)
    skill_arena = {
        "config": _repository_binding(SKILL_ARENA_CONFIG),
        "config_manifest": _repository_binding(SKILL_ARENA_MANIFEST),
        "profiles": contract["benchmark"]["profiles"],
        "consult_skills": config_manifest["consult_skills"],
    }
    implementation = {
        "mechanical_runtime": manifest["implementation"]["mechanical_runtime"],
        "preparer": manifest["implementation"]["preparer"],
        "reviewer": review_report["implementation"]["reviewer"],
        "aggregator": _repository_binding(IMPLEMENTATION_FILES["aggregator"]),
    }
    return skill_arena, implementation


def build_summary(
    mechanical: Mapping[str, Any],
    manifest: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
    review_report: Mapping[str, Any],
    contract: Mapping[str, Any],
    input_dir: Path,
    reviews_path: Path,
) -> dict[str, Any]:
    """Build a compact report without copying candidate outputs or reviewer notes."""

    review_by_id = {review["answer_id"]: review for review in review_report["reviews"]}
    rows: list[dict[str, Any]] = []
    for mechanical_row in mechanical["answers"]:
        review = review_by_id[mechanical_row["answer_id"]]
        metrics = dict(mechanical_row["metrics"])
        metrics.update(_semantic_metrics(review))
        rows.append(
            {
                "answer_id": mechanical_row["answer_id"],
                "profile_id": mechanical_row["profile_id"],
                "question_id": mechanical_row["question_id"],
                "repetition": mechanical_row["repetition"],
                "output_sha256": mechanical_row["output_sha256"],
                "parseable": float(mechanical_row["parse_status"] == "object"),
                "promptfoo_full_pass": mechanical_row["promptfoo_full_pass"],
                "metrics": {metric: metrics[metric] for metric in contract["metrics"]},
            }
        )

    profiles = contract["benchmark"]["profiles"]
    questions = contract["benchmark"]["question_ids"]
    metrics = contract["metrics"]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_profile: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["profile_id"], row["question_id"])].append(row)
        by_profile[row["profile_id"]].append(row)

    profile_question_metrics: list[dict[str, Any]] = []
    for profile in profiles:
        for question in questions:
            cell = sorted(grouped[(profile, question)], key=lambda row: row["repetition"])
            profile_question_metrics.append(
                {
                    "profile_id": profile,
                    "question_id": question,
                    "answer_count": len(cell),
                    "parseable_rate": _rounded(_mean(row["parseable"] for row in cell)),
                    "strict_full_pass_rate": _rounded(
                        _mean(float(row["promptfoo_full_pass"]) for row in cell)
                    ),
                    "metrics": _metric_mean(cell, metrics),
                    "output_identity_sha256": _hash_output_identities(cell),
                }
            )

    question_lookup = {
        (row["profile_id"], row["question_id"]): row for row in profile_question_metrics
    }
    aggregates: dict[str, Any] = {}
    for profile in profiles:
        profile_rows = by_profile[profile]
        question_rows = [question_lookup[(profile, question)] for question in questions]
        aggregates[profile] = {
            "answer_count": len(profile_rows),
            "question_count": len(question_rows),
            "repetitions_per_question": contract["benchmark"]["repetitions_per_cell"],
            "parseable_rate": _rounded(_mean(row["parseable_rate"] for row in question_rows)),
            "strict_full_pass_rate": _rounded(
                _mean(float(row["strict_full_pass_rate"]) for row in question_rows)
            ),
            "metrics": _metric_mean(question_rows, metrics),
            "metric_population_stddev": _metric_stddev(question_rows, metrics),
            "worst_question_metrics": {
                metric: _rounded(min(row["metrics"][metric] for row in question_rows))
                for metric in metrics
            },
        }

    treatment = "ensemble-consult-treatment"
    contrasts = (
        ("ensemble_vs_knowledge_only", "knowledge-only-control"),
        ("ensemble_vs_adaptive", "adaptive-consult-control"),
    )
    paired_deltas: dict[str, Any] = {}
    for comparison_id, control in contrasts:
        per_question = []
        for question in questions:
            treatment_row = question_lookup[(treatment, question)]
            control_row = question_lookup[(control, question)]
            per_question.append(
                {
                    metric: treatment_row["metrics"][metric] - control_row["metrics"][metric]
                    for metric in metrics
                }
            )
        paired_deltas[comparison_id] = {
            "treatment_profile": treatment,
            "control_profile": control,
            "matched_question_count": len(per_question),
            "strict_full_pass_rate": _rounded(
                _mean(
                    question_lookup[(treatment, question)]["strict_full_pass_rate"]
                    - question_lookup[(control, question)]["strict_full_pass_rate"]
                    for question in questions
                )
            ),
            "metrics": {
                metric: _rounded(_mean(row[metric] for row in per_question))
                for metric in metrics
            },
        }

    input_dir = input_dir.resolve(strict=True)
    reviews_path = reviews_path.resolve(strict=True)
    task_path = input_dir / "review-tasks.jsonl"
    manifest_path = input_dir / "review-manifest.json"
    mechanical_path = input_dir / "mechanical-results.json"
    skill_arena, implementation = _publication_bindings(contract, manifest, review_report)
    return {
        "schema_version": contract["publication"]["compact_schema_version"],
        "status": "pass",
        "answer_count": len(rows),
        "contract": manifest["contract"],
        "benchmark": manifest["benchmark"],
        "bundle": manifest["bundle"],
        "ground_truth": manifest["ground_truth"],
        "skill_arena": skill_arena,
        "implementation": implementation,
        "inputs": {
            "promptfoo": manifest["input"],
            "review_tasks": {"path": display_path(task_path), "sha256": sha256(task_path)},
            "review_manifest": {"path": display_path(manifest_path), "sha256": sha256(manifest_path)},
            "mechanical_results": {"path": display_path(mechanical_path), "sha256": sha256(mechanical_path)},
            "reviews": {"path": display_path(reviews_path), "sha256": sha256(reviews_path)},
        },
        "review": {
            "model": review_report["model"],
            "blinded": True,
            "model_judged": True,
            "review_count": review_report["review_count"],
            "score_values": review_report["score_values"],
            "task_sha256": review_report["task_sha256"],
        },
        "metric_contract": {
            **mechanical["metric_contract"],
            "claim_correctness": "blinded fixed-rubric fidelity of each candidate claim to supplied authoritative support records",
            "semantic_completeness": "blinded fixed-rubric coverage of every atomic ground-truth claim",
            "important_negative_coverage": "blinded fixed-rubric coverage of important exclusions and failure conditions",
        },
        "profile_order": profiles,
        "aggregates": aggregates,
        "profile_question_metrics": profile_question_metrics,
        "paired_deltas": paired_deltas,
        "answer_identity_sha256": _hash_output_identities(rows),
    }


def _reject_machine_paths(value: Any, label: str = "report") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_machine_paths(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_machine_paths(item, f"{label}[{index}]")
    elif isinstance(value, str) and (ABSOLUTE_WINDOWS.match(value) or value.startswith("/home/") or value.startswith("/Users/")):
        raise AnswerEvaluationError(f"compact report contains an absolute machine path at {label}")


def _validate_metric_object(value: Any, metrics: Sequence[str], label: str, *, delta: bool = False) -> None:
    exact_keys(value, set(metrics), label)
    lower = -1.0 if delta else 0.0
    for metric, score in value.items():
        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not math.isfinite(float(score))
            or not lower <= float(score) <= 1.0
        ):
            raise AnswerEvaluationError(f"{label}.{metric} is outside its score range")


def _validate_repository_binding(value: Any, path: Path, label: str) -> None:
    binding = exact_keys(value, {"path", "sha256"}, label)
    if binding != _repository_binding(path):
        raise AnswerEvaluationError(f"{label} differs from the current repository file")


def validate_summary(summary: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the compact checked-report schema and complete cell coverage."""

    exact_keys(
        summary,
        {
            "schema_version",
            "status",
            "answer_count",
            "contract",
            "benchmark",
            "bundle",
            "ground_truth",
            "skill_arena",
            "implementation",
            "inputs",
            "review",
            "metric_contract",
            "profile_order",
            "aggregates",
            "profile_question_metrics",
            "paired_deltas",
            "answer_identity_sha256",
        },
        "compact answer report",
    )
    if summary["schema_version"] != contract["publication"]["compact_schema_version"] or summary["status"] != "pass":
        raise AnswerEvaluationError("compact answer report schema or status differs")
    if summary["answer_count"] != contract["benchmark"]["total_answers"]:
        raise AnswerEvaluationError("compact answer report answer count differs")
    exact_keys(summary["contract"], {"path", "sha256"}, "compact contract binding")
    contract_label = summary["contract"]["path"]
    if not isinstance(contract_label, str) or not contract_label:
        raise AnswerEvaluationError("compact contract path must be repository-relative")
    logical_contract = PurePosixPath(contract_label.replace("\\", "/"))
    if logical_contract.is_absolute() or any(part in {"", ".", ".."} for part in logical_contract.parts):
        raise AnswerEvaluationError("compact contract path must be repository-relative")
    contract_path = REPO_ROOT.joinpath(*logical_contract.parts).resolve(strict=True)
    try:
        contract_path.relative_to(REPO_ROOT.resolve(strict=True))
    except ValueError as exc:
        raise AnswerEvaluationError("compact contract path escapes the repository") from exc
    if summary["contract"]["sha256"] != sha256(contract_path):
        raise AnswerEvaluationError("compact contract binding differs from the current contract")
    if summary["benchmark"] != {
        "id": contract["benchmark"]["id"],
        "profiles": contract["benchmark"]["profiles"],
        "variant_id": contract["benchmark"]["variant_id"],
        "question_ids": contract["benchmark"]["question_ids"],
        "repetitions_per_cell": contract["benchmark"]["repetitions_per_cell"],
        "answer_count": contract["benchmark"]["total_answers"],
    }:
        raise AnswerEvaluationError("compact answer benchmark binding differs")
    expected_bundle = contract["bundle"]
    if summary["bundle"] != {
        "run_id": expected_bundle["run_id"],
        "repository_path": expected_bundle["repository_path"],
        "file_count": expected_bundle["file_count"],
        "tree_sha256": expected_bundle["tree_sha256"],
        "ensemble_index_sha256": expected_bundle["ensemble_index_sha256"],
        "ensemble_plan_sha256": expected_bundle["ensemble_plan_sha256"],
        "core_tree_sha256": expected_bundle["core_tree_sha256"],
        "records_sha256": expected_bundle["records_sha256"],
        "record_count": expected_bundle["record_count"],
        "source_manifest_sha256": expected_bundle["source_manifest_sha256"],
    }:
        raise AnswerEvaluationError("compact answer bundle binding differs")
    if summary["ground_truth"] != {
        "path": contract["ground_truth"]["path"],
        "sha256": contract["ground_truth"]["sha256"],
    }:
        raise AnswerEvaluationError("compact answer ground-truth binding differs")
    skill_arena = exact_keys(
        summary["skill_arena"],
        {"config", "config_manifest", "profiles", "consult_skills"},
        "compact Skill Arena binding",
    )
    _validate_repository_binding(skill_arena["config"], SKILL_ARENA_CONFIG, "compact Skill Arena config")
    _validate_repository_binding(
        skill_arena["config_manifest"],
        SKILL_ARENA_MANIFEST,
        "compact Skill Arena manifest",
    )
    current_manifest = load_json(SKILL_ARENA_MANIFEST)
    if skill_arena["profiles"] != contract["benchmark"]["profiles"]:
        raise AnswerEvaluationError("compact Skill Arena profiles differ")
    if skill_arena["consult_skills"] != current_manifest["consult_skills"]:
        raise AnswerEvaluationError("compact Skill Arena skill bindings differ")
    implementation = exact_keys(
        summary["implementation"],
        set(IMPLEMENTATION_FILES),
        "compact implementation bindings",
    )
    for name, path in IMPLEMENTATION_FILES.items():
        _validate_repository_binding(
            implementation[name],
            path,
            f"compact implementation {name}",
        )
    exact_keys(
        summary["inputs"],
        {"promptfoo", "review_tasks", "review_manifest", "mechanical_results", "reviews"},
        "compact answer inputs",
    )
    for name, binding in summary["inputs"].items():
        expected_keys = (
            {"path", "sha256", "promptfoo_eval_id", "effective_config_sha256"}
            if name == "promptfoo"
            else {"path", "sha256"}
        )
        exact_keys(binding, expected_keys, f"compact input {name}")
        if not isinstance(binding["path"], str) or re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]) is None:
            raise AnswerEvaluationError(f"compact input binding differs for {name}")
        if name == "promptfoo" and re.fullmatch(
            r"[0-9a-f]{64}", binding["effective_config_sha256"]
        ) is None:
            raise AnswerEvaluationError("compact Promptfoo effective config binding differs")
    exact_keys(
        summary["review"],
        {"model", "blinded", "model_judged", "review_count", "score_values", "task_sha256"},
        "compact review binding",
    )
    if summary["review"] != {
        "model": contract["review"]["model"],
        "blinded": True,
        "model_judged": True,
        "review_count": contract["benchmark"]["total_answers"],
        "score_values": contract["review"]["score_values"],
        "task_sha256": summary["review"]["task_sha256"],
    } or re.fullmatch(r"[0-9a-f]{64}", summary["review"]["task_sha256"]) is None:
        raise AnswerEvaluationError("compact review binding differs")
    if summary["profile_order"] != contract["benchmark"]["profiles"]:
        raise AnswerEvaluationError("compact answer report profile order differs")
    if set(summary["metric_contract"]) != set(contract["metrics"]):
        raise AnswerEvaluationError("compact answer report metric contract differs")
    if not isinstance(summary["answer_identity_sha256"], str) or re.fullmatch(
        r"[0-9a-f]{64}", summary["answer_identity_sha256"]
    ) is None:
        raise AnswerEvaluationError("compact answer identity SHA-256 differs")
    profiles = contract["benchmark"]["profiles"]
    questions = contract["benchmark"]["question_ids"]
    metrics = contract["metrics"]
    if not isinstance(summary["aggregates"], dict) or list(summary["aggregates"]) != profiles:
        raise AnswerEvaluationError("compact answer aggregates differ")
    for profile, aggregate in summary["aggregates"].items():
        exact_keys(
            aggregate,
            {
                "answer_count",
                "question_count",
                "repetitions_per_question",
                "parseable_rate",
                "strict_full_pass_rate",
                "metrics",
                "metric_population_stddev",
                "worst_question_metrics",
            },
            f"aggregate {profile}",
        )
        if (
            aggregate["answer_count"] != len(questions) * contract["benchmark"]["repetitions_per_cell"]
            or aggregate["question_count"] != len(questions)
            or aggregate["repetitions_per_question"] != contract["benchmark"]["repetitions_per_cell"]
        ):
            raise AnswerEvaluationError(f"aggregate counts differ for {profile}")
        for key in ("parseable_rate", "strict_full_pass_rate"):
            if not 0.0 <= aggregate[key] <= 1.0:
                raise AnswerEvaluationError(f"aggregate {key} differs for {profile}")
        _validate_metric_object(aggregate["metrics"], metrics, f"aggregate metrics {profile}")
        _validate_metric_object(
            aggregate["metric_population_stddev"], metrics, f"aggregate stddev {profile}"
        )
        _validate_metric_object(
            aggregate["worst_question_metrics"], metrics, f"aggregate worst question {profile}"
        )
    cells = summary["profile_question_metrics"]
    if not isinstance(cells, list) or len(cells) != len(profiles) * len(questions):
        raise AnswerEvaluationError("compact answer question-cell count differs")
    observed: set[tuple[str, str]] = set()
    for cell in cells:
        exact_keys(
            cell,
            {
                "profile_id",
                "question_id",
                "answer_count",
                "parseable_rate",
                "strict_full_pass_rate",
                "metrics",
                "output_identity_sha256",
            },
            "profile-question metric cell",
        )
        identity = (cell["profile_id"], cell["question_id"])
        if identity in observed:
            raise AnswerEvaluationError(f"duplicate compact profile-question cell: {identity}")
        observed.add(identity)
        if cell["answer_count"] != contract["benchmark"]["repetitions_per_cell"]:
            raise AnswerEvaluationError(f"compact repetition count differs for {identity}")
        if not 0.0 <= cell["parseable_rate"] <= 1.0 or not 0.0 <= cell["strict_full_pass_rate"] <= 1.0:
            raise AnswerEvaluationError(f"compact cell rate differs for {identity}")
        if re.fullmatch(r"[0-9a-f]{64}", cell["output_identity_sha256"]) is None:
            raise AnswerEvaluationError(f"compact cell output identity differs for {identity}")
        _validate_metric_object(cell["metrics"], metrics, f"cell metrics {identity}")
    expected_cells = {(profile, question) for profile in profiles for question in questions}
    if observed != expected_cells:
        raise AnswerEvaluationError("compact profile-question identities differ")
    expected_order = [(profile, question) for profile in profiles for question in questions]
    if [(cell["profile_id"], cell["question_id"]) for cell in cells] != expected_order:
        raise AnswerEvaluationError("compact profile-question order differs")
    cell_lookup = {
        (cell["profile_id"], cell["question_id"]): cell
        for cell in cells
    }
    for profile in profiles:
        question_rows = [cell_lookup[(profile, question)] for question in questions]
        expected_aggregate = {
            "answer_count": len(questions) * contract["benchmark"]["repetitions_per_cell"],
            "question_count": len(questions),
            "repetitions_per_question": contract["benchmark"]["repetitions_per_cell"],
            "parseable_rate": _rounded(
                _mean(row["parseable_rate"] for row in question_rows)
            ),
            "strict_full_pass_rate": _rounded(
                _mean(row["strict_full_pass_rate"] for row in question_rows)
            ),
            "metrics": _metric_mean(question_rows, metrics),
            "metric_population_stddev": _metric_stddev(question_rows, metrics),
            "worst_question_metrics": {
                metric: _rounded(min(row["metrics"][metric] for row in question_rows))
                for metric in metrics
            },
        }
        if summary["aggregates"][profile] != expected_aggregate:
            raise AnswerEvaluationError(
                f"compact aggregate arithmetic differs for {profile}"
            )
    if set(summary["paired_deltas"]) != {"ensemble_vs_knowledge_only", "ensemble_vs_adaptive"}:
        raise AnswerEvaluationError("compact paired comparison identities differ")
    expected_controls = {
        "ensemble_vs_knowledge_only": "knowledge-only-control",
        "ensemble_vs_adaptive": "adaptive-consult-control",
    }
    for comparison, delta in summary["paired_deltas"].items():
        exact_keys(
            delta,
            {"treatment_profile", "control_profile", "matched_question_count", "strict_full_pass_rate", "metrics"},
            f"paired delta {comparison}",
        )
        if (
            delta["treatment_profile"] != "ensemble-consult-treatment"
            or delta["control_profile"] != expected_controls[comparison]
            or delta["matched_question_count"] != len(questions)
        ):
            raise AnswerEvaluationError(f"paired delta identity differs for {comparison}")
        if not -1.0 <= delta["strict_full_pass_rate"] <= 1.0:
            raise AnswerEvaluationError(f"paired strict delta differs for {comparison}")
        _validate_metric_object(delta["metrics"], metrics, f"paired metrics {comparison}", delta=True)
        treatment = delta["treatment_profile"]
        control = delta["control_profile"]
        per_question = [
            {
                metric: cell_lookup[(treatment, question)]["metrics"][metric]
                - cell_lookup[(control, question)]["metrics"][metric]
                for metric in metrics
            }
            for question in questions
        ]
        expected_delta = {
            "treatment_profile": treatment,
            "control_profile": control,
            "matched_question_count": len(questions),
            "strict_full_pass_rate": _rounded(
                _mean(
                    cell_lookup[(treatment, question)]["strict_full_pass_rate"]
                    - cell_lookup[(control, question)]["strict_full_pass_rate"]
                    for question in questions
                )
            ),
            "metrics": {
                metric: _rounded(_mean(row[metric] for row in per_question))
                for metric in metrics
            },
        }
        if delta != expected_delta:
            raise AnswerEvaluationError(
                f"compact paired-delta arithmetic differs for {comparison}"
            )
    _reject_machine_paths(summary)
    return dict(summary)


def render_markdown(summary: Mapping[str, Any]) -> str:
    """Render the compact comparison in English."""

    metrics = summary["metric_contract"]
    lines = [
        "# Semantic OKF Ensemble Answer-Output Evaluation",
        "",
        f"Status: **{summary['status']}**. This report covers {summary['answer_count']} live answers: three profiles, ten hard questions, and three repetitions per profile-question cell.",
        "",
        "Correctness, semantic completeness, and important-negative coverage are model-judged under a blinded fixed rubric. Contract, evidence validity, grounding, exact claim identity, paper, and source metrics are recomputed mechanically against the exact final-03 bundle. Promptfoo's evidence named score is not reused.",
        "",
        "| Profile | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for profile in summary["profile_order"]:
        aggregate = summary["aggregates"][profile]
        score = aggregate["metrics"]
        lines.append(
            f"| `{profile}` | {aggregate['strict_full_pass_rate']:.1%} | "
            f"{score['response_contract']:.1%} | {score['evidence_validity']:.1%} | "
            f"{score['grounding']:.1%} | {score['claim_correctness']:.1%} | "
            f"{score['semantic_completeness']:.1%} | {score['exact_atomic_evidence_coverage']:.1%} | "
            f"{score['required_paper_coverage']:.1%} | {score['required_source_coverage']:.1%} | "
            f"{score['important_negative_coverage']:.1%} | {score['exact_negative_evidence_coverage']:.1%} |"
        )
    lines.extend(
        [
            "",
            "## Stability diagnostics",
            "",
            "Population standard deviation and worst-question means are shown as `σ / worst`. These diagnostics prevent a high average from hiding a brittle question family.",
            "",
            "| Profile | Contract | Evidence validity | Grounding | Correctness | Completeness |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for profile in summary["profile_order"]:
        aggregate = summary["aggregates"][profile]
        deviation = aggregate["metric_population_stddev"]
        worst = aggregate["worst_question_metrics"]
        lines.append(
            f"| `{profile}` | {deviation['response_contract']:.1%} / {worst['response_contract']:.1%} | "
            f"{deviation['evidence_validity']:.1%} / {worst['evidence_validity']:.1%} | "
            f"{deviation['grounding']:.1%} / {worst['grounding']:.1%} | "
            f"{deviation['claim_correctness']:.1%} / {worst['claim_correctness']:.1%} | "
            f"{deviation['semantic_completeness']:.1%} / {worst['semantic_completeness']:.1%} |"
        )
    lines.extend(
        [
            "",
            "## Causal profile contrasts",
            "",
            "Positive values favor the ensemble consultation treatment. Deltas are means of ten matched question-level differences, each question already averaged over its three repetitions.",
            "",
            "| Contrast | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for comparison in ("ensemble_vs_knowledge_only", "ensemble_vs_adaptive"):
        comparison_row = summary["paired_deltas"][comparison]
        delta = comparison_row["metrics"]
        lines.append(
            f"| `{comparison}` | {comparison_row['strict_full_pass_rate']:+.1%} | "
            f"{delta['response_contract']:+.1%} | "
            f"{delta['evidence_validity']:+.1%} | {delta['grounding']:+.1%} | "
            f"{delta['claim_correctness']:+.1%} | {delta['semantic_completeness']:+.1%} | "
            f"{delta['exact_atomic_evidence_coverage']:+.1%} | "
            f"{delta['required_paper_coverage']:+.1%} | {delta['required_source_coverage']:+.1%} | "
            f"{delta['important_negative_coverage']:+.1%} | "
            f"{delta['exact_negative_evidence_coverage']:+.1%} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- Retrieval metrics and answer metrics are separate: finding a paper does not prove that the generated synthesis is correct, complete, or grounded.",
            "- Semantic scores are model-judged evidence, not mechanical truth. The reviewer is blinded to profile and repetition, and the report preserves that qualification.",
            "- A strict full-pass failure can coexist with useful partial scores because one failed assertion fails a complete Skill Arena cell.",
            "- Raw answers, prompts, mappings, and reviewer transcripts remain append-only under the ignored results tree. This compact report retains only hashes, bindings, and aggregate scores.",
            f"- The report binds Skill Arena config `{summary['skill_arena']['config']['sha256']}`, config manifest `{summary['skill_arena']['config_manifest']['sha256']}`, and every evaluator/reviewer implementation file by SHA-256.",
            "",
            "## Metric contract",
            "",
        ]
    )
    for metric_name in summary["metric_contract"]:
        lines.append(f"- **{metric_name}**: {metrics[metric_name]}.")
    lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        contract_path = args.contract.resolve(strict=True)
        contract = load_contract(contract_path)
        tasks, manifest, mechanical = validate_preparation(args.input_dir, contract, contract_path)
        reviews_path = (args.reviews or (args.input_dir / "reviews.json")).resolve(strict=True)
        try:
            reviews_path.relative_to(REPO_ROOT.resolve(strict=True))
        except ValueError as exc:
            raise AnswerEvaluationError("review report must remain inside the repository") from exc
        review_report = validate_review_report(
            load_json(reviews_path), tasks, manifest, contract
        )
        summary = build_summary(
            mechanical,
            manifest,
            tasks,
            review_report,
            contract,
            args.input_dir,
            reviews_path,
        )
        validate_summary(summary, contract)
        write_new(args.output_json.resolve(strict=False), json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
        write_new(args.output_markdown.resolve(strict=False), render_markdown(summary))
    except (AnswerEvaluationError, OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "answers": summary["answer_count"],
                "profiles": len(summary["profile_order"]),
                "reviews": summary["review"]["review_count"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
