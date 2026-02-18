# ILC Phase 226 Open-CDL Security Triage v0.1

Status: Phase-226 triage artifact  
Date: 2026-02-18  
Scope: `CDL-001`, `CDL-002`, `CDL-007`

## 1. Purpose

Apply the locked Genesis-blocker rubric to open constitutional security decisions and produce deterministic verdicts with explicit Phase-227 execution mode.

Rubric (locked by sequence spec):
1. first-run breakage without missing capability,
2. key/data loss risk,
3. exploitable rollback/state-corruption risk,
4. no viable mitigation path/workaround.

A decision is `genesis_blocker` if any one rubric criterion is true.

## 2. CDL-001 Triaging Record

### 2.1 Current scope summary
`CDL-001` currently tracks canonical signer lineage definition, with required artifacts still open (key registry spec update and validator tests).

### 2.2 Scope adequacy check (MG-03)
Compared to MG-03 expanded scope expectations, current scope is incomplete for trust-root coverage unless explicitly extended to include: key hierarchy, lifecycle/rotation/recovery, and canonical authority linkage.

### 2.3 Evidence anchors
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (`CDL-001` row)
- `docs/specs/ilc_constitutional_context_audit_response_v0.1.md` (MG-03)
- `docs/research/constitution_dredge_matrix_v0.2.md` (`raw-009224`, `raw-019035`, `raw-012745`, `raw-012748`)

### 2.4 Rubric evaluation

| Criterion | Result | Notes |
|---|---|---|
| 1. first-run breakage | fail | Current package can run local scoring/conformance flows without full signer-lineage rollout. |
| 2. key/data loss risk | pass | Incomplete trust-root signer lineage leaves high-impact key misuse/identity ambiguity risk for canonical operations. |
| 3. exploitable rollback/state-corruption risk | pass | Undefined signer authority boundaries increase risk of disputed canonical authority transitions. |
| 4. no viable mitigation | fail | Temporary mitigations exist (non-canonical/test-signing boundaries and explicit deployment scope limits). |

verdict: genesis_blocker

### 2.5 Required remediation scope if blocker
- Define signer-lineage model surface (hierarchy + lifecycle + rotation/recovery).
- Define canonical-authority linkage rules for signer acceptance/rejection.
- Add validator-level conformance checks for lineage constraints.

## 3. CDL-002 Triaging Record

### 3.1 Current scope summary
`CDL-002` tracks emergency key compromise response, with incident policy text and integration tests still open.

### 3.2 Scope adequacy check (MG-04)
Compared to MG-04 expanded scope expectations, current scope must explicitly include Genesis-specific coercion/compromise pathways and recovery controls.

### 3.3 Evidence anchors
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (`CDL-002` row)
- `docs/specs/ilc_constitutional_context_audit_response_v0.1.md` (MG-04)
- `docs/research/constitution_dredge_matrix_v0.2.md` (`raw-006766`, `raw-012565`, `raw-013401`)

### 3.4 Rubric evaluation

| Criterion | Result | Notes |
|---|---|---|
| 1. first-run breakage | fail | Local deterministic scoring/reward tooling can run without emergency key-response machinery. |
| 2. key/data loss risk | pass | Missing compromise response policy creates unbounded key-loss and authority-loss risk once canonical keys are operational. |
| 3. exploitable rollback/state-corruption risk | pass | Lack of explicit compromise-response path increases exploit surface for malicious key continuation. |
| 4. no viable mitigation | fail | Short-term mitigation exists via constrained non-canonical deployment scope and no production signer authority exposure. |

verdict: genesis_blocker

### 3.5 Required remediation scope if blocker
- Define compromise detection triggers and authority freeze/revoke pathway.
- Define Genesis-specific coercion and recovery controls.
- Add incident-policy and integration-test contract for compromise events.

## 4. CDL-007 Triaging Record

### 4.1 Current scope summary
`CDL-007` tracks rollback resistance baseline, currently open with required channel spec and negative tests.

### 4.2 Evidence anchors
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (`CDL-007` row)
- `docs/specs/ilc_constitutional_context_audit_response_v0.1.md` (SG-05)
- `docs/research/constitution_dredge_matrix_v0.2.md` (`raw-002601`)
- `ilc_core/ledger/canon_bundle_key_registry_channel.py`

### 4.3 Rubric evaluation

| Criterion | Result | Notes |
|---|---|---|
| 1. first-run breakage | fail | Current package workflows can execute without full protocol-level rollback baseline closure. |
| 2. key/data loss risk | pass | Ambiguous rollback/clawback baseline can cause unrecoverable ledger state divergence and payout integrity risk. |
| 3. exploitable rollback/state-corruption risk | pass | Incomplete rollback baseline creates room for replay/supersession ambiguity across canonical history boundaries. |
| 4. no viable mitigation | fail | Partial channel-level protections provide interim mitigation but not full protocol-level closure. |

verdict: genesis_blocker

### 4.4 Required remediation scope if blocker
- Lock protocol-level rollback supersession and clawback semantics.
- Add negative-path tests for rollback abuse and conflicting supersession paths.
- Align channel-level protections with protocol-level baseline contract.

## 5. Phase 227 Execution Mode

Because at least one triaged item is `genesis_blocker` (all three are), Phase 227 mode is:

- remediation_required

## 6. Non-ratification statement

This artifact performs triage and disposition only. It does not mutate CDL status values and does not ratify any open decision-log row.
