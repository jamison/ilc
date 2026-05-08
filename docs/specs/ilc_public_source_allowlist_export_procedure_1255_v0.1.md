# ILC Public Source Allowlist Export Procedure 1255 v0.1

**Phase:** 1255
**Date:** 2026-05-08
**Status:** PROCEDURE DEFINED, EXPORT NOT AUTHORIZED
**Authority:** CDL-086 counsel disposition C5 plus Window 1249-1256 Phase 1255

```text
allowlist_export_procedure_defined_required_before_public_repo_publication
allowlist_export_procedure_defined_phase_1255
public_repository_publication_not_authorized_phase_1255
phase_1255_tla_allowlist_export_complete
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
us_provisional_patent_application_filed_required_before_public_repo_publication
```

## 1. Purpose

This document defines the procedure for a future clean public-source export
from the private canonical repository. It closes the missing procedure surface
identified by CDL-086 C5 and the Window 1249-1256 plan.

This document does not execute the export. It does not publish a repository,
select final license instruments, approve a CLA, approve trademark policy, file
or disclose patent material, generate release keys, produce release envelopes,
or make any public RC claim.

## 2. Governing Boundaries

The private canonical repository history remains intact and unpublished. Future
public-source publication must use an explicit allowlist-based export into a
separate public repository that starts from a clean public genesis commit.
There must be no git history rewrite of the private canonical repository for
the public export.

Public repository publication remains blocked until all of these are true:

| Gate | Required state before execution |
|---|---|
| License | Counsel-approved final license instruments, SPDX expressions, license files, and per-zone license markings. |
| CLA | Counsel-approved contributor agreement or explicit no-external-contributor policy. |
| Trademark and identity | Approved canonical identity and trademark policy for ILC marks and fork labeling. |
| Patent and publication review | Patent-sensitive material reviewed, with required provisional filings or explicit no-file decision complete before disclosure. |
| Allowlist manifest | Reviewed manifest with deterministic include/exclude rules and dry-run evidence. |
| Constitutional authorization | Separate explicit human/constitutional authorization to publish the selected export. |

## 3. Source Freeze Preconditions

Before a future export dry run:

1. Select a committed source revision; do not export from an uncommitted working tree.
2. Record the source commit hash and active capsule in the export manifest.
3. Verify `docs/PLANNING_INDEX.md`, `docs/phases/STATUS.md`, and the active launch roadmap agree on the public-RC frontier.
4. Confirm no local secrets, private keys, `.env` files, editor state, or generated local caches are inside the candidate export root.
5. Confirm the export run is dry-run only unless a separate publication authorization token is present.

## 4. Manifest Contract

The future manifest should be a canonical JSON or YAML document with stable key
ordering. If JSON is used for any machine-verifiable artifact, serialize with
`sort_keys=True` and `allow_nan=False`.

Required manifest fields:

| Field | Meaning |
|---|---|
| `schema_version` | Export manifest schema version, starting at `ilc_public_source_allowlist_manifest.v0.1`. |
| `source_commit` | Full private-canonical source commit hash. |
| `capsule` | Current capsule path and version at export freeze. |
| `mode` | `dry_run` or `authorized_publication`; default must be `dry_run`. |
| `include_rules` | Ordered repo-relative allowlist selectors. |
| `exclude_rules` | Ordered repo-relative deny selectors; deny wins over include. |
| `review_required` | Paths or classes requiring counsel, patent, trademark, or Genesis review. |
| `license_zone_map` | Per-path license zone after counsel approval. |
| `file_hashes` | Full SHA-256 hash for every exported file after dry-run materialization. |
| `non_claims` | Explicit statement that dry-run evidence is not publication authorization. |

Selectors must be repo-relative, must not contain absolute paths, and must not
escape the repository root through `..` or symlinks.
denylist overrides allowlist: a matching exclude rule always wins over a
matching include rule.

## 5. Default Exclusion Rules

The following classes are excluded unless later explicitly reviewed and
allowlisted:

