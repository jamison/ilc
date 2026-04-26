# ILC Integration Coherence Report 838 — CDL-069 PQ Identity and Epoch Endorsement Ratification

**Phase:** 838k
**Date:** 2026-04-26
**Window:** 838 (CDL-069 ratification lane)

`cdl_069_ratification_838_coherence_published`
`cdl_069_ratified_recorded_in_coherence_838`
`phase_838_runtime_audit_two_rounds_complete`
`phase_838_test_count_213_all_pass`

## 1. Purpose

This report closes Phase 838 — the CDL-069 post-quantum identity and epoch
endorsement protocol ratification lane. It records what was delivered, what
was audited and fixed, what remains open, and where each forward obligation
sits.

## 2. Phase 838 Delivery Summary

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 838a  | CDL-069 opening — §1 scope definition | ✅ COMPLETE |
| 838b  | CDL-069 §2 protocol specification (identity derivation, endorsement packet, epoch-close attestation, temporal tier framework) | ✅ COMPLETE |
| 838c  | `epoch_endorsement_runtime.py` — validator-side cache + agent-side protocol logic | ✅ COMPLETE |
| 838d  | CDL-069 §2a blinding factor + identity derivation (Pre-image derivations locked) | ✅ COMPLETE |
| 838e  | `genesis_record_schema.py` — four-field genesis record schema + recovery transaction protocol | ✅ COMPLETE |
| 838f  | `endorsement_packet_schema.py` — endorsement packet schema + COSE_Sign1 payload construction | ✅ COMPLETE |
| 838f  | Audit round 1: 8 findings (F1–F8), all fixed, 13 regression tests added | ✅ COMPLETE |
| 838g  | Ratification planning: 14-item evidence checklist sweep (9/14 satisfied at entry) | ✅ COMPLETE |
| 838h  | Evidence items 6 + 7: minting proof chain audit + Row 5 / SIM-LEAKAGE-03 assertion | ✅ COMPLETE |
| 838i  | Evidence items 8 + 12 + 14: CDL-017 interaction, CDL-001 compatibility, temporal tier framework audit | ✅ COMPLETE |
| 838j  | Ratification readiness dossier — all 14/14 tokens satisfied | ✅ COMPLETE |
| 838j  | CDL-069 ratification evidence (Commit 1) | ✅ COMPLETE |
| 838j  | Decision log mutation — `status: open → ratified` (Commit 2) | ✅ COMPLETE |
| 838k  | Audit round 2: 9 findings (F1–F8 + D2), all fixed, 21 regression tests added | ✅ COMPLETE |

## 3. New Runtime Files

Three runtime files govern CDL-069 identity and endorsement:

| File | Version token | Tests |
|------|---------------|-------|
| `ilc_core/identity/genesis_record_schema.py` | `genesis_record_schema_838e.v0.1` | 57 (838e suite) |
| `ilc_core/identity/endorsement_packet_schema.py` | `endorsement_packet_schema_838f.v0.1` | 68 (838f suite) |
| `ilc_core/identity/epoch_endorsement_runtime.py` | `epoch_endorsement_runtime_838c.v0.1` | 88 (838c suite) |

**Total: 213 tests, 213 pass.**

All three files carry `CDL_069_DEPENDENCY = "cdl_069_opens_phase_838"`.

## 4. Audit Summary

### Round 1 (c5dc9633) — 8 findings

| ID | Severity | Finding |
|----|----------|---------|
| F1 | Critical | `ephemeral_signing_pk` entirely missing from `EpochEndorsementPacket.validate()` |
| F2 | Significant | `EpochCloseAttestation` ECU commitment fields length-only, no hex-char check |
| F3 | Significant | `is_ephemeral_key_valid` superseded-key boundary inverted — returned False unconditionally |
| F4 | Significant | `evict_expired` leaked `_frozen` map (unbounded memory growth) |
| F5 | Significant | `derive_epoch_nonce` raised `OverflowError` on negative `epoch_id` |
| F6 | Moderate | `compute_ecu_commitment` accepted empty string silently |
| F7 | Moderate | `verify_liveness_assertion` propagated exceptions instead of returning False |
| F8 | Minor | Unused `field` import in `endorsement_packet_schema.py` |

