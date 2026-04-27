# ILC Window 913–920 Sequence Lock

Status: locked
Date: 2026-04-27
Window: 913–920
Topic: CDL-079 — P2P Bootstrap Distribution Protocol (HB-002)

`window_913_920_commissioned`
`cdl_079_hb_002_p2p_bootstrap_distribution`

---

## 1. Authorization Basis

This window is authorized by:

- Window 906–912 closure gate `9340eb92`:
  `hb_002_is_next_window_primary_obligation`
- `docs/specs/ilc_window_906_929_forward_planning_v0.1.md` §4
- `docs/specs/ilc_homoiconic_bootstrap_forward_obligations_v0.1.md` §2 (HB-002)
- HB-001 (genesis-authority assertion schema) — **closed** (CDL-073, Phase 860)
- HB-003 (Layer 0 bundle truth-primitive schema) — **closed** (CDL-073, Phase 860)
- CDL-077 WANT-HAVE/WANT-BLOCK fetch — **ratified** (Phase 904): provides the fetch
  infrastructure that makes HB-002 implementable without a separate channel

Pre-phase open questions resolved before this sequence lock:

**Q1: Can HB-002 reuse CDL-077 (WANT-BLOCK) rather than introducing a separate bootstrap channel?**

Answer: **Yes.** The bootstrap bundle (signed JSON manifest: peer endpoints +
genesis CID + authority signature) is served as a record by any bootstrap-capable
node. A new node with one operator-provided seed peer endpoint and bundle CID can
WANT-BLOCK that bundle via CDL-077, verify it, and populate its peer registry.
No separate gossip channel, no DHT, no mDNS required.

`hb_002_uses_cdl_077_want_block_no_separate_channel`

**Q2: Does HB-002 need to implement permissionless peer admission?**

Answer: **No.** The Phase 578 curated lineage lock (`curated_genesis_lineage_testnet_only`)
remains in force. The bootstrap bundle is operator-curated. Peers listed in the
bundle are admitted via the existing explicit-promotion model. Permissionless
admission is a post-RC1 concern.

`hb_002_curated_bundle_explicit_promotion_only`

**Q3: Does star.map get CDL-079 or is HB-002 CDL-079?**

Answer: **HB-002 gets CDL-079.** Star.map N-gram route index is renumbered CDL-080
(Window 921–929). This resolves the forward planning doc (which was written before
CDL-078 ratified and assigned CDL-079 speculatively to star.map).

`cdl_079_assigned_to_hb_002_star_map_renumbered_cdl_080`

---

## 2. Architectural Grounding

### 2.1 Problem statement

As of capsule v5.29:
- A new node requires a static peer list in its config JSON (operator-managed)
- Genesis artifacts are distributed via GitHub-hosted JSON (out-of-band trust anchor)
- HB-001/003 are closed: genesis records CAN be expressed as verifiable truth primitives
- HB-002 is the bridge: distribute those verified records to new nodes via the protocol itself

### 2.2 Solution: CDL-077 bootstrap bundle fetch

```
Operator provisions new node with:
    ILC_BOOTSTRAP_SEED_PEER = "https://seed1.ilc.example"
    ILC_BOOTSTRAP_BUNDLE_CID = "bafyreiabc..."   # known bundle CID

New node startup:
    1. fetch_bootstrap_bundle(seed_peer, bundle_cid)
          → WANT-HAVE /fetch/want-have {node_id: bundle_cid}
          → WANT-BLOCK /fetch/want-block {node_id: bundle_cid}
          → bundle = {peers: [...], genesis_cid: "...", signed_by: "...", cdl_version: "..."}
    2. verify_bootstrap_bundle_signature(bundle, genesis_authority_key)
    3. Peer list promoted into gossip_peer_registry (explicit promotion model)
    4. Node continues with normal startup (node_startup_runtime.py)
```

No GitHub required. No separate channel required. One seed peer + one bundle CID
is sufficient to bootstrap the full peer set.

### 2.3 Bootstrap bundle schema

