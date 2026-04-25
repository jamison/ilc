# Phase 838g — CDL-069 Ratification Planning: 14-Item Evidence Checklist Sweep

**Phase:** 838g  
**Date:** 2026-04-25  
**Governing spec:** CDL-069 §4 Evidence Checklist (14 items)  
**Purpose:** Survey checklist completion status; identify open items; plan ratification sequencing.

---

## 1. Checklist status sweep

| # | Item | Token | Status | Phase completed |
|---|------|-------|--------|-----------------|
| 1 | Phase 838a complete — Genesis Agent 1 keygen + cold storage | `genesis_agent1_mldsa_keygen_complete` | **COMPLETE** | 838a |
| 2 | ML-DSA runtime operational in ILC toolchain | `mldsa_65_runtime_operational_in_ilc_toolchain` | **COMPLETE** | 838a (Rust pq_keygen binary) |
| 3 | agent_id derivation updated — identity_seed + SHA-384 + CDL-042 amendment | `cdl_042_amendment_identity_seed_and_sha384_implemented` | **COMPLETE** | 838d |
| 4 | Genesis record schema specified | `genesis_record_schema_proposed` | **COMPLETE** | 838e |
| 5 | Epoch endorsement packet schema specified | `epoch_endorsement_packet_schema_proposed` | **COMPLETE** | 838f |
| 6 | Minting proof chain audit | `minting_proof_chain_compatibility_audit_complete` | **OPEN** | — |
| 7 | Privacy lane compatibility assertion | `row5_epoch_endorsement_compatibility_asserted` | **OPEN** | — |
| 8 | CDL-017 interaction resolved | `cdl_017_mldsa_interaction_resolved` | **OPEN** | — |
| 9 | SHA-384 binding decision recorded | `tier3_sha384_binding_decision_recorded` | **COMPLETE (inline)** | CDL-069 §2g (see §3 below) |
| 10 | Authority recovery key scheme reviewed | `authority_recovery_key_scheme_reviewed` | **COMPLETE (inline)** | CDL-069 §2a (see §3 below) |
| 11 | ecu_readiness elimination confirmed | `ecu_readiness_field_eliminated_confirmed` | **COMPLETE (inline)** | CDL-069 §2b (see §3 below) |
| 12 | CDL-001 compatibility assertion | `cdl_001_compatibility_asserted` | **OPEN** | — |
| 13 | Warm key delegation format specified | `warm_key_delegation_format_specified` | **COMPLETE (inline)** | CDL-069 §2b (see §3 below) |
| 14 | Temporal tier framework consistency audit | `temporal_tier_framework_consistency_audit_complete` | **OPEN** | — |

**Summary:** 9 complete, 5 open.

---

## 2. Open items — disposition and sequencing

### Item 6 — Minting proof chain audit (`minting_proof_chain_compatibility_audit_complete`)

**What is required:** The Phase 550 passive ECU attribution runtime and the
minting economics (CDL-054) must be audited for compatibility with the
epoch-close attestation → minting authorization chain introduced by CDL-069.
Specifically: the `ecu_sent_commitment` deferred-reveal mechanism
(`sha256(ecu_sent_total || epoch_nonce)`) must be verified compatible with
ECU total aggregation in the minting circuit.

**Evidence needed:** Written audit report confirming: (a) no field conflicts
between epoch-close attestation and Phase 550 attribution runtime; (b)
`epoch_nonce = sha256(identity_seed_commitment || epoch_id)` is compatible
with the aggregation model; (c) the deferred-reveal window does not break
any CDL-054 timing guarantee.

**Disposition:** Requires a dedicated audit phase. The Phase 550 runtime
(`ilc_core/reputation/passive_ecu_attribution_runtime.py`) and CDL-054 must
be read against the CDL-069 §2b epoch-close attestation protocol.

**Proposed phase:** 838h.

---

### Item 7 — Privacy lane compatibility assertion (`row5_epoch_endorsement_compatibility_asserted`)

**What is required:** Explicit verification that the epoch endorsement protocol
does not violate SIM-LEAKAGE-03 bounds or Row 5 anonymity constraints.
CDL-069 prelock criterion 10 states: "The ML-DSA endorsement packet must not
reveal Row 5 group membership, routing assignment, or privacy lane participation."

**Evidence needed:** Written analysis confirming: (a) the 8 required fields
of the endorsement packet contain no Row 5-identifying data; (b) the
`epoch_nonce` construction protects ECU amounts against brute-force in the
deferred-reveal window; (c) participation threshold interaction with rolling
group construction does not leak membership.

**Disposition:** Can be written by reviewing the endorsement packet fields
against the Row 5 / SIM-LEAKAGE-03 bounds from the capsule. No new runtime
required.

**Proposed phase:** 838h (same phase as item 6 — both are written analysis).

---

### Item 8 — CDL-017 interaction resolved (`cdl_017_mldsa_interaction_resolved`)

**What is required:** A decision on whether validator identity root keys
migrate to ML-DSA. CDL-017 (open) governs the Validator-Agent identity
system. CDL-069 introduces ML-DSA as the mandatory identity root for all
agents. The interaction must be explicitly resolved before CDL-069 ratifies.

