# ILC Public Release Propagation Workflow

**Version:** v0.1  
**Phase:** 1575e  
**Date:** 2026-07-14  
**Status:** committed workflow scaffold  
**Sensitivity:** NON-SENSITIVE; no public push authority

## 1. Purpose and Post-1575c Boundary

Phase 1575c authorized public RC and authorized human publication of a sanitized mirror, but Codex did not push to GitHub or change repository visibility. Phase 1575d then changed dependency files, making the Phase 1575c mirror stale. This workflow defines how later private changes are prepared for public propagation without using raw private `main` as a public release artifact.

This workflow does not authorize public push, repository visibility changes, package publication, guard clearance, ECU minting, ILC settlement, production wallet writes, or epoch transition.

## 2. Three-Lane Model

ILC release propagation has three separate lanes:

1. Private development lane.
2. Current public release lane.
3. Future graph-native homoiconic release lane.

The lanes share evidence, but they do not share authority. A private commit is not automatically a public release. A sanitized mirror receipt is not graph-native export. A future graph-native exporter is not active yet.

## 3. Private Development Lane

Private `main` remains the canonical development source of truth. Ordinary private pushes to the Jamison-owned private GitHub repository are allowed by normal development policy.

Private development commits may contain internal prompts, phase walkthroughs, research memos, generated evidence, private tooling, and other material that must not appear in a public mirror. Therefore public release updates must not be pushed directly from raw private `main`.

## 4. Current Public Release Lane

The current public release lane is the interim post-RC workflow:

1. Start from an exact `source_private_commit`.
2. Confirm worktree and branch state.
3. Confirm graph accounting for changed load-bearing files through Atlas/LMDB or the Fix38 ledger.
4. Run source allowlist export rehearsal.
5. Regenerate a sanitized public mirror when authorized for release preparation with `tools/scripts/generate_public_mirror.sh`.
6. Record a no-push public release propagation receipt.
7. Require a separate human public-push gate before any GitHub public remote receives the mirror.

The sanitized public mirror is a derived artifact and must not be hand-edited. If mirror content is wrong, correct the private source or mirror pipeline, then regenerate the mirror.

## 5. Future Graph-Native Homoiconic Release Lane

The target lane materializes public packages from graph membership rather than file-marker scanning. Future public release should derive from Atlas/LMDB graph membership, source nodes, package profiles, AtlasSliceManifest records, content hashes/CIDs, availability receipts, and conformance receipts.

Current `PUBLIC_RC_EXCLUDE` and allowlist scanning are interim controls. They are not the final graph-native release mechanism.

## 6. Release Propagation Receipt Schema

Every public release update must produce a machine-readable receipt with at least:

- `schema_version`
- `phase`
- `source_private_commit`
- `source_private_branch`
- `private_worktree_clean`
- `changed_files_since_last_public_release`
- `changed_file_baseline_status`
- `graph_accounting`
- `source_export`
- `sanitized_mirror`
- `homoiconic_forward_fields`
- `public_push_authorized`
- `non_claims`

The receipt must use deterministic JSON serialization with `sort_keys=True`, compact separators, and `allow_nan=False`.

## 7. Graph Accounting Requirements

Every changed load-bearing file needs graph accounting before public propagation. At minimum, a record must identify:

- repo-relative path
- node kind
- graph_delta
- source hash or content hash where available
- trace edges, including `SOURCE_TREE_MEMBER`

Graph accounting may be represented directly in Atlas/LMDB or in the Fix38 ledger as candidate records. Missing records must be recorded in the receipt as named gaps, not hidden in prose.

## 8. No-Push / Push-Gate Separation

The release preparation tool must never run `git push`, change GitHub repository visibility, publish packages, or claim public push authorization. It may generate a sanitized mirror into a local staging directory and record its filtered HEAD and archive hash.

The human operator push gate is separate. It must name the exact receipt, exact `source_private_commit`, exact sanitized mirror location, filtered public HEAD, and target remote.

## 9. Failure Modes and Named Blockers

Named blockers include:

| Blocker | Meaning |
|---|---|
| `requires_explicit_baseline_commit` | Changed-file comparison cannot be computed without a known prior public source commit. |
| `baseline_commit_not_found` | The supplied baseline commit is not present locally. |
| `source_export_failed` | Source allowlist export did not pass. |
| `graph_accounting_missing_records` | Changed load-bearing files lack Atlas/LMDB or Fix38 accounting. |
| `public_mirror_generation_failed` | Sanitized mirror generation failed. |
| `public_push_attempt_detected` | A tool or workflow attempted to push during a no-push phase. |

Failures must stop publication preparation or record an explicit blocked disposition.

## 10. Migration Plan From Interim Mirror Lane to Homoiconic Exporter

The current release receipt includes `homoiconic_forward_fields` so a later exporter can populate the same public contract without changing downstream release evidence. The migration path is:

1. Complete Atlas/LMDB coverage for public-package membership.
2. Ratify or commit AtlasSliceManifest package/slice schemas.
3. Add package profile IDs for public source, sidecars, and skill packages.
4. Add graph-native materializer receipts proving byte-for-byte reconstruction.
5. Replace file-marker exclusion with graph membership selection.
6. Preserve receipt fields while changing the source of truth from scanner output to graph-derived export.

Until that migration is complete, the graph-native exporter status remains `not_activated`.
