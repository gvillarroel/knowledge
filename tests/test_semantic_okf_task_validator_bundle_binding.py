"""Tests for generated-task validation against the exact reference bundle."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = (
    REPO / "evaluations/semantic-okf-datasets/validate_harbor_tasks.py"
)


def load_validator() -> ModuleType:
    """Load the task validator without requiring a package import path."""

    spec = importlib.util.spec_from_file_location(
        "semantic_okf_task_validator_bundle_binding", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def write_manifest(task_root: Path, bundle_hash: str) -> None:
    """Write the manifest fields needed by the bundle-binding preflight."""

    task_root.mkdir(parents=True)
    (task_root / "manifest.json").write_text(
        json.dumps(
            {
                "reference_bundle_tree_sha256": bundle_hash,
                "agent_network_mode": "public",
                "verifier_network_mode": "public",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def write_reference_bundle(bundle: Path) -> None:
    """Write the minimum checked reference-bundle shape used by the preflight."""

    (bundle / "semantic").mkdir(parents=True)
    (bundle / "index.md").write_text("default\n", encoding="utf-8")
    (bundle / "semantic/records.jsonl").write_text("{}\n", encoding="utf-8")


def test_implicit_nondefault_bundle_fails_before_task_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    validator = load_validator()
    task_root = tmp_path / "tasks"
    default_bundle = tmp_path / "default-bundle"
    write_reference_bundle(default_bundle)
    pinned_hash = "f" * 64
    write_manifest(task_root, pinned_hash)

    monkeypatch.setattr(
        validator.data,
        "load_dataset",
        lambda _dataset_id: {"reference_bundle": "checked/default"},
    )
    monkeypatch.setattr(
        validator.data,
        "repo_path",
        lambda _value, _label: default_bundle,
    )

    def unexpected_validation(*_args: object, **_kwargs: object) -> dict[str, object]:
        pytest.fail("task validation must not run after an implicit bundle mismatch")

    monkeypatch.setattr(validator, "validate", unexpected_validation)

    with pytest.raises(SystemExit) as raised:
        validator.main(
            [
                "--dataset",
                "graphrag-papers-40",
                "--family",
                "adaptive",
                "--mode",
                "consult-only",
                "--tasks",
                str(task_root),
            ]
        )

    message = str(raised.value)
    assert pinned_hash in message
    assert validator.data.tree_digest(default_bundle) in message
    assert "--bundle <path-to-exact-adaptive-bundle>" in message
    assert "exact adaptive bundle" in message


def test_matching_default_bundle_preserves_validation_behavior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    validator = load_validator()
    task_root = tmp_path / "tasks"
    default_bundle = tmp_path / "default-bundle"
    write_reference_bundle(default_bundle)
    write_manifest(task_root, validator.data.tree_digest(default_bundle))

    monkeypatch.setattr(
        validator.data,
        "load_dataset",
        lambda _dataset_id: {"reference_bundle": "checked/default"},
    )
    monkeypatch.setattr(
        validator.data,
        "repo_path",
        lambda _value, _label: default_bundle,
    )
    monkeypatch.setattr(
        validator,
        "validate",
        lambda *_args: {"status": "pass", "task_count": 40},
    )

    assert (
        validator.main(
            [
                "--dataset",
                "graphrag-papers-40",
                "--family",
                "legacy",
                "--mode",
                "consult-only",
                "--tasks",
                str(task_root),
                "--skip-generation-check",
            ]
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "pass"
    assert report["deterministic"] is False


def test_explicit_bundle_is_forwarded_to_deterministic_regeneration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    validator = load_validator()
    task_root = tmp_path / "tasks"
    explicit_bundle = tmp_path / "adaptive-bundle"
    write_manifest(task_root, "a" * 64)
    explicit_bundle.mkdir()

    monkeypatch.setattr(
        validator.data,
        "load_dataset",
        lambda _dataset_id: {"reference_bundle": "checked/default"},
    )
    monkeypatch.setattr(
        validator,
        "validate",
        lambda *_args: {"status": "pass", "task_count": 40},
    )
    calls: list[list[str]] = []

    def record_run(command: list[str], **_kwargs: object) -> None:
        calls.append(command)

    monkeypatch.setattr(validator.subprocess, "run", record_run)

    assert (
        validator.main(
            [
                "--dataset",
                "graphrag-papers-40",
                "--family",
                "adaptive",
                "--mode",
                "consult-only",
                "--tasks",
                str(task_root),
                "--bundle",
                str(explicit_bundle),
            ]
        )
        == 0
    )
    assert len(calls) == 1
    bundle_index = calls[0].index("--bundle")
    assert calls[0][bundle_index + 1] == str(explicit_bundle.resolve())
    assert json.loads(capsys.readouterr().out)["deterministic"] is True
