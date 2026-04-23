# ILC Row-5 Layer-2 Mechanism Implementation 778 v0.1

**Phase:** 778  
**Window:** 775-782  
**Date:** 2026-04-22  

`layer2_batching_multi_relay_implemented`

## 1. Mechanism decision record

Phase 778 implements the near-term Layer-2 mechanism selected in the Window
775-782 sequence lock: batching plus real multi-relay submission indirection on
the submission path exercised by SIM-LEAKAGE-01.

The implementation surface is testnet-only:

- `ilc_consensus/src/network.rs` adds `GossipMessage::RelaySubmit`
- `ilc_consensus/src/node.rs` forwards the relay wrapper unchanged across the
  remaining validator path
- `ilc_consensus/src/testnet_client_main.rs` adds client-side batching and an
  explicit relay route

This window does **not** claim runtime `R_min` / `C_min` percentile filtering.
The truthful baseline is an explicit relay allowlist and an explicit relay path.

## 2. Batching implementation

The submission client now accepts `--batch-window-ms <N>` for `--msg broadcast`.
When relay mode is enabled, the client applies a bounded sleep before the first
relay dispatch for each submission. This is the Layer-2 timing window.

Phase 778 baseline:

- default `batch_window_ms = 500`
- batching applies only in relay-aware submission mode
- no timestamp field is added to `TransferCertificate`

This is sufficient for Phase 779 calibration against the 500ms and 1000ms
windows without mutating the certificate contract.

## 3. Multi-relay routing implementation

The submission client now accepts:

- `--relay-count <N>`
- `--relay-route <id,id,...>`
- `--validators <id@addr,id@addr,...>`

If relay mode is enabled, the client computes the explicit relay plan from the
declared final target validator plus the explicit relay list, connects to the
first relay hop, and sends `RelaySubmit { transfer, remaining_route }`.

Relay semantics:

- each relay forwards the wrapper unchanged toward the next validator
- the wrapper is bounded by a max-hop cap and rejects duplicate-hop loops
- the client relay planner rejects duplicate validator ids or duplicate
  validator addresses in the declared validator map
- the final validator consumes the unchanged `ECUTransfer` through the existing
  `BroadcastHonest` path
- `TransferCertificate` remains unchanged

The forwarding wrapper is explicitly marked `testnet_only` and is rejected in
non-`testnet_fault_sim` builds.

## 4. Relay path selection: testnet allowlist baseline and later runtime target

Phase 778 baseline relay path for the real M-009 topology is:

- client on `ilc-node-1` (local)
- first relay: validator-2 on `ilc-node-2` (VPS)
- second relay: validator-3 on `ilc-node-3` (VPS)
- final destination: validator-1 on `ilc-node-1` (local)

Recorded as validator path: `2 -> 3 -> 1`

Why this path:

- it exercises the local machine plus both VPS hosts
- it avoids validator-4, which remains the manual / silent-Byzantine slot and
  is not part of the honest relay baseline
- it gives Phase 779 a stable final observation point on validator-1's local log

Carry-forward:

- later runtime relay eligibility may use reputation and centrality surfaces
- this window does not claim those percentile gates are calibrated in runtime

## 5. ZK compatibility note

TransferCertificate carries no client-side timing or routing metadata. If a
testnet-only relay wrapper is introduced for Window
775-782, it remains outside the `TransferCertificate` field structure. A ZK
nullifier overlay can be added at the envelope layer in a later window without
modifying the existing `TransferCertificate` field structure.

## 6. Observability floor non-impact statement

Phase 778 does not reduce the Phase 679 observability floor:

- receipts remain discoverable through the existing read surfaces
- lineage remains legible through epoch and balance query surfaces
- challengeability remains anchored in the existing certificate and checkpoint
  structures
- bounded human auditability remains intact

Layer-2 changes only the submission transport path used before a validator logs
or executes a transfer. It does not remove the public receipt surfaces.
