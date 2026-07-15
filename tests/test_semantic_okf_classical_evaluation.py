from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-classical"
EMBEDDING_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-embeddings"
GENERATOR = EVALUATION_ROOT / "scripts" / "generate_hard_questions.py"
VALIDATOR = EVALUATION_ROOT / "scripts" / "validate_hard_ground_truth.py"
CONFIG_GENERATOR = EVALUATION_ROOT / "scripts" / "generate_skill_arena_configs.py"
RUN_PREPARER = EVALUATION_ROOT / "scripts" / "prepare_evaluation_run.py"
ANSWER_REVIEWER = EVALUATION_ROOT / "scripts" / "review_grounded_answers.py"
ANSWER_EVALUATOR = EVALUATION_ROOT / "scripts" / "evaluate_grounded_answers.py"
RETRY_MERGER = EVALUATION_ROOT / "scripts" / "merge_skill_arena_retries.py"
GROUNDED_SUMMARY = EVALUATION_ROOT / "grounded-answer-summary.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_classical_plan_selects_exact_frozen_core_and_excludes_auxiliary() -> None:
    inventory = json.loads((EMBEDDING_ROOT / "input-inventory.json").read_text(encoding="utf-8"))
    plan = json.loads((EVALUATION_ROOT / "classical-plan.json").read_text(encoding="utf-8"))
    paper_ids = sorted({entry["paper_id"] for entry in inventory["files"]})
    suffixes = [paper_id.replace(".", "-", 1) for paper_id in paper_ids]
    expected_sources = sorted(
        [f"claims-{suffix}" for suffix in suffixes]
        + [f"paper-{suffix}" for suffix in suffixes]
    )

    assert len(inventory["files"]) == 30
    assert len(paper_ids) == 15
    assert plan["selection"]["source_ids"] == expected_sources
    assert "analysis-vocabulary" not in plan["selection"]["source_ids"]
    assert inventory["required_auxiliary"]["real_build_input_count"] == 31
    assert inventory["required_auxiliary"]["real_build_record_count"] == 874
    assert plan["reranking"]["max_per_evidence_identity"] == 1
    assert plan["topics"]["topic_count"] == 16
    assert plan["associations"]["max_vocabulary"] == 3000


def test_hard_question_generation_is_current_and_independent_validation_passes() -> None:
    generated = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    validated = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert generated.returncode == 0, generated.stdout + generated.stderr
    assert "deterministic and current" in generated.stdout
    assert validated.returncode == 0, validated.stdout + validated.stderr
    assert "every authoritative claim line and paper-page hash" in validated.stdout


def test_expanded_benchmark_retains_original_thirty_then_adds_ten() -> None:
    baseline = read_jsonl(EMBEDDING_ROOT / "retrieval-questions.jsonl")
    hard = read_jsonl(EVALUATION_ROOT / "hard-questions.jsonl")
    expanded = read_jsonl(EVALUATION_ROOT / "retrieval-questions.jsonl")

    assert len(baseline) == 30
    assert len(hard) == 10
    assert expanded[:30] == baseline
    assert expanded[30:] == hard
    assert [record["id"].split("-", 1)[0] for record in hard] == [
        f"q{number:03d}" for number in range(31, 41)
    ]
    assert all(set(record) == {"id", "question", "qrels"} for record in hard)
    assert len({record["question"] for record in expanded}) == 40


def test_ground_truth_is_compact_atomic_and_requires_multi_paper_reasoning() -> None:
    records = read_jsonl(EVALUATION_ROOT / "hard-ground-truth.jsonl")

    assert len(records) == 10
    for record in records:
        ground_truth = record["ground_truth"]
        evidence = record["authoritative_evidence"]
        assert len(ground_truth["answer_claims"]) >= 3
        assert len(ground_truth["required_paper_ids"]) >= 3
        assert len({step["operation"] for step in ground_truth["derivation"]}) >= 2
        assert ground_truth["important_negatives"]
        assert ground_truth["acceptable_variants"]
        assert {item["paper_id"] for item in evidence} == set(
            ground_truth["required_paper_ids"]
        )
        for item in evidence:
            assert item["review_state"] == "reviewed"
            assert len(item["interpretation_sha256"]) == 64
            assert set(item["claim_source"]) == {
                "path",
                "line_number",
                "char_start",
                "char_end",
                "record_sha256",
            }
            for page in item["paper_evidence"]:
                assert set(page) == {
                    "path",
                    "locator",
                    "char_start",
                    "char_end",
                    "text_length",
                    "text_sha256",
                }
                assert page["locator"].startswith("PDF-page-")
                assert page["char_end"] - page["char_start"] == page["text_length"]
                assert len(page["text_sha256"]) == 64
                assert "text" not in page


