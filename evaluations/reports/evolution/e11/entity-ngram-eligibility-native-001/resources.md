# Construction resource evidence and bounded transfer opportunities

The native Entity trial reached its second builder invocation. At 2026-09-10T21:38:43.281198+00:00, the live command targeted `rebuild` and its cgroup was at the unchanged 6 GiB memory limit. The [native outcome](README.md) records the original dispatcher's eventual result. This resource snapshot itself contains no quality score.

| Native cgroup observation | Value |
| --- | ---: |
| Current accounted memory | 6,442,434,560 bytes |
| Configured memory limit | 6,442,450,944 bytes |
| Peak accounted memory so far | 6,442,708,992 bytes |
| Current swap | 1,671,512,064 bytes |
| Peak swap so far | 4,061,745,152 bytes |
| Major page faults so far | 5,346,995 |
| Local memory-limit events so far | 408,617 |
| OOM kills so far | 0 |
| CPU throttle events so far | 0 |

The kernel counters establish swap use and memory pressure for this container. They do not identify the Python allocation responsible or prove a future improvement. `memory.peak` is a cgroup-lifetime observation and the kernel permits temporary excursions above `memory.max`. See the [kernel memory-interface definitions](https://www.kernel.org/doc/html/v6.6/admin-guide/cgroup-v2.html) and [pressure definitions](https://docs.kernel.org/accounting/psi.html). The earlier Docker CLI memory figure excludes cache and is a separate observation; see [Docker's definition](https://docs.docker.com/reference/cli/docker/container/stats/).

Source inspection identifies overlapping RDF and projection state in the Entity builder. A prospective two-file transfer can reuse Ensemble's existing lifetime boundaries while keeping every validation. This is an unreserved hypothesis, not a generated or qualified candidate.

The reverse transfer has a different constraint: Ensemble can potentially reuse the Entity matching automaton and extraction eligibility function, but it must preserve its own `DERIVED_ROOTS` and `core_inventory` behavior. Copying the entire Entity model would include the wrong core-file exclusions. The source comparisons preserve that distinction explicitly.

The unchanged Entity consultant has a separately measurable extraction cost in the retained synthetic profile. Any transfer there must remain a consultation-only treatment with the complete builder frozen.

All three opportunities require their own reservation, realization and evidence before use. Claims remain 87 of 585. No native retry, new model call, candidate mutation or private release occurred. [Exact observations, source hashes and limitations](resource-diagnosis.json).
