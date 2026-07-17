---
name: build-semantic-okf-classical
description: Build and independently validate an atomic Semantic OKF/RDF snapshot plus a deterministic, non-authoritative classical text-retrieval projection. Use when Codex needs Bag of Words, Okapi BM25, corpus lexical statistics, co-occurrence topic communities, PPMI query expansion, or diversity-aware retrieval without embeddings or model downloads. This standalone skill owns construction only and never answers from a published snapshot.
---

# Build Semantic OKF Classical

Build one authoritative Semantic OKF core and one model-free classical discovery projection as a single validated release. Keep passages, term statistics, topic communities, and association edges outside the ledger and RDF graphs.

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
- Read [classical-plan.md](references/classical-plan.md) before selecting sources or text-processing parameters.
- Read [classical-format.md](references/classical-format.md) before reviewing or diagnosing derived artifacts.
- Read [python-runtime.md](references/python-runtime.md) before installing or running the package.

## Workflow

1. Define the source authority, exact physical input set, competency questions, and evidence identities.
2. Inspect source identifiers, schemas, encodings, and mappings; write the closed Semantic OKF manifest.
3. Write a closed classical plan. Select source IDs explicitly and pin tokenizer, n-grams, BM25, association, topic, expansion, and reranking parameters.
4. Install only `scripts/requirements.txt`. The classical layer uses the Python standard library and requires no model or network access.
5. Build into a new output path. The command creates the authoritative core, derives exact page or record passages, validates every binding, and publishes with one final rename.
6. Run the independent validator against the published output.
7. Rebuild unchanged inputs and plan into another absent path; require identical sorted path-and-byte hashes.
8. Open representative returned locators and verify that they resolve to exact authoritative text.

Never accept unknown plan members, implicit defaults, partial source selection, stale hashes, unsafe paths, approximate locators, non-deterministic output, or topics presented as ontology truth.

## Build and validate

Run from this skill directory, or prefix scripts with the copied skill root:

```bash
python scripts/build_semantic_okf_classical.py manifest.json classical-plan.json semantic-okf-classical --output-format json
python scripts/validate_semantic_okf_classical.py semantic-okf-classical --output-format json
```

The destination must not exist. A successful release contains the complete core and exactly six classical files:

```text
semantic-okf-classical/
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

`documents.jsonl` uses exact full-record or character-range locators. `lexicon.json` persists Bag-of-Words, document-frequency, corpus-frequency, inverse-document-frequency, and BM25 length statistics. `associations.jsonl` persists bounded positive-PMI neighbors. `topics.json` persists deterministic seeded weighted-label-propagation communities. The index binds all four artifacts to the authoritative tree, selected inputs, and complete plan.

## Completion gate

Before delivery, confirm:

- the package-local runtime smoke passes;
- every requested source is eligible and every exclusion is explicit;
- core and classical validation pass without warning;
- the closed artifact set contains no symlink or unknown file;
- every document binds to one record, concept, source path, text hash, and exact locator;
- token counts, BM25 statistics, PPMI neighbors, topics, and document-topic weights reproduce from authoritative text;
- build-report and index hashes match the live artifacts;
- failure leaves no destination or private candidate;
- two clean builds are byte-identical; and
- representative page and claim passages have been manually opened and verified.
