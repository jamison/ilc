# M-018 Execution Guidance: Workload F — Bounded Public Auditability

**Date:** 2026-04-19  
**Prepared by:** Claude Sonnet 4.6  
**For:** Gemini (M-series lane executor)  
**Prerequisite:** M-017 COMPLETE — `run_m017_workload_e_verdict=pass`  
**Authority:** `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` §M-018

---

## 0. Tool Usage Rules — Read Before Touching Any Tool

**grep_search, search_files, semantic_search, and any other search tool WILL
time out on this repository. Do not call them. Ever. Not once.**

Use only direct file reads. Every file path you need is listed explicitly in
this document. If a path is not listed here, ask Claude rather than searching.

### Mandatory tool pattern

| Task | Correct tool | Wrong tool |
|---|---|---|
| Read a source file | `view_file <absolute-path>` | grep_search, search_files |
| Read a config | `view_file <absolute-path>` | any search |
| Check a log | `run_command tail -50 /tmp/ilc_m018_v1.log` | grep_search tool |
| Find a token in a log | `run_command grep "epoch_record_committed" /tmp/ilc_m018_v1.log` | grep_search tool |
| Build | `run_command ~/.cargo/bin/cargo build --release ...` | anything else |

`run_command` (bash execution) is safe. The search/grep *tools* are what freeze.
Using `grep` as a shell command inside `run_command` is fine.

### All file paths you need — pre-resolved, no searching required

```
# Source files to modify or read
ilc_consensus/src/types.rs            — EpochCheckpoint, AggSig, ValidatorSet, ValidatorKey
ilc_consensus/src/epoch_settlement.rs — process_epoch_checkpoint (SEC-009 target), EpochStore
ilc_consensus/src/network.rs          — MissingEpochResponse (carry Vec<EpochCheckpoint>)
ilc_consensus/src/node.rs             — dispatch(), handle_missing_epoch_response()
ilc_consensus/src/app_interface.rs    — gRPC service impl (add GetEpochRecord, GetEpochChain)
ilc_consensus/src/main.rs             — gRPC stub skip (activate in M-018)
ilc_consensus/src/config.rs           — NodeConfig (grpc_listen_addr field)
ilc_consensus/proto/ilc_app.proto     — gRPC proto (add new RPCs; EdgeRecord/HyperEdgeRecord already present)
ilc_consensus/Cargo.toml              — dependencies (blst, tonic, prost already present)
ilc_consensus/build.rs                — proto compilation (verify new messages compile cleanly)

# Reference runners and configs
tools/testbed/ilc_loopback_m017_runner.sh   — most recent runner; copy structure
config/mysticeti_testnet_M009/genesis.json
config/mysticeti_testnet_M009/validator_[1-4]_config.json
config/mysticeti_testnet_M009/certs/

# M-018 output files (you will create these)
tools/testbed/ilc_loopback_m018_runner.sh
docs/research/ilc_mysticeti_workload_f_results_M018_v0.1.md
docs/research/ilc_m018_auditability_report.json
docs/phases/phase_M018_workload_f_walkthrough.md
tests/test_phase_M018_workload_f_results.py

# Runtime logs
/tmp/ilc_m018_v1.log  /tmp/ilc_m018_v2.log
/tmp/ilc_m018_v3.log  /tmp/ilc_m018_v4.log
/tmp/ilc_m018_grpc_client.log
/tmp/ilc_m018_auditability_report.json
```

---

## 0. Critical Operating Rules — Read First

1. **No new consensus protocol.** Do not change DAG commit logic, fast-path
   cert logic, or transfer processing. BLS verification is added *at the
   settlement layer*, not inside the DAG. gRPC activation wires existing
   code; it adds no new consensus behavior.

2. **SEC-009 is the load-bearing gate.** Until BLS verification is in
   `process_epoch_checkpoint`, there is no quorum proof in the LMDB chain.
   Do SEC-009 before gRPC — the gRPC surface exposes records that must be
   verifiable before they are publicly readable.

3. **Do not change `grpc_listen_addr` config semantics.** Config already
   has the field. Activation in main.rs removes the skip block and wires
   the tonic server.

