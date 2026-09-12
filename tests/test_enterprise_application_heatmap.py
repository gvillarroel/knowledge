"""Check public chart fidelity, unavailable cells and append-only output."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("enterprise_heatmap", ROOT / "evaluations/render_enterprise_application_heatmap.py")
PLOT = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(PLOT)
COMPARISON = "graphify-generation-009-001"
INVENTORY = "opportunity-accounting-002"


@pytest.fixture
def inputs(tmp_path):
    hashes = []
    for name in (COMPARISON, INVENTORY):
        source = ROOT / PLOT.VIEWS.BASE / name / "aggregate.json"
        target = tmp_path / PLOT.VIEWS.BASE / name / "aggregate.json"
        target.parent.mkdir(parents=True)
        target.write_bytes(source.read_bytes())
        hashes.append(hashlib.sha256(source.read_bytes()).hexdigest())
    return tmp_path, COMPARISON, hashes[0], INVENTORY, hashes[1]


def test_matrix_preserves_real_values_ties_missing_and_counts(inputs):
    matrix = PLOT.comparison_matrix(*inputs)
    assert len(matrix["families"]) == 8 and len(matrix["rows"]) == 10
    drive = next(row for row in matrix["rows"] if row["group"] == "google_drive")
    assert drive["leaders"] == ["graphify"] and drive["retrieval_eligible"] == 14
    assert drive["ndcg_at_10"][5] == 0.8014123416194165
    assert matrix["rows"][0]["leaders"] == ["legacy", "turso"]
    assert all(row["ndcg_at_10"][-2:] == [None, None] for row in matrix["rows"])
    assert matrix["candidate_selection_performed"] is False and matrix["new_native_jobs"] == 0


@pytest.mark.parametrize("change", ["digest", "leader", "count", "score"])
def test_invalid_evidence_is_rejected_before_output(inputs, change):
    root, comparison, digest, inventory, inventory_digest = inputs
    if change == "digest":
        digest = "0" * 64
    else:
        path = root / PLOT.VIEWS.BASE / comparison / "aggregate.json"
        data = json.loads(path.read_text())
        group = next(g for g in data["cross_family_comparison"]["groups"] if g["group"] == "google_drive")
        if change == "leader":
            group["descriptive_ndcg_leaders"] = ["legacy"]
        elif change == "count":
            group["retained_metrics"]["legacy"]["retrieval_eligible"] = 999
        else:
            group["retained_metrics"]["legacy"]["ndcg_at_10"] = True
        path.write_text(json.dumps(data))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        PLOT.render_heatmap(root, comparison, digest, inventory, inventory_digest, "application-heatmap-001")
    assert not (root / PLOT.VIEWS.BASE / "application-heatmap-001").exists()


@pytest.mark.parametrize("output", ["../escape", "graphify-generation-009-001", "/absolute"])
def test_output_cannot_overwrite_or_escape_report_leaves(inputs, output):
    with pytest.raises(ValueError):
        PLOT.render_heatmap(*inputs, output)


def test_render_has_exact_companion_and_cannot_be_repeated(inputs):
    if importlib.util.find_spec("matplotlib") is None:
        pytest.skip("Optional Matplotlib dependency is unavailable")
    output = PLOT.render_heatmap(*inputs, "application-heatmap-001")
    assert {p.name for p in output.iterdir()} == {"applications.png", "applications.svg", "matrix.json"}
    data = json.loads((output / "matrix.json").read_text())
    for name, digest in data["artifact_sha256"].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == digest
    assert (output / "applications.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert "Google Drive" in (output / "applications.svg").read_text()
    with pytest.raises(ValueError, match="absent"):
        PLOT.render_heatmap(*inputs, "application-heatmap-001")
