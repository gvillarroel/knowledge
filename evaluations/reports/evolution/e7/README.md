# EnterpriseRAG stratified evolution E7

Status: sealed and running. The independent review passed all 32 registered
tasks, 36 runtime isolation probes and 224 production-verifier fixtures. The
native pipeline is executing development; the private gate remains unopened.

The latest [all-family progress audit](status-015/README.md) records two
completed searches and four qualified baselines. Classical now retains 60.01%
weighted nDCG@10, up from 55.04%, while its eleventh variant runs. Adaptive
now retains 61.15%, up from 60.04%, after its fifth variant improved with
`bm25.k1=2.0`. Its sixth variant is running with `bm25.k1=3.0`.
Entity Graph, Ensemble,
Graphify and Turso have not started and are excluded from completed opportunity counts.
The preceding [first audit](status-001/README.md),
[second audit](status-002/README.md), [third audit](status-003/README.md),
[fourth audit](status-004/README.md), [fifth audit](status-005/README.md),
[sixth audit](status-006/README.md), [seventh audit](status-007/README.md),
[eighth audit](status-008/README.md), [ninth audit](status-009/README.md),
[tenth audit](status-010/README.md), [eleventh audit](status-011/README.md),
[twelfth audit](status-012/README.md), [thirteenth audit](status-013/README.md)
and [fourteenth audit](status-014/README.md)
remain unchanged.

The [provisional cross-family comparison](retained-cross-family-001/README.md)
aligns the four retained profiles from status015 across all question categories
and application groups. Among these four, Embeddings has the highest nDCG in
Confluence, GitHub and Slack; Adaptive in Fireflies; and Legacy in the other
five application groups. Legacy has the highest aggregate, while Embeddings
leads the project-related category. These descriptive development means use
matching question denominators and preserve exact ties. The four unmeasured
families are omitted, and the comparison does not change a selected profile.

The [first Adaptive gain](adaptive-progress-001/README.md) sets `bm25.k1=2.0`
and gains 1.12 percentage points over the initial baseline. It improves 18
eligible questions, regresses on 7 and ties on 87. All four aggregate retrieval
metrics improve, and the miss counter resets. The
[category and application breakdown](adaptive-progress-001/subgroups.md)
shows that semantic questions contribute 0.75 points to the overall gain.
GitHub gains 5.57 points and Jira 0.72, while Fireflies loses 0.31, Google Drive
0.14 and HubSpot 0.12. The remaining saturation variant and later mechanisms
still have to complete; this is a development selection.

The [fifth Classical gain](classical-progress-005/README.md) reduces
`bm25.title_weight` to `1.0` on the retained `bm25.b=1.0`, `bm25.k1=3.0` base.
Fusion gains 4.97 percentage points over the initial baseline and 1.34 over
candidate007. Against the baseline, 19 eligible questions improve, 10 regress
and 83 tie; against candidate007, the counts are 9, 7 and 96. The title-weight
catalog ends with this gain and a reset counter. The next mechanism tests
expansion strength, starting with association weight `0.0875` and topic
weight `0.05`. All four diagnostic routes improve against the baseline.
The [category and application breakdown](classical-progress-005/subgroups.md)
shows contributions of 3.31 points from basic questions and 1.11 from semantic
questions to the 4.97-point overall gain. Linear gains 11.27 points, GitHub
10.68 and Slack 8.44, while Confluence loses 2.18 and Fireflies loses 0.64.
These overlapping application groups describe development results; they do
not change the selected profile or establish transfer performance.

The [fourth Classical gain](classical-progress-004/README.md) combines
`bm25.b=1.0` with `bm25.k1=3.0`. Fusion gains 3.63 percentage points over the
baseline and 0.43 over candidate006. It improves 15 eligible questions,
regresses on 8 and ties on 89. The finite saturation catalog ends with this
gain and a reset miss counter; the next mechanism tested title weighting.
This transition follows catalog exhaustion,
not three consecutive misses.
The [first title-weight mutation](classical-title-001/README.md), at `4.0`,
scored 50.59%, a measured loss of 8.08 points against the incumbent. It
improves 2 questions, regresses on 22 and ties on 88; all four routes decline.
The next title weight, `8.0`, scored 42.81%, the second consecutive qualified
miss. Both title variants completed without execution errors. The later
weight `1.0` produced the fifth gain and replaced candidate007.
The [category and application breakdown](classical-progress-004/subgroups.md)
shows that the basic category contributes 2.94 of the 3.63-point overall gain.
Linear gains 11.27 points, GitHub 8.57 and Gmail 5.21, while Fireflies loses
1.25 and Jira loses 1.17. Application groups overlap, and the profile remains
a development selection pending the whole-bundle gates.

The [third Classical gain](classical-progress-003/README.md) combines
`bm25.b=1.0` with `bm25.k1=2.0`. Fusion gains 3.20 percentage points over the
baseline and 1.14 over candidate004. It improves 13 eligible questions,
regresses on 4 and ties on 95. All four retrieval metrics improve in aggregate;
the miss counter reset before the subsequent `bm25.k1=3.0` gain.
The [paired category and application breakdown](classical-progress-003/subgroups.md)
shows that two basic questions contribute 2.33 of the 3.20-point overall gain.
Linear gains 10.53 points, GitHub 9.95 and Slack 3.75, while Confluence loses
0.34 and Jira loses 0.24. These are descriptive development results with
overlapping application groups, not a new selection rule.

