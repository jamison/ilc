# ILC Bootstrap Peer Source and Promotion Model v0.1

Status: planning spec
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This document separates peer sourcing, peer admission, and peer runtime
selection for the first release-candidate path.

## 2. Core rule

Candidate discovery is not active-peer admission.

The first release-candidate path uses curated bootstrap peers and explicit
promotion into the active runtime peer set.

## 3. Accepted peer sources for the first testbed

Accepted bootstrap sources are:
- a Genesis or bootstrap node endpoint controlled by the operator set
- a curated GitHub-hosted bootstrap JSON file
- a local operator-managed override file

These are sources of candidate or approved peers, depending on trust level.
They are not automatic admission authorities.

## 4. Rejected sources for the first testbed

The following remain out of scope:
- DHT or swarm discovery
- mDNS or LAN discovery
- open public bulletin-board discovery
- invitation chains that auto-admit peers
- LLM-driven autonomous peer admission

## 5. Required separation of files

The model uses four distinct file classes.

### 5.1 Approved runtime peers

Authoritative file for the active runtime peer set.

Recommended path:
- `/etc/ilc/node_config.json`

This file is consumed by startup/runtime.

### 5.2 Curated bootstrap peers

Curated source of known bootstrap endpoints.

Recommended control-plane path:
- `testbed/bootstrap_peers.json`

This file may be sourced from GitHub or a bootstrap node, but it is still
curated input, not autonomous discovery.

### 5.3 Candidate discovery cache

Append-only discovery cache for machine-written observations.

Recommended path:
- `testbed/peer_candidates.ndjson`

This file may be written by OpenClaw-assisted tooling or operator scripts, but
must not be loaded directly into the active peer registry.

### 5.4 Local operator overrides

Manual allow, deny, or pin rules.

Recommended path:
- `testbed/peer_overrides.json`

## 6. Promotion flow

The required promotion flow is:
1. source candidate endpoints
2. test HTTPS reachability
3. capture node metadata and TLS fingerprint
4. record candidate result
5. apply operator policy and overrides
6. promote approved peers into the active runtime config

No step may skip directly from discovery to live admission.

## 7. Minimum bootstrap entry schema

Each bootstrap entry must contain at least:
- `node_id`
- `network_id`
- `endpoint`
- `transport_kind`
- `tls_fingerprint`
- `source`
- `status`
- `last_verified_at`

Example:

```json
{
  "node_id": "node-alpha",
  "network_id": "testnet-0",
  "endpoint": "https://node-alpha.example.org:19571",
  "transport_kind": "http",
  "tls_fingerprint": "sha256:...",
  "source": "genesis-bootstrap",
  "status": "approved",
  "last_verified_at": "2026-04-01T12:00:00Z"
}
```

## 8. OpenClaw-assisted discovery rule

OpenClaw or similar tooling may:
- fetch curated bootstrap lists
- resolve DNS
- test HTTPS reachability
- inspect TLS certificates
- append candidate records
- recommend promotions

OpenClaw or similar tooling may not silently rewrite the authoritative active
peer set.

## 9. Forward path

Later lanes may add richer bootstrap and discovery logic, but only after an
explicit governance lane opens for:
- dynamic discovery
- public admission policy
- reputation exchange or trust graph signaling
