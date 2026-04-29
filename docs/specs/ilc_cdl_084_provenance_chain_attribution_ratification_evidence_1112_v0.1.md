# CDL-084 Ratification Evidence — Phase 1112

**CDL:** CDL-084 — PROVENANCE Chain Attribution
**Phase:** 1112 (prelock hardening + evidence assembly)
**Window:** 1110-1117
**Date:** 2026-04-29
**Ratification target:** Phase 1113

---

## 1. Scope and Purpose

This document specifies the ratification evidence required for CDL-084. CDL-084
constitutionalises ECU attribution for PROVENANCE derivation chains while keeping settlement
pure: callers provide an explicit nearest-first ancestor chain, and settlement performs no
graph queries.

Evidence covers:

1. Runtime constants and dependency tokens after ratification.
2. `AttributionEvent` shape and validation rules.
3. Decimal-only geometric decay payout behavior.
4. Duplicate-node and duplicate-creator handling.
5. Caller-only contract structure.
6. CDL-084 spec/log state and historical OPEN assertion.
7. No float leakage in PROVENANCE payouts.

---

## 2. Q1-Q10 Resolution Record

All ten questions were resolved before opening and human-authorized on 2026-04-29.

| Q | Decision | Token |
|---|----------|-------|
| Q1 | PROVENANCE triggers ECU via caller-only PROVENANCE event contract | `q1_provenance_triggers_ecu_caller_only_contract` |
| Q2 | Geometric decay with `PROVENANCE_DECAY_ALPHA = Decimal("0.5")`, provisional pending SIM-PROVENANCE-01 | `q2_geometric_decay_alpha_decimal_0_5_provisional` |
| Q3 | `PROVENANCE_MAX_DEPTH = 3`; immediate parent is hop 1 | `q3_max_depth_3_hop_1_is_immediate_parent` |
| Q4 | Ancestor node creator receives ECU | `q4_ancestor_creator_receives_ecu` |
| Q5 | Fresh per-event state; `visited_creators` nearest-hop-wins | `q5_fresh_per_event_visited_creators_nearest_hop_wins` |
| Q6 | Explicit nearest-first chain payload; no graph queries in settle | `q6_explicit_chain_payload_nearest_first_pure_settle` |
| Q7 | Duplicate node ID raises; duplicate creator ID nearest-hop-wins | `q7_duplicate_node_id_raises_nearest_creator_wins` |
| Q8 | Epoch mint source; SIM-PROVENANCE-01 required before alpha locks | `q8_epoch_mint_source_sim_provenance_01_required` |
| Q9 | Replace float alpha with `Decimal("0.5")` before runtime use | `q9_float_kill_decimal_literal_0_5` |
| Q10 | Missing/empty chain raises explicit validation errors | `q10_none_raises_missing_empty_raises_empty` |

---

## 3. Pre-Ratification Checklist

```
[ ] CDL-084 opened at Phase 1111 with Status: OPEN
[ ] CDL-084 log row inserted with opened_phase: 1111 and status: open
[ ] Phase 1112 historical OPEN assertion recorded
[ ] Phase 1113 Commit 1: types/runtime constants and event shape implemented, no CDL env var
[ ] Phase 1113 Commit 2: CDL-084 OPEN -> RATIFIED and log row updated, CDL env var used
[ ] Phase 1114: PROVENANCE settlement path implemented
[ ] Phase 1115: evidence tests pass with at least 30 tests
```

---

## 4. Test Coverage Specification

Tests will be written in `tests/test_phase_1115_cdl_084_provenance_chain_attribution.py`.
Minimum: 30 tests.

| Group | Count | Coverage |
|-------|-------|----------|
| G1 — Runtime constants | 4 | `PROVENANCE_MAX_DEPTH == 3` and `int`; `PROVENANCE_DECAY_ALPHA == Decimal("0.5")` and `Decimal`; alpha is not `float`; `REUSE_ATTRIBUTION_RATE == Decimal("0.20")` |
| G2 — Dependency tokens | 3 | `CDL_084_DEPENDENCY`, `CDL_084_TYPES_DEPENDENCY`, and `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1114.v0.3"` |
| G3 — `AttributionEvent` shape | 2 | `provenance_chain` field present; dataclass fields exactly match the ratified order |
| G4 — Q10 missing/empty validation | 2 | `None` chain raises `provenance_event_missing_chain`; empty chain raises `provenance_event_empty_chain` |
| G5 — Q7 duplicate node validation | 1 | Duplicate `node_id` raises `provenance_chain_contains_duplicate_node_id` |
| G6 — Single-hop payout | 3 | Hop 1 payout equals `REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA`; payout is `Decimal`; correct creator paid |
| G7 — Multi-hop payout | 3 | Three-hop payouts use alpha powers 1, 2, and 3; over-depth chain truncates at depth 3; all amounts are `Decimal` |
| G8 — Duplicate creator handling | 2 | Same creator at hop 1 and hop 3 is paid once at hop-1 rate; distinct creators are paid independently |
| G9 — Caller-only contract | 1 | PROVENANCE event shape has no `upheld` field and no runtime REUSE/PROVENANCE cross-event detector |
| G10 — CDL-084 spec and log state | 2 | CDL-084 spec is RATIFIED; CDL log row has `ratified_phase: 1113` |
| G11 — Historical prelock assertion | 1 | `git show <phase_1111_introducing_commit>:...opening_1111...` contains `**Status:** OPEN` |
| G12 — No float leakage | 2 | Alpha is `Decimal`, not `float`; all PROVENANCE payouts are `Decimal` |
| G13 — Distribution and truncation edge cases | 3 | Empty descendants do not matter; chain length exactly 3 pays 3 entries; chain length 4 pays no hop-4 entry |
| G14 — Validation hardening | 2 | Malformed chain item shape raises stable error; non-string node or creator IDs raise stable errors if Phase 1114 adopts explicit type validation |

Expected minimum count: 31 tests if all groups are implemented. If Phase 1114 chooses not to
validate malformed tuple shape or non-string IDs explicitly, G14 may be replaced with two
additional CDL/log or mixed-batch regression tests to preserve the 30-test minimum.

---

## 5. Required Regression Context

Phase 1115 must also run:

```bash
PATH=.venv/bin:$PATH python3 -m pytest \
  tests/test_phase_0947_h012_epoch_attribution_settle.py \
  tests/test_phase_1107_h_con_02_panel_quorum_settle.py \
  -q
```

Expected current baseline at Phase 1111: combined `61 passed`.

---

## 6. Evidence Tokens

```
cdl_084_ratification_evidence_spec_published_phase_1111
cdl_084_g1_g14_evidence_groups_defined
cdl_084_phase_1115_minimum_30_tests_required
sim_provenance_01_required_before_alpha_locked
provenance_decimal_no_float_leakage_required
```
