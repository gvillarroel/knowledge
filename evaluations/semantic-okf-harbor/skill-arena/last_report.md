# Skill Arena q031 paired-control validation

Validation date: 2026-07-16

Skill Arena `v0.1.0` validated and dry-ran all six configurations. Every plan contains one frozen q031 prompt, two profiles, one Pi/GPT-5.3 Codex Spark variant, two total requests, zero unsupported cells, no cache, and maximum concurrency one.

| Family | Config validation | Dry run | Planned cells | Unsupported | Live Skill Arena run |
| --- | ---: | ---: | ---: | ---: | --- |
| Adaptive | Pass | Pass | 2 | 0 | Not run |
| Classical | Pass | Pass | 2 | 0 | Not run |
| Embeddings | Pass | Pass | 2 | 0 | Not run |
| Ensemble | Pass | Pass | 2 | 0 | Not run |
| Entity graph | Pass | Pass | 2 | 0 | Not run |
| Legacy | Pass | Pass | 2 | 0 | Not run |

Additional static checks passed for every file: the parsed prompt exactly equals the frozen generated q031 instruction after final-newline normalization; there are exactly two profiles and one variant; every skill source is a checked-in `skills/` path whose expected tree hash remains bound in `config-manifest.json`; the adapter/model pair is Pi with `openai-codex/gpt-5.3-codex-spark`; and a leakage scan found no qrel or expected-answer vocabulary. The config-author closeout hook also completed with two rust-code-analysis JSON artifacts.

No live Skill Arena model calls were made. The Harbor jobs are the primary live evidence and must not be conflated with these successful planning checks.
