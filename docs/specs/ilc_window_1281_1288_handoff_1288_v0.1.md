# ILC Window 1281-1288 Handoff 1288 v0.1

Status: handoff artifact
Date: 2026-05-09
Classification: closure and carry-forward handoff
Window: 1281-1288
Closure phase: 1288
Closure verdict: pass
Human authorization: `GO Phase 1285-1288`

Required closure tokens:

```text
window_1281_1288_closed_phase_1288
window_1281_1288_closure_gate_verdict=pass
phase_1288_window_1281_1288_closure_complete
window_1289_plus_sequence_lock_required_before_next_phase_assignment
public_rc_remains_blocked_after_phase_1288
```

## 1. Window identity and closure basis

Phase 1288 closes Window 1281-1288 with a scoped pass verdict. The pass verdict
means the locked window work is coherently recorded, tested, and handed off. It
does not mean public RC, public launch, public claimability, public verifier/API
serving, TransportPrincipal public-path activation, public sidecar/projection
serving, source publication, release artifacts, release keys, release envelopes,
Genesis Atlas mutation/signing, v0.2 signing, wallet economics, ECU minting, or
ILC settlement are authorized.

The closure consumes:

| Input | Path | Closure role |
|-------|------|--------------|
| Planning index | `docs/PLANNING_INDEX.md` | Current frontier and session-start routing |
| Current capsule | `docs/specs/ilc_antigravity_context_capsule_v5.51.md` | Current in-place capsule through Phase 1288 closure |
| Status tail | `docs/phases/STATUS.md` | Phase frontier and actual phase completion order |
| Window guidance | `docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md` | Planned 1281-1288 scope and closure criteria |
| Sequence lock | `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md` | Executed window order and sensitive-gate basis |
| Prior handoff | `docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md` | Baseline blocker inheritance |
| Roadmap | `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Controlling public-RC blocker map |
| CDL register | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-087 ratified and CDL-088 not opened |

Discovery discipline at closure remained the same as the window prompts:
exact-token `rg` checks were treated as schema checks only, and concept searches
also covered token components, older terms, adjacent concepts, denial language,
and contradictory public-activation claims.

## 2. Canon checks and token audit

| Check | Closure result |
|-------|----------------|
| §0a Known-token audit | Required Phase 1288 tokens were present in the Phase 1288 prompt and are now recorded in this handoff, PLANNING_INDEX, STATUS, roadmap, capsule, walkthrough, and focused tests. |
| §0b Concept-discovery search | Searched Window 1281, capsule, claimability, verifier, API, TransportPrincipal, sidecar, publication, release, v0.2 signing, CDL-088, public RC, and Phases 1281 through 1288. |
| §0c Contradiction and non-claim search | Searched blocked, deferred, not authorized, not enabled, local-only, PUBLIC_RC_EXCLUDE, no public, no listener, no release, no signing, no mutation, and superseded. No source granted public activation, publication, signing, Genesis mutation, CDL-088 opening, or public-RC claim authority. |
| §0d Source expansion and newly discovered tokens | Direct-read the planning index, capsule v5.51, STATUS tail, sequence lock, Phase 1282 through Phase 1287 packets, prior handoff, roadmap, and CDL register. New closure tokens are the required Phase 1288 tokens listed above. |

## 3. Inputs and closure inheritance

The closure inherits the following completed phase packets:

| Phase | Packet | Status at closure |
|-------|--------|-------------------|
| 1281 | `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md` | Sequence lock executed for this window. |
| 1282 | `docs/specs/ilc_antigravity_context_capsule_v5.51.md` | Capsule v5.51 published and then updated in place through closure. |
| 1282 Fix1 | `docs/phases/phase_1282_fix1_claimability_runtime_audit_hardening_walkthrough.md` | Local claimability/conversion hardening recorded; no public activation. |
| 1283 | `docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md` | Public claimability authority preflight closed with no activation and no public API. |
| 1284 | `docs/specs/ilc_public_claimability_verifier_api_boundary_preflight_1284_v0.1.md` | Claimability verifier/API boundary closed as internal-only with no public API. |
| 1285 | `docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md` | TransportPrincipal public-path activation preflight closed with no public path activation. |
| 1286 | `docs/specs/ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md` | Sidecar public projection privacy/serving preflight closed with no public serving. |
| 1287 | `docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md` | Release publication/signing authorization preflight closed with no publication or signing. |
| 1288 | `docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md` | Closure gate passed and Window 1289+ sequence lock is required. |

## 4. Closure verdict summary

| Phase | Scope | Closure disposition |
|-------|-------|---------------------|
| 1281 | Sequence lock | Closed. Window order, sensitive gates, and non-authorization boundaries were locked. |
| 1282 | Context Capsule v5.51 frontier refresh | Closed. Current capsule superseded v5.50 and reflected CDL-087 ratification plus Window 1273-1280 closure. |
| 1282 Fix1 | Claimability runtime audit hardening | Closed for local helper hardening only. Public claimability and wallet economics remain blocked. |
| 1283 | Public claimability authority decision preflight | Closed as no activation and no public API. |
| 1284 | Claimability verifier/API boundary preflight | Closed as internal-only boundary. No public verifier service, endpoint, or API is enabled. |
| 1285 | TransportPrincipal public-path activation preflight | Closed as preflight-only. Public P2P and public fetch serving remain blocked. |
| 1286 | Sidecar public projection privacy/serving preflight | Closed as preflight-only. Public sidecar/projection serving remains blocked. |
| 1287 | Release publication/signing authorization preflight | Closed as preflight-only. Source export, publication, release artifacts, keys, envelopes, Genesis signing, and v0.2 signing remain blocked. |
| 1288 | Closure gate | Passed. Window 1281-1288 is closed and Window 1289+ requires a new sequence lock before further phase assignment. |

## 5. Public claimability and verifier/API status

Relevant tokens:

```text
public_claimability_authority_decision_preflight_phase_1283.v0.1
public_claimability_activation_requires_explicit_human_authorization_phase_1283
public_claimability_activation_not_authorized_by_default_phase_1283
wallet_withdrawal_transfer_spend_still_blocked_phase_1283
claimability_human_question_escalation_required_phase_1283
public_claimability_authority_verdict_phase_1283=no_activation_no_public_api
public_claimability_verifier_api_boundary_preflight_phase_1284.v0.1
claimability_api_public_serving_not_enabled_phase_1284
claimability_verifier_authority_not_activated_phase_1284
public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api
```

Window 1281-1288 clarified the public-claimability boundary without activating
it. Phase 1283 recorded that public claimability requires explicit human
authorization and is not activated by default. Phase 1284 kept verifier/API work
as an internal boundary and intentionally did not add a public helper or public
route.

Public claimability remains a public-RC blocker after Phase 1288.

## 6. TransportPrincipal, sidecar, and public-path status

Relevant tokens:

```text
transport_principal_public_path_activation_preflight_phase_1285.v0.1
transport_principal_public_p2p_not_activated_phase_1285
public_fetch_serving_not_enabled_phase_1285
requester_id_fallback_still_forbidden_phase_1285
transport_principal_lifecycle_revocation_replay_required_phase_1285
transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation
transport_principal_public_path_authority_not_activated_phase_1285
sidecar_public_projection_privacy_serving_preflight_phase_1286.v0.1
sidecar_public_serving_not_enabled_phase_1286
non_loopback_bind_not_enabled_phase_1286
public_projection_endpoint_not_enabled_phase_1286
transport_principal_activation_required_before_public_projection_phase_1286
sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving
no_new_public_listener_phase_1286
peer_discovery_not_enabled_phase_1286
```

Window 1281-1288 preserved the existing internal preflight helpers as
`PUBLIC_RC_EXCLUDE` substrates and did not create new runtime surfaces.
TransportPrincipal public-path authority is not activated. Public fetch serving,
public P2P, non-loopback bind, public projection endpoint serving, listener, and
peer discovery remain disabled.

Public projection serving still requires explicit sidecar public-serving
authority, actual TransportPrincipal public-path activation, public-safe
projection schema, field filtering, privacy review, abuse controls, rate limits,
and hostile-network validation.

## 7. Release, publication, and signing status

Relevant tokens:

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
```

