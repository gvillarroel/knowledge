# ADR 0071: Package trace-derived experts and rank their direct retrieval

## Status

Accepted on 2026-07-28.

## Context

ADR 0067 separates deterministic knowledge construction, reviewed domain
guidance, and standalone expert packaging. ADR 0070 promotes
`build-semantic-okf-tika-mallet` candidate `v46-qualified-runtime` after direct
builder development and holdout scores of `1.0`.

The consultation trace-distillation study also produced v39 and v42 proposal
evidence. V39 passed two of three development cases and v42 passed one of three;
neither passed its all-cases promotion gate and neither opened a qualified
holdout. Their accepted proposal content is useful experimental guidance, but
their historical grounded answers cannot support a promoted consultation skill
or a balanced answer-quality rank.

The generated expert query helper originally lacked the exact locator, text,
and text-hash fields required by the shared direct-retrieval evidence contract.
It also relied on the host console encoding and dynamic evaluation could create
Python bytecode inside an expert before its immutability snapshot.

The v46 builder correctly refuses a non-atomic publication. A Linux container
build directed at a Windows DrvFS bind mount reached publication and returned
`EINVAL` from `RENAME_NOREPLACE`; it left no partial destination. The same
network-disabled build published successfully on the container's native Linux
filesystem and passed an independent validation after being copied to the
workspace.

## Decision

Use the accepted v46 Tika/MALLET builder state as the builder provenance for
this study. Run its atomic publication on a native Linux filesystem, preserve
the build receipt, and independently validate any copied workspace projection.
Package two separate experimental expert skills:

- `graphrag-trace-expert-v39`, with full-question and exact-facet guidance;
- `graphrag-trace-expert-v42`, with the same retrieval anchor plus bounded
  evidence-union and response-integrity guidance.

Extend the generated query helper to emit exact record locators, authoritative
text, and SHA-256 text bindings, and to force UTF-8 CLI output. Prevent the
evaluator from writing bytecode into the expert and take the expert inventory
before dynamic loading.

Evaluate both experts on all 40 frozen `graphrag-papers-40` questions at Top 10
and pool 100. Admit one shared deterministic lexical row only after exact
cross-expert ranking replay, exact Top-10 prefixes, identical builder and
knowledge bindings, distinct guidance bindings, zero errors, and 100% exact
evidence validity.

The complete knowledge artifact contains 30 records: 15 papers and 15
reviewed-claim collections. Deduplicate the ranked records by authoritative
paper identity before applying the Top-10 budget.

The resulting row has 72.20% Recall@10, 80.07% MRR@10, 66.57% nDCG@10, and
170.78 ms selected P95. It is position 19 of 24 under the shared direct
retrieval contract.

Do not assign a grounded-answer rank. Preserve v39 and v42 as experimental
guidance because their historical Harbor development gates failed.

## Consequences

- Standalone experts now satisfy the exact direct-evidence contract and work on
  Windows consoles containing non-ASCII source text.
- The canonical audit proves deterministic retrieval replication across two
  independently packaged guidance variants and larger candidate pools.
- Cross-platform orchestration must not weaken the builder's atomic publication
  contract; DrvFS destinations are rejected and native Linux publication is
  validated before packaging.
- The direct rank measures the packaged lexical helper, not the quality impact
  of applying v39 or v42 guidance during model synthesis.
- A future grounded rank requires a new frozen, balanced Harbor campaign with
  complete responses and separate semantic review.
