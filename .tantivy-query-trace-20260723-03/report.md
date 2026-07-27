# Harbor Trace Distillation: tantivy-query-trace-distillation-20260723

Mode: `live`
Decision: **keep-baseline**

## Discovery evidence

- Unique trials: 6
- Unique task checksums: 6
- Outcomes: `{"success": 6}`

## Consolidation

- Accepted patches: idf-01-snapshot-frequency-map, idf-02-load-document-frequency, idf-03-boost-rare-natural-terms, idf-04-version-engine, idf-05-disclose-normalization
- Rejected patches: none
- Candidate: `/mnt/c/Users/villa/dev/knowledge/.tantivy-query-trace-20260723-03/candidate/skills/consult-semantic-okf-tantivy`
- Candidate digest: `sha256:3039bc2a856bd0f66fe17458a2b6bf8607dc20563c4ad2b16de5ac81a733c937`

## Candidate development gate

- Decision: **pass**
- Fairness basis: `trial-lock-and-result`
- Unique trials: 6
- Unique task checksums: 6
- Candidate pass rate: 100.0%
- Minimum pass rate: 100.0%
- Candidate qualified: yes
- Blockers: none

## Holdout gate

- Fairness basis: `trial-lock-and-result`
- Baseline mean reward: 0.853
- Candidate mean reward: 0.884
- Mean gain: +0.031
- Candidate errors: 0
- Candidate qualified: yes
- Required rewards complete: yes

The source skill was not modified. Review every cited Harbor artifact and validate the candidate bundle before promotion.
