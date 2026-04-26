# ILC CDL-069 Post-Quantum Identity and Epoch Endorsement Protocol Ratification Evidence 838j v0.1

Status: ratification evidence artifact
Date: 2026-04-26
Decision vehicle: CDL-069
Phase: 838j
Owner lane: CDL-069 PQ identity and epoch endorsement ratification lane
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`cdl_069_ratification_evidence_complete`
`cdl_069_ratified_pq_identity_and_epoch_endorsement_protocol`
`cdl_069_mldsa65_mandatory_identity_root_from_genesis`
`cdl_069_bls12381_retained_for_consensus_and_ephemeral_hot_signing_only`
`cdl_069_three_tier_key_hierarchy_ratified`
`cdl_069_epoch_endorsement_packet_schema_ratified`
`cdl_069_temporal_data_tier_framework_ratified`
`cdl_069_commit_1_does_not_mutate_decision_log`
`cdl_069_commit_2_mutates_only_cdl_069_row`

## 1. Phase 838j dossier verdict re-read

This ratification phase re-reads the explicit verdict from
`docs/specs/ilc_cdl_069_ratification_readiness_dossier_838j_v0.1.md`
Section `5` verbatim:

> cdl_069_ratification_readiness_verdict=ready_for_ratification

Verbatim verdict token:
`cdl_069_ratification_readiness_verdict=ready_for_ratification`

That dossier already checked:

- all 14 evidence checklist items from CDL-069 §4, individually,
- all 12 CDL-069 §5 prelock criteria individually,
- the non-ratification boundary for Phase `838j`.

Phase `838j` therefore does not reopen checklist satisfaction. It consumes the
Phase `838j` dossier as the explicit ratification-readiness authority.

## 2. Ratified constitutional decision

The constitutional lane opened in Phase `838` is now ratified.

`CDL-069` is ratified as the constitutional framework governing:

- ML-DSA-65 (FIPS 204) as the mandatory canonical identity root key algorithm
  for all agents from Genesis forward,
- BLS12-381 retained exclusively for consensus aggregation and ephemeral hot
  signing (per-validation-epoch endorsement keys),
- the three-tier key hierarchy (cold ML-DSA-65 identity root, SPHINCS+
  SLH-DSA-SHA2-128s recovery key, BLS ephemeral operational key),
- the genesis record four-field schema (identity_seed_commitment,
  canonical_root_pk, recovery_commitment, personhood_commitment),
- the epoch endorsement packet schema (8 required fields, optional extensions,
  COSE_Sign1 encoding, liveness assertion construction),
- the epoch-close attestation protocol and ECU commitment construction,
- the temporal data tier framework (Tier 3 permanent SHA-384, Tier 2 issuance
  epoch SHA-256, Tier 1 validation epoch SHA-256),
- the identity recovery and key rotation protocol,
- the freeze and revocation protocol.

This ratification remains narrow:

- it ratifies identity and endorsement law rather than validator governance law,
- it does not amend CDL-017 (validator governance process is algorithm-agnostic),
- it does not amend CDL-043, CDL-044, or CDL-V1 (CDL-071 forward obligation),
- it does not ratify CDL-070 (forward PQ migration ceremony),
- it does not select sovereign substrate or graduate Option B,
- it does not claim row 5, row 7, or row 8 runtime closure.

## 3. Ratified key hierarchy and algorithm assignments

The ratified constitutional key hierarchy is:

| Tier | Key role | Algorithm | CDL-001 mapping | Persistence |
|------|----------|-----------|-----------------|-------------|
| Cold (identity root) | `canonical_root_pk` | ML-DSA-65 (FIPS 204), 1664-byte pk | `canonical_root_key` | Tier 3 — permanent |
| Recovery | `recovery_commitment` preimage | SPHINCS+ SLH-DSA-SHA2-128s (FIPS 205), 32-byte pk | `authority_recovery_key` | Tier 3 — permanent |
| Operational (hot) | `ephemeral_signing_pk` | BLS12-381 G1, per-validation-epoch | `operational_signer_key` | Tier 1 — ephemeral |

Ratified protocol constants:

