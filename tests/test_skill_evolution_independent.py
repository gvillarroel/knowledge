"""Independent synthetic checks of the deterministic Harbor bridge contract."""
from __future__ import annotations

import asyncio
import copy
import hashlib
import importlib.util
import json
import math
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tmp/evolution-independent-audit"


def load_module(name, path):
    specification = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


verifier = load_module("independent_evolution_verifier", ROOT / "evaluations/skill-evolution/verifier.py")


class IndependentScorer:
    """Compute the four published retrieval metrics on synthetic records only."""

    @staticmethod
    def metrics(hits, relevant):
        positions = [position for position, hit in enumerate(hits, 1) if hit["record_id"] in relevant]
        gain = sum(1 / math.log2(position + 1) for position in positions)
        maximum = sum(1 / math.log2(position + 1) for position in range(1, min(len(relevant), 10) + 1))
        return {
            "recall_at_10": len(positions) / len(relevant),
            "mrr_at_10": 1 / positions[0] if positions else 0,
            "ndcg_at_10": gain / maximum,
            "full_qrel_coverage_at_10": float(len(positions) == len(relevant)),
        }


@pytest.fixture
def audit_directory():
    AUDIT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="pytest-", dir=AUDIT))


@pytest.fixture
def trial():
    records = {
        key: {
            "record_id": key,
            "record_sha256": key * 64,
            "source_id": "manuals",
            "concept_id": "concept-" + key,
            "concept_path": "concepts/" + key + ".md",
        }
        for key in ("a", "b", "c")
    }
    queries = [
        {"id": "orchard", "hits": [{**records[key], "rank": position} for position, key in enumerate(("a", "b", "c"), 1)], "milliseconds": 3.0},
        {"id": "weaving", "hits": [{**records[key], "rank": position} for position, key in enumerate(("c", "a", "b"), 1)], "milliseconds": 4.0},
    ]
    skill_files = {"SKILL.md": "d" * 64, "assets/families/classical/consultant/scripts/_classical_snapshot.py": "e" * 64}
    imported = {"assets/families/classical/consultant/scripts/_classical_snapshot.py": "e" * 64}
    answer = {
        "schema_version": "skill-retrieval-trial/1.0", "family": "classical",
        "primary_route": "fusion", "builds_byte_identical": True,
        "record_identities": records, "routes": {"fusion": {"queries": queries, "p95_ms": 4.0}},
        "build_seconds": 2.0, "knowledge_bytes": 100, "skill_files": skill_files,
        "imported_candidate_modules": imported, "knowledge_files": {"semantic/records.jsonl": "f" * 64},
        "plan_sha256": "0" * 64, "llm_calls": 0, "answer_quality_evaluated": False,
    }
    contract = {
        "family": "classical", "primary_route": "fusion", "routes": ["fusion"],
        "records": {key: record["record_sha256"] for key, record in records.items()},
        "record_identities": copy.deepcopy(records),
        "skill_files": copy.deepcopy(skill_files),
        "imported_candidate_modules": copy.deepcopy(imported),
        "questions": [{"id": "orchard", "relevant": ["a", "b"]}, {"id": "weaving", "relevant": ["c"]}],
    }
    return answer, contract


def test_independent_scoring_accounts_for_order_and_irrelevant_hits(trial):
    answer, contract = trial
    rewards, diagnostics = verifier.evaluate(answer, contract, IndependentScorer)
    assert rewards["reward"] == rewards["mrr_at_10"] == rewards["recall_at_10"] == 1
    hits = answer["routes"]["fusion"]["queries"][0]["hits"]
    hits[:] = [hits[2], hits[0], hits[1]]
    for position, hit in enumerate(hits, 1):
        hit["rank"] = position
    observed, _ = verifier.evaluate(answer, contract, IndependentScorer)
    expected_ndcg = ((1 / math.log2(3) + 1 / math.log2(4)) / (1 + 1 / math.log2(3)) + 1) / 2
    assert observed["reward"] == pytest.approx(expected_ndcg)
    assert observed["mrr_at_10"] == 0.75
    assert observed["recall_at_10"] == 1
    assert diagnostics["question_count"] == 2


@pytest.mark.parametrize("field,value", [("source_id", "invented"), ("concept_id", "invented"), ("concept_path", "../../outside.md")])
def test_coordinated_answer_evidence_drift_is_rejected(trial, field, value):
    answer, contract = trial
    answer["record_identities"]["a"][field] = value
    for row in answer["routes"]["fusion"]["queries"]:
        for hit in row["hits"]:
            if hit["record_id"] == "a":
                hit[field] = value
    with pytest.raises(ValueError):
        verifier.evaluate(answer, contract, IndependentScorer)


