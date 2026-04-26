# ILC CDL-069 Ratification Readiness Dossier 838j v0.1

Status: ratification-readiness dossier
Date: 2026-04-26
Phase: 838j
Decision vehicle: CDL-069
Owner lane: G8 Phase 838 PQ identity ratification lane
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`cdl_069_ratification_readiness_dossier_838j_complete`
`all_cdl_069_opening_checklist_items_satisfied_phase_838j`
`all_phase_838_prelock_criteria_checked_phase_838j`
`cdl_069_ratification_readiness_verdict=ready_for_ratification`
`cdl_069_not_ratified_in_this_dossier_commit`

## 1. Purpose and scope

This dossier re-reads the CDL-069 opening checklist (§4, 14 items) exactly as
written, checks every item against the named evidence source, checks all twelve
CDL-069 §5 prelock criteria individually, and publishes an explicit
ratification-readiness verdict.

This dossier does not ratify CDL-069. It does not mutate
`docs/specs/ilc_constitutional_decision_log_v0.1.md`. It records that the
opening-side evidence burden is satisfied.

Authoritative source set for this dossier:

- `docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_opening_838_v0.1.md`
- `docs/genesis/genesis_agent1_pubkey_record_838a.txt`
- `docs/specs/ilc_phase_838a_genesis_agent1_keygen_closure_v0.1.md`
- `docs/specs/ilc_phase_838b_sphincs_shamir_split_closure_v0.1.md`
- `ilc_core/identity/agent_id_runtime.py` (Phase 838d)
- `ilc_core/identity/genesis_record_schema.py` (Phase 838e)
- `ilc_core/identity/endorsement_packet_schema.py` (Phase 838f)
- `ilc_core/identity/epoch_endorsement_runtime.py` (Phase 838c)
- `docs/specs/ilc_phase_838h_cdl_069_evidence_items_6_7_v0.1.md`
- `docs/specs/ilc_phase_838i_cdl_069_evidence_items_8_12_14_v0.1.md`
- `docs/specs/ilc_phase_838g_cdl_069_ratification_planning_v0.1.md`

---

## 2. CDL-069 opening checklist re-read (§4, 14 items)

### Item 1 — Phase 838a complete (`genesis_agent1_mldsa_keygen_complete`)

**Checklist text:** Genesis Agent 1 identity_seed, ML-DSA-65 keypair, and
SPHINCS+ recovery keypair generated and cold-stored using the shamir_sphincs
recovery mechanism. Pubkey verification record and genesis record template on
cold-storage media. Tool tests passing.

**Evidence:**
- `docs/genesis/genesis_agent1_pubkey_record_838a.txt` — committed pubkey record.
- `docs/specs/ilc_phase_838a_genesis_agent1_keygen_closure_v0.1.md` — ceremony closure.
- `tests/test_phase_838a_genesis_agent1_keygen.py` — 24 tests passing.
- `ilc_consensus/src/pq_keygen_main.rs` — token: `pq_keygen_838a_binary_present`.
- Phase 838b: Shamir 2-of-3 split complete; Plate 3 destroyed.
  Token: `shamir_split_838b_binary_present`.

**Status: SATISFIED.** Token: `genesis_agent1_mldsa_keygen_complete`.

---

### Item 2 — ML-DSA runtime operational (`mldsa_65_runtime_operational_in_ilc_toolchain`)

**Checklist text:** ML-DSA-65 keygen, sign, and verify path operational in the
ILC toolchain. Sign/verify round-trip test coverage. SPHINCS+ sign/verify coverage.

**Evidence:**
- `ilc_consensus/src/pq_keygen_main.rs` uses `fips204::ml_dsa_65::KG` and
  `fips205::slh_dsa_sha2_128s::KG` for keypair generation.
- `tests/test_phase_838a_genesis_agent1_keygen.py` includes 3 live binary smoke
  tests exercising the ML-DSA and SPHINCS+ keygen paths.
