# ILC Antigravity Context Capsule v5.39

**Date:** 2026-05-04
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.38.md`
**Frontier:** Window 1139-1147 CLOSED via Phase 1147

`capsule_v5_39_supersedes_v5_38`
`window_1139_1147_three_lane_complete`
`run02_fix2_corrected_baseline_committed`
`sim_spectral_03_disposition_phase_1146`

---

## 1. Current State

Window 1139-1147 is closed. The window delivered three lanes:

- corrected SIM-SPECTRAL-02 Run 02 Fix2 baseline;
- signed Genesis Atlas Tier-1 32-node star map v0.1;
- SIM-SPECTRAL-03 Run 01, topology calibration audit, and CDL-085 DEFER disposition.

The current closure handoff is:

- `docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md`

The current coherence report is:

- `docs/specs/ilc_integration_coherence_report_1147_v0.1.md`

---

## 2. Constitutional Frontier

`CDL-084` remains the ratified attribution frontier.

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`

`CDL-085` remains unopened and SIM-gated. Phase 1146 declares:

`CDL-085 recommendation: DEFER`

No CDL mutation occurred in Window 1139-1147.

---

## 3. Runtime Frontier

Runtime semantics are unchanged.

- Runtime version: `epoch_attribution_settle_runtime_1129_fix1.v0.5`
- No settlement rule changed.
- No QATPS rule changed.
- No slashing rule changed.

Audit nuance: commit `102ed6f2` added a comment-only audit annotation to
`ilc_core/analysis/embedding_pipeline.py`. This is not a runtime semantic mutation.

---

## 4. Genesis Atlas Frontier

The signed Genesis star map v0.1 is now the Tier-1 authority baseline.

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32
- Edges: 55
- All nodes: `genesis_attested=true`
- All nodes: `signature_status=signed`
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- Signature file: `out/genesis_signing_root_envelope_v0.1.sig`
- Checkpoint #1: `genesis_compile_checkpoint_1_pass`
- Signed diagnostic immutability: `out/genesis_compile_coverage_diagnostic_v0.1.json`
  is covered by the Phase 1142s toolchain manifest and remains at the signed v0.1 hash.

Human-facing language: 32/32 nodes are authority-grounded and included in the signed
package. The 31/32 authority-traceability traversal metric excludes Node 0 by traversal
convention only.

---

## 5. SIM-SPECTRAL Frontier

Corrected Run 02 Fix2 is the operative baseline:

- `out/sim_spectral_02_run02_fix2_summary.json`
- entry count: 333
- S3/S1 threshold: `0.6416011282246747`
- G2/S1 threshold: `0.8640456434014127`

SIM-SPECTRAL-03 result:

- S1 slope: `0.21355627860399237`
- S3/S1: `1.6736470076736112`
- G2/S1: `2.2539040876901315`
- Phase 1145a passing topology-overlay variants: `0`

Named finding:

`raw_authority_graph_is_not_the_right_spectral_work_graph`

Next simulation obligation:

`sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration`

---

## 6. Active Carry-Forward Obligations

Phase 1146 and Phase 1147 carry forward:

- `sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration`
- `genesis_32_node_composability_audit_required`
- `matched_size_controls_required_for_future_spectral_sims`
- `genesis_canonical_lineage_contract_required_before_public_rc`
- `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`
- `public_rc_envelope_hash_transition_policy_required`
- `contributor_agreement_required_before_public_repo`
- counsel review for mixed license / contributor / trademark strategy before public repo
- canon bundle signing failures carried forward as tooling debt

---

## 7. Next Routing

Window 1148+ should begin from the Phase 1147 handoff, not from memory.

Recommended lanes:

- Atlas Tier-2 governance node promotion and GENESIS-COMPILE checkpoint #2.
- Genesis 32-node composability audit.
- SIM-SPECTRAL-04 claim-composition projection program spec.
- Genesis Canonical Lineage Contract draft.
- Parallel counsel track for license, contributor agreement, and trademark/identity
  policy.

No public RC, CDL-085 opening, or runtime semantic mutation is pre-authorized by this
capsule.

---

## 8. Verification

Phase 1147 closure gate passed under:

`ILC_PHASE_1147_GATE_SELFTEST=1`

Targeted closure verification covered the corrected baseline, signed Genesis star map,
SIM-SPECTRAL-03 disposition, CDL/runtime invariants, capsule/coherence/handoff routing,
planning index, and roadmap postscript.

`capsule_v5_39_supersedes_v5_38`
