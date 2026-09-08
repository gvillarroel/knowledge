"""Verify aggregate-only report routing, unit conversion, and tie semantics."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("report_catalog_test", ROOT / "evaluations/build_report_catalog.py")
CATALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CATALOG)


@pytest.mark.parametrize(("text", "unit", "expected"), [("**0.429**", "ratio", 42.9), ("92.58%", "percent", 92.58),
                                                        ("1,234.50 ms", "ms", 1234.5), ("N/A", "ratio", None), ("0", "percent", 0)])
def test_metric_units_are_explicit(text, unit, expected):
    result = CATALOG.number(text, unit)
    assert result == pytest.approx(expected) if expected is not None else result is None


@pytest.mark.parametrize("text", ["nan", "inf", "-1", "101"])
def test_invalid_percentages_are_rejected(text):
    with pytest.raises(ValueError):
        CATALOG.number(text, "percent")


def test_table_selection_is_unambiguous():
    text = "| Route | Score |\n|---|---:|\n| x | 25% |\n"
    assert CATALOG.table(text, "Route") == [{"Route": "x", "Score": "25%"}]
    with pytest.raises(ValueError, match="exactly one"):
        CATALOG.table(text + "\n" + text, "Route")
    with pytest.raises(ValueError, match="width"):
        CATALOG.table(text.replace("| x | 25% |", "| x |"), "Route")


def test_leaders_preserve_ties_and_exclude_unavailable_rows():
    rows = [{"route": "a", "status": "measured", "metrics": {"ndcg_at_10": 80}},
            {"route": "b", "status": "measured", "metrics": {"ndcg_at_10": 80}},
            {"route": "c", "status": "unavailable", "metrics": {"ndcg_at_10": 100}}]
    assert [row["route"] for row in CATALOG.leaders({"primary_metric": "ndcg_at_10", "rows": rows})] == ["a", "b"]


def test_fulltext_enterprise_report_is_not_mislabeled_as_title_only():
    specs = json.loads((ROOT / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    old = CATALOG.load_dataset(next(s for s in specs if s["id"] == "enterprise-rag-bench-40-v1"))
    current = {**old, "id": "enterprise-rag-generator-g2-fulltext-40", "label": "Full-text Enterprise replay"}
    rendered = CATALOG.render([old, current])
    assert "**Scope correction:**" in rendered["datasets/enterprise-rag-bench-40-v1.md"]
    assert "titles without mapped" not in rendered["datasets/enterprise-rag-generator-g2-fulltext-40.md"]


def test_full_corpus_classical_does_not_turn_retrieval_into_a_public_answer_rank():
    specs = json.loads((ROOT / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    group = CATALOG.load_dataset(next(s for s in specs if s["id"] == "enterprise-rag-classical-full-500"))
    evidence = json.loads((ROOT / "evaluations/reports/enterprise-classical-full/aggregate.json").read_text(encoding="utf-8"))
    assert group["question_count"] == 500 and len(group["rows"]) == 1
    assert evidence["retrieval"]["documents"] == 511962
    assert evidence["retrieval"]["all_questions"]["questions_with_references"] == 470
    assert evidence["retrieval"]["public_leaderboard_position"] is None
    assert evidence["answer_stage"]["overall"] is None
    assert evidence["answer_stage"]["public_position"] is None
    assert "only measured alternative" in group["scope"]
    assert group["rows"][0]["metrics"]["ndcg_at_10"] == pytest.approx(
        100 * evidence["retrieval"]["all_questions"]["metrics"]["ndcg_at_10"], abs=0.005)


def test_existing_published_winners_and_missing_values_are_preserved():
    specs = json.loads((ROOT / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    datasets = {spec["id"]: CATALOG.load_dataset(spec) for spec in specs if spec["format"] != "enterprise-json"}
    assert CATALOG.leaders(datasets["software-architecture-books-40"])[0]["route"] == "Fusion"
    assert CATALOG.leaders(datasets["data-science-ai-ml-books-40"])[0]["route"] == "Fast"
    assert len(CATALOG.leaders(datasets["astro-40"])) == 2
    endocrine = datasets["endocrine-hygiene"]
    assert len([row for row in endocrine["rows"] if row["status"] == "unavailable"]) == 2
    assert CATALOG.leaders(datasets["tau3-banking-knowledge-97"])[0]["route"] == "Local topic"


def test_aggregate_publication_does_not_copy_arbitrary_source_fields(tmp_path):
    source = {"alternatives": [{"id": "legacy-lexical", "label": "Legacy lexical", "question": "PRIVATE QUESTION",
                                "metrics": {"ndcg_at_10": 10, "recall_at_10": 20, "mrr_at_10": 30,
                                            "representative_p95_ms": 1, "gold_answer": "PRIVATE ANSWER"}}]}
    (tmp_path / "report.json").write_text(json.dumps(source), encoding="utf-8")
    spec = {"id": "fixture", "label": "Fixture", "scope": "public", "question_count": 1, "expected_rows": 1,
            "primary_metric": "ndcg_at_10", "path": "report.json", "format": "comparison-json"}
    normalized = CATALOG.load_dataset(spec, tmp_path)
    assert "PRIVATE" not in json.dumps(normalized)
    spec["expected_rows"] = 2
    with pytest.raises(ValueError, match="row count"):
        CATALOG.load_dataset(spec, tmp_path)


def test_family_prefixes_and_skill_links_are_exact():
    assert CATALOG.family_name("Tika/MALLET/Tantivy fusion") == "tika-mallet-tantivy"
    assert CATALOG.family_name("specialized-expert-trace-early-confidence") == "specialized-expert"
    with pytest.raises(ValueError, match="unknown"):
        CATALOG.family_name("invented")
    assert (ROOT / CATALOG.skill_path("legacy")).exists()


def test_rendered_navigation_and_cta_have_no_broken_local_links():
    specs = json.loads((ROOT / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    groups = [CATALOG.load_dataset(spec) for spec in specs if spec["format"] != "enterprise-json"]
    files = CATALOG.render(groups)
    virtual = {(CATALOG.OUTPUT / path).resolve() for path in files}
    for relative, content in files.items():
        if not relative.endswith(".md"):
            continue
        for target in re.findall(r"\]\(([^)]+)\)", content):
            path = (CATALOG.OUTPUT / relative).parent / target
            assert path.resolve() in virtual or path.exists(), (relative, target)
    assert "Runtime errors" in files["cta/README.md"]
    assert "input plus output" in files["cta/README.md"]


def test_primary_projection_binds_complete_numeric_rows_and_omissions():
    specs = json.loads((ROOT / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    group = CATALOG.load_dataset(next(spec for spec in specs if spec["id"] == "endocrine-hygiene"))
    contract, lines = CATALOG.comparison_projection(group)
    assert len(contract["alternatives"]) == 4
    assert lines[2].startswith("| Pos. | Pair / strategy |")
    assert all(isinstance(value, (int, float)) for row in contract["alternatives"] for value in row["metrics"].values())
    assert "Omitted" in "\n".join(lines)
    assert "entity-graph" in "\n".join(lines)
    assert group["source_sha256"] in contract["dataset_scope"]["metric_contract"]


def test_primary_projection_omits_unmeasured_latency_column():
    specs = json.loads((ROOT / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    group = CATALOG.load_dataset(next(spec for spec in specs if spec["id"] == "tau3-banking-knowledge-97"))
    contract, lines = CATALOG.comparison_projection(group)
    assert "p95_ms" not in {metric["id"] for metric in contract["metrics"]}
    assert "P95 is not available" in "\n".join(lines)


def test_evolution_labels_keep_the_candidate_without_repeating_the_family():
    specs = json.loads((ROOT / "evaluations/report-sources.json").read_text(encoding="utf-8"))["datasets"]
    group = CATALOG.load_dataset(next(spec for spec in specs if spec["id"] == "enterprise-rag-e6-development-40"))
    original = {row["route"]: row["metrics"] for row in group["rows"]}
    contract, lines = CATALOG.comparison_projection(group)
    for row in contract["alternatives"]:
        assert row["label"] in original
        assert row["metrics"] == original[row["label"]]
    rendered = "\n".join(lines + CATALOG.render_table(group["rows"], group["primary_metric"]))
    assert "embeddings / embeddings /" not in rendered
    assert "ensemble / candidate-018 / quality" in rendered
    assert "embeddings / baseline / hybrid" in rendered
