# Cost, time and scope: Entity consultant runtime fixture

One pinned container completed a paired public compatibility fixture. Both roles
passed two nonempty queries through each of four routes, with exact payload and
deep-inspection parity. No EnterpriseRAG native job or proposal was added.

| Observation | Parent | Candidate |
| --- | ---: | ---: |
| Child Python process seconds | 1.981745 | 1.929649 |
| Deep snapshot load seconds, included in process time | 0.857760 | 0.822399 |
| Deep validations | 1 | 1 |
| Nonempty query payloads | 8 | 8 |
| Exit code | 0 | 0 |

Container wall time was 6.960122 seconds. It includes
staging and fixture orchestration and is a different observation from the child
process times. Deep-load time is already included in each process time; do not
add it again. There is one observation per role, parent first, with no randomized
order or cache control. These timings are descriptive and do not support a causal
speedup, performance ranking or extrapolation to the complete corpus.

| Scope and resources | Value |
| --- | --- |
| Public processed records / snapshot files | 128 / 145 |
| Python | 3.12.13 |
| CPU quota / memory limit | 2 CPUs / 6 GiB |
| Network | None |
| Snapshot storage | Same container-local staged copy; byte parity checked after execution |
| Maximum child time / fixture time | 300 s each / 660 s total |
| Actual child commands / builds | 2 / 0 |
| Native Harbor jobs / retries | 0 / 0 |
| New proposal charges / quality misses | 0 / 0 |
| Cumulative proposal claims | 86 / 585 |
| Peak memory | Not observed |
| Model tokens / USD cost | Not observed; no model call in this fixture |
| EnterpriseRAG score / official rank | Unavailable for this candidate |
| Full-workload qualification / promotion | Pending / none |

The [aggregate](aggregate.json) preserves exact observations and source commitments.
The [software candidate](../entity-consultant-token-automaton-001/README.md) and
[prior native timeout](../entity-token-automaton-native-001/README.md) remain separate,
immutable checkpoints. [Report](README.md) · [E11](../README.md)
