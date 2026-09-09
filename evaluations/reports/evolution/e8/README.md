# EnterpriseRAG continuation E8

Status at 2026-09-09 05:11 UTC: independently reviewed, design-sealed and active.
The native owner has revalidated all 66 completed historical jobs: 17 Legacy,
seven Embeddings, 23 Classical and 19 Adaptive. All imports retained the original
best candidates and executed zero new trials. The new Turso and Graphify
baselines are now running in their native containers; Entity Graph and Ensemble
follow in the same two-worker baseline pass. No new completed E8 score is
published in this checkpoint.
The private gate remains unopened.

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

The continuation preserves cumulative attempts and rounds, excludes both
interrupted profiles from new dispatch, and requires all-eight joint replay,
one frozen all-500 comparison and the one-way whole-bundle private gate.
The all-500 execution profile prospectively permits 10,800 seconds for both
arms; it supplies no final measurement yet. Raw data and native artifacts remain
ignored under `tmp/e8/`.

The independent review verified 32 unchanged task roots, all 66 historical
job/skill inventories, 17 custody-guard checks and five actual image/resource
isolation probes. The maintained organizer accepted the complete review and
sealed execution contract SHA-256
`033aa7e01db8ed05bf306171573c116c46fdc2fa314b840ddbe1eea07809fb67`.
The review directory digest is
`4660244022088d6d157a67562778bd326cbf9437a96fe1920eba0bb45f1e2300`.
These checks establish the declared execution boundary; they are not retrieval
scores or measured all-500 completion.

The [family progress publisher](../../../../evaluations/publish_enterprise_family_progress.py)
requires an exact native comparison and replays cumulative decisions before
publishing a completed candidate prefix. It distinguishes gain over baseline
from gain over the actual previous incumbent and includes application/category,
route and CTA views. The latest implementation gate passed 1,568 tests with
90.7% application coverage. This verification does not supply retrieval scores.

[Operating guide](../../../../docs/enterprise-continuation.md) ·
[Decision](../../../../.specs/adr/0130-continue-interrupted-enterprise-search-prospectively.md) ·
[Original study](../e7/README.md)
