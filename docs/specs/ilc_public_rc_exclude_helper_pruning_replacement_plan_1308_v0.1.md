# ILC PUBLIC_RC_EXCLUDE Helper Pruning Replacement Plan 1308 v0.1

**Date:** 2026-05-11
**Phase:** 1308, Window 1303-1316
**Status:** Helper disposition inventory and truth-primitive sidecar boundary
recorded; no source export, no helper stripping, no marker removal, and no
helper promotion.

```text
public_rc_exclude_helper_pruning_replacement_plan_phase_1308.v0.1
public_rc_exclude_helper_disposition_inventory_recorded_phase_1308
truth_primitive_sidecar_boundary_recorded_phase_1308
helper_stripping_not_executed_phase_1308
source_allowlist_export_not_executed_phase_1308
phase_1309_transport_principal_admission_sidecar_lifecycle_next
public_rc_remains_blocked_after_phase_1308
```

## 1. Verdict

Phase 1308 converts the Phase 1293 keep-internal register into an executable
disposition inventory at:

```text
ilc_core/rc/public_rc_exclude_disposition.py
```

Every current runtime helper carrying the internal launch-surface marker remains
internal. The Phase 1308 disposition for each helper is
`replace_before_export`: a public-safe module or sidecar boundary must replace
the internal scaffold before any public source, package, or release export can
claim the affected functionality.

This is a planning and hardening phase only. It does not materialize a public
tree, execute source allowlist export, strip helpers from an exported tree,
remove markers, promote helpers, publish a package, produce release artifacts,
generate release keys or envelopes, activate public claimability, activate
public P2P/fetch/sidecar serving, mutate Genesis, sign v0.2, open CDL-088,
authorize wallet withdrawal/transfer/spend, authorize ECU minting, or authorize
ILC settlement.

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Verified Phase 1308 tokens against the prompt, PLANNING_INDEX, Capsule v5.53, STATUS tail, sequence lock, and planning tests. Before this phase, the Phase 1308 tokens existed only in the prompt/test scaffolding. |
| Section 0b Concept-discovery search | Searched `PUBLIC_RC_EXCLUDE`, `internal_phase_helper`, helper promotion/removal/stripping, `replace_before_export`, `strip_from_export`, `defer_public_rc`, truth primitive terms, source allowlist, and public-tree terms. |
| Section 0c Contradiction and non-claim search | Searched not-authorized, not-enabled, no-export, no-publication, no-marker-removal, no-helper-promotion, fail-closed, legacy-public, and public-RC-clean terms. |
| Section 0d Source expansion | Direct-read the four runtime helpers, Phase 1293 helper register, Phase 1294 allowlist rehearsal, Phase 1301 no-activation audit, Phase 1255 allowlist export procedure, public-RC packaging architecture gate, graph-native sidecar suite architecture, Capsule v5.53, and the Phase 1303 sequence lock. |

Discovery outcome: the runtime helper inventory is four files. Many docs mention
`PUBLIC_RC_EXCLUDE`, but those references are not all helper markers. They
remain governed by the Phase 1255 exclude-by-default and legacy-review rules.

## 3. Helper Disposition Inventory

| Helper | Phase 1308 disposition | Replacement boundary | Follow-up route |
|--------|------------------------|----------------------|-----------------|
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | `replace_before_export` | Public-safe claimability receipt contract. | Value-path preflight in 1314/1315 before any 1333 export gate. |
| `ilc_core/ledger/claimability_proof_binding_runtime.py` | `replace_before_export` | Offline claimability receipt verifier sidecar and later public verifier contract. | 1305/1306 verifier substrate plus later 1314/1333 gates. |
| `ilc_core/network/d2d/transport_principal_public_path_preflight.py` | `replace_before_export` | TransportPrincipal admission sidecar. | 1309/1310 lifecycle and hostile-network tests before any 1313/1333 public-path/export gate. |
| `ilc_core/graph/sidecar_public_path_preflight.py` | `replace_before_export` | Local graph/memory projection sidecar with public-safe projection contract. | 1311/1312 projection/privacy work before any 1333 export gate. |

All four helpers retain:

