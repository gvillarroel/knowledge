---
adr: "0003"
title: "ADR 0003: Project Native Skills into a Strict OKF Bundle"
summary: "Keep runtime skill metadata native and publish the project plus every skill as a generated OKF v0.1 subdirectory."
status: "Accepted"
date: "2026-07-09"
product: "knowledge"
owner: "Platform Architecture"
area: "Knowledge Interoperability"
tags:
  - knowledge
  - okf
  - skills
  - interoperability
---

# ADR 0003: Project Native Skills into a Strict OKF Bundle

## Status

Accepted

## Context

OKF v0.1 requires every non-reserved concept document to have a non-empty top-level `type`. Native Codex skills use `SKILL.md` discovery frontmatter whose portable contract is `name` and `description`.

ADR 0002 attempted to combine these contracts through `metadata.okf.type`. That marker is not strict OKF because the required field is not top-level, and it adds runtime metadata that is unnecessary for skill discovery.

The OKF specification permits a bundle to be a subdirectory of a larger repository. This provides a clean compatibility boundary without turning every repository Markdown file into a concept or breaking native tool contracts.

## Decision

The repository publishes a deterministic OKF v0.1 bundle under `okf/`.

- `project.md` projects `README.md` as a `Software Project` concept.
- `specification.md` projects `SPEC.md` as a `Project Specification` concept.
- `skills/<name>.md` projects every `skills/*/SKILL.md` as an `Agent Skill` concept.
- Native skill frontmatter contains only `name` and `description`.
- The projection preserves traceability with producer-defined `source_path` and `skill_name` fields.
- Reserved `index.md` files provide progressive disclosure; only the root index declares `okf_version: "0.1"`.
- The checked-in projection is generated and drift-checked with the scripts bundled in `skills/open-knowledge-format/`.

This decision supersedes only the Codex skill-frontmatter clause in ADR 0002. The export normalization decision in ADR 0002 remains accepted.

## Consequences

Positive:

- the project and all current or future repo-local skills form a strict, independently consumable OKF bundle;
- native skill discovery remains valid and portable;
- adding a skill automatically changes the expected bundle, so CI or tests can detect projection drift;
- OKF consumers receive normal top-level `type` values instead of a vendor-specific nested marker.

Negative:

- projected Markdown duplicates source documentation;
- contributors must regenerate the bundle after changing project documentation or skills.

## Upstream Baseline

The implementation was reviewed against GoogleCloudPlatform `knowledge-catalog/okf/SPEC.md` at commit `ee67a5ca27044ebe7c38385f5b6cffc2305a9c1a`, dated June 12, 2026. Future OKF revisions require a specification diff and an ADR update before changing conformance behavior.
