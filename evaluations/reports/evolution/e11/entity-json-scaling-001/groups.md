# Public development input size by application

This is metadata from the nine already bound development document files.
Character counts describe raw body fields, not generated records, tokens
accepted by a retriever, quality, or the private validation cohort. No
document content or identities are included.

| Application | Documents | Median body characters | p95 body characters | Maximum body characters |
| --- | ---: | ---: | ---: | ---: |
| confluence | 543 | 10004 | 16418 | 22516 |
| fireflies | 139 | 11701 | 26068 | 33976 |
| github | 312 | 4886 | 7339 | 13836 |
| gmail | 1336 | 7266 | 9900 | 13715 |
| google-drive | 647 | 7282 | 12946 | 18401 |
| hubspot | 321 | 2940 | 4946 | 7049 |
| jira | 584 | 5620 | 7802 | 10219 |
| linear | 991 | 5409 | 9341 | 15422 |
| slack | 1127 | 3388 | 6330 | 15508 |

Total: 6,000 documents and 37,183,736 raw body characters; pooled median
5,869, p95 11,897 and maximum 33,976. Quantiles use nearest rank.

The separately generated profile inputs have 256 and 1,024 synthetic
records, each with an 8,192-character body. They provide no application-level
retrieval scores. Existing scores remain in the [family index](../../../../../docs/enterprise-family-report-index.md).

[Diagnostic](README.md) · [CTA](cta.md) · [Aggregate](aggregate.json)
