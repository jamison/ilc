# ILC Window 1225-1232 Handoff 1232 v0.1

**Phase:** 1232
**Window:** 1225-1232
**Date:** 2026-05-06
**Status:** CLOSED
**Closure verdict:** PASS

`window_1225_1232_closed_phase_1232`
`window_1225_1232_closure_gate_verdict=pass`

---

## 1. Window Outcome Summary

| Phase | Topic | Verdict | Token |
|-------|-------|---------|-------|
| 1225 | Sequence lock | PASS | `window_1225_1232_sequence_lock_committed` |
| 1226 | `commit.epoch` causal frontier mapping | PASS | `commit_epoch_causal_frontier_mapping_spec_committed_phase_1226` |
| 1226 Fix1 | Causal frontier DAG/hypergraph cut refinement | PASS | `commit_epoch_causal_frontier_mapping_spec_committed_phase_1226` |
| 1227 | CDL-087 opening | OPENED | `cdl_087_canonical_fetch_distribution_policy_opened_phase_1227` |
| 1228 | CDL-087 prelock | PRELOCKED | `cdl_087_prelock_committed_phase_1228` |
| 1229 | Agent graph projection runtime | IMPLEMENTED | `agent_graph_projection_runtime_1229.v0.1` |
| 1230 | v0.2 signing | DEFERRED | `v0_2_signing_ceremony_deferred_pending_signing_authorization` |
| 1231 | Coherence + capsule v5.49 | PASS | `capsule_v5_49_supersedes_v5_48` |
| 1232 | Closure gate | PASS | `window_1225_1232_closure_gate_verdict=pass` |

---

## 2. Constitutional / Governance State

`commit.epoch` mapping:

```text
commit_epoch_causal_frontier_mapping_spec_committed_phase_1226
commit_epoch_mapping_governed_by_cdl_051_no_new_cdl_required
commit_epoch_projection_runtime_required_before_production_emission
```

Phase 1226 consumed the Phase 1219 mapping carry-forward. Production emission runtime remains
open and must not be inferred from the mapping spec.

CDL-087 state:

```text
cdl_087_canonical_fetch_distribution_policy_opened_phase_1227
cdl_087_prelock_committed_phase_1228
cdl_087_not_ratified_phase_1228
```

CDL-087 remains:

```text
OPEN / PRELOCKED / NOT RATIFIED
```

No phantom CDL-087 ratification occurred. Ratification remains gated by SIM-FETCH-01 and all
six Phase 1228 ratification conditions.

CDL-086 remains ratified as the public-launch packaging blocker, with public-launch acts
still separately blocked:

```text
cdl_086_ratified_phase_1220
```

---

## 3. Runtime / Graph State

Phase 1229 implemented:

```text
agent_graph_projection_runtime_1229.v0.1
```

Runtime path:

```text
ilc_core/graph/agent_graph_projection_runtime.py
```

The existing graph import contract remains valid:

```python
from ilc_core.graph import EpistemicGraph
```

The Phase 1228 incentive projection carry-forward is resolved at projection level:

```text
fetch_incentive_hypergraph_slice_projection_required_phase_1229
```

The runtime exposes a named `fetch_incentive_hypergraph_slice` with distinct projection nodes
for serving-peer identity and served-Graph-Node centrality. This is a projection-layer
resolution only; production serving-peer instrumentation remains future work.

---

## 4. Fetch Distribution State

The preferred fetch-distribution direction remains:

```text
fetch_distribution_architecture_reframed_phase_1222
transport_abuse_circuit_breaker_not_final_scaling_policy
```

The reciprocal scoring formula in Phase 1222 §2 remains a non-selected research candidate,
not the preferred implementation path.

CDL-087 encodes pull-first canonical availability, verified lineage, high-centrality caching,
snapshot/mirror architecture, privacy-minimized observability, and local circuit breakers. It
does not create a universal service mandate and does not supersede CDL-077.

---

## 5. Signing / Genesis State

Signed Genesis v0.1 remains canonical and unchanged:

```text
ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c
```

Immutable diagnostic SHA confirmed:

```text
5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56
```

v0.2 signing remains deferred:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

No signing ceremony executed, no release key was generated or registered, no release envelope
was produced, Genesis Atlas remains unchanged, and v0.2 remains an unsigned 41-node / 73-edge
candidate.

---

## 6. Active Carry-Forward Obligations

The following carry forward beyond Window 1225-1232:

```text
commit_epoch_projection_runtime_required_before_production_emission
cdl_087_ratification_deferred_pending_sim_fetch_01
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
l3_sidecar_infrastructure_spec_required_window_1225_plus
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

CDL-087 ratification is not authorized by this closure.

---

## 7. PLANNING_INDEX Hygiene

Phase 1232 reviewed and updated `docs/PLANNING_INDEX.md`:

- live capsule row points to v5.49;
- Window 1225-1232 handoff is listed as the current closure handoff;
- reciprocal fetch admission remains marked as a non-selected research candidate;
- Launch Roadmap v0.9 remains marked superseded by v1.0;
- stale frontier note now points to Window 1225-1232 closed through Phase 1232.

---

## 8. Non-Claims

Window 1225-1232 did not authorize or perform:

- CDL-087 ratification;
- CDL-077 amendment;
- reciprocal scoring CDL opening;
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
- immutable diagnostic mutation.

---

## 9. Verification

Closure gate:

```bash
ILC_PHASE_1232_GATE_SELFTEST=1 .venv/bin/python -m pytest tests/test_phase_1232_window_1225_1232_closure_gate.py -q
```

Window regression:

```bash
.venv/bin/python -m pytest \
  tests/test_phase_1225_sequence_lock.py \
  tests/test_phase_1226_commit_epoch_mapping_spec.py \
  tests/test_phase_1227_cdl_087_opening.py \
  tests/test_phase_1228_cdl_087_prelock.py \
  tests/test_phase_1229_agent_graph_projection_runtime.py \
  tests/test_phase_1230_v0_2_signing_skip.py \
  tests/test_phase_1231_coherence_capsule_v5_49.py \
  tests/test_phase_1232_window_1225_1232_closure_gate.py \
  -q
```

`window_1225_1232_closed_phase_1232`
`window_1225_1232_closure_gate_verdict=pass`
