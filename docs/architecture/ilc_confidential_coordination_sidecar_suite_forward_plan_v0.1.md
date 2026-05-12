# ILC Confidential Coordination Sidecar Suite Forward Plan v0.1

**Status:** Forward architecture and phase-routing plan.
**Recorded:** 2026-05-11.
**Authority:** This document records planning only. It does not open Window
1303+, execute source export, publish a repository or package, produce release
artifacts, generate release keys or envelopes, mutate or sign Genesis Atlas,
sign v0.2, activate public claimability, activate public P2P/fetch/sidecar
serving, authorize a public confidential-messaging claim, or authorize
wallet/ECU/ILC economics.

```text
confidential_coordination_sidecar_suite_forward_plan_recorded
confidential_coordination_sidecar_suite_graph_native_not_signal_clone
confidential_coordination_sidecar_suite_not_public_rc_blocker_by_default
confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329
confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only
confidential_coordination_public_claim_requires_phase_1337_1341_authority
```

## 1. Purpose

The Confidential Coordination Sidecar Suite is the graph-native route for
private agent and human coordination over ILC. It is not a conventional chat
API placed on top of ILC and it is not a claim that ILC is already a Signal
replacement. The suite should use ILC-native objects: encrypted or gated shard
headers, capability references, sealed D2d payload envelopes, opaque gossip
channels, projection filters, TransportPrincipal policy state, and explicit
non-claims.

The near-term objective is a private/local suite that can be hosted by
OpenClaw, NemoClaw, a future first-party ILC harness, or another harness
without making that harness a protocol dependency.

The suite should remain non-public and non-blocking for the first public RC
unless a later explicit sequence lock selects it as a public-RC requirement.

## 2. Canon Basis

