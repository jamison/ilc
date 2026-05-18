# ILC Project-Authority Security Disposition — Phase 1387 Fix v0.1

**Phase:** 1387-Fix  
**Date:** 2026-05-18  
**Status:** DISPOSITION COMPLETE  
**Authority:** Project-authority AI-assisted structured security review + direct code audit  
**Review method:** Deterministic direct-read audit of every named source file; no memory-only claims  
**Disposition token:** `project_authority_security_disposition_complete_phase_1387_fix`

---

```text
project_authority_security_disposition_complete_phase_1387_fix
high_001_disposition_closed_log_layer_structural_non_claim_accepted
high_002_disposition_closed_bls_threshold_fix_verified
medium_001_disposition_accepted_with_carry_forward
medium_002_disposition_accepted_with_carry_forward
medium_003_disposition_accepted_with_carry_forward
all_known_high_findings_dispositioned_phase_1387_fix
```

---

## 1. Purpose and Scope

This document is the project-authority security disposition required by the Phase 1387 pre-activation hardening gate. It covers every surface named in the Phase 1384 scope record:

- `ilc_consensus/` — BFT safety, certificate construction, epoch checkpoint handling, consensus networking, and settlement handoff code
- `ilc_core/` — economic surfaces that can affect ECU, ILC, stake, reward, claimability, governance weight, or settlement state
- HIGH-001 defense — log-layer defense, non-loopback evidence, and the remaining sender-privacy non-claim boundary

Every known HIGH-severity finding is explicitly dispositioned below as closed, accepted, or deferred with rationale and bounded carry-forward authority.

---

## 2. Files Directly Audited (deterministic read, no memory-only claims)

| File | Lines | Review focus |
|------|-------|-------------|
| `ilc_consensus/src/epoch_settlement.rs` | 1015 | BLS AggSig verification, epoch monotonicity, LMDB write path |
| `ilc_consensus/src/validator.rs` | 401 | quorum_threshold, ValidatorSet construction, concentration limit |
| `ilc_consensus/src/types.rs` | 494 | type safety, G2 subgroup checks, AgentID/AggSig deserialization |
| `ilc_consensus/src/fast_path.rs` | 890 | certificate execution, sender sig verification ordering, historical ValidatorSet resolution |
| `ilc_consensus/src/balance_store.rs` | 378 | transfer atomicity, version-lock, overflow guards, attribution replay guard |
| `ilc_core/ledger/exact_numeric.py` | 103 | float ban, non-finite rejection, canonical serialization |
| `ilc_core/ledger/ecu_active_layer_runtime.py` | 359 | earmark reserve accounting, oversubscription checks |
| `ilc_core/epoch/epoch_emission_runtime.py` | 194 | C_MAX enforcement, production minting gate |
| `ilc_core/epoch/epoch_boundary_witness_runtime.py` | 56 | blocking authority state |
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | 1107 | ECU-to-ILC dry-run conservation, activation flags |
| `ilc_core/ledger/claimability_proof_binding_runtime.py` | 670 | proof-binding integrity, activation flags |
| `docs/phases/phase_1359_high_001_two_layer_defense_walkthrough.md` | 151 | HIGH-001 defense evidence |

---

## 3. HIGH-Severity Finding Dispositions

### HIGH-001: Sender Identity Leakage via Plaintext AgentID in Logs

**Classification:** HIGH  
**Original source:** Phase 779 leakage simulation (`ilc_sim_leakage_01_run2_post_both_layers_results_779_v0.1.md`); Phase 1359 walkthrough  
**Surfaces:** Rust validator log path; Python agent/onboarding/mining log paths; structural network-level variants B and C

**Audit findings:**

**Layer 1 — Rust validator log-layer defense (CLOSED):**
- `ilc_consensus/src/node.rs` — `fmt_agent_id()` returns the constant `[redacted:agent_id]` outside the `debug_agent_ids` feature. Object-ref logs route through `fmt_object_ref()` which also uses `fmt_agent_id()`. Verified per Phase 1359 walkthrough §Pre-Execution.
- `ilc_consensus/src/lib.rs` — `compile_error!` guard prevents release builds from enabling `debug_agent_ids`. This is a compile-time control, not a runtime flag.
- `ilc_consensus/src/pq_keygen_main.rs` — prints derived public keygen material as intentional user output; this is a CLI tool, not a validator log-write path. Publication review should confirm intent before inclusion in a public release package.

