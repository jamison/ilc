# ILC Graph-Native Sidecar Registry Manifest 1307 v0.1

**Date:** 2026-05-11
**Phase:** 1307, Window 1303-1316
**Status:** Deterministic local/package sidecar registry and profile hardening
complete; no public serving, no source export, no package publication, and no
public confidential messaging authority.

```text
graph_native_sidecar_registry_manifest_phase_1307.v0.1
sidecar_manifest_deterministic_profile_declared_phase_1307
openclaw_compatible_local_bridge_profile_declared_phase_1307
confidential_coordination_local_preview_profile_declared_phase_1307
package_profile_integrity_hardened_phase_1307
phase_1308_public_rc_exclude_helper_pruning_replacement_plan_next
public_rc_remains_blocked_after_phase_1307
```

## 1. Verdict

Phase 1307 adds the deterministic graph-native sidecar registry manifest at:

```text
ilc_core/sidecars/registry_manifest.py
```

The manifest is local/package metadata only. It declares the essential
graph-native sidecars, OpenClaw/NemoClaw-compatible local bridge profiles, the
claimable local bridge profile, and the
`confidential_coordination_local_preview` profile. It validates deterministic
profile ordering, package-profile identity matching, sidecar reachability,
private wiring modes, source-allowlist readiness flags, and non-authorization
flags.

Phase 1307 also hardens package-profile integrity in:

```text
ilc_core/rc/package_profiles.py
ilc_core/rc/package_profile_ci_gate.py
ilc_core/rc/atlas_graph_discipline.py
```

The `openclaw_skill_claimable` package profile now requires the offline
claimability receipt verifier sidecar component. The package-profile CI gate
now measures `ilc_core/sidecars` as part of the `local_sidecar` surface. The
ATLAS-G package reachability graph now has component reachability entries for
the sidecar registry, offline claimability verifier, OpenClaw-compatible bridge,
and confidential coordination local preview profile.

This is not export materialization. It is not package publication. It is not a
public sidecar service.

## 2. Registry Profiles

| Registry profile | Package profile | Required sidecars | Public posture |
|------------------|-----------------|-------------------|----------------|
| `openclaw_compatible_local_bridge` | `openclaw_skill_local` | `sidecar_registry_manifest`, `openclaw_nemoclaw_local_bridge` | Local/private harness bridge only; no public P2P, no public claimability runtime activation. |
| `openclaw_claimable_local_bridge` | `openclaw_skill_claimable` | `sidecar_registry_manifest`, `offline_claimability_receipt_verifier`, `openclaw_nemoclaw_local_bridge` | Claimable package profile metadata only; public claimability runtime remains not activated. |
| `confidential_coordination_local_preview` | `confidential_coordination_local_preview` | `sidecar_registry_manifest`, `confidential_coordination_local_preview`, `local_graph_memory_projection`, `openclaw_nemoclaw_local_bridge` | Private/local preview only; no public confidential messaging or public confidential coordination serving claim. |

All registry profiles require `public_serving_enabled=false` and
`public_p2p_activated=false`. All public claimability activation flags remain
false.

## 3. Sidecar Manifest

| Sidecar | Implementation status | Authority gate |
|---------|-----------------------|----------------|
| `sidecar_registry_manifest` | Implemented in Phase 1307. | Local/package metadata only. |
| `offline_claimability_receipt_verifier` | Implemented in Phase 1305 and hardened in Phase 1306. | Local verifier only; no public API. |
| `truth_primitive_submission_boundary` | Planned Phase 1308 boundary. | Helper disposition and public-safe replacement planning required before export. |
| `transport_principal_admission` | Planned Phase 1309/1310 substrate. | No public path until lifecycle, revocation, replay, admission, ban, rate, and privacy gates close. |
| `local_graph_memory_projection` | Planned Phase 1311/1312 substrate. | No public projection serving until privacy and bind/listener gates close. |
| `confidential_coordination_local_preview` | Profile declared in Phase 1307. | Runtime and dry-run routed to Phases 1324-1329; private/local only. |
| `openclaw_nemoclaw_local_bridge` | Profile declared in Phase 1307. | Harness bridge only; OpenClaw/NemoClaw are hosts, not protocol substrates. |

## 4. Package Profile Integrity

Phase 1307 updates `PUBLIC_RC_PACKAGE_PROFILES_VERSION` to:

```text
public_rc_package_profiles_1307.v0.1
```

Integrity changes:

- `openclaw_skill_local` requires `graph_native_sidecar_registry_manifest` and
  `openclaw_compatible_local_bridge`.
- `openclaw_skill_claimable` additionally requires
  `offline_claimability_receipt_verifier_sidecar`.
- `confidential_coordination_local_preview` is a new local-preview package
  profile and must not claim public RC, public P2P, or public claimability.
- Any public-claimability package profile now requires
  `ecu_to_ilc_conversion_runtime`, `public_claimability_runtime`, and
  `offline_claimability_receipt_verifier_sidecar`.
- `local_sidecar` package-profile CI measurement now includes
  `ilc_core/sidecars`.
- The registry package-profile integrity block embeds the Phase 1305 verifier
  manifest and validates its public API, public claimability activation,
  non-loopback claimability API, and receipt public-serving flags remain false.

