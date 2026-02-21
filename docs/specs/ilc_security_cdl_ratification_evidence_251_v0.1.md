# ILC Security CDL Ratification Evidence 251 v0.1

Status: Ratification evidence (Phase 251)
Date: 2026-02-21
Ratification lane: G8 Constitution Cluster A
CDLs ratified: CDL-001, CDL-002, CDL-007
Ceremony protocol reference: `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md` §6

## 1. Scope and batch ratification basis

This document records the ratification evidence for the batch closure of `CDL-001`, `CDL-002`, and `CDL-007`.

Batch ratification basis per Section 6.5 of the ceremony protocol: all three CDLs share the same evidence chain and gate lineage — each was scoped under the Phase-227 remediation package, implemented under the Phase 240-244 security-runtime sequence, validated by the same Phase-244 composed gate, and verified for cross-CDL interaction coherence by the same test suite.

Boundary statement: No runtime implementation was introduced in this ratification phase. This document and the associated decision-log mutations are the sole outputs of Phase 251.

---

## 2. CDL-001: Canonical signer lineage definition

### 2.1 Evidence table

| Evidence field | Reference |
| --- | --- |
| Contract document | `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md` |
| Contract scope | Signer hierarchy (canonical_root_key, authority_recovery_key, operational_signer_key); lifecycle event contract (active/rotated/revoked/recovered); canonical authority linkage; auditability contract |
| Chosen option | `lineage+timelock` (per decision-log current candidate) |
| Implementation phase | Phase 241 |
| Implementation module | `ilc_core/security/signer_lineage_runtime.py` |
| Unit test file | `tests/test_cdl_001_signer_lineage_runtime.py` |
| Unit test pass count | 8 passed |
| Phase-244 gate | `tools/run_phase_244_security_runtime_gate.py` — PASS |
| Cross-CDL interaction tests | `tests/test_security_runtime_cross_cdl_interactions_244.py` — 4 passed |
| Cross-CDL participation | CDL-001 signer lineage participates in: `test_compromise_revocation_then_verification_rejection`, `test_rollback_against_revoked_signer_is_rejected`, `test_recover_then_valid_future_supersession_is_accepted`, `test_validate_rejects_revoked_signer_unauthorized_supersession_path` |
| Phase-248 coherence check | `docs/specs/ilc_integration_coherence_report_248_v0.1.md` §4 — CDL-001 alignment confirmed |
| Remediation package | `docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md` §CDL-001 |
| bounded_for_genesis_packaging | yes |

### 2.2 Formal ratification statement — CDL-001

`CDL-001` (Canonical signer lineage definition) is hereby ratified with the following evidence chain:

1. The Phase-227 remediation contract (`ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`) defined the full signer hierarchy, lifecycle event states, canonical authority linkage, and auditability contract.
2. Phase 241 implemented the runtime module `ilc_core/security/signer_lineage_runtime.py` satisfying all four contract elements.
3. Eight unit tests in `tests/test_cdl_001_signer_lineage_runtime.py` pass, covering: trust-root chain validation (accept and reject paths), revoked-lineage rejection, full lifecycle-transition coverage (active → rotated → revoked → recovered), append-only replayable transition log, and three state-gating tests for verify_canonical_authority.
4. The Phase-244 composed gate (`run_phase_244_security_runtime_gate.py`) passes, confirming integration of CDL-001 runtime within the full security-runtime suite.
5. Four cross-CDL interaction tests in `tests/test_security_runtime_cross_cdl_interactions_244.py` pass, confirming CDL-001 signer lineage interacts correctly with CDL-002 (compromise/revocation) and CDL-007 (rollback resistance) runtime modules.
6. `docs/specs/ilc_integration_coherence_report_248_v0.1.md` §4 confirmed CDL-001 alignment through Phase 248.

Chosen option: `lineage+timelock`
Ratification basis: all four promotion criteria satisfied (source citations, chosen option with rationale, concrete implementation impact, verification artifacts).

---

## 3. CDL-002: Emergency key compromise response

### 3.1 Evidence table

| Evidence field | Reference |
| --- | --- |
| Contract document | `docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md` |
| Contract scope | Trigger contract (suspected/confirmed states, four trigger classes); immediate containment (freeze, quarantine, suspend); revocation and replacement; Genesis-specific coercion/recovery clause; incident audit contract |
| Chosen option | `revoke+grace period` (per decision-log current candidate) |
| Implementation phase | Phase 242 |
| Implementation module | `ilc_core/security/key_compromise_runtime.py` |
| Unit test file | `tests/test_cdl_002_key_compromise_runtime.py` |
| Unit test pass count | 8 passed |
| Phase-244 gate | `tools/run_phase_244_security_runtime_gate.py` — PASS |
| Cross-CDL interaction tests | `tests/test_security_runtime_cross_cdl_interactions_244.py` — 4 passed |
| Cross-CDL participation | CDL-002 compromise/revocation participates in: `test_compromise_revocation_then_verification_rejection`, `test_rollback_against_revoked_signer_is_rejected`, `test_recover_then_valid_future_supersession_is_accepted` |
| Phase-248 coherence check | `docs/specs/ilc_integration_coherence_report_248_v0.1.md` §4 — CDL-002 alignment confirmed |
| Remediation package | `docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md` §CDL-002 |
| bounded_for_genesis_packaging | yes |

### 3.2 Formal ratification statement — CDL-002

`CDL-002` (Emergency key compromise response) is hereby ratified with the following evidence chain:

1. The Phase-227 remediation contract (`ilc_cdl_002_key_compromise_response_contract_v0.1.md`) defined the trigger contract, containment contract, revocation and replacement contract, Genesis coercion/recovery clause, and incident audit contract.
2. Phase 242 implemented the runtime module `ilc_core/security/key_compromise_runtime.py` satisfying all five contract elements.
3. Eight unit tests in `tests/test_cdl_002_key_compromise_runtime.py` pass, covering: all four trigger classes (signer_anomaly, custody_loss, coercion_signal, crypto_compromise), containment-action strict ordering, incident-record containment emission, confirmed-compromise revoke-then-recover sequence, and deterministic reason code with recovery attestation.
4. The Phase-244 composed gate (`run_phase_244_security_runtime_gate.py`) passes, confirming integration of CDL-002 runtime within the full security-runtime suite.
5. Four cross-CDL interaction tests in `tests/test_security_runtime_cross_cdl_interactions_244.py` pass, confirming CDL-002 compromise/revocation interacts correctly with CDL-001 (lineage verification) and CDL-007 (rollback resistance) runtime modules.
6. `docs/specs/ilc_integration_coherence_report_248_v0.1.md` §4 confirmed CDL-002 alignment through Phase 248.

Chosen option: `revoke+grace period`
Ratification basis: all four promotion criteria satisfied (source citations, chosen option with rationale, concrete implementation impact, verification artifacts).

---

## 4. CDL-007: Rollback resistance baseline

### 4.1 Evidence table

| Evidence field | Reference |
| --- | --- |
| Contract document | `docs/specs/ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md` |
| Contract scope | Supersession event contract (finalization_state=rolled_back token); clawback declaration contract (clawback_required / clawback_not_required); conflict rejection contract (invalid duplicate supersession chains, replay rejection); channel-to-protocol alignment contract |
| Chosen option | `seq+hash+signed checkpoints` (per decision-log current candidate) |
| Implementation phase | Phase 243 |
| Implementation module | `ilc_core/security/rollback_resistance_runtime.py` |
| Unit test file | `tests/test_cdl_007_rollback_resistance_runtime.py` |
| Unit test pass count | 7 passed |
| Phase-244 gate | `tools/run_phase_244_security_runtime_gate.py` — PASS |
| Cross-CDL interaction tests | `tests/test_security_runtime_cross_cdl_interactions_244.py` — 4 passed |
| Cross-CDL participation | CDL-007 rollback resistance participates in: `test_rollback_against_revoked_signer_is_rejected`, `test_recover_then_valid_future_supersession_is_accepted`, `test_validate_rejects_revoked_signer_unauthorized_supersession_path` |
| Phase-248 coherence check | `docs/specs/ilc_integration_coherence_report_248_v0.1.md` §4 — CDL-007 alignment confirmed |
| Remediation package | `docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md` §CDL-007 |
| bounded_for_genesis_packaging | yes |

### 4.2 Formal ratification statement — CDL-007

`CDL-007` (Rollback resistance baseline) is hereby ratified with the following evidence chain:

1. The Phase-227 remediation contract (`ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md`) defined the supersession event contract, clawback declaration contract, conflict rejection contract, and channel-to-protocol alignment contract.
2. Phase 243 implemented the runtime module `ilc_core/security/rollback_resistance_runtime.py` satisfying all four contract elements.
3. Seven unit tests in `tests/test_cdl_007_rollback_resistance_runtime.py` pass, covering: supersession event token validation, finalization-state rejection for non-rolled-back states, clawback policy acceptance for both allowed tokens, invalid clawback policy rejection, replay identifier rejection, and conflicting supersession chain rejection.
4. The Phase-244 composed gate (`run_phase_244_security_runtime_gate.py`) passes, confirming integration of CDL-007 runtime within the full security-runtime suite.
5. Four cross-CDL interaction tests in `tests/test_security_runtime_cross_cdl_interactions_244.py` pass, confirming CDL-007 rollback resistance interacts correctly with CDL-001 (lineage verification) and CDL-002 (compromise/revocation) runtime modules.
6. `docs/specs/ilc_integration_coherence_report_248_v0.1.md` §4 confirmed CDL-007 alignment through Phase 248.

Chosen option: `seq+hash+signed checkpoints`
Ratification basis: all four promotion criteria satisfied (source citations, chosen option with rationale, concrete implementation impact, verification artifacts).

---

## 5. Batch ratification summary

| CDL | Decision topic | Chosen option | Status transition | Ratified phase | Evidence sections |
| --- | --- | --- | --- | --- | --- |
| CDL-001 | Canonical signer lineage definition | lineage+timelock | open → ratified | 251 | §2.1, §2.2 |
| CDL-002 | Emergency key compromise response | revoke+grace period | open → ratified | 251 | §3.1, §3.2 |
| CDL-007 | Rollback resistance baseline | seq+hash+signed checkpoints | open → ratified | 251 | §4.1, §4.2 |

Shared gate lineage confirming batch eligibility:
- Phase-227 remediation package: common scope boundary for all three CDLs.
- Phases 241-243: runtime implementations for each CDL under the shared Phase 240-244 security-runtime sequence.
- Phase-244 gate (`run_phase_244_security_runtime_gate.py`): composed validation covering all three runtime modules and cross-CDL interactions.
- Phase-248 coherence report: cross-reference integrity confirmed for all three CDLs.

---

## 6. Non-goal boundary statement

This ratification phase introduces no runtime implementation changes. The following are unchanged:
- All `ilc_core/` modules.
- All contract source documents (`ilc_cdl_001/002/007_*_contract_v0.1.md`).
- All CDLs outside CDL-001, CDL-002, CDL-007 (CDL-019, CDL-025 through CDL-031, CDL-032, CDL-033 remain unchanged).
- No new runtime test logic beyond verification tests in `tests/test_security_cdl_ratification_251.py`.
