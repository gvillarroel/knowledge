#!/usr/bin/env python3
"""Run the complete real-tool Tika/MALLET experiment without downloading tools."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
BUILD_SCRIPTS = REPO_ROOT / "skills" / "build-semantic-okf-tika-mallet" / "scripts"
CONSULT_SCRIPTS = REPO_ROOT / "skills" / "consult-semantic-okf-tika-mallet" / "scripts"
BUILD_SKILL = BUILD_SCRIPTS.parent
CONSULT_SKILL = CONSULT_SCRIPTS.parent
REPARSE_POINT = 0x0400


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root: Path, *, ignore_runtime_caches: bool = False) -> list[dict[str, str]]:
    """Return a complete regular-file inventory without following links."""

    files: list[Path] = []
    pending = [root]
    while pending:
        current = pending.pop()
        for entry in os.scandir(current):
            path = Path(entry.path)
            value = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(value.st_mode) or (
                getattr(value, "st_file_attributes", 0) & REPARSE_POINT
            ):
                raise RuntimeError(f"inventory contains a link or reparse point: {path}")
            if stat.S_ISDIR(value.st_mode):
                if ignore_runtime_caches and path.name == "__pycache__":
                    continue
                pending.append(path)
            elif stat.S_ISREG(value.st_mode):
                if ignore_runtime_caches and path.suffix.casefold() == ".pyc":
                    continue
                files.append(path)
            else:
                raise RuntimeError(f"inventory contains an unsupported entry: {path}")
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(files, key=lambda item: item.relative_to(root).as_posix())
    ]


def inventory_receipt(root: Path, *, ignore_runtime_caches: bool = False) -> dict[str, Any]:
    rows = inventory(root, ignore_runtime_caches=ignore_runtime_caches)
    return {
        "file_count": len(rows),
        "inventory_sha256": hashlib.sha256(
            canonical_json(rows).encode("utf-8")
        ).hexdigest(),
        "inventory": rows,
    }


def run_json(command: Sequence[str], *, cwd: Path, timeout: int) -> dict[str, Any]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=timeout,
    )
    if completed.returncode != 0:
        diagnostic = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            f"command exited {completed.returncode}: {diagnostic[:2000]}"
        )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("command did not return one JSON value") from exc
    if not isinstance(value, dict) or value.get("status") != "pass":
        raise RuntimeError("command returned a non-passing result")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--tika-home", type=Path, required=True)
    parser.add_argument("--mallet-home", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--query", default="Confluence round trip verification", help="Smoke query"
    )
    parser.add_argument("--timeout-seconds", type=int, default=600)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_root = args.output_root.expanduser().resolve()
    if output_root.exists() or output_root.is_symlink():
        raise SystemExit(f"output root already exists: {output_root}")
    output_root.mkdir(parents=True)
    build_a = output_root / "bundle-a"
    build_b = output_root / "bundle-b"
    ingestion = HERE / "ingestion-plan.json"
    retrieval = HERE / "retrieval-plan.json"
    builder = BUILD_SCRIPTS / "build_semantic_okf_tika_mallet.py"
    validator = BUILD_SCRIPTS / "validate_semantic_okf_tika_mallet.py"
    consultant = CONSULT_SCRIPTS / "query_semantic_okf_tika_mallet.py"
    common = [
        "--java",
        str(args.java),
        "--tika-home",
        str(args.tika_home),
        "--mallet-home",
        str(args.mallet_home),
        "--output-format",
        "json",
    ]
    builds = []
    for destination in (build_a, build_b):
        builds.append(
            run_json(
                [
                    sys.executable,
                    "-B",
                    str(builder),
                    str(ingestion),
                    str(retrieval),
                    str(destination),
                    *common,
                ],
                cwd=HERE,
                timeout=args.timeout_seconds,
            )
        )
    validations = [
        run_json(
            [
                sys.executable,
                "-B",
                str(validator),
                str(destination),
                "--java",
                str(args.java),
                "--mallet-home",
                str(args.mallet_home),
                "--output-format",
                "json",
            ],
            cwd=HERE,
            timeout=args.timeout_seconds,
        )
        for destination in (build_a, build_b)
    ]
    deep = run_json(
        [
            sys.executable,
            "-B",
            str(consultant),
            str(build_a),
            "inspect",
            "--deep-validation",
            "--java",
            str(args.java),
            "--mallet-home",
            str(args.mallet_home),
        ],
        cwd=HERE,
        timeout=args.timeout_seconds,
    )
    search = run_json(
        [
            sys.executable,
            "-B",
            str(consultant),
            str(build_a),
            "search",
            "--query",
            args.query,
            "--mode",
            "fusion",
            "--top-k",
            "2",
        ],
        cwd=HERE,
        timeout=args.timeout_seconds,
    )
    inventory_a = inventory(build_a)
    inventory_b = inventory(build_b)
    if inventory_a != inventory_b:
        raise RuntimeError("the two clean bundle inventories differ")
    digest = hashlib.sha256(canonical_json(inventory_a).encode("utf-8")).hexdigest()
    report = {
        "schema_version": "1.0",
        "status": "pass",
        "experiment": "semantic-okf-tika-mallet-real-tools",
        "builds": [
            {"tika": row["tika"], "mallet": row["mallet"]} for row in builds
        ],
        "validations": [row["valid"] for row in validations],
        "deep_validation": deep["validation"],
        "search": {
            "effective_mode": search["effective_mode"],
            "returned": search["returned"],
        },
        "reproducibility": {
            "equal": True,
            "file_count": len(inventory_a),
            "inventory_sha256": digest,
            "inventory": inventory_a,
        },
        "fixture_sha256": {
            path.relative_to(HERE).as_posix(): sha256_file(path)
            for path in sorted((HERE / "fixtures").rglob("*"))
            if path.is_file()
        },
        "inputs": {
            "ingestion_plan_sha256": sha256_file(ingestion),
            "retrieval_plan_sha256": sha256_file(retrieval),
            "source_combination_decision_sha256": sha256_file(
                HERE / "source-combination-decision.json"
            ),
        },
        "python_runtime": {
            "implementation": platform.python_implementation(),
            "version": sys.version,
            "platform": platform.platform(),
        },
        "locks": {
            "builder_requirements_sha256": sha256_file(
                BUILD_SCRIPTS / "requirements.txt"
            ),
            "consultant_requirements_sha256": sha256_file(
                CONSULT_SCRIPTS / "requirements.txt"
            ),
        },
        "skills": {
            "builder": inventory_receipt(
                BUILD_SKILL, ignore_runtime_caches=True
            ),
            "consultant": inventory_receipt(
                CONSULT_SKILL, ignore_runtime_caches=True
            ),
        },
    }
    report_path = output_root / "report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