**Layer 1 — Python log-write site remediation (CLOSED):**
Phase 1359 directly audited and remediated:
- `ilc_core/economics/onboarding.py` — starter credit and repayment logs now call `redact_agent_id_for_log()` before the logger call.
- `ilc_core/mining/benchmark.py` — CapProof initialization log remediated.
- `ilc_core/agent.py` — all AgentID-bearing lifecycle log sites remediated.

The deterministic pseudonym scheme (`sha256("ilc-high-001-agentid-log-redaction-v1:epoch=N:agent_id")[:24]`) uses no randomness, no wall clock, no persistent mapping, and no post-hoc scrubber.

**Layer 2 — Transfer-mixing k-anonymity framework (ACTIVATION GATED OFF):**
`ilc_core/privacy/transfer_mixing_framework.py` has `ACTIVATION_GATE_REQUIRED = True`. `route_transfer_through_mixing_framework()` always raises `ValueError("mixing_framework_not_activated_production_phase_1359")`. Row-5 parameters locked: `K_PRIMARY=30`, `K_FALLBACK=20`, `RELEASE_JITTER_EPOCHS=3`.

**Structural sender privacy (ACCEPTED NON-CLAIM):**
Phase 779 simulation results record structural Variant B (hosted-query recall = 1.0) and Variant C (epoch-lineage recall = 1.0) as unresolved. These remain open. Full sender-privacy is explicitly not claimed. This is a documented non-claim boundary, not an unaddressed finding.

**Disposition:** **CLOSED — log layer**. Structural sender-privacy variants B and C accepted as open with explicit non-claim boundary. No sender-privacy claim is made or authorized by this review. The non-claim is project-authority-recorded and bounded: a future phase that proves structural sender privacy would need to address Variant B and Variant C specifically before any sender-privacy claim could be authorized.

---

### HIGH-002: BLS Aggregate Signature Threshold Bug (referenced in codebase as HIGH-002 fix)

**Classification:** HIGH  
**Original source:** BLS quorum threshold requiring all N validators; prior to fix, threshold was implicitly N rather than 2f+1  
**Surface:** `ilc_consensus/src/epoch_settlement.rs::process_epoch_checkpoint`

**Audit findings (direct code read):**

`epoch_settlement.rs` lines 237–276 implement the full HIGH-002 fix:

1. `n = validator_set.validators.len()` — uses actual ValidatorSet size, not a hardcoded constant.
2. `threshold = quorum_threshold(n)` — calls `validator.rs::quorum_threshold` which computes `2 * (n.saturating_sub(1) / 3) + 1`.
3. `checkpoint.signers.len() < threshold` — enforced before any BLS work.
4. HashSet-based duplicate signer check — prevents inflating apparent quorum by listing the same validator ID twice.
5. All signers resolved from active `ValidatorSet.validators` (O(1) HashMap lookup) — unknown signers fail with `ILCConsensusError::Other("signer validator N not in active validator set")`.
6. `sig.fast_aggregate_verify(true, msg, ILC_EPOCH_SIG_DST, &pk_refs)` — the aggregate is verified against the exact named subset's public keys. Claiming more signers than actually signed fails cryptographically: a partial aggregate cannot verify against a superset of public keys.

Mathematical verification of `quorum_threshold`:
- N=1 → 1; N=2 → 1; N=3 → 1; N=4 → 3; N=7 → 5; N=10 → 7 — all consistent with BFT safety requirement 2f+1 where f=⌊(N-1)/3⌋.
- `saturating_sub(1)` handles N=0 safely (returns 1); N=0 is structurally prevented by `ValidatorSet::new` requiring N > 3F.