def test_independent_validator_rejects_changed_claim_and_page_hashes() -> None:
    module = load_module("test_hard_ground_truth_validator", VALIDATOR)
    record = read_jsonl(EVALUATION_ROOT / "hard-ground-truth.jsonl")[0]
    changed_claim = copy.deepcopy(record)
    changed_claim["authoritative_evidence"][0]["claim_source"]["record_sha256"] = "0" * 64
    changed_page = copy.deepcopy(record)
    changed_page["authoritative_evidence"][0]["paper_evidence"][0]["text_sha256"] = "f" * 64

    with pytest.raises(module.ValidationError, match="claim source locator or hash mismatch"):
        module.validate_ground_truth_record(REPO_ROOT, changed_claim)
    with pytest.raises(module.ValidationError, match="paper locator, offsets, or text hash mismatch"):
        module.validate_ground_truth_record(REPO_ROOT, changed_page)


def test_generator_rejects_a_question_that_no_longer_joins_three_papers() -> None:
    generator = load_module("test_hard_question_generator", GENERATOR)
    inventory_path = EMBEDDING_ROOT / "input-inventory.json"
    inventory, corpus_root = generator.validate_inventory(REPO_ROOT, inventory_path)
    claims = generator.build_claim_index(REPO_ROOT, corpus_root, inventory)
    blueprint = json.loads((EVALUATION_ROOT / "hard-question-evidence.json").read_text(encoding="utf-8"))
    broken = copy.deepcopy(blueprint)
    first = broken["questions"][0]
    first["evidence_claim_ids"] = [
        "claim-2506-05690v3-043",
        "claim-2506-05690v3-044",
        "claim-2506-05690v3-033",
    ]

    with pytest.raises(generator.GenerationError, match="at least three papers"):
        generator.validate_blueprint(broken, claims)