The [second Classical gain](classical-progress-002/README.md) sets
`bm25.b=1.0`. The fixed fusion route gains 2.06 percentage points over the
baseline and 1.04 over the previous retained setting. Against the baseline,
11 eligible questions improve, 2 regress and 99 tie. All four diagnostic
routes, build time and original native runtime are included in the report.
The fourth variant replaced candidate001 and reset the miss counter.
The finite length-normalization catalog was exhausted before BM25 saturation
began. Its first variant, `bm25.k1=0.6`, completed without execution errors
at 54.23%, below the then-retained 57.10%. That miss preceded the third gain.
The change from length normalization to saturation followed catalog exhaustion,
not a third consecutive miss.

The [first Classical gain](classical-progress-001/README.md), at `bm25.b=0.25`,
remains preserved. The next `bm25.b=0` and `bm25.b=0.5` variants scored 54.30%
and 54.83% and were rejected before the later gains. All ten completed variants have
qualified measurements with no execution errors. The full family search and
all-500 comparison remain pending.

The [paired Classical breakdown](classical-subgroups-001/README.md) describes
candidate004 by question category and all nine application groups. GitHub
gains 10.92 points, while Confluence loses 1.86 and Slack loses 0.54. One
improved basic question contributes 1.55 of the 2.06 points of overall gain
under the frozen sampling weights. This snapshot exposes the concentration
of the gain and subgroup regressions without changing the retained profile.

The [Adaptive baseline](adaptive-baseline-001/README.md) records 60.04%
nDCG@10, 69.19% recall@10, 60.70% MRR@10 and 62.39% full qrel coverage@10.
Its native job completed in 23.13 minutes with no execution errors or retries.
This is an initial measurement, not an improvement. The
[three length-normalization variants](adaptive-length-001/README.md),
`bm25.b=0.25`, `0.0` and `0.5`, scored 59.69%, 58.00% and 59.64% with no
execution errors. The third consecutive miss stopped this mechanism and
skipped the untested `bm25.b=1.0` setting in this pass. Replaying the exact
three-attempt prefix reproduces the next sealed mutation, `bm25.k1=0.6`.
That saturation variant then scored 58.35% without execution errors, the first
miss of the new mechanism. The next setting, `bm25.k1=2.0`, produced the first
Adaptive gain and replaced the baseline. The remaining mechanisms and complete
family stopping history still have to run.

The [completed Embeddings search](embeddings-complete-001/README.md) retains
its 63.51% baseline. Six distinct construction variants exceeded the same
40-minute builder limit before retrieval could be measured. Three consecutive
misses stopped semantic segmentation and three stopped neighboring-sentence
context. The complete round had no improvement, and its native history was
replayed against the frozen controller. The failed original jobs consumed
243.17 minutes in total; no retrieval score was invented and no trial was retried.
This establishes a budget limitation for the tested profiles, not worse
retrieval relevance for semantic chunking in general. The earlier
[three-miss mechanism transition](runtime-002/README.md) remains preserved.

The [completed Legacy search](legacy-complete-001/README.md) retained 72.38%
weighted development nDCG@10, up from 61.11% (+11.27 percentage points).
Its 16 variants and two catalog rounds ended with a complete non-improving
round. All 17 original jobs qualified without execution errors, and the
entire selection and stopping history was replayed against native evidence.
The six remaining family searches, joint replay, final all-500 comparison
and private gate remain pending. No E7 retrieval profile is promoted.

The earlier [first increment](progress-001/README.md), [saturation adjustment](progress-002/README.md)
and [title-weight increment](progress-003/README.md) remain separately preserved.

The [paired Legacy breakdown](legacy-subgroups-001/README.md) shows 46 improved,
9 regressed and 57 tied eligible questions. It includes every question category
and all nine overlapping application groups, with their sample sizes and
sampling weights. The aggregate gain does not hide individual regressions.

The [first semantic-segmentation timeout receipt](runtime-001/README.md)
remains preserved. All six failures used the same fixed 40-minute builder
subprocess limit.

The study covers all eight knowledge families with 120 category-stratified
development questions and a fixed 6,000-document full-text corpus. The final
comparison covers all 500 public questions, of which 470 have original qrels.
The [strategy coverage matrix](strategy-coverage.md) lists every family's
mutation channel, primary route and predeclared mechanisms.
The [configuration audit](catalog-audit-001/README.md) checks the 117 declared
variants and records a conditional Adaptive protection limit. These synthetic
checks do not add to the native opportunity or performance counts.
The [final runtime readiness audit](runtime-readiness-001/README.md) uses
original query timings and the frozen category weights to project the cost
of all 500 queries. Classical's baseline projects to 75.84 minutes against
the declared 60-minute agent limit; Adaptive's baseline projects to 57.54.
These are conditional estimates, not completed all-500 runs or observed
failures. The audit checks all eight final task descriptors and leaves the
native campaign unchanged.
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