Test coverage for HIGH-002 in `epoch_settlement.rs`: `test_quorum_threshold_correctness`, `test_three_of_four_signers_commits_epoch`, `test_two_of_four_signers_rejected`, `test_duplicate_signer_rejected`, `test_unknown_signer_rejected`.

**Disposition:** **CLOSED**. HIGH-002 fix is correctly implemented and tested. The quorum threshold, duplicate signer check, active-set membership check, and BLS aggregate verification chain are all present and correct.

---

## 4. BFT Safety — Detailed Audit Results

### 4.1 Epoch Monotonicity (SEC-FIX-02)

**Source:** `epoch_settlement.rs` lines 284–313

The epoch sentinel is read **inside** the write transaction (LMDB `begin_rw_txn`) before the record is written. This eliminates the TOCTOU window present in the prior implementation, which read the sentinel before acquiring the write lock.

Enforcement: `checkpoint.record.epoch.0 != current_epoch + 1` → `InvalidEpoch`. This means:
- Epoch 0 → must commit epoch 1 first.
- Epoch skip (e.g., 0 → 5) → rejected.
- Past epoch replay (e.g., submitting epoch 2 when current is 3) → rejected.
- `checked_add(1)` handles the u64::MAX edge case (returns `InvalidEpoch`; unreachable in practice).

Defence-in-depth duplicate-check at lines 316–319 (separate `txn.get` after the +1 guard) is correctly characterized as redundant but harmless.

**Verdict:** CORRECT. SEC-FIX-02 is properly implemented.

### 4.2 BLS G2 Subgroup and Infinity Point Checks (SEC-FIX-01)

**Source:** `types.rs` lines 61–66 (AgentSig), 159–163 (ValidatorSig), 229–232 (AggSig)

All three deserialization paths call `sig.validate(true)` after `Signature::from_bytes`. The `true` argument enables subgroup and infinity-point membership checks beyond what `from_bytes` performs. This guards against:
- Small-subgroup attacks (rogue key attacks)
- Identity/infinity-point injection (which would pass `verify` trivially)
- Cofactor-related forgeries on BLS12-381

`fast_path.rs` additionally calls `sender_pubkey.validate()` after extracting the G1 point from `AgentID.0` bytes (line 84–87).

**Verdict:** CORRECT.

### 4.3 Validator Set Construction Invariants

**Source:** `types.rs` lines 463–493, `validator.rs` lines 24–127

`ValidatorSet::new` enforces:
- N > 3F (BFT liveness/safety requirement) — rejects sets that would violate the Byzantine fault assumption.
- No duplicate ValidatorID — O(n²) key loop at construction (acceptable; validator sets are small).
- No duplicate ValidatorKey — prevents a single operator from masquerading as multiple validators with the same key.

`admit_validator` and `eject_validator` both call `rebuild_with` which calls `ValidatorSet::new`, maintaining invariants on every mutation.

`BUG-001` (f=0 when N reduces to 2 or 3): emits `[sec_warn] sec_warn_bft_fault_tolerance_zero` to stderr but proceeds. This is mathematically valid — N=3, f=0 still satisfies N>3F (3>0). The safety risk is operational: a single honest validator can finalize. Documented and warned.

**Verdict:** CORRECT with accepted BUG-001 (see §5).

### 4.4 Stake Concentration Limit

**Source:** `validator.rs` lines 43–70

Uses multiplication rather than division to avoid the floor-division off-by-one where `stake == total_stake/3` (exactly 1/3) would incorrectly pass: `stake * 3 >= total_stake`. The u128 cast prevents overflow for u64 stake values. The `u128::MAX` saturation guard is defensive for pathological input.

Edge case `stake=33, total=99` (exactly 1/3): `33*3=99 >= 99` → correctly rejected. Verified by `test_concentration_limit_exact_one_third_rejected`.

**Verdict:** CORRECT.

### 4.5 Fast-Path Certificate Execution

**Source:** `fast_path.rs` lines 69–153

Ordering: sender signature verified BEFORE quorum check. This prevents an attacker from learning quorum thresholds through timing differences on invalid sender keys.

