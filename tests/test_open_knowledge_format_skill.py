from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "open-knowledge-format"


def test_standalone_skill_declares_pinned_dependencies_and_portable_commands() -> None:
    """The copied skill must not inherit setup or command paths from this repository."""

    direct_requirements = (SKILL_ROOT / "scripts" / "requirements.in").read_text(
        encoding="utf-8"
    )
    locked_requirements = (SKILL_ROOT / "scripts" / "requirements.txt").read_text(
        encoding="utf-8"
    )
    instructions = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert direct_requirements.splitlines() == ["PyYAML==6.0.3"]
    assert "PyYAML==6.0.3" in locked_requirements.splitlines()
    assert "## Standalone boundary" in instructions
    assert "Python 3.11 or newer" in instructions
    assert "python -m venv .venv" in instructions
    assert "python -m pip install -r scripts/requirements.txt" in instructions
    assert "python scripts/validate_okf_bundle.py <bundle-root>" in instructions
    assert "python skills/open-knowledge-format/" not in instructions


def test_copied_skill_builds_and_validates_a_generic_project(tmp_path: Path) -> None:
    """All supported scripts must run after only the skill directory is copied."""

    standalone = tmp_path / "standalone" / "open-knowledge-format"
    shutil.copytree(
        SKILL_ROOT,
        standalone,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    project = tmp_path / "generic-project"
    project.mkdir()
    (project / "README.md").write_text(
        "# Nebula Toolkit\n\nA generic toolkit for processing observations.\n",
        encoding="utf-8",
    )
    (project / "SPEC.md").write_text(
        "# Requirements\n\nThe toolkit must process observations deterministically.\n",
        encoding="utf-8",
    )
    (project / "pyproject.toml").write_text(
        '[project]\nname = "nebula-tools"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )
    skill_dir = project / "skills" / "observe-nebulae"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: observe-nebulae\n"
        "description: Analyze a local collection of nebula observations.\n"
        "---\n\n"
        "# Observe Nebulae\n\nUse local observation files as evidence.\n",
        encoding="utf-8",
    )

    runner = tmp_path / "unrelated-working-directory"
    runner.mkdir()
    output = project / "okf"
    builder = standalone / "scripts" / "build_project_okf_bundle.py"
    validator = standalone / "scripts" / "validate_okf_bundle.py"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = ""

    build = subprocess.run(
        [sys.executable, str(builder), str(project), "--output", str(output)],
        cwd=runner,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert build.returncode == 0, build.stderr

    check = subprocess.run(
        [sys.executable, str(builder), str(project), "--output", str(output), "--check"],
        cwd=runner,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, check.stderr

    validation = subprocess.run(
        [sys.executable, str(validator), str(output)],
        cwd=runner,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validation.returncode == 0, validation.stderr

    project_frontmatter = yaml.safe_load(
        (output / "project.md").read_text(encoding="utf-8").split("---", 2)[1]
    )
    specification_frontmatter = yaml.safe_load(
        (output / "specification.md").read_text(encoding="utf-8").split("---", 2)[1]
    )
    skill_frontmatter = yaml.safe_load(
        (output / "skills" / "observe-nebulae.md")
        .read_text(encoding="utf-8")
        .split("---", 2)[1]
    )

    assert project_frontmatter == {
        "type": "Software Project",
        "title": "Nebula Toolkit",
        "description": "Project documentation for nebula-tools.",
        "tags": ["project", "okf"],
        "source_path": "README.md",
    }
    assert specification_frontmatter["description"] == (
        "Requirements and architecture for Nebula Toolkit."
    )
    assert specification_frontmatter["tags"] == ["requirements", "okf"]
    assert skill_frontmatter["skill_name"] == "observe-nebulae"
    assert skill_frontmatter["source_path"] == "skills/observe-nebulae/SKILL.md"

    generated_text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(output.rglob("*.md"))
    ).lower()
    assert "knowledge cli" not in generated_text
