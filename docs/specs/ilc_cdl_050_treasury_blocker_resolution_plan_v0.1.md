# ILC CDL-050 Treasury Lane: Blocker Resolution Plan and Implementation Roadmap v0.1

**Status:** Internal planning document — non-normative, post-consensus research roadmap
**Date:** 2026-03-19
**Authors:** Jamie (ILC Project Lead) + Claude Sonnet 4.6
**Source sessions:** Gemini (2026-03-18 CDL-050 and long-tail discussions), Opus 4.6 (2026-03-19 treasury reframing), Codex review (2026-03-19)
**Dependencies:** CDL-047 (Treasury governance framework), CDL-030 (P_e clamp range), ADR-0017 (post-issuance transition, corrected 2026-03-19), ADR-0018 (Sequestered Financial Shard)

---

## 1. Current Blocking State

CDL-050 remains unopened. Three official blockers are live, recorded by Phase 431 and re-confirmed by Phase 438:

1. **A decoupled recovery criterion** — the simulation's recovery definition was trigger-coupled and circular.
2. **An explicit Treasury risk-tolerance judgment** — no constitutional bounds have been specified for intervention lever magnitudes.
3. **Additional discriminating simulation evidence** — SIM-009 results were too weakly differentiated between leading choices to justify parameter lock-in.

Additionally, the CDL-050 lane framing requires resolution before the blockers can be addressed. The old framing (lock P_e trigger/limit constants) has been superseded by the ECU-side credit governance model established in ADR-0017 (corrected 2026-03-19). The three blockers must be addressed within the reframed model, not within the old P_e-defense framing.

Reference documents:
- `docs/specs/ilc_treasury_pe_prerequisite_satisfaction_review_438_v0.1.md` (Phase 438 blocker re-confirmation)
- `docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md` (Phase 431 original blocker recording)
- `docs/research/ilc_cdl_050_blocker_map_and_reframing_memo_v0.1.md` (reframing analysis)
- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md` (corrected ECU-side model)

---

## 2. Architectural Prerequisite: The L1/L2 Separation

Before the three blockers can be resolved, one architectural decision must be formalized: the separation between the Treasury (L1) and the Sequestered Financial Shard (L2).

This is not a new concept. ADR-0018 (Sequestered Financial Shard) already proposes a dedicated shard for securities-like trading, HFT, and financial instruments, with a separate conversion budget (`B_hft` independent of `B_e`) and explicit contagion firewalls. What changes here is priority: ADR-0018 must be elevated from "post-launch optional" to **Genesis affordance and CDL-050 prerequisite**.

**The L1/L2 principle:**

- **L1 (Treasury):** Operates exclusively on ECU-side credit conditions. Issues ECU based on real-time productive work. Constitutional prohibition on the Treasury reading or responding to L2 derivative market state.
- **L2 (Sequestered Financial Shard):** Agent-to-agent derivatives, futures, and leveraged positions on node NPV. Operates under separate rules with `B_hft` independent of `B_e`. Full contagion firewall from L1.

**Why this is a CDL-050 prerequisite:** Treasury risk-tolerance bounds (Blocker 2) cannot be correctly specified unless it is known that derivative market collapse cannot reach L1. Without the L1/L2 firewall, any risk-tolerance judgment must account for an unbounded contagion surface. With it, Treasury risk is bounded strictly to ECU-side lever magnitudes.

**Action required:** Revise ADR-0018 priority from "Post-launch" to "Genesis affordance (required before CDL-050 opens)."

Reference:
- `docs/research/ilc_decoupled_derivative_mechanics_v0.1.md` (Gemini reconstruction of the contagion isolation concept)
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md` Section 4.3 (Sequestered Shard proposal)

---

## 3. Proposed Solution: Blocker 1 — Decoupled Recovery Criterion

### The problem

Phase 430 simulation defined recovery as "P_e returns to trigger threshold." This coupled trigger and recovery to the same observable (P_e), making the test circular: any Treasury intervention that forced P_e above the threshold counted as "recovered," even if the underlying ECU economy was still in distress.

### Proposed fix: separate observables for trigger and recovery

**Trigger condition (starts intervention):**

```
P_e < P_low  OR  P_e > P_high
```

Measured from `P_e`, the downstream conversion rate output.

**Recovery condition (ends intervention):**

The Treasury deactivates when all three sub-conditions hold simultaneously:

