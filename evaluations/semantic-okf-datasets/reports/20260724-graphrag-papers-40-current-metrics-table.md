# GraphRAG 40-question current-metrics evaluation table

## Interpretation boundary

This is an artifact-only recalculation of immutable Harbor traces; **no new model calls were made**. Every discovered raw trial was rescored with the current dataset policy and diagnostics schema 3.0. The scorer used each trial's native ledger and crosswalk so exact evidence identities remain valid across family-specific source representations.

The reward is a mechanical contract-and-focus diagnostic, not a semantic score. Semantic verdicts remain the documented manual adjudications. The forty curated references are shown only as a calibration surface and are not counted as live trials.

## Recalculation summary

| Measure | Value |
|---|---:|
| Dataset questions | 40 |
| Raw Harbor trials rescored | 180 / 180 |
| Reviewable raw responses | 143 |
| Legacy reviewed responses without raw bodies | 32 |
| Total individually reviewable responses | 175 |
| Current mechanical qualification passes | 99 / 180 |
| Questions with empirical response coverage | 29 / 40 |
| Reference calibrations passing current contract | 40 / 40 |
| Comparable rewards increased / decreased / unchanged | 46 / 0 / 128 |
| Mean original / current reward (comparable trials) | 0.244128 / 0.402476 |

Trace outcomes: `agent-interrupted`=5, `answer-emitted`=162, `missing-response`=1, `missing-trace`=7, `provider-context-limit`=2, `provider-error`=1, `provider-quota`=2.

Empirical full-dataset claim eligible: `false`. Missing empirical questions: `q028`, `q031`, `q032`, `q033`, `q034`, `q035`, `q036`, `q037`, `q038`, `q039`, `q040`.

## Every question under the current metrics

