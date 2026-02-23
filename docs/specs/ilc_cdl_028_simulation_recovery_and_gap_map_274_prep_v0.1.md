# ILC CDL-028 Simulation Recovery and Gap Map 274 Prep v0.1

Status: Pre-ratification evidence artifact (non-ratifying)
Date: 2026-02-23
Scope: Recover historical simulation provenance and map evidence gaps before CDL-028 ratification.

## 1. Purpose

This artifact documents:
- where historically referenced Python simulation work lives in `Z_Past_Chats`,
- which scripts were recovered verbatim into the repo for provenance,
- what evidence those scripts can and cannot provide for `CDL-028` (fee-burn split),
- what additional simulation work is required before Phase 274 ratification.

This artifact does not ratify any CDL and does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

## 2. Historical simulation provenance recovered

Primary historical source:
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt`

Recovered code blocks and repo copies:
1. Controller telemetry simulation (80 epochs)
   - Source lines: `6134-6389`
   - Recovered file: `simulations/historical_recovered/sim_controller_telemetry_80_epoch_recovered_20251009.py`
2. kappa_s A/B simulation (normal + stressed, 120 epochs)
   - Source lines: `6998-7198`
   - Recovered file: `simulations/historical_recovered/sim_kappa_ab_recovered_20251009.py`

Additional historical fee-burn policy context (scenario framing, not code):
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:19890-19926`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20110-20230`

Existing simulation artifacts already in repo and referenced for lineage:
- `simulations/sim_burn_pb_grid.py`
- `simulations/sim_macro_econ_abcd.py`
- `simulations/sim_econ_scenarios_demo.py`
- `out/phase_64e/burn_pb_grid.csv`
- `out/phase_64d/macro_econ_scenarios.csv`

## 3. Coverage against Phase-256 modeling requirements

Reference requirement set:
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md` section 4.

Coverage assessment:
1. Long-horizon issuance sustainability across terminal model variants
   - Status: partial
   - Why: existing scripts show short to medium horizon sweeps and directional accounting; they do not yet provide a canonical long-horizon Model-A/B/C comparison package with fixed acceptance thresholds.
2. Cap sensitivity and emission-curve scenario sweeps
   - Status: missing for CDL-028 lane
   - Why: cap and decay coupling is represented in issuance planning docs, but no dedicated simulation bundle currently ties cap-sensitivity outputs to fee-burn selection.
3. Fee-burn split incentive impact under adversarial usage
   - Status: partial
   - Why: historical scenario comparisons and grid outputs exist, but not yet as a locked adversarial test harness with explicit objective criteria for ratification.
4. Allocation split resilience checks against concentration and gaming
   - Status: mostly addressed in prior lanes (`CDL-029`), but indirect for CDL-028
   - Why: allocation evidence exists, but interaction effects with fee-burn variants are not yet locked as a composed evidence package.
5. Clamp-bound stability tests under volatile reward demand
   - Status: missing for direct CDL-028 decision support
   - Why: clamp work is deferred downstream (`CDL-030`), and no current artifact quantifies fee-burn choice impact on clamp-bound behavior under volatility.

## 4. Additional evidence gaps discovered

Beyond the five Phase-256 bullets, two practical evidence gaps remain before a defensible `CDL-028` lock:
- Objective function gap: no canonical, pre-locked scoring function for choosing among fee-burn candidates (for example: runway floor, incorrect-final bound, and issuance sustainability target in one weighted decision rule).
- Reproducibility contract gap: no single ratification-prep script currently emits a deterministic candidate-ranking table with fixed seed, scenario matrix, and explicit winner declaration for CDL-028.

## 5. Pre-ratification evidence step required

Before executing the sensitive Phase 274 ratification lane, add a non-sensitive evidence phase that:
- adapts recovered simulation lineage into one canonical fee-burn candidate sweep harness,
- pins deterministic seed(s), scenario matrix, and evaluation metrics,
- produces a candidate-ranking output artifact and recommendation,
- adds tests that verify artifact presence, deterministic rerun behavior, and declared selected candidate.

Required output class for that phase:
- one evidence closure artifact for CDL-028 candidate selection,
- one simulation output table (CSV),
- one test file asserting deterministic structure and selected-candidate token.

## 6. Ratification boundary

`CDL-028` should remain `open` until the pre-ratification evidence step above is complete and referenced as an entry criterion in the Phase 274 prompt.

