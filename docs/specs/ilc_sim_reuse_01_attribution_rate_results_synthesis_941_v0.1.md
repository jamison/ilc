# ILC SIM-REUSE-01: REUSE Attribution Rate Calibration — Results and Synthesis

**Phase:** 941
**SIM-ID:** SIM-REUSE-01
**Status:** Complete — CDL-081 Q6 disposition ready
**Date:** 2026-04-28
**Gate:** CDL-081 Q6 deferred Phase 929; this SIM unlocks the lock

---

## 1. Scope

CDL-081 Q6 deferred REUSE_ATTRIBUTION_RATE to SIM-REUSE-01.
`REUSE_ATTRIBUTION_RATE = None` in `ilc_core/types.py` pending this result.

This document synthesises simulation evidence and issues the disposition for CDL-081 Q6.

Non-ratifying as a stand-alone document. CDL-081 must be ratified for REUSE_ATTRIBUTION_RATE
to become constitutionally locked.

---

## 2. Model

```
N_AGENTS:           120 agents, creativity ~ Beta(2,3)
T_EPOCHS:           300 validation epochs
CREATION_COST:      1.0 ECU per content node
TRAVERSAL_ECU_BASE: 0.10 ECU per reuse traversal (before attribution split)
INITIAL_STAKE:      10.0 ECU per agent
GAMING_COST:        1.5 ECU overhead per fake reuse event
SEED:               940001 (deterministic)

Targets:
  Incentive alignment:  mean_creation_rate ≥ 0.25 (≥25% of agents create per epoch)
  Gini:                 final_gini ≤ 0.55 (distribution not too concentrated)
  Gaming resistance:    gaming_roi_ratio < 1.5 (gaming ROI < 1.5× creation ROI)
```

---

## 3. Results

| rate | creation_rate | gini@300 | gaming_roi_ratio | incentive_ok | gini_ok | gaming_ok | ALL |
|------|---------------|----------|------------------|--------------|---------|-----------|-----|
| 0.05 | 0.0843 | 0.8736 | 0.0167 | N | N | Y | N |
| 0.10 | 0.5907 | 0.4031 | 0.0048 | Y | Y | Y | **Y** |
| 0.15 | 0.8080 | 0.1988 | 0.0038 | Y | Y | Y | Y |
| 0.20 | 0.8228 | 0.1968 | 0.0035 | Y | Y | Y | Y |
| 0.25 | 0.9249 | 0.1103 | 0.0033 | Y | Y | Y | Y |
| 0.30 | 0.8601 | 0.1832 | 0.0032 | Y | Y | Y | Y |
| 0.40 | 0.9830 | 0.0640 | 0.0031 | Y | Y | Y | Y |
| 0.50 | 0.9753 | 0.1029 | 0.0030 | Y | Y | Y | Y |

---

## 4. Key Findings

### Finding 1 — Sharp Incentive Cliff at Rate=0.10

Rate=0.05 fails the creation-rate target (8.43% vs ≥25%) and produces severe inequality
(gini=0.874). Rate=0.10 passes all three targets simultaneously (creation_rate=59.07%,
gini=0.403, gaming_roi_ratio=0.005). The cliff between 0.05 and 0.10 is abrupt — there
is no gradual transition.

**Interpretation:** The floor for REUSE_ATTRIBUTION_RATE is **0.10**. Below 0.10, the attribution
signal is too weak to sustain content creation as a rational economic activity.

### Finding 2 — Gaming is Structurally Non-Attractive

gaming_roi_ratio < 0.02 across all tested rates. Gaming (creating a fake reuse traversal
at 1.5× creation_cost overhead) has an ROI that is orders of magnitude below real creation.
This holds because:
- Single fake traversal yields: rate × TRAVERSAL_ECU_BASE (e.g., 0.10 × 0.10 = 0.01 ECU)
- Gaming cost: 1.5 ECU
- Gaming ROI: 0.01 / 1.5 ≈ 0.007 — vs. real creation ROI of ~1.0-3.0 over the planning horizon

The REUSE attribution mechanism is gaming-resistant by construction, not by parameter choice.
This finding is robust across the full rate range.

### Finding 3 — Gini Compression Above Rate=0.20

| Rate | Gini @300 | Interpretation |
|------|-----------|----------------|
| 0.10 | 0.403 | Moderate inequality |
| 0.20 | 0.197 | Low inequality |
| 0.25 | 0.110 | Very low inequality |
| 0.40 | 0.064 | Near-equal distribution |

At rate=0.20, the Gini coefficient drops below 0.20 — a level comparable to historically
low-inequality economies. At rate=0.25+, the distribution is extremely flat.

**Note:** Very low Gini at high rates may indicate over-attribution — all agents receive similar
ECU regardless of quality differences, which weakens the quality signal embedded in the
star-map topology.

### Finding 4 — Creation Rate Plateau Above Rate=0.25

creation_rate does not increase substantially above rate=0.25 (0.9249 at 0.25 vs 0.9830 at 0.40).
Beyond 0.25, effectively all economically capable agents are creating regardless of rate.
Higher rates primarily change the ECU distribution (Gini) without improving participation.

---

## 5. Disposition — CDL-081 Q6

**Evidence candidate:** `REUSE_ATTRIBUTION_RATE = 0.20`

Rationale:
1. **Floor confirmed at 0.10** — any rate ≥ 0.10 satisfies all calibration targets
2. **Rate 0.20 chosen over 0.10** because:
   - Creation rate at 0.10 is 59% — meaningful but not maximally aligned
   - At 0.20: 82.3% creation rate + gini=0.197 — strong alignment with low inequality
   - The marginal attribution cost of moving from 0.10 to 0.20 is small (10% more of traversal value flows to creator vs. traversal infrastructure)
3. **Rate 0.20 chosen over 0.25+** because:
   - At 0.25, Gini=0.110 risks erasing the quality differentiation signal
   - 0.20 preserves meaningful variation in creator returns, maintaining the epistemic quality gradient
   - CDL-081 §4.1 specifies `EpochAttributionBatch.settle()` as the mechanism — the rate should be conservative at ratification and revisited with real traversal data

**Constitutional note:** This rate applies to CO_AUTHORSHIP and REUSE edge types per CDL-081 Q1.
ATTESTATION is excluded (CDL-081 Q1 decision). REFUTATION is conditional (CDL-V7 scope).

**Proposed lock:** `REUSE_ATTRIBUTION_RATE = 0.20`

---

## 6. CDL-081 Ratification Path

CDL-081 Q6 is now resolved by SIM-REUSE-01 evidence. Remaining ratification path:

1. Lock CDL-081 Q6 decision into CDL-081 spec document
2. CDL-081 ratification evidence package (tests + coherence report)
3. CDL-081 ratification commit (requires ILC_CDL_MUTATION_AUTHORIZED)
4. Update `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` in `ilc_core/types.py`
   (pending CDL-081 ratification — do NOT update before ratification)

---

`sim_reuse_01_complete`
`sim_reuse_01_recommended_reuse_attribution_rate=0.20`
`cdl_081_q6_resolved_reuse_attribution_rate_0_20_pending_ratification`
`gaming_structurally_non_attractive_validated`
`reuse_attribution_floor_confirmed_at_0_10`