4. **Do not activate `PARTITION_BLOCK_PEERS` or `CENSOR_VALIDATOR`.**
   M-018 runner is a clean multi-epoch run for gRPC evidence capture.

5. **Proto forward-compatibility: `EdgeRecord` and `HyperEdgeRecord` are
   already in `ilc_app.proto`.** Do NOT remove or renumber them. Add new
   RPC response messages with `repeated EdgeRecord edges` fields per
   ADR-0031 (see §3.3).

6. **Carry M-017 runner patterns.** `set -euo pipefail`, trap cleanup,
   VALIDATOR_PIDS, `export REPO_ROOT`, retry-only-missing loop.

7. **AggSig serialization caveat.** `blst::min_pk::AggregateSignature`
   does not implement `serde::Serialize`. When storing `EpochCheckpoint`
   to LMDB, you must serialize AggSig as its underlying bytes. See §2.4
   for the exact approach.

---

## 1. Scope and Pass Criteria

M-018 closes four items that have been open since M-006:

| Criterion | Gate item | Pass condition |
|---|---|---|
| SEC-009 | BLS AggSig verification in `process_epoch_checkpoint` | Forged checkpoint rejected; valid checkpoint accepted; 4 new Rust tests pass |
| SEC-009 companion | AggSig stored in LMDB with epoch record | `EpochCheckpoint` (record + sig bytes) round-trips through LMDB |
| Workload F gRPC | gRPC server activated; `GetEpochRecord` and `GetEpochChain` methods live | Python client retrieves epoch chain from a running validator via gRPC without LMDB access |
| Row-7 accessibility | Public epoch chain retrievable without operator cooperation | `test_grpc_epoch_chain_reconstruction_without_local_lmdb` passes |

---

## 2. Implementation Sequence

Implement in this order. Each step builds on the previous.

### 2.1 LMDB schema: store EpochCheckpoint instead of EpochSettlementRecord

**File:** `ilc_consensus/src/epoch_settlement.rs`

**Current state** (line ~182):
```rust
let val_bytes = bincode::serialize(&checkpoint.record)
    .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;
txn.put(self.epoch_store.db, &current_key_bytes, &val_bytes, WriteFlags::empty())
```

Only `checkpoint.record` is stored. `checkpoint.sigs` (the AggSig) is discarded.

**Required change:** Store a serializable form of the full checkpoint. `AggSig`
wraps `blst::min_pk::AggregateSignature`, which does not implement `Serialize`.
Serialize it as bytes:

```rust
// At top of epoch_settlement.rs: add a serializable checkpoint form
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
struct StoredCheckpoint {
    record: EpochSettlementRecord,
    agg_sig_bytes: Vec<u8>,  // blst AggregateSignature::to_signature().serialize()
}
```

Then in `process_epoch_checkpoint`:
```rust
let sig_bytes = checkpoint.sigs.0.to_signature().serialize().to_vec();
let stored = StoredCheckpoint {
    record: checkpoint.record.clone(),
    agg_sig_bytes: sig_bytes,
};
let val_bytes = bincode::serialize(&stored)
    .map_err(|e| ILCConsensusError::Other(format!("Serialize error: {}", e)))?;
txn.put(self.epoch_store.db, &current_key_bytes, &val_bytes, WriteFlags::empty())
```

Add a `get_checkpoint` method to `EpochStore` that reads back a `StoredCheckpoint`
(in addition to the existing `get_epochs_after` which can remain for compatibility
but should also be updated to return `StoredCheckpoint`).

**Compatibility note:** Existing M-016 LMDB files store `EpochSettlementRecord`
bytes. The M-018 runner creates fresh tempfile LMDBs, so there is no migration
concern for testnet. Document this limitation in the walkthrough.

---

### 2.2 SEC-009: BLS AggSig verification

**File:** `ilc_consensus/src/epoch_settlement.rs`

**Current state** (line ~168):
```rust
pub fn process_epoch_checkpoint(&self, checkpoint: EpochCheckpoint) -> Result<CIDv1Root, ILCConsensusError> {
    // Validation check over Sig components bounds -> (Skipped for M-006, validated manually via M-007 implementation)
```

**Required change:** Add BLS verification before the LMDB write. The function
signature must accept the active `ValidatorSet` so it can check keys.

