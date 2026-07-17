# Ensemble ranking determinism

Status: **pass** for the deeply validated bundle and the frozen forty-question, top-ten ranking.

| Policy | Repetitions | Process scope | Ranking SHA-256 | Equal |
| --- | ---: | --- | --- | ---: |
| `fast` | 3 | one fresh process | `58ffec9f7ec18413e3cd397f874be81014976b850f8f9b168637d038b8e3d835` | yes |
| `robust` | 3 | one fresh process | `1cd400efd0d3b936cacb7a8bbc98b7d3053265256c0b58b4ce7c8ee2e8a3c90c` | yes |
| `quality` | 4 | three in one fresh process and one in a second fresh process | `a8c94ecbe6967993a7920edd06e62c4cbefad27513b9445740294684329c3346` | yes |

All observations use the exact independently rebuilt `final-03` bundle. The ranking identity hashes
question ID plus each hit's rank, canonical paper ID, source ID, record ID,
and retained-text hash. Timing is deliberately excluded. The quality observation uses the runtime
after canonical paper-ID normalization; pre-fix rows are not accepted evidence for this report.