```json
{
  "schema_version": "bootstrap_bundle_v1",
  "bundle_cid": "<CIDv1 of this bundle>",
  "genesis_cid": "<CIDv1 of genesis record>",
  "peers": [
    {"endpoint": "https://peer1.ilc.example", "node_id": "<CIDv1>"},
    ...
  ],
  "signed_by": "<ML-DSA-65 genesis authority pubkey hex>",
  "signature": "<signature over canonical JSON excluding signature field>",
  "cdl_version": "cdl_079_bootstrap_bundle_v1"
}
```

Canonicalization: `json.dumps(bundle_without_signature, sort_keys=True).encode()`

**Verification path:** `signed_by` key must match the genesis authority key embedded
in the genesis-authority assertion (CDL-073 §2). This closes the trust chain:
genesis authority key → bootstrap bundle signature → peer list.

`bootstrap_bundle_trust_chain_via_cdl_073_genesis_authority_key`

### 2.4 Startup integration

`node_startup_runtime.py` (Phase 570) gains two optional env vars:

```
ILC_BOOTSTRAP_SEED_PEER    — HTTPS endpoint of one seed peer
ILC_BOOTSTRAP_BUNDLE_CID   — CIDv1 of the bootstrap bundle to fetch
```

If both are set → bootstrap fetch mode: fetch bundle, verify, promote peers.
If neither is set → static mode: load peers from config JSON (existing behavior).
If only one is set → error (both required for bootstrap mode).

`static_peer_config_fallback_preserved`

### 2.5 Scope constraints

```
no_permissionless_peer_admission_in_window_913_920
no_dht_in_window_913_920
no_mdns_in_window_913_920
no_auto_peer_promotion_without_bundle_verification
no_star_map_wiring_in_window_913_920
no_onion_routing_in_window_913_920
no_hb_001_or_hb_003_rework_in_window_913_920    already closed
```

---

## 3. Window Scope

### 3.1 In scope

| Phase | Topic |
|-------|-------|
| 913 | Sequence lock (this document) |
| 914 | CDL-079 opening document |
| 915 | `bootstrap_fetch_runtime.py` — fetch + verify bootstrap bundle via CDL-077 |
| 916 | `node_startup_runtime.py` patch — `ILC_BOOTSTRAP_SEED_PEER` + `ILC_BOOTSTRAP_BUNDLE_CID` integration |
| 917 | Tests |
| 918 | CDL-079 ratification + coherence report + capsule v5.30 |
| 919 | Closure gate |
| 920 | Spare / overflow |

### 3.2 Explicit exclusions

```
no_permissionless_peer_admission
no_dht_or_swarm_discovery
no_mdns_or_lan_discovery
no_invitation_chains_that_auto_admit_peers
no_separate_bootstrap_gossip_channel
no_star_map_wiring
no_hb_001_or_hb_003_rework
no_cdl_080_or_higher_in_this_window
```

---

## 4. Hard Pass Conditions

The Phase 919 closure gate must verify all 8 conditions:

| # | Condition |
|---|-----------|
| 1 | `ilc_core/network/d2d/bootstrap_fetch_runtime.py` exists |
| 2 | `BOOTSTRAP_FETCH_RUNTIME_VERSION` and `CDL_079_DEPENDENCY` tokens present |
| 3 | `fetch_bootstrap_bundle(seed_peer, bundle_cid)` fetches bundle via CDL-077 WANT-HAVE/WANT-BLOCK |
| 4 | `verify_bootstrap_bundle_signature(bundle, genesis_authority_key)` verifies ML-DSA-65 signature |
| 5 | `node_startup_runtime.py` patched: `ILC_BOOTSTRAP_SEED_PEER` + `ILC_BOOTSTRAP_BUNDLE_CID` → bootstrap mode |
| 6 | Static peer config fallback preserved (existing behavior when env vars absent) |
| 7 | No DHT, no swarm discovery, no automatic peer admission introduced |
| 8 | CDL-079 opened (Phase 914) and ratified (Phase 918) in CDL master log |

---

## 5. Phase Detail

### Phase 914 — CDL-079 Opening

