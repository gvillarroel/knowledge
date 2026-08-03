from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "evaluations"
    / "semantic-okf-tika-mallet"
    / "scripts"
    / "prepare_canonical_input.py"
)
SPEC = importlib.util.spec_from_file_location("prepare_tika_mallet_input", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    entries = sorted(
        (
            path.relative_to(root).as_posix().encode("utf-8"),
            path.relative_to(root).as_posix(),
            path,
        )
        for path in root.rglob("*")
        if path.is_file() and path.name != "input-manifest.json"
    )
    for _sort_key, relative, path in entries:
        digest.update(relative.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def test_prepare_binds_candidate_family_and_registry_tree_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = tmp_path / "source-root"
    source = source_root / "sources" / "paper.md"
    source.parent.mkdir(parents=True)
    source.write_text("Grounded paper.\n", encoding="utf-8")
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps(
            {
                "schema_version": "semantic-okf-tika-mallet-canonical-input/1.0",
                "dataset_id": "graphrag-papers-40",
                "source_root": "source-root",
                "files": [
                    {
                        "path": "sources/paper.md",
                        "bytes": source.stat().st_size,
                        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    ingestion = tmp_path / "ingestion.json"
    retrieval = tmp_path / "retrieval.json"
    ingestion.write_text('{"ingestion":true}\n', encoding="utf-8")
    retrieval.write_text('{"retrieval":true}\n', encoding="utf-8")
    monkeypatch.setattr(MODULE, "REPO", tmp_path)
    output = tmp_path / "prepared"

    receipt = MODULE.prepare(
        output,
        check=False,
        inventory=inventory,
        ingestion_plan=ingestion,
        retrieval_plan=retrieval,
        family="tika-mallet-tantivy",
    )

    assert receipt["family"] == "tika-mallet-tantivy"
    assert receipt["payload_tree_sha256"] == _tree_digest(output)
    assert MODULE.prepare(
        output,
        check=True,
        inventory=inventory,
        ingestion_plan=ingestion,
        retrieval_plan=retrieval,
        family="tika-mallet-tantivy",
    )["check"] is True


@pytest.mark.parametrize("family", ["", "Tika-Mallet", " tika-mallet", "tika_mallet"])
def test_prepare_rejects_noncanonical_family(tmp_path: Path, family: str) -> None:
    with pytest.raises(MODULE.PreparationError, match="lowercase kebab-case"):
        MODULE.prepare(tmp_path / "prepared", check=False, family=family)
