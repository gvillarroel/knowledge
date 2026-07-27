# Tantivy Consultation Trace-Distillation Result

## Outcome

Do not promote the evolved Tantivy consultant. Candidate S passed all four
development trials, but the sealed two-question holdout selected
`keep-baseline` with `promoted: false`. The checked-in standalone
`consult-semantic-okf-tantivy` skill therefore remains unchanged and outside
the canonical eight-family registry.

This is a strict promotion decision, not a claim that the current skill is
globally better than S. The holdout compared S with experimental candidate R;
neither side qualified on the two hidden questions.

## Evaluation boundary

- Dataset: `graphrag-papers-40`, canonical processed classical snapshot.
- Mode: `consult-only`; no raw sources or build skill were mounted.
- Runtime: Harbor 0.18.0, Pi 0.81.1, and
  `openai-codex/gpt-5.6-luna`.
- Independence: one attempt per task, no retries, four development questions,
  and two disjoint holdout questions.
- Evolution record: 15 versioned proposal/configuration iterations from E
  through S. Raw outputs remain append-only outside the tracked repository.

## Development gate

Candidate S, digest
`sha256:745be487dc3b6e75a7fa2c28a1f786ffea0366c77853dd51070f2d0fd7155634`,
passed 4/4 evaluable trials with no errors. Every trial satisfied both the
exact-evidence and mechanical-qualification gates.

| Question | Reward | Evidence gate | Mechanical gate |
| --- | ---: | ---: | ---: |
| q001 | 0.739016 | 1 | 1 |
| q013 | 0.807703 | 1 | 1 |
| q031 | 0.146928 | 1 | 1 |
| q039 | 0.400000 | 1 | 1 |

S preserved R's role-driven retrieval and changed the terminal handoff: it
allowed one bounded repair up to 1,600 semantic-text characters, retained
1,200 as the drafting target, emitted zero-indent line-anchored JSON, and
forbade manual evidence reconstruction after finalizer failure.

## Holdout gate

The holdout was evaluable and used identical zero-retry policies for R and S.
Both mean rewards were 0.0, and neither candidate qualified because the
mechanical gate failed on q010 and q029. S additionally lost the exact-evidence
gate on q029.

| Question | R evidence / mechanical | S evidence / mechanical | Reward delta |
| --- | ---: | ---: | ---: |
| q010 | 1 / 0 | 1 / 0 | 0.0 |
| q029 | 1 / 0 | 0 / 0 | 0.0 |

The gate consequently returned `keep-baseline`. Because the comparison
baseline was itself an unpromoted experimental variant, no evolved variant is
copied into the live skill.

## Reproducibility record

The machine-readable companion report records candidate identity, exact trial
evidence IDs, qualification values, cohort membership, and the promotion
decision. Versioned proposal and schema-2 driver files remain beside this
report. Credentials and host-specific raw result paths are deliberately
excluded.
