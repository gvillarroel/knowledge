from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from urllib.parse import unquote, urlsplit

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper"
BUILDER_PATH = EVALUATION_ROOT / "scripts" / "build_okf_graphify.py"
PAPERS_PATH = EVALUATION_ROOT / "papers.json"
MARKDOWN_DIR = EVALUATION_ROOT / "sources" / "markdown"
CLAIMS_DIR = EVALUATION_ROOT / "sources" / "claims"
VOCABULARY_PATH = EVALUATION_ROOT / "sources" / "semantic" / "analysis-vocabulary.jsonl"


def load_builder() -> ModuleType:
    """Load the standalone evaluation builder without packaging it."""

    spec = importlib.util.spec_from_file_location("graphrag_okf_graphify_builder", BUILDER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def split_document(path: Path) -> tuple[dict[str, Any], str]:
    """Parse one generated or source Markdown document."""

    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    frontmatter = yaml.safe_load(text[4:end])
    assert isinstance(frontmatter, dict)
    body = text[end + len("\n---\n") :]
    if body.startswith("\n"):
        body = body[1:]
    return frontmatter, body


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load every non-empty JSON object from a JSON Lines file."""

    values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert all(isinstance(value, dict) for value in values)
    return values


def tree_bytes(root: Path) -> dict[str, bytes]:
    """Return a stable relative-path snapshot of every generated file."""

    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def logical_sha256(data: bytes) -> str:
    """Hash bytes after the benchmark's cross-platform line-ending normalization."""

    normalized = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def markdown_tree_digest(root: Path) -> str:
    """Recompute the manifest's non-self-referential Markdown tree digest."""

    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": logical_sha256(path.read_bytes()),
        }
        for path in sorted(root.rglob("*.md"))
    ]
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@pytest.fixture(scope="module")
def built_bundle(tmp_path_factory: pytest.TempPathFactory) -> tuple[ModuleType, Path, dict[str, Any]]:
    """Build the real pinned corpus once for structural tests."""

    builder = load_builder()
    output = tmp_path_factory.mktemp("okf-graphify") / "knowledge"
    manifest = builder.build_bundle(output)
    return builder, output, manifest


def test_builder_materializes_complete_okf_graph(
    built_bundle: tuple[ModuleType, Path, dict[str, Any]],
) -> None:
    builder, output, manifest = built_bundle
    catalog = json.loads(PAPERS_PATH.read_text(encoding="utf-8"))
    claims = [record for path in sorted(CLAIMS_DIR.glob("*.jsonl")) for record in load_jsonl(path)]
    terms = load_jsonl(VOCABULARY_PATH)
    dimensions = [record for record in terms if record["term_kind"] == "analysis-dimension"]
    methods = [record for record in terms if record["term_kind"] == "paper-specific-method"]

    expected_counts = {
        "papers": len(catalog["papers"]),
        "claims": len(claims),
        "dimensions": len(dimensions),
        "methods": len(methods),
    }
    assert expected_counts == {"papers": 15, "claims": 831, "dimensions": 13, "methods": 15}
    assert {key: manifest["counts"][key] for key in expected_counts} == expected_counts
    assert manifest["counts"]["concepts"] == sum(expected_counts.values()) == 874
    assert manifest["counts"]["markdown_files"] == 875
    assert len(list(output.rglob("*.md"))) == 875
    assert not (output / "graphify-out").exists()

    expected_types = {
        "papers": "Paper",
        "claims": "PaperSemanticClaim",
        "dimensions": "AnalysisDimension",
        "methods": "PaperSpecificMethod",
    }
    for path in output.rglob("*.md"):
        frontmatter, _ = split_document(path)
        relative = path.relative_to(output)
        if relative.as_posix() == "index.md":
            assert frontmatter["okf_version"] == "0.1"
            continue
        assert frontmatter["type"] == expected_types[relative.parts[0]]
        assert isinstance(frontmatter["resource"], str) and frontmatter["resource"]
        assert frontmatter["tags"]

    paper_id = "2402.07630v3"
    source_frontmatter, source_body = split_document(MARKDOWN_DIR / f"{paper_id}.md")
    paper_frontmatter, paper_body = split_document(output / "papers" / f"{paper_id}.md")
    assert paper_frontmatter["source_frontmatter"] == source_frontmatter
    assert paper_frontmatter["source_path"] == f"sources/markdown/{paper_id}.md"
    assert paper_frontmatter["source_sha256"] == hashlib.sha256(
        (MARKDOWN_DIR / f"{paper_id}.md").read_bytes()
    ).hexdigest()
    assert paper_body.startswith(source_body)
    assert paper_body.count("## PDF page ") == source_body.count("## PDF page ") == 23

    claim = load_jsonl(CLAIMS_DIR / f"{paper_id}.jsonl")[0]
    dimension_id = unquote(urlsplit(claim["object_term_iri"]).path.rsplit("/", 1)[-1])
    method_id = unquote(urlsplit(claim["subject_term_iri"]).path.rsplit("/", 1)[-1])
    claim_path = output / "claims" / paper_id / f"{claim['id']}.md"
    claim_frontmatter, claim_body = split_document(claim_path)
    assert claim["interpretation"] in claim_body.splitlines()[0]
    assert claim_frontmatter["source_record"] == claim
    assert f"](../../papers/{paper_id}.md)" in claim_body
    assert f"](../../dimensions/{dimension_id}.md)" in claim_body
    assert f"](../../methods/{method_id}.md)" in claim_body
    assert f"../../papers/{paper_id}.md#PDF-page-4" in claim_body
    assert builder.validate_artifacts(
        {
            path.relative_to(output).as_posix(): path.read_bytes()
            for path in output.rglob("*.md")
        }
    )["status"] == "pass"


