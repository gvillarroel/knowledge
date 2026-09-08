"""Publish aggregate development diagnostics from verified native Harbor reports."""
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime
from pathlib import Path

from bridge import PRIMARY
from prepare_experiment import REPO, WORK, sha, write_json


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def host_path(value):
    if os.name == "nt" and value.startswith("/mnt/c/"):
        return Path("C:/" + value[len("/mnt/c/"):])
    return Path(value)


def elapsed_seconds(phase):
    """Retain native phase timing without turning absent timestamps into zero."""
    if not phase or not phase.get("started_at") or not phase.get("finished_at"):
        return None
    elapsed = (datetime.fromisoformat(phase["finished_at"]) - datetime.fromisoformat(phase["started_at"])).total_seconds()
    if elapsed < 0:
        raise ValueError("Native phase timestamps are reversed")
    return elapsed


def collect(archive, native_report, metadata):
    """Project source aggregates only; never rescore questions or hide errors."""
    if archive["holdoutDataUsed"] is not False or native_report["source"] != "harbor":
        raise ValueError("Expected development-only native evidence")
    jobs = {str(host_path(job["jobDirectory"]).resolve()): job for job in native_report["jobs"]}
    summaries, routes, failures = [], [], []
    accounting = {"input_tokens": 0, "output_tokens": 0, "cache_tokens": 0, "model_provider_cost_usd": 0.0}
    for candidate in archive["candidateResults"]:
        directory = host_path(candidate["jobDirectory"]).resolve()
        if str(directory) not in jobs or not jobs[str(directory)]["complete"]:
            raise ValueError("Every candidate requires a complete native reporter projection")
        stats = read(directory / "result.json")["stats"]
        for target, key in (("input_tokens", "n_input_tokens"), ("output_tokens", "n_output_tokens"), ("cache_tokens", "n_cache_tokens"), ("model_provider_cost_usd", "cost_usd")):
            value = stats.get(key)
            if value is None:
                raise ValueError("Native model accounting is unavailable")
            accounting[target] += value
        summaries.append({"candidate": candidate["candidateId"], "qualified": candidate["qualification"]["passed"],
                          "expected_trials": candidate["summary"]["expectedTrials"], "completed_trials": candidate["summary"]["completedTrials"],
                          "errors": candidate["summary"]["errorCount"],
                          "scored_trials": candidate["summary"]["evaluableTrials"],
                          "mean_ndcg_at_10": candidate["summary"]["meanReward"] if candidate["qualification"]["passed"] else None,
                          "native_diagnostic_mean_reward": candidate["summary"]["meanReward"],
                          "skill_digest": candidate["skillDigest"], "source_skill_digest": candidate["sourceSkillDigest"],
                          "job_id": candidate["jobId"], "job_result_sha256": sha(directory / "result.json"),
                          "native_lock_sha256": sha(directory / "lock.json")})
        seen = set()
        for result_path in sorted(directory.glob("*/result.json")):
            result = read(result_path)
            identity = result["task_name"]
            if identity not in metadata or identity in seen:
                raise ValueError("Unexpected or duplicated native development task")
            seen.add(identity)
            item = metadata[identity]
            common = {"candidate": candidate["candidateId"], "dataset": item["source_cohort"], "family": item["family"]}
            diagnostic_path = result_path.parent / "verifier/diagnostics.json"
            diagnostic = read(diagnostic_path) if diagnostic_path.is_file() else {}
            if result.get("exception_info") or diagnostic.get("status") != "pass":
                failures.append({**common, "status": "non-evaluable" if result.get("exception_info") else "integrity-failed",
                                 "error_type": (result.get("exception_info") or {}).get("exception_type", diagnostic.get("error_type", "missing-diagnostics"))})
                continue
            for route, metrics in diagnostic["routes"].items():
                routes.append({**common, "route": route, "primary": route == PRIMARY[item["family"]],
                               "questions": diagnostic["question_count"],
                               **{key: metrics[key] for key in ("ndcg_at_10", "recall_at_10", "mrr_at_10", "full_qrel_coverage_at_10", "p95_ms")},
                               "double_build_seconds": diagnostic["build_seconds"], "knowledge_bytes": diagnostic["knowledge_bytes"],
                               "agent_execution_seconds": elapsed_seconds(result.get("agent_execution")), "native_trial_seconds": elapsed_seconds(result)})
        if seen != set(metadata):
            raise ValueError("Native development coverage differs from registered task membership")
    return {"candidates": summaries, "routes": routes, "failures": failures, "model_accounting": accounting}


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def number(value, scale=100):
    return "unavailable" if value is None else f"{value * scale:.2f}"


