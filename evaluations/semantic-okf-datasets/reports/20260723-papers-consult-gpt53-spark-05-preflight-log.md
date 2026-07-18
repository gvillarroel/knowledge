# Campaign 05 closed-input preflight log

## Outcome

Campaign `20260723-papers-consult-gpt53-spark-05` is prepared and scheduled for
`2026-07-23T14:26:00Z`, 88 seconds after the recorded provider reset. It has
made zero model calls and contains zero runs, outcomes, or checkpoints. It is
not evaluation-complete or ranking-eligible.

Campaign 04 was disabled only after Campaign 05 passed scheduler round-trip
validation. Campaign 04 remains intact as a zero-call historical preparation.

The machine-readable authority for the values below is
[`20260723-papers-consult-gpt53-spark-05-readiness.json`](20260723-papers-consult-gpt53-spark-05-readiness.json).

## Closed snapshot

The campaign was created atomically from the reviewed Campaign 04 family
bundles. Publication copied regular files into a temporary sibling, excluded
Python bytecode, rewrote all task runtime references, produced and reproduced
the version 2 binding, and only then renamed the directory to its final path.

| Boundary | Evidence |
|---|---|
| Schedule | 320 cells; SHA-256 `f202c3c8744cc8259fddce586826768c90e896c8c180a0b2e96a0a88aaf70f7d` |
| Frozen manifest | SHA-256 `735287c53b184aee1dc4199e8d65e7faa8feac089d72f98bde95a122ee1e5dc2` |
| Version 2 binding | SHA-256 `1df029a35e6566f8602db46dfbd6b7b8b9cfa5c24ddd5789304216b5210f0d80` |
| Frozen repository | 4,743 files; 1,231,705,118 bytes; tree `17b13a04b45696ea63740a7ed82f7369761afdc98035913fd62970a89ddd460c` |
| Offline model | 11 files; 91,607,178 bytes; tree `989cb896bc4eebf640856e79bd08eea0c7b59e51a300fad1e0d7b359c87ef804` |
| Links and bytecode | 0 symlinks, 0 shared hardlinks, 0 `.pyc`/`.pyo`, 0 `__pycache__` directories |

The exact model is
`sentence-transformers/all-MiniLM-L6-v2@1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
Its files are independent regular files rather than links into the shared host
cache.

## Runtime and Harbor

The qualified runtime image is
`sha256:bcd2b2b57b968ff8b4976bedf8c5ddf7b7e2ff41c341f7a13a05ae4df2ffc9d8`.
Dockerfiles use the content-addressed local tag whose suffix contains that
complete ID. The runner re-resolves the tag before and after every live wave.

The image was probed with networking disabled and reported Python 3.12.13,
Node 22.23.1, npm 10.9.8, and Pi 0.73.1. It contains no model weights. A real
`adaptive/q001` verifier image also built successfully with `--network none`.

Harbor 0.18.0 is vendored inside the campaign. Its qualified Pi adapter source
hash is `ae6214…91868`; the patched adapter hash is `97ea1f…0a834`. The patch
uses the preinstalled Node and Pi packages and removes trial-time nvm/npm
installation. The complete 82-package host Harbor inventory is bound.

## Dry runs and forensic boundary

The atomic preparation dry run and a separately invoked WSL dry run both
returned the same version 2 binding:

```text
1df029a35e6566f8602db46dfbd6b7b8b9cfa5c24ddd5789304216b5210f0d80
```

The external reproduction completed in 591.9 seconds from the campaign-local
repository, model closure, task tree, skills, and Harbor entrypoint. Neither
dry run invoked Harbor live execution or Pi.

The campaign-local auditor then emitted
[`preflight forensic Markdown`](20260723-papers-consult-gpt53-spark-05-preflight-forensic.md)
and [lossless JSON](20260723-papers-consult-gpt53-spark-05-preflight-forensic.json).
They report 0/320 evaluable trials, no winner, and explicit invalidity for
comparison while execution is pending.

## Access and scheduler controls

Windows inheritance and broad sandbox ACEs were removed from both the Pi auth
directory and `auth.json`. Only `villa`, `SYSTEM`, and `Administrators` remain;
WSL verified the required credential slot without printing or hashing a
secret. The frozen tree, bundles, schedule, manifests, binding, and launcher
are protected read/execute inputs for `villa`. Output locations remain
writable.

The registered action first verifies launcher SHA-256
`cd248e54a7272169a1cabab6663ee5c32c8687d51d4704752ad03293179c7600`
before executing it as WSL user `villa`. The launcher independently checks the
three campaign sidecars, the runtime tag-to-ID mapping, auth shape, Docker,
Harbor, network reachability, and another complete dry run. No live shard is
possible before `2026-07-23T14:24:32Z`.

`SemanticOKF-Campaign05` round-tripped as Ready and enabled with:

- `InteractiveToken` and limited run level;
- `IgnoreNew`, `StartWhenAvailable`, and `WakeToRun`;
- `RunOnlyIfNetworkAvailable` plus an unauthenticated HTTPS reachability check;
- three 15-minute task retries and a 72-hour execution limit; and
- forensic summary after every terminal launcher path, with strict summary
  only after a completed checkpoint.

`SemanticOKF-Campaign04` is disabled and preserved. It was not deleted.

## Repository validation

| Gate | Result |
|---|---|
| Focused campaign/binding/summary tests | 20 passed |
| Full repository suite | 1,855 passed, 10 skipped |
| Coverage gate | 733 passed; 90.9% application coverage; 80% required |
| Dataset registry | Astro and GraphRAG Papers passed; eight families each |
| Runtime pin validation | Passed |
| Python compilation | Passed |
| Diff whitespace check | Passed |

The initial unqualified full-suite command imported `knowledge` from an
unrelated editable worktree and failed during collection. Repeating with this
checkout's `src/` first in `PYTHONPATH` produced the authoritative full-suite
result above. The coverage gate already applies that isolation itself.

## Next transition

After the provider reset, the launcher performs cheap readiness retries and a
complete campaign-local dry run. Only then may `adaptive/q001` become the
counted quota preflight. A successful preflight permits the fixed balanced
matrix to continue; any provider or binding failure stops new submissions and
remains non-semantic evidence.
