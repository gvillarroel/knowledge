"""Publish the owning controller's terminal validation decision without case data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aggregate_development import host_path, number, read
from prepare_experiment import REPO, WORK, sha, write_json
from run_search import verified_state


def project(promotion, native_report):
    """Use an explicit field allowlist; preserve failures and the native decision."""
    if promotion.get("source") != "harbor" or native_report.get("source") != "harbor":
        raise ValueError("Expected native Harbor evidence")
    gate = promotion["holdout"]
    rules = {"minimumMeanGain": .01, "allowCaseRegressions": False, "requireNoErrors": True}
    if gate["promotionRules"] != rules:
        raise ValueError("Terminal rules differ from the frozen study")
    jobs = {str(host_path(row["jobDirectory"]).resolve()): row for row in native_report["jobs"]}
    expected_jobs = {str(host_path(path).resolve()) for path in promotion["jobs"].values()}
    if len(jobs) != 2 or set(jobs) != expected_jobs:
        raise ValueError("Expected exactly the two terminal native jobs")
    cases = len(gate["perCase"])
    if cases != 16 or len(promotion["holdoutChecksums"]) != cases:
        raise ValueError("Terminal portfolio must contain all 16 registered cells")
    roles = {}
    for role in ("baseline", "candidate"):
        directory = host_path(promotion["jobs"][role]).resolve()
        if not jobs[str(directory)]["complete"]:
            raise ValueError("Terminal native report is incomplete")
        stats = read(directory / "result.json")["stats"]
        fields = ("n_completed_trials", "n_errored_trials", "n_retries", "n_input_tokens", "n_output_tokens", "n_cache_tokens", "cost_usd")
        if any(stats.get(key) is None for key in fields):
            raise ValueError("Native completion or model accounting is unavailable")
        if stats["n_completed_trials"] != cases:
            raise ValueError("Native completion differs from the terminal portfolio")
        roles[role] = {
            "qualified": gate[role + "Qualified"], "evaluable": gate[role + "Evaluable"],
            "mean_ndcg_at_10": gate[role + "MeanReward"] if gate[role + "Qualified"] else None,
            "native_diagnostic_mean_reward": gate[role + "MeanReward"],
            "expected_cells": cases, "native_accounting": {key: stats[key] for key in fields},
            "job_result_sha256": sha(directory / "result.json"), "native_lock_sha256": sha(directory / "lock.json"),
        }
    if gate["promoted"] and any(not row["qualified"] or row["native_accounting"]["n_errored_trials"] for row in roles.values()):
        raise ValueError("Native promotion conflicts with the frozen complete-integrity requirement")
    comparable = all(row["qualified"] and row["evaluable"] for row in roles.values())
    return {
        "schema_version": "retrieval-validation-aggregates/1.0", "phase": "terminal-independent-validation",
        "source": "native Harbor jobs and owning reflective Pareto decision",
        "selected_candidate": gate["selectedCandidate"], "selected_skill_digest": promotion["selectedSkillDigest"],
        "development_profile_digest": promotion["developmentProfileDigest"],
        "decision": "promote" if gate["promoted"] else "keep-baseline",
        "native_status": gate["status"], "evaluable": gate["evaluable"],
        "mean_gain": gate["meanGain"] if comparable else None,
        "native_diagnostic_mean_gain": gate["meanGain"], "regressed_cell_count": len(gate["regressedCases"]),
        "required_rewards_complete": gate["requiredRewardsComplete"],
        "profile_matches_declared": gate["profileMatchesDeclared"], "rules": rules, "roles": roles,
        "source_groups": 2, "source_portfolio": ["FiQA", "SciFact"], "questions_per_source": 12,
        "scope": "Small reference-enriched transfer gate; not official BEIR or answer-quality scores",
        "further_evolution_permitted_in_this_study": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-report", type=Path, required=True)
    args = parser.parse_args()
    state = verified_state()
    if state["validationRelease"] is None or any(state["stages"][name]["status"] != "completed" for name in ("evolve", "validate")):
        raise ValueError("Publish only after completed evolution and terminal validation")
    source = WORK / "pareto/holdout/promotion.json"
    report = project(read(source), read(args.native_report))
    report.update(study=WORK.name, promotion_sha256=sha(source), native_report_sha256=sha(args.native_report))
    output = REPO / "evaluations/reports/evolution" / WORK.name / "validation"
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "aggregates.json", report)
    lines = ["# Terminal independent validation", "", "[Evolution studies](../../README.md) · [Exact aggregate provenance](aggregates.json)", "",
             f"Native decision: **{report['decision']}**. Selected profile: `{report['selected_candidate']}`. This is the single terminal gate for the frozen candidate; the study permits no further mutation or selection after release.", "",
             "The registered portfolio contains FiQA and SciFact, each with 12 queries and 985 reference-enriched documents. Each profile runs all eight skill families: 16 cells per profile and 32 native trials in total. Values below display binary nDCG@10 on a 0–100 scale. This bounded transfer check does not establish statistical significance or full-benchmark performance.", "",
             "| Profile | Qualified | Evaluable | Completed / expected cells | Errors | nDCG@10 |", "|---|---|---|---:|---:|---:|"]
    for role, row in report["roles"].items():
        stats = row["native_accounting"]
        lines.append(f"| {role} | {row['qualified']} | {row['evaluable']} | {stats['n_completed_trials']} / {row['expected_cells']} | {stats['n_errored_trials']} | {number(row['mean_ndcg_at_10'])} |")
    lines += ["", f"Mean gain: **{number(report['mean_gain'])} percentage points**. Regressed cells: **{report['regressed_cell_count']} / 16**. Native status: `{report['native_status']}`.", "",
              "Acceptance requires at least one percentage point of mean gain, no cell regression, complete integrity rewards, and no execution errors. Unqualified means are unavailable for comparison; native partial diagnostics remain explicitly labeled in the aggregate JSON.", "",
              "The JSON preserves native completion, retry, token and provider-cost accounting for both jobs. Local CPU and model execution costs are not priced. Private questions, references, task identities, per-case scores, diagnostic messages and trajectories are excluded from this publication.", "",
              "This decision governs only the frozen construction profile. The separately qualified Graphify correctness repair belongs to both baseline and candidate and is not an effect of profile evolution.", ""]
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "published-terminal-aggregates", "decision": report["decision"]}))


if __name__ == "__main__":
    main()
