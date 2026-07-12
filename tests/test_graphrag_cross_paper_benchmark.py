from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType

import yaml
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper"
GENERATOR = EVALUATION_ROOT / "scripts" / "generate_benchmark.py"
BUNDLE = EVALUATION_ROOT / "fixtures" / "workspaces" / "skill-overlay" / "knowledge"
SKILL_SNAPSHOT = (
    EVALUATION_ROOT
    / "fixtures"
    / "workspaces"
    / "skill-overlay"
    / "skills"
    / "consult-semantic-okf"
)
CANONICAL_SKILL = REPO_ROOT / "skills" / "consult-semantic-okf"
QUERY_HELPER = CANONICAL_SKILL / "scripts" / "query_semantic_okf.py"
HISTORICAL_EVOLUTION_TREE_SHA256 = (
    "53a1fa06419a27d8de3bfb67be24aa202eb0b815ff89a5b692d31e36591176fb"
)
HISTORICAL_ARTIFACT_SHA256 = {
    "baseline-report.md": "bb3cf10abe4a36b6f3ebf5d51ada7db3acac236b36eb255f81342146b9c04836",
    "holdout-improved-report.md": "30bbcb36941997659a2dac5bbb0bf7c895198f8fd6f93634109d91f82c8100d3",
    "live-run-status.md": "222ab4ee5b9c1693d8b68cd775ea4287b3be3b5793d0cbd179b9d9f06995d45f",
    "paired-holdout-evaluation.yaml": (
        "58f7f8f1b989e16f3dcdc675168d080b87103e61e4e1793beda9eac3061cd638"
    ),
    "paired-holdout-report.md": "7b5b6b049b0a499d718111d10a61ce37da34173fdf473e6193e63576c2c81a17",
    "smoke-report.md": "883003b4e4243b8743330800e3a0c3c1e53be30f0c30fefb4f438306634e1635",
}
SMOKE_IDS = {
    "q001-methodology-taxonomy",
    "q006-path-subgraph-reasoning",
    "q016-noise-redundancy",
    "q024-evaluation-practices",
    "q030-design-decision-framework",
}
HOLDOUT_IDS = {
    "q005-community-hierarchy",
    "q010-context-organization",
    "q015-incremental-updates",
    "q020-domain-adaptation",
    "q025-benchmark-bias",
    "q029-static-agentic-retrieval",
}
TECHNICAL_RECOVERY_IDS = {
    "q009-query-processing-routing",
    "q017-imperfect-graphs",
}
PROCESSOR = {
    "contract_version": "1.0",
    "name": "semantic-okf-python",
    "records": 874,
    "sources": 31,
}
FORBIDDEN_ENGINE_TERMS = re.compile(
    r"apache\s+spark|pyspark|py4j|sparkcontext|sparksession|--master|"
    r"spark-runtime|spark_pi|\bspark\b",
    re.IGNORECASE,
)


