# EnterpriseRAG: dataset scopes

| Condition | Questions | Eligible | Documents | Highest observed strategy | nDCG@10 ×100 | Evidence coverage |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| Interrupted all-500 public observation | 500 | 470 | 6,000 | legacy | 70.72 | 4/8 qualified originals |
| Historical stratified development | 120 | 112 | 6,000 | legacy, turso | 72.38 | Six E14 observations; two E16 timeouts |
| Official full-corpus answer benchmark | 500 | Different contract | 511,962 | No new measurement | Not applicable | No new result in this study |

The two internal cohorts overlap. Their scores use different query populations and agent limits; do not subtract them as a paired improvement or pool them as independent evidence. The historical full-corpus Classical retrieval and Luna answer-generation treatments remain separate.

[All-500 table](README.md) · [Historical E16 closure](../../evolution/e16/terminal-001/README.md) · [Repository dataset catalog](../../../COMPARISON-REPORTS.md).