**Revised signature:**
```rust
pub fn process_epoch_checkpoint(
    &self,
    checkpoint: EpochCheckpoint,
    validator_set: &ValidatorSet,
) -> Result<CIDv1Root, ILCConsensusError>
```

**Verification logic to add immediately after the monotonicity check:**
```rust
// SEC-009: BLS AggSig verification
// M-018 testnet policy: verify aggregate signature against all N validator keys.
// Production policy (post-M-022): require 2F+1 signer bitmask; this is a known
// testnet simplification documented in the M-018 walkthrough.
let msg = bincode::serialize(&checkpoint.record)
    .map_err(|e| ILCConsensusError::Other(format!("BLS msg serialize error: {}", e)))?;
let sig = checkpoint.sigs.0.to_signature();
let pub_keys: Vec<blst::min_pk::PublicKey> = validator_set.validators
    .iter()
    .map(|(_, vk)| vk.0.clone())
    .collect();
let pk_refs: Vec<&blst::min_pk::PublicKey> = pub_keys.iter().collect();
const ILC_EPOCH_SIG_DST: &[u8] = b"ILC_EPOCH_SIG_BLS12381G2_XMD:SHA-256_SSWU_RO_NUL_";
let blst_result = sig.fast_aggregate_verify(
    true,
    msg.as_slice(),
    ILC_EPOCH_SIG_DST,
    &pk_refs,
);
if blst_result != blst::BLST_ERROR::BLST_SUCCESS {
    return Err(ILCConsensusError::InvalidSignature);
}
```

**Important testnet simplification:** `fast_aggregate_verify` verifies an
aggregate of ALL provided keys against ONE message. This works for testnet
where the consensus protocol aggregates all 4 validators' signatures before
calling `process_epoch_checkpoint`. For production (where only 2F+1 of N
sign), the protocol must provide a signer bitmask and verify against only
the signing subset. Document this clearly in the walkthrough as a known M-018
limitation to be addressed in M-022.

**DST constant:** Add `const ILC_EPOCH_SIG_DST` to `types.rs` or
`epoch_settlement.rs` and reference it consistently from both the signing
path (in `node.rs` or `validator.rs`) and the verification path. Do not
hard-code DST bytes in two places — they must match.

**Signing path:** Find where `EpochCheckpoint.sigs` is populated (somewhere
in `node.rs` DAG commit flow) and confirm the same DST is used. If it is
different, the verification will always fail. Read `node.rs` to locate the
signing call before writing the verification.

**Callers of `process_epoch_checkpoint`:** Update all call sites in `node.rs`
and `network.rs` to pass the active `ValidatorSet`. `NodeRunner` already holds
the genesis `ValidatorSet` — pass it through.

---

### 2.3 MissingEpochResponse: carry EpochCheckpoint instead of EpochSettlementRecord

**File:** `ilc_consensus/src/network.rs` (line ~41-43)

**Current state:**
```rust
MissingEpochResponse {
    records: Vec<EpochSettlementRecord>,
},
```

**Required change:**
```rust
MissingEpochResponse {
    records: Vec<StoredCheckpoint>,  // now carries AggSig bytes for recovery path verification
},
```

Where `StoredCheckpoint` is the serializable form defined in §2.1. This
requires `StoredCheckpoint` to be exported from `epoch_settlement.rs` and
imported in `network.rs`.

Update `handle_missing_epoch_response` in `node.rs` to:
1. Deserialize `StoredCheckpoint` from each record
2. Reconstruct `EpochCheckpoint` (decode `agg_sig_bytes` back to `AggSig`)
3. Call `process_epoch_checkpoint(checkpoint, &self.validator_set)` for each record
   (so recovery-path records are BLS-verified before being committed)

This closes the recovery-path gap noted in the SEC-009 analysis: previously,
recovered records bypassed BLS verification entirely.

---

### 3. Proto changes: new gRPC RPCs

**File:** `ilc_consensus/proto/ilc_app.proto`

Add these RPCs to the `ILCAppReadService` service block:

