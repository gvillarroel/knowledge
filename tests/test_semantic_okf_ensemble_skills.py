from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Iterator

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-ensemble"
CONSULT_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-ensemble"
CONSULT_SCRIPTS = CONSULT_ROOT / "scripts"
FINAL_BUNDLE = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "results"
    / "runs"
    / "20260715-ensemble-final-03"
    / "workspace-a"
    / "knowledge"
)
Q031_QUERY = (
    "A production router must choose among question-only or standalone-model answering, "
    "basic RAG, and GraphRAG before generation. Derive an evidence-based decision boundary "
    "for simple facts, interconnected synthesis, and noisy graph evidence, and explain why "
    "an always-use-the-graph policy is unsupported."
)
RUNTIME_MODULES = {
    "_adaptive_snapshot",
    "_embedding_snapshot",
    "_ensemble_snapshot",
    "_entity_graph_model",
    "_entity_graph_snapshot",
}


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_canonical(value) + "\n", encoding="utf-8")


def _tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_consult_skill_mandates_in_memory_finalizer_stdout_gate() -> None:
    skill = (CONSULT_ROOT / "SKILL.md").read_text(encoding="utf-8")

    required = [
        "Enforce the CLI-only structured-answer gate",
        "Use only the packaged read-only CLI",
        "Deep-validate the bundle before retrieval",
        "Read every `coverage-brief` page",
        "full-coverage and priority-order",
        "finalize-answer --draft -",
        "Return the last successful finalizer JSON verbatim without modification",
        "never merge stderr with `2>&1`",
        "Do not hand-author a non-null contracted response as a fallback",
        "Never skip, repeat, or reorder a page",
        "Keep stdout and stderr separate",
        "without parsing and reserializing it",
        "$DraftJson",
        "$LASTEXITCODE -ne 0",
        "--summary-min-words",
        "--summary-max-words",
    ]
    assert all(text in skill for text in required)
    assert "Get-Content answer-draft.json" not in skill
    forbidden = [
        "semantic_okf_bootstrap_skill",
        "semantic_okf_inspect",
        "semantic_okf_coverage_brief",
        "semantic_okf_prepare_answer",
        "semantic_okf_confirm_answer",
        "semantic-okf-prepared-answer",
        "mcp-runtime",
        "publication-runtime",
    ]
    assert all(text not in skill.casefold() for text in forbidden)
    assert not (CONSULT_ROOT / "mcp-runtime").exists()
    assert not (CONSULT_ROOT / "publication-runtime").exists()


def test_consult_launcher_uses_explicit_absolute_python_and_fails_closed(tmp_path: Path) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is required for the packaged Windows launcher")
    launcher = CONSULT_SCRIPTS / "run_query.ps1"
    launcher_text = launcher.read_text(encoding="utf-8")
    assert "Select-Object -First 1" in launcher_text
    environment = os.environ.copy()
    environment["SEMANTIC_OKF_PYTHON"] = sys.executable
    environment["SEMANTIC_OKF_HF_HUB_CACHE"] = str(tmp_path.resolve())
    valid = subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-File", str(launcher), "--help"],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert valid.returncode == 0, valid.stderr
    assert "coverage-brief" in valid.stdout
    assert "finalize-answer" in valid.stdout

    environment["SEMANTIC_OKF_PYTHON"] = "python"
    rejected = subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-File", str(launcher), "--help"],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert "must be an absolute executable path" in rejected.stderr

    environment["SEMANTIC_OKF_PYTHON"] = sys.executable
    environment["SEMANTIC_OKF_HF_HUB_CACHE"] = "relative-cache"
    rejected_cache = subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-File", str(launcher), "--help"],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected_cache.returncode != 0
    assert "must be an absolute directory path" in rejected_cache.stderr


