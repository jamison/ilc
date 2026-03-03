# ILC Antigravity Context Capsule v0.9

Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.8.md`

## 1. Project Identity

ILC remains a ratification-first constitutional protocol project with runtime implementation deferred until the relevant CDL is ratified.

ILC remains a protocol for autonomous digital agents to participate in an epistemic graph through claims, refutations, economic incentives, and challenge-driven reuse.

## 2. Core Architectural Invariants

The three-envelope model remains the anchor invariant.

No runtime implementation was authorized in Window 338-347.

The following remain invariant:
- canonical encoding remains DAG-CBOR + CIDv1 + COSE Sign1 + NDJSON,
- the graph remains the computer,
- protocol value remains challenge- and reuse-oriented rather than approval-oriented,
- constitutional changes remain controlled by the CDL process rather than runtime consensus shortcuts.

Canonical carried-forward panel and governance tokens:
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
- `The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.`
- `The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.`
- `Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention.`

## 3. Project State (as of Phase 346 completion)

Phase 346 complete.

Phase 347 next.

Window 338-347 closure lane remains pending.

## 4. Window 338-347 Constitutional State

Window 338-347 remains a pre-ratification, pre-implementation contract window.

CDL-034 through CDL-038 are open and unratified.

CDL-024 is ratified.

CDL-V1 through CDL-V7 are ratified.

CDL-021 remains open and milestone-triggered/deferred.

## 5. Node-Schema Contract Openings

The active open stack is `CDL-034`, `CDL-035`, `CDL-036`, `CDL-037`, and `CDL-038`.

- `CDL-034` covers the unified node schema envelope, reserved fields, and primitive/core field taxonomy.
- `CDL-035` covers validation lifecycle, gate-verdict attachment, and quarantine semantics.
- `CDL-036` covers node dissemination header, payload fetch contract, and transport boundary.
- `CDL-037` covers executable node descriptor, safety contract, and agent-side sandboxing.
- `CDL-038` covers private-to-public promotion, `promotion_receipt` provenance, and visibility-change continuity.

Window 348+ begins with ratification work, not runtime implementation.

## 6. Reputation Adjoint Verdict

Reputation adjunct contract is sufficient; no dedicated CDL lane is required in Window 348+.

Reputation remains derived from lifecycle outputs, not from a direct score field, and mutable inline node-level reputation remains forbidden.

## 7. Open Risks and Runtime Deferrals

Canary token obfuscation fix: 5c2b89f

Recurring phantom-edit incidents affected CDL-026 and signer-lineage worktree files; commit-time and canary controls caught them before constitutional drift.

`docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md currently omits the 7+1 evaluation panel as an agent behavioral role.`

`This gap must be resolved before Window 348+ implementation begins.`

## 8. Ratification-First Window 348+ Entry Conditions

Window 348+ begins with ratification work, not runtime implementation.

The first authorized Window-348+ work is controlled ratification of `CDL-034` through `CDL-038`.

## 9. Change Log from v0.8

Changed relative to v0.8:

This capsule is self-contained; unchanged sections from v0.8 are carried forward in full where still applicable.

Unchanged sections are carried forward unless explicitly updated here.

Changed sections are enumerated explicitly rather than implied.

- Added the Window 338-347 constitutional opening inventory.
- Added the Phase-345 reputation verdict.
- Added the ratification-first Window 348+ readiness boundary.
- Added the canary-fix and phantom-edit operational notes.

## 10. Key Canonical Anchors

- `docs/specs/ilc_antigravity_context_capsule_v0.8.md`
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_338_347_node_schema_program_plan_v0.1.md`
- `docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_336_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_346_v0.1.md`
- `docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
