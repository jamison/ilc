# ILC Antigravity Context Capsule v5.53

**Date:** 2026-05-11
**Produced by:** Phase 1304 - Context Capsule v5.53 frontier refresh; updated by Phases 1305-1316
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
**Window frontier:** Window 1303-1316 is CLOSED / PASS with carry-forward through Phase 1316
**Public RC status:** Blocked

```text
context_capsule_v5_53_frontier_refresh_phase_1304.v0.1
capsule_v5_53_supersedes_v5_52
window_1303_1316_sequence_lock_reflected_in_capsule_phase_1304
public_rc_blocker_map_refreshed_phase_1304
phase_1305_offline_claimability_receipt_verifier_sidecar_next
public_rc_remains_blocked_after_phase_1304
offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1
claimability_verifier_local_only_no_api_phase_1305
receipt_verifier_public_serving_not_enabled_phase_1305
public_claimability_activation_not_authorized_phase_1305
phase_1306_proof_binding_canonical_hash_negative_path_tests_next
public_rc_remains_blocked_after_phase_1305
proof_binding_canonical_hash_negative_path_tests_phase_1306.v0.1
forged_receipt_negative_paths_hardened_phase_1306
canonical_json_exact_numeric_proof_safety_hardened_phase_1306
replay_nullifier_duplicate_claim_policy_still_gated_phase_1306
phase_1307_sidecar_registry_manifest_profile_hardening_next
public_rc_remains_blocked_after_phase_1306
graph_native_sidecar_registry_manifest_phase_1307.v0.1
sidecar_manifest_deterministic_profile_declared_phase_1307
openclaw_compatible_local_bridge_profile_declared_phase_1307
confidential_coordination_local_preview_profile_declared_phase_1307
package_profile_integrity_hardened_phase_1307
phase_1308_public_rc_exclude_helper_pruning_replacement_plan_next
public_rc_remains_blocked_after_phase_1307
public_rc_exclude_helper_pruning_replacement_plan_phase_1308.v0.1
public_rc_exclude_helper_disposition_inventory_recorded_phase_1308
truth_primitive_sidecar_boundary_recorded_phase_1308
helper_stripping_not_executed_phase_1308
source_allowlist_export_not_executed_phase_1308
phase_1309_transport_principal_admission_sidecar_lifecycle_next
public_rc_remains_blocked_after_phase_1308
transport_principal_admission_sidecar_lifecycle_hardening_phase_1309.v0.1
transport_principal_lifecycle_policy_local_substrate_phase_1309
transport_principal_public_path_not_activated_phase_1309
public_p2p_not_activated_phase_1309
phase_1310_revocation_replay_admission_ban_tests_next
public_rc_remains_blocked_after_phase_1309
revocation_replay_admission_ban_tests_phase_1310.v0.1
transport_principal_revocation_replay_tests_hardened_phase_1310
admission_ban_rate_privacy_tests_hardened_phase_1310
hostile_network_public_path_still_blocked_phase_1310
phase_1311_local_graph_memory_projection_sidecar_next
public_rc_remains_blocked_after_phase_1310
local_graph_memory_projection_sidecar_phase_1311.v0.1
public_safe_projection_implementation_local_only_phase_1311
confidential_coordination_projection_reference_local_only_phase_1311
public_sidecar_projection_serving_not_enabled_phase_1311
phase_1312_projection_privacy_field_filtering_tests_next
public_rc_remains_blocked_after_phase_1311
projection_privacy_field_filtering_tests_phase_1312.v0.1
projection_privacy_filters_hardened_phase_1312
confidential_coordination_projection_non_leakage_tests_phase_1312
public_sidecar_projection_serving_not_enabled_phase_1312
phase_1313_public_fetch_p2p_activation_candidate_default_off_next
public_rc_remains_blocked_after_phase_1312
public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1
rust_public_p2p_substrate_gate_status_recorded_phase_1313
public_p2p_default_off_phase_1313
public_fetch_serving_default_off_phase_1313
transport_public_path_activation_not_authorized_phase_1313
phase_1314_wallet_withdrawal_transfer_spend_preflight_next
public_rc_remains_blocked_after_phase_1313
wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1
wallet_withdrawal_transfer_spend_not_activated_phase_1314
wallet_signing_ledger_write_not_authorized_phase_1314
public_claimability_user_action_boundary_recorded_phase_1314
phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next
public_rc_remains_blocked_after_phase_1314
ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1
ecu_minting_not_authorized_phase_1315
ilc_settlement_not_authorized_phase_1315
value_path_activation_boundary_recorded_phase_1315
phase_1316_window_1303_1316_closure_audit_next
public_rc_remains_blocked_after_phase_1315
window_1303_1316_closed_phase_1316
window_1303_1316_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1316_window_1303_1316_closure_complete
window_1317_plus_sequence_lock_required_before_next_phase_assignment
implementation_hardening_blockers_classified_phase_1316
public_rc_remains_blocked_after_phase_1316
```