def test_consult_launcher_preserves_multiline_pipeline_input(tmp_path: Path) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is required for the packaged Windows launcher")
    launcher = tmp_path / "run_query.ps1"
    shutil.copy2(CONSULT_SCRIPTS / "run_query.ps1", launcher)
    (tmp_path / "query_semantic_okf_ensemble.py").write_text(
        "import json, sys\n"
        "print(json.dumps({'args': sys.argv[1:], 'stdin': sys.stdin.read()}))\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["SEMANTIC_OKF_PYTHON"] = sys.executable
    environment.pop("SEMANTIC_OKF_HF_HUB_CACHE", None)
    command = (
        "$payload = @'\nline one\nline two\n'@; "
        f"$payload | & '{launcher}' bundle probe"
    )
    completed = subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-Command", command],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["args"] == ["bundle", "probe"]
    assert payload["stdin"].splitlines() == ["line one", "line two"]


@pytest.fixture(scope="module")
def runtime() -> Iterator[ModuleType]:
    previous = {name: sys.modules.get(name) for name in RUNTIME_MODULES}
    for name in RUNTIME_MODULES:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(CONSULT_SCRIPTS))
    unique_name = "_test_semantic_okf_ensemble_snapshot"
    try:
        spec = importlib.util.spec_from_file_location(
            unique_name,
            CONSULT_SCRIPTS / "_ensemble_snapshot.py",
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[unique_name] = module
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.path.remove(str(CONSULT_SCRIPTS))
        sys.modules.pop(unique_name, None)
        for name in RUNTIME_MODULES:
            sys.modules.pop(name, None)
            if previous[name] is not None:
                sys.modules[name] = previous[name]


def _policy(
    routes: list[str],
    weights: list[float],
    *,
    promotion_route: str = "graph_lexical",
    confirmation_routes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "routes": routes,
        "weights": weights,
        "rrf_k": 5,
        "protected_route": "adaptive",
        "promotion": {
            "route": promotion_route,
            "confirmation_routes": confirmation_routes or ["adaptive"],
            "confirmation_depth": 3,
            "minimum_confirmations": 1,
            "maximum_protected_rank": 3,
        },
    }


def _plan(*, quality_uses_embedding: bool = False) -> dict[str, Any]:
    direct = _policy(["adaptive", "graph_lexical"], [4.0, 1.0])
    quality = (
        _policy(
            ["adaptive", "graph_lexical", "embedding_hybrid"],
            [4.0, 1.0, 1.0],
        )
        if quality_uses_embedding
        else copy.deepcopy(direct)
    )
    return {
        "schema_version": "1.0",
        "adaptive": {},
        "entity_graph": {},
        "embedding": {},
        "policies": {
            "default": "quality",
            "quality": quality,
            "fast": copy.deepcopy(direct),
            "robust": copy.deepcopy(direct),
        },
        "quality_gates": {
            "required_components": ["adaptive", "entity_graph", "embedding"],
            "protect_candidate_set": True,
            "require_core_parity": True,
            "reviewed_graph_claims_only": True,
            "reviewed_embedding_claims_only": True,
            "candidate_edge_weight": 0.0,
            "maximum_graph_claims_per_facet": 2,
            "maximum_graph_claims_total": 3,
            "maximum_embedding_claims_per_facet": 2,
            "maximum_embedding_claims_total": 3,
            "require_facet_status": True,
            "require_exact_answer_bindings": True,
        },
    }


def _snapshot(plan: dict[str, Any] | None = None, *, root: Path | None = None) -> Any:
    selected_plan = plan or _plan()
    return SimpleNamespace(
        root=root or REPO_ROOT,
        index={
            "plan": selected_plan,
            "ensemble_plan_sha256": hashlib.sha256(
                _canonical(selected_plan).encode("utf-8")
            ).hexdigest(),
            "core": {"tree_sha256": "core-tree"},
        },
        index_sha256="ensemble-index",
        adaptive=SimpleNamespace(
            index={"plan": {}},
            answer_bindings=[],
            lexicon={
                "tokenization": {
                    "tokenizer": "ascii-alphanumeric-v1",
                    "stopwords": "english-v1",
                    "min_token_length": 2,
                    "ngram_range": [1, 2],
                },
                "terms": [],
            },
        ),
        graph=SimpleNamespace(entities=[], edges=[]),
        embedding=SimpleNamespace(),
        deep_validation=False,
    )


def _search_payload(papers: list[str], *, adaptive: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "results": [
            {
                "rank": rank,
                "paper_id": paper_id,
                "document_id": f"document-{paper_id}",
                "score": 1.0 / rank,
            }
            for rank, paper_id in enumerate(papers, start=1)
        ]
    }
    if adaptive:
        payload.update(
            {
                "evidence_rows": [
                    {"rank": rank, "paper_id": paper_id, "record_id": f"source-{paper_id}"}
                    for rank, paper_id in enumerate(papers, start=1)
                ],
                "answer_evidence_rows": [
                    {"rank": rank, "paper_id": paper_id, "record_id": f"claim-{paper_id}"}
                    for rank, paper_id in enumerate(papers, start=1)
                ],
                "evidence_contract": {"authoritative": True},
                "answer_evidence_contract": {"exact_bindings": True},
            }
        )
    return payload


def _install_search_routes(
    monkeypatch: pytest.MonkeyPatch,
    runtime: ModuleType,
    rankings: dict[str, list[str]],
) -> None:
    def run_route(_snapshot: Any, route: str, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return _search_payload(rankings[route], adaptive=route == "adaptive")

    monkeypatch.setattr(runtime, "_run_route", run_route)


def _write_minimal_bundle(runtime: ModuleType, root: Path, plan: dict[str, Any]) -> None:
    core = {"tree_sha256": "core-tree"}
    component_specs = {
        "adaptive": ("adaptive/index.json", "adaptive"),
        "entity_graph": ("entity-graph/index.json", "entity_graph"),
        "embedding": ("retrieval/index.json", "embedding"),
    }
    for relative, _name in component_specs.values():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(
            path,
            {
                "schema_version": "1.0",
                "authoritative": False,
                "core": core,
            },
        )
    components = {
        name: runtime._component(root, name, relative)
        for name, (relative, _label) in component_specs.items()
    }
    ensemble = root / "ensemble"
    ensemble.mkdir()
    index = {
        "schema_version": "1.0",
        "authoritative": False,
        "discovery_only": True,
        "ensemble_plan_sha256": runtime.sha256_canonical(plan),
        "plan": plan,
        "core": core,
        "components": components,
        "algorithms": {
            "direct_search": runtime.ALGORITHM_ID,
            "coverage": runtime.COVERAGE_ALGORITHM_ID,
            "answer_gate": runtime.ANSWER_GATE_ID,
        },
        "summary": {
            "policies": 3,
            "required_components": 3,
            "default_policy": "quality",
        },
    }
    _write_json(ensemble / "index.json", index)
    report = {
        "schema_version": "1.0",
        "valid": True,
        "status": "pass",
        "authoritative": False,
        "discovery_only": True,
        "errors": [],
        "warnings": [],
        "ensemble_plan_sha256": index["ensemble_plan_sha256"],
        "core": core,
        "components": {name: component["index"] for name, component in components.items()},
        "artifacts": {"index": runtime._artifact(root, "ensemble/index.json")},
        "summary": index["summary"],
    }
    _write_json(ensemble / "build-report.json", report)


def test_plan_is_closed_leakage_resistant_and_requires_protected_scoring_route(
    runtime: ModuleType,
) -> None:
    runtime._validate_plan(_plan())

    extra = _plan()
    extra["unexpected"] = True
    with pytest.raises(runtime.SnapshotError, match="closed schema"):
        runtime._validate_plan(extra)

    leaked = _plan()
    leaked["adaptive"]["benchmark"] = "q001-hard"
    with pytest.raises(runtime.SnapshotError, match="question IDs"):
        runtime._validate_plan(leaked)

    missing_protected = _plan()
    missing_protected["policies"]["fast"]["routes"] = ["graph_lexical"]
    missing_protected["policies"]["fast"]["weights"] = [1.0]
    with pytest.raises(runtime.SnapshotError, match="include the adaptive route"):
        runtime._validate_plan(missing_protected)

    consensus_only = _plan()
    consensus_only["policies"]["fast"]["routes"] = ["adaptive"]
    consensus_only["policies"]["fast"]["weights"] = [4.0]
    runtime._validate_plan(consensus_only)

    no_op_self_promotion = copy.deepcopy(consensus_only)
    no_op_self_promotion["policies"]["robust"]["routes"] = ["adaptive"]
    no_op_self_promotion["policies"]["robust"]["weights"] = [4.0]
    no_op_self_promotion["policies"]["robust"]["promotion"]["route"] = "adaptive"
    no_op_self_promotion["policies"]["robust"]["promotion"]["confirmation_routes"] = [
        "adaptive"
    ]
    runtime._validate_plan(no_op_self_promotion)


def test_closed_index_load_is_read_only_and_rejects_unknown_artifacts(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    plan = _plan()
    _write_minimal_bundle(runtime, tmp_path, plan)
    core = {"tree_sha256": "core-tree"}
    adaptive = SimpleNamespace(index={"core": core}, answer_bindings=[])
    graph = SimpleNamespace(index={"core": core}, entities=[], edges=[])
    embedding = SimpleNamespace(index={"core": core})
    monkeypatch.setattr(runtime.adaptive_runtime, "load_snapshot", lambda *_a, **_k: adaptive)
    monkeypatch.setattr(runtime.graph_runtime, "load_snapshot", lambda *_a, **_k: graph)
    monkeypatch.setattr(runtime.embedding_runtime, "load_snapshot", lambda *_a, **_k: embedding)

    before = _tree(tmp_path)
    loaded = runtime.load_snapshot(tmp_path)
    assert loaded.index["plan"] == plan
    assert runtime.inspect_snapshot(loaded)["read_only"] is True
    assert _tree(tmp_path) == before

    (tmp_path / "ensemble" / "unexpected.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(runtime.SnapshotError, match="artifact set is closed"):
        runtime.load_snapshot(tmp_path)


def test_protected_set_reranking_and_bounded_promotion(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adaptive = ["paper-a", "paper-b", "paper-c", "paper-d"]
    _install_search_routes(
        monkeypatch,
        runtime,
        {
            "adaptive": adaptive,
            "graph_lexical": ["paper-b", "paper-a", "paper-d", "paper-c"],
        },
    )
    promoted = runtime.search_snapshot(_snapshot(), "graph retrieval", "quality", 4)
    assert promoted["candidate_set_gate"] == {
        "protected_route": "adaptive",
        "protected_paper_ids": adaptive,
        "selected_paper_ids": ["paper-b", "paper-a", "paper-c", "paper-d"],
        "preserved_exactly": True,
    }
    assert promoted["promotion_gate"]["passed"] is True
    assert promoted["promotion_gate"]["candidate"] == "paper-b"
    assert promoted["policy"]["effective_scoring_routes"] == [
        "adaptive",
        "graph_lexical",
    ]
    assert promoted["results"][0]["score"] == pytest.approx(4 / 7 + 1 / 6)
    assert {row["paper_id"] for row in promoted["results"]} == set(adaptive)

    _install_search_routes(
        monkeypatch,
        runtime,
        {
            "adaptive": adaptive,
            "graph_lexical": ["paper-d", "paper-a", "paper-b", "paper-c"],
        },
    )
    bounded = runtime.search_snapshot(_snapshot(), "graph retrieval", "quality", 4)
    assert bounded["promotion_gate"]["candidate"] == "paper-d"
    assert bounded["promotion_gate"]["protected_rank"] == 4
    assert bounded["promotion_gate"]["passed"] is False
    assert bounded["results"][0]["paper_id"] != "paper-d"
    assert set(bounded["candidate_set_gate"]["selected_paper_ids"]) == set(adaptive)


def test_exact_fused_score_ties_use_component_consensus_before_paper_id(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _plan()
    plan["policies"]["quality"] = {
        "routes": ["adaptive", "graph_lexical"],
        "weights": [1.0, 1.0],
        "rrf_k": 0,
        "protected_route": "adaptive",
        "promotion": {
            "route": "graph_lexical",
            "confirmation_routes": ["adaptive", "graph_lexical"],
            "confirmation_depth": 2,
            "minimum_confirmations": 2,
            "maximum_protected_rank": 2,
        },
    }
    _install_search_routes(
        monkeypatch,
        runtime,
        {
            "adaptive": ["paper-z", "paper-a"],
            "graph_lexical": ["paper-outside", "paper-a"],
        },
    )

    result = runtime.search_snapshot(_snapshot(plan), "tie", "quality", 2)

    assert result["results"][0]["paper_id"] == "paper-z"
    assert result["results"][0]["score"] == pytest.approx(1.0)
    assert result["results"][1]["paper_id"] == "paper-a"
    assert result["results"][1]["score"] == pytest.approx(1.0)
    assert result["promotion_gate"]["passed"] is False


def test_embedding_unavailability_fails_quality_without_silent_fallback(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def run_route(_snapshot: Any, route: str, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        calls.append(route)
        if route == "embedding_hybrid":
            raise runtime.embedding_runtime.ProviderUnavailable("model is not installed")
        return _search_payload(["paper-a", "paper-b"], adaptive=route == "adaptive")

    monkeypatch.setattr(runtime, "_run_route", run_route)
    snapshot = _snapshot(_plan(quality_uses_embedding=True))
    with pytest.raises(runtime.SnapshotError, match="choose fast or robust explicitly"):
        runtime.search_snapshot(snapshot, "semantic retrieval", "quality", 2)
    assert "embedding_hybrid" in calls

    calls.clear()
    robust = runtime.search_snapshot(snapshot, "semantic retrieval", "robust", 2)
    assert robust["effective_policy"] == "robust"
    assert "embedding_hybrid" not in calls


def test_embedding_source_identity_normalizes_to_protected_arxiv_paper_id(
    runtime: ModuleType,
) -> None:
    ranking, rows = runtime._paper_ranking(
        {
            "hits": [
                {
                    "source_id": "paper-2503-06474v2",
                    "record_id": "sources/markdown/2503.06474v2",
                }
            ]
        }
    )
    assert ranking == ["2503.06474v2"]
    assert list(rows) == ranking


def test_graph_claim_candidates_require_reviewed_edges_and_exact_bindings(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def entity(
        entity_id: str,
        entity_type: str,
        *,
        review_state: str = "reviewed",
        claim_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "review_state": review_state,
            "authoritative_identity": {"record_id": claim_id} if claim_id else None,
        }

    graph = SimpleNamespace(
        entities=[
            entity("method", "method"),
            entity("claim-reviewed", "claim", claim_id="claim-1"),
            entity("claim-candidate-edge", "claim", claim_id="claim-2"),
            entity("claim-unreviewed", "claim", review_state="candidate", claim_id="claim-3"),
            entity("claim-no-binding", "claim", claim_id="claim-4"),
        ],
        edges=[
            {
                "source_node": "method",
                "target_node": "claim-reviewed",
                "review_state": "reviewed",
                "weight": 4.0,
            },
            {
                "source_node": "method",
                "target_node": "claim-candidate-edge",
                "review_state": "candidate",
                "weight": 100.0,
            },
            {
                "source_node": "method",
                "target_node": "claim-unreviewed",
                "review_state": "reviewed",
                "weight": 100.0,
            },
            {
                "source_node": "method",
                "target_node": "claim-no-binding",
                "review_state": "reviewed",
                "weight": 100.0,
            },
        ],
    )
    binding = {
        "record_id": "claim-1",
        "paper_id": "paper-a",
        "concept_path": "concepts/paper-a/claim-1.json",
        "source_path": "sources/paper-a.md",
        "locator_tokens": ["page:1", "section:methods", "page:1"],
        "citation_pages": [1],
        "authoritative_text": "The reviewed method supports the claim.",
        "authoritative_text_sha256": "claim-text-sha",
    }
    snapshot = _snapshot()
    snapshot.graph = graph
    snapshot.adaptive.answer_bindings = [binding]
    monkeypatch.setattr(
        runtime.graph_runtime,
        "_resolve_entities",
        lambda *_args: [{"entity_id": "method", "score": 1.0}],
    )

    rows = runtime._graph_claim_candidates(snapshot, "reviewed method", maximum=10)
    assert [row["claim_id"] for row in rows] == ["claim-1"]
    assert rows[0]["review_state"] == "reviewed"
    assert rows[0]["concept_path"] == binding["concept_path"]
    assert rows[0]["source_path"] == binding["source_path"]
    assert rows[0]["locators"] == ["page:1", "section:methods"]
    assert rows[0]["authoritative_text_sha256"] == "claim-text-sha"


def test_embedding_claim_candidates_require_reviewed_exact_bindings(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = {
        "record_id": "claim-1",
        "source_id": "claims-paper-a",
        "source_path": "sources/claims/paper-a.jsonl",
        "paper_id": "paper-a",
        "concept_path": "concepts/claims-paper-a/claim-1.md",
        "locator_tokens": ["PDF-page-2"],
        "citation_pages": [2],
        "authoritative_text": "A reviewed claim.",
        "authoritative_text_sha256": "claim-text-sha",
        "review_state": "reviewed",
    }
    snapshot = _snapshot()
    snapshot.adaptive.answer_bindings = [binding]
    captured: dict[str, Any] = {}

    def run_route(
        _snapshot: Any,
        route: str,
        query: str,
        top_k: int,
        **filters: Any,
    ) -> dict[str, Any]:
        captured.update({"route": route, "query": query, "top_k": top_k, **filters})
        return {
            "hits": [
                {
                    "record_id": "claim-1",
                    "source_id": binding["source_id"],
                    "source_path": binding["source_path"],
                    "concept_path": binding["concept_path"],
                    "scores": {"hybrid": 0.75},
                },
                {
                    "record_id": "claim-unbound",
                    "source_id": binding["source_id"],
                    "source_path": binding["source_path"],
                    "concept_path": "concepts/claim-unbound.md",
                    "scores": {"hybrid": 1.0},
                },
            ]
        }

    monkeypatch.setattr(runtime, "_run_route", run_route)
    rows = runtime._embedding_claim_candidates(
        snapshot,
        "semantic facet",
        maximum=2,
        preferred_paper_ids=("paper-a",),
    )
    assert [row["claim_id"] for row in rows] == ["claim-1"]
    assert rows[0]["review_state"] == "reviewed"
    assert rows[0]["score"] == 0.75
    assert captured == {
        "route": "embedding_hybrid",
        "query": "semantic facet",
        "top_k": 2,
        "source_ids": ("claims-paper-a",),
        "concept_ids": (),
        "concept_types": (),
    }


def test_embedding_claim_candidates_diversify_over_leading_adaptive_papers(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paper_claims = {
        paper: [f"claim-{paper}-{number}" for number in range(1, 7)]
        for paper in ("paper-a", "paper-b", "paper-c")
    }
    other = [f"claim-paper-z-{number}" for number in range(1, 5)]
    ordered = [
        paper_claims["paper-a"][0],
        paper_claims["paper-b"][0],
        paper_claims["paper-c"][0],
        paper_claims["paper-a"][1],
        paper_claims["paper-b"][1],
        paper_claims["paper-c"][1],
        *paper_claims["paper-a"][2:],
        *paper_claims["paper-b"][2:],
        *paper_claims["paper-c"][2:],
        *other,
    ]
    bindings = []
    for claim_id in ordered:
        paper_id = claim_id.removeprefix("claim-").rsplit("-", 1)[0]
        bindings.append(
            {
                "record_id": claim_id,
                "source_id": f"claims-{paper_id}",
                "source_path": f"sources/claims/{paper_id}.jsonl",
                "paper_id": paper_id,
                "concept_path": f"concepts/{claim_id}.md",
                "locator_tokens": ["PDF-page-1"],
                "citation_pages": [1],
                "authoritative_text": claim_id,
                "authoritative_text_sha256": hashlib.sha256(
                    claim_id.encode("utf-8")
                ).hexdigest(),
                "review_state": "reviewed",
            }
        )
    by_id = {row["record_id"]: row for row in bindings}
    snapshot = _snapshot()
    snapshot.adaptive.answer_bindings = bindings

    monkeypatch.setattr(
        runtime,
        "_run_route",
        lambda *_args, **_kwargs: {
            "hits": [
                {
                    "record_id": claim_id,
                    "source_id": by_id[claim_id]["source_id"],
                    "source_path": by_id[claim_id]["source_path"],
                    "concept_path": by_id[claim_id]["concept_path"],
                    "scores": {"hybrid": 1.0 / rank},
                }
                for rank, claim_id in enumerate(ordered, 1)
            ]
        },
    )
    rows = runtime._embedding_claim_candidates(
        snapshot,
        "facet",
        maximum=20,
        preferred_paper_ids=("paper-a", "paper-b", "paper-c", "paper-z"),
    )
    selected = [row["claim_id"] for row in rows]
    assert selected[:6] == ordered[:6]
    assert all(claim_id in selected for paper in paper_claims.values() for claim_id in paper)
    assert len(selected) == len(set(selected)) == 20
    assert [row["rank"] for row in rows] == list(range(1, 21))
    assert runtime.EMBEDDING_CLAIM_RERANK_ID in (
        "adaptive-paper-conditioned-claim-diversification-v1",
    )


def test_coverage_multisignal_union_is_globally_unique_and_bounded(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adaptive = {
        "primary": {"ranked_bindings": [{"record_id": "adaptive-primary"}]},
        "coverage_facets": [
            {"facet": "facet one", "candidates": [{"claim_id": "adaptive-facet"}]},
            {"facet": "facet two", "candidates": []},
        ],
    }
    monkeypatch.setattr(
        runtime.adaptive_runtime,
        "build_coverage_pack",
        lambda *_args, **_kwargs: copy.deepcopy(adaptive),
    )
    candidates = {
        "full question": ["graph-1", "graph-2"],
        "facet one": ["graph-2", "graph-3"],
        "facet two": ["graph-4", "graph-5"],
    }
    embedding = {
        "full question": ["embedding-1", "graph-2"],
        "facet one": ["embedding-2", "embedding-3"],
        "facet two": ["embedding-4"],
    }

    def graph_candidates(_snapshot: Any, query: str, maximum: int) -> list[dict[str, Any]]:
        return [
            {"claim_id": claim_id, "review_state": "reviewed"}
            for claim_id in candidates[query][:maximum]
        ]

    monkeypatch.setattr(runtime, "_graph_claim_candidates", graph_candidates)
    monkeypatch.setattr(
        runtime,
        "_embedding_claim_candidates",
        lambda _snapshot, query, maximum, preferred_paper_ids=(): [
            {"claim_id": claim_id, "review_state": "reviewed"}
            for claim_id in embedding[query][:maximum]
        ],
    )
    coverage = runtime.build_coverage_pack(_snapshot(), "full question", 10, 5, 5)
    flattened = [
        candidate["claim_id"]
        for row in coverage["graph_queries"]
        for candidate in row["candidates"]
    ]
    assert flattened == ["graph-1", "graph-2", "graph-3"]
    embedding_flattened = [
        candidate["claim_id"]
        for row in coverage["embedding_queries"]
        for candidate in row["candidates"]
    ]
    assert embedding_flattened == ["embedding-1", "graph-2", "embedding-2"]
    assert coverage["graph_candidate_claims"] == 3
    assert coverage["embedding_candidate_claims"] == 3
    assert coverage["unique_candidate_claims"] == 7
    assert coverage["union_claim_ids"] == [
        "adaptive-facet",
        "adaptive-primary",
        "embedding-1",
        "embedding-2",
        "graph-1",
        "graph-2",
        "graph-3",
    ]
    assert coverage["gates"]["limits_passed"] is True
    assert all(row["returned"] <= 2 for row in coverage["graph_queries"])
    assert all(row["returned"] <= 2 for row in coverage["embedding_queries"])


def test_coverage_brief_pages_the_complete_union_with_closed_stable_rows(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def binding(claim_id: str, number: int) -> dict[str, Any]:
        text = f"Reviewed authoritative statement {number} for {claim_id}."
        return {
            "record_id": claim_id,
            "paper_id": f"2500.0000{number}v1",
            "authoritative_text": text,
            "authoritative_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "citation_pages": [number],
            "review_state": "reviewed",
        }

    bindings = [binding(f"claim-{letter}", number) for number, letter in enumerate("abcdefg", 1)]
    snapshot = _snapshot()
    snapshot.adaptive.answer_bindings = bindings

    def candidate(claim_id: str, rank: int, *, primary: bool = False) -> dict[str, Any]:
        return {"record_id" if primary else "claim_id": claim_id, "rank": rank}

    coverage = {
        "query": "full question",
        "algorithm": runtime.COVERAGE_ALGORITHM_ID,
        "unique_candidate_claims": 7,
        "union_claim_ids": [f"claim-{letter}" for letter in "abcdefg"],
        "adaptive": {
            "primary": {
                "ranked_bindings": [
                    candidate("claim-a", 1, primary=True),
                    candidate("claim-b", 2, primary=True),
                    candidate("claim-c", 3, primary=True),
                ]
            },
            "coverage_facets": [
                {
                    "facet": "facet one",
                    "candidates": [candidate("claim-d", 1), candidate("claim-e", 2)],
                }
            ],
        },
        "graph_queries": [
            {
                "query_kind": "full",
                "facet": "full question",
                "candidates": [candidate("claim-b", 1), candidate("claim-f", 2)],
            },
            {
                "query_kind": "facet",
                "facet": "facet one",
                "candidates": [candidate("claim-d", 1), candidate("claim-g", 2)],
            },
        ],
        "embedding_queries": [
            {
                "query_kind": "full",
                "facet": "full question",
                "candidates": [candidate("claim-c", 1), candidate("claim-g", 2)],
            },
            {
                "query_kind": "facet",
                "facet": "facet one",
                "candidates": [candidate("claim-e", 1), candidate("claim-f", 2)],
            },
        ],
        "gates": {
            "maximum_graph_claims_per_facet": 2,
            "maximum_embedding_claims_per_facet": 2,
        },
        "snapshot": {
            "core_tree_sha256": "core-tree",
            "ensemble_index_sha256": "ensemble-index",
        },
    }
    calls = 0

    def full_pack(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return copy.deepcopy(coverage)

    monkeypatch.setattr(runtime, "build_coverage_pack", full_pack)
    pages = [
        runtime.build_coverage_brief(snapshot, "full question", 3, 2, 2, page, 2)
        for page in range(1, 5)
    ]

    assert calls == 4
    assert [row["pagination"]["page"] for row in pages] == [1, 2, 3, 4]
    assert all(row["pagination"]["total_pages"] == 4 for row in pages)
    assert all(row["full_coverage"]["sha256"] == pages[0]["full_coverage"]["sha256"] for row in pages)
    paged_claim_ids = [
        claim["claim_id"]
        for page in pages
        for claim in page["claims"]
    ]
    assert paged_claim_ids == [
        "claim-f",
        "claim-g",
        "claim-b",
        "claim-c",
        "claim-d",
        "claim-e",
        "claim-a",
    ]
    assert len(paged_claim_ids) == len(set(paged_claim_ids))
    assert pages[-1]["pagination"]["has_more"] is False
    assert pages[-1]["pagination"]["next_page"] is None
    assert pages[0]["facets"] == [{"facet_index": 1, "facet": "facet one"}]

    expected_top_keys = {
        "schema_version",
        "status",
        "authoritative",
        "discovery_only",
        "query",
        "algorithm",
        "parameters",
        "pagination",
        "facets",
        "routes",
        "claims",
        "counts",
        "full_coverage",
        "snapshot",
        "brief_contract",
    }
    for page in pages:
        assert set(page) == expected_top_keys
        page_claim_ids = {claim["claim_id"] for claim in page["claims"]}
        assert page["brief_contract"]["all_full_claims_paged"] is True
        assert all(
            set(claim)
            == {
                "claim_id",
                "paper_id",
                "authoritative_text",
                "authoritative_text_sha256",
                "citation_pages",
                "review_state",
                "provenance",
            }
            for claim in page["claims"]
        )
        assert all(claim["review_state"] == "reviewed" for claim in page["claims"])
        assert all(
            set(provenance) == {"query_kind", "facet_index", "route", "rank"}
            for claim in page["claims"]
            for provenance in claim["provenance"]
        )
        assert all(
            set(route)
            == {
                "query_kind",
                "facet_index",
                "facet",
                "route",
                "candidate_limit",
                "total_candidates",
                "page_candidates",
                "candidate_claim_ids",
            }
            for route in page["routes"]
        )
        assert all(
            route["total_candidates"] <= route["candidate_limit"]
            and route["page_candidates"] == len(route["candidate_claim_ids"])
            and set(route["candidate_claim_ids"]) <= page_claim_ids
            for route in page["routes"]
        )

    with pytest.raises(runtime.SnapshotError, match="exceeds total pages"):
        runtime.build_coverage_brief(snapshot, "full question", 3, 2, 2, 5, 2)


def test_facet_finalizer_requires_status_and_rebuilds_exact_evidence(
    runtime: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    coverage = {
        "maximum_facets": 2,
        "union_claim_ids": ["claim-1", "claim-2"],
    }
    monkeypatch.setattr(runtime, "build_coverage_pack", lambda *_args, **_kwargs: coverage)
    monkeypatch.setattr(
        runtime.adaptive_runtime,
        "decompose_coverage_facets",
        lambda *_args, **_kwargs: ["facet one", "facet two"],
    )
    captured: dict[str, Any] = {}

    def finalize(
        _snapshot: Any,
        _path: Any,
        question_id: str,
        minimum_words: int,
        maximum_words: int,
        *,
        draft_payload: str,
    ) -> dict[str, Any]:
        captured.update(
            {
                "question_id": question_id,
                "minimum_words": minimum_words,
                "maximum_words": maximum_words,
                "draft": json.loads(draft_payload),
            }
        )
        return {"status": "pass", "evidence_valid": True}

    monkeypatch.setattr(runtime.adaptive_runtime, "finalize_answer", finalize)
    draft = {
        "summary": "A concise grounded synthesis.",
        "facets": [
            {
                "facet": "facet one",
                "status": "supported",
                "statement": "The first facet is supported.",
                "supporting_claim_ids": ["claim-1"],
            },
            {
                "facet": "facet two",
                "status": "unresolved",
                "statement": "The available evidence does not resolve this facet.",
                "supporting_claim_ids": [],
            },
        ],
    }
    result = runtime.finalize_answer(
        _snapshot(),
        None,
        "hard-question",
        "full question",
        3,
        40,
        draft_payload=_canonical(draft),
    )
    assert result == {"status": "pass", "evidence_valid": True}
    assert captured["question_id"] == "hard-question"
    assert captured["draft"] == {
        "summary": draft["summary"],
        "claims": [
            {
                "statement": "The first facet is supported.",
                "supporting_claim_ids": ["claim-1"],
            }
        ],
    }

    outside_gate = copy.deepcopy(draft)
    outside_gate["facets"][0]["supporting_claim_ids"] = ["claim-outside-coverage"]
    with pytest.raises(runtime.SnapshotError, match="outside the gated coverage pack"):
        runtime.finalize_answer(
            _snapshot(),
            None,
            "hard-question",
            "full question",
            3,
            40,
            draft_payload=_canonical(outside_gate),
        )

    unresolved = copy.deepcopy(draft)
    unresolved["facets"][0].update(
        status="unresolved",
        supporting_claim_ids=[],
    )
    with pytest.raises(runtime.SnapshotError, match="cannot mark every facet unresolved"):
        runtime.finalize_answer(
            _snapshot(),
            None,
            "hard-question",
            "full question",
            3,
            40,
            draft_payload=_canonical(unresolved),
        )


@pytest.mark.parametrize("root", [BUILD_ROOT, CONSULT_ROOT])
def test_standalone_runtime_smoke_without_pythonpath(root: Path) -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "runtime_smoke.py")],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "pass"
    assert payload["runtime"].startswith("semantic-okf-ensemble-")


def test_q031_coverage_brief_cli_is_compact_complete_parseable_and_deterministic() -> None:
    runtime_python = Path(
        os.environ.get(
            "SEMANTIC_OKF_PYTHON",
            str(REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
        )
    )
    if not FINAL_BUNDLE.is_dir() or not runtime_python.is_file():
        pytest.skip("the generated final bundle and exact semantic runtime are required")

    program = r"""
import contextlib
import io
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
query = sys.argv[2]
sys.path.insert(0, str(root / "skills/consult-semantic-okf-ensemble/scripts"))
from query_semantic_okf_ensemble import main

def run(page):
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main([
            str(root / "evaluations/semantic-okf-ensemble/results/runs/20260715-ensemble-final-03/workspace-a/knowledge"),
            "coverage-brief",
            "--query",
            query,
            "--page",
            str(page),
        ])
    if code != 0:
        raise RuntimeError(f"coverage-brief page {page} failed with exit {code}")
    raw = stdout.getvalue()
    return raw, json.loads(raw)

first_raw, first = run(1)
pages = [(first_raw, first)]
for number in range(2, first["pagination"]["total_pages"] + 1):
    pages.append(run(number))
repeat_raw, repeat = run(1)
claim_ids = [claim["claim_id"] for _, page in pages for claim in page["claims"]]
print(json.dumps({
    "deterministic": first_raw == repeat_raw and first == repeat,
    "page_sizes": [len(raw.encode("utf-8")) for raw, _ in pages],
    "total_pages": first["pagination"]["total_pages"],
    "total_claims": first["pagination"]["total_claims"],
    "seen_claims": len(claim_ids),
    "unique_seen_claims": len(set(claim_ids)),
    "priority_order": first["full_coverage"]["priority_order"],
    "priority_order_hashes": sorted({
        page["full_coverage"]["priority_order_sha256"] for _, page in pages
    }),
    "q031_core_in_first_page": {
        "claim-2402-07630v3-039",
        "claim-2503-13804v1-037",
        "claim-2503-13804v1-038",
        "claim-2506-05690v3-043",
        "claim-2506-05690v3-044",
    } <= {claim["claim_id"] for claim in first["claims"]},
    "facet_count": len(first["facets"]),
    "coverage_hashes": sorted({page["full_coverage"]["sha256"] for _, page in pages}),
    "all_full_claims_paged": all(
        page["brief_contract"]["all_full_claims_paged"] for _, page in pages
    ),
}, sort_keys=True))
"""
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["HF_HUB_OFFLINE"] = "1"
    environment["TRANSFORMERS_OFFLINE"] = "1"
    environment["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    governed_cache = environment.get("SEMANTIC_OKF_HF_HUB_CACHE")
    if governed_cache:
        environment["HF_HUB_CACHE"] = governed_cache
    completed = subprocess.run(
        [str(runtime_python), "-c", program, str(REPO_ROOT), Q031_QUERY],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        encoding="utf-8",
        timeout=240,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result == {
        "all_full_claims_paged": True,
        "coverage_hashes": [result["coverage_hashes"][0]],
        "deterministic": True,
        "facet_count": 8,
        "priority_order": "persisted-idf-facet-consensus-priority-v1",
        "priority_order_hashes": [result["priority_order_hashes"][0]],
        "q031_core_in_first_page": True,
        "page_sizes": result["page_sizes"],
        "seen_claims": 206,
        "total_claims": 206,
        "total_pages": 5,
        "unique_seen_claims": 206,
    }
    assert result["coverage_hashes"][0] == "881dec7d573003631c7ee5bb6c55ba4568393df1f911c26dbaa7bfa5c0619ac7"
    assert max(result["page_sizes"]) < 50 * 1024


def test_consult_skill_resolves_overlay_cli_without_global_filesystem_scan() -> None:
    skill = (CONSULT_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "skills/consult-semantic-okf-ensemble/scripts/run_query.ps1" in skill
    assert "Do not run `find /`" in skill
    assert "searches outside the current workspace" in skill
    assert "& $QueryCommand $Bundle" in skill
    assert "SEMANTIC_OKF_PYTHON" in skill
    assert "SEMANTIC_OKF_HF_HUB_CACHE" in skill
