# Independent semantic gates — current quality interpretation

All rows used Pi with GPT-5.6 Luna. Earlier rows retain their original blind
review; the v27 semantic column uses the superseding two-orientation R2 audit.
Cohorts are digest-locked and disjoint, so deltas are valid within a row but
raw values must not be compared across rows as if they were paired
observations.

| Candidate | Pi | Cohort | Cases | Mean reward, baseline to candidate | Mean tokens, baseline to candidate | Token delta | Candidate evidence-valid cases | Current semantic regressions | Gate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Initial exact structural chunking | 0.73.1 | q019-q024 development | 6 | 0.898 to 0.600 | 414,029.3 to 349,756.7 | -15.52% | 4/6 | 4/6 | Reject; independent cohorts remained sealed |
| Structured multiline terminal composer v11 | 0.84.2 | q041-q046 independent validation | 6 | 0.294 to 0.677 | 705,460.8 to 63,660.2 | -90.98% | 5/6 | 4/6 | Reject |
| Compact terminal, inflection-tolerant distinctive-facet composer v27 | 0.84.2 | q047-q052 independent validation | 6 | 0.163 to 0.926 | 447,704.0 to 79,224.7 | -82.30% | 6/6 | 3/6 | Reject; do not promote |

The final v27 validation improved mechanical reward by 0.763, reduced mean
agent latency from 141,173.7 ms to 95,991.3 ms (-32.01%), and reduced cost
from $0.20052016 to $0.06656484 (-66.80%). These are valid efficiency and
mechanical-contract results, not semantic-quality scores.

The solution-agnostic R2 audit re-adjudicated the same completed answers twice
with order reversal and hid answer evidence, retrieval traces, strategies,
paths, hashes, locators, rewards, and token usage. It found three regressions,
two improvements, and one mixed case; mean required-point coverage changed
from 77.08% to 75.00%. The zero-regression gate therefore remains rejected.
The earlier evidence-relative 2/6 review is preserved byte-for-byte in
`historical-independent-gates-pre-quality-audit.table.md` but is superseded for
quality claims. No holdout was declared or run.
