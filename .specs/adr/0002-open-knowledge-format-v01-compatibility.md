---
adr: "0002"
title: "ADR 0002: Add Open Knowledge Format v0.1 Compatibility"
summary: "Treat OKF v0.1 fields as an additive metadata layer on exported Markdown concepts."
status: "Accepted"
date: "2026-07-05"
product: "knowledge"
owner: "Platform Architecture"
area: "Knowledge Export"
tags:
  - knowledge
  - okf
  - markdown
  - interoperability
---

# ADR 0002: Add Open Knowledge Format v0.1 Compatibility

## Status

Accepted

## Context

Google Cloud introduced Open Knowledge Format (OKF) v0.1 as a minimal, open format for knowledge bundles represented as Markdown files with YAML frontmatter.

The `know` project already uses Markdown plus frontmatter as its export contract, but existing files did not consistently include the OKF-required `type` field or the recommended OKF fields that make bundles easier for other consumers to traverse.

## Decision

`know` exports should be OKF v0.1-compatible by default.

This means:

- every non-reserved Markdown concept document gets a non-empty `type` field;
- recommended OKF fields are derived when available: `title`, `description`, `resource`, `tags`, and `timestamp`;
- existing source provenance fields remain intact;
- OKF compatibility is implemented as additive normalization, not a replacement for source-specific metadata;
- Codex skill files keep their native skill frontmatter shape and expose OKF compatibility through `metadata.okf` so skill discovery is not broken.

The skill-frontmatter clause above is superseded by ADR 0003. Native skills now keep only their runtime fields and are represented through a generated, strictly conformant OKF projection.

## Consequences

Positive:

- exported libraries can interoperate with OKF-aware tools and agents;
- source-specific traceability is preserved;
- old final-layout Markdown can be repaired by rerunning export.

Negative:

- frontmatter is slightly larger;
- Codex `SKILL.md` files cannot be strict OKF concept documents without violating the skill frontmatter contract, so they use OKF metadata rather than top-level OKF `type`.

## Follow-Up

- track upstream OKF spec changes before adopting future versions;
- add stricter bundle generation if a future task requires pure OKF archives without non-Markdown sidecar files.
- follow ADR 0003 for project and skill interoperability.
