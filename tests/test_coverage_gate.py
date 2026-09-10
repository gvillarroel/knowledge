from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest


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


def test_coverage_scope_excludes_skill_suites_with_package_local_dependencies() -> None:
    coverage = load_coverage_script()

    assert {
        "tests/test_build_semantic_okf_tantivy_skill.py",
        "tests/test_consult_semantic_okf_tika_mallet_bounded_skill.py",
        "tests/test_consult_semantic_okf_tika_mallet_tantivy_skill.py",
        "tests/test_visualize_semantic_okf_classical_skill.py",
    } <= set(coverage.NON_APPLICATION_TESTS)


def test_trace_environment_prioritizes_the_current_checkout(
    monkeypatch,
) -> None:
    coverage = load_coverage_script()
    monkeypatch.setenv("PYTHONPATH", "C:/external/package")

    env = coverage.trace_environment(REPO_ROOT)
    entries = env["PYTHONPATH"].split(os.pathsep)

    assert entries[:2] == [str(REPO_ROOT / "src"), str(REPO_ROOT)]
    assert entries[2] == "C:/external/package"


@pytest.mark.parametrize(
    ("source", "extra_args", "exit_code"),
    [
        ("def test_outcome():\n    assert True\n", [], 0),
        ("def test_outcome():\n    assert False\n", [], 1),
        ("raise RuntimeError('collection failure')\n", [], 2),
        ("def test_outcome():\n    assert True\n", ["--unknown-coverage-test-option"], 4),
        ("# No tests collected.\n", [], 5),
    ],
)
def test_real_trace_preserves_pytest_exit_status(
    tmp_path: Path, monkeypatch, capsys, source: str, extra_args: list[str], exit_code: int,
) -> None:
    coverage = load_coverage_script()
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    config = tmp_path / "pytest.ini"
    config.write_text("[pytest]\n", encoding="utf-8")
    probe = tmp_path / "test_probe.py"
    probe.write_text(source, encoding="utf-8")
    coverdir = tmp_path / "coverage"
    pytest_args = ["-c", str(config), str(probe), *extra_args]

    if exit_code:
        with pytest.raises(SystemExit) as error:
            coverage.run_trace(coverdir, pytest_args)
        assert error.value.code == exit_code
    else:
        output = coverage.run_trace(coverdir, pytest_args)
        assert "1 passed" in output
        assert coverage.parse_summary(output, "test_probe")

    if exit_code in (0, 1, 2):
        # Coverage artifacts must survive unsuccessful execution too.
        assert (coverdir / "test_probe.cover").is_file()
    captured = capsys.readouterr()
    if exit_code == 1:
        assert "1 failed" in captured.out
    if exit_code == 4:
        assert "unrecognized arguments" in captured.err
