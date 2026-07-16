# Astro Semantic OKF Build Comparison

Every family was built twice from the same frozen 416-document corpus. Derived projections are non-authoritative; the core-parity gate compares the complete authoritative Semantic OKF core across families.

| Family | Status | Build | Validation | Deterministic bundle | Deterministic core | Core parity | Mean build ms |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy | pass | pass | pass | pass | pass | pass | 13386.8 |
| embeddings | pass | pass | pass | pass | pass | pass | 232249.1 |
| classical | pass | pass | pass | pass | pass | pass | 24183.9 |
| adaptive | pass | pass | pass | pass | pass | pass | 24698.2 |
| entity-graph | pass | pass | pass | pass | pass | pass | 42479.9 |
| ensemble | pass | pass | pass | pass | pass | pass | 334528.9 |

Run: `evaluations/semantic-okf-astro/results/runs/20260716-astro-generic-01`

No MCP server or transport participates in acquisition, build, validation, or consultation.
