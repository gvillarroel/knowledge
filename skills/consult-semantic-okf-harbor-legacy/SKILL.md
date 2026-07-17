---
name: consult-semantic-okf-harbor-legacy
description: Consult a validated Semantic OKF snapshot with deterministic ledger TF-IDF, bounded facet coverage, and a closed answer compiler that emits exact hash-bound evidence. Use for read-only questions that require a compact grounded JSON answer, especially multi-clause synthesis evaluated through Harbor. Do not use to build, repair, refresh, or modify a snapshot.
---

# Consult Semantic OKF Harbor Legacy

Answer from one immutable Semantic OKF snapshot without hand-transcribing evidence metadata.

## Standalone boundary

- Use only this package and the supplied bundle.
- Treat the bundle, ledger, concepts, and semantic graphs as immutable.
- Do not import sibling skills, repository helpers, evaluation fixtures, or expected answers.
- Do not use the web or prior knowledge when the snapshot is authoritative.
- Stop if the build report is not passing or the compiler rejects the ledger.

## Required workflow

1. Preserve the exact question ID and question text from the request.
2. Run `harbor_answer.py prepare` once with the exact final parameters.
3. Read only the bounded support excerpts needed to compose the answer.
4. Copy `draft_template` and replace its placeholder summary. Add atomic claims.
5. Put only listed `support_id` values in the draft `evidence` array, in order of first use.
6. Point every claim to one or more zero-based indices in that array.
7. Run `harbor_answer.py finalize` with the same question and parameters.
8. Return the finalizer's JSON object exactly. Do not add wrapper text or edit its evidence rows.

The finalizer recomputes retrieval and rejects duplicate JSON keys, changed parameters, a changed
question, stale packs, unknown or duplicate supports, out-of-range indices, unused evidence, and
evidence not ordered by first use.

## Prepare support

Run from this skill directory, or prefix the paths with its root:

```bash
python -B scripts/harbor_answer.py BUNDLE prepare \
  --question-id QUESTION_ID \
  --question "EXACT QUESTION" > support-pack.json
```

The dependency-free compiler decomposes the full question into at most eight ordered facets, ranks
the authoritative ledger with deterministic TF-IDF, round-robins facet hits, and deduplicates exact
`source_id` plus `record_id` identities. Support IDs bind the complete public evidence identity by
hash. Excerpts are discovery context only.

Read [harbor-answer-contract.md](references/harbor-answer-contract.md) before drafting. Read
[querying.md](references/querying.md) only when the question requires direct ledger or RDF
inspection beyond the compact support pack. Read [source-boundaries.md](references/source-boundaries.md)
when authorities or partitions differ.

## Finalize the answer

Start with the emitted `draft_template`. A draft has exactly these fields:

```json
{
  "question_id": "q000",
  "question_sha256": "COPY_FROM_PACK",
  "parameters": {"COPY": "FROM_PACK"},
  "support_pack_sha256": "COPY_FROM_PACK",
  "answer": {
    "summary": "Concise synthesis.",
    "claims": [
      {"statement": "One atomic claim.", "evidence_indices": [0]}
    ]
  },
  "evidence": ["support-..." ]
}
```

Finalize from a file:

```bash
python -B scripts/harbor_answer.py BUNDLE finalize \
  --question-id QUESTION_ID \
  --question "EXACT QUESTION" \
  --draft answer-draft.json
```

Use identical `--facet-limit`, `--per-facet`, `--max-supports`, and `--excerpt-chars` values on both
commands if overriding defaults. Never reconstruct source IDs, paths, hashes, or locators manually.

## Other consultation layers

The copied `query_semantic_okf.py` remains byte-identical to the legacy package and is available for
exact ledger filters and read-only SELECT or ASK queries. Use it only when needed to understand the
support, then still pass the public answer through `harbor_answer.py finalize`.

## Completion gate

- Confirm the bundle was not modified.
- Confirm the support pack came from the exact question and final parameters.
- Keep claims atomic and cite only support that directly establishes each statement.
- Include important qualifications and negatives when the support establishes them.
- Return only a successful finalizer output with exact key ordering and hash-valid ledger evidence.
