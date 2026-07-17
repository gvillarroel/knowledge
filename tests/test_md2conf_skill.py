"""Contract tests for the standalone md2conf publishing skill."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "md2conf"
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "md2conf"


def test_skill_targets_the_active_distribution_and_version_checks() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "markdown-to-confluence==0.6.1" in skill
    assert "md2conf --version" in skill
    assert "md2conf --help" in skill
    assert "obsolete PyPI distribution named `md2conf`" in skill
    assert "pip install md2conf" not in skill
    assert "--comments" in skill
    assert "development-only" in skill


def test_skill_exposes_markdown_authority_and_destructive_surfaces() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
    safety = (SKILL_ROOT / "references" / "publishing-safety.md").read_text(
        encoding="utf-8"
    ).lower()

    assert "markdown as the authoritative source" in skill
    assert "never describe md2conf publication as a lossless confluence round trip" in skill
    assert "delete every existing page attachment" in skill
    assert "full label set returned by confluence" in skill
    assert "do not assume only global labels are affected" in skill
    assert "remove unspecified existing content properties" in skill
    assert "move or reorder children" in skill
    assert "assume partial completion" in skill
    assert "byte length rather than a content hash" in safety
    assert "explicit page ids" in safety
    assert "inline comments" in safety


def test_skill_keeps_conversion_offline_and_credentials_out_of_arguments() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "--local" in skill
    assert "disposable copy" in skill
    assert "It does not call Confluence" in skill
    assert "CONFLUENCE_API_KEY" in skill
    assert "never through `-a`, `--api-key`" in skill
    assert "--no-overwrite" in skill
    assert "--no-notify" in skill
    assert "--skip-update" in skill
    assert "--keep-update" in skill
    assert "[name](mailto:email)" in skill.lower()
    assert "first mention on a page can notify" in skill
    assert "--no-notify` only as a request" in skill


def test_skill_closes_reviews_with_local_and_remote_evidence() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "## Complete every response" in skill
    assert "Do not let an unavailable executable" in skill
    assert "one well-formed, tenant-compatible storage XML node" in skill
    assert "user lookup by name" in skill
    assert "conversion to `ri:user`" in skill
    assert "local mode cannot preview the lookup" in skill
    assert "full label API result" in skill
    assert "version-scoped reconciliation rule and the case-specific impact" in skill
    assert "`tags: []` therefore requests removal" in skill
    assert "`properties: {}` removes every non-synchronization property" in skill
    assert "creating a duplicate as an automatic repair" in skill
    assert "keeping the existing page Confluence-authored" in skill
    assert "separate, explicitly Markdown-owned page" in skill
    assert "authenticated-browser verification" in skill


def test_markdown_reference_covers_identity_hierarchy_and_raw_storage() -> None:
    contract = (SKILL_ROOT / "references" / "markdown-contract.md").read_text(
        encoding="utf-8"
    )

    assert "confluence-page-id" in contract
    assert 'page_id: "20250001023"' in contract
    assert "Reject duplicate explicit IDs" in contract
    assert "--root-page" in contract
    assert "--keep-hierarchy" in contract
    assert ".mdignore" in contract
    assert "synchronized: false" in contract
    assert "fenced `csf` block" in contract
    assert "xml-compatible" in contract.lower()
    assert "<br />" in contract
    assert "local mode cannot preview" in contract.lower()


def test_skill_covers_second_evolution_routing_and_reconciliation_edges() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    contract = (SKILL_ROOT / "references" / "markdown-contract.md").read_text(
        encoding="utf-8"
    )
    safety = (SKILL_ROOT / "references" / "publishing-safety.md").read_text(
        encoding="utf-8"
    )

    assert "can override the site-level `--space`" in skill
    assert "inline `confluence-page-id` and `confluence-space-key` values first" in skill
    assert "merge recursively" in skill
    assert "global values filling missing or null paths" in skill
    assert "deletion request contains only the name" in skill
    assert "Do not stop at predicting deletion" in skill
    assert "complete intended property set before any live command" in skill
    assert "current Confluence page version differs" in skill
    assert "inventory existing attachments" in skill
    assert "upload or reconcile every generated reference" in skill
    assert "generated body and title are current" in skill
    assert "correction only after destination review" in skill
    assert "unsupported nested matching" in contract
    assert "strict relative-page resolution" in contract
    assert "recursively coalesces document properties" in contract
    assert "same-name global/team/personal labels" in safety


def test_isolated_evaluation_compares_one_skill_with_an_offline_control() -> None:
    config = yaml.safe_load(
        (EVALUATION_ROOT / "evaluation.yaml").read_text(encoding="utf-8")
    )
    profiles = config["comparison"]["profiles"]

    assert len(profiles) == 2
    control = next(profile for profile in profiles if not profile["capabilities"])
    treatment = next(profile for profile in profiles if profile["capabilities"])
    assert control["isolation"] == {"inheritSystem": False}
    assert treatment["isolation"] == {"inheritSystem": False}
    assert treatment["capabilities"]["skills"] == [
        {
            "source": {
                "type": "local-path",
                "path": "skills/md2conf",
                "skillId": "md2conf",
            },
            "install": {"strategy": "workspace-overlay"},
        }
    ]

    agent = config["comparison"]["variants"][0]["agent"]
    assert agent["sandboxMode"] == "read-only"
    assert agent["approvalPolicy"] == "never"
    assert agent["webSearchEnabled"] is False
    assert agent["networkAccessEnabled"] is False


def test_evaluation_has_four_distinct_cases_and_real_fixtures() -> None:
    config = yaml.safe_load(
        (EVALUATION_ROOT / "evaluation.yaml").read_text(encoding="utf-8")
    )
    coverage = json.loads(
        (EVALUATION_ROOT / "prompt-coverage.json").read_text(encoding="utf-8")
    )
    prompts = config["task"]["prompts"]
    cases = coverage["cases"]

    assert len(prompts) == 4
    assert {prompt["id"] for prompt in prompts} == {
        case["promptId"] for case in cases
    }
    assert len({case["taskFamily"] for case in cases}) == 4
    assert [case["caseKind"] for case in cases].count("naturalistic-forward") == 2
    assert {case["caseKind"] for case in cases} >= {
        "naturalistic-forward",
        "generalization",
        "boundary-recovery",
    }

    fixture_root = EVALUATION_ROOT / "fixtures" / "workspaces" / "base"
    assert (fixture_root / "single" / "guide.md").is_file()
    assert (fixture_root / "tree" / ".mdignore").is_file()
    assert (fixture_root / "diagnose" / "operator-notes.txt").is_file()
    assert (fixture_root / "boundary" / "current-page.json").is_file()


def test_evolution_evaluation_has_varied_semantic_cases() -> None:
    config = yaml.safe_load(
        (EVALUATION_ROOT / "evolution.yaml").read_text(encoding="utf-8")
    )
    coverage = json.loads(
        (EVALUATION_ROOT / "evolution-coverage.json").read_text(encoding="utf-8")
    )
    prompts = config["task"]["prompts"]
    cases = coverage["cases"]

    assert len(prompts) == 17
    assert {prompt["id"] for prompt in prompts} == {
        case["promptId"] for case in cases
    }
    assert len({case["taskFamily"] for case in cases}) == 13
    assert {case["caseKind"] for case in cases} == {
        "naturalistic-forward",
        "generalization",
        "boundary-recovery",
    }
    for prompt in prompts:
        assertions = prompt["evaluation"]["assertions"]
        assert len(assertions) == 1
        assert assertions[0]["type"] == "llm-rubric"
        assert assertions[0]["provider"] == "skill-arena:judge:codex"
        assert "Pass only when" in assertions[0]["value"]

    shared = config["evaluation"]["assertions"]
    assert shared == [
        {
            "type": "javascript",
            "metric": "non-empty-response",
            "value": 'typeof output === "string" && output.trim().length >= 80',
        }
    ]
    assert config["evaluation"]["requests"] == 3


def test_evolution_evaluation_preserves_isolation_and_fixture_coverage() -> None:
    config = yaml.safe_load(
        (EVALUATION_ROOT / "evolution.yaml").read_text(encoding="utf-8")
    )
    profiles = config["comparison"]["profiles"]

    assert [profile["id"] for profile in profiles] == ["no-skill", "skill"]
    assert all(profile["isolation"] == {"inheritSystem": False} for profile in profiles)
    assert profiles[0]["capabilities"] == {}
    assert profiles[1]["capabilities"]["skills"][0]["source"] == {
        "type": "local-path",
        "path": "skills/md2conf",
        "skillId": "md2conf",
    }

    fixture_root = EVALUATION_ROOT / "fixtures" / "workspaces" / "base"
    required = [
        "auth/target.json",
        "attachment-incident/incident.json",
        "extensions/tenant.json",
        "mapping/target-state.json",
        "mentions/policy.json",
        "metadata-matrix/neither-state.json",
        "metadata-matrix/empty-state.json",
        "metadata-matrix/properties-only-state.json",
        "metadata-matrix/tags-only-state.json",
        "metadata/remote-state.json",
        "recovery/incident.json",
        "single/guide.md",
        "tree/.mdignore",
    ]
    assert all((fixture_root / relative).is_file() for relative in required)


def test_second_evolution_development_corpus_is_distinct_and_frozen() -> None:
    config = yaml.safe_load(
        (EVALUATION_ROOT / "evolution-v2-development.yaml").read_text(
            encoding="utf-8"
        )
    )
    coverage = json.loads(
        (EVALUATION_ROOT / "evolution-v2-development-coverage.json").read_text(
            encoding="utf-8"
        )
    )
    prompts = config["task"]["prompts"]
    cases = coverage["cases"]

    assert len(prompts) == 7
    assert len({case["taskFamily"] for case in cases}) == 7
    assert {prompt["id"] for prompt in prompts} == {
        case["promptId"] for case in cases
    }
    assert {case["caseKind"] for case in cases} == {
        "naturalistic-forward",
        "generalization",
        "boundary-recovery",
    }
    assert [profile["id"] for profile in config["comparison"]["profiles"]] == [
        "no-skill",
        "current-v1",
        "candidate-v2",
    ]
    assert config["comparison"]["profiles"][1]["capabilities"]["skills"][0][
        "source"
    ]["path"] == "evaluations/md2conf/fixtures/skills/md2conf-v1"
    assert config["comparison"]["profiles"][2]["capabilities"]["skills"][0][
        "source"
    ]["path"] == "skills/md2conf"
    assert config["evaluation"]["requests"] == 1
    for prompt in prompts:
        rubrics = prompt["evaluation"]["assertions"]
        assert len(rubrics) == 2
        assert {rubric["provider"] for rubric in rubrics} == {
            "skill-arena:judge:codex"
        }
        assert sum("core-safety" in rubric["metric"] for rubric in rubrics) == 1
        assert sum(rubric["metric"].endswith("-mechanics") for rubric in rubrics) == 1

    snapshot = (
        EVALUATION_ROOT / "fixtures" / "skills" / "md2conf-v1" / "SKILL.md"
    ).read_bytes()
    assert hashlib.sha256(snapshot).hexdigest() == (
        "04e83ffaf1aa00c6b79cc69b35312a68fed8307a26bfd2a9523452ba47ccc8c7"
    )

    fixture_root = (
        EVALUATION_ROOT / "fixtures" / "workspaces" / "v2-development"
    )
    required = [
        "space-routing/approved-target.json",
        "property-merge/global-properties.yaml",
        "label-collision/remote-state.json",
        "unmanaged-overwrite/remote-state.json",
        "current-body-attachment/remote-state.json",
        "mapping-precedence/conflicted.md",
        "ignore-rules/.mdignore",
        "ignore-rules/drafts/obsolete.md",
    ]
    assert all((fixture_root / relative).is_file() for relative in required)


def test_second_evolution_qualification_is_unseen_and_cross_variant() -> None:
    development = yaml.safe_load(
        (EVALUATION_ROOT / "evolution-v2-development.yaml").read_text(
            encoding="utf-8"
        )
    )
    qualification = yaml.safe_load(
        (EVALUATION_ROOT / "evolution-v2-qualification.yaml").read_text(
            encoding="utf-8"
        )
    )
    coverage = json.loads(
        (EVALUATION_ROOT / "evolution-v2-qualification-coverage.json").read_text(
            encoding="utf-8"
        )
    )
    prompts = qualification["task"]["prompts"]

    assert len(prompts) == 4
    assert len({case["taskFamily"] for case in coverage["cases"]}) == 4
    assert {prompt["id"] for prompt in prompts}.isdisjoint(
        {prompt["id"] for prompt in development["task"]["prompts"]}
    )
    assert [profile["id"] for profile in qualification["comparison"]["profiles"]] == [
        "no-skill",
        "frozen-v1",
        "candidate",
    ]
    assert {
        variant["agent"]["adapter"]
        for variant in qualification["comparison"]["variants"]
    } == {"codex", "antigravity-cli"}
    antigravity = next(
        variant
        for variant in qualification["comparison"]["variants"]
        if variant["agent"]["adapter"] == "antigravity-cli"
    )["agent"]
    assert antigravity["sandboxMode"] == "workspace-write"
    assert antigravity["config"]["mode"] == "accept-edits"
    assert qualification["evaluation"]["requests"] == 1
    assert qualification["evaluation"]["maxConcurrency"] == 2
    assert qualification["evaluation"]["noCache"] is True
    for prompt in prompts:
        rubrics = prompt["evaluation"]["assertions"]
        assert len(rubrics) == 2
        assert {rubric["provider"] for rubric in rubrics} == {
            "skill-arena:judge:codex"
        }