---

## 1. Current Frontier

Capsule v5.53 supersedes Capsule v5.52. Capsule v5.52 remains a historical
snapshot through Window 1289-1302 closure and Phase 1303 sequence locking.
Capsule v5.53 is the current session-start capsule after Phase 1316.

Window 1289-1302 is closed. Its closure handoff remains the carry-forward
baseline:

```text
window_1289_1302_closed_phase_1302
window_1289_1302_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1302_window_1289_1302_closure_complete
public_rc_exclude_helper_stripping_carried_forward_to_window_1303_plus
public_rc_remains_blocked_after_phase_1302
```

Window 1303-1316 is CLOSED / PASS with carry-forward through Phase 1316.
The current closure handoff is:

```text
docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md
```

The consumed sequence lock is now a closed reference:

```text
docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md
```

The consumed guidance is now a closed reference:

```text
docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md
```

Phase 1303 opened the implementation-hardening window and records:

```text
window_1303_1316_sequence_lock_committed
window_1303_1316_sequence_lock_verdict=pass
phase_1304_context_capsule_v5_53_refresh_next
window_1303_1316_no_public_rc_or_public_activation
rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate
human_question_escalation_required_for_uncertain_authority
```

Phase 1304 records this capsule refresh and does not execute Phase 1305:

```text
context_capsule_v5_53_frontier_refresh_phase_1304.v0.1
capsule_v5_53_supersedes_v5_52
window_1303_1316_sequence_lock_reflected_in_capsule_phase_1304
public_rc_blocker_map_refreshed_phase_1304
phase_1305_offline_claimability_receipt_verifier_sidecar_next
public_rc_remains_blocked_after_phase_1304
```

Phase 1305 is complete after explicit `GO Phase 1305`. It records:

```text
offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1
claimability_verifier_local_only_no_api_phase_1305
receipt_verifier_public_serving_not_enabled_phase_1305
public_claimability_activation_not_authorized_phase_1305
phase_1306_proof_binding_canonical_hash_negative_path_tests_next
public_rc_remains_blocked_after_phase_1305
```

The local verifier substrate is:

```text
ilc_core/sidecars/claimability_receipt_verifier.py
```

It is local-only and no public API, no public verifier service, no public
claimability activation, no wallet withdrawal, no ECU minting, and no ILC
settlement are authorized.

Phase 1306 is complete after explicit `GO Phase 1306`. It records:

```text
proof_binding_canonical_hash_negative_path_tests_phase_1306.v0.1
forged_receipt_negative_paths_hardened_phase_1306
canonical_json_exact_numeric_proof_safety_hardened_phase_1306
replay_nullifier_duplicate_claim_policy_still_gated_phase_1306
phase_1307_sidecar_registry_manifest_profile_hardening_next
public_rc_remains_blocked_after_phase_1306
```

Phase 1306 hardens local proof-binding and canonical hash negative-path
coverage around the Phase 1305 verifier. It adds tests for forged receipts,
forged proofs, root drift, exact numeric drift, canonical JSON drift, decision
hash drift, and semantic decision forgery. It also hardens canonical payload
traversal to reject tuple values and oversized mapping keys before hashing.
Replay/nullifier and duplicate-claim registry policy remain gated blockers.

Phase 1307 is complete after explicit `GO Phase 1307`. It records:

```text
graph_native_sidecar_registry_manifest_phase_1307.v0.1
sidecar_manifest_deterministic_profile_declared_phase_1307
openclaw_compatible_local_bridge_profile_declared_phase_1307
confidential_coordination_local_preview_profile_declared_phase_1307
package_profile_integrity_hardened_phase_1307
phase_1308_public_rc_exclude_helper_pruning_replacement_plan_next
public_rc_remains_blocked_after_phase_1307
```

Phase 1307 adds deterministic local/package sidecar registry metadata at:

```text
ilc_core/sidecars/registry_manifest.py
```

