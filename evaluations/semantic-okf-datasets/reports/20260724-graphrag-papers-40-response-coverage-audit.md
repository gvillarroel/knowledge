# GraphRAG 40-question response and coverage audit

## Scope correction

The canonical dataset contains **40 questions**. The earlier 18-response report was a v36 evidence slice, not the complete dataset.

This audit inventories 189 complete raw Harbor responses. 31 of them were matched by trial id to preserved historical adjudications; 1 adjudicated historical rows remain without a raw body. The result contains **190 reviewable responses**.

Semantic adjudication covers 175 responses. The remaining 15 raw responses have current mechanical diagnostics but await digest-bound semantic review.

Only **29/40 questions** have a complete response. Missing: `q028`, `q031`, `q032`, `q033`, `q034`, `q035`, `q036`, `q037`, `q038`, `q039`, `q040`.

`q002`-`q004` account for 118/189 raw responses (62.4%), so the archive is iteration-heavy rather than question-balanced.

Semantic adjudications: 3 pass, 168 partial, and 4 fail; 15 are not reviewed. Mechanical reward is not used as semantic correctness.

**Full-dataset claim eligible:** `false`.

The 60 older comparison cells are retained as summary-only evidence; their response bodies are absent, so they are not silently counted as individually reviewable responses.

## Every question

| Question | Cohort | Focus docs | Minimum | Semantic targets | Raw | Historical | Total | Coverage |
|---|---|---:|---:|---:|---:|---:|---:|---|
| q001 | discovery | 15 | 8 | 4 | 3 | 0 | 3 | covered |
| q002 | discovery | 8 | 6 | 4 | 40 | 0 | 40 | covered |
| q003 | discovery | 10 | 6 | 4 | 42 | 0 | 42 | covered |
| q004 | discovery | 11 | 7 | 4 | 36 | 0 | 36 | covered |
| q005 | holdout | 5 | 4 | 4 | 10 | 0 | 10 | covered |
| q006 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q007 | discovery | 5 | 4 | 4 | 2 | 0 | 2 | covered |
| q008 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q009 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q010 | holdout | 8 | 6 | 4 | 9 | 0 | 9 | covered |
| q011 | discovery | 7 | 5 | 4 | 1 | 0 | 1 | covered |
| q012 | discovery | 9 | 6 | 4 | 1 | 0 | 1 | covered |
| q013 | discovery | 8 | 6 | 4 | 1 | 0 | 1 | covered |
| q014 | discovery | 10 | 7 | 4 | 1 | 0 | 1 | covered |
| q015 | holdout | 7 | 5 | 4 | 8 | 0 | 8 | covered |
| q016 | discovery | 10 | 7 | 4 | 1 | 0 | 1 | covered |
| q017 | discovery | 8 | 6 | 4 | 1 | 0 | 1 | covered |
| q018 | discovery | 9 | 6 | 4 | 1 | 0 | 1 | covered |
| q019 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q020 | holdout | 7 | 5 | 4 | 7 | 0 | 7 | covered |
| q021 | discovery | 7 | 5 | 4 | 1 | 0 | 1 | covered |
| q022 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q023 | discovery | 15 | 8 | 5 | 1 | 0 | 1 | covered |
| q024 | discovery | 14 | 8 | 4 | 1 | 0 | 1 | covered |
| q025 | holdout | 5 | 4 | 4 | 9 | 0 | 9 | covered |
| q026 | discovery | 9 | 6 | 4 | 1 | 0 | 1 | covered |
| q027 | discovery | 5 | 4 | 4 | 1 | 0 | 1 | covered |
| q028 | discovery | 8 | 6 | 4 | 0 | 0 | 0 | missing |
| q029 | holdout | 9 | 6 | 4 | 5 | 1 | 6 | covered |
| q030 | discovery | 15 | 10 | 5 | 1 | 0 | 1 | covered |
| q031 | hard | 3 | — | 7 | 0 | 0 | 0 | missing |
| q032 | hard | 5 | — | 9 | 0 | 0 | 0 | missing |
| q033 | hard | 3 | — | 7 | 0 | 0 | 0 | missing |
| q034 | hard | 4 | — | 7 | 0 | 0 | 0 | missing |
| q035 | hard | 4 | — | 7 | 0 | 0 | 0 | missing |
| q036 | hard | 4 | — | 9 | 0 | 0 | 0 | missing |
| q037 | hard | 3 | — | 9 | 0 | 0 | 0 | missing |
| q038 | hard | 4 | — | 7 | 0 | 0 | 0 | missing |
| q039 | hard | 4 | — | 8 | 0 | 0 | 0 | missing |
| q040 | hard | 4 | — | 8 | 0 | 0 | 0 | missing |

