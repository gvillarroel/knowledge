# Cost, time and attempts

One original per cell, one attempt, no retries, concurrency two. Eight constructions and eight additional agent validators were planned. Each complete positive adds one trusted verifier-side validator; semantic negatives do not invoke it. Every cell shares one 570-second useful verifier budget within the native 600-second limit.

| Strategy / records | Agent seconds | Native verifier seconds | Completed child command seconds | Positive validator sequence seconds | Provider USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Entity Graph / 9 | 4.447 | 94.887 | 0.919 | 0.939 | 0.000 |
| Ensemble / 9 | 7.210 | 113.890 | 1.119 | 1.135 | 0.000 |
| Entity Graph / 18 | 5.064 | 84.823 | 0.918 | 0.934 | 0.000 |
| Ensemble / 18 | 9.661 | 103.857 | 1.168 | 1.188 | 0.000 |

| Strategy / records | Recorded evaluator attempts | Granted validator entries | Proven child starts | Proven child completions |
| --- | ---: | ---: | ---: | ---: |
| Entity Graph / 9 | 7 | 1 | 1 | 1 |
| Ensemble / 9 | 7 | 1 | 1 | 1 |
| Entity Graph / 18 | 7 | 1 | 1 | 1 |
| Ensemble / 18 | 7 | 1 | 1 | 1 |

The callback records granted validator entry before process creation. Proven child counts come from the checked command journal; a start-only journal does not prove that the child started. Command wall time includes process startup, log collection and cleanup. The positive validator sequence also includes setup and post-validation tree hashing. Both intervals are nested in native verifier time and must not be added as separate costs.

Recorded native environment starts/stops: 8/8 of eight expected. Complete exact resource cleanup confirmed: true. Native owner exit code: 0.

Native job wall time: **353.330 seconds**. Agent and separate verifier each used two CPUs and 6 GiB RAM. Network access was disabled. The original deterministic agent made zero LLM calls; reported provider USD does not include local hardware, preparation or human/assistant review costs.

The full evaluator cap was 28 and the trusted-child cap was eight across the study. The guard narrowed actual trusted calls to the positives. Counts reflect the retained native diagnostics. Timing observations apply only to these small authored conformance fixtures and do not estimate full-corpus performance or a strategy speed ranking.

[General report](README.md) · [Semantic checks](checks.md)
