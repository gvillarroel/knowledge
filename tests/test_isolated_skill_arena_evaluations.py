"""Structural guards for the fast, isolated Skill Arena evolution suites."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations"

ISOLATED_SUITES = {
    "brave-search-effective": "brave-search-effective",
    "extract-ontologies": "extract-ontologies",
    "know": "know",
    "open-knowledge-format": "open-knowledge-format",
    "roundtrip-confluence-pages": "roundtrip-confluence-pages",
    "television": "television",
}


@pytest.mark.parametrize(("suite", "skill_id"), ISOLATED_SUITES.items())
def test_evolution_suite_compares_no_skill_with_exactly_one_skill(
    suite: str,
    skill_id: str,
) -> None:
    config = yaml.safe_load(
        (EVALUATION_ROOT / suite / "evaluation.yaml").read_text(encoding="utf-8")
    )
    profiles = config["comparison"]["profiles"]

    assert len(profiles) == 2
    control = next(profile for profile in profiles if not profile["capabilities"])
    treatment = next(profile for profile in profiles if profile["capabilities"])
    installed_skills = treatment["capabilities"]["skills"]

    assert control["isolation"] == {"inheritSystem": False}
    assert treatment["isolation"] == {"inheritSystem": False}
    assert len(installed_skills) == 1
    assert installed_skills[0]["source"] == {
        "type": "local-path",
        "path": f"skills/{skill_id}",
        "skillId": skill_id,
    }
    assert installed_skills[0]["install"] == {"strategy": "workspace-overlay"}

    variant = config["comparison"]["variants"][0]["agent"]
    assert variant["sandboxMode"] == "read-only"
    assert variant["approvalPolicy"] == "never"
    assert variant["webSearchEnabled"] is False
    assert variant["networkAccessEnabled"] is False


@pytest.mark.parametrize("suite", ISOLATED_SUITES)
def test_evolution_suite_coverage_matches_declared_diverse_prompts(suite: str) -> None:
    suite_root = EVALUATION_ROOT / suite
    config = yaml.safe_load((suite_root / "evaluation.yaml").read_text(encoding="utf-8"))
    coverage = json.loads(
        (suite_root / "prompt-coverage.json").read_text(encoding="utf-8")
    )
    prompts = config["task"]["prompts"]
    cases = coverage["cases"]

    policy = coverage["policy"]

    assert len(prompts) >= policy["minimumPrompts"]
    assert {prompt["id"] for prompt in prompts} == {
        case["promptId"] for case in cases
    }
    assert len(cases) == len(prompts)
    assert len({case["taskFamily"] for case in cases}) >= policy["minimumTaskFamilies"]
    assert [case["caseKind"] for case in cases].count("naturalistic-forward") >= 2
    assert {case["caseKind"] for case in cases} >= {
        "naturalistic-forward",
        "generalization",
        "boundary-recovery",
    }
