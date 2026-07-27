from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-rust-mallet"
SUMMARY_PATH = EVALUATION_ROOT / "retrieval-summary.json"
PLAN_PATH = EVALUATION_ROOT / "rust-mallet-plan.json"
EVOLVED_CONSULT_ROOT = (
    REPO_ROOT / "skills" / "consult-semantic-okf-rust-mallet-evolved"
)
REFERENCE_DICTIONARY_MODULE = (
    EVOLVED_CONSULT_ROOT / "scripts" / "_reference_dictionary.py"
)
REFERENCE_CONTRACT_MODULE = (
    EVALUATION_ROOT / "evolution-assets" / "reference_contract.py"
)
EVOLUTION_PREPARER_MODULE = (
    EVALUATION_ROOT / "scripts" / "prepare_harbor_evolution.py"
)
BUILDER_EVOLUTION_PREPARER_MODULE = (
    EVALUATION_ROOT / "scripts" / "prepare_harbor_builder_evolution.py"
)
PRESERVING_PREPARE_PROPOSALS_MODULE = (
    EVALUATION_ROOT / "scripts" / "generate_preserving_prepare_proposals.py"
)
ONE_COMMAND_BUILDER_PROPOSALS_MODULE = (
    EVALUATION_ROOT / "scripts" / "generate_one_command_builder_proposals.py"
)
PRESERVING_PREPARE_HELPER_MODULE = (
    EVALUATION_ROOT
    / "evolution-assets"
    / "consult-preserving-prepare"
    / "prepare_reference_consult.py"
)
REFERENCE_PARITY_MODULE = (
    EVALUATION_ROOT / "scripts" / "compare_reference_retrieval.py"
)
CANONICAL_EVALUATOR_MODULE = (
    EVALUATION_ROOT / "scripts" / "evaluate_canonical_retrieval.py"
)
CANONICAL_RETRIEVAL_SUMMARY = (
    EVALUATION_ROOT / "canonical-retrieval-summary.json"
)
GENERAL_RETRIEVAL_TABLE = (
    REPO_ROOT / "evaluations" / "semantic-okf-ensemble" / "EVALUATION-CONCLUSIONS.md"
)
REFERENCE_EVOLUTION_SUMMARY = EVALUATION_ROOT / "reference-evolution-summary.json"
PRESERVING_PREPARE_SUMMARY = (
    EVALUATION_ROOT / "preserving-prepare-trace-distillation-summary.json"
)
LIVE_EVOLVED_BUILDER = REPO_ROOT / "skills" / "build-semantic-okf-rust-mallet-evolved"
BUILDER_CANDIDATE_ASSETS = EVALUATION_ROOT / "evolution-assets" / "builder"
ONE_COMMAND_BUILDER_ASSETS = (
    EVALUATION_ROOT / "evolution-assets" / "builder-one-command"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_summarizer():
    return load_module(
        "test_rust_mallet_summarizer",
        EVALUATION_ROOT / "scripts" / "summarize_retrieval.py",
    )


def load_builder_evolution_preparer(name: str):
    load_module("prepare_harbor_evolution", EVOLUTION_PREPARER_MODULE)
    return load_module(name, BUILDER_EVOLUTION_PREPARER_MODULE)


def sample_documents() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for number in (1, 2):
        rows.append(
            {
                "document_id": f"document-{number}",
                "source_id": f"source-{number}",
                "record_id": f"record-{number}",
                "concept_path": f"concepts/source-{number}/record-{number}.md",
                "source_path": f"sources/source-{number}.jsonl",
                "record_sha256": f"{number:064x}",
                "locator": {"kind": "record"},
                "text_sha256": f"{number + 10:064x}",
            }
        )
    return rows


def test_rust_mallet_plan_pins_the_complete_native_sampler() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    assert set(plan["topics"]) == {
        "topic_count",
        "max_iterations",
        "burn_in",
        "optimize_interval",
        "num_samples",
        "sample_interval",
        "alpha_sum",
        "beta",
        "random_seed",
        "min_document_frequency",
        "max_document_fraction",
        "top_terms",
    }
    assert plan["topics"]["random_seed"] == 42
    assert plan["topics"]["max_iterations"] == 250
    assert plan["topics"]["burn_in"] == 100


def test_checked_summary_preserves_validation_and_observed_regression() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    assert summary["schema_version"] == "semantic-okf-rust-mallet-retrieval-summary/1.0"
    assert summary["rust_mallet"] == {
        "repository": "https://github.com/mimno/RustMallet",
        "package": "pyrmallet",
        "version": "0.1.1",
        "algorithm": "pyrmallet-0.1.1-sparse-gibbs-lda-v1",
    }
    assert summary["determinism"] == {
        "status": "pass",
        "byte_identical": True,
        "file_count": 890,
        "tree_sha256": "7f42997c20cdec17f72aac1442fa8ee138e62199867a6ac3f5962e1143aa3569",
    }
    assert set(summary["runs"]) == {"top10", "pool100"}
    for run in summary["runs"].values():
        assert run["query_count"] == 40
        assert run["core_semantic_parity"] == "pass"
        assert run["evidence_validity"] == "pass"
        for comparison in run["comparisons"].values():
            assert comparison["rust_mallet"]["error_count"] == 0
            assert comparison["rust_mallet"]["evidence_validity"]["ratio"] == 1.0

    fusion = summary["runs"]["top10"]["comparisons"]["fusion"]
    assert fusion["rust_mallet_minus_classical"]["all_40"][
        "recall_at_10"
    ] == pytest.approx(-0.03176587)
    assert fusion["rust_mallet_minus_classical"]["hard_10"]["recall_at_10"] == -0.095
    assert (
        summary["runs"]["pool100"]["comparisons"]["fusion"][
            "rust_mallet_minus_classical"
        ]
        == fusion["rust_mallet_minus_classical"]
    )


def test_summarizer_rejects_incomplete_or_invalid_runs() -> None:
    module = load_summarizer()
    with pytest.raises(module.SummaryError, match="identity or question count"):
        module._assert_run({}, 10)

    invalid = {
        "schema_version": "1.4",
        "query_count": 40,
        "top_k": 10,
        "core_semantic_parity": {"status": "pass"},
        "inputs": {"raw_input_verification": {"status": "pass"}},
        "routes": [],
    }
    with pytest.raises(module.SummaryError, match="four expected routes"):
        module._assert_run(invalid, 10)


def test_evaluation_docs_do_not_claim_canonical_promotion() -> None:
    readme = (EVALUATION_ROOT / "README.md").read_text(encoding="utf-8")
    markdown = (EVALUATION_ROOT / "retrieval-summary.md").read_text(encoding="utf-8")

    assert "does not add a ninth family" in readme
    assert "Retain RustMallet as an experimental skill pair" in markdown
    assert "TODO" not in readme + markdown


def test_reference_dictionary_is_stable_and_bound_to_exact_evidence() -> None:
    module = load_module(
        "test_rust_mallet_reference_dictionary", REFERENCE_DICTIONARY_MODULE
    )
    documents = sample_documents()

    first = module.derive_reference_dictionary(documents)
    second = module.derive_reference_dictionary(deepcopy(documents))

    assert first == second
    assert first["reference_count"] == 2
    assert list(first["references"]) == sorted(first["references"])
    assert all(
        reference_id.startswith("ref-") and len(reference_id) == 28
        for reference_id in first["references"]
    )
    by_document = module.validate_reference_dictionary(first, documents)
    assert set(by_document) == {"document-1", "document-2"}

    tampered = deepcopy(first)
    reference_id = next(iter(tampered["references"]))
    tampered["references"][reference_id]["evidence"]["record_sha256"] = "f" * 64
    with pytest.raises(module.ReferenceDictionaryError, match="stale ID"):
        module.validate_reference_dictionary(tampered, documents)

    duplicate = deepcopy(documents)
    duplicate[1]["document_id"] = duplicate[0]["document_id"]
    with pytest.raises(module.ReferenceDictionaryError, match="duplicate document_id"):
        module.derive_reference_dictionary(duplicate)


def test_reference_contract_resolves_compact_rows_and_preserves_legacy(
    tmp_path: Path,
) -> None:
    dictionary_module = load_module(
        "test_rust_mallet_reference_dictionary_contract", REFERENCE_DICTIONARY_MODULE
    )
    contract_module = load_module(
        "test_rust_mallet_reference_contract", REFERENCE_CONTRACT_MODULE
    )
    dictionary = dictionary_module.derive_reference_dictionary(sample_documents())
    dictionary_path = tmp_path / "references.json"
    dictionary_path.write_text(
        json.dumps(dictionary, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reference_ids = list(dictionary["references"])
    compact = {
        "question_id": "q-test",
        "answer": {"summary": "Supported.", "claims": []},
        "evidence": [{"reference_id": value} for value in reference_ids],
    }

    materialized, count = contract_module.materialize_reference_evidence(
        compact, dictionary_path
    )

    assert count == 2
    assert compact["evidence"] == [
        {"reference_id": value} for value in reference_ids
    ]
    assert [list(row) for row in materialized["evidence"]] == [
        list(contract_module.EVIDENCE_KEYS),
        list(contract_module.EVIDENCE_KEYS),
    ]
    legacy, legacy_count = contract_module.materialize_reference_evidence(
        materialized, dictionary_path
    )
    assert legacy is materialized
    assert legacy_count == 0

    for evidence, error in (
        ([{"reference_id": "ref-000000000000000000000000"}], "unknown"),
        ([{"reference_id": reference_ids[0]}] * 2, "duplicate"),
        (
            [
                {"reference_id": reference_ids[0]},
                {"source_id": "mixed"},
            ],
            "mixed-or-invalid",
        ),
    ):
        invalid = deepcopy(compact)
        invalid["evidence"] = evidence
        with pytest.raises(ValueError, match=error):
            contract_module.materialize_reference_evidence(
                invalid, dictionary_path
            )


def test_evolution_task_seals_dictionary_for_the_verifier(
    tmp_path: Path,
) -> None:
    preparer = load_module(
        "test_rust_mallet_evolution_preparer", EVOLUTION_PREPARER_MODULE
    )
    dictionary_path = tmp_path / "references.json"
    dictionary_path.write_text("{\"sealed\":true}\n", encoding="utf-8")
    source = (
        preparer.CANONICAL_TASKS / preparer.CONSULT_DISCOVERY[0][0] / "q007"
    )
    destination = tmp_path / "q007"

    preparer.copy_consult_task(
        source,
        destination,
        consult_skill="consult-semantic-okf-rust-mallet-evolved",
        variant="rust-mallet-reference-contract-test",
        reference_contract=True,
        reference_dictionary=dictionary_path,
    )

    tests = destination / "tests"
    assert (tests / "reference-dictionary.json").read_bytes() == (
        dictionary_path.read_bytes()
    )
    assert "/tests/reference-dictionary.json" in (
        tests / "test.sh"
    ).read_text(encoding="utf-8")
    assert not list(destination.rglob("*.pyc"))
    assert not list(destination.rglob("__pycache__"))


def test_evolution_preparer_accepts_an_explicit_untouched_holdout() -> None:
    preparer = load_module(
        "test_rust_mallet_evolution_holdout", EVOLUTION_PREPARER_MODULE
    )

    assert preparer.holdout_entries(["q005", "q020"]) == (
        ("holdout", "q005"),
        ("holdout", "q020"),
    )
    with pytest.raises(ValueError, match="at least two"):
        preparer.holdout_entries(["q005"])
    with pytest.raises(ValueError, match="unique"):
        preparer.holdout_entries(["q005", "q005"])
    with pytest.raises(ValueError, match="invalid"):
        preparer.holdout_entries(["question-5", "q020"])
    with pytest.raises(ValueError, match="absent"):
        preparer.holdout_entries(["q005", "q999"])


def test_evolution_job_uses_one_explicit_model_profile() -> None:
    preparer = load_module(
        "test_rust_mallet_evolution_model", EVOLUTION_PREPARER_MODULE
    )
    job = preparer.job_config(
        name="model-profile-test",
        task_root="/tasks",
        task_ids=["q007"],
        snapshot="/knowledge",
        auth_directory="/auth",
        attempts=1,
        jobs_dir="/jobs",
        baseline_skill="/skills/consult",
        model_name="openai-codex/gpt-5.3-codex",
    )

    assert job["agents"][0]["model_name"] == "openai-codex/gpt-5.3-codex"


def test_builder_evolution_preparer_accepts_an_explicit_untouched_holdout() -> None:
    preparer = load_builder_evolution_preparer(
        "test_rust_mallet_builder_evolution_holdout",
    )

    assert preparer.holdout_entries(["q005", "q020"]) == (
        ("holdout", "q005"),
        ("holdout", "q020"),
    )
    with pytest.raises(ValueError, match="at least two"):
        preparer.holdout_entries(["q005"])
    with pytest.raises(ValueError, match="unique"):
        preparer.holdout_entries(["q005", "q005"])
    with pytest.raises(ValueError, match="invalid"):
        preparer.holdout_entries(["question-5", "q020"])
    with pytest.raises(ValueError, match="absent"):
        preparer.holdout_entries(["q005", "q999"])


def test_builder_evolution_job_uses_one_explicit_model_profile() -> None:
    preparer = load_builder_evolution_preparer(
        "test_rust_mallet_builder_evolution_model",
    )
    job = preparer.job_config(
        name="builder-model-profile-test",
        jobs_dir="/jobs",
        task_root="/tasks",
        task_ids=["q007"],
        input_root="/dataset",
        auth_directory="/auth",
        build_skill="/skills/build",
        consult_skill="/skills/consult",
        model_name="github-copilot/gpt-5.3-codex",
        attempts=1,
    )

    assert job["agents"][0]["model_name"] == "github-copilot/gpt-5.3-codex"


def test_preserving_prepare_proposals_are_trace_backed_and_atomic() -> None:
    generator = load_module(
        "test_rust_mallet_preserving_prepare_proposals",
        PRESERVING_PREPARE_PROPOSALS_MODULE,
    )

    proposals = generator.proposal_document()["proposals"]
    assert {proposal["operation"] for proposal in proposals} == {
        "create",
        "replace",
    }
    assert {proposal["target"] for proposal in proposals} == {
        "SKILL.md",
        "scripts/prepare_reference_consult.py",
    }
    assert all(len(proposal["evidenceIds"]) == 2 for proposal in proposals)
    helper = next(
        proposal for proposal in proposals if proposal["operation"] == "create"
    )
    assert 'return {**search, "selected": selected}' in helper["content"]
    protocol = next(
        proposal for proposal in proposals if proposal["operation"] == "replace"
    )
    assert "matched query" in protocol["content"]
    assert "MINIMUM + 2" in protocol["content"]
    with pytest.raises(ValueError, match="at least two unique"):
        generator.proposal_document(("duplicate", "duplicate"))


def test_one_command_builder_proposals_are_trace_backed_and_distinct() -> None:
    generator = load_module(
        "test_rust_mallet_one_command_builder_proposals",
        ONE_COMMAND_BUILDER_PROPOSALS_MODULE,
    )
    payload = generator.proposal_document(
        LIVE_EVOLVED_BUILDER,
        BUILDER_CANDIDATE_ASSETS,
        ONE_COMMAND_BUILDER_ASSETS,
        ["job-a:trial-a", "job-a:trial-b"],
    )
    proposals = payload["proposals"]

    assert len(proposals) == 5
    assert {proposal["target"] for proposal in proposals} == {
        "SKILL.md",
        "references/rust-mallet-format.md",
        "scripts/_reference_dictionary.py",
        "scripts/_rust_mallet_retrieval.py",
        "scripts/build_validate_semantic_okf_rust_mallet.py",
    }
    assert all(len(proposal["evidenceIds"]) == 2 for proposal in proposals)
    assert all(
        "one public build-and-validate command" in proposal["diagnosis"]
        for proposal in proposals
    )
    with pytest.raises(ValueError, match="at least two unique"):
        generator.proposal_document(
            LIVE_EVOLVED_BUILDER,
            BUILDER_CANDIDATE_ASSETS,
            ONE_COMMAND_BUILDER_ASSETS,
            ["duplicate", "duplicate"],
        )


def test_one_command_builder_requires_build_and_independent_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.syspath_prepend(str(LIVE_EVOLVED_BUILDER / "scripts"))
    wrapper = load_module(
        "test_rust_mallet_one_command_builder_wrapper",
        ONE_COMMAND_BUILDER_ASSETS
        / "build_validate_semantic_okf_rust_mallet.py",
    )
    output = tmp_path / "knowledge"
    calls: list[tuple[str, Path]] = []

    def fake_build(
        manifest: Path,
        plan: Path,
        destination: Path,
        core_builder: object,
    ) -> dict[str, object]:
        calls.append(("build", destination))
        destination.mkdir()
        return {"status": "pass", "summary": {"documents": 2}}

    def fake_validate(destination: Path) -> dict[str, object]:
        calls.append(("validate", destination))
        return {
            "status": "pass",
            "valid": True,
            "errors": [],
            "warnings": [],
        }

    monkeypatch.setattr(wrapper, "atomic_build", fake_build)
    monkeypatch.setattr(wrapper, "validate_classical_bundle", fake_validate)

    assert wrapper.main(["manifest.json", "plan.json", str(output)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "pass"
    assert [name for name, _ in calls] == ["build", "validate"]
    assert all(destination == output for _, destination in calls)


def test_preserving_prepare_keeps_guidance_text_and_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scripts = EVOLVED_CONSULT_ROOT / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    helper = load_module(
        "test_rust_mallet_preserving_prepare_helper",
        PRESERVING_PREPARE_HELPER_MODULE,
    )
    recommended = [
        {
            "reference_id": "ref-000000000000000000000001",
            "interpretation": "mechanism one",
        },
        {
            "reference_id": "ref-000000000000000000000002",
            "interpretation": "mechanism two",
        },
    ]
    selected = [
        {
            "reference_id": row["reference_id"],
            "source_identity": f"paper-{number}",
            "text": f"authoritative text {number}",
        }
        for number, row in enumerate(recommended, start=1)
    ]
    monkeypatch.setattr(
        helper,
        "_search",
        lambda args: {"status": "pass", "recommended": recommended},
    )
    monkeypatch.setattr(
        helper,
        "_show",
        lambda args: {"status": "pass", "selected": selected},
    )

    result = helper.prepare(SimpleNamespace(bundle=Path("/knowledge")))

    assert result["recommended"] == recommended
    assert result["selected"] == selected

    monkeypatch.setattr(
        helper,
        "_show",
        lambda args: {"status": "pass", "selected": list(reversed(selected))},
    )
    with pytest.raises(
        helper.ReferenceConsultError,
        match="order differs",
    ):
        helper.prepare(SimpleNamespace(bundle=Path("/knowledge")))


def test_reference_evolution_summary_preserves_strict_gate_decisions() -> None:
    summary = json.loads(REFERENCE_EVOLUTION_SUMMARY.read_text(encoding="utf-8"))

    assert summary["status"] == "complete"
    assert summary["decision"] == {
        "builder": "keep-baseline",
        "consult": "retain-reference-aware-parent-a",
        "native_builder_candidate": "experimental-not-promoted",
        "one_command_builder_candidate": "experimental-not-promoted",
    }
    assert summary["reference_dictionary"]["count"] == 1135
    assert summary["reference_dictionary"]["sha256"] == (
        "886c3ba3ffb99c8f6a44ae8029e8792bfcf813ed80d59373ea2c2fe86033db3f"
    )
    consult = summary["consult_evolution"]
    assert consult["source_matches_harbor_bundle_excluding_bytecode"] is True
    assert consult["live_clean_source_digest"] == (
        "sha256:a86ced363990095d62ca8e413e5fc881aed08f0cdb21acb905da4f5c9600ccff"
    )
    builder = summary["builder_evolution"]
    assert builder["development"]["pass_rate"] == 1.0
    assert builder["holdout"]["candidate_qualified"] is True
    assert builder["holdout"]["decision"] == "keep-baseline"
    assert builder["holdout"]["mean_gain"] < 0
    assert all(
        row["delta"] < 0 for row in builder["holdout"]["per_task"].values()
    )
    one_command = summary["one_command_builder_evolution"]
    assert one_command["mechanical_validation"]["builds_byte_identical"] is True
    assert one_command["mechanical_validation"]["classical_file_count"] == 7
    assert one_command["development"]["pass_rate"] == 1.0
    assert one_command["holdout"]["candidate_qualified"] is True
    assert one_command["holdout"]["mean_gain"] > 0.01
    assert one_command["holdout"]["candidate_mean_wall_seconds"] < (
        one_command["holdout"]["baseline_mean_wall_seconds"]
    )
    assert one_command["holdout"]["decision"] == "keep-baseline"
    assert one_command["holdout"]["per_task"]["q015"]["delta"] < 0
    parity = summary["full_40_retrieval_parity"]
    assert parity["question_count"] == 40
    assert parity["comparison_count"] == 320
    assert parity["mismatch_count"] == 0
    assert parity["reference_rows_checked"] == 7267


def test_preserving_prepare_summary_records_non_evaluable_live_holdout() -> None:
    summary = json.loads(
        PRESERVING_PREPARE_SUMMARY.read_text(encoding="utf-8")
    )

    assert summary["status"] == "not-evaluable-holdout"
    assert summary["candidate"]["behavior"] == {
        "public_preparation_calls": 1,
        "legacy_search_and_show_retained": True,
        "recommended_interpretations_retained": True,
        "selected_authoritative_text_retained": True,
        "breadth_buffer_retained": True,
    }
    assert summary["local_qualification"]["q007_preparation"][
        "order_match"
    ] is True
    campaign = summary["promotion_campaign"]
    assert campaign["development"]["task_checksums_match_discovery"] is True
    assert campaign["development"]["evaluable_trials"] == 2
    assert campaign["development"]["pass_rate"] == 1.0
    assert campaign["holdout"]["tasks"] == ["q005", "q020"]
    assert campaign["holdout"]["opened"] is True
    assert campaign["holdout"]["decision"] == "not-evaluable"
    assert campaign["holdout"]["candidate_errors"] == 1
    assert campaign["holdout"]["candidate_mean_reward"] is None
    assert campaign["holdout"]["per_task"]["q020"]["candidate_error"].endswith(
        "exit 137"
    )
    assert summary["decision"]["promotion"] is False


def test_rejected_native_builder_is_not_copied_into_live_skill() -> None:
    live = (
        LIVE_EVOLVED_BUILDER / "scripts" / "_rust_mallet_retrieval.py"
    ).read_text(encoding="utf-8")
    candidate = (
        BUILDER_CANDIDATE_ASSETS / "_rust_mallet_retrieval.py"
    ).read_text(encoding="utf-8")

    assert '"references": "classical/references.json"' not in live
    assert '"references": "classical/references.json"' in candidate
    assert (BUILDER_CANDIDATE_ASSETS / "_reference_dictionary.py").is_file()


def test_reference_parity_normalization_removes_only_compact_id() -> None:
    module = load_module(
        "test_rust_mallet_reference_parity", REFERENCE_PARITY_MODULE
    )
    payload = {
        "status": "pass",
        "snapshot": {"path": "snapshot-a"},
        "results": [
            {
                "document_id": "document-1",
                "reference_id": "ref-0123456789abcdef01234567",
                "score": 1.0,
            }
        ],
    }

    assert module._normalized(payload) == {
        "status": "pass",
        "results": [{"document_id": "document-1", "score": 1.0}],
    }
    assert payload["results"][0]["reference_id"].startswith("ref-")


def test_canonical_evaluator_requires_complete_compact_references(
    tmp_path: Path,
) -> None:
    module = load_module(
        "test_rust_mallet_canonical_evaluator", CANONICAL_EVALUATOR_MODULE
    )
    bundle = tmp_path / "bundle"
    artifact = bundle / "classical" / "references.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text('{"references":{}}\n', encoding="utf-8")
    snapshot = SimpleNamespace(
        documents=(
            {"document_id": "document-1"},
            {"document_id": "document-2"},
        ),
        references_by_document={
            "document-1": {
                "reference_id": "ref-000000000000000000000001"
            },
            "document-2": {
                "reference_id": "ref-000000000000000000000002"
            },
        },
    )

    contract = module._reference_contract(snapshot, bundle)

    assert contract["status"] == "pass"
    assert contract["count"] == 2
    assert contract["artifact"]["sha256"]

    snapshot.references_by_document["document-2"]["reference_id"] = (
        "ref-000000000000000000000001"
    )
    with pytest.raises(
        module.CanonicalEvaluationError, match="missing, duplicated, or malformed"
    ):
        module._reference_contract(snapshot, bundle)


def test_canonical_evaluator_refuses_to_replace_evidence(tmp_path: Path) -> None:
    module = load_module(
        "test_rust_mallet_canonical_append_only", CANONICAL_EVALUATOR_MODULE
    )
    output = tmp_path / "comparison.json"
    output.write_text("{}\n", encoding="utf-8")

    with pytest.raises(module.CanonicalEvaluationError, match="already exists"):
        module._require_absent(output)


def test_checked_canonical_rerun_reports_quality_time_and_registry_boundary() -> None:
    summary = json.loads(
        CANONICAL_RETRIEVAL_SUMMARY.read_text(encoding="utf-8")
    )

    assert summary["status"] == "pass"
    assert summary["question_count"] == 40
    assert summary["candidate_state"] == (
        "experimental-comparator-not-registry-family"
    )
    assert summary["top10"]["error_count"] == 0
    assert summary["top10"]["evidence_validity"] == 1.0
    assert summary["top10"]["evaluation_wall_ms"] > 0
    assert summary["top10"]["shared_setup_ms"] > 0
    assert set(summary["top10"]["routes"]) == {
        "rust_mallet_bm25",
        "rust_mallet_topic",
        "rust_mallet_association",
        "rust_mallet_fusion",
    }
    assert all(
        route["timing_ms"]["p95"] > 0
        for route in summary["top10"]["routes"].values()
    )
    assert summary["reference_parity"] == {
        "status": "pass",
        "deep_validation": True,
        "comparison_count": 320,
        "mismatch_count": 0,
        "reference_rows_checked": 7267,
        "unique_reference_ids_returned": 728,
    }

    table = GENERAL_RETRIEVAL_TABLE.read_text(encoding="utf-8")
    for route in summary["top10"]["routes"]:
        assert f"`{route}`" in table
    assert "RustMallet + references (experimental)" in table
    assert "do not add either candidate to the canonical eight-family" in table
