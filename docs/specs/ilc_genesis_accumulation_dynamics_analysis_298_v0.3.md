# ILC Genesis Agent Accumulation Dynamics Analysis
**Version**: v0.3  
**Date**: 2026-02-24  
**Author**: Codex (hybrid correction after Sonnet pushback)  
**Status**: Pre-Phase-305 draft (canon-safe + quantitative context)

---

## Executive Summary

This v0.3 keeps v0.2's correctness boundaries and restores quantitative planning signal.

Two lenses are intentionally separated:

1. **Canonical protocol lens** (ratified + implemented):
   - Issuance governance constants are ratified (`CDL-025/026/027/028/029/030/031`).
   - Genesis accrual governor surface is implemented with `theta_hard = 1/20`, `theta_soft = exp(-3)`, and steepness `40.0`.

2. **Exploratory trajectory lens** (simulation assumptions):
   - Local exploratory sweep shows materially different behavior by denominator mode.
   - Under `theoretical_cap` mode with `H=48`, 5% is reached quickly (p50 ~23 epochs).
   - Under `issued_to_date` mode with the current exploratory share assumptions, 5% is not reached within the 480-epoch horizon.

The key governance point is not "no signal"; it is **mode sensitivity + assumption sensitivity**. Trajectory statements must stay mode-qualified until a canonical simulation lane is phase-locked.

---

## 1. Evidence classification

- **[Canonical]** Ratified constants and decision-log state.
- **[Canonical]** Implemented governor semantics in `ilc_core/analysis/genesis_accrual_governor.py`.
- **[Derived]** Math from ratified constants (e.g., `0.05 * C_max`).
- **[Exploratory]** Uncommitted simulation script and local output files.
- **[Open]** Any parameter or policy not formally ratified/implemented.

---

## 2. Canonical constants and anchors

| Parameter | Value | Class | Anchor |
|---|---|---|---|
| Allocation split | `80 / 15 / 5` | Canonical | `CDL-029` |
| `theta_hard` continuity | `1/20 = 0.05` | Canonical | `CDL-029` evidence continuity |
| `C_max` | `25,920,000 ILC` | Canonical | `CDL-026` |
| Decay schedule | `halving`, `H=48`, monthly epochs | Canonical | `CDL-027` |
| Fee-burn | `10%` | Canonical | `CDL-028` |
| ECU clamp | `P_min=0.75`, `P_max=1.30` | Canonical | `CDL-030` |
| Terminal issuance model | Model B (fee-funded tail) | Canonical | `CDL-025` |
| Dynamic ranking multiplier policy | ratified | Canonical | `CDL-031` |
| `theta_soft` | `exp(-3) ~= 0.049787` | Canonical (impl constant) | governor code |
| Taper steepness | `40.0` | Canonical (impl constant) | governor code |

**Derived constant:**
- **[Derived]** `GENESIS_DERIVED_5PCT = 0.05 * 25,920,000 = 1,296,000 ILC`.

---

## 3. Canonical runtime/conformance behavior

Implemented in `ilc_core/analysis/genesis_accrual_governor.py`:

- **[Canonical]** Share ratio: `ratio = genesis_cumulative_accrual / total_cumulative_issuance`.
- **[Canonical]** Taper function: sigmoid around `theta_soft` with steepness `40.0`.
- **[Canonical]** Current-step hard stop: `taper = 0` when `ratio >= theta_hard`.

Important nuance:
- The module is a governor/conformance surface, not a full issuance execution engine.
- It does not directly implement centrality/reputation/subsidy dynamics.
- It does not add an independent persistent-latch state in this module; gating is evaluated from current ratio input each step.

---

## 4. Derived issuance schedule profile (H=48, monthly)

Using ratified `C_max = 25,920,000`, halving `H=48`, and 480 epochs:

