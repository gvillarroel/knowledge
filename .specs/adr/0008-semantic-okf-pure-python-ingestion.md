---
adr: "0008"
title: "ADR 0008: Use Deterministic Pure-Python Semantic OKF Adapters"
summary: "Remove the external distributed runtime and ingest Semantic OKF sources with strict deterministic Python adapters."
status: "Accepted"
date: "2026-07-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Processing"
tags:
  - knowledge
  - python
  - csv
  - json
  - rdf
  - determinism
---

# ADR 0008: Use Deterministic Pure-Python Semantic OKF Adapters

## Status

Accepted. This decision supersedes ADR 0005.

## Context

The Semantic OKF builder previously depended on Apache Spark for CSV, JSON, Markdown, and RDF ingestion. That dependency required Java, platform-specific worker behavior, a large runtime installation, and execution controls unrelated to the size and atomic materialization model of the current bundles.

Evaluation model identifiers are routing concerns for their harnesses. They are independent from ingestion technology and do not justify a distributed data-processing dependency in the knowledge-building skill.

The materializer already retains the complete normalized record set to validate cross-artifact identity, provenance, and digests before atomic publication. A strict local adapter layer can therefore preserve the semantic contract while reducing operational complexity.

## Decision

Semantic OKF ingestion will use deterministic Python adapters with no Java, JDK, PySpark, or external processing engine.

The adapters will:

- match CSV headers exactly and case-sensitively, independent of manifest member order;
- reject duplicate, missing, extra, and width-mismatched CSV columns;
- parse declared booleans, 32-bit integers, 64-bit integers, finite doubles, ISO dates, and ISO timestamps strictly;
- preserve dotted field names as literal top-level names;
- parse JSON with duplicate-key and non-standard-number rejection;
- accept JSON Lines as one object per line and multiline JSON only as one object or an array of objects;
- reject nested values where a scalar field is declared;
- normalize and sort records before materialization;
- discover and hash source members before parsing, rediscover membership after parsing, and rehash content before publication so membership and content races fail;
- materialize through an atomic staging directory and publish only a validated complete snapshot.

Generated reports will identify the stable processor contract as `semantic-okf-python` with a contract version and source and record counts. They will not encode host Python patch versions or platform details that would make otherwise identical snapshots differ.

Refresh continues to reprocess every declared source. It never merges an old generated tree with a new one.

## Consequences

Positive:

- the skill has a small locked Python dependency set and no external runtime installation;
- local Windows, macOS, and Linux behavior is easier to reproduce;
- source membership, source content, record ordering, and scalar conversions have explicit failure contracts;
- semantic artifacts remain byte-stable for equivalent normalized inputs;
- evaluation model routing can change independently without coupling the knowledge-building skill to a data-processing engine.

Negative:

- ingestion is single-process and does not provide distributed scale-out;
- normalization and atomic cross-layer validation retain all records in memory;
- bundles that exceed comfortable local memory or latency limits require an upstream partitioning strategy or a separately designed streaming materializer;
- the superseded decision remains in the ADR history so the prior implementation and its rationale stay auditable.
