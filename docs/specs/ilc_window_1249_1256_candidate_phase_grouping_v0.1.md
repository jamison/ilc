# ILC Window 1249-1256 Candidate Phase Grouping v0.1

**Status:** Planning-only candidate guidance / prompt-draft registry.
**Recorded:** 2026-05-08.
**Authority:** This document does not open Window 1249-1256, assign official
phase authority, authorize public RC, authorize public repository publication,
mutate any CDL, activate public claimability, expose public P2P, mutate Genesis,
or authorize v0.2 signing. Exact execution authority must be set by the future
Phase 1249 sequence lock after explicit human `GO Phase 1249`.

```text
window_1249_1256_candidate_phase_grouping_recorded_after_phase_1248
window_1249_1256_not_open_until_sequence_lock
```

---

## 1. Purpose

Window 1241-1248 closed with Roadmap v1.1 controlling, Gap 14 first slices
landed, CDL-087 review-only disposition complete, and ATLAS-G-001..003 complete.
Public RC remains blocked by package boundary debt, public claimability,
CDL-087 production-candidate evidence, ATLAS-G public-RC graph reachability,
TransportPrincipal, counsel/IP/allowlist work, and v0.2 signing authorization.

This candidate grouping turns the Phase 1248 handoff into the next executable
window plan. The emphasis is actual public-RC code readiness, not another
documentation-only pass:

```text
gap_14_adapter_extraction_and_package_ci_gate_should_continue_before_public_rc_claim
gap_13_public_claimability_runtime_should_start_before_final_public_rc_claim
transport_principal_identity_required_before_public_p2p
atlas_g_004_high_authority_gap_closure_required
atlas_g_005_import_dependency_graph_bridge_required
```

---

## 2. Retrieval And Verification Basis

Direct current-canon inputs:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
3. `docs/phases/STATUS.md`
4. `docs/specs/ilc_window_1241_1248_handoff_1248_v0.1.md`
5. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
6. `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`
7. `docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md`
8. `docs/specs/ilc_tla_plus_formal_verification_forward_planning_v0.1.md`
9. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Direct lineage reads used for the Gap 13 / claimability slice:

1. `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
2. `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md`
3. `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py`
4. `ilc_core/protocol/public_wallet_runtime.py`
5. `ilc_core/rc/package_profiles.py`

MemPalace was used only as advisory retrieval support. Relevant historical
hits pointed back to the Phase 576 and Phase 615 settlement/wallet boundary
documents. Those documents were direct-read before this grouping treated their
tokens as planning inputs.

Standing retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
```

---

## 3. Candidate Phase Order

