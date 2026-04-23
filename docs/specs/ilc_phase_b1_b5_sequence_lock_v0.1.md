# ILC Phase B1-B5 Sequence Lock v0.1

**Window:** B-Scope
**Phases:** B-1 through B-5
**Date:** 2026-04-23
**Status:** locked for execution through the B-4 hold point

`row5_b_scope_sequence_lock_published`
`row5_b_scope_hold_point_at_b4`

## Purpose

This sequence lock opens the Row 5 mechanism scoping window. The window is a
simulation-backed scoping pass only. It selects no live runtime mechanism and
closes no runtime legitimacy gate.

## Locked Pre-Decisions

1. This window scopes and selects the Row 5 mechanism family. It does not
   implement any privacy layer in Rust or Python runtime paths.
2. The autoresearch methodology specified in the B-Scope prompt is mandatory
   for Phase B-3. A single-shot SIM does not satisfy B-3.
3. The Phase 740 closure bar (`0.45 / 0.60`) is not reaffirmed. Phase B-3 may
   produce only simulation-derived bar recommendations. Those recommendations
   are not runtime bars. The human may set an intended target at B-4, and only
   B-Impl plus SIM-LEAKAGE-03 can confirm whether the live system actually
   meets it.
4. The aspirational target is the mixing layer. All three mechanism families
   will be simulated. Selection at B-4 remains evidence-driven.
5. Layer-1 log hygiene is treated as a completed prerequisite. The simulation
   models the post-Layer-1 baseline, not the pre-redaction baseline.
6. No Rust source modifications occur in this window. `node.rs`,
   `epoch_settlement.rs`, and `network.rs` remain untouched.
7. No CDL mutation occurs in this window.
8. No new Option B implication is made beyond what Phase 814 already recorded.
9. The autoresearch harness is a standalone statistical simulation. It does not
   require `validator_harness`, the gRPC stack, or live multi-machine traffic.
10. Phase B-4 is a HOLD POINT. B-5 does not proceed until the human confirms
    the mechanism family, parameter range, and simulation-derived bar
    recommendation in conversation.

## Deliverable Boundary

Execution under this lock is authorized through:

- B-1 sequence lock acknowledgment,
- B-2 mechanism family analysis + harness delivery,
- B-3 autoresearch execution + evidence artifact,
- B-4 recommendation document + human hold point.

This lock does not authorize:

- B-5 closure without human confirmation,
- any implementation window,
- any claim that Row 5 is closed.
