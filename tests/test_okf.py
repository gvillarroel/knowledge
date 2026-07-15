from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

from knowledge.exporter import export_source
from knowledge.okf import apply_okf_frontmatter, split_frontmatter
from knowledge.store import KnowledgeStore


def make_store(tmp_path: Path) -> KnowledgeStore:
    store = KnowledgeStore(tmp_path)
    store.initialize()
    return store


def test_apply_okf_frontmatter_derives_required_and_recommended_fields() -> None:
    source = {
        "key": "research",
        "type": "arxiv",
        "title": "https://arxiv.org/abs/1706.03762",
        "updated_at": "2026-07-05T12:00:00+00:00",
        "config": {"url": "https://arxiv.org/abs/1706.03762"},
    }

    payload = apply_okf_frontmatter(
        {"categories": ["cs.CL"]},
        source=source,
        body="# Paper\n\nTransformer paper summary.",
    )

    assert payload["type"] == "arXiv Paper"
    assert payload["title"] == "https://arxiv.org/abs/1706.03762"
    assert payload["description"] == "Transformer paper summary."
    assert payload["resource"] == "https://arxiv.org/abs/1706.03762"
    assert payload["timestamp"] == "2026-07-05T12:00:00+00:00"
    assert payload["tags"] == ["cs.cl", "arxiv", "research"]


def test_apply_okf_frontmatter_repairs_invalid_type_and_accepts_urn_resource() -> None:
    payload = apply_okf_frontmatter(
        {"type": 7, "resource": "urn:codex:skill:know"},
        source={"type": "television"},
    )

    assert payload["type"] == "Television Channel"
    assert payload["resource"] == "urn:codex:skill:know"


def test_split_frontmatter_accepts_bom_and_crlf() -> None:
    frontmatter, body, has_frontmatter = split_frontmatter(
        "\ufeff---\r\ntype: Reference\r\ntitle: Windows\r\n---\r\n\r\n# Body\r\n"
    )

    assert has_frontmatter is True
    assert frontmatter == {"type": "Reference", "title": "Windows"}
    assert body == "# Body\r\n"