def test_generated_links_are_local_complete_and_non_orphaned(
    built_bundle: tuple[ModuleType, Path, dict[str, Any]],
) -> None:
    builder, output, _ = built_bundle
    artifacts = {
        path.relative_to(output).as_posix(): path.read_bytes() for path in output.rglob("*.md")
    }
    validation = builder.validate_artifacts(artifacts)
    assert validation["broken_local_links"] == 0
    assert validation["orphans"] == 0
    assert validation["concepts_reachable_from_index"] == len(artifacts) - 1
    assert validation["local_links"] > len(artifacts)

    index_text = (output / "index.md").read_text(encoding="utf-8")
    for paper_path in sorted((output / "papers").glob("*.md")):
        assert f"papers/{paper_path.name}" in index_text


def test_manifest_pins_inputs_graphify_and_bundle_digest(
    built_bundle: tuple[ModuleType, Path, dict[str, Any]],
) -> None:
    _, output, returned_manifest = built_bundle
    manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
    assert manifest == returned_manifest
    assert manifest["builder"] == {
        "deterministic": True,
        "name": "graphrag-okf-graphify",
        "semantic_llm": False,
        "version": "1.0",
    }
    assert manifest["graphify"]["package"] == "graphifyy"
    assert manifest["graphify"]["version"] == "0.9.17"
    assert manifest["graphify"]["requirement"] == "graphifyy==0.9.17"
    assert manifest["graphify"]["builder_invoked"] is False
    assert manifest["graphify"]["semantic_llm"] is False
    assert manifest["graphify"]["orchestration_command"] == "graphify update . --no-cluster"
    assert manifest["graphify"]["query"] == {
        "depth": 2,
        "token_budget": 1500,
        "traversal": "bfs",
    }
    assert manifest["inputs"]["dataset_source_count"] == 31
    assert manifest["inputs"]["dataset_record_count"] == 874
    assert manifest["inputs"]["dataset_tree_sha256"] == (
        "ab14c14f6471086a320f75350def889ba91f2bbd3b040f81fa4797814ce689ab"
    )
    assert len(manifest["inputs"]["sources"]) == 31
    for entry in manifest["inputs"]["sources"]:
        source_path = EVALUATION_ROOT / entry["path"]
        assert source_path.is_file()
        assert entry["bytes"] == source_path.stat().st_size
        assert entry["sha256"] == hashlib.sha256(source_path.read_bytes()).hexdigest()
        assert entry["logical_sha256"] == logical_sha256(source_path.read_bytes())
    assert manifest["bundle"]["build_manifest_excluded_from_tree_digest"] is True
    assert manifest["bundle"]["file_count"] == 875
    assert manifest["bundle"]["bundle_tree_sha256"] == markdown_tree_digest(output)
    assert manifest["validation"]["input_counts_and_digests"] == "pass"
    assert manifest["validation"]["deterministic_rebuild"] == "pass"