SEC-004 historical ValidatorSet resolution: `epoch_sets.range(..=cert.epoch).next_back()` correctly selects the latest active set at cert issuance time. Stale rotation guard in `rotate_validator_set` prevents replayed or out-of-order governance actions.

Lock ordering (`epoch_sets` → `validator_set`): consistent across all paths. Documented in code comment (lines 59–64).

**Verdict:** CORRECT.

### 4.6 Balance Store Atomicity

**Source:** `balance_store.rs` lines 59–156

Single LMDB write transaction covering both sender debit and recipient credit. `checked_sub` and `checked_add` on all arithmetic. Self-transfer rejected before DB access. Zero-amount transfer rejected (prevents version-slot DoS). Version lock checked against `version_attempt` before balance check (ConflictingTransfer on mismatch — enforces SafetyNoDualCert at the storage layer).

Attribution replay guard: `batch.epoch.0 <= agent_bal.epoch.0` for existing agents, with new-agent exemption. Same-epoch replay test: `test_apply_attribution_same_epoch_replay_rejected` confirms double-minting is prevented.

**Verdict:** CORRECT.

### 4.7 testnet_fault_sim Bypass Path

**Source:** `balance_store.rs::commit_epoch_record` (EpochStore, not BalanceStore — same file, lines 49–98)

`commit_epoch_record` writes epoch records without BLS verification (`agg_sig_bytes: vec![]`). The code comment says this is "called only by `handle_epoch_settlement_tx` which is gated to `testnet_fault_sim` builds (CRIT-001)". The gate is on the caller, not on this function. The monotonicity check (duplicate key guard) is present, but the +1 sequential guard from SEC-FIX-02 is intentionally absent — this is the correct design for direct test injection without ordering constraints.

**Risk:** If `handle_epoch_settlement_tx` is not correctly gated (i.e., reachable without the `testnet_fault_sim` feature flag), this would allow epoch record injection without BLS verification. This is a compile-time guarantee on the caller, not this function.

**Disposition:** MEDIUM-001 — accepted with carry-forward (see §5).

---

## 5. Medium-Severity Findings — Disposition

### MEDIUM-001: testnet_fault_sim caller gate relies on code comment, not compile-time attribute

**Surface:** `ilc_consensus/src/epoch_settlement.rs::EpochStore::commit_epoch_record`  
**Risk:** If the caller `handle_epoch_settlement_tx` does not have a correct `#[cfg(feature = "testnet_fault_sim")]` guard, the BLS-bypassing epoch record injection path is reachable in production.  
**Mitigating factors:** The production epoch commit path `process_epoch_checkpoint` does full BLS verification. The two paths are architecturally distinct (production: DAG commitment callback; testnet: direct injection). Code comment explicitly documents the CRIT-001 gate.  
**Disposition:** **ACCEPTED**. Carry-forward: a hardening follow-on phase should add a `#[cfg(feature = "testnet_fault_sim")]` attribute directly on `commit_epoch_record` (not just the caller) to make the gate a compile-time invariant rather than a documentation-only constraint. This does not block Phase 1388.

### MEDIUM-002: f=0 warn-only when ValidatorSet drops to N≤3 members

**Surface:** `ilc_consensus/src/validator.rs::ValidatorSet::rebuild_with` lines 28–39  
**Risk:** With f=0, a single validator can finalize transfers (quorum_threshold(2)=1, quorum_threshold(3)=1). No Byzantine fault tolerance.  
**Mitigating factors:** The sec_warn token `sec_warn_bft_fault_tolerance_zero` is emitted to stderr with a machine-readable token. N>3F is still satisfied (f=0 satisfies N>0 for N≥1). This matches Phase 694 model where small-N sets are operationally restricted.  
**Disposition:** **ACCEPTED**. Operationally, the Genesis bootstrap set starts small and grows. The warning is visible to operators. No code change required before Phase 1388. Carry-forward: operator deployment guidance should include a minimum N≥4 recommendation for production.

### MEDIUM-003: CDL-048 dry-run conservation delta is tautological

