# Exact campaign helper sources

These are byte-for-byte source copies of the four workspace helpers used in
the e5 construction-profile study. The [manifest](manifest.json) records their
SHA-256 values; the live versions remain in the ignored `tmp/e5` workspace.
This directory contains code and source commitments only.
Its Git attributes preserve LF line endings so source hashes remain stable
across Windows and Linux checkouts.

- [Native report normalization](normalize_native.py) invokes the installed
  Harbor reporter on completed development or terminal validation jobs.
- [Supported merge preparation](prepare_merges.py) verifies the native archive,
  full profile, ordered complementary plans and predecessor binding before
  realizing the four permitted combinations. Its exact source was independently
  qualified before the actual generation-one preparation.
- [Completed generation registration](register_generation.py) binds native jobs,
  their archive and reviewed reports to the active organizer stage, preserving
  existing evidence and retaining native error counts.
- [Interrupted generation normalization](normalize_interruption.py) preserves
  complete-job comparisons and a separately labeled incomplete native report.
  It hashes sources before and after reporting and starts no evaluation or
  recovery. This helper was added after the runtime interruption; it is not a
  change to the frozen execution controller.

Their path-based imports require execution from the registered study workspace,
`tmp/e5`. Preserve existing files and match the manifest before restoring a
missing helper there. Running these archival copies in this directory is not a
supported entry point. The [operating guide](../../../docs/retrieval-profile-evolution.md)
explains the study boundaries and required stage order.

[Experiment overview](../README.md) · [Published e5 evidence](../../reports/evolution/e5/README.md)
