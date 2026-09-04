# ILC Public RC Version Consistency Gate Report

Phase: GAP-PUBLIC-RC-VERSION-CONSISTENCY-00
Date: 2026-09-04
Verdict: PASS

## Summary

All active package version surfaces agree on `ilc-core==0.4.15`. The patched release-signing prompts contain no residual execution-critical references to the prior 0.4.13 capsule-sign target. The signing chain may proceed to GAP-RELEASE-SIGN-00a.

## Surface Checks

| Surface | Actual value | Verdict |
|---|---|---|
| `pyproject.toml` | `version = "0.4.15"` | PASS |
| `tools/install.sh` | `RC_WHEEL_URL` points to `ilc_core-0.4.15-py3-none-any.whl`; `TMP_WHEEL` is derived dynamically from the URL basename | PASS |
| `_0415` installable manifest | `release_id: ilc-core-0.4.15`; wheel artifact `ilc-artifact:ilc-core-python-wheel-0415@phase-1627`; sdist artifact `ilc-artifact:ilc-core-python-sdist-0415@phase-1627` | PASS |
| Release-signing prompts | RELEASE-SIGN-00a/00b/00c/00d all validate and have zero residual 0.4.13/_0413/PATCH-07 execution-critical target references | PASS |

## Token Checks

| Token | Count | Verdict |
|---|---:|---|
| `relay_bootstrap_capsule_signed_bundled_GAP_RELAY_BOOTSTRAP_CAPSULE_SIGN_00` | 3 | PASS |
| `invite_shortcode_deploy_guard_cleared_GAP_INVITE_SHORTCODE_DEPLOY_00` | 2 | PASS |
| `release_sign_prompts_patched_for_0415_direct_patch` | 1 | PASS |
| `connectivity_smoke_passed_GAP_INSTALL_CONNECTIVITY_SMOKE_00` | 6 | PASS |
| `version_consistency_gate_passed_GAP_PUBLIC_RC_VERSION_CONSISTENCY_00` before execution | 0 | PASS |

## Manifest Artifact State

| Artifact type | Artifact ID | Hash | Size | Signing status |
|---|---|---|---:|---|
| `python_wheel` | `ilc-artifact:ilc-core-python-wheel-0415@phase-1627` | `sha256:058e2deec5656d25cc92de3d16acd8db01778f26c18e6405e06db48569ce7524` | 1451016 | `unsigned` |
| `python_sdist` | `ilc-artifact:ilc-core-python-sdist-0415@phase-1627` | `sha256:3aea9f609898a1f841de26a64cd8c9706be4a16094b14934879c78456232f21e` | 1183400 | `unsigned` |

## Mirror Disposition

No mirror generation or mirror push occurred. CDL017-MIRROR-REFRESH-00 remains post-signing and must run only after RELEASE-SIGN-00d so the sanitized mirror captures the signed `_0415` manifest and release envelope set.

## Non-Claims

No release signing occurred. No manifest signing occurred. No signing-status mutation occurred. No mirror generation or mirror push occurred. No VPS mutation occurred. No PyPI upload or yank occurred. No public RC activation, epoch transition, settlement, ECU minting, or ILC minting occurred.