Phase 1287 closed only the release publication/signing authorization preflight.
Phase 1255 remains a source allowlist procedure, Phase 1213 remains a release
artifact schema, Phase 1271 remains a graph gate with release artifacts blocked,
and Phase 1279 remains an inventory-only prepublication packet.

No source allowlist export was executed. No public repository or package was
published. No release artifact was produced. No release keys or envelopes were
generated. Genesis Atlas was not mutated, regenerated, or signed. v0.2 was not
signed.

## 8. Public-RC blocker classification

Public RC remains blocked after Phase 1288:

```text
public_rc_remains_blocked_after_phase_1288
public_rc_remains_blocked_after_phase_1287
public_rc_remains_blocked_after_phase_1286
public_rc_remains_blocked_after_phase_1285
public_rc_remains_blocked_after_phase_1284
public_rc_remains_blocked_after_phase_1283
public_rc_remains_blocked_after_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282
public_rc_remains_blocked_after_phase_1280_fix1
public_rc_remains_blocked_after_phase_1280
```

Current blocker classes:

- Final public claimability API/verifier authority and release allowlist promotion.
- Actual TransportPrincipal public-path activation authority plus lifecycle, revocation, replay, admission, ban, rate-limit, and hostile-network hardening.
- Actual public sidecar/projection serving authorization, privacy review, public-safe projection schema, field filtering, non-loopback bind/listener policy, and peer-discovery policy.
- Counsel/license/CLA/trademark/patent/publication authorization.
- Source allowlist export execution, public source publication, public package publication, release artifacts, release keys, release envelopes, and release manifest instance production.
- Genesis Atlas mutation/regeneration/signing and v0.2 signing authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- Wallet withdrawal, wallet transfer, wallet spend, wallet signing authority, and wallet ledger-write authority.
- ECU minting, ILC settlement, and withdrawal runtime activation.

