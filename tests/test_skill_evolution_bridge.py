"""Behavioral checks for candidate execution and independent retrieval scoring."""
from __future__ import annotations

import copy
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bridge = load("evolution_bridge_under_test", "evaluations/skill-evolution/bridge.py")
verifier = load("evolution_verifier_under_test", "evaluations/skill-evolution/verifier.py")
scorer = load("evolution_reference_scorer", "evaluations/private-book-strategy-comparison/scripts/evaluate_all_routes.py")


def example():
    records = {identifier: {"record_id": identifier, "record_sha256": identifier * 64,
                           "source_id": "source", "concept_id": "concept-" + identifier,
                           "concept_path": "concepts/" + identifier + ".md"}
               for identifier in ("a", "b", "c")}
    hits = [{**records[identifier], "rank": rank} for rank, identifier in enumerate(("a", "b", "c"), 1)]
    answer = {"schema_version": "skill-retrieval-trial/1.0", "family": "classical", "builds_byte_identical": True,
              "primary_route": "fusion", "record_identities": records,
              "routes": {"fusion": {"queries": [{"id": "query", "hits": hits, "milliseconds": 5.0}], "p95_ms": 5.0}},
              "build_seconds": 1.0, "knowledge_bytes": 100, "skill_files": {"SKILL.md": "d" * 64}, "imported_candidate_modules": {},
              "knowledge_files": {"semantic/records.jsonl": "f" * 64}, "llm_calls": 0, "answer_quality_evaluated": False}
    contract = {"family": "classical", "primary_route": "fusion", "routes": ["fusion"],
                "records": {key: row["record_sha256"] for key, row in records.items()},
                "record_identities": copy.deepcopy(records), "skill_files": {"SKILL.md": "d" * 64}, "imported_candidate_modules": {},
                "questions": [{"id": "query", "relevant": ["a", "b"]}]}
    return answer, contract


def test_two_equivalent_ideal_orders_and_less_relevant_result():
    answer, contract = example()
    rewards, _ = verifier.evaluate(answer, contract, scorer)
    assert rewards["reward"] == 1
    rows = answer["routes"]["fusion"]["queries"][0]["hits"]
    rows[0], rows[1] = rows[1], rows[0]
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    assert verifier.evaluate(answer, contract, scorer)[0] == rewards
    rows.reverse()
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    observed = verifier.evaluate(answer, contract, scorer)[0]["reward"]
    assert 0 < observed < 1


@pytest.mark.parametrize("mutation", ["missing-query", "wrong-query", "duplicate-hit", "unknown-hit", "wrong-hash", "wrong-concept", "wrong-rank", "boolean-rank", "wrong-family", "missing-route", "wrong-primary", "missing-record", "changed-record", "nondeterministic-build", "nan-latency", "negative-latency"])
def test_shortcuts_and_identity_drift_fail(mutation):
    answer, contract = example()
    row = answer["routes"]["fusion"]["queries"][0]
    if mutation == "missing-query": answer["routes"]["fusion"]["queries"] = []
    elif mutation == "wrong-query": row["id"] = "different"
    elif mutation == "duplicate-hit": row["hits"].append(row["hits"][0])
    elif mutation == "unknown-hit": row["hits"][0]["record_id"] = "unknown"
    elif mutation == "wrong-hash": row["hits"][0]["record_sha256"] = "0" * 64
    elif mutation == "wrong-concept": row["hits"][0]["concept_path"] = "concepts/other.md"
    elif mutation == "wrong-rank": row["hits"][0]["rank"] = 2
    elif mutation == "boolean-rank": row["hits"][0]["rank"] = True
    elif mutation == "wrong-family": answer["family"] = "embeddings"
    elif mutation == "missing-route": answer["routes"] = {}
    elif mutation == "wrong-primary": answer["primary_route"] = "bm25"
    elif mutation == "missing-record": answer["record_identities"].pop("c")
    elif mutation == "changed-record": answer["record_identities"]["a"]["record_sha256"] = "0" * 64
    elif mutation == "nondeterministic-build": answer["builds_byte_identical"] = False
    elif mutation == "nan-latency": answer["routes"]["fusion"]["p95_ms"] = math.nan
    elif mutation == "negative-latency": answer["routes"]["fusion"]["p95_ms"] = -1
    with pytest.raises((ValueError, KeyError)):
        verifier.evaluate(answer, contract, scorer)


@pytest.mark.parametrize("text", ['{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}'])
def test_nonstandard_json_fails(text):
    with pytest.raises(ValueError):
        verifier.strict_json(text)


def test_formatting_is_not_a_quality_signal():
    answer, contract = example()
    one = verifier.evaluate(verifier.strict_json(json.dumps(answer)), contract, scorer)
    two = verifier.evaluate(verifier.strict_json(json.dumps(answer, indent=4, sort_keys=True)), contract, scorer)
    assert one == two


def test_selected_package_controls_execution_and_attestation(tmp_path):
    script = "def load_snapshot(*args, **kwargs): return None\ndef search_snapshot(snapshot, query, mode, top_k): return {'results': [{'record_id': %r}]}\n"
    paths = []
    for label in ("baseline", "candidate"):
        package = tmp_path / label
        target = package / "assets/families/classical/consultant/scripts/_classical_snapshot.py"
        target.parent.mkdir(parents=True)
        target.write_text(script % label, encoding="utf-8")
        paths.append(package)
    observations = []
    for package in paths:
        attestation = {}
        operations = bridge.routes(package, "classical", tmp_path, scorer, attestation)
        observations.append(operations["fusion"]("identical request"))
        key = "assets/families/classical/consultant/scripts/_classical_snapshot.py"
        assert attestation == {key: bridge.sha256(package / key)}
    assert observations == [[{"record_id": "baseline"}], [{"record_id": "candidate"}]]


def test_missing_candidate_module_never_falls_back(tmp_path):
    with pytest.raises(FileNotFoundError):
        bridge.routes(tmp_path, "classical", tmp_path, scorer, {})


def test_tree_binding_detects_content_changes(tmp_path):
    item = tmp_path / "SKILL.md"
    item.write_text("first", encoding="utf-8")
    first = bridge.tree(tmp_path)
    item.write_text("second", encoding="utf-8")
    assert first != bridge.tree(tmp_path)


def test_missing_package_root_is_not_an_empty_valid_package(tmp_path):
    with pytest.raises(ValueError):
        bridge.tree(tmp_path / "missing")