def test_rebuild_is_byte_deterministic_and_check_detects_drift(
    built_bundle: tuple[ModuleType, Path, dict[str, Any]],
    tmp_path: Path,
) -> None:
    builder, first_output, _ = built_bundle
    second_output = tmp_path / "second" / "knowledge"
    builder.build_bundle(second_output)
    assert tree_bytes(first_output) == tree_bytes(second_output)

    checked = subprocess.run(
        [sys.executable, str(BUILDER_PATH), "--output", str(second_output), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)["status"] == "checked"

    drifted_output = tmp_path / "drifted" / "knowledge"
    shutil.copytree(second_output, drifted_output)
    index_path = drifted_output / "index.md"
    index_path.write_text(index_path.read_text(encoding="utf-8") + "\nDrift.\n", encoding="utf-8")
    drifted = subprocess.run(
        [sys.executable, str(BUILDER_PATH), "--output", str(drifted_output), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert drifted.returncode == 2
    assert "drifted" in drifted.stderr


def test_malformed_claim_input_fails_closed(tmp_path: Path) -> None:
    builder = load_builder()
    paper_id = "1234.56789v1"
    pdf_sha256 = "a" * 64
    papers_path = tmp_path / "papers.json"
    markdown_dir = tmp_path / "sources" / "markdown"
    claims_dir = tmp_path / "sources" / "claims"
    vocabulary_path = tmp_path / "sources" / "semantic" / "analysis-vocabulary.jsonl"
    markdown_dir.mkdir(parents=True)
    claims_dir.mkdir(parents=True)
    vocabulary_path.parent.mkdir(parents=True)
    papers_path.write_text(
        json.dumps(
            {
                "collection_id": "malformed-fixture",
                "selection_policy": "One synthetic paper for a negative unit test.",
                "papers": [
                    {
                        "arxiv_id": "1234.56789",
                        "version": "v1",
                        "title": "Fixture Paper",
                        "authors": ["Test Author"],
                        "year": 2026,
                        "abs_url": f"https://arxiv.org/abs/{paper_id}",
                        "pdf_url": f"https://arxiv.org/pdf/{paper_id}",
                        "pdf_sha256": pdf_sha256,
                        "selection_dimension": "Negative input validation",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (markdown_dir / f"{paper_id}.md").write_text(
        "\n".join(
            [
                "---",
                'title: "Fixture Paper"',
                'description: "Negative input validation"',
                'type: "Paper"',
                f'resource: "https://arxiv.org/abs/{paper_id}"',
                'tags: ["fixture"]',
                f'paper_id: "{paper_id}"',
                f'source_url: "https://arxiv.org/abs/{paper_id}"',
                f'pdf_url: "https://arxiv.org/pdf/{paper_id}"',
                f'pdf_sha256: "{pdf_sha256}"',
                "page_count: 1",
                "---",
                "",
                "# Fixture Paper",
                "",
                "## PDF page 1",
                "",
                "Evidence text.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    vocabulary_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "definition": "A test dimension.",
                        "id": "dimension-test",
                        "label": "Test Dimension",
                        "term_kind": "analysis-dimension",
                    },
                    sort_keys=True,
                ),
                json.dumps(
                    {
                        "definition": "A source-scoped test method.",
                        "id": f"method-{paper_id.replace('.', '-')}",
                        "label": "Fixture Method",
                        "term_kind": "paper-specific-method",
                    },
                    sort_keys=True,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    malformed_claim = {
        "claim_kind": "test",
        "claim_origin": "negative-test",
        "confidence": "high",
        "evidence_locator": f"sources/markdown/{paper_id}.md#PDF-page-1",
        "id": f"claim-{paper_id.replace('.', '-')}-001",
        # The required interpretation field is intentionally absent.
        "object_term_iri": "https://example.org/resource/analysis-vocabulary/dimension-test",
        "paper_iri": "https://example.org/resource/paper-1234-56789v1/source",
        "pdf_sha256": pdf_sha256,
        "review_state": "reviewed",
        "subject_term_iri": (
            "https://example.org/resource/analysis-vocabulary/"
            f"method-{paper_id.replace('.', '-')}"
        ),
        "title": "Malformed fixture claim",
    }
    (claims_dir / f"{paper_id}.jsonl").write_text(
        json.dumps(malformed_claim, sort_keys=True) + "\n", encoding="utf-8"
    )

    with pytest.raises(builder.BuildError, match="interpretation"):
        builder.build_bundle(
            tmp_path / "output",
            papers_path=papers_path,
            markdown_dir=markdown_dir,
            claims_dir=claims_dir,
            vocabulary_path=vocabulary_path,
            enforce_default_pins=False,
        )
