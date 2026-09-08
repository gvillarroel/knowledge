"""Project reviewed Enterprise evolution aggregates into catalog and profile views."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

from validate_comparison_contract import format_metric, validate_report_against_contract

FAMILIES = {"legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble", "graphify", "turso"}
QUALITY = {"ndcg_at_10": "nDCG@10", "recall_at_10": "Recall@10", "mrr_at_10": "MRR@10"}
ROUTES = {"legacy": {"lexical"}, "embeddings": {"lexical", "vector", "hybrid"},
          "classical": {"bm25", "topic", "association", "fusion"}, "adaptive": {"adaptive"},
          "entity-graph": {"lexical", "entity", "traversal", "fusion"},
          "ensemble": {"fast", "quality", "robust"}, "graphify": {"search"}, "turso": {"lexical-sql"}}
PRIMARY = {"legacy": "lexical", "embeddings": "hybrid", "classical": "fusion", "adaptive": "adaptive",
           "entity-graph": "fusion", "ensemble": "quality", "graphify": "search", "turso": "lexical-sql"}


def route_metrics(row: dict) -> dict:
    """Transcribe published quality ratios and one observed latency value."""
    metrics = {}
    for key in QUALITY:
        number = row[key]
        if type(number) not in (int, float) or not math.isfinite(number) or not 0 <= number <= 1:
            raise ValueError("Invalid published quality ratio")
        metrics[key] = 100 * number
    latency = row["query_p95_ms"]
    if type(latency) not in (int, float) or not math.isfinite(latency) or latency < 0:
        raise ValueError("Invalid published query latency")
    metrics["representative_p95_ms"] = latency
    return metrics


def project(value: dict, digest: str) -> tuple[dict, list[dict]]:
    """Transcribe only each already-selected primary route, without reselection."""
    if (value.get("schema_version") != "enterprise-sweep-report/1.0"
            or value.get("source") != "harbor" or value.get("answer_quality_evaluated") is not False):
        raise ValueError("Expected a reviewed native retrieval-only sweep report")
    summaries = value["families"]
    if len(summaries) != 8 or {row["family"] for row in summaries} != FAMILIES:
        raise ValueError("All eight distinct families must be published")
    alternatives, profiles = [], []
    for summary in summaries:
        family, winner = summary["family"], summary["winner"]
        routes = [row for row in value["routes"] if row["family"] == family
                  and row["candidate"] == winner and row["primary"] is True]
        attempts = [row for row in value["attempts"] if row["family"] == family and row["candidate"] == winner]
        if len(routes) != 1 or len(attempts) != 1 or attempts[0]["qualified"] is not True:
            raise ValueError("Selected candidate must have one qualified primary route")
        route = routes[0]
        if route["dataset"] != "enterprise-rag-40" or route["questions"] != 40:
            raise ValueError("Unexpected development cohort")
        if (route["ndcg_at_10"] != summary["winner_ndcg_at_10"]
                or route["ndcg_at_10"] != attempts[0]["ndcg_at_10"]
                or route["treatment"] != summary["treatment"]):
            raise ValueError("Published selected-route evidence disagrees")
        metrics = route_metrics(route)
        alternatives.append({"id": family+"-"+winner, "label": family+" / "+winner+" / "+route["route"], "metrics": metrics})
        profiles.append({"family": family, "candidate": winner, "treatment": summary["treatment"],
                         "skill_digest": attempts[0]["skill_digest"], "profile": summary["profile"]})
    alternatives.sort(key=lambda row: (-row["metrics"]["ndcg_at_10"], row["id"]))
    metrics = [{"id": key, "label": label, "unit": "percent", "aggregation": "mean",
                "direction": "higher", "display_precision": 2} for key, label in QUALITY.items()]
    metrics.append({"id": "representative_p95_ms", "label": "Query P95 (ms)", "unit": "ms",
                    "aggregation": "percentile_95", "direction": "lower", "display_precision": 2})
    contract = {"schema_version": "final-report-comparison/1.0", "report": "comparison.md",
                "heading": "## Direct comparison", "dataset_scope": {
                    "dataset_id": "enterprise-rag-e6-development-40", "cohort": "exposed-development-40",
                    "candidate_budget": "top-10; fixed 33-tactic development search; maximum 116 new candidates",
                    "identity_grouping": "authoritative document; 985-document corpus; one source/annotation group",
                    "metric_contract": "published-aggregate-sha256:"+digest},
                "metrics": metrics, "alternatives": alternatives}
    return contract, sorted(profiles, key=lambda row: row["family"])


def retained_routes(value: dict) -> list[dict]:
    """Retain all 18 diagnostic routes of the already-selected family profiles."""
    result = []
    for summary in value["families"]:
        family, winner = summary["family"], summary["winner"]
        rows = [row for row in value["routes"] if row["family"] == family and row["candidate"] == winner]
        if len(rows) != len(ROUTES[family]) or {row["route"] for row in rows} != ROUTES[family]:
            raise ValueError("Incomplete or duplicate retained-family routes")
        for row in rows:
            if (row["dataset"] != "enterprise-rag-40" or row["questions"] != 40
                    or row["treatment"] != summary["treatment"]
                    or type(row["primary"]) is not bool or row["primary"] != (row["route"] == PRIMARY[family])):
                raise ValueError("Diagnostic route differs from the primary/cohort contract")
            result.append({"family": family, "candidate": winner, "route": row["route"],
                           "primary": row["primary"], "metrics": route_metrics(row)})
    return sorted(result, key=lambda row: (row["family"], not row["primary"], row["route"]))


def publish(source: Path, output: Path) -> None:
    """Create append-only public views without reading native jobs or sealed cohorts."""
    raw = source.read_bytes()
    value = json.loads(raw)
    contract, profiles = project(value, hashlib.sha256(raw).hexdigest())
    routes = retained_routes(value)
    link = Path(os.path.relpath(source.parent / "README.md", output)).as_posix()
    lines = ["# EnterpriseRAG: selected development profiles", "", contract["heading"], "",
             "| Pos. | Pair / strategy | " + " | ".join(metric["label"] for metric in contract["metrics"]) + " |",
             "|---:|---|"+"---:|"*len(contract["metrics"])]
    for index, row in enumerate(contract["alternatives"], 1):
        lines.append(f"| {index} | {row['label']} | "+" | ".join(
            format_metric(row["metrics"][metric["id"]], metric) for metric in contract["metrics"])+" |")
    lines += ["", "[Source development comparison]("+link+") · [Exact family profiles](profiles.md) · [All retained-profile routes](routes.md)", "",
              "Each row transcribes the predeclared primary route of that family's already-selected incumbent. "
              "It does not select a different route using secondary metrics. Forty exposed queries on a "
              "reference-enriched 985-document corpus form one Enterprise source/annotation group.", "",
              "These development maxima do not establish unseen-query performance, official generated-answer "
              "quality or canonical skill promotion. Consult the campaign's terminal decision for independent validation. "
              "Shared-host query P95 is descriptive and is not combined across attempts.", "",
              "Source aggregate SHA-256: `"+contract["dataset_scope"]["metric_contract"].split(":", 1)[1]+"`."]
    report = "\n".join(lines)+"\n"
    validate_report_against_contract(report, contract)
    profile_lines = ["# Exact selected family profiles", "", "[Development comparison](comparison.md)", "",
                     "Each configuration below belongs to the named evaluated candidate digest. "
                     "Construction and consultation treatments retain their separate scopes. "
                     "These are reproducibility records; publication does not install a default skill."]
    helper = Path(os.path.relpath(Path(__file__).parent / "enterprise-evolution/profiles.py", output)).as_posix()
    profile_lines += ["", "These are profile overrides. The [frozen profile helper]("+helper+") applies them "
                      "to the unchanged construction plan or consultation defaults. Reproduction also requires "
                      "the campaign's frozen runtime and control plan. The complete bundle digest binds the "
                      "underlying builders and consultants."]
    for row in profiles:
        profile_lines += ["", "## "+row["family"], "", "Candidate: `"+row["candidate"]+"`. Treatment: **"+row["treatment"]+"**.",
                          "", "Complete evaluated bundle digest: `"+row["skill_digest"]+"`.", "", "```json",
                          json.dumps(row["profile"], indent=2, sort_keys=True, allow_nan=False), "```"]
    route_lines = ["# All routes of retained family profiles", "", "[Primary comparison](comparison.md)", "",
                   "These 18 diagnostic rows belong to the already-selected family incumbents. Secondary routes "
                   "did not choose another candidate or alter the frozen validation decision. The source "
                   "development report retains every attempted profile, including rejected candidates.", "",
                   "| Family | Candidate | Route | Selection route | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |",
                   "|---|---|---|---|---:|---:|---:|---:|"]
    for row in routes:
        route_lines.append(f"| {row['family']} | {row['candidate']} | {row['route']} | {'Yes' if row['primary'] else 'No'} | "
                           + " | ".join(format_metric(row["metrics"][metric["id"]], metric) for metric in contract["metrics"])+" |")
    route_lines += ["", "[Source development comparison]("+link+"). Source aggregate SHA-256: `"
                    +hashlib.sha256(raw).hexdigest()+"`."]
    output.mkdir(parents=True, exist_ok=False)
    (output / "comparison.json").write_text(json.dumps(contract, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    (output / "comparison.md").write_text(report, encoding="utf-8", newline="\n")
    (output / "profiles.md").write_text("\n".join(profile_lines)+"\n", encoding="utf-8", newline="\n")
    (output / "routes.md").write_text("\n".join(route_lines)+"\n", encoding="utf-8", newline="\n")


def publish_terminal(source: Path, decision_source: Path, selection_source: Path, output: Path) -> None:
    """Publish a closed native decision using only selected aggregate fields."""
    sources = {"development": source, "decision": decision_source, "selection": selection_source}
    raw = {key: path.read_bytes() for key, path in sources.items()}
    values = {key: json.loads(content) for key, content in raw.items()}
    value, decision, selection = (values[key] for key in sources)
    contract, profiles = project(value, hashlib.sha256(raw["development"]).hexdigest())
    retained_routes(value)
    selected = [row for row in profiles if row["family"] == selection["family"]
                and row["candidate"] == selection["candidate"]]
    if (len(selected) != 1 or selected[0]["skill_digest"] != selection["skill_digest"]
            or decision["selected_family"] != selection["family"]
            or decision.get("further_evolution_permitted") is not False
            or type(selection.get("unchanged")) is not bool):
        raise ValueError("Terminal selection differs from the completed development publication")
    changed = not selection["unchanged"]
    if decision.get("private_gate_opened") is not changed or type(decision.get("promoted")) is not bool:
        raise ValueError("Terminal gate release differs from the frozen selection")
    route = next(row for row in contract["alternatives"]
                 if row["id"] == selection["family"]+"-"+selection["candidate"])
    result = {"schema_version": "enterprise-terminal-publication/1.0",
              "decision": decision["decision"], "selected_family": selection["family"],
              "selected_candidate": selection["candidate"], "selected_skill_digest": selection["skill_digest"],
              "selected_development_ndcg_at_10": route["metrics"]["ndcg_at_10"] / 100,
              "private_gate_opened": changed, "promoted_for_declared_scope": decision["promoted"],
              "canonical_skill_installed": False, "further_evolution_permitted": False,
              "answer_quality_evaluated": False,
              "source_sha256": {key: hashlib.sha256(content).hexdigest() for key, content in raw.items()}}
    if not changed:
        if decision["decision"] != "baseline-retained" or decision["promoted"]:
            raise ValueError("An unchanged finalist cannot be promoted through an unopened gate")
        explanation = "The unchanged control remains the selected development profile. The private validation portfolio was not opened. No candidate was promoted."
    else:
        rules = {"minimumMeanGain": 0.0, "allowCaseRegressions": False, "requireNoErrors": True}
        if (decision.get("schema_version") != "enterprise-terminal-decision/1.0"
                or decision.get("selected_candidate") != selection["candidate"]
                or decision.get("selected_skill_digest") != selection["skill_digest"]
                or decision.get("source_groups") != 2 or decision.get("questions_per_group") != 12
                or decision.get("rules") != rules or decision.get("canonical_skill_installed") is not False
                or decision.get("native_status") not in {"complete", "non-evaluable"}
                or decision["decision"] != ("accepted-for-declared-scope" if decision["promoted"] else "keep-baseline")):
            raise ValueError("Unexpected terminal gate scope or decision")
        for key, low, high in (("baseline_mean", 0, 1), ("candidate_mean", 0, 1), ("mean_gain", -1, 1)):
            number = decision[key]
            if number is None and decision["native_status"] == "non-evaluable":
                continue
            if type(number) not in (int, float) or not math.isfinite(number) or not low <= number <= high:
                raise ValueError("Invalid terminal aggregate quality")
        expected_gain = (decision["candidate_mean"]-decision["baseline_mean"]
                         if decision["candidate_mean"] is not None and decision["baseline_mean"] is not None else None)
        gain_matches = (decision["mean_gain"] is None if expected_gain is None else
                        decision["mean_gain"] is not None and math.isclose(decision["mean_gain"], expected_gain, rel_tol=0, abs_tol=1e-12))
        if (any(type(decision[key]) is not bool for key in ("baseline_qualified", "candidate_qualified"))
                or type(decision["regressed_group_count"]) is not int or not 0 <= decision["regressed_group_count"] <= 2
                or not gain_matches):
            raise ValueError("Inconsistent terminal qualification or aggregate gain")
        if decision["promoted"] and (decision["native_status"] != "complete"
                                    or not decision["baseline_qualified"] or not decision["candidate_qualified"]
                                    or decision["regressed_group_count"] or decision["mean_gain"] < 0):
            raise ValueError("Accepted terminal decision contradicts its gate requirements")
        keys = ("native_status", "source_groups", "questions_per_group", "baseline_mean", "candidate_mean", "mean_gain",
                "baseline_qualified", "candidate_qualified", "regressed_group_count", "rules")
        result["validation"] = {key: decision[key] for key in keys}
        explanation = ("The exact frozen candidate passed the declared independent transfer gate. "
                       "Acceptance applies to that candidate and scope; the canonical skill was not installed."
                       if decision["promoted"] else
                       "The exact frozen candidate did not pass the declared independent transfer gate. "
                       "The baseline remains in place, and this study permits no further evolution.")
        if decision["native_status"] == "non-evaluable":
            explanation = "The independent transfer gate was not evaluable. No quality failure or zero score is inferred from unavailable evidence. The baseline remains in place, and this study permits no further evolution."
    link = Path(os.path.relpath(source.parent / "README.md", output)).as_posix()
    lines = ["# Terminal campaign decision", "", explanation, "",
             "Selected family: **"+result["selected_family"]+"**. Candidate: `"+result["selected_candidate"]+"`.", "",
             "Selected development nDCG@10: **"+f"{100*result['selected_development_ndcg_at_10']:.2f}"+"** on the exposed 40-query, 985-document Enterprise corpus.", "",
             "Complete selected bundle digest: `"+result["selected_skill_digest"]+"`."]
    if changed:
        gate = result["validation"]
        displayed = {key: "N/A" if gate[key] is None else f"{100*gate[key]:.2f}"
                     for key in ("baseline_mean", "candidate_mean", "mean_gain")}
        lines += ["", "| Independent transfer aggregate | Value |", "|---|---:|",
                  f"| Native status | {gate['native_status']} |",
                  f"| Source groups | {gate['source_groups']} |", f"| Questions per group | {gate['questions_per_group']} |",
                  f"| Baseline mean nDCG@10 | {displayed['baseline_mean']} |",
                  f"| Candidate mean nDCG@10 | {displayed['candidate_mean']} |",
                  f"| Mean gain, percentage points | {displayed['mean_gain']} |",
                  f"| Regressed groups | {gate['regressed_group_count']} |",
                  f"| Baseline qualified | {gate['baseline_qualified']} |",
                  f"| Candidate qualified | {gate['candidate_qualified']} |"]
    lines += ["", "The reserved portfolio covers FiQA and SciFact, with 12 queries and a reduced 985-document "
              "corpus per source group. It is a transfer gate on two source groups, "
              "not a test of previously unseen EnterpriseRAG questions. Private task text, identities, per-query "
              "scores and diagnostics are excluded from this publication. The native decision is transcribed; "
              "this report does not rerank candidates or rescore the gate.", "",
              "[Development evidence]("+link+") · [Machine-readable decision](decision.json)", "",
              "Source SHA-256 bindings:"]
    lines += ["", *["- "+key+": `"+digest+"`." for key, digest in result["source_sha256"].items()]]
    output.mkdir(parents=True, exist_ok=False)
    (output / "decision.json").write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    (output / "README.md").write_text("\n".join(lines)+"\n", encoding="utf-8", newline="\n")


def main() -> None:
    """Publish a catalog projection from an explicitly reviewed aggregate source."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--terminal-decision", type=Path)
    parser.add_argument("--selection", type=Path)
    args = parser.parse_args()
    if bool(args.terminal_decision) != bool(args.selection):
        parser.error("--terminal-decision and --selection must be supplied together")
    if args.terminal_decision:
        publish_terminal(args.source.resolve(), args.terminal_decision.resolve(), args.selection.resolve(), args.output.resolve())
    else:
        publish(args.source.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
