# RustMallet Semantic OKF Retrieval Evaluation

The fixed-seed RustMallet candidate passed two-build byte determinism, authoritative-core parity, and exact evidence validation on all 40 GraphRAG questions.

## Top-10 comparison

| Mode | Classical recall@10 | RustMallet recall@10 | Delta | Classical nDCG@10 | RustMallet nDCG@10 | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bm25 | 49.72% | 49.72% | 0.00% | 60.94% | 60.94% | 0.00% |
| topic | 82.42% | 80.80% | -1.62% | 82.25% | 81.86% | -0.38% |
| association | 82.56% | 79.49% | -3.07% | 82.58% | 80.84% | -1.74% |
| fusion | 83.46% | 80.28% | -3.18% | 83.23% | 81.84% | -1.39% |

## Hard-10 comparison

| Mode | Classical recall@10 | RustMallet recall@10 | Delta | Classical nDCG@10 | RustMallet nDCG@10 | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bm25 | 63.17% | 63.17% | 0.00% | 69.31% | 69.31% | 0.00% |
| topic | 93.00% | 88.50% | -4.50% | 83.75% | 82.75% | -1.00% |
| association | 93.00% | 86.50% | -6.50% | 84.76% | 81.18% | -3.58% |
| fusion | 95.50% | 86.00% | -9.50% | 84.98% | 81.40% | -3.58% |

## Validation

- Two clean builds were byte-identical across 890 files with tree SHA-256 `7f42997c20cdec17f72aac1442fa8ee138e62199867a6ac3f5962e1143aa3569`.
- Both retrieval runs had passing authoritative-core parity, zero route errors, and 100% exact evidence validity.
- The pool-100 run is retained in the JSON summary to distinguish candidate-budget effects from top-10 ranking quality.

## Decision

Retain RustMallet as an experimental skill pair. It preserves BM25 and exact evidence validity but does not replace the classical topic-community default on this benchmark.
