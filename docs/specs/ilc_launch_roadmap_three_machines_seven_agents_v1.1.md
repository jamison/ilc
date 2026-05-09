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
| Window frontier | Window 1281-1288 CLOSED / PASS through Phase 1288; closure handoff is `docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md`; Phase 1282 publishes Capsule v5.51, Phase 1282 Fix1 hardens local claimability/conversion helpers without public activation, Phase 1283 records `public_claimability_authority_verdict_phase_1283=no_activation_no_public_api`, Phase 1284 records `public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api`, Phase 1285 records `transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation`, Phase 1286 records `sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving`, Phase 1287 records `release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing`, and Phase 1288 records `window_1281_1288_closure_gate_verdict=pass`; Window 1289+ sequence lock required before next phase assignment |
| Capsule | v5.51 current and updated in place through Phase 1288 |
| Prior closure | Window 1233-1240 CLOSED / PASS at Phase 1240 |
| CDL-086 | **RATIFIED** in Phase 1220 (`cdl_086_ratified_phase_1220`) |
| CDL-087 | **RATIFIED** in Phase 1278 Fix1 (`cdl087_ratified_phase_1278_fix1`); public fetch serving, public sidecar/projection serving, CDL-088, and public RC remain separately gated |
| v0.2 signing | Deferred; explicit signing authorization absent |
| Tier-3 runtime linkage | **IMPLEMENTED** in Phase 1201 (`tier3_runtime_linkage_runtime_1201.v0.1`) |
| Persistent fetch rate limiter backend | **IMPLEMENTED** in Phase 1202 (`persistent_fetch_rate_limiter_runtime_1202.v0.1`) |
| Persistent limiter HTTP wiring | **WIRED** in Phase 1212 (`persistent_rate_limiter_transport_wiring_committed_phase_1212`) |
| `commit.epoch` runtime alignment | Complete through devnet E2E harness; production emission unauthorized |
| L3 sidecar query runtime | Local/read-only runtime complete; Phase 1268 records loopback/subprocess-only boundary with no new listener and Phase 1278 adds an internal public-path preflight helper while keeping public/non-loopback projection serving blocked |
| TransportPrincipal runtime identity | Phase 1267 pre-public helper implemented for authenticated credential key derivation; Phase 1277 adds an internal public-path preflight helper; no public P2P, public fetch serving, or non-loopback serving activation |
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

- The first public-RC path is a local OpenClaw/NemoClaw-compatible ILC skill or
  package profile.
- That path makes no public ILC-owned P2P claim.
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
| OpenClaw/NemoClaw local skill preview | Local harness preview only | Open execution lane in Window 1241-1248; not final public RC |
| OpenClaw/NemoClaw claimable public RC | Final selected public-RC target profile | Requires Gap 14 package modularity plus Gap 13 claimability path |

Token:

```text
public_rc_blocker_classification_required_in_roadmap_v1_1
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
| Public-RC local harness preview | Clean OpenClaw/NemoClaw local skill package; no public P2P; no final claimability claim | Window 1241-1248 execution lane |
| Public-RC claimable harness profile | Local harness package plus public ECU-to-ILC claimability; no public ILC P2P claim | Target profile, still blocked |
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

**Status:** Open hard gate before public repository publication and public RC.
Phase 1255 defines the allowlist-export procedure, but does not authorize
publication. Counsel/IP/trademark/CLA/patent gates and explicit publication
authorization remain open.

Required:

- Root license and zone table decision.
- DCO/CLA decision before external contributors.
- Trademark policy before public launch.
- US provisional patent filing before public repository publication.
- Public-source allowlist/export procedure: defined in Phase 1255, execution
  still blocked.

Tokens:

```text
counsel_license_instrument_selection_required_before_public_rc
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

**Status:** Open; Phase 1274 conversion-sweeper runtime skeleton and Phase 1275
local proof binding recorded; final public-RC claimability API/verifier
authority still open.

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

### Gap 14 - OpenClaw/NemoClaw Package Modularity and CLI/Sidecar Boundary

**Status:** Immediate Window 1241-1248 execution lane.

Package modularity must prove that ILC can be consumed as a local skill/package
without making OpenClaw/NemoClaw a protocol dependency and without letting
Genesis, ILC, ECU, canonical JSON, protocol bundle verification, or Rust
consensus-core binding become excisable.

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
