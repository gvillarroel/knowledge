from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-tantivy"
REPORT_PATH = EVALUATION_ROOT / "reports" / "trace-distillation-20260722.json"
QUERY_IDF_REPORT_PATH = (
    EVALUATION_ROOT
    / "reports"
    / "trace-distillation-query-idf-20260723.json"
)
BUILDER_TRACE_REPORT_PATH = (
    EVALUATION_ROOT
    / "reports"
    / "trace-distillation-builder-forward-four-20260723.json"
)
ROUND3_TRACE_REPORT_PATH = (
    EVALUATION_ROOT
    / "reports"
    / "trace-distillation-round3-endocrine-20260723.json"
)
PREPARER_PATH = EVALUATION_ROOT / "scripts" / "prepare_trace_distillation.py"
CANONICAL_EVALUATOR_PATH = (
    EVALUATION_ROOT / "scripts" / "evaluate_canonical_retrieval.py"
)
CANONICAL_SUMMARIZER_PATH = (
    EVALUATION_ROOT / "scripts" / "summarize_canonical_retrieval.py"
)
CANONICAL_SUMMARY_PATH = EVALUATION_ROOT / "canonical-retrieval-summary.json"
BUILDER_GENERATOR_PATH = (
    EVALUATION_ROOT / "scripts" / "generate_builder_evolution_tasks.py"
)
ASTRO_QUERY_GENERATOR_PATH = (
    EVALUATION_ROOT / "scripts" / "generate_astro_evolution_tasks.py"
)
ASTRO_BUILDER_GENERATOR_PATH = (
    EVALUATION_ROOT / "scripts" / "generate_astro_builder_evolution_tasks.py"
)
ENDOCRINE_QUERY_GENERATOR_PATH = (
    EVALUATION_ROOT / "scripts" / "generate_endocrine_evolution_tasks.py"
)
ENDOCRINE_BUILDER_GENERATOR_PATH = (
    EVALUATION_ROOT / "scripts" / "generate_endocrine_builder_evolution_tasks.py"
)
CONSULT_FREEZE_PATH = EVALUATION_ROOT / "consult-freeze-20260723.json"
BUILDER_FREEZE_PATH = EVALUATION_ROOT / "builder-freeze-20260723.json"
GENERAL_RETRIEVAL_TABLE = (
    REPO_ROOT / "evaluations" / "semantic-okf-ensemble" / "EVALUATION-CONCLUSIONS.md"
)
LIVE_SKILL = REPO_ROOT / "skills" / "consult-semantic-okf-tantivy"


