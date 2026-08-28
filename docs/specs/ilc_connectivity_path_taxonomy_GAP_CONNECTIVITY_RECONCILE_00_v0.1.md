# ILC Connectivity Path Taxonomy and Claim Boundaries
Version: v0.1
Phase: GAP-CONNECTIVITY-RECONCILE-00
Date: 2026-08-28
Status: ratified-spec-candidate
Governs: connectivity model, path bindings, connectivity modes, relay admission, probe observer policy, CDL-112 scope
Authority: ADR-0011, ADR-0025, ADR-0039, CDL-103

## 1 - 8-Layer Path Stack

| Layer | Name | Description | Governing authority |
|---:|---|---|---|
| 1 | Identity/Authority layer | AgentID, BLS public key, invite provenance, proof-of-possession, and lineage evidence that establish which actor is making a connectivity claim. | CDL-017, CDL-068 |
| 2 | Connectivity layer | Reachability mode, NAT detection result, relay availability, probe receipt, and declared connectivity state. | ADR-0039, CDL-112 (proposed) |
| 3 | Transport layer | QUIC/mTLS for validator consensus; HTTP/3-over-QUIC or HTTP/2-over-TLS fallback for D2D gossip and serving. | ADR-0011, ADR-0025 |
| 4 | Message/Payload layer | Signed bundles, truth primitives, invite nullifiers, peer advertisements, connectivity receipts, and relay admission handshakes. | CDL-103, CDL-074 |
| 5 | Graph/Registry layer | Content-addressed node IDs, LMDB records, signed validator endpoint assertions, and read-only endpoint projections. | ADR-0039, CDL-098 |
| 6 | Selection/Routing layer | Peer selection, deterministic introduction sampling, gossip fan-out, relay slot assignment, and future candidate endpoint preference order. | CDL-103 |
| 7 | Trust/Verification layer | ML-DSA-65 signature verification, invite provenance check, BLS PoP, TLS endpoint assertion verification, and relay pass-through verification. | CDL-068 |
| 8 | Economic/Reputation layer | Serve-event to centrality delta, reputation effects, and later relay incentive accounting after explicit governance activation. | CDL-078 |

The layers are ordered by authority dependency, not by packet order. A transport path is not authoritative unless the identity, graph, and trust layers above it validate the claim it carries.

## 2 - 5 Path Bindings

| Path binding | Transport mechanism | Peer selection | Usage context | Non-claims |
|---|---|---|---|---|
| Local fast path | Same-machine loopback, UDS, or future local IPC. | Loopback only. | Intra-process and local sidecar communication for co-located agents. | Does not imply network reachability; not a serving path. |
| Bootstrap/fetch path | HTTPS plus ML-DSA-65 signed bundle verification. | Seed peers and CDL-079 HB-002 WANT-HAVE/WANT-BLOCK. | Initial identity bundle fetch, release artifacts, bootstrap graph slices, and signed seed material. | Not a gossip path; PyPI/GitHub fallback is not removed pre-RC. |
| Slow D2D path | HTTP/3-over-QUIC or HTTP/2-over-TLS fallback, carrying bounded signed gossip envelopes. | CDL-103 peer discovery and signed advertisements. | D2D gossip, peer advertisements, invite/nullifier propagation, non-urgent graph serving, and WAN serving. | Relay fallback may be included; not consensus; not validator admission. |
| Fast consensus path | Rust/Mysticeti QUIC/mTLS active validator transport. | Validator registry and ADR-0039 endpoint projection. | Active validator consensus only. | Not available until validator admission; relay version must be pass-through and must not re-sign consensus messages. |
| Relay/rendezvous path | Pass-through TCP/QUIC forwarding plus rendezvous allocation. | Invite-provenance-gated AgentID under Option A. | Fallback reachability for NAT-blocked peers and validator-capable observers. | Does not grant validator authority; does not terminate or re-origin consensus messages; no production incentives pre-RC. |

The path bindings deliberately separate bootstrap trust from bootstrap transport. A centralized host may carry bytes during pre-RC, but the trust claim comes from signed artifacts, canonical hashes, and graph authority.

## 3 - 9 Connectivity Modes

