# Window 899–905 Closure Gate — Phase 905

Status: CLOSED
Date: 2026-04-27
Window: 899–905
Phase: 905

---

## 1. Purpose

This gate document closes Window 899–905 and verifies all hard pass conditions are
satisfied before the window is recorded as complete.

---

## 2. Commit Map

| Phase | Commit | Subject |
|-------|--------|---------|
| 899 | `6b5b8d47` | feat(g8): phase 899 window 899-905 sequence lock cdl-077 fetch |
| 900 | `9f785e61` | feat(g8): phase 900 cdl-077 want-have/want-block fetch opening |
| 901–903 | `d8b08ffa` | feat(g8): phase 899-903 cdl-077 want-have want-block fetch protocol |
| 904 | `e1bc7d44` | docs(g8): phase 904 cdl-077 ratification, coherence report, capsule v5.28 |

---

## 3. Hard Pass Condition Verification

| # | Condition | Commit | Status |
|---|-----------|--------|--------|
| 1 | `truth_primitive_fetch_runtime.py` exists in `ilc_core/network/d2d/` | `d8b08ffa` | ✅ PASS |
| 2 | `TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION = "truth_primitive_fetch_runtime_901.v0.1"` and CDL dep tokens | `d8b08ffa` | ✅ PASS |
| 3 | `WANT_HAVE_PATH = "/fetch/want-have"` and `WANT_BLOCK_PATH = "/fetch/want-block"` | `d8b08ffa` | ✅ PASS |
| 4 | Client `want_have()` returns `{have: bool, node_id: str}` | `d8b08ffa` | ✅ PASS |
| 5 | Client `want_block()` returns bytes or None | `d8b08ffa` | ✅ PASS |
| 6 | Server `handle_want_have_request()` responds with `{have: bool, node_id}` | `d8b08ffa` | ✅ PASS |
| 7 | Server `handle_want_block_request()` → bytes / 404 / 429 / 503 / 400 | `d8b08ffa` | ✅ PASS |
| 8 | `FetchRateLimiter` with `WANT_BLOCK_RATE_LIMIT_PER_MINUTE`; over-limit → `fetch_rate_limit_exceeded` (no crash) | `d8b08ffa` | ✅ PASS |
| 9 | `http_fetch_transport_runtime.py` exists; fetch server starts; `/fetch/want-have` and `/fetch/want-block` handled; unknown path → 404 | `d8b08ffa` | ✅ PASS |
| 10 | CDL-077 opened (Phase 900) and ratified (Phase 904) in CDL master log | `e1bc7d44` | ✅ PASS |

All 10 hard pass conditions: **PASS**.

---

## 4. Test Count at Closure

| Scope | Tests |
|-------|-------|
| Window 899–905 (CDL-077 fetch) | 34 |
| Window 892–898 (CDL-076 gossip) | 26 |
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **365** |

---

## 5. Exclusion Token Verification

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

---

## 6. Architecture Amendments at Closure

**Layer map corrected from 4 to 5 layers.** Capsule v5.27 recorded a 4-layer delivery
architecture. This window establishes the canonical 5-layer map (recorded in capsule v5.28):

| Layer | CDL | Status |
|-------|-----|--------|
| L1 — Announcement gossip | CDL-076 | Ratified |
| L2 — WANT-HAVE/WANT-BLOCK fetch | CDL-077 | Ratified |
| L3 — star.map N-gram routing | Future | H-series |
| L4 — Onion routing + SURB | Future | H-series |
| L5 — ECU routing fees + relay incentives | CDL-078+ | Design intent |

**Star map dissemination:** Confirmed to use CDL-076/077 pipeline — no separate Merkle
sync protocol needed. Star.map payloads are DAG-CBOR → CIDv1 natively.

**Relay incentive model:** Locked as reputation-implicit (not per-hop ECU micro-payment).
Design intent recorded in capsule v5.28 and ratification evidence.

---

## 7. Forward Obligations Carried to Phase 906+

| Obligation | Vehicle | Priority |
|------------|---------|----------|
| CDL-078: relay fee CDL (reputation-implicit) | CDL-078 | Phase 906+ next window |
| star.map L3 routing (N-gram index, spectral) | H-series CDL | Post-RC1 |
| Onion routing + SURB reply envelopes (L4 privacy) | Future CDL | Post-L3 |
| Multi-hop centrality attribution CDL | Future CDL | SIM-MULTI-HOP-01 evidence (Phase 552) |
| HB-002 P2P bootstrap distribution | Re-evaluate each window | HB-001 satisfied |
| CDL-070 PQ migration ceremony | Deep audit window | SIM-MONETARY-01 prerequisite |
| Persistent rate limiter (cross-restart) | Future CDL | In-process only in CDL-077 |

---

## 8. Closure Tokens

```
window_899_905_closed
capsule_v5_28_is_current_frontier
cdl_077_ratified
layer_map_5_layers_is_canonical
relay_fee_cdl_is_next_l5_obligation
relay_incentive_model_is_reputation_implicit_not_per_hop_ecu
star_map_dissemination_uses_cdl_076_cdl_077_pipeline_no_separate_protocol
window_899_905_closed_recorded_in_capsule_v5_28
```
