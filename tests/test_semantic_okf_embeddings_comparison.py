from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-embeddings"
HISTORICAL_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper"
COMPARATOR = EVALUATION_ROOT / "scripts" / "compare_retrieval.py"
ORCHESTRATOR = EVALUATION_ROOT / "scripts" / "run_evaluation.py"
SUMMARIZER = EVALUATION_ROOT / "scripts" / "summarize_comparison_reports.py"
INVENTORY = EVALUATION_ROOT / "input-inventory.json"
QUESTIONS = EVALUATION_ROOT / "retrieval-questions.jsonl"
HISTORICAL_QUESTIONS = HISTORICAL_ROOT / "questions.jsonl"
COMPACT_SUMMARY = EVALUATION_ROOT / "comparison-summary.json"


def load_comparator() -> ModuleType:
    """Load the standalone comparison script without packaging it."""

    module_name = "semantic_okf_embeddings_comparison"
    spec = importlib.util.spec_from_file_location(module_name, COMPARATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_orchestrator() -> ModuleType:
    """Load the standalone append-only evaluation orchestrator."""

    module_name = "semantic_okf_embeddings_orchestrator"
    spec = importlib.util.spec_from_file_location(module_name, ORCHESTRATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_summarizer() -> ModuleType:
    """Load the compact-report summarizer without packaging it."""

    module_name = "semantic_okf_embeddings_summary"
    spec = importlib.util.spec_from_file_location(module_name, SUMMARIZER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read a compact JSONL fixture."""

    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: object) -> None:
    """Write deterministic JSON for a temporary bundle fixture."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _comparison_fixture(top_k: int) -> dict[str, object]:
    questions = [f"q{index:03d}" for index in range(1, 31)]
    routes = []
    for name in ("legacy_lexical", "new_lexical", "vector", "hybrid"):
        routes.append(
            {
                "name": name,
                "query_count": 30,
                "error_count": 0,
                "errors": [],
                "setup_ms": 0.0,
                "timing_scope": "fixture",
                "timing_ms": {"mean": 1.0, "p95": 1.0},
                "paper_metrics": {"recall_at_10": 1.0},
                "source_metrics": {"recall_at_10": 1.0},
                "evidence_validity": {"ratio": 1.0},
                "queries": [
                    {
                        "question_id": question_id,
                        "elapsed_ms": 1.0,
                        "error": None,
                        "hit_count": 1,
                        "hits": [{"large": "payload"}],
                        "paper_ids": ["paper-a"],
                        "source_ids": ["source-a"],
                        "paper_metrics": {"recall_at_10": 1.0},
                        "source_metrics": {"recall_at_10": 1.0},
                        "evidence_validity": {"ratio": 1.0},
                    }
                    for question_id in questions
                ],
            }
        )
    return {
        "schema_version": "1.2",
        "top_k": top_k,
        "routes": routes,
        "inputs": {"questions": {"sha256": "a" * 64}},
        "bundles": {"legacy": {}, "new": {}},
        "core_semantic_parity": {
            "status": "pass",
            "authoritative_file_set": {"equal": True},
            "logical_core_tree_equal": True,
            "key_artifacts_equal": True,
        },
        "metric_contract": {"primary_identity": "paper_id"},
        "evidence_contract": {"exact_bindings": True},
        "timing_methodology": {"scope": "fixture"},
    }


def test_compact_summary_preserves_metrics_and_drops_hit_payloads(tmp_path: Path) -> None:
    summarizer = load_summarizer()
    primary = tmp_path / "primary.json"
    diagnostic = tmp_path / "diagnostic.json"
    write_json(primary, _comparison_fixture(100))
    write_json(diagnostic, _comparison_fixture(10))

    summary = summarizer.summarize(primary, diagnostic)

    assert summary["status"] == "pass"
    assert summary["gates"]["all_retained_evidence_valid"] is True
    assert summary["cohorts"]["primary_identity_collapsed"]["query_count"] == 30
    query = summary["cohorts"]["primary_identity_collapsed"]["routes"][0]["queries"][0]
    assert query["paper_ids"] == ["paper-a"]
    assert "hits" not in query
    assert summary["source_reports"]["primary"]["sha256"] == summarizer.sha256(primary)


def test_checked_compact_summary_retains_the_accepted_result_contract() -> None:
    summary = json.loads(COMPACT_SUMMARY.read_text(encoding="utf-8"))

    assert summary["schema_version"] == "semantic-okf-embeddings-comparison-summary/1.0"
    assert summary["status"] == "pass"
    assert all(summary["gates"].values())
    assert summary["source_reports"]["primary"]["sha256"] == (
        "8dc000d04568753d18b0c744b25b269001d9b3ff2eb986c03c0670192c988d23"
    )
    assert summary["source_reports"]["diagnostic"]["sha256"] == (
        "08a83e45c8596743170c7ccb05015019c3cc0d00b7167f8432ba2c76fd07114c"
    )
    primary = summary["cohorts"]["primary_identity_collapsed"]
    assert primary["query_count"] == 30
    assert len(primary["question_ids"]) == len(set(primary["question_ids"])) == 30
    assert [route["name"] for route in primary["routes"]] == [
        "legacy_lexical",
        "new_lexical",
        "vector",
        "hybrid",
    ]
    expected_recall = {
        "legacy_lexical": 0.7885954785954786,
        "new_lexical": 0.7813323713323713,
        "vector": 0.7392147667147667,
        "hybrid": 0.7728270803270803,
    }
    for route in primary["routes"]:
        assert route["query_count"] == 30
        assert route["error_count"] == 0
        assert route["evidence_validity"]["ratio"] == 1.0
        assert route["paper_metrics"]["recall_at_10"] == pytest.approx(
            expected_recall[route["name"]]
        )
        assert all("hits" not in query for query in route["queries"])


def test_input_inventory_freezes_exact_historical_core() -> None:
    comparator = load_comparator()
    inventory = comparator.load_inventory(INVENTORY)
    entries = inventory["files"]

    assert len(entries) == inventory["core_file_count"] == 30
    assert sum(entry["bytes"] for entry in entries) == inventory["core_total_bytes"] == 1_845_945
    assert sum(entry["rows"] for entry in entries) == inventory["core_record_count"] == 846
    assert {entry["kind"] for entry in entries} == {"markdown", "jsonl"}
    assert sum(entry["kind"] == "markdown" for entry in entries) == 15
    assert sum(entry["kind"] == "jsonl" for entry in entries) == 15

    verification = comparator.verify_input_inventory(HISTORICAL_ROOT, inventory)
    assert verification == {
        "status": "pass",
        "expected_core_files": 30,
        "verified_core_files": 30,
        "expected_core_tree_sha256": "25945882b73ca659230c8b8c66a58fa8418313f8a0233f57e85b0e48445f4328",
        "actual_core_tree_sha256": "25945882b73ca659230c8b8c66a58fa8418313f8a0233f57e85b0e48445f4328",
        "errors": [],
    }
    auxiliary = inventory["required_auxiliary"]
    assert auxiliary["real_build_input_count"] == 31
    assert auxiliary["real_build_record_count"] == 874
    assert auxiliary["real_build_inputs_tree_sha256"] == (
        "ab14c14f6471086a320f75350def889ba91f2bbd3b040f81fa4797814ce689ab"
    )
    assert auxiliary["manifest"]["sha256"] == (
        "a4e83ce7d9630bf57ce4b3c2bf2cb445e34032c3ec46673b4bbed585885b0c37"
    )


def test_retrieval_qrels_are_derived_from_the_historical_questions() -> None:
    historical = read_jsonl(HISTORICAL_QUESTIONS)
    retrieval = read_jsonl(QUESTIONS)

    assert len(historical) == len(retrieval) == 30
    for original, derived in zip(historical, retrieval, strict=True):
        paper_ids = original["focus_papers"]
        suffixes = [paper_id.replace(".", "-", 1) for paper_id in paper_ids]
        expected_sources = sorted(
            [f"claims-{suffix}" for suffix in suffixes]
            + [f"paper-{suffix}" for suffix in suffixes]
        )
        assert derived == {
            "id": original["id"],
            "question": original["question"],
            "qrels": {
                "paper_ids": paper_ids,
                "source_ids": expected_sources,
            },
        }


def test_ranking_metrics_deduplicate_identifiers() -> None:
    comparator = load_comparator()
    ranking = ["p1", "miss", "p2", "p1"]
    relevant = {"p1", "p2", "p3"}

    metrics = comparator.evaluate_ranking(ranking, relevant)

    assert metrics["recall_at_1"] == pytest.approx(1 / 3)
    assert metrics["recall_at_3"] == pytest.approx(2 / 3)
    assert metrics["recall_at_5"] == pytest.approx(2 / 3)
    assert metrics["recall_at_10"] == pytest.approx(2 / 3)
    assert metrics["mrr_at_10"] == 1.0
    expected_dcg = 1.0 + 1.0 / math.log2(4)
    ideal_dcg = 1.0 + 1.0 / math.log2(3) + 1.0 / math.log2(4)
    assert metrics["ndcg_at_10"] == pytest.approx(expected_dcg / ideal_dcg)


def test_comparator_runs_four_routes_and_writes_explicit_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    comparator = load_comparator()
    inventory_path = tmp_path / "input-inventory.json"
    questions_path = tmp_path / "retrieval-questions.jsonl"
    legacy_bundle = tmp_path / "legacy"
    new_bundle = tmp_path / "new"
    consult_script = tmp_path / "query_semantic_okf_embeddings.py"
    output_json = tmp_path / "reports" / "comparison.json"
    output_markdown = tmp_path / "reports" / "comparison.md"
    source_path = "sources/markdown/2402.07630v3.md"
    auxiliary_path = "sources/semantic/analysis-vocabulary.jsonl"
    source_id = "paper-2402-07630v3"
    concept_path = "concepts/paper-2402-07630v3/relevant.md"
    concept_id = "concepts/paper-2402-07630v3/relevant"
    record_id = "relevant"
    body = "Graph evidence is retrieved for grounded answers."
    source_record_path = source_path

    write_json(
        inventory_path,
        {
            "files": [{"path": source_path}],
            "required_auxiliary": {"file": {"path": auxiliary_path}},
        },
    )
    questions_path.write_text(
        json.dumps(
            {
                "id": "q001",
                "question": "How is graph evidence retrieved?",
                "qrels": {
                    "paper_ids": ["2402.07630v3"],
                    "source_ids": [source_id],
                },
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = {"sources": [{"path": source_path}, {"path": auxiliary_path}]}
    ledger = (
        json.dumps(
                {
                    "source_id": source_id,
                    "record_id": record_id,
                    "record_sha256": "a" * 64,
                    "concept_id": concept_id,
                    "concept_path": concept_path,
                    "source_path": source_record_path,
                    "title": "Graph evidence retrieval",
                    "body": body,
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    for bundle in (legacy_bundle, new_bundle):
        write_json(bundle / "semantic" / "source-manifest.json", manifest)
        (bundle / "semantic" / "records.jsonl").write_text(ledger, encoding="utf-8")
        for relative in (
            "semantic/ontology.ttl",
            "semantic/data.ttl",
            "semantic/shapes.ttl",
            "semantic/provenance.ttl",
            "semantic/validation-report.ttl",
        ):
            artifact = bundle / relative
            artifact.write_text(f"# {relative}\n", encoding="utf-8")
        concept = bundle / concept_path
        concept.parent.mkdir(parents=True, exist_ok=True)
        concept.write_text("# Relevant graph evidence\n", encoding="utf-8")
    for relative in (
        "retrieval/index.json",
        "retrieval/chunks.jsonl",
        "retrieval/embeddings.jsonl",
        "retrieval/build-report.json",
    ):
        artifact = new_bundle / relative
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(f"{{\"fixture\":\"{relative}\"}}\n", encoding="utf-8")
    consult_script.write_text(
        """#!/usr/bin/env python3
import argparse
import hashlib
import json

parser = argparse.ArgumentParser()
parser.add_argument("bundle")
parser.add_argument("command", choices=("search",))
parser.add_argument("--query", required=True)
parser.add_argument("--mode", choices=("lexical", "vector", "hybrid"), required=True)
parser.add_argument("--top-k", type=int, required=True)
args = parser.parse_args()
text = "Graph evidence is retrieved for grounded answers."
print(json.dumps({
    "status": "pass",
    "requested_mode": args.mode,
    "hits": [{
        "source_id": "paper-2402-07630v3",
        "chunk_id": "chunk-example",
        "ordinal": 0,
        "record_id": "relevant",
        "record_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "concept_id": "concepts/paper-2402-07630v3/relevant",
        "concept_path": "concepts/paper-2402-07630v3/relevant.md",
        "source_path": "sources/markdown/2402.07630v3.md",
        "locator": {"kind": "character-range", "start": 0, "end": len(text)},
        "text": text,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "scores": {args.mode: 1.0},
    }],
}))
""",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    exit_code = comparator.main(
        [
            "--inventory",
            str(inventory_path),
            "--questions",
            str(questions_path),
            "--legacy-bundle",
            str(legacy_bundle),
            "--new-bundle",
            str(new_bundle),
            "--consult-script",
            str(consult_script),
            "--python-executable",
            sys.executable,
            "--top-k",
            "10",
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(output_markdown),
        ]
    )

    assert exit_code == 0
    report = json.loads(output_json.read_text(encoding="utf-8"))
    assert report["consult_command_contract"].endswith("--top-k K")
    assert [route["name"] for route in report["routes"]] == [
        "legacy_lexical",
        "new_lexical",
        "vector",
        "hybrid",
    ]
    assert all(route["paper_metrics"]["recall_at_1"] == 1.0 for route in report["routes"])
    assert report["schema_version"] == "1.2"
    assert all(route["evidence_validity"]["ratio"] == 1.0 for route in report["routes"])
    assert all(route["evidence_validity"]["ledger"]["record_count"] == 1 for route in report["routes"])
    retained = report["routes"][1]["queries"][0]["hits"][0]
    assert retained["concept_id"] == concept_id
    assert retained["chunk_id"] == "chunk-example"
    assert retained["ordinal"] == 0
    assert retained["record_id"] == record_id
    assert retained["source_path"] == source_record_path
    assert retained["locator"] == {"kind": "character-range", "start": 0, "end": len(body)}
    assert "text" not in retained
    assert retained["text_sha256"] == comparator.sha256_bytes(body.encode("utf-8"))
    assert retained["text_bytes"] == len(body.encode("utf-8"))
    assert retained["text_characters"] == len(body)
    assert retained["evidence_validation"] == {"valid": True, "issues": []}
    assert report["bundles"]["legacy"]["input_coverage"]["covered"] == 1
    assert report["bundles"]["new"]["input_coverage"]["required_auxiliary_declared"] is True
    assert set(report["bundles"]["new"]["fingerprint"]["key_artifacts"]) >= {
        "retrieval/index.json",
        "retrieval/chunks.jsonl",
        "retrieval/embeddings.jsonl",
        "retrieval/build-report.json",
    }
    parity = report["core_semantic_parity"]
    assert parity["status"] == "pass"
    assert parity["authoritative_file_set"]["equal"] is True
    assert parity["logical_core_tree_equal"] is True
    assert parity["key_artifacts_equal"] is True
    assert report["timing_methodology"]["legacy_lexical"]["execution_model"].startswith("single")
    assert report["timing_methodology"]["new_routes"]["execution_model"].startswith("one fresh")
    assert report["bundles"]["legacy"]["path"] == "legacy"
    assert report["bundles"]["new"]["path"] == "new"
    assert not Path(report["inputs"]["inventory"]["path"]).is_absolute()
    assert report["inputs"]["comparator_script"]["sha256"] == comparator.sha256_file(COMPARATOR)
    assert all(
        not Path(report["inputs"][name]["path"]).is_absolute()
        for name in ("inventory", "questions", "consult_script", "comparator_script")
    )
    markdown = output_markdown.read_text(encoding="utf-8")
    assert markdown.startswith("# Semantic OKF Embedding Retrieval Comparison\n")
    assert "## Timing methodology" in markdown
    assert "## Core semantic parity" in markdown
    assert "Evidence validity" in markdown


def test_evidence_validation_rejects_tampered_text_and_locator(tmp_path: Path) -> None:
    comparator = load_comparator()
    bundle = tmp_path / "bundle"
    body = "0123456789"
    record = {
        "source_id": "paper-2402-07630v3",
        "record_id": "record-1",
        "record_sha256": "b" * 64,
        "concept_id": "concepts/paper-2402-07630v3/record-1",
        "concept_path": "concepts/paper-2402-07630v3/record-1.md",
        "source_path": "sources/markdown/2402.07630v3.md",
        "body": body,
    }
    ledger_path = bundle / "semantic" / "records.jsonl"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    concept_path = bundle / record["concept_path"]
    concept_path.parent.mkdir(parents=True)
    concept_path.write_text("# Record\n", encoding="utf-8")
    ledger = comparator.AuthoritativeLedger.from_bundle(bundle)
    hit = comparator.RetrievalHit(
        source_id=record["source_id"],
        paper_id="2402.07630v3",
        chunk_id="chunk-example",
        ordinal=0,
        concept_path=record["concept_path"],
        concept_id=record["concept_id"],
        record_id=record["record_id"],
        record_sha256=record["record_sha256"],
        source_path=record["source_path"],
        locator={"kind": "character-range", "start": 2, "end": 5},
        text="tampered",
        text_sha256="0" * 64,
        score=1.0,
    )

    validation = comparator._validate_hit_evidence(bundle, ledger, hit)

    assert validation["valid"] is False
    assert {issue["code"] for issue in validation["issues"]} == {
        "text-sha256",
        "character-range-text",
    }

    emitted = comparator._hit_report(hit, validation, rank=1)
    assert "text" not in emitted
    assert emitted["text_sha256"] == "0" * 64
    assert emitted["text_bytes"] == len("tampered".encode("utf-8"))
    assert emitted["text_characters"] == len("tampered")


def test_orchestrator_dry_run_is_portable_and_refuses_overwrite(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    orchestrator = load_orchestrator()
    run_root = tmp_path / "runs"
    arguments = [
        "--repo-root",
        str(REPO_ROOT),
        "--python-executable",
        sys.executable,
        "--run-root",
        str(run_root),
        "--run-id",
        "fixed-audit",
        "--dry-run",
    ]

    assert orchestrator.main(arguments) == 0
    manifest_path = run_root / "fixed-audit" / "run-manifest.json"
    before = manifest_path.read_bytes()
    manifest = json.loads(before)
    assert manifest["status"] == "planned"
    assert manifest["run_directory"] == "$RUN"
    assert manifest["model"]["revision"] == "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    assert {item["name"] for item in manifest["planned_commands"]} >= {
        "build-embedding-a",
        "build-embedding-b",
        "validate-embedding-a",
        "validate-embedding-b",
        "compare-top-k-10",
        "compare-top-k-100",
    }
    assert all(item["sha256"] for item in manifest["requirements"])
    assert all(tool["path"].startswith("$REPO/") for tool in manifest["tools"].values())
    assert all(
        not Path(value).is_absolute()
        for command in manifest["planned_commands"]
        for value in command["argv"]
        if value not in {"$PYTHON"} and not value.startswith("--")
    )

    assert orchestrator.main(arguments) == 2
    assert manifest_path.read_bytes() == before
    assert "refusing to overwrite existing run directory" in capsys.readouterr().err
