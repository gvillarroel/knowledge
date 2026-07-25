# GraphRAG 40-question response and coverage audit

## Scope correction

The canonical dataset contains **40 questions**. The earlier 18-response report was a v36 evidence slice, not the complete dataset.

This audit inventories 143 complete raw Harbor responses and 32 additional historical responses with preserved manual adjudications: **175 reviewable responses**.

Only **29/40 questions** have a complete response. Missing: `q028`, `q031`, `q032`, `q033`, `q034`, `q035`, `q036`, `q037`, `q038`, `q039`, `q040`.

`q002`-`q004` account for 97/143 raw responses (67.8%), so the archive is iteration-heavy rather than question-balanced.

Semantic adjudications: 3 pass, 168 partial, and 4 fail. Mechanical reward is not used as semantic correctness.

**Full-dataset claim eligible:** `false`.

The 60 older comparison cells are retained as summary-only evidence; their response bodies are absent, so they are not silently counted as individually reviewable responses.

## Every question

| Question | Cohort | Focus docs | Minimum | Semantic targets | Raw | Historical | Total | Coverage |
|---|---|---:|---:|---:|---:|---:|---:|---|
| q001 | discovery | 15 | 8 | 4 | 2 | 1 | 3 | covered |
| q002 | discovery | 8 | 6 | 4 | 33 | 2 | 35 | covered |
| q003 | discovery | 10 | 6 | 4 | 34 | 3 | 37 | covered |
| q004 | discovery | 11 | 7 | 4 | 30 | 1 | 31 | covered |
| q005 | holdout | 5 | 4 | 4 | 6 | 4 | 10 | covered |
| q006 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q007 | discovery | 5 | 4 | 4 | 1 | 1 | 2 | covered |
| q008 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q009 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q010 | holdout | 8 | 6 | 4 | 4 | 5 | 9 | covered |
| q011 | discovery | 7 | 5 | 4 | 1 | 0 | 1 | covered |
| q012 | discovery | 9 | 6 | 4 | 1 | 0 | 1 | covered |
| q013 | discovery | 8 | 6 | 4 | 1 | 0 | 1 | covered |
| q014 | discovery | 10 | 7 | 4 | 1 | 0 | 1 | covered |
| q015 | holdout | 7 | 5 | 4 | 4 | 4 | 8 | covered |
| q016 | discovery | 10 | 7 | 4 | 1 | 0 | 1 | covered |
| q017 | discovery | 8 | 6 | 4 | 1 | 0 | 1 | covered |
| q018 | discovery | 9 | 6 | 4 | 1 | 0 | 1 | covered |
| q019 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q020 | holdout | 7 | 5 | 4 | 4 | 3 | 7 | covered |
| q021 | discovery | 7 | 5 | 4 | 1 | 0 | 1 | covered |
| q022 | discovery | 6 | 5 | 4 | 1 | 0 | 1 | covered |
| q023 | discovery | 15 | 8 | 5 | 1 | 0 | 1 | covered |
| q024 | discovery | 14 | 8 | 4 | 1 | 0 | 1 | covered |
| q025 | holdout | 5 | 4 | 4 | 4 | 5 | 9 | covered |
| q026 | discovery | 9 | 6 | 4 | 1 | 0 | 1 | covered |
| q027 | discovery | 5 | 4 | 4 | 1 | 0 | 1 | covered |
| q028 | discovery | 8 | 6 | 4 | 0 | 0 | 0 | missing |
| q029 | holdout | 9 | 6 | 4 | 3 | 3 | 6 | covered |
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
| `historical/20260717-papers-consult-gpt53-spark-01/07e23ace-ace3-4778-acdc-9e957c2f7655` | q002 | partial | non-null | 1 | 12 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/1f43edb2-1a69-4161-bcd7-159b88afd6e6` | q001 | partial | non-null | 0 | 41 | — | 14 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/33e5217c-f174-4297-861b-c0fc50e250ee` | q005 | partial | non-null | 0 | 22 | — | 3 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/3532b336-16ad-463d-b774-7be5f751dc23` | q003 | partial | non-null | 1 | 15 | — | 2 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/3aed67ca-ce2d-49a8-879d-fba45213f6b1` | q020 | partial | non-null | 0 | 30 | — | 4 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/50a09529-f8dd-480e-9096-58073d5a5790` | q005 | partial | non-null | 1 | 14 | — | 4 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/50a84566-8a52-485b-a4ce-0ef6dcb25ac7` | q025 | partial | non-null | 1 | 16 | — | 1 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/6713ac5f-bb88-490c-835e-231ced3d00f2` | q007 | partial | non-null | 0 | 18 | — | 4 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/6a6778a0-072b-4425-8d4d-ba625dd0814c` | q010 | partial | non-null | 0 | 8 | — | 2 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/6c7fc2d1-214d-4157-9ec2-56dce6d73e2b` | q029 | partial | non-null | 0 | 13 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/77721d26-ce40-4845-af14-896c886cfcc1` | q002 | partial | non-null | 0 | 33 | — | 6 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/821eac3a-5664-4afc-9872-601e03d69fbe` | q005 | partial | non-null | 1 | 14 | — | 2 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/8538428e-749f-4d1f-9e8e-5c360e0b23d3` | q015 | partial | non-null | 0 | 10 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/8573a931-850c-4c4f-b64b-50805a322091` | q015 | partial | non-null | 0 | 10 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/88f9aab6-cc81-4be2-8713-59b152d900cf` | q010 | partial | non-null | 0 | 10 | — | 3 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/8dc2313c-c8fc-4c40-90a1-30247668ab7b` | q015 | partial | non-null | 0 | 11 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/919b6b71-60e0-4b24-84a4-3785d1a8c4c3` | q029 | partial | non-null | 1 | 7 | — | 2 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/9b5c8868-e106-4272-a655-027783ada26d` | q029 | fail | non-null | 0 | 0 | — | 0 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/a13a5c9c-bec3-40fe-98cf-6b3d023ee00d` | q004 | partial | non-null | 0 | 11 | — | 4 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/a8a6e95c-5a95-48e7-8c53-9b9a68c443f0` | q003 | partial | non-null | 1 | 14 | — | 2 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/bfe9b1c6-d7d1-4ce6-80d5-4b32e04421be` | q025 | partial | non-null | 0 | 18 | — | 3 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/cce65ee3-f234-4331-9efd-57b22bd7f76e` | q005 | partial | non-null | 0 | 14 | — | 4 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/d0a6dc93-aca3-420a-8e4d-4250bd0a400c` | q020 | partial | non-null | 0 | 5 | — | 4 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/d67e3b79-00b8-4c72-8a9b-d8d398f0b0fe` | q025 | partial | non-null | 0 | 6 | — | 1 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/d9f2da6a-8d3b-4461-ba1e-b46acb956401` | q020 | partial | non-null | 1 | 9 | — | 4 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/dcfcb559-8558-4292-97df-2bc21735d581` | q010 | partial | non-null | 1 | 9 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/ddec4f09-7244-4f25-bc75-ce4d0e6da24e` | q015 | partial | non-null | 0 | 12 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/de4ec73d-1cd1-459e-93e9-5a03c48d392a` | q003 | partial | non-null | 1 | 7 | — | 2 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/e334f3c0-2f39-4da1-a572-845493b2ba57` | q010 | partial | non-null | 1 | 14 | — | 6 | 0.840103 |
| `historical/20260717-papers-consult-gpt53-spark-01/f143ca25-2b20-4f58-8a61-24855beefbac` | q025 | partial | non-null | 1 | 6 | — | 2 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/f1c0f025-d993-4df9-ad2c-db88baa80e5f` | q010 | partial | non-null | 1 | 9 | — | 5 | 0.000000 |
| `historical/20260717-papers-consult-gpt53-spark-01/f9b7358d-264f-4c2b-a75c-8da3b7c29446` | q025 | partial | non-null | 0 | 20 | — | 4 | 0.000000 |
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

Each response row has a separate semantic verdict and retains its mechanical observations. Detailed rationales are in the companion JSON report. Historical rows do not invent unavailable raw payloads.
