# Classical Semantic OKF Retrieval Results

This compact report summarizes the append-only schema 1.3 runs. All eight routes used the same 40 questions, the same authoritative core, and the same exact evidence-validation contract. Elapsed times are diagnostic only.

## Top-10 direct output

| Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `legacy_lexical` | 0.7931 | 0.7896 | 0.7422 | 0.8067 | 0.5750 | 0.5681 | 100% |
| `new_lexical` | 0.5475 | 0.8883 | 0.6092 | 0.7350 | 0.8033 | 0.6578 | 100% |
| `vector` | 0.5040 | 0.7875 | 0.5477 | 0.6100 | 0.6667 | 0.5305 | 100% |
| `hybrid` | 0.4834 | 0.8854 | 0.5651 | 0.6517 | 0.8750 | 0.6460 | 100% |
| `classical_bm25` | 0.4972 | 0.9583 | 0.6094 | 0.6317 | 0.9500 | 0.6931 | 100% |
| `classical_topic` | 0.8242 | 0.9333 | 0.8225 | 0.9300 | 0.9500 | 0.8375 | 100% |
| `classical_association` | 0.8256 | 0.9458 | 0.8258 | 0.9300 | 0.9500 | 0.8476 | 100% |
| `classical_fusion` | 0.8346 | 0.9583 | 0.8323 | 0.9550 | 0.9500 | 0.8498 | 100% |

## Pool-100 with paper-level top-10 scoring

| Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `legacy_lexical` | 0.7931 | 0.7896 | 0.7422 | 0.8067 | 0.5750 | 0.5681 | 100% |
| `new_lexical` | 0.8185 | 0.8883 | 0.7913 | 0.9300 | 0.8033 | 0.7567 | 100% |
| `vector` | 0.7494 | 0.7875 | 0.7115 | 0.7800 | 0.6667 | 0.6150 | 100% |
| `hybrid` | 0.8059 | 0.8854 | 0.7736 | 0.9050 | 0.8750 | 0.7737 | 100% |
| `classical_bm25` | 0.8264 | 0.9583 | 0.8331 | 0.9300 | 0.9500 | 0.8533 | 100% |
| `classical_topic` | 0.8242 | 0.9333 | 0.8225 | 0.9300 | 0.9500 | 0.8375 | 100% |
| `classical_association` | 0.8256 | 0.9458 | 0.8258 | 0.9300 | 0.9500 | 0.8476 | 100% |
| `classical_fusion` | 0.8346 | 0.9583 | 0.8323 | 0.9550 | 0.9500 | 0.8498 | 100% |

## Interpretation

Classical fusion retrieved 95.5% of required hard-question papers at 10 versus 80.7% for the legacy lexical route. Topic and association routes independently reached the same broad hard-question coverage, while fusion improved it further. This supports the claim that topic and association signals materially participate in evidence choice; it is not evidence that retrieval scores are factual authority.

The pool-100 run is retained because chunk-heavy embedding routes can surface multiple passages from one paper before paper-level deduplication. Both runs preserve zero-error, 100% evidence-valid outputs and authoritative-core parity.
