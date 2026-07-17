# Skill Portfolio Routing Regrade

## Source run

- Benchmark: `knowledge-skill-portfolio-smoke-compare`
- Skill Arena result: `results/knowledge-skill-portfolio-smoke-compare/2026-07-13T10-17-42-117Z-compare/`
- Original generated report: `last_report.md`

## Reason for regrade

The generated report scored the treatment at 7/8 because the OKF response said not to modify native skill frontmatter and to keep OKF metadata exclusively in the generated projection. The assertion accepted only narrower wording such as `do not add`, `unchanged`, or `separate projection`. The current assertion accepts the equivalent non-mutation and generated-projection language.

No provider call was repeated for this regrade. The current prompt and global JavaScript assertions were executed against the unchanged `merged-summary.json` outputs from the source run.

## Regraded result

| Profile | Passed | Total |
| --- | ---: | ---: |
| `skill-portfolio` | 8 | 8 |
| `no-skill` | 0 | 8 |

This portfolio remains a routing smoke. Causal evidence for individual skills comes from the single-skill comparisons and the specialized Semantic OKF benchmarks.