All 40 question specifications were reviewed against their authored rubric or hard ground truth. No question-content defect was found. The defects were in coverage and evaluator semantics.

## Every reviewable response

| Response | Question | Semantic | Answer | Contract | Evidence | Valid docs | Focus docs | Reward |
|---|---|---|---|---:|---:|---:|---:|---:|
| `historical/20260717-papers-consult-gpt53-spark-01/9b5c8868-e106-4272-a655-027783ada26d` | q029 | fail | non-null | 0 | 0 | — | 0 | 0.000000 |
| `raw/20260723-tika-mallet-consult-holdout-q005-live-04/q005__yh5yy9X` | q005 | partial | non-null | 1 | 7 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-consult-holdout-q005-live-05/q005__gHaYNSh` | q005 | partial | non-null | 1 | 7 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-consult-holdout-q005-live-v2-01/q005__qFqD7Yj` | q005 | partial | non-null | 1 | 6 | — | 4 | 0.833061 |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q010__B9sqvVX` | q010 | partial | non-null | 1 | 7 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q015__U2FuVa3` | q015 | partial | non-null | 1 | 9 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q020__euRLrjj` | q020 | partial | non-null | 1 | 7 | — | 5 | 0.795868 |
| `raw/20260723-tika-mallet-consult-holdout-rest-live-v2-01/q025__a9u8Ban` | q025 | partial | non-null | 1 | 8 | — | 2 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-github-copilot-preflight-02/q001__JgbQyBS` | q001 | partial | non-null | 1 | 9 | — | 9 | 0.777757 |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q002__pN36ijn` | q002 | partial | non-null | 1 | 7 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v1-discovery-baseline-01/q003__h524KYS` | q003 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v3-development-candidate-03/q003__okYVTgk` | q003 | partial | non-null | 1 | 10 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-development-candidate-01/q002__fQtYmeu` | q002 | partial | non-null | 1 | 8 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-development-candidate-01/q003__SrhQcZ8` | q003 | partial | non-null | 0 | 7 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-development-candidate-01/q004__Kdp3rVK` | q004 | partial | non-null | 0 | 8 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-01/q002__gzPBEmE` | q002 | partial | non-null | 1 | 9 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-01/q003__Tfnutc7` | q003 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-01/q004__mXH7TvG` | q004 | partial | non-null | 1 | 7 | — | 6 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-02/q002__HyWuJCC` | q002 | partial | non-null | 1 | 6 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-02/q003__Z8i6Fx4` | q003 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-discovery-baseline-02/q004__8fcXLe2` | q004 | partial | non-null | 1 | 11 | — | 8 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v5-provider-preflight-01/q002__QCX6gdT` | q002 | partial | non-null | 1 | 7 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v6-development-candidate-01/q002__QuhuA2G` | q002 | partial | non-null | 1 | 8 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v6-development-candidate-01/q003__Rn3rLd8` | q003 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v6-development-candidate-01/q004__QtDuMkU` | q004 | partial | non-null | 1 | 7 | — | 6 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v7-development-candidate-01/q002__GwCByW4` | q002 | partial | non-null | 1 | 8 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v7-development-candidate-01/q003__mjivyt7` | q003 | partial | non-null | 1 | 8 | — | 6 | 0.734272 |
| `raw/20260723-tika-mallet-tantivy-v7-development-candidate-01/q004__YfPyWdG` | q004 | partial | non-null | 1 | 9 | — | 8 | 0.813295 |
| `raw/20260723-tika-mallet-tantivy-v8-development-candidate-01/q002__azcgJwZ` | q002 | partial | non-null | 1 | 8 | — | 7 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v8-development-candidate-01/q003__X4zgxS3` | q003 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v8-development-candidate-01/q004__LQbhEdP` | q004 | partial | non-null | 1 | 12 | — | 9 | 0.859971 |
| `raw/20260723-tika-mallet-tantivy-v9-development-candidate-01/q002__WEb4NaC` | q002 | partial | non-null | 1 | 8 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-tantivy-v9-development-candidate-01/q003__zCQcKFb` | q003 | partial | non-null | 1 | 8 | — | 6 | 0.727004 |
| `raw/20260723-tika-mallet-tantivy-v9-development-candidate-01/q004__msRqjWq` | q004 | partial | non-null | 1 | 8 | — | 7 | 0.760667 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q001__PebPBhy` | q001 | partial | non-null | 1 | 10 | — | 9 | 0.777757 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q002__r3B8JPb` | q002 | partial | non-null | 1 | 7 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q003__xzGPwP4` | q003 | partial | non-null | 1 | 7 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q004__sLi4Dqz` | q004 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q006__eakXQfk` | q006 | partial | non-null | 1 | 10 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q007__GwiHvjF` | q007 | partial | non-null | 1 | 6 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q008__ppJGeAn` | q008 | pass | non-null | 0 | 5 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q009__oBjsXHo` | q009 | partial | non-null | 1 | 6 | — | 5 | 0.884330 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q011__QtwkC4K` | q011 | partial | non-null | 1 | 5 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q012__V9qSEaF` | q012 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q013__aoc5bq7` | q013 | partial | non-null | 1 | 9 | — | 7 | 0.898978 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q014__Rfx8WJ7` | q014 | partial | non-null | 1 | 10 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q016__nMhf2M4` | q016 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q017__RnYZcfx` | q017 | partial | non-null | 1 | 7 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q018__WfCPXPk` | q018 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q019__aLN785h` | q019 | partial | non-null | 1 | 8 | — | 2 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q021__4XPFLhs` | q021 | pass | non-null | 0 | 10 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q022__kXxqnME` | q022 | partial | non-null | 1 | 6 | — | 5 | 0.884330 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q023__UYWESow` | q023 | pass | non-null | 1 | 9 | — | 9 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q024__B3cFMLe` | q024 | partial | non-null | 1 | 8 | — | 7 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q026__MYr6QnG` | q026 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q027__Csou2Jh` | q027 | partial | non-null | 1 | 5 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-v3-discovery-live-01/q030__HdWwAVo` | q030 | partial | non-null | 1 | 10 | — | 10 | 0.000000 |
| `raw/20260723-tika-mallet-v3-holdout-q029-live-01/q029__2rqaPyg` | q029 | partial | non-null | 1 | 6 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q005__gNNuojW` | q005 | partial | non-null | 1 | 5 | — | 3 | 0.000000 |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q010__QvwywR6` | q010 | partial | non-null | 1 | 10 | — | 6 | 0.000000 |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q015__8RAbSdf` | q015 | partial | non-null | 1 | 8 | — | 4 | 0.000000 |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q020__emcyE9S` | q020 | partial | non-null | 1 | 10 | — | 5 | 0.770331 |
| `raw/20260723-tika-mallet-v3-holdout-rest-live-01/q025__AhWGmHo` | q025 | partial | non-null | 1 | 5 | — | 2 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v10-development-candidate-01/q002__TKj95xH` | q002 | partial | non-null | 1 | 9 | — | 5 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v10-development-candidate-01/q003__keYyjcF` | q003 | partial | non-null | 1 | 7 | — | 6 | 0.745766 |
| `raw/20260724-tika-mallet-tantivy-v10-development-candidate-01/q004__rM4rNM9` | q004 | partial | non-null | 1 | 8 | — | 7 | 0.777757 |
| `raw/20260724-tika-mallet-tantivy-v11-development-candidate-01/q002__gLddyCJ` | q002 | partial | non-null | 1 | 8 | — | 4 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v11-development-candidate-01/q003__Tgpiqvv` | q003 | partial | non-null | 1 | 8 | — | 6 | 0.718359 |
| `raw/20260724-tika-mallet-tantivy-v11-development-candidate-01/q004__eCTkQHj` | q004 | partial | non-null | 1 | 11 | — | 8 | 0.799238 |
| `raw/20260724-tika-mallet-tantivy-v12-development-candidate-01/q002__Mm7pSUc` | q002 | partial | non-null | 1 | 7 | — | 6 | 0.840103 |
| `raw/20260724-tika-mallet-tantivy-v12-development-candidate-01/q003__rj3GwQB` | q003 | partial | non-null | 0 | 9 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v12-development-candidate-01/q004__RqzMc4Q` | q004 | partial | non-null | 1 | 8 | — | 7 | 0.760667 |
| `raw/20260724-tika-mallet-tantivy-v13-development-candidate-01/q002__JKaTWqs` | q002 | partial | non-null | 1 | 8 | — | 5 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v13-development-candidate-01/q003__9RxyPk8` | q003 | partial | non-null | 1 | 9 | — | 7 | 0.798232 |
| `raw/20260724-tika-mallet-tantivy-v13-development-candidate-01/q004__DpueGfL` | q004 | partial | non-null | 1 | 14 | — | 11 | 0.943032 |
| `raw/20260724-tika-mallet-tantivy-v14-development-candidate-01/q002__UN7N8Bi` | q002 | partial | non-null | 1 | 8 | — | 2 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v14-development-candidate-01/q003__we7toSx` | q003 | partial | non-null | 1 | 10 | — | 7 | 0.782572 |
| `raw/20260724-tika-mallet-tantivy-v14-development-candidate-01/q004__x6X5JBs` | q004 | partial | non-null | 1 | 7 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v15-development-candidate-01/q002__hnXKesc` | q002 | partial | non-null | 1 | 7 | — | 3 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v15-development-candidate-01/q003__JfnXg59` | q003 | partial | non-null | 1 | 10 | — | 8 | 0.851687 |
| `raw/20260724-tika-mallet-tantivy-v15-development-candidate-01/q004__rwH2dRE` | q004 | partial | non-null | 1 | 7 | — | 7 | 0.799041 |
| `raw/20260724-tika-mallet-tantivy-v16-development-candidate-01/q002__nbas6Bd` | q002 | partial | non-null | 1 | 10 | — | 6 | 0.787529 |
| `raw/20260724-tika-mallet-tantivy-v16-development-candidate-01/q003__xpJap6u` | q003 | partial | non-null | 1 | 6 | — | 4 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v16-development-candidate-01/q004__gtxRpNc` | q004 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v17-development-candidate-01/q002__h8YAEjt` | q002 | partial | non-null | 1 | 6 | — | 1 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v17-development-candidate-01/q003__JyVtjr6` | q003 | partial | non-null | 1 | 6 | — | 4 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v17-development-candidate-01/q004__uApz4Rs` | q004 | partial | non-null | 1 | 11 | — | 9 | 0.873012 |
| `raw/20260724-tika-mallet-tantivy-v18-development-candidate-01/q002__X5fydxu` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.804378 |
| `raw/20260724-tika-mallet-tantivy-v18-development-candidate-01/q003__Vo5c64Z` | q003 | partial | non-null | 1 | 7 | — | 3 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v19-development-candidate-01/q002__dj28UPF` | q002 | partial | non-null | 1 | 8 | — | 7 | 0.899559 |
| `raw/20260724-tika-mallet-tantivy-v19-development-candidate-01/q003__RgjtZVL` | q003 | partial | non-null | 1 | 8 | — | 6 | 0.593990 |
| `raw/20260724-tika-mallet-tantivy-v19-development-candidate-01/q004__Z9Ahf2h` | q004 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v20-development-candidate-01/q002__3295tXQ` | q002 | partial | non-null | 1 | 8 | — | 7 | 0.904819 |
| `raw/20260724-tika-mallet-tantivy-v20-development-candidate-01/q003__q2fkXaq` | q003 | partial | non-null | 0 | 7 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v21-development-candidate-01/q002__6YTzLsn` | q002 | partial | non-null | 0 | 7 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v21-development-candidate-01/q003__FV7g9vj` | q003 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v21-development-candidate-01/q004__SzQxMYj` | q004 | partial | non-null | 1 | 15 | — | 11 | 0.957612 |
| `raw/20260724-tika-mallet-tantivy-v22-development-candidate-02/q002__YCbnwcn` | q002 | partial | non-null | 1 | 8 | — | 5 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v22-development-candidate-02/q003__G664wbW` | q003 | partial | non-null | 1 | 6 | — | 3 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v22-development-candidate-02/q004__iwFuJDx` | q004 | partial | non-null | 1 | 13 | — | 9 | 0.849576 |
| `raw/20260724-tika-mallet-tantivy-v23-development-candidate-02/q002__mw32b4Q` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.794442 |
| `raw/20260724-tika-mallet-tantivy-v23-development-candidate-02/q003__Qikawyn` | q003 | partial | non-null | 1 | 7 | — | 6 | 0.737121 |
| `raw/20260724-tika-mallet-tantivy-v23-development-candidate-02/q004__EvTDCLj` | q004 | partial | non-null | 0 | 8 | — | 7 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v24-development-candidate-01/q002__FbbgA9C` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.821706 |
| `raw/20260724-tika-mallet-tantivy-v24-development-candidate-01/q003__rtisM2b` | q003 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v24-development-candidate-01/q004__h6RwqF8` | q004 | partial | non-null | 1 | 9 | — | 8 | 0.690336 |
| `raw/20260724-tika-mallet-tantivy-v25-development-candidate-01/q002__cJZUyxk` | q002 | fail | null | 1 | 0 | — | 0 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v25-development-candidate-01/q003__bsotojk` | q003 | partial | non-null | 1 | 8 | — | 7 | 0.811745 |
| `raw/20260724-tika-mallet-tantivy-v25-development-candidate-01/q004__XD5acgs` | q004 | partial | non-null | 1 | 9 | — | 8 | 0.821440 |
| `raw/20260724-tika-mallet-tantivy-v26-development-candidate-01/q002__2h9niyq` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.822676 |
| `raw/20260724-tika-mallet-tantivy-v26-development-candidate-01/q003__76XqsQ6` | q003 | partial | non-null | 1 | 8 | — | 7 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v26-development-candidate-01/q004__g7NRfQE` | q004 | partial | non-null | 1 | 9 | — | 8 | 0.690336 |
| `raw/20260724-tika-mallet-tantivy-v27-development-candidate-01/q003__TXhYMMm` | q003 | partial | non-null | 1 | 8 | — | 7 | 0.795629 |
| `raw/20260724-tika-mallet-tantivy-v27-development-candidate-01/q004__KoD58YT` | q004 | fail | null | 1 | 0 | — | 0 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v28-clean-development-baseline-01/q002__C6GauaP` | q002 | partial | non-null | 1 | 8 | — | 3 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v28-clean-development-baseline-01/q003__gEFQnha` | q003 | partial | non-null | 1 | 10 | — | 8 | 0.861037 |
| `raw/20260724-tika-mallet-tantivy-v28-clean-development-baseline-01/q004__oEPgEJ9` | q004 | partial | non-null | 1 | 11 | — | 7 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v32-clean-development-candidate-01/q002__LnJbSpS` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v32-clean-development-candidate-01/q003__yd8DHpW` | q003 | partial | non-null | 1 | 8 | — | 7 | 0.795629 |
| `raw/20260724-tika-mallet-tantivy-v32-clean-development-candidate-01/q004__gjKY5Tr` | q004 | partial | non-null | 1 | 9 | — | 7 | 0.733706 |
| `raw/20260724-tika-mallet-tantivy-v33-opaque-concept-path-development-candidate-01/q002__zgHt4Yd` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.813120 |
| `raw/20260724-tika-mallet-tantivy-v33-opaque-concept-path-development-candidate-01/q003__DrZ85he` | q003 | partial | non-null | 1 | 8 | — | 7 | 0.808851 |
| `raw/20260724-tika-mallet-tantivy-v33-opaque-concept-path-development-candidate-01/q004__mfhGqUx` | q004 | partial | non-null | 1 | 9 | — | 7 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v34-minimum-target-development-candidate-01/q002__rr38ccB` | q002 | partial | non-null | 1 | 6 | — | 4 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v34-minimum-target-development-candidate-01/q003__Qm3zAfh` | q003 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v34-minimum-target-development-candidate-01/q004__EegtA3m` | q004 | partial | non-null | 1 | 7 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v35-shape-aware-transport-development-candidate-01/q002__aYGhpJd` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v35-shape-aware-transport-development-candidate-01/q003__H2kUJzT` | q003 | partial | non-null | 1 | 8 | — | 7 | 0.808851 |
| `raw/20260724-tika-mallet-tantivy-v35-shape-aware-transport-development-candidate-01/q004__QEeUbMx` | q004 | partial | non-null | 1 | 9 | — | 7 | 0.733706 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q005__teubYqY` | q005 | partial | non-null | 1 | 6 | — | 3 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q010__Gq8U6DX` | q010 | partial | non-null | 1 | 9 | — | 6 | 0.785142 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q015__CZWMyic` | q015 | partial | non-null | 1 | 6 | — | 3 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q020__QbXNAtt` | q020 | partial | non-null | 1 | 7 | — | 3 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q025__xyHcZJi` | q025 | partial | non-null | 0 | 10 | — | 1 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-baseline-01/q029__tTgMEsL` | q029 | partial | non-null | 1 | 6 | — | 5 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q005__rTEm6MW` | q005 | partial | non-null | 1 | 6 | — | 2 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q010__fGXdzkM` | q010 | partial | non-null | 1 | 8 | — | 4 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q015__R2jd2ZE` | q015 | partial | non-null | 1 | 7 | — | 5 | 0.800281 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q020__QoDNZm6` | q020 | fail | null | 1 | 0 | — | 0 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q025__eqtN4V6` | q025 | partial | non-null | 1 | 6 | — | 1 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-holdout-candidate-01/q029__uUQrgJr` | q029 | partial | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/20260724-tika-mallet-tantivy-v36-opaque-identity-suffix-development-candidate-01/q002__ooCvVJQ` | q002 | partial | non-null | 1 | 8 | — | 6 | 0.818615 |
| `raw/20260724-tika-mallet-tantivy-v36-opaque-identity-suffix-development-candidate-01/q003__xQYbvtR` | q003 | partial | non-null | 1 | 8 | — | 7 | 0.795629 |
| `raw/20260724-tika-mallet-tantivy-v36-opaque-identity-suffix-development-candidate-01/q004__vy2CWRx` | q004 | partial | non-null | 1 | 9 | — | 7 | 0.733706 |
| `raw/adaptive-discovery/q002__soewiqK` | q002 | partial | non-null | 1 | 12 | — | 5 | 0.000000 |
| `raw/adaptive-discovery/q003__evBKRLQ` | q003 | partial | non-null | 1 | 7 | — | 2 | 0.287202 |
| `raw/adaptive-holdout/q010__KqryTJk` | q010 | partial | non-null | 1 | 9 | — | 5 | 0.572781 |
| `raw/adaptive-holdout/q015__FHVbQZU` | q015 | partial | non-null | 0 | 11 | — | 5 | 0.000000 |
| `raw/adaptive-holdout/q025__XyHgrki` | q025 | partial | non-null | 0 | 18 | — | 3 | 0.000000 |
| `raw/classical-discovery/q003__Rnv36DN` | q003 | partial | non-null | 1 | 15 | — | 2 | 0.000000 |
| `raw/classical-holdout/q005__7mhMq98` | q005 | partial | non-null | 1 | 14 | — | 2 | 0.655944 |
| `raw/classical-holdout/q010__WfBS95N` | q010 | partial | non-null | 1 | 9 | — | 5 | 0.746641 |
| `raw/classical-holdout/q020__aXVDZbf` | q020 | partial | non-null | 1 | 9 | — | 4 | 0.000000 |
| `raw/classical-holdout/q025__fxvE4Qw` | q025 | partial | non-null | 1 | 16 | — | 1 | 0.000000 |
| `raw/classical-holdout/q029__ccGGwUz` | q029 | partial | non-null | 1 | 7 | — | 2 | 0.357524 |
| `raw/development-candidate-01-0b7b8af34f/q002__KkaHjZy` | q002 | not-reviewed | non-null | 1 | 8 | — | 6 | 0.821706 |
| `raw/development-candidate-01-0b7b8af34f/q003__3nLLfvF` | q003 | not-reviewed | non-null | 1 | 8 | — | 7 | 0.811745 |
| `raw/development-candidate-01-0b7b8af34f/q004__z6QVDZu` | q004 | not-reviewed | null | 1 | 0 | — | 0 | 0.000000 |
| `raw/development-candidate-01-1685aeb983/q002__LwwvhVk` | q002 | not-reviewed | non-null | 1 | 8 | — | 6 | 0.821706 |
| `raw/development-candidate-01-1685aeb983/q003__CFPMaop` | q003 | not-reviewed | non-null | 1 | 8 | — | 7 | 0.813768 |
| `raw/development-candidate-01-1685aeb983/q004__GrDpiFm` | q004 | not-reviewed | non-null | 1 | 9 | — | 7 | 0.733706 |
| `raw/development-candidate-01-bf3233d5a7/q002__Ctc7KWQ` | q002 | not-reviewed | non-null | 1 | 8 | — | 6 | 0.821706 |
| `raw/development-candidate-01-bf3233d5a7/q003__PNjxahX` | q003 | not-reviewed | non-null | 1 | 8 | — | 7 | 0.795629 |
| `raw/development-candidate-01-bf3233d5a7/q004__CMPFCMU` | q004 | not-reviewed | null | 1 | 0 | — | 0 | 0.000000 |
| `raw/development-candidate-01-dcc6a3b78f/q002__Ak5SbZS` | q002 | not-reviewed | non-null | 1 | 8 | — | 6 | 0.672087 |
| `raw/development-candidate-01-dcc6a3b78f/q003__2yTyghh` | q003 | not-reviewed | non-null | 1 | 8 | — | 7 | 0.671260 |
| `raw/development-candidate-01-dcc6a3b78f/q004__uHFiPa9` | q004 | not-reviewed | non-null | 1 | 9 | — | 7 | 0.765708 |
| `raw/development-candidate-01-e778c5bfd4/q002__SubYSQ4` | q002 | not-reviewed | non-null | 1 | 8 | — | 6 | 0.000000 |
| `raw/development-candidate-01-e778c5bfd4/q003__jPv2UtN` | q003 | not-reviewed | non-null | 1 | 8 | — | 7 | 0.795629 |
| `raw/development-candidate-01-e778c5bfd4/q004__wT2pNNc` | q004 | not-reviewed | non-null | 1 | 9 | — | 8 | 0.813295 |
| `raw/embeddings-discovery/q003__XUq7zEQ` | q003 | partial | non-null | 1 | 14 | — | 2 | 0.477686 |
| `raw/embeddings-holdout/q005__YyjSfDs` | q005 | partial | non-null | 1 | 14 | — | 4 | 0.000000 |
| `raw/embeddings-holdout/q010__Tbfcz9S` | q010 | partial | non-null | 1 | 14 | — | 6 | 0.840103 |
| `raw/embeddings-holdout/q025__2XTrhpu` | q025 | partial | non-null | 0 | 6 | — | 1 | 0.000000 |
| `raw/entity-graph-holdout/q015__2ScZo2o` | q015 | partial | non-null | 0 | 10 | — | 5 | 0.000000 |
| `raw/entity-graph-holdout/q020__pm88Gir` | q020 | partial | non-null | 0 | 5 | — | 4 | 0.000000 |
| `raw/entity-graph-holdout/q025__hws9bNQ` | q025 | partial | non-null | 1 | 6 | — | 2 | 0.000000 |
| `raw/legacy-discovery/q001__rTbcCiF` | q001 | partial | non-null | 0 | 41 | — | 14 | 0.000000 |
| `raw/legacy-discovery/q002__4zz7Ev2` | q002 | partial | non-null | 0 | 33 | — | 6 | 0.000000 |
| `raw/legacy-discovery/q004__8weRpp4` | q004 | partial | non-null | 0 | 11 | — | 4 | 0.000000 |
| `raw/legacy-discovery/q007__V3TjcCH` | q007 | partial | non-null | 0 | 18 | — | 4 | 0.000000 |
| `raw/legacy-holdout/q005__iNh7Frt` | q005 | partial | non-null | 0 | 14 | — | 4 | 0.000000 |
| `raw/legacy-holdout/q010__67E5SRG` | q010 | partial | non-null | 0 | 8 | — | 2 | 0.000000 |
| `raw/legacy-holdout/q015__pDEQ5G8` | q015 | partial | non-null | 0 | 10 | — | 5 | 0.000000 |
| `raw/turso-holdout/q005__U6wVt9C` | q005 | partial | non-null | 0 | 22 | — | 3 | 0.000000 |
| `raw/turso-holdout/q010__rf8BN2S` | q010 | partial | non-null | 0 | 10 | — | 3 | 0.000000 |
| `raw/turso-holdout/q015__3MyZE8q` | q015 | partial | non-null | 0 | 12 | — | 5 | 0.000000 |
| `raw/turso-holdout/q020__HCMuVsV` | q020 | partial | non-null | 0 | 30 | — | 4 | 0.000000 |
| `raw/turso-holdout/q025__k2Fs7Ee` | q025 | partial | non-null | 0 | 20 | — | 4 | 0.000000 |
| `raw/turso-holdout/q029__uTdWPsh` | q029 | partial | non-null | 0 | 13 | — | 5 | 0.000000 |

Each response row has a separate semantic verdict and retains its mechanical observations. Detailed rationales are in the companion JSON report. Historical adjudications recovered by trial id retain their original rationale without inventing unavailable payloads.
