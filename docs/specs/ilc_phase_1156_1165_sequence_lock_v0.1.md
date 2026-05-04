# ILC Phase 1156-1165 Sequence Lock v0.1

Status: sequence lock
Phase: 1156
Date: 2026-05-04

`window_1156_1165_sequence_lock_committed`
`phase_1156_deferred_not_authorized_inherited_from_window_1148_1156`
`cdl_085_no_canonical_opening_spec_exists_prior_to_phase_1163`

---

## 1. Purpose

This sequence lock opens Window 1156-1165 after Window 1148-1156 closed at
Phase 1155. The prior Phase 1156 tail signing slot was deferred and not
authorized; this window resumes with Phase 1156 as a new sequence-lock phase.

This phase consumes:

- `docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.40.md`
- `docs/specs/ilc_window_1156_1165_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_adr_stale_reconciliation_strike_force_1156_v0.1.md`

No CDL mutation, runtime semantic mutation, signed artifact mutation, or v0.2
signing authorization occurs in Phase 1156.

---

## 2. Firm Phase Sequence

| Phase | Scope | Sensitivity |
|-------|-------|-------------|
| 1156 | Window sequence lock | NON-SENSITIVE |
| 1157 | ADR-0020 acceptance review and unsigned v0.2 candidate update | NON-SENSITIVE |
| 1158 | ADR batch acceptance review: ADR-0012, ADR-0022, ADR-0023, ADR-0008 | NON-SENSITIVE |
| 1159 | ADR-0036 operational release-key draft | NON-SENSITIVE |
| 1160 | SIM-SPECTRAL-04 claim-composition projection build | NON-SENSITIVE |
| 1161 | SIM-SPECTRAL-04 Run 01 | NON-SENSITIVE |
| 1162 | SIM-SPECTRAL-04 disposition and CDL-085 gate verdict | NON-SENSITIVE |
| 1163 | CDL-085 opening | CONDITIONAL; requires `sim_spectral_04_gate_pass` and `GO Phase 1163` |
| 1164 | Coherence report and capsule v5.41 | NON-SENSITIVE |
| 1165 | Window closure gate | SENSITIVE; requires `GO Phase 1165` |

---

## 3. Carry-Forward Tokens

The following carry-forward tokens are inherited from Window 1148-1156:

`adr_0020_acceptance_review_priority_before_tier3_embedding_linkage`
`adr_0012_tier2_blocked_status_proposed`
`adr_0022_tier2_blocked_status_proposed`
`adr_0023_tier2_blocked_status_proposed`
`adr_0008_tier2_blocked_status_proposed_not_accepted`
`sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration`
`matched_size_controls_required_for_future_spectral_sims`
`genesis_canonical_lineage_contract_required_before_public_rc`
`truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`
`contributor_agreement_required_before_public_repo`
`public_rc_envelope_hash_transition_policy_required`

ADR stale-reconciliation routing tokens consumed by this lock:

`adr_0020_phase_1157_priority_lane`
`adr_0012_phase_1158_acceptance_candidate`
`adr_0022_phase_1158_acceptance_candidate`
`adr_0023_phase_1158_scoped_acceptance_candidate_overclaim_risk`
`adr_0008_phase_1158_boundary_acceptance_candidate_after_b6e9e7a8`

---

## 4. CDL-085 Pre-Opening Status

No canonical CDL-085 pre-opening spec exists before Phase 1163.

Current planning references are:

- Phase 1146 disposition and named finding
  `raw_authority_graph_is_not_the_right_spectral_work_graph`;
- `docs/sims/sim_spectral_04/program.md` §5 gate criterion;
- older `EDGE_MINT_PHI_BOUND = None` mentions in runtime/planning surfaces;
- the Window 1156-1165 candidate guidance.

If Phase 1162 emits `sim_spectral_04_gate_pass`, Phase 1163 must first create
`docs/specs/ilc_cdl_085_werner_phi_bound_opening_1163_v0.1.md` from Phase 1162
evidence and must confirm CDL-085 remains unused before CDL mutation.

---

## 5. Non-Claims

This sequence lock does not:

- accept any ADR;
- open or ratify any CDL;
- mutate signed Genesis v0.1 artifacts;
- sign the unsigned Atlas v0.2 candidate;
- change settlement, QATPS, slashing, or runtime semantics;
- select license or contributor-agreement terms.

`window_1156_1165_sequence_lock_committed`
