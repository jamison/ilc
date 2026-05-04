# ILC Antigravity Context Capsule v5.41

**Date:** 2026-05-04
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.40.md`
**Frontier:** Window 1156-1165, Phase 1164 complete (Phase 1165 closure gate pending)

`capsule_v5_41_supersedes_v5_40`
`window_1156_1165_phases_1156_1164_complete`
`sim_spectral_04_gate_fail_phase_1162`
`atlas_tier2_v0_2_candidate_41_nodes_unsigned`

---

## 1. Current State

Window 1156-1165 phases 1156–1164 are complete. Phase 1165 (closure gate, SENSITIVE) is
pending human GO. Phase 1163 (CDL-085 opening) did not execute — `sim_spectral_04_gate_fail`
was produced at Phase 1162.

Current closure handoff (from prior window):
- `docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md`

Current coherence report:
- `docs/specs/ilc_integration_coherence_report_1164_v0.1.md`

---

## 2. Constitutional Frontier

`CDL-084` remains the ratified attribution frontier.

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`

`CDL-085` remains **unopened and SIM-gated**. Phase 1162 gate verdict:

```
sim_spectral_04_gate_fail — CDL-085 reconsideration not supported
cdl_085_sim_gated_pending_sybil_discrimination_resolution
```

New carry-forward (Phase 1164 structural perturbation research):
```
sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required
```

No CDL mutation occurred in Window 1156-1165.

---

## 3. Runtime Frontier

Runtime semantics are unchanged.

- Runtime version: `epoch_attribution_settle_runtime_1129_fix1.v0.5`
- No settlement rule changed.
- No QATPS rule changed.
- No slashing rule changed.

---

## 4. Genesis Atlas Frontier

Signed v0.1 remains the canonical signed Genesis Atlas artifact — **untouched**.

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32, Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- `out/genesis_compile_coverage_diagnostic_v0.1.json`: immutable, not regenerated

Unsigned v0.2 candidate advanced from 36 → **41 nodes** (73 edges) in this window:

- Candidate: `out/genesis_core_star_map_v0.2_candidate.json`
- Nodes: **41**, Edges: **73**
- ADRs added in Window 1156-1165:
  - ADR-0020 (Knowledge-Node-First Design Principle) — Phase 1157
  - ADR-0012 (ECU-ILC-Graph Coupling and Anti-Reflexivity) — Phase 1158
  - ADR-0022 (Local-First Private Use and Publication-Bound Economics) — Phase 1158
  - ADR-0023 (Multi-Layer Quality Signal Architecture, scoped) — Phase 1158
  - ADR-0008 (Node Usefulness vs Governance Weight and Genesis Dilution) — Phase 1158
- Status: unsigned candidate only
- Signing ceremony: deferred to Window 1166+ (requires ADR-0036 acceptance)

---

## 5. ADR Governance Frontier

**Accepted in Window 1156-1165:**

| ADR | Title | Acceptance token |
|-----|-------|-----------------|
| ADR-0020 | Knowledge-Node-First Design Principle | `adr_0020_accepted_phase_1157` |
| ADR-0012 | ECU-ILC-Graph Coupling and Anti-Reflexivity Contract | `adr_0012_accepted_phase_1158` |
| ADR-0022 | Local-First Private Use and Publication-Bound Economics | `adr_0022_accepted_phase_1158` |
| ADR-0023 | Multi-Layer Quality Signal Architecture (scoped) | `adr_0023_accepted_phase_1158_scoped_quality_signal_architecture` |
| ADR-0008 | Node Usefulness vs Governance Weight and Genesis Dilution | `adr_0008_accepted_phase_1158` |

ADR-0023 scoped acceptance: limited to evidence-backed multi-layer quality-signal
architecture. Does not accept multi-hop centrality, aesthetic re-evaluation, or
long-horizon tuning claims.

**Proposed (not yet accepted):**

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0036 | Operational Release Key Genesis Binding | Proposed — acceptance Window 1166+ |

ADR-0036 scope: operational release-key mechanism only. The broader Genesis Canonical
Lineage Contract requires its own ADR:
`genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036`

---

## 6. SIM-SPECTRAL Frontier

**SIM-SPECTRAL-04 complete — gate fail.**

- Projection: `out/genesis_claim_composition_projection_v0.1.json` (56 vertices, 125 edges)
- Run summary: `out/sim_spectral_04_run01_summary.json`
- Disposition: `docs/sims/sim_spectral_04/disposition_1162_v0.1.md`
- S1 slope improved: 0.214 (SIM-SPECTRAL-03 raw authority) → 0.345 (claim-composition)
- G2/S1 passes all seeds ✓
- S3/S1 fails all seeds ✗ (min 0.781, max 0.808, threshold 0.642)

**Structural perturbation research (Phase 1164, exploratory):**

- Research doc: `docs/research/sim_spectral_04_structural_perturbation_research_1164_v0.1.md`
- Tools: `tools/sim_spectral_04_auto_research.py`,
  `tools/sim_spectral_04_three_path_research.py`
- Key finding: λ_max and spectral_gap are strong discriminants against random graphs
  (9.8σ and 8.9σ) but require testing against the committed `synthetic_sybil_cluster`
  S3 topology before promotion as gate alternatives
- Proximate cause of gate failure: λ₂-based `structural_impedance` is inactive because
  both S1 and S3 clear `THETA_FLOOR`, not simply that λ₂ is the wrong eigenvalue

**SIM-SPECTRAL-05 obligation:**
`sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required`

SIM-SPECTRAL-05 must test: λ₂ floor sweep, λ_max/spectral-gap discriminants, and
degree-inequality/hub-dominance metrics — all against the actual `synthetic_sybil_cluster`,
not only random graphs.

---

## 7. Active Carry-Forward Obligations

Window 1166+ entry criteria:

- `cdl_085_sim_gated_pending_sybil_discrimination_resolution` — CDL-085 blocked until
  SIM-SPECTRAL-05 produces positive discrimination evidence
- `sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required`
- v0.2 signing ceremony — blocked on ADR-0036 acceptance
- ADR-0036 acceptance review — Window 1166+
- Genesis Canonical Lineage Contract ADR — Window 1166+, separate from ADR-0036
- Tier-3 runtime linkage — governance prerequisite met (ADR-0020 accepted); runtime
  implementation is a separate lane
- Truth-primitive permanence community ratification — carry-forward
- Contributor agreement, license, trademark — counsel track
- Canon bundle signing repair — tooling debt carry-forward

---

## 8. Verification

Phases 1156–1162 committed at `d0a02596` (57 tests passed).
Phase 1164 adds: coherence report, capsule v5.41, research doc, research tools.
Signed v0.1 artifacts confirmed unchanged throughout window.
Runtime semantics confirmed unchanged throughout window.
Phase 1165 closure gate pending.

`capsule_v5_41_supersedes_v5_40`
