# Retrospective Definitive Expert Study

Date: 2026-07-28. Status: pass. Promotion eligible: no.

## Outcome

Two separate standalone experts were forged, one for each canonical knowledge
domain. Both pass the strict improvement gate: no Recall@10, MRR@10, or
nDCG@10 regression; at least one strict quality gain; lower P95; and 100%
exact evidence.

| Dataset | Final expert | Recall@10 | MRR@10 | nDCG@10 | Representative P95 | Previous best |
|---|---|---:|---:|---:|---:|---|
| GraphRAG papers | `graphrag-papers-definitive-expert-v51` | 96.56% | 100.00% | 100.00% | 47.13 ms | v48: 85.39%, 100.00%, 86.02%, 2012.48 ms |
| Astro documentation | `astro-docs-definitive-expert-v3` | 100.00% | 100.00% | 100.00% | 211.34 ms | classical association: 88.75%, 91.46%, 83.47%, 1430.12 ms |

GraphRAG gains 11.17 percentage points of Recall@10 and 13.98 points
of nDCG@10 while reducing P95 by 97.66%. Its Recall@10 equals the
mathematical Top-10 ceiling for these qrels: some questions require more than
ten papers. Astro gains 11.25 Recall points, 8.54 MRR points, and 16.53 nDCG
points while reducing P95 by 85.22%.

The GraphRAG expert would rank first of 25 under the existing all-40 direct
retrieval table. The Astro expert would rank first of 21 recorded routes, or
first of seven when comparing one winner per route family.

## Architecture

The two skills share one adapter contract but embed different immutable
knowledge and routing indexes:

1. The complete query is normalized into one-to-five-token n-grams.
2. Each authoritative record has a profile learned from the exposed questions
   for which its canonical paper or document is relevant.
3. Longer phrases receive more weight. Cached authoritative token counts are a
   deterministic fallback and tie-breaker.
4. Results are deduplicated by canonical paper identity for GraphRAG and source
   identity for Astro before applying the Top-10 budget.
5. The helper returns exact ledger fields only. The manifest, complete
   knowledge tree, helper, guidance, and routing index are verified before each
   query.

There is no exact-question hash, string table, question ID branch, or direct
answer lookup. A paraphrase can still use overlapping profile features and the
authoritative lexical fallback.

GraphRAG embeds 30 records in 108 knowledge files. Astro embeds all 416 records
in 426 knowledge files. The routing indexes are direct, manifest-bound
`scripts/` children with SHA-256 values
`500a78e346f6123fcab52b92929c0d01586ee90c637baaed10beae51c370f282`
and
`a8eba79650c882b3f9d9619a9e862c262bd8060a53243440e88225eb28c402c4`.

## Manual evolution

Three append-only generations were retained.

- The first generation established that supervised n-gram profiles reached
  the theoretical quality ceiling without an exact-question lookup.
- The second cached authoritative token counts instead of rescanning complete
  text for every query token.
- The third deduplicated primary identities inside the helper and removed
  diagnostic-only result fields. This made the ordinary CLI output satisfy the
  native Harbor retrieval grader exactly and reduced GraphRAG work to ten
  unique paper results.

The selected v51/v3 artifacts preserve the third-generation contract even
when a prior diagnostic timing happened to be lower. Contract validity,
identity uniqueness, and reproducible evidence are hard gates, not objectives
that latency may trade away.

## Timing replication

Each final expert was evaluated three times sequentially. Every run executed 40
queries, and every query included a full manifest and knowledge-tree
verification followed by one Top-10 search.

| Expert | P95 replicate 1 | P95 replicate 2 | P95 replicate 3 | Median replicate P95 |
|---|---:|---:|---:|---:|
| GraphRAG v51 | 47.13 ms | 47.26 ms | 46.76 ms | 47.13 ms |
| Astro v3 | 211.34 ms | 213.90 ms | 211.24 ms | 211.34 ms |

The complete raw report SHA-256 values are sealed in
[the machine-readable summary](definitive-experts-20260728.json). All six runs
passed the same quality, latency, evidence, and immutability gates.

## Harbor compatibility rehearsal

The v51 package generated a deterministic native Harbor task tree and reproduced
it byte-for-byte with `--check`. The unmodified Harbor grader then scored q001
and q031 directly from normal helper output:

| Question | Manifest gate | Evidence gate | nDCG@10 | MRR@10 | Recall@10 | Reward |
|---|---:|---:|---:|---:|---:|---:|
| q001 | 1.0 | 1.0 | 1.0 | 1.0 | 0.6667 | 1.0 |
| q031 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0000 | 1.0 |

Q001 has fifteen relevant papers, so `10 / 15 = 0.6667` is its maximum
Recall@10. The generated q031 directory is called `holdout` by the generic task
generator, but it is not an untouched holdout in this study; all GraphRAG qrels
were already exposed.

## Evidence boundary

These are definitive frozen-benchmark experts, not holdout-qualified
promotions. All forty questions and qrels were available during profile
construction. The result proves in-sample routing quality, exact evidence,
deterministic packaging, and response-time improvement for the fixed datasets.
It does not prove unseen-query generalization.

A future promotion-capable study must register new untouched questions before
mutation, keep them unavailable to profile construction and selection, freeze
the candidate digest, and release that holdout once. Until then, the new
experts are ranked first only in the explicitly retrospective tables.

## Reproduction

The deterministic profile builder, query adapter, evaluator, baselines, and
tests are:

- `scripts/build_supervised_profile_index.py`
- `adapters/query_expert_knowledge_supervised_profiles.py`
- `scripts/evaluate_definitive_expert.py`
- `scripts/audit_definitive_experts.py`
- `definitive-baselines.json`
- `tests/test_definitive_expert_profiles.py`

Generated skills and raw reports remain in the ignored, append-only directory
`evaluations/semantic-okf-specialized-experts/generated/20260728-definitive-profiles-03/`.
