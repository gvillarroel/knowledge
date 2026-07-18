# GraphRAG papers consultation strategy test log

This is the durable, append-only progress record for campaign `20260717-papers-consult-gpt53-spark-01`. Raw Harbor jobs, model traces, generated tasks, credentials, and built bundles remain ignored; this report records only reproducibility identities, validation outcomes, and compact aggregate checkpoints.

> **Current status: invalid for comparison.** The evaluator audit appended below supersedes the interpretation of `final-complete`. Earlier checkpoint prose is retained as historical evidence of what the original aggregator reported; it must not be read as a current ranking or winner declaration.

## Campaign contract

| Field | Value |
|---|---|
| Dataset | `graphrag-papers-40` |
| Mode | `consult-only` |
| Families | `adaptive`, `classical`, `embeddings`, `ensemble`, `entity-graph`, `graphify`, `legacy`, `turso` |
| Questions per family | 40: discovery 24, holdout 6, hard 10 |
| Expected live trials | 320 |
| Model | `openai-codex/gpt-5.3-codex-spark` |
| Pi | `0.73.1` |
| Thinking | `high` |
| Attempts | 1 |
| Concurrent jobs | 4 |
| Agent timeout | 600 seconds |
| Semantic retries | None |
| Knowledge mount | One family-specific built bundle, read-only at `/knowledge` |
| Installed skill | Exactly the matching consultation skill; no build skill |

Every family bundle was built once before live consultation. All eight bundles contain 874 authoritative records and share records SHA-256 `df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc`. Family-derived indexes differ and therefore have distinct complete-tree digests.

## Reproducibility identities

| Family | Bundle tree SHA-256 | Consultation skill tree SHA-256 |
|---|---|---|
| Adaptive | `4305743103e3a2de5d80f3c74edb34f90fcf7a4a795fd7ba5d43289b75d133d6` | `7e020f77c0d49cfa3c288d16998232947390cae3635be1fd7c22a0a922b629e7` |
| Classical | `832a84d16df88546bb87b4114a6dc79cb87ba57bc540992ed6b25e7b9151dea1` | `60812561265ca45669be58a36f75c1b07d544b2e9bd62d98ffb13f814c186b24` |
| Embeddings | `c1a70bee4acacdc11628d37abb4afeab34995b99ca06b3d1291ea43f6ae02420` | `79d73f91542835623e0b89a1250961ca9886b5c489bd8d5d003b38bd0a05c6d6` |
| Ensemble | `264acd347230b3a713da14ed208a28bb610157dc7c95d467e14512430332c6fa` | `f53bd380629426d7bd75fa343568c4f2cf3a2becec051b8379ccad1127b200b8` |
| Entity graph | `c203e5d4ccd0ca94859c6b1bd3d8c529134d7405214396463cd5e95464cc88d1` | `36034c508900ad25b364518c14be5c18187eec5debcdfef4f984f5e167749cf0` |
| Graphify | `8bf748d947b105a1f786b0f4c1df2dc5552260b290cf9960600fc55454828bf5` | `211ba5f504036a4c39bb66a29491c70e1d92603525dcfabea9ced68c867d2d00` |
| Legacy | `8f127d26cacded575478b7871e1031f73a849f98f92297631b93fc3f17b3d405` | `8e3412afc7690f2862073eb25ea5fa82736fb5b1c9f243585e6df704b850a8a7` |
| Turso | `b50a439dacac90517038124695339a6ee053d6b0a03bebe57c751b96f99f7dbd` | `9321a551020932f1f5f49d5f8a8064c65744c544bdcd3ba05adbda0da2280258` |

The shared runtime image is `semantic-okf-harbor-runtime:1.0`, image ID `sha256:1315195dcef58980e6d2620eaa41062ea6edc15c3eb8ed47d42c143be57aded5`, with requirements digest `2361f6b8e49cecea6ba1f5e676d54ed87c2b6279665a4a895a317de2896a57e8`. Runtime qualification confirmed `sentence-transformers==5.6.0`, `huggingface-hub==1.23.0`, `llama-index-core==0.14.23`, `graphifyy==0.9.17`, and `pyturso==0.6.1`.

## Validation log

