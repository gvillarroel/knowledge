# Classical full corpus: cost, time and quality

[Main report](README.md) · [Question categories](categories.md)

| Measurement | Value | Scope |
|---|---:|---|
| Index construction (seconds) | 2798.83 | All 511,962 records; includes posting merges; excludes final file hashing |
| Published SQLite index (GiB) | 4.6138 | Document store and 64 term partitions; excludes temporary posting blocks |
| Retrieval time (seconds) | 82.18 | Sum of 500 search calls; excludes index opening, hash checks and result serialization |
| Mean query latency (ms) | 164.37 | One pass; 500 queries |
| P95 query latency (ms) | 286.40 | Nearest rank; one pass; 500 queries |
| Retrieval model calls | 0 | Deterministic Classical BM25 |
| Retrieval LLM tokens | 0 | No inference for construction or retrieval |
| Retrieval LLM cost (USD) | 0.00 | Local compute cost is not measured |

The GPT-5.4 answer phase stopped after 712.81 seconds with 317 preserved answers
and two HTTP 429 quota failures across 319 calls. Its usage was 4,789,977 input
tokens and 212,373 output tokens: 5,002,350 total tokens, with no cached input
reported. The $15.16054 cost is an OpenAI-token-rate equivalent, not a Copilot
invoice. No judge ran; answer-quality Overall and public position are unavailable.

The separate [internal Luna arm](luna.md) completed all 500 fixed inputs;
generation and judging usage are reported separately below. Its Codex
estimates use the frozen runtime's rates and are not subscription invoices.
Incomplete model work is never ranked for answer quality.

Retrieval execution: offline Linux Docker, Python 3.12, four CPU quota and an 8 GiB memory limit. The frozen image digest is recorded in the aggregate companion. Answer generation and judging use the Windows host with the separately bound Python and Pi/Node runtime. This single pass does not establish a throughput distribution or a speed advantage over other hardware.

## Completed internal Luna usage

| Phase | Attempts | Known input tokens | Cached input (subset) | Known output tokens | Known total tokens | Seconds | Known estimated USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Answer generation | 500 | 7,864,961 | 0 | 93,042 | 7,958,003 | 808.42 | 1.68464 |
| Evaluation | 4,071 | 15,383,082 | 41,472 | 826,180 | 16,209,262 | 4934.13 | 4.06057 |

Cached input is already included in input tokens and is not added again to total tokens. Phase time includes initialization, integrity checks and artifact writing. Judge time sums the original, offline-replay and continuation phases and excludes repair development between stages. Estimates use the frozen runtime catalog and are not Codex invoices. Neutral availability probes are excluded from these phase totals.

The judge attempt count includes two historical requests with unknown usage. The known token and cost totals exclude that missing usage; they are lower bounds. Their combined conservative cost ceiling is $0.4634448. The full Luna answer-and-judge cost equivalent therefore lies between $5.74521 and $6.20865. This interval is not a subscription invoice.

[Exact phase aggregates and evidence hashes](luna.aggregate.json)