This improves package integrity but does not make the measured package
exportable. Phase 1308 must still decide `PUBLIC_RC_EXCLUDE` helper disposition,
and Phase 1319/1333 remain the materialization/release gates if later
authorized.

## 5. Source Allowlist Readiness

The registry records source-allowlist readiness as fail-closed metadata:

| Field | Phase 1307 value |
|-------|------------------|
| `source_allowlist_export_executed` | `false` |
| `clean_public_tree_materialized` | `false` |
| `phase_1308_public_rc_exclude_disposition_required` | `true` |
| `marker_scan_required_before_export` | `true` |
| `legacy_untagged_docs_review_required` | `true` |

The deterministic scaffold dispositions remain:

```text
compile_into_contract
retain_as_public_metadata
retain_internal_only
strip_from_export
replace_before_export
```

## 6. Public-RC Impact

Phase 1307 narrows Gap 14 by making the sidecar suite and package-profile
relationship executable and deterministic. It does not close public RC.

Still-open blockers include:

- `PUBLIC_RC_EXCLUDE` helper replacement, stripping, or explicit deferral;
- source allowlist export execution and clean public tree materialization;
- public claimability API/verifier serving authority;
- replay/nullifier policy and duplicate-claim registry policy;
- public-safe disclosure and projection privacy implementation;
- TransportPrincipal public-path activation and hostile-network controls;
- public P2P/fetch/sidecar/projection serving authority;
- release artifacts, release keys, release envelopes, Genesis/v0.2 signing;
- wallet-facing withdrawal/transfer/spend request activation, wallet writes,
  withdrawal runtime, ECU minting activation, ILC settlement activation, and
  final value-path activation authority.

## 7. Non-Claims

Phase 1307 makes no public RC claim, no public launch claim, no source allowlist
export claim, no public repository publication claim, no public package
publication claim, no release artifact claim, no release-key claim, no
release-envelope claim, no public claimability API activation claim, no public
verifier service claim, no public claim endpoint claim, no public P2P/fetch
serving claim, no public sidecar/projection serving claim, no non-loopback bind
claim, no helper promotion claim, no marker removal claim, no helper stripping
claim, no Genesis mutation or signing claim, no v0.2 signing claim, no CDL
mutation claim, no CDL-088 opening claim, no wallet withdrawal claim, no wallet
transfer claim, no wallet spend claim, no ECU minting claim, no ILC settlement
claim, no public confidential messaging claim, and no public confidential
coordination serving claim.

Public RC remains blocked:

```text
public_rc_remains_blocked_after_phase_1307
```

Phase 1308 remains the next sensitive gate:

```text
phase_1308_public_rc_exclude_helper_pruning_replacement_plan_next
```

Phase 1308 is sensitive and requires explicit `GO Phase 1308`.

## 8. Phase 1314 Wallet Action Boundary Addendum

Phase 1314 updates the executable registry with a new local preflight sidecar:

```text
wallet_action_semantics_preflight
```

The sidecar records:

```text
wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1
wallet_withdrawal_transfer_spend_not_activated_phase_1314
wallet_signing_ledger_write_not_authorized_phase_1314
public_claimability_user_action_boundary_recorded_phase_1314
wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314
phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next
public_rc_remains_blocked_after_phase_1314
```

The `openclaw_claimable_local_bridge` profile now requires
`wallet_action_semantics_preflight` alongside the offline claimability verifier.
The package-profile integrity block embeds
`wallet_action_semantics_preflight_manifest` and validates that wallet-facing
withdrawal requests, wallet-facing transfer requests, wallet-facing spend
requests, wallet-provider signing requests, wallet-provider ledger-write
requests, public claimability activation, and public claim endpoint flags
remain false.

This addendum does not change the Phase 1307 non-authorization boundary: no
wallet-facing withdrawal request, no wallet-facing transfer request, no
wallet-facing spend request, no wallet-provider signing request, no
wallet-provider ledger-write request, no public claim endpoint, no ECU minting,
and no ILC settlement are authorized.

## 9. Phase 1315 Value-Path Boundary Addendum

Phase 1315 updates the executable registry with a new local preflight sidecar:

```text
value_path_activation_boundary_preflight
```

The sidecar records:

```text
ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1
ecu_minting_not_authorized_phase_1315
ilc_settlement_not_authorized_phase_1315
value_path_activation_boundary_recorded_phase_1315
phase_1316_window_1303_1316_closure_audit_next
public_rc_remains_blocked_after_phase_1315
```

The `openclaw_claimable_local_bridge` profile now requires
`value_path_activation_boundary_preflight` alongside the offline claimability
verifier and wallet-action semantics preflight. The package-profile integrity
block embeds `value_path_activation_boundary_preflight_manifest` and validates
that ECU minting, ECU creation, ILC settlement, ILC transfer, withdrawal
runtime, wallet writes, public claimability activation, and public claim
endpoint flags remain false.

This addendum does not change the Phase 1307 non-authorization boundary: no
wallet-facing withdrawal request, no wallet-facing transfer request, no
wallet-facing spend request, no wallet-provider signing request, no
wallet-provider ledger-write request, no public claim endpoint, no public
claimability activation, no withdrawal runtime, no ECU minting, no ILC
settlement, and no value-path activation are authorized. Phase 1316 is
sensitive and requires explicit `GO Phase 1316`.