def test_exported_raw_markdown_is_okf_conformant(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("sample")
    source = store.add_collection_source(
        "sample",
        "arxiv",
        title="https://arxiv.org/abs/1706.03762",
        config={"url": "https://arxiv.org/abs/1706.03762"},
        update_command="sync",
        delete_command="del",
    )
    raw_file = store.source_raw_dir(source) / "paper.txt"
    raw_file.write_text("Attention Is All You Need\n", encoding="utf-8")

    export_source(store, source)

    exported = (store.source_library_dir(source) / "paper.md").read_text(encoding="utf-8")
    frontmatter, body, has_frontmatter = split_frontmatter(exported)
    assert has_frontmatter is True
    assert frontmatter["type"] == "arXiv Paper"
    assert frontmatter["resource"] == "https://arxiv.org/abs/1706.03762"
    assert "arxiv" in frontmatter["tags"]
    assert "Attention Is All You Need" in body


def test_export_repairs_existing_final_layout_markdown(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("sites")
    source = store.add_collection_source(
        "sites",
        "site",
        title="https://example.com/docs",
        config={"url": "https://example.com/docs"},
        update_command="sync",
        delete_command="del",
    )
    source_dir = store.source_dir(source)
    pages_dir = source_dir / "pages"
    pages_dir.mkdir(parents=True)
    (source_dir / "source-metadata.yaml").write_text("documents: 1\n", encoding="utf-8")
    page = pages_dir / "example.com_docs.md"
    page.write_text("---\ntitle: Example Docs\n---\n\n# Example Docs\n\nA short guide.\n", encoding="utf-8")

    export_source(store, source)

    frontmatter = yaml.safe_load(page.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["type"] == "Web Page"
    assert frontmatter["description"] == "A short guide."
    assert frontmatter["resource"] == "https://example.com/docs"


def test_export_repairs_legacy_raw_and_library_markdown(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("legacy")
    source = store.add_collection_source(
        "legacy",
        "video",
        source_id="video-legacy",
        title="Legacy Video",
        config={"url": "https://example.com/watch?v=legacy"},
        update_command="sync",
        delete_command="del",
    )
    legacy_raw = tmp_path / "legacy" / "raw" / "video" / "video-legacy"
    legacy_library = tmp_path / "legacy" / "library" / "video" / "video-legacy"
    legacy_raw.mkdir(parents=True)
    legacy_library.mkdir(parents=True)
    (legacy_raw / "transcript.md").write_text("# Transcript\n\nRaw transcript.\n", encoding="utf-8")
    (legacy_library / "transcript.md").write_text(
        "---\n"
        "title: Legacy transcript\n"
        "---\n\n"
        "# Transcript\n\nRendered transcript.\n",
        encoding="utf-8",
    )

    result = export_source(store, source)

    assert result["legacy_markdown_files"] == 2
    for path in (legacy_raw / "transcript.md", legacy_library / "transcript.md"):
        frontmatter = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        assert frontmatter["type"] == "Video Transcript"
        assert frontmatter["resource"] == "https://example.com/watch?v=legacy"


def test_export_avoids_reserved_index_name_for_generated_concepts(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("repos")
    source = store.add_collection_source(
        "repos",
        "github",
        source_id="github-docs",
        title="https://github.com/example/docs.git",
        config={"repo_url": "https://github.com/example/docs.git"},
        update_command="sync",
        delete_command="del",
    )
    raw_index = store.source_raw_dir(source) / "main" / "docs" / "index.md"
    raw_index.parent.mkdir(parents=True)
    raw_index.write_text("# Docs\n\nRepository docs index.\n", encoding="utf-8")

    export_source(store, source)

    generated = store.source_library_dir(source) / "main" / "docs" / "index.document.md"
    assert generated.exists()
    frontmatter = yaml.safe_load(generated.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["type"] == "Repository File"
    assert not raw_index.read_text(encoding="utf-8").startswith("---")


def test_export_strips_legacy_reserved_index_frontmatter(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.create_collection_key("legacy")
    source = store.add_collection_source(
        "legacy",
        "github",
        source_id="github-legacy",
        title="https://github.com/example/legacy.git",
        config={"repo_url": "https://github.com/example/legacy.git"},
        update_command="sync",
        delete_command="del",
    )
    legacy_index = tmp_path / "legacy" / "library" / "github" / "github-legacy" / "docs" / "index.md"
    legacy_index.parent.mkdir(parents=True)
    legacy_index.write_text("---\ntitle: Legacy index\n---\n\n# Legacy index\n", encoding="utf-8")

    result = export_source(store, source)

    assert result["legacy_markdown_files"] == 1
    assert legacy_index.read_text(encoding="utf-8") == "# Legacy index\n"


def test_open_knowledge_format_skill_validator_accepts_valid_bundle(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "index.md").write_text("# Bundle\n\n* [Concept](concept.md) - summary\n", encoding="utf-8")
    (bundle / "concept.md").write_text(
        "---\n"
        "type: Reference\n"
        "title: Concept\n"
        "---\n\n"
        "# Concept\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "skills/open-knowledge-format/scripts/validate_okf_bundle.py",
            str(bundle),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "OKF validation passed" in result.stdout


def test_repository_skills_keep_native_frontmatter_and_have_okf_projections() -> None:
    skills_dir = Path(__file__).resolve().parents[1] / "skills"
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    assert skill_files

    for skill_file in skill_files:
        assert (skill_file.parent / "agents" / "openai.yaml").is_file(), skill_file
        text = skill_file.read_text(encoding="utf-8")
        raw_frontmatter = text.split("---", 2)[1]
        frontmatter = yaml.safe_load(raw_frontmatter)
        assert set(frontmatter) == {"name", "description"}, skill_file

        projection = skills_dir.parent / "okf" / "skills" / f"{skill_file.parent.name}.md"
        assert projection.is_file(), projection
        projected_frontmatter = yaml.safe_load(projection.read_text(encoding="utf-8").split("---", 2)[1])
        assert projected_frontmatter["type"] == "Agent Skill"
        assert projected_frontmatter["skill_name"] == frontmatter["name"]
        assert projected_frontmatter["source_path"] == f"skills/{skill_file.parent.name}/SKILL.md"


def test_projected_skill_reference_links_resolve_to_package_files() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    projection_root = repo_root / "okf" / "skills"
    link_pattern = re.compile(r"\]\((?!https?://|#|/)([^)\s]+)\)")
    checked = 0

    for projection in sorted(projection_root.glob("*.md")):
        for target in link_pattern.findall(projection.read_text(encoding="utf-8")):
            if target.endswith(".md") and target != projection.name:
                assert (projection.parent / target).resolve().is_file(), (
                    projection,
                    target,
                )
                checked += 1

    assert checked >= 50


def test_project_okf_bundle_is_current_and_conformant() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    builder = repo_root / "skills" / "open-knowledge-format" / "scripts" / "build_project_okf_bundle.py"
    validator = repo_root / "skills" / "open-knowledge-format" / "scripts" / "validate_okf_bundle.py"

    check = subprocess.run(
        [sys.executable, str(builder), str(repo_root), "--output", str(repo_root / "okf"), "--check"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, check.stderr

    validation = subprocess.run(
        [sys.executable, str(validator), str(repo_root / "okf")],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validation.returncode == 0, validation.stderr


def test_okf_validator_accepts_crlf_and_root_version_frontmatter(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    validator = repo_root / "skills" / "open-knowledge-format" / "scripts" / "validate_okf_bundle.py"
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "index.md").write_bytes(
        b"---\r\nokf_version: '0.1'\r\n---\r\n\r\n# Concepts\r\n\r\n* [Example](example.md) - Example.\r\n"
    )
    (bundle / "example.md").write_bytes(b"---\r\ntype: Reference\r\n---\r\n\r\n# Example\r\n")

    result = subprocess.run(
        [sys.executable, str(validator), str(bundle)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_okf_validator_rejects_invalid_concepts_and_reserved_files(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    validator = repo_root / "skills" / "open-knowledge-format" / "scripts" / "validate_okf_bundle.py"
    bundle = tmp_path / "bundle"
    nested = bundle / "nested"
    nested.mkdir(parents=True)
    (bundle / "concept.md").write_text("---\ntitle: Missing type\n---\n\nBody.\n", encoding="utf-8")
    (nested / "index.md").write_text("---\nokf_version: '0.1'\n---\n\n# Concepts\n", encoding="utf-8")
    (bundle / "log.md").write_text(
        "# Updates\n\n## 2026-07-08\n* **Update**: New.\n\n## 2026-07-09\n* **Update**: Out of order.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(validator), str(bundle)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "non-empty top-level 'type'" in result.stderr
    assert "only the bundle-root index.md" in result.stderr
    assert "newest first" in result.stderr
