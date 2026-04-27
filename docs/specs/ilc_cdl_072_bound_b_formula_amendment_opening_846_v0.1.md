# ILC CDL-072 Bound B Formula Amendment — Opening v0.1

Status: opening artifact
Date: 2026-04-26
Decision vehicle: CDL-072
Phase: 846

`cdl_072_bound_b_formula_amendment_opening_846`
`cdl_072_opened_phase_846`

---

## 1. Decision Identity

**CDL-072** — Row-5 SIM-LEAKAGE-03 Bound B formula revision.

**Related:** ADR-0028 (Option B selection), Phase 831–833 (B-Impl obligations 1–6),
Phase 834 (honest non-closure), Phase 845 (SIM-LEAKAGE-03 live run — Bound B
structural finding), commissioning spec §1 and §3.6.

**Trigger:** Phase 845 evidence `sim_leakage_03_bound_b_fail_structural` —
the original Bound B formula `std(jitter)/max(jitter) ≤ 0.15` is structurally
incompatible with the locked jitter mechanism. Carry-forward obligation
`bound_b_formula_revision_carry_forward` recorded at Phase 845.

---

## 2. Decision Topic

Replace the Bound B evaluation criterion in the Row-5 SIM-LEAKAGE-03 evaluation
suite with a formula that:

1. Correctly operationalizes the intended property (no group settles later than
   the locked jitter window permits), and
2. Is achievable under the locked mechanism
   (`secrets.randbelow(release_jitter_epochs + 1)`, i.e., jitter ∈ {0..J}).

---

## 3. Why the Current Formula Fails

The current formula:

```
Bound B: std(jitter_deltas) / max(jitter_deltas) ≤ 0.15
```

requires that the standard deviation of the jitter distribution is ≤ 15% of its
maximum value. For the locked mechanism with `release_jitter_epochs=3`:

- Jitter samples drawn uniformly from {0, 1, 2, 3}
- Expected std ≈ 1.12 (population), max = 3 → spread ≈ 0.37 → **FAIL**
- The bound passes only if ≥97.7% of groups have identical jitter
- This is impossible with a uniform PRNG and defeats the purpose of jitter

**What the formula was intended to test:** detect extreme jitter outliers that
would significantly delay transfer settlement — a form of liveness violation.

**The confusion:** the `std/max` formula tests *relative concentration* (are all
groups settling at nearly the same delay?). Concentration is not the property we
care about. Jitter is *supposed* to be random; uniformity is the feature.

---

## 4. Options

| Option | Formula | Assessment |
|--------|---------|-----------|
| A | `std(jitter) / max(jitter) ≤ 0.15` (current) | Structurally incompatible — REJECTED |
| B | `max(jitter_deltas) ≤ release_jitter_epochs` | Tests liveness boundary directly; would catch PRNG overflow bugs |
| C | `std(jitter) ≤ release_jitter_epochs × 0.50` | Absolute std bound (std ≤ 1.5 for J=3); passes with uniform {0..3}; std≈1.12 |
| D | Drop B entirely; add new Bound D for max settlement delay | Operationally clean but increases CDL surface |

---

## 5. Chosen Option

**Option B: `max(observed_jitter_deltas) ≤ release_jitter_epochs`**

**Rationale:**

1. **Direct property test.** The intent of Bound B is "no group settles after
   the locked jitter window closes." Option B tests this directly: if any observed
   jitter delta exceeds `release_jitter_epochs`, the jitter mechanism is broken.

2. **Catches real bugs.** A PRNG implementation error (e.g., `randint(0, J+1)`
   returning J+1, off-by-one in the release epoch computation, or incorrect
   epoch arithmetic) would produce jitter > J and cause this bound to fail.

3. **Consistent with the locked mechanism.** `secrets.randbelow(J+1)` guarantees
   jitter ∈ {0..J} by construction, so a correct implementation always passes.

4. **Minimal CDL surface.** No new bound letter; B is revised in place.

5. **Avoids trivial vacuity.** The bound cannot pass vacuously (all-zero jitter)
   because max=0 ≤ J=3 is a valid pass — but that case represents a mechanism
   that always releases immediately, which A and C together validate anyway.

**Implementation:** Replace `_check_jitter_spread` in `LeakageMetricsCollector`
with a `max(jd.keys()) ≤ SIM_LEAKAGE_03_BOUND_B_MAX_JITTER` check.

---

## 6. Scope

This CDL amends:

1. `ilc_core/privacy/metrics.py` — `_check_jitter_spread` implementation and
   new module constant `SIM_LEAKAGE_03_BOUND_B_MAX_JITTER`
2. The Bound B entry in commissioning spec §1 (informational note added)

This CDL does NOT:

- Change the mechanism (k, jitter range, max_wait) — locked by B-Scope
- Change Bound A or Bound C thresholds
- Modify any other CDL row
- Affect settlement routing, live ECU paths, or any code outside `metrics.py`

---

## 7. Verification Artifact

Gate tests in `tests/test_phase_846_cdl_072_bound_b_and_row5_closure.py`:

- CDL-072 row exists in CDL master log with `status: ratified`
- `check_bounds()` returns `{"A": True, "B": True, "C": True}` at 10 epochs × 30 transfers
- No jitter value in any run exceeds `release_jitter_epochs=3`
- Row 5 advances to `runtime_closed` in the evidence record

`cdl_072_verification_artifact_defined`