```text
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

No helper receives `strip_from_export` execution in Phase 1308 because no public
tree exists to strip. No helper receives `defer_public_rc` as its primary Phase
1308 disposition because the current best plan is to replace each helper before
the relevant public export/profile gate. If a later replacement fails or remains
incomplete, the affected profile must become `defer_public_rc` at the dry-run or
execution gate.

## 4. Truth-Primitive Sidecar Boundary

Phase 1308 records the local truth-primitive sidecar boundary as graph-native
replacement infrastructure:

```text
truth_primitive_sidecar_boundary_recorded_phase_1308
```

The boundary consumes the existing ratified truth primitive submission runtime:

```text
ilc_core/epistemic/truth_primitive_submission_runtime.py
```

Agent-issuable primitives are:

```text
assert.truth
validate.claim
contradict.assert
refute.claim
revise.assert
link.claim
```

`commit.epoch` remains consensus-layer only and is rejected for agent
submission. The boundary is local-only by default: in-process import or local
CLI subprocess. It does not authorize graph persistence, network delivery,
public API serving, public sidecar serving, source export, public confidential
messaging, or public confidential coordination serving.

The Phase 1307 sidecar registry is updated so
`truth_primitive_submission_boundary` records:

```text
truth_primitive_sidecar_boundary_recorded_phase_1308
```

## 5. Document And Legacy Policy

Phase 1308 records these public-tree materialization rules in executable
metadata:

| Policy | Default disposition |
|--------|---------------------|
| Files carrying `PUBLIC_RC_EXCLUDE` | `strip_from_export` unless a later explicit gate removes or supersedes the marker before materialization. |
| `docs/phases/` and `docs/antigravity_tasks/` | `strip_from_export` by default as private execution history. |
| `docs/research/` | `strip_from_export` by default unless counsel/publication review later allowlists a specific file. |
| Untagged legacy docs | `defer_public_rc` / review-required; absence of `PUBLIC_RC_EXCLUDE` is not allowlist clearance. |

This preserves the Phase 1255 rule: `PUBLIC_RC_EXCLUDE` is a deny marker, not
an allowlist signal, and untagged legacy material is not automatically public.

## 6. Non-Export Proof

The executable inventory records:

```text
helper_stripping_not_executed_phase_1308
source_allowlist_export_not_executed_phase_1308
```

The machine state keeps these flags false:

| Flag | Phase 1308 value |
|------|------------------|
| `source_allowlist_export_executed` | `false` |
| `clean_public_tree_materialized` | `false` |
| `helper_promotion_authorized` | `false` |
| `marker_removal_authorized` | `false` |
| `helper_stripping_executed` | `false` |
| `public_rc_claimed` | `false` |

The next materialization checkpoints remain Phase 1319 dry-run and Phase 1333
execution gate if later explicitly authorized.

## 7. Public-RC Impact

Phase 1308 narrows the packaging blocker by making helper disposition explicit,
but it does not close public RC.

Still-open blockers include:

- public claimability verifier/API serving authority;
- replay/nullifier and duplicate-claim registry policy;
- public-safe disclosure and projection privacy implementation;
- TransportPrincipal admission sidecar lifecycle and hostile-network tests;
- Rust public-P2P substrate/integration before any activation-style public path;
- source allowlist export dry run and clean public tree materialization;
- counsel/license/CLA/trademark/IP/publication clearance;
- release artifacts, release keys, release envelopes, Genesis/v0.2 signing;
- wallet withdrawal/transfer/spend, ECU minting, and ILC settlement.

Public RC remains blocked:

```text
public_rc_remains_blocked_after_phase_1308
```

The next planned phase is:

```text
phase_1309_transport_principal_admission_sidecar_lifecycle_next
```

Phase 1309 is sensitive and requires explicit `GO Phase 1309`.

## 8. Non-Claims

Phase 1308 makes no public RC claim, no public launch claim, no source allowlist
export claim, no clean public tree claim, no public repository publication
claim, no public package publication claim, no release artifact claim, no
release-key claim, no release-envelope claim, no helper promotion claim, no
marker removal claim, no helper stripping claim, no public claimability API
activation claim, no public verifier service claim, no public claim endpoint
claim, no public P2P/fetch serving claim, no public sidecar/projection serving
claim, no non-loopback bind claim, no Genesis mutation or signing claim, no
v0.2 signing claim, no CDL mutation claim, no CDL-088 opening claim, no wallet
withdrawal claim, no wallet transfer claim, no wallet spend claim, no ECU
minting claim, no ILC settlement claim, no public confidential messaging claim,
and no public confidential coordination serving claim.

## 9. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/rc/public_rc_exclude_disposition.py -> package/public_rc/helper-disposition
graph_delta=load_bearing_code_changed:ilc_core/sidecars/registry_manifest.py -> graph-native-sidecars/truth-boundary
graph_delta=load_bearing_spec_added:docs/specs/ilc_public_rc_exclude_helper_pruning_replacement_plan_1308_v0.1.md -> package/public_rc/helper-disposition
graph_delta=support_tests_added:tests/test_phase_1308_public_rc_exclude_helper_pruning_replacement_plan.py -> validation
graph_delta=support_only:docs/phases/phase_1308_public_rc_exclude_helper_pruning_replacement_plan_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.53.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md -> package/public_rc
graph_delta=support_only:docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md -> graph-native-sidecars
```
