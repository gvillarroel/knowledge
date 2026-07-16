from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
import yaml


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "evaluations" / "semantic-okf-endocrine-hygiene" / "scripts"


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def reporting_modules() -> tuple[ModuleType, ModuleType, ModuleType, ModuleType]:
    sys.path.insert(0, str(SCRIPTS))
    retrieval = _load_module("_retrieval_eval", SCRIPTS / "_retrieval_eval.py")
    manual = _load_module("endocrine_manual_reporting", SCRIPTS / "manual_verify_queries.py")
    answers = _load_module("endocrine_hard_answers", SCRIPTS / "compare_hard_answers.py")
    arena = _load_module("endocrine_arena_summary", SCRIPTS / "summarize_skill_arena.py")
    return retrieval, manual, answers, arena


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _write_bundle(
    root: Path,
    retrieval: ModuleType,
    *,
    source_id: str = "claims-pmc6504186",
    record_id: str = "claim-pmc6504186-test",
) -> tuple[Path, dict[str, Any]]:
    bundle = root
    concept_path = f"concepts/{source_id}/{record_id}.md"
    (bundle / concept_path).parent.mkdir(parents=True, exist_ok=True)
    (bundle / concept_path).write_text("reviewed concept\n", encoding="utf-8")
    body = "reviewed claim body"
    record: dict[str, Any] = {
        "source_id": source_id,
        "source_kind": "claim-jsonl",
        "source_path": "sources/claims/PMC6504186.jsonl",
        "record_id": record_id,
        "subject_iri": f"urn:test:{record_id}",
        "ontology_class_iri": "urn:test:ReviewedClaim",
        "concept_type": "ReviewedClaim",
        "title": "Reviewed claim",
        "body": body,
        "attributes": {
            "interpretation": "The exact reviewed interpretation.",
            "evidence_locator": "sources/markdown/PMC6504186.md#BioC-passage-0001",
            "evidence_text_sha256": "a" * 64,
        },
        "concept_id": f"concept-{record_id}",
        "concept_path": concept_path,
    }
    digest = {field: record[field] for field in retrieval.RECORD_DIGEST_FIELDS}
    record["record_sha256"] = hashlib.sha256(_canonical(digest).encode("utf-8")).hexdigest()
    semantic = bundle / "semantic"
    semantic.mkdir(parents=True, exist_ok=True)
    (semantic / "records.jsonl").write_text(_canonical(record) + "\n", encoding="utf-8")
    return bundle, record


