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
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-ensemble"
REVIEWED_ROOT = EVALUATION_ROOT / "reviewed-benchmark"
AMENDMENTS = EVALUATION_ROOT / "reviewed-answer-benchmark-amendments.json"
GENERATOR = EVALUATION_ROOT / "scripts" / "generate_reviewed_answer_benchmark.py"
CLASSICAL_VALIDATOR = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-classical"
    / "scripts"
    / "validate_hard_ground_truth.py"
)
PARENT_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-adaptive"
PARENT_FROZEN = (
    REPO_ROOT / "evaluations" / "semantic-okf-adaptive-evolution" / "frozen-benchmark.json"
)


def _module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _generator() -> ModuleType:
    return _module("test_reviewed_answer_benchmark_generator", GENERATOR)


def _validator() -> ModuleType:
    return _module("test_reviewed_answer_benchmark_classical_validator", CLASSICAL_VALIDATOR)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _group(record: dict[str, object], kind: str, group_id: str) -> dict[str, object]:
    section = "answer_claims" if kind == "answer_claim" else "important_negatives"
    rows = record["ground_truth"][section]
    matches = [row for row in rows if row["id"] == group_id]
    assert len(matches) == 1
    return matches[0]


def test_amendments_are_closed_english_and_match_the_independent_allowlist() -> None:
    module = _generator()
    amendments = json.loads(AMENDMENTS.read_text(encoding="utf-8"))

    assert set(amendments) == {
        "schema_version",
        "amendment_id",
        "parent_benchmark_id",
        "language",
        "addition_policy",
        "additions",
        "rejected_close_alternatives",
    }
    module.validate_amendments(amendments)
    observed = tuple(
        (
            row["question_id"],
            row["group_kind"],
            row["group_id"],
            tuple(item["claim_id"] for item in row["append_claims"]),
        )
        for row in amendments["additions"]
    )
    assert observed == module.APPROVED_ADDITIONS
    assert len(observed) == 32
    assert sum(len(row[3]) for row in observed if row[1] == "answer_claim") == 22
    assert sum(len(row[3]) for row in observed if row[1] == "important_negative") == 19
    assert len(amendments["rejected_close_alternatives"]) == 38
    assert all(
        item["reason"].strip().endswith(".")
        for item in amendments["rejected_close_alternatives"]
    )


def test_reviewed_ground_truth_is_an_exact_append_only_option_amendment() -> None:
    module = _generator()
    parent_rows = _jsonl(PARENT_ROOT / "hard-ground-truth.jsonl")
    reviewed_rows = _jsonl(REVIEWED_ROOT / "hard-ground-truth.jsonl")
    parent = {row["id"]: row for row in parent_rows}
    reviewed = {row["id"]: row for row in reviewed_rows}

    assert list(reviewed) == list(parent)
    touched: set[tuple[str, str, str]] = set()
    first_new_ids: dict[str, list[str]] = {question_id: [] for question_id in reviewed}
    for question_id, kind, group_id, additions in module.APPROVED_ADDITIONS:
        parent_group = _group(parent[question_id], kind, group_id)
        reviewed_group = _group(reviewed[question_id], kind, group_id)
        assert reviewed_group["statement"] == parent_group["statement"]
        assert reviewed_group["evidence_claim_ids"] == [
            *parent_group["evidence_claim_ids"],
            *additions,
        ]
        touched.add((question_id, kind, group_id))
        for claim_id in additions:
            if claim_id not in first_new_ids[question_id]:
                first_new_ids[question_id].append(claim_id)

    for question_id, parent_row in parent.items():
        reviewed_row = reviewed[question_id]
        assert reviewed_row["schema_version"] == parent_row["schema_version"]
        assert reviewed_row["question"] == parent_row["question"]
        assert reviewed_row["corpus_inventory"] == parent_row["corpus_inventory"]
        for key in (
            "required_paper_ids",
            "required_source_ids",
            "derivation",
            "acceptable_variants",
        ):
            assert reviewed_row["ground_truth"][key] == parent_row["ground_truth"][key]
        for kind, section in (
            ("answer_claim", "answer_claims"),
            ("important_negative", "important_negatives"),
        ):
            for parent_group in parent_row["ground_truth"][section]:
                if (question_id, kind, parent_group["id"]) not in touched:
                    assert _group(reviewed_row, kind, parent_group["id"]) == parent_group
        parent_evidence = parent_row["authoritative_evidence"]
        reviewed_evidence = reviewed_row["authoritative_evidence"]
        assert reviewed_evidence[: len(parent_evidence)] == parent_evidence
        assert [item["claim_id"] for item in reviewed_evidence[len(parent_evidence) :]] == first_new_ids[
            question_id
        ]


def test_every_added_evidence_object_rederives_from_authoritative_sources() -> None:
    module = _generator()
    inventory, paper_roles = module.validate_inventory(REPO_ROOT)
    claims = module.build_claim_index(REPO_ROOT, inventory, paper_roles)
    parent = {row["id"]: row for row in _jsonl(PARENT_ROOT / "hard-ground-truth.jsonl")}
    reviewed = {row["id"]: row for row in _jsonl(REVIEWED_ROOT / "hard-ground-truth.jsonl")}

    checked = 0
    for question_id, reviewed_row in reviewed.items():
        parent_ids = {item["claim_id"] for item in parent[question_id]["authoritative_evidence"]}
        for item in reviewed_row["authoritative_evidence"]:
            if item["claim_id"] in parent_ids:
                continue
            expected = module.derive_authoritative_evidence(REPO_ROOT, item["claim_id"], claims)
            assert item == expected
            assert item["claim_source"]["char_end"] > item["claim_source"]["char_start"]
            assert all(page["char_end"] > page["char_start"] for page in item["paper_evidence"])
            checked += 1
    assert checked == 27


