# Semantic OKF Evaluation Datasets

This directory is the canonical registry and execution scaffold for reusable Semantic OKF evaluations. It turns the existing Astro documentation and GraphRAG paper benchmarks into checked datasets that can run in either of two isolated modes.

## Inventory

| Dataset | Raw sources | Questions | Hard questions | Cohorts | Checked processed bundle |
|---|---:|---:|---:|---|---|
| `astro-40` | 416 Astro MDX files | 40 | 10 | `train=24`, `dev=8`, `holdout=8` | No; build one and pass `--bundle` |
| `graphrag-papers-40` | 15 papers, 15 reviewed claim files, and 1 vocabulary file | 40 | 10 | `discovery=24`, `holdout=6`, `hard=10` | `evaluations/graphrag-cross-paper/bundle` |

Every descriptor pins the source manifest, question set, optional semantic rubric, hard ground truth, cohorts, and family-specific plan files by SHA-256. The papers descriptor restores the original q001–q030 document minimums and hidden required points from the authored blueprint.

The `graphrag-papers-40` qrel paper lists are curated, non-exhaustive focus
sets. They are useful for focus coverage and retrieval diagnostics, but an
otherwise valid paper is not semantically irrelevant merely because it is
outside that list. For newly generated tasks, the public minimum-document gate
therefore counts independent documents with exact valid evidence, while focus
coverage remains a separate metric. Neither metric establishes answer
correctness: semantic ranking requires review against every hidden required
point or hard-ground-truth claim, derivation, and important negative.

A report may claim full-dataset coverage only when every q001–q040 question has
at least one complete response. Audit the local response archive and the
preserved historical manual review with:

```bash
python evaluations/semantic-okf-datasets/audit_response_coverage.py \
  --raw-adjudications evaluations/semantic-okf-datasets/reports/20260724-graphrag-papers-40-raw-semantic-adjudications.json
```

Dataset contract 1.2 pins a curated reference-answer collection for all forty
questions at
[`reports/20260724-graphrag-papers-40-best-answers.json`](reports/20260724-graphrag-papers-40-best-answers.json).
Each answer was reviewed independently against every authored semantic target
and validated against the exact evidence ledger. These answers are evaluator
reference material, not live model trials; their presence does not make an
incomplete empirical campaign eligible for a full-dataset claim.

An independent second-pass assignment for every question rechecked all 175
reviewable historical responses, 200 authored semantic targets, and 94 hard
evidence anchors. The audit retained 26 answers and replaced 14 whose wording,
claim-level citations, metric attribution, or inference boundaries could be
made more exact. The complete decision record is the
[`second-pass review`](reports/20260724-graphrag-papers-40-second-pass-review.md)
with a
[`machine-readable companion`](reports/20260724-graphrag-papers-40-second-pass-review.json).
All forty final answers pass the exact current response and mechanical
qualification contracts.

The current-metrics
[`evaluation table`](reports/20260724-graphrag-papers-40-current-metrics-table.md)
rescored all 516 available local Harbor trial artifacts without making a new
model call or changing an original result. The inventory combines 180 trials
from the primary result tree, 15 complete and distinct trace-distillation
trials, 320 original eight-family campaign trials, and one completed
provider-quota retry. It applies the current question policy while retaining
each trial's native ledger and source-combination crosswalk, which is necessary
because candidate families expose different exact record identities for the
same authoritative papers. The companion JSON preserves all current metrics,
artifact-root provenance, and redacted diagnostics for every trial. Historical
semantic adjudications are rejoined to 32 raw campaign trials by immutable
trial id; emitted responses without an adjudication remain explicitly
unreviewed. This is an artifact-only diagnostic: 503 rows belong to complete
parent jobs, while 13 rows belong to four incomplete parent jobs and are
reported separately rather than treated as final comparison evidence. One
trial from a different incomplete Rust-Mallet study is excluded.

Reproduce the table from a fresh, validated current task tree:

```bash
python evaluations/semantic-okf-datasets/generate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family legacy --mode consult-only \
  --output evaluations/runs/graphrag-second-pass-current-metrics-20260724/tasks
python evaluations/semantic-okf-datasets/validate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family legacy --mode consult-only \
  --tasks evaluations/runs/graphrag-second-pass-current-metrics-20260724/tasks
python evaluations/semantic-okf-datasets/recalculate_graphrag_evaluation_table.py
```

The registry covers these eight paired strategies:

| Family | Build skill | Consult skill | Plan | HF cache |
|---|---|---|---|---|
| `legacy` | `build-semantic-okf` | `consult-semantic-okf` | No | No |
| `embeddings` | `build-semantic-okf-embeddings` | `consult-semantic-okf-embeddings` | Yes | Yes |
| `classical` | `build-semantic-okf-classical` | `consult-semantic-okf-classical` | Yes | No |
| `adaptive` | `build-semantic-okf-adaptive` | `consult-semantic-okf-adaptive` | Yes | No |
| `entity-graph` | `build-semantic-okf-entity-graph` | `consult-semantic-okf-entity-graph` | Yes | No |
| `ensemble` | `build-semantic-okf-ensemble` | `consult-semantic-okf-ensemble` | Yes | Yes |
| `graphify` | `build-semantic-okf-graphify` | `consult-semantic-okf-graphify` | No | No |
| `turso` | `build-semantic-okf-turso` | `consult-semantic-okf-turso` | No | No |

### Candidate admission queue

Candidate intake is tracked separately from `families.json`. An intake row makes
the available evidence and missing measurements visible, but it does not change
the eight-family campaign cardinality, make a direct-retrieval result a grounded
Harbor result, or rewrite a historical comparison.

| Candidate | Build skill | Consult skill | Mechanical evidence | Canonical metrics | Registry state |
|---|---|---|---|---|---|
| `tantivy` | `build-semantic-okf-tantivy` | `consult-semantic-okf-tantivy` | Pass: dedicated build preserved all 884 authoritative core files byte for byte and regenerated the six bound projection files with deterministic LF serialization; two post-distillation 890-file rebuilds were byte-identical to the frozen bundle; 40-question Top-10 run, exact replay, pool-100 prefix parity, zero query errors, and 100% exact evidence validity | Direct Top-10 measured: 80.74% all-40 Recall@10, 92.17% hard-10 Recall@10, 93.75% MRR@10, 81.05% nDCG@10, and 90.92 ms P95; grounded Harbor admission remains separate | Query winner remains promoted; later IDF query and forward-four builder candidates were rejected by non-regressing holdout gates; experimental pair not registered |
| `tika-mallet` | `build-semantic-okf-tika-mallet` | `consult-semantic-okf-tika-mallet`; bounded Harbor candidate frozen separately | Pass: two clean 15-paper builds, extraction-fidelity replicate, 40-question Top-10 replicate, pool-100 parity, and 100% exact evidence validity | Direct fusion measured: 74.82% Recall@10, 71.83% hard Recall@10, 87.50% MRR@10, 75.44% nDCG@10, and 86.36 ms P95; grounded Harbor admission remains separate | Rankable experimental direct-retrieval comparator; not registered or promoted |

The machine-readable
[`tika-mallet` intake](../semantic-okf-tika-mallet/canonical-evaluation-intake.json)
records the admitted direct-retrieval metrics and preserves grounded Harbor rewards
as null. The v3 treatment has a terminal context-limit cell; the bounded v4
preflight was rejected for provider quota before agent execution. Remaining
non-compensating promotion gates include broader format coverage, one clean frozen
40-question grounded Harbor treatment, Linux or WSL build and retrieval
reproducibility, and promotion review. Only after those gates pass may a separate
decision modify `families.json`, dataset descriptors, or strict campaign
cardinality.

## Execution modes

| Contract | `build-consult` | `consult-only` |
|---|---|---|
| Installed skills | One matched build/consult pair | The matched consult skill only |
| Public read-only mount | Raw staged input at `/dataset` | Processed Semantic OKF at `/knowledge` |
| Knowledge used for the answer | Built during the trial at `/workspace/knowledge` | Prebuilt mounted snapshot |
| Prebuilt knowledge visible to agent | No | Yes |
| Raw sources visible to agent | Yes | No |
| Questions, qrels, and ground truth in public mount | Never | Never |

The hidden verifier always contains its own pinned reference ledger, qrels, semantic rubric, and hard evidence. Required semantic points remain hidden, while a declared minimum relevant-document count is stated in the public prompt. In `consult-only`, the runner requires the agent bundle to match that reference exactly. In `build-consult`, the reference is not mounted into the agent; the newly built snapshot must emit compatible authoritative record identities and hashes to score successfully.

Generated inputs, tasks, bundles, dry runs, and live results are ignored. Run receipts are append-only and record dataset, mode, family, skills, model, Pi version, task IDs, and resource hashes.

Multi-family consultation campaigns are audited with:

```bash
python evaluations/semantic-okf-datasets/summarize_consult_campaign.py \
  evaluations/semantic-okf-datasets/generated/campaigns/<campaign> \
  --json-output evaluations/semantic-okf-datasets/reports/<campaign>.json \
  --markdown-output evaluations/semantic-okf-datasets/reports/<campaign>.md
```

