# Generated Chunked Classical Expert Contract

## Contents

- [Inputs](#inputs)
- [Output](#output)
- [Manifest](#manifest)
- [Read-only query contract](#read-only-query-contract)
- [Context and citation contract](#context-and-citation-contract)
- [Validation and comparison](#validation-and-comparison)

## Inputs

The generator accepts a closed Semantic OKF source manifest, a closed classical
retrieval plan, reviewed application guidance, an optional closed context plan,
and a new output directory whose basename equals the generated skill name. The
bundled context plan is used when no override is supplied.

Guidance describes application behavior rather than duplicating the corpus. It
contains Scope, Application workflow, Decision rules, and Evidence and limits.

## Output

The generated skill has this closed executable surface:

```text
<skill-name>/
  SKILL.md
  expert-manifest.json
  agents/openai.yaml
  references/
    guidance.md
    knowledge/
      index.md
      concepts/
      semantic/
      classical/
    context/
      index.json
      chunks.jsonl
  scripts/
    query_expert_knowledge.py
    _classical_snapshot.py
    _context_projection.py
    runtime_smoke.py
    requirements.txt
```

`references/knowledge/` remains byte-equivalent to the accepted separate
classical builder. Context is an additive derived projection and never changes
authoritative record bodies, identities, graphs, or classical ranks.

## Manifest

`expert-manifest.json` uses
`classical-chunked-knowledge-skill/1.0`. It binds:

- generated skill identity and every executable or instruction artifact;
- complete immutable knowledge tree and classical index;
- complete context tree, index, plan, chunk count, and token budgets;
- input manifest, classical plan, and context plan digests; and
- deep build and validation state.

It contains no timestamp or absolute path. Identical inputs produce an
identical complete skill tree.

## Read-only query contract

Every operation verifies the manifest, executable artifacts, complete
knowledge tree, context tree, record count, and index bindings before use. It
creates no cache, bytecode, query, or answer file.

- `verify` checks every physical record and chunk binding; `--deep-validation`
  independently rederives classical retrieval and all chunks.
- `inspect` reports immutable capabilities and digests.
- `context` runs unchanged classical retrieval internally and emits only a
  budgeted set of exact, nonredundant record spans.
- `chunk` hydrates one exact chunk plus zero to two verified linked neighbors.
- `search` preserves the full standalone classical payload for diagnostics and
  compatibility.
- `get` returns one exact authoritative ledger record and optionally its body.

The default route is `fusion`; all four classical routes remain available.

## Context and citation contract

Chunk rows contain no copied body text. Each row binds its classical passage,
authoritative identity, record-relative range, exact text digest, structural
heading path, token estimate, term counts, and previous/next links. Query-time
hydration slices the authoritative ledger body and verifies the digest.

The selector reserves distinct evidence identities, repairs uncovered
retrievable query facets, and then combines query relevance, new query-term
coverage, parent rank, evidence diversity, linked continuity, token cost, and
Jensen-Shannon redundancy. A `quality_guard` reports whether the selected
bundle meets both coverage and evidence-identity thresholds. An incomplete
bundle requires one bounded escalation or targeted neighbor hydration before
answering.

Every emitted span includes logical and physical concept paths, an optional
packed-record anchor, a direct citation, and the exact record character range.

## Validation and comparison

A passing package requires deep core, classical, and context validation;
deterministic `--check`; exact physical citations; source-package portability;
and unchanged full-search ranks and payloads relative to the accepted classical
consultant before citation enrichment.

Efficiency evaluation compares provider-visible `context --format markdown`
bytes or native tokens with the full-search baseline on identical questions.
Quality evaluation separately requires exact span reconstruction, retained
evidence identities, query-coverage gates, direct-retrieval parity, and—before
promotion—independent paired semantic non-regression. Mechanical evidence does
not establish answer correctness by itself.