It declares OpenClaw/NemoClaw-compatible local bridge and claimable local bridge
profiles, declares `confidential_coordination_local_preview` as private/local
only, embeds the Phase 1305 verifier manifest in registry integrity checks, and
hardens claimable package-profile integrity so the offline claimability receipt
verifier sidecar is required. It does not authorize public serving, public
package publication, source allowlist export, public confidential messaging,
wallet withdrawal, ECU minting, or ILC settlement.

Phase 1308 is complete after explicit `GO Phase 1308`. It records:

```text
public_rc_exclude_helper_pruning_replacement_plan_phase_1308.v0.1
public_rc_exclude_helper_disposition_inventory_recorded_phase_1308
truth_primitive_sidecar_boundary_recorded_phase_1308
helper_stripping_not_executed_phase_1308
source_allowlist_export_not_executed_phase_1308
phase_1309_transport_principal_admission_sidecar_lifecycle_next
public_rc_remains_blocked_after_phase_1308
```

Phase 1308 adds deterministic helper disposition metadata at:

```text
ilc_core/rc/public_rc_exclude_disposition.py
```

It maps all four current runtime helpers to `replace_before_export`, records
marked/legacy document exclusion policy, and records the truth-primitive
submission sidecar boundary for local graph-native use. It does not authorize
helper promotion, marker removal, helper stripping, source allowlist export,
clean public tree materialization, public serving, wallet withdrawal, ECU
minting, or ILC settlement.

Phase 1309 is complete after explicit `GO Phase 1309`. It records:

```text
transport_principal_admission_sidecar_lifecycle_hardening_phase_1309.v0.1
transport_principal_lifecycle_policy_local_substrate_phase_1309
transport_principal_public_path_not_activated_phase_1309
public_p2p_not_activated_phase_1309
phase_1310_revocation_replay_admission_ban_tests_next
public_rc_remains_blocked_after_phase_1309
```

Phase 1309 adds deterministic local-only TransportPrincipal admission sidecar
lifecycle substrate at:

```text
ilc_core/sidecars/transport_principal_admission.py
```

It consumes the Phase 1267 pre-public TransportPrincipal context validator,
emits canonical local admission decisions keyed only by authenticated
TransportPrincipal material, updates the sidecar registry, and extends the
sensitive-runtime guardrail to scan the new sidecar. It does not import or
promote the stale Phase 1277 `PUBLIC_RC_EXCLUDE` helper. It does not authorize
public P2P, public fetch serving, public sidecar/projection serving, public
credential issuer authority, public revocation registry activation, public
replay cache activation, public rate-limit state activation, non-loopback bind,
listener, peer discovery, source export, public package publication, wallet
withdrawal, ECU minting, or ILC settlement.

Phase 1310 is complete after explicit `GO Phase 1310`. It records:

```text
revocation_replay_admission_ban_tests_phase_1310.v0.1
transport_principal_revocation_replay_tests_hardened_phase_1310
admission_ban_rate_privacy_tests_hardened_phase_1310
hostile_network_public_path_still_blocked_phase_1310
phase_1311_local_graph_memory_projection_sidecar_next
public_rc_remains_blocked_after_phase_1310
```

Phase 1310 hardens hostile-network negative-path coverage and local admission
sidecar behavior for revocation, replay, admission, ban, rate-limit, and
privacy. It rejects fallback/private context keys such as `requester_id`,
`client_ip`, `AgentID`, wallet, stake, economic position, and graph position;
adds bounded local caller-supplied rate-limit counter checks keyed only by
authenticated `tp_rate:<sha256>` material; and rejects unexpected decision keys
or non-JSON value types before canonical validation. It does not authorize
public P2P, public fetch serving, public sidecar/projection serving, public
credential issuer authority, public revocation registry activation, public
replay cache activation, public rate-limit state activation, non-loopback bind,
listener, peer discovery, source export, public package publication, wallet
withdrawal, ECU minting, or ILC settlement.

Phase 1311 is complete after explicit `GO Phase 1311`. It records:

```text
local_graph_memory_projection_sidecar_phase_1311.v0.1
public_safe_projection_implementation_local_only_phase_1311
confidential_coordination_projection_reference_local_only_phase_1311
public_sidecar_projection_serving_not_enabled_phase_1311
phase_1312_projection_privacy_field_filtering_tests_next
public_rc_remains_blocked_after_phase_1311
```

