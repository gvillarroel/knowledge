---
name: build-semantic-okf-rust-mallet-evolved
description: Build and independently validate an atomic Semantic OKF/RDF snapshot plus a non-authoritative retrieval projection with a compact exact-evidence reference dictionary, RustMallet sparse-Gibbs LDA, Bag of Words, Okapi BM25, PPMI query expansion, and diversity-aware reranking. Use for fixed-seed local probabilistic topics or reference-resolvable RustMallet knowledge releases. This standalone skill owns construction only and never answers from a published snapshot.
---

# Build Semantic OKF RustMallet Evolved

Build one authoritative Semantic OKF core and one local RustMallet discovery
projection as a single validated release. Keep passages, lexical statistics,
probabilistic topics, associations, and compact evidence references outside the
ledger and RDF graphs.

## Standalone and authority boundary

- Use only this directory's instructions, scripts, references, and requirements.
- Treat the manifest, sources, plan, and absent destination as explicit inputs.
- Never import a sibling skill, repository helper, evaluator, or prebuilt knowledge.
- Own source processing, derivation, validation, and atomic publication.
- Never answer, cite, search, or synthesize from the published snapshot.
- Treat `classical/` as non-authoritative discovery data.

## Exact build protocol

When the manifest and RustMallet plan are already supplied:

1. Do not inspect helper source, list the skill, invoke help, rewrite the manifest
   or plan, or manually repair the output.
2. Install `scripts/requirements.txt` only if `pyrmallet` is unavailable.
3. Run exactly one build-and-validate command. It builds into a private sibling,
   derives and binds all seven classical artifacts, validates the complete release
   independently, and publishes once. Continue only when its JSON status is
   `pass`.
4. Hand the exact published path to the requested consult skill read-only. Do not
   change the release after validation.

```bash
SKILL_DIR="$HOME/.agents/skills/build-semantic-okf-rust-mallet-evolved"
python -B "$SKILL_DIR/scripts/build_validate_semantic_okf_rust_mallet.py" \
  MANIFEST RUST_MALLET_PLAN ABSENT_OUTPUT
```

For a new or changed source contract, read
[source-combination.md](references/source-combination.md),
[manifest.md](references/manifest.md), and
[coherence-contract.md](references/coherence-contract.md). For a new or changed
retrieval plan, also read [rust-mallet-plan.md](references/rust-mallet-plan.md),
[rust-mallet-format.md](references/rust-mallet-format.md), and
[python-runtime.md](references/python-runtime.md).

## Published contract

A successful release contains the complete authoritative core and exactly seven
regular, non-symlink classical files:

```text
classical/
  index.json
  documents.jsonl
  references.json
  lexicon.json
  associations.jsonl
  topics.json
  build-report.json
```

`references.json` binds one deterministic `ref-[0-9a-f]{24}` ID to every
document's exact source ID, record ID, concept path, source path, record digest,
locator, and text digest. The index and build report hash-bind that dictionary.
Validation re-derives the dictionary, documents, lexical statistics, PPMI
neighbors, fixed-seed RustMallet topics, and document-topic weights from the
authoritative core and closed plan.

## Completion gate

Before delivery, confirm that:

- the one command returned `status: pass`;
- the requested output is the only published release;
- the closed artifact set contains all seven files and no unknown file;
- every document has exactly one re-derived compact reference ID;
- index and build-report fingerprints match live artifacts;
- the validator reported no error or warning; and
- the snapshot was not changed after validation.