def load_preparer():
    spec = importlib.util.spec_from_file_location(
        "test_tantivy_trace_distillation_preparer", PREPARER_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_canonical_evaluator():
    spec = importlib.util.spec_from_file_location(
        "test_tantivy_canonical_evaluator", CANONICAL_EVALUATOR_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_canonical_summarizer():
    spec = importlib.util.spec_from_file_location(
        "test_tantivy_canonical_summarizer", CANONICAL_SUMMARIZER_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_builder_generator():
    scripts = str(EVALUATION_ROOT / "scripts")
    sys.path.insert(0, scripts)
    try:
        spec = importlib.util.spec_from_file_location(
            "test_tantivy_builder_evolution_generator",
            BUILDER_GENERATOR_PATH,
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(scripts)


def load_evaluation_script(name: str, path: Path):
    scripts = str(EVALUATION_ROOT / "scripts")
    sys.path.insert(0, scripts)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(scripts)


def test_checked_report_preserves_strict_harbor_decision() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert report["status"] == "complete"
    assert report["final_candidate"]["label"] == "S"
    assert report["final_candidate"]["tree_sha256"] == (
        "sha256:745be487dc3b6e75a7fa2c28a1f786ffea0366c77853dd51070f2d0fd7155634"
    )
    assert report["development"]["decision"] == "pass"
    assert report["development"]["pass_rate"] == 1.0
    assert report["development"]["passed_trials"] == 4
    assert all(
        trial["evidence_contract_gate"] == 1.0
        and trial["mechanical_qualification_gate"] == 1.0
        for trial in report["development"]["trials"].values()
    )

    holdout = report["holdout"]
    assert holdout["decision"] == "keep-baseline"
    assert holdout["promoted"] is False
    assert holdout["baseline_qualified"] is False
    assert holdout["candidate_qualified"] is False
    assert holdout["mean_gain"] == 0.0
    assert holdout["trials"]["q029"]["candidate"]["evidence_contract_gate"] == 0.0
    assert report["decision"] == {
        "development": "pass",
        "holdout": "keep-baseline",
        "promoted": False,
        "checked_in_skill": "retain-unchanged",
        "canonical_registry": "unchanged",
    }


def test_query_idf_trace_report_retains_non_regressing_baseline() -> None:
    report = json.loads(QUERY_IDF_REPORT_PATH.read_text(encoding="utf-8"))

    assert report["status"] == "complete"
    assert report["development"]["decision"] == "pass"
    assert report["development"]["mean_gain"] > 0
    assert report["holdout"]["mean_gain"] > 0
    assert report["holdout"]["decision"] == "keep-baseline"
    assert report["holdout"]["promoted"] is False
    assert report["holdout"]["regressed_tasks"] == 1
    assert min(row["delta"] for row in report["holdout"]["per_task"]) < 0
    assert report["decision"]["checked_in_consult_skill"] == (
        "retain-identity-natural"
    )


def test_builder_trace_report_rejects_holdout_regression_and_replays_canonical(
) -> None:
    report = json.loads(BUILDER_TRACE_REPORT_PATH.read_text(encoding="utf-8"))

    assert report["status"] == "complete"
    assert report["development"]["decision"] == "pass"
    assert report["development"]["regressed_tasks"] == 0
    assert report["development"]["mean_gain"] > 0
    assert report["holdout"]["decision"] == "keep-baseline"
    assert report["holdout"]["promoted"] is False
    assert report["holdout"]["mean_gain"] < 0
    assert report["holdout"]["regressed_tasks"] == 2
    assert report["decision"]["checked_in_builder_skill"] == (
        "retain-stable-dedicated-baseline"
    )
    replay = report["canonical_replay"]
    assert replay["status"] == "pass"
    assert replay["rebuilds_byte_identical"] is True
    assert replay["rebuild_equals_frozen_bundle"] is True
    assert replay["canonical_metrics_unchanged"] is True
    assert replay["question_count"] == 40
    assert replay["queries_across_top10_replay_and_pool100"] == 120
    assert replay["evidence_validity"] == 1.0


def test_round3_trace_report_stops_after_both_candidates_are_rejected(
) -> None:
    report = json.loads(ROUND3_TRACE_REPORT_PATH.read_text(encoding="utf-8"))

    assert report["status"] == "pass"
    assert report["dataset"]["cohorts_disjoint"] is True
    assert report["query"]["decision"] == "keep-baseline"
    assert report["query"]["development"]["gain"] > 0
    assert report["query"]["holdout"]["gain"] > 0
    assert report["query"]["holdout"]["regressed_cells"] == 1
    assert report["query"]["excluded_discovery_attempt"]["used_as_evidence"] is False

    builder = report["builder"]
    assert builder["decision"] == "keep-baseline-after-canonical-regression"
    assert builder["development"]["gain"] > 0
    assert builder["holdout"]["gain"] > 0
    assert builder["holdout"]["regressed_cells"] == 0
    canonical = builder["canonical_gate"]
    assert canonical["two_builds_byte_identical"] is True
    assert canonical["ranked_top10_replay_identical"] is True
    assert canonical["pool100_top10_prefix_identical"] is True
    assert canonical["evidence_validity"] == 1.0
    assert canonical["candidate_hard_10"]["recall_at_10"] < (
        canonical["retained_hard_10"]["recall_at_10"]
    )

    assert report["decision"] == {
        "query_promoted": False,
        "builder_promoted": False,
        "complete_round_promoted_anything": False,
        "stopping_criterion_met": True,
        "checked_in_consult_skill": "retain-unchanged",
        "checked_in_builder_skill": "retain-unchanged",
        "canonical_table": "retain-unchanged",
    }


def test_evolution_record_is_complete_redacted_and_not_promoted() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    markdown = REPORT_PATH.with_suffix(".md").read_text(encoding="utf-8")
    readme = (EVALUATION_ROOT / "README.md").read_text(encoding="utf-8")
    adr = (
        REPO_ROOT
        / ".specs"
        / "adr"
        / "0046-reject-tantivy-consult-trace-distillation-candidate.md"
    ).read_text(encoding="utf-8")

    assert "auth.json" not in report + markdown
    assert "/home/" not in report + markdown
    assert "promoted: false" in markdown + readme + adr
    assert "no evolved candidate was copied" in readme
    assert "Do not promote candidate S" in adr
    assert (LIVE_SKILL / "SKILL.md").is_file()
    assert not (LIVE_SKILL / "scripts" / "finalize_bounded_answer.py").exists()

    expected_iterations = tuple("efghijklmnopqrs")
    for iteration in expected_iterations:
        assert (EVALUATION_ROOT / f"proposals-20260722-{iteration}.yaml").is_file()
        config = EVALUATION_ROOT / f"trace-distillation-20260722-{iteration}.json"
        assert config.is_file()
        payload = json.loads(config.read_text(encoding="utf-8"))
        assert payload["schemaVersion"] == 2


def test_final_proposals_are_trace_supported_and_bounded() -> None:
    payload = yaml.safe_load(
        (EVALUATION_ROOT / "proposals-20260722-s.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert len(payload["proposals"]) == 3
    for proposal in payload["proposals"]:
        assert len(set(proposal["evidenceIds"])) >= 2
        assert proposal["target"] in {
            "SKILL.md",
            "scripts/finalize_bounded_answer.py",
        }
    contents = "\n".join(str(row.get("content", "")) for row in payload["proposals"])
    normalized_contents = " ".join(contents.split())
    assert "MAX_SEMANTIC_TEXT_CHARS = 1600" in contents
    assert "indent=0" in contents
    assert "Never bypass a second finalizer error" in normalized_contents


def test_preparer_helpers_preserve_isolation_and_zero_retry_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_preparer()
    repo = tmp_path / "repo"
    canonical = repo / "canonical"
    snapshot = repo / "snapshot"
    skill = repo / "skill"
    source = canonical / "discovery" / "q001"
    source.mkdir(parents=True)
    (source / "task.toml").write_text(
        'name = "fixture__classical__q001"\nfamily = "classical"\n'
        'tags = ["classical",]\n',
        encoding="utf-8",
    )
    (source / "instruction.md").write_text(
        "Use consult-semantic-okf-classical for this consult-only question.\n",
        encoding="utf-8",
    )
    (source / "__pycache__").mkdir()
    (source / "__pycache__" / "ignored.pyc").write_bytes(b"ignored")
    (canonical / "manifest.json").write_text("{}\n", encoding="utf-8")
    (snapshot / "semantic").mkdir(parents=True)
    (snapshot / "classical").mkdir()
    (snapshot / "semantic" / "records.jsonl").write_text("{}\n", encoding="utf-8")
    (snapshot / "classical" / "index.json").write_text("{}\n", encoding="utf-8")
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Fixture\n", encoding="utf-8")

    monkeypatch.setattr(module, "REPO", repo)
    monkeypatch.setattr(module, "CANONICAL_TASKS", canonical)
    monkeypatch.setattr(module, "SNAPSHOT", snapshot)
    monkeypatch.setattr(module, "SKILL", skill)
    module.require_inputs("/tmp/redacted-auth")
    with pytest.raises(ValueError, match="absolute Linux path"):
        module.require_inputs("relative-auth")

    destination = tmp_path / "generated" / "q001"
    record = module.copy_task("q001", destination)
    assert len(record["source_tree_sha256"]) == 64
    assert len(record["generated_tree_sha256"]) == 64
    assert "tantivy-consult-distillation" in (
        destination / "task.toml"
    ).read_text(encoding="utf-8")
    assert "consult-semantic-okf-tantivy" in (
        destination / "instruction.md"
    ).read_text(encoding="utf-8")
    assert not list(destination.rglob("*.pyc"))

    config = module.job_config(
        name="fixture",
        jobs_dir="/tmp/jobs",
        task_root="/tmp/tasks",
        task_ids=("q001",),
        snapshot="/tmp/snapshot",
        skill="/tmp/skill",
        auth_directory="/tmp/redacted-auth",
    )
    assert config["retry"]["max_retries"] == 0
    assert config["n_attempts"] == 1
    assert config["environment"]["mounts"][0]["read_only"] is True
    assert config["environment"]["mounts"][0]["target"] == "/knowledge"
    assert config["agents"][0]["model_name"] == "openai-codex/gpt-5.6-luna"


def test_canonical_evaluator_adapts_natural_questions_without_qrel_expansion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evaluator = load_canonical_evaluator()
    observed: dict[str, object] = {}

    class Runtime:
        @staticmethod
        def search_snapshot(snapshot, query: str, top_k: int):
            observed.update(snapshot=snapshot, query=query, top_k=top_k)
            return {"results": []}

    monkeypatch.setattr(
        evaluator.BASE,
        "parse_search_output",
        lambda payload, top_k: [payload, top_k],
    )

    normalized = evaluator.tantivy_hits(
        Runtime,
        object(),
        "How should a model's evidence be ranked?",
        10,
    )

    assert observed["query"] == "How should a model s evidence be ranked"
    assert observed["top_k"] == 10
    assert normalized[1] == 10


def test_checked_canonical_tantivy_summary_and_general_table() -> None:
    report = json.loads(CANONICAL_SUMMARY_PATH.read_text(encoding="utf-8"))

    assert report["status"] == "pass"
    assert report["question_count"] == 40
    assert report["route"] == "tantivy_bm25"
    assert report["candidate_state"] == (
        "experimental-comparator-not-registry-family"
    )
    assert report["determinism"] == {
        "status": "pass",
        "question_count": 40,
        "ranked_top10_identical": True,
        "pool100_top10_prefix_identical": True,
    }
    assert report["top10"]["error_count"] == 0
    assert report["top10"]["evidence_validity"] == 1.0
    assert report["top10"]["route_evidence_rows"] == 400
    assert report["pool100"]["route_evidence_rows"] == 527
    assert report["top10"]["all_40"]["recall_at_10"] == pytest.approx(
        0.8074089105
    )
    assert report["top10"]["hard_10"]["recall_at_10"] == pytest.approx(
        0.9216666667
    )
    assert report["tantivy_minus_classical"]["all_40"][
        "recall_at_10"
    ] == pytest.approx(0.3102101405)

    table = GENERAL_RETRIEVAL_TABLE.read_text(encoding="utf-8")
    assert "| Tantivy dedicated pair (experimental) | `tantivy_bm25` |" in table
    assert "| `tantivy_bm25` | 80.74% | 93.75% | 81.05% |" in table
    assert "do not add either candidate to the canonical eight-family Harbor registry" in table

    markdown = CANONICAL_SUMMARY_PATH.with_suffix(".md").read_text(encoding="utf-8")
    assert "400/400 valid evidence rows" in markdown
    assert "527/527 valid evidence rows" in markdown
    assert "Tantivy materially improves retrieval coverage and nDCG" in markdown


def test_staged_freeze_receipts_bind_query_and_builder_decisions() -> None:
    consult = json.loads(CONSULT_FREEZE_PATH.read_text(encoding="utf-8"))
    builder = json.loads(BUILDER_FREEZE_PATH.read_text(encoding="utf-8"))

    assert consult["selected_candidate"] == "identity-natural"
    assert consult["holdout"]["promoted"] is True
    assert consult["holdout"]["regressed_tasks"] == 0
    query_trace = consult["trace_distillation_holdout"]
    assert query_trace["candidate"] == "idf-boosted-natural-query"
    assert query_trace["holdout_gain"] > 0
    assert query_trace["holdout_regressed_tasks"] == 1
    assert query_trace["promoted"] is False
    assert query_trace["decision"] == "retain-identity-natural"
    assert builder["selected_candidate"] == "stable-dedicated-baseline"
    assert builder["frozen_consult"]["realizer_sha256"] == (
        consult["source_tree"]["realizer_sha256"]
    )
    assert builder["frozen_consult"]["unchanged_during_builder_evolution"] is True
    assert builder["baseline_parity"]["authoritative_core_file_count"] == 884
    assert builder["baseline_parity"]["authoritative_core_differing_files"] == 0
    assert builder["baseline_parity"]["projection_byte_differing_files"] == 6
    assert (
        builder["baseline_parity"]["newline_normalized_data_artifacts_equal"] == 4
    )
    assert builder["holdout"]["promoted"] is False
    assert builder["holdout"]["gain"] < 0
    assert builder["holdout"]["decision"] == "retain-stable-dedicated-baseline"
    trace = builder["trace_distillation_holdout"]
    assert trace["candidate"] == "forward-four"
    assert trace["development_regressed_tasks"] == 0
    assert trace["holdout_gain"] < 0
    assert trace["holdout_regressed_tasks"] == 2
    assert trace["promoted"] is False
    assert trace["decision"] == "retain-stable-dedicated-baseline"


def test_builder_evolution_tasks_embed_and_lock_the_frozen_consult() -> None:
    generator = load_builder_generator()
    files = generator.expected_files(
        REPO_ROOT / "evaluations" / "semantic-okf-adaptive" / "retrieval-questions.jsonl",
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-datasets"
        / "datasets"
        / "graphrag-papers-40-cohorts.json",
    )
    manifest = json.loads(files["manifest.json"])

    assert manifest["status"] == "pass"
    assert manifest["frozen_consult_tree_sha256"] == (
        "sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7"
    )
    phases = [task["phase"] for task in manifest["tasks"]]
    assert phases.count("development") == 6
    assert phases.count("holdout") == 4
    assert all(len(task["question_ids"]) == 4 for task in manifest["tasks"])
    assert len(
        {
            question
            for task in manifest["tasks"]
            for question in task["question_ids"]
        }
    ) == 40
    for task in manifest["tasks"]:
        task_root = task["task"]
        lock = json.loads(files[f"{task_root}/solution/consult-lock.json"])
        assert lock["tree_sha256"] == manifest["frozen_consult_tree_sha256"]
        assert lock["files"]
        for relative, expected in lock["files"].items():
            payload = files[f"{task_root}/solution/frozen-consult/{relative}"]
            assert __import__("hashlib").sha256(payload).hexdigest() == expected


def test_astro_query_evolution_tasks_use_source_identity_and_prospective_dev(
) -> None:
    generator = load_evaluation_script(
        "test_tantivy_astro_query_evolution_generator",
        ASTRO_QUERY_GENERATOR_PATH,
    )
    files = generator.expected_files(
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-astro"
        / "benchmark"
        / "retrieval-questions.jsonl",
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-datasets"
        / "datasets"
        / "astro-40-cohorts.json",
        "train",
        "dev",
    )
    manifest = json.loads(files["manifest.json"])

    assert manifest["status"] == "pass"
    assert manifest["dataset_id"] == "astro-40"
    assert manifest["identity_field"] == "source_id"
    assert manifest["cohort_mapping"] == {
        "development": "train",
        "holdout": "dev",
    }
    phases = [task["phase"] for task in manifest["tasks"]]
    assert phases.count("development") == 6
    assert phases.count("holdout") == 2
    qrels = json.loads(files["development/part-01/tests/qrels.json"])
    assert qrels["identity_field"] == "source_id"
    assert qrels["questions"][0]["identity_ids"]
    score = files["development/part-01/tests/score.py"].decode("utf-8")
    assert 'hit.get("source_id")' in score
    assert 'truth["identity_ids"]' in score
    assert 'hit.get("paper_id")' not in score


def test_astro_builder_tasks_lock_the_explicit_consult_and_reserve_holdout(
) -> None:
    generator = load_evaluation_script(
        "test_tantivy_astro_builder_evolution_generator",
        ASTRO_BUILDER_GENERATOR_PATH,
    )
    digest = "sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7"
    files = generator.expected_files(
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-astro"
        / "benchmark"
        / "retrieval-questions.jsonl",
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-datasets"
        / "datasets"
        / "astro-40-cohorts.json",
        "train",
        "holdout",
        LIVE_SKILL,
        digest,
    )
    manifest = json.loads(files["manifest.json"])

    assert manifest["status"] == "pass"
    assert manifest["frozen_consult_tree_sha256"] == digest
    assert manifest["cohort_mapping"] == {
        "development": "train",
        "holdout": "holdout",
    }
    phases = [task["phase"] for task in manifest["tasks"]]
    assert phases.count("development") == 6
    assert phases.count("holdout") == 2
    for task in manifest["tasks"]:
        task_root = task["task"]
        lock = json.loads(files[f"{task_root}/solution/consult-lock.json"])
        assert lock["tree_sha256"] == digest
        assert lock["files"]


def test_endocrine_query_tasks_separate_development_and_query_holdout(
) -> None:
    generator = load_evaluation_script(
        "test_tantivy_endocrine_query_evolution_generator",
        ENDOCRINE_QUERY_GENERATOR_PATH,
    )
    files = generator.expected_files(
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-endocrine-hygiene"
        / "benchmark"
        / "retrieval-questions.jsonl",
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-endocrine-hygiene"
        / "benchmark"
        / "evolution-cohorts.json",
        "development",
        "query-holdout",
    )
    manifest = json.loads(files["manifest.json"])

    assert manifest["dataset_id"] == "endocrine-hygiene-30"
    assert manifest["identity_field"] == "source_id"
    assert manifest["cohort_mapping"] == {
        "development": "development",
        "holdout": "query-holdout",
    }
    phases = [task["phase"] for task in manifest["tasks"]]
    assert phases.count("development") == 5
    assert phases.count("holdout") == 2
    development = {
        question
        for task in manifest["tasks"]
        if task["phase"] == "development"
        for question in task["question_ids"]
    }
    holdout = {
        question
        for task in manifest["tasks"]
        if task["phase"] == "holdout"
        for question in task["question_ids"]
    }
    assert len(development) == 20
    assert len(holdout) == 5
    assert development.isdisjoint(holdout)
    qrels = json.loads(files["development/part-01/tests/qrels.json"])
    assert qrels["identity_field"] == "source_id"
    assert qrels["questions"][0]["identity_ids"]


def test_endocrine_builder_tasks_freeze_consult_and_reserve_hard_holdout(
) -> None:
    generator = load_evaluation_script(
        "test_tantivy_endocrine_builder_evolution_generator",
        ENDOCRINE_BUILDER_GENERATOR_PATH,
    )
    digest = (
        "sha256:896d038b16dd974411ef50bf91e5efead5e2589262058114b4bed4d8993f0c84"
    )
    files = generator.expected_files(
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-endocrine-hygiene"
        / "benchmark"
        / "retrieval-questions.jsonl",
        REPO_ROOT
        / "evaluations"
        / "semantic-okf-endocrine-hygiene"
        / "benchmark"
        / "evolution-cohorts.json",
        "development",
        "builder-holdout",
        LIVE_SKILL,
        digest,
    )
    manifest = json.loads(files["manifest.json"])

    assert manifest["frozen_consult_tree_sha256"] == digest
    assert manifest["cohort_mapping"] == {
        "development": "development",
        "holdout": "builder-holdout",
    }
    phases = [task["phase"] for task in manifest["tasks"]]
    assert phases.count("development") == 5
    assert phases.count("holdout") == 2
    hard_ids = [
        question
        for task in manifest["tasks"]
        if task["phase"] == "holdout"
        for question in task["question_ids"]
    ]
    assert hard_ids == ["q026", "q027", "q028", "q029", "q030"]
    for task in manifest["tasks"]:
        task_root = task["task"]
        lock = json.loads(files[f"{task_root}/solution/consult-lock.json"])
        assert lock["tree_sha256"] == digest
        assert lock["files"]


def test_canonical_summarizer_rejects_incomplete_run() -> None:
    summarizer = load_canonical_summarizer()

    with pytest.raises(summarizer.SummaryError, match="invalid or incomplete"):
        summarizer.require_run({}, 10)
