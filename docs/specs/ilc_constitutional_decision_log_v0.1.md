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
| CDL-003 | CDP-003 | Founder fade-out mechanics | ratified | fixed sunset, trigger-based sunset, governance-vote sunset | trigger-based sunset | governance spec section, telemetry obligations |
| CDL-004 | CDP-003/CDP-008 | Founder operational caps | ratified | soft norms, hard protocol caps, hard caps + public reporting | hard caps + reporting | economics/governance spec alignment |
| CDL-005 | CDP-007 | Issuance/cap constitutional wording | ratified | cap-only, cap+trajectory, cap+trajectory+guardrails | cap+trajectory+guardrails | economics spec + regression tests |
| CDL-006 | CDP-004/CDP-005 | Governance override/challenge process | ratified | single-body, dual-body, multi-body checks | multi-body checks | challenge node spec, audit path tests |
| CDL-007 | CDP-006 | Rollback resistance baseline | open | seq-only, seq+hash-link, seq+hash+signed checkpoints | seq+hash+signed checkpoints | channel spec + negative tests |
| CDL-008 | CDP-010 | Layer boundary: fixed core vs policy-loaded layers | ratified | heavy fixed core, minimal fixed core, split-by-domain | split-by-domain | architecture appendix + ADR |
| CDL-009 | CDP-009 | Fork legitimacy/user signaling | ratified | naming-only, signature-badge, signature-badge+eligibility rules | signature-badge+eligibility rules | client UX + policy docs |
| CDL-010 | CDP-003 | Pseudonymity/accountability balance | ratified | strict anonymity, pseudonymous attestations, doxxed governance | pseudonymous attestations | comms policy + incident policy |
| CDL-011 | ADR-0008 / NodeValueTrack | Node usefulness formula ratification (`EW`) | ratified | reuse-heavy, balanced composite, resilience-heavy | balanced composite | deterministic score vectors + conformance tests |
| CDL-012 | ADR-0008 / NodeValueTrack | Utility-flow reward linkage (`UF`) | ratified | usage-only, usage+freshness, full composite | usage+freshness | payout simulation + regression tests |
| CDL-013 | ADR-0008 / NodeValueTrack | Governance-weight decay and Genesis baseline | ratified | decay-all, decay-non-genesis-only, hybrid baseline | decay-non-genesis-only | governance normalization tests + policy docs |
| CDL-014 | ADR-0008 / NodeValueTrack | Path-level marginal contribution method | ratified | local delta, counterfactual path-lift, market-only proxy | counterfactual path-lift | replayable counterfactual harness |
| CDL-015 | ADR-0008 / NodeValueTrack | Implementation order lock (refactor avoidance) | ratified | ad-hoc order, dependency-ordered sequence, strict phase gate | strict phase gate | ratification plan + master plan sequencing |
| CDL-019 | ADR-0008 / NodeValueTrack | Multiplier-governance surface: resolve relationship between flat Genesis constant (1.2x), refutation-profitability invariant floor, and eventual dynamic ranking-based multiplier mechanism | open | flat Genesis constant only, governed constant + invariant floor, governed constant + dynamic ranking mechanism | governed constant + invariant floor (dynamic ranking deferred) | multiplier policy contract update, invariant regression coverage, governance migration plan |

## Scoped Ratification Record (Phase 993)

The following decision IDs were ratified in the Phase 993 governance conflict-set closure:

- `CDL-003`: selected `trigger-based sunset`
- `CDL-004`: selected `hard caps + public reporting`
- `CDL-005`: selected `cap+trajectory+guardrails`
- `CDL-006`: selected `multi-body checks`
- `CDL-008`: selected `split-by-domain`
- `CDL-009`: selected `signature-badge+eligibility rules`
- `CDL-010`: selected `pseudonymous attestations`

Conflict-cluster mapping and rationale record:
- `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`

## Scoped Ratification Record (Phase 215)

The following decision IDs were ratified in the Phase 215 node-value/governance ratification evidence closure:

- `CDL-011`: selected `balanced composite`
- `CDL-012`: selected `usage+freshness`
- `CDL-013`: selected `decay-non-genesis-only`
- `CDL-014`: selected `counterfactual path-lift`
- `CDL-015`: selected `strict phase gate`

Ratification evidence package:
- `docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md`

## Scoped Remediation Record (Phase 227)

The following decision IDs remain `open` and received bounded remediation-contract notes in Phase 227:

- `CDL-001`: remediation scope lock published in `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`
- `CDL-002`: remediation scope lock published in `docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md`
- `CDL-007`: remediation scope lock published in `docs/specs/ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md`

Phase-227 package record:
- `docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md`

Status mutation rule for this scoped record:
- No Phase-227 status promotion is applied; `CDL-001`, `CDL-002`, and `CDL-007` remain `open` until a later ratification phase proves closure criteria.

## Scoped Queue Entry Record (Phase 230 Preparation)

- `CDL-019` created from Phase-229 carry-forward debt.
- status: `open`
- description: "Multiplier-governance surface: resolve relationship between flat Genesis constant (1.2x), refutation-profitability invariant floor, and eventual dynamic ranking-based multiplier mechanism"
- action: `decision_log`
- phase identified: `229`

## Conflict Notes

- Historical sources include both high-level ideals and implementation-era tactical discussion. Tactical excerpts are not automatically constitutional.
- Clauses move to ratified state only when represented as explicit normative language and tied to concrete implementation or governance controls.

## Promotion Rule

A decision may be marked `ratified` only when:

1. It has source citations, and
2. It has a chosen option with rationale, and
3. It has concrete implementation impact listed, and
4. It has at least one verification artifact (test/spec check).
