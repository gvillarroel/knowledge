---
adr: "0098"
title: "ADR 0098: Adopt Overlapping Multi-Lane arXiv Discovery"
summary: "Use a versioned multi-lane query profile, overlapping time windows, exact-version identity, and an auditable selection ledger for scheduled paper discovery."
status: "Accepted"
date: "2026-08-09"
product: "knowledge"
owner: "Platform Architecture"
area: "Research Acquisition"
tags: [knowledge, research, arxiv, discovery, automation, provenance]
---

# ADR 0098: Adopt Overlapping Multi-Lane arXiv Discovery

## Status

Accepted.

## Context

The weekly paper automation described its topic only in prose and issued four
manually chosen exact-phrase searches. On 2026-08-03 it searched for
`self-improvement`, `long-term memory`, `persistent memory`,
`memory management`, `knowledge management`, and `knowledge graph`. It did
not search for long-horizon execution, agent harnesses, task-state management,
skills, or context engineering.

`LongHorizon-Harness` (arXiv:2608.01964v1) was submitted that day and described
its contribution with the omitted vocabulary. It therefore never entered the
candidate set. The same run also sent concurrent requests to the arXiv API,
encountered rate limiting, and relied on ad hoc registration and abstract
injection rather than one idempotent acquisition path.

## Decision

- Keep the reviewed query lanes in `papers/arxiv-discovery-queries.txt` rather
  than burying them only in an automation prompt.
- Search every lane with a fourteen-day overlap from the most recent successful
  run. A temporal filter is operational state and must remain separate from the
  versioned topic profile.
- Apply that boundary inside each arXiv API query and expose truncated lanes.
  A discovery run is complete only when every lane returns its full window or
  is repeated with a sufficient result cap.
- Run arXiv calls sequentially with a default three-second inter-request delay,
  compact exact-ID metadata batches, an identifying user agent, and bounded
  `Retry-After`-aware retries.
- Deduplicate candidates by exact arXiv version and annotate registration for
  both the exact version and other versions of the same work.
- Treat search as candidate generation, not an automatic relevance verdict.
  Title-screen the complete result set, inspect abstracts for plausible
  finalists, append every finalist decision with its reason, and retain
  aggregate counts and reasons for title-screened rejections in
  `papers/discovery-log.md`.
- Normalize supported arXiv and alphaXiv links to official arXiv abstract URLs.
  Pin selected research inputs to exact versions.
- Register reviewed batches through one idempotent `add arxiv --if-missing
  --sync` command, then export and verify the active knowledge key.
- Batch exact IDs into compact API calls. If bounded API retries are exhausted,
  recover only from the matching official arXiv abstract page, preserve its
  citation and submission metadata, and label the acquisition route.

This decision extends ADR 0080's exact-version evidence boundary to ongoing
research acquisition. It does not mutate an immutable methodology snapshot;
a newly selected paper informs a future explicitly versioned snapshot.

## Consequences

Positive:

- vocabulary drift no longer makes one exact phrase a single point of failure;
- skipped or partially failed weekly runs are recovered by the overlap window;
- exact-version deduplication makes reruns safe;
- API pacing and retries reduce transient acquisition failures;
- the candidate ledger exposes why a paper was selected or rejected.

Negative:

- broader recall creates more candidates that require semantic review;
- no finite query profile guarantees exhaustive discovery;
- a fourteen-day overlap repeats some review work unless the ledger and
  registration annotations are consulted;
- exact-version pinning requires an explicit later decision to adopt a revision.
