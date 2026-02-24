# ILC Historical Simulation Replay Evidence (2025-10-09 set) v0.1

Status: non-normative replay evidence  
Date: 2026-02-23

## 1. Scope

This artifact records deterministic local replay outputs for historical simulation sets referenced in:
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt`

Included replay groups:
1. controller telemetry 80-epoch replay,
2. kappa A/B replay (normal + stressed),
3. A5 subjective-gating policy replay (`off`, `conservative`, `hybrid`).

## 2. Replay commands

```bash
python3 simulations/historical_recovered/replay_controller_telemetry_80_epoch_20251009.py
python3 simulations/historical_recovered/replay_kappa_ab_20251009.py
python3 simulations/historical_recovered/replay_a5_subjective_gating_20251009.py
```

## 3. Output location

All replay outputs are written under:
- `out/recovered_20251009/`

File integrity manifest:
- `out/recovered_20251009/checksums.sha256`

## 4. Output inventory

### 4.1 Controller telemetry replay
- `out/recovered_20251009/controller_telemetry/telemetry_80_epoch_trace.csv`
- `out/recovered_20251009/controller_telemetry/telemetry_80_summary.csv`

### 4.2 Kappa A/B replay
- `out/recovered_20251009/kappa_ab/kappa_normal_base_epoch.csv`
- `out/recovered_20251009/kappa_ab/kappa_normal_kappa_epoch.csv`
- `out/recovered_20251009/kappa_ab/kappa_stressed_base_epoch.csv`
- `out/recovered_20251009/kappa_ab/kappa_stressed_kappa_epoch.csv`
- `out/recovered_20251009/kappa_ab/kappa_ab_summary.csv`

### 4.3 A5 subjective-gating replay (historical policy variants)
- `out/recovered_20251009/a5_subjective_gating/a5_off_epoch.csv`
- `out/recovered_20251009/a5_subjective_gating/a5_conservative_epoch.csv`
- `out/recovered_20251009/a5_subjective_gating/a5_hybrid_epoch.csv`
- `out/recovered_20251009/a5_subjective_gating/a5_subjective_gating_summary.csv`

## 5. A5 summary snapshot

From `a5_subjective_gating_summary.csv`:

| policy | incorrect_finalized_pct | false_refute_per_final_pct | qa_duty | subjective_broadcasts | reuse_hits |
|---|---:|---:|---:|---:|---:|
| off | 2.91 | 0.00 | 0.77 | 0 | 0 |
| conservative | 2.89 | 0.00 | 0.86 | 77 | 77 |
| hybrid | 3.32 | 0.12 | 0.82 | 431 | 431 |

## 6. Reproducibility notes

1. The telemetry and kappa replays execute recovered historical logic through wrapper scripts that localize outputs.
2. The A5 replay is a deterministic reconstruction of historical policy variants using fixed seeds and target policy totals from the chat corpus references.
3. This evidence package is replay-oriented and does not mutate protocol runtime or decision-log state.
