# Native generator construction adapter

This adapter runs one declared generator CLI request in a native Harbor task.
It measures construction contracts without model calls. Follow the
[generator evolution guide](../../../docs/knowledge-generator-evolution.md) and
[study playbook](../../../docs/knowledge-skill-evolution-playbook.md) before using
it for evaluation or promotion.

`materialize.py` accepts an authored case root containing per-case `input/`,
`request.json` and private `tests/test.sh` trees. It builds source-only images from
an existing pinned runtime, creates separate verifier containers, and rejects
links and output overwrites. Immediately repeat with `--check` to verify exact
deterministic task replay. Set temporary/cache directories inside the authorized
project. Keep all case trees, native tasks, candidates and jobs ignored.

```powershell
python evaluations/integrated-semantic-okf-knowledge-skill/evolution/materialize.py --cases <cases> --output <native-tasks> --image <pinned-local-runtime>
python evaluations/integrated-semantic-okf-knowledge-skill/evolution/materialize.py --cases <cases> --output <native-tasks> --image <pinned-local-runtime> --check
```

The runtime must contain `/opt/generator-study/run_generator.py` and the pinned
family dependencies. `native_agent.py` is the host-side Harbor agent import. Its
setup probes that only loopback is available, `/dataset` is read-only and private
tests are absent. The request wrapper accepts a closed schema, validates source
and output boundaries, records source hashes before/after execution, and writes
`/workspace/result.json`. A generator rejection remains a valid execution for the
independent verifier to assess; transport failures are execution errors.

Artifacts explicitly map `/workspace` to `workspace` and `/logs/artifacts` to
`published-artifacts`. In Harbor 0.18.0 the explicit convention destination uses
copying, avoiding an unguarded host directory inspection implicated in G1's
intermittent EIO abort. It does not disable native log bind mounts or establish the
filesystem root cause. Require a native public transport preflight before sealing
an execution profile and inspect artifact manifest status before treating a job
as evaluable. Never hide failed collection as a semantic zero or rerun private
trials without the applicable maintained recovery contract.

Freeze this adapter with the task trees, runtime/image IDs, protocol and candidate
digests. A later transport change belongs in a fresh prospective execution study;
do not rewrite earlier sealed tasks or incomplete native job roots.
