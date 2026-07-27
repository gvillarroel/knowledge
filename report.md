# Harbor Population Search

- Generation: 0
- Baseline: baseline
- Logical skill: consult-semantic-okf-tantivy
- Selected winner: identity-natural
- Minimum development pass rate: 100.0%
- Selection evidence: native Harbor development jobs only

| Rank | Candidate | Qualified | Winner eligible | Provenance | Fitness | Mean reward | Pass rate | Errors |
| ---: | --- | :---: | :---: | --- | ---: | ---: | ---: | ---: |
| 1 | identity-natural | yes | yes | verified | 0.851161 | 0.851161 | 100.0% | 0 |
| 2 | identity-cap | yes | yes | verified | 0.806505 | 0.806505 | 100.0% | 0 |
| 3 | natural-query | yes | yes | verified | 0.614243 | 0.614243 | 100.0% | 0 |
| 4 | baseline | yes | yes | verified | 0.54831 | 0.54831 | 100.0% | 0 |

## Holdout

- Status: staged
- Next step: Create a disjoint native Harbor holdout job template. Evaluate the preserved baseline and selected winner, then rerun with --holdout-template and --holdout-job baseline=.../winner=... in --analyze-only mode, or supply --holdout-template during a live run.
