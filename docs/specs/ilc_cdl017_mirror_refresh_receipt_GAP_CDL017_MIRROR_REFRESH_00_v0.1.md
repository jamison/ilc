# ILC CDL-017 Public-RC Mirror Refresh Receipt

**Phase:** `GAP-CDL017-MIRROR-REFRESH-00`
**Date:** 2026-09-04
**Authorization:** `GO Phase GAP-CDL017-MIRROR-REFRESH-00 CDL017-MIRROR-REFRESH-AUTHORIZED`
**Status:** COMPLETE

## Mirror Artifact

```json
{
  "artifact_id": "ilc-artifact:public-mirror-option-c-manifest@phase-1575e-fix1",
  "artifact_type": "source_release_tarball",
  "author_rewrite_result": "Genesis Agent <ilcops@proton.me>",
  "canonical_hash": "sha256:cfbebf8d9fc0363fbf8f9882fab46364bd5b69549a8b2fe36e222e7b9cc0b301",
  "commit_count_after": 3361,
  "commit_count_before": 5086,
  "commit_count_min_required": 3051,
  "denylist_scan_result": "pass",
  "excluded_path_count": 8906,
  "filtered_public_head_sha": "b7d90ee9673198d40ab6db17e22b8642d003fb39",
  "lineage_reference": "genesis:v0.4",
  "no_push": true,
  "pipeline_duration_seconds": 943,
  "pipeline_version": "generate_public_mirror_1575e_fix1.v0.1",
  "produced_phase": "1575e-fix1",
  "public_rc_exclude_scan_result": "pass",
  "publication_authority": "none - push gated to human operator per public_repository_push_authorized_phase_1575c",
  "ratification_token": "public_mirror_exclusion_list_hardened_phase_1575e_fix1",
  "signing_status": "deferred",
  "source_private_commit": "0fd377333ac243b79c39b2f5cc95b8aba6c2ecb6",
  "staging_dir": "/private/tmp/ilc-public-mirror-cdl017-refresh-00-0fd377333"
}
```

## Verification Summary

- Source private commit: `0fd377333ac243b79c39b2f5cc95b8aba6c2ecb6`.
- Staged public mirror head: `b7d90ee9673198d40ab6db17e22b8642d003fb39`.
- Staged mirror path: `/private/tmp/ilc-public-mirror-cdl017-refresh-00-0fd377333`.
- Mirror tracked files: 4530.
- Public mirror commit count: 3361, above the required minimum 3051.
- Denylist scan: PASS.
- Authoritative tracked header-marker scan: 0 `PUBLIC_RC_EXCLUDE` declaration hits.
- Sensitive exact-term tracked scan: 0 hits.
- Signed `_0415` manifest present with both package artifacts marked `signed`.
- Release envelope set present at `docs/specs/ilc_core_0415_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json`.
- `_0415` manifest `release_envelope_ref` is public HTTPS: `https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_core_0415_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json`.
- `_0415` manifest no longer contains `no_release_signing`.
- Graph-intake coverage for the new receipt and walkthrough reports `missing_count: 0`.
- `docs/phases/STATUS.md` contains the output token exactly once.
- `git diff --check` passed before commit.

## Scope Notes

The mirror was generated from a clean detached worktree at the exact committed source revision because the main checkout had unrelated operator-owned generated-file changes. No unrelated dirty files were staged or committed.

`ilc_core` runtime/protocol code was not modified for the mirror contents. Mirror tooling and public-export rehearsal code were hardened before generation, including `ilc_core/rc/source_allowlist_export_rehearsal.py`, under the mirror phase's explicit tooling-hardening exception.

Raw prose references to `PUBLIC_RC_EXCLUDE` remain in public documentation as policy/history text. The authoritative declaration scan checks tracked-file header windows and reports zero declaration hits.

## Non-Claims

No public repository push occurred. No public visibility change occurred. No public RC activation occurred. No validator teardown or reprovisioning occurred. No epoch transition occurred. No settlement occurred. No ECU minting occurred. No ILC minting occurred.

## Output Token

`cdl017_public_rc_mirror_refreshed_GAP_CDL017_MIRROR_REFRESH_00`
