---
adr: "0016"
title: "ADR 0016: Separate md2conf Publishing from Native Confluence Round Trips"
summary: "Use md2conf only for Markdown-authoritative whole-page publication and retain storage XML round trips for Confluence-authoritative preservation."
status: "Accepted"
date: "2026-07-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Confluence Interoperability"
tags:
  - confluence
  - md2conf
  - skills
  - publishing
  - authority
---

# ADR 0016: Separate md2conf Publishing from Native Confluence Round Trips

## Status

Accepted.

## Context

The project already has a Confluence-authoritative round-trip contract for editing existing published pages through storage XML while preserving unknown macros, extensions, attachments, and page metadata. That contract prevents page-tree moves and attachment deletion and requires operation-bound API and authenticated-browser evidence.

The active `hunyadi/md2conf` tool solves a different problem. It converts a Markdown file or directory into Confluence Storage Format and publishes the generated result. Its stable 0.6.1 release can create pages, inject page and space identifiers into Markdown, upload and delete attachments, replace labels and content properties, resolve Markdown mail links into user mentions, and move or reorder child pages. It regenerates the complete body from Markdown and does not preserve native structures that are absent from the source.

The tool's name also has a supply-chain ambiguity: the maintained project is distributed as `markdown-to-confluence`, while an unrelated obsolete PyPI distribution is named `md2conf`. The stable release and the upstream development branch can expose different CLI flags despite sharing a version string in source. A dedicated skill therefore needs explicit package and option preflight rather than copied commands alone.

## Decision

Ship `skills/md2conf/` as a standalone Markdown-authoritative publishing skill.

- Use md2conf only when Markdown owns the complete generated page body and referenced attachment set.
- Treat the external CLI, Confluence service, credentials, optional renderers, Marketplace apps, and Markdown source as explicit public inputs.
- Verify `md2conf --version`, `md2conf --help`, and the `markdown-to-confluence` distribution before using version-sensitive options. Never direct users to install the obsolete `md2conf` PyPI package.
- Convert a disposable source copy with `--local` before publication and inspect generated storage and assets. Treat this as a conversion preview, not a remote dry-run.
- Keep live publication separately authorized. Review the target space, root, explicit page mappings, existing page ownership, attachments, labels, content properties, inline comments, mailto-driven mention candidates, hierarchy, overwrite policy, notification effects, and source-update policy before mutation.
- Expose the stable tool's destructive and non-transactional behavior: it can delete unreferenced attachments, replace label/property sets, edit source mappings, create or reorder pages, and leave partial state after failure.
- Require source-diff and authenticated-browser verification after publication. A successful CLI exit or REST update does not prove that links, attachments, diagrams, or Marketplace macros render correctly.
- Stop with an in-scope source-of-truth diagnostic when a native or manually authored page must remain authoritative. Do not require or invoke another skill from the md2conf package.

Retain ADR 0013 unchanged for Confluence-authoritative page preservation. The two skills may both write Confluence, but their authority models and completion claims are mutually exclusive for a given page operation.

## Consequences

Positive:

- Markdown documentation trees gain a focused, reproducible publication workflow;
- agents can distinguish the maintained package from obsolete namesakes and development-only flags;
- destructive defaults and partial-failure recovery become reviewable before publication;
- native macro-rich pages retain the stronger storage round-trip preservation contract;
- isolated evaluation can measure md2conf guidance without mounting another Confluence skill.

Negative:

- users must choose the authoritative representation before editing an existing page;
- local conversion cannot predict every tenant-specific API or rendering failure;
- browser verification remains necessary after live publication;
- some safety guidance deliberately duplicates a small authority boundary so each skill remains standalone.
