# Entity consultant: pinned-runtime compatibility

The separately declared consultant-only fixture passed in the pinned Python
3.12.13 container. Parent and candidate deeply validated the same processed
128-record public snapshot and returned identical inspections and all eight
nonempty query payloads across lexical, entity, traversal and fusion routes.
**This adds compatibility evidence, not an EnterpriseRAG retrieval score.**

## What the fixture establishes

The complete builder and the other 251 package files remain frozen. Only the
consultant's `derive_mentions` function differs, as documented in the
[candidate report](../entity-consultant-token-automaton-001/README.md) and
[decision record](../../../../../.specs/adr/0142-optimize-entity-consultant-matching-with-frozen-builder.md).
The fixture imports the consultant model before its snapshot module and retains
`deep_validation=True`, matching the actual workload's setup order.

One container ran two separate Python processes, parent first and candidate
second, against one unchanged 145-file processed snapshot. Consultant packages
and snapshot were mounted read-only and staged onto the container's writable
filesystem. Complete post-run byte comparisons passed for both packages and the
snapshot. No builder or raw source was mounted and no build was repeated.

The container and its original runner both exited successfully, without an OOM
event. The fixture used two CPUs, 6 GiB memory and no network, with the same pinned
image as the retained runtime evidence. The full
[aggregate](aggregate.json) binds the declaration, helpers and actual output files.

## Limits and next measurement

The two roles are a single fixed-order pair with no randomization. Their
[descriptive timings](cta.md) do not establish a causal speedup, memory reduction,
complete 6,000-document feasibility or retrieval improvement. The previously
consumed builder fixtures and four native construction attempts remain intact.
The earlier timeout's exact internal phase remains unresolved.

The new consultant candidate's EnterpriseRAG first measurement remains unassigned
at this checkpoint. The ordinary qualification must update its consultant digest
in both the task's skill-file inventory and imported-module inventory while
retaining repeated builds, independent validators, deep consultation and the
existing resources. No canonical skill has been promoted.

## Retained eight-family comparison

These are existing internal development results on 120 questions, 112
retrieval-eligible questions and 6,000 complete documents. The metric is frozen
category-weighted nDCG@10 multiplied by 100. This fixture changes none of them.
They are not generated-answer quality, official Overall, a public ranking or the
final all-500 evaluation.

| Family | Retained development nDCG@10 × 100 |
| --- | ---: |
| legacy | 72.38 |
| turso | 72.08 |
| adaptive | 66.21 |
| embeddings | 63.51 |
| classical | 62.10 |
| graphify | 8.12 |
| ensemble | Unavailable |
| entity-graph | Unavailable |

Cumulative proposals remain 86 of 585, with five family searches open. The
three-consecutive-unique-evaluable-miss and five-round rules remain unchanged.
Both historical pending first measurements retain their existing charges. The
remaining full-workload qualification, composed reference, twelve fresh starting
roles, open catalogs, joint replay, exact freeze, paired all-500 comparison and
reserved one-way independent acceptance are still required.

[Cost/time/scope](cta.md) · [Application/category availability](../entity-token-automaton-native-001/groups.md) · [Family evidence](../../../../../docs/enterprise-family-report-index.md) · [E11](../README.md)
