---
adr: "0044"
title: "ADR 0044: Add a Tika and Java MALLET Semantic OKF Experiment"
summary: "Extract heterogeneous local documents with Tika 4, preserve them in an authoritative Semantic OKF core, and derive a read-only Java MALLET topic-retrieval projection through a standalone skill pair."
status: "Accepted"
date: "2026-07-22"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Ingestion and Retrieval"
tags:
  - knowledge
  - okf
  - tika
  - mallet
  - lda
  - retrieval
  - skills
---

# ADR 0044: Add a Tika and Java MALLET Semantic OKF Experiment

## Status

Accepted.

This decision extends ADRs 0010, 0012, 0014, 0019, and 0042. It does not modify
the accepted classical skills, the RustMallet candidate, the canonical eight-family
Harbor registry, or historical evaluation artifacts.

## Context

The existing Semantic OKF builders consume already textual Markdown, CSV, JSON,
or RDF sources. Apache Tika can detect and extract text and metadata from binary
document formats, and its 4.0.0-beta-1 release changes the default content handler
to Markdown. Java MALLET provides a mature sparse-Gibbs LDA implementation that is
distinct from both deterministic classical topic communities and the RustMallet
Python binding already evaluated in ADR 0042.

Combining these tools is useful only if their outputs remain subordinate to the
reviewed OKF authority model. Tika extraction must not silently replace source
provenance, and MALLET topics must not become ontology classes or accepted facts.
Both tools also require Java 17 and independently supplied distributions. The
MALLET command-line layer can report a process success code even when an option is
malformed, so process exit alone is not an adequate validation contract.

## Decision

Ship two additional standalone experimental skills:

1. `build-semantic-okf-tika-mallet` hashes selected local files, extracts Markdown
   and canonical metadata with Apache Tika 4.0.0-beta-1, materializes and validates
   an authoritative Semantic OKF core, then derives a Java MALLET 2.1.0 retrieval
   projection.
2. `consult-semantic-okf-tika-mallet` validates and searches the resulting snapshot
   read-only through BM25, MALLET topic expansion, PPMI association, or reciprocal
   rank fusion, and requires authoritative concept or ledger verification before a
   factual answer.

Treat Java 17, an unpacked official Tika application distribution, and an unpacked
official MALLET distribution as explicit public prerequisites. Never download,
install, or discover them implicitly. Preflight exact tool versions and record a
sorted hash inventory of the jars that executed.

The builder uses Tika's default handler and separately requests `--md`; the two
normalized UTF-8 outputs must agree for every input. It also requests `--json`,
canonicalizes metadata, and persists a closed ingestion receipt that binds the
plan, source-relative locator, raw byte hash, metadata hash, extracted body hash,
and generated Markdown source. Tika diagnostics containing timestamps are not
domain evidence and are not persisted.

Generate a narrow `ExtractedDocument` ontology for this experimental ingestion
boundary. Require source locator, raw hash, media type, Tika version, metadata hash,
and extracted-body hash through SHACL. The generated concept Markdown, record
ledger, and purpose-selected RDF graphs remain authoritative inside the snapshot;
the original local file remains the external source authority identified by the
receipt.

Run MALLET with an explicit pretokenized corpus, exact `mallet-2.1.0.jar`, fixed
seed, one training thread, closed sampler parameters, and required output files.
Parse and validate document-topic rows and topic-word weights independently. Fail
when any expected output is absent, empty, malformed, incomplete, duplicated, or
inconsistent even when the Java process returned zero. Persist only canonical,
hash-bound retrieval artifacts; temporary MALLET serialization and training files
never enter the published snapshot.

Allow one immediate retry only when Java reports the exact Windows JShell/JDI
signature `TransportTimeoutException: timeout waiting for connection` while
launching the execution engine. This narrow retry addresses an observed transient
local listener failure without treating ordinary MALLET, option, timeout, parsing,
or non-zero-exit failures as recoverable.

Snapshot each selected raw file into private storage with one content read before
invoking Tika. Hash that same byte stream, reject an identity or metadata change
during the copy, and run default Markdown, explicit Markdown, and metadata
extraction only against the private snapshot. Reject symbolic links and Windows
reparse points lexically before resolving plan inputs, runtimes, bundle trees, or
publication paths.

Construct MALLET's Java classpath from the sorted, hash-bound jar inventory rather
than a wildcard, and revalidate executable, directory, and jar-tree identities
immediately around each Java invocation. Deep consultant retraining must use a
fresh scratch directory disjoint from both the immutable bundle and MALLET home,
even when the process temporary-directory setting is hostile.

Publish only through an atomic no-replace rename after rechecking the output parent
identity. A concurrently created destination, including an empty directory or a
dangling link, is a hard failure and is never overwritten. Consultant inspection
accepts only the closed root, Semantic, Tika, concept, and classical trees bound by
the authoritative ledger and receipts.

Keep Tika ingestion evidence under `tika/` and the derived retrieval projection
under `classical/`. Tika extraction metadata and MALLET scores are provenance and
discovery signals, not accepted domain assertions. The consultant never writes a
cache, lock, query, or regenerated model into the bundle. Ordinary inspection and
search need no Java runtime; explicit deep validation may retrain MALLET against an
independently supplied matching runtime.

Keep the pair outside the canonical Harbor registry until a separate evidence-first
evaluation establishes document-format coverage, extraction fidelity, retrieval
quality, grounded-answer quality, runtime cost, and cross-platform reproducibility.

## Consequences

Positive:

- binary PDF, Office, and other Tika-supported inputs gain a hash-bound route into
  Semantic OKF without weakening record or evidence identity;
- the experiment exercises upstream Java MALLET rather than a substitute library;
- Tika's new default-Markdown behavior is tested directly against explicit
  Markdown output;
- retrieval remains separable from authoritative OKF records and RDF semantics;
  and
- copied skill packages retain explicit, diagnosable external tool boundaries.

Negative:

- Java 17 and two external distributions increase setup and build cost;
- extracting each input twice to verify the beta default handler increases Tika
  runtime;
- fixed-seed, single-thread MALLET reproducibility still requires validation on
  each supported platform and exact distribution;
- the generic extraction ontology does not replace evidence-led domain ontology
  authoring; and
- Tika Markdown fidelity and MALLET retrieval merit require broader evaluation
  before either technology can become a default.

## Acceptance boundary

Acceptance requires exact-version preflight, real Tika extraction of at least two
document formats, default-versus-explicit Markdown equality, canonical metadata,
complete raw-to-concept bindings, passing Semantic OKF and SHACL validation,
fixed-seed one-thread MALLET determinism, two byte-identical complete builds,
closed-tree and tamper tests, copied-package execution, read-only consultation,
project OKF regeneration, repository tests, and the application coverage gate.
