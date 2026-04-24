# ILC Row-5 Mechanism Selection Recommendation B-4 FIX-2 v0.1

**Phase:** B-4 FIX-2
**Window:** B-Scope FIX-2
**Date:** 2026-04-23
**Status:** hold point recommendation — updated with settlement timing evidence
**Supersedes:** `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix1_v0.1.md`

`row5_mechanism_selection_human_gate_pending`
`row5_b4_fix2_recommendation_updated`

## 1. What changed from B-4 FIX-1

FIX-2 added three simulation capabilities: rolling threshold release, settlement
timing metrics, and realistic contributor distributions (power_law / long_tail).
The central finding of FIX-2 directly answers the user's question:

> "Is it necessary to wait to release batches or can they be done on a rolling basis
> in a way that decreases time to settlement while maintaining the other desired
> factors?"

**Answer: rolling threshold is fast but exposes Variant C under realistic workloads.**

| Mechanism | Settlement p95 | Recall A | Recall B | Recall C | Viable? |
|---|---:|---:|---:|---:|---|
| k-anon k=20, rolling, bounded_hold, long_tail | 1 ep | 0.050 | 0.050 | **0.824** | No — C fails |
| mixing pool=32, delay=1, uniform | **1 ep** | 0.091 | 0.084 | **0.005** | **Yes** |
| mixing pool=32, delay=2, uniform | 2 ep | 0.091 | 0.083 | 0.005 | Yes |
| k-anon k=20, epoch_aligned, drop, uniform (FIX-1) | 3–5 ep | 0.060 | 0.046 | 0.005 | Yes |

## 2. Revised mechanism recommendation

### 2.1 If fast settlement (p95 ≤ 1 epoch, ≈ 1 minute) is the priority

**Recommend: mixing pool=32, rounds=2, delay=1 epoch.**

This is the only configuration in the FIX-2 evidence that simultaneously achieves:
- Settlement p95 = 1 epoch
- Variant C recall ≤ 0.01
- Variant A and B recall ≤ 0.10

Complexity is 0.72 (higher than k=20 epoch_aligned at 0.56, but operationally
feasible — 32 in-flight contributors per validator pool).

### 2.2 If maximum privacy (all three variants minimized) is the priority

**Recommend: k-anonymity k=20, epoch_aligned, bounded_hold with max_wait=3–5 epochs.**

This follows from FIX-1 evidence (the FIX-1 result was not re-reached in FIX-2 due
to parameter space expansion, but is not invalidated). Settlement p95 is 3–5 epochs
(3–5 minutes at 1-minute validation epoch cadence).

Do NOT use rolling threshold with this configuration. Rolling threshold exposes
Variant C to 0.82–0.99 recall under long_tail/power_law contributor distributions.

### 2.3 Rolling threshold with jitter mitigation (future option, not yet modeled)

Rolling threshold can be made Variant-C-safe by adding a random release jitter
of 0–J epochs before each completed group is released. This blurs the correlation
between contributor activity timing and release timing. The jitter adds at most
J epochs to p95 settlement. J=2 would give p95 ≈ 3 epochs — comparable to
epoch-aligned — while maintaining the fast-path for groups that happen to be
released without jitter. This is not modeled in FIX-2 and requires FIX-3 to validate.

## 3. The settlement timing question answered

At 1-minute validation epoch cadence:

| Config | p95 settlement time | Notes |
|---|---|---|
| Rolling threshold k=20 | ~1 minute | Fast, but Variant C 0.82+ with real distributions |
| Mixing pool=32, delay=1 | ~1 minute | Fast, Variant C protected |
| Mixing pool=32, delay=2 | ~2 minutes | Good privacy |
| k-anon k=20, epoch_aligned, rebatch=5 | ~5 minutes | Maximum privacy |
| k-anon k=5, epoch_aligned, rebatch=2 | ~2 minutes | Lower k, higher recall |

**1-minute UX is achievable** with mixing pool=32 + delay=1. This is not
prohibitively complex and eliminates the liveness concern from k-anonymity's
carry_over=drop policy.

## 4. Carry-over policy update

The FIX-1 concern about `carry_over=drop` is partially resolved by FIX-2:

- `carry_over=bounded_hold` with `max_wait_epochs=3–5` eliminates silent discard.
  Contributors are held for up to 3–5 epochs, then force-released individually.
- FIX-2 shows `bounded_hold` with rolling threshold still exposes Variant C.
  `bounded_hold` with epoch_aligned release maintains C protection.
- Mixing has no carry_over concern — pool fill is opportunistic; unused slots
  are discarded at epoch boundary without a settlement failure.

If k-anonymity is selected: use `bounded_hold` with `max_wait_epochs=3`,
`release_strategy=epoch_aligned`. This provides the FIX-1 privacy result plus
a guaranteed settlement bound of 3 rebatch windows.

## 5. Revised questions for the hold point

The B-4 FIX-1 questions remain, with updated evidence:

**Q1: Mechanism family selection**

The FIX-2 evidence changes the framing:
- **k-anonymity** (FIX-1 Pareto winner): best recall (A≈0.06, B≈0.05, C≈0.005)
  at complexity 0.56, settlement p95 ≈ 5 minutes. Epoch-aligned only.
- **Mixing pool=32** (FIX-2 speed result): A≈0.09, B≈0.08, C≈0.005
  at complexity 0.72, settlement p95 ≈ 1 minute. Operationally simpler.

If 1-minute settlement is important for user experience: **mixing is recommended**.
If 5-minute settlement is acceptable and maximizing privacy is paramount:
**k-anonymity with k=20 epoch-aligned is recommended**.

Rolling threshold k-anonymity is **not recommended without jitter mitigation**.

**Q2: Carry-over policy (k-anonymity only)**
- Recommended: `bounded_hold` with `max_wait_epochs=3`, `release_strategy=epoch_aligned`
- This eliminates the FIX-1 silent-drop concern with minimal privacy cost.

**Q3: Simulation-derived bar recommendation**
FIX-1 bar (A≤0.15, B≤0.15, C≤0.05) is maintained with one addition:
- Variant C bar applies only to epoch-aligned release strategies.
- If rolling threshold is deployed, Variant C requires separate timing-privacy analysis.

**Q4: Settlement time requirement**
New question from FIX-2 evidence: Is p95 ≤ 1 minute required, or is p95 ≤ 5 minutes
acceptable? This directly determines mixing vs k-anonymity.

## 6. Non-claims

This recommendation does NOT:
- Pre-select the mechanism (Q1 requires human response)
- Authorize rolling threshold without jitter mitigation analysis
- Set the runtime bar (still simulation-derived, pending B-Impl)
- Authorize B-5 (hold point remains active until human responds)
- Claim FIX-2's mixing result invalidates FIX-1's k-anonymity result — both are
  valid measurements of different configurations; the user's settlement timing
  preference determines which applies
