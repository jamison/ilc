# ILC Antigravity Context Capsule v5.52

**Date:** 2026-05-10
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
**Produced:** Phase 1290, Window 1289-1302; updated by Phases 1291-1298
**Frontier:** Window 1289-1302 is open through Phase 1298. Phase 1298 records a
sidecar bind/listener/peer-discovery authority preflight only. Phase 1299 is
sensitive and requires explicit `GO Phase 1299`.

```text
context_capsule_v5_52_frontier_refresh_phase_1290.v0.1
capsule_v5_52_supersedes_v5_51
window_1289_1302_sequence_lock_reflected_in_capsule_phase_1290
window_1289_1302_open_through_phase_1290
window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289
phase_1291_public_claimability_verifier_contract_preflight_requires_explicit_go
public_rc_blocker_map_refreshed_phase_1290
public_rc_remains_blocked_after_phase_1290
phase_1290_non_sensitive_docs_canon_refresh_no_activation
public_claimability_verifier_contract_preflight_phase_1291.v0.1
public_claimability_activation_not_authorized_by_default_phase_1291
claimability_verifier_public_api_not_enabled_phase_1291
wallet_withdrawal_transfer_spend_still_blocked_phase_1291
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
claimability_contract_no_runtime_helper_added_phase_1291
phase_1292_verifier_negative_path_corpus_package_boundary_next
public_rc_remains_blocked_after_phase_1291
claimability_package_profile_allowlist_rehearsal_phase_1292.v0.1
source_allowlist_export_not_executed_phase_1292
public_package_publication_not_authorized_phase_1292
public_rc_exclude_helpers_preserved_phase_1292
verifier_negative_path_corpus_recorded_phase_1292
claimability_package_profile_boundary_verdict_phase_1292=pass_import_boundary_publication_blocked
ilc_logic_network_import_boundary_repaired_phase_1292
package_profile_ci_artifacts_refreshed_phase_1292
phase_1293_public_rc_exclude_helper_promotion_removal_register_next
public_rc_remains_blocked_after_phase_1292
public_rc_exclude_helper_promotion_removal_register_phase_1293.v0.1
public_rc_exclude_helper_register_verdict_phase_1293=all_current_helpers_keep_internal_no_promotion
public_rc_exclude_helpers_keep_internal_phase_1293
public_rc_exclude_helper_promotion_not_authorized_phase_1293
public_rc_exclude_helper_removal_not_authorized_phase_1293
public_rc_exclude_helper_replacement_required_before_public_export_phase_1293
source_allowlist_export_not_executed_phase_1293
public_package_publication_not_authorized_phase_1293
public_rc_remains_blocked_after_phase_1293
phase_1294_claimability_package_allowlist_rehearsal_next
claimability_package_allowlist_rehearsal_phase_1294.v0.1
claimability_package_allowlist_verdict_phase_1294=rehearsal_pass_export_blocked
openclaw_skill_claimable_allowlist_rehearsed_phase_1294
public_rc_exclude_helpers_excluded_from_export_phase_1294
claimability_package_manifest_not_materialized_phase_1294
source_allowlist_export_not_executed_phase_1294
public_repository_publication_not_authorized_phase_1294
public_package_publication_not_authorized_phase_1294
public_claimability_activation_not_authorized_phase_1294
public_rc_remains_blocked_after_phase_1294
phase_1295_transport_principal_lifecycle_revocation_replay_preflight_next
transport_principal_lifecycle_revocation_replay_preflight_phase_1295.v0.1
transport_principal_lifecycle_revocation_replay_verdict_phase_1295=preflight_only_stale_helper_not_promotable
cdl087_ratified_but_phase_1277_helper_still_pre_ratification_gate_phase_1295
transport_principal_public_path_helper_not_promoted_phase_1295
transport_principal_lifecycle_policy_not_activated_phase_1295
transport_principal_revocation_registry_not_activated_phase_1295
transport_principal_replay_cache_not_activated_phase_1295
requester_id_fallback_still_forbidden_phase_1295
public_p2p_not_activated_phase_1295
public_fetch_serving_not_enabled_phase_1295
public_rc_remains_blocked_after_phase_1295
phase_1296_hostile_network_admission_ban_rate_privacy_plan_next
hostile_network_admission_ban_rate_privacy_plan_phase_1296.v0.1
hostile_network_plan_verdict_phase_1296=plan_recorded_no_activation
transport_principal_admission_policy_not_activated_phase_1296
transport_principal_ban_registry_not_activated_phase_1296
transport_principal_rate_limit_state_not_activated_phase_1296
transport_principal_privacy_policy_not_activated_phase_1296
requester_id_client_ip_agentid_fallback_still_forbidden_phase_1296
werner_overlay_not_activated_phase_1296
public_p2p_not_activated_phase_1296
public_fetch_serving_not_enabled_phase_1296
public_sidecar_projection_serving_not_enabled_phase_1296
public_rc_remains_blocked_after_phase_1296
phase_1297_sidecar_public_safe_projection_schema_next
sidecar_public_safe_projection_schema_phase_1297.v0.1
sidecar_public_safe_projection_schema_verdict_phase_1297=schema_recorded_no_serving
privacy_filtering_contract_recorded_phase_1297
sidecar_public_projection_fields_not_served_phase_1297
public_sidecar_projection_serving_not_enabled_phase_1297
public_rc_remains_blocked_after_phase_1297
phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_next
sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1
sidecar_bind_listener_peer_discovery_verdict_phase_1298=preflight_only_no_public_serving
non_loopback_bind_not_enabled_phase_1298
public_listener_not_enabled_phase_1298
peer_discovery_not_enabled_phase_1298
public_sidecar_projection_serving_not_enabled_phase_1298
public_rc_remains_blocked_after_phase_1298
phase_1299_release_allowlist_artifact_genesis_readiness_preflight_next
```

