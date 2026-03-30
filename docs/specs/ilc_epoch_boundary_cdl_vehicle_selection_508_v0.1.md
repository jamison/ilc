# ILC Epoch-Boundary CDL Vehicle Selection 508 v0.1

Status: vehicle selection
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Candidate vehicle set

Phase 498 carried forward three candidate constitutional vehicles for the epoch-boundary witness
lane:
- `cdl_030_extension`
- `cdl_051_extension`
- `new_cdl_057`

The numbered lane opened in Phase 509 remains CDL-057 regardless of which constitutional rationale
is selected here.

## 2. Selected vehicle

epoch_boundary_vehicle_selected = new_cdl_057

Phase 509 opens CDL-057 as the numbered lane, with `new_cdl_057` as the governing constitutional
rationale. The selected vehicle is a narrow witness lane because the scoped surface is bounded to
epoch-boundary conversion-batch witness semantics and should not reopen the full meaning of either
CDL-030 or CDL-051.

## 3. Rejected alternatives

Rejected alternative: `cdl_030_extension`
- Rejected because CDL-030 governs the P_e clamp surface, not the validator-witness attachment
  surface.
- Rejected because reopening CDL-030 would make the witness lane appear to amend ECU pricing
  semantics that remain unchanged.

Rejected alternative: `cdl_051_extension`
- Rejected because CDL-051 governs quorum-state, epoch-finality, and deterministic fork resolution,
  while the scoped witness lane is narrower than the full consensus state machine.
- Rejected because the witness lane may reference epoch boundaries without reinterpreting
  epoch-finality attestations as conversion authorization.

## 4. Scope disposition

The implementable no-CDL surface from Phase 498 remains provenance tagging and audit-only witness
metadata. A blocking or authorizing witness role remains a constitutional question, but that role is
not implemented in this window.

blocking_authority_scope = deferred

## 5. Constitutional protections

cdl_053_unaffected
cdl_030_p_e_clamp_unchanged

The CDL-030 P_e clamp [0.75, 1.30] semantics are unchanged by the vehicle choice.
CDL-053 Werner credit lane is unaffected.
No decision-log mutation occurs in Phase 508.
Phase 509 is the next authorized phase.
