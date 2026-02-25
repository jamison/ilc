# ILC Phase 305 Genesis Accumulation Canonicalization Checklist v0.1

Status: Planning checklist artifact  
Date: 2026-02-24  
Target lane: Phase 305 economic monitoring rollout baseline

## 1. Purpose

Provide a concrete execution checklist so Phase 305 can convert Genesis accumulation analysis from exploratory context into canonical, reproducible evidence.

## 2. Canonical baseline (must stay fixed)

Use only ratified/implemented anchors unless explicitly marked exploratory:
- `CDL-025` terminal model (Model B)
- `CDL-026` `C_max = 25,920,000`
- `CDL-027` `halving`, `H=48`, monthly epochs
- `CDL-028` fee-burn `10%`
- `CDL-029` allocation split continuity `80/15/5` with `theta_hard = 1/20`
- `CDL-030` clamp bounds `P_min=0.75`, `P_max=1.30`
- `CDL-031` ranking policy ratified state
- implemented governor constants from `ilc_core/analysis/genesis_accrual_governor.py`

## 3. Required Phase 305 outputs

1. **Canonical simulation script**
   - committed script path (no untracked local-only dependency)
   - deterministic seed contract documented
   - explicit denominator mode handling documented (`issued_to_date` vs `theoretical_cap`)

2. **Reproducible output package**
   - canonical summary artifact under `docs/specs/`
   - deterministic machine-readable output(s) with hash manifest
   - if full CSV is too large, include compact canonical slice + reproducibility hash proof

3. **Contract tests**
   - deterministic re-run hash equality test
   - scenario-count and parameter-grid lock test
   - mode-label coverage test for all projections
   - check that canonical section contains no unratified assumptions

4. **Walkthrough + STATUS update**
   - exact commands executed
   - output hashes recorded
   - explicit statement of what remains exploratory

## 4. Mandatory analysis sections in Phase 305 artifact

- Canonical constants table (ratified + implemented only)
- Derived arithmetic section (e.g., H=48 issuance schedule math)
- Mode-qualified trajectory table (`issued_to_date` and `theoretical_cap` separated)
- Assumption registry (ratified vs exploratory)
- External-communication-safe claims section
- Residual open questions and governance follow-ups

## 5. Governance and boundary rules

- Do not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md` in this lane unless explicitly scoped by prompt.
- Do not present exploratory assumptions as active protocol behavior.
- Do not publish a single timeline claim without denominator-mode label.
- Keep `v0.2`/`v0.3` supersession chain explicit.

## 6. Waypoint checklist before entering Phase 305

- [ ] Confirm `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.2.md` remains canonical fallback.
- [ ] Confirm `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md` is marked pre-305 draft context.
- [ ] Promote exploratory script into a committed canonical script path or create a new committed script.
- [ ] Define output retention policy (full data vs compact canonical package + hash evidence).
- [ ] Predeclare test contract in Phase 305 prompt (determinism + mode separation + assumption labeling).

## 7. Carry-forward references

- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.2.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`
- `docs/specs/ilc_economic_risk_monitoring_contract_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
