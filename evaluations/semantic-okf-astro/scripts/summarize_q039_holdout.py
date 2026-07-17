#!/usr/bin/env python3
"""Publish a checked, evidence-audited summary of the frozen q039 holdout."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
REPORTS = EVALUATION / "reports"
COMMON_PATH = SCRIPT.with_name("summarize_q040_skill_arena.py")
ANSWER_SCORER_PATH = SCRIPT.with_name("compare_hard_answers.py")
ACCEPTED_RUN_ID = "2026-07-16T11-59-44-962Z-compare"
BENCHMARK_ID = "semantic-okf-astro-q039-ensemble-post-tuning-holdout"
QUESTION_ID = "q039"
VARIANT_ID = "pi-luna-only"
PROFILES = ("knowledge-only-control", "ensemble-consult-treatment")
SCHEMA_VERSION = "semantic-okf-astro-q039-holdout-result/1.0"
DEFAULT_COMPARE_DIR = REPO / "results" / BENCHMARK_ID / ACCEPTED_RUN_ID
DEFAULT_BUNDLE = (
    EVALUATION
    / "results"
    / "runs"
    / "20260716-astro-generic-01"
    / "bundles"
    / "ensemble-a"
)
DEFAULT_CROSSWALK = EVALUATION / "corpus" / "source-combination.json"


def load_common():
    """Load the shared strict parser and authoritative evidence validator."""

    specification = importlib.util.spec_from_file_location(
        "semantic_okf_astro_skill_arena_summary_support", COMMON_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load shared summary support: {COMMON_PATH}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


COMMON = load_common()
SummaryError = COMMON.SummaryError


def load_answer_scorer():
    """Load the accepted hard-answer sufficiency scorer used by the 40-case report."""

    specification = importlib.util.spec_from_file_location(
        "semantic_okf_astro_hard_answer_score_support", ANSWER_SCORER_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load hard-answer scorer: {ANSWER_SCORER_PATH}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


ANSWER_SCORER = load_answer_scorer()


def pct(value: float) -> str:
    """Render one pass ratio."""

    return f"{100.0 * value:.0f}%"


def tree_sha256(root: Path) -> str:
    """Bind a skill tree using the same canonical algorithm as its frozen manifest."""

    rows = [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": COMMON.sha256_file(path),
        }
        for path in sorted(
            item
            for item in root.rglob("*")
            if item.is_file() and "__pycache__" not in item.parts
        )
    ]
    return COMMON.sha256_bytes(COMMON.canonical_json(rows).encode("utf-8"))


def execution_traces(parent: Path, accepted: Path) -> list[dict[str, Any]]:
    """Classify every append-only preflight, dry-run, or completed live trace."""

    traces: list[dict[str, Any]] = []
    completed_live = 0
    for directory in sorted(parent.glob("*-compare")):
        log_path = directory / "execution.log"
        log = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
        started_live = "Starting evaluation " in log
        completed = (directory / "promptfoo-results.json").is_file()
        dry_run = "dry-run completed without promptfoo eval" in log
        if completed:
            completed_live += 1
        if directory == accepted:
            classification = "accepted completed live holdout"
        elif dry_run:
            classification = "preflight dry-run; no model evaluation"
        elif started_live:
            classification = "non-accepted live trace"
        else:
            classification = "incomplete preflight; no model evaluation"
        traces.append(
            {
                "run_id": directory.name,
                "accepted": directory == accepted,
                "started_live_evaluation": started_live,
                "completed_live_evaluation": completed,
                "classification": classification,
                "execution_log_sha256": COMMON.sha256_file(log_path) if log_path.is_file() else None,
            }
        )
    if completed_live != 1:
        raise SummaryError(
            f"expected exactly one completed q039 live evaluation; found {completed_live}"
        )
    return traces


def summarize(
    compare_dir: Path,
    *,
    bundle: Path = DEFAULT_BUNDLE,
    crosswalk: Path = DEFAULT_CROSSWALK,
) -> dict[str, Any]:
    """Cross-check the one accepted live pair and reconstruct all evidence rows."""

    compare_dir = compare_dir.resolve()
    bundle, crosswalk = bundle.resolve(), crosswalk.resolve()
    if compare_dir.name != ACCEPTED_RUN_ID:
        raise SummaryError(
            f"the frozen accepted q039 run is {ACCEPTED_RUN_ID}; found {compare_dir.name}"
        )
    if not compare_dir.is_dir():
        raise SummaryError(f"compare directory does not exist: {compare_dir}")
    promptfoo_path = compare_dir / "promptfoo-results.json"
    config_path = compare_dir / "promptfooconfig.yaml"
    summary_path = compare_dir / "summary.json"
    promptfoo = COMMON.load_json(promptfoo_path)
    normalized = COMMON.load_json(summary_path)
    eval_id = promptfoo.get("evalId")
    if not isinstance(eval_id, str) or normalized.get("evalId") != eval_id:
        raise SummaryError("promptfoo and normalized summaries disagree on eval ID")
    if normalized.get("benchmarkId") != BENCHMARK_ID:
        raise SummaryError("q039 summary benchmark ID differs")
    providers = normalized.get("providers")
    if (
        not isinstance(providers, list)
        or [row.get("profileId") for row in providers if isinstance(row, dict)]
        != list(PROFILES)
    ):
        raise SummaryError("q039 profile IDs/order differ")
    if normalized.get("unsupportedCells") != []:
        raise SummaryError("q039 comparison contains unsupported cells")

    profiles = COMMON.exact_profiles(
        "ensemble",
        promptfoo,
        normalized,
        expected_benchmark=BENCHMARK_ID,
        expected_prompt=QUESTION_ID,
        profiles_expected=PROFILES,
    )
    ledger = COMMON.AuthoritativeLedger(bundle / "semantic" / "records.jsonl", crosswalk)
    truth_path = EVALUATION / "benchmark" / "hard-ground-truth.jsonl"
    truth_rows = COMMON.load_jsonl(truth_path)
    truth = next((row for row in truth_rows if row.get("id") == QUESTION_ID), None)
    if not isinstance(truth, dict):
        raise SummaryError("q039 hard-answer ground truth is missing")
    document_body_lengths = {
        ledger.document_by_identity[identity]: len(record["body"])
        for identity, record in ledger.by_identity.items()
    }
    for profile in profiles:
        profile["evidence_validation"] = COMMON.validate_response_evidence(
            profile["parsed_response"], ledger
        )
        evidence = profile["parsed_response"]["evidence"]
        selected_hits = [
            {
                **row,
                "document_id": validation["document_id"],
                "evidence_validation": validation,
            }
            for row, validation in zip(
                evidence, profile["evidence_validation"]["rows"], strict=True
            )
        ]
        profile["benchmark_evidence_audit"] = ANSWER_SCORER.score_answer(
            truth, selected_hits, document_body_lengths
        )
    stats = promptfoo.get("results", {}).get("stats")
    if not isinstance(stats, dict) or (
        stats.get("successes"), stats.get("failures"), stats.get("errors")
    ) != (2, 0, 0):
        raise SummaryError("accepted q039 aggregate stats must be 2/0/0")
    if not all(profile["pass"] for profile in profiles):
        raise SummaryError("both accepted q039 cells must pass their three assertions")

    control, treatment = profiles
    traces = execution_traces(compare_dir.parent, compare_dir)
    config_source = EVALUATION / "skill-arena" / "q039-ensemble-holdout.yaml"
    manifest_source = EVALUATION / "skill-arena" / "q039-ensemble-holdout-manifest.json"
    coverage_source = EVALUATION / "skill-arena" / "q039-ensemble-holdout-prompt-coverage.json"
    manifest = COMMON.load_json(manifest_source)
    frozen_skill_sha = manifest.get("treatment_skill", {}).get("tree_sha256")
    current_skill_sha = tree_sha256(REPO / "skills" / "consult-semantic-okf-ensemble")
    scenarios = normalized.get("scenarioSummaries")
    if not isinstance(scenarios, list):
        raise SummaryError("q039 summary has no scenario workspaces")
    workspace_by_profile: dict[str, Path] = {}
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise SummaryError("q039 scenario summary is malformed")
        profile_id, raw_workspace = scenario.get("profileId"), scenario.get(
            "workspaceDirectory"
        )
        if profile_id not in PROFILES or not isinstance(raw_workspace, str):
            raise SummaryError("q039 scenario workspace identity differs")
        workspace = Path(raw_workspace).resolve()
        if not workspace.is_relative_to(compare_dir.parent):
            raise SummaryError("q039 archived scenario workspace escapes its result root")
        workspace_by_profile[profile_id] = workspace
    if tuple(workspace_by_profile) != PROFILES:
        raise SummaryError("q039 archived scenario workspaces differ from the paired profiles")
    control_skill = (
        workspace_by_profile[PROFILES[0]] / "skills" / "consult-semantic-okf-ensemble"
    )
    executed_skill = (
        workspace_by_profile[PROFILES[1]] / "skills" / "consult-semantic-okf-ensemble"
    )
    if control_skill.exists() or not executed_skill.is_dir():
        raise SummaryError("q039 archived control/treatment skill isolation differs")
    executed_skill_sha = tree_sha256(executed_skill)
    if (
        not isinstance(frozen_skill_sha, str)
        or current_skill_sha != frozen_skill_sha
        or executed_skill_sha != frozen_skill_sha
    ):
        raise SummaryError("ensemble treatment skill changed after the frozen q039 manifest")
    if manifest.get("config", {}).get("sha256") != COMMON.sha256_file(config_source):
        raise SummaryError("q039 config differs from its frozen manifest")
    if manifest.get("prompt", {}).get("coverage_sha256") != COMMON.sha256_file(
        coverage_source
    ):
        raise SummaryError("q039 prompt coverage differs from its frozen manifest")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "holdout": {
            "post_tuning": True,
            "frozen_before_live_execution": True,
            "completed_live_evaluations": 1,
            "skill_changed_after_result": False,
            "executed_skill_tree_sha256": executed_skill_sha,
            "causal_scope": "one same-model, same-bundle q039 control/treatment pair",
        },
        "accepted_run": {
            "run_id": compare_dir.name,
            "eval_id": eval_id,
            "benchmark_id": BENCHMARK_ID,
            "question_id": QUESTION_ID,
            "variant_id": VARIANT_ID,
            "compare_directory": COMMON.repository_path(compare_dir),
        },
        "outcome": {
            "control_pass_rate": float(control["pass"]),
            "treatment_pass_rate": float(treatment["pass"]),
            "absolute_percentage_point_delta": 100.0
            * (float(treatment["pass"]) - float(control["pass"])),
            "control_evidence_status": control["evidence_validation"]["status"],
            "treatment_evidence_status": treatment["evidence_validation"]["status"],
            "interpretation": (
                "The treatment passes the frozen response-contract and evidence-validity gates, "
                "but the control also passes. This is contract-level no-regression evidence, not "
                "evidence of superiority or exact ground-truth sufficiency parity."
            ),
        },
        "profiles": profiles,
        "source_artifacts": {
            "holdout_config": COMMON.artifact(config_source.resolve()),
            "holdout_manifest": COMMON.artifact(manifest_source.resolve()),
            "prompt_coverage": COMMON.artifact(coverage_source.resolve()),
            "promptfoo_results": COMMON.artifact(promptfoo_path),
            "promptfoo_config": COMMON.artifact(config_path),
            "skill_arena_summary": COMMON.artifact(summary_path),
            "authoritative_records": COMMON.artifact(
                bundle / "semantic" / "records.jsonl"
            ),
            "source_crosswalk": COMMON.artifact(crosswalk),
            "hard_answer_ground_truth": COMMON.artifact(truth_path.resolve()),
        },
        "execution_traces": traces,
        "privacy": {
            "raw_environment_copied": False,
            "raw_workspace_paths_copied": False,
            "parsed_model_responses_retained_exactly": True,
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the compact holdout audit and both exact parsed answers."""

    accepted, outcome = report["accepted_run"], report["outcome"]
    lines = [
        "# Frozen q039 Ensemble Holdout",
        "",
        f"Accepted run `{accepted['run_id']}` (`{accepted['eval_id']}`) is the only completed live evaluation. The config, prompt, bundle, runner, and treatment skill were frozen before execution and the skill was not changed after inspecting the result.",
        "",
        "| Profile | Contract | Evidence valid | Required docs | Exact spans | Atomic claims | Negatives | Latency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for profile in report["profiles"]:
        evidence = profile["evidence_validation"]
        audit = profile["benchmark_evidence_audit"]
        lines.append(
            f"| `{profile['profile_id']}` | {'yes' if profile['pass'] else 'no'} | "
            f"{evidence['valid']}/{evidence['returned']} ({evidence['status']}) | "
            f"{pct(audit['required_document_coverage'])} | "
            f"{pct(audit['authoritative_evidence_completeness'])} | "
            f"{pct(audit['atomic_claim_evidence_completeness'])} | "
            f"{pct(audit['important_negative_evidence_completeness'])} | "
            f"{profile['latency_ms']} ms |"
        )
    lines.extend(
        [
            "",
            f"Control {pct(outcome['control_pass_rate'])}, treatment {pct(outcome['treatment_pass_rate'])}, delta {outcome['absolute_percentage_point_delta']:.0f} percentage points. {outcome['interpretation']}",
            "",
            "Both answers distinguish processed module deduplication from unprocessed inline scripts, constrain `data-astro-rerun` to intentional repeatable work, use Astro navigation lifecycle events, and guard or clean up persistent global listeners.",
            "The strict evaluator-owned evidence audit is narrower than that manual facet audit. The treatment covers 2/3 required pages, 3/4 exact spans, 4/5 atomic claim groups, and both important negatives because it cites the authoritative Astro transitions module instead of the required directives-reference span. This is valid alternative evidence, but it does not receive exact-span credit.",
            "",
            "## Integrity bindings",
            "",
            "| Artifact | Bytes | SHA-256 |",
            "|---|---:|---|",
        ]
    )
    for name, artifact in report["source_artifacts"].items():
        lines.append(f"| {name} | {artifact['bytes']} | `{artifact['sha256']}` |")
    lines.extend(["", "## Exact parsed answers", ""])
    for profile in report["profiles"]:
        lines.extend(
            [
                f"### {profile['profile_id']}",
                "",
                "```json",
                json.dumps(
                    profile["parsed_response"],
                    ensure_ascii=False,
                    indent=2,
                    allow_nan=False,
                ),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Append-only execution traces",
            "",
            "| Run | Accepted | Live started | Live completed | Classification |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for trace in report["execution_traces"]:
        lines.append(
            f"| `{trace['run_id']}` | {'yes' if trace['accepted'] else 'no'} | "
            f"{'yes' if trace['started_live_evaluation'] else 'no'} | "
            f"{'yes' if trace['completed_live_evaluation'] else 'no'} | "
            f"{trace['classification']} |"
        )
    lines.extend(
        [
            "",
            "Promptfoo contract scoring and authoritative evidence validity are separate gates. Every evidence row above was reconstructed from the frozen ledger and crosswalk. No MCP runtime participated.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse checked inputs and outputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare-dir", type=Path, default=DEFAULT_COMPARE_DIR)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--crosswalk", type=Path, default=DEFAULT_CROSSWALK)
    parser.add_argument(
        "--json-output", type=Path, default=REPORTS / "skill-arena-q039-holdout.json"
    )
    parser.add_argument(
        "--markdown-output", type=Path, default=REPORTS / "skill-arena-q039-holdout.md"
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Write or byte-check the compact report."""

    args = parse_args(argv)
    try:
        report = summarize(args.compare_dir, bundle=args.bundle, crosswalk=args.crosswalk)
        json_text = COMMON.pretty_json(report)
        markdown_text = render_markdown(report)
        if args.check:
            COMMON.check_content(args.json_output.resolve(), json_text)
            COMMON.check_content(args.markdown_output.resolve(), markdown_text)
        else:
            COMMON.atomic_write(args.json_output.resolve(), json_text)
            COMMON.atomic_write(args.markdown_output.resolve(), markdown_text)
    except (SummaryError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "check" if args.check else "write",
                "eval_id": report["accepted_run"]["eval_id"],
                "control": pct(report["outcome"]["control_pass_rate"]),
                "treatment": pct(report["outcome"]["treatment_pass_rate"]),
                "treatment_evidence": report["outcome"]["treatment_evidence_status"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
