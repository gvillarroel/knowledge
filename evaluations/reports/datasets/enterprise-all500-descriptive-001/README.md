# EnterpriseRAG: interrupted all-500 evaluation

This is a partial diagnostic report of the original eight-strategy allocation, not a completed evaluation. Four strategies settled and passed the native evidence-integrity gate. Entity Graph and Ensemble were interrupted without native result records; Graphify and Turso were not admitted. The original worker is no longer active. WSL was observed with a recent boot and both interrupted containers were stopped; the exact cause and time of interruption remain undetermined. The launcher returned an abnormal exit code.

The artifact-only native reporter explicitly used its incomplete-job mode. The unmodified native job still has no final timestamp and records four completed, two running and two pending originals at its last snapshot. Those running/pending counts are stale artifacts, not live processes. No trial was rerun, no missing result was synthesized, and the two dependent study stages are closed as stopped.

The fixed allocation permitted one attempt per strategy, zero retries and two simultaneous trials. The complete reference bundle, source inputs and 10,800-second limit were fixed before this evaluation.

Scores are native nDCG@10 multiplied by 100, across 470 retrieval-eligible questions among all 500 public questions and a corpus of 6,000 complete documents. Missing observations have unavailable quality, never an imputed zero. Legacy is the highest observed among the four qualified strategies only.

| Strategy | nDCG@10 ×100 | Original outcome |
| --- | ---: | --- |
| [legacy](skills/legacy.md) | 70.72 | Qualified |
| [embeddings](skills/embeddings.md) | 64.04 | Qualified |
| [adaptive](skills/adaptive.md) | 63.61 | Qualified |
| [classical](skills/classical.md) | 56.16 | Qualified |
| [ensemble](skills/ensemble.md) | Unavailable | Interrupted; no native result |
| [entity-graph](skills/entity-graph.md) | Unavailable | Interrupted; no native result |
| [graphify](skills/graphify.md) | Unavailable | Not admitted; no native result |
| [turso](skills/turso.md) | Unavailable | Not admitted; no native result |

This partial allocation does not establish a winner across all eight strategies. It does not complete E16's finite evolution, all-eight development qualification, paired joint replay, paired all-500 comparison or private acceptance. No candidate was selected, no private data was released, and no skill was promoted.

The cohort overlaps the 120-question development sample. These observations do not establish causal improvements, independent generalization or a position on the official 511,962-document answer-quality leaderboard.

[Applications and categories](groups.md) · [Cost, time and quality](cta.md) · [Dataset scopes](datasets.md) · [Machine-readable aggregate](aggregate.json) · [Protocol](../../../../docs/enterprise-all500-descriptive-evaluation.md)
