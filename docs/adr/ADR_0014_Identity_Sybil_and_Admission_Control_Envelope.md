# ADR-0014: Identity, Sybil, and Admission Control Envelope

**Status:** Accepted
**Acceptance token:** `adr_0014_accepted_phase_1545p_fix17`
**Acceptance evidence:** `docs/phases/phase_1545p_fix17b_adr_acceptance_batch_walkthrough.md`
**Date:** 2026-02-25
**Context:** Preventing mesh abuse and preserving graph quality under open participation

## Context

Low-latency P2P systems are vulnerable to identity flooding, feed spam, and coordination sabotage without explicit admission and abuse controls.

## Decision

Define mandatory identity/sybil envelope across communication planes:
1. signed identity assertions for write-path participation,
2. per-identity rate limits and epoch-scoped quotas,
3. peer scoring and quarantine/deprioritization pathways,
4. deterministic rejection reasons and telemetry emission,
5. replay/conflict protections in coordination plane.

The envelope applies to both human-operated and digital-agent participants.

## Consequences

Positive:
- reduces sybil amplification and spam attack surface,
- supports predictable operator response and forensic review,
- preserves availability for productive agents.

Costs:
- additional complexity in node operations and policy tuning,
- risk of false positives if thresholds are poorly calibrated.

## Non-goals

- This ADR does not fix exact threshold values.
- This ADR does not choose a single identity provider model.
