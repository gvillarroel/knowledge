# Adaptive Projection Format

## Authority

The `adaptive/` tree is derived discovery data. It does not define record identity, accepted RDF facts, ontology meaning, provenance, shapes, or validation results.

## Closed artifacts

The directory contains exactly `index.json`, `documents.jsonl`, `answer-bindings.jsonl`, `lexicon.json`, `associations.jsonl`, `topics.json`, and `build-report.json`. All are regular non-symlink files.

Each document row contains one exact passage plus source, record, concept ID and type,
source path, optional paper identity, ordinal, text digest, title/body term counts,
lengths, and topic weights. A null paper identity is valid for source-generic records.
A locator is exactly `{"kind":"record"}` or
`{"kind":"character-range","start":N,"end":M}`.

Each answer-binding row is a deterministic, non-authoritative projection of one reviewed record with unambiguous page evidence. It keeps the record and concept identities, claim-source path, paper identity, reviewed interpretation, exact evidence-source paths, canonical string locator tokens such as `PDF-page-7`, integer citation pages such as `7`, and their hashes. Those two page representations are intentionally distinct. The builder emits no row when any source fragment is malformed, the mapped paper identity differs, or the referenced `## PDF page N` heading is absent.

The index includes the full closed plan and its canonical SHA-256, fixed algorithm identities, selected source inventory, authoritative pre-adaptive tree and ledger hashes, artifact paths/bytes/hashes/counts, and summary counts. Its dependency graph is acyclic because the core tree digest excludes `adaptive/`.

Validation re-derives documents, answer bindings, lexicon, associations, topics, and topic weights from the authoritative ledger and embedded plan. A raw artifact hash alone is not sufficient. The build report must equal the live validation summary and artifact fingerprints.

The index also pins `protected-full-query-plus-aspect-rrf-v2`, `exact-authoritative-fields-v2`, `verified-pdf-page-bindings-v1`, and `record-level-adaptive-fusion-v1`. They define query-time aspect fusion, exact search-result evidence rows, verified answer bindings, and claim-preserving answer-evidence ranking respectively. None adds domain facts to the core.
