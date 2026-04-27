# ILC Window 899–905 Sequence Lock

Status: locked
Date: 2026-04-27
Window: 899–905
Topic: CDL-077 — WANT-HAVE/WANT-BLOCK two-phase fetch with DoS rate limiting (Layer 2 network delivery)

`window_899_905_commissioned`
`cdl_077_want_have_want_block_fetch_layer_2`

---

## 1. Authorization Basis

This window is authorized by the forward obligation recorded in:

- `docs/specs/ilc_antigravity_context_capsule_v5.27.md` §8:
  *"CDL-077: WANT-HAVE/WANT-BLOCK fetch + DoS prevention — Phase 899+ — Next window"*
- Window 892–898 closure gate `ba9e5b01`: `window_892_898_closed`,
  `cdl_077_is_next_window_primary_obligation`
- CDL-076 ratification evidence (Phase 897): *"No fetch endpoint (CDL-077) was implemented
  or wired in this window."*

Pre-phase research completed 2026-04-27 with MemPalace corpus retrieval (192MB palace,
`out/mempalace_active_palace/`) and architectural review of H-series routing design
(`star.map.ngram.route_index.v1.md`, H-014/H-015 spectral routing records).

---

## 2. Architectural Grounding

### 2.1 Layer map amendment

Window 892–898 recorded a 4-layer delivery architecture. That map was incomplete.
This window establishes the corrected 5-layer map:

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip — soft push-signal per CDL-036 | CDL-076 | Ratified (Phase 897) |
| **L2 (this window)** | WANT-HAVE / WANT-BLOCK two-phase fetch; DoS rate limiting | CDL-077 | This window |
| L3 | star.map N-gram route index; spectral routing; location-agnostic CID discovery | Future CDL | H-series designed, not wired |
| L4 | Onion routing + SURB reply envelopes (privacy) | Future CDL | H-series designed, not wired |
| L5 | Two-sided ECU routing fees; relay incentives; centrality attribution per fetch | Future CDL | Partially ratified (CDL-060, passive ECU); full wiring Phase 907+ |

`layer_map_corrected_to_5_layers_in_window_899_905`

**Amendment note:** The 4-layer map in capsule v5.27 conflated L4 (privacy) into L3 and
omitted L4 (onion/SURB) as a named layer. Capsule v5.28 will record the corrected map.

### 2.2 Pull dominance — CDL-036 governing contract

CDL-036 (ratified Phase 351): *"ILC leans pull, not push."* CDL-077 implements the pull
side of the CDL-036 dissemination contract. CDL-076 (L1) signals availability;
CDL-077 (L2) delivers content on demand. No push of full records.

`cdl_077_is_the_pull_side_of_cdl_036`

### 2.3 WANT-HAVE / WANT-BLOCK protocol design

Two-phase fetch, based on Bitswap-style probe-then-fetch:

```
Phase 1 — WANT-HAVE probe (cheap):
  Requester → Peer: POST /fetch/want-have  {node_id: <CIDv1>, requester_id: <agent_id>}
  Peer → Requester: {have: true|false, node_id: <CIDv1>}

Phase 2 — WANT-BLOCK content fetch (expensive, rate-limited):
  Requester → Peer: POST /fetch/want-block  {node_id: <CIDv1>, requester_id: <agent_id>}
  Peer → Requester: full node record (DAG-CBOR bytes) — or 429 if rate-limited
```

**Design rationale:**
- WANT-HAVE is a free availability probe — cheap, no record content exposed, DoS surface minimal
- WANT-BLOCK is rate-limited per `requester_id` identity — prevents flooding the content path
- `requester_id` is the ML-DSA-65 agent_id (CDL-042 globally flat namespace) — unforgeable identity
- Rate limit: `WANT_BLOCK_RATE_LIMIT_PER_MINUTE` (calibration: 10/minute per identity, configurable)
- Absence of `ILC_TRUTH_GRAPH_STORE_PATH` → server returns `fetch_store_not_configured` gracefully

### 2.4 DoS prevention — identity-bound rate limiting

