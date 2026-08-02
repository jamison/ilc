# ILC CDL-104 Spectral Hash Epoch Commitment Ratification

**Phase:** 1582 / GAP-SPECTRAL-01b
**Date:** 2026-08-02
**GO phrase:** `GO Phase 1582 GAP-SPECTRAL-01b CDL-104-RATIFY`
**Opening document:** `docs/specs/ilc_cdl_104_spectral_hash_epoch_commitment_opening_gap_spectral_01a_v0.1.md`
**Ratification token:** `cdl_104_ratified_phase_1582`
**Runtime token:** `spectral_hash_rust_field_committed_phase_1582`

## 1. Ratified Decision

CDL-104 is ratified for public-RC epoch commitments. Validators now commit to:

```text
C(t) = (M(t), S(t))
```

where:

- `M(t)` is the 36-byte epoch `state_root` CIDv1 already committed in `EpochSettlementRecord`.
- `S(t)` is the 32-byte `spectral_hash` field added to the Rust `EpochSettlementRecord`.

The Rust field is:

```rust
pub spectral_hash: [u8; 32]
```

The field is serialized as part of `EpochSettlementRecord`; validators BLS-sign that serialized record; `process_epoch_checkpoint()` verifies the aggregate BLS signature over that same serialized record before committing the epoch.

## 2. Ratified Digest Recipe

CDL-104 v1 uses the Phase 1580 candidate recipe without amendment:

| Parameter | Ratified value |
|---|---|
| Graph object | Normalized hypergraph Laplacian `Delta(t)` |
| Eigenvalue selection | Sorted ascending eigenvalues, top `k = 20` |
| Quantization | `mu_i = round_ties_to_even(lambda_i * 1_000_000)` |
| Encoding | Signed int64 little-endian per quantized eigenvalue |
| Digest | SHA-256 over concatenated encoded values |
| Python source anchor | `spectral_hash_fixed_point_int64_le(eigenvalues, q=1_000_000, k=20)` |
| Rust field | `spectral_hash: [u8; 32]` |

Legacy raw IEEE-754 `spectral_hash()` and the older SHA-384 planning candidate are rejected for CDL-104 v1 epoch commitments.

## 3. Implementation Binding

Phase 1582 implements the CDL-104 field across the public-RC substrate boundary:

1. `ilc_consensus/src/types.rs` adds `spectral_hash: [u8; 32]` to `EpochSettlementRecord`.
2. `ilc_consensus/src/network.rs` adds `spectral_hash: [u8; 32]` to `EpochProposal`.
3. `ilc_consensus/src/node.rs` maps proposal `spectral_hash` into the signed record and includes it in `proposal_commitment_sha256()`.
4. `ilc_consensus/proto/ilc_app.proto` adds `SubmitEpochProposalRequest.spectral_hash = 9`.
5. `ilc_consensus/src/app_interface.rs` rejects malformed spectral hashes and exposes committed spectral hashes in `GetEpochRecordResponse`.
6. `ilc_core/consensus/production_bridge.py` accepts, validates, serializes, and submits the 32-byte spectral hash; the Python idempotency preimage matches the Rust commitment order.

## 4. Scope Boundary

This ratification authorizes commitment and signature binding of supplied `S(t)` values. It does not yet authorize an independent Rust-side recomputation of `S(t)` from graph state, nor does it claim that validators can reject a mathematically incorrect but correctly shaped spectral digest by recomputation.

That recomputation/enforcement boundary is deliberately separate from the field-ratification boundary. Phase 1582 closes the public-RC factual claim that validators sign `C(t) = (M(t), S(t))`; it does not create a spectral-proof verifier, public spectral privacy guarantee, CCSS routing primitive, or Laplacian recomputation engine.

## 5. Non-Claims

Phase 1582 does not:

- activate public RC or mainnet;
- mint ECU or ILC;
- authorize wallet transfer, spend, withdrawal, or external-address claimability;
- alter settlement reward math;
- modify `AttributionBatch` reputation or backward-attribution roots;
- use CCSS-SPECTRAL route tokens as epoch commitments;
- add spectral digest recomputation enforcement;
- publish a public mirror.

## 6. Output Tokens

- `cdl_104_ratified_phase_1582`
- `spectral_hash_rust_field_committed_phase_1582`
