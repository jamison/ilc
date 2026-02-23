# ILC Epoch Duration Candidate Matrix and Policy Options 274 Fix 2 v0.1

Status: Non-ratifying analytical artifact
Date: 2026-02-23
Window: Phase 274 pre-ratification evidence hardening

## 1. Purpose and boundary

This artifact converts epoch-index issuance simulations into wall-clock time and provides three concrete policy options (`A/B/C`) for downstream ratification lanes (`CDL-027`, `CDL-030`).

Boundary statement:
- non-ratifying,
- no decision-log mutation,
- no runtime changes.

## 2. Canonical constants and historical anchors

Canonical constants used in this matrix:
- `C_max = 25,920,000`,
- `G_max = 1,296,000` (`5%` of `C_max`).

Historical anchors recovered from corpus:
- `Z_Past_Chats/2025_06_03_ILC - Higher Dimensional Geometry in DS.txt:3408` (`25,920,000` recommendation),
- `Z_Past_Chats/2025_06_03_ILC - Higher Dimensional Geometry in DS.txt:3446` (user acceptance),
- `Z_Past_Chats/2025_06_18_ILC - 4D Cognitive AI Model.txt:7004` (`5-6%` threshold framing),
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:6597` (Bitcoin halving is block-based),
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20889` (smooth front-loaded decay framing).

## 3. Simulation basis and interpretation

Source outputs:
- `out/genesis_accrual_sweep_274_exploratory/genesis_accrual_centrality_reputation_sweep.csv`,
- `out/genesis_accrual_sweep_274_exploratory/genesis_accrual_centrality_reputation_summary.json`.

Interpretation rules:
- `reach_5pct_epoch`: epoch index where Genesis cumulative reaches `G_max`,
- `p50/p90`: median and 90th percentile across swept centrality/reputation scenarios,
- wall-clock conversion: `years = epochs * (days_per_epoch / 365)`.

Governor pushback (design-critical):
- if the Genesis taper governor uses issued-to-date denominator, Genesis does not reliably converge to exact `5%` of `C_max`,
- if the denominator is theoretical-cap (`C_max`), Genesis consistently converges to exact `1,296,000`.

Therefore all policy options below assume:
- `governor_mode = theoretical_cap`.

## 4. Epoch duration candidate matrix (wall-clock years)

Time to `G_max` (`5%`) by schedule candidate:

| Schedule candidate | Reach `5%` p50 (epochs) | Reach `5%` p90 (epochs) | 1 day epoch (p50 / p90 years) | 1 week epoch (p50 / p90 years) | 1 month epoch (p50 / p90 years) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `exp, lambda=0.030` | 10 | 18 | 0.03 / 0.05 | 0.19 / 0.35 | 0.82 / 1.48 |
| `exp, lambda=0.024` | 13 | 23 | 0.04 / 0.06 | 0.25 / 0.44 | 1.07 / 1.89 |
| `exp, lambda=0.018` | 18 | 33 | 0.05 / 0.09 | 0.35 / 0.63 | 1.48 / 2.71 |
| `halving, H=32` | 15 | 26 | 0.04 / 0.07 | 0.29 / 0.50 | 1.23 / 2.14 |
| `halving, H=48` | 23 | 45 | 0.06 / 0.12 | 0.44 / 0.86 | 1.89 / 3.70 |
| `halving, H=64` | 31 | 71 | 0.08 / 0.19 | 0.59 / 1.36 | 2.55 / 5.84 |

Long-tail view (`~95%` total issuance reached), by same schedules:

| Schedule candidate | Epochs to ~95% issuance | 1 day epoch (years) | 1 week epoch (years) | 1 month epoch (years) |
| --- | ---: | ---: | ---: | ---: |
| `exp, lambda=0.030` | 99 | 0.3 | 1.9 | 8.1 |
| `exp, lambda=0.024` | 124 | 0.3 | 2.4 | 10.2 |
| `exp, lambda=0.018` | 165 | 0.5 | 3.2 | 13.6 |
| `halving, H=32` | 137 | 0.4 | 2.6 | 11.3 |
| `halving, H=48` | 207 | 0.6 | 4.0 | 17.0 |
| `halving, H=64` | 276 | 0.8 | 5.3 | 22.7 |

## 5. Policy options for 274/275 carry-forward

All options below keep:
- `C_max = 25,920,000`,
- `G_max = 1,296,000` hard cap objective,
- `governor_mode = theoretical_cap`,
- `CDL-028` prelock candidate from Phase 274-fix1: `10%` fee-burn split.

### Option A: Fast fade (high front-load)

- schedule: `exp, lambda=0.030`,
- epoch duration candidate: `1 month`,
- Genesis reaches `5%`: `0.82y` p50 (`1.48y` p90),
- total issuance reaches `~95%`: `8.1y`.

Pros:
- fastest Genesis handoff signal,
- strongest early onboarding incentives.

Risks:
- compressed distribution window,
- sharper early concentration pressure.

### Option B: Balanced handoff (recommended)

- schedule: `halving, H=48`,
- epoch duration candidate: `1 month`,
- Genesis reaches `5%`: `1.89y` p50 (`3.70y` p90),
- total issuance reaches `~95%`: `17.0y`.

Pros:
- aligns with "first few years" Genesis taper objective,
- materially longer issuance tail for sustained network incentives,
- closer behavioral rhythm to Bitcoin-style long-run scarcity narratives without step-cliff shock.

Risks:
- slower Genesis fade than Option A,
- requires tighter fee/reward controller discipline during years 2-5.

### Option C: Long-tail conservative

- schedule: `halving, H=64`,
- epoch duration candidate: `1 month`,
- Genesis reaches `5%`: `2.55y` p50 (`5.84y` p90),
- total issuance reaches `~95%`: `22.7y`.

Pros:
- strongest long-horizon issuance tail,
- lowest schedule-induced volatility.

Risks:
- slowest Genesis fade,
- may under-deliver early participation urgency.

## 6. Monetary-theory pushback and design guidance

Policy pushback:
- unconditional perpetual inflation is not required for healthy usage velocity,
- in this design, usage incentives should be anchored primarily to ECU-denominated work pricing and adaptive conversion, not to blunt inflation.

Recommended compromise for future lane discussion (`CDL-027` / `CDL-030`):
- keep hard-cap narrative intact,
- allow only contingent micro-tail activation (security-budget mode) and pair it with a burn floor so net issuance stays near neutral,
- do not introduce unconditional perpetual tail as default policy.

## 7. Recommended patch targets for upcoming lanes

For Phase 274 ratification evidence (`CDL-028`):
- include a short dependency note that fee-burn lock is compatible with all three options above and does not pre-ratify decay schedule.

For Phase 275 evidence closure C:
- include this matrix verbatim (or equivalent derived table),
- evaluate `A/B/C` explicitly,
- select one recommended candidate to carry into `CDL-027` ratification lane (`Phase 276`),
- preserve non-ratifying boundary in Phase 275.

## 8. Non-goals

This artifact does not:
- ratify `CDL-027` or `CDL-030`,
- set final clamp bounds (`P_min`, `P_max`),
- modify any decision-log row.