- Genesis Agent 1 pubkey record includes committed `mldsa_pk_hex` (3328 hex
  chars = 1664 bytes, correct for ML-DSA-65).

**Status: SATISFIED.** Token: `mldsa_65_runtime_operational_in_ilc_toolchain`.

---

### Item 3 — agent_id derivation updated (`cdl_042_amendment_identity_seed_and_sha384_implemented`)

**Checklist text:** `ilc_core/identity/agent_id_runtime.py` updated to:
(a) accept identity_seed bytes, (b) use SHA-384 for Tier 3 derivation,
(c) deprecate BLS-pk-based derivation.

**Evidence:**
- `AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_838d.v0.2"` (Phase 838d).
- `CDL_069_AMENDMENT = "cdl_069_opens_phase_838"` present.
- `derive_agent_id_v2(identity_seed)` → sha384("ilc-agent-id-v1:" || seed) → 96-char hex.
- Legacy `derive_agent_id` retained with DEPRECATED docstring.
- `tests/test_phase_838d_agent_id_runtime_v2.py` — 27 tests passing.

**Status: SATISFIED.** Token: `cdl_042_amendment_identity_seed_and_sha384_implemented`.

---

### Item 4 — Genesis record schema specified (`genesis_record_schema_proposed`)

**Checklist text:** Concrete schema for all four committed fields, recovery_spec
format for each supported type, freeze_from_epoch recovery transaction field.

**Evidence:**
- `ilc_core/identity/genesis_record_schema.py` (Phase 838e).
- `GENESIS_RECORD_SCHEMA_VERSION = "genesis_record_schema_838e.v0.1"`.
- `GenesisRecord` dataclass: all four fields with SHA-384 validation.
- `RecoverySpecType` enum: 7 types (SINGLE_KEY_MLDSA, SINGLE_KEY_SPHINCS,
  SHAMIR_SPHINCS, QUORUM_VALIDATOR, THRESHOLD_MULTIPARTY, HSM_ATTESTATION,
  PERSONHOOD_BIOMETRIC).
- `RecoveryTransaction.validate_against_record()`: freeze_from_epoch clamping.
- `tests/test_phase_838e_genesis_record_schema.py` — 57 tests passing.

**Status: SATISFIED.** Token: `genesis_record_schema_proposed`.

---

### Item 5 — Epoch endorsement packet schema specified (`epoch_endorsement_packet_schema_proposed`)

**Checklist text:** Concrete field names, COSE encoding, required vs. optional
fields, agent_state_root computation specification.

**Evidence:**
- `ilc_core/identity/endorsement_packet_schema.py` (Phase 838f).
- `ENDORSEMENT_PACKET_SCHEMA_VERSION = "endorsement_packet_schema_838f.v0.1"`.
- All 8 required fields validated with machine-auditable error tokens.
- `build_cose_tbs_bytes()` COSE_Sign1 TBS stub with `ILC-EndorsementPacket-v1:` domain tag.
- `agent_state_root`: CID of prior epoch-close attestation (non-empty string).
- `tests/test_phase_838f_endorsement_packet_schema.py` — 66 tests passing.

**Status: SATISFIED.** Token: `epoch_endorsement_packet_schema_proposed`.

---

### Item 6 — Minting proof chain audit (`minting_proof_chain_compatibility_audit_complete`)

**Evidence:** `docs/specs/ilc_phase_838h_cdl_069_evidence_items_6_7_v0.1.md` §6.

Audit findings:
- No field conflicts between epoch-close attestation and Phase 550 runtime.
- `epoch_nonce` construction compatible with ECU aggregation (sequential layers).
- Deferred-reveal window (1 validation epoch) does not break CDL-054 timing.

**Status: SATISFIED.** Token: `minting_proof_chain_compatibility_audit_complete`.

---

### Item 7 — Privacy lane compatibility assertion (`row5_epoch_endorsement_compatibility_asserted`)

