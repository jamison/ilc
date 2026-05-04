# ILC Antigravity Context Capsule v5.42

**Date:** 2026-05-04
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.41.md`
**Frontier:** Window 1166-1175 in progress; Phase 1174 complete; Phase 1175 closure gate pending

`capsule_v5_42_supersedes_v5_41`
`sim_spectral_05_gate_pass`
`cdl_085_open_phase_1172`
`adr_0037_accepted_phase_1173`
`adr_0036_accepted_phase_1173`

---

## 1. Current State

Window 1166-1175 is complete through Phase 1174. Phase 1175 remains pending and is
SENSITIVE.

Current coherence report:

- `docs/specs/ilc_integration_coherence_report_1174_v0.1.md`

Current active window lock and guidance:

- `docs/specs/ilc_phase_1166_1175_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1166_1175_candidate_phase_grouping_v0.1.md`

---

## 2. Constitutional Frontier

`CDL-084` remains the ratified attribution frontier:

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- Runtime dependency: `CDL_084_DEPENDENCY`
- Runtime version remains `epoch_attribution_settle_runtime_1129_fix1.v0.5`

`CDL-085` is now open:

- Opening phase: 1172
- Opening artifact: `docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md`
- Token: `cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass`
- Scope: Werner φ-bound provenance equivalence limit
- Status: opening only, not ratified
- `EDGE_MINT_PHI_BOUND`: unset pending prelock and later ratification

No runtime semantic mutation occurred with CDL-085 opening.

---

## 3. SIM-SPECTRAL-05 Frontier

SIM-SPECTRAL-05 passed.

| Track | Verdict | Key result |
|-------|---------|------------|
| Track A | `track_a_pass` | `lambda_max` 3.180229σ, `spectral_gap` 2.775223σ, `degree_gini` 2.726353σ vs `synthetic_sybil_cluster` |
| Track B | `track_b_pass` | S1 convergence 0.85, S3 Sybil convergence 0.25, separation 0.60 |
| Overall | `sim_spectral_05_gate_pass` | CDL-085 reconsideration supported and Phase 1172 executed after human GO |

Artifacts:

- `out/sim_spectral_05_track_a_calibration_summary.json`
- `out/genesis_branchial_claim_projection_v0.1.json`
- `out/sim_spectral_05_track_b_run_summary.json`
- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md`

Deferred observer slices:

- `sim_spectral_05_runtime_binding_slice_deferred_window_1176`
- `sim_spectral_05_economic_flow_slice_deferred_window_1176`
- `sim_spectral_05_gossip_slice_deferred_window_1176`

---

## 4. ADR Governance Frontier

Accepted in Window 1166-1175:

| ADR | Title | Token |
|-----|-------|-------|
| ADR-0037 | Genesis Canonical Lineage Contract | `adr_0037_accepted_phase_1173` |
| ADR-0036 | Operational Release Key Genesis Binding | `adr_0036_accepted_phase_1173` |

ADR-0037 now governs canonical lineage, equivalence, merge policy, PEC, multi-slice
Genesis encrustation, and fork boundary.

ADR-0036 now governs the operational release-key mechanism. Its release authority is
bounded by ADR-0037's version equivalence and fork-boundary rules.

---

## 5. Genesis Atlas Frontier

Signed v0.1 remains canonical and unchanged:

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- `out/genesis_compile_coverage_diagnostic_v0.1.json`: unchanged, not regenerated

Unsigned v0.2 candidate:

- Artifact: `out/genesis_core_star_map_v0.2_candidate.json`
- Nodes: 41
- Edges: 73
- Status: unsigned candidate

ADR-0036 and ADR-0037 acceptance complete the governance preconditions identified for
future v0.2 signing. The signing ceremony itself remains deferred to Window 1176+ and
requires explicit signing authorization.

---

## 6. Runtime Frontier

Runtime semantics are unchanged:

- Runtime version: `epoch_attribution_settle_runtime_1129_fix1.v0.5`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- No settlement rule changed
- No QATPS rule changed
- No slashing rule changed
- No release key was generated
- No v0.2 artifact was signed

---

## 7. Active Carry-Forward Obligations

### CDL-085

- `cdl_085_prelock_required_after_opening_phase_1172`
- `edge_mint_phi_bound_value_unset_pending_cdl_085_prelock`

CDL-085 requires a future prelock before ratification. The prelock must resolve bound
object, bound expression, φ interpretation, runtime relation, and economic-flow dependency.

### Deferred Observer Slices

- `sim_spectral_05_runtime_binding_slice_deferred_window_1176`
- `sim_spectral_05_economic_flow_slice_deferred_window_1176`
- `sim_spectral_05_gossip_slice_deferred_window_1176`

### Genesis / Launch

- v0.2 signing ceremony - deferred to Window 1176+; ADR preconditions satisfied,
  explicit signing authorization still required
- Tier-3 runtime linkage - implementation lane remains
- Truth-primitive permanence community ratification - carry-forward
- Contributor agreement, license, trademark - counsel track
- Canon bundle signing repair - tooling debt

---

## 8. Verification

Window 1166-1175 is verified through Phase 1174:

- Phase 1169 Track A tests passed
- Phase 1170 branchial projection tests passed
- Phase 1171 disposition tests passed
- Phase 1172 CDL-085 opening tests passed
- Phase 1173 ADR acceptance tests passed

Phase 1175 closure gate remains pending and requires explicit GO.

`capsule_v5_42_supersedes_v5_41`
