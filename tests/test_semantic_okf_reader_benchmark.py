from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-reader"
GENERATOR = EVALUATION_ROOT / "scripts" / "generate_benchmark.py"
LUNA_FALLBACK_BUILDER = EVALUATION_ROOT / "scripts" / "build_luna_fallback.py"
TECHNICAL_RESUME_BUILDER = (
    EVALUATION_ROOT / "scripts" / "build_technical_resume.py"
)
TECHNICAL_MERGE_BUILDER = (
    EVALUATION_ROOT / "scripts" / "merge_technical_results.py"
)
SEMANTIC_MERGE_BUILDER = (
    EVALUATION_ROOT / "scripts" / "merge_semantic_results.py"
)
ACTIVE_BASE = EVALUATION_ROOT / "fixtures" / "workspaces" / "base-v2"
ACTIVE_OVERLAY = EVALUATION_ROOT / "fixtures" / "workspaces" / "reader-v2-overlay"
BUNDLE = ACTIVE_OVERLAY / "knowledge"
HISTORICAL_V1_BASE = EVALUATION_ROOT / "fixtures" / "workspaces" / "base"
HISTORICAL_V1_OVERLAY = EVALUATION_ROOT / "fixtures" / "workspaces" / "skill-overlay"

EXPECTED_CATEGORIES = {
    "typed-fact": 40,
    "relation-traversal": 40,
    "multi-hop-join": 50,
    "typed-filter": 40,
    "aggregation": 45,
    "provenance-lineage": 40,
    "ontology-shacl": 20,
    "integrity-negative": 15,
    "bundle-inventory": 10,
}
EXPECTED_DIFFICULTIES = {"easy": 80, "medium": 120, "hard": 100}
EXPECTED_SNAPSHOT_TREE_SHA256 = (
    "d1071f6f53b8df9bef5e1ea37b69b9efdb3ed8d5fe5ec4d9496ad7e28259fe43"
)
EXPECTED_SKILL_SNAPSHOT_TREE_SHA256 = (
    "5d4f0f3eafa9d68d82dfa698b53b281cb6930d05bc1ef7f0c12bd44eaacaf73a"
)
SMOKE_IDS = {
    "q006-typed-fact",
    "q081-multi-hop-join",
    "q171-aggregation",
    "q216-provenance-lineage",
    "q276-integrity-negative",
}


