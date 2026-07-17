---
adr: "0031"
title: "ADR 0031: Add Turso-Backed Semantic OKF Build and Consultation Skills"
summary: "Publish a local Turso Database projection with each Semantic OKF release and query it through a separate least-authority skill."
status: "Accepted"
date: 2026-07-14
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Storage"
tags:
  - knowledge
  - okf
  - turso
  - database
  - sql
  - skills
---

# ADR 0031: Add Turso-Backed Semantic OKF Build and Consultation Skills

## Status

Accepted.

This decision extends ADR 0004, ADR 0010, ADR 0012, and ADR 0014 without replacing the existing file-backed Semantic OKF skills.

## Context

The existing Semantic OKF release provides a deterministic record ledger, readable Markdown concepts, explicit RDF graphs, provenance, constraints, and validation evidence. Consultation reparses JSONL and Turtle on each invocation. That remains portable and auditable, but repeated filters, joins, aggregations, and cross-source traversal benefit from a relational indexed query surface.

Turso now maintains two related engines. `libSQL` is the production-ready fork of SQLite. Turso Database is a newer ground-up rewrite of SQLite in Rust, with a SQLite-compatible SQL and file interface. The current Python package for local embedded use is `pyturso`, imported as `turso`. Choosing the older `libsql` client or Python's standard `sqlite3` would not implement the requested Rust-engine variant.

The Turso Database engine and bindings are still evolving. A safe integration must therefore pin the package, preserve the existing semantic evidence, avoid experimental features, detect logical drift independently of physical page layout, and keep database writes out of the consultation authority.

## Decision

Ship two additional standalone skills:

1. `build-semantic-okf-turso` owns source ingestion, complete Semantic OKF materialization, Turso database creation, validation, refresh, promotion, rollback, and recovery.
2. `consult-semantic-okf-turso` owns read-only verification, prepared record and triple filters, stored-artifact reading, schema and statistics inspection, and bounded SQL consultation.

Retain `build-semantic-okf` and `consult-semantic-okf` as the file-backed baseline. The Turso variants are separate packages rather than conditional modes so their dependency, storage, authority, and evaluation boundaries remain explicit.

Use pinned `pyturso==0.6.1` and the `turso` Python module for the local embedded baseline. Do not silently substitute `sqlite3`, `libsql`, Turso Cloud over-the-wire access, or an external SQLite process. A missing wheel may require a Rust and native compiler toolchain; runtime preflight failure is an explicit diagnostic.

The local baseline is network-free. It does not require a Turso organization, database URL, token, push, pull, or remote write. Cloud synchronization may be added only through a separately reviewed conflict, credential, revision, and rollback contract.

Each release contains the unchanged Semantic OKF core plus `semantic/knowledge.db`. The folder remains one release unit. The reviewed source plan and normalized records remain provenance authority; the database is the required indexed consultation projection for the Turso variant. A build publishes neither surface until both pass.

The database contains:

- storage and engine metadata;
- copies and hashes of the root index and core semantic artifacts;
- source declarations and source/record-set digests;
- normalized records and canonical record JSON;
- complete generated concept Markdown;
- typed ordered record attributes; and
- stable RDF statements from the data, ontology, and provenance graphs.

Shapes and validation reports remain stored textual artifacts rather than parsed statement rows because their blank-node labels are not stable cross-parse identities. Source blank nodes remain prohibited by the existing ingestion contract.

Do not use views, triggers, virtual tables, FTS, vector indexes, MVCC flags, or other experimental engine features in the baseline. Use ordinary tables, primary keys, and indexes supported by the verified engine surface.

Build the bundle and database in one hidden candidate. Database creation is create-only. Refresh reprocesses every declared source and reconstructs every file and row; it never merges generated trees or carries rows forward. Candidate validation requires core Semantic OKF and OKF checks plus:

- `PRAGMA integrity_check`;
- exact table and column shape;
- relational source, record, concept, and attribute coherence;
- stored row counts;
- canonical record JSON agreement;
- artifact and concept parity with the candidate files;
- source-manifest digest agreement; and
- a deterministic logical digest over every declared table and column.

Use the logical digest for database-content reproducibility independently of compatible physical page layout. Turso-variant compare-and-swap hashing uses raw bytes for ordinary release files and the validated database logical digest for `knowledge.db`; full integrity and relational validation must pass before that digest is accepted. This avoids false changes when engine page layout varies with process-open order while preserving semantic change detection.

Consultation rejects a published database with active sidecars, hashes the quiescent file, copies it into an isolated temporary directory, activates `PRAGMA query_only=1` on that working copy, and verifies the database contract. This contains the engine's connection sidecar outside the immutable release. High-level filters use prepared parameters. Raw SQL accepts one size-bounded `SELECT`, `WITH`, or `EXPLAIN` statement, rejects mutation, transaction, attachment, pragma, extension, and file-access surfaces, caps result rows by default, and requires unique output column names. The helper re-hashes the published database after consultation and fails if it changed.

The `records` and `concepts` tables handle identity, source, type, attributes, lexical discovery, and reading. The `rdf_statements` table handles joins and traversal only after explicitly selecting `data`, `ontology`, or `provenance`. Shapes and validation artifacts must never be presented as ordinary domain facts.

## Consequences

Positive:

- repeated exact filters, joins, grouping, aggregation, and traversal use indexed local SQL;
- the requested Rust Turso Database engine is exercised directly through its supported Python binding;
- the database remains auditable against the existing Markdown, JSONL, RDF, provenance, and validation evidence;
- build and consultation retain separate mutation authorities;
- complete rebuilds remove stale rows when source membership changes;
- prepared filters, query-only mode, SQL screening, result limits, and byte checks provide layered read-only enforcement; and
- the local baseline remains offline and credential-free.

Negative:

- each release stores duplicated concept and semantic artifact content;
- database creation and full logical validation add build time and disk use;
- Windows or an unsupported interpreter may compile a substantial Rust extension when no wheel is available;
- evolving Turso compatibility may require future schema or runtime revisions;
- the standalone variants duplicate builder and validation logic; and
- Turso Cloud synchronization is intentionally not included in this decision.
