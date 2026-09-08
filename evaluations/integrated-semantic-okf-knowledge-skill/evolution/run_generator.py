"""Execute the declared generator and preserve artifacts, including rejected builds."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def execute(skill, request):
    expected = {"manifest", "guidance", "family", "name", "description", "output", "plan", "concept_layout"}
    if set(request) != expected:
        raise ValueError("Unexpected generator request schema")
    inputs = Path("/dataset")
    workspace = Path("/workspace")
    for key in ("manifest", "guidance", "plan"):
        if request[key] is not None and not Path(request[key]).resolve().is_relative_to(inputs):
            raise ValueError("Input path escaped the mounted source")
    output = Path(request["output"])
    if output == workspace or not output.resolve().is_relative_to(workspace) or output.exists():
        raise ValueError("Expected a new generated output below /workspace")
    before = inventory(inputs)
    command = [sys.executable, "-B", str(skill / "scripts/build_semantic_okf_knowledge_skill.py"),
               request["manifest"], str(output), "--family", request["family"], "--name", request["name"],
               "--description", request["description"], "--guidance", request["guidance"],
               "--concept-layout", request["concept_layout"], "--output-format", "json"]
    if request["plan"] is not None:
        command.extend(["--plan", request["plan"]])
    started = time.monotonic()
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=780)
    result = {"schema_version": "generator-cli-trial/1.0", "request": request,
              "return_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr,
              "seconds": time.monotonic() - started, "input_before": before,
              "input_after": inventory(inputs), "published": output.is_dir(),
              "output_files": inventory(output) if output.is_dir() else {}}
    Path("/workspace/result.json").write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    result = execute(args.skill, json.loads(args.request))
    print(json.dumps({"return_code": result["return_code"], "published": result["published"]}))
