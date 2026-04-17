# ADR-0011: Native P2P Transport Baseline for Agent Communication

**Status:** Accepted
**Date:** 2026-02-25
**Accepted:** 2026-03-31 (post-Phase 547 architectural review; consistent with CDL-024 allowed transport kinds and ADR-0025)
**Context:** Independence and low-latency requirements for digital-agent workloads

## Context

The project requires no mandatory third-party relay, high distribution, and low-latency machine-native communication. HTTP request/response payment flows and centralized brokers are not suitable as core transport for hot-path graph operations.

## Decision

Adopt native P2P transport baseline:
- **Primary network transport:** QUIC-based encrypted streams.
- **Local fast-path:** shared-memory/UDS when co-located.
- **Dissemination:** gossip/pub-sub over the P2P mesh.
- **No mandatory central broker** as a protocol dependency.

Gateway adapters (HTTP/x402-like, exchange integrations) are explicitly external and optional.

## Consequences

Positive:
- aligns with no-third-party-hard-dependency requirement,
- improves reconnect and multiplexing behavior for agent traffic,
- preserves compatibility with external bridges without making them protocol critical.

Costs:
- peer discovery and abuse resistance become core protocol concerns,
- NAT and connectivity operations require explicit design.

## Non-goals

- This ADR does not commit to a specific implementation framework (e.g., libp2p vs custom stack).

---

## Amendment — 2026-04-16: Network Discriminator in Cryptographic DST (SEC-002)

**Amendment status:** Accepted (records a mandatory pre-mainnet gate arising
from M-series implementation audit)

**Background:** During the M-001 to M-007 security hardening pass (commit
`486b6896`), it was identified that the BLS domain separation tag used for
all ILC fast-path validator signatures — `b"ILC_FAST_PATH_V1"`, now
centralized in `ilc_consensus/src/validator.rs` as `VALIDATOR_DST` — contains
no network discriminator. Because the DST is identical across any ILC
deployment, a `TransferCertificate` produced on one network (e.g., testnet)
is cryptographically valid on any other ILC network using the same validator
key set (e.g., mainnet). This is a cross-network replay attack vector.

**Required gate (pre-M-009, pre-mainnet):** Before the first multi-machine
testnet (M-009) is established, `VALIDATOR_DST` must be refactored from a
static constant to a network-parameterized value. The recommended form is:

```rust
pub fn validator_dst(network_id: &str) -> Vec<u8> {
    format!("ILC_FAST_PATH_V1:{}", network_id).into_bytes()
}
```

The `network_id` string must be:
- set at node startup from configuration (not at compile time),
- distinct and non-empty for every independent network deployment,
- included in the node startup log at INFO level for operator verification.

Example values: `testnet_m009`, `testnet_m010`, `mainnet_genesis`.

**Consequence for ADR-0011 transport baseline:** All QUIC transport
implementations (M-008 and later) must receive `network_id` from the node
configuration layer and pass it through to all signing and verification
operations. The transport layer must not hardcode or assume a network identity.

**Tracking token:** `sec_002_chain_id_dst_required_before_m009_testnet`
**Full context:** §6, SEC-002 in
`docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

**Gate closure (2026-04-16):** Satisfied in M-008. `VALIDATOR_DST` static constant
removed from `validator.rs`; replaced with `pub fn validator_dst(network_id: &str) ->
Vec<u8>` producing `b"ILC_FAST_PATH_V1:{network_id}"`. Both `sign_message` and
`verify_signature` now accept `network_id: &str`. Enforcement implemented in
`FastPathProtocol` and carried through all signing/verification call sites. Network ID
is loaded from node configuration and logged at startup. Implementation commit:
`acfcfd2d`. Token `sec_002_chain_id_dst_required_before_m009_testnet` — SATISFIED.
