# Classical Consultation Token-Efficiency Lessons

## Decision summary

No lower-token Classical consultation candidate is accepted or promoted. The
search proved that large token reductions are possible, but every candidate
that met the token target either lost semantic fidelity, failed another hard
gate, or did not produce an answer.

The canonical `consult-semantic-okf-classical` skill remains unchanged. The
durable learning is preserved here so a future study can begin from the best
observed hypotheses without treating a rejected bundle as production-ready.

## Comparison boundaries

Construction tokens and consultation tokens are different units and must not
be combined. This document concerns consultation only. Native consultation
tokens are provider-reported input plus output tokens; cache tokens are already
part of input and are not added again.

Only rows from the same frozen model, runtime, task cohort, and metric contract
are directly rankable. Percentages from different studies remain useful within
their original comparator, but they are not one global leaderboard.

The acceptance rule is conjunctive:

- more than 30% lower native tokens under the frozen comparator;
- zero forbidden errors, retries, tools, continuations, or compactions;
- every required mechanical metric preserved;
- no material regression in independent paired semantic review; and
- success on the predeclared development, validation, and holdout sequence.

Token savings never compensate for one failed quality gate.

## Best V30 results by token usage

V30 used one released development screening case with a 547,318-token frozen
canonical control. These rows are token-ranked, not acceptance-ranked.

| Token position | Candidate | Native tokens | Reduction | Mechanical result | Semantic result | Future reuse |
| ---: | --- | ---: | ---: | ---: | --- | --- |
| 1 | R17 exact minimum grounding | 124,151 | 77.316478% | 21/21 | Rejected: unsupported section attribution and Markdown in answer strings | Second priority; lowest-token useful answer |
| 2 | R16 runtime-compatible complete record | 124,344 | 77.281215% | 18/21 | Rejected: version, evidence, section, and reuse errors | Sixth priority; architecture baseline only |
| 3 | R20 exact acronym attribution | 124,455 | 77.260934% | 21/21 | Rejected: proposal-versus-reuse attribution and synthesized pair | Fourth priority; attribution ablation |
| 4 | R18 sectionless plain JSON | 125,299 | 77.106728% | 21/21 | Rejected: guessed CAMEL expansion and unsupported terminology | Fifth priority; terminology ablation |
| 5 | R21 exact pair and provenance | 125,419 | 77.084803% | 21/21 | Rejected: one decisive synthesized acronym pair after coordinate correction | First priority; closest semantic near miss |
| 6 | R23 literal acronym pair only | 126,008 | 76.977187% | 21/21 | Rejected: internal location narration and unsupported method grouping | Third priority; literal-pair stress case |
| 7 | Frozen canonical control | 547,318 | baseline | 21/21 | Control | Retain until a full candidate qualifies |

All six answer-generating candidates passed the strict token screen. Five
passed every mechanical metric. None passed independent semantic
non-regression, so V30 selected no winner and never opened its replicate,
validation, holdout, or promotion stages.

## V30 alternatives without usable token results

| Candidate | What happened | Reuse decision |
| --- | --- | --- |
| R15 dynamic complete record | Sealed and provider-free qualified, but the canonical-first live preflight exposed a runtime-digest incompatibility before provider use | Superseded by R16; do not retry as-is |
| R19 exact supported terminology | Independent design review found that broad exact-copy rules could suppress harmless normalization or reproduce OCR artifacts | Preserve as a rejected design boundary |
| R22 literal-pair claim-local entailment | Independent review found completeness risk and an incorrect evidence-coordinate premise | Preserve as a rejected design boundary |
| R24 direct content-location guard | The sole authorized live run ended after the user message and before an assistant response | Diagnose the live boundary, not token quality |
| R25 direct claim separation | Provider-free replay and launch checks passed, but the sole live run reproduced R24's pre-answer failure | Diagnose the live boundary; no retry in V30 |

Missing-response verifier zeroes are placeholders, not quality or token
measurements. R24 and R25 cannot be ranked against answer-generating rows.

## Earlier alternatives and the durable lesson from each

