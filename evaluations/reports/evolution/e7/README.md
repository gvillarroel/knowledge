# EnterpriseRAG stratified evolution E7

Status: sealed and running. The independent review passed all 32 registered
tasks, 36 runtime isolation probes and 224 production-verifier fixtures. The
native pipeline is executing development; the private gate remains unopened.

The latest [all-family progress audit](status-023/README.md) records two
completed searches and four qualified baselines. Classical now retains 60.10%
weighted nDCG@10, up from 55.04%. All three declared diversity variants tied,
ending that mechanism after three consecutive misses. Its first full round
completed with six retained gains, so a second round begins. Candidate018 tests
`bm25.b=0.25` on the retained candidate011 base.
Adaptive now retains 65.36%, up from 60.04%. Its twelfth variant gained with
association weight `0.175` and topic weight `0.1` on the retained `bm25.k1=3.0`,
title-weight `1.0` base, resetting the counter after two expansion misses.
The thirteenth gained recall but lost primary nDCG. The expansion catalog ends
with one consecutive miss; candidate014 starts relevance-diversity with
relevance weight `1.0` and both novelty weights at zero.
Entity Graph, Ensemble,
Graphify and Turso have not started and are excluded from completed opportunity counts.
The current audit contains 52 completed variants: 46 qualified measurements
and six Embeddings execution errors, plus four qualified native baselines.
The preceding [first audit](status-001/README.md),
[second audit](status-002/README.md), [third audit](status-003/README.md),
[fourth audit](status-004/README.md), [fifth audit](status-005/README.md),
[sixth audit](status-006/README.md), [seventh audit](status-007/README.md),
[eighth audit](status-008/README.md), [ninth audit](status-009/README.md),
[tenth audit](status-010/README.md), [eleventh audit](status-011/README.md),
[twelfth audit](status-012/README.md), [thirteenth audit](status-013/README.md),
[fourteenth audit](status-014/README.md), [fifteenth audit](status-015/README.md),
[sixteenth audit](status-016/README.md), [seventeenth audit](status-017/README.md),
[eighteenth audit](status-018/README.md), [nineteenth audit](status-019/README.md),
[twentieth audit](status-020/README.md), [twenty-first audit](status-021/README.md)
and [twenty-second audit](status-022/README.md)
remain unchanged.

The [Classical diversity stopping audit](classical-diversity-001/README.md)
replays the seventeen-variant prefix, its three qualified ties, first-round
gain and next sealed mutation. The [second Adaptive expansion tradeoff](adaptive-expansion-002/README.md)
records a 0.3298-point nDCG loss alongside gains of 0.7878 points in recall and
1.5403 points in full reference coverage. Its thirteen-variant prefix confirms
catalog exhaustion after all four expansion settings, rather than a three-miss
stop. Both family searches continue under the same frozen objective.

The [fourth Adaptive gain](adaptive-progress-004/README.md) adds 0.13 percentage
points over candidate009 and 5.33 over the initial baseline. Against candidate009,
5 eligible questions improve, 1 regresses and 106 tie; against the baseline,
30 improve, 5 regress and 77 tie. The
[category and application breakdown](adaptive-progress-004/subgroups.md) shows
Fireflies at 80.52% and Gmail at 71.70%. Every application-group mean is
nondecreasing against candidate009, while the question-level regression remains
visible. The exact twelve-variant prefix and next sealed contract replayed;
this is a development gain, not a final promotion.

The [completed-job CTA snapshot](development-cta-001/README.md) covers all 54
native jobs bound by status022, including four baselines and 50 variants.
Their durations sum to 17.82 job-hours, with 4.05 hours in the six failed
Embeddings attempts. This is accumulated job time, not campaign wall time or
billed time. Forty-eight jobs record zero native tokens and USD cost; six have
missing accounting fields. Complete cost remains unavailable, and orchestration
and machine costs are outside those native records.

The [Ensemble protection audit](ensemble-protection-001/README.md) verifies the
ranking opportunity of its quality weights with eight synthetic function cases.
The weights can change order, but preserve Adaptive's document set and cannot
refill a short set from auxiliary evidence. Ensemble construction can separately
change that protected set. These fixtures add no native Enterprise measurement
or completed family opportunity.

The [Graphify function audit](graphify-opportunity-001/README.md) exercises the
frozen query function with pinned local Graphify scoring and traversal on two
synthetic graphs. Fourteen depth cases show both a changing document set and
an unchanged top ten despite visiting more nodes. Four lexical fusion settings
produce three distinct orders. The audit also confirms that first enabling
fusion expands its candidate pools, and rank-decay variants explicitly set
lexical weight to one. These complete treatment changes must remain visible
when interpreting future native scores. No Graphify trial is counted here.

The [Classical source-group audit](classical-source-cap-001/README.md) identifies
an additional opportunity outside the frozen catalog. Its three diversified
routes cap results at one document per application and return five to nine
hits, while BM25 returns ten on all 120 questions. Twenty-four of the 112
eligible questions require multiple documents from one application. The
candidate015 tie confirms that zero novelty weights leave this cap active.
A digest-bound [follow-up plan](classical-source-cap-001/plan-review.md) separates
a cap-only treatment from a document-identity treatment. It has no new candidate
score or reserved independent validation; the live E7 protocol is unchanged.

The [provisional cross-family comparison](retained-cross-family-004/README.md)
aligns the four retained profiles from status022 across all question categories
and application groups. Among these four, Embeddings has the highest nDCG in
Confluence, GitHub and Slack; Adaptive in Fireflies; and Legacy in the other
five application groups. Legacy has the highest aggregate, while Embeddings
leads the project-related category. These descriptive development means use
matching question denominators and preserve exact ties. The four unmeasured
families are omitted, and the comparison does not change a selected profile.
The [first comparison](retained-cross-family-001/README.md),
[second comparison](retained-cross-family-002/README.md) and
[third comparison](retained-cross-family-003/README.md) remain unchanged.