- `agent_id = sha384("ilc-agent-id-v1:" || identity_seed)` — 96-char lowercase hex, permanent
- `identity_seed_commitment = sha384("ilc-seed-commit-v1:" || identity_seed)` — 96-char lowercase hex
- `blinding_factor = sha384("ilc-recovery-blind-v1:" || identity_seed)` — deterministic, no separate cold storage
- `recovery_commitment = sha384("ilc-recovery-commit-v1:" || recovery_spec || blinding_factor)` — 96-char lowercase hex
- `liveness_assertion = sha256("ilc-liveness-v1:" || agent_id || epoch_id.to_bytes(8,'big'))` — 64-char hex
- `epoch_nonce = sha256("ilc-epoch-nonce-v1:" || identity_seed_commitment || epoch_id.to_bytes(8,'big'))` — 64-char hex
- `ecu_*_commitment = sha256(domain || ecu_total || epoch_nonce)` — 64-char hex
- `freeze_from_epoch` clamping: `effective = max(current_epoch, freeze_from_epoch)` — no retroactive invalidation

Constitutional reading:

- BLS12-381 as identity root is deprecated from Genesis forward; the pre-Genesis
  migration window is a CDL-069 ratification clause, not a CDL-017 clause,
- SHA-384 (2^128 collision, 2^192 preimage quantum security) is the canonical
  hash function for Tier 3 permanent commitments,
- the `derive_agent_id` legacy path is retained for backward compatibility with
  pre-ratification agents during the migration window only,
- the `blinding_factor` derivation from `identity_seed` eliminates a separate
  cold storage item for the recovery commitment blinding value.

## 4. CDL-069 §5 prelock criteria re-read as satisfied

### 4.1 Criterion 1 satisfied

Criterion:

> `genesis_record_schema_committed` — genesis record four-field schema
> committed as spec artifact

Dossier citation:

- Phase `838j` dossier Section `3.1`

Status: satisfied. `ilc_core/identity/genesis_record_schema.py` committed Phase `838e`.

### 4.2 Criterion 2 satisfied

Criterion:

> `endorsement_packet_schema_committed` — endorsement packet schema committed
> as spec artifact

Dossier citation:

- Phase `838j` dossier Section `3.2`

Status: satisfied. `ilc_core/identity/endorsement_packet_schema.py` committed Phase `838f`.

### 4.3 Criterion 3 satisfied

Criterion:

> `epoch_endorsement_runtime_committed` — epoch endorsement runtime committed

Dossier citation:

- Phase `838j` dossier Section `3.3`

Status: satisfied. `ilc_core/identity/epoch_endorsement_runtime.py` committed Phase `838c`, audited and hardened Phase `838f`.

### 4.4 Criterion 4 satisfied

Criterion:

> `genesis_record_schema_tests_pass` — genesis record schema tests pass

Dossier citation:

- Phase `838j` dossier Section `3.4`

Status: satisfied. `tests/test_phase_838e_genesis_record_schema.py` — 57 tests pass.

### 4.5 Criterion 5 satisfied

Criterion:

> `endorsement_packet_schema_tests_pass` — endorsement packet schema tests pass

Dossier citation:

- Phase `838j` dossier Section `3.5`

Status: satisfied. `tests/test_phase_838f_endorsement_packet_schema.py` — 66 tests pass.

### 4.6 Criterion 6 satisfied

Criterion:

> `epoch_endorsement_runtime_tests_pass` — epoch endorsement runtime tests pass

Dossier citation:

- Phase `838j` dossier Section `3.6`

Status: satisfied. `tests/test_phase_838c_epoch_endorsement_runtime.py` — all tests pass.

### 4.7 Criterion 7 satisfied

Criterion:

> `audit_complete` — code audit complete, no blocking issues

Dossier citation:

- Phase `838j` dossier Section `3.7`

Status: satisfied. Audit executed Phase `838f`; 8 findings (F1–F8) identified and fixed. Commit `c5dc9633` closes all findings.

### 4.8 Criterion 8 satisfied

Criterion:

> `cdl_017_mldsa_interaction_resolved` — CDL-017 interaction resolved

Dossier citation:

- Phase `838j` dossier Section `3.8`

Status: satisfied. Item 8 evidence: `docs/specs/ilc_phase_838i_cdl_069_evidence_items_8_12_14_v0.1.md` Section `Item 8`. CDL-017 governs governance process (not key algorithms); no conflict; no CDL-017 amendment required.

### 4.9 Criterion 9 satisfied

Criterion:

> `cdl_001_compatibility_asserted` — CDL-001 Phase-227 compatibility asserted

Dossier citation:

- Phase `838j` dossier Section `3.9`

Status: satisfied. Item 12 evidence: `docs/specs/ilc_phase_838i_cdl_069_evidence_items_8_12_14_v0.1.md` Section `Item 12`. All four CDL-001 hierarchy roles and four lifecycle states representable. No CDL-001 provision violated.

### 4.10 Criterion 10 satisfied

Criterion:

> `row5_epoch_endorsement_compatibility_asserted` — Row 5 privacy lane
> compatibility asserted: SIM-LEAKAGE-03 bounds remain satisfiable

