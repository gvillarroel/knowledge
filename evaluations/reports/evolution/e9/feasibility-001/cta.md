# Graphify feasibility: cost, time and quality

[Feasibility result](README.md)

The fixed native allocation is one trial and zero retries. Agent limits remain 2 CPUs and 6 GiB, with 2,400 seconds per construction and 3,600 seconds for the bridge. The separate verifier uses 2 CPUs and 2 GiB.

| Observation | Value |
| --- | ---: |
| Native job elapsed seconds | 2797.711602 |
| Agent execution seconds | 2743.217389 |
| Native errors | 0 |
| Retries | 0 |
| double build seconds | 2639.574884984 |
| knowledge bytes | 240091223 |
| primary query p95 ms | 782.3678689996996 |
| Native reported n_input_tokens | 0 |
| Native reported n_cache_tokens | 0 |
| Native reported n_output_tokens | 0 |
| Native reported cost_usd | 0.0 |

Missing usage stays unavailable. Native zero model-usage fields do not price CPU, machine, storage or host overhead. The displayed native and agent durations overlap and must not be summed. Build duration is contained within agent execution.

The [terminal E7/E8 CTA](../../e8/development-cta-003/README.md) preserves the preceding 83 completed jobs, including seven construction errors. This report adds one separately identified feasibility trial; it does not replace prior costs or include every earlier project campaign. There is no cost-per-quality-gain estimate against the unmeasured original.
