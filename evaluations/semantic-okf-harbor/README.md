# Semantic OKF Harbor Evaluation

This directory adapts the frozen forty-question Astro benchmark to Harbor without changing any Semantic OKF builder or consultation skill. It is a prospective skill-evolution harness, not a new claim that the repeatedly inspected Astro corpus is an untouched population holdout.

The checked-in inputs are compact and immutable. Generated Harbor tasks, runtime build receipts, raw trials, model traces, and result bundles are append-only and ignored. The agent receives one question, the source-generic response contract, one read-only published bundle at `/knowledge`, and exactly one frozen consultation skill which the prompt requires it to use. Qrels, hard-question ground truth, and authoritative scoring inputs exist only in a separate credential- and mount-isolated verifier image.

## Experimental boundary

- `train`: 24 questions. The previously inspected `q039` and `q040` are forced here.
- `dev`: 8 questions used once to decide whether a frozen evolved candidate is promotable.
- `holdout`: 8 prospectively reserved question labels used only after the candidate is frozen.
- The split is question-label-disjoint, not source-disjoint. Authoritative pages overlap cohorts.
- Baseline and evolved runs use separate Harbor jobs with the same question, bundle, model, Pi version, timeouts, and verifier. Only the installed skill snapshot changes.
- An all-skills portfolio is not causal evidence.

## Runtime and generation

Build the common runtime from WSL or another Linux Docker host:

```bash
python evaluations/semantic-okf-harbor/runtime/build_runtime.py
```

Model weights are not copied into the image. When a family needs the pinned embedding model, mount its already verified cache read-only for that job.

Generate the ignored task dataset:

```bash
python evaluations/semantic-okf-harbor/generate_tasks.py
python evaluations/semantic-okf-harbor/validate_tasks.py
```

Each task uses the prebuilt `semantic-okf-harbor-runtime:1.0` agent image. Its private `tests/Dockerfile` extends the same image with the grader and hidden inputs. Harbor collects the built-in Pi JSONL log as an artifact; the grader extracts the last assistant message from that log.

The current WSL Docker host cannot start Harbor 0.18.0's egress-control sidecar for either the agent allowlist or a `no-network` separate verifier. Generated local-live tasks therefore default both phases to `public`. The verifier code performs no network operations and receives neither the bundle nor authentication mounts, but egress is not technically blocked. This is recorded as `agent_network_enforcement: false` and `verifier_network_enforcement: false`. `generate_tasks.py --agent-network-mode allowlist --verifier-network-mode no-network` is available for a compatible Harbor host and must pass a disposable smoke test before use.

Run configurations must pin Harbor `0.18.0`, built-in agent `pi` version `0.73.1`, and model `openai-codex/gpt-5.3-codex-spark`. Mount exactly one accepted family bundle at `/knowledge` read-only. Copy the host Pi authentication file into a per-run temporary directory, mount that temporary directory only for the job, and delete it after Harbor exits. Never put authentication contents in a config, image, report, or Git.

Create the immutable local baseline snapshots, then run one append-only job from WSL. Repeat the snapshot command for each family. This pilot uses one attempt for every cohort; the result must therefore be interpreted as a diagnostic case study, not a stable population estimate. Pass the populated Pi credential explicitly when the WSL home credential is not the Windows credential.

```bash
python evaluations/semantic-okf-harbor/snapshot_skills.py --generation baseline --family legacy
python evaluations/semantic-okf-harbor/run_harbor.py \
  --family legacy --generation baseline --split train \
  --auth-file /mnt/c/Users/<user>/.pi/agent/auth.json
```

After freezing a standalone evolved package in `snapshots/evolved-manifest.json`, snapshot and run it with the same family, split, bundle, and model. Produce checked compact outputs without copying raw responses or traces:

```bash
python evaluations/semantic-okf-harbor/summarize_results.py \
  --baseline evaluations/semantic-okf-harbor/results/<baseline-job> \
  --evolved evaluations/semantic-okf-harbor/results/<evolved-job> \
  --split train \
  --output-json evaluations/semantic-okf-harbor/reports/<family>-train.json \
  --output-markdown evaluations/semantic-okf-harbor/reports/<family>-train.md
```

## Metrics

The verifier emits `/logs/verifier/reward.json` with independent dimensions. A non-compensating `quality_gate` requires a strict response contract, a substantive answer, valid references, and valid evidence. Retrieval metrics are computed over evidence actually cited in the answer: precision, recall, reciprocal rank, nDCG, and complete-qrel coverage. Hard tasks additionally score required-document coverage, exact authoritative-span coverage, atomic-claim evidence completeness, and important-negative evidence completeness.

These hard metrics measure evidence sufficiency. They do not, by themselves, prove semantic correctness, prose completeness, or entailment. Any later semantic answer score must come from an independently frozen rubric or blinded review and remain separate from the deterministic evidence metrics.

## Evolution protocol

1. Freeze the task, grader, runtime, accepted bundle, and baseline skill hashes.
2. Run each family baseline on train once.
3. Inspect only train traces and make exactly one standalone evolved candidate for that family.
4. Freeze the candidate before dev.
5. Promote only if contract and evidence validity remain perfect, answerable abstentions do not increase, macro quality does not regress, hard evidence metrics do not regress, and cost/latency remain within the declared bound.
6. Run each frozen baseline and candidate once on the declared holdout pilot case. Do not edit a candidate after holdout output is opened.
7. Report paired per-question deltas and retries. Retry only transport or rate-limit failures, never semantic or contract failures.

The source for every test is the pinned Astro benchmark under `evaluations/semantic-okf-astro/benchmark/`, whose questions were produced evidence-first from the authoritative Astro MDX corpus pinned in that evaluation. The corpus contains the 416 English MDX files from the official `withastro/docs` repository at commit `5c37be52c5038e1174be1e838d3dd5852db26a21`. The ten hard questions were written only after locating and hashing their authoritative evidence spans. The new split changes experimental use, not question text or ground truth.

## Compact checked evidence

- `campaign.json` freezes the live cases, runtime, model, one-evolution limit, gates, and interpretation boundary.
- `snapshots/baseline-manifest.json` and `snapshots/evolved-manifest.json` bind every immutable skill tree.
- `campaign-bindings.json` binds accepted append-only jobs and trials by four independent hashes; it never discovers a convenient run by globbing.
- `summarize_campaign.py` verifies those bindings and writes cohort-separated JSON and Markdown tables.
- `skill-arena/` contains six direct baseline/evolved configs. Their validation and dry runs establish configuration integrity only; Harbor supplies the live model evidence.
- `reports/benchmark-id-audit.{json,md}` proves that all forty question IDs, qrel identities, crosswalk joins, and forty-six authoritative hard-evidence locators are coherent.
- `reports/q031-semantic-review.*`, `q032-semantic-review.*`, and `q034-semantic-review.*` score actual answer prose with separately frozen atomic rubrics; they do not relabel evidence coverage as correctness.
- `reports/` contains compact paired and campaign reports. Raw answers, traces, generated tasks, bundles, and local runtime receipts remain ignored.
