# ILC Window 906–912 Sequence Lock

Status: locked
Date: 2026-04-27
Window: 906–912
Topic: CDL-078 — Relay incentive constitutional lock (Layer 5 network delivery)

`window_906_912_commissioned`
`cdl_078_relay_incentive_constitutional_lock_layer_5`

---

## 1. Authorization Basis

This window is authorized by:

- `docs/specs/ilc_antigravity_context_capsule_v5.28.md` §8:
  *"CDL-078: Relay fee CDL — reputation-implicit model, not per-hop ECU — Phase 906+ — Design intent locked; CDL not yet opened"*
- Window 899–905 closure gate `eeb0eef8`:
  `relay_fee_cdl_is_next_l5_obligation`,
  `relay_incentive_model_is_reputation_implicit_not_per_hop_ecu`
- Forward planning doc `docs/specs/ilc_window_906_929_forward_planning_v0.1.md` §3

Pre-phase open questions resolved before this sequence lock:

**Q1: Does SIM-RELAY-01 need to run, or can serve_centrality_delta be locked analytically?**

Answer: Lock analytically. The CDL-060 centrality delta pipeline already uses
`accumulate_centrality_delta(node_id, delta, epoch, state)` with delta bounded by
`_normalized_delta()` and `CENTRALITY_SCORE_CAP = 1.0`. A fixed `SERVE_CENTRALITY_DELTA`
constant, calibrated to be smaller than a direct truth primitive submission delta,
is sufficient for RC phase. SIM-RELAY-01 is reserved for post-RC1 calibration tuning;
it is named here as a forward obligation but does not gate this window.

**Q2: Is there a per-epoch cap on serve-event centrality contribution?**

Answer: Yes. A `SERVE_CENTRALITY_MAX_PER_EPOCH` constant caps total serve-event
contribution per node per epoch. This prevents a fast-serving node from dominating
centrality purely through WANT-BLOCK volume, decoupling volume from epistemic merit.
Calibration: `SERVE_CENTRALITY_MAX_PER_EPOCH = 0.10` (10% of CENTRALITY_SCORE_CAP per epoch).

**Q3: Do dropped/refused WANT-BLOCK requests produce a negative centrality signal?**

Answer: No direct negative signal. The absence of a positive serve-event signal is
the implicit cost — a node that never serves accumulates no routing reputation
contribution from the fetch path. This is simpler and avoids a new negative delta
type in the CDL-060 pipeline, which only handles non-negative deltas. The CDL-036
temporal decay (CDL-V1) already erodes unused centrality scores over time.
Explicit negative routing reputation signals are deferred to CDL-080+.

`sim_relay_01_is_forward_obligation_not_gate`
`serve_centrality_delta_locked_analytically`
`no_negative_serve_signal_in_cdl_078`
`cdl_v1_temporal_decay_provides_implicit_non_serve_penalty`

---

## 2. Architectural Grounding

### 2.1 Position in 5-layer architecture

CDL-078 closes the L5 constitutional layer. L1 and L2 are ratified. L5 (relay
incentives) cannot be implemented without L2 (WANT-BLOCK) as the serve event source.

| Layer | CDL | Status |
|-------|-----|--------|
| L1 — Announcement gossip | CDL-076 | Ratified (Phase 897) |
| L2 — WANT-HAVE/WANT-BLOCK fetch | CDL-077 | Ratified (Phase 904) |
| **L5 — Relay incentives (this window)** | **CDL-078** | **This window** |
| L3 — star.map N-gram routing | CDL-079 | Window 921–929 |
| L4 — Onion routing + SURB | Future | Post-L3 |

CDL-078 does not implement L3 or L4. It closes L5's constitutional ambiguity using
only the infrastructure already ratified.

### 2.2 Governing economic framework

The relay incentive model is **reputation-implicit**:

1. Node A successfully serves a WANT-BLOCK for `node_id` to Node B.
2. A serve event is recorded locally: `(node_id, epoch)`.
3. At epoch close, accumulated serve events emit centrality delta signals into
   the CDL-060 centrality delta gossip pipeline.
