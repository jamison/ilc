# ILC Security Hardening Gate and Fix-Induced Regression Audit 647 v0.1

Status: hardening gate artifact
Date: 2026-04-14
Classification: hardening gate and regression audit
Phase: 647
Owner lane: G8 security boundary and remaining-float strike force

## 1. Gate identity and pass basis

Phase 647 is the bounded hardening gate for Window 642-648.

The gate passes only if:
- the first-order security issues touched in Phases 644-646 remain closed
- the expected second-order regressions were actively checked
- the remaining-float inventory and TODO carry-forward are still present

`window_642_648_security_hardening_gate_pass_required`

## 2. First-order issue checklist

Checked first-order issues:
- canonical JSON/signature drift on touched bundle/report/CLI surfaces
- predictable PRNG on touched runtime/security-sensitive paths
- production invariant enforcement via `assert` on the touched passive ECU runtime
- unbounded NDJSON bundle aggregation in memory
- missing bifurcated timeout contracts on the touched HTTP wrappers

## 3. Fix-induced regression checklist

Checked second-order regressions:
- canonical JSON fix did not leave whitespace/separator drift:
  `canonical_json_fix_induced_whitespace_drift_checked`
- PRNG fix did not simply swap in a new entropy-heavy runtime dependency and the
  touched deterministic selection remains reproducible:
  `prng_fix_induced_entropy_or_determinism_regression_checked`
- assert replacement did not introduce broad exception swallowing on the touched
  boundaries:
  `assert_replacement_exception_swallowing_regression_checked`
- bounded stream fix did not shift the attack to temporary-disk spooling:
  `bounded_stream_fix_did_not_shift_attack_to_temp_disk_checked`

## 4. Remaining-float carry-forward verification

Verified before closure:
- `docs/specs/ilc_remaining_float_and_security_follow_on_inventory_643_v0.1.md`
  exists and still carries the post-641 float inventory
- `TODO.txt` still contains the top-level Post-641 remaining-float/security block

`remaining_float_inventory_and_todo_verified_before_closure`

## 5. Test matrix and command record

Hardening gate command:
- `bash tools/run_window_642_648_security_hardening_gate_phase_647.sh`

Covered slices:
- Phase 643 inventory/TODO guard
- Phase 644 canonical JSON/signature hardening slice
- Phase 645 PRNG/timeout/assert hardening slice
- Phase 646 NDJSON ingress and CLI boundary slice

## 6. Verdict and closure readiness

Verdict: PASS.

The bounded security issues touched by Window 642-648 are closed to the extent
promised by the window, and the second-order regressions anticipated by the
planning packet were explicitly checked rather than assumed away.
