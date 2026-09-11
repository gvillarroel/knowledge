# Bound Windows task-tree publication retries

Status: Accepted. Date: 2026-09-11.

## Context

Application coverage runs 050 and 051 both failed while the deterministic
generator adapter renamed a completely staged task directory into its final
location. Windows reported `PermissionError` with `WinError 5`. The same
materializer test passed in an intervening isolated run. These observations
establish intermittent publication failure, but do not identify the process
or operating-system component responsible. Run 050 also had a Confluence
publication failure; that test passed in the isolated check and in run 051.

The [coverage exit-status contract](0146-preserve-pytest-exit-status-in-coverage-checks.md)
correctly rejected both full runs. Historical coverage success cannot override
their failed tests.

## Decision

In the generator adapter, retry only the final directory rename after Windows
access-denied, sharing-violation or lock-violation `PermissionError` codes
5, 32 or 33. Microsoft defines these
[Windows error codes](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-);
they do not, by themselves, prove that a failure is temporary.

Allow five attempts with four delays of 0.05, 0.1, 0.2 and 0.4 seconds. Propagate
the final error, other Windows codes and errors without a Windows code. Check
for an existing destination, including a symlink or junction, before each
attempt. Keep the same `Path.rename` operation; on Windows its underlying
[`os.rename` rejects an existing destination](https://docs.python.org/3/library/os.html#os.rename).
Do not introduce replacement, copying, deletion, permission changes or another
task-construction pass as recovery. Existing deterministic replay and temporary
directory cleanup semantics remain unchanged.

Exercise transient failures, the persistent-failure bound, immediate propagation
of unrelated errors and a destination created during the retry delay. Preserve
the original failing coverage logs and require a fresh full application gate.

## Consequences

This correction gives a short access conflict time to clear while a persistent
failure remains visible. It does not claim to repair a particular Windows
service, or extend the same behavior to other publication code without evidence.
The adapter and its tests are outside E14's frozen execution source map. No
native evaluation, candidate, dataset, consumed identity, quality miss or
proposal allowance is retried or changed by this software correction.