---

## 1. Current State

Window 1273-1280 is closed with a pass verdict. Window 1281-1288 is closed
with a pass verdict through Phase 1288. Phase 1288 Fix1 runtime deep audit
hardening is complete. Phase 1288 Fix2 drafted the narrower Window 1289-1296
prompt package, and Phase 1289 superseded that draft by opening the active
Window 1289-1302 sequence lock.

Current active sequence lock:

- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`

Current active guidance:

- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`

Superseded prompt-draft source:

- `docs/specs/ilc_window_1289_1296_candidate_phase_grouping_v0.1.md`

Current closure handoff:

- `docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md`

Current launch roadmap:

- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`

The user's explicit `GO Phase 1298 and any subsequent non-sensitive phases, in
order` authorized the Phase 1298 sidecar bind/listener/peer-discovery authority
preflight only. The next phase, Phase 1299, is sensitive because it preflights
release allowlist, artifact, and Genesis readiness and must not proceed without
explicit authorization.

---

## 2. Active Window Frontier

Phase 1289 records:

```text
window_1289_1302_sequence_lock_committed
window_1289_1302_sequence_lock_verdict=pass
phase_1290_context_capsule_v5_52_refresh_next
window_1289_1302_no_public_rc_or_public_activation
human_question_escalation_required_for_uncertain_authority
window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289
```

Phase 1290 records this capsule refresh:

```text
context_capsule_v5_52_frontier_refresh_phase_1290.v0.1
capsule_v5_52_supersedes_v5_51
window_1289_1302_sequence_lock_reflected_in_capsule_phase_1290
public_rc_blocker_map_refreshed_phase_1290
public_rc_remains_blocked_after_phase_1290
```

Historical Phase 1290 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1290
requires explicit `GO Phase 1291`
Phase 1290 does not close any of those blockers
```

Phase 1291 records the verifier contract preflight:

```text
public_claimability_verifier_contract_preflight_phase_1291.v0.1
public_claimability_activation_not_authorized_by_default_phase_1291
claimability_verifier_public_api_not_enabled_phase_1291
wallet_withdrawal_transfer_spend_still_blocked_phase_1291
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
claimability_contract_no_runtime_helper_added_phase_1291
phase_1292_verifier_negative_path_corpus_package_boundary_next
public_rc_remains_blocked_after_phase_1291
```

Historical Phase 1291 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1291
Phase 1292 is sensitive
```

Phase 1292 records the verifier negative-path corpus and package-profile boundary rehearsal:

```text
claimability_package_profile_allowlist_rehearsal_phase_1292.v0.1
source_allowlist_export_not_executed_phase_1292
public_package_publication_not_authorized_phase_1292
public_rc_exclude_helpers_preserved_phase_1292
verifier_negative_path_corpus_recorded_phase_1292
claimability_package_profile_boundary_verdict_phase_1292=pass_import_boundary_publication_blocked
ilc_logic_network_import_boundary_repaired_phase_1292
package_profile_ci_artifacts_refreshed_phase_1292
phase_1293_public_rc_exclude_helper_promotion_removal_register_next
public_rc_remains_blocked_after_phase_1292
```

Historical Phase 1292 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1292
Phase 1293 is sensitive
```