Strict mode requires all eight families, every declared cohort, one result per question, valid run identities, Pi `0.73.1`, `openai-codex/gpt-5.3-codex-spark`, no provider/evaluator failures, and 40 evaluable final responses per family. For scheduled campaigns it additionally verifies the immutable input binding, exact one-task shard paths, receipts, terminal outcomes, and completed checkpoint; an answer is scorer-observable only when the current verifier emitted its complete finite metric vector and a recognized scored status. `--allow-partial` is only for incomplete progress inspection. `--allow-invalid` emits an explicitly forensic report for a structurally complete but non-rankable campaign. Add `--rescore` to apply the current grader to immutable historical traces; this never changes raw results.

## Recorded campaigns

Durable progress checkpoints for the first GraphRAG papers consultation campaign are recorded in [`reports/20260717-papers-consult-gpt53-spark-01-test-log.md`](reports/20260717-papers-consult-gpt53-spark-01-test-log.md), with exact machine-readable values in [`reports/20260717-papers-consult-gpt53-spark-01-checkpoints.json`](reports/20260717-papers-consult-gpt53-spark-01-checkpoints.json). Append new checkpoints at cohort or audit boundaries; do not rewrite prior observations after later results are known.

That campaign is **not a valid comparison**. Although all 320 result artifacts exist, 254 ended at provider quota and only 32 emitted complete final responses. The current sources are the corrected [`audit Markdown`](reports/20260717-papers-consult-gpt53-spark-01-audit-v2.md), lossless [`audit JSON`](reports/20260717-papers-consult-gpt53-spark-01-audit-v2.json), and complete [`manual answer review`](reports/20260717-papers-consult-gpt53-spark-01-manual-review.md). The historical `-final` reports remain only as superseded evidence of the original aggregator defect; they do not establish a winner.

The first corrected live retry, campaign 02, is also not a comparison. Its
counted `adaptive/q001` preflight ended at provider quota on July 17, 2026, and
the fair scheduler aborted before submitting the remaining 319 cells. See the
[`campaign 02 test log`](reports/20260717-papers-consult-gpt53-spark-02-test-log.md)
and its [machine-readable checkpoint](reports/20260717-papers-consult-gpt53-spark-02-checkpoint.json).
The current grader's lossless rescore is preserved as a
[`forensic Markdown report`](reports/20260717-papers-consult-gpt53-spark-02-forensic.md)
and [`forensic JSON report`](reports/20260717-papers-consult-gpt53-spark-02-forensic.json);
strict summarization rejects the incomplete campaign rather than emitting a
ranking.
The provider reported a reset at `2026-07-23T14:24:32+00:00`.

Campaign 03 was abandoned before any model call when its WSL dry run exposed a
platform-dependent tree-digest ordering bug. Its original Windows binding is
preserved append-only. The canonical digest correction was verified in a fresh
campaign 04: Windows and WSL reproduced the same version 1 binding, all 320
exact-bundle task validations passed, and the live runtime image binding passed.
Campaign 04 contains zero runs, outcomes, and checkpoints. A later
execution-closure audit found that version 1 did not bind the model bytes,
campaign-local pipeline and Harbor distribution, complete job contract, or
post-call drift boundary. Campaign 04 is therefore superseded before execution
and must not be used for a live run. Its
[`preflight log`](reports/20260723-papers-consult-gpt53-spark-04-preflight-log.md)
and [machine-readable readiness record](reports/20260723-papers-consult-gpt53-spark-04-readiness.json)
remain unchanged as historical readiness evidence.

Campaign 05 is the append-only version 2 successor. Its preparation freezes the
pipeline, tasks, skills, grader, registry, descriptor, vendored Harbor adapter,
pinned runtime identity, exact offline model closure, job contract, host
identities, and auditor provenance. The closed snapshot and two dry runs now
reproduce input binding
`1df029a35e6566f8602db46dfbd6b7b8b9cfa5c24ddd5789304216b5210f0d80`.
It is scheduled after the provider reset with zero model calls; it is not yet
run, evaluable, or ranking-eligible. See its
[`preflight log`](reports/20260723-papers-consult-gpt53-spark-05-preflight-log.md)
and [machine-readable readiness record](reports/20260723-papers-consult-gpt53-spark-05-readiness.json).
The
cross-campaign [`evolution log`](reports/graphrag-papers-consult-campaign-evolution.md)
compares campaigns 01 through 05, links their evidence, and records exact rerun
commands. [ADR 0036](../../.specs/adr/0036-closed-campaign-local-harbor-inputs.md)
defines the version 2 execution-closure decision.

