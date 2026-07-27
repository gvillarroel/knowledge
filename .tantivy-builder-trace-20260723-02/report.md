# Harbor Trace Distillation: tantivy-builder-trace-distillation-20260723

Mode: `live`
Decision: **keep-baseline**

## Discovery evidence

- Unique trials: 6
- Unique task checksums: 6
- Outcomes: `{"success": 6}`

## Consolidation

- Accepted patches: forward-four-01-runtime, forward-four-02-workflow-disclosure, forward-four-03-reference-disclosure
- Rejected patches: none
- Candidate: `/mnt/c/Users/villa/dev/knowledge/.tantivy-builder-trace-20260723-02/candidate/skills/build-semantic-okf-tantivy`
- Candidate digest: `sha256:0fccf4555edea1fadbe0530262030b15f183f6e696acd6e32dba17225b848a5d`

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
- Candidate mean reward: 0.832
- Mean gain: -0.021
- Candidate errors: 0
- Candidate qualified: yes
- Required rewards complete: yes

The source skill was not modified. Review every cited Harbor artifact and validate the candidate bundle before promotion.