Phase 1293 records the `PUBLIC_RC_EXCLUDE` helper promotion/removal register:

```text
public_rc_exclude_helper_promotion_removal_register_phase_1293.v0.1
public_rc_exclude_helper_register_verdict_phase_1293=all_current_helpers_keep_internal_no_promotion
public_rc_exclude_helpers_keep_internal_phase_1293
public_rc_exclude_helper_promotion_not_authorized_phase_1293
public_rc_exclude_helper_removal_not_authorized_phase_1293
public_rc_exclude_helper_replacement_required_before_public_export_phase_1293
source_allowlist_export_not_executed_phase_1293
public_package_publication_not_authorized_phase_1293
public_rc_remains_blocked_after_phase_1293
phase_1294_claimability_package_allowlist_rehearsal_next
```

Historical Phase 1293 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1293
Phase 1294 is sensitive
```

Phase 1294 records the claimability package allowlist rehearsal:

```text
claimability_package_allowlist_rehearsal_phase_1294.v0.1
claimability_package_allowlist_verdict_phase_1294=rehearsal_pass_export_blocked
openclaw_skill_claimable_allowlist_rehearsed_phase_1294
public_rc_exclude_helpers_excluded_from_export_phase_1294
claimability_package_manifest_not_materialized_phase_1294
source_allowlist_export_not_executed_phase_1294
public_repository_publication_not_authorized_phase_1294
public_package_publication_not_authorized_phase_1294
public_claimability_activation_not_authorized_phase_1294
public_rc_remains_blocked_after_phase_1294
phase_1295_transport_principal_lifecycle_revocation_replay_preflight_next
```

Historical Phase 1294 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1294
Phase 1295 is sensitive
```

Phase 1295 records the TransportPrincipal lifecycle, revocation, and replay
preflight:

```text
transport_principal_lifecycle_revocation_replay_preflight_phase_1295.v0.1
transport_principal_lifecycle_revocation_replay_verdict_phase_1295=preflight_only_stale_helper_not_promotable
cdl087_ratified_but_phase_1277_helper_still_pre_ratification_gate_phase_1295
transport_principal_public_path_helper_not_promoted_phase_1295
transport_principal_lifecycle_policy_not_activated_phase_1295
transport_principal_revocation_registry_not_activated_phase_1295
transport_principal_replay_cache_not_activated_phase_1295
requester_id_fallback_still_forbidden_phase_1295
public_p2p_not_activated_phase_1295
public_fetch_serving_not_enabled_phase_1295
public_rc_remains_blocked_after_phase_1295
phase_1296_hostile_network_admission_ban_rate_privacy_plan_next
```

Historical Phase 1295 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1295
Phase 1296 is sensitive
```

Phase 1296 records the hostile-network admission, ban, rate-limit, and privacy
plan:

```text
hostile_network_admission_ban_rate_privacy_plan_phase_1296.v0.1
hostile_network_plan_verdict_phase_1296=plan_recorded_no_activation
transport_principal_admission_policy_not_activated_phase_1296
transport_principal_ban_registry_not_activated_phase_1296
transport_principal_rate_limit_state_not_activated_phase_1296
transport_principal_privacy_policy_not_activated_phase_1296
requester_id_client_ip_agentid_fallback_still_forbidden_phase_1296
werner_overlay_not_activated_phase_1296
public_p2p_not_activated_phase_1296
public_fetch_serving_not_enabled_phase_1296
public_sidecar_projection_serving_not_enabled_phase_1296
public_rc_remains_blocked_after_phase_1296
phase_1297_sidecar_public_safe_projection_schema_next
```

Historical Phase 1296 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1296
Phase 1297 is sensitive
```

Phase 1297 records the sidecar public-safe projection schema:

```text
sidecar_public_safe_projection_schema_phase_1297.v0.1
sidecar_public_safe_projection_schema_verdict_phase_1297=schema_recorded_no_serving
privacy_filtering_contract_recorded_phase_1297
sidecar_public_projection_fields_not_served_phase_1297
public_sidecar_projection_serving_not_enabled_phase_1297
public_rc_remains_blocked_after_phase_1297
phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_next
```

