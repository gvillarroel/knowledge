# Harbor Population Search

- Generation: 0
- Baseline: baseline
- Logical skill: build-semantic-okf-tantivy
- Selected winner: papers-forward-3
- Minimum development pass rate: 100.0%
- Selection evidence: native Harbor development jobs only

| Rank | Candidate | Qualified | Winner eligible | Provenance | Fitness | Mean reward | Pass rate | Errors |
| ---: | --- | :---: | :---: | --- | ---: | ---: | ---: | ---: |
| 1 | papers-forward-3 | yes | yes | verified | 0.86857 | 0.86857 | 100.0% | 0 |
| 2 | papers-centered-3 | yes | yes | verified | 0.868179 | 0.868179 | 100.0% | 0 |
| 3 | papers-overlap-forward | yes | yes | verified | 0.864621 | 0.864621 | 100.0% | 0 |
| 4 | papers-only | yes | yes | verified | 0.855319 | 0.855319 | 100.0% | 0 |
| 5 | baseline | yes | yes | verified | 0.851161 | 0.851161 | 100.0% | 0 |

## Holdout

- Status: staged
- Next step: Create a disjoint native Harbor holdout job template. Evaluate the preserved baseline and selected winner, then rerun with --holdout-template and --holdout-job baseline=.../winner=... in --analyze-only mode, or supply --holdout-template during a live run.