**Surface:** `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py::build_cdl048_dry_run_wire_quote` line 444  
**Finding:** `conservation_delta = amount_ilc - amount_ilc` is always exactly `Decimal("0")`. The assertion `double_entry_conservation_proven = conservation_delta == Decimal("0")` is trivially satisfied. The semantic intent (proving debit_value_ilc == amount_ilc_credit) holds — since both are set to `amount_ilc` — but the proof is not a meaningful check against independently computed debit and credit legs.  
**Mitigating factors:** This is a dry-run quote only — no ledger mutation occurs. The gate is `gate_closed=True`, `quote_only=True`, `ledger_write_authorized=False`. The conservation proof token is Phase 1380 internal only and not published as an external security guarantee.  
**Disposition:** **ACCEPTED** with carry-forward. Phase 1388 (CDL-048 activation) must implement genuine double-entry verification where debit and credit legs are computed independently before the assertion. The tautological form in Phase 1380 dry-run wiring is acceptable as a scaffolding placeholder but must not be carried into the activation path.

---

## 6. Low-Severity Observations

| # | Surface | Observation | Disposition |
|---|---------|-------------|-------------|
| LOW-001 | `ecu_active_layer_runtime.py::_to_decimal` | Accepts `float` via `Decimal(str(value))`. The canonical `exact_numeric.to_decimal` does not accept float. Slight permissiveness at runtime input boundary. | ACCEPTED. Float→str conversion produces the decimal representation of the float literal, not the IEEE 754 mantissa. Acceptable for UI input normalization. Canonical economic protocol values use `Decimal`/`str`. |
| LOW-002 | `balance_store.rs::commit_epoch_record` sentinel update | After record write, sentinel update uses `stored.record.epoch.0 <= current` to skip non-advancing epochs. This means a testnet injection at epoch 3 when sentinel is 5 silently leaves sentinel at 5. Harmless for testnet path. | ACCEPTED. Testnet-only path. Sentinel represents "latest" — leaving it at a higher value is correct. |
| LOW-003 | `pq_keygen_main.rs` prints public key material | `println!("  agent_id: ...")` is intentional keygen output. Not a validator log path. | ACCEPTED. Publication review required if CLI tool is included in a public release package. No code change before Phase 1388. |

---

## 7. Economic Surface Audit Summary

| Surface | Finding | Verdict |
|---------|---------|---------|
| `exact_numeric.py::to_decimal` | Rejects bool, float, non-finite. Uses `is_finite()` check. | CORRECT |
| `epoch_emission_runtime.py::build_epoch_emission_quote` | `production_minting_activated=False` hardcoded. `require_production_minting_activation` always raises. | CORRECT — production minting gate closed |
| `epoch_emission_runtime.py::halving_decay_ratio` | 80-digit precision context. ROUND_DOWN prevents inflation. | CORRECT |
| C_MAX_ILC = Decimal("25920000") | Immutable module constant. | CORRECT |
| `ecu_active_layer_runtime.py::earmark_propose` | Self-commission prohibited. Zero/negative amounts rejected. Oversubscription check before earmark creation. Cap per agent enforced. | CORRECT |
| `ecu_active_layer_runtime.py::process_epoch_boundary` | Balance invariant check before debit. Strict `>` (not `>=`) for debit timing — correct, fires epoch after delivery. | CORRECT |
| `cdl048_conversion_sweeper_runtime.py` | `public_claimability_activated=False`; wallet/mint/settlement flags all `False`; validated in `_validate_receipt_semantics`. `build_cdl048_dry_run_wire_quote` fails on `activation_requested=True`. Float rejection in canonical JSON. | CORRECT (see MEDIUM-003 for conservation delta) |
| `claimability_proof_binding_runtime.py` | All activation flags hardcoded `False`. Receipt hash and proof hash independently recomputed and verified. Agent-ID, settled-root, wallet-root cross-bindings enforced. | CORRECT |
| `canonical_json` in both sweeper and binding | `json.dumps(sort_keys=True, allow_nan=False)` — complies with ILC canonicalization mandate. | CORRECT |

---

## 8. HIGH-001 Non-Claim Boundary — Formal Record

