# Source-Provenance Drift Diagnostic

## Outcome

The `2026-07-15T13-25-43-918Z-compare` run was intentionally stopped and rejected
after source-provenance drift was detected. The stop decision was made when 10 of 90
planned rows had persisted; two already-running cells completed during shutdown, so
the Promptfoo database contains 12 rows in total, four per profile. No result file
was published.

None of those rows is benchmark evidence. Their scores, assertions, answers, and
reviewer fields are deliberately omitted from the compact diagnostic.

## Why the run is ineligible

Skill Arena correctly materialized an isolated treatment package whose tree hash was
`e99b40283a67a2c801cee7cc4815e07015b400c802d02d00756d6731e8f52544`.
While the comparison was running, the checked-in consultation instructions were
clarified to describe the then-final, now historical MCP v1.3.1 recovery contract.
That long-candidate confirmation handshake was later superseded by the active v1.4.0
prepared-envelope and digest-confirmation protocol. The final package tree at the
time of this diagnostic
therefore became
`773b36e85d761f9d1bff1c46840386ec4c3c027e9aca906ee8612827883ddf37`.
Even though the retrieval code and comparison config did not change, the treatment
instructions were no longer byte-identical to the intended final package. That breaks
the source-identity gate required for a causal control/treatment comparison.

## Decision and remediation

The interrupted run is retained only to prove why it was rejected. The final package
and config manifest were rebound and validated, and all bound package, runtime,
config, and documentation sources must remain frozen throughout the replacement
90-cell run. Only a fresh run whose materialized identities match that frozen
manifest can contribute comparison metrics.

The machine-readable companion,
[`source-provenance-drift-diagnostic-20260715.json`](source-provenance-drift-diagnostic-20260715.json),
binds the ignored execution log, generated Promptfoo config, privacy-preserving row
projection, materialized identities, and final frozen identities. Raw answers remain
append-only and ignored.
