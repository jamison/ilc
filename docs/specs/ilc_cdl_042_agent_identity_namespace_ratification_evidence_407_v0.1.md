# ILC CDL-042 Agent Identity Namespace Ratification Evidence 407 v0.1

Status: Phase-407 ratification evidence artifact
Date: 2026-03-13
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact records ratification closure for CDL-042, the agent identity namespace and self-sovereign ID derivation lane opened in Phase 402 and hardened in Phase 403.

Scope boundary:
- ratify only CDL-042,
- lock the globally flat key-derived agent_id rule as constitutional law,
- clear the sequence-lock gate for D2e Agent SDK implementation in Phases 410-411,
- preserve runtime deferral in this constitutional phase.

## 2. Ratified decision

CDL-042 is ratified with the globally flat key-derived agent_id candidate.

The ratified candidate keeps a single globally unique namespace surface derived from the CDL-001 trust-root anchor and rejects operator-scoped and epoch-scoped alternatives.

## 3. Evidence basis

Evidence basis for ratification:
- Phase-402 opened the CDL-042 lane and locked the three candidate options,
- Phase-403 hardened the derivation rule, signer-lineage continuity, collision-resistance framing, and D2e carry-forward boundary,
- CDL-001 defines the canonical_root_key trust-root law that anchors identity continuity,
- ADM-003 v0.2 provides the agent-architecture binding and distinguishes agent identity from routing and signing-provider interfaces,
- the Window-402-413 sequence lock requires CDL-042 ratification before D2e runtime implementation.

## 4. Section-7 ratification readiness evidence checklist satisfaction

1. The globally flat namespace candidate is confirmed as the ratified option and the two rejected candidates remain excluded.
2. agent_id derivation from canonical_root_key public bytes is specified and constitutionally locked.
3. CDL-001 signer-lineage continuity under operational key rotation is preserved without changing agent_id.
4. D2e Agent SDK implementation in Phases 410-411 is authorized to use the ratified derivation specification and no substitute derivation path is authorized.
5. Both rejected candidates (domain-prefixed operator-scoped identity and hierarchical epoch-scoped rotation identity) remain constitutionally excluded.

## 5. Agent identity derivation specification

agent_id is deterministically derived from the canonical_root_key public bytes as the CDL-001 trust-root anchor, with no external registry or coordinator required.

CDL-001 signer-lineage continuity is preserved: agent_id is bound to the canonical_root_key public bytes; operational_signer_key rotation does not change agent_id.

Operational derivation rule:
- source material: canonical_root_key public bytes,
- transform: deterministic domain-separated cryptographic hash,
- output class: fixed-length globally unique agent identifier,
- continuity rule: lineage proof binds rotated and recovered operational keys back to the same canonical_root_key rather than re-deriving identity from runtime signing keys.

## 6. Scope boundary and dependency closure

Domain-prefixed namespace with operator-scoped agent_id is rejected because it requires externally assigned operator_id, introducing a registry or coordination step that violates the no-central-registry requirement.

Hierarchical namespace with epoch-scoped key rotation chain is rejected because it changes agent_id at each key rotation epoch, breaking identity continuity across CDL-001 signer-lineage transitions.

No D2e identity implementation may substitute operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary identity derivation without opening a new constitutional lane.

Dependency closure note:
- CDL-040 identity-envelope semantics remain a prerequisite constitutional dependency already ratified in Phase 393,
- CDL-001 remains the signing-lineage trust-root anchor,
- CDL-042 ratification closes the identity-namespace blocker for D2e implementation sequencing.

## 7. D2e Agent SDK carry-forward binding

D2e Agent SDK implementation in Phases 410-411 is now authorized to use the ratified CDL-042 agent_id derivation specification.

CDL-042 ratification is the sequence-lock gate for D2e Agent SDK implementation, and that gate is now cleared for Phases 410-411.

The D2e runtime must treat the ratified canonical_root_key-derived agent_id rule as fixed constitutional input rather than an implementation-time design choice.

## 8. Out-of-scope and deferred tracks

Out of scope in Phase 407:
- no CDL-045 ratification,
- no CDL-046 ratification,
- no D2e Agent SDK runtime implementation,
- no ilc_core runtime mutation,
- no alternate identity aliasing, registry overlay, or epoch-scoped rotation namespace.

Any future display-name layer, alias namespace, or operator grouping metadata must remain derivative of the ratified agent_id rule rather than replacing it.

## 9. Canonical anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_042_agent_identity_namespace_prelock_hardening_403_v0.1.md`
- `docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
