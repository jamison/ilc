# ILC Window 1289-1296 Candidate Phase Grouping v0.1

**Status:** Planning-only candidate guidance / prompt-draft registry.
**Recorded:** 2026-05-10.
**Authority:** This document does not open Window 1289-1296, assign official
phase authority, mutate any CDL row, open CDL-088, authorize public RC,
authorize public repository publication, execute source allowlist export,
produce public release artifacts, generate release keys, produce release
envelopes, expose public P2P, expose public fetch serving, expose public
sidecar/projection serving, activate public claimability, enable wallet
withdrawal/transfer/spend, mint ECU, settle ILC, mutate Genesis, sign Genesis
Atlas, or authorize v0.2 signing. Exact execution authority must be set by the
future Phase 1289 sequence lock after explicit human `GO Phase 1289`.

```text
window_1289_1296_candidate_phase_grouping_recorded_after_phase_1288_fix1
window_1289_1296_not_open_until_sequence_lock
phase_1289_window_1289_1296_sequence_lock_required
human_question_escalation_required_for_uncertain_authority
public_rc_remains_blocked_after_phase_1288_fix1
```
---

## 1. Purpose

Window 1281-1288 closed honestly with a pass verdict and carried the public-RC
blockers forward. Phase 1288 Fix1 then hardened the local conversion,
claimability, TransportPrincipal, and sidecar preflight helpers against
canonical-payload traversal hazards. The next candidate window should move from
"authority preflight only" toward release-candidate blocker closure rehearsals,
but only under explicit sequence-lock control.

The default stance remains fail-closed:

```text
preflight_stance_preserved_until_explicit_activation_authority_window_1289_1296
public_rc_candidate_standard_preserved_window_1289_1296
no_public_activation_from_candidate_guidance_window_1289_1296
```

No candidate phase below is a public-RC claim. The future sequence lock must
decide which scopes are executable and which must stop for human authorization.

## 2. Retrieval And Verification Basis

Direct current-canon inputs:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
3. `docs/phases/STATUS.md`
4. `docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md`
5. `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md`
6. `docs/phases/phase_1288_fix1_runtime_deep_audit_hardening_walkthrough.md`
7. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
8. `docs/specs/ilc_constitutional_decision_log_v0.1.md`
9. `docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md`
10. `docs/specs/ilc_public_claimability_verifier_api_boundary_preflight_1284_v0.1.md`
11. `docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md`
12. `docs/specs/ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md`
13. `docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md`
14. `docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md`
15. `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md`
16. `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
17. `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
18. `docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md`
19. `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`
20. `ilc_core/ledger/claimability_proof_binding_runtime.py`
21. `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
22. `ilc_core/graph/sidecar_public_path_preflight.py`

Standing retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Every executable prompt draft in this window must include the exact four-part
§0 discovery pass before coding:

1. `### §0a — Known-token audit` for required tokens and explicit claims.
2. `### §0b — Concept-discovery search` for forgotten synonyms, older names,
   code symbols, phase numbers, and domain concepts not already listed as
   tokens.
3. `### §0c — Contradiction and non-claim search` for blockers such as
   `deferred`, `blocked`, `not authorized`, `local-only`, `no public`,
   `PUBLIC_RC_EXCLUDE`, `superseded`, and domain-specific denial terms.
4. `### §0d — Source expansion and newly discovered tokens` to direct-read
   every relevant hit and carry newly discovered tokens/non-claims into the
   phase walkthrough, STATUS entry, or carry-forward docs.

MemPalace may be used as advisory recall support only. Returned paths must be
direct-read before any result is treated as canon.

Exact-token `rg` is a schema/completion check only. It confirms that a required
token appears somewhere; it does not prove that related historical wording,
runtime symbols, or blocker concepts have been found.

## 3. Human Escalation Rule

If a phase discovers a decision that cannot be resolved from committed canon and
would widen authority, mutate a CDL row, open CDL-088, enable public exposure,
enable claimability/spend semantics, publish source, produce release artifacts,
generate or sign release material, mutate or sign Genesis Atlas, sign v0.2, or
choose between conflicting mathematical/security evidence routes, the phase
must stop and prompt the human reviewer.

Default to the narrower non-authorization path and record the unresolved
question in the walkthrough, STATUS entry, handoff, or carry-forward table.

```text
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
```

## 4. Candidate Phase Order

| Phase | Candidate scope | Sensitivity | Prompt draft |
|-------|-----------------|-------------|--------------|
| 1289 | Window 1289-1296 sequence lock | **SENSITIVE** - requires `GO Phase 1289` | `docs/antigravity_tasks/antigravity_prompt__phase_1289_g8_window_1289_1296_sequence_lock.md` |
| 1290 | Context Capsule v5.52 frontier refresh | NON-SENSITIVE docs/canon refresh only; no runtime or public activation | `docs/antigravity_tasks/antigravity_prompt__phase_1290_g8_context_capsule_v5_52_frontier_refresh.md` |
| 1291 | Public claimability verifier contract preflight | **SENSITIVE** - no public endpoint or claimability activation by default | `docs/antigravity_tasks/antigravity_prompt__phase_1291_g8_public_claimability_verifier_contract_preflight.md` |
| 1292 | Claimability package-profile allowlist rehearsal | **SENSITIVE** - dry-run/package-profile rehearsal only; no source export or package publication | `docs/antigravity_tasks/antigravity_prompt__phase_1292_g8_claimability_package_profile_allowlist_rehearsal.md` |
| 1293 | TransportPrincipal lifecycle activation-blocker preflight | **SENSITIVE** - no public P2P or public fetch serving by default | `docs/antigravity_tasks/antigravity_prompt__phase_1293_g8_transport_principal_lifecycle_activation_blocker_preflight.md` |
| 1294 | Sidecar public-safe projection schema preflight | **SENSITIVE** - no listener, non-loopback bind, or public projection endpoint by default | `docs/antigravity_tasks/antigravity_prompt__phase_1294_g8_sidecar_public_safe_projection_schema_preflight.md` |
| 1295 | Release allowlist, artifact, Genesis readiness preflight | **SENSITIVE** - no publication, release artifact, keys, envelopes, Genesis signing, or v0.2 signing by default | `docs/antigravity_tasks/antigravity_prompt__phase_1295_g8_release_allowlist_artifact_genesis_readiness_preflight.md` |
| 1296 | Window 1289-1296 closure gate | **SENSITIVE** - requires `GO Phase 1296` unless authorized as part of a wider sensitive run | `docs/antigravity_tasks/antigravity_prompt__phase_1296_g8_window_1289_1296_closure_gate.md` |