def load_generator() -> ModuleType:
    """Load the deterministic benchmark generator without packaging it."""

    spec = importlib.util.spec_from_file_location("semantic_okf_reader_benchmark", GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_luna_fallback_builder() -> ModuleType:
    """Load the Luna fallback manifest builder without packaging it."""

    spec = importlib.util.spec_from_file_location(
        "semantic_okf_reader_luna_fallback", LUNA_FALLBACK_BUILDER
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_technical_resume_builder() -> ModuleType:
    """Load the technical resume manifest builder without packaging it."""

    spec = importlib.util.spec_from_file_location(
        "semantic_okf_reader_technical_resume", TECHNICAL_RESUME_BUILDER
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_technical_merge_builder() -> ModuleType:
    """Load the canonical technical-result merger without packaging it."""

    spec = importlib.util.spec_from_file_location(
        "semantic_okf_reader_technical_merge", TECHNICAL_MERGE_BUILDER
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_semantic_merge_builder() -> ModuleType:
    """Load the semantic-fallback result merger without packaging it."""

    spec = importlib.util.spec_from_file_location(
        "semantic_okf_reader_semantic_merge", SEMANTIC_MERGE_BUILDER
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_questions() -> list[dict[str, object]]:
    """Read the hidden JSONL battery."""

    return [
        json.loads(line)
        for line in (EVALUATION_ROOT / "questions.jsonl").read_text(encoding="utf-8").splitlines()
    ]


def javascript_json_value(value: object) -> object:
    """Mirror JavaScript JSON.stringify number normalization for assertion hashes."""

    if isinstance(value, str):
        if re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
            value,
        ):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return (
                parsed.astimezone(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z")
            )
        return value
    if isinstance(value, bool) or value is None or isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, list):
        return [javascript_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): javascript_json_value(item) for key, item in value.items()}
    raise TypeError(type(value).__name__)


def result_sha256(value: object) -> str:
    normalized = javascript_json_value(value)
    return hashlib.sha256(
        json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def test_semantic_question_bank_is_complete_unique_and_grounded() -> None:
    questions = load_questions()

    assert len(questions) == 300
    assert [question["id"].split("-", 1)[0] for question in questions] == [
        f"q{index:03d}" for index in range(1, 301)
    ]
    assert len({question["id"] for question in questions}) == 300
    assert len({question["question"] for question in questions}) == 300
    assert len({question["semantic_signature"] for question in questions}) == 300
    assert len(
        {
            json.dumps(
                question["semantic_descriptor"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            for question in questions
        }
    ) == 300
    assert Counter(question["category"] for question in questions) == Counter(EXPECTED_CATEGORIES)
    assert Counter(question["difficulty"] for question in questions) == Counter(
        EXPECTED_DIFFICULTIES
    )

    for question in questions:
        signature = str(question["semantic_signature"])
        assert len(signature) == 64
        int(signature, 16)
        descriptor = question["semantic_descriptor"]
        descriptor_json = json.dumps(
            descriptor,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        assert "question" not in descriptor_json
        assert set(descriptor) == {"graph_scope", "operation", "semantics"}
        assert hashlib.sha256(descriptor_json.encode("utf-8")).hexdigest() == signature
        expected = question["expected"]
        assert isinstance(expected, dict)
        value = expected["value"]
        actual_digest = result_sha256(value)
        evidence = question["evidence"]
        assert isinstance(evidence, dict)
        assert evidence["result_sha256"] == actual_digest
        assert evidence["accepted_sets"]
        assert evidence["accepted_set_sha256"] == sorted(
            result_sha256(sorted(items)) for items in evidence["accepted_sets"]
        )
        evidence_sets = [frozenset(items) for items in evidence["accepted_sets"]]
        assert all(
            not left > right
            for left in evidence_sets
            for right in evidence_sets
            if left is not right
        )
        for evidence_set in evidence["accepted_sets"]:
            assert evidence_set == sorted(evidence_set)
            assert len(evidence_set) == len(set(evidence_set))
            for locator in evidence_set:
                locator = str(locator)
                assert (BUNDLE / locator).is_file()
        oracle = question["oracle"]
        assert isinstance(oracle, dict)
        assert set(oracle) == {"entailment", "graph_scope", "operation"}
        assert oracle["entailment"] == "none"
        assert oracle["graph_scope"]


def test_compare_configs_encode_isolated_pi_access_without_gold_leakage() -> None:
    full = yaml.safe_load((EVALUATION_ROOT / "evaluation.yaml").read_text(encoding="utf-8"))
    smoke = yaml.safe_load(
        (EVALUATION_ROOT / "smoke-evaluation.yaml").read_text(encoding="utf-8")
    )
    questions = load_questions()

    assert full["schemaVersion"] == 1
    assert full["benchmark"]["id"] == "semantic-okf-reader-v2-300-compare"
    assert "active v2" in full["benchmark"]["description"]
    assert len(full["task"]["prompts"]) == 300
    assert [prompt["id"] for prompt in full["task"]["prompts"]] == [
        question["id"] for question in questions
    ]
    assert [profile["id"] for profile in full["comparison"]["profiles"]] == [
        "no-skill",
        "skill",
    ]
    control, treatment = full["comparison"]["profiles"]
    assert control["isolation"] == {"inheritSystem": False}
    assert control["capabilities"] == {}
    assert treatment["isolation"] == {"inheritSystem": False}
    skill = treatment["capabilities"]["skills"][0]
    assert skill["source"] == {
        "type": "local-path",
        "path": "evaluations/semantic-okf-reader/fixtures/workspaces/reader-v2-overlay",
        "skillId": "consult-semantic-okf",
    }
    assert skill["install"] == {"strategy": "workspace-overlay"}
    assert full["evaluation"] == {
        "assertions": full["evaluation"]["assertions"],
        "requests": 1,
        "timeoutMs": 600000,
        "tracing": False,
        "maxConcurrency": 4,
        "noCache": True,
    }
    assert [item["type"] for item in full["evaluation"]["assertions"]] == [
        "is-json",
        "javascript",
        "javascript",
    ]
    assert [item["metric"] for item in full["evaluation"]["assertions"]] == [
        "response-format",
        "response-contract",
        "evidence-path-validity",
    ]
    for prompt, question in zip(full["task"]["prompts"], questions, strict=True):
        assertions = prompt["evaluation"]["assertions"]
        assert [item["metric"] for item in assertions] == [
            "semantic-accuracy",
            "evidence-grounding",
        ]
        assert question["evidence"]["result_sha256"] in assertions[0]["value"]
        for evidence_set in question["evidence"]["accepted_sets"]:
            for path in evidence_set:
                assert path in assertions[1]["value"]
    variant = full["comparison"]["variants"][0]
    assert variant["id"] == "pi-luna-only"
    assert variant["agent"] == {
        "adapter": "pi",
        "model": "openai-codex/gpt-5.6-luna",
        "executionMethod": "command",
        "commandPath": "bin/pi-luna.ps1",
        "sandboxMode": "read-only",
        "approvalPolicy": "never",
        "webSearchEnabled": False,
        "networkAccessEnabled": True,
        "reasoningEffort": "medium",
        "additionalDirectories": [],
        "cliEnv": {
            "PI_MODEL_TIMEOUT_SECONDS": "240",
        },
        "config": {},
    }
    assert variant["output"] == {
        "tags": ["pi", "gpt-5.6-luna", "luna-only", "isolated", "v2"],
        "labels": {
            "variantDisplayName": "PI GPT-5.6 Luna",
            "adapter_family": "pi",
            "model": "openai-codex/gpt-5.6-luna",
            "routing": "luna-only",
            "benchmark_generation": "v2",
        },
    }

    assert smoke["benchmark"]["id"] == "semantic-okf-reader-v2-smoke-compare"
    assert {prompt["id"] for prompt in smoke["task"]["prompts"]} == SMOKE_IDS
    assert smoke["evaluation"]["maxConcurrency"] == 4

    base = ACTIVE_BASE
    overlay = ACTIVE_OVERLAY
    assert {
        path.relative_to(base).as_posix() for path in base.rglob("*") if path.is_file()
    } == {"README.md", "bin/pi-luna.ps1"}
    assert {path.name for path in overlay.iterdir()} == {"knowledge", "skills"}
    assert (overlay / "knowledge" / "semantic" / "records.jsonl").is_file()
    assert {path.name for path in (overlay / "skills").iterdir()} == {
        "consult-semantic-okf"
    }
    assert (overlay / "skills" / "consult-semantic-okf" / "SKILL.md").is_file()
    assert not (overlay / "skills" / "build-semantic-okf").exists()

    installed_skill = overlay / "skills" / "consult-semantic-okf"
    assert (installed_skill / "scripts" / "query_semantic_okf.py").is_file()
    assert not (installed_skill / "scripts" / "build_semantic_okf.py").exists()
    assert not (installed_skill / "scripts" / "refresh_semantic_okf.py").exists()
    generator = load_generator()
    assert (
        generator.snapshot_tree_sha256(installed_skill)
        == EXPECTED_SKILL_SNAPSHOT_TREE_SHA256
    )
    question_id_pattern = re.compile(
        "|".join(re.escape(str(question["id"])) for question in questions)
    )
    for path in overlay.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert question_id_pattern.search(text) is None, path

    active_files = [GENERATOR, EVALUATION_ROOT / "evaluation.yaml", EVALUATION_ROOT / "smoke-evaluation.yaml"]
    for path in active_files:
        active_text = path.read_text(encoding="utf-8")
        assert "gpt-5.3" not in active_text.lower(), path
        assert "pi-spark-luna-fallback" not in active_text.lower(), path
        assert "skillId: build-semantic-okf" not in active_text, path

    assert (HISTORICAL_V1_BASE / "bin" / "pi-spark-luna-fallback.ps1").is_file()
    assert (HISTORICAL_V1_OVERLAY / "skills" / "build-semantic-okf" / "SKILL.md").is_file()


def test_generator_is_reproducible_and_snapshot_is_pinned() -> None:
    check = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert check.returncode == 0, f"{check.stdout}\n{check.stderr}"
    assert "300 questions" in check.stdout

    generator = load_generator()
    coverage = json.loads((EVALUATION_ROOT / "coverage.json").read_text(encoding="utf-8"))
    assert coverage["schema_version"] == "2.0"
    assert coverage["benchmark_generation"] == "v2"
    assert coverage["question_count"] == 300
    assert coverage["expanded_executions"] == 600
    assert coverage["smoke_expanded_executions"] == 10
    assert coverage["profiles"] == ["no-skill", "skill"]
    assert coverage["variants"] == ["pi-luna-only"]
    assert set(coverage["smoke_question_ids"]) == SMOKE_IDS
    assert coverage["snapshot"] == {
        "plan_sha256": "8ee36a7417482796829f8e6495843ff28d33af1fef1bf3e5b1f3343575fc0e13",
        "record_count": 60,
        "source_count": 40,
        "tree_sha256": EXPECTED_SNAPSHOT_TREE_SHA256,
    }
    assert coverage["skill_snapshot"] == {
        "skill_id": "consult-semantic-okf",
        "tree_sha256": EXPECTED_SKILL_SNAPSHOT_TREE_SHA256,
    }
    assert generator.PINNED_SNAPSHOT_TREE_SHA256 == EXPECTED_SNAPSHOT_TREE_SHA256
    assert (
        generator.PINNED_SKILL_SNAPSHOT_TREE_SHA256
        == EXPECTED_SKILL_SNAPSHOT_TREE_SHA256
    )
    assert generator.snapshot_tree_sha256(BUNDLE) == EXPECTED_SNAPSHOT_TREE_SHA256
    build_report = json.loads(
        (BUNDLE / "semantic" / "build-report.json").read_text(encoding="utf-8")
    )
    assert build_report["valid"] is True
    assert build_report["summary"]["shacl"] == "conformant"
    assert build_report["errors"] == []
    assert build_report["warnings"] == []


def test_generated_javascript_scores_answers_evidence_and_abstention_separately() -> None:
    full = yaml.safe_load((EVALUATION_ROOT / "evaluation.yaml").read_text(encoding="utf-8"))
    questions = load_questions()
    response_contract = full["evaluation"]["assertions"][1]["value"]
    evidence_path_validity = full["evaluation"]["assertions"][2]["value"]
    cases: list[dict[str, object]] = []

    for prompt, question in zip(full["task"]["prompts"], questions, strict=True):
        accuracy, grounding = prompt["evaluation"]["assertions"]
        answered = json.dumps(
            {
                "question_id": question["id"],
                "answer": question["expected"]["value"],
                "evidence": question["evidence"]["accepted_sets"][0],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        abstained = json.dumps(
            {"question_id": question["id"], "answer": None, "evidence": []},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        cases.extend(
            [
                {"code": response_contract, "output": answered, "expected": True},
                {"code": evidence_path_validity, "output": answered, "expected": True},
                {"code": accuracy["value"], "output": answered, "expected": True},
                {"code": grounding["value"], "output": answered, "expected": True},
                {"code": response_contract, "output": abstained, "expected": True},
                {"code": evidence_path_validity, "output": abstained, "expected": True},
                {"code": accuracy["value"], "output": abstained, "expected": False},
                {"code": grounding["value"], "output": abstained, "expected": True},
            ]
        )
        for evidence_set in question["evidence"]["accepted_sets"][1:]:
            alternative = json.dumps(
                {
                    "question_id": question["id"],
                    "answer": question["expected"]["value"],
                    "evidence": evidence_set,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            cases.append({"code": grounding["value"], "output": alternative, "expected": True})
            cases.append(
                {"code": evidence_path_validity, "output": alternative, "expected": True}
            )
        for evidence_set in question["evidence"]["accepted_sets"]:
            if len(evidence_set) > 1:
                unsorted = json.dumps(
                    {
                        "question_id": question["id"],
                        "answer": question["expected"]["value"],
                        "evidence": list(reversed(evidence_set)),
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                cases.append(
                    {"code": grounding["value"], "output": unsorted, "expected": False}
                )
        redundant = json.dumps(
            {
                "question_id": question["id"],
                "answer": question["expected"]["value"],
                "evidence": sorted(
                    {*question["evidence"]["accepted_sets"][0], "index.md"}
                ),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        cases.append({"code": grounding["value"], "output": redundant, "expected": True})
        cases.append(
            {"code": evidence_path_validity, "output": redundant, "expected": True}
        )
        prefixed = json.dumps(
            {
                "question_id": question["id"],
                "answer": question["expected"]["value"],
                "evidence": [
                    f"knowledge/{path}"
                    for path in question["evidence"]["accepted_sets"][0]
                ],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        cases.append({"code": grounding["value"], "output": prefixed, "expected": True})
        cases.append(
            {"code": evidence_path_validity, "output": prefixed, "expected": True}
        )
        invalid = json.dumps(
            {
                "question_id": question["id"],
                "answer": question["expected"]["value"],
                "evidence": sorted(
                    {*question["evidence"]["accepted_sets"][0], "semantic/not-real.ttl"}
                ),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        cases.append(
            {"code": evidence_path_validity, "output": invalid, "expected": False}
        )

    runner = """
const fs = require('node:fs');
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
for (let index = 0; index < cases.length; index += 1) {
  const item = cases[index];
  const actual = new Function('output', item.code)(item.output);
  if (actual !== item.expected) {
    console.error(JSON.stringify({index, expected: item.expected, actual}));
    process.exit(1);
  }
}
"""
    result = subprocess.run(
        ["node", "-e", runner],
        input=json.dumps(cases, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_snapshot_hash_normalizes_git_line_endings(tmp_path: Path) -> None:
    generator = load_generator()
    lf = tmp_path / "lf"
    crlf = tmp_path / "crlf"
    lf.mkdir()
    crlf.mkdir()
    (lf / "record.jsonl").write_bytes(b'{"id":1}\n{"id":2}\n')
    (crlf / "record.jsonl").write_bytes(b'{"id":1}\r\n{"id":2}\r\n')

    assert generator.snapshot_tree_sha256(lf) == generator.snapshot_tree_sha256(crlf)


def test_answer_hash_normalizes_equivalent_utc_datetime_lexical_forms() -> None:
    generator = load_generator()
    expected = {"updatedAt": "2026-01-15T12:30:00.000Z"}

    assert generator.result_sha256(expected) == generator.result_sha256(
        {"updatedAt": "2026-01-15T12:30:00+00:00"}
    )
    assert generator.result_sha256(expected) == generator.result_sha256(
        {"updatedAt": "2026-01-15T13:30:00+01:00"}
    )


def test_luna_fallback_selects_complete_failed_skill_cells_by_prompt_id() -> None:
    builder = load_luna_fallback_builder()
    primary = {
        "benchmark": {"id": "semantic"},
        "task": {
            "prompts": [
                {"id": "q001", "prompt": "first"},
                {"id": "q002", "prompt": "second"},
                {"id": "q003", "prompt": "third"},
            ]
        },
    }

    def row(prompt_id: str, prompt: str, success: bool) -> dict[str, object]:
        return {
            "provider": {"id": "skill"},
            "success": success,
            "metadata": {
                "benchmarkId": "semantic",
                "promptId": prompt_id,
                "profileId": "skill",
            },
            "vars": {"taskPrompt": prompt},
            "response": {"output": '{"answer": 1}'},
        }

    rows = [
        row("q003", "third", False),
        {"provider": {"id": "no-skill"}, "success": False},
        row("q001", "first", True),
        row("q002", "second", False),
    ]

    assert builder.failed_prompt_ids(primary, rows) == ["q002", "q003"]


def test_luna_fallback_maps_indices_and_builds_exact_retry_config() -> None:
    builder = load_luna_fallback_builder()
    prompts = [
        {"id": "q001", "prompt": "first", "evaluation": {"assertions": ["a"]}},
        {"id": "q002", "prompt": "second", "evaluation": {"assertions": ["b"]}},
        {"id": "q003", "prompt": "third", "evaluation": {"assertions": ["c"]}},
    ]
    skill_profile = {
        "id": "skill",
        "description": "Treatment",
        "capabilities": {"skills": [{"source": {"type": "local-path"}}]},
        "isolation": {"inheritSystem": False},
    }
    primary = {
        "schemaVersion": 1,
        "benchmark": {
            "id": "semantic-okf-reader-smoke-compare",
            "description": "Primary",
            "tags": ["semantic-okf", "pi"],
        },
        "task": {"prompts": prompts},
        "comparison": {
            "profiles": [
                {
                    "id": "no-skill",
                    "description": "Control",
                    "capabilities": {},
                    "isolation": {"inheritSystem": False},
                },
                skill_profile,
            ],
            "variants": [{"id": "spark-primary"}],
        },
        "evaluation": {
            "assertions": [{"type": "is-json"}],
            "requests": 1,
            "timeoutMs": 240000,
            "tracing": False,
            "maxConcurrency": 1,
            "noCache": False,
        },
    }

    fallback = builder.build_fallback_config(primary, ["q001", "q003"])

    assert primary["task"]["prompts"] == prompts
    assert fallback["schemaVersion"] == 1
    assert fallback["benchmark"] == {
        "id": "semantic-okf-reader-300-luna-semantic-fallback",
        "description": "Retry failed Semantic OKF treatment cells with PI GPT-5.6 Luna.",
        "tags": ["semantic-okf", "pi", "luna", "semantic-fallback"],
    }
    assert fallback["task"]["prompts"] == [prompts[0], prompts[2]]
    assert fallback["comparison"]["profiles"] == [skill_profile]
    assert fallback["comparison"]["variants"] == [
        {
            "id": "pi-openrouter-gpt56-luna-semantic-fallback",
            "description": (
                "PI GPT-5.6 Luna semantic fallback for treatment cells that failed the "
                "initial model route."
            ),
            "agent": {
                "adapter": "pi",
                "model": "openrouter/openai/gpt-5.6-luna",
                "executionMethod": "command",
                "commandPath": "bin/pi-spark-luna-fallback.ps1",
                "sandboxMode": "read-only",
                "approvalPolicy": "never",
                "webSearchEnabled": False,
                "networkAccessEnabled": True,
                "reasoningEffort": "low",
                "additionalDirectories": [],
                "cliEnv": {
                    "OPENROUTER_API_KEY": "$HOST_ENV:OPENROUTER_API_KEY",
                    "PI_FALLBACK_MODEL": "openrouter/openai/gpt-5.6-luna",
                    "PI_MODEL_TIMEOUT_SECONDS": "90",
                },
                "config": {},
            },
            "output": {
                "tags": ["pi", "gpt-5.6-luna", "semantic-fallback", "isolated"],
                "labels": {
                    "variantDisplayName": "PI GPT-5.6 Luna fallback",
                    "adapter_family": "pi",
                    "retry_model": "openrouter/openai/gpt-5.6-luna",
                    "fallback_reason": "failed-complete-treatment-cell",
                },
            },
        }
    ]
    assert fallback["evaluation"] == {
        "assertions": [{"type": "is-json"}],
        "requests": 1,
        "timeoutMs": 240000,
        "tracing": False,
        "maxConcurrency": 2,
        "noCache": True,
    }


def test_luna_fallback_requires_results_from_the_exact_source_manifest() -> None:
    builder = load_luna_fallback_builder()
    primary = {
        "benchmark": {"id": "semantic-smoke"},
        "task": {"prompts": [{"id": "q001", "prompt": "exact prompt"}]},
    }
    row = {
        "provider": {"id": "skill"},
        "testIdx": 0,
        "success": False,
        "metadata": {"benchmarkId": "semantic-smoke", "promptId": "q001"},
        "vars": {"taskPrompt": "exact prompt"},
        "response": {"output": '{"answer": 1}'},
    }

    builder.validate_results_binding(primary, [row])

    mismatched = json.loads(json.dumps(row))
    mismatched["metadata"]["promptId"] = "q171"
    try:
        builder.validate_results_binding(primary, [mismatched])
    except ValueError as exc:
        assert "unknown prompt ID" in str(exc)
    else:
        raise AssertionError("mismatched results/config binding was accepted")


def _technical_resume_primary() -> dict[str, object]:
    prompts = [
        {"id": "q001", "prompt": "first", "evaluation": {"assertions": ["a"]}},
        {"id": "q002", "prompt": "second", "evaluation": {"assertions": ["b"]}},
        {"id": "q003", "prompt": "third", "evaluation": {"assertions": ["c"]}},
        {"id": "q004", "prompt": "fourth", "evaluation": {"assertions": ["d"]}},
    ]
    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": "semantic-okf-reader-300-compare",
            "description": "Primary",
            "tags": ["semantic-okf", "pi"],
        },
        "task": {"prompts": prompts},
        "comparison": {
            "profiles": [
                {
                    "id": "no-skill",
                    "description": "Control",
                    "capabilities": {},
                    "isolation": {"inheritSystem": False},
                },
                {
                    "id": "skill",
                    "description": "Treatment",
                    "capabilities": {"skills": [{"source": {"type": "local-path"}}]},
                    "isolation": {"inheritSystem": False},
                },
            ],
            "variants": [{"id": "spark-primary"}],
        },
        "evaluation": {
            "assertions": [{"type": "is-json"}],
            "requests": 1,
            "timeoutMs": 240000,
            "tracing": False,
            "maxConcurrency": 4,
            "noCache": False,
        },
    }


def _technical_resume_row(
    prompt_id: str,
    prompt: str,
    profile_id: str,
    *,
    output: object = '{"answer": 1}',
    error: object = None,
    success: bool = True,
) -> dict[str, object]:
    return {
        "provider": {"id": profile_id},
        "metadata": {
            "benchmarkId": "semantic-okf-reader-300-compare",
            "promptId": prompt_id,
            "profileId": profile_id,
            "variantId": "spark-primary",
        },
        "vars": {"taskPrompt": prompt},
        "response": {"output": output, "error": error},
        "success": success,
    }


def test_technical_resume_classifies_response_transport_not_assertion_success() -> None:
    builder = load_technical_resume_builder()
    primary = _technical_resume_primary()
    prompts = primary["task"]["prompts"]
    rows: list[dict[str, object]] = []
    for profile_id in ("skill", "no-skill"):
        rows.extend(
            [
                # A failed assertion is still technically complete when output exists.
                _technical_resume_row(
                    "q001", "first", profile_id, success=False
                ),
                # Assertion success cannot make blank output technically complete.
                _technical_resume_row(
                    "q002", "second", profile_id, output="   ", success=True
                ),
                _technical_resume_row(
                    "q003", "third", profile_id, output='{"answer": 3}'
                ),
                # A response error wins even if output and assertion success are present.
                _technical_resume_row(
                    "q004",
                    "fourth",
                    profile_id,
                    output='{"answer": 4}',
                    error="provider unavailable",
                    success=True,
                ),
            ]
        )
    rows.reverse()

    prompt_ids, profile_ids = builder.technical_error_prompt_ids(primary, rows)

    assert prompt_ids == ["q002", "q004"]
    assert profile_ids == ["no-skill", "skill"]
    assert [item["id"] for item in prompts] == ["q001", "q002", "q003", "q004"]


def test_technical_resume_requires_exact_result_manifest_binding() -> None:
    builder = load_technical_resume_builder()
    primary = _technical_resume_primary()
    base = _technical_resume_row("q001", "first", "no-skill")
    mutations = [
        (lambda row: row["metadata"].__setitem__("benchmarkId", "another-benchmark")),
        (lambda row: row["metadata"].__setitem__("promptId", "q999")),
        (lambda row: row["metadata"].__setitem__("profileId", "skill")),
        (lambda row: row["metadata"].__setitem__("variantId", "another-variant")),
        (lambda row: row["vars"].__setitem__("taskPrompt", "changed prompt")),
    ]

    for mutate in mutations:
        row = json.loads(json.dumps(base))
        mutate(row)
        try:
            builder.technical_error_prompt_ids(primary, [row])
        except ValueError:
            pass
        else:
            raise AssertionError(f"mismatched result binding was accepted: {row}")

    duplicate = json.loads(json.dumps(base))
    try:
        builder.technical_error_prompt_ids(primary, [base, duplicate])
    except ValueError as exc:
        assert "duplicate result cell" in str(exc)
    else:
        raise AssertionError("duplicate result cell was accepted")


def test_technical_resume_rejects_different_error_masks_between_profiles() -> None:
    builder = load_technical_resume_builder()
    primary = _technical_resume_primary()
    rows = [
        _technical_resume_row("q001", "first", "no-skill", output=""),
        _technical_resume_row("q001", "first", "skill"),
    ]

    try:
        builder.technical_error_prompt_ids(primary, rows)
    except ValueError as exc:
        assert "technical error masks differ by profile" in str(exc)
        assert "no-skill=4" in str(exc)
        assert "skill=3" in str(exc)
    else:
        raise AssertionError("different technical error masks were accepted")


def test_technical_resume_builds_ordered_one_attempt_luna_manifest() -> None:
    builder = load_technical_resume_builder()
    primary = _technical_resume_primary()

    resume = builder.build_resume_config(primary, ["q004", "q002"])

    assert [item["id"] for item in resume["task"]["prompts"]] == ["q004", "q002"]
    assert [item["id"] for item in resume["comparison"]["profiles"]] == [
        "no-skill",
        "skill",
    ]
    assert len(resume["comparison"]["variants"]) == 1
    variant = resume["comparison"]["variants"][0]
    assert variant["id"] == "pi-openai-gpt56-luna-technical-resume"
    assert variant["agent"]["model"] == "openrouter/openai/gpt-5.6-luna"
    assert variant["agent"]["cliEnv"] == {
        "OPENROUTER_API_KEY": "$HOST_ENV:OPENROUTER_API_KEY",
        "PI_FALLBACK_MODEL": "openrouter/openai/gpt-5.6-luna",
        "PI_MODEL_TIMEOUT_SECONDS": "90",
    }
    assert (
        variant["agent"]["model"]
        == variant["agent"]["cliEnv"]["PI_FALLBACK_MODEL"]
    )
    assert resume["evaluation"]["maxConcurrency"] == 2
    assert resume["evaluation"]["noCache"] is True
    assert primary["evaluation"]["maxConcurrency"] == 4
    assert primary["evaluation"]["noCache"] is False


def _technical_merge_primary() -> dict[str, object]:
    return {
        "benchmark": {"id": "semantic-primary"},
        "task": {
            "prompts": [
                {"id": "q001", "prompt": "first"},
                {"id": "q002", "prompt": "second"},
            ]
        },
        "comparison": {
            "profiles": [{"id": "no-skill"}, {"id": "skill"}],
            "variants": [{"id": "spark-primary"}],
        },
    }


def _technical_merge_row(
    prompt_id: str,
    prompt: str,
    profile_id: str,
    *,
    benchmark_id: str = "semantic-primary",
    variant_id: str = "spark-primary",
    test_idx: int = 0,
    output: str = '{"answer": 1}',
    error: str | None = None,
    success: bool = True,
) -> dict[str, object]:
    metadata = {
        "benchmarkId": benchmark_id,
        "promptId": prompt_id,
        "profileId": profile_id,
        "skillModeId": profile_id,
        "variantId": variant_id,
        "variantDisplayName": variant_id,
        "rowId": f"{variant_id}:{prompt_id}",
    }
    variables = {
        "taskPrompt": prompt,
        "variantId": variant_id,
        "variantDisplayName": variant_id,
    }
    response: dict[str, object] = {"output": output, "metadata": {}}
    if error is not None:
        response["error"] = error
    return {
        "provider": {"id": profile_id, "label": profile_id},
        "metadata": metadata,
        "vars": variables,
        "testCase": {"metadata": metadata, "vars": variables},
        "testIdx": test_idx,
        "promptIdx": 0 if profile_id == "no-skill" else 1,
        "response": response,
        "success": success,
        "score": 1 if success else 0,
    }


def _technical_merge_document(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "evalId": "evaluation",
        "results": {
            "timestamp": "2026-01-01T00:00:00.000Z",
            "results": rows,
            "prompts": [
                {"provider": "no-skill", "metrics": {"tokenUsage": {}}},
                {"provider": "skill", "metrics": {"tokenUsage": {}}},
            ],
            "stats": {
                "successes": 0,
                "failures": 0,
                "errors": 0,
                "tokenUsage": {"numRequests": len(rows)},
                "durationMs": 10,
                "evaluationDurationMs": 10,
            },
        },
        "metadata": {},
    }


def _technical_merge_attempt_config(
    primary: dict[str, object],
    *,
    benchmark_id: str,
    variant_id: str,
    profile_ids: list[str],
) -> dict[str, object]:
    attempt = json.loads(json.dumps(primary))
    attempt["benchmark"]["id"] = benchmark_id
    attempt["task"]["prompts"] = [primary["task"]["prompts"][1]]
    attempt["comparison"]["profiles"] = [
        profile
        for profile in primary["comparison"]["profiles"]
        if profile["id"] in profile_ids
    ]
    attempt["comparison"]["variants"] = [{"id": variant_id}]
    return attempt


def test_technical_merge_selects_first_complete_attempt_and_restores_identity(
    tmp_path: Path,
) -> None:
    builder = load_technical_merge_builder()
    primary = _technical_merge_primary()
    primary_rows = [
        _technical_merge_row("q001", "first", "no-skill", success=False),
        _technical_merge_row("q001", "first", "skill"),
        _technical_merge_row(
            "q002", "second", "no-skill", test_idx=1, output="", error="quota", success=False
        ),
        _technical_merge_row(
            "q002", "second", "skill", test_idx=1, output="", error="quota", success=False
        ),
    ]
    resume_rows = [
        _technical_merge_row(
            "q002",
            "second",
            "no-skill",
            benchmark_id="semantic-resume",
            variant_id="luna-resume",
            success=False,
        ),
        _technical_merge_row(
            "q002",
            "second",
            "skill",
            benchmark_id="semantic-resume",
            variant_id="luna-resume",
            output="",
            error="timeout",
            success=False,
        ),
    ]
    retry_rows = [
        _technical_merge_row(
            "q002",
            "second",
            "skill",
            benchmark_id="semantic-resume-retry",
            variant_id="luna-resume",
        )
    ]
    paths = [tmp_path / name for name in ("primary.json", "resume.json", "retry.json")]
    config_paths = [
        tmp_path / name for name in ("primary.yaml", "resume.yaml", "retry.yaml")
    ]
    for path in [*paths, *config_paths]:
        path.write_text("fixture", encoding="utf-8")
    resume_config = _technical_merge_attempt_config(
        primary,
        benchmark_id="semantic-resume",
        variant_id="luna-resume",
        profile_ids=["no-skill", "skill"],
    )
    retry_config = _technical_merge_attempt_config(
        primary,
        benchmark_id="semantic-resume-retry",
        variant_id="luna-resume",
        profile_ids=["skill"],
    )

    merged, audit = builder.merge_results(
        primary,
        _technical_merge_document(primary_rows),
        [
            _technical_merge_document(resume_rows),
            _technical_merge_document(retry_rows),
        ],
        resume_configs=[resume_config, retry_config],
        source_paths=paths,
        source_config_paths=config_paths,
    )

    rows = merged["results"]["results"]
    assert [(row["metadata"]["promptId"], row["provider"]["id"]) for row in rows] == [
        ("q001", "no-skill"),
        ("q001", "skill"),
        ("q002", "no-skill"),
        ("q002", "skill"),
    ]
    assert [row["testIdx"] for row in rows] == [0, 0, 1, 1]
    retried = rows[-1]
    assert retried["metadata"]["benchmarkId"] == "semantic-primary"
    assert retried["metadata"]["variantId"] == "spark-primary"
    assert retried["vars"]["variantId"] == "spark-primary"
    assert retried["metadata"]["technicalMerge"] == {
        "sourceIndex": 2,
        "sourceRole": "resume-2",
        "sourceFile": paths[2].resolve().as_posix(),
        "sourceBenchmarkId": "semantic-resume-retry",
        "sourceVariantId": "luna-resume",
        "sourceTestIdx": 0,
    }
    assert merged["results"]["stats"]["successes"] == 2
    assert merged["results"]["stats"]["failures"] == 2
    assert merged["results"]["stats"]["errors"] == 0
    assert merged["results"]["stats"]["tokenUsage"]["numRequests"] == 4
    assert audit["canonical_cell_count"] == 4
    assert audit["selected_source_counts"] == {
        "primary": 2,
        "resume-1": 1,
        "resume-2": 1,
    }


def test_technical_merge_rejects_unresolved_and_mismatched_cells(
    tmp_path: Path,
) -> None:
    builder = load_technical_merge_builder()
    primary = _technical_merge_primary()
    rows = [
        _technical_merge_row("q001", "first", "no-skill"),
        _technical_merge_row("q001", "first", "skill"),
        _technical_merge_row("q002", "second", "no-skill", output="", error="quota"),
        _technical_merge_row("q002", "second", "skill", output="", error="quota"),
    ]
    paths = [tmp_path / "primary.json", tmp_path / "resume.json"]
    config_paths = [tmp_path / "primary.yaml", tmp_path / "resume.yaml"]
    for path in [*paths, *config_paths]:
        path.write_text("fixture", encoding="utf-8")
    resume_config = _technical_merge_attempt_config(
        primary,
        benchmark_id="semantic-resume",
        variant_id="luna-resume",
        profile_ids=["no-skill", "skill"],
    )
    incomplete_resume_rows = [
        _technical_merge_row(
            "q002",
            "second",
            profile_id,
            benchmark_id="semantic-resume",
            variant_id="luna-resume",
            output="",
            error="timeout",
            success=False,
        )
        for profile_id in ("no-skill", "skill")
    ]

    try:
        builder.merge_results(
            primary,
            _technical_merge_document(rows),
            [_technical_merge_document(incomplete_resume_rows)],
            resume_configs=[resume_config],
            source_paths=paths,
            source_config_paths=config_paths,
        )
    except ValueError as exc:
        assert "unresolved cells" in str(exc)
    else:
        raise AssertionError("unresolved technical cells were accepted")

    mismatched = _technical_merge_row("q002", "changed", "skill")
    try:
        builder.index_result_rows(
            _technical_merge_document([mismatched]),
            path=paths[1],
            prompt_by_id={"q001": {"id": "q001", "prompt": "first"}, "q002": {"id": "q002", "prompt": "second"}},
            profile_ids=["no-skill", "skill"],
        )
    except ValueError as exc:
        assert "prompt text mismatch" in str(exc)
    else:
        raise AssertionError("mismatched resume prompt text was accepted")


def test_semantic_merge_overlays_only_bound_failed_skill_cells(tmp_path: Path) -> None:
    builder = load_semantic_merge_builder()
    primary = _technical_merge_primary()
    primary_rows = [
        _technical_merge_row("q001", "first", "no-skill", success=False),
        _technical_merge_row("q001", "first", "skill"),
        _technical_merge_row("q002", "second", "no-skill", test_idx=1, success=False),
        _technical_merge_row("q002", "second", "skill", test_idx=1, success=False),
    ]
    fallback = _technical_merge_attempt_config(
        primary,
        benchmark_id="semantic-fallback",
        variant_id="luna-fallback",
        profile_ids=["skill"],
    )
    fallback_rows = [
        _technical_merge_row(
            "q002",
            "second",
            "skill",
            benchmark_id="semantic-fallback",
            variant_id="luna-fallback",
        )
    ]
    primary_path = tmp_path / "primary.json"
    fallback_path = tmp_path / "fallback.json"
    primary_path.write_text("fixture", encoding="utf-8")
    fallback_path.write_text("fixture", encoding="utf-8")

    merged, audit = builder.merge_semantic_results(
        primary,
        _technical_merge_document(primary_rows),
        fallback,
        _technical_merge_document(fallback_rows),
        primary_path=primary_path,
        fallback_path=fallback_path,
    )

    rows = merged["results"]["results"]
    selected = rows[-1]
    assert selected["success"] is True
    assert selected["testIdx"] == 1
    assert selected["metadata"]["benchmarkId"] == "semantic-primary"
    assert selected["metadata"]["variantId"] == "spark-primary"
    assert selected["metadata"]["semanticFallback"]["sourceRole"] == "semantic-fallback"
    assert merged["results"]["stats"] == {
        **merged["results"]["stats"],
        "successes": 2,
        "failures": 2,
        "errors": 0,
    }
    assert audit["fallback_cell_count"] == 1
    assert audit["fallback_pass_count"] == 1
    assert audit["fallback_fail_count"] == 0


def test_semantic_merge_rejects_success_target_and_incomplete_fallback(
    tmp_path: Path,
) -> None:
    builder = load_semantic_merge_builder()
    primary = _technical_merge_primary()
    fallback = _technical_merge_attempt_config(
        primary,
        benchmark_id="semantic-fallback",
        variant_id="luna-fallback",
        profile_ids=["skill"],
    )
    primary_path = tmp_path / "primary.json"
    fallback_path = tmp_path / "fallback.json"
    primary_path.write_text("fixture", encoding="utf-8")
    fallback_path.write_text("fixture", encoding="utf-8")

    for original_success, fallback_output, fallback_error, message in (
        (True, '{"answer": 1}', None, "targeted a successful"),
        (False, "", "timeout", "technically incomplete"),
    ):
        primary_rows = [
            _technical_merge_row("q001", "first", "no-skill", success=False),
            _technical_merge_row("q001", "first", "skill"),
            _technical_merge_row("q002", "second", "no-skill", success=False),
            _technical_merge_row(
                "q002", "second", "skill", success=original_success
            ),
        ]
        fallback_rows = [
            _technical_merge_row(
                "q002",
                "second",
                "skill",
                benchmark_id="semantic-fallback",
                variant_id="luna-fallback",
                output=fallback_output,
                error=fallback_error,
                success=False,
            )
        ]
        try:
            builder.merge_semantic_results(
                primary,
                _technical_merge_document(primary_rows),
                fallback,
                _technical_merge_document(fallback_rows),
                primary_path=primary_path,
                fallback_path=fallback_path,
            )
        except ValueError as exc:
            assert message in str(exc)
        else:
            raise AssertionError(f"invalid semantic fallback was accepted: {message}")


def test_active_v2_luna_wrapper_is_single_attempt_and_strict(tmp_path: Path) -> None:
    wrapper = ACTIVE_BASE / "bin" / "pi-luna.ps1"
    fake_pi = tmp_path / "pi.ps1"
    fake_pi.write_text(
        '[IO.File]::AppendAllText($env:PI_TEST_LOG, "call`n")\n'
        "if ($env:PI_TEST_SLEEP_SECONDS) { Start-Sleep -Seconds ([int] $env:PI_TEST_SLEEP_SECONDS) }\n"
        "if ($env:PI_TEST_EXIT_CODE) { exit ([int] $env:PI_TEST_EXIT_CODE) }\n"
        'Write-Output "ok"\n'
        "exit 0\n",
        encoding="utf-8",
    )
    log = tmp_path / "calls.log"
    environment = os.environ.copy()
    environment["PATH"] = f"{tmp_path}{os.pathsep}{environment['PATH']}"
    environment["PI_TEST_LOG"] = str(log)
    environment["PI_MODEL_TIMEOUT_SECONDS"] = "10"

    def invoke(
        *arguments: str, overrides: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
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
            env=environment | (overrides or {}),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    valid = invoke("--model", "openai-codex/gpt-5.6-luna", "x" * 12000)
    assert valid.returncode == 0
    assert valid.stdout.strip() == "ok"
    assert "routing=luna-only" in valid.stderr
    assert log.read_text(encoding="utf-8").splitlines() == ["call"]

    wrong = invoke("--model", "example/not-luna")
    assert wrong.returncode == 64
    assert "refusing non-Luna model" in wrong.stderr
    duplicate = invoke(
        "--model", "openai-codex/gpt-5.6-luna", "--model", "example/not-luna"
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


def test_historical_v1_wrapper_preserves_spark_to_luna_fallback_behavior(
    tmp_path: Path,
) -> None:
    """Keep the completed v1 experiment reproducible without making it active."""

    wrapper = (
        HISTORICAL_V1_BASE / "bin" / "pi-spark-luna-fallback.ps1"
    )
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    invocation_log = tmp_path / "pi-invocations.txt"
    fake_pi = fake_bin / "pi.cmd"
    fake_pi.write_text(
        """@echo off
echo %*>>"%FAKE_PI_LOG%"
echo %* | findstr /C:"openai-codex/gpt-5.3-codex-spark" >nul
if %ERRORLEVEL%==0 (
  if "%FAKE_PRIMARY_HANG%"=="1" (
    ping 127.0.0.1 -n 10 >nul
  )
  if "%FAKE_PRIMARY_SUCCESS%"=="1" (
    echo {"route":"primary"}
    exit /b 0
  )
  if "%FAKE_PRIMARY_UNICODE%"=="1" (
    python -c "import sys;sys.stdout.buffer.write(bytes.fromhex('7b22726f757465223a227072696d617279222c2274657874223a22cf8020e2809420e69d8ee99bb720f09f9a80227d'))"
    exit /b 0
  )
  echo primary failed 1>&2
  exit /b 42
)
echo %* | findstr /C:"openai-codex/gpt-5.6-luna" >nul
if %ERRORLEVEL%==0 (
  echo {"route":"fallback"}
  exit /b 0
)
exit /b 43
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"
    environment["FAKE_PI_LOG"] = str(invocation_log)
    environment["PI_FALLBACK_MODEL"] = "openai-codex/gpt-5.6-luna"
    command = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(wrapper),
        "--model",
        "openai-codex/gpt-5.3-codex-spark",
        "--no-skills",
        "-p",
        "test prompt",
    ]

    fallback = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert fallback.returncode == 0, fallback.stderr
    assert json.loads(fallback.stdout) == {"route": "fallback"}
    assert "fallback-triggered=true exit=42" in fallback.stderr
    assert "skill-arena-model=openai-codex/gpt-5.6-luna fallback=true" in fallback.stderr
    invocations = invocation_log.read_text(encoding="utf-8")
    assert "openai-codex/gpt-5.3-codex-spark" in invocations
    assert "openai-codex/gpt-5.6-luna" in invocations

    invocation_log.unlink()
    environment["FAKE_PRIMARY_SUCCESS"] = "1"
    primary = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert primary.returncode == 0, primary.stderr
    assert json.loads(primary.stdout) == {"route": "primary"}
    assert "fallback=false" in primary.stderr
    assert "openai-codex/gpt-5.6-luna" not in invocation_log.read_text(encoding="utf-8")

    invocation_log.unlink()
    environment.pop("FAKE_PRIMARY_SUCCESS")
    environment["FAKE_PRIMARY_UNICODE"] = "1"
    unicode_result = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=30,
    )
    assert unicode_result.returncode == 0, unicode_result.stderr
    assert json.loads(unicode_result.stdout) == {
        "route": "primary",
        "text": "π — 李雷 🚀",
    }

    invocation_log.unlink()
    environment.pop("FAKE_PRIMARY_UNICODE")
    environment["FAKE_PRIMARY_HANG"] = "1"
    environment["PI_MODEL_TIMEOUT_SECONDS"] = "3"
    environment["PI_FALLBACK_TIMEOUT_SECONDS"] = "10"
    timed_out = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    assert timed_out.returncode == 0, timed_out.stderr
    assert json.loads(timed_out.stdout) == {"route": "fallback"}
    assert "fallback-triggered=true exit=124" in timed_out.stderr
    assert "timed out after 3 seconds" in timed_out.stderr

    invocation_log.unlink()
    environment.pop("FAKE_PRIMARY_HANG")
    environment.pop("PI_FALLBACK_TIMEOUT_SECONDS")
    environment["PI_MODEL_TIMEOUT_SECONDS"] = "10"
    environment["PI_FALLBACK_MODEL"] = "openai-codex/gpt-5.3-codex-spark"
    same_model = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    assert same_model.returncode == 42
    assert "fallback-skipped=same-model" in same_model.stderr
    assert len(invocation_log.read_text(encoding="utf-8").splitlines()) == 1
