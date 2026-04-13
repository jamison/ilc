# ILC Phase 642-648 Sequence Lock v0.1

Status: sequence lock
Date: 2026-04-14
Classification: bounded implementation/security strike-force lock
Phase: 642
Owner lane: G8 security boundary and remaining-float strike force

## 1. Window identity and authorization basis

Human direction 2026-04-14: remaining float carry-forward and live bounded
security issues are treated as a single bounded strike-force lane rather than
as diffuse future debt.

Window 637-641 closed bounded residual numeric leakage and produced a clean
runtime foundation. That closure does not remove the need for remaining-float
carry-forward visibility or for bounded implementation/security hardening on
still-live touched surfaces.

Window 642-648 is therefore locked as a non-constitutional strike-force lane:
`window_642_648_sequence_lock_primary_gate`
`window_642_648_is_non_constitutional_security_strike_force`

No new CDL or ADR opening is authorized here. This lane exists to close live
implementation/security issues and to keep remaining float cleanup visible
after the exact-numeric windows, not to reopen governance posture.

## 2. Primary live target surface

Primary live target files for this window:
- `ilc_core/ledger/canon_bundle_replay_report.py`
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/network/peer.py`
- `ilc_core/epistemic/aesthetic_panel_runtime.py`
- `ilc_core/economics/passive_ecu_attribution_runtime.py`
- `ilc_core/protocol/ndjson_bundle.py`
- `ilc_core/cli/ep_task_cli.py`

These files are the bounded surface where the current live hazards remain:
- canonical JSON drift on machine-verifiable bundle/report/signature paths
- predictable PRNG on touched runtime/security-sensitive selection paths
- production invariant enforcement still depending on `assert`
- unbounded bundle aggregation in memory
- missing or underspecified timeout/error boundaries on touched HTTP wrappers

## 3. Remaining-float inventory basis

This window must not pretend repo-wide float removal is complete. Phase 643 is
required to publish the remaining-float inventory and a durable TODO block.

That inventory must distinguish:
- runtime-critical exact-numeric work already closed
- runtime-adjacent or public-contract float surfaces still open
- lower-tier sim / analysis / devnet float surfaces still deferred

`remaining_float_inventory_and_todo_required_in_phase_643`

## 4. Second-order security guardrails

Every hardening phase in this window must obey these second-order guardrails:

- Canonical JSON on touched machine-verifiable paths requires both sorted keys
  and compact separators:
  `canonical_json_guard_requires_sort_keys_and_compact_separators`
- Non-finite numeric constants must be rejected at touched JSON/Decimal
  boundaries:
  `non_finite_json_and_decimal_rejection_required_in_touched_boundaries`
- No predictable PRNG may remain in touched runtime/security paths:
  `no_predictable_prng_in_touched_runtime_security_paths`
- Assert removal must not be replaced by broad exception swallowing:
  `assert_replacement_must_not_introduce_broad_exception_swallowing`
- Stream bounding must not simply move the attack from RAM to temp-disk
  exhaustion:
  `bounded_stream_fix_must_not_shift_attack_to_temp_disk_exhaustion`

## 5. Inherited boundary state

Window 642-648 inherits and confirms:
- Phase 609 ECU / ILC separation
- Phase 576 and Phase 581 wallet boundary
- Phase 612 two-form MVP gate rule
- ADR-0028 `Option D` active posture
- Window 631-636 exact Tier-0 numeric foundation
- Window 637-641 residual numeric contract cleanup closure

The inherited posture remains unchanged:
`wallet_boundary_576_581_unchanged_in_window_642_648`
`option_d_posture_active_after_642`

## 6. Per-phase scope constraints

Per-phase scope:
- Phase 642: sequence lock only
- Phase 643: remaining-float inventory and TODO registration only
- Phase 644: canonical JSON/signature boundary hardening
- Phase 645: PRNG, timeout, and invariant enforcement hardening
- Phase 646: NDJSON ingress and operational boundary hardening
- Phase 647: hardening gate and fix-induced regression audit
- Phase 648: closure, capsule, and handoff

No phase in this window may:
- mutate the decision log
- mutate any ADR
- widen wallet/payment authority
- claim `Option B` selection
- open `CDL-062`

## 7. Routing and exclusions

Window 623+ remains the broader runtime/interface continuation after this
bounded lane:
`window_623_plus_priority_preserved_after_642_648`

This window is additive hardening beneath that roadmap, not a replacement for
it. Exclusions for this lane:
- no decision-log mutation
- no ADR mutation
- no new constitutional vehicle
- no `CDL-062` opening
- no `Option B` selection claim
- no generalized ECU transfer or ILC transferability
- no repo-wide simulation cleanup

## AG-Gate Table

| Gate | Basis | Verdict | Note |
|---|---|---|---|
| AG-1 Co-flourishing mission | Security fixes protect agent-facing runtime trust without widening authority | PASS | bounded safety work supports agent usability rather than postponing it |
| AG-2 W_e increase | Hardening removes preventable runtime breakage on machine-verifiable paths | PASS | fewer boundary failures means less wasted work |
| AG-3 Epistemic integrity | Canonical JSON, bounded ingress, and explicit invariants improve reliability | PASS | no drift into loose runtime contracts |
| AG-4 ECU-ILC separation | No wallet widening or payment transfer work is opened here | PASS | economic posture unchanged |
| AG-5 Harness-agnostic | Touched fixes remain runtime/library level, not harness-specific | PASS | no harness lock-in |
| AG-6 Near-infinite scale | Bundle-scale limits and bounded network behavior are explicit | PASS | no unbounded ingest path remains by design intent |
| AG-7 Machine-legible first | Canonical JSON and structured error boundaries are explicit | PASS | machine-verifiable surfaces improved first |
| AG-8 Outbound economic loop | This lane does not alter economic-loop semantics | PASS | security hardening only; no regression against prior active-layer work |
