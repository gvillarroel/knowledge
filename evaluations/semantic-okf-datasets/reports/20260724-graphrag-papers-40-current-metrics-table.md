# GraphRAG 40-question current-metrics evaluation table

## Interpretation boundary

This is an artifact-only recalculation of immutable Harbor traces; **no new model calls were made**. Every raw trial discovered across the declared append-only result roots was rescored with the current dataset policy and diagnostics schema 3.0. The scorer used each trial's native ledger and crosswalk so exact evidence identities remain valid across family-specific source representations.

The reward is a mechanical contract-and-focus diagnostic, not a semantic score. Semantic verdicts remain the documented manual adjudications. The forty curated references are shown only as a calibration surface and are not counted as live trials.

## Recalculation summary

| Measure | Value |
|---|---:|
| Dataset questions | 40 |
| Raw Harbor trials rescored | 516 / 516 |
| Primary / additional result-root trials | 180 / 336 |
| Complete-parent / partial-parent trial artifacts | 503 / 13 |
| Incomplete parent jobs represented | 4 |
| Semantically reviewed raw responses | 175 |
| Primary / recovered historical reviewed responses | 143 / 32 |
| Emitted raw responses awaiting semantic review | 34 |
| Legacy reviewed responses without raw bodies | 0 |
| Total individually reviewable responses | 175 |
| Current mechanical qualification passes | 115 / 516 |
| Questions with empirical response coverage | 29 / 40 |
| Reference calibrations passing current contract | 40 / 40 |
| Comparable rewards increased / decreased / unchanged | 46 / 3 / 461 |
| Mean original / current reward (comparable trials) | 0.109322 / 0.160423 |

Trace outcomes: `agent-interrupted`=21, `answer-emitted`=209, `missing-response`=1, `missing-trace`=7, `output-limit`=4, `provider-context-limit`=16, `provider-error`=1, `provider-quota`=257.

Empirical full-dataset claim eligible: `false`. Missing empirical questions: `q028`, `q031`, `q032`, `q033`, `q034`, `q035`, `q036`, `q037`, `q038`, `q039`, `q040`.

## Strategy summary

Means and qualification rates use emitted answers only, so provider, agent, and missing-response outcomes remain separate.

| Strategy | Trials | Q | Emitted | No answer | Semantically reviewed | Contract | Qualified | Rate | Mean utility | Mean reward | Semantic P/Pt/F |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `adaptive` | 41 | 40 | 5 | 36 | 5 | 3/5 | 2/5 | 40.0% | 0.313 | 0.172 | P0/Pt5/F0 |
| `classical` | 40 | 40 | 6 | 34 | 6 | 6/6 | 1/6 | 16.7% | 0.568 | 0.124 | P0/Pt6/F0 |
| `embeddings` | 40 | 40 | 4 | 36 | 4 | 3/4 | 1/4 | 25.0% | 0.665 | 0.210 | P0/Pt4/F0 |
| `ensemble` | 40 | 40 | 0 | 40 | 0 | 0/0 | 0/0 | — | — | — | P0/Pt0/F0 |
| `entity-graph` | 40 | 40 | 4 | 36 | 4 | 1/4 | 0/4 | 0.0% | 0.145 | 0.000 | P0/Pt3/F1 |
| `graphify` | 40 | 40 | 0 | 40 | 0 | 0/0 | 0/0 | — | — | — | P0/Pt0/F0 |
| `legacy` | 40 | 40 | 7 | 33 | 7 | 0/7 | 0/7 | 0.0% | 0.000 | 0.000 | P0/Pt7/F0 |
| `tika-mallet-bounded-v4` | 1 | 1 | 0 | 1 | 0 | 0/0 | 0/0 | — | — | — | P0/Pt0/F0 |
| `tika-mallet-canonical-text` | 4 | 1 | 2 | 2 | 2 | 2/2 | 1/2 | 50.0% | 0.662 | 0.359 | P0/Pt2/F0 |
| `tika-mallet-canonical-text-v2` | 6 | 6 | 5 | 1 | 5 | 5/5 | 5/5 | 100.0% | 0.604 | 0.604 | P0/Pt5/F0 |
| `tika-mallet-canonical-text-v3` | 30 | 30 | 29 | 1 | 29 | 27/29 | 17/29 | 58.6% | 0.655 | 0.402 | P3/Pt26/F0 |
| `tika-mallet-tantivy-canonical-text` | 154 | 15 | 141 | 13 | 107 | 115/141 | 88/141 | 62.4% | 0.566 | 0.454 | P0/Pt104/F3 |
| `turso` | 40 | 40 | 6 | 34 | 6 | 0/6 | 0/6 | 0.0% | 0.000 | 0.000 | P0/Pt6/F0 |

## Every question under the current metrics

