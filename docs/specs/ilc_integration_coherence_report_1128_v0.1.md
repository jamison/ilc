# ILC Integration Coherence Report — Phase 1128
Window: 1124–1129
Phase: 1128
Date: 2026-04-30
Verdict: coherence_report_1128_verdict=pass

---

## 1. Purpose

Window 1124–1129 executed a single constitutional lane: the CDL-084 Q2 alpha amendment
locking `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` based on SIM-PROVENANCE-01 evidence.
This report audits that the amendment is internally consistent and ready for the Phase
1129 closure gate.

Prelock source: `docs/specs/ilc_cdl_084_q2_amendment_prelock_1125_v0.1.md`.

---

## 2. CDL-084 Q2 Amendment Coverage Table

| Item | Before (Phase 1113) | After (Phase 1126) | Verified |
|------|---------------------|-------------------|----------|
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.5")` (provisional) | `Decimal("0.45")` (locked) | `ilc_core/types.py` |
| Q2 token | `q2_geometric_decay_alpha_decimal_0_5_provisional` | `q2_geometric_decay_alpha_decimal_0_45_locked` | CDL-084 doc |
| Runtime version | `epoch_attribution_settle_runtime_1114.v0.3` | `epoch_attribution_settle_runtime_1126.v0.4` | settle runtime |
| CDL log | CDL-084 Q2: provisional | CDL-084 Q2: locked Phase 1126 | CDL log row |
| Q8 status | Active — SIM required | Satisfied Phase 1121 | alpha disposition |

---

## 3. SIM Evidence Chain

SIM result to constitutional lock:

- Q8 satisfaction: `docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md`.
- Run 01 (Phase 1120): alpha `0.45` passed; alpha `0.50` failed mint-surface
  (`0.2065 > 0.20` threshold).
- Run 02 (Phase 1121): alpha `0.45` keep rate `3/3` across seeds `42`, `1337`, and
  `2026`; alpha `0.50` keep rate `2/3`.
- SIM recommendation adopted by CDL-084 Q2 amendment in Phase 1126.

---

## 4. Dependency Token Check

| Token | Expected value |
|-------|----------------|
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.45")` |
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1126.v0.4"` |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` (unchanged) |

---

## 5. Three-Hop Payout Reference (Locked)

| Hop | Payout | Formula |
|-----|--------|---------|
| 1 | `Decimal("0.09")` | `Decimal("0.20") * Decimal("0.45")^1` |
| 2 | `Decimal("0.0405")` | `Decimal("0.20") * Decimal("0.45")^2` |
| 3 | `Decimal("0.018225")` | `Decimal("0.20") * Decimal("0.45")^3` |

---

## 6. Blast Radius Disposition

Phase 1125 found 18 UPDATE-REQUIRED source-line hits across 7 test files. All were updated
in Phase 1126 Commit 1 (`deb5fc00`). Phantom edit verification passed between Commit 1 and
Commit 2.

One additional correction was included: `test_phase_942_cdl_081_hyperedge_ecu_attribution.py`
line 140 previously compared `PROVENANCE_DECAY_ALPHA` to float `0.5`; it now compares to
`Decimal("0.45")`.

---

## 7. Audit Findings

| Finding | Disposition |
|---------|-------------|
| CDL-084 Q2 alpha value | Locked at `Decimal("0.45")` in Phase 1126 |
| CDL-084 Q8 SIM obligation | Satisfied by SIM-PROVENANCE-01 Run 01 + Run 02 |
| Runtime version | Bumped to `epoch_attribution_settle_runtime_1126.v0.4` |
| Test evidence | Phase 1127 evidence suite passed (`8 passed`) |
| Historical preservation | Phase 1113 git history still records `Decimal("0.5")` |

No blocking audit findings. Window 1124–1129 is clean for Phase 1129 closure gate.

`coherence_report_1128_verdict=pass`
