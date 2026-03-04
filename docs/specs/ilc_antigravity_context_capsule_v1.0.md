# ILC Antigravity Context Capsule v1.0

Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.9.md`

This capsule is self-contained and carries forward all still-applicable v0.9 context.

## 1. Project Identity

ILC remains a ratification-first constitutional protocol project.

ILC remains a protocol for autonomous digital agents to participate in an epistemic graph through claims, refutations, economic incentives, and challenge-driven reuse.

## 2. Core Architectural Invariants

The three-envelope model remains the anchor invariant.

Canonical encoding remains DAG-CBOR + CIDv1 + COSE Sign1 + NDJSON.

The graph remains the computer.

Protocol value remains challenge- and reuse-oriented rather than approval-oriented.

Constitutional changes remain controlled by the CDL process rather than runtime consensus shortcuts.

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

## 3. Project State (as of Phase 355 completion)

Phase 355 complete.

Phase 356 next.

Window 348-357 remains implementation-free through this phase.

## 4. Window 348-357 Constitutional State

CDL-034 through CDL-038 are ratified.

ADM-003 7+1 panel role is resolved.

`CDL-024` and `CDL-V1` through `CDL-V7` remain ratified.

`CDL-021` remains open and milestone-triggered/deferred.

## 5. Ratified Node-Schema Surfaces

Ratified node-schema set:
- `CDL-034` — node schema core envelopes and reserved-field boundary,
- `CDL-035` — validation lifecycle and gate-verdict attachment,
- `CDL-036` — dissemination header and fetch contract,
- `CDL-037` — executable descriptor and safety contract,
- `CDL-038` — promotion continuity and `promotion_receipt`.

Window 358+ may begin implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.

## 6. ADM-003 and Reputation Boundary

ADM-003 7+1 panel role is resolved.

Reputation adjunct contract remains sufficient; no dedicated reputation CDL lane is required.

The 7+1 panel remains case-evaluation infrastructure rather than constitutional voting authority.

Graph observation remains governance-preparation infrastructure rather than ratification authority.

## 7. Runtime Authorization Boundary

No runtime implementation occurs in Phase 355.

Phase 355 does not authorize runtime implementation.

Window 358+ may begin implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.

Unratified surfaces remain implementation-barred.

## 8. Remaining Risks and Window-357 Preconditions

Window 357 must still prove:
- all closure-gate conditions hold,
- no runtime implementation occurred in Window 348-357,
- the implementation authorization scope remains bounded to ratified surfaces only.

Operational note:
- canary race artifacts remain an editor concern, not a constitutional-state concern.

## 9. Change Log from v0.9

Changed relative to v0.9:

v1.0 incorporates the ratified CDL-034 through CDL-038 state and the resolved ADM-003 panel-role boundary.

This capsule upgrades the prior open-prelock framing to ratified-state framing.

This capsule upgrades the implementation boundary from ratification-first entry conditions to post-ratification authorization scope gated on Phase 357 closure.

## 10. Key Canonical Anchors

- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md`
- `docs/specs/ilc_phase_348_357_sequence_lock_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_355_v0.1.md`
- `docs/specs/ilc_node_schema_implementation_authorization_scope_355_v0.1.md`
