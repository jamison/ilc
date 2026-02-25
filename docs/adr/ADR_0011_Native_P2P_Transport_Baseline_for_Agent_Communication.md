# ADR-0011: Native P2P Transport Baseline for Agent Communication

**Status:** Proposed  
**Date:** 2026-02-25  
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
