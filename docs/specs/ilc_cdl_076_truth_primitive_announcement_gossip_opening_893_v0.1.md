# CDL-076 Truth Primitive Announcement Gossip — Opening 893 v0.1

Status: open
Date: 2026-04-27
Phase: 893
Window: 892–898

`cdl_076_opened_phase_893`
`cdl_076_truth_primitive_announcement_gossip`

---

## 1. Purpose

CDL-076 ratifies the truth primitive announcement gossip extension: a new CDL-061 gossip type
(`"truth_primitive_announced"`) that carries a lightweight announcement payload after a truth
primitive node is successfully persisted to the CDL-075 LMDB graph store.

This is the "soft push-signal" leg of the CDL-036 dissemination contract applied to truth
primitive nodes. The CID-addressed pull fetch leg is deferred to CDL-077.

`cdl_076_is_the_soft_push_signal_leg_of_cdl_036_for_truth_primitives`

---

## 2. Constitutional Basis

### 2.1 Parent CDLs

| CDL | Role |
|-----|------|
| CDL-036 | Governing dissemination contract — header-first + CID pull; "ILC leans pull, not push" |
| CDL-061 | Gossip HTTP envelope contract — CDL-076 adds a new gossip type within this contract |
| CDL-075 | Truth primitive graph persistence — CDL-076 fires after confirmed CDL-075 persist |
| CDL-042 | CLI framework — submit CLI extension carries the gossip wire point |

### 2.2 CDL-036 constraint

CDL-036 §4 tokens carried forward:

> *"header-first dissemination does not authorize full-payload push as the default transport rule."*
> *"ILC leans pull, not push."*
> *"pull-dominant with soft push-signals"*

CDL-076 Option C (selected) is consistent with all three. Options A and B are rejected precisely
because they violate this constraint.

---

## 3. Options Evaluated

### Option A — Full node record payload in gossip message

**Rejected.** Transmitting the complete CDL-075 node record in the gossip envelope violates
CDL-036's prohibition on full-payload push as the default transport rule. The full record is
available via CID-addressed pull fetch (CDL-077). Pushing it eagerly creates redundant
traffic and defeats the pull-dominant architecture.

### Option B — Push to all known peers unconditionally, no activation gate

**Rejected.** Gossip without an activation gate makes every `ilc submit` command a network
operation regardless of environment. This is incorrect behavior in development, testing, and
single-node RC0.1 deployments. CDL-075 established the env-var gate pattern
(`ILC_TRUTH_GRAPH_STORE_PATH`) for optional features; CDL-076 follows the same pattern.

### Option C — Lightweight announcement with activation gate (Selected)

**Selected.** A lightweight announcement payload `{node_id, primitive, agent_id, epoch, cdl_version}`
is gossiped via the CDL-061 envelope to configured peers only when `ILC_D2D_GOSSIP_PEERS` is set
and a CDL-075 persist has confirmed a `node_id`. Absent either condition: graceful skip with
descriptive receipt field. This is the soft push-signal per CDL-036.

`cdl_076_option_c_selected`

---

## 4. Ratified Decision (to be confirmed at Phase 897)

**CDL-076 ratifies Option C:**

> Truth primitive announcement gossip — lightweight `{node_id, primitive, agent_id, epoch,
> cdl_version}` payload via CDL-061 envelope with gossip type `"truth_primitive_announced"`,
> activated by `ILC_D2D_GOSSIP_PEERS` env var, fired only after confirmed CDL-075 persist.
> Full-payload push explicitly excluded per CDL-036. Pull fetch deferred to CDL-077.

---

## 5. Implementation Contract

### 5.1 New module

`ilc_core/network/d2d/truth_primitive_gossip_runtime.py`

Required module-level constants:
```python
TRUTH_PRIMITIVE_GOSSIP_RUNTIME_VERSION = "truth_primitive_gossip_runtime_894.v0.1"
CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"
CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
TRUTH_PRIMITIVE_GOSSIP_TYPE = "truth_primitive_announced"
```

### 5.2 Announcement payload (CBOR-serialized)

```python
{
    "node_id":     str,   # CIDv1 — content address of the persisted node
    "primitive":   str,   # e.g. "assert.truth", "validate.claim"
    "agent_id":    str,   # submitting agent's CDL-042 agent_id
    "epoch":       int,   # submission epoch
    "cdl_version": str,   # CDL_076_DEPENDENCY constant
}
```

