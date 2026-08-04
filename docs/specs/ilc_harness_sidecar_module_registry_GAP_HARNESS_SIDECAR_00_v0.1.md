# ILC Harness Sidecar Module Registry GAP-HARNESS-SIDECAR-00 v0.1

**Status:** advisory source reconciliation registry
**Phase:** GAP-HARNESS-SIDECAR-00
**Date:** 2026-08-04
**Sensitivity:** NON-SENSITIVE

```text
harness_sidecar_module_registry_committed_GAP_HARNESS_SIDECAR_00
sidecar_registry_import_health_gate_passed_GAP_HARNESS_SIDECAR_00
```

## 1. Scope

This note reconciles current ILC harness and graph-native sidecar source state.
It is a registry and audit artifact only. It does not activate public sidecar
serving, public graph writes, public P2P, wallet writes, value-path writes, ECU
minting, ILC settlement, public RC, mainnet, external withdrawal, or any CDL.

The controlling architecture is that ILC is agent-native and harness-agnostic.
OpenClaw, NemoClaw, Hermes-like harnesses, Codex-style agents, and future ILC
hosts are adapters over ILC-native protocol surfaces; they are not protocol
substrates.

## 2. Source Inputs Read

- `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md`
- `docs/architecture/ilc_harness_architecture_spec_1459p_v0.1.md`
- `docs/research/ilc_web2_service_primitive_trust_recipe_mapping_v0.1.md` §6.5
- `docs/phases/phase_0468_genesis_validator_openclaw_scoping_and_window_closure_gate_walkthrough.md`
- `docs/specs/ilc_agent_skills_surface_spec_621_v0.1.md`
- `docs/specs/ilc_bounded_ecu_exchange_model_622_v0.1.md`
- `ilc_core/sidecars/registry_manifest.py`
- `ilc_core/sidecars/`
- `ilc_core/harness/`

MemPalace query `sidecar registry manifest import harness circular dependency
fix` returned planning references to the graph-native sidecar suite, Phase 1307
registry manifest, OpenClaw/NemoClaw local bridge profile, and local/package
metadata boundary. No MemPalace result authorized public serving or value-path
activation for this phase.

## 3. Import Health Finding

Before GAP-HARNESS-SIDECAR-00, importing
`build_sidecar_registry_manifest()` failed through a circular dependency:

```text
registry_manifest
-> local_graph_memory_projection
-> sidecar_query_runtime
-> agent_graph_projection_runtime
-> public_path_activation
-> openclaw_p2p_relay
-> routing_reputation_runtime
-> centrality_delta_gossip_runtime
-> ilc_core.epistemic.__init__
-> ingestion_shadow_harness
-> genesis work/epoch/economics imports
-> epoch_attribution_settle_runtime
-> centrality_delta_gossip_runtime while partially initialized
```

The fix extracts dependency-light CDL-060 constants into
`ilc_core/network/d2d/centrality_delta_gossip_constants.py`. Modules that only
need `CDL_060_GOSSIP_RUNTIME_VERSION` or `CENTRALITY_QUANTUM` now import those
constants without importing the full gossip runtime. The centrality runtime
still exports the same values.

Verified command:

```text
.venv/bin/python -c "from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest; print('OK'); m=build_sidecar_registry_manifest(); print(len(m['sidecars']))"
OK
14
```

## 4. Current Sidecar Registry Manifest

`build_sidecar_registry_manifest()` currently returns 14 sidecar records. All
14 have `public_serving_enabled = False`.

| Sidecar ID | Component | Status | Authority gate |
|---|---|---|---|
| `confidential_coordination_capability_membership_boundary` | `ccss_002_capability_membership_boundary` | `contract_recorded_phase_1325_no_public_serving` | `phase_1325_private_local_contract_only` |
| `confidential_coordination_gossip_jitter_cover_policy` | `ccss_004_gossip_jitter_cover_policy_tests` | `contract_recorded_phase_1327_no_public_serving` | `phase_1327_private_local_contract_only` |
| `confidential_coordination_local_preview` | `confidential_coordination_local_preview_profile` | `profile_declared_phase_1307` | `phase_1324_1329_required_for_runtime_dry_run` |
| `confidential_coordination_private_gated_shard` | `ccss_001_private_gated_shard_contract` | `contract_recorded_phase_1324_no_public_serving` | `phase_1324_private_local_contract_only` |
| `confidential_coordination_sealed_sender_local_delivery` | `ccss_003_sealed_sender_local_delivery_boundary` | `contract_recorded_phase_1326_no_public_serving` | `phase_1326_private_local_contract_only` |
| `local_graph_memory_projection` | `local_sidecar_query_runtime` | `local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312` | `phase_1311_1312_local_projection_substrate_privacy_hardened_public_serving_blocked` |
| `offline_claimability_receipt_verifier` | `offline_claimability_receipt_verifier_sidecar` | `implemented_phase_1305_hardened_phase_1306` | `phase_1305_1306_local_verifier_only` |
| `openclaw_nemoclaw_local_bridge` | `openclaw_compatible_local_bridge` | `profile_declared_phase_1307` | `phase_1323_1328_private_dry_run_before_public_claim` |
| `public_fetch_p2p_readiness_candidate` | `public_fetch_p2p_readiness_candidate` | `readiness_candidate_recorded_phase_1313_default_off` | `phase_1313_default_off_readiness_only_rust_public_p2p_gate_required` |
| `sidecar_registry_manifest` | `graph_native_sidecar_registry_manifest` | `implemented_phase_1307` | `phase_1307_local_package_metadata_only` |
| `transport_principal_admission` | `transport_principal_identity` | `lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310` | `phase_1309_1310_local_lifecycle_substrate_public_path_blocked` |
| `truth_primitive_submission_boundary` | `graph_native_sidecar_registry_manifest` | `boundary_recorded_phase_1308_no_public_serving` | `phase_1308_boundary_recorded_public_export_still_blocked` |
| `value_path_activation_boundary_preflight` | `value_path_activation_boundary_preflight` | `preflight_recorded_phase_1315_no_ecu_mint_or_ilc_settlement_activation` | `phase_1315_preflight_only_value_path_activation_blocked` |
| `wallet_action_semantics_preflight` | `wallet_action_semantics_preflight` | `preflight_recorded_phase_1314_no_wallet_action_activation` | `phase_1314_preflight_only_wallet_actions_blocked` |

