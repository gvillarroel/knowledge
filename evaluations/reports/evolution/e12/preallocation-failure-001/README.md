# EnterpriseRAG: preserved controller failure and tested template correction

Date: 2026-09-11.

The latest development invocation produced **zero native jobs and zero new
scores**. A controller defect stopped it before per-job admission, allocation
persistence or native execution. Independent terminal review confirmed that
no first measurement, additional proposal or quality miss was consumed.
The four E12 stages are stopped and the organizer's final verification passed.

## Retained EnterpriseRAG comparison

These values are copied from the [previous reviewed comparison](../../e11/entity-evidence-index-reuse-001/README.md#retained-enterpriserag-comparison).
They are historical internal retrieval results on **120 stratified questions,
112 retrieval-eligible questions and 6,000 complete documents**. The metric is
frozen-category-weighted **nDCG@10 multiplied by 100**. They are not measurements
of the corrected controller or a new installed skill version.

| Family | Retained nDCG@10 x100 | Proposals / cap | Search status |
| --- | ---: | ---: | --- |
| Legacy | 72.38 | 16 / 55 | Recorded catalog stop |
| Turso | 72.08 | 2 / 55 | Open; original pending measurement preserved |
| Adaptive | 66.21 | 20 / 100 | Open; original pending measurement preserved |
| Embeddings | 63.51 | 6 / 40 | Recorded catalog stop |
| Classical | 62.10 | 37 / 85 | Recorded catalog stop |
| Graphify | 8.12 | 0 / 65 | Open |
| Entity Graph | Unavailable | 8 / 80 | Open; new first measurement unassigned |
| Ensemble | Unavailable | 2 / 105 | Open |

The Embeddings stop does not mean six evaluable quality losses. Unavailable
Entity Graph and Ensemble scores remain missing; they are not quality zeroes.
The full eight-family all-500 comparison, generated-answer Overall, public
leaderboard position and independent whole-bundle acceptance remain unfinished.

## Cause and correction

The pinned native owner's `normalize_config` preserves `developmentJob` and
`holdoutJob` as file paths. The sealed adapter attempted to call `model_dump`
on one of those paths. Adaptive raised `AttributeError`; Turso encountered the
shared stop, and the six other families were interrupted. The two written
generation-zero configurations were declarations, not evaluated jobs.

The isolated prospective correction loads the path through the owner's
`load_job_template` before serializing the returned `JobConfig` or passing it
to `job_signature`. It leaves the original normalized configuration unchanged
for the native runner. The original E12 source and failed invocation remain
preserved. [ADR 0151](../../../../../.specs/adr/0151-load-enterprise-native-job-templates-through-owner-api.md)
records the correction boundary.

All **nine software tests** passed with Harbor 0.18.0 in the native Linux
Python environment. They use the real normalization, loading and signature
functions with a synthetic runner and in-memory admission/persistence. They
reproduce the original error, exercise both public family configurations and
public joint profiles, check a wholly synthetic private-phase template, and
verify that repeated admission and resource limits are retained. No private
template or task was read by the tests, and no native workload ran.

Earlier synthetic source tests did not exercise this actual API type contract
and missed the defect. Their original passing results and the failed original
remain distinct from this new regression evidence. Passing software tests does
not establish native admission, retrieval improvement or full-workload feasibility.

## Opportunity accounting and remaining work

Cumulative proposal accounting stays **91 of 585**, with **373 maximum new
family-bound claims** across the five open searches. The **121 unused slots**
in closed searches remain nontransferable. Nine prior construction first
measurements remain consumed; the new Entity first measurement is unassigned.
Pending Turso `k1=0.6` and Adaptive `b=0.25` retain their exact original identities.
Classical023 and Adaptive019 remain unavailable.

The continuation still requires qualified starting roles for every participating
family, completion of all inherited search obligations, and the unchanged
three-consecutive-evaluable-misses rule and five-round ceiling. Final acceptance
still requires all eight families, the paired joint development replay, one
frozen complete bundle, the paired all-500 comparison and the unopened independent
gate. No canonical skill has been promoted from this checkpoint.

## Terminal evidence

The independent audit binds the original failure and its zero-allocation
state. The organizer then recorded that diagnostic, stopped evolution and
the three planned dependants, and verified the final ledger. It has **14
events**, head
`c941f53959a90120690a013b9df982bdda23268f8ea83164ff763c4ee7aea2e3`.
Validation was not released. [The aggregate](aggregate.json) records source
digests without publishing raw tasks, native logs or private review content.

[CTA](cta.md) · [Applications and datasets](groups.md)
· [E12 overview](../README.md)
