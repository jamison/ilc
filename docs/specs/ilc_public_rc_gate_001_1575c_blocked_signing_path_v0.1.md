# ILC Public RC Gate-001 1575c Blocked Signing Path Record v0.1

**Phase:** 1575c  
**Date:** 2026-07-14  
**Sensitivity:** SENSITIVE gate record; contains no secret material  
**Authorization received:** `GO PUBLIC-RC-GATE-001`  
**Verdict:** BLOCKED  
**Named defect:** `production_genesis_signing_path_unavailable_phase_1575c`

## 1. Gate Entry

The exact Phase 1575c authorization phrase was received:

```text
GO PUBLIC-RC-GATE-001
```

The gate began execution and passed the pre-signing readiness checks. It stopped at the production Genesis signing disposition because no acceptable production Genesis v0.4 signing path was available in the current workspace.

## 2. Preconditions Passed Before Block

| Check | Result |
|---|---|
| Public-RC economic intent reconciled | PASS |
| Phase 1575a disposition accepted for 1575b consumption | PASS |
| Phase 1575b Economic Activation Certificate present | PASS |
| Fix8 CDL-057 witness lane rehearsal present | PASS |
| Fix9 epoch 0-to-1 private transition rehearsal present | PASS |
| Fix1 bootstrap readiness present | PASS |
| Fix3 Atlas slice readiness present | PASS |
| Fix4 StarMap installer present | PASS |
| Fix2f Atlas/LMDB cleanliness gate present | PASS |
| Six `NOT_ACTIVATED` guards remain True | PASS |
| Bootstrap readiness verdict | `ready_pending_operator_bootstrap_bundle_publication` |
| Activation matrix `public_rc_live` rows found | 18 |
| Source export rehearsal | PASS; 435 included files, 39 excluded files |
| Genesis v0.4 source artifact | Present and unsigned |

## 3. Signing Disposition

Phase 1574 recorded `phase_1575_signing_pending`, and the hardened Phase 1575c prompt correctly scopes production Genesis signing inside Phase 1575c.

The currently available Atlas signing CLI path is:

```text
ilc atlas sign-manifest --private-key-hex
```

Direct source inspection showed that this surface is dev/test-only:

```text
signature_profile = ed25519_cose_sign1_dev_test_only
non_claims.genesis_signing = False
non_claims.ml_dsa_manifest_signing = False
non_claims.public_graph_publication = False
non_claims.public_rc_activation = False
```

That path is insufficient for this gate. Older Phase 1446 signing records are public attestations for v0.3-era artifacts and do not constitute current v0.4 production Genesis signing.

No production Genesis v0.4 signing key path, production signing ceremony tool, or production signing environment was available to complete the signing requirement.

## 4. Named Blocker

The gate stops with:

```text
blocked_with_named_defect:production_genesis_signing_path_unavailable_phase_1575c
```

This is not a failure of economics, Atlas slice readiness, source export, or bootstrap readiness. It is a production-signing availability blocker.

## 5. Tokens Not Emitted

The following tokens were intentionally not emitted:

- `genesis_v04_signed_phase_1575c`
- `genesis_v04_signature_verified_phase_1575c`
- `atlas_slice_manifest_signed_phase_1575c`
- `public_rc_gate_001_authorized`
- `window_1565_closed_phase_1575c`
- `window_1565_closure_gate_verdict=pass`
- `public_rc_live_phase_1575c`
- `public_repository_push_authorized_phase_1575c`

## 6. Evidence

Machine-readable evidence:

```text
out/block6_public_rc_gate_001_1575c/evidence_records.json
```

SHA-256:

```text
fce573209c15df1e2ab711f9f10da9e89a79c6dd211dc2719b34f0edd1f32eb1
```

## 7. Non-Claims

Phase 1575c did not authorize public RC, did not push or expose a public repository, did not change repository visibility, did not produce a Genesis v0.4 production signature, did not produce a production-signed AtlasSliceManifest, did not clear runtime guards, did not mint ECU, did not settle ILC, did not write wallets, and did not transition epochs.
