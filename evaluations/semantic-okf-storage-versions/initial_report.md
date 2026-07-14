# Semantic OKF Storage Version Comparison: Initial Run

The first live run completed all 16 cells without infrastructure errors. Its raw assertion result was:

| Profile | Passed | Rate |
| --- | ---: | ---: |
| No skill | 0/4 | 0% |
| File-backed | 4/4 | 100% |
| Embedding-backed | 4/4 | 100% |
| Turso-backed | 3/4 | 75% |

The Turso exact-record response was manually adjudicated as semantically correct. It identified the immutable `semantic/knowledge.db` release, verified the complete logical and relational contract, used a bounded parameterized exact lookup on `(source_id, record_id)`, returned the literal concept path and complete stored concept evidence, and required unchanged database hashes. The assertion rejected it only because the response described the supported consultation helper instead of spelling `query_turso_knowledge.py` literally.

That rejection contradicts ADR 0015's preference for observable semantic behavior over incidental exact command spelling. The evaluator now also accepts the explicit Turso database plus bounded parameterized exact-record route. This file preserves the unmodified first-run score; later raw results and their explicit contract adjudication are recorded in `last_report.md` and `comparison-report.md`.

Initial Skill Arena evaluation ID: `eval-fZY-2026-07-14T10:38:02`.
