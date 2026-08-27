# Preflight rejections and infrastructure failures

Preflight rejections did not consume Harbor model trials and are not reward
observations. Infrastructure failures are likewise excluded from strategy
ranking.

## Deterministic preflight treatments

| Treatment | Status | Reason |
| --- | --- | --- |
| One-focus-per-facet v14 | Reject before Harbor | Distinct facets were selected, but the operational measurement passage was still displaced |
| Lexical-head backoff v15 | Reject before Harbor | The suffix facet recovered the topic but ranked a later noise passage instead of the requested procedure |
| Balanced four-focus v17 | Reject before Harbor | Bibliography and repeated generic windows still displaced an operation-specific span |
| Contents-filtered coverage contract v19 | Reject before Harbor | Several omissions were repaired, but the requested ancilla limitation remained absent |
| Single-anchor facet v20 | Reject before Harbor | A figure-dense span tied with and preceded the explanatory prose needed for direct support |
| Scope-anchored evidence yield v22 | Reject before Harbor | It missed both tested source-local complements and shifted capacity toward generic overview material |
| Role-reserved linked chunks v23 | Reject before Harbor | It repaired one method/result complement but truncated a suppression factor at an arbitrary window boundary |
| Full-coverage distinctive facet v25 | Reject before Harbor | Singular/plural variation reduced weighted lexical coverage below an exact admission gate |
| Inflection-tolerant distinctive facet v26 | Pass to terminal hardening | All six contexts fit the 12,000-token budget and covered all 15 registered relevant sources; v27 added compact output before live evaluation |

## Evaluation infrastructure

| Attempt | Agent calls completed | Verifier calls completed | Usable strategy result | Failure and disposition |
| --- | ---: | ---: | --- | --- |
| v27 initial | 0 | 0 | No | Host Python path could not import `pi_luna_agent`; rerun from a corrected environment |
| v27 r1 | 6 | 0 | No | Docker Desktop rejected Harbor's nftables `fib daddr type local` rule before `test.sh`; 478,570 tokens and $0.06806804 were spent but no semantic reward exists |
| v27 r2 | 6 | 6 | Yes | A digest-pinned compatible egress adapter was used in a fresh full Harbor job |

The same pinned adapter was then used for both canonical and v27 independent
validation jobs. This preserves fairness without reusing the failed r1 agent
outputs or applying an unsupported verifier-only recovery.
