---
type: Agent Skill
title: Consult Semantic OKF Graphify
description: Give an agent read-only local tools and context to verify, search, traverse,
  compare, and cite an existing Graphify-backed Semantic OKF release. Use for exact
  record lookup, Graphify lexical discovery and BFS traversal, authoritative concept
  reading, grouped ledger counts, or grounded cross-source synthesis. This skill never
  builds, repairs, refreshes, or modifies knowledge.
tags:
- codex
- skill
skill_name: consult-semantic-okf-graphify
source_path: skills/consult-semantic-okf-graphify/SKILL.md
---

# Consult Semantic OKF with Graphify

Use Graphify to orient discovery, then verify selected claims in the unchanged Semantic OKF ledger and concept Markdown.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared requirements.
- Treat the supplied bundle as the only domain input; this package contains no corpus.
- Do not import a sibling skill, repository helper, external knowledge, or the web.
- If the core or projection is absent, stale, corrupt, or unsupported, stop with the diagnostic.

## Read-only boundary

- Validate the complete hash binding before every command.
- Use pinned Graphify scoring and BFS in memory; never run extraction, update, clustering, or semantic LLM workflows.
- Hash every published file before and after consultation and fail if any byte changes.
- Never create a cache or query log, repair an edge, rewrite a digest, or mutate the release.
- Treat traversal as discovery only and open the authoritative `concept_path` before citing a fact.

Read [querying.md](../../skills/consult-semantic-okf-graphify/references/querying.md) before choosing a route and [source-boundaries.md](../../skills/consult-semantic-okf-graphify/references/source-boundaries.md) when authority matters.

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py --format json
```

## Verify, query, and hydrate

```bash
python scripts/query_semantic_okf_graphify.py SNAPSHOT verify
python scripts/query_semantic_okf_graphify.py SNAPSHOT records --source-id SOURCE --record-id RECORD --show-content
python scripts/query_semantic_okf_graphify.py SNAPSHOT search "connected subgraph retrieval" --depth 2 --top-k 10 --show-content
python scripts/query_semantic_okf_graphify.py SNAPSHOT read concepts/source/item.md
python scripts/query_semantic_okf_graphify.py SNAPSHOT aggregate
```

Exact identity and counts come from `semantic/records.jsonl`. Search reports deterministic Graphify seeds, bounded context nodes, traversal counts, scores, ledger-derived paper identity, and exact authoritative concept-file locators. It reports `fallback: null`; any alternative route must be explicit.

## Completion gate

- Runtime, core, ledger, regenerated view, derived identity, record-index, graph, node, edge, path, and orphan checks passed.
- Every returned value and citation was checked in the authoritative concept or ledger.
- Source, ontology, provenance, validation, and derived-graph boundaries remained separate.
- The complete snapshot hash is identical before and after consultation.
