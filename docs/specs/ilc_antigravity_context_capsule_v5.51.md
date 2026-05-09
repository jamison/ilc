# ILC Antigravity Context Capsule v5.51

**Date:** 2026-05-09
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
**Produced:** Phase 1282, Window 1281-1288
**Frontier:** Window 1281-1288 open through Phase 1282; Phase 1283 sensitive public-claimability authority gate pending

```text
context_capsule_v5_51_frontier_refresh_phase_1282.v0.1
capsule_v5_51_supersedes_v5_50
cdl087_ratification_reflected_in_capsule_phase_1282
window_1273_1280_closure_reflected_in_capsule_phase_1282
public_rc_remains_blocked_after_phase_1282
```

---

## 1. Current State

Window 1273-1280 is closed with a pass verdict, Phase 1280 Fix1 hardening is
complete, Window 1281-1288 is open through Phase 1282, and Phase 1283 is the
next locked phase. Phase 1283 is sensitive and requires explicit `GO Phase 1283`.

Current active window lock:

- `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md`

Current prior-window handoff:

- `docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md`

Current launch roadmap:

- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`

Current H/IP planning hardening packet:

- `docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md`

Phase 1282 is a docs/canon refresh only. It does not authorize public RC,
public serving, source publication, release artifacts, release keys, release
envelopes, Genesis mutation, CDL mutation, CDL-088 opening, public
claimability, ECU minting, ILC settlement, or v0.2 signing.

---

## 2. Phase Frontier

Recent frontier tokens:

```text
window_1273_1280_closed_phase_1280
window_1273_1280_closure_gate_verdict=pass
phase_1280_window_1273_1280_closure_complete
public_rc_remains_blocked_after_phase_1280
phase_1280_fix1_hypergraph_laplacian_docs_hardened
h_series_020_plus_registered_phase_1280_fix1
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
public_rc_candidate_standard_preserved_phase_1280_fix1
public_rc_remains_blocked_after_phase_1280_fix1
window_1281_1288_sequence_lock_committed
window_1281_1288_sequence_lock_verdict=pass
phase_1282_context_capsule_v5_51_refresh_next
window_1281_1288_no_public_rc_or_public_activation
human_question_escalation_required_for_uncertain_authority
context_capsule_v5_51_frontier_refresh_phase_1282.v0.1
capsule_v5_51_supersedes_v5_50
```

Locked Window 1281-1288 order:

| Phase | Topic | Sensitivity |
|-------|-------|-------------|
| 1281 | Window 1281-1288 sequence lock | SENSITIVE, complete |
| 1282 | Context Capsule v5.51 frontier refresh | NON-SENSITIVE, complete |
| 1283 | Public claimability authority decision preflight | SENSITIVE, pending explicit `GO Phase 1283` |
| 1284 | Public claimability verifier/API boundary preflight | SENSITIVE |
| 1285 | TransportPrincipal public-path activation preflight | SENSITIVE |
| 1286 | Sidecar public projection privacy/serving preflight | SENSITIVE |
| 1287 | Release publication and v0.2 signing authorization preflight | SENSITIVE |
| 1288 | Window 1281-1288 closure gate | SENSITIVE |

---

## 3. Governance Frontier

CDL-087 is ratified as of Phase 1278 Fix1:

```text
cdl087_ratification_evidence_phase_1278_fix1.v0.1
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
cdl087_ratification_reflected_in_capsule_phase_1282
```

The current CDL register row records CDL-087 as ratified and points to:

- `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md`

CDL-087 ratification does not authorize public serving or new public economic
semantics:

```text
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

CDL-088 remains unopened. Reciprocal scoring, ECU-escrow admission, public
fetch serving, and public sidecar/projection serving remain separately gated.

