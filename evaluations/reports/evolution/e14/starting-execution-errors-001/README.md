# EnterpriseRAG E14: Entity Graph and Ensemble starting execution errors

Date: 2026-09-11. **Six families have qualified starting results; Entity Graph and Ensemble completed their original starting attempts with execution errors.** Ensemble encountered a Docker out-of-memory event during construction. Entity Graph timed out after its build and validation summaries had passed. Neither produced a qualified retrieval result.

The workload is unchanged: 120 stratified questions, 112 retrieval-eligible questions, eligible population weight 470 and 6,000 complete documents. Both original attempts are consumed. No retry, resource change, mutation proposal or mutation quality miss is introduced by this report.

## Native outcomes

| Family | Original attempt | Native exception | Qualified retrieval nDCG@10 | Controller outcome |
| --- | --- | --- | --- | --- |
| Ensemble | 1, zero retries | RuntimeError | Unavailable | Family-local stop |
| Entity Graph | 1, zero retries | AgentTimeoutError | Unavailable | Family-local stop |

The native owner accepted the execution-profile and skill-provenance checks, then rejected both starting qualifications. Both archives have no best candidate. The controller recorded `FamilyStopped: Starting measurement is not qualified`; this permits other ready families to continue. A family stopped before qualification has not exhausted its remaining evolution hypotheses.

## Ensemble

Docker recorded an `oom` event for the exact Ensemble trial container at **18:27:30.567879610 UTC**, under its fixed **6 GiB** memory limit. The agent then reported a failed `build_semantic_okf_ensemble.py` command and exited with a runtime error. No response artifact or verifier result was produced. The job finished at 18:27:47.495126 UTC.

The OOM event is direct runtime evidence. The exact killed process and the internal failing builder location are unavailable: the inner `knowledge-build.log` was not exported, and the native environment was subsequently deleted. This report preserves that limit instead of assigning an unobserved exit signal or required memory size.

## Entity Graph

The original exclusive evidence-index first measurement reached **AgentTimeoutError after 3,600 seconds**. Before teardown, four existing logs were copied read-only from the original container: the first build, its validation, the second build and its validation. All four report `pass`, `valid: true` and no errors. The two build summaries are byte-identical, as are the two validation summaries. These auxiliary logs are not native verifier output and do not prove whole-bundle byte equality or retrieval completion.

The build summaries describe **6,000 records, 6,343 sections, 7,200 entities, 1,604,806 edges and 1,594,205 mentions**. They show that construction reached its reported success boundary. They do not identify which later validation, loading or query operation consumed the remaining time.

After the timeout, the native verifier reported a missing `ranking.json` and assigned zero reward and zero evidence integrity. There is no complete retrieval output from which to calculate nDCG, recall, MRR or application/category scores. The exclusive first-measurement identity remains consumed; this report neither remaps it nor substitutes an ordinary baseline.

## Reward accounting and quality

The native analyzer marks both error trials `evaluable: true` for its accounting and carries a mean reward of 0.0. Ensemble has no observed verifier reward; Entity Graph has an observed verifier reward of 0.0 for the missing output. Both fail qualification. **Those accounting zeros are not measured retrieval nDCG scores and are not mutation quality misses.** The unrounded native summaries and qualification records are preserved in [aggregate.json](aggregate.json).

## Cost, time and quality

| Family | Job seconds | Agent seconds | Attempts | Execution errors | Retrieval quality |
| --- | --- | --- | --- | --- | --- |
| Ensemble | 1,501.739 | 1,472.485 | 1 | 1 | Unavailable |
| Entity Graph | 3,648.920 | 3,600.102 | 1 | 1 | Unavailable |

Each row describes its one consumed original native job. Token and provider-cost fields are unavailable in these failed jobs; complete host and orchestration costs are unpriced. The timeout budget is not extended, and no answer-generation or judging score is assigned.

## Retained eight-family comparison

The six qualified starting scores remain unchanged. The two failed families retain unavailable quality values. This is still the stratified development workload, not the final all-500 comparison or a public leaderboard result.

| Family | Retained nDCG@10 x100 | Inherited proposals / cap | Current E14 start |
| --- | --- | --- | --- |
| Legacy | 72.38 | 16 / 55 | Qualified |
| Turso | 72.08 | 2 / 55 | Qualified |
| Adaptive | 66.21 | 20 / 100 | Qualified |
| Embeddings | 63.51 | 6 / 40 | Qualified |
| Classical | 62.10 | 37 / 85 | Qualified |
| Graphify | 8.12 | 0 / 65 | Qualified |
| Ensemble | Unavailable | 2 / 105 | Execution error; not qualified |
| Entity Graph | Unavailable | 8 / 80 | Execution error; not qualified |

## Repository verification

Full application gates 050 and 051 failed on intermittent Windows directory
publication errors. Both original logs remain source-bound. Two isolated tests
passed between those runs; the repeated full-suite materializer failure still
required a correction. The Confluence test passed in run 051.

The unfrozen generator adapter now allows bounded retries of its final rename
for specific Windows access conflicts and preserves an existing destination.
The [publication decision](../../../../../.specs/adr/0154-bound-windows-task-tree-publication-retries.md)
records the scope and limits. Twelve targeted tests passed after the correction.
Fresh full gate **052 passed 1,643 tests and 373 subtests, with 90.5% total
application coverage**, above the required 80%. No native trial, consumed
identity or skill treatment was rerun or changed by this software correction.

## Remaining work

Turso, Adaptive and Graphify retain open searches in this controller. Legacy, Embeddings and Classical preserve their earlier catalog stops. The remaining Entity Graph and Ensemble hypotheses are still outstanding after these starting failures. Their errors do not transfer capacity to other families or reset consumed identities.

The all-eight qualification and completion gate is unmet. The full objective still requires all family opportunities, the paired joint replay, one frozen whole bundle, the all-500 comparison and independent acceptance. This report authorizes no partial selection, private release or promotion. Any later work must preserve the original failures, budgets, treatment separation and one-way validation boundaries.

[Qualified six-family application/category and CTA comparison](../qualified-starts-comparison-001/README.md) · [Last qualified Classical family report](../classical-starting-qualified-001/README.md) · [E14 overview](../README.md) · [Dataset view](../../../datasets/enterprise-rag-stratified-development-120.md) · [Aggregate and source commitments](aggregate.json)
