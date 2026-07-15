---
type: Agent Skill
title: Consult Semantic OKF Entity Graph
description: Consult an existing Semantic OKF entity-section graph through lexical
  section ranking, direct entity resolution, bounded reviewed-claim traversal, or
  reciprocal-rank fusion. Use when Codex must find entities extracted from files,
  follow graph relations to exact sections, retrieve multi-paper evidence, inspect
  claim provenance, or answer with verifiable claim IDs and page locators. This standalone
  skill is read-only and never builds, repairs, refreshes, or modifies knowledge.
tags:
- codex
- skill
skill_name: consult-semantic-okf-entity-graph
source_path: skills/consult-semantic-okf-entity-graph/SKILL.md
---

# Consult Semantic OKF Entity Graph

Resolve query entities and reviewed claims, follow bounded graph paths, and return exact source sections for verification. Use the projection for discovery only; use authoritative concepts, ledger records, or purpose-selected RDF graphs for factual support.

## Standalone and read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the supplied bundle as an explicit external input.
- Never write a cache, query, answer, lock, repaired file, or artifact into the bundle.
- Stop on a stale core hash, closed-schema violation, symlink, unsafe path, orphan node, invalid locator, broken graph reference, or failing report.
- Treat candidate phrases, mentions, co-mentions, traversal weights, and rankings as discovery signals.
- Treat only the underlying reviewed ledger records and selected authoritative graphs as factual evidence.

## Required references

- Read [entity-graph-format.md](../../skills/consult-semantic-okf-entity-graph/references/entity-graph-format.md) when inspecting integrity or diagnosing a snapshot.
- Read [querying.md](../../skills/consult-semantic-okf-entity-graph/references/querying.md) before choosing a mode, traversing claims, or assembling citations.

## Workflow

1. Inspect the snapshot. For new, benchmark, or release-critical input, use `--deep-validation` once to rederive every graph artifact in memory.
2. Decompose synthesis questions into mechanisms, conditions, contrasts, exclusions, and important negatives.
3. Run `fusion` for broad discovery, `entity` for direct entity/claim evidence, `traversal` for connected evidence, or `lexical` for exact terminology.
4. Read `resolved_entities`. For reviewed claim nodes, preserve exact `record_id`, `concept_path`, `record_source_path`, and `claim_evidence` locators.
5. Open each selected claim concept and its exact paper sections. Reject a candidate when the authoritative interpretation does not support the intended statement.
6. For multi-paper answers, run focused subqueries and retain at least one independent evidence path per required contrast. Do not let one paper satisfy a cross-paper requirement.
7. Construct the answer from atomic statements. Bind each statement to exact reviewed claim IDs, then derive sorted paper IDs, page citations, and evidence rows from those same claims.
8. Validate the requested response contract literally: key order, exact keys, word bounds, sorted unique arrays, path spelling, integer pages, and explicit abstention behavior.

## Environment and inspection

The package uses only the Python standard library:

```bash
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_entity_graph.py BUNDLE inspect
python scripts/query_semantic_okf_entity_graph.py BUNDLE inspect --deep-validation
```

Use `python -B` or `PYTHONDONTWRITEBYTECODE=1` when the mounted skill must remain byte-identical.

## Search modes

Exact section terminology:

```bash
python scripts/query_semantic_okf_entity_graph.py BUNDLE search --query "Prize-Collecting Steiner Tree" --mode lexical --top-k 10
```

Direct entity and reviewed-claim evidence:

```bash
python scripts/query_semantic_okf_entity_graph.py BUNDLE search --query "community summaries for global questions" --mode entity --top-k 10
```

Bounded paths through reviewed claims, papers, sections, mentions, and candidate co-mentions:

```bash
python scripts/query_semantic_okf_entity_graph.py BUNDLE search --query "corruption defenses for incomplete triples" --mode traversal --top-k 10
```

Reciprocal-rank fusion of lexical, direct-entity, and traversal rankings:

```bash
python scripts/query_semantic_okf_entity_graph.py BUNDLE search --query "compare evidence organization mechanisms" --mode fusion --top-k 15
```

Repeat `--source-id` or `--paper-id` to select a union inside that filter. The two filter kinds combine with logical AND.

## Answer discipline

- Preserve exact claim record IDs; do not substitute section IDs, entity IDs, or graph edge IDs.
- Use a claim's concept path for claim evidence and its paper-section locator for PDF citations.
- A graph path is a discovery explanation, not permission to strengthen a claim beyond its reviewed interpretation.
- Important negatives require explicit supporting claims. Absence of a graph edge is not evidence of absence unless the authoritative contract makes the graph complete for that predicate.
- If evidence is insufficient, return the contract's abstention form instead of filling gaps with model memory.

## Completion gate

Before answering, confirm:

- inspection passed and the bundle tree remained unchanged;
- evaluation-critical input passed deep rederivation;
- every cited claim exists and retains `review_state: reviewed`;
- every page locator resolves to an exact paper section and text hash;
- each atomic statement names all supporting claim IDs;
- paper IDs, citations, claims, and evidence are mutually consistent;
- important exclusions and failure conditions are stated when requested;
- output keys, ordering, sorting, word bounds, and types satisfy the prompt exactly; and
- no candidate entity, co-mention, score, web source, or model memory is presented as ground truth.
