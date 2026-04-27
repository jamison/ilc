# CDL-078 Relay Incentive Constitutional Lock — Ratification Evidence (Phase 911)

Status: ratified
Date: 2026-04-27
Phase: 911
CDL: CDL-078
Opening document: docs/specs/ilc_cdl_078_relay_incentive_constitutional_lock_opening_907_v0.1.md

---

## 1. Ratification Summary

CDL-078 ratifies the relay incentive model for the ILC network. The implementation
covers Phases 907–910 of Window 906–912 and satisfies all 8 hard pass conditions
from the sequence lock (`docs/specs/ilc_phase_906_912_sequence_lock_v0.1.md`).

The selected option is **Option C** (serve-event epoch buffer → CDL-060 centrality
delta). Options A (per-hop ECU micro-payment) and B (negative signal for WANT-BLOCK
refusal) are rejected.

`cdl_078_ratified_phase_911`
`option_c_selected_serve_event_buffer_feeds_cdl_060`

---

## 2. Hard Pass Condition Verification

### Condition 1 — `routing_reputation_runtime.py` exists

**Result: PASS**

File: `ilc_core/network/d2d/routing_reputation_runtime.py`

Verified by `test_routing_reputation_runtime_exists()` in
`tests/test_phase_908_912_cdl_078_relay_incentive.py`.

---

### Condition 2 — Version and CDL dependency tokens present

**Result: PASS**

```python
ROUTING_REPUTATION_RUNTIME_VERSION = "routing_reputation_runtime_908.v0.1"
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
```

Also present in `truth_primitive_fetch_runtime.py`:
```python
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"
```

Verified by tests: `test_routing_reputation_runtime_version_token`,
`test_cdl_078_dependency_token`, `test_cdl_060_dependency_token`,
`test_cdl_077_dependency_token`, `test_cdl_078_dependency_in_fetch_runtime`.

---

### Condition 3 — `SERVE_CENTRALITY_DELTA` and `SERVE_CENTRALITY_MAX_PER_EPOCH` declared

**Result: PASS**

```python
SERVE_CENTRALITY_DELTA: float = 0.01
SERVE_CENTRALITY_MAX_PER_EPOCH: float = 0.10
```

Locked analytically per sequence lock §1 (Q1/Q2). Calibration rationale:
- `SERVE_CENTRALITY_DELTA = 0.01`: 1% of `CENTRALITY_SCORE_CAP` per successful serve.
  ~10 distinct serves per epoch to reach per-epoch cap. Reflects genuine network utility.
- `SERVE_CENTRALITY_MAX_PER_EPOCH = 0.10`: 10% cap prevents volume gaming. A node
  cannot dominate centrality purely through WANT-BLOCK throughput.

Verified by tests: `test_serve_centrality_delta_is_0_01`,
`test_serve_centrality_max_per_epoch_is_0_10`.

---

### Condition 4 — `record_serve_event()` accumulates in epoch buffer

**Result: PASS**

Implementation in `routing_reputation_runtime.py`:

```python
def record_serve_event(node_id: str, epoch: int, state: dict) -> None:
    try:
        with _state_lock:
            buf = _serve_buffer(state)
            epoch_buf = buf.setdefault(epoch, {})
            epoch_buf[node_id] = epoch_buf.get(node_id, 0) + 1
    except Exception:
        pass  # best-effort — never propagate
```

Properties verified:
- Single event increments `state["serve_buffer"][epoch][node_id]` to 1
- Two events for same node accumulate to 2
- Different nodes are independent (no cross-contamination)
- Different epochs stored independently
- Never raises on garbage input (empty node_id, negative epoch, None state)

Verified by tests: `test_record_serve_event_single`,
`test_record_serve_event_accumulates`, `test_record_serve_event_different_nodes_independent`,
`test_record_serve_event_different_epochs`, `test_record_serve_event_never_raises_on_bad_input`.

---

### Condition 5 — `flush_epoch_serve_events()` produces CDL-060 centrality delta calls

**Result: PASS**

Implementation contract:
```
for (node_id, count) in serve_buffer[epoch]:
    raw_delta = min(count × SERVE_CENTRALITY_DELTA, SERVE_CENTRALITY_MAX_PER_EPOCH)
    accumulate_centrality_delta(node_id, raw_delta, epoch, centrality_state)
serve_buffer[epoch] cleared after flush
flush receipt appended to flush_log
```

Properties verified:
- Single serve produces delta = `SERVE_CENTRALITY_DELTA` (0.01)
- 20 serves for same node → delta capped at `SERVE_CENTRALITY_MAX_PER_EPOCH` (0.10)
- Epoch buffer cleared after flush
- Flush receipt written to `state["flush_log"]`
- Empty epoch is a no-op (no `accumulate_centrality_delta` call)

Verified by tests: `test_flush_single_serve_produces_correct_delta`,
`test_flush_cap_enforced`, `test_flush_clears_epoch_buffer`,
`test_flush_writes_receipt_to_flush_log`, `test_flush_empty_epoch_is_noop`.

---

### Condition 6 — `handle_want_block_request()` wired: 200 → serve event recorded

**Result: PASS**

Wiring added at Phase 909 in `truth_primitive_fetch_runtime.py`:

```python
# CDL-078: record successful serve event for routing reputation (best-effort).
try:
    from ilc_core.network.d2d.routing_reputation_runtime import (
        record_serve_event,
        _global_reputation_state,
    )
    record_serve_event(node_id, int(time.time() // 60), _global_reputation_state)
except Exception:
    pass  # best-effort; WANT-BLOCK response is not affected
```

