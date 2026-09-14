"""Draft source-linked aggregates after the frozen study lifecycle completes."""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import math

from .files import host, read, sha, write
from .planner import FAMILIES, ProtocolError


def public_case_groups(task: dict, diagnostics: dict, route: str) -> dict:
    """Aggregate existing public native case rewards; never rescore answers."""
    questions, cases = task["questions"], diagnostics["cases"][route]
    if len(questions) != len(cases):
        raise ProtocolError("Public diagnostic order/count differs from its task contract")
    grouped = {}
    for question, case in zip(questions, cases):
        category_key = "category:" + question["category"]
        grouped.setdefault(category_key, {"dimension": "category", "group": question["category"],
                                          "eligible_questions": 0, "weight": 0, "weighted_sum": 0})
        if not question["relevant"]:
            continue
        value, weight = case["ndcg_at_10"], question["weight"]
        if (type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1
                or type(weight) not in (float, int) or not math.isfinite(weight) or weight <= 0):
            raise ProtocolError("Public native case reward or declared weight is invalid")
        applications = {task["record_identities"][key]["source_id"] for key in question["relevant"] if key in task["record_identities"]}
        keys = [("all", "all"), ("category", question["category"]), *[("application", app) for app in sorted(applications)]]
        for dimension, label in keys:
            row = grouped.setdefault(dimension + ":" + label, {"dimension": dimension, "group": label,
                                      "eligible_questions": 0, "weight": 0, "weighted_sum": 0})
            row["eligible_questions"] += 1
            row["weight"] += weight
            row["weighted_sum"] += value * weight
    return {key: {"dimension": row["dimension"], "group": row["group"], "eligible_questions": row["eligible_questions"],
                  "ndcg_at_10": row["weighted_sum"] / row["weight"] if row["weight"] else None} for key, row in grouped.items()}


def _duration(value: dict) -> float | None:
    if not value.get("started_at") or not value.get("finished_at"):
        return None
    result = (datetime.fromisoformat(value["finished_at"]) - datetime.fromisoformat(value["started_at"])).total_seconds()
    if result < 0:
        raise ProtocolError("Native duration is negative")
    return result


def _views(native: dict, contract: dict) -> tuple[list[dict], list[dict]]:
    job = read(host(contract["jobs"]["recalculation"]))
    tasks = {host(row["path"]).name: host(row["path"]) for row in job["tasks"]}
    groups, costs = {}, []
    for record in native["records"]:
        arm = record["candidateId"]
        for trial in record["trials"]:
            family = contract["task_families"]["recalculation"][trial["taskName"]]
            task = read(tasks[trial["taskName"]] / "tests/contract.json")
            paths = [host(p) for p in trial["verifierFiles"] if host(p).name == "diagnostics.json"]
            if len(paths) != 1:
                raise ProtocolError("Missing unique native diagnostics for aggregate views")
            diagnostics, result = read(paths[0]), read(host(trial["resultPath"]))
            route = task["primary_route"]
            projected = public_case_groups(task, diagnostics, route)
            if abs(projected["all:all"]["ndcg_at_10"] - trial["reward"]) > 1e-12:
                raise ProtocolError("Public aggregation did not reproduce the native scalar")
            if arm == "frozen":
                for key, row in projected.items():
                    target = groups.setdefault(key, {k: v for k, v in row.items() if k != "ndcg_at_10"})
                    if target["eligible_questions"] != row["eligible_questions"]:
                        raise ProtocolError("Cross-family public group membership differs")
                    target.setdefault("families", {})[family] = row["ndcg_at_10"]
            usage = result.get("agent_result") or {}
            costs.append({"family": family, "arm": arm, "ndcg_at_10": trial["reward"],
                          "trial_seconds": _duration(result), "agent_seconds": _duration(result.get("agent_execution") or {}),
                          "two_build_seconds": diagnostics["build_seconds"], "knowledge_bytes": diagnostics["knowledge_bytes"],
                          "query_p95_ms": diagnostics["routes"][route]["p95_ms"],
                          "reported_provider_usd": usage.get("cost_usd"), "input_tokens": usage.get("n_input_tokens"),
                          "cached_input_tokens": usage.get("n_cache_tokens"), "output_tokens": usage.get("n_output_tokens"),
                          "native_result_sha256": sha(host(trial["resultPath"])), "native_diagnostics_sha256": sha(paths[0])})
    for row in groups.values():
        if set(row["families"]) != set(FAMILIES):
            raise ProtocolError("A public group is missing a family")
        values = [v for v in row["families"].values() if v is not None]
        best = max(values) if values else None
        row["leaders"] = [f for f in FAMILIES if best is not None and row["families"][f] is not None
                          and abs(row["families"][f] - best) <= 1e-12]
    return [groups[key] for key in sorted(groups)], costs


