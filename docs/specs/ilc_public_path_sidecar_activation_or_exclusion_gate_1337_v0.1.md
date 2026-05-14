# ILC Public Path Sidecar Activation Or Exclusion Gate 1337 v0.1

**Date:** 2026-05-14
**Phase:** 1337
**Status:** excluded from first RC; no public path, sidecar, P2P, fetch, or confidential coordination serving activated

```text
public_path_sidecar_activation_or_exclusion_gate_phase_1337.v0.1
transport_principal_public_path_requires_explicit_authority_phase_1337
public_sidecar_projection_serving_requires_explicit_authority_phase_1337
public_confidential_coordination_serving_requires_explicit_authority_phase_1337
phase_1338_wallet_ecu_ilc_activation_gate_next
public_rc_remains_blocked_after_phase_1337
```

## 1. Verdict

Phase 1337 executed after the explicit gate authorization:

```text
GO Phase 1337
```

That authorization was sufficient to execute the public-path activation-or-
exclusion gate. It was not explicit authority to activate a public
TransportPrincipal path, public P2P, public fetch serving, non-loopback
listener, peer discovery, public graph-native sidecar serving, public projection
endpoint, public confidential coordination serving, source publication, release
signing, public RC publication/claim, wallet path, ECU minting, ILC settlement,
identity bootstrap, CDL mutation, CDL-088 opening, Genesis/Atlas mutation, or
v0.2 signing.

The gate result is:

```text
result=excluded_from_first_rc
public_path_sidecar_activation_or_exclusion_gate_verdict=excluded_from_first_rc
phase_1337_status=complete_excluded_from_first_rc
```

No runtime code was changed and no public endpoint, listener, public route, peer
discovery path, sidecar server, projection server, or confidential coordination
server was activated.

## 2. Claim Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1337 prompt validates and is executable. | `docs/antigravity_tasks/antigravity_prompt__phase_1337_g8_public_path_sidecar_activation_or_exclusion_gate.md`; `tools/validate_phase_prompt.py` | confirmed |
| Public P2P and public fetch serving remain default-off. | `docs/specs/ilc_public_fetch_p2p_activation_candidate_default_off_1313_v0.1.md`; `ilc_core/sidecars/public_fetch_p2p_readiness.py` | confirmed |
| TransportPrincipal public path remains local-only and not activated. | `docs/specs/ilc_transport_principal_admission_sidecar_lifecycle_1309_v0.1.md`; `docs/specs/ilc_revocation_replay_admission_ban_tests_1310_v0.1.md`; `ilc_core/sidecars/transport_principal_admission.py` | confirmed |
| Sidecar projection serving remains local-only and no public listener/bind/peer discovery authority is active. | `docs/specs/ilc_projection_privacy_field_filtering_tests_1312_v0.1.md`; `docs/specs/ilc_sidecar_bind_listener_peer_discovery_authority_preflight_1298_v0.1.md`; `ilc_core/sidecars/local_graph_memory_projection.py` | confirmed |
| CCSS private droplet success is private evidence only and not public confidential coordination serving authority. | `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md`; CCSS-001 through CCSS-005 specs and registry flags | confirmed |
| Sidecar registry records public-serving flags as false for current sidecar profiles. | `ilc_core/sidecars/registry_manifest.py` | confirmed |
| Phase 1336 left public claimability/API unactivated and Phase 1338 is the next wallet/ECU/ILC gate after Phase 1337. | `docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.json`; Phase 1337 prompt | confirmed |

MemPalace was queried as advisory retrieval. It returned older transport-
planning hits but no current planning or evidence result that superseded direct
repo reads.

## 3. Public-Path Decision Table

| Surface | Status | Public serving enabled | Reason |
|---------|--------|------------------------|--------|
| TransportPrincipal public path | excluded from first RC | false | `transport_principal_public_path_requires_explicit_authority_phase_1337` |
| Public P2P | excluded from first RC | false | `rust_public_p2p_substrate_gate_still_required_phase_1313` |
| Public fetch serving | excluded from first RC | false | `public_fetch_serving_default_off_phase_1313` |
| Public sidecar projection serving | excluded from first RC | false | `public_sidecar_projection_serving_requires_explicit_authority_phase_1337` |
| Public confidential coordination serving | excluded from first RC | false | `public_confidential_coordination_serving_requires_explicit_authority_phase_1337` |
| Public listener | excluded from first RC | false | `public_listener_not_enabled_phase_1298` |
| Peer discovery | excluded from first RC | false | `peer_discovery_not_enabled_phase_1298` |
| Non-loopback bind | excluded from first RC | false | `non_loopback_bind_not_enabled_phase_1298` |

The gate selected explicit first-RC exclusion because public-path authority and
public-mode preconditions are missing. This is not a runtime scan failure; it is
the fail-closed decision required by the phase prompt when activation authority
is absent.

## 4. Carry-Forward Blockers

| Blocker | Status | Carry-forward route |
|---------|--------|---------------------|
| Explicit public-path authority missing | open | Post-Phase-1342 public transport/sidecar serving window |
| Rust public-P2P substrate gate not satisfied | open | Window 1357+ or dedicated public P2P/sidecar serving window pending Rust P2P ADR |
| TransportPrincipal public path not authorized | open | Future public TransportPrincipal activation lane |
| Public bind/listener/peer discovery not authorized | open | Future public bind/listener/peer-discovery authority gate |
| Public sidecar projection serving not authorized | open | Future public sidecar projection serving gate |
| Public confidential coordination serving not selected | open | Post-claimability or dedicated CCSS public serving window if selected |
| Atlas-G signing/publication preconditions not closed | open | Phases 1339-1341 Atlas-G, signing, and publication gates |
| Source publication, release, and public RC claim not authorized | open | Phase 1341 public RC publication/claim gate or carry-forward |

## 5. CCSS Boundary

CCSS-001 through CCSS-005 remain private/local evidence. The Phase 1328 droplet
dry run proves private OpenClaw/NemoClaw-compatible coordination substrate
behavior; it is not public confidential messaging, not public confidential
coordination serving, not public P2P, not relay serving, not public sidecar
serving, and not a Signal-equivalent product claim.

## 6. Non-Claims

Phase 1337 does not authorize or perform:

- TransportPrincipal public-path activation
- public P2P, public fetch serving, public listener, peer discovery, or non-loopback bind
- public graph-native sidecar serving or public projection endpoint serving
- public confidential messaging or public confidential coordination serving
- source publication, public repository publication, or public package publication
- release artifact production, release-key generation, release envelope production, release signing, or release signature production
- public RC publication or public RC claim
- wallet-facing withdrawal, transfer, or spend requests
- wallet signing or wallet ledger-write
- ECU minting or ILC settlement
- identity bootstrap, identity artifact creation, seed commitment creation, mnemonic generation, private-key generation, or secret-store write
- Genesis/Atlas mutation, regeneration, or signing
- v0.2 signing
- CDL mutation or CDL-088 opening
- counsel approval, patent filing, trademark-policy publication, or legal conclusion

Public RC remains blocked:

```text
public_rc_remains_blocked_after_phase_1337
```

## 7. Next Phase

The next planned phase is:

```text
phase_1338_wallet_ecu_ilc_activation_gate_next
```

Phase 1338 remains sensitive and requires explicit future `GO Phase 1338`.

## 8. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_public_path_sidecar_activation_or_exclusion_gate_1337_v0.1.json,docs/specs/ilc_public_path_sidecar_activation_or_exclusion_gate_1337_v0.1.md -> planning/frontier
```
