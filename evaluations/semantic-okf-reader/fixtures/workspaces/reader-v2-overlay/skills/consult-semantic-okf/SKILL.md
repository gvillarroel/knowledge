---
name: consult-semantic-okf
description: Give an agent the general read-only context and local tools needed to navigate and consult an existing Semantic OKF knowledge folder efficiently. Use when Codex needs to discover records, read concepts, choose an authoritative semantic layer, run safe local SELECT or ASK queries, trace provenance, compare sources, or return grounded evidence. This skill never creates, repairs, refreshes, or modifies knowledge.
---

# Consult Semantic OKF

Navigate and answer from one published Semantic OKF knowledge folder while preserving its revision and evidence boundaries.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared Python requirements.
- Do not import scripts, instructions, validators, or conventions from sibling skills or repository files.
- Treat the supplied knowledge folder as the only domain input; the skill itself contains no domain corpus.
- Provide read-only navigation and consultation context only. Never create or maintain the knowledge folder.

## Read-only boundary

- Treat the bundle, source manifest, concepts, and semantic graphs as immutable inputs.
- Do not edit sources, manifests, mappings, ontology declarations, SHACL rules, ledgers, concepts, or generated graphs.
- Do not run build, refresh, recovery, or promotion commands.
- If the snapshot is missing, failed, stale, or requires source changes, report that condition and stop without attempting a repair.
- Do not use prior knowledge, the web, or guesses when the request limits answers to the snapshot.

## Workflow

1. Parse the question and exact output contract: requested facts, operations, source scope, graph scope, evidence form, keys, types, ordering, limits, and citation requirements.
2. Locate the bundle and require a passing `semantic/build-report.json` plus the declared read artifacts.
3. Choose the cheapest authoritative layer that can answer the operation.
4. Discover exact identifiers and artifact paths through `semantic/records.jsonl` before opening large concepts or graphs.
5. Read selected `concepts/` Markdown for full explanations and source-oriented context.
6. Use `semantic/data.ttl` only when the question needs joins, traversal, grouping, aggregation, or typed values. Add other graphs only for their declared purpose.
7. For multi-source questions, establish breadth and evidence coverage before reading any one source deeply.
8. Verify every returned value, citation, page locator, and `concept_path` against the selected authoritative layer.
9. Apply the requested response schema exactly and verify the final evidence paths before returning the answer.

## Required references

- Read [querying.md](references/querying.md) before choosing a layer or writing a query.
- Read [source-boundaries.md](references/source-boundaries.md) when a bundle contains separate authorities, homogeneous partitions, or cross-bundle evidence.
- Read [cross-source-synthesis.md](references/cross-source-synthesis.md) before comparing, aggregating, or citing multiple sources.

## Environment

Run commands from the directory containing this `SKILL.md`, or prefix paths with the skill root.

```bash
python -m venv .venv
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
```

The helper is local and read-only. It does not perform network requests, mutation, entailment, build, refresh, or recovery.

## Choose the authoritative layer

1. Use `semantic/records.jsonl` for exact identifiers, source filters, record types, mapped attributes, counts, and literal artifact paths.
2. Use `concepts/` Markdown with fixed-string search for lexical discovery and human reading.
3. Use `semantic/data.ttl` for accepted domain facts and semantic operations.
4. Add `ontology.ttl` only for reviewed schema questions.
5. Add `provenance.ttl` only for lineage or physical-source questions.
6. Query `shapes.ttl` for declared constraints and `validation-report.ttl` for validation outcomes; never present either as ordinary domain facts.

Do not union all graphs by default. Use entailment `none` unless a separately declared reasoner workflow is part of the request.

## Query examples

```bash
python scripts/query_semantic_okf.py BUNDLE ledger \
  --source-id papers --type "Research Paper" --all --format json

python scripts/query_semantic_okf.py BUNDLE ledger \
  --contains "retrieval strategy" --show-content --format json

python scripts/query_semantic_okf.py BUNDLE sparql \
  --query-file queries/methods.rq --graph data --format json

python scripts/query_semantic_okf.py BUNDLE sparql \
  --query-file queries/lineage.rq --graph data --graph provenance --format json
```

Use `--validate` to parse the complete read surface before consultation. This verifies the ledger, exact concept paths, semantic plan, and local Turtle graphs. It is a read-only integrity check, not a repair operation.

## Cross-source synthesis

Work breadth before depth. Convert the request into a clause checklist and build a source-by-clause-by-dimension ledger from one batched query. Count a source only when a selected claim directly supports a requested clause. Meet the independent-source minimum with verified relevant sources before reading any one source deeply.

Copy artifact paths verbatim from ledger `concept_path` values. Never reconstruct hashes, shorten generated names, use wildcard paths, or substitute a topic-adjacent source for a relevant one. Keep source IDs, cited pages, and evidence paths aligned.

Read [cross-source-synthesis.md](references/cross-source-synthesis.md) only when the request needs multi-source comparison or a strict evidence contract. Its optional helpers remain local and read-only.

## Completion gate

Before returning an answer, confirm:

- the snapshot passed the read-surface gate and was not modified;
- any strict evidence contract passed its bundled read-only preflight after the final repair;
- the chosen graph set matches the question and no unrelated graph was treated as domain evidence;
- every requested operation, clause, controlled dimension, and source minimum is satisfied;
- returned scalars, arrays, objects, RDF terms, datatypes, and nulls match the requested representation;
- every citation and evidence path exists and directly supports the associated statement;
- exact keys, types, ordering, uniqueness, limits, and length requirements are satisfied;
- no claim depends on the web, guesses, or unmounted knowledge when the snapshot is authoritative.
