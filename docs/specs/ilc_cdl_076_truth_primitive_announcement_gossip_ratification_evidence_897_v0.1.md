# CDL-076 Truth Primitive Announcement Gossip — Ratification Evidence 897 v0.1

Status: Phase-897 ratification evidence artifact
Date: 2026-04-27
Window: 892–898
Phase: 897

## 1. Purpose and scope

This artifact ratifies CDL-076 and records the selected truth primitive announcement gossip
contract for Window 892–898.

CDL-076 ratifies this phase only. No fetch endpoint is ratified in this window (CDL-077 scope).

## 2. Ratified decision

CDL-076 ratifies **Option C — lightweight announcement with ILC_D2D_GOSSIP_PEERS activation gate.**

Rejected options:
- **Option A** — full node record payload in gossip message (violates CDL-036 prohibition on full-payload push)
- **Option B** — unconditional push to all peers without activation gate (incorrect in single-node RC0.1 deployments)

The ratified answer:
- Gossip type: `"truth_primitive_announced"` (locked)
- Payload: exactly `{node_id, primitive, agent_id, epoch, cdl_version}` — no full record content
- Activation: `ILC_D2D_GOSSIP_PEERS` env var (comma-separated HTTPS endpoints)
- Fires only after confirmed CDL-075 persist (node_id present)
- Absent peers or absent node_id: graceful skip with descriptive receipt field
- No LMDB read or write in gossip path

`cdl_076_option_c_ratified`
`truth_primitive_announced_is_the_locked_gossip_type`
`cdl_076_extends_cdl_036_to_truth_primitive_nodes`

## 3. Evidence basis

- Sequence lock: `docs/specs/ilc_phase_892_898_sequence_lock_v0.1.md`
- CDL-076 opening: `docs/specs/ilc_cdl_076_truth_primitive_announcement_gossip_opening_893_v0.1.md`
- Runtime: `ilc_core/network/d2d/truth_primitive_gossip_runtime.py`
  - `TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION = "truth_primitive_gossip_runtime_894.v0.1"`
  - `CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"`
  - `TRUTH_PRIMITIVE_GOSSIP_TYPE = "truth_primitive_announced"`
- Submit CLI: `ilc_core/cli/d2e_submit_cli.py`
  - `CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"` added
  - `gossip_delivery` field in result dict
- Tests: `tests/test_phase_894_898_truth_primitive_gossip.py` — 26 tests, all pass

## 4. Hard pass condition satisfaction

| # | Condition | Status |
|---|-----------|--------|
| 1 | `truth_primitive_gossip_runtime.py` exists | ✅ PASS |
| 2 | `TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION` and CDL dep tokens present | ✅ PASS |
| 3 | `TRUTH_PRIMITIVE_GOSSIP_TYPE = "truth_primitive_announced"` | ✅ PASS |
| 4 | Payload exactly `{node_id, primitive, agent_id, epoch, cdl_version}` | ✅ PASS |
| 5 | `ILC_D2D_GOSSIP_PEERS` absent → graceful skip | ✅ PASS |
| 6 | Submit CLI wired: `gossip_delivery` field in result | ✅ PASS |
| 7 | Absent peers → `"deferred — gossip peers not configured"` | ✅ PASS |
| 8 | Absent store path → gossip not attempted | ✅ PASS |
| 9 | No LMDB mutation via gossip path | ✅ PASS |
| 10 | CDL-076 opened (893) and ratified (897) in CDL master log | ✅ PASS |

All 10 hard pass conditions satisfied.

## 5. Exclusion token satisfaction

```
no_fetch_endpoint_in_window_892_898         SATISFIED
no_want_have_want_block_in_window_892_898   SATISFIED
no_star_map_wiring_in_window_892_898        SATISFIED
no_spectral_routing_in_window_892_898       SATISFIED
no_dht_in_window_892_898                    SATISFIED
no_routing_fee_in_window_892_898            SATISFIED
no_multi_hop_attribution_in_window_892_898  SATISFIED
no_cdl_077_in_window_892_898               SATISFIED
no_hb_002_in_window_892_898               SATISFIED
no_cdl_070_in_window_892_898              SATISFIED
no_new_cdl_beyond_076_in_window_892_898   SATISFIED
```

## 6. Runtime deferral boundary

No fetch endpoint (CDL-077) was implemented or wired in this window.
No star.map wiring was performed.
No DHT or dynamic peer discovery.
`gossip_peer_registry.py` remains `static_v1`.

## 7. Canonical anchors

- `docs/specs/ilc_phase_892_898_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `ilc_core/network/d2d/truth_primitive_gossip_runtime.py`
- `ilc_core/cli/d2e_submit_cli.py`
- `tests/test_phase_894_898_truth_primitive_gossip.py`