| Mode | Code | Description | Preconditions | Serving peer active? | Validator eligible? | Transition from |
|---|---|---|---|---|---|---|
| Local only | `local_only` | Installed identity exists, but no network reachability has been proven. | AgentID provisioned; all network operations fail or have not been attempted. | No | No | Initial state |
| Outbound only | `outbound_only` | Instance can fetch, submit, or gossip outbound but cannot receive inbound. | At least one successful outbound probe; no inbound route. | Yes, outbound only | No | `local_only` after first successful outbound |
| NAT-traversed direct candidate | `nat_traversed_direct` | Automatic traversal produced a candidate public endpoint. | Traversal receipt exists; external verification pending. | Yes | No | `outbound_only` after successful traversal/probe |
| Relay reachable | `relay_reachable` | Instance is reachable through relay/rendezvous fallback. | Invite-provenance-gated relay slot active. | Yes | No | `outbound_only` or `nat_traversed_direct`; fallback when direct fails |
| Direct public | `direct_public` | Direct inbound endpoint is externally verified. | External probe confirms IP/port; no NAT obstruction for selected port. | Yes | No, until admitted | `nat_traversed_direct` or `outbound_only` |
| Validator observer via relay | `validator_observer_relay` | Validator-capable observer reachable through relay, but not an active consensus validator. | Relay slot active; validator candidate state exists. | Yes | Observer only, not active | `relay_reachable` after validator enrollment begins |
| Validator observer direct | `validator_observer_direct` | Validator-capable observer directly reachable, but not an active consensus validator. | Direct endpoint verified; validator candidate state exists. | Yes | Observer only, not active | `direct_public` after validator enrollment begins |
| Validator direct | `validator_direct` | Admitted active validator using direct endpoint. | Validator admission complete; direct endpoint verified; current endpoint assertion valid. | Yes | Yes, active | `validator_observer_direct` after admission |
| Validator relay | `validator_relay` | Admitted active validator using pass-through relay endpoint. | Validator admission complete; relay slot active; relay pass-through invariant verified. | Yes | Yes, active | `validator_observer_relay` after admission |

Transition rules:

| Rule | Requirement |
|---|---|
| No upward authority by advertisement alone | A CDL-103 `PeerAdvertisement` can move a serving instance between discovery states but cannot grant validator, wallet, economic, public-serving, or claimability authority. |
| Direct beats relay when verified | If direct and relay endpoints are both live, direct transport is preferred for ordinary serving and validator consensus unless policy explicitly chooses relay for privacy or resilience testing. |
| Candidate direct is not direct public | `nat_traversed_direct` records a local traversal result only. It becomes `direct_public` only after an ILC probe observer verifies inbound reachability. |
| Validator observer is not active validator | `validator_observer_*` modes mean validator-capable software and key material may exist, but BFT quorum participation remains unavailable until validator admission and endpoint checks pass. |
| Relay pass-through is mandatory for consensus | Any relay used by `validator_relay` must forward encrypted consensus traffic without terminating TLS/QUIC, re-signing, rewriting, or re-originating validator messages. |
| Mode declarations are receipts, not authority | A local mode receipt is evidence for later verification. It is not itself a graph authority edge until signed, admitted, and accepted under the relevant governance surface. |

## 4 - Relay Admission Policy: Option A

**Relay admission policy: Option A - invite-provenance-gated.** A relay slot may only be issued to an AgentID that completed a Genesis-traced install (confirmed invite bundle, PoP-verified nullifier, ML-DSA-65 AgentID). An unverified or anonymous install cannot obtain a relay slot. This policy applies pre-RC and post-RC unless explicitly superseded by a future CDL.

Pre-RC relay admission is a safety gate, not a reward gate. The relay service may help NAT-blocked installs become useful, but relay admission does not create validator authority, does not satisfy endpoint-assertion requirements by itself, and does not authorize production relay incentives.

Required relay slot constraints:

| Constraint | Rule |
|---|---|
| One active slot per AgentID | An AgentID may hold at most one active relay slot at a time unless a future CDL authorizes a multi-slot exception. |
| Slot cap | The suggested pre-RC operational cap is 500 concurrent relay slots per VPS validator; this is a planning value, not yet codified as protocol law. |
| Invite lineage | The relay admission request must include a verified invite lineage rooted in Genesis-traced onboarding evidence. |
| Nullifier binding | The relay request must be bound to the redeemed invite nullifier or a successor privacy-preserving nullifier proof. |
| PoP binding | The requesting AgentID must prove control of the onboarded key. |
| Operator cost | Pre-RC relay operation is operator-funded. CDL-078 incentives are not active for production relay infrastructure. |
| Abuse controls | Rate limits, slot TTLs, and revocation receipts must be defined before public relay deployment. |

