---
name: build-semantic-okf-graphify-next
description: Build and validate an experimental Semantic OKF Graphify projection with reciprocal content-similarity and documentation-reference bridges. Use when evaluating whether deterministic ledger-derived cross-references improve consultation retrieval beyond the official builder without changing authoritative records or the consultation skill. This candidate owns mutation only and never answers domain questions.
---

# Build Semantic OKF with Graphify Next

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
- When the authoritative core is source-packed, reconstruct the record-per-file
  Graphify input in memory from the ledger and semantic plan. Never materialize
  those logical documents; require the resulting graph to remain byte-equivalent
  to the same records built with the record-per-file layout.
- Put reviewed values into deterministic temporary headings, neutralize Markdown structural punctuation in scalar text, and emit links only for reviewed IRI relationships because Graphify's structural extractor does not index ordinary paragraph or bullet text.
- Preserve Graphify's original labels. Identify exactly one `record-root` per ledger record and retain the official reciprocal top-one cross-partition binary TF-IDF bridge derived from authoritative title, record ID, concept type, and body.
- Add a separate bridge when two authoritative bodies reference each other's normalized `/en/.../` documentation routes. Derive routes only from ledger record IDs and reviewed body links; ignore one-way references and reciprocal-reference nodes with degree above six to limit hub expansion.
- Publish the two signals separately as `harbor-lexical-similarity` and `harbor-reciprocal-reference`, validate both by complete ledger regeneration, and never treat their scores or paths as evidence.
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
python scripts/build_semantic_okf_graphify.py manifest.json semantic-okf-graphify-output --concept-layout source-packed-v1
python scripts/validate_okf_bundle.py semantic-okf-graphify-output
python scripts/validate_semantic_okf_graphify.py semantic-okf-graphify-output --output-format json
```

The output must not exist. A passing release adds `retrieval/graphify/graph.json` and `retrieval/graphify/index.json`.
The recommended source-packed layout combines repeated CSV, JSON, and RDF
records into one authoritative Markdown collection per source while preserving
every logical ledger identity, complete body, digest, and byte-equivalent
Graphify retrieval projection.

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
- Every ledger record has exactly one deterministic `record-root`; every lexical-similarity and reciprocal-reference link equals the value regenerated from the ledger.
- Every ledger record has a projected node and a readable authoritative concept
  file or hash-anchored collection record.
- The source-packed and record-per-file builds of the same ledger produce the
  same Graphify graph bytes and ranked query results.
- An independent second build has the same core and graph logical digests.
- No view, cache, query log, credential, remote call, or semantic LLM output was published.
