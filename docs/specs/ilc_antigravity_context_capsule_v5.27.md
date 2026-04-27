# ILC Antigravity Context Capsule v5.27

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.26.md
Date: 2026-04-27
Owner lane: Window 892–898 — CDL-076 truth primitive announcement gossip (Layer 1 network delivery)

`capsule_v5_27_supersedes_v5_26`
`window_892_898_closed_recorded_in_capsule_v5_27`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 892–898 — COMPLETE.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 892 | Sequence lock | Window 892–898 commissioned; layered delivery architecture established |
| 893 | CDL-076 opening | `"truth_primitive_announced"` gossip type locked |
| 894 | `truth_primitive_gossip_runtime.py` | announce_truth_primitive(); lightweight payload only |
| 895 | Submit CLI wiring | `gossip_delivery` field in `handle_submit` result |
| 896 | Tests | 26 tests; all pass |
| 897 | CDL-076 ratification + coherence + capsule | This phase |
| 898 | Closure gate | Gate document; window closed |

**Previous windows:**
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
| CDL-042 | Ratified | 407 | CLI framework — extended by Windows 873–898 |
| CDL-052 | Ratified | 466 | Popperian gate — intact |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-076 | Ratified | 897 | Truth primitive announcement gossip (Layer 1) |
| CDL-077 | Not yet opened | — | WANT-HAVE/WANT-BLOCK fetch — Phase 899+ |
| CDL-070 | Deferred | — | PQ migration |

(Full CDL table in v5.26 — unchanged except CDL-076 ratified and CDL-077 noted.)

---

## 4. Window 892–898 Deliverable

**New module:** `ilc_core/network/d2d/truth_primitive_gossip_runtime.py`

```python
TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION = "truth_primitive_gossip_runtime_894.v0.1"
CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"
TRUTH_PRIMITIVE_GOSSIP_TYPE = "truth_primitive_announced"

def announce_truth_primitive(write_receipt, envelope) -> dict:
    # Gossips {node_id, primitive, agent_id, epoch, cdl_version} per peer
    # Activation: ILC_D2D_GOSSIP_PEERS env var (comma-separated HTTPS URLs)
    # Returns: {gossip_delivery, peers_attempted, peers_succeeded, version}
```

**CLI:** `ilc submit` now returns `gossip_delivery` field:
```
"gossip_delivery": "announced to 2/2 peers"   # peers configured + node persisted
"gossip_delivery": "deferred — gossip peers not configured"  # ILC_D2D_GOSSIP_PEERS absent
```

**No new CDL beyond CDL-076.** CDL-042 framework extension.

**Test coverage:** 26 tests in `tests/test_phase_894_898_truth_primitive_gossip.py`

---

## 5. Full Submit → Persist → Announce → Query Loop

The submit → persist → gossip announce → query loop is now operational locally:

```
ilc submit --primitive assert.truth --payload-json '...' \
           --agent-id agent-001 --epoch 1
# → node_id: bafyreicbeey...
# → graph_persistence: persisted
# → gossip_delivery: announced to N/N peers  (if ILC_D2D_GOSSIP_PEERS set)

# On receiving peer (CDL-077 fetch — next window):
ilc query truth-node --node-id bafyreicbeey...
# → node_record: {primitive: "assert.truth", ...}
```

Both `ILC_TRUTH_GRAPH_STORE_PATH` and `ILC_D2D_GOSSIP_PEERS` must be set for full loop.

---

## 6. Layered Network Delivery Architecture (established Window 892–898)

Based on pre-phase research (MemPalace retrieval 2026-04-27, 192MB palace):

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip — soft push-signal | CDL-076 | **Ratified** |
| L2 | WANT-HAVE/WANT-BLOCK two-phase fetch; DoS prevention | CDL-077 | Phase 899+ |
| L3 | star.map N-gram route index; spectral routing | Future | H-series, post-RC1 |
| L4 | Two-sided ECU routing market; centrality attribution | Future CDL | Long term |

Historical canon anchors:
- `star.map` primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- Spectral routing: H-014 SIM-ROUTING-01 (Window 791–800)
- Passive ECU formula: `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- Two-sided ECU ledger: MemPalace `2026_03_15_21` / `2026_03_22_31` session records

---

## 7. Test Count

| Scope | Tests |
|-------|-------|
| Window 892–898 (CDL-076 gossip) | 26 |
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **331** |

---

## 8. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| CDL-077: WANT-HAVE/WANT-BLOCK fetch + DoS prevention | Phase 899+ | Next window |
| star.map L3 routing layer | Post-RC1 | H-series designed; not wired |
| Multi-hop centrality attribution CDL | Future | SIM-MULTI-HOP-01 evidence available (Phase 552) |
| Relay fee / two-sided ECU routing market | Future | Design intent; simulation pending |
| HB-002 (P2P bootstrap distribution) | Re-evaluate each closure | HB-001 closed; RC1 readiness watch |
| CDL-070 (PQ migration ceremony) | Deep audit window | SIM-MONETARY-01 prerequisite |
| Cross-epoch compaction / snapshot export | Deferred | — |
