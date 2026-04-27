# ILC Window 892–898 Sequence Lock

Status: locked
Date: 2026-04-27
Window: 892–898
Topic: CDL-076 — Truth primitive announcement gossip (Layer 1 network delivery)

`window_892_898_commissioned`
`cdl_076_truth_primitive_announcement_gossip_layer_1`

---

## 1. Authorization Basis

This window is authorized by the forward obligation recorded in:

- `docs/specs/ilc_antigravity_context_capsule_v5.26.md` §7:
  *"Network-layer delivery of persisted truth primitive records — Phase 892+ — CDL-076 required"*
- Window 887–891 closure gate: `window_887_891_closed`, `capsule_v5_26_is_current_frontier`
- CDL-075 ratification evidence (Phase 884): *"read-path query integration, network delivery, and
  cross-epoch compaction deferred"*

Pre-phase research completed 2026-04-27 with MemPalace corpus retrieval (192MB palace,
`out/mempalace_active_palace/`). All open questions resolved before sequence lock composition.

---

## 2. Architectural Grounding

### 2.1 Constitutional anchor — CDL-036

CDL-036 (ratified Phase 351) is the governing dissemination contract:

> *"ILC leans pull, not push."*
> *"pull-dominant with soft push-signals"*
> *"header-first dissemination does not authorize full-payload push as the default transport rule."*

CDL-076 extends CDL-036's header-first + CID-addressed pull fetch contract to truth primitive
node records persisted under CDL-075. No competing dissemination architecture is opened.

`cdl_076_extends_cdl_036_to_truth_primitive_nodes`

### 2.2 Layered delivery architecture

This window implements Layer 1 of a fully designed multi-layer delivery architecture. Layers
are sequenced; this window does not attempt higher layers.

| Layer | Mechanism | Window |
|-------|-----------|--------|
| **L1 — CDL-076 (this window)** | Announcement gossip — soft push-signal per CDL-036 | 892–898 |
| L2 — CDL-077 | WANT-HAVE / WANT-BLOCK two-phase fetch; DoS prevention; direct peer handshake | 899+ |
| L3 — star.map | N-gram route index, spectral routing, location-agnostic CID discovery | H-series, post-RC1 |
| L4 — Economics | Two-sided ECU routing market, relay fees, centrality attribution per fetch | Future CDL |

Historical canon anchors for L2–L4:

- `star.map` named primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- Tier 4 spectral routing: `docs/specs/ilc_phase_791_800_sequence_lock_v0.1.md` (H-014/H-015)
- Two-sided ECU ledger: MemPalace retrieval from `2026_03_15_21_ILC_VSCode_Session_Mar15_21.md`
  and `2026_03_22_31_ILC_VSCode_Session_Mar22_31.md`
- Passive ECU formula: `docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md`
- Multi-hop centrality: SIM-MULTI-HOP-01 (Phase 552, research-only — no CDL opened from it)

### 2.3 Economic incentive basis

Every truth primitive fetch (CDL-077+) will trigger a centrality update for the served node,
feeding the ratified passive ECU formula:

```
passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)
```

(rate=0.20, decay_floor=0.05, attribution_cap=0.15 — SIM-PASSIVE-ECU-01, Phase 542)

Holding and serving data is structurally rewarded through centrality accumulation at epoch
boundaries. The relay fee / routing market layer (L4) is forward-obligated, not implemented here.

---

## 3. Window Scope

### 3.1 In scope

| Phase | Topic |
|-------|-------|
| 892 | Sequence lock (this document) |
| 893 | CDL-076 opening stub + opening document |
| 894 | `ilc_core/network/d2d/truth_primitive_gossip_runtime.py` |
| 895 | Submit CLI wiring (`d2e_submit_cli.py` Phase 895 extension) |
| 896 | Tests (`tests/test_phase_894_898_truth_primitive_gossip.py`) |
| 897 | CDL-076 ratification + coherence report + capsule v5.27 |
| 898 | Closure gate |

### 3.2 Explicit exclusions

```
no_fetch_endpoint_in_window_892_898         CDL-077 scope; not this window
no_want_have_want_block_in_window_892_898   CDL-077 scope
no_star_map_wiring_in_window_892_898        H-series, post-RC1
no_spectral_routing_in_window_892_898       H-series, conditional on H-014
no_dht_in_window_892_898                    static peer config only
no_routing_fee_in_window_892_898            ECU routing market, future CDL
no_multi_hop_attribution_in_window_892_898  SIM-MULTI-HOP-01 evidence exists; CDL not yet opened
no_cdl_077_in_window_892_898               next window
no_hb_002_in_window_892_898               RC2+ evaluation at each closure
no_cdl_070_in_window_892_898              SIM-MONETARY-01 prerequisite; deep audit agenda
no_new_cdl_beyond_076_in_window_892_898   one CDL only
```