| Q | Cohort | Trials | Reviewed raw+legacy | Semantic (P/Pt/F) | Qualified | Latest trial | Latest reviewed | Valid/focus docs | Gate | Utility | Reward | Empirical |
|---|---|---:|---:|---|---:|---|---|---:|---:|---:|---:|---|
| q001 | discovery | 19 | 3+0 | P0/Pt3/F0 | 2/19 | provider-error | answer-emitted; partial | 9/9 | 1 | 0.778 | 0.778 | covered |
| q002 | discovery | 54 | 35+0 | P0/Pt34/F1 | 28/54 | answer-emitted | answer-emitted; partial | 8/6 | 1 | 0.819 | 0.819 | covered |
| q003 | discovery | 51 | 37+0 | P0/Pt37/F0 | 33/51 | answer-emitted | answer-emitted; partial | 8/7 | 1 | 0.796 | 0.796 | covered |
| q004 | discovery | 50 | 31+0 | P0/Pt30/F1 | 24/50 | answer-emitted | answer-emitted; partial | 9/7 | 1 | 0.734 | 0.734 | covered |
| q005 | holdout | 16 | 10+0 | P0/Pt10/F0 | 5/16 | answer-emitted | answer-emitted; partial | 6/2 | 1 | 0.556 | 0.556 | covered |
| q006 | discovery | 10 | 1+0 | P0/Pt1/F0 | 0/10 | missing-trace | answer-emitted; partial | 8/4 | 0 | 0.494 | 0.000 | covered |
| q007 | discovery | 10 | 2+0 | P0/Pt2/F0 | 0/10 | missing-trace | answer-emitted; partial | 5/3 | 0 | 0.710 | 0.000 | covered |
| q008 | discovery | 10 | 1+0 | P1/Pt0/F0 | 0/10 | missing-trace | answer-emitted; pass | 3/1 | 0 | 0.399 | 0.000 | covered |
| q009 | discovery | 10 | 1+0 | P0/Pt1/F0 | 1/10 | missing-trace | answer-emitted; partial | 6/5 | 1 | 0.884 | 0.884 | covered |
| q010 | holdout | 12 | 9+0 | P0/Pt9/F0 | 6/12 | answer-emitted | answer-emitted; partial | 8/4 | 1 | 0.616 | 0.616 | covered |
| q011 | discovery | 10 | 1+0 | P0/Pt1/F0 | 0/10 | missing-trace | answer-emitted; partial | 2/1 | 0 | 0.407 | 0.000 | covered |
| q012 | discovery | 9 | 1+0 | P0/Pt1/F0 | 0/9 | answer-emitted | answer-emitted; partial | 5/4 | 0 | 0.653 | 0.000 | covered |
| q013 | discovery | 9 | 1+0 | P0/Pt1/F0 | 1/9 | answer-emitted | answer-emitted; partial | 9/7 | 1 | 0.899 | 0.899 | covered |
| q014 | discovery | 9 | 1+0 | P0/Pt1/F0 | 0/9 | answer-emitted | answer-emitted; partial | 7/3 | 0 | 0.484 | 0.000 | covered |
| q015 | holdout | 12 | 8+0 | P0/Pt8/F0 | 3/12 | answer-emitted | answer-emitted; partial | 7/5 | 1 | 0.800 | 0.800 | covered |
| q016 | discovery | 9 | 1+0 | P0/Pt1/F0 | 1/9 | answer-emitted | answer-emitted; partial | 7/6 | 1 | 0.757 | 0.757 | covered |
| q017 | discovery | 9 | 1+0 | P0/Pt1/F0 | 0/9 | answer-emitted | answer-emitted; partial | 6/3 | 0 | 0.568 | 0.000 | covered |
| q018 | discovery | 9 | 1+0 | P0/Pt1/F0 | 1/9 | answer-emitted | answer-emitted; partial | 6/5 | 1 | 0.717 | 0.717 | covered |
| q019 | discovery | 9 | 1+0 | P0/Pt1/F0 | 1/9 | answer-emitted | answer-emitted; partial | 8/2 | 1 | 0.480 | 0.480 | covered |
| q020 | holdout | 12 | 7+0 | P0/Pt6/F1 | 3/12 | answer-emitted | answer-emitted; fail | 0/0 | 0 | 0.000 | 0.000 | covered |
| q021 | discovery | 9 | 1+0 | P1/Pt0/F0 | 0/9 | answer-emitted | answer-emitted; pass | 8/4 | 0 | 0.678 | 0.000 | covered |
| q022 | discovery | 9 | 1+0 | P0/Pt1/F0 | 1/9 | answer-emitted | answer-emitted; partial | 6/5 | 1 | 0.884 | 0.884 | covered |
| q023 | discovery | 9 | 1+0 | P1/Pt0/F0 | 0/9 | answer-emitted | answer-emitted; pass | 8/8 | 0 | 0.739 | 0.000 | covered |
| q024 | discovery | 9 | 1+0 | P0/Pt1/F0 | 1/9 | answer-emitted | answer-emitted; partial | 8/7 | 1 | 0.684 | 0.684 | covered |
| q025 | holdout | 12 | 9+0 | P0/Pt9/F0 | 2/12 | answer-emitted | answer-emitted; partial | 2/1 | 0 | 0.447 | 0.000 | covered |
| q026 | discovery | 9 | 1+0 | P0/Pt1/F0 | 1/9 | answer-emitted | answer-emitted; partial | 6/5 | 1 | 0.722 | 0.722 | covered |
| q027 | discovery | 9 | 1+0 | P0/Pt1/F0 | 0/9 | answer-emitted | answer-emitted; partial | 4/3 | 0 | 0.581 | 0.000 | covered |
| q028 | discovery | 10 | 0+0 | P0/Pt0/F0 | 0/10 | provider-quota | — | — | — | — | — | missing |
| q029 | holdout | 12 | 6+0 | P0/Pt5/F1 | 1/12 | answer-emitted | answer-emitted; partial | 7/5 | 0 | 0.683 | 0.000 | covered |
| q030 | discovery | 9 | 1+0 | P0/Pt1/F0 | 0/9 | answer-emitted | answer-emitted; partial | 9/9 | 0 | 0.778 | 0.000 | covered |
| q031 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q032 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q033 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q034 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q035 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q036 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q037 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q038 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q039 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |
| q040 | hard | 8 | 0+0 | P0/Pt0/F0 | 0/8 | provider-quota | — | — | — | — | — | missing |

## Every raw Harbor trial rescored

