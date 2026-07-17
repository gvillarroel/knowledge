#!/usr/bin/env python3
"""Build every Astro Semantic OKF alternative twice into one append-only run."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
PLANS = EVALUATION / "plans"
DEFAULT_MANIFEST = EVALUATION / "corpus" / "manifest.json"
DEFAULT_RUNS = EVALUATION / "results" / "runs"
DEFAULT_REPORT = EVALUATION / "reports" / "build-comparison.json"
DEFAULT_MARKDOWN = EVALUATION / "reports" / "build-comparison.md"
DEFAULT_PYTHON = REPO / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
SCHEMA = "semantic-okf-astro-build-comparison/1.0"
RUN_SCHEMA = "semantic-okf-astro-build-run/1.0"
DERIVED_ROOTS = frozenset({"adaptive", "classical", "ensemble", "entity-graph", "retrieval"})


class BuildError(RuntimeError):
    """Describe an invalid input, failed command, or unsafe publication."""


@dataclass(frozen=True)
class Family:
    """Describe one independently installable build/consult family."""

    name: str
    plan: str | None
    builder: str
    validator: str
    deep_validator: str | None


FAMILIES = (
    Family(
        "legacy",
        None,
        "skills/build-semantic-okf/scripts/build_semantic_okf.py",
        "skills/build-semantic-okf/scripts/validate_semantic_okf.py",
        None,
    ),
    Family(
        "embeddings",
        "embedding-plan.json",
        "skills/build-semantic-okf-embeddings/scripts/build_semantic_okf_embeddings.py",
        "skills/build-semantic-okf-embeddings/scripts/validate_semantic_okf_embeddings.py",
        "skills/build-semantic-okf-embeddings/scripts/validate_okf_bundle.py",
    ),
    Family(
        "classical",
        "classical-plan.json",
        "skills/build-semantic-okf-classical/scripts/build_semantic_okf_classical.py",
        "skills/build-semantic-okf-classical/scripts/validate_semantic_okf_classical.py",
        "skills/build-semantic-okf-classical/scripts/validate_okf_bundle.py",
    ),
    Family(
        "adaptive",
        "adaptive-plan.json",
        "skills/build-semantic-okf-adaptive/scripts/build_semantic_okf_adaptive.py",
        "skills/build-semantic-okf-adaptive/scripts/validate_semantic_okf_adaptive.py",
        "skills/build-semantic-okf-adaptive/scripts/validate_okf_bundle.py",
    ),
    Family(
        "entity-graph",
        "entity-graph-plan.json",
        "skills/build-semantic-okf-entity-graph/scripts/build_semantic_okf_entity_graph.py",
        "skills/build-semantic-okf-entity-graph/scripts/validate_semantic_okf_entity_graph.py",
        "skills/build-semantic-okf-entity-graph/scripts/validate_okf_bundle.py",
    ),
    Family(
        "ensemble",
        "ensemble-plan.json",
        "skills/build-semantic-okf-ensemble/scripts/build_semantic_okf_ensemble.py",
        "skills/build-semantic-okf-ensemble/scripts/validate_semantic_okf_ensemble.py",
        "skills/build-semantic-okf-ensemble/scripts/validate_okf_bundle.py",
    ),
)


def canonical_json(value: Any) -> str:
    """Serialize one JSON-compatible value deterministically."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pretty_json(value: Any) -> str:
    """Serialize one report as stable human-readable JSON."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def sha256_bytes(value: bytes) -> str:
    """Return the lowercase SHA-256 digest of bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path, *, logical_text: bool = False) -> str:
    """Hash one file, optionally normalizing text line endings."""

    payload = path.read_bytes()
    if logical_text:
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256_bytes(payload)


