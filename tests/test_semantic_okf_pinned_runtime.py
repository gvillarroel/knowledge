"""Static contract tests for the dependency-pinned Harbor runtime."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PINNED = ROOT / "evaluations/semantic-okf-harbor/runtime/pinned"
RUNTIME = PINNED.parent
EVALUATION_ROOT = ROOT / "evaluations/semantic-okf-datasets"
sys.path.insert(0, str(EVALUATION_ROOT))

import freeze_consult_campaign as FREEZE  # noqa: E402


def load_builder():
    """Load the standalone runtime builder as a module."""

    path = PINNED / "build_runtime.py"
    spec = importlib.util.spec_from_file_location("semantic_okf_pinned_runtime", path)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


BUILDER = load_builder()


def test_pinned_runtime_inputs_are_exact_and_portable() -> None:
    binding = BUILDER.validate_inputs()
    assert binding["pi_coding_agent"] == {
        "package": "@mariozechner/pi-coding-agent",
        "version": "0.73.1",
        "integrity": (
            "sha512-gXQh3SaZmWTfVMc4Ao5+LGbVeKvzyO7tolok0nLsZgq9nGjZx/EEU3NM8C+qUnB4"
            "Nvs2rswG5qOVgLzQkq0fHQ=="
        ),
        "locked_package_count": 197,
    }
    assert set(binding["input_files"]) == {
        "dockerfile",
        "requirements",
        "package_json",
        "package_lock",
        "receipt_schema",
    }
    assert binding["input_files"]["requirements"]["path"] == "requirements.txt"
    assert all(
        len(item["sha256"]) == 64 for item in binding["input_files"].values()
    )


def test_dockerfile_pins_python_node_checksum_and_locked_npm_install() -> None:
    dockerfile = (PINNED / "Dockerfile").read_text(encoding="utf-8")
    assert dockerfile.startswith(
        "ARG PYTHON_IMAGE=python:3.12.13-slim-bookworm@"
        "sha256:d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b\n"
    )
    assert "node-v22.23.1-linux-x64.tar.xz" in dockerfile
    assert "9749e988f437343b7fa832c69ded82a312e41a03116d766797ac14f6f9eee578" in dockerfile
    assert 'test "$(npm --version)" = "10.9.8"' in dockerfile
    assert "COPY requirements.txt" in dockerfile
    assert "COPY pinned/package.json pinned/package-lock.json" in dockerfile
    assert "npm ci --omit=dev" in dockerfile
    assert "0.73.1" in dockerfile
    assert "npm install --global" not in dockerfile


def test_package_lock_is_an_exact_registry_graph() -> None:
    lock = json.loads((PINNED / "package-lock.json").read_text(encoding="utf-8"))
    assert lock["lockfileVersion"] == 3
    assert lock["packages"][""]["dependencies"] == {
        "@mariozechner/pi-coding-agent": "0.73.1"
    }
    assert all(
        {"version", "resolved", "integrity"} <= set(package)
        for path, package in lock["packages"].items()
        if path
    )


def test_receipt_conforms_to_checked_in_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    binding = BUILDER.validate_inputs()
    receipt = BUILDER.make_receipt(
        tag="semantic-okf-harbor-runtime:2.0",
        image_id="sha256:" + "1" * 64,
        repo_digests=["semantic-okf-harbor-runtime@sha256:" + "2" * 64],
        observed_python="3.12.13",
        observed_node="v22.23.1",
        observed_npm="10.9.8",
        observed_pi="0.73.1",
        observed_model_weights=False,
        binding=binding,
    )
    schema = json.loads(
        (PINNED / "runtime-build.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema).validate(receipt)
    assert receipt["base_image"] == {
        "reference": "python:3.12.13-slim-bookworm",
        "digest": (
            "sha256:d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b"
        ),
    }


def test_receipt_rejects_observed_component_drift() -> None:
    with pytest.raises(BUILDER.InputError, match="node: expected 22.23.1"):
        BUILDER.make_receipt(
            tag="semantic-okf-harbor-runtime:2.0",
            image_id="sha256:" + "1" * 64,
            repo_digests=[],
            observed_python="3.12.13",
            observed_node="v22.23.0",
            observed_npm="10.9.8",
            observed_pi="0.73.1",
            observed_model_weights=False,
            binding=BUILDER.validate_inputs(),
        )

    with pytest.raises(BUILDER.InputError, match="contains Hugging Face model files"):
        BUILDER.make_receipt(
            tag="semantic-okf-harbor-runtime:2.0",
            image_id="sha256:" + "1" * 64,
            repo_digests=[],
            observed_python="3.12.13",
            observed_node="v22.23.1",
            observed_npm="10.9.8",
            observed_pi="0.73.1",
            observed_model_weights=True,
            binding=BUILDER.validate_inputs(),
        )


def test_runtime_inspection_executes_the_pi_entrypoint(monkeypatch) -> None:
    commands: list[list[str]] = []

    def run(command: list[str]) -> str:
        commands.append(command)
        if command[1:4] == ["image", "inspect", "--format"]:
            if command[4] == "{{.Id}}":
                return "sha256:" + "1" * 64
            return "[]"
        entrypoint = command[command.index("--entrypoint") + 1]
        if entrypoint == "python" and "/models/huggingface" in command[-1]:
            return "false"
        return {
            "python": "3.12.13",
            "node": "v22.23.1",
            "npm": "10.9.8",
            "pi": "0.73.1",
        }[entrypoint]

    monkeypatch.setattr(BUILDER, "run", run)
    receipt = BUILDER.inspect_receipt(
        "fixture-docker",
        "semantic-okf-harbor-runtime:2.0",
        BUILDER.validate_inputs(),
    )

    assert receipt["pi_coding_agent"]["observed_version"] == "0.73.1"
    assert any(
        "--entrypoint" in command
        and command[command.index("--entrypoint") + 1] == "pi"
        and command[-1] == "--version"
        for command in commands
    )


def test_campaign_freeze_reprobes_the_receipted_runtime(
    tmp_path: Path, monkeypatch
) -> None:
    receipt = json.loads(
        (PINNED / "build/runtime-build.json").read_text(encoding="utf-8")
    )
    receipt_path = tmp_path / "runtime-build.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(FREEZE, "PINNED_RUNTIME_RECEIPT", receipt_path)
    monkeypatch.setattr(FREEZE.runtime_builder, "validate_inputs", lambda: {"pins": True})

    def inspect(docker, tag, binding):
        assert binding == {"pins": True}
        calls.append((docker, tag))
        return receipt

    monkeypatch.setattr(FREEZE.runtime_builder, "inspect_receipt", inspect)
    assert FREEZE._load_runtime_receipt("fixture-docker") == receipt
    assert calls == [("fixture-docker", receipt["image_tag"])]

    tampered = dict(receipt)
    tampered["image_id"] = "sha256:" + "0" * 64
    receipt_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(FREEZE.FreezeError, match="fresh offline component attestation"):
        FREEZE._load_runtime_receipt("fixture-docker")


def test_campaign_publication_is_atomic_no_clobber(tmp_path: Path) -> None:
    source = tmp_path / "prepared"
    destination = tmp_path / "campaign"
    source.mkdir()
    destination.mkdir()
    (source / "source.txt").write_text("source", encoding="utf-8")
    (destination / "claim.txt").write_text("claim", encoding="utf-8")

    with pytest.raises(FREEZE.FreezeError, match="destination already exists"):
        FREEZE._publish_directory_no_clobber(source, destination)

    assert (source / "source.txt").read_text(encoding="utf-8") == "source"
    assert (destination / "claim.txt").read_text(encoding="utf-8") == "claim"

    unclaimed_source = tmp_path / "prepared-unclaimed"
    unclaimed_destination = tmp_path / "campaign-unclaimed"
    unclaimed_source.mkdir()
    (unclaimed_source / "ready.txt").write_text("ready", encoding="utf-8")
    FREEZE._publish_directory_no_clobber(unclaimed_source, unclaimed_destination)
    assert not unclaimed_source.exists()
    assert (unclaimed_destination / "ready.txt").read_text(encoding="utf-8") == "ready"


def test_campaign_publication_rechecks_zero_call_source(tmp_path: Path) -> None:
    temporary = tmp_path / "prepared"
    campaign = tmp_path / "campaign"
    source_campaign = tmp_path / "source-campaign"
    temporary.mkdir()
    (source_campaign / "runs/0001").mkdir(parents=True)
    (source_campaign / "runs/0001/result.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FREEZE.FreezeError, match="zero-call migration"):
        FREEZE._publish_prepared_campaign(temporary, campaign, source_campaign)

    assert temporary.is_dir()
    assert not campaign.exists()


def test_zero_call_source_allows_only_the_empty_legacy_launcher_lease(
    tmp_path: Path,
) -> None:
    source_campaign = tmp_path / "source-campaign"
    launcher_log = source_campaign / "launcher-logs/0001.log"
    launcher_log.parent.mkdir(parents=True)
    launcher_log.write_text("launch attempted\n", encoding="utf-8")

    with pytest.raises(FREEZE.FreezeError, match="launcher artifacts"):
        FREEZE._require_unused_source_campaign(source_campaign)

    launcher_log.unlink()
    legacy_lock = launcher_log.parent / "deferred-live.lock"
    legacy_lock.touch()
    FREEZE._require_unused_source_campaign(source_campaign)

    legacy_lock.write_text("not an empty lease", encoding="utf-8")
    with pytest.raises(FREEZE.FreezeError, match="launcher artifacts"):
        FREEZE._require_unused_source_campaign(source_campaign)


def test_campaign_model_migration_is_bound_to_the_verified_source_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    source_campaign = tmp_path / "source-campaign"
    source_hub = source_campaign / "frozen/model-cache/hub"
    source_hub.mkdir(parents=True)
    destination = tmp_path / "destination-hub"
    expected = {"tree_sha256": "1" * 64}
    calls: list[tuple[Path, Path, dict[str, str]]] = []

    monkeypatch.setattr(
        FREEZE.binding,
        "verify_frozen_inputs",
        lambda campaign: {"offline_model": expected},
    )

    def rematerialize(source, target, descriptor):
        calls.append((source, target, descriptor))
        return descriptor

    monkeypatch.setattr(
        FREEZE.binding, "rematerialize_hf_runtime_closure", rematerialize
    )
    result = FREEZE._materialize_model_input(
        source_campaign=source_campaign,
        hf_cache=source_hub,
        destination_hub=destination,
    )

    assert result == expected
    assert calls == [(source_hub, destination, expected)]
