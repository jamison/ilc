# CDL-077 WANT-HAVE/WANT-BLOCK Fetch — Opening 900 v0.1

Status: open
Date: 2026-04-27
Window: 899–905
Phase: 900

---

## 1. CDL Summary

CDL-077 ratifies the two-phase fetch protocol for truth primitive nodes:

- **WANT-HAVE** — lightweight CID-addressed availability probe
- **WANT-BLOCK** — rate-limited full record delivery

CDL-077 is the pull side of the CDL-036 dissemination contract (`"ILC leans pull, not push"`),
and the Layer 2 complement to CDL-076 (Layer 1 announcement gossip).

`cdl_077_is_the_pull_side_of_cdl_036`
`cdl_077_is_layer_2_complement_to_cdl_076_layer_1`

---

## 2. Motivation

CDL-076 (ratified Phase 897) enables truth primitive announcement gossip: peers learn that
a node exists (its CID, primitive type, and agent). CDL-076 delivers no record content.
A receiving peer that wants the full record has no constitutional mechanism to fetch it.

CDL-077 closes this gap. The two-phase design prevents full-record push (CDL-036 prohibition)
while enabling efficient, DoS-resistant pull:

1. **WANT-HAVE probe** (cheap): "Do you have node X?" → yes/no. No record content transmitted.
2. **WANT-BLOCK request** (expensive, rate-limited): "Give me node X." → full record delivered.

The two-phase structure limits the attack surface of WANT-BLOCK to peers that have already
provided a positive WANT-HAVE response, and allows independent rate limiting of the
content-delivery path.

---

## 3. Options

### Option A — Single-phase full-record fetch (rejected)
A single `POST /fetch` endpoint returns the full node record immediately.

**Rejection reason:** Creates a high-value DoS target — any peer can cause any server to
perform an LMDB read and full DAG-CBOR serialization for every request. No probe cost.

### Option B — Persistent cross-session rate limiter (rejected)
Rate limiter state is written to disk and survives process restarts.

**Rejection reason:** Out of scope for RC phase. Adds LMDB write path complexity to the
rate limiter. An in-process token bucket is sufficient for the current deployment scale.

### Option C — Two-phase probe+fetch with in-process per-identity rate limiter (selected)

```
POST /fetch/want-have  → {have: bool, node_id: str}  (no rate limit)
POST /fetch/want-block → full node record bytes        (rate limited per requester_id)
```

Rate limiter: in-process token bucket, keyed by `requester_id` (ML-DSA-65 agent_id from
CDL-042 globally flat namespace). Unforgeable — requester_id is a cryptographic identity.

`cdl_077_option_c_selected`
`want_have_is_unrate_limited_availability_probe`
`want_block_is_rate_limited_content_delivery`

---

## 4. Implementation Contract

### 4.1 Protocol paths

```
WANT_HAVE_PATH  = "/fetch/want-have"
WANT_BLOCK_PATH = "/fetch/want-block"
```

### 4.2 Request schema (JSON, both endpoints)

```json
{
  "node_id": "<CIDv1>",
  "requester_id": "<ML-DSA-65 agent_id>"
}
```

### 4.3 WANT-HAVE response

```json
{
  "have": true,
  "node_id": "<CIDv1>"
}
```

or

```json
{
  "have": false,
  "node_id": "<CIDv1>"
}
```

HTTP 200 in both cases (negative answer is a valid response, not an error).

### 4.4 WANT-BLOCK responses

| Case | HTTP | Body |
|------|------|------|
| Node found, not rate-limited | 200 | Full node record bytes (DAG-CBOR) |
| Node not found | 404 | `{"token": "fetch_node_not_found", "node_id": "..."}` |
| Rate limit exceeded | 429 | `{"token": "fetch_rate_limit_exceeded", "requester_id": "..."}` |
| Store not configured | 503 | `{"token": "fetch_store_not_configured"}` |
| Malformed request | 400 | `{"token": "<descriptive_token>"}` |

### 4.5 Rate limiter

```python
WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10  # per requester_id identity
```

In-process token bucket. Not persistent across process restarts.
Over-limit: HTTP 429 with `fetch_rate_limit_exceeded` token. No crash.

### 4.6 Activation

- `ILC_TRUTH_GRAPH_STORE_PATH` required for server to serve records.
  Absent: WANT-HAVE returns `{have: false}`, WANT-BLOCK returns 503.
- `ILC_D2D_GOSSIP_PEERS` (reused) lists peers for client-side fetch.
  Absent: `fetch_truth_primitive()` returns None without error.

### 4.7 Peer reuse

Client-side fetch uses `ILC_D2D_GOSSIP_PEERS` (same as CDL-076 announcement gossip).
The fetch server runs on a separate port from the gossip server (separate
`http_fetch_transport_runtime.py` module — gossip server path routing is gossip-type-keyed
and cannot dispatch fetch paths).

### 4.8 No LMDB write via fetch path

`handle_want_have_request()` performs a presence check only — no full LMDB read.
`handle_want_block_request()` performs a read only — no write.
The store is never mutated by a fetch operation.

`no_lmdb_write_in_fetch_path`

---

## 5. Module Tokens

**`ilc_core/network/d2d/truth_primitive_fetch_runtime.py`:**
```python
TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION = "truth_primitive_fetch_runtime_901.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"
WANT_HAVE_PATH = "/fetch/want-have"
WANT_BLOCK_PATH = "/fetch/want-block"
WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10
```

**`ilc_core/network/d2d/http_fetch_transport_runtime.py`:**
```python
HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_902.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
FETCH_RUNTIME_DEPENDENCY = "truth_primitive_fetch_runtime_901.v0.1"
```

---

## 6. Exclusion Tokens

```
no_surb_onion_routing_in_cdl_077            L4 privacy — future CDL
no_star_map_wiring_in_cdl_077               L3 — H-series, not this CDL
no_per_hop_ecu_micropayment_in_cdl_077      reputation-implicit model only
no_persistent_rate_limiter_in_cdl_077       in-process only
no_dht_in_cdl_077                           static peer config only
no_relay_fee_clearing_in_cdl_077            relay incentive CDL Phase 907+
```

---

## 7. Forward Obligations

| Obligation | Vehicle |
|------------|---------|
| Onion routing + SURB reply envelopes (L4 privacy) | Future CDL |
| Relay fee CDL: reputation-implicit incentive model | CDL-078, Phase 907+ |
| Persistent rate limiter (cross-restart) | Future CDL |
| star.map L3 integration | Future CDL, H-series |

---

## 8. Parent CDLs

- **CDL-036**: Pull-dominant dissemination contract (governing)
- **CDL-042**: Agent identity — globally flat namespace, ML-DSA-65 agent_id
- **CDL-075**: Truth primitive graph persistence — LMDB store being read
- **CDL-076**: Truth primitive announcement gossip — CDL-077 is its pull complement