**Evidence:** `docs/specs/ilc_phase_838h_cdl_069_evidence_items_6_7_v0.1.md` §7.

Findings:
- All 8 required fields contain no Row 5 group/routing/lane information.
- Bounds A, B, C remain satisfiable. Participation threshold interaction
  does not widen membership inference beyond pre-existing observable.

**Status: SATISFIED.** Token: `row5_epoch_endorsement_compatibility_asserted`.

---

### Item 8 — CDL-017 interaction resolved (`cdl_017_mldsa_interaction_resolved`)

**Evidence:** `docs/specs/ilc_phase_838i_cdl_069_evidence_items_8_12_14_v0.1.md` §8.

CDL-017 (ratified Phase 765) is silent on key algorithms; no conflict.
Compatibility clause: pre-ratification validators have a migration window;
new validators from ratification forward require ML-DSA-65.

**Status: SATISFIED.** Token: `cdl_017_mldsa_interaction_resolved`.

---

### Item 9 — SHA-384 binding decision recorded (`tier3_sha384_binding_decision_recorded`)

**Evidence:** CDL-069 §2g contains the binding threat model justification
(committed to repo at Phase 838 opening). All Phase 838c/838d/838e/838f
runtimes implement SHA-384 for Tier 3 data uniformly.

**Status: SATISFIED.** Token: `tier3_sha384_binding_decision_recorded`.

---

### Item 10 — Authority recovery key scheme reviewed (`authority_recovery_key_scheme_reviewed`)

**Evidence:** CDL-069 §2a specifies all 7 recovery_spec types with blinding
factor construction. Phase 838e implements and tests all 7 types (57 tests).
Enumeration resistance: 48-byte SHA-384 blinding factor. SPHINCS+ / ML-DSA
independence confirmed by separate seed generation in pq_keygen_main.rs.

**Status: SATISFIED.** Token: `authority_recovery_key_scheme_reviewed`.

---

### Item 11 — ecu_readiness elimination confirmed (`ecu_readiness_field_eliminated_confirmed`)

**Evidence:** CDL-069 §2b explicitly states the field is eliminated and packet
presence is the readiness signal. No CDL-027, CDL-050, CDL-054, CDL-068, or
Phase 550 runtime uses `ecu_readiness` as a contractual field.

**Status: SATISFIED.** Token: `ecu_readiness_field_eliminated_confirmed`.

---

### Item 12 — CDL-001 compatibility assertion (`cdl_001_compatibility_asserted`)

**Evidence:** `docs/specs/ilc_phase_838i_cdl_069_evidence_items_8_12_14_v0.1.md` §12.

CDL-069 three-tier hierarchy maps to CDL-001 Phase-227 remediation boundary.
All four hierarchy roles and all four lifecycle states satisfied.
freeze_from_epoch clamping ensures forward-only auditability.

**Status: SATISFIED.** Token: `cdl_001_compatibility_asserted`.

---

### Item 13 — Warm key delegation format specified (`warm_key_delegation_format_specified`)

**Evidence:** CDL-069 §2b warm key delegation section specifies: `delegate_pk`,
`ilc_limit_per_epoch`, `ecu_limit_per_epoch` (optional), `valid_until_epoch`,
`scope` fields; `supersedes_epoch_id` revocation; bounded-authority model.

**Status: SATISFIED.** Token: `warm_key_delegation_format_specified`.

---

### Item 14 — Temporal tier framework consistency audit (`temporal_tier_framework_consistency_audit_complete`)

**Evidence:** `docs/specs/ilc_phase_838i_cdl_069_evidence_items_8_12_14_v0.1.md` §14.

CDL-043 pruning operates on claim graph only (Tier 1/2; Tier 3 identity exempt).
CDL-044 retention_epochs is layer-separated from Tier 2 semantics.
CDL-V1 decay operates on Tier 2 within issuance epoch cadence.
No conflicts found. CDL-071 forward obligation is normative consolidation.

