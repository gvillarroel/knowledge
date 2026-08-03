---
adr: "0082"
title: "ADR 0082: Cache Normalized Inputs for Incremental Semantic Refresh"
summary: "Detect raw-file deltas by content and reuse only processor-bound normalized records while retaining complete validated snapshot publication."
status: "Accepted"
date: "2026-07-30"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Operations"
tags: [knowledge, incremental, cache, refresh, provenance]
---

# ADR 0082: Cache Normalized Inputs for Incremental Semantic Refresh

## Status

Accepted. This refines the processing strategy in ADR 0004 without changing its
complete replacement, validation, review, transaction, or recovery boundaries.

## Context

ADR 0004 correctly rejects in-place merging of generated Markdown, RDF, and
provenance because deleted inputs could leave stale knowledge. Its requirement
to parse every raw file on every refresh is nevertheless expensive for corpora
whose acquisition, PDF extraction, or normalization cost is much larger than
the number of changed files.

Folder dates and filesystem modification times are insufficient change
identities. Files can be copied while preserving a timestamp, regenerated with
the same date, renamed, deleted, or changed by a new paper version. Reusing
normalized output by raw content alone is also unsafe when a mapping, adapter,
or processor implementation changes.

Content-addressed systems demonstrate the useful separation. Git names stored
objects by content. DVC tracks directory members with per-file hashes. Apache
Iceberg uses manifests to classify added, existing, and deleted files while a
snapshot still represents the complete table state.

## Decision

Add an opt-in external incremental cache to the canonical Semantic OKF builder
and refresh command.

1. Inventory every resolved physical input as `(source_id, logical_path,
   size, raw_sha256)`.
2. Bind each cached raw-record object to the exact adapter configuration and a
   processor digest covering the adapter and semantic core implementation.
3. Reuse an object only when logical identity, raw content, adapter
   configuration, processor digest, object digest, record count, source ID,
   source kind, and cached locator all validate.
4. Parse added or changed files through their real deterministic adapter.
   Treat a rename as one removal and one addition because paths can participate
   in record identity and provenance.
5. Remove deleted-file objects from the current cache manifest and omit their
   records from the candidate. Content-addressed objects may remain as
   unreferenced, recoverable cache data.
6. Finalize all current records and materialize a complete new snapshot. Never
   copy generated concepts or merge RDF from the published snapshot.
7. Run the existing semantic, OKF, SHACL, source-stability, review, CAS,
   journaled promotion, and recovery gates unchanged.
8. Keep cache metrics outside authoritative snapshot bytes so cold and warm
   builds from identical inputs remain byte-identical.
9. Treat missing, invalid, or corrupt cache state as a cache miss. The cache is
   derived, answer-ineligible, and safe to delete.

The cache must live outside the raw source tree and generated snapshot. The
machine-readable run report classifies exact added, changed, removed, unchanged,
processed, and reused files and reports processed and reused record counts.

## Consequences

Positive:

- unchanged PDFs, Markdown files, partitions, and pages avoid repeated adapter
  work;
- deletions still produce a clean complete snapshot without stale concepts or
  triples;
- processor or mapping changes invalidate reuse automatically;
- the cache can be rebuilt from raw sources and never becomes an evidence
  authority; and
- complete snapshot bytes remain deterministic regardless of cache warmth.

Negative:

- complete graph and concept materialization remains linear in current record
  count;
- one changed multi-record file still reparses every record in that file;
- cache objects consume additional disk until garbage-collected; and
- acquisition connectors still need their own conditional-request or
  version-discovery logic before local raw-file delta processing begins.

## Validation

Acceptance requires tests for cold and warm builds, byte identity, exact
add/change/remove classification, corrupt-object fallback, deletion without
stale knowledge, incremental refresh promotion, and a paper update run whose
read-only query result changes only after the new source is published.
