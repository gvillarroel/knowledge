# EnterpriseRAG continuation E8

Status at 2026-09-09 10:18 UTC: independently reviewed, design-sealed and active.
Turso has its first retained gain. Four later or initial admissions were refused
before native dispatch; Graphify has one native construction timeout.
The native owner has revalidated all 66 completed historical jobs: 17 Legacy,
seven Embeddings, 23 Classical and 19 Adaptive. All imports retained the original
best candidates and executed zero new trials. The new
[Turso baseline](turso-baseline-001/README.md) completed at 45.43% weighted
nDCG@10; its [first candidate](turso-progress-001/README.md) improved to 72.08%,
a gain of 26.65 percentage points. Its next candidate and Adaptive's first E8
candidate were refused before dispatch while Classical was active.
Graphify's original
[baseline failed during construction](graphify-baseline-failure-001/README.md)
at the fixed 2,400-second limit and has no retrieval score.
Entity Graph and Ensemble were rejected before dispatch,
with zero native trials. The [independent diagnosis](dispatch-control-001/README.md)
confirmed that the sealed guard rejects Docker's legitimate Compose plugin
child. Their missing opportunities are not quality failures.
The private gate remains unopened.

Classical's [first completed continuation candidate](classical-progress-001/README.md)
raised title weight to 8 and regressed from its retained 61.89% to 38.78%
weighted nDCG@10. It qualified without execution errors, counted as one miss,
and retained the original `candidate-022`. The next
[expansion-strength candidate](classical-progress-002/README.md) disabled both
expansion weights and improved nDCG@10 to **62.10%**, a gain of 0.21 percentage
points over that incumbent. One eligible question improved, none regressed
and 111 tied. It is now retained, with the miss counter reset; remaining catalog
work is active. [Applications/categories](classical-progress-002/groups.md),
[routes](classical-progress-002/routes.md) and [CTA](classical-progress-002/cta.md)
preserve the exact paired evidence.
The [following expansion trial](classical-progress-003/README.md) restored the
default association/topic weights and regressed to 61.89%. It had no execution
error, retained `continuation-002` and recorded the first miss since that gain.
The [stronger expansion trial](classical-progress-004/README.md) then used
association/topic weights 0.7/0.4 and measured 60.13%, 1.98 percentage points
below that incumbent. It qualified without errors and recorded a second
consecutive miss. The 62.10% candidate remains retained.
The next [relevance-only reranking trial](classical-progress-005/README.md)
disabled source and topic novelty and tied that incumbent on all four primary
metrics. It qualified with zero errors and recorded the first miss in the new
`relevance-diversity` mechanism. This counter is separate from expansion's two
misses; the frozen controller continues the remaining declared opportunities.
The following [mild-diversity reranking trial](classical-progress-006/README.md)
used relevance/source/topic weights 0.9/0.05/0.05 and again tied all four primary
metrics. It qualified without execution errors and counted the second miss in
that mechanism. The same 62.10% incumbent remains retained; neither tie supplies
a new quality gain.
The [third reranking variant](classical-progress-007/README.md), with weights
0.5/0.25/0.25, also qualified and tied all four primary metrics. It records the
third consecutive miss, satisfying the declared mechanism stopping rule.
`continuation-002` remains retained at 62.10%; remaining outer-round catalog
opportunities continue under the same cumulative budget.
The next [length-normalization trial](classical-progress-008/README.md) started
the third round with `b=0.25`. It qualified at 60.89%, 1.21 percentage points
below the retained 62.10%. Three eligible questions improved, eleven regressed
and 98 tied. This records the first miss in that round's length mechanism;
`continuation-002` remains retained. Its [application/category evidence](classical-progress-008/groups.md)
and [CTA](classical-progress-008/cta.md) preserve the full paired comparison.
The following [zero length-normalization trial](classical-progress-009/README.md)
used `b=0` and qualified at 59.56%, 2.55 percentage points below the incumbent.
Six eligible questions improved, eighteen regressed and 88 tied. This is the
second miss in the third round's length mechanism, with zero execution errors
or retries. The same 62.10% candidate remains retained; the
[application/category comparison](classical-progress-009/groups.md) and
[CTA](classical-progress-009/cta.md) include the complete paired evidence.

