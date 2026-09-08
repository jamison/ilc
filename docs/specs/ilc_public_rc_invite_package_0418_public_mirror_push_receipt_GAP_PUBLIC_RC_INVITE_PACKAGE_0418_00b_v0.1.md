# ILC Public RC Invite Package 0418 Public Mirror Push Receipt

**Phase:** GAP-PUBLIC-RC-INVITE-PACKAGE-0418-00b
**Date:** 2026-09-08
**Status:** COMPLETE
**Sensitivity:** SENSITIVE

## Scope

This receipt records the sanitized public mirror regeneration and public
`github.com/jamison/ilc` push performed after `ilc-core==0.4.18` was uploaded,
fetchback-verified, release-signed, and retargeted in `tools/install.sh`.

## Mirror Pipeline

```json
{
  "artifact_id": "ilc-artifact:public-mirror-option-c-manifest@phase-1575e-fix1",
  "artifact_type": "source_release_tarball",
  "author_rewrite_result": "Genesis Agent <ilcops@proton.me>",
  "canonical_hash": "sha256:18cb37fbe47f9d4ce61b3fdd59a20b220068a8db157677fb9feb1e4c552b03de",
  "commit_count_after": 3403,
  "commit_count_before": 5129,
  "commit_count_min_required": 3077,
  "denylist_scan_result": "pass",
  "excluded_path_count": 8965,
  "filtered_public_head_sha": "6dca34604e559e3f614a420b9dd286b3e513b635",
  "lineage_reference": "genesis:v0.4",
  "no_push": true,
  "pipeline_duration_seconds": 1287,
  "pipeline_version": "generate_public_mirror_1575e_fix1.v0.1",
  "produced_phase": "1575e-fix1",
  "public_rc_exclude_scan_result": "pass",
  "publication_authority": "none - push gated to human operator per public_repository_push_authorized_phase_1575c",
  "ratification_token": "public_mirror_exclusion_list_hardened_phase_1575e_fix1",
  "signing_status": "deferred",
  "source_private_commit": "2dbf480580fc9c3c9beffc6aa589973110d33333",
  "staging_dir": "/private/tmp/ilc-public-mirror-0418-2dbf48058"
}
```

## Public Push

Previous public head:

```text
153e34869d4f96b628b7eb9e1e3eb5fe14fb9b12
```

Push command:

```bash
git -C /private/tmp/ilc-public-mirror-0418-2dbf48058 push public main:main --force-with-lease=refs/heads/main:153e34869d4f96b628b7eb9e1e3eb5fe14fb9b12
```

Push output:

```text
To github.com:jamison/ilc.git
forced update accepted with force-with-lease
previous_public_head_sha=153e34869d4f96b628b7eb9e1e3eb5fe14fb9b12
new_public_head_sha=6dca34604e559e3f614a420b9dd286b3e513b635
```

Post-push remote head:

```text
6dca34604e559e3f614a420b9dd286b3e513b635	refs/heads/main
```

Repository visibility:

```json
{"url":"https://github.com/jamison/ilc","visibility":"PUBLIC"}
```

## Public Raw-GitHub Verification

Release envelope:

```text
https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_core_0418_release_envelopes_GAP_PUBLIC_RC_INVITE_PACKAGE_0418_00b_v0.1.json
status=200
bytes=2102
sha256=133361b5a9ad23876fede9671f4d9843786b494e4a935f5f2e362e7c5f292dd9
```

Installable manifest:

```text
https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_installable_release_manifest_ilc_core_0418_GAP_PUBLIC_RC_INVITE_PACKAGE_0418_00b_v0.1.json
status=200
bytes=2596
sha256=cb891434880ac8c5bbc281a5adc93dcdf48ecddebe4ca1bd49929bd5b07091c3
```

Installer:

```text
https://raw.githubusercontent.com/jamison/ilc/main/tools/install.sh
status=200
bytes=29475
sha256=d2fb381abf95ede963f669ed8fdd399fc0bb836e4d20c63fcd4e8b2c8c6ae436
contains_0418_wheel=True
contains_0418_envelope_ref=True
```

## Non-Claims

No epoch transition occurred. No settlement occurred. No ECU minting occurred.
No ILC minting occurred. No VPS, validator, relay host, DigitalOcean resource,
or production LMDB was mutated by the mirror push. No CDL was opened, ratified,
or amended by this receipt.
