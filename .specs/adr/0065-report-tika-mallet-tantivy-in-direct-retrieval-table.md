---
adr: "0065"
title: "ADR 0065: Report Tika/MALLET/Tantivy in the Direct-Retrieval Table"
summary: "Admit the replicated Tika/MALLET/Tantivy fusion result to the frozen GraphRAG direct-retrieval comparison while retaining its experimental non-registry status."
status: "Accepted"
date: "2026-07-27"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, tika, mallet, tantivy, evaluation, retrieval]
---

# ADR 0065: Report Tika/MALLET/Tantivy in the Direct-Retrieval Table

## Status

Accepted. This extends ADRs 0049, 0055, and 0057. It changes deterministic
direct-retrieval reporting, not the candidate's grounded-answer result or
eight-family registry status.

## Context

ADR 0055 introduced the standalone read-only
`consult-semantic-okf-tika-mallet-tantivy` skill. It validates a Tika and
MALLET snapshot, builds a pathless Tantivy 0.26.0 index in memory, and exposes
native Tantivy, MALLET topic, PPMI association, and reciprocal-rank fusion
routes. Fusion was defined before this evaluation as the combination of the
other three rankings.

The existing Harbor inventory aggregated 154 development trials across only 15
distinct questions and many candidate revisions. Its contract, utility,
reward, and semantic outcomes could not supply Recall@10, MRR@10, nDCG@10, or
P95 under the frozen direct-retrieval comparison.

A new deterministic evaluator reused the same two independently reproduced
Tika/MALLET bundles, 40 questions, reviewed binary qrels, paper identities, and
evidence validator as the canonical comparison. It ran every route at Top 10
and pool 100 against both bundles after independent fixed-seed MALLET
rederivation.

The audit established:

- exact Top-10 rankings, scores, metrics, and evidence across both bundles;
- exact pool-100 replay and exact Top-10 prefixes in both pool runs;
- identical evaluator inputs, bundle inventory, and authoritative record
  digest;
- 400/400 valid fusion Top-10 evidence rows;
- Tantivy 0.26.0 native Rust runtime identity; and
- unchanged immutable bundles before and after every run.

The checked audit JSON has SHA-256
`eb20a9677913ecd3ef528edc23097f32238d7d40910f934c3dccf741d818bc18`.
Both bundles retained inventory SHA-256
`bc7db567bb8dfbbe3f3e80c2279f002bdc1e1af57d143bfc1c70707ab029d993`
and records SHA-256
`faac75af34f1a3bd67c10354fbf217850cd1b4d0468a93b1a90416e236e9286c`.

## Decision

Report `tika_mallet_tantivy_fusion` as an experimental route in the canonical
GraphRAG 40-question direct-retrieval table:

- 73.50% all-40 Recall@10;
- 84.79% all-40 MRR@10;
- 71.75% all-40 nDCG@10;
- 73.83% hard-10 Recall@10;
- 54.17% hard-10 MRR@10;
- 55.04% hard-10 nDCG@10;
- 100.00% exact evidence validity; and
- 470.74 ms P95 query latency after 7,257.02 ms of separately reported shared
  validation and loading setup.

Use the prospectively defined attempt-10 Top-10 result for the table. Keep the
independent Top-10 replay and both pool-100 runs as append-only supporting
evidence.

Do not interpret direct-retrieval rankability as grounded-answer promotion.
The combined Harbor evidence remains a separate, incomplete development
history with uneven question coverage.

## Consequences

Positive:

- the version that actually combines Tika, MALLET, and Tantivy now has a
  same-contract direct comparison;
- deterministic replay, pool-prefix parity, runtime identity, and exact
  evidence validity are independently checked; and
- the table no longer treats this implemented combination as unmeasured.

Negative:

- the selected fusion route underperforms standalone Tika/MALLET fusion on
  all-40 Recall@10, MRR@10, and nDCG@10;
- rebuilding the pathless Tantivy index per query raises P95 latency;
- the extraction study still covers the frozen 15-paper PDF corpus rather than
  Tika's complete format surface; and
- answer correctness and completeness remain outside this retrieval audit.