The [first Adaptive expansion trial](adaptive-expansion-001/README.md) illustrates
a metric tradeoff: recall gains 0.0788 percentage points, but nDCG loses 0.8395
and MRR loses 1.1243 against candidate009. Full reference coverage is unchanged.
There are 6 improved, 5 regressed and 101 tied eligible questions, but the
weighted losses exceed the gains. The fixed nDCG objective retained candidate009
at that checkpoint. The ten-variant prefix and next zero-expansion contract
replayed exactly. The later candidate012 gain is reflected in the current matrix.

The [third Adaptive gain](adaptive-progress-003/README.md) reduces title weight
to `1.0` on the retained `bm25.k1=3.0` base. It gains 5.20 percentage points
over the initial baseline and 3.74 over candidate006. Against the baseline,
29 eligible questions improve, 6 regress and 77 tie; against candidate006,
the counts are 19, 6 and 87. The
[category and application breakdown](adaptive-progress-003/subgroups.md)
shows basic and semantic questions contributing 2.76 and 1.40 points to the
overall baseline gain. Gmail gains 12.64 points and Google Drive 7.91, while
the constrained category loses 2.43. The title catalog ends on a gain and
reset counter, followed by expansion. The nine-variant prefix and the next
sealed mutation were replayed exactly; this remains a development selection.

The [Classical expansion stopping audit](classical-expansion-002/README.md)
records the three qualified misses following candidate011. The last setting,
association weight `0.7` and topic weight `0.4`, scored 59.994413%, losing
0.103408 percentage points. Its paired counts against candidate011 are
3 improvements, 4 regressions and 105 ties. All four declared expansion
options were exercised, and the third consecutive miss ends this mechanism.
The fourteen-variant prefix and the next relevance-diversity mutation matched
the frozen scheduler and sealed contract. The complete family search continues.

The [zero-expansion Classical trial](classical-expansion-001/README.md) scored
60.095906%, just below the retained 60.097820%. The loss is 0.001915 percentage
points even though both display as 60.10% at two decimal places. One eligible
question improves, one regresses and 110 tie against candidate011. This is the
first qualified expansion miss; display rounding does not change the decision.
Adaptive's first title-weight trial, at `4.0` on its retained `bm25.k1=3.0`
base, scored 53.48%, losing 8.02 points against 61.49%. It is the first
qualified title miss. Both trials completed without execution errors and
retained their preceding profiles for the next tests.

The following Classical expansion trial, at association weight `0.175` and
topic weight `0.1`, scored 60.014757%, a loss of 0.083063 percentage points
against candidate011. Adaptive's following title-weight trial, at `8.0`,
scored 47.059863%, a loss of 14.433991 points against candidate006. Both
qualified with no execution errors or retries. Each was its mechanism's second
consecutive miss. The subsequent variants produced the Adaptive gain and the
Classical third miss documented above.

The [second Adaptive gain](adaptive-progress-002/README.md) sets `bm25.k1=3.0`
and gains 1.46 percentage points over the baseline, including 0.34 over
candidate005. Against the baseline, 24 eligible questions improve, 6 regress
and 82 tie; against candidate005, the counts are 11, 2 and 99. All four
aggregate retrieval metrics improve. The saturation catalog ended on this gain
with a reset miss counter, and title weighting followed. The
[category and application breakdown](adaptive-progress-002/subgroups.md)
shows GitHub gaining 6.50 points, Google Drive 2.38 and Confluence 1.28, while
Fireflies loses 0.14 and HubSpot loses 0.12. The profile remains provisional.

The [sixth Classical gain](classical-progress-006/README.md) reduces expansion
association weight to `0.0875` and topic weight to `0.05`. Fusion gains 5.06
percentage points over the initial baseline and 0.0831 over candidate010.
This small increment improves 2 eligible questions, regresses on none and
ties on 110 against the incumbent. The
[category and application breakdown](classical-progress-006/subgroups.md)
shows reduced loss on constrained questions and a small semantic-category
increment. The next variant set both expansion weights to zero and produced
the small measured loss documented above. Two further misses then ended the
mechanism with this same retained profile.

The [first Adaptive gain](adaptive-progress-001/README.md) sets `bm25.k1=2.0`
and gains 1.12 percentage points over the initial baseline. It improves 18
eligible questions, regresses on 7 and ties on 87. All four aggregate retrieval
metrics improve, and the miss counter resets. The
[category and application breakdown](adaptive-progress-001/subgroups.md)
shows that semantic questions contribute 0.75 points to the overall gain.
GitHub gains 5.57 points and Jira 0.72, while Fireflies loses 0.31, Google Drive
0.14 and HubSpot 0.12. The subsequent saturation setting produced the second
gain. This earlier development snapshot remains unchanged.

The [fifth Classical gain](classical-progress-005/README.md) reduces
`bm25.title_weight` to `1.0` on the retained `bm25.b=1.0`, `bm25.k1=3.0` base.
Fusion gains 4.97 percentage points over the initial baseline and 1.34 over
candidate007. Against the baseline, 19 eligible questions improve, 10 regress
and 83 tie; against candidate007, the counts are 9, 7 and 96. The title-weight
catalog ends with this gain and a reset counter. The next mechanism tested
expansion strength, starting with association weight `0.0875` and topic
weight `0.05`, and produced the sixth gain. All four diagnostic routes in
this fifth-gain snapshot improve against the baseline.
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
and 54.83% and were rejected before the later gains. All fourteen completed variants have
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