| Trial | Q | Outcome | Reviewed | Contract | Valid/focus docs | Gate | Utility | Original reward | Current reward | Delta | Semantic |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `raw/20260723-tika-mallet-consult-holdout-live-02/q005__GpiFZ57` | q005 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-consult-holdout-q005-live-03/q005__2hVWTkC` | q005 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | — | 0.000 | — | not-reviewed |
| `raw/20260723-tika-mallet-consult-holdout-q005-live-04/q005__yh5yy9X` | q005 | answer-emitted | 1 | 1 | 3/2 | 0 | 0.606 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-consult-holdout-q005-live-05/q005__gHaYNSh` | q005 | answer-emitted | 1 | 1 | 4/3 | 1 | 0.719 | 0.000 | 0.719 | 0.719 | partial |
| `raw/20260723-tika-mallet-consult-holdout-q005-live-v2-01/q005__qFqD7Yj` | q005 | answer-emitted | 1 | 1 | 6/4 | 1 | 0.833 | 0.833 | 0.833 | 0.000 | partial |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q010__B9sqvVX` | q010 | answer-emitted | 1 | 1 | 6/4 | 1 | 0.523 | 0.000 | 0.523 | 0.523 | partial |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q015__U2FuVa3` | q015 | answer-emitted | 1 | 1 | 6/4 | 1 | 0.555 | 0.000 | 0.555 | 0.555 | partial |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q020__euRLrjj` | q020 | answer-emitted | 1 | 1 | 7/5 | 1 | 0.796 | 0.796 | 0.796 | 0.000 | partial |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q025__a9u8Ban` | q025 | answer-emitted | 1 | 1 | 7/2 | 1 | 0.316 | 0.000 | 0.316 | 0.316 | partial |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q029__cSsY3bV` | q029 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-github-copilot-preflight-01/q001__WnWg9ng` | q001 | missing-response | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-github-copilot-preflight-02/q001__JgbQyBS` | q001 | answer-emitted | 1 | 1 | 9/9 | 1 | 0.778 | 0.778 | 0.778 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-provider-preflight-01/q001__bYTqMpi` | q001 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q001__oqTNUSn` | q001 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q002__pN36ijn` | q002 | answer-emitted | 1 | 1 | 7/5 | 1 | 0.597 | 0.000 | 0.597 | 0.597 | partial |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q003__h524KYS` | q003 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.693 | 0.000 | 0.693 | 0.693 | partial |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q004__5xLXMe9` | q004 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q006__44JUAWu` | q006 | missing-trace | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q007__SLRogdp` | q007 | missing-trace | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q008__dH5XXYV` | q008 | missing-trace | 0 | 0 | 0/0 | 0 | 0.000 | — | 0.000 | — | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q009__Nb3n5Lj` | q009 | missing-trace | 0 | 0 | 0/0 | 0 | 0.000 | — | 0.000 | — | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q011__CF32NXW` | q011 | missing-trace | 0 | 0 | 0/0 | 0 | 0.000 | — | 0.000 | — | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v2-provider-preflight-01/q002__L7cSr3G` | q002 | missing-trace | 0 | 0 | 0/0 | 0 | 0.000 | — | 0.000 | — | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v2-provider-preflight-01/q003__i8gdasu` | q003 | missing-trace | 0 | 0 | 0/0 | 0 | 0.000 | — | 0.000 | — | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-development-candidate-03/q001__79BWGwG` | q001 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-development-candidate-03/q002__JMUSrfq` | q002 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-development-candidate-03/q003__okYVTgk` | q003 | answer-emitted | 1 | 1 | 7/5 | 0 | 0.664 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v3-development-candidate-03/q004__QwJ6g6A` | q004 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-01/q001__YYpoepm` | q001 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-01/q002__ZNMuxpp` | q002 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-01/q003__XewPxDE` | q003 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-01/q004__kxejaqk` | q004 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-02/q001__TDBbQZe` | q001 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-02/q002__3PZeH7i` | q002 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-02/q003__8dsvXXU` | q003 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-discovery-baseline-02/q004__Q45D6wi` | q004 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-provider-preflight-01/q002__qzV52E5` | q002 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v3-provider-preflight-02/q002__Q6Fwi9p` | q002 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v4-development-candidate-01/q001__e9wuuew` | q001 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v4-development-candidate-01/q002__nETTsCt` | q002 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v4-development-candidate-01/q003__Umo8uCp` | q003 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v4-development-candidate-01/q004__KkmRLYC` | q004 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v5-development-candidate-01/q002__fQtYmeu` | q002 | answer-emitted | 1 | 1 | 8/5 | 1 | 0.732 | 0.000 | 0.732 | 0.732 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-development-candidate-01/q003__SrhQcZ8` | q003 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-development-candidate-01/q004__Kdp3rVK` | q004 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-01/q001__aofpfoA` | q001 | provider-error | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-01/q002__gzPBEmE` | q002 | answer-emitted | 1 | 1 | 8/4 | 0 | 0.644 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-01/q003__Tfnutc7` | q003 | answer-emitted | 1 | 1 | 7/5 | 0 | 0.677 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-01/q004__mXH7TvG` | q004 | answer-emitted | 1 | 1 | 7/6 | 1 | 0.584 | 0.000 | 0.584 | 0.584 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-02/q002__HyWuJCC` | q002 | answer-emitted | 1 | 1 | 6/4 | 1 | 0.645 | 0.000 | 0.645 | 0.645 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-02/q003__Z8i6Fx4` | q003 | answer-emitted | 1 | 1 | 5/4 | 0 | 0.629 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-02/q004__8fcXLe2` | q004 | answer-emitted | 1 | 1 | 4/3 | 0 | 0.528 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v5-provider-preflight-01/q002__QCX6gdT` | q002 | answer-emitted | 1 | 1 | 6/3 | 0 | 0.549 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v6-development-candidate-01/q002__QuhuA2G` | q002 | answer-emitted | 1 | 1 | 8/4 | 1 | 0.480 | 0.000 | 0.480 | 0.480 | partial |
| `raw/20260723-tika-mallet-tantivy-v6-development-candidate-01/q003__Rn3rLd8` | q003 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.693 | 0.000 | 0.693 | 0.693 | partial |
| `raw/20260723-tika-mallet-tantivy-v6-development-candidate-01/q004__QtDuMkU` | q004 | answer-emitted | 1 | 1 | 6/5 | 0 | 0.668 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v7-development-candidate-01/q002__GwCByW4` | q002 | answer-emitted | 1 | 1 | 6/3 | 1 | 0.568 | 0.000 | 0.568 | 0.568 | partial |
| `raw/20260723-tika-mallet-tantivy-v7-development-candidate-01/q003__mjivyt7` | q003 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.734 | 0.734 | 0.734 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v7-development-candidate-01/q004__YfPyWdG` | q004 | answer-emitted | 1 | 1 | 9/8 | 1 | 0.813 | 0.813 | 0.813 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v8-development-candidate-01/q002__azcgJwZ` | q002 | answer-emitted | 1 | 1 | 7/6 | 0 | 0.819 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v8-development-candidate-01/q003__X4zgxS3` | q003 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.693 | 0.000 | 0.693 | 0.693 | partial |
| `raw/20260723-tika-mallet-tantivy-v8-development-candidate-01/q004__LQbhEdP` | q004 | answer-emitted | 1 | 1 | 12/9 | 1 | 0.860 | 0.860 | 0.860 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v9-development-candidate-01/q002__WEb4NaC` | q002 | answer-emitted | 1 | 1 | 5/3 | 0 | 0.583 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v9-development-candidate-01/q003__zCQcKFb` | q003 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.727 | 0.727 | 0.727 | 0.000 | partial |
| `raw/20260723-tika-mallet-tantivy-v9-development-candidate-01/q004__msRqjWq` | q004 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.761 | 0.761 | 0.761 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q001__PebPBhy` | q001 | answer-emitted | 1 | 1 | 9/9 | 1 | 0.778 | 0.778 | 0.778 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q002__r3B8JPb` | q002 | answer-emitted | 1 | 1 | 7/4 | 1 | 0.450 | 0.000 | 0.450 | 0.450 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q003__xzGPwP4` | q003 | answer-emitted | 1 | 1 | 7/5 | 1 | 0.661 | 0.000 | 0.661 | 0.661 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q004__sLi4Dqz` | q004 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.706 | 0.000 | 0.706 | 0.706 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q006__eakXQfk` | q006 | answer-emitted | 1 | 1 | 8/4 | 0 | 0.494 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q007__GwiHvjF` | q007 | answer-emitted | 1 | 1 | 5/3 | 0 | 0.710 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q008__ppJGeAn` | q008 | answer-emitted | 1 | 0 | 3/1 | 0 | 0.399 | 0.000 | 0.000 | 0.000 | pass |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q009__oBjsXHo` | q009 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.884 | 0.884 | 0.884 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q011__QtwkC4K` | q011 | answer-emitted | 1 | 1 | 2/1 | 0 | 0.407 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q012__V9qSEaF` | q012 | answer-emitted | 1 | 1 | 5/4 | 0 | 0.653 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q013__aoc5bq7` | q013 | answer-emitted | 1 | 1 | 9/7 | 1 | 0.899 | 0.899 | 0.899 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q014__Rfx8WJ7` | q014 | answer-emitted | 1 | 1 | 7/3 | 0 | 0.484 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q016__nMhf2M4` | q016 | answer-emitted | 1 | 1 | 7/6 | 1 | 0.757 | 0.000 | 0.757 | 0.757 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q017__RnYZcfx` | q017 | answer-emitted | 1 | 1 | 6/3 | 0 | 0.568 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q018__WfCPXPk` | q018 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.717 | 0.000 | 0.717 | 0.717 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q019__aLN785h` | q019 | answer-emitted | 1 | 1 | 8/2 | 1 | 0.480 | 0.000 | 0.480 | 0.480 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q021__4XPFLhs` | q021 | answer-emitted | 1 | 0 | 8/4 | 0 | 0.678 | 0.000 | 0.000 | 0.000 | pass |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q022__kXxqnME` | q022 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.884 | 0.884 | 0.884 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q023__UYWESow` | q023 | answer-emitted | 1 | 1 | 8/8 | 0 | 0.739 | 0.000 | 0.000 | 0.000 | pass |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q024__B3cFMLe` | q024 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.684 | 0.000 | 0.684 | 0.684 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q026__MYr6QnG` | q026 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.722 | 0.000 | 0.722 | 0.722 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q027__Csou2Jh` | q027 | answer-emitted | 1 | 1 | 4/3 | 0 | 0.581 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q028__2gCTcoD` | q028 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q030__HdWwAVo` | q030 | answer-emitted | 1 | 1 | 9/9 | 0 | 0.778 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-holdout-q029-live-01/q029__2rqaPyg` | q029 | answer-emitted | 1 | 1 | 6/3 | 1 | 0.542 | 0.000 | 0.542 | 0.542 | partial |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q005__gNNuojW` | q005 | answer-emitted | 1 | 1 | 5/3 | 1 | 0.705 | 0.000 | 0.705 | 0.705 | partial |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q010__QvwywR6` | q010 | answer-emitted | 1 | 1 | 7/6 | 0 | 0.842 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q015__8RAbSdf` | q015 | answer-emitted | 1 | 1 | 8/4 | 1 | 0.480 | 0.000 | 0.480 | 0.480 | partial |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q020__emcyE9S` | q020 | answer-emitted | 1 | 1 | 9/5 | 1 | 0.770 | 0.770 | 0.770 | 0.000 | partial |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q025__AhWGmHo` | q025 | answer-emitted | 1 | 1 | 5/2 | 1 | 0.541 | 0.000 | 0.541 | 0.541 | partial |
| `raw/20260723-tika-mallet-v4-discovery-q028-live-01/q028__KJL2eeP` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260724-tika-mallet-tantivy-v10-development-candidate-01/q002__TKj95xH` | q002 | answer-emitted | 1 | 1 | 8/5 | 1 | 0.708 | 0.000 | 0.708 | 0.708 | partial |
| `raw/20260724-tika-mallet-tantivy-v10-development-candidate-01/q003__keYyjcF` | q003 | answer-emitted | 1 | 1 | 7/6 | 1 | 0.746 | 0.746 | 0.746 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v10-development-candidate-01/q004__rM4rNM9` | q004 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.778 | 0.778 | 0.778 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v11-development-candidate-01/q002__gLddyCJ` | q002 | answer-emitted | 1 | 1 | 8/4 | 1 | 0.494 | 0.000 | 0.494 | 0.494 | partial |
| `raw/20260724-tika-mallet-tantivy-v11-development-candidate-01/q003__Tgpiqvv` | q003 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.718 | 0.718 | 0.718 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v11-development-candidate-01/q004__eCTkQHj` | q004 | answer-emitted | 1 | 1 | 11/8 | 1 | 0.799 | 0.799 | 0.799 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v12-development-candidate-01/q002__Mm7pSUc` | q002 | answer-emitted | 1 | 1 | 7/6 | 1 | 0.840 | 0.840 | 0.840 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v12-development-candidate-01/q003__rj3GwQB` | q003 | answer-emitted | 1 | 0 | 8/5 | 0 | 0.663 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v12-development-candidate-01/q004__RqzMc4Q` | q004 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.761 | 0.761 | 0.761 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v13-development-candidate-01/q002__JKaTWqs` | q002 | answer-emitted | 1 | 1 | 8/5 | 1 | 0.714 | 0.000 | 0.714 | 0.714 | partial |
| `raw/20260724-tika-mallet-tantivy-v13-development-candidate-01/q003__9RxyPk8` | q003 | answer-emitted | 1 | 1 | 9/7 | 1 | 0.798 | 0.798 | 0.798 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v13-development-candidate-01/q004__DpueGfL` | q004 | answer-emitted | 1 | 1 | 14/11 | 1 | 0.943 | 0.943 | 0.943 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v14-development-candidate-01/q002__UN7N8Bi` | q002 | answer-emitted | 1 | 1 | 8/2 | 1 | 0.302 | 0.000 | 0.302 | 0.302 | partial |
| `raw/20260724-tika-mallet-tantivy-v14-development-candidate-01/q003__we7toSx` | q003 | answer-emitted | 1 | 1 | 10/7 | 1 | 0.783 | 0.783 | 0.783 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v14-development-candidate-01/q004__x6X5JBs` | q004 | answer-emitted | 1 | 1 | 6/5 | 0 | 0.650 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v15-development-candidate-01/q002__hnXKesc` | q002 | answer-emitted | 1 | 1 | 7/3 | 1 | 0.405 | 0.000 | 0.405 | 0.405 | partial |
| `raw/20260724-tika-mallet-tantivy-v15-development-candidate-01/q003__JfnXg59` | q003 | answer-emitted | 1 | 1 | 10/8 | 1 | 0.852 | 0.852 | 0.852 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v15-development-candidate-01/q004__rwH2dRE` | q004 | answer-emitted | 1 | 1 | 7/7 | 1 | 0.799 | 0.799 | 0.799 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v16-development-candidate-01/q002__nbas6Bd` | q002 | answer-emitted | 1 | 1 | 10/6 | 1 | 0.788 | 0.788 | 0.788 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v16-development-candidate-01/q003__xpJap6u` | q003 | answer-emitted | 1 | 1 | 6/4 | 1 | 0.602 | 0.000 | 0.602 | 0.602 | partial |
| `raw/20260724-tika-mallet-tantivy-v16-development-candidate-01/q004__gtxRpNc` | q004 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.686 | 0.000 | 0.686 | 0.686 | partial |
| `raw/20260724-tika-mallet-tantivy-v17-development-candidate-01/q002__h8YAEjt` | q002 | answer-emitted | 1 | 1 | 6/1 | 1 | 0.345 | 0.000 | 0.345 | 0.345 | partial |
| `raw/20260724-tika-mallet-tantivy-v17-development-candidate-01/q003__JyVtjr6` | q003 | answer-emitted | 1 | 1 | 6/4 | 1 | 0.604 | 0.000 | 0.604 | 0.604 | partial |
| `raw/20260724-tika-mallet-tantivy-v17-development-candidate-01/q004__uApz4Rs` | q004 | answer-emitted | 1 | 1 | 11/9 | 1 | 0.873 | 0.873 | 0.873 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v18-development-candidate-01/q002__X5fydxu` | q002 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.804 | 0.804 | 0.804 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v18-development-candidate-01/q003__Vo5c64Z` | q003 | answer-emitted | 1 | 1 | 7/3 | 1 | 0.494 | 0.000 | 0.494 | 0.494 | partial |
| `raw/20260724-tika-mallet-tantivy-v18-development-candidate-01/q004__zqaiJof` | q004 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260724-tika-mallet-tantivy-v19-development-candidate-01/q002__dj28UPF` | q002 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.900 | 0.900 | 0.900 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v19-development-candidate-01/q003__RgjtZVL` | q003 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.594 | 0.594 | 0.594 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v19-development-candidate-01/q004__Z9Ahf2h` | q004 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.690 | 0.000 | 0.690 | 0.690 | partial |
| `raw/20260724-tika-mallet-tantivy-v20-development-candidate-01/q002__3295tXQ` | q002 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.905 | 0.905 | 0.905 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v20-development-candidate-01/q003__q2fkXaq` | q003 | answer-emitted | 1 | 0 | 6/6 | 0 | 0.778 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v20-development-candidate-01/q004__TzNJwC3` | q004 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260724-tika-mallet-tantivy-v21-development-candidate-01/q002__6YTzLsn` | q002 | answer-emitted | 1 | 0 | 6/5 | 0 | 0.747 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v21-development-candidate-01/q003__FV7g9vj` | q003 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.693 | 0.000 | 0.693 | 0.693 | partial |
| `raw/20260724-tika-mallet-tantivy-v21-development-candidate-01/q004__SzQxMYj` | q004 | answer-emitted | 1 | 1 | 15/11 | 1 | 0.958 | 0.958 | 0.958 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v22-development-candidate-02/q002__YCbnwcn` | q002 | answer-emitted | 1 | 1 | 8/5 | 1 | 0.713 | 0.000 | 0.713 | 0.713 | partial |
| `raw/20260724-tika-mallet-tantivy-v22-development-candidate-02/q003__G664wbW` | q003 | answer-emitted | 1 | 1 | 6/3 | 1 | 0.507 | 0.000 | 0.507 | 0.507 | partial |
| `raw/20260724-tika-mallet-tantivy-v22-development-candidate-02/q004__iwFuJDx` | q004 | answer-emitted | 1 | 1 | 13/9 | 1 | 0.850 | 0.850 | 0.850 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v23-development-candidate-02/q002__mw32b4Q` | q002 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.794 | 0.794 | 0.794 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v23-development-candidate-02/q003__Qikawyn` | q003 | answer-emitted | 1 | 1 | 7/6 | 1 | 0.737 | 0.737 | 0.737 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v23-development-candidate-02/q004__EvTDCLj` | q004 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v24-development-candidate-01/q002__FbbgA9C` | q002 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.822 | 0.822 | 0.822 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v24-development-candidate-01/q003__rtisM2b` | q003 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.552 | 0.000 | 0.552 | 0.552 | partial |
| `raw/20260724-tika-mallet-tantivy-v24-development-candidate-01/q004__h6RwqF8` | q004 | answer-emitted | 1 | 1 | 9/8 | 1 | 0.690 | 0.690 | 0.690 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v25-development-candidate-01/q002__cJZUyxk` | q002 | answer-emitted | 1 | 1 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | fail |
| `raw/20260724-tika-mallet-tantivy-v25-development-candidate-01/q003__bsotojk` | q003 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.812 | 0.812 | 0.812 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v25-development-candidate-01/q004__XD5acgs` | q004 | answer-emitted | 1 | 1 | 9/8 | 1 | 0.821 | 0.821 | 0.821 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v26-development-candidate-01/q002__2h9niyq` | q002 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.823 | 0.823 | 0.823 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v26-development-candidate-01/q003__76XqsQ6` | q003 | answer-emitted | 1 | 1 | 7/6 | 0 | 0.737 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v26-development-candidate-01/q004__g7NRfQE` | q004 | answer-emitted | 1 | 1 | 9/8 | 1 | 0.690 | 0.690 | 0.690 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v27-development-candidate-01/q002__k5ryCN9` | q002 | answer-emitted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/20260724-tika-mallet-tantivy-v27-development-candidate-01/q003__TXhYMMm` | q003 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.796 | 0.796 | 0.796 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v27-development-candidate-01/q004__KoD58YT` | q004 | answer-emitted | 1 | 1 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | fail |
| `raw/20260724-tika-mallet-tantivy-v28-clean-development-baseline-01/q002__C6GauaP` | q002 | answer-emitted | 1 | 1 | 7/2 | 0 | 0.305 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v28-clean-development-baseline-01/q003__gEFQnha` | q003 | answer-emitted | 1 | 1 | 10/8 | 1 | 0.861 | 0.861 | 0.861 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v28-clean-development-baseline-01/q004__oEPgEJ9` | q004 | answer-emitted | 1 | 1 | 11/7 | 0 | 0.720 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v32-clean-development-candidate-01/q002__LnJbSpS` | q002 | answer-emitted | 1 | 1 | 2/1 | 0 | 0.395 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v32-clean-development-candidate-01/q003__yd8DHpW` | q003 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.796 | 0.796 | 0.796 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v32-clean-development-candidate-01/q004__gjKY5Tr` | q004 | answer-emitted | 1 | 1 | 9/7 | 1 | 0.734 | 0.734 | 0.734 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v33-opaque-concept-path-development-candidate-01/q002__zgHt4Yd` | q002 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.813 | 0.813 | 0.813 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v33-opaque-concept-path-development-candidate-01/q003__DrZ85he` | q003 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.809 | 0.809 | 0.809 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v33-opaque-concept-path-development-candidate-01/q004__mfhGqUx` | q004 | answer-emitted | 1 | 1 | 7/6 | 0 | 0.707 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v34-minimum-target-development-candidate-01/q002__rr38ccB` | q002 | answer-emitted | 1 | 1 | 6/4 | 1 | 0.649 | 0.000 | 0.649 | 0.649 | partial |
| `raw/20260724-tika-mallet-tantivy-v34-minimum-target-development-candidate-01/q003__Qm3zAfh` | q003 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.690 | 0.000 | 0.690 | 0.690 | partial |
| `raw/20260724-tika-mallet-tantivy-v34-minimum-target-development-candidate-01/q004__EegtA3m` | q004 | answer-emitted | 1 | 1 | 6/6 | 0 | 0.746 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v35-shape-aware-transport-development-candidate-01/q002__aYGhpJd` | q002 | answer-emitted | 1 | 1 | 7/5 | 0 | 0.746 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v35-shape-aware-transport-development-candidate-01/q003__H2kUJzT` | q003 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.809 | 0.809 | 0.809 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v35-shape-aware-transport-development-candidate-01/q004__QEeUbMx` | q004 | answer-emitted | 1 | 1 | 9/7 | 1 | 0.734 | 0.734 | 0.734 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q005__teubYqY` | q005 | answer-emitted | 1 | 1 | 6/3 | 1 | 0.702 | 0.000 | 0.702 | 0.702 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q010__Gq8U6DX` | q010 | answer-emitted | 1 | 1 | 9/6 | 1 | 0.785 | 0.785 | 0.785 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q015__CZWMyic` | q015 | answer-emitted | 1 | 1 | 6/3 | 0 | 0.448 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q020__QbXNAtt` | q020 | answer-emitted | 1 | 1 | 7/3 | 1 | 0.590 | 0.000 | 0.590 | 0.590 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q025__xyHcZJi` | q025 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q029__tTgMEsL` | q029 | answer-emitted | 1 | 1 | 6/5 | 0 | 0.717 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q005__rTEm6MW` | q005 | answer-emitted | 1 | 1 | 6/2 | 1 | 0.556 | 0.000 | 0.556 | 0.556 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q010__fGXdzkM` | q010 | answer-emitted | 1 | 1 | 8/4 | 1 | 0.616 | 0.000 | 0.616 | 0.616 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q015__R2jd2ZE` | q015 | answer-emitted | 1 | 1 | 7/5 | 1 | 0.800 | 0.800 | 0.800 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q020__QoDNZm6` | q020 | answer-emitted | 1 | 1 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | fail |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q025__eqtN4V6` | q025 | answer-emitted | 1 | 1 | 2/1 | 0 | 0.447 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q029__uUQrgJr` | q029 | answer-emitted | 1 | 1 | 7/5 | 0 | 0.683 | 0.000 | 0.000 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-opaque-identity-suffix-development-candidate-01/q002__ooCvVJQ` | q002 | answer-emitted | 1 | 1 | 8/6 | 1 | 0.819 | 0.819 | 0.819 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-opaque-identity-suffix-development-candidate-01/q003__xQYbvtR` | q003 | answer-emitted | 1 | 1 | 8/7 | 1 | 0.796 | 0.796 | 0.796 | 0.000 | partial |
| `raw/20260724-tika-mallet-tantivy-v36-opaque-identity-suffix-development-candidate-01/q004__vy2CWRx` | q004 | answer-emitted | 1 | 1 | 9/7 | 1 | 0.734 | 0.734 | 0.734 | 0.000 | partial |
| `raw/development-candidate-01-e778c5bfd4/q002__SubYSQ4` | q002 | answer-emitted | 0 | 1 | 6/4 | 0 | 0.655 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/development-candidate-01-e778c5bfd4/q003__jPv2UtN` | q003 | answer-emitted | 0 | 1 | 8/7 | 1 | 0.796 | 0.796 | 0.796 | 0.000 | not-reviewed |
| `raw/development-candidate-01-e778c5bfd4/q004__wT2pNNc` | q004 | answer-emitted | 0 | 1 | 9/8 | 1 | 0.813 | 0.813 | 0.813 | 0.000 | not-reviewed |
| `raw/development-candidate-01-bf3233d5a7/q002__Ctc7KWQ` | q002 | answer-emitted | 0 | 1 | 8/6 | 1 | 0.822 | 0.822 | 0.822 | 0.000 | not-reviewed |
| `raw/development-candidate-01-bf3233d5a7/q003__PNjxahX` | q003 | answer-emitted | 0 | 1 | 8/7 | 1 | 0.796 | 0.796 | 0.796 | 0.000 | not-reviewed |
| `raw/development-candidate-01-bf3233d5a7/q004__CMPFCMU` | q004 | answer-emitted | 0 | 1 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/development-candidate-01-dcc6a3b78f/q002__Ak5SbZS` | q002 | answer-emitted | 0 | 1 | 8/6 | 1 | 0.672 | 0.672 | 0.672 | 0.000 | not-reviewed |
| `raw/development-candidate-01-dcc6a3b78f/q003__2yTyghh` | q003 | answer-emitted | 0 | 1 | 8/7 | 1 | 0.671 | 0.671 | 0.671 | 0.000 | not-reviewed |
| `raw/development-candidate-01-dcc6a3b78f/q004__uHFiPa9` | q004 | answer-emitted | 0 | 1 | 9/7 | 1 | 0.766 | 0.766 | 0.766 | 0.000 | not-reviewed |
| `raw/development-candidate-01-0b7b8af34f/q002__KkaHjZy` | q002 | answer-emitted | 0 | 1 | 8/6 | 1 | 0.822 | 0.822 | 0.822 | 0.000 | not-reviewed |
| `raw/development-candidate-01-0b7b8af34f/q003__3nLLfvF` | q003 | answer-emitted | 0 | 1 | 8/7 | 1 | 0.812 | 0.812 | 0.812 | 0.000 | not-reviewed |
| `raw/development-candidate-01-0b7b8af34f/q004__z6QVDZu` | q004 | answer-emitted | 0 | 1 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/development-candidate-01-1685aeb983/q002__LwwvhVk` | q002 | answer-emitted | 0 | 1 | 8/6 | 1 | 0.822 | 0.822 | 0.822 | 0.000 | not-reviewed |
| `raw/development-candidate-01-1685aeb983/q003__CFPMaop` | q003 | answer-emitted | 0 | 1 | 8/7 | 1 | 0.814 | 0.814 | 0.814 | 0.000 | not-reviewed |
| `raw/development-candidate-01-1685aeb983/q004__GrDpiFm` | q004 | answer-emitted | 0 | 1 | 9/7 | 1 | 0.734 | 0.734 | 0.734 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q001__2dVyrgg` | q001 | output-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q002__soewiqK` | q002 | answer-emitted | 1 | 1 | 8/5 | 0 | 0.707 | 0.000 | 0.000 | 0.000 | partial |
| `raw/adaptive-discovery/q003__evBKRLQ` | q003 | answer-emitted | 1 | 1 | 6/2 | 1 | 0.287 | 0.287 | 0.287 | 0.000 | partial |
| `raw/adaptive-discovery/q004__ZXGmnW9` | q004 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q006__mq9yunb` | q006 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q007__ZRxAZjw` | q007 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q008__wqU4JDM` | q008 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q009__5vyqRv5` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q011__XCtehx6` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q012__U6hBKH6` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q013__So3zPek` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q014__7bg9VjW` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q016__jo2RFGH` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q017__SQXHVtX` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q018__edqeQnG` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q019__3nE6qYC` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q021__BTZc5Rc` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q022__E39vcRa` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q023__2TvTgLr` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q024__isbugtG` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q026__PENtkUZ` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q027__MfsaCCi` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q028__LfC5Sde` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-discovery/q030__DCTS3hJ` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q031__nU7mG3h` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q032__gecngDE` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q033__vP6eP3d` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q034__KvQpZoa` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q035__A44vnam` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q036__GD9FkzE` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q037__faTKfyT` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q038__ba3BtYo` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q039__avX7Yn8` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-hard/q040__Tfe7Bx3` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-holdout/q005__X3jbyCS` | q005 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-holdout/q010__KqryTJk` | q010 | answer-emitted | 1 | 1 | 9/5 | 1 | 0.573 | 0.573 | 0.573 | 0.000 | partial |
| `raw/adaptive-holdout/q015__FHVbQZU` | q015 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/adaptive-holdout/q020__SqAUwSp` | q020 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/adaptive-holdout/q025__XyHgrki` | q025 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/adaptive-holdout/q029__azaHoVd` | q029 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q001__F2RNvqi` | q001 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q002__zoJ6Edm` | q002 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q003__Rnv36DN` | q003 | answer-emitted | 1 | 1 | 4/2 | 0 | 0.453 | 0.000 | 0.000 | 0.000 | partial |
| `raw/classical-discovery/q004__LSN5snQ` | q004 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q006__LXQjLzT` | q006 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q007__Uk6ncfC` | q007 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q008__cJuwbJy` | q008 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q009__CPngaY9` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q011__b4k2TXu` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q012__sayXX8s` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q013__Xvy3kNP` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q014__uSAHGjq` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q016__QcTGvf5` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q017__GSBMkyq` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q018__RdN9aSS` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q019__ixDZ8N9` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q021__ybsshM3` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q022__87mYMsz` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q023__ok729ji` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q024__Us37BFa` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q026__MyVGTAP` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q027__tnoQ7To` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q028__FgcD4Lx` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-discovery/q030__KfkSVRa` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q031__VUP92pm` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q032__HAGsfw5` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q033__zF2CsZm` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q034__SFk2J9R` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q035__H9MnkKB` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q036__Sy7i6Dg` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q037__Y65cZoz` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q038__H2VFHsV` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q039__ZZCZEPs` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-hard/q040__WT9r4VL` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-holdout/q005__7mhMq98` | q005 | answer-emitted | 1 | 1 | 2/2 | 0 | 0.656 | 0.656 | 0.000 | -0.656 | partial |
| `raw/classical-holdout/q010__WfBS95N` | q010 | answer-emitted | 1 | 1 | 6/5 | 1 | 0.747 | 0.747 | 0.747 | 0.000 | partial |
| `raw/classical-holdout/q015__2xYEHSZ` | q015 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/classical-holdout/q020__aXVDZbf` | q020 | answer-emitted | 1 | 1 | 3/3 | 0 | 0.676 | 0.000 | 0.000 | 0.000 | partial |
| `raw/classical-holdout/q025__fxvE4Qw` | q025 | answer-emitted | 1 | 1 | 1/1 | 0 | 0.522 | 0.000 | 0.000 | 0.000 | partial |
| `raw/classical-holdout/q029__ccGGwUz` | q029 | answer-emitted | 1 | 1 | 3/2 | 0 | 0.358 | 0.358 | 0.000 | -0.358 | partial |
| `raw/embeddings-discovery/q001__tTw8vxZ` | q001 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q002__vWY9Lvk` | q002 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q003__XUq7zEQ` | q003 | answer-emitted | 1 | 1 | 3/2 | 0 | 0.478 | 0.478 | 0.000 | -0.478 | partial |
| `raw/embeddings-discovery/q004__dLJs9N9` | q004 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q006__e86JnmT` | q006 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q007__s76E3HR` | q007 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q008__mZ4KbUD` | q008 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q009__zx7ecaq` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q011__fEtNYKN` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q012__4REbVeq` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q013__mcCGoKj` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q014__kkq2NRX` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q016__iEeugsu` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q017__z2ViZEK` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q018__swoUtJn` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q019__Mww9Ezo` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q021__S9JdWVg` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q022__Pexoz6b` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q023__wmbKofF` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q024__eFx7HV4` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q026__NzmwzvX` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q027__J3x6mgy` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q028__qbGtJZ4` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-discovery/q030__uQFF52U` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q031__SMGFF9c` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q032__YrVfEMy` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q033__pFSui7m` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q034__WKSwsUS` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q035__j5XpBnP` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q036__RZWR6qo` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q037__dBzQuPb` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q038__Ksrmn2f` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q039__nTQTj8j` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-hard/q040__8FDce5S` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-holdout/q005__YyjSfDs` | q005 | answer-emitted | 1 | 1 | 7/4 | 0 | 0.822 | 0.000 | 0.000 | 0.000 | partial |
| `raw/embeddings-holdout/q010__Tbfcz9S` | q010 | answer-emitted | 1 | 1 | 7/6 | 1 | 0.840 | 0.840 | 0.840 | 0.000 | partial |
| `raw/embeddings-holdout/q015__MCEZJTF` | q015 | output-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-holdout/q020__3w9oRLK` | q020 | output-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/embeddings-holdout/q025__2XTrhpu` | q025 | answer-emitted | 1 | 0 | 1/1 | 0 | 0.522 | 0.000 | 0.000 | 0.000 | partial |
| `raw/embeddings-holdout/q029__Vy3RC37` | q029 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q001__hsMGtiL` | q001 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q002__VERDTok` | q002 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q003__RuoowDd` | q003 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q004__BiAvb2g` | q004 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q006__tX3o7pZ` | q006 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q007__eoVy9m9` | q007 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q008__VdcNrci` | q008 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q009__XwuW32L` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q011__gpiBGew` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q012__wPFq5zR` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q013__e3GRu3a` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q014__yFhsUrt` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q016__e36bUTo` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q017__PmaxyM9` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q018__Qy3ALK4` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q019__jM4rd46` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q021__97xCqwP` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q022__zrWkdck` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q023__Pgctfro` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q024__83rxCAz` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q026__fwSHE6G` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q027__ZtFMfXe` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q028__sAcm7oL` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-discovery/q030__oV7pp5V` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q031__8YPQUxG` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q032__BYmBXMM` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q033__zEqzRPC` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q034__DmmCp25` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q035__yaVnVsW` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q036__D2BJgpX` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q037__CfACx76` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q038__HpBGrvt` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q039__J4cZ73L` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-hard/q040__Tf4T6tb` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-holdout/q005__md3HDcu` | q005 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-holdout/q010__nFUm37S` | q010 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-holdout/q015__phdDkGb` | q015 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-holdout/q020__sgYzFTA` | q020 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-holdout/q025__iZFBFyg` | q025 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/ensemble-holdout/q029__BRdyXRd` | q029 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q001__iunfo6L` | q001 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q002__7gneGzv` | q002 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q003__ZoTbwPw` | q003 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q004__4ag2xdD` | q004 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q006__uWyWE3j` | q006 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q007__R5BWppN` | q007 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q008__AWAhSkK` | q008 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q009__cntqGwW` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q011__SDxVjCs` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q012__sVAP3Xf` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q013__pxY2HVU` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q014__W4BP6jU` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q016__52nbJsw` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q017__iehxtqr` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q018__CLhBsQy` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q019__YgfEQeX` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q021__LNt8JeY` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q022__ihMDY2c` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q023__QoM76Ge` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q024__GNCjuLP` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q026__fPXPX7t` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q027__VphhpFV` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q028__eRGSMwc` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-discovery/q030__E2UjwsC` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q031__xqppze4` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q032__hf2vVa3` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q033__ZNHAKXj` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q034__VbySLUU` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q035__qBUuUvc` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q036__6y2XbVv` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q037__4ekX2VB` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q038__FKNEcnQ` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q039__GYa5udw` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-hard/q040__WHtRBuV` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-holdout/q005__BGairJf` | q005 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-holdout/q010__jP3fB8g` | q010 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/entity-graph-holdout/q015__2ScZo2o` | q015 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/entity-graph-holdout/q020__pm88Gir` | q020 | answer-emitted | 1 | 0 | 1/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/entity-graph-holdout/q025__hws9bNQ` | q025 | answer-emitted | 1 | 1 | 4/2 | 0 | 0.581 | 0.000 | 0.000 | 0.000 | partial |
| `raw/entity-graph-holdout/q029__r6FuVB2` | q029 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | fail |
| `raw/graphify-discovery/q001__hKoBtsw` | q001 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q002__qVonfoj` | q002 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q003__zwuFAQW` | q003 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q004__844TiTd` | q004 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q006__wYyFUGE` | q006 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q007__sVi5dhL` | q007 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q008__wmSfHVU` | q008 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q009__q9WRjpJ` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q011__uYRo5Nb` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q012__vhkSi7V` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q013__fTb3vZ5` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q014__7FeQTw2` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q016__XLBKMdx` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q017__GMX5BTA` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q018__F35J7wT` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q019__pBRXD5z` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q021__Hu4gbx6` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q022__b9FkTkw` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q023__t3965fz` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q024__svpXKZm` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q026__9b2FE4A` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q027__yiVXdWa` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q028__SW9iAGC` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-discovery/q030__AhPTjPm` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q031__S5PL9px` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q032__yRTeMFV` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q033__UFc3iZP` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q034__FXSKVDT` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q035__QbZWGXw` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q036__yhC8K6A` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q037__yW4LXtu` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q038__awwJa2Q` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q039__2MGkSYQ` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-hard/q040__YzTPuV7` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-holdout/q005__oWaV8x4` | q005 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-holdout/q010__xAStiwb` | q010 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-holdout/q015__THhj5Fc` | q015 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-holdout/q020__LshRYn4` | q020 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-holdout/q025__GLr5mnt` | q025 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/graphify-holdout/q029__VjbPJhk` | q029 | agent-interrupted | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q001__rTbcCiF` | q001 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/legacy-discovery/q002__4zz7Ev2` | q002 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/legacy-discovery/q003__9AEFNBv` | q003 | output-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q004__8weRpp4` | q004 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/legacy-discovery/q006__dSUz3wk` | q006 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q007__V3TjcCH` | q007 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/legacy-discovery/q008__6jqbxmv` | q008 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q009__rn45UXS` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q011__D2iY2rk` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q012__PskLCte` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q013__EFVrALz` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q014__xvqNDDf` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q016__nhMRVi2` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q017__a5oMBvc` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q018__JbBgiRD` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q019__cPaCvYQ` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q021__VozCatW` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q022__tVBBevz` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q023__iYqVuLR` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q024__TwqXdEW` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q026__nkSSf6N` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q027__6zmQTjm` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q028__EDQBBNn` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-discovery/q030__F58ctpw` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q031__sWadN54` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q032__Qc96sN7` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q033__rbeNCvv` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q034__k8Dtus9` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q035__DeejAJu` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q036__QjwrV8c` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q037__MNidVaY` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q038__HervpTG` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q039__TGTi72t` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-hard/q040__3CtKMdU` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-holdout/q005__iNh7Frt` | q005 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/legacy-holdout/q010__67E5SRG` | q010 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/legacy-holdout/q015__pDEQ5G8` | q015 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/legacy-holdout/q020__SEZceZy` | q020 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-holdout/q025__tWSSxjJ` | q025 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/legacy-holdout/q029__KpYF8pM` | q029 | provider-context-limit | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q001__iQoAtiw` | q001 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q002__eGddevf` | q002 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q003__dXzgniC` | q003 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q004__gnWSiHV` | q004 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q006__LiSxDiU` | q006 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q007__dCX5Xv5` | q007 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q008__f2EuTLp` | q008 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q009__XUihHwg` | q009 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q011__dQ3kZFa` | q011 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q012__wDxRUQF` | q012 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q013__x232djs` | q013 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q014__bLFLJAT` | q014 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q016__YRoCxSW` | q016 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q017__CRCdfBD` | q017 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q018__JUhyE7L` | q018 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q019__YDidgDU` | q019 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q021__k8bKKNZ` | q021 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q022__n3TdcRk` | q022 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q023__DLH2ych` | q023 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q024__ysycVFb` | q024 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q026__Ksr47mg` | q026 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q027__e4ArSRt` | q027 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q028__BNXZ2N6` | q028 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-discovery/q030__XKyBKmg` | q030 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q031__aTVnFyH` | q031 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q032__uAzXj2Q` | q032 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q033__hkp5DqZ` | q033 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q034__yYDvQKV` | q034 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q035__tfHYYwb` | q035 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q036__MXFTGjR` | q036 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q037__NXKYakP` | q037 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q038__RYTQXH2` | q038 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q039__9XRRwYw` | q039 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-hard/q040__27WMpcN` | q040 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |
| `raw/turso-holdout/q005__U6wVt9C` | q005 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/turso-holdout/q010__rf8BN2S` | q010 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/turso-holdout/q015__3MyZE8q` | q015 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/turso-holdout/q020__HCMuVsV` | q020 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/turso-holdout/q025__k2Fs7Ee` | q025 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/turso-holdout/q029__uTdWPsh` | q029 | answer-emitted | 1 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | partial |
| `raw/0001-q001-adaptive/q001__9D4i3hi` | q001 | provider-quota | 0 | 0 | 0/0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | not-reviewed |

