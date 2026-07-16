#!/usr/bin/env python3
"""Generate the frozen q039 ensemble-only post-tuning Skill Arena holdout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
OUTPUT = EVALUATION / "skill-arena"

# Import the reviewed serialization, hashing, input, and atomic-publication helpers
# used by the q040 paired comparisons instead of creating a second implementation.
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
import generate_skill_arena_configs as shared  # noqa: E402


SCHEMA = "semantic-okf-astro-q039-ensemble-holdout-manifest/1.0"
QUESTION_ID = "q039"
SKILL_ID = "consult-semantic-okf-ensemble"
MODEL = "openai-codex/gpt-5.6-luna"
CONFIG_NAME = "q039-ensemble-holdout.yaml"
COVERAGE_NAME = "q039-ensemble-holdout-prompt-coverage.json"
MANIFEST_NAME = "q039-ensemble-holdout-manifest.json"
EXPECTED_QUESTIONS_SHA256 = (
    "781b68739af5f5867dc67189dc08ab25ccca0ce809c89543709961bacdd7c948"
)
EXPECTED_BUILD_REPORT_SHA256 = (
    "76d189ae10d34ff8b328c920bcc9b8d5bca03055090fdf605529f2a0b44aaba7"
)
EXPECTED_BUNDLE_TREE_SHA256 = (
    "23473bc95b393ce62c94ac2395fa7b8525c2378c0150d4cea49776d3f4e9dfb9"
)
EXPECTED_SKILL_TREE_SHA256 = (
    "ab66ade281810abc10ff626d3189d78314f8c939874c3aed86634e1023f8fe19"
)
EXPECTED_RUNNER_SHA256 = (
    "6fad208c56322d67d7779a0a5c90434cc823da3a5ba18d8f3d7e0bbcbda24c18"
)
EXPECTED_PROMPT_SHA256 = (
    "e6182136b6e9674d9b4fec26c585d26f2215fc2cc6655dd0d38e3f7abd900e70"
)
EXPECTED_CONFIG_SHA256 = (
    "6fe54755b1165c5e147255f431e088e19639bf7b61ded7df19827be80c20054e"
)
EXPECTED_QUESTION = (
    "After enabling ClientRouter, a page initializer fires twice on some navigations "
    "and not at all on others. Derive a script-loading contract covering processed "
    "module deduplication, inline scripts, data-astro-rerun, lifecycle events, and "
    "guards for persistent global listeners."
)


def _load_q039(path: Path) -> dict[str, Any]:
    """Load the frozen natural question while deliberately discarding qrels."""

    if shared.sha256_file(path) != EXPECTED_QUESTIONS_SHA256:
        raise shared.ConfigError("frozen hard-question input hash differs")
    try:
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise shared.ConfigError(f"cannot load hard questions: {exc}") from exc
    row = next(
        (
            item
            for item in rows
            if isinstance(item, dict) and item.get("id") == QUESTION_ID
        ),
        None,
    )
    if not isinstance(row, dict) or set(row) != {
        "id",
        "question",
        "question_type",
        "qrels",
    }:
        raise shared.ConfigError("q039 is missing or malformed")
    if row["question"] != EXPECTED_QUESTION or row["question_type"] != "hard":
        raise shared.ConfigError("frozen q039 wording or type differs")
    return {
        "id": row["id"],
        "question": row["question"],
        "question_type": row["question_type"],
    }


def _holdout_question(question: str) -> str:
    """Make the already-declared inline-script facet explicit without adding an answer."""

    marker = "inline scripts, data-astro-rerun"
    if marker not in question:
        raise shared.ConfigError("q039 no longer contains its inline-script facet")
    return question.replace(
        marker,
        "inline scripts (including `is:inline`), `data-astro-rerun`",
        1,
    )


def _response_contract_assertion() -> str:
    """Return a generic grounded-answer JSON shape check with no answer key."""

    return """try {
  const value = JSON.parse(output.trim());
  if (JSON.stringify(Object.keys(value)) !== JSON.stringify(['question_id','answer','evidence'])) return false;
  if (value.question_id !== 'q039' || !Array.isArray(value.evidence)) return false;
  if (value.answer === null) return value.evidence.length === 0;
  if (JSON.stringify(Object.keys(value.answer)) !== JSON.stringify(['summary','claims'])) return false;
  if (typeof value.answer.summary !== 'string' || !value.answer.summary.trim() || !Array.isArray(value.answer.claims)) return false;
  if (!value.answer.claims.every((row) => JSON.stringify(Object.keys(row)) === JSON.stringify(['statement','evidence_indices']) && typeof row.statement === 'string' && row.statement.trim() && Array.isArray(row.evidence_indices) && row.evidence_indices.every(Number.isInteger))) return false;
  return value.evidence.every((row) => JSON.stringify(Object.keys(row)) === JSON.stringify(['source_id','record_id','concept_path','source_path','record_sha256','locator','text_sha256']) && typeof row.source_id === 'string' && typeof row.record_id === 'string' && typeof row.concept_path === 'string' && typeof row.source_path === 'string' && /^[0-9a-f]{64}$/.test(row.record_sha256) && row.locator && typeof row.locator === 'object' && /^[0-9a-f]{64}$/.test(row.text_sha256));
} catch { return false; }"""


def _grounded_assertion() -> str:
    """Require evidence-linked statements without encoding expected statements."""

    return """try {
  const value = JSON.parse(output.trim());
  if (value.answer === null || !Array.isArray(value.evidence) || value.evidence.length === 0) return false;
  if (!Array.isArray(value.answer.claims) || value.answer.claims.length === 0) return false;
  return value.answer.claims.every((claim) => claim.evidence_indices.length > 0 && claim.evidence_indices.every((index) => index >= 0 && index < value.evidence.length));
} catch { return false; }"""


def _prompt(question: str) -> str:
    """Render the identical, non-leaking task supplied to both holdout cells."""

    return f"""Answer the Astro technical question below using only the published Semantic OKF snapshot at `knowledge/`. Do not use the web, model memory, or guesses. Treat the snapshot as immutable. If it cannot support an answer, return `answer: null` and an empty `evidence` array.

