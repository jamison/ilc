# ILC Integration Coherence Report 1174 v0.1

Status: pass
Phase: 1174
Date: 2026-05-04
Window: 1166-1175

`coherence_report_1174_verdict=pass`

---

## 1. Window Identity

Window 1166-1175 is coherent through Phase 1174. Phase 1175 remains the pending
SENSITIVE closure gate.

Executed phases:

| Phase | Outcome |
|-------|---------|
| 1166 | Window sequence lock committed |
| 1167 | ADR-0037 Genesis Canonical Lineage Contract drafted as Proposed |
| 1168 | SIM-SPECTRAL-05 program spec and multi-slice observer framework committed |
| 1169 | SIM-SPECTRAL-05 Track A completed with `track_a_pass` |
| 1170 | Branchial claim-state projection built |
| 1171 | Track B completed and overall `sim_spectral_05_gate_pass` emitted |
| 1172 | CDL-085 opened after explicit human `GO Phase 1172` |
| 1173 | ADR-0037 and ADR-0036 accepted |
| 1174 | Coherence report and capsule v5.42 |

No phase in the executed range was skipped. Phase 1175 has not executed.

---

## 2. SIM-SPECTRAL-05 Outcome

| Item | Value |
|------|-------|
| Track A verdict | `track_a_pass` |
| Track B verdict | `track_b_pass` |
| Overall gate verdict | `sim_spectral_05_gate_pass` |
| Observer slices tested | claim-composition, provenance, authority (partial) |
| Provenance equivalence criterion | ADR-0037 §3.2 |

Track A discriminants against `synthetic_sybil_cluster`:

| Discriminant | S1 value | S3 mean | z-score vs Sybil | Verdict |
|--------------|----------|---------|------------------|---------|
| `lambda_max` | 8.402868203511 | 5.755398383452 | 3.180229 | `discriminates_against_sybil` |
| `spectral_gap` | 8.052720429411 | 5.742505452315 | 2.775223 | `discriminates_against_sybil` |
| `degree_gini` | 0.230190629306 | 0.109217159731 | 2.726353 | `discriminates_against_sybil` |

Track B convergence:

| Topology | Mean convergence rate | Criterion |
|----------|-----------------------|-----------|
| S1 legitimate branchial paths | 0.85 | `>= 0.75` |
| S3 branchial Sybil paths | 0.25 | `<= 0.50` |
| Separation | 0.60 | `>= 0.25` |

Deferred observer slices:

- `sim_spectral_05_runtime_binding_slice_deferred_window_1176`
- `sim_spectral_05_economic_flow_slice_deferred_window_1176`
- `sim_spectral_05_gossip_slice_deferred_window_1176`

---

## 3. CDL-085 State

CDL-085 opened in Phase 1172 after both gate conditions were satisfied:

- Phase 1171 emitted `sim_spectral_05_gate_pass`
- Human issued explicit `GO Phase 1172`

Current token:

`cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass`

CDL-085 status is `open`. This is an opening only. No φ value, runtime constant,
economic-flow activation, or ratification occurred. `EDGE_MINT_PHI_BOUND` remains
unset pending prelock and later ratification.

---

## 4. ADR Outcomes

| ADR | Outcome | Token |
|-----|---------|-------|
| ADR-0037 Genesis Canonical Lineage Contract | Accepted | `adr_0037_accepted_phase_1173` |
| ADR-0036 Operational Release Key Genesis Binding | Accepted | `adr_0036_accepted_phase_1173` |

ADR-0037 now supplies the accepted lineage, equivalence, merge policy, PEC, multi-slice
encrustation, and fork-boundary contract. ADR-0036 now supplies the accepted operational
release-key mechanism, explicitly bounded by ADR-0037.

---

## 5. Genesis Atlas State

Signed v0.1 remains unchanged:

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

`out/genesis_compile_coverage_diagnostic_v0.1.json` was not regenerated. Its SHA-256
remains:

`5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Unsigned v0.2 candidate remains:

- Artifact: `out/genesis_core_star_map_v0.2_candidate.json`
- Nodes: 41
- Edges: 73
- Status: unsigned candidate

No new ADR acceptance in Phase 1173 added nodes to v0.2. ADR-0036 and ADR-0037 acceptance
complete the governance prerequisites for a future signing ceremony, but v0.2 signing
itself is deferred to Window 1176+ and still requires explicit signing authorization.

---

## 6. Runtime State

Runtime semantics are unchanged:

- `epoch_attribution_settle_runtime_1129_fix1.v0.5`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- No settlement rule changed
- No QATPS rule changed
- No slashing rule changed

The only CDL mutation in this window was the Phase 1172 CDL-085 opening. There was no
runtime mutation.

---

## 7. Carry-Forward into Window 1176+

Closed this window:

- `sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required`
- `sim_spectral_05_branchial_claim_state_projection_required`
- `sim_spectral_05_multi_slice_observer_convergence_framework_required`
- `genesis_multi_slice_encrustation_model_required_for_lineage_contract_adr`
- `genesis_equivalence_and_merge_policy_required_for_lineage_contract_adr`
- `popperian_equivalence_criterion_required_as_merge_gate_in_lineage_contract_adr`
- `genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036`

Remaining carry-forwards:

| Obligation | Status |
|------------|--------|
| `cdl_085_prelock_required_after_opening_phase_1172` | New, required before any CDL-085 ratification |
| `edge_mint_phi_bound_value_unset_pending_cdl_085_prelock` | New, no runtime constant locked |
| `sim_spectral_05_runtime_binding_slice_deferred_window_1176` | Deferred observer slice |
| `sim_spectral_05_economic_flow_slice_deferred_window_1176` | Deferred observer slice |
| `sim_spectral_05_gossip_slice_deferred_window_1176` | Deferred observer slice |
| v0.2 signing ceremony | Deferred to Window 1176+; ADR preconditions now satisfied, signing authorization still required |
| Tier-3 runtime linkage | Still implementation lane |
| Truth-primitive permanence community ratification | Carry-forward |
| Contributor agreement, license, trademark | Counsel track |
| Canon bundle signing repair | Tooling debt |

---

## 8. Verification

Focused checks:

- Phase 1169 Track A tests: passed
- Phase 1170 branchial projection tests: passed
- Phase 1171 disposition tests: passed
- Phase 1172 CDL-085 opening tests: passed
- Phase 1173 ADR acceptance tests: passed

Phase 1174 adds this coherence report and capsule v5.42. Signed v0.1 artifacts remain
unchanged. Runtime semantics remain unchanged.

`coherence_report_1174_verdict=pass`
