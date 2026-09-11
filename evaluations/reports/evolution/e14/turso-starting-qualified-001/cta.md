# Turso starting pair: cost, time and quality

Only the retained-profile execution is new E14 work. The original E13 reference is displayed for comparison and must not be charged a second time.

| Measurement | Original E13 reference | New E14 retained profile |
| --- | ---: | ---: |
| Native job seconds | 415.515 | 246.684 |
| Agent seconds | 365.147 | 195.422 |
| Two-build seconds | 174.339 | 175.684 |
| Primary query P95, milliseconds | 2,442.047 | 102.276 |
| Knowledge bytes | 842,070,178 | 842,070,178 |
| Model calls | 0 | 0 |
| Reported provider cost, USD | 0.00 | 0.00 |
| Execution errors / retries | 0 / 0 | 0 / 0 |
| Weighted nDCG@10 x100 | 45.43 | 72.08 |

New completed native work in this report is **246.684 job seconds** and **195.422 agent seconds**. These values exclude the still-running work of other families, controller verification time and the previously charged E13 reference. They are not total campaign wall time.

The route keeps the identifier `lexical-sql`: the empty reference profile ranks SQL substring presence, while the retained profile loads the canonical records and ranks normalized tokens with BM25. Its observed timing and quality differences reproduce that existing treatment. Timing is descriptive; the jobs ran at different times and shared host resources with other work.

The deterministic retrieval agent reports zero provider tokens and cost. Host compute has no recorded price, so a complete dollar cost is unavailable. No Luna answering or judging stage is included. The report normalizer and reconciliation dispatched zero native jobs.

[Quality and opportunity status](README.md) · [Applications and categories](groups.md) · [Aggregate](aggregate.json)
