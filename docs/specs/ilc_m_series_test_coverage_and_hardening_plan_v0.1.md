# ILC M-Series: Test Coverage and Hardening Plan v0.1

**Date:** 2026-04-18  
**Author:** Claude Code  
**Status:** Active forward planning artifact — update at each M-phase close

This document captures every test coverage gap, known security concern, and
hardening task identified during M-001 through M-016 execution. Each item is
assigned a specific M-phase for resolution. This document is the authoritative
reference for "what tests are missing and when will they exist."

Codex, Claude, and Gemini should all consult this before drafting phase prompts
in the M-018+ range.

---

## 1. Items Resolved In-Phase (reference only)

These were identified and fixed immediately. Recorded here so the pattern is
not re-introduced.

| Item | Resolution | Phase |
|---|---|---|
| SEC-001: No agent sender sig on ECUTransfer | `sender_sig: AgentSig` added; verified before quorum | `acfcfd2d` |
| SEC-002: Bare VALIDATOR_DST constant | `validator_dst(network_id)` function; `test_cross_network_sig_rejected` | M-008 |
| SEC-003: No gossip sync for offline validators | `MissingCertSync`/`MissingCertResponse` added | M-008 |
| SEC-005: No LMDB map_size | `lmdb_map_size_bytes` in node config; single env | M-010 `83a1305d` |
| SEC-006: NullVerifier in TLS | `PinnedCertVerifier`; `test_spoofed_peer_id_rejected` | M-008 |
| SEC-007: 5 Dependabot CVEs (quinn/rustls/ring/rand) | Dep bump to quinn 0.11.9, rustls 0.23.38 | `7f5a0cdb` |
| SEC-008: O(N) MissingEpochSync wire growth | Cursor protocol (`latest_contiguous_epoch: u64`); 5 new tests | M-016 audit `57a9a777` |
| M-016 results overclaim: row-7 + anchor | Scope split (reconstruction/accessibility); results doc corrected | `57a9a777` |
| M-016 runner: REPO_ROOT not exported | `export REPO_ROOT` added before Python heredoc | `57a9a777` |

---

## 2. Open Items — Scheduled for M-018

M-018 is Workload F: Bounded Public Auditability. It activates the gRPC query
surface. The following hardening items are gated on M-018 because they require
the BLS verification infrastructure to exist before the tests can be written.

### 2.1 BLS Signature Verification for Epoch Records (SEC-009)

**Gap:** `process_epoch_checkpoint` has an explicit M-006 skip:
```
// Validation check over Sig components bounds -> (Skipped for M-006, validated manually via M-007 implementation)
```
The `AggSig` in `EpochCheckpoint` is never verified. Both the primary path
(`EpochSettlementTx → commit_epoch_record`) and the recovery path
(`MissingEpochResponse → commit_epoch_record`) commit epoch records without
BLS quorum verification.

**Impact:** Any validator with a valid mTLS cert can commit a forged epoch
record with an arbitrary state root. mTLS provides transport-layer peer
authentication but not application-layer quorum proof.

**When exploitable:** Only by a validator holding a pinned cert (SEC-006 gate).
Not exploitable by external actors. At N=4/F=1, a single Byzantine validator
could forge any epoch record.

**Resolution plan for M-018:**
1. Implement BLS AggSig verification in `process_epoch_checkpoint`. The
   verification must check that the AggSig covers the canonical serialization
   of `EpochSettlementRecord` under the active `ValidatorSet`.
2. Change `MissingEpochResponse` to carry `Vec<EpochCheckpoint>` (with AggSig)
   instead of `Vec<EpochSettlementRecord>` (without).
3. Route `handle_missing_epoch_response` through `process_epoch_checkpoint`
   so recovered records are verified before committing.
4. Store `EpochCheckpoint` (with AggSig) in LMDB, not just `EpochSettlementRecord`.
   This allows later offline verification of the quorum proof.

**Tests to add in M-018:**
- `test_forged_epoch_record_rejected` — send `MissingEpochResponse` with
  invalid AggSig; `process_epoch_checkpoint` must return an error
- `test_epoch_checkpoint_signature_persisted` — after commit, verify the
  AggSig can be read back from LMDB (proves proof-of-history is stored)
- `test_recovery_path_verifies_signature` — `handle_missing_epoch_response`
  with a valid-but-wrong AggSig (different message) is rejected
- `test_recovery_path_accepts_valid_checkpoint` — full round-trip: 2F+1
  validators sign an epoch record; recovered node accepts it via sync

**Token:** `sec_009_epoch_bls_verification_owned_by_m018`

---

### 2.2 AggSig Storage in LMDB (companion to SEC-009)

**Gap:** LMDB stores only `EpochSettlementRecord` bytes. The `AggSig`
(BLS aggregate signature proving ≥2F+1 validator quorum) is discarded at
commit time. A node cannot prove to an auditor that a committed epoch record
has valid quorum proof — only that it has the record.