def _cell(value) -> str:
    return "Unavailable" if value is None else f"{value:.3f}"


def _label(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def publish(work: Path, plan: dict, selection: dict, outcome: dict) -> dict:
    """Preserve eight-family results without publishing task-level evidence."""
    comparison = work / "recalculation/comparison/comparison.json"
    native = read(comparison)
    contract = read(work / "runtime-contract.json")
    mapping = contract["task_families"]["recalculation"]
    arms = {}
    for record in native["records"]:
        arms[record["candidateId"]] = {mapping[row["taskName"]]: row["meanReward"] for row in record["cases"]}
    if set(arms) != {"baseline", "frozen"} or any(set(a) != set(FAMILIES) for a in arms.values()):
        raise ProtocolError("Publication lacks a complete native comparison")
    rows = [{"family": f, "development_reference": selection["families"][f]["reference_score"],
             "development_selected": selection["families"][f]["selected_score"],
             "all500_reference": arms["baseline"][f], "all500_frozen": arms["frozen"][f],
             "all500_delta": arms["frozen"][f] - arms["baseline"][f],
             "claims": selection["families"][f]["claims"], "stop_reason": selection["families"][f]["stop_reason"]} for f in FAMILIES]
    rows.sort(key=lambda r: (-r["all500_frozen"], r["family"]))
    groups, costs = _views(native, contract)
    aggregate = {"schema": "enterprise-isolated-aggregate/1.0", "study_id": plan["study_id"],
                 "status": "complete-awaiting-independent-publication-review", "rows": rows,
                 "development_questions": 120, "all500_questions": 500, "retrieval_eligible": 470,
                 "documents": 6000, "metric": "nDCG@10", "official_public_leaderboard_comparable": False,
                 "native_comparison_sha256": sha(comparison), "decision": outcome,
                 "canonical_skill_installed": False, "further_optimization_permitted": False}
    aggregate.update(public_groups=groups, cost_time_quality=costs)
    output = work / "aggregate-draft"
    write(output / "aggregate.json", aggregate)
    lines = ["# EnterpriseRAG: completed internal comparison", "",
             "Native Harbor retrieval comparison on 500 questions (470 retrieval-eligible) and 6,000 complete documents. "
             "Scores below are nDCG@10 multiplied by 100. This is not the full-corpus official answer-quality leaderboard.", "",
             "| Strategy | Development reference | Development selected | All-500 reference | All-500 frozen | Delta |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        lines.append(f"| {r['family']} | {100*r['development_reference']:.2f} | {100*r['development_selected']:.2f} | "
                     f"{100*r['all500_reference']:.2f} | {100*r['all500_frozen']:.2f} | {100*r['all500_delta']:+.2f} |")
    lines += ["", "The six closed catalogs retain their previous development selections. The two corrected implementations "
              "establish new reference measurements; they do not count as gains against failed runs.", "",
              "The optimizer exited before all-500 comparison and private acceptance. Neither can change this study's selection.",
              "", "Decision: `" + outcome["decision"] + "`. Canonical skill installation remains a separate reviewed action.",
              "", "[Applications and categories](groups.md) · [Cost, time and quality](cta.md) · [Dataset comparison](datasets.md)", ""]
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    group_lines = ["# EnterpriseRAG: applications and categories", "", "All-500 frozen-arm nDCG@10 multiplied by 100. "
                   "These are descriptive aggregates of native per-question rewards. Application groups overlap; "
                   "questions belong to the applications of their referenced documents available in the fixed corpus.", "",
                   "| Dimension | Group | Eligible questions | " + " | ".join(FAMILIES) + " | Highest value |",
                   "| --- | --- | ---: | " + " | ".join(["---:"]*8) + " | --- |"]
    for row in groups:
        group_lines.append("| " + " | ".join([row["dimension"], _label(row["group"]), str(row["eligible_questions"]),
                            *["Unavailable" if row['families'][f] is None else f"{row['families'][f]*100:.2f}" for f in FAMILIES],
                            ", ".join(row["leaders"]) or "Unavailable"]) + " |")
    (output / "groups.md").write_text("\n".join(group_lines)+"\n", encoding="utf-8", newline="\n")
    cta = ["# EnterpriseRAG: cost, time and quality", "", "Native trial and agent times are descriptive, "
           "not total campaign wall time. Two-build time includes the reproducibility pair. Provider cost "
           "excludes host, electricity and orchestration costs. Missing observations remain unavailable.", "",
           "| Strategy | Arm | nDCG@10 ×100 | Trial seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Provider USD |",
           "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in costs:
        cta.append("| " + " | ".join([row["family"], row["arm"], f"{100*row['ndcg_at_10']:.2f}",
                   *[_cell(row[k]) for k in ("trial_seconds", "agent_seconds", "two_build_seconds", "query_p95_ms")],
                   str(row["knowledge_bytes"]), _cell(row["reported_provider_usd"])]) + " |")
    (output / "cta.md").write_text("\n".join(cta)+"\n", encoding="utf-8", newline="\n")
    dataset_lines = ["# EnterpriseRAG: dataset comparison", "", "Both rows use 6,000 complete documents and eight skill strategies. "
                     "The development cohort and all-500 corpus overlap; they are not independent generalization estimates.", "",
                     "| Dataset role | Questions | Eligible | Highest retained strategy | nDCG@10 ×100 |",
                     "| --- | ---: | ---: | --- | ---: |"]
    for label, field, questions, eligible in (("Stratified development", "development_selected", 120, 112), ("All-500 frozen comparison", "all500_frozen", 500, 470)):
        best = max(row[field] for row in rows)
        leaders = ", ".join(row["family"] for row in rows if abs(row[field]-best) <= 1e-12)
        dataset_lines.append(f"| {label} | {questions} | {eligible} | {leaders} | {100*best:.2f} |")
    (output / "datasets.md").write_text("\n".join(dataset_lines)+"\n", encoding="utf-8", newline="\n")
    (output / "skills").mkdir()
    for row in rows:
        text = f"# EnterpriseRAG: {row['family']}\n\n" + "| Dataset | Reference | Retained/frozen |\n| --- | ---: | ---: |\n" \
               + f"| Stratified development | {100*row['development_reference']:.2f} | {100*row['development_selected']:.2f} |\n" \
               + f"| All-500 comparison | {100*row['all500_reference']:.2f} | {100*row['all500_frozen']:.2f} |\n\n" \
               + f"Scores are nDCG@10 multiplied by 100. Catalog stop: `{row['stop_reason']}`; cumulative claims: {row['claims']}.\n\n" \
               + "[All strategies](../README.md) · [Applications and categories](../groups.md) · [CTA](../cta.md)\n"
        (output / "skills" / (row["family"]+".md")).write_text(text, encoding="utf-8", newline="\n")
    return {"draft_aggregate_sha256": sha(output / "aggregate.json"), "independent_review_required": True}
