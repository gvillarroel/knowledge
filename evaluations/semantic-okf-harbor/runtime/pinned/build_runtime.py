#!/usr/bin/env python3
"""Build and attest the dependency-pinned Semantic OKF Harbor runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RUNTIME_ROOT = HERE.parent
DEFAULT_TAG = "semantic-okf-harbor-runtime:2.0"
BASE_IMAGE_REFERENCE = "python:3.12.13-slim-bookworm"
BASE_IMAGE_DIGEST = (
    "sha256:d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b"
)
BASE_IMAGE = f"{BASE_IMAGE_REFERENCE}@{BASE_IMAGE_DIGEST}"
PYTHON_VERSION = "3.12.13"
NODE_VERSION = "22.23.1"
NODE_ARCHIVE_URL = (
    "https://nodejs.org/dist/v22.23.1/node-v22.23.1-linux-x64.tar.xz"
)
NODE_ARCHIVE_SHA256 = (
    "9749e988f437343b7fa832c69ded82a312e41a03116d766797ac14f6f9eee578"
)
NPM_VERSION = "10.9.8"
PI_PACKAGE = "@mariozechner/pi-coding-agent"
PI_VERSION = "0.73.1"
PI_INTEGRITY = (
    "sha512-gXQh3SaZmWTfVMc4Ao5+LGbVeKvzyO7tolok0nLsZgq9nGjZx/EEU3NM8C+qUnB4"
    "Nvs2rswG5qOVgLzQkq0fHQ=="
)
SCHEMA_VERSION = "semantic-okf-harbor-pinned-runtime-build/2.0"

INPUT_PATHS = {
    "dockerfile": ("pinned/Dockerfile", HERE / "Dockerfile"),
    "requirements": ("requirements.txt", RUNTIME_ROOT / "requirements.txt"),
    "package_json": ("pinned/package.json", HERE / "package.json"),
    "package_lock": ("pinned/package-lock.json", HERE / "package-lock.json"),
    "receipt_schema": (
        "pinned/runtime-build.schema.json",
        HERE / "runtime-build.schema.json",
    ),
}


class InputError(ValueError):
    """Raised when a checked-in runtime input violates its pinning contract."""


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of one input file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> str:
    """Run one command and return its stripped successful output stream."""

    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout.strip() or completed.stderr.strip()


def locked_pi_metadata() -> dict[str, Any]:
    """Validate the npm lock graph and return the pinned Pi package metadata."""

    package_json = json.loads((HERE / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((HERE / "package-lock.json").read_text(encoding="utf-8"))
    expected_dependency = {PI_PACKAGE: PI_VERSION}
    if package_json.get("dependencies") != expected_dependency:
        raise InputError("package.json must declare only the exact Pi dependency")
    if lock.get("lockfileVersion") != 3:
        raise InputError("package-lock.json must use lockfileVersion 3")
    packages = lock.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise InputError("package-lock.json has no package graph")
    root = packages.get("")
    if not isinstance(root, dict) or root.get("dependencies") != expected_dependency:
        raise InputError("package-lock.json root dependency does not match package.json")
    for path, package in packages.items():
        if not path:
            continue
        if not isinstance(package, dict) or not all(
            isinstance(package.get(field), str) and package[field]
            for field in ("version", "resolved", "integrity")
        ):
            raise InputError(f"lock entry {path!r} is not an exact registry artifact")
        if not package["resolved"].startswith("https://registry.npmjs.org/"):
            raise InputError(f"lock entry {path!r} is not from the npm registry")
    pi = packages.get(f"node_modules/{PI_PACKAGE}")
    if not isinstance(pi, dict):
        raise InputError("package-lock.json does not contain the Pi package")
    if pi.get("version") != PI_VERSION:
        raise InputError("Pi version in package-lock.json is stale")
    if pi.get("integrity") != PI_INTEGRITY:
        raise InputError("Pi integrity in package-lock.json is stale")
    return {
        "package": PI_PACKAGE,
        "version": PI_VERSION,
        "integrity": PI_INTEGRITY,
        "locked_package_count": len(packages) - 1,
    }


def validate_inputs() -> dict[str, Any]:
    """Validate all source pins and return their portable digest binding."""

    missing = [str(path) for _, path in INPUT_PATHS.values() if not path.is_file()]
    if missing:
        raise InputError(f"missing runtime input files: {', '.join(missing)}")
    pi = locked_pi_metadata()
    files = {
        name: {"path": portable_path, "sha256": sha256_file(path)}
        for name, (portable_path, path) in INPUT_PATHS.items()
    }
    return {"input_files": files, "pi_coding_agent": pi}


def inspect_in_image(docker: str, tag: str, executable: str, *arguments: str) -> str:
    """Inspect one installed component without granting the container network access."""

    return run(
        [
            docker,
            "run",
            "--rm",
            "--network",
            "none",
            "--entrypoint",
            executable,
            tag,
            *arguments,
        ]
    )


def make_receipt(
    *,
    tag: str,
    image_id: str,
    repo_digests: list[str],
    observed_python: str,
    observed_node: str,
    observed_npm: str,
    observed_pi: str,
    observed_model_weights: bool,
    binding: dict[str, Any],
) -> dict[str, Any]:
    """Create a runtime build receipt after checking every observed version."""

    expected = {
        "python": (PYTHON_VERSION, observed_python),
        "node": (NODE_VERSION, observed_node.removeprefix("v")),
        "npm": (NPM_VERSION, observed_npm),
        "pi": (PI_VERSION, observed_pi),
    }
    mismatches = [
        f"{name}: expected {wanted}, observed {actual}"
        for name, (wanted, actual) in expected.items()
        if actual != wanted
    ]
    if mismatches:
        raise InputError("runtime version mismatch: " + "; ".join(mismatches))
    if observed_model_weights:
        raise InputError("runtime image unexpectedly contains Hugging Face model files")
    if not image_id.startswith("sha256:"):
        raise InputError("Docker image identity must be a content-addressed SHA-256 ID")
    return {
        "schema_version": SCHEMA_VERSION,
        "image_tag": tag,
        "image_id": image_id,
        "repo_digests": sorted(repo_digests),
        "base_image": {
            "reference": BASE_IMAGE_REFERENCE,
            "digest": BASE_IMAGE_DIGEST,
        },
        "input_files": binding["input_files"],
        "python": {"version": PYTHON_VERSION, "observed_version": observed_python},
        "node": {
            "version": NODE_VERSION,
            "observed_version": observed_node.removeprefix("v"),
            "archive_url": NODE_ARCHIVE_URL,
            "archive_sha256": NODE_ARCHIVE_SHA256,
            "npm_version": NPM_VERSION,
            "observed_npm_version": observed_npm,
        },
        "pi_coding_agent": {
            **binding["pi_coding_agent"],
            "observed_version": observed_pi,
        },
        "model_weights_in_image": False,
    }


def inspect_receipt(docker: str, tag: str, binding: dict[str, Any]) -> dict[str, Any]:
    """Inspect the built image and return its complete receipt."""

    image_id = run([docker, "image", "inspect", "--format", "{{.Id}}", tag])
    raw_repo_digests = run(
        [docker, "image", "inspect", "--format", "{{json .RepoDigests}}", tag]
    )
    repo_digests = json.loads(raw_repo_digests or "[]") or []
    observed_python = inspect_in_image(
        docker,
        tag,
        "python",
        "-c",
        "import platform; print(platform.python_version())",
    )
    observed_node = inspect_in_image(docker, tag, "node", "--version")
    observed_npm = inspect_in_image(docker, tag, "npm", "--version")
    observed_pi = inspect_in_image(docker, tag, "pi", "--version")
    model_probe = inspect_in_image(
        docker,
        tag,
        "python",
        "-c",
        "from pathlib import Path; p=Path('/models/huggingface'); "
        "print('true' if p.exists() and any(x.is_file() for x in p.rglob('*')) else 'false')",
    )
    if model_probe not in {"true", "false"}:
        raise InputError("runtime model-weight probe returned an invalid result")
    return make_receipt(
        tag=tag,
        image_id=image_id,
        repo_digests=repo_digests,
        observed_python=observed_python,
        observed_node=observed_node,
        observed_npm=observed_npm,
        observed_pi=observed_pi,
        observed_model_weights=model_probe == "true",
        binding=binding,
    )


def main() -> int:
    """Build or inspect the image and write its ignored content-addressed receipt."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--no-build", action="store_true", help="Inspect an existing tag only.")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate checked-in pins without invoking Docker.",
    )
    parser.add_argument("--output", type=Path, default=HERE / "build/runtime-build.json")
    args = parser.parse_args()

    binding = validate_inputs()
    if args.validate_only:
        print(json.dumps(binding, sort_keys=True))
        return 0
    if not args.no_build:
        subprocess.run(
            [
                args.docker,
                "build",
                "--pull=false",
                "--platform",
                "linux/amd64",
                "--file",
                str(HERE / "Dockerfile"),
                "--tag",
                args.tag,
                str(RUNTIME_ROOT),
            ],
            check=True,
        )
    receipt = inspect_receipt(args.docker, args.tag, binding)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
