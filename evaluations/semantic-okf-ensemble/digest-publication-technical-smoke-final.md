# MCP 1.4.0 Digest Publication Technical Smoke

## Status

Accepted as a **non-causal technical smoke**. The retained q031 run proves that the live MCP 1.4.0 preparation, digest confirmation, and host publication path completed its technical contract in all three repetitions. It provides no causal answer-quality metrics and does not rank the ensemble against any alternative.

## Result

| Repetition | Technical contract | Assertion score | Response contract | Evidence validity | Atomic answer completeness | Important negatives | Confirmed output SHA-256 | Bytes |
| --- | --- | ---: | --- | --- | --- | --- | --- | ---: |
| 1 | Pass | 1.0 | Pass | Pass | Pass | Pass | `a4dcf2087c8de2cf48aec1edd2e24bf394d15acd15c98f0afef43f4cefe12a2f` | 8,125 |
| 2 | Pass | 0.8 | Pass | Pass | Fail: exact reviewed OR group only | Pass | `529d1561c90341adf61e3ca685144458e1e16ecc413fb82abb033645547dd099` | 8,078 |
| 3 | Pass | 1.0 | Pass | Pass | Pass | Pass | `a87dd68d2c414a41a35023eb287188122c6625f5dd38681e0f1dfd2bdfcb19fe` | 7,687 |

The second repetition missed only the exact atomic option set `claim-2503-13804v1-037 | claim-2503-13804v1-038`. All three repetitions passed response format, response contract, evidence validity, and important-negative coverage. Therefore, the Promptfoo assertion results are two full passes and one 0.8 result, while the narrower digest-publication technical contract is 3/3.

## Attested protocol evidence

The frozen attestor was used read-only over each retained execution trace. Every repetition:

- started with one successful `semantic_okf_inspect` call;
- read coverage pages 1 through 5 exactly once, in ascending order;
- bound `persisted-idf-facet-consensus-priority-v1` with priority-order SHA-256 `9ec21df4d02d0e1fba2a9dac3555c68e424968d347ff4d48d8df768351e1b25b`;
- ended with successful `semantic_okf_prepare_answer` then one terminal successful `semantic_okf_confirm_answer` using only `response_sha256`;
- published bytes whose SHA-256 and byte count matched both the prepared envelope and confirmation receipt;
- made zero failed MCP calls, needed zero recovery attempts, and made zero shell or command calls; and
- required the host publication correction, so `publication_corrected` is true in all three repetitions.

The retained trace hashes are:

| Repetition | Trace SHA-256 |
| --- | --- |
| 1 | `6c748ec75c6ade24f0b999a706e55a04858598fbfe66419c5f06a3f5bb2ac593` |
| 2 | `20982ce51d263da3c0c51c98ef03fe718c84b6cee8a1f3a7f4bee03d397ea6f4` |
| 3 | `4da23666fdca02321e29c04faa276d2e249803d6d8cffada56e8eafa014a2f6f` |

## Reproducibility bindings

| Artifact | SHA-256 |
| --- | --- |
| Full comparison config `evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml` | `be443278a2eab287a78945f5bf8f42a5bcb7f49153476901b042b8aeb2d9564b` |
| Config manifest `evaluations/semantic-okf-ensemble/skill-arena/config-manifest.json` | `46fc4604289410de0acfc294a92eb72c941179f361aa6a3c66742487ac144b29` |
| Answer-output contract `evaluations/semantic-okf-ensemble/answer-output-evaluation-contract.json` | `f87cb914a0961bf4a1e3264fb0ca635d1a28426d200074500478f8a9e940e09a` |
| Frozen attestor `evaluations/semantic-okf-ensemble/scripts/attest_skill_arena_mcp_runtime.py` | `146a301d39fac6018288ba83a48ef8a1e5aaeac8a057454cd4d0bc88dfd14fe6` |
| Smoke config `results/q031-digest-publication-smoke-v4.yaml` | `ab8db143851bcb4e07b435739b4670ef8475125c21b6cc0a9ead924b6bc5bc23` |
| Promptfoo result `results/semantic-okf-ensemble-q031-digest-publication-smoke-v4/2026-07-15T14-20-42-509Z-compare/promptfoo-results.json` | `0898100ffc69bb71820609f941b91c8eb2db07826ab1874621c2d4f696b90cb1` |

## Interpretation boundary

This smoke has one treatment profile, one question, and three repeated executions. It has no concurrent control arm and does not isolate the skill from model-run variance. Its assertion scores must not be added to the causal 90-answer comparison, used to estimate an answer-quality lift, or treated as evidence that this approach is better than another. Its accepted use is limited to showing that the final digest-confirmed publication protocol works in a live isolated Skill Arena execution.

The compact machine-readable companion is `evaluations/semantic-okf-ensemble/digest-publication-technical-smoke-final.json`.
