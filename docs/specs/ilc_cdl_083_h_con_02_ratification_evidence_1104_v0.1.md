# CDL-083 Ratification Evidence — Phase 1104

**CDL:** CDL-083 — H-CON-02 Panel Quorum Rules for Ejected Stake Treasury Distribution
        and REFUTATION Attribution
**Phase:** 1104 (prelock hardening + evidence assembly)
**Window:** 1102–1109
**Date:** 2026-04-28
**Ratification target:** Phase 1105

---

## 1. Scope and Purpose

This document assembles the ratification evidence for CDL-083. CDL-083 constitutionalises
the H-CON-02 panel quorum rules for ejected stake treasury distribution and REFUTATION
attribution, clearing the `CDL_HCON_02_DEPENDENCY` stub active since Phase 946.

Evidence covers:

1. Prelock assertion — CDL-083 was OPEN at the Phase 1103 introducing commit
2. CDL-083 Q1–Q5 resolution record (all resolved at opening, human-authorized 2026-04-28)
3. Pre-ratification checklist
4. Test coverage specification (tests executed Phase 1107)
5. Regression context at Phase 1104 boundary

---

## 2. Prelock Assertion: CDL-083 OPEN at Phase 1103 Commit

**Opening commit:** `da10991f` — `feat(cdl): open CDL-083 H-CON-02 panel quorum ejected stake (Phase 1103)`

**Verification command:**
```bash
git show da10991f:docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md \
  | grep "^\*\*Status:"
```

**Expected output:** `**Status:** OPEN`

**Result at Phase 1104 boundary:** `**Status:** OPEN` ✓

This confirms CDL-083 opened in the correct state at Phase 1103 and was not retroactively
mutated before prelock hardening.

`cdl_083_prelock_asserts_open_at_phase_1103_commit_da10991f`

---

## 3. Q1–Q5 Resolution Record

All five human-gate questions were resolved at opening (pre-authorized 2026-04-28):

| Q | Decision | Token |
|---|----------|-------|
| Q1 | ≥0.50 participation floor; hard minimum 2 voters | `q1_quorum_floor_geq_050_hard_minimum_2_voters` |
| Q2 | Exact 2/3 supermajority of participants, evaluated by integer arithmetic | `q2_vote_threshold_exact_two_thirds_supermajority` |
| Q3 | Proportional to all remaining members' stake at distribution epoch | `q3_distribution_proportional_all_remaining_members_stake_at_distribution_epoch` |
| Q4 | Upheld REFUTATION → REUSE_ATTRIBUTION_RATE (0.20) to refuting agent, epoch mint source; caller-filters | `q4_refutation_ecu_reuse_attribution_rate_epoch_mint_source_caller_filters_upheld` |
| Q5 | Ejected stake irrevocable; readmission starts fresh | `q5_ejected_stake_irrevocable_readmission_starts_fresh` |

Canon anchors: `epoch_state_runtime.py` (2/3 threshold); CDL-081 §4.2 (stake-proportional);
CDL-058 (re-admission); CDL-046 (ejection); CDL-V7 (Popperian gate).

---

## 4. Pre-Ratification Checklist

```
[x] CDL-083 opened at Phase 1103 — OPEN state confirmed at introducing commit da10991f
[x] CDL-083 Q1–Q5 all resolved at opening (human-authorized 2026-04-28)
[x] Constitutional log row inserted at Phase 1103 (CDL-083 row, status: open)
[x] Prelock hardening complete — Phase 1104 — §7 added to CDL-083 spec
[x] Ratification evidence document (this file) — Phase 1104
[x] Runtime mutation targets specified — §4.1–4.3 of CDL-083 spec
[x] Test coverage specification — §5 below
[ ] Phase 1105 Commit 1: runtime constants + REFUTATION path implemented (ilc_core/ only)
[ ] Phase 1105 Commit 2: CDL-083 OPEN → RATIFIED; log row updated (CDL env var)
[ ] Human ratification authorization — Phase 1105 — pending
```

Items through "test coverage specification" are satisfied at Phase 1104. The remaining items
execute at Phase 1105.

---

## 5. Test Coverage Specification (Phase 1107)

Tests will be written in `tests/test_phase_1107_h_con_02_panel_quorum_settle.py`.
Minimum 10 tests required.

| Test group | Coverage |
|-----------|---------|
| G1 — Runtime constants | `HCON02_QUORUM_FLOOR == Decimal("0.50")`; `HCON02_QUORUM_MINIMUM_VOTERS == 2`; `HCON02_VOTE_THRESHOLD_NUMERATOR == 2`; `HCON02_VOTE_THRESHOLD_DENOMINATOR == 3`; no float/rounded decimal threshold |
| G2 — Dependency tokens | `CDL_083_DEPENDENCY` token present; `CDL_HCON_02_DEPENDENCY` still present as historical marker (raise removed, token retained) |
| G3 — REFUTATION attribution | Upheld REFUTATION event produces `(refuting_agent_id, REUSE_ATTRIBUTION_RATE)` payout; amount is Decimal("0.20"); no NotImplementedError raised; refuted target creator is not paid |
| G4 — REFUTATION caller-filter contract | REFUTATION events in batch are by construction upheld; no `upheld` field on AttributionEvent (structural assertion) |
| G4b — REFUTATION recipient shape | Runtime event shape carries explicit `refuting_agent_id` or equivalent recipient field; tests prove `target_creator_id` is not treated as the payout recipient for REFUTATION |
| G5 — Version token | `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` updated to `"epoch_attribution_settle_runtime_1106.v0.2"` |
| G6 — CDL-083 spec state | CDL-083 spec exists; `**Status:** RATIFIED` present; `cdl_083_ratified_phase_1105` token present |
| G7 — CDL log state | CDL-083 row in constitutional log has `ratified` status |
| G8 — Q1/Q2 quorum floor constants | `HCON02_QUORUM_FLOOR` and `HCON02_QUORUM_MINIMUM_VOTERS` are positive; exact 2/3 vote threshold passes 2-of-3, 4-of-6, and 6-of-9 |
| G9 — No float leakage | CDL-083 fractional values use Decimal or integer numerator/denominator pairs; no float threshold constants |
| G10 — Prelock historical assertion | CDL-083 was OPEN at commit `da10991f` (git show assertion, same pattern as CDL-082 evidence) |

Minimum test count: 10 groups, at least 1 test per group = ≥10 tests. Additional tests
for edge cases (zero-member refutation, mixed batch with REUSE + REFUTATION) are encouraged.

---

## 6. Regression Context (Phase 1104 boundary)

### H-012 baseline

File: `tests/test_phase_0947_h012_epoch_attribution_settle.py`
Count: **31 tests** — all pass at Phase 1104 boundary
Key: `test_g6_refutation_raises_not_implemented` confirms `NotImplementedError` is still raised
     (CDL-083 runtime not yet implemented — Phase 1106 scope)

### Phase 1101 closure gate

File: `tests/test_phase_1101_window_945_1101_closure_gate.py`
Count: **25 tests** — all pass
Confirms: CDL-082 ratified, H-012 partial settle deployed, capsule v5.33 current.

---

## 7. Evidence Tokens

```
cdl_083_ratification_evidence_complete_phase_1104
cdl_083_prelock_asserts_open_at_phase_1103_commit_da10991f
cdl_083_q1_q5_all_resolved_at_opening_human_authorized_2026_04_28
cdl_083_prelock_hardening_complete_phase_1104
h012_settle_31_tests_pass_at_phase_1104_boundary
```
