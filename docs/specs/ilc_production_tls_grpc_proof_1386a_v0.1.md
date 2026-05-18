# ILC Production TLS gRPC Proof 1386a v0.1

**Phase:** 1386a
**Date:** 2026-05-18
**Status:** complete
**Scope:** Testnet infrastructure proof only; no production activation

## Tokens

```text
production_tls_grpc_path_proven_phase_1386a
epoch_0_sentinel_reconciliation_verified_phase_1386a
get_epoch_chain_channel_limit_added_phase_1386a
```

## Summary

Phase 1386a proves the production TLS gRPC read path from `ilc_core/` to
`ilc_consensus/`. This is distinct from Phase 1360, which proved a plaintext
private-Tailscale gRPC path using an insecure channel.

The proof uses `build_secure_grpc_read_stub()` with
`tls_root_certificates` against a TLS-configured Rust `validator_harness`
gRPC endpoint. The same proof verifies epoch-0 sentinel behavior for
`GetEpochChain(from_epoch=0, to_epoch=0)` and closes hardening carry-forward
item 7 by adding a channel receive-size cap plus bounded response iteration
before epoch-chain records are normalized.

## Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| `build_secure_grpc_read_stub` exists | `ilc_core/consensus/production_bridge.py` | confirmed |
| Python production bridge uses TLS credentials and `grpc.secure_channel` | `build_secure_grpc_read_stub()` | confirmed; no `grpc.insecure_channel` call exists in `production_bridge.py` |
| TLS root certificates are passed into the gRPC credential constructor | `grpc.ssl_channel_credentials(root_certificates=config.tls_root_certificates)` | confirmed |
| gRPC channel receive-size cap is configured | `grpc.secure_channel(..., options=(("grpc.max_receive_message_length", config.max_epoch_chain_receive_bytes),))` | confirmed |
| Epoch-chain response records are bounded before materialization | `ILCConsensusGrpcReadAdapter.get_epoch_chain()` | confirmed; no `records = list(...)` remains |
| Rust validator gRPC server is TLS-configured | `ilc_consensus/src/main.rs` | confirmed; `ServerTlsConfig` and `Identity::from_pem(...)` are used |
| Rust node config carries PEM certificate and key material for tonic TLS identity | `ilc_consensus/src/config.rs` | confirmed |
| Rust epoch-0 sentinel no longer underflows at genesis | `ilc_consensus/src/app_interface.rs` | confirmed; `expected_count` is guarded when `from > to` |
| Phase 1360 did not prove the production TLS path | `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md`; `docs/phases/STATUS.md` | confirmed |
| No live ECU transfer is activated | `production_bridge.py`; Phase 1386a proof run config `settlement_path=none` | confirmed |

## Live TLS Proof Evidence

The live proof ran a locally built Rust `validator_harness` with validator 1's
existing M009 testnet TLS certificate and a TLS-enabled gRPC listener.

| Evidence | Value |
|----------|-------|
| Harness binary | `ilc_consensus/target/debug/validator_harness` |
| Config path | `out/phase_1386a/validator_1_tls_grpc_config.json` |
| Log path | `out/phase_1386a/validator_1_tls_grpc.log` |
| Proof JSON | `out/phase_1386a/phase_1386a_tls_grpc_live_proof.json` |
| TLS root used by Python | `config/mysticeti_testnet_M009/certs/validator_1_cert.pem` |
| gRPC target | `100.111.172.103:61090` |
| TLS stub constructor used | `build_secure_grpc_read_stub` |
| `tls_root_certificates` used | true |
| `GetEpoch` result | `current_epoch=0` |
| Python adapter `GetEpochChain(0,0)` | `chain_complete=true`, `records=0` |
| Direct Rust `GetEpochChain(0,0)` via generated stub | `chain_complete=true`, `records=0` |
| Settlement path | `none` |

The earlier pre-fix probe reached the TLS Rust server and then reset the stream
on `GetEpochChain(0,0)` because `app_interface.rs` attempted `to - from + 1`
when genesis mapped `from=1` and `to=0`. Phase 1386a fixes that by returning
an empty complete chain when the sentinel range is valid but the current epoch
is still 0.

## Epoch-0 Sentinel Reconciliation

Rust semantics:

```text
from_epoch=0 -> start from epoch 1
to_epoch=0 -> use current epoch
```

At genesis, `current_epoch=0`, so the derived Rust range is `from=1`, `to=0`.
That range is intentionally empty and complete. The Rust service now computes
`expected_count=0` when `from > to`, preventing underflow and returning a valid
empty chain response.

Python semantics:

```text
get_epoch_chain(0, 0) forwards the sentinel range to Rust
```

Python still rejects invalid non-sentinel decreasing ranges, but it no longer
rejects the Rust sentinel pair `(0,0)`.

## Implementation Changes

| File | Change |
|------|--------|
| `ilc_core/consensus/production_bridge.py` | Added `MAX_EPOCH_CHAIN_RECEIVE_BYTES`, config validation, `grpc.max_receive_message_length`, epoch-0 sentinel forwarding, and bounded response iteration |
| `ilc_consensus/src/config.rs` | Loaded validator TLS PEM cert/key alongside existing DER material so tonic can build a TLS server identity |
| `ilc_consensus/src/main.rs` | Configured optional gRPC server with `ServerTlsConfig` and PEM identity |
| `ilc_consensus/src/app_interface.rs` | Fixed epoch-0 sentinel genesis range and added a direct Rust regression test |
| `tests/test_production_tls_grpc_proof_1386a.py` | Added Phase 1386a TLS, sentinel, and proof-record tests |
| `tests/test_phase_1358_production_bridge.py` | Updated Phase 1358 bridge regression tests for receive-size channel options and bounded iteration |

## Non-Authorizations

Phase 1386a records no production activation, no live ECU transfers, no CDL mutation,
no public gRPC endpoint activation, no production validator deployment, no value-path
activation, no public RC claim, no sender-privacy claim, no package publication, and
no public source release.

## Graph Delta

```text
graph_delta=load_bearing_artifact_changed:ilc_core/consensus/production_bridge.py -> ilc-core-ilc-consensus-production-bridge
graph_delta=load_bearing_artifact_changed:ilc_consensus/src/main.rs -> consensus-validator-tls-grpc-read-service
graph_delta=load_bearing_artifact_changed:ilc_consensus/src/config.rs -> consensus-validator-tls-grpc-read-service
graph_delta=load_bearing_artifact_changed:ilc_consensus/src/app_interface.rs -> consensus-validator-tls-grpc-read-service
graph_delta=load_bearing_artifact_added:docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md -> phase-1386a-production-tls-grpc-proof
```
