# ILC CDL-042 Agent Identity Namespace Open Prelock v0.1

Status: Phase-402 constitutional opening prelock
Date: 2026-03-13
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact opens the CDL-042 constitutional lane for agent identity namespace design and self-sovereign agent_id derivation.

The opening is additive and non-ratifying.

## 2. CDL-042 opening state

status: open

CDL-042 opens as the agent identity namespace lane, unblocked by CDL-040, CDL-041, and CDL-043 ratification in Phases 393-395.

## 3. Constitutional and architectural dependency anchors

Anchors:
- CDL-001 signing-key identity root and signer-lineage continuity.
- ADM-003 agent architecture and signing-provider boundary.
- CDL-034 envelope and authored/protocol/transport identity boundary.
- CDL-040 ratified identity-envelope semantics.

## 4. Self-sovereign ID derivation constraint and candidate option framing

Agent identity derivation must be deterministic from the signing key with no central registry requirement.

Candidate options opened in the decision log:
- globally flat namespace with key-derived agent_id,
- domain-prefixed namespace with operator-scoped agent_id,
- hierarchical namespace with epoch-scoped key rotation chain.

The proposed opening candidate is the globally flat namespace with key-derived agent_id.

## 5. Multi-agent-per-operator uniqueness constraint

The operator_id may be shared across many agents; agent_id must remain unique per agent.

CDL-042 must treat operator_id and agent_id as distinct identifiers so high-scale multigenic deployments do not collapse into a registry bottleneck.

## 6. D2e dependency and sequencing note

CDL-042 is the identity prerequisite for the D2e Agent SDK block planned for Phases 410-411.

Phase-403 is the targeted prelock hardening lane for CDL-042.

## 7. Out-of-scope and deferred tracks

No runtime implementation occurs in Phase 402.

Full namespace collision analysis, operator-scale uniqueness proofs, and D2e implementation binding are deferred to later phases.

## 8. Canonical anchors

- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_window_392_413_candidate_phase_grouping_v0.1.md`
