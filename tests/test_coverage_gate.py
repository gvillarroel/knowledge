from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_SCRIPT = REPO_ROOT / "scripts" / "check_coverage.py"


def load_coverage_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("knowledge_coverage_gate", COVERAGE_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_coverage_scope_skips_only_non_application_suites_by_default() -> None:
    coverage = load_coverage_script()
    args = argparse.Namespace(include_non_application_tests=False, tests_args=["-x"])

    pytest_args = coverage.coverage_pytest_args(args)

    assert pytest_args[-1] == "-x"
    assert pytest_args[:-1] == [
        f"--ignore={path}" for path in coverage.NON_APPLICATION_TESTS
    ]


def test_coverage_scope_can_include_every_repository_test() -> None:
    coverage = load_coverage_script()
    args = argparse.Namespace(include_non_application_tests=True, tests_args=None)

    assert coverage.coverage_pytest_args(args) == []