def test_manifest_hashes_bind_blueprint_questions_and_ground_truth() -> None:
    manifest = json.loads(
        (EVALUATION_ROOT / "hard-ground-truth-manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["schema_version"] == "semantic-okf-hard-ground-truth-manifest/1.0"
    assert manifest["inputs"]["baseline_questions"]["count"] == 30
    assert manifest["inputs"]["corpus_inventory"]["core_file_count"] == 30
    assert set(manifest["outputs"]) == {
        "hard-ground-truth.jsonl",
        "hard-questions.jsonl",
        "retrieval-questions.jsonl",
    }
    assert manifest["outputs"]["retrieval-questions.jsonl"]["count"] == 40
    assert manifest["contracts"]["question_prompt"].endswith("never exposed")


def test_skill_arena_configs_are_deterministic_paired_and_do_not_leak_answers(
    tmp_path: Path,
) -> None:
    output = tmp_path / "skill-arena"
    bundle = (
        REPO_ROOT
        / "evaluations"
        / "graphrag-cross-paper"
        / "fixtures"
        / "workspaces"
        / "skill-overlay"
        / "knowledge"
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(CONFIG_GENERATOR),
            "--ground-truth",
            str(EVALUATION_ROOT / "hard-ground-truth.jsonl"),
            "--bundle",
            str(bundle),
            "--output-dir",
            str(output),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    ground_truth = read_jsonl(EVALUATION_ROOT / "hard-ground-truth.jsonl")
    answer_statements = {
        item["statement"]
        for question in ground_truth
        for item in (
            question["ground_truth"]["answer_claims"]
            + question["ground_truth"]["important_negatives"]
        )
    }
    for method in ("legacy", "embedding", "classical"):
        generated = (output / f"{method}-hard10.yaml").read_text(encoding="utf-8")
        checked = (EVALUATION_ROOT / "skill-arena" / f"{method}-hard10.yaml").read_text(
            encoding="utf-8"
        )
        assert generated == checked
        assert "TODO" not in generated
        assert "knowledge-only-control" in generated
        assert f"{method}-consult-treatment" in generated
        assert all(statement not in generated.split("workspace:", 1)[0] for statement in answer_statements)

    coverage = json.loads((output / "prompt-coverage.json").read_text(encoding="utf-8"))
    assert len(coverage["cases"]) == 10
    assert {case["caseKind"] for case in coverage["cases"]} == {
        "naturalistic-forward",
        "generalization",
        "boundary-recovery",
    }
    assert len({case["taskFamily"] for case in coverage["cases"]}) == 9


def test_run_manifest_excludes_only_derived_indexes_and_requires_core_parity(
    tmp_path: Path,
) -> None:
    module = load_module("test_classical_run_preparer", RUN_PREPARER)
    run = tmp_path / "run-001"
    for method in ("legacy", "embedding", "classical"):
        bundle = run / "workspaces" / method / "knowledge"
        (bundle / "semantic").mkdir(parents=True)
        (bundle / "semantic" / "build-report.json").write_text(
            json.dumps({"status": "pass", "valid": True}) + "\n", encoding="utf-8"
        )
        (bundle / "semantic" / "records.jsonl").write_text(
            json.dumps({"source_id": "source", "record_id": "record"}) + "\n",
            encoding="utf-8",
        )
        (bundle / "index.md").write_text("authoritative\n", encoding="utf-8")

    legacy = run / "workspaces" / "legacy" / "knowledge"
    core_hash = module._logical_tree_sha256(legacy, module._relative_files(legacy))
    for method, directory in (("embedding", "retrieval"), ("classical", "classical")):
        derived = run / "workspaces" / method / "knowledge" / directory
        derived.mkdir()
        (derived / "index.json").write_text("{}\n", encoding="utf-8")
        (derived / "build-report.json").write_text(
            json.dumps(
                {
                    "status": "pass",
                    "valid": True,
                    "core": {"tree_sha256": core_hash},
                }
            )
            + "\n",
            encoding="utf-8",
        )

    manifest = module._manifest(run)

    assert manifest["parity"]["status"] == "pass"
    assert manifest["parity"]["logical_core_tree_sha256"] == core_hash
    assert manifest["bundles"]["legacy"]["fingerprint"]["file_count"] == 3
    assert manifest["bundles"]["embedding"]["fingerprint"]["file_count"] == 5
    assert manifest["bundles"]["classical"]["fingerprint"]["file_count"] == 5
    assert {
        value["fingerprint"]["logical_core_tree_sha256"]
        for value in manifest["bundles"].values()
    } == {core_hash}

    input_manifest = module._write_manifest(run)
    assert input_manifest.is_file()
    for relative in (
        "retrieval/top10/comparison.json",
        "retrieval/pool100/comparison.json",
        "skill-arena/legacy/promptfoo-results.json",
        "skill-arena/embedding/promptfoo-results.json",
        "skill-arena/classical/promptfoo-results.json",
        "skill-arena/reviews/reviews.json",
    ):
        path = run / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    external = tmp_path / "compact-summary.json"
    external.write_text("{}\n", encoding="utf-8")
    classical_index = run / "workspaces" / "classical" / "knowledge" / "index.md"
    classical_index.write_text("drifted\n", encoding="utf-8")
    with pytest.raises(ValueError, match="workspaces changed"):
        module._finalize(run, [])
    classical_index.write_text("authoritative\n", encoding="utf-8")
    final_manifest = module._finalize(run, [f"summary={external}"])
    final = json.loads(final_manifest.read_text(encoding="utf-8"))
    assert final["status"] == "pass"
    assert final["append_only"] is True
    assert final["external_artifacts"][0]["name"] == "summary"
    with pytest.raises(FileExistsError, match="run manifest already exists"):
        module._finalize(run, [])

    (run / "workspaces" / "classical" / "knowledge" / "index.md").write_text(
        "drifted\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="authoritative cores are not identical"):
        module._manifest(run)


def test_compact_retrieval_summary_covers_eight_routes_and_both_candidate_pools() -> None:
    summary = json.loads((EVALUATION_ROOT / "retrieval-summary.json").read_text(encoding="utf-8"))

    assert summary["schema_version"] == "semantic-okf-classical-retrieval-summary/1.0"
    assert summary["question_count"] == 40
    assert summary["cohorts"] == {"original_30": 30, "hard_10": 10}
    assert summary["route_order"] == [
        "legacy_lexical",
        "new_lexical",
        "vector",
        "hybrid",
        "classical_bm25",
        "classical_topic",
        "classical_association",
        "classical_fusion",
    ]
    for run in summary["runs"].values():
        assert run["query_count"] == 40
        assert run["core_semantic_parity"]["status"] == "pass"
        for route in run["routes"].values():
            assert route["error_count"] == 0
            assert route["evidence_validity"]["ratio"] == 1.0
            assert route["evidence_validity"]["invalid"] == 0

    routes = summary["runs"]["top10"]["routes"]
    fusion_hard = routes["classical_fusion"]["hard_10"]["paper"]["recall_at_10"]
    assert fusion_hard == pytest.approx(0.955)
    assert fusion_hard > max(
        routes[name]["hard_10"]["paper"]["recall_at_10"]
        for name in ("legacy_lexical", "new_lexical", "vector", "hybrid")
    )


def test_grounded_answer_evidence_validator_normalizes_real_agent_path_and_page_forms() -> None:
    evaluator = load_module("test_grounded_answer_evaluator", ANSWER_EVALUATOR)
    bundle = (
        REPO_ROOT
        / "evaluations"
        / "graphrag-cross-paper"
        / "fixtures"
        / "workspaces"
        / "skill-overlay"
        / "knowledge"
    )
    records, paper_records = evaluator._records(bundle)
    record = records["claim-2506-05690v3-043"]
    item = {
        "claim_id": "claim-2506-05690v3-043",
        "concept_path": f"knowledge/{record['concept_path']}",
        "paper_id": "2506.05690v3",
        "source_path": record["source_path"],
        "locators": [7, "PDF-page-8"],
    }

    valid, claim_id, pages = evaluator._score_evidence_item(
        item,
        bundle,
        records,
        paper_records,
        {"2506.05690v3": {7, 8}},
    )

    assert valid is True
    assert claim_id == "claim-2506-05690v3-043"
    assert pages == {7, 8}
    changed = copy.deepcopy(item)
    changed["concept_path"] = "knowledge/concepts/not-the-record.md"
    assert evaluator._score_evidence_item(
        changed, bundle, records, paper_records, {"2506.05690v3": {7, 8}}
    )[0] is False


def test_blinded_answer_review_contract_requires_every_candidate_and_ground_truth_id() -> None:
    reviewer = load_module("test_grounded_answer_reviewer", ANSWER_REVIEWER)
    task = {
        "answer_id": "opaque-answer",
        "candidate": {"claims": [{"statement": "claim", "supporting_claim_ids": ["c1"]}]},
        "ground_truth": {
            "answer_claims": [{"id": "a1"}],
            "important_negatives": [{"id": "n1"}],
        },
    }
    review = {
        "answer_id": "opaque-answer",
        "claim_fidelity": [{"index": 0, "score": 1}],
        "atomic_scores": {"a1": 0.5},
        "negative_scores": {"n1": 1},
        "note": "Faithful but partially complete.",
    }

    assert reviewer._validate_review(copy.deepcopy(review), task) == review
    broken = copy.deepcopy(review)
    broken["atomic_scores"] = {}
    with pytest.raises(ValueError, match="ground-truth IDs"):
        reviewer._validate_review(broken, task)

    assert reviewer._support_context({"answer": None}, {}) == []


def test_reviewer_resolves_powershell_launcher_from_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviewer = load_module("test_grounded_answer_reviewer_launcher", ANSWER_REVIEWER)
    launcher = tmp_path / "pi.ps1"
    launcher.write_text("Write-Output ok\n", encoding="utf-8")
    monkeypatch.setenv("PATH", str(tmp_path))

    assert reviewer._resolve_command("pi.ps1") == str(launcher.resolve())


def test_manual_query_verification_covers_all_modes_and_preserves_bundle() -> None:
    report = json.loads(
        (EVALUATION_ROOT / "manual-query-verification.json").read_text(encoding="utf-8")
    )

    assert report["schema_version"] == "semantic-okf-classical-manual-query-verification/1.0"
    assert report["status"] == "pass"
    assert report["case_count"] == 4
    assert report["bundle_unchanged"] is True
    assert report["bundle_tree_before"] == report["bundle_tree_after"]
    assert [item["mode"] for item in report["results"]] == [
        "bm25",
        "topic",
        "association",
        "fusion",
    ]
    assert all(item["all_evidence_paths_exist"] for item in report["results"])
    assert all(
        item["unique_paper_count"] == 5
        for item in report["results"]
        if item["mode"] != "bm25"
    )


def test_retry_merge_replaces_only_failed_matching_cells(tmp_path: Path) -> None:
    merger = load_module("test_skill_arena_retry_merger", RETRY_MERGER)

    def row(provider: str, question_id: str, output: bool) -> dict[str, object]:
        value: dict[str, object] = {
            "provider": {"id": provider},
            "vars": {
                "taskPrompt": f"Answer it. Set question_id to `{question_id}`. Return JSON."
            },
        }
        if output:
            value["response"] = {
                "output": json.dumps({"question_id": question_id, "answer": {}})
            }
        else:
            value["error"] = "timeout"
        return value

    primary_path = tmp_path / "primary.json"
    retry_path = tmp_path / "retry.json"
    primary_path.write_text(
        json.dumps(
            {
                "results": {
                    "results": [
                        row("control", "q031", True),
                        row("treatment", "q031", False),
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    retry_path.write_text(
        json.dumps(
            {
                "results": {
                    "results": [
                        row("control", "q031", True),
                        row("treatment", "q031", True),
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    merged, manifest = merger.merge(primary_path, [retry_path])

    rows = merged["results"]["results"]
    assert rows[0] == json.loads(primary_path.read_text(encoding="utf-8"))["results"]["results"][0]
    assert merger._usable(rows[1]) is True
    assert manifest["replacement_count"] == 1
    assert manifest["replacements"][0]["provider"] == "treatment"
    assert manifest["final_usable_row_count"] == 2


def test_retry_merge_fails_closed_when_a_cell_remains_unresolved(tmp_path: Path) -> None:
    merger = load_module("test_skill_arena_retry_merger_unresolved", RETRY_MERGER)
    prompt = "Set question_id to `q040`."
    failed = {"provider": {"id": "control"}, "vars": {"taskPrompt": prompt}, "error": "timeout"}
    primary = tmp_path / "primary.json"
    retry = tmp_path / "retry.json"
    primary.write_text(json.dumps({"results": {"results": [failed]}}), encoding="utf-8")
    retry.write_text(json.dumps({"results": {"results": [failed]}}), encoding="utf-8")

    with pytest.raises(ValueError, match="No successful retry"):
        merger.merge(primary, [retry])


def test_compact_grounded_answer_summary_separates_six_profiles_and_nine_metrics() -> None:
    summary = json.loads(GROUNDED_SUMMARY.read_text(encoding="utf-8"))

    assert summary["schema_version"] == "semantic-okf-grounded-answer-comparison/1.0"
    assert summary["question_count"] == 10
    assert summary["answer_count"] == 60
    assert summary["review"]["blinded"] is True
    assert summary["review"]["review_count"] == 60
    expected_profiles = {
        "legacy": {"knowledge-only-control", "legacy-consult-treatment"},
        "embedding": {"knowledge-only-control", "embedding-consult-treatment"},
        "classical": {"knowledge-only-control", "classical-consult-treatment"},
    }
    assert {
        method: set(profiles) for method, profiles in summary["aggregates"].items()
    } == expected_profiles
    for profiles in summary["aggregates"].values():
        for aggregate in profiles.values():
            assert aggregate["answer_count"] == 10
            assert set(aggregate["metrics"]) == set(summary["metric_contract"])
            assert all(0.0 <= value <= 1.0 for value in aggregate["metrics"].values())

    answers = summary["answers"]
    assert len(answers) == len({item["answer_id"] for item in answers}) == 60
    assert all("candidate" not in item and "output" not in item for item in answers)
    assert summary["paired_deltas"]["embedding"]["evidence_validity"] > 0
