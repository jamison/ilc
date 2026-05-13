# ILC Launch Roadmap: Three Computers, Seven Agents

**Version:** v1.1
**Produced:** 2026-05-08
**Phase:** 1242
**Status:** CURRENT controlling public-RC roadmap after Phase 1242
**Supersedes:** `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md`

`launch_roadmap_v1_1_published_phase_1242`
`roadmap_v1_1_controlling_public_rc_roadmap_phase_1242`

---

## 1. Purpose

Roadmap v1.1 replaces Roadmap v1.0 as the controlling public-RC roadmap. The
refresh is not an addendum: v1.0 contained stale RC2 rows after later windows
ratified CDL-086, implemented Tier-3 runtime linkage, implemented and wired the
persistent fetch rate limiter, completed SIM-FETCH-01 evidence through Fix10,
and opened Window 1241-1248.

This roadmap governs public-RC execution from Window 1241-1248 onward. It
preserves the default public-RC path selected in current planning:

```text
openclaw_nemoclaw_skill_first_public_rc_path_no_public_ilc_p2p_claim
public_claimability_required_for_final_public_rc_profile
gap_14_package_modularity_executes_before_gap_10_public_p2p
```

---

## 2. Current Canon Baseline

| Surface | Current status |
|---------|----------------|
| Window frontier | Window 1303-1316 is CLOSED / PASS with carry-forward through Phase 1316; closure handoff is `docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md`; sequence lock `docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md` and guidance `docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md` are closed references; no next phase is assigned; Window 1317+ sequence lock is required before any further phase assignment; no public RC, public activation, publication, release artifact production, release-key generation, Genesis Atlas mutation/regeneration/signing, CDL-088, wallet-facing action activation, ECU minting activation, ILC settlement activation, withdrawal runtime, final value-path activation authority, or v0.2 signing authorization is granted |
| Capsule | v5.53 current; supersedes v5.52 and is updated through Phase 1316 |
| Prior closure | Window 1233-1240 CLOSED / PASS at Phase 1240 |
| CDL-086 | **RATIFIED** in Phase 1220 (`cdl_086_ratified_phase_1220`) |
| CDL-087 | **RATIFIED** in Phase 1278 Fix1 (`cdl087_ratified_phase_1278_fix1`); public fetch serving, public sidecar/projection serving, CDL-088, and public RC remain separately gated |
| v0.2 signing | Deferred; explicit signing authorization absent |
| Tier-3 runtime linkage | **IMPLEMENTED** in Phase 1201 (`tier3_runtime_linkage_runtime_1201.v0.1`) |
| Persistent fetch rate limiter backend | **IMPLEMENTED** in Phase 1202 (`persistent_fetch_rate_limiter_runtime_1202.v0.1`) |
| Persistent limiter HTTP wiring | **WIRED** in Phase 1212 (`persistent_rate_limiter_transport_wiring_committed_phase_1212`) |
| `commit.epoch` runtime alignment | Complete through devnet E2E harness; production emission unauthorized |
| L3 sidecar query runtime | Local/read-only runtime complete; Phase 1268 records loopback/subprocess-only boundary with no new listener and Phase 1278 adds an internal public-path preflight helper while keeping public/non-loopback projection serving blocked |
| TransportPrincipal runtime identity | Phase 1267 pre-public helper implemented for authenticated credential key derivation; Phase 1309 adds the local admission sidecar substrate; Phase 1310 hardens revocation, replay, admission, ban, rate-limit, and privacy negative paths; Phase 1313 records a default-off public fetch/P2P readiness packet and Rust substrate gate status; no public P2P, public fetch serving, public listener, peer discovery, public revocation registry, public replay cache, public rate-limit state, or non-loopback serving activation |
| SIM-FETCH-01 | Evidence complete through Fix10 robustness suite; consumed into CDL-087 ratification by Phase 1278 Fix1 |

Latest closed handoff and current window artifacts:

```text
docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md
docs/specs/ilc_window_1257_1264_handoff_1264_v0.1.md
window_1257_1264_closed_phase_1264
docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md
docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md
cdl_087_ratification_decision_phase_1266=no_ratification_no_register_mutation
docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md
transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1
docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md
sidecar_loopback_projection_endpoint_boundary_phase_1268.v0.1
docs/specs/ilc_werner_default_topology_pressure_profile_1269_v0.1.md
werner_default_topology_pressure_profile_phase_1269.v0.1
docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md
gap13_claimability_conversion_sweeper_preflight_phase_1270.v0.1
public_claimability_runtime_not_activated_phase_1270
cdl_048_conversion_sweeper_requirements_recorded_phase_1270
wallet_withdrawal_transfer_spend_not_enabled_phase_1270
docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md
atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1
public_rc_graph_reachability_verdict_recorded_phase_1271
public_release_artifact_not_authorized_phase_1271
no_genesis_atlas_mutation_phase_1271
atlas_g_006_manifest_profile_consistency_hardening_phase_1271_fix1.v0.1
docs/specs/ilc_window_1265_1272_handoff_1272_v0.1.md
window_1265_1272_closed_phase_1272
window_1265_1272_closure_gate_verdict=pass
phase_1272_window_1265_1272_closure_complete
window_1273_plus_sequence_lock_required_before_next_phase_assignment
docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md
window_1273_1280_sequence_lock_committed
window_1273_1280_sequence_lock_verdict=pass
docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
ecu_lot_deadline_epoch_enforcement_recorded_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
docs/specs/ilc_cdl087_ratification_authorization_preflight_1276_v0.1.md
cdl087_ratification_authorization_preflight_phase_1276.v0.1
docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md
transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1
docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md
release_manifest_allowlist_publication_preflight_phase_1279.v0.1
docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md
window_1273_1280_closed_phase_1280
window_1273_1280_closure_gate_verdict=pass
phase_1280_window_1273_1280_closure_complete
window_1281_plus_sequence_lock_required_before_next_phase_assignment
```

---

## 3. Public-RC Branch Decision

Default branch:

```text
public_rc_default_path=openclaw_skill_first_public_claimability_no_public_p2p_claim
```

Meaning:

- The first public-RC path is a graph-native sidecar suite that can be hosted by
  OpenClaw/NemoClaw, Codex-style agents, or a future first-party ILC harness.
- That path makes no public ILC-owned P2P claim.
- OpenClaw/NemoClaw are hosts or consumers of ILC graph-native sidecars, not
  protocol substrates and not protocol-truth authorities.
- Public ILC-owned P2P remains a parallel lane gated by TransportPrincipal and
  Rust public-P2P substrate work.
- A local preview profile is not final public RC.
- The final public-RC profile must include public ECU-to-ILC claimability.

---

## 4. Public-RC Blocker Classes

| Blocker class | Blocks | Current disposition |
|---------------|--------|---------------------|
| Public repository publication | Making selected source tree public | Blocked by license/IP/provisional-patent/allowlist work |
| Public RC claim | Claiming any release candidate is public | Blocked until selected package profile, claimability, graph reachability, release manifest, and blocker classes close |
| Public P2P exposure | Public hostile-network ILC node | Blocked by TransportPrincipal, Rust P2P substrate decision, Python HTTP downgrade |
| Public sidecar/projection serving | Non-loopback graph/projection endpoint | Blocked by CDL-087 ratification plus TransportPrincipal policy if exposed beyond loopback |
| Public economic claimability | Human withdrawal/claim/transfer path | Blocked by ECU-to-ILC conversion runtime and public claimability substrate |
| Graph-native sidecar suite local preview | Local truth/projection/claimability sidecars operated by a harness or native ILC host | Essential-suite planning routed to Windows 1303-1342; no public serving authority |
| OpenClaw/NemoClaw local skill preview | Local host/consumer preview of the graph-native sidecar suite | Open execution lane in Window 1241-1248; not final public RC |
| OpenClaw/NemoClaw claimable public RC | Final selected public-RC target profile hosted by OpenClaw/NemoClaw or equivalent | Requires essential sidecar suite, Gap 14 package modularity, and Gap 13 claimability path |

Token:

```text
public_rc_blocker_classification_required_in_roadmap_v1_1
ilc_graph_native_sidecar_suite_architecture_recorded
openclaw_nemoclaw_are_hosts_not_protocol_substrates
essential_openclaw_rc_sidecars_truth_projection_claimability_bridge
sidecar_suite_public_serving_remains_blocked_until_explicit_authority
```

Status: satisfied by this roadmap as a classification surface; blockers remain
open until their implementation/gate phases close.

---

## 5. Milestone Map

| Milestone | Gate criteria | Current status |
|-----------|---------------|----------------|
| RC0.1 | Three-node substrate; seven-agent scenario; reproducible substrate | `satisfied_for_testbed` |
| RC1 | Truth primitive stack operational; CDL-073 through CDL-084; HB-002 closed | `satisfied` |
| RC2 | Pre-public-RC governance/runtime hardening, v0.2 decision, package/public-path blocker disposition | In progress; several original v1.0 subgates now satisfied |
| Public-RC local harness preview | Clean graph-native sidecar suite hosted by OpenClaw/NemoClaw or equivalent; no public P2P; no final claimability claim | Window 1241-1248 execution lane plus Windows 1303-1342 essential-suite routing |
| Public-RC claimable harness profile | Graph-native sidecar suite package plus public ECU-to-ILC claimability; no public ILC P2P claim | Target profile, still blocked |
| Public P2P RC | ILC-owned public P2P node | Parallel lane, blocked by TransportPrincipal and Rust P2P decisions |
| Public launch | Post-RC launch obligations, counsel/IP/trademark, economic claimability, security gates | Long-range |

---

## 6. Gap Inventory

### Gap 1 - v0.2 Signing Ceremony

**Status:** Deferred.

v0.2 remains an unsigned 41-node / 73-edge candidate. Explicit signing
authorization remains required.

Token:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

### Gap 2 - Public-Launch Packaging Blocker / CDL-086

**Status:** Governance precondition satisfied; public acts still blocked.

CDL-086 was ratified in Phase 1220:

```text
cdl_086_ratified_phase_1220
```

Ratification did not authorize public launch, public repository publication,
public RC claim, release-key generation, or external operator bootstrap.
Remaining package/publication work is now tracked by blocker classes and Gap 7.

### Gap 3 - Tier-3 Runtime Linkage

**Status:** Satisfied at runtime level.

Phase 1201 implemented additive Tier-3 runtime linkage validation:

```text
tier3_runtime_linkage_runtime_1201.v0.1
```

### Gap 4 - Persistent Rate Limiter

**Status:** Satisfied for current devnet/test HTTP transport; not a public-P2P
identity solution.

Phase 1202 implemented the persistent backend:

```text
persistent_fetch_rate_limiter_runtime_1202.v0.1
```

Phase 1212 wired it into HTTP fetch transport:

```text
persistent_rate_limiter_transport_wiring_committed_phase_1212
```

For public hostile-network P2P, this remains insufficient until rate limiting
binds to authenticated TransportPrincipal rather than IP or JSON/body identity.

### Gap 5 - Truth-Primitive Permanence

**Status:** Attested/governance-routed through Phase 1219.

Phase 1219 records Genesis authority attestation, no dissent, and non-bypass
rules. It does not remove later public-RC packaging, signing, or claimability
obligations.

### Gap 6 - Canon Bundle Signing Repair

**Status:** Satisfied in Phase 1197.

```text
canon_bundle_signing_repair_pass_phase_1197
```

### Gap 7 - Counsel, License, CLA, Trademark, IP

**Status:** Partially satisfied after Phase 1323 Fix3. The root license and
zone table are now implemented provisionally as a layered posture, with
`AGPL-3.0-only` as the runtime/package default and `LICENSING.md` as the zone
table. Future counsel review/modification remains expected, but unresolved
root-license selection is no longer a standalone implementation blocker. Phase
1300 inventoried this state only and granted no legal clearance, IP filing,
paper publication, repository publication, or package publication authority.
Phase 1255 defines the allowlist-export procedure, but does not authorize
publication. CLA, trademark, IP/patent gates, source-export execution, and
explicit publication authorization remain open.

Required:

- Root license and zone table decision: implemented provisionally in Phase 1323
  Fix3; future counsel review/modification expected.
- DCO/CLA decision before external contributors.
- Trademark policy before public launch.
- US provisional patent filing before public repository publication.
- Public-source allowlist/export procedure: defined in Phase 1255, execution
  still blocked.

Tokens:

```text
layered_license_posture_implemented_phase_1323_fix3
counsel_license_review_future_modification_not_public_rc_blocker_phase_1323_fix3
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
us_provisional_patent_application_filed_required_before_public_repo_publication
allowlist_export_procedure_defined_required_before_public_repo_publication
allowlist_export_procedure_defined_phase_1255
public_repository_publication_not_authorized_phase_1255
```

### Gap 8 - Long-Range Economic, Privacy, Scale, and Formal Work

**Status:** Deferred / mixed.

Includes multi-hop centrality attribution CDL, cross-epoch compaction,
CDL-070 PQ ceremony, reputation/centrality float migration, dynamic epistemic
traversal engine, and later TLA+/TLAPS work. The immediate pre-RC TLA item is
now closed as informal refinement notes. Post-launch Spec D, TLAPS, and
economic specs remain deferred. Spec A must not be described as a clean
completed `MaxRound=12` gate; Phase 816 was memory-bound without a discovered
counterexample before heap exhaustion.

```text
tla_refinement_notes_pre_rc_window_1241_plus_candidate
tla_refinement_notes_pre_rc_closed_phase_1255
phase_1255_tla_allowlist_export_complete
```

### Gap 9 - Sidecar Projection Endpoint

**Status:** Blocked.

Local read-only sidecar query runtime exists. No projection endpoint is
authorized. Non-loopback projection serving requires CDL-087 ratification and
TransportPrincipal policy.

Tokens:

```text
sidecar_projection_endpoint_required_post_cdl_087_ratification
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
```

### Gap 10 - TransportPrincipal Identity Layer

**Status:** Open; public-P2P hard requirement.

TransportPrincipal is the missing authenticated transport identity layer for
public hostile-network operation. It is required before public ILC-owned P2P
claim and before any non-loopback sidecar/projection public path.

Tokens:

```text
transport_principal_identity_required_before_public_p2p
d2d_rate_limiter_key_must_be_authenticated_transport_principal
agent_id_must_not_be_default_transport_rate_limit_key
json_requester_id_rate_limit_fallback_forbidden_public_p2p
transport_principal_cdl_required_before_runtime_implementation
python_http_transport_formally_downgraded_to_devnet_test_only_required
rust_p2p_substrate_decision_adr_required_quinn_vs_libp2p
```

### Gap 11 - Werner Topological Flow Governor

**Status:** SIM evidence surface exists; Phase 1263 sensitive decision recorded
no CDL opening or prelock.

SIM-FETCH Fix8 implemented an opt-in simulation-only Werner topology overlay.
Future work must promote or retire the overlay before runtime-CDL use. Heat
signals prefer reputation, routing, admission, and cache/mirror priority before
any direct ECU creation assumption.

Phase 1262 promoted Werner only as a future SIM-FETCH evidence profile after
follow-up. Phase 1263 then executed the sensitive Werner CDL decision gate and
recorded that evidence is not yet sufficient to open or prelock a Werner
flow-governor CDL. The closing conditions are now explicit: default evidence
profile, beta/noise decomposition, spectral trust threshold discipline,
TransportPrincipal/admission binding before public-path effects, and separate
productive-credit authorization before any value path.

Phase 1269 closes only the default evidence-profile recording condition by
adding an explicit SIM-FETCH profile adapter for `topology_pressure_model=werner_v1`
and preserving `topology_pressure_model=none` as the comparison profile. It is
simulation/evidence only and does not open/prelock a Werner CDL, activate
runtime economic policy, mint ECU, settle ILC, or activate public claimability.

Tokens:

```text
werner_flow_governor_cdl_opening_prelock_decision_phase_1263.v0.1
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
direct_werner_ecu_creation_rejected_phase_1263
phase_1263_sensitive_cdl_gate_complete
werner_default_topology_pressure_profile_phase_1269.v0.1
topology_pressure_model_werner_v1_profile_recorded_phase_1269
werner_none_profile_control_preserved_phase_1269
no_werner_ecu_minting_or_ilc_settlement_phase_1269
werner_overlay_opt_in_must_be_promoted_or_retired_after_validation
werner_heat_prefers_reputation_routing_admission_before_ecu_creation
direct_werner_ecu_creation_assumption_requires_repo_memtrace_check
heat_signal_must_not_directly_mint_ecu
beta_decomposition_required_before_policy_use
flow_governor_spectral_trust_threshold_required_before_policy_use
```

### Gap 12 - ECU Credit Creation In Agentic Wallet

**Status:** Open; public-launch hard requirement.

Wallet-visible balances are not ECU creation authority. Productive-credit
creation requires intent objects, authorization evidence, exposure ceilings,
escrow/clawback, and consensus-epoch settlement.

Tokens:

```text
agentic_wallet_ecu_credit_creation_runtime_required_pre_public_launch
ecu_credit_creation_intent_cdl_required
werner_productive_credit_authorization_cdl_required
ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation
```

### Gap 13 - ECU-to-ILC Settlement Execution Runtime and Claimability

