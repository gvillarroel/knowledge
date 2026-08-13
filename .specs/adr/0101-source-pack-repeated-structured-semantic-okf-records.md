---
adr: "0101"
title: "ADR 0101: Source-Pack Repeated Structured Semantic OKF Records"
summary: "Render repeated CSV, JSON, and RDF records as one anchored OKF collection per source while preserving the authoritative record ledger and retrieval behavior."
status: "Accepted"
date: "2026-08-12"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Materialization"
tags: [knowledge, semantic-okf, compaction, retrieval, provenance]
---

# ADR 0101: Source-Pack Repeated Structured Semantic OKF Records

## Status

Accepted.

## Context

The Semantic OKF builders rendered every normalized record as a separate
Markdown concept. This was appropriate for prose sources, where one input file
normally represents one substantive document, but inefficient for repeated
structured rows. The GraphRAG evaluation bundle contained 874 logical records:
15 paper documents, 28 vocabulary records, and 831 claim records. The old
layout produced 874 concept files, 859 of which were smaller than 4 KiB. Their
repeated frontmatter occupied 1,115,328 bytes, or 38.07 percent of all concept
Markdown bytes.

Deleting short records or deduplicating semantically similar claims would
reduce file count but would also remove reviewed evidence, provenance, or
retrieval candidates. The GraphRAG inventory contained no empty normalized
record that could be removed without changing the authoritative corpus.

Open Knowledge Format 0.2 defines a concept as one Markdown document and
permits free structural Markdown in its body. It does not require every
normalized row from a structured source to become an independent physical
document. This permits one source-level collection concept with stable anchors
for its complete records.

## Decision

- Add the versioned physical layout `source-packed-v1` alongside the compatible
  `record-per-file-v1` layout.
- Make `source-packed-v1` the standard layout in all canonical builder skill
  instructions. Keep the explicit legacy layout available for migration,
  comparison, and existing callers.
- Pack records only when a CSV, JSON, or RDF source produces more than one
  normalized record. Keep prose and single-record sources one document per
  record.
- Render one collection under `concepts/<source_id>.md`. Repeat source-level
  frontmatter once and render every complete record body under an anchor
  derived from the first 16 hexadecimal characters of its authoritative
  `record_sha256`.
- Preserve every logical `source_id`, `record_id`, `concept_id`,
  `concept_path`, body, record hash, source binding, RDF assertion, and
  provenance statement in the authoritative ledger and semantic graphs.
  Logical record paths remain stable locators; the declared layout resolves
  them to physical collection documents.
- Teach refresh, validation, projection builders, and consultation adapters to
  resolve both layouts. A compact-bundle evidence check must verify the safe
  physical path, the hash-derived anchor, and the exact authoritative body. It
  must not treat a merely existing collection as sufficient.
- Keep retrieval projections independent of physical materialization. When a
  Graphify projection would otherwise parse packed collection structure, rebuild
  the exact record-per-file Markdown inputs in memory from the ledger and
  semantic plan. Do not materialize the expanded documents, and require graph
  byte parity with the record-per-file build before accepting the compact path.
- Do not delete short or metadata-heavy records solely because of size. A
  record may be removed only under an independent semantic-content decision
  with its own quality evaluation.
- Keep completed frozen evaluation studies immutable. Their verification must
  check the files against the digests recorded inside the frozen manifest, not
  regenerate them from whichever builder sources happen to be current. A new
  builder baseline requires a new append-only study version.

The authoritative ledger remains granular because retrieval, provenance, and
record-level locators consume that granularity. Compaction changes physical
materialization, not the evidence population.

## Alternatives considered

### Delete short documents

Rejected. File size did not identify semantic emptiness, and the tested corpus
had no empty normalized records. Deletion would reduce recall and provenance
coverage.

### Trim frontmatter but retain one file per record

Rejected as the primary solution. It saves bytes but leaves filesystem entry
count, traversal cost, and repeated YAML parsing almost unchanged.

### Build one monolithic bundle document

Rejected. It discards useful source boundaries, creates an unnecessarily large
edit and validation unit, and makes targeted inspection less efficient.

### Deduplicate semantically similar records

Rejected. Similarity is not identity; merging reviewed claims changes evidence
and requires a separate quality-controlled semantic mutation.

### Source-level collections for repeated structured records

Accepted. Source identity is already deterministic and provenance-bearing, and
the collection can preserve every record body and locator without multiplying
source metadata.

## Validation evidence

The controlled A/B used the canonical GraphRAG input, current scripts,
identical dependency versions, identical plans, and the same consultation code.
The physical layout was the only builder variable.

