---
adr: "0001"
title: "ADR 0001: Treat Library Export as the Primary Contract"
summary: "Make exported Markdown library output the stable contract between knowledge ingestion and downstream consumers."
status: "Proposed"
date: "2026-04-05"
product: "knowledge"
owner: "Platform Architecture"
area: "Knowledge Export"
tags:
  - knowledge
  - markdown
  - contract
---

# ADR 0001: Treat Library Export as the Primary Contract

## Status

Proposed

## Context

`know` already ingests multiple source systems and materializes local state, but downstream tools
need one predictable interface that is durable, inspectable, and portable across environments.

## Decision

We should treat the exported Markdown library as the primary contract for downstream consumers.

That means:

- ingestion remains source-specific
- normalization remains internal
- exported Markdown becomes the stable handoff format

## Consequences

Positive:

- downstream tools can rely on one portable output model
- debugging becomes easier because the handoff is human-readable
- archives and sharing workflows stay simple

Negative:

- some source-specific richness may not survive the export unchanged
- export semantics need stronger versioning discipline

## Follow-Up

- document the export contract
- define version markers for generated libraries
- add regression checks for exported Markdown structure