Dossier citation:

- Phase `838j` dossier Section `3.10`

Status: satisfied. Item 7 evidence: `docs/specs/ilc_phase_838h_cdl_069_evidence_items_6_7_v0.1.md` Section `Item 7`. Bounds A ≤ 0.15, B ≤ 0.15, C ≤ 0.05 remain satisfiable. Hard constraint (no Row 5 group/routing/lane info in endorsement packets) satisfied by design.

### 4.11 Criterion 11 satisfied

Criterion:

> `minting_proof_chain_compatibility_audit_complete` — minting proof chain
> compatibility audited

Dossier citation:

- Phase `838j` dossier Section `3.11`

Status: satisfied. Item 6 evidence: `docs/specs/ilc_phase_838h_cdl_069_evidence_items_6_7_v0.1.md` Section `Item 6`. Phase 550 passive ECU attribution runtime is layer-separated from epoch-close attestation; deferred-reveal window (1 validation epoch) does not break CDL-054 minting batch timing.

### 4.12 Criterion 12 satisfied

Criterion:

> `temporal_tier_framework_consistency_audit_complete` — temporal data tier
> framework consistency audited against CDL-043, CDL-044, CDL-V1

Dossier citation:

- Phase `838j` dossier Section `3.12`

Status: satisfied. Item 14 evidence: `docs/specs/ilc_phase_838i_cdl_069_evidence_items_8_12_14_v0.1.md` Section `Item 14`. No conflicts found. CDL-071 forward obligation is normative consolidation, not emergency conflict resolution.

The prelock criteria therefore remain satisfied at ratification time.

## 5. Open item D1 — recovery spec wire format mismatch

**D1** is carried forward as an open but non-blocking item:

The Rust `pq_keygen` binary encodes recovery spec as
`b"single_key_sphincs:" || raw_pk_bytes`, while Python
`genesis_record_schema.py` `encode_recovery_spec` produces canonical JSON.
These produce different SHA-384 `recovery_commitment` values for the same
logical spec.

**Non-blocking determination:** Genesis Agent 1's `recovery_commitment` in
the genesis record is the Rust binary's authoritative value. Python recovery
verification against that commitment must use the Rust wire format, not the
Python canonical JSON encoding. This is a cross-language encoding alignment
issue, not a protocol correctness issue.

**Resolution path:** CDL-070 (forward PQ migration ceremony) will specify
the canonical wire format for `encode_recovery_spec` across all
implementations. Until CDL-070 ratification, the Rust genesis binary's
format is authoritative for Genesis Agent 1. Python-based recovery
verification must use `b"single_key_sphincs:" || raw_pk_bytes` for
currently-provisioned agents.

D1 does not block CDL-069 ratification.

## 6. Migration window clause

Pre-Genesis validators and any agent provisioned on the testnet prior to
CDL-069 ratification that uses a BLS12-381 identity root key are subject to a
migration window: such agents must re-provision with ML-DSA-65 as their
canonical root key within the first CDL-069-compliant validator admission
process. Until re-provisioned, their BLS-rooted endorsement packets are
accepted under the legacy `derive_agent_id` path, which is retained for
backward compatibility per CDL-069 §2b and Phase `838d`.

New validators admitted from CDL-069 ratification forward must use ML-DSA-65
as their identity root key. No exceptions.

This clause does not require CDL-017 to be amended.

## 7. Two-commit mutation discipline and decision-log consequence

This phase uses a two-commit constitutional mutation pattern.

Commit `1`:

- publishes this ratification artifact,
- re-states the satisfied prelock burden using the Phase `838j` dossier,
- does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

Commit `2`:

- mutates exactly the `CDL-069` row in
  `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- changes `status: open` to `status: ratified`,
- appends `ratified_phase: 838j`,
- appends `ratified_date: 2026-04-26`,
- appends
  `evidence_document: docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md`.

No other decision-log row may change in commit `2`.

## 8. Preserved exclusions and non-goals

This ratification does not do any of the following:

- amend CDL-017 (validator governance process is algorithm-agnostic),
- amend CDL-043, CDL-044, or CDL-V1 (CDL-071 forward obligation),
- ratify CDL-070 (forward PQ migration ceremony — separate lane),
- resolve D1 recovery spec wire format mismatch (CDL-070 path),
- authorize a BLS12-381 identity root for new agents post-ratification,
- claim row 5, row 7, or row 8 runtime closure,
- execute SIM-LEAKAGE-03 live against M-009 testbed (Row 5 runtime gate),
- select sovereign substrate or graduate Option B,
- mutate any genesis record already committed on-chain.
