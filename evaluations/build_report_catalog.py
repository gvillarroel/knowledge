#!/usr/bin/env python3
"""Render dataset, skill, and cost/time/quality views from reviewed aggregates only."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "evaluations/reports"
METRICS = {"ndcg_at_10": "nDCG@10", "recall_at_10": "Recall@10", "mrr_at_10": "MRR@10",
           "full_evidence_at_10": "Full evidence@10", "p95_ms": "P95 (ms)"}
FAMILY_NAMES = {"entity graph": "entity-graph", "rustmallet": "rust-mallet",
                "tika/mallet/tantivy": "tika-mallet-tantivy", "tika/mallet": "tika-mallet"}
PREFIXES = ["specialized-expert", "tika-mallet-tantivy", "entity-graph", "rust-mallet", "tika-mallet",
            "classical", "adaptive", "ensemble", "embeddings", "legacy", "tantivy", "graphify", "turso"]


def slug(value: str) -> str:
    """Create a deterministic safe label for a known public report route."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def family_name(value: str) -> str:
    """Normalize published family labels without inferring task-specific identities."""
    text = value.replace("`", "").strip().lower()
    for label, family in sorted(FAMILY_NAMES.items(), key=lambda item: -len(item[0])):
        if text == label or text.startswith(label + " "):
            return family
    normalized = slug(text)
    for prefix in PREFIXES:
        if normalized == prefix or normalized.startswith(prefix + "-"):
            return prefix
    raise ValueError(f"unknown published family label: {value}")


def number(text: str, unit: str) -> float | None:
    """Parse explicit report units, preserving missing values and rejecting malformed metrics."""
    cleaned = text.strip().replace("**", "").replace("`", "").replace(",", "")
    if cleaned.lower() in {"n/a", "na", "—", "", "not measured"}:
        return None
    cleaned = cleaned.removesuffix(" ms").removesuffix("%")
    value = float(cleaned)
    if unit == "ratio":
        value *= 100
    if not math.isfinite(value) or value < 0 or (unit in {"ratio", "percent"} and value > 100):
        raise ValueError("invalid report metric")
    return value


def table(text: str, required_header: str) -> list[dict[str, str]]:
    """Read exactly one bounded Markdown table by a declared header name."""
    lines = text.splitlines()
    matches = []
    for index, line in enumerate(lines[:-1]):
        if not line.startswith("|") or not re.fullmatch(r"[| :\-]+", lines[index + 1]):
            continue
        headers = [cell.strip() for cell in line.strip("|").split("|")]
        if required_header not in headers:
            continue
        rows = []
        for row in lines[index + 2:]:
            if not row.startswith("|"):
                break
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) != len(headers):
                raise ValueError("report table width mismatch")
            rows.append(dict(zip(headers, cells)))
        matches.append(rows)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one report table containing {required_header!r}")
    return matches[0]


def skill_path(family: str) -> str | None:
    """Link an aggregate family to its actual skill package."""
    special = {"specialized-expert": "build-specialized-skill", "integrated-classical": "build-classical-knowledge-skill",
               "upstream-bm25": None}
    name = special.get(family, "consult-semantic-okf" + ("" if family == "legacy" else "-" + family))
    if name is None:
        return None
    path = Path("skills") / name / "SKILL.md"
    if not (REPO / path).is_file():
        raise ValueError(f"skill package is missing: {name}")
    return path.as_posix()