Historical Phase 1297 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1297
Phase 1298 is sensitive
```

Phase 1298 records the sidecar bind, listener, and peer-discovery authority
preflight:

```text
sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1
sidecar_bind_listener_peer_discovery_verdict_phase_1298=preflight_only_no_public_serving
non_loopback_bind_not_enabled_phase_1298
public_listener_not_enabled_phase_1298
peer_discovery_not_enabled_phase_1298
public_sidecar_projection_serving_not_enabled_phase_1298
public_rc_remains_blocked_after_phase_1298
phase_1299_release_allowlist_artifact_genesis_readiness_preflight_next
```

Locked Window 1289-1302 order:

| Phase | Scope | Sensitivity |
|-------|-------|-------------|
| 1289 | Window 1289-1302 sequence lock | SENSITIVE, complete |
| 1290 | Context Capsule v5.52 frontier refresh | NON-SENSITIVE, complete |
| 1291 | Public claimability verifier contract preflight | SENSITIVE, complete |
| 1292 | Verifier negative-path corpus and package-profile boundary | SENSITIVE, complete |
| 1293 | `PUBLIC_RC_EXCLUDE` helper promotion/removal register | SENSITIVE, complete |
| 1294 | Claimability package allowlist rehearsal | SENSITIVE, complete |
| 1295 | TransportPrincipal lifecycle, revocation, replay preflight | SENSITIVE, complete |
| 1296 | Hostile-network admission, ban, rate-limit, privacy plan | SENSITIVE, complete |
| 1297 | Sidecar public-safe projection schema | SENSITIVE, complete |
| 1298 | Sidecar bind, listener, peer-discovery authority preflight | SENSITIVE, complete |
| 1299 | Release allowlist, artifact, Genesis readiness preflight | SENSITIVE, requires explicit `GO Phase 1299` |
| 1300 | Counsel, IP, publication clearance inventory | SENSITIVE |
| 1301 | Deep no-activation assertion audit | SENSITIVE |
| 1302 | Window 1289-1302 closure gate | SENSITIVE |

---

## 3. Governance Frontier

CDL-087 is ratified as of Phase 1278 Fix1:

```text
cdl087_ratification_evidence_phase_1278_fix1.v0.1
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

CDL-088 remains unopened. Phase 1290 does not mutate the CDL register. Phases
1291, 1292, 1293, 1294, 1295, 1296, 1297, and 1298 also do not mutate the CDL
register and do not open any new constitutional decision log entry.

