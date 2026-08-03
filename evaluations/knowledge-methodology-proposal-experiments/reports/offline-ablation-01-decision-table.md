# Offline Ablation 01: Quantitative Decision Table

## Reading the table

All changes are absolute metric deltas unless a relative percentage is shown.
Recall intervals are paired 95% query-bootstrap intervals when available.
Latency is median query time on the experiment machine and excludes index
construction. The qrels are exposed and non-exhaustive, so these decisions are
for the next experiment stage, not production promotion.

| Treatment or decision | Classification | GraphRAG evidence | QEC evidence | Quantitative action |
|---|---|---|---|---|
| Chunked char-TF-IDF | Works strongly | Fixed-128 raises Recall@10 from 0.6853 to 0.8215: +0.1363 absolute, +19.9% relative, 95% CI [+0.0858, +0.1902]. MRR +0.1283; nDCG +0.1476; latency 44.3x document. | Fixed-128 raises Recall@10 from 0.8625 to 1.0000: +0.1375 absolute, +15.9% relative, 95% CI [+0.0625, +0.2208]. MRR +0.3892; nDCG +0.3418; latency 59.1x document. | Continue KM-004. Keep chunking configurable and measure its cost; do not use whole-document char-TF-IDF as the default. |
| Fixed-512 hybrid | Works with a recall caveat | Recall +0.0396 (+5.1%), MRR +0.0095, nDCG +0.0345; Recall CI [-0.0033, +0.0804]; latency 32.9x document. | Recall +0.0167 (+1.7%), MRR +0.1733, nDCG +0.1498; Recall CI [+0.0000, +0.0500]; latency 20.6x document. | Keep as a cross-domain candidate. Its ranking-quality gains are large in QEC, but Recall superiority is not strong enough for promotion. |
| Fixed-512 BM25 | Useful control, not a proven Recall improvement | Recall +0.0130 (+1.7%), MRR +0.0238, nDCG +0.0153; Recall CI [-0.0413, +0.0664]; latency 17.5x document. | Recall +0.0083 (+0.9%), MRR +0.1010, nDCG +0.0832; Recall CI [-0.0292, +0.0458]; latency 12.7x document. | Retain as a simple chunked baseline. Do not claim Recall improvement; investigate its QEC early-rank gain. |
| Fixed-128 BM25 as a global default | Does not work | Recall -0.0273 (-3.5%) and nDCG -0.0105 versus document BM25, while latency rises 20.7x. MRR improves only +0.0173. | Recall +0.0083, MRR +0.0519, and nDCG +0.0428, showing a domain-specific benefit. | Reject as a repository-wide default. The GraphRAG regression contradicts a global setting. |
| Hierarchical page scoring | Inconclusive; no default justification | Versus page char-TF-IDF: Recall -0.0190, MRR +0.0158, nDCG -0.0024, latency 2.94x. | Versus page char-TF-IDF: Recall -0.0125, MRR -0.0083, nDCG -0.0088, latency 1.08x. | Do not make hierarchical scoring the default. Test only where an explicit parent-child reasoning hypothesis exists. |
| 256-token overlap | Mixed and domain-dependent | Versus fixed-256 char-TF-IDF: Recall +0.0100, MRR +0.0313, nDCG +0.0256, but latency 2.33x. | Versus fixed-256 char-TF-IDF: Recall +0.0125, MRR -0.0125, nDCG +0.0017, latency 1.18x. For hybrid it is worse on all three quality metrics and 1.17x slower. | Keep overlap opt-in. The extra cost is not consistently repaid across retrievers and domains. |
| QEC fixed-128 char-TF-IDF secondary-quality winner | Works when quality dominates cost | Versus its own document baseline, the corresponding GraphRAG treatment gains +0.1363 Recall. | Three treatments tie at Recall 1.0000. Versus fixed-512 char-TF-IDF, fixed-128 has unchanged Recall, MRR +0.0354, nDCG +0.0397, but 2.48x latency. | Use fixed-128 only when the secondary-quality tie-break gain is worth the extra latency. Do not call it a unique primary-metric winner. |
| QEC fixed-512 hybrid cost-balanced option | Works as a trade-off | It is the GraphRAG primary-metric point winner at Recall 0.8245. | Versus fixed-128 char-TF-IDF: Recall -0.0125, MRR +0.0229, nDCG +0.0054, and median latency -55.4%. | Prefer when latency and early rank matter more than the final 1.25 Recall points. |
| One global winner | Does not exist in this evidence | Point winner: fixed-512 hybrid, Recall 0.8245, MRR 0.8667, nDCG 0.7870. | Point winner: fixed-128 char-TF-IDF, Recall 1.0000, MRR 0.9521, nDCG 0.9454. | Continue KM-005. Select by domain and objective; 14 of 21 treatments remain on the measured cross-domain Pareto frontier. |
| Uncertainty-free point ranking | Does not work as a decision method | The widest Recall@10 interval across the study is 0.1625, while several treatment deltas are below 0.04. | The same registered bootstrap contract applies; small Recall gains of 0.0083–0.0167 are not large relative to sampling uncertainty. | Continue KM-006. Require intervals and practical-effect thresholds beside every point score. |

## Net decision

Proceed with configurable fixed chunking, char-TF-IDF as a diagnostic baseline,
the fixed-512 hybrid as a cross-domain candidate, and explicit uncertainty.
Reject one global chunk size, whole-document char-TF-IDF as a default,
fixed-128 BM25 as a global default, and point-only ranking. Keep hierarchy and
overlap experimental until a task-specific gain pays for their additional
cost.
