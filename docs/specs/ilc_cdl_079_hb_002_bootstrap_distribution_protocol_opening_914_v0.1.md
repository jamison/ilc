# CDL-079 HB-002 Bootstrap Distribution Protocol — Opening 914 v0.1

Status: open
Date: 2026-04-27
Window: 913–920
Phase: 914

---

## 1. CDL Summary

CDL-079 ratifies the peer-to-peer bootstrap distribution protocol for the ILC
network: the constitutional definition of how a new node can receive and verify
genesis bootstrap artifacts from existing peers using the CDL-077 fetch protocol,
without requiring out-of-band distribution (GitHub) as a trust anchor.

The model is **bundle-fetch**: a signed bootstrap bundle (peer list + genesis
reference + authority signature) is published as a content-addressed record by
bootstrap-capable nodes and fetched by new nodes via CDL-077 WANT-BLOCK from a
single operator-provided seed peer.

`cdl_079_is_hb_002_bootstrap_distribution_lock`
`bootstrap_bundle_fetch_via_cdl_077_no_separate_channel`

---

## 2. Motivation

CDL-073 (Phase 860, ratified) closed HB-001 and HB-003: genesis artifacts can now
be expressed as verifiable truth primitives with machine-legible schema. CDL-077
(Phase 904, ratified) provides the WANT-HAVE/WANT-BLOCK fetch protocol. These two
pieces together make HB-002 tractable without new transport infrastructure.

Without CDL-079:
- New nodes depend on GitHub-hosted bootstrap JSON for peer discovery (out-of-band trust anchor)
- The network is not self-distributing: a GitHub outage or compromise degrades bootstrap
- The CDL-077 fetch infrastructure has no bootstrap application layer on top of it

CDL-079 closes this gap by:
1. Defining the `bootstrap_bundle_v1` schema (signed peer list + genesis CID)
2. Specifying the fetch protocol (CDL-077 WANT-BLOCK of a known bundle CID from a seed peer)
3. Defining signature verification (ML-DSA-65, genesis authority key from CDL-073)
4. Wiring into `node_startup_runtime.py` via `ILC_BOOTSTRAP_SEED_PEER` / `ILC_BOOTSTRAP_BUNDLE_CID`

---

## 3. Options

### Option A — Separate bootstrap gossip channel (rejected)

A new CDL-061 gossip type (`"peer_announced"`) announces peer availability.
New nodes subscribe and collect peer announcements.

**Rejection reason:** Requires new transport-layer gossip channel, new gossip type,
new routing logic. CDL-077 already provides pull-on-demand fetch. A push gossip
channel for bootstrap is redundant infrastructure when a single WANT-BLOCK fetch
of a bundle CID achieves the same result.

### Option B — DHT-based peer discovery (rejected)

A Kademlia-style DHT allows new nodes to discover peers without a seed.

**Rejection reason:** DHT is complex, unratified infrastructure. The Phase 578
curated lineage lock explicitly rejects DHT for RC phase. Permissionless peer
discovery is a post-RC1 concern.

### Option C — CDL-077 bundle fetch with operator-provided seed (selected)

```
Operator provisions:
    ILC_BOOTSTRAP_SEED_PEER = "https://seed1.ilc.example"
    ILC_BOOTSTRAP_BUNDLE_CID = "bafyreiabc..."

New node:
    fetch_bootstrap_bundle(seed_peer, bundle_cid)
        → WANT-HAVE probe → WANT-BLOCK fetch
        → bundle = {peers, genesis_cid, signed_by, signature, cdl_version}
    verify_bootstrap_bundle_signature(bundle, genesis_authority_pubkey)
    extract_peer_endpoints(bundle) → promote into peer registry
```

`cdl_079_option_c_selected`
`bootstrap_bundle_reuses_cdl_077_want_block_path`

---

## 4. Implementation Contract

### 4.1 Bootstrap bundle schema (`bootstrap_bundle_v1`)

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
  "signature": "<ML-DSA-65 signature hex>",
  "cdl_version": "cdl_079_bootstrap_bundle_v1"
}
```

Signed payload (canonicalization):
```python
payload = {k: v for k, v in bundle.items() if k != "signature"}
signed_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
```

The `signed_by` public key must match the genesis authority key embedded in the
genesis-authority assertion (CDL-073 §2). This closes the trust chain.

### 4.2 Module tokens

**`ilc_core/network/d2d/bootstrap_fetch_runtime.py`:**
```python
BOOTSTRAP_FETCH_RUNTIME_VERSION = "bootstrap_fetch_runtime_915.v0.1"
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"
```

**`ilc_core/node/node_startup_runtime.py` (extension):**
```python
CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"
```

### 4.3 Core API

```python
def fetch_bootstrap_bundle(
    seed_peer_endpoint: str,
    bundle_cid: str,
) -> dict | None:
    """Fetch bootstrap bundle from seed peer via CDL-077 WANT-BLOCK.
    Returns parsed bundle dict or None if not found.
    Raises FetchTransportError on transport failure."""

def verify_bootstrap_bundle_signature(
    bundle: dict,
    genesis_authority_pubkey_hex: str,
) -> bool:
    """Verify ML-DSA-65 signature. Never raises. Returns True/False."""

def extract_peer_endpoints(bundle: dict) -> list[str]:
    """Extract normalized HTTPS endpoints from verified bundle.
    Invalid entries silently skipped."""
```

### 4.4 Env var integration (node_startup_runtime.py patch)

```
ILC_BOOTSTRAP_SEED_PEER    — HTTPS endpoint of seed peer (required for bootstrap mode)
ILC_BOOTSTRAP_BUNDLE_CID   — CIDv1 of bootstrap bundle (required for bootstrap mode)
```

Both present → bootstrap mode. Neither present → static mode (existing behavior).
One without the other → `bootstrap_mode_requires_both_seed_peer_and_bundle_cid` error.

### 4.5 Curated model preservation

The Phase 578 curated lineage contract is preserved in full:
- `candidate_discovery_not_active_peer_admission`
- `explicit_promotion_required_before_runtime_peer_use`
- Bundle verification (signature check) is the explicit promotion gate
- No automatic admission of unverified peers

`curated_lineage_contract_preserved_in_cdl_079`

---

## 5. Exclusion Tokens

```
no_permissionless_peer_admission_in_cdl_079       curated model only
no_dht_in_cdl_079                                 Kademlia/swarm rejected
no_separate_bootstrap_gossip_channel_in_cdl_079   CDL-077 reused
no_mdns_in_cdl_079                                LAN discovery rejected
no_auto_peer_promotion_without_bundle_verification explicit gate required
no_star_map_wiring_in_cdl_079                     CDL-080 window
no_new_cdl_beyond_079_in_window_913_920           one CDL only
```

---

## 6. Forward Obligations

| Obligation | Vehicle |
|------------|---------|
| Full permissionless peer discovery | Post-RC1 CDL |
| Bootstrap bundle rotation / revocation | Future CDL |
| Cross-peer bundle consistency verification | Future CDL |
| star.map N-gram route index (CDL-080) | Window 921–929 |

---

## 7. Parent CDLs

- **CDL-073**: Homoiconic bootstrap schema (genesis-authority key definition)
- **CDL-077**: WANT-HAVE/WANT-BLOCK fetch (transport protocol reused)
- **CDL-036**: Pull-dominant dissemination contract (governing)