**Status:** Open; Phase 1274 conversion-sweeper runtime skeleton, Phase 1275
local proof binding, and Phase 1305 offline/local verifier sidecar substrate
recorded. Public-RC claimability API/verifier serving authority remains open.

Internal conversion runtime and public claimability substrate are distinct.
Final public RC requires public claimability for the selected OpenClaw/NemoClaw
claimable profile.

Tokens:

```text
ecu_to_ilc_conversion_execution_runtime_required_pre_public_launch
pe_governor_fixed_point_runtime_required_pre_public_launch
mandatory_conversion_sweeper_required_for_cdl_048_runtime
ecu_lot_accounting_required_for_cdl_048_conversion_sweeper
ilc_public_claimability_substrate_required_pre_public_launch
public_claimability_required_for_final_public_rc_profile
gap13_claimability_conversion_sweeper_preflight_phase_1270.v0.1
public_claimability_runtime_not_activated_phase_1270
cdl_048_conversion_sweeper_requirements_recorded_phase_1270
wallet_withdrawal_transfer_spend_not_enabled_phase_1270
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
ecu_lot_deadline_epoch_enforcement_recorded_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1
claimability_verifier_local_only_no_api_phase_1305
receipt_verifier_public_serving_not_enabled_phase_1305
public_claimability_activation_not_authorized_phase_1305
phase_1306_proof_binding_canonical_hash_negative_path_tests_next
public_rc_remains_blocked_after_phase_1305
```

Phase 1270 recorded the public claimability and CDL-048 conversion-sweeper
requirements without activating runtime claimability. Phase 1274 adds the
narrow conversion-sweeper runtime skeleton for ECU lot accounting, four issuance
epoch deadline enforcement, finite exact numeric boundaries, canonical JSON
receipt/root binding, and replay or double-conversion prevention. Public
claimability still cannot close until later work authorizes a public verifier
and API; Phase 1275 only binds settled runtime roots, wallet-state roots,
latest balance receipts, history digests, epoch identifiers, canonical agent
identity, and conversion receipt semantics into a local proof boundary without
opening wallet withdrawal, transfer, or spend semantics.

Phase 1305 adds a local-only verifier sidecar substrate for canonical
claimability presentations and deterministic decisions. It validates local
receipt/proof/root material and keeps all public API, public verifier service,
public claimability activation, wallet action, ECU minting, and ILC settlement
flags false. It does not close final public claimability because public serving
authority, public-safe disclosure, replay/nullifier policy, duplicate-claim
policy, TransportPrincipal public-path authority, package/export materialization,
and release authority remain open.

### Gap 14 - OpenClaw/NemoClaw Package Modularity and CLI/Sidecar Boundary

**Status:** Immediate Window 1241-1248 execution lane.

Package modularity must prove that ILC can be consumed as a local skill/package
without making OpenClaw/NemoClaw a protocol dependency and without letting
Genesis, ILC, ECU, canonical JSON, protocol bundle verification, or Rust
consensus-core binding become excisable.

The corrected architecture is not an ordinary wrapper API. It is a
graph-native sidecar suite: sidecar registry/manifest, truth primitive
submission, local graph/memory projection, offline claimability/receipt
verification, and OpenClaw/NemoClaw bridge components that consume and emit
ILC-native graph objects. OpenClaw/NemoClaw remain optional hosts for the suite,
not protocol substrates.

Window 1241-1248 routing:

```text
gap_14_package_modularity_first_slice_before_gap_10_transport_principal
ilc_package_modularity_split_required_before_openclaw_skill_launch
ilc_logic_pure_protocol_interfaces_required
ilc_logic_must_not_require_http_lmdb_or_harness_transport
ilc_cli_package_boundary_required
harness_adapter_transport_storage_protocols_required
generic_agent_harness_adapter_contract_required
sidecar_dependency_isolation_required_for_harness_adapters
public_package_size_audit_required_before_openclaw_skill_launch
ilc_graph_native_sidecar_suite_architecture_recorded
graph_native_sidecar_creation_routed_to_forward_windows_1303_1342
essential_openclaw_rc_sidecars_truth_projection_claimability_bridge
```

First external harness deployment target remains private/local:

```text
digitalocean_openclaw_droplet_first_external_harness_target
tailscale_private_harness_network_allowed_no_public_p2p_claim
```

### Gap 15 - Atlas Graph Reachability and Integrated Phase Discipline

**Status:** Immediate Window 1241-1248 first slice; public-RC gate later.

Package modularity must not become excisability. Public-RC load-bearing
artifacts must remain reachable from Genesis, ILC, ECU, and hypergraph anchors.

Window 1241-1248 first-slice tokens:

```text
phase_close_graph_delta_field_required
atlas_g_001_graph_delta_schema_required
atlas_g_002_repo_hypergraph_compiler_hardening_required
atlas_g_003_package_profile_reachability_manifest_required
```

Later public-RC gate:

```text
atlas_g_006_public_rc_graph_reachability_gate_required
ilc_package_self_compilation_homoiconic_graph_required_before_public_rc
public_rc_release_artifact_must_include_profile_graph_manifest
```

---

## 7. Window 1241-1248 Execution Policy

| Phase | Role | Policy |
|-------|------|--------|
| 1242 | Roadmap v1.1 | This roadmap; no runtime/CDL mutation |
| 1243 | Gap 14 package profile contracts | RC-code execution begins |
| 1244 | Import-boundary lint and Protocol stubs | Enforce `ilc_logic` purity boundary |
| 1245 | OpenClaw/NemoClaw local skill preview | Local/private harness only |
| 1246 | CDL-087 governance review | Review-only; no ratification |
| 1247 | ATLAS-G-001..003 first slice | Graph discipline and package-profile reachability |
| 1248 | Closure | SENSITIVE; requires `GO Phase 1248` |

---

## 8. Non-Claims

This roadmap does not claim:

- public RC achieved;
- public launch achieved;
- public repository publication authorized;
- public P2P exposure authorized;
- public sidecar/projection serving authorized;
- CDL-087 ratified;
- CDL-088 opened;
- public claimability implemented;
- ECU minting or ILC settlement authorized;
- release keys generated;
- v0.2 signing executed;
- Genesis Atlas mutated.

---

## 9. Phase 1248 Closure Addendum

Window 1241-1248 closed at Phase 1248:

```text
window_1241_1248_closed_phase_1248
window_1241_1248_closure_gate_verdict=pass
```

Closure status updates:

- Roadmap v1.1 is the controlling public-RC roadmap.
- Gap 14 first slice is complete, but package split/CI remains open because the
  Phase 1244 `ilc_logic` migration debt still needs adapter extraction.
- OpenClaw/NemoClaw local skill preview exists as a local/private seam, not a
  final public-RC claim.
- CDL-087 governance review is complete, but ratification remains deferred
  pending production-candidate fetch evidence and a later sensitive phase.
- ATLAS-G-001..003 first slice is complete, but ATLAS-G-004..010 and the public
  RC graph reachability gate remain open.
- Final public RC still requires public claimability.
- No public ILC-owned P2P claim is introduced by this closure.

Recommended next-window direction:

```text
window_1249_plus_sequence_lock_required_before_next_phase_assignment
gap_14_adapter_extraction_and_package_ci_gate_should_continue_before_public_rc_claim
gap_13_public_claimability_runtime_should_start_before_final_public_rc_claim
transport_principal_identity_required_before_public_p2p
unknown_unknown_discovery_required_before_phase_execution
```

### Phase 1249+ prompt discipline addendum

Every future public-RC phase prompt derived from this roadmap should include the
four-part §0 discovery pass before coding: `Known-token audit`,
`Concept-discovery search`, `Contradiction and non-claim search`, and
`Source expansion and newly discovered tokens`. This is required because the
public-RC path crosses old terminology for ECU/ILC conversion, claimability,
TransportPrincipal, ATLAS-G, Werner flow, and publication/counsel gates.
MemPalace is advisory recall only; direct repo reads remain authoritative.
Exact-token `rg` is only a schema/completion check; concept discovery
must also search token components, synonyms, neighboring ideas, older names,
code symbols, and denial terms before any public-RC blocker is marked absent.

---

## 10. Phase 1256 Closure Addendum

Window 1249-1256 closed at Phase 1256:

```text
window_1249_1256_closed_phase_1256
window_1249_1256_closure_gate_verdict=pass
phase_1256_window_1249_1256_closure_complete
phase_1250_fix1_gap_audit_routes_reconciled_phase_1256
```

Closure status updates:

- Gap 14 adapter extraction, package CI, and package-size measurement closed
  for the selected OpenClaw/NemoClaw package profiles; no package publication
  or public RC claim occurred.
- Gap 13 public claimability remains blocked at runtime: Phase 1252 closed a
  sensitive boundary/classification pass and did not activate claimability,
  wallet withdrawal, wallet transfer, wallet spend, ECU mint, or ILC settlement
  semantics.
- TransportPrincipal is specified but not implemented as runtime public-P2P
  admission identity; public P2P and non-loopback sidecar/projection serving
  remain blocked.
- ATLAS-G-004/005 high-authority classification and dependency bridge closed,
  but ATLAS-G-006+ and the public-RC graph reachability gate remain open.
- TLA refinement notes and allowlist-export procedure closed for documentation
  scope; public repository publication remains unauthorized.
- Phase 1250 Fix1 routes are reconciled in
  `docs/specs/ilc_window_1249_1256_handoff_1256_v0.1.md`.
- CDL-087 remained open/prelocked/not ratified through this closure. This
  historical blocker is superseded by Phase 1278 Fix1 ratification.
- v0.2 signing remains deferred pending explicit signing authorization.

Public RC remains blocked after Phase 1256:

```text
public_rc_remains_blocked_after_phase_1256
window_1257_plus_sequence_lock_required_before_next_phase_assignment
```

Recommended next-window direction:

```text
gap13_claimability_runtime_conversion_sweeper_required_before_final_public_rc
transport_principal_runtime_adr_required_before_public_p2p
atlas_g_006_public_rc_graph_reachability_gate_required
cdl_087_production_candidate_evidence_ratification_phase_required
public_source_allowlist_execution_requires_publication_authorization
v0_2_signing_requires_explicit_human_authorization
```

## 11. Phase 1264 Closure Addendum

Window 1257-1264 closed at Phase 1264:

```text
window_1257_1264_closed_phase_1264
window_1257_1264_closure_gate_verdict=pass
phase_1264_window_1257_1264_closure_complete
window_1265_plus_sequence_lock_required_before_next_phase_assignment
```

Closure status updates:

- CDL-087 local production-candidate evidence improved: Phase 1259 recorded
  local Tier A/B/C classification and bootstrap snapshot builder/verifier
  evidence; Phase 1260 recorded local Section 6 observability and final
  CDL-077 limiter regression evidence.
- CDL-087 remained open/prelocked/not ratified at Phase 1264 close. Phase 1260 readiness was only:
  `cdl_087_ratification_readiness_verdict_phase_1260=ready_for_later_sensitive_ratification_review`.
- Public/non-loopback sidecar projection serving remains blocked:
  `sidecar_projection_endpoint_authorization_verdict_phase_1261=blocked_public_path`.
- TransportPrincipal remains a spec/ADR input, not runtime public-path identity
  with lifecycle, revocation, replay, privacy, and authenticated rate-limit
  binding.
- Werner remains an evidence lane. Phase 1262 promoted Werner only as a future
  SIM-FETCH topology-pressure evidence profile after follow-up; Phase 1263
  recorded `werner_flow_governor_cdl_decision_phase_1263=no_open_no_prelock`.
- Direct Werner ECU creation is rejected:
  `direct_werner_ecu_creation_rejected_phase_1263`.
- Public RC remains blocked by claimability runtime/conversion sweeper,
  CDL-087 sensitive ratification review, sidecar/public-path gates,
  TransportPrincipal/Rust public-P2P hardening, ATLAS-G-006+ graph reachability,
  counsel/publication authorization, and v0.2 signing authorization.

Public RC remains blocked after Phase 1264:

```text
public_rc_remains_blocked_after_phase_1264
```

Recommended Window 1265+ direction:

```text
cdl_087_sensitive_ratification_review_required_after_phase_1264
transport_principal_runtime_required_before_non_loopback_projection
sidecar_projection_public_path_still_blocked_after_phase_1264
werner_default_topology_pressure_profile_required_before_runtime_cdl
werner_productive_credit_authorization_cdl_required
gap13_claimability_runtime_conversion_sweeper_required_before_final_public_rc
atlas_g_006_public_rc_graph_reachability_gate_required
public_source_allowlist_execution_requires_publication_authorization
v0_2_signing_requires_explicit_human_authorization
```

---

## 12. Phase 1266 CDL-087 Review Addendum

Phase 1266 recorded the CDL-087 sensitive review decision:

```text
cdl_087_sensitive_ratification_review_phase_1266.v0.1
cdl_087_ratification_decision_recorded_phase_1266
cdl_087_ratification_not_executed_by_default_phase_1266
cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1266
no_public_fetch_serving_enabled_phase_1266
cdl_087_ratification_decision_phase_1266=no_ratification_no_register_mutation
```

Roadmap impact:

- CDL-087 remained open/prelocked/not ratified after Phase 1266. Phase 1278
  Fix1 later ratifies it with explicit register-mutation authorization.
- The CDL register was not mutated.
- The Phase 1258-1260 local evidence chain remains useful evidence for a later
  explicit ratification phase, but it did not become a ratification act.
- Public fetch serving remains disabled.
- Public/non-loopback sidecar projection remains blocked by missing CDL-087
  ratification and missing TransportPrincipal runtime/public-path policy.
- Public RC remains blocked by CDL-087 ratification, TransportPrincipal/Rust
  public-path hardening, public claimability/conversion sweeper, ATLAS-G-006+
  graph reachability, counsel/publication authorization, and v0.2 signing
  authorization.

## 13. Phase 1267 TransportPrincipal Pre-Public Identity Addendum

Phase 1267 added a bounded pre-public TransportPrincipal runtime helper:

```text
transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1
transport_principal_runtime_not_public_p2p_activation_phase_1267
requester_id_rate_limit_fallback_still_forbidden_phase_1267
non_loopback_projection_still_blocked_phase_1267
```

Roadmap impact:

- The public-path identity blocker is reduced but not closed.
- Future public fetch/P2P admission, rate-limit, ban, and replay paths now have
  a local deterministic helper to derive full-hash keys from authenticated
  transport credential material.
- JSON/body `requester_id`, AgentID, harness identity, and `client_ip` remain
  forbidden as public-path identity fallbacks.
- Public P2P, public fetch serving, and public/non-loopback sidecar projection
  serving remain disabled.

Public RC remains blocked after Phase 1267:

```text
public_rc_remains_blocked_after_phase_1267
public_rc_remains_blocked_after_phase_1266
```

## 14. Phase 1268 Sidecar Loopback Boundary Addendum

Phase 1268 recorded the sidecar endpoint boundary:

```text
sidecar_loopback_projection_endpoint_boundary_phase_1268.v0.1
sidecar_loopback_only_no_non_loopback_serving_phase_1268
sidecar_public_path_still_blocked_phase_1268
transport_principal_required_before_non_loopback_projection_phase_1268
```

Roadmap impact:

- No HTTP server, socket listener, Unix-socket server, peer-discovery surface,
  non-loopback bind, public sidecar/projection serving, or public P2P exposure
  was implemented.
- Local in-process sidecar query/export and local skill-preview seams remain the
  only active sidecar surfaces.
- Future loopback or Unix-socket prototypes require explicit phase scope and
  must remain local-only.
- Non-loopback sidecar/projection serving still requires CDL-087 or equivalent
  governance authorization, full TransportPrincipal public-path integration,
  privacy/replay/revocation controls, Rust/public-P2P hardening, and ATLAS-G
  public-RC graph closure.

Public RC remains blocked after Phase 1268:

```text
public_rc_remains_blocked_after_phase_1268
public_rc_remains_blocked_after_phase_1267
public_rc_remains_blocked_after_phase_1266
```

## 15. Phase 1269 Werner Default Topology-Pressure Profile Addendum

Phase 1269 recorded the Werner default profile as simulation/evidence:

```text
werner_default_topology_pressure_profile_phase_1269.v0.1
topology_pressure_model_werner_v1_profile_recorded_phase_1269
werner_none_profile_control_preserved_phase_1269
no_werner_ecu_minting_or_ilc_settlement_phase_1269
```

Roadmap impact:

- `topology_pressure_model=werner_v1` now maps to the existing SIM-FETCH Werner
  overlay as the explicit default evidence profile.
- `topology_pressure_model=none` remains the comparison/control profile.
- Canonical evidence export rejects float, serializes finite Decimal values,
  uses `sort_keys=True` and `allow_nan=False`, and enforces a max-byte bound.
- Werner still does not authorize a runtime flow-governor CDL, ECU minting, ILC
  settlement, public claimability, wallet semantics, public P2P, public fetch
  serving, or public sidecar/projection serving.

Public RC remains blocked after Phase 1269:

```text
public_rc_remains_blocked_after_phase_1269
public_rc_remains_blocked_after_phase_1268
public_rc_remains_blocked_after_phase_1267
public_rc_remains_blocked_after_phase_1266
```

## 16. Phase 1270 Gap 13 Claimability Conversion-Sweeper Preflight Addendum

Phase 1270 recorded Gap 13 preflight requirements:

