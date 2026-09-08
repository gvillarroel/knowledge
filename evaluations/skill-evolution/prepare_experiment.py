"""Materialize evaluator-free inputs, clean packages, and a pinned local runtime.

This preparation command does not select candidates or run a validation gate.
Dataset payloads and model weights are written only below the ignored workspace.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORK = REPO / "tmp/e5"
TASKS = WORK / "tasks"
PROTOCOL = WORK / "protocol"
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(path):
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob("*")) if p.is_file()}


def clean_copy(source, target):
    if source.is_symlink():
        raise ValueError("Linked source package")
    for p in source.rglob("*"):
        if p.is_symlink():
            raise ValueError("Linked source package content")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".pytest_cache"))


def wsl_path(path):
    path = path.resolve()
    if os.name != "nt":
        return str(path)
    return "/mnt/" + path.drive[0].lower() + "/" + path.as_posix().split(":/", 1)[1]


def linux(args, *, log=None):
    command = ["wsl", "-d", "Ubuntu", "--exec", *args] if os.name == "nt" else args
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    text = result.stdout.decode("utf-8", errors="replace")
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(text, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Command failed: {args[0]}; log={log}")
    return text.strip()


def prepare_runtime():
    index = 1
    while (WORK / f"runtime-context-{index:03d}").exists():
        index += 1
    context = WORK / f"runtime-context-{index:03d}"
    context.mkdir(parents=True, exist_ok=False)
    frozen = context / "frozen"
    frozen.mkdir()
    for name in ("bridge.py", "verifier.py"):
        shutil.copyfile(HERE / name, frozen / name)
    helper = REPO / "evaluations/private-book-strategy-comparison/scripts"
    for name in ("evaluate_all_routes.py", "prepare_strategy_bundles.py"):
        shutil.copyfile(helper / name, frozen / name)
    shutil.copyfile(REPO / "evaluations/semantic-okf-embeddings/scripts/compare_retrieval.py", frozen / "legacy_comparator.py")
    base = linux(["docker", "image", "inspect", "semantic-okf-harbor-runtime:2.0", "--format", "{{.Id}}"])
    (context / "Dockerfile").write_text(
        f"FROM semantic-okf-harbor-runtime:2.0\nLABEL org.knowledge.base-image={base}\nCOPY frozen/ /opt/knowledge/evolution/runtime/\nENV OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1\nWORKDIR /workspace\n", encoding="utf-8")
    tag = f"knowledge-skill-evolution-runtime:{WORK.name}-{index:03d}"
    linux(["docker", "build", "--pull=false", "--network=none", "-t", tag, wsl_path(context)], log=WORK / f"logs/runtime-build-{index:03d}.log")
    if linux(["docker", "image", "inspect", "semantic-okf-harbor-runtime:2.0", "--format", "{{.Id}}"] ) != base:
        raise ValueError("Base runtime changed during build")
    image = linux(["docker", "image", "inspect", tag, "--format", "{{.Id}}"])
    write_json(WORK / "runtime.json", {"base_image": base, "image": image, "tag": tag, "frozen_files": tree(frozen), "harbor": "0.18.0", "llm_calls": 0})
    print(json.dumps({"stage": "runtime", "status": "pass", "image": image}), flush=True)


def prepare_model(cache):
    name = "models--" + MODEL_ID.replace("/", "--")
    source = cache / name / "snapshots" / MODEL_REVISION
    target = WORK / "models/hub" / name / "snapshots" / MODEL_REVISION
    target.mkdir(parents=True, exist_ok=False)
    for p in sorted(source.rglob("*")):
        relative = p.relative_to(source)
        if any(part in {"onnx", "openvino", ".cache"} for part in relative.parts):
            continue
        if not p.is_file() or p.suffix in {".h5", ".ot", ".bin"}:
            continue
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(p.read_bytes())
    required = ["config.json", "modules.json", "model.safetensors", "tokenizer.json", "1_Pooling/config.json"]
    if not all((target / name).is_file() for name in required):
        raise ValueError("Incomplete local model snapshot")
    write_json(WORK / "model-inventory.json", {"model_id": MODEL_ID, "revision": MODEL_REVISION, "files": tree(target), "bytes": sum(p.stat().st_size for p in target.rglob("*") if p.is_file()), "source": f"https://huggingface.co/{MODEL_ID}/tree/{MODEL_REVISION}", "use": "offline symmetric dense retrieval; no instruction-model calls"})
    print(json.dumps({"stage": "model", "status": "pass", "model_id": MODEL_ID, "revision": MODEL_REVISION}), flush=True)


def freeze_baseline():
    target = WORK / "baseline/build-semantic-okf-knowledge-skill"
    clean_copy(REPO / "skills/build-semantic-okf-knowledge-skill", target)
    write_json(WORK / "baseline-binding.json", {"source": "skills/build-semantic-okf-knowledge-skill", "files": tree(target)})
    print(json.dumps({"stage": "baseline", "status": "frozen", "files": len(tree(target))}), flush=True)


def copy_manifest_inputs(manifest_path, target):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target.mkdir(parents=True, exist_ok=False)
    source_root = manifest_path.parent.resolve()
    for source in manifest["sources"]:
        relative = Path(source["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe source manifest path")
        originals = sorted(source_root.glob(relative.as_posix()))
        if not originals:
            raise ValueError("Manifest source selection is empty")
        for original in originals:
            if original.is_symlink() or not original.resolve().is_relative_to(source_root) or not original.is_file():
                raise ValueError("Unsafe source manifest member")
            dest = target / original.relative_to(source_root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, dest)
    shutil.copyfile(manifest_path, target / "manifest.json")


def prepare_enterprise():
    original = REPO / "evaluations/enterprise-rag-bench/processed/enterprise-rag-bench-40-v1"
    target = WORK / "development-inputs/enterprise"
    copy_manifest_inputs(original / "input/manifest.json", target / "input")
    rows = json.loads((original / "evaluator/questions.json").read_text(encoding="utf-8"))
    write_json(target / "queries.json", [{"id": row["id"], "question": row["question"]} for row in rows])
    write_json(WORK / "curator/development/enterprise-qrels.json", rows)
    write_json(WORK / "development-inputs/enterprise-binding.json", {"files": tree(target), "question_count": len(rows), "exposure": "previously published full-workload diagnostic; explicitly development-only in this study"})
    print(json.dumps({"stage": "enterprise-development", "status": "prepared", "questions": len(rows)}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["runtime", "model", "baseline", "enterprise"])
    parser.add_argument("--model-cache", type=Path)
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    if args.stage == "runtime":
        prepare_runtime()
    elif args.stage == "model":
        if args.model_cache is None:
            parser.error("--model-cache is required")
        prepare_model(args.model_cache.resolve())
    elif args.stage == "baseline":
        freeze_baseline()
    else:
        prepare_enterprise()


if __name__ == "__main__":
    main()
