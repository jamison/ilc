# CDL-084 Q2 Alpha Amendment Prelock — Phase 1125

Window: 1124–1129
Phase: 1125
Date: 2026-04-30
Sensitivity: NON-SENSITIVE

`cdl_084_q2_prelock_hardened_phase_1125`

## 1. Amendment Summary

| Item | Value |
|------|-------|
| CDL | CDL-084 |
| Q number | Q2 |
| Current value | `PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.5")` (provisional) |
| Proposed value | `PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.45")` (locked) |
| Current Q2 token | `q2_geometric_decay_alpha_decimal_0_5_provisional` |
| New Q2 token | `q2_geometric_decay_alpha_decimal_0_45_locked` |
| Current runtime version | `epoch_attribution_settle_runtime_1114.v0.3` |
| New runtime version | `epoch_attribution_settle_runtime_1126.v0.4` |
| Amendment phase | 1126 (SENSITIVE — human GO token required) |

## 2. SIM Evidence Basis

SIM-PROVENANCE-01 is complete and satisfies CDL-084 Q8:
`q8_epoch_mint_source_sim_provenance_01_required`.

| Alpha | Keep rate | Mean mint drift | Drift stddev | Concentration pass rate | Disposition |
|-------|-----------|-----------------|--------------|-------------------------|-------------|
| `0.45` | `3/3` | `0.1742826703` | `0.0100630625` | `3/3` | recommended |
| `0.50` | `2/3` | `0.1933566361` | `0.0114533082` | `3/3` | seed-marginal; not confirmed |

Evidence sources:

- Run 01: `docs/sims/sim_provenance_01/results_phase_1120_run_01.md`
- Run 02: `docs/sims/sim_provenance_01/results_phase_1121_run_02.md`
- Disposition: `docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md`

The SIM recommendation is `α=0.45`. This amendment adopts that recommendation if the
future SENSITIVE Phase 1126 ratification proceeds.

## 3. Files To Modify In Phase 1126

Commit 1 (runtime — no CDL env var):

- `ilc_core/types.py`
- `ilc_core/economics/epoch_attribution_settle_runtime.py`
- `tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py`
- `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py`
- `tests/test_phase_1117_window_1110_1117_closure_gate.py`
- `tests/test_phase_1120_sim_provenance_01_commissioning.py`
- `tests/test_phase_1121_sim_provenance_01_run02_disposition.py`
- `tests/test_phase_1122_coherence_capsule_v5_36.py`
- `tests/test_phase_1123_window_1118_1123_closure_gate.py`

