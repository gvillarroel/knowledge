# Native trial configuration checks

The Enterprise execution guard must read Harbor's durable `TrialConfig` as it
is written. Harbor 0.18.0 uses `exclude_defaults=True`; a missing optional field
can therefore mean its native default. E10's frozen checker instead expected a
full model dump and rejected a legitimate captured agent at
`extra_instruction_paths`. The [stopped E10 report](../evaluations/reports/evolution/e10/README.md)
preserves that result and its limits.

[`enterprise_native_trial_config.py`](../evaluations/enterprise_native_trial_config.py)
provides a prospective reader. It authenticates the complete native configuration
source and writer against fixed SHA-256 commitments, then derives omission
defaults from the source AST without executing its factories. It validates all
supported model fields, JSON types and nested mount fields before comparing the
complete effective inputs with a separately bound expected projection.

The supported contract is the local deterministic Enterprise workload. Optional
MCP servers, TPU settings and artifact-object configurations are rejected. The
reader preserves explicit supported values; it does not lowercase inputs, accept
legacy aliases, discard unknown fields, overwrite overrides or generate missing
identities. Duplicate JSON keys, non-finite values and booleans in numeric fields
are refusals. Refusal messages contain static codes rather than input values.

## Caller contract

Instantiate `NativeTrialReader` with the actual bytes of the independently bound
native configuration source and writer. Call `require_policy` with the durable
JSON, the trusted expected projection, the declared phase and the native role.
The expected projection must come from the frozen native job, task and owner
contract, with only declared generated identities and staged skill paths added.
It must not be copied from the observed configuration being checked.

| Phase | Adapter | Required agent execution override |
| --- | --- | --- |
| Development | `enterprise_agent:SkillRetrievalAgent` | Native default `None` |
| Recalculation | `enterprise_final_agent:SkillRetrievalAgent` | Explicit 10,800 seconds |
| Independent validation | `enterprise_agent:SkillRetrievalAgent` | Native default `None` |

Both the agent and separate verifier use the trial's configuration. The reader
does not infer a role from configuration or relax inputs for the verifier. The
caller must still verify each role's exact image, resources, mounts, task,
package digest and native owner lineage. A successful decode is not execution
admission or evidence of previously unobserved isolation.

## Verification and preservation

Run the independent synthetic regressions with:

```sh
python -B -m pytest tests/test_enterprise_native_trial_config.py tests/test_enterprise_execution_scope.py -q
```

The 40 tests and 125 subtests cover omitted versus explicit defaults, all eight
original overrides, complete effective-input drift, malformed JSON, identities,
types, nested mounts, source drift and all three phases with both roles. The
unit suite uses synthetic authenticated-source fixtures and does not claim a
live native admission.

A separate artifact-only parity check used all three completed public E10
durable configurations and the actual installed native configuration models.
Every effective field matched, as did the independently reconstructed declared
job/task/identity/staged-skill projection. Twelve representation and role checks
passed without a new native job, model inference or private task-body read.
That evidence does not retroactively admit E10 or create its missing receipt.

The repository completion gate passed with 1,626 tests, 359 subtests and 90.7%
total application coverage. The reader itself remains a prospective component
until its complete caller and replacement study receive independent review and
a new seal. [ADR 0136](../.specs/adr/0136-read-native-trial-configurations-with-authenticated-defaults.md)
requires preserving all three consumed starting roles, all historical claims and
E10's terminal history. The remaining nine starting roles must never become a
reason to rerun the three completed semantic outcomes.

[Documentation index](README.md) · [Enterprise family reports](enterprise-family-report-index.md)
