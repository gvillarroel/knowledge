"""Focused tests for the executable Astro build, retrieval, and answer harness."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
EVALUATION = REPO / "evaluations" / "semantic-okf-astro"


def load_script(name: str, filename: str):
    """Load one evaluation script through its real file boundary."""

    path = EVALUATION / "scripts" / filename
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a small deterministic JSONL fixture."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_build_harness_binds_the_frozen_416_document_input() -> None:
    """The runner must discover exactly the checked acquisition set and all plans."""

    runtime = load_script("astro_build_harness_test", "run_builds.py")
    report = runtime.validate_inputs(EVALUATION / "corpus" / "manifest.json")
    assert report["corpus"]["source_count"] == 416
    assert report["corpus"]["input_file_count"] == 416
    assert report["corpus"]["input_bytes"] == 2_944_859
    assert len(report["plans"]) == 5
    assert {family.name for family in runtime.FAMILIES} == {
        "legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble"
    }


def test_retrieval_harness_uses_only_explicit_source_record_identity() -> None:
    """The evaluator joins all 416 records without filename or title inference."""

    runtime = load_script("astro_retrieval_identity_test", "evaluate_retrieval.py")
    identity, documents = runtime.load_identity_map(EVALUATION / "corpus" / "source-combination.json")
    questions = runtime.load_questions(EVALUATION / "benchmark" / "retrieval-questions.jsonl", documents)
    assert len(identity) == len(documents) == 416
    assert len(questions) == 40
    assert sum(question.cohort == "hard" for question in questions) == 10
    assert all(identity[(row["source_id"], row["record_id"])] == row["document_id"] for row in documents.values())


def test_ledger_reconstructs_whole_record_and_character_range(tmp_path: Path) -> None:
    """Evidence validation must reject altered retained text while accepting exact slices."""

    runtime = load_script("astro_retrieval_ledger_test", "evaluate_retrieval.py")
    body = "Alpha section.\n\nBeta section."
    record = {
        "source_id": "source-a",
        "record_id": "record-a",
        "record_sha256": "a" * 64,
        "concept_id": "concepts/source-a/record-a",
        "concept_path": "concepts/source-a/record-a.md",
        "source_path": "sources/a.mdx",
        "body": body,
        "title": "A",
    }
    write_jsonl(tmp_path / "semantic" / "records.jsonl", [record])
    ledger = runtime.Ledger(tmp_path, {("source-a", "record-a"): "/en/a/"})
    start, end = body.index("Beta"), len(body)
    exact = runtime.Hit(
        source_id="source-a", record_id="record-a", document_id=None, record_sha256=None,
        concept_id=record["concept_id"], concept_path=record["concept_path"],
        source_path=record["source_path"],
        locator={"target": "record-body", "kind": "character-range", "start": start, "end": end, "fragment": "f"},
        text=body[start:end], text_sha256=runtime.sha256_bytes(body[start:end].encode()),
        score=1.0, retrieval_id="section-a",
    )
    bound = ledger.bind(exact)
    assert ledger.validate(bound) == {"valid": True, "issues": []}
    altered = runtime.replace(bound, text="Beta section?", text_sha256=runtime.sha256_bytes(b"Beta section?"))
    assert ledger.validate(altered)["valid"] is False


def test_ranking_and_family_selection_prioritize_hard_recall() -> None:
    """The frozen route selector must prefer hard coverage over an easier aggregate tie-break."""

    runtime = load_script("astro_retrieval_metrics_test", "evaluate_retrieval.py")
    metrics = runtime.ranking_metrics(["b", "a", "c"], {"a", "c"})
    assert metrics["recall_at_1"] == 0.0
    assert metrics["recall_at_3"] == 1.0
    assert metrics["mrr_at_10"] == 0.5

    def route(name: str, hard: float, ndcg: float) -> dict[str, object]:
        base = {f"recall_at_{cutoff}": 0.0 for cutoff in runtime.METRIC_CUTOFFS}
        base.update({"mrr_at_10": 0.2, "ndcg_at_10": ndcg})
        hard_metrics = dict(base, recall_at_10=hard)
        return {
            "family": "legacy", "route": name, "status": "pass",
            "overall": {"document_metrics": base, "evidence_validity": {"ratio": 1.0}},
            "hard": {"document_metrics": hard_metrics},
        }

    routes = [route("aggregate", 0.4, 0.9), route("hard", 0.8, 0.1)]
    for family, names in runtime.FAMILY_ROUTES.items():
        if family != "legacy":
            routes.extend(
                {
                    **route(names[0], 0.0, 0.0),
                    "family": family,
                }
                for _ in [0]
            )
    selected = runtime.best_families(routes)
    assert next(row for row in selected if row["family"] == "legacy")["best_route"] == "hard"


def test_inspection_commands_place_deep_validation_on_the_supported_parser() -> None:
    """Global and subcommand deep-validation flags must use their actual CLI positions."""

    runtime = load_script("astro_retrieval_command_test", "evaluate_retrieval.py")
    bundle = Path("bundle")
    ensemble = runtime.inspect_command("python", "ensemble", bundle)
    classical = runtime.inspect_command("python", "classical", bundle)
    legacy = runtime.legacy_inspect_command("python", bundle)
    assert ensemble[-2:] == ["--deep-validation", "inspect"]
    assert classical[-2:] == ["inspect", "--deep-validation"]
    assert legacy[-5:] == ["ledger", "--all", "--validate", "--format", "json"]


def test_warm_runtime_loads_snapshot_once_and_rejects_route_or_fallback(
    monkeypatch,
) -> None:
    """Repeated route queries must reuse one snapshot and preserve exact routing."""

    runtime = load_script("astro_retrieval_warm_runtime_test", "evaluate_retrieval.py")
    calls: list[tuple[object, ...]] = []

    class FakeRuntime:
        @staticmethod
        def load_snapshot(bundle: Path, *, deep_validation: bool):
            calls.append(("load", bundle, deep_validation))
            return object()

        @staticmethod
        def search_snapshot(snapshot: object, query: str, route: str, top_k: int):
            calls.append(("search", snapshot, query, route, top_k))
            return {
                "status": "pass",
                "effective_mode": route,
                "fallback": None,
                "results": [],
            }

    monkeypatch.setattr(runtime, "_load_module", lambda *args, **kwargs: FakeRuntime)
    payload_search = runtime._load_warm_payload_searcher("classical", Path("bundle"))
    first = payload_search("bm25", "first query")
    second = payload_search("fusion", "second query")
    assert [call for call in calls if call[0] == "load"] == [
        ("load", Path("bundle"), True)
    ]
    assert first["effective_mode"] == "bm25"
    assert second["effective_mode"] == "fusion"
    runtime.validate_route_payload(first, "classical", "bm25")

    changed = dict(first, effective_mode="fusion")
    try:
        runtime.validate_route_payload(changed, "classical", "bm25")
    except runtime.EvaluationError:
        pass
    else:
        raise AssertionError("changed effective route was accepted")
    fallback = dict(first, fallback={"from": "bm25", "to": "fusion"})
    try:
        runtime.validate_route_payload(fallback, "classical", "bm25")
    except runtime.EvaluationError:
        pass
    else:
        raise AssertionError("declared fallback was accepted")


def test_family_routes_run_query_major_and_standalone_timing_is_separate(
    capsys,
) -> None:
    runtime = load_script(
        "astro_retrieval_query_major_test", "evaluate_retrieval.py"
    )
    questions = [
        runtime.Question("q1", "hard", "first query", ("/doc/",), ("source",)),
        runtime.Question("q2", "hard", "second query", ("/doc/",), ("source",)),
    ]
    calls: list[tuple[str, str]] = []

    def search(route: str):
        def run(query: str):
            calls.append((query, route))
            return [
                runtime.Hit(
                    source_id="source",
                    record_id="record",
                    document_id="/doc/",
                    record_sha256="a" * 64,
                    concept_id="concept",
                    concept_path="concept.md",
                    source_path="source.mdx",
                    locator=None,
                    text=None,
                    text_sha256=None,
                    score=1.0,
                    retrieval_id=f"{route}-{query}",
                )
            ]

        return run

    class ValidLedger:
        @staticmethod
        def validate(_hit):
            return {"valid": True, "issues": []}

    routes = ("one", "two")
    results = runtime.evaluate_family_routes(
        "fake",
        routes,
        questions,
        ValidLedger(),
        {route: search(route) for route in routes},
        "query-major test",
        progress=True,
    )
    assert calls == [
        ("first query", "one"),
        ("first query", "two"),
        ("second query", "one"),
        ("second query", "two"),
    ]
    assert [row["route"] for row in results] == list(routes)
    assert all(row["overall"]["document_metrics"]["recall_at_10"] == 1.0 for row in results)
    assert all(row["overall"]["evidence_validity"]["ratio"] == 1.0 for row in results)
    assert "fake: 2/2 questions" in capsys.readouterr().err

    calls.clear()
    timing = runtime.standalone_route_timing(
        "fake", "two", questions, search("two"), progress=True
    )
    assert calls == [("first query", "two"), ("second query", "two")]
    assert timing["status"] == "pass"
    assert timing["route"] == "two"
    assert "no sibling-route cache priming" in timing["execution"]


def test_embedding_model_setup_and_inference_warmup_precede_route_timing(
    monkeypatch,
) -> None:
    """The pinned model factory and its lazy first inference must run only at setup."""

    runtime = load_script("astro_retrieval_embedding_warmup_test", "evaluate_retrieval.py")
    calls: list[tuple[object, ...]] = []
    snapshot = type(
        "Snapshot",
        (),
        {"index": {"embedding": {"provider": "sentence-transformers"}}},
    )()

    class FakeRuntime:
        @staticmethod
        def load_snapshot(bundle: Path):
            calls.append(("load", bundle))
            return snapshot

        @staticmethod
        def search_snapshot(active_snapshot, query: str, **kwargs):
            calls.append(("search", active_snapshot, query, kwargs["embedder"]))
            return {
                "status": "pass",
                "effective_mode": kwargs["requested_mode"],
                "fallback": None,
                "results": [],
            }

    def provider(active_runtime, active_snapshot):
        calls.append(("provider", active_runtime, active_snapshot))

        def encode(text: str, config):
            calls.append(("encode", text, config))
            return [1.0]

        return encode

    monkeypatch.setattr(runtime, "_load_module", lambda *args, **kwargs: FakeRuntime)
    monkeypatch.setattr(runtime, "_cached_embedding_provider", provider)
    payload_search = runtime._load_warm_payload_searcher("embeddings", Path("bundle"))
    assert [call[0] for call in calls] == ["load", "provider", "encode"]
    assert calls[-1][1] == runtime.EMBEDDING_WARMUP_QUERY
    payload_search("vector", "timed query")
    assert [call[0] for call in calls].count("load") == 1
    assert [call[0] for call in calls].count("provider") == 1


def test_extractive_answer_generation_and_evidence_sufficiency_are_separate() -> None:
    """A valid grounded answer can still be incomplete against atomic evidence."""

    runtime = load_script("astro_answer_harness_test", "compare_hard_answers.py")
    text = "Use server output for request-time pages. Keep unrelated routes prerendered."
    hit = {
        "rank": 1,
        "document_id": "/en/a/",
        "source_id": "source-a",
        "record_id": "record-a",
        "concept_path": "concepts/a.md",
        "source_path": "sources/a.mdx",
        "record_sha256": "a" * 64,
        "locator": {"kind": "character-range", "start": 0, "end": len(text)},
        "text": text,
        "text_sha256": "b" * 64,
        "retrieval_id": "section-a",
        "evidence_validation": {"valid": True, "issues": []},
    }
    answer = runtime.make_answer("q", "How should routes render?", [hit], 4)
    assert answer["answer"] is not None
    assert answer["evidence"][0]["document_id"] == "/en/a/"
    truth = {
        "id": "q",
        "authoritative_evidence": [
            {"id": "e1", "document_id": "/en/a/", "start_char": 0, "end_char": 10},
            {"id": "e2", "document_id": "/en/b/", "start_char": 0, "end_char": 10},
        ],
        "ground_truth": {
            "required_document_ids": ["/en/a/", "/en/b/"],
            "answer_claims": [{"id": "a1", "evidence_ids": ["e1", "e2"]}],
            "important_negatives": [{"id": "n1", "evidence_ids": ["e2"]}],
        },
    }
    metrics = runtime.score_answer(truth, [hit], {"/en/a/": len(text), "/en/b/": 20})
    assert metrics["grounding"] == 1.0
    assert metrics["evidence_validity"] == 1.0
    assert metrics["required_document_coverage"] == 0.5
    assert metrics["atomic_claim_evidence_completeness"] == 0.0


def test_active_astro_harness_contains_no_mcp_runtime_dependency() -> None:
    """The active experiment may document retirement but cannot import or start MCP."""

    forbidden = ("import mcp", "from mcp", "fastmcp", "mcp_server", "mcp-server")
    for path in (
        EVALUATION / "scripts" / "run_builds.py",
        EVALUATION / "scripts" / "evaluate_retrieval.py",
        EVALUATION / "scripts" / "compare_hard_answers.py",
    ):
        source = path.read_text(encoding="utf-8").casefold()
        assert not any(token in source for token in forbidden)


def test_skill_arena_generator_is_pairwise_and_does_not_leak_qrels() -> None:
    """Each config must isolate one skill against a knowledge-identical control."""

    runtime = load_script("astro_skill_arena_generator_test", "generate_skill_arena_configs.py")
    payload = runtime.config(
        "ensemble",
        "evaluations/semantic-okf-astro/results/runs/example",
        {"id": "q040", "question": "How should the routes be configured?", "question_type": "hard"},
    )
    profiles = payload["comparison"]["profiles"]
    assert [row["id"] for row in profiles] == [
        "knowledge-only-control", "ensemble-consult-treatment"
    ]
    assert profiles[0]["capabilities"] == {}
    assert len(profiles[1]["capabilities"]["skills"]) == 1
    assert payload["comparison"]["variants"][0]["agent"]["model"] == "openai-codex/gpt-5.6-luna"
    rendered = json.dumps(payload).casefold()
    assert "qrels" not in rendered
    assert "mcp" not in rendered.replace("no-mcp", "")


def test_skill_arena_prompt_coverage_is_explicitly_diagnostic() -> None:
    """The one-case causal diagnostic must not masquerade as broad coverage."""

    runtime = load_script("astro_skill_arena_coverage_test", "generate_skill_arena_configs.py")
    coverage = runtime.prompt_coverage()
    assert coverage["policy"]["minimumPrompts"] == 1
    assert coverage["policy"]["minimumNaturalisticCases"] == 0
    assert coverage["cases"] == [
        {
            "promptId": "q040",
            "caseKind": "boundary-recovery",
            "taskFamily": "conditional-routing-synthesis",
        }
    ]