```text
gap13_claimability_conversion_sweeper_preflight_phase_1270.v0.1
public_claimability_runtime_not_activated_phase_1270
cdl_048_conversion_sweeper_requirements_recorded_phase_1270
wallet_withdrawal_transfer_spend_not_enabled_phase_1270
```

Roadmap impact:

- CDL-048 remains ratified with `ecu_conversion_deadline = 4 issuance epochs`,
  but the mandatory conversion sweeper runtime is not complete.
- Future sweeper runtime must track ECU lots, issue epochs, provenance,
  deadline epochs, conversion status, and replay/double-conversion keys.
- Future public claimability must consume settled runtime roots, wallet-state
  roots, latest balance receipts, history digests, epoch identifiers, canonical
  agent identity, and full SHA-256 or stronger proof binding.
- The current lifecycle and public wallet runtimes remain read-only/deferred and
  do not expose withdrawal, transfer, spend, signing, minting, or settlement
  authority.
- Non-loopback claimability APIs remain blocked until TransportPrincipal or an
  equivalent authenticated transport identity contract is authorized and
  integrated.

Public RC remains blocked after Phase 1270:

```text
public_rc_remains_blocked_after_phase_1270
public_rc_remains_blocked_after_phase_1269
public_rc_remains_blocked_after_phase_1268
public_rc_remains_blocked_after_phase_1267
public_rc_remains_blocked_after_phase_1266
```

## 17. Phase 1271 ATLAS-G-006 Public-RC Graph Reachability Gate Addendum

Phase 1271 recorded the ATLAS-G-006 public-RC graph reachability verdict:

```text
atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1
public_rc_graph_reachability_verdict_recorded_phase_1271
public_release_artifact_not_authorized_phase_1271
no_genesis_atlas_mutation_phase_1271
atlas_g_006_manifest_profile_consistency_hardening_phase_1271_fix1.v0.1
```

Roadmap impact:

- Selected profile `openclaw_skill_claimable` passes the graph reachability gate
  for the required `ecu`, `genesis`, `hypergraph`, and `ilc` anchors.
- The Phase 1254 high-authority dependency bridge provides the required package
  component, package surface, anchor reachability, Python, Rust, CLI, and source
  classification edge families.
- ATLAS-G-006 is no longer the selected-profile graph reachability blocker.
- Phase 1271 Fix1 hardens supplied-manifest profile consistency; top-level or
  nested profile-id mismatch now fails closed with
  `atlas_g_006_manifest_profile_mismatch`.
- This does not authorize public release artifact production, public RC claim,
  public repository publication, Genesis Atlas mutation/regeneration/signing, or
  v0.2 signing.

Public RC remains blocked after Phase 1271:

```text
public_rc_remains_blocked_after_phase_1271
public_rc_remains_blocked_after_phase_1270
public_rc_remains_blocked_after_phase_1269
public_rc_remains_blocked_after_phase_1268
public_rc_remains_blocked_after_phase_1267
public_rc_remains_blocked_after_phase_1266
```

## 18. Phase 1272 Window 1265-1272 Closure Addendum

Phase 1272 closed Window 1265-1272:

```text
window_1265_1272_closed_phase_1272
window_1265_1272_closure_gate_verdict=pass
phase_1272_window_1265_1272_closure_complete
window_1273_plus_sequence_lock_required_before_next_phase_assignment
```

Roadmap impact:

- CDL-087 remained open/prelocked/not ratified at Phase 1272 close; Phase 1266
  recorded no-ratification/no-register-mutation, and any future CDL-087
  ratification or register mutation required explicit future human ratification
  authorization. Phase 1278 Fix1 later consumed that authorization.
- TransportPrincipal has a pre-public helper, but full public-path ADR,
  revocation, replay, privacy, rate-limit binding, and Rust/public-P2P
  hardening remain open.
- Sidecar/projection remains local-only or loopback/subprocess/Unix-socket
  scoped; public/non-loopback serving remains blocked.
- Werner `topology_pressure_model=werner_v1` is now the default SIM-FETCH
  evidence profile and `none` remains the control profile, but no Werner CDL,
  ECU minting, ILC settlement, or public claimability is authorized.
- Gap 13 and CDL-048 conversion-sweeper requirements are recorded, but public
  claimability runtime, wallet withdrawal/transfer/spend, ECU minting, and ILC
  settlement remain blocked.
- ATLAS-G-006 is no longer the selected-profile graph reachability blocker for
  `openclaw_skill_claimable`; Phase 1271 Fix1 also makes supplied-manifest
  profile-id mismatches fail closed with `atlas_g_006_manifest_profile_mismatch`.
- Public release artifact production, public RC claim, public repository
  publication, Genesis Atlas mutation/regeneration/signing, release manifest
  publication, allowlist publication, and v0.2 signing remain unauthorized.
- Window 1273+ sequence lock is required before assigning further phase numbers.

Public RC remains blocked after Phase 1272:

```text
public_rc_remains_blocked_after_phase_1272
public_rc_remains_blocked_after_phase_1271
public_rc_remains_blocked_after_phase_1270
public_rc_remains_blocked_after_phase_1269
public_rc_remains_blocked_after_phase_1268
public_rc_remains_blocked_after_phase_1267
public_rc_remains_blocked_after_phase_1266
```

## 19. Phase 1274 CDL-048 Conversion-Sweeper Runtime Skeleton Addendum

Phase 1274 recorded the narrow CDL-048 runtime skeleton:

```text
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
ecu_lot_deadline_epoch_enforcement_recorded_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
```

Roadmap impact:

- CDL-048 ECU lot registration now has a bounded runtime skeleton with exact
  positive Decimal-compatible amount handling, issue epoch tracking, computed
  four-issuance-epoch deadline, origin, funding provenance, and conversion
  status.
- Internal conversion receipts now bind conversion epoch, canonical agent id,
  lot id, wallet-state root, conversion transition, settled runtime root, and
  sweeper state root using canonical JSON and SHA-256.
- Replay and double-conversion guards are present at the skeleton state level,
  and stale settled-runtime root epoch mismatches fail closed.
- The skeleton does not prove public claimability, wallet-root membership,
  latest-balance receipt inclusion, or non-loopback API authority; those remain
  routed to Phase 1275 and later.
- Public claimability runtime, wallet withdrawal/transfer/spend, ECU minting,
  and ILC settlement remain blocked.

Public RC remains blocked after Phase 1274:

```text
public_rc_remains_blocked_after_phase_1274
public_rc_remains_blocked_after_phase_1272
public_rc_remains_blocked_after_phase_1271
public_rc_remains_blocked_after_phase_1270
```

## 20. Phase 1275 Claimability Proof-Binding Runtime Boundary Addendum

Phase 1275 recorded the local proof-binding boundary:

```text
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
```

Roadmap impact:

- Future claimability verification now has a deterministic local binding over
  settled runtime root, wallet-state root, latest balance receipt, history
  digest, epoch identifier, canonical agent identity, and Phase 1274 conversion
  receipt semantics.
- Proof exports use canonical JSON with deterministic key ordering,
  `allow_nan=False`, compact separators, and full SHA-256 digest bindings.
- Phase 1275 rejects floats recursively from proof input payloads and validates
  full root, receipt, history, conversion-key, and proof hashes.
- The boundary remains local-only and does not add a public/non-loopback API,
  route, listener, wallet withdrawal, wallet transfer, wallet spend, ECU mint,
  ILC settlement, or public claim endpoint.
- Public RC remains blocked by CDL-087, public-path TransportPrincipal and
  sidecar serving gates, counsel/IP/publication authorization, v0.2 signing,
  release manifest/allowlist publication, and final public claimability API
  authority.

Public RC remains blocked after Phase 1275:

```text
public_rc_remains_blocked_after_phase_1275
public_rc_remains_blocked_after_phase_1274
public_rc_remains_blocked_after_phase_1272
public_rc_remains_blocked_after_phase_1271
public_rc_remains_blocked_after_phase_1270
```

## 21. Phase 1276 CDL-087 Ratification Authorization Preflight Addendum

Phase 1276 recorded the CDL-087 authorization preflight:

```text
cdl087_ratification_authorization_preflight_phase_1276.v0.1
cdl087_ratification_requires_explicit_human_ratification_authorization_phase_1276
cdl087_register_mutation_not_authorized_by_default_phase_1276
no_public_fetch_serving_enabled_phase_1276
```

Roadmap impact:

- CDL-087 evidence is now classified as ready for a future explicitly
  authorized ratification attempt, not as ratified.
- Phase 1276 does not mutate the CDL register; CDL-087 remains open/prelocked
  and not ratified.
- Future ratification must explicitly authorize CDL-087 ratification and CDL
  register mutation, then reprove all six conditions against current canon.
- Public fetch serving remains disabled; public P2P, public sidecar/projection
  serving, public claimability, public release artifacts, source publication,
  and v0.2 signing remain unauthorized.

Public RC remains blocked after Phase 1276:

```text
public_rc_remains_blocked_after_phase_1276
public_rc_remains_blocked_after_phase_1275
public_rc_remains_blocked_after_phase_1274
public_rc_remains_blocked_after_phase_1272
```

## 22. Phase 1277 TransportPrincipal Public-Path Preflight Addendum

Phase 1277 recorded the TransportPrincipal public-path ADR/runtime preflight:

```text
transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1
transport_principal_public_p2p_not_activated_phase_1277
requester_id_fallback_still_forbidden_phase_1277
non_loopback_projection_still_blocked_phase_1277
public_fetch_serving_not_enabled_phase_1277
cdl087_ratification_fix_phase_planned_after_1277_1278_if_both_pass_phase_1277
genesis_atlas_v0_2_signing_deferred_until_atlas_g_tail_phase_1277
```

Roadmap impact:

- Public-path admission, rate limiting, bans, and replay controls now have an
  internal preflight helper bound to authenticated TransportPrincipal material.
- The helper is marked `PUBLIC_RC_EXCLUDE` and is not a public RC launch surface.
- The helper rejects requester_id, client_ip, AgentID, and harness-identity
  fallback authority, and it keeps public P2P, public fetch serving, non-loopback
  projection, sidecar public path authorization, CDL-087 ratification, Rust
  public-P2P hardening completion, and release authorization false.
- Credential lifecycle, revocation, replay, privacy, canonical JSON, full
  SHA-256 binding, and recursive float rejection are now recorded for the
  TransportPrincipal public-path preflight boundary.
- The current window should plan a CDL-087 ratification Fix phase after Phase
  1277 and Phase 1278 if both pass, but that later Fix still requires explicit
  human ratification and CDL register mutation authorization.
- Genesis Atlas v0.2 signing remains deferred until the end of the planned
  Atlas-G phases.

Public RC remains blocked after Phase 1277:

```text
public_rc_remains_blocked_after_phase_1277
public_rc_remains_blocked_after_phase_1276
public_rc_remains_blocked_after_phase_1275
public_rc_remains_blocked_after_phase_1274
```

## 23. Phase 1278 Sidecar Non-Loopback Public-Path Preflight Addendum

Phase 1278 recorded the sidecar public-path authorization preflight:

```text
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
sidecar_public_serving_not_enabled_phase_1278
transport_principal_and_cdl087_required_before_public_projection_phase_1278
no_new_public_listener_phase_1278
non_loopback_bind_not_enabled_phase_1278
public_projection_endpoint_not_enabled_phase_1278
sidecar_projection_privacy_review_required_phase_1278
cdl087_ratification_fix_phase_planned_after_1277_1278_if_both_pass_phase_1278
```

Roadmap impact:

- Public sidecar/projection serving remained blocked in Phase 1278 because
  CDL-087 was not yet ratified and because TransportPrincipal public-path
  preflight was available only as an internal preflight, not activation
  authority.
- The Phase 1278 helper is marked `PUBLIC_RC_EXCLUDE` and is not a public RC
  launch surface.
- No public projection endpoint, non-loopback bind, wildcard bind, public host
  bind, new listener, peer discovery, public fetch serving, or public P2P
  exposure is authorized.
- Existing local sidecar query exports remain read-only, canonical, bounded,
  and float-safe.
- Before Phase 1278 Fix1, CDL-087 ratification was the next gated action
  requiring explicit authorization for ratification and CDL register mutation.
- Genesis Atlas v0.2 signing remains deferred until the end of the planned
  Atlas-G phases.

Public RC remained blocked after Phase 1278 before the Fix1 ratification:

```text
public_rc_remains_blocked_after_phase_1278
public_rc_remains_blocked_after_phase_1277
public_rc_remains_blocked_after_phase_1276
public_rc_remains_blocked_after_phase_1275
```

## 24. Phase 1278 Fix1 CDL-087 Ratification Addendum

Phase 1278 Fix1 records explicit CDL-087 ratification and CDL register mutation:

