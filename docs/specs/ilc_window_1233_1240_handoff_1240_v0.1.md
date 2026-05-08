# ILC Window 1233-1240 Handoff 1240 v0.1

**Phase:** 1240
**Window:** 1233-1240
**Date:** 2026-05-08
**Status:** CLOSED
**Closure verdict:** PASS
**Human authorization:** `GO Phase 1240`

`window_1233_1240_closed_phase_1240`
`window_1233_1240_closure_gate_verdict=pass`

---

## 1. Window Identity and Closure Basis

Window 1233-1240 is closed by Phase 1240 after explicit human authorization:

```text
GO Phase 1240
```

Authoritative closure inputs:

- `docs/specs/ilc_phase_1233_1240_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1233_1240_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_coherence_report_1239_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
- `docs/phases/STATUS.md`
- `docs/PLANNING_INDEX.md`

Closure verdict:

```text
window_1233_1240_closure_gate_verdict=pass
```

---

## 2. Inputs and Closure Inheritance

| Phase | Topic | Verdict | Token |
|-------|-------|---------|-------|
| 1233 | Sequence lock | PASS | `window_1233_1240_sequence_lock_committed` |
| 1234 | `commit.epoch` audit and mutation plan | PASS | `commit_epoch_audit_complete_phase_1234` |
| 1235 | `commit.epoch` canonical runtime mutation | PASS | `commit_epoch_canonical_constructor_phase_1235.v0.1` |
| 1236 | `commit.epoch` emission connector | PASS / NOT PRODUCTION-AUTHORIZED | `commit_epoch_emission_runtime_1236.v0.1` |
| 1236 Fix1-Fix6 | connector spec, quorum projection, causal frontier, finalized adapter, Rust fixture mapping, devnet E2E harness | PASS / NOT PRODUCTION-AUTHORIZED | `phase_1236_fix6_devnet_end_to_end_harness_complete` |
| 1237 | L3 sidecar infrastructure spec | PASS | `l3_sidecar_infrastructure_spec_committed_phase_1237` |
| 1237 Fix1-Fix7 | local read-only sidecar query runtime | PASS / LOCAL ONLY | `l3_sidecar_query_runtime_strike_force_complete_phase_1237` |
| 1237 Post-Fix7 | sidecar runtime audit hardening | PASS | `phase_1237_post_fix7_sidecar_audit_hardening_complete` |
| 1238-1238j | SIM-FETCH-01 harness and Fix1-Fix10 evidence suite | PASS / CDL-087 NOT RATIFIED | `sim_fetch_01_fix10_robustness_suite_1238j.v0.1` |
| 1239 | coherence report and capsule v5.50 | PASS | `capsule_v5_50_supersedes_v5_49` |
| 1240 | closure gate | PASS | `window_1233_1240_closure_gate_verdict=pass` |

---

## 3. Closure Verdict Summary

Closed in this window:

- `commit.epoch` canonical runtime conflict: canonical payload path no longer carries
  wall-clock `created_at`.
- `vote_weight` float issue in the audited finality/circuit-breaker/epoch-state surfaces.
- `commit.epoch` connector stack through quorum projection, causal-frontier projection,
  finalized adapter, Rust fixture mapping, and devnet E2E harness.
- L3 sidecar infrastructure spec and local read-only sidecar query runtime.
- SIM-FETCH-01 harness through Fix10, including routed holder model, multi-hop retry,
  adaptive heat replication, CDL-078 credit bridge, Werner overlay, AutoResearch
  evidence matrix, and robustness suite.
- Context capsule v5.50 and coherence report 1239.

Still explicitly deferred:

```text
commit_epoch_projection_runtime_required_before_production_emission
commit_epoch_production_emission_not_yet_authorized
cdl_087_ratification_deferred_pending_sim_fetch_01
v0_2_signing_ceremony_deferred_pending_signing_authorization
sidecar_projection_endpoint_required_post_cdl_087_ratification
```

CDL-087 remains:

```text
OPEN / PRELOCKED / NOT RATIFIED
cdl_087_candidate_envelope_identified_not_ratified_phase_1238j
```

No phantom CDL-087 ratification occurred. Phase 1238j provides evidence for future
governance review; it does not ratify the CDL.

---

## 4. Carry-Forward Items and Residual Blockers

### 4.1 Window 1241+ public-RC planning

Roadmap v1.1 is required as the next controlling public-RC roadmap:

```text
launch_roadmap_v1_1_refresh_required_after_phase_1240
public_rc_blocker_classification_required_in_roadmap_v1_1
```

Window 1241+ is not opened by this handoff. Exact phases require a future sequence lock.

### 4.2 OpenClaw/NemoClaw-first public RC path

The default public-RC path remains OpenClaw/NemoClaw skill-first, without a public ILC-owned
P2P claim. Gap 14 should run before Gap 10 on this path:

```text
openclaw_skill_local_profile_is_preview_only
openclaw_skill_claimable_profile_is_final_public_rc_target
```

Open implementation work:

- import-boundary enforcement for `ilc_logic` / OpenClaw skill packaging;
- harness adapter protocol stubs;
- dependency-isolated package profile tests;
- packaging CI gate;
- claimable profile wiring once Gap 13 closes.

### 4.3 Public economic path

The public-RC economic path still requires public claimability:

```text
ecu_to_ilc_conversion_runtime_required_before_public_claimability
public_claimability_substrate_required_before_public_rc_claim
```

Wallet-visible balances and internal conversion planning are not sufficient for final public RC.

### 4.4 Transport and public exposure

Public P2P and non-loopback sidecar/projection exposure remain blocked until authenticated
transport principal work lands:

```text
transport_principal_required_before_public_p2p
sidecar_projection_endpoint_requires_transport_principal_if_non_loopback
```

Python HTTP gossip/fetch transports remain devnet/test oriented until a future public-P2P
ADR and implementation decision.

### 4.5 ATLAS-G and homoiconic graph discipline

ATLAS-G work remains planning-only but registered:

```text
atlas_graph_integrated_phase_discipline_forward_planning_recorded_phase_1238
atlas_g_1241_plus_candidate_phase_grouping_recorded_phase_1238
atlas_g_prompt_drafts_registered_phase_1238
```

The next window should decide whether ATLAS-G runs as a parallel strike-force lane or as
integrated phase-close gates. The currently preferred discipline is integrated phase-close
graph delta fields plus targeted ATLAS-G strike-force phases.

### 4.6 Dirty generated artifacts

Closure verified the committed immutable diagnostic anchor at `HEAD`:

```text
5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56
```

At closure preflight, the working-tree copy of `out/genesis_compile_coverage_diagnostic_v0.1.json`
had digest:

```text
f3235a8f9dcc88d3544f9cacf3f78b29caf17d50686dd46611783c225f0eff3a
```

Those generated working-tree edits were pre-existing and were not staged into this closure
commit. They must be reconciled explicitly in the ATLAS-G / Genesis graph lane before any
future signing, public-RC graph gate, or v0.2 candidate claim. This closure does not claim
working-tree generated artifact cleanliness.

### 4.7 Counsel and release blockers

Still open:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
us_provisional_patent_application_filed
```

