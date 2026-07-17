---
adr: "0029"
title: "ADR 0029: Generalize Entity Graph and Ensemble Retrieval by Authoritative Evidence Identity"
summary: "Add backward-compatible source-generic graph and ensemble schemas that group every route through exact source-record identities and record-body locators, then evaluate them on a pinned Astro documentation corpus acquired through Know."
status: "Accepted"
date: "2026-07-16"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - entity-graph
  - ensemble
  - source-portability
  - astro
  - know
---

# ADR 0029: Generalize Entity Graph and Ensemble Retrieval by Authoritative Evidence Identity

## Status

Accepted.

This decision extends ADRs 0014, 0017, 0019, 0020, 0021, 0023, 0027, and
0028. It preserves the version 1 entity-graph and definitive-ensemble contracts
and their completed evaluations. It adds versioned generic contracts rather than
rewriting historical PDF, arXiv, BioC, PMCID, or MCP evidence.

## Context

The entity-section graph was designed for one record per paper source, literal
`## PDF page N` headings, reviewed claim records, and a separately declared
analysis vocabulary. The definitive ensemble additionally required complete
canonical versioned arXiv identity mappings so adaptive, graph, and embedding
routes could be fused at paper level. Those constraints were honest for the
frozen GraphRAG corpus, but the PMCID portability evaluation showed that they
reject ordinary authoritative sources rather than merely ranking them poorly.

Generic documentation exposes different shapes. One source can contain hundreds
of records. Stable identities may be URLs, slugs, PMCID values, repository paths,
or only source-scoped record IDs. Useful evidence may be an entire record or an
exact character range under a Markdown heading. There may be no reviewed claim
ledger or auxiliary vocabulary. Inferring a paper identity from a filename,
source prefix, heading, or identifier-like string would silently weaken provenance
and can merge records that are distinct in the authoritative Semantic OKF core.

The official Astro documentation is a useful domain-shifted evaluation. Its
English source consists of 416 MDX documents in `withastro/docs`. Know initially
omitted those files because the GitHub adapter did not classify `.mdx` as text.
A rendered-site crawl would also lose exact MDX structure and bind the experiment
to mutable HTML. The repository source at an exact commit provides a stronger
acquisition and locator contract while still exercising Know as the acquisition
and export boundary.

## Decision

### Preserve legacy contracts and add generic schemas

Keep entity-graph schema 1.0 and ensemble schema 1.0 available for byte-compatible
validation and historical reproduction. Add version-dispatched generic schemas.
An existing plan never changes meaning merely because a newer package is installed.

The generic entity graph:

- selects arbitrary Semantic OKF source IDs and accepts any positive record count
  per source;
- does not require paper IDs, reviewed claims, PDF headings, or a vocabulary;
- creates one authoritative record node per `(source_id, record_id)` and keeps
  extracted phrases, mentions, co-mentions, traversal state, and rankings derived;
- segments Markdown by deterministic ATX headings when available and otherwise
  uses deterministic bounded exact record-body ranges;
- binds every section to its source ID, record ID, record hash, concept path,
  source path, concept type, exact locator, text, and text hash; and
- uses source-scoped identities for every node, edge, relation, and lookup.

The generic ensemble publishes a closed, hash-bound total identity crosswalk. Each
selected authoritative record resolves exactly once to an opaque evidence group
derived from a governed namespace and its source-scoped identity. The crosswalk row
is additionally bound to the authoritative record hash, while each returned
evidence identity binds that record hash, exact locator, and retained-text hash.
This keeps the default group stable across content revisions without accepting
stale evidence. Adaptive, entity-graph, and embedding results join only through
this crosswalk. Path prefixes, filenames, titles, headings, and arXiv-shaped strings
are never identity inference rules.

The protected candidate set is a set of evidence groups. Component consensus may
rerank those groups and select the strongest exact passage inside each group, but a
weaker route cannot displace a protected group at the fixed budget. Validation
requires child-plan digest parity, complete component coverage, group parity,
source-scoped identity, exact locator reconstruction, exact evidence-text hashes,
the actual authoritative source path, common core parity, and a closed regular-file
tree.