```text
cdl087_ratification_evidence_phase_1278_fix1.v0.1
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

Roadmap impact:

- CDL-087 is no longer a public-RC governance blocker; the CDL register now
  records `CDL-087` as ratified with evidence document
  `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md`.
- The six ratification conditions were re-proved from SIM-FETCH-01 evidence,
  Phase 1259 Tier A/B/C and bootstrap snapshot evidence, Phase 1260
  observability and limiter evidence, and Phase 1276 authorization preflight.
- Public fetch serving remains disabled; ratification does not activate
  CDL-077 serving endpoints, peer discovery, public P2P, or public release
  distribution.
- Public sidecar/projection serving remains blocked pending separate
  TransportPrincipal public-path activation, sidecar/projection serving
  authorization, privacy review, and hostile-network hardening.
- CDL-088 remains unopened. Reciprocal scoring and ECU-escrow admission remain
  deferred unless opened by a later explicit constitutional act.
- Phase 1279 remains the next locked non-sensitive inventory/prepublication
  preflight, and Genesis Atlas v0.2 signing remains deferred until the end of
  the planned Atlas-G phases.

Public RC remains blocked after Phase 1278 Fix1:

```text
public_rc_remains_blocked_after_phase_1278_fix1
public_rc_remains_blocked_after_phase_1278
public_rc_remains_blocked_after_phase_1277
public_rc_remains_blocked_after_phase_1276
```

## 25. Phase 1279 Release Manifest Allowlist Prepublication Addendum

Phase 1279 records release manifest/source allowlist prepublication inventory
only:

```text
release_manifest_allowlist_publication_preflight_phase_1279.v0.1
public_repository_publication_not_authorized_phase_1279
release_artifact_production_not_authorized_phase_1279
v0_2_signing_not_authorized_phase_1279
source_allowlist_export_not_executed_phase_1279
release_keys_not_generated_phase_1279
release_envelope_not_produced_phase_1279
genesis_atlas_mutation_not_authorized_phase_1279
public_rc_remains_blocked_after_phase_1279
```

Roadmap impact:

- Phase 1279 binds the existing Phase 1213 release artifact manifest schema,
  Phase 1213 distribution checklist, Phase 1255 public-source allowlist export
  procedure, Phase 1271 ATLAS-G-006 graph reachability pass, and Phase 1278
  Fix1 CDL-087 ratification into a single prepublication inventory.
- The source allowlist procedure remains defined but not executed; no clean
  public repository export, source publication, public package publication, or
  public release artifact production is authorized.
- Release keys, release envelopes, Genesis Atlas mutation/regeneration/signing,
  and v0.2 signing remain unauthorized.
- Counsel/IP/publication gates remain open for license instruments, CLA or
  no-external-contributor policy, trademark/fork labeling, patent/publication
  review, reviewed source allowlist manifest, and explicit publication
  authorization.
- Public RC remains blocked by public sidecar/projection serving authorization,
  TransportPrincipal public-path activation, Rust M-5/public-P2P
  hostile-network hardening, counsel/IP/publication authorization, v0.2 signing
  authorization, source publication/release artifact authorization, and final
  public claimability API/verifier authority.

Public RC remains blocked after Phase 1279:

```text
public_rc_remains_blocked_after_phase_1279
public_rc_remains_blocked_after_phase_1278_fix1
public_rc_remains_blocked_after_phase_1278
public_rc_remains_blocked_after_phase_1277
```

## 26. Phase 1280 Window 1273-1280 Closure Addendum

Phase 1280 closes Window 1273-1280:

```text
window_1273_1280_closed_phase_1280
window_1273_1280_closure_gate_verdict=pass
phase_1280_window_1273_1280_closure_complete
window_1281_plus_sequence_lock_required_before_next_phase_assignment
public_rc_remains_blocked_after_phase_1280
```

Roadmap impact:

- Window 1273-1280 is closed with a scoped pass verdict for sequence-lock,
  local claimability/conversion-sweeper work, proof binding, CDL-087
  ratification, public-path preflight helpers, release prepublication
  inventory, and handoff coherence.
- CDL-087 remains ratified from Phase 1278 Fix1, but public fetch serving,
  public sidecar/projection serving, public P2P exposure, CDL-088, and public
  RC remain separately gated.
- Claimability remains local-only after Phases 1274-1275; public claimability
  API/verifier authority remains open.
- Release publication remains blocked after Phase 1279 inventory; no source
  export, public repository publication, public package publication, release
  artifact production, release keys, release envelopes, Genesis Atlas mutation,
  or v0.2 signing is authorized.
- A Window 1281+ sequence lock is required before assigning the next phase.
- A capsule refresh is recommended because v5.50 is still the latest published
  capsule but is stale on CDL-087 ratification and this window closure.

Public RC remains blocked after Phase 1280:

```text
public_rc_remains_blocked_after_phase_1280
public_rc_remains_blocked_after_phase_1279
public_rc_remains_blocked_after_phase_1278_fix1
```

## 27. Phase 1280 Fix1 Hypergraph/Laplacian Planning Hardening Addendum

Phase 1280 Fix1 records a docs-only hardening pass after the Window 1273-1280
closure:

```text
phase_1280_fix1_hypergraph_laplacian_docs_hardened
h_series_020_plus_registered_phase_1280_fix1
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
public_rc_candidate_standard_preserved_phase_1280_fix1
```

The phase fixes stale hypergraph/Laplacian/ATLAS-G/DTE planning records and
registers H-020 through H-028 plus IP-001 through IP-006. It does not file any
patent application, publish any paper, authorize public source publication,
produce release artifacts, generate release keys/envelopes, mutate Genesis,
sign v0.2, open or mutate any CDL row, activate public fetch serving, activate
public sidecar/projection serving, activate public claimability, mint ECU,
settle ILC, or make a public-RC claim.

Public RC remains blocked after Phase 1280 Fix1:

```text
public_rc_remains_blocked_after_phase_1280_fix1
```

## 30. Phase 1284 Public Claimability Verifier/API Boundary Preflight Addendum

Phase 1284 records the sensitive public-claimability verifier/API boundary
preflight after explicit `GO Phase 1284`:

```text
public_claimability_verifier_api_boundary_preflight_phase_1284.v0.1
claimability_api_public_serving_not_enabled_phase_1284
claimability_verifier_authority_not_activated_phase_1284
wallet_withdrawal_transfer_spend_still_blocked_phase_1284
public_rc_exclude_internal_helper_required_phase_1284
public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api
phase_1285_transport_principal_public_path_activation_preflight_next
public_rc_remains_blocked_after_phase_1284
```

Roadmap impact:

- Phase 1284 closes only the verifier/API boundary preflight record. It does
  not activate a public verifier service, public or non-loopback claimability
  API, public claim endpoint, HTTP route, socket listener, wallet withdrawal,
  wallet transfer, wallet spend, ECU minting, ILC settlement, release artifact,
  Genesis mutation, v0.2 signing, CDL mutation, CDL-088 opening, public-RC
  claim, or public launch claim.
- No new runtime helper was introduced. The existing Phase 1274 and Phase 1275
  helpers remain internal `PUBLIC_RC_EXCLUDE` scaffolds until a later explicit
  public-RC allowlist review promotes or replaces them.
- The future public verifier surface still needs a public-safe presentation
  schema, privacy filtering, public claim nullifier or claim-registry semantics,
  TransportPrincipal binding before non-loopback serving, hostile-network
  hardening, and release allowlist promotion.
- The next executable public-path slice is Phase 1285, a sensitive
  TransportPrincipal public-path activation preflight.

Public RC remains blocked after Phase 1284 by TransportPrincipal public-path
activation, sidecar public projection privacy/serving preflight, release
publication and v0.2 signing authorization, counsel/IP/public-release
authority, source/release artifact authority, final public claimability
API/verifier authority, wallet withdrawal/transfer/spend semantics, ECU
minting, and ILC settlement:

```text
public_rc_remains_blocked_after_phase_1284
public_rc_remains_blocked_after_phase_1283
public_rc_remains_blocked_after_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282
public_rc_remains_blocked_after_phase_1280_fix1
```

## 28. Phase 1282 Fix1 Claimability Runtime Audit Hardening Addendum

Phase 1282 Fix1 records a deterministic implementation-audit hardening pass over
the local CDL-048 conversion-sweeper helper and local claimability proof-binding
helper:

```text
phase_1282_fix1_claimability_runtime_audit_hardening
claimability_conversion_receipt_semantics_hardened_phase_1282_fix1
settled_runtime_root_domain_separation_hardened_phase_1282_fix1
balance_receipt_decimal_boundary_hardened_phase_1282_fix1
cdl048_conversion_sweeper_public_rc_exclude_marked_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282_fix1
```

Roadmap impact:

- The Phase 1274 sweeper helper is now marked `PUBLIC_RC_EXCLUDE` and remains an
  internal phase helper, not a public RC launch surface.
- Conversion receipts now fail closed unless root refs are full prefixed
  lowercase SHA-256 refs, deadline math matches CDL-048, conversion epoch is
  inside the issue/deadline window, settled epoch matches conversion epoch,
  conversion transition is exact, conversion key derivation matches the receipt
  binding material, required tokens are present, and activation flags are false.
- Claimability proof binding now rejects `wallet_state_sha256:` in the
  settled-runtime-root position, preserving settled-runtime vs wallet-state root
  domain separation.
- Latest balance receipt economic fields must be finite Decimal strings, with
  non-negative `balance_after_ilc`.
- Public claimability remains blocked; no public API, wallet withdrawal, wallet
  transfer, wallet spend, ECU minting, ILC settlement, publication, release
  artifact, Genesis mutation, v0.2 signing, CDL mutation, or public-RC claim is
  authorized.

Public RC remains blocked after Phase 1282 Fix1:

```text
public_rc_remains_blocked_after_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282
public_rc_remains_blocked_after_phase_1280_fix1
```

## 29. Phase 1283 Public Claimability Authority Decision Preflight Addendum

Phase 1283 records the sensitive public-claimability authority decision
preflight after explicit `GO Phase 1283`:

```text
public_claimability_authority_decision_preflight_phase_1283.v0.1
public_claimability_activation_requires_explicit_human_authorization_phase_1283
public_claimability_activation_not_authorized_by_default_phase_1283
wallet_withdrawal_transfer_spend_still_blocked_phase_1283
claimability_human_question_escalation_required_phase_1283
public_claimability_authority_verdict_phase_1283=no_activation_no_public_api
phase_1284_claimability_verifier_api_boundary_preflight_next
public_rc_remains_blocked_after_phase_1283
```

## 31. Phase 1285 TransportPrincipal Public-Path Activation Preflight Addendum

Phase 1285 records the sensitive TransportPrincipal public-path activation
preflight under explicit `GO Phase 1285-1288` and the user's preflight-only
stance:

```text
transport_principal_public_path_activation_preflight_phase_1285.v0.1
transport_principal_public_p2p_not_activated_phase_1285
public_fetch_serving_not_enabled_phase_1285
requester_id_fallback_still_forbidden_phase_1285
transport_principal_lifecycle_revocation_replay_required_phase_1285
transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation
transport_principal_public_path_authority_not_activated_phase_1285
phase_1286_sidecar_public_projection_privacy_serving_preflight_next
public_rc_remains_blocked_after_phase_1285
```

## 35. Phase 1288 Fix1 Runtime Deep Audit Hardening Addendum

Phase 1288 Fix1 records a deep deterministic implementation audit and hardening
pass over the runtime/helper surfaces introduced or relied on by Phases 1274,
1275, 1277, 1278, and 1282 Fix1:

```text
phase_1288_fix1_runtime_deep_audit_hardening
canonical_payload_float_rejection_hardened_phase_1288_fix1
untrusted_payload_cycle_depth_bounds_hardened_phase_1288_fix1
public_path_preflight_key_shape_hardened_phase_1288_fix1
public_rc_remains_blocked_after_phase_1288_fix1
```

Roadmap impact:

- Local CDL-048 conversion canonical payloads and claimability proof-binding
  canonical payloads reject finite floats before canonical hashing/export.
- Local conversion/claimability canonical payload traversal and
  TransportPrincipal/sidecar public-path preflight validation now fail closed on
  recursive cycles, excessive traversal depth, excessive traversal node count,
  and non-string JSON object keys.
- `tools/check_sensitive_runtime_coding_taboos.py` now tracks the untrusted
  payload-bound contracts for these four helper surfaces.
- No public claimability, public verifier/API, TransportPrincipal public path,
  public sidecar/projection serving, source publication, release artifact,
  release key, release envelope, Genesis mutation/signing, CDL mutation,
  CDL-088 opening, wallet withdrawal/transfer/spend, ECU minting, ILC
  settlement, public RC claim, or v0.2 signing is authorized.

Public RC remains blocked after Phase 1288 Fix1:

```text
public_rc_remains_blocked_after_phase_1288_fix1
public_rc_remains_blocked_after_phase_1288
public_rc_remains_blocked_after_phase_1287
public_rc_remains_blocked_after_phase_1286
```

Phase 1285 does not activate public P2P, public fetch serving, non-loopback
sidecar/projection serving, public claimability, wallet withdrawal/transfer/
spend, ECU minting, ILC settlement, release publication, Genesis Atlas
mutation, v0.2 signing, CDL mutation, CDL-088 opening, or a public RC claim.

Public RC remains blocked after Phase 1285 by sidecar public projection
privacy/serving preflight, release publication and v0.2 signing authorization,
counsel/IP/publication authorization, source publication/release artifact
authorization, final public claimability API/verifier authority, actual
TransportPrincipal public-path activation authority, wallet
withdrawal/transfer/spend semantics, ECU minting, and ILC settlement.

## 32. Phase 1286 Sidecar Public Projection Privacy/Serving Preflight Addendum

Phase 1286 records the sensitive sidecar public projection privacy/serving
preflight under explicit `GO Phase 1285-1288` and the user's preflight-only
stance:

```text
sidecar_public_projection_privacy_serving_preflight_phase_1286.v0.1
sidecar_public_serving_not_enabled_phase_1286
non_loopback_bind_not_enabled_phase_1286
public_projection_endpoint_not_enabled_phase_1286
transport_principal_activation_required_before_public_projection_phase_1286
sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving
no_new_public_listener_phase_1286
peer_discovery_not_enabled_phase_1286
phase_1287_release_publication_signing_authorization_preflight_next
public_rc_remains_blocked_after_phase_1286
```

Phase 1286 does not activate public sidecar/projection serving, public
projection endpoint serving, non-loopback bind, wildcard bind, public host bind,
listener, peer discovery, public fetch serving, public P2P, TransportPrincipal
public-path activation, public claimability, wallet withdrawal/transfer/spend,
ECU minting, ILC settlement, release publication, Genesis Atlas mutation, v0.2
signing, CDL mutation, CDL-088 opening, or a public RC claim.

Public RC remains blocked after Phase 1286 by release publication and v0.2
signing authorization, counsel/IP/publication authorization, source
publication/release artifact authorization, final public claimability
API/verifier authority, actual TransportPrincipal public-path activation
authority, actual sidecar public projection serving authority, privacy
filtering/public-safe projection schema, wallet withdrawal/transfer/spend
semantics, ECU minting, and ILC settlement.

Roadmap impact:

- Phase 1286 closes only the sidecar public projection privacy/serving
  preflight record. It does not activate public sidecar/projection serving or
  create a listener, endpoint, non-loopback bind, wildcard bind, public host
  bind, or peer discovery surface.
- The Phase 1278 sidecar public-path helper remains `PUBLIC_RC_EXCLUDE`
  internal preflight scaffolding. Release allowlist review has not promoted it
  into a public RC package.
- Future public projection serving still requires explicit sidecar public
  serving authority, actual TransportPrincipal public-path activation,
  public-safe projection schema, field filtering, privacy review, abuse/rate
  limit controls, and hostile-network validation.
- At Phase 1286 close, the locked successor was Phase 1287, release
  publication and v0.2 signing authorization preflight.

Public RC remains blocked after Phase 1286 by release publication and v0.2
signing authorization, counsel/IP/publication authorization, source
publication/release artifact authorization, final public claimability
API/verifier authority, actual TransportPrincipal public-path activation
authority, actual sidecar public projection serving authority, privacy
filtering/public-safe projection schema, wallet withdrawal/transfer/spend
semantics, ECU minting, and ILC settlement:

```text
public_rc_remains_blocked_after_phase_1286
public_rc_remains_blocked_after_phase_1285
public_rc_remains_blocked_after_phase_1284
public_rc_remains_blocked_after_phase_1283
```

## 33. Phase 1287 Release Publication Signing Authorization Preflight Addendum

Phase 1287 records the sensitive release publication/signing authorization
preflight under explicit `GO Phase 1285-1288` and the user's preflight-only
stance:

```text
release_publication_signing_authorization_preflight_phase_1287.v0.1
public_repository_publication_not_authorized_phase_1287
release_artifact_production_not_authorized_phase_1287
source_allowlist_export_not_executed_phase_1287
release_keys_not_generated_phase_1287
release_envelope_not_produced_phase_1287
v0_2_signing_not_authorized_phase_1287
genesis_atlas_mutation_not_authorized_phase_1287
release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing
public_package_publication_not_authorized_phase_1287
public_rc_claim_not_authorized_phase_1287
genesis_atlas_signing_not_authorized_phase_1287
phase_1288_window_1281_1288_closure_gate_next
public_rc_remains_blocked_after_phase_1287
```

Phase 1287 does not execute source allowlist export, publish a public repository
or package, produce release artifacts, generate release keys, produce release
envelopes, mutate/regenerate/sign Genesis Atlas, sign v0.2, make a public RC
claim, open CDL-088, mutate the CDL register, or activate public runtime or
economic surfaces.

Roadmap impact:

- Phase 1287 closes only the release publication/signing authorization preflight
  record. It does not convert Phase 1255 allowlist procedure, Phase 1213
  manifest schema, Phase 1271 graph pass, or Phase 1279 inventory into release
  authority.
- Public RC remains blocked by final public claimability API/verifier
  authority, actual TransportPrincipal public-path activation authority, actual
  sidecar public projection serving authority, counsel/IP/publication
  authorization, source allowlist export execution, release artifact
  production, release keys, release envelopes, Genesis Atlas mutation/signing if
  needed, v0.2 signing authorization, wallet semantics, ECU minting, and ILC
  settlement.
- At Phase 1287 close, the locked successor was Phase 1288, Window 1281-1288
  closure gate, which closed the window honestly without making a public RC
  claim and without granting release or activation authority.

Public RC remains blocked after Phase 1287:

```text
public_rc_remains_blocked_after_phase_1287
public_rc_remains_blocked_after_phase_1286
public_rc_remains_blocked_after_phase_1285
public_rc_remains_blocked_after_phase_1284
```

## 34. Phase 1288 Window 1281-1288 Closure Addendum

Phase 1288 closes Window 1281-1288 under explicit `GO Phase 1285-1288`:

```text
window_1281_1288_closed_phase_1288
window_1281_1288_closure_gate_verdict=pass
phase_1288_window_1281_1288_closure_complete
window_1289_plus_sequence_lock_required_before_next_phase_assignment
public_rc_remains_blocked_after_phase_1288
```

The closure pass is a coherence and handoff verdict only. It does not authorize
public RC, public launch, public claimability, public verifier/API serving,
TransportPrincipal public-path activation, public sidecar/projection serving,
source publication, release artifacts, release keys, release envelopes, Genesis
Atlas mutation/signing, CDL mutation, CDL-088 opening, wallet economics, ECU
minting, ILC settlement, or v0.2 signing.

Roadmap impact:

- Window 1281-1288 is closed/pass through Phase 1288.
- Window 1289+ sequence lock is required before assigning any next phase.
- Public RC remains blocked by final public claimability API/verifier authority,
  actual TransportPrincipal public-path activation authority, actual sidecar
  public projection serving authority, privacy filtering/public-safe projection
  schema, counsel/IP/publication authorization, source allowlist export
  execution, release artifact production, release keys, release envelopes,
  Genesis Atlas mutation/regeneration/signing if needed, v0.2 signing
  authorization, wallet semantics, ECU minting, and ILC settlement.

Public RC remains blocked after Phase 1288:

```text
public_rc_remains_blocked_after_phase_1288
public_rc_remains_blocked_after_phase_1287
public_rc_remains_blocked_after_phase_1286
public_rc_remains_blocked_after_phase_1285
```

---

## 36. Phase 1288 Fix2 Window 1289-1296 Guidance Addendum

Phase 1288 Fix2 records the planning-only guidance and prompt-draft package for
candidate Window 1289-1296:

This addendum is historical. Phase 1289 supersedes its active routing with the
Window 1289-1302 sequence lock; later addenda control the active Phase 1293
scope.

```text
phase_1288_fix2_window_1289_1296_guidance_drafted
window_1289_1296_candidate_phase_grouping_recorded_after_phase_1288_fix1
window_1289_1296_not_open_until_sequence_lock
phase_1289_window_1289_1296_sequence_lock_required
```

Candidate routing:

| Candidate phase | Candidate scope | Default authority stance |
|-----------------|-----------------|--------------------------|
| 1289 | Window 1289-1296 sequence lock | Sensitive; requires explicit GO. |
| 1290 | Context Capsule v5.52 frontier refresh | Docs/canon refresh only. |
| 1291 | Public claimability verifier contract preflight | Sensitive; no public API or activation by default. |
| 1292 | Claimability package-profile allowlist rehearsal | Sensitive; no source export or package publication. |
| 1293 | TransportPrincipal lifecycle activation-blocker preflight | Sensitive; no public P2P or fetch serving. |
| 1294 | Sidecar public-safe projection schema preflight | Sensitive; no listener, non-loopback bind, endpoint, or peer discovery. |
| 1295 | Release allowlist/artifact/Genesis readiness preflight | Sensitive; no publication, artifacts, keys, envelopes, Genesis signing, or v0.2 signing. |
| 1296 | Window 1289-1296 closure gate | Sensitive; closes honestly or carries blockers forward. |

Roadmap impact:

- Window 1289-1296 is not open until a future Phase 1289 sequence lock.
- The drafted prompt package does not authorize public RC, public activation,
  source export, source publication, package publication, release artifact
  production, release keys, release envelopes, Genesis mutation/signing, CDL
  mutation, CDL-088 opening, wallet economics, ECU minting, ILC settlement, or
  v0.2 signing.
- Public RC remains blocked.

```text
public_rc_remains_blocked_after_phase_1288_fix2
```

---

## 37. Phase 1289 Window 1289-1302 Sequence Lock Addendum

Phase 1289 opens the next active planning window after explicit `GO Phase 1289`
and expands the Phase 1288 Fix2 draft from Window 1289-1296 to Window 1289-1302:

```text
window_1289_1302_sequence_lock_committed
window_1289_1302_sequence_lock_verdict=pass
phase_1290_context_capsule_v5_52_refresh_next
window_1289_1302_no_public_rc_or_public_activation
window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289
```

Roadmap impact:

- Phase 1290 is non-sensitive context-capsule refresh and may proceed under the
  user's continue-through-non-sensitive instruction.
- Phase 1291 is the next sensitive gate and requires explicit `GO Phase 1291`.
- Public RC remains blocked by public claimability verifier/API authority,
  TransportPrincipal public-path activation authority, sidecar public projection
  serving authority, release publication/artifact/key/envelope authority,
  Genesis/v0.2 signing authority, wallet/ECU/ILC activation, and IP/publication
  clearance.

---

## 38. Phase 1290 Context Capsule v5.52 Addendum

Phase 1290 publishes Context Capsule v5.52 and updates the roadmap frontier to
Window 1289-1302 OPEN through Phase 1290:

```text
context_capsule_v5_52_frontier_refresh_phase_1290.v0.1
capsule_v5_52_supersedes_v5_51
window_1289_1302_sequence_lock_reflected_in_capsule_phase_1290
public_rc_blocker_map_refreshed_phase_1290
public_rc_remains_blocked_after_phase_1290
```

Roadmap impact:

- Capsule v5.52 supersedes v5.51 as the session-start capsule.
- Phase 1291 is the next phase and remains sensitive.
- No public RC blocker is closed by Phase 1290; the blocker map is refreshed
  and carried forward for explicit future phases.

---

## 39. Phase 1291 Public Claimability Verifier Contract Preflight Addendum

Phase 1291 records the public claimability verifier contract boundary after
explicit `GO Phase 1291`:

```text
public_claimability_verifier_contract_preflight_phase_1291.v0.1
public_claimability_activation_not_authorized_by_default_phase_1291
claimability_verifier_public_api_not_enabled_phase_1291
wallet_withdrawal_transfer_spend_still_blocked_phase_1291
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
claimability_contract_no_runtime_helper_added_phase_1291
phase_1292_verifier_negative_path_corpus_package_boundary_next
public_rc_remains_blocked_after_phase_1291
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1291.
- Phase 1291 defines future `ClaimabilityVerifierInput` and
  `ClaimabilityVerifierDecision` envelopes, mandatory denial conditions, and a
  public-safe disclosure carry-forward.