| Q | Cohort | Trials | Reviewed raw+legacy | Semantic (P/Pt/F) | Qualified | Latest trial | Latest reviewed | Valid/focus docs | Gate | Utility | Reward | Empirical |
|---|---|---:|---:|---|---:|---|---|---:|---:|---:|---:|---|
| q001 | discovery | 10 | 2+1 | P0/Pt3/F0 | 2/10 | provider-error | answer-emitted; partial | 9/9 | 1 | 0.778 | 0.778 | covered |
| q002 | discovery | 41 | 33+2 | P0/Pt34/F1 | 24/41 | answer-emitted | answer-emitted; partial | 8/6 | 1 | 0.819 | 0.819 | covered |
| q003 | discovery | 38 | 34+3 | P0/Pt37/F0 | 27/38 | answer-emitted | answer-emitted; partial | 8/7 | 1 | 0.796 | 0.796 | covered |
| q004 | discovery | 37 | 30+1 | P0/Pt30/F1 | 21/37 | answer-emitted | answer-emitted; partial | 9/7 | 1 | 0.734 | 0.734 | covered |
| q005 | holdout | 8 | 6+4 | P0/Pt10/F0 | 5/8 | answer-emitted | answer-emitted; partial | 6/2 | 1 | 0.556 | 0.556 | covered |
| q006 | discovery | 2 | 1+0 | P0/Pt1/F0 | 0/2 | missing-trace | answer-emitted; partial | 8/4 | 0 | 0.494 | 0.000 | covered |
| q007 | discovery | 2 | 1+1 | P0/Pt2/F0 | 0/2 | missing-trace | answer-emitted; partial | 5/3 | 0 | 0.710 | 0.000 | covered |
| q008 | discovery | 2 | 1+0 | P1/Pt0/F0 | 0/2 | missing-trace | answer-emitted; pass | 3/1 | 0 | 0.399 | 0.000 | covered |
| q009 | discovery | 2 | 1+0 | P0/Pt1/F0 | 1/2 | missing-trace | answer-emitted; partial | 6/5 | 1 | 0.884 | 0.884 | covered |
| q010 | holdout | 4 | 4+5 | P0/Pt9/F0 | 3/4 | answer-emitted | answer-emitted; partial | 8/4 | 1 | 0.616 | 0.616 | covered |
| q011 | discovery | 2 | 1+0 | P0/Pt1/F0 | 0/2 | missing-trace | answer-emitted; partial | 2/1 | 0 | 0.407 | 0.000 | covered |
| q012 | discovery | 1 | 1+0 | P0/Pt1/F0 | 0/1 | answer-emitted | answer-emitted; partial | 5/4 | 0 | 0.653 | 0.000 | covered |
| q013 | discovery | 1 | 1+0 | P0/Pt1/F0 | 1/1 | answer-emitted | answer-emitted; partial | 9/7 | 1 | 0.899 | 0.899 | covered |
| q014 | discovery | 1 | 1+0 | P0/Pt1/F0 | 0/1 | answer-emitted | answer-emitted; partial | 7/3 | 0 | 0.484 | 0.000 | covered |
| q015 | holdout | 4 | 4+4 | P0/Pt8/F0 | 3/4 | answer-emitted | answer-emitted; partial | 7/5 | 1 | 0.800 | 0.800 | covered |
| q016 | discovery | 1 | 1+0 | P0/Pt1/F0 | 1/1 | answer-emitted | answer-emitted; partial | 7/6 | 1 | 0.757 | 0.757 | covered |
| q017 | discovery | 1 | 1+0 | P0/Pt1/F0 | 0/1 | answer-emitted | answer-emitted; partial | 6/3 | 0 | 0.568 | 0.000 | covered |
| q018 | discovery | 1 | 1+0 | P0/Pt1/F0 | 1/1 | answer-emitted | answer-emitted; partial | 6/5 | 1 | 0.717 | 0.717 | covered |
| q019 | discovery | 1 | 1+0 | P0/Pt1/F0 | 1/1 | answer-emitted | answer-emitted; partial | 8/2 | 1 | 0.480 | 0.480 | covered |
| q020 | holdout | 4 | 4+3 | P0/Pt6/F1 | 3/4 | answer-emitted | answer-emitted; fail | 0/0 | 0 | 0.000 | 0.000 | covered |
| q021 | discovery | 1 | 1+0 | P1/Pt0/F0 | 0/1 | answer-emitted | answer-emitted; pass | 8/4 | 0 | 0.678 | 0.000 | covered |
| q022 | discovery | 1 | 1+0 | P0/Pt1/F0 | 1/1 | answer-emitted | answer-emitted; partial | 6/5 | 1 | 0.884 | 0.884 | covered |
| q023 | discovery | 1 | 1+0 | P1/Pt0/F0 | 0/1 | answer-emitted | answer-emitted; pass | 8/8 | 0 | 0.739 | 0.000 | covered |
| q024 | discovery | 1 | 1+0 | P0/Pt1/F0 | 1/1 | answer-emitted | answer-emitted; partial | 8/7 | 1 | 0.684 | 0.684 | covered |
| q025 | holdout | 4 | 4+5 | P0/Pt9/F0 | 2/4 | answer-emitted | answer-emitted; partial | 2/1 | 0 | 0.447 | 0.000 | covered |
| q026 | discovery | 1 | 1+0 | P0/Pt1/F0 | 1/1 | answer-emitted | answer-emitted; partial | 6/5 | 1 | 0.722 | 0.722 | covered |
| q027 | discovery | 1 | 1+0 | P0/Pt1/F0 | 0/1 | answer-emitted | answer-emitted; partial | 4/3 | 0 | 0.581 | 0.000 | covered |
| q028 | discovery | 2 | 0+0 | P0/Pt0/F0 | 0/2 | provider-quota | — | — | — | — | — | missing |
| q029 | holdout | 4 | 3+3 | P0/Pt5/F1 | 1/4 | answer-emitted | answer-emitted; partial | 7/5 | 0 | 0.683 | 0.000 | covered |
| q030 | discovery | 1 | 1+0 | P0/Pt1/F0 | 0/1 | answer-emitted | answer-emitted; partial | 9/9 | 0 | 0.778 | 0.000 | covered |
| q031 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q032 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q033 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q034 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q035 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q036 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q037 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q038 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q039 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |
| q040 | hard | 0 | 0+0 | P0/Pt0/F0 | 0/0 | — | — | — | — | — | — | missing |

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

## Legacy reviewed responses without a raw body

