"""Validate the restricted knowledge-methodology reviewer contract."""

from __future__ import annotations

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
AGENT_ROOT = REPO / "agents" / "knowledge-methodology-reviewer"
DATASET_ROOT = REPO / "evaluations" / "knowledge-methodology-papers"
SKILL_ROOT = REPO / "skills" / "review-knowledge-methodology"


def validate_agent() -> dict[str, object]:
    """Return a compact passing report or raise on any contract violation."""

    manifest = json.loads(
        (AGENT_ROOT / "agent.json").read_text(encoding="utf-8")
    )
    expected_skills = ["review-knowledge-methodology"]
    assert manifest["schema_version"] == "repository-agent/1.0"
    assert manifest["default_skills"] == expected_skills
    assert manifest["allowed_skills"] == expected_skills
    assert manifest["authority"] == {
        "mode": "read-only-review",
        "may_modify_repository": False,
        "may_acquire_external_sources": False,
    }
    assert manifest["knowledge_dataset"]["dataset_id"] == (
        "knowledge-methodology-papers-47"
    )
    assert (AGENT_ROOT / manifest["instructions"]).is_file()
    assert (DATASET_ROOT / "paper-selection.json").is_file()
    assert (DATASET_ROOT / "bundle" / "semantic" / "build-report.json").is_file()
    assert (SKILL_ROOT / "SKILL.md").is_file()
    assert (SKILL_ROOT / "expert-manifest.json").is_file()

    instructions = (AGENT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "read-only review agent" in instructions
    assert "Use no other skill" in instructions
    assert "versioned arXiv IDs" in instructions

    return {
        "status": "pass",
        "agent": manifest["name"],
        "default_skills": expected_skills,
        "dataset_id": manifest["knowledge_dataset"]["dataset_id"],
    }


def main() -> int:
    """Validate the agent and emit one stable JSON report."""

    print(json.dumps(validate_agent(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