E8 continues the remaining opportunities after the
[E7 interruption](../e7/interruption-001/README.md), preserving 66 completed
original jobs and two unavailable original profiles. It first measures native
baselines for Turso, Graphify, Entity Graph and Ensemble, then evolves those
families and continues Classical and Adaptive. Legacy and Embeddings keep their
completed searches as historical development evidence.

| Inherited family | Baseline nDCG@10 | Last retained nDCG@10 | Historical scope |
| --- | ---: | ---: | --- |
| Legacy | 61.11% | 72.38% | Completed E7 search |
| Embeddings | 63.51% | 63.51% | Baseline retained; six construction timeouts |
| Classical | 55.04% | 61.89% | Valid prefix through022;023 unavailable |
| Adaptive | 60.04% | 66.21% | Valid prefix through018;019 unavailable |

These are previously published E7 values, not new E8 measurements. The
[family index](../../../../docs/enterprise-family-report-index.md) and
[last four-family matrix](../e7/retained-cross-family-007/README.md) link to their
original category/application evidence. All retain the weighted 120-question,
112-eligible, 6,000-document development contract.

The [Embeddings workload audit](embeddings-window-workload-001/README.md)
independently reconstructs 264,738 requested preliminary semantic windows from
those public documents. Threshold changes occur after this encoding pass;
identical whole-text reuse could remove at most 0.221% of its requested inputs.
These are structural input counts, not timing or a proven timeout cause.
The six original failed trials and the 63.51% retained score remain unchanged.

| New E8 Turso measurement | nDCG@10 | Recall@10 | MRR@10 | Full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 45.43% | 54.48% | 46.88% | 48.28% |
| Retained continuation-001 | 72.08% | 82.51% | 71.61% | 77.26% |

This fifth measured family now has one qualified native candidate gain.
The original Turso route uses SQL substring presence; its declared nonempty
profile variants introduce in-memory BM25 over the canonical database records.
The [mechanism audit](../e7/turso-opportunity-001/README.md) describes that boundary.

The [five-family matrix](retained-cross-family-002/README.md) compares exact
retained aggregates across categories and applications. Legacy retains the
highest observed overall nDCG; Turso leads recall, MRR and full-qrel coverage
among these five, plus the Gmail and HubSpot groups. These are provisional
development comparisons. Turso's search has not reached a stopping rule.

The [cumulative CTA through Classical006](development-cta-001/README.md) binds
75 completed original jobs across E7 and E8: 68 qualified measurements and seven
construction errors. Their native durations sum to 26.09 job hours, including
4.73 hours in failed jobs. This fixed total excludes the two interrupted
originals, later/running jobs and host preparation. Missing token/cost telemetry
remains unknown; historical imports count no additional native trial.

