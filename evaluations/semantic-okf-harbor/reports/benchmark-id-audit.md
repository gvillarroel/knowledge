# Semantic OKF Harbor benchmark ID and locator audit

Status: **PASS**.

## Conclusion

The expected IDs are coherent and all evaluator joins are valid. Question IDs are stable scoped ordinals (`q001`-`q040`); document IDs are canonical English Astro routes; source IDs are deterministic opaque IDs derived as `astro-doc-` plus the first 16 hexadecimal characters of SHA-256 over the document ID; and record IDs are derived from the pinned upstream MDX path. Qrel source and document arrays are validated as sets through the crosswalk, not paired by list position.

Hard evidence IDs, answer-claim IDs, and negative IDs are question-scoped ordinals (`qNNN-eK`, `qNNN-aK`, and `qNNN-nK`). Every reference resolves within its question.

## Coverage

| Check | Result |
|---|---:|
| Ordered question IDs | 40 (`q001`-`q040`) |
| Split membership | 24 train / 8 dev / 8 holdout; 0 overlap |
| Generated tasks matching benchmark rows | 40 / 40 |
| Qrel assignments | 80 |
| Distinct qrel source-to-ledger-to-crosswalk joins | 30 / 30 |
| Hard required ID sets equal to qrels | 10 / 10 |
| Real-grader unique evidence mappings | 46 / 46 |
| CRLF/CR line-ending normalizations used | 46 |
| EOF terminal-newline trims used | 8 |

The file and selected-text hashes are checked against raw authoritative bytes before newline normalization. The real Harbor grader then maps the normalized selection uniquely into the corresponding ledger record body. EOF-only publication newlines are trimmed only when the direct normalized join fails.

## Hard-question locator audit

| Question | Evidence | Unique grader mappings | Line-ending normalized | EOF trimmed | Required IDs = qrels |
|---|---:|---:|---:|---:|---|
| q031 | 3 | 3 | 3 | 0 | yes |
| q032 | 6 | 6 | 6 | 1 | yes |
| q033 | 5 | 5 | 5 | 0 | yes |
| q034 | 4 | 4 | 4 | 0 | yes |
| q035 | 4 | 4 | 4 | 1 | yes |
| q036 | 5 | 5 | 5 | 2 | yes |
| q037 | 4 | 4 | 4 | 2 | yes |
| q038 | 6 | 6 | 6 | 1 | yes |
| q039 | 4 | 4 | 4 | 0 | yes |
| q040 | 5 | 5 | 5 | 1 | yes |

## Interpretation

The IDs are evaluator identities, not relevance scores. A source ID is intentionally opaque, while its crosswalk document ID remains human-readable. Because each qrel source resolves to exactly one source-scoped ledger record and exactly one canonical document, the expected IDs are suitable for deterministic scoring. This audit validates identity, hashing, range integrity, and join uniqueness; it does not independently judge whether a benchmark question is pedagogically ideal or whether an answer semantically entails every claim.

The machine-readable companion contains every distinct qrel join and all 46 per-binding real-grader mapping receipts.
