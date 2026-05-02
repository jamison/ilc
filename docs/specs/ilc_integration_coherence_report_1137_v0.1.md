# ILC Integration Coherence Report — Phase 1137

**Date:** 2026-05-02
**Window:** 1130–1138
**Phase:** 1137
**Status:** NON-SENSITIVE — doc-only

`coherence_report_1137_verdict=pass`

---

## §1 Purpose

This coherence report covers Window 1130–1138, the SIM-SPECTRAL-02 simulation research
window. The window commissioned, ran, and disposed of SIM-SPECTRAL-02: the simulation
testing whether the hypergraph can serve as a relative directional epistemic efficiency
meter. A secondary research stream — the Genesis Morphogenic Hypergraph Atlas — was
inserted as Phase 1136A, producing the first formally documented Genesis core star map,
GENESIS-COMPILE-01 diagnostic, and atlas tooling chain.

No CDL was opened or ratified in this window. No `ilc_core/` files were changed. No
settlement rules were amended. The pre-commit CDL mutation hook was not triggered at
any phase.

---

## §2 SIM-SPECTRAL-02 Outcome Summary

### Declared scenario

**Scenario B — Advisory Only** (`sim_spectral_02_scenario_b_advisory_phase_1136`)

### Key findings

**What works:** The V_t efficiency slope metric correctly identifies the healthy scenario
(S1) by pass/fail verdict (18/18 vs 0/18) and by slope magnitude across all three topology
tracks (A, B, C). S1 dominates in absolute slope (+0.557) under homoiconic dynamics, and
the Track D connectivity response curve establishes a clear trust threshold.

**What doesn't yet work:**

1. **Gaming resistance gap.** Under the homoiconic model, adversarial and gaming scenarios
   also produce positive slopes (S2=+0.214, S3=+0.358, S4=+0.246, G2=+0.481). The flat
   sign-separation of the synthetic baseline is lost. The β calibration probe (β=2.0,
   α=0.5) improves G2 coordinated-reuse discrimination (S/S1 ratio 0.864→0.626) but does
   not resolve S3 Sybil (S/S1 ratio 0.643→0.647 — essentially unchanged). A
   topology-sensitive Structural_Impedance term is needed.

2. **Genesis seed limitation.** Run 02 seeds only 3 Genesis axioms + 97 synthetic
   artifacts. The 31-node Genesis core star map (produced Phase 1136A) is the proposed
   next S1 seed for SIM-SPECTRAL-03.

3. **Track D threshold.** `s1_vs_s2_separated=true` at all density multipliers including
   λ₂=0 (disconnected). Slope separation is not a spectral health signal. Spectral trust
   requires λ₂ > 0 (normalized Laplacian), N_BOOTSTRAP=44 nodes, and
   `largest_component_ratio ≥ 0.80` simultaneously.

### Disposition verdict

The metric is a **valid directional bootstrap indicator** but is **not deployment-ready**
as a constitutional or settlement input. Three conditions must be met before it advances:
(1) gaming resistance fix, (2) SIM-SPECTRAL-03 re-run with 31-node Genesis seed, (3)
spectral connectivity confirmed. No CDL opened. ADR recommendation is PROPOSED only.

---

## §3 CDL Chain: Unchanged

The CDL frontier is unchanged from Window 1124–1129.

| CDL | Status | Note |
|-----|--------|------|
| CDL-084 | Ratified (Phase 1113/1126) | Frontier; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` locked |
| CDL-085 | Deferred — SIM-gated | Phase 1136 disposition is Scenario B advisory; not yet sufficient to open CDL-085 |

No CDL was opened, prelocked, or ratified in Window 1130–1138. CDL-085 remains SIM-gated
pending SIM-SPECTRAL-03 evidence.

---

## §4 Runtime Chain: Unchanged

No `ilc_core/` files were modified in Window 1130–1138. The active runtime chain is
identical to the Window 1124–1129 close.

| Module | Version |
|--------|---------|
| `epoch_attribution_settle_runtime.py` | `epoch_attribution_settle_runtime_1129_fix1.v0.5` |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.45")` — locked Phase 1126 |
| `PROVENANCE_MAX_DEPTH` | `3` |

All CDL-084 Q1–Q10 decisions remain locked. No regression or drift detected.

---

## §5 Audit Findings

**Window is clean.** No findings to report.

- No `ilc_core/` changes — confirmed by `git diff --name-only HEAD~20..HEAD | grep ilc_core` returning no protocol files
- No CDL mutation env var used at any phase commit
- No float used for ECU/balance/reward values in any new code
- No `import random` in any new module
- Dirty files at window close: `out/monitoring/d2e_risk_snapshot_phase_306.json` and `out/monitoring/infrastructure_risk_snapshot_phase_316.json` — pre-existing, unrelated to this window; carry forward unchanged

### Atlas audit note

The GENESIS-COMPILE-01 diagnostic (Phase 1136A addendum) produced a
`PARTIAL_WITH_STRUCTURAL_GAPS` result: 17/31 core nodes are reachable from the Genesis
transition basis, and 506/1,623 observed source files are explained by the core star map.
This is a **graph-construction gap** (missing explicit authority-chain edges), not a
protocol defect or primitive-basis failure. Atlas Tier-1 edge additions in Window 1139+
are the correct response. This finding does not affect the runtime chain, CDL chain, or
any `ilc_core/` module.

---

`coherence_report_1137_verdict=pass`