**Disposition:** CDL-017 is still open. The interaction resolution can take
one of three forms:
1. CDL-017 explicitly adopts ML-DSA for validator identity root keys (strong
   consistency with CDL-069; recommended path if CDL-017 is ready).
2. CDL-017 is amended to note ML-DSA applicability and defers full migration
   timeline to a CDL-017 sub-phase.
3. CDL-069 ratification adds a non-migration clause: validators with pre-
   Genesis BLS root keys are exempt from ML-DSA migration until CDL-017
   ratifies; new validators from Genesis forward use ML-DSA.

**Proposed path:** Option 3 is the minimal blocker — add an explicit
compatibility clause to CDL-069 ratification evidence. Does not require
CDL-017 to ratify first.

**Proposed phase:** 838i (written decision).

---

### Item 12 — CDL-001 compatibility assertion (`cdl_001_compatibility_asserted`)

**What is required:** Explicit statement that CDL-069's three-tier key
hierarchy (Tier 3: permanent cold-key, Tier 2: operational hot-key, Tier 1:
ephemeral per-epoch key) is compatible with CDL-001's remediation boundary
(Phase-227 contract).

**What CDL-001 governs:** The Phase-227 remediation boundary governs the
conditions under which a validator may be removed from the active set. The
question is whether a cold-key rotation (recovery transaction) during an
active remediation triggers the boundary condition.

**Disposition:** CDL-069 §2a specifies that `freeze_from_epoch` is clamped
to `max(current_epoch, value)`, preventing retroactive invalidation. This
means a recovery transaction cannot retroactively invalidate prior
endorsement packets or transactions. This is directly compatible with
CDL-001's forward-only remediation model.

**Evidence needed:** Written one-paragraph assertion citing the
`freeze_from_epoch` clamping rule and the CDL-001 remediation forward-only
constraint.

**Proposed phase:** 838i (same phase as item 8 — both are written assertions).

---

### Item 14 — Temporal tier framework consistency audit (`temporal_tier_framework_consistency_audit_complete`)

**What is required:** An explicit check that CDL-069's tier assignments are
consistent with CDL-043 pruning rules, CDL-044 retention epochs, and CDL-V1
temporal decay. Any conflicts must be enumerated for CDL-071.

**Tier assignments in CDL-069:**
- Tier 3 (permanent): genesis record fields, agent_id, canonical_root_pk,
  SHA-384 commitments — never pruned
- Tier 2 (issuance-epoch duration): endorsement packet content, epoch-close
  attestation — pruned after minting confirmation
- Tier 1 (validation-epoch or shorter): ephemeral signing keys, per-epoch
  BLS keys — pruned every validation epoch

**CDL-043:** Governs claim pruning. Claim data is Tier 1/2 by construction.
No conflict expected.

**CDL-044:** Governs retention epochs for gossip/transport data. Transport
envelopes are Tier 1 (pruned ≤ retention_epochs). No conflict expected.

**CDL-V1:** Governs temporal reputation decay. Reputation scores are Tier 2.
Decay function is bounded by issuance epoch cadence. No conflict expected.

**Disposition:** No conflicts found in the above analysis. Written audit
statement can be produced from this section.

**Proposed phase:** 838i.

---

## 3. Inline-complete items — evidence

### Item 9 — SHA-384 binding decision (`tier3_sha384_binding_decision_recorded`)

**Evidence:** CDL-069 §2g (Temporal data tier framework) contains the binding
written justification: "SHA-384 is used uniformly for all Tier 3 (permanent)
data: agent_id derivation, genesis record commitment fields, identity_seed_
commitment, recovery_commitment, personhood_commitment." The threat model is
explicit: "A CDL governing quantum-resistant identity that uses 85-bit quantum
collision resistance on commitment fields would be internally inconsistent."
The decision is binding at ratification.

**Token satisfied:** CDL-069 §2g is committed to the repo. Runtime
implementations in 838d, 838e, 838f all use SHA-384 uniformly for Tier 3
data and SHA-256 for Tier 1/2 data. The decision is fully recorded.

---

### Item 10 — Authority recovery key scheme reviewed (`authority_recovery_key_scheme_reviewed`)

**Evidence:** CDL-069 §2a contains the full recovery_spec format for all 7
supported types (SINGLE_KEY_MLDSA, SINGLE_KEY_SPHINCS, SHAMIR_SPHINCS,
QUORUM_VALIDATOR, THRESHOLD_MULTIPARTY, HSM_ATTESTATION, PERSONHOOD_BIOMETRIC).
The commitment scheme uses `blinding_factor = sha384("ilc-recovery-blind-v1:"
|| identity_seed)`, which is derived deterministically and eliminates a
separate cold-storage item. SPHINCS+ and ML-DSA recovery key independence
is confirmed by different derivation paths (mldsa_seed vs sphincs_seed,
both derived from getrandom in pq_keygen_main.rs). Enumeration resistance
is provided by the 48-byte SHA-384 blinding factor.

Phase 838e (`genesis_record_schema.py`) implements all commitment functions
and validates them against 57 tests. The blinding factor domain separation
is verified by `test_blinding_factor_domain_separates_from_identity_commitment`.

