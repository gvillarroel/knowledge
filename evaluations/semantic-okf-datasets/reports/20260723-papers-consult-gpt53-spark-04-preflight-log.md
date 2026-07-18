# GraphRAG Papers Consult Campaign 04 Preflight Log

## Purpose

Campaign `20260723-papers-consult-gpt53-spark-04` is the prepared successor to
the provider-quota-aborted campaign 02 and the cross-platform-rejected campaign
03. It preserves the corrected consultation tasks, exact family bundles,
provider-aware terminal handling, mechanical grader, and balanced 320-cell
schedule.

This campaign has **not run any evaluation cell and is not ranking-eligible**.
Its live preflight must wait until the provider reset at
`2026-07-23T14:24:32+00:00` (`2026-07-23T10:24:32-04:00`, EDT).

## Campaign 03: rejected preparation

Campaign `20260723-papers-consult-gpt53-spark-03` created an immutable input
binding on Windows with SHA-256
`20117467fdd966b0600067d88118f9eac73f93afaebcfb0f23ad733532de840b`.
The subsequent WSL dry run rejected that binding before Harbor launch or any
model call because its generated task and skill tree digests differed across
operating systems.

The cause was native `Path` ordering: Windows compared mixed-case paths
case-insensitively, while Linux compared them case-sensitively. Tree digests now
normalize relative paths to POSIX form and sort their UTF-8 bytes
case-sensitively before hashing. Campaign 03 remains append-only with its
original rejected binding and with zero runs, terminal outcomes, or checkpoints.
It must never be resumed or rewritten.

## Campaign 04: frozen readiness evidence

Campaign 04 was created as a new append-only directory after the canonical tree
digest correction.

| Check | Result |
|---|---|
| Dataset and mode | `graphrag-papers-40`, `consult-only` |
| Strategy families | 8 of 8 |
| Balanced schedule cells | 320 |
| Schedule SHA-256 | `f202c3c8744cc8259fddce586826768c90e896c8c180a0b2e96a0a88aaf70f7d` |
| Immutable input-binding SHA-256 | `d28382315291d0003687d04c7b0b4aa3bcb6738f8db10a9bcce34be6c5ad440a` |
| Runtime image ID | `sha256:1315195dcef58980e6d2620eaa41062ea6edc15c3eb8ed47d42c143be57aded5` |
| Exact family-bundle task validation | Passed, 320 of 320 tasks |
| Windows schedule/input-binding dry run | Passed |
| WSL schedule/input-binding dry run | Passed with the same binding SHA-256 |
| Live runtime tag/image-ID check | Passed |
| Runs / outcomes / checkpoints | `0 / 0 / 0` |

Each of the eight family validators used the exact bundle copied into campaign
04 and passed all 40 deterministic task checks. These are mechanical readiness
checks only; they do not count as model responses or semantic evaluation
results.

The exact-bundle checks are reproducible by replacing `<family>` with each of
the eight registered family IDs:

```bash
python evaluations/semantic-okf-datasets/validate_harbor_tasks.py \
  --dataset graphrag-papers-40 \
  --family <family> \
  --mode consult-only \
  --bundle evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-04/bundles/<family>
```

## Repository validation gates

| Gate | Result |
|---|---|
| Focused campaign, grader, dataset, and digest regressions | 42 passed |
| Full repository suite | 1,841 passed, 10 skipped |
| Coverage scope | 719 passed |
| Total application coverage | 90.9% against an 80.0% minimum |
| Python compilation | 14 changed or new Python files passed |
| Dataset registry | Both datasets and all eight families passed |
| Diff whitespace check | Passed |
| Campaign 02 strict forensic summary | Rejected incomplete campaign with exit code 1, as required |

The full suite explicitly prioritized this checkout's `src` directory because
the interactive environment inherited a `PYTHONPATH` entry for another
worktree. The repository coverage command already enforces the same local-path
precedence internally. After stale concurrent coverage processes were removed,
the required clean command completed normally:

```bash
python scripts/check_coverage.py --threshold 80
```

## Deferred execution registration

The local Windows task `SemanticOKF-Campaign04` is registered to invoke WSL at
`2026-07-23T10:26:00-04:00` (`2026-07-23T14:26:00+00:00`), 88 seconds after
the provider's reset instant. The task is currently `Ready` and has never run;
Task Scheduler result `0x00041303` is the standard not-yet-run state.

| Control | Frozen value |
|---|---|
| Launcher | `generated/campaigns/20260723-papers-consult-gpt53-spark-04/launch-after-reset.sh` |
| Launcher SHA-256 | `ef14cc83353a618e1e63c6a15a16e121d9c437c0041e4e867a939b43fcc3ad06` |
| Shell syntax and input validation | Passed |
| Early-start guard | Passed; refused with exit 75 and created zero runs or outcomes |
| Multiple instances | `IgnoreNew` plus a nonblocking WSL `flock` |
| Availability policy | Start when available and wake to run |
| Failure policy | Three retries, fifteen minutes apart |
| Execution time limit | 72 hours |
| Logon mode | Current-user interactive token; a missed trigger starts at the next available interactive session |

The launcher contains paths but no credentials or tokens. It verifies the
frozen campaign, cache, authentication file, and Harbor executable without
serializing their contents; refuses to run before the reset; never repeats
execution when a terminal checkpoint already exists; and appends stdout and
stderr below the campaign's ignored `launcher-logs/` directory. The campaign
runner still revalidates its immutable binding and live Docker image before any
model call.

After execution, the launcher always writes current-grader forensic JSON and
Markdown reports with `--allow-partial --allow-invalid --rescore`. It attempts
strict final JSON and Markdown reports only when the campaign has a completed
checkpoint. A failed strict audit exits nonzero and therefore cannot silently
turn a mechanically completed but invalid campaign into a ranking.

## Execution and ranking boundary

Campaign 04 is scheduled for one counted synchronous quota preflight after the
provider reset. Before that time, another live attempt would consume a campaign
cell only to reproduce the known account-level limit. No campaign 04 run,
outcome, or checkpoint artifact currently exists, and no result from campaigns
01, 02, or 03 may be merged into it.

If the counted preflight succeeds, the fair scheduler may continue the complete
balanced schedule under the frozen binding. If it fails, campaign 04 must remain
append-only as another aborted attempt. Even a mechanically complete 320-cell
run will remain ineligible for a winner claim until all scorer-observability and
blinded semantic-review requirements pass.

At or after the reset, the deferred WSL command is:

```bash
python3 evaluations/semantic-okf-datasets/run_consult_campaign.py \
  --campaign evaluations/semantic-okf-datasets/generated/campaigns/20260723-papers-consult-gpt53-spark-04 \
  --hf-cache /mnt/c/Users/<user>/.cache/huggingface/hub \
  --auth-file /mnt/c/Users/<user>/.pi/agent/auth.json \
  --harbor "$HOME/.local/bin/harbor" \
  --max-concurrency 4
```