def load_dataset(spec: dict[str, Any], root: Path = REPO) -> dict[str, Any]:
    """Normalize one known public aggregate without opening raw or sealed task material."""
    source = root / spec["path"]
    content = source.read_bytes()
    text = content.decode("utf-8")
    rows = []
    if spec["format"] in {"comparison-json", "enterprise-json"}:
        original = json.loads(text)
        enterprise = spec["format"] == "enterprise-json"
        if enterprise and (original["status"] != "pass" or original["question_count"] != spec["question_count"]):
            raise ValueError("incomplete EnterpriseRAG comparison")
        for row in original["ranking" if enterprise else "alternatives"]:
            values = row["metrics"]
            metrics = {key: number(str(values[key]), "ratio" if enterprise else "percent")
                       for key in ("ndcg_at_10", "recall_at_10", "mrr_at_10")}
            metrics["p95_ms"] = number(str(row["representative_p95_ms"] if enterprise
                                            else values["representative_p95_ms"]), "ms")
            route = row["label"]
            family = family_name(row["family"] if enterprise else row["id"])
            rows.append({"family": family, "route": route, "status": "measured", "metrics": metrics})
    else:
        for row in table(text, spec["table_header"]):
            route = row[spec["route_column"]].replace("`", "")
            if spec.get("family_from_tau3"):
                family = "upstream-bm25" if route.startswith("Upstream") else "integrated-classical"
            else:
                family = spec.get("fixed_family") or family_name(row[spec["family_column"]] if "family_column" in spec else route)
            valid = "status_column" not in spec or row[spec["status_column"]] == "pass"
            metrics = {key: number(row[column], unit) for key, (column, unit) in spec["metrics"].items()}
            rows.append({"family": family, "route": route, "status": "measured" if valid else "unavailable",
                         "metrics": metrics})
    if len(rows) != spec["expected_rows"]:
        raise ValueError(f"row count drift: {spec['id']}")
    if len({(row["family"], row["route"]) for row in rows}) != len(rows):
        raise ValueError("duplicate strategy rows")
    for row in rows:
        if row["status"] == "measured" and row["metrics"].get(spec["primary_metric"]) is None:
            raise ValueError("measured row has no primary metric")
    return {"id": spec["id"], "label": spec["label"], "scope": spec["scope"],
            "question_count": spec["question_count"], "primary_metric": spec["primary_metric"],
            "source": spec["path"], "source_report": spec.get("report", spec["path"]),
            "source_sha256": hashlib.sha256(content).hexdigest(), "rows": rows}


