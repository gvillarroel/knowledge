---
type: Agent Skill
title: Build Semantic OKF Entity Graph
description: Build and independently validate an atomic Semantic OKF snapshot plus
  a deterministic, non-authoritative document, entity, mention, co-mention, and exact-section
  graph over arbitrary declared sources. Use when Codex must extract candidate entities
  from Markdown, CSV, JSON, or RDF records, connect source-scoped records to precise
  evidence sections, preserve a legacy reviewed-claim graph, or reproduce offline
  entity-first retrieval. This standalone skill owns construction only and never answers
  from a published snapshot.
tags:
- codex
- skill
skill_name: build-semantic-okf-entity-graph
source_path: skills/build-semantic-okf-entity-graph/SKILL.md
---

# Build Semantic OKF Entity Graph

Build the authoritative Semantic OKF core unchanged, then derive an entity-first graph that points every usable relation or mention to exact source sections. Keep automatic phrases, mention matches, co-mentions, traversal weights, and scores outside the authoritative ledger and RDF graphs.

## Standalone and authority boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the manifest, sources, graph plan, and absent destination as explicit inputs.
- Do not import or execute a sibling skill, repository helper, evaluation fixture, or root document.
- Own source processing, core materialization, graph derivation, validation, and atomic publication.
- Do not search, answer, compare, cite, or synthesize from a published snapshot.
- Preserve reviewed claim semantics exactly in legacy plans. Never promote document prose, extracted phrases, matched mentions, or co-mentions to authoritative facts.

## Required references

- Read [source-combination.md](../../skills/build-semantic-okf-entity-graph/references/source-combination.md) before combining physical sources.
- Read [manifest.md](../../skills/build-semantic-okf-entity-graph/references/manifest.md) before authoring the Semantic OKF manifest.
- Read [coherence-contract.md](../../skills/build-semantic-okf-entity-graph/references/coherence-contract.md) before changing mappings or validation.
- Read [entity-graph-plan.md](../../skills/build-semantic-okf-entity-graph/references/entity-graph-plan.md) before selecting sources or parameters.
- Read [entity-graph-format.md](../../skills/build-semantic-okf-entity-graph/references/entity-graph-format.md) before reviewing or diagnosing artifacts.
- Read [python-runtime.md](../../skills/build-semantic-okf-entity-graph/references/python-runtime.md) before installing or running the package.

## Workflow

1. Define source authority, exact physical inputs, identity scope, competency questions, and evidence identities.
2. Inspect source schemas and write the closed Semantic OKF manifest. Keep entity fusion upstream when records need reconciliation.
3. Write a closed plan. Prefer source-generic schema `2.0` with explicit `source_ids`; use legacy schema `1.0` only to reproduce the pinned paper/claim/vocabulary graph.
4. Pin sectioning, tokenization, candidate extraction, BM25, co-mention, traversal, fusion, and diversity parameters.
5. Install only `scripts/requirements.txt`; the graph derivation is deterministic, offline, and model-free.
6. Build into an absent path. The command materializes the core, rederives the complete graph, validates it, and publishes with one final rename.
7. Run the independent validator and a second clean build. Require identical sorted path-and-byte hashes.
8. Open representative concept paths and section locators. Confirm exact `record.body` slices, source-record identities, and graph joins. For legacy plans, also confirm reviewed claim paths.

Never accept unknown plan members, partial source selection, source/record identity collisions, approximate locators, symlinks, stale hashes, or an existing destination. In legacy mode, also reject unreviewed claims and missing evidence sections.

## Build and validate

Run from this skill directory, or prefix scripts with the copied skill root:

```bash
python scripts/runtime_smoke.py
python scripts/build_semantic_okf_entity_graph.py manifest.json entity-graph-plan.json semantic-okf-entity-graph --output-format json
python scripts/validate_semantic_okf_entity_graph.py semantic-okf-entity-graph --output-format json
```

A successful release contains the complete core and exactly seven graph files:

```text
semantic-okf-entity-graph/
  index.md
  concepts/
  semantic/
  entity-graph/
    index.json
    entities.jsonl
    sections.jsonl
    mentions.jsonl
    edges.jsonl
    lexicon.json
    build-report.json
```

In schema `2.0`, every selected ledger record becomes a collision-safe document node keyed by `(source_id, record_id)`. Heading-aware sections are bounded exact character ranges over authoritative `record.body`; headerless records use the same bounded fallback. `partOfDocument` is an authoritative structural binding, while phrase mentions and co-mentions remain candidates. Schema `1.0` retains the original reviewed method, dimension, paper, claim, and PDF-page projection unchanged.

## Completion gate

Before delivery, confirm:

- package-local runtime smoke passes;
- every selected source is eligible and exclusions are explicit;
- authoritative core validation and graph rederivation pass;
- the closed graph directory has no unknown file or symlink;
- every authoritative document entity binds to one source-scoped ledger record and concept;
- every section reconstructs an exact authoritative `record.body` slice and text hash;
- every schema `2.0` section preserves source, record, source-content, record, concept, and locator bindings;
- every schema `1.0` reviewed claim resolves every declared locator, including multi-page evidence;
- candidate phrases, mentions, and co-mentions are labeled non-authoritative;
- artifact hashes, summary counts, index, and build report agree;
- failure leaves no destination or private candidate;
- two unchanged builds are byte-identical; and
- after publication, an independently installed `consult-semantic-okf-entity-graph` package can run representative entity, traversal, and fusion queries that return verifiable file and section locators. The build package itself does not query the published snapshot.