Commit 2 (CDL doc — requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1126`):

- `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Blast-radius summary: 18 UPDATE-REQUIRED source-line hits across 7 test files. This exceeds
the Phase 1125 prompt's `>10` threshold, so Phase 1126 must not proceed without explicit
human confirmation that this scope is acceptable.

## 4. Grep Results

### Grep 1 — Live constant references in tests

Command:

```bash
grep -rn "PROVENANCE_DECAY_ALPHA" tests/
```

Output:

```text
tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py:38:    PROVENANCE_DECAY_ALPHA,
tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py:140:    assert PROVENANCE_DECAY_ALPHA == 0.5, "PROVENANCE_DECAY_ALPHA must be 0.5 (provisional)"
tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py:142:    assert PROVENANCE_DECAY_ALPHA < 1.0, "PROVENANCE_DECAY_ALPHA must be < 1 for convergence"
tests/test_phase_1120_sim_provenance_01_commissioning.py:16:    PROVENANCE_DECAY_ALPHA,
tests/test_phase_1120_sim_provenance_01_commissioning.py:121:    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
tests/test_phase_1120_sim_provenance_01_commissioning.py:122:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1120_sim_provenance_01_commissioning.py:148:    assert payouts == [("creator_parent", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA)]
tests/test_phase_1120_sim_provenance_01_commissioning.py:205:    assert "PROVENANCE_DECAY_ALPHA" in text
tests/test_phase_1120_sim_provenance_01_commissioning.py:254:    assert "does not change `PROVENANCE_DECAY_ALPHA`" in text
tests/test_phase_1117_window_1110_1117_closure_gate.py:23:    PROVENANCE_DECAY_ALPHA,
tests/test_phase_1117_window_1110_1117_closure_gate.py:127:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1117_window_1110_1117_closure_gate.py:128:    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
tests/test_phase_1117_window_1110_1117_closure_gate.py:129:    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)
tests/test_phase_1117_window_1110_1117_closure_gate.py:157:    assert PROVENANCE_DECAY_ALPHA**1 == Decimal("0.5")
tests/test_phase_1117_window_1110_1117_closure_gate.py:158:    assert PROVENANCE_DECAY_ALPHA**2 == Decimal("0.25")
tests/test_phase_1117_window_1110_1117_closure_gate.py:159:    assert PROVENANCE_DECAY_ALPHA**3 == Decimal("0.125")
tests/test_phase_1117_window_1110_1117_closure_gate.py:167:    assert payouts[0] == ("c1", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**1)
tests/test_phase_1117_window_1110_1117_closure_gate.py:168:    assert payouts[1] == ("c2", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**2)
tests/test_phase_1117_window_1110_1117_closure_gate.py:169:    assert payouts[2] == ("c3", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**3)
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:27:    PROVENANCE_DECAY_ALPHA,
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:65:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:66:    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:70:    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:158:    expected = REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:184:        ("creator_A", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:185:        ("creator_B", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:186:        ("creator_C", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 3)),
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:222:        ("creator_A", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:223:        ("creator_B", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:290:    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:291:    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:345:        ("creator_A", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:346:        ("creator_B", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
tests/test_phase_1122_coherence_capsule_v5_36.py:6:from ilc_core.types import PROVENANCE_DECAY_ALPHA
tests/test_phase_1122_coherence_capsule_v5_36.py:44:    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
tests/test_phase_1122_coherence_capsule_v5_36.py:45:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
Binary file tests/__pycache__/test_phase_1117_window_1110_1117_closure_gate.cpython-314-pytest-9.0.3.pyc matches
Binary file tests/__pycache__/test_phase_1121_sim_provenance_01_run02_disposition.cpython-314-pytest-9.0.3.pyc matches
Binary file tests/__pycache__/test_phase_1115_cdl_084_provenance_chain_attribution.cpython-314-pytest-9.0.3.pyc matches
Binary file tests/__pycache__/test_phase_1122_coherence_capsule_v5_36.cpython-314-pytest-9.0.3.pyc matches
Binary file tests/__pycache__/test_phase_942_cdl_081_hyperedge_ecu_attribution.cpython-314-pytest-9.0.3.pyc matches
Binary file tests/__pycache__/test_phase_1120_sim_provenance_01_commissioning.cpython-314-pytest-9.0.3.pyc matches
Binary file tests/__pycache__/test_phase_1123_window_1118_1123_closure_gate.cpython-314-pytest-9.0.3.pyc matches
tests/test_phase_1121_sim_provenance_01_run02_disposition.py:8:from ilc_core.types import PROVENANCE_DECAY_ALPHA
tests/test_phase_1121_sim_provenance_01_run02_disposition.py:73:    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
tests/test_phase_1121_sim_provenance_01_run02_disposition.py:74:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1123_window_1118_1123_closure_gate.py:10:from ilc_core.types import PROVENANCE_DECAY_ALPHA
tests/test_phase_1123_window_1118_1123_closure_gate.py:92:    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
tests/test_phase_1123_window_1118_1123_closure_gate.py:93:    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)
tests/test_phase_1123_window_1118_1123_closure_gate.py:94:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1123_window_1118_1123_closure_gate.py:154:    assert "PROVENANCE_DECAY_ALPHA remains Decimal(\"0.50\") in ilc_core/types.py" in src
tests/test_phase_1123_window_1118_1123_closure_gate.py:163:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
```

Classification:

- UPDATE-REQUIRED: `tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py:140`
- UPDATE-REQUIRED: `tests/test_phase_1120_sim_provenance_01_commissioning.py:122`
- UPDATE-REQUIRED: `tests/test_phase_1117_window_1110_1117_closure_gate.py:127`, `:157`, `:158`, `:159`
- UPDATE-REQUIRED: `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:65`
- UPDATE-REQUIRED: `tests/test_phase_1122_coherence_capsule_v5_36.py:45`
- UPDATE-REQUIRED: `tests/test_phase_1121_sim_provenance_01_run02_disposition.py:74`
- UPDATE-REQUIRED: `tests/test_phase_1123_window_1118_1123_closure_gate.py:94`, `:163`
- UNRELATED: import/type-only/computed-live uses, convergence check `< 1.0`, doc-string checks, and generated `__pycache__` hits.

### Grep 2 — Hardcoded old alpha value in tests

Command:

```bash
grep -rn 'Decimal("0\.5")' tests/ | grep -v "REUSE\|0\.50\|0\.500"
```

Output:

```text
tests/test_phase_550_passive_ecu_attribution_runtime.py:107:    assert runtime.quality_factor(Decimal("0.5")) == Decimal("1.000000000000")
tests/test_phase_550_passive_ecu_attribution_runtime.py:112:        Decimal("1"), Decimal("0.04"), Decimal("0.5")
tests/test_phase_550_passive_ecu_attribution_runtime.py:118:        Decimal("0"), Decimal("1"), Decimal("0.5")
tests/test_phase_550_passive_ecu_attribution_runtime.py:130:        Decimal("1"), Decimal("0.5"), Decimal("0.5")
tests/test_phase_0947_h012_epoch_attribution_settle.py:248:    stake_map = {"star_1": {"alice": Decimal("1"), "bob": Decimal("0.5")}}
tests/test_phase_1120_sim_provenance_01_commissioning.py:122:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1117_window_1110_1117_closure_gate.py:127:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1117_window_1110_1117_closure_gate.py:157:    assert PROVENANCE_DECAY_ALPHA**1 == Decimal("0.5")
tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:65:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1122_coherence_capsule_v5_36.py:45:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
Binary file tests/__pycache__/test_phase_1123_window_1118_1123_closure_gate.cpython-314-pytest-9.0.3.pyc matches
tests/test_phase_1121_sim_provenance_01_run02_disposition.py:74:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1123_window_1118_1123_closure_gate.py:94:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_phase_1123_window_1118_1123_closure_gate.py:163:    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")
tests/test_epoch_ledger.py:17:    ledger.record_task(epoch=1, ecu_spent=Decimal("0.5"), reward=Decimal("0.25"))
tests/test_epoch_ledger.py:27:    assert stats1.ecu_spent == Decimal("0.5")
tests/test_window_545_554_audit_regressions.py:35:            passive_runtime.compute_passive_ecu(invalid, Decimal("0.5"), Decimal("0.5"))
tests/test_window_545_554_audit_regressions.py:45:            passive_runtime.compute_passive_ecu(Decimal("1"), invalid, Decimal("0.5"))
tests/test_window_545_554_audit_regressions.py:74:        Decimal("1"), Decimal(str(committed_score)), Decimal("0.5")
tests/test_phase_551_passive_ecu_attribution_hardening.py:70:        Decimal("1"), Decimal("0.5"), Decimal("0")
tests/test_phase_551_passive_ecu_attribution_hardening.py:73:        Decimal("1"), Decimal("0.5"), Decimal("1")
tests/test_phase_551_passive_ecu_attribution_hardening.py:87:    for centrality_score in (Decimal("0.05"), Decimal("0.5"), Decimal("1")):
tests/test_phase_551_passive_ecu_attribution_hardening.py:88:        for q_i in (Decimal("0"), Decimal("0.5"), Decimal("1")):
tests/test_phase_551_passive_ecu_attribution_hardening.py:94:        runtime.compute_passive_ecu(Decimal("-1"), Decimal("0.5"), Decimal("0.5"))
```

Classification:

- UPDATE-REQUIRED: `tests/test_phase_1120_sim_provenance_01_commissioning.py:122`
- UPDATE-REQUIRED: `tests/test_phase_1117_window_1110_1117_closure_gate.py:127`, `:157`
- UPDATE-REQUIRED: `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py:65`
- UPDATE-REQUIRED: `tests/test_phase_1122_coherence_capsule_v5_36.py:45`
- UPDATE-REQUIRED: `tests/test_phase_1121_sim_provenance_01_run02_disposition.py:74`
- UPDATE-REQUIRED: `tests/test_phase_1123_window_1118_1123_closure_gate.py:94`, `:163`
- UNRELATED: passive ECU quality/centrality values, epoch ledger values, co-authorship stake, and generated `__pycache__` hits.

### Grep 3 — Hardcoded hop-1 payout

Command:

```bash
grep -rn '"0\.10"\|Decimal("0\.10")' tests/
```

Output:

```text
tests/test_phase_0947_h012_epoch_attribution_settle.py:148:    assert amounts["alice"] == amounts["bob"] == Decimal("0.10")
```

Classification:

- UNRELATED: CO_AUTHORSHIP equal split, not PROVENANCE alpha payout.

### Grep 4 — Hardcoded hop-2 payout

Command:

```bash
grep -rn '"0\.05"\|Decimal("0\.05")' tests/
```

Output:

```text
tests/test_phase_550_passive_ecu_attribution_runtime.py:91:    assert runtime.DECAY_FLOOR == Decimal("0.05")
tests/test_phase_0947_h012_epoch_attribution_settle.py:160:    assert amounts["bob"] == Decimal("0.05")
tests/test_phase_551_passive_ecu_attribution_hardening.py:87:    for centrality_score in (Decimal("0.05"), Decimal("0.5"), Decimal("1")):
```

Classification:

- UNRELATED: passive ECU decay floor, CO_AUTHORSHIP stake split, and centrality score test values.

### Grep 5 — Hardcoded hop-3 payout

Command:

```bash
grep -rn '"0\.025"\|Decimal("0\.025")' tests/
```

Output:

```text
zero results
```

Classification: zero results.

### Grep 6 — PROVENANCE_DECAY_ALPHA in ilc_core/

Command:

```bash
grep -rn "PROVENANCE_DECAY_ALPHA" ilc_core/
```

Output:

```text
ilc_core/types.py:74:# PROVENANCE_DECAY_ALPHA: geometric decay per provenance hop (α < 1 ensures
ilc_core/types.py:83:PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.5")         # Q9: CDL-084 locks mechanism; SIM-PROVENANCE-01 refines value
Binary file ilc_core/__pycache__/types.cpython-314.pyc matches
ilc_core/economics/epoch_attribution_settle_runtime.py:9:PROVENANCE_DECAY_ALPHA; AttributionEvent.provenance_chain field added.
ilc_core/economics/epoch_attribution_settle_runtime.py:22:    PROVENANCE_DECAY_ALPHA,
ilc_core/economics/epoch_attribution_settle_runtime.py:231:                decay = PROVENANCE_DECAY_ALPHA ** (hop_index + 1)
Binary file ilc_core/economics/__pycache__/epoch_attribution_settle_runtime.cpython-314.pyc matches
```

Classification:

- UPDATE-REQUIRED: `ilc_core/types.py:83`
- UNRELATED: comments/import/use sites that should continue referencing the constant; generated `__pycache__` hits.

### Supplemental grep — old payout-equivalent literals missed by Greps 3–5

Command:

```bash
rg -n 'Decimal\("0\.(100|0500|02500|25|125)"\)|"0\.(100|0500|02500|25|125)"' tests/
```

Output:

```text
tests/test_phase_1117_window_1110_1117_closure_gate.py:158:    assert PROVENANCE_DECAY_ALPHA**2 == Decimal("0.25")
tests/test_phase_1117_window_1110_1117_closure_gate.py:159:    assert PROVENANCE_DECAY_ALPHA**3 == Decimal("0.125")
tests/test_phase_1117_window_1110_1117_closure_gate.py:184:        ("c1", Decimal("0.100")),
tests/test_phase_1117_window_1110_1117_closure_gate.py:185:        ("c2", Decimal("0.0500")),
tests/test_phase_1117_window_1110_1117_closure_gate.py:186:        ("c3", Decimal("0.02500")),
tests/test_phase_1117_window_1110_1117_closure_gate.py:228:    assert payouts == [("c1", Decimal("0.100")), ("c2", Decimal("0.0500"))]
tests/test_phase_1120_sim_provenance_01_commissioning.py:168:        ("creator_1", Decimal("0.100")),
tests/test_phase_1120_sim_provenance_01_commissioning.py:169:        ("creator_2", Decimal("0.0500")),
tests/test_phase_1120_sim_provenance_01_commissioning.py:170:        ("creator_3", Decimal("0.02500")),
tests/test_epoch_ledger.py:17:    ledger.record_task(epoch=1, ecu_spent=Decimal("0.5"), reward=Decimal("0.25"))
tests/test_epoch_ledger.py:28:    assert stats1.rewards_paid == Decimal("0.25")
```

Classification:

- UPDATE-REQUIRED: `tests/test_phase_1117_window_1110_1117_closure_gate.py:158`, `:159`, `:184`, `:185`, `:186`, `:228`
- UPDATE-REQUIRED: `tests/test_phase_1120_sim_provenance_01_commissioning.py:168`, `:169`, `:170`
- UNRELATED: epoch ledger reward values.

## 5. Payout Value Reference

The three-hop PROVENANCE payout changes as follows. Phase 1126 must update any
UPDATE-REQUIRED hits to these new values:

| Hop | Old (α=0.50) | New (α=0.45) |
|-----|--------------|--------------|
| 1 | `Decimal("0.10")` = `Decimal("0.20") * Decimal("0.5")^1` | `Decimal("0.09")` = `Decimal("0.20") * Decimal("0.45")^1` |
| 2 | `Decimal("0.05")` = `Decimal("0.20") * Decimal("0.5")^2` | `Decimal("0.0405")` = `Decimal("0.20") * Decimal("0.45")^2` |
| 3 | `Decimal("0.025")` = `Decimal("0.20") * Decimal("0.5")^3` | `Decimal("0.018225")` = `Decimal("0.20") * Decimal("0.45")^3` |

Python verification:

```text
Decimal("0.20") * Decimal("0.45") ** 1 = Decimal("0.0900")
Decimal("0.20") * Decimal("0.45") ** 2 = Decimal("0.040500")
Decimal("0.20") * Decimal("0.45") ** 3 = Decimal("0.01822500")
```

Tests may assert the canonical shorter forms `Decimal("0.09")`, `Decimal("0.0405")`,
and `Decimal("0.018225")`; Decimal equality ignores trailing zeros.

## 6. Historical Commit Reference

Phase 1127 evidence test E5 will assert that the Phase 1113 runtime commit still shows
the old `Decimal("0.5")` value in git history.

Phase 1113 runtime commit: `3d943f32`

Evidence test pattern:

```python
result = subprocess.run(
    ["git", "show", "3d943f32:ilc_core/types.py"],
    capture_output=True, text=True, check=True,
)
assert 'Decimal("0.5")' in result.stdout
```

## 7. Prelock Token

`cdl_084_q2_prelock_hardened_phase_1125`