## 9. Exit criteria reconciliation

The Window 1281-1288 guidance exit criteria are reconciled as follows:

| Exit criterion | Phase evidence | Closure result |
|----------------|----------------|----------------|
| Sequence lock exists | Phase 1281 | Satisfied. |
| Capsule v5.51 refresh complete | Phase 1282 | Satisfied and updated in place through closure. |
| Public claimability authority decision recorded | Phase 1283 | Satisfied as no activation and no public API. |
| Claimability verifier/API boundary recorded | Phase 1284 | Satisfied as internal-only and no public API. |
| TransportPrincipal public-path activation preflight recorded | Phase 1285 | Satisfied as preflight-only and no public path activation. |
| Sidecar public projection privacy/serving preflight recorded | Phase 1286 | Satisfied as preflight-only and no public serving. |
| Release publication/signing authorization preflight recorded | Phase 1287 | Satisfied as preflight-only and no publication or signing. |
| Public-RC blockers honestly classified | Phase 1288 | Satisfied; public RC remains blocked. |

## 10. Carry-forward items and residual blockers

Closed inside Window 1281-1288:

- Window 1281-1288 sequence lock.
- Capsule v5.51 refresh over v5.50.
- Local claimability/conversion hardening record.
- Public claimability authority decision preflight.
- Claimability verifier/API boundary preflight.
- TransportPrincipal public-path activation preflight.
- Sidecar public projection privacy/serving preflight.
- Release publication/signing authorization preflight.
- Window closure and blocker classification.

Carried forward:

- Public claimability verifier/API authority and public claimability activation.
- Wallet withdrawal, transfer, spend, wallet signing authority, and wallet ledger-write authority.
- Public sidecar/projection serving authorization, non-loopback bind, listener, peer discovery, privacy review, and public-safe projection schema.
- TransportPrincipal public-path activation, lifecycle, revocation, replay, admission, ban, rate-limit, and public-P2P policy.
- Rust M-5/public-P2P hostile-network hardening.
- Counsel/license/CLA/trademark/patent/publication authorization.
- Source allowlist export execution, public source publication, public package publication, release artifacts, release keys, and release envelopes.
- Genesis Atlas mutation/regeneration/signing and v0.2 signing authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- ECU minting, ILC settlement, and withdrawal runtime activation.

## 11. Next-window entry criteria and routing

No additional phase should be assigned from Window 1281-1288. The next phase
assignment requires a new Window 1289+ sequence lock:

```text
window_1289_plus_sequence_lock_required_before_next_phase_assignment
```

Recommended Window 1289+ routing:

- Publish a new sequence lock that consumes this handoff and keeps public RC blocked until explicitly authorized.
- Decide whether the next lane is public claimability authority, TransportPrincipal activation, sidecar public serving, release publication/signing, H-series math/research planning, or IP/publication drafting.
- Keep publication/IP work tracked without making it a public-RC activation claim.
- Preserve the current preflight stance until a later explicit activation/release phase grants authority.

## 12. MemPalace refresh disposition

Disposition: required

Active working set impacted: yes

Recommended command:

```bash
bash tools/mempalace/build_active_working_set.sh
```

This is an advisory recall refresh only. Direct repo reads remain authoritative.

## 13. Non-authorization boundary

Phase 1288 does not authorize:

- public RC claim;
- public launch claim;
- public claimability activation;
- public claimability API activation;
- public verifier service;
- public repository publication;
- public package publication;
- source allowlist export execution;
- public release artifact production;
- release artifact manifest instance production;
- release key generation;
- release envelope production;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback sidecar/projection serving;
- public projection endpoint serving;
- listener, non-loopback bind, wildcard bind, public host bind, or peer discovery;
- wallet withdrawal, transfer, or spend;
- wallet signing or ledger-write authority;
- ECU minting;
- ILC settlement or withdrawal runtime;
- CDL mutation;
- CDL-088 opening;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- IP filing or paper publication;
- immutable diagnostic mutation;
- production `commit.epoch` emission authorization.

## 14. Graph delta

```text
graph_delta=support_only:docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1288_window_1281_1288_closure_gate_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1288_window_1281_1288_closure_gate.py -> validation
graph_delta=support_tests_changed:tests/test_phase_1287_release_publication_signing_authorization_preflight.py -> validation/frontier
```
