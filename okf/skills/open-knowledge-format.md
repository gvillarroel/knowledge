---
type: Agent Skill
title: Open Knowledge Format
description: Use when Codex needs to validate, generate, repair, convert, or explain
  Google Cloud Open Knowledge Format (OKF) v0.1 bundles, including Markdown knowledge
  libraries, project documentation, Codex or agent skills that need a separate OKF
  projection, YAML frontmatter, reserved index.md/log.md files, citations, cross-links,
  or `know` CLI exports.
tags:
- codex
- skill
skill_name: open-knowledge-format
source_path: skills/open-knowledge-format/SKILL.md
---

# Open Knowledge Format

## Overview

Use this skill to produce or audit Google Cloud Open Knowledge Format (OKF) v0.1 bundles: directory trees of Markdown concept documents with YAML frontmatter.

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

For a project with repo-local skills, generate a strict OKF subdirectory instead:

```bash
python scripts/build_project_okf_bundle.py <project-root> --output <project-root>/okf
python scripts/build_project_okf_bundle.py <project-root> --output <project-root>/okf --check
```

The builder projects `README.md`, `SPEC.md` when present, and every `skills/*/SKILL.md` into ordinary OKF concept documents. It also creates reserved indexes and runs the bundled validator. Keep the generated bundle committed when the project treats it as an interoperability artifact.

## `know` CLI Mapping

When working in this repository, prefer these OKF concept types for exported source documents:

- `arxiv` -> `arXiv Paper`
- `site` -> `Web Page`
- `confluence` -> `Confluence Page`
- `jira` -> `Jira Issue`
- `aha` -> `Aha Feature`
- `google_releases` -> `Google Cloud Release Note`
- `video` -> `Video Transcript`
- `github` -> `Repository File`
- `television` -> `Television Channel`

Keep existing provenance fields such as `knowledge_key`, `source_id`, `source_type`, `source_url`, `web_url`, `entry_url`, `paper_id`, and `issue_key`; OKF permits producer-defined fields.

## Validation

Run:

```bash
python skills/open-knowledge-format/scripts/validate_okf_bundle.py <bundle-root>
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