4. CDL-060 gossip propagates the centrality delta to peers.
5. Passive ECU (CDL-075 ratified formula) accrues at epoch boundary:
   `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`

No new token, no new ledger entry, no per-hop micro-payment. ECU accrues through
existing ratified mechanisms. CDL-078 adds only the serve-event → centrality delta
bridge.

`cdl_078_closes_l5_using_existing_cdl_060_and_passive_ecu_infrastructure`
`no_new_token_in_cdl_078`
`no_per_hop_micropayment_in_cdl_078`

### 2.3 Interaction with CDL-077 (WANT-BLOCK handler)

`handle_want_block_request()` (Phase 901) returns `(200, record_bytes)` on success.
CDL-078 introduces a serve event registration call at this success path. The call
is non-blocking and non-critical: if the serve event recording fails for any reason,
the WANT-BLOCK response still succeeds. Serve event recording is best-effort.

`serve_event_recording_is_best_effort_non_blocking`

### 2.4 Serve event batching strategy

Serve events are accumulated in-process (not persisted to LMDB) and converted to
centrality delta calls at epoch close. This mirrors the CDL-060
`ACCUMULATION_MODEL = "epoch_boundary_atomic"` design and keeps the CDL-077
fetch path fully decoupled from disk I/O.

---

## 3. Window Scope

### 3.1 In scope

| Phase | Topic |
|-------|-------|
| 906 | Sequence lock (this document) |
| 907 | CDL-078 opening document |
| 908 | `ilc_core/network/d2d/routing_reputation_runtime.py` — serve event recorder + epoch flush → CDL-060 |
| 909 | Wire serve events: patch `handle_want_block_request()` to call `record_serve_event()` on 200 response |
| 910 | Tests (`tests/test_phase_908_912_cdl_078_relay_incentive.py`) |
| 911 | CDL-078 ratification + coherence report + capsule v5.29 |
| 912 | Closure gate |

### 3.2 Explicit exclusions

```
no_sim_relay_01_required_in_window_906_912        analytic lock; SIM deferred
no_negative_serve_signal_in_window_906_912        absent-signal implicit penalty only
no_per_hop_ecu_micropayment_in_window_906_912     reputation-implicit model only
no_new_token_or_ledger_in_window_906_912          existing CDL-060 + passive ECU
no_persistent_serve_log_in_window_906_912         in-process epoch buffer only
no_star_map_wiring_in_window_906_912              L3 deferred to Window 921+
no_onion_routing_in_window_906_912                L4 deferred
no_hb_002_in_window_906_912                      Window 913+
no_cdl_070_in_window_906_912                     SIM-MONETARY-01 prerequisite
no_new_cdl_beyond_078_in_window_906_912          one CDL only
```

---

## 4. Hard Pass Conditions

The Phase 912 closure gate must verify all 8 conditions:

| # | Condition |
|---|-----------|
| 1 | `ilc_core/network/d2d/routing_reputation_runtime.py` exists |
| 2 | `ROUTING_REPUTATION_RUNTIME_VERSION` and `CDL_078_DEPENDENCY` tokens present |
| 3 | `SERVE_CENTRALITY_DELTA` and `SERVE_CENTRALITY_MAX_PER_EPOCH` constants declared |
| 4 | `record_serve_event(node_id, epoch, state)` accumulates serve events in epoch buffer |
| 5 | `flush_epoch_serve_events(epoch, state)` produces centrality delta calls into CDL-060 `accumulate_centrality_delta()` |
| 6 | `handle_want_block_request()` calls `record_serve_event()` on HTTP 200 response (best-effort, non-blocking) |
| 7 | No per-hop ECU micro-payment mechanism introduced anywhere in this window |
| 8 | CDL-078 opened (Phase 907) and ratified (Phase 911) in CDL master log |

---

## 5. Phase Detail

### Phase 907 — CDL-078 Opening

**Deliverables:**
- CDL-078 row inserted in `docs/specs/ilc_constitutional_decision_log_v0.1.md` as `open`
- `docs/specs/ilc_cdl_078_relay_incentive_constitutional_lock_opening_907_v0.1.md`

