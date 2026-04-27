# CDL-078 Relay Incentive Constitutional Lock — Opening 907 v0.1

Status: open
Date: 2026-04-27
Window: 906–912
Phase: 907

---

## 1. CDL Summary

CDL-078 ratifies the relay incentive model for the ILC network: the constitutional
definition of how serving WANT-BLOCK fetch requests (CDL-077) earns routing reputation,
and how that reputation feeds the existing passive ECU formula.

The model is **reputation-implicit**: no per-hop micro-payment, no new token, no new
ledger. Serving well → centrality score rises → passive ECU accrues. Not serving → score
decays via CDL-V1 temporal decay.

`cdl_078_is_layer_5_relay_incentive_lock`
`reputation_implicit_model_no_per_hop_micropayment`

---

## 2. Motivation

CDL-077 (Layer 2, ratified Phase 904) enables WANT-BLOCK fetch. Nodes now have the
infrastructure to serve truth primitive node records to peers on demand. However, there
is no constitutional definition of what serving earns. Without CDL-078:

- Nodes have no ratified incentive to serve WANT-BLOCK requests
- The relationship between serving and ECU accrual is design intent, not law
- The CDL-060 centrality delta pipeline has no ratified feed from the fetch path

CDL-078 closes this gap by:
1. Defining `SERVE_CENTRALITY_DELTA` — the unit centrality credit per successful serve
2. Defining `SERVE_CENTRALITY_MAX_PER_EPOCH` — the per-node cap preventing volume gaming
3. Wiring `handle_want_block_request()` success → `record_serve_event()` →
   `flush_epoch_serve_events()` → `accumulate_centrality_delta()` (CDL-060)

---

## 3. Options

### Option A — Per-hop ECU micro-payment clearing (rejected)

Each WANT-BLOCK serve triggers a direct ECU transfer from requester to server.

**Rejection reason:** Requires a new micro-payment clearing mechanism — new ledger
writes, new dispute surface, new protocol complexity. Inconsistent with CDL-036
pull-dominant philosophy. The existing passive ECU formula already rewards centrality;
a separate payment layer is redundant and creates double-counting risk.

### Option B — Explicit negative signal for WANT-BLOCK refusal (rejected)

A refused or dropped WANT-BLOCK (404/429/absent) produces a negative centrality delta.

**Rejection reason:** CDL-060 `accumulate_centrality_delta()` only accepts
non-negative deltas (`_require_non_negative_float`). Introducing negative deltas would
require amending CDL-060, which is out of scope. The CDL-V1 temporal decay already
erodes unused centrality scores — the absence of a positive serve signal is a
sufficient implicit penalty within the existing framework.

### Option C — Serve-event epoch buffer → CDL-060 centrality delta (selected)

```
WANT-BLOCK 200 response
    → record_serve_event(node_id, epoch, state)          [in-process, best-effort]
    → state["serve_buffer"][epoch][node_id] += 1

At epoch close:
    → flush_epoch_serve_events(epoch, state, centrality_state)
    → delta = min(count × SERVE_CENTRALITY_DELTA, SERVE_CENTRALITY_MAX_PER_EPOCH)
    → accumulate_centrality_delta(node_id, delta, epoch, centrality_state)  [CDL-060]
```

`cdl_078_option_c_selected`
`serve_event_buffer_feeds_cdl_060_at_epoch_close`

---

## 4. Implementation Contract

### 4.1 Constants

```python
SERVE_CENTRALITY_DELTA = 0.01          # centrality credit per successful serve
SERVE_CENTRALITY_MAX_PER_EPOCH = 0.10  # cap per node per epoch (prevents volume gaming)
```

Calibration rationale:
- `SERVE_CENTRALITY_DELTA = 0.01` — one serve contributes 1% of CENTRALITY_SCORE_CAP.
  A node must successfully serve ~10 distinct nodes per epoch to reach the per-epoch cap.
  This ensures routing reputation reflects genuine network utility, not raw throughput.
- `SERVE_CENTRALITY_MAX_PER_EPOCH = 0.10` — 10% of CENTRALITY_SCORE_CAP per epoch.
  A node cannot dominate centrality purely through WANT-BLOCK volume.

### 4.2 Module tokens

**`ilc_core/network/d2d/routing_reputation_runtime.py`:**
```python
ROUTING_REPUTATION_RUNTIME_VERSION = "routing_reputation_runtime_908.v0.1"
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
SERVE_CENTRALITY_DELTA = 0.01
SERVE_CENTRALITY_MAX_PER_EPOCH = 0.10
```

**`ilc_core/network/d2d/truth_primitive_fetch_runtime.py` (wiring extension):**
```python
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"
```

### 4.3 Serve event state shape

```python
{
    "serve_buffer": {
        <epoch: int>: {<node_id: str>: <count: int>, ...},
        ...
    },
    "flush_log": [
        {"epoch": int, "nodes_flushed": int, "total_delta_emitted": float},
        ...
    ]
}
```

### 4.4 Epoch definition

Validation epoch: `int(time.time() // 60)` — 1-minute cadence, consistent with
CDL-071 Tier 2 epoch definition (established Phase 851).

### 4.5 Non-blocking wiring contract

`record_serve_event()` must never raise. All exceptions are swallowed internally.
The WANT-BLOCK response is the primary function; serve event recording is secondary.
If recording fails (e.g., state dict mutation error), the 200 response still returns.

### 4.6 No LMDB write in serve event path

Serve events accumulate in-process only. No write to the LMDB truth primitive store,
no write to any other persistent store.

`no_lmdb_write_in_serve_event_path`

---

## 5. Exclusion Tokens

```
no_per_hop_ecu_micropayment_in_cdl_078        reputation-implicit only
no_negative_serve_signal_in_cdl_078           temporal decay provides implicit penalty
no_new_token_in_cdl_078                       existing CDL-060 + passive ECU
no_persistent_serve_log_in_cdl_078            in-process epoch buffer only
no_lmdb_write_in_serve_event_path             fetch path remains read-only
no_cdl_060_amendment_in_cdl_078              CDL-060 unchanged; only its API is called
```

---

## 6. Forward Obligations

| Obligation | Vehicle |
|------------|---------|
| SIM-RELAY-01: serve-rate → centrality delta calibration tuning | Post-RC1 CDL amendment if warranted |
| Negative routing reputation signals | CDL-080+ |
| Persistent serve event log (cross-restart) | Future CDL |

---

## 7. Parent CDLs

- **CDL-036**: Pull-dominant dissemination contract (governing)
- **CDL-060**: Centrality delta gossip pipeline (extended — serve events feed it)
- **CDL-077**: WANT-HAVE/WANT-BLOCK fetch (serve event source)
