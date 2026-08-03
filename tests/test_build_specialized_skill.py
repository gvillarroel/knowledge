"""Tests for deterministic Semantic OKF expert-skill packaging."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-specialized-skill"
BUILD_SCRIPT = SKILL_ROOT / "scripts" / "build_specialized_skill.py"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_specialized_skill.py"
TRACE_QUERY_TEMPLATE = (
    SKILL_ROOT
    / "assets"
    / "expert-template"
    / "query_expert_knowledge_trace_bm25.py"
)


def _write_knowledge(root: Path, *, valid: bool = True) -> Path:
    knowledge = root / "knowledge"
    concept_path = knowledge / "concepts" / "policies" / "release-window.md"
    concept_path.parent.mkdir(parents=True)
    concept_body = (
        "# Release window\n\n"
        "Deployments are permitted on Tuesday after the change record is approved.\n"
        "The policy uses the comparison marker ∗ in its reviewed notation.\n"
    )
    concept_path.write_text(concept_body, encoding="utf-8", newline="\n")
    (knowledge / "index.md").write_text(
        '# Test knowledge\n\n- [Release window](concepts/policies/release-window.md)\n',
        encoding="utf-8",
        newline="\n",
    )
    semantic = knowledge / "semantic"
    semantic.mkdir()
    report = {
        "schema_version": "1.0",
        "status": "pass" if valid else "fail",
        "valid": valid,
        "errors": [] if valid else ["fixture failure"],
        "summary": {"records": 1},
    }
    (semantic / "build-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    record = {
        "source_id": "policies",
        "record_id": "release-window",
        "title": "Release window",
        "concept_type": "Policy",
        "concept_path": "concepts/policies/release-window.md",
        "record_sha256": hashlib.sha256(concept_body.encode("utf-8")).hexdigest(),
        "body": concept_body,
    }
    (semantic / "records.jsonl").write_text(
        json.dumps(record, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return knowledge


def _write_guidance(root: Path) -> Path:
    guidance = root / "guidance.md"
    guidance.write_text(
        """# Release Governance Expert

## Scope

Apply the bundled release-policy knowledge to scheduling and approval questions.
Exclude emergency procedures unless an exact bundled record describes them.

## Application workflow

Identify the requested release, find the exact policy record, verify its scope,
and compare every requested condition with the authoritative concept.

## Decision rules

Approve a proposed window only when the stated weekday and approval condition
both match the policy. Treat missing approval evidence as unresolved, not passed.

## Evidence and limits