## 5 - Probe Observer Policy

**Probe observer policy: ILC bootstrap nodes only.** The external IP/port of a peer may only be determined by querying ILC-configured bootstrap nodes (seed peers). Use of arbitrary third-party STUN servers (RFC 3489 / RFC 5389) is not authorized. This avoids leaking peer IP to untrusted third parties and avoids taking a dependency on external STUN infrastructure for ILC reachability detection.

Probe observers are not validators merely because they observe reachability. They are ILC-controlled or ILC-configured bootstrap nodes whose only role in this path is to report the externally observed endpoint of the probing peer. A probe receipt must distinguish:

| Field | Meaning |
|---|---|
| `observer_agent_id` | The ILC bootstrap/probe node that observed the candidate endpoint. |
| `observed_endpoint` | The IP/port observed from the probe connection. |
| `observed_at_epoch` | The protocol epoch or test epoch used for replay-bounded interpretation. |
| `probe_method` | Direct listener probe, outbound-reflexive observation, relay health check, or explicit fallback. |
| `result` | `reachable`, `outbound_only`, `relay_required`, or `failed`. |

No arbitrary third-party STUN, TURN, ICE, UPnP, NAT-PMP, or PCP authority is introduced by this phase. Later phases may implement ILC-native traversal with explicit consent and ILC probe observers.

## 6 - CDL-112 Scope Decision

CDL-112 is proposed as a new CDL governing connectivity advertisement schema. It is not a CDL-103 amendment.

CDL-103 is already ratified and governs bounded dynamic peer discovery for testnet use. Its `PeerAdvertisement` runtime currently has a single `TransportEndpoint` (`scheme`, `host`, `port`), no `relay_endpoint` field, and no `candidate_list` field. That schema must not be silently expanded under the CDL-103 name.

CDL-112 should cover:

| Scope item | Required decision |
|---|---|
| Relay endpoint form | Canonical representation for direct, relay, and rendezvous endpoint candidates. |
| Candidate endpoint list | Ordered, bounded endpoint candidates with direct-first and relay-fallback preference semantics. |
| Connectivity mode declaration | Signed declaration of one of the 9 modes in this spec, including TTL and proof references. |
| Probe receipt reference | Binding between mode declaration and ILC probe observer receipt. |
| Privacy boundary | Which IP, NAT, relay, and availability fields may be public, private, or hash-only. |
| Abuse limits | TTL, rate limits, maximum candidates, relay slot caps, and revocation behavior. |
| Authority split | Peer advertisements are discovery hints; endpoint assertions and validator admission remain separate authority surfaces. |

Before any phase opens CDL-112, the CDL register must be checked again. As of this phase, direct read of `docs/specs/ilc_constitutional_decision_log_v0.1.md` shows CDL-103 ratified, CDL-111 opened, CDL-SIGMA-01 ratified, and no CDL-112 allocation.

## 7 - Non-Claims Table

| Non-claim | Scope | Authority |
|---|---|---|
| No DHT pre-RC | Peer discovery uses gossip plus seed peers only; no distributed hash table until post-RC governance explicitly authorizes it. | ADR-0011, CDL-103 |
| No silent UPnP/NAT-PMP/firewall mutation | Router or firewall mutation must be explicit opt-in through `--enable-upnp` or an equivalent future explicit flag; never silent. | ADR-0011 design gap; policy defined in GAP-AUTO-NAT-TRAVERSAL-POLICY-00 |
| No serving rewards without proven reachability | CDL-078 serve-event credit requires verified serve evidence; an unverified relay or mode claim cannot generate ECU. | CDL-078 |
| No validator admission from peer advertisement alone | CDL-103 `PeerAdvertisement` is not sufficient for validator admission; ADR-0039 endpoint registry, identity authority, and validator admission checks are required. | ADR-0039, CDL-068 |
| No production relay incentives pre-RC | Pre-RC relay is operator cost. Automated production reward logic remains inactive. | CDL-078 |
| No removal of PyPI/GitHub fallback pre-RC | Bootstrap/fetch path retains PyPI/GitHub fallback while moving trust toward signed ILC-native artifacts. | CDL-079 |
| No consensus relay that terminates or re-originates validator messages | A consensus relay must be pass-through only; validator message integrity remains end-to-end. | ADR-0039 |
| No claim that every install becomes directly reachable | Many installs will remain `outbound_only` or `relay_reachable`; useful participation must not require universal direct inbound reachability. | ADR-0011 NAT design gap |
| No public P2P activation by this spec | This document defines taxonomy only and does not clear public sidecar listener guards. | CDL-103 |
| No CDL mutation | This phase records the proposed CDL-112 scope but does not allocate, open, amend, prelock, or ratify any CDL. | Phase scope |