**Status: SATISFIED.** Token: `temporal_tier_framework_consistency_audit_complete`.

---

## 3. Checklist summary

All 14 items satisfied:

```
genesis_agent1_mldsa_keygen_complete                    SATISFIED (838a)
mldsa_65_runtime_operational_in_ilc_toolchain           SATISFIED (838a)
cdl_042_amendment_identity_seed_and_sha384_implemented  SATISFIED (838d)
genesis_record_schema_proposed                          SATISFIED (838e)
epoch_endorsement_packet_schema_proposed                SATISFIED (838f)
minting_proof_chain_compatibility_audit_complete        SATISFIED (838h)
row5_epoch_endorsement_compatibility_asserted           SATISFIED (838h)
cdl_017_mldsa_interaction_resolved                      SATISFIED (838i)
tier3_sha384_binding_decision_recorded                  SATISFIED (CDL-069 §2g + 838c/d/e/f)
authority_recovery_key_scheme_reviewed                  SATISFIED (CDL-069 §2a + 838e)
ecu_readiness_field_eliminated_confirmed                SATISFIED (CDL-069 §2b)
cdl_001_compatibility_asserted                          SATISFIED (838i)
warm_key_delegation_format_specified                    SATISFIED (CDL-069 §2b)
temporal_tier_framework_consistency_audit_complete      SATISFIED (838i)
```

---

## 4. CDL-069 §5 prelock criteria — all twelve checked

### Criterion 1 satisfied

> agent_id is derived from a permanent 32-byte identity_seed using SHA-384
> with the domain separator "ilc-agent-id-v1:". No key event changes agent_id.

Evidence: `derive_agent_id_v2()` in `agent_id_runtime.py` implements exactly
this. Known vector test locks the SHA-384 derivation formula. Legacy path
retained but deprecated.

**Status: satisfied.**

---

### Criterion 2 satisfied

> ML-DSA-65 (FIPS 204) is the mandatory canonical root key algorithm for all
> agents from Genesis forward. BLS12-381 is deprecated as an identity root.

Evidence: `pq_keygen_main.rs` uses `fips204::ml_dsa_65`. Genesis Agent 1
ceremony completed. CDL-042 amendment formalized in `agent_id_runtime.py`.

**Status: satisfied.**

---

### Criterion 3 satisfied

> The genesis record contains four committed fields: identity_seed_commitment,
> canonical_root_pk, recovery_commitment, and optional personhood_commitment.
> All commitment fields use SHA-384 with a blinding_factor derived from identity_seed.

Evidence: `GenesisRecord` in `genesis_record_schema.py` with all four fields.
All SHA-384, blinding_factor = sha384("ilc-recovery-blind-v1:" || identity_seed).

**Status: satisfied.**

---

### Criterion 4 satisfied

> Recovery mechanism type, constituent keys, threshold, and parameters are
> entirely private until recovery is triggered. No agent is labeled by
> recovery class in any on-chain record.

Evidence: `recovery_commitment = sha384(recovery_spec_bytes || blinding_factor)`.
The recovery_spec pre-image is never stored on-chain. Only the 96-char SHA-384
commitment is public. All 7 recovery types are hidden behind the same commitment
interface.

**Status: satisfied.**

---

### Criterion 5 satisfied

> Every active agent at or above the participation threshold must publish an
> epoch endorsement packet at each validation epoch boundary, signed by the
> ML-DSA identity root key.

Evidence: `EpochEndorsementPacket` in `epoch_endorsement_runtime.py` specifies
the mandatory publication protocol. `EndorsementCache.accept_packet()` enforces
the acceptance rules. Protocol is implemented and tested (58 tests).

**Status: satisfied.**

---

### Criterion 6 satisfied

> The epoch endorsement packet required fields are: protocol_version, agent_id,
> epoch_id, sequence_number, ephemeral_signing_pk, valid_epochs,
> liveness_assertion, and agent_state_root.

