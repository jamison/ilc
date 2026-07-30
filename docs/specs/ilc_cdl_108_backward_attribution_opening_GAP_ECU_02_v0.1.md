# CDL-108 Backward Attribution Opening (GAP-ECU-02) v0.1

**Phase:** GAP-ECU-02 / Phase 1595d
**Date:** 2026-07-30
**Status:** OPENED, not prelocked, not ratified
**Sensitivity:** SENSITIVE CDL opening
**Opening token:** `backward_attribution_cdl_opened_GAP_ECU_02`

## 1. Purpose

CDL-108 opens the constitutional lane for production backward-attribution ECU
semantics over the ILC epistemic hypergraph. The lane exists to decide how
accepted frontier work may propagate ECU credit backward through typed
provenance, reuse, validation, and revision paths without double-counting
existing CDL-083 refutation credits or CDL-084 caller-specified provenance
credits.

This document records the candidate parameter region selected by
GAP-ECU-01b. It does not ratify the formula, activate runtime graph traversal,
mint ECU, settle ILC, write wallet state, clear public-RC guards, or mutate any
production consensus path.

## 2. CDL Number Assignment

CDL-108 is assigned for this lane after direct register review. CDL-103,
CDL-104, and CDL-105 are already reserved by the pre-RC discovery, spectral,
and validator-identity lanes. CDL-107 is reserved by the GAP-REPUTATION lane
for the reputation/ECU boundary and validator eligibility tier authority.
CDL-108 is therefore the next conflict-free CDL identifier for this
backward-attribution opening.

## 3. Source Authority and Evidence

| Source | Role in this opening |
| --- | --- |
| `docs/specs/ilc_ecu_backward_attribution_canon_reconciliation_GAP_ECU_00_v0.1.md` | Canon reconciliation for all ECU surfaces and the nine unresolved backward-attribution parameter surfaces. |
| `docs/specs/ilc_backward_attribution_sim_contract_GAP_ECU_01a_v0.1.md` | Deterministic SIM contract, adversarial scenarios, output schema, and no-double-count checks. |
| `docs/specs/ilc_backward_attribution_sim_results_GAP_ECU_01b_v0.1.md` | Executed SIM evidence and locked recommended candidate region. |
| `docs/specs/ilc_cdl_083_refutation_economics_ratification_evidence_1420_v0.1.md` | Existing refutation-credit authority and double-count boundary. |
| `docs/specs/ilc_cdl_084_provenance_chain_attribution_ratification_evidence_1422_v0.1.md` | Existing caller-provided provenance-chain authority and decay-depth boundary. |
| `docs/specs/ilc_cdl_102_inviter_chaining_economics_prelock_1573aq_v0.1.md` | Invite-chain economics lane whose Q1 must later reference a ratified backward-attribution formula. |
| `ilc_core/economics/node_value_kernel.py` | Analysis-grade kernel reference only; not production runtime authority. |

## 4. Candidate Parameter Surfaces

The following table records the nine GAP-ECU-00/GAP-ECU-01a parameter surfaces
and the GAP-ECU-01b locked recommended candidate values. These are candidates
for deliberation and prelock, not ratified constants.

| Surface | Candidate value | Evidence note |
| --- | --- | --- |
| Triggering events | `accepted_frontier_plus_invite_init` | Frontier acceptance and invite-init surfaces passed all six adversarial scenarios in the locked region. |
| Eligible upstream artifacts | `medium` | Includes the source artifact classes selected by the SIM without admitting broad unbounded historical capture. |
| Typed path semantics | `PROVENANCE_REUSE_VALIDATE_REVISION` | Allows typed propagation over provenance, reuse, validation, and revision paths while preserving no-double-count checks. |
| Provenance-distance scoring | `status_quality_weighted_distance` | Uses path distance with status and quality weighting rather than raw hop count alone. |
| Decay form | `alpha=0.45`, `max_depth=3`, `age_half_life_epochs=16`, `shape=geometric_hop_with_status_quality_weight` | The locked region passes early-node, stale-founder, citation-ring, and Sybil reuse adversarial tests. |
| Bidirectional / refutation credit split | `beta=0.10`, `forward_retained=0.90`, `refutation_beta=0`, invite beta in same region but not hardcoded | Preserves CDL-083 refutation separation; invite mechanics remain deliberation items. |
| Bounds and caps | `max_traversal_nodes=1000`, `max_traversal_edges=5000`, `novelty_minimum=0.20`, `per_node_cap=0.05`, `per_agent_cap=0.10`, `per_cluster_cap=0.25` | The locked region passed dominance and novelty-gate scenarios; cap unit semantics remain unresolved. |
| Refutation interaction | `refutation_excluded_from_generic_backward_pool` | Validated against CDL-083 no-double-count checks; `refutation_net_only` was not evaluated and remains deferred. |
| Audit surface | `hybrid_merkle_proof` | Candidate proof shape for later runtime binding; no production proof implementation is authorized by this opening. |

