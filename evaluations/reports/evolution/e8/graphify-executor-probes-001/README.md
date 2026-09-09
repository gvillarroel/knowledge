# Graphify: exact package and resource probes passed

Two serial probes passed in the pinned agent and verifier images. They establish
that the declared direct Docker environments load the expected package and
enforce the checked resources and mounts. The complete EnterpriseRAG builder
trial remains pending; these probes produce no retrieval score.

| Observed check | Agent image | Verifier image |
| --- | --- | --- |
| Effective CPU limit | 2 | 2 |
| Effective memory limit | 6 GiB | 2 GiB |
| Network interfaces | Loopback only | Loopback only |
| Exact read-only bind mounts | 3 | 4 |
| Initial workspace and external knowledge | Empty | Empty |
| Undeclared host, memory and socket paths | All 7 absent | All 7 absent |
| Complete staged candidate | All 252 files matched | No candidate present |
| Runtime implementation | Four image files matched | Not imported |
| Module-definition imports | Exact builder and consultant paths/hashes | None |
| Package after imports | All files unchanged | Not applicable |
| Reference access | No reference mounted | Synthetic canary only; write denied |
| Exit code | 0 | 0 |

The driver explicitly selected and checked the Python entrypoint and command,
actual image identity, source and destination of every mount, mount count,
resource configuration and complete typed result payload. Container checks also
read the effective cgroup limits and verified that CPU quota and period were
positive. The whole initial workspace was checked, including task-specific
output locations. Query-file presence and input permission bits were inspected;
question, relevance and source bodies were not read by the probes.

The candidate was copied to Harbor's conventional `/harbor/skills` location as
a complete package. The agent imported only the two module definitions. It did
not construct a snapshot or call a query, validator, scorer or model. The
verifier's canary contained no actual reference data. Both temporary containers
were removed after their single execution.

Independent review passed 78 isolated cases against the exact final driver and
container probe. It found and corrected three issues before the first execution:
an unbound effective entrypoint and permissive result payload, an incomplete
initial-workspace check, and acceptance of a nonpositive synthetic CPU quota.
The unexecuted prior sources and their counterexamples remain preserved.

These are direct Docker probes. Actual Harbor-generated writable log mounts,
native skill staging, task and skill locks, submitted package identity and
full-workload qualification remain obligations of the separately reviewed
native caller. Read-only input permission bits do not prevent UID zero from
overriding baked-image permissions; the design retains its trusted-host boundary.

The allocation consumed two container starts with one worker, zero retries and
a 60-second limit per Docker operation. It consumed zero native feasibility
trials and zero model calls. The earlier complete public artifact-parity pass
and unchanged candidate remain prerequisites. This result does not establish
native speed, an EnterpriseRAG gain, private acceptance or skill installation.

[Exact observations and commitments](aggregate.json) ·
[Complete public artifact parity](../graphify-fixture-success-002/README.md) ·
[Task and runtime binding](../graphify-task-binding-001/README.md) ·
[Campaign](../README.md)