---

## 5. Next-Window Entry Criteria and Routing

The next valid window must begin with a new sequence lock. This handoff recommends the
first Window 1241+ work band:

1. Publish Roadmap v1.1 as the new controlling public-RC roadmap and tombstone v1.0 as
   superseded.
2. Start Gap 14 package modularity implementation: import-boundary enforcement, adapter
   protocol stubs, and package-profile CI.
3. Decide CDL-087 governance routing using Phase 1238j evidence.
4. Start ATLAS-G graph discipline if selected by the new sequence lock.
5. Route Gap 13 public claimability and Gap 10 TransportPrincipal into separate
   implementation lanes.

No Window 1241+ phase is opened here. No public release or production network surface is
authorized here.

---

## 6. MemPalace Refresh Disposition

**Disposition:** `required`
**Active working set impacted:** `yes`
**Basis:** Window 1233-1240 changed the active frontier materially: `commit.epoch`
runtime alignment, sidecar query runtime, SIM-FETCH-01 evidence, OpenClaw-first public-RC
planning, ATLAS-G graph discipline, and capsule v5.50 are now live repo canon. The next
sequence lock should refresh the active working set before assigning Window 1241+ phases.

**Working-set descriptor:** `docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`
**Manifest:** `docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json`
**Rebuild command:** `bash tools/mempalace/build_active_working_set.sh`

