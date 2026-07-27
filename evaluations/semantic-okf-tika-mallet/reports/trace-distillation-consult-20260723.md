# Tika/MALLET Consultation Trace-Distillation Candidate

- Date: `2026-07-23`
- Dataset: `graphrag-papers-40`
- Skill: `consult-semantic-okf-tika-mallet`
- Status: `candidate-staged-not-promoted`
- Ranking eligible: `false`
- Published skill modified: `false`

## Provenance

The frozen baseline reproduces the discovery TrialLock digest
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

Analyze-only did not read holdout results.

## Accepted discovery proposals

| Proposal | Evidence support | Candidate change |
|---|---:|---|
| `seal-answer-pack-evidence-acquisition` | 8 trials / 8 tasks | Make a successful `answer-pack` terminal for evidence acquisition and require a declared null response instead of direct bundle reads or follow-up searches. |
| `diversify-answer-pack-facet-queries` | 4 trials / 4 tasks | Map distinct requested facets to complementary, mechanism-specific queries instead of generic labels or near-synonyms. |

The context-budget proposal is supported by seven scored traces that performed
direct post-pack reads with 731,437 to 2,433,287 input tokens and by q028, which
terminated at the provider context limit. The query-formulation proposal is
supported by four scored traces that failed the mechanical gate with incomplete
required-document coverage.

Both proposals were accepted by the configured minimum of two unique trials and
two unique task checksums. The resulting exploratory candidate digest is
`sha256:6925181e953d42bb291fe59f8c117416678ae61f6c56946c7e609a79c919e4dd`.
Only `references/querying.md` differs from the frozen baseline.

## Promotion gate

The candidate is not promoted. The schema-2 distiller correctly rejects the
legacy discovery job because `lock.json.retry` lacks the required
`include_exceptions` field. Those results can support diagnosis and candidate
materialization, but they cannot satisfy the prospective development and
holdout protocol.

A replacement live preflight is also externally blocked. The provider returned
`usage_limit_reached` before any model tokens or agent tool calls and reported a
reset at `2026-07-29T17:08:54-04:00`.

After provider access is restored, promotion requires new append-only Harbor
0.18.0 jobs with zero built-in retries:

1. rerun the exact baseline discovery cells with complete schema-2 retry locks;
2. run the frozen candidate on the same development cells with new attempts;
3. run baseline and candidate on a disjoint untouched holdout; and
4. promote only if all required rewards pass, candidate errors are absent, mean
   gain is non-negative, and no holdout task regresses.

The builder and bounded-consult skills remain unchanged because no compatible
eligible discovery trace set supports mutations to their locked identities.

## Validation

- Harbor trace-distillation `--dry-run`: pass.
- Harbor trace-distillation `--doctor`: pass.
- Legacy analyze-only normalization and proposal consolidation: pass.
- Candidate Python syntax compilation without candidate bytecode writes: pass.
- Candidate runtime smoke: pass.
- Candidate inspection of the 319-document, 30-source snapshot: pass.
- Canonical dataset validation for both datasets and all eight registered
  strategy pairs: pass.
- Tika/MALLET focused test suite: 50 passed.
- Repository coverage gate: 90.9%, above the required 80% threshold.

The coverage command's repository-wide pytest invocation reported 696 passes
and one unrelated pre-existing Tantivy builder-evolution assertion failure:
the test expects two phase entries while the current generator returns ten.
No Tantivy file was changed as part of this candidate.

The candidate does not change the canonical ranking table because it has not
passed prospective development and sealed holdout evaluation.