The WANT-HAVE probe is lightweight and not rate-limited in this window (CDL-077 scope).
WANT-BLOCK is rate-limited because it triggers an LMDB read and full record serialization.

Rate limiter design: in-process token bucket per `requester_id`.
- Not persistent across restarts (acceptable for RC phase)
- Persistent rate limiter state deferred to future CDL
- Over-limit: HTTP 429, token `fetch_rate_limit_exceeded`, no crash

### 2.5 Relay incentives — reputation-implicit model

The relay fee CDL (L5) will NOT specify ECU micro-payments per relay hop.
Based on architectural review (2026-04-27), the ILC-native mechanism is:

- *Serving* a WANT-BLOCK → routing reputation accurate → centrality score rises →
  higher passive ECU via ratified formula (SIM-PASSIVE-ECU-01, Phase 542):
  `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- *Dropping/refusing* to serve → routing reputation degrades → centrality falls → reduced ECU

ECU is the long-run consequence of routing behavior, not a per-hop payment.
This avoids a micro-payment clearing mechanism and aligns with CDL-036's pull-dominant philosophy.

`relay_incentive_model_is_reputation_implicit_not_per_hop_ecu`
`relay_fee_cdl_will_not_specify_micropayment_clearing`

This design intent is a forward obligation for the relay fee CDL; it is not ratified here.

### 2.6 Star map dissemination — no separate protocol needed

The star.map `@v1` spec (`docs/specs/star.map.ngram.route_index.v1.md`) uses
DAG-CBOR → CIDv1 NodeID → COSE_Sign1 — content-addressed natively. A new star.map
index version produces a new CID. The dissemination of "new route index available"
is exactly CDL-076 (`truth_primitive_announced` gossip carrying the route-index node_id),
and the index fetch is exactly CDL-077 (WANT-BLOCK for the index CID). No separate
Merkle sync or versioning protocol is required.

`star_map_dissemination_uses_cdl_076_cdl_077_pipeline_no_separate_protocol`

### 2.7 Fetch transport — separate from gossip transport

The CDL-061 gossip server routes inbound POST requests via
`gossip_request_path(gossip_type)` — a gossip-type-keyed path pattern.
Fetch endpoints (`/fetch/want-have`, `/fetch/want-block`) fall outside gossip-type
routing and must be served by a dedicated fetch transport server. This is implemented
as `http_fetch_transport_runtime.py`, following the same design patterns as
`http_gossip_transport_runtime.py` but handling fetch paths only.

---

## 3. Window Scope

### 3.1 In scope

| Phase | Topic |
|-------|-------|
| 899 | Sequence lock (this document) |
| 900 | CDL-077 opening document |
| 901 | `ilc_core/network/d2d/truth_primitive_fetch_runtime.py` (client + server handlers + rate limiter) |
| 902 | `ilc_core/network/d2d/http_fetch_transport_runtime.py` (fetch HTTP server) |
| 903 | Tests (`tests/test_phase_901_905_cdl_077_fetch.py`) |
| 904 | CDL-077 ratification + coherence report + capsule v5.28 |
| 905 | Closure gate |

### 3.2 Explicit exclusions

```
no_surb_onion_routing_in_window_899_905        L4 privacy — future CDL
no_star_map_wiring_in_window_899_905           L3 — H-series, not this window
no_spectral_routing_in_window_899_905          L3 — H-014 prerequisite
no_dht_in_window_899_905                       static peer config only
no_relay_fee_cdl_in_window_899_905             L5 — relay incentive CDL Phase 907+
no_micropayment_clearing_in_window_899_905     reputation-implicit model only
no_persistent_rate_limiter_in_window_899_905   in-process only for RC phase
no_hb_002_in_window_899_905                   re-evaluate each window closure
no_cdl_070_in_window_899_905                  SIM-MONETARY-01 prerequisite; deep audit agenda
no_new_cdl_beyond_077_in_window_899_905       one CDL only
```

---

## 4. Hard Pass Conditions

The Phase 905 closure gate must verify all 10 conditions:

| # | Condition |
|---|-----------|
| 1 | `ilc_core/network/d2d/truth_primitive_fetch_runtime.py` exists |
| 2 | `TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION` and `CDL_077_DEPENDENCY` tokens present in fetch runtime |
| 3 | `WANT_HAVE_PATH = "/fetch/want-have"` and `WANT_BLOCK_PATH = "/fetch/want-block"` constants declared |
| 4 | Client `want_have(node_id, peer_endpoint)` → `{have: bool, node_id: str}` (HTTP POST, no full record) |
| 5 | Client `want_block(node_id, peer_endpoint)` → node record bytes or `None` |
| 6 | Server `handle_want_have_request(body, store)` responds with `{have: bool, node_id: str}` |
| 7 | Server `handle_want_block_request(body, store, rate_limiter)` → node bytes or 429 token |
| 8 | `FetchRateLimiter` with `WANT_BLOCK_RATE_LIMIT_PER_MINUTE` constant; over-limit → `fetch_rate_limit_exceeded` (no crash) |
| 9 | `ilc_core/network/d2d/http_fetch_transport_runtime.py` exists; fetch server starts and handles `/fetch/want-have` and `/fetch/want-block` |
| 10 | CDL-077 opened (Phase 900) and ratified (Phase 904) in CDL master log |

---

## 5. Phase Detail

### Phase 900 — CDL-077 Opening

**Deliverables:**
- CDL-077 row inserted in `docs/specs/ilc_constitutional_decision_log_v0.1.md` as `open`
- `docs/specs/ilc_cdl_077_want_have_want_block_fetch_opening_900_v0.1.md`

**CDL-077 scope statement:**
CDL-077 ratifies the two-phase fetch protocol for truth primitive nodes: WANT-HAVE (lightweight
availability probe) followed by WANT-BLOCK (rate-limited full record delivery). CDL-077 is the
pull side of the CDL-036 dissemination contract and the Layer 2 complement to CDL-076 (Layer 1
announcement gossip). Rate limiting is per-identity (ML-DSA-65 agent_id) using an in-process
token bucket.

**Options under consideration for CDL-077:**
- Option A (rejected): single-phase full-record fetch — no probe, DoS surface too high
- Option B (rejected): persistent rate limiter with cross-session accounting — out of scope for RC phase
- **Option C (selected):** two-phase probe+fetch with in-process per-identity rate limiter

**Parent CDLs:** CDL-036 / CDL-042 / CDL-075 / CDL-076

---

### Phase 901 — Fetch Runtime

**File:** `ilc_core/network/d2d/truth_primitive_fetch_runtime.py`

**Required tokens:**
```python
TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION = "truth_primitive_fetch_runtime_901.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"
WANT_HAVE_PATH = "/fetch/want-have"
WANT_BLOCK_PATH = "/fetch/want-block"
WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10
_FETCH_TIMEOUT_SECONDS = 5.0
```

**Client functions:**
```python
def want_have(node_id: str, peer_endpoint: str) -> dict:
    """
    Send WANT-HAVE probe to peer.
    Returns {have: bool, node_id: str}.
    Raises FetchTransportError on network/protocol failure.
    """

