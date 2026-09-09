# Graphify: preserved public fixture comparator failure

The first fixed public host fixture run stopped at its required cross-layout
query comparison. It remains **failed**. Both implementations completed the
singleton fixture in both physical layouts before that stop; the remaining
three fixtures and all negative-validator checks were not executed.

| Observed scope | Result |
| --- | --- |
| Paired positive layout cells completed before the failed cross-layout gate | 2 of 8 planned |
| Original/candidate arm cells completed | 4 of 16 planned |
| Ordinary generated-expert constructions | 8 |
| Explicit deterministic check rebuilds | 4 |
| Read commands | 78 |
| Negative-validator commands | 0 of 16 planned |
| Recorded top-level command exit codes | All 90 were zero; the subsequent comparator assertion failed |
| Elapsed host time | 71.50 seconds |
| Harbor jobs or model calls | 0 |

Inspection of all twelve completed cross-layout native query pairs identified
one differing root field: `read_only_sha256`. The pinned native CLI appends this
hash over the complete physical knowledge snapshot. Each reported value matches
an independently reconstructed path/size/file-hash inventory for its own
snapshot. The physical snapshots legitimately differ between layouts.

The fixed comparator accounted for three record-level physical fields but
omitted this root snapshot commitment. All other fields in those twelve native
query pairs were identical. Within each layout, the complete original and
candidate generated packages and all 24 native/enriched query-payload pairs
were exactly equal. Those limited positive observations do not override the
failed whole-design gate.

The original 424-file execution artifact is immutable and bound in the E8
ledger. Its twelve construction commands and 78 reads remain consumed costs.
A separately reviewed new public fixture design may verify every native
snapshot hash against its own folder before excluding that exact field only
from the cross-layout comparison. Its new full-run allocation must count the
original costs, preserve all other checks, and leave both candidate and source
inputs unchanged. The original run is not resumed or relabeled as passing.

This is host correctness evidence for synthetic inputs. It supplies no full
fixture pass, full-workload feasibility, EnterpriseRAG retrieval score, candidate
acceptance or installation. The native feasibility allowance remains unconsumed.

[Observed counts and source commitments](aggregate.json) ·
[Sealed builder candidate](../graphify-candidate-001/README.md) ·
[Separate native task-binding correction](../graphify-task-binding-001/README.md) ·
[Campaign](../README.md)