---

## 4. Hard Pass Conditions

The Phase 898 closure gate must verify all 10 conditions:

| # | Condition |
|---|-----------|
| 1 | `ilc_core/network/d2d/truth_primitive_gossip_runtime.py` exists |
| 2 | `TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION` and `CDL_076_DEPENDENCY` tokens present |
| 3 | `TRUTH_PRIMITIVE_GOSSIP_TYPE = "truth_primitive_announced"` declared as module constant |
| 4 | Announcement payload is exactly `{node_id, primitive, agent_id, epoch, cdl_version}` — no full record content |
| 5 | `ILC_D2D_GOSSIP_PEERS` env var (comma-separated HTTPS URLs) activates gossip; absent → graceful skip |
| 6 | Submit CLI wired: gossip fires after CDL-075 persist; result includes `gossip_delivery` field |
| 7 | Absent `ILC_D2D_GOSSIP_PEERS` → `gossip_delivery: "deferred — gossip peers not configured"` (no crash) |
| 8 | Absent `ILC_TRUTH_GRAPH_STORE_PATH` → gossip not attempted (nothing to announce) |
| 9 | No mutation of LMDB store via gossip path |
| 10 | CDL-076 opened (Phase 893) and ratified (Phase 897) in CDL master log |

---

## 5. Phase Detail

### Phase 893 — CDL-076 Opening

**Deliverables:**
- CDL-076 row inserted in `docs/specs/ilc_constitutional_decision_log_v0.1.md` as `open`
- `docs/specs/ilc_cdl_076_truth_primitive_announcement_gossip_opening_893_v0.1.md`

**CDL-076 scope statement:**
CDL-076 ratifies the truth primitive announcement gossip extension: a new CDL-061 gossip type
(`"truth_primitive_announced"`) that carries a lightweight announcement payload after a truth
primitive node is persisted to the CDL-075 LMDB store. CDL-076 extends CDL-036 header-first
dissemination semantics to truth primitive nodes. Full-payload push is explicitly rejected per
CDL-036. The CID-addressed pull fetch protocol is deferred to CDL-077.

**Options under consideration for CDL-076:**
- Option A (rejected): full node record payload in gossip message — violates CDL-036
- Option B (rejected): push to all known peers unconditionally — no activation gate
- **Option C (selected):** lightweight announcement `{node_id, primitive, agent_id, epoch, cdl_version}`
  via `ILC_D2D_GOSSIP_PEERS` gate; fires only after confirmed CDL-075 persist

**Parent CDLs:** CDL-036 / CDL-061 / CDL-075

---

### Phase 894 — Runtime Implementation

**File:** `ilc_core/network/d2d/truth_primitive_gossip_runtime.py`

**Required tokens:**
```python
TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION = "truth_primitive_gossip_runtime_894.v0.1"
CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
TRUTH_PRIMITIVE_GOSSIP_TYPE = "truth_primitive_announced"
```

**Peer configuration:**
- Env var: `ILC_D2D_GOSSIP_PEERS` — comma-separated HTTPS peer endpoints
- Each peer validated with `validate_peer_endpoint()` from `gossip_peer_registry.py`
- If absent or empty: return `{"gossip_delivery": "deferred — gossip peers not configured"}`

**Core function:**
```python
def announce_truth_primitive(write_receipt: dict) -> dict:
    """
    Gossip a lightweight truth primitive announcement to configured peers.

    Fires after CDL-075 write_truth_primitive_result() confirms persistence.
    Uses CDL-061 HttpGossipTransportRuntime.send_gossip() per peer.

    Returns delivery receipt: {gossip_delivery, peers_attempted, peers_succeeded, version}
    """
```

**Announcement payload (CBOR-serialized):**
```python
{
    "node_id":     write_receipt["node_id"],      # CIDv1
    "primitive":   write_receipt["primitive"],     # e.g. "assert.truth"
    "agent_id":    envelope["agent_id"],
    "epoch":       envelope["epoch"],
    "cdl_version": CDL_076_DEPENDENCY,
}
```

**No full node record content in payload.** Per CDL-036: soft push-signal only.

**Dependency guard:** verify `HttpGossipTransportRuntime` version token at import time;
raise `RuntimeError` on mismatch (same pattern as existing dep-chain guards).

---

### Phase 895 — Submit CLI Wiring

**File:** `ilc_core/cli/d2e_submit_cli.py` (extension — Phase 895)

**Wire point:** after CDL-075 persist block, before building return dict:

```python
# CDL-076: announce to gossip peers when store path and peers are configured.
gossip_delivery: str = "deferred — gossip peers not configured"
if store_path and node_id:
    from ilc_core.network.d2d.truth_primitive_gossip_runtime import (
        announce_truth_primitive,
    )
    gossip_receipt = announce_truth_primitive(write_receipt)
    gossip_delivery = gossip_receipt["gossip_delivery"]
```

