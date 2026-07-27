# Tantivy Query IDF Trace-Distillation Result

## Outcome

Retain the promoted `identity-natural` consultant. The IDF candidate passed all
six development tasks and improved the four-task holdout mean from 0.852793 to
0.883546, but holdout part 04 regressed by 0.001614. The non-compensating
no-task-regression gate therefore returned `keep-baseline`.

The checked consultation tree remains frozen at realizer digest
`sha256:8c3666ede3281b96a8630321d9c2fb91d015da96469003ecf22643e041b6f7e7`.

## Candidate

For syntax-free natural questions, the candidate preserved every term accepted
by the immutable unigram lexicon and boosted at most twelve terms with the
lowest persisted document frequency by 2.0. Explicit Tantivy query syntax
remained unchanged. Its sealed Harbor skill digest was
`sha256:3039bc2a856bd0f66fe17458a2b6bf8607dc20563c4ad2b16de5ac81a733c937`.

## Gates

| Cohort | Baseline mean | Candidate mean | Gain | Result |
| --- | ---: | ---: | ---: | --- |
| Development, 6 tasks | 0.851161 | 0.864072 | +0.012911 | Pass |
| Holdout, 4 tasks | 0.852793 | 0.883546 | +0.030753 | Keep baseline |

Every candidate task was evaluable, error-free, and satisfied the exact
evidence and mechanical qualification gates.

| Holdout task | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| part 01 | 0.813455 | 0.863751 | +0.050296 |
| part 02 | 0.817969 | 0.877458 | +0.059489 |
| part 03 | 0.825374 | 0.840214 | +0.014840 |
| part 04 | 0.954375 | 0.952761 | -0.001614 |

The positive mean cannot compensate for the part-04 regression. No candidate
file was copied into the live consultant, and the builder stage continues
against the previously accepted frozen query.
