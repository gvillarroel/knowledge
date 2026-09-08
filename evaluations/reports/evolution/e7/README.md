# EnterpriseRAG stratified evolution E7

Status: sealed and running. The independent review passed all 32 registered
tasks, 36 runtime isolation probes and 224 production-verifier fixtures. The
native pipeline is executing development; the private gate remains unopened.

The [all-family progress audit](status-005/README.md), observed at 2026-09-08
17:42 UTC, records one completed search, three qualified baselines and two
verified live trials. Classical now retains 56.06% weighted nDCG@10, up from
55.04%, while its fourth variant runs. The five remaining families
have not started and are explicitly excluded from completed opportunity counts.
The preceding [first audit](status-001/README.md),
[second audit](status-002/README.md), [third audit](status-003/README.md) and
[fourth audit](status-004/README.md)
remain unchanged.

The [first Classical gain](classical-progress-001/README.md) changes the
construction profile to `bm25.b=0.25`. Its fixed fusion route gains 1.02
percentage points: 8 eligible questions improve, 8 regress and 96 tie.
The report includes all four diagnostic routes and measured build/runtime
costs. This is a provisional development improvement; the family search
and all-500 measurement remain pending.
The following `bm25.b=0` and `bm25.b=0.5` variants scored 54.30% and 54.83%
and were rejected, leaving candidate001 retained and two consecutive misses.
Both completed without execution errors, so their lower scores are measured
quality results. The next predeclared length-normalization variant is running.

The [Embeddings mechanism transition](runtime-002/README.md),
observed at 16:54 UTC, records three original build timeouts at semantic
thresholds 95, 90 and 80. The three-miss rule stopped that mechanism.
The first neighboring-sentence context candidate, with buffer size 2,
subsequently exceeded the same construction limit. It is the first miss of
that mechanism, and the next distinct variant with buffer size 3 is running.
Embeddings retains its 63.51% baseline. The three segmentation failures
consumed 121.62 minutes; all four failed variants have no retrieval quality
measurement and were not retried.

The [completed Legacy search](legacy-complete-001/README.md) retained 72.38%
weighted development nDCG@10, up from 61.11% (+11.27 percentage points).
Its 16 variants and two catalog rounds ended with a complete non-improving
round. All 17 original jobs qualified without execution errors, and the
entire selection and stopping history was replayed against native evidence.
The other seven families, joint replay, final all-500 comparison and private
gate remain pending. No E7 retrieval profile is promoted.

The earlier [first increment](progress-001/README.md), [saturation adjustment](progress-002/README.md)
and [title-weight increment](progress-003/README.md) remain separately preserved.

The [paired Legacy breakdown](legacy-subgroups-001/README.md) shows 46 improved,
9 regressed and 57 tied eligible questions. It includes every question category
and all nine overlapping application groups, with their sample sizes and
sampling weights. The aggregate gain does not hide individual regressions.

The [first semantic-segmentation timeout receipt](runtime-001/README.md)
remains preserved. All four failures used the same fixed 40-minute builder
subprocess limit.

The study covers all eight knowledge families with 120 category-stratified
development questions and a fixed 6,000-document full-text corpus. The final
comparison covers all 500 public questions, of which 470 have original qrels.
The [strategy coverage matrix](strategy-coverage.md) lists every family's
mutation channel, primary route and predeclared mechanisms, including all
seven families whose work follows the completed Legacy search.
The [configuration audit](catalog-audit-001/README.md) checks the 117 declared
variants and records a conditional Adaptive protection limit. These synthetic
checks do not add to the native opportunity or performance counts.
This is an internal, reference-enriched retrieval experiment. It does not
replace the [full-corpus Classical/Luna report](../../enterprise-classical-full/README.md)
and does not establish an official public rank or answer Overall score.

Every mechanism follows the three-consecutive-miss rule. Improving catalog
rounds repeat, with at most five rounds; a full round without improvement
terminates a family. All eight selected configurations must reproduce jointly
and freeze before the final comparison and one terminal transfer gate.

Datasets, task contracts, private validation, native traces and candidates are
ignored under `tmp/e7/`. This tracked directory is reserved for reviewed family,
route, category, application, CTA and general comparison reports.

[Study guide](../../../../docs/enterprise-stratified-evolution.md) ·
[Decision](../../../../.specs/adr/0129-stratified-enterprise-family-evolution-and-joint-gate.md) ·
[Evolution index](../README.md)
