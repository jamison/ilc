# ILC CDL-050 L1/L2 Prerequisite Disposition 452 v0.1

Status: Phase-452 L1/L2 prerequisite disposition artifact
Date: 2026-03-21
Owner lane: G8 Constitution Cluster A

## 1. Disposition decision

L1/L2 separation is adopted as a CDL-050 prerequisite.

L1/L2 disposition is frozen as of Phase 452.

No hidden or assumed prerequisite is allowed.

## 2. Rationale

The current Treasury blocker-resolution stack already treats the L1/L2 question as the decisive architectural fork for Gate 2. Adopting the separation explicitly is the narrower and more defensible constitutional move.

ADR-0018 is the relevant architectural anchor for this choice. The current planning corpus still describes ADR-0018 as post-launch optional, but Window 450-459 requires a narrower Treasury surface than that older priority allows.

For CDL-050, the Sequestered Financial Shard must be elevated from post-launch optional to Genesis affordance so Treasury risk is bounded to ECU-side levers rather than enlarged to absorb derivative contagion.

## 3. Interface boundary conditions

The adopted L1/L2 boundary for CDL-050 is:
- L1 Treasury operates on ECU-side observables and lever ceilings only,
- L1 Treasury does not read, price, or respond to L2 derivative-market state,
- L2 financial activity remains outside the L1 Treasury control loop,
- L2 uses a distinct budget and contagion boundary consistent with ADR-0018,
- failure or liquidation pressure inside L2 must not be treated as direct justification for L1 Treasury intervention.

This interface boundary is adopted as a Genesis affordance for CDL-050 blocker resolution, not as a post-hoc implementation convenience.

## 4. Risk model implications

Because L1/L2 separation is adopted, the Treasury risk model for CDL-050 is bounded to ECU-side intervention ceilings, intervention duration, intervention cost, production continuity, and release-shock behavior.

This means later phases may evaluate Treasury candidate choices without enlarging the risk model to include derivative contagion as an endogenous L1 signal.

If this prerequisite had been rejected, the Treasury risk model would have to be enlarged accordingly to account for cross-layer contagion, derivative collapse propagation, and interface ambiguity. Phase 452 rejects that enlarged model path for Window 450-459.

## 5. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 452.

Phase 452 freezes the L1/L2 prerequisite disposition and interface boundary only. It does not authorize Treasury implementation, simulation execution, or CDL-050 parameter lock-in.