The [Graphify scaling audit](graphify-scaling-001/README.md) preserves an isolated
neighbor-selection prototype with identical synthetic outputs and a 20.43-fold
function timing ratio at 800 records. A subsequent
[complete candidate](graphify-candidate-001/README.md) is now sealed with one
changed file and 150 exact synthetic comparisons. Native builder feasibility
and retrieval quality remain unmeasured. The
[versioned-reference decision](../../../../.specs/adr/0132-qualify-graphify-builder-before-consultation.md)
keeps this construction treatment separate from consultation evolution.
Before native execution, an [exact task-binding correction](graphify-task-binding-001/README.md)
also versions the verifier's one expected builder-file digest. The first
unexecuted proposal would reject the intended constructor as frozen-file drift;
questions, scoring and the mutable-path list remain unchanged.
The first [public host fixture run](graphify-fixture-failure-001/README.md)
stopped because its cross-layout comparator omitted the native physical
snapshot hash's layout-dependent meaning. The completed same-layout singleton
comparisons agreed, but the fixed design remains failed; a separately reviewed
replacement design retained its consumed costs and all required checks. That
[complete second design passed](graphify-fixture-success-002/README.md): all
eight paired layout cells, 48 constructions/check rebuilds, 330 reads and sixteen
declared corruption rejections completed in 301.75 host seconds. Original and
candidate packages agreed within layouts; verified graph/query semantics agreed
across layouts. The following [two environment probes](graphify-executor-probes-001/README.md)
passed with the exact 252-file candidate, pinned images, effective CPU/memory
limits and declared read-only mounts. They consumed no native trial. Actual
Harbor-generated access and full-workload qualification still require the
separately reviewed native caller; retrieval quality remains unmeasured.
That [caller implementation review has now passed](graphify-native-caller-review-001/README.md)
450 isolated cases. Its original five defects and corrected source commitments
are preserved. Complete terminal-history review, ordinary study design sealing
and a separate independent admission remain required before its one native trial.
The [common public task bindings](aggregate-public-task-bindings-001/README.md)
are also prepared and independently reviewed for all eight strategies, covering
sixteen task roots. Each recognizes the exact fixed builder through one digest
change while preserving every other contract value and seven other files.
Both public roles retain their original exposure and weighting; all 120
development question identities overlap the all-500 workload. The reproduced
task trees and Harbor identities agree. These authoring results add no native
trial or quality gain and become usable only after the fixed feasibility and
separate continuation gates.

The continuation preserves cumulative attempts and rounds, excludes both
interrupted profiles from new dispatch, and requires all-eight joint replay,
one frozen all-500 comparison and the one-way whole-bundle private gate.
The all-500 execution profile prospectively permits 10,800 seconds for both
arms; it supplies no final measurement yet. Raw data and native artifacts remain
ignored under `tmp/e8/`.

The missing baselines prevent E8 from satisfying its all-eight joint gate.
The existing controller continues independent lanes under its sealed rules.
Corrected execution requires a prospective study after E8 becomes terminal,
with all completed evidence, consumed budgets and unavailable profiles retained.
The [control decision](../../../../.specs/adr/0131-correct-sealed-enterprise-admission-prospectively.md)
does not authorize an in-place guard change or a new private release.
The [prospective classifier review](prospective-control-001/README.md) passed
23 scope tests, 36 subtests, ten independent negative probes and a genuine live
parent/plugin comparison. Its source is separate from E8 and awaits a future
complete caller and study review.

The independent review verified 32 unchanged task roots, all 66 historical
job/skill inventories, 17 custody-guard checks and five actual image/resource
isolation probes. The maintained organizer accepted the complete review and
sealed execution contract SHA-256
`033aa7e01db8ed05bf306171573c116c46fdc2fa314b840ddbe1eea07809fb67`.
The review directory digest is
`4660244022088d6d157a67562778bd326cbf9437a96fe1920eba0bb45f1e2300`.
Those preparation checks did not exercise the native long-lived
`docker-compose` child visible during live execution. The subsequent diagnosis
records that coverage gap while preserving the original review unchanged.
Neither review supplies retrieval scores or measured all-500 completion.

The [family progress publisher](../../../../evaluations/publish_enterprise_family_progress.py)
requires an exact native comparison and replays cumulative decisions before
publishing a completed candidate prefix. It distinguishes gain over baseline
from gain over the actual previous incumbent and includes application/category,
route and CTA views. The latest implementation gate passed 1,609 tests and
270 subtests with
90.7% application coverage. This verification does not supply retrieval scores.

[Operating guide](../../../../docs/enterprise-continuation.md) ·
[Decision](../../../../.specs/adr/0130-continue-interrupted-enterprise-search-prospectively.md) ·
[Original study](../e7/README.md)
