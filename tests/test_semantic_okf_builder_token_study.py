"""Tests for the frozen eight-family direct-builder token study."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "evaluations/semantic-okf-datasets"
sys.path.insert(0, str(ROOT))

import builder_token_score as SCORE  # noqa: E402
import capture_registered_token_evidence as CAPTURE  # noqa: E402
import prepare_builder_token_study as PREPARE  # noqa: E402
import run_builder_token_study as RUN  # noqa: E402


def write_bundle(root: Path, records: bytes, sentinel: str) -> None:
    """Create one minimal mechanically valid generated folder."""

    files = {
        "index.md": b"# Knowledge\n",
        "semantic/build-report.json": (
            json.dumps(
                {
                    "status": "pass",
                    "valid": True,
                    "errors": [],
                },
                sort_keys=True,
            ).encode()
            + b"\n"
        ),
        "semantic/records.jsonl": records,
        "semantic/validation-report.ttl": (
            b'_:r <http://www.w3.org/ns/shacl#conforms> "true" .\n'
        ),
        sentinel: b"family projection\n",
    }
    for relative, content in files.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def test_frozen_builder_study_has_all_eight_registered_families() -> None:
    manifest = PREPARE.verify(PREPARE.DEFAULT_OUTPUT)

    assert set(manifest["families"]) == {
        "adaptive",
        "classical",
        "embeddings",
        "ensemble",
        "entity-graph",
        "graphify",
        "legacy",
        "turso",
    }
    assert manifest["model"] == "openai-codex/gpt-5.3-codex-spark"
    assert manifest["pi_version"] == "0.73.1"
    for family, record in manifest["families"].items():
        task_root = (
            PREPARE.DEFAULT_OUTPUT / "tasks/development" / family
        )
        assert sorted(path.name for path in task_root.iterdir()) == [
            "replicate-a",
            "replicate-b",
        ]
        for task in task_root.iterdir():
            text = (task / "task.toml").read_text(encoding="utf-8")
            assert PREPARE.RUNTIME_IMAGE in text
            assert "builder-token" in text
        assert record["build_skill"].startswith("build-semantic-okf")


def test_builder_scorer_qualifies_one_valid_folder(
    tmp_path: Path,
) -> None:
    records = b'{"id":"one"}\n{"id":"two"}\n'
    expected_sha256 = hashlib.sha256(records).hexdigest()
    first = tmp_path / "primary"
    sentinel = "family/index.json"
    write_bundle(first, records, sentinel)
    pi_log = tmp_path / "pi.jsonl"
    commands = [
        "python build_family.py /dataset/manifest.json "
        f"{first}",
        f"python validate_family.py {first}",
    ]
    pi_log.write_text(
        "\n".join(
            json.dumps(
                {
                    "type": "tool_execution_start",
                    "toolName": "bash",
                    "toolCallId": f"call-{index}",
                    "arguments": {"command": command},
                }
            )
            for index, command in enumerate(commands)
        )
        + "\n",
        encoding="utf-8",
    )
    config = {
        "family": "fixture",
        "outputs": [str(first)],
        "build_script": "build_family.py",
        "validate_script": "validate_family.py",
        "family_sentinel": sentinel,
        "expected_records_sha256": expected_sha256,
        "expected_records_count": 2,
    }

    rewards, diagnostics = SCORE.score(config, pi_log)

    assert rewards == {
        "reward": 1.0,
        "artifact_integrity_gate": 1.0,
        "records_identity_gate": 1.0,
        "workflow_safety_gate": 1.0,
        "invocation_coverage_gate": 1.0,
    }
    assert diagnostics["status"] == "qualified-single-folder"
    assert diagnostics["bundles"][0]["tree_sha256"] == SCORE.tree_digest(
        first
    )


def test_builder_scorer_rejects_a_repeated_builder_invocation(
    tmp_path: Path,
) -> None:
    records = b'{"id":"one"}\n'
    output = tmp_path / "knowledge"
    sentinel = "family/index.json"
    write_bundle(output, records, sentinel)
    commands = [
        f"python build_family.py /dataset/manifest.json {output}",
        f"python build_family.py /dataset/manifest.json {output}",
        f"python validate_family.py {output}",
    ]
    pi_log = tmp_path / "pi.jsonl"
    pi_log.write_text(
        "\n".join(
            json.dumps(
                {
                    "type": "tool_execution_start",
                    "toolName": "bash",
                    "toolCallId": f"call-{index}",
                    "arguments": {"command": command},
                }
            )
            for index, command in enumerate(commands)
        )
        + "\n",
        encoding="utf-8",
    )

    rewards, diagnostics = SCORE.score(
        {
            "family": "fixture",
            "outputs": [str(output)],
            "build_script": "build_family.py",
            "validate_script": "validate_family.py",
            "family_sentinel": sentinel,
            "expected_records_sha256": hashlib.sha256(records).hexdigest(),
            "expected_records_count": 1,
        },
        pi_log,
    )

    assert rewards["invocation_coverage_gate"] == 0.0
    assert rewards["reward"] == 0.75
    assert diagnostics["status"] == "unqualified-single-folder"


def test_builder_runner_uses_one_family_skill_and_balanced_schedule(
    tmp_path: Path,
) -> None:
    manifest = json.loads(
        (PREPARE.DEFAULT_OUTPUT / "frozen-inputs.json").read_text(
            encoding="utf-8"
        )
    )
    config = RUN.job_config(
        frozen=PREPARE.DEFAULT_OUTPUT,
        jobs=tmp_path / "jobs",
        manifest=manifest,
        family_id="embeddings",
        replicate="replicate-a",
        auth_directory=tmp_path / "auth",
        hf_cache=tmp_path / "hub",
    )

    agent = config["agents"][0]
    assert agent["model_name"] == manifest["model"]
    assert agent["skills"] == [
        str(
            PREPARE.DEFAULT_OUTPUT
            / "skills/build-semantic-okf-embeddings"
        )
    ]
    mounts = config["environment"]["mounts"]
    assert [mount["target"] for mount in mounts] == [
        "/dataset",
        "/root/.pi/agent",
        "/models/huggingface/hub",
    ]
    assert "read_only" not in mounts[1]
    schedule = RUN.selected_schedule(
        sorted(PREPARE.FAMILY_SENTINELS),
        list(PREPARE.REPLICATES),
    )
    assert len(schedule) == 16
    assert {
        family: sum(row[0] == family for row in schedule)
        for family in PREPARE.FAMILY_SENTINELS
    } == {family: 2 for family in PREPARE.FAMILY_SENTINELS}


def test_capture_resolves_the_single_native_harbor_trial(
    tmp_path: Path,
) -> None:
    job = tmp_path / "job"
    trial = job / "replicate-a__abc123"
    trial.mkdir(parents=True)
    result = trial / "result.json"
    result.write_text("{}\n", encoding="utf-8")

    assert CAPTURE.one_trial_result(job) == result


def test_capture_reads_qualified_builder_tree_identity(
    tmp_path: Path,
) -> None:
    trial = tmp_path / "replicate-a__abc123"
    result = trial / "result.json"
    result.parent.mkdir(parents=True)
    result.write_text("{}\n", encoding="utf-8")
    tree_sha256 = "a" * 64
    diagnostics = trial / "verifier/diagnostics.json"
    diagnostics.parent.mkdir()
    diagnostics.write_text(
        json.dumps(
            {
                "schema_version": (
                    "semantic-okf-builder-token-diagnostics/2.0"
                ),
                "status": "qualified-single-folder",
                "family": "adaptive",
                "bundles": [
                    {
                        "artifact_integrity": True,
                        "records_identity": True,
                        "tree_sha256": tree_sha256,
                    }
                ],
                "commands": {
                    "build_command_count": 1,
                    "validation_command_count": 1,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    assert CAPTURE.builder_diagnostics(
        result,
        "adaptive",
    ) == (diagnostics, tree_sha256)