**Deliverables:**
- CDL-079 row inserted in `docs/specs/ilc_constitutional_decision_log_v0.1.md` as `open`
- `docs/specs/ilc_cdl_079_hb_002_bootstrap_distribution_protocol_opening_914_v0.1.md`

**Options under consideration:**
- Option A (rejected): separate bootstrap gossip channel (new CDL-061 gossip type)
- Option B (rejected): DHT-based peer discovery
- **Option C (selected):** reuse CDL-077 WANT-BLOCK fetch; bootstrap bundle is a signed
  JSON manifest fetched by CID from a seed peer; operator provides seed peer + bundle CID;
  curated explicit-promotion model preserved

**Parent CDLs:** CDL-073 (bootstrap schema/genesis authority key) / CDL-077 (fetch protocol) / CDL-078 (relay incentive — bootstrap bundle serves as a truth primitive node serving event)

---

### Phase 915 — Bootstrap Fetch Runtime

**File:** `ilc_core/network/d2d/bootstrap_fetch_runtime.py`

**Required tokens:**
```python
BOOTSTRAP_FETCH_RUNTIME_VERSION = "bootstrap_fetch_runtime_915.v0.1"
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"
```

**Core functions:**
```python
def fetch_bootstrap_bundle(
    seed_peer_endpoint: str,
    bundle_cid: str,
) -> dict | None:
    """Fetch the bootstrap bundle from a seed peer via CDL-077 WANT-BLOCK.

    Returns parsed bundle dict if successful, None if not found.
    Raises FetchTransportError on transport failure.
    """

def verify_bootstrap_bundle_signature(
    bundle: dict,
    genesis_authority_pubkey_hex: str,
) -> bool:
    """Verify the ML-DSA-65 signature on a bootstrap bundle.

    Canonicalization: json.dumps(bundle_without_signature, sort_keys=True).encode()
    Returns True if signature valid, False otherwise. Never raises.
    """

def extract_peer_endpoints(bundle: dict) -> list[str]:
    """Extract validated peer HTTPS endpoints from a verified bootstrap bundle.

    Returns list of normalized endpoints (via validate_peer_endpoint).
    Invalid entries silently skipped.
    """
```

**Dep-chain guard:** verify `TRUTH_PRIMITIVE_FETCH_RUNTIME_VERSION` at import time.

---

### Phase 916 — Node Startup Patch

**File:** `ilc_core/node/node_startup_runtime.py` (patch)

**New function:**
```python
def bootstrap_node_startup(
    bootstrap_seed_peer: str,
    bootstrap_bundle_cid: str,
    genesis_authority_pubkey_hex: str,
) -> NodeStartupContext:
    """Bootstrap startup mode: fetch + verify bundle, promote peers, return context.

    Raises BootstrapError if bundle not found, signature invalid, or no peers.
    """
```

**New exception:**
```python
class BootstrapError(Exception):
    def __init__(self, token: str) -> None: ...
```

**Env var logic** (integrated into existing startup flow):
```python
seed_peer = os.environ.get("ILC_BOOTSTRAP_SEED_PEER", "").strip()
bundle_cid = os.environ.get("ILC_BOOTSTRAP_BUNDLE_CID", "").strip()

if bool(seed_peer) != bool(bundle_cid):
    raise ValueError("bootstrap_mode_requires_both_seed_peer_and_bundle_cid")

if seed_peer and bundle_cid:
    # bootstrap mode
    ctx = bootstrap_node_startup(seed_peer, bundle_cid, genesis_authority_pubkey_hex)
else:
    # static mode (existing behavior)
    ctx = load_static_peer_config(config_path)
```

**Version token:** `NODE_STARTUP_RUNTIME_VERSION` remains `"node_startup_runtime_570.v0.1"`.
Add `CDL_079_DEPENDENCY` as a new module constant.

---

### Phase 917 — Tests

**File:** `tests/test_phase_913_920_cdl_079_hb_002_bootstrap.py`

**Commit subject (for scope guard):**
`"feat(g8): phase 914-917 cdl-079 hb-002 bootstrap distribution protocol"`

