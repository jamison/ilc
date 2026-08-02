# ILC Production Bridge Proposal Ingress Spec 1585 v0.1

**Date:** 2026-07-27
**Phase:** 1585 / GAP-SUBSTRATE-BRIDGE-SPEC
**Status:** spec committed
**Sensitivity:** NON-SENSITIVE
**Output token:** `production_bridge_proposal_ingress_spec_committed_phase_1585`

## 0. Purpose

This specification defines the public-RC bridge boundary between the Python economics
layer and the Rust distributed DAG substrate. It is a design gate for Phase 1586
Rust implementation and Phase 1587 Python client implementation.

No runtime code is implemented here. No guard is cleared. No CDL is opened or
ratified.

## 1. Architecture Separation Statement

CDL-065 and CDL-067 fix the layer boundary:

- The Python economics layer authors already-legitimate ILC protocol state:
  ECU attribution, economic settlement preimages, lifecycle balance writes, and
  epoch state-root construction.
- The Rust `ilc_consensus/` substrate carries, orders, anchors, and commits that
  already-legitimate state through distributed BFT.
- The Rust substrate must not author economic legitimacy and Python must not bypass
  the validator BFT path.

For public RC, Python submits an epoch settlement proposal. Rust validators own
proposal admission, BFT ordering, quorum signature assembly, and checkpoint
commitment. `process_epoch_checkpoint()` remains a Rust-internal post-consensus
commit function.

The forbidden bypass shape is an externally callable `SubmitEpochCheckpoint` RPC
that accepts a Python-supplied checkpoint as if BFT had already happened. The
allowed shape is `SubmitEpochProposal`: an authenticated proposal-ingress RPC whose
payload is routed into validator-owned consensus before any checkpoint is committed.

## 2. Epoch Proposal Wire Format

Phase 1586 should add a new write service to `ilc_consensus/proto/ilc_app.proto`,
separate from the current read-only `ILCAppReadService`.

Recommended service name:

```proto
service ILCAppProposalIngressService {
  rpc SubmitEpochProposal (SubmitEpochProposalRequest)
      returns (SubmitEpochProposalResponse) {}
}
```

`SubmitEpochProposalRequest` fields:

```proto
message SubmitEpochProposalRequest {
  bytes  submitter_agent_id = 1;        // exactly 48 bytes
  uint64 epoch_number = 2;              // proposed next epoch
  bytes  state_root_cidv1 = 3;          // exactly 36 bytes
  bytes  epoch_data_hash = 4;           // exactly 32 bytes SHA-256 digest
  bytes  settlement_record_bytes = 5;   // canonical Python economic evidence bytes
  string idempotency_key = 6;           // lowercase hex SHA-256 over canonical request preimage
  uint64 not_before_unix_ms = 7;        // lower-bound timestamp for epoch validity
  string network_id = 8;                // non-empty network discriminator
  bytes  spectral_hash = 9;             // CDL-104 S(t), exactly 32 bytes
}
```

`SubmitEpochProposalResponse` fields:

```proto
message SubmitEpochProposalResponse {
  string status_token = 1;
  string error_code = 2;
  uint64 accepted_epoch_number = 3;
  bytes  accepted_state_root_cidv1 = 4;
  string proposal_id = 5;
}
```

Field validation:

| Field | Required validation |
|-------|---------------------|
| `submitter_agent_id` | Exactly 48 bytes; maps to an enrolled agent/operator identity before Phase 1586 accepts live requests. |
| `epoch_number` | Must equal the Rust store sentinel plus 1 after consensus acceptance. |
| `state_root_cidv1` | Exactly 36 bytes; Rust constructs `CIDv1Root` from these bytes. |
| `spectral_hash` | Exactly 32 bytes; CDL-104 structural commitment `S(t)`. |
| `epoch_data_hash` | Exactly 32 bytes; SHA-256 over `settlement_record_bytes`. |
| `settlement_record_bytes` | Bounded byte array containing canonical Python economic evidence; not a pre-signed checkpoint. |
| `idempotency_key` | Lowercase 64-hex SHA-256 over the canonical request preimage. |
| `not_before_unix_ms` | Must satisfy the timing contract in Section 4. |
| `network_id` | Must match the running validator network id exactly. |