## 8 - Claim Verification Notes

| Claim checked | Source evidence |
|---|---|
| Dynamic peer discovery guard cleared for testnet scope | `ilc_core/network/d2d/peer_discovery_manager.py:28` and `ilc_core/network/d2d/gossip_peer_registry.py:36` set `DYNAMIC_PEER_DISCOVERY_NOT_ACTIVATED = False`. |
| Peer discovery manager performs no network I/O | `ilc_core/network/d2d/peer_discovery_manager.py:4-6` states local advertisement, validation, and sampling only. |
| PeerAdvertisement has one transport endpoint | `ilc_core/network/d2d/peer_advertisement.py:106-117` defines one `transport_endpoint`; searches found no `relay_endpoint` or `candidate_list`. |
| PeerAdvertisement canonical preimage is deterministic | `ilc_core/network/d2d/peer_advertisement.py:130-139` uses sorted JSON keys, compact separators, ASCII, and `allow_nan=False`. |
| Bootstrap/fetch path is signed bundle plus seed peer, no DHT | `ilc_core/network/d2d/bootstrap_fetch_runtime.py:20-27` and CDL-079 register row describe explicit-promotion seed bundle fetch and no DHT. |
| OpenClaw relay is not the relay/rendezvous MVP | `ilc_core/network/d2d/openclaw_p2p_relay.py:2-7` states harness-assisted relay with no socket binding or native Rust QUIC P2P; line 51 keeps `NATIVE_RUST_P2P_NOT_ACTIVATED = True`. |
| ADR-0011 requires explicit NAT/connectivity design | `docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md:29-32`. |
| ADR-0025 binds slow D2D to HTTP/3/HTTP/2 and originally deferred discovery | `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md:28-31` and `89-92`. |
| ADR-0039 defines direct and relay endpoint forms | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md:57-76`, `85-124`. |
| ADR-0039 relay must not terminate or re-origin consensus messages | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md:121-124`. |
| CDL-103 rejects validator authority from advertisements | `docs/specs/ilc_cdl_103_dynamic_peer_discovery_ratification_1583_v0.1.md:63` and `73-85`. |
| Agent INIT starts as permissionless but zero public weight until attestation | `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md:66-110`. |
| Sealed sender concerns remain separate from reachability mode taxonomy | `docs/adr/ADR_0034_D2d_Sealed_Sender_Mechanism.md:61-79` preserves bounded relay scope and no unbounded gossip. |

## 9 - Newly Discovered Tokens

| Token | Source | Disposition |
|---|---|---|
| `cdl_103_signed_peer_table_roots_deferred_phase_1583` | CDL-103 ratification evidence | Respect as anti-eclipse carry-forward; this phase does not claim signed peer table roots. |
| `cdl_103_multi_seed_comparison_deferred_phase_1583` | CDL-103 ratification evidence | Respect as anti-eclipse carry-forward; this phase does not claim multi-seed comparison. |
| `lexicographic_gossip_fanout_rotation_deferred_pending_cdl_103_phase_1575h_fix2` | `gossip_peer_registry.py` | Respect as routing-selection carry-forward; this phase does not activate hash-derived fanout rotation. |
| `native_rust_p2p_not_activated_phase_1437` | `openclaw_p2p_relay.py` | Confirms OpenClaw harness is not native relay deployment. |
| `agent_init_permissionless_zero_public_weight_until_attestation` | ADR-0041 | Preserved by invite-provenance relay admission: reachability help does not equal public epistemic weight. |
| `run_h013_d2d_sealed_sender_adr_verdict=accepted` | ADR-0034 | Privacy path remains adjacent; no sealed-sender implementation in this phase. |

## 10 - Graph Delta

```text
load_bearing_artifact_added: docs/specs/ilc_connectivity_path_taxonomy_GAP_CONNECTIVITY_RECONCILE_00_v0.1.md -> genesis:genesis_root_v0.4
support_only: docs/phases/phase_gap_connectivity_reconcile_00_walkthrough.md
```