| Measure | Record per file | Source packed | Change |
|---|---:|---:|---:|
| Logical records | 874 | 874 | 0 |
| Concept Markdown files | 874 | 31 | -96.45% |
| Total bundle files | 884 | 41 | -95.36% |
| Concept Markdown bytes | 2,929,939 | 1,887,513 | -35.58% |
| Frontmatter bytes | 1,115,328 | 33,597 | -96.99% |
| Total bundle bytes | 11,024,180 | 9,847,299 | -10.68% |
| Concept files below 4 KiB | 859 | 0 | -100% |

The `records.jsonl`, source manifest, data graph, ontology, shapes, provenance,
and validation report remained byte-identical. Classical documents, lexicon,
topics, and associations, and embedding chunks and vectors also remained
byte-identical; only layout-bound reports and index fingerprints changed.

The 40-question retrieval comparison covered eight routes: legacy lexical,
new lexical, vector, hybrid, BM25, topic, association, and classical fusion.
All aggregate metrics were exactly equal. Every per-question ranked hit was
identical, with zero query mismatches and zero hit mismatches. Each route
validated 400 of 400 retained evidence hits against the appropriate physical
document, for 3,200 of 3,200 valid hits overall.

The compact builder and consultation path also passed the legacy, adaptive,
classical, embeddings, ensemble, entity-graph, Graphify, and Turso GraphRAG
families. The Astro corpus stayed at 416 records and 416 concepts, and the
quantum-error-correction corpus stayed at 15 and 15, demonstrating that prose
sources are not collapsed. The canonical dataset registry validated all
registered datasets and all eight strategy families. Generated GraphRAG
`build-consult` and compact `consult-only` task sets each passed deterministic
regeneration, leakage checks, and all 40 mechanical oracle gates.

An extension on 2026-08-13 applied the same layout contract to the remaining
specialized builders and consultation adapters:

| Specialized bundle | Record-per-file files | Source-packed files | Reduction | Quality gate |
|---|---:|---:|---:|---|
| Graphify Next | 886 | 43 | 95.15% | 0/40 ranking mismatches; 400/400 evidence hits |
| Harbor Graphify | 886 | 43 | 95.15% | 0/40 ranking mismatches; 400/400 evidence hits |
| Tantivy | 890 | 47 | 94.72% | 0/40 ranking mismatches; 400/400 evidence hits |
| Rust + MALLET | 891 | 48 | 94.61% | exact metrics on four routes; 1,598/1,598 evidence hits |

Graphify required an additional storage-independent projection rule. Directly
parsing packed collections changed six of forty rankings and reduced source-level
MRR and nDCG, so that implementation was rejected. Extracting only temporary
record views also reduced source-level early-rank metrics and was rejected. The
accepted implementation reconstructs legacy-equivalent Markdown in memory and
passes it through the pinned Graphify Markdown extractor. Both Graphify variants
then produced graph bytes identical to their record-per-file baselines, exact
aggregate metrics, and identical per-question rankings without publishing or
temporarily materializing the expanded concept tree.

The Tantivy documents, lexicon, associations, and topics were byte-identical
across layouts. The Rust documents, lexicon, associations, topics, and reference
dictionary were byte-identical; only the layout-bound index changed. Its BM25,
association, fusion, and topic routes retained their complete rankings and exact
metrics. Rust-evolved uses the same compact core and its frozen consultant was
the consultation implementation exercised by that four-route comparison.

The Tika-integrated GraphRAG path normalizes Tika extractions as substantive
Markdown documents, so it correctly remained at one physical concept per input
and gained no artificial file-count reduction. Its underlying Semantic OKF core
and all Tika, bounded-Tika, and Tika-Tantivy consultants nevertheless support
source-packed CSV, JSON, and RDF inputs; controlled two-record fixtures verified
one collection, unchanged semantic artifacts, exact anchors and bodies, and
fail-closed tamper rejection. This preserves the rule that prose must not be
collapsed merely to improve a file-count metric.

## Consequences

Positive:

- repeated structured metadata is paid once per source rather than once per
  record;
- file traversal, Markdown parsing, and artifact transfer operate on far fewer
  filesystem entries;
- record-level retrieval and provenance remain intact;
- corpora composed of substantive prose documents retain their existing
  physical granularity;
- compact and legacy bundles remain readable by the same consultation skills.

Negative:

- consumers may no longer assume that every logical ledger `concept_path`
  names a physical file in a compact bundle;
- consumers must honor `processor.concept_layout` and resolve a collection
  document before opening evidence;
- collection documents are larger change units than individual structured
  rows, although record hashes and anchors still identify exact sections;
- the compatibility layout and dual-layout tests remain necessary during the
  migration period.

## References

- [Open Knowledge Format 0.2 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [Google Cloud introduction to Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
