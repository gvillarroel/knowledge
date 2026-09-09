# Graphify: sealed construction-efficiency candidate

Snapshot: 2026-09-09 06:23 UTC. Preparation only; zero native candidate trials.

One complete candidate changes `_lexical_similarity_pairs` in the Graphify
builder asset. It keeps the best permitted neighbors while visiting record
pairs, avoiding repeated scans of a complete score map. Feature extraction,
global IDF, cosine arithmetic, partition rules, score/path ordering, mutual
edges and twelve-decimal scores remain subject to exact parity checks.

The candidate has 252 files and 78 directories. Exactly one file changed;
all other package bytes, including consultation and validation call sites,
match the frozen parent. The changed source compiles. The realizer ran skill
frontmatter validation and 150 exact synthetic edge comparisons in a disposable
copy, then sealed and independently verified the package receipts. Parent and
prepared bundle digests remained unchanged during validation.

| Binding | SHA-256 |
| --- | --- |
| Parent canonical realizer tree | `f7f8bbc2e94ca89404c22e0e6645714a72a016be6fefe4c44804f0f5531cbbc3` |
| Candidate canonical realizer tree | `b352ebab48148260e16ab43fd6ad0781e38ad39b1f11ff8be833a4ed7e61b8f8` |
| Mutation contract object | `a285bd46666e6b5ce176c49532d2e3944238cd1c8446ba80a52127a2e6ce7263` |
| Candidate manifest object | `072b91d056d0b38a2c03bc1b312fc86bc2f1689c894c211931f445112739c442` |
| Validation receipt object | `f6fc43a0fa85f5275cfcf181b28d5e341d2292203d799823f5acf708059da5b5` |
| Operator realization object | `0e096ea7681f877b46a48765a292e808a23e8c36b0c0d52126a3d7f3fcc79619` |

These are the realizer's canonical tree/object algorithms, not Harbor lock
digests or raw receipt-file hashes. Complete candidate and receipt files remain
ignored local preparation artifacts. The production skill has not been changed
or installed, and E8 does not load this candidate.

The [earlier synthetic microbenchmark](../graphify-scaling-001/README.md) measured
a 20.43-fold host function timing ratio on 800 short generated records. That
figure is not a complete-build speedup. The new package still needs independent
artifact/graph parity checks and a complete native feasibility trial. Its
existing validator uses the same changed function, so passing that validator
alone would not establish correctness independently.

A concrete native job proposal preserves the original task, agent, cache,
resources and attempt policy, changing only the job identity, output directory
and candidate skill source. Harbor 0.18 accepted it through `--print-config`
under WSL. This was configuration validation only: no study directory, trial,
runtime access probe or native candidate outcome was created.

[ADR 0132](../../../../../.specs/adr/0132-qualify-graphify-builder-before-consultation.md)
defines a separate fixed public feasibility study, followed by a versioned
reference for consultation optimization if feasibility passes. The original
[construction timeout](../graphify-baseline-failure-001/README.md) remains one
consumed failed attempt with unavailable retrieval quality. This preparation
does not claim fitness, selection, acceptance or permission for native dispatch.

[Exact preparation aggregate](aggregate.json) · [Campaign status](../README.md) · [Family index](../../../../../docs/enterprise-family-report-index.md)