def best_by_dataset(aggregate, *, primary_only=True):
    """Describe local maxima among qualified profiles without selecting a policy."""
    qualified = {row["candidate"] for row in aggregate["candidates"] if row["qualified"]}
    eligible = [row for row in aggregate["routes"] if (row["primary"] or not primary_only) and row["candidate"] in qualified]
    output = []
    for dataset in sorted({row["dataset"] for row in [*aggregate["routes"], *aggregate.get("failures", [])]}):
        rows = [row for row in eligible if row["dataset"] == dataset]
        if not rows:
            output.append({"dataset": dataset, "winners": [], "ndcg_at_10": None})
            continue
        best = max(row["ndcg_at_10"] for row in rows)
        winners = sorted({(row["family"], row["candidate"], "" if primary_only else row["route"]) for row in rows if abs(row["ndcg_at_10"] - best) < 1e-12})
        output.append({"dataset": dataset, "winners": [{"family": family, "profile": candidate, **({} if primary_only else {"route": route})} for family, candidate, route in winners], "ndcg_at_10": best})
    return output


def primary_changes(aggregate):
    """Compare measured default routes without qualifying incomplete profiles."""
    qualification = {row["candidate"]: row["qualified"] for row in aggregate["candidates"]}
    lookup = {(row["candidate"], row["dataset"], row["family"]): row for row in aggregate["routes"] if row["primary"]}
    cells = sorted({(row["dataset"], row["family"]) for row in [*aggregate["routes"], *aggregate["failures"]]})
    output = []
    for candidate in qualification:
        for dataset, family in cells:
            baseline = lookup.get(("baseline", dataset, family))
            selected = lookup.get((candidate, dataset, family))
            baseline_value = baseline["ndcg_at_10"] if baseline else None
            selected_value = selected["ndcg_at_10"] if selected else None
            measured = selected_value - baseline_value if baseline and selected else None
            comparable = qualification.get("baseline", False) and qualification[candidate] and measured is not None
            output.append({"candidate": candidate, "dataset": dataset, "family": family,
                           "qualified_comparison": comparable, "baseline_ndcg_at_10": baseline_value,
                           "candidate_ndcg_at_10": selected_value, "delta_ndcg_at_10": measured if comparable else None,
                           "diagnostic_measured_delta": measured})
    return output


def change_counts(candidate, changes):
    rows = [row for row in changes if row["candidate"] == candidate]
    if not rows or any(not row["qualified_comparison"] for row in rows):
        return {"improved_cells": None, "unchanged_cells": None, "regressed_cells": None}
    return {"improved_cells": sum(row["delta_ndcg_at_10"] > 0 for row in rows),
            "unchanged_cells": sum(row["delta_ndcg_at_10"] == 0 for row in rows),
            "regressed_cells": sum(row["delta_ndcg_at_10"] < 0 for row in rows)}