1. The *organic* ECU creation rate — defined as ECU generated per epoch excluding (a) bounty-enhanced claims and (b) claims filed while maximum-escrow restrictions are active — returns to within ±15% of its 12-epoch trailing average.
2. The above holds for 3 or more consecutive epochs.
3. The trigger condition is simultaneously false (`P_e` is within bounds).

### Why this is decoupled

- The trigger measures a downstream price output (`P_e`).
- The recovery criterion measures upstream production velocity, explicitly purged of Treasury intervention contributions.
- The Treasury cannot game its own exit criterion by continuing to intervene — bounty-enhanced ECU and maximum-escrow-restricted claims are excluded from the organic rate measurement.
- Recovery requires the system to self-stabilize, not the Treasury to force `P_e` to any value.

### Artifact required

`docs/specs/ilc_cdl_050_decoupled_recovery_criterion_v0.1.md` — formal specification including the organic rate calculation method, the ±15% tolerance band, and the 3-epoch stability requirement. This is a Phase 455 deliverable. The specific tolerance values (±15%, 3 epochs) are illustrative and must be confirmed by SIM-T Scenario 5.

---

## 4. Proposed Solution: Blocker 2 — Explicit Treasury Risk-Tolerance Judgment

### The problem

No constitutional bounds have been specified for how aggressively each ECU-side intervention lever may be used. A risk-tolerance judgment without the L1/L2 firewall would need to account for unlimited contagion risk from derivative markets. The L1/L2 separation (Section 2) bounds the risk surface to ECU-side lever magnitudes only.

### Four constitutional bounds required

Exact values are determined by SIM-T (Section 5). The following are illustrative planning anchors pending simulation:

| Lever | Parameter | Illustrative anchor | Constraint rationale |
|---|---|---|---|
| Bounty stimulus ceiling | `B_max_bounty` | ≤ 25% of `B_e` per epoch | Prevents Treasury from crowding out organic productive work |
| Escrow tightening ceiling | `E_ceiling` | ≤ 10x baseline escrow | Prevents productive agent exodus; to be validated by SIM-T Scenario 1 |
| Vesting time-lock ceiling | `V_max` | ≤ 50 additional epochs | Limits end-of-lock release shock; to be validated by SIM-T Scenario 2 |
| Stabilization levy ceiling | `L_max` | ≤ 0.1% of locked stake per epoch | Minimal mutualized backstop; to be confirmed by SIM-T Scenario 4 |

**Fifth bound (categorical, not a parameter):** Constitutional prohibition on the Treasury reading or responding to L2 (Sequestered Shard) derivative market state. This is the hard outer wall — zero contagion tolerance, enforced structurally through the ADR-0018 architecture rather than by parameter calibration.

### Artifact required

`docs/specs/ilc_cdl_050_treasury_risk_tolerance_judgment_v0.1.md` — explicit statement of all four parameter bounds (values filled in from SIM-T results) plus the categorical L2 prohibition. This is a Phase 454 deliverable.

---

## 5. Proposed Solution: Blocker 3 — Discriminating Simulation Evidence

### The problem

SIM-009 results were too weakly differentiated between competing intervention-limit choices to justify locking any constants. The simulation was designed around the old P_e framing and did not test ECU-side levers at all.

### SIM-010 naming conflict

The comprehensive architecture document (`docs/specs/ilc_economic_architecture_comprehensive_v0.1.md` Section 8) defines SIM-010 as "Transfer tax rate calibration." A separate Gemini session defined SIM-010 as the Treasury adversarial simulation. Neither is ratified. The Treasury adversarial simulation is labeled **SIM-T** throughout this plan until the canonical simulation number is assigned at Phase 451.

### SIM-T: five discriminating scenarios

**Scenario 1 — Escrow multiplier discrimination:**
Compare escrow ceiling = 2x, 5x, 10x, 20x under a standardized overheating episode.
Discriminating question: what is the minimum effective ceiling that stops spam without causing productive agent exodus (measured by organic claim rate drop)?

**Scenario 2 — Vesting lock duration discrimination:**
Compare time-lock = 10, 25, 50, 100 additional epochs under a standardized velocity crisis.
Discriminating question: what duration produces the best P_e stability profile during the lock period AND the smallest release shock at expiry when the cohort of locked ECU converts en masse?

