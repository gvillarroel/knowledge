# Tika/MALLET Consultation Trace Distillation: Cumulative Round 3

- Date: `2026-07-23`
- Dataset: `graphrag-papers-40`
- Skill: `consult-semantic-okf-tika-mallet`
- Status: `candidate-staged-not-promoted`
- Ranking eligible: `false`
- Published skill modified: `false`

## Provenance

Round 3 uses the same 24-trial discovery cohort and frozen baseline as the
earlier rounds. The baseline reproduces the Harbor TrialLock digest
`sha256:3324cfddf1dc52efb34ae557e17e4c991bda094e840dd61814a4aa4f13e5631d`.
The legacy discovery import contains 24 unique task checksums: 4 successes,
19 verifier failures, and 1 actionable provider context-limit failure.

The distiller ran under WSL to preserve Harbor 0.18.0's case-sensitive
POSIX-path ordering. No native Harbor lock, result, trace, diagnostic, or
receipt was edited or relabeled. Analyze-only did not read holdout inputs.

## Accepted cumulative proposals

| Proposal | Round added | Support | Effect |
|---|---:|---:|---|
| `diversify-answer-pack-facet-queries` | 1 | 4 trials / 4 tasks | Map distinct answer facets to complementary queries. |
| `seal-answer-pack-evidence-acquisition` | 1 | 8 trials / 8 tasks | Stop evidence acquisition after the bounded pack. |
| `select-only-direct-pack-support` | 2 | 4 trials / 4 tasks | Retain only excerpts that directly support complete claims. |
| `stop-after-first-finalization-pass` | 2 | 2 trials / 2 tasks | Treat the first passing finalization as terminal. |
| `bind-canonical-paper-identity-inside-answer-pack` | 3 | 3 trials / 3 tasks | Carry the persisted paper identity only inside pack selection. |
| `deduplicate-answer-pack-by-canonical-paper` | 3 | 3 trials / 3 tasks | Prevent paper and claims variants of one paper from consuming separate support slots. |
| `report-answer-pack-canonical-paper-diversity` | 3 | 3 trials / 3 tasks | Document canonical-paper diversity without changing the public evidence contract. |
| `preserve-validated-final-file-verbatim` | 3 | 11 trials / 11 tasks | Forbid reserialization or normalization of the validated final JSON. |

All eight patches were accepted and none was rejected.

The canonical-paper change is supported by q014, q016, and q018. Each original
ten-support pack contained only eight canonical papers because `paper-*` and
`claims-*` variants of the same article occupied separate source slots. All
three tasks then failed the mechanical gate with incomplete required-document
coverage.

The verbatim-transfer change is supported by 11 tasks. In those traces, the
passing finalizer file and the assistant response differed in 15 evidence
rows. Hyphens were normalized to dots in paths or hexadecimal characters were
omitted from hashes. The changed rows exactly matched the verifier's invalid
evidence indices.

## Candidate

The cumulative candidate digest is
`sha256:68de0ae6c8bea0a61b869253b01680062f83b133193006c870c663d1f7e8238b`.
Only these files differ from the frozen baseline:

- `references/querying.md`
- `scripts/query_semantic_okf_tika_mallet.py`

An intermediate implementation exposed an internal identity field through the
closed `batch-search` response and failed one candidate test. That artifact
was rejected. The final implementation keeps the identity internal to
`answer-pack`; all 17 consultant tests pass against the staged candidate.

The real q014 query set now produces 10 supports with 10 distinct canonical
paper identities while retaining the existing public pack schema.

## Saturation

A subsequent novelty-only round re-audited all 24 traces and supplied an empty
proposal set. Harbor accepted zero patches, rejected zero patches, produced an
unchanged baseline digest, and read no holdout input. This is the first round
in which the available discovery evidence cannot support another mutation.
See `trace-distillation-consult-v4-saturation-20260723.md`.

## Promotion gate

The candidate is not promoted. The strict schema-2 attempt failed closed
before development or holdout because the legacy discovery job's
`lock.json.retry` object lacks `include_exceptions`.

Promotion still requires new append-only Harbor 0.18.0 baseline and exact
candidate-development attempts with complete zero-retry locks, followed by a
disjoint untouched holdout. The provider previously reported
`usage_limit_reached` with reset at `2026-07-29T17:08:54-04:00`.

The builder and bounded-consult skills remain unchanged. A repository-wide
lock scan found no Harbor artifact for the builder. The bounded consultant has
one locked q028 trial, but it is a non-actionable provider-quota failure with
zero model tokens and is below the mandatory two-task support threshold. Its
separate saturation run also accepted zero patches and preserved its digest.

## Validation

- Harbor `--dry-run`, `--doctor`, and analyze-only consolidation: pass.
- Candidate Python compilation: 6 files passed.
- Candidate runtime smoke: pass.
- Candidate consultant suite: 17 passed.
- Synthetic internal-only canonical-paper deduplication: pass.
- Real snapshot pack diversity: 10 supports / 10 canonical identities.
- Snapshot inspection: 319 documents and 30 sources.
- Toolchains: Apache Tika `4.0.0-beta-1` and MALLET `2.1.0`.
- Both canonical datasets and all eight registered family pairs: pass.
- Tika/MALLET focused repository tests: 50 passed.
- Repository suite: 701 passed.
- Application coverage: 90.9%, above the required 80% threshold.

The canonical ranking table remains unchanged because the cumulative candidate
has not passed prospective development and sealed holdout evaluation.