**Resolution:** Part of the SEC-009 implementation. Store `EpochCheckpoint`
serialized form (including AggSig). Update `get_epochs_after` to return
`Vec<EpochCheckpoint>` so the proof travels with the record.

**Token:** `sec_009_aggsig_storage_companion_to_bls_verification`

---

### 2.3 gRPC Public Query Auditability (Workload F)

**Gap:** gRPC is a compile-time stub in `main.rs` (`"gRPC start is a stub
in M-010; skipping."`). The row-7 accessibility component of Workload D
(proving epoch data is publicly obtainable without operator cooperation) cannot
be demonstrated until a public query surface exists.

**Resolution plan for M-018:**
1. Activate the gRPC server with `GetEpochRecord` and `GetEpochChain` methods.
2. Expose read-only epoch records from LMDB via gRPC (Python or external client).
3. Demonstrate that a participant with only the validator's public IP can
   obtain the full epoch chain without operator credentials.
4. Update M-016 results doc §5 to record that the accessibility component
   is now closed by M-018.

**Tests to add in M-018:**
- Python test: `test_grpc_get_epoch_record_returns_correct_state_root`
- Python test: `test_grpc_no_write_methods_exposed` (re-verify the proto contract)
- Python test: `test_grpc_epoch_chain_reconstruction_without_local_lmdb`
  (full Workload D + F integration: client has no LMDB, reconstructs via gRPC)

**Token:** `sec_grpc_public_query_surface_owned_by_m018_workload_f`

---

## 3. Open Items — Scheduled for M-019

M-019 is Adversarial Hardening and Byzantine Fault Simulation. The following
items require M-018 (BLS verification) to be complete before they can be tested
meaningfully.

### 3.1 TLA+ Spec D: Epoch Sync Safety with Byzantine Peers

**Gap:** Specs A, B, C cover DAG liveness, fast-path cert safety, and
partition/heal. No spec covers the epoch sync protocol (`MissingEpochSync` /
`MissingEpochResponse`) under Byzantine validator behavior.

**Why it matters:** SEC-009 adds BLS verification to the recovery path. Spec D
would formally verify that:
1. A Byzantine validator cannot cause an honest validator to commit a forged
   epoch record (even if it holds a valid mTLS cert)
2. The cursor-based sync protocol terminates in bounded rounds for an honest
   validator rejoining after a partition

**Prerequisite:** SEC-009 (M-018) must be implemented first. Writing Spec D
before BLS verification exists would produce a spec that models a broken
protocol.

**Spec outline:**
```tla
VARIABLES committed_epochs, sync_requests, byzantine_set
ASSUME byzantine_set \subseteq Validators /\ Cardinality(byzantine_set) <= F

SafetyEpochSync == \A v \in Validators \ byzantine_set :
    \A ep \in committed_epochs[v] :
        HasValidAggSig(ep, Validators \ byzantine_set)

LivenessEpochSync == <>(\A v \in Validators \ byzantine_set :
    committed_epochs[v] = FullChain)
```

**Deliverable:** `docs/specs/tla/ilc_epoch_sync_safety.tla` + TLC model check
results. Add to M-019 gate script.

**Token:** `tla_spec_d_epoch_sync_safety_pre_m019`

---

### 3.2 `testnet_fault_sim` Feature Gate (SEC-007c)

**Gap:** 5 blocks in `node.rs` carry `TODO(pre-production): isolate under
#[cfg(feature = "testnet_fault_sim")]` but `Cargo.toml` has no `[features]`
table. These fault-injection paths (`PARTITION_BLOCK_PEERS`, `CENSOR_VALIDATOR`)
compile into production release builds unconditionally.

**Affected locations in node.rs:**
1. `partition_block_peers` field (struct declaration)
2. `dispatch()` inbound drop check
3. `EpochSettlementTx` censor check in `dispatch()`
4. `broadcast_certificate()` outbound filter
5. `send_to_peer()` outbound filter

**Resolution for M-019:**
1. Add to `Cargo.toml`:
   ```toml
   [features]
   testnet_fault_sim = []
   ```
2. Gate all 5 blocks with `#[cfg(feature = "testnet_fault_sim")]`.
3. Update M-015/M-016 runners to build with
   `cargo build --release --features testnet_fault_sim`.
4. Production build (M-020 audit prep) uses `cargo build --release` (no
   testnet_fault_sim) and `partition_block_peers` does not exist.

**Tests to add in M-019:**
- `test_production_build_has_no_fault_injection` — compile without feature,
  verify `PARTITION_BLOCK_PEERS` env var has no effect
- `test_fault_sim_build_partition_blocks_peer` — compile with feature, verify
  partition drop works as expected (existing M-015 behavior)

**Token:** `sec_007c_testnet_fault_sim_feature_gate_owned_by_m019`

---

### 3.3 Byzantine Epoch Forgery Simulation (requires SEC-009)