```proto
service ILCAppReadService {
    rpc GetBalance     (GetBalanceRequest)      returns (GetBalanceResponse) {}
    rpc GetEpoch       (GetEpochRequest)         returns (GetEpochResponse) {}
    rpc GetEpochRecord (GetEpochRecordRequest)   returns (GetEpochRecordResponse) {}
    rpc GetEpochChain  (GetEpochChainRequest)    returns (GetEpochChainResponse) {}
}
```

Add these message types **after** the existing `GetEpochResponse` message and
**before** the existing ADR-0031 forward-reservation block:

```proto
message GetEpochRecordRequest {
    uint64 epoch = 1;
}

// Subgraph Homomorphism Invariant (ADR-0031): this response returns a single
// epoch record — no edges field needed (single node, no inter-node edges).
message GetEpochRecordResponse {
    uint64 epoch      = 1;
    bytes  state_root = 2;   // 36 bytes: CIDv1Root
    bytes  agg_sig    = 3;   // BLS AggSig serialized bytes (96 bytes, blst compressed G1)
    bool   found      = 4;   // false if epoch does not exist
}

message GetEpochChainRequest {
    uint64 from_epoch    = 1;  // inclusive; 0 = from genesis
    uint64 to_epoch      = 2;  // inclusive; 0 = to current epoch
    bool   include_edges = 3;  // ADR-0031: set true to include EdgeRecord entries
}

// Subgraph Homomorphism Invariant (ADR-0031): when include_edges=true,
// if both source and target of an edge are in records[], that edge MUST
// appear in edges[]. Chain records form a linear sequence; sequential
// epoch edges are implied but not required here unless explicitly linked.
message GetEpochChainResponse {
    repeated GetEpochRecordResponse records  = 1;
    repeated EdgeRecord             edges    = 2;  // empty when include_edges=false
    repeated HyperEdgeRecord        hyperedges = 3;  // reserved; always empty in M-018
    bool                            chain_complete = 4;
}
```

**Do NOT remove or renumber `EdgeRecord` or `HyperEdgeRecord`.** They are
field-number-reserved per ADR-0031. Any response message carrying multiple
nodes must include the `edges` and `hyperedges` fields.

After adding new messages, run:
```bash
cargo build --release --manifest-path ilc_consensus/Cargo.toml 2>&1 | head -50
```
Confirm no proto compilation errors before proceeding.

---

### 3.1 gRPC service implementation

**File:** `ilc_consensus/src/app_interface.rs`

Add `GetEpochRecord` and `GetEpochChain` to the service trait bound imports and
implement them on `ApplicationInterface`:

```rust
// In the ilc_app mod block, add:
use ilc_app::{GetEpochRecordRequest, GetEpochRecordResponse,
              GetEpochChainRequest, GetEpochChainResponse};

// In IlcAppReadService impl:
async fn get_epoch_record(
    &self,
    request: Request<GetEpochRecordRequest>,
) -> Result<Response<GetEpochRecordResponse>, Status> {
    let epoch = request.into_inner().epoch;
    match self.epoch_store.get_checkpoint(epoch) {
        Ok(Some(stored)) => Ok(Response::new(GetEpochRecordResponse {
            epoch: stored.record.epoch.0,
            state_root: stored.record.state_root.0.to_vec(),
            agg_sig: stored.agg_sig_bytes,
            found: true,
        })),
        Ok(None) => Ok(Response::new(GetEpochRecordResponse {
            epoch, state_root: vec![], agg_sig: vec![], found: false,
        })),
        Err(e) => Err(Status::internal(format!("LMDB read error: {:?}", e))),
    }
}

async fn get_epoch_chain(
    &self,
    request: Request<GetEpochChainRequest>,
) -> Result<Response<GetEpochChainResponse>, Status> {
    let req = request.into_inner();
    // from_epoch=0 means start at epoch 1 (genesis sentinel is epoch 0)
    let from = if req.from_epoch == 0 { 1 } else { req.from_epoch };
    let current = self.epoch_store.get_current_epoch()
        .map_err(|e| Status::internal(format!("Epoch read error: {:?}", e)))?;
    let to = if req.to_epoch == 0 || req.to_epoch > current { current } else { req.to_epoch };

    let mut records = Vec::new();
    for ep in from..=to {
        match self.epoch_store.get_checkpoint(ep) {
            Ok(Some(stored)) => records.push(GetEpochRecordResponse {
                epoch: stored.record.epoch.0,
                state_root: stored.record.state_root.0.to_vec(),
                agg_sig: stored.agg_sig_bytes,
                found: true,
            }),
            Ok(None) => break,  // gap in chain — stop here; chain_complete=false
            Err(e) => return Err(Status::internal(format!("{:?}", e))),
        }
    }

    let chain_complete = records.len() as u64 == (to - from + 1);
    // include_edges: ADR-0031 reserved; chain is linear sequence — edges not populated in M-018
    Ok(Response::new(GetEpochChainResponse {
        chain_complete,
        records,
        edges: vec![],
        hyperedges: vec![],
    }))
}
```

