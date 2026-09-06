# ILC Public RC Publish Exec Receipt - GAP-PUBLIC-RC-PUBLISH-EXEC-00 v0.1

## Summary

GAP-PUBLIC-RC-PUBLISH-EXEC-00 was executed on 2026-09-06 after Genesis authorization:
`GO Phase GAP-PUBLIC-RC-PUBLISH-EXEC-00 PUBLISH-EXEC-AUTHORIZED`.

The sanitized CDL-017 public mirror staged at
`/private/tmp/ilc-public-mirror-cdl017-refresh-0417-912255e83e` was pushed to
the already-public GitHub repository `git@github.com:jamison/ilc.git`.

## Publication Record

- Public repository: `https://github.com/jamison/ilc`
- Repository visibility before push: `public`
- Repository visibility after push: `public`
- Previous public `main`: `aadd786ca26fdf48d61cf5f7018e9137e94ce419`
- Published public `main`: `153e34869d4f96b628b7eb9e1e3eb5fe14fb9b12`
- Mirror staging directory: `/private/tmp/ilc-public-mirror-cdl017-refresh-0417-912255e83e`
- Mirror refresh receipt: `docs/specs/ilc_cdl017_mirror_refresh_receipt_0417_GAP_CDL017_MIRROR_REFRESH_00_v0.1.md`
- Private execution HEAD before receipt commit: `6f7fbc974a029cb49468ad25d917c9577b73dc80`

## Push Output

```text
To github.com:jamison/ilc.git
 + aadd786c...153e3486 main -> main (forced update)
```

## Post-Push Verification

Remote head:

```text
153e34869d4f96b628b7eb9e1e3eb5fe14fb9b12	refs/heads/main
```

Repository visibility:

```text
visibility: public
private: False
html_url: https://github.com/jamison/ilc
```

Release envelope fetch:

```text
status: 200
final_url: https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_core_0417_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json
bytes: 2101
envelopes: 2
```

Installable manifest fetch:

```text
status: 200
final_url: https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_installable_release_manifest_ilc_core_0417_GAP_CONSENSUS_BINARY_DEPLOY_FIX2_00_v0.1.json
bytes: 2567
release_id: ilc-core-0.4.17
release_envelope_ref: https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_core_0417_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json
```

## Pre-Push Gates

- Input token `cdl017_public_rc_mirror_refreshed_0417_GAP_CDL017_MIRROR_REFRESH_00`: present once.
- Input token `version_consistency_gate_passed_0417_GAP_PUBLIC_RC_VERSION_CONSISTENCY_00`: present once.
- Input token `release_signing_ceremony_0417_complete_GAP_RELEASE_SIGN_00c`: present once.
- Input token `ilc_core_0417_artifacts_signed_GAP_RELEASE_SIGN_00c`: present once.
- Input token `install_verify_signature_0417_integration_committed_GAP_RELEASE_SIGN_00d`: present once.
- Input token `install_e2e_verified_signed_0417_GAP_INSTALL_DO_SMOKE_00`: present once.
- Input token `fresh_linux_invite_bootstrap_smoke_signed_pass_GAP_INSTALL_DO_SMOKE_00`: present once.
- Output token `public_rc_published_GAP_PUBLIC_RC_PUBLISH_EXEC_00`: absent before execution.
- Publication revocation marker scan: zero hits.
- Staged mirror HEAD matched the mirror refresh receipt filtered public head.
- Staged `_0417` manifest contained an HTTPS `release_envelope_ref`.
- Staged release envelope file was present and non-empty.
- Independent staged mirror private-key/API-token scan returned zero hits.
- Authoritative first-8-lines `PUBLIC_RC_EXCLUDE` header-marker scan returned zero hits.

## Scope Notes

The broad raw `PUBLIC_RC_EXCLUDE` string appears in public-safe examples and
scanner prose. The authoritative header-marker scan is the first-8-lines
declaration scan used by the CDL-017 mirror refresh receipt, and that scan
returned zero declaration hits in the staged mirror.

The generic version-consistency report file is historical 0.4.15 evidence. The
current 0.4.17 version-consistency evidence is the PATCH-09 walkthrough plus
the STATUS token
`version_consistency_gate_passed_0417_GAP_PUBLIC_RC_VERSION_CONSISTENCY_00`.

## Output Token

`public_rc_published_GAP_PUBLIC_RC_PUBLISH_EXEC_00`

## Non-Claims

No PyPI upload occurred. No GitHub Release asset changed. No VPS, validator, or
DigitalOcean resource was mutated. No validator LMDB state was mutated. No
epoch transition occurred. No settlement occurred. No ECU minting occurred. No
ILC minting occurred. No public mainnet activation occurred beyond the
authorized public repository mirror publication.
