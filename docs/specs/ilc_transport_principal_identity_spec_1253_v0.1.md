# ILC TransportPrincipal Identity Spec 1253 v0.1

Status: locked
Date: 2026-05-08
Phase: 1253
Owner lane: G8 public-RC blocker lane

`transport_principal_identity_spec_phase_1253.v0.1`
`python_http_transport_devnet_test_downgrade_plan_phase_1253`
`json_requester_id_rate_limit_fallback_forbidden_public_p2p_phase_1253`
`phase_1253_transport_digest_and_rust_m5_disposition_recorded`
`phase_1253_transport_principal_spec_complete`

## 1. Purpose and non-activation boundary

This packet defines the TransportPrincipal identity boundary and the public-P2P
readiness disposition for the Phase 1250 Fix1 transport findings. It is an
ADR-input and public-RC blocker specification, not a runtime implementation.

Phase 1253 does not activate TransportPrincipal runtime, public P2P, public
sidecar/projection serving, public claimability, wallet withdrawal, wallet
transfer, wallet spend authority, public repository publication, public RC,
release keys, release envelopes, CDL mutation, CDL-087 ratification, CDL-088
opening, v0.2 signing, signed Genesis mutation, immutable diagnostic mutation,
or production `commit.epoch` emission.

The forbidden activation boundary explicitly includes public sidecar/projection serving.

The controlling rule is:

```text
transport_principal_identity_required_before_public_p2p
d2d_rate_limiter_key_must_be_authenticated_transport_principal
agent_id_must_not_be_default_transport_rate_limit_key
json_requester_id_rate_limit_fallback_forbidden_public_p2p
transport_principal_cdl_required_before_runtime_implementation
transport_principal_lifecycle_and_revocation_spec_required
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
```

## 2. Canon lineage verified in this phase

| Source | Direct-read conclusion |
|--------|------------------------|
| `docs/PLANNING_INDEX.md` | Window 1249-1256 is open through Phase 1252 plus post-audit route hardening; Phase 1253 is next and non-sensitive. |
| `docs/specs/ilc_antigravity_context_capsule_v5.50.md` | Gap 10 TransportPrincipal remains open; public P2P and non-loopback sidecar/projection surfaces require hostile-network hardening. |
| `docs/phases/STATUS.md` | Phase 1252 carried network digest candidates and Rust M-5 disposition to Phase 1253; post-audit route hardening corrected the Phase 1253 inputs. |
| `docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md` | Phase 1253 is non-sensitive design/spec only after Phase 1252; Phase 1256 remains sensitive. |
| `docs/specs/ilc_window_1249_1256_candidate_phase_grouping_v0.1.md` | TransportPrincipal, network digest/Rust M-5 disposition, and Python HTTP downgrade are Phase 1253 scope. |
| `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` | Defines the L0-L4 identity ladder and the requirement that public-path rate limiting bind to authenticated TransportPrincipal, not body `requester_id`. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Gap 10 is a public-P2P hard requirement and applies to non-loopback sidecar/projection public paths. |
| `docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md` | Claimability remains epoch/root-resolution driven and deferred; transport candidates remain Phase 1253 work. |
| `docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.md` and `.json` | `RCGAP-1250-FIX1-004`, `RCGAP-1250-FIX1-005`, and `RCGAP-1250-FIX1-008` route to Phase 1253. |
| `ilc_core/network/d2d/http_fetch_transport_runtime.py` | Actual current path for fetch HTTP runtime; HTTP serving keys WANT-BLOCK rate limiting on `client_ip`, not JSON body `requester_id`, and retains body `requester_id` as payload/audit field. |
| `ilc_core/network/d2d/http_gossip_transport_runtime.py` | Actual current path for gossip HTTP runtime; bounded/read-timeout wrapper with explicit local/testbed TLS verification escape hatch. |
| `ilc_consensus/src/network.rs` | Rust Quinn/rustls transport exists with pinned certificate verification and operation timeouts. |
| `ilc_consensus/src/node.rs` | `FIXME(M-5)` confirms dynamic membership quorum `f` is captured at `NodeRunner::new()` and must be fixed before dynamic public-P2P membership claims. |
| `ilc_core/graph/sidecar_query_runtime.py` | Sidecar query/export runtime is local read-only with bounded JSON/NDJSON exports and no network serving. |