def want_block(node_id: str, peer_endpoint: str) -> bytes | None:
    """
    Send WANT-BLOCK request to peer.
    Returns raw node record bytes if peer has it, None if peer returns 404.
    Raises FetchRateLimitError if peer returns 429.
    Raises FetchTransportError on network/protocol failure.
    """

def fetch_truth_primitive(node_id: str) -> bytes | None:
    """
    Try all peers from ILC_D2D_GOSSIP_PEERS with WANT-HAVE then WANT-BLOCK.
    Returns node record bytes from first willing peer, or None if not found.
    ILC_D2D_GOSSIP_PEERS absent → returns None with descriptive log.
    """
```

**Server handler functions:**
```python
def handle_want_have_request(body: bytes, store: Any) -> tuple[int, bytes]:
    """
    Server-side WANT-HAVE handler.
    Parses {node_id, requester_id} from body.
    Checks store for node_id presence (no full read).
    Returns (200, JSON response {have: bool, node_id: str})
    or (400, error JSON) on bad request.
    """

def handle_want_block_request(
    body: bytes, store: Any, rate_limiter: "FetchRateLimiter"
) -> tuple[int, bytes]:
    """
    Server-side WANT-BLOCK handler.
    Parses {node_id, requester_id}.
    Checks rate_limiter for requester_id — returns (429, {token: "fetch_rate_limit_exceeded"}) if exceeded.
    Reads full node record from store.
    Returns (200, record_bytes) or (404, error JSON) if not found.
    """
