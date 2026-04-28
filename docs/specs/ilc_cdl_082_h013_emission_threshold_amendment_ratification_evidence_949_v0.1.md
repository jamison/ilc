# CDL-082 Ratification Evidence — Phase 949

**CDL:** CDL-082 — H-013 Gossip Beacon Emission Threshold Amendment
**Phase:** 949 (prelock hardening + evidence assembly)
**Window:** 945–952
**Date:** 2026-04-28
**Ratification target:** Phase 950

---

## 1. Scope and Purpose

This document assembles the complete ratification evidence for CDL-082. CDL-082 constitutionalises
the SIM-BEACON-01 recommendation to raise `H013_CHANGE_THRESHOLD` from 0.10 to 0.15, exiting
the spurious-emission regime. Evidence covers:

1. SIM-BEACON-01 simulation results (Phase 939) — the primary evidence source
2. Prelock assertion — CDL-082 was `open` at the Phase 948 introducing commit
3. Pre-ratification checklist completion
4. H-012 regression context — all settle() evidence tests pass at this phase boundary

---

## 2. SIM-BEACON-01 Evidence Record

**Source:** `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`
**Executed:** Phase 939

### Key SIM tokens cited

| Token | Meaning |
|-------|---------|
| `Q_SIGMA_SWEEP_COMPLETE` | Full sigma parameter sweep completed |
| `adversary_reduction_constant_0_684_regardless_of_sigma` | Adversary reduction is mathematical constant `1 - 1/√T` for T=10 — independent of sigma |
| `change_threshold_raise_0_10_to_0_15_recommended` | SIM recommends raising threshold to exit spurious-emission regime |
| `routing_correctness_0_05_sigma_97_65_percent` | Routing correctness at sigma=0.05 is 97.65% — unaffected by threshold change |

### Parameter recommendations from SIM-BEACON-01

| Parameter | Recommendation | Rationale |
|-----------|---------------|-----------|
| `H013_CHANGE_THRESHOLD` | Raise 0.10 → **0.15** | Exits spurious-emission regime; stable nodes suppress unnecessary emissions |
| `H013_TESTNET_EMISSION_SIGMA` | Keep at **0.05** | 97.65% routing correctness confirmed; sigma revision needs adversary model SIM |
| `DEFAULT_DEAD_PEER_SILENCE_EPOCHS` | Keep at **10** | 0% false-dead rate confirmed at 10 epochs |

### Pre-mutation state confirmed

Current value in `ilc_core/node/node_startup_runtime.py` (line 61, Phase 949 boundary):

```
H013_CHANGE_THRESHOLD: float = 0.1
```

This is the pre-mutation value. Phase 950 Commit 1 will raise this to `0.15`.

---

## 3. Pre-Ratification Checklist Completion

```
[x] SIM-BEACON-01 evidence cited — Phase 939 — complete (§2 above)
[x] Prelock hardening complete — Phase 949 — complete (§4 below)
[x] Runtime mutation target specified — ilc_core/node/node_startup_runtime.py:H013_CHANGE_THRESHOLD
[x] H-012 settle() tests pass (31/31) — Phase 947 — complete (§5 below)
[ ] Human ratification authorization — Phase 950 — pending
```

All items except human authorization are satisfied. Ratification authorization will be recorded
at Phase 950 execution.

---

## 4. Prelock Test: CDL-082 Open at Phase 948 Commit

**Opening commit:** `192e58ea` — `feat(cdl): open CDL-082 h013 emission threshold amendment (Phase 948)`

**Verification command:**
```bash
git show 192e58ea:docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md \
  | grep "^\*\*Status:"
```

**Expected output:** `**Status:** OPEN`

**Result at Phase 949 boundary:** `**Status:** OPEN` ✓

This confirms the CDL opened in the correct state at Phase 948 and was not retroactively mutated.

`cdl_082_prelock_asserts_open_at_phase_948_commit`

---

## 5. Regression Context (Phase 949 boundary)

### H-012 Evidence Tests

File: `tests/test_phase_0947_h012_epoch_attribution_settle.py`
Count: **31 tests** (30 CDL-081 §§4.1–4.6 evidence + 1 phantom edit guard)
Result: **31/31 pass**

Key assertions confirmed:
- `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_946.v0.1"`
- `CDL_081_DEPENDENCY == "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"`
- `CDL_HCON_01_DEPENDENCY` absent from `ilc_core/types.py` (phantom edit guard)
- All REUSE, CO_AUTHORSHIP, zero-member commons, REFUTATION paths verified
- All payout amounts confirmed Decimal (no float leakage)

### Full Regression

Test collection at Phase 949 boundary: **7,644 collected** (7,643 prior + 31 new Phase 947 tests;
note: 1 collection error in `test_phase_942_cdl_081_hyperedge_ecu_attribution.py` is pre-existing
and unrelated to this window's work).

Phase 945–948 deliverables are all documentary (sequence lock, capsule, CDL opening) — no test
regressions introduced. Phase 946 M1 Decimal fix is tested by Phase 947 test group 7 (4 tests).

---

## 6. Evidence Tokens

```
cdl_082_ratification_evidence_complete_phase_949
cdl_082_prelock_asserts_open_at_phase_948_commit
sim_beacon_01_change_threshold_recommendation_cited
h012_settle_31_tests_pass_evidence_recorded
cdl_082_prelock_hardening_complete_phase_949
```
