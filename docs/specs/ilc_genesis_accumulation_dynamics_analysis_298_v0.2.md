# ILC Genesis Agent Accumulation Dynamics Analysis
**Version**: v0.2  
**Date**: 2026-02-24  
**Author**: Codex (remediation pass after Sonnet review handoff)  
**Status**: Canon-safe correction of v0.1

---

## 1. Scope and correction intent

This v0.2 replaces v0.1 as the review-safe reference for Genesis accumulation dynamics.

Primary correction goals:
1. Separate **ratified constants** from **unratified simulation assumptions**.
2. Separate **implemented runtime/conformance behavior** from **exploratory projected trajectories**.
3. Remove numeric timeline claims that are not currently grounded in committed, canonical artifacts.

---

## 2. Ratified issuance-governance constants (verified)

| Parameter | Value | Anchor |
|---|---|---|
| Allocation split (performer / auditor / genesis) | `80 / 15 / 5` | `CDL-029` ratified (Phase 272) |
| `theta_hard` continuity target | `1/20 = 0.05` | `CDL-029` evidence continuity |
| `C_max` | `25,920,000 ILC` | `CDL-026` ratified (Phase 273) |
| Decay schedule | `halving`, `H=48`, monthly epochs | `CDL-027` ratified (Phase 276) |
| Fee-burn split | `10%` | `CDL-028` ratified (Phase 274) |
| ECU clamp | `P_min=0.75`, `P_max=1.30` | `CDL-030` ratified (Phase 277) |
| Terminal issuance model | `Model B` (fee-funded tail) | `CDL-025` ratified (Phase 267) |
| Dynamic ranking multiplier policy | ratified | `CDL-031` ratified (Phase 288) |

Reference: `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

Note on derived quantity:
- `0.05 * 25,920,000 = 1,296,000` is a derived arithmetic value from ratified constants.
- This derived value is **not itself a separately implemented runtime clamp in `ilc_core/analysis/genesis_accrual_governor.py`**.

---

## 3. Implemented canonical control surface (what exists in code)

Implemented module:
- `ilc_core/analysis/genesis_accrual_governor.py`

Implemented behavior:
- Computes share ratio: `ratio = genesis_cumulative_accrual / total_cumulative_issuance`.
- Computes taper multiplier from sigmoid around `theta_soft = exp(-3)` with steepness `40.0`.
- Returns taper `0.0` when `ratio >= theta_hard` at evaluation time.

Important boundary:
- This module is a **governor/conformance surface**, not a full issuance execution engine.
- It does not independently simulate epoch budgets, centrality decay, reputation decay, network growth, or subsidy policies.
- It does not include an explicit persistent "latch" that permanently disables future accrual independent of future ratio inputs.

---

## 4. Non-canonical assumptions previously mixed into v0.1

The following are design/simulation assumptions and should not be presented as currently active protocol runtime behavior:
- `genesis_subsidy_factor` (explicitly marked designed/not ratified in context capsules).
- Centrality/reputation decay curves as direct drivers of Genesis per-epoch grant.
- Claims of a canonical fixed wall-clock timeline such as "~7–20 years to 5%".

These assumptions may still be useful for exploratory analysis but require explicit lane-level ratification/implementation before being treated as protocol behavior.

---

## 5. Exploratory simulation status (non-canonical)

Exploratory file:
- `simulations/sim_genesis_accrual_centrality_reputation_sweep_274_exploratory.py`

Current status:
- Untracked/uncommitted in git as of this review.
- Mechanism note in file output remains stale regarding CDL-027 openness.
- Parameter sweep dimensions currently produce `26,244` scenarios (not `2,916`).
- Local output directory exists in working tree (`out/genesis_accrual_sweep_274_exploratory/`) but is not canonical source-of-truth for governance claims.

Interpretation rule:
- Treat this simulation as exploratory evidence only until a dedicated phase locks a committed script + deterministic outputs + tests + handoff artifact.

---

## 6. What we can safely claim today

Safe claims:
1. The issuance governance constants listed in Section 2 are ratified.
2. Genesis-share governor constants and taper behavior are implemented as a conformance/governor surface.
3. The system has a ratified target structure for issuance + clamp + burn + allocation.

Not safe to claim yet:
1. A canonical wall-clock timeline for Genesis reaching any derived cap value.
2. Canonical per-epoch Genesis overperformance dynamics from centrality/reputation/subsidy assumptions.
3. Economic-path predictions that require coupling unratified assumptions with uncommitted exploratory simulation output.

---

## 7. Required closure work before external/canonical trajectory claims

1. Commit a canonical Genesis-trajectory simulation lane with deterministic seed control and locked dependencies.
2. Restrict that lane to ratified schedule/clamp/burn anchors unless explicitly modeling alternative hypotheses.
3. Add explicit tests for scenario-count determinism and output-hash reproducibility.
4. Publish committed output artifacts and a phase handoff that states exactly which assumptions are active vs exploratory.
5. Decide whether denominator-mode alternatives are purely exploratory or require constitutional classification.

Recommended target lane: the planned economic monitoring rollout lane (Phase 305 track).
Execution checklist anchor: `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`.

---

## 8. Open governance/architecture questions

1. Should Genesis trajectory monitoring remain a pure conformance signal, or become a runtime execution policy surface?
2. If subsidy/decay assumptions are desired as protocol behavior, which ADM/CDL lane will formally bind them?
3. Should external-facing whitepaper language include derived values (`1,296,000`) now, or only after trajectory simulation is canonized?

---

## 9. Supersession note

This file supersedes interpretive portions of:
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.1.md`

v0.1 remains useful as historical draft context but should not be used as canonical policy analysis without the corrections captured here.
