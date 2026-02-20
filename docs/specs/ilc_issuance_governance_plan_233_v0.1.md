# ILC Issuance Governance Plan 233 v0.1

Status: Phase-233 planning artifact (no parameter ratification)
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact locks the issuance-governance planning surface for Phase 233.

Scope boundaries:
- no parameter ratification is performed in this phase,
- no `ilc_core/` runtime behavior is changed,
- no existing CDL status is mutated from `open` to `ratified`,
- new decision-log queue entries may be proposed as `open` planning IDs in the queue mapping.

## 2. CDL-019 scope analysis

`CDL-019` topic: multiplier-governance surface linking temporary Genesis behavior and long-term governed behavior.

### 2.1 Flat Genesis constant (`1.2x`) scope and sunset condition

Current scope:
- the flat `1.2x` multiplier is a Genesis bootstrapping constant applied to refutation-side reward weighting.

Sunset condition:
- the flat constant must sunset when a governed multiplier policy contract is approved and migration checks are complete.
- sunset activation must require explicit migration plan coverage, invariants regression coverage, and decision-log closure criteria.

### 2.2 Refutation-profitability invariant floor constraint

Constitutional bound:
- the refutation-profitability invariant floor cannot be relaxed by any `CDL-019` option.
- any governed multiplier policy must preserve `R(refute) > R(validate)` under all allowed configurations.

### 2.3 Dynamic ranking-based multiplier path prerequisites

Dynamic path prerequisites:
- formal spec artifact for ranking inputs and bounded update behavior,
- dedicated CDL queue entry for dynamic ranking policy closure,
- migration plan with deterministic rollback behavior,
- invariant regression suite proving the floor remains protected.

### 2.4 CDL-019 closure framing (for future ratification)

Future closure of `CDL-019` must resolve:
1. governed constant surface (who can adjust, bounds, and cadence),
2. invariant floor preservation contract,
3. migration path from flat Genesis constant to governed mechanism,
4. whether dynamic ranking is deferred or admitted with explicit guardrails.

## 3. Open issuance parameter inventory

| Parameter | Current status | Closure path | CDL assignment |
| --- | --- | --- | --- |
| `C_max` total supply cap | proposed, unresolved | ratify explicit cap value after terminal issuance model selection | `CDL-026` (proposed) |
| halving period `H` or continuous decay rate `lambda` | unresolved | choose one decay formulation and lock schedule constants | `CDL-027` (proposed) |
| tail emission mint rate | unresolved | resolve terminal model first; if fee-funded tail selected, mint tail rate locks to zero | `CDL-025` (proposed) |
| fee-burn split ratio | unresolved | lock fee burn / redistribution percentages and transition rule | `CDL-028` (proposed) |
| allocation split (performer/auditor/genesis) | proposed `80/15/5`, unresolved | lock split only after validation against `theta_hard = 1/20` | `CDL-029` (proposed) |
| ECU price clamp bounds (`P_min`, `P_max`) | unresolved | derive clamp bounds from issuance schedule and budget dynamics | `CDL-030` (proposed) |

## 4. Hard cap vs. tail emission reconciliation

Model options:
- **Model A - Asymptotic cap:** perpetual small mint tail with theoretical cap framing.
- **Model B - Fee-funded tail:** mint issuance decays to zero at hard cap; post-issuance rewards are fee-funded.
- **Model C - Burn-offset tail:** ongoing mint tail offset by burns to constrain circulating supply.

Recommended model for routing:
- **Model B** is recommended for future ratification because it keeps the hard-cap claim logically consistent and aligns with fee-funded late-stage rewards.

Ratification routing:
- model selection is routed to `CDL-025` (proposed queue entry).

Prerequisite lock statement:
- hard-cap vs. tail-emission reconciliation must be resolved before `C_max` lock is eligible for closure.

## 5. Decision-log queue mapping

| Queue topic | CDL entry | Current status | Target ratification window |
| --- | --- | --- | --- |
| terminal issuance model (`A/B/C` reconciliation) | `CDL-025` (proposed) | open (proposed) | `Phase 240-241` |
| `C_max` lock | `CDL-026` (proposed) | open (proposed) | `Phase 241-242` |
| decay formulation (`H` vs `lambda`) and schedule | `CDL-027` (proposed) | open (proposed) | `Phase 241-242` |
| fee-burn split ratio | `CDL-028` (proposed) | open (proposed) | `Phase 242-243` |
| allocation split validation and lock | `CDL-029` (proposed) | open (proposed) | `Phase 242-243` |
| ECU price clamp bounds (`P_min`, `P_max`) | `CDL-030` (proposed) | open (proposed) | `Phase 243-244` |
| multiplier-governance closure and migration (`CDL-019`) | `CDL-019` (existing) | open | `Phase 241-243` |
| dynamic ranking multiplier policy (if admitted) | `CDL-031` (proposed) | open (proposed) | `Phase 243-245` |

Queue mapping rule:
- no listed issuance or multiplier-governance item remains unassigned.

## 6. Dependency map

Required ordering constraints:
1. hard-cap vs. tail-emission reconciliation (`CDL-025`) must precede `C_max` lock (`CDL-026`).
2. `C_max` lock (`CDL-026`) must precede decay schedule lock (`CDL-027`).
3. allocation split lock (`CDL-029`) must be validated against `theta_hard = 1/20` before closure.
4. `CDL-019` must be resolved before any dynamic ranking multiplier implementation is eligible.
5. ECU price clamp bounds (`CDL-030`) must follow issuance schedule establishment (`CDL-027`).
6. fee-burn split lock (`CDL-028`) must follow terminal issuance model selection (`CDL-025`).
7. dynamic ranking policy lane (`CDL-031`) must follow `CDL-019` closure criteria and invariant-floor migration checks.

## 7. Non-goal boundaries

Out of scope for Phase 233:
- QATPS/CIT economic coupling (deferred behind Gate E from Phase 231),
- ADAPT profile governance ratification (requires dedicated CDL lane),
- CDL-001/CDL-002/CDL-007 runtime economics (handled in security runtime lane planning),
- cryptographic algorithm or key-size parameters,
- ratification of any issuance or multiplier parameter value in this document.

## 8. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
- `docs/whitepaper/whitepaper_ecu_profiles_and_payouts_v0.2.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.2.md`
- `docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md`
