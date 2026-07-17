# Semantic OKF Embedding Retrieval Comparison

Queries: 30; top-k: 100; primary relevance identity: paper ID.

## Retrieval quality

| Route | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 | Source Recall@10 | Evidence validity | Mean ms | p95 ms | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy_lexical | 0.0977 | 0.2979 | 0.4736 | 0.7886 | 0.8611 | 0.8002 | 0.3943 | 1.0000 | 3.1422 | 4.3592 | 0 |
| new_lexical | 0.1108 | 0.3049 | 0.4709 | 0.7813 | 0.9167 | 0.8028 | 0.4040 | 1.0000 | 1313.5472 | 1550.6167 | 0 |
| vector | 0.0939 | 0.2547 | 0.4220 | 0.7392 | 0.8278 | 0.7436 | 0.3922 | 1.0000 | 6188.6624 | 6745.8441 | 0 |
| hybrid | 0.1048 | 0.2799 | 0.3960 | 0.7728 | 0.8889 | 0.7736 | 0.4309 | 1.0000 | 6609.9743 | 7012.5548 | 0 |

## Timing methodology

- Legacy lexical: single in-process index reused across queries; only LegacyLexicalIndex.search is timed.
- New lexical, vector, and hybrid: one fresh CLI subprocess per query; timing includes process startup, full snapshot validation, provider/model loading, retrieval, JSON serialization, and parent-side parsing.
- Interpretation: reported latency is operational end-to-end latency, not an isolated algorithm-speed comparison; legacy and new route timings have intentionally different execution scopes.

## Corpus coverage and bundle size

| Bundle | 30-input coverage | Auxiliary vocabulary | Files | Bytes | Logical tree SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- |
| legacy | 30/30 (100.0%) | yes | 884 | 10888503 | `331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424` |
| new | 30/30 (100.0%) | yes | 888 | 21808060 | `1a1f4883a9824fa44b1ec039ff37b9e86a5a04239c6b3ebce2493df66321b920` |

## Core semantic parity

Status: **pass**. Authoritative file sets equal: **yes** (884 legacy, 884 new).

Logical core trees equal: **yes**. Legacy: `331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`; new: `331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`.

| Required artifact | Equal | Legacy SHA-256 | New SHA-256 |
| --- | ---: | --- | --- |
| `semantic/records.jsonl` | yes | `df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc` | `df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc` |
| `semantic/source-manifest.json` | yes | `42753ac5051dd53ed936f3edf3d236936d41d27d010388fe9aa870a9526c5da8` | `42753ac5051dd53ed936f3edf3d236936d41d27d010388fe9aa870a9526c5da8` |
| `semantic/ontology.ttl` | yes | `5f580f034208333e9236379efe13aff2b479a47c9db0a268f3b1238a90a25669` | `5f580f034208333e9236379efe13aff2b479a47c9db0a268f3b1238a90a25669` |
| `semantic/data.ttl` | yes | `87afa329979d5936ea8c32c54ff1d311f1189f5d112262cda896599de5575380` | `87afa329979d5936ea8c32c54ff1d311f1189f5d112262cda896599de5575380` |
| `semantic/shapes.ttl` | yes | `cc0c8850d4ab649090bb68cb95083041c4179ff1eb8d8a9d757864f57e523c98` | `cc0c8850d4ab649090bb68cb95083041c4179ff1eb8d8a9d757864f57e523c98` |
| `semantic/provenance.ttl` | yes | `3cbb460c271a74c8bb2b727162e64e72d36f9e8943517de539d4535619e20fd3` | `3cbb460c271a74c8bb2b727162e64e72d36f9e8943517de539d4535619e20fd3` |
| `semantic/validation-report.ttl` | yes | `86bfd457468be247fc763f8f70ca0705a60aed2a13101abcff5df0e8594712d0` | `86bfd457468be247fc763f8f70ca0705a60aed2a13101abcff5df0e8594712d0` |

## Raw input verification

Status: **pass**. Verified core files: 30/30.
