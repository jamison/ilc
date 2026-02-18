# ILC CDL-002 Key Compromise Response Contract v0.1

Status: Phase-227 remediation contract (decision remains open)
Date: 2026-02-18
Related decision: `CDL-002`
Related artifacts:
- `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 1. Blocker statement

Phase-226 rubric verdict for `CDL-002` is `genesis_blocker` because missing compromise response controls create key-loss and malicious-key continuation risk.

## 2. Remediation boundary (locked in Phase 227)

`CDL-002` remediation is bounded to a deterministic compromise-response contract with five required elements:

1. **Trigger contract**
   - compromise states: `suspected`, `confirmed`
   - trigger classes: signer anomaly, custody-loss report, coercion signal, cryptographic compromise signal
2. **Immediate containment contract**
   - required actions: `freeze_authority`, `quarantine_lineage`, `suspend_new_canonical_signatures`
3. **Revocation and replacement contract**
   - required actions: `revoke_compromised_keys`, `register_replacement_lineage`, `publish_recovery_attestation`
4. **Genesis-specific coercion/recovery clause**
   - explicit path for coercion scenarios where signer identity/control is at risk
   - explicit recovery sequence that does not grant unilateral permanent privilege
5. **Incident audit contract**
   - every compromise decision must emit an auditable incident record with deterministic reason code

## 3. Deterministic acceptance checks

This remediation contract is accepted only if all checks are true:

1. This artifact defines all trigger classes and response actions in Section 2.
2. The remediation package artifact (`docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md`) includes a `CDL-002` section with required boundary/check/defer/risk fields and bounded token.
3. Decision-log Phase-227 remediation notes explicitly reference this contract while keeping `CDL-002` status `open`.
4. Phase-227 gate/tests validate artifact presence and required tokens.

## 4. Deferred implementation list (explicit)

Deferred beyond this docs-contract phase:
- runtime compromise detectors and responder automation,
- signer-custody telemetry and alert pipeline,
- production recovery drills with signing quorum infrastructure,
- operational keybook tooling and emergency command controls.

## 5. Residual risk after bounded mitigation

Until runtime compromise controls are implemented, response remains policy-constrained and manual rather than automated at protocol runtime.

## 6. Bounded status for Genesis packaging

bounded_for_genesis_packaging: yes

