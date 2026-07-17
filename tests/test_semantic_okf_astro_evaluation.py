from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION = REPO_ROOT / "evaluations" / "semantic-okf-astro"


def _module(name: str, relative: str):
    path = REPO_ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def prepare_module():
    return _module(
        "semantic_okf_astro_prepare_test",
        "evaluations/semantic-okf-astro/scripts/prepare_corpus.py",
    )


@pytest.fixture(scope="module")
def validator_module():
    return _module(
        "semantic_okf_astro_validator_test",
        "evaluations/semantic-okf-astro/scripts/validate_evaluation.py",
    )


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_frozen_evaluation_passes_independent_validator(validator_module) -> None:
    result = validator_module.validate()

    assert result == {
        "answer_claims": 50,
        "documents": 416,
        "evidence_bindings": 46,
        "hard_questions": 10,
        "questions": 40,
        "source_record_mappings": 416,
        "status": "pass",
    }


def test_routes_and_opaque_source_ids_are_deterministic(prepare_module) -> None:
    assert prepare_module.route_for(Path("index.mdx")) == "/en/"
    assert prepare_module.route_for(Path("guides/deploy/index.mdx")) == "/en/guides/deploy/"
    assert prepare_module.route_for(Path("guides/actions.mdx")) == "/en/guides/actions/"
    assert prepare_module.source_id_for("/en/guides/actions/") == "astro-doc-08a92557027a42f0"


def test_source_record_crosswalk_is_total_and_uses_builder_record_ids() -> None:
    inventory = json.loads((EVALUATION / "corpus/input-inventory.json").read_text(encoding="utf-8"))
    identity = json.loads((EVALUATION / "corpus/source-combination.json").read_text(encoding="utf-8"))

    assert len(inventory["documents"]) == len(identity["records"]) == 416
    assert len(identity["source_record_to_document_ids"]) == 416
    for row in inventory["documents"]:
        expected_record = row["path"].removeprefix("corpus/").removesuffix(".mdx")
        key = json.dumps([row["source_id"], expected_record], separators=(",", ":"))
        assert row["record_id"] == expected_record
        assert identity["source_record_to_document_ids"][key] == row["document_id"]


def test_benchmark_and_plans_are_reproducibly_derived_from_authored_inputs(prepare_module) -> None:
    for name, payload in prepare_module.build_benchmark_outputs().items():
        assert (EVALUATION / "benchmark" / name).read_bytes() == payload
    for name, payload in prepare_module.build_plan_outputs().items():
        assert (EVALUATION / "plans" / name).read_bytes() == payload


def test_question_partition_and_qrel_identity_parity() -> None:
    questions = _jsonl(EVALUATION / "benchmark/retrieval-questions.jsonl")
    identity = json.loads((EVALUATION / "corpus/source-combination.json").read_text(encoding="utf-8"))
    source_map = identity["source_ids_to_document_ids"]

    assert [row["id"] for row in questions] == [f"q{number:03d}" for number in range(1, 41)]
    assert [row["question_type"] for row in questions].count("direct") == 20
    assert [row["question_type"] for row in questions].count("cross-document") == 10
    assert [row["question_type"] for row in questions].count("hard") == 10
    for row in questions:
        mapped = sorted(source_map[source_id] for source_id in row["qrels"]["source_ids"])
        assert mapped == row["qrels"]["document_ids"]


def test_hard_evidence_intervals_and_hashes_are_exact() -> None:
    truths = _jsonl(EVALUATION / "benchmark/hard-ground-truth.jsonl")

    assert len(truths) == 10
    for truth in truths:
        assert len(truth["ground_truth"]["answer_claims"]) == 5
        assert len(truth["ground_truth"]["important_negatives"]) >= 2
        assert len({row["document_id"] for row in truth["authoritative_evidence"]}) >= 2
        evidence_ids = {row["id"] for row in truth["authoritative_evidence"]}
        for evidence in truth["authoritative_evidence"]:
            path = REPO_ROOT / evidence["path"]
            payload = path.read_bytes()
            text = payload.decode("utf-8-sig")
            selected = text[evidence["start_char"] : evidence["end_char"]]
            assert hashlib.sha256(payload).hexdigest() == evidence["file_sha256"]
            assert hashlib.sha256(selected.encode("utf-8")).hexdigest() == evidence["text_sha256"]
            assert selected.startswith("#")
            assert evidence["heading"] in selected.splitlines()[0]
        for claim in truth["ground_truth"]["answer_claims"]:
            assert set(claim["evidence_ids"]).issubset(evidence_ids)
        for negative in truth["ground_truth"]["important_negatives"]:
            assert set(negative["evidence_ids"]).issubset(evidence_ids)


def test_strict_json_and_heading_resolution_reject_ambiguous_inputs(
    validator_module,
    prepare_module,
) -> None:
    with pytest.raises(validator_module.EvaluationError, match="duplicate JSON key"):
        validator_module.strict_json('{"same":1,"same":2}', "duplicate fixture")
    with pytest.raises(prepare_module.PreparationError, match="cannot resolve heading"):
        prepare_module._heading_section(
            b"---\ntitle: Fixture\n---\n\n## Existing\nBody\n",
            {"heading": "Missing", "occurrence": 1},
            "missing fixture",
        )


@pytest.mark.parametrize(
    ("script_dir", "module_name", "function_name", "plan_name", "assertion"),
    [
        (
            "skills/build-semantic-okf-classical/scripts",
            "_classical_retrieval",
            "load_plan",
            "classical-plan.json",
            "len(plan.source_ids) == 416",
        ),
        (
            "skills/build-semantic-okf-adaptive/scripts",
            "_adaptive_retrieval",
            "load_plan",
            "adaptive-plan.json",
            "len(plan.source_ids) == 416",
        ),
        (
            "skills/build-semantic-okf-embeddings/scripts",
            "_embedding_retrieval",
            "load_plan",
            "embedding-plan.json",
            "len(plan.source_ids) == 416",
        ),
        (
            "skills/build-semantic-okf-entity-graph/scripts",
            "_entity_graph_model",
            "load_plan",
            "entity-graph-plan.json",
            "plan.schema_version == '2.0' and len(plan.source_ids) == 416",
        ),
        (
            "skills/build-semantic-okf-ensemble/scripts",
            "_ensemble_build",
            "load_plan",
            "ensemble-plan.json",
            "plan['schema_version'] == '2.0' and len(plan['adaptive']['selection']['source_ids']) == 416",
        ),
    ],
)
def test_each_retrieval_plan_passes_its_package_loader(
    script_dir: str,
    module_name: str,
    function_name: str,
    plan_name: str,
    assertion: str,
) -> None:
    code = (
        "import sys; from pathlib import Path; "
        f"sys.path.insert(0, {str(REPO_ROOT / script_dir)!r}); "
        f"from {module_name} import {function_name}; "
        f"plan = {function_name}(Path({str(EVALUATION / 'plans' / plan_name)!r})); "
        f"assert {assertion}"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
