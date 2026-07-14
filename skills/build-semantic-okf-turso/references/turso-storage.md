# Turso Storage Contract

## Engine boundary

Use the pinned `pyturso` distribution and import its `turso` module. This is the local embedded Turso Database engine written in Rust. Do not replace it with Python `sqlite3`, the legacy `libsql` client, or a Turso Cloud HTTP connection without a separately reviewed migration.

The baseline is local-first and network-free. `TURSO_DATABASE_URL`, authentication tokens, push, pull, and remote database creation are not required. Treat any future cloud synchronization as a separate explicit operation with its own conflict, credential, and rollback policy.

## Release layout

Write the database to `semantic/knowledge.db` inside the generated release. Build it in the same hidden candidate as the Semantic OKF artifacts and publish the directory only after both surfaces validate.

The database is create-only within a candidate. A refresh reconstructs it from every current normalized record. Never:

- insert, update, or delete rows in a published database;
- copy forward rows from the previous release;
- repair a drifted artifact or concept independently;
- let a database file refer to concepts outside its release; or
- treat cloud replication as a substitute for the release promotion journal.

## Tables

- `bundle_metadata`: storage contract, engine identity, schema digest, source-manifest digest, logical digest, indexed graph map, and row counts.
- `artifacts`: root index plus core JSON, JSONL, and Turtle artifacts with media types and hashes.
- `sources`: one row per reviewed source declaration and its content, record-set, and count evidence.
- `records`: indexed identity, type, title, source, ontology, provenance, body, and canonical record JSON.
- `concepts`: complete generated concept Markdown and its digest, joined one-to-one to `records`.
- `record_attributes`: typed, ordered attribute values for prepared exact filters and SQL joins.
- `rdf_statements`: stable statements from the `data`, `ontology`, and `provenance` graphs.

Do not store parsed blank-node statements in `rdf_statements`, because parser-assigned blank-node labels are not stable database identities. Keep shapes and validation-report Turtle in `artifacts`. The accepted manifest contract already rejects blank nodes from domain source identity.

Do not add triggers, views, virtual tables, full-text indexes, vector indexes, or experimental engine flags to the baseline. Review engine maturity, cross-platform support, deterministic rebuild behavior, query semantics, and migration impact before extending the schema.

## Logical integrity

Compute `logical_sha256` over every table and column in a fixed order, excluding only the digest's own metadata row. This digest proves reproducible logical contents independently of database page layout.

Validation must also check:

1. `PRAGMA integrity_check` returns `ok`;
2. the table and column contract is exact;
3. stored row counts match observed rows;
4. records reference declared sources;
5. records and concepts are one-to-one;
6. canonical record JSON agrees with indexed identity columns;
7. the logical digest recomputes exactly;
8. stored artifacts and concepts match the release files byte-for-text; and
9. the stored source-manifest digest matches the release.

Physical database SHA-256 may vary with compatible engine page layout or process-open order even when logical contents do not. Use the logical digest for reproducibility claims. For compare-and-swap promotion, hash raw bytes for every ordinary release artifact and substitute the validated database `logical_sha256` for the raw `knowledge.db` bytes. Full validation still rejects corrupt or incoherent physical files before that hash is accepted.

## Query boundary

Published databases are read through a separate least-authority client. It must reject active sidecars, hash the published file, copy it to an isolated temporary directory, activate `PRAGMA query_only=1` on that working copy, use prepared values for filters, reject write/admin/file operations in raw SQL, cap result rows, and confirm the published bytes did not change. This prevents the engine's empty connection sidecar from appearing in the immutable release. A direct interactive shell is useful for manual diagnostics but is not the supported read-only agent contract.