Cite the exact bundled concept path beside the decision. Distinguish direct
policy language from inference and stop when the snapshot lacks a requested rule.
""",
        encoding="utf-8",
        newline="\n",
    )
    return guidance


def _write_profile_questions(root: Path) -> Path:
    questions = root / "profile-questions.jsonl"
    rows = [
        {
            "id": "q001",
            "question": "Which policy permits Tuesday deployments after approval?",
            "qrels": {"source_ids": ["policies"]},
        },
        {
            "id": "q002",
            "question": "What approval evidence is required for the release window?",
            "qrels": {"source_ids": ["policies"]},
        },
    ]
    questions.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    return questions


def _run(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *map(str, arguments)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_build_validate_check_and_query_standalone_expert(tmp_path: Path) -> None:
    """The three-stage artifact is bound, reproducible, and independently usable."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    output = tmp_path / "release-governance-expert"
    knowledge_before = _tree_bytes(knowledge)

    built = _run(
        BUILD_SCRIPT,
        knowledge,
        output,
        "--name",
        output.name,
        "--description",
        "Apply bundled release governance knowledge to scheduling decisions.",
        "--guidance",
        guidance,
    )
    assert built.returncode == 0, built.stderr
    assert json.loads(built.stdout)["record_count"] == 1
    assert _tree_bytes(knowledge) == knowledge_before

    validated = _run(VALIDATE_SCRIPT, output)
    assert validated.returncode == 0, validated.stderr
    assert json.loads(validated.stdout)["status"] == "pass"

    checked = _run(
        BUILD_SCRIPT,
        knowledge,
        output,
        "--name",
        output.name,
        "--description",
        "Apply bundled release governance knowledge to scheduling decisions.",
        "--guidance",
        guidance,
        "--check",
    )
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)["mode"] == "check"

    query = _run(
        output / "scripts" / "query_expert_knowledge.py",
        "search",
        "--contains",
        "Tuesday approved",
        "--show-content",
    )
    assert query.returncode == 0, query.stderr
    payload = json.loads(query.stdout)
    assert payload["verification"]["status"] == "pass"
    assert payload["results"][0]["record_id"] == "release-window"
    assert payload["results"][0]["concept_path"] == (
        "concepts/policies/release-window.md"
    )
    assert payload["results"][0]["locator"] == {"kind": "record"}
    assert payload["results"][0]["text"] == payload["results"][0]["body"]
    assert payload["results"][0]["text_sha256"] == hashlib.sha256(
        payload["results"][0]["text"].encode("utf-8")
    ).hexdigest()

    hostile_environment = os.environ.copy()
    hostile_environment["PYTHONIOENCODING"] = "cp1252"
    hostile_console = subprocess.run(
        [
            sys.executable,
            str(output / "scripts" / "query_expert_knowledge.py"),
            "search",
            "--contains",
            "Tuesday approved",
            "--show-content",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        env=hostile_environment,
        check=False,
    )
    assert hostile_console.returncode == 0, hostile_console.stderr
    assert "∗".encode() in hostile_console.stdout

    copied_parent = tmp_path / "copied"
    copied_parent.mkdir()
    copied = copied_parent / output.name
    shutil.copytree(output, copied)
    copied_query = _run(
        copied / "scripts" / "query_expert_knowledge.py",
        "get",
        "--source-id",
        "policies",
        "--record-id",
        "release-window",
    )
    assert copied_query.returncode == 0, copied_query.stderr


def test_identical_inputs_produce_byte_identical_experts(tmp_path: Path) -> None:
    """Absolute input and output locations do not enter generated bytes."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    first = tmp_path / "first" / "policy-expert"
    second = tmp_path / "second" / "policy-expert"
    arguments = (
        "--name",
        "policy-expert",
        "--description",
        "Apply the bundled policy knowledge with exact evidence.",
        "--guidance",
        guidance,
    )

    first_result = _run(BUILD_SCRIPT, knowledge, first, *arguments)
    second_result = _run(BUILD_SCRIPT, knowledge, second, *arguments)

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    assert _tree_bytes(first) == _tree_bytes(second)


def test_builder_can_bind_the_trace_bm25_query_template(tmp_path: Path) -> None:
    """A selected query profile is copied, bound, queried, and reproducible."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    output = tmp_path / "trace-policy-expert"
    arguments = (
        "--name",
        output.name,
        "--description",
        "Apply the bundled policy knowledge with trace-derived retrieval.",
        "--guidance",
        guidance,
        "--query-template",
        TRACE_QUERY_TEMPLATE,
    )

    built = _run(BUILD_SCRIPT, knowledge, output, *arguments)
    assert built.returncode == 0, built.stderr
    manifest = json.loads(
        (output / "expert-manifest.json").read_text(encoding="utf-8")
    )
    query_script = output / "scripts" / "query_expert_knowledge.py"
    assert manifest["artifacts"]["query_script"]["sha256"] == hashlib.sha256(
        query_script.read_bytes()
    ).hexdigest()

    queried = _run(
        query_script,
        "search",
        "--contains",
        "Tuesday approved",
        "--show-content",
    )
    assert queried.returncode == 0, queried.stderr
    payload = json.loads(queried.stdout)
    assert payload["verification"]["retrieval"]["id"] == (
        "trace-bm25-field-fusion-v1"
    )
    assert payload["results"][0]["record_id"] == "release-window"

    checked = _run(BUILD_SCRIPT, knowledge, output, *arguments, "--check")
    assert checked.returncode == 0, checked.stderr


def test_builder_binds_multi_file_query_adapter(tmp_path: Path) -> None:
    """Custom adapters may carry hash-bound local modules and requirements."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    support = tmp_path / "quality_support.py"
    support.write_text(
        'ROUTE_NAME = "fixture-quality"\n',
        encoding="utf-8",
        newline="\n",
    )
    requirements = tmp_path / "requirements.txt"
    requirements.write_text(
        "# No third-party packages are required.\n",
        encoding="utf-8",
        newline="\n",
    )
    template = tmp_path / "query_template.py"
    default_template = (
        SKILL_ROOT
        / "assets"
        / "expert-template"
        / "query_expert_knowledge.py"
    ).read_text(encoding="utf-8")
    template.write_text(
        default_template.replace(
            "import sys\n",
            "import sys\nsys.dont_write_bytecode = True\nimport quality_support\n",
            1,
        ),
        encoding="utf-8",
        newline="\n",
    )
    output = tmp_path / "multi-file-expert"
    arguments = (
        "--name",
        output.name,
        "--description",
        "Apply bundled knowledge through a multi-file query adapter.",
        "--guidance",
        guidance,
        "--query-template",
        template,
        "--query-support",
        support,
        "--query-support",
        requirements,
    )

    built = _run(BUILD_SCRIPT, knowledge, output, *arguments)
    assert built.returncode == 0, built.stderr
    manifest = json.loads(
        (output / "expert-manifest.json").read_text(encoding="utf-8")
    )
    assert [row["path"] for row in manifest["artifacts"]["query_support"]] == [
        "scripts/quality_support.py",
        "scripts/requirements.txt",
    ]

    queried = _run(
        output / "scripts" / "query_expert_knowledge.py",
        "search",
        "--contains",
        "Tuesday approved",
    )
    assert queried.returncode == 0, queried.stderr
    assert not (output / "scripts" / "__pycache__").exists()

    checked = _run(BUILD_SCRIPT, knowledge, output, *arguments, "--check")
    assert checked.returncode == 0, checked.stderr

    (output / "scripts" / "quality_support.py").write_text(
        'ROUTE_NAME = "tampered"\n',
        encoding="utf-8",
        newline="\n",
    )
    rejected = _run(VALIDATE_SCRIPT, output)
    assert rejected.returncode != 0
    assert "query-support artifact digest drift" in rejected.stderr


def test_builder_forges_explicit_retrospective_profile(tmp_path: Path) -> None:
    """The high-performing exposed-qrel route is integrated and reproducible."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    questions = _write_profile_questions(tmp_path)
    output = tmp_path / "profile-policy-expert"
    arguments = (
        "--name",
        output.name,
        "--description",
        "Apply policy knowledge with a retrospective fixed-workload profile.",
        "--guidance",
        guidance,
        "--retrieval-profile",
        "retrospective-supervised-ngram",
        "--profile-dataset-id",
        "release-policy-2",
        "--profile-questions",
        questions,
        "--profile-qrel-key",
        "source_ids",
        "--profile-identity-mode",
        "source-id",
        "--acknowledge-exposed-qrels",
    )

    built = _run(BUILD_SCRIPT, knowledge, output, *arguments)
    assert built.returncode == 0, built.stderr
    build_payload = json.loads(built.stdout)
    assert build_payload["retrieval_profile"] == {
        "mode": "retrospective-supervised-ngram",
        "promotion_eligible": False,
    }

    manifest = json.loads(
        (output / "expert-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["schema_version"] == "semantic-okf-expert-skill/1.1"
    assert manifest["retrieval_profile"]["question_count"] == 2
    assert manifest["retrieval_profile"]["promotion_eligible"] is False
    profile = json.loads(
        (output / "scripts" / "expert_routing_index.json").read_text(
            encoding="utf-8"
        )
    )
    assert profile["retrieval"]["exact_question_lookup"] is False
    assert profile["development_evidence"]["questions_sha256"] == hashlib.sha256(
        questions.read_bytes()
    ).hexdigest()
    assert "Which policy permits" not in json.dumps(profile)

    validated = _run(VALIDATE_SCRIPT, output)
    assert validated.returncode == 0, validated.stderr
    assert json.loads(validated.stdout)["retrieval_profile"][
        "promotion_eligible"
    ] is False

    queried = _run(
        output / "scripts" / "query_expert_knowledge.py",
        "search",
        "--contains",
        "Tuesday deployments after approval",
        "--show-content",
    )
    assert queried.returncode == 0, queried.stderr
    payload = json.loads(queried.stdout)
    assert payload["verification"]["promotion_eligible"] is False
    assert payload["verification"]["retrieval"]["id"] == (
        "retrospective-supervised-ngram-fusion-v2"
    )
    assert payload["results"][0]["source_id"] == "policies"
    assert payload["results"][0]["locator"] == {"kind": "record"}

    checked = _run(BUILD_SCRIPT, knowledge, output, *arguments, "--check")
    assert checked.returncode == 0, checked.stderr

    profile_path = output / "scripts" / "expert_routing_index.json"
    profile_path.write_text("{}\n", encoding="utf-8", newline="\n")
    rejected = _run(VALIDATE_SCRIPT, output)
    assert rejected.returncode != 0
    assert "digest drift" in rejected.stderr


def test_builder_rejects_evaluation_only_questions_for_profiles(
    tmp_path: Path,
) -> None:
    """A local deny-use marker blocks the v51-style supervised leakage path."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    questions_root = tmp_path / "sealed-evaluation"
    questions_root.mkdir()
    questions = _write_profile_questions(questions_root)
    (questions_root / "EVALUATION_ONLY.json").write_text(
        json.dumps(
            {
                "schema_version": "evaluation-only-dataset-policy/1.0",
                "dataset_id": "fixture-evaluation-only",
                "classification": "evaluation-only",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    output = tmp_path / "forbidden-profile-expert"

    rejected = _run(
        BUILD_SCRIPT,
        knowledge,
        output,
        "--name",
        output.name,
        "--description",
        "This profile must not be created.",
        "--guidance",
        guidance,
        "--retrieval-profile",
        "retrospective-supervised-ngram",
        "--profile-dataset-id",
        "fixture-evaluation-only",
        "--profile-questions",
        questions,
        "--profile-qrel-key",
        "source_ids",
        "--profile-identity-mode",
        "source-id",
        "--acknowledge-exposed-qrels",
    )

    assert rejected.returncode != 0
    assert "evaluation-only" in rejected.stderr
    assert not output.exists()


def test_retrospective_profile_requires_acknowledgement_and_owns_adapter(
    tmp_path: Path,
) -> None:
    """The builder cannot silently expose qrels or mix retrieval treatments."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    questions = _write_profile_questions(tmp_path)
    output = tmp_path / "unsafe-profile-expert"
    base = (
        "--name",
        output.name,
        "--description",
        "Apply policy knowledge with a retrospective profile.",
        "--guidance",
        guidance,
        "--retrieval-profile",
        "retrospective-supervised-ngram",
        "--profile-dataset-id",
        "release-policy-2",
        "--profile-questions",
        questions,
        "--profile-qrel-key",
        "source_ids",
        "--profile-identity-mode",
        "source-id",
    )
    unacknowledged = _run(BUILD_SCRIPT, knowledge, output, *base)
    assert unacknowledged.returncode != 0
    assert "--acknowledge-exposed-qrels" in unacknowledged.stderr
    assert not output.exists()

    mixed = _run(
        BUILD_SCRIPT,
        knowledge,
        output,
        *base,
        "--acknowledge-exposed-qrels",
        "--query-template",
        TRACE_QUERY_TEMPLATE,
    )
    assert mixed.returncode != 0
    assert "cannot be combined" in mixed.stderr
    assert not output.exists()


def test_validator_detects_embedded_knowledge_drift(tmp_path: Path) -> None:
    """Consultation fails closed after any embedded snapshot mutation."""

    knowledge = _write_knowledge(tmp_path)
    guidance = _write_guidance(tmp_path)
    output = tmp_path / "policy-expert"
    built = _run(
        BUILD_SCRIPT,
        knowledge,
        output,
        "--name",
        output.name,
        "--description",
        "Apply the bundled policy knowledge with exact evidence.",
        "--guidance",
        guidance,
    )
    assert built.returncode == 0, built.stderr
    embedded = (
        output
        / "references"
        / "knowledge"
        / "concepts"
        / "policies"
        / "release-window.md"
    )
    embedded.write_text("tampered\n", encoding="utf-8", newline="\n")

    validated = _run(VALIDATE_SCRIPT, output)
    queried = _run(output / "scripts" / "query_expert_knowledge.py", "verify")

    assert validated.returncode != 0
    assert "digest drift" in validated.stderr
    assert queried.returncode != 0
    assert "digest drift" in queried.stderr


def test_builder_rejects_failed_knowledge_and_placeholder_guidance(
    tmp_path: Path,
) -> None:
    """Both stage inputs must pass their explicit gates."""

    failed_knowledge = _write_knowledge(tmp_path / "failed", valid=False)
    guidance = _write_guidance(tmp_path)
    output = tmp_path / "failed-expert"
    rejected_knowledge = _run(
        BUILD_SCRIPT,
        failed_knowledge,
        output,
        "--name",
        output.name,
        "--description",
        "Apply failed fixture knowledge.",
        "--guidance",
        guidance,
    )
    assert rejected_knowledge.returncode != 0
    assert "status 'pass'" in rejected_knowledge.stderr
    assert not output.exists()

    valid_knowledge = _write_knowledge(tmp_path / "valid")
    bad_guidance = tmp_path / "bad-guidance.md"
    bad_guidance.write_text(
        "# Expert\n\nTODO: complete the domain workflow.\n",
        encoding="utf-8",
        newline="\n",
    )
    rejected_guidance = _run(
        BUILD_SCRIPT,
        valid_knowledge,
        output,
        "--name",
        output.name,
        "--description",
        "Apply valid fixture knowledge.",
        "--guidance",
        bad_guidance,
    )
    assert rejected_guidance.returncode != 0
    assert "Guidance" in rejected_guidance.stderr
    assert not output.exists()


def test_specialized_stage_does_not_replace_generic_build_and_consult() -> None:
    """The new artifact path coexists with the accepted two-stage packages."""

    build_skill = (REPO_ROOT / "skills" / "build-semantic-okf" / "SKILL.md")
    consult_skill = (REPO_ROOT / "skills" / "consult-semantic-okf" / "SKILL.md")
    specialized = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert build_skill.is_file()
    assert consult_skill.is_file()
    assert "existing two-stage Build and Consult path remains valid" in specialized
    assert "Never acquire sources, build or repair Semantic OKF" in specialized
