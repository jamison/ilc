# ILC CDL-017 Public-RC Mirror Refresh Receipt, 0.4.17 Run

**Phase:** `GAP-CDL017-MIRROR-REFRESH-00`
**Date:** 2026-09-06
**Authorization:** `GO Phase GAP-CDL017-MIRROR-REFRESH-00 CDL017-MIRROR-REFRESH-AUTHORIZED`
**Status:** COMPLETE
**Output token:** `cdl017_public_rc_mirror_refreshed_0417_GAP_CDL017_MIRROR_REFRESH_00`

## Mirror Artifact

```json
{
  "artifact_id": "ilc-artifact:public-mirror-option-c-manifest@phase-1575e-fix1",
  "artifact_type": "source_release_tarball",
  "author_rewrite_result": "Genesis Agent <ilcops@proton.me>",
  "canonical_hash": "sha256:64bf28a92b84e99966c42b7970f96b12cf2b11ea1172f1fc0aacd5696563f6d8",
  "commit_count_after": 3384,
  "commit_count_before": 5109,
  "commit_count_min_required": 3065,
  "denylist_scan_result": "pass",
  "excluded_path_count": 8950,
  "filtered_public_head_sha": "153e34869d4f96b628b7eb9e1e3eb5fe14fb9b12",
  "lineage_reference": "genesis:v0.4",
  "no_push": true,
  "pipeline_duration_seconds": 1146,
  "pipeline_version": "generate_public_mirror_1575e_fix1.v0.1",
  "produced_phase": "1575e-fix1",
  "public_rc_exclude_scan_result": "pass",
  "publication_authority": "none - push gated to human operator per public_repository_push_authorized_phase_1575c",
  "ratification_token": "public_mirror_exclusion_list_hardened_phase_1575e_fix1",
  "signing_status": "deferred",
  "source_private_commit": "912255e83ec3cdeef42984f8ad50ee1527f7cc7e",
  "staging_dir": "/private/tmp/ilc-public-mirror-cdl017-refresh-0417-912255e83e"
}
```

## Verification Summary

- Source private commit: `912255e83ec3cdeef42984f8ad50ee1527f7cc7e`.
- Staged public mirror head: `153e34869d4f96b628b7eb9e1e3eb5fe14fb9b12`.
- Staged mirror path: `/private/tmp/ilc-public-mirror-cdl017-refresh-0417-912255e83e`.
- Source export rehearsal: `result=pass`, `included_files=514`, `excluded_files=7267`, `blocked_ambiguities=0`, `dependency_hits=0`, `marker_hits=0`.
- Public mirror commit count: `3384`, above the required minimum `3065`.
- Generator denylist scan: `pass`.
- Generator `public_rc_exclude_scan_result`: `pass`.
- Authoritative tracked header-marker scan: `0` `PUBLIC_RC_EXCLUDE` declaration hits.
- Raw `PUBLIC_RC_EXCLUDE` references: `658`, classified as prose/test/scanner references, not header declarations.
- Sensitive exact-term tracked scan: `0` hits for the configured email/name/private-key denylist terms.
- `docs/PLANNING_INDEX.md` is absent from the mirror.
- `docs/phases/` is absent from the mirror.
- `_0417` signed installable manifest is present in the staged mirror.
- `_0417` release envelope set is present in the staged mirror.
- Mirrored `tools/install.sh` references `ilc_core-0.4.17-py3-none-any.whl`.
- Mirrored manifest `release_envelope_ref` is public HTTPS: `https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_core_0417_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json`.
- Mirrored manifest records `signer_public_key_hex=5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a`.
- Mirrored Python wheel and sdist artifacts are marked `signed`; the unchanged v0.4.16 consensus helper tarball remains `unsigned`.
- Focused public-export regression tests passed: `28 passed, 25 skipped`.
- Prompt validation passed: `VALID`.
- `git diff --check` passed.

## Supersession

This regeneration supersedes `GAP-PUBLIC-RC-MIRROR-REFRESH-00` (marked SUPERSEDED, never executed) and all prior `filtered_public_head_sha` values, including the 0.4.15 mirror-refresh head `b7d90ee9673198d40ab6db17e22b8642d003fb39`.

## Scope Notes

The mirror was generated from a clean detached worktree at the exact committed source revision because the main checkout had an unrelated operator-owned dirty forward-plan file.

The source commit includes one pre-generation support-test hardening commit, `912255e83`, so the staged mirror and receipt source commit are aligned.

No `ilc_core/` runtime or protocol code was modified in this mirror refresh phase.

No push occurred. Mirror is staged locally at `/private/tmp/ilc-public-mirror-cdl017-refresh-0417-912255e83e`. `GAP-PUBLIC-RC-PUBLISH-EXEC-00` is the explicit human-operator push gate.

## Non-Claims

No public repository push occurred. No public visibility change occurred. No public RC activation occurred. No PyPI upload occurred. No GitHub Release asset changed. No VPS or DigitalOcean resource was mutated. No validator teardown or reprovisioning occurred. No epoch transition occurred. No settlement occurred. No ECU minting occurred. No ILC minting occurred.
