# EnterpriseRAG stratified evolution E7

Status: sealed and running. The independent review passed all 32 registered
tasks, 36 runtime isolation probes and 224 production-verifier fixtures. The
native pipeline is executing development; the private gate remains unopened.

The [all-family progress audit](status-001/README.md), observed at 2026-09-08
16:23 UTC, records one completed search, three qualified baselines and two
verified live trials. Classical's baseline is 55.04% weighted nDCG@10 and its
first variant is running. Embeddings retains its 63.51% baseline while its
third variant runs after two execution failures. The five remaining families
have not started and are explicitly excluded from completed opportunity counts.

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

The [first semantic-segmentation runtime receipt](runtime-001/README.md)
records a completed Embeddings build timeout at the fixed 40-minute subprocess
limit. The failed candidate has no measured retrieval score and cannot replace
the 63.51% baseline. The next distinct variant continues under the same limits.

The study covers all eight knowledge families with 120 category-stratified
development questions and a fixed 6,000-document full-text corpus. The final
comparison covers all 500 public questions, of which 470 have original qrels.
The [strategy coverage matrix](strategy-coverage.md) lists every family's
mutation channel, primary route and predeclared mechanisms, including all
seven families whose work follows the completed Legacy search.
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
