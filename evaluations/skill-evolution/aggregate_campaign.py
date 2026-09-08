"""Join registered development reports without creating an archive or selecting a skill."""
from __future__ import annotations

import json
import math
from pathlib import Path

from aggregate_development import best_by_dataset, number, read, write_csv, write_navigation_views
from bridge import PRIMARY
from prepare_experiment import REPO, WORK, sha, write_json
from run_search import assert_frozen


PROFILES = (
    {"baseline", "neural-record", "quarter-expansion", "bm25-low-b", "stronger-titles"},
    {"baseline", "neural-expand", "neural-titles", "neural-bm25", "expand-titles"},
)
DATASETS = {"architecture", "astro", "data-science", "enterprise"}
ACCOUNTING_FIELDS = ("input_tokens", "output_tokens", "cache_tokens", "model_provider_cost_usd")
FIELDS = {
    "candidates": ("candidate", "qualified", "expected_trials", "completed_trials", "errors", "scored_trials", "mean_ndcg_at_10", "native_diagnostic_mean_reward", "skill_digest", "source_skill_digest", "job_id", "job_result_sha256", "native_lock_sha256", "mean_gain", "improved_cells", "unchanged_cells", "regressed_cells"),
    "routes": ("candidate", "dataset", "family", "route", "primary", "questions", "ndcg_at_10", "recall_at_10", "mrr_at_10", "full_qrel_coverage_at_10", "p95_ms", "double_build_seconds", "knowledge_bytes", "agent_execution_seconds", "native_trial_seconds"),
    "failures": ("candidate", "dataset", "family", "status", "error_type"),
    "primary_changes": ("candidate", "dataset", "family", "qualified_comparison", "baseline_ndcg_at_10", "candidate_ndcg_at_10", "delta_ndcg_at_10", "diagnostic_measured_delta"),
}


def project(generations):
    """Keep generation identities and native means; do not pool repeated baselines."""
    if len(generations) != 2:
        raise ValueError("Both complete development generations are required")
    common = ("study", "development_profile_digest", "execution_kind", "hardware_sha256", "scope")
    if any(not generations[0].get(key) or generations[0][key] != generations[1].get(key) for key in common):
        raise ValueError("Development comparison profiles or hardware commitments differ")
    result = {"schema_version": "retrieval-campaign-comparison/1.0", "study": "e5",
              "phase": "development-publication", "validation_used": False,
              "selection_established": False, "promotion_established": False,
              "comparison_scope": "Descriptive measurements across two generations; not a combined native archive",
              "finalist_scope": "Qualified members of the final native generation archive only",
              "candidates": [], "routes": [], "failures": [], "primary_changes": [],
              "generation_accounting": [], "sources": []}
    reference_routes = None
    for generation, aggregate in enumerate(generations):
        if (aggregate.get("schema_version") != "retrieval-evolution-aggregates/1.0"
                or aggregate.get("study") != "e5" or aggregate.get("generation") != generation
                or aggregate.get("phase") != "development" or aggregate.get("validation_used") is not False):
            raise ValueError("Expected the ordered e5 development projections")
        candidates = aggregate["candidates"]
        names = [row["candidate"] for row in candidates]
        if len(names) != 5 or set(names) != PROFILES[generation]:
            raise ValueError("Candidate membership differs from the frozen generation")
        if any(row["expected_trials"] != 32 or row["completed_trials"] != 32 for row in candidates):
            raise ValueError("All native trials must finish before campaign publication")
        seen = set()
        for row in aggregate["routes"]:
            key = (row["candidate"], row["dataset"], row["family"], row["route"])
            if (key in seen or row["candidate"] not in names or row["questions"] != 40
                    or row["dataset"] not in DATASETS or row["family"] not in PRIMARY
                    or row["primary"] is not (row["route"] == PRIMARY[row["family"]])):
                raise ValueError("Duplicate, unexpected or differently sized route measurement")
            seen.add(key)
            for metric in ("ndcg_at_10", "recall_at_10", "mrr_at_10", "full_qrel_coverage_at_10"):
                value = row[metric]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError("Expected finite development quality on the original 0-1 scale")
        baseline_routes = {(row["dataset"], row["family"], row["route"], row["primary"])
                           for row in aggregate["routes"] if row["candidate"] == "baseline"}
        if len(baseline_routes) != 72 or sum(key[3] for key in baseline_routes) != 32:
            raise ValueError("The registered baseline route grid is incomplete")
        if reference_routes is not None and baseline_routes != reference_routes:
            raise ValueError("Generation route grids differ")
        reference_routes = baseline_routes
        for row in candidates:
            if not isinstance(row["qualified"], bool):
                raise ValueError("Profile qualification must be a native boolean")
            routes = {(item["dataset"], item["family"], item["route"], item["primary"])
                      for item in aggregate["routes"] if item["candidate"] == row["candidate"]}
            mean = row["mean_ndcg_at_10"]
            if row["qualified"]:
                if (row["errors"] != 0 or row["scored_trials"] != 32 or routes != reference_routes
                        or any(item["candidate"] == row["candidate"] for item in aggregate["failures"])
                        or isinstance(mean, bool) or not isinstance(mean, (int, float))
                        or not math.isfinite(mean) or not 0 <= mean <= 1):
                    raise ValueError("Qualified profile completion or quality is inconsistent")
            elif mean is not None or row["mean_gain"] is not None:
                raise ValueError("Unqualified profiles cannot have a comparable native mean")
        for key in ("candidates", "routes", "failures", "primary_changes"):
            for row in aggregate[key]:
                if row["candidate"] not in names:
                    raise ValueError("A report row references an unknown profile")
                if key != "candidates" and (row["dataset"] not in DATASETS or row["family"] not in PRIMARY):
                    raise ValueError("A report row references an unknown dataset or family")
                result[key].append({**{field: row[field] for field in FIELDS[key]}, "generation": generation, "profile": row["candidate"],
                                    "candidate": f"g{generation}-" + row["candidate"]})
        result["generation_accounting"].append({"generation": generation,
                                               **{key: aggregate["model_accounting"][key] for key in ACCOUNTING_FIELDS}})
        result["sources"].append({"generation": generation, "generation_seal": aggregate["generation_seal"],
                                  "archive_sha256": aggregate["archive_sha256"],
                                  "native_report_sha256": aggregate["native_report_sha256"]})
    result.update({key: generations[0][key] for key in common})
    result["measured_runs"] = len(result["candidates"])
    result["unique_profiles"] = len({row["profile"] for row in result["candidates"]})
    result["completed_native_trials"] = sum(row["completed_trials"] for row in result["candidates"])
    result["native_errors"] = sum(row["errors"] for row in result["candidates"])
    result["best_default_by_dataset"] = best_by_dataset(result)
    result["best_all_routes_by_dataset"] = best_by_dataset(result, primary_only=False)
    return result