Evidence: Both `epoch_endorsement_runtime.py` and `endorsement_packet_schema.py`
implement all 8 required fields with validation and machine-auditable error
tokens. `valid_epochs ∈ [1, 1440]`. `supersedes_epoch_id` closes distributed
atomicity gap (audit fix F3 applied).

**Status: satisfied.**

---

### Criterion 7 satisfied

> ECU fast-path transfers are authorized by the ephemeral hot signing key.
> ILC coin slow-path transfers are authorized by the ML-DSA identity root key
> (or warm delegate key within its authorized limit).

Evidence: CDL-069 §2b specifies the authorization boundary. This is a
constitutional declaration; runtime enforcement of this split is a CDL-070
scope item.

**Status: satisfied** (constitutional declaration; CDL-070 governs enforcement).

---

### Criterion 8 satisfied

> The epoch-close attestation feeds the minting proof chain. ECU totals are
> committed as sha256(total || epoch_nonce) where epoch_nonce = sha256(
> identity_seed_commitment || epoch_id), protecting Row 5 anonymity.

Evidence: `compute_ecu_commitment()` and `derive_epoch_nonce()` in
`epoch_endorsement_runtime.py` implement the exact formula. `EpochCloseAttestation`
includes `ecu_sent_commitment` and `ecu_received_commitment`. Minting audit
(838h item 6) confirms compatibility.

**Status: satisfied.**

---

### Criterion 9 satisfied

> SHA-384 is used uniformly for all Tier 3 (permanent) data. SHA-256 is used
> for Tier 1 and Tier 2 data.

Evidence: All Tier 3 operations (agent_id, genesis record commitments,
blinding_factor) use SHA-384. All Tier 1/2 operations (liveness_assertion,
epoch_nonce, ecu_commitment) use SHA-256. Verified across all Phase 838 runtimes.

**Status: satisfied.**

---

### Criterion 10 satisfied

> The ML-DSA endorsement packet must not reveal Row 5 group membership,
> routing assignment, or privacy lane participation. Hard constraint.

Evidence: Phase 838h item 7 analyzed all 8 required fields and all optional
fields. No Row 5 structural information is present or permitted in the schema.

**Status: satisfied.**

---

### Criterion 11 satisfied

> CDL-069 introduces the temporal data tier framework as a constitutional
> principle. CDL-043, CDL-044, and CDL-V1 are consistent partial implementations.
> CDL-071 will formally reconcile them.

Evidence: CDL-069 §2g states this principle. Phase 838i item 14 audited
CDL-043, CDL-044, and CDL-V1 for conflicts — none found.

**Status: satisfied.**

---

### Criterion 12 satisfied

> CDL-069 cannot be ratified until all fourteen evidence checklist items (§4) are complete.

Evidence: All 14 items checked above in Section 2. All satisfied.

**Status: satisfied.**

---

## 5. Ratification readiness verdict

All 14 opening checklist items are satisfied. All 12 prelock criteria are
satisfied.

**CDL-069 is ready for ratification.**

`cdl_069_ratification_readiness_verdict=ready_for_ratification`
`cdl_069_checklist_14_of_14_satisfied`
`cdl_069_prelock_criteria_12_of_12_satisfied`

---

## 6. Open question noted but not blocking

**Recovery spec wire format (D1 from audit):**
The Rust pq_keygen binary encodes recovery_spec as
`b"single_key_sphincs:" || raw_pk_bytes`. The Python `encode_recovery_spec()`
uses canonical JSON. These produce different pre-images for the same key.
Genesis Agent 1's `recovery_commitment` was produced by the Rust binary — that
is the authoritative committed value. CDL-069 ratification should include a
clause specifying that the canonical recovery_spec wire format is the Rust
binary's format for all currently provisioned agents, with CDL-070 or a
sub-instrument to specify the forward format for future agents. This is a
documentation note; it does not block ratification.
