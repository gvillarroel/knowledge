---
adr: "0036"
title: "ADR 0036: Require Closed Campaign-Local Inputs for Live Harbor Evaluation"
summary: "Freeze every non-secret execution input, use an immutable runtime identity, and fail closed on drift before and after each live wave."
status: "Accepted"
date: "2026-07-17"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic OKF Evaluation"
tags:
  - semantic-okf
  - harbor
  - evaluation
  - hermetic-execution
  - reproducibility
  - supply-chain
---

# ADR 0036: Require Closed Campaign-Local Inputs for Live Harbor Evaluation

## Status

Accepted.

This decision extends ADR 0035. Provider-aware outcome handling is necessary
for a fair campaign, but it is insufficient unless every non-secret input used
by a live shard is also fixed and independently verifiable.

## Context

Campaign 03 demonstrated that a content digest can disagree across operating
systems when paths are sorted with platform-native comparison rules. Campaign
04 corrected that defect and reproduced one input-binding version 1 digest on
Windows and WSL, but a later execution-closure audit found that the binding was
still incomplete.

Version 1 bound the schedule, generated task tree, family bundles, consultation
skills, grader, registry, model name, Pi version, and a runtime image ID. It did
not close all bytes that a live shard could consume. In particular, the host
Hugging Face cache, repository pipeline sources, installed Harbor package and
its Pi adapter, host executable identities, and final Harbor job contract could
change after preparation. Several paths still pointed at shared mutable trees.
The stock Harbor 0.18.0 Pi adapter also installs Node and Pi during each agent
image build, so a pinned base image alone does not make the executed Pi package
reproducible.

Cross-platform equality of an incomplete manifest is readiness evidence, not
proof that the eventual live execution uses the same inputs. Campaign 04 must
therefore remain a zero-call, superseded preparation artifact rather than be
used for the scheduled live evaluation.

## Decision

Require input-binding schema version 2 for every new live consultation
campaign. Version 1 remains readable only for historical and forensic audits.

### Atomic campaign-local snapshot

Create each version 2 campaign in a temporary sibling directory, validate it,
run its campaign-local dry run, and publish it with one atomic rename. Refuse to
overwrite an existing campaign path. A zero-call campaign may supply reviewed
family bundles to a successor, but its run, outcome, and checkpoint trees must
be empty.

The campaign-local snapshot contains:

- the balanced 320-cell schedule and all eight exact family bundles;
- all 320 generated consultation tasks, 320 verifier Dockerfiles, and eight
  task manifests rewritten to a content-addressed local tag that encodes the
  immutable runtime image ID;
- the eight consultation skill packages, current grader, dataset descriptor,
  cohorts, family registry, and execution and reporting pipeline sources;
- a vendored Harbor 0.18.0 package whose Pi adapter is patched only after its
  checked source digest matches, and a campaign-local Harbor entrypoint;
- the pinned runtime inputs and build receipt; and
- a dereferenced offline copy of the exact
  `sentence-transformers/all-MiniLM-L6-v2` revision
  `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` required by Embeddings and
  Ensemble.

Reject symbolic links, shared hardlinks, unexpected files, path traversal,
case-fold collisions, incomplete model inventories, and task/runtime identity
drift in the closed snapshot. Tree ordering uses normalized relative POSIX
paths sorted by their case-sensitive UTF-8 bytes on every host.

### Runtime and Harbor closure

Build the execution image from checked, hash-pinned inputs. The qualified image
contains Python 3.12.13, Node 22.23.1, npm 10.9.8, and
`@mariozechner/pi-coding-agent` 0.73.1 with its npm integrity value recorded.
Dockerfiles cannot portably use a bare `sha256:<image-id>` in `FROM`: BuildKit
interprets it as a repository name. Tasks and verifier Dockerfiles therefore
use a campaign-qualified local tag whose suffix is the complete image ID. The
binding records both values, and every pre/post-wave check requires Docker to
resolve that exact tag to the separately attested ID. A retargeted tag is
drift, not a valid continuation.

The vendored Harbor adapter must use the preinstalled Node and Pi distribution
and must not download or install them while building a trial. Bind the Harbor
source tree, dependency inventory, entrypoint, interpreter, and version into
the campaign manifest.

### Version 2 binding and drift boundary

Bind the frozen-input manifest and trees, offline model closure, runtime build
receipt and image ID, task/job contract, pipeline, grader, registry, descriptor,
Harbor distribution, relevant host executable identities, and auditor
provenance in canonical JSON with a sidecar SHA-256.

