# ILC Integration Coherence Report — Phase 904

Status: final
Date: 2026-04-27
Window: 899–905
Phase: 904

---

## 1. Purpose

This report verifies that Window 899–905 is internally coherent and that CDL-077
WANT-HAVE/WANT-BLOCK fetch connects cleanly to the CDL-075 LMDB graph store and
CDL-076 gossip announcement without disturbing existing handlers.

---

## 2. Scope of Changes

| File | Role |
|------|------|
| `docs/specs/ilc_phase_899_905_sequence_lock_v0.1.md` | Window sequence lock (Phase 899) |
| `docs/specs/ilc_cdl_077_want_have_want_block_fetch_opening_900_v0.1.md` | CDL-077 opening (Phase 900) |
| `ilc_core/network/d2d/truth_primitive_fetch_runtime.py` | Fetch runtime (Phases 901) |
| `ilc_core/network/d2d/http_fetch_transport_runtime.py` | Fetch HTTP transport (Phase 902) |
| `tests/test_phase_901_905_cdl_077_fetch.py` | 34 tests (Phase 903) |
| `docs/specs/ilc_cdl_077_want_have_want_block_fetch_ratification_evidence_904_v0.1.md` | Ratification evidence (Phase 904) |

---

## 3. Coherence Checks

### 3.1 WANT-HAVE handler performs presence check only — no full-record exposure in probe

`handle_want_have_request()` calls `store.get_node(node_id)` to check presence.
The response is `{have: bool, node_id: str}` — no node record content is returned.
This satisfies CDL-036: the probe is a soft push-signal, not a content delivery.

Token: `no_record_content_in_want_have_response` satisfied.

### 3.2 No LMDB write via fetch path

`handle_want_have_request()` and `handle_want_block_request()` both call
`store.get_node()` only — a read operation. No `put_node_if_absent()`,
`put_edge_if_absent()`, or any write method is called anywhere in the fetch path.

Token: `no_lmdb_write_in_fetch_path` satisfied.

### 3.3 CDL-076 gossip runtime untouched by fetch path

`truth_primitive_gossip_runtime.py` is not modified in this window.
The fetch runtime imports only from `gossip_transport` (for dep-chain guard) and
`gossip_peer_registry` (for `validate_peer_endpoint`). No gossip handler is invoked
during fetch operations.

Token: `no_cdl_076_gossip_runtime_mutation_in_window_899_905` satisfied.

### 3.4 Gossip HTTP transport untouched by fetch path

`http_gossip_transport_runtime.py` is not modified in this window. Fetch endpoints
run in a dedicated `HttpFetchTransportRuntime` server (Phase 902). The two servers
occupy separate ports and have independent handler chains. Path routing conflicts
are impossible.

Token: `no_http_gossip_transport_mutation_in_window_899_905` satisfied.

### 3.5 Rate limiter is per-identity and thread-safe

`FetchRateLimiter` uses a single `threading.Lock()` protecting the identity bucket
dict. Tests verify that identities are independent and that the over-limit token
`fetch_rate_limit_exceeded` is returned (not raised as an exception from the server
handler — only from the client-side `FetchRateLimitError` exception on 429).

### 3.6 Fetch server handles absent store gracefully

`HttpFetchTransportRuntime` opens the LMDB store on `start()` only if `store_path`
is non-empty. Absent store: `handle_want_have_request()` receives `store=None` and
returns `{have: false}`; `handle_want_block_request()` returns 503 with
`fetch_store_not_configured`. No crash, no stack trace.

This mirrors the CDL-075 pattern (`ILC_TRUTH_GRAPH_STORE_PATH` absent → persist skipped)
and the CDL-076 pattern (`ILC_D2D_GOSSIP_PEERS` absent → gossip deferred).

### 3.7 Dep-chain guard in fetch runtime

`truth_primitive_fetch_runtime.py` verifies `gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION`
at import time and raises `RuntimeError` on mismatch. Same pattern as existing dep-chain
guards in `truth_primitive_gossip_runtime.py` and `http_gossip_transport_runtime.py`.

`http_fetch_transport_runtime.py` verifies `TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION`
at import time.

### 3.8 No new CDL beyond CDL-077

CDL-077 is the only CDL opened and ratified in this window.

Token: `no_new_cdl_beyond_077_in_window_899_905` satisfied.

---

## 4. Forward Obligations Opened by This Window

| Obligation | Vehicle |
|------------|---------|
| Relay fee CDL: reputation-implicit incentive model | CDL-078, Phase 906+ |

---

## 5. Open Forward Obligations Carried Forward

| Obligation | Next window |
|------------|-------------|
| Relay fee CDL (L5): reputation-implicit relay incentive, not per-hop ECU | Phase 906+ |
| star.map L3 routing (N-gram index, spectral) | H-series, post-RC1 |
| Onion routing + SURB reply envelopes (L4 privacy) | Future CDL |
| Multi-hop centrality attribution CDL | Future |
| HB-002 P2P bootstrap distribution | Re-evaluate each window closure |
| CDL-070 PQ migration ceremony | Deep audit window |
| Persistent rate limiter (cross-restart) | Future CDL |

---

## 6. Coherence Verdict

Window 899–905 is coherent. All scope boundaries observed. All exclusion tokens satisfied.
34 new tests pass. No regressions. CDL-077 ratified.

`window_899_905_coherence_verified`