- Phase 1291 adds no runtime helper, public verifier service, public claim
  endpoint, HTTP route, FastAPI route, socket listener, non-loopback bind,
  wildcard bind, public host bind, peer discovery, wallet withdrawal, wallet
  transfer, wallet spend, ECU minting, or ILC settlement.
- Phase 1292 is the next sensitive phase and requires explicit `GO Phase 1292`.
- Public RC remains blocked by final public claimability API/verifier
  authority, negative-path corpus and package-profile boundary, public-safe
  disclosure schema, TransportPrincipal public-path activation authority,
  sidecar public projection serving authority, release publication/artifact/key
  and envelope authority, Genesis/v0.2 signing authority, wallet/ECU/ILC
  activation, CDL-088, and IP/publication clearance.

---

## 40. Phase 1292 Verifier Negative-Path And Package Boundary Addendum

Phase 1292 records the verifier negative-path corpus and claimability
package-profile boundary rehearsal after explicit `GO Phase 1292`:

```text
claimability_package_profile_allowlist_rehearsal_phase_1292.v0.1
source_allowlist_export_not_executed_phase_1292
public_package_publication_not_authorized_phase_1292
public_rc_exclude_helpers_preserved_phase_1292
verifier_negative_path_corpus_recorded_phase_1292
claimability_package_profile_boundary_verdict_phase_1292=pass_import_boundary_publication_blocked
ilc_logic_network_import_boundary_repaired_phase_1292
package_profile_ci_artifacts_refreshed_phase_1292
phase_1293_public_rc_exclude_helper_promotion_removal_register_next
public_rc_remains_blocked_after_phase_1292
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1292.
- Phase 1292 repairs the pure `ilc_logic` import-boundary regression where
  `ilc_core/graph/sidecar_public_path_preflight.py` imported
  `ilc_core.network`.
- The deterministic package-profile CI audit now passes for
  `openclaw_skill_local` and `openclaw_skill_claimable`, but that pass is not
  source-publication, package-publication, release-artifact, or public-RC
  authority.
- Phase 1292 records verifier denial cases for forged receipts, wrong roots,
  stale roots, replay, missing nullifier/duplicate-claim policy, exact-numeric
  violations, traversal bounds, public-safe disclosure gaps, and accidental
  `PUBLIC_RC_EXCLUDE` inclusion.
- Phase 1293 is the next sensitive phase and requires explicit `GO Phase 1293`.
- Public RC remains blocked by helper promotion/removal review, final public
  claimability API/verifier authority, public-safe disclosure schema,
  TransportPrincipal public-path activation authority, sidecar public projection
  serving authority, release publication/artifact/key and envelope authority,
  Genesis/v0.2 signing authority, wallet/ECU/ILC activation, CDL-088, and
  IP/publication clearance.

---

## 41. Phase 1293 PUBLIC_RC_EXCLUDE Helper Register Addendum

Historical Phase 1292 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1292
```

Phase 1293 records the `PUBLIC_RC_EXCLUDE` helper promotion/removal register
after explicit `GO Phase 1293`:

```text
public_rc_exclude_helper_promotion_removal_register_phase_1293.v0.1
public_rc_exclude_helper_register_verdict_phase_1293=all_current_helpers_keep_internal_no_promotion
public_rc_exclude_helpers_keep_internal_phase_1293
public_rc_exclude_helper_promotion_not_authorized_phase_1293
public_rc_exclude_helper_removal_not_authorized_phase_1293
public_rc_exclude_helper_replacement_required_before_public_export_phase_1293
source_allowlist_export_not_executed_phase_1293
public_package_publication_not_authorized_phase_1293
public_rc_remains_blocked_after_phase_1293
phase_1294_claimability_package_allowlist_rehearsal_next
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1293.
- The current runtime helpers in `ilc_core/ledger/` and `ilc_core/network/d2d/`
  plus the sidecar public-path helper remain internal and keep their
  `PUBLIC_RC_EXCLUDE` markers.
- The stale Phase 1288 Fix2 Phase 1293 prompt body is corrected to the active
  1289-1302 helper-register scope; the old TransportPrincipal Phase 1293 row is
  historical only.
- No helper promotion, marker removal, source allowlist export execution,
  public repository publication, public package publication, release artifact,
  release-key generation, release envelope, public claimability API, public
  verifier service, public P2P/fetch/sidecar serving, Genesis signing, v0.2
  signing, CDL mutation, CDL-088 opening, wallet/ECU/ILC activation, IP filing,
  or paper publication is authorized.
- Phase 1294 is the next sensitive phase and requires explicit `GO Phase 1294`.
- Public RC remains blocked by final public claimability API/verifier
  authority, public-safe helper replacement or later explicit helper promotion
  prerequisites, public-safe disclosure schema, TransportPrincipal public-path
  activation authority, sidecar public projection serving authority, release
  publication/artifact/key and envelope authority, Genesis/v0.2 signing
  authority, wallet/ECU/ILC activation, CDL-088, and IP/publication clearance.

---

## 44. Phase 1296 Hostile-Network Admission Ban Rate Privacy Plan Addendum

Historical Phase 1295 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1295
Phase 1296 is the next sensitive phase
```

Phase 1296 records the hostile-network admission, ban, rate-limit, and privacy
plan after explicit `GO Phase 1296`:

```text
hostile_network_admission_ban_rate_privacy_plan_phase_1296.v0.1
hostile_network_plan_verdict_phase_1296=plan_recorded_no_activation
transport_principal_admission_policy_not_activated_phase_1296
transport_principal_ban_registry_not_activated_phase_1296
transport_principal_rate_limit_state_not_activated_phase_1296
transport_principal_privacy_policy_not_activated_phase_1296
requester_id_client_ip_agentid_fallback_still_forbidden_phase_1296
werner_overlay_not_activated_phase_1296
public_p2p_not_activated_phase_1296
public_fetch_serving_not_enabled_phase_1296
public_sidecar_projection_serving_not_enabled_phase_1296
public_rc_remains_blocked_after_phase_1296
phase_1297_sidecar_public_safe_projection_schema_next
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1296.
- Phase 1296 records admission, ban, rate-limit, privacy, and Werner interaction
  requirements only; it activates no admission policy, ban registry, rate-limit
  state, privacy policy, or Werner overlay.
- Phase 1296 keeps `requester_id`, `client_ip`, AgentID, agent id, harness
  identity, OpenClaw identity, and Tailscale identity forbidden as default
  public-path admission/rate/ban keys.
- Phase 1296 also refreshes the active Window 1289-1302 Phase Prompt drafts so
  they cite the 1289-1302 lock/guidance rather than the superseded 1289-1296
  draft window or stale Phase 1296 closure boundary.
- Phase 1296 does not activate TransportPrincipal public path, public credential
  issuer authority, public revocation registry, public replay cache, public
  P2P, public fetch, public sidecar/projection serving, helper promotion,
  marker removal, source export, repository or package publication, release
  artifacts, release keys, release envelopes, Genesis mutation/signing, v0.2
  signing, CDL mutation, CDL-088, IP filing, paper publication, or
  wallet/ECU/ILC activation.
- Phase 1297 is the next sensitive phase and requires explicit `GO Phase 1297`.
- Public RC remains blocked by final public claimability API/verifier authority,
  public-safe helper replacement or later explicit helper promotion
  prerequisites, public-safe disclosure schema, replay/nullifier and
  duplicate-claim registry policy, actual TransportPrincipal public-path
  activation authority including post-ratification CDL-087 helper replacement,
  lifecycle policy, revocation registry, replay cache, admission policy, ban
  registry, rate-limit state, privacy policy, sidecar public projection serving
  authority, release publication/artifact/key and envelope authority,
  Genesis/v0.2 signing authority, wallet/ECU/ILC activation, CDL-088, and
  IP/publication clearance.

---

## 43. Phase 1295 TransportPrincipal Lifecycle Revocation Replay Preflight Addendum

Historical Phase 1294 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1294
Phase 1295 is the next sensitive phase
```

Phase 1295 records the TransportPrincipal lifecycle, revocation, and replay
preflight after explicit `GO Phase 1295`:

```text
transport_principal_lifecycle_revocation_replay_preflight_phase_1295.v0.1
transport_principal_lifecycle_revocation_replay_verdict_phase_1295=preflight_only_stale_helper_not_promotable
cdl087_ratified_but_phase_1277_helper_still_pre_ratification_gate_phase_1295
transport_principal_public_path_helper_not_promoted_phase_1295
transport_principal_lifecycle_policy_not_activated_phase_1295
transport_principal_revocation_registry_not_activated_phase_1295
transport_principal_replay_cache_not_activated_phase_1295
requester_id_fallback_still_forbidden_phase_1295
public_p2p_not_activated_phase_1295
public_fetch_serving_not_enabled_phase_1295
public_rc_remains_blocked_after_phase_1295
phase_1296_hostile_network_admission_ban_rate_privacy_plan_next
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1295.
- Phase 1295 confirms the current TransportPrincipal helper remains internal and
  fail-closed, but is not directly promotable because CDL-087 is now ratified
  while `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
  still carries the pre-ratification `cdl087_not_ratified_by_phase_1277` false
  gate.
- Phase 1295 records transport lifecycle/revocation/replay classification only.
  It does not activate TransportPrincipal public path, public credential issuer
  authority, credential lifecycle policy, public revocation registry, replay
  cache, public P2P, public fetch, public sidecar/projection serving, helper
  promotion, marker removal, source export, repository or package publication,
  release artifacts, release keys, release envelopes, Genesis mutation/signing,
  v0.2 signing, CDL mutation, CDL-088, IP filing, paper publication, or
  wallet/ECU/ILC activation.
- Phase 1296 is the next sensitive phase and requires explicit `GO Phase 1296`.
- Public RC remains blocked by final public claimability API/verifier
  authority, public-safe helper replacement or later explicit helper promotion
  prerequisites, public-safe disclosure schema, TransportPrincipal public-path
  activation authority including post-ratification CDL-087 helper replacement,
  lifecycle policy, revocation registry, replay cache, admission, ban,
  rate-limit, and privacy controls, sidecar public projection serving
  authority, release publication/artifact/key and envelope authority,
  Genesis/v0.2 signing authority, wallet/ECU/ILC activation, CDL-088, and
  IP/publication clearance.

---

## 42. Phase 1294 Claimability Package Allowlist Rehearsal Addendum

Historical Phase 1293 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1293
Phase 1294 is the next sensitive phase
```

Phase 1294 records the claimability package allowlist rehearsal after explicit
`GO Phase 1294`:

```text
claimability_package_allowlist_rehearsal_phase_1294.v0.1
claimability_package_allowlist_verdict_phase_1294=rehearsal_pass_export_blocked
openclaw_skill_claimable_allowlist_rehearsed_phase_1294
public_rc_exclude_helpers_excluded_from_export_phase_1294
claimability_package_manifest_not_materialized_phase_1294
source_allowlist_export_not_executed_phase_1294
public_repository_publication_not_authorized_phase_1294
public_package_publication_not_authorized_phase_1294
public_claimability_activation_not_authorized_phase_1294
public_rc_remains_blocked_after_phase_1294
phase_1295_transport_principal_lifecycle_revocation_replay_preflight_next
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1294.
- The `openclaw_skill_claimable` package-profile CI pass is preserved, but the
  raw measured profile is not directly publishable because the measured
  `ilc_logic` surface includes `ilc_core/graph/sidecar_public_path_preflight.py`,
  which remains `PUBLIC_RC_EXCLUDE`.
- Phase 1294 records allowlist classification only. It does not materialize an
  export manifest, execute source export, publish a repository or package,
  promote helpers, remove markers, activate public claimability, activate a
  public verifier service, produce release artifacts, generate release keys,
  produce release envelopes, mutate Genesis, sign v0.2, mutate CDLs, open
  CDL-088, file IP, publish papers, or authorize wallet/ECU/ILC activation.
- Phase 1295 is the next sensitive phase and requires explicit `GO Phase 1295`.
- Public RC remains blocked by final public claimability API/verifier
  authority, public-safe helper replacement or later explicit helper promotion
  prerequisites, public-safe disclosure schema, TransportPrincipal public-path
  activation authority, sidecar public projection serving authority, release
  publication/artifact/key and envelope authority, Genesis/v0.2 signing
  authority, wallet/ECU/ILC activation, CDL-088, and IP/publication clearance.

---

## 45. Phase 1297 Sidecar Public-Safe Projection Schema Addendum

Historical Phase 1296 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1296
Phase 1297 is the next sensitive phase
```

Phase 1297 records the sidecar public-safe projection schema after explicit
`GO Phase 1297`:

```text
sidecar_public_safe_projection_schema_phase_1297.v0.1
sidecar_public_safe_projection_schema_verdict_phase_1297=schema_recorded_no_serving
privacy_filtering_contract_recorded_phase_1297
sidecar_public_projection_fields_not_served_phase_1297
public_sidecar_projection_serving_not_enabled_phase_1297
public_rc_remains_blocked_after_phase_1297
phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_next
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1297.
- Phase 1297 records a deny-by-default public-safe projection envelope, field
  classification, and privacy filtering contract only.
- Phase 1297 does not implement a public filter, serve projection fields, add a
  public endpoint, add a listener, bind non-loopback, enable peer discovery, or
  promote any `PUBLIC_RC_EXCLUDE` helper.
- The existing sidecar query runtime remains local/read-only and bounded; the
  existing sidecar public-path preflight helper remains `PUBLIC_RC_EXCLUDE` and
  records no listener, bind, or serving surface.
- Phase 1298 is the next sensitive phase and requires explicit `GO Phase 1298`.
- Public RC remains blocked by final public claimability API/verifier
  authority, privacy filter implementation/review, replay/nullifier and
  duplicate-claim registry policy, actual TransportPrincipal public-path
  activation authority, sidecar public projection serving authority, sidecar
  bind/listener/peer-discovery authority, release publication/artifact/key and
  envelope authority, Genesis/v0.2 signing authority, wallet/ECU/ILC
  activation, CDL-088, and IP/publication clearance.

