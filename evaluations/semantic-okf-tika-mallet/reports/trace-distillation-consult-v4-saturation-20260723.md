# Tika/MALLET Consultation Trace Distillation: Round 4 Saturation

- Date: `2026-07-23`
- Dataset: `graphrag-papers-40`
- Skill: `consult-semantic-okf-tika-mallet`
- Status: `saturated-no-new-evolution`
- New accepted proposals: `0`
- New rejected proposals: `0`
- Holdout read: `false`

## Saturation result

After the cumulative round-3 candidate was validated, all 24 discovery
trajectories were audited again against their tool sequence, finalizer output,
assistant response, verifier diagnostics, qualification metrics, pack query
coverage, and canonical-paper diversity.

The novelty-only proposal file was intentionally empty because no remaining
observation established another safe mutation with the required support of at
least two unique trials and two unique task checksums.

Harbor materialized an unchanged candidate:

- baseline digest:
  `sha256:3324cfddf1dc52efb34ae557e17e4c991bda094e840dd61814a4aa4f13e5631d`;
- saturation candidate digest:
  `sha256:3324cfddf1dc52efb34ae557e17e4c991bda094e840dd61814a4aa4f13e5631d`;
- baseline-to-candidate diff: empty;
- accepted patches: none;
- rejected patches: none; and
- holdout access: none.

This is the first attempt in which the available discovery cohort cannot
evolve the skill further.

## Other Tika/MALLET skill identities

The bounded consultant was checked through a separate Harbor saturation run.
Its only locked discovery trial is q028, a provider-quota failure with zero
input and output tokens. Harbor classified it as non-evaluable,
non-actionable, and ineligible proposal evidence. The run accepted zero
patches, rejected zero patches, and preserved the bounded skill digest
`sha256:e7a59befad271cbea48d45bbb50737b717adc7c2514c56b852ebc4d8a433ca59`.

A repository-wide native-lock scan found no Harbor artifact for
`build-semantic-okf-tika-mallet`. Analyze-only requires at least one completed
discovery artifact, so there is no legal builder trace pool to distill.

## Covered recurring patterns

| Recurring causal pattern | Cumulative round-3 coverage |
|---|---|
| Unbounded reads after a successful pack | `seal-answer-pack-evidence-acquisition` |
| Generic or redundant facet queries | `diversify-answer-pack-facet-queries` |
| Weak evidence retained to fill source margins | `select-only-direct-pack-support` |
| Repeated finalization after a pass | `stop-after-first-finalization-pass` |
| Paper and claims variants consuming separate slots | Three canonical-paper diversity patches |
| Exact identities changed while transferring final JSON | `preserve-validated-final-file-verbatim` |

## Remaining non-evolvable observations

- Only q018 had a requested query with zero selected pack supports. One task
  cannot satisfy the two-task transferability gate.
- The q028 provider context-limit outcome supports only the already accepted
  context-budget mutation.
- Provider quota remains an external failure and is not proposal evidence.
- Environment preparation and snapshot inspection occurred in successful and
  unsuccessful trials, so the traces do not establish them as a failure cause.
- Residual incomplete hidden-qrel coverage identifies weak cases but does not,
  by itself, establish another safe procedural or code mutation.

Further evolution now requires genuinely new eligible Harbor traces, not more
proposal mining from this cohort.

## Validation

- Saturation `--dry-run`: pass.
- Saturation `--doctor`: pass.
- Saturation analyze-only: pass.
- Bounded-consult saturation `--dry-run`, `--doctor`, and analyze-only: pass.
- Bounded-consult accepted and rejected patches: 0 / 0.
- Unique trials normalized: 24.
- Unique task checksums normalized: 24.
- Baseline and candidate tree digests equal: pass.
- Baseline-to-candidate diff empty: pass.
- Both canonical datasets and all eight registered family pairs: pass.
- Tika/MALLET focused tests: 50 passed.
- Repository suite: 701 passed.
- Application coverage: 90.9%.

The cumulative round-3 candidate remains staged and unranked. This saturation
run neither replaces it nor authorizes promotion.
