# ILC Public Fetch/P2P Activation Candidate Default Off 1313 v0.1

Status: implemented / readiness-only / default-off / no public transport claim
Date: 2026-05-11
Phase: 1313
Owner lane: G8 graph-native sidecars / Gap 10 / CDL-087 public-path readiness

Required tokens:

```text
public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1
rust_public_p2p_substrate_gate_status_recorded_phase_1313
public_p2p_default_off_phase_1313
public_fetch_serving_default_off_phase_1313
transport_public_path_activation_not_authorized_phase_1313
phase_1314_wallet_withdrawal_transfer_spend_preflight_next
public_rc_remains_blocked_after_phase_1313
```

Phase 1313 was executed after explicit human authorization:

```text
GO Phase 1313
```

This phase records a deterministic default-off public fetch/P2P readiness
candidate at `ilc_core/sidecars/public_fetch_p2p_readiness.py`. It does not
authorize public P2P, public fetch serving, a public listener, peer discovery,
non-loopback bind, wildcard bind, public host bind, public sidecar/projection
serving, source export, package publication, release artifacts, release keys,
release envelopes, signing, wallet withdrawal, ECU minting, or ILC settlement.

## 0. Discovery Discipline

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | The seven Phase 1313 required tokens existed only in the executable prompt and prompt-draft tests before implementation. They are now carried into code, tests, this spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.53, Roadmap v1.1, network forward planning, and graph-native sidecar architecture. |
| Section 0b Concept-discovery search | Searched Rust public P2P, Quinn, libp2p, `network.rs`, public fetch, public P2P, listener, peer discovery, non-loopback, TransportPrincipal, CDL-087, hostile network, and default-off terms across docs, code, tests, and MemPalace advisory results. |
| Section 0c Contradiction and non-claim search | Confirmed no public transport authority: no public P2P, no public fetch serving, no public listener, no peer discovery, no non-loopback bind, no public sidecar/projection serving, no source/release/signing authority, no CDL-088, no wallet/ECU/ILC authority. |
| Section 0d Source expansion and newly discovered tokens | Direct-read PLANNING_INDEX, Capsule v5.53, STATUS tail, Window 1303-1316 lock/guidance, transport/value forward planning, Phase 1296 hostile-network plan, Phase 1298 bind/listener preflight, Launch Roadmap v1.1, CDL register, `ilc_consensus/src/network.rs`, Python HTTP fetch/gossip runtime, Phase 1277/1278 `PUBLIC_RC_EXCLUDE` preflight helpers, and Phase 1309-1312 sidecar code/tests. |

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

## 1. Gate Classification

Phase 1313 classifies the Rust public-P2P substrate gate as:

```text
gate_required_not_satisfied
```

Rationale:

- `ilc_consensus/src/network.rs` exists and contains Rust QUIC/rustls validator
  gossip substrate with mTLS peer binding, timeouts, and frame-size bounds.
- Current canon still requires a separate public-P2P substrate
  ADR/integration gate before public fetch/P2P activation.
- The existing Rust path is not, by itself, an explicit public D2D/fetch
  activation authority.
- Python HTTP fetch/gossip runtimes remain devnet/test regression surfaces and
  are not public-P2P substrates.
- Older Phase 1277/1278 public-path preflight helpers remain
  `PUBLIC_RC_EXCLUDE` and are not directly promotable.

The Phase 1313 readiness packet therefore records:

```text
rust_public_p2p_substrate_gate_still_required_phase_1313
```

## 2. Implemented Readiness Packet

The new module provides:

- `public_fetch_p2p_readiness_required_tokens()`
- `public_fetch_p2p_readiness_candidate_manifest()`
- `build_public_fetch_p2p_readiness_candidate()`
- `validate_public_fetch_p2p_readiness_candidate()`
- `public_fetch_p2p_readiness_candidate_ref()`
- `export_public_fetch_p2p_readiness_candidate_json()`

The packet is deterministic and canonical:

- JSON export uses `json.dumps(..., sort_keys=True, allow_nan=False)`.
- Floats, cycles, non-JSON values, oversized text, excessive depth, and
  excessive payload nodes are rejected.
- The packet carries a `candidate_sha256` over the canonical payload.
- Validation also rejects readiness-verdict drift, source-evidence drift,
  public-activation requirement drift, Rust `network.rs` path drift, and
  contradictory Rust gate status/evidence combinations.
- The packet records the TransportPrincipal admission sidecar dependency as
  local-only and public-path blocked.

## 3. Default-Off Matrix

| Surface | Phase 1313 disposition |
|---------|------------------------|
| Public P2P | Default off; token `public_p2p_default_off_phase_1313`. |
| Public fetch serving | Default off; token `public_fetch_serving_default_off_phase_1313`. |
| Transport public-path activation | Not authorized; token `transport_public_path_activation_not_authorized_phase_1313`. |
| Public listener | Default off; no listener, socket, or HTTP route added. |
| Peer discovery | Default off; no peer-discovery path added. |
| Non-loopback, wildcard, or public host bind | Default off. |
| Python HTTP fetch/gossip runtime | Classified as devnet/test, not public-P2P substrate. |
| Rust QUIC/rustls network code | Evidence exists, but public-P2P ADR/integration gate remains required. |
| Sidecar/projection public serving | Not enabled. |
| Release/publication/signing | Not authorized. |

## 4. Registry Impact

The sidecar registry now includes:

```text
public_fetch_p2p_readiness_candidate
```

with authority gate:

```text
phase_1313_default_off_readiness_only_rust_public_p2p_gate_required
```

and implementation status:

```text
readiness_candidate_recorded_phase_1313_default_off
```

This is local/package metadata only. It does not create a server, listener,
socket, HTTP route, endpoint, bind surface, peer-discovery path, public P2P
surface, public fetch surface, wallet action, ECU mint, or ILC settlement
surface.

## 5. Non-Claims

Phase 1313 does not authorize:

- public RC claim or public launch claim;
- source export, source publication, package publication, release artifact production, release keys, release envelopes, or signing;
- public claimability/API activation or public verifier service;
- public P2P, public fetch serving, public sidecar/projection serving, non-loopback bind, public listener, or peer discovery;
- helper promotion, marker removal, helper stripping, or public export stripping;
- Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, or CDL-088 opening;
- wallet withdrawal, transfer, spend, wallet signing, ledger-write, ECU minting, ILC settlement, or withdrawal runtime;
- public confidential messaging or public confidential coordination serving.

## 6. Next Gate

Phase 1314 is sensitive and requires explicit `GO Phase 1314`.

```text
phase_1314_wallet_withdrawal_transfer_spend_preflight_next
```
