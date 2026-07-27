---
name: consult-semantic-okf-harbor-graphify
description: Consult an immutable Graphify-backed Semantic OKF snapshot with bounded lexical facet searches and BFS traversal, then compile strict source-generic Harbor answers from authoritative parent records. Use for compact grounded synthesis, exact hashes and locators, deterministic first-use evidence ordering, or Graphify Harbor evaluation. This standalone skill is read-only and never builds, repairs, or modifies knowledge.
---

# Consult Semantic OKF Harbor Graphify

Use Graphify only for discovery, hydrate every selected result from the exact ledger parent, and compile the final answer from the bounded support pack.

## Standalone boundary

- Use only this directory and the read-only bundle supplied by the user.
- Do not import sibling skills, evaluator data, fixtures, answer keys, the web, or model memory as evidence.
- Keep the copied Graphify runtime unchanged. Treat graph scores, labels, seeds, and traversed edges as non-authoritative discovery signals.
- Fail on stale hashes, corrupt graphs, unknown identities, unsafe paths, altered support packs, or output-contract violations.

Read [querying.md](references/querying.md) before selecting supports and [source-boundaries.md](references/source-boundaries.md) when authority matters.

## Answer workflow

1. Decompose the question into named subjects, mechanisms, conditions, contrasts, exclusions, and important negatives.
2. Run `harbor_answer.py prepare` exactly as shown, without overriding retrieval or size defaults. It searches the full question and bounded facets, uses Graphify lexical scoring plus BFS depth 2, interleaves facet results, deduplicates exact source-record identities, and emits at most 6 compact ledger-hydrated excerpts as one compact JSON value.
3. Inspect the returned excerpts in that pack. After `prepare` succeeds, do not run diagnostic search, read, exact-record, or verification commands; proceed directly to draft and finalize. Use a support only when it directly entails the atomic statement and qualify unsupported facets.
4. Copy `draft_template`, add an atomic summary and claims, list used support IDs in evidence first-use order, then run `finalize` with the same parameters.
5. Return finalizer JSON unchanged. If it fails, repair the external draft or regenerate support; never hand-build evidence.

```bash
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_graphify.py /knowledge verify
python scripts/harbor_answer.py /knowledge prepare \
  --question-id q031 --question "A hard multi-part question"
python scripts/harbor_answer.py /knowledge finalize \
  --question-id q031 --question "A hard multi-part question" --draft /tmp/draft.json
```

Use a location outside the bundle for ephemeral drafts. Preserve the exact closed draft keys, parameter binding, support IDs, and evidence-index ordering emitted by the template.

## Completion gate

Confirm snapshot verification passed; the bundle hash is unchanged; every facet used Graphify with the declared depth; every claim maps to directly supporting authoritative record text; all identifiers, paths, locators, and hashes were compiler-generated; every evidence row is used in first-use order; unsupported facets are qualified; and finalization succeeded without fallback.