Phase 1311 adds `ilc_core/sidecars/local_graph_memory_projection.py`, updates
the sidecar registry for `local_graph_memory_projection`, and extends the
sensitive-runtime guardrail to scan the new sidecar. The sidecar emits bounded
canonical local-only projection envelopes with aggregate summaries, opaque
private/gated shard header refs, and opaque encrypted coordination-node refs.
It denies plaintext, membership, route history, sealed payloads, AgentID,
requester/client IP/harness identities, wallet fields, stake fields, and
economic fields. It does not authorize public sidecar/projection serving,
non-loopback bind, public listener, peer discovery, public confidential
messaging, public confidential coordination serving, source export, public
package publication, wallet withdrawal, ECU minting, or ILC settlement.

Phase 1312 is complete after explicit `GO Phase 1312`. It records:

```text
projection_privacy_field_filtering_tests_phase_1312.v0.1
projection_privacy_filters_hardened_phase_1312
confidential_coordination_projection_non_leakage_tests_phase_1312
public_sidecar_projection_serving_not_enabled_phase_1312
phase_1313_public_fetch_p2p_activation_candidate_default_off_next
public_rc_remains_blocked_after_phase_1312
```

Phase 1312 hardens the local graph/memory projection sidecar with an
export-level raw-fragment leak guard, focused tests for deny-by-default field
filtering, confidential-coordination non-leakage tests, and bounded-serving
blocker tests. The sidecar registry now records `local_graph_memory_projection`
as
`local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312`.
No public sidecar/projection serving, non-loopback bind, public listener, peer
discovery, public P2P/fetch serving, public confidential messaging, public
confidential coordination serving, source export, public package publication,
wallet withdrawal, ECU minting, or ILC settlement is authorized.

Phase 1313 is complete after explicit `GO Phase 1313`. It records:

```text
public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1
rust_public_p2p_substrate_gate_status_recorded_phase_1313
public_p2p_default_off_phase_1313
public_fetch_serving_default_off_phase_1313
transport_public_path_activation_not_authorized_phase_1313
phase_1314_wallet_withdrawal_transfer_spend_preflight_next
public_rc_remains_blocked_after_phase_1313
```

Phase 1313 adds `ilc_core/sidecars/public_fetch_p2p_readiness.py`, updates the
sidecar registry with `public_fetch_p2p_readiness_candidate`, records Rust
QUIC/rustls source evidence from `ilc_consensus/src/network.rs`, classifies the
Rust public-P2P substrate gate as still required before public activation, and
classifies Python HTTP fetch/gossip as devnet/test rather than a public-P2P
substrate. No public P2P, public fetch serving, public listener, peer
discovery, non-loopback bind, public transport claim, public sidecar/projection
serving, source export, public package publication, wallet-facing withdrawal
requests, ECU minting, or ILC settlement is authorized.

Phase 1314 is complete after explicit `GO Phase 1314`. It records:

```text
wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1
wallet_withdrawal_transfer_spend_not_activated_phase_1314
wallet_signing_ledger_write_not_authorized_phase_1314
public_claimability_user_action_boundary_recorded_phase_1314
wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314
phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next
public_rc_remains_blocked_after_phase_1314
```

Phase 1314 adds `ilc_core/sidecars/wallet_action_semantics_preflight.py`,
updates the sidecar registry with `wallet_action_semantics_preflight`, and
requires that sidecar in the OpenClaw/NemoClaw claimable local bridge profile.
The current public wallet runtime remains read-only with only `wallet_status`,
`wallet_history`, `wallet_export`, and `ledger_summary`. No wallet-facing
withdrawal request, wallet-facing transfer request, wallet-facing spend
request, wallet-provider signing request, wallet-provider ledger-write request,
public claim endpoint, public claimability activation, source export, public
package publication, ECU minting, or ILC settlement is authorized. ILC remains
wallet-provider agnostic but not ledger-truth agnostic: wallets are adapters or
sidecars around ledger/graph/receipt truth, not truth sources.

Phase 1315 is complete after explicit `GO Phase 1315`. It records:

```text
ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1
ecu_minting_not_authorized_phase_1315
ilc_settlement_not_authorized_phase_1315
value_path_activation_boundary_recorded_phase_1315
phase_1316_window_1303_1316_closure_audit_next
public_rc_remains_blocked_after_phase_1315
```