No full node record content. No LMDB read in gossip path (payload sourced from write receipt).

### 5.3 Activation

- `ILC_D2D_GOSSIP_PEERS`: comma-separated HTTPS peer endpoints (e.g.
  `"https://peer1:8443,https://peer2:8443"`)
- Each endpoint validated with `validate_peer_endpoint()` from `gossip_peer_registry.py`
- If absent or empty: return `{"gossip_delivery": "deferred — gossip peers not configured", ...}`
- If `node_id` is None (edge-only primitive with no persist): gossip not attempted

### 5.4 Submit CLI wire point

In `ilc_core/cli/d2e_submit_cli.py` — after CDL-075 persist block:

```python
CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"

# ... after write_receipt = write_truth_primitive_result(store, envelope, result) ...

gossip_delivery = "deferred — gossip peers not configured"
if node_id:
    from ilc_core.network.d2d.truth_primitive_gossip_runtime import announce_truth_primitive
    gossip_receipt = announce_truth_primitive(write_receipt, envelope)
    gossip_delivery = gossip_receipt["gossip_delivery"]
```

Result dict includes: `"gossip_delivery": gossip_delivery`

### 5.5 No LMDB mutation in gossip path

The gossip path is read-free of LMDB. Announcement payload is derived entirely from the
`write_receipt` dict returned by `write_truth_primitive_result()`. No store open/close in
`announce_truth_primitive()`.

`no_lmdb_read_or_write_in_gossip_path`

---

## 6. Relationship to Layered Delivery Architecture

CDL-076 is Layer 1 of a four-layer delivery architecture established by research completed
2026-04-27 (MemPalace retrieval from active palace, confirmed in historical canon):

| Layer | CDL | Mechanism |
|-------|-----|-----------|
| **L1** | **CDL-076** | Announcement gossip — soft push-signal |
| L2 | CDL-077 | WANT-HAVE / WANT-BLOCK two-phase fetch; DoS prevention; direct peer handshake |
| L3 | star.map CDL | N-gram route index, spectral routing, location-agnostic CID discovery |
| L4 | Future CDL | Two-sided ECU routing market, relay fees, centrality attribution per fetch |

Forward obligations not in CDL-076 scope:
- `star.map.ngram.route_index.v1.md` — L3 routing
- H-015 spectral routing wiring — conditional on H-014 SIM-ROUTING-01
- SIM-MULTI-HOP-01 (Phase 552) evidence — multi-hop attribution CDL not yet opened
- Two-sided ECU ledger routing market — future CDL

---

## 7. Exclusion Tokens

```
cdl_076_excludes_full_payload_push
cdl_076_excludes_fetch_endpoint       (CDL-077)
cdl_076_excludes_want_have_want_block (CDL-077)
cdl_076_excludes_star_map_wiring      (H-series, post-RC1)
cdl_076_excludes_spectral_routing     (H-series, conditional)
cdl_076_excludes_dht                  (static peer config only)
cdl_076_excludes_routing_fee          (future CDL)
cdl_076_excludes_multi_hop_attribution (SIM-MULTI-HOP-01 basis; CDL not yet opened)
```

---

## 8. Forward Obligations

| Obligation | Vehicle | Status |
|------------|---------|--------|
| CID-addressed pull fetch | CDL-077 | Phase 899+ |
| WANT-HAVE probe protocol + DoS prevention | CDL-077 | Phase 899+ |
| star.map L3 routing layer | star.map CDL | H-series, post-RC1 |
| Multi-hop centrality attribution | Future CDL | SIM-MULTI-HOP-01 evidence available |
| Relay fee / routing market | Future CDL | Design intent; not yet simulated |
| HB-002 P2P bootstrap | Re-evaluate each closure | HB-001 closed |
| CDL-070 PQ migration | Deep audit window | SIM-MONETARY-01 prerequisite |

---

## 9. Canonical Anchors

- `docs/specs/ilc_phase_892_898_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- CDL-036 evidence: `docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md`
- CDL-061 evidence: `docs/specs/ilc_cdl_061_gossip_http_envelope_contract_ratification_evidence_561_v0.1.md`
- CDL-075 evidence: `docs/specs/ilc_cdl_075_truth_primitive_graph_persistence_ratification_evidence_883_v0.1.md`
- star.map spec: `docs/specs/star.map.ngram.route_index.v1.md`
- Passive ECU formula: `docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md`
