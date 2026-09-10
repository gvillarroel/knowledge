# EnterpriseRAG construction candidates: native terminal results

Both prepared construction candidates were measured once on the original
6,000-document workload, and **neither qualified**. Ensemble failed during
standalone validation with a confirmed container out-of-memory event. Entity
Graph reached the 3,600-second agent limit. Neither submitted a ranking, so
this checkpoint adds **no retrieval score or measured quality gain**. The
[aggregate](aggregate.json) binds the native results, original reports,
qualification failures, preserved diagnosis and terminal closure.

## Results by strategy

The retained comparison remains the
[qualified E11 starting comparison](../starting-terminal-001/README.md):
frozen-category-weighted retrieval nDCG@10 multiplied by 100, on 120
stratified EnterpriseRAG questions, 112 with references, and 6,000 complete
source documents. These are internal retrieval measurements. They do not
measure Luna answer quality, official answer/judge Overall, or public rank.

| Strategy | Initial score | Best verified score | Current disposition |
| --- | ---: | ---: | --- |
| Legacy | 61.11 | **72.38** | Completed search; retain its profile |
| Turso | 45.43 | **72.08** | Pending first measurement and remaining consultation search |
| Adaptive | 60.04 | **66.21** | Pending first measurement and remaining consultation search |
| Embeddings | 63.51 | **63.51** | Completed search; retain baseline |
| Classical | 55.04 | **62.10** | Completed search; retain its profile |
| Graphify | 8.12 | 8.12 baseline | Consultation search remains pending |
| Entity Graph | Unavailable | Unavailable | Matching correction also timed out; construction qualification remains open |
| Ensemble | Unavailable | Unavailable | Memory-lifetime correction also failed; construction qualification remains open |

Legacy has the highest confirmed subset score. Turso has the largest measured
gain over its own starting score, **26.65 points**. No new head-to-head result
across eight successfully constructed families is claimed.

## What the new executions established

The [Ensemble candidate](../ensemble-candidate-validation-001/README.md)
retained its passing public-fixture correctness and exact artifact/query
parity. On the full workload, its first build command returned zero, then
`validate_semantic_okf_ensemble.py` failed while validating that first bundle.
The agent ran for **2,136.072 seconds**. A preserved Docker event records an
OOM in the exact agent container at **2026-09-10 05:32:04.055531 UTC**, under
the unchanged **6 GiB** limit. The internal validation log, killed PID, child
exit code and allocation site were not retained. The evidence locates the
outer failing phase; it does not identify the precise allocation that failed.

Source inspection suggests one bounded next hypothesis: collect unreachable
semantic-validation state after the complete validator frame returns and
before the component derives additional structures. This remains unproven.
It cannot reduce a peak inside core validation, and it requires focused
retained-object evidence plus unchanged reports and rejection behavior before
claiming benefit. No new candidate or proposal charge is created by this report.

The [Entity Graph candidate](../entity-prefix-candidate-validation-001/README.md)
retained its exact mention-matching and integration evidence. Its native trial
ended with `AgentTimeoutError`: the configured limit was **3,600 seconds**,
and the recorded agent interval was **3,600.101 seconds**. It submitted no
response and has no verifier rewards. The successful small-fixture optimization
therefore does not establish full-workload feasibility or a native speedup.

Both original workers returned normally from Harbor orchestration, and both
native reporters completed. Each job nevertheless contains one execution error.
The two original qualifications rejected missing required native checkpoints.
A worker exit code of zero does not turn an errored Harbor trial into a
successful evaluation. The native report's 0.8 display threshold is diagnostic;
missing quality is not converted into a measured zero.

## Opportunity coverage and remaining work

The two construction first measurements are now **consumed**. This supersedes
the unconsumed status in the earlier
[control-portability checkpoint](../construction-owner-portability-001/README.md).
Claims remain **83 of the existing 585-proposal ceiling**: 81 historical
proposals and the two already charged construction corrections. No automatic
retry, replacement attempt or additional proposal was launched.

| Strategy | Proposals claimed / ceiling | Search state |
| --- | ---: | --- |
| Legacy | 16 / 55 | Closed under the existing stopping rule |
| Embeddings | 6 / 40 | Closed under the existing stopping rule |
| Classical | 37 / 85 | Closed; preserve the unavailable original and retained result |
| Adaptive | 20 / 100 | Open; one historical first measurement remains pending |
| Turso | 2 / 55 | Open; one historical first measurement remains pending |
| Entity Graph | 1 / 80 | Open; construction proposal measured with an execution error |
| Ensemble | 1 / 105 | Open; construction proposal measured with an execution error |
| Graphify | 0 / 65 | Open; baseline qualified, consultation proposals pending |

An execution error supplies no evaluable quality miss. The rule of three
consecutive distinct evaluable misses per mechanism and the five-round limit
remain unchanged; unused capacity from closed catalogs is not transferred.
The maintained organizer recorded the immutable terminal evidence and stopped
this ordinary evaluation at ledger sequence 7. Private validation and holdout
were not released, and no skill was installed.

The failed construction path does not authorize composition or dependent
search. Further construction proposals need their own prospective declaration
and charge. The remaining family searches, joint replay, exact bundle freeze,
paired all-500 comparison and reserved independent whole-bundle acceptance
remain incomplete. The overall request is still open.

## Applications, categories and datasets

These two trials provide no query results to aggregate by Jira, Gmail,
Confluence or other applications. Existing measured application/category
breakdowns remain available in the
[family report index](../../../../../docs/enterprise-family-report-index.md)
and the [retained cross-family comparison](../../e8/retained-cross-family-002/README.md).
This checkpoint concerns EnterpriseRAG only; it adds no measurement on another
dataset. The [report hub](../../../README.md) retains the dataset views.

[Cost, time and quality](cta.md) · [E11 overview](../README.md) ·
[Evolution evidence index](../../README.md)
