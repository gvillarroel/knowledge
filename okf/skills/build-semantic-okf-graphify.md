---
type: Agent Skill
title: Build Semantic OKF Graphify
description: Build and maintain a validated Semantic OKF snapshot with a hash-bound
  deterministic Graphify structural retrieval projection. Use for reviewed Markdown,
  CSV, JSON, JSONL, or RDF sources when construction, migration, validation, complete
  rebuild, promotion, or recovery of an OKF plus Graphify release is requested. This
  skill owns mutation only and never answers domain questions.
tags:
- codex
- skill
skill_name: build-semantic-okf-graphify
source_path: skills/build-semantic-okf-graphify/SKILL.md
---

# Build Semantic OKF with Graphify

Build one authoritative Semantic OKF release plus a non-authoritative Graphify graph for structural and lexical discovery.

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
- Put reviewed values into deterministic temporary headings, neutralize Markdown structural punctuation in scalar text, and emit links only for reviewed IRI relationships because Graphify's structural extractor does not index ordinary paragraph or bullet text.
- Regenerate every view digest from the authoritative ledger during validation, and verify deletion of all temporary views and caches before publishing.
- Read [graphify-projection.md](../../skills/build-semantic-okf-graphify/references/graphify-projection.md) before changing this contract.

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
python scripts/build_semantic_okf_graphify.py manifest.json semantic-okf-graphify-output
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
- Every ledger record has a projected node and readable authoritative concept.
- An independent second build has the same core and graph logical digests.
- No view, cache, query log, credential, remote call, or semantic LLM output was published.
