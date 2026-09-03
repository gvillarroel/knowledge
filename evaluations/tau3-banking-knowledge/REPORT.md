# tau3 banking-knowledge evaluation report

Date: 2026-08-23

## Outcome

The repository's integrated classical and chunked-classical knowledge-skill builders both passed deterministic generation, reproduction checks, independent deep validation, packaged runtime smoke tests, and packaged deep verification on the pinned tau3 banking corpus. Their document rankings are identical in all four supported retrieval modes.

On the retrospective oracle-context retrieval diagnostic, the local classical index substantially outperformed the exact upstream BM25 implementation. The result is useful regression evidence for retrieval mechanics, but it is not an official tau3 conversational score and cannot serve as sealed validation or promotion evidence.

## Dataset and integrity

- Harbor dataset: `sierra-research/tau3-bench`, banking-knowledge domain.
- Upstream release: `tau2-bench` `v1.0.0`, commit `17e07b1da2bbc0cadfddeea36412686e0604127b`.
- Corpus: 698 documents, each preserved as a distinct evidence identity.
- Cohort: all 97 banking-knowledge tasks.
- Upstream/Harbor task parity: 97 of 97 exact matches.
- Source document tree SHA-256: `5f6421a037ea3670db4872d0b653a7a55473a574c212ef49fa956cc08a8e2b7b`.
- Harbor task-config tree SHA-256: `e6f44065459e1ad324f05407d43c8402fa37c55713072fe320421868c215137f`.
- Evaluator material is physically excluded from the builder-visible input tree.

The public Harbor task images clone the upstream repository without a commit pin. The harness therefore resolves the release independently, digest-locks the documents and task configs, and fails closed on drift.

## Retrieval results

The query is the complete `task.user_scenario.instructions` text and the binary qrels are `task.required_documents`. Results are macro averages across all 97 tasks.

| Runtime and mode | Hit@10 | Recall@10 | MRR@10 | nDCG@10 | All qrels@10 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Upstream BM25 | 67.01% | 14.72% | 0.338 | 0.156 | 3.09% |
| Local BM25 | 92.78% | **35.41%** | 0.672 | 0.428 | **8.25%** |
| Local association | 91.75% | 35.29% | 0.682 | 0.427 | **8.25%** |
| Local fusion | **93.81%** | 35.09% | 0.680 | 0.421 | **8.25%** |
| Local topic | **93.81%** | 35.27% | **0.692** | **0.429** | **8.25%** |

The default fusion mode has the best Hit@10 but is not uniformly best. Local BM25 has the highest Recall@10, while topic has the highest MRR@10 and nDCG@10. This dataset does not support claiming one mode dominates every retrieval objective.

Both generated experts produced identical full top-10 rankings for BM25, association, fusion, and topic. Their shared validated knowledge tree is `90e34328ee38dafdfa2b823bc8ad8455055966bb3db71ad4c34a18ddba3cd5d0`.

## Chunked context result

At the default 6,000-token budget, the chunked selector returned 17.29 chunks and used 5,969.93 estimated tokens on average. It achieved:

- 97.94% task hit rate;
- 40.66% mean required-document recall;
- 9.28% complete-qrel coverage;
- 79.38% internal quality-guard completion.

The selector improves evidence coverage beyond document top-10, but almost exhausts its budget and leaves its quality guard incomplete on 20.62% of tasks. It is therefore a useful bounded evidence interface, not an unconditional quality improvement.

## Runtime and Harbor smoke

- Classical batch: 250.08 seconds for deep verification plus 388 searches.
- Chunked batch: 382.14 seconds for deep verification, the same 388 searches, and 97 context selections.
- Harbor 0.18 `install-only`: one official task environment and Pi agent setup completed for each expert with zero exceptions. Verification was deliberately disabled, so these jobs have no reward and must not be interpreted as passes or failures.
- Official end-to-end tau3 conversations were not run because the tau3 user simulator and verifier require `OPENAI_API_KEY`, which was not available. No score was imputed from the install-only jobs.

## Interpretation boundary

The full hidden scenario is an oracle-context ceiling: a live agent must elicit those facts over multiple turns. Qrel retrieval does not measure final answer correctness, customer-tool actions, or conversational policy compliance. Because the qrels were inspected while constructing this adapter, this study is retrospective and non-promotional. Any promotion decision requires a new organizer-owned study with fresh, sealed validation as required by ADR 0111.

Detailed machine-readable output is generated at `evaluations/semantic-okf-datasets/generated/external/tau3-banking-knowledge-evaluation-v5/reports/retrieval-evaluation.json`. Harbor install artifacts and the native Harbor report are under the adjacent `harbor-smoke/` and `reports/harbor-install-smoke/` directories.
