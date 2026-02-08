# ILC Constitutional Decision Log v0.1

Status: Open
Date: 2026-02-08
Companion proposal: `docs/specs/ilc_constitutional_decisions_proposal_v0.1.md`

Triage reference:
- `docs/research/constitution_clause_triage_v0.1.md`
- `docs/research/constitution_mvp_criticality_v0.1.md`
- `docs/research/constitution_mvp_guardrails_matrix_v0.1.md`
- `docs/specs/ilc_constitutional_decisions_proposal_v0.2.md`

## Triage Snapshot

- `KEEP-NOW`: CDP-001, CDP-002, CDP-004, CDP-005, CDP-006, CDP-009
- `KEEP-DEFER`: CDP-003, CDP-007, CDP-010
- `DEFER-OUT`: CDP-008

## MVP Guardrail Snapshot

- Guardrail matrix: `docs/research/constitution_mvp_guardrails_matrix_v0.1.md`
- `mvp_now` clauses require strict implementation (`CDP-001`, `CDP-002`, `CDP-006`).
- `mvp_guardrail` clauses require explicit owner artifacts now and deferred-target tracking.

## Decision Register

| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |
|---|---|---|---|---|---|---|
| CDL-001 | CDP-001/CDP-002 | Canonical signer lineage definition | open | strict lineage, lineage+timelock, lineage+multi-sig council | lineage+timelock | key registry spec update, validator tests |
| CDL-002 | CDP-001 | Emergency key compromise response | open | immediate revoke, revoke+grace period, staged migration | revoke+grace period | incident policy text, integration tests |
| CDL-003 | CDP-003 | Founder fade-out mechanics | open | fixed sunset, trigger-based sunset, governance-vote sunset | trigger-based sunset | governance spec section, telemetry obligations |
| CDL-004 | CDP-003/CDP-008 | Founder operational caps | open | soft norms, hard protocol caps, hard caps + public reporting | hard caps + reporting | economics/governance spec alignment |
| CDL-005 | CDP-007 | Issuance/cap constitutional wording | open | cap-only, cap+trajectory, cap+trajectory+guardrails | cap+trajectory+guardrails | economics spec + regression tests |
| CDL-006 | CDP-004/CDP-005 | Governance override/challenge process | open | single-body, dual-body, multi-body checks | multi-body checks | challenge node spec, audit path tests |
| CDL-007 | CDP-006 | Rollback resistance baseline | open | seq-only, seq+hash-link, seq+hash+signed checkpoints | seq+hash+signed checkpoints | channel spec + negative tests |
| CDL-008 | CDP-010 | Layer boundary: fixed core vs policy-loaded layers | open | heavy fixed core, minimal fixed core, split-by-domain | split-by-domain | architecture appendix + ADR |
| CDL-009 | CDP-009 | Fork legitimacy/user signaling | open | naming-only, signature-badge, signature-badge+eligibility rules | signature-badge+eligibility rules | client UX + policy docs |
| CDL-010 | CDP-003 | Pseudonymity/accountability balance | open | strict anonymity, pseudonymous attestations, doxxed governance | pseudonymous attestations | comms policy + incident policy |

## Conflict Notes

- Historical sources include both high-level ideals and implementation-era tactical discussion. Tactical excerpts are not automatically constitutional.
- Clauses move to ratified state only when represented as explicit normative language and tied to concrete implementation or governance controls.

## Promotion Rule

A decision may be marked `ratified` only when:

1. It has source citations, and
2. It has a chosen option with rationale, and
3. It has concrete implementation impact listed, and
4. It has at least one verification artifact (test/spec check).
