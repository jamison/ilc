# ILC Window 637-641 Candidate Phase Grouping v0.1

Status: candidate grouping
Date: 2026-04-13
Owner lane: G8 residual exact-numeric cleanup
Classification: planning surface — not canonical law until sequence lock is committed

`window_637_641_candidate_grouping_v0_1`

## 1. Window identity and basis

Window 637-641 is the bounded residual `R2/R3` numeric cleanup window.
Its purpose is to:
- remove the remaining shared-contract and protocol-mapping float contracts that
  can leak back into resumed runtime work,
- clean up protocol/runtime-adjacent numeric surfaces that still emit or assume
  float semantics,
- align canon-export companion validators and schema helpers with the exact-
  numeric contract already ratified in `CDL-064`,
- harden the resulting residual cleanup before routing fully back into the
  broader runtime roadmap.

This window is deliberately narrower than Window 631-636. `CDL-064` is already
ratified. No new constitutional vehicle is needed. The task now is bounded
consumption of that ratified contract across the remaining shared and companion
surfaces that were explicitly deferred or only partially covered in the Tier-0
strike force.

**Authorization basis:**
- Window 631-636 removed the Tier-0 blocker and closed cleanly, but the Phase
  632 inventory explicitly left `R2` and `R3` residuals.
- The highest-risk residual item is shared type/mapping leakage through
  `ilc_core/types.py` and `ilc_core/protocol/mapper.py`.
- The project should not stop resumed runtime work for a repo-wide float purge,
  but it also should not let Window 623+ inherit float-bearing shared contracts
  and validator/export companions by accident.

`window_637_641_residual_numeric_cleanup_basis_recorded`

## 2. Scope

This window targets the bounded residual `R2/R3` numeric surfaces after
Window 631-636:

Primary `R2` targets:
- `ilc_core/types.py`
- `ilc_core/protocol/mapper.py`
- `ilc_core/protocol/event_log.py` (non-commit numeric validators only)
- `ilc_core/ledger/settlement_metrics.py`
- `ilc_core/ledger/ecu_active_layer_runtime.py` compatibility getter/egress shape

Primary `R3` targets:
- `ilc_core/ledger/canon_export_validate.py`
- `ilc_core/ledger/canon_export_bundle_validate.py`
- `ilc_core/ledger/canon_export_bundle.py`
- `ilc_core/ledger/canon_export_format.py`
- `ilc_core/ledger/canon_bundle_audit_artifact.py`

Explicitly out of scope:
- repo-wide simulation cleanup
- analytics/KPI sweep
- genesis/task-model cleanup
- new constitutional opening
- `Option B` selection or `CDL-062` work

Across any external numeric boundary touched in this window, non-finite values
must be rejected explicitly. `Decimal` migration alone is not sufficient:
`NaN`, `Infinity`, and `-Infinity` must not survive parsing into runtime,
validator, mapping, or companion-validation logic.

## 3. Phase map

### Phase 637 — Window 637-641 Sequence Lock (SENSITIVE)

**Type:** SENSITIVE — sequence lock  
**Primary output:** `docs/specs/ilc_phase_637_641_sequence_lock_v0.1.md`

**Mission:** Lock the residual numeric cleanup lane, define the `R2/R3` target
surface, confirm that this window consumes already-ratified `CDL-064` rather
than opening a new constitutional vehicle, and record the relationship to
Window 623+.

---

### Phase 638 — R2 Shared Numeric Contract Cleanup

**Type:** Runtime contract cleanup  
**Primary outputs:**
- `docs/specs/ilc_r2_shared_numeric_contract_cleanup_638_v0.1.md`
- `tests/test_phase_638_r2_shared_numeric_contract_cleanup.py`

**Mission:** Remove float-bearing shared contract leakage from
`ilc_core/types.py`, `ilc_core/protocol/mapper.py`, and directly coupled tests
or DTOs required to make those contracts coherent under `CDL-064`, including
canonical decimal-string serialization at mapped machine-legible boundaries.

---

### Phase 639 — R2 Protocol/Runtime-Adjacent Numeric Cleanup

**Type:** Runtime-adjacent cleanup  
**Primary outputs:**
- `docs/specs/ilc_r2_protocol_runtime_adjacent_numeric_cleanup_639_v0.1.md`
- `tests/test_phase_639_r2_protocol_runtime_adjacent_numeric_cleanup.py`

**Mission:** Clean up the remaining runtime-adjacent numeric surfaces that can
still reintroduce float semantics into resumed runtime work: non-commit numeric
validators and helper constructors in `event_log.py`, settlement metrics
helpers, bounded compatibility egress, and non-finite (`NaN` / `Infinity`)
numeric boundary handling.

---

### Phase 640 — R3 Numeric Companion Cleanup

**Type:** Export/validator companion cleanup  
**Primary outputs:**
- `docs/specs/ilc_r3_numeric_companion_cleanup_640_v0.1.md`
- `tests/test_phase_640_r3_numeric_companion_cleanup.py`

**Mission:** Align canon-export companion validators, bundle helpers, and audit
artifact scalar contracts with the exact-numeric rule already active in the
core Tier-0 surfaces, including explicit rejection of non-finite numeric values
where companion validators parse or admit numeric input.

---

### Phase 641 — Residual Numeric Hardening Gate + Window Closure

**Type:** Hardening / closure  
**Primary outputs:**
- `docs/specs/ilc_residual_numeric_cleanup_and_window_637_641_closure_641_v0.1.md`
- `tests/test_phase_641_residual_numeric_cleanup_and_closure.py`
- `tests/test_residual_numeric_hardening.py`
- `tools/run_window_637_641_residual_numeric_gate_phase_641.sh`
- `docs/specs/ilc_antigravity_context_capsule_v3.6.md`
- `docs/specs/ilc_window_637_641_handoff_641_v0.1.md`

**Mission:** Prove the residual `R2/R3` cleanup is stable, confirm the shared
contract leak paths are closed, confirm non-finite numeric ingress is rejected
at the boundaries touched by this window, and route the project cleanly back to
the broader runtime roadmap.

## 4. Window-level constraints

All phases share:
- No decision-log mutation
- No ADR mutation
- `CDL-064` is consumed, not reopened
- No wallet widening
- No generalized ECU transfer widening
- No ILC transferability
- No `Option B` selection claim
- No `CDL-062` opening
- No simulation-wide or analytics-wide float cleanup unless directly required
  for the bounded residual surface

## 5. Relationship to Window 623+

Window 623+ remains the named broader runtime/interface continuation.

This packet does not try to displace that. The intended posture is:
- run this residual cleanup window before or directly alongside early Window 623+
  work that would otherwise inherit shared float contracts,
- then resume broader participant-facing runtime work on the now-cleaner exact-
  numeric foundation.

## 6. AG-gate preview

| Gate | Preview | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Removes residual numeric ambiguity from shared human/agent economic/runtime surfaces. |
| AG-2 W_e increase | neutral | This is enabling cleanup rather than direct productivity expansion. |
| AG-3 Epistemic integrity | pass | No Popperian bypass or settled-state mutation introduced. |
| AG-4 ECU-ILC separation | pass | The window tightens numeric contract coherence without collapsing ECU into ILC. |
| AG-5 Harness-agnostic | pass | Shared contract cleanup improves cross-harness consistency. |
| AG-6 Near-infinite scale | pass | Shared exact-numeric contracts reduce scale-time replay drift and interface leakage. |
| AG-7 Machine-legible first | advance | Companion validators and exports become more consistent with the canonical machine contract. |
| AG-8 Outbound economic loop | neutral | This window protects the loop’s contract surface but does not widen its economics. |
