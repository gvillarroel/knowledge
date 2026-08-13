---
name: build-semantic-okf-graphify
description: Build and maintain a validated Semantic OKF snapshot with a hash-bound deterministic Graphify projection whose record roots are connected by reciprocal ledger-derived lexical similarity. Use for reviewed Markdown, CSV, JSON, JSONL, or RDF sources when construction, migration, validation, complete rebuild, promotion, or recovery of a Graphify-backed Semantic OKF release is requested. This skill owns mutation only and never answers domain questions.
---

# Build Semantic OKF with Graphify

Build one authoritative Semantic OKF release plus a non-authoritative Graphify graph for structural and lexical discovery. Preserve compatibility with the unchanged `consult-semantic-okf-graphify` contract.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared requirements.
- Treat the reviewed manifest and local sources as explicit user inputs.
- Own ingestion, complete rebuild, projection creation, validation, promotion, rollback, and recovery.
- Do not search, answer, compare, cite, or synthesize domain knowledge.
- Never import a sibling skill or repository helper.

## Authority and engine boundary

- The ledger, concept Markdown, RDF graphs, provenance, and validation evidence remain authoritative.
- `retrieval/graphify/graph.json` is a hash-bound discovery projection only.
- Pin `graphifyy==0.9.17`; use structural Markdown extraction with no semantic LLM and no clustering.
- With `source-packed-v1`, reconstruct the exact `record-per-file-v1` Markdown inputs in memory and feed those virtual documents to the pinned extractor. Never materialize the expanded concept tree, and require the published graph bytes and query rankings to match the record-per-file build.
- Put reviewed values into deterministic temporary headings, neutralize Markdown structural punctuation in scalar text, and emit links only for reviewed IRI relationships because Graphify's structural extractor does not index ordinary paragraph or bullet text.
- Preserve Graphify's original labels. Identify exactly one `record-root` per ledger record, derive binary TF-IDF similarity from authoritative title, record ID, concept type, and body, and connect roots only when they are reciprocal nearest neighbors outside their record-ID partitions. Derive partitions from the first segment after the corpus-wide common record-ID prefix; fall back to unrestricted reciprocal neighbors when the corpus has only one partition.
- Publish similarity links as `harbor-lexical-similarity`, validate them by complete ledger regeneration, and never treat their scores or paths as evidence.
- Regenerate every view digest from the authoritative ledger during validation, and verify deletion of all temporary views and caches before publishing.
- Read [graphify-projection.md](references/graphify-projection.md) before changing this contract.

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py --format json
```

On Windows PowerShell activate with `.\.venv\Scripts\Activate.ps1`.

## Build and validate

```bash
python scripts/build_semantic_okf_graphify.py manifest.json semantic-okf-graphify-output \
  --concept-layout source-packed-v1
python scripts/validate_okf_bundle.py semantic-okf-graphify-output
python scripts/validate_semantic_okf_graphify.py semantic-okf-graphify-output --output-format json
```

The output must not exist. A passing release adds `retrieval/graphify/graph.json` and `retrieval/graphify/index.json`.

For a create-only migration of an existing validated core:

```bash
python scripts/materialize_graphify_projection.py EXISTING_BUNDLE --output-format json
```

## Complete rebuild rule

Refresh into a new directory by rerunning the complete manifest. Compare core tree, ledger, graph logical digest, and validation reports before atomic promotion. Never merge generated records, views, or graph nodes in place.

## Completion gate

- The runtime reports exactly Graphify 0.9.17 and all required query primitives.
- Every source and the unchanged Semantic OKF core validate.
- Graph nodes and edges are closed, relative, non-orphaned, and bound to regenerated record, paper, and view identity.
- Every ledger record has exactly one deterministic `record-root`; every lexical-similarity link equals the value regenerated from the ledger.
- Every ledger record has a projected node and readable authoritative concept.
- An independent second build has the same core and graph logical digests.
- No view, cache, query log, credential, remote call, or semantic LLM output was published.
