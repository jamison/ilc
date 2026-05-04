# ILC Antigravity Context Capsule v5.40

**Date:** 2026-05-04
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.39.md`
**Frontier:** Window 1148-1156 CLOSED via Phase 1155

`capsule_v5_40_supersedes_v5_39`
`window_1148_1156_closed_phase_1155`
`atlas_tier2_v0_2_candidate_36_nodes_unsigned`
`sim_spectral_04_program_committed_phase_1152`

---

## 1. Current State

Window 1148-1156 is closed at Phase 1155. Phase 1156 was a conditional signing tail slot
and did not execute.

The current closure handoff is:

- `docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md`

The current coherence report is:

- `docs/specs/ilc_integration_coherence_report_1155_v0.1.md`

---

## 2. Constitutional Frontier

`CDL-084` remains the ratified attribution frontier.

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`

`CDL-085` remains unopened and SIM-gated. Phase 1146 declared:

`CDL-085 recommendation: DEFER`

No CDL mutation occurred in Window 1148-1156.

---

## 3. Runtime Frontier

Runtime semantics are unchanged.

- Runtime version: `epoch_attribution_settle_runtime_1129_fix1.v0.5`
- No settlement rule changed.
- No QATPS rule changed.
- No slashing rule changed.

---

## 4. Genesis Atlas Frontier

Signed v0.1 remains the canonical signed Genesis Atlas artifact.

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- Signature file: `out/genesis_signing_root_envelope_v0.1.sig`
- Signed diagnostic hash remains unchanged from Phase 1142s.

Unsigned v0.2 candidate exists:

- Candidate: `out/genesis_core_star_map_v0.2_candidate.json`
- Nodes: 36
- Edges: 63
- Added accepted ADR nodes: ADR-0019, ADR-0026, ADR-0028, ADR-0031
- New nodes: `signature_status=pending_signing`
- Status: unsigned candidate only

Phase 1156 is deferred and not authorized. The v0.2 candidate remains unsigned until a
release key or explicit Genesis exceptional signing authorization exists.

---

## 5. GENESIS-COMPILE Frontier

Checkpoint #2 passes the Tier-2 authority gate:

- Diagnostic: `out/genesis_compile_coverage_diagnostic_v0.2_candidate.json`
- Authority-traceable core nodes: `36/36`
- Authority ratio: `1.000000`
- Checkpoint token: `genesis_compile_checkpoint_2_pass`

The legacy tool verdict remains `FAIL_CORE_INADEQUATE` because basis-reachability and
source-explainability are not complete. That verdict is expected at this stage and is not
the checkpoint #2 authority gate criterion.

---

## 6. SIM-SPECTRAL Frontier

SIM-SPECTRAL-04 program specification is committed:

- Audit: `out/genesis_32_node_composability_audit_v0.1.json`
- Program: `docs/sims/sim_spectral_04/program.md`
- Token: `sim_spectral_04_program_committed_phase_1152`

No SIM-SPECTRAL-04 run occurred in this window.

CDL-085 reconsideration remains blocked until future SIM-SPECTRAL-04 execution produces
positive evidence under matched-size S3/G2 controls.

---

## 7. Active Carry-Forward Obligations

Window 1157+ should begin from the Phase 1155 handoff and this capsule.

Carry-forward obligations:

- `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage`
- ADR acceptance review batch for ADR-0012, ADR-0022, ADR-0023, and ADR-0008
- formal Genesis Canonical Lineage Contract ADR
- operational release-key ADR and Genesis-bound release key registration
- truth-primitive permanence community ratification before Genesis sunset
- contributor agreement, license strategy, and trademark/identity counsel track
- canon bundle signing failure repair
- SIM-SPECTRAL-04 implementation and run planning
- v0.2 candidate signing only after release key or explicit Genesis exceptional signing

---

## 8. Verification

Phase 1155 closure gate passed under:

`ILC_PHASE_1155_GATE_SELFTEST=1`

Targeted closure verification covered the Window 1148-1156 sequence lock, ADR status
normalization, unsigned v0.2 candidate shape, signed v0.1 immutability, checkpoint #2
authority traceability, composability audit, SIM-SPECTRAL-04 program spec, Canonical
Lineage Contract planning spec, obligations synthesis, runtime invariants, capsule,
coherence report, handoff, planning index, roadmap postscript, and STATUS frontier.

`capsule_v5_40_supersedes_v5_39`
