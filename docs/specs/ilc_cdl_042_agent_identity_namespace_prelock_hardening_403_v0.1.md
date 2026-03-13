# ILC CDL-042 Agent Identity Namespace Prelock Hardening v0.1

Status: Phase-403 constitutional prelock hardening artifact
Date: 2026-03-13
Owner lane: G8 Constitution Cluster A

## 1. Purpose and hardening scope

This artifact hardens the CDL-042 opening lane into a full prelock record for later ratification.

CDL-042 prelock hardening confirms the proposed candidate: globally flat namespace with key-derived agent_id.

## 2. CDL-042 current state and Phase-402 opening inheritance

status: open

Phase-402 opened CDL-042 as the agent identity namespace lane and established the three candidate options, the self-sovereign derivation boundary, and the operator-scale uniqueness requirement.

This hardening artifact is distinct from and supersedes the Phase-402 opening stub for evidential purposes while preserving the Phase-402 register state unchanged.

No CDL row mutation occurs in Phase 403.

## 3. Candidate option discrimination

Winning candidate:
- globally flat namespace with key-derived agent_id.

Rejected candidate A:
- Domain-prefixed namespace with operator-scoped agent_id is rejected because it requires externally assigned operator_id, introducing a registry or coordination step that violates the no-central-registry requirement.

Rejected candidate B:
- Hierarchical namespace with epoch-scoped key rotation chain is rejected because it changes agent_id at each key rotation epoch, breaking identity continuity across CDL-001 signer-lineage transitions.

The globally flat namespace wins because it is deterministic, decentralized, collision-resistant at protocol scale, and directly compatible with CDL-001 signer-lineage continuity and later D2e binding.

## 4. Proposed candidate: globally flat key-derived agent_id specification

agent_id is deterministically derived from the canonical_root_key public bytes as the CDL-001 trust-root anchor, with no external registry or coordinator required.

Derivation specification:
- source material: DER-encoded compressed canonical_root_key public bytes,
- transform: domain-separated cryptographic hash over the canonical_root_key public bytes,
- output requirement: fixed-length identifier with at least 256 bits of effective collision resistance,
- publication boundary: agent_id is public protocol identity material, distinct from the opaque COSE kid routing identifier required by ADM-003 and the signing-provider interface.

Using canonical_root_key public bytes rather than operational_signer_key public bytes preserves identity stability across operational key rotation while keeping the namespace self-sovereign.

## 5. Namespace collision resistance and uniqueness at scale

Namespace collision probability at target network scale is negligible under the proposed derivation scheme.

A 256-bit hash space remains effectively collision-free for the minimum viable 10,000-agent regime observed in SIM-001 through SIM-003 and for all expected deployment scales materially beyond that threshold.

operator_id does not participate in uniqueness derivation. It remains an orthogonal grouping field for operators managing many agents, while agent_id remains globally unique on its own namespace surface.

## 6. Signer-lineage compatibility and key rotation semantics

CDL-001 signer-lineage continuity is preserved: agent_id is bound to the canonical_root_key public bytes; operational_signer_key rotation does not change agent_id.

Operational key lifecycle events (`active`, `rotated`, `revoked`, `recovered`) are validated through the CDL-001 signer-lineage chain. Identity continuity is proven by lineage linkage back to the same canonical_root_key, not by re-deriving agent_id from rotated operational keys.

This preserves stable protocol identity across rotation and recovery while keeping revocation and replay validation within the existing signer-lineage law.

## 7. D2e SDK integration binding and Phase 407 ratification readiness

D2e Agent SDK implementation in Phases 410-411 is bound to the CDL-042 agent_id derivation specification locked in this hardening artifact.

No D2e identity implementation may substitute operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary identity derivation without opening a new constitutional lane.

Phase 407 is the targeted CDL-042 ratification lane; this hardening artifact constitutes the primary prelock evidence.

## 8. Out-of-scope and deferred tracks

Out of scope in Phase 403:
- no CDL row mutation,
- no CDL-042 ratification,
- no CDL-045 prelock hardening,
- no CDL-035 timed_out amendment work,
- no D2e runtime implementation,
- no ilc_core runtime mutation.

Any future namespace aliasing, human-readable display naming, or identity-recovery UX layer must remain derivative of the ratified agent_id rule rather than replacing it.

## 9. Canonical anchors

- `docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_042_agent_identity_namespace_open_prelock_402_v0.1.md`
- `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
- `docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md`
- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`