| Source | Relevance |
|--------|-----------|
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | Establishes graph-native sidecars rather than a conventional wrapper API. |
| `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | Owns the candidate post-1302 phase routing. |
| `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md` | Defines opaque D2d gossip channel and no `creator_agent_id` transport-header leakage. |
| `docs/adr/ADR_0034_D2d_Sealed_Sender_Mechanism.md` | Defines fixed-size one-relay sealed sender for H-013 spectral beacon scope. |
| `docs/research/ilc_private_shard_architecture_proposal_791_v0.1.md` | Defines private/gated shard membership and encrypted coordination-node direction. |
| `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix3_v0.1.md` | Establishes jitter as a timing-correlation mitigation pattern. |
| `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` | Establishes OpenClaw/NemoClaw as harness/onboarding hosts, not protocol substrates. |

## 3. Suite Components

| Component | Role | First phase target | Public posture |
|-----------|------|--------------------|----------------|
| Confidential coordination profile in sidecar registry | Declares the local/private suite profile, required sidecars, capabilities, private wiring, non-claims, and export posture. | 1307 | Manifest/profile only; no public serving. |
| Private/gated shard sidecar | Creates and validates encrypted coordination-node envelopes, shard headers, commitments, and private-to-public promotion evidence. | 1324 | Local/private only. |
| Capability and membership sidecar | Manages capability references, grants, revocation, shard membership policy, and a ZK-proof interface boundary where applicable. | 1325 | No plaintext disclosure or public membership leak. |
| Sealed sender delivery sidecar | Builds fixed-size sealed payloads and relay instructions by reusing the H-013/H-015 boundary where authorized. | 1326 | No public P2P activation by default. |
| Gossip announce/pull and jitter policy sidecar | Announces encrypted object availability over opaque channels and tests batching, jitter, and cover-policy choices against traffic-analysis overclaims. | 1327 | No anonymity guarantee by default. |
| OpenClaw/NemoClaw confidential bridge | Lets a third-party harness call the local/private confidential suite through imports, CLI, or private loopback/Tailscale wiring. | 1328 | Private DigitalOcean droplet testing only unless later authorized. |

## 4. Specific Phase Routing

Current Window 1289-1302:

| Phase | Assignment |
|-------|------------|
| 1297 | Completed related prerequisite: public-safe projection schema. It does not implement confidential coordination. |
| 1298 | Completed related prerequisite: bind/listener/peer-discovery authority preflight. It does not enable public serving. |
| 1299 | If release readiness is reviewed, carry this suite as future/private sidecar scope unless explicitly selected. Do not package it into public RC by implication. |
| 1302 | Closure should classify this suite as forward-routed, private/local by default, and not a first-public-RC blocker unless explicitly selected. |

Window 1303-1316:

| Phase | Assignment |
|-------|------------|
| 1307 | Complete. Added `confidential_coordination_local_preview` to the sidecar registry/manifest profile set with required sidecars, non-claims, private wiring modes, package isolation, and no public confidential messaging claim. |
| 1311 | Complete. Added local graph/memory projection records for private/gated shard headers and encrypted coordination-node references without exposing plaintext, membership, route history, or raw sealed payloads. |
| 1312 | Complete. Added privacy/filtering tests for confidential-coordination projections, including deny-by-default field classification, export-level raw-fragment leak guards, bounded-serving blocker tests, and no accidental public-safe promotion. |

Window 1317-1329:

| Phase | Assignment |
|-------|------------|
| 1324 | CCSS-001: implement or formally specify the private/gated shard sidecar contract, encrypted coordination-node envelope, shard-header projection, and private-to-public promotion evidence shape. |
| 1325 | CCSS-002: implement or formally specify capability, membership, grant, revocation, and optional ZK-membership proof interface boundaries. |
| 1326 | CCSS-003: implement or formally specify sealed sender local delivery sidecar boundaries, fixed-size payload handling, H-013/H-015 dependency seams, and no-public-P2P defaults. |
| 1327 | CCSS-004: implement or formally specify gossip announce/pull, jitter, batching, cover-policy, and traffic-analysis negative tests; explicitly avoid an anonymity-guarantee claim. |
| 1328 | CCSS-005: run a private OpenClaw/NemoClaw or equivalent DigitalOcean droplet dry run over loopback, Tailscale, or other private wiring. No public serving claim. |
| 1329 | Closure gate: decide whether the suite remains a post-RC/private lane, becomes a selected public-RC blocker, or is split into a later dedicated window. |

Window 1330-1342:

| Phase | Assignment |
|-------|------------|
| 1337 | Public-path gate must explicitly activate or exclude any confidential coordination serving claim. Local/private droplet success is not public serving authority. |
| 1341 | Public RC publication/claim must not imply a public confidential messaging product unless Phase 1337 explicitly selected and passed that scope. |

## 5. Security Boundaries

- Content confidentiality requires mature message/session cryptography or an
  explicitly ratified equivalent. ILC graph anchoring does not itself replace
  double-ratchet, MLS-style group messaging, key backup, device sync, or
  session-rekey analysis.
- Metadata protection is layered: opaque channels, no creator identity in
  transport headers, sealed sender payloads, relay/admission controls,
  private/gated shard headers, batching, jitter, and cover-policy tests.
- Attribution resistance is a realistic near-term goal. Anonymity guarantee is not a default claim.
- All public serving remains blocked until TransportPrincipal, public transport,
  replay, rate-limit, privacy, bind/listener, and release authority gates close.
- OpenClaw, NemoClaw, and DigitalOcean droplets are harness/deployment targets,
  not protocol substrates.

## 6. Non-Claims

This plan does not authorize:

- Window 1303+ execution;
- public confidential messaging;
- public sidecar serving;
- public projection endpoint serving;
- public claimability API activation;
- public verifier service;
- public P2P or public fetch serving;
- OpenClaw/NemoClaw as protocol substrate;
- source allowlist export execution;
- public repository publication;
- public package publication;
- release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- wallet withdrawal, transfer, spend, ECU minting, or ILC settlement;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- CDL mutation or CDL-088 opening;
- IP filing or paper publication.
