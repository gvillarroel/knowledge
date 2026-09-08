"""Regression checks retain original document content without a source-skill runtime."""
from __future__ import annotations

import copy
import html
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / "evaluations/enterprise-rag-bench" / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


FULL = module("enterprise_fulltext_test", "fulltext_projection.py")
DATA = module("enterprise_fulltext_v1_test", "dataset_tool.py")


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "original"
    (root / "documents").mkdir(parents=True)
    FULL.write_json(root / "manifest.json", DATA.manifest(["gmail", "slack"], "synthetic"))
    for name in ("gmail", "slack"):
        row = {"id": name + "-1", "title": name + " title", "body": "Decision—approved.\nFull <source> & café.\n",
               "upstream_path": name + "/original.txt", "upstream_sha256": "a" * 64}
        (root / "documents" / (name + ".jsonl")).write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    (root / "LICENSE").write_text("Synthetic fixture.\n", encoding="utf-8")
    return root


def ledger(source, target):
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    originals, _ = FULL.source_documents(source, manifest)
    rows = [{"record_id": identity, "source_id": row["source_id"], "attributes": {"body": row["body"]},
             "body": "Title\n" + html.escape(row["body"], quote=False).replace("\n", " ↵ ").strip()}
            for identity, row in originals.items()]
    target.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
    return rows


def test_projection_is_separate_deterministic_and_copies_only_source_files(source, tmp_path):
    (source / "questions.json").write_text('"PRIVATE ANSWERS"', encoding="utf-8")
    before = FULL.tree_hashes(source)
    output = tmp_path / "fulltext"
    receipt = FULL.prepare(source, output)
    assert receipt == FULL.prepare(source, output, check=True)
    assert FULL.tree_hashes(source) == before
    assert not (output / "input/questions.json").exists()
    assert receipt["document_count"] == 2
    for name in ("gmail", "slack"):
        relative = "documents/" + name + ".jsonl"
        assert (source / relative).read_bytes() == (output / "input" / relative).read_bytes()
    projected = json.loads((output / "input/manifest.json").read_text(encoding="utf-8"))
    assert projected["sources"][0]["fields"]["body"] == "documentText"
    assert "fields" not in DATA.manifest(["gmail"], "synthetic")["sources"][0]


def test_real_canonical_builder_detects_title_only_and_preserves_mapped_unicode(source, tmp_path):
    output = tmp_path / "fulltext"
    FULL.prepare(source, output)
    for incoming, name in ((source, "old"), (output / "input", "complete")):
        knowledge = tmp_path / name
        result = subprocess.run([sys.executable, "-X", "utf8", "-B",
            str(REPO / "skills/build-semantic-okf/scripts/build_semantic_okf.py"),
            str(incoming / "manifest.json"), str(knowledge), "--output-format", "json"],
            capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert result.returncode == 0, result.stdout + result.stderr
        records = knowledge / "semantic/records.jsonl"
        if name == "old":
            with pytest.raises(ValueError, match="lost or changed"):
                FULL.verify(source, records)
        else:
            receipt = FULL.verify(source, records)
            assert receipt["records"] == 2
            assert receipt["original_body_characters"] == receipt["preserved_body_characters"]


def test_projection_does_not_overwrite_and_check_detects_added_files(source, tmp_path):
    output = tmp_path / "fulltext"
    FULL.prepare(source, output)
    with pytest.raises(FileExistsError):
        FULL.prepare(source, output)
    (output / "extra.txt").write_text("unexpected", encoding="utf-8")
    with pytest.raises(ValueError, match="drift"):
        FULL.prepare(source, output, check=True)
    assert not list(tmp_path.glob(".fulltext-*"))


def test_projection_preserves_other_ontology_properties_and_mappings():
    manifest = DATA.manifest(["gmail"], "synthetic")
    extra = {"name": "origin", "kind": "datatype", "domain": "EnterpriseDocument", "range": "xsd:string"}
    manifest["ontology"]["properties"].append(extra)
    manifest["sources"][0]["fields"] = {"upstream_path": "origin"}
    before = copy.deepcopy(manifest)
    changed = FULL.fulltext_manifest(manifest)
    assert manifest == before
    assert changed["ontology"]["properties"] == [extra, FULL.BODY_PROPERTY]
    assert changed["sources"][0]["fields"] == {"upstream_path": "origin", "body": "documentText"}
    assert FULL.fulltext_manifest(changed) == changed


@pytest.mark.parametrize("mutation", ["property", "field", "schema", "source-identity"])
def test_conflicting_manifest_is_rejected(mutation):
    manifest = DATA.manifest(["gmail"], "synthetic")
    if mutation == "property":
        manifest["ontology"]["properties"] = [{**FULL.BODY_PROPERTY, "range": "xsd:integer"}]
    elif mutation == "field":
        manifest["sources"][0]["fields"] = {"body": "otherProperty"}
    elif mutation == "schema":
        manifest["sources"][0]["schema"]["body"] = "integer"
    else:
        manifest["sources"] *= 2
    with pytest.raises(ValueError):
        FULL.fulltext_manifest(manifest)


@pytest.mark.parametrize("mutation", ["title-only", "changed-body", "search-truncation", "missing", "duplicate", "wrong-source"])
def test_fidelity_rejects_semantic_content_loss_and_identity_drift(source, tmp_path, mutation):
    path = tmp_path / "records.jsonl"
    rows = ledger(source, path)
    if mutation == "title-only":
        rows[0]["attributes"] = {}
    elif mutation == "changed-body":
        rows[0]["attributes"]["body"] = "Changed decision."
    elif mutation == "search-truncation":
        rows[0]["body"] = "Title"
    elif mutation == "missing":
        rows.pop()
    elif mutation == "duplicate":
        rows[1] = rows[0]
    else:
        rows[0]["source_id"] = "other"
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    with pytest.raises(ValueError):
        FULL.verify(source, path)


@pytest.mark.parametrize("relative", ["../questions.jsonl", "/documents/a.jsonl", "documents/../../a.jsonl", "documents\\a.jsonl", "C:/documents/a.jsonl"])
def test_only_declared_document_paths_can_enter_projection(source, tmp_path, relative):
    path = source / "manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["sources"][0]["path"] = relative
    FULL.write_json(path, value)
    with pytest.raises(ValueError, match="source path"):
        FULL.prepare(source, tmp_path / "fulltext")
    assert not (tmp_path / "fulltext").exists()


def test_duplicate_original_identities_and_nested_output_are_rejected(source, tmp_path):
    path = source / "documents/gmail.jsonl"
    path.write_bytes(path.read_bytes() * 2)
    with pytest.raises(ValueError, match="Duplicate"):
        FULL.prepare(source, tmp_path / "fulltext")
    with pytest.raises(ValueError, match="disjoint"):
        FULL.prepare(source, source / "new")


def test_cli_verification_reports_failure_without_fabricating_success(source, tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_text("", encoding="utf-8")
    result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(Path(FULL.__file__)),
                             "verify", "--input", str(source), "--records", str(path)],
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "error"
