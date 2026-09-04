# ILC Deterministic Source Allowlist Export Rehearsal 1319 v0.1

**Status:** DRY-RUN REHEARSAL ONLY, NO PUBLICATION.
**Phase:** 1319.

```text
deterministic_source_allowlist_export_rehearsal_phase_1319.v0.1
public_rc_exclude_marker_scan_zero_exported_markers_phase_1319
stripped_helper_import_scan_zero_phase_1319
legacy_untagged_review_results_recorded_phase_1319
source_export_rehearsal_no_publication_phase_1319
phase_1320_release_artifact_manifest_instance_rehearsal_next
public_rc_remains_blocked_after_phase_1319
```

## Verdict

- Result: `pass`.
- Included files: `536`.
- Excluded files: `7590`.
- Exported marker hits: `0`.
- Stripped-helper dependency hits: `0`.
- Blocked ambiguities: `0`.
- Expected manifest hash: `19e5ec480afa00809afb124552bfb12add5bf321b35d88f302262d846413e980`.

## Scanner Scope

The rehearsal scans a deterministic source/package candidate set and does not copy files into a public export tree.
Marker scanning is performed on included file bytes after candidate selection.
Dependency scanning uses Python AST static imports for Python files and exact path/module text patterns for non-Python files.
Dynamic imports and runtime-generated dependency edges remain out of scope and are recorded as scanner limitations.

## Non-Claims

This rehearsal is not public source export, not source publication, not package publication, not release artifact production, not release signing, and not a public RC claim.
Public RC remains blocked after Phase 1319.