## Inspect and validate the registry

Run these commands from the repository root:

```bash
python evaluations/semantic-okf-datasets/dataset_tool.py list
python evaluations/semantic-okf-datasets/dataset_tool.py validate --dataset all
python evaluations/semantic-okf-datasets/dataset_tool.py describe --dataset graphrag-papers-40 --family legacy
```

## Repeat the papers evaluation

The GraphRAG paper test is a first-class dataset. The following legacy-family sequence exercises both modes.

Stage evaluator-free raw input and verify deterministic staging:

```bash
python evaluations/semantic-okf-datasets/dataset_tool.py prepare \
  --dataset graphrag-papers-40 --family legacy
python evaluations/semantic-okf-datasets/dataset_tool.py prepare \
  --dataset graphrag-papers-40 --family legacy --check
```

Build and validate a host-side snapshot. This is an independent end-to-end rehearsal; its `semantic/records.jsonl` must match the checked reference ledger for the legacy family.

```bash
python skills/build-semantic-okf/scripts/build_semantic_okf.py \
  evaluations/semantic-okf-datasets/generated/inputs/graphrag-papers-40/legacy/manifest.json \
  evaluations/semantic-okf-datasets/generated/bundles/graphrag-papers-40/legacy \
  --output-format json
python skills/build-semantic-okf/scripts/validate_semantic_okf.py \
  evaluations/semantic-okf-datasets/generated/bundles/graphrag-papers-40/legacy \
  --output-format json
```

Generate and validate all forty tasks in both modes:

```bash
python evaluations/semantic-okf-datasets/generate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family legacy --mode consult-only
python evaluations/semantic-okf-datasets/generate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family legacy --mode build-consult
python evaluations/semantic-okf-datasets/validate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family legacy --mode consult-only
python evaluations/semantic-okf-datasets/validate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family legacy --mode build-consult
```

Each validator command checks deterministic regeneration, prompt leakage, mode boundaries, hidden bindings, and 40 successful mechanical qualification oracles. Mechanical contract, retrieval, document-minimum, and anchor metrics do not establish semantic correctness.

Create cross-platform redacted Harbor dry runs:

```bash
python evaluations/semantic-okf-datasets/run_harbor.py \
  --dataset graphrag-papers-40 --family legacy --mode consult-only \
  --cohort holdout --task-id q005 --dry-run
python evaluations/semantic-okf-datasets/run_harbor.py \
  --dataset graphrag-papers-40 --family legacy --mode build-consult \
  --cohort holdout --task-id q005 --dry-run
```

## Repeat the Astro evaluation

Astro intentionally has no checked processed bundle in this registry. Build it first, then use that exact snapshot when generating and running consult-only tasks.

```bash
python evaluations/semantic-okf-datasets/dataset_tool.py prepare \
  --dataset astro-40 --family legacy
python skills/build-semantic-okf/scripts/build_semantic_okf.py \
  evaluations/semantic-okf-datasets/generated/inputs/astro-40/legacy/manifest.json \
  evaluations/semantic-okf-datasets/generated/bundles/astro-40/legacy \
  --output-format json
python skills/build-semantic-okf/scripts/validate_semantic_okf.py \
  evaluations/semantic-okf-datasets/generated/bundles/astro-40/legacy \
  --output-format json
python evaluations/semantic-okf-datasets/generate_harbor_tasks.py \
  --dataset astro-40 --family legacy --mode consult-only \
  --bundle evaluations/semantic-okf-datasets/generated/bundles/astro-40/legacy
python evaluations/semantic-okf-datasets/generate_harbor_tasks.py \
  --dataset astro-40 --family legacy --mode build-consult \
  --bundle evaluations/semantic-okf-datasets/generated/bundles/astro-40/legacy
python evaluations/semantic-okf-datasets/validate_harbor_tasks.py \
  --dataset astro-40 --family legacy --mode consult-only \
  --bundle evaluations/semantic-okf-datasets/generated/bundles/astro-40/legacy
python evaluations/semantic-okf-datasets/validate_harbor_tasks.py \
  --dataset astro-40 --family legacy --mode build-consult \
  --bundle evaluations/semantic-okf-datasets/generated/bundles/astro-40/legacy
```

Use `train`, `dev`, or `holdout` as the Astro runner cohort.

## Run another family

Replace `legacy` consistently in prepare, generate, validate, and run commands. `generated/inputs/<dataset>/<family>/input-manifest.json` records the exact host build and validation command shapes. Plan-backed builders receive the staged `plan.json` between the manifest and output arguments.

