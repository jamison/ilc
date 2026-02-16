# Glossary Term Elevation Matrix v0.1

Status: Draft planning artifact  
Date: 2026-02-16  
Scope: `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md` Section 6.1 ("Concepts & Mechanisms")

## 1. Purpose

Evaluate each glossary concept term using the same constitutional gating approach already used for raw-ledger triage:
- constitutional fit and ratifiability,
- architecture and implementation alignment,
- leverage and agent-pull timing,
- roadmap lane assignment (`Now`, `Near`, `Later`, `Reject`).

This matrix is intended to prevent useful ideas from being silently stranded as "reference only".

## 2. Term-by-Term Elevation Decisions

| Term | Current Corpus State | Canonical Mapping / Alias | Gate Outcome | Proposed Lane | Target Layer | Evidence Anchors | Recommended Next Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Context Packs | Reviewed, partial, promote_guardrail | `Capsule` + reproducible docs bundle discipline | Promote as canonical-adjacent | Near | L1/L2 | `raw-016125`; master plan context-pack notes | Spec paragraph tying context-pack reproducibility to capsule manifest checks |
| Court Certification (7+1) | Deferred, conflict, decision_log | Multi-body governance checks + VRF outsider seat | Keep, unresolved governance conflict | Near | L2/L3 | `raw-012616`, `raw-012647`, `raw-012660`, `raw-012888`, `raw-012475`, `raw-012515` | Governance anti-capture spec + conformance tests (shortlist rank 8) |
| Epistemic Lineage Anchoring | Reviewed, partial, promote_guardrail | Canon lineage immutability and replay stability | Promote | Now | L0/L1 | `raw-006018`; rollback/canon clauses | Add explicit lineage-hardening conformance checks |
| Epistemological Purism | Discarded, out_of_scope, drop | Historical framing only | Keep historical, do not promote | Reject | N/A | `raw-005525` | None; keep as historical concept |
| Evidence Submission | Reviewed, partial, promote_clause | Challenge evidence validity requirements | Promote | Now | L1 | `raw-008957` | Challenge evidence schema + validator tests |
| Genesis Attention Broadcast (GAB) | Deferred, missing, decision_log | Founder soft-power vote trigger | Keep pending ratification | Near | L2/L3 | `raw-012589`, `raw-012605`, `raw-012640` | Founder governance policy package with bounded powers |
| Graph Anchoring | Reviewed, partial, promote_guardrail | Opaque-to-public lineage anchor requirement | Promote as guardrail | Now | L1 | `raw-005533` | Schema/validator checks for minimum public anchor linkage |
| Intelligent Labor | Already central mission concept | PoIL economic work unit framing | Already canonical in direction | Now | L0 | Master principles + PoIL references | No rename required; keep in canon glossary as primary concept |
| Lawfulness | Reviewed, missing, promote_guardrail | Legal/jurisdictional governance subgraphs | Keep, defer implementation depth | Later | L2/L3 | `raw-011599`, `raw-011600` | Governance/legal subgraph ADR + policy-loading boundary text |
| Minimal Theoretic Core | Deferred, missing, decision_log | Fixed-core minimalism principle | Keep principle, defer mechanization | Near | L0/L1 | `raw-001366` | Ratify as constitutional text plus L0 boundary constraints |
| Namespace Deprecation Protocol | Deferred, missing, decision_log | Namespace quarantine/archive governance process | Keep, needs formal design | Later | L2/L3 | `raw-008655` | Namespace deprecation policy spec + migration/compat tests |
| Passive Observation Feeds | Discarded, out_of_scope, drop | Replaced by star-map/routing artifact framing | Do not promote as primitive | Reject | N/A | `raw-018884` | None; retain as dropped/historical |
| Philosophical Relativism | Reviewed, partial, promote_guardrail | Fork-policy cautionary framing | Keep as explanatory principle | Later | L2/L3 | `raw-009939` | Optional appendix text in fork-policy docs |
| Protocol Critical | Reviewed, partial, promote_clause | Protocol-critical surface classification | Promote | Now | L0/L1 | `raw-015983` | Protocol-critical registry/checklist tied to release gates |
| Provenance | Present in principles; reviewed promote_clause rows | Signature/time-stamped lineage and auditability | Promote (already strongly aligned) | Now | L1 | `raw-009693`, principle section 25 | Tighten provenance conformance tests at ledger/report boundaries |
| Quality Floor | Reviewed, missing, todo | Minimum quality threshold for mint eligibility | Keep, incomplete economics implementation | Near | L1/L2 | `raw-009689` | Economics spec clause + reward-path tests for low-quality zeroing |
| Rate of Adaptation | Discarded, out_of_scope, drop | Ecosystem-level objective, not primitive | Keep as strategic metric, not core primitive | Reject | N/A | `raw-011585` | None in constitutional core |
| Receipts Schema | Reviewed, missing, promote_guardrail; leverage rank #2 | `Receipt` canonical primitive and payout/dispute envelope | Promote (high priority) | Now | L1 | `raw-012308`; leverage ranking top cluster | Receipts schema ratification + code/tests for evidence/payout trails |
| Spec Oracle | Reviewed, partial, promote_guardrail | SIM behavior replication requirement for new implementations | Promote as guardrail | Now | L1 | `raw-018145` | Spec-oracle conformance harness in CI |
| Task Routing Protocol (TRP) | Term entry partly dropped in one governance row; principle already exists | Existing canonical Principle 12 routing framework | Already canon-adjacent under established name | Now | L1/L2 | Master principles section 12; `raw-011749` mixed status | Keep canonical wording; avoid duplicate competing TRP definitions |
| Token Graph Sharding | Discarded/deprecated | Topic sharding semantic locality model | Do not promote legacy form | Reject | N/A | `raw-011567`; glossary deprecation section | Keep as deprecated alias only |
| Trusted Verifier Safeguards | Deferred, missing, todo | Fork/upgrade verifier integrity safeguards | Keep; useful but not yet ratified | Near | L2/L3 | `raw-002624` | Fork-safety/verifier safeguards subsection with tests |
| Truth Ledger | Reviewed, partial, promote_guardrail | Canon ledger of validated proofs and lineage | Promote as canonical-adjacent | Near | L1 | `raw-000483` | Align term with existing canon ledger export and verification surfaces |