You will also need to add `get_checkpoint(epoch: u64) -> Result<Option<StoredCheckpoint>, ...>`
to `EpochStore`. It reads the LMDB record for that epoch key and deserializes
as `StoredCheckpoint`.

---

### 3.2 gRPC server activation

**File:** `ilc_consensus/src/main.rs` (lines ~182-188)

**Current state (stub to remove):**
```rust
if let Some(grpc_addr) = cfg.grpc_listen_addr {
    eprintln!(
        "[m010_harness] grpc_listen_addr={} — gRPC start is a stub in M-010; skipping",
        grpc_addr
    );
    // gRPC server wiring is a follow-on M-series workload.
    // app_interface.rs provides the service impl; tonic transport wiring is M-011+.
}
```

**Replace with activation:**
```rust
if let Some(grpc_addr) = cfg.grpc_listen_addr {
    let app_iface = ApplicationInterface::new(
        Arc::clone(&balance_store),
        Arc::clone(&epoch_store),
    );
    let svc = ilc_app_read_service_server::IlcAppReadServiceServer::new(app_iface);
    let grpc_addr_parsed: std::net::SocketAddr = grpc_addr.parse()
        .expect("[m018] invalid grpc_listen_addr");
    tokio::spawn(async move {
        eprintln!("[m018] gRPC server listening on {}", grpc_addr_parsed);
        tonic::transport::Server::builder()
            .add_service(svc)
            .serve(grpc_addr_parsed)
            .await
            .expect("[m018] gRPC server failed");
    });
}
```

Add the required imports to `main.rs`:
```rust
use crate::app_interface::ilc_app::ilc_app_read_service_server;
use crate::app_interface::ApplicationInterface;
```

**Validator configs:** Add `grpc_listen_addr` to each validator config JSON.
The testbed uses loopback so safe values are:
- Validator 1: `"grpc_listen_addr": "127.0.0.1:50051"`
- Validator 2: `"grpc_listen_addr": "127.0.0.1:50052"`
- Validator 3: `"grpc_listen_addr": "127.0.0.1:50053"`
- Validator 4: `"grpc_listen_addr": "127.0.0.1:50054"`

Verify `config.rs` field `grpc_listen_addr: Option<String>` is already parsed
correctly (it should be — it was present since M-010).

---

## 4. Runner Specification

**File:** `tools/testbed/ilc_loopback_m018_runner.sh`

Copy structure from `ilc_loopback_m017_runner.sh`. Phase sequence:

```
Phase 0: Build release binary (cargo build --release)
Phase 1: Start 4 validators with grpc_listen_addr configured (fresh tempfile LMDBs)
Phase 2: Submit 20 epochs (retry-only-missing loop, 4 passes)
Phase 3: Confirm all 80 commits
Phase 4: Query V1's gRPC: GetEpochChain(from_epoch=1, to_epoch=20, include_edges=false)
         → Verify chain_complete=true, 20 records returned, each has agg_sig bytes
Phase 5: Query V1's gRPC: GetEpochRecord(epoch=10)
         → Verify found=true, state_root matches the committed record
Phase 6: Verify the AggSig bytes in the gRPC response are non-empty (96 bytes)
         → Confirms BLS verification path is active (sig was stored, not discarded)
Phase 7: Emit JSON report and verdict token
Phase 8: Stop all validators
```

