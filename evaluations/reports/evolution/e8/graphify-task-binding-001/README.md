# Graphify: exact fixed-builder task binding

The first prospective native feasibility configuration would be rejected by the
original task's verifier: that contract permits changes only to the retrieval
profile and binds every builder file to its original digest. This was detected
before any feasibility trial. The original proposal remains preserved and
unexecuted.

A second proposal now contains a separately versioned task. It changes exactly
one expected file digest in `tests/contract.json`, binding the sealed Graphify
builder asset to its actual bytes. The remaining seven task files are byte
identical, and all other parsed contract values are exactly equal. The mutable
path list is unchanged. Questions, relevance references, source records,
verifier/scoring code, images, routes and resource limits are preserved.

| Preparation check | Observed result |
| --- | --- |
| Complete candidate files matched against fixed expectations | 252 |
| Candidate files incompatible with the original fixed contract | 1 |
| Versioned task files | 1 of 8 |
| Changed parsed contract values | One exact expected builder-file digest |
| Broadened mutable paths | 0 |
| Native Harbor 0.18 configuration/import preflight | Passed for the second proposal |
| Independent exact task-binding audit | Passed; six isolated file/import-binding probes |
| Actual pinned image runtime inspected | Four files, through a container that was never started |
| Feasibility native trials, created studies or execution admissions | 0 |

The changed path is
`assets/families/graphify/builder/scripts/_graphify_projection.py`.
Its fixed expected digest changes from
`f52b62934248497726e950308b2e99f2751d739522ac91ca901dd8401d19e987`
to
`257cf75c3419bafcf100371d95a48a6350b75a6cd74558544394e76b61903a19`.
This explicitly declares the intended construction treatment; it does not
allow arbitrary builder changes.

The independent audit verified the exact task delta, all 252 candidate files,
four candidate object seals and twelve proposal source commitments. Its six
isolated probes confirmed original-contract rejection, exact new-file
acceptance and rejection of missing, extra or changed fixed files. The inherited
mutable profile remains unchanged in the verifier, so native qualification must
also compare the complete submitted package against the exact frozen source.

Static inspection of the actual pinned image confirmed its four runtime files.
The bridge fixes construction subprocesses at 2,400 seconds, builds and validates
two source-packed snapshots, checks their equality and verifies unchanged skill
and knowledge inventories after consultation. Its SHA-256 is
`c2b305449f7b1b97a40c739207f6d89a4f753b4266b22ae52b096b46a90341a1`.
The temporary inspection container had no mounts, was never started and was
removed. This establishes image file identity, not effective runtime access or
the modified builder's performance.

The new task still requires a new native checksum. Complete public fixture
validation, actual runtime/source isolation, terminal E8 work
and a sealed design remain prerequisites. The single native feasibility-trial
cap applies across proposal versions. Nothing here establishes construction
feasibility, retrieval gain, all-500 completion or acceptance.

[Task-binding decision](../../../../../.specs/adr/0133-version-exact-builder-bindings-in-feasibility-tasks.md) ·
[Sealed candidate](../graphify-candidate-001/README.md) ·
[Original native failure](../graphify-baseline-failure-001/README.md) ·
[Preparation commitments](aggregate.json) · [Campaign](../README.md)
