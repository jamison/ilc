# ILC Epoch-Boundary Witness Prelock Hardening 510 v0.1

Status: prelock hardening
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Scope lock

epoch_boundary_witness_scope_locked

The Phase 509 opening boundary is preserved:
- provenance-only witness metadata remains the in-scope surface,
- blocking-authority remains deferred,
- the witness lane does not authorize or block ECU to ILC conversion batches in Phase 510.

## 2. Rejected alternatives

Rejected alternatives at prelock:
- validator witness veto over conversion batches,
- settlement-block authority for witness absence,
- reinterpretation of epoch-finality attestations as conversion authorization.

## 3. Compatibility guards

cdl_030_p_e_clamp_unchanged
cdl_v3_diversity_floor_unchanged

CDL-030 P_e clamp [0.75, 1.30] semantics are unchanged.
CDL-051 epoch transition surface is unchanged.
CDL-V3 diversity protections remain intact.

## 4. Opening-state preservation

CDL-057 remains status: open in Phase 510.
No decision-log mutation occurs in Phase 510.
Phase 511 is the next authorized phase.

## 5. Prelock summary

The epoch-boundary witness lane is hardened as a narrow provenance lane. Any future witness role
that blocks or authorizes settlement would require later constitutional work beyond this prelock.