**Python gRPC client for phases 4-6:** The runner should invoke a small Python
helper that uses the generated proto stubs to call `GetEpochChain` and
`GetEpochRecord` against V1's gRPC port. Write the helper inline in the runner
(via `python3 -c "..."`) or as a standalone file at
`tools/testbed/ilc_m018_grpc_audit_client.py`.

The proto stubs need to be generated for Python. Options:
1. Use `grpcurl` (if available) instead of Python proto stubs — simpler but
   less portable
2. Generate Python stubs from `ilc_app.proto` and call them from the runner

**Preferred:** Use `grpcurl` for the runner (avoid Python proto compilation in
the runner script). Install check: `which grpcurl || brew install grpcurl`.
Fallback: embed the gRPC calls in the Python test file with a running server.

For the runner, use `grpcurl`:
```bash
GRPC_V1="127.0.0.1:50051"
# GetEpochChain query
CHAIN=$(grpcurl -plaintext -d '{"from_epoch":1,"to_epoch":20}' \
    "$GRPC_V1" ilc_app.ILCAppReadService/GetEpochChain 2>/dev/null)
CHAIN_COMPLETE=$(echo "$CHAIN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('chainComplete','false'))")
RECORD_COUNT=$(echo "$CHAIN" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('records',[])))")
```

**Verdict emission:**
```bash
if [[ "$CHAIN_COMPLETE" == "true" && "$RECORD_COUNT" -eq 20 && ... ]]; then
    echo "run_m018_workload_f_verdict=pass"
else
    echo "run_m018_workload_f_verdict=fail"
fi
```

---

## 5. JSON Report Schema

`docs/research/ilc_m018_auditability_report.json`:

```json
{
  "phase": "M-018",
  "workload": "Workload F: Bounded Public Auditability",
  "date": "<ISO-8601>",
  "sec_009": {
    "bls_verification_implemented": true,
    "forged_epoch_rejected": true,
    "recovery_path_verified": true,
    "agg_sig_stored_in_lmdb": true,
    "testnet_simplification": "all-N verify (not 2F+1 bitmask); documented in walkthrough"
  },
  "grpc": {
    "server_activated": true,
    "get_epoch_record_tested": true,
    "get_epoch_chain_tested": true,
    "chain_complete": true,
    "epochs_returned": 20,
    "agg_sig_bytes_in_response": true
  },
  "row_7": {
    "accessibility_component_closed": true,
    "method": "grpc_get_epoch_chain_without_local_lmdb"
  },
  "adr_0031": {
    "edge_record_in_proto": true,
    "hyper_edge_record_in_proto": true,
    "include_edges_field_in_get_epoch_chain_request": true,
    "edges_field_in_get_epoch_chain_response": true
  },
  "overall_verdict": "workload_f_auditability_pass"
}
```

---

## 6. Results Doc Structure

`docs/research/ilc_mysticeti_workload_f_results_M018_v0.1.md`

```
## 1. Scope
## 2. SEC-009: BLS AggSig verification
   ### 2.1 Implementation approach
   ### 2.2 DST constant and signing-path alignment
   ### 2.3 Testnet simplification: all-N verify
   ### 2.4 Recovery path closure
## 3. LMDB schema: StoredCheckpoint
   ### 3.1 AggSig serialization approach
   ### 3.2 Compatibility note (pre-M018 LMDB files)
## 4. gRPC public query surface
   ### 4.1 Activation evidence
   ### 4.2 GetEpochRecord evidence
   ### 4.3 GetEpochChain evidence (chain_complete=true, 20 records, agg_sig present)
## 5. Row-7 accessibility closure
## 6. ADR-0031 forward-compatibility confirmation
## 7. Known limitations (testnet scope)
## 8. Overall verdict
```

The verdict token `run_m018_workload_f_verdict=pass` must appear in §8.

---

## 7. Rust Test Requirements (new tests in existing test modules)

**In `epoch_settlement.rs` `#[cfg(test)]` block — add 4 new tests:**

1. `test_forged_epoch_record_rejected`  
   Create a 2-validator `ValidatorSet` with keys K1 and K2. Sign a record with
   only K1. Aggregate. Call `process_epoch_checkpoint` with `ValidatorSet{K1,K2}`.
   Assert `Err(ILCConsensusError::InvalidSignature)` is returned (because only
   one key signed but both are required under all-N policy).