```

**Rate limiter:**
```python
class FetchRateLimiter:
    """In-process per-identity token bucket rate limiter for WANT-BLOCK requests."""

    def __init__(self, limit_per_minute: int = WANT_BLOCK_RATE_LIMIT_PER_MINUTE) -> None: ...

    def check_and_consume(self, requester_id: str) -> bool:
        """Returns True if request is allowed, False if rate limit exceeded."""
```

**Dep-chain guard:** verify `CDL_042_DEPENDENCY` against agent_id runtime at import time.

---

### Phase 902 — Fetch HTTP Transport

**File:** `ilc_core/network/d2d/http_fetch_transport_runtime.py`

**Required tokens:**
```python
HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_902.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
FETCH_RUNTIME_DEPENDENCY = "truth_primitive_fetch_runtime_901.v0.1"
```

**Design:** Minimal threaded HTTP server (same pattern as `http_gossip_transport_runtime.py`)
handling exactly two POST paths: `WANT_HAVE_PATH` and `WANT_BLOCK_PATH`. All other paths
return 404. No SSL server cert required for RC phase (nodes call each other within trusted
network perimeter; TLS posture documented in ADR-0025).

**Configuration:**
```python
@dataclass
class FetchTransportConfig:
    bind_host: str = "127.0.0.1"
    bind_port: int = 0          # 0 → OS assigns free port
    store_path: str = ""        # ILC_TRUTH_GRAPH_STORE_PATH
    rate_limit_per_minute: int = WANT_BLOCK_RATE_LIMIT_PER_MINUTE
    request_timeout_seconds: float = 5.0