## 3. Governance Conflicts (Core Set Resolved in Phase 993)

Below are the governance conflicts that previously blocked promotion of some glossary candidates. The core set was resolved in Phase 993 and mapped to ratified decision-log outcomes.

### 3.1 Conflict Rows in Constitutional Matrix (Resolved Core Set)

- `raw-012616`: mapped to ratified `CDL-006`, `CDL-003`, `CDL-004`
- `raw-012647`: mapped to ratified `CDL-006`
- `raw-012640`: mapped to ratified `CDL-003`, `CDL-004`, `CDL-010`
- `raw-012888`: mapped to ratified `CDL-006`, `CDL-008`
- `raw-012660`: mapped to ratified `CDL-006`, `CDL-008`, `CDL-009`
- `raw-012615`: mapped to ratified `CDL-006`, `CDL-004`
- `raw-012645`: mapped to ratified `CDL-006`, `CDL-009`

### 3.2 Constitutional Decision Log Entries (Governance-Relevant, Ratified Core Set)

- `CDL-006`: Governance override/challenge process (`ratified`, `multi-body checks`)
- `CDL-003`: Founder fade-out mechanics (`ratified`, `trigger-based sunset`)
- `CDL-004`: Founder operational caps (`ratified`, `hard caps + reporting`)
- `CDL-005`: Issuance/cap constitutional wording (`ratified`, `cap+trajectory+guardrails`)
- `CDL-008`: Fixed core vs policy-loaded layer boundary (`ratified`, `split-by-domain`)
- `CDL-009`: Fork legitimacy/user signaling (`ratified`, `signature-badge+eligibility rules`)
- `CDL-010`: Pseudonymity/accountability balance (`ratified`, `pseudonymous attestations`)

### 3.3 Immediate Practical Effect

- `Court Certification` and related `7+1` semantics remain `Near` candidates but are no longer blocked by the core unresolved-governance cluster.
- Promotion still requires term-specific spec and verification artifacts per promotion rules.

Ratification mapping artifact:
- `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`

## 4. Recommended Sequencing

1. Close constitutional `Now` conformance work first (`CONST-001..006` and guardrails).
2. Ratify governance conflict package (`CDL-006` plus adjacent founder/governance entries).
3. Promote `Court Certification`/anti-capture governance terms from glossary candidate to canonical-adjacent spec language.
4. Stage deeper L2/L3 governance expansions after core ratification and conformance are green.

## 5. Promotion Rule Reminder

A term should not move from reference candidate to canonical unless all are true:
- stable definition,
- spec/ADR anchor,
- implementation anchor,
- deterministic verification anchor,
- phase traceability in walkthrough/STATUS.
