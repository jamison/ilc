# M-012 Verbose Guidance — Full BFT ECUTransfer Round-Trip

**Date:** 2026-04-17  
**For:** Gemini (owner), local reviewer / Sonnet (auditor)  
**Phase:** M-012  
**Prerequisite:** M-011 COMPLETE (`83a1305d` main, `ef244272` backfill)  
**Verdict target:** `binary_complete` — tooling committed and smoke-tested; real run on 4 validators follows in M-013

---

## 1. What M-012 Is and Why It Exists

M-011 (`testnet_client`) can only **inject** messages into validators — it cannot
receive responses. This is by design: the client binds to `"0.0.0.0:0"` (ephemeral
port, no QUIC listener), so when a validator calls `send_to_peer(from, AckFor)` in
response to a `BroadcastHonest`, there is no socket for the `AckFor` to land on.

Reference: `ilc_consensus/src/testnet_client_main.rs` line 207:
```rust
let bind_addr: SocketAddr = "0.0.0.0:0".parse().unwrap();
let network = PeerNetwork::new_client(bind_addr, peer_certs, my_cert_der, my_key_der)
```

The `--msg broadcast` mode in M-011 demonstrates the first half of the fast path
(BroadcastHonest injection), but not the round-trip. The full Mysticeti owned-object
fast path is:

```
Client ──BroadcastHonest──► Validator 1 ──AckFor──► Client
Client ──BroadcastHonest──► Validator 2 ──AckFor──► Client
Client ──BroadcastHonest──► Validator 3 ──AckFor──► Client
Client ──BroadcastHonest──► Validator 4 ──AckFor──► Client
                                                      │
                        Client accumulates AckFor ◄──┘
                        (need 2F+1 = 3 for N=4, F=1)
                                │
                        Client forms TransferCertificate
                                │
Client ──Certificate──► Validator 1 (execute_certificate → LMDB)
Client ──Certificate──► Validator 2 (execute_certificate → LMDB)
Client ──Certificate──► Validator 3 (execute_certificate → LMDB)
Client ──Certificate──► Validator 4 (execute_certificate → LMDB)
```

M-012 closes this gap by extending `testnet_client` to run the full round-trip.

---

## 2. How AckFor Routing Works (Read This First)

Understanding the existing routing is critical before writing M-012 code.

### 2a. from is self-reported via GossipEnvelope.peer_id

In `node.rs`, `dispatch()` extracts `from` as:
```rust
// ilc_consensus/src/node.rs line 156
let from = envelope.peer_id;
```

`envelope.peer_id` is whatever the *sender* put in the `GossipEnvelope`. It is **not**
derived from TLS identity. The TLS cert is used only to accept/reject the mTLS
connection (`PinnedCertVerifier` / `client_auth_mandatory = true`) — not to assign
a peer_id.

### 2b. AckFor is sent back to the peer_id in the envelope

`handle_broadcast_honest` calls:
```rust
// ilc_consensus/src/node.rs lines 246-249
self.send_to_peer(
    from,
    GossipMessage::AckFor { object_ref, sig },
).await
```

`send_to_peer` resolves the address by looking up `from` (a `ValidatorID`) in
`self.peer_addrs`:
```rust
// ilc_consensus/src/node.rs lines 428-431
let addr = self.peer_addrs.iter()
    .find(|(id, _)| *id == peer_id)
    .map(|(_, addr)| *addr)
    .ok_or_else(|| ILCConsensusError::Other(format!("Unknown peer {}", peer_id.0)))?;
```

`peer_addrs` is populated from the `peers` array in the validator's JSON config
(`RawNodeConfig.peers` → `Vec<RawPeer>` → `Vec<PeerAddr>`):
```rust
// ilc_consensus/src/config.rs lines 50-53, 63, 85-88
struct RawPeer {
    validator_id: u32,
    addr: String,
}
// ...
peers: Vec<RawPeer>,
// ...
pub struct PeerAddr {
    pub validator_id: u32,
    pub addr: std::net::SocketAddr,
}
```

