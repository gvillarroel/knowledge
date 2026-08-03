#!/usr/bin/env python3
"""Audit the sealed definitive-expert summary against every local artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import statistics
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-definitive-experts-summary/1.0"
SCRIPT_PATH = Path(__file__).resolve()
EVALUATION_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_SUMMARY = (
    EVALUATION_ROOT
    / "reports"
    / "definitive-experts-20260728.json"
)
BASELINE_REGISTRY = EVALUATION_ROOT / "definitive-baselines.json"
DATASET_IDS = {"astro-40", "graphrag-papers-40"}


class AuditError(ValueError):
    """Describe a missing, drifting, or internally inconsistent artifact."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"{label} must be a JSON object: {path}")
    return value


def _repo_path(raw: Any, *, label: str) -> Path:
    if not isinstance(raw, str):
        raise AuditError(f"{label} must be a repository-relative path")
    relative = PurePosixPath(raw)
    if (
        relative.is_absolute()
        or not relative.parts
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise AuditError(f"Unsafe {label}: {raw!r}")
    path = REPO_ROOT.joinpath(*relative.parts)
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise AuditError(f"{label} escapes the repository: {raw}") from exc
    if not path.exists():
        raise AuditError(f"{label} is absent: {raw}")
    return path


def _inventory(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        if path.is_symlink():
            raise AuditError(f"Artifact contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    return rows


def _canonical_digest(value: Any) -> str:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def _same_number(left: Any, right: Any) -> bool:
    return (
        not isinstance(left, bool)
        and not isinstance(right, bool)
        and isinstance(left, (int, float))
        and isinstance(right, (int, float))
        and abs(float(left) - float(right)) <= 1e-12
    )


def _audit_baseline(
    dataset_id: str,
    declared: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> None:
    registered = registry.get(dataset_id)
    if not isinstance(registered, dict):
        raise AuditError(f"Baseline registry lacks {dataset_id}")
    if declared.get("candidate_id") != registered.get("candidate_id"):
        raise AuditError(f"{dataset_id} baseline identity drift")
    evidence = registered.get("evidence_report")
    if not isinstance(evidence, dict):
        raise AuditError(f"{dataset_id} baseline evidence is invalid")
    if declared.get("evidence_report_path") != evidence.get("path"):
        raise AuditError(f"{dataset_id} baseline path drift")
    if declared.get("evidence_report_sha256") != evidence.get("sha256"):
        raise AuditError(f"{dataset_id} baseline digest declaration drift")
    evidence_path = _repo_path(
        declared.get("evidence_report_path"),
        label=f"{dataset_id} baseline evidence",
    )
    if _sha256_file(evidence_path) != declared.get("evidence_report_sha256"):
        raise AuditError(f"{dataset_id} baseline evidence digest drift")
    metrics = declared.get("metrics")
    registered_metrics = registered.get("metrics")
    if not isinstance(metrics, dict) or not isinstance(registered_metrics, dict):
        raise AuditError(f"{dataset_id} baseline metrics are invalid")
    for name in ("recall_at_10", "mrr_at_10", "ndcg_at_10"):
        if not _same_number(metrics.get(name), registered_metrics.get(name)):
            raise AuditError(f"{dataset_id} baseline {name} drift")
    if not _same_number(declared.get("p95_ms"), registered.get("p95_ms")):
        raise AuditError(f"{dataset_id} baseline P95 drift")


def _audit_candidate(
    dataset_id: str,
    declared: Mapping[str, Any],
) -> None:
    candidate_id = declared.get("candidate_id")
    expert = _repo_path(
        declared.get("expert_path"),
        label=f"{dataset_id} expert",
    )
    if not expert.is_dir() or expert.name != candidate_id:
        raise AuditError(f"{dataset_id} expert identity drift")
    manifest_path = expert / "expert-manifest.json"
    if _sha256_file(manifest_path) != declared.get("expert_manifest_sha256"):
        raise AuditError(f"{dataset_id} expert manifest digest drift")
    manifest = _load_json(manifest_path, label=f"{dataset_id} expert manifest")
    if manifest.get("skill_name") != candidate_id:
        raise AuditError(f"{dataset_id} manifest skill identity drift")
    inventory = _inventory(expert)
    if _canonical_digest(inventory) != declared.get("expert_tree_sha256"):
        raise AuditError(f"{dataset_id} expert tree digest drift")
    knowledge = manifest.get("knowledge")
    if not isinstance(knowledge, dict) or not isinstance(knowledge.get("tree"), dict):
        raise AuditError(f"{dataset_id} manifest knowledge binding is invalid")
    if knowledge["tree"].get("sha256") != declared.get("knowledge_tree_sha256"):
        raise AuditError(f"{dataset_id} knowledge tree digest drift")
    if knowledge["tree"].get("file_count") != declared.get("knowledge_file_count"):
        raise AuditError(f"{dataset_id} knowledge file count drift")
    if knowledge.get("record_count") != declared.get("record_count"):
        raise AuditError(f"{dataset_id} knowledge record count drift")

    routing_source = _repo_path(
        declared.get("routing_index_path"),
        label=f"{dataset_id} routing index",
    )
    routing_sha256 = declared.get("routing_index_sha256")
    embedded_routing = expert / "scripts" / "expert_routing_index.json"
    if (
        _sha256_file(routing_source) != routing_sha256
        or _sha256_file(embedded_routing) != routing_sha256
    ):
        raise AuditError(f"{dataset_id} routing index digest drift")


def _audit_replicates(
    dataset_id: str,
    dataset: Mapping[str, Any],
) -> None:
    candidate = dataset.get("candidate")
    improvement = dataset.get("improvement")
    replicates = dataset.get("replicates")
    if (
        not isinstance(candidate, dict)
        or not isinstance(improvement, dict)
        or not isinstance(replicates, list)
        or len(replicates) != 3
    ):
        raise AuditError(f"{dataset_id} replicate contract is invalid")
    p95_values = []
    for index, declared in enumerate(replicates):
        if not isinstance(declared, dict):
            raise AuditError(f"{dataset_id} replicate {index} is invalid")
        report_path = _repo_path(
            declared.get("path"),
            label=f"{dataset_id} replicate {index}",
        )
        if _sha256_file(report_path) != declared.get("report_sha256"):
            raise AuditError(f"{dataset_id} replicate {index} digest drift")
        report = _load_json(
            report_path,
            label=f"{dataset_id} replicate {index}",
        )
        if (
            report.get("status") != "pass"
            or report.get("dataset_id") != dataset_id
            or report.get("candidate_id") != candidate.get("candidate_id")
            or report.get("promotion_eligible") is not False
            or report.get("improvement_gate", {}).get("status") != "pass"
        ):
            raise AuditError(f"{dataset_id} replicate {index} state drift")
        selected = report.get("selected_metrics")
        if not isinstance(selected, dict):
            raise AuditError(f"{dataset_id} replicate {index} metrics are invalid")
        metrics = selected.get("all_40")
        timing = selected.get("timing_ms")
        evidence = selected.get("evidence_validity")
        if (
            not isinstance(metrics, dict)
            or not isinstance(timing, dict)
            or not isinstance(evidence, dict)
            or evidence.get("ratio") != 1.0
        ):
            raise AuditError(f"{dataset_id} replicate {index} evidence drift")
        for name in ("recall_at_10", "mrr_at_10", "ndcg_at_10"):
            if not _same_number(metrics.get(name), candidate["metrics"].get(name)):
                raise AuditError(
                    f"{dataset_id} replicate {index} {name} drift"
                )
        if not _same_number(timing.get("p95"), declared.get("p95_ms")):
            raise AuditError(f"{dataset_id} replicate {index} P95 drift")
        p95_values.append(float(declared["p95_ms"]))
    if not _same_number(
        statistics.median(p95_values),
        improvement.get("representative_p95_ms"),
    ):
        raise AuditError(f"{dataset_id} representative P95 is not the median")


def audit(summary_path: Path) -> dict[str, Any]:
    """Audit every summary binding and return a compact receipt."""

    summary = _load_json(summary_path, label="definitive expert summary")
    if summary.get("schema_version") != SCHEMA_VERSION:
        raise AuditError("Unsupported definitive expert summary schema")
    if summary.get("status") != "pass":
        raise AuditError("Definitive expert summary is not passing")
    if summary.get("promotion_eligible") is not False:
        raise AuditError("Retrospective summary cannot be promotion eligible")
    datasets = summary.get("datasets")
    if not isinstance(datasets, dict) or set(datasets) != DATASET_IDS:
        raise AuditError("Definitive summary dataset set drift")
    registry = _load_json(BASELINE_REGISTRY, label="baseline registry")
    for dataset_id in sorted(DATASET_IDS):
        dataset = datasets[dataset_id]
        if not isinstance(dataset, dict):
            raise AuditError(f"{dataset_id} summary is invalid")
        baseline = dataset.get("baseline")
        candidate = dataset.get("candidate")
        if not isinstance(baseline, dict) or not isinstance(candidate, dict):
            raise AuditError(f"{dataset_id} summary lacks baseline or candidate")
        _audit_baseline(dataset_id, baseline, registry)
        _audit_candidate(dataset_id, candidate)
        _audit_replicates(dataset_id, dataset)
    return {
        "status": "pass",
        "summary_sha256": _sha256_file(summary_path),
        "dataset_count": len(datasets),
        "replicate_count": sum(
            len(dataset["replicates"])
            for dataset in datasets.values()
        ),
        "promotion_eligible": False,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Audit the definitive-expert evidence package."""

    args = build_parser().parse_args(argv)
    try:
        receipt = audit(args.summary.resolve())
    except (AuditError, OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
