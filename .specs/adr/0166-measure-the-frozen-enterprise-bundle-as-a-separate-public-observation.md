# ADR 0166: Measure the frozen EnterpriseRAG bundle as a separate public observation

Date: 2026-09-14.

Status: Accepted for prospective preparation. Execution requires the new ordinary-evaluation study's independent review and seal.

## Context

E16 completed its two original first measurements with `AgentTimeoutError` at
3,600 seconds. Neither result qualified. The isolated planner emitted no
selection, both original jobs settled, the optimizer was removed, and all four
E16 stages stopped without private validation release. The original evidence
and all E16 bindings remain immutable.

[ADR 0164](0164-close-e15-after-independent-preparation-rejection.md) prohibits
substituting a partial or report-only run for the prerequisites of the paired
all-500 evolution comparison. [ADR 0165](0165-isolate-the-frozen-enterprise-evolution-planner.md)
also requires a terminal stop after an unqualified original. Those decisions
remain in force. The requested evolution, paired recalculation and independent
acceptance were not completed in E16.

The user also requested a table showing how the strategies perform across the
EnterpriseRAG questions. A narrower, ordinary public evaluation can answer a
descriptive question: what retrieval quality and execution outcomes does the
already fixed complete reference bundle produce under its previously declared
all-500 condition? The maintained organizer distinguishes ordinary evaluation
from evolution; the mandatory independent-validation gate applies before
evolution, while an ordinary public evaluation does not select or promote.

## Decision

Register `enterprise-all500-descriptive-001` as a new schema-2 study with one
ordinary `evaluation` stage and a dependent `publication` stage, both owned by
`harbor-run-results`. Register all eight exact all-500 native task roots before
execution. The public tasks and complete reference bundle retain their E16
preparation bytes. Copy the eight tasks byte-for-byte into one new public
dataset root; change only the job name, output directory and task source paths
to these identical copies in the original job template.

The frozen job template already declared a 10,800-second agent limit, one
attempt per task, two concurrent trials and zero retries before the E16
failures. Preserve those settings, task order, the 6 GiB / two-CPU task limits,
images, agent version, skill provisioning, scorer, source corpus and query
cohort. Preserve the exact executor policy that isolates the agent's verifier
feedback mount. An independent six-check review must substantiate these
bindings and the actual executor evidence before sealing and admission.

The study measures the complete precommitted reference bundle once, across
all eight strategies. It has no optimizer, new candidates, adaptive proposals,
selection, private release or promotion. Outcomes cannot be returned to E16,
used to requalify its original errors, or used for subsequent candidate changes
under this study. It does not execute E16's paired 16-trial comparison.

Use native Harbor for execution and result validation. Preserve each original
trial, including exceptions. Report a retrieval score only when the native
trial has no exception, passes the declared evidence-integrity gate and has a
finite reward. An error remains unavailable in every quality table; never
reinterpret the verifier's error marker as a zero-quality observation.

Publish reviewed descriptive rankings, source-bound application/category
aggregates, dataset scope, per-strategy evidence and CTA. Label the common
500-question / 6,000-document condition, the 470 retrieval-eligible questions,
the overlap with the 120-question development cohort and the different agent
limits. These are internal retrieval observations, not the official
511,962-document answer-quality leaderboard or independent generalization
evidence. Keep source data, generated knowledge and native traces ignored.

## Consequences

The new table can answer the narrower performance question without changing a
failed study or inventing an accepted evolved bundle. Completion of this
ordinary evaluation means its declared measurements and report finished; it
does not mean E16's outstanding evolution, paired comparison or private gates
passed. Any future evolution or promotion needs its own valid prospective
protocol and independent acceptance boundaries.

See the [public descriptive protocol](../../docs/enterprise-all500-descriptive-evaluation.md).
