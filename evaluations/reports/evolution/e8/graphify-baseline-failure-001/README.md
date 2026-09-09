# E8 Graphify construction failure

Snapshot: 2026-09-09 05:54 UTC. The original native Graphify baseline completed
with one execution error after its first builder subprocess exceeded the fixed
2,400-second budget. It produced no retrieval rewards or qualified baseline.

| Native trials | Execution errors | Retries | Builder limit | Native job time | Agent time |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 0 | 2,400 s | 2,432.53 s | 2,400.75 s |

The preserved native execution log identifies `subprocess.TimeoutExpired` in
the first build of the Graphify knowledge snapshot. The native report validates
one completed trial with an error, empty rewards and unavailable mean reward.
The native Pareto owner excludes this baseline from its qualified archive.
Its diagnostic search summary's numeric zero is not a measured nDCG@10 value.

Construction did not reach the required double-build, validation and query
sequence. Retrieval quality, complete knowledge size, evidence integrity and
cost remain unavailable. The fixed model is the deterministic local retrieval
adapter. This resource-budget failure is not an external-failure retry, and the
original job is preserved without rerun. It consumes one baseline attempt and
does not establish a completed Graphify mutation search.

The existing E8 controller stops this lane and continues independent families.
Graphify requires a separate construction-efficiency treatment before a viable
native comparison can be claimed. The
[synthetic neighbor-selection prototype](../graphify-scaling-001/README.md)
supplies a concrete hypothesis with exact synthetic outputs; it does not prove
that the complete native build now fits the budget or identify the entire cause
of this failure. E8's sealed builder remains unchanged.

[Aggregate and source commitments](aggregate.json) bind the original native
report, root result, archive, execution log and source-integrity receipt. The
native reporter's exact skill digest is
`sha256:2dc74826fa29e282b52bb1dcb6c58bd4cc8342d28fd3aa0baf54ebe3cd9332b9`.
The maintained organizer recorded the native report at E8 ledger sequence 12,
event digest `b284427831c3cde7e9a346e251ad8e6a77bfc983e0e88a90d88f1b6c964dafb9`.
Raw logs, task contents and candidate artifacts remain ignored.

[Campaign status](../README.md) · [Family reports](../../../../../docs/enterprise-family-report-index.md)