Question: {_holdout_question(question)}

Return JSON only with top-level keys `question_id`, `answer`, and `evidence`, in that order. Set `question_id` to `q039`. A non-null `answer` must contain `summary` and `claims`, in that order. Give a precise 180-320 word synthesis addressing every facet named in the question. Each claim must contain exactly `statement` and `evidence_indices`; indices are zero-based references into `evidence`. Every evidence row must contain exactly `source_id`, `record_id`, `concept_path`, `source_path`, `record_sha256`, `locator`, and `text_sha256`, copied from an exact validated consultation hit. Keep evidence in first-use order. Do not include benchmark-only relevance labels or unsupported facts."""


def _coverage() -> dict[str, Any]:
    """Describe the intentionally single-case post-tuning holdout."""

    return {
        "schemaVersion": 1,
        "policy": {
            "minimumPrompts": 1,
            "minimumTaskFamilies": 1,
            "minimumNaturalisticCases": 0,
            "requiredCaseKinds": ["boundary-recovery"],
            "maximumPromptWords": 320,
            "maximumPairwiseJaccard": 1.0,
            "maximumSingleFamilyShare": 1.0,
        },
        "cases": [
            {
                "promptId": QUESTION_ID,
                "caseKind": "boundary-recovery",
                "taskFamily": "client-router-script-lifecycle",
            }
        ],
    }


def _config(run_dir: str, question: Mapping[str, Any]) -> dict[str, Any]:
    """Create one same-bundle knowledge-only/control versus ensemble comparison."""

    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": "semantic-okf-astro-q039-ensemble-post-tuning-holdout",
            "description": (
                "Frozen q039 same-bundle knowledge-only control versus the final "
                "ensemble consultation skill."
            ),
            "tags": [
                "compare",
                "semantic-okf",
                "astro",
                "q039",
                "post-tuning-holdout",
                "paired",
                "isolated",
                "cli",
                "no-mcp",
            ],
        },
        "task": {
            "prompts": [
                {
                    "id": QUESTION_ID,
                    "description": (
                        "hard ClientRouter script lifecycle and duplication synthesis"
                    ),
                    "prompt": _prompt(str(question["question"])),
                    "evaluation": {
                        "assertions": [
                            {
                                "type": "javascript",
                                "metric": "response-contract",
                                "value": _response_contract_assertion(),
                            },
                            {
                                "type": "javascript",
                                "metric": "grounded-answer",
                                "value": _grounded_assertion(),
                            },
                        ]
                    },
                }
            ]
        },
        "workspace": {
            "sources": [
                {
                    "id": "ensemble-bundle",
                    "type": "local-path",
                    "path": f"{run_dir}/bundles/ensemble-a",
                    "target": "/knowledge",
                },
                {
                    "id": "pi-luna-runner",
                    "type": "local-path",
                    "path": "evaluations/semantic-okf-builder/fixtures/workspaces/base/bin",
                    "target": "/bin",
                },
            ],
            "setup": {
                "initializeGit": True,
                "env": {
                    "HF_HUB_OFFLINE": "1",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SEMANTIC_OKF_BUNDLE": "$WORKSPACE/knowledge",
                    "TRANSFORMERS_OFFLINE": "1",
                },
            },
        },
        "evaluation": {
            "assertions": [{"type": "is-json", "metric": "response-format"}],
            "requests": 1,
            "timeoutMs": 600000,
            "tracing": False,
            "maxConcurrency": 1,
            "noCache": True,
        },
        "comparison": {
            "profiles": [
                {
                    "id": "knowledge-only-control",
                    "description": (
                        "The immutable ensemble bundle with no declared consultation skill."
                    ),
                    "isolation": {"inheritSystem": False},
                    "capabilities": {},
                    "output": {
                        "tags": ["control", "knowledge-only", "post-tuning-holdout"],
                        "labels": {
                            "capability": "none",
                            "causal_role": "passive-control",
                        },
                    },
                },
                {
                    "id": "ensemble-consult-treatment",
                    "description": (
                        "The same immutable ensemble bundle with only the ensemble "
                        "consultation skill installed."
                    ),
                    "isolation": {"inheritSystem": False},
                    "capabilities": {
                        "skills": [
                            {
                                "source": {
                                    "type": "local-path",
                                    "path": f"skills/{SKILL_ID}",
                                    "skillId": SKILL_ID,
                                },
                                "install": {"strategy": "workspace-overlay"},
                            }
                        ]
                    },
                    "output": {
                        "tags": [
                            "treatment",
                            "ensemble",
                            "post-tuning-holdout",
                            "cli",
                            "no-mcp",
                        ],
                        "labels": {
                            "capability": SKILL_ID,
                            "causal_role": "treatment",
                        },
                    },
                },
            ],
            "variants": [
                {
                    "id": "pi-luna-only",
                    "description": (
                        "The same PI GPT-5.6 Luna route for both isolated holdout cells."
                    ),
                    "agent": {
                        "adapter": "pi",
                        "model": MODEL,
                        "executionMethod": "command",
                        "commandPath": "bin/pi-luna.ps1",
                        "sandboxMode": "read-only",
                        "approvalPolicy": "never",
                        "webSearchEnabled": False,
                        "networkAccessEnabled": True,
                        "reasoningEffort": "medium",
                        "additionalDirectories": [],
                        "cliEnv": {"PI_MODEL_TIMEOUT_SECONDS": "600"},
                        "envPassthrough": [
                            "SEMANTIC_OKF_PYTHON",
                            "SEMANTIC_OKF_HF_HUB_CACHE",
                        ],
                        "config": {},
                    },
                    "output": {
                        "tags": [
                            "pi",
                            "gpt-5.6-luna",
                            "isolated",
                            "post-tuning-holdout",
                            "cli",
                            "no-mcp",
                        ],
                        "labels": {"variantDisplayName": "PI GPT-5.6 Luna"},
                    },
                }
            ],
        },
    }


def build_artifacts(
    repo_root: Path = REPO,
    *,
    build_report_path: Path | None = None,
    questions_path: Path | None = None,
) -> dict[str, bytes]:
    """Build every holdout artifact in memory without publishing it."""

    repo_root = repo_root.resolve()
    evaluation = repo_root / "evaluations" / "semantic-okf-astro"
    build_report_path = (
        build_report_path or evaluation / "reports" / "build-comparison.json"
    ).resolve()
    questions_path = (
        questions_path or evaluation / "benchmark" / "hard-questions.jsonl"
    ).resolve()

    if shared.sha256_file(build_report_path) != EXPECTED_BUILD_REPORT_SHA256:
        raise shared.ConfigError("frozen accepted build-report hash differs")
    build = shared.load_json(build_report_path)
    if build.get("status") != "pass" or build.get("authoritative_core_parity") is not True:
        raise shared.ConfigError("build report is not an accepted all-family parity run")
    run_dir = build.get("run_dir")
    if not isinstance(run_dir, str):
        raise shared.ConfigError("build report run_dir is missing")
    bundle = repo_root / run_dir / "bundles" / "ensemble-a"
    skill = repo_root / "skills" / SKILL_ID
    runner = (
        repo_root
        / "evaluations"
        / "semantic-okf-builder"
        / "fixtures"
        / "workspaces"
        / "base"
        / "bin"
        / "pi-luna.ps1"
    )
    for label, path in (("bundle", bundle), ("skill", skill)):
        if not path.is_dir():
            raise shared.ConfigError(f"frozen {label} is unavailable: {path}")
    if not runner.is_file():
        raise shared.ConfigError(f"frozen PI runner is unavailable: {runner}")
    bundle_tree_sha256 = shared.tree_sha256(bundle)
    skill_tree_sha256 = shared.tree_sha256(skill)
    runner_sha256 = shared.sha256_file(runner)
    if bundle_tree_sha256 != EXPECTED_BUNDLE_TREE_SHA256:
        raise shared.ConfigError("frozen ensemble bundle tree hash differs")
    if skill_tree_sha256 != EXPECTED_SKILL_TREE_SHA256:
        raise shared.ConfigError("frozen ensemble consultation skill tree hash differs")
    if runner_sha256 != EXPECTED_RUNNER_SHA256:
        raise shared.ConfigError("frozen PI runner hash differs")

    question = _load_q039(questions_path)
    coverage = _coverage()
    config = _config(run_dir, question)
    config_bytes = yaml.dump(
        config,
        Dumper=shared.Dumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    ).encode("utf-8")
    coverage_bytes = (
        json.dumps(coverage, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")

    prompt_text = config["task"]["prompts"][0]["prompt"]
    prompt_sha256 = shared.sha256_bytes(prompt_text.encode("utf-8"))
    config_sha256 = shared.sha256_bytes(config_bytes)
    if prompt_sha256 != EXPECTED_PROMPT_SHA256:
        raise shared.ConfigError("frozen q039 holdout prompt hash differs")
    if config_sha256 != EXPECTED_CONFIG_SHA256:
        raise shared.ConfigError("frozen q039 holdout config hash differs")
    manifest = {
        "schema_version": SCHEMA,
        "status": "pass",
        "interpretation": (
            "A frozen post-tuning q039 causal holdout: the only profile difference is "
            "installation of consult-semantic-okf-ensemble. No live result is part of "
            "this manifest."
        ),
        "holdout_protocol": {
            "frozen_before_live_execution": True,
            "live_evaluation_executed_by_generator": False,
            "result_inspection_authorized": False,
            "skill_changes_authorized": False,
            "profiles": [
                "knowledge-only-control",
                "ensemble-consult-treatment",
            ],
            "same_bundle": True,
            "same_model": True,
            "mcp_enabled": False,
        },
        "question": question,
        "question_source": {
            "path": questions_path.relative_to(repo_root).as_posix(),
            "sha256": shared.sha256_file(questions_path),
            "qrels_in_prompt": False,
        },
        "prompt": {
            "id": QUESTION_ID,
            "sha256": prompt_sha256,
            "coverage_path": (
                evaluation / "skill-arena" / COVERAGE_NAME
            ).relative_to(repo_root).as_posix(),
            "coverage_sha256": shared.sha256_bytes(coverage_bytes),
        },
        "build_report": {
            "path": build_report_path.relative_to(repo_root).as_posix(),
            "sha256": shared.sha256_file(build_report_path),
            "run_dir": run_dir,
        },
        "bundle": {
            "path": bundle.relative_to(repo_root).as_posix(),
            "tree_sha256": bundle_tree_sha256,
        },
        "treatment_skill": {
            "id": SKILL_ID,
            "path": skill.relative_to(repo_root).as_posix(),
            "tree_sha256": skill_tree_sha256,
        },
        "runner": {
            "path": runner.relative_to(repo_root).as_posix(),
            "sha256": runner_sha256,
        },
        "config": {
            "path": (
                evaluation / "skill-arena" / CONFIG_NAME
            ).relative_to(repo_root).as_posix(),
            "sha256": config_sha256,
        },
        "model": MODEL,
        "requests_per_cell": 1,
    }
    manifest_bytes = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    return {
        CONFIG_NAME: config_bytes,
        COVERAGE_NAME: coverage_bytes,
        MANIFEST_NAME: manifest_bytes,
    }


def _publish(output: Path, artifacts: Mapping[str, bytes]) -> None:
    """Publish deterministic artifacts atomically."""

    for name, payload in artifacts.items():
        shared.atomic_write(output / name, payload.decode("utf-8"))


def _check(output: Path, artifacts: Mapping[str, bytes]) -> list[str]:
    """Return missing or byte-drifted artifact names without modifying them."""

    failures = []
    for name, expected in artifacts.items():
        path = output / name
        if not path.is_file() or path.read_bytes() != expected:
            failures.append(name)
    return failures


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse deterministic generator options."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--build-report", type=Path)
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail on missing or drifted outputs without rewriting them.",
    )
    args = parser.parse_args(argv)
    args.repo_root = args.repo_root.resolve()
    if args.build_report is not None:
        args.build_report = args.build_report.resolve()
    if args.questions is not None:
        args.questions = args.questions.resolve()
    if args.output_dir is None:
        args.output_dir = (
            args.repo_root / "evaluations" / "semantic-okf-astro" / "skill-arena"
        )
    args.output_dir = args.output_dir.resolve()
    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Generate the holdout or verify that checked artifacts are unchanged."""

    args = parse_args(argv)
    try:
        artifacts = build_artifacts(
            args.repo_root,
            build_report_path=args.build_report,
            questions_path=args.questions,
        )
        if args.check:
            failures = _check(args.output_dir, artifacts)
            if failures:
                print(
                    json.dumps(
                        {"status": "error", "drifted": failures},
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                )
                return 2
        else:
            _publish(args.output_dir, artifacts)
    except (shared.ConfigError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(
            json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "check" if args.check else "write",
                "artifacts": list(artifacts),
                "output": str(args.output_dir),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
