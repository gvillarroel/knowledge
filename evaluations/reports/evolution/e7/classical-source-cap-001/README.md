# Classical: an unchanged ranking and an application-level diversity limit

Candidate-015 is a qualified exact tie with retained candidate-011 at **60.097820% weighted nDCG@10**. It changes relevance weight to `1.0` and both novelty weights to zero. The primary fusion route returns identical ordered record IDs for all 120 development questions. It is the first miss of the relevance-diversity mechanism, and candidate-011 remains retained.

The two native plans have different SHA-256 digests, confirming that the tested setting reached the original agent response. All case metric dictionaries are identical on all four routes. BM25 has identical ordered hits on every question; association changes only order for one question; topic changes the hit set for one question. These diagnostic changes do not change their case scores. Both jobs have evidence integrity 1.0, no native errors and no retries.

## Observed structural limit

The frozen Classical plan sets `max_per_evidence_identity=1`, a candidate pool of 100 and a result budget of ten. The native diversity function groups by `paper_id` when present and otherwise by `source_id`. In this corpus, source IDs identify the nine applications. All 6,000 native record identities were matched to the frozen raw inputs. A metadata scan using the native paper pattern found no matches, including a conservative scan of upstream paths.

Consequently, the three diversified routes return at most one document per application and at most nine documents overall. Setting novelty weights to zero leaves this cap active. BM25 bypasses this diversity function and returns ten documents for all 120 questions.

| Retained candidate-011 route | 5 hits | 6 hits | 7 hits | 8 hits | 9 hits | 10 hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| association | 1 | 10 | 28 | 46 | 35 | 0 |
| bm25 | 0 | 0 | 0 | 0 | 0 | 120 |
| fusion | 1 | 10 | 28 | 45 | 36 | 0 |
| topic | 1 | 11 | 29 | 44 | 35 | 0 |

Of the 112 eligible development questions, **24 require multiple reference documents from the same application**. Their category population weights sum to 63.333333 of the 470 eligible population weight. Across these questions, 79 reference occurrences lie beyond the first reference in an application group. The current cap prevents selecting all references in those groups.

Those 79 occurrences are a structural count, not an estimated score gain or a count of recoverable hits. The count does not subtract the independent top-ten limit. Candidate-pool coverage, rank order and result deduplication can also prevent recovery. No changed-cap or changed-identity candidate has been built or scored.

## Follow-up and study boundary

The current E7 catalog varies relevance and novelty weights while keeping the candidate pool and identity cap fixed. Its eventual catalog exhaustion therefore cannot establish exhaustion of all knowledge-evolution opportunities. Keep the live study unchanged and carry this newly observed opportunity into a separately registered, digest-bound follow-up.

Two separate hypotheses are ready for protocol design: a plan-only cap sweep with an unchanged consultant, and a consultation-only correction that distinguishes application grouping from authoritative document identity. Do not combine those mutations in one treatment. The latter must retain exact source/record/locator/hash evidence and deduplicate repeated passages of the same document without merging independent documents.

A four-operator knowledge-expertise plan was generated and deterministically verified against the complete retained 252-file target and sanitized development evidence. It includes coverage expansion, conservative retention, evidence-copy integrity and early-rank calibration. Only coverage expansion is attached to the demonstrated gap; the remaining operators are portfolio preservation or dimension-coverage suggestions, not newly demonstrated failures.

The plan is **planned-fitness-unverified**. No fresh independent validation is reserved for this follow-up, so it declares validation unavailable and promotion ineligible. The existing E7 private gate remains sealed and reserved for the original joint bundle. See the [reviewed handoff](plan-review.md) for the planner wording limitation and required next steps.

Scope: original 120-question stratified development evidence over 6,000 reference-enriched documents. No new native trial, language-model call, private feedback, all-500 result, candidate creation, profile promotion or public leaderboard claim is introduced here.

[Exact aggregates and source digests](aggregate.json) · [Retained Classical gain](../classical-progress-006/README.md) · [Campaign](../README.md)
