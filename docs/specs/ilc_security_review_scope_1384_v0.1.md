# ILC Security Review Scope Record - Phase 1384 v0.1

**Phase:** 1384  
**Date:** 2026-05-18  
**Status:** SCOPE RECORDED  
**Authority:** NON-SENSITIVE documentation and planning alignment only

```text
security_review_scope_recorded_phase_1384
audit_scope_bft_safety_economic_surfaces_high_001
phase_1387_requires_project_authority_security_disposition
```

## 1. Purpose

This record replaces the earlier commercial-audit-firm engagement requirement
for Window 1369-1390 with a project-authority security review path. It records
the review scope and the Phase 1387 gate requirement, but it does not conduct
the review and does not close any HIGH-severity finding.

Commercial external audit firm engagement is not required and is not planned for
this window. The review path is:

1. AI-assisted structured security review using a frontier LLM.
2. Open source community security contributions after the repository becomes
   public.
3. Internal ongoing review under ILC coding security standards and phase
   guardrails.

Rationale: commercial audit engagement is not viable under current project
funding constraints and operator anonymity requirements. The project remains on
an open source path, so community review is a durable supplement once publication
is authorized. This relaxation removes the commercial-report requirement only;
it does not relax the substantive security gate.

## 2. Scope

Phase 1387 must confirm coverage or disposition for all of the following review
surfaces:

| Surface | Review boundary |
| --- | --- |
| `ilc_consensus/` BFT safety | Validator quorum safety, certificate construction, equivocation resistance, epoch checkpoint handling, consensus networking, fast-path execution, validator key handling, and settlement handoff code. |
| `ilc_core/` economic surfaces | Ledger, epoch, reward, fee, treasury, claimability, conversion, exact numeric, settlement verification, governance-weight, and production bridge surfaces that can affect ECU, ILC, stake, reward, claimability, or settlement state. |
| HIGH-001 defense | Phase 1359 log-layer defense, Phase 776 Rust validator log hygiene, non-loopback deployment verification, and the remaining sender-privacy non-claim boundary. |

The scope token for this combined review boundary is:

```text
audit_scope_bft_safety_economic_surfaces_high_001
```

## 3. HIGH-001 Current Posture

Phase 1359 records `high_001_log_redaction_runtime_phase_1359.v0.1`,
`sender_privacy_claim_blocker_cleared_phase_1359`, and
`mixing_framework_not_activated_production_phase_1359`.

Current posture:

- The Python AgentID log-redaction runtime exists at
  `ilc_core/identity/log_redaction_runtime.py`.
- Known Python plaintext AgentID logging sites were remediated in Phase 1359.
- Rust validator plaintext AgentID log hygiene was reverified from Phase 776.
- The transfer-mixing framework remains default-off and not production
  activated.
- Full sender privacy remains unclaimed because structural hosted-query and
  epoch-lineage privacy gaps remain outside Phase 1359.

Phase 1387 must still verify HIGH-001 defense in a non-loopback deployment. This
Phase 1384 scope record does not satisfy that verification.

## 4. Phase 1387 Gate Requirement

Phase 1387 requires a project-authority security disposition document for every
known HIGH-severity finding in the scoped surfaces above.

The disposition document must explicitly mark each known HIGH finding as one of:

| Disposition | Required content |
| --- | --- |
| Closed | Evidence that the finding is fixed or no longer applicable, plus verification scope. |
| Accepted | Rationale for accepting the residual risk and the exact authority under which the risk is accepted. |
| Deferred | Rationale, bounded carry-forward scope, blocking or non-blocking status, and the later phase or gate that owns closure. |

The required gate token is:

```text
phase_1387_requires_project_authority_security_disposition
```

The Phase 1387 security disposition is not the same as this Phase 1384 scope
record. `security_review_scope_recorded_phase_1384` is an input to Phase 1387,
not a pass condition by itself.

## 5. AI-Assisted Review Obligation

Before Phase 1387 can pass, the project must conduct or ingest a structured
security review that covers the scoped surfaces. For the AI-assisted path, the
review artifact must at minimum record:

- model or review tool identity at the level appropriate for reproducibility,
- reviewed repository commit,
- files and surfaces reviewed,
- questions or prompts used for BFT safety and economic-surface review,
- findings classified by severity,
- false-positive or duplicate disposition rationale,
- project-authority disposition for every HIGH-severity finding.

Community contributions received after publication may supplement this record,
but absence of public community reports does not itself close the Phase 1387
gate.

## 6. Non-Authorization

Phase 1384 does not authorize commercial audit spending, public repository
publication, public package publication, public RC claim, public launch claim,
public claimability activation, public verifier API activation, public serving,
wallet withdrawal, wallet transfer, wallet spend, ECU minting, ILC settlement,
live ECU transfer routing, production transfer mixing, sender-privacy claim,
production validator deployment, production governance execution, CDL mutation,
Genesis or Atlas mutation, release signing, counsel approval, or legal
conclusion.

## 7. Forward Routing

Phase 1385 remains the next planned phase. Phase 1387 remains the pre-activation
hardening gate and must fail closed unless the project-authority disposition
condition is satisfied for every known HIGH-severity finding.
