# Solution-agnostic answer-quality audit

The same completed answers were re-adjudicated independently against the frozen semantic rubric and ground-truth claim contract. Answer-selected evidence, retrieval traces, strategies, paths, hashes, locators, native rewards, and token counts were hidden. Each case was reviewed twice by Pi with GPT-5.6 Luna at high thinking, with answer order reversed; the published score is the conservative consensus.

| Metric | canonical | chunked-v27 |
| --- | ---: | ---: |
| Full-quality cases | 0/6 | 0/6 |
| Mean required-point coverage | 77.08% | 75.00% |
| Orientation agreement | 80.56% | 94.44% |

| Required-point status | canonical | chunked-v27 |
| --- | ---: | ---: |
| satisfied | 13 | 12 |
| partial | 11 | 12 |
| missing | 0 | 0 |
| contradicted | 0 | 0 |

| Case | canonical | chunked-v27 | Second-arm result |
| ---: | --- | --- | --- |
| 1 | fail; 75.0%; minor-error | fail; 75.0%; major-error | regressed |
| 2 | fail; 87.5%; minor-error | fail; 75.0%; major-error | regressed |
| 3 | fail; 87.5%; minor-error | fail; 75.0%; minor-error | regressed |
| 4 | fail; 50.0%; major-error | fail; 62.5%; minor-error | improved |
| 5 | fail; 75.0%; major-error | fail; 87.5%; minor-error | improved |
| 6 | fail; 87.5%; major-error | fail; 75.0%; minor-error | mixed |

Second-arm paired outcomes: improved=2, mixed=1, regressed=3.

This semantic table supersedes native mechanical reward for quality claims. Native reward remains valid only for contract compliance and focus/evidence-anchor coverage; efficiency measurements remain separate.