Phase 1315 adds
`ilc_core/sidecars/value_path_activation_boundary_preflight.py`, updates the
sidecar registry with `value_path_activation_boundary_preflight`, and requires
that sidecar in the OpenClaw/NemoClaw claimable local bridge profile. It records
local read-only substrates while blocking ECU minting, ECU creation, ECU supply
mutation, ILC settlement, ILC transfer, settlement root publication,
withdrawal runtime, wallet writes, public claimability activation, public claim
endpoint serving, release materialization, and CDL-088 opening. No ECU minting,
no ILC settlement, no withdrawal runtime, no wallet-facing withdrawal request,
no wallet-facing transfer request, no wallet-facing spend request, no
wallet-provider signing request, no wallet-provider ledger-write request, no
public claim endpoint, no public claimability activation, and no value-path
activation is authorized.

Phase 1316 closes Window 1303-1316 with carried-forward blockers:

```text
window_1303_1316_closed_phase_1316
window_1303_1316_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1316_window_1303_1316_closure_complete
window_1317_plus_sequence_lock_required_before_next_phase_assignment
implementation_hardening_blockers_classified_phase_1316
public_rc_remains_blocked_after_phase_1316
```

Phase 1316 publishes
`docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md` and classifies local
implementation-hardening work as complete while carrying forward public/release
blockers. No next phase is assigned; Window 1317+ sequence lock is required
before any further phase assignment.

---

## 2. Current Canon Sources

Read these first for new work:

| Role | Path | Current use |
|------|------|-------------|
| Planning index | `docs/PLANNING_INDEX.md` | Session-start index and active frontier pointer. |
| Current capsule | `docs/specs/ilc_antigravity_context_capsule_v5.53.md` | Current capsule after Phase 1316. |
| Superseded capsule | `docs/specs/ilc_antigravity_context_capsule_v5.52.md` | Historical baseline through Phase 1303 sequence lock. |
| Status log | `docs/phases/STATUS.md` | Actual phase completion source of truth. |
| Window 1289-1302 handoff | `docs/specs/ilc_window_1289_1302_handoff_1302_v0.1.md` | Carry-forward blocker baseline. |
| Window 1303-1316 handoff | `docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md` | Closure handoff; Window 1303-1316 closed with carry-forward. |
| Window 1303-1316 sequence lock | `docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md` | Closed reference after Phase 1316. |
| Window 1303-1316 guidance | `docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md` | Closed consumed guidance and prompt registry. |
| Forward packaging/signing plan | `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | Planning-only future windows. |
| Public RC packaging gate | `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md` | Clean materialized public-tree rule. |
| Graph-native sidecar suite | `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | Harness-agnostic sidecar suite architecture. |
| Confidential coordination sidecar plan | `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md` | Private/local CCSS routing. |
| Graph-native sidecar registry manifest 1307 | `docs/specs/ilc_graph_native_sidecar_registry_manifest_1307_v0.1.md` | Deterministic local/package sidecar registry and profile hardening. |
| Public RC exclude helper disposition 1308 | `docs/specs/ilc_public_rc_exclude_helper_pruning_replacement_plan_1308_v0.1.md` | Helper replacement/strip/defer inventory and truth-primitive sidecar boundary. |
| TransportPrincipal admission sidecar lifecycle 1309 | `docs/specs/ilc_transport_principal_admission_sidecar_lifecycle_1309_v0.1.md` | Local-only TransportPrincipal admission sidecar lifecycle substrate; public path remains blocked. |
| Revocation replay admission ban tests 1310 | `docs/specs/ilc_revocation_replay_admission_ban_tests_1310_v0.1.md` | Hostile-network local negative-path tests and hardening for TransportPrincipal revocation, replay, admission, ban, rate-limit, and privacy; public path remains blocked. |
| Projection privacy field filtering tests 1312 | `docs/specs/ilc_projection_privacy_field_filtering_tests_1312_v0.1.md` | Local projection privacy/filtering hardening; public sidecar/projection serving remains blocked. |
| Public fetch/P2P default-off readiness 1313 | `docs/specs/ilc_public_fetch_p2p_activation_candidate_default_off_1313_v0.1.md` | Default-off readiness packet; public P2P/fetch/listener/peer-discovery/non-loopback bind remain blocked. |
| Wallet-facing value-action semantics preflight 1314 | `docs/specs/ilc_wallet_withdrawal_transfer_spend_semantics_preflight_1314_v0.1.md` | Preflight-only wallet-facing request boundary; withdrawal/transfer/spend/signing/ledger-write/public claim endpoint remain blocked and wallets remain adapters around ledger-truth objects. |
| ECU/ILC value-path activation boundary preflight 1315 | `docs/specs/ilc_ecu_minting_ilc_settlement_boundary_preflight_1315_v0.1.md` | Preflight-only ECU minting and ILC settlement boundary; minting/settlement/withdrawal runtime/wallet writes/public claim endpoint remain blocked and ILC remains wallet-provider agnostic but not ledger-truth agnostic. |
| Launch roadmap | `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Public-RC blocker map. |
| CDL register | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-087 ratified; CDL-088 unopened. |

Standing retrieval discipline:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Exact-token search is a completion check only. Each phase must also search
token components, synonyms, older names, code symbols, denial terms, and nearby
concepts before treating an implementation concept or blocker as absent.

---

## 3. Window 1303-1316 Phase Order

| Phase | Scope | Current status |
|-------|-------|----------------|
| 1303 | Window 1303-1316 sequence lock | Complete. Opened the window and no public authority. |
| 1304 | Context Capsule v5.53 frontier refresh | Complete in this capsule. Docs/canon only. |
| 1305 | Offline/local claimability and receipt verifier sidecar/library, no API serving | Complete. Local-only sidecar substrate; no public API. |
| 1306 | Proof-binding, canonical hash, and negative-path tests | Complete. Forged receipt/proof, exact numeric, and canonical JSON negative paths hardened; no public API. |
| 1307 | Graph-native sidecar registry/manifest plus claimability package profile hardening | Complete. Deterministic local/package registry and profile integrity hardened; no public serving. |
| 1308 | Helper pruning/replacement plan with `PUBLIC_RC_EXCLUDE` enforcement and truth-primitive sidecar boundary | Complete. All current runtime helpers mapped to `replace_before_export`; no export or stripping. |
| 1309 | TransportPrincipal admission sidecar lifecycle implementation hardening | Complete. Local-only admission sidecar substrate recorded; no public path activation. |
| 1310 | Revocation, replay, admission, and ban tests | Complete. Hostile-network local negative paths hardened; no public path activation. |
| 1311 | Local graph/memory projection sidecar and public-safe projection implementation | Complete. Local-only projection substrate; no public serving. |
| 1312 | Projection privacy and field-filtering tests | Complete. Privacy/filtering and confidential-coordination non-leakage tests hardened; no public serving. |
| 1313 | Public fetch/P2P readiness candidate, default off with no activation | Complete. Rust gate status recorded; no public P2P/fetch/listener/peer-discovery/non-loopback bind. |
| 1314 | Wallet-facing withdrawal, transfer, and spend request semantics preflight | Complete. Preflight-only wallet-facing boundary; no wallet write authority. |
| 1315 | ECU minting and ILC settlement boundary preflight | Complete. Preflight-only value-path boundary; no minting, settlement, withdrawal runtime, wallet write, public claim endpoint, or public claimability activation. |
| 1316 | Window closure and implementation audit | Complete. Window closed with carry-forward; no public activation. |

Phase 1313 closed as readiness-only/default-off. Any future activation-style
public fetch/P2P candidate still requires a separate Rust public-P2P substrate
ADR/integration gate before execution:

```text
rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate
rust_public_p2p_substrate_gate_status_recorded_phase_1313
public_p2p_default_off_phase_1313
public_fetch_serving_default_off_phase_1313
```

---

## 4. Public-RC Blocker Map

Public RC remains blocked after Phase 1316 by:

- legacy public-labeled FastAPI routes that must be excluded, replaced, or
  explicitly gated before clean public-RC packaging.
- public claimability verifier/API serving authority and public endpoint
  authorization. Phase 1305 adds the local-only verifier substrate, Phase 1306
  hardens local proof/canonical-hash negative paths, and Phase 1307 binds the
  offline verifier into claimable package-profile integrity, but public
  serving, public claim endpoint authority, replay/nullifier and
  duplicate-claim registry policy, and public-safe disclosure remain open.
- `PUBLIC_RC_EXCLUDE` helper replacement and dry-run export proof that a
  materialized public tree contains no marked helpers or stripped-helper imports.
- Privacy filter implementation/review, replay/nullifier and duplicate-claim
  registry policy.
- TransportPrincipal public-path activation authority, public credential
  issuer authority, public revocation registry, public replay cache, public
  rate-limit state, public admission and ban policy, privacy controls, Rust
  public-P2P substrate evidence, and public transport activation authority.
- Rust public-P2P substrate ADR/integration gate and hostile-network transport
  hardening.
- public sidecar/projection serving authority, including public-safe
  field serving, filtering implementation, bind/listener policy, and
  peer-discovery policy.
- Counsel-approved license/CLA/trademark/IP/publication clearance.
- Source allowlist export execution and clean materialized public tree
  production.
- Release artifact production, release-key generation, release envelope
  production, release signing material generation, and release artifact
  manifest instance production.
- Genesis Atlas mutation/regeneration/signing if needed and v0.2 signing
  authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- wallet-facing action activation for withdrawal, transfer, spend, signing,
  ledger-write, public claim endpoint submission, and withdrawal runtime.
- ECU minting activation, ILC settlement activation, and final value-path
  activation authority.

Exact blocker phrase guard:

```text
legacy public-labeled FastAPI routes
public claimability verifier/API serving authority
PUBLIC_RC_EXCLUDE helper replacement and dry-run export proof
privacy filter implementation/review
replay/nullifier and duplicate-claim registry policy
TransportPrincipal public-path activation authority
Rust public-P2P substrate ADR/integration gate
public sidecar/projection serving authority
Counsel/license/CLA/trademark/IP/publication clearance
source allowlist export execution
clean materialized public tree production
release artifact production
release-key generation
release envelope production
release signing material generation
Genesis Atlas mutation/regeneration/signing
v0.2 signing authorization
CDL-088 opening
wallet-facing action activation
Wallet-provider signing and ledger-write activation
ECU minting activation
ILC settlement activation
final value-path activation authority
```

Phase 1305 narrows the local verifier substrate portion of Gap 13. Phase 1306
narrows its proof-binding, canonical-hash, and negative-path test coverage.
Phase 1307 narrows Gap 14 by making the graph-native sidecar registry and
claimable package-profile relationship executable and deterministic. Phase 1308
records helper disposition and the truth-primitive boundary. Phase 1309 narrows
the local TransportPrincipal lifecycle substrate blocker. Phase 1314 narrows
the wallet-facing user-action semantics blocker by recording a deterministic
preflight-only boundary, and Phase 1315 records the ECU/ILC value-path boundary,
but neither activates wallet-facing actions, ECU minting, or ILC settlement.
Phase 1316 closes the window as an implementation audit, not as an activation
gate. These phases do not close the public claimability verifier/API serving
authority blocker, source export/materialization blocker, public
TransportPrincipal activation blocker, or any other public-RC blocker.

---

## 5. Public RC Packaging Rule

The controlling architecture rule remains the materialized-public-tree rule:
public RC packages must be built from a clean public tree, not from private
helpers whose flags are flipped at release time.

`PUBLIC_RC_EXCLUDE` is a deny marker, not allowlist clearance. Absence of the
marker is also not allowlist clearance. Legacy untagged documents remain
excluded or review-required before public export.

Phase 1308 is the first helper disposition planning point. It must map each
current helper to exactly one of:

| Disposition | Meaning |
|-------------|---------|
| `replace_before_export` | Implement a public-safe module and remove exported-code dependencies on the internal helper before any export materialization. |
| `strip_from_export` | Exclude the helper from public source/package/release artifacts and prove exported code has no import dependency on it. |
| `defer_public_rc` | Carry the blocker forward and do not claim public RC for the affected package profile. |

Phase 1308 did not execute helper stripping. Dry-run materialization remains
routed to Phase 1319. Export execution remains routed to Phase 1333 if later
explicitly authorized.

Phase 1306 records the deterministic scaffold compilation rule: private
development scaffolding and token chains remain valid in the development
workspace, but public RC materialization must deterministically compile them
into final contracts or exclude them by disposition. The current disposition
vocabulary is `compile_into_contract`, `retain_as_public_metadata`,
`retain_internal_only`, `strip_from_export`, and `replace_before_export`.
Phase 1307 records these dispositions in the registry source-allowlist
readiness block without executing export or materialization.

---

## 6. Graph-Native Sidecar Routing

OpenClaw, NemoClaw, DigitalOcean droplets, or any later harness are hosts or
consumers, not protocol substrates. OpenClaw/NemoClaw are hosts or consumers, not protocol substrates.
The ILC direction is a graph-native sidecar suite with harness-agnostic adapter
boundaries.

Essential sidecar ordering inside Window 1303-1316:

| Order | Sidecar | Candidate phase target |
|-------|---------|------------------------|
| 1 | Offline claimability and receipt verifier sidecar | 1305/1306 |
| 2 | Sidecar registry and deterministic manifest | 1307 complete |
| 3 | Truth primitive submission sidecar boundary | 1308 |
| 4 | TransportPrincipal admission sidecar substrate | 1309/1310 |
| 5 | Local graph/memory projection sidecar | 1311/1312 |
| 6 | Confidential coordination local preview profile | 1307 prerequisites, 1311/1312 projection prerequisites, 1324-1329 implementation/dry-run lane |

Confidential coordination remains private/local by default and not a first
public-RC blocker unless later explicitly selected:

```text
confidential_coordination_sidecar_suite_forward_plan_recorded
confidential_coordination_sidecar_suite_graph_native_not_signal_clone
confidential_coordination_sidecar_suite_not_public_rc_blocker_by_default
confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329
confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only
```

Phase 1307 declares the `confidential_coordination_local_preview` profile as
private/local only. It does not authorize public confidential messaging or
public confidential coordination serving.

---

## 7. Governance And Runtime Frontier

CDL-087 is ratified. CDL-088 remains unopened. Phase 1308 does not mutate the
CDL register and does not open CDL-088.

Current helper and runtime boundaries remain as carried forward by Capsule
v5.52 and the Phase 1302 handoff:

- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` remains internal and
  is mapped to `replace_before_export`.
