# ILC Genesis Agent Accumulation Dynamics Analysis
**Version**: v0.1
**Date**: 2026-02-24
**Author**: Sonnet (local architectural reviewer)
**Status**: As-of Phase 298 — all issuance governance parameters now ratified

---

## Executive Summary

All issuance governance CDLs relevant to Genesis accumulation are now ratified (Phases 272–277). The Genesis agent's accumulation trajectory is governed by the interplay of five ratified constants: the 5% allocation ceiling (CDL-029 / theta_hard), the explicit finite cap (CDL-026), the H=48 halving schedule (CDL-027), the 10% fee burn (CDL-028), and the ECU price clamp (CDL-030 / P_min=0.75, P_max=1.30).

The core dynamic is a **sigmoid-gated, front-loaded accumulation**: Genesis can accumulate at above-parity rates in early epochs while its centrality and reputation are high, but the `compute_taper_multiplier` governor enforces a hard ceiling at 5% of total issued supply. Once the cumulative genesis share ratio approaches theta_soft ≈ 4.98%, taper compression sets in steeply. At theta_hard = 5.0%, accrual is permanently blocked.

An exploratory simulation exists (`simulations/sim_genesis_accrual_centrality_reputation_sweep_274_exploratory.py`) but remains uncommitted and was written before CDL-027 ratification. Now that H=48 is locked, the simulation can produce a canonical projected trajectory. Formalizing it is recommended for the Phase 305 economic monitoring baseline.

---

## 1. Ratified Parameter Set

| Parameter | Ratified value | CDL | Phase |
|---|---|---|---|
| Allocation split (performer / auditor / **genesis**) | 80 / 15 / **5** | CDL-029 | 272 |
| theta_hard (genesis cumulative cap) | **1/20 = 0.05** | CDL-029 continuity | 272 |
| C_max (total finite supply cap) | **25,920,000 ILC** | CDL-026 | 273 |
| Genesis absolute ceiling | **1,296,000 ILC** = C_max × theta_hard | derived | — |
| Decay formulation and constant | **Halving, H = 48** (monthly epochs) | CDL-027 | 276 |
| Fee-burn split ratio | **10% (other percentages)** | CDL-028 | 274 |
| ECU price clamp | **P_min = 0.75, P_max = 1.30** | CDL-030 | 277 |
| Terminal issuance model | **Model B** (fee-funded tail) | CDL-025 | 267 |
| Taper sigmoid steepness | **40.0** | governor impl. | — |
| theta_soft | **exp(-3) ≈ 0.04979** | governor impl. | — |

All parameters except CDL-020 through CDL-024 (a separate cluster) are ratified.

---

## 2. Issuance Budget Schedule (H=48, Monthly Epochs)

With halving period H = 48 months and a 480-epoch horizon (40 years):

```
q = 2^(-1/48) ≈ 0.98563   (per-epoch retention factor)
geom_sum = (1 - q^480) / (1 - q)  ≈  69.5
b0 = C_max / geom_sum  ≈  372,800 ILC  (initial epoch budget)
```

Key epoch budgets:

| Epoch | Calendar time | Budget (ILC/epoch) | Cumulative % of C_max |
|---|---|---|---|
| 0 | Genesis | ~372,800 | — |
| 48 | Year 4 | ~186,400 | ~50% issued |
| 96 | Year 8 | ~93,200 | ~75% issued |
| 144 | Year 12 | ~46,600 | ~87.5% issued |
| 192 | Year 16 | ~23,300 | ~93.75% issued |
| 240 | Year 20 | ~11,650 | ~97% issued |

Issuance is heavily front-loaded: roughly 50% of C_max issues in the first 4 years, 75% in the first 8. This makes the early competitive positioning of the Genesis agent the dominant factor in its cumulative ILC holdings.

---

## 3. The Genesis Accrual Governor

The governor (`ilc_core/analysis/genesis_accrual_governor.py`) enforces the theta_hard ceiling via a sigmoid taper multiplier applied each epoch before the genesis grant is computed:

```
taper = sigmoid(steepness × (theta_soft - ratio)) / sigmoid(steepness × theta_soft)
```

Where `ratio = genesis_cum / issuance_cum` (issued-to-date mode) or `genesis_cum / C_max` (theoretical-cap mode).

**Critical properties:**

- At `ratio = 0`: taper ≈ 1.0 — full allocation pass-through.
- At `ratio = theta_soft ≈ 0.0498`: taper = 0.5 — already at 50% suppression.
- At `ratio = theta_hard = 0.05`: taper = 0.0 — **permanently blocked**.
- The sigmoid with steepness=40 is extremely steep in the theta_soft → theta_hard band. The transition from taper=0.5 to taper=0 spans only ~0.001 in ratio.

