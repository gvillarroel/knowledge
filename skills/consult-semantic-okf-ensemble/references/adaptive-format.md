# Adaptive Snapshot Contract

The projection is non-authoritative and contains exactly seven regular files under
`adaptive/`: index, documents, answer bindings, lexicon, associations, topics, and
build report.

The index binds the complete plan, fixed algorithm identities, selected source inventory, pre-adaptive core tree, authoritative ledger, and every derived artifact hash. Inspection validates the passing semantic build report, recomputes the core tree and lexicon, checks every document identity and exact locator, checks the topic and association schemas, and verifies the build report against live fingerprints.

A document is an exact record or character-range passage. Preserve `source_id`,
`record_id`, `record_sha256`, `concept_id`, `concept_type`, `concept_path`,
`source_path`, optional `paper_id`, `ordinal`, `locator`, and `text_sha256` when
carrying evidence into an answer workflow. A null paper ID is normal for source-generic
records and must not trigger path- or prefix-based inference.

Corrupt or stale declared artifacts always stop consultation. There is no fallback to an unvalidated lexical scan.

Every search route emits `evidence_rows` using `exact-authoritative-fields-v2`. Each row copies the selected source, record, concept, source path, locator, hashes, and evidence text. The adapter does not infer or normalize an identity.

Ensemble schema `2.0` resolves each row only through its exact
`(source_id, record_id, record_sha256)` crosswalk key and normalizes its locator to an
explicit authoritative `record-body` character range. The adaptive projection itself
remains unchanged and independently valid.