Open counsel/public-release obligations remain:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
```

---

## 4. Public-RC Blocker Map

Public RC remains blocked after Phase 1298 by:

- Final public claimability verifier/API authority and public endpoint
  authorization.
- Public-safe helper replacement or later explicit helper promotion
  prerequisites for any materialized public export.
- Public-safe disclosure schema is now recorded, but privacy filter
  implementation/review, replay/nullifier policy, and duplicate-claim registry
  remain open.
- Actual TransportPrincipal public-path activation authority, including
  post-ratification CDL-087 helper replacement, lifecycle policy, revocation
  registry, replay cache, admission, ban, rate-limit, and privacy controls.
- Actual public sidecar/projection serving authority, including public-safe
  field serving, filtering implementation, bind/listener policy, and
  peer-discovery policy. Phase 1298 records those bind/listener/peer-discovery
  surfaces as preflight-only and does not grant authority.
- Counsel/license/CLA/trademark/IP/publication clearance.
- Source allowlist export execution and public source/package publication.
- Release artifact production, release-key generation, release envelope
  production, and release manifest instance production.
- Genesis Atlas mutation/regeneration/signing if needed and v0.2 signing
  authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- Wallet withdrawal/transfer/spend semantics, wallet signing authority,
  wallet ledger-write authority, ECU minting, ILC settlement, and withdrawal
  runtime activation.

Phase 1295 closes the TransportPrincipal lifecycle/revocation/replay preflight
as a classification-only pass. Phase 1296 closes the hostile-network
admission/ban/rate/privacy plan as a planning-only pass. Phase 1297 records the
public-safe projection schema as a schema-only pass. Phase 1298 records
bind/listener/peer-discovery authority as a preflight-only pass. None of these
phases activates public path serving, lifecycle policy, revocation registry,
replay cache, admission policy, ban registry, rate-limit state, privacy policy,
sidecar projection serving, bind, listener, peer discovery, publication,
release, Genesis signing, v0.2 signing, wallet, ECU, or ILC blockers.

Exact blocker phrase guard:

```text
Final public claimability verifier/API authority
PUBLIC_RC_EXCLUDE helper replacement or later explicit promotion prerequisites
Public-safe disclosure schema
privacy filter implementation/review
replay/nullifier policy
Actual TransportPrincipal public-path activation authority
Actual public sidecar/projection serving authority
sidecar bind/listener policy
peer-discovery policy
Counsel/license/CLA/trademark/IP/publication clearance
Source allowlist export execution
Release artifact production
release-key generation
release envelope production
Genesis Atlas mutation/regeneration/signing
v0.2 signing authorization
CDL-088 opening
Wallet withdrawal/transfer/spend semantics
ECU minting
ILC settlement
```

---

## 5. Runtime Frontier

Public-path helper surfaces remain internal preflight helpers, not public RC
launch surfaces:

```text
transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1
transport_principal_public_p2p_not_activated_phase_1277
non_loopback_projection_still_blocked_phase_1277
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
sidecar_public_serving_not_enabled_phase_1278
no_new_public_listener_phase_1278
non_loopback_bind_not_enabled_phase_1278
public_projection_endpoint_not_enabled_phase_1278
```

Claimability and conversion helper surfaces remain local/offline:

```text
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
phase_1282_fix1_claimability_runtime_audit_hardening
phase_1288_fix1_runtime_deep_audit_hardening
canonical_payload_float_rejection_hardened_phase_1288_fix1
untrusted_payload_cycle_depth_bounds_hardened_phase_1288_fix1
public_path_preflight_key_shape_hardened_phase_1288_fix1
```

No runtime code changes are made by Phase 1290.

Phase 1291 adds no runtime helper. Existing local helper surfaces remain
internal preflight helpers and retain their `PUBLIC_RC_EXCLUDE` launch-surface
exclusion:

```text
claimability_contract_no_runtime_helper_added_phase_1291
ilc_core/ledger/cdl048_conversion_sweeper_runtime.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
ilc_core/ledger/claimability_proof_binding_runtime.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

Phase 1292 repairs the sidecar helper import boundary:

```text
ilc_logic_network_import_boundary_repaired_phase_1292
ilc_core/graph/sidecar_public_path_preflight.py no longer imports ilc_core.network
```

The helper remains `PUBLIC_RC_EXCLUDE`; Phase 1292 does not promote it to a
public RC launch surface.

Phase 1293 records the helper register and keeps all current runtime helpers
internal:

```text
public_rc_exclude_helpers_keep_internal_phase_1293
ilc_core/ledger/cdl048_conversion_sweeper_runtime.py keep_internal
ilc_core/ledger/claimability_proof_binding_runtime.py keep_internal
ilc_core/network/d2d/transport_principal_public_path_preflight.py keep_internal
ilc_core/graph/sidecar_public_path_preflight.py keep_internal
```

No helper is promoted, removed, replaced, exported, or made public-RC eligible
by Phase 1293.

Phase 1294 records that `openclaw_skill_claimable` remains a measured target
profile, not a materialized public export:

```text
claimability_package_allowlist_verdict_phase_1294=rehearsal_pass_export_blocked
openclaw_skill_claimable_allowlist_rehearsed_phase_1294
public_rc_exclude_helpers_excluded_from_export_phase_1294
```

The package-profile CI pass is preserved, but the raw measured profile is not
directly exportable because `ilc_core/graph/sidecar_public_path_preflight.py`
remains `PUBLIC_RC_EXCLUDE` inside the measured `ilc_logic` surface.

Phase 1295 records that the TransportPrincipal public-path helper remains an
internal preflight substrate and is not directly promotable:

```text
transport_principal_lifecycle_revocation_replay_verdict_phase_1295=preflight_only_stale_helper_not_promotable
cdl087_ratified_but_phase_1277_helper_still_pre_ratification_gate_phase_1295
transport_principal_public_path_helper_not_promoted_phase_1295
```

The blocker is specific: CDL-087 is ratified by Phase 1278 Fix1, but
`ilc_core/network/d2d/transport_principal_public_path_preflight.py` still
requires `authorization_flags.cdl087_ratified == False` under the old
`cdl087_not_ratified_by_phase_1277` token. That is safe only while the helper
remains `PUBLIC_RC_EXCLUDE`.

Phase 1297 records the public-safe projection schema without runtime changes:

