# Blocking-Authority Vehicle Selection — Phase 1344 Deferral Resolution

**Recorded:** 2026-05-16
**Authority:** Human-authorized (Genesis Agent)
**Status:** FINAL — unblocks Phase 1362 hard gate

---

## Decision

The blocking-authority CDL vehicle for activating CDL-057 epoch-boundary witness
blocking authority is:

**CDL-089**

---

## Rationale

Phase 1344 closed the CDL-053 vehicle collision (recorded
`blocking_authority_vehicle_must_not_be_cdl_053_phase_1344`) and deferred vehicle
selection to Phase 1362 (recorded
`blocking_authority_vehicle_selection_deferred_to_phase_1362_phase_1344`).

Phase 1362's prompt contains a hard gate requiring Phase 1344 to have produced an
unambiguous vehicle selection before Phase 1362 executes. Phase 1344 produced the
deferral but not the selection, creating a circular dependency. This document
resolves that dependency by human authority.

**Why CDL-089:**

| Candidate | Status | Disposition |
|-----------|--------|-------------|
| CDL-053 | Reserved for Werner-credit architecture (Phases 508, 511, 1344) | Excluded by `blocking_authority_vehicle_must_not_be_cdl_053_phase_1344` |
| CDL-088 | Pre-reserved for public claimability authority (Phase 1374) | Excluded — do not disturb |
| CDL-089 | No entry in CDL register; no references in codebase | Selected |

CDL-089 is the next clean slot after CDL-088. It has no existing references in
`ilc_constitutional_decision_log_v0.1.md` or anywhere else in the repository.

---

## Tokens

```text
blocking_authority_vehicle_selected_cdl_089_human_authorized_2026_05_16
blocking_authority_vehicle_selection_deferred_to_phase_1362_phase_1344_resolved
```

---

## Phase 1362 Hard Gate

Phase 1362 must read this document at §0c pre-condition verification and record the
path `docs/specs/ilc_blocking_authority_vehicle_selection_phase_1344_v0.1.md` in
its walkthrough as the Phase 1344 resolution document. The vehicle number CDL-089
satisfies the unambiguous vehicle selection requirement.

This document does NOT open CDL-089. Opening CDL-089 is Phase 1362's act and
requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1362`.
