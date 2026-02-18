# ILC Phase 227 Blocker Remediation Package v0.1

Status: Phase-227 remediation package artifact
Date: 2026-02-18
Inputs:
- `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
- `docs/specs/ilc_phase_226_decision_log_backlog_queue_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 1. Purpose

Convert Phase-226 open-CDL Genesis blockers (`CDL-001`, `CDL-002`, `CDL-007`) into bounded remediation contracts with deterministic acceptance checks for Genesis packaging scope lock.

## 2. CDL-001 remediation package

- blocker statement: Phase-226 rubric verdict `genesis_blocker` due to signer-lineage trust-root ambiguity and key-risk surface.
- remediation boundary: defined by `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md` (hierarchy, lifecycle, canonical authority linkage, auditability).
- deterministic acceptance checks:
  1. `CDL-001` contract spec exists.
  2. `CDL-001` contract spec includes hierarchy/lifecycle/linkage/auditability sections.
  3. Decision-log Phase-227 notes reference the `CDL-001` contract while keeping status `open`.
- deferred implementation list: runtime key-registry enforcement, signing infrastructure automation, and quorum recovery wiring.
- residual risk: signer misuse remains policy-bounded until runtime enforcement is shipped.
- bounded_for_genesis_packaging: yes

## 3. CDL-002 remediation package

- blocker statement: Phase-226 rubric verdict `genesis_blocker` due to missing compromise-response and recovery baseline.
- remediation boundary: defined by `docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md` (trigger states, containment actions, revocation/replacement, Genesis coercion clause, incident auditability).
- deterministic acceptance checks:
  1. `CDL-002` contract spec exists.
  2. `CDL-002` contract spec includes trigger/containment/recovery/coercion/audit tokens.
  3. Decision-log Phase-227 notes reference the `CDL-002` contract while keeping status `open`.
- deferred implementation list: runtime detectors/responders, custody telemetry, recovery drill tooling.
- residual risk: compromise handling remains manual/policy-driven until runtime integration.
- bounded_for_genesis_packaging: yes

## 4. CDL-007 remediation package

- blocker statement: Phase-226 rubric verdict `genesis_blocker` due to incomplete protocol-level rollback supersession/clawback baseline.
- remediation boundary: defined by `docs/specs/ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md` (supersession token, clawback declaration, conflict rejection, channel/protocol alignment).
- deterministic acceptance checks:
  1. `CDL-007` contract spec exists.
  2. `CDL-007` contract spec includes required rollback tokens and conflict rejection baseline.
  3. Decision-log Phase-227 notes reference the `CDL-007` contract while keeping status `open`.
- deferred implementation list: full rollback runtime orchestration and integrated clawback settlement paths.
- residual risk: rollback enforcement remains baseline-defined with partial runtime coverage only.
- bounded_for_genesis_packaging: yes

## 5. Backlog candidate disposition (Phase-226 carry-forward)

Source of truth: `docs/specs/ilc_phase_226_decision_log_backlog_queue_v0.1.md`

- genesis_blocker_candidate_total: 19
- subsumed_by_cdl_001_002_007: 19
- additional_blockers_requiring_followup: 0
- one-line disposition rationale per additional blocker (if any): none
- backlog_candidate_disposition_complete: yes

Disposition rule applied in this phase:
- Each `genesis_blocker_candidate` row from Phase-226 queue maps to one of the three security trust-root surfaces (`CDL-001`, `CDL-002`, `CDL-007`), so no new independent blocker lane is opened in Phase 227.

## 6. Aggregate package verdict

phase_227_package_verdict: bounded

## 7. Non-ratification statement

This package defines remediation boundaries only. `CDL-001`, `CDL-002`, and `CDL-007` remain `open` in Phase 227.

