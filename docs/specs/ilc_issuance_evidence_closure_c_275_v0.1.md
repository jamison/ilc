# ILC Issuance Evidence Closure C 275 v0.1

Status: Non-ratifying evidence artifact
Date: 2026-02-23
Window: Phase 275
Primary lane: `CDL-027` and `CDL-030` evidence closure

## 1. Scope

This artifact closes evidence for:
- `CDL-027` (decay formulation and schedule constants),
- `CDL-030` (ECU price clamp derivation methodology).

Boundary statement:
- non-ratifying,
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no runtime policy activation.

## 2. CDL-027 Decay Formulation Evidence

### 2.1 Inputs and assumptions
- Locked cap baseline: `C_max = 25,920,000` (from `CDL-026` evidence).
- Model continuity anchor: `CDL-025` fee-funded tail / Model B.
- Candidate schedule families reviewed:
  - `halving` (`H` candidates),
  - `exp` (`lambda` candidates).

### 2.2 Evidence summary
- Candidate schedule sweep compared exponential and halving families under locked cap continuity (`C_max = 25,920,000`) and Genesis-cap objective (`5%`).
- Under the selected governance mode (`theoretical_cap` denominator), schedule candidates can be compared in wall-clock terms without breaking the Genesis cap objective.
- Option B (`halving`, `H=48`, monthly epochs) provides the best balance between:
  - early-but-not-abrupt Genesis fade,
  - long-tail issuance continuity,
  - lower concentration pressure than faster front-load candidates.

Sensitivity comments:
- Option A reaches the Genesis cap faster but compresses issuance into a shorter early window.
- Option C extends the tail strongly but slows Genesis fade relative to the "first few years" target.

Tradeoff summary:
- Option A: strongest onboarding impulse, highest concentration/volatility pressure.
- Option B: balanced trajectory and recommended carry-forward.
- Option C: strongest long-tail conservatism, weakest early handoff cadence.

### 2.3 Carry-forward recommendation to Phase 276
Locked carry-forward candidate from Phase 275:
- **Option B**
  - schedule family: `halving`,
  - schedule constant: `H = 48`,
  - epoch duration candidate: `1 month`.

This is a carry-forward recommendation only.
Final ratification remains in sensitive Phase 276 (`CDL-027` lane).

## 3. Epoch Duration Matrix and Policy Options (A/B/C)

Reference source:
- `docs/specs/ilc_epoch_duration_candidate_matrix_and_policy_options_274_fix2_v0.1.md`

### 3.1 Wall-clock conversion matrix

| Candidate | p50 epochs to 5% Genesis cap | p90 epochs to 5% Genesis cap | 1 day epoch (p50/p90 years) | 1 week epoch (p50/p90 years) | 1 month epoch (p50/p90 years) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Option A (`exp`, `lambda=0.030`) | 10 | 18 | 0.03 / 0.05 | 0.19 / 0.35 | 0.82 / 1.48 |
| Option B (`halving`, `H=48`) | 23 | 45 | 0.06 / 0.12 | 0.44 / 0.86 | 1.89 / 3.70 |
| Option C (`halving`, `H=64`) | 31 | 71 | 0.08 / 0.19 | 0.59 / 1.36 | 2.55 / 5.84 |

### 3.2 Option comparison summary

#### Option A
- Pros: fastest Genesis-cap convergence; strongest early participation incentives.
- Risks: steeper early issuance compression; higher concentration and volatility pressure.

#### Option B (selected carry-forward)
- Balanced handoff rationale: reaches Genesis cap in a "first few years" envelope under monthly epochs without extreme front-loading.
- Long-tail rationale: preserves a materially longer issuance tail than Option A, supporting medium/long-horizon incentive continuity.

#### Option C
- Conservative-long-tail rationale: strongest smoothing and longest tail among the three candidates.
- Drawback: slowest Genesis fade timeline and weakest early-transition cadence.

### 3.3 Selection statement

Phase 275 selects **Option B** as the only carry-forward candidate to Phase 276:
- `halving`, `H=48`, `1 month` epochs.

No schedule constant is ratified in this phase.

## 4. Practical Risk Controls Carry-Forward

Reference source:
- `docs/specs/ilc_economic_risk_monitoring_contract_v0.1.md`

Required carry-forward controls:

1. **No macro-hedge claim boundary**
   - This lane must not claim ILC as an inflation hedge, macro hedge, or decoupled safe-haven asset.
   - Economic positioning remains utility-first: verified work, dispute quality, and protocol throughput.

2. **Custody/liquidity resilience carry-forward**
   - Evidence must preserve the requirement for direct-signing/self-custody-first operational paths where possible.
   - Centralized-custody dependency and withdrawal-freeze exposure remain monitored risk surfaces.

3. **Anti-leverage/reflexivity control note**
   - This lane must not introduce debt-funded reflexive treasury assumptions into issuance policy claims.
   - Any leverage-dependent growth claims are out of scope and must be explicitly excluded.

4. **Utility-first KPI requirement**
   - Carry-forward monitoring must prioritize productive-use KPIs over price-led KPIs:
     - productive action ratio,
     - dispute close rate and median resolution time,
     - protocol-invariant violation counts.

## 5. CDL-030 Derivation Methodology

### 5.1 Objective
Define derivation logic for `P_min` and `P_max` from the selected `CDL-027` schedule family.

### 5.2 Method outline

Derivation structure (non-ratifying in this phase):

1. Build epoch issuance path from carry-forward schedule candidate:
   - `E_e` from `halving(H=48)` with monthly epochs.
2. Compute cumulative path and expected per-epoch available issuance budget.
3. Define provisional clamp envelope as a function of:
   - schedule-derived issuance pressure,
   - ECU-denominated demand proxy,
   - guardrail floors/ceilings to prevent abrupt step changes.
4. Evaluate clamp-behavior stability under:
   - low/medium/high volatility scenarios,
   - demand spikes,
   - prolonged low-demand windows.
5. Produce candidate derivation package for Phase 277 ratification without mutating decision-log state.

Required inputs:
- `CDL-027` carry-forward candidate (Option B),
- locked cap baseline (`C_max`),
- fee-burn continuity context (`CDL-028` lane),
- volatility scenario set (low/medium/high).

Expected validation tests:
- monotonicity and bound-respect checks,
- no negative/invalid clamp outputs,
- stress-case convergence and no oscillatory runaway behavior,
- reproducibility under deterministic seeds.

### 5.3 Boundary
`P_min`/`P_max` values are not ratified in Phase 275.
Ratification remains in sensitive Phase 277 (`CDL-030` lane).

## 6. Non-goals

This artifact does not:
- ratify `CDL-027`,
- ratify `CDL-030`,
- modify decision-log rows,
- introduce runtime behavior changes in `ilc_core/`.

## 7. Canonical Anchors

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
- `docs/specs/ilc_issuance_governance_activation_survey_247_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md`
- `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md`
- `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- `docs/specs/ilc_epoch_duration_candidate_matrix_and_policy_options_274_fix2_v0.1.md`
- `docs/specs/ilc_economic_risk_monitoring_contract_v0.1.md`