### Round 2 (c8fd06a0) — 9 findings

| ID | Severity | Finding |
|----|----------|---------|
| F1 | Critical | `ephemeral_signing_pk` entirely unvalidated in `EpochEndorsementPacket.validate()`; test fixtures 64≠96 chars |
| F2 | Significant | `EpochCloseAttestation.agent_id` hex chars not checked |
| F3 | Significant | `EpochCloseAttestation.epoch_id` / `reputation_delta` accepted booleans |
| F4 | Significant | `derive_liveness_assertion` (runtime): no `agent_id` type/length check; bool epoch_id accepted |
| F5 | Significant | `derive_liveness_assertion` (schema): bool epoch_id accepted |
| F6 | Moderate | `verify_ecu_commitment` raised instead of returning False on bad input |
| F7 | Security | `RecoveryTransaction.validate_against_record` did not verify `old_canonical_root_pk` against genesis record |
| F8 | Moderate | `compute_recovery_commitment`/`compute_personhood_commitment` raised TypeError instead of GenesisRecordError |
| D2 | Docstring | `check_endorsement_window` quoted `>` but implementation uses `>=` at boundary |

## 5. CDL-069 Ratification Record

CDL-069 is ratified as of Phase 838j (commit `9ea0ca23`).

**Ratified scope:**
- ML-DSA-65 (FIPS 204) is the mandatory canonical identity root key algorithm
  for all agents from Genesis forward.
- BLS12-381 retained exclusively for consensus aggregation and ephemeral hot
  signing (per-validation-epoch endorsement keys).
- Three-tier key hierarchy: cold ML-DSA-65 identity root, SPHINCS+ recovery
  key, BLS ephemeral operational key.
- Genesis record four-field schema: `identity_seed_commitment`,
  `canonical_root_pk`, `recovery_commitment`, `personhood_commitment`.
- Endorsement packet 8 required fields and COSE_Sign1 signing protocol.
- Temporal data tier framework: Tier 3 (permanent SHA-384), Tier 2 (issuance
  epoch SHA-256), Tier 1 (validation epoch SHA-256).
- Freeze and revocation protocol with `freeze_from_epoch` clamping.

**Evidence document:**
`docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md`

## 6. Open Item D1 — Recovery Spec Wire Format Mismatch

The Rust `pq_keygen` binary encodes recovery spec as
`b"single_key_sphincs:" || raw_pk_bytes`; Python `encode_recovery_spec`
uses canonical JSON. These produce different SHA-384 `recovery_commitment`
values for the same logical spec.

**Status:** Non-blocking. Rust binary is authoritative for Genesis Agent 1.
**Resolution path:** CDL-070 (forward PQ migration ceremony) will specify
the canonical wire format across all implementations.

`cdl_069_d1_recovery_spec_wire_format_mismatch_open_cdl_070_path`

## 7. Forward Obligations Established by CDL-069

| Obligation | Owner | Gate |
|------------|-------|------|
| CDL-070 — forward PQ migration ceremony | Future CDL lane | Separate constitutional lane |
| CDL-071 — reconcile CDL-043, CDL-044, CDL-V1 under temporal tier framework | Future CDL lane | Normative consolidation, not emergency |
| SIM-LEAKAGE-03 live run against M-009 testbed | Row 5 runtime closure gate | Rust privacy lane integration (human gate) |
| D1 — recovery spec wire format canonical encoding | CDL-070 | CDL-070 ratification |

## 8. Hard Constraint Compliance

This lane:
- did **not** amend CDL-017 (validator governance is algorithm-agnostic),
- did **not** amend CDL-043, CDL-044, or CDL-V1 (CDL-071 path),
- did **not** claim Row 5 runtime closure,
- did **not** pull the first-validator human gate,
- did **not** graduate Option B,
- did **not** select sovereign substrate,
- did **not** claim SIM-LEAKAGE-03 live run (structural assertion only).

`cdl_069_ratification_lane_hard_constraints_satisfied`
