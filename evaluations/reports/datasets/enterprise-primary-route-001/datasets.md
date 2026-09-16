# EnterpriseRAG: dataset and treatment boundaries

| Dataset condition | Questions | Eligible | Documents | Highest observed | nDCG@10 x100 | Coverage |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| Source-linked all-500 catalog | 500 | 470 | 6,000 | legacy, turso | 70.72 | 7/8 qualified; mixed declared treatments |
| Historical stratified development | 120 | 112 | 6,000 | legacy, turso | 72.38 | Six retained observations |
| Official full-corpus answer benchmark | 500 | Different scoring contract | 511,962 in the retained reference | No new measurement | Not applicable | No new generated-answer evaluation |

The historical 120-question cohort overlaps the 500-question cohort. Different question scope, runtime conditions and prior exposure prevent interpreting the difference as paired improvement. The new two-original study changes only Entity Graph and Ensemble's outer route workload and adds progress instrumentation. It does not turn the eight rows into one matched native experiment.

[Full catalog](README.md) · [Historical development](../enterprise-rag-stratified-development-120.md) · [Other internal datasets and their evaluated skills](../../../COMPARISON-REPORTS.md)