---

### Item 11 — ecu_readiness elimination confirmed (`ecu_readiness_field_eliminated_confirmed`)

**Evidence:** CDL-069 §2b explicitly states: "The `ecu_readiness` field from
the original opening is eliminated. Endorsement packet publication is the
readiness signal. Presence is active; absence is inactive. This simplifies
the protocol and removes one open ratification decision."

No existing CDL, runtime module, or test refers to `ecu_readiness` as a
mandatory field. The search confirms: no CDL-027, CDL-050, CDL-054, CDL-068,
or Phase 550 runtime uses `ecu_readiness` as a contractual field. Elimination
does not break any existing CDL obligation.

---

### Item 13 — Warm key delegation format specified (`warm_key_delegation_format_specified`)

**Evidence:** CDL-069 §2b (warm key delegation section) specifies the
delegation authorization fields: `delegate_pk`, `ilc_limit_per_epoch`,
`ecu_limit_per_epoch` (optional), `valid_until_epoch`, `scope`. The
revocation protocol uses `supersedes_epoch_id` propagation (Fix M1). The
limit enforcement model is the "corporate credit card" bounded authority
pattern. Delegation format and scope encoding are specified. Ratification
decisions (full format lock) are deferred to CDL-070.

---

## 4. Ratification phase plan

Based on the above, CDL-069 ratification requires three additional phases:

### Phase 838h — Written analysis (items 6 + 7)
- Item 6: Minting proof chain compatibility audit
  - Read `ilc_core/reputation/passive_ecu_attribution_runtime.py` against CDL-069 §2b
  - Confirm epoch_nonce construction compatible with aggregation
  - Write audit report with machine token `minting_proof_chain_compatibility_audit_complete`
- Item 7: Privacy lane compatibility assertion
  - Review 8 required endorsement packet fields for Row 5 leakage
  - Write assertion with token `row5_epoch_endorsement_compatibility_asserted`

### Phase 838i — Written decisions (items 8 + 12 + 14)
- Item 8: CDL-017 interaction — write Option 3 clause (non-migration boundary)
  - Token: `cdl_017_mldsa_interaction_resolved`
- Item 12: CDL-001 compatibility — write one-paragraph assertion
  - Token: `cdl_001_compatibility_asserted`
- Item 14: Temporal tier consistency audit
  - Write formal audit statement from §2 analysis above
  - Token: `temporal_tier_framework_consistency_audit_complete`

### Phase 838j — Prelock + ratification
- Assemble all 14 evidence tokens
- Write CDL-069 prelock document (cf. CDL-068 prelock pattern)
- Run 7-test prelock verification suite
- Write CDL-069 ratification evidence (cf. CDL-068 ratification pattern)
- Commit ratification: bump CDL-069 `status: ratified`, `ratification_phase: 838j`

**Total phases remaining:** 3 (838h, 838i, 838j)

---

## 5. Phase 838 sub-phase summary

| Sub-phase | Description | Status | Commit |
|-----------|-------------|--------|--------|
| 838a | Genesis Agent 1 keygen ceremony | COMPLETE | published |
| 838b | SPHINCS+ Shamir 2-of-3 ceremony | COMPLETE | published |
| 838c | Epoch endorsement runtime (`epoch_endorsement_runtime.py`) | COMPLETE | published |
| 838d | agent_id v2 (identity_seed + SHA-384) | COMPLETE | 9863fde5^ |
| 838e | Genesis record schema | COMPLETE | 9863fde5 |
| 838f | Endorsement packet schema + COSE stub | COMPLETE | 70328780 |
| 838g | Ratification planning (this document) | COMPLETE | — |
| 838h | Minting audit + privacy lane assertion | PENDING | — |
| 838i | CDL-017 / CDL-001 / temporal audit | PENDING | — |
| 838j | Prelock + ratification | PENDING | — |

---

## 6. Machine tokens — status index

```
genesis_agent1_mldsa_keygen_complete                    SATISFIED (838a)
mldsa_65_runtime_operational_in_ilc_toolchain           SATISFIED (838a)
cdl_042_amendment_identity_seed_and_sha384_implemented  SATISFIED (838d)
genesis_record_schema_proposed                          SATISFIED (838e)
epoch_endorsement_packet_schema_proposed                SATISFIED (838f)
minting_proof_chain_compatibility_audit_complete        OPEN (838h)
row5_epoch_endorsement_compatibility_asserted           OPEN (838h)
cdl_017_mldsa_interaction_resolved                      OPEN (838i)
tier3_sha384_binding_decision_recorded                  SATISFIED (CDL-069 §2g)
authority_recovery_key_scheme_reviewed                  SATISFIED (CDL-069 §2a + 838e)
ecu_readiness_field_eliminated_confirmed                SATISFIED (CDL-069 §2b)
cdl_001_compatibility_asserted                          OPEN (838i)
warm_key_delegation_format_specified                    SATISFIED (CDL-069 §2b)
temporal_tier_framework_consistency_audit_complete      OPEN (838i)
```

9 of 14 tokens satisfied. 5 remain for 838h and 838i.
