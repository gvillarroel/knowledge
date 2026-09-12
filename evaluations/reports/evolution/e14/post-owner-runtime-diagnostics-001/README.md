# EnterpriseRAG E14: post-owner runtime diagnostics

Date: 2026-09-12. The bounded Entity Graph and Ensemble public runtime
diagnostics both passed after the E14 owner terminated and the native runtime
became quiescent. They establish exact parent/candidate behavior on their
declared public fixtures. They do not supply EnterpriseRAG retrieval scores,
qualify either family on the 6,000-document workload, or change the retained
ranking.

| Family | Diagnostic result | Public fixture | Exact behavior checked | EnterpriseRAG nDCG@10 x100 |
| --- | --- | --- | --- | --- |
| Entity Graph | Passed | 1,024 records; 8,388,608 body characters | Four builds, two validations, two deep inspections, eight paired route responses, four corruption rejections and two overwrite rejections | Unavailable |
| Ensemble | Passed | Four Markdown records; hashing embeddings | Four builds, two validations, three paired policy responses and four corruption rejections | Unavailable |

The Entity Graph candidate reproduced all 19 artifact files and all eight
reference responses across lexical, entity, traversal and fusion routes. Its
fixture produced 66,552 nonempty mentions and exercised bounded selection over
1,024 selected records. The Ensemble candidate reproduced all 35 artifact
files, all valid and corrupt reports, all three query policies and 53 nonempty
mentions for both parent and candidate. Both containers exited zero without an
out-of-memory event. Source packages and inputs remained unchanged.

These checks use small, public, purpose-built fixtures. Ensemble uses hashing
embeddings rather than the learned embedding provider in the EnterpriseRAG
workload. Entity Graph processes the declared 1,024-record synthetic fixture,
not the complete 6,000-document corpus. Neither diagnostic runs Harbor, calls a
language model, scores retrieval, opens validation, allocates a native first
measurement, adds a proposal charge, or records a quality miss.

## Retained measurable table

| Rank | Strategy | Weighted nDCG@10 x100 | Status |
| ---: | --- | ---: | --- |
| 1= | Legacy | 72.38 | Qualified |
| 1= | Turso | 72.38 | Qualified |
| 3 | Adaptive | 66.21 | Qualified |
| 4 | Graphify | 63.72 | Qualified |
| 5 | Embeddings | 63.51 | Qualified |
| 6 | Classical | 62.10 | Qualified |
| — | Entity Graph | — | Original start unqualified; software diagnostic passed |
| — | Ensemble | — | Original start unqualified; software diagnostic passed |

This table is the retained E14 development retrieval comparison on 120
stratified questions, 112 retrieval-eligible questions, 6,000 complete
documents and eligible population weight 470. It is not the public
EnterpriseRAG generated-answer Overall table. The latest score-changing source
remains [Graphify generation 16](../graphify-generation-016-001/comparison.md).

## Controller outcome and remaining gates

Graphify generation 24 scored 52.42 and completed the third consecutive
`fusion-rank-decay` miss. The owner then skipped duplicate profiles, closed
Graphify round 3 with `full-round-without-improvement`, and issued no generation
25 claim. The overall controller terminated fail-closed because Entity Graph
and Ensemble still lacked qualified starting measurements. It did not authorize
joint selection or private release.

All-eight full-workload qualification, the paired 16-trial joint development
replay, one frozen whole bundle, the 16-trial all-500 comparison and the
32-trial independent acceptance gate remain unfinished. A future native
qualification requires a separately registered prospective control with
preserved identities, resource limits, accounting and fresh independent
validation.

Application gate 061 remains current: 1,697 tests, 373 subtests and 90.5%
coverage. This report changes no application, canonical skill, dataset or
frozen runtime.

[Cost, time and quality](cta.md) · [Source-bound aggregate](aggregate.json) ·
[Graphify generation 24](../graphify-generation-024-001/README.md) ·
[E14 overview](../README.md)
