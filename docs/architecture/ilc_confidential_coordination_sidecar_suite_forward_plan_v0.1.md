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

Phase 1324 completion:

```text
ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1
encrypted_coordination_node_envelope_contract_recorded_phase_1324
shard_header_projection_contract_recorded_phase_1324
private_to_public_promotion_evidence_shape_recorded_phase_1324
ccss_public_serving_not_enabled_phase_1324
phase_1325_ccss_capability_membership_boundary_next
public_rc_remains_blocked_after_phase_1324
```

The CCSS-001 contract is now implemented locally at
`ilc_core/sidecars/confidential_coordination_shard.py` and registered as
`confidential_coordination_private_gated_shard`. It defines `PrivateShardRef`,
`EncryptedCoordinationNodeEnvelope`, `ShardHeaderProjection`,
`PromotionEvidenceRef`, and `DisclosureDenial` without enabling public
confidential coordination serving, public P2P, public promotion, source
publication, release signing, identity bootstrap, wallet actions, ECU minting,
ILC settlement, or value-path activation.

Phase 1324 Fix1 hardens that contract before CCSS-002:

```text
phase_1324_fix1_ccss_001_shard_contract_hardening.v0.1
ccss_001_epoch_zero_rejected_phase_1324_fix1
ccss_001_canonical_json_byte_cap_enforced_phase_1324_fix1
ccss_001_ref_list_count_prechecked_phase_1324_fix1
ccss_001_phase_1325_membership_ref_false_positive_removed_phase_1324_fix1
```

CCSS-002 should define capability and membership semantics without routing raw
membership material through CCSS-001. CCSS-001 permits opaque membership-boundary
reference strings only as refs; actual membership lists, member-agent
identifiers, participant identities, route history, and capability contents
remain denied.

Phase 1325 completion:

```text
ccss_002_capability_membership_grant_revocation_boundary_phase_1325.v0.1
private_shard_access_control_boundary_recorded_phase_1325
membership_plaintext_disclosure_forbidden_phase_1325
optional_zk_interface_boundary_recorded_phase_1325
phase_1326_ccss_sealed_sender_boundary_next
public_rc_remains_blocked_after_phase_1325
```

The CCSS-002 contract is now implemented locally at
`ilc_core/sidecars/confidential_coordination_capability.py` and registered as
`confidential_coordination_capability_membership_boundary`. It defines
`CapabilityPolicyRef`, `MembershipBoundaryRef`, `CapabilityGrantRef`,
`CapabilityRevocationRef`, `ZKMembershipInterfaceRef`, and local
`CapabilityAccessDecision` records. Unknown, malformed, replayed, cross-shard,
revoked, expired, superseded, and ZK-deferred capabilities deny by default.
The optional ZK seam records interface shape only and does not activate a
ratified verifier or public proof service. Actual member lists, bearer
identities, raw grants, raw membership material, revocation reasons, plaintext,
route history, and ZK witnesses remain denied.

Phase 1325 Fix1 completion:

```text
phase_1325_fix1_ccss_002_access_audit_hardening.v0.1
ccss_002_zk_record_kind_validated_phase_1325_fix1
ccss_002_revocation_precedes_zk_deferred_phase_1325_fix1
ccss_002_pre_serialization_payload_byte_budget_phase_1325_fix1
sidecar_del_control_character_rejected_cross_module_phase_1325_fix1
public_rc_remains_blocked_after_phase_1325_fix1
phase_1326_ccss_sealed_sender_boundary_next_after_fix1
```

The CCSS-002 access decision now preserves deterministic revocation audit
state before optional ZK deferral and validates the ZK seam record kind and
boundary match. CCSS-002 canonical JSON traversal now enforces a
pre-serialization payload byte budget. The cross-module sidecar text-validation
sweep now rejects ASCII DEL (`0x7f`) as a control character. Phase 1326 remains the next
sensitive CCSS-003 sealed sender boundary and requires explicit `GO Phase
1326`.

Phase 1325 Fix2 completion:

```text
phase_1325_fix2_ccss_002_branch_and_integer_hardening.v0.1
ccss_002_oversized_raw_int_rejected_before_stringification_phase_1325_fix2
ccss_002_access_branch_coverage_expanded_phase_1325_fix2
ccss_002_payload_depth_node_limits_covered_phase_1325_fix2
public_rc_remains_blocked_after_phase_1325_fix2
phase_1326_ccss_sealed_sender_boundary_next_after_fix2
```

