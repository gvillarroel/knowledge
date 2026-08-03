from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = (
    ROOT
    / "evaluations"
    / "semantic-okf-tika-mallet-tantivy"
    / "scripts"
    / "generate_builder_pareto_tasks.py"
)
SCORER = (
    ROOT
    / "evaluations"
    / "semantic-okf-tika-mallet-tantivy"
    / "builder_pareto_score.py"
)
SOURCE_BUILDER = ROOT / "skills" / "build-semantic-okf-tika-mallet"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_builder_pareto_tasks_are_deterministic_and_holdout_separate(tmp_path: Path) -> None:
    generator = load(GENERATOR, "builder_pareto_generator")
    output = tmp_path / "tasks"
    generator.materialize(output)
    generator.check(output)

    development = sorted(path.name for path in (output / "development").iterdir())
    holdout = sorted(path.name for path in (output / "holdout").iterdir())
    assert development == ["qualified-runtime-a", "qualified-runtime-b"]
    assert holdout == ["qualified-runtime-c", "qualified-runtime-d"]
    assert set(development).isdisjoint(holdout)
    for task in generator.TASKS:
        root = output / task.cohort / task.task_id
        instruction = (root / "instruction.md").read_text(encoding="utf-8")
        assert "/dataset/ingestion-plan.json" in instruction
        assert "/dataset/retrieval-plan.json" in instruction
        assert "Do not consult" in instruction
        task_config = (root / "task.toml").read_text(encoding="utf-8")
        assert 'network_mode = "no-network"' not in task_config
        assert task_config.count('network_mode = "public"') == 4
        assert 'destination = "snapshot-primary"' in task_config
        assert 'destination = "snapshot-replay"' in task_config
        assert (root / "environment").is_dir()


def test_builder_command_policy_rewards_qualified_runtime() -> None:
    scorer = load(SCORER, "builder_pareto_scorer")
    good = scorer.command_checks(
        [
            'python scripts/build_semantic_okf_tika_mallet.py a b x --java "$SEMANTIC_OKF_JAVA"',
            'python scripts/validate_semantic_okf_tika_mallet.py x --java "$SEMANTIC_OKF_JAVA"',
            'python scripts/build_semantic_okf_tika_mallet.py a b y --java "$SEMANTIC_OKF_JAVA"',
            'python scripts/validate_semantic_okf_tika_mallet.py y --java "$SEMANTIC_OKF_JAVA"',
        ]
    )
    assert good["runtime_contract_gate"] == 1.0
    assert good["validation_invocation_gate"] == 1.0
    assert good["workflow_efficiency"] == 1.0

    bad = scorer.command_checks(
        [
            "which java",
            "pip install -r scripts/requirements.txt",
            "rm -rf /workspace/knowledge",
            "python scripts/build_semantic_okf_tika_mallet.py a b x --java /usr/bin/java",
        ]
    )
    assert bad["runtime_contract_gate"] == 0.0
    assert bad["workflow_efficiency"] == 0.0


def test_builder_command_parser_uses_completed_events_and_ignores_help(
    tmp_path: Path,
) -> None:
    scorer = load(SCORER, "builder_pareto_event_parser")
    command = (
        "python scripts/build_semantic_okf_tika_mallet.py a b x "
        '--java "$SEMANTIC_OKF_JAVA"'
    )
    help_command = "python scripts/build_semantic_okf_tika_mallet.py --help"
    content = [
        {
            "type": "toolCall",
            "id": "call-build",
            "arguments": {"command": command},
        },
        {
            "type": "toolCall",
            "id": "call-help",
            "arguments": {"command": help_command},
        },
    ]
    log = tmp_path / "pi.txt"
    log.write_text(
        "\n".join(
            json.dumps(
                {
                    "type": event_type,
                    "message": {"role": "assistant", "content": content},
                }
            )
            for event_type in ("message_start", "message_end")
        )
        + "\n",
        encoding="utf-8",
    )

    commands = scorer.tool_commands(log)
    checks = scorer.command_checks(commands)
    assert commands == [command, help_command]
    assert checks["command_count"] == 2
    assert checks["build_invocations"] == 1


def test_promoted_builder_documents_the_qualified_runtime_contract() -> None:
    skill = (SOURCE_BUILDER / "SKILL.md").read_text(encoding="utf-8")

    assert "use the supplied CPython 3.12 interpreter directly" in skill
    assert "Do not create a virtual environment, run `pip install`" in skill
    assert "Run `runtime_smoke.py` exactly once before any build" in skill
    assert "first build, first independent validation, second build" in skill
    assert "do not scan `/`, search the PATH" in skill