def load_json(path: Path) -> dict[str, Any]:
    """Read one required JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"expected a JSON object at {path}")
    return value


def atomic_write(path: Path, payload: str) -> None:
    """Publish a compact report by same-directory atomic replacement."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
    try:
        temporary.write_text(payload, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def binding(path: Path) -> dict[str, Any]:
    """Bind one regular repository file by portable path, bytes, and digest."""

    resolved = path.resolve(strict=True)
    try:
        label = resolved.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        label = f"external/{resolved.name}"
    return {"path": label, "bytes": resolved.stat().st_size, "sha256": sha256_file(resolved)}


def run_binding(path: Path, stage: Path) -> dict[str, Any]:
    """Bind one raw run artifact relative to its eventual append-only run root."""

    resolved = path.resolve(strict=True)
    try:
        label = resolved.relative_to(stage.resolve()).as_posix()
    except ValueError as exc:
        raise BuildError(f"run artifact escapes its staging root: {resolved}") from exc
    return {"path": label, "bytes": resolved.stat().st_size, "sha256": sha256_file(resolved)}


def validate_inputs(manifest_path: Path) -> dict[str, Any]:
    """Validate and fingerprint the closed Astro manifest and every family plan."""

    manifest_path = manifest_path.resolve(strict=True)
    manifest = load_json(manifest_path)
    sources = manifest.get("sources")
    if manifest.get("schema_version") != "1.0" or not isinstance(sources, list) or not sources:
        raise BuildError("Astro manifest must use schema 1.0 and contain sources")
    root = manifest_path.parent.resolve()
    source_ids: list[str] = []
    input_paths: set[Path] = {manifest_path}
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            raise BuildError(f"manifest source {index} is not an object")
        source_id, raw_path = source.get("id"), source.get("path")
        if not isinstance(source_id, str) or not source_id or not isinstance(raw_path, str) or not raw_path:
            raise BuildError(f"manifest source {index} lacks id/path")
        candidate = PurePosixPath(raw_path)
        if candidate.is_absolute() or ".." in candidate.parts or "\\" in raw_path:
            raise BuildError(f"manifest source {source_id} has an unsafe path")
        matches = sorted(
            path.resolve()
            for value in glob.glob(str(root / raw_path), recursive=True)
            if (path := Path(value)).is_file()
        )
        if not matches and not source.get("allow_empty", False):
            raise BuildError(f"manifest source {source_id} matched no files")
        for path in matches:
            try:
                path.relative_to(root)
            except ValueError as exc:
                raise BuildError(f"manifest source {source_id} escapes the corpus") from exc
            input_paths.add(path)
        source_ids.append(source_id)
    if source_ids != list(dict.fromkeys(source_ids)):
        raise BuildError("manifest source IDs are not unique")

    plans: list[dict[str, Any]] = []
    for family in FAMILIES:
        if family.plan is None:
            continue
        path = (PLANS / family.plan).resolve(strict=True)
        load_json(path)
        plans.append(binding(path))
    inputs = [binding(path) for path in sorted(input_paths)]
    return {
        "manifest": binding(manifest_path),
        "plans": sorted(plans, key=lambda row: row["path"]),
        "corpus": {
            "source_count": len(source_ids),
            "source_ids": source_ids,
            "input_file_count": len(input_paths) - 1,
            "input_bytes": sum(path.stat().st_size for path in input_paths if path != manifest_path),
            "logical_input_sha256": sha256_bytes(canonical_json(inputs).encode("utf-8")),
            "files": inputs,
        },
    }


def tree_fingerprint(root: Path) -> dict[str, Any]:
    """Fingerprint a complete bundle and its authoritative non-derived core."""

    files = sorted(path for path in root.rglob("*") if path.is_file())
    relative = [path.relative_to(root).as_posix() for path in files]
    core = [
        label for label in relative
        if not PurePosixPath(label).parts or PurePosixPath(label).parts[0] not in DERIVED_ROOTS
    ]

    def digest(labels: list[str]) -> str:
        rows = [
            {"path": label, "sha256": sha256_file(root / Path(label), logical_text=True)}
            for label in labels
        ]
        return sha256_bytes(canonical_json(rows).encode("utf-8"))

    records = root / "semantic" / "records.jsonl"
    return {
        "file_count": len(relative),
        "total_bytes": sum(path.stat().st_size for path in files),
        "logical_tree_sha256": digest(relative),
        "core_file_count": len(core),
        "logical_core_tree_sha256": digest(core),
        "semantic_records_sha256": sha256_file(records) if records.is_file() else None,
    }


def portable_command(command: Sequence[str], stage: Path) -> list[str]:
    """Redact machine-specific roots from a persisted command."""

    rendered: list[str] = []
    for item in command:
        value = str(item).replace(str(REPO.resolve()), "$REPO").replace(str(stage.resolve()), "$RUN")
        rendered.append(value.replace("\\", "/"))
    return rendered


def execute(command: Sequence[str], *, stage: Path, log: Path, timeout: float, env: Mapping[str, str]) -> dict[str, Any]:
    """Execute one bounded command and retain append-only stdout/stderr logs."""

    started = time.perf_counter()
    timed_out = False
    try:
        completed = subprocess.run(
            list(command), cwd=REPO, env=dict(env), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout, check=False,
        )
        code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        code = None
        stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stderr += f"\nTimed out after {timeout} seconds.\n"
    elapsed = round((time.perf_counter() - started) * 1000.0, 3)
    log.parent.mkdir(parents=True, exist_ok=True)
    stdout_path, stderr_path = log.with_suffix(".stdout.txt"), log.with_suffix(".stderr.txt")
    stdout_path.write_text(stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr, encoding="utf-8", newline="\n")
    diagnostic = "\n".join(line for line in f"{stdout}\n{stderr}".splitlines() if line.strip())[-5000:]
    diagnostic = diagnostic.replace(str(REPO.resolve()), "$REPO").replace(str(stage.resolve()), "$RUN")
    return {
        "command": portable_command(command, stage),
        "returncode": code,
        "timed_out": timed_out,
        "elapsed_ms": elapsed,
        "stdout": run_binding(stdout_path, stage),
        "stderr": run_binding(stderr_path, stage),
        "diagnostic_excerpt": diagnostic,
    }


def run_attempt(
    family: Family,
    suffix: str,
    *,
    manifest: Path,
    stage: Path,
    python: str,
    timeout: float,
    env: Mapping[str, str],
) -> dict[str, Any]:
    """Build and validate one independent family repetition."""

    output = stage / "bundles" / f"{family.name}-{suffix}"
    command = [python, str(REPO / family.builder), str(manifest)]
    if family.plan is not None:
        command.append(str(PLANS / family.plan))
    command.extend([str(output), "--output-format", "json"])
    build = execute(
        command, stage=stage, log=stage / "logs" / f"{family.name}-{suffix}" / "build",
        timeout=timeout, env=env,
    )
    validators: list[dict[str, Any]] = []
    if build["returncode"] == 0 and output.is_dir():
        for kind, script in (("family", family.validator), ("deep", family.deep_validator)):
            if script is None:
                continue
            validator = [python, str(REPO / script), str(output)]
            if kind == "family":
                validator.extend(["--output-format", "json"])
            validators.append(
                {
                    "kind": kind,
                    **execute(
                        validator, stage=stage,
                        log=stage / "logs" / f"{family.name}-{suffix}" / f"validate-{kind}",
                        timeout=timeout, env=env,
                    ),
                }
            )
    return {
        "attempt": suffix,
        "build": build,
        "output_published": output.is_dir(),
        "validators": validators,
        "fingerprint": tree_fingerprint(output) if output.is_dir() else None,
    }


def summarize(family: Family, attempts: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize build, validation, and deterministic-rebuild gates."""

    built = all(row["build"]["returncode"] == 0 and row["output_published"] for row in attempts)
    validated = built and all(row["validators"] or family.deep_validator is None for row in attempts) and all(
        item["returncode"] == 0 and not item["timed_out"]
        for row in attempts for item in row["validators"]
    )
    deterministic = built and len({row["fingerprint"]["logical_tree_sha256"] for row in attempts}) == 1
    core_deterministic = built and len({row["fingerprint"]["logical_core_tree_sha256"] for row in attempts}) == 1
    records_deterministic = built and len({row["fingerprint"]["semantic_records_sha256"] for row in attempts}) == 1
    return {
        "family": family.name,
        "status": "pass" if built and validated and deterministic and core_deterministic and records_deterministic else "fail",
        "builds_pass": built,
        "validations_pass": validated,
        "deterministic_rebuild": deterministic,
        "authoritative_core_deterministic": core_deterministic,
        "records_deterministic": records_deterministic,
        "attempts": attempts,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the compact build-gate table."""

    lines = [
        "# Astro Semantic OKF Build Comparison",
        "",
        "Every family was built twice from the same frozen 416-document corpus. Derived projections are non-authoritative; the core-parity gate compares the complete authoritative Semantic OKF core across families.",
        "",
        "| Family | Status | Build | Validation | Deterministic bundle | Deterministic core | Core parity | Mean build ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["families"]:
        mean = sum(item["build"]["elapsed_ms"] for item in row["attempts"]) / len(row["attempts"])
        lines.append(
            f"| {row['family']} | {row['status']} | {'pass' if row['builds_pass'] else 'fail'} | "
            f"{'pass' if row['validations_pass'] else 'fail'} | {'pass' if row['deterministic_rebuild'] else 'fail'} | "
            f"{'pass' if row['authoritative_core_deterministic'] else 'fail'} | "
            f"{'pass' if report['authoritative_core_parity'] else 'fail'} | {mean:.1f} |"
        )
    lines.extend(
        [
            "",
            f"Run: `{report['run_dir']}`",
            "",
            "No MCP server or transport participates in acquisition, build, validation, or consultation.",
            "",
        ]
    )
    return "\n".join(lines)


def default_run_id() -> str:
    """Return a sortable collision-resistant UTC run ID."""

    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--run-id", default=default_run_id())
    parser.add_argument("--python", default=str(DEFAULT_PYTHON if DEFAULT_PYTHON.is_file() else Path(sys.executable)))
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args(argv)
    if not args.run_id or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for character in args.run_id):
        parser.error("--run-id must contain only letters, digits, dot, underscore, and hyphen")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    for name in ("manifest", "runs_root", "report", "markdown"):
        setattr(args, name, getattr(args, name).resolve())
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the append-only double-build experiment."""

    args = parse_args(argv)
    final = args.runs_root / args.run_id
    stage = args.runs_root / f".{args.run_id}.{secrets.token_hex(5)}.staging"
    if final.exists():
        print(json.dumps({"status": "error", "error": f"run already exists: {final}"}), file=sys.stderr)
        return 1
    try:
        inputs = validate_inputs(args.manifest)
        stage.mkdir(parents=True, exist_ok=False)
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
        env.update({"PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
        families = [
            summarize(
                family,
                [
                    run_attempt(
                        family, suffix, manifest=args.manifest, stage=stage,
                        python=args.python, timeout=args.timeout, env=env,
                    )
                    for suffix in ("a", "b")
                ],
            )
            for family in FAMILIES
        ]
        passing = [row for row in families if row["status"] == "pass"]
        core_hashes = {
            row["attempts"][0]["fingerprint"]["logical_core_tree_sha256"]
            for row in passing
        }
        record_hashes = {
            row["attempts"][0]["fingerprint"]["semantic_records_sha256"]
            for row in passing
        }
        core_parity = len(passing) == len(families) and len(core_hashes) == 1 and len(record_hashes) == 1
        report: dict[str, Any] = {
            "schema_version": SCHEMA,
            "status": "pass" if len(passing) == len(families) and core_parity else "fail",
            "run_id": args.run_id,
            "run_dir": (final.relative_to(REPO).as_posix() if final.is_relative_to(REPO) else str(final)),
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "inputs": inputs,
            "authoritative_core_parity": core_parity,
            "logical_core_tree_sha256": next(iter(core_hashes)) if len(core_hashes) == 1 else None,
            "semantic_records_sha256": next(iter(record_hashes)) if len(record_hashes) == 1 else None,
            "families": families,
        }
        (stage / "run.json").write_text(
            pretty_json({"schema_version": RUN_SCHEMA, **report}), encoding="utf-8", newline="\n"
        )
        final.parent.mkdir(parents=True, exist_ok=True)
        os.replace(stage, final)
        atomic_write(args.report, pretty_json(report))
        atomic_write(args.markdown, render_markdown(report))
    except (BuildError, OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        shutil.rmtree(stage, ignore_errors=True)
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"], "run_dir": str(final), "families": len(families)}))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
