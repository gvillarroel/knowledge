"""Regression checks for source-relative empty-heading graph identities."""
from __future__ import annotations

import copy
import importlib
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def projection():
    path = Path(__file__).resolve().parents[1] / "skills/build-semantic-okf-graphify/scripts/_graphify_projection.py"
    spec = importlib.util.spec_from_file_location("graphify_heading_regression", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("edge_key", ["edges", "links"])
@pytest.mark.parametrize("absolute_source", [False, True])
def test_empty_heading_is_root_invariant_without_collapsing_links(
    projection, tmp_path, edge_key, absolute_source
):
    documents = [
        ("docs/source.md", "# Visible heading\n\n##  \n\n[Other document](./other.md)\n"),
        ("docs/other.md", "# Other document\n\nLinked source.\n"),
    ]
    results = []
    for name in ("temporary-alpha", "temporary-beta"):
        root = tmp_path / name
        root.mkdir()
        data = projection._extract_virtual_markdown(root, documents)
        data[edge_key] = data.pop("edges")
        if absolute_source:
            for item in [*data["nodes"], *data[edge_key]]:
                if item.get("source_file"):
                    item["source_file"] = str(root / item["source_file"])
        original = copy.deepcopy(data)
        projection._normalize_local_heading_ids(root, data)
        identifiers = {node["id"] for node in data["nodes"]}
        assert len(identifiers) == len(data["nodes"]) == 5
        assert len(data[edge_key]) == 4
        assert sum(edge["relation"] == "references" for edge in data[edge_key]) == 1
        assert all(edge["source"] in identifiers and edge["target"] in identifiers for edge in data[edge_key])
        assert all(edge["source"] != edge["target"] for edge in data[edge_key])
        empty = [node for node in data["nodes"] if node.get("label") == ""]
        assert len(empty) == 1 and empty[0]["id"].startswith("semantic-okf:heading:")
        for before, after in zip(original["nodes"], data["nodes"]):
            assert {key: value for key, value in before.items() if key != "id"} == {
                key: value for key, value in after.items() if key != "id"
            }
        once = copy.deepcopy(data)
        projection._normalize_local_heading_ids(root, data)
        assert data == once
        if absolute_source:
            for item in [*data["nodes"], *data[edge_key]]:
                if item.get("source_file"):
                    item["source_file"] = Path(item["source_file"]).relative_to(root).as_posix()
        results.append(projection._canonical_graph(data))
    assert results[0] == results[1]


def test_heading_normalization_rejects_missing_location_and_collision(projection, tmp_path):
    file_node_id = importlib.import_module("graphify.extract")._file_node_id
    node = {"id": file_node_id(tmp_path / "source.md"), "source_file": "source.md", "label": ""}
    data = {"nodes": [node], "links": []}
    with pytest.raises(projection.GraphifyProjectionError, match="no source location"):
        projection._normalize_local_heading_ids(tmp_path, copy.deepcopy(data))
    node["source_location"] = "L3"
    repaired = copy.deepcopy(data)
    projection._normalize_local_heading_ids(tmp_path, repaired)
    data["nodes"].append({"id": repaired["nodes"][0]["id"], "source_file": "other.md"})
    with pytest.raises(projection.GraphifyProjectionError, match="collides"):
        projection._normalize_local_heading_ids(tmp_path, data)


def test_regular_and_already_relative_identities_are_preserved(projection, tmp_path):
    data = projection._extract_virtual_markdown(tmp_path, [("source.md", "# Regular heading\n\nText.\n")])
    before = copy.deepcopy(data)
    projection._normalize_local_heading_ids(tmp_path, data)
    assert data == before
