from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-adaptive-evolution"
MANIFEST = EVALUATION_ROOT / "frozen-benchmark.json"
VALIDATOR = EVALUATION_ROOT / "scripts" / "validate_frozen_benchmark.py"
MANIFEST_SHA256 = "2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414"
RETRIEVAL_SHA256 = "21ca640514c7378c06f3e2a1a02210d079c5c3048fd2d07b14ade15f1c9788ec"
HARD_QUESTIONS_SHA256 = "59b41fe5f81141ee2fc9ab04e61751c474d97e17eb8eead7aaf432ecd47259ca"
GROUND_TRUTH_SHA256 = "c4e5aa00a85efba41cd18c4de7fda5e2b7f3ce61de9916f55268cfc5afecd388"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _module() -> ModuleType:
    name = "test_semantic_okf_adaptive_frozen_validator"
    spec = importlib.util.spec_from_file_location(name, VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _copy_fixture(tmp_path: Path) -> tuple[Path, Path]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = [entry["path"] for entry in manifest["cohorts"].values()]
    for group in ("support_files", "evaluator_files", "incumbent_reports"):
        paths.extend(entry["path"] for entry in manifest[group])
    destination_manifest = tmp_path / MANIFEST.relative_to(REPO_ROOT)
    destination_manifest.parent.mkdir(parents=True)
    shutil.copy2(MANIFEST, destination_manifest)
    for relative in sorted(set(paths)):
        source = REPO_ROOT / relative
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return tmp_path, destination_manifest


def test_frozen_benchmark_has_exact_question_and_ground_truth_hashes() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert _sha256(MANIFEST) == MANIFEST_SHA256
    assert manifest["status"] == "frozen"
    assert manifest["benchmark_id"] == "semantic-okf-adaptive-frozen-40-plus-hard10-v1"
    assert manifest["cohorts"]["retrieval_questions"]["sha256"] == RETRIEVAL_SHA256
    assert manifest["cohorts"]["hard_questions"]["sha256"] == HARD_QUESTIONS_SHA256
    assert manifest["cohorts"]["hard_ground_truth"]["sha256"] == GROUND_TRUTH_SHA256
    assert _sha256(REPO_ROOT / manifest["cohorts"]["retrieval_questions"]["path"]) == RETRIEVAL_SHA256
    assert _sha256(REPO_ROOT / manifest["cohorts"]["hard_questions"]["path"]) == HARD_QUESTIONS_SHA256
    assert _sha256(REPO_ROOT / manifest["cohorts"]["hard_ground_truth"]["path"]) == GROUND_TRUTH_SHA256


def test_frozen_benchmark_validator_checks_all_bound_files_and_alignment() -> None:
    result = _module().validate(REPO_ROOT, MANIFEST)

    assert result["status"] == "pass"
    assert result["retrieval_questions"] == 40
    assert result["hard_questions"] == 10
    assert result["bound_files"] == 17


@pytest.mark.parametrize(
    ("relative_path", "replacement"),
    [
        (
            "evaluations/semantic-okf-adaptive/retrieval-questions.jsonl",
            b"\n",
        ),
        (
            "evaluations/semantic-okf-adaptive/hard-ground-truth.jsonl",
            b" ",
        ),
    ],
)
def test_frozen_benchmark_rejects_question_or_ground_truth_drift(
    tmp_path: Path, relative_path: str, replacement: bytes
) -> None:
    root, manifest = _copy_fixture(tmp_path)
    target = root / relative_path
    target.write_bytes(target.read_bytes() + replacement)
    module = _module()

    with pytest.raises(module.FrozenBenchmarkError, match="changed"):
        module.validate(root, manifest)


def test_frozen_benchmark_rejects_a_manifest_that_relaxes_a_bound_hash(tmp_path: Path) -> None:
    root, manifest_path = _copy_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["cohorts"]["retrieval_questions"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    module = _module()

    with pytest.raises(module.FrozenBenchmarkError, match="frozen cohort changed"):
        module.validate(root, manifest_path)
