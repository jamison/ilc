# ADR-0013: External Payment Boundary and Third-Party Independence

**Status:** Proposed  
**Date:** 2026-02-25  
**Context:** Clarifying optional perimeter payment integrations vs core protocol design

## Context

External HTTP payment standards (for example x402-style flows) can support inbound commerce, but introducing them as internal dependencies conflicts with independence and latency requirements.

## Decision

Set boundary rule:
- External payment protocols are **perimeter adapters** only.
- Core ILC communication, graph operations, and ECU accounting must remain operational without external facilitators.
- If external payment ingress is enabled, failures in those adapters must degrade to boundary denial only, not core protocol instability.

## Consequences

Positive:
- protects core protocol from third-party outage/censorship risk,
- allows optional business integration without architectural lock-in.

Costs:
- duplicate pathway complexity (native settlement + boundary adapters),
- requires explicit operator guidance for fallback behavior.

## Non-goals

- This ADR does not reject all third-party integrations.
- This ADR does not define adapter API details.