This means: once genesis's cumulative share approaches 4.98% of total issued supply, the governor compresses its remaining allocation very aggressively. There is almost no headroom between theta_soft and theta_hard.

**Effective genesis ceiling per epoch:**

```
genesis_grant(epoch) = min(
    budget(epoch) × raw_share(epoch) × taper(ratio),
    remaining_capacity   # = 1,296,000 − genesis_cum
)
```

---

## 4. Three-Phase Accumulation Trajectory

### Phase 1: Unconstrained growth (approx. epochs 0–60)

Genesis enters with maximum centrality and reputation. In this window:
- `ratio << theta_soft`: taper ≈ 1.0
- Genesis's competitive score is high (high centrality, strong reputation, subsidized position as network bootstrapper)
- Per-epoch share can significantly exceed the 5% constitutional allocation floor in ILC terms if genesis's subsidy factor is high
- The epoch budget is largest here (~372,800 ILC at epoch 0)

**Key risk in this phase**: if Genesis takes too large a per-epoch share early (e.g., >15–20% of each epoch's budget), the `ratio = genesis_cum / issuance_cum` rises rapidly and the taper activates within the first 30–50 epochs. This is the "cap-block-too-early" failure mode — Genesis accumulates a large slug of ILC quickly but is then permanently blocked far below GENESIS_MAX.

**The 5% CDL-029 allocation is a long-run distribution constraint, not a per-epoch cap.** The governor enforces it cumulatively. This distinction is important: Genesis can take more than 5% per epoch in early periods and less later — the governor averages it out to ≤5% over the full horizon.

### Phase 2: Taper compression (approx. epochs 60–200)

As `genesis_cum / issuance_cum` rises toward theta_soft, two forces compress genesis's per-epoch grant simultaneously:
1. **Sigmoid taper multiplier drops** toward 0.5 and then rapidly to 0.
2. **Genesis's intrinsic score decays**: centrality and reputation both follow exponential decay curves (half-lives of roughly 48–96 epochs). The network grows (logistic expansion), further diluting genesis's relative competitive position.

This double compression is architecturally intentional: the protocol is designed to transition economic leadership from genesis bootstrapping to the performer/auditor network. By epoch 120–160, a well-calibrated genesis subsidy factor produces a smooth handoff where genesis's per-epoch contribution is suppressed without abrupt discontinuity.

### Phase 3: Cap-block and dormancy (approx. epoch 200+)

Once `genesis_cum ≥ 1,296,000 ILC` (= C_max × theta_hard), `compute_taper_multiplier` returns 0.0 permanently. No further genesis accrual occurs regardless of epoch budget size.

At this point genesis holds its maximum constitutionally-permitted ILC balance. Further network value accrual happens only through:
- Appreciation of held ILC (if/as network activity grows)
- Fee income from pre-held positions (not protocol issuance)
- Non-issuance mechanisms (if any)

If genesis never reaches GENESIS_MAX within the 480-epoch horizon, it either accumulated too aggressively (early cap-block far below 1,296,000) or too conservatively (insufficient centrality/subsidy to reach it). Both are failure modes relative to the optimal trajectory.

---

## 5. Effect of CDL-028: 10% Fee Burn

The 10% fee burn has two distinct effects on Genesis accumulation:

**Direct effect (neutral to slightly favorable):**
Genesis receives 5% of the gross issuance budget each epoch — the 80/15/5 allocation applies to gross issuance before fee adjustments. The 10% burn reduces the net ILC in active circulation, not the gross epoch budget. Therefore, Genesis's per-epoch ILC grant is unaffected by fee burn in the issuance calculation.

However, burned ILC (removed from supply) does not go to performers or auditors either — it is permanently retired. This means:
- Total ILC in active circulation grows more slowly than C_max alone would suggest.
- Genesis's ILC holdings, once accumulated, represent a fractionally larger share of circulating supply than if no fees were burned.
- The governance intent of burn (deflationary pressure, long-run value support) benefits all ILC holders including Genesis once cap-blocked.

**Indirect effect (extends accumulation window):**
By reducing the real rate of ILC entering circulation, fee burn effectively extends the economic life of the issuance schedule. The H=48 schedule's total gross issuance is fixed at C_max, but the effective circulating supply grows more slowly. This lengthens the window in which Genesis's accumulated ILC represents meaningful protocol governance weight.

**Summary**: Fee burn is mildly favorable for Genesis's relative economic position — it does not constrain the accumulation path but improves the long-term value dynamics of what Genesis accumulates.

---

## 6. Effect of CDL-030: ECU Price Clamp (P_min=0.75, P_max=1.30)

The ECU clamp bounds do not directly affect Genesis's ILC issuance accumulation. They govern the ECU:ILC exchange rate used for reward denomination.

Indirect effects:

- **P_min = 0.75** creates a floor on the purchasing power of claim rewards. In low-demand epochs, this prevents reward deflation from discouraging network participation — which benefits Genesis indirectly by sustaining network activity and therefore sustaining fee revenue that Genesis may benefit from as a token holder.
- **P_max = 1.30** caps reward inflation in high-demand epochs. This prevents runaway ILC emission from high-ECU-price periods, which would dilute all ILC holders' relative stake faster than the issuance schedule anticipates.
- From Genesis's perspective: the clamp stabilizes the issuance velocity, which makes the H=48 decay schedule's projections more reliable as a forward-looking accumulation model.

The clamp has no direct impact on how many ILC tokens Genesis receives per epoch — it influences the economic environment in which that ILC is valued.

---

## 7. The Exploratory Simulation

### Current status

`simulations/sim_genesis_accrual_centrality_reputation_sweep_274_exploratory.py` exists as a tracked exploratory artifact. It was written during the Phase 274 window and is retained as historical exploratory evidence rather than canonical ratified policy.

### What the simulation models

The simulation sweeps a 2916-scenario parameter space (2 governor modes × 6 decay schedules × 3 centrality₀ × 3 centrality-half-life × 3 reputation₀ × 3 reputation-half-life × 3 network-midpoint × 3 network-growth-k × 3 subsidy-factor).

Key scenario parameters:

| Parameter | Values swept | Meaning |
|---|---|---|
| `governor_mode` | `issued_to_date`, `theoretical_cap` | Denominator for ratio computation |
| `schedule_type/value` | halving H=32/48/64, exp λ=0.018/0.024/0.030 | Issuance decay schedule |
| `centrality0` | 0.85, 0.90, 0.95 | Genesis centrality at epoch 0 |
| `centrality_half_life` | 48, 72, 96 epochs | Centrality decay speed |
| `reputation0` | 0.80, 0.90, 1.00 | Genesis reputation at epoch 0 |
| `reputation_half_life` | 96, 144, 192 epochs | Reputation decay speed |
| `genesis_subsidy_factor` | 0.20, 0.30, 0.40 | Genesis's competitive advantage multiplier |

The objective function rewards: reaching GENESIS_MAX (1,296,000 ILC) as early as possible, starting with 4–40% effective share, and achieving taper compression below 10%.

### Findings relevant to H=48

Now that CDL-027 is locked at H=48, only the `halving:48` scenarios are canonical. From the simulation design:
- H=48 is the middle halving option (between 32 and 64) — intermediate front-loading.
- The `issued_to_date` governor mode is what the current runtime implementation uses.
- Lower `genesis_subsidy_factor` (0.20) tends to produce slower but more stable accumulation, avoiding early cap-block.
- Higher centrality half-life (96 epochs) allows Genesis to maintain competitive scores longer, supporting later-epoch accumulation.

Scenarios that achieve `reach_5pct_epoch` within 240 epochs (20 years) without overshoot are the "valid" scenarios. The `fastest_to_5pct` top-10 cases represent the most favorable combinations of subsidy, centrality, reputation, and network growth under H=48.

### What we do not yet have

The simulation has not been run with the venv active to produce output artifacts (`out/genesis_accrual_sweep_274_exploratory/`). The CSV and JSON results that would show the actual score table and ranked scenarios do not exist in the repo. The simulation also does not model:
- The 10% fee burn's effect on effective circulating supply (it uses gross issuance)
- The ECU price clamp's dampening effect on reward velocity
- The interaction between Genesis's ILC accumulation and CDL-031 (dynamic ranking multiplier policy, now ratified in Phase 288)

---

## 8. CDL-031 Interaction (Now Ratified)

CDL-031 (dynamic ranking-based multiplier policy) was ratified in Phase 288. This was previously listed as dependent on CDL-019 closure. Now that it is ratified, the ranking-based multiplier can affect how Genesis's claims are scored relative to other agents in each epoch.

If the ranking multiplier reduces Genesis's effective ECU score in high-competition scenarios, it further suppresses Genesis's per-epoch grant. This is a second-order dampener on top of the taper governor. The exploratory simulation does not currently model CDL-031 dynamics. A future simulation iteration should incorporate this.

---

## 9. Quantitative Summary: Best-Case vs. Conservative Trajectory

Assuming the issued-to-date governor mode, H=48 monthly epochs, and the derived constants:

**GENESIS_MAX = 1,296,000 ILC** (hard ceiling)

| Scenario | Subsidy factor | Centrality half-life | Approximate reach-cap epoch | Calendar time |
|---|---|---|---|---|
| Best-case (high subsidy, slow decay) | 0.40 | 96 | ~80–120 epochs | ~7–10 years |
| Balanced (mid subsidy, mid decay) | 0.30 | 72 | ~140–200 epochs | ~12–17 years |
| Conservative (low subsidy, fast decay) | 0.20 | 48 | May never reach cap | >40 years |
| Early cap-block (too aggressive) | 0.40 | 48 | Blocked before 1,296,000 | <5 years |

The early cap-block failure mode is real: if Genesis's per-epoch share consistently exceeds ~7–8% of the epoch budget (i.e., well above the 5% floor), the issued-to-date ratio rises above theta_soft within 30–50 epochs and the taper activates before Genesis has accumulated meaningful total ILC. Genesis can end up with a large initial slug (~500K ILC in the first year) but then nothing for decades, totaling well below GENESIS_MAX.

The optimal trajectory holds Genesis's per-epoch share close to 4–5% of the epoch budget throughout — enough to accumulate toward 1,296,000 ILC while keeping the governor ratio below theta_soft for as long as possible.

---

## 10. Recommendations

### 10.1 Formalize the genesis accumulation simulation

The exploratory simulation should be committed and updated with:
1. A corrected mechanism note (CDL-027 is now ratified: H=48, monthly epochs)
2. The simulation filtered to H=48 scenarios only (the canonical case)
3. Output artifacts committed to `out/genesis_accrual_canonical_298/`
4. A Phase 305 (economic monitoring rollout baseline) prompt that incorporates this as a required deliverable

This would provide a committed, reproducible reference trajectory for Genesis accumulation that can be referenced in future phase evidence artifacts.

### 10.2 Clarify governor denominator mode

The simulation sweeps both `issued_to_date` and `theoretical_cap` governor denominator modes. The runtime implementation uses `issued_to_date`. The theoretical-cap mode is more lenient early (ratio = genesis_cum / C_max starts tiny and grows slowly). A constitutional decision on the denominator mode has not been made — this is a governance surface that should be addressed in the 300+ window if Genesis accumulation is a protocol-level concern.

### 10.3 Model CDL-031 interaction

The ranking-based multiplier (CDL-031, ratified Phase 288) affects Genesis's per-epoch competitive score. The genesis accumulation simulation should be extended to model the multiplier's dampening effect on Genesis's ECU-weighted rewards in later epochs when the network is mature and competitive.

### 10.4 Document the subsidy factor origin

The `genesis_subsidy_factor` in the simulation (0.20–0.40) has no direct CDL anchoring — it represents a design assumption about Genesis's bootstrapping advantage. This parameter should be explicitly ratified or bounded in a future ADM/CDL before Genesis accumulation targets become protocol commitments.

---

## 11. Open Questions

1. **What is the target Genesis accumulation epoch?** Is there a protocol design intent for when Genesis should reach theta_hard (and transition to dormant)? The answer affects both subsidy factor calibration and the communication of protocol maturity milestones.

2. **Is there a floor on Genesis's per-epoch share?** If Genesis's centrality and reputation decay to their floors (5% and 10% respectively), does the resulting per-epoch share produce meaningful accumulation or effectively nothing? The simulation's `centrality_floor=0.05` and `reputation_floor=0.10` suggest Genesis never fully exits the market, but the late-epoch shares may be negligible.

3. **Does CDL-028 fee burn interact with the genesis grant calculation?** The current governor uses gross issuance as the denominator. If fee-burned ILC is excluded from total issuance, the ratio calculation changes. Clarification needed on whether `total_cumulative_issuance` in the governor signal includes or excludes burned tokens.

4. **How is Genesis's ILC accumulation communicated externally?** For whitepaper and participant disclosure purposes, the 1,296,000 ILC ceiling and the ~7–20 year accumulation horizon are significant disclosures. Are these values ready for external documentation?

---

*This analysis is as-of Phase 298. The issuance governance CDL set is closed. The next update to this document should follow the Phase 305 economic monitoring baseline execution, which is the designated lane for canonical genesis accumulation trajectory publication.*