---

## 47. Forward Phase Windows 1303-1342 Packaging and Signing Plan Addendum

The forward plan
`docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md`
and architecture gates
`docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md` and
`docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` record
the best current candidate sequence for the next three post-1302 windows.
The Confidential Coordination Sidecar Suite routing is recorded in
`docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md`:

```text
forward_phase_windows_1303_1342_packaging_and_signing_plan_recorded
public_rc_exclude_helper_stripping_routed_to_phase_1308_1319_1333
source_allowlist_export_materialization_must_fail_on_public_rc_exclude_markers
public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution
public_rc_package_export_must_be_public_tree_clean_not_flag_flip
release_artifact_packet_must_reference_clean_export_gate
public_rc_exclude_absence_is_not_allowlist_clearance
legacy_untagged_docs_default_review_required_before_public_export
ilc_graph_native_sidecar_suite_architecture_recorded
graph_native_sidecar_creation_routed_to_forward_windows_1303_1342
essential_openclaw_rc_sidecars_truth_projection_claimability_bridge
openclaw_nemoclaw_are_hosts_not_protocol_substrates
sidecar_suite_public_serving_remains_blocked_until_explicit_authority
confidential_coordination_sidecar_suite_forward_plan_recorded
confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329
confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only
confidential_coordination_not_public_rc_blocker_without_explicit_selection
```

Roadmap impact:

- The durable plan is implementation first, deterministic dry-run
  materialization second, and explicit export/release/signing gate third.
- Phase 1308 is the implementation-hardening planning point for
  `PUBLIC_RC_EXCLUDE` helper replacement, stripping, or explicit carry-forward.
- Phase 1307 through Phase 1314 are the implementation-hardening planning points
  for the essential graph-native sidecar suite: registry/manifest, offline
  claimability verifier, truth primitive submission boundary, TransportPrincipal
  admission substrate, local graph/memory projection, and default-off public
  fetch/P2P readiness, and wallet-facing value-action semantics preflight.
- Phase 1322 and Phase 1323 are the private deployment and OpenClaw/NemoClaw
  dry-run points for the essential sidecar suite; successful private
  DigitalOcean/OpenClaw tests do not authorize public sidecar serving.
- Phase 1324 through Phase 1328 are now the preferred planning lane for the
  Confidential Coordination Sidecar Suite after the essential sidecar suite is
  testable: private/gated shard sidecar, capability/membership sidecar, sealed
  sender delivery sidecar, gossip announce/pull with jitter/cover policy, and a
  private OpenClaw/NemoClaw droplet dry run.
- Phase 1329 is the closure point for deciding whether confidential
  coordination remains a private/post-RC lane, becomes a selected public-RC
  blocker, or moves to a dedicated later window.
- Phase 1319 is the deterministic source allowlist export rehearsal; the
  materialized dry-run tree must contain zero `PUBLIC_RC_EXCLUDE` markers and no
  imports of stripped helper modules.
- Phase 1333 is the final source allowlist export execution gate, if later
  explicitly authorized. It must fail closed if marked helpers, imports of
  stripped helpers, or missing marker/import-scan evidence remain.
- Internal helper flags must not be flipped from false to true as a publication
  shortcut. Public RC packaging must replace the helper with public-safe code,
  strip it from the public export, or carry the affected profile forward as
  blocked.
- `PUBLIC_RC_EXCLUDE` is a deny marker, not allowlist clearance. Older unmarked
  docs, research notes, roadmap fragments, whitepaper drafts, and phase
  walkthroughs remain excluded or review-required until an explicit manifest
  lists them with legacy-untagged review evidence.
- Release artifact packets must reference the clean export evidence; release
  artifacts must not be used to hide private helper scaffolds or convert a false
  internal helper flag into a public claim.
- Confidential coordination is not a first-public-RC blocker by default and
  does not become a public confidential messaging claim without explicit Phase
  1337 and Phase 1341 authority.
- This addendum does not open Window 1303+, execute export, publish source or
  packages, produce release artifacts, generate keys/envelopes, mutate or sign
  Genesis, sign v0.2, activate public paths, or authorize economics.

---

## 48. Confidential Coordination Sidecar Suite Forward Plan Addendum

The forward plan
`docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md`
records the graph-native confidential coordination lane:

```text
confidential_coordination_sidecar_suite_forward_plan_recorded
confidential_coordination_sidecar_suite_graph_native_not_signal_clone
confidential_coordination_sidecar_suite_not_public_rc_blocker_by_default
confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329
confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only
confidential_coordination_public_claim_requires_phase_1337_1341_authority
```

Roadmap impact:

- Phase 1297 and Phase 1298 are related prerequisites only; they do not
  implement confidential coordination or enable serving.
- Phase 1307 should add the `confidential_coordination_local_preview` profile
  to the sidecar registry/manifest design with private wiring modes and
  explicit non-claims.
- Phase 1311 and Phase 1312 should ensure projection support for private/gated
  shard headers and encrypted coordination-node references without leaking
  plaintext, membership, route history, or sealed payloads.
- Phase 1324 is CCSS-001 private/gated shard sidecar contract.
- Phase 1325 is CCSS-002 capability, membership, grant, revocation, and
  optional ZK-membership proof interface boundary.
- Phase 1326 is CCSS-003 sealed sender local delivery sidecar boundary using
  H-013/H-015 seams and no-public-P2P defaults.
- Phase 1327 is CCSS-004 gossip announce/pull, jitter, batching, cover-policy,
  and traffic-analysis negative tests with no anonymity-guarantee claim.
- Phase 1328 is CCSS-005 private OpenClaw/NemoClaw or equivalent DigitalOcean
  droplet dry run over loopback, Tailscale, or other private wiring.
- Phase 1329 decides whether the suite remains post-RC/private, becomes a
  selected public-RC blocker, or moves to a later dedicated window.
- Phase 1337 must explicitly activate or exclude any public confidential
  coordination serving claim; private droplet success is not public authority.
- Phase 1341 must not imply a public confidential messaging product unless
  Phase 1337 explicitly selected and passed that scope.
- This addendum does not open Window 1303+, activate public serving, publish
  source, produce release artifacts, generate keys/envelopes, mutate/sign
  Genesis, sign v0.2, or authorize wallet/ECU/ILC economics.

---

## 46. Phase 1298 Sidecar Bind Listener Peer Discovery Authority Preflight Addendum

Historical Phase 1297 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1297
Phase 1298 is the next sensitive phase
```

Phase 1298 records the sidecar bind, listener, and peer-discovery authority
preflight after explicit `GO Phase 1298 and any subsequent non-sensitive
phases, in order`:

```text
sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1
sidecar_bind_listener_peer_discovery_verdict_phase_1298=preflight_only_no_public_serving
non_loopback_bind_not_enabled_phase_1298
public_listener_not_enabled_phase_1298
peer_discovery_not_enabled_phase_1298
public_sidecar_projection_serving_not_enabled_phase_1298
public_rc_remains_blocked_after_phase_1298
phase_1299_release_allowlist_artifact_genesis_readiness_preflight_next
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1298.
- Window 1289-1302 OPEN through Phase 1298.
- Phase 1298 records a preflight-only authority table for local in-process
  sidecar reads, loopback-only historical boundaries, non-loopback bind,
  wildcard bind, public host bind, public listener, socket listener, HTTP route,
  peer discovery, public sidecar/projection serving, public P2P, and public
  fetch serving.
- Phase 1298 does not enable non-loopback bind, wildcard bind, public host
  bind, public listener, socket listener, HTTP route, peer discovery, public
  sidecar/projection serving, public projection endpoint serving, public P2P,
  or public fetch serving.
- The existing sidecar public-path preflight helper remains `PUBLIC_RC_EXCLUDE`
  and records no listener, bind, or serving surface. Local in-process sidecar
  reads remain the only active sidecar path.
- Phase 1299 is the next sensitive phase and requires explicit `GO Phase 1299`.
- Public RC remains blocked by final public claimability API/verifier
  authority, privacy filter implementation/review, replay/nullifier and
  duplicate-claim registry policy, actual TransportPrincipal public-path
  activation authority, sidecar public projection serving authority, sidecar
  bind/listener/peer-discovery authority, release publication/artifact/key and
  envelope authority, Genesis/v0.2 signing authority, wallet/ECU/ILC
  activation, CDL-088, and IP/publication clearance.

---

## 49. Phase 1299 Release Allowlist Artifact Genesis Readiness Preflight Addendum

Historical Phase 1298 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1298
Phase 1299 is the next sensitive phase
```

Phase 1299 records the release allowlist, artifact, and Genesis readiness
preflight after explicit `GO Phase 1299`:

```text
release_allowlist_artifact_genesis_readiness_preflight_phase_1299.v0.1
release_readiness_verdict_phase_1299=preflight_only_no_artifacts
source_allowlist_export_not_executed_phase_1299
release_artifact_not_produced_phase_1299
release_keys_not_generated_phase_1299
release_envelope_not_produced_phase_1299
genesis_atlas_not_mutated_or_signed_phase_1299
v0_2_signing_not_authorized_phase_1299
public_rc_exclude_helper_stripping_deferred_to_package_materialization_after_phase_1299
public_rc_remains_blocked_after_phase_1299
phase_1300_counsel_ip_publication_clearance_inventory_next
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1299.
- Window 1289-1302 OPEN through Phase 1299.
- Phase 1299 records release readiness classification only. Phase 1255 remains
  a source allowlist procedure, Phase 1213 remains a release artifact manifest
  schema, Phase 1279 and Phase 1287 remain prepublication/pre-signing
  preflights, and ATLAS-G-006 remains graph evidence with release artifacts
  blocked.
- Phase 1299 does not execute source export, materialize an export manifest,
  publish source or packages, produce release artifacts, produce a release
  artifact manifest instance, generate release keys, produce release envelopes,
  strip or promote helpers, remove markers, mutate Genesis Atlas, sign Genesis
  Atlas, authorize v0.2 signing, mutate the CDL register, open CDL-088, file
  IP, publish papers, or authorize wallet/ECU/ILC economics.
- `PUBLIC_RC_EXCLUDE` helper stripping is deferred to package materialization:
  Phase 1308 replacement/strip/carry-forward planning, Phase 1319 dry-run
  materialization, and Phase 1333 export execution gate if later authorized.
- Phase 1300 is the next sensitive phase and requires explicit `GO Phase 1300`.
- Public RC remains blocked by final public claimability API/verifier
  authority, privacy filter implementation/review, replay/nullifier and
  duplicate-claim registry policy, actual TransportPrincipal public-path
  activation authority, sidecar public projection serving authority, sidecar
  bind/listener/peer-discovery authority, counsel/IP/publication clearance,
  source allowlist export execution, release publication/artifact/key and
  envelope authority, Genesis/v0.2 signing authority, wallet/ECU/ILC
  activation, and CDL-088.

---

## 50. Phase 1300 Counsel IP Publication Clearance Inventory Addendum

Historical Phase 1299 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1299
Phase 1300 is the next sensitive phase
```

Phase 1300 records the counsel, IP, and publication clearance inventory after
explicit `GO Phase 1300`:

```text
counsel_ip_publication_clearance_inventory_phase_1300.v0.1
counsel_ip_publication_verdict_phase_1300=inventory_only_no_publication
ip_filing_not_performed_phase_1300
paper_publication_not_authorized_phase_1300
public_repository_publication_not_authorized_phase_1300
public_package_publication_not_authorized_phase_1300
public_rc_remains_blocked_after_phase_1300
phase_1301_deep_no_activation_assertion_audit_next
```

Roadmap impact:

- At Phase 1300 close, Window 1289-1302 was open through Phase 1300.
- Historical Phase 1300 frontier phrase guard: Window 1289-1302 OPEN through Phase 1300.
- Phase 1300 confirms CDL-086 counsel dispositions are Genesis-authorized
  provisional dispositions only, not counsel-approved legal conclusions.
- Phase 1300 confirms IP-001 through IP-006 remain internal-only
  IP/publication planning lanes, with IP-lane files `PUBLIC_RC_EXCLUDE` by
  default.
- Phase 1300 does not select final license instruments, approve CLA text,
  approve DCO-only contributor policy, publish trademark or canonical identity
  policy, execute the publication clearance matrix, file IP, publish papers,
  release a preprint, execute source allowlist export, publish a repository,
  publish a package, produce release artifacts, generate release keys, produce
  release envelopes, mutate Genesis Atlas, sign Genesis Atlas, authorize v0.2
  signing, mutate the CDL register, open CDL-088, activate public paths, or
  authorize wallet/ECU/ILC economics.
- At Phase 1300 close, Phase 1301 was the next sensitive phase and required explicit `GO Phase 1301`; Phase 1301 is now complete.
- Public RC remains blocked by final public claimability API/verifier
  authority, privacy filter implementation/review, replay/nullifier and
  duplicate-claim registry policy, actual TransportPrincipal public-path
  activation authority, sidecar public projection serving authority, sidecar
  bind/listener/peer-discovery authority, open
  CLA/trademark/IP/patent/publication clearance, source allowlist export
  execution, release publication/artifact/key and envelope authority,
  Genesis/v0.2 signing authority, wallet/ECU/ILC activation, and CDL-088.

## 50a. Phase 1323 Fix3 Layered License Posture Addendum

Phase 1323 Fix3 implements the provisional layered license posture now, rather
than leaving blanket MIT as the effective current posture while awaiting future
counsel review.

```text
phase_1323_fix3_layered_license_posture.v0.1
blanket_mit_license_removed_phase_1323_fix3
agpl_runtime_default_recorded_phase_1323_fix3
licensing_zone_table_committed_phase_1323_fix3
genesis_canonical_identity_zone_recorded_phase_1323_fix3
patent_pending_zone_reserved_phase_1323_fix3
whitepaper_mit_language_replaced_phase_1323_fix3
ip_series_confirmed_as_ip001_to_ip006_phase_1323_fix3
public_rc_remains_blocked_after_phase_1323_fix3
```

Roadmap impact:

- The current root `LICENSE` is no longer blanket MIT; it records a layered
  license notice and delegates zone boundaries to `LICENSING.md`.
- Runtime/source package metadata now defaults to `AGPL-3.0-only` for bootstrap
  protection.
- `LICENSING.md` records separate zones for runtime code, protocol interfaces
  and schemas, Genesis canonical artifacts, explanatory docs, patent-sensitive
  material, services, trademarks/canonical identity, and internal-only files.
- The remembered legal/patent phase lane is confirmed in current canon as
  IP-001 through IP-006, not an active P-series or L-series.
- Future counsel review/modification remains expected, but root license/zone
  table selection is no longer an unresolved implementation blocker.
- Fix3 does not approve CLA text, publish trademark policy, file IP, publish
  papers, execute source allowlist export, publish a repository, publish a
  package, produce release artifacts, generate release keys or envelopes,
  mutate/sign Genesis Atlas, authorize v0.2 signing, open CDL-088, activate
  public paths, or authorize wallet/ECU/ILC economics.

## 50b. Phase 1324 CCSS-001 Private/Gated Shard Contract Addendum

Phase 1324 implements the first concrete Confidential Coordination Sidecar
Suite contract as a local-only private/gated shard sidecar substrate.

```text
ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1
encrypted_coordination_node_envelope_contract_recorded_phase_1324
shard_header_projection_contract_recorded_phase_1324
private_to_public_promotion_evidence_shape_recorded_phase_1324
ccss_public_serving_not_enabled_phase_1324
phase_1325_ccss_capability_membership_boundary_next
public_rc_remains_blocked_after_phase_1324
```

Roadmap impact:

- `ilc_core/sidecars/confidential_coordination_shard.py` now defines and
  validates `PrivateShardRef`, `EncryptedCoordinationNodeEnvelope`,
  `ShardHeaderProjection`, `PromotionEvidenceRef`, and `DisclosureDenial`.
- The sidecar registry records `confidential_coordination_private_gated_shard`
  under `phase_1324_private_local_contract_only` and requires it for the
  confidential coordination local-preview profile.
- The contract carries only opaque refs, ciphertext digests/storage refs,
  bounded sizes, local header projection metadata, and promotion-evidence refs.
- Plaintext body, membership list, route history, sender/recipient identity,
  AgentID, wallet, harness, IP, seed, mnemonic, private-key, and secret fields
  are denied by the contract and focused tests.
- Promotion evidence remains shape-only and preserves CDL-038: no public
  promotion, no private content reveal, no public availability claim, no
  automatic public corroboration carry-forward, and no automatic public
  reputation carry-forward.
- Phase 1324 does not execute ATLAS-G-007 through ATLAS-G-010, authorize public
  confidential coordination serving, public P2P, source publication, package
  publication, release artifact/key/envelope production, release signing,
  public promotion, identity bootstrap, wallet actions, ECU minting, ILC
  settlement, or value-path activation.

## 51. Phase 1301 Deep No-Activation Assertion Audit Addendum

Historical Phase 1300 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1300
Phase 1301 is the next sensitive phase
```

Phase 1301 records the deep no-activation assertion audit after explicit
`GO Phase 1301`:

