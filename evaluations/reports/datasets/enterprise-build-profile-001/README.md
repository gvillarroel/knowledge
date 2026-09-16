# EnterpriseRAG construction feasibility and phase costs

The original four-cell diagnostic produced **0 qualified construction outcomes out of four**.
The official native report records 0 passed trials,
4 verifier failures and 0 execution errors.
These are construction measurements of the unchanged Entity Graph and Ensemble
reference skills. They add no retrieval score or answer-quality leaderboard rank.

| Family / records | Outcome | Agent seconds | Qualified output bytes |
| --- | --- | ---: | ---: |
| Entity Graph / 256 | Construction integrity failed | 19.01 | Unavailable |
| Ensemble / 256 | Construction integrity failed | 82.86 | Unavailable |
| Entity Graph / 1,024 | Construction integrity failed | 87.98 | Unavailable |
| Ensemble / 1,024 | Construction integrity failed | 335.86 | Unavailable |


[Phase costs and sampled code locations](phases.md) · [Cost, time and quality](cta.md) ·
[Entity Graph](skills/entity-graph.md) · [Ensemble](skills/ensemble.md) · [Exact aggregate](aggregate.json).

## Why the four integrity gates failed

Independent read-only inspection localized the same earliest verifier rejection
in all four originals: `check_records` raises `Missing actual concept document`.
The saved native diagnostic contains only `ValueError`; the exact message and
location were reproduced from saved artifacts and the frozen pure verifier prefix.
The unchanged constructor keeps a logical per-record `concept_path` in its
record ledger. Under `source-packed-v1`, multiple structured records from the
same source share the physical document `concepts/<source_id>.md`. The frozen
profile verifier instead requires the logical per-record path to exist as a
separate physical file. That assumption rejects this supported packing branch.

The finite nine-record rehearsal had one record per application. It therefore
missed the multiple-record packing branch despite declaring the same layout.
It exercised the constructors, family validators and transport verifier, but
did not rehearse the complete measured verifier on a source with multiple records.
This was a preparation coverage gap in this diagnostic.

The saved artifacts support narrower observations: all eight constructed trees
preserve the 5,120 expected record instances and their complete fields and bodies;
the 72 physical source-packed documents have the expected bodies and anchors.
The two trees in each cell are byte-identical, and all six command phases finish.
These comparisons are forensic observations, not replacement verdicts. The
trusted verifier-side family validator was never reached, so all four original
rewards remain zero and qualified output bytes remain unavailable. No rerun or
rescoring occurred. The aggregate binds the independent forensic evidence.

Any follow-up evaluation must first cover both single-record and multiple-record
source layouts with an end-to-end verifier rehearsal under a new prospective
protocol. This report does not establish a candidate improvement or justify
changing the reference constructor to satisfy the faulty physical-path check.

## Dataset and execution scope

Both public workloads retain complete original source records across nine applications:
Confluence, Fireflies, GitHub, Gmail, Google Drive, HubSpot, Jira, Linear and Slack.
The 256-record input contains 1,629,264 UTF-8 body bytes; the 1,024-record input
contains 6,797,341 bytes. A deterministic application-balanced ordering makes the
smaller workload a prefix of the larger. These are related workload variants,
not independent dataset samples. Application counts are balanced, not body bytes
or the parent corpus proportions. No query or relevance label controls selection.

One job, four originals, one attempt per cell, zero retries, concurrency two,
two CPUs and 6 GiB per agent and separate verifier. Each cell attempts two complete
constructions, two additional validator commands and byte equality under a
1,800-second whole-agent limit. The unchanged Ensemble provider is hashing,
revision 1, 384 dimensions; both families retain `source-packed-v1`.

The [prospective protocol](../../../../docs/enterprise-construction-profile.md) and
[ADR 0168](../../../../.specs/adr/0168-profile-construction-before-further-enterprise-mutations.md)
define the separate finite fixture/transport rehearsal and independent admission.
The rehearsal is not part of the four measured cells. It does not replenish any
old evaluation allocation. Raw inputs, indexed knowledge, native trials and sampled
stacks remain ignored; this directory contains aggregate reporting only.

## Interpretation

Builder-command time includes internal validation. Subsequent explicit validator
commands and the trusted verifier-side validation are reported separately.
The trusted validation sequence is unavailable here because the earlier
integrity check rejected every original before that sequence could start.
Partial phases remain partial, and an execution error never receives an inferred
construction or retrieval score. Stack counts identify observed code locations;
they are not exclusive CPU time. One attempt, nested inputs, observer overhead,
cache effects and concurrent neighbors limit comparisons to descriptive observations.

The [six-strategy all-500 retrieval catalog](../enterprise-all500-first-executions-001/README.md)
remains the retrieval comparison: Legacy and Turso 70.72, Embeddings 64.04,
Adaptive 63.61, Graphify 60.50 and Classical 56.16 (nDCG@10 multiplied by 100).
Entity Graph and Ensemble remain unavailable in that catalog. This diagnostic
does not replace those interrupted executions, complete E16, mutate a skill,
select a candidate or provide an independent promotion gate.