Open counsel/public-release obligations remain:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
```

Phase 1280 Fix1 registered an internal publication/IP planning lane:

```text
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
PUBLIC_RC_EXCLUDE: internal_ip_publication_planning_not_public_rc_launch_surface
```

That lane does not file IP, publish papers, publish source, or authorize public
release material.

---

## 4. Runtime Frontier

`commit.epoch` connector stack remains implemented through the Phase 1236
connector/finalized adapter lane, but production emission remains unauthorized:

```text
COMMIT_EPOCH_CANONICAL_DEPENDENCY = "commit_epoch_canonical_constructor_phase_1235.v0.1"
COMMIT_EPOCH_EMISSION_RUNTIME_VERSION = "commit_epoch_emission_runtime_1236.v0.1"
COMMIT_EPOCH_QUORUM_PROJECTION_VERSION = "commit_epoch_quorum_projection_1236_fix2.v0.1"
COMMIT_EPOCH_CAUSAL_FRONTIER_PROJECTION_VERSION = "commit_epoch_causal_frontier_projection_1236_fix3.v0.1"
COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION = "commit_epoch_finalized_adapter_1236_fix4.v0.1"
commit_epoch_production_emission_not_yet_authorized
```

Sidecar query runtime remains local/read-only:

```text
SIDECAR_QUERY_RUNTIME_VERSION = "sidecar_query_runtime_1237.v0.1"
SIDECAR_PROJECTION_DEPENDENCY = "agent_graph_projection_runtime_1229.v0.1"
```

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

Claimability/conversion helper surfaces remain local:

```text
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
phase_1282_fix1_claimability_runtime_audit_hardening
claimability_conversion_receipt_semantics_hardened_phase_1282_fix1
settled_runtime_root_domain_separation_hardened_phase_1282_fix1
balance_receipt_decimal_boundary_hardened_phase_1282_fix1
cdl048_conversion_sweeper_public_rc_exclude_marked_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282_fix1
```

No wallet withdrawal, transfer, spend, wallet signing authority, wallet
ledger-write authority, ECU minting, ILC settlement, or withdrawal runtime is
authorized by this capsule.

Phase 1282 Fix1 hardens the local claimability/conversion helpers after
deterministic implementation audit. The current local verifier now rejects
hash-consistent forged conversion receipts when CDL-048 deadline math,
conversion epoch bounds, transition, conversion-key derivation, root namespace,
positive Decimal amount, required tokens, or false activation flags do not
match. Latest balance receipt economic fields must be finite Decimal strings,
and `settled_runtime_root` accepts only the `settled_runtime_sha256:` namespace.
The helpers remain internal and public RC remains blocked.

---

## 5. SIM-FETCH and Canonical Fetch Frontier

SIM-FETCH-01 evidence remains implemented through Phase 1238j and was later
consumed by the CDL-087 evidence chain:

```text
SIM_FETCH_01_HARNESS_VERSION = "sim_fetch_01_harness_1238j.v0.1"
SIM_FETCH_01_FIX10_VERSION = "sim_fetch_01_fix10_robustness_suite_1238j.v0.1"
sim_fetch_01_cdl_087_robustness_suite_committed_phase_1238j
sim_fetch_01_negative_control_validated_phase_1238j
sim_fetch_01_retry_and_adaptive_recovery_validated_phase_1238j
```

CDL-087 ratification now consumes that evidence plus later Phase 1258-1260 and
Phase 1276-1278 evidence. Public fetch serving remains not enabled.

Werner overlay remains simulation/evidence unless separately promoted:

```text
topology_pressure_model_werner_v1_profile_recorded_phase_1269
no_werner_ecu_minting_or_ilc_settlement_phase_1269
direct_werner_ecu_creation_rejected_phase_1263
```

---

## 6. Public RC Frontier

OpenClaw/NemoClaw skill-first remains the selected public-RC direction, with no
public ILC-owned P2P claim on the default RC path.

Current profile split:

- `openclaw_skill_local` - local preview only; no public claimability claim.
- `openclaw_skill_claimable` - final public-RC target; public ECU-to-ILC
  claimability present only after explicit authority and implementation gates.
- `full_node_public_p2p` - future full node profile requiring TransportPrincipal
  and hostile-network hardening.

Public RC remains blocked after Phase 1282:

```text
public_rc_remains_blocked_after_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282
public_rc_remains_blocked_after_phase_1280_fix1
public_rc_remains_blocked_after_phase_1280
```

Current blocker classes:

- public claimability authority and verifier/API boundary.
- TransportPrincipal public-path activation, lifecycle, revocation, replay,
  admission, ban, and hostile-network hardening.
- public sidecar/projection serving authorization, privacy review,
  non-loopback bind/listener policy, and peer-discovery policy.
- Counsel/license/CLA/trademark/patent/publication authorization.
- Source allowlist export execution, public source publication, public package
  publication, release artifacts, release keys, release envelopes, and release
  manifest instance production.
- Genesis Atlas mutation/regeneration/signing and v0.2 signing authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- ECU minting, ILC settlement, and withdrawal runtime activation.

---

## 7. Genesis Atlas Frontier

Signed Genesis v0.1 remains canonical and unchanged:

- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

Committed immutable diagnostic anchor:

- `out/genesis_compile_coverage_diagnostic_v0.1.json`
- Expected SHA-256:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Unsigned v0.2 candidate:

- Nodes: 41
- Edges: 73
- v0.2 remains unsigned.
- Token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

Genesis Atlas v0.2 signing remains deferred until the Atlas-G tail and requires
explicit signing authorization.

---

## 8. Stale v5.50 Corrections

This capsule supersedes v5.50 because v5.50 was produced at Phase 1239 and no
longer reflects the live frontier:

| v5.50 area | v5.51 correction |
|------------|------------------|
| CDL-087 state | CDL-087 is ratified by Phase 1278 Fix1 and reflected here by `cdl087_ratification_reflected_in_capsule_phase_1282`. |
| Window state | Window 1273-1280 is closed by Phase 1280 and reflected here by `window_1273_1280_closure_reflected_in_capsule_phase_1282`. |
| H/IP planning | Phase 1280 Fix1 registered H-020..H-028 and IP-001..IP-006 without public-RC authority. |
| Runtime audit hardening | Phase 1282 Fix1 hardened local claimability/conversion receipt semantics without public activation. |
| Active window | Window 1281-1288 is open through Phase 1282 Fix1; Phase 1283 is sensitive and pending. |
| Public RC | Public RC remains blocked after Phase 1282 Fix1. |

```text
capsule_v5_51_supersedes_v5_50
```

---

## 9. MemPalace Disposition

No callable MemPalace tool is exposed to Codex in this session. MemPalace
remains advisory-only. Current execution relied on direct repo canon:
`docs/PLANNING_INDEX.md`, `docs/phases/STATUS.md`, the active sequence lock,
the prior handoff, the CDL register, and committed phase packets.

---

## 10. Verification

Phase 1282 verification:

- Phase 1282 focused capsule tests passed.
- Sensitive-runtime guardrail passed.
- CDL register diff remained clean.
- Scoped `git diff --check` passed.

Phase 1282 Fix1 verification:

- Focused claimability/conversion hardening tests passed.
- Sensitive-runtime guardrail passed.
- Scoped `git diff --check` passed.

Phase 1283 remains pending and SENSITIVE.

```text
context_capsule_v5_51_frontier_refresh_phase_1282.v0.1
capsule_v5_51_supersedes_v5_50
cdl087_ratification_reflected_in_capsule_phase_1282
window_1273_1280_closure_reflected_in_capsule_phase_1282
public_rc_remains_blocked_after_phase_1282
phase_1282_fix1_claimability_runtime_audit_hardening
claimability_conversion_receipt_semantics_hardened_phase_1282_fix1
settled_runtime_root_domain_separation_hardened_phase_1282_fix1
balance_receipt_decimal_boundary_hardened_phase_1282_fix1
cdl048_conversion_sweeper_public_rc_exclude_marked_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282_fix1
```
