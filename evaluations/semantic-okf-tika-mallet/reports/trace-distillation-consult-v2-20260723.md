# Tika/MALLET Consultation Trace Distillation: Round 2

- Date: `2026-07-23`
- Dataset: `graphrag-papers-40`
- Skill: `consult-semantic-okf-tika-mallet`
- Status: `candidate-staged-not-promoted`
- Ranking eligible: `false`
- Published skill modified: `false`

## Provenance

The round-2 candidate uses the same frozen baseline and discovery cohort as
round 1. The baseline reproduces the discovery TrialLock digest
`sha256:3324cfddf1dc52efb34ae557e17e4c991bda094e840dd61814a4aa4f13e5631d`.
Its source-only tree also reproduces the run receipt digest
`d6ab811fe99c9c4b765d286e71272ad5e27345cb2f0b8bc4fd3c8b4f0a7faefe`.

Harbor 0.18.0 computes its skill digest by sorting native `Path` values.
Windows and Linux order the mixed-case path set differently. The digest was
therefore verified and the distiller was run under WSL, consistent with ADR
0035's case-sensitive POSIX-path requirement. No lock, result, trace, or
receipt was edited or relabeled.

The legacy analyze-only import normalized 24 unique trials and 24 unique task
checksums:

- 4 scored successes;
- 19 scored verifier failures; and
- 1 non-evaluable but actionable provider context-limit failure.

Analyze-only did not read holdout results. It is discovery evidence, not
promotion evidence.

## Accepted proposals

| Proposal | Round | Evidence support | Candidate change |
|---|---:|---:|---|
| `diversify-answer-pack-facet-queries` | Retained from 1 | 4 trials / 4 tasks | Map distinct requested facets to complementary, mechanism-specific queries instead of generic labels or near-synonyms. |
| `seal-answer-pack-evidence-acquisition` | Retained from 1 | 8 trials / 8 tasks | Make a successful `answer-pack` terminal for evidence acquisition and require a declared null response instead of direct bundle reads or follow-up searches. |
| `select-only-direct-pack-support` | Added in 2 | 4 trials / 4 tasks | Treat the pack as a candidate set and retain only exact excerpts that directly ground a complete claim. |
| `stop-after-first-finalization-pass` | Added in 2 | 2 trials / 2 tasks | Treat the first successful `finalize-answer` result as terminal and allow repair only after an error. |

The new evidence-selection proposal is supported by q002, q014, q019, and
q027. Those trials emitted 5 to 10 evidence rows, achieved evidence precision
from 0.25 to 0.60, and all failed the mechanical qualification gate. This
supports removing weakly related rows instead of filling a requested
source-count margin.

The new terminal-finalization proposal is supported by q014 and q026. q014
invoked the finalizer three times, producing two passes and one overwrite
error. q026 produced three separate passing final files. Both traces continued
after the first passing result.

All four proposals meet the configured minimum of two unique trials and two
unique task checksums. None was rejected. The resulting exploratory candidate
digest is
`sha256:28f5711230bb63e42ccd459f36de87149b894d8ba120953db1ef96b1a7a111cd`.
Only `references/querying.md` differs from the frozen baseline; its SHA-256 is
`91851f1e526ebb3cf7d50d9b83d80660c126f21ff0a10f34108c16d03748e943`.

## Promotion gate

The candidate is not promoted. A strict schema-2 attempt stopped before
holdout access because the legacy discovery job's `lock.json.retry` object
lacks the required `include_exceptions` field. The artifacts can support
diagnosis and candidate materialization, but they cannot satisfy the
prospective development and holdout protocol.

A replacement live evaluation is also externally blocked. The provider
returned `usage_limit_reached` before model tokens or agent tool calls and
reported a reset at `2026-07-29T17:08:54-04:00`.

After provider access is restored, promotion requires new append-only Harbor
0.18.0 jobs with zero built-in retries:

1. rerun the exact frozen baseline on the development cells with complete
   schema-2 retry metadata;
2. run this exact candidate on the same cells with new attempts;
3. run baseline and candidate on a disjoint untouched holdout; and
4. promote only if all required rewards pass, candidate errors are absent,
   mean gain is non-negative, and no holdout task regresses.

The builder and bounded-consult skills remain unchanged because no compatible
eligible trace set supports mutations to their locked identities.

## Validation

- Harbor trace-distillation `--dry-run`: pass.
- Harbor trace-distillation `--doctor`: pass.
- Legacy analyze-only normalization and four-proposal consolidation: pass.
- Strict schema-2 fail-closed behavior before holdout access: pass.
- Candidate Python syntax compilation without candidate bytecode writes: pass.
- Candidate runtime smoke: pass.
- Candidate inspection of the 319-document, 30-source snapshot: pass.
- Exact snapshot identity: Tika `4.0.0-BETA` and MALLET `2.1`: pass.
- Canonical dataset validation for both datasets and all eight registered
  strategy pairs: pass.
- Tika/MALLET focused test suite: 50 passed.
- Repository test suite: 701 passed.
- Repository coverage gate: 90.9%, above the required 80% threshold.

The candidate does not change the canonical ranking table because it has not
passed prospective development and sealed holdout evaluation.
