# ILC Public Mirror Manifest 1573n v0.1

**Phase:** 1573n
**Window:** 1565-1575
**Date:** 2026-07-08
**Sensitivity:** NON-SENSITIVE
**Status:** committed rehearsal evidence

## Purpose

This document records the Phase 1573n Option C public mirror rehearsal. The
private canonical repository was transformed into a sanitized staging mirror
under `/tmp/ilc-public-mirror-1573n` by
`tools/scripts/generate_public_mirror.sh`. The staging mirror was then deleted.

No public repository push, public RC activation, release signing, package
publication, guard clearance, wallet write, minting, or settlement occurred.

## Manifest Values

| Field | Value |
|-------|-------|
| `pipeline_version` | `generate_public_mirror_1573n.v0.1` |
| `source_private_commit` | `33667341ca661ea4a70ed9f1d515bd503393399b` |
| `filtered_public_head_sha` | `636ff974061793d12f57308e95fac640b9697e07` |
| `canonical_hash` | `sha256:5aa97a4ca76b6560802d31067428cc8fc5482c3ccebc9669509c36a710041804` |
| `commit_count_before` | `4186` |
| `commit_count_after` | `2848` |
| `commit_count_min_required` | `2511` |
| `excluded_path_count` | `7117` |
| `denylist_scan_result` | `pass` |
| `public_rc_exclude_scan_result` | `pass` |
| `author_rewrite_result` | `Genesis Agent <ilcops@proton.me>` |
| `pipeline_duration_seconds` | `178` |
| `no_push` | `true` |
| `publication_authority` | `none - push gated to Phase 1575` |

## Public Mirror Maintenance Policy

The private canonical repo (`/Users/jamison/Documents/ILC_Main/01_Current`) is
the single source of truth. All development occurs there.

The public mirror (`ILC-Foundation/ilc`) is a derived artifact, regenerated from
the private repo via `tools/scripts/generate_public_mirror.sh`. It is never
hand-edited.

Each public mirror update requires running the full pipeline, producing a
manifest, and recording `source_private_commit` to `filtered_public_head_sha`
traceability.

No manual patches to the public repo are permitted. Contributor PRs on the
public repo are reviewed and applied to the private canonical repo; the next
mirror cycle propagates them back to the public mirror.

The public push, whether Phase 1575 or a post-RC mirror-release phase, uses
force-push replacement of the public mirror with the latest filtered output.
This is expected because the public mirror is a derived snapshot of canonical
history, not a diverging branch.

The header-anchored `PUBLIC_RC_EXCLUDE` detector is an interim fail-closed
control, not the final ILC-native package builder. Once Fix38/Fix65+ close
source-node coverage and a ratified LMDB field such as
`public_mirror_category: public | internal | review_required | private_excluded`
exists on graph nodes, the public mirror exclusion list should be generated
from Atlas/AtlasSliceManifest metadata and source digests. Phase 1573n records
this as forward planning only and does not claim graph-derived export is already
implemented.

## Recorded Tokens

```text
public_mirror_is_derived_artifact_not_source_of_truth
sanitized_repo_updates_require_reproducible_filter_manifest
no_manual_public_repo_patches_policy
public_push_requires_clean_denylist_and_exclude_scan
graph_derived_public_mirror_export_routed_to_window_1576_plus
```

## Non-Claims

This manifest does not authorize public push, publication, release signing,
public RC activation, package publication, guard clearance, protocol mutation,
wallet writes, minting, settlement, or any public claim beyond successful local
mirror-pipeline rehearsal.
