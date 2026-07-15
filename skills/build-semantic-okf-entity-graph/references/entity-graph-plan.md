# Entity-Graph Plan

The JSON plan is closed and versioned as `1.0`. Unknown or missing members fail.

## Selection

Declare sorted, unique `paper_source_ids`, `claim_source_ids`, and one `vocabulary_source_id`. The groups cannot overlap. Every selected source must exist and produce records. Paper sources must each produce exactly one paper record; claims must be reviewed; vocabulary records must be paper-specific methods or analysis dimensions.

## Sectioning and tokens

`sectioning.strategy` is `pdf-page-headings-v1`. Each `## PDF page N` heading begins an exact character-range section. Trailing whitespace is excluded by moving the range end, never by changing section text.

`tokenization` fixes the ASCII alphanumeric tokenizer, the bundled English stopword set, and minimum token length. This same contract drives candidate extraction, mentions, BM25, and query resolution.

## Candidate extraction

The n-gram range, section-frequency floor, maximum section fraction, global cap, and per-section cap are explicit. Salient n-grams are selected deterministically from corpus counts and inverse section frequency. They are `candidate-phrase` nodes, not accepted entities.

## Graph and query

The graph plan bounds entities considered per section, co-mention frequency, neighbors, and retained evidence sections. Query settings bound resolved entities, traversal hops, reviewed and candidate edge weights, hop decay, mention weight, candidate pool, paper diversity, and reciprocal-rank-fusion constant.

Candidate edge weight must remain lower than reviewed edge weight in reviewed production plans. Parameter changes create a new derived projection; they never change the authoritative core.
