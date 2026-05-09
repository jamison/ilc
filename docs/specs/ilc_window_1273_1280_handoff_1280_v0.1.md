# ILC Window 1273-1280 Handoff 1280 v0.1

Status: handoff artifact
Date: 2026-05-09
Classification: closure and carry-forward handoff
Window: 1273-1280
Closure phase: 1280
Closure verdict: pass
Human authorization: `GO Phase 1280`

Required closure tokens:

```text
window_1273_1280_closed_phase_1280
window_1273_1280_closure_gate_verdict=pass
phase_1280_window_1273_1280_closure_complete
window_1281_plus_sequence_lock_required_before_next_phase_assignment
public_rc_remains_blocked_after_phase_1280
```

## 1. Window identity and closure basis

Phase 1280 closes Window 1273-1280 with a scoped pass verdict. The pass verdict
means the locked window work is coherently recorded, tested, and handed off. It
does not mean public RC, public launch, public source publication, public P2P,
public sidecar/projection serving, public claimability, release artifacts, v0.2
signing, or Genesis Atlas mutation are authorized.

The closure consumes:

| Input | Path | Closure role |
|-------|------|--------------|
| Planning index | `docs/PLANNING_INDEX.md` | Current frontier and session-start routing |
| Current capsule | `docs/specs/ilc_antigravity_context_capsule_v5.50.md` | Latest published capsule; superseded locally on CDL-087 by Phase 1278 Fix1 |
| Status tail | `docs/phases/STATUS.md` | Phase frontier and actual phase completion order |
| Window guidance | `docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md` | Planned 1273-1280 scope and exit criteria |
| Sequence lock | `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md` | Executed window order and carry-forward addenda |
| Roadmap | `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Controlling public-RC blocker map |

Discovery discipline at closure remained the same as the window prompts:
exact-token `rg` checks were treated as schema checks only, and concept searches
also covered token components, older terms, adjacent concepts, denial language,
and contradictory public-activation claims.

## 2. Inputs and closure inheritance

The closure inherits the following completed phase packets:

| Phase | Packet | Status at closure |
|-------|--------|-------------------|
| 1273 | `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md` | Sequence lock closed for this window. |
| 1274 | `docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md` | Local conversion-sweeper runtime skeleton recorded; public claimability not activated. |
| 1275 | `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md` | Local proof/root/receipt binding recorded; public claimability API remains blocked. |
| 1276 | `docs/specs/ilc_cdl087_ratification_authorization_preflight_1276_v0.1.md` | CDL-087 authorization preflight closed; no mutation by default. |
| 1277 | `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md` | Internal `PUBLIC_RC_EXCLUDE` TransportPrincipal public-path helper recorded; public P2P blocked. |
| 1278 | `docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md` | Internal `PUBLIC_RC_EXCLUDE` sidecar public-path helper recorded; public serving blocked. |
| 1278 Fix1 | `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md` | CDL-087 ratified and the CDL register mutated under explicit human authorization. |
| 1279 | `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md` | Release manifest/source allowlist prepublication inventory recorded; publication blocked. |
| 1280 | `docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md` | Closure gate passed and Window 1281+ sequence lock required. |

## 3. Closure verdict summary

| Phase | Scope | Closure disposition |
|-------|-------|---------------------|
| 1273 | Sequence lock | Closed. Window order, sensitive gates, and non-authorization boundaries were locked. |
| 1274 | CDL-048 conversion-sweeper runtime skeleton | Closed for local runtime skeleton only. No public claimability, wallet withdrawal, transfer, spend, ECU minting, or ILC settlement. |
| 1275 | Claimability proof-binding runtime boundary | Closed for local proof binding only. No non-loopback claimability API or public claimability activation. |
| 1276 | CDL-087 authorization preflight | Closed as evidence-ready preflight. It did not mutate the CDL register by default. |
| 1277 | TransportPrincipal public-path preflight | Closed as internal helper only. Public P2P and non-loopback projection remain blocked. |
| 1278 | Sidecar non-loopback/public projection preflight | Closed as internal helper only. Public sidecar/projection serving remains blocked. |
| 1278 Fix1 | CDL-087 ratification | Closed. Explicit human authorization ratified CDL-087 and mutated only the CDL-087 register row. |
| 1279 | Release manifest/source allowlist prepublication | Closed as inventory/procedure preflight only. No source export, publication, release artifacts, release keys, release envelopes, Genesis Atlas mutation, or v0.2 signing. |
| 1280 | Closure gate | Passed. Window 1273-1280 is closed and Window 1281+ requires a new sequence lock before further phase assignment. |

## 4. Claimability and CDL-048 status

Relevant tokens:

```text
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
ecu_lot_deadline_epoch_enforcement_recorded_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
```

The window materially improved the claimability lane by recording local exact
conversion-sweeper accounting and local proof binding across settled runtime
root, wallet-state root, balance receipt, history digest, epoch id, canonical
agent identity, and conversion receipt semantics. The closing condition for the
window is satisfied because the runtime/proof boundary is explicit and tested.

The public claimability closing condition remains open. A later phase must
authorize and implement the public verifier/API authority before any public-RC
claimability statement can be made.

## 5. CDL-087 status

Relevant tokens:

```text
cdl087_ratification_evidence_phase_1278_fix1.v0.1
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

CDL-087 is now ratified. The register mutation was explicitly authorized by the
human in Phase 1278 Fix1 and was limited to the CDL-087 row. That clears the
governance blocker for the canonical fetch distribution policy, but it does not
activate public fetch serving, public sidecar/projection serving, public P2P,
public RC, CDL-088, release publication, or v0.2 signing.

## 6. TransportPrincipal, sidecar, and public-path status