Recompute the complete binding before live execution, before every submitted
wave, and after every wave. A post-call mismatch converts the affected result
to a runner failure and stops new submissions; it must never be treated as a
semantic zero. The campaign-local shard runner independently verifies the same
version 2 binding and permits only its campaign-local tasks, skills, model
cache, Harbor adapter, and runtime identity.

### Authentication continuity without secret binding

Authentication is an external secret, not an evaluation artifact. Validate
that the supplied JSON contains an `openai-codex` credential, then create one
private copy scoped to the input-binding digest for the whole campaign. Reuse
that copy across shards and restarts so token refresh continuity is preserved.
Delete it only after a terminal checkpoint. Never persist the credential,
credential hash, provider headers, or raw provider error text in campaign
manifests or reports.

### Readiness and ranking remain separate

Successful freezing, deterministic regeneration, a dry run, task validation,
or scheduler registration records preparation only. None consumes a model
call or produces an evaluable response. ADR 0035 still governs live outcome
classification and ranking: all 320 cells must be scorer-observable and free
of provider and evaluator failures before the fixed matrix is rankable, and
semantic winner claims still require a separate blinded or documented manual
review.

## Alternatives considered

- **Extend version 1 with the model-cache digest only.** Rejected because the
  mutable execution pipeline, Harbor package, job contract, and host
  executables would remain outside the trust boundary.
- **Trust a Docker tag without a separate image-ID check.** Rejected because a
  tag can be retargeted between preparation and execution. The selected local
  tag encodes the ID and is re-resolved against the separately bound ID.
- **Mount the original Hugging Face cache.** Rejected because its snapshots are
  symlinks into a shared blob store and unrelated cache mutation would remain
  possible. The campaign receives independent regular files only.
- **Use the globally installed Harbor command at run time.** Rejected because
  package upgrades or adapter changes would alter execution after binding.
- **Allow stock Harbor to install Node and Pi during every trial.** Rejected
  because live package resolution is not reproducible and adds an unnecessary
  network dependency.
- **Hash the authentication file.** Rejected because it would serialize a
  stable secret-derived value and would make legitimate token refreshes look
  like evaluation-input drift.
- **Resume Campaign 04 after adding external checks.** Rejected because its
  immutable version 1 binding cannot be rewritten. Campaign 05 is a new
  append-only preparation under version 2.

## Consequences

Positive:

- every non-secret byte and execution contract that can affect a shard is
  campaign-local or explicitly bound;
- Windows and Linux verify the same normalized identities;
- trial images do not resolve Node or Pi from the network;
- drift is detected on both sides of a model call; and
- authentication remains usable across restarts without becoming part of the
  published evidence.

Negative:

- every campaign snapshot includes an independent model copy and vendored
  execution package, increasing preparation time and disk use;
- preparing a campaign requires an already qualified runtime image and a
  locally installed, exactly supported Harbor distribution;
- hashing the closed trees before and after waves adds host-side overhead; and
- a drift detected after a model call invalidates that cell as infrastructure
  failure even if an answer was produced.

## Verification

The checked pins can be verified without Docker:

```bash
python evaluations/semantic-okf-harbor/runtime/pinned/build_runtime.py \
  --validate-only
```

On Linux or WSL, build and record the qualified runtime, atomically prepare a
new campaign, then repeat the campaign-local dry run:

```bash
python evaluations/semantic-okf-harbor/runtime/pinned/build_runtime.py
python evaluations/semantic-okf-datasets/freeze_consult_campaign.py \
  --campaign evaluations/semantic-okf-datasets/generated/campaigns/<new-campaign> \
  --source-campaign evaluations/semantic-okf-datasets/generated/campaigns/<zero-call-campaign> \
  --hf-cache <absolute-huggingface-hub> \
  --harbor "$HOME/.local/bin/harbor"
python evaluations/semantic-okf-datasets/generated/campaigns/<new-campaign>/frozen/repo/evaluations/semantic-okf-datasets/run_consult_campaign.py \
  --campaign evaluations/semantic-okf-datasets/generated/campaigns/<new-campaign> \
  --hf-cache evaluations/semantic-okf-datasets/generated/campaigns/<new-campaign>/frozen/model-cache/hub \
  --harbor evaluations/semantic-okf-datasets/generated/campaigns/<new-campaign>/frozen/repo/vendor/harbor-cli \
  --dry-run
```

The dry run is a binding and configuration rehearsal only. It must report zero
model calls and does not make the campaign evaluation-complete or
ranking-eligible.
