#!/usr/bin/env python3
"""Create an atomic, campaign-local snapshot for a consult evaluation."""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import errno
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import campaign_binding as binding  # noqa: E402
import dataset_tool as data  # noqa: E402
import run_consult_campaign as runner  # noqa: E402


CAMPAIGN_PREFIX = "20260723-papers-consult-gpt53-spark-"
DATASET_ID = "graphrag-papers-40"
SOURCE_RUNTIME_TAG = "semantic-okf-harbor-runtime:1.0"
PINNED_RUNTIME = REPO / "evaluations/semantic-okf-harbor/runtime/pinned"
PINNED_RUNTIME_RECEIPT = PINNED_RUNTIME / "build/runtime-build.json"
sys.path.insert(0, str(PINNED_RUNTIME))

import build_runtime as runtime_builder  # noqa: E402


class FreezeError(ValueError):
    """Raised when an atomic campaign snapshot cannot be prepared safely."""


def _copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FreezeError(f"required snapshot source is absent: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination, follow_symlinks=True)


def _ignore_transient_bytecode(_directory: str, names: list[str]) -> set[str]:
    """Exclude mutable interpreter caches from every frozen source tree."""

    return {
        name
        for name in names
        if name == "__pycache__" or name.endswith((".pyc", ".pyo"))
    }


def _copy_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FreezeError(f"required snapshot tree is absent: {source}")
    if destination.exists():
        raise FreezeError(f"snapshot destination already exists: {destination}")
    shutil.copytree(
        source,
        destination,
        symlinks=False,
        copy_function=shutil.copy2,
        ignore=_ignore_transient_bytecode,
    )


def _load_runtime_receipt(docker: str) -> dict[str, Any]:
    try:
        value = json.loads(PINNED_RUNTIME_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FreezeError(
            "the pinned runtime must be built and recorded before freezing a campaign"
        ) from exc
    if not isinstance(value, dict):
        raise FreezeError("pinned runtime receipt must be a JSON object")
    image_id = value.get("image_id")
    if (
        value.get("image_tag") != "semantic-okf-harbor-runtime:2.0"
        or not isinstance(image_id, str)
        or not image_id.startswith("sha256:")
        or not binding.SHA256.fullmatch(image_id[7:])
    ):
        raise FreezeError("pinned runtime receipt has an invalid image identity")
    try:
        observed = runtime_builder.inspect_receipt(
            docker,
            str(value["image_tag"]),
            runtime_builder.validate_inputs(),
        )
    except Exception as exc:  # noqa: BLE001 - normalize Docker and pin validation failures
        raise FreezeError(
            "pinned runtime failed a fresh offline component attestation"
        ) from exc
    if observed != value:
        raise FreezeError(
            "pinned runtime receipt differs from a fresh offline component attestation"
        )
    return value


def _harbor_source(harbor: Path) -> tuple[Path, Path, str]:
    executable = harbor.expanduser().resolve()
    if not executable.is_file():
        raise FreezeError(f"Harbor executable is absent: {executable}")
    try:
        first_line = executable.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, UnicodeError, IndexError) as exc:
        raise FreezeError("Harbor executable has no readable Python shebang") from exc
    if not first_line.startswith("#!/"):
        raise FreezeError("Harbor executable is not a pinned Python entrypoint")
    interpreter = Path(first_line[2:]).expanduser()
    if not interpreter.is_absolute() or not interpreter.is_file():
        raise FreezeError("Harbor shebang does not name an absolute interpreter")
    script = (
        "import importlib.metadata as m,json,pathlib,harbor;"
        "print(json.dumps({'root':str(pathlib.Path(harbor.__file__).parent),"
        "'version':m.version('harbor')}))"
    )
    completed = subprocess.run(
        [str(interpreter), "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise FreezeError("cannot locate the selected Harbor distribution") from exc
    root = Path(str(result.get("root", ""))).resolve()
    version = str(result.get("version", ""))
    if completed.returncode != 0 or not root.is_dir() or version != binding.HARBOR_VERSION:
        raise FreezeError("selected Harbor distribution is not the qualified 0.18.0 build")
    return interpreter, root, version


def _rewrite_frozen_tasks(repo: Path, image_reference: str) -> None:
    root = (
        repo
        / "evaluations/semantic-okf-datasets/generated/tasks"
        / DATASET_ID
        / "consult-only"
    )
    task_files = sorted(root.glob("*/*/q*/task.toml"))
    verifier_files = sorted(root.glob("*/*/q*/tests/Dockerfile"))
    manifests = sorted(root.glob("*/manifest.json"))
    if len(task_files) != 320 or len(verifier_files) != 320 or len(manifests) != 8:
        raise FreezeError("source task matrix is incomplete")
    for path in task_files:
        source = path.read_text(encoding="utf-8")
        needle = f'docker_image = "{SOURCE_RUNTIME_TAG}"'
        if source.count(needle) != 1:
            raise FreezeError(f"task runtime tag is not canonical: {path}")
        path.write_text(
            source.replace(needle, f'docker_image = "{image_reference}"', 1),
            encoding="utf-8",
            newline="\n",
        )
    for path in verifier_files:
        source = path.read_text(encoding="utf-8")
        needle = f"FROM {SOURCE_RUNTIME_TAG}"
        if source.count(needle) != 1:
            raise FreezeError(f"verifier runtime tag is not canonical: {path}")
        path.write_text(
            source.replace(needle, f"FROM {image_reference}", 1),
            encoding="utf-8",
            newline="\n",
        )
    for path in manifests:
        value = data.load_json(path)
        if value.get("runtime_image") != SOURCE_RUNTIME_TAG:
            raise FreezeError(f"task manifest runtime tag drift: {path}")
        value["runtime_image"] = image_reference
        path.write_bytes(binding.canonical_json_bytes(value))


def _stage_repository(
    destination: Path,
    *,
    harbor_package: Path,
    harbor_interpreter: Path,
    image_reference: str,
) -> dict[str, Any]:
    for relative in binding.PIPELINE_SOURCE_PATHS:
        pure = PurePosixPath(relative)
        _copy_file(REPO / Path(*pure.parts), destination / Path(*pure.parts))

    dataset_root = Path("evaluations/semantic-okf-datasets")
    for name in ("families.json", "datasets/graphrag-papers-40.json", "datasets/graphrag-papers-40-cohorts.json"):
        pure = PurePosixPath(name)
        _copy_file(HERE / Path(*pure.parts), destination / dataset_root / Path(*pure.parts))

    task_source = HERE / "generated/tasks" / DATASET_ID / "consult-only"
    task_destination = destination / dataset_root / "generated/tasks" / DATASET_ID / "consult-only"
    _copy_tree(task_source, task_destination)

    families = data.load_families()
    for family in sorted(families):
        skill_name = str(families[family]["consult_skill"])
        _copy_tree(REPO / "skills" / skill_name, destination / "skills" / skill_name)

    _copy_tree(
        REPO / "evaluations/semantic-okf-harbor/grader",
        destination / "evaluations/semantic-okf-harbor/grader",
    )
    _copy_tree(
        PINNED_RUNTIME,
        destination / "evaluations/semantic-okf-harbor/runtime/pinned",
    )
    _copy_file(
        REPO / "evaluations/semantic-okf-harbor/runtime/requirements.txt",
        destination / "evaluations/semantic-okf-harbor/runtime/requirements.txt",
    )
    vendor = destination / "vendor"
    _copy_tree(harbor_package, vendor / "harbor")
    adapter = binding.patch_harbor_pi_for_pinned_runtime(vendor)
    wrapper = vendor / "harbor-cli"
    wrapper.write_text(
        "\n".join(
            (
                f"#!{harbor_interpreter}",
                "from harbor.cli.main import app",
                "",
                "if __name__ == '__main__':",
                "    app()",
                "",
            )
        ),
        encoding="utf-8",
        newline="\n",
    )
    binding.make_executable(wrapper)
    _rewrite_frozen_tasks(destination, image_reference)
    return {
        "harbor_version": binding.HARBOR_VERSION,
        "source_tree_sha256": data.tree_digest(harbor_package),
        **adapter,
    }


def _copy_bundles(source_campaign: Path, destination_campaign: Path) -> None:
    source = source_campaign / "bundles"
    families = sorted(data.load_families())
    if sorted(path.name for path in source.iterdir() if path.is_dir()) != families:
        raise FreezeError("source campaign does not contain exactly eight family bundles")
    for family in families:
        _copy_tree(source / family, destination_campaign / "bundles" / family)


def _absolute_without_resolving(path: Path) -> Path:
    """Return a lexical absolute path while preserving symlink evidence."""

    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _materialize_model_input(
    *,
    source_campaign: Path,
    hf_cache: Path,
    destination_hub: Path,
) -> dict[str, Any]:
    """Materialize either a raw cache or the exact verified source closure."""

    supplied = _absolute_without_resolving(hf_cache)
    source_hub = source_campaign / "frozen" / "model-cache" / "hub"
    if supplied != source_hub:
        return binding.materialize_hf_runtime_closure(supplied, destination_hub)

    for relative in ("frozen", "frozen/model-cache", "frozen/model-cache/hub"):
        path = source_campaign / relative
        junction = getattr(path, "is_junction", None)
        if path.is_symlink() or (junction is not None and junction()):
            raise FreezeError(f"source campaign model path is not a plain directory: {path}")
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise FreezeError(f"source campaign model path is absent: {path}") from exc
        if not stat.S_ISDIR(metadata.st_mode):
            raise FreezeError(f"source campaign model path is not a plain directory: {path}")
    source_manifest = binding.verify_frozen_inputs(source_campaign)
    expected_model = source_manifest.get("offline_model")
    if not isinstance(expected_model, Mapping):
        raise FreezeError("source campaign has no bound offline model descriptor")
    return binding.rematerialize_hf_runtime_closure(
        source_hub, destination_hub, expected_model
    )


def _require_unused_source_campaign(source_campaign: Path) -> None:
    for name in ("runs", "outcomes", "checkpoints"):
        root = source_campaign / name
        if root.exists() and any(root.rglob("*")):
            raise FreezeError(
                f"source campaign has evaluation artifacts and cannot be a zero-call migration: {root}"
            )
    launcher_logs = source_campaign / "launcher-logs"
    if not launcher_logs.exists():
        return
    entries = list(launcher_logs.rglob("*"))
    legacy_lock = launcher_logs / "deferred-live.lock"
    if not entries:
        return
    if (
        entries != [legacy_lock]
        or legacy_lock.is_symlink()
        or not legacy_lock.is_file()
        or legacy_lock.stat().st_size != 0
    ):
        raise FreezeError(
            "source campaign has launcher artifacts and cannot be a zero-call migration: "
            f"{launcher_logs}"
        )


@contextlib.contextmanager
def _legacy_launcher_lock(source_campaign: Path):
    """Exclude the pre-operation-lock WSL launcher for the full source migration."""

    if not sys.platform.startswith("linux"):
        raise FreezeError("legacy launcher exclusion is only supported from Linux or WSL")
    try:
        import fcntl
    except ImportError as exc:  # pragma: no cover - guarded by the platform check
        raise FreezeError("Linux flock support is required for source migration") from exc

    lock_path = source_campaign / "launcher-logs/deferred-live.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
        raise FreezeError(f"legacy launcher lease path is unsafe: {lock_path}")
    with lock_path.open("a+b") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise FreezeError("source campaign launcher is already active") from exc
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _publish_directory_no_clobber(source: Path, destination: Path) -> None:
    """Atomically publish one directory without replacing any concurrent claimant."""

    if os.name == "nt":
        try:
            os.rename(source, destination)
        except FileExistsError as exc:
            raise FreezeError(
                f"append-only campaign destination already exists: {destination}"
            ) from exc
        return
    if not sys.platform.startswith("linux"):
        raise FreezeError("atomic no-clobber publication is unsupported on this platform")

    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is None:
        raise FreezeError("Linux renameat2 is required for atomic no-clobber publication")
    renameat2.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    renameat2.restype = ctypes.c_int
    result = renameat2(
        -100,
        os.fsencode(source),
        -100,
        os.fsencode(destination),
        1,
    )
    if result == 0:
        return
    error = ctypes.get_errno()
    if error in {errno.EINVAL, errno.ENOSYS, errno.ENOTSUP}:
        _publish_windows_mount_no_clobber(source, destination)
        return
    if error in {errno.EEXIST, errno.ENOTEMPTY}:
        raise FreezeError(
            f"append-only campaign destination already exists: {destination}"
        )
    raise OSError(error, os.strerror(error), str(destination))


def _publish_windows_mount_no_clobber(source: Path, destination: Path) -> None:
    """Use Windows Directory.Move when WSL's mounted filesystem lacks renameat2."""

    converted: list[str] = []
    for path in (source, destination):
        completed = subprocess.run(
            ["wslpath", "-w", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0 or not completed.stdout.strip():
            raise FreezeError(
                "atomic no-clobber publication is unavailable for this Linux filesystem"
            )
        converted.append(completed.stdout.strip())
    environment = dict(os.environ)
    environment["SEMANTIC_OKF_PUBLISH_SOURCE"] = converted[0]
    environment["SEMANTIC_OKF_PUBLISH_DESTINATION"] = converted[1]
    inherited = [item for item in environment.get("WSLENV", "").split(":") if item]
    inherited.extend(
        ["SEMANTIC_OKF_PUBLISH_SOURCE", "SEMANTIC_OKF_PUBLISH_DESTINATION"]
    )
    environment["WSLENV"] = ":".join(dict.fromkeys(inherited))
    script = (
        "$ErrorActionPreference='Stop';"
        "[IO.Directory]::Move("
        "[Environment]::GetEnvironmentVariable('SEMANTIC_OKF_PUBLISH_SOURCE'),"
        "[Environment]::GetEnvironmentVariable('SEMANTIC_OKF_PUBLISH_DESTINATION'))"
    )
    moved = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if moved.returncode == 0:
        return
    if destination.exists():
        raise FreezeError(
            f"append-only campaign destination already exists: {destination}"
        )
    raise FreezeError(
        "Windows no-clobber directory publication failed: "
        + (moved.stderr.strip() or moved.stdout.strip())
    )


def _publish_prepared_campaign(
    temporary: Path, campaign: Path, source_campaign: Path
) -> None:
    """Recheck zero-call provenance and publish a prepared campaign no-clobber."""

    _require_unused_source_campaign(source_campaign)
    _publish_directory_no_clobber(temporary, campaign)


def _materialize_runtime_reference(docker: str, image_id: str) -> str:
    """Create and verify the content-addressed local tag required by Dockerfiles."""

    reference = binding.runtime_image_reference(image_id)
    tagged = subprocess.run(
        [docker, "image", "tag", image_id, reference],
        capture_output=True,
        text=True,
        check=False,
    )
    if tagged.returncode != 0:
        raise FreezeError(
            "cannot create the content-addressed runtime tag: "
            + (tagged.stderr.strip() or tagged.stdout.strip())
        )
    inspected = subprocess.run(
        [docker, "image", "inspect", "--format", "{{.Id}}", reference],
        capture_output=True,
        text=True,
        check=False,
    )
    if inspected.returncode != 0 or inspected.stdout.strip() != image_id:
        raise FreezeError("content-addressed runtime tag does not resolve to its bound ID")
    return reference


def prepare_campaign(
    campaign: Path,
    *,
    source_campaign: Path,
    hf_cache: Path,
    harbor: Path,
    docker: str,
) -> dict[str, Any]:
    """Prepare a campaign while excluding every source execution process."""

    source_campaign = source_campaign.resolve()
    with _legacy_launcher_lock(source_campaign):
        with runner.campaign_operation_lock(source_campaign, "freeze-source"):
            return _prepare_campaign_locked(
                campaign,
                source_campaign=source_campaign,
                hf_cache=hf_cache,
                harbor=harbor,
                docker=docker,
            )


def _prepare_campaign_locked(
    campaign: Path,
    *,
    source_campaign: Path,
    hf_cache: Path,
    harbor: Path,
    docker: str,
) -> dict[str, Any]:
    """Prepare, validate, and atomically publish one frozen campaign directory."""

    campaign = campaign.resolve()
    source_campaign = source_campaign.resolve()
    if campaign.exists():
        raise FreezeError(f"append-only campaign destination already exists: {campaign}")
    if not campaign.name.startswith(CAMPAIGN_PREFIX):
        raise FreezeError("campaign destination has an unexpected identity")
    _require_unused_source_campaign(source_campaign)
    runtime_receipt = _load_runtime_receipt(docker)
    image_id = str(runtime_receipt["image_id"])
    image_reference = _materialize_runtime_reference(docker, image_id)
    harbor_interpreter, harbor_package, _version = _harbor_source(harbor)

    parent = campaign.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{campaign.name}-preparing-", dir=parent))
    try:
        schedule = runner.build_schedule(DATASET_ID)
        runner.persist_schedule(temporary, schedule)
        _copy_bundles(source_campaign, temporary)
        binding.model_identity_from_bundles(temporary)
        frozen_repo = temporary / "frozen" / "repo"
        adapter = _stage_repository(
            frozen_repo,
            harbor_package=harbor_package,
            harbor_interpreter=harbor_interpreter,
            image_reference=image_reference,
        )
        model = _materialize_model_input(
            source_campaign=source_campaign,
            hf_cache=hf_cache,
            destination_hub=temporary / "frozen" / "model-cache" / "hub",
        )
        task_runtime = binding.task_runtime_references(frozen_repo, DATASET_ID)
        frozen_manifest = {
            "schema_version": binding.FROZEN_INPUTS_SCHEMA,
            "source_campaign": source_campaign.name,
            "dataset_id": DATASET_ID,
            "mode": "consult-only",
            "frozen_repo": {
                "path": "frozen/repo",
                **binding.tree_identity(frozen_repo),
            },
            "offline_model": model,
            "task_runtime": task_runtime,
            "harbor_adapter": adapter,
            "pi_distribution": {
                "name": binding.PI_PACKAGE,
                "version": binding.PI_VERSION,
                "npm_integrity": binding.PI_NPM_INTEGRITY,
                "node_version": binding.NODE_VERSION,
            },
        }
        binding.write_canonical_exclusive(temporary / "frozen-inputs.json", frozen_manifest)

        staged_runner = frozen_repo / "evaluations/semantic-okf-datasets/run_consult_campaign.py"
        staged_harbor = frozen_repo / "vendor/harbor-cli"
        staged_hf = temporary / "frozen/model-cache/hub"
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                str(staged_runner),
                "--campaign",
                str(temporary),
                "--hf-cache",
                str(staged_hf),
                "--harbor",
                str(staged_harbor),
                "--docker",
                docker,
                "--max-concurrency",
                "1",
                "--dry-run",
            ],
            cwd=frozen_repo,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise FreezeError(
                "frozen runner dry-run failed before publication: "
                + (completed.stderr.strip() or completed.stdout.strip())
            )
        bindings = data.load_json(temporary / "input-bindings.json")
        if bindings.get("schema_version") != runner.INPUT_BINDING_SCHEMA_V2:
            raise FreezeError("frozen runner did not create an input-binding v2 manifest")
        result = {
            "campaign": campaign.name,
            "frozen_inputs_sha256": data.sha256_file(temporary / "frozen-inputs.json"),
            "input_bindings_sha256": data.sha256_file(temporary / "input-bindings.json"),
            "runtime_image_id": image_id,
            "runtime_image_reference": image_reference,
            "schedule_sha256": data.sha256_file(temporary / "schedule.json"),
            "status": "prepared",
        }
        _publish_prepared_campaign(temporary, campaign, source_campaign)
        return result
    except Exception:
        if temporary.exists() and temporary.parent == parent:
            shutil.rmtree(temporary)
        raise


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse one atomic campaign migration."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--source-campaign", type=Path, required=True)
    parser.add_argument("--hf-cache", type=Path, required=True)
    parser.add_argument("--harbor", type=Path, required=True)
    parser.add_argument("--docker", default="docker")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Prepare and publish one validated frozen campaign."""

    args = parse_args(argv)
    try:
        result = prepare_campaign(
            args.campaign,
            source_campaign=args.source_campaign,
            hf_cache=args.hf_cache,
            harbor=args.harbor,
            docker=args.docker,
        )
    except (FreezeError, binding.BindingError, runner.CampaignRunError, OSError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