- **[Derived]** `q = 2^(-1/48) ~= 0.985663`
- **[Derived]** geometric sum over 480 epochs `~= 69.68245`
- **[Derived]** epoch-0 budget `b0 ~= 371,973 ILC`

Selected checkpoints:

| Epoch | Approx budget (ILC/epoch) | Cumulative issued fraction |
|---:|---:|---:|
| 0 | 371,973 | - |
| 48 | 185,987 | 50.05% |
| 96 | 92,993 | 75.07% |
| 144 | 46,497 | 87.59% |
| 192 | 23,248 | 93.84% |
| 240 | 11,624 | 96.97% |

Interpretation:
- **[Derived]** This is front-loaded issuance in the first decade under monthly epochs.

---

## 5. Exploratory simulation readout (mode-qualified)

Exploratory assets (not canonical):
- Script: `simulations/sim_genesis_accrual_centrality_reputation_sweep_274_exploratory.py` (tracked exploratory artifact; not a canonical policy surface).
- Local outputs: `out/genesis_accrual_sweep_274_exploratory/*.csv|*.json` (working-tree local evidence only).

Observed sweep size:
- **[Exploratory]** 26,244 scenarios (not 2,916).

### 5.1 H=48 only, by denominator mode

| Mode | H=48 scenarios | Reach 5% within 480 epochs | Reach epoch p50 (if reached) | Cap-block first-epoch signal | Final Genesis cumulative (p50) |
|---|---:|---:|---:|---:|---:|
| `issued_to_date` | 2,187 | 0 / 2,187 | n/a | epoch 1 in all scenarios | ~1,231,096 ILC |
| `theoretical_cap` | 2,187 | 2,187 / 2,187 | 23 | epoch 24 (p50) | 1,296,000 ILC |

### 5.2 H=48 wall-clock intuition under monthly epochs

- **[Exploratory, theoretical_cap mode]**
  - p10 reach: ~16 months
  - p50 reach: ~23 months
  - p90 reach: ~45 months

- **[Exploratory, issued_to_date mode with current share assumptions]**
  - no scenario reaches the derived 5% target within 480 months.

Interpretation:
- The denominator choice is first-order material.
- Claims like "reaches 5% in ~X years" must be explicitly denominator-qualified.

---

## 6. What v0.1 got right vs wrong

### Retained from v0.1
- Correct ratified parameter set and anchor references.
- Correct statement that exploratory simulation is stale/uncommitted and needs canonicalization.
- Correctly identifies front-loaded issuance under H=48.

### Corrected from v0.1
- Removed unqualified trajectory table as if it were canonical runtime truth.
- Corrected scenario-count claim (26,244 in current script dimensions).
- Reframed "permanent block" language into current-step gating semantics within the implemented governor surface.
- Split fixed-ratified statements from unratified simulation assumptions.

---

## 7. Open issues that remain real

1. **[Open] Denominator mode constitutionalization**
   - The exploratory lane compares `issued_to_date` vs `theoretical_cap`, but canonical lane binding for trajectory projection is not yet settled in a dedicated governance artifact.

2. **[Open] Subsidy/centrality/reputation dynamics as protocol policy**
   - `genesis_subsidy_factor` and related decay assumptions are not ratified protocol constants.

3. **[Open] Canonical simulation lane**
   - No committed, deterministic, phase-locked trajectory artifact yet ties all ratified constants into one governance-grade projection set.

---

## 8. Recommended next actions (Phase 305-oriented)

1. Commit a canonical simulation script variant with fixed dependency inputs and deterministic seed policy.
2. Emit committed CSV/JSON outputs with hash-locked reproducibility tests.
3. Publish a short artifact explicitly labeling each reported metric as Canonical/Derived/Exploratory.
4. Add a governance note that any external timeline claim must include denominator mode and assumption set.
5. Execute checklist: `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`.

---

## 9. Supersession note

- v0.3 supersedes interpretive use of:
  - `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.1.md`
  - `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.2.md`

v0.1 and v0.2 remain historical context records.
