# Tika and MALLET Snapshot Integrity

## Authority layers

The snapshot has three distinct roles:

1. `concepts/`, `semantic/records.jsonl`, and purpose-selected RDF graphs are
   authoritative knowledge.
2. `tika/` is a provenance receipt for extraction: it binds raw source hashes,
   canonical metadata, generated Markdown, the Tika beta runtime, and ledger records.
3. `classical/` is non-authoritative retrieval data derived from authoritative text.
4. Tantivy is an ephemeral query engine over validated `classical/documents.jsonl`;
   no Tantivy index is part of the published snapshot.

Never promote a MALLET topic, PPMI association, Tantivy score, rank, or fusion value
into a factual claim. Use it to find a passage, then verify the claim in a concept,
ledger record, or RDF graph appropriate to the question.

## Closed Tika receipt

`tika/` contains exactly `index.json`, `documents.jsonl`, `extracted/`, and
`metadata/`. Its index binds the ingestion plan, Java version, Tika
`4.0.0-beta-1`, every JAR digest, artifact hashes, and directory inventories.

Every document row binds one source locator and raw hash to one metadata object and
one Markdown source. Generated YAML frontmatter repeats the raw hash and size,
detected media type, Tika version and handler, metadata hash, body hash, locator,
and title. Those values must equal the corresponding authoritative ledger record.

The normal handler identity means the persisted body is Tika Markdown whose
implicit and explicit Markdown invocations agreed. The hybrid algorithm may also
contain a source declared as `utf8-verbatim-tika-verified`. For that source, handler
`utf8-verbatim-tika-metadata-verified-v1` means Tika verified metadata and a textual
media type, while the persisted authoritative body is strict UTF-8 raw text with
only CRLF/CR normalized to LF. Its generated Semantic source mapping must declare
`body_normalization: line-endings-only`. Do not reinterpret this handler as a
claim that Tika rendered the body.

The bundle intentionally omits the raw binary source. The persisted raw hash proves
identity but does not allow the consultant to recreate extraction. Re-extraction is
a new build task and is outside this read-only skill.

## Closed MALLET projection

`classical/` contains exactly `index.json`, `documents.jsonl`, `lexicon.json`,
`associations.jsonl`, `topics.json`, and `build-report.json`. Its index binds the
authoritative core inventory, selected source hashes, complete retrieval plan,
MALLET `2.1.0` and Java identity, every MALLET JAR digest, artifact hashes, and
counts.

Ordinary inspection checks the closed schemas, paths, hashes, lexical statistics,
locators, topic shapes, Tika parity, and build reports without requiring Java.
Deep inspection additionally requires the exact bound MALLET distribution and a
Java 17-or-later executable. It rederives passages, BM25 statistics, and PPMI edges,
then retrains fixed-seed one-thread MALLET in fresh temporary storage disjoint from
both the bundle and MALLET home. The bundle remains read-only.

## Failure conditions

Stop instead of searching when inspection finds any of the following:

- a symbolic link, unsafe path, missing file, or unknown file in a closed area;
- a stale raw, metadata, Markdown, body, concept, record, artifact, or tree hash;
- a Tika plan, generated Semantic plan, ledger attribute, or source identity mismatch;
- a MALLET toolchain, plan, algorithm, vocabulary, topic, or document-order mismatch;
- a locator that does not resolve exactly to authoritative text; or
- a non-passing Semantic OKF or projection build report.

Do not repair the snapshot in place. Report the exact failed binding, preserve the
immutable evidence, and state that rebuilding is outside this standalone
consultation skill's scope.
