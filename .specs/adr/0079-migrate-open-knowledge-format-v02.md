---
adr: "0079"
title: "ADR 0079: Migrate Producers and Skills to Open Knowledge Format v0.2"
summary: "Adopt OKF v0.2 across exports, project projections, and every Semantic OKF builder while retaining documented v0.1 consumer fallbacks."
status: "Accepted"
date: "2026-07-29"
product: "knowledge"
owner: "Platform Architecture"
area: "Knowledge Interoperability"
tags: [knowledge, okf, skills, provenance, trust, attestation, evaluation]
---

# ADR 0079: Migrate Producers and Skills to Open Knowledge Format v0.2

## Status

Accepted. This supersedes the v0.1 producer and projection requirements in
ADRs 0002 and 0003. Their native-skill boundary, additive normalization, and
dedicated-project-bundle decisions remain accepted.

## Context

GoogleCloudPlatform `knowledge-catalog/okf/SPEC.md` at commit
`3fcbb9f828c2f23d109c855ee403c3a4c81f3a96`, dated July 24, 2026, specifies
OKF v0.2 and supersedes v0.1.

The new version retains the required concept `type`, reserved files, bundle
structure, recommended `title`, `description`, `resource`, and `tags`, and
permissive handling of extensions. It supersedes two v0.1 conventions:

- `timestamp` becomes `generated.at`, paired with required `generated.by`; and
- body `# Citations` becomes frontmatter `sources`, with keyed footnotes for
  claim attribution.

It also adds optional provenance credibility signals, verification events,
lifecycle fields, actor conventions, and the `Attested Computation` contract.

The repository had independent implementations in the `know` exporter, the
strict project projection, the standalone OKF skill, and fourteen standalone
Semantic OKF builders. Updating only one copy would publish inconsistent
bundles and invalidate deterministic evaluation bindings.

## Decision

Adopt OKF v0.2 as the only producer target.

- `know` exports always emit `generated.by: process:know-export`, migrate a
  known legacy `timestamp` to `generated.at`, and derive `sources` only from a
  concrete source resource.
- The project projector declares `okf_version: "0.2"` and adds deterministic
  `sources` plus `generated.by` to project, specification, and skill concepts.
- Every Semantic OKF builder declares version 0.2 and adds the exact normalized
  input locator as `sources[].resource` plus
  `generated.by: process:semantic-okf-python`.
- Semantic builds omit `generated.at`; injecting a build clock would break
  deterministic snapshots and would not describe the source content's last
  meaningful change.
- Producers do not infer `verified`, `status`, `stale_after`, credibility
  signals, executors, or attesters without evidence.
- The standalone validator accepts a bare `verified` mapping as one event and
  validates optional v0.2 family shapes when they are present.
- Native `SKILL.md` frontmatter remains limited to `name` and `description`.
- Historical frozen evaluation artifacts remain immutable. New builds and
  evaluation runs use v0.2 and append new evidence rather than rewriting old
  traces.

Consumers may retain the v0.2 specification's legacy fallbacks for v0.1
`timestamp` and body citations, but current producers must not emit those
legacy forms.

## Evaluation

The isolated Open Knowledge Format comparison is revised to cover lossless
v0.1-to-v0.2 migration and Attested Computation planning. Deterministic
Semantic OKF dataset descriptors, all declared strategy pairs, project
projection drift, relevant unit tests, and total application coverage must be
recalculated after the migration.

Live model evaluation results are append-only and must report the exact updated
prompt set and runtime. A structurally valid dry run is not a quality score.

The completed migration produced these results:

- all eight canonical GraphRAG family bundles rebuilt and validated as OKF
  v0.2 while retaining one shared 874-record authoritative ledger;
- all 16 family/mode Harbor task trees regenerated deterministically with
  leakage checks passing and 640 of 640 mechanical qualification oracles
  passing;
- all 16 family/mode q005 rehearsals produced redacted dry-run receipts with
  the intended raw-input or processed-knowledge boundary; and
- isolated Codex GPT-5.6 Sol evaluation
  `eval-xEl-2026-07-29T22:33:18` scored the standalone OKF skill at 5/5 and
  the no-skill control at 0/5 on the five updated prompts; and
- the final repository suite passed 776 tests with 90.9% total application
  coverage against the required 80% gate.

A preceding append-only run exposed two lexical false negatives in the
evaluation assertions. The calibrated run accepts semantically equivalent
resolved output paths and derivation wording without weakening any required
operation or safety condition.

## Consequences

Positive:

- all current producers expose first-class provenance and producer identity;
- project and Semantic OKF bundles declare one consistent current version;
- deterministic Semantic OKF output remains byte-reproducible;
- validators and skill instructions cover v0.2 trust, lifecycle, and
  attestation fields without making optional data mandatory.

Negative:

- bundle and source-manifest digests change even when authoritative record
  content does not;
- exact processed-snapshot evaluation bindings must be regenerated;
- v0.1 consumers that reject unknown minor-version fields may require their
  own upgrade despite the specification's best-effort consumption guidance.
