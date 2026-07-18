"""Adversarial tests for frozen Semantic OKF campaign inputs."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import pytest

EVALUATION_ROOT = (
    Path(__file__).resolve().parents[1] / "evaluations" / "semantic-okf-datasets"
)
sys.path.insert(0, str(EVALUATION_ROOT))

import campaign_binding as BINDING  # noqa: E402


def _small_hf_source(tmp_path: Path, monkeypatch) -> tuple[Path, dict[str, bytes]]:
    hub = tmp_path / "source-hub"
    snapshot = (
        hub
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
    )
    (hub / BINDING.HF_REPOSITORY_DIRECTORY / "blobs").mkdir(parents=True)
    contents = {
        "1_Pooling/config.json": b'{"pooling":"mean"}\n',
        "config.json": b'{"model":"fixture"}\n',
    }
    expected: dict[str, tuple[int, str]] = {}
    for relative, payload in contents.items():
        path = snapshot / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        expected[relative] = (len(payload), hashlib.sha256(payload).hexdigest())
    monkeypatch.setattr(BINDING, "HF_EXPECTED_FILES", expected)
    return hub, contents


def test_hf_runtime_closure_is_independent_regular_and_closed(
    tmp_path: Path, monkeypatch
) -> None:
    source, contents = _small_hf_source(tmp_path, monkeypatch)
    destination = tmp_path / "campaign-hub"

    descriptor = BINDING.materialize_hf_runtime_closure(source, destination)
    BINDING.verify_hf_runtime_closure(destination, descriptor)
    staged = (
        destination
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
    )
    assert descriptor["file_count"] == 2
    assert descriptor["total_bytes"] == sum(map(len, contents.values()))
    assert all(path.is_file() and not path.is_symlink() for path in staged.rglob("*") if not path.is_dir())

    source_config = (
        source
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
        / "config.json"
    )
    source_config.write_text("mutated source\n", encoding="utf-8")
    assert (staged / "config.json").read_bytes() == contents["config.json"]

    (staged / "unexpected.env").write_text("not allowed\n", encoding="utf-8")
    with pytest.raises(BINDING.BindingError, match="qualified model file inventory"):
        BINDING.verify_hf_runtime_closure(destination, descriptor)


def test_hf_runtime_closure_can_be_rematerialized_from_a_closed_campaign(
    tmp_path: Path, monkeypatch
) -> None:
    if os.name != "posix":
        pytest.skip("secure closed-campaign rematerialization requires POSIX")
    source, contents = _small_hf_source(tmp_path, monkeypatch)
    first_campaign = tmp_path / "first-campaign-hub"
    second_campaign = tmp_path / "second-campaign-hub"

    first_descriptor = BINDING.materialize_hf_runtime_closure(
        source, first_campaign
    )
    second_descriptor = BINDING.rematerialize_hf_runtime_closure(
        first_campaign, second_campaign, first_descriptor
    )

    assert second_descriptor == first_descriptor
    second_snapshot = (
        second_campaign
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
    )
    assert {
        path.relative_to(second_snapshot).as_posix(): path.read_bytes()
        for path in second_snapshot.rglob("*")
        if path.is_file()
    } == contents
    assert all(
        path.is_file() and not path.is_symlink()
        for path in second_snapshot.rglob("*")
        if not path.is_dir()
    )
    first_config = (
        first_campaign
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
        / "config.json"
    )
    first_config.write_text("mutated after migration\n", encoding="utf-8")
    assert (second_snapshot / "config.json").read_bytes() == contents["config.json"]


def test_hf_rematerialization_rejects_an_unqualified_closed_source(
    tmp_path: Path, monkeypatch
) -> None:
    if os.name != "posix":
        pytest.skip("secure closed-campaign rematerialization requires POSIX")
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed_source = tmp_path / "closed-source"
    BINDING.materialize_hf_runtime_closure(source, closed_source)
    snapshot = (
        closed_source
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
    )
    (snapshot / "unexpected.txt").write_text("not qualified\n", encoding="utf-8")

    with pytest.raises(BINDING.BindingError, match="qualified model file inventory"):
        BINDING.rematerialize_hf_runtime_closure(
            closed_source, tmp_path / "destination", {}
        )


def test_hf_closed_layout_rejects_unexpected_hub_and_repository_entries(
    tmp_path: Path, monkeypatch
) -> None:
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed = tmp_path / "closed"
    descriptor = BINDING.materialize_hf_runtime_closure(source, closed)

    (closed / "unexpected-model").mkdir()
    with pytest.raises(BINDING.BindingError, match="closure hub contains"):
        BINDING.verify_hf_runtime_closure(closed, descriptor)
    (closed / "unexpected-model").rmdir()

    repository = closed / BINDING.HF_REPOSITORY_DIRECTORY
    (repository / "blobs").mkdir()
    with pytest.raises(BINDING.BindingError, match="closure repository contains"):
        BINDING.verify_hf_runtime_closure(closed, descriptor)


def test_hf_closed_layout_rejects_a_symlinked_path_component(
    tmp_path: Path, monkeypatch
) -> None:
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed = tmp_path / "closed"
    descriptor = BINDING.materialize_hf_runtime_closure(source, closed)
    real_repository = closed / BINDING.HF_REPOSITORY_DIRECTORY
    moved_repository = tmp_path / "moved-repository"
    real_repository.rename(moved_repository)
    try:
        os.symlink(moved_repository, real_repository, target_is_directory=True)
    except OSError:
        pytest.skip("directory symbolic links are unavailable to this test process")

    with pytest.raises(BINDING.BindingError, match="not a plain directory"):
        BINDING.verify_hf_runtime_closure(closed, descriptor)


def test_hf_closed_layout_rejects_a_junction_like_path_component(
    tmp_path: Path, monkeypatch
) -> None:
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed = tmp_path / "closed"
    descriptor = BINDING.materialize_hf_runtime_closure(source, closed)
    repository = closed / BINDING.HF_REPOSITORY_DIRECTORY
    original = getattr(Path, "is_junction", None)

    def is_junction(path: Path) -> bool:
        return path == repository or (original is not None and original(path))

    monkeypatch.setattr(Path, "is_junction", is_junction, raising=False)
    with pytest.raises(BINDING.BindingError, match="not a plain directory"):
        BINDING.verify_hf_runtime_closure(closed, descriptor)


def test_hf_closed_layout_rejects_a_shared_hardlink(
    tmp_path: Path, monkeypatch
) -> None:
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed = tmp_path / "closed"
    descriptor = BINDING.materialize_hf_runtime_closure(source, closed)
    config = (
        closed
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
        / "config.json"
    )
    alias = tmp_path / "config-hardlink.json"
    try:
        os.link(config, alias)
    except OSError:
        pytest.skip("hardlinks are unavailable to this test process")

    with pytest.raises(BINDING.BindingError, match="shared hardlink"):
        BINDING.verify_hf_runtime_closure(closed, descriptor)


def test_hf_rematerialization_rejects_a_preexisting_destination(
    tmp_path: Path, monkeypatch
) -> None:
    if os.name != "posix":
        pytest.skip("secure closed-campaign rematerialization requires POSIX")
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed = tmp_path / "closed"
    descriptor = BINDING.materialize_hf_runtime_closure(source, closed)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(BINDING.BindingError, match="destination already exists"):
        BINDING.rematerialize_hf_runtime_closure(
            closed, destination, descriptor
        )


def test_hf_rematerialization_rejects_source_mutation_during_copy(
    tmp_path: Path, monkeypatch
) -> None:
    if os.name != "posix":
        pytest.skip("secure closed-campaign rematerialization requires POSIX")
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed = tmp_path / "closed"
    descriptor = BINDING.materialize_hf_runtime_closure(source, closed)
    source_config = (
        closed
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
        / "config.json"
    )
    original_copy = BINDING.shutil.copyfileobj
    calls = 0

    def mutating_copy(source_stream, target_stream, length):
        nonlocal calls
        original_copy(source_stream, target_stream, length)
        calls += 1
        if calls == 1:
            source_config.write_text("mutated\n", encoding="utf-8")

    monkeypatch.setattr(BINDING.shutil, "copyfileobj", mutating_copy)
    with pytest.raises(BINDING.BindingError, match="source HF closure changed"):
        BINDING.rematerialize_hf_runtime_closure(
            closed, tmp_path / "destination", descriptor
        )


def test_hf_rematerialization_does_not_block_on_a_raced_fifo(
    tmp_path: Path, monkeypatch
) -> None:
    if os.name != "posix" or not hasattr(os, "mkfifo"):
        pytest.skip("FIFO no-block validation requires POSIX")
    source, _contents = _small_hf_source(tmp_path, monkeypatch)
    closed = tmp_path / "closed"
    descriptor = BINDING.materialize_hf_runtime_closure(source, closed)
    config = (
        closed
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
        / "config.json"
    )
    original_open_source = BINDING._open_attested_hf_source_files
    raced = False

    @contextlib.contextmanager
    def racing_open_source(source_hub, expected):
        nonlocal raced
        raced = True
        config.unlink()
        os.mkfifo(config)
        with original_open_source(source_hub, expected) as source_files:
            yield source_files

    monkeypatch.setattr(
        BINDING, "_open_attested_hf_source_files", racing_open_source
    )
    started = time.monotonic()
    with pytest.raises(BINDING.BindingError, match="differs from its manifest"):
        BINDING.rematerialize_hf_runtime_closure(
            closed, tmp_path / "destination", descriptor
        )
    assert raced
    assert time.monotonic() - started < 2.0


def test_hf_materialization_rejects_a_link_outside_the_blob_store(
    tmp_path: Path, monkeypatch
) -> None:
    hub = tmp_path / "source-hub"
    snapshot = (
        hub
        / BINDING.HF_REPOSITORY_DIRECTORY
        / "snapshots"
        / BINDING.HF_REVISION
    )
    (hub / BINDING.HF_REPOSITORY_DIRECTORY / "blobs").mkdir(parents=True)
    snapshot.mkdir(parents=True)
    external = tmp_path / "external.json"
    external.write_text("outside\n", encoding="utf-8")
    link = snapshot / "config.json"
    try:
        os.symlink(external, link)
    except OSError:
        pytest.skip("symbolic links are unavailable to this test process")
    monkeypatch.setattr(
        BINDING,
        "HF_EXPECTED_FILES",
        {"config.json": (8, hashlib.sha256(b"outside\n").hexdigest())},
    )

    with pytest.raises(BINDING.BindingError, match="escapes its blob store"):
        BINDING.materialize_hf_runtime_closure(hub, tmp_path / "destination")


def _write_task_matrix(repo: Path, image: str) -> None:
    root = (
        repo
        / "evaluations/semantic-okf-datasets/generated/tasks"
        / "graphrag-papers-40/consult-only"
    )
    for family_number in range(8):
        family = f"family-{family_number}"
        family_root = root / family
        (family_root / "manifest.json").parent.mkdir(parents=True, exist_ok=True)
        (family_root / "manifest.json").write_text(
            json.dumps({"runtime_image": image}), encoding="utf-8"
        )
        for question_number in range(1, 41):
            task = family_root / "discovery" / f"q{question_number:03d}"
            task.mkdir(parents=True)
            (task / "task.toml").write_text(
                f'[environment]\ndocker_image = "{image}"\n', encoding="utf-8"
            )
            tests = task / "tests"
            tests.mkdir()
            (tests / "Dockerfile").write_text(f"FROM {image}\n", encoding="utf-8")


def test_frozen_task_matrix_requires_one_content_addressed_image_tag(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    image_id = "sha256:" + "1" * 64
    image = BINDING.runtime_image_reference(image_id)
    _write_task_matrix(repo, image)

    binding = BINDING.task_runtime_references(repo, "graphrag-papers-40")
    assert binding == {
        "manifest_count": 8,
        "task_count": 320,
        "verifier_dockerfile_count": 320,
        "runtime_image_reference": image,
        "runtime_image_id": image_id,
    }

    changed = next(repo.glob("**/q001/task.toml"))
    changed.write_text(
        '[environment]\ndocker_image = "semantic-okf-harbor-runtime:2.0"\n',
        encoding="utf-8",
    )
    with pytest.raises(BINDING.BindingError, match="do not share"):
        BINDING.task_runtime_references(repo, "graphrag-papers-40")


def test_harbor_pi_patch_removes_live_nvm_and_npm_install(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "vendor"
    pi = root / "harbor/agents/installed/pi.py"
    pi.parent.mkdir(parents=True)
    source = '''class Pi:
    def get_version_command(self):
        return ". ~/.nvm/nvm.sh; pi --version"

    async def install(self, environment):
        await self.exec_as_root(
            environment,
            command="apt-get update && apt-get install -y curl",
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )
        version_spec = f"@{self._version}" if self._version else "@latest"
        await self.exec_as_agent(
            environment,
            command=(
                "set -euo pipefail; "
                f"{nvm_node_install_snippet()} && "
                f"npm install -g @mariozechner/pi-coding-agent{version_spec} && "
                "pi --version"
            ),
        )

    async def run(self):
        command = (f". ~/.nvm/nvm.sh; " f"pi --print")
'''
    pi.write_text(source, encoding="utf-8")
    monkeypatch.setattr(BINDING, "HARBOR_PI_SOURCE_SHA256", BINDING.sha256_file(pi))

    hashes = BINDING.patch_harbor_pi_for_pinned_runtime(root)
    patched = pi.read_text(encoding="utf-8")

    assert hashes["patched_sha256"] == BINDING.sha256_file(pi)
    assert "npm install -g" not in patched
    assert "nvm_node_install_snippet()" not in patched
    assert 'test "$(node --version)" = "v22.23.1"' in patched
    assert 'return "pi --version"' in patched


def test_frozen_manifest_sidecar_is_canonical_and_tamper_evident(
    tmp_path: Path,
) -> None:
    path = tmp_path / "frozen-inputs.json"
    value = {"schema_version": "fixture", "value": 1}
    digest = BINDING.write_canonical_exclusive(path, value)

    assert digest == BINDING.sha256_file(path)
    assert path.read_bytes() == BINDING.canonical_json_bytes(value)
    path.write_text('{"value":2}\n', encoding="utf-8")
    with pytest.raises(BINDING.BindingError, match="not canonical|does not verify"):
        BINDING.load_frozen_inputs(tmp_path)