```text
deep_no_activation_assertion_audit_phase_1301.v0.1
no_activation_audit_verdict_phase_1301=pass_or_blockers_recorded
public_endpoint_activation_absent_or_blocked_phase_1301
release_artifact_activation_absent_or_blocked_phase_1301
genesis_signing_activation_absent_or_blocked_phase_1301
wallet_ecu_ilc_activation_absent_or_blocked_phase_1301
public_rc_remains_blocked_after_phase_1301
phase_1302_window_1289_1302_closure_gate_next
legacy_public_labeled_fastapi_routes_carry_forward_phase_1301
legacy_public_labeled_fastapi_routes_not_public_rc_clean_phase_1301
```

Roadmap impact:

- Window 1289-1302 is now open through Phase 1301.
- Window 1289-1302 OPEN through Phase 1301.
- Phase 1301 confirms no source allowlist export execution, materialized export
  manifest production, public repository publication, public package
  publication, release artifact production, release-key generation, release
  envelope production, Genesis Atlas mutation/signing, v0.2 signing, CDL
  mutation, CDL-088 opening, public claimability activation, public P2P/fetch
  serving activation, public sidecar/projection serving, wallet withdrawal,
  wallet transfer, wallet spend, ECU minting, or ILC settlement authority was
  granted.
- Phase 1301 records legacy `/v1/public/*` FastAPI routes in `ilc_core/server.py`
  as clean-public-RC blockers, not as public-RC activation authority.
- Phase 1302 is sensitive and requires explicit `GO Phase 1302`.
- Public RC remains blocked by legacy public-labeled FastAPI route exclusion or
  replacement, final public claimability API/verifier authority, privacy filter
  implementation/review, replay/nullifier and duplicate-claim registry policy,
  actual TransportPrincipal public-path activation authority, sidecar public
  projection serving authority, sidecar bind/listener/peer-discovery authority,
  open CLA/trademark/IP/patent/publication clearance, source
  allowlist export execution, release publication/artifact/key and envelope
  authority, Genesis/v0.2 signing authority, wallet/ECU/ILC activation, and
  CDL-088.

## 52. Phase 1302 Window 1289-1302 Closure Gate Addendum

Historical Phase 1301 frontier phrase guard:

```text
Window 1289-1302 OPEN through Phase 1301
Phase 1302 is the next sensitive phase
```

Phase 1302 records the Window 1289-1302 closure gate after explicit
`GO Phase 1302`:

```text
window_1289_1302_closed_phase_1302
window_1289_1302_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1302_window_1289_1302_closure_complete
window_1303_plus_sequence_lock_required_before_next_phase_assignment
public_rc_exclude_helper_stripping_carried_forward_to_window_1303_plus
public_rc_remains_blocked_after_phase_1302
```

Roadmap impact:

- Window 1289-1302 CLOSED / PASS through Phase 1302 with blockers carried
  forward.
- Window 1303+ sequence lock is required before assigning further phases,
  including any Phase 1303 implementation-hardening work.
- Phase 1302 closes the window's planned sequence lock, capsule refresh,
  claimability verifier contract, package-boundary rehearsal, helper register,
  allowlist rehearsal, TransportPrincipal preflight, hostile-network plan,
  sidecar schema, sidecar bind/listener/peer-discovery preflight, release
  readiness preflight, counsel/IP/publication inventory, and no-activation
  audit work.
- Phase 1302 does not execute source allowlist export, materialize a public
  export tree, publish a repository, publish a package, produce release
  artifacts, generate release keys, produce release envelopes, promote or strip
  helpers, mutate Genesis Atlas, sign Genesis Atlas, authorize v0.2 signing,
  mutate the CDL register, open CDL-088, activate public paths, or authorize
  wallet/ECU/ILC economics.
- Public RC remains blocked after Phase 1302 by legacy public-labeled FastAPI
  route exclusion or replacement, Final public claimability verifier/API
  authority, `PUBLIC_RC_EXCLUDE` helper replacement, stripping, or explicit
  deferral, privacy filter implementation/review, replay/nullifier and
  duplicate-claim registry policy, actual TransportPrincipal public-path
  activation authority, Rust public P2P integration and hostile-network
  transport hardening, sidecar public projection serving authority, sidecar
  bind/listener/peer-discovery authority, counsel-approved
  license/CLA/trademark/IP/publication clearance, source allowlist export
  execution, clean public tree materialization, release artifact production,
  release-key generation, release envelope production, Genesis Atlas
  mutation/regeneration/signing, v0.2 signing, CDL-088 opening, wallet
  withdrawal, wallet transfer, wallet spend, wallet signing authority, wallet
  ledger-write authority, ECU minting, and ILC settlement.

Exact Phase 1302 blocker phrase guard:

```text
Final public claimability verifier/API authority
`PUBLIC_RC_EXCLUDE` helper replacement, stripping
Rust public P2P integration
privacy filter implementation/review
source allowlist export execution
release artifact production
release-key generation
release envelope production
Genesis Atlas mutation/regeneration/signing
v0.2 signing
CDL-088 opening
wallet withdrawal
ECU minting
ILC settlement
```

## 53. Phase 1305 Offline Claimability Receipt Verifier Sidecar Addendum

Phase 1305 records the offline/local claimability receipt verifier sidecar after
explicit `GO Phase 1305`:

```text
offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1
claimability_verifier_local_only_no_api_phase_1305
receipt_verifier_public_serving_not_enabled_phase_1305
public_claimability_activation_not_authorized_phase_1305
phase_1306_proof_binding_canonical_hash_negative_path_tests_next
public_rc_remains_blocked_after_phase_1305
```

Roadmap impact:

- Gap 13 now has a local-only verifier substrate at
  `ilc_core/sidecars/claimability_receipt_verifier.py`.
- The sidecar verifies canonical local presentations, conversion receipts,
  claimability proofs, settled runtime roots, wallet-state roots, balance
  receipt refs, history digests, activation flags, exact numeric strings, and
  canonical decision hashes.
- Accepted decisions are `accepted_local_only_no_public_serving_phase_1305` and
  still carry public-mode blockers.
- Rejected decisions fail closed with stable rejection tokens.
- The sidecar does not import or promote the existing `PUBLIC_RC_EXCLUDE`
  Phase 1274/1275 ledger helpers.
- Public RC remains blocked by public claimability API/verifier serving
  authority, public-safe disclosure, replay/nullifier policy, duplicate-claim
  policy, TransportPrincipal public-path authority, `PUBLIC_RC_EXCLUDE` helper
  disposition, package/export materialization, release authority, wallet
  withdrawal/transfer/spend semantics, ECU minting, and ILC settlement.

Phase 1305 does not authorize source export, public repository publication,
public package publication, release artifacts, release keys, release envelopes,
release signing material, public claimability activation, public verifier
service, public claim endpoint, public P2P/fetch/sidecar serving, helper
promotion, marker removal, helper stripping, CDL mutation, CDL-088 opening,
Genesis Atlas mutation/regeneration/signing, v0.2 signing, wallet withdrawal,
wallet transfer, wallet spend, ECU minting, ILC settlement, public confidential
messaging, or public confidential coordination serving.

Phase 1306 is sensitive and requires explicit `GO Phase 1306`.

## 54. Phase 1306 Proof-Binding Canonical-Hash Negative-Path Addendum

Phase 1306 records proof-binding, canonical-hash, exact-numeric, and
negative-path hardening after explicit `GO Phase 1306`:

```text
proof_binding_canonical_hash_negative_path_tests_phase_1306.v0.1
forged_receipt_negative_paths_hardened_phase_1306
canonical_json_exact_numeric_proof_safety_hardened_phase_1306
replay_nullifier_duplicate_claim_policy_still_gated_phase_1306
phase_1307_sidecar_registry_manifest_profile_hardening_next
public_rc_remains_blocked_after_phase_1306
```

Roadmap impact:

- Gap 13 now has focused local verifier negative-path tests for forged
  conversion receipts, forged proof-binding hashes, forged proof refs, root
  namespace drift, latest balance receipt ref drift, exact numeric drift,
  canonical JSON drift, canonical decision hash drift, and semantic decision
  forgery.
- `ilc_core/sidecars/claimability_receipt_verifier.py` now rejects tuple values
  as non-JSON canonical payloads and bounds mapping-key text before hashing.
- Replay/nullifier policy and duplicate-claim registry policy remain gated
  blockers, not solved by local proof validity.
- The public RC packaging architecture gate now records deterministic scaffold
  compilation: development scaffolding and token chains are retained in the
  private workspace, while public RC materialization must compile them into
  final contracts or exclude them by disposition.
- Public RC remains blocked by public claimability API/verifier serving
  authority, public-safe disclosure, replay/nullifier policy, duplicate-claim
  policy, TransportPrincipal public-path authority, `PUBLIC_RC_EXCLUDE` helper
  disposition, package/export materialization, release authority, wallet
  withdrawal/transfer/spend semantics, ECU minting, and ILC settlement.

Phase 1306 does not authorize source export, public repository publication,
public package publication, release artifacts, release keys, release envelopes,
release signing material, public claimability activation, public verifier
service, public claim endpoint, public P2P/fetch/sidecar serving, helper
promotion, marker removal, helper stripping, CDL mutation, CDL-088 opening,
Genesis Atlas mutation/regeneration/signing, v0.2 signing, wallet withdrawal,
wallet transfer, wallet spend, ECU minting, ILC settlement, public confidential
messaging, or public confidential coordination serving.

Phase 1307 has now completed, and Phase 1308 is recorded below. Phase 1309 is
sensitive and requires explicit `GO Phase 1309`.

## 55. Phase 1307 Graph-Native Sidecar Registry Manifest Addendum

Phase 1307 records graph-native sidecar registry/manifest and package-profile
hardening after explicit `GO Phase 1307`:

```text
graph_native_sidecar_registry_manifest_phase_1307.v0.1
sidecar_manifest_deterministic_profile_declared_phase_1307
openclaw_compatible_local_bridge_profile_declared_phase_1307
confidential_coordination_local_preview_profile_declared_phase_1307
package_profile_integrity_hardened_phase_1307
phase_1308_public_rc_exclude_helper_pruning_replacement_plan_next
public_rc_remains_blocked_after_phase_1307
```

Roadmap impact:

- Gap 14 now has deterministic local/package sidecar registry metadata at
  `ilc_core/sidecars/registry_manifest.py`.
- `openclaw_skill_local` and `openclaw_skill_claimable` package profiles now
  include the graph-native sidecar registry and OpenClaw-compatible local bridge
  components.
- `openclaw_skill_claimable` now requires the offline claimability receipt
  verifier sidecar as package-profile integrity metadata; public claimability
  runtime activation remains false.
- `confidential_coordination_local_preview` is declared as a private/local
  package profile with no public confidential messaging claim and no public
  confidential coordination serving claim.
- OpenClaw, NemoClaw, DigitalOcean droplets, and equivalent harnesses remain
  hosts or consumers, not protocol substrates.
- The `local_sidecar` package-profile CI surface now measures
  `ilc_core/sidecars`, and the deterministic Phase 1251 package-profile audit
  artifacts were refreshed under profile version
  `public_rc_package_profiles_1307.v0.1`.
- Source allowlist readiness remains fail-closed: no source allowlist export,
  no clean public tree materialization, no public package publication, and no
  release materialization occurred.
- Phase 1308 is the helper disposition planning point for `PUBLIC_RC_EXCLUDE`
  helper replacement, stripping, or deferral and has now recorded the concrete
  runtime-helper inventory.

Phase 1307 does not authorize public serving, source export, public repository
publication, public package publication, release artifacts, release keys,
release envelopes, release signing material, public claimability activation,
public verifier service, public claim endpoint, public P2P/fetch/sidecar
serving, helper promotion, marker removal, helper stripping, CDL mutation,
CDL-088 opening, Genesis Atlas mutation/regeneration/signing, v0.2 signing,
wallet withdrawal, wallet transfer, wallet spend, ECU minting, ILC settlement,
public confidential messaging, or public confidential coordination serving.

Phase 1308, Phase 1309, Phase 1310, Phase 1311, Phase 1312, Phase 1313,
Phase 1314, Phase 1315, and Phase 1316 have now completed. Window 1303-1316 is
closed with carry-forward.

## 62. Phase 1316 Window 1303-1316 Closure Implementation Audit Addendum

Phase 1316 closes Window 1303-1316 after explicit `GO Phase 1316`:

```text
window_1303_1316_closed_phase_1316
window_1303_1316_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1316_window_1303_1316_closure_complete
window_1317_plus_sequence_lock_required_before_next_phase_assignment
implementation_hardening_blockers_classified_phase_1316
public_rc_remains_blocked_after_phase_1316
```

Window 1303-1316 is CLOSED / PASS with carry-forward through Phase 1316.
The closure handoff is
`docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md`. No next phase is
assigned; Window 1317+ sequence lock is required before any further phase
assignment.

Roadmap impact:

- Window 1303-1316 completed local/offline implementation hardening for the
  claimability verifier substrate, proof-binding negative paths, graph-native
  sidecar registry/profile metadata, `PUBLIC_RC_EXCLUDE` helper disposition
  planning, TransportPrincipal local admission, hostile-network negative-path
  tests, local projection privacy, default-off public fetch/P2P readiness,
  wallet-facing preflight boundaries, and ECU/ILC value-path preflight
  boundaries.

Exact Phase 1316 blocker phrase guard:

```text
legacy public-labeled FastAPI routes
public claimability verifier/API serving authority
replay/nullifier and duplicate-claim registry policy
PUBLIC_RC_EXCLUDE helper replacement and dry-run export proof
Rust public-P2P substrate ADR/integration gate
TransportPrincipal public-path activation authority
public sidecar/projection serving authority
source allowlist export execution
clean materialized public tree production
release artifact production
release-key generation
Genesis Atlas mutation/regeneration/signing
v0.2 signing authorization
wallet-facing action activation
ECU minting activation
ILC settlement activation
final value-path activation authority
```

- Public RC remains blocked by legacy public-labeled FastAPI routes, public
  claimability verifier/API serving authority, replay/nullifier and
  duplicate-claim registry policy, PUBLIC_RC_EXCLUDE helper replacement and
  dry-run export proof, Rust public-P2P substrate ADR/integration gate,
  TransportPrincipal public-path activation authority, public
  sidecar/projection serving authority, source allowlist export execution,
  clean materialized public tree production, release artifact production,
  release-key generation, Genesis Atlas mutation/regeneration/signing, v0.2
  signing authorization, wallet-facing action activation, ECU minting
  activation, ILC settlement activation, and final value-path activation
  authority.
- No public RC claim, source allowlist export execution, public repository
  publication, public package publication, release artifact production,
  release-key generation, release envelope production, release signing
  material, public claimability activation, public verifier service, public
  claim endpoint, public P2P, public fetch serving, public sidecar/projection
  serving, non-loopback bind, public listener, peer discovery, helper
  promotion, marker removal, helper stripping, CDL mutation, CDL-088 opening,
  Genesis Atlas mutation, v0.2 signing, wallet-facing withdrawal request,
  wallet-facing transfer request, wallet-facing spend request,
  wallet-provider signing, wallet-provider ledger-write, ECU minting, ILC
  settlement, or value-path activation is authorized by Phase 1316.

## 56. Phase 1308 PUBLIC_RC_EXCLUDE Helper Disposition Addendum

Phase 1308 records helper pruning/replacement planning after explicit
`GO Phase 1308`:

```text
public_rc_exclude_helper_pruning_replacement_plan_phase_1308.v0.1
public_rc_exclude_helper_disposition_inventory_recorded_phase_1308
truth_primitive_sidecar_boundary_recorded_phase_1308
helper_stripping_not_executed_phase_1308
source_allowlist_export_not_executed_phase_1308
phase_1309_transport_principal_admission_sidecar_lifecycle_next
public_rc_remains_blocked_after_phase_1308
```

Roadmap impact:

- The four current runtime `PUBLIC_RC_EXCLUDE` helpers are mapped to
  `replace_before_export`: the CDL-048 conversion sweeper, claimability
  proof-binding scaffold, TransportPrincipal public-path preflight scaffold,
  and sidecar public-path preflight scaffold.
- The public-RC package path remains materialization-based: later dry-run and
  execution gates must prove no marked helpers and no stripped-helper imports
  exist in the clean public tree.
- The truth primitive submission sidecar boundary is now recorded for local
  graph-native use. It does not authorize public API serving, graph
  persistence, network delivery, public confidential messaging, or public
  confidential coordination serving.
- Legacy docs and documents carrying `PUBLIC_RC_EXCLUDE` remain excluded or
  review-required by default; absence of the marker remains not enough for
  allowlist clearance.
- Phase 1309 is now the next sensitive gate for TransportPrincipal admission
  sidecar lifecycle hardening.

Phase 1308 does not authorize helper promotion, marker removal, helper
stripping, source allowlist export, clean public tree materialization, public
repository publication, public package publication, release artifacts, release
keys, release envelopes, release signing material, public claimability
activation, public verifier service, public claim endpoint, public P2P/fetch
serving, public sidecar/projection serving, CDL mutation, CDL-088 opening,
Genesis Atlas mutation/regeneration/signing, v0.2 signing, wallet withdrawal,
wallet transfer, wallet spend, ECU minting, ILC settlement, public confidential
messaging, or public confidential coordination serving.

Phase 1309, Phase 1310, Phase 1311, Phase 1312, Phase 1313, Phase 1314, and
Phase 1315 have now completed. Phase 1316 is sensitive and requires explicit
`GO Phase 1316`.

