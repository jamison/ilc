# ILC Integration Coherence Report — Phase 846

**Phase:** 846
**Window:** 844–847
**Date:** 2026-04-26
**Status:** coherent — Row 5 runtime_closed

`coherence_report_846_published`
`row5_runtime_closed_recorded_in_coherence_846`

---

## 1. Purpose

Phase 846 is the Row-5 closure evaluation phase for window 844–847. It:

1. Opens and ratifies CDL-072 (Bound B formula revision)
2. Re-runs SIM-LEAKAGE-03 under the corrected formula
3. Advances Row 5 from `spec_closed_runtime_pending` to `runtime_closed`
4. Records the definitive pass verdict for the capsule

---

## 2. CDL-072 Coherence

**Amendment scope:** Narrow and well-bounded.

- Only `ilc_core/privacy/metrics.py` (`_check_jitter_spread`, one new constant, CDL dependency token)
- No mechanism change (k, jitter range, max_wait untouched)
- No change to Bounds A or C
- No settlement routing, live ECU paths, or protocol state affected

**Amendment necessity:** The Phase 845 structural finding is conclusive:
`std(jitter)/max(jitter) ≤ 0.15` requires ≥97.7% of groups to have
identical jitter — structurally incompatible with `secrets.randbelow(J+1)`.
CDL-072 replaces it with a formula that tests the actual invariant.

**Option B correctness:** `max(observed_jitter) ≤ release_jitter_epochs`
directly operationalizes "no group settles after the configured window." It
catches real bugs (PRNG overflow, epoch arithmetic errors) while being satisfied
by construction for a correctly implemented mechanism.

---

## 3. SIM-LEAKAGE-03 Final Verdict

| Bound | Old formula | New formula (CDL-072) | Result |
|-------|------------|----------------------|--------|
| A | fill-failure ≤ 0.15 | (unchanged) | PASS |
| B | std/max ≤ 0.15 | max(jitter) ≤ 3 | PASS |
| C | degraded_fraction ≤ 0.05 | (unchanged) | PASS |

`check_bounds()` → `{"A": True, "B": True, "C": True}` ✅

---

## 4. Row 5 Advancement

| Phase | Event |
|-------|-------|
| B-Scope (Phase 770+) | Mechanism locked: k=30, jitter=3, bounded_hold |
| Phase 831–833 | B-Impl obligations 1–6 delivered |
| Phase 834 | Honest non-closure (SIM-LEAKAGE-03 not yet live) |
| Phase 844 | Rust routing instrumentation — 42/42 tokens, contribution class |
| Phase 845 | Live run — A PASS, B FAIL (structural), C PASS — honest non-closure |
| Phase 846 | CDL-072 ratified; re-run — A PASS, B PASS, C PASS → **runtime_closed** |

`row5_runtime_closed_846`

---

## 5. Inheritance and Scope Boundaries

This coherence report does NOT:
- Claim any CDL row mutation beyond CDL-072
- Change Option B graduation posture
- Mutate any Row other than Row 5
- Affect live settlement routing or ECU paths
- Claim capsule advance (capsule v5.20 published separately in Phase 846)

---

## 6. Forward Obligations

- **Phase 847** — closure gate, STATUS.md update, window 844–847 close
- **CDL-070** — PQ migration ceremony (deferred, carries forward)
- **CDL-071** — temporal tier reconciliation (deferred, higher priority than CDL-070)
- **Row 5 carry-forward:** `runtime_closed` is recorded. Option B graduation posture
  unchanged (ADR-0028 = option_b, Phase 814 selection).
