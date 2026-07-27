# Python Runtime

## Base environment

CPython 3.12 is the compatibility baseline for the package-local lock. Create and activate an isolated environment, then install and verify the base runtime:

```bash
python -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version"
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

On Windows PowerShell, run the same version assertion against the exact `python.exe`
you intend to use, create the environment with that interpreter, then activate it
with `.\.venv\Scripts\Activate.ps1`. Do not rely on a launcher alias that may select
a different installed minor version.

Set `PYTHONDONTWRITEBYTECODE=1` or invoke the entry points with `python -B` when the copied skill root itself must remain byte-for-byte read-only. Build outputs are unaffected; this only suppresses ordinary Python `__pycache__` files beside imported package scripts.

The Python lock contains PyYAML, RDFLib, pySHACL, and OWL-RL for the authoritative core. Tika and MALLET are deliberately external: the skill accepts explicit paths to an unpacked Apache Tika `4.0.0-beta-1` application distribution, an unpacked MALLET `2.1.0` binary distribution, and a Java 17-or-later executable. It never downloads or replaces them.

Run the full preflight with explicit paths:

```bash
python scripts/runtime_smoke.py --java JAVA --tika-home TIKA_HOME --mallet-home MALLET_HOME
```

The preflight checks required classes, versions, every JAR hash, and a path-independent tree digest. It requires all three arguments; there is no argument-free external-runtime smoke. Do not substitute the single legacy Tika JAR, a MALLET source checkout, another topic-model implementation, or an unpinned preview build.

## Determinism limits

The contract fixes the Tika handler check, Java locale and timezone, MALLET version, sampler seed, one-thread execution, priors, iteration schedule, vocabulary filters, and eight-decimal serialization. Require two byte-identical clean builds on the release platform. Preserve the Python lock, Java version, JAR inventories, platform, and both tree digests in evaluation evidence; do not claim cross-platform byte identity until it has been measured.

## Resource limits

The core builder and retrieval projection retain normalized records, the token corpus, and topic matrices in memory. Exact JSONL output is appropriate for ordinary local research collections. Partition collections upstream when these no longer fit comfortably in memory. Do not silently skip records or publish a partial projection.