MemPalace was used as advisory retrieval support only. The query returned
historical Roadmap v0.3 fragments rather than current TransportPrincipal canon,
so no MemPalace hit was promoted without direct repo reads.

## 3. TransportPrincipal identity contract

TransportPrincipal is the missing L3 transport identity layer. It is distinct from permanent AgentID, BLS consensus/economic keys, Ed25519 enrollment/beacon
keys, and OpenClaw/NemoClaw harness identity.

Required properties:

- Short-lived or epoch-rotating identity suitable for D2D connection
  authentication, rate limiting, local bans, and peer reputation.
- Cryptographic proof of possession at the transport boundary, with Ed25519 or
  stronger as the minimum expected signing primitive unless a later ADR chooses
  a different concrete scheme.
- Issuance rules that do not reveal permanent AgentID or economic stake to a
  passive network observer by default.
- Epoch-scoped rotation and replay prevention so an old credential cannot be
  replayed as a current public-path principal.
- Revocation and local-ban persistence keyed by TransportPrincipal credential
  material or a full-hash derivative, not by mutable body fields.
- Optional governance-authorized linkage to stake, admission, or reputation
  without making the default public network handle equal to AgentID or a BLS
  validator key.
- Public-path observability that records full security-binding fingerprints or
  full hash identifiers where the identifier is used as a proof, ban key,
  revocation key, or audit root.

Before runtime implementation, an ADR or CDL-input packet must decide:

```text
transport_principal_cdl_required_before_runtime_implementation
transport_principal_lifecycle_and_revocation_spec_required
```

## 4. Public-path rate-limit and admission rules

The public-path rule is strict:

```text
json_requester_id_rate_limit_fallback_forbidden_public_p2p_phase_1253
```

For public P2P, non-loopback fetch, non-loopback gossip, or non-loopback
sidecar/projection serving:

- JSON/body `requester_id` must not be used as the rate-limit key, admission
  key, ban key, abuse circuit-breaker key, or public-path reputation key.
- `client_ip` is only a devnet/test or local abuse-damping fallback. It is not a
  sufficient hostile-network principal because NAT, rotation, shared hosts, and
  proxying weaken identity and fairness.
- Permanent AgentID must not be the default transport rate-limit key.
- BLS validator/economic keys must not become per-connection public transport
  handles by default.
- OpenClaw/NemoClaw harness identity is deployment/orchestration identity only
  and must not become ILC protocol law.

The existing fetch handler remains acceptable for local/devnet regression use
because `HttpFetchTransportRuntime` passes `rate_limit_key=client_ip` for HTTP
WANT-BLOCK requests. The direct-call fallback to body `requester_id` remains a
test and compatibility surface only; it is forbidden for public P2P.

## 5. Python HTTP devnet/test-only downgrade plan

`python_http_transport_devnet_test_downgrade_plan_phase_1253`

The Python HTTP runtime files are formally classified as devnet/test harnesses:

- `ilc_core/network/d2d/http_fetch_transport_runtime.py`
- `ilc_core/network/d2d/http_gossip_transport_runtime.py`

Disposition:

- Keep the modules intact as regression, local harness, and devnet/test
  surfaces. Do not rip them out.
- Preserve their existing bounded-state hardening, payload-size guards, socket
  timeouts, no-redirect behavior, and local/testbed TLS verification escape
  hatch constraints.
- Do not claim them as public-internet-facing P2P substrate.
- Do not bind them beyond loopback or private harness networks as an ILC public
  service until TransportPrincipal and public-path policy gates exist.
- Update phase prompts and future planning to use the actual current paths under
  `ilc_core/network/d2d/`, not stale `ilc_core/transport/` paths.

The current Python HTTP posture is compatible with the OpenClaw/NemoClaw
skill-first public-RC direction because that direction does not make an ILC-owned
public P2P claim.

## 6. Rust public-P2P substrate ADR input

Rust Quinn/rustls already exists in `ilc_consensus/src/network.rs`:

- `quinn::{ClientConfig, Connection, Endpoint, RecvStream, SendStream, ServerConfig}`
- rustls TLS 1.3 verifier implementations for pinned client and server certs
- ALPN `ilc-gossip`
- `IO_TIMEOUT_MS` and per-operation timeout guards

That code is a candidate foundation, not a completed public-P2P substrate for
all D2D surfaces.

Future ADR input:

