# ILC Antigravity Context Capsule v5.44

**Date:** 2026-05-04
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.43.md`
**Produced:** Phase 1189, Window 1183-1190
**Frontier:** Window 1183-1190 in progress; Phase 1189 complete; Phase 1190 closure gate pending

`capsule_v5_44_supersedes_v5_43`
`window_1183_1190_sequence_lock_committed`
`cdl_085_ratified_phase_1185`
`v0_2_signing_ceremony_deferred_pending_signing_authorization`
`sim_spectral_05_gossip_slice_pass`
`sim_spectral_05_three_slice_observer_framework_complete`
`cdl_001_genesis_blocker_scoping_committed_phase_1188`

---

## 1. Current State

Window 1183-1190 is complete through Phase 1189. Phase 1190 remains pending and is
SENSITIVE.

Current coherence report:

- `docs/specs/ilc_integration_coherence_report_1189_v0.1.md`

Current active window lock and guidance:

- `docs/specs/ilc_phase_1183_1190_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1183_1190_candidate_phase_grouping_v0.1.md`

---

## 2. Constitutional Frontier

`CDL-085` is ratified:

- Opening phase: 1172
- Prelock phase: 1177
- Ratification phase: 1185
- Opening token: `cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass`
- Prelock token: `cdl_085_prelock_committed_phase_1177`
- Ratification token: `cdl_085_ratified_phase_1185`
- Ratified bound: `EDGE_MINT_PHI_BOUND = Decimal("0.60")`
- Runtime dependency: `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`

`CDL-084` remains active:

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `PROVENANCE_MAX_DEPTH = 3`
- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`

CDL-086 remains the next fresh CDL number.

---

## 3. Runtime Frontier

Runtime version:

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1185.v0.6"
```

Active attribution constants:

```python
PROVENANCE_DECAY_ALPHA = Decimal("0.45")
EDGE_MINT_PHI_BOUND = Decimal("0.60")
```

No settlement, QATPS, slashing, wallet, or gossip transport rule beyond the ratified
phi-bound activation is changed by this capsule.

---

## 4. SIM-SPECTRAL-05 Frontier

Previously closed:

| Track | Verdict | Key result |
|-------|---------|------------|
| Track A | `track_a_pass` | `lambda_max` 3.180229σ, `spectral_gap` 2.775223σ, `degree_gini` 2.726353σ vs `synthetic_sybil_cluster` |
| Track B | `track_b_pass` | S1 convergence 0.85, S3 Sybil convergence 0.25, separation 0.60 |
| Overall | `sim_spectral_05_gate_pass` | CDL-085 opening supported |

Observer-slice outcomes:

| Slice | Verdict | Status |
|-------|---------|--------|
| runtime-binding | `sim_spectral_05_runtime_binding_slice_pass` | resolved |
| economic-flow | `sim_spectral_05_economic_flow_slice_pass` | resolved |
| gossip | `sim_spectral_05_gossip_slice_pass` | resolved |

Completion token:

`sim_spectral_05_three_slice_observer_framework_complete`

---

## 5. ADR Governance Frontier

Accepted before this capsule:

| ADR | Title | Token |
|-----|-------|-------|
| ADR-0037 | Genesis Canonical Lineage Contract | `adr_0037_accepted_phase_1173` |
| ADR-0036 | Operational Release Key Genesis Binding | `adr_0036_accepted_phase_1173` |

ADR-0037 governs canonical lineage, equivalence, merge policy, PEC, multi-slice Genesis
encrustation, and fork boundary. ADR-0036 governs the operational release-key mechanism,
bounded by ADR-0037.

---

## 6. Genesis Atlas Frontier

Signed Genesis v0.1 remains canonical and unchanged:

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

Strictly immutable diagnostic:

- `out/genesis_compile_coverage_diagnostic_v0.1.json`
- Expected SHA-256:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Unsigned v0.2 candidate:

- Artifact: `out/genesis_core_star_map_v0.2_candidate.json`
- Nodes: 41
- Edges: 73
- Status: unsigned candidate
- Signing outcome this window: deferred pending signing authorization
- Token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

## 7. Public Launch / CDL-001 Scoping

Phase 1188 scoped the public-launch `genesis_blocker` lane:

- Scoping artifact: `docs/specs/ilc_cdl_001_genesis_blocker_scoping_1188_v0.1.md`
- Token: `cdl_001_genesis_blocker_scoping_committed_phase_1188`

Important finding: the current CDL register already contains historical ratified
`CDL-001` for canonical signer lineage definition. The public-launch blocker label must
be reconciled before any future opening.

---

## 8. Active Carry-Forward Obligations

- Phase 1190 closure gate — requires explicit `GO Phase 1190`
- v0.2 signing ceremony — deferred pending explicit signing authorization
- Public-launch blocker opening — requires identifier/scope reconciliation and counsel-track routing
- Tier-3 runtime linkage — implementation lane remains
- Truth-primitive permanence community ratification — carry-forward
- Contributor agreement, license, trademark — counsel track
- Canon bundle signing repair — tooling debt

---

## 9. Verification

Window 1183-1190 is verified through Phase 1189:

- Phase 1183 sequence-lock tests passed
- Phase 1184 prelock-hardening tests passed before ratification
- Phase 1185 CDL/runtime ratification tests passed
- Sensitive runtime coding taboo test passed
- Phase 1187 gossip slice tests passed
- Phase 1188 scoping tests passed
- Phase 1189 coherence/capsule tests passed

Phase 1190 closure gate remains pending and requires explicit GO.

`capsule_v5_44_supersedes_v5_43`
