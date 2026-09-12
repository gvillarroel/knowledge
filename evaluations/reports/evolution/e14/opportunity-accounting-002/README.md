# EnterpriseRAG E14: five catalog stops and remaining work

Snapshot: **2026-09-12 03:39:49 UTC**. This fixed inventory includes published
Turso generation 15, Adaptive generation 10 and Graphify generation 6, plus
the original owner's terminal family records. It supersedes the earlier
inventory for current status while preserving that historical snapshot.

**Five families have recorded catalog stops, six have qualified retrieval
references, and three still lack a catalog closure.** These counts describe
different requirements. Among the five stopped catalogs, Adaptive and Classical
each retain one historical hypothesis without valid fitness. The study is
incomplete and no canonical skill is promoted.

## All eight strategies

Scores are the published retained nDCG@10 values multiplied by 100.

| Family | Retained score | Reserved proposals / cap | Catalog status | Historical measurement limitation |
| --- | ---: | ---: | --- | --- |
| Legacy | 72.38 | 16 / 55 | Inherited round stop; current reference qualified | No permanently unavailable original |
| Turso | 72.38 | 16 / 55 | Round 2 closed without improvement | No permanently unavailable original |
| Adaptive | 66.21 | 29 / 100 | Round 2 closed without improvement | One permanently unavailable original |
| Embeddings | 63.51 | 6 / 40 | Inherited round stop; current reference qualified | No permanently unavailable original |
| Classical | 62.10 | 37 / 85 | Inherited round stop; current reference qualified | One permanently unavailable original |
| Graphify | 27.94 | 7 / 65 | Generation 6 complete; generation 7 issued | Search remains open |
| Ensemble | Unavailable | 3 / 105 | No qualified family completion | Valid full-workload evidence is still missing |
| Entity Graph | Unavailable | 9 / 80 | No qualified family completion | Valid full-workload evidence is still missing |

The [general application and category comparison](../graphify-generation-004-001/comparison.md)
is unchanged. Embeddings leads Confluence, GitHub and Slack; Classical leads
Fireflies and Linear; Legacy and Turso share the highest values for the other
five application cohorts. Application cohorts overlap. These descriptive
leaders do not establish a router or statistical significance.

## What closed after the last scored observations

[Turso generation 15](../turso-generation-015-001/README.md) scored **69.72**
against **72.38** retained. It was the third consecutive unique evaluable miss
for length normalization in round 2. The fourth listed normalization variant
was left unissued under the stop rule. The owner then visited the three
remaining title-weight settings, recognized all three complete profiles as
already seen, and skipped them. With no improvement in the full second round,
it recorded the catalog stop.

[Adaptive generation 10](../adaptive-generation-010-001/README.md) scored
**66.04** against **66.21** retained and reached the third expansion-strength
miss. The owner subsequently skipped six already-seen profiles across its
remaining mechanisms and recorded a full second round without improvement.

Those final callbacks added **zero proposals, zero native observations and
zero quality misses**. A duplicate is not another failed evaluation. The last
scored progress files still describe the state before those callbacks; this
inventory uses the separately verified terminal family records.

Legacy, Embeddings and Classical preserve their earlier catalog stops and
their qualified E14 references. Their native starting reports remain available
for [Legacy](../legacy-starting-qualified-001/README.md),
[Embeddings](../embeddings-starting-qualified-001/README.md), and
[Classical](../classical-starting-qualified-001/README.md).

## Historical fitness gaps remain explicit

Adaptive's original `candidate-019` and Classical's original
`candidate-023` have **unavailable fitness**, with reissue explicitly
disallowed. Their exact profile commitments remain in the aggregate. Neither
identity was retried, remapped, assigned zero fitness, or counted as a new
quality miss.

A finite catalog stop therefore does not prove that every historical
hypothesis received a valid measurement. The owner's
`complete_hypothesis_coverage` flag is false for these two families. This
report preserves those limitations and does not grant a new recovery
admission or reopen closed allowances.

## Accounting and outstanding work

The **123 reserved proposals** comprise **91 inherited reservations**,
**30 new E14 charges**, and the two existing extra construction reservations,
one each for Entity Graph and Ensemble. The 32 E14 claim files include two
previously charged pending identities; those identities add no second charge.

The five catalog stops leave **231 closed, nontransferable unused slots**:
39 for Legacy, 39 for Turso, 71 for Adaptive, 34 for Embeddings and 48 for
Classical. With a combined cap of 585, the current snapshot leaves **at most
231 additional family-bound opportunities**: 58 for Graphify, 102 for Ensemble
and 71 for Entity Graph. The finite catalogs, duplicate checks, three-miss
rule and five-round ceiling can stop those searches earlier. This upper bound
is neither a required trial count nor a completion percentage.

The [earlier inventory](../opportunity-accounting-001/README.md) remains an
immutable record of its 02:07 UTC snapshot. Its 119 reservations and 121
closed slots are historical values. Native allocation counts are not refreshed
or inferred from proposal counts in either inventory.

Graphify generation 7 is testing lexical/graph fusion. The prepared
[Entity candidate](../../candidates/entity-bounded-selection-001/README.md) and
[Ensemble candidate](../../candidates/ensemble-mention-automaton-transfer-001/README.md)
retain their software evidence and original reservations; both still need
valid full-workload measurement. Execution errors do not exhaust their
remaining hypotheses.

The full objective still requires the remaining family qualification and
opportunity obligations, the **16-trial paired joint development replay**,
**one whole-bundle freeze**, the **16-trial all-500 comparison**, and
**32-trial independent acceptance**. Validation remains sealed.

## Verification and metric scope

The closure audit verified **461 source bindings** and reproduced each
terminal state from its already normalized, reconciled and published native
prefix. Only duplicate skips and terminal transitions were replayed in memory;
an unseen profile would reject the closure claim. Original native winners,
archive/config pointers, claims, seen profiles and unavailable identities
matched exactly. Seven focused software tests passed, including rejection of
premature closure, unresolved attempts, budget mislabeling and schema drift.

Application coverage gate **057** passed **1,643 tests and 373 subtests** with
**90.5% total coverage**, threshold 80 and process exit zero. No application,
canonical skill, dataset or frozen runtime changed in this publication.

The retained scores use **120 stratified development questions**, **112
retrieval-eligible questions**, **6,000 complete documents**, and eligible
population weight **470**. They are internal retrieval metrics. Generated-answer
Overall, all-500 results, public leaderboard rank and final promotion remain
unassigned. Per-strategy reports contain their cost, time and quality records.

[Aggregate and source commitments](aggregate.json) ·
[Reporting decision](../../../../../.specs/adr/0158-distinguish-catalog-stops-from-hypothesis-coverage.md) ·
[E14 reports](../README.md)