2. `test_valid_checkpoint_accepted`  
   Sign the record with K1 and K2. Aggregate. Call `process_epoch_checkpoint`
   with `ValidatorSet{K1,K2}`. Assert `Ok(state_root)`.

3. `test_epoch_checkpoint_agg_sig_stored_in_lmdb`  
   After a successful `process_epoch_checkpoint`, call `get_checkpoint(epoch)`
   and assert `stored.agg_sig_bytes` is non-empty (96 bytes for compressed G1).

4. `test_recovery_path_verifies_signature`  
   Simulate a `MissingEpochResponse` with a `StoredCheckpoint` containing a
   forged (wrong-message) sig. Assert `process_epoch_checkpoint` returns
   `Err(ILCConsensusError::InvalidSignature)`.

**In `app_interface.rs` `#[cfg(test)]` block — add 3 new async tests:**

5. `test_get_epoch_record_returns_stored_agg_sig`  
   Commit a checkpoint; call `get_epoch_record`; assert `found=true`,
   `agg_sig.len() == 96`.

6. `test_get_epoch_chain_chain_complete`  
   Commit epochs 1-5; call `get_epoch_chain(from=1, to=5)`; assert
   `chain_complete=true`, `records.len() == 5`.

7. `test_get_epoch_chain_gap_returns_partial`  
   Commit epochs 1-3 then 5 (skip 4); call `get_epoch_chain(from=1, to=5)`;
   assert `chain_complete=false`, `records.len() == 3`.

All 7 new Rust tests must pass: `cargo test --manifest-path ilc_consensus/Cargo.toml -q`

---

## 8. Python Test File Specification

`tests/test_phase_M018_workload_f_results.py` — minimum 16 tests.

| # | Test | What it checks |
|---|---|---|
| 1 | `test_results_doc_exists` | Results doc present |
| 2 | `test_results_doc_verdict_pass` | `run_m018_workload_f_verdict=pass` in doc |
| 3 | `test_auditability_report_exists_and_parseable` | JSON present and valid |
| 4 | `test_report_sec_009_implemented` | `sec_009.bls_verification_implemented == true` |
| 5 | `test_report_forged_rejected` | `sec_009.forged_epoch_rejected == true` |
| 6 | `test_report_agg_sig_stored` | `sec_009.agg_sig_stored_in_lmdb == true` |
| 7 | `test_report_recovery_path_verified` | `sec_009.recovery_path_verified == true` |
| 8 | `test_report_grpc_activated` | `grpc.server_activated == true` |
| 9 | `test_report_chain_complete` | `grpc.chain_complete == true` |
| 10 | `test_report_epochs_returned` | `grpc.epochs_returned == 20` |
| 11 | `test_report_agg_sig_in_grpc_response` | `grpc.agg_sig_bytes_in_response == true` |
| 12 | `test_report_row7_closed` | `row_7.accessibility_component_closed == true` |
| 13 | `test_report_adr_0031_edge_record` | `adr_0031.edge_record_in_proto == true` |
| 14 | `test_report_adr_0031_include_edges_field` | `adr_0031.include_edges_field_in_get_epoch_chain_request == true` |
| 15 | `test_runner_emits_verdict_token` | `run_m018_workload_f_verdict=pass` in runner |
| 16 | `test_overall_verdict_field` | `overall_verdict == "workload_f_auditability_pass"` |

---

## 9. Walkthrough Specification

`docs/phases/phase_M018_workload_f_walkthrough.md` must cover:

- What this phase proved (BLS quorum proof stored, public chain reconstruction via gRPC)
- SEC-009 implementation: where verification was added, the DST constant chosen,
  the signing-path alignment check
- **Testnet simplification documented:** all-N verify (not 2F+1 bitmask). Name
  this explicitly as a known gap for M-022 (convergence window) to close with
  the production ValidatorSet signer tracking
- `StoredCheckpoint` LMDB schema change and AggSig serialization approach
- `MissingEpochResponse` migration to carry `StoredCheckpoint`
- gRPC activation: which config fields, how tonic server is spawned
- ADR-0031 forward-reservation confirmation: `EdgeRecord` and `HyperEdgeRecord`
  unchanged; `GetEpochChainResponse` carries `edges` and `hyperedges` fields
