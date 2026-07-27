# Tantivy Trace-Distillation Round 3

Status: **complete**. Decision: **retain both live skills**. This complete
round promoted neither consultation nor construction, so the declared stopping
criterion is satisfied.

## Prospective contract

The previously unused endocrine-hygiene benchmark supplied 20 development
questions, five separate cross-paper query holdout questions, and five separate
hard builder holdout questions. The cohorts are disjoint. Harbor 0.18.0 used
schema 2, one attempt, zero retries, exact evidence and mechanical gates, and
digest-locked skills. One interrupted query discovery job is retained as
append-only history but is excluded from every trace and decision.

## Query result

The bounded concept-type seed raised development reward from `0.788357` to
`0.862557`. On the unopened five-question holdout its mean also rose from
`0.681789` to `0.697527`, but one of the two cells regressed by `0.011854`.
The strict zero-regression gate therefore kept consultant digest
`sha256:896d038b16dd974411ef50bf91e5efead5e2589262058114b4bed4d8993f0c84`.

## Builder result

With that consultant frozen, exact structured interpretation ranges raised
development reward from `0.788357` to `0.810701`. The hard holdout rose from
`0.648749` to `0.690840` with no regressed cell.

The additional canonical gate rejected promotion. Two 890-file GraphRAG builds
were byte-identical, all 120 Top-10/replay/pool-100 queries completed, evidence
validity was 100%, and ranking determinism passed. Nevertheless, all-40
Recall@10 fell from 80.74% to 77.43% and nDCG@10 fell from 81.05% to 79.59%.
Hard-10 Recall@10 fell from 92.17% to 83.17%, MRR from 90.00% to 88.33%, and
nDCG from 80.54% to 77.43%. Builder digest
`sha256:8a5024734f62d4b53fe55b6b6f569d831513429460c0de8783ae1b47584de40a`
is retained.

## Final decision

Neither candidate was copied into the live skills. The canonical table remains
unchanged at 80.74% Recall@10, 93.75% MRR@10, and 81.05% nDCG@10 overall;
92.17%, 90.00%, and 80.54% on hard-10.
