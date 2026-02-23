# ILC Economic Risk Monitoring Contract v0.1

Status: Draft operational contract (non-ratifying)
Date: 2026-02-23
Owner lane: G8 economic governance

## 1. Purpose

Define a minimal, enforceable monitoring contract so economic risk control is not left as prose.

This contract defines:
- what is monitored,
- how often it is measured,
- escalation thresholds,
- required response actions,
- complexity guardrails.

Boundary:
- no decision-log mutation,
- no runtime policy-value ratification,
- no direct `ilc_core/` behavior change in this artifact.

## 2. Monitoring planes

The following six planes are mandatory:

1. **Protocol invariants**
   - signer lineage validity,
   - rollback/supersession integrity,
   - fail-closed contract behavior.

2. **Economic invariants**
   - issuance path conformance,
   - clamp stability,
   - concentration drift,
   - security-budget sufficiency.

3. **Governance hygiene**
   - mutation-scope adherence,
   - evidence chain completeness,
   - non-target CDL row immutability.

4. **Operational resilience**
   - custody/liquidity counterparty exposure,
   - withdrawal/freeze contingency readiness,
   - incident recovery runbook readiness.

5. **Adoption utility**
   - productive usage throughput,
   - dispute-resolution quality,
   - retention in non-speculative workflows.

6. **Narrative integrity**
   - utility-first positioning adherence,
   - prohibited macro-hedge claims,
   - anti-pyramid/anti-reflexivity communication checks.

## 3. Core KPI set (v0.1)

Each KPI must be computed at least once per epoch and summarized per release window.

### 3.1 Protocol invariants KPIs
- `kpi_invalid_lineage_events` (count, target `0`)
- `kpi_unauthorized_supersession_rejects` (count, informational + trend)
- `kpi_fail_closed_violation_count` (count, target `0`)

### 3.2 Economic invariants KPIs
- `kpi_issuance_schedule_deviation` (absolute deviation from selected schedule path)
- `kpi_clamp_violation_count` (`P_min`/`P_max` outside events)
- `kpi_genesis_share_ratio` (must stay `<= 0.05`)
- `kpi_top10_share_ratio` (concentration signal)

### 3.3 Governance hygiene KPIs
- `kpi_out_of_scope_row_mutations` (count, target `0`)
- `kpi_missing_evidence_anchor_count` (count, target `0`)
- `kpi_phase_guard_failures` (count by phase)

### 3.4 Operational resilience KPIs
- `kpi_custodial_dependency_ratio` (share of activity requiring centralized custody)
- `kpi_withdrawal_failure_events` (count)
- `kpi_runbook_last_drill_days` (days since last drill)

### 3.5 Adoption utility KPIs
- `kpi_productive_action_ratio` (productive actions / total actions)
- `kpi_dispute_close_rate` (resolved disputes / opened disputes)
- `kpi_median_time_to_resolution` (duration)

### 3.6 Narrative integrity KPIs
- `kpi_macro_hedge_claim_incidents` (count in official docs/prompts)
- `kpi_price_only_kpi_incidents` (count)
- `kpi_utility_anchor_coverage` (share of public artifacts with utility framing)

## 4. Complexity guardrail (new mandatory check)

All new economic/governance proposals must include:

1. **Necessity test**
   - What concrete risk or failure mode is solved?
   - What is the measured baseline showing this problem exists?

2. **Simpler-alternative test**
   - At least one simpler alternative must be documented and rejected with reason.

3. **Complexity budget score**
   - `n_new_params` (new tunable parameters introduced),
   - `n_new_conditionals` (new policy branch points),
   - `n_new_cross_dependencies` (new lane coupling edges).

4. **Complexity decision rule**
   - If any of the following is true, explicit review is required before adoption:
     - `n_new_params > 2`,
     - `n_new_conditionals > 2`,
     - `n_new_cross_dependencies > 1`.

## 5. Alert thresholds and severity

Severity levels:
- `S0`: informational
- `S1`: warning
- `S2`: elevated risk
- `S3`: release-blocking

Default hard thresholds:
- `kpi_out_of_scope_row_mutations > 0` -> `S3`
- `kpi_fail_closed_violation_count > 0` -> `S3`
- `kpi_genesis_share_ratio > 0.05` -> `S3`
- `kpi_clamp_violation_count > 0` for two consecutive epochs -> `S2`
- `kpi_productive_action_ratio` sustained decline over three epochs -> `S2`
- `kpi_macro_hedge_claim_incidents > 0` -> `S1` (escalate to `S2` if repeated)

## 6. Cadence and reporting contract

Required cadence:
- **per-epoch**: machine-readable KPI snapshot,
- **per-phase (governance lane)**: include KPI summary deltas in walkthrough,
- **per-window (e.g., 270-279)**: consolidated monitoring report.

Artifact contract:
- `out/monitoring/economic_risk_snapshot_<epoch>.json`
- `docs/specs/ilc_economic_risk_monitoring_report_<window>_v0.1.md`

## 7. Response playbook by effort class

### 7.1 Immediate / easy actions (do now)
- Add KPI section template to evidence-closure artifacts (starting Phase 275).
- Enforce non-target mutation checks in all ratification tests.
- Add explicit utility-first and non-macro-hedge language checks in governance docs.

### 7.2 Medium actions (next 1-3 phases)
- Add a deterministic monitoring report for the 270-279 window.
- Add custody/liquidity exposure fields to operational walkthroughs.
- Add complexity budget table to sensitive prompts before GO.

### 7.3 High / hard actions (schedule, not ad hoc)
- Build simulated exchange-freeze / leverage-cascade stress pack.
- Build correlation-regime stress scenarios (financialization risk).
- Add long-horizon concentration and agent-centralization monitoring pipeline.

## 8. Phase mapping and scheduling

Current window mapping:
- Phase 275: include `A/B/C` option evidence plus initial KPI/complexity tables (non-ratifying).
- Phase 276-277: apply thresholds to sensitive ratification evidence and tests.
- Phase 278-279: publish first consolidated monitoring report and handoff notes.

Deferred mapping:
- Post-279 window: implement hard stress-pack simulations and telemetry automation.

## 9. Non-goals

This contract does not:
- set final ratified economic constants,
- replace CDL ratification process,
- force immediate runtime implementation in `ilc_core/`.
