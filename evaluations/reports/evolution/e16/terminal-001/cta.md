# EnterpriseRAG E16: cost, time and quality

Native Harbor validation confirms that both jobs completed with execution exceptions. Each used one attempt, two configured CPUs and a 6 GiB memory limit. The two trials ran concurrently. Agent time and total trial time are separate observations; their sum is not campaign wall time.

| Strategy | Outcome | Agent seconds | Trial seconds | Qualified nDCG@10 | Provider USD |
| --- | --- | ---: | ---: | ---: | ---: |
| entity-graph | AgentTimeoutError | 3600.015 | 3647.179 | Unavailable | Unavailable |
| ensemble | AgentTimeoutError | 3600.017 | 3646.515 | Unavailable | Unavailable |

Token and provider-cost observations are missing and remain unavailable. No remote generative-model calls were requested. Host, electricity and orchestration costs were not measured. Neither timeout should be classified as a new retrieval-quality loss.

Read-only process observations showed Entity Graph continuing in its main process; Ensemble reached its second construction before timeout. These observations do not attest to completed output, byte equality, query coverage or a verifier score. Memory samples are point observations, not a complete peak measurement. The native terminal exception in both cases is timeout.

The previously measured six-family resource results remain in the [retained CTA report](../../e15/terminal-001/cta.md).

[Back to E16 outcome](README.md).
