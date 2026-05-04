# ADR-0012: ECU-ILC-Graph Coupling and Anti-Reflexivity Contract

**Status:** Accepted
**Date:** 2026-02-25  
**Context:** Economic integrity and utility-first objective for agent ecosystems
**Accepted:** Phase 1158, 2026-05-04
**Acceptance token:** `adr_0012_accepted_phase_1158`

**Scope of acceptance:** Accepted for the directional ECU/ILC/graph coupling and
anti-reflexivity contract. Acceptance does not lock settlement-window length,
new issuance constants, public minting semantics, or final settlement substrate
selection.

## Context

The protocol has a functional triad:
- epistemic graph (assertion/provenance substrate),
- ECU (work-value accounting),
- ILC (scarce settlement/governance layer).

Without explicit coupling constraints, reflexive loops can dominate utility and destabilize incentives.

## Decision

Define a directional coupling contract:
1. Graph activity produces ECU under verifiable rules.
2. ECU conversion to ILC occurs via settlement-plane policy, not hot-path messaging.
3. ILC governance modifies policy parameters through explicit ratification lanes only.
4. No component may directly self-amplify issuance outside ratified policy boundaries.

Explicit framing: ILC is provenance+adjudication infrastructure, not a guarantee of objective truth.

## Consequences

Positive:
- preserves utility-first economics,
- reduces risk of speculative reflexivity dominating protocol behavior,
- improves explainability for agent-facing economic APIs.

Costs:
- requires stronger telemetry and monitoring to detect coupling drift,
- requires clear KPI ownership across protocol/economic/governance planes.

## Non-goals

- This ADR does not lock ECU settlement window length.
- This ADR does not set new issuance constants.
