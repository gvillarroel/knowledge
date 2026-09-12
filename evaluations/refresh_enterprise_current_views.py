#!/usr/bin/env python3
"""Refresh bounded current E14 summaries from explicitly chosen public aggregates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("evaluations/reports/evolution/e14")
FAMILIES = {"legacy": "Legacy", "turso": "Turso", "adaptive": "Adaptive",
            "embeddings": "Embeddings", "classical": "Classical", "graphify": "Graphify",
            "ensemble": "Ensemble", "entity-graph": "Entity Graph"}
APPLICATIONS = {"confluence": "Confluence", "fireflies": "Fireflies", "github": "GitHub",
                "gmail": "Gmail", "google_drive": "Google Drive", "hubspot": "HubSpot",
                "jira": "Jira", "linear": "Linear", "slack": "Slack"}
SECTIONS = {
    "docs/enterprise-family-report-index.md": ("Verified EnterpriseRAG comparison", "Checkpoint history"),
    "evaluations/reports/datasets/enterprise-rag-stratified-development-120.md": ("Retained comparison", "Observation history"),
    "evaluations/reports/evolution/e14/README.md": ("Verified development status", "Published observation history"),
}
INDEXES = ["docs/README.md", *SECTIONS, "evaluations/reports/README.md",
           "evaluations/reports/cta/README.md", "evaluations/reports/evolution/README.md",
           "evaluations/reports/skills/README.md"]
LEAF = re.compile(r"(?:legacy|turso|adaptive|embeddings|classical|graphify|ensemble|entity-graph)-generation-\d{3}-001")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _path(root: Path, relative: str | Path) -> Path:
    path = root / relative
    _require(not Path(relative).is_absolute() and path.resolve() == path
             and path.is_relative_to(root) and path.is_file(), f"Unsafe or missing file: {relative}")
    return path


def _object(pairs: list[tuple[str, object]]) -> dict:
    result = dict(pairs)
    _require(len(result) == len(pairs), "Duplicate JSON keys")
    return result


def _load(root: Path, relative: Path, expected: str) -> dict:
    _require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None, "Expected SHA-256 is required")
    data = _path(root, relative).read_bytes()
    _require(_sha(data) == expected, f"Aggregate digest mismatch: {relative}")
    def reject_constant(value: str) -> None:
        raise ValueError(f"Non-finite JSON constant: {value}")
    value = json.loads(data, object_pairs_hook=_object, parse_constant=reject_constant)
    _require(isinstance(value, dict), "Aggregate must be an object")
    return value


def _ratio(value: object) -> float:
    _require(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1,
             "Expected a finite numeric ratio, not a boolean or string")
    return value


def _date(value: str) -> str:
    parsed = datetime.fromisoformat(value)
    _require(parsed.tzinfo is not None, "Aggregate timestamp requires a time zone")
    return parsed.isoformat()


def _projection(report: dict, inventory: dict) -> dict:
    _require(report["schema"] == "enterprise-e14-family-gain-and-retained-comparison/1.0", "Unsupported comparison schema")
    _require(inventory["schema"] == "enterprise-e14-opportunity-accounting/1.1", "Unsupported inventory schema")
    for value in (report, inventory):
        _require(all(value[k] is False for k in ("private_gate_access", "promoted", "goal_complete")), "Incompatible report scope")
    _require(report["new_family_development_incumbent"] is True and report["report_operation_native_runs"] == 0,
             "Expected a completed gain publication")
    cross, prefix = report["cross_family_comparison"], report["family_prefix"]
    _require(all(cross[k] is False for k in ("private_gate_access", "promoted", "goal_complete", "final_all500_complete"))
             and prefix["private_gate_access"] is False and prefix["promoted"] is False, "Incompatible nested report scope")
    for key, expected in (("questions", 120), ("retrieval_eligible", 112), ("complete_documents", 6000),
                          ("eligible_population_weight", 470)):
        _require(type(cross[key]) in (int, float) and cross[key] == prefix[key] == expected, "Different workload")
    _require(cross["required_family_count"] == 8 and cross["display_multiplier"] == 100
             and cross["metric"] == "frozen-category-weighted ndcg_at_10", "Different comparison contract")
    qualified = cross["qualified_families"]
    _require(len(set(qualified)) == len(qualified) and set(qualified) <= FAMILIES.keys(), "Invalid qualified families")
    retained = {r["family"]: r for r in report["retained_comparison"]}
    _require(len(report["retained_comparison"]) == len(retained) == 8 and set(retained) == FAMILIES.keys(), "Expected eight distinct families")
    groups = {(g["dimension"], g["group"]): g for g in cross["groups"]}
    _require(len(groups) == len(cross["groups"]) == 20, "Expected distinct retained groups")
    _require({name for dimension, name in groups if dimension == "application"} == APPLICATIONS.keys(), "Different application cohorts")
    scores = groups["all", "all"]["retained_metrics"]
    _require(set(scores) == set(qualified), "Qualified metric coverage differs")
    display = {}
    for family in FAMILIES:
        display[family] = f"{100 * _ratio(scores[family]['ndcg_at_10']):.2f}" if family in qualified else "Unavailable"
        _require(retained[family]["retained_display_value"] == display[family], "Rounded score disagrees with full precision")
        _require((retained[family]["current_start"] == "Qualified") == (family in qualified), "Qualification disagrees with metrics")
        if family not in qualified:
            _require(retained[family]["current_start"] == "Execution error; not qualified", "Unsupported unavailable qualification")
    tolerance = _ratio(cross["tie_absolute_tolerance"])
    leaders = {}
    for app in APPLICATIONS:
        group = groups["application", app]
        _require(set(group["retained_metrics"]) == set(qualified), "Missing application metrics")
        values = {f: _ratio(m["ndcg_at_10"]) for f, m in group["retained_metrics"].items()
                  if m["ndcg_at_10"] is not None}
        leaders[app] = sorted(f for f, score in values.items() if abs(score - max(values.values())) <= tolerance)
        _require(group["descriptive_ndcg_leaders"] == leaders[app], "Application leaders disagree with metrics")
    step = prefix["prefix"][-1]
    family = prefix["family"]
    _require(type(prefix["through_generation"]) is int and prefix["through_generation"] > 0
             and family in qualified and step["improved"] is True
             and step["candidate"] == prefix["retained_candidate"]
             and step["generation"] == prefix["through_generation"], "Incomplete retained observation")
    before, after = _ratio(step["previous_incumbent"]["score"]), _ratio(prefix["retained_score"])
    _require(after > before and after == scores[family]["ndcg_at_10"], "Gain disagrees with retained comparison")
    overall = next(g for g in prefix["groups"] if g["dimension"] == "all" and g["group"] == "all")
    pairs = [p["paired_cases"] for p in overall["comparisons"]
             if p["reference"] == step["previous_incumbent"]["candidate"] and p["candidate"] == step["candidate"]]
    _require(len(pairs) == 1, "Ambiguous paired observation")
    pair = pairs[0]
    _require(all(type(pair[k]) is int and pair[k] >= 0 for k in ("improved", "regressed", "tied", "without_references"))
             and pair["improved"] + pair["regressed"] + pair["tied"] == 112 and pair["without_references"] == 8,
             "Invalid paired case counts")
    closures = inventory["verified_catalog_closures"]
    closed = [row["family"] for row in closures]
    _require(type(inventory["recorded_catalog_stops"]) is int
             and len(set(closed)) == len(closed) == inventory["recorded_catalog_stops"]
             and set(closed) <= FAMILIES.keys(), "Invalid catalog closure inventory")
    _require(all(row["recorded_catalog_stop"] == "full-round-without-improvement" for row in closures), "Unsupported catalog stop")
    gaps = sum(len(row["permanently_unavailable_originals"]) for row in closures)
    _require(type(inventory["historical_unavailable_hypotheses_among_stopped_families"]) is int
             and gaps == inventory["historical_unavailable_hypotheses_among_stopped_families"], "Historical gap count differs")
    return {"family": family, "generation": prefix["through_generation"], "before": before, "after": after,
            "pair": pair, "display": display, "qualified": qualified, "leaders": leaders,
            "closed": closed, "gaps": gaps, "snapshot": _date(inventory["snapshot_at_utc"]),
            "published": _date(report["generated_at_utc"])}


def _body(page: Path, report_leaf: str, inventory_leaf: str, data: dict) -> str:
    link = lambda leaf, name: Path(os.path.relpath(BASE / leaf / name, page.parent)).as_posix()
    result, comparison = link(report_leaf, "README.md"), link(report_leaf, "comparison.md")
    lines = ["", f"Explicitly selected published observation: **{FAMILIES[data['family']]} generation {data['generation']}**, "
             f"published {data['published']}. [Source-bound result]({result}).", "",
             "The fixed development workload contains **120 stratified questions, 112 retrieval-eligible questions "
             "and 6,000 complete documents**. Scores are frozen-category-weighted **nDCG@10 x100**; "
             "the eligible population weight is 470.", "",
             "| Family | Retained nDCG@10 x100 | Qualification |", "| --- | ---: | --- |"]
    for family, title in FAMILIES.items():
        state = "Qualified" if family in data["qualified"] else "Unavailable after execution error"
        lines.append(f"| {title} | {data['display'][family]} | {state} |")
    pair = data["pair"]
    lines += ["", f"The selected {FAMILIES[data['family']]} gain is **{100 * data['before']:.2f} to {100 * data['after']:.2f}**. "
              f"Paired questions: **{pair['improved']} improve, {pair['regressed']} regress and {pair['tied']} tie**; "
              "eight questions lack retrieval references. Other retained families keep their original observations.", "",
              "### Catalog status and remaining work", "",
              f"The [catalog inventory]({link(inventory_leaf, 'README.md')}) is a separate snapshot at **{data['snapshot']}**. "
              f"It records **{len(data['closed'])} catalog stops**: {', '.join(FAMILIES[f] for f in data['closed'])}. "
              f"It also preserves **{data['gaps']} unavailable historical hypotheses** among stopped families. "
              "Catalog closure does not imply complete historical measurement coverage. This dated inventory "
              "does not supply current reservation counts or replace the newer retained scores above.", "",
              f"**{len(data['qualified'])} of eight families have qualified retrieval references** in this comparison. "
              "Remaining work includes outstanding family qualification and evolution, the paired joint development replay, "
              "one whole-bundle freeze, the all-500 comparison and independent acceptance. Validation stays sealed "
              "until the selected candidate is frozen.", "", "### Applications, categories and CTA", "",
              f"[General application/category comparison]({comparison}) · "
              f"[Paired groups]({link(report_leaf, 'groups.md')}) · [Retained-family CTA]({link(report_leaf, 'cta.md')}).", "",
              "Application cohorts overlap. Highest values describe the supplied comparison; no application router is tested.", "",
              "| Application | Highest retained nDCG |", "| --- | --- |"]
    for app, title in APPLICATIONS.items():
        lines.append(f"| {title} | {', '.join(FAMILIES[f] for f in data['leaders'][app]) or 'Unavailable'} |")
    lines += ["", "### Measurement boundaries", "",
              "These development retrieval metrics do not establish all-500 results, generated-answer Overall, "
              "statistical significance, canonical promotion or a public leaderboard position. Host and orchestration "
              "costs are unpriced. Historical observations below retain their original scope and counts.", ""]
    related = lambda name: Path(os.path.relpath(Path("evaluations/reports") / name, page.parent)).as_posix()
    lines += [f"The earlier [Classical full-corpus run]({related('datasets/enterprise-rag-classical-full-500.md')}), "
              f"[Luna answer audit]({related('enterprise-classical-full/luna.md')}) and "
              f"[cross-dataset comparisons]({related('README.md')}#historical-retrieval-comparisons) "
              "retain their separate workloads and scoring contracts.", ""]
    return "\n".join(lines) + "\n"


def _replace_section(original: bytes, first: str, last: str, replacement: str) -> bytes:
    starts = list(re.finditer(rb"(?m)^## " + re.escape(first.encode()) + rb"(\r?\n)", original))
    ends = list(re.finditer(rb"(?m)^## " + re.escape(last.encode()) + rb"\r?$", original))
    _require(len(starts) == len(ends) == 1 and starts[0].end() < ends[0].start(), "Missing, duplicate or reversed current-section boundaries")
    body = replacement.replace("\n", starts[0].group(1).decode()).encode()
    return original[:starts[0].end()] + body + original[ends[0].start():]


def _bound_predecessor(root: Path, report: dict, target: Path) -> bool:
    family, generation = target.parent.name.rsplit("-generation-", 1)
    selected = report["cross_family_comparison"]["selected_native_rows"].get(family)
    if selected is None or int(generation[:3]) > selected["generation"]:
        return False
    pending, seen = [report], {}
    while pending:
        value = pending.pop()
        for name, digest in value.get("source_sha256", {}).items():
            path = Path(name)
            if path.parent.parent != BASE or path.name != "aggregate.json" or LEAF.fullmatch(path.parent.name) is None:
                continue
            if path in seen:
                _require(seen[path] == digest, "Conflicting public predecessor digests")
                continue
            seen[path] = digest
            previous = _load(root, path, digest)
            if path == target:
                return True
            pending.append(previous)
    return False


def plan_views(root: Path, report_leaf: str, report_sha: str, inventory_leaf: str, inventory_sha: str) -> dict[str, tuple[bytes, bytes]]:
    """Plan only current sections and obsolete latest-link labels; never select a candidate."""
    root = root.resolve()
    _require(LEAF.fullmatch(report_leaf) is not None and re.fullmatch(r"opportunity-accounting-\d{3}", inventory_leaf) is not None,
             "Expected explicit public E14 leaf names")
    report = _load(root, BASE / report_leaf / "aggregate.json", report_sha)
    inventory = _load(root, BASE / inventory_leaf / "aggregate.json", inventory_sha)
    for name in ("README.md", "comparison.md", "groups.md", "cta.md"):
        _path(root, BASE / report_leaf / name)
    _path(root, BASE / inventory_leaf / "README.md")
    data = _projection(report, inventory)
    _require(report_leaf == f"{data['family']}-generation-{data['generation']:03d}-001", "Leaf identity disagrees with observation")
    primary = {*INDEXES, f"evaluations/reports/skills/{data['family']}.md"}
    pages = [*INDEXES, *[f"evaluations/reports/skills/{family}.md" for family in FAMILIES]]
    changes = {}
    for relative in pages:
        page = _path(root, relative)
        original = page.read_bytes()
        selected_links = []
        def relabel(match: re.Match[bytes]) -> bytes:
            label, target = match.group(1), match.group(2)
            if b"latest general comparison" not in label.lower() and label != b"Latest general application/category comparison":
                return match.group(0)
            destination = (page.parent / target.decode()).resolve()
            _require(destination.is_relative_to(root / BASE) and destination.name in ("README.md", "comparison.md")
                     and LEAF.fullmatch(destination.parent.name) is not None, "Unexpected latest-comparison link")
            if destination.parent.name == report_leaf:
                selected_links.append(target)
                return match.group(0)
            prior = (destination.parent / "aggregate.json").relative_to(root)
            _require(_bound_predecessor(root, report, prior), "Refusing to supersede a comparison outside the supplied predecessor bindings")
            label = re.sub(rb"Latest general application/category comparison", b"Comparison at this observation", label, flags=re.I)
            label = re.sub(rb"latest general comparison", b"comparison at this observation", label, flags=re.I)
            return b"[" + label + b"](" + target + b")"
        updated = re.sub(rb"\[([^\]\r\n]+)\]\(([^)\r\n]+)\)", relabel, original)
        if relative in primary:
            _require(bool(selected_links), f"Selected observation has not been exported to this index: {relative}")
        if relative in SECTIONS:
            updated = _replace_section(updated, *SECTIONS[relative], _body(Path(relative), report_leaf, inventory_leaf, data))
        changes[relative] = original, updated
    return changes


def apply_views(root: Path, changes: dict[str, tuple[bytes, bytes]], *, check: bool = False) -> list[str]:
    """Preflight every input; atomically replace each changed index or check without writes."""
    root = root.resolve()
    allowed = set(INDEXES) | {f"evaluations/reports/skills/{f}.md" for f in FAMILIES}
    _require(set(changes) <= allowed, "Output is outside mutable report indexes")
    paths = {name: _path(root, name) for name in changes}
    for name, path in paths.items():
        _require(path.read_bytes() == changes[name][0], f"Index changed after planning: {name}")
    different = [name for name, (before, after) in changes.items() if before != after]
    if check:
        _require(not different, "Current report views differ: " + ", ".join(different))
        return []
    for name in different:
        path, temporary = paths[name], None
        try:
            with tempfile.NamedTemporaryFile(prefix=".enterprise-current-", dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(changes[name][1])
            _require(path.read_bytes() == changes[name][0], f"Index changed before replacement: {name}")
            os.replace(temporary, path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return different


def main(argv: list[str] | None = None) -> int:
    """Check or apply explicitly bound current-view updates without running evaluations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--comparison-sha256", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--inventory-sha256", required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    changes = plan_views(ROOT, args.comparison, args.comparison_sha256, args.inventory, args.inventory_sha256)
    changed = apply_views(ROOT, changes, check=args.check)
    print(json.dumps({"status": "pass", "mode": "check" if args.check else "apply", "changed_indexes": changed,
                      "comparison": args.comparison, "comparison_sha256": args.comparison_sha256,
                      "inventory": args.inventory, "inventory_sha256": args.inventory_sha256,
                      "new_native_jobs": 0, "candidate_selection_performed": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
