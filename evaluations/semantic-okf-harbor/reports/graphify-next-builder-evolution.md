# Graphify Next Builder Evolution

Date: 2026-07-20

Decision: make the reciprocal cross-partition builder the implementation of
`build-semantic-okf-graphify`, keep `consult-semantic-okf-graphify` unchanged,
and retain `build-semantic-okf-graphify-next` as a retrospective candidate with
capped reciprocal documentation-reference bridges.

## Promotion boundary

- The previously accepted builder is now the official `build-semantic-okf-graphify` skill.
- The official graph has 6,390 nodes and 6,419 edges; 30 edges are regenerated `harbor-lexical-similarity` bridges.
- The historical `build-semantic-okf-harbor-graphify` package remains independently installable as campaign evidence.
- `consult-semantic-okf-graphify` is byte-identical to the pre-promotion package.

## Retrospective candidate comparison

All rows use the same 40 Astro questions and the unchanged consultation skill.
Because the original holdout had already been opened, these results are
retrospective and do not constitute a new prospective holdout claim.

| Builder mutation | R@10 | R@20 | Hard R@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms | p95 ms | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Official reciprocal lexical K=1 | 77.3% | 78.1% | 57.5% | **0.579** | 0.578 | 301/301 | **81.6** | **113.3** | Official control |
| Reciprocal lexical K=2 | 77.3% | 79.0% | 57.5% | 0.579 | 0.577 | 353/353 | 87.2 | 125.1 | Reject |
| Reciprocal lexical K=3 | 76.7% | 79.0% | 57.5% | 0.577 | 0.573 | 408/408 | 113.7 | 234.7 | Reject |
| K=1 plus title/record-ID identity | 76.7% | 78.1% | 57.5% | 0.577 | 0.572 | 352/352 | 86.9 | 120.8 | Reject |
| K=1 plus uncapped reciprocal references | 78.1% | **83.8%** | **60.8%** | 0.573 | 0.583 | 516/516 | 92.9 | 135.4 | Reject: hub displacement |
| K=1 plus reciprocal references, degree cap 5 | 79.0% | 80.6% | **60.8%** | 0.578 | 0.585 | 336/336 | 94.0 | 132.6 | Reject: lower recall than cap 6 |
| K=1 plus reciprocal references, degree cap 6 | **80.6%** | 83.1% | **60.8%** | 0.576 | **0.591** | 449/449 | 88.5 | 127.8 | Freeze as next candidate |
| Cap 6 plus title root labels | **80.6%** | **84.0%** | **60.8%** | 0.576 | 0.591 | 449/449 | 171.5 | 282.4 | Reject: no primary gain, large latency regression |

## Frozen candidate

The candidate retains the official reciprocal lexical K=1 graph and adds only
mutual internal documentation references whose endpoints have reciprocal-reference
degree at most six. Routes are derived from authoritative record IDs and links
are parsed from authoritative record bodies. One-way references and higher-degree
hubs are excluded.

Two independent builds produce graph logical SHA-256
`ab17730bb536da30c6c20c74bdc80c6c9d86e09a8171ace687ed92e97224587a`,
with 6,390 nodes, 6,494 edges, zero orphans, and 416 records. The unchanged
consult validator accepts the candidate bundle. Relative to the official
control, Recall@10 improves by 3.33 percentage points, hard Recall@10 by 3.33
points, and nDCG@10 by 0.0132; MRR@10 decreases by 0.0029 and mean latency rises
by 7.0 ms.

The candidate is frozen for a future prospective dataset or holdout. It is not
promoted over the newly official builder from this retrospective evidence alone.

## Harbor tracer status

The q032 WSL rehearsal passed and bound the candidate bundle tree SHA-256
`c1907df36eae772e0f71c5e27187474179860d0106cfedb293242da1c32355fc`
to the unchanged consult tree SHA-256
`f27bf956b8656f62c3de8bf883a15a3cd3a60674826cabbf814f7b027f32917f`.
Authentication was not serialized. The first live invocation stopped before
trial creation because Docker was unavailable and remains preserved as a
non-resumable infrastructure attempt. After Docker recovery, a new append-only
Harbor 0.18.0 job completed one q032 trial with reward `0.000`. Retrieval reached
complete qrel coverage, MRR `1.000`, and nDCG `1.000`, but the unchanged answer
path failed `response_contract`, `reference_validity`, and
`all_evidence_valid`. The completed semantic failure is not eligible for the
external-failure resume path.

## Cross-dataset all-evolver audit

The GraphRAG figures below are development diagnostics over the 24-question
discovery cohort, using the unchanged consultant at depth two and a 20-record
candidate pool before distinct-paper scoring. They are not Harbor rewards and
do not open the six-question holdout for candidate selection.

| Builder mutation | Added graph edges | Papers R@10 | Papers R@20 | Papers MRR | Papers nDCG@10 | Unchanged consult | Decision |
|---|---:|---:|---:|---:|---:|---|---|
| Current next: lexical K=1 + capped reciprocal references | 0 on papers | **66.46%** | **67.31%** | **0.851** | **0.717** | Pass | Keep Pareto incumbent |
| Same-paper claim chains | 788 | 66.46% | 67.31% | 0.851 | 0.717 | Pass in-memory | Reject: no effect |
| Cross-paper dimension round-robin | 819 | 66.46% | 67.31% | 0.851 | 0.717 | Pass in-memory | Reject: no effect |
| Reciprocal dimension Jaccard | 98 | 66.46% | 67.31% | 0.851 | 0.717 | Pass in-memory | Reject: no effect |
| Dimension round-robin + same-paper chains | 1,607 | 66.46% | 67.31% | 0.851 | 0.717 | Pass in-memory | Reject: density without gain |
| Record or related-paper root labels | 0 | 66.00% | 66.83% | 0.851 | 0.714 | Pass in-memory | Reject: retrieval regression |
| Lexical semantic-anchor bridges | 215 | 63.55% | 63.83% | 0.851 | 0.698 | Pass in-memory | Reject: retrieval regression |
| Lexical title-anchor bridges | 215 | 63.37% | 63.65% | 0.851 | 0.696 | Pass in-memory | Reject: retrieval regression |
| Related-paper heading in temporary views | 0 | Not scored | Not scored | Not scored | Not scored | **Fail** | Reject: view-digest contract break |

The current next bundle and official bundle are byte-different skills but emit
the same GraphRAG graph: 10,797 nodes, 13,504 edges, and logical SHA-256
`9d3574cee7b42825d9b72e1a1526c31ed24aa127f8041be86bb33d12ad9b632`.
This is a verified no-regression result, not a GraphRAG improvement claim.

## Builder-only Harbor follow-up

A later builder-only campaign tested bounded authoritative search text on
existing root nodes. It improved both development tasks and became the sole
development Pareto candidate, but regressed the Astro holdout reward by
`0.003447`. The strict no-task-regression gate therefore rejected promotion.
See `graphify-next-all-evolvers-20260720.md` and ADR 0041 for the complete
cross-dataset table and evolution-engine audit.

GEPA and trace distillation cannot causally mutate this builder from the
available q032 job because the job installs only the consultant, contains one
unique task, and the failure is in the response contract. Native population,
reflective Pareto, and operator coevolution likewise require one candidate
skill per SHA-bound Harbor job; the canonical build-consult task installs two
skills. Metaskill evolution requires a producer-published append-only policy
ledger, which this campaign does not have. These engines therefore fail closed
instead of manufacturing projections from the local diagnostics. Candidate
realization was exercised: it sealed and verified the related-paper-heading
mutation before the unchanged consultant rejected its view digests.
