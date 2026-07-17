---
type: Agent Skill
title: Consult Semantic OKF Harbor Embeddings
description: Consult an immutable embedding-enabled Semantic OKF snapshot with facet-wise
  hybrid chunk retrieval, authoritative parent-record resolution, and a closed answer
  compiler that emits exact hash-bound evidence. Use for paraphrase-heavy or multi-clause
  grounded JSON answers evaluated through Harbor. Do not use to build, repair, download
  models for, refresh, or modify a snapshot.
tags:
- codex
- skill
skill_name: consult-semantic-okf-harbor-embeddings
source_path: skills/consult-semantic-okf-harbor-embeddings/SKILL.md
---

# Consult Semantic OKF Harbor Embeddings

Discover with the declared embedding projection, but answer only from immutable ledger parents.

## Standalone boundary

- Use only this package, the supplied bundle, and its explicitly mounted offline model cache.
- Do not import sibling skills, repository helpers, evaluation fixtures, or expected answers.
- Treat retrieval artifacts as derived discovery data and ledger parent records as evidence.
- Never write a cache, query, answer, repair, or model into the bundle.
- Stop on any stale digest, malformed artifact, unknown provider, or invalid record binding.

## Required workflow

1. Preserve the exact question ID and question text.
2. Run `harbor_answer.py prepare` once with the final parameters and `--mode auto`.
3. Check each support's `effective_mode`; disclose fallback when the response contract permits it.
4. Draft atomic claims from the bounded parent-record excerpts.
5. Put listed `support_id` values in the draft `evidence` array in order of first use.
6. Point every claim to one or more zero-based indices in that array.
7. Run `harbor_answer.py finalize` with the identical question, mode, and parameters.
8. Return the finalizer's JSON object exactly, without wrapper text or evidence edits.

The finalizer reloads and validates the complete embedding snapshot, reruns the same facet searches,
and rejects duplicate JSON keys, parameter drift, stale packs, unknown supports, invalid indices,
unused evidence, and evidence not ordered by first use.

## Prepare support

Run from this skill directory, or prefix paths with its root:

```bash
python -B scripts/harbor_answer.py BUNDLE prepare \
  --question-id QUESTION_ID \
  --question "EXACT QUESTION" \
  --mode auto > support-pack.json
```

The compiler decomposes the request into at most eight ordered facets and runs this package's existing
hybrid chunk search for each facet. It round-robins results, deduplicates exact source-record
identities, resolves chunks to authoritative ledger parents, and exposes at most sixteen bounded
parent excerpts. Every opaque support ID hashes the complete public evidence identity.

Read [harbor-answer-contract.md](../../skills/consult-semantic-okf-harbor-embeddings/references/harbor-answer-contract.md) before drafting. Read
[retrieval-format.md](../../skills/consult-semantic-okf-harbor-embeddings/references/retrieval-format.md) when diagnosing integrity. Read
[querying.md](../../skills/consult-semantic-okf-harbor-embeddings/references/querying.md) before changing retrieval mode or interpreting fallback.

## Finalize the answer

Copy `draft_template` from the support pack. Replace the summary, add claim objects with exactly
`statement` and `evidence_indices`, and list only known support IDs in `evidence`.

```bash
python -B scripts/harbor_answer.py BUNDLE finalize \
  --question-id QUESTION_ID \
  --question "EXACT QUESTION" \
  --mode auto \
  --draft answer-draft.json
```

Use identical `--facet-limit`, `--per-facet`, `--max-supports`, `--excerpt-chars`, and `--mode` values
on both commands when overriding defaults. `auto` is the normal hybrid route and may degrade only
for an allowed provider-availability condition. Never reconstruct source IDs, paths, hashes, or
locators manually.

## Existing retrieval CLI

The copied `query_semantic_okf_embeddings.py` and `_embedding_snapshot.py` remain byte-identical to
the embedding baseline. Use `inspect` for diagnostics or `search` for exploratory retrieval, but pass
the public answer through `harbor_answer.py finalize`.

## Completion gate

- Confirm snapshot inspection and parent-record resolution passed without mutation.
- Confirm the pack came from the exact question and final parameters.
- Keep claims atomic and cite only parent support that directly establishes each statement.
- Include important qualifications and negatives when evidence supports them.
- Return only successful finalizer JSON with exact key ordering and hash-valid record evidence.