When a family's processed snapshot differs from the dataset descriptor's checked default, pass that same snapshot explicitly to both task generation and validation:

```bash
python evaluations/semantic-okf-datasets/generate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family adaptive --mode consult-only \
  --bundle evaluations/semantic-okf-datasets/generated/bundles/graphrag-papers-40/adaptive
python evaluations/semantic-okf-datasets/validate_harbor_tasks.py \
  --dataset graphrag-papers-40 --family adaptive --mode consult-only \
  --bundle evaluations/semantic-okf-datasets/generated/bundles/graphrag-papers-40/adaptive
```

The validator rejects an omitted `--bundle` before running the oracles when the existing task manifest is bound to a different reference tree. Always provide the exact family snapshot used to generate those tasks; a merely compatible or newly rebuilt snapshot will fail deterministic regeneration.

For `embeddings` and `ensemble`, pass an already verified Hugging Face cache to the runner:

```bash
--hf-cache /absolute/path/to/huggingface/hub
```

The runner rejects that option for every other family and rejects missing caches for those two families.

## Live Harbor execution

Build the shared runtime once on a Linux Docker host:

```bash
python evaluations/semantic-okf-harbor/runtime/build_runtime.py
```

Remove `--dry-run` and run from Linux or WSL. The default credential path is `~/.pi/agent/auth.json`; use `--auth-file` when the populated credential is elsewhere. Consult-only may use the descriptor's checked bundle or an explicit `--bundle`. Build-consult accepts `--input` but forbids `--bundle` because no processed snapshot may cross that mode boundary.

```bash
python evaluations/semantic-okf-datasets/run_harbor.py \
  --dataset graphrag-papers-40 --family legacy --mode consult-only \
  --cohort holdout --auth-file /mnt/c/Users/<user>/.pi/agent/auth.json
python evaluations/semantic-okf-datasets/run_harbor.py \
  --dataset graphrag-papers-40 --family legacy --mode build-consult \
  --cohort holdout --auth-file /mnt/c/Users/<user>/.pi/agent/auth.json
```

The current task defaults preserve the historical local Harbor network-policy limitation: agent and verifier phases use `public`, while the verifier performs no network operations and receives neither authentication nor public data mounts. Use the task generator's stricter network flags only on a Harbor host where its egress-control sidecar has passed a disposable smoke test.

### Fair eight-family campaign

Do not launch whole family cohorts in parallel. That schedule gives early families more model access when quota is exhausted. Build the eight family bundles below one new append-only campaign directory, then persist and inspect the balanced schedule without making a model call:

```bash
python evaluations/semantic-okf-datasets/run_consult_campaign.py \
  --campaign evaluations/semantic-okf-datasets/generated/campaigns/<new-campaign> \
  --schedule-only
```

On Linux or WSL, run the same command without `--schedule-only`, providing the existing Hugging Face cache required by Embeddings and Ensemble:

```bash
python evaluations/semantic-okf-datasets/run_consult_campaign.py \
  --campaign evaluations/semantic-okf-datasets/generated/campaigns/<new-campaign> \
  --hf-cache /absolute/path/to/huggingface/hub \
  --auth-file /mnt/c/Users/<user>/.pi/agent/auth.json
```

The tracked scheduler covers q001–q040 across all eight families exactly once, rotates every family through every wave position, counts the first real task as the quota preflight, runs at most four one-task shards concurrently, and stops submitting new work on the first terminal quota/rate/provider error. Before the first live shard it writes immutable `input-bindings.json` and `input-bindings.sha256` artifacts for the corrected task manifests and complete task trees, family bundles and ledgers, consultation skill trees, grader and family registry, model, Pi version, thinking level, runtime build receipt and image ID, and schedule. It rechecks the affected family bindings before each wave and requires the live Docker tag to resolve to that image ID; drift becomes a redacted runner abort before another model call. Existing in-flight shards finish and an aborted checkpoint is preserved. A completed mechanical campaign still requires blinded semantic review before any semantic winner claim.

## Reproducibility checklist

1. Validate the descriptor and chosen family.
2. Prepare raw input and rerun preparation with `--check`.
3. Build and validate a host-side snapshot for the selected family.
4. Generate both task modes and validate all mechanical qualification oracles.
5. Inspect one dry-run receipt per mode before consuming model quota.
6. Keep each live output append-only; never reuse an existing `--output` path.
7. Verify terminal trace outcomes; a result directory or receipt does not by itself make a trial evaluable.
8. Compare only campaigns with 40 complete final responses per family, identical dataset/runtime bindings, no provider or evaluator failures, and a separate semantic review.