## 57. Phase 1309 TransportPrincipal Admission Sidecar Lifecycle Addendum

Phase 1309 records local-only TransportPrincipal admission sidecar lifecycle
hardening after explicit `GO Phase 1309`:

```text
transport_principal_admission_sidecar_lifecycle_hardening_phase_1309.v0.1
transport_principal_lifecycle_policy_local_substrate_phase_1309
transport_principal_public_path_not_activated_phase_1309
public_p2p_not_activated_phase_1309
phase_1310_revocation_replay_admission_ban_tests_next
public_rc_remains_blocked_after_phase_1309
```

Roadmap impact:

- Gap 10 now has a deterministic local-only TransportPrincipal admission
  sidecar lifecycle substrate at `ilc_core/sidecars/transport_principal_admission.py`.
- The sidecar uses Phase 1267 authenticated TransportPrincipal context material
  and emits canonical local admission decisions with bounded revocation, replay,
  accepted-kind, and ban inputs.
- The sidecar rejects requester_id, JSON requester id, client IP, AgentID,
  harness identity, OpenClaw identity, and Tailscale identity fallback flags.
- The sidecar does not import or promote the stale Phase 1277
  `PUBLIC_RC_EXCLUDE` public-path preflight helper.
- The graph-native sidecar registry now records `transport_principal_admission`
  as `lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310`.
- The sensitive-runtime coding taboo checker now scans the new admission
  sidecar for canonical JSON, untrusted payload bounds, assert usage, wall-clock
  usage, and predictable PRNG usage.
- Phase 1310 has now hardened revocation, replay, admission, and ban
  negative-path tests. Public-path readiness remains blocked until later
  explicit public-path authority and substrate evidence.

Phase 1309 does not authorize public P2P, public fetch serving, public
sidecar/projection serving, public credential issuer authority, credential
lifecycle policy activation for a public path, public revocation registry
activation, public replay cache activation, admission policy activation for a
public path, ban registry activation for a public path, public rate-limit state
activation, privacy policy activation for a public path, non-loopback bind,
wildcard bind, public host bind, listener, peer discovery, helper promotion,
marker removal, helper stripping, source allowlist export, clean public tree
materialization, public repository publication, public package publication,
release artifacts, release keys, release envelopes, release signing material,
CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration/signing,
v0.2 signing, wallet withdrawal, wallet transfer, wallet spend, ECU minting,
ILC settlement, public confidential messaging, or public confidential
coordination serving.

Phase 1310, Phase 1311, Phase 1312, Phase 1313, Phase 1314, and Phase 1315
have now completed. Phase 1316 is sensitive and requires explicit
`GO Phase 1316`.

## 62. Phase 1314 Wallet-Facing Value-Action Semantics Preflight Addendum

Phase 1314 records wallet-facing withdrawal, transfer, and spend request
semantics preflight after explicit `GO Phase 1314`:

```text
wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1
wallet_withdrawal_transfer_spend_not_activated_phase_1314
wallet_signing_ledger_write_not_authorized_phase_1314
public_claimability_user_action_boundary_recorded_phase_1314
wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314
phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next
public_rc_remains_blocked_after_phase_1314
```

Roadmap impact:

- Gap 13 now has a deterministic local wallet-facing value-action semantics
  preflight packet at `ilc_core/sidecars/wallet_action_semantics_preflight.py`.
- The current public wallet runtime remains read-only with only
  `wallet_status`, `wallet_history`, `wallet_export`, and `ledger_summary`.
- The graph-native sidecar registry now records
  `wallet_action_semantics_preflight` with no public serving and requires it
  for the OpenClaw/NemoClaw claimable local bridge profile.
- The claimable package profile now records
  `wallet_action_semantics_preflight_sidecar` as a package component, but this
  is still preflight/package metadata and not wallet activation.
- Public RC remains blocked by public claimability API/verifier authority,
  public claim endpoint authority, replay/nullifier and duplicate-claim policy,
  source/release/signing authority, ECU minting, ILC settlement, and final
  explicit wallet-facing action activation authority.
- ILC is recorded as wallet-provider agnostic but not ledger-truth agnostic:
  wallets are adapters/sidecars around ledger state, graph state, receipts,
  settled roots, wallet-root bindings, claimability proofs, and deterministic
  sidecar manifests.
- A future ILC-native wallet should be routed as an optional recipe of
  graph-native sidecars: provider adapter, signing-intent/payload binding,
  ledger-truth value-action validation, receipt/history presentation, and
  recovery/export portability. This is a later planning lane after Phase 1315
  settlement-boundary work, not a Phase 1314 deliverable.

Phase 1314 does not authorize public P2P, public fetch serving, public
sidecar/projection serving, public credential issuer authority, credential
lifecycle policy activation for a public path, public revocation registry
activation, public replay cache activation, public rate-limit state activation,
admission policy activation for a public path, ban registry activation for a
public path, privacy policy activation for a public path, non-loopback bind,
wildcard bind, public host bind, listener, peer discovery, helper promotion,
marker removal, helper stripping, source allowlist export, clean public tree
materialization, public repository publication, public package publication,
release artifacts, release keys, release envelopes, release signing material,
CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration/signing,
v0.2 signing, wallet-facing withdrawal requests, wallet-facing transfer
requests, wallet-facing spend requests, wallet-provider signing requests,
wallet-provider ledger-write requests, public claim endpoint, ECU minting, ILC
settlement, withdrawal runtime activation, public confidential messaging, or
public confidential coordination serving.

Phase 1315 has now completed. Phase 1316 is sensitive and requires explicit
`GO Phase 1316`.

## 63. Phase 1315 ECU/ILC Value-Path Boundary Preflight Addendum

Phase 1315 records ECU minting and ILC settlement boundary preflight after
explicit `GO Phase 1315`:

```text
ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1
ecu_minting_not_authorized_phase_1315
ilc_settlement_not_authorized_phase_1315
value_path_activation_boundary_recorded_phase_1315
phase_1316_window_1303_1316_closure_audit_next
public_rc_remains_blocked_after_phase_1315
```

Roadmap impact:

- Gap 12/13 now has a deterministic local ECU/ILC value-path activation
  boundary packet at
  `ilc_core/sidecars/value_path_activation_boundary_preflight.py`.
- The packet records local read-only substrates while blocking ECU minting, ECU
  creation, ECU supply policy mutation, ILC settlement, ILC transfer,
  settlement root publication, withdrawal runtime, wallet writes, public
  claimability activation, public claim endpoint, release materialization, and
  CDL-088 opening.
- The graph-native sidecar registry now records
  `value_path_activation_boundary_preflight` with no public serving and
  requires it for the OpenClaw/NemoClaw claimable local bridge profile.
- The claimable package profile now records
  `value_path_activation_boundary_preflight_sidecar` as a package component,
  but this is still preflight/package metadata and not value-path activation.
- Public RC remains blocked by public claimability API/verifier authority,
  public claim endpoint authority, replay/nullifier and duplicate-claim policy,
  source/release/signing authority, public transport/projection authority,
  ECU minting activation authority, ILC settlement activation authority,
  withdrawal runtime authority, wallet write authority, and final explicit
  value-path activation authority.
- ILC remains wallet-provider agnostic but not ledger-truth agnostic: wallets
  are adapters/sidecars around ledger state, graph state, receipts, settled
  roots, wallet-root bindings, claimability proofs, and deterministic sidecar
  manifests.

Phase 1315 does not authorize public P2P, public fetch serving, public
sidecar/projection serving, public credential issuer authority, credential
lifecycle policy activation for a public path, public revocation registry
activation, public replay cache activation, public rate-limit state activation,
admission policy activation for a public path, ban registry activation for a
public path, privacy policy activation for a public path, non-loopback bind,
wildcard bind, public host bind, listener, peer discovery, helper promotion,
marker removal, helper stripping, source allowlist export, clean public tree
materialization, public repository publication, public package publication,
release artifacts, release keys, release envelopes, release signing material,
CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration/signing,
v0.2 signing, wallet-facing withdrawal requests, wallet-facing transfer
requests, wallet-facing spend requests, wallet-provider signing requests,
wallet-provider ledger-write requests, public claim endpoint, public
claimability activation, withdrawal runtime, ECU minting, ILC settlement,
value-path activation, public confidential messaging, or public confidential
coordination serving.

Phase 1316 has now completed and closed Window 1303-1316 with carry-forward.

## 58. Phase 1310 Revocation Replay Admission Ban Tests Addendum

Phase 1310 records hostile-network local negative-path hardening after explicit
`GO Phase 1310`:

```text
revocation_replay_admission_ban_tests_phase_1310.v0.1
transport_principal_revocation_replay_tests_hardened_phase_1310
admission_ban_rate_privacy_tests_hardened_phase_1310
hostile_network_public_path_still_blocked_phase_1310
phase_1311_local_graph_memory_projection_sidecar_next
public_rc_remains_blocked_after_phase_1310
```

Roadmap impact:

- Gap 10 now has local hostile-network negative-path coverage for
  TransportPrincipal revocation, replay, admission, ban, rate-limit, and
  privacy behavior.
- The admission sidecar now rejects fallback/private context keys including
  `requester_id`, `client_ip`, `AgentID`, `agent_id`, harness identity,
  OpenClaw identity, Tailscale identity, wallet fields, stake fields, economic
  position, and graph position.
- Local rate-limit checks are bounded and keyed only by authenticated
  `tp_rate:<sha256>` material. This is caller-supplied local state only, not a
  public rate-limit registry.
- Admission decision validation now rejects unexpected decision keys and
  non-JSON value types before canonical validation or export.
- The graph-native sidecar registry now records `transport_principal_admission`
  as `lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310`.
- Public TransportPrincipal path activation remains blocked pending public
  credential issuer authority, public revocation registry, public replay cache,
  public rate-limit state, public admission and ban policy, public privacy
  policy, Rust public-P2P substrate evidence, and explicit public transport
  activation authority.

Phase 1310 does not authorize public P2P, public fetch serving, public
sidecar/projection serving, public credential issuer authority, credential
lifecycle policy activation for a public path, public revocation registry
activation, public replay cache activation, public rate-limit state activation,
admission policy activation for a public path, ban registry activation for a
public path, privacy policy activation for a public path, non-loopback bind,
wildcard bind, public host bind, listener, peer discovery, helper promotion,
marker removal, helper stripping, source allowlist export, clean public tree
materialization, public repository publication, public package publication,
release artifacts, release keys, release envelopes, release signing material,
CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration/signing,
v0.2 signing, wallet withdrawal, wallet transfer, wallet spend, ECU minting,
ILC settlement, public confidential messaging, or public confidential
coordination serving.

Phase 1311, Phase 1312, Phase 1313, Phase 1314, Phase 1315, and Phase 1316
have now completed. Window 1303-1316 is closed with carry-forward.

## 59. Phase 1311 Local Graph Memory Projection Sidecar Addendum

Phase 1311 records local graph/memory projection sidecar implementation after
explicit `GO Phase 1311`:

```text
local_graph_memory_projection_sidecar_phase_1311.v0.1
public_safe_projection_implementation_local_only_phase_1311
confidential_coordination_projection_reference_local_only_phase_1311
public_sidecar_projection_serving_not_enabled_phase_1311
phase_1312_projection_privacy_field_filtering_tests_next
public_rc_remains_blocked_after_phase_1311
```

Roadmap impact:

- Gap 9 now has a deterministic local-only projection sidecar substrate at
  `ilc_core/sidecars/local_graph_memory_projection.py`.
- The sidecar emits bounded canonical projection envelopes with aggregate
  summaries, opaque private/gated shard header refs, and opaque encrypted
  coordination-node refs.
- The sidecar denies plaintext, membership, route history, sealed payloads,
  AgentID, requester id, client IP, harness identity, OpenClaw identity,
  Tailscale identity, wallet fields, stake fields, and economic fields.
- The graph-native sidecar registry now records `local_graph_memory_projection`
  as
  `local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312`.
- Public sidecar/projection serving remains blocked pending explicit public
  projection serving authority, bind/listener/peer-discovery authority,
  TransportPrincipal public-path
  activation authority, source/release authority, and final public RC gates.

Phase 1311 does not authorize public P2P, public fetch serving, public
sidecar/projection serving, public credential issuer authority, credential
lifecycle policy activation for a public path, public revocation registry
activation, public replay cache activation, public rate-limit state activation,
admission policy activation for a public path, ban registry activation for a
public path, privacy policy activation for a public path, non-loopback bind,
wildcard bind, public host bind, listener, peer discovery, helper promotion,
marker removal, helper stripping, source allowlist export, clean public tree
materialization, public repository publication, public package publication,
release artifacts, release keys, release envelopes, release signing material,
CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration/signing,
v0.2 signing, wallet withdrawal, wallet transfer, wallet spend, ECU minting,
ILC settlement, public confidential messaging, or public confidential
coordination serving.

Phase 1312, Phase 1313, Phase 1314, Phase 1315, and Phase 1316 have now
completed. Window 1303-1316 is closed with carry-forward.

## 60. Phase 1312 Projection Privacy Field Filtering Tests Addendum

Phase 1312 records projection privacy and field-filtering hardening after
explicit `GO Phase 1312`:

```text
projection_privacy_field_filtering_tests_phase_1312.v0.1
projection_privacy_filters_hardened_phase_1312
confidential_coordination_projection_non_leakage_tests_phase_1312
public_sidecar_projection_serving_not_enabled_phase_1312
phase_1313_public_fetch_p2p_activation_candidate_default_off_next
public_rc_remains_blocked_after_phase_1312
```

Roadmap impact:

- Gap 9 now has focused local tests for deny-by-default projection field
  filtering, raw identifier redaction, confidential-coordination non-leakage,
  and bounded-serving blockers.
- `ilc_core/sidecars/local_graph_memory_projection.py` now rejects forbidden
  raw export fragments before canonical JSON export, in addition to the Phase
  1311 forbidden-key and exact-schema checks.
- The graph-native sidecar registry now records `local_graph_memory_projection`
  as
  `local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312`.
- Public sidecar/projection serving remains blocked pending explicit public
  projection serving authority, bind/listener/peer-discovery authority,
  TransportPrincipal public-path activation authority, source/release authority,
  and final public RC gates.

Phase 1312 does not authorize public P2P, public fetch serving, public
sidecar/projection serving, public credential issuer authority, credential
lifecycle policy activation for a public path, public revocation registry
activation, public replay cache activation, public rate-limit state activation,
admission policy activation for a public path, ban registry activation for a
public path, privacy policy activation for a public path, non-loopback bind,
wildcard bind, public host bind, listener, peer discovery, helper promotion,
marker removal, helper stripping, source allowlist export, clean public tree
materialization, public repository publication, public package publication,
release artifacts, release keys, release envelopes, release signing material,
CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration/signing,
v0.2 signing, wallet withdrawal, wallet transfer, wallet spend, ECU minting,
ILC settlement, public confidential messaging, or public confidential
coordination serving.

Phase 1313, Phase 1314, Phase 1315, and Phase 1316 have now completed. Window
1303-1316 is closed with carry-forward.

## 61. Phase 1313 Public Fetch/P2P Default-Off Readiness Addendum

Phase 1313 records a public fetch/P2P readiness candidate after explicit
`GO Phase 1313`:

```text
public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1
rust_public_p2p_substrate_gate_status_recorded_phase_1313
public_p2p_default_off_phase_1313
public_fetch_serving_default_off_phase_1313
transport_public_path_activation_not_authorized_phase_1313
phase_1314_wallet_withdrawal_transfer_spend_preflight_next
public_rc_remains_blocked_after_phase_1313
```

Roadmap impact:

- Gap 10 now has a deterministic default-off public fetch/P2P readiness packet
  at `ilc_core/sidecars/public_fetch_p2p_readiness.py`.
- The packet records Rust QUIC/rustls source evidence from
  `ilc_consensus/src/network.rs`, but classifies the Rust public-P2P substrate
  gate as still required before any public activation.
- Python HTTP fetch/gossip runtimes remain devnet/test regression surfaces and
  are not public-P2P substrates.
- The graph-native sidecar registry now records
  `public_fetch_p2p_readiness_candidate` with no public serving.
- Public TransportPrincipal path activation remains blocked pending public
  credential issuer authority, public revocation registry, public replay cache,
  public rate-limit state, public admission and ban policy, public privacy
  policy, Rust public-P2P substrate ADR/integration evidence, and explicit
  public transport activation authority.

Phase 1313 does not authorize public P2P, public fetch serving, public
sidecar/projection serving, public credential issuer authority, credential
lifecycle policy activation for a public path, public revocation registry
activation, public replay cache activation, public rate-limit state activation,
admission policy activation for a public path, ban registry activation for a
public path, privacy policy activation for a public path, non-loopback bind,
wildcard bind, public host bind, listener, peer discovery, helper promotion,
marker removal, helper stripping, source allowlist export, clean public tree
materialization, public repository publication, public package publication,
release artifacts, release keys, release envelopes, release signing material,
CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration/signing,
v0.2 signing, wallet withdrawal, wallet transfer, wallet spend, ECU minting,
ILC settlement, public confidential messaging, or public confidential
coordination serving.

Phase 1314, Phase 1315, and Phase 1316 have now completed. Window 1303-1316 is
closed with carry-forward.
