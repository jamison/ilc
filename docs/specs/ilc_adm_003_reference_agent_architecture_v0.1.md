# ILC ADM-003 Reference Agent Architecture v0.1

Status: Phase-292 architecture lock artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the canonical reference-agent architecture boundaries for post-ratification implementation planning.

Scope:
- architecture-level decomposition,
- signing and key-isolation boundary definition,
- dependency and phased rollout mapping,
- explicit 7+1 evaluation panel behavioral-role resolution.

## 2. Architecture layers and responsibilities

Layer model:
1. Interface layer: CLI/SDK command surfaces and JSON contract adaptation.
2. Orchestration layer: workflow coordination, policy-gated execution planning.
3. Protocol layer: canonical validation, ratification-aware policy evaluation.
4. Runtime integration layer: storage/network adapters and environment bindings.

Responsibility split:
- policy interpretation remains separated from transport/runtime adapters,
- deterministic protocol behavior remains isolated from UI concerns.

Role decomposition:
- `Evaluation Panel Member`
- `Graph Observation / Schema Evolution Analyst`

The 7+1 evaluation panel is case-evaluation infrastructure, not a standing constitutional authority.

Evaluation Panel Member responsibilities:
- the `7+1 evaluation panel` evaluates knowledge-claim cases,
- `panel_size=8`,
- `independence_k=3`,
- `outsider_seat=true`,
- `Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat`,
- `VRF-selected outsider seat is the anti-capture mechanism`,
- `trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2`,
- `CDL-V3 cluster diversity floor operationalizes independence_k=3`,
- `CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism`,
- `L0=3 is architecturally safe because CDL-V7's Popperian gate ensures L0 basic statements are independently and directly verifiable.`,
- `The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.`,
- `The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.`

Graph Observation / Schema Evolution Analyst responsibilities:
- monitors public-graph patterns,
- prepares evidence summaries for future CDL lanes,
- surfaces schema-evolution candidates without ratifying them,
- remains separate from case evaluation and from constitutional authority.

## 3. Signing and key-isolation boundaries

Signing boundary principles:
- wallet-agnostic signing is mandatory,
- signing provider interface remains abstracted from protocol logic,
- private key material must remain outside protocol-state payloads.

Key-isolation boundary:
- signing requests use detached payload digest contracts,
- provider isolation is required for local, hardware, and external wallet backends.

`kid` privacy boundary:
- COSE `kid` must not contain raw public key material,
- `kid` values are opaque routing identifiers only.
- kid values are opaque routing identifiers only.

## 4. Protocol/SDK/runtime dependency map

Dependency map:
- protocol invariants and CDL states feed SDK command-level affordances,
- SDK command contracts feed runtime adapters,
- runtime adapters must not bypass protocol validation boundaries.

Governance-preparation boundary:
- Continuous graph observation and schema-evolution preparation are analytics/governance-preparation functions, not ratification authority.
- ADM-003 defines role boundaries; a separate governance artifact defines schema-evolution workflow.
- The graph-observation role may prepare evidence summaries for future CDL lanes but may not open or ratify CDL rows by itself.
- Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.
- This Phase-354 role resolution remains a prerequisite for Window-358+ implementation authorization; it does not itself authorize implementation.

Implementation boundary:
- no runtime changes in `ilc_core/`,
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no implementation authorization in this phase.

Carry-forward dependencies:
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`,
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`,
- `docs/specs/ilc_integration_coherence_report_336_v0.1.md`,
- `docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md`,
- `docs/specs/ilc_phase_348_357_sequence_lock_v0.1.md`,
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`.

## 5. Security and privacy invariants

Invariants:
1. no unsigned state transitions in canonical protocol path,
2. signer identity metadata must preserve privacy boundary constraints,
3. provider compromise must be containable without protocol-layer secret leakage,
4. protocol validation must remain deterministic across replay contexts,
5. panel participation does not convert the evaluation panel into constitutional voting authority,
6. graph observation does not become schema-ratification authority,
7. L-tiers remain epistemic tiers rather than authority tiers or reputation tiers,
8. reputation thresholds and reviewer defaults remain unratified and must not be encoded as settled protocol law.

## 6. Non-goals and phased rollout

Non-goals in this phase:
- no runtime implementation in `ilc_core/`,
- no decision-log mutation,
- no direct CLI feature implementation,
- no panel-to-constitution shortcut,
- no graph-observation ratification authority,
- no implementation authorization for Window 358+.

Phased rollout boundary:
- implementation remains deferred until Window 357 closure and explicit Window 358+ authorization,
- this phase resolves the ADM-003 role gap required before implementation authorization can later be granted,
- this phase does not itself grant implementation authorization.

## 7. Canonical anchors

- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.9.md`
- `docs/specs/ilc_integration_coherence_report_336_v0.1.md`
- `docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md`
- `docs/specs/ilc_phase_348_357_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Boundary statement:
- no runtime changes in `ilc_core/` and no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md` in this artifact lane.
