---
name: open-knowledge-format
description: Use when Codex needs to validate, generate, repair, or explain Google Cloud Open Knowledge Format (OKF) bundles, especially Markdown knowledge libraries with YAML frontmatter, concept documents, index.md/log.md reserved files, citations, cross-links, or `know` CLI exports that should interoperate with OKF v0.1.
metadata:
  okf:
    type: Skill
    okf_version: "0.1"
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

## Sources

Primary references:

- Google Cloud blog: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- GoogleCloudPlatform knowledge-catalog OKF spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
