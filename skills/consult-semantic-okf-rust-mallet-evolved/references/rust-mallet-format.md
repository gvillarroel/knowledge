# RustMallet Snapshot Contract

The projection is non-authoritative and contains exactly seven regular files under `classical/`: index, documents, references, lexicon, associations, topics, and build report.

The index binds the complete plan, `pyrmallet==0.1.1` algorithm identity, selected source inventory, pre-classical core tree, authoritative ledger, and every derived artifact hash. Inspection validates the passing semantic build report, recomputes the core tree and lexicon, checks every document identity and exact locator, checks RustMallet topic probabilities and association schemas, and verifies the build report against live fingerprints. Deep validation retrains the fixed-seed model and requires byte-equivalent derived data.

A document is an exact record or character-range passage. Preserve `source_id`, `record_id`, `record_sha256`, `concept_id`, `concept_type`, `concept_path`, `source_path`, `paper_id`, `ordinal`, `locator`, and `text_sha256` when carrying evidence into an answer workflow.

`classical/references.json` is the canonical processed reference dictionary. It
maps a deterministic 96-bit `ref-...` identifier to one `document_id` and the
seven exact answer-evidence fields. The classical index and build report bind
its bytes, SHA-256 digest, and count. Validation independently regenerates the
entire map from `documents.jsonl` and rejects missing, extra, duplicate, stale,
colliding, or manually edited bindings.

Corrupt or stale declared artifacts always stop consultation. There is no fallback to an unvalidated lexical scan.