| Stage | Outcome | Evidence |
|---|---|---|
| Dataset registry | Passed | Two registered 40-question datasets and eight matched strategy families validated. |
| Family builds | Passed | Eight one-time paper bundles built and published; all validators passed. |
| Task generation | Passed | Eight consult-only family trees generated for discovery, holdout, and hard cohorts. |
| Oracle and isolation validation | Passed | 320/320 structural oracles passed; deterministic regeneration, leak checks, hidden bindings, and mode isolation passed. |
| Runtime smoke | Passed | All eight consultation CLIs loaded with their pinned dependencies in the shared image. |
| Repository tests | Passed | 691 tests passed in 89.34 seconds. |
| Coverage gate | Passed | Total application coverage 90.9%; required minimum 80.0%. |
| Live holdout | Complete | 48/48 immutable one-attempt trials. |
| Live discovery wave 1 | Complete | 96/96 trials for Adaptive, Classical, Embeddings, and Legacy. |
| Live discovery wave 2 | Complete | 96/96 trials for Entity graph, Ensemble, Graphify, and Turso. |
| Live hard cohort | Complete | 80/80 immutable one-attempt trials. |
| Strict final aggregation | Passed | 320/320 results, 24/24 run receipts, no missing or duplicate questions, and one shared authoritative ledger digest. |

## Checkpoint 1: holdout complete

Recorded after all 48 holdout trials completed. Gate and contract rates use all six trials as their denominator; missing technical outcomes count as failures. Retrieval means use only trials where the verifier emitted the metric.

| Family | Trials | Reward mean | Gate | Contract | Technical failures | Precision | Recall | MRR | NDCG |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Classical | 6 | **0.293** | **3/6** | **5/6** | 1 | **0.900** | 0.404 | **0.900** | 0.508 |
| Embeddings | 6 | 0.140 | 1/6 | 2/6 | 2 | 0.482 | 0.438 | 0.750 | 0.506 |
| Adaptive | 6 | 0.095 | 1/6 | 1/6 | 3 | 0.461 | **0.646** | 0.319 | 0.472 |
| Turso | 6 | 0.000 | 0/6 | 0/6 | **0** | 0.709 | 0.603 | 0.889 | **0.659** |
| Legacy | 6 | 0.000 | 0/6 | 0/6 | 3 | 0.785 | 0.588 | 0.778 | 0.592 |
| Entity graph | 6 | 0.000 | 0/6 | 1/6 | 3 | 0.439 | 0.421 | 0.583 | 0.444 |
| Ensemble | 6 | 0.000 | 0/6 | 0/6 | 6 | — | — | — | — |
| Graphify | 6 | 0.000 | 0/6 | 0/6 | 6 | — | — | — | — |

Classical is the holdout leader. Turso retrieved useful material without runtime failures but did not satisfy the response contract or quality gate. Ensemble and Graphify timed out on every holdout trial.

## Checkpoint 2: discovery wave 1 complete

Recorded after the first four families completed all 24 discovery questions. The high verifier-error counts mainly represent responses that could not be scored under the strict output/evidence contract; they are retained as zero-reward outcomes rather than retried or discarded.

| Family | Trials | Reward mean | Gate | Contract | Technical failures | Failure types | Retrieval observations |
|---|---:|---:|---:|---:|---:|---|---:|
| Embeddings | 24 | **0.020** | 1/24 | 1/24 | 23 | Verifier 23 | 1 |
| Adaptive | 24 | 0.012 | 1/24 | **2/24** | 22 | Timeout 1; verifier 21 | 2 |
| Classical | 24 | 0.000 | 0/24 | 0/24 | 23 | Timeout 2; verifier 21 | 1 |
| Legacy | 24 | 0.000 | 0/24 | 0/24 | **20** | Verifier 20 | 4 |

These discovery results are not yet a complete eight-family comparison. They show that response serialization and verifier compatibility dominate this checkpoint: only 8 of 96 trials emitted retrieval metrics.

## Checkpoint 3: live progress snapshot

At `2026-07-17T15:37:17.9510206Z`, the campaign had 159/320 persisted results:

| Family/cohort | Completed |
|---|---:|
| Adaptive discovery | 24/24 |
| Classical discovery | 24/24 |
| Embeddings discovery | 24/24 |
| Legacy discovery | 24/24 |
| Entity graph discovery | 6/24 |
| Ensemble discovery | 6/24 |
| Graphify discovery | 2/24 |
| Turso discovery | 1/24 |
| All holdout | 48/48 |
| All hard | 0/80 |

## Checkpoint 4: discovery complete

