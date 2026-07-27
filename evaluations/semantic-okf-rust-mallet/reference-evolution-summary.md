# RustMallet Reference Evolution Summary

## Outcome

The processed RustMallet snapshot now has a deterministic reference-dictionary
contract. `classical/references.json` maps 1,135 compact IDs to the seven exact
evidence identity fields and is validated before consultation. The selected
consult skill returns only those IDs; deterministic verifier code expands them
when a legacy exact-evidence schema is required.

The reference-aware consultant's Harbor bundle digest was
`637af0aefb44de8bf24fffb246158c9db6a8e9bdfb6780150ca6f043cc965a6d`.
That staged bundle contained four ignored `__pycache__` files. After removing
bytecode, the clean live source digest is
`a86ced363990095d62ca8e413e5fc881aed08f0cdb21acb905da4f5c9600ccff`;
all 11 non-bytecode files match the evaluated parent exactly. A later
one-command consultant candidate regressed on sealed holdout and was rejected.

The native builder candidate passed development and all required holdout gates,
including reference resolution, but its semantic reward decreased by 0.00243.
Because both holdout task cells regressed, the strict gate decided
`keep-baseline`. The native candidate remains under `evolution-assets/builder/`
and was not promoted into the live evolved builder skill.

## Exact-reference contract

- Artifact: `classical/references.json`
- Algorithm: `exact-evidence-reference-dictionary-v1`
- ID shape: `ref-[0-9a-f]{24}`
- Entries: 1,135
- Bytes: 730,707
- SHA-256: `886c3ba3ffb99c8f6a44ae8029e8792bfcf813ed80d59373ea2c2fe86033db3f`

IDs are derived from canonical JSON containing source ID, record ID, concept
path, source path, record SHA-256, exact locator, and text SHA-256. Validation
rejects stale IDs, collisions, duplicate document bindings, mixed compact and
legacy rows, unknown references, and modified evidence.

## Harbor results

The builder candidate digest was
`cc32ea3e3342ff41ea2b029c7b801a171461d046d1d4d48a61f5137a0a2cf0a5`;
the frozen baseline digest was
`3a4bf469bd005862e3874d411988df8a2b1697150bcd8fb9bf5ac464cb0a91f9`.

Development passed 2/2 tasks with zero errors. The sealed holdout used q010 and
q029, two attempts per task, fixed Pi 0.73.1 / `gpt-5.3-codex-spark`, and no
Harbor retries. Every candidate trial passed `quality_gate=1` and
`reference_dictionary_resolution=1`.

| Cell | Baseline mean | Candidate mean | Delta |
| --- | ---: | ---: | ---: |
| q010 | 0.839808 | 0.838940 | -0.000868 |
| q029 | 0.791155 | 0.787166 | -0.003989 |
| Overall | 0.815482 | 0.813053 | -0.002429 |

The gate was evaluable, retry-contract verified, and error-free. Its decision
was `keep-baseline` because task regressions were not allowed.

## One-command builder distillation

A second builder campaign combined native reference-dictionary publication
with one build-and-independent-validation command. The isolated candidate
digest was
`381e79b5d50001e139bd48b0c30000232e18ce0124f2de5484b591e69d6b2372`;
the frozen live baseline was
`af3b51512084a0d02d12b26d9823c6db1aad50337977e8ed9b403cbafa897af9`.

Two local builds produced byte-identical 891-file trees with exactly seven
classical artifacts, 1,135 references, and tree digest
`8aeff450b0c132b994dae5cfd51fe87718482155e71764482cbbfdc289654ae9`.
Harbor development passed q007 and q019 at 100%, with zero errors and both
required gates at 1.0.

The untouched q015/q025 holdout used two attempts per task:

| Cell | Baseline mean | Candidate mean | Delta |
| --- | ---: | ---: | ---: |
| q015 | 0.130812 | 0.127488 | -0.003324 |
| q025 | 0.467333 | 0.557208 | +0.089874 |
| Overall | 0.299073 | 0.342348 | +0.043275 |

The candidate was faster: mean end-to-end trial wall time fell from 262.25 to
244.97 seconds, a 6.59% reduction. The distiller nevertheless decided
`keep-baseline` because the frozen rule required no task regression in addition
to a mean gain of at least 0.01, zero errors, and complete required gates. The
q015 regression is non-compensating, so the candidate remains isolated.

## Deterministic validation

Two clean native Linux builds produced byte-identical 891-file trees. A same-
platform original builder followed by deterministic reference backfill produced
the exact same tree. The inventory digest was
`05864991584a4ef5b000bdbe9059a649b7d25a2b29d2b0c22286f30b496ec9d7`.

The full canonical 40-question retrieval comparison ran BM25, topic,
association, and fusion at top-k 10 and 100. All 320 original/evolved payload
pairs matched after removing only the added `reference_id` member. The run
resolved 7,267 returned rows, exercised 728 unique IDs, used deep validation,
and found zero mismatches.

A fresh canonical candidate run then measured the reference-aware routes
directly. The Top-10 evaluator took 44,746.75 ms including 12,150.39 ms of
shared deep validation. Route P95 latency was 226.69 ms for BM25, 238.70 ms for
topic, 224.30 ms for association, and 232.25 ms for fusion. The independent
pool-100 evaluator took 48,463.00 ms. The results are now included as
experimental comparator rows in the general direct-retrieval table; RustMallet
remains outside the eight-family Harbor registry.

## Platform note

Fixed-seed RustMallet output was byte-identical within Linux and within the
previous Windows experiment, but Windows and Linux topic artifacts differed.
The native-versus-backfill equality claim therefore uses identical Linux inputs,
dependencies, and runtime rather than comparing across operating systems.