### Distinguish reviewed-claim and authoritative-passage answer modes

Reviewed-claim coverage and claim-ID finalization remain available only when complete
exact answer bindings exist. A claimless bundle must not fabricate claim IDs or paper
citations. It exposes exact authoritative passages for retrieval and uses a separate
deterministic answer gate. A bounded full-query answer brief derives facet-ranked
verbatim support passages and hash-bound support IDs from the evidence pack; every
draft claim names only those support IDs. The finalizer rebuilds the brief and rejects
unknown IDs, changed quote bindings, malformed
closed-schema drafts, and evidence outside that pack. It then constructs the exact
source, record, path, locator, and hash fields and first-use evidence indices. This
gate establishes identity and quoted-support integrity without relabeling a passage
as a reviewed claim; semantic entailment and completeness still require consultation
review. Claim-only coverage commands remain unavailable for a claimless bundle.

The consultant remains read-only. It may validate and rank local artifacts but may
not write caches, queries, answers, repairs, model downloads, or locks into a
published bundle. MCP remains retired from active definitive consultation under
ADR 0027; the generic build, query, and evaluation paths use deterministic local
CLI operations.

### Acquire and freeze Astro documentation through Know

Know registers the official `https://github.com/withastro/docs.git` repository at
commit `5c37be52c5038e1174be1e838d3dd5852db26a21`. The GitHub adapter treats `.mdx`
as text. The accepted corpus selects every file under
`src/content/docs/en/**/*.mdx`, records the exact 416-file path-and-hash inventory,
and preserves the source bytes and relative paths. The checked compact acquisition
manifest binds the Know key, repository URL, commit, export hash, selected-file
inventory, and generated Semantic OKF manifest. A later upstream commit requires a
new corpus version rather than an in-place refresh of accepted results.

### Evaluate algorithms separately from skill effects

The Astro benchmark is evidence-first. Every question is written only after the
authoritative documents and exact evidence ranges have been inspected. Ground truth
records required source identities, exact paths and hashes, derivation or contrast
logic, acceptable variants, and important negatives.

Direct deterministic evaluation compares retrieval routes over identical
authoritative records and separates recall, reciprocal rank, nDCG, evidence
validity, query errors, latency, build integrity, and portability. Skill Arena is
used only with identical knowledge and isolated one-skill treatments against a
knowledge-only control. A profile containing several consultation skills is a
routing smoke and is not causal evidence.

Large Know stores, exports, generated bundles, and raw runs remain append-only and
ignored. Compact acquisition bindings, inventories, plans, questions, ground truth,
configuration manifests, reports, and English documentation are checked in.

## Consequences

Positive:

- ordinary documentation, BioC passages, repository files, JSON records, and legacy
  papers can use one honest source-scoped evidence identity model;
- graph retrieval can operate without synthetic paper IDs or a reviewed claim
  ledger;
- every fused result has a deterministic cross-component join and an exact path
  back to authoritative text;
- historical plans and metrics retain their original meaning; and
- Astro supplies a substantially broader portability and retrieval test than the
  repeatedly optimized paper benchmark.

Negative:

- the packages must maintain two explicit schema generations and parity tests;
- generic claimless answers cannot use the stronger claim-ID entailment contract and
  instead rely on exact support IDs bound to verified verbatim passages;
- heading and bounded-range sections are retrieval units, not authoritative facts;
- a 416-document evaluation materially increases build and query time; and
- corpus-specific benchmark results do not establish universal superiority.

## Acceptance boundary

Acceptance requires package validation, deterministic double builds, common
authoritative-core hashes, complete identity-crosswalk validation, exact section
and evidence reconstruction, read-only consultation, zero benchmark leakage,
validated evidence-first questions and ground truth, direct route comparison,
isolated Skill Arena configuration validation and dry runs, repository tests, and
the application coverage gate. Any executed route with invalid evidence, stale
hashes, identity inference, core drift, or a modified bundle fails independently of
its ranking score.
