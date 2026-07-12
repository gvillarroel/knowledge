from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-builder"
BASE = EVALUATION_ROOT / "fixtures" / "workspaces" / "base"
SETUP = BASE / "cases" / "setup_case.py"
PREPARE_INTERRUPTION = BASE / "cases" / "prepare_interruption.py"
VERIFIER = BASE / "verification" / "verify_lifecycle.py"
BUILD = REPO_ROOT / "skills" / "build-semantic-okf" / "scripts" / "build_semantic_okf.py"
REFRESH = REPO_ROOT / "skills" / "build-semantic-okf" / "scripts" / "refresh_semantic_okf.py"
VALIDATE = REPO_ROOT / "skills" / "build-semantic-okf" / "scripts" / "validate_semantic_okf.py"
PROMPT_IDS = [
    "create-heterogeneous",
    "augment-add-source",
    "refresh-changed-source",
    "remove-source-safely",
    "choose-source-topology",
    "atomic-rejection-recovery",
    "detect-tampering",
]
CASE_IDS = ["create", "augment", "refresh", "remove", "topology", "atomic", "tamper"]


def load_yaml(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def run(
    arguments: list[str],
    *,
    cwd: Path,
    expected: int = 0,
    report: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=240,
    )
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(result.stdout, encoding="utf-8")
    assert result.returncode == expected, f"{arguments}\nstdout={result.stdout}\nstderr={result.stderr}"
    return result


def setup_case(workspace: Path, case: str) -> Path:
    target = workspace / "work" / case
    run(
        [
            sys.executable,
            str(SETUP),
            case,
            str(target),
            "--force",
            "--reset-deliverable",
            str(workspace / "deliverables" / case),
        ],
        cwd=workspace,
    )
    return target


def build(manifest: Path, output: Path, workspace: Path, *, expected: int = 0, report: Path | None = None) -> None:
    run(
        [sys.executable, str(BUILD), str(manifest), str(output), "--output-format", "json"],
        cwd=workspace,
        expected=expected,
        report=report,
    )


def verify(workspace: Path, case: str) -> None:
    result = run(
        [sys.executable, str(VERIFIER), case, "--workspace", str(workspace)],
        cwd=workspace,
    )
    payload = json.loads(result.stdout)
    assert payload == {"case": case, "errors": [], "pass": True}


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_config_covers_seven_distinct_lifecycle_tasks_and_one_smoke_task() -> None:
    full = load_yaml(EVALUATION_ROOT / "evaluation.yaml")
    smoke = load_yaml(EVALUATION_ROOT / "smoke-evaluation.yaml")

    assert full["schemaVersion"] == 1
    assert full["benchmark"]["id"] == "semantic-okf-builder-lifecycle-compare"
    assert [prompt["id"] for prompt in full["task"]["prompts"]] == PROMPT_IDS
    assert [prompt["id"] for prompt in smoke["task"]["prompts"]] == ["create-heterogeneous"]
    assert smoke["task"]["prompts"][0]["prompt"] == full["task"]["prompts"][0]["prompt"]

    required_language = {
        "create-heterogeneous": ["Markdown, CSV, JSONL, and RDF", "independent bundle validator"],
        "augment-add-source": ["adds the reviewed `projects` source", "plan-change approval"],
        "refresh-changed-source": ["normal full-source refresh", "people-v2.csv"],
        "remove-source-safely": ["ontology-version reuse", "record-removal approvals"],
        "choose-source-topology": ["separate-bundles", "upstream-canonicalization"],
        "atomic-rejection-recovery": ["fail atomically", "recovery command"],
        "detect-tampering": ["tampered copy", "expected to exit 1"],
    }
    for prompt in full["task"]["prompts"]:
        text = prompt["prompt"]
        assert all(fragment in text for fragment in required_language[prompt["id"]])
        assertion_types = [item["type"] for item in prompt["evaluation"]["assertions"]]
        assert assertion_types == ["javascript", "file-contains", "file-contains"]


@pytest.mark.parametrize("config_name", ["evaluation.yaml", "smoke-evaluation.yaml"])
def test_config_is_builder_only_and_luna_only(config_name: str) -> None:
    config_path = EVALUATION_ROOT / config_name
    config = load_yaml(config_path)
    text = config_path.read_text(encoding="utf-8")
    profiles = config["comparison"]["profiles"]
    variants = config["comparison"]["variants"]

    assert [profile["id"] for profile in profiles] == ["no-skill", "skill"]
    assert profiles[0]["capabilities"] == {}
    skill_entries = profiles[1]["capabilities"]["skills"]
    assert skill_entries == [
        {
            "source": {
                "type": "local-path",
                "path": "skills/build-semantic-okf",
                "skillId": "build-semantic-okf",
            },
            "install": {"strategy": "workspace-overlay"},
        }
    ]
    assert "consult-semantic-okf" not in text
    assert "query_semantic_okf.py" not in text

    assert len(variants) == 1
    variant = variants[0]
    assert variant["id"] == "pi-luna-only"
    assert variant["agent"] == {
        "adapter": "pi",
        "model": "openai-codex/gpt-5.6-luna",
        "executionMethod": "command",
        "commandPath": "bin/pi-luna.ps1",
        "sandboxMode": "workspace-write",
        "approvalPolicy": "never",
        "webSearchEnabled": False,
        "networkAccessEnabled": True,
        "reasoningEffort": "medium",
        "additionalDirectories": [],
        "cliEnv": {"PI_MODEL_TIMEOUT_SECONDS": "360"},
        "config": {},
    }
    assert config["evaluation"]["requests"] == 1
    assert config["evaluation"]["maxConcurrency"] == 1
    assert "gpt-5.3" not in text.lower()
    assert "fallback" not in text.lower()
    assert "llm-rubric" not in text


def test_case_setup_is_deterministic(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for case in CASE_IDS:
        target = setup_case(workspace, case)
        first = tree_hash(target)
        target = setup_case(workspace, case)
        assert tree_hash(target) == first


def test_reference_lifecycle_outcomes_pass_all_case_verifiers(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    case = setup_case(workspace, "create")
    output = workspace / "deliverables" / "create" / "bundle"
    build(case / "manifest.json", output, workspace)
    run([sys.executable, str(VALIDATE), str(output), "--output-format", "json"], cwd=workspace)
    verify(workspace, "create")

    case = setup_case(workspace, "augment")
    output = workspace / "deliverables" / "augment" / "bundle"
    build(case / "manifest-v1.json", output, workspace)
    run(
        [
            sys.executable,
            str(REFRESH),
            "update",
            str(case / "manifest-v2.json"),
            str(output),
            "--allow-plan-change",
            "--output-format",
            "json",
        ],
        cwd=workspace,
        report=workspace / "deliverables" / "augment" / "refresh-report.json",
    )
    verify(workspace, "augment")

    case = setup_case(workspace, "refresh")
    output = workspace / "deliverables" / "refresh" / "bundle"
    build(case / "manifest.json", output, workspace)
    shutil.copyfile(case / "seeds" / "people-v2.csv", case / "live" / "people.csv")
    run(
        [sys.executable, str(REFRESH), "update", str(case / "manifest.json"), str(output), "--output-format", "json"],
        cwd=workspace,
        report=workspace / "deliverables" / "refresh" / "refresh-report.json",
    )
    verify(workspace, "refresh")

    case = setup_case(workspace, "remove")
    output = workspace / "deliverables" / "remove" / "bundle"
    build(case / "manifest-v1.json", output, workspace)
    run(
        [
            sys.executable,
            str(REFRESH),
            "update",
            str(case / "manifest-v2-reused-version.json"),
            str(output),
            "--check",
            "--output-format",
            "json",
        ],
        cwd=workspace,
        expected=3,
        report=workspace / "deliverables" / "remove" / "safety-report.json",
    )
    run(
        [
            sys.executable,
            str(REFRESH),
            "update",
            str(case / "manifest-v2.json"),
            str(output),
            "--allow-plan-change",
            "--allow-record-removals",
            "--output-format",
            "json",
        ],
        cwd=workspace,
        report=workspace / "deliverables" / "remove" / "refresh-report.json",
    )
    verify(workspace, "remove")

    setup_case(workspace, "topology")
    decision = {
        "crm-support": "separate-in-bundle",
        "regional-partitions": "logical-union",
        "tenant-isolation": "separate-bundles",
        "vendor-entity-fusion": "upstream-canonicalization",
    }
    decision_path = workspace / "deliverables" / "topology" / "decision.json"
    decision_path.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verify(workspace, "topology")

    case = setup_case(workspace, "atomic")
    rejected = workspace / "deliverables" / "atomic" / "rejected"
    build(
        case / "manifest-invalid.json",
        rejected,
        workspace,
        expected=2,
        report=workspace / "deliverables" / "atomic" / "rejection-report.json",
    )
    output = workspace / "deliverables" / "atomic" / "bundle"
    build(case / "manifest-valid.json", output, workspace)
    run([sys.executable, str(PREPARE_INTERRUPTION), str(output)], cwd=workspace)
    run(
        [sys.executable, str(REFRESH), "recover", str(output), "--output-format", "json"],
        cwd=workspace,
        report=workspace / "deliverables" / "atomic" / "recovery-report.json",
    )
    verify(workspace, "atomic")

    case = setup_case(workspace, "tamper")
    output = workspace / "deliverables" / "tamper" / "bundle"
    build(case / "manifest.json", output, workspace)
    tampered = workspace / "deliverables" / "tamper" / "tampered"
    shutil.copytree(output, tampered)
    with (tampered / "semantic" / "data.ttl").open("a", encoding="utf-8") as handle:
        handle.write('\n<https://example.org/tamper-extra> <https://example.org/ontology/tamper#name> "Injected" .\n')
    run(
        [sys.executable, str(VALIDATE), str(tampered), "--output-format", "json"],
        cwd=workspace,
        expected=1,
        report=workspace / "deliverables" / "tamper" / "validation-report.json",
    )
    verify(workspace, "tamper")


def test_luna_wrapper_rejects_alternate_routes_and_invokes_once(tmp_path: Path) -> None:
    if os.name != "nt":
        pytest.skip("The benchmark wrapper is Windows-specific.")

    wrapper = BASE / "bin" / "pi-luna.ps1"
    wrapper_text = wrapper.read_text(encoding="utf-8")
    assert wrapper_text.startswith("Set-StrictMode -Version Latest\n")
    assert 'requiredModel = "openai-codex/gpt-5.6-luna"' in wrapper_text
    assert "routing=luna-only" in wrapper_text
    assert "gpt-5.3" not in wrapper_text.lower()
    assert "fallback" not in wrapper_text.lower()

    fake_pi = tmp_path / "pi.ps1"
    fake_pi.write_text(
        '[IO.File]::AppendAllText($env:PI_TEST_LOG, "call`n")\n'
        'Write-Output "ok"\n'
        "exit 0\n",
        encoding="utf-8",
    )
    log = tmp_path / "calls.log"
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}{os.pathsep}{env['PATH']}"
    env["PI_TEST_LOG"] = str(log)
    env["PI_MODEL_TIMEOUT_SECONDS"] = "10"

    def invoke(*arguments: str) -> subprocess.CompletedProcess[str]:
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
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    valid = invoke("--model", "openai-codex/gpt-5.6-luna", "prompt")
    assert valid.returncode == 0
    assert valid.stdout.strip() == "ok"
    assert "routing=luna-only" in valid.stderr
    wrong = invoke("--model", "example/not-luna")
    assert wrong.returncode == 64
    duplicate = invoke(
        "--model",
        "openai-codex/gpt-5.6-luna",
        "--model",
        "openai-codex/gpt-5.6-luna",
    )
    assert duplicate.returncode == 64
    assert log.read_text(encoding="utf-8").splitlines() == ["call"]
