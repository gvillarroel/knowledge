from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


REPOSITORY = Path(__file__).resolve().parents[1]
EVALUATION = REPOSITORY / "evaluations" / "semantic-okf-endocrine-hygiene"
VALIDATOR = EVALUATION / "scripts" / "validate_ground_truth.py"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("endocrine_hygiene_claim_contract", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifacts(module: ModuleType) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, tuple[str, str]]]:
    requirements = module.load_json(EVALUATION / "benchmark" / "hard-claim-requirements.json")
    ground_truth = module.load_jsonl(EVALUATION / "benchmark" / "hard-ground-truth.jsonl")
    seed = json.loads(
        (EVALUATION / "corpus" / "claims-seed.json").read_text(encoding="utf-8")
    )
    corpus_claims = {
        claim["id"]: (claim["paper_id"], claim["passage_sha256"])
        for claim in seed["claims"]
    }
    return requirements, ground_truth, corpus_claims


def test_exact_claim_contract_covers_every_hard_atom_negative_and_evidence_binding() -> None:
    module = _load_validator()
    requirements, ground_truth, corpus_claims = _artifacts(module)

    counts = module.validate_hard_claim_requirements(
        requirements,
        ground_truth,
        corpus_claims,
    )

    assert counts == {
        "hard_claim_requirement_records": 5,
        "hard_answer_claims": 27,
        "hard_important_negatives": 15,
        "hard_required_claim_bindings": 128,
        "distinct_required_claims": 37,
        "hard_evidence_claim_projections": 60,
    }


def test_claim_contract_rejects_unknown_members_and_nonunique_claim_ids() -> None:
    module = _load_validator()
    requirements, ground_truth, corpus_claims = _artifacts(module)
    unknown_member = copy.deepcopy(requirements)
    unknown_member["derived"] = True

    with pytest.raises(module.ValidationError, match="closed schema"):
        module.validate_hard_claim_requirements(unknown_member, ground_truth, corpus_claims)

    duplicate_claim_id = copy.deepcopy(requirements)
    claim_ids = duplicate_claim_id["questions"][0]["answer_claims"][0]["required_claim_ids"]
    claim_ids[:] = [claim_ids[0], claim_ids[0]]
    with pytest.raises(module.ValidationError, match="sorted and duplicate-free"):
        module.validate_hard_claim_requirements(duplicate_claim_id, ground_truth, corpus_claims)


def test_claim_contract_rejects_missing_and_unreferenced_atom_requirements() -> None:
    module = _load_validator()
    requirements, ground_truth, corpus_claims = _artifacts(module)
    missing = copy.deepcopy(requirements)
    missing["questions"][0]["answer_claims"].pop()

    with pytest.raises(module.ValidationError, match="must match ground truth exactly"):
        module.validate_hard_claim_requirements(missing, ground_truth, corpus_claims)

    unreferenced = copy.deepcopy(requirements)
    unreferenced["questions"][0]["important_negatives"].append(
        {"id": "q026-n99", "required_claim_ids": ["claim-pmc8812815-001"]}
    )
    with pytest.raises(module.ValidationError, match="must match ground truth exactly"):
        module.validate_hard_claim_requirements(unreferenced, ground_truth, corpus_claims)


def test_claim_contract_rejects_missing_or_wrongly_bound_corpus_claims() -> None:
    module = _load_validator()
    requirements, ground_truth, corpus_claims = _artifacts(module)
    claim_id = requirements["questions"][0]["answer_claims"][0]["required_claim_ids"][0]
    missing = dict(corpus_claims)
    missing.pop(claim_id)

    with pytest.raises(module.ValidationError, match="requires unknown corpus claim"):
        module.validate_hard_claim_requirements(requirements, ground_truth, missing)

    wrong_signature = dict(corpus_claims)
    wrong_signature[claim_id] = ("PMC11764522", "0" * 64)
    with pytest.raises(module.ValidationError, match="is not bound to any of its evidence IDs"):
        module.validate_hard_claim_requirements(requirements, ground_truth, wrong_signature)


def test_every_hard_evidence_binding_requires_a_reviewed_claim_projection() -> None:
    module = _load_validator()
    requirements, ground_truth, corpus_claims = _artifacts(module)
    without_projection = dict(corpus_claims)
    without_projection.pop("claim-pmc6504186-007")

    with pytest.raises(module.ValidationError, match="q027-e2 has no reviewed corpus-claim projection"):
        module.validate_hard_claim_requirements(requirements, ground_truth, without_projection)


def test_benchmark_manifest_binds_the_exact_claim_contract_hash_and_counts() -> None:
    module = _load_validator()
    requirements, ground_truth, corpus_claims = _artifacts(module)
    counts = module.validate_hard_claim_requirements(requirements, ground_truth, corpus_claims)
    questions = module.load_jsonl(EVALUATION / "benchmark" / "retrieval-questions.jsonl")
    hard_questions = module.load_jsonl(EVALUATION / "benchmark" / "hard-questions.jsonl")
    manifest = module.load_json(EVALUATION / "benchmark" / "benchmark-manifest.json")

    module.validate_benchmark_manifest(
        manifest,
        questions,
        hard_questions,
        ground_truth,
        requirements,
        counts,
    )

    stale_hash = copy.deepcopy(manifest)
    stale_hash["files"]["hard-claim-requirements.json"]["sha256"] = "0" * 64
    with pytest.raises(module.ValidationError, match="hash for hard-claim-requirements.json is stale"):
        module.validate_benchmark_manifest(
            stale_hash,
            questions,
            hard_questions,
            ground_truth,
            requirements,
            counts,
        )

    stale_count = copy.deepcopy(manifest)
    stale_count["counts"]["hard_required_claim_bindings"] -= 1
    with pytest.raises(module.ValidationError, match="benchmark manifest counts are stale"):
        module.validate_benchmark_manifest(
            stale_count,
            questions,
            hard_questions,
            ground_truth,
            requirements,
            counts,
        )
