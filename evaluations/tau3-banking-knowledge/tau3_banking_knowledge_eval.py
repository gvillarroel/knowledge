#!/usr/bin/env python3
"""Prepare and evaluate local classical knowledge skills on tau3 banking tasks."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


EVALUATION_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = EVALUATION_ROOT.parents[1]
DESCRIPTOR_PATH = EVALUATION_ROOT / "descriptor.json"
DEFAULT_GENERATED_ROOT = (
    REPOSITORY_ROOT
    / "evaluations"
    / "semantic-okf-datasets"
    / "generated"
    / "external"
    / "tau3-banking-knowledge-evaluation-v5"
)
STATIC_INPUTS = (
    "descriptor.json",
    "source-combination.json",
    "guidance.md",
)
RUNTIME_MODULE_NAMES = (
    "_classical_snapshot",
    "_context_projection",
    "_knowledge_skill",
    "_semantic_okf",
)


class EvaluationError(RuntimeError):
    """Describe one reproducibility or evaluation contract failure."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"Cannot read JSON from {path}: {exc}") from exc


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def tree_digest(root: Path, files: Iterable[Path] | None = None) -> tuple[str, int]:
    """Return a path-sensitive SHA-256 digest and file count."""

    selected = sorted(
        (files if files is not None else (path for path in root.rglob("*") if path.is_file())),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    digest = hashlib.sha256()
    for path in selected:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest(), len(selected)


def _descriptor() -> dict[str, Any]:
    descriptor = _load_json(DESCRIPTOR_PATH)
    if not isinstance(descriptor, dict):
        raise EvaluationError("descriptor.json must contain an object")
    return descriptor


def _resolved_project_path(relative: str) -> Path:
    candidate = (REPOSITORY_ROOT / relative).resolve()
    try:
        candidate.relative_to(REPOSITORY_ROOT.resolve())
    except ValueError as exc:
        raise EvaluationError(f"Configured path escapes the repository: {relative}") from exc
    return candidate


def _git_head(clone: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(clone), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise EvaluationError(f"Cannot resolve upstream Git HEAD: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _validate_document(path: Path, payload: Any) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise EvaluationError(f"Document must be an object: {path}")
    required = {"id", "title", "content"}
    if not required.issubset(payload):
        raise EvaluationError(f"Document is missing {sorted(required - set(payload))}: {path}")
    projected = {key: payload[key] for key in ("id", "title", "content")}
    if any(not isinstance(value, str) or not value.strip() for value in projected.values()):
        raise EvaluationError(f"Document id, title, and content must be nonempty strings: {path}")
    if projected["id"] != path.stem:
        raise EvaluationError(f"Document filename/id mismatch: {path}")
    return projected


def normalize_source_id(record_id: str) -> str:
    """Map one upstream record identity to a closed Semantic OKF source id."""

    source_id = re.sub(r"[^a-z0-9]+", "-", record_id.lower()).strip("-")
    if not source_id:
        raise EvaluationError(f"Record id cannot form a valid source id: {record_id!r}")
    return source_id


def _load_documents(document_dir: Path) -> tuple[list[dict[str, str]], dict[str, Path]]:
    paths = sorted(document_dir.glob("*.json"), key=lambda path: path.name)
    documents = [_validate_document(path, _load_json(path)) for path in paths]
    by_id: dict[str, Path] = {}
    for path, document in zip(paths, documents, strict=True):
        document_id = document["id"]
        if document_id in by_id:
            raise EvaluationError(f"Duplicate document id: {document_id}")
        by_id[document_id] = path
    return documents, by_id


def _load_tasks(
    harbor_root: Path,
    upstream_tasks: Path,
    document_ids: set[str],
) -> tuple[list[dict[str, Any]], list[Path]]:
    task_dirs = sorted(
        (path for path in harbor_root.glob("*banking_knowledge*") if path.is_dir()),
        key=lambda path: path.name,
    )
    rows: list[dict[str, Any]] = []
    config_paths: list[Path] = []
    seen: set[str] = set()
    for task_dir in task_dirs:
        config_path = task_dir / "tests" / "config.json"
        config = _load_json(config_path)
        if not isinstance(config, dict) or config.get("domain") != "banking_knowledge":
            raise EvaluationError(f"Unexpected Harbor task configuration: {config_path}")
        task_id = config.get("source_task_id")
        task = config.get("task")
        if not isinstance(task_id, str) or not isinstance(task, dict):
            raise EvaluationError(f"Missing source task identity: {config_path}")
        if task_id in seen:
            raise EvaluationError(f"Duplicate Harbor source task id: {task_id}")
        seen.add(task_id)
        upstream_task = _load_json(upstream_tasks / f"{task_id}.json")
        if task != upstream_task:
            raise EvaluationError(f"Harbor/upstream task drift: {task_id}")
        scenario = task.get("user_scenario")
        query = scenario.get("instructions") if isinstance(scenario, dict) else None
        qrels = task.get("required_documents")
        if not isinstance(query, str) or not query.strip():
            raise EvaluationError(f"Task has no scenario query: {task_id}")
        if not isinstance(qrels, list) or not qrels or any(not isinstance(row, str) for row in qrels):
            raise EvaluationError(f"Task has invalid required_documents: {task_id}")
        missing = sorted(set(qrels) - document_ids)
        if missing:
            raise EvaluationError(f"Task {task_id} references missing documents: {missing}")
        basis = config.get("reward_basis")
        if not isinstance(basis, list) or any(not isinstance(row, str) for row in basis):
            raise EvaluationError(f"Task has invalid reward_basis: {task_id}")
        rows.append(
            {
                "task_id": task_id,
                "query": query,
                "required_documents": qrels,
                "reward_basis": basis,
            }
        )
        config_paths.append(config_path)
    return rows, config_paths


def _prepare_into(destination: Path) -> dict[str, Any]:
    descriptor = _descriptor()
    upstream = descriptor["upstream"]
    harbor = descriptor["harbor_dataset"]
    clone = _resolved_project_path(upstream["clone_directory"])
    harbor_root = _resolved_project_path(upstream["harbor_download_directory"])
    if not clone.is_dir():
        raise EvaluationError(f"Pinned upstream clone is missing: {clone}")
    if not harbor_root.is_dir():
        raise EvaluationError(f"Downloaded Harbor dataset is missing: {harbor_root}")
    actual_commit = _git_head(clone)
    if actual_commit != upstream["commit"]:
        raise EvaluationError(
            f"Upstream commit drift: expected {upstream['commit']}, found {actual_commit}"
        )

    domain_root = clone / "data" / "tau2" / "domains" / "banking_knowledge"
    documents, documents_by_id = _load_documents(domain_root / "documents")
    if len(documents) != upstream["expected_document_count"]:
        raise EvaluationError(
            f"Document count drift: expected {upstream['expected_document_count']}, "
            f"found {len(documents)}"
        )
    tasks, config_paths = _load_tasks(
        harbor_root,
        domain_root / "tasks",
        set(documents_by_id),
    )
    if len(tasks) != harbor["expected_task_count"]:
        raise EvaluationError(
            f"Task count drift: expected {harbor['expected_task_count']}, found {len(tasks)}"
        )

    destination.mkdir(parents=True, exist_ok=False)
    skill_input = destination / "skill-input"
    evaluation_input = destination / "evaluation"
    skill_input.mkdir()
    evaluation_input.mkdir()
    for name in STATIC_INPUTS:
        shutil.copyfile(EVALUATION_ROOT / name, skill_input / name)
    source_dir = skill_input / "sources" / "documents"
    source_dir.mkdir(parents=True)
    source_rows = []
    source_id_by_record_id: dict[str, str] = {}
    seen_source_ids: set[str] = set()
    for document in documents:
        source_id = normalize_source_id(document["id"])
        if source_id in seen_source_ids:
            raise EvaluationError(f"Normalized source id collision: {source_id}")
        source_id_by_record_id[document["id"]] = source_id
        seen_source_ids.add(source_id)
        document_path = source_dir / f"{document['id']}.json"
        document_path.write_text(
            json.dumps(document, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        source_rows.append(
            {
                "id": source_id,
                "kind": "json",
                "path": f"sources/documents/{document['id']}.json",
                "concept_type": "Knowledge Document",
                "ontology_class": "KnowledgeDocument",
                "id_field": "id",
                "title_field": "title",
                "schema": {"id": "string", "title": "string", "content": "string"},
                "fields": {"title": "documentTitle", "content": "documentContent"},
            }
        )
    manifest = _load_json(EVALUATION_ROOT / "manifest-template.json")
    manifest["sources"] = source_rows
    source_ids = [source_id_by_record_id[document["id"]] for document in documents]
    for rule in manifest["rules"]:
        rule["basis"]["references"] = source_ids
    _write_json(skill_input / "manifest.json", manifest)
    plan = _load_json(EVALUATION_ROOT / "classical-plan-template.json")
    plan["selection"]["source_ids"] = source_ids
    _write_json(skill_input / "classical-plan.json", plan)
    combination = _load_json(skill_input / "source-combination.json")
    combination["sources"] = [
        {
            "id": source_id_by_record_id[document["id"]],
            "record_id": document["id"],
            "role": "authoritative",
            "scope": "banking_knowledge",
        }
        for document in documents
    ]
    _write_json(skill_input / "source-combination.json", combination)

    documents_path = evaluation_input / "documents.jsonl"
    documents_path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in documents
        ),
        encoding="utf-8",
        newline="\n",
    )
    tasks_path = evaluation_input / "tasks.jsonl"
    tasks_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in tasks),
        encoding="utf-8",
        newline="\n",
    )

    source_digest, source_count = tree_digest(
        domain_root / "documents", documents_by_id.values()
    )
    task_digest, task_count = tree_digest(harbor_root, config_paths)
    if source_digest != upstream["expected_document_tree_sha256"]:
        raise EvaluationError(
            "Pinned upstream document tree digest drift: "
            f"expected {upstream['expected_document_tree_sha256']}, found {source_digest}"
        )
    if task_digest != harbor["expected_task_config_tree_sha256"]:
        raise EvaluationError(
            "Downloaded Harbor task-config tree digest drift: "
            f"expected {harbor['expected_task_config_tree_sha256']}, found {task_digest}"
        )
    receipt = {
        "schema_version": "tau3-banking-knowledge-preparation/1.0",
        "status": "pass",
        "harbor_dataset": harbor["name"],
        "domain": harbor["domain"],
        "upstream_commit": actual_commit,
        "document_count": len(documents),
        "task_count": len(tasks),
        "source_document_tree_sha256": source_digest,
        "source_document_file_count": source_count,
        "harbor_task_config_tree_sha256": task_digest,
        "harbor_task_config_file_count": task_count,
        "documents_jsonl_sha256": _sha256_file(documents_path),
        "tasks_jsonl_sha256": _sha256_file(tasks_path),
        "skill_input_tree_sha256": tree_digest(skill_input)[0],
        "evaluator_material_in_skill_input": False,
        "source_identity_count": len(source_rows),
        "query_contract": descriptor["retrieval_evaluation"]["query_field"],
        "qrels_contract": descriptor["retrieval_evaluation"]["qrels_field"],
        "harbor_upstream_task_parity": True,
    }
    _write_json(destination / "preparation-receipt.json", receipt)
    return receipt


def prepare(output_dir: Path, *, check: bool) -> dict[str, Any]:
    """Prepare deterministic skill input and qrels from pinned external data."""

    output_dir = output_dir.resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tau3-prepare-", dir=output_dir.parent) as raw:
        candidate = Path(raw) / "input"
        receipt = _prepare_into(candidate)
        candidate_digest, candidate_count = tree_digest(candidate)
        if check:
            if not output_dir.is_dir():
                raise EvaluationError(f"Prepared input is missing for --check: {output_dir}")
            current_digest, current_count = tree_digest(output_dir)
            if (candidate_digest, candidate_count) != (current_digest, current_count):
                raise EvaluationError("Prepared input differs from deterministic regeneration")
            return {**receipt, "mode": "check", "tree_sha256": current_digest}
        if output_dir.exists():
            current_digest, current_count = tree_digest(output_dir)
            if (candidate_digest, candidate_count) != (current_digest, current_count):
                raise EvaluationError(
                    f"Refusing to replace different prepared input: {output_dir}"
                )
            return {**receipt, "mode": "existing", "tree_sha256": current_digest}
        shutil.copytree(candidate, output_dir)
        return {**receipt, "mode": "prepare", "tree_sha256": candidate_digest}


def _run_checked(command: Sequence[str], *, cwd: Path = REPOSITORY_ROOT) -> str:
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise EvaluationError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{detail}")
    return completed.stdout.strip()


def build_experts(input_dir: Path, experts_dir: Path) -> dict[str, Any]:
    """Build, reproduce, deeply validate, and smoke-test both local skills."""

    skill_input = input_dir / "skill-input"
    manifest = skill_input / "manifest.json"
    plan = skill_input / "classical-plan.json"
    guidance = skill_input / "guidance.md"
    configurations = (
        {
            "label": "classical",
            "builder": REPOSITORY_ROOT
            / "skills/build-classical-knowledge-skill/scripts/build_classical_knowledge_skill.py",
            "validator": REPOSITORY_ROOT
            / "skills/build-classical-knowledge-skill/scripts/validate_classical_knowledge_skill.py",
            "output": experts_dir / "rho-bank-classical-expert",
            "name": "rho-bank-classical-expert",
            "description": "Consult the pinned Rho-Bank banking knowledge corpus with verified classical retrieval.",
        },
        {
            "label": "classical-chunked",
            "builder": REPOSITORY_ROOT
            / "skills/build-classical-chunked-knowledge-skill/scripts/build_classical_chunked_knowledge_skill.py",
            "validator": REPOSITORY_ROOT
            / "skills/build-classical-chunked-knowledge-skill/scripts/validate_classical_chunked_knowledge_skill.py",
            "output": experts_dir / "rho-bank-classical-chunked-expert",
            "name": "rho-bank-classical-chunked-expert",
            "description": "Consult the pinned Rho-Bank corpus with verified classical retrieval and budgeted exact chunks.",
        },
    )
    experts_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for configuration in configurations:
        output = configuration["output"]
        command = [
            sys.executable,
            str(configuration["builder"]),
            str(manifest),
            str(plan),
            str(output),
            "--name",
            configuration["name"],
            "--description",
            configuration["description"],
            "--guidance",
            str(guidance),
            "--output-format",
            "json",
        ]
        mode = "check" if output.is_dir() else "build"
        if mode == "check":
            command.append("--check")
        build_output = _run_checked(command)
        _run_checked(
            [sys.executable, str(configuration["validator"]), str(output), "--deep-validation"]
        )
        _run_checked([sys.executable, "-B", str(output / "scripts/runtime_smoke.py")])
        verification = json.loads(
            _run_checked(
                [
                    sys.executable,
                    "-B",
                    str(output / "scripts/query_expert_knowledge.py"),
                    "verify",
                    "--deep-validation",
                ]
            )
        )
        skill_digest, skill_file_count = tree_digest(output)
        rows.append(
            {
                "label": configuration["label"],
                "mode": mode,
                "path": str(output),
                "tree_sha256": skill_digest,
                "file_count": skill_file_count,
                "verification_status": verification.get("status"),
                "build_output": json.loads(build_output),
            }
        )
    receipt = {
        "schema_version": "tau3-banking-knowledge-expert-build/1.0",
        "status": "pass",
        "experts": rows,
    }
    _write_json(experts_dir / "build-receipt.json", receipt)
    return receipt


def ranking_metrics(ranked_ids: Sequence[str], relevant_ids: Sequence[str], cutoff: int) -> dict[str, float]:
    """Compute binary-qrel metrics for one ranking at one cutoff."""

    relevant = set(relevant_ids)
    if not relevant:
        raise EvaluationError("At least one relevant document is required")
    if isinstance(cutoff, bool) or not isinstance(cutoff, int) or cutoff < 1:
        raise EvaluationError("Cutoff must be a positive integer")
    ranking = list(ranked_ids[:cutoff])
    hits = [1 if document_id in relevant else 0 for document_id in ranking]
    hit_count = sum(hits)
    reciprocal_rank = 0.0
    for rank, hit in enumerate(hits, start=1):
        if hit:
            reciprocal_rank = 1.0 / rank
            break
    dcg = sum(hit / math.log2(rank + 1) for rank, hit in enumerate(hits, start=1))
    ideal_hits = min(len(relevant), cutoff)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return {
        "hit": float(bool(hit_count)),
        "recall": hit_count / len(relevant),
        "precision": hit_count / cutoff,
        "mrr": reciprocal_rank,
        "ndcg": dcg / idcg if idcg else 0.0,
        "all_relevant": float(hit_count == len(relevant)),
    }


def _mean(values: Iterable[float]) -> float:
    rows = list(values)
    return sum(rows) / len(rows) if rows else 0.0


def aggregate_rankings(
    rankings: Mapping[str, Sequence[str]],
    tasks: Sequence[Mapping[str, Any]],
    cutoffs: Sequence[int],
) -> dict[str, Any]:
    """Aggregate retrieval metrics across the complete task cohort."""

    per_cutoff: dict[str, Any] = {}
    for cutoff in cutoffs:
        rows = [
            ranking_metrics(
                rankings[str(task["task_id"])],
                task["required_documents"],
                cutoff,
            )
            for task in tasks
        ]
        per_cutoff[str(cutoff)] = {
            key: round(_mean(float(row[key]) for row in rows), 8)
            for key in ("hit", "recall", "precision", "mrr", "ndcg", "all_relevant")
        }
    return per_cutoff


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise EvaluationError(f"Expected object at {path}:{line_number}")
        rows.append(value)
    return rows


def _load_expert_module(expert: Path, unique_name: str) -> Any:
    scripts = expert / "scripts"
    query_script = scripts / "query_expert_knowledge.py"
    if not query_script.is_file():
        raise EvaluationError(f"Generated expert query runtime is missing: {query_script}")
    for name in RUNTIME_MODULE_NAMES:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(scripts))
    previous_bytecode_setting = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(unique_name, query_script)
        if spec is None or spec.loader is None:
            raise EvaluationError(f"Cannot load generated expert runtime: {query_script}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
        sys.path.remove(str(scripts))


def _evaluate_expert(
    expert: Path,
    tasks: Sequence[Mapping[str, Any]],
    modes: Sequence[str],
    cutoffs: Sequence[int],
) -> tuple[dict[str, Any], dict[str, dict[str, list[str]]]]:
    module = _load_expert_module(expert, f"tau3_expert_{hashlib.sha256(str(expert).encode()).hexdigest()[:12]}")
    started = time.perf_counter()
    verified = module._verify(deep_validation=True)
    if len(verified) == 4:
        _, snapshot, rows, verification = verified
        projection = None
    elif len(verified) == 5:
        _, snapshot, rows, projection, verification = verified
    else:
        raise EvaluationError(f"Unexpected generated expert verification tuple: {expert}")
    max_cutoff = max(cutoffs)
    rankings_by_mode: dict[str, dict[str, list[str]]] = {}
    summaries: dict[str, Any] = {}
    for mode in modes:
        rankings: dict[str, list[str]] = {}
        for task in tasks:
            payload = module.search_snapshot(
                snapshot,
                str(task["query"]),
                mode,
                max_cutoff,
                source_ids=(),
                concept_ids=(),
                concept_types=(),
            )
            rankings[str(task["task_id"])] = [
                str(row["record_id"]) for row in payload["results"]
            ]
        rankings_by_mode[mode] = rankings
        summaries[mode] = aggregate_rankings(rankings, tasks, cutoffs)

    context_summary = None
    if projection is not None:
        recalls = []
        hits = []
        all_relevant = []
        used_tokens = []
        returned_chunks = []
        complete_guards = []
        per_task = []
        for task in tasks:
            payload = module.select_context(
                snapshot,
                projection,
                rows,
                str(task["query"]),
                "fusion",
                budget_tokens=None,
                maximum_chunks=None,
                source_ids=(),
                concept_ids=(),
                concept_types=(),
            )
            selected_ids = list(dict.fromkeys(str(row["record_id"]) for row in payload["chunks"]))
            relevant = set(task["required_documents"])
            selected_relevant = relevant.intersection(selected_ids)
            recall = len(selected_relevant) / len(relevant)
            recalls.append(recall)
            hits.append(float(bool(selected_relevant)))
            all_relevant.append(float(selected_relevant == relevant))
            used_tokens.append(float(payload["budget"]["used_tokens"]))
            returned_chunks.append(float(payload["budget"]["returned_chunks"]))
            complete_guards.append(float(bool(payload["quality_guard"]["complete"])))
            per_task.append(
                {
                    "task_id": task["task_id"],
                    "relevant_recall": round(recall, 8),
                    "used_tokens": payload["budget"]["used_tokens"],
                    "returned_chunks": payload["budget"]["returned_chunks"],
                    "quality_guard_complete": bool(payload["quality_guard"]["complete"]),
                }
            )
        context_summary = {
            "mode": "fusion",
            "mean_relevant_recall": round(_mean(recalls), 8),
            "hit_rate": round(_mean(hits), 8),
            "all_relevant_rate": round(_mean(all_relevant), 8),
            "mean_used_tokens": round(_mean(used_tokens), 2),
            "mean_returned_chunks": round(_mean(returned_chunks), 2),
            "quality_guard_complete_rate": round(_mean(complete_guards), 8),
            "per_task": per_task,
        }
    elapsed = time.perf_counter() - started
    return (
        {
            "skill_name": verification["skill_name"],
            "knowledge_tree_sha256": verification["knowledge_tree_sha256"],
            "task_count": len(tasks),
            "elapsed_seconds": round(elapsed, 3),
            "retrieval": summaries,
            "context": context_summary,
        },
        rankings_by_mode,
    )


def _official_bm25_rankings(
    documents: Sequence[Mapping[str, Any]],
    tasks: Sequence[Mapping[str, Any]],
    top_k: int,
) -> dict[str, list[str]]:
    try:
        from rank_bm25 import BM25Okapi
    except ImportError as exc:
        raise EvaluationError(
            "The exact upstream BM25 baseline requires rank-bm25; run with "
            "`uv run --with rank-bm25 python ...`."
        ) from exc
    document_ids = [str(row["id"]) for row in documents]
    corpus = [str(row["content"]).lower().split() for row in documents]
    index = BM25Okapi(corpus)
    rankings = {}
    for task in tasks:
        scores = index.get_scores(str(task["query"]).lower().split())
        order = sorted(range(len(scores)), key=lambda index_: scores[index_], reverse=True)
        rankings[str(task["task_id"])] = [document_ids[index_] for index_ in order[:top_k]]
    return rankings


def evaluate(input_dir: Path, experts_dir: Path, output_path: Path) -> dict[str, Any]:
    """Evaluate both generated experts and the exact upstream BM25 baseline."""

    descriptor = _load_json(input_dir / "skill-input" / "descriptor.json")
    preparation = _load_json(input_dir / "preparation-receipt.json")
    tasks = _load_jsonl(input_dir / "evaluation" / "tasks.jsonl")
    documents = _load_jsonl(input_dir / "evaluation" / "documents.jsonl")
    modes = descriptor["retrieval_evaluation"]["modes"]
    cutoffs = descriptor["retrieval_evaluation"]["cutoffs"]
    expert_paths = (
        experts_dir / "rho-bank-classical-expert",
        experts_dir / "rho-bank-classical-chunked-expert",
    )
    expert_rows = []
    rankings = []
    for expert in expert_paths:
        summary, expert_rankings = _evaluate_expert(expert, tasks, modes, cutoffs)
        expert_rows.append(summary)
        rankings.append(expert_rankings)
    parity_by_mode = {
        mode: all(
            rankings[0][mode][str(task["task_id"])]
            == rankings[1][mode][str(task["task_id"])]
            for task in tasks
        )
        for mode in modes
    }
    baseline_rankings = _official_bm25_rankings(documents, tasks, max(cutoffs))
    baseline = aggregate_rankings(baseline_rankings, tasks, cutoffs)
    payload = {
        "schema_version": "tau3-banking-knowledge-retrieval-evaluation/1.0",
        "status": "pass",
        "evaluation_kind": "retrospective-oracle-context-retrieval-diagnostic",
        "official_tau3_end_to_end_score": None,
        "official_tau3_end_to_end_status": (
            "not-run: OPENAI_API_KEY is required by the tau3 user simulator and verifier"
            if not os.environ.get("OPENAI_API_KEY")
            else "not-run: retrieval diagnostic command does not launch model-judged conversations"
        ),
        "task_count": len(tasks),
        "document_count": len(documents),
        "query_field": descriptor["retrieval_evaluation"]["query_field"],
        "qrels_field": descriptor["retrieval_evaluation"]["qrels_field"],
        "preparation": preparation,
        "upstream_bm25_baseline": {
            "implementation": "rank_bm25.BM25Okapi with upstream lowercase-whitespace tokenization",
            "retrieval": baseline,
        },
        "experts": expert_rows,
        "classical_chunked_full_ranking_parity": parity_by_mode,
        "limitations": [
            "The scenario instruction is an oracle-context query available only after all relevant customer facts have been elicited.",
            "Required-document qrels evaluate retrieval mechanics, not answer correctness, tool use, or conversational policy compliance.",
            "The public Harbor tasks clone upstream tau2-bench without a commit pin; this evaluation separately pins and parity-checks the exact upstream commit.",
            "This retrospective diagnostic cannot be used as sealed validation or promotion evidence after its qrels have been inspected.",
        ],
    }
    _write_json(output_path, payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="Prepare deterministic local input")
    prepare_parser.add_argument("--output-dir", type=Path, default=DEFAULT_GENERATED_ROOT / "input")
    prepare_parser.add_argument("--check", action="store_true")
    build_parser = commands.add_parser("build", help="Build and validate both local expert skills")
    build_parser.add_argument("--input-dir", type=Path, default=DEFAULT_GENERATED_ROOT / "input")
    build_parser.add_argument("--experts-dir", type=Path, default=DEFAULT_GENERATED_ROOT / "experts")
    evaluate_parser = commands.add_parser("evaluate", help="Run qrel retrieval diagnostics")
    evaluate_parser.add_argument("--input-dir", type=Path, default=DEFAULT_GENERATED_ROOT / "input")
    evaluate_parser.add_argument("--experts-dir", type=Path, default=DEFAULT_GENERATED_ROOT / "experts")
    evaluate_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_GENERATED_ROOT / "reports" / "retrieval-evaluation.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            payload = prepare(args.output_dir, check=args.check)
        elif args.command == "build":
            payload = build_experts(args.input_dir.resolve(), args.experts_dir.resolve())
        else:
            payload = evaluate(
                args.input_dir.resolve(),
                args.experts_dir.resolve(),
                args.output.resolve(),
            )
    except (EvaluationError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
