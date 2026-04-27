# ILC Antigravity Context Capsule v5.29

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.28.md
Date: 2026-04-27
Owner lane: Window 906–912 — CDL-078 Relay Incentive Constitutional Lock (Layer 5)

`capsule_v5_29_supersedes_v5_28`
`window_906_912_closed_recorded_in_capsule_v5_29`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 906–912 — COMPLETE.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 906 | Sequence lock | Window 906–912 commissioned; open questions resolved analytically |
| 907 | CDL-078 opening | Relay incentive CDL opened; Option C selected |
| 908 | `routing_reputation_runtime.py` | Serve event recorder + epoch flush → CDL-060 |
| 909 | Serve event wiring | `handle_want_block_request()` 200 path → `record_serve_event()` |
| 910 | Tests | 28 tests; all pass |
| 911 | CDL-078 ratification + coherence + capsule | This phase |
| 912 | Closure gate | Gate document; window closed |

**Previous windows:**
- Window 899–905 COMPLETE. CDL-077 ratified (Phase 904). 365 tests.
- Window 892–898 COMPLETE. CDL-076 ratified (Phase 897). 331 tests.
- Window 887–891 COMPLETE. Truth primitive read-path query. 305 tests.
- Window 877–886 COMPLETE. CDL-075 ratified (Phase 884). 282 tests.
- Window 873–876 COMPLETE. CLI `submit` command. 251 tests.
- Window 863–872 COMPLETE. CDL-074 ratified (Phase 870). 229 tests.

---

## 2. Option B Status (unchanged)

`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`

---

## 3. CDL Status

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-042 | Ratified | 407 | CLI framework — extended by Windows 873–912 |
| CDL-052 | Ratified | 466 | Popperian gate — intact |
| CDL-060 | Ratified | 541 | Centrality delta gossip — fed by CDL-078 serve events |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-076 | Ratified | 897 | Truth primitive announcement gossip (Layer 1) |
| CDL-077 | Ratified | 904 | WANT-HAVE/WANT-BLOCK fetch (Layer 2) |
| CDL-078 | **Ratified** | **911** | **Relay incentive constitutional lock (Layer 5)** |
| CDL-070 | Deferred | — | PQ migration |
| CDL-079 | Not yet opened | — | star.map N-gram route index (Layer 3) — Window 921–929 |

(Full CDL table in v5.27 — unchanged except CDL-077, CDL-078 ratified.)

---

## 4. Window 906–912 Deliverables

### 4.1 New module: `routing_reputation_runtime.py`

```python
# ilc_core/network/d2d/routing_reputation_runtime.py

ROUTING_REPUTATION_RUNTIME_VERSION = "routing_reputation_runtime_908.v0.1"
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"

SERVE_CENTRALITY_DELTA: float = 0.01          # credit per successful WANT-BLOCK serve
SERVE_CENTRALITY_MAX_PER_EPOCH: float = 0.10  # per-node cap per epoch

def new_reputation_state() -> dict:
    """{"serve_buffer": {}, "flush_log": []}"""

def record_serve_event(node_id: str, epoch: int, state: dict) -> None:
    """Best-effort. Never raises. Thread-safe. Increments serve_buffer[epoch][node_id]."""

def flush_epoch_serve_events(epoch, state, centrality_state) -> dict:
    """Converts epoch buffer → CDL-060 centrality delta calls.
    raw_delta = min(count × SERVE_CENTRALITY_DELTA, SERVE_CENTRALITY_MAX_PER_EPOCH)
    Returns {"epoch", "nodes_flushed", "total_delta_emitted"}"""
```

### 4.2 Patch: `truth_primitive_fetch_runtime.py` (Phase 909)

CDL-078 serve event wiring added to `handle_want_block_request()` at 200 success path:

```python
CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"

# Inside handle_want_block_request(), after return 200, record_bytes path:
try:
    from ilc_core.network.d2d.routing_reputation_runtime import (
        record_serve_event, _global_reputation_state,
    )
    record_serve_event(node_id, int(time.time() // 60), _global_reputation_state)
except Exception:
    pass  # best-effort; WANT-BLOCK response is not affected
```

### 4.3 Test coverage

**28 tests** in `tests/test_phase_908_912_cdl_078_relay_incentive.py`:

