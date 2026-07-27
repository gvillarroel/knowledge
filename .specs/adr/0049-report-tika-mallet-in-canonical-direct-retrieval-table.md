---
adr: "0049"
title: "ADR 0049: Report Tika and MALLET in the Canonical Direct-Retrieval Table"
summary: "Admit the replicated Tika/MALLET fusion result to the 40-question direct-retrieval comparison while keeping grounded Harbor evaluation and registry promotion explicitly pending."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - tika
  - mallet
  - evaluation
  - extraction
  - retrieval
---

# ADR 0049: Report Tika and MALLET in the Canonical Direct-Retrieval Table

## Status

Accepted.

This decision extends ADR 0044. It changes direct-retrieval reporting, not the
canonical eight-family Harbor registry, Tika's production status, or the
candidate's grounded-answer promotion state.

## Context

ADR 0044 authorized a bounded Semantic OKF experiment using Apache Tika
`4.0.0-beta-1` for extraction and Java MALLET `2.1.0` for topics. The initial
evidence covered only two fixtures and could not support a comparative ranking.

The candidate subsequently completed two clean canonical builds from the 15
GraphRAG papers. Both builds produced the same 15 record identities and bundle
inventory. An extraction audit compared the Tika text with the reviewed canonical
paper text and passed all 75 exact source, media type, raw-byte, raw-hash, and page
count gates. Its macro token recall was 98.79%, token precision was 93.69%, and
five-gram recall was 95.55%. The independent build reproduced all extraction
metrics exactly.

The direct evaluator then ran all 40 frozen questions at Top 10 and pool 100
against both builds. It established exact Top-10 replay, exact pool-100 replay,
exact Top-10 prefixes within both pool-100 runs, matching record identities, and
400/400 valid Top-10 evidence rows.

Grounded Harbor execution is a different measurement. Earlier consultation
treatments encountered one provider context-limit failure and therefore cannot be
combined into a ranking. A separately frozen bounded consultation treatment was
then rejected on its first model call with `usage_limit_reached`, before any agent
tokens or tool calls. Provider-failure placeholder values are not semantic scores.

## Decision

Report `tika_mallet_fusion` in
`evaluations/semantic-okf-ensemble/EVALUATION-CONCLUSIONS.md` as an experimental
direct-retrieval route.

Use the prospectively selected attempt-10 Top-10 report for the row. Report:

- 74.82% all-40 Recall@10;
- 87.50% all-40 MRR@10;
- 75.44% all-40 nDCG@10;
- 71.83% hard-10 Recall@10;
- 71.67% hard-10 MRR@10;
- 61.80% hard-10 nDCG@10;
- 100.00% exact evidence validity; and
- 86.36 ms P95 query latency after a separately reported 8,641.89 ms validation
  and loading setup.

The tracked retrieval audit binds both clean builds, all four Top-10 and pool-100
reports, the common record digest, and the common bundle inventory. The
independent Top-10 replicate measured 75.52 ms P95; timing variation does not
alter the exactly reproduced rankings, scores, evidence, or aggregate metrics.

Keep the candidate outside `families.json`. Direct-retrieval rankability does not
make the candidate eligible for a grounded Harbor ranking or registry promotion.
Grounded admission requires one new append-only, frozen prospective treatment
that completes all 40 questions exactly once without provider or evaluator
failure, passes the strict current-scorer audit, and receives separate semantic
review.

Do not retry or reinterpret the quota-rejected v4 cell while provider access
remains unavailable. The provider reported a reset at
`2026-07-29T17:08:54-04:00`; restored credits or the completed reset are external
preconditions for a new campaign.

## Consequences

Positive:

- the canonical table now contains a complete, evidence-backed Tika/MALLET
  comparator rather than smoke-test placeholders;
- extraction fidelity and direct retrieval remain separately observable;
- exact replicate and pool-prefix checks establish deterministic ranking; and
- the Semantic OKF authoritative record and evidence boundary remains intact.

Negative:

- the table includes another experimental route, so its non-registry status must
  remain explicit;
- the canonical extraction study covers PDF plus the earlier XLSX smoke fixture,
  not Tika's full format surface;
- the latency is an in-process diagnostic whose setup boundary differs from other
  implementations; and
- answer-level Harbor quality remains unknown until external model access returns
  and a clean 40-question treatment completes.