def write_navigation_views(output, aggregate):
    """Make the same measured rows discoverable by skill, profile, and dataset."""
    summaries = {row["candidate"]: row for row in aggregate["candidates"]}
    links = {}
    for dimension, directory, title in (("family", "by-skill", "Skill family"), ("candidate", "by-profile", "Construction profile"), ("dataset", "by-dataset", "Dataset")):
        keys = sorted({row[dimension] for row in [*aggregate["routes"], *aggregate["failures"]]})
        links[directory] = keys
        target = output / directory
        target.mkdir()
        for key in keys:
            rows = [row for row in aggregate["routes"] if row[dimension] == key]
            failures = [row for row in aggregate["failures"] if row[dimension] == key]
            lines = [f"# {title}: {key}", "", "[General development comparison](../README.md) · [Cost, time and accuracy](../cta.md)", "",
                     "Development retrieval diagnostics; values are not independent validation or official benchmark scores. Primary routes use the predeclared family default. Qualification applies to the whole profile, including every failed cell.", "",
                     "| Dataset | Skill family | Profile | Qualified | Route | Primary | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |", "|---|---|---|---|---|---|---:|---:|---:|---:|"]
            for row in sorted(rows, key=lambda row: (row["dataset"], row["family"], row["candidate"], not row["primary"], row["route"])):
                lines.append(f"| {row['dataset']} | {row['family']} | {row['candidate']} | {summaries[row['candidate']]['qualified']} | {row['route']} | {row['primary']} | {number(row['ndcg_at_10'])} | {number(row['recall_at_10'])} | {number(row['mrr_at_10'])} | {row['p95_ms']:.2f} |")
            if failures:
                lines += ["", "## Failed cells", "", "| Dataset | Skill family | Profile | Status | Error |", "|---|---|---|---|---|"]
                lines.extend(f"| {row['dataset']} | {row['family']} | {row['candidate']} | {row['status']} | {row['error_type']} |" for row in failures)
            (target / (key + ".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return links


def render_comparison(output, aggregate):
    """Render measured primary-route cells with an explicit shared score scale."""
    os.environ["MPLCONFIGDIR"] = str(REPO / "tmp/retrieval-report-matplotlib")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    profiles = [row["candidate"] for row in aggregate["candidates"]]
    qualification = {row["candidate"]: row["qualified"] for row in aggregate["candidates"]}
    families = list(PRIMARY)
    datasets = sorted({row["dataset"] for row in [*aggregate["routes"], *aggregate["failures"]]})
    lookup = {(row["dataset"], row["family"], row["candidate"]): row["ndcg_at_10"] * 100 for row in aggregate["routes"] if row["primary"]}
    labels = {"baseline": "Baseline", "neural-record": "MiniLM", "quarter-expansion": "Expansion\n× 0.25", "bm25-low-b": "BM25\nb = 0.25", "stronger-titles": "Title\nweight 4"}
    names = {"enterprise": "EnterpriseRAG · 40 queries", "astro": "Astro · 40 queries", "architecture": "Architecture books · 40 queries", "data-science": "Data science books · 40 queries"}
    figure, axes = plt.subplots(2, 2, figsize=(13, 11), layout="constrained")
    color = plt.get_cmap("YlGnBu").copy()
    color.set_bad("#e5e7eb")
    for axis, dataset in zip(axes.flat, datasets):
        values = np.array([[lookup.get((dataset, family, profile), np.nan) for profile in profiles] for family in families])
        plot = axis.imshow(values, vmin=0, vmax=100, cmap=color, aspect="auto")
        axis.set_title(names.get(dataset, dataset), loc="left", fontsize=13, fontweight="bold", pad=12)
        axis.set_yticks(range(len(families)), [family.replace("-", " ").title() for family in families])
        axis.set_xticks(range(len(profiles)), [labels.get(profile, profile.replace("-", "\n")) + ("*" if not qualification[profile] else "") for profile in profiles], fontsize=9)
        axis.tick_params(length=0, pad=8)
        for row in range(len(families)):
            for column in range(len(profiles)):
                value = values[row, column]
                axis.text(column, row, "—" if np.isnan(value) else f"{value:.1f}", ha="center", va="center", fontsize=10, color="white" if value >= 65 else "#111827")
        for spine in axis.spines.values():
            spine.set_visible(False)
    for axis in list(axes.flat)[len(datasets):]:
        axis.set_visible(False)
    figure.colorbar(plot, ax=axes, location="bottom", fraction=.025, pad=.035, label="Binary nDCG@10 · 0–100 · higher is better")
    figure.suptitle("Development retrieval by skill and construction profile", fontsize=18, fontweight="bold")
    figure.supxlabel("Predeclared default routes · * unqualified profile · — non-evaluable cell\nDevelopment evidence; not independent validation or official EnterpriseRAG scores.", fontsize=10)
    figure.savefig(output / "comparison.svg", metadata={"Date": None})
    figure.savefig(output / "comparison.png", dpi=140)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", type=int, choices=(0, 1), required=True)
    parser.add_argument("--native-report", type=Path, required=True)
    parser.add_argument("--plot", action="store_true", help="Render standalone SVG/PNG comparisons using Matplotlib")
    args = parser.parse_args()
    source = WORK / f"pareto/development/generation-{args.generation:03d}/pareto-archive.json"
    archive = read(source)
    metadata = {}
    for path in sorted((WORK / "curator/development").glob("*-tasks.json")):
        for row in read(path):
            metadata[row["task_id"]] = row
    aggregate = collect(archive, read(args.native_report), metadata)
    aggregate["primary_changes"] = primary_changes(aggregate)
    baseline_mean = next(row["mean_ndcg_at_10"] for row in aggregate["candidates"] if row["candidate"] == "baseline")
    for candidate in aggregate["candidates"]:
        value = candidate["mean_ndcg_at_10"]
        candidate.update(mean_gain=value - baseline_mean if value is not None and baseline_mean is not None else None,
                         **change_counts(candidate["candidate"], aggregate["primary_changes"]))
    output = REPO / "evaluations/reports/evolution" / WORK.name / f"generation-{args.generation:03d}"
    output.mkdir(parents=True, exist_ok=False)
    aggregate.update(schema_version="retrieval-evolution-aggregates/1.0", study=WORK.name, generation=args.generation,
                     source="native Harbor verifier aggregates and owning Pareto archive", phase="development",
                     archive_sha256=sha(source), native_report_sha256=sha(args.native_report),
                     generation_seal=archive["generationSeal"], development_profile_digest=archive["developmentProfileDigest"],
                     archive_members=[row["candidateId"] for row in archive["archive"]], validation_used=False,
                     execution_kind="deterministic skill runtime with no instruction-model invocation",
                     scope="Deterministic construction and retrieval; not official EnterpriseRAG/BEIR or answer-quality scores")
    hardware = WORK / "hardware.json"
    aggregate.update(hardware=read(hardware) if hardware.is_file() else None,
                     hardware_sha256=sha(hardware) if hardware.is_file() else None)
    write_json(output / "aggregates.json", aggregate)
    for key in ("candidates", "routes", "failures", "primary_changes"):
        write_csv(output / (key + ".csv"), aggregate[key])
    navigation = write_navigation_views(output, aggregate)
    if args.plot:
        render_comparison(output, aggregate)
    primary = [row for row in aggregate["routes"] if row["primary"]]
    write_csv(output / "cta.csv", primary)
    lines = [f"# Construction-profile development, generation {args.generation}", "", "[Evolution studies](../../README.md)", "",
             "Scores are binary nDCG@10 on a 0–100 display scale. The primary score weights each of the 32 dataset × family cells equally. All retrieval routes and resource measurements are available in [routes.csv](routes.csv); exact native provenance is in [aggregates.json](aggregates.json).", "",
             "These are development diagnostics. Archive membership does not establish validation or promotion. Every registered task remains in the completion/error counts. An unqualified profile has no comparable primary score; any partial native diagnostic mean is retained separately in the machine-readable evidence.", "",
             "| Profile | Qualified | Completed / expected cells | Errors | Primary nDCG@10 | Gain, pp | Improved / unchanged / regressed cells |", "|---|---|---:|---:|---:|---:|---|"]
    for row in sorted(aggregate["candidates"], key=lambda row: (row["mean_ndcg_at_10"] is None, -(row["mean_ndcg_at_10"] or 0), row["candidate"])):
        counts = " / ".join(str(row[key]) if row[key] is not None else "unavailable" for key in ("improved_cells", "unchanged_cells", "regressed_cells"))
        lines.append(f"| {row['candidate']} | {row['qualified']} | {row['completed_trials']} / {row['expected_trials']} | {row['errors']} | {number(row['mean_ndcg_at_10'])} | {number(row['mean_gain'])} | {counts} |")
    lines += ["", "Gain is the candidate-minus-baseline difference in percentage points. Cell counts use unrounded default-route values and do not imply independent samples. [Every default-route change by dataset and skill](changes.md) is retained, including unavailable comparisons."]
    if args.plot:
        lines += ["", "![Measured development retrieval by dataset, skill and profile](comparison.svg)", "", "[Download PNG](comparison.png) · [Download SVG](comparison.svg)"]
    lines += ["", "## Reports by skill, profile and dataset", ""]
    for directory, label in (("by-skill", "Skill families"), ("by-profile", "Profiles"), ("by-dataset", "Datasets")):
        lines.append(label + ": " + " · ".join(f"[{key}]({directory}/{key}.md)" for key in navigation[directory]) + ".")
        lines.append("")
    lines += ["## Which skill is strongest on each dataset?", "", "Best measured default routes among qualified profiles. This is an exploratory view of development evidence, not a routed policy or a replacement for the frozen selection rule.", "", "| Dataset | Skill family / profile | nDCG@10 |", "|---|---|---:|"]
    for row in best_by_dataset(aggregate):
        winners = ", ".join(item["family"] + " / " + item["profile"] for item in row["winners"]) or "No qualified profile"
        lines.append(f"| {row['dataset']} | {winners} | {number(row['ndcg_at_10'])} |")
    lines += ["", "## Best measured strategy across all 18 routes", "", "These maxima include secondary routes from qualified profiles. They describe which measured strategy retrieves best on each development dataset; they do not change the frozen default-route selection rule or establish a validated routing policy.", "", "| Dataset | Skill family / route / profile | nDCG@10 |", "|---|---|---:|"]
    for row in best_by_dataset(aggregate, primary_only=False):
        winners = ", ".join(item["family"] + " / " + item["route"] + " / " + item["profile"] for item in row["winners"]) or "No qualified profile"
        lines.append(f"| {row['dataset']} | {winners} | {number(row['ndcg_at_10'])} |")
    lines += ["", "## Best observed default route by dataset and family", "", "These local maxima may come from different profiles, including unqualified profiles with failures elsewhere. They are diagnostics, not promotion or a new selection rule; see each profile's qualification above.", "", "| Dataset | Family | Profile(s) | nDCG@10 |", "|---|---|---|---:|"]
    for dataset, family in sorted({(row["dataset"], row["family"]) for row in primary}):
        rows = [row for row in primary if row["dataset"] == dataset and row["family"] == family]
        best = max(row["ndcg_at_10"] for row in rows)
        winners = ", ".join(row["candidate"] for row in rows if abs(row["ndcg_at_10"] - best) < 1e-12)
        lines.append(f"| {dataset} | {family} | {winners} | {number(best)} |")
    lines += ["", "## Cost, time and accuracy", "", "[CTA table](cta.md) · [CTA data by dataset, family and profile](cta.csv).", "", "The experiment makes no instruction-model calls and incurs no model-provider charge. Local CPU/model execution still has a real resource cost. `double_build_seconds` includes two independent validated builds; storage counts one knowledge artifact. Query P95 covers the complete fixed cohort on each route. Timings are descriptive under two concurrent CPU-limited trials, not production latency guarantees.", "",
              "Historical datasets are exposed development evidence. The independent validation portfolio remains outside this report. Do not compare these retrieval scores directly with the public EnterpriseRAG answer-quality leaderboard.", ""]
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")
    changes = ["# Default-route changes against the frozen baseline", "", "[Development comparison](README.md) · [Change data](primary_changes.csv)", "",
               "Scores and differences use a 0–100 display scale; gains are percentage points. Both complete profiles must qualify for a comparable delta. Individual measurements and explicitly labeled diagnostic differences remain in the CSV when a profile fails elsewhere. Every registered dataset-by-family cell stays visible. These are development diagnostics, not validation or a new selection policy.", "",
               "| Dataset | Family | Profile | Qualified comparison | Baseline nDCG@10 | Profile nDCG@10 | Gain, pp |", "|---|---|---|---|---:|---:|---:|"]
    for row in sorted(aggregate["primary_changes"], key=lambda row: (row["dataset"], row["family"], row["candidate"])):
        if row["candidate"] != "baseline":
            changes.append(f"| {row['dataset']} | {row['family']} | {row['candidate']} | {row['qualified_comparison']} | {number(row['baseline_ndcg_at_10'])} | {number(row['candidate_ndcg_at_10'])} | {number(row['delta_ndcg_at_10'])} |")
    (output / "changes.md").write_text("\n".join(changes) + "\n", encoding="utf-8")
    cta = ["# Cost, time and accuracy by dataset and skill family", "", "[Development report](README.md) · [Machine-readable table](cta.csv)", "",
           "One row per completed primary-route cell. The native accounting reports zero instruction-model tokens and provider charge; local execution cost is not priced. Construction includes both deterministic builds and validators. Agent time additionally captures snapshot loading, initialization and every declared route; trial wall time also includes native setup and verification. Those totals describe the full evaluation, not one production query. Failed cells remain in the main report and have no invented timing or quality value.", "",
           "| Dataset | Family | Profile | nDCG@10 | Query P95 ms | Double build s | Agent s, all routes | Native trial s | Knowledge MiB |", "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in sorted(primary, key=lambda row: (row["dataset"], row["family"], row["candidate"])):
        cta.append(f"| {row['dataset']} | {row['family']} | {row['candidate']} | {number(row['ndcg_at_10'])} | {row['p95_ms']:.2f} | {row['double_build_seconds']:.2f} | {number(row['agent_execution_seconds'], 1)} | {number(row['native_trial_seconds'], 1)} | {row['knowledge_bytes'] / 2**20:.2f} |")
    if aggregate["hardware"]:
        host = aggregate["hardware"]
        cta += ["", f"Host snapshot: {host['cpu'].get('Model name', 'unavailable')}; Docker exposes {host['docker']['NCPU']} CPUs and {host['docker']['MemTotal'] / 2**30:.2f} GiB RAM. Each trial is limited to two CPUs and two numerical threads. The host was not reserved for exclusive use. Full non-identifying hardware and native model-accounting values are bound in [aggregates.json](aggregates.json)."]
    (output / "cta.md").write_text("\n".join(cta) + "\n", encoding="utf-8")
    print(json.dumps({"status": "published-development-aggregates", "generation": args.generation,
                      "candidates": len(aggregate["candidates"]), "route_rows": len(aggregate["routes"]), "failed_cells": len(aggregate["failures"])}))


if __name__ == "__main__":
    main()