## 5. GAP-ECU-01b Evidence Limits and Deliberation Items

1. GAP-ECU-01b is guard-coverage sufficiency evidence under a deterministic
   parametric model. It is not calibrated production graph traversal evidence.
   Calibration against the live Atlas graph and runtime extraction surfaces
   remains in GAP-ECU-04a and GAP-ECU-04b.
2. Cap semantics must be resolved before ratification. The phrase
   `per_agent_cap=0.10` and related dominance caps must specify whether caps are
   per triggering event, per epoch, per attribution batch, per connected
   component, or over another ratified accounting interval.
3. CDL-083 interaction is limited by the SIM result. GAP-ECU-01b validated
   `refutation_excluded_from_generic_backward_pool`; it did not evaluate
   `refutation_net_only`. The latter is deferred unless a later phase explicitly
   models it before prelock.
4. CDL-085 and `EDGE_MINT_PHI_BOUND` interaction must remain open until prelock
   unless fully reconciled. The production lane must decide how phi-bound edge
   mint suppression composes with backward attribution, especially when a typed
   edge is eligible for epistemic credit but also falls under an edge-mint
   bound.
5. Invite-init trigger mechanics remain open. Before ratification, the lane must
   answer how invite-init triggers avoid circular invite credit,
   self-amplification through inviter/worker identity overlap, and thin invite
   chains that add no epistemic novelty. A separate invite-init adversarial
   scenario may be required before prelock if the existing six scenarios are not
   sufficient.

## 6. Relationship to Existing CDLs

**CDL-084 relationship:** CDL-108 does not amend CDL-084. CDL-084 remains the
caller-specified provenance-chain attribution lane. CDL-108 may later ratify a
graph-derived backward-attribution formula only if it preserves no-double-count
separation from explicit CDL-084 provenance-chain credits.

**CDL-083 relationship:** CDL-108 does not amend CDL-083. Upheld refutation
credit remains governed by CDL-083. Generic backward attribution must exclude
or otherwise reconcile refutation-specific credit so the same refutation event
cannot mint twice.

**CDL-085 relationship:** CDL-108 does not amend CDL-085. Any future
backward-attribution runtime must preserve the `EDGE_MINT_PHI_BOUND` suppression
boundary or obtain separate constitutional authority to alter it.

**CDL-102 relationship:** CDL-108 does not ratify invite economics. CDL-102 Q1
must reference a ratified backward-attribution formula before inviter credit is
activated for public RC.

## 7. Open Deliberation Questions for GAP-ECU-02b

1. What is the exact accounting interval for `per_agent_cap`, `per_cluster_cap`,
   and `per_node_cap`?
2. Is `accepted_frontier_plus_invite_init` retained as one trigger class, or are
   invite-init triggers gated by additional identity and novelty predicates?
3. Is `refutation_net_only` rejected, deferred, or added to a targeted SIM
   before prelock?
4. How does `EDGE_MINT_PHI_BOUND` interact with graph-derived backward
   attribution when an eligible typed edge is also phi-bound?
5. What exact proof fields must be included in the `hybrid_merkle_proof`
   surface for third-party verification?
6. Which live Atlas calibration evidence is mandatory before runtime activation
   in GAP-ECU-04a and GAP-ECU-04b?

## 8. Non-Claims

- This opening does not ratify a backward-attribution formula.
- This opening does not activate backward-attribution runtime traversal.
- This opening does not mutate `ilc_core/`.
- This opening does not authorize invite ECU credit.
- This opening does not amend CDL-083, CDL-084, CDL-085, or CDL-102.
- This opening does not mint ECU, settle ILC, write wallet state, or change any
  guard.
- This opening does not authorize public mirror regeneration, public RC, public
  launch, mainnet, or an epoch transition.

## 9. Required Prelock Inputs

GAP-ECU-02b must not prelock this lane until it resolves the evidence-limit
items in Section 5, either by accepting a bounded disposition or requiring
additional SIM/runtime evidence. Prelock must also record exact parameter
constants, cap units, proof schema, no-double-count rules, public-RC
non-activation constraints, and the downstream dependency on GAP-ECU-03
ratification before GAP-ECU-04a/04b implementation can activate a production
bridge.

## 10. Output Token

`backward_attribution_cdl_opened_GAP_ECU_02`
