---
adr: "0006"
title: "ADR 0006: Make Semantic OKF Source Combination Explicit"
summary: "Represent separate authorities as distinct declarations, compatible partitions as one glob-backed logical source, and true entity fusion as an upstream canonicalization stage."
status: "Accepted"
date: "2026-07-11"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Processing"
tags:
  - knowledge
  - provenance
  - identity
  - federation
  - canonicalization
---

# ADR 0006: Make Semantic OKF Source Combination Explicit

## Status

Accepted

## Context

A multi-input semantic bundle can mean materially different things. Inputs may need to remain distinguishable because they have different authorities, identity namespaces, governance, or release needs. Alternatively, several files may be homogeneous partitions of one logical record set. A third case requires records from several sources to be matched, reconciled, and coalesced into canonical entities.

The existing manifest has a closed schema. It directly represents the first case as several source declarations and the second as one declaration whose path glob resolves several files. The normalized record model has one source ID, one record ID, one physical source path, and one provenance origin. It cannot represent field-level winner decisions or several raw origins for one fused record.

Without an explicit protocol, callers could incorrectly treat a shared `data.ttl` as isolation, use a glob as implicit deduplication, or infer real-world equivalence from overlapping IDs and values.

## Decision

Every Semantic OKF plan with more than one physical input will record one reviewed topology beside the manifest:

1. **Separate bundles** for permissions, tenants, licensing, retention, deletion, independent ontology versions, or independent release and rollback boundaries.
2. **Separate declarations in one bundle** when sources may share one validated snapshot but must retain source-scoped identity, provenance, and query filters.
3. **Homogeneous partition union** when every physical member implements one adapter, schema, mapping, authority, governance, identity namespace, and refresh lifecycle. Encode this as one source declaration with one path glob.
4. **Upstream canonicalization** when records require cross-source matching, schema normalization, deduplication, field precedence, conflict resolution, or multi-origin lineage. Ingest the deterministic canonical output as a new logical source and retain its identity map, merge ledger, conflicts, quarantine, and raw-source inventory as release evidence.

Non-RDF record identity remains `(source_id, record_id)`. A local ID may overlap across separate declarations but must be unique across a homogeneous partition union. RDF subjects remain absolute and therefore collide globally inside one bundle. Duplicate concept IDs and subject IRIs fail; file order, first-write-wins, last-write-wins, and automatic `owl:sameAs` are not conflict policies.

The source-combination decision is a sidecar because the current manifest schema is closed. It records the mode, members, logical source ID when applicable, identity scope, a `reject-within-identity-scope` duplicate policy, governance and approval references, and whether record fusion occurred. The expected-member path/hash inventory is also sidecar evidence and must be checked by an external blocking gate because the current builder reports observed members but does not enforce an expected set.

Consultation follows the topology:

- use streaming ledger filters for one exact source or logical union;
- use Markdown for lexical discovery and reading;
- use the accepted data graph for cross-source joins and aggregation while retaining `sourceId`;
- add provenance only for physical-member lineage;
- use an authorized external dataset or triplestore for independent bundles or frequent large queries, with every consulted revision pinned.

## Consequences

Positive:

- overlapping local IDs remain observable without accidental entity collapse;
- compatible partitions can be processed and queried as one source without adding manifest fields;
- duplicate identities and RDF subjects fail instead of producing order-dependent output;
- governance and access boundaries are not confused with source labels in one graph;
- refresh and query expectations are explicit for each topology;
- unsupported entity fusion is routed to a reproducible, auditable stage.

Negative:

- separate declarations inside one bundle still share validation, publication, and refresh lifecycle;
- one changed partition changes the aggregate source digest used throughout its logical source;
- the generated source manifest does not contain a per-member raw-hash inventory, so that inventory remains required sidecar evidence;
- the current builder does not enforce the expected-member inventory, so release automation must perform that comparison before build and refresh;
- upstream canonicalization adds artifacts and review work when records truly overlap;
- federated or independently authorized querying requires infrastructure outside the local snapshot helper.
