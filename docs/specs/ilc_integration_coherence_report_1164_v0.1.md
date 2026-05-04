# ILC Integration Coherence Report 1164 v0.1

Status: pass
Phase: 1164
Date: 2026-05-04
Window: 1156-1165

`coherence_report_1164_verdict=pass`

---

## 1. Verdict

Window 1156-1165 is coherent through Phase 1164. All firm NON-SENSITIVE phases (1156–1162)
are complete. Phase 1163 (CDL-085 opening) did not execute — the gate condition
`sim_spectral_04_gate_fail` was reached at Phase 1162, so no CDL mutation occurred. Phase
1165 (closure gate) is pending human GO.

The window advanced the ADR acceptance frontier, completed SIM-SPECTRAL-04, extended
structural perturbation research into the gate failure, and carried both CDL-085 diagnosis
tokens forward as carry-forward obligations for Window 1166+.

---

## 2. Constitutional and Runtime Coherence

`CDL-084` remains the ratified attribution frontier.

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`
- Runtime frontier: `epoch_attribution_settle_runtime_1129_fix1.v0.5`

`CDL-085` remains unopened and SIM-gated. Phase 1162 produced:
```
sim_spectral_04_gate_fail — CDL-085 reconsideration not supported
cdl_085_sim_gated_pending_sybil_discrimination_resolution
```

No CDL mutation occurred in Window 1156-1165. No runtime semantic mutation occurred.

---

## 3. ADR Acceptance Coherence

All five ADR acceptance reviews completed. Outcomes:

| ADR | Phase | Outcome | Token |
|-----|-------|---------|-------|
| ADR-0020 | 1157 | Accepted | `adr_0020_accepted_phase_1157` |
| ADR-0012 | 1158 | Accepted | `adr_0012_accepted_phase_1158` |
| ADR-0022 | 1158 | Accepted | `adr_0022_accepted_phase_1158` |
| ADR-0023 | 1158 | Scoped-accepted | `adr_0023_accepted_phase_1158_scoped_quality_signal_architecture` |
| ADR-0008 | 1158 | Accepted | `adr_0008_accepted_phase_1158` |

All five ADRs accepted in this window. ADR-0023 acceptance is scoped to the evidence-backed
multi-layer quality-signal architecture only; it does not accept future multi-hop centrality,
aesthetic re-evaluation, or long-horizon tuning claims.

ADR-0020 acceptance satisfies:
`adr_0020_acceptance_review_priority_before_tier3_embedding_linkage`
at the governance level. Tier-3 implementation remains a separate lane.

---

## 4. Genesis Atlas Coherence

Signed v0.1 artifacts are unchanged.

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32, Edges: 55
- Root envelope hash: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- `out/genesis_compile_coverage_diagnostic_v0.1.json`: not regenerated (immutable)

Unsigned v0.2 candidate grew from 36 → 41 nodes across Phases 1157–1158:

- Candidate: `out/genesis_core_star_map_v0.2_candidate.json`
- Nodes: 41, Edges: 73
- All five newly-accepted ADR nodes added to curated seed
- Status: unsigned candidate only

---

## 5. SIM-SPECTRAL-04 Coherence

Phase 1160: `claim_composition_projection_built_phase_1160`
- Projection: `out/genesis_claim_composition_projection_v0.1.json`
- 56 vertices, 125 edges, hash `fc1496ea12319338d10db0e63f78087b3a72c46a31507d09b35234c79a45a2ab`

Phase 1161: `sim_spectral_04_run01_committed_phase_1161`
- Run summary: `out/sim_spectral_04_run01_summary.json`
- S1 mean slope 0.3453 (improved over SIM-SPECTRAL-03 baseline 0.2136)

Phase 1162: `sim_spectral_04_gate_fail`
- Matched G2/S1 passes all seeds ✓
- Matched S3/S1 fails all seeds ✗ (min 0.7805, max 0.8082, threshold 0.6416)
- Diagnosis: `cdl_085_sim_gated_pending_sybil_discrimination_resolution`

---

## 6. Structural Perturbation Research Coherence

Following the Phase 1162 gate fail, structural perturbation research was conducted during
Window 1156-1165 and historicized as a carry-forward research artifact:

`docs/research/sim_spectral_04_structural_perturbation_research_1164_v0.1.md`

Key findings (exploratory, not canonical gate evidence):
- No node addition or subtraction passes the gate; baseline is the structural optimum
- Community partitioning (bipartite) reduces S3/S1 from 0.864 to 0.765 — directional but
  insufficient
- Threshold recalibration is not a viable path (any threshold that passes S1 admits 75%+
  of random controls)
- λ_max and spectral_gap are strong discriminants against random graphs (9.8σ and 8.9σ)
  but have not yet been tested against the committed `synthetic_sybil_cluster` S3 topology
- λ₂-based structural impedance is not discriminating because both S1 and S3 clear
  `THETA_FLOOR`, making the impedance term 0 for both — a calibration issue, not simply
  the wrong eigenvalue

New carry-forward obligation added:
`sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required`

---

## 7. ADR-0036 Coherence

Phase 1159: `adr_0036_release_key_draft_committed_phase_1159`
- `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` — Status: Proposed
- Scope correctly bounded to operational release-key mechanism only
- Genesis Canonical Lineage Contract explicitly excluded:
  `genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036`

---

## 8. Carry-Forward Obligations into Window 1166+

| Obligation | Status |
|-----------|--------|
| `cdl_085_sim_gated_pending_sybil_discrimination_resolution` | Unchanged from Phase 1162 |
| `sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required` | New — Phase 1164 |
| v0.2 signing ceremony | Deferred — requires ADR-0036 acceptance |
| ADR-0036 acceptance review | Deferred to Window 1166+ |
| Genesis Canonical Lineage Contract ADR | Separate from ADR-0036; Window 1166+ |
| Tier-3 runtime linkage | ADR-0020 now accepted at governance level; runtime lane separate |
| Truth-primitive permanence community ratification | Carry-forward |
| Contributor agreement, license, trademark | Counsel track |
| Canon bundle signing repair | Tooling debt; carry-forward |

---

## 9. Verification

Phases 1156–1162 verified under `d0a02596` (57 tests passed).
Structural perturbation research tools verified manually (15-variant sweep + 3-path research).
Signed v0.1 artifacts confirmed unchanged.
Runtime chain confirmed unchanged.