```text
sidecar_public_safe_projection_schema_phase_1297.v0.1
sidecar_public_safe_projection_schema_verdict_phase_1297=schema_recorded_no_serving
privacy_filtering_contract_recorded_phase_1297
sidecar_public_projection_fields_not_served_phase_1297
public_sidecar_projection_serving_not_enabled_phase_1297
```

`ilc_core/graph/sidecar_query_runtime.py` remains a local/read-only bounded
runtime. `ilc_core/graph/sidecar_public_path_preflight.py` remains
`PUBLIC_RC_EXCLUDE` and records no listener, bind, or serving surface.

Phase 1298 records the sidecar bind/listener/peer-discovery authority preflight
without runtime changes:

```text
sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1
sidecar_bind_listener_peer_discovery_verdict_phase_1298=preflight_only_no_public_serving
non_loopback_bind_not_enabled_phase_1298
public_listener_not_enabled_phase_1298
peer_discovery_not_enabled_phase_1298
public_sidecar_projection_serving_not_enabled_phase_1298
```

The current sidecar helper remains `PUBLIC_RC_EXCLUDE` and deliberately does
not open a listener, bind a socket, serve projection data, or enable peer
discovery. Local in-process sidecar reads remain the only active sidecar path.

---

## 6. Non-Authorization Boundary

Phase 1298 does not authorize TransportPrincipal public-path activation,
admission policy activation, ban registry activation, public rate-limit state
activation, privacy policy activation, Werner overlay activation, public
credential issuer authority, credential lifecycle policy activation, public
revocation registry activation, public replay cache activation, materialized
export manifest production, helper promotion, marker removal, public RC, public
launch, public repository publication, public package publication, source
allowlist export execution, public release artifact production, release-key
generation, release envelope production, non-loopback bind, wildcard bind,
public host bind, public listener, socket listener, HTTP route, peer discovery,
public P2P, public fetch serving, public sidecar/projection serving,
non-loopback sidecar/projection serving, public claimability API activation,
public verifier service, public claimability activation, wallet withdrawal,
wallet transfer, wallet spend, wallet signing authority, wallet ledger-write
authority, ECU minting, ILC settlement, withdrawal runtime activation, CDL
mutation, CDL-088 opening, Genesis Atlas mutation/regeneration or signing, v0.2
signing, IP filing, paper publication, immutable diagnostic mutation, or
production `commit.epoch` emission.

Exact non-authorization phrase guard:

```text
public claimability API activation
materialized export manifest production
helper promotion
marker removal
public verifier service
TransportPrincipal public-path activation
public credential issuer authority
credential lifecycle policy activation
public revocation registry activation
public replay cache activation
non-loopback bind
wildcard bind
public host bind
public listener
socket listener
HTTP route
peer discovery
public P2P
public fetch serving
public sidecar/projection serving
source allowlist export execution
public release artifact production
release-key generation
release envelope production
wallet withdrawal
wallet transfer
wallet spend
CDL mutation
CDL-088 opening
Genesis Atlas mutation/regeneration
v0.2 signing
IP filing
paper publication
production `commit.epoch` emission
```

---

## 7. Phase 1291 Contract Boundary

Phase 1291 defines future `ClaimabilityVerifierInput` and
`ClaimabilityVerifierDecision` envelopes. It keeps all activation and economic
flags false, records mandatory future denial conditions, and leaves public-safe
field disclosure unresolved.

The Phase 1291 contract is a planning/spec boundary only:

```text
ClaimabilityVerifierInput
ClaimabilityVerifierDecision
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
```

No HTTP route, FastAPI route, socket listener, non-loopback bind, wildcard bind,
public host bind, peer discovery surface, public verifier service, public claim
endpoint, wallet withdrawal, wallet transfer, wallet spend, ECU mint endpoint,
or ILC settlement endpoint is added.

---

## 8. Next Gate

Next phase:

```text
Phase 1299 - Release allowlist, artifact, Genesis readiness preflight
```

Phase 1299 is sensitive. It requires explicit `GO Phase 1299` before execution.
Default authority stance remains no public endpoint, no public claimability API,
no source export, no helper promotion, no package publication, no public P2P or
fetch serving, no admission/ban/rate/privacy activation, no public sidecar or
projection serving, no bind/listener/peer-discovery activation, no release
artifact production, no release-key generation, no release envelope production,
no Genesis mutation/signing, no v0.2 signing, no wallet spend semantics, no ECU
minting, and no ILC settlement.
