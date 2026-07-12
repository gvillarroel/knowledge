---
adr: "0010"
title: "ADR 0010: Separate Semantic OKF Lifecycle and Consultation Skills"
summary: "Give snapshot mutation and read-only knowledge consultation distinct skills, resources, tests, and evaluation profiles."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Operations"
tags:
  - knowledge
  - okf
  - skills
  - lifecycle
  - consultation
---

# ADR 0010: Separate Semantic OKF Lifecycle and Consultation Skills

## Status

Accepted.

This decision supersedes the combined skill-packaging direction in ADR 0004. It preserves ADR 0004's accepted refresh and query semantics, but assigns them to separate agent skills.

## Context

Semantic OKF work has two materially different authority levels. Lifecycle operations create or replace artifacts: they review source topology and mappings, ingest or remove declared sources, rebuild complete snapshots, validate candidates, and promote a new release. Consultation operations consume a published snapshot: they locate facts, select graphs, aggregate or traverse relations, synthesize across sources, and return verifiable evidence.

Combining both workflows in `build-semantic-okf` made its trigger ambiguous. A request to answer a question could load mutation instructions and source-management tools, while a request to expand a source collection also loaded detailed answer-synthesis guidance. Reader evaluations then mounted a complete builder skill, so they could not prove that the consultation procedure was independently sufficient or read-only.

Ontology extraction is a third, earlier concern. It derives a reviewed semantic model from evidence. It does not own Semantic OKF snapshot lifecycle or consultation.

## Decision

Maintain two distinct Semantic OKF skills:

1. `build-semantic-okf` owns mutation and lifecycle operations. It selects and records source-combination topology; creates bundles; adds, changes, or removes declared sources and reviewed mappings; reprocesses every declared source during refresh; validates complete candidates; and performs guarded promotion or recovery.
2. `consult-semantic-okf` owns read-only use of published knowledge. It chooses among the record ledger, concept Markdown, and explicitly selected RDF graphs; runs local read-only queries; answers and compares questions; synthesizes across sources; and verifies citations, page locators, source counts, and exact evidence paths.

The consultation skill must never modify a source, manifest, generated concept, semantic graph, report, or published snapshot. The lifecycle skill must not present itself as the skill for searching, answering, comparing, or citing knowledge. When one user request contains both phases, complete and validate the lifecycle phase first, then hand the immutable snapshot revision to the consultation phase explicitly.

Keep `extract-ontologies` focused on evidence-led ontology learning and authoring before materialization. Its trigger and agent prompt must exclude Semantic OKF creation, expansion, refresh, repair, and consultation.

Each skill must be independently usable and tested. A consultation profile must not gain lifecycle authority through a sibling import, mounted builder skill, shared writable overlay, or hidden build command. Shared format rules may be represented by narrowly scoped read-only code or references, but the consultation implementation must not depend on installing the builder skill.

## Test and evaluation contract

Lifecycle tests cover source topology, initial creation, source declaration additions and removals, changed mappings and schemas, complete reprocessing, stale-record deletion, semantic version review, validation, atomic failure, promotion, rollback, and recovery.

Consultation tests cover ledger filtering, lexical discovery, typed values, graph selection, traversal, aggregation, provenance, ontology and SHACL questions, path safety, output contracts, cross-source synthesis, citation grounding, and snapshot immutability. They must reject SPARQL mutation, federation, implicit dataset clauses, and any attempt to write into the bundle.

Boundary tests verify mutually exclusive metadata triggers, the absence of lifecycle commands from reader-only overlays, and unchanged bundle hashes after consultation. Active reader benchmarks use an independently pinned `consult-semantic-okf` snapshot plus pinned knowledge. Completed historical benchmark artifacts remain immutable and keep the skill identity and hashes that were actually evaluated.

## Consequences

Positive:

- consultation receives least-authority instructions and tools;
- lifecycle changes and reader-procedure changes can regress independently;
- benchmarks can measure the consultation skill without also mounting mutation capabilities;
- trigger selection is clearer for creation, update, and answer requests;
- ontology authoring remains distinguishable from bundle materialization.

Negative:

- query code that previously imported builder internals must gain an independent read-only implementation boundary;
- shared Semantic OKF format rules need drift tests or one intentionally generated source of truth;
- existing active configurations and generated OKF projections must migrate to the new consultation skill;
- historical results require explicit labeling because they evaluated the formerly combined skill.
