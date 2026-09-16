# Construction phases and sampled code locations

Command wall time includes that command's own bounded finalization. The initial
and final integrity phases use their journal boundaries. Missing phase ends
remain censored; a retained lower bound is not a completed duration.

## Entity Graph / 256

| Phase | State | Wall seconds | Censored lower bound seconds | Samples |
| --- | --- | ---: | ---: | ---: |
| initial-attestation | ended | 0.09 | Unavailable | Unavailable |
| plan-generate | ended | 0.17 | Unavailable | 0 |
| plan-adjust | ended | 0.17 | Unavailable | 0 |
| build-1 | ended | 6.87 | Unavailable | 1 |
| additional-validation-1 | ended | 2.03 | Unavailable | 0 |
| build-2 | ended | 6.88 | Unavailable | 1 |
| additional-validation-2 | ended | 2.03 | Unavailable | 0 |
| final-integrity | ended | 0.12 | Unavailable | Unavailable |

Main-thread leaf locations, up to three most frequent locations per sampled phase:

| Phase | Code location | Samples / retained phase samples |
| --- | --- | ---: |
| build-1 | `root0/assets/families/entity-graph/builder/scripts/_entity_graph_model.py:263 (reject_duplicates)` | 1 / 1 |
| build-2 | `root3/lib/python3.12/json/decoder.py:338 (decode)` | 1 / 1 |

## Ensemble / 256

| Phase | State | Wall seconds | Censored lower bound seconds | Samples |
| --- | --- | ---: | ---: | ---: |
| initial-attestation | ended | 0.10 | Unavailable | Unavailable |
| plan-generate | ended | 0.17 | Unavailable | 0 |
| plan-adjust | ended | 0.17 | Unavailable | 0 |
| build-1 | ended | 34.65 | Unavailable | 6 |
| additional-validation-1 | ended | 6.10 | Unavailable | 1 |
| build-2 | ended | 34.95 | Unavailable | 6 |
| additional-validation-2 | ended | 5.95 | Unavailable | 1 |
| final-integrity | ended | 0.14 | Unavailable | Unavailable |

Main-thread leaf locations, up to three most frequent locations per sampled phase:

| Phase | Code location | Samples / retained phase samples |
| --- | --- | ---: |
| build-1 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:711 (_derive_associations)` | 1 / 6 |
| build-1 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:720 (_derive_associations)` | 1 / 6 |
| build-1 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:659 (_derive_lexicon)` | 1 / 6 |
| additional-validation-1 | `root0/assets/families/ensemble/builder/scripts/_entity_graph_model.py:264 (reject_duplicates)` | 1 / 1 |
| build-2 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:807 (<genexpr>)` | 1 / 6 |
| build-2 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:725 (_derive_associations)` | 1 / 6 |
| build-2 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:771 (_derive_topics)` | 1 / 6 |
| additional-validation-2 | `root0/assets/families/ensemble/builder/scripts/_entity_graph_model.py:264 (reject_duplicates)` | 1 / 1 |

## Entity Graph / 1,024

| Phase | State | Wall seconds | Censored lower bound seconds | Samples |
| --- | --- | ---: | ---: | ---: |
| initial-attestation | ended | 0.12 | Unavailable | Unavailable |
| plan-generate | ended | 0.17 | Unavailable | 0 |
| plan-adjust | ended | 0.17 | Unavailable | 0 |
| build-1 | ended | 33.59 | Unavailable | 6 |
| additional-validation-1 | ended | 9.50 | Unavailable | 1 |
| build-2 | ended | 33.95 | Unavailable | 6 |
| additional-validation-2 | ended | 9.48 | Unavailable | 1 |
| final-integrity | ended | 0.24 | Unavailable | Unavailable |

Main-thread leaf locations, up to three most frequent locations per sampled phase:

| Phase | Code location | Samples / retained phase samples |
| --- | --- | ---: |
| build-1 | `dynamic-code:0 (unknown)` | 1 / 6 |
| build-1 | `root0/assets/families/entity-graph/builder/scripts/_entity_graph_model.py:1532 (derive_generic_edges)` | 1 / 6 |
| build-1 | `root0/assets/families/entity-graph/builder/scripts/_entity_graph_model.py:607 (read_jsonl)` | 1 / 6 |
| additional-validation-1 | `root0/assets/families/entity-graph/builder/scripts/_entity_graph_model.py:1470 (derive_generic_edges)` | 1 / 1 |
| build-2 | `dynamic-code:0 (unknown)` | 1 / 6 |
| build-2 | `root0/assets/families/entity-graph/builder/scripts/_entity_graph_model.py:697 (tokens)` | 1 / 6 |
| build-2 | `root3/lib/python3.12/json/__init__.py:234 (dumps)` | 1 / 6 |
| additional-validation-2 | `root3/lib/python3.12/json/encoder.py:258 (iterencode)` | 1 / 1 |

## Ensemble / 1,024

| Phase | State | Wall seconds | Censored lower bound seconds | Samples |
| --- | --- | ---: | ---: | ---: |
| initial-attestation | ended | 0.12 | Unavailable | Unavailable |
| plan-generate | ended | 0.17 | Unavailable | 0 |
| plan-adjust | ended | 0.17 | Unavailable | 0 |
| build-1 | ended | 145.22 | Unavailable | 28 |
| additional-validation-1 | ended | 23.79 | Unavailable | 4 |
| build-2 | ended | 141.93 | Unavailable | 27 |
| additional-validation-2 | ended | 23.54 | Unavailable | 4 |
| final-integrity | ended | 0.29 | Unavailable | Unavailable |

Main-thread leaf locations, up to three most frequent locations per sampled phase:

| Phase | Code location | Samples / retained phase samples |
| --- | --- | ---: |
| build-1 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:711 (_derive_associations)` | 3 / 28 |
| build-1 | `dynamic-code:0 (unknown)` | 2 / 28 |
| build-1 | `root0/assets/families/ensemble/builder/scripts/_entity_graph_model.py:241 (<lambda>)` | 2 / 28 |
| additional-validation-1 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:711 (_derive_associations)` | 1 / 4 |
| additional-validation-1 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:759 (_derive_topics)` | 1 / 4 |
| additional-validation-1 | `root0/assets/families/ensemble/builder/scripts/_entity_graph_model.py:1699 (<genexpr>)` | 1 / 4 |
| build-2 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:730 (<lambda>)` | 2 / 27 |
| build-2 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:711 (_derive_associations)` | 2 / 27 |
| build-2 | `root3/lib/python3.12/json/decoder.py:342 (decode)` | 2 / 27 |
| additional-validation-2 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:774 (<genexpr>)` | 1 / 4 |
| additional-validation-2 | `root0/assets/families/ensemble/builder/scripts/_adaptive_retrieval.py:711 (_derive_associations)` | 1 / 4 |
| additional-validation-2 | `root0/assets/families/ensemble/builder/scripts/_entity_graph_build.py:189 (_validate_or_raise)` | 1 / 4 |


`root0` is the complete frozen skill; `root1` is the profiling runtime; `root2`
contains the original image's plan helpers; `root3` is the Python installation.
Each sample contributes at most one main-thread leaf location. Counts do not
sum inclusive call stacks and do not estimate exclusive CPU time. Short commands
may finish before the first five-second sample. Aggregate JSON retains every
observed leaf count, receipt presence and sampler overhead. An incomplete stream
is not treated as a complete sampling measurement.

[Construction outcomes](README.md) · [CTA](cta.md).
