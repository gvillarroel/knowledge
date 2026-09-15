# EnterpriseRAG: one fixed public descriptive evaluation

This protocol governs `enterprise-all500-descriptive-001`, an ordinary public
evaluation of the complete reference bundle frozen before the E16 execution
failures. It answers a descriptive question about retrieval quality and runtime
on all 500 EnterpriseRAG questions. It does not resume E16 or replace its
unfinished evolution, paired recalculation and independent-acceptance gates.
The decision is recorded in [ADR 0166](../.specs/adr/0166-measure-the-frozen-enterprise-bundle-as-a-separate-public-observation.md).

## Fixed inputs and budget

| Field | Declared value |
| --- | --- |
| Study owner | `harbor-run-results` |
| Stages | Ordinary `evaluation`, then dependent `publication` |
| Strategies | Legacy, Embeddings, Classical, Adaptive, Entity Graph, Ensemble, Graphify, Turso |
| Bundle | The complete precommitted E16 reference; no new candidate selection |
| Public cohort | 500 questions; 470 retrieval-eligible questions |
| Source corpus | 6,000 complete documents |
| Primary quality observation | Native nDCG@10, displayed multiplied by 100 |
| Quality eligibility | No native exception, `evidence_integrity` at least 1, finite native reward |
| Trials | Eight originals; exactly one attempt per task |
| Concurrency | Two trials |
| Retries | Zero |
| Agent timeout | 10,800 seconds, already declared in the original all-500 template |
| Task resources | Two CPUs and 6 GiB; unchanged original task configuration |
| Model treatment | Fixed deterministic local retrieval agent; no remote generative-model requests |
| Mutation, selection, private release, promotion | None |

The original all-500 job template has SHA-256
`676721f18864833808cd00f4699f912a2b238188749de32141c6df4c2af4a5b3`.
Its new copy changes only `job_name`, `jobs_dir` and task source locations
to byte-identical copies in the new single public dataset. Preserve task order,
timeouts, attempts, concurrency, retry settings, agent version, complete skill
provisioning, images, mounts, scorer and task bytes. The native configuration
receipt, execution manifest and independent admission receipt bind the exact
paths and digests under ignored `tmp/enterprise-all500-descriptive-001/`.

## Admission and execution

Register the eight byte-identical all-500 task copies together as one public
`development` dataset in the organizer. Here `development` is its public access role; the study has no
evolution stage or optimizer. The eight strategy conditions share one question
cohort and are not eight independent semantic samples. Register the two ordered
stages, provide the complete frozen protocol and baseline binding, and pass all
six substantive independent review checks before sealing the design.

The independent admission receipt must bind the execution manifest and sealed
study ledger, confirm the ordinary evaluation is running, and confirm zero
private releases. The Windows launcher holds the repository's exclusive
native-execution lease, creates a one-use allocation ticket and refuses an
existing ticket or output job. Linux runs the native Harbor job using the same
source-pinned executor policy before loading the job and agent classes.

The preparation check validates the exact native configuration and all task
configurations without creating a Harbor job. The task containers keep the
verified read-only root, disabled networking, restricted privileges, isolated
feedback paths and fresh workspace volumes. No optimizer notes, prior traces,
private data or undeclared state are added to their mounts or prompts.

The declaration permits one complete job only. Every admitted trial settles
under the native job even when a sibling fails. A sticky global stop prevents
later environments from starting after source drift, inaccessible inputs, a
proven failure of the frozen agent's access contract, or an exhausted required
host filesystem. Use Harbor's environment-start hook inside its native error
boundary; the end hook may latch failure but never throw and cancel siblings.
Preserve refused originals as native `AdmissionStopped` errors, distinguish them
from executed environments, and keep all eight rows in the report. Ordinary
agent timeouts, runtime failures and verifier outcomes do not authorize a retry
or a replacement. E16's original 120-question jobs, journal and study remain
untouched.

## Reporting and interpretation

Validate the completed native job with `harbor-run-results`. Use the declared
evidence-integrity gate to distinguish qualified observations from exceptions
and malformed output. Source every quality value from a qualified native trial;
preserve missing token, cost and timing fields as unavailable. Report original
attempt coverage, errors, execution time and eligibility before interpreting
the descriptive ranking. The highest measured score is a table statistic, not
a selected candidate or permission to promote a skill.

Publish only independently reviewed aggregates: the eight-strategy table,
application/category groups, dataset view, per-skill views and CTA. Groups must
retain native eligible-question membership; application groups may overlap.
Keep all eight strategy entries, including unavailable scores. Do not remove a
failed strategy from the declared denominator or replace its reward with zero.

The 500-question cohort overlaps the development sample and uses a smaller
corpus than the official benchmark. A result cannot establish causal skill
improvement, independent generalization or an official leaderboard position.
The historical Classical full-corpus retrieval and Luna answer-quality runs
remain separately labeled treatments. No new private validation or skill
promotion is part of this protocol, and E16's outstanding gates remain
unfulfilled regardless of this descriptive study's results.

Data, generated knowledge, native records and per-question outputs remain
ignored. Publish approved reports in `evaluations/reports/` and update the
dataset, skill and CTA catalog links. Never publish the source corpus or raw
evaluation traces as documentation.

[Back to the documentation index](README.md).