def leaders(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    """Retain every exact tie at published precision within one metric contract."""
    metric = dataset["primary_metric"]
    rows = [row for row in dataset["rows"] if row["status"] == "measured"
            and row["metrics"].get(metric) is not None]
    if not rows:
        return []
    highest = max(row["metrics"][metric] for row in rows)
    return [row for row in rows if row["metrics"][metric] == highest]


def metric_text(value: float | None, percent: bool = True) -> str:
    """Show unavailable data without treating it as zero."""
    return "N/A" if value is None else f"{value:.2f}" + ("%" if percent else "")


def route_name(row: dict[str, Any]) -> str:
    """Keep a published family prefix without displaying it twice."""
    prefix = row["family"] + " / "
    return row["route"] if row["route"].startswith(prefix) else prefix + row["route"]


def render_table(rows: list[dict[str, Any]], primary: str) -> list[str]:
    """Render comparable numeric metrics only; explain eligibility outside the table."""
    keys = [primary, *[key for key in ("recall_at_10", "mrr_at_10", "ndcg_at_10", "p95_ms") if key != primary]]
    lines = ["| Skill family / route | " + " | ".join(METRICS[key] for key in keys) + " |",
             "|---|" + "---:|" * len(keys)]
    for row in sorted(rows, key=lambda row: (-(row["metrics"].get(primary) or 0), row["family"], row["route"])):
        lines.append(f"| {route_name(row)} | " + " | ".join(
            metric_text(row["metrics"].get(key), key != "p95_ms") for key in keys) + " |")
    return lines


def comparison_projection(group: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Bind and validate a complete metric-only primary table using the existing contract."""
    spec = importlib.util.spec_from_file_location("catalog_comparison_contract", REPO / "evaluations/validate_comparison_contract.py")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    primary = group["primary_metric"]
    rows = [row for row in group["rows"] if row["status"] == "measured"]
    rows.sort(key=lambda row: (-row["metrics"][primary], row["family"], row["route"]))
    keys = [primary, *[key for key in ("recall_at_10", "mrr_at_10", "ndcg_at_10", "p95_ms") if key != primary]]
    keys = [key for key in keys if all(row["metrics"].get(key) is not None for row in rows)]
    contract = {"schema_version": "final-report-comparison/1.0", "report": f"{group['id']}.md",
                "heading": "## Direct comparison",
                "dataset_scope": {"dataset_id": group["id"], "cohort": "published-source-cohort",
                                  "candidate_budget": "top-10", "identity_grouping": "as-defined-by-bound-source-report",
                                  "metric_contract": "published-aggregate-sha256:" + group["source_sha256"]},
                "metrics": [{"id": key, "label": METRICS[key], "unit": "ms" if key == "p95_ms" else "percent",
                             "aggregation": "percentile_95" if key == "p95_ms" else "mean",
                             "direction": "lower" if key == "p95_ms" else "higher", "display_precision": 2}
                            for key in keys],
                "alternatives": [{"id": slug(row["family"] + "-" + row["route"]),
                                  "label": route_name(row),
                                  "metrics": {key: row["metrics"][key] for key in keys}} for row in rows]}
    lines = [contract["heading"], "", "| Pos. | Pair / strategy | " + " | ".join(METRICS[key] for key in keys) + " |",
             "|---:|---|" + "---:|" * len(keys)]
    for index, row in enumerate(contract["alternatives"], 1):
        lines.append(f"| {index} | {row['label']} | " + " | ".join(
            validator.format_metric(row["metrics"][metric["id"]], metric) for metric in contract["metrics"]) + " |")
    validator.validate_report_against_contract("\n".join(lines), contract)
    omitted = [row["family"] for row in group["rows"] if row["status"] != "measured"]
    if omitted:
        lines.extend(["", "Omitted because this historical contract has no comparable measurements: "
                      + ", ".join(sorted(set(omitted))) + ". These are unavailable, not zero-score results."])
    if "p95_ms" not in keys:
        lines.extend(["", "P95 is not available for every measured alternative and is omitted from this primary table."])
    return contract, lines


def render(datasets: list[dict[str, Any]]) -> dict[str, str]:
    """Create navigation, per-dataset, per-skill, and CTA views from the same aggregates."""
    files: dict[str, str] = {}
    overview = ["# Evaluation report hub", "", "Reviewed results organized by dataset, skill, and cost/time/quality (CTA).",
                "", "[By skill](skills/README.md) · [CTA](cta/README.md) · [Evolution studies](evolution/README.md) · [Report catalog](../COMPARISON-REPORTS.md)", "",
                "The [stratified Enterprise evolution E7](evolution/e7/README.md) covers all eight families "
                "on 120 development questions and 6,000 complete documents. Its "
                "[strategy coverage](evolution/e7/strategy-coverage.md) distinguishes declared mechanisms, "
                "native attempts and completed searches. The campaign page owns current progress; interim "
                "development scores do not enter the completed all-500 comparison table.", "",
                "The earlier [Enterprise evolution sweep E6](evolution/e6/README.md) follows eight knowledge families "
                "through a fixed tactic catalog, with three consecutive misses per tactic and a separate final validation gate. "
                "Its campaign page records the execution and publication status.", "",
                "The [agent-selected source-skill comparison](enterprise-source-skills/README.md) evaluates a unified "
                "expert and nine application experts with complete document bodies. The "
                "[ingestion scope correction](enterprise-source-skills/ingestion-scope-20260907.md) binds "
                "historical Enterprise v1/e6 retrieval to a title-only projection. Do not pool the two contracts.", "",
                "The [knowledge-skill generator evolution](evolution/generator-g2/README.md) compares explicit "
                "source selection and normalized coverage auditing with the incoming generator, using a "
                "separate independent construction gate. Its metric is not a retrieval or answer score.", "",
                "The [EnterpriseRAG generator replay](enterprise-generator-g2/README.md) compares the incoming "
                "and G2 versions on identical complete documents, with family, category and CTA views.", "",
                "The [full-corpus Classical run](enterprise-classical-full/README.md) covers all 511,962 "
                "documents and 500 questions. Only Classical BM25 is measured; its retrieval result "
                "does not establish an official answer-quality score or public-table position.", "",
                "The [internal Luna answer evaluation](enterprise-classical-full/luna.md) reuses that "
                "full-corpus retrieval with Luna for both answering and judging; its score is separate "
                "from the public GPT-5.4 judge contract.", "",
                "The earlier [construction-profile study](evolution/e5/README.md) records controlled comparisons "
                "across EnterpriseRAG, Astro, architecture and data science. Its reports provide skill, profile, "
                "dataset and CTA views, with completion status and independent-validation availability kept explicit.", "",
                "## Historical retrieval comparisons", "",
                "The table identifies the highest observed primary metric within each published contract. "
                "Ties at the source's precision are preserved. These are retrieval measurements; generated-answer "
                "correctness, promotion, and a universal cross-dataset winner are not established.", "",
                "| Dataset | Highest observed skill / route | Primary metric | Value |", "|---|---|---|---:|"]
    families = sorted({row["family"] for group in datasets for row in group["rows"]})
    for group in datasets:
        best = leaders(group)
        labels = "; ".join(route_name(row) for row in best) or "No comparable result"
        value = metric_text(best[0]["metrics"][group["primary_metric"]]) if best else "N/A"
        overview.append(f"| [{group['label']}](datasets/{group['id']}.md) | {labels} | {METRICS[group['primary_metric']]} | {value} |")
        source_link = "../../../" + group["source_report"]
        contract, primary_lines = comparison_projection(group)
        lines = [f"# {group['label']}", "", *primary_lines, "", group["scope"], "",
                 f"[Original report]({source_link}) · [Report hub](../README.md) · [CTA](../cta/README.md)", "",
                 "Primary comparison: **" + METRICS[group["primary_metric"]] + "**. "
                 "N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.", "",
                 "Publication source SHA-256: `" + group["source_sha256"] + "`.", ""]
        if group["id"] in {"enterprise-rag-bench-40-v1", "enterprise-rag-e6-development-40"}:
            lines.extend(["**Scope correction:** these historical Enterprise records contain titles without mapped "
                          "document bodies. See the [ingestion audit](../enterprise-source-skills/ingestion-scope-20260907.md). "
                          "Their original scores are preserved and are not full-text retrieval measurements.", "",
                          "[Enterprise evolution sweep and its separate development contract](../evolution/e6/README.md)", ""])
        files[f"datasets/{group['id']}.md"] = "\n".join(lines)
        files[f"datasets/{group['id']}.comparison.json"] = json.dumps(contract, indent=2, sort_keys=True, allow_nan=False) + "\n"
    overview.extend(["", "Historical reports keep their original source locations and meanings. "
                     "The hub reads only reviewed aggregate sources and does not reopen sealed tasks. "
                     "Latency and costs from different hosts, cache policies, models, or cohorts must be interpreted separately.", "",
                     "[Data storage and reproduction](../../docs/evaluation-datasets-and-reports.md)", ""])
    files["README.md"] = "\n".join(overview)
    skill_index = ["# Reports by skill", "", "[Report hub](../README.md) · [Enterprise evolution](../evolution/e6/README.md) · [Construction-profile evolution](../evolution/e5/README.md)", "",
                   "[Stratified Enterprise evolution E7: all eight families, opportunity counts and campaign status](../evolution/e7/README.md)", "",
                   "[Agent-selected skills by application](../enterprise-source-skills/README.md)", "",
                   "[Knowledge-skill generator: construction evolution and independent acceptance](../evolution/generator-g2/README.md)", "",
                   "[EnterpriseRAG: incoming versus G2 generator, all eight families](../enterprise-generator-g2/README.md)", "",
                   "[EnterpriseRAG: Classical BM25 over the complete corpus and all 500 questions](../enterprise-classical-full/README.md)", "",
                   "[EnterpriseRAG: internal Classical + Luna answer evaluation](../enterprise-classical-full/luna.md)", "",
                   "The table links historical skill comparisons. The evolution campaign pages provide controlled per-family comparisons with their execution and independent-validation status.", "",
                   "| Skill family | Reports |", "|---|---|"]
    for family in families:
        path = skill_path(family)
        lines = [f"# {family}: dataset results", "", "[Report hub](../README.md) · [All skills](README.md)", "",
                 "This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.", ""]
        if path:
            lines.extend([f"[Skill package](../../../{path})", ""])
        if family in {"legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble", "graphify", "turso"}:
            lines.extend(["[Stratified Enterprise evolution E7 and this family's opportunity status](../evolution/e7/README.md)", "",
                          "[Earlier Enterprise evolution E6](../evolution/e6/README.md)", ""])
        if family == "integrated-classical":
            lines.extend(["The tau3 source reports identical rankings for the integrated Classical and "
                          "[chunked Classical](../../../skills/build-classical-chunked-knowledge-skill/SKILL.md) packages.", ""])
        for group in datasets:
            rows = [row for row in group["rows"] if row["family"] == family]
            if not rows:
                continue
            lines.extend([f"## {group['label']}", "", group["scope"], "",
                          f"[All compared skills](../datasets/{group['id']}.md)", "",
                          *render_table(rows, group["primary_metric"]), ""])
        lines.extend(["[Cost, time, quality, and measurement limits](../cta/README.md)", ""])
        files[f"skills/{family}.md"] = "\n".join(lines)
        skill_index.append(f"| {family} | [Dataset comparisons]({family}.md) |")
    files["skills/README.md"] = "\n".join(skill_index) + "\n"
    token_path = "evaluations/semantic-okf-datasets/reports/20260730-semantic-okf-token-usage.md"
    token_text = (REPO / token_path).read_text(encoding="utf-8")
    cta = ["# CTA: cost, time, and quality", "", "[Report hub](../README.md) · [By skill](../skills/README.md) · [Enterprise evolution](../evolution/e6/README.md) · [Construction-profile evolution](../evolution/e5/README.md)", "",
           "[Stratified Enterprise evolution E7](../evolution/e7/README.md) records native development time, "
           "qualified retrieval scores and execution errors. Its declared model-call budget is zero; "
           "a timed-out attempt has no retrieval quality measurement. Follow the campaign for completion "
           "of all eight families, the paired all-500 comparison and the separate transfer gate.", "",
           "The evolution studies report query P95, two-build construction time, full native execution time and storage under their fixed runtimes. Follow each campaign's execution and publication status. The historical comparisons below retain their own measurement contracts.", "",
           "CTA is interpreted here as cost, time, and accuracy/quality. Retrieval relevance is measured by "
           "nDCG, Recall, MRR, or complete evidence; it is not generated-answer accuracy. "
           "Missing USD costs or answer-quality measurements remain N/A.", "",
           "## Retrieval time and quality by dataset", "",
           "P95 covers the exact route and runtime described in each source report. "
           "Initialization, warm caches, hardware, and corpus sizes vary across historical studies. "
           "No cross-host latency winner or cost-to-quality composite is computed.", "",
           "| Dataset | Highest primary-metric route(s) | P95 (ms), in route order | Provider USD for new local retrieval |",
           "|---|---|---:|---:|"]
    for group in datasets:
        best = leaders(group)
        cta.append(f"| [{group['label']}](../datasets/{group['id']}.md) | " + "; ".join(row["route"] for row in best)
                   + " | " + "; ".join(metric_text(row["metrics"].get("p95_ms"), False) for row in best)
                   + " | " + ("0.00" if group["id"] == "enterprise-rag-bench-40-v1" else "N/A") + " |")
    cta.extend(["", "## Historical agent token usage: construction", "",
                "These are actual agent tokens on the GraphRAG construction contract, not dollar prices. "
                "All eight arms produced two qualified folders under the same published model and runtime.", "",
                f"[Exact contract and original report](../../../{token_path})", "",
                "| Skill | Calls | Qualified | Mean tokens / folder |", "|---|---:|---:|---:|"])
    for row in table(token_text, "Mean input/folder"):
        cta.append(f"| {row['Strategy']} | {row['Calls']} | {row['Qualified']} | {row['Mean total/folder']} |")
    cta.extend(["", "## Historical agent token usage: consultation", "",
                "Every family received the same six questions. Runtime errors remain visible in the denominator. "
                "The complete zero-error arms are Legacy and Turso; early failures cannot establish efficiency.", "",
                "| Skill | Queries | Complete | Runtime errors | Mean tokens / submitted query |",
                "|---|---:|---:|---:|---:|"])
    for row in table(token_text, "Mean total/submitted query"):
        cta.append(f"| {row['Strategy']} | {row['Queries']} | {row['Complete']} | {row['Runtime errors']} | {row['Mean total/submitted query']} |")
    cta.extend(["", "Harbor input already includes cached input; total is input plus output. "
                "Deterministic EnterpriseRAG retrieval used zero model calls and zero LLM tokens. "
                "Local machine cost was not measured.", "", "## Generated-answer quality", "",
                "Use the [comparison catalog](../../COMPARISON-REPORTS.md) for the current isolated semantic audit "
                "and the incomplete historical multi-family campaigns. Those results have separate cohort and evidence gates; "
                "they are not pooled with document-retrieval scores.", ""])
    cta.extend(["[Agent-selected Enterprise source skills and their separate answer/CTA contract](../enterprise-source-skills/README.md)", ""])
    cta.extend(["[Knowledge-skill generator: deterministic construction quality and execution cost](../evolution/generator-g2/README.md)", ""])
    cta.extend(["[EnterpriseRAG generator replay: fixed full-text retrieval and construction costs](../enterprise-generator-g2/cta.md)", ""])
    cta.extend(["[EnterpriseRAG full corpus: Classical construction, 500-query latency and separate answer-stage usage](../enterprise-classical-full/cta.md)", ""])
    files["cta/README.md"] = "\n".join(cta)
    files["catalog.json"] = json.dumps({"schema_version": "evaluation-report-catalog/1.0", "datasets": datasets,
                                      "token_source_sha256": hashlib.sha256(token_text.encode()).hexdigest()},
                                     indent=2, sort_keys=True, allow_nan=False) + "\n"
    return files


def main() -> int:
    """Regenerate or check all report views using only tracked aggregate publications."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    specs = json.loads((REPO / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    files = render([load_dataset(spec) for spec in specs])
    for relative, content in files.items():
        path = OUTPUT / relative
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise ValueError(f"report drift: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "pass", "datasets": len(specs), "report_files": len(files)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
