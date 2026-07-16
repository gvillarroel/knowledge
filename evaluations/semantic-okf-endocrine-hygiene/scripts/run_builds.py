#!/usr/bin/env python3
"""Build every Semantic OKF baseline twice and publish an append-only audit run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


EVALUATION = Path(__file__).resolve().parents[1]
REPO_ROOT = EVALUATION.parents[1]
PLANS = EVALUATION / "plans"
DEFAULT_MANIFEST = EVALUATION / "corpus" / "manifest.json"
DEFAULT_RUNS = EVALUATION / "results" / "runs"
DEFAULT_JSON_REPORT = EVALUATION / "reports" / "build-comparison.json"
DEFAULT_MARKDOWN_REPORT = EVALUATION / "reports" / "build-comparison.md"
DEFAULT_PYTHON = (
    REPO_ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
)
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PMCID_RE = re.compile(r"^PMC[1-9][0-9]*$")
ARXIV_VERSION_RE = re.compile(r"(?<![0-9])\d{4}\.\d{4,5}v[1-9][0-9]*(?![0-9])")
DERIVED_ROOTS = frozenset({"adaptive", "classical", "ensemble", "entity-graph", "retrieval"})
REPORT_SCHEMA = "semantic-okf-endocrine-hygiene-build-comparison/1.0"
RUN_SCHEMA = "semantic-okf-endocrine-hygiene-build-run/1.0"


class BuildRunError(RuntimeError):
    """Describe an invalid evaluation input or unsafe publication request."""


@dataclass(frozen=True)
class Family:
    """Describe one unchanged builder and its expected corpus compatibility."""

    name: str
    plan: str | None
    builder: str
    validator: str
    deep_validator: str | None
    expected: str
    failure_patterns: tuple[str, ...] = ()


FAMILIES = (
    Family(
        "legacy",
        None,
        "skills/build-semantic-okf/scripts/build_semantic_okf.py",
        "skills/build-semantic-okf/scripts/validate_semantic_okf.py",
        None,
        "success",
    ),
    Family(
        "embeddings",
        "embedding-plan.json",
        "skills/build-semantic-okf-embeddings/scripts/build_semantic_okf_embeddings.py",
        "skills/build-semantic-okf-embeddings/scripts/validate_semantic_okf_embeddings.py",
        "skills/build-semantic-okf-embeddings/scripts/validate_okf_bundle.py",
        "success",
    ),
    Family(
        "classical",
        "classical-plan.json",
        "skills/build-semantic-okf-classical/scripts/build_semantic_okf_classical.py",
        "skills/build-semantic-okf-classical/scripts/validate_semantic_okf_classical.py",
        "skills/build-semantic-okf-classical/scripts/validate_okf_bundle.py",
        "success",
    ),
    Family(
        "entity-graph",
        "entity-graph-plan.json",
        "skills/build-semantic-okf-entity-graph/scripts/build_semantic_okf_entity_graph.py",
        "skills/build-semantic-okf-entity-graph/scripts/validate_semantic_okf_entity_graph.py",
        "skills/build-semantic-okf-entity-graph/scripts/validate_okf_bundle.py",
        "incompatible",
        ("has no PDF page headings",),
    ),
    Family(
        "adaptive",
        "adaptive-plan.json",
        "skills/build-semantic-okf-adaptive/scripts/build_semantic_okf_adaptive.py",
        "skills/build-semantic-okf-adaptive/scripts/validate_semantic_okf_adaptive.py",
        "skills/build-semantic-okf-adaptive/scripts/validate_okf_bundle.py",
        "success",
    ),
    Family(
        "ensemble",
        "ensemble-plan.json",
        "skills/build-semantic-okf-ensemble/scripts/build_semantic_okf_ensemble.py",
        "skills/build-semantic-okf-ensemble/scripts/validate_semantic_okf_ensemble.py",
        "skills/build-semantic-okf-ensemble/scripts/validate_okf_bundle.py",
        "incompatible",
        ("paper identity mappings must contain canonical versioned arXiv IDs",),
    ),
)


def canonical_json(value: Any) -> str:
    """Serialize a JSON-compatible value for portable logical hashes."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def logical_file_sha256(path: Path) -> str:
    """Hash one file after normalizing line endings across Git platforms."""

    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256_bytes(payload)