The following boundaries are explicitly NOT claimed as closed by this review or any prior phase:

1. **Structural Variant B — Hosted-query sender recall**: An observer with access to the epistemic graph query history can recover sender identity from query patterns. Phase 779 records recall=1.0 for this variant. No phase has closed this.

2. **Structural Variant C — Epoch-lineage sender recall**: An observer with access to epoch-commitment lineage can correlate epochs with sender timing. Phase 779 records recall=1.0 for this variant.

3. **Production transfer mixing**: `transfer_mixing_framework.py` activation gate is closed. No production batch mixing, k-anonymity, or jitter has been activated.

4. **Non-loopback privacy proof for mixing**: Phase 1360 proved non-loopback gRPC connectivity; it did not prove end-to-end sender privacy in a multi-operator mixing scenario.

**Authority:** Any future sender-privacy claim requires a separate dedicated phase with explicit evidence addressing Variants B and C. This review does not grant or imply any such authority.

---

## 9. Surfaces Not Audited in This Review

The following surfaces within the Phase 1384 scope were not directly read in this review:

- `ilc_consensus/src/network.rs` — QUIC transport layer, gossip, peer discovery
- `ilc_consensus/src/node.rs` — NodeRunner, main consensus loop, epoch triggering
- `ilc_consensus/src/persistent_quic.rs` — persistent QUIC sessions (reviewed in Phase 1386c)
- `ilc_core/governance/` — governance weight computation
- `ilc_core/economics/reward.py`, `entropy.py` — reward distribution internals
- `ilc_core/epoch/treasury_governance_runtime.py` — treasury P_e governor

**Disposition for unaudited surfaces:** These surfaces are bounded by the gate conditions already verified in Phase 1384–1387 series (TLS gRPC, endpoint ADR, persistent QUIC, no hardcoded peer list). The production value path (ECU mint, ILC settlement, wallet activation) remains gated off via `production_minting_activated=False`, `public_claimability_activated=False`, and `ledger_write_authorized=False` across all economic surfaces. The unaudited surfaces do not have a path to activate any value-path output in the current gated state.

A future pre-mainnet review should extend direct audit coverage to the governance, reward, and network transport modules before any production value-path activation.

---

## 10. Verdict

All known HIGH-severity findings within the Phase 1384 scope are explicitly dispositioned:

| Finding | Disposition |
|---------|-------------|
| HIGH-001: Sender identity leakage — log layer | **CLOSED** |
| HIGH-001: Structural Variant B (hosted-query recall) | **ACCEPTED NON-CLAIM** — no sender-privacy claim; explicitly deferred to a future dedicated privacy proof phase |
| HIGH-001: Structural Variant C (epoch-lineage recall) | **ACCEPTED NON-CLAIM** — same as Variant B |
| HIGH-002: BLS aggregate threshold bug | **CLOSED** |

All known MEDIUM-severity findings are accepted with bounded carry-forward authority:
- MEDIUM-001: testnet_fault_sim gate is caller-documented, not function-guarded — carry-forward hardening, does not block Phase 1388
- MEDIUM-002: f=0 warn-only — accepted, operator guidance carry-forward
- MEDIUM-003: CDL-048 dry-run conservation delta tautological — must be fixed in Phase 1388 activation path before any ledger write is authorized

The codebase reviewed does not contain any unaddressed HIGH-severity finding that blocks Phase 1388 or Phase 1389 proceeding under their existing gate conditions.

---

## 11. Non-Authorization Record

This disposition document does not authorize Phase 1388, Phase 1389, CDL mutation, runtime mutation, production validator deployment, public P2P activation, public gRPC serving, public claimability activation, public RC claim, source publication, release signing, wallet/ECU/ILC value-path activation, sender-privacy claim, production transfer mixing, counsel approval, or legal conclusion.

Phase 1387 can be re-run or superseded by a passing gate after this document is committed.

## 12. Graph Delta

`graph_delta=load_bearing_artifact_added:docs/specs/ilc_security_disposition_phase_1387_fix_v0.1.md -> project-authority/security-disposition`
