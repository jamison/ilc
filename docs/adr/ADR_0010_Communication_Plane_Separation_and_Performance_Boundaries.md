# ADR-0010: Communication Plane Separation and Performance Boundaries

**Status:** Proposed  
**Date:** 2026-02-25  
**Context:** Post-Phase 299 architecture hardening for agent-native throughput

## Context

ILC traffic has distinct workloads with incompatible latency/correctness needs:
- high-frequency traversal and query operations,
- feed/dissemination propagation,
- coordination/conflict resolution,
- epoch settlement and clawback safety windows.

Treating these as one plane causes either latency collapse (if all traffic is settlement-bound) or safety collapse (if all traffic is best-effort).

## Decision

ILC will use a four-plane communication model:
1. **Hot Path Plane** (query/traversal/refactor assist): low-latency request/reply.
2. **Dissemination Plane** (subscriptions/feeds): gossip-oriented fanout.
3. **Coordination Plane** (proposal/conflict/supersession): signed operations with deterministic conflict handling.
4. **Settlement Plane** (ECU->ILC conversion, clawback/slash): epoch-batched finality.

Required rule: no settlement-plane dependency on hot-path request completion.

## Consequences

Positive:
- latency and safety targets can be tuned per plane,
- avoids forcing consensus/finality into sub-10ms routes,
- makes D2e command contracts clearer by explicitly mapping operations to planes.

Costs:
- more protocol surface to specify and test,
- increased monitoring complexity.

## Non-goals

- This ADR does not select exact transport libraries.
- This ADR does not ratify settlement window length.