@pytest.mark.parametrize("value", [1, "false", [True]])
def test_determinism_claim_requires_boolean_true(trial, value):
    answer, contract = trial
    answer["builds_byte_identical"] = value
    with pytest.raises(ValueError):
        verifier.evaluate(answer, contract, IndependentScorer)


@pytest.mark.parametrize("field,value", [("build_seconds", -1), ("build_seconds", True), ("build_seconds", math.inf), ("knowledge_bytes", -1), ("knowledge_bytes", True), ("knowledge_bytes", 0.5), ("llm_calls", 1), ("answer_quality_evaluated", True)])
def test_invalid_resource_and_execution_claims_are_rejected(trial, field, value):
    answer, contract = trial
    answer[field] = value
    with pytest.raises(ValueError):
        verifier.evaluate(answer, contract, IndependentScorer)


@pytest.mark.parametrize("field", ["skill_files", "imported_candidate_modules"])
def test_declared_candidate_binding_cannot_be_removed(trial, field):
    answer, contract = trial
    answer[field] = {}
    with pytest.raises(ValueError):
        verifier.evaluate(answer, contract, IndependentScorer)


def test_latency_aggregate_must_match_observed_query_timings(trial):
    answer, contract = trial
    answer["routes"]["fusion"]["p95_ms"] = 0.0
    with pytest.raises(ValueError):
        verifier.evaluate(answer, contract, IndependentScorer)


@pytest.mark.parametrize("value", [-1, True, math.inf])
def test_query_timings_are_finite_nonnegative_numbers(trial, value):
    answer, contract = trial
    answer["routes"]["fusion"]["queries"][0]["milliseconds"] = value
    with pytest.raises(ValueError):
        verifier.evaluate(answer, contract, IndependentScorer)


