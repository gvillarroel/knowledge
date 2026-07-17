---
type: Agent Skill
title: Open Knowledge Format
description: Use when Codex needs to validate, generate, repair, convert, or explain
  Google Cloud Open Knowledge Format (OKF) v0.1 bundles, including Markdown knowledge
  libraries, project documentation, Codex or agent skills that need a separate OKF
  projection, YAML frontmatter, reserved index.md/log.md files, citations, cross-links,
  or generated Markdown exports.
tags:
- codex
- skill
skill_name: open-knowledge-format
source_path: skills/open-knowledge-format/SKILL.md
---

# Open Knowledge Format

## Overview

Use this skill to produce or audit Google Cloud Open Knowledge Format (OKF) v0.1 bundles: directory trees of Markdown concept documents with YAML frontmatter.

## Standalone boundary

The scripts require Python 3.11 or newer. After copying this skill directory, run all commands from the copied skill root and install its local dependency lock in an isolated environment:

```bash
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on POSIX shells or `.venv\Scripts\Activate.ps1` in PowerShell, then install the pinned dependencies:

```bash
python -m pip install -r scripts/requirements.txt
```

Do not rely on a repository-level environment, lock file, or sibling skill.

## Workflow

1. Read `references/okf-v0.1.md` when exact format rules matter or when converting an existing bundle.
2. Identify the bundle root. Treat every non-reserved `.md` file below it as a concept document.
3. Ensure every concept document starts with parseable YAML frontmatter and has a non-empty `type` field.
4. Preserve producer-specific fields; OKF consumers should tolerate unknown keys.
5. Add recommended fields when they can be derived without guessing: `title`, `description`, `resource`, `tags`, and `timestamp`.
6. Keep `index.md` and `log.md` reserved. Do not use those filenames for concepts.
7. Validate with `scripts/validate_okf_bundle.py <bundle-root>` before declaring the bundle compatible.

## Project And Skill Projection

Do not add a top-level OKF `type` to a native Codex `SKILL.md`. Its frontmatter is a separate discovery contract and should contain only `name` and `description`.

For a project with project-local skills, generate a strict OKF subdirectory instead. Run these commands from this skill's root:

```bash
python scripts/build_project_okf_bundle.py <project-root> --output <project-root>/okf
python scripts/build_project_okf_bundle.py <project-root> --output <project-root>/okf --check
```

The builder projects `README.md`, `SPEC.md` when present, and every `skills/*/SKILL.md` into ordinary OKF concept documents. It also creates reserved indexes and runs the validator bundled in this directory. Keep the generated bundle committed when the project treats it as an interoperability artifact.

## Producer Metadata

Choose short concept types that describe the source artifact without inventing a central taxonomy. Preserve existing producer-specific provenance fields because OKF permits unknown metadata keys.

## Validation

Run:

```bash
python scripts/validate_okf_bundle.py <bundle-root>
```

Treat validation failures as actionable:

- Missing or invalid concept frontmatter: add a YAML block at the top.
- Missing `type`: choose a short, descriptive concept type. Do not invent a central taxonomy.
- `index.md` with non-root frontmatter: remove it or rename the file if it is actually a concept.
- `log.md` date headings not in `YYYY-MM-DD`: normalize the heading.
- Native `SKILL.md` with extra compatibility keys: restore its native frontmatter and project it with `build_project_okf_bundle.py`.

## Sources

Primary references:

- Google Cloud blog: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- GoogleCloudPlatform knowledge-catalog OKF spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
