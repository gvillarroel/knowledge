#!/usr/bin/env python3
"""Build the common Harbor runtime and record its immutable local identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TAG = "semantic-okf-harbor-runtime:1.0"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> str:
    """Run one Docker command and return stripped standard output."""

    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def main() -> int:
    """Build the image and write an ignored, reproducible build receipt."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--no-build", action="store_true", help="Inspect an existing tag only.")
    args = parser.parse_args()
    if not args.no_build:
        subprocess.run(
            [args.docker, "build", "--pull=false", "--tag", args.tag, str(HERE)],
            check=True,
        )
    image_id = run([args.docker, "image", "inspect", "--format", "{{.Id}}", args.tag])
    repo_digests_raw = run(
        [args.docker, "image", "inspect", "--format", "{{json .RepoDigests}}", args.tag]
    )
    receipt = {
        "schema_version": "semantic-okf-harbor-runtime-build/1.0",
        "image_tag": args.tag,
        "image_id": image_id,
        "repo_digests": json.loads(repo_digests_raw or "[]"),
        "dockerfile_sha256": sha256_file(HERE / "Dockerfile"),
        "requirements_sha256": sha256_file(HERE / "requirements.txt"),
        "model_weights_in_image": False,
    }
    output = HERE / "build" / "runtime-build.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
