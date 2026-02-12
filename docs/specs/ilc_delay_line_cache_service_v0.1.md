# ILC Delay-Line Cache Service (Distributed) v0.1

## Summary
Define a trust-minimized, distributed delay-line cache service for streaming data. The service behaves like a FIFO buffer (time-shifted stream), suitable for predictable, sequential access patterns. ILC provides coordination, verification, and incentives so the cache can be provisioned by multiple providers without trusting any single operator.

This is **not** RAM or random-access storage. It is a streaming delay line with deterministic latency and bounded jitter.

## Goals
- Provide a **trust-minimized** (not “trustful”) cache service for sequential data streams.
- Enable multi-provider/sharded capacity with verifiable delivery and economic enforcement.
- Offer deterministic receipts, proofs, and SLA reporting compatible with ILC bundle tooling.

## Non‑Goals
- Random access memory semantics.
- Lossless storage guarantees beyond the declared retention window.
- Hiding latency: the delay is explicit and part of the contract.

## Terms
- **Delay-line cache**: FIFO stream where data reappears after a fixed delay.
- **Shard**: A provider’s segment of the total delay-line capacity.
- **Receipt**: Signed acknowledgment of a write.
- **Proof**: Evidence that a previously written chunk is returned intact.

## Roles
- **Client**: Writes data, later reads or challenges retrieval.
- **Provider**: Operates a delay-line shard; stakes ILC and serves reads.
- **Auditor**: Verifies proofs and adjudicates slashing.

## Service Contract (per provider)
Each provider publishes a contract:
- `capacity_bits`
- `bandwidth_bps`
- `delay_ms`
- `jitter_ms_max`
- `error_rate_bound`
- `fec_scheme` (if any)
- `bundle_format` (required: ILC bundle or NDJSON chunk schema)
- `receipt_sig_alg`, `receipt_pubkey`

## Data Model
### Write receipt
A receipt is signed by the provider.
Fields (minimum):
- `receipt_version`: "v0.1"
- `provider_id`
- `chunk_hash`
- `chunk_len`
- `timestamp_utc`
- `delay_ms`
- `bundle_format`
- `sig`

### Proof record
A proof shows the chunk was returned intact.
Fields (minimum):
- `proof_version`: "v0.1"
- `provider_id`
- `receipt_id` (or `chunk_hash`)
- `retrieved_at_utc`
- `chunk_hash`
- `ok`
- `detail` (optional)

## Protocol Sketch
1. **Write**: Client sends chunk `C` and computes `H = hash(C)`.
2. **Receipt**: Provider returns a signed receipt including `H` and contract params.
3. **Read/Challenge**: After `delay_ms`, client requests the chunk (or a random sample).
4. **Verify**: Client checks `hash(C') == H`.
5. **Slash/Reward**: Failure triggers slashing; success yields payment/credit.

## Verification and Incentives
- Providers stake ILC.
- Clients pay per chunk or per bandwidth‑time unit.
- Sampling challenges reduce verification cost while preserving deterrence.
- Repeated failures reduce reputation and slash stake.

## Sharding and Distribution
- A stream may be partitioned into shard lanes (provider-specific).
- Clients can split a stream across multiple providers to reduce single‑point risk.
- Contracts must disclose shard capacity and failure domain.

## Security Notes
- This is **trust‑minimized**, not trustful. Integrity is enforced by crypto + economics.
- No confidentiality guarantees unless the payload is encrypted end‑to‑end.
- Providers cannot be assumed to preserve data beyond the declared delay window.

## API Shape (conceptual)
- `delay_cache.write(chunk, metadata) -> receipt`
- `delay_cache.read(receipt_id) -> chunk`
- `delay_cache.probe() -> contract + live metrics`

## Fit with ILC
- Chunks should be ILC bundle fragments or NDJSON items.
- Receipts/proofs are canonical artifacts that can be verified with existing bundle tooling.
- SLA + proof records can feed ILC governance/audit workflows.

## Open Questions
- Standard receipt/proof schemas and signature algorithms.
- Minimal viable challenge rate to deter cheating.
- Whether to support multi‑hop chaining of delay lines.

