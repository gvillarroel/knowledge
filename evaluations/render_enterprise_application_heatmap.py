#!/usr/bin/env python3
"""Render an explicitly bound public E14 comparison without running evaluations."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("enterprise_heatmap_contract", ROOT / "evaluations/refresh_enterprise_current_views.py")
VIEWS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VIEWS)


def comparison_matrix(root: Path, comparison: str, comparison_sha: str, inventory: str, inventory_sha: str) -> dict:
    """Validate public inputs and preserve unavailable cells and full-precision ties."""
    if VIEWS.LEAF.fullmatch(comparison) is None or re.fullmatch(r"opportunity-accounting-\d{3}", inventory) is None:
        raise ValueError("Expected explicit public comparison and inventory leaves")
    report = VIEWS._load(root, VIEWS.BASE / comparison / "aggregate.json", comparison_sha)
    catalog = VIEWS._load(root, VIEWS.BASE / inventory / "aggregate.json", inventory_sha)
    data = VIEWS._projection(report, catalog)
    cross = report["cross_family_comparison"]
    groups = {(g["dimension"], g["group"]): g for g in cross["groups"]}
    order = [("all", "all", "Overall"), *[("application", app, title) for app, title in VIEWS.APPLICATIONS.items()]]
    rows = []
    for dimension, key, title in order:
        group = groups[dimension, key]
        metrics = group["retained_metrics"]
        counts = {m["retrieval_eligible"] for m in metrics.values()}
        if len(counts) != 1 or any(type(n) is not int or n < 0 for n in counts):
            raise ValueError("Inconsistent reference-bearing question counts")
        values = [metrics.get(family, {}).get("ndcg_at_10") for family in VIEWS.FAMILIES]
        numeric = [VIEWS._ratio(value) for value in values if value is not None]
        leaders = sorted(family for family, value in zip(VIEWS.FAMILIES, values)
                         if value is not None and abs(value - max(numeric)) <= cross["tie_absolute_tolerance"])
        if leaders != group["descriptive_ndcg_leaders"]:
            raise ValueError("Published row leaders disagree with full precision")
        rows.append({"dimension": dimension, "group": key, "title": title,
                     "retrieval_eligible": counts.pop(), "ndcg_at_10": values, "leaders": leaders})
    return {"schema": "enterprise-public-application-heatmap/1.0", "comparison": comparison,
            "comparison_sha256": comparison_sha, "inventory": inventory, "inventory_sha256": inventory_sha,
            "source_published_at": data["published"], "family": data["family"], "generation": data["generation"],
            "families": list(VIEWS.FAMILIES), "family_titles": list(VIEWS.FAMILIES.values()), "rows": rows,
            "questions": 120, "retrieval_eligible": 112, "complete_documents": 6000,
            "metric": cross["metric"], "display_multiplier": 100, "application_cohorts_overlap": True,
            "candidate_selection_performed": False, "new_native_jobs": 0, "retrieval_rescored": False,
            "canonical_skill_promoted": False, "public_leaderboard_result": False}


def render_heatmap(root: Path, comparison: str, comparison_sha: str, inventory: str, inventory_sha: str, output: str) -> Path:
    """Create one append-only PNG/SVG snapshot and a source-bound numeric companion."""
    root = root.resolve()
    if re.fullmatch(r"application-heatmap-\d{3}", output) is None:
        raise ValueError("Output must be a new application-heatmap-NNN leaf")
    destination = root / VIEWS.BASE / output
    if destination.resolve() != destination or not destination.parent.is_dir() or destination.exists():
        raise ValueError("Output must be absent under the existing public E14 report directory")
    data = comparison_matrix(root, comparison, comparison_sha, inventory, inventory_sha)
    cache = root / "tmp/enterprise-application-heatmap-cache"
    if cache.resolve() != cache:
        raise ValueError("Plot cache must remain inside the supplied repository")
    cache.mkdir(parents=True, exist_ok=True)
    previous_cache = os.environ.get("MPLCONFIGDIR")
    os.environ["MPLCONFIGDIR"] = str(cache)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        import numpy as np

        values = np.array([[float("nan") if v is None else 100 * v for v in row["ndcg_at_10"]] for row in data["rows"]])
        with plt.rc_context({"font.family": "DejaVu Sans", "svg.hashsalt": comparison_sha}):
            fig, ax = plt.subplots(figsize=(13, 8.6), facecolor="white")
            try:
                fig.subplots_adjust(left=.19, right=.88, top=.79, bottom=.20)
                cmap = plt.get_cmap("viridis").copy(); cmap.set_bad("#edf0f2")
                chart = ax.imshow(np.ma.masked_invalid(values), vmin=0, vmax=100, cmap=cmap, aspect="auto")
                ax.set_xticks(range(8), data["family_titles"], rotation=20, ha="left", fontsize=10)
                ax.xaxis.tick_top()
                ax.set_yticks(range(len(data["rows"])), [f"{r['title']}  (n={r['retrieval_eligible']})" for r in data["rows"]], fontsize=11)
                ax.tick_params(length=0, pad=9)
                ax.set_xticks(np.arange(-.5, 8, 1), minor=True)
                ax.set_yticks(np.arange(-.5, len(data["rows"]), 1), minor=True)
                ax.grid(which="minor", color="white", linewidth=2)
                ax.tick_params(which="minor", length=0)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                for i, row in enumerate(data["rows"]):
                    for j, family in enumerate(data["families"]):
                        value = values[i, j]
                        missing = np.isnan(value)
                        ax.text(j, i, "N/A" if missing else f"{value:.2f}", ha="center", va="center", fontsize=11,
                                color="#54616c" if missing else ("#172126" if value >= 55 else "white"))
                        if family in row["leaders"]:
                            ax.add_patch(Rectangle((j-.44, i-.40), .88, .80, fill=False, linewidth=2.1, edgecolor="#172126"))
                ax.axhline(.5, color="#172126", linewidth=2)
                bar = fig.colorbar(chart, ax=ax, fraction=.035, pad=.025)
                bar.set_label("nDCG@10 × 100", fontsize=11)
                bar.set_ticks([0, 20, 40, 60, 80, 100])
                fig.text(.04, .95, "EnterpriseRAG: retrieval by application", fontsize=22, weight="bold", color="#172126")
                fig.text(.04, .91, f"Retained profiles after {VIEWS.FAMILIES[data['family']]} generation {data['generation']}  ·  {data['source_published_at'][:10]}", fontsize=12, color="#45535e")
                fig.text(.04, .865, "120 stratified development questions · 112 retrieval-eligible · 6,000 complete documents", fontsize=11)
                fig.text(.04, .135, "Outlined cells have the highest published nDCG in their row; full-precision ties are preserved.", fontsize=11)
                fig.text(.04, .10, "n = retrieval-eligible questions in the cohort. Application cohorts overlap. N/A = no qualified measurement.", fontsize=10, color="#45535e")
                fig.text(.04, .065, "Development retrieval only: no generated-answer Overall score, public leaderboard rank or tested application router.", fontsize=10, color="#45535e")
                destination.mkdir()
                fig.savefig(destination / "applications.png", dpi=160, metadata={"Software": "Matplotlib", "Description": comparison})
                fig.savefig(destination / "applications.svg", metadata={"Date": None, "Description": comparison})
            finally:
                plt.close(fig)
        data["renderer_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        data["comparison_validator_sha256"] = hashlib.sha256((ROOT / "evaluations/refresh_enterprise_current_views.py").read_bytes()).hexdigest()
        data["matplotlib_version"] = matplotlib.__version__
        data["artifact_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir()}
        with (destination / "matrix.json").open("x", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False); stream.write("\n")
        return destination
    finally:
        if previous_cache is None:
            os.environ.pop("MPLCONFIGDIR", None)
        else:
            os.environ["MPLCONFIGDIR"] = previous_cache


def main(argv: list[str] | None = None) -> int:
    """Render a chosen published comparison; never choose or evaluate candidates."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("comparison", "comparison-sha256", "inventory", "inventory-sha256", "output"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    result = render_heatmap(ROOT, args.comparison, args.comparison_sha256, args.inventory, args.inventory_sha256, args.output)
    print(json.dumps({"status": "rendered", "output": result.relative_to(ROOT).as_posix(), "new_native_jobs": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
