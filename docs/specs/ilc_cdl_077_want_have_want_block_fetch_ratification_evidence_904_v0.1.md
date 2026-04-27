# CDL-077 WANT-HAVE/WANT-BLOCK Fetch — Ratification Evidence 904 v0.1

Status: Phase-904 ratification evidence artifact
Date: 2026-04-27
Window: 899–905
Phase: 904

## 1. Purpose and scope

This artifact ratifies CDL-077 and records the selected WANT-HAVE/WANT-BLOCK two-phase
fetch contract for Window 899–905.

CDL-077 ratifies the pull protocol only. Onion routing/SURB privacy (L4) and relay fee
economics (L5) are explicitly deferred to future CDLs.

## 2. Ratified decision

CDL-077 ratifies **Option C — two-phase probe+fetch with in-process per-identity rate limiter.**

Rejected options:
- **Option A** — single-phase full-record fetch (violates DoS prevention intent — no probe cost)
- **Option B** — persistent cross-session rate limiter (out of scope for RC phase; adds write
  path complexity)

The ratified answer:
- WANT-HAVE: `POST /fetch/want-have` → `{have: bool, node_id: str}` — no rate limit, no record
- WANT-BLOCK: `POST /fetch/want-block` → full node record bytes — rate limited per requester_id
- Rate limiter: in-process token bucket, `WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10` per identity
- `requester_id` is ML-DSA-65 agent_id (CDL-042 globally flat namespace)
- No LMDB write via fetch path — presence check + read only
- `ILC_D2D_GOSSIP_PEERS` absent → `fetch_truth_primitive()` returns None without error
- `ILC_TRUTH_GRAPH_STORE_PATH` absent on server → 200 `{have: false}` for WANT-HAVE, 503 for WANT-BLOCK
- Relay incentive model: reputation-implicit, not per-hop ECU micro-payment

`cdl_077_option_c_ratified`
`want_have_is_unrate_limited_availability_probe`
`want_block_is_rate_limited_content_delivery`
`relay_incentive_model_is_reputation_implicit_not_per_hop_ecu`
`no_lmdb_write_in_fetch_path`

## 3. Evidence basis

- Sequence lock: `docs/specs/ilc_phase_899_905_sequence_lock_v0.1.md`
- CDL-077 opening: `docs/specs/ilc_cdl_077_want_have_want_block_fetch_opening_900_v0.1.md`
- Fetch runtime: `ilc_core/network/d2d/truth_primitive_fetch_runtime.py`
  - `TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION = "truth_primitive_fetch_runtime_901.v0.1"`
  - `CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"`
  - `WANT_HAVE_PATH = "/fetch/want-have"`, `WANT_BLOCK_PATH = "/fetch/want-block"`
  - `WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10`
- HTTP fetch transport: `ilc_core/network/d2d/http_fetch_transport_runtime.py`
  - `HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_902.v0.1"`
  - `FETCH_RUNTIME_DEPENDENCY = "truth_primitive_fetch_runtime_901.v0.1"`
- Tests: `tests/test_phase_901_905_cdl_077_fetch.py` — 34 tests, all pass

## 4. Hard pass condition satisfaction

| # | Condition | Status |
|---|-----------|--------|
| 1 | `truth_primitive_fetch_runtime.py` exists | ✅ PASS |
| 2 | `TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION` and CDL dep tokens present | ✅ PASS |
| 3 | `WANT_HAVE_PATH = "/fetch/want-have"` and `WANT_BLOCK_PATH = "/fetch/want-block"` | ✅ PASS |
| 4 | Client `want_have()` returns `{have: bool, node_id: str}` | ✅ PASS |
| 5 | Client `want_block()` returns bytes or None | ✅ PASS |
| 6 | Server `handle_want_have_request()` responds with `{have: bool, node_id}` | ✅ PASS |
| 7 | Server `handle_want_block_request()` → bytes / 404 / 429 / 503 / 400 | ✅ PASS |
| 8 | `FetchRateLimiter` with `WANT_BLOCK_RATE_LIMIT_PER_MINUTE`; over-limit → `fetch_rate_limit_exceeded` | ✅ PASS |
| 9 | `http_fetch_transport_runtime.py` exists; server starts; `/fetch/want-have` and `/fetch/want-block` handled | ✅ PASS |
| 10 | CDL-077 opened (Phase 900) and ratified (Phase 904) in CDL master log | ✅ PASS |

All 10 hard pass conditions satisfied.

## 5. Exclusion token satisfaction

```
no_surb_onion_routing_in_window_899_905        SATISFIED
no_star_map_wiring_in_window_899_905           SATISFIED
no_spectral_routing_in_window_899_905          SATISFIED
no_dht_in_window_899_905                       SATISFIED
no_relay_fee_cdl_in_window_899_905             SATISFIED
no_micropayment_clearing_in_window_899_905     SATISFIED
no_persistent_rate_limiter_in_window_899_905   SATISFIED
no_hb_002_in_window_899_905                   SATISFIED
no_cdl_070_in_window_899_905                  SATISFIED
no_new_cdl_beyond_077_in_window_899_905       SATISFIED
```

## 6. Runtime deferral boundary

No onion routing or SURB reply envelopes were implemented (L4 deferred).
No star.map wiring was performed (L3 deferred).
No relay fee CDL opened (L5 deferred — reputation-implicit model locked as design intent).
Rate limiter is in-process only — not persistent across restarts.
`gossip_peer_registry.py` remains `static_v1` — no dynamic peer discovery.

## 7. Canonical anchors

- `docs/specs/ilc_phase_899_905_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `ilc_core/network/d2d/truth_primitive_fetch_runtime.py`
- `ilc_core/network/d2d/http_fetch_transport_runtime.py`
- `tests/test_phase_901_905_cdl_077_fetch.py`