def test_manual_cli_rebinds_every_legacy_row_and_rejects_forged_digest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    reporting_modules: tuple[ModuleType, ModuleType, ModuleType, ModuleType],
) -> None:
    retrieval, manual, _, _ = reporting_modules
    bundles = tmp_path / "bundles"
    bundle, record = _write_bundle(bundles / "legacy-a", retrieval)
    payload = {"status": "pass", "mode": "ledger", "returned": 1, "records": [record]}

    def completed(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(manual.subprocess, "run", completed)
    result = manual.run_cli(
        bundles,
        {record["source_id"]: "PMC6504186"},
        "legacy",
        "legacy-a",
        "evaluations/semantic-okf-endocrine-hygiene/scripts/manual_verify_queries.py",
        [],
    )
    assert result["evidence_valid"] is True
    assert result["evidence_validation"]["checked"] == 1
    assert result["evidence_validation"]["invalid"] == 0
    assert result["top_results"][0]["record_sha256"] == record["record_sha256"]
    assert result["top_results"][0]["locator"] == {"kind": "record"}
    assert result["top_results"][0]["retained_text_sha256"] == hashlib.sha256(
        record["body"].encode("utf-8")
    ).hexdigest()
    assert manual.tree_sha256(bundle) == result["bundle_tree_sha256_before"]

    forged = copy.deepcopy(record)
    forged["record_sha256"] = "f" * 64
    payload["records"] = [forged]
    with pytest.raises(manual.VerificationError, match="independent ledger validation"):
        manual.run_cli(
            bundles,
            {record["source_id"]: "PMC6504186"},
            "legacy",
            "legacy-a",
            "evaluations/semantic-okf-endocrine-hygiene/scripts/manual_verify_queries.py",
            [],
        )


def test_manual_embeddings_digest_rebound_is_explicit_and_does_not_mask_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    reporting_modules: tuple[ModuleType, ModuleType, ModuleType, ModuleType],
) -> None:
    retrieval, manual, _, _ = reporting_modules
    bundles = tmp_path / "bundles"
    _, record = _write_bundle(bundles / "embeddings-a", retrieval)
    hit = {
        "source_id": record["source_id"],
        "record_id": record["record_id"],
        "concept_id": record["concept_id"],
        "concept_path": record["concept_path"],
        "source_path": record["source_path"],
        "locator": {"kind": "record"},
        "text": record["body"],
        "text_sha256": hashlib.sha256(record["body"].encode("utf-8")).hexdigest(),
        "score": 1.0,
    }
    payload = {
        "status": "pass",
        "requested_mode": "lexical",
        "effective_mode": "lexical",
        "returned": 1,
        "hits": [hit],
    }

    def completed(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(manual.subprocess, "run", completed)
    result = manual.run_cli(
        bundles,
        {record["source_id"]: "PMC6504186"},
        "embeddings",
        "embeddings-a",
        "evaluations/semantic-okf-endocrine-hygiene/scripts/manual_verify_queries.py",
        [],
    )
    assert result["evidence_validation"]["record_sha256_rebound_hit_count"] == 1
    assert result["top_results"][0]["record_sha256_origin"] == "authoritative-ledger-rebound"

    hit["record_sha256"] = "f" * 64
    with pytest.raises(manual.VerificationError, match="independent ledger validation"):
        manual.run_cli(
            bundles,
            {record["source_id"]: "PMC6504186"},
            "embeddings",
            "embeddings-a",
            "evaluations/semantic-okf-endocrine-hygiene/scripts/manual_verify_queries.py",
            [],
        )


def _selected_claim(claim_id: str, *, evidence_hash: str = "b" * 64) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "paper_id": "PMC1",
        "source_id": "claims-pmc1",
        "concept_path": f"concepts/claims-pmc1/{claim_id}.md",
        "source_path": "sources/claims/PMC1.jsonl",
        "record_sha256": "c" * 64,
        "evidence_locator": "sources/markdown/PMC1.md#BioC-passage-0001",
        "evidence_text_sha256": evidence_hash,
    }


def test_hard_answer_scoring_uses_exact_claim_ids_separately_from_passage_evidence(
    reporting_modules: tuple[ModuleType, ModuleType, ModuleType, ModuleType],
) -> None:
    _, _, answers, _ = reporting_modules
    truth = {
        "authoritative_evidence": [{"id": "e1", "paper_id": "PMC1", "text_sha256": "b" * 64}],
        "ground_truth": {
            "required_paper_ids": ["PMC1"],
            "answer_claims": [{"id": "a1", "evidence_ids": ["e1"]}],
            "important_negatives": [{"id": "n1", "evidence_ids": ["e1"]}],
        },
    }
    requirements = {
        "answer_claims": [{"id": "a1", "required_claim_ids": ["claim-a", "claim-b"]}],
        "important_negatives": [{"id": "n1", "required_claim_ids": ["claim-b"]}],
    }
    claims = [_selected_claim("claim-a"), _selected_claim("claim-same-passage-but-wrong")]
    metrics = answers._score_answer(truth, requirements, claims)
    assert metrics["authoritative_evidence_completeness"] == 1.0
    assert metrics["atomic_reviewed_claim_fidelity"] == 0.0
    assert metrics["important_negative_reviewed_claim_fidelity"] == 0.0
    assert metrics["exact_required_claim_precision"] == 0.5
    assert metrics["covered_required_claim_ids"] == ["claim-a"]
    assert metrics["missing_required_claim_ids"] == ["claim-b"]

    complete = answers._score_answer(truth, requirements, [*claims, _selected_claim("claim-b")])
    assert complete["atomic_reviewed_claim_fidelity"] == 1.0
    assert complete["important_negative_reviewed_claim_fidelity"] == 1.0
    assert complete["exact_required_claim_precision"] == pytest.approx(2 / 3)


