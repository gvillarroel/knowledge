# Enterprise generator replay: verification

[Comparison](README.md) · [Machine-readable verification](verification.json)

All eight G2 experts passed deterministic `--check` reconstruction, independent validation, generated deep verification, builder/consultant runtime checks, exact native-to-façade payload comparison, physical probe citations and exact record lookup. Each expert remained unchanged. These are artifact and consultation checks; no benchmark question or semantic outcome was rerun.

| Family | Rebuild | Independent validator | Native/façade payload | Probe citations | Exact get | Unchanged |
|---|---|---|---|---:|---|---|
| adaptive | pass | pass | equal | 5 | pass | yes |
| classical | pass | pass | equal | 5 | pass | yes |
| embeddings | pass | pass | equal | 5 | pass | yes |
| ensemble | pass | pass | equal | 5 | pass | yes |
| entity-graph | pass | pass | equal | 5 | pass | yes |
| graphify | pass | pass | equal | 4 | pass | yes |
| legacy | pass | pass | equal | 5 | pass | yes |
| turso | pass | pass | equal | 5 | pass | yes |

The application coverage gate passed with **1,405 tests** and **90.7% total application coverage**, against the required 80% minimum. The reviewed command was `python scripts/check_coverage.py --threshold 80`, with a project-local test temporary directory.

The test suite includes the full-text comparator fixture, invalid question rejection, append-only result writing, Turso sidecar containment, and the regression preventing full-text reports from inheriting the historical title-only warning.

The verification uses the same pinned generator, source and plan bindings. The additional generic native/façade probes and reconstruction costs are separate from the 1,440 benchmark query executions and their CTA table. Application coverage measures the application package; the eight-family CLI checks separately exercise the generated experts.

The completed G2 construction study and S2 application-split study also passed their organizer integrity checks without rewriting their histories. No private gate was opened by this replay, and no new skill promotion or push occurred.