```

**Key invariants:**
- `store_path` absent → WANT-HAVE returns `{have: false}`, WANT-BLOCK returns 503
  with token `fetch_store_not_configured`
- Malformed request body → 400 with descriptive token, no crash
- Unknown path → 404
- All POST paths read body into memory-bounded buffer (same OOM guard pattern as gossip transport)

---

### Phase 903 — Tests

**File:** `tests/test_phase_901_905_cdl_077_fetch.py`

**Commit subject (for scope guard):**
`"feat(g8): phase 899-903 cdl-077 want-have want-block fetch protocol"`

**Test coverage (minimum 22 tests):**

| Group | Tests |
|-------|-------|
| 1. Module existence + tokens | fetch runtime exists; version token; CDL-077/075/042 dep tokens; path constants |
| 2. Rate limiter | under limit → allowed; over limit → False; window resets; separate identities independent |
| 3. WANT-HAVE client | mocked peer → `{have: true}`; mocked peer absent → `{have: false}`; bad peer → FetchTransportError |
| 4. WANT-BLOCK client | mocked peer → bytes; 404 → None; 429 → FetchRateLimitError; bad peer → error |
| 5. fetch_truth_primitive | no peers configured → None; first peer has it → bytes; first no second yes → bytes |
| 6. Server WANT-HAVE handler | node in store → `{have: true}`; node absent → `{have: false}`; malformed → 400 |
| 7. Server WANT-BLOCK handler | in store → 200+bytes; absent → 404; rate limited → 429+token; malformed → 400 |
| 8. HTTP transport server | starts on free port; handles `/fetch/want-have`; handles `/fetch/want-block`; unknown path → 404 |
| 9. Store-absent guard | `store_path` empty → WANT-HAVE returns false; WANT-BLOCK returns 503 |
| 10. Commit scope guard | Phase 903 commit touches only `ilc_core/network/d2d/` + `tests/` |

---

### Phase 904 — CDL-077 Ratification + Coherence Report + Capsule v5.28

**CDL-077 ratification:**
- CDL master log row updated from `open` → `ratified`
- Ratification evidence: `docs/specs/ilc_cdl_077_want_have_want_block_fetch_ratification_evidence_904_v0.1.md`
- Atomic commit with `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=904`

**Coherence report:** `docs/specs/ilc_integration_coherence_report_904_v0.1.md`
- Key check: WANT-HAVE handler does NOT perform full LMDB read (presence check only)
- Key check: WANT-BLOCK handler does NOT mutate store
- Key check: Gossip transport (`http_gossip_transport_runtime.py`) is not modified in this window

**Capsule:** `docs/specs/ilc_antigravity_context_capsule_v5.28.md` — supersedes v5.27
- Records corrected 5-layer delivery architecture
- Records `relay_incentive_model_is_reputation_implicit_not_per_hop_ecu` design intent
- Records `star_map_dissemination_uses_cdl_076_cdl_077_pipeline_no_separate_protocol`

**Test count update (estimated):**

| Scope | Tests |
|-------|-------|
| Window 899–905 (CDL-077 fetch) | ~22 |
| Window 892–898 (CDL-076 gossip) | 26 |
| Prior windows | 305 |
| **Total (estimated)** | **~353** |

---

### Phase 905 — Closure Gate

**File:** `docs/specs/ilc_window_899_905_closure_gate_905_v0.1.md`

Verifies all 10 hard pass conditions. On PASS emits:

```
window_899_905_closed
capsule_v5_28_is_current_frontier
cdl_077_ratified
relay_fee_cdl_is_next_l5_obligation
layer_map_5_layers_is_canonical
```

---

## 6. Forward Obligations Carried Forward

| Obligation | Next window | Evidence basis |
|------------|-------------|----------------|
| Relay fee CDL (L5): reputation-implicit relay incentive, not per-hop ECU | Phase 906+ | Design intent locked 2026-04-27; relay fee CDL to open after CDL-077 ratified |
| star.map L3 routing (N-gram index, spectral) | H-series, post-RC1 | `star.map.ngram.route_index.v1.md`; H-014/H-015; CDL-076/077 pipeline serves star.map updates |
| Onion routing + SURB reply envelopes (L4 privacy) | Future CDL | H-series designed; not wired |
| Multi-hop centrality attribution CDL | Future | SIM-MULTI-HOP-01 Phase 552 evidence |
| HB-002 P2P bootstrap distribution | Re-evaluate each window closure | HB-001 closed |
| CDL-070 PQ migration ceremony | Deep audit window | SIM-MONETARY-01 prerequisite |
| Persistent rate limiter (cross-restart) | Future CDL | In-process only in this window |

---

## 7. Sequence Constraints

1. Phase 900 (CDL-077 open) must precede Phase 901 (fetch runtime)
2. Phase 901 (fetch runtime) must precede Phase 902 (HTTP fetch transport)
3. Phase 902 (transport server) must precede Phase 903 (tests)
4. Phase 903 (tests passing) must precede Phase 904 (ratification)
5. Phase 904 (ratification) must precede Phase 905 (closure gate)
6. No star.map wiring, no SURB/onion routing, no relay fee CDL in this window

---

## 8. Governing Tokens

```
window_899_905_commissioned
cdl_077_is_the_pull_side_of_cdl_036
want_have_is_the_availability_probe
want_block_is_the_rate_limited_content_fetch
fetch_rate_limiter_is_per_identity_in_process
relay_incentive_model_is_reputation_implicit_not_per_hop_ecu
star_map_dissemination_uses_cdl_076_cdl_077_pipeline_no_separate_protocol
layer_map_5_layers_is_canonical
http_fetch_transport_is_separate_from_gossip_transport
cdl_078_relay_fee_is_the_l5_obligation
```