def load_generator() -> ModuleType:
    """Load the deterministic benchmark generator without packaging it."""

    spec = importlib.util.spec_from_file_location("graphrag_cross_paper_benchmark", GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_cross_source_helper() -> ModuleType:
    """Load the skill's read-only ranking helper for discovery regression checks."""

    scripts = CANONICAL_SKILL / "scripts"
    support_spec = importlib.util.spec_from_file_location(
        "_consult_semantic_okf", scripts / "_consult_semantic_okf.py"
    )
    assert support_spec and support_spec.loader
    support = importlib.util.module_from_spec(support_spec)
    sys.modules[support_spec.name] = support
    support_spec.loader.exec_module(support)
    cross_spec = importlib.util.spec_from_file_location(
        "graphrag_cross_source_helper", scripts / "_cross_source.py"
    )
    assert cross_spec and cross_spec.loader
    module = importlib.util.module_from_spec(cross_spec)
    sys.modules[cross_spec.name] = module
    cross_spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, object]:
    """Load one JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def load_questions() -> list[dict[str, object]]:
    """Load the generated question battery."""

    return [
        json.loads(line)
        for line in (EVALUATION_ROOT / "questions.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]


def source_files(root: Path) -> dict[str, str]:
    """Return normalized distributable text while excluding interpreter caches."""

    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8").replace(
            "\r\n", "\n"
        ).rstrip()
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.relative_to(root).parts
        and path.suffix != ".pyc"
    }


def test_question_battery_is_unique_cross_paper_and_fully_covered() -> None:
    blueprint = load_json(EVALUATION_ROOT / "questions-blueprint.json")
    questions = load_questions()
    coverage = load_json(EVALUATION_ROOT / "coverage.json")

    assert len(blueprint["questions"]) == 30
    assert len(questions) == 30
    assert [item["id"] for item in questions] == [
        item["id"] for item in blueprint["questions"]
    ]
    assert len({item["id"] for item in questions}) == 30
    assert len({item["question"] for item in questions}) == 30
    assert len({item["semantic_signature"] for item in questions}) == 30
    assert len({item["category"] for item in questions}) == 30

    focus_counts: Counter[str] = Counter()
    dimension_counts: Counter[str] = Counter()
    for question in questions:
        focus = question["focus_papers"]
        dimensions = question["dimensions"]
        evidence = question["paper_concept_paths"]
        assert isinstance(focus, list) and focus == sorted(set(focus))
        assert isinstance(dimensions, list) and dimensions
        assert isinstance(evidence, dict) and set(evidence) == set(focus)
        assert question["min_papers"] >= 3
        assert question["min_papers"] <= len(focus)
        assert len(question["required_points"]) >= 3
        for path in evidence.values():
            assert (BUNDLE / str(path)).is_file()
        focus_counts.update(focus)
        dimension_counts.update(dimensions)

    assert set(dimension_counts) == load_generator().CLAIM_KINDS
    assert min(focus_counts.values()) >= 8
    assert coverage["question_count"] == 30
    assert coverage["semantic_signature_count"] == 30
    assert coverage["smoke_question_count"] == 5
    assert coverage["holdout_question_count"] == 6
    assert coverage["skill_only_question_count"] == 30
    assert coverage["technical_recovery_question_count"] == 2
    assert coverage["paper_focus_counts"] == dict(sorted(focus_counts.items()))
    assert coverage["dimension_counts"] == dict(sorted(dimension_counts.items()))


def test_evidence_planner_covers_every_discovery_relevance_minimum() -> None:
    """Freeze the trace-derived selection gain without consulting the holdout split."""

    cross_source = load_cross_source_helper()
    catalog = cross_source.load_catalog(BUNDLE)
    blueprint = load_json(EVALUATION_ROOT / "questions-blueprint.json")
    checked = 0
    for question in blueprint["questions"]:
        if question["id"] in HOLDOUT_IDS:
            continue
        ranked = cross_source.rank_papers(
            catalog,
            question["question"],
            question["dimensions"],
        )
        eligible = [
            candidate
            for candidate in ranked
            if candidate["dimension_coverage"]
            and candidate["rank_components"]["matched_dimensions"] > 0
        ]
        selected = {
            candidate["paper_id"]
            for candidate in eligible[: question["min_papers"] + 5]
        }
        assert len(selected & set(question["focus_papers"])) >= question["min_papers"], (
            question["id"]
        )
        checked += 1
    assert checked == 24


def test_compare_configs_isolate_access_and_keep_the_requested_pi_model_route() -> None:
    full = yaml.safe_load((EVALUATION_ROOT / "evaluation.yaml").read_text(encoding="utf-8"))
    smoke = yaml.safe_load(
        (EVALUATION_ROOT / "smoke-evaluation.yaml").read_text(encoding="utf-8")
    )
    holdout = yaml.safe_load(
        (EVALUATION_ROOT / "holdout-evaluation.yaml").read_text(encoding="utf-8")
    )
    skill_only = yaml.safe_load(
        (EVALUATION_ROOT / "skill-only-evaluation.yaml").read_text(encoding="utf-8")
    )
    recovery = yaml.safe_load(
        (EVALUATION_ROOT / "technical-recovery-evaluation.yaml").read_text(
            encoding="utf-8"
        )
    )
    questions = load_questions()

    assert full["schemaVersion"] == 1
    assert full["benchmark"]["id"] == "graphrag-cross-paper-30-compare"
    assert [prompt["id"] for prompt in full["task"]["prompts"]] == [
        question["id"] for question in questions
    ]
    assert {prompt["id"] for prompt in smoke["task"]["prompts"]} == SMOKE_IDS
    assert len(smoke["task"]["prompts"]) == 5
    expected_holdout_ids = [question["id"] for question in questions if question["id"] in HOLDOUT_IDS]
    assert [prompt["id"] for prompt in holdout["task"]["prompts"]] == expected_holdout_ids
    assert holdout["benchmark"]["id"] == "graphrag-cross-paper-holdout-6-validation"
    assert len(holdout["task"]["prompts"]) == 6
    for config in (full, smoke):
        assert config["evaluation"]["timeoutMs"] == 600000
        assert config["evaluation"]["maxConcurrency"] == 2

    full_prompts = {prompt["id"]: prompt for prompt in full["task"]["prompts"]}
    assert holdout["task"]["prompts"] == [full_prompts[identifier] for identifier in expected_holdout_ids]
    assert holdout["evaluation"] == full["evaluation"]
    assert holdout["comparison"]["variants"] == full["comparison"]["variants"]
    assert len(holdout["comparison"]["profiles"]) == 1
    consultation = holdout["comparison"]["profiles"][0]
    assert consultation["id"] == "consult-skill"
    assert consultation["capabilities"] == full["comparison"]["profiles"][1]["capabilities"]
    assert consultation["output"]["labels"] == {
        "skill_state": "consult",
        "knowledge_access": "on",
        "split": "holdout",
    }
    assert skill_only["benchmark"]["id"] == (
        "graphrag-cross-paper-30-consult-skill-retest"
    )
    assert skill_only["task"]["prompts"] == full["task"]["prompts"]
    assert skill_only["comparison"]["variants"] == full["comparison"]["variants"]
    assert len(skill_only["comparison"]["profiles"]) == 1
    skill_only_profile = skill_only["comparison"]["profiles"][0]
    assert skill_only_profile["id"] == "consult-skill"
    assert skill_only_profile["capabilities"] == full["comparison"]["profiles"][1][
        "capabilities"
    ]
    assert skill_only_profile["output"]["labels"] == {
        "skill_state": "consult-evolved",
        "knowledge_access": "on",
        "evaluation_scope": "skill-only",
    }
    assert skill_only["evaluation"] == {
        **full["evaluation"],
        "maxConcurrency": 4,
    }
    assert recovery["benchmark"]["id"] == "graphrag-cross-paper-technical-recovery-2"
    assert {prompt["id"] for prompt in recovery["task"]["prompts"]} == (
        TECHNICAL_RECOVERY_IDS
    )
    assert len(recovery["comparison"]["profiles"]) == 1
    assert recovery["comparison"]["profiles"][0]["id"] == "consult-skill"
    assert recovery["comparison"]["profiles"][0]["output"]["labels"] == {
        "skill_state": "consult-evolved",
        "knowledge_access": "on",
        "evaluation_scope": "technical-recovery-only",
        "score_merge": "forbidden",
    }
    assert recovery["comparison"]["variants"][0]["agent"]["model"] == (
        "openai-codex/gpt-5.6-luna"
    )
    assert recovery["comparison"]["variants"][0]["agent"]["cliEnv"] == {
        "PI_MODEL_TIMEOUT_SECONDS": "360"
    }
    assert recovery["evaluation"]["maxConcurrency"] == 2

    control, treatment = full["comparison"]["profiles"]
    assert control["id"] == "no-skill"
    assert control["isolation"] == {"inheritSystem": False}
    assert control["capabilities"] == {}
    assert treatment["id"] == "consult-skill"
    assert treatment["isolation"] == {"inheritSystem": False}
    installed = treatment["capabilities"]["skills"][0]
    assert installed == {
        "source": {
            "type": "local-path",
            "path": "evaluations/graphrag-cross-paper/fixtures/workspaces/skill-overlay",
            "skillId": "consult-semantic-okf",
        },
        "install": {"strategy": "workspace-overlay"},
    }

    variant = full["comparison"]["variants"][0]
    assert variant["id"] == "pi-luna-only"
    assert variant["agent"]["adapter"] == "pi"
    assert variant["agent"]["model"] == "openai-codex/gpt-5.6-luna"
    assert variant["agent"]["commandPath"] == "bin/pi-luna.ps1"
    assert variant["agent"]["cliEnv"] == {
        "PI_MODEL_TIMEOUT_SECONDS": "240",
    }
    assert variant["agent"]["webSearchEnabled"] is False
    assert variant["agent"]["sandboxMode"] == "read-only"
    assert variant["output"] == {
        "tags": ["pi", "gpt-5.6-luna", "luna-only", "isolated"],
        "labels": {
            "variantDisplayName": "PI GPT-5.6 Luna",
            "adapter_family": "pi",
            "model": "openai-codex/gpt-5.6-luna",
            "routing": "luna-only",
        },
    }

    luna_wrapper = (
        EVALUATION_ROOT
        / "fixtures"
        / "workspaces"
        / "base"
        / "bin"
        / "pi-luna.ps1"
    ).read_text(encoding="utf-8")
    assert 'Get-Command "pi.ps1"' in luna_wrapper
    assert 'Get-Command "pi.cmd"' not in luna_wrapper
    assert 'openai-codex/gpt-5.6-luna' in luna_wrapper
    assert "fallback" not in luna_wrapper.lower()

    question_by_id = {question["id"]: question for question in questions}
    for prompt in full["task"]["prompts"]:
        assert "Use only that snapshot; do not use the web" in prompt["prompt"]
        assert "use the ledger for discovery" in prompt["prompt"]
        question = question_by_id[prompt["id"]]
        required_dimensions = json.dumps(sorted(question["dimensions"]))
        assert f"required controlled claim-kind ID {required_dimensions}" in prompt["prompt"]
        assert f"at least {question['min_papers']} independent papers" in prompt["prompt"]
        assert "paper-specific claim concepts both count" in prompt["prompt"]
        assertions = prompt["evaluation"]["assertions"]
        assert [item["metric"] for item in assertions] == [
            "semantic-structure",
            "page-citation-grounding",
            "cross-paper-evidence",
        ]

    active_route_files = [
        GENERATOR,
        EVALUATION_ROOT / "evaluation.yaml",
        EVALUATION_ROOT / "smoke-evaluation.yaml",
        EVALUATION_ROOT / "holdout-evaluation.yaml",
        EVALUATION_ROOT / "skill-only-evaluation.yaml",
        EVALUATION_ROOT / "technical-recovery-evaluation.yaml",
        EVALUATION_ROOT / "scope.md",
        EVALUATION_ROOT / "fixtures" / "workspaces" / "base" / "bin" / "pi-luna.ps1",
    ]
    for path in active_route_files:
        route_text = path.read_text(encoding="utf-8")
        assert "gpt-5.6" in route_text.lower(), path
        assert "gpt-5.3" not in route_text.lower(), path
        assert "PI_FALLBACK" not in route_text, path


def test_luna_wrapper_is_single_attempt_strict_and_long_prompt_safe(tmp_path: Path) -> None:
    if os.name != "nt":
        pytest.skip("The benchmark wrapper is Windows-specific.")

    wrapper = (
        EVALUATION_ROOT
        / "fixtures"
        / "workspaces"
        / "base"
        / "bin"
        / "pi-luna.ps1"
    )
    fake_pi = tmp_path / "pi.ps1"
    fake_pi.write_text(
        "[IO.File]::AppendAllText($env:PI_TEST_LOG, \"call`n\")\n"
        "if ($env:PI_TEST_SLEEP_SECONDS) { Start-Sleep -Seconds ([int] $env:PI_TEST_SLEEP_SECONDS) }\n"
        "if ($env:PI_TEST_EXIT_CODE) { exit ([int] $env:PI_TEST_EXIT_CODE) }\n"
        "Write-Output \"ok\"\n"
        "exit 0\n",
        encoding="utf-8",
    )
    log = tmp_path / "calls.log"
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}{os.pathsep}{env['PATH']}"
    env["PI_TEST_LOG"] = str(log)
    env["PI_MODEL_TIMEOUT_SECONDS"] = "10"

    def invoke(*arguments: str, overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        call_env = env | (overrides or {})
        return subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(wrapper),
                *arguments,
            ],
            cwd=REPO_ROOT,
            env=call_env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    long_prompt = "x" * 12000
    valid = invoke("--model", "openai-codex/gpt-5.6-luna", long_prompt)
    assert valid.returncode == 0
    assert valid.stdout.strip() == "ok"
    assert "routing=luna-only" in valid.stderr
    assert log.read_text(encoding="utf-8").splitlines() == ["call"]

    wrong = invoke("--model", "example/not-luna")
    assert wrong.returncode == 64
    assert "refusing non-Luna model" in wrong.stderr
    duplicate = invoke(
        "--model",
        "openai-codex/gpt-5.6-luna",
        "--model",
        "example/not-luna",
    )
    assert duplicate.returncode == 64
    assert "exactly one --model" in duplicate.stderr
    assert log.read_text(encoding="utf-8").splitlines() == ["call"]

    failed = invoke(
        "--model",
        "openai-codex/gpt-5.6-luna",
        overrides={"PI_TEST_EXIT_CODE": "7"},
    )
    assert failed.returncode == 7
    assert "failed=true exit=7" in failed.stderr
    assert log.read_text(encoding="utf-8").splitlines() == ["call", "call"]

    timed_out = invoke(
        "--model",
        "openai-codex/gpt-5.6-luna",
        overrides={"PI_TEST_SLEEP_SECONDS": "5", "PI_MODEL_TIMEOUT_SECONDS": "1"},
    )
    assert timed_out.returncode == 124
    assert "timed out after 1 seconds" in timed_out.stderr
    assert log.read_text(encoding="utf-8").splitlines() == ["call", "call", "call"]


def test_treatment_overlay_is_reader_only_and_matches_the_canonical_consult_skill() -> None:
    build_report = load_json(BUNDLE / "semantic" / "build-report.json")
    source_manifest = load_json(BUNDLE / "semantic" / "source-manifest.json")

    assert build_report["valid"] is True
    assert build_report["status"] == "pass"
    assert build_report["processor"] == PROCESSOR
    assert source_manifest["processor"] == PROCESSOR
    assert "spark" not in build_report
    assert "spark" not in source_manifest
    assert len(source_manifest["sources"]) == 31
    smoke_report = EVALUATION_ROOT / "smoke-report.md"
    if smoke_report.exists():
        report_text = smoke_report.read_text(encoding="utf-8")
        assert report_text.startswith("# graphrag-cross-paper-30-compare")
        assert "Five-question live rehearsal" in report_text

    assert source_files(SKILL_SNAPSHOT) == source_files(CANONICAL_SKILL)
    assert not list(SKILL_SNAPSHOT.rglob("__pycache__"))
    assert not (SKILL_SNAPSHOT / "scripts" / "build_semantic_okf.py").exists()
    assert not (SKILL_SNAPSHOT / "scripts" / "refresh_semantic_okf.py").exists()
    assert not (SKILL_SNAPSHOT / "scripts" / "validate_semantic_okf.py").exists()
    assert not (SKILL_SNAPSHOT / "references" / "manifest.md").exists()
    assert "name: consult-semantic-okf" in (SKILL_SNAPSHOT / "SKILL.md").read_text(
        encoding="utf-8"
    )
    for path in SKILL_SNAPSHOT.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert FORBIDDEN_ENGINE_TERMS.search(text) is None, path
        assert re.search(r"\b\d{4}[.-]\d{5}v\d+\b", text) is None, path

    question_ids = re.compile(
        "|".join(re.escape(str(question["id"])) for question in load_questions())
    )
    for path in SKILL_SNAPSHOT.rglob("*"):
        if path.is_file():
            assert question_ids.search(path.read_text(encoding="utf-8", errors="ignore")) is None


def test_treatment_bundle_contains_all_papers_claims_and_query_layers() -> None:
    records = [
        json.loads(line)
        for line in (BUNDLE / "semantic" / "records.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]

    assert len(records) == 874
    assert Counter(record["concept_type"] for record in records) == Counter(
        {"Paper Semantic Claim": 831, "Analysis Term": 28, "Research Paper": 15}
    )
    assert len({record["record_id"] for record in records}) == 874
    assert len({record["concept_path"] for record in records}) == 874
    for record in records:
        assert (BUNDLE / record["concept_path"]).is_file()

    expected_semantic = {
        "build-report.json",
        "data.ttl",
        "ontology.ttl",
        "provenance.ttl",
        "records.jsonl",
        "semantic-plan.json",
        "shapes.ttl",
        "source-manifest.json",
        "validation-report.ttl",
    }
    assert {path.name for path in (BUNDLE / "semantic").iterdir() if path.is_file()} == (
        expected_semantic
    )


def test_competency_queries_return_the_reviewed_cross_paper_views() -> None:
    expected_counts = {
        "claim-coverage.rq": 13,
        "method-task-evidence.rq": 78,
        "paper-dimension-coverage.rq": 15,
        "retrieval-evidence.rq": 141,
    }
    for query_name, expected_count in expected_counts.items():
        completed = subprocess.run(
            [
                sys.executable,
                str(QUERY_HELPER),
                str(BUNDLE),
                "sparql",
                "--query-file",
                str(EVALUATION_ROOT / "queries" / query_name),
                "--graph",
                "data",
                "--format",
                "json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert completed.returncode == 0, f"{query_name}: {completed.stderr}"
        result = json.loads(completed.stdout)
        assert result["status"] == "pass"
        assert result["returned"] == expected_count
        assert result["truncated"] is False


def test_generator_is_reproducible_and_snapshot_hashes_are_current() -> None:
    completed = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, f"{completed.stdout}\n{completed.stderr}"

    generator = load_generator()
    coverage = load_json(EVALUATION_ROOT / "coverage.json")
    assert coverage["snapshot_tree_sha256"] == generator.tree_sha256(BUNDLE)
    assert coverage["skill_id"] == "consult-semantic-okf"
    assert coverage["skill_snapshot_tree_sha256"] == generator.tree_sha256(SKILL_SNAPSHOT)
    assert "baseline_skill_snapshot_tree_sha256" not in coverage
    assert coverage["record_count"] == 874
    assert coverage["paper_count"] == 15
    assert coverage["skill_only_question_count"] == 30
    assert coverage["technical_recovery_question_count"] == 2


def test_pre_split_evolution_and_reports_are_frozen_historical_artifacts() -> None:
    scope = (EVALUATION_ROOT / "scope.md").read_text(encoding="utf-8")
    assert "## Historical evaluation artifacts" in scope
    assert "immutable historical evidence" in scope

    for relative, expected_sha256 in HISTORICAL_ARTIFACT_SHA256.items():
        assert hashlib.sha256((EVALUATION_ROOT / relative).read_bytes()).hexdigest() == (
            expected_sha256
        )

    generator = load_generator()
    evolution = EVALUATION_ROOT / "evolution" / "luna-2026-07-12"
    assert generator.tree_sha256(evolution) == HISTORICAL_EVOLUTION_TREE_SHA256
    assert EVALUATION_ROOT / "paired-holdout-evaluation.yaml" not in generator.build_outputs()
