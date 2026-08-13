#!/usr/bin/env python3
"""Prove direct expert parity with every canonical Semantic OKF skill pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "integrated-semantic-okf-knowledge-skill-comparison/1.0"
EXPECTED_QUESTIONS = 40
TOP_K = 5
LOCATION_FIELDS = {
    "logical_concept_path",
    "physical_concept_path",
    "evidence_path",
    "evidence_anchor",
    "citation",
}
DATASETS = {
    "astro": "astro-40",
    "graphrag": "graphrag-papers-40",
    "qec": "quantum-error-correction-papers-40",
}
PROBE_QUERIES = {
    "astro-40": "component",
    "graphrag-papers-40": "graph",
    "quantum-error-correction-papers-40": "surface",
}
FAMILIES = (
    "legacy",
    "embeddings",
    "classical",
    "adaptive",
    "entity-graph",
    "ensemble",
    "graphify",
    "turso",
)


class ComparisonError(ValueError):
    """Describe an invalid artifact or a mechanical parity failure."""


def canonical_json(value: Any) -> str:
    """Serialize deterministic JSON and reject non-finite values."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    """Return one lowercase SHA-256 digest."""

    return hashlib.sha256(value).hexdigest()


def regular_files(root: Path) -> list[Path]:
    """Return one closed tree of regular files in cross-platform order."""

    if not root.is_dir() or root.is_symlink():
        raise ComparisonError(f"Directory is absent or unsafe: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ComparisonError(f"Symlink is not allowed: {path}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ComparisonError(f"Special file is not allowed: {path}")
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def tree_binding(root: Path) -> tuple[str, dict[str, str]]:
    """Bind relative paths, lengths, and exact bytes for one tree."""

    digest = hashlib.sha256()
    files: dict[str, str] = {}
    for path in regular_files(root):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
        files[relative] = sha256_bytes(data)
    return digest.hexdigest(), files


def mapped_tree(mappings: Sequence[tuple[str, Path]]) -> dict[str, str]:
    """Project several source trees onto their generated relative locations."""

    result: dict[str, str] = {}
    for prefix, source in mappings:
        if source.is_file() and not source.is_symlink():
            result[prefix] = sha256_bytes(source.read_bytes())
            continue
        for path in regular_files(source):
            relative = path.relative_to(source).as_posix()
            projected = f"{prefix}/{relative}" if prefix else relative
            if projected in result:
                raise ComparisonError(f"Duplicate projected consultation file: {projected}")
            result[projected] = sha256_bytes(path.read_bytes())
    return result


def question_rows(repo: Path, dataset_id: str) -> tuple[list[dict[str, Any]], str]:
    """Load and digest-bind one registered canonical question set."""

    descriptor_path = repo / "evaluations/semantic-okf-datasets/datasets" / f"{dataset_id}.json"
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    question_contract = descriptor.get("questions")
    if not isinstance(question_contract, dict):
        raise ComparisonError(f"Question contract is absent for {dataset_id}")
    relative = question_contract.get("path")
    expected_digest = question_contract.get("sha256")
    if not isinstance(relative, str) or not isinstance(expected_digest, str):
        raise ComparisonError(f"Question contract is invalid for {dataset_id}")
    path = repo.joinpath(*PurePosixPath(relative).parts)
    if path.is_symlink() or not path.is_file():
        raise ComparisonError(f"Question set is absent or unsafe: {path}")
    payload = path.read_bytes()
    actual_digest = sha256_bytes(payload)
    if actual_digest != expected_digest:
        raise ComparisonError(f"Question digest drift for {dataset_id}")
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(payload.decode("utf-8").splitlines(), 1):
        if not raw:
            raise ComparisonError(f"Blank question line at {path}:{number}")
        value = json.loads(raw)
        if not isinstance(value, dict) or not isinstance(value.get("question"), str):
            raise ComparisonError(f"Invalid question at {path}:{number}")
        rows.append(value)
    if len(rows) != EXPECTED_QUESTIONS:
        raise ComparisonError(
            f"Expected {EXPECTED_QUESTIONS} questions for {dataset_id}; found {len(rows)}"
        )
    identifiers = [row.get("id") for row in rows]
    if any(not isinstance(value, str) or not value for value in identifiers):
        raise ComparisonError(f"Invalid question IDs for {dataset_id}")
    if len(set(identifiers)) != len(identifiers):
        raise ComparisonError(f"Duplicate question IDs for {dataset_id}")
    return rows, actual_digest


def native_target(knowledge: Path, family: Mapping[str, Any]) -> Path:
    """Resolve the exact target declared by one family contract."""

    target = family.get("target")
    if target == "bundle":
        return knowledge
    if not isinstance(target, str):
        raise ComparisonError("Family target is invalid")
    return knowledge.joinpath(*PurePosixPath(target).parts)


def native_arguments(
    family: Mapping[str, Any],
    knowledge: Path,
    query: str,
) -> list[str]:
    """Create the exact default-route CLI used by the generated façade."""

    family_id = family["id"]
    mode = family["default_mode"]
    target = str(native_target(knowledge, family))
    if family_id == "legacy":
        return [
            target,
            "ledger",
            "--contains",
            query,
            "--limit",
            str(TOP_K),
            "--validate",
            "--format",
            "json",
        ]
    if family_id in {"embeddings", "classical", "adaptive"}:
        return [
            target,
            "search",
            "--query",
            query,
            "--mode",
            mode,
            "--top-k",
            str(TOP_K),
        ]
    if family_id == "entity-graph":
        return [
            target,
            "search",
            "--query",
            query,
            "--mode",
            mode,
            "--top-k",
            str(TOP_K),
        ]
    if family_id == "ensemble":
        return [
            target,
            "search",
            "--query",
            query,
            "--policy",
            mode,
            "--top-k",
            str(TOP_K),
        ]
    if family_id == "graphify":
        return [
            "--format",
            "json",
            target,
            "search",
            query,
            "--top-k",
            str(TOP_K),
            "--show-content",
        ]
    if family_id == "turso":
        return [
            target,
            "records",
            "--contains",
            query,
            "--show-body",
            "--limit",
            str(TOP_K),
            "--format",
            "json",
        ]
    raise ComparisonError(f"Unsupported family: {family_id!r}")


def offline_environment() -> dict[str, str]:
    """Return a deterministic offline subprocess environment without auth tokens."""

    environment = os.environ.copy()
    for key in (
        "HF_TOKEN",
        "HUGGING_FACE_HUB_TOKEN",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        environment.pop(key, None)
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "TOKENIZERS_PARALLELISM": "false",
        }
    )
    return environment


def run_json(
    python: Path,
    script: Path,
    arguments: Sequence[str],
) -> dict[str, Any]:
    """Run one local consultation command and return its object payload."""

    completed = subprocess.run(
        [str(python), "-B", str(script), *arguments],
        cwd=script.parent,
        env=offline_environment(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
        timeout=600,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise ComparisonError(
            f"Consultation failed ({completed.returncode}) for {script}: {detail[-2000:]}"
        )
    value = json.loads(completed.stdout)
    if not isinstance(value, dict) or value.get("status") == "error":
        raise ComparisonError(f"Consultation returned an invalid payload: {script}")
    return value


def strip_enrichment(value: Any, *, root: bool = True) -> Any:
    """Remove only the stable façade's added expert and location fields."""

    if isinstance(value, list):
        return [strip_enrichment(item, root=False) for item in value]
    if not isinstance(value, dict):
        return value
    result = {
        key: strip_enrichment(item, root=False)
        for key, item in value.items()
        if key not in LOCATION_FIELDS and not (root and key == "expert")
    }
    return result


