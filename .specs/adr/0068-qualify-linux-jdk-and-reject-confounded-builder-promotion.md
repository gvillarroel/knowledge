# ADR 0068: Qualify Linux JDK and reject a confounded builder promotion

## Status

Accepted on 2026-07-27.

## Context

The Tika/MALLET builder could not run in Harbor because the shared Debian 12 image
had no Linux Java runtime. The build contract requires Java 17 or later and forbids
downloading a runtime inside a trial. The frozen consultation control also means a
builder treatment must install two skills in one Harbor job.

The generated candidate-family task initially described generic
`/dataset/manifest.json` and `/dataset/plan.json` inputs. The Tika/MALLET builder
actually consumes separate immutable ingestion and retrieval plans.

Harbor trace distillation then exposed a Harbor 0.18 multi-skill edge case. The
distiller replaced the target builder with a `Path`, while the frozen consultation
skill remained a string. `Job.create()` re-resolved only string entries and dropped
the candidate builder. The incomplete attempt was stopped before it could be
treated as development evidence.

After correcting those prerequisites, builder candidate v45 produced rewards
`0.8637`, `0.3942`, and `0.6454` on q009, q011, and q012. It had no errors and passed
all required mechanical gates, but only one of three trials reached the `0.70`
primary threshold. The required development pass rate was 100%.

## Decision

Extend the preserved Harbor 1.0 image with the exact Debian package
`openjdk-17-jdk-headless:amd64 17.0.19+10-1~deb12u2`. Keep the original image
available under its content-addressed local tag. Bind the active image, Dockerfile,
JDK version, and qualified Tika/MALLET jar-tree digests in a checked runtime receipt.
Mount Tika and MALLET read-only at stable paths in every evaluation arm.

Use append-only build-consult task tree v43, whose instruction names
`/dataset/ingestion-plan.json` and `/dataset/retrieval-plan.json`. Require
deterministic regeneration, leakage checks, and all 40 oracle gates before live
evaluation.

Use the repository-local trace adapter to stringify every skill path after candidate
substitution. Require a no-model `Job.create()` check to prove that both target and
control skills survive Harbor resolution.

Reject builder candidate v45 and keep holdout closed. Do not copy its patch into the
source builder. The builder produced the same authoritative records digest in every
arm, while the primary reward measured the downstream answer. A future builder
promotion must include direct build-specific metrics before semantic answer reward
can be interpreted causally.

## Consequences

- Linux Java, Tika, and MALLET now pass the actual builder preflight inside the
  Harbor image used by generated tasks.
- The original runtime image remains recoverable by content-addressed tag.
- v43 is the first valid build-consult task tree for this candidate family.
- The v44 staging failure is preserved as excluded infrastructure evidence, not a
  scored candidate attempt.
- Candidate v45 remains an experimental artifact; the source builder and holdout are
  unchanged.
- Further builder evolution needs a verifier surface for build success, validation,
  reproducibility, and snapshot identity rather than relying only on end-answer
  variation.
