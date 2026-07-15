#!/usr/bin/env python3
"""Run the complete Semantic OKF embedding evaluation without replacing prior outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PACKAGE_NAMES = (
    "llama-index-core",
    "numpy",
    "pyshacl",
    "PyYAML",
    "rdflib",
    "sentence-transformers",
    "torch",
)


class OrchestrationError(RuntimeError):
    """Describe an invalid or failed append-only evaluation run."""


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically for logical fingerprints."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    """Return the physical byte SHA-256 for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def portable_path(path: Path, repo_root: Path, run_dir: Path | None = None) -> str:
    """Represent a path without embedding machine-specific absolute prefixes."""

    resolved = path.resolve()
    if run_dir is not None:
        try:
            relative = resolved.relative_to(run_dir.resolve())
        except ValueError:
            pass
        else:
            return "$RUN" if not relative.parts else f"$RUN/{relative.as_posix()}"
    try:
        relative = resolved.relative_to(repo_root.resolve())
    except ValueError:
        return f"external/{resolved.name}"
    return "$REPO" if not relative.parts else f"$REPO/{relative.as_posix()}"


def file_fingerprint(path: Path, repo_root: Path, run_dir: Path | None = None) -> dict[str, Any]:
    """Fingerprint a file and retain only its portable path label."""

    return {
        "path": portable_path(path, repo_root, run_dir),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def tree_fingerprint(root: Path, repo_root: Path, run_dir: Path) -> dict[str, Any]:
    """Fingerprint every file in a tree by sorted path and byte digest."""

    files = sorted(path for path in root.rglob("*") if path.is_file())
    entries = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}
        for path in files
    ]
    return {
        "path": portable_path(root, repo_root, run_dir),
        "file_count": len(files),
        "total_bytes": sum(path.stat().st_size for path in files),
        "logical_tree_sha256": hashlib.sha256(canonical_json(entries).encode("utf-8")).hexdigest(),
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(4)}"


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OrchestrationError(f"Cannot read JSON object at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise OrchestrationError(f"Expected a JSON object at {path}")
    return value


def _runtime_identity(python_executable: Path, repo_root: Path) -> dict[str, Any]:
    probe = """
import importlib.metadata
import json
import platform
import sys

names = json.loads(sys.argv[1])
versions = {}
for name in names:
    try:
        versions[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        versions[name] = None
print(json.dumps({
    "python": {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "version_detail": sys.version,
    },
    "platform": {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    },
    "packages": versions,
}, sort_keys=True))
"""
    try:
        completed = subprocess.run(
            [str(python_executable), "-c", probe, canonical_json(PACKAGE_NAMES)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=30,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        raise OrchestrationError(f"Cannot probe the selected Python runtime: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise OrchestrationError(f"Selected Python runtime probe failed: {detail}")
    try:
        identity = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise OrchestrationError(f"Selected Python runtime probe emitted invalid JSON: {exc}") from exc
    if not isinstance(identity, dict):
        raise OrchestrationError("Selected Python runtime probe did not emit a JSON object.")
    executable: dict[str, Any] = {"name": python_executable.name}
    if python_executable.is_file():
        executable.update(
            {
                "bytes": python_executable.stat().st_size,
                "sha256": sha256_file(python_executable),
            }
        )
    identity["python"]["executable"] = executable
    identity["repository"] = {"path": portable_path(repo_root, repo_root)}
    return identity


def _requirements_fingerprints(repo_root: Path) -> list[dict[str, Any]]:
    files: list[Path] = []
    for skill in (
        "build-semantic-okf",
        "build-semantic-okf-embeddings",
        "consult-semantic-okf-embeddings",
    ):
        scripts = repo_root / "skills" / skill / "scripts"
        files.extend(scripts.glob("requirements*.in"))
        files.extend(scripts.glob("requirements*.txt"))
    return [file_fingerprint(path, repo_root) for path in sorted(set(files))]


def _tool_fingerprints(repo_root: Path) -> dict[str, dict[str, Any]]:
    relative = {
        "builder": "skills/build-semantic-okf-embeddings/scripts/build_semantic_okf_embeddings.py",
        "embedding_validator": "skills/build-semantic-okf-embeddings/scripts/validate_semantic_okf_embeddings.py",
        "legacy_semantic_validator": "skills/build-semantic-okf/scripts/validate_semantic_okf.py",
        "build_runtime_smoke": "skills/build-semantic-okf-embeddings/scripts/runtime_smoke.py",
        "consult_runtime_smoke": "skills/consult-semantic-okf-embeddings/scripts/runtime_smoke.py",
        "consult": "skills/consult-semantic-okf-embeddings/scripts/query_semantic_okf_embeddings.py",
        "comparator": "evaluations/semantic-okf-embeddings/scripts/compare_retrieval.py",
        "orchestrator": "evaluations/semantic-okf-embeddings/scripts/run_evaluation.py",
    }
    result: dict[str, dict[str, Any]] = {}
    for name, value in relative.items():
        path = repo_root / value
        if not path.is_file():
            raise OrchestrationError(f"Required tool is missing: {value}")
        result[name] = file_fingerprint(path, repo_root)
    return result


def _portable_argv(argv: Sequence[str], repo_root: Path, run_dir: Path, python_executable: Path) -> list[str]:
    result: list[str] = []
    for value in argv:
        if value == str(python_executable):
            result.append("$PYTHON")
            continue
        candidate = Path(value)
        if candidate.is_absolute():
            result.append(portable_path(candidate, repo_root, run_dir))
        else:
            result.append(value.replace("\\", "/"))
    return result


def _command_specs(
    repo_root: Path,
    run_dir: Path,
    python_executable: Path,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    evaluation = repo_root / "evaluations" / "semantic-okf-embeddings"
    historical = repo_root / "evaluations" / "graphrag-cross-paper"
    build_scripts = repo_root / "skills" / "build-semantic-okf-embeddings" / "scripts"
    legacy_scripts = repo_root / "skills" / "build-semantic-okf" / "scripts"
    consult_scripts = repo_root / "skills" / "consult-semantic-okf-embeddings" / "scripts"
    comparator = evaluation / "scripts" / "compare_retrieval.py"
    embedding_a = run_dir / "embedding-a"
    embedding_b = run_dir / "embedding-b"
    reports = run_dir / "reports"

    def spec(name: str, *argv: object) -> dict[str, Any]:
        command = [str(python_executable), *(str(item) for item in argv)]
        return {
            "name": name,
            "argv": command,
            "portable_argv": _portable_argv(command, repo_root, run_dir, python_executable),
            "timeout_seconds": timeout_seconds,
        }

    specs = [
        spec(
            "validate-legacy-semantic",
            legacy_scripts / "validate_semantic_okf.py",
            historical / "bundle",
            "--output-format",
            "json",
        ),
        spec("smoke-build-runtime", build_scripts / "runtime_smoke.py"),
        spec("smoke-consult-runtime", consult_scripts / "runtime_smoke.py"),
        spec(
            "build-embedding-a",
            build_scripts / "build_semantic_okf_embeddings.py",
            historical / "manifest.json",
            evaluation / "retrieval-plan.json",
            embedding_a,
            "--output-format",
            "json",
        ),
        spec(
            "validate-embedding-a",
            build_scripts / "validate_semantic_okf_embeddings.py",
            embedding_a,
            "--output-format",
            "json",
        ),
        spec(
            "build-embedding-b",
            build_scripts / "build_semantic_okf_embeddings.py",
            historical / "manifest.json",
            evaluation / "retrieval-plan.json",
            embedding_b,
            "--output-format",
            "json",
        ),
        spec(
            "validate-embedding-b",
            build_scripts / "validate_semantic_okf_embeddings.py",
            embedding_b,
            "--output-format",
            "json",
        ),
    ]
    for top_k in (10, 100):
        prefix = reports / f"top-k-{top_k}"
        specs.append(
            spec(
                f"compare-top-k-{top_k}",
                comparator,
                "--inventory",
                evaluation / "input-inventory.json",
                "--questions",
                evaluation / "retrieval-questions.jsonl",
                "--legacy-bundle",
                historical / "bundle",
                "--new-bundle",
                embedding_a,
                "--consult-script",
                consult_scripts / "query_semantic_okf_embeddings.py",
                "--python-executable",
                python_executable,
                "--input-root",
                historical,
                "--top-k",
                top_k,
                "--timeout-seconds",
                timeout_seconds,
                "--output-json",
                prefix.with_suffix(".json"),
                "--output-markdown",
                prefix.with_suffix(".md"),
            )
        )
    return specs


def _run_command(
    spec: dict[str, Any],
    sequence: int,
    repo_root: Path,
    run_dir: Path,
    environment: dict[str, str],
) -> dict[str, Any]:
    logs = run_dir / "logs"
    logs.mkdir(exist_ok=True)
    prefix = logs / f"{sequence:02d}-{spec['name']}"
    stdout_path = prefix.with_suffix(".stdout.txt")
    stderr_path = prefix.with_suffix(".stderr.txt")
    if stdout_path.exists() or stderr_path.exists():
        raise OrchestrationError(f"Refusing to overwrite command logs for {spec['name']}")
    started_at = _utc_now()
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            spec["argv"],
            cwd=repo_root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=float(spec["timeout_seconds"]),
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}\n"
        returncode = -1
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    record = {
        "name": spec["name"],
        "argv": spec["portable_argv"],
        "started_at": started_at,
        "elapsed_ms": elapsed_ms,
        "exit_code": returncode,
        "stdout": file_fingerprint(stdout_path, repo_root, run_dir),
        "stderr": file_fingerprint(stderr_path, repo_root, run_dir),
    }
    return record


def _write_new_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise OrchestrationError(f"Refusing to overwrite run manifest: {path}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _manifest_base(
    repo_root: Path,
    run_dir: Path,
    python_executable: Path,
    specs: list[dict[str, Any]],
) -> dict[str, Any]:
    evaluation = repo_root / "evaluations" / "semantic-okf-embeddings"
    historical = repo_root / "evaluations" / "graphrag-cross-paper"
    plan = _load_json_object(evaluation / "retrieval-plan.json")
    inputs = {
        "semantic_manifest": file_fingerprint(historical / "manifest.json", repo_root),
        "retrieval_plan": file_fingerprint(evaluation / "retrieval-plan.json", repo_root),
        "input_inventory": file_fingerprint(evaluation / "input-inventory.json", repo_root),
        "retrieval_questions": file_fingerprint(evaluation / "retrieval-questions.jsonl", repo_root),
        "historical_bundle": tree_fingerprint(historical / "bundle", repo_root, run_dir),
    }
    return {
        "schema_version": "1.0",
        "contract": (
            "Append-only evaluation: every build, validation, log, report, and manifest is created beneath "
            "one previously absent run directory; no prior result is deleted or replaced."
        ),
        "run_id": run_dir.name,
        "run_directory": portable_path(run_dir, repo_root, run_dir),
        "created_at": _utc_now(),
        "runtime": _runtime_identity(python_executable, repo_root),
        "model": {
            **dict(plan.get("embedding") or {}),
            "loading": "explicit, local-only, offline; weights are an external preloaded input",
        },
        "chunking": plan.get("chunking"),
        "environment": {
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "PYTHONHASHSEED": "0",
            "TOKENIZERS_PARALLELISM": "false",
        },
        "inputs": inputs,
        "requirements": _requirements_fingerprints(repo_root),
        "tools": _tool_fingerprints(repo_root),
        "planned_commands": [
            {"name": item["name"], "argv": item["portable_argv"], "timeout_seconds": item["timeout_seconds"]}
            for item in specs
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the non-destructive orchestration CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--python-executable", type=Path, default=Path(sys.executable))
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--run-id", help="Optional unique directory name; existing directories are rejected.")
    parser.add_argument("--timeout-seconds", type=float, default=1800.0)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create only a planned run manifest in a new run directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Create a unique run, execute every gate, and publish one immutable manifest."""

    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    python_executable = args.python_executable.resolve()
    run_root = (
        args.run_root.resolve()
        if args.run_root is not None
        else repo_root / "evaluations" / "semantic-okf-embeddings" / "results" / "runs"
    )
    run_id = args.run_id or _default_run_id()
    if not RUN_ID_RE.fullmatch(run_id):
        print(
            "orchestration error: --run-id must use only letters, digits, dot, underscore, or hyphen",
            file=sys.stderr,
        )
        return 2
    if args.timeout_seconds <= 0:
        print("orchestration error: --timeout-seconds must be positive", file=sys.stderr)
        return 2
    run_dir = run_root / run_id
    try:
        run_root.mkdir(parents=True, exist_ok=True)
        run_dir.mkdir(exist_ok=False)
    except FileExistsError:
        print(f"orchestration error: refusing to overwrite existing run directory: {run_dir}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"orchestration error: cannot create run directory: {exc}", file=sys.stderr)
        return 2

    specs: list[dict[str, Any]] = []
    manifest: dict[str, Any] = {}
    commands: list[dict[str, Any]] = []
    deterministic_record: dict[str, Any] | None = None
    started = time.perf_counter()
    try:
        specs = _command_specs(repo_root, run_dir, python_executable, args.timeout_seconds)
        manifest = _manifest_base(repo_root, run_dir, python_executable, specs)
        if args.dry_run:
            manifest.update({"status": "planned", "dry_run": True, "commands": [], "outputs": {}})
            _write_new_json(run_dir / "run-manifest.json", manifest)
            print(canonical_json({"status": "planned", "run_id": run_id}))
            return 0

        environment = os.environ.copy()
        environment.update(manifest["environment"])
        build_and_validation_specs = [item for item in specs if not item["name"].startswith("compare-")]
        comparison_specs = [item for item in specs if item["name"].startswith("compare-")]
        for sequence, spec in enumerate(build_and_validation_specs, start=1):
            command = _run_command(spec, sequence, repo_root, run_dir, environment)
            commands.append(command)
            if command["exit_code"] != 0:
                raise OrchestrationError(canonical_json({"command_failure": command}))

        deterministic_started = time.perf_counter()
        first = tree_fingerprint(run_dir / "embedding-a", repo_root, run_dir)
        second = tree_fingerprint(run_dir / "embedding-b", repo_root, run_dir)
        deterministic = first["logical_tree_sha256"] == second["logical_tree_sha256"]
        deterministic_elapsed_ms = (time.perf_counter() - deterministic_started) * 1000.0
        deterministic_record = {
            "status": "pass" if deterministic else "fail",
            "contract": "Two independent builds must have identical sorted path-and-byte SHA-256 trees.",
            "elapsed_ms": deterministic_elapsed_ms,
            "first": first,
            "second": second,
        }
        if not deterministic:
            raise OrchestrationError("The two clean embedding builds are not byte-identical.")
        for sequence, spec in enumerate(comparison_specs, start=len(build_and_validation_specs) + 1):
            command = _run_command(spec, sequence, repo_root, run_dir, environment)
            commands.append(command)
            if command["exit_code"] != 0:
                raise OrchestrationError(canonical_json({"command_failure": command}))
        reports = {
            name: file_fingerprint(run_dir / "reports" / name, repo_root, run_dir)
            for name in ("top-k-10.json", "top-k-10.md", "top-k-100.json", "top-k-100.md")
        }
        manifest.update(
            {
                "status": "pass",
                "dry_run": False,
                "elapsed_ms": (time.perf_counter() - started) * 1000.0,
                "commands": commands,
                "deterministic_rebuild": deterministic_record,
                "outputs": {
                    "embedding_a": first,
                    "embedding_b": second,
                    "reports": reports,
                },
            }
        )
        _write_new_json(run_dir / "run-manifest.json", manifest)
    except (OSError, UnicodeError, OrchestrationError, json.JSONDecodeError) as exc:
        if not manifest:
            manifest = {
                "schema_version": "1.0",
                "run_id": run_id,
                "created_at": _utc_now(),
            }
        manifest.update(
            {
                "status": "fail",
                "dry_run": False,
                "elapsed_ms": (time.perf_counter() - started) * 1000.0,
                "commands": commands,
                "error": str(exc),
            }
        )
        if deterministic_record is not None:
            manifest["deterministic_rebuild"] = deterministic_record
        try:
            _write_new_json(run_dir / "run-manifest.failed.json", manifest)
        except (OSError, OrchestrationError):
            pass
        print(f"orchestration error: {exc}", file=sys.stderr)
        return 2
    print(canonical_json({"status": "pass", "run_id": run_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
