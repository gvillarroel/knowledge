# GraphRAG Papers Consultation Campaign Evolution Log

## Purpose and interpretation boundary

This is the durable, append-oriented index for the successive eight-family
`graphrag-papers-40` consultation alternatives. It records why each alternative
was retained, rejected, or superseded without rewriting its raw artifacts.
Detailed reports remain the authority for exact counts and hashes.

Preparation checks and dry runs are not evaluations. A row is evaluable only
when a live model response is complete and the current scorer emitted its full
finite metric vector with a recognized scored status. A fixed-matrix ranking
requires all 320 declared question/family cells plus the provider, evaluator,
and semantic-review requirements in ADR 0035.

## Alternative comparison

| Campaign | Activity type | Calls/cells submitted | Evaluable responses | Binding | Current disposition | What changed next |
|---|---|---:|---:|---|---|---|
| `20260717-papers-consult-gpt53-spark-01` | Historical live run | 320 result artifacts | 32/320 | Pre-provider-aware campaign | Invalid for comparison; no winner | Separate provider failures from semantic zeroes, restore rubric fidelity, and use a balanced one-cell scheduler |
| `20260717-papers-consult-gpt53-spark-02` | Counted live quota preflight | 1/320 | 0/320 | Version 1 precursor | Provider-quota-aborted; 319 cells unsubmitted | Preserve provider reset metadata safely and defer a new append-only attempt |
| `20260723-papers-consult-gpt53-spark-03` | Windows/WSL preparation dry run | 0/320 | 0/320 | Version 1, rejected digest | Abandoned before execution | Normalize paths to POSIX and sort case-sensitive UTF-8 bytes for cross-platform tree hashes |
| `20260723-papers-consult-gpt53-spark-04` | Cross-platform preparation and 320 task validations | 0/320 | 0/320 | Version 1, SHA-256 `d28382315291d0003687d04c7b0b4aa3bcb6738f8db10a9bcce34be6c5ad440a` | Superseded before execution; do not use its registered launcher for a live run | Close model bytes, pipeline, tasks, skills, Harbor, runtime, job contract, host identities, auditor provenance, and post-call drift checks |
| `20260723-papers-consult-gpt53-spark-05` | Atomic version 2 preparation, two frozen dry runs, and deferred scheduling | 0/320 | 0/320 | Version 2, SHA-256 `1df029a35e6566f8602db46dfbd6b7b8b9cfa5c24ddd5789304216b5210f0d80` | Scheduled awaiting provider reset; zero calls; not evaluable or rankable | Repeat readiness and the exact dry run after reset, then submit `adaptive/q001` as the counted quota preflight |

Campaign 01's 320 directories are structural artifacts, not 320 evaluable
answers. Campaign 02's one quota-ending attempt is not an evaluable response
and must not be combined with another campaign. Campaigns 03 and 04 made no
model call. Campaign 05 also has no model call while it waits for the provider
reset.

## Evidence map