| Lineage | Strongest measured result | Why it was not accepted | Durable lesson |
| --- | --- | --- | --- |
| Compact navigation v1-v3 | Up to 69.79% lower mean tokens | Seven to twenty-two quality regressions; v3 also errored | Bounded reads reduce context, but retrieval and evidence coverage must remain exact |
| V34 original development and holdout | Development mean -20.73%; untouched holdout mean -8.96% with semantic parity | Failed the frozen reduction and five-of-six consistency gates | This is the strongest quality-preserving control, but it does not meet the token target |
| Exact V34 direct canonical revalidation | 79,744 versus 6,015,810 total tokens, a 98.674426% reduction, with all numeric metrics at 1.0 | Independent review found semantic regressions in four of six cases | Automatic metric parity is insufficient; semantic review is mandatory |
| Exact V20, exact V21, and preferred-margin v2 | 97.8278% to 98.3487% lower tokens against the matched canonical control | Numeric and semantic regressions | Extreme compression remains a hypothesis source, not a production shortcut |
| V46 repeated small-window `rg`/`sed` navigation | Mean tokens increased 7.30%; median increased 82.39% | Twenty metrics regressed | Repeated narrow reads can cost more than a well-selected larger payload |
| V65 R6 lossless opaque blocks | 45.9967% more tokens than its immediate experimental parent | The second completion dominated output cost | Smaller source bytes do not guarantee fewer provider tokens |
| V29 R2-R5 early termination | Very low or null visible usage | Failed protocol or no answer | Never count incomplete execution as useful-answer efficiency |
| V29 R13 one-shot runtime | Provider-free gates and audits passed | The sole live smoke produced no answer and null usage | Offline lifecycle proofs do not establish live terminal reliability |
| V30 complete-record one-shot family | 76.977187% to 77.316478% lower tokens on the screen | Every answer failed semantic review | The architecture is efficient enough; the remaining problem is relation-preserving synthesis |

## What to try next

The next study should not resume V30 or mutate against its sealed validation.
It should register a new append-only study with fresh validation before any new
candidate is implemented.

Use this order:

1. Qualify a live one-request adapter that produces an observable terminal
   assistant response without retries or continuations. R24 and R25 show that
   provider-free replay alone is insufficient.
2. Use R21 as the semantic parent concept and R17 as the token comparator.
   Preserve exact source relations, acronym surface forms, proposal-versus-reuse
   roles, and complete evidence identities in a deterministic claim compiler.
3. Keep answer claims separate from internal source locations and retrieval
   narration. R23 demonstrates that literal terminology can still create an
   unsupported relationship.
4. Avoid universal exact-copy or omission rules. R19 and R22 show that these
   policies can trade one hallucination for OCR leakage or missing relevant
   content.
5. Evaluate at least two distinct development tasks before generalizing an
   instruction. The V30 token ranking is based on one screening case and does
   not establish a multi-query average.
6. Require per-case and aggregate token savings, 21/21 mechanical parity, and
   blinded semantic non-regression before freezing one candidate.
7. Release validation only for that frozen candidate. A failed validation
   starts a new study; it is not mutation input. Holdout remains a separate
   final gate.

The most promising new treatment is therefore not “read smaller files” by
itself. It is a relation-preserving, source-grounded compiler over a bounded
complete-record payload, combined with a live-boundary-stable one-request
adapter. Repeated `sed` windows should remain a negative control rather than
the default navigation strategy.

## Local negative-evidence archive

The rejected V30 bundles, decisive audits, and metrics remain local and
ignored by Git. The consolidated pointer archive is:

`evaluations/semantic-okf-datasets/processed/classical-token-efficiency-failed-options-v30/`

It contains:

- `options.json`: candidate paths, candidate-tree and manifest SHA-256 values,
  decisive evidence paths, dispositions, and future reuse order;
- `metrics.csv`: the compact R15-R25 comparison; and
- `README.md`: archive semantics and next-study guidance.

The exact bundles remain under the ignored V30 `private/candidates/` tree. The
archive points to them rather than duplicating them, so digest identity remains
unambiguous.

## Durable evidence

- The complete attempt ledger is
  `evaluations/semantic-okf-datasets/reports/20260802-classical-token-optimization-attempts.md`.
- The safe V30 aggregate table is
  `evaluations/semantic-okf-classical-token-efficiency-study-v30/publication/tables/v30-development-token-screen.table.md`.
- The V30 publication index binds ledger head
  `992438749fc00ed918162d0f92f93a111011acc37f34455c326599b49ef0505e`,
  298 events, one reviewed aggregate table, and confirms that validation and
  holdout were never released.

This documentation records learning only. It does not install a candidate,
modify the canonical skill, publish raw Harbor artifacts, or make a promotion
claim.
