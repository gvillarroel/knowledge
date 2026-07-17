# Astro Benchmark Contract

The benchmark contains 40 frozen English questions:

- `q001` through `q020`: direct documentation questions;
- `q021` through `q030`: cross-document synthesis questions; and
- `q031` through `q040`: hard questions requiring exclusions, conditions, contrasts, or multi-document joins.

`question-specs.json` is the reviewed authoring source. Generated consultation input is `retrieval-questions.jsonl`; `hard-questions.jsonl` is its exact `q031`-`q040` subset. Qrels contain sorted canonical route IDs and opaque manifest source IDs, and are never included in the consultation prompt.

## Evidence-first hard-question workflow

Each hard question was written only after the relevant pinned MDX sections were identified and the intended answer was decomposed. Its ground truth records:

- at least four atomic answer claims;
- at least two important negatives;
- at least two explicit join, contrast, partition, ordering, inversion, or conditional derivations;
- acceptable variants and concrete failure conditions; and
- at least two authoritative pages, with each selected section bound by path, source ID, document route, heading path, character interval, file SHA-256, and selected-text SHA-256.

The generator resolves an exact heading and occurrence. Missing or ambiguous selections fail generation. The independent validator reopens the checked MDX, verifies the interval starts at the declared heading, recomputes both hashes, checks all claim and negative evidence references, and requires every atomic answer claim to participate in the explicit derivation.

## Scoring separation

Retrieval evaluation should report page-level precision, recall, reciprocal rank, nDCG, and complete-qrel coverage separately for direct, cross-document, and hard subsets. Actual hard answers should then be evaluated independently for atomic claim correctness and completeness, important-negative compliance, grounding, evidence validity, and response-contract compliance. A page hit alone must not receive answer credit.