Canonical request preimage:

```text
ILC_SUBMIT_EPOCH_PROPOSAL_V1 || network_id || epoch_number ||
submitter_agent_id || state_root_cidv1 || spectral_hash || epoch_data_hash ||
sha256(settlement_record_bytes) || not_before_unix_ms
```

The request preimage is a byte-domain definition, not a JSON float surface. No
economic amount is serialized as a float in this request.

## 3. BLS Signing Chain

Human Decision 1 is locked for public RC: N>=4, f=1 distributed BFT. The f=0
single-validator path is not an authorized public-RC implementation path.

Signing chain:

1. Python computes the canonical economic settlement evidence and the 36-byte
   epoch state-root CIDv1.
2. Python submits `SubmitEpochProposalRequest` to the Rust proposal-ingress service.
3. Rust validates request shape, `network_id`, payload bounds, idempotency, and timing
   preconditions that can be checked before consensus.
4. Rust routes the proposal into validator-owned BFT ordering.
5. Validators construct `EpochSettlementRecord` locally from:
   - `epoch = EpochSeq(epoch_number)`
   - `state_root = CIDv1Root(state_root_cidv1)`
   - `spectral_hash = request.spectral_hash`
   - `not_before_unix_ms = request.not_before_unix_ms`
6. Validators BLS-sign the Rust-native serialized `EpochSettlementRecord` only after
   BFT acceptance.
7. Rust assembles `EpochCheckpoint` with aggregate BLS signature plus explicit signer
   set.
8. Rust calls `process_epoch_checkpoint()` with the quorum-signed checkpoint.
9. Python verifies success by reading back the committed epoch through the read-only
   gRPC surface.

Quorum rule:

- Public RC requires at least four validators with `f=1`.
- `quorum_threshold(N)` remains the Rust quorum rule for checkpoint acceptance.
- `check_settlement_path_gate()` rejecting f=0 is part of the safety boundary, not a
  temporary workaround.

## 4. Error Contract

Phase 1586 should expose stable string error codes in `SubmitEpochProposalResponse.error_code`
and should not rely on process-local panic strings as protocol output.

Required errors:

| Condition | Error code |
|-----------|------------|
| Invalid request type, malformed bytes, or missing required field | `submit_epoch_proposal_invalid_request_phase_1586` |
| `submitter_agent_id` is not exactly 48 bytes | `submit_epoch_proposal_agent_id_invalid_phase_1586` |
| `state_root_cidv1` is not exactly 36 bytes | `submit_epoch_proposal_state_root_invalid_phase_1586` |
| `epoch_data_hash` is not exactly 32 bytes or does not match `settlement_record_bytes` | `submit_epoch_proposal_epoch_data_hash_mismatch_phase_1586` |
| Body exceeds the configured max proposal body bytes | `submit_epoch_proposal_body_too_large_phase_1586` |
| `network_id` does not match the running validator network | `submit_epoch_proposal_network_id_mismatch_phase_1586` |
| `settlement_path` is not `mysticeti_fast_path` | `submit_epoch_proposal_settlement_path_inactive_phase_1586` |
| `not_before_unix_ms` exceeds clock skew tolerance | `submit_epoch_proposal_not_before_too_far_future_phase_1586` |
| Minimum epoch duration has not elapsed | `submit_epoch_proposal_min_epoch_duration_not_elapsed_phase_1586` |
| Proposed epoch is not exactly current epoch plus 1 | `submit_epoch_proposal_invalid_epoch_sequence_phase_1586` |
| Duplicate `idempotency_key` for conflicting payload | `submit_epoch_proposal_idempotency_conflict_phase_1586` |
| BFT quorum is unavailable or rejects the proposal | `submit_epoch_proposal_bft_rejected_phase_1586` |
| BLS aggregate verification fails | `submit_epoch_proposal_bls_verify_failed_phase_1586` |

