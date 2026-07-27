# Negative-case matrix

This matrix is part of the experiment acceptance evidence. Every case must fail
closed without publishing a partial destination or changing an inspected bundle.

| Boundary | Injected condition | Required result | Automated evidence |
| --- | --- | --- | --- |
| Ingestion plan | Parent traversal, absolute path, or unknown field | Reject before discovery | `test_ingestion_plan_is_closed_and_paths_are_portable` |
| Source membership | Glob matches no regular file | Reject the source as incomplete | `test_unmatched_and_oversized_sources_fail_closed` |
| Source size | Selected file exceeds `max_input_bytes` | Reject before Tika execution | `test_unmatched_and_oversized_sources_fail_closed` |
| Source path | File or ancestor is a symlink/reparse point | Reject lexically without following it | `test_source_symlink_or_reparse_point_is_rejected` |
| Source stability | Original file changes after its private copy | Tika still reads only the bound snapshot | `test_tika_uses_one_private_raw_snapshot` |
| Tika handler | Default output differs from explicit `--md` | Reject extraction | `test_tika_runs_default_markdown_explicit_markdown_and_json` |
| Tika receipt | Metadata, body, raw hash, or closed tree is stale | Reject validation and search | `test_tika_metadata_tamper_is_rejected_before_search` |
| MALLET process | Non-zero exit or an error marker with exit zero | Reject and publish nothing | `test_mallet_command_detects_exit_zero_errors_and_retries_transient_jshell` |
| MALLET runtime | Hash-bound jar changes after preflight | Reject before Java execution | `test_mallet_classpath_is_explicit_and_rechecked` |
| Classical tree | Unknown, missing, linked, or malformed artifact | Reject inspection | `test_closed_classical_tree_and_toolchain_binding_reject_tamper` |
| Authoritative core | Unknown concept directory or linked entry | Reject before ranking | `test_closed_concept_tree_rejects_unknown_and_linked_entries` |
| Deep scratch | Temporary root points inside bundle or MALLET home | Reject without creating bundle files | `test_deep_scratch_rejects_bundle_temp_root` |
| Publication | Destination exists, appears concurrently, or is a dangling link | Never replace it; remove private work | `test_no_replace_publication_preserves_concurrent_destination` |
| Candidate setup | Private workspace creation fails | Remove the Tika stage and leave no destination | `test_candidate_setup_failure_cleans_tika_stage` |

The real-tool run complements these unit cases with two clean builds, two
published-bundle validations, independent consultant retraining, a fusion query,
and complete path-and-hash inventory equality. It is not a retrieval-quality or
production-readiness claim.