## 5. Harness Runtime Inventory

`ilc_core/harness/` contains private harness proof-of-concept modules from the
1459p lane:

| Module | Current role |
|---|---|
| `provider_usage_adapter.py` | Local provider token budget and quota signal tracking. |
| `local_node_capture.py` | Deterministic private capture snapshots from local node data. |
| `consent_gate.py` | Explicit consent checks before private capture-to-artifact transitions. |
| `idle_capacity_scheduler.py` | Local idle-budget routing for private maintenance tasks. |
| `maintenance_task_executor.py` | Deterministic fixture-task execution for private artifacts. |
| `co_attestation_receipt.py` | Local co-attestation receipt construction and verification. |
| `local_immutable_store.py` | Local immutable record persistence helper. |

These files remain private/default-off architecture or local runtime surfaces.
They are not public-RC sidecar serving modules and are not imported into public
packaging by this phase.

## 6. CLI And Agent Action Anchors

Current harness-relevant CLI/action surfaces include:

- `ilc agent keygen`, added by GAP-AGENT-KEYGEN-00, for explicit local Ed25519
  action-hotkey generation.
- `ilc submit --signing-key file:///path/to/hotkey.pem`, added by
  GAP-GRAPH-SIGN-00, for
  optional self-contained truth primitive signing.
- Existing value-action and ECU transfer lanes, which are scoped to agent-id
  ILC transfer and bounded graph-contextual ECU movement only where separately
  activated.

No automatic hotkey generation occurs in this phase. No key resolver, central
registry, generalized `ILCSigningProvider`, `env://` provider, hardware signer,
or secp256k1 provider is created here.

## 7. Gap Register

| Gap | Disposition |
|---|---|
| Startup import health for `build_sidecar_registry_manifest()` | Closed by GAP-HARNESS-SIDECAR-00 constants extraction. |
| CLI/JSON conformance matrix across all agent-facing commands | Route to GAP-HARNESS-SIDECAR-01. |
| AgentID plus hotkey onboarding guide and private harness CLI audit | Route to GAP-HARNESS-SIDECAR-02. |
| Generalized `AgentActionEnvelope` beyond transfer-specific runtime | SENSITIVE; route to GAP-HARNESS-SIDECAR-03/CDL work. |
| Public graph read/query hardening | Route to GAP-HARNESS-SIDECAR-04a. |
| Public graph write/refutation/admission hardening | SENSITIVE; route to GAP-HARNESS-SIDECAR-04b. |
| Execution receipt schema/runtime for sidecar tool actions | Route to GAP-HARNESS-SIDECAR-05. |
| Value-action sidecar integration | SENSITIVE if guard state changes; route to GAP-HARNESS-SIDECAR-06. |
| Optional Tier 1/Tier 2 root skills pack | Route to GAP-HARNESS-SIDECAR-07. |
| Task coordination and market commissioning recipes | Route to GAP-HARNESS-SIDECAR-08/09. |
| End-to-end harness soak | SENSITIVE if connected to public graph/value; route to GAP-HARNESS-SIDECAR-10. |

## 8. Non-Claims

This phase does not claim or authorize:

- public sidecar serving;
- public graph mutation;
- public P2P or public fetch serving;
- wallet write, transfer, spend, withdrawal, or external address collection;
- ECU minting or ILC settlement;
- generalized ECU money transfer;
- hotkey-to-AgentID binding authority;
- central signing registry or resolver;
- `OperatorDelegationRecord` runtime;
- `PUBLIC_RC_EXCLUDE` promotion;
- public mirror push;
- public RC, mainnet, or epoch transition.
