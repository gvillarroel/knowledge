---
name: consult-semantic-okf-entity-graph
description: Consult an existing Semantic OKF entity-section graph through lexical section ranking, direct entity resolution, bounded document/association traversal, or reciprocal-rank fusion. Use when Codex must find entities extracted from arbitrary sources, follow graph paths to exact source-record sections, retrieve multi-document evidence, inspect source-scoped provenance, or reproduce a legacy reviewed-claim query. This standalone skill is read-only and never builds, repairs, refreshes, or modifies knowledge.
---

# Consult Semantic OKF Entity Graph

Resolve query entities and documents, follow bounded graph paths, and return exact source-record sections for verification. Use the projection for discovery only; use authoritative concepts, ledger records, or purpose-selected RDF graphs for factual support.

## Standalone and read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the supplied bundle as an explicit external input.
- Never write a cache, query, answer, lock, repaired file, or artifact into the bundle.
- Stop on a stale core hash, closed-schema violation, symlink, unsafe path, orphan node, invalid locator, broken graph reference, or failing report.
- Treat candidate phrases, mentions, co-mentions, traversal weights, and rankings as discovery signals.
- Treat the ledger identity and exact body slice as authoritative provenance, not automatic proof that document prose is true. Use reviewed records or selected authoritative graphs when the domain requires reviewed factual evidence.

## Required references

- Read [entity-graph-format.md](references/entity-graph-format.md) when inspecting integrity or diagnosing a snapshot.
- Read [querying.md](references/querying.md) before choosing a mode, traversing claims, or assembling citations.

## Workflow

1. Inspect the snapshot. For new, benchmark, or release-critical input, use `--deep-validation` once to rederive every graph artifact in memory.
2. Decompose synthesis questions into mechanisms, conditions, contrasts, exclusions, and important negatives.
3. Run `fusion` for broad discovery, `entity` for direct entity/document evidence, `traversal` for connected evidence, or `lexical` for exact terminology.
4. Preserve the returned structured `document_identity`, source and record digests, concept/source paths, locator, text, and text hash. Never reconstruct them from filenames or prose.
5. Open each selected concept and verify `record.body[start:end]`. Reject a candidate when the exact source context does not support the intended statement.
6. For multi-document answers, run focused subqueries and retain at least one independent source-record evidence path per required contrast. Do not let one document satisfy a cross-document requirement.
7. Construct the answer from atomic statements and bind each statement to exact source-record sections. For legacy reviewed-claim snapshots, retain exact claim IDs and their page evidence.
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

Bounded paths through documents, sections, mentions, and candidate co-mentions:

```bash
python scripts/query_semantic_okf_entity_graph.py BUNDLE search --query "corruption defenses for incomplete triples" --mode traversal --top-k 10
```

Reciprocal-rank fusion of lexical, direct-entity, and traversal rankings:

```bash
python scripts/query_semantic_okf_entity_graph.py BUNDLE search --query "compare evidence organization mechanisms" --mode fusion --top-k 15
```

For schema `2.0`, repeat `--source-id`, `--document-id`, or `--record-id` to select a union within one filter; filter kinds combine with logical AND. For schema `1.0`, use `--source-id` and `--paper-id`. Supplying a legacy paper filter to a generic bundle, or a generic document filter to a legacy bundle, fails closed.

## Answer discipline

- Preserve exact `(source_id, record_id, record_sha256)` bindings; do not substitute section, entity, or graph-edge IDs for provenance.
- Treat `record-body` character ranges as locators into the ledger body, not into the raw source or concept Markdown.
- In legacy schema `1.0`, preserve exact claim record IDs and page locators.
- A graph path is a discovery explanation, not permission to strengthen a claim beyond its reviewed interpretation.
- Important negatives require explicit supporting claims. Absence of a graph edge is not evidence of absence unless the authoritative contract makes the graph complete for that predicate.
- If evidence is insufficient, return the contract's abstention form instead of filling gaps with model memory.

## Completion gate

Before answering, confirm:

- inspection passed and the bundle tree remained unchanged;
- evaluation-critical input passed deep rederivation;
- every cited section retains exact source, record, concept, locator, and digest bindings;
- every locator reconstructs the exact authoritative record-body slice and text hash;
- each atomic statement names its supporting source-record evidence;
- legacy claim IDs, paper IDs, page citations, and evidence are mutually consistent when schema `1.0` is used;
- important exclusions and failure conditions are stated when requested;
- output keys, ordering, sorting, word bounds, and types satisfy the prompt exactly; and
- no candidate entity, co-mention, score, web source, or model memory is presented as ground truth.