**CDL-078 scope statement:**
CDL-078 ratifies the relay incentive model for the ILC network. Nodes that
successfully serve WANT-BLOCK fetch requests earn routing reputation through centrality
delta accumulation. Centrality feeds the existing passive ECU formula (CDL-060, Phase 542).
No per-hop ECU micro-payment is introduced. The incentive is implicit in the existing
economic stack: serve → centrality score rises → passive ECU accrues; do not serve →
centrality score decays via CDL-V1 temporal decay.

**Options under consideration:**
- Option A (rejected): per-hop ECU micro-payment clearing
- Option B (rejected): explicit negative reputation signal for WANT-BLOCK refusal
- **Option C (selected):** serve event → in-process epoch buffer → CDL-060 centrality
  delta at epoch close; no negative signal; temporal decay provides implicit penalty

**Parent CDLs:** CDL-036 / CDL-060 / CDL-077

---

### Phase 908 — Routing Reputation Runtime

**File:** `ilc_core/network/d2d/routing_reputation_runtime.py`

**Required tokens:**
```python
ROUTING_REPUTATION_RUNTIME_VERSION = "routing_reputation_runtime_908.v0.1"
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
SERVE_CENTRALITY_DELTA = 0.01
SERVE_CENTRALITY_MAX_PER_EPOCH = 0.10
```

**Core functions:**
```python
def record_serve_event(node_id: str, epoch: int, state: dict) -> None:
    """
    Record a successful WANT-BLOCK serve event in the epoch buffer.
    state["serve_buffer"][epoch][node_id] += 1
    Non-blocking. Never raises. Best-effort.
    """

def flush_epoch_serve_events(epoch: int, state: dict, centrality_state: dict) -> dict:
    """
    At epoch close, convert accumulated serve events to centrality deltas.
    For each (node_id, count) in serve_buffer[epoch]:
        raw_delta = min(count × SERVE_CENTRALITY_DELTA, SERVE_CENTRALITY_MAX_PER_EPOCH)
        accumulate_centrality_delta(node_id, raw_delta, epoch, centrality_state)
    Clears serve_buffer[epoch] after flush.
    Returns flush receipt: {epoch, nodes_flushed, total_delta_emitted}
    """

def new_reputation_state() -> dict:
    """
    Return a fresh routing reputation state dict:
    {"serve_buffer": {}, "flush_log": []}
    """
```

**Dep-chain guard:** verify `CDL_060_GOSSIP_RUNTIME_VERSION` and
`TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION` at import time.

---

### Phase 909 — Serve Event Wiring

**File:** `ilc_core/network/d2d/truth_primitive_fetch_runtime.py` (patch)

Wire `record_serve_event()` into `handle_want_block_request()` at the success path.

The patch is additive only — existing function signature and return contract unchanged.

```python
# At the 200 success path in handle_want_block_request():
try:
    from ilc_core.network.d2d.routing_reputation_runtime import record_serve_event
    record_serve_event(node_id, _current_epoch(), _global_reputation_state)
except Exception:
    pass  # best-effort; WANT-BLOCK response is not affected
```

`_current_epoch()` returns `int(time.time() // 60)` — validation epoch (1-minute cadence,
consistent with the established CDL-071 Tier 2 epoch definition).

`_global_reputation_state` is a module-level singleton dict (initialized lazily on first call).
The singleton pattern follows the same approach as `_rate_limiter` in `FetchRateLimiter`.

**Version token:** `TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION` remains
`"truth_primitive_fetch_runtime_901.v0.1"` — this is a best-effort wiring extension,
not a new module version. Add `CDL_078_DEPENDENCY` as a new module constant.

---

### Phase 910 — Tests

**File:** `tests/test_phase_908_912_cdl_078_relay_incentive.py`

**Commit subject (for scope guard):**
`"feat(g8): phase 906-910 cdl-078 relay incentive reputation-implicit model"`

**Test coverage (minimum 20 tests):**

