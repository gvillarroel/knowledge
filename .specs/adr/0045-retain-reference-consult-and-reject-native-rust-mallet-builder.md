---
adr: "0045"
title: "ADR 0045: Retain Reference Consultation and Reject the Native RustMallet Builder Candidate"
summary: "Use snapshot-owned compact evidence references in the evolved RustMallet consultant, retain deterministic backfill for processed snapshots, and do not promote the native builder candidate after a small sealed-holdout regression."
status: "Accepted"
date: "2026-07-23"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - rust-mallet
  - evidence
  - references
  - harbor
---

# ADR 0045: Retain Reference Consultation and Reject the Native RustMallet Builder Candidate

## Status

Accepted.

This decision extends ADR 0042. It does not promote RustMallet into the
canonical eight-family registry and does not modify the original RustMallet
skill pair or historical evaluation artifacts.

## Context

Exact evidence rows contain long paths, locators, and SHA-256 values. Passing
those identities through model output creates an unnecessary transcription
boundary: a one-character mutation makes otherwise correct evidence invalid.
The processed snapshot already contains every exact identity needed to resolve a
retrieval hit deterministically.

The initial reference-aware builder discovery succeeded only after agents
manually derived, wrote, indexed, and validated a dictionary after the original
builder had published its six-file classical projection. Those repairs required
57 calls on q007 and 41 calls on q019. A native builder candidate was therefore
created from two qualified discovery traces and evaluated with schema-2 Harbor
trace distillation.

## Decision

Keep `classical/references.json` as processed, non-authoritative snapshot data.
Derive each `ref-` ID from the first 96 bits of the SHA-256 of canonical JSON for
the seven exact evidence fields. Require sorted one-to-one coverage of every
document and bind the artifact through the classical index and build report.

Retain `consult-semantic-okf-rust-mallet-evolved`. Its Harbor bundle digest was
`637af0aefb44de8bf24fffb246158c9db6a8e9bdfb6780150ca6f043cc965a6d`,
including four ignored Python bytecode files. The clean live source digest is
`a86ced363990095d62ca8e413e5fc881aed08f0cdb21acb905da4f5c9600ccff`;
all non-bytecode files match the evaluated parent. Its bounded
search/show/finalize protocol returns only compact IDs. A hidden or local
deterministic resolver expands IDs before legacy exact-evidence scoring.
Unknown, duplicate, stale, mixed, or tampered references fail closed.

Do not promote the native builder candidate at digest
`cc32ea3e3342ff41ea2b029c7b801a171461d046d1d4d48a61f5137a0a2cf0a5`.
It passed 2/2 development trials and 4/4 holdout trials with complete quality and
reference-resolution gates, but sealed holdout mean reward decreased from
0.815482 to 0.813053. Both q010 and q029 regressed, so the no-task-regression
rule selected the frozen builder baseline.

Keep the candidate implementation in evaluation assets, not in the live
builder skill. Use the deterministic atomic backfill tool to add the dictionary
to existing RustMallet processed snapshots until a fresh discovery-led builder
candidate earns promotion.

## Consequences

Positive:

- the model emits short immutable references instead of copying exact identity
  fields;
- consultation preserves the legacy verifier contract through deterministic
  resolution;
- full-40 retrieval parity confirms that adding references does not change
  BM25, topic, association, or fusion results;
- same-platform native builds and original-plus-backfill builds are byte-exact;
  and
- the strict Harbor promotion boundary remains intact.

Negative:

- processed snapshots require a separate atomic backfill while the native
  builder candidate remains unpromoted;
- the evolved consultant cannot read a six-file legacy snapshot until that
  snapshot is upgraded; and
- fixed-seed RustMallet artifacts are reproducible within the evaluated
  platform but not byte-identical across Windows and Linux.
