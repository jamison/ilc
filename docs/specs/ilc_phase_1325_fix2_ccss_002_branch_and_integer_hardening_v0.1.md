# ILC Phase 1325 Fix2 CCSS-002 Branch And Integer Hardening v0.1

**Phase:** 1325 Fix2
**Date:** 2026-05-13
**Status:** local/private audit hardening complete; no public serving

```text
phase_1325_fix2_ccss_002_branch_and_integer_hardening.v0.1
ccss_002_oversized_raw_int_rejected_before_stringification_phase_1325_fix2
ccss_002_access_branch_coverage_expanded_phase_1325_fix2
ccss_002_payload_depth_node_limits_covered_phase_1325_fix2
public_rc_remains_blocked_after_phase_1325_fix2
phase_1326_ccss_sealed_sender_boundary_next_after_fix2
```

## Scope

Phase 1325 Fix2 closes the low-cost follow-up items from the post-Fix1
CCSS-002 audit. It does not change the CCSS-002 public authority boundary or
the local-only contract shape.

## Fixes

`canonical_ccss_002_json()` now rejects raw integer payload leaves whose
absolute value exceeds the CCSS-002 canonical JSON integer bound before
converting them to decimal text. This avoids exposing direct callers to
expensive `int.__str__` work on adversarially large Python integers while
preserving the existing post-traversal `json.dumps()` byte cap.

Focused tests now cover the previously unexercised local access decision
branches for superseded capabilities, capability-ref mismatch,
membership-boundary shard mismatch, and membership-boundary ref mismatch. They
also cover grant validity-window rejection and zero grant-sequence rejection.

Payload-bound tests now exercise both tree-depth and node-count failures, in
addition to the existing traversal byte-cap and cycle tests.

## Non-Claims

This fix does not authorize public RC, source export execution, source
publication, package publication, public serving, public P2P, public
confidential coordination serving, public membership directory, public
credential authority, public ZK verifier, public capability service, release
artifact production, release-key generation, release signing material, signing,
Genesis Atlas mutation/regeneration/signing, v0.2 signing, identity artifacts,
wallet writes, ECU minting, ILC settlement, value-path activation, or Phase 1326
execution.

## Next

Phase 1326 remains the next planned CCSS-003 sealed sender boundary and requires
explicit `GO Phase 1326`.