**Test coverage (minimum 22 tests):**

| Group | Tests |
|-------|-------|
| 1. Module existence + tokens | runtime file exists; version token; CDL-079/077/073 dep tokens |
| 2. fetch_bootstrap_bundle | success → returns bundle dict; 404 → None; transport error → raises |
| 3. verify_bootstrap_bundle_signature | valid signature → True; invalid → False; missing fields → False |
| 4. extract_peer_endpoints | valid endpoints returned; invalid entries skipped; empty bundle → [] |
| 5. node_startup integration | both env vars set → bootstrap mode; neither set → static mode; one set → error |
| 6. Explicit promotion only | bootstrap does not auto-promote without verification |
| 7. No DHT/swarm | no DHT call in source scan |
| 8. CDL-079 in master log | CDL master log contains CDL-079 row with opened_phase: 914 |
| 9. Commit scope guard | commit touches only `ilc_core/network/d2d/`, `ilc_core/node/`, `tests/`, `docs/` |

---

### Phase 918 — CDL-079 Ratification + Coherence + Capsule v5.30

**CDL-079 ratification:**
- CDL master log row updated from `open` → `ratified`
- Ratification evidence: `docs/specs/ilc_cdl_079_hb_002_bootstrap_distribution_ratification_evidence_918_v0.1.md`
- Atomic commit with `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=918`

**Coherence report:** `docs/specs/ilc_integration_coherence_report_918_v0.1.md`
- Key check: static peer config fallback preserved — existing tests still pass
- Key check: bootstrap bundle signature verification is non-optional before peer promotion
- Key check: `fetch_bootstrap_bundle()` is additive on CDL-077 — `handle_want_block_request()` unchanged
- Key check: no automatic peer admission; curated explicit-promotion model intact

**Capsule:** `docs/specs/ilc_antigravity_context_capsule_v5.30.md` — supersedes v5.29

**Estimated test count:**

| Scope | Tests |
|-------|-------|
| Window 913–920 (CDL-079) | ~22 |
| Prior windows | 393 |
| **Total (estimated)** | **~415** |

---

### Phase 919 — Closure Gate

**File:** `docs/specs/ilc_window_913_920_closure_gate_919_v0.1.md`

On PASS emits:
```
window_913_920_closed
capsule_v5_30_is_current_frontier
cdl_079_ratified
hb_002_bootstrap_distribution_protocol_locked
star_map_cdl_080_is_next_l3_obligation
```

---

## 6. Forward Obligations Carried Forward

| Obligation | Next window | Evidence basis |
|------------|-------------|----------------|
| CDL-080: star.map N-gram route index (renumbered from CDL-079) | Window 921–929 | H-series SIM-ROUTING-01 retrieval required before sequence lock |
| SIM-RELAY-01: serve-rate calibration | Post-RC1 | CDL-078 forward obligation |
| CDL-001 packaging track | Pre-launch | genesis_blocker |
| CDL-070 PQ migration ceremony | Deep audit | SIM-MONETARY-01 prerequisite |

---

## 7. Sequence Constraints

1. Phase 914 (CDL-079 open) must precede Phase 915 (runtime)
2. Phase 915 (runtime) must precede Phase 916 (wiring patch)
3. Phase 916 (wiring) must precede Phase 917 (tests)
4. Phase 917 (tests passing) must precede Phase 918 (ratification)
5. Phase 918 (ratification) must precede Phase 919 (closure gate)
6. No DHT, no swarm discovery, no separate bootstrap channel in this window

---

## 8. Governing Tokens

```
window_913_920_commissioned
cdl_079_hb_002_p2p_bootstrap_distribution
hb_002_uses_cdl_077_want_block_no_separate_channel
hb_002_curated_bundle_explicit_promotion_only
cdl_079_assigned_to_hb_002_star_map_renumbered_cdl_080
bootstrap_bundle_trust_chain_via_cdl_073_genesis_authority_key
static_peer_config_fallback_preserved
no_permissionless_peer_admission_in_window_913_920
```
