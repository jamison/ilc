# ILC Row-5 Mechanism Selection Recommendation B-4 FIX-1 v0.1

**Phase:** B-4 FIX-1
**Window:** B-Scope FIX-1
**Date:** 2026-04-23
**Status:** hold point recommendation — updated from real simulation
**Supersedes:** `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_v0.1.md`

`row5_mechanism_selection_human_gate_pending`
`row5_b4_fix1_recommendation_updated`

## 1. What changed from B-4

The original B-4 recommendation was derived from formula-based metric
functions. The FIX-1 real Monte Carlo simulation (120 iterations, 5.6 minutes,
2.81s/iteration) produced materially different results on two dimensions:

| Dimension | B-3 formula result | FIX-1 real simulation |
|---|---|---|
| Family ranking | Mixing dominant | **k-anonymity dominant** on Pareto frontier |
| Proposed closure bar | A≤0.30, B≤0.45, C≤0.40 | **A≤0.15, B≤0.15, C≤0.05** |
| Mixing competitive? | Yes, at moderate pool sizes | Only at pool_size=32 (highest complexity) |
| k-anon competitive? | No (Variant C couldn't clear 0.45) | Yes, strongly |

This recommendation is not a cosmetic update — the underlying evidence changed.

## 2. Decision summary

### 2.1 Mechanism family

The Pareto frontier is dominated by **k-anonymity** (`k=20`, `epoch_aligned`
partitioning, `rebatch_interval_epochs=5`).

Mixing is **not recommended as the primary mechanism** based on FIX-1 evidence.
Mixing reaches competitive privacy only at `pool_size=32` (the maximum explored),
at higher complexity (0.70–0.96 vs k-anonymity 0.56), without improving on
k-anonymity's recall numbers.

**HOWEVER**: there is an important caveat that requires human judgment (§3).

### 2.2 Recommended parameter range

If k-anonymity is confirmed as the mechanism:

- `k_value`: **16–20** (k=20 is optimal; k=16 provides a lower-complexity
  fallback with slightly higher recall)
- `partition_strategy`: **epoch_aligned** (creates stable, predictable batches)
- `rebatch_interval_epochs`: **3–5** (5 epochs = 5 minutes of buffering before
  release; 3 epochs is the minimum that reliably fills k=20 groups at 70%
  contribution rate)
- `carry_over_policy`: **hold OR timeout-bounded** (see §3 — `drop` dominates
  the simulation but is a real liveness concern; human must decide)
- `amount_distribution` has negligible effect on k-anonymity recall

If mixing is preferred despite the Pareto evidence:

- `mix_pool_size`: **32** (below 32, mixing is dominated by k-anon)
- `num_rounds`: **2–5** (minimal marginal effect above 2 at pool=32)
- `delay_epochs`: **1–2** (4-epoch delay adds latency without proportionate
  privacy gain at pool=32)
- `forward_fraction`: **0.85–1.0**
- `shuffle_strategy`: **uniform** or **weighted_by_volume** (negligible difference)

### 2.3 Simulation-derived bar recommendation

Updated simulation-derived bar recommendation, pending B-Impl live confirmation:

- Variant A: **≤ 0.15**
- Variant B: **≤ 0.15**
- Variant C: **≤ 0.05**

The old B-3 recommendation (A≤0.30, B≤0.45, C≤0.40) is now too lenient.
Both competitive mechanism families achieve well below those thresholds in the
model. A tighter bar is both achievable and honest.

This is still a simulation-derived bar recommendation. The constitutionally
final runtime bar is set when B-Impl runs SIM-LEAKAGE-03 against the live
system and measured recall falls within it.

## 3. Human judgment required: the carry_over=drop liveness problem

The dominant k-anonymity configuration uses `carry_over_policy=drop`. This
means transfers that do not complete a k-group within a rebatch window are
**silently discarded**. The simulation treats this as a privacy neutral miss
(the transfer is not attributed because it is not in the event stream). In
a real system, this is a **settlement failure**: the contributor submitted a
transfer that never committed.

This requires an explicit human decision before B-Impl scopes the mechanism:

**Option A — carry_over=drop with explicit timeout:**
Transfers that miss their window are dropped, but the contributor receives an
explicit failure response (not silently lost). They can retry. Privacy is
preserved. Liveness is bounded: contributors retry on failure.
*Complexity implication:* requires a failure-notification path.

**Option B — carry_over=hold with maximum wait cap:**
Transfers hold across windows until a group forms, up to a maximum wait of
N windows (e.g., 3 windows = 15 minutes at rebatch=5 epochs). After the cap,
the transfer is released individually (losing k-anon for that transfer) or
dropped with failure notification.
*Privacy implication:* individual releases above the cap degrade Variant A
for low-activity contributors. Recall impact depends on how often contributors
fail to find k-groups.

**Option C — carry_over=immediate always (k-anon fallback):**
If a group doesn't form, release transfers individually with a single-
contributor anonymity set. This degrades privacy to the baseline for transfers
in sparse windows.
*Privacy implication:* the simulation shows this raises recall significantly
(see k-anon `immediate` results — metric ~1.4 vs `drop` metric ~0.10).

The simulation cannot determine which option is correct — this is a design
decision about the tradeoff between privacy, liveness, and user experience.

## 4. Why mixing might still be preferred despite Pareto evidence

The Pareto evidence favors k-anonymity, but there are legitimate reasons to
prefer mixing that the simulation does not capture:

1. **Epoch-aligned release timing is itself a signal.** k-anonymity with
   `epoch_aligned` partitioning releases all groups simultaneously at the
   end of the rebatch window. A network-level observer who can time global
   release events may be able to identify that all transfers in a given
   release burst came from the same rebatch window, reducing the effective
   anonymity set.

2. **Fixed group size leaks participant count.** k=20 means every batch
   contains exactly 20 contributors. An attacker who knows k can reduce
   their search space to exactly k contributors per batch.

3. **Mixing is architecturally more aligned with the aspirational goal.**
   The original aspiration was the mixing layer because it more closely
   resembles classical anonymous communication systems (Chaum mixes, Tor
   circuits) where the privacy property is well-studied. k-anonymity's
   privacy properties under adaptive adversaries are less thoroughly
   analyzed in the literature.

None of these reasons is quantified in the simulation. They are offered for
human consideration.

## 5. Explicit questions for the hold point

The following questions require human response before B-5 proceeds:

**Q1: Mechanism family selection**
Given that k-anonymity dominates the Pareto frontier but mixing has
legitimate architectural arguments not captured in the simulation:
- Accept k-anonymity as the mechanism family? OR
- Accept mixing as the mechanism family (acknowledging the higher
  complexity and Pareto-dominated position)?

**Q2: Carry-over policy (k-anonymity only)**
If k-anonymity is selected:
- Which carry-over policy? (drop+notify / hold+timeout-cap / immediate)
- What is the maximum acceptable wait before a transfer is either released
  individually or explicitly failed?

**Q3: Simulation-derived bar recommendation**
Do you accept A≤0.15, B≤0.15, C≤0.05 as the intended B-Impl target
pending live confirmation? Or should the bar be set differently?

**Q4: Any adjustments before B-5 locks the selection?**

## 6. What B-Impl will need to deliver

Regardless of mechanism choice:
- Real implementation of the selected mechanism in the ILC gossip/settlement path
- Log hygiene (Layer 1, Phase 777) verified still in place
- Live instrumentation sufficient to run SIM-LEAKAGE-03 against the M-009
  testbed or equivalent
- Measured recall under the B-Impl target bar
- Honest closure verdict based on live evidence

For k-anonymity specifically:
- Group construction logic integrated into the transfer submission path
- Carry-over policy implementation with the chosen approach
- Release timing integrated with epoch boundaries
- Failure notification path if drop policy is chosen

For mixing specifically:
- Pool management integrated into the validator-to-validator relay path
- Release scheduling logic against epoch timing
- pool_size=32 implies significant memory commitment per validator

## 7. Non-claims

This recommendation does NOT:
- Pre-select the mechanism (human confirmation required at Q1)
- Set the runtime bar (still simulation-derived, pending B-Impl)
- Authorize B-5 (hold point remains active until human responds)
- Claim that the real simulation perfectly models live behavior
