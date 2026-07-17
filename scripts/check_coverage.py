from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SUMMARY_RE = re.compile(
    r"^\s*(?P<lines>\d+)\s+(?P<pct>\d+(?:\.\d+)?)%\s+(?P<module>[\w\.]+)\s+\((?P<path>.+)\)\s*$"
)
NON_APPLICATION_TESTS = (
    "tests/test_build_semantic_okf_embeddings_skill.py",
    "tests/test_build_semantic_okf_skill.py",
    "tests/test_consult_semantic_okf_embeddings_skill.py",
    "tests/test_consult_semantic_okf_skill.py",
    "tests/test_extract_ontologies_skill.py",
    "tests/test_graphify_semantic_okf_skills.py",
    "tests/test_graphify_storage_comparison.py",
    "tests/test_graphrag_okf_graphify.py",
    "tests/test_roundtrip_confluence_pages_skill.py",
    "tests/test_roundtrip_confluence_batch_skill.py",
    "tests/test_confluence_8h_campaign.py",
    "tests/test_confluence_8h_live_fixtures.py",
    "tests/test_skill_independence.py",
    "tests/test_graphrag_cross_paper_benchmark.py",
    "tests/test_semantic_okf_builder_benchmark.py",
    "tests/test_semantic_okf_embeddings_comparison.py",
    "tests/test_semantic_okf_reader_benchmark.py",
    "tests/test_semantic_okf_storage_versions_comparison.py",
    "tests/test_turso_semantic_okf_skills.py",
)


@dataclass
class ModuleCoverage:
    lines: int
    pct: float
    module: str
    path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run unit tests under trace and enforce a minimum total application coverage threshold.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Minimum required total application coverage percentage.",
    )
    parser.add_argument(
        "--package-prefix",
        default="knowledge.",
        help="Only modules with this prefix are included in the application coverage total.",
    )
    parser.add_argument(
        "--include-non-application-tests",
        action="store_true",
        help=(
            "Also trace repository skill/evaluation suites that do not import the measured "
            "application package."
        ),
    )
    parser.add_argument(
        "--tests-args",
        nargs=argparse.REMAINDER,
        help="Optional extra arguments passed to pytest after `--`.",
    )
    return parser.parse_args()


def coverage_pytest_args(args: argparse.Namespace) -> list[str]:
    """Build the pytest scope that contributes to application-package coverage."""

    pytest_args = list(args.tests_args or [])
    if args.include_non_application_tests:
        return pytest_args
    return [
        *(f"--ignore={path}" for path in NON_APPLICATION_TESTS),
        *pytest_args,
    ]


def trace_environment(repo_root: Path) -> dict[str, str]:
    """Prioritize this checkout over an unrelated editable installation."""

    env = os.environ.copy()
    local_paths = [str(repo_root / "src"), str(repo_root)]
    inherited = env.get("PYTHONPATH")
    if inherited:
        local_paths.append(inherited)
    env["PYTHONPATH"] = os.pathsep.join(local_paths)
    return env


def run_trace(coverdir: Path, pytest_args: list[str]) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    python_lib = Path(sys.base_prefix) / "Lib"
    site_packages = python_lib / "site-packages"
    ignore_dirs = os.pathsep.join(
        [
            str(python_lib),
            str(site_packages),
        ]
    )
    command = [
        sys.executable,
        "-m",
        "trace",
        "--count",
        "--summary",
        "--missing",
        "--coverdir",
        str(coverdir),
        "--ignore-dir",
        ignore_dirs,
        "--module",
        "pytest",
        "-q",
        *pytest_args,
    ]
    result = subprocess.run(
        command,
        cwd=repo_root,
        env=trace_environment(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return result.stdout


def parse_summary(output: str, package_prefix: str) -> list[ModuleCoverage]:
    rows: list[ModuleCoverage] = []
    for line in output.splitlines():
        match = SUMMARY_RE.match(line)
        if not match:
            continue
        module = match.group("module")
        if not module.startswith(package_prefix):
            continue
        rows.append(
            ModuleCoverage(
                lines=int(match.group("lines")),
                pct=float(match.group("pct")),
                module=module,
                path=match.group("path"),
            )
        )
    if not rows:
        raise SystemExit("No application coverage rows were parsed from trace output.")
    return rows


def total_pct(rows: list[ModuleCoverage]) -> float:
    total_lines = sum(row.lines for row in rows)
    covered_lines = sum(row.lines * row.pct / 100.0 for row in rows)
    return round((covered_lines / total_lines) * 100.0, 1)


def main() -> int:
    args = parse_args()
    pytest_args = coverage_pytest_args(args)

    repo_root = Path(__file__).resolve().parents[1]
    coverdir = repo_root / "tracecov"
    shutil.rmtree(coverdir, ignore_errors=True)
    coverdir.mkdir(parents=True, exist_ok=True)

    output = run_trace(coverdir, pytest_args)
    rows = parse_summary(output, args.package_prefix)
    total = total_pct(rows)

    print(f"\nApplication coverage total: {total:.1f}%")
    print(f"Coverage threshold: {args.threshold:.1f}%")

    low_rows = sorted(rows, key=lambda row: row.pct)[:5]
    print("Lowest modules:")
    for row in low_rows:
        print(f"- {row.module}: {row.pct:.1f}% ({row.lines} lines)")

    if total < args.threshold:
        print("Coverage gate failed.")
        return 1

    print("Coverage gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