After BLS verification is in place (M-018), M-019 should run a simulated
Byzantine validator that:
1. Sends `MissingEpochResponse` with forged state roots (wrong CIDv1Root)
2. Sends responses with replayed AggSigs from different epochs

Expected outcomes (to verify):
- Honest validators reject forged records at the `process_epoch_checkpoint` gate
- Honest validators commit only records with valid quorum proofs
- The epoch chain on honest validators remains consistent

**Test:** `test_m019_byzantine_epoch_forge_rejected` (integration test using
the Tier-2 partition harness, with a modified testnet_client that sends
crafted forged records).

**Token:** `sec_009_byzantine_epoch_forgery_test_owned_by_m019`

---

### 3.4 SEC-004: Epoch / Validator Set Historical Binding (CDL-017 activation)

**Status:** OPEN dormant — only becomes active when CDL-017 is ratified.

`TransferCertificate` carries no epoch reference. After validator set rotation
(CDL-017 activation), a certificate from Epoch N could be evaluated against
the wrong `ValidatorSet`. Resolution requires:
1. `TransferCertificate` gains an `epoch: EpochSeq` field
2. `execute_certificate` resolves the historically active `ValidatorSet` for
   that epoch from LMDB before verifying signatures
3. Test: `test_ejected_validator_sig_rejected_after_epoch_boundary`

**Token:** `sec_004_epoch_validator_binding_owned_by_cdl_017_activation`

---

## 4. Open Items — Scheduled for M-020 (Audit Prep)

### 4.1 SEC-007a: Eliminate protoc System Dependency

**Gap:** `build.rs` shells out to system `protoc` binary. Fragile build dep.

**Immediate fix (M-020 or earlier):** Add `protoc-bin-vendored = "3"` as a
build-dependency and set `PROTOC` env in `build.rs`.

**Long-term fix (requires tonic 0.13+):** Use `protox` (pure Rust protoc).
Requires `tonic` + `tonic-build` upgrade from 0.11 → 0.13+.

**Token:** `sec_007a_protoc_build_dep_owned_by_m020_or_earlier`

---

### 4.2 SEC-007b: rand 0.8.6 Dependabot Alert

**Gap:** Not fixable without tonic 0.11→0.13+ upgrade (tower dep chain).
Not exploitable in ILC. Clearance path: tonic upgrade window.

**Token:** `sec_007b_rand_dep_clearance_with_tonic_upgrade`

---

### 4.3 state_extractor Binary Unit Tests

**Gap:** `state_extractor_main.rs` has no `#[cfg(test)]` block. Correctness
verified only by Python tests and committed JSON artifact.

**Resolution for M-020 (audit prep):**
- `test_extractor_empty_lmdb_exits_nonzero`
- `test_extractor_chain_complete_passes`
- `test_extractor_gap_in_chain_fails`
- `test_extractor_sentinel_mismatch_fails`

**Token:** `state_extractor_unit_tests_owned_by_m020`

---

## 5. Test Count Tracking

| Phase | Rust lib tests | Python tests | Notes |
|---|---|---|---|
| M-008 | 5 (network) | — | SEC-006 acceptance tests |
| M-010 | 30 | — | Full lib suite at M-010 close |
| M-015 | 30 | 11 | M-015 Python gate tests |
| M-016 | 30 | 12 | M-016 Workload D Python tests |
| M-016 audit | **35** | 12 | +5 SEC-008 cursor tests |
| M-018 target | 35 + 4 Rust + 3 Python | 15 | SEC-009 BLS + gRPC tests |
| M-019 target | 40+ Rust | 15 | Feature gate + Byzantine sim |
| M-020 target | 44+ Rust | 15 | Extractor unit tests |

---

## 6. Row-7 Replayability Closure Tracking

Row-7 requires: "censorship resistance, exitability, replayability must be provable."

| Component | Status | Phase | Evidence |
|---|---|---|---|
| Reconstruction step | **PROVEN** | M-016 `d5283dca` | state_extractor offline LMDB scan |
| Accessibility step (public query) | **DEFERRED** | M-018 | gRPC surface needed |
| Quorum proof stored | **DEFERRED** | M-018 | AggSig persistence (SEC-009) |
| Full row-7 closure | **OPEN** | M-018 | Requires accessibility + quorum proof |

`row_7_replayability_partial_m016_full_closure_requires_m018`

---

## 7. Document Maintenance Protocol

- Update §5 test count table at every M-phase close.
- Update §6 row-7 tracking when M-018 accessibility components are implemented.
- When SEC-009 is implemented (M-018), move it from §2 to §1 and update token.
- When Spec D is written (M-019), add TLC state count to the Spec C row in
  the TLA+ gap analysis doc.
- When `testnet_fault_sim` feature gate is implemented (M-019), remove the 5
  TODO markers from node.rs and update §3.2 status.

`m_series_test_coverage_plan_published_2026_04_18`