```text
rust_public_p2p_transport_lane_required_before_public_p2p
rust_quic_tls_transport_already_exists_in_ilc_consensus_src_network_rs
rust_p2p_substrate_decision_adr_required_quinn_vs_libp2p
```

The ADR must decide one of:

- Extend the existing Quinn/rustls lane and add TransportPrincipal mapping,
  D2D fetch/gossip binding, revocation, admission, and abuse policy.
- Adopt libp2p for the public-P2P substrate and define how it maps to existing
  consensus identities, certificates, and D2D protocols.
- Define an adapter boundary that can support Quinn/rustls and libp2p without
  forcing Python HTTP or harness identity into protocol law.

The ADR must also decide whether TransportPrincipal credential material is
separate from TLS certificates, embedded into certs, or attested through an
application-layer handshake over a mutually authenticated transport.

## 7. Phase 1250 Fix1 transport dispositions

`phase_1253_transport_digest_and_rust_m5_disposition_recorded`

| Finding | Candidate | Classification | Phase 1253 disposition |
|---------|-----------|----------------|------------------------|
| `RCGAP-1250-FIX1-004` | `ilc_core/network/d2d/gossip.py:181` `channel_tag = sha256(...).hexdigest()[:16]` | Metadata display/privacy tag, not an authenticated principal or security root. | Leave unchanged for this design phase. No public security, ban, revocation, or admission decision may depend on the truncated tag. Reassess if public observer metadata becomes a security-binding proof. |
| `RCGAP-1250-FIX1-004` | `ilc_core/network/d2d/spectral_beacon.py:207` `agent:` digest prefix | Terminal-visible pseudonymous AgentID alias derived from public key, not a TransportPrincipal. | Leave unchanged for this design phase. It must not become the public transport rate-limit key or peer-ban key. |
| `RCGAP-1250-FIX1-004` | `ilc_core/network/star_map/star_map_route_index_runtime.py:120` `_ngram_bucket_key()` 16-char digest | Route-index bucket key for n-gram indexing, not transport auth, settlement proof, or security root. | Leave unchanged for this design phase. If bucket keys become external proofs or adversarial routing commitments, migrate to full digest or collision-handled bucket structure in that future phase. |
| `RCGAP-1250-FIX1-005` | `ilc_consensus/src/node.rs:636` `FIXME(M-5)` | Real dynamic-membership/public-P2P substrate confidence gap. | Carry forward as a required Rust public-P2P hardening item before dynamic validator admission/ejection or public-P2P substrate claims. Static genesis testnet posture is not enough for hostile dynamic membership. |
| `RCGAP-1250-FIX1-008` | deferred peer discovery and Python HTTP surfaces | Public-P2P lane work, not skill-first package blocker. | Keep routed to TransportPrincipal plus Rust public-P2P ADR. No dynamic discovery or non-loopback public serving is authorized here. |

## 8. Sidecar/projection boundary

`sidecar_projection_endpoint_public_path_requires_transport_principal_auth`

`ilc_core/graph/sidecar_query_runtime.py` is a local read-only query/export
runtime. It includes deterministic JSON export with `sort_keys=True`,
`allow_nan=False`, compact separators, finite Decimal enforcement, float
rejection, maximum byte limits, and maximum result limits.

Phase 1253 does not add a sidecar HTTP server or projection endpoint.
Any future non-loopback sidecar/projection path must require:

- TransportPrincipal authentication.
- Public-path rate limiting keyed by authenticated TransportPrincipal.
- Export/result byte and count bounds at every untrusted boundary.
- Privacy rules for projection data, serving peer identifiers, and graph
  membership leakage.
- CDL-087 and public sidecar policy readiness where applicable.

## 9. Prompt path correction

The Phase 1253 prompt originally named stale paths under
`ilc_core/transport/`. The actual current repo paths are:

```text
ilc_core/network/d2d/http_fetch_transport_runtime.py
ilc_core/network/d2d/http_gossip_transport_runtime.py
```

The prompt has been corrected so future reruns direct-read the current code.

## 10. Graph delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md -> transport/public_rc
graph_delta=support_tests_added:tests/test_phase_1253_transport_principal_identity_spec.py -> validation
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1253_g8_transport_principal_identity_and_http_downgrade.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1253_transport_principal_identity_spec_walkthrough.md -> planning/frontier
```
