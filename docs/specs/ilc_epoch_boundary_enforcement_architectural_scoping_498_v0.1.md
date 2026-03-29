# ILC Epoch-Boundary Enforcement Architectural Scoping 498 v0.1

Status: architectural scoping
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Surface description

The scoped surface is a validator-attestation witness role for ECU to ILC conversion batches at the
epoch boundary. The question is whether validator signatures may be used only as provenance tags,
or whether they become constitutional gating conditions for conversion batches.

## 2. Constitutional amendment analysis

No CDL is opened in Phase 498.
No decision-log mutation occurs in Phase 498.
A witness role that merely records validator provenance on conversion-batch metadata can be added
without reopening CDL-030 or CDL-051. A witness role that blocks, authorizes, or finalizes ECU to
ILC conversion batches would change the constitutional meaning of both the P_e conversion surface
and epoch-finality handling and therefore requires a future CDL amendment in Window 505+.

## 3. Implementable without CDL amendment

Implementable without a CDL amendment:
- provenance tagging for conversion-batch witness identities,
- audit-only validator attestations that do not block settlement,
- telemetry and reporting on whether validator witnesses were present.

Not implementable without a CDL amendment:
- validator witness quorum as a hard precondition for ECU to ILC conversion,
- validator witness veto or settlement-block authority,
- reinterpretation of epoch-finality attestations as conversion authorization.

## 4. Carry-forward disposition

Epoch-boundary CDL amendment carry-forward is deferred to Window 505+.
If opened later, the amendment lane must decide whether the correct home is a CDL-030 extension, a
CDL-051 extension, or a new narrow epoch-boundary witness lane. This scoping phase does not choose
between those amendment vehicles.
