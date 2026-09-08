"""Publish source-bound aggregate reports; never rescore task questions."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from prepare import WORK, REPO, HPY, read, write, sha
from profiles import FAMILIES, baseline_profile, mutate
from sweep import Sweep

PRIMARY = {"legacy": "lexical", "embeddings": "hybrid", "classical": "fusion", "adaptive": "adaptive", "entity-graph": "fusion", "ensemble": "quality", "graphify": "search", "turso": "lexical-sql"}


def host(value):
    return Path("C:/"+value[len("/mnt/c/"):]) if os.name == "nt" and value.startswith("/mnt/c/") else Path(value)


def number(value, scale=100):
    return "N/A" if value is None else f"{value*scale:.2f}"


def quality(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Invalid aggregate quality")
    return value


def seconds(value):
    if not value or not value.get("started_at") or not value.get("finished_at"):
        return None
    result = (datetime.fromisoformat(value["finished_at"])-datetime.fromisoformat(value["started_at"])).total_seconds()
    if result < 0:
        raise ValueError("Reversed native timing")
    return result


def normalize():
    if os.name == "nt":
        raise ValueError("Normalize through the native Linux Harbor runtime")
    reporter = "/mnt/c/Users/villa/.codex/skills/harbor-run-results/scripts/report_harbor_jobs.py"
    for family in FAMILIES:
        result = read(WORK / "family-results" / (family+".json"))
        jobs = [row["job"] for row in result["outcomes"]]
        output = WORK / "native-reports" / family
        log = WORK / "logs" / ("report-"+family+".log")
        with log.open("xb") as stream:
            subprocess.run([sys.executable, "-B", reporter, *jobs, "--compare", "--output-dir", str(output)], stdout=stream, stderr=subprocess.STDOUT, check=True)
        print(json.dumps({"event": "native-report", "family": family, "jobs": len(jobs)}), flush=True)


def audit_family(result, strategies):
    """Replay stopping decisions; a status label alone cannot prove exhaustion."""
    family = result["family"]
    state = Sweep(strategies, "baseline", result["baseline_score"], baseline_profile())
    outcomes = iter(result["outcomes"][1:])
    count = 0
    while proposed := state.next():
        strategy, variant = proposed
        profile = mutate(state.profile, family, variant)
        if not state.claim(profile):
            continue
        outcome = next(outcomes, None)
        if outcome is None or outcome["strategy"] != strategy["id"] or outcome["variant"] != variant:
            raise ValueError("Missing or reordered scheduled attempt")
        improved = state.observe(outcome["candidate"], profile, outcome["score"], qualified=outcome["qualified"])
        if (improved != outcome["improved"] or state.failures != outcome["consecutive_failures"]
                or state.best_id != outcome["best_candidate"] or state.best_score != outcome["best_score"]):
            raise ValueError("Recorded incumbent or miss streak differs from replay")
        count += 1
    if next(outcomes, None) is not None or count != result["generation"]:
        raise ValueError("Attempt budget differs from the exhausted schedule")
    if result["events"] != state.events or result["profile"] != state.profile or result["winner"]["id"] != state.best_id:
        raise ValueError("Terminal ledger or winner differs from replay")


def collect():
    routes, attempts, families, stops = [], [], [], []
    protocol = read(WORK / "protocol.json")
    for family in FAMILIES:
        result = read(WORK / "family-results" / (family+".json"))
        if result["status"] != "catalog-exhausted":
            raise ValueError("Cannot publish unfinished family as exhausted")
        audit_family(result, protocol["strategies"][family])
        native = read(WORK / "native-reports" / family / "final-report.json")
        native_jobs = {str(host(row["jobDirectory"]).resolve()): row for row in native["jobs"]}
        families.append({"family": family, "treatment": result["treatment"], "baseline_ndcg_at_10": quality(result["baseline_score"]), "winner_ndcg_at_10": quality(result["score"]), "delta_ndcg_at_10": result["score"]-result["baseline_score"], "winner": result["winner"]["id"], "attempts": result["generation"], "profile": result["profile"][family]})
        stops.extend({"family": family, **event} for event in result["events"] if event["event"] in {"strategy-finished", "duplicate-skipped"})
        for outcome in result["outcomes"]:
            directory = host(outcome["job"])
            normalized = native_jobs[str(directory.resolve())]
            if not normalized["complete"]:
                raise ValueError("Incomplete native job cannot supply a complete report")
            archive = read(host(outcome["archive"]))
            candidate = next(c for c in archive["candidateResults"] if c["candidateId"] == outcome["candidate"])
            if not candidate["promotionEligibleProvenance"] or not archive["promotionEligibleProfile"]:
                raise ValueError("Unverified native provenance")
            valid = candidate["evaluable"] and candidate["qualification"]["passed"]
            primary = candidate["summary"]["meanReward"] if valid else None
            if valid and not math.isclose(quality(primary), quality(outcome["score"]), rel_tol=0, abs_tol=1e-12):
                raise ValueError("Scheduler score differs from native owner")
            attempts.append({"family": family, "treatment": result["treatment"], "candidate": outcome["candidate"], "strategy": outcome["strategy"], "qualified": valid, "ndcg_at_10": primary, "improved_incumbent": outcome.get("improved", False), "consecutive_failures": outcome.get("consecutive_failures", 0), "variant": outcome.get("variant", {}), "skill_digest": candidate["skillDigest"], "job_id": candidate["jobId"], "job_result_sha256": sha(directory / "result.json"), "native_lock_sha256": sha(directory / "lock.json")})
            trials = list(directory.glob("*/result.json"))
            if len(trials) != 1:
                raise ValueError("Expected one exact family trial")
            trial = read(trials[0])
            if not valid:
                continue
            diagnostic = read(trials[0].parent / "verifier/diagnostics.json")
            if diagnostic["status"] != "pass" or diagnostic["question_count"] != 40:
                raise ValueError("Invalid native diagnostic cohort")
            rewards = trial["verifier_result"]["rewards"]
            if rewards["evidence_integrity"] != 1 or not math.isclose(rewards["reward"], primary, rel_tol=0, abs_tol=1e-12):
                raise ValueError("Native verifier and archive disagree")
            for route, metrics in diagnostic["routes"].items():
                row = {"dataset": "enterprise-rag-40", "family": family, "treatment": result["treatment"], "candidate": outcome["candidate"], "strategy": outcome["strategy"], "route": route, "primary": route == PRIMARY[family], "questions": 40, **{key: quality(metrics[key]) for key in ("ndcg_at_10", "recall_at_10", "mrr_at_10", "full_qrel_coverage_at_10")}, "query_p95_ms": metrics["p95_ms"], "double_build_seconds": diagnostic["build_seconds"], "knowledge_bytes": diagnostic["knowledge_bytes"], "agent_seconds": seconds(trial.get("agent_execution")), "native_trial_seconds": seconds(trial)}
                for key in ("query_p95_ms", "double_build_seconds", "knowledge_bytes", "agent_seconds", "native_trial_seconds"):
                    value = row[key]
                    if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                        raise ValueError("Invalid native resource metric")
                if row["primary"] and not math.isclose(row["ndcg_at_10"], primary, rel_tol=0, abs_tol=1e-12):
                    raise ValueError("Primary route and owner reward differ")
                routes.append(row)
    return {"schema_version": "enterprise-sweep-report/1.0", "source": "harbor", "answer_quality_evaluated": False, "families": families, "attempts": attempts, "routes": routes, "stops": stops, "protocol_sha256": sha(WORK / "protocol.json"), "execution_contract_sha256": sha(WORK / "execution-contract.json")}


def csv_file(path, rows):
    if not rows:
        return
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in rows)


def markdown(path, lines):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines)+"\n")


def publish(output):
    value = collect()
    output.mkdir(parents=True, exist_ok=False)
    write(output / "aggregates.json", value)
    for key in ("attempts", "routes", "families", "stops"):
        if key != "stops":
            csv_file(output / (key+".csv"), value[key])
    rows = sorted(value["families"], key=lambda r: (-r["winner_ndcg_at_10"], r["family"]))
    lines = ["# EnterpriseRAG evolution sweep", "", "Native development ranking on 40 previously exposed queries and a reduced, reference-enriched 985-document corpus. All eight families completed their declared finite tactic catalogs or per-tactic three-miss plateaus. These are retrieval scores; official full-corpus answer quality is a different metric.", "", "[All attempts](attempts.csv) · [All routes](routes.csv) · [Cost, time and quality](CTA.md) · [Strategy stopping ledger](strategies.md)", "", "| Family | Treatment | Baseline nDCG@10 | Best nDCG@10 | Gain pp | New candidates |", "|---|---|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| [{row['family']}](by-skill/{row['family']}.md) | {row['treatment']} | {number(row['baseline_ndcg_at_10'])} | {number(row['winner_ndcg_at_10'])} | {number(row['delta_ndcg_at_10'])} | {row['attempts']} |")
    lines += ["", "Every control contains that family's best completely measured historical Enterprise configuration, including pinned MiniLM where useful. Every number above is a fresh native measurement, with historical parity checked before any child. One aggregate Harbor case per family contains all 40 queries; this is one Enterprise source/annotation group, not 40 independent transfer cases.", "", "The exact selected family and private gate outcome are reported separately in the campaign decision. Development maxima alone do not promote a canonical default.", "", "![Baseline and best development scores](comparison.png)"]
    markdown(output / "README.md", lines)
    (output / "by-skill").mkdir()
    for family in FAMILIES:
        lines = ["# "+family+" evolution", "", "[General comparison](../README.md)", "", "| Candidate | Strategy | Qualified | nDCG@10 | Improved incumbent | Consecutive misses |", "|---|---|---|---:|---|---:|"]
        for row in value["attempts"]:
            if row["family"] == family:
                lines.append(f"| {row['candidate']} | {row['strategy']} | {row['qualified']} | {number(row['ndcg_at_10'])} | {row['improved_incumbent']} | {row['consecutive_failures']} |")
        markdown(output / "by-skill" / (family+".md"), lines)
    lines = ["# Strategy stopping ledger", "", "[General comparison](README.md)", "", "Three consecutive misses stop a tactic. A gain resets the counter. A shorter finite catalog can end before three misses. Duplicate profiles do not count as attempts. This is exhaustion of the declared catalog, not every possible future research strategy.", "", "| Family | Strategy | Stop reason | Final miss streak | Unused variants |", "|---|---|---|---:|---:|"]
    for row in value["stops"]:
        if row["event"] == "strategy-finished":
            lines.append(f"| {row['family']} | {row['strategy']} | {row['reason']} | {row['failures']} | {row['unused_variants']} |")
    lines += ["", "Skipped duplicate profiles: "+str(sum(r["event"] == "duplicate-skipped" for r in value["stops"]))+"."]
    markdown(output / "strategies.md", lines)
    lines = ["# Cost, time and quality", "", "[General comparison](README.md)", "", "Every row is one primary route in a complete native trial. Two builds and matched validators are included in construction time. Query P95 values are not pooled. Trials use zero instruction-model calls; local CPU/model execution and assistant authoring are not priced. Shared-host timings are descriptive.", "", "| Family | Candidate | nDCG@10 | Query P95 ms | Double build s | Agent s | Native trial s | Knowledge MiB |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in value["routes"]:
        if row["primary"]:
            lines.append(f"| {row['family']} | {row['candidate']} | {number(row['ndcg_at_10'])} | {number(row['query_p95_ms'], 1)} | {number(row['double_build_seconds'], 1)} | {number(row['agent_seconds'], 1)} | {number(row['native_trial_seconds'], 1)} | {number(row['knowledge_bytes'], 1/1048576)} |")
    markdown(output / "CTA.md", lines)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 6.5), layout="constrained")
    positions = list(range(len(rows)))
    ax.barh([y+.19 for y in positions], [100*r["baseline_ndcg_at_10"] for r in rows], height=.36, label="Frozen control", color="#9eacbe")
    bars = ax.barh([y-.19 for y in positions], [100*r["winner_ndcg_at_10"] for r in rows], height=.36, label="Best development candidate", color="#16697a")
    ax.bar_label(bars, fmt="%.2f", padding=4, fontsize=10)
    ax.set_yticks(positions, [r["family"]+" ("+r["treatment"]+")" for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("nDCG@10 × 100")
    ax.set_title("EnterpriseRAG: observed evolution by knowledge family\n40 development queries · 985 documents · no answer-quality claim")
    ax.legend(loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(output / "comparison.png", dpi=170)
    fig.savefig(output / "comparison.svg")
    plt.close(fig)
    print(json.dumps({"report": str(output), "attempts_including_controls": len(value["attempts"]), "route_rows": len(value["routes"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["normalize", "publish"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode == "normalize":
        normalize()
    else:
        if args.output is None:
            parser.error("--output is required")
        publish(args.output.resolve())
