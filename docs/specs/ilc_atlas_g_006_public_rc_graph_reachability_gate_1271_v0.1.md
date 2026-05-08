# ILC ATLAS-G-006 Public-RC Graph Reachability Gate 1271 v0.1

**Date:** 2026-05-08
**Phase:** 1271
**Status:** PASS for graph gate only; public release remains unauthorized
**Token:** `atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1`

---

## 1. Verdict

Phase 1271 records the ATLAS-G-006 public-RC graph reachability verdict for the
selected public-RC target profile:

```text
selected_profile_id=openclaw_skill_claimable
graph_reachability_verdict=pass_graph_gate_only_release_artifacts_blocked
public_rc_graph_reachability_verdict_recorded_phase_1271
public_release_artifact_not_authorized_phase_1271
no_genesis_atlas_mutation_phase_1271
```

The gate passes because the selected `openclaw_skill_claimable` profile is
public-RC eligible, includes public claimability without a public ILC P2P claim,
reaches all required `ecu`, `genesis`, `hypergraph`, and `ilc` anchors, includes
the non-excisable components, and is backed by the Phase 1254 ATLAS-G-004/005
high-authority dependency bridge.

This is not a public RC claim. Release artifact production remains unauthorized.
Genesis Atlas mutation, regeneration, or signing remains unauthorized.

---

## 2. Canon Checks and Token Audit

| Check | Result |
|-------|--------|
| Exact-token audit | Before Phase 1271 implementation, the required tokens appeared only in `docs/antigravity_tasks/antigravity_prompt__phase_1271_g8_atlas_g_006_public_rc_graph_reachability_gate.md`. They are now recorded in this artifact, walkthrough, STATUS, PLANNING_INDEX, roadmap, and code/tests. |
| Concept discovery | Searched for ATLAS-G-006, graph reachability, public RC graph, package reachability, high-authority sources, dependency bridge, Genesis Atlas, release artifact, allowlist, publication, and `graph_delta`. |
| Contradiction and non-claim search | Searched for `not authorized`, `blocked`, `no public`, `no release`, `no Genesis mutation`, `no signing`, `deferred`, `stale`, `missing graph_delta`, and `must not`. Current canon still blocks public release artifacts, public RC claim, public repository publication, Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, and public claimability activation. |
| Source expansion | Direct-read the active planning index, STATUS tail, Window 1265-1272 lock and guidance, ATLAS-G forward planning, ATLAS-G grouping, Phase 1254 bridge artifact, Phase 1247 package reachability tests/manifests, `ilc_core/rc/atlas_graph_discipline.py`, and the public-RC roadmap before recording the verdict. |

Exact-token `rg` was used only as a schema/completion check. Context discovery
used token components, synonyms, neighboring ideas, older names, code symbols,
file/path variants, and denial terms before concluding the gate state.

---

## 3. Deterministic Gate Evidence

The Phase 1271 builder is:

```text
ilc_core/rc/atlas_graph_discipline.py::build_atlas_g_006_public_rc_graph_reachability_gate
```

Gate evidence:

| Evidence | Result |
|----------|--------|
| Selected profile | `openclaw_skill_claimable` |
| Public-RC eligible | true |
| Public claimability declared | true |
| Public ILC P2P declared | false |
| Package reachability manifest status | pass |
| Required anchor set | `ecu`, `genesis`, `hypergraph`, `ilc` |
| Missing required anchors | none |
| Missing non-excisable components | none |
| Missing representative paths | none |
| Phase 1254 bridge status | pass |
| Phase 1254 high-authority classification status | pass |
| Phase 1254 dependency bridge edge count | 296 |

The gate requires these dependency edge families:

```text
high_authority_source_classified_as
package_component_reachable_from_anchor
package_profile_exports_surface
package_profile_requires_component
python_cli_entrypoint
python_surface_imports_root
rust_binary_entrypoint
rust_crate_dependency
```

The gate requires these selected-profile components:

```text
canonical_json_policy
ecu_ilc_economic_boundary
ecu_to_ilc_conversion_runtime
genesis_lineage_verification
ilc_identity_namespace
protocol_bundle_verification
public_claimability_runtime
rust_consensus_core_binding
```

The gate requires these selected-profile package surfaces:

```text
ilc_cli
ilc_harness_adapters
ilc_logic
local_sidecar
public_claimability
```

The canonical JSON export function is:

```text
ilc_core/rc/atlas_graph_discipline.py::export_atlas_g_006_public_rc_graph_reachability_gate_json
```

It uses `json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))`.

---

## 4. Non-Authorization Boundary

Phase 1271 records a graph evidence verdict only. It does not authorize:

- public release artifact production
- public RC claim
- public repository publication
- public package publication
- public ILC P2P exposure
- public sidecar/projection serving
- public claimability runtime activation
- wallet withdrawal, transfer, or spend
- ECU minting
- ILC settlement or withdrawal runtime activation
- CDL mutation
- CDL-087 ratification
- CDL-088 opening
- release-key generation
- v0.2 signing
- signed Genesis v0.1 mutation
- Genesis Atlas mutation, regeneration, or signing
- immutable diagnostic mutation
- production `commit.epoch` emission

Required boundary tokens:

```text
public_release_artifact_not_authorized_phase_1271
no_genesis_atlas_mutation_phase_1271
```

---

## 5. Open Public-RC Blockers After Phase 1271

ATLAS-G-006 is no longer the graph-reachability blocker for the selected
OpenClaw/NemoClaw claimable skill profile. Public RC remains blocked by:

- claimability runtime and conversion sweeper implementation
- CDL-087 ratification
- public sidecar/projection serving authorization
- TransportPrincipal public-path ADR and Rust M-5 hardening
- counsel/IP/publication authorization
- v0.2 signing authorization
- release manifest and allowlist publication authorization

Carry-forward token:

```text
public_rc_remains_blocked_after_phase_1271
```

---

## 6. Graph Delta

```text
graph_delta=load_bearing_code_changed:ilc_core/rc/atlas_graph_discipline.py -> hypergraph/public_rc
graph_delta=load_bearing_artifact_changed:docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.json -> hypergraph/public_rc
graph_delta=load_bearing_spec_added:docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md -> hypergraph/public_rc
graph_delta=support_tests_added:tests/test_phase_1271_atlas_g_006_public_rc_graph_reachability_gate.py -> validation
graph_delta=support_only:docs/phases/phase_1271_atlas_g_006_public_rc_graph_reachability_gate_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