def atomic_write(path: Path, payload: str) -> None:
    """Publish one compact report by same-directory atomic replacement."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
    try:
        temporary.write_text(payload, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuildRunError(f"Cannot load JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildRunError(f"Expected a JSON object at {path}")
    return value


def file_binding(path: Path, *, base: Path = REPO_ROOT) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        label = resolved.relative_to(base.resolve()).as_posix()
    except ValueError:
        label = f"external/{resolved.name}"
    return {"path": label, "bytes": resolved.stat().st_size, "sha256": sha256_file(resolved)}


def relative_files(root: Path, *, core_only: bool = False) -> list[str]:
    result = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if core_only and relative.parts and relative.parts[0] in DERIVED_ROOTS:
            continue
        result.append(relative.as_posix())
    return sorted(result)


def logical_tree_sha256(root: Path, paths: Iterable[str]) -> str:
    entries = [
        {"path": relative, "sha256": logical_file_sha256(root / Path(relative))}
        for relative in sorted(paths)
    ]
    return sha256_bytes(canonical_json(entries).encode("utf-8"))


def tree_fingerprint(root: Path) -> dict[str, Any]:
    files = relative_files(root)
    core = relative_files(root, core_only=True)
    records = root / "semantic" / "records.jsonl"
    return {
        "file_count": len(files),
        "total_bytes": sum((root / Path(relative)).stat().st_size for relative in files),
        "logical_tree_sha256": logical_tree_sha256(root, files),
        "core_file_count": len(core),
        "core_total_bytes": sum((root / Path(relative)).stat().st_size for relative in core),
        "logical_core_tree_sha256": logical_tree_sha256(root, core),
        "semantic_records_sha256": sha256_file(records) if records.is_file() else None,
    }


def all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from all_strings(item)


def source_selection(plan: Mapping[str, Any], family: str) -> set[str]:
    """Read source IDs from either a native plan or the local legacy descriptor."""

    if family == "entity-graph":
        selection = plan.get("selection", {})
        return set(selection.get("paper_source_ids", [])) | set(selection.get("claim_source_ids", []))
    if family == "ensemble":
        selection = plan.get("adaptive", {}).get("selection", {})
        return set(selection.get("source_ids", []))
    selection = plan.get("selection", {})
    return set(selection.get("source_ids", []))


def validate_inputs(manifest_path: Path) -> dict[str, Any]:
    """Bind plans to the closed generated corpus without altering baseline schemas."""

    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    sources = manifest.get("sources")
    if manifest.get("schema_version") != "1.0" or not isinstance(sources, list) or not sources:
        raise BuildRunError("The generated corpus manifest is missing its closed source list")
    corpus = manifest_path.parent.resolve()
    source_ids: list[str] = []
    source_files: list[Path] = []
    for number, source in enumerate(sources, start=1):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not isinstance(source.get("path"), str):
            raise BuildRunError(f"Manifest source {number} lacks an id or path")
        source_id = source["id"]
        path = (corpus / source["path"]).resolve()
        try:
            path.relative_to(corpus)
        except ValueError as exc:
            raise BuildRunError(f"Manifest source {source_id} escapes the corpus directory") from exc
        if not path.is_file():
            raise BuildRunError(f"Manifest source {source_id} is missing: {path}")
        source_ids.append(source_id)
        source_files.append(path)
    if source_ids != list(dict.fromkeys(source_ids)):
        raise BuildRunError("Manifest source IDs must be unique")

    source_set = set(source_ids)
    retrieval_set = {item for item in source_set if item != "analysis-vocabulary"}
    expected_pmcids = {
        item.removeprefix("paper-").upper()
        for item in retrieval_set
        if item.startswith("paper-")
    }
    if len(expected_pmcids) != 15 or any(PMCID_RE.fullmatch(item) is None for item in expected_pmcids):
        raise BuildRunError("The manifest must contain exactly 15 real PMCID paper sources")
    expected_retrieval = {
        f"{prefix}-{pmcid.lower()}" for pmcid in expected_pmcids for prefix in ("paper", "claims")
    }
    if retrieval_set != expected_retrieval:
        raise BuildRunError("The manifest must contain one paper and one claims source per PMCID")

    plans: dict[str, Any] = {}
    bindings = []
    for family in FAMILIES:
        filename = family.plan or "legacy-plan.json"
        path = PLANS / filename
        plan = load_json(path)
        plans[family.name] = plan
        bindings.append(file_binding(path))
        selection = source_selection(plan, family.name)
        expected = source_set if family.name == "legacy" else retrieval_set
        if selection != expected:
            raise BuildRunError(
                f"{family.name} source selection differs from the generated corpus; "
                f"missing={sorted(expected - selection)}, unexpected={sorted(selection - expected)}"
            )
        leaked = sorted({value for value in all_strings(plan) if ARXIV_VERSION_RE.search(value)})
        if leaked:
            raise BuildRunError(f"{family.name} plan fabricates versioned arXiv identities: {leaked}")

    entity_selection = plans["entity-graph"]["selection"]
    if entity_selection.get("vocabulary_source_id") != "analysis-vocabulary":
        raise BuildRunError("The entity-graph plan must select the declared auxiliary vocabulary")
    adaptive = plans["adaptive"]
    if adaptive["passages"]["markdown_pdf_page_source_ids"] or adaptive["evidence_identity"]["paper_ids_by_source"]:
        raise BuildRunError("The standalone adaptive baseline must not relabel BioC passages or fabricate native IDs")
    ensemble_map = plans["ensemble"]["adaptive"]["evidence_identity"]["paper_ids_by_source"]
    if set(ensemble_map) != retrieval_set:
        raise BuildRunError("The ensemble incompatibility plan must map every selected source")
    for source_id, pmcid in ensemble_map.items():
        if PMCID_RE.fullmatch(pmcid) is None or not source_id.endswith(pmcid.lower()):
            raise BuildRunError(f"Ensemble identity mapping is not a real source-aligned PMCID: {source_id} -> {pmcid}")

    input_files = [manifest_path, *source_files]
    input_entries = [file_binding(path) for path in sorted(input_files)]
    return {
        "manifest": file_binding(manifest_path),
        "plans": sorted(bindings, key=lambda row: row["path"]),
        "corpus": {
            "paper_count": len(expected_pmcids),
            "source_count": len(source_set),
            "paper_ids": sorted(expected_pmcids),
            "files": input_entries,
            "logical_input_tree_sha256": sha256_bytes(canonical_json(input_entries).encode("utf-8")),
        },
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_run_id() -> str:
    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"


def portable_command(command: Sequence[str], run_stage: Path, final_run: Path) -> list[str]:
    result = []
    stage_label = str(run_stage.resolve())
    final_label = str(final_run.resolve())
    repo_label = str(REPO_ROOT.resolve())
    for item in command:
        rendered = str(item).replace(stage_label, "$RUN").replace(final_label, "$RUN").replace(repo_label, "$REPO")
        if rendered == sys.executable:
            rendered = "$PYTHON"
        result.append(rendered.replace("\\", "/"))
    return result


def sanitized_diagnostic(value: str, run_stage: Path, final_run: Path) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace(str(run_stage.resolve()), "$RUN").replace(str(final_run.resolve()), "$RUN")
    normalized = normalized.replace(str(REPO_ROOT.resolve()), "$REPO")
    lines = [line.rstrip() for line in normalized.splitlines() if line.strip()]
    return "\n".join(lines[-20:])[-4000:]


def execute(
    command: Sequence[str],
    *,
    log_prefix: Path,
    run_stage: Path,
    final_run: Path,
    timeout_seconds: int,
    environment: Mapping[str, str],
) -> dict[str, Any]:
    started = time.perf_counter()
    timed_out = False
    try:
        completed = subprocess.run(
            list(command),
            cwd=REPO_ROOT,
            env=dict(environment),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stderr += f"\nCommand timed out after {timeout_seconds} seconds.\n"
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
    stdout_path = log_prefix.with_suffix(".stdout.txt")
    stderr_path = log_prefix.with_suffix(".stderr.txt")
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    combined = f"{stdout}\n{stderr}"
    return {
        "command": portable_command(command, run_stage, final_run),
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_ms": elapsed_ms,
        "stdout": file_binding(stdout_path, base=run_stage),
        "stderr": file_binding(stderr_path, base=run_stage),
        "diagnostic_excerpt": sanitized_diagnostic(combined, run_stage, final_run),
    }


def build_command(family: Family, manifest: Path, output: Path, python: str) -> list[str]:
    command = [python, str(REPO_ROOT / family.builder), str(manifest)]
    if family.plan is not None:
        command.append(str(PLANS / family.plan))
    command.extend([str(output), "--output-format", "json"])
    return command


def validator_command(script: str, output: Path, python: str, *, deep: bool) -> list[str]:
    command = [python, str(REPO_ROOT / script), str(output)]
    if not deep:
        command.extend(["--output-format", "json"])
    return command


def run_attempt(
    family: Family,
    number: int,
    *,
    manifest: Path,
    stage: Path,
    final_run: Path,
    python: str,
    timeout_seconds: int,
    environment: Mapping[str, str],
) -> dict[str, Any]:
    repetition = "a" if number == 1 else "b"
    output = stage / "bundles" / f"{family.name}-{repetition}"
    logs = stage / "logs" / f"{family.name}-{repetition}"
    build = execute(
        build_command(family, manifest, output, python),
        log_prefix=logs / "build",
        run_stage=stage,
        final_run=final_run,
        timeout_seconds=timeout_seconds,
        environment=environment,
    )
    diagnostic = build["diagnostic_excerpt"]
    matched = next((pattern for pattern in family.failure_patterns if pattern.casefold() in diagnostic.casefold()), None)
    result: dict[str, Any] = {
        "attempt": number,
        "build": build,
        "output_published": output.is_dir(),
        "matched_expected_failure": matched,
        "validators": [],
        "fingerprint": tree_fingerprint(output) if output.is_dir() else None,
    }
    if build["returncode"] == 0 and output.is_dir():
        validators = [(family.validator, False)]
        if family.deep_validator is not None:
            validators.append((family.deep_validator, True))
        for script, deep in validators:
            name = "deep" if deep else "family"
            result["validators"].append(
                {
                    "kind": name,
                    **execute(
                        validator_command(script, output, python, deep=deep),
                        log_prefix=logs / f"validate-{name}",
                        run_stage=stage,
                        final_run=final_run,
                        timeout_seconds=timeout_seconds,
                        environment=environment,
                    ),
                }
            )
    return result


def summarize_family(family: Family, attempts: list[dict[str, Any]]) -> dict[str, Any]:
    builds_pass = all(item["build"]["returncode"] == 0 and item["output_published"] for item in attempts)
    validations_pass = builds_pass and all(
        validator["returncode"] == 0 and not validator["timed_out"]
        for item in attempts
        for validator in item["validators"]
    ) and all(item["validators"] for item in attempts)
    failed_as_expected = all(
        item["build"]["returncode"] not in (0, None)
        and item["matched_expected_failure"] is not None
        for item in attempts
    )
    if builds_pass:
        tree_hashes = [item["fingerprint"]["logical_tree_sha256"] for item in attempts]
        core_hashes = [item["fingerprint"]["logical_core_tree_sha256"] for item in attempts]
        deterministic = len(set(tree_hashes)) == 1 and len(set(core_hashes)) == 1
        determinism_basis = "two LF-normalized bundle-tree and authoritative-core hashes"
    else:
        matched = [item["matched_expected_failure"] for item in attempts]
        deterministic = failed_as_expected and len(set(matched)) == 1
        determinism_basis = "two independently observed, contract-matched incompatibility failures"
    if family.expected == "success":
        gate = builds_pass and validations_pass and deterministic
        observed = "success" if builds_pass else "failure"
    else:
        gate = failed_as_expected and deterministic
        observed = "expected-incompatibility" if failed_as_expected else ("success" if builds_pass else "unexpected-failure")
    return {
        "expected": family.expected,
        "observed": observed,
        "gate": "pass" if gate else "fail",
        "builds_pass": builds_pass,
        "validations_pass": validations_pass if builds_pass else None,
        "deterministic_rebuild": {
            "status": "pass" if deterministic else "fail",
            "basis": determinism_basis,
            "logical_tree_sha256": attempts[0]["fingerprint"]["logical_tree_sha256"] if builds_pass else None,
        },
        "core": attempts[0]["fingerprint"] if builds_pass else None,
        "failure_contract": {
            "patterns": list(family.failure_patterns),
            "matched": [item["matched_expected_failure"] for item in attempts],
            "diagnostics": [item["build"]["diagnostic_excerpt"] for item in attempts],
        } if family.expected == "incompatible" else None,
        "attempts": attempts,
    }


def core_parity(families: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    eligible = {
        name: result
        for name, result in families.items()
        if result["expected"] == "success" and result["builds_pass"]
    }
    expected = sorted(name for name, result in families.items() if result["expected"] == "success")
    core_hashes = {
        result["core"]["logical_core_tree_sha256"]
        for result in eligible.values()
        if result.get("core")
    }
    record_hashes = {
        result["core"]["semantic_records_sha256"]
        for result in eligible.values()
        if result.get("core")
    }
    complete = sorted(eligible) == expected
    passed = complete and len(core_hashes) == 1 and len(record_hashes) == 1
    return {
        "status": "pass" if passed else "fail",
        "contract": "Every compatible builder must publish the same LF-normalized non-derived core tree and byte-identical semantic records.",
        "expected_families": expected,
        "observed_families": sorted(eligible),
        "logical_core_tree_sha256": next(iter(core_hashes)) if len(core_hashes) == 1 else None,
        "semantic_records_sha256": next(iter(record_hashes)) if len(record_hashes) == 1 else None,
        "per_family": {
            name: {
                "logical_core_tree_sha256": value["core"]["logical_core_tree_sha256"],
                "semantic_records_sha256": value["core"]["semantic_records_sha256"],
            }
            for name, value in sorted(eligible.items())
        },
    }


def git_commit() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", value) else None


def runtime_identity(python: str) -> dict[str, Any]:
    """Capture the interpreter and relevant package versions used for every build."""

    probe = r"""