def result_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return the top-level native result array used by the façade contract."""

    value = payload.get("results")
    if value is None:
        value = payload.get("hits")
    if value is None:
        value = payload.get("records")
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ComparisonError("Search payload has no valid result array")
    return value


def verify_citations(expert: Path, rows: Iterable[Mapping[str, Any]]) -> int:
    """Require every retained result to resolve to exact local Markdown evidence."""

    count = 0
    for row in rows:
        citation = row.get("citation")
        if not isinstance(citation, str) or not citation.startswith("references/knowledge/"):
            raise ComparisonError("Generated result has no physical evidence citation")
        raw_path, separator, anchor = citation.partition("#")
        target = expert.joinpath(*PurePosixPath(raw_path).parts)
        if target.is_symlink() or not target.is_file():
            raise ComparisonError(f"Citation target is absent or unsafe: {citation}")
        if separator:
            marker = f'<a id="{anchor}"></a>'
            if marker not in target.read_text(encoding="utf-8"):
                raise ComparisonError(f"Citation anchor is absent: {citation}")
        count += 1
    return count


def compare_case(
    repo: Path,
    study: Path,
    alias: str,
    dataset_id: str,
    family_id: str,
    python: Path,
) -> dict[str, Any]:
    """Compare one generated expert with its exact separate build/consult stack."""

    questions, question_digest = question_rows(repo, dataset_id)
    expert = study / alias / f"{alias}-{family_id}-expert"
    baseline = study / alias / f"{alias}-{family_id}-baseline"
    knowledge = expert / "references" / "knowledge"
    manifest_path = expert / "expert-manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ComparisonError(f"Generated expert manifest is absent: {expert}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    family = manifest.get("family")
    if not isinstance(family, dict) or family.get("id") != family_id:
        raise ComparisonError(f"Generated family binding drift: {expert}")

    baseline_sha256, baseline_files = tree_binding(baseline)
    knowledge_sha256, knowledge_files = tree_binding(knowledge)
    if baseline_sha256 != knowledge_sha256 or baseline_files != knowledge_files:
        raise ComparisonError(f"Knowledge byte drift for {dataset_id}/{family_id}")
    declared_tree = manifest.get("knowledge", {}).get("tree", {})
    if declared_tree.get("sha256") != knowledge_sha256:
        raise ComparisonError(f"Generated knowledge binding drift for {dataset_id}/{family_id}")

    consult_name = family.get("consult_skill")
    if not isinstance(consult_name, str):
        raise ComparisonError(f"Consult skill binding is invalid for {dataset_id}/{family_id}")
    consult = repo / "skills" / consult_name
    expected_consultation = mapped_tree(
        (
            ("references/consultation/SKILL.md", consult / "SKILL.md"),
            ("references/consultation/references", consult / "references"),
            ("scripts/native", consult / "scripts"),
        ),
    )
    actual_consultation = mapped_tree(
        (
            ("references/consultation/SKILL.md", expert / "references/consultation/SKILL.md"),
            ("references/consultation/references", expert / "references/consultation/references"),
            ("scripts/native", expert / "scripts/native"),
        ),
    )
    if expected_consultation != actual_consultation:
        raise ComparisonError(f"Consultation package drift for {dataset_id}/{family_id}")

    query = PROBE_QUERIES[dataset_id]
    native_name = family.get("query_script")
    if not isinstance(native_name, str):
        raise ComparisonError(f"Native query binding is invalid for {dataset_id}/{family_id}")
    separate_payload = run_json(
        python,
        consult / "scripts" / native_name,
        native_arguments(family, baseline, query),
    )
    facade_payload = run_json(
        python,
        expert / "scripts/query_expert_knowledge.py",
        ["search", "--query", query, "--top-k", str(TOP_K)],
    )
    packaged_payload = strip_enrichment(facade_payload)
    if canonical_json(separate_payload) != canonical_json(packaged_payload):
        raise ComparisonError(
            f"Native or façade payload drift for {dataset_id}/{family_id}"
        )
    hits = result_rows(facade_payload)
    if not hits:
        raise ComparisonError(f"Default query returned no evidence for {dataset_id}/{family_id}")
    citation_count = verify_citations(expert, hits)

    ledger = knowledge / "semantic/records.jsonl"
    first_record = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    exact = run_json(
        python,
        expert / "scripts/query_expert_knowledge.py",
        [
            "get",
            "--source-id",
            first_record["source_id"],
            "--record-id",
            first_record["record_id"],
            "--show-content",
        ],
    )
    returned = exact.get("record")
    if not isinstance(returned, dict) or returned.get("body") != first_record.get("body"):
        raise ComparisonError(f"Exact record lookup drift for {dataset_id}/{family_id}")
    verify_citations(expert, [returned])

    return {
        "dataset_id": dataset_id,
        "family": family_id,
        "default_mode": family["default_mode"],
        "question_count": len(questions),
        "question_sha256": question_digest,
        "probe_query": query,
        "authoritative_records": manifest["knowledge"]["record_count"],
        "knowledge_files": len(knowledge_files),
        "knowledge_tree_sha256": knowledge_sha256,
        "knowledge_bytes_equal": True,
        "consultation_files": len(expected_consultation),
        "consultation_bytes_equal": True,
        "native_payload_equal": True,
        "facade_payload_equal_before_enrichment": True,
        "default_query_hits": len(hits),
        "verified_hit_citations": citation_count,
        "exact_get_verified": True,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Create one deterministic cross-family comparison report."""

    totals = {
        "dataset_count": len({row["dataset_id"] for row in rows}),
        "family_count": len({row["family"] for row in rows}),
        "dataset_family_cells": len(rows),
        "bound_question_cells": sum(row["question_count"] for row in rows),
        "authoritative_record_instances": sum(row["authoritative_records"] for row in rows),
        "knowledge_file_instances": sum(row["knowledge_files"] for row in rows),
        "consultation_file_instances": sum(row["consultation_files"] for row in rows),
        "native_query_probe_cells": sum(int(row["native_payload_equal"]) for row in rows),
        "facade_query_probe_cells": sum(
            int(row["facade_payload_equal_before_enrichment"]) for row in rows
        ),
        "returned_hits": sum(row["default_query_hits"] for row in rows),
        "verified_hit_citations": sum(row["verified_hit_citations"] for row in rows),
        "exact_get_cells": sum(int(row["exact_get_verified"]) for row in rows),
        "knowledge_mismatches": sum(not row["knowledge_bytes_equal"] for row in rows),
        "consultation_mismatches": sum(not row["consultation_bytes_equal"] for row in rows),
        "native_payload_mismatches": sum(not row["native_payload_equal"] for row in rows),
        "facade_payload_mismatches": sum(
            not row["facade_payload_equal_before_enrichment"] for row in rows
        ),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "comparison": {
            "baseline": "exact separate canonical builder and consultant pair",
            "candidate": "build-semantic-okf-knowledge-skill generated expert",
            "concept_layout": "source-packed-v1",
            "top_k": TOP_K,
            "families": list(FAMILIES),
            "mechanical_equivalence": (
                "Complete knowledge-tree byte equality plus complete consultation-instruction, "
                "reference, and runtime byte equality establishes behavior equality for every "
                "bound question. One default-route native and façade payload is additionally "
                "executed per dataset-family cell."
            ),
        },
        "datasets": rows,
        "totals": totals,
        "boundary": (
            "This is a deterministic build, consultation-runtime, query-façade, and citation "
            "parity evaluation. It is not a new model-judged Harbor answer-quality run."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render a compact evidence-first report."""

    lines = [
        "# Canonical Multi-Family Direct Knowledge Skill Parity Verification",
        "",
        "| Dataset | Family | Records | Knowledge files | Consult files | Native query | Façade | Hit citations | Exact get |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["datasets"]:
        lines.append(
            "| {dataset_id} | {family} | {authoritative_records} | "
            "{knowledge_files}/{knowledge_files} | {consultation_files}/{consultation_files} | "
            "1/1 | 1/1 | {verified_hit_citations}/{default_query_hits} | 1/1 |".format(**row)
        )
    totals = report["totals"]
    lines.extend(
        [
            "",
            (
                f"Result: **PASS** across {totals['dataset_family_cells']} dataset-family cells, "
                f"{totals['family_count']} canonical families, and "
                f"{totals['bound_question_cells']} bound question cells. All complete knowledge "
                "trees and matched consultation packages are byte-identical to the separate stack."
            ),
            "",
            (
                f"All {totals['native_query_probe_cells']} separate-versus-packaged native query "
                f"probes and all {totals['facade_query_probe_cells']} façade projections matched. "
                f"All {totals['verified_hit_citations']} retained hits and "
                f"{totals['exact_get_cells']} exact-record probes resolved locally."
            ),
            "",
            f"Equivalence basis: {report['comparison']['mechanical_equivalence']}",
            "",
            f"Boundary: {report['boundary']}",
            "",
        ]
    )
    return "\n".join(lines)


def write_or_check(path: Path, payload: bytes, *, check: bool) -> None:
    """Write one report atomically or require exact reproduction."""

    if check:
        if path.is_symlink() or not path.is_file() or path.read_bytes() != payload:
            raise ComparisonError(f"Report drift: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    repo = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo)
    parser.add_argument(
        "--study-root",
        type=Path,
        default=(
            repo
            / "evaluations/semantic-okf-datasets/generated/"
            "integrated-family-validation-20260813-02"
        ),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=(
            repo
            / "evaluations/integrated-semantic-okf-knowledge-skill/reports/"
            "20260813-parity-verification.json"
        ),
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=(
            repo
            / "evaluations/integrated-semantic-okf-knowledge-skill/reports/"
            "20260813-parity-verification.md"
        ),
    )
    parser.add_argument(
        "--base-python",
        type=Path,
        default=Path(sys.executable),
        help="Interpreter with the baseline, Graphify, and Turso locks",
    )
    parser.add_argument(
        "--model-python",
        type=Path,
        default=Path(sys.executable),
        help="Interpreter with the embedding and ensemble optional locks",
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Compare all canonical dataset-family cells and publish reports."""

    args = parse_args()
    repo = args.repo_root.resolve()
    study = args.study_root.resolve()
    if not repo.is_dir() or repo.is_symlink():
        raise ComparisonError(f"Repository root is absent or unsafe: {repo}")
    if not study.is_dir() or study.is_symlink():
        raise ComparisonError(f"Study root is absent or unsafe: {study}")
    base_python = args.base_python.resolve()
    model_python = args.model_python.resolve()
    for label, python in (("base", base_python), ("model", model_python)):
        if python.is_symlink() or not python.is_file():
            raise ComparisonError(f"{label.capitalize()} Python is absent or unsafe: {python}")
    rows = [
        compare_case(
            repo,
            study,
            alias,
            dataset_id,
            family,
            model_python if family in {"embeddings", "ensemble"} else base_python,
        )
        for alias, dataset_id in DATASETS.items()
        for family in FAMILIES
    ]
    report = summarize(rows)
    json_payload = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    markdown_payload = render_markdown(report).encode("utf-8")
    write_or_check(args.output_json.resolve(), json_payload, check=args.check)
    write_or_check(args.output_markdown.resolve(), markdown_payload, check=args.check)
    print(canonical_json(report["totals"]))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ComparisonError, OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        print(
            canonical_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "error",
                    "error": str(exc),
                }
            ),
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