Recorded at `2026-07-17T16:13:09.0235804Z` after all eight families completed 24/24 discovery trials, for 192/192 discovery results. Retrieval means remain observation-only; a dash means no trial emitted that metric.

| Family | Reward mean | Gate | Contract | Technical failures | Failure types | Retrieval observations |
|---|---:|---:|---:|---:|---|---:|
| Embeddings | **0.020** | 1/24 | 1/24 | 23 | Verifier 23 | 1 |
| Adaptive | 0.012 | 1/24 | **2/24** | **22** | Timeout 1; verifier 21 | 2 |
| Classical | 0.000 | 0/24 | 0/24 | 23 | Timeout 2; verifier 21 | 1 |
| Legacy | 0.000 | 0/24 | 0/24 | **20** | Verifier 20 | **4** |
| Ensemble | 0.000 | 0/24 | 0/24 | 24 | Verifier 24 | 0 |
| Entity graph | 0.000 | 0/24 | 0/24 | 24 | Verifier 24 | 0 |
| Graphify | 0.000 | 0/24 | 0/24 | 24 | Verifier 24 | 0 |
| Turso | 0.000 | 0/24 | 0/24 | 24 | Verifier 24 | 0 |

Across all eight strategies, discovery produced 2 quality-gate passes out of 192 trials. The wave-2 families produced structurally unscorable outputs in all 96 trials. This checkpoint therefore measures both retrieval behavior and strict response-protocol reliability; it must not be reduced to retrieval quality alone.

## Checkpoint 5: campaign complete

Recorded at `2026-07-17T16:44:59.2758597Z` after the strict aggregator accepted 320/320 trials. Gate and contract rates count all forty family trials; retrieval means use the smaller observed verifier denominator recorded in the final JSON report.

| Family | Reward mean | Gates | Contract | Technical failures | Failure types | Precision | Recall | MRR | NDCG |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Classical | **0.044** | **3/40** | **5/40** | 34 | Timeout 3; verifier 31 | **0.833** | 0.370 | **0.917** | 0.483 |
| Embeddings | 0.033 | 2/40 | 3/40 | 35 | Timeout 1; verifier 34 | 0.519 | 0.390 | 0.800 | 0.476 |
| Adaptive | 0.021 | 2/40 | 3/40 | 35 | Timeout 3; verifier 32 | 0.468 | 0.553 | 0.492 | 0.457 |
| Ensemble | 0.000 | 0/40 | 0/40 | 40 | Timeout 6; verifier 34 | — | — | — | — |
| Entity graph | 0.000 | 0/40 | 1/40 | 37 | Timeout 3; verifier 34 | 0.439 | 0.421 | 0.583 | 0.444 |
| Graphify | 0.000 | 0/40 | 0/40 | 40 | Timeout 6; verifier 34 | — | — | — | — |
| Legacy | 0.000 | 0/40 | 0/40 | **33** | Verifier 33 | 0.802 | **0.659** | 0.719 | 0.641 |
| Turso | 0.000 | 0/40 | 0/40 | 34 | Verifier 34 | 0.709 | 0.603 | 0.889 | **0.659** |

Classical is the final campaign leader by mean reward and quality-gate passes. Embeddings ranks second and Adaptive third. All 80 hard trials ended as verifier errors, so no strategy emitted observable hard-cohort retrieval or hard-evidence metrics. The primary campaign finding is therefore protocol reliability under strict evidence serialization, not only ranking quality when retrieval metrics happen to be available.

Final report artifacts:

- `20260717-papers-consult-gpt53-spark-01-final.md`, SHA-256 `af4b294df41ac70298c29fdf35de3b4f8e1dbaa1e96da2778832649a2eab8ee4`.
- `20260717-papers-consult-gpt53-spark-01-final.json`, SHA-256 `e26c40bac73edab1c8e360eb0d10e994acd399d8de16b1313770fde52f3f73e7`.

## Interpretation and update policy

- This is a live evaluation log, not a declaration of a final winner.
- No semantic retry is allowed. Agent timeouts, verifier errors, contract failures, and low semantic scores are all retained.
- The final comparison is accepted because every family has exactly 40 results and the strict summarizer accepted all 24 completed run receipts.
- Future reruns must append a new campaign record rather than rewriting these checkpoints after observing later results.
- The machine-readable companion file preserves exact unrounded checkpoint values for downstream analysis.

## Checkpoint 6: evaluator audit invalidated the comparison