**Scenario 3 — L1/L2 contagion isolation test:**
Simulate full L2 (Sequestered Shard) market collapse: all leveraged positions default simultaneously.
Discriminating question: is `P_e` in the main economy unaffected? Is L1 organic ECU production unaffected?

**Scenario 4 — Long-tail zero-issuance stress test:**
Set ILC epoch issuance `I_e = 0`. Induce 300% spike in verification requests.
Discriminating question: do L1 ECU-side levers alone (bounties, escrow tightening, velocity control) maintain `P_e` within clamp bounds (CDL-030: 0.75–1.30) without any ILC issuance subsidy?

**Scenario 5 — Recovery criterion exit validation:**
Apply the decoupled recovery criterion from Section 3 to an active intervention episode.
Discriminating question: does the criterion correctly exit intervention when organic ECU production normalizes? Can it be gamed by an adversary who manipulates `P_e` from outside?

### Artifact required

`docs/specs/ilc_sim_t_treasury_adversarial_commission_brief_v0.1.md` — formal commission brief with all five scenarios, explicit input states, perturbation methods, success criteria, and discriminating metrics. This is a Phase 451 deliverable. The brief must define what "discriminating evidence" means before any simulation run begins.

---

## 6. Terminology Normalization

All future Treasury constitutional work must use canonical ILC terms. The following Gemini and research-session terms are mapped here for reference:

| Research/Gemini term | Canonical ILC term |
|---|---|
| Algorithmic Load Balancer | Treasury |
| Epistemic Fuel | ECU |
| Epistemic Dividend | Reuse scoring (existing, BAL profile reuse weight 0.35) |
| block_reward | Epoch issuance `I_e` |
| L2 Epistemic Bond derivatives | Sequestered Financial Shard (ADR-0018) |
| SIM-010 (Gemini Treasury) | SIM-T (planning label, pending canonical number) |
| SIM-010 (architecture doc) | Transfer tax calibration simulation (Section 8, comprehensive architecture) |

---

## 7. Implementation Roadmap (Post-Window 449)

All work below is scheduled post-Window 441-449. CDL-050 is explicitly excluded from the consensus block by the Phase 441 sequence lock.

| Phase | Deliverable | Blocker addressed |
|---|---|---|
| 450 | Treasury Reframing Review — formally lock ECU-governor framing, retire old P_e-defense framing | Prerequisite |
| 450 | ADR-0018 priority revision — Sequestered Shard elevated from post-launch optional to Genesis affordance + CDL-050 prerequisite | Prerequisite |
| 451 | SIM-T Commission Brief — five discriminating scenarios with explicit success criteria; resolve SIM-010 naming conflict | Blocker 3 setup |
| 452–453 | SIM-T Simulation Run — comparative results for all five scenarios | Blocker 3 evidence |
| 454 | Treasury Risk-Tolerance Judgment Document — four constitutional bounds derived from simulation results | Blocker 2 cleared |
| 455 | Decoupled Recovery Criterion Document — formal trigger/recovery observable specification | Blocker 1 cleared |
| 456 | CDL-050 Pre-Opening Review — confirm all three blockers cleared; confirm ADR-0018 in Genesis affordances | Gate |
| 457 | CDL-050 Opening | (if gate passes) |

---

## 8. Non-Goals of This Plan

- This plan does not authorize opening CDL-050 now or before Phase 456.
- This plan does not supersede the Window 441-449 consensus-first sequencing.
- This plan does not define final Treasury constants — those are Phase 454 deliverables based on SIM-T results.
- This plan does not resolve the SIM-010 naming conflict — that is a Phase 451 deliverable.
- This plan is not constitutional law. It is a non-normative planning document subject to revision as research advances.

---

## 9. Supporting Research Documents

The following non-normative documents informed this plan:

- `docs/research/ilc_cdl_050_blocker_map_and_reframing_memo_v0.1.md`
- `docs/research/ilc_treasury_ecu_credit_governor_concept_note_v0.1.md`
- `docs/research/ilc_treasury_and_resource_rotation_open_questions_register_v0.1.md`
- `docs/research/ilc_long_horizon_resource_rotation_concept_note_v0.1.md`
- `docs/research/ilc_opus_treasury_jubilee_and_graph_dependency_analysis_v0.1.md`
- `docs/research/ilc_treasury_pe_long_tail_mechanics_and_sim_010_design_v0.1.md`
- `docs/research/ilc_decoupled_derivative_mechanics_v0.1.md`
