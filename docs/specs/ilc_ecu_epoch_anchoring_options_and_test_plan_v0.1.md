# ILC ECU Epoch Anchoring Options and Test Plan v0.1

Status: Planning artifact  
Date: 2026-02-25  
Owner lane: Economic monitoring / settlement policy

## 1. Problem statement

Should ECU settlement into ILC be anchored to one epoch only, or spread across multiple epochs?

Trade-off:
- shorter window -> faster utility and agent feedback,
- longer window -> better rollback/clawback/dispute safety.

## 2. Option set

| Option | Settlement window | Utility latency | Safety against fraud/reorg/dispute | Operational complexity |
|---|---|---|---|---|
| A | 1 epoch | highest | lowest | lowest |
| B | 2 epochs rolling | high | medium-high | medium |
| C | 3 epochs rolling | medium | high | medium-high |
| D | adaptive window (1-3) | variable | variable | highest |

## 3. Pushback and recommendation

### Pushback

- Pure 1-epoch anchoring is attractive for speed but fragile for adversarial phases and rollback requirements.
- 3+ epoch anchoring improves safety but can reduce agent utility by delaying realizable value and increasing treasury-like float effects.
- Adaptive schemes can outperform static windows but risk governance complexity and opaque behavior if triggers are weak.

### Recommended default for canonical testing

Start with **Option B (2-epoch rolling)** as baseline:
- Release model (example baseline for testing):
  - 70% of eligible ECU settlement at epoch `e+1`,
  - 30% deferred to epoch `e+2` subject to dispute/clawback outcomes.
- Rationale:
  - maintains strong utility responsiveness,
  - introduces meaningful safety buffer,
  - keeps policy understandable for both digital and human participants.

## 4. Testable hypotheses

H1: Option B preserves >90% of Option A utility throughput while materially reducing clawback error exposure.

H2: Option C reduces settlement volatility further but degrades agent participation/throughput more than Option B under normal loads.

H3: Adaptive window outperforms static windows only if trigger metrics are deterministic and low-noise.

## 5. Simulation plan

### 5.1 Required inputs
- ratified issuance constants (`CDL-025/026/027/028/029/030/031` context),
- workload profiles (steady, bursty, adversarial),
- dispute/fraud event model,
- rollback/reorg perturbation scenarios.

### 5.2 Required outputs
- settlement completion latency distribution,
- clawback precision/recall metrics,
- net agent utility throughput (ECU realized per wall-clock period),
- concentration and liquidity stress metrics,
- governance intervention frequency.

### 5.3 Determinism contract
- fixed seeds and locked parameter grids,
- reproducibility hash for each output artifact,
- mode-labeled outputs for every scenario class.

## 6. Lessons-learned integration checklist

Before policy ratification, demonstrate evidence against common failure modes:
- latency-arbitrage exploitation,
- reflexive emission loops,
- delayed-finality bank-run behavior,
- abuse of dispute windows by spam/low-quality claims,
- centralization pressure from long settlement delays.

## 7. Proposed policy path

1. Use Option B as canonical baseline in Phase-305 simulation lane.
2. Compare against A and C in the same test harness.
3. Defer adaptive D until baseline metrics are stable and trigger rules are deterministic.
4. Create `CDL-039` only after deterministic evidence package is published.

## 8. Canonical anchors

- `docs/specs/ilc_economic_risk_monitoring_contract_v0.1.md`
- `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.2.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`
