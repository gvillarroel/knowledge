# Tika and MALLET Build Contract

## Experimental scope

This package is an evaluation candidate, not a production promotion. Apache Tika
`4.0.0-beta-1` is a preview release. Use this skill when the task explicitly asks
to test that release or compare its extraction behavior; keep stable production
pipelines on their accepted runtime until separate evidence supports promotion.

The supported external runtime is closed:

- Java 17 or later;
- the unpacked Tika application distribution whose root contains
  `tika-app-4.0.0-beta-1.jar` and its `lib/` and `plugins/` trees; and
- the unpacked MALLET `2.1.0` binary distribution whose `lib/` contains
  `mallet-2.1.0.jar`.

Pass all three paths explicitly. The skill never downloads prerequisites, searches
`PATH`, consults a user cache, or accepts a different release implicitly.

## Ingestion plan

The ingestion plan has exactly four root members:

```json
{
  "schema_version": "1.0",
  "bundle": {
    "title": "Format experiment",
    "description": "Tika extraction and MALLET topic experiment.",
    "base_iri": "https://example.org/format-experiment/",
    "ontology_iri": "https://example.org/ontology/format-experiment",
    "version_iri": "https://example.org/ontology/format-experiment/1.0.0",
    "prefix": "formatx",
    "owl_profile": "rl"
  },
  "sources": [
    {
      "id": "office-documents",
      "path": "inputs/*.xlsx",
      "concept_type": "Office Document"
    }
  ],
  "tika": {
    "version": "4.0.0-beta-1",
    "verify_default_markdown": true,
    "timeout_seconds": 120,
    "max_input_bytes": 104857600
  }
}
```

Source paths are plan-relative portable glob patterns. They may not be absolute,
contain `..`, or name a URL. Each source must match at least one regular,
non-symlink file. Symbolic links and Windows reparse points in any existing path
component are rejected before resolution. Source IDs are stable evidence
partitions and must be unique.

For every file, the builder reads the raw bytes once into a private snapshot while
computing the persisted hash and size. It rejects an identity or metadata change
during that copy, then runs Tika only against the snapshot: with the beta's default
handler, with explicit `--md`, and with `--json`. Default and explicit Markdown must
be byte-equal after newline and Unicode normalization. Empty text, missing media
type, invalid JSON metadata, a timeout, or any mismatch aborts the entire atomic
build.

The builder generates a fixed `ExtractedDocument` ontology and SHACL contract. The
raw input hash and size, detected media type, Tika version, metadata hash, handler
identity, extracted-body hash, and source locator become authoritative ledger
attributes. Tika metadata itself remains under `tika/metadata/` as bound provenance.

## Retrieval plan

The retrieval plan is closed and selects source IDs explicitly. Its `topics` object
uses these Java MALLET fields:

- `topic_count`, `num_iterations`, and `num_icm_iterations`;
- `num_threads`, which must equal `1`;
- `optimize_interval` and `optimize_burn_in`;
- `alpha_sum`, `beta`, and a positive signed-32-bit `random_seed`;
- `min_document_frequency`, `max_document_fraction`, and `top_terms`; and
- `timeout_seconds`.

The remaining tokenization, BM25, association, expansion, and reranking sections
use explicit values and reject unknown members. Vocabulary filtering happens before
MALLET so the persisted lexicon and model corpus are independently reproducible.

MALLET is considered successful only when its process succeeds, emits no known CLI
or runtime error marker, and creates all four non-empty outputs: topic keys,
document topics, topic-word weights, and word-topic counts. Parsers verify document
order, vocabulary coverage, probability sums, topic identities, and the relationship
between sparse assignment counts and topic-word weights.

The Java classpath is the explicit ordered list from the hash-bound `lib/*.jar`
inventory, never a wildcard. The executable, MALLET home, and complete jar tree are
rechecked immediately around every Java invocation. A post-preflight change is a
hard failure.

## Authority

`concepts/`, `semantic/records.jsonl`, and purpose-selected RDF graphs are the
authoritative OKF layers. The `classical/` documents, topics, PPMI edges, scores,
and ranks are replaceable discovery aids. Do not write MALLET topic labels into the
ontology or present them as facts.