@pytest.mark.parametrize("artifact", [None, [], "not an object", {}])
def test_malformed_complete_json_produces_zero_reward_receipt(audit_directory, artifact):
    tests = audit_directory / "tests"
    tests.mkdir()
    output = audit_directory / "answer.json"
    output.write_text(json.dumps(artifact), encoding="utf-8")
    (tests / "contract.json").write_text(json.dumps({"verifier_output_path": str(output)}), encoding="utf-8")
    (tests / "evaluate_all_routes.py").write_text("def metrics(*args):\n    raise AssertionError('Invalid artifacts must not reach scoring')\n", encoding="utf-8")
    logs = audit_directory / "logs"
    result = subprocess.run([sys.executable, "-B", str(ROOT / "evaluations/skill-evolution/verifier.py"), "--tests", str(tests), "--logs", str(logs)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert json.loads((logs / "reward.json").read_text(encoding="utf-8")) == {"reward": 0.0, "evidence_integrity": 0.0}
    assert json.loads((logs / "diagnostics.json").read_text(encoding="utf-8"))["status"] == "failed"


@pytest.mark.parametrize("mutation", ["routes-list", "oversized-integer"])
def test_malformed_nested_artifact_produces_zero_reward_receipt(audit_directory, trial, mutation):
    answer, contract = trial
    if mutation == "routes-list":
        answer["routes"] = ["fusion"]
    else:
        answer["build_seconds"] = 10 ** 400
    tests = audit_directory / "tests"
    tests.mkdir()
    output = audit_directory / "answer.json"
    output.write_text(json.dumps(answer), encoding="utf-8")
    contract["verifier_output_path"] = str(output)
    (tests / "contract.json").write_text(json.dumps(contract), encoding="utf-8")
    (tests / "evaluate_all_routes.py").write_text("def metrics(*args):\n    raise AssertionError('Malformed input reached scoring')\n", encoding="utf-8")
    logs = audit_directory / "logs"
    result = subprocess.run([sys.executable, "-B", str(ROOT / "evaluations/skill-evolution/verifier.py"), "--tests", str(tests), "--logs", str(logs)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert json.loads((logs / "reward.json").read_text(encoding="utf-8")) == {"reward": 0.0, "evidence_integrity": 0.0}


@pytest.fixture
def native_agent(monkeypatch, audit_directory):
    base = ModuleType("harbor.agents.base")
    base.BaseAgent = type("BaseAgent", (), {})
    monkeypatch.setitem(sys.modules, "harbor.agents.base", base)
    native = load_module("independent_native_evolution_agent", ROOT / "evaluations/skill-evolution/native_agent.py")
    agent = native.SkillRetrievalAgent()
    agent.skills_dir = "/skills/staged with spaces"
    agent.logs_dir = audit_directory
    return agent


@pytest.mark.parametrize("path", ["/tmp/result.json", "/workspace/../elsewhere/result.json", "relative.json", "/workspace/result.txt"])
def test_native_agent_rejects_output_escape_before_execution(native_agent, path):
    async def unexpected_execution(**kwargs):
        raise AssertionError("Invalid output path reached environment execution")
    request = json.dumps({"family": "classical", "instruction": "Use synthetic manuals", "output_path": path})
    with pytest.raises(ValueError):
        asyncio.run(native_agent.run(request, SimpleNamespace(exec=unexpected_execution), SimpleNamespace()))


def test_native_agent_executes_quoted_staged_package_without_model_calls(native_agent):
    commands = []

    async def execute(**kwargs):
        commands.append(kwargs)
        return SimpleNamespace(stdout="synthetic success", stderr="", return_code=0)

    context = SimpleNamespace()
    request = json.dumps({"family": "classical", "instruction": "Use synthetic manuals", "output_path": "/workspace/space here/result.json"})
    asyncio.run(native_agent.setup(SimpleNamespace(exec=execute)))
    asyncio.run(native_agent.run(request, SimpleNamespace(exec=execute), context))
    assert len(commands) == 2
    assert "/sys/class/net" in shlex.split(commands[0]["command"])[-1]
    argv = shlex.split(commands[1]["command"])
    assert argv[argv.index("--skill") + 1] == "/skills/staged with spaces/build-semantic-okf-knowledge-skill"
    assert argv[argv.index("--output") + 1] == "/workspace/space here/result.json"
    assert argv[argv.index("--input") + 1] == "/dataset"
    assert commands[1]["timeout_sec"] == 3600
    assert context.n_input_tokens == context.n_output_tokens == context.n_cache_tokens == 0
    assert context.cost_usd == 0
    assert context.metadata["llm_calls"] == 0


def test_native_agent_rejects_nonisolated_environment(native_agent):
    async def failed_probe(**kwargs):
        return SimpleNamespace(stdout='{"network_interfaces":["eth0","lo"]}', return_code=1)

    with pytest.raises(RuntimeError, match="unexpected network interface"):
        asyncio.run(native_agent.setup(SimpleNamespace(exec=failed_probe)))


def test_actual_task_generator_emits_kernel_executable_lf_entrypoint(monkeypatch, audit_directory):
    """The generated Linux entrypoint must not acquire CRLF on a Windows host."""
    tools = ROOT / "evaluations/skill-evolution"
    monkeypatch.syspath_prepend(str(tools))
    author = load_module("independent_generated_shell_author", tools / "prepare_datasets.py")
    work = audit_directory / "generated-shell"
    monkeypatch.setattr(author, "WORK", work)
    monkeypatch.setattr(author, "TASKS", work / "tasks")
    monkeypatch.setattr(author, "FAMILIES", ("legacy",))
    source = work / "development-inputs/synthetic"
    (source / "input").mkdir(parents=True)
    author.write_json(source / "input/manifest.json", {"bundle": {}, "sources": []})
    questions = [{"id": "manual", "question": "How is the synthetic loom maintained?", "relevant": ["record"]}]
    author.write_json(source / "queries.json", [{key: row[key] for key in ("id", "question")} for row in questions])
    author.write_json(work / "curator/development/synthetic-oracle.json", {"questions": questions, "records": {"record": "a" * 64}, "record_identities": {"record": {"record_id": "record", "record_sha256": "a" * 64, "source_id": "manual", "concept_id": "loom", "concept_path": "concepts/loom.md"}}, "source_binding": author.tree(source)})
    frozen_image = "sha256:" + "b" * 64
    author.write_json(work / "runtime.json", {"tag": "synthetic-runtime", "image": frozen_image})
    task_id = "retrieval-" + hashlib.sha256(b"synthetic:legacy").hexdigest()[:20]
    author.write_json(work / "curator/authoring/plan/plan.private.json", {"tasks": [{"taskId": task_id, "split": "development", "variantAxes": {"output-root": "/workspace", "output-name": "answer.json"}}]})
    baseline = work / "baseline/build-semantic-okf-knowledge-skill"
    baseline.mkdir(parents=True)
    (baseline / "SKILL.md").write_text("Synthetic packaging fixture", encoding="utf-8")
    monkeypatch.setattr(author, "linux", lambda argv, **kwargs: frozen_image)

    author.task_roots("synthetic", "development")

    entrypoint = author.TASKS / "internal-development-v1" / task_id / "tests/test.sh"
    emitted = entrypoint.read_bytes()
    assert emitted.startswith(b"#!/bin/sh\n")
    assert b"\r" not in emitted
    assert b"/tests/verifier.py --scoring /tests/runtime/support/evaluate_all_routes.py\n" in emitted