## Legacy reviewed responses without a raw body

These rows retain their historical mechanical observations and manual verdicts, but they cannot be recalculated under schema 3.0 because the original response bodies are absent.

| Response | Q | Contract | Evidence | Focus docs | Historical reward | Semantic |
|---|---|---:|---:|---:|---:|---|

## Curated reference calibration

| Q | Evidence | Valid/focus docs | Gate | Utility | Reward | Semantic targets | Hard anchors |
|---|---:|---:|---:|---:|---:|---:|---:|
| q001 | 15 | 15/15 | 1 | 1.000 | 1.000 | 4 | 0 |
| q002 | 8 | 8/8 | 1 | 1.000 | 1.000 | 4 | 0 |
| q003 | 8 | 8/8 | 1 | 0.891 | 0.891 | 4 | 0 |
| q004 | 11 | 11/11 | 1 | 1.000 | 1.000 | 4 | 0 |
| q005 | 5 | 5/5 | 1 | 1.000 | 1.000 | 4 | 0 |
| q006 | 6 | 6/6 | 1 | 1.000 | 1.000 | 4 | 0 |
| q007 | 5 | 5/5 | 1 | 1.000 | 1.000 | 4 | 0 |
| q008 | 13 | 6/6 | 1 | 1.000 | 1.000 | 4 | 0 |
| q009 | 6 | 6/6 | 1 | 1.000 | 1.000 | 4 | 0 |
| q010 | 19 | 7/6 | 1 | 0.838 | 0.838 | 4 | 0 |
| q011 | 14 | 7/7 | 1 | 1.000 | 1.000 | 4 | 0 |
| q012 | 9 | 9/9 | 1 | 1.000 | 1.000 | 4 | 0 |
| q013 | 17 | 7/6 | 1 | 0.829 | 0.829 | 4 | 0 |
| q014 | 10 | 10/10 | 1 | 1.000 | 1.000 | 4 | 0 |
| q015 | 7 | 7/7 | 1 | 1.000 | 1.000 | 4 | 0 |
| q016 | 16 | 10/10 | 1 | 1.000 | 1.000 | 4 | 0 |
| q017 | 23 | 8/8 | 1 | 1.000 | 1.000 | 4 | 0 |
| q018 | 9 | 9/9 | 1 | 1.000 | 1.000 | 4 | 0 |
| q019 | 14 | 6/6 | 1 | 1.000 | 1.000 | 4 | 0 |
| q020 | 7 | 7/7 | 1 | 1.000 | 1.000 | 4 | 0 |
| q021 | 10 | 7/7 | 1 | 1.000 | 1.000 | 4 | 0 |
| q022 | 6 | 6/6 | 1 | 1.000 | 1.000 | 4 | 0 |
| q023 | 20 | 11/11 | 1 | 0.853 | 0.853 | 5 | 0 |
| q024 | 24 | 8/8 | 1 | 0.761 | 0.761 | 4 | 0 |
| q025 | 5 | 5/5 | 1 | 1.000 | 1.000 | 4 | 0 |
| q026 | 15 | 9/9 | 1 | 1.000 | 1.000 | 4 | 0 |
| q027 | 6 | 6/5 | 1 | 0.960 | 0.960 | 4 | 0 |
| q028 | 19 | 8/8 | 1 | 1.000 | 1.000 | 4 | 0 |
| q029 | 9 | 9/9 | 1 | 1.000 | 1.000 | 4 | 0 |
| q030 | 35 | 15/15 | 1 | 1.000 | 1.000 | 5 | 0 |
| q031 | 3 | 3/3 | 1 | 1.000 | 1.000 | 7 | 6 |
| q032 | 5 | 5/5 | 1 | 1.000 | 1.000 | 9 | 7 |
| q033 | 3 | 3/3 | 1 | 1.000 | 1.000 | 7 | 8 |
| q034 | 4 | 4/4 | 1 | 1.000 | 1.000 | 7 | 6 |
| q035 | 4 | 4/4 | 1 | 1.000 | 1.000 | 7 | 8 |
| q036 | 4 | 4/4 | 1 | 1.000 | 1.000 | 9 | 9 |
| q037 | 3 | 3/3 | 1 | 1.000 | 1.000 | 9 | 19 |
| q038 | 4 | 4/4 | 1 | 1.000 | 1.000 | 7 | 12 |
| q039 | 4 | 4/4 | 1 | 1.000 | 1.000 | 8 | 8 |
| q040 | 4 | 4/4 | 1 | 1.000 | 1.000 | 8 | 11 |

All reference rows are curated evaluator material. Their pass status validates the metric implementation and expected-answer surface; it does not improve empirical model coverage.
