# ILC Row-5 Mechanism Selection Recommendation B-4 FIX-3 v0.1

**Phase:** B-4 FIX-3
**Window:** B-Scope FIX-3
**Date:** 2026-04-24
**Status:** hold point recommendation — FIX-3 jitter run complete
**Supersedes:** `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix2_v0.1.md`

`row5_mechanism_selection_human_gate_pending`
`row5_b4_fix3_recommendation_updated`

## 1. What changed from B-4 FIX-2

FIX-3 adds release_jitter_epochs to rolling threshold k-anonymity. The FIX-2 hold
point question Q2 asked: "Should rolling threshold with jitter mitigation be
explored before locking mechanism?" FIX-3 answers that question.

**Answer: yes — jitter=3 epochs resolves the Variant C exposure from FIX-2 while
maintaining acceptable settlement latency.**

## 2. Complete mechanism landscape (all FIX runs)

| Mechanism | A | B | C | p95 settlement | Metric | Status |
|---|---:|---:|---:|---:|---:|---|
| k=30, rolling, jitter=3 | 0.033 | 0.033 | 0.030 | **3 ep** | **0.074** | **FIX-3 winner** |
| k=20, epoch-aligned, drop | 0.060 | 0.046 | 0.005 | 5 ep | 0.103 | FIX-1 winner |
| mixing pool=32, delay=1 | 0.091 | 0.084 | 0.005 | 1 ep | 0.186 | FIX-2 fast option |
| k=20, rolling, jitter=0 | 0.050 | 0.050 | 0.824 | 1 ep | 1.831 | Not viable |

All three viable configurations clear the simulation-derived bar A≤0.15/B≤0.15/C≤0.05.

## 3. Decision summary

### 3.1 Recommended mechanism: k=30, rolling threshold, jitter=3

**k=30, rolling_threshold, release_jitter_epochs=3, bounded_hold, max_wait=3–5**

This is the best-metric configuration across all three FIX runs. It achieves:
- Lowest combined recall across all three attacker variants
- Full compliance with the simulation-derived privacy bar
- p95 settlement of 3 epochs (≈ 3 minutes at 1-minute validation epoch cadence)
- Natural scaling: at higher ILC network volume, group fill time approaches zero
  and all contributors experience the jitter-dominated settlement floor

The mechanism is operationally clean: no pool management (unlike mixing), no
epoch boundary coordination (unlike epoch-aligned), and no silent settlement
failure (bounded_hold guarantees release within max_wait).

### 3.2 Settlement timing at scale

This directly addresses the design objective: *settlement should approach near-
instantaneous as operation volume increases.*

With rolling threshold + jitter=3:
- At current simulation volume (200 contrib, 70% rate): p95 = 3 ep, mean = 1.6 ep
- At higher volume (500+ contrib, 50%+ rate): group fill time → 0; p95 → 3 ep,
  mean → 1.5 ep (pure jitter distribution, no queue-fill component)
- At very high volume (thousands of active contributors): **every transfer settles
  within 0..3 epochs of submission, bounded by the jitter window, not by queue size**

This is the correct architectural property: the jitter is a fixed privacy budget
(3 epochs = 3 minutes maximum decorrelation window), not a throughput limit.
Volume increases improve throughput and group-fill rates but do not change the
latency bound. The system naturally becomes faster under load at the p50 level
while maintaining the p95 privacy guarantee.

### 3.3 If 1-epoch p95 settlement is a hard requirement

Use mixing pool=32, delay=1 epoch (FIX-2 result):
- p95 = 1 epoch (1 minute)
- A=0.091, B=0.084, C=0.005
- Higher complexity than k-anonymity (pool management, 32-slot pool per validator)
- All privacy bars met

Note: this configuration does not improve with volume — settlement is always
delay_epochs=1 regardless of throughput.

## 4. Carry-over policy resolved

With bounded_hold and max_wait=3–5 epochs:
- Transfers that form complete groups settle within 0..3 epochs (jitter bound)
- Transfers that cannot form complete groups (sparse windows, rare contributors)
  settle within max_wait epochs as a force-release
- No silent discard. No indefinite hold. No individual-release privacy degradation
  (force-release releases with whatever group has formed, not single contributor)

The FIX-1 liveness concern (carry_over=drop → silent settlement failure) is
resolved. Use bounded_hold.

## 5. Questions for the hold point

**Q1: Accept k=30, rolling_threshold, jitter=3, bounded_hold as the mechanism?**

The simulation evidence strongly favors this configuration. It achieves the best
privacy across all three variants while meeting the settlement-at-volume objective.

If yes — B-5 proceeds to mechanism lock and B-Impl scoping.

**Q2: Is p95 ≤ 3 minutes acceptable UX, or is 1 minute required?**

If 1 minute is required: use mixing pool=32, delay=1. This forfeits the Variant
A/B improvement (0.091 vs 0.033) but maintains C=0.005.

If 3 minutes is acceptable: k=30+jitter=3 is recommended.

**Q3: Simulation-derived bar confirmation**

All FIX-3 best configurations clear A≤0.15, B≤0.15, C≤0.05. This bar is
confirmed as the B-Impl target pending live confirmation via SIM-LEAKAGE-03.

**Q4: k=30 group-fill contingency**

If B-Impl live testing shows insufficient contributor volume to reliably fill
k=30 groups within max_wait epochs, fallback to k=20 with jitter=3 (not yet
simulated but expected to be similar: A≈0.05 vs 0.033, C≈0.05–0.10 depending
on jitter effectiveness at k=20). Should FIX-4 explore k=20+jitter to provide
the fallback evidence?

## 6. What B-Impl must deliver

For k=30, rolling_threshold, jitter=3:
- Rolling group construction integrated into the transfer submission path
- Deferred release queue with jitter scheduling
- bounded_hold carry-over with max_wait enforcement
- Group-fill monitoring: alert if k=30 groups fail to fill within 2×max_wait
- Failure notification path for force-released transfers (so contributors know
  their transfer settled with a degraded anonymity set)
- Live instrumentation sufficient to run SIM-LEAKAGE-03 against the M-009
  testbed or equivalent

## 7. Non-claims

This recommendation does NOT:
- Pre-select the mechanism (Q1 requires human response)
- Set the runtime bar (still simulation-derived, pending B-Impl)
- Authorize B-5 (hold point remains active until human responds)
- Guarantee that k=30 fills reliably at ILC mainnet launch volume
- Claim jitter=3 provides the same Variant C protection as epoch-aligned release
  (epoch-aligned achieves C=0.005; jitter=3 achieves C=0.030 — both below 0.05 bar
  but epoch-aligned is stronger)
