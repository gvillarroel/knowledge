---
adr: "0012"
title: "ADR 0012: Package Semantic OKF Build and Consultation as Standalone Skills"
summary: "Make each Semantic OKF skill independently installable and narrow build to folder lifecycle while consult provides general read-only navigation context."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Operations"
tags:
  - knowledge
  - okf
  - skills
  - standalone
  - lifecycle
  - consultation
---

# ADR 0012: Package Semantic OKF Build and Consultation as Standalone Skills

## Status

Accepted.

This decision strengthens ADR 0010. It preserves the separate authority model while superseding ADR 0010's allowance for shared external code or references and its explicit cross-skill handoff.

## Context

The lifecycle and consultation skills were separated conceptually, but they were not fully independent packages. The builder refresh command executed an OKF validator from a sibling skill. Both skill instructions named the other package as a handoff target, and the builder described post-publication consultation. The consultant also framed invalid input as a reason to invoke the builder instead of returning a read-only diagnostic.

Those links make installation order and repository layout part of the runtime contract. They also blur the intended responsibilities: construction and maintenance for the builder, versus general read-only navigation context for the consultant.

## Decision

Package `build-semantic-okf` and `consult-semantic-okf` as standalone directories.

For both skills:

- every runtime script, validator, reference, and instruction must live inside the skill directory;
- bundled scripts may depend on third-party Python packages only through requirements declared inside that directory;
- no instruction or runtime path may require a sibling skill, repository document, evaluation fixture, or repository-relative helper;
- copying the directory outside the repository must preserve its supported behavior.

`build-semantic-okf` exclusively owns the source definition and generated knowledge-folder lifecycle: source inspection, topology, manifest and mapping authoring, deterministic materialization, validation, refresh, promotion, rollback, and recovery. It does not provide knowledge lookup, question answering, comparison, citation, or synthesis workflows. The independent OKF validator used during refresh is bundled with the builder.

`consult-semantic-okf` exclusively gives an agent general read-only context and local helpers for efficient navigation of an existing knowledge folder. It explains progressive discovery through the ledger, concepts, and explicitly selected semantic graphs; preserves provenance and evidence paths; and never acquires sources, changes manifests, repairs validation, or mutates the folder. Missing, stale, untrusted, or invalid folders produce a diagnostic and stop condition rather than a cross-skill handoff.

The two packages may implement the same public file-format rules independently. Drift is controlled by package-local tests and copied-directory smoke tests rather than a runtime dependency between the skills.

## Consequences

Positive:

- either skill can be installed, copied, tested, and used without the repository or the other skill;
- trigger metadata and instructions align with one responsibility;
- consultation retains least authority and the builder contains its complete maintenance toolchain;
- external layout changes cannot break refresh validation.

Negative:

- shared format rules and the OKF validator are duplicated across package boundaries;
- compatible format changes may require coordinated edits in both packages;
- tests must detect external references and exercise each copied package independently.