## 5. Scope Rationale

### 5.1 Refresh the capsule before further blocker closure

Capsule v5.51 is current through Phase 1288 Fix1. If Window 1289-1296 opens, a
v5.52 refresh should record the new sequence lock, this planning package, and
the exact post-Fix1 public-RC blocker map before sensitive work depends on it.

### 5.2 Claimability should move through verifier contract before public API

Phases 1283 and 1284 denied public activation and public API authority. The
next safe slice is a verifier contract preflight: inputs, outputs, proof
bindings, package-profile boundary, helper exclusion status, and negative
activation assertions. Public serving remains blocked unless later explicitly
authorized.

### 5.3 Package-profile rehearsal should not execute publication

The allowlist/export work should be rehearsed as a deterministic package-profile
boundary. It should not execute source allowlist export, publish source, publish
packages, produce public release artifacts, or remove `PUBLIC_RC_EXCLUDE`
markers without explicit review.

### 5.4 TransportPrincipal and sidecar must close privacy and lifecycle blockers

Public fetch/projection requires more than CDL-087 ratification. The next
candidate window should separate TransportPrincipal lifecycle/revocation/replay
evidence from sidecar public-safe projection schema, field filtering, bind
policy, listener policy, and peer-discovery policy.

### 5.5 Release readiness and signing remain human-authority gates

Release material, Genesis Atlas signing, and v0.2 signing are still blocked.
Phase 1295 is a readiness preflight by default, not publication or signing.

## 6. Open Questions To Prompt During The Window

The following questions should be raised to the human reviewer only when a
phase reaches the relevant decision point:

- Phase 1291: is the verifier contract still local/package-profile only, or is
  any public verifier/API authority explicitly granted?
- Phase 1292: which helper files, if any, may be promoted out of
  `PUBLIC_RC_EXCLUDE` for a public-RC package profile?
- Phase 1293: is TransportPrincipal public-path activation authorized, or
  should the phase remain lifecycle/revocation/replay preflight only?
- Phase 1294: what projection fields are public-safe, and is any non-loopback
  sidecar/projection serving authorized?
- Phase 1295: are source export, public repository/package publication, release
  artifacts, release keys/envelopes, Genesis Atlas signing, or v0.2 signing
  explicitly authorized, or do they remain blocked?

Do not route IP filing or publication-draft work into Phases 1289-1296 unless a
future sequence lock explicitly widens scope. The IP lane registered in Phase
1280 Fix1 remains advisory carry-forward planning, not publication
authorization.

## 7. Window Exit Criteria

Window 1289-1296 should not close as pass unless all of the following are true:

1. Phase 1289 sequence lock exists and records exact sensitive gates.
2. Capsule v5.52 refresh status is explicit, or the reason for deferral is
   recorded.
3. Public claimability verifier contract status is explicit without accidental
   public endpoint activation.
4. Package-profile allowlist rehearsal status is explicit without source export
   or package publication.
5. TransportPrincipal lifecycle/revocation/replay blocker status is explicit
   without public P2P or public fetch serving unless separately authorized.
6. Sidecar public-safe projection schema status is explicit without accidental
   listener, non-loopback bind, peer discovery, or public endpoint.
7. Release/readiness status is explicit without source publication, release
   artifact production, release-key generation, release-envelope production,
   Genesis Atlas mutation/signing, or v0.2 signing unless explicit authority
   exists.
8. Public-RC blocker classes remain honestly classified as closed, open, or
   carried forward.

## 8. Non-Claims

This guidance does not:

- open Window 1289-1296;
- execute Phase 1289;
- mutate any CDL row;
- open CDL-088;
- authorize public RC;
- authorize public repository publication;
- authorize public package publication;
- execute source allowlist export;
- produce public release artifacts;
- generate release keys;
- produce release envelopes;
- authorize public P2P exposure;
- authorize public fetch serving;
- authorize public sidecar/projection serving;
- activate public claimability;
- enable wallet withdrawal, transfer, or spend;
- authorize ECU minting;
- authorize ILC settlement or withdrawal runtime;
- mutate signed Genesis v0.1;
- regenerate or sign Genesis Atlas v0.2+;
- file any patent application;
- publish, submit, or preprint any paper;
- authorize v0.2 signing.

## 9. Carry-Forward Tokens

```text
window_1289_1296_candidate_phase_grouping_recorded_after_phase_1288_fix1
window_1289_1296_not_open_until_sequence_lock
phase_1289_window_1289_1296_sequence_lock_required
preflight_stance_preserved_until_explicit_activation_authority_window_1289_1296
public_rc_candidate_standard_preserved_window_1289_1296
no_public_activation_from_candidate_guidance_window_1289_1296
human_question_escalation_required_for_uncertain_authority
public_rc_remains_blocked_after_phase_1288_fix1
```