def test_inventory_hash_validation_rejects_authoritative_source_drift(tmp_path: Path) -> None:
    module = _generator()
    copied_root = tmp_path / "repo"
    inventory_source = REPO_ROOT / module.INVENTORY_PATH
    inventory_target = copied_root / module.INVENTORY_PATH
    inventory_target.parent.mkdir(parents=True)
    shutil.copy2(inventory_source, inventory_target)
    inventory = json.loads(inventory_source.read_text(encoding="utf-8"))
    for entry in inventory["files"]:
        source = REPO_ROOT / module.CORPUS_ROOT / entry["path"]
        target = copied_root / module.CORPUS_ROOT / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    module.validate_inventory(copied_root)
    changed = copied_root / module.CORPUS_ROOT / inventory["files"][0]["path"]
    changed.write_bytes(changed.read_bytes() + b"\n")
    with pytest.raises(module.GenerationError, match="pinned corpus hash mismatch"):
        module.validate_inventory(copied_root)


def test_questions_qrels_and_classical_validator_remain_compatible() -> None:
    validator = _validator()
    assert (REVIEWED_ROOT / "hard-questions.jsonl").read_bytes() == (
        PARENT_ROOT / "hard-questions.jsonl"
    ).read_bytes()
    assert (REVIEWED_ROOT / "retrieval-questions.jsonl").read_bytes() == (
        PARENT_ROOT / "retrieval-questions.jsonl"
    ).read_bytes()

    validator.validate_all(REPO_ROOT, REVIEWED_ROOT)
    independently_derived = [
        validator.validate_ground_truth_record(REPO_ROOT, row)
        for row in _jsonl(REVIEWED_ROOT / "hard-ground-truth.jsonl")
    ]
    assert independently_derived == _jsonl(REVIEWED_ROOT / "hard-questions.jsonl")


def test_frozen_manifest_has_the_exact_closed_schema_and_hash_bindings() -> None:
    manifest = json.loads(
        (REVIEWED_ROOT / "frozen-answer-benchmark.json").read_text(encoding="utf-8")
    )
    assert set(manifest) == {
        "schema_version",
        "benchmark_id",
        "status",
        "frozen_on",
        "mutation_policy",
        "parent_frozen_benchmark",
        "amendments",
        "generator",
        "cohorts",
        "invariants",
        "audit_summary",
    }
    assert manifest["benchmark_id"] == "semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1"
    assert manifest["status"] == "frozen"
    assert set(manifest["parent_frozen_benchmark"]) == {"path", "sha256", "benchmark_id"}
    assert manifest["parent_frozen_benchmark"]["sha256"] == _sha256(PARENT_FROZEN)
    for key in ("amendments", "generator"):
        assert set(manifest[key]) == {"path", "sha256"}
        assert manifest[key]["sha256"] == _sha256(REPO_ROOT / manifest[key]["path"])
    assert set(manifest["cohorts"]) == {
        "hard_ground_truth",
        "hard_questions",
        "retrieval_questions",
    }
    for cohort in manifest["cohorts"].values():
        assert set(cohort) == {"path", "sha256", "count", "ordered_ids"}
        assert cohort["sha256"] == _sha256(REPO_ROOT / cohort["path"])
        assert cohort["count"] == len(cohort["ordered_ids"])
    assert all(isinstance(value, str) and value.strip() for value in manifest["invariants"].values())
    assert all(isinstance(value, int) and value >= 0 for value in manifest["audit_summary"].values())
    assert manifest["audit_summary"] == {
        "questions": 10,
        "atomic_answer_claims": 44,
        "important_negatives": 13,
        "parent_expected_id_links": 72,
        "appended_atomic_option_links": 22,
        "appended_negative_option_links": 19,
        "reviewed_expected_id_links": 113,
        "parent_unique_expected_claim_ids": 42,
        "added_unique_claim_ids": 26,
        "reviewed_unique_expected_claim_ids": 68,
        "parent_authoritative_evidence_objects": 44,
        "added_authoritative_evidence_objects": 27,
        "reviewed_authoritative_evidence_objects": 71,
        "rejected_close_alternatives": 38,
    }


def test_generator_is_deterministic_checks_drift_and_never_mutates_parent(
    tmp_path: Path,
) -> None:
    module = _generator()
    parent_paths = [
        PARENT_ROOT / "hard-ground-truth.jsonl",
        PARENT_ROOT / "hard-questions.jsonl",
        PARENT_ROOT / "retrieval-questions.jsonl",
        PARENT_FROZEN,
    ]
    before = {path: _sha256(path) for path in parent_paths}
    first = module.build_outputs(REPO_ROOT)
    second = module.build_outputs(REPO_ROOT)
    assert first == second

    output = tmp_path / "reviewed"
    assert module.main(["--repo-root", str(REPO_ROOT), "--output-dir", str(output)]) == 0
    assert module.main(
        ["--repo-root", str(REPO_ROOT), "--output-dir", str(output), "--check"]
    ) == 0
    (output / "hard-questions.jsonl").write_bytes(b"{}\n")
    assert module.main(
        ["--repo-root", str(REPO_ROOT), "--output-dir", str(output), "--check"]
    ) == 2
    assert {path: _sha256(path) for path in parent_paths} == before