def test_hard_claim_requirement_loader_fails_closed_on_nonexact_atom_ids(
    tmp_path: Path,
    reporting_modules: tuple[ModuleType, ModuleType, ModuleType, ModuleType],
) -> None:
    _, _, answers, _ = reporting_modules
    truth = {
        "q1": {
            "ground_truth": {
                "answer_claims": [{"id": "q1-a1"}],
                "important_negatives": [{"id": "q1-n1"}],
            }
        }
    }
    value = {
        "schema_version": "semantic-okf-endocrine-hygiene-hard-claim-requirements/1.0",
        "contract": "Every exact reviewed claim is required.",
        "questions": [
            {
                "id": "q1",
                "answer_claims": [{"id": "wrong", "required_claim_ids": ["claim-a"]}],
                "important_negatives": [{"id": "q1-n1", "required_claim_ids": ["claim-b"]}],
            }
        ],
    }
    path = tmp_path / "requirements.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(answers.EvaluationError, match="do not exactly match"):
        answers._load_claim_requirements(path, truth)


def _arena_fixture(
    tmp_path: Path,
    retrieval: ModuleType,
    arena: ModuleType,
) -> dict[str, Path]:
    bundle, record = _write_bundle(tmp_path / "bundle", retrieval)
    prompt_id = "q030-causal-evidence-map"
    profile_ids = ["knowledge-only-control", "classical-cli-consult-treatment"]
    variant_id = "pi-luna-only"
    model = "openai-codex/gpt-test"
    prompt_text = "Answer the bound question and return exact JSON."
    global_assertions = [{"type": "is-json", "metric": "response-format"}]
    local_assertions = [
        {"type": "javascript", "metric": "evidence-validity", "value": "return true;"},
        {"type": "javascript", "metric": "claim-fidelity", "value": "return true;"},
    ]
    source = {
        "schemaVersion": 1,
        "benchmark": {"id": "bound-benchmark"},
        "task": {
            "prompts": [
                {
                    "id": prompt_id,
                    "prompt": prompt_text,
                    "evaluation": {"assertions": local_assertions},
                }
            ]
        },
        "workspace": {},
        "evaluation": {"assertions": global_assertions, "requests": 1},
        "comparison": {
            "profiles": [{"id": profile_id} for profile_id in profile_ids],
            "variants": [
                {"id": variant_id, "agent": {"model": model, "adapter": "pi"}}
            ],
        },
    }
    source_path = tmp_path / "source.yaml"
    source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
    manifest = {
        "status": "pass",
        "benchmark_id": "bound-benchmark",
        "prompt_ids": [prompt_id],
        "profiles": profile_ids,
        "requests_per_cell": 1,
        "config": {"path": "source.yaml", "sha256": arena.sha256_file(source_path)},
        "bundle": arena.tree_binding(bundle),
        "reviewed_ledger_claim_count": 1,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    compiled_tests = [
        {
            "vars": {"taskPrompt": prompt_text, "variantId": variant_id},
            "metadata": {
                "benchmarkId": "bound-benchmark",
                "promptId": prompt_id,
                "variantId": variant_id,
                "rowId": f"{variant_id}:{prompt_id}",
            },
            "assert": [*global_assertions, *local_assertions],
        }
    ]
    providers = [
        {
            "id": "compare-provider",
            "label": profile_id,
            "config": {
                "provider_id": profile_id,
                "profile_id": profile_id,
                "routes": {
                    variant_id: {"provider": {"config": {"model": model}}}
                },
            },
        }
        for profile_id in profile_ids
    ]
    compiled = {
        "description": "bound-benchmark:compare",
        "prompts": ["{{taskPrompt}}"],
        "providers": providers,
        "tests": compiled_tests,
    }
    run = tmp_path / "append-only-run"
    run.mkdir()
    compiled_path = run / "promptfooconfig.yaml"
    compiled_path.write_text(yaml.safe_dump(compiled, sort_keys=False), encoding="utf-8")
    evidence = {
        "claim_id": record["record_id"],
        "concept_path": record["concept_path"],
        "paper_id": "PMC6504186",
        "source_path": record["source_path"],
        "evidence_locator": record["attributes"]["evidence_locator"],
        "evidence_text_sha256": record["attributes"]["evidence_text_sha256"],
    }
    output = {
        "question_id": prompt_id,
        "answer": {
            "summary": "A bound exact answer.",
            "claims": [
                {
                    "statement": record["attributes"]["interpretation"],
                    "supporting_claim_ids": [record["record_id"]],
                }
            ],
            "paper_ids": ["PMC6504186"],
        },
        "evidence": [evidence],
    }
    rows = []
    for profile_id in profile_ids:
        rows.append(
            {
                "testCase": {
                    "metadata": compiled_tests[0]["metadata"],
                    "vars": compiled_tests[0]["vars"],
                    "assert": compiled_tests[0]["assert"],
                },
                "provider": {"id": profile_id, "label": profile_id},
                "metadata": {"profileId": profile_id, "variantId": variant_id},
                "prompt": {"raw": prompt_text},
                "response": {"output": json.dumps(output)},
                "gradingResult": {
                    "namedScores": {
                        "response-format": 1,
                        "evidence-validity": 1,
                        "claim-fidelity": 1,
                    }
                },
                "success": True,
                "score": 1.0,
                "latencyMs": 100,
            }
        )
    raw = {
        "evalId": "eval-bound",
        "config": {**compiled, "tags": {}},
        "results": {"results": rows, "stats": {"errors": 0}},
    }
    raw_path = run / "promptfoo-results.json"
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    return {
        "bundle": bundle,
        "source": source_path,
        "manifest": manifest_path,
        "compiled": compiled_path,
        "raw": raw_path,
        "json_output": tmp_path / "report.json",
        "markdown_output": tmp_path / "report.md",
    }


def test_arena_summary_binds_every_identity_and_both_config_hashes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    reporting_modules: tuple[ModuleType, ModuleType, ModuleType, ModuleType],
) -> None:
    retrieval, _, _, arena = reporting_modules
    paths = _arena_fixture(tmp_path, retrieval, arena)
    monkeypatch.setattr(arena, "REPOSITORY", tmp_path)
    assert (
        arena.main(
            [
                "--input",
                str(paths["raw"]),
                "--raw-promptfoo-config",
                str(paths["compiled"]),
                "--source-config",
                str(paths["source"]),
                "--config-manifest",
                str(paths["manifest"]),
                "--bundle",
                str(paths["bundle"]),
                "--json-output",
                str(paths["json_output"]),
                "--markdown-output",
                str(paths["markdown_output"]),
            ]
        )
        == 0
    )
    report = json.loads(paths["json_output"].read_text(encoding="utf-8"))
    assert report["binding"]["status"] == "pass"
    assert report["binding"]["source_config"]["sha256"] == arena.sha256_file(paths["source"])
    assert report["binding"]["raw_promptfoo_config"]["sha256"] == arena.sha256_file(paths["compiled"])
    assert report["execution"]["reviewed_ledger_claim_count"] == 1
    assert len(report["cells"]) == 2
    assert all(cell["independent_ledger_evidence_valid"] for cell in report["cells"])
    assert all(cell["independent_reviewed_claim_fidelity"] for cell in report["cells"])


def test_arena_summary_rejects_duplicate_cells_and_source_config_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    reporting_modules: tuple[ModuleType, ModuleType, ModuleType, ModuleType],
) -> None:
    retrieval, _, _, arena = reporting_modules
    paths = _arena_fixture(tmp_path, retrieval, arena)
    monkeypatch.setattr(arena, "REPOSITORY", tmp_path)
    source = arena.load_yaml(paths["source"])
    contract = arena.source_contract(source)
    raw = arena.load_json(paths["raw"])
    rows = raw["results"]["results"]
    rows[1]["provider"] = dict(rows[0]["provider"])
    rows[1]["metadata"]["profileId"] = rows[0]["metadata"]["profileId"]
    with pytest.raises(arena.SummaryError, match="duplicate result cell"):
        arena.validate_result_cells(rows, contract)

    paths["source"].write_text(paths["source"].read_text(encoding="utf-8") + "# drift\n", encoding="utf-8")
    manifest = arena.load_json(paths["manifest"])
    with pytest.raises(arena.SummaryError, match="digest does not match"):
        arena.validate_manifest_binding(manifest, contract, paths["source"], paths["bundle"])
