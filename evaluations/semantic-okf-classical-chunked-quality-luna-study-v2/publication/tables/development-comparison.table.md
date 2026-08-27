# Canonical versus exact-chunk Classical consultation

Development-only paired comparison under `openai-codex/gpt-5.6-luna`, PI 0.73.1, high thinking, and one attempt per case.

## Decision

**Reject the exact-chunk candidate.** It reduced aggregate tokens, cost, and latency, but materially regressed reward, evidence validity, and semantic quality. The sealed independent cohorts were not released.

## Aggregate results

| Metric | Canonical | Exact chunk | Delta |
| --- | ---: | ---: | ---: |
| Mean reward | 0.898 | 0.600 | -0.299 (-33.24%) |
| Exact passes | 2/6 | 1/6 | -16.7 points |
| Total tokens | 2,484,176 | 2,098,540 | -385,636 (-15.52%) |
| Median tokens | 401,002 | 345,644 | -13.80% |
| Total cost | $4.5223 | $3.6017 | -20.36% |
| Mean agent latency | 166.8 s | 118.1 s | -29.20% |
| All evidence valid | 6/6 | 4/6 | -33.3 points |

## Independent Luna semantic review

Verdict: **reject**; 4/6 paired cases regressed on at least one required semantic dimension.

## Offline proxy versus live Luna

The deterministic QEC payload proxy predicted a 65.52% token reduction with 100% retrieval parity and a 100% guard pass rate. The live end-to-end Luna reduction was only 15.52% because the agent sometimes performed schema discovery and raw-ledger fallbacks.

## Paired cases

| Case | Reward (old → new) | Reward outcome | Semantic outcome | Tokens (old → new) | Token delta | Invalid new evidence rows |
| ---: | ---: | --- | --- | ---: | ---: | ---: |
| 1 | 1.000 → 1.000 | tied | non-regressed | 146,945 → 499,158 | +239.69% | 0 |
| 2 | 0.934 → 0.723 | regressed | regressed | 432,854 → 494,585 | +14.26% | 0 |
| 3 | 1.000 → 0.000 | regressed | non-regressed | 369,150 → 168,136 | -54.45% | 1 |
| 4 | 0.906 → 0.000 | regressed | regressed | 247,022 → 191,740 | -22.38% | 3 |
| 5 | 0.888 → 0.926 | improved | regressed | 565,630 → 548,218 | -3.08% | 0 |
| 6 | 0.663 → 0.950 | improved | regressed | 722,575 → 196,703 | -72.78% | 0 |

## Diagnosis

The chunk context contract did not directly emit the benchmark's exact evidence-row schema, so Luna translated fields or fell back to raw-ledger exploration.

- Two candidate cases received zero reward after invalid evidence rows failed the mechanical qualification gate.
- Four of six candidate cases used fewer total tokens, but two used more; one of those was the largest proportional increase.
- Trace inspection shows context calls followed by extra schema discovery and raw-ledger fallbacks, defeating the intended bounded path in some cases.

## Scope

Only the frozen canonical skill and the frozen exact-chunk successor are compared. Other strategies and failed variants are excluded. The result is a development rejection, so no claim is made from the sealed independent cohorts.