| Campaign | Authoritative tracked evidence | Evidence type |
|---|---|---|
| 01 | [`audit v2`](20260717-papers-consult-gpt53-spark-01-audit-v2.md), [`test log`](20260717-papers-consult-gpt53-spark-01-test-log.md), and [`manual answer review`](20260717-papers-consult-gpt53-spark-01-manual-review.md) | Corrected forensic audit of an invalid live run |
| 02 | [`test log`](20260717-papers-consult-gpt53-spark-02-test-log.md), [`checkpoint`](20260717-papers-consult-gpt53-spark-02-checkpoint.json), and [`forensic report`](20260717-papers-consult-gpt53-spark-02-forensic.md) | Quota-aborted counted preflight and current-grader forensic interpretation |
| 03 | [`Campaign 04 preflight log, rejected-preparation section`](20260723-papers-consult-gpt53-spark-04-preflight-log.md#campaign-03-rejected-preparation) | Zero-call cross-platform digest rejection |
| 04 | [`preflight log`](20260723-papers-consult-gpt53-spark-04-preflight-log.md) and [`readiness snapshot`](20260723-papers-consult-gpt53-spark-04-readiness.json) | Historical version 1 readiness evidence, superseded by the execution-closure audit |
| 05 | [`preflight log`](20260723-papers-consult-gpt53-spark-05-preflight-log.md), [`readiness record`](20260723-papers-consult-gpt53-spark-05-readiness.json), [`pre-live forensic audit`](20260723-papers-consult-gpt53-spark-05-preflight-forensic.md), and [ADR 0036](../../../.specs/adr/0036-closed-campaign-local-harbor-inputs.md) | Closed version 2 preparation and deferred scheduler evidence; no live result yet |

The Campaign 04 readiness files accurately preserve what had passed when they
were written. Their scheduling conclusion is superseded: later audit showed
that version 1 did not bind the complete live execution closure. Do not rewrite
those historical files; append Campaign 05 evidence separately.

## Test layers

| Layer | Consumes model quota | What a pass establishes | What it does not establish |
|---|---|---|---|
| Registry and task validation | No | Pinned descriptors, isolated mounts, exact task regeneration, leakage checks, and mechanical oracle quality | Answer quality or model availability |
| Runtime input validation/build | No model call | Checked package pins and, after a build, one inspected image identity | Harbor task correctness or provider access |
| Frozen campaign dry run | No | The campaign-local version 2 binding and redacted Harbor job configuration reproduce | An evaluable response or ranking |
| Counted synchronous live preflight | Yes, one scheduled cell | The first declared cell reached a terminal live outcome | Matrix completion or family quality |
| Full balanced live run | Yes, up to 320 scheduled cells | Raw material for the fixed comparison when every cell is scorer-observable | Semantic correctness by itself |
| Strict summary and semantic review | No additional model call unless the review protocol declares one | Ranking eligibility and separately adjudicated semantic claims | Permission to merge cells across campaigns |

## Reproducible preparation and audit commands

Run the repository-wide registry gate first:

```bash
python evaluations/semantic-okf-datasets/dataset_tool.py validate --dataset all
```

Validate the pinned runtime inputs without invoking Docker, then build and
record the image on Linux or WSL:

```bash
python evaluations/semantic-okf-harbor/runtime/pinned/build_runtime.py \
  --validate-only
python evaluations/semantic-okf-harbor/runtime/pinned/build_runtime.py
```

Campaign 05 must be created atomically from the zero-call Campaign 04 bundles.
This is preparation only:

```bash
python evaluations/semantic-okf-datasets/freeze_consult_campaign.py \
  --campaign evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-05 \
  --source-campaign evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-04 \
  --hf-cache <absolute-huggingface-hub> \
  --harbor "$HOME/.local/bin/harbor"
```

After publication, repeat the dry run from the campaign-local repository and
use only its campaign-local model cache and Harbor entrypoint:

```bash
python evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-05/frozen/repo/evaluations/semantic-okf-datasets/run_consult_campaign.py \
  --campaign evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-05 \
  --hf-cache evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-05/frozen/model-cache/hub \
  --harbor evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-05/frozen/repo/vendor/harbor-cli \
  --dry-run
```

Forensic inspection is allowed while a campaign is incomplete and must never
emit a winner:

```bash
python evaluations/semantic-okf-datasets/summarize_consult_campaign.py \
  evaluations/semantic-okf-datasets/generated/campaigns/<campaign> \
  --allow-partial --allow-invalid --rescore
```

Strict summarization deliberately omits those flags and is appropriate only
after a completed checkpoint. It must exit nonzero unless every fixed cell and
binding requirement is satisfied:

```bash
python evaluations/semantic-okf-datasets/summarize_consult_campaign.py \
  evaluations/semantic-okf-datasets/generated/campaigns/<campaign>
```

## Append-only update rule

For every later alternative, add a new row and link its separately named
readiness, live, forensic, and semantic-review records. Never overwrite raw
campaign results, reuse a live output path, relabel a dry run as a live test,
convert a provider failure into a semantic zero, or combine successful cells
from different campaigns into one ranking.
