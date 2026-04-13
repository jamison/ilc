# ILC Residual Numeric Cleanup and Window 637-641 Closure 641 v0.1

Status: implemented
Date: 2026-04-13
Window: 637-641
Phase: 641
Owner lane: G8 residual exact-numeric cleanup hardening gate

## 1. Gate identity and authority

Phase 641 is the hardening gate and closure artifact for Window 637-641.

The gate authority is:
- Phase 637 sequence lock
- Phase 638 shared-contract cleanup
- Phase 639 runtime-adjacent cleanup
- Phase 640 companion cleanup
- ratified `CDL-064`

No decision-log mutation occurs in Phase 641. No ADR mutation occurs in
Phase 641.

`residual_numeric_hardening_gate_641_locked`
`runtime_residual_numeric_hardening_gate_phase_641_executed`

## 2. Residual surface under test

The bounded residual surface under test is exactly the 638-640 target set:
- `ilc_core/types.py`
- `ilc_core/protocol/mapper.py`
- `ilc_core/protocol/event_log.py`
- `ilc_core/ledger/settlement_metrics.py`
- `ilc_core/ledger/ecu_active_layer_runtime.py`
- `ilc_core/ledger/canon_export_validate.py`
- `ilc_core/ledger/canon_export_bundle_validate.py`
- `ilc_core/ledger/canon_export_bundle.py`
- `ilc_core/ledger/canon_export_format.py`
- `ilc_core/ledger/canon_bundle_audit_artifact.py`

The bounded question answered by this gate is:
- do these `R2/R3` surfaces still leak float-backed machine contracts
- do the touched external numeric boundaries still accept non-finite values
- can the project route back to the broader runtime roadmap without reopening
  this residual numeric defect class first

## 3. Hardening suite executed

The residual hardening suite executed:
- shared-contract exact numeric stability on `Node` / `ClaimRecord`
- protocol-mapping exact numeric stability, including zero-default cleanup in
  `mapper.py`
- runtime-adjacent validator and metrics stability
- active-layer compatibility getter and non-finite ingress stability
- canon-export companion normalization, non-finite rejection, and bundle
  validation coherence
- phase-gate checks for Phases 638, 639, and 640

This gate explicitly covers:
- absence of residual float-based contract leakage in the bounded `R2/R3`
  surface
- explicit rejection of `NaN`, `Infinity`, and `-Infinity` at the residual
  external numeric boundaries touched in Phases 638-640

## 4. Findings and fix-loop disposition

Outside audit result:
- one real residual defect remained at gate-open: `ilc_core/protocol/mapper.py`
  still used float defaults (`0.0`) for exact numeric fields in
  `epoch_summary_to_protocol(...)`

Fix-loop disposition:
- fixed in Phase 641 before closure by replacing those defaults with canonical
  zero string defaults (`"0"`)
- no second material residual defect stood up inside the bounded 638-640 target
  surface after the fix
- finite legacy float ingress remains accepted only where earlier phases
  explicitly preserved bounded compatibility, but those values are normalized
  immediately and no longer define the machine contract

`residual_r2_r3_numeric_cleanup_pass`
`shared_contract_float_leakage_closed`
`canon_export_companion_numeric_contract_coherent`

## 5. Closure verdict and carry-forward

Window 637-641 changed:
- shared graph contract `net_stake` no longer defines a float machine contract
- protocol-mapping economic outputs no longer project through float defaults
- runtime-adjacent event-log, settlement-metrics, and active-layer compatibility
  surfaces now emit canonical decimal strings and reject non-finite values
- canon-export companion files no longer declare float as the scalar contract
  and reject non-finite bundle/export numerics at the touched boundaries

Still deferred outside the bounded residual cleanup:
- broader simulation/devnet float cleanup
- broader protocol-adjacent cleanup outside the named 638-640 target set
- Window 623+ MVP runtime/interface closure
- broader public RC activation after both MVP forms close
- coupling-invariants governance lock
- privacy-preserving legitimacy, censorship-resistance, independence, and
  transport/discovery graduation items for later Option-B work

Closure verdict:
- PASS
- Window 637-641 closes as a bounded residual numeric cleanup lane
- Window 623+ may resume without residual numeric contract leakage from the
  named `R2/R3` surface

`window_637_641_closure_verdict_pass`
`window_623_plus_may_resume_without_residual_numeric_contract_leakage`

## 6. Capsule and handoff updates

Phase 641 advances the capsule from v3.5 to v3.6 and publishes a closure
handoff for Window 637-641.

The updated capsule and handoff record:
- Window 637-641 closed
- residual numeric cleanup PASS
- routing back into the broader runtime roadmap
- no change to the constitutional posture: `Option D` remains active, no wallet
  widening, no ILC transferability, and no `CDL-062` authorization
