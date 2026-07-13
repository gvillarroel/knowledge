# Round-trip Confluence Semantic Regrade

## Source run

- Benchmark: `roundtrip-confluence-pages-isolated-planning-compare`
- Skill Arena result: `results/roundtrip-confluence-pages-isolated-planning-compare/2026-07-13T10-21-20-011Z-compare/`
- Original generated report: `last_report.md`

## Reason for regrade

The generated report scored the treatment at 3/4 because the boundary response used one separately reviewed workflow for both the page move and restriction change. The assertion required two incidental phrases even though the response explicitly said the skill must perform neither operation. The evaluator now checks the durable invariants: both operations are identified and a separate, prohibited, or unsupported boundary is stated.

No provider call was repeated for this regrade. The current prompt and global JavaScript assertions were executed against the unchanged `merged-summary.json` outputs from the source run.

## Regraded result

| Profile | Passed | Total |
| --- | ---: | ---: |
| `skill` | 4 | 4 |
| `no-skill` | 0 | 4 |

Every treatment output satisfies its prompt assertion, JSON response contract, and response-format assertion. Every control output remains unsuccessful.