- `ilc_core/ledger/claimability_proof_binding_runtime.py` remains internal and
  is mapped to `replace_before_export`.
- `ilc_core/network/d2d/transport_principal_public_path_preflight.py` remains
  internal and stale relative to ratified CDL-087 until replaced by the
  TransportPrincipal admission sidecar or carried forward safely.
- `ilc_core/graph/sidecar_public_path_preflight.py` remains internal and is
  mapped to `replace_before_export`.
- `ilc_core/rc/public_rc_exclude_disposition.py` records the Phase 1308 helper
  disposition inventory and truth-primitive sidecar boundary.
- Local/in-process sidecar reads remain distinct from public sidecar serving.
- Legacy `/v1/public/*` FastAPI routes in `ilc_core/server.py` remain a public
  RC cleanliness blocker.

Phase 1314 and Phase 1315 change only local value-action and value-path
preflight metadata plus registry/package-profile boundary records. Phase 1316
changes only closure and carry-forward metadata. These phases do not change
public serving, public transport, wallet-facing activation, ECU minting, ILC
settlement, release, signing, or CDL behavior.

---

## 8. Non-Authorization Boundary

Phase 1316 does not authorize public RC claim, public launch claim, source
export, source publication, package publication, release artifact production,
release artifact manifest instance production, release-key generation, release
envelope production, release signing material generation, public claimability
activation, public claimability API activation, public verifier service, public
claim endpoint, HTTP route activation, FastAPI route activation, socket
listener, non-loopback bind, wildcard bind, public host bind, public listener,
peer discovery, public P2P, public fetch serving, public sidecar/projection
serving, non-loopback sidecar/projection serving, TransportPrincipal public-path
activation, public credential issuer authority, credential lifecycle policy
activation, public revocation registry activation, public replay cache
activation, admission policy activation, ban registry activation, public
rate-limit state activation, privacy policy activation, Werner overlay
activation, helper promotion, marker removal, helper stripping, materialized
export manifest production, clean public export tree production, CDL mutation,
CDL-088 opening, Genesis Atlas mutation, Genesis Atlas regeneration, Genesis
Atlas signing, v0.2 signing, IP filing, paper publication, patent-sensitive
public disclosure, public confidential messaging, public confidential
coordination serving, wallet-facing withdrawal requests, wallet-facing transfer
requests, wallet-facing spend requests, wallet-provider signing authority,
wallet-provider ledger-write authority, public claim endpoint submission,
external chain destination collection, ECU minting, ILC settlement, withdrawal
runtime activation, immutable diagnostic mutation, or production `commit.epoch`
emission.

Exact non-authorization phrase guard:

```text
public claimability API activation
public verifier service
public P2P
public fetch serving
public sidecar/projection serving
source allowlist export execution
public release artifact production
release artifact manifest instance production
release-key generation
release envelope production
wallet-facing withdrawal request
wallet-facing transfer request
wallet-facing spend request
wallet-provider signing request
wallet-provider ledger-write request
public claim endpoint
ECU minting
ILC settlement
CDL mutation
CDL-088 opening
Genesis Atlas mutation/regeneration
v0.2 signing
IP filing
paper publication
production `commit.epoch` emission
```

---

## 9. Next Gate

No next phase is assigned. Window 1317+ sequence lock is required before any
further phase assignment or execution:

```text
window_1317_plus_sequence_lock_required_before_next_phase_assignment
```
