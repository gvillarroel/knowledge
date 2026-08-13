---
name: build-semantic-okf-rust-mallet-evolved
description: Build and independently validate an atomic Semantic OKF/RDF snapshot plus a non-authoritative retrieval projection with RustMallet sparse-Gibbs LDA, Bag of Words, Okapi BM25, PPMI query expansion, and diversity-aware reranking. Use when Codex needs fixed-seed probabilistic topics without embeddings or hosted model calls, or needs to compare RustMallet against deterministic classical topic communities. This standalone skill owns construction only and never answers from a published snapshot.
---

# Build Semantic OKF RustMallet Evolved

Build one authoritative Semantic OKF core and one local RustMallet discovery projection as a single validated release. Keep passages, lexical statistics, probabilistic topics, and association edges outside the ledger and RDF graphs.

## Standalone and authority boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the manifest, sources, plan, and destination as explicit user inputs.
- Do not import or execute a sibling skill, repository helper, evaluation fixture, or root document.
- Own source processing, core materialization, classical derivation, validation, and atomic publication.
- Do not search, answer, compare claims, cite, or synthesize from a published snapshot.
- Treat `classical/` as non-authoritative discovery data. Keep `concepts/`, `semantic/records.jsonl`, and purpose-selected RDF graphs authoritative.

## Required references

- Read [source-combination.md](references/source-combination.md) before combining physical sources.
- Read [manifest.md](references/manifest.md) before writing or changing the Semantic OKF manifest.
- Read [coherence-contract.md](references/coherence-contract.md) before changing mappings or validation.
- Read [rust-mallet-plan.md](references/rust-mallet-plan.md) before selecting sources or training parameters.
- Read [rust-mallet-format.md](references/rust-mallet-format.md) before reviewing or diagnosing derived artifacts.
- Read [python-runtime.md](references/python-runtime.md) before installing or running the package.

## Workflow

1. Define the source authority, exact physical input set, competency questions, and evidence identities.
2. Inspect source identifiers, schemas, encodings, and mappings; write the closed Semantic OKF manifest.
3. Write a closed RustMallet plan. Select source IDs explicitly and pin tokenizer, n-grams, BM25, association, sparse-Gibbs LDA, expansion, and reranking parameters.
4. Install only `scripts/requirements.txt`. It pins `pyrmallet==0.1.1`; training is local and requires no model download or hosted request.
5. Build into a new output path. The command creates the authoritative core, derives exact page or record passages, validates every binding, and publishes with one final rename.
6. Run the independent validator against the published output.
7. Rebuild unchanged inputs and plan into another absent path; require identical sorted path-and-byte hashes.
8. Open representative returned locators and verify that they resolve to exact authoritative text.

Never accept unknown plan members, implicit defaults, partial source selection, stale hashes, unsafe paths, approximate locators, non-deterministic output, or topics presented as ontology truth.

## Build and validate

Run from this skill directory, or prefix scripts with the copied skill root:

```bash
python scripts/build_semantic_okf_rust_mallet.py manifest.json rust-mallet-plan.json semantic-okf-rust-mallet --concept-layout source-packed-v1 --output-format json
python scripts/validate_semantic_okf_rust_mallet.py semantic-okf-rust-mallet --output-format json
```

The destination must not exist. A successful release contains the complete core and exactly six classical files:

The recommended source-packed layout combines repeated CSV, JSON, and RDF
records into one authoritative Markdown collection per source. Logical concept
paths, ledger records, evidence locators, reference IDs, and RustMallet
ranking content remain record-specific. Core-bound indexes, reports, and
reference dictionaries are regenerated for the new physical tree.

```text
semantic-okf-rust-mallet/
  index.md
  concepts/
  semantic/
  classical/
    index.json
    documents.jsonl
    lexicon.json
    associations.jsonl
    topics.json
    build-report.json
```

`documents.jsonl` uses exact full-record or character-range locators. `lexicon.json` persists Bag-of-Words, document-frequency, corpus-frequency, inverse-document-frequency, and BM25 length statistics. `associations.jsonl` persists bounded positive-PMI neighbors. `topics.json` persists RustMallet topic-word probabilities, a deterministic argmax term mapping, and document-topic distributions. The index binds all four artifacts to the authoritative tree, selected inputs, complete plan, and `pyrmallet==0.1.1` algorithm identity.

## Completion gate

Before delivery, confirm:

- the package-local runtime smoke passes;
- every requested source is eligible and every exclusion is explicit;
- core and classical validation pass without warning;
- the closed artifact set contains no symlink or unknown file;
- every document binds to one record, concept, source path, text hash, and exact locator;
- token counts, BM25 statistics, PPMI neighbors, fixed-seed RustMallet topics, and document-topic weights reproduce from authoritative text;
- build-report and index hashes match the live artifacts;
- failure leaves no destination or private candidate;
- two clean builds are byte-identical; and
- representative page and claim passages have been manually opened and verified.
