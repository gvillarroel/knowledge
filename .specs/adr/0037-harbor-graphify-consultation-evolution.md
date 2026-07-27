---
adr: "0037"
title: "ADR 0037: Add a Bounded Harbor Evolution for Graphify Consultation"
summary: "Preserve Graphify retrieval byte-for-byte while adding a terminal bounded support-pack compiler for Harbor answers."
status: "Accepted"
date: "2026-07-20"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, graphify, harbor, skills]
---

# ADR 0037: Add a Bounded Harbor Evolution for Graphify Consultation

## Status

Accepted. This extends ADRs 0030, 0032, and 0033.

## Decision

Add `consult-semantic-okf-harbor-graphify` as an independently named standalone candidate paired only with `build-semantic-okf-graphify`. Keep the Graphify runtime, query CLI, dependency lock, and smoke test byte-identical to the parent consultation skill.

The candidate adds a read-only answer compiler that decomposes a question into bounded lexical facets, runs pinned Graphify scoring and BFS, interleaves results, hydrates exact ledger parents, and emits at most six compact supports. A successful `prepare` is terminal for discovery: the agent must draft and call `finalize` without additional search or full-document reads. Finalization recomputes the support pack and enforces exact identities, hashes, locators, closed keys, and first-use evidence ordering.

Use q031 only for failure diagnosis, q032 for development, and q034 as an untouched holdout. Infrastructure failures are not semantic failures. Promote only when development and holdout retain all non-compensating contract and evidence gates.

## Consequences

Graphify ranking quality is unchanged by construction. The candidate reduces agent context expansion and converts valid discovery into contract-ready evidence. The live pilot remains one case per cohort and does not establish population-level semantic superiority.
