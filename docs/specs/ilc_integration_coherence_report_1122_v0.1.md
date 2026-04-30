# ILC Integration Coherence Report — Phase 1122
Window: 1118–1123
Phase: 1122
Date: 2026-04-30
Verdict: coherence_report_1122_verdict=pass

---

## 1. Purpose

Window 1118–1123 executed two independent tracks: FLOAT-KILL-01 runtime security hardening
and SIM-PROVENANCE-01 alpha calibration. This report audits that both tracks are internally
consistent and ready for the Phase 1123 closure gate.

---

## 2. FLOAT-KILL-01 Coverage Table

| Directive | Violation | File | Commit | Verification |
|-----------|-----------|------|--------|--------------|
| Directive 2 | Predictable PRNG dependency in routing/runtime selection surfaces | `ilc_core/network/d2d/spectral_routing_runtime.py`, `ilc_core/economics/rl_agents.py` | `9d51d8a0` | Module tests `62 passed`; scoped regression `180 passed` |
| Directive 3 | API economic amount ingestion allowed non-finite Decimal strings | `ilc_core/server.py` | `d407de44` | API tests include non-finite rejection |
| Directive 3 | Passive ECU attribution returned float | `ilc_core/economics/passive_ecu_attribution_runtime.py` | `d407de44` | Passive ECU tests assert Decimal values |
| Directive 3 | RC economic cycle cast `ecu_estimate_decimal` to float | `ilc_core/rc/economic_cycle_runtime.py` | `d407de44` | RC tests passed |
| Directive 3 | Epoch ledger stored ECU/reward totals as float | `ilc_core/economics/epoch_ledger.py` | `d407de44` | Epoch ledger tests assert Decimal aggregate state |
| Directive 3 | Governance, consensus, agent, onboarding, exception, work-task, and outcome/reward interfaces exposed economic floats | `governance.py`, `engine.py`, `agent.py`, `onboarding.py`, `exceptions.py`, `work_task.py`, `outcome.py`, `reward.py` | `08d94ab9` | Module tests `78 passed`; scoped regression `180 passed` |

FLOAT-KILL-02 was not triggered. The `consensus/engine.py` blast radius stayed within the
Phase 1119 Commit 3 scope.

Sensitive-runtime PRNG result: the active runtime grep excluding explicitly permitted
simulation, analysis, devnet, and benchmark paths returned zero results. The final
sensitive-runtime guardrail passed (`tests/test_sensitive_runtime_coding_taboos.py`:
`1 passed`).

---

## 3. SIM-PROVENANCE-01 Coverage Table

| Item | Run 01 (Phase 1120) | Run 02 (Phase 1121) |
|------|---------------------|---------------------|
| Sweep range | `α=0.30–0.70`, step `0.05` | `α=0.40–0.50`, step `0.01` |
| Seeds | `42` | `42`, `1337`, `2026` |
| `α=0.50` result | failed mint-surface keep rule (`0.2065 > 0.20`) on seed `42`; concentration pass | keep rate `2/3`; seed-marginal; concentration pass `3/3` |
| `α=0.45` result | pass, keep | keep rate `3/3`; recommended |
| Disposition | `α=0.45` SIM recommendation | recommendation confirmed with evidentiary weight |

Run 01 produced the required per-node PROVENANCE descendant count time series. Run 02
confirmed that the current provisional value `α=0.50` is concentration-safe but
seed-marginal under the stricter mint-surface keep rule.

---

## 4. CDL-084 Q-Token Status

| Q | Token | Status |
|---|-------|--------|
| Q2 | `q2_geometric_decay_alpha_decimal_0_5_provisional` | **Active** — alpha remains provisional; CDL amendment required to adopt `α=0.45` |
| Q8 | `q8_epoch_mint_source_sim_provenance_01_required` | **Satisfied** — SIM-PROVENANCE-01 has run (Run 01 + Run 02) |
| Q9 | `q9_float_kill_decimal_literal_0_5` | **Complete** — float kill completed before this window and reinforced by FLOAT-KILL-01 Phase 1119 hardening |
| All other Q tokens | unchanged from Phase 1113 ratification | No change this window |

`PROVENANCE_DECAY_ALPHA` remains `Decimal("0.5")` in `ilc_core/types.py`. The SIM
recommendation (`α=0.45`) requires a future-window CDL amendment (SENSITIVE, human GO
token) to take effect constitutionally. No CDL mutation occurred in Window 1118–1123.

---

## 5. Dependency Token Check

| Token | Expected value | Status |
|-------|----------------|--------|
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1114.v0.3"` | unchanged |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` | unchanged |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.5")` | unchanged; provisional |

---

## 6. SIM-SPECTRAL-02 Readiness

`out/sim_provenance_01_time_series.json` was written at Phase 1120 with shape 100 nodes ×
200 epochs. It satisfies the hard input requirement for SIM-SPECTRAL-02: per-node forward
PROVENANCE descendant counts as a time series, not a single epoch snapshot.
SIM-SPECTRAL-02 is not scheduled this window; the data dependency is satisfied and
scheduling is a next-window decision.

---

## 7. Deferred Research: Conley Index

Conley Index Theory framing for ILC epistemic stability is archived at
`docs/antigravity_tasks/antigravity_prompt__conley_index_framing_review_v0.1.md` and
deferred as a pre-RC1.0 research direction; it is not scheduled in any current window.

---

## 8. Audit Findings

| Finding | Disposition |
|---------|-------------|
| Q8 SIM-PROVENANCE-01 obligation | Satisfied by Phase 1120 Run 01 + Phase 1121 Run 02 |
| Q2 alpha lock | Still active; requires future SENSITIVE CDL amendment before adopting `α=0.45` |
| FLOAT-KILL-02 | Not triggered |
| SIM-SPECTRAL-02 | Data dependency satisfied; scheduling deferred |
| Conley Index research | Backburner / pre-RC1.0; not a current-window task |

No blocking audit findings. Window 1118–1123 is clean for Phase 1123 closure gate.

`coherence_report_1122_verdict=pass`