| Group | Tests |
|-------|-------|
| Module existence + tokens | 6 |
| Constants | 4 |
| `record_serve_event` | 5 |
| `flush_epoch_serve_events` | 5 |
| `handle_want_block_request` wiring (200/404/429/503) | 4 |
| No negative delta | 1 |
| No per-hop ECU (source scan) | 1 |
| CDL-078 in master log | 1 |
| Commit scope guard | 1 |

---

## 5. Relay Incentive Model (CDL-078)

The CDL-078 relay incentive model is **reputation-implicit**:

```
WANT-BLOCK 200 response
    → record_serve_event(node_id, epoch, state)          [in-process, best-effort]
    → state["serve_buffer"][epoch][node_id] += 1

At epoch close (epoch = int(time.time() // 60)):
    → flush_epoch_serve_events(epoch, state, centrality_state)
    → raw_delta = min(count × 0.01, 0.10)
    → accumulate_centrality_delta(node_id, raw_delta, epoch, centrality_state)  [CDL-060]
    → centrality_score rises
    → passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)
```

**No new token. No new ledger. No per-hop micro-payment.**

The incentive is implicit in the existing economic stack:
- Serve well → centrality rises → passive ECU accrues
- Do not serve → centrality decays via CDL-V1 temporal decay (existing mechanism)

`cdl_078_closes_l5_using_existing_cdl_060_and_passive_ecu_infrastructure`
`relay_incentive_model_is_reputation_implicit_not_per_hop_ecu`

---

## 6. 5-Layer Network Delivery Architecture (canonical)

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip — soft push-signal | CDL-076 | **Ratified (Phase 897)** |
| **L2** | WANT-HAVE/WANT-BLOCK two-phase fetch; DoS rate limiting | CDL-077 | **Ratified (Phase 904)** |
| **L5** | Relay incentives — serve → centrality → passive ECU | **CDL-078** | **Ratified (Phase 911)** |
| L3 | star.map N-gram route index; spectral routing | CDL-079 | Window 921–929 |
| L4 | Onion routing + SURB reply envelopes (privacy) | Future CDL | Post-L3 |

`layer_map_5_layers_is_canonical`
`l5_relay_incentive_model_constitutionally_locked`

---

## 7. Test Count

| Scope | Tests |
|-------|-------|
| Window 906–912 (CDL-078 relay incentive) | 28 |
| Window 899–905 (CDL-077 fetch) | 34 |
| Window 892–898 (CDL-076 gossip) | 26 |
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **393** |

---

## 8. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| HB-002: P2P bootstrap distribution | Window 913–920 | Next window primary obligation |
| CDL-079: star.map N-gram route index (L3) | Window 921–929 | H-series designed; CDL-076/077/078 serve star.map dissemination |
| Onion routing + SURB reply envelopes (L4 privacy) | Post-L3 | H-series designed, not wired |
| SIM-RELAY-01: serve-rate → centrality delta calibration tuning | Post-RC1 | Named forward obligation; not gate |
| Negative routing reputation signals | CDL-080+ | Deferred; CDL-V1 decay provides implicit penalty |
| Persistent serve event log (cross-restart) | Future CDL | In-process only in CDL-078 |
| CDL-001 packaging track | Pre-launch | genesis_blocker |
| CDL-070 PQ migration ceremony | Deep audit window | SIM-MONETARY-01 prerequisite |
| Multi-hop centrality attribution CDL | Future | SIM-MULTI-HOP-01 evidence available |

---

## 9. RC1 Remaining Gates

| Gate | Status |
|------|--------|
| CDL-077 (L2 fetch) | **Ratified (Phase 904)** |
| CDL-078 (L5 relay incentive) | **Ratified (Phase 911)** |
| HB-002 (P2P bootstrap distribution) | Pending (Window 913–920) |
| CDL-001 (packaging track) | Pending |

---

## 10. Historical State Anchors

- Full CDL ratification history: v5.27 §3 (unchanged)
- Full window history through Window 892–898: v5.27 §2
- Option B rationale (ADR-0028): v5.13
- Passive ECU formula: `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- Centrality score cap: `CENTRALITY_SCORE_CAP = 1.0`
- Two-sided ECU ledger: MemPalace `2026_03_15_21` / `2026_03_22_31`
- star.map primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- Spectral routing: H-014 SIM-ROUTING-01 (Window 791–800)