Success code:

- `submit_epoch_proposal_accepted_phase_1586`

## 5. ConsensusBridgeConfig Extension

Phase 1587 should extend `ilc_core/consensus/production_bridge.py` with write-path
configuration fields while preserving the read-only fields already present.

Required new fields:

| Field | Type | Rule |
|-------|------|------|
| `proposal_ingress_endpoint` | `str` | Non-empty gRPC target for `SubmitEpochProposal`; may equal `target` only when read and write services share an endpoint. |
| `proposal_timeout_seconds` | `int` | Positive integer; default should not be lower than the current read timeout. |
| `max_proposal_body_bytes` | `int` | Positive integer with a conservative public-RC cap. |
| `proposal_retry_count` | `int` | Non-negative integer; retries must preserve the same idempotency key. |
| `proposal_tls_root_certificates` | `bytes | None` | Same type rule as current `tls_root_certificates`; no TLS verification bypass. |

`PRODUCTION_BRIDGE_ACTIVE` must remain `False` until Phase 1587 explicitly implements
and tests the write client under the authorized SENSITIVE phase.

## 6. SettlementPath Prerequisite

The write path is active only when the Rust node config sets:

```json
{"settlement_path": "mysticeti_fast_path"}
```

Activation checks:

1. Rust startup must call `check_settlement_path_gate()` before starting the write
   ingress service.
2. Rust must reject `mysticeti_fast_path` when `network_id` is empty.
3. Rust must reject `mysticeti_fast_path` with f=0.
4. Rust must require `endpoint_projection_path` before constructing persistent peer
   sessions.
5. Python must perform a startup probe or readback check that confirms the remote
   validator advertises `mysticeti_fast_path` before submitting any proposal.

Current code state at Phase 1585:

- `ilc_consensus/src/config.rs` defaults omitted or `"none"` settlement paths to
  `SettlementPath::None`.
- `ilc_consensus/src/main.rs` rejects f=0 for `SettlementPath::MysticetiFastPath`.
- `config/mysticeti_testnet_M009/genesis.json` uses `is_testnet: true`; Phase 1588
  is scheduled to remove the production timing bypass and enforce timing unconditionally.

## 7. Human Decision 1 Record

Decision recorded by Genesis Agent on 2026-07-27:

- Public RC uses N>=4, f=1 distributed BFT.
- f=0 is rejected for public-RC implementation in this lane.
- The BLS signing chain in Phase 1586 must implement collective validator signing,
  not a Genesis-controlled single-validator checkpoint path.

## 8. Implementation Requirements For Phase 1586

Phase 1586 must:

- Add a proposal-ingress write service without weakening the existing read-only service.
- Validate request byte lengths before allocation-heavy or signature-heavy work.
- Apply a maximum proposal body size before deserializing `settlement_record_bytes`.
- Store idempotency keys or equivalent replay-prevention state in a bounded, durable
  surface.
- Route accepted proposals through BFT before calling `process_epoch_checkpoint()`.
- Keep `process_epoch_checkpoint()` internal to Rust validators.
- Preserve BLS subgroup and aggregate-signature verification.
- Add tests for malformed lengths, duplicate idempotency, conflicting idempotency,
  inactive settlement path, f=0 rejection, wrong network id, timing failure, and quorum
  acceptance.

## 9. Non-Claims

This phase does not:

- implement Rust gRPC write code
- implement the Python write client
- clear `PRODUCTION_BRIDGE_ACTIVE`
- mutate `SettlementPath` config files
- mutate validator admission state
- clear passive ECU disposition
- open or ratify a CDL
- execute settlement
- write wallet state
- regenerate or push the public mirror
- activate public RC