| Group | Tests |
|-------|-------|
| 1. Module existence + tokens | runtime file exists; version token; CDL-078/060/077 dep tokens; delta constants |
| 2. record_serve_event | single event → buffer incremented; two events same node → count 2; different nodes independent |
| 3. flush_epoch_serve_events | single serve → delta = SERVE_CENTRALITY_DELTA; max cap enforced; flush clears buffer; flush log written |
| 4. Per-epoch cap | N × SERVE_CENTRALITY_DELTA > MAX_PER_EPOCH → capped at MAX_PER_EPOCH |
| 5. handle_want_block_request wired | 200 success → serve event recorded; 404 no event; 429 no event; 503 no event |
| 6. No negative signal | refused WANT-BLOCK (404/429/503) does not produce negative centrality delta |
| 7. No per-hop ECU | no ECU transfer call anywhere in routing_reputation_runtime.py |
| 8. centrality_state integration | flush → accumulate_centrality_delta called with correct args |
| 9. CDL-078 in master log | CDL master log contains CDL-078 row with opened_phase: 907 |
| 10. Commit scope guard | Phase 910 commit touches only `ilc_core/network/d2d/` + `tests/` + `docs/` |

---

### Phase 911 — CDL-078 Ratification + Coherence Report + Capsule v5.29

**CDL-078 ratification:**
- CDL master log row updated from `open` → `ratified`
- Ratification evidence: `docs/specs/ilc_cdl_078_relay_incentive_ratification_evidence_911_v0.1.md`
- Atomic commit with `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=911`

**Coherence report:** `docs/specs/ilc_integration_coherence_report_911_v0.1.md`
- Key check: `handle_want_block_request()` return contract unchanged — CDL-077 tests still pass
- Key check: serve event recording is best-effort — no exception propagates to caller
- Key check: centrality delta is non-negative (CDL-060 invariant upheld)
- Key check: LMDB store not written by serve event path

**Capsule:** `docs/specs/ilc_antigravity_context_capsule_v5.29.md` — supersedes v5.28

**Estimated test count:**

| Scope | Tests |
|-------|-------|
| Window 906–912 (CDL-078) | ~20 |
| Prior windows | 365 |
| **Total (estimated)** | **~385** |

---

### Phase 912 — Closure Gate

**File:** `docs/specs/ilc_window_906_912_closure_gate_912_v0.1.md`

On PASS emits:
```
window_906_912_closed
capsule_v5_29_is_current_frontier
cdl_078_ratified
l5_relay_incentive_model_constitutionally_locked
hb_002_is_next_window_primary_obligation
```

---

## 6. Forward Obligations Carried Forward

| Obligation | Next window | Evidence basis |
|------------|-------------|----------------|
| HB-002: P2P bootstrap distribution | Window 913–920 | Forward planning doc §4 |
| SIM-RELAY-01: serve-rate calibration | Post-RC1 | Named as forward obligation; not gate |
| star.map L3 routing (CDL-079) | Window 921–929 | Forward planning doc §5 |
| Onion routing + SURB (L4) | Post-L3 | H-series designed |
| CDL-001 packaging track | Pre-launch | genesis_blocker |
| CDL-070 PQ migration ceremony | Deep audit | SIM-MONETARY-01 prerequisite |

---

## 7. Sequence Constraints

1. Phase 907 (CDL-078 open) must precede Phase 908 (runtime)
2. Phase 908 (runtime) must precede Phase 909 (wiring patch)
3. Phase 909 (wiring) must precede Phase 910 (tests)
4. Phase 910 (tests passing) must precede Phase 911 (ratification)
5. Phase 911 (ratification) must precede Phase 912 (closure gate)
6. No HB-002 work, no star.map wiring, no negative serve signals in this window

---

## 8. Governing Tokens

```
window_906_912_commissioned
cdl_078_closes_l5_using_existing_cdl_060_and_passive_ecu_infrastructure
no_new_token_in_cdl_078
no_per_hop_micropayment_in_cdl_078
serve_event_recording_is_best_effort_non_blocking
sim_relay_01_is_forward_obligation_not_gate
serve_centrality_delta_locked_analytically
no_negative_serve_signal_in_cdl_078
cdl_v1_temporal_decay_provides_implicit_non_serve_penalty
```