- Row-7 accessibility: how `GetEpochChain` closes the accessibility component
  (public read without operator cooperation)
- What comes next: M-019 (adversarial hardening + TLA+ Spec D)

---

## 10. Verdict Conditions

| Condition | Required for pass |
|---|---|
| `run_m018_workload_f_verdict=pass` in runner | Yes |
| `overall_verdict: "workload_f_auditability_pass"` in JSON | Yes |
| All 7 new Rust tests pass (35+ total) | Yes |
| All 16+ Python tests pass | Yes |
| `process_epoch_checkpoint` signature takes `&ValidatorSet` | Yes |
| `StoredCheckpoint` stored in LMDB (not raw `EpochSettlementRecord`) | Yes |
| `MissingEpochResponse` carries `StoredCheckpoint` | Yes |
| gRPC server starts without panic at validator launch | Yes |
| `GetEpochChain` returns `chain_complete=true` for 20 committed epochs | Yes |
| `GetEpochRecord` returns non-empty `agg_sig` bytes | Yes |
| `EdgeRecord` and `HyperEdgeRecord` field numbers unchanged in proto | Yes |
| `include_edges` field present in `GetEpochChainRequest` | Yes |
| `edges` and `hyperedges` fields present in `GetEpochChainResponse` | Yes |
| Testnet simplification documented in walkthrough | Yes |
| No new consensus protocol changes | Yes |

`run_m018_workload_f_verdict=pass` is the gate token for M-019.

---

## 11. Scope Boundaries (What NOT to Do)

- **Do not add a 2F+1 signer bitmask to `EpochCheckpoint`.** That is a production
  design question for M-022. The testnet all-N verify is the honest current posture.
- **Do not add `testnet_fault_sim` feature gate.** That is SEC-007c, M-019.
- **Do not implement TLA+ Spec D.** That is M-019, after SEC-009 exists.
- **Do not change DAG commit rules, fast-path logic, or transfer processing.**
- **Do not add write methods to the gRPC service.** `ILCAppReadService` is
  read-only by design. Adding mutations would violate the CDL-approved boundary.
- **Do not populate `edges` or `hyperedges` in `GetEpochChainResponse`.**
  Reserve the fields; leave them empty. Subgraph query semantics are post-mainnet
  (ADR-0029/0030).
- **Do not change `EdgeRecord` or `HyperEdgeRecord` field numbers.** These are
  wire-format-reserved per ADR-0031. Changing them is a breaking change.
- **Do not claim row-7 is fully closed.** The accessibility component is closed
  by M-018. The quorum proof is now stored (SEC-009). Full row-7 closure is
  declared by the Codex lane in Window 739-744 after runtime form evidence is
  captured.

---

## 12. Carry-Forward to M-019

After M-018 is approved:

1. **TLA+ Spec D** — Epoch sync safety with Byzantine peers. Requires SEC-009 to
   be implemented (cannot model BLS-verified sync before the impl exists). Spec D
   should cover: valid-quorum epoch records accepted, forged records rejected,
   recovery-path record propagation doesn't amplify Byzantine influence.

2. **SEC-007c** — `testnet_fault_sim` feature gate. Gate the 5 blocks in
   `node.rs` under `#[cfg(feature = "testnet_fault_sim")]`. Runners that need
   fault injection build with `--features testnet_fault_sim`.

3. **M-019 adversarial hardening** — Byzantine fault simulation using
   `PARTITION_BLOCK_PEERS` and `CENSOR_VALIDATOR` under the feature gate.
   Targets: f=1 partition + BFT recovery under verified epoch sync.

4. **Production 2F+1 signer bitmask** — `EpochCheckpoint` needs a signers set
   for partial-quorum verification. Design deferred to M-022 convergence window
   where ValidatorSet management becomes authoritative.

These items are documented in:
- `docs/specs/ilc_m_series_test_coverage_and_hardening_plan_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

`m018_approved_opens_m019`  
`run_m018_workload_f_verdict=pass_required_before_m019`  
`sec_009_closes_m018_opens_spec_d_tla_plus`  
`row_7_accessibility_closed_m018`