| Class | Default disposition |
|---|---|
| Private process docs | Exclude `docs/antigravity_tasks/`, `docs/phases/`, scratch prompts, internal handoff drafts, and private execution notes unless a specific public transparency excerpt is approved. |
| Patent-sensitive research | Exclude `docs/research/patent_pending/`, patent strategy notes, unpublished paper drafts, and any file marked patent-sensitive. |
| Raw chat or memory corpus | Exclude `Z_Past_Chats/`, raw dredge corpora, MemPalace stages, local context recovery packs, and private transcript derivatives. |
| Generated local outputs | Exclude `out/`, local monitoring snapshots, generated diagnostics, cache directories, coverage artifacts, and benchmark scratch output unless a specific evidence artifact is approved. |
| Secrets and local environment | Exclude `.env*`, private keys, release keys, TLS keys, local certificates, `.venv/`, editor files, and OS metadata. |
| Public-claimability and release artifacts | Exclude unsigned release envelopes, draft release manifests, signing ceremony material, and claimability artifacts until their independent gates close. |
| Ambiguous docs | Route `docs/research/`, whitepaper drafts, counsel notes, licensing memos, and roadmap drafts to human review rather than automatic export. |

## 6. Candidate Allowlist Classes

These classes may be considered for future allowlisting after the gates above
close. Listing them here is not approval.

| Class | Review requirement |
|---|---|
| Source code | Path-level package/profile review, dependency audit, license-zone assignment, and security scan. |
| Public package metadata | Counsel-approved license metadata and release posture review. Existing metadata is not final legal approval. |
| Selected specs | Canonicality, license tier, public-claim boundary, and patent-sensitivity review. |
| Selected tests | Secret scan, fixture review, and removal of private phase-history assertions if they reveal internal execution history. |
| Selected tools | Reproducibility review, no private-path assumptions, bounded IO, and dependency/license review. |
| Public evidence summaries | Must avoid unpublished patent disclosure, private deliberation, and unsupported public-RC claims. |

## 7. Dry-Run Procedure

1. Build the manifest from reviewed include and exclude rules.
2. Materialize the export into a temporary directory outside the private repo.
3. Reject any symlink, absolute path, or path traversal.
4. Compute full SHA-256 hashes for every exported file.
5. Run secret scans and broad contradiction searches for terms including
   `private`, `not public`, `do not publish`, `patent pending`, `counsel
   required`, `not authorized`, `release key`, `secret`, and `token`.
6. Run license/SPDX checks against the counsel-approved license zone map.
7. Run package/build tests only inside the exported tree, using public
   dependency sources and no private path references.
8. Produce a dry-run report listing included files, excluded files, ambiguous
   paths, scan findings, and all non-claims.
9. Require human review of the dry-run report before any publication act.

## 8. Publication Procedure

Publication requires a later explicit authorization that names the exact source
commit, manifest hash, and public destination. Without that authorization, the
procedure stops after dry-run reporting.

If authorized later:

1. Re-run the dry-run from the authorized source commit.
2. Verify the manifest hash matches the authorized manifest.
3. Create a clean public repository with a public genesis commit.
4. Commit only the materialized allowlist export, not private history.
5. Include a public provenance file that states the public repo is a clean
   export from a private canonical archive and does not contain full internal
   phase history.
6. Tag or release only if release-key and release-envelope gates are also
   separately authorized.

## 9. Non-Claims

```text
public_repository_publication_not_authorized_phase_1255
```

Phase 1255 defines a future export procedure only. It does not authorize:

- public repository publication,
- public release artifact distribution,
- public RC announcement,
- external contributor onboarding,
- final SPDX/license selection,
- trademark policy publication,
- patent filing or patent disclosure,
- release-key generation,
- release envelope production,
- v0.2 signing,
- public P2P exposure,
- public claimability activation.

## 10. Phase 1256 Carry-Forward

Phase 1256 should classify this blocker as procedure-defined but still
publication-blocked until counsel/IP/trademark/CLA/patent and explicit
publication authorization gates close.