| Phase | Candidate scope | Sensitivity | Prompt draft |
|-------|-----------------|-------------|--------------|
| 1249 | Window 1249-1256 sequence lock | **SENSITIVE** - requires `GO Phase 1249` | `docs/antigravity_tasks/antigravity_prompt__phase_1249_g8_window_1249_1256_sequence_lock.md` |
| 1250 | Gap 14 adapter extraction for `ilc_logic` migration debt | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1250_g8_gap14_adapter_extraction_import_debt.md` |
| 1251 | Gap 14 package CI gate, profile export audit, and package-size measurement | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1251_g8_gap14_package_ci_and_profile_size_audit.md` |
| 1252 | Gap 13 claimability resolution boundary and chain/crypto dependency inventory | **SENSITIVE** - requires `GO Phase 1252` | `docs/antigravity_tasks/antigravity_prompt__phase_1252_g8_gap13_claimability_resolution_boundary.md` |
| 1253 | TransportPrincipal identity spec and Python HTTP devnet downgrade plan | NON-SENSITIVE design/spec only | `docs/antigravity_tasks/antigravity_prompt__phase_1253_g8_transport_principal_identity_and_http_downgrade.md` |
| 1254 | ATLAS-G-004/005 high-authority classification plus import/dependency graph bridge | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1254_g8_atlas_g_004_005_high_authority_dependency_bridge.md` |
| 1255 | TLA+ refinement notes and allowlist-export procedure | NON-SENSITIVE procedure/doc closure | `docs/antigravity_tasks/antigravity_prompt__phase_1255_g8_tla_refinement_and_allowlist_export.md` |
| 1256 | Window 1249-1256 coherence, blocker classification, and closure gate | **SENSITIVE** - requires `GO Phase 1256` | `docs/antigravity_tasks/antigravity_prompt__phase_1256_g8_window_1249_1256_closure_gate.md` |

---

## 4. Scope Rationale

### 4.1 Gap 14 remains first on the public-RC critical path

The selected default public-RC posture remains OpenClaw/NemoClaw skill-first
with no public ILC-owned P2P claim. Therefore the immediate blocker is a clean,
dependency-isolated package/skill surface, not public P2P.

Phase 1250 should retire or route the Phase 1244 `ilc_logic` migration debt:

```text
ilc_logic_import_boundary_migration_debt_recorded_phase_1244
```

The recorded debt is specific and testable: proposed `ilc_logic` surfaces still
pull storage/node runtime modules that should sit behind adapter or harness
interfaces before any public package claim.

Phase 1251 then turns the scanner into a package CI gate and measures the
selected package profile rather than using monorepo line counts as a proxy.

### 4.2 Gap 13 is sensitive and must not silently widen wallet semantics

Public claimability is required for the final public-RC profile, but existing
canon keeps wallet visibility and internal settlement separate from public
withdrawal/transfer/claim rights:

```text
rc0_1_balance_visibility_does_not_imply_public_claimability
ecu_accrual_reaches_ilc_balance_only_through_epoch_commit
wallet_visibility_and_accounting_only
no_public_claimability_or_spend_in_lifecycle_spec
```

Phase 1252 should be a sensitive boundary/inventory phase. It may specify what
public claimability requires, inventory chain/cryptography/Rust dependencies,
and define the transition from deferred claimability to a future executable
runtime. It must not activate public claimability or imply that agent-specific
manual claims are required where canon instead routes conversion through epoch
commit and settled runtime roots.

### 4.3 TransportPrincipal starts in parallel, not as the default RC path

TransportPrincipal remains required before public P2P and before any non-loopback
sidecar/projection serving. Phase 1253 should produce a design/spec/ADR-input
packet and formally classify Python HTTP transports as devnet/test where
appropriate. It must not expose public P2P, bind public sidecar endpoints, or
implement a runtime identity layer before the lifecycle and revocation contract
is locked.

### 4.4 ATLAS-G-004/005 bridges graph reachability to real imports

ATLAS-G-001..003 created graph-delta discipline and package-profile reachability
manifests. Phase 1254 should continue with high-authority source classification
and import/dependency graph bridge work so package modularity and graph
reachability stop drifting independently.

### 4.5 TLA refinement and allowlist-export are low-cost pre-RC closures

The TLA forward plan records `tla_refinement_notes_pre_rc` as a small, high-value
doc-only item mapping TLA variables to Rust implementation points. The allowlist
export procedure remains a public-repository-publication blocker. Phase 1255
should close both as non-sensitive documentation/procedure work without
publishing the repo or making a public RC claim.

---

## 5. Window Exit Criteria

Window 1249-1256 should not close as pass unless all of the following are true:

1. Phase 1249 sequence lock exists and records exact sensitive gates.
2. Gap 14 adapter extraction either closes the Phase 1244 `ilc_logic` migration
   debt or leaves a file-by-file carry-forward with exact blockers.
3. Package CI/import-boundary gate exists for selected public-RC package
   profiles, or the closure handoff states why it remains blocked.
4. Public package size/profile audit measures selected profile content rather
   than monorepo LOC.
5. Gap 13 claimability boundary records whether public claimability remains
   deferred and what chain/crypto/Rust dependencies must close before runtime.
6. TransportPrincipal design/spec packet records issuance, rotation, revocation,
   replay, privacy, and rate-limit key requirements without public exposure.
7. ATLAS-G-004/005 produces high-authority classification and import/dependency
   graph bridge artifacts or exact carry-forward blockers.
8. TLA refinement notes and allowlist-export procedure are closed or explicitly
   carried forward with file-level references.

---

## 6. Non-Claims

This guidance does not:

- open Window 1249-1256;
- execute Phase 1249;
- ratify CDL-087;
- open CDL-088;
- mutate any CDL row;
- authorize public RC;
- authorize public repository publication;
- authorize public P2P exposure;
- authorize public sidecar/projection serving;
- activate public claimability;
- authorize ECU minting;
- authorize ILC settlement or withdrawal runtime;
- generate release keys;
- produce release envelopes;
- mutate signed Genesis v0.1;
- regenerate Genesis Atlas v0.2+;
- mutate immutable diagnostic anchors;
- authorize v0.2 signing.

---

## 7. Carry-Forward Tokens

```text
window_1249_1256_candidate_phase_grouping_recorded_after_phase_1248
window_1249_1256_not_open_until_sequence_lock
gap_14_adapter_extraction_and_package_ci_gate_should_continue_before_public_rc_claim
gap_13_public_claimability_runtime_should_start_before_final_public_rc_claim
transport_principal_identity_required_before_public_p2p
atlas_g_004_high_authority_gap_closure_required
atlas_g_005_import_dependency_graph_bridge_required
tla_refinement_notes_pre_rc_window_1241_plus_candidate
allowlist_export_procedure_window_1241_plus_candidate
```