CCSS-002 now rejects oversized raw integer canonical-JSON payload leaves before
decimal stringification and has focused coverage for supersession, mismatch,
invalid-window, zero-sequence, depth-limit, and node-limit paths. Phase 1326
remains the next sensitive CCSS-003 sealed sender boundary and requires
explicit `GO Phase 1326`.

Phase 1326 completion:

```text
ccss_003_sealed_sender_local_delivery_boundary_phase_1326.v0.1
sealed_sender_fixed_size_payload_boundary_recorded_phase_1326
h013_h015_dependency_seams_recorded_phase_1326
public_p2p_not_activated_by_ccss_phase_1326
phase_1327_ccss_gossip_jitter_cover_policy_next
public_rc_remains_blocked_after_phase_1326
```

The CCSS-003 contract is now implemented locally at
`ilc_core/sidecars/confidential_coordination_sealed_sender.py` and registered
as `confidential_coordination_sealed_sender_local_delivery`. It defines
fixed-size H-013 sealed payload classes, local delivery intents, local delivery
receipts, and private/local delivery projections for `sealed_pending_local`,
`sealed_delivered_local`, `rejected_size_class`, `rejected_metadata_leak`,
`rejected_replay`, and `blocked_public_transport`. H-013 and H-015 are recorded
as dependency seams only. The sidecar does not activate public P2P, public relay
serving, public confidential coordination serving, public messaging, source
publication, release authority, release signing, identity bootstrap, wallet
actions, ECU minting, ILC settlement, or value-path activation.

Phase 1327 completion:

```text
ccss_004_gossip_jitter_cover_policy_tests_phase_1327.v0.1
gossip_announce_pull_jitter_policy_recorded_phase_1327
traffic_analysis_negative_tests_recorded_phase_1327
anonymity_guarantee_not_claimed_phase_1327
phase_1328_ccss_private_droplet_reproducibility_next
public_rc_remains_blocked_after_phase_1327
```

The CCSS-004 contract is now implemented locally at
`ilc_core/sidecars/confidential_coordination_gossip_policy.py` and registered as
`confidential_coordination_gossip_jitter_cover_policy`. It defines
traffic-analysis matrix refs, private/local gossip announce/pull policy refs,
and cover-policy decision refs for bounded metadata announce, receiver-controlled
pull, bounded jitter, bounded batching, idle cover, deterministic test-fixture
jitter, rejected public network attempts, rejected deterministic runtime jitter
seed attempts, rejected participant metadata, rejected disabled cover, and
rejected unbounded batches. The sidecar does not activate public P2P, public
relay serving, public confidential coordination serving, public messaging,
source publication, release authority, release signing, identity bootstrap,
wallet actions, ECU minting, ILC settlement, value-path activation, anonymity,
unlinkability, or Signal-equivalent protection.

Phase 1328 completion:

```text
ccss_005_private_openclaw_nemoclaw_droplet_dry_run_phase_1328.v0.1
confidential_coordination_private_wiring_dry_run_recorded_phase_1328
reproducibility_pass_recorded_phase_1328
public_confidential_coordination_serving_not_enabled_phase_1328
phase_1329_window_1317_1329_closure_next
public_rc_remains_blocked_after_phase_1328
```

The CCSS-005 private OpenClaw/NemoClaw-compatible dry run is now recorded at
`docs/specs/ilc_ccss_005_private_openclaw_nemoclaw_droplet_dry_run_1328_v0.1.md`.
It used the real private Tailscale droplets `ilc-node-2`, `ilc-node-3`, and
`ilc-node-6`, verified private Git-bundle sync to committed source
`acc92d645055c4ea288aad947df0f54604975fc6`, full mesh reachability, UFW
Tailscale-only inbound, OpenClaw local workspace skill readiness on
`ilc-node-6`, no OpenClaw gateway listener on `18789` or `19001`, and
deterministic CCSS-001 through CCSS-004 sample construction on all three nodes.
It remains private evidence only and does not authorize public serving, public
P2P, public confidential coordination serving, public messaging, source
publication, OpenClaw skill publication, ClawHub listing, public installability,
identity bootstrap, wallet actions, ECU minting, ILC settlement, value-path
activation, release authority, signing authority, or Atlas-G tail work.

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