Wiring is:
- **Non-blocking**: wrapped in `try/except Exception: pass`
- **Non-critical**: WANT-BLOCK response always returned regardless
- **Scoped to 200 path**: after rate-limit check and store lookup succeed

Negative path verification:
- 404 (node not found): no serve event
- 429 (rate-limited): no serve event (rate check fires before store lookup)
- 503 (store not configured): no serve event (early return before record path)

Verified by tests: `test_want_block_success_records_serve_event`,
`test_want_block_404_no_serve_event`, `test_want_block_429_no_serve_event`,
`test_want_block_503_no_serve_event`.

---

### Condition 7 — No per-hop ECU micro-payment introduced

**Result: PASS**

Source scan of `ilc_core/network/d2d/routing_reputation_runtime.py`:

Forbidden terms not present: `transfer_ecu`, `ledger_write`, `ecu_transfer`,
`pay_ecu`, `deduct_ecu`.

The module contains no LMDB write, no ECU transfer, no ledger mutation. The
incentive is entirely reputation-implicit: serve → centrality rises → passive ECU
accrues at epoch boundary via existing ratified formula.

`no_per_hop_ecu_micropayment_confirmed_by_source_scan`

Verified by test: `test_no_ecu_transfer_in_routing_reputation_runtime`.

---

### Condition 8 — CDL-078 opened in CDL master log

**Result: PASS**

CDL-078 row present in `docs/specs/ilc_constitutional_decision_log_v0.1.md`:

```
opened_phase: 907 | opened_date: 2026-04-27
```

Verified by test: `test_cdl_078_row_in_master_log`.

---

## 3. CDL-060 Invariant Preservation

`flush_epoch_serve_events()` only calls `accumulate_centrality_delta()` with
non-negative deltas:
- `SERVE_CENTRALITY_DELTA = 0.01 > 0`
- `raw_delta = min(count × 0.01, 0.10)` — both bounds positive
- No path through the flush function can produce a negative delta

This upholds CDL-060's `_require_non_negative_float` invariant without amendment.

Verified by test: `test_flush_never_produces_negative_delta`.

`cdl_060_non_negative_delta_invariant_upheld`

---

## 4. CDL-077 Return Contract Preserved

The Phase 909 wiring patch is additive only. `handle_want_block_request()`:
- Signature unchanged: `(body, store, rate_limiter) → (int, bytes)`
- All 34 CDL-077 tests in `tests/test_phase_901_905_cdl_077_fetch.py` continue to pass
- The wiring is after the `return 200, record_bytes` path — serve event call
  does not block, delay, or alter the return value

`cdl_077_return_contract_unchanged`

---

## 5. No LMDB Write in Serve Event Path

Serve events accumulate exclusively in-process in `_global_reputation_state["serve_buffer"]`.
No write to the LMDB truth primitive store (`CDL-075`). The WANT-BLOCK handler
remains read-only with respect to all persistent stores.

`no_lmdb_write_in_serve_event_path_confirmed`

---

## 6. Test Summary

| Test file | Tests | Status |
|-----------|-------|--------|
| `tests/test_phase_908_912_cdl_078_relay_incentive.py` | 28 | All pass (1 scope guard skips before commit; 28/28 after commit `6e4a5eec`) |
| `tests/test_phase_901_905_cdl_077_fetch.py` | 34 | All pass (CDL-077 regression) |

Total new tests in Window 906–912: **28**
Total passing tests across full suite: **393**

---

## 7. Rejected Options

**Option A — Per-hop ECU micro-payment clearing:** Rejected. Requires new micro-payment
clearing mechanism, new ledger writes, new dispute surface. Inconsistent with CDL-036
pull-dominant philosophy. Creates double-counting risk with passive ECU formula.

**Option B — Explicit negative signal for WANT-BLOCK refusal:** Rejected. CDL-060
`accumulate_centrality_delta()` only accepts non-negative deltas. Introducing negative
deltas would require CDL-060 amendment (out of scope). CDL-V1 temporal decay already
erodes unused centrality scores — absence of positive signal is sufficient implicit penalty.

`option_a_rejected_per_hop_ecu_micropayment`
`option_b_rejected_negative_delta_out_of_scope`
`option_c_selected_cdl_078`

---

## 8. Exclusion Tokens (confirmed)

```
no_per_hop_ecu_micropayment_in_cdl_078        confirmed — source scan, test 7
no_negative_serve_signal_in_cdl_078           confirmed — CDL-060 invariant upheld
no_new_token_in_cdl_078                       confirmed — existing CDL-060 + passive ECU
no_persistent_serve_log_in_cdl_078            confirmed — in-process epoch buffer only
no_lmdb_write_in_serve_event_path             confirmed — no persistent store write
no_cdl_060_amendment_in_cdl_078              confirmed — only API consumed, not amended
```

---

## 9. Ratification Authorization

CDL-078 is hereby ratified at Phase 911 (2026-04-27).

Ratification is authorized by satisfaction of all 8 hard pass conditions defined in
the Window 906–912 sequence lock and corroborated by 28 passing tests.

`cdl_078_ratified_911`
`window_906_912_hard_pass_conditions_all_satisfied`
`relay_incentive_model_constitutionally_locked`
`l5_relay_incentive_reputation_implicit_model_ratified`
