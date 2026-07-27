---
adr: "0039"
title: "ADR 0039: Promote Reciprocal Graphify and Freeze a Reference-Bridge Candidate"
summary: "Make reciprocal cross-partition lexical Graphify official and retain a retrospectively improved reference-bridge builder for prospective validation."
status: "Accepted"
date: "2026-07-20"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, graphify, harbor, builder, skills]
---

# ADR 0039: Promote Reciprocal Graphify and Freeze a Reference-Bridge Candidate

## Status

Accepted. This follows ADR 0038 and does not change the consultation package.

## Context

ADR 0038 accepted a reciprocal cross-partition lexical builder under the
campaign-specific `build-semantic-okf-harbor-graphify` name. Its deterministic
40-question retrieval results and sealed holdout supported promotion, while its
paired Harbor answer trace remained limited by the unchanged consultation
response contract.

After that holdout was opened, further builder-only experiments could improve
the product but could no longer support another prospective promotion decision
on the same benchmark.

## Decision

Replace the implementation of `build-semantic-okf-graphify` with the accepted
ADR 0038 reciprocal lexical builder. Keep the official skill name stable and
keep `consult-semantic-okf-graphify` byte-identical.

Create `build-semantic-okf-graphify-next` as a standalone experimental builder.
Retain the official reciprocal lexical K=1 edges and add an edge only when two
authoritative bodies reference each other's normalized internal documentation
routes and neither endpoint has reciprocal-reference degree greater than six.
Regenerate the complete edge set from `records.jsonl` during validation.

Freeze, but do not promote, the new candidate. Require a fresh prospective
dataset or sealed holdout before it may replace the official builder.

## Consequences

The official skill now reproduces the accepted 6,390-node, 6,419-edge graph with
logical SHA-256 `5541ba21da0116a435cbb60392327e03259c81049cfb6610266499837322366d`.

The frozen candidate reproducibly produces 6,390 nodes and 6,494 edges with
logical SHA-256 `ab17730bb536da30c6c20c74bdc80c6c9d86e09a8171ace687ed92e97224587a`.
On the reused 40-question benchmark it improves Recall@10 from 77.3% to 80.6%,
hard Recall@10 from 57.5% to 60.8%, and nDCG@10 from 0.578 to 0.591. MRR@10
falls from 0.579 to 0.576 and standalone mean latency rises from 81.6 ms to
88.5 ms. All 449 returned candidate evidence rows validate.

These measurements justify preserving the candidate, not declaring a second
prospective promotion.

The q032 Harbor rehearsal binds the candidate to the unchanged consultation
skill without serializing authentication. The initial live attempt produced no
trial because Docker was unavailable. A later append-only Harbor 0.18.0 job
completed with reward `0.000`: retrieval achieved complete qrel coverage and
perfect MRR/nDCG for the case, while the unchanged response and evidence
contract failed. This is a semantic result and is not eligible for external
failure resumption.
