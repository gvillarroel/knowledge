---
type: Agent Skill
title: Build Semantic OKF with Tantivy
description: Build and independently validate an atomic Semantic OKF/RDF snapshot
  plus the deterministic, non-authoritative classical projection consumed by the frozen
  Tantivy BM25 consultant. Use when Codex must construct, reproduce, diagnose, or
  optimize a snapshot specifically for consult-semantic-okf-tantivy without modifying
  the frozen consultation skill. This standalone skill owns construction only and
  never answers from a published snapshot.
tags:
- codex
- skill
skill_name: build-semantic-okf-tantivy
source_path: skills/build-semantic-okf-tantivy/SKILL.md
---

# Build Semantic OKF for Tantivy

Build one authoritative Semantic OKF core and one deterministic lexical
projection as a single validated release. The projection remains named
`classical/` because that closed contract is what the frozen Tantivy consultant
validates and indexes.

## Frozen-consumer boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the manifest, sources, plan, and absent destination as explicit inputs.
- Do not import or execute a sibling skill, repository helper, evaluation
  fixture, or root document.
- Do not modify `consult-semantic-okf-tantivy` while changing or evaluating this
  builder.
- Require the consumer tree digest recorded by the active freeze receipt before
  attributing a retrieval result to this builder.
- Own source processing, core materialization, lexical derivation, validation,
  and atomic publication.
- Never search, answer, compare claims, cite, or synthesize from a published
  snapshot.
- Treat `classical/` as non-authoritative discovery data. Keep `concepts/`,
  `semantic/records.jsonl`, and purpose-selected RDF graphs authoritative.

## Required references

- Read [source-combination.md](../../skills/build-semantic-okf-tantivy/references/source-combination.md) before combining physical sources.
- Read [manifest.md](../../skills/build-semantic-okf-tantivy/references/manifest.md) before writing or changing the Semantic OKF manifest.
- Read [coherence-contract.md](../../skills/build-semantic-okf-tantivy/references/coherence-contract.md) before changing mappings or validation.
- Read [classical-plan.md](../../skills/build-semantic-okf-tantivy/references/classical-plan.md) before selecting sources or text-processing parameters.
- Read [classical-format.md](../../skills/build-semantic-okf-tantivy/references/classical-format.md) before changing any artifact consumed by Tantivy.
- Read [tantivy-consumer-contract.md](../../skills/build-semantic-okf-tantivy/references/tantivy-consumer-contract.md) before builder evolution or evaluation.
- Read [python-runtime.md](../../skills/build-semantic-okf-tantivy/references/python-runtime.md) before installing or running the package.

## Workflow

1. Freeze the exact consumer receipt and verify its live skill tree before
   creating a builder candidate.
2. Define source authority, physical inputs, competency questions, and evidence
   identities.
3. Inspect source identifiers, schemas, encodings, and mappings; write the
   closed Semantic OKF manifest.
4. Write a closed lexical plan. Select source IDs and pin tokenizer, n-grams,
   BM25, association, topic, expansion, and reranking parameters.
5. Install only `scripts/requirements.txt`.
6. Build into a new output path. The command creates the authoritative core,
   derives exact page or record passages, validates every binding, and publishes
   with one final rename.
7. Run the independent validator against the published output.
8. Rebuild unchanged inputs and plan into another absent path; require
   identical sorted path-and-byte hashes.
9. Run the frozen Tantivy consultant only after construction validation passes.
10. Open representative returned locators and verify exact authoritative text.

Never accept unknown plan members, implicit defaults, partial source selection,
stale hashes, unsafe paths, approximate locators, non-deterministic output, or
topics presented as ontology truth.

## Build and validate

Run from this skill directory, or prefix scripts with the copied skill root:

```bash
python scripts/build_semantic_okf_tantivy.py manifest.json plan.json semantic-okf-tantivy --output-format json
python scripts/validate_semantic_okf_tantivy.py semantic-okf-tantivy --output-format json
```

The destination must not exist. A successful release contains the complete core
and exactly six consumer-facing projection files:

```text
semantic-okf-tantivy/
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

`documents.jsonl` uses exact full-record or character-range locators. Long
non-paper records retain the complete record and may add one exact overview
before their first level-two heading.
`lexicon.json` supplies the frozen consultant's natural-query unigram
vocabulary. The plan's `candidate_pool` and `max_per_evidence_identity` control
the frozen consultant's bounded native search and result diversification.

## Completion gate

Before delivery, confirm:

- the package-local runtime smoke passes;
- the frozen consumer receipt still matches the live consultation tree;
- every requested source is eligible and every exclusion is explicit;
- core and projection validation pass without warning;
- the closed artifact set contains no symlink or unknown file;
- every document binds to one record, concept, source path, text hash, and exact
  locator;
- token counts, BM25 statistics, PPMI neighbors, topics, and document-topic
  weights reproduce from authoritative text;
- build-report and index hashes match live artifacts;
- failure leaves no destination or private candidate;
- two clean builds are byte-identical; and
- representative passages pass the frozen consultation evidence contract.