import importlib.metadata
import json
import platform
import sys

packages = {}
for name in ("llama-index-core", "numpy", "pyshacl", "rdflib", "sentence-transformers", "torch"):
    try:
        packages[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        packages[name] = None
print(json.dumps({
    "implementation": platform.python_implementation(),
    "python": platform.python_version(),
    "platform": platform.platform(),
    "executable": sys.executable,
    "packages": packages,
}, sort_keys=True))
"""
    completed = subprocess.run(
        [python, "-c", probe],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise BuildRunError(f"Cannot inspect selected Python runtime: {completed.stderr.strip()}")
    value = json.loads(completed.stdout)
    executable = Path(value.pop("executable"))
    value["executable"] = file_binding(executable) if executable.is_file() else {"path": executable.name}
    value["offline_embedding_environment"] = True
    return value


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Endocrine-Hygiene Semantic OKF Build Comparison",
        "",
        f"Run: `{report['run_id']}`",
        f"Status: **{report['status']}**",
        (
            f"Corpus: {report['inputs']['corpus']['paper_count']} papers and "
            f"{report['inputs']['corpus']['source_count']} declared sources "
            "(30 authoritative paper/claim sources plus 1 auxiliary vocabulary)."
        ),
        "",
        "| Family | Expected | Observed | Build validation | Determinism | Core hash |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, result in report["families"].items():
        validation = "pass" if result["validations_pass"] is True else ("N/A" if result["validations_pass"] is None else "fail")
        core_hash = result["core"]["logical_core_tree_sha256"] if result["core"] else "N/A"
        lines.append(
            f"| {name} | {result['expected']} | {result['observed']} | {validation} | "
            f"{result['deterministic_rebuild']['status']} | `{core_hash}` |"
        )
    lines.extend(
        [
            "",
            "## Gates",
            "",
            f"- Authoritative-core parity: **{report['core_parity']['status']}**.",
            f"- Two executions per family: **{'pass' if all(len(row['attempts']) == 2 for row in report['families'].values()) else 'fail'}**.",
            "- Entity-graph incompatibility is expected because authoritative BioC passage headings are not PDF-page headings.",
            "- Ensemble incompatibility is expected because the unchanged adaptive component accepts only canonical versioned arXiv identity mappings while this corpus uses real PMCIDs.",
            "",
            "Raw commands, stdout, stderr, bundle trees, and both attempts remain append-only under the ignored run directory. The JSON report retains exact hashes and bounded diagnostics.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build all six unchanged Semantic OKF families twice and atomically publish comparison reports."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--run-id", default=default_run_id())
    parser.add_argument(
        "--python",
        default=str(DEFAULT_PYTHON if DEFAULT_PYTHON.is_file() else Path(sys.executable)),
        help="Python runtime for builders; defaults to the repository virtual environment when present.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate and fingerprint the generated corpus and plans without creating a run.",
    )
    args = parser.parse_args(argv)
    if not RUN_ID_RE.fullmatch(args.run_id):
        parser.error("--run-id must contain only letters, digits, dot, underscore, and hyphen")
    if args.timeout_seconds < 1:
        parser.error("--timeout-seconds must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    inputs = validate_inputs(args.manifest)
    if args.preflight_only:
        print(json.dumps({"status": "pass", "inputs": inputs}, indent=2, ensure_ascii=False))
        return 0

    runs_root = args.runs_root.resolve()
    runs_root.mkdir(parents=True, exist_ok=True)
    final_run = runs_root / args.run_id
    if final_run.exists():
        raise BuildRunError(f"Append-only run already exists: {final_run}")
    stage = Path(tempfile.mkdtemp(prefix=f".{args.run_id}.staging-", dir=runs_root))
    environment = dict(os.environ)
    environment.update(
        {
            "HF_DATASETS_OFFLINE": "1",
            "HF_HUB_OFFLINE": "1",
            "NO_COLOR": "1",
            "PYTHONHASHSEED": "0",
            "TOKENIZERS_PARALLELISM": "false",
            "TRANSFORMERS_OFFLINE": "1",
        }
    )
    started_at = utc_now()
    try:
        (stage / "inputs").mkdir(parents=True)
        shutil.copy2(args.manifest.resolve(), stage / "inputs" / "manifest.json")
        for filename in sorted({family.plan or "legacy-plan.json" for family in FAMILIES}):
            shutil.copy2(PLANS / filename, stage / "inputs" / filename)
        family_results: dict[str, Any] = {}
        for family in FAMILIES:
            attempts = [
                run_attempt(
                    family,
                    number,
                    manifest=args.manifest.resolve(),
                    stage=stage,
                    final_run=final_run,
                    python=args.python,
                    timeout_seconds=args.timeout_seconds,
                    environment=environment,
                )
                for number in (1, 2)
            ]
            family_results[family.name] = summarize_family(family, attempts)
        parity = core_parity(family_results)
        status = "pass" if parity["status"] == "pass" and all(
            value["gate"] == "pass" for value in family_results.values()
        ) else "fail"
        report = {
            "schema_version": REPORT_SCHEMA,
            "status": status,
            "run_id": args.run_id,
            "started_at": started_at,
            "completed_at": utc_now(),
            "run_directory": f"evaluations/semantic-okf-endocrine-hygiene/results/runs/{args.run_id}",
            "repository": {"commit": git_commit()},
            "runtime": runtime_identity(args.python),
            "inputs": inputs,
            "families": family_results,
            "core_parity": parity,
        }
        run_report = {
            **report,
            "schema_version": RUN_SCHEMA,
            "publication": {
                "append_only": True,
                "run_directory_published_atomically": True,
                "compact_reports_published_atomically": True,
            },
        }
        (stage / "run-report.json").write_text(
            json.dumps(run_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )
        (stage / "run-report.md").write_text(render_markdown(report), encoding="utf-8", newline="\n")
        os.replace(stage, final_run)
        atomic_write(args.json_report.resolve(), json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        atomic_write(args.markdown_report.resolve(), render_markdown(report))
        print(json.dumps({"status": status, "run_id": args.run_id, "run_directory": str(final_run)}, indent=2))
        return 0 if status == "pass" else 1
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildRunError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