These rows retain their historical mechanical observations and manual verdicts, but they cannot be recalculated under schema 3.0 because the original response bodies are absent.

| Response | Q | Contract | Evidence | Focus docs | Historical reward | Semantic |
|---|---|---:|---:|---:|---:|---|
| `historical/20260717-papers-consult-gpt53-spark-01/07e23ace-ace3-4778-acdc-9e957c2f7655` | q002 | 1 | 12 | 5 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/de4ec73d-1cd1-459e-93e9-5a03c48d392a` | q003 | 1 | 7 | 2 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/f1c0f025-d993-4df9-ad2c-db88baa80e5f` | q010 | 1 | 9 | 5 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/8dc2313c-c8fc-4c40-90a1-30247668ab7b` | q015 | 0 | 11 | 5 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/bfe9b1c6-d7d1-4ce6-80d5-4b32e04421be` | q025 | 0 | 18 | 3 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/3532b336-16ad-463d-b774-7be5f751dc23` | q003 | 1 | 15 | 2 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/821eac3a-5664-4afc-9872-601e03d69fbe` | q005 | 1 | 14 | 2 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/dcfcb559-8558-4292-97df-2bc21735d581` | q010 | 1 | 9 | 5 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/d9f2da6a-8d3b-4461-ba1e-b46acb956401` | q020 | 1 | 9 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/50a84566-8a52-485b-a4ce-0ef6dcb25ac7` | q025 | 1 | 16 | 1 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/919b6b71-60e0-4b24-84a4-3785d1a8c4c3` | q029 | 1 | 7 | 2 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/a8a6e95c-5a95-48e7-8c53-9b9a68c443f0` | q003 | 1 | 14 | 2 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/50a09529-f8dd-480e-9096-58073d5a5790` | q005 | 1 | 14 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/e334f3c0-2f39-4da1-a572-845493b2ba57` | q010 | 1 | 14 | 6 | 0.840 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/d67e3b79-00b8-4c72-8a9b-d8d398f0b0fe` | q025 | 0 | 6 | 1 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/8538428e-749f-4d1f-9e8e-5c360e0b23d3` | q015 | 0 | 10 | 5 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/d0a6dc93-aca3-420a-8e4d-4250bd0a400c` | q020 | 0 | 5 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/f143ca25-2b20-4f58-8a61-24855beefbac` | q025 | 1 | 6 | 2 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/9b5c8868-e106-4272-a655-027783ada26d` | q029 | 0 | 0 | 0 | 0.000 | fail |
| `historical/20260717-papers-consult-gpt53-spark-01/1f43edb2-1a69-4161-bcd7-159b88afd6e6` | q001 | 0 | 41 | 14 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/77721d26-ce40-4845-af14-896c886cfcc1` | q002 | 0 | 33 | 6 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/a13a5c9c-bec3-40fe-98cf-6b3d023ee00d` | q004 | 0 | 11 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/cce65ee3-f234-4331-9efd-57b22bd7f76e` | q005 | 0 | 14 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/6713ac5f-bb88-490c-835e-231ced3d00f2` | q007 | 0 | 18 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/6a6778a0-072b-4425-8d4d-ba625dd0814c` | q010 | 0 | 8 | 2 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/8573a931-850c-4c4f-b64b-50805a322091` | q015 | 0 | 10 | 5 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/33e5217c-f174-4297-861b-c0fc50e250ee` | q005 | 0 | 22 | 3 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/88f9aab6-cc81-4be2-8713-59b152d900cf` | q010 | 0 | 10 | 3 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/ddec4f09-7244-4f25-bc75-ce4d0e6da24e` | q015 | 0 | 12 | 5 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/3aed67ca-ce2d-49a8-879d-fba45213f6b1` | q020 | 0 | 30 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/f9b7358d-264f-4c2b-a75c-8da3b7c29446` | q025 | 0 | 20 | 4 | 0.000 | partial |
| `historical/20260717-papers-consult-gpt53-spark-01/6c7fc2d1-214d-4157-9ec2-56dce6d73e2b` | q029 | 0 | 13 | 5 | 0.000 | partial |

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
| q030 | 34 | 15/15 | 1 | 1.000 | 1.000 | 5 | 0 |
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
