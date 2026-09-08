"""Materialize private generator-construction cases as isolated native Harbor tasks."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def hashes(root):
    paths = sorted(root.rglob("*"))
    if any(p.is_symlink() or getattr(p, "is_junction", lambda: False)() for p in paths):
        raise ValueError("Case trees cannot contain links")
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}


def linux_path(path):
    value = path.resolve().as_posix()
    return "/mnt/" + value[0].lower() + "/" + value.split(":/", 1)[1] if ":/" in value else value


def docker(arguments):
    prefix = ["wsl", "-d", "Ubuntu", "--exec"] if __import__("os").name == "nt" else []
    result = subprocess.run([*prefix, "docker", *arguments], capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def render_case(case, destination, image):
    base_id = docker(["image", "inspect", image, "--format", "{{.Id}}"])
    request = json.loads((case / "request.json").read_text(encoding="utf-8"))
    inputs = case / "input"
    if not inputs.is_dir() or not (case / "tests/test.sh").is_file():
        raise ValueError("Each case needs input/, request.json, and tests/test.sh")
    environment = destination / "environment"
    environment.mkdir(parents=True)
    shutil.copytree(inputs, environment / "input")
    shutil.copytree(case / "tests", destination / "tests")
    (destination / "instruction.md").write_text(json.dumps(request, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (environment / "Dockerfile").write_text(f"FROM {image}\nCOPY input/ /dataset/\n", encoding="utf-8", newline="\n")
    tag = "knowledge-generator-case:" + hashlib.sha256(json.dumps({"base": base_id, "inputs": hashes(inputs)}, sort_keys=True).encode()).hexdigest()[:24]
    docker(["build", "--pull=false", "--provenance=false", "--network=none", "-t", tag, linux_path(environment)])
    if docker(["image", "inspect", image, "--format", "{{.Id}}"]) != base_id:
        raise ValueError("Base runtime changed during task construction")
    built = docker(["image", "inspect", tag, "--format", "{{.Id}}"])
    compose = "services:\n  main:\n    network_mode: none\n"
    (environment / "docker-compose.yaml").write_text(compose + "    volumes:\n      - type: bind\n        source: ./input\n        target: /dataset\n        read_only: true\n", encoding="utf-8", newline="\n")
    (destination / "tests/docker-compose.yaml").write_text(compose + "    volumes:\n      - type: bind\n        source: .\n        target: /tests\n        read_only: true\n", encoding="utf-8", newline="\n")
    (destination / "task.toml").write_text(f'''schema_version = "1.3"
artifacts = [
  {{ source = "/logs/artifacts", destination = "published-artifacts" }},
  {{ source = "/workspace", destination = "workspace" }}
]
[metadata]
capability = "knowledge-skill-construction"
resource_class = "cpu-two-threads"
[agent]
timeout_sec = 1000.0
network_mode = "public"
[verifier]
timeout_sec = 180.0
environment_mode = "separate"
network_mode = "public"
[verifier.environment]
docker_image = "{base_id}"
os = "linux"
network_mode = "public"
cpus = 2
memory_mb = 4096
[environment]
docker_image = "{built}"
os = "linux"
network_mode = "public"
cpus = 2
memory_mb = 8192
storage_mb = 8192
workdir = "/workspace"
''', encoding="utf-8", newline="\n")


def materialize(cases, output, image, check=False):
    if output.exists() and not check:
        raise FileExistsError(output)
    if check and not output.is_dir():
        raise ValueError("Missing task tree for --check")
    inputs = sorted(p.parent for p in cases.glob("*/request.json"))
    if not inputs:
        raise ValueError("No construction cases")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".generator-tasks-", dir=output.parent) as temporary:
        pending = Path(temporary) / "tasks"
        for case in inputs:
            identity = "gc-" + hashlib.sha256(json.dumps(hashes(case), sort_keys=True).encode()).hexdigest()[:20]
            render_case(case, pending / identity, image)
        if check:
            if hashes(pending) != hashes(output):
                raise ValueError("Deterministic task replay differs")
        else:
            pending.rename(output)
    return {"task_count": len(inputs), "tree_sha256": hashlib.sha256(json.dumps(hashes(output), sort_keys=True).encode()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(materialize(args.cases, args.output, args.image, args.check), sort_keys=True))
