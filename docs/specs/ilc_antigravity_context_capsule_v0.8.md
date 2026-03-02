# ILC Antigravity Context Capsule v0.8

Status: living document - updated at phase boundaries  
Date: 2026-03-02  
Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.7.md`

Purpose: provide the minimum current architectural and constitutional context needed to execute post-Phase-336 work without reintroducing the closed-window governance ambiguities that Phase 336 resolved.

## 1. Project Identity

ILC remains a protocol for autonomous digital agents to participate in an epistemic graph through claims, refutations, economic incentives, and challenge-driven reuse.

## 2. Core Architectural Invariants

The following remain invariant:
- canonical encoding remains DAG-CBOR + CIDv1 + COSE Sign1 + NDJSON,
- the graph remains the computer,
- protocol value remains challenge- and reuse-oriented rather than approval-oriented,
- constitutional changes remain controlled by the CDL process rather than runtime consensus shortcuts.

## 3. Project State (as of Phase 336 completion)

Current state tokens:
- `Phase 336 complete`
- `Phase 337 next`
- `Window 328-337 closure lane remains pending.`

## 4. Window 328-335 Constitutional State

Current constitutional state:
- `CDL-024 is ratified.`
- `CDL-V1 through CDL-V7 are ratified.`
- `CDL-021 remains open and milestone-triggered/deferred.`

## 5. Evaluation Panel Architecture

Canonical panel tokens:
- `panel_size=8`
- `independence_k=3`
- `outsider_seat=true`
- `Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat`
- `quorum k=5 of m=7`
- `VRF-selected outsider seat`
- `VRF-selected outsider seat is the anti-capture mechanism`
- `trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2`
- `CDL-V3 cluster diversity floor operationalizes independence_k=3`
- `CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism`

## 6. L-Tier Disambiguation

Boundary tokens:
- `The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.`
- `The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.`
- `Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention.`

## 7. CDL-V Authority and Sequencing Carry-Forward

Sequencing tokens:
- `CDL-V2 -> CDL-V3 -> CDL-V4`
- `CDL-V4 <-> CDL-V6`
- `CDL-V5 -> CDL-V7`
- `CDL-V1 has no V-series ordering constraint`

## 8. ADM-003 Carry-Forward Gap

Gap tokens:
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md currently omits the 7+1 evaluation panel as an agent behavioral role.`
- `This gap must be resolved before Window 338+ implementation begins.`

## 9. Implementation Frontier

Near-term frontier:
- Phase 337 closure execution for Window 328-337,
- carry-forward of the ratified panel architecture into future implementation planning,
- resolution of the `ADM-003` panel-role omission before Window 338+ implementation begins.

## 10. Key Canonical Anchors

Primary anchors:
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_336_v0.1.md`
