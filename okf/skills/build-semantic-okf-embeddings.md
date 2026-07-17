---
type: Agent Skill
title: Build Semantic OKF Embeddings
description: Build and independently validate an atomic Semantic OKF/RDF v1 snapshot
  plus a hash-bound, non-authoritative retrieval projection with record or semantic
  chunks and local embeddings. Use when Codex needs to materialize Markdown, CSV,
  JSON/JSONL, or RDF sources for semantic discovery, compare native and LlamaIndex
  splitting, use deterministic hashing or a pinned offline SentenceTransformers model,
  or reproduce an embedding-enabled corpus build. This skill owns construction only
  and does not answer questions from the snapshot.
tags:
- codex
- skill
skill_name: build-semantic-okf-embeddings
source_path: skills/build-semantic-okf-embeddings/SKILL.md
---

# Build Semantic OKF Embeddings

Build one authoritative Semantic OKF core and one derived retrieval projection as a single validated release. Keep model-dependent chunks outside the record ledger and RDF graphs so retrieval changes never redefine reviewed semantic identity.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and package-local requirements.
- Do not import or execute scripts, validators, instructions, or conventions from sibling skills.
- Own manifest review, source processing, chunking, embedding, materialization, and independent validation here.
- Do not search, answer, compare claims, cite, or synthesize from a published snapshot.
- Treat `retrieval/` as non-authoritative discovery data; `concepts/`, `semantic/records.jsonl`, and the RDF graphs remain the evidence layers.

## Required references

- Read [source-combination.md](references/source-combination.md) before combining physical sources.
- Read [manifest.md](references/manifest.md) before writing or changing the Semantic OKF manifest.
- Read [coherence-contract.md](references/coherence-contract.md) before changing core mappings or validation.
- Read [retrieval-plan.md](references/retrieval-plan.md) before choosing sources, chunking, or embeddings.
- Read [python-runtime.md](references/python-runtime.md) before installing or running the package.

## Workflow

1. Define scope, competency questions, source authority, and the requested physical input set.
2. Inspect source identifiers, schemas, encodings, and mappings; write the closed Semantic OKF manifest.
3. Write a closed retrieval plan. Select source IDs explicitly and pin every provider, model, revision, dimension, normalization rule, splitter, buffer, and threshold.
4. Install the base runtime. Install an optional backend only when the plan selects it, and pre-populate model weights explicitly.
5. Build into a new output path. The command creates the authoritative core first, derives retrieval artifacts in the same private candidate, validates both layers, and publishes with one final rename.
6. Run the independent validator against the published output.
7. Rebuild unchanged inputs into another new path and compare logical artifact hashes before accepting the release.

Never accept an implicit provider, hosted model, mutable model revision, network download, remote code, partial source selection, zero vector, or stale retrieval binding.

## Build and validate

Run commands from the directory containing this `SKILL.md`, or prefix paths with the copied skill root:

```bash
python scripts/build_semantic_okf_embeddings.py manifest.json retrieval-plan.json semantic-okf-embeddings --output-format json
python scripts/validate_semantic_okf_embeddings.py semantic-okf-embeddings --output-format json
```

The output directory must not already exist. A successful release contains the complete Semantic OKF core and exactly four derived retrieval files:

```text
semantic-okf-embeddings/
  index.md
  concepts/
  semantic/
    ontology.ttl
    data.ttl
    shapes.ttl
    provenance.ttl
    records.jsonl
    semantic-plan.json
    source-manifest.json
    validation-report.ttl
    build-report.json
  retrieval/
    index.json
    chunks.jsonl
    embeddings.jsonl
    build-report.json
```

`retrieval/index.json` binds the projection to the byte digest of `semantic/records.jsonl`, a canonical digest of every core file, a canonical selected-input inventory, the closed retrieval-plan digest, and the chunk/vector artifact hashes. Chunks bind back to exact record and concept identities. Vectors bind one-to-one to sorted chunk IDs.

## Portable baseline

Use this plan shape for a dependency-free retrieval baseline after installing the core requirements:

```json
{
  "schema_version": "1.0",
  "selection": {
    "source_ids": ["claims-a", "paper-a"]
  },
  "chunking": {
    "implementation": "native",
    "strategy": "semantic",
    "buffer_size": 1,
    "breakpoint_percentile_threshold": 95
  },
  "embedding": {
    "provider": "hashing",
    "model_id": "knowledge-hashing-embedding",
    "revision": "1",
    "dimension": 384,
    "normalize": true
  }
}
```

Use `strategy: "record"` for one chunk per selected record. The native semantic splitter uses the selected embedder to compare buffered adjacent sentence units. Smaller percentile thresholds generally create more chunks; validate the resulting evidence boundaries on representative inputs.

## Optional backends

Install LlamaIndex only for `chunking.implementation: "llamaindex"`:

```bash
python -m pip install -r scripts/requirements-llamaindex.txt
```

Install SentenceTransformers only for `embedding.provider: "sentence-transformers"`:

```bash
python -m pip install -r scripts/requirements-sentence-transformers.txt
```

The SentenceTransformers plan requires a Hugging Face `namespace/repository` model ID and immutable hexadecimal revision. The runtime forces Hugging Face and Transformers offline modes, resolves that exact revision from the local cache, verifies the snapshot directory revision, and gives SentenceTransformers only the resolved local path with `local_files_only=True`, `trust_remote_code=False`, and CPU execution. It never downloads weights or accepts a local path as a model ID. Prepare and govern the cache outside this build, then prove the exact revision is locally available before starting.

LlamaIndex receives the selected local embedder explicitly. It never chooses an OpenAI model or another hosted default. Optional imports are lazy; a missing extra fails with the exact package-local requirements file to install.

## Completion gate

Before delivery, confirm all of the following:

- base runtime smoke passes and only selected optional extras are installed;
- every requested source ID appears in `eligible_source_ids`, and excluded sources are explicit;
- the independent core and retrieval validator passes;
- output publication left no candidate or partial destination;
- record, core-tree, selected-input, plan, chunk, and embedding digests agree;
- chunk locators resolve to exact text in the authoritative record body;
- every chunk has exactly one finite, non-zero vector of the declared dimension;
- normalized vectors have unit L2 norm within the declared precision tolerance;
- unchanged inputs and plan reproduce the same logical artifacts; and
- representative evidence paths have been opened and manually checked without modifying the snapshot.
