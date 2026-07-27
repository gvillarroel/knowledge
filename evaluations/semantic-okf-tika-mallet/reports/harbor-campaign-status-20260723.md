# Tika/MALLET Harbor Campaign Status

- Dataset: `graphrag-papers-40`
- Evaluation scope: grounded answer construction
- Status: `incomplete-external-provider-quota`
- Ranking eligible: `false`

No frozen treatment completed all 40 questions exactly once without a provider
failure. These runs therefore do not produce an answer-quality ranking and do not
alter the separately admitted deterministic direct-retrieval row.

| Treatment | Attempted | Answers emitted | Provider context limits | Provider quota | Harbor ranking |
|---|---:|---:|---:|---:|---|
| v2 original consult | 6/40 | 5 | 1 | 0 | Ineligible |
| v3 original consult with bounded prompt | 30/40 | 29 | 1 | 0 | Ineligible |
| v4 bounded consult | 1/40 | 0 | 0 | 1 | Ineligible |

The v3 `q028` cell exceeded the provider context window. This is a terminal
treatment failure and cannot be replaced or combined with another treatment.

The v4 preflight used the separately frozen
`consult-semantic-okf-tika-mallet-bounded` skill. The provider rejected its first
model call with `usage_limit_reached`: zero input tokens, zero output tokens, no
assistant output, and no agent tool calls. Numeric verifier values in that result
are audit placeholders, not semantic scores. The provider reported a reset at
`2026-07-29T17:08:54-04:00`.

After provider access is restored, admission requires a new append-only
prospective v4 campaign covering all 40 questions exactly once, followed by the
strict current-scorer audit and a separate semantic review. Prior treatments must
not be merged, and provider-failure placeholders must not enter a ranking.

The exact receipts and their SHA-256 bindings are recorded in
[`harbor-campaign-status-20260723.json`](harbor-campaign-status-20260723.json).
