from __future__ import annotations

import copy
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations/semantic-okf-ensemble"
SCRIPTS = EVALUATION_ROOT / "scripts"


def _load(name: str, path: Path) -> ModuleType:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def modules(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[ModuleType, ModuleType, ModuleType]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    answer = importlib.import_module("_answer_output")
    evaluation = importlib.import_module("_evaluation")
    aggregate = _load(
        "test_semantic_okf_answer_aggregate",
        SCRIPTS / "aggregate_answer_output_evaluation.py",
    )
    monkeypatch.setattr(answer, "REPO_ROOT", tmp_path)
    skill_arena_config = tmp_path / "ensemble-hard10.yaml"
    skill_arena_config.write_text(
        json.dumps(
            {
                "task": {
                    "prompts": [
                        {"id": question_id, "prompt": _task_prompt(question_id)}
                        for question_id in _contract()["benchmark"]["question_ids"]
                    ]
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(answer, "SKILL_ARENA_CONFIG", skill_arena_config)
    monkeypatch.setattr(evaluation, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(aggregate, "REPO_ROOT", tmp_path)
    return answer, aggregate, evaluation


def _contract() -> dict:
    return json.loads(
        (EVALUATION_ROOT / "answer-output-evaluation-contract.json").read_text(encoding="utf-8")
    )


def test_answer_contract_binds_the_reviewed_ground_truth_and_frozen_manifest() -> None:
    answer = _load(
        "test_semantic_okf_reviewed_answer_contract",
        SCRIPTS / "_answer_output.py",
    )

    contract = answer.load_contract(
        EVALUATION_ROOT / "answer-output-evaluation-contract.json"
    )

    assert contract["schema_version"] == (
        "semantic-okf-ensemble-answer-evaluation-contract/1.5"
    )
    assert contract["benchmark"]["command_path"] == r"publication-runtime\run_codex.cmd"
    assert contract["ground_truth"] == {
        "path": (
            "evaluations/semantic-okf-ensemble/reviewed-benchmark/"
            "hard-ground-truth.jsonl"
        ),
        "sha256": "c656fc575b0c7e06cd386093d975cd74ef9c9aead743312e3aadec1cbdc08451",
        "schema_version": "semantic-okf-hard-ground-truth/1.0",
        "benchmark_manifest_path": (
            "evaluations/semantic-okf-ensemble/reviewed-benchmark/"
            "frozen-answer-benchmark.json"
        ),
        "benchmark_manifest_sha256": (
            "257997cc2da3d9afae596ac8b46551a1b1fa73480f15861a25f262bb85a91f62"
        ),
        "benchmark_id": "semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1",
    }
    assert contract["publication"]["mcp_protocol"] == {
        "tools": [
            "semantic_okf_bootstrap_skill",
            "semantic_okf_inspect",
            "semantic_okf_coverage_brief",
            "semantic_okf_prepare_answer",
            "semantic_okf_confirm_answer",
        ],
        "bootstrap_schema": "semantic-okf-skill-bootstrap/1.0",
        "bootstrap_key_order": [
            "schema",
            "skill_id",
            "skill_sha256",
            "byte_count",
            "skill_markdown",
        ],
        "bootstrap_skill_id": "consult-semantic-okf-ensemble",
        "bootstrap_skill_sha256": "ec80687beb701f5fc8b6cd13d5ec779cbe5e1f52baffbf3a4a41db4f390717c2",
        "bootstrap_skill_byte_count": 15699,
        "bootstrap_exactly_once": True,
        "bootstrap_first": True,
        "treatment_shell_tool_disabled": True,
        "treatment_skill_id": "consult-semantic-okf-ensemble",
        "shell_disable_arguments": ["--disable", "shell_tool"],
        "shell_isolation_receipt_schema": (
            "semantic-okf-shell-isolation-receipt/1.0"
        ),
        "shell_isolation_receipt_key_order": [
            "schema",
            "skill_id",
            "shell_tool_disabled",
        ],
        "controls_shell_policy_unchanged": True,
        "mode_argument": False,
        "minimum_successful_prepares": 1,
        "prepared_answer_schema": "semantic-okf-prepared-answer/1.0",
        "prepared_answer_key_order": [
            "schema",
            "candidate_json",
            "response_sha256",
            "byte_count",
        ],
        "candidate_digest_binding": "sha256-lowercase-hex-of-utf8-candidate-json",
        "confirm_argument": "response_sha256",
        "confirm_argument_pattern": "^[0-9a-f]{64}$",
        "confirmation_receipt_schema": "semantic-okf-answer-confirmation-receipt/1.0",
        "confirmation_receipt_key_order": [
            "schema",
            "status",
            "response_sha256",
            "byte_count",
        ],
        "publication_source": "prepared-envelope-candidate-json-bytes",
        "confirm_exactly_once": True,
        "confirm_terminal": True,
        "confirm_idempotent": False,
        "failed_protocol_call_publishes": False,
        "failed_protocol_call_clears_transaction": True,
        "failure_requires_fresh_prepare": True,
        "final_transaction_must_be_clean": True,
        "coverage_priority_order": "persisted-idf-facet-consensus-priority-v1",
        "priority_order_session_bound": True,
    }


def test_answer_contract_rejects_reviewed_manifest_hash_drift(tmp_path: Path) -> None:
    answer = _load(
        "test_semantic_okf_reviewed_answer_contract_drift",
        SCRIPTS / "_answer_output.py",
    )
    contract = _contract()
    contract["ground_truth"]["benchmark_manifest_sha256"] = "0" * 64
    changed = tmp_path / "answer-output-evaluation-contract.json"
    changed.write_text(
        json.dumps(contract, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(
        answer.AnswerEvaluationError,
        match="benchmark manifest SHA-256 differs",
    ):
        answer.load_contract(changed)


def test_answer_contract_rejects_prepare_confirm_protocol_drift(
    tmp_path: Path,
) -> None:
    answer = _load(
        "test_semantic_okf_answer_contract_protocol_drift",
        SCRIPTS / "_answer_output.py",
    )
    contract = _contract()
    contract["publication"]["mcp_protocol"]["mode_argument"] = True
    changed = tmp_path / "answer-output-evaluation-contract.json"
    changed.write_text(
        json.dumps(contract, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(answer.AnswerEvaluationError, match="publication contract differs"):
        answer.load_contract(changed)


def test_answer_contract_rejects_candidate_copy_confirmation_regression(
    tmp_path: Path,
) -> None:
    answer = _load(
        "test_semantic_okf_answer_contract_digest_regression",
        SCRIPTS / "_answer_output.py",
    )
    contract = _contract()
    contract["publication"]["mcp_protocol"]["confirm_argument"] = "candidate_json"
    changed = tmp_path / "answer-output-evaluation-contract.json"
    changed.write_text(
        json.dumps(contract, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(answer.AnswerEvaluationError, match="publication contract differs"):
        answer.load_contract(changed)


def _ledger(answer: ModuleType, root: Path, contract: dict) -> object:
    claim_id = "claim-2402-07630v3-001"
    concept_path = "concepts/claims-2402-07630v3/claim-2402-07630v3-001-test.md"
    body = "# Reviewed claim\n\n- **interpretation**: Fixture claim."
    claim = {
        "record_id": claim_id,
        "record_sha256": "1" * 64,
        "source_id": "claims-2402-07630v3",
        "source_path": "sources/claims/2402.07630v3.jsonl",
        "concept_path": concept_path,
        "body": body,
        "attributes": {
            "review_state": "reviewed",
            "claim_kind": "comparison",
            "interpretation": "Fixture claim.",
            "evidence_locator": (
                "sources/markdown/2402.07630v3.md#PDF-page-4;"
                "sources/markdown/2402.07630v3.md#PDF-page-5"
            ),
        },
    }
    paper = {
        "record_id": "paper-2402-07630v3",
        "source_id": "paper-2402-07630v3",
        "source_path": "sources/markdown/2402.07630v3.md",
    }
    concept = root / concept_path
    concept.parent.mkdir(parents=True)
    concept.write_text(
        "---\n"
        f"record_id: {claim_id}\n"
        f"record_sha256: {claim['record_sha256']}\n"
        f"source_id: {claim['source_id']}\n"
        f"source_path: {claim['source_path']}\n"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
        newline="\n",
    )
    expected = contract["bundle"]
    identity = {
        "run_id": expected["run_id"],
        "repository_path": expected["repository_path"],
        "file_count": expected["file_count"],
        "tree_sha256": expected["tree_sha256"],
        "ensemble_index_sha256": expected["ensemble_index_sha256"],
        "ensemble_plan_sha256": expected["ensemble_plan_sha256"],
        "core_tree_sha256": expected["core_tree_sha256"],
        "records_sha256": expected["records_sha256"],
        "record_count": expected["record_count"],
        "source_manifest_sha256": expected["source_manifest_sha256"],
    }
    return answer.BundleLedger(
        root=root,
        identity=identity,
        records={claim_id: claim, paper["record_id"]: paper},
        paper_records={"2402.07630v3": paper},
    )


def _truth(contract: dict) -> dict[str, dict]:
    result = {}
    for question_id in contract["benchmark"]["question_ids"]:
        prefix = question_id.split("-", 1)[0]
        result[question_id] = {
            "id": question_id,
            "question": f"Fixture question for {question_id}?",
            "ground_truth": {
                "answer_claims": [
                    {
                        "id": f"{prefix}-a1",
                        "statement": "Fixture answer claim.",
                        "evidence_claim_ids": ["claim-2402-07630v3-001"],
                    }
                ],
                "derivation": [
                    {"operation": "identity", "inputs": [f"{prefix}-a1"], "conclusion": "Fixture."}
                ],
                "important_negatives": [
                    {
                        "id": f"{prefix}-n1",
                        "statement": "Do not contradict the fixture.",
                        "evidence_claim_ids": ["claim-2402-07630v3-001"],
                    }
                ],
                "acceptable_variants": ["Equivalent fixture wording."],
                "required_paper_ids": ["2402.07630v3"],
                "required_source_ids": ["claims-2402-07630v3", "paper-2402-07630v3"],
            },
        }
    return result


def _output(question_id: str) -> str:
    summary = " ".join(f"word{index}" for index in range(180))
    value = {
        "question_id": question_id,
        "answer": {
            "summary": summary,
            "claims": [
                {
                    "statement": "Fixture claim.",
                    "supporting_claim_ids": ["claim-2402-07630v3-001"],
                }
            ],
            "paper_ids": ["2402.07630v3"],
            "citations": [{"paper_id": "2402.07630v3", "pages": [4]}],
        },
        "evidence": [
            {
                "claim_id": "claim-2402-07630v3-001",
                "concept_path": "concepts/claims-2402-07630v3/claim-2402-07630v3-001-test.md",
                "paper_id": "2402.07630v3",
                "source_path": "sources/claims/2402.07630v3.jsonl",
                "locators": ["PDF-page-4"],
            }
        ],
    }
    return json.dumps(value, separators=(",", ":"))


def _task_prompt(question_id: str) -> str:
    return (
        "Answer using only the published Semantic OKF snapshot at `knowledge/`.\n"
        f"Question: Fixture question for {question_id}?\n"
        "Return JSON only with the contracted answer and authoritative evidence."
    )


def _effective_provider(profile: str, variant: str) -> dict:
    skill_id = {
        "knowledge-only-control": None,
        "adaptive-consult-control": "consult-semantic-okf-adaptive",
        "ensemble-consult-treatment": "consult-semantic-okf-ensemble",
    }[profile]
    root = f"C:/skill-arena-execution-{profile}"
    preamble = (
        ""
        if skill_id is None
        else "Skill activation: explicitly invoke and follow these skills before solving the task: "
        f"${skill_id}."
    )
    installed = (
        []
        if skill_id is None
        else [{"path": f"{root}/codex-home/skills/{skill_id}/SKILL.md", "enabled": True}]
    )
    return {
        "id": "C:/skill-arena/src/providers/compare-matrix-provider.js",
        "label": profile,
        "config": {
            "provider_id": profile,
            "profile_id": profile,
            "skill_mode_id": profile,
            "routes": {
                variant: {
                    "scenarioId": f"{variant}-{profile}",
                    "provider": {
                        "id": "C:/skill-arena/src/providers/codex-system-provider.js",
                        "label": "codex:command:gpt-5.6-luna",
                        "config": {
                            "provider_id": "codex:command:gpt-5.6-luna",
                            "execution_method": "command",
                            "command_path": r"publication-runtime\run_codex.cmd",
                            "model": "gpt-5.6-luna",
                            "working_dir": f"{root}/workspace",
                            "sandbox_mode": "workspace-write",
                            "approval_policy": "never",
                            "web_search_enabled": False,
                            "network_access_enabled": False,
                            "model_reasoning_effort": "medium",
                            "env_passthrough": [
                                "SEMANTIC_OKF_PYTHON",
                                "SEMANTIC_OKF_HF_HUB_CACHE",
                            ],
                            "strict_runtime_isolation": True,
                            "prompt_preamble": preamble,
                            "cli_env": {
                                "HF_HUB_OFFLINE": "1",
                                "TRANSFORMERS_OFFLINE": "1",
                                "PYTHONDONTWRITEBYTECODE": "1",
                                "SKILL_ARENA_ISOLATION": "strict",
                                "SKILL_ARENA_EXECUTION_ROOT": root,
                                "SKILL_ARENA_ALLOWED_SKILLS": skill_id or "",
                                "SEMANTIC_OKF_BUNDLE": f"{root}/workspace/knowledge",
                            },
                            "codex_config": {
                                "mcp_servers": {
                                    "semantic_okf": {
                                        "command": "cmd.exe",
                                        "args": ["/d", "/c", "mcp-runtime\\run_server.cmd"],
                                        "env_vars": [
                                            "SKILL_ARENA_ALLOWED_SKILLS",
                                            "CODEX_HOME",
                                            "SEMANTIC_OKF_BUNDLE",
                                            "SEMANTIC_OKF_PYTHON",
                                            "SEMANTIC_OKF_HF_HUB_CACHE",
                                            "HF_HUB_OFFLINE",
                                            "TRANSFORMERS_OFFLINE",
                                            "PYTHONDONTWRITEBYTECODE",
                                        ],
                                        "enabled_tools": [
                                            "semantic_okf_bootstrap_skill",
                                            "semantic_okf_inspect",
                                            "semantic_okf_coverage_brief",
                                            "semantic_okf_prepare_answer",
                                            "semantic_okf_confirm_answer",
                                        ],
                                        "startup_timeout_sec": 60,
                                        "tool_timeout_sec": 600,
                                    }
                                },
                                "skills": {"config": installed},
                            },
                        },
                    },
                }
            },
        },
    }


def _promptfoo(contract: dict) -> dict:
    rows = []
    variant = contract["benchmark"]["variant_id"]
    for profile in contract["benchmark"]["profiles"]:
        for question in contract["benchmark"]["question_ids"]:
            for repetition in range(1, contract["benchmark"]["repetitions_per_cell"] + 1):
                rows.append(
                    {
                        "id": f"{profile}:{question}:{repetition}",
                        "provider": {"id": profile, "label": profile},
                        "metadata": {
                            "benchmarkId": contract["benchmark"]["id"],
                            "profileId": profile,
                            "promptId": question,
                            "variantId": variant,
                            "scenarioId": f"{variant}-{profile}",
                            "rowId": f"{variant}:{question}",
                        },
                        "vars": {"variantId": variant},
                        "response": {"output": _output(question)},
                        "error": None,
                        "score": 0,
                    }
                )
    tests = []
    for question in contract["benchmark"]["question_ids"]:
        tests.append(
            {
                "vars": {"taskPrompt": _task_prompt(question), "variantId": variant},
                "metadata": {
                    "benchmarkId": contract["benchmark"]["id"],
                    "promptId": question,
                    "variantId": variant,
                    "rowId": f"{variant}:{question}",
                },
                "assert": [
                    {"type": "fixture", "metric": metric}
                    for metric in [
                        "response-format",
                        "response-contract",
                        "evidence-validity",
                        "atomic-answer-completeness",
                        "important-negative-coverage",
                    ]
                ],
            }
        )
    return {
        "evalId": "fixture-eval",
        "config": {
            "description": f"{contract['benchmark']['id']}:compare",
            "prompts": ["{{taskPrompt}}"],
            "providers": [
                _effective_provider(profile, variant)
                for profile in contract["benchmark"]["profiles"]
            ],
            "tests": tests,
        },
        "results": {"version": 3, "results": rows},
    }


def _prepare(
    answer: ModuleType,
    evaluation: ModuleType,
    tmp_path: Path,
) -> tuple[dict, object, dict, list[dict], dict, dict, Path, Path]:
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    truth = _truth(contract)
    raw_path = tmp_path / "raw" / "promptfoo-results.json"
    raw_path.parent.mkdir()
    raw_path.write_text(json.dumps(_promptfoo(contract)) + "\n", encoding="utf-8")
    contract_path = tmp_path / "answer-output-evaluation-contract.json"
    contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
    binding = {
        "path": contract_path.relative_to(tmp_path).as_posix(),
        "sha256": evaluation.sha256(contract_path),
    }
    mechanical, manifest, tasks = answer.prepare_answers(
        raw_path, ledger, truth, contract, binding
    )
    return contract, ledger, truth, tasks, mechanical, manifest, raw_path, contract_path


def test_exact_90_cell_parser_scores_valid_answers_and_blinds_profiles(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, _, evaluation = modules
    contract, _, _, tasks, mechanical, manifest, _, _ = _prepare(answer, evaluation, tmp_path)

    assert len(tasks) == len(mechanical["answers"]) == len(manifest["mapping"]) == 90
    assert {
        (row["profile_id"], row["question_id"], row["repetition"])
        for row in mechanical["answers"]
    } == {
        (profile, question, repetition)
        for profile in contract["benchmark"]["profiles"]
        for question in contract["benchmark"]["question_ids"]
        for repetition in range(1, 4)
    }
    assert all(set(row["metrics"].values()) == {1.0} for row in mechanical["answers"])
    blinded = answer.task_text(tasks)
    assert all(profile not in blinded for profile in contract["benchmark"]["profiles"])
    assert '"repetition"' not in blinded


@pytest.mark.parametrize(
    ("tamper", "expected"),
    [
        ("missing-config", "no effective config"),
        ("mcp-command", "MCP config differs"),
        ("allowed-skill", "allowed skill differs"),
        ("task-prompt", "task prompt differs"),
        ("provider", "Codex provider differs"),
        ("assertions", "assertion metrics differ"),
    ],
)
def test_parser_rejects_tampered_effective_generation_config(
    modules: tuple[ModuleType, ModuleType, ModuleType],
    tmp_path: Path,
    tamper: str,
    expected: str,
) -> None:
    answer, _, _ = modules
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    report = _promptfoo(contract)
    if tamper == "missing-config":
        report.pop("config")
    elif tamper == "mcp-command":
        report["config"]["providers"][0]["config"]["routes"][
            contract["benchmark"]["variant_id"]
        ]["provider"]["config"]["codex_config"]["mcp_servers"]["semantic_okf"][
            "command"
        ] = "python"
    elif tamper == "allowed-skill":
        report["config"]["providers"][2]["config"]["routes"][
            contract["benchmark"]["variant_id"]
        ]["provider"]["config"]["cli_env"]["SKILL_ARENA_ALLOWED_SKILLS"] = ""
    elif tamper == "task-prompt":
        report["config"]["tests"][0]["vars"]["taskPrompt"] += " altered"
    elif tamper == "provider":
        report["config"]["providers"][0]["config"]["routes"][
            contract["benchmark"]["variant_id"]
        ]["provider"]["id"] = "C:/skill-arena/src/providers/pi-system-provider.js"
    else:
        report["config"]["tests"][0]["assert"].reverse()
    raw_path = tmp_path / "promptfoo-results.json"
    raw_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(answer.AnswerEvaluationError, match=expected):
        answer.prepare_answers(
            raw_path,
            ledger,
            _truth(contract),
            contract,
            {"path": "contract.json", "sha256": "0" * 64},
        )


@pytest.mark.parametrize(
    "failure",
    [
        "partial",
        "duplicate-row",
        "missing-output",
        "response-error",
        "unclassified-row-error",
        "unclassified-false",
        "malformed-success",
    ],
)
def test_parser_fails_closed_on_partial_duplicate_or_adapter_failure(
    modules: tuple[ModuleType, ModuleType, ModuleType],
    tmp_path: Path,
    failure: str,
) -> None:
    answer, _, evaluation = modules
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    report = _promptfoo(contract)
    rows = report["results"]["results"]
    if failure == "partial":
        rows.pop()
        expected = "expected exactly 90"
    elif failure == "duplicate-row":
        rows[1]["id"] = rows[0]["id"]
        expected = "row IDs must be unique"
    elif failure == "missing-output":
        rows[0]["response"] = {"error": None}
        expected = "has no model output"
    elif failure == "response-error":
        rows[0]["response"]["error"] = "provider failed"
        expected = "adapter/runtime failure"
    elif failure == "unclassified-row-error":
        rows[0]["error"] = "provider failed"
        expected = "unclassified row error"
    elif failure == "unclassified-false":
        rows[0]["success"] = False
        expected = "unclassified false state"
    else:
        rows[0]["success"] = "false"
        expected = "non-boolean success state"
    raw_path = tmp_path / "promptfoo-results.json"
    raw_path.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(answer.AnswerEvaluationError, match=expected):
        answer.prepare_answers(
            raw_path,
            ledger,
            _truth(contract),
            contract,
            {"path": "contract.json", "sha256": "0" * 64},
        )


def test_parser_accepts_promptfoo_assertion_failure_with_completed_output(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, _, evaluation = modules
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    report = _promptfoo(contract)
    row = report["results"]["results"][0]
    reason = "Custom function returned false\nreturn false;"
    row["error"] = reason
    row["success"] = False
    row["gradingResult"] = {
        "pass": False,
        "score": 0,
        "reason": reason,
        "componentResults": [{"pass": False, "score": 0, "reason": reason}],
    }
    raw_path = tmp_path / "promptfoo-results.json"
    raw_path.write_text(json.dumps(report), encoding="utf-8")

    mechanical, manifest, tasks = answer.prepare_answers(
        raw_path,
        ledger,
        _truth(contract),
        contract,
        {"path": "contract.json", "sha256": "0" * 64},
    )

    assert len(mechanical["answers"]) == len(manifest["mapping"]) == len(tasks) == 90


def test_evidence_validity_is_independent_of_response_serialization_order(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, _, _ = modules
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    item = {
        "locators": ["PDF-page-5", "PDF-page-4"],
        "source_path": "sources/claims/2402.07630v3.jsonl",
        "paper_id": "2402.07630v3",
        "concept_path": "concepts/claims-2402-07630v3/claim-2402-07630v3-001-test.md",
        "claim_id": "claim-2402-07630v3-001",
    }

    valid, reason, claim_id = answer.verify_evidence_item(
        item,
        ledger,
        {"2402.07630v3": {4, 5}},
        contract["response_contract"]["evidence_keys"],
    )

    assert (valid, reason, claim_id) == (True, "valid", "claim-2402-07630v3-001")
    output = json.loads(_output("q031-graph-routing-boundary"))
    output["answer"]["citations"][0]["pages"] = [4, 5]
    output["evidence"] = [item]
    assert answer.response_contract_score(
        output, "q031-graph-routing-boundary", contract
    ) == 0.0


def test_parser_accepts_recoverable_tool_stderr_with_completed_output(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, _, evaluation = modules
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    report = _promptfoo(contract)
    report["results"]["results"][0]["response"]["metadata"] = {
        "stderr": "ERROR codex_core::tools::router: recoverable command failure"
    }
    raw_path = tmp_path / "promptfoo-results.json"
    raw_path.write_text(json.dumps(report), encoding="utf-8")

    mechanical, manifest, tasks = answer.prepare_answers(
        raw_path,
        ledger,
        _truth(contract),
        contract,
        {"path": "contract.json", "sha256": "0" * 64},
    )

    assert len(mechanical["answers"]) == len(manifest["mapping"]) == len(tasks) == 90


def test_parser_rejects_malformed_stderr_metadata(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, _, _ = modules
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    report = _promptfoo(contract)
    report["results"]["results"][0]["response"]["metadata"] = {"stderr": ["bad"]}
    raw_path = tmp_path / "promptfoo-results.json"
    raw_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(answer.AnswerEvaluationError, match="malformed stderr metadata"):
        answer.prepare_answers(
            raw_path,
            ledger,
            _truth(contract),
            contract,
            {"path": "contract.json", "sha256": "0" * 64},
        )


def test_parser_rejects_non_object_response_metadata(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, _, _ = modules
    contract = _contract()
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    ledger = _ledger(answer, bundle_root, contract)
    report = _promptfoo(contract)
    report["results"]["results"][0]["response"]["metadata"] = ["bad"]
    raw_path = tmp_path / "promptfoo-results.json"
    raw_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(answer.AnswerEvaluationError, match="malformed response metadata"):
        answer.prepare_answers(
            raw_path,
            ledger,
            _truth(contract),
            contract,
            {"path": "contract.json", "sha256": "0" * 64},
        )


def test_preparation_review_and_compact_aggregate_closed_contract(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, aggregate, _ = modules
    contract, _, _, tasks, mechanical, manifest, _, contract_path = _prepare(
        answer, importlib.import_module("_evaluation"), tmp_path
    )
    preparation = tmp_path / "prepared"
    preparation.mkdir()
    (preparation / "review-tasks.jsonl").write_text(
        answer.task_text(tasks), encoding="utf-8", newline="\n"
    )
    (preparation / "review-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (preparation / "mechanical-results.json").write_text(
        json.dumps(mechanical, indent=2) + "\n", encoding="utf-8"
    )
    validated_tasks, validated_manifest, validated_mechanical = answer.validate_preparation(
        preparation, contract, contract_path
    )
    reviews = []
    for task in validated_tasks:
        reviews.append(
            {
                "answer_id": task["answer_id"],
                "claim_fidelity": [{"index": 0, "score": 1}],
                "atomic_scores": {
                    item["id"]: 1 for item in task["ground_truth"]["answer_claims"]
                },
                "negative_scores": {
                    item["id"]: 1 for item in task["ground_truth"]["important_negatives"]
                },
                "note": "Faithful, complete, and grounded fixture.",
            }
        )
    review_report = {
        "schema_version": contract["review"]["schema_version"],
        "model": contract["review"]["model"],
        "blinded": True,
        "score_values": contract["review"]["score_values"],
        "task_sha256": validated_manifest["task_sha256"],
        "review_count": len(reviews),
        "implementation": {
            "reviewer": answer._implementation_binding(answer.REVIEWER),
        },
        "reviews": reviews,
    }
    answer.validate_review_report(
        review_report, validated_tasks, validated_manifest, contract
    )
    reviews_path = preparation / "reviews.json"
    reviews_path.write_text(json.dumps(review_report) + "\n", encoding="utf-8")
    summary = aggregate.build_summary(
        validated_mechanical,
        validated_manifest,
        validated_tasks,
        review_report,
        contract,
        preparation,
        reviews_path,
    )
    aggregate.validate_summary(summary, contract)
    assert all(set(profile["metrics"].values()) == {1.0} for profile in summary["aggregates"].values())
    assert all(set(delta["metrics"].values()) == {0.0} for delta in summary["paired_deltas"].values())
    encoded = json.dumps(summary)
    assert "Fixture claim." not in encoded
    assert "Faithful, complete" not in encoded
    markdown = aggregate.render_markdown(summary)
    assert markdown.startswith("# Semantic OKF Ensemble Answer-Output Evaluation")
    assert "## Stability diagnostics" in markdown
    assert "Strict full pass" in markdown
    assert summary["bundle"]["source_manifest_sha256"] == contract["bundle"][
        "source_manifest_sha256"
    ]
    assert summary["skill_arena"]["consult_skills"]
    assert set(summary["implementation"]) == {
        "mechanical_runtime",
        "preparer",
        "reviewer",
        "aggregator",
    }

    broken = copy.deepcopy(summary)
    broken["unknown"] = True
    with pytest.raises(answer.AnswerEvaluationError, match="closed schema"):
        aggregate.validate_summary(broken, contract)

    stale_contract = copy.deepcopy(summary)
    stale_contract["contract"]["sha256"] = "0" * 64
    with pytest.raises(answer.AnswerEvaluationError, match="current contract"):
        aggregate.validate_summary(stale_contract, contract)

    stale_skill = copy.deepcopy(summary)
    stale_skill["skill_arena"]["consult_skills"][1]["tree_sha256"] = "0" * 64
    with pytest.raises(answer.AnswerEvaluationError, match="skill bindings"):
        aggregate.validate_summary(stale_skill, contract)

    stale_implementation = copy.deepcopy(summary)
    stale_implementation["implementation"]["reviewer"]["sha256"] = "0" * 64
    with pytest.raises(answer.AnswerEvaluationError, match="current repository file"):
        aggregate.validate_summary(stale_implementation, contract)

    stale_source_manifest = copy.deepcopy(summary)
    stale_source_manifest["bundle"]["source_manifest_sha256"] = "0" * 64
    with pytest.raises(answer.AnswerEvaluationError, match="bundle binding"):
        aggregate.validate_summary(stale_source_manifest, contract)

    arithmetic_tampers = [
        (
            ("aggregates", "knowledge-only-control", "parseable_rate"),
            0.5,
            "aggregate arithmetic",
        ),
        (
            ("aggregates", "knowledge-only-control", "strict_full_pass_rate"),
            0.5,
            "aggregate arithmetic",
        ),
        (
            ("aggregates", "knowledge-only-control", "metrics", "grounding"),
            0.5,
            "aggregate arithmetic",
        ),
        (
            (
                "aggregates",
                "knowledge-only-control",
                "metric_population_stddev",
                "grounding",
            ),
            0.5,
            "aggregate arithmetic",
        ),
        (
            (
                "aggregates",
                "knowledge-only-control",
                "worst_question_metrics",
                "grounding",
            ),
            0.5,
            "aggregate arithmetic",
        ),
        (
            ("paired_deltas", "ensemble_vs_knowledge_only", "strict_full_pass_rate"),
            0.5,
            "paired-delta arithmetic",
        ),
        (
            ("paired_deltas", "ensemble_vs_knowledge_only", "metrics", "grounding"),
            0.5,
            "paired-delta arithmetic",
        ),
    ]
    for path, replacement, message in arithmetic_tampers:
        tampered = copy.deepcopy(summary)
        target = tampered
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = replacement
        with pytest.raises(answer.AnswerEvaluationError, match=message):
            aggregate.validate_summary(tampered, contract)


def test_review_validator_rejects_missing_atomic_identity(
    modules: tuple[ModuleType, ModuleType, ModuleType], tmp_path: Path
) -> None:
    answer, _, evaluation = modules
    contract, _, _, tasks, _, _, _, _ = _prepare(answer, evaluation, tmp_path)
    task = tasks[0]
    review = {
        "answer_id": task["answer_id"],
        "claim_fidelity": [{"index": 0, "score": 1}],
        "atomic_scores": {},
        "negative_scores": {
            item["id"]: 1 for item in task["ground_truth"]["important_negatives"]
        },
        "note": "Incomplete identity set.",
    }
    with pytest.raises(answer.AnswerEvaluationError, match="atomic identities differ"):
        answer.validate_review(review, task, contract)


def test_windows_reviewer_resolver_prefers_powershell_shim(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    reviewer = _load(
        "test_semantic_okf_answer_reviewer",
        SCRIPTS / "run_blinded_answer_reviews.py",
    )
    extensionless = tmp_path / "pi"
    powershell = tmp_path / "pi.ps1"
    extensionless.write_text("#!/bin/sh\n", encoding="utf-8")
    powershell.write_text("# PowerShell shim\n", encoding="utf-8")
    monkeypatch.setattr(reviewer, "WINDOWS", True)
    monkeypatch.setenv("PATH", str(tmp_path))

    assert reviewer._resolve_command("pi") == str(powershell.resolve())


def test_reviewer_json_parser_rejects_duplicate_keys() -> None:
    reviewer = _load(
        "test_semantic_okf_answer_reviewer_duplicate_keys",
        SCRIPTS / "run_blinded_answer_reviews.py",
    )

    with pytest.raises(reviewer.AnswerEvaluationError, match="duplicate reviewer output key"):
        reviewer._extract_json('{"reviews":[],"reviews":[]}')