def render(output, aggregate):
    """Publish the same source rows through a combined, generation-labeled catalog."""
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "aggregates.json", aggregate)
    for key in ("candidates", "routes", "failures", "primary_changes"):
        write_csv(output / (key + ".csv"), aggregate[key])
    navigation = write_navigation_views(output, aggregate)
    lines = ["# Development comparison across both generations", "",
             "[Study overview](../README.md) · [Exact aggregate provenance](aggregates.json) · [CTA](cta.md)", "",
             "This view contains ten measured runs of nine distinct profiles across four datasets and eight skill families. Baseline was measured once in each generation; both measurements retain their identities. They are not independent samples and no pooled grand mean is created.", "",
             "This is a descriptive report, not a combined native Pareto archive. Finalist selection still uses only the final generation's native archive and the frozen rule. Neither a descriptive maximum nor an earlier generation's higher score replaces that decision. This publication precedes private validation and establishes no promotion.", "",
             "Scores use binary nDCG@10 on a 0-100 display scale. Every native profile mean weights its 32 default-route cells equally. Gains and change counts retain each generation's own baseline and unrounded native values.", "",
             "| Measured run | Qualified | Complete / expected | Errors | Native nDCG@10 | Gain, pp | Improved / unchanged / regressed |",
             "|---|---|---:|---:|---:|---:|---|"]
    for row in sorted(aggregate["candidates"], key=lambda item: (item["mean_ndcg_at_10"] is None, -(item["mean_ndcg_at_10"] or 0), item["candidate"])):
        counts = " / ".join(str(row[key]) if row[key] is not None else "unavailable" for key in ("improved_cells", "unchanged_cells", "regressed_cells"))
        link = f"[{row['candidate']}](by-profile/{row['candidate']}.md)"
        lines.append(f"| {link} | {row['qualified']} | {row['completed_trials']} / {row['expected_trials']} | {row['errors']} | {number(row['mean_ndcg_at_10'])} | {number(row['mean_gain'])} | {counts} |")
    for key, title in (("best_default_by_dataset", "Best measured default route on each dataset"), ("best_all_routes_by_dataset", "Best measured strategy across all 18 routes")):
        lines += ["", "## " + title, "", "Only qualified profiles enter these descriptive maxima. Every tie remains visible; a route maximum is not a validated routing policy.", "",
                  "| Dataset | Skill / route | Run(s) | nDCG@10 |", "|---|---|---|---:|"]
        for row in aggregate[key]:
            groups = {}
            for winner in row["winners"]:
                label = winner["family"] + (" / " + winner["route"] if "route" in winner else " / default")
                groups.setdefault(label, []).append(winner["profile"])
            if not groups:
                lines.append(f"| {row['dataset']} | No qualified profile | unavailable | unavailable |")
            for label, runs in groups.items():
                lines.append(f"| [{row['dataset']}](by-dataset/{row['dataset']}.md) | {label} | {', '.join(runs)} | {number(row['ndcg_at_10'])} |")
    lines += ["", "## Browse the complete measurements", ""]
    for directory, title in (("by-skill", "Skill families"), ("by-profile", "Measured runs"), ("by-dataset", "Datasets")):
        lines += [title + ": " + " · ".join(f"[{name}]({directory}/{name}.md)" for name in navigation[directory]) + ".", ""]
    lines += ["[Generation-zero comparison and chart](../generation-000/README.md) · [Generation-one comparison and chart](../generation-001/README.md)", "",
              "Failures and unavailable values remain in the linked generation reports and combined CSV/JSON. The report does not load questions, relevance labels, private validation or trajectories. These retrieval diagnostics are not official EnterpriseRAG/BEIR or generated-answer scores.", ""]
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")
    qualification = {row["candidate"]: row["qualified"] for row in aggregate["candidates"]}
    primary = [{**row, "profile_qualified": qualification[row["candidate"]]}
               for row in aggregate["routes"] if row["primary"]]
    write_csv(output / "cta.csv", primary)
    cta = ["# Cost, time and accuracy across both generations", "",
           "[Combined comparison](README.md) · [Exact primary-cell measurements](cta.csv)", "",
           "Every row retains its generation and profile. Query P95 values refer to one fixed route and cohort; they are not pooled across runs. Build time includes both deterministic builds and validators. Agent and trial durations cover the full evaluation, not one production query. Failed cells have no invented measurements and remain visible in the comparison and generation reports.", "",
           "Native token and provider accounting is preserved separately by generation in aggregates.json. It excludes assistant research, authoring, review and orchestration. Local CPU/model execution is unpriced; zero native provider charge does not mean the complete development effort was free. The same declared hardware limits apply, but the host was shared and timings are descriptive.", "",
           "| Dataset | Family | Measured run | Qualified | nDCG@10 | Query P95 ms | Double build s | Agent s, all routes | Native trial s | Knowledge MiB |",
           "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in sorted(primary, key=lambda item: (item["dataset"], item["family"], item["candidate"])):
        cta.append(f"| {row['dataset']} | {row['family']} | {row['candidate']} | {row['profile_qualified']} | {number(row['ndcg_at_10'])} | {row['p95_ms']:.2f} | {row['double_build_seconds']:.2f} | {number(row['agent_execution_seconds'], 1)} | {number(row['native_trial_seconds'], 1)} | {row['knowledge_bytes'] / 2**20:.2f} |")
    (output / "cta.md").write_text("\n".join(cta) + "\n", encoding="utf-8")


def main():
    state = assert_frozen()
    if (state["stages"]["evolve"]["status"] != "running"
            or state["validationRelease"] is not None or state["holdoutRelease"] is not None):
        raise ValueError("Freeze descriptive development comparisons before private release")
    report_root = REPO / "evaluations/reports/evolution" / WORK.name
    inputs = []
    for generation, word in enumerate(("zero", "one")):
        source = report_root / f"generation-{generation:03d}"
        evidence = state["evidence"].get(f"generation-{word}-public-report")
        if (not evidence or Path(evidence["source"]).resolve() != source.resolve()
                or evidence["kind"] != "final-report" or evidence["stageId"] != "evolve"
                or evidence["role"] != "report" or evidence["visibility"] != "public"):
            raise ValueError("Both generation reports must be registered before composition")
        aggregate = read(source / "aggregates.json")
        archive = WORK / f"pareto/development/generation-{generation:03d}/pareto-archive.json"
        native = WORK / f"native-reports/development-generation-{generation:03d}/final-report.json"
        if aggregate["archive_sha256"] != sha(archive) or aggregate["native_report_sha256"] != sha(native):
            raise ValueError("Generation report source commitments differ")
        inputs.append(aggregate)
    aggregate = project(inputs)
    for generation, source in enumerate(aggregate["sources"]):
        source["aggregate_sha256"] = sha(report_root / f"generation-{generation:03d}/aggregates.json")
    aggregate["reporter_sha256"] = sha(Path(__file__))
    render(report_root / "comparison", aggregate)
    print(json.dumps({"status": "published-cross-generation-development", "runs": aggregate["measured_runs"],
                      "unique_profiles": aggregate["unique_profiles"], "native_trials": aggregate["completed_native_trials"],
                      "native_errors": aggregate["native_errors"], "route_rows": len(aggregate["routes"])}))


if __name__ == "__main__":
    main()
