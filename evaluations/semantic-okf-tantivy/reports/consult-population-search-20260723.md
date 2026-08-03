# Tantivy Consultation Population Search

Date: 2026-07-23. Status: development selection only. Promotion: no.

## Attempt

The generation-zero scalar population compared four complete
`consult-semantic-okf-tantivy` candidates using native Harbor development jobs.
The preserved baseline remained in the population, the minimum development
pass rate was 100%, and selection used verified native reward evidence.

| Rank | Candidate | Mean reward | Pass rate | Development disposition |
| ---: | --- | ---: | ---: | --- |
| 1 | `identity-natural` | 0.851161 | 100% | Selected development winner |
| 2 | `identity-cap` | 0.806505 | 100% | Survivor |
| 3 | `natural-query` | 0.614243 | 100% | Not selected |
| 4 | `baseline` | 0.548310 | 100% | Preserved control |

The selected candidate improved the development mean by 0.302851 over the
baseline. All four candidates passed the declared evidence and mechanical
gates with no recorded trial error in this comparison.

## Decision boundary

No disjoint native Harbor holdout was executed. The run staged a future
baseline-versus-winner holdout but did not release it, so `identity-natural`
was not promoted and this result must not be read as a production decision.
Later Tantivy trace-distillation work used separate contracts and also retained
the live consultant after its own holdout and canonical gates.

The candidate copies, jobs, trial logs, verifier diagnostics, and search
receipts remain in the ignored append-only evaluation artifact tree. This
tracked report is the durable summary of what was attempted and why the
development winner did not become the live skill.
