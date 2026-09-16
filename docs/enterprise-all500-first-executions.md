# EnterpriseRAG: first executions of two previously unadmitted strategies

This prospective ordinary evaluation measures Graphify and Turso using the
unchanged all-500 task conditions that were never admitted by the interrupted
eight-strategy job. [ADR 0167](../.specs/adr/0167-measure-the-two-unadmitted-enterprise-strategies.md)
records the decision. The original [partial diagnostic report](../evaluations/reports/datasets/enterprise-all500-descriptive-001/README.md)
and its stopped study remain unchanged.

## Scope and fixed budget

| Field | Declared value |
| --- | --- |
| Study identity | `enterprise-all500-first-executions-001` |
| Owner | `harbor-run-results` |
| Stages | Ordinary `evaluation`, then dependent `publication` |
| Task order | Graphify, then Turso |
| Question cohort | The same 500 public questions; 470 retrieval-eligible |
| Source corpus | The same 6,000 complete documents |
| Primary routes | Graphify `search`; Turso `lexical-sql` |
| Primary metric | Native nDCG@10, displayed multiplied by 100 |
| Eligibility | No native exception, `evidence_integrity >= 1`, finite native reward |
| Skill | The exact complete reference bundle committed by the original study |
| Agent | `enterprise-stratified-final` 3.1.0; deterministic local retrieval |
| New allocation | Two original trials in one new job; one attempt per task |
| Retry budget | Zero automatic and zero manual retries |
| Concurrency | Two trials |
| Agent timeout | 10,800 seconds |
| Task resources | Two CPUs and 6 GiB per task |
| Planned workload | Two knowledge constructions and 500 primary-route queries per strategy |
| Mutation, selection, validation release, promotion | None |

The previous eight allocated originals stay charged. The two allocations here
are additional work under the user's continuation instruction. No result from
Legacy, Embeddings, Adaptive or Classical is executed again. Entity Graph and
Ensemble are excluded from this new job because they previously reached agent
execution; missing results alone do not make them eligible external retries.

## Input and execution boundaries

Copy only the exact Graphify and Turso task roots from the original public
dataset. The new manifest binds their original and copied tree digests,
the original execution manifest and native artifact inventory, the full skill,
model-cache bytes, agent sources and native Harbor runtime. The copied task
names preserve their ancestry; a new output directory does not create a new
independent semantic sample.

Derive the native configuration from the original all-500 configuration by
selecting precisely those two tasks in the declared order, then changing only
the output job identity, jobs directory and task-copy locations. Preserve all
other normalized JobConfig and TrialConfig fields, including native retries,
agent timeout, separate verifier environment, images, mounts and skill loading.

Use the unchanged executor policy with read-only input/skill mounts, no
networking, restricted privileges, fresh workspaces and isolated verifier
feedback. Do not expose optimizer history, prior outputs, public result tables,
private sources, answer artifacts or undeclared caches to the task executor.
The model cache is the exact previously declared read-only local cache.

Before execution, register one public dataset, both dependent stages and the
baseline; independently substantiate all six design checks and seal the design.
An admission receipt binds the current manifest and study ledger. The Windows
launcher holds the repository's exclusive native-execution lease and creates
a single-use two-trial allocation receipt. A pre-existing allocation or native
output identity prevents launch.

The native environment-start guard verifies all source commitments and required
host storage before each admission. Its sticky global stop denies later starts
after source drift or access-contract failure without canceling an admitted
sibling. Ordinary exceptions and timeouts consume their original opportunity;
none authorizes another native call. Preserve all outputs after an interruption.

## Reporting and completion

Use the native Harbor reporter with `evidence_integrity >= 1`. Require both
originals to settle before declaring this two-trial job complete. An execution
exception remains an error with unavailable quality. Missing timing, tokens
or provider cost remains unavailable. Do not infer a zero score or total cost
for an incomplete trial.

Publish independently reviewed aggregates by strategy, application/category,
dataset scope and cost/time/quality. Retain the original eligible-question
membership and overlapping application groups. A combined catalog may
transcribe the four existing qualified observations and the two new outcomes,
with explicit study provenance. It must retain all eight strategy rows and
state the number actually qualified. Native jobs remain separate.

The two studies share the query/corpus/skill contract, but timing was observed
with different concurrency partners and at different times. Treat quality as
descriptive and resource measurements as execution-specific. No paired
improvement, independent generalization or statistical superiority is claimed.
The public benchmark uses a larger corpus and a different answer-quality
contract; these retrieval values establish no official leaderboard position.

Record immutable native artifacts and reviewed reporting evidence before
closing each stage. If this job is incomplete, stop both stages and publish only
a separately reviewed partial diagnostic notice. Never rewrite the old study
or fabricate an eight-trial effective job. E16 and the two interrupted strategy
conditions retain their existing terminal outcomes and unmet acceptance gates.

Keep task datasets, generated knowledge, models, native records and query-level
outputs ignored. Publish only the reviewed portable aggregate package under
`evaluations/reports/datasets/enterprise-all500-first-executions-001/` and update
the existing report catalogs after exact-byte review.

[Back to the documentation index](README.md).
