---
adr: "0004"
title: "ADR 0004: Refresh Semantic OKF Snapshots and Query by Layer"
summary: "Rebuild semantic bundles from their original manifests, promote validated snapshots transactionally, and query the cheapest authoritative layer."
status: "Accepted"
date: "2026-07-11"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Operations"
tags:
  - knowledge
  - okf
  - rdf
  - refresh
  - query
---

# ADR 0004: Refresh Semantic OKF Snapshots and Query by Layer

## Status

Accepted

## Context

The Semantic OKF builder creates and validates deterministic snapshots, but its output path is create-only. The skill description promises updates without defining how an existing bundle is reprocessed or promoted. It also requires competency queries without explaining which generated layer should answer discovery, full-text, semantic, or provenance questions.

Incrementally merging generated files is unsafe because removed source records could leave stale Markdown, RDF, or provenance behind. Replacing a non-empty directory is not a single portable atomic operation. Querying every layer for every question is also wasteful and can accidentally combine domain data, ontology axioms, validation shapes, and reports.

## Decision

Keep `build_semantic_okf.py` create-only and add separate refresh and query commands.

Refresh behavior:

- always load the original external manifest from its original source root;
- rebuild every declared source through the real Python adapters into a new sibling snapshot;
- validate semantic coherence and strict OKF conformance before promotion;
- compare source, record, artifact, plan, revision, and full-tree digests;
- require explicit approval for record removals and reviewed plan changes;
- reject semantic plan changes that reuse an immutable ontology `version_iri`;
- preserve the bundle `base_iri` and `ontology_iri` across an in-place refresh;
- serialize writers with a sibling lock and detect concurrent mutation with a current-tree digest;
- let unattended promotion pin both the previously published tree and the exact candidate tree reviewed during `--check`, because preview and promotion are separate rebuilds;
- promote with a journaled two-rename transaction, rollback on ordinary failure, and provide deterministic recovery after interruption;
- never merge trees or preserve unmanaged files from the old snapshot.

Because portable filesystems cannot exchange a populated directory in one operation, the direct output path may be absent briefly between the two renames. Readers that require uninterrupted availability must use immutable release directories plus an independently managed pointer outside this contract.

Query behavior:

- use `records.jsonl` for cheap identifier, source, type, attribute, and concept-path filtering;
- use `concepts/` Markdown for human reading and fixed-string lexical search;
- use `data.ttl` for explicit domain facts, add `ontology.ttl` only for schema-aware work, and add `provenance.ttl` only for lineage;
- do not treat `shapes.ttl` or `validation-report.ttl` as domain knowledge;
- allow only local, read-only SPARQL `SELECT` and `ASK` queries in the bundled helper;
- reject SPARQL federation and dataset clauses so graph selection remains an explicit local allowlist;
- run with entailment `none`; use separately declared reasoner tooling when inference is required;
- recommend a persistent indexed triplestore for repeated queries or bundles too large to parse per invocation.

The manifest schema remains unchanged. Durable competency-query files and expected results stay beside the original manifest rather than being copied into the generated bundle implicitly.

## Consequences

Positive:

- additions, changes, and deletions are reflected coherently across Markdown, RDF, and provenance;
- failed builds and ordinary promotion failures leave the previous validated snapshot recoverable;
- automation receives stable machine-readable diffs and exit codes;
- common lookups avoid parsing RDF, while semantic joins remain available through SPARQL;
- query graph boundaries and entailment assumptions are explicit.

Negative:

- refresh requires enough disk space for the old snapshot, candidate, and temporary backup;
- promotion has a short two-rename visibility gap;
- interrupted promotion may require the recovery command before another refresh;
- one-shot RDFLib SPARQL still reparses selected Turtle graphs and is not a substitute for a production triplestore.