Relevant tokens:

```text
transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1
transport_principal_public_p2p_not_activated_phase_1277
requester_id_fallback_still_forbidden_phase_1277
non_loopback_projection_still_blocked_phase_1277
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
sidecar_public_serving_not_enabled_phase_1278
transport_principal_and_cdl087_required_before_public_projection_phase_1278
no_new_public_listener_phase_1278
non_loopback_bind_not_enabled_phase_1278
public_projection_endpoint_not_enabled_phase_1278
sidecar_projection_privacy_review_required_phase_1278
```

Phases 1277 and 1278 added internal preflight helpers marked `PUBLIC_RC_EXCLUDE`
so the team can validate future public-path records without accidentally
shipping them as public-RC surfaces. They deliberately reject public activation
flags and preserve fail-closed boundaries.

Public-path work still needs explicit authorization for TransportPrincipal
activation, public sidecar/projection serving, privacy review, replay/revocation
policy, public-P2P hostile-network hardening, and release packaging.

## 7. Release, publication, and signing status

Relevant tokens:

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

Phase 1279 created a prepublication inventory that binds the Phase 1213 release
manifest/checklist schemas, Phase 1255 source allowlist procedure, Phase 1271
ATLAS-G-006 graph reachability pass, and Phase 1278 Fix1 CDL-087 ratification.
It did not execute publication or release production.

Public RC remains blocked after Phase 1280:

```text
public_rc_remains_blocked_after_phase_1280
public_rc_remains_blocked_after_phase_1279
public_rc_remains_blocked_after_phase_1278_fix1
```

## 8. Exit criteria reconciliation

The Window 1273-1280 guidance exit criteria are reconciled as follows:

| Exit criterion | Phase evidence | Closure result |
|----------------|----------------|----------------|
| Sequence lock exists | Phase 1273 | Satisfied. |
| Claimability/conversion-sweeper status recorded | Phases 1274-1275 | Satisfied for local runtime/proof boundary; public activation remains open. |
| Proof/root binding status recorded | Phase 1275 | Satisfied. |
| CDL-087 ratification/no-ratification explicit | Phase 1278 Fix1 | Satisfied. CDL-087 is ratified. |
| TransportPrincipal status recorded | Phase 1277 | Satisfied. Public activation remains open. |
| Sidecar status recorded | Phase 1278 | Satisfied. Public serving remains open. |
| Release manifest/source allowlist status recorded | Phase 1279 | Satisfied as inventory/prepublication only. |
| Public-RC blockers honestly classified | Phase 1280 | Satisfied; public RC remains blocked. |

## 9. Carry-forward items and residual blockers

Closed inside Window 1273-1280:

- Window 1273-1280 sequence lock.
- CDL-048 conversion-sweeper local runtime skeleton.
- Claimability proof-binding local runtime boundary.
- CDL-087 evidence readiness and explicit ratification/register mutation.
- TransportPrincipal public-path preflight helper boundary.
- Sidecar public-path preflight helper boundary.
- Release manifest/source allowlist prepublication inventory.
- Window closure and blocker classification.

Carried forward:

- Public claimability verifier/API authority and public claimability activation.
- Wallet withdrawal, transfer, spend, wallet signing authority, and wallet ledger-write authority.
- Public sidecar/projection serving authorization, non-loopback bind, listener, peer discovery, and privacy review.
- TransportPrincipal public-path activation, lifecycle, revocation, replay, admission, and public-P2P policy.
- Rust M-5/public-P2P hostile-network hardening.
- Counsel/license/CLA/trademark/patent/publication authorization.
- Source allowlist export execution, public source publication, release artifacts, release keys, and release envelopes.
- Genesis Atlas mutation/regeneration/signing and v0.2 signing authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- ECU minting, ILC settlement, and withdrawal runtime activation.
- Capsule refresh after Phase 1278 Fix1 and this closure, because v5.50 remains the latest published capsule but is stale on CDL-087.

## 10. Next-window entry criteria and routing

No additional phase should be assigned from Window 1273-1280. The next window
must begin with a new sequence lock:

```text
window_1281_plus_sequence_lock_required_before_next_phase_assignment
```

Recommended Window 1281+ routing:

- Publish a new sequence lock that consumes this handoff and keeps public RC blocked until explicitly authorized.
- Refresh the current context capsule so CDL-087 ratification and Window 1273-1280 closure are no longer only planning-index supersessions over v5.50.
- Decide the next narrow public-claimability activation slice or explicitly defer it.
- Continue sidecar/public-path work only after TransportPrincipal/public serving/privacy authority is explicit.
- Keep release/publication/signing work as prepublication until counsel, source export, release key/envelope, and v0.2 signing authority are explicit.

## 11. MemPalace refresh disposition

Disposition: required

Active working set impacted: yes

Recommended command:

```bash
bash tools/mempalace/build_active_working_set.sh
```

This is an advisory recall refresh only. Direct repo reads remain authoritative.

## 12. Non-authorization boundary

Phase 1280 does not authorize:

- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- source allowlist export execution;
- public release artifact production;
- release key generation;
- release envelope production;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback sidecar/projection serving;
- public projection endpoint serving;
- public claimability API activation;
- wallet withdrawal, transfer, or spend;
- wallet signing or ledger-write authority;
- ECU minting;
- ILC settlement or withdrawal runtime;
- CDL mutation beyond the already authorized Phase 1278 Fix1 CDL-087 row;
- CDL-088 opening;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission authorization.

## 13. Graph delta

```text
graph_delta=support_only:docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1280_window_1273_1280_closure_gate_walkthrough.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1280_window_1273_1280_closure_gate.py -> validation
```
