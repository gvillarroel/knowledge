from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIREMENT_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")
IMPORT_TO_DISTRIBUTION = {
    "PIL": "Pillow",
    "pyparsing": "pyparsing",
    "pyshacl": "pyshacl",
    "rdflib": "rdflib",
    "requests": "requests",
    "yaml": "pyyaml",
}


def skill_roots() -> list[Path]:
    """Return every first-party standalone skill package."""

    return sorted(path.parent for path in SKILLS_ROOT.glob("*/SKILL.md"))


def frontmatter(path: Path) -> dict[str, object]:
    """Parse the first YAML frontmatter block in a Markdown file."""

    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    raw = text.split("---", 2)[1]
    payload = yaml.safe_load(raw)
    assert isinstance(payload, dict), path
    return payload


@pytest.mark.parametrize("skill_root", skill_roots(), ids=lambda path: path.name)
def test_skill_package_declares_a_standalone_boundary(skill_root: Path) -> None:
    skill_path = skill_root / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8")
    metadata = frontmatter(skill_path)
    interface_path = skill_root / "agents" / "openai.yaml"

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == skill_root.name
    assert isinstance(metadata["description"], str) and metadata["description"].strip()
    assert "## Standalone boundary" in skill
    assert interface_path.is_file()

    interface = yaml.safe_load(interface_path.read_text(encoding="utf-8"))["interface"]
    assert interface["display_name"].strip()
    assert interface["short_description"].strip()
    assert f"${skill_root.name}" in interface["default_prompt"]


@pytest.mark.parametrize("skill_root", skill_roots(), ids=lambda path: path.name)
def test_skill_markdown_links_are_package_local_or_external(skill_root: Path) -> None:
    violations: list[str] = []
    resolved_root = skill_root.resolve()

    for markdown in sorted(skill_root.rglob("*.md")):
        for raw_target in MARKDOWN_LINK_RE.findall(markdown.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>").split(maxsplit=1)[0]
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            relative = unquote(parsed.path)
            candidate = (markdown.parent / relative).resolve()
            try:
                candidate.relative_to(resolved_root)
            except ValueError:
                violations.append(f"{markdown.relative_to(skill_root)} escapes to {target}")
                continue
            if not candidate.exists():
                violations.append(f"{markdown.relative_to(skill_root)} misses {target}")

    assert violations == []


def test_skill_instructions_do_not_require_this_checkout() -> None:
    forbidden = {
        "in this repository",
        "repository-approved",
        "repository-native",
        "src/knowledge/",
        "docs/cli.md",
        "python skills/",
    }
    violations: list[str] = []

    for skill_root in skill_roots():
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8").lower()
        matches = sorted(token for token in forbidden if token in skill)
        if matches:
            violations.append(f"{skill_root.name}: {matches}")

    assert violations == []


@pytest.mark.parametrize(
    ("skill_name", "preflight"),
    [
        ("brave-search-effective", "bx --help"),
        ("know", "know --help"),
        ("television", "tv --help"),
    ],
)
def test_instruction_only_tool_skills_declare_an_external_preflight(
    skill_name: str,
    preflight: str,
) -> None:
    skill = (SKILLS_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")

    assert preflight in skill


@pytest.mark.parametrize("skill_root", skill_roots(), ids=lambda path: path.name)
def test_python_dependencies_are_declared_inside_each_skill(skill_root: Path) -> None:
    scripts = skill_root / "scripts"
    if not scripts.is_dir():
        return

    local_modules = {path.stem for path in scripts.glob("*.py")}
    imports: set[str] = set()
    for script in scripts.glob("*.py"):
        tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])

    third_party = imports - set(sys.stdlib_module_names) - local_modules - {"__future__"}
    if not third_party:
        return

    requirements_path = scripts / "requirements.txt"
    assert requirements_path.is_file(), f"{skill_root.name} imports {sorted(third_party)}"
    declared = {
        match.group(1).lower().replace("_", "-")
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if (match := REQUIREMENT_NAME_RE.match(line.strip())) and not line.lstrip().startswith("#")
    }
    expected = {
        IMPORT_TO_DISTRIBUTION.get(module, module).lower().replace("_", "-")
        for module in third_party
    }
    assert expected <= declared, f"{skill_root.name} does not declare {sorted(expected - declared)}"


@pytest.mark.parametrize("skill_root", skill_roots(), ids=lambda path: path.name)
def test_public_scripts_start_from_a_copied_skill(skill_root: Path, tmp_path: Path) -> None:
    copied = tmp_path / skill_root.name
    shutil.copytree(
        skill_root,
        copied,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".venv"),
    )
    entrypoints = sorted(
        path for path in (copied / "scripts").glob("*.py") if not path.name.startswith("_")
    ) if (copied / "scripts").is_dir() else []

    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for entrypoint in entrypoints:
        completed = subprocess.run(
            [sys.executable, str(entrypoint), "--help"],
            cwd=copied,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
            env=env,
        )
        assert completed.returncode == 0, (
            f"{skill_root.name}/{entrypoint.name} failed from copied package:\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