MemPalace remains advisory. Current canon remains repo source: PLANNING_INDEX, STATUS,
capsule v5.50, this handoff, the sequence locks, the CDL register, and committed tests.

---

## 7. Non-Claims

Window 1233-1240 did not authorize or perform:

- CDL-087 ratification;
- CDL-088 opening;
- CDL-077 amendment;
- production `commit.epoch` emission;
- sidecar projection endpoint implementation;
- public sidecar/projection serving;
- public P2P exposure;
- TransportPrincipal implementation;
- ECU mint authorization;
- ILC settlement authorization;
- public launch;
- public RC claim;
- public repository publication;
- public release artifact distribution;
- external contributor onboarding;
- external operator bootstrap;
- v0.2 signing;
- release-key generation;
- release envelope production;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation;
- committed immutable diagnostic mutation.

---

## 8. Verification

Closure gate:

```bash
ILC_PHASE_1240_GATE_SELFTEST=1 .venv/bin/python -m pytest tests/test_phase_1240_window_1233_1240_closure_gate.py -q
```

Window-focused regression:

```bash
.venv/bin/python -m pytest \
  tests/test_phase_1233_sequence_lock.py \
  tests/test_phase_1234_commit_epoch_audit.py \
  tests/test_phase_1235_commit_epoch_canonical_mutation.py \
  tests/test_phase_1236_commit_epoch_emission_connector.py \
  tests/test_phase_1236_fix1_commit_epoch_full_connector_spec.py \
  tests/test_phase_1236_fix2_commit_epoch_quorum_projection.py \
  tests/test_phase_1236_fix3_commit_epoch_causal_frontier_projection.py \
  tests/test_phase_1236_fix4_commit_epoch_finalized_adapter.py \
  tests/test_phase_1236_fix5_rust_fixture_mapping.py \
  tests/test_phase_1236_fix6_devnet_end_to_end_harness.py \
  tests/test_phase_1237_l3_sidecar_spec.py \
  tests/test_phase_1237_sidecar_query_runtime.py \
  tests/test_phase_1237_fix2_ego_graph_query.py \
  tests/test_phase_1237_fix3_centrality_metrics.py \
  tests/test_phase_1237_fix4_convergence_trace.py \
  tests/test_phase_1237_fix5_dispatcher_integration.py \
  tests/test_phase_1237_fix6_canonical_export_bundle.py \
  tests/test_phase_1237_fix7_sidecar_local_smoke_harness.py \
  tests/test_phase_1237_post_fix7_sidecar_audit_hardening.py \
  tests/test_phase_1238_sim_fetch_01_harness.py \
  tests/test_phase_1238a_sim_fetch_01_fix1_hardening.py \
  tests/test_phase_1238b_sim_fetch_01_fix2_request_model.py \
  tests/test_phase_1238c_sim_fetch_01_fix3_tier_verdict.py \
  tests/test_phase_1238d_sim_fetch_01_fix4_routed_holder_model.py \
  tests/test_phase_1238e_sim_fetch_01_fix5_routed_multihop_retry.py \
  tests/test_phase_1238f_sim_fetch_01_fix6_adaptive_heat_replication.py \
  tests/test_phase_1238g_sim_fetch_01_fix7_cdl_078_credit_bridge.py \
  tests/test_phase_1238h_sim_fetch_01_fix8_werner_overlay.py \
  tests/test_phase_1238i_sim_fetch_01_fix9_cdl_087_evidence_matrix.py \
  tests/test_phase_1238j_sim_fetch_01_fix10_robustness_suite.py \
  tests/test_phase_1239_coherence_capsule_v5_50.py \
  tests/test_phase_1240_window_1233_1240_closure_gate.py \
  -q
```

`window_1233_1240_closed_phase_1240`
`window_1233_1240_closure_gate_verdict=pass`
