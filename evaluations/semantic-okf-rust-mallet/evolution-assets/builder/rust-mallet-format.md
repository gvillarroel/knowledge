# RustMallet Projection Format

## Authority

The `classical/` tree is derived discovery data. It does not define record identity, accepted RDF facts, ontology meaning, provenance, shapes, or validation results.

## Closed artifacts

The directory contains exactly `index.json`, `documents.jsonl`, `references.json`, `lexicon.json`, `associations.jsonl`, `topics.json`, and `build-report.json`. All are regular non-symlink files.

Each document row contains one exact passage plus source, record, concept ID and type, source-path, paper, ordinal, text-digest, title/body term counts, lengths, and topic weights. A locator is exactly `{"kind":"record"}` or `{"kind":"character-range","start":N,"end":M}`.

`references.json` is a closed, sorted dictionary from compact IDs matching `ref-[0-9a-f]{24}` to one document ID and its seven exact evidence fields: source ID, record ID, concept path, source path, record SHA-256, locator, and text SHA-256. Each ID is the first 96 bits of the SHA-256 of canonical JSON for those evidence fields. Validation requires exact equality with deterministic derivation, so stale IDs, collisions, duplicate document bindings, and modified evidence fail closed.

The index includes the full closed plan and its canonical SHA-256, fixed algorithm identities, selected source inventory, authoritative pre-classical tree and ledger hashes, artifact paths/bytes/hashes/counts, and summary counts. Its dependency graph is acyclic because the core tree digest excludes `classical/`.

`topics.json` identifies `pyrmallet-0.1.1-sparse-gibbs-lda-v1`, persists ranked topic-word probabilities, and assigns each retained term to its strongest topic for deterministic query expansion. Document rows persist RustMallet document-topic probabilities.

Validation re-derives documents, the complete reference dictionary, lexicon, associations, fixed-seed RustMallet topics, and topic weights from the authoritative ledger and embedded plan. A raw artifact hash alone is not sufficient. The build report must equal the live validation summary and artifact fingerprints.
