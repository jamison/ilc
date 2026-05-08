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
| Window frontier | Window 1265-1272 OPEN / PASS through Phase 1267; current sequence lock is `docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md` |
| Capsule | v5.50 current |
| Prior closure | Window 1233-1240 CLOSED / PASS at Phase 1240 |
| CDL-086 | **RATIFIED** in Phase 1220 (`cdl_086_ratified_phase_1220`) |
| CDL-087 | OPEN / PRELOCKED / NOT RATIFIED; Phase 1266 sensitive review recorded no-ratification/no-register-mutation |
| v0.2 signing | Deferred; explicit signing authorization absent |
| Tier-3 runtime linkage | **IMPLEMENTED** in Phase 1201 (`tier3_runtime_linkage_runtime_1201.v0.1`) |
| Persistent fetch rate limiter backend | **IMPLEMENTED** in Phase 1202 (`persistent_fetch_rate_limiter_runtime_1202.v0.1`) |
| Persistent limiter HTTP wiring | **WIRED** in Phase 1212 (`persistent_rate_limiter_transport_wiring_committed_phase_1212`) |
| `commit.epoch` runtime alignment | Complete through devnet E2E harness; production emission unauthorized |
| L3 sidecar query runtime | Local/read-only runtime complete; Phase 1261 keeps public/non-loopback projection serving blocked |
| TransportPrincipal runtime identity | Phase 1267 pre-public helper implemented for authenticated credential key derivation; no public P2P or non-loopback serving activation |
| SIM-FETCH-01 | Evidence complete through Fix10 robustness suite; CDL-087 not ratified |

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

Tokens:

```text
werner_flow_governor_cdl_opening_prelock_decision_phase_1263.v0.1
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
direct_werner_ecu_creation_rejected_phase_1263
phase_1263_sensitive_cdl_gate_complete
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

**Status:** Open; final public-RC hard requirement.

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
```

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
- CDL-087 remains open/prelocked/not ratified.
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
- CDL-087 remains open/prelocked/not ratified. Phase 1260 readiness is only:
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

- CDL-087 remains open/prelocked/not ratified after Phase 1266.
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