### 2c. Consequence for M-012

For a validator to successfully route `AckFor` back to the testnet_client:

1. The client must claim a `peer_id` that exists in each validator's `peers` config array
2. The address registered for that `peer_id` in each validator config must be the client's actual QUIC listen address
3. The client's TLS cert DER must be in each validator's `peer_cert_dir` (for `PinnedCertVerifier` to accept the connection)
4. The client must be running a QUIC *server* endpoint at that address so it can receive the `AckFor` response

---

## 3. M-012 Implementation Plan

### 3a. Assign the client a peer_id and listen address

Add `ValidatorID(5)` as the client identity (validators 1-4 use IDs 1-4 in the
testnet config). Register the client's listen address (e.g., `0.0.0.0:9500` or a
Tailscale/LAN address for real multi-machine runs) in each validator's JSON config
under `peers`:

```json
// config/mysticeti_testnet_M009/validator_1_config.json (example)
"peers": [
  {"validator_id": 2, "addr": "127.0.0.1:9002"},
  {"validator_id": 3, "addr": "127.0.0.1:9003"},
  {"validator_id": 4, "addr": "127.0.0.1:9004"},
  {"validator_id": 5, "addr": "127.0.0.1:9500"}   // ← client
]
```

Repeat for validators 2, 3, 4. The client address differs on multi-machine runs
(use the machine's Tailscale IP).

### 3b. Generate a TLS cert for the client and register it

The `--gen-tls` harness mode generates certs for validators 1-4. Add a client cert
generation step to `run_mysticeti_testnet_M011.sh` (or create
`run_mysticeti_testnet_M012.sh`):

```bash
# Generate client TLS cert
openssl req -x509 -newkey rsa:2048 -days 3650 -nodes \
    -subj "/CN=ilc-testnet-client" \
    -keyout config/mysticeti_testnet_M009/client_key.pem \
    -out    config/mysticeti_testnet_M009/client_cert.pem

# Convert to DER for peer_cert_dir registration
openssl x509 -in  config/mysticeti_testnet_M009/client_cert.pem \
             -out config/mysticeti_testnet_M009/client_cert.der \
             -outform DER

# Copy client_cert.der into each validator's peer_cert_dir
cp config/mysticeti_testnet_M009/client_cert.der \
   config/mysticeti_testnet_M009/validator_1_peers/client_cert.der
# ... repeat for validators 2, 3, 4
```

### 3c. Add `--msg full_transfer` mode to testnet_client

Extend `testnet_client_main.rs` with a new `MsgType::FullTransfer` variant.

**New CLI args for this mode:**
```
--msg full_transfer
--sender-key <file>      # 64-char hex BLS secret key (from keygen --out)
--to <96hex>             # recipient agent public key
--amount <u64>           # micro-ECU amount
--version <u64>          # ObjectRef version (0 for first transfer)
--listen-addr <addr>     # QUIC listen address for AckFor (e.g., 0.0.0.0:9500)
--client-cert <pem>      # client TLS cert (not a validator cert)
--client-key <pem>       # client TLS key
--validators <addr,...>  # comma-separated list of all 4 validator addresses
--validator-certs <der,...>  # comma-separated DER paths for all 4 validators
```

**Pseudocode for full_transfer:**

```rust
async fn run_full_transfer(args: FullTransferArgs) -> Result<(), Box<dyn Error>> {
    // 1. Build the ECUTransfer + sender_sig (same as --msg broadcast)
    let transfer = build_transfer(&args)?;
    let object_ref = transfer.object_ref;

    // 2. Bind a QUIC server endpoint at --listen-addr using client cert
    //    (use PeerNetwork::new_server, not new_client)
    let client_server = PeerNetwork::new_server(
        args.listen_addr,
        all_validator_cert_map,   // peer_certs: validator DERs keyed by id
        client_cert_der,
        client_key_der,
    )?;

    // 3. Also build an outbound client endpoint to connect to validators
    let outbound = PeerNetwork::new_client(
        "0.0.0.0:0".parse()?,
        all_validator_cert_map,
        client_cert_der,
        client_key_der,
    )?;

    // 4. Send BroadcastHonest to all 4 validators with peer_id = 5
    for (validator_id, validator_addr) in &args.validators {
        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: ValidatorID(5),   // client's registered peer_id
            payload: GossipMessage::BroadcastHonest(transfer.clone()),
        };
        let conn = outbound.endpoint.connect(*validator_addr, "localhost")?.await?;
        let (send, _recv) = conn.open_bi().await?;
        outbound.transmit(send, envelope).await?;
        eprintln!("[m012_client] sent BroadcastHonest to validator {}", validator_id);
    }

    // 5. Accept AckFor responses on the server endpoint
    //    Collect until we have 2F+1 = 3 acks (with N=4, F=1)
    let quorum = 2 * 1 + 1;  // F=1
    let mut acks: Vec<(ValidatorID, ValidatorSig)> = Vec::new();

    while acks.len() < quorum {
        let incoming = client_server.endpoint.accept().await
            .ok_or("server endpoint closed")?;
        let conn = incoming.await?;
        let (_, recv) = conn.accept_bi().await?;
        let envelope = client_server.receive(&conn, recv).await?;
        if let GossipMessage::AckFor { object_ref: ack_ref, sig } = envelope.payload {
            if ack_ref == object_ref {
                let from = envelope.peer_id;
                // Deduplicate: one sig per validator
                if !acks.iter().any(|(id, _)| *id == from) {
                    acks.push((from, sig));
                    eprintln!("[m012_client] received AckFor from validator {} ({}/{})",
                        from.0, acks.len(), quorum);
                }
            }
        }
    }

    // 6. Assemble TransferCertificate
    let cert = TransferCertificate { transfer, sigs: acks };
    eprintln!("[m012_client] certificate assembled — broadcasting to all validators");

    // 7. Broadcast Certificate to all 4 validators
    for (validator_id, validator_addr) in &args.validators {
        let envelope = GossipEnvelope {
            frame_type: 0x00,
            peer_id: ValidatorID(5),
            payload: GossipMessage::Certificate(cert.clone()),
        };
        let conn = outbound.endpoint.connect(*validator_addr, "localhost")?.await?;
        let (send, _recv) = conn.open_bi().await?;
        outbound.transmit(send, envelope).await?;
        eprintln!("[m012_client] sent Certificate to validator {}", validator_id);
    }

    eprintln!("[m012_client] full_transfer_round_trip_complete");
    Ok(())
}
```

### 3d. Note on using PeerNetwork::new_server for the client

`PeerNetwork::new_server` (defined in `ilc_consensus/src/network.rs` lines 91-121)
sets up a QUIC `Endpoint` in server mode: it calls `Endpoint::server(server_config, bind_addr)`
and uses `PinnedCertVerifier` for client cert verification
(`client_auth_mandatory = true`). This is exactly the same TLS posture as the validators.

For M-012, the client uses `new_server` to accept incoming QUIC connections from
validators sending `AckFor` back. The client's `PinnedCertVerifier` should accept
all 4 validator certs (so validators can connect to send AckFor).

The `receive` method (on `PeerNetwork`) reads the length-prefixed bincode envelope:
```rust
// ilc_consensus/src/network.rs line 174 (transmit is the mirror)
// receive: read 4-byte big-endian length, then read that many bytes, bincode-deserialize
```
Check `network.rs` for the exact `receive` implementation and replicate its framing
in the accept loop.

---

## 4. mTLS Constraint Summary

The validator's `PinnedCertVerifier` (`client_auth_mandatory = true`) means every
inbound QUIC connection must present a cert that is in the validator's `peer_cert_dir`.

For M-012:
- Each validator's `peer_cert_dir` must contain `client_cert.der` (the new client cert)
- The harness `--gen-tls` or a new `--gen-client-tls` mode handles this
- The client presents `client_cert.pem`/`client_key.pem` (not a validator's cert)
- When the client acts as a *server* accepting validator responses, the validator
  (acting as a QUIC client connecting back to send AckFor) must present its own cert —
  which the client's `PinnedCertVerifier` must also recognize. So the client's
  `peer_certs` map must contain all 4 validator certs.

This is symmetric: validators accept the client cert; the client accepts validator certs.

References:
- `ilc_consensus/src/network.rs` lines 64-89 (`PinnedCertVerifier`, `client_auth_mandatory`)
- `docs/phases/phase_M011_workload_a_walkthrough.md` §mTLS constraint section

---

## 5. Quorum Arithmetic (N=4, F=1)

The quorum threshold is `2F+1 = 3`. This is *not* hardcoded in the client — it must
be read from genesis or passed as a config argument. In the existing `NodeRunner`:
```rust
// ilc_consensus/src/node.rs line 262
let quorum = 2 * self.f + 1;
```

For `testnet_client`, F=1 is known from genesis (`genesis.json` has `"f": 1`).
The client should either:
- Read `genesis.json` to extract `f`, or
- Accept `--f <value>` as a CLI argument (simpler for testnet use)

Do **not** hardcode `quorum = 3`. The parameter must be explicit so it works
for different testnet configurations.

---

## 6. Deliverables

| Artifact | Description |
|---|---|
| `ilc_consensus/src/testnet_client_main.rs` | Extended with `--msg full_transfer` mode |
| `tools/run_mysticeti_testnet_M012.sh` | Harness: `--gen-client-tls`, `--update-peer-configs`, `--local-smoke`, `--operator-guide` |
| `docs/research/ilc_mysticeti_testnet_M012_full_bft_transfer_v0.1.md` | Artifact doc (8+ headings, verdict, design decisions) |
| `tests/test_phase_M012_full_bft_transfer.py` | Phase test (8+ tests: content + commit-presence checks) |
| `docs/phases/phase_M012_full_bft_transfer_walkthrough.md` | Backfill walkthrough |

**Two-commit structure (mandatory):**
- **Main commit**: all 5 deliverables above (exact set, no extras)
- **Backfill commit**: walkthrough + STATUS.md entry

**Verdict line in artifact**: `` `run_m012_full_bft_transfer_verdict=binary_complete` ``

---

## 7. Audit Checklist (Local Reviewer / Sonnet)

At the review stage, verify each of the following against the actual committed code:

**Protocol correctness:**
- [ ] Client binds a real QUIC server endpoint at a non-ephemeral address (`new_server`, not just `new_client`)
- [ ] Client sends `BroadcastHonest` to ALL 4 validators (not just one)
- [ ] `GossipEnvelope.peer_id` in BroadcastHonest is set to the client's registered peer_id (5), not a validator's id
- [ ] Client accepts incoming QUIC connections and reads `AckFor` from the stream (real network receive)
- [ ] AckFor deduplication: at most one sig per `ValidatorID` (mirrors `node.rs` line 270)
- [ ] Quorum threshold is `2 * f + 1` where `f` is read from config/genesis — NOT hardcoded as 3
- [ ] `TransferCertificate` is assembled only after `sigs.len() >= quorum`
- [ ] Certificate is broadcast to ALL 4 validators after assembly

**mTLS:**
- [ ] Client cert (`client_cert.pem`/`client_cert.der`) is distinct from any validator cert
- [ ] Client cert DER is present in each validator's `peer_cert_dir`
- [ ] Client's validator cert map includes all 4 validator DERs (for accepting their inbound AckFor connections)
- [ ] Harness `--gen-client-tls` (or equivalent) generates and distributes the client cert

**Config correctness:**
- [ ] Each validator's `peers` array includes an entry for the client (`validator_id: 5`) with the correct address
- [ ] Client's `peer_id = 5` is consistent across all envelope sends
- [ ] Harness `--update-peer-configs` (or equivalent) patches all 4 validator configs

**Existing functionality preserved:**
- [ ] `--msg epoch_settlement` still works unchanged
- [ ] `--msg broadcast` (fire-and-forget) still works unchanged
- [ ] 30+ Rust unit tests still pass: `cargo test -p ilc_consensus`
- [ ] M-011 10/10 phase tests still pass: `python3 -m pytest tests/test_phase_M011_workload_a_liveness.py`

**Two-commit discipline:**
- [ ] Main commit contains exactly the 5 deliverables listed in §6 — no extra files
- [ ] Backfill commit adds walkthrough + STATUS.md entry with correct commit hash
- [ ] STATUS.md M-012 entry is present, has `binary_complete` verdict, and links to both commits

**Document structure:**
- [ ] Artifact doc has ≥ 8 required headings
- [ ] Artifact doc has exactly one verdict line: `` `run_m012_full_bft_transfer_verdict=binary_complete` ``
- [ ] Walkthrough documents the design decisions (especially: why two endpoints, how peer_id 5 is chosen, why not reuse a validator cert/id)

---

## 8. What M-012 Does NOT Cover

These are explicitly out of scope — do not implement them in M-012:

- **Balance query after Certificate**: reading LMDB via gRPC to verify balance update — this is M-013 Workload A scope
- **Multi-transfer concurrency**: multiple in-flight transfers from the same client simultaneously
- **Validator reconnection recovery** (SEC-003 `MissingCertSync`): full sync response is deferred to a later M-phase
- **SEC-004 epoch-validator binding**: dormant until CDL-017 activation
- **N > 4 testnet**: M-012 targets the existing 4-validator testnet only

---

## 9. Key File References

| File | Relevance |
|---|---|
| `ilc_consensus/src/testnet_client_main.rs` | File to extend (existing M-011 client) |
| `ilc_consensus/src/network.rs` | `PeerNetwork`, `GossipEnvelope`, `GossipMessage`, `transmit` — all needed for M-012 |
| `ilc_consensus/src/node.rs` | Reference implementation: AckFor handling (`handle_ack_for`, lines 256-300), quorum logic (line 262), certificate assembly (lines 290-298) |
| `ilc_consensus/src/types.rs` | `TransferCertificate`, `ECUTransfer`, `ObjectRef`, `ValidatorID`, `ValidatorSig`, `AGENT_TRANSFER_DST` |
| `ilc_consensus/src/config.rs` | `RawPeer`, `PeerAddr`, `NodeConfig.peers` — shows how peer_addrs is configured |
| `config/mysticeti_testnet_M009/` | Testnet config directory — validator configs to update |
| `tools/run_mysticeti_testnet_M011.sh` | Harness to extend or reference |
| `docs/research/ilc_mysticeti_testnet_M011_workload_a_v0.1.md` | M-011 artifact — design boundary (why M-011 stops at BroadcastHonest injection) |
| `docs/phases/phase_M011_workload_a_walkthrough.md` | M-011 walkthrough — mTLS constraint, design decisions |
| `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` | Full M-series lane spec — M-012 entry in phase table (§7) |

---

## 10. M-013 Preview (Real Liveness Run)

M-012 verdict is `binary_complete`. The real 4-validator end-to-end run is M-013.

M-013 will:
1. Run provisioning steps (keygen + gen-tls + gen-client-tls + update-peer-configs)
2. Distribute binaries to VPS nodes
3. Start all 4 validators
4. Run `testnet_client --msg epoch_settlement --count 10` (epochs 1-10, all validators)
5. Run `testnet_client --msg full_transfer` (complete BFT round-trip)
6. Verify balance update via gRPC query on all 4 validators
7. Silent-validator test: kill validator 1, inject epochs 11-12 to validators 2-4
8. Verdict: `run_m013_workload_a_verdict=pass`

M-013 requires M-012 to be approved first. Do not begin provisioning until the
`binary_complete` verdict is confirmed and committed.
