from __future__ import annotations

import copy
import hashlib
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
GRAPH_SOURCE = ROOT / "skills" / "consult-semantic-okf-entity-graph"
GRAPH_EVOLVED = ROOT / "skills" / "consult-semantic-okf-harbor-entity-graph"
ENSEMBLE_SOURCE = ROOT / "skills" / "consult-semantic-okf-ensemble"
ENSEMBLE_EVOLVED = ROOT / "skills" / "consult-semantic-okf-harbor-ensemble"


def _load_adapter(name: str, skill: Path, local_modules: tuple[str, ...]) -> Any:
    scripts = skill / "scripts"
    for module_name in local_modules:
        sys.modules.pop(module_name, None)
    sys.path.insert(0, str(scripts))
    try:
        spec = importlib.util.spec_from_file_location(name, scripts / "harbor_answer.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(scripts))


GRAPH = _load_adapter(
    "semantic_okf_harbor_graph_adapter_test",
    GRAPH_EVOLVED,
    ("_entity_graph_snapshot", "_entity_graph_model"),
)
ENSEMBLE = _load_adapter(
    "semantic_okf_harbor_ensemble_adapter_test",
    ENSEMBLE_EVOLVED,
    (
        "_ensemble_snapshot",
        "_adaptive_snapshot",
        "_embedding_snapshot",
        "_entity_graph_snapshot",
        "_entity_graph_model",
    ),
)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _record(name: str, body: str) -> dict[str, Any]:
    return {
        "source_id": f"source-{name}",
        "record_id": f"records/{name}",
        "concept_path": f"concepts/{name}.md",
        "source_path": f"sources/{name}.md",
        "record_sha256": hashlib.sha256(f"record:{name}".encode()).hexdigest(),
        "body": body,
    }


def _graph_hit(record: dict[str, Any], rank: int) -> dict[str, Any]:
    body = record["body"]
    return {
        "rank": rank,
        "section_id": f"section-{record['source_id']}",
        "heading": record["record_id"],
        **{key: record[key] for key in ("source_id", "record_id", "record_sha256", "concept_path", "source_path")},
        "locator": {
            "kind": "character-range",
            "target": "record-body",
            "start": 0,
            "end": len(body),
            "fragment": "record-body-test",
        },
        "text": body,
        "text_sha256": _sha(body),
        "supporting_edge_ids": ["edge-must-never-be-support"],
    }


def _ensemble_result(record: dict[str, Any], rank: int) -> tuple[dict[str, Any], dict[str, Any]]:
    body = record["body"]
    identity = {
        key: record[key]
        for key in ("source_id", "record_id", "record_sha256", "concept_path", "source_path")
    }
    hit = {"rank": rank, "group_id": f"group-{record['source_id']}", **identity}
    passage = {
        "rank": rank,
        "evidence_id": f"evidence-{record['source_id']}",
        **identity,
        "locator": {
            "kind": "character-range",
            "target": "record-body",
            "start": 0,
            "end": len(body),
            "fragment": None,
        },
        "text": body,
        "text_sha256": _sha(body),
    }
    return hit, passage


def _parameters(module: Any, **overrides: Any) -> dict[str, Any]:
    base = {
        "facet_limit": 8,
        "per_facet": 1,
        "max_supports": 8,
        "excerpt_chars": 240,
        "strategy": module.STRATEGY,
    }
    base.update(overrides)
    return base


def _valid_draft(pack: dict[str, Any]) -> dict[str, Any]:
    support_ids = [row["support_id"] for row in pack["supports"]]
    claims = [
        {"statement": f"Atomic statement {index + 1}.", "evidence_indices": [index]}
        for index in range(len(support_ids))
    ]
    return {
        "question_id": pack["question_id"],
        "question_sha256": pack["question_sha256"],
        "parameters": pack["parameters"],
        "support_pack_sha256": pack["support_pack_sha256"],
        "answer": {"summary": "A compact evidence-grounded synthesis.", "claims": claims},
        "evidence": support_ids,
    }


@pytest.mark.parametrize(
    ("source", "evolved"),
    ((GRAPH_SOURCE, GRAPH_EVOLVED), (ENSEMBLE_SOURCE, ENSEMBLE_EVOLVED)),
)
def test_reviewed_source_scripts_are_preserved_byte_for_byte(source: Path, evolved: Path) -> None:
    source_files = sorted(
        path.relative_to(source / "scripts")
        for path in (source / "scripts").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    assert source_files
    for relative in source_files:
        assert (evolved / "scripts" / relative).read_bytes() == (source / "scripts" / relative).read_bytes()
    assert (evolved / "scripts" / "harbor_answer.py").is_file()


def test_graph_adapter_unions_fusion_facets_and_projects_exact_parents(monkeypatch: pytest.MonkeyPatch) -> None:
    alpha = _record("alpha", "Alpha systems establish the primary mechanism." * 8)
    beta = _record("beta", "Beta safety establishes the independent exclusion." * 8)
    snapshot = SimpleNamespace(records=[alpha, beta])
    calls: list[tuple[str, str, int]] = []

    monkeypatch.setattr(GRAPH, "load_snapshot", lambda _: snapshot)

    def search(_: Any, query: str, mode: str, top_k: int) -> dict[str, Any]:
        calls.append((query, mode, top_k))
        record = beta if query.casefold() == "beta safety" else alpha
        return {"results": [_graph_hit(record, 1)]}

    monkeypatch.setattr(GRAPH, "search_snapshot", search)
    question = "Alpha systems and beta safety."
    params = _parameters(GRAPH, mode="fusion")
    pack = GRAPH.build_support_pack(Path("unused"), "q901", question, params)

    assert calls[0] == (question, "fusion", 1)
    assert all(mode == "fusion" for _, mode, _ in calls)
    assert [row["source_id"] for row in pack["supports"]] == ["source-alpha", "source-beta"]
    assert all(row["locator"] == {"kind": "record", "target": "record.body"} for row in pack["supports"])
    assert all("edge" not in key for row in pack["supports"] for key in row)
    assert all(len(row["excerpt"]) <= params["excerpt_chars"] for row in pack["supports"])
    assert len({(row["source_id"], row["record_id"]) for row in pack["supports"]}) == 2

    result = GRAPH.finalize(pack, _valid_draft(pack))
    assert list(result) == ["question_id", "answer", "evidence"]
    assert [claim["evidence_indices"] for claim in result["answer"]["claims"]] == [[0], [1]]
    assert [row["source_id"] for row in result["evidence"]] == ["source-alpha", "source-beta"]
    assert list(result["evidence"][0]) == list(GRAPH.EVIDENCE_KEYS)


def test_ensemble_adapter_adds_focused_candidate_missing_from_full_query(monkeypatch: pytest.MonkeyPatch) -> None:
    alpha = _record("alpha", "Alpha systems establish the primary mechanism." * 8)
    beta = _record("beta", "Beta safety establishes the independent exclusion." * 8)
    snapshot = SimpleNamespace(graph=SimpleNamespace(records=[alpha, beta]))
    calls: list[tuple[str, str, int]] = []

    monkeypatch.setattr(ENSEMBLE, "load_snapshot", lambda _: snapshot)

    def search(_: Any, query: str, policy: str, top_k: int) -> dict[str, Any]:
        calls.append((query, policy, top_k))
        record = beta if query.casefold() == "beta safety" else alpha
        hit, passage = _ensemble_result(record, 1)
        return {"results": [hit], "evidence_rows": [passage]}

    monkeypatch.setattr(ENSEMBLE, "search_snapshot", search)
    question = "Alpha systems and beta safety."
    params = _parameters(ENSEMBLE, policy="quality")
    pack = ENSEMBLE.build_support_pack(Path("unused"), "q902", question, params)

    assert calls[0] == (question, "quality", 1)
    assert any(query == "beta safety" for query, _, _ in calls[1:])
    assert all(policy == "quality" for _, policy, _ in calls)
    assert pack["candidate_union"] == {
        "full_query": True,
        "focused_query_count": 2,
        "selected_parent_count": 2,
    }
    assert [row["source_id"] for row in pack["supports"]] == ["source-alpha", "source-beta"]
    assert all(row["locator"] == {"kind": "record", "target": "record.body"} for row in pack["supports"])

    result = ENSEMBLE.finalize(pack, _valid_draft(pack))
    assert list(result) == ["question_id", "answer", "evidence"]
    assert [row["source_id"] for row in result["evidence"]] == ["source-alpha", "source-beta"]


@pytest.mark.parametrize("module", (GRAPH, ENSEMBLE))
def test_finalizer_fails_closed_on_unknown_parameters_supports_and_order(module: Any) -> None:
    row_one = {
        "support_id": "support-one",
        **{key: value for key, value in _parent_row("one").items()},
    }
    row_two = {
        "support_id": "support-two",
        **{key: value for key, value in _parent_row("two").items()},
    }
    pack = {
        "question_id": "q903",
        "question_sha256": "a" * 64,
        "parameters": {"closed": True},
        "support_pack_sha256": "b" * 64,
        "supports": [row_one, row_two],
    }
    draft = _valid_draft(pack)

    changed_parameters = copy.deepcopy(draft)
    changed_parameters["parameters"] = {"closed": False}
    with pytest.raises(module.AnswerError, match="parameters"):
        module.finalize(pack, changed_parameters)

    unknown = copy.deepcopy(draft)
    unknown["evidence"][0] = "support-tampered"
    with pytest.raises(module.AnswerError, match="unknown or tampered"):
        module.finalize(pack, unknown)

    duplicate = copy.deepcopy(draft)
    duplicate["evidence"] = ["support-one", "support-one"]
    with pytest.raises(module.AnswerError, match="duplicate support"):
        module.finalize(pack, duplicate)

    wrong_order = copy.deepcopy(draft)
    wrong_order["answer"]["claims"] = [
        {"statement": "Second first.", "evidence_indices": [1]},
        {"statement": "First second.", "evidence_indices": [0]},
    ]
    with pytest.raises(module.AnswerError, match="first use"):
        module.finalize(pack, wrong_order)

    unused = copy.deepcopy(draft)
    unused["answer"]["claims"] = [{"statement": "Only one.", "evidence_indices": [0]}]
    with pytest.raises(module.AnswerError, match="unused"):
        module.finalize(pack, unused)


@pytest.mark.parametrize("module", (GRAPH, ENSEMBLE))
def test_strict_json_rejects_duplicate_members(module: Any) -> None:
    with pytest.raises(module.AnswerError, match="duplicate JSON key"):
        module._loads_json('{"answer":1,"answer":2}', "test")


def test_graph_rejects_tampered_section_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record("alpha", "Authoritative graph section text.")
    snapshot = SimpleNamespace(records=[record])
    hit = _graph_hit(record, 1)
    hit["text"] = "Tampered graph section text."
    monkeypatch.setattr(GRAPH, "load_snapshot", lambda _: snapshot)
    monkeypatch.setattr(GRAPH, "search_snapshot", lambda *_: {"results": [hit]})
    with pytest.raises(GRAPH.AnswerError, match="text or hash"):
        GRAPH.build_support_pack(
            Path("unused"),
            "q904",
            "Graph support question",
            _parameters(GRAPH, mode="fusion"),
        )


def test_ensemble_rejects_tampered_passage_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record("alpha", "Authoritative ensemble passage text.")
    snapshot = SimpleNamespace(graph=SimpleNamespace(records=[record]))
    hit, passage = _ensemble_result(record, 1)
    passage["text_sha256"] = "0" * 64
    monkeypatch.setattr(ENSEMBLE, "load_snapshot", lambda _: snapshot)
    monkeypatch.setattr(
        ENSEMBLE,
        "search_snapshot",
        lambda *_: {"results": [hit], "evidence_rows": [passage]},
    )
    with pytest.raises(ENSEMBLE.AnswerError, match="text or hash"):
        ENSEMBLE.build_support_pack(
            Path("unused"),
            "q905",
            "Ensemble support question",
            _parameters(ENSEMBLE, policy="fast"),
        )


def _parent_row(name: str) -> dict[str, Any]:
    record = _record(name, f"Authoritative {name} body.")
    return {
        "source_id": record["source_id"],
        "record_id": record["record_id"],
        "concept_path": record["concept_path"],
        "source_path": record["source_path"],
        "record_sha256": record["record_sha256"],
        "locator": {"kind": "record", "target": "record.body"},
        "text_sha256": _sha(record["body"]),
    }
