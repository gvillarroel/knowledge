# Classical Projection Format

## Authority

The `classical/` tree is derived discovery data. It does not define record identity, accepted RDF facts, ontology meaning, provenance, shapes, or validation results.

## Closed artifacts

The directory contains exactly `index.json`, `documents.jsonl`, `lexicon.json`, `associations.jsonl`, `topics.json`, and `build-report.json`. All are regular non-symlink files.

Each document row contains one exact passage plus source, record, concept ID and type, source-path, paper, ordinal, text-digest, title/body term counts, lengths, and topic weights. A locator is exactly `{"kind":"record"}` or `{"kind":"character-range","start":N,"end":M}`.

The index includes the full closed plan and its canonical SHA-256, fixed algorithm identities, selected source inventory, authoritative pre-classical tree and ledger hashes, artifact paths/bytes/hashes/counts, and summary counts. Its dependency graph is acyclic because the core tree digest excludes `classical/`.

Validation re-derives documents, lexicon, associations, topics, and topic weights from the authoritative ledger and embedded plan. A raw artifact hash alone is not sufficient. The build report must equal the live validation summary and artifact fingerprints.
