from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-endocrine-hygiene"
GENERATOR_PATH = EVALUATION_ROOT / "scripts" / "generate_skill_arena_config.py"
CONFIG_PATH = EVALUATION_ROOT / "skill-arena" / "classical-hard4.yaml"
MANIFEST_PATH = EVALUATION_ROOT / "skill-arena" / "classical-hard4-manifest.json"
PROMPT_COVERAGE_PATH = EVALUATION_ROOT / "skill-arena" / "prompt-coverage.json"


def _load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("endocrine_hygiene_arena_generator", GENERATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _embedded_json(script: str, variable: str, next_statement: str) -> Any:
    match = re.search(
        rf"const {re.escape(variable)} = (.*);\n  {re.escape(next_statement)}",
        script,
    )
    assert match, f"missing embedded {variable} ledger"
    return json.loads(match.group(1))


def _assertions(prompt: dict[str, Any]) -> dict[str, str]:
    return {
        assertion["metric"]: str(assertion["value"])
        for assertion in prompt["evaluation"]["assertions"]
    }


def _published_claim_ledger(generator: ModuleType) -> dict[str, dict[str, str]]:
    """Recreate deterministic published paths from the frozen source ledger."""

    ledger: dict[str, dict[str, str]] = {}
    for claim_id, item in generator.source_claim_ledger().items():
        source_id = f"claims-{Path(item['source_path']).stem.casefold()}"
        segment = f"{claim_id}-{hashlib.sha256(claim_id.encode('utf-8')).hexdigest()[:10]}"
        ledger[claim_id] = {
            "concept_path": f"concepts/{source_id}/{segment}.md",
            **item,
        }
    return ledger


def _run_javascript(script: str, output: dict[str, Any]) -> bool:
    program = (
        "const fs=require('node:fs');"
        "const p=JSON.parse(fs.readFileSync(0,'utf8'));"
        "const result=new Function('output',p.script)(p.output);"
        "process.stdout.write(JSON.stringify(result));"
    )
    completed = subprocess.run(
        ["node", "-e", program],
        input=json.dumps(
            {
                "script": script,
                "output": json.dumps(output, ensure_ascii=False, separators=(",", ":")),
            },
            ensure_ascii=False,
        ),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_all_reviewed_claims_and_exact_hard_requirements_are_derived() -> None:
    generator = _load_generator()
    ledger = generator.source_claim_ledger()
    truths = generator.hard_truth()
    requirements = generator.hard_claim_requirements(truths, ledger)
    source_row_count = sum(
        len(generator.load_jsonl(path))
        for path in sorted((EVALUATION_ROOT / "corpus" / "sources" / "claims").glob("PMC*.jsonl"))
    )

    assert len(ledger) == source_row_count == 93
    assert "claim-pmc6504186-008" in ledger
    assert "claim-pmc6504186-009" in ledger
    assert "claim-pmc9566193-007" in ledger
    assert list(requirements) == list(generator.PROMPT_IDS)
    assert set(generator.PROMPT_IDS) == {
        "q026-receptor-to-gestation-boundary",
        "q027-feminine-risk-reconciliation",
        "q028-phthalate-name-normalization",
        "q029-label-gate-validity",
        "q030-causal-evidence-map",
    }
    for question in requirements.values():
        for groups in question.values():
            for claim_ids in groups.values():
                assert claim_ids == sorted(set(claim_ids))
                assert all(claim_id in ledger for claim_id in claim_ids)


def test_prompt_assertions_bind_exact_interpretations_claim_ids_and_evidence() -> None:
    generator = _load_generator()
    ledger = _published_claim_ledger(generator)
    truths = generator.hard_truth()
    questions = generator.hard_questions()
    requirements = generator.hard_claim_requirements(truths, ledger)
    expected_interpretations = {
        claim_id: item["interpretation"] for claim_id, item in ledger.items()
    }

    for identifier in generator.PROMPT_IDS:
        value = generator.prompt(
            identifier,
            questions[identifier],
            truths[identifier],
            requirements[identifier],
            ledger,
        )
        assertions = _assertions(value)
        assert list(assertions) == [
            "response-contract",
            "evidence-validity",
            "claim-fidelity",
            "atomic-answer-completeness",
            "important-negative-coverage",
            "required-paper-coverage",
        ]
        assert "cite exactly one reviewed claim record ID" in value["prompt"]
        assert "copy that record's reviewed `interpretation` exactly as `statement`" in value["prompt"]

        fidelity = assertions["claim-fidelity"]
        assert "row.supporting_claim_ids.length !== 1" in fidelity
        assert "row.statement !== expected" in fidelity
        assert "new Set(claimIds).size !== claimIds.length" in fidelity
        assert "JSON.stringify(claimIds) === JSON.stringify(evidenceIds)" in fidelity
        assert _embedded_json(fidelity, "interpretations", "const claimIds") == expected_interpretations

        atomic = assertions["atomic-answer-completeness"]
        negative = assertions["important-negative-coverage"]
        assert _embedded_json(atomic, "groups", "return Object.values") == requirements[identifier]["answer_claims"]
        assert _embedded_json(negative, "groups", "return Object.values") == requirements[identifier]["important_negatives"]
        assert "claimIds.every((id) => used.has(id) && evidence.has(id))" in atomic
        assert "claimIds.every((id) => used.has(id) && evidence.has(id))" in negative

        papers = assertions["required-paper-coverage"]
        assert "actual.evidence.map((item) => item.paper_id)" in papers
        assert "JSON.stringify(actual.answer.paper_ids) !== JSON.stringify(derived)" in papers
        assert "required.every((paper) => derived.includes(paper))" in papers

    q029 = generator.prompt(
        generator.PROMPT_IDS[3],
        questions[generator.PROMPT_IDS[3]],
        truths[generator.PROMPT_IDS[3]],
        requirements[generator.PROMPT_IDS[3]],
        ledger,
    )
    q029_assertions = _assertions(q029)
    assert "claim-pmc9566193-007" in q029_assertions["atomic-answer-completeness"]
    assert "claim-pmc9566193-007" in q029_assertions["important-negative-coverage"]


def test_generated_javascript_accepts_exact_claim_rows_and_rejects_drift() -> None:
    if shutil.which("node") is None:
        pytest.skip("Node.js is required to execute Skill Arena JavaScript assertions.")
    generator = _load_generator()
    ledger = _published_claim_ledger(generator)
    truths = generator.hard_truth()
    questions = generator.hard_questions()
    requirements = generator.hard_claim_requirements(truths, ledger)
    identifier = "q029-label-gate-validity"
    prompt = generator.prompt(
        identifier,
        questions[identifier],
        truths[identifier],
        requirements[identifier],
        ledger,
    )
    assertions = _assertions(prompt)
    required_ids = sorted(
        {
            claim_id
            for groups in requirements[identifier].values()
            for claim_ids in groups.values()
            for claim_id in claim_ids
        }
    )
    evidence = [
        {
            "claim_id": claim_id,
            "concept_path": ledger[claim_id]["concept_path"],
            "paper_id": ledger[claim_id]["paper_id"],
            "source_path": ledger[claim_id]["source_path"],
            "evidence_locator": ledger[claim_id]["evidence_locator"],
            "evidence_text_sha256": ledger[claim_id]["evidence_text_sha256"],
        }
        for claim_id in required_ids
    ]
    exact = {
        "question_id": identifier,
        "answer": {
            "summary": " ".join(["evidence"] * 180),
            "claims": [
                {
                    "statement": ledger[claim_id]["interpretation"],
                    "supporting_claim_ids": [claim_id],
                }
                for claim_id in required_ids
            ],
            "paper_ids": sorted({item["paper_id"] for item in evidence}),
        },
        "evidence": evidence,
    }

    assert all(_run_javascript(script, exact) for script in assertions.values())

    wrong_statement = copy.deepcopy(exact)
    wrong_statement["answer"]["claims"][0]["statement"] += " Changed."
    assert not _run_javascript(assertions["claim-fidelity"], wrong_statement)

    multiple_ids = copy.deepcopy(exact)
    multiple_ids["answer"]["claims"][0]["supporting_claim_ids"].append(required_ids[1])
    assert not _run_javascript(assertions["claim-fidelity"], multiple_ids)

    wrong_evidence = copy.deepcopy(exact)
    wrong_evidence["evidence"][0]["evidence_text_sha256"] = "0" * 64
    assert not _run_javascript(assertions["evidence-validity"], wrong_evidence)

    declared_only = copy.deepcopy(exact)
    declared_only["answer"]["paper_ids"].append("PMC999999")
    declared_only["answer"]["paper_ids"].sort()
    assert not _run_javascript(assertions["required-paper-coverage"], declared_only)

    incomplete = copy.deepcopy(exact)
    omitted = requirements[identifier]["answer_claims"]["q029-a1"][0]
    incomplete["answer"]["claims"] = [
        row for row in incomplete["answer"]["claims"] if row["supporting_claim_ids"] != [omitted]
    ]
    incomplete["evidence"] = [row for row in incomplete["evidence"] if row["claim_id"] != omitted]
    assert not _run_javascript(assertions["atomic-answer-completeness"], incomplete)


def test_checked_config_is_a_five_prompt_single_surface_paired_comparison() -> None:
    generator = _load_generator()
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    prompt_ids = [prompt["id"] for prompt in config["task"]["prompts"]]

    assert config["benchmark"]["id"] == "semantic-okf-endocrine-hygiene-classical-hard5-paired"
    assert prompt_ids == list(generator.PROMPT_IDS)
    assert manifest["benchmark_id"] == config["benchmark"]["id"]
    assert manifest["prompt_ids"] == prompt_ids
    assert manifest["profiles"] == [
        "knowledge-only-control",
        "classical-cli-consult-treatment",
    ]
    assert manifest["reviewed_ledger_claim_count"] == len(generator.source_claim_ledger())
    assert manifest["varied_capability_surfaces"] == ["skills"]
    assert manifest["config"]["sha256"] == hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
    assert manifest["prompt_coverage"]["sha256"] == hashlib.sha256(
        PROMPT_COVERAGE_PATH.read_bytes()
    ).hexdigest()

    profiles = config["comparison"]["profiles"]
    assert profiles[0]["capabilities"] == {}
    assert set(profiles[1]["capabilities"]) == {"skills"}
    assert len(profiles[1]["capabilities"]["skills"]) == 1
    assert [variant["id"] for variant in config["comparison"]["variants"]] == ["pi-luna-only"]
    assert config["evaluation"]["requests"] == 1
    assert "mcp" not in json.dumps(config, ensure_ascii=False).casefold()
    assert config["workspace"]["sources"][0]["path"].endswith(
        "results/runs/20260715-endocrine-builds-05/bundles/classical-a"
    )

    for prompt in config["task"]["prompts"]:
        assert "claim-fidelity" in _assertions(prompt)
