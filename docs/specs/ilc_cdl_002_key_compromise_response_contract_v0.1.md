# ILC CDL-002: Credential Supersession and Compromise Signaling v0.2

Status: ratified; Phase 1573av constitutional reframe applied
Date: 2026-02-18
Amended: 2026-07-10 (Phase 1573av)
Related decision: `CDL-002`
Related artifacts:
- `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/phases/phase_1573av_cdl002_credential_supersession_reframe_walkthrough.md`

## 0. Canonical ILC Identity and Root Key Principle (Phase 1573av amendment)

Root identity keys are not revocable. They may only be forward-superseded through a recovery or succession policy that was explicitly committed on-graph before the supersession event and whose activation rules are verifiable from on-graph evidence. Bad behavior from a root key is handled organically by juries, reputation, routing refusal, pruning, and temporal validity, not by cancellation.

Later governance may judge, downgrade, route around, or prune an agent whose root key is compromised. It may not invent a recovery path for an agent that did not precommit one.

## 0a. Key-Class Distinction

| Key class | Canonical treatment |
|-----------|-------------------|
| `root_identity_key` | Not revocable. Only forward-supersedable through precommitted on-graph recovery/succession policy with verifiable activation rules. |
| `delegated_signer` | Revocable/rotatable by the root identity or its precommitted policy. |
| `session / contact / invite / KEM credential` | May expire, rotate, or be refused under local rules. |
| `compromise_claim` | Evidence node only. No automatic authority change. |
| `coercion_signal` | Duress metadata and governance evidence only. No automatic authority change. |
| `bad_root_key_behavior` | Handled organically: juries, reputation decay, routing refusal, graph pruning, temporal validity. Not by administrative cancellation. |

## 0b. Delegated-Signer Scope Boundary

The Phase-227 remediation language below is retained as historical and operational
delegated-signer machinery. It must not be read as a doctrine for root identity
key revocation. The `revoke` and `recover` state names in CDL-001 signer-lineage
machinery apply to delegated/operational signer lineage state, not cancellation
of an agent's root identity key or on-graph voice.

`coercion_signal`, `custody_loss`, and `crypto_compromise` are evidence and
response triggers for default-off delegated signer workflows. They do not
automatically alter root identity authority.

## 1. Blocker statement

Phase-226 rubric verdict for `CDL-002` was `genesis_blocker` because missing
delegated credential response controls created key-loss and malicious delegated
signer continuation risk.

## 2. Remediation boundary (locked in Phase 227)

`CDL-002` delegated-signer remediation is bounded to a deterministic
compromise-response contract with five required elements:

1. **Trigger contract**
   - compromise states: `suspected`, `confirmed`
   - trigger classes: signer anomaly, custody-loss report, coercion signal, cryptographic compromise signal
2. **Immediate containment contract**
   - required actions: `freeze_authority`, `quarantine_lineage`, `suspend_new_canonical_signatures`
3. **Delegated signer supersession contract**
   - required actions: `revoke_compromised_delegated_signer`,
     `register_replacement_lineage`, `publish_recovery_attestation`
   - applies only to delegated signer lineage, not root identity keys
4. **Genesis-specific coercion/recovery evidence clause**
   - explicit path for coercion scenarios where delegated signer control is at risk
   - coercion evidence may support governance, routing refusal, reputation impact,
     or delegated credential supersession, but does not grant root identity
     cancellation power
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

Until runtime compromise controls are implemented, delegated-signer response
remains policy-constrained and manual rather than automated at protocol runtime.

## 6. Bounded status for Genesis packaging

bounded_for_genesis_packaging: yes

## 7. Phase 1573av Amendment Record

Phase 1573av renames CDL-002 from "Emergency key compromise response" to
"Credential Supersession and Compromise Signaling" in the constitutional
decision log. It ratifies the key-class distinction above and scopes
`ilc_core/security/key_compromise_runtime.py` to default-off delegated signer
machinery only.

This amendment does not execute recovery, revoke a root identity key, supersede
a root identity key, activate runtime guards, authorize public RC, or publish a
public mirror.
