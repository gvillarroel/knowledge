# Construction cost, time and quality

The original job wall time was **599.40 seconds**. Concurrency
was two, so trial durations must not be summed into job elapsed time.

| Family / records | Agent seconds | Total trial seconds | Native verifier seconds | Trusted extra validation sequence seconds | Reported provider USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Entity Graph / 256 | 19.01 | 88.09 | 26.15 | Unavailable | 0.0000 |
| Ensemble / 256 | 82.86 | 148.33 | 27.08 | Unavailable | 0.0000 |
| Entity Graph / 1,024 | 87.98 | 155.19 | 27.92 | Unavailable | 0.0000 |
| Ensemble / 1,024 | 335.86 | 407.29 | 30.08 | Unavailable | 0.0000 |


Agent time covers the complete native agent call. Total trial time also includes
setup, artifact transport and verification. Native verifier time covers its
separate environment workflow; the trusted extra validation sequence is a nested
measurement, including its adjacent integrity work, and must not be added again.
[Command wall times](phases.md) separately identify builds and additional validations.

These deterministic agents make no LLM calls. Provider usage is shown only where
the native result records it; unavailable usage is not imputed to zero. Reported
provider USD excludes local CPU, memory, storage and orchestration costs.

Construction integrity is the quality gate. Retrieval nDCG and answer quality
were not evaluated. [Outcomes and scope](README.md).
