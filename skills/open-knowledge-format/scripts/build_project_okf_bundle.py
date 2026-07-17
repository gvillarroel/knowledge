#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

from validate_okf_bundle import OKF_VERSION, validate_bundle


NATIVE_SKILL_FIELDS = {"name", "description"}


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split native skill frontmatter from its Markdown body."""
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("document must start with YAML frontmatter")
    try:
        end_index = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("document has unterminated YAML frontmatter") from exc
    try:
        payload = yaml.safe_load("\n".join(lines[1:end_index]))
    except yaml.YAMLError as exc:
        raise ValueError(f"document has invalid YAML frontmatter: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("document frontmatter must be a YAML mapping")
    return payload, "\n".join(lines[end_index + 1 :]).lstrip("\n").rstrip() + "\n"


def render_concept(frontmatter: dict[str, Any], body: str) -> str:
    """Render one OKF concept document."""
    metadata = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).rstrip()
    return f"---\n{metadata}\n---\n\n{body.rstrip()}\n"


def expected_bundle_files(project_root: Path) -> dict[Path, str]:
    """Return the complete deterministic Markdown projection for a project."""
    project_root = project_root.resolve()
    readme_path = project_root / "README.md"
    if not readme_path.is_file():
        raise ValueError(f"project README.md not found: {readme_path}")

    name, description = _project_metadata(project_root)
    readme = readme_path.read_text(encoding="utf-8")
    title = _first_heading(readme) or name
    files: dict[Path, str] = {
        Path("project.md"): render_concept(
            {
                "type": "Software Project",
                "title": title,
                "description": description,
                "tags": ["project", "okf"],
                "source_path": "README.md",
            },
            readme,
        )
    }

    project_entries = [(title, "project.md", description)]
    spec_path = project_root / "SPEC.md"
    if spec_path.is_file():
        spec_body = spec_path.read_text(encoding="utf-8")
        spec_title = f"{title} specification"
        spec_description = f"Requirements and architecture for {title}."
        files[Path("specification.md")] = render_concept(
            {
                "type": "Project Specification",
                "title": spec_title,
                "description": spec_description,
                "tags": ["requirements", "okf"],
                "source_path": "SPEC.md",
            },
            spec_body,
        )
        project_entries.append((spec_title, "specification.md", spec_description))

    skill_entries: list[tuple[str, str, str]] = []
    skills_root = project_root / "skills"
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        frontmatter, body = split_frontmatter(skill_file.read_text(encoding="utf-8"))
        unexpected = set(frontmatter) - NATIVE_SKILL_FIELDS
        if unexpected:
            fields = ", ".join(sorted(str(field) for field in unexpected))
            raise ValueError(f"{skill_file}: unsupported native skill frontmatter fields: {fields}")
        skill_name = frontmatter.get("name")
        skill_description = frontmatter.get("description")
        if not isinstance(skill_name, str) or not skill_name.strip():
            raise ValueError(f"{skill_file}: skill name must be a non-empty string")
        if not isinstance(skill_description, str) or not skill_description.strip():
            raise ValueError(f"{skill_file}: skill description must be a non-empty string")

        display_name = _skill_display_name(skill_file.parent, skill_name)
        relative_source = skill_file.relative_to(project_root).as_posix()
        output_name = f"{skill_file.parent.name}.md"
        files[Path("skills") / output_name] = render_concept(
            {
                "type": "Agent Skill",
                "title": display_name,
                "description": skill_description.strip(),
                "tags": ["codex", "skill"],
                "skill_name": skill_name.strip(),
                "source_path": relative_source,
            },
            body,
        )
        skill_entries.append((display_name, output_name, skill_description.strip()))

    if not skill_entries:
        raise ValueError(f"no skills found below {skills_root}")

    files[Path("skills") / "index.md"] = _index_body("Agent Skills", skill_entries)
    root_body = _index_body("Project", project_entries).rstrip()
    root_body += "\n\n# Subdirectories\n\n"
    root_body += "* [Agent Skills](skills/index.md) - OKF projections of every native project skill.\n"
    files[Path("index.md")] = render_concept({"okf_version": OKF_VERSION}, root_body)
    return files


def write_bundle(project_root: Path, output: Path, *, prune: bool = False) -> list[Path]:
    """Write the deterministic project bundle and return written paths."""
    expected = expected_bundle_files(project_root)
    output = output.resolve()
    if output == project_root.resolve():
        raise ValueError("bundle output must be a dedicated subdirectory, not the project root")
    output.mkdir(parents=True, exist_ok=True)

    unexpected = _unexpected_markdown(output, expected)
    if unexpected and not prune:
        paths = ", ".join(path.as_posix() for path in unexpected)
        raise ValueError(f"bundle contains unexpected Markdown files; rerun with --prune: {paths}")
    for relative_path in unexpected:
        (output / relative_path).unlink()

    written: list[Path] = []
    for relative_path, content in expected.items():
        target = output / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
        written.append(target)
    _remove_empty_directories(output)
    return written


def check_bundle(project_root: Path, output: Path) -> list[str]:
    """Return drift messages for a generated project bundle."""
    expected = expected_bundle_files(project_root)
    output = output.resolve()
    problems: list[str] = []
    for relative_path, content in expected.items():
        target = output / relative_path
        if not target.is_file():
            problems.append(f"missing: {relative_path.as_posix()}")
            continue
        if target.read_text(encoding="utf-8") != content:
            problems.append(f"stale: {relative_path.as_posix()}")
    for relative_path in _unexpected_markdown(output, expected):
        problems.append(f"unexpected: {relative_path.as_posix()}")
    if output.is_dir():
        for issue in validate_bundle(output):
            problems.append(f"invalid: {issue.path}: {issue.message}")
    return problems


def _project_metadata(project_root: Path) -> tuple[str, str]:
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        return project_root.name, f"Project documentation for {project_root.name}."
    with pyproject_path.open("rb") as handle:
        payload = tomllib.load(handle)
    project = payload.get("project") if isinstance(payload, dict) else None
    if not isinstance(project, dict):
        return project_root.name, f"Project documentation for {project_root.name}."
    name = str(project.get("name") or project_root.name)
    description = str(project.get("description") or f"Project documentation for {name}.")
    return name, description


def _first_heading(markdown: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else None


def _skill_display_name(skill_dir: Path, skill_name: str) -> str:
    metadata_path = skill_dir / "agents" / "openai.yaml"
    if metadata_path.is_file():
        payload = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
        interface = payload.get("interface") if isinstance(payload, dict) else None
        display_name = interface.get("display_name") if isinstance(interface, dict) else None
        if isinstance(display_name, str) and display_name.strip():
            return display_name.strip()
    return " ".join(part.capitalize() for part in skill_name.split("-"))


def _index_body(heading: str, entries: list[tuple[str, str, str]]) -> str:
    lines = [f"# {heading}", ""]
    for title, link, description in sorted(entries, key=lambda item: item[0].casefold()):
        lines.append(f"* [{title}]({link}) - {description}")
    return "\n".join(lines).rstrip() + "\n"


def _unexpected_markdown(output: Path, expected: dict[Path, str]) -> list[Path]:
    if not output.is_dir():
        return []
    expected_paths = set(expected)
    actual = {path.relative_to(output) for path in output.rglob("*.md") if path.is_file()}
    return sorted(actual - expected_paths)


def _remove_empty_directories(output: Path) -> None:
    for path in sorted((item for item in output.rglob("*") if item.is_dir()), reverse=True):
        if not any(path.iterdir()):
            path.rmdir()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a strict OKF v0.1 projection of a project and its skills.")
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Fail when the generated bundle is missing or stale.")
    parser.add_argument("--prune", action="store_true", help="Remove stale generated Markdown from the output.")
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    output = (args.output or (project_root / "okf")).resolve()
    try:
        if args.check:
            problems = check_bundle(project_root, output)
            if problems:
                for problem in problems:
                    print(problem, file=sys.stderr)
                return 1
            print(f"OKF project bundle is current and valid: {output}")
            return 0

        written = write_bundle(project_root, output, prune=args.prune)
        issues = validate_bundle(output)
        if issues:
            for issue in issues:
                print(f"{issue.path}: {issue.message}", file=sys.stderr)
            return 1
        print(f"Built {len(written)} OKF documents: {output}")
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