Recorded at `2026-07-17T21:01:02Z` after manually inspecting the available answers and classifying every terminal Pi trace. This checkpoint supersedes the interpretation of `final-complete` without changing the raw Harbor jobs or the original final-report hashes.

The old aggregator proved only that 320 result directories and 24 receipts existed. It did not inspect terminal provider state. The actual disjoint terminal outcomes are:

| Terminal outcome | Trials | Evaluable answer response |
|---|---:|---:|
| Provider quota, `usage_limit_reached` | 254 | No |
| Provider context limit | 14 | No |
| Output length limit | 4 | No |
| Agent interrupted during tool work | 16 | No |
| Complete final response | 32 | Yes |

All 80 hard trials ended at the provider quota boundary. Ensemble and Graphify emitted no final response. Quota exhaustion began while family/cohort jobs were being scheduled in family blocks, so which strategies received actual model calls was order-biased. Provider and execution failures are no longer converted into semantic zeroes or labeled `VerifierError`.

The corrected campaign state is:

| Property | Value |
|---|---:|
| Result artifacts present | 320/320 |
| Structurally complete | Yes |
| Evaluable final responses | 32/320 |
| Provider clean | No |
| Evaluation complete | No |
| Ranking eligible | No |
| Winner | None |

### Grader corrections

1. Evidence objects now require the exact declared member set but not an undeclared property order. Classical q003 is the reproduced false negative: all 15 evidence rows and first-use references are valid after this correction.
2. The original q001–q030 `min_papers` thresholds and hidden `required_points` are restored from their pinned blueprint. The public task states the minimum; required points remain verifier-only.
3. The former `quality_gate` is split into `evidence_contract_gate`, `minimum_document_gate`, and `mechanical_qualification_gate`.
4. Hard metrics are named `answer_claim_anchor_coverage` and `important_negative_anchor_coverage`; exact evidence anchors do not prove that candidate statements entail the reviewed claims.
5. Terminal outcomes are classified as provider failure, agent execution failure, invalid complete response, scored response, or true verifier failure. Error headers and raw answer text are not serialized into reports.

All eight regenerated task families passed 40/40 corrected mechanical oracles, for 320/320 total.

Post-correction repository validation passed 1,826 tests with 10 skipped. The official application coverage gate passed 704 tests and reported 90.9% total application coverage against the required 80.0% minimum.

### Manual answer audit

Every one of the 32 complete final responses was reviewed against the original semantic rubric and relevant-document minimum:

| Manual outcome | Count |
|---|---:|
| Semantic pass | 0 |
| Semantic partial | 31 |
| Semantic fail | 1 |
| Minimum document threshold met | 11 |
| All required points covered | 1 |
| Hard responses available | 0 |

The single answer covering all required points, Adaptive q025, still cited only 3 of the required 4 relevant documents. Embeddings q010 was the only original gate pass to meet its paper minimum, but it covered only 1 of 4 required semantic points under the conservative review.

### Corrected artifacts

- Corrected forensic JSON: `20260717-papers-consult-gpt53-spark-01-audit-v2.json`, SHA-256 `a939a7f717df78c896bae42b125a9e708da106a12bcc0f6bb056df68b57d1d7e`.
- Corrected forensic Markdown: `20260717-papers-consult-gpt53-spark-01-audit-v2.md`, SHA-256 `a18553e6e3884003516eb0b34de5266ce7c4029d1f8c3d9880bd503063ef0d0e`.
- Complete manual review: `20260717-papers-consult-gpt53-spark-01-manual-review.md`, SHA-256 `c70254d8a9247c96a3663052df9d66f4f3fdfd9ca0f2de5a0ecf44ed164674b6`.

The historical `-final.json` and `-final.md` files remain preserved as the original flawed aggregation. They are superseded, not silently rewritten.

### Required next campaign

A replacement run must use the tracked balanced scheduler. It executes one question across rotating family waves, counts the first real trial as a synchronous quota preflight, stops submitting work on the first 429, and writes append-only one-task shards. No family ranking may be published until all eight families have 40 evaluable responses and semantic review is complete.

The schedule-only rehearsal for replacement campaign `20260717-papers-consult-gpt53-spark-02` produced the deterministic 320-cell schedule SHA-256 `f202c3c8744cc8259fddce586826768c90e896c8c180a0b2e96a0a88aaf70f7d` without making a model call. Live execution was not started while the audited credential remained at its provider usage limit.