**Result dict addition:**
```python
"gossip_delivery": gossip_delivery,
```

**Version token update:** `D2E_SUBMIT_CLI_VERSION` remains `"d2e_submit_cli_874.v0.1"` —
Phase 895 is a wiring extension, not a new module version. Add
`CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"` as a new module constant.

---

### Phase 896 — Tests

**File:** `tests/test_phase_894_898_truth_primitive_gossip.py`

**Commit subject (for scope guard):**
`"feat(g8): phase 892-896 cdl-076 truth primitive announcement gossip"`

**Test coverage (minimum 18 tests):**

| Group | Tests |
|-------|-------|
| 1. Module existence + tokens | runtime file exists; version token; CDL-076/061/075 dep tokens; gossip type constant |
| 2. Announcement payload shape | exactly 5 fields; node_id is CIDv1; no record content leaked |
| 3. Absent peers → graceful skip | `ILC_D2D_GOSSIP_PEERS` unset → deferred receipt; no crash |
| 4. Absent store path → no gossip | `ILC_TRUTH_GRAPH_STORE_PATH` unset → gossip not attempted |
| 5. Per-peer send | mocked `send_gossip`: called once per peer; correct args |
| 6. Submit CLI wired | `gossip_delivery` field in result; absent peers → deferred string |
| 7. Subprocess CLI integration | `ilc submit` with store + peers set → `gossip_delivery` in JSON output |
| 8. No LMDB mutation | node count unchanged after announce_truth_primitive() |
| 9. Commit scope guard | Phase 896 commit touches only `ilc_core/network/d2d/` + `ilc_core/cli/` + `tests/` |

---

### Phase 897 — CDL-076 Ratification + Coherence Report + Capsule v5.27

**CDL-076 ratification:**
- CDL master log row updated from `open` → `ratified`
- Ratification evidence: `docs/specs/ilc_cdl_076_truth_primitive_announcement_gossip_ratification_evidence_897_v0.1.md`
- Atomic commit with `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=897`

**Coherence report:** `docs/specs/ilc_integration_coherence_report_897_v0.1.md`

**Capsule:** `docs/specs/ilc_antigravity_context_capsule_v5.27.md` — supersedes v5.26

**Capsule test count update:**

| Scope | Tests |
|-------|-------|
| Window 892–898 (gossip) | ~18 |
| Window 887–891 (query CLI) | 23 |
| Prior windows | 282 |
| **Total** | **~323** |

---

### Phase 898 — Closure Gate

**File:** `docs/specs/ilc_window_892_898_closure_gate_898_v0.1.md`

Verifies all 10 hard pass conditions. On PASS emits:

```
window_892_898_closed
capsule_v5_27_is_current_frontier
cdl_076_ratified
```

---

## 6. Forward Obligations Carried Forward

| Obligation | Next window | Evidence basis |
|------------|-------------|----------------|
| CDL-077: WANT-HAVE/WANT-BLOCK fetch + DoS prevention | Phase 899+ | Q4 architectural decision 2026-04-27 |
| star.map L3 routing (N-gram index, spectral) | H-series, post-RC1 | `star.map.ngram.route_index.v1.md`; H-014 pending |
| Multi-hop centrality attribution CDL | Future | SIM-MULTI-HOP-01 Phase 552 evidence available |
| Relay fee / two-sided ECU routing market | Future CDL | Design intent; SIM-COMMISSION-01 basis |
| HB-002 P2P bootstrap distribution | Re-evaluate each window closure | HB-001 closed; RC1 readiness watch |
| CDL-070 PQ migration ceremony | Deep audit window | SIM-MONETARY-01 prerequisite |
| Cross-epoch compaction / snapshot export | Deferred | CDL-075 carry-forward |

---

## 7. Sequence Constraints

1. Phase 893 (CDL-076 open) must precede Phase 894 (runtime implementation)
2. Phase 894 (runtime) must precede Phase 895 (CLI wiring)
3. Phase 895 (CLI wiring) must precede Phase 896 (tests)
4. Phase 896 (tests passing) must precede Phase 897 (ratification)
5. Phase 897 (ratification) must precede Phase 898 (closure gate)
6. No CDL-077 work may begin in this window

---

## 8. Governing Tokens

```
window_892_898_commissioned
cdl_076_extends_cdl_036_to_truth_primitive_nodes
cdl_076_announcement_gossip_only_no_full_payload
truth_primitive_announced_is_the_gossip_type
ilc_d2d_gossip_peers_is_the_activation_env_var
layer_1_of_4_network_delivery_architecture
cdl_077_is_the_fetch_layer_not_this_window
star_map_is_the_l3_routing_convergence_target
passive_ecu_formula_is_the_economic_incentive_basis
```
