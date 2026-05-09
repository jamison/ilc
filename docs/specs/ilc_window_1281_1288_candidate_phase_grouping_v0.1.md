# ILC Window 1281-1288 Candidate Phase Grouping v0.1

**Status:** Planning-only candidate guidance / prompt-draft registry.
**Recorded:** 2026-05-09.
**Authority:** This document does not open Window 1281-1288, assign official
phase authority, mutate any CDL row, open CDL-088, authorize public RC,
authorize public repository publication, expose public P2P, expose public
sidecar/projection serving, activate public claimability, enable wallet
withdrawal/transfer/spend, mint ECU, settle ILC, mutate Genesis, produce public
release artifacts, generate release keys, produce release envelopes, or
authorize v0.2 signing. Exact execution authority must be set by the future
Phase 1281 sequence lock after explicit human `GO Phase 1281`.

```text
window_1281_1288_candidate_phase_grouping_recorded_after_phase_1280
window_1281_1288_not_open_until_sequence_lock
human_question_escalation_required_for_uncertain_authority
```

---

## 1. Purpose

Window 1273-1280 closed with CDL-087 ratified and several public-RC runway
preflights complete, but public RC remains blocked. The largest remaining
cross-cutting blockers are current-capsule staleness, public claimability
authority, TransportPrincipal public-path activation, sidecar public
projection/serving authority, counsel/publication/release authorization, and
v0.2 signing authority.

This candidate grouping turns the Phase 1280 handoff into the next draft
execution window. The default posture remains pre-authorization and fail-closed:

```text
context_capsule_refresh_window_candidate_after_phase_1280
public_claimability_authority_decision_window_candidate
public_claimability_activation_not_authorized_by_default_phase_1283
public_claimability_verifier_api_boundary_window_candidate
transport_principal_public_path_activation_window_candidate
sidecar_public_projection_privacy_serving_window_candidate
release_publication_signing_authorization_window_candidate
```

No candidate phase below is a public-RC claim. The future sequence lock must
decide which scopes are executable and which must stop for human authorization.

---

## 2. Retrieval And Verification Basis

Direct current-canon inputs:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
3. `docs/phases/STATUS.md`
4. `docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md`
5. `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md`
6. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
7. `docs/specs/ilc_constitutional_decision_log_v0.1.md`
8. `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md`
9. `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md`
10. `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md`
11. `docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md`
12. `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md`
13. `docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md`
14. `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
15. `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
16. `docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md`
17. `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`
18. `ilc_core/ledger/claimability_proof_binding_runtime.py`
19. `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
20. `ilc_core/graph/sidecar_public_path_preflight.py`

Standing retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Every executable prompt draft in this window must include the exact four-part
§0 discovery pass before coding:

1. `### §0a — Known-token audit` for Required Tokens and explicit claims.
2. `### §0b — Concept-discovery search` for forgotten synonyms, older names,
   code symbols, phase numbers, and domain concepts not already listed as
   tokens.
3. `### §0c — Contradiction and non-claim search` for blockers such as
   `deferred`, `blocked`, `not authorized`, `local-only`, `no public`,
   `PUBLIC_RC_EXCLUDE`, `superseded`, and domain-specific denial terms.
4. `### §0d — Source expansion and newly discovered tokens` to direct-read
   every relevant hit and carry newly discovered tokens/non-claims into the
   phase walkthrough, STATUS entry, or carry-forward docs.

MemPalace may be used as an advisory recall net in §0b/§0d, but returned paths
must be direct-read before any result is treated as canon.

Exact-token `rg` is a schema/completion check only. It confirms that a required
token appears somewhere; it does not prove that related historical wording,
runtime symbols, or blocker concepts have been found.

---

## 3. Human Escalation Rule

If a phase discovers a decision that cannot be resolved from committed canon and
would widen authority, mutate a CDL row, enable public exposure, enable
claimability/spend semantics, publish source, produce/sign release material,
mutate Genesis Atlas, or choose between conflicting mathematical/security
evidence routes, the phase must stop and prompt the human reviewer.

Default to the narrower non-authorization path and record the unresolved
question in the walkthrough, STATUS entry, handoff, or carry-forward table.

```text
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
```

## 4. Candidate Phase Order

| Phase | Candidate scope | Sensitivity | Prompt draft |
|-------|-----------------|-------------|--------------|
| 1281 | Window 1281-1288 sequence lock | **SENSITIVE** - requires `GO Phase 1281` | `docs/antigravity_tasks/antigravity_prompt__phase_1281_g8_window_1281_1288_sequence_lock.md` |
| 1282 | Context Capsule v5.51 frontier refresh | NON-SENSITIVE docs/canon refresh only; no runtime or public activation | `docs/antigravity_tasks/antigravity_prompt__phase_1282_g8_context_capsule_v5_51_frontier_refresh.md` |
| 1283 | Public claimability authority decision preflight | **SENSITIVE** - requires `GO Phase 1283`; activation requires explicit human authorization | `docs/antigravity_tasks/antigravity_prompt__phase_1283_g8_public_claimability_authority_decision_preflight.md` |
| 1284 | Public claimability verifier/API boundary preflight | **SENSITIVE** - no public endpoint by default; any helper must be `PUBLIC_RC_EXCLUDE` unless explicitly reviewed | `docs/antigravity_tasks/antigravity_prompt__phase_1284_g8_public_claimability_verifier_api_boundary_preflight.md` |
| 1285 | TransportPrincipal public-path activation preflight | **SENSITIVE** - no public P2P or public fetch serving by default | `docs/antigravity_tasks/antigravity_prompt__phase_1285_g8_transport_principal_public_path_activation_preflight.md` |
| 1286 | Sidecar public projection privacy/serving preflight | **SENSITIVE** - no listener, non-loopback bind, or public projection endpoint by default | `docs/antigravity_tasks/antigravity_prompt__phase_1286_g8_sidecar_public_projection_privacy_serving_preflight.md` |
| 1287 | Release publication and v0.2 signing authorization preflight | **SENSITIVE** - inventory/decision packet only unless explicit publication/signing authority exists | `docs/antigravity_tasks/antigravity_prompt__phase_1287_g8_release_publication_signing_authorization_preflight.md` |
| 1288 | Window 1281-1288 closure gate | **SENSITIVE** - requires `GO Phase 1288` | `docs/antigravity_tasks/antigravity_prompt__phase_1288_g8_window_1281_1288_closure_gate.md` |

---

## 5. Scope Rationale

### 5.1 Refresh the capsule before further public-RC decisions

Capsule v5.50 is the latest published capsule, but it is stale on CDL-087 and
Window 1273-1280 closure. A v5.51 refresh should make the current frontier
machine-readable before later phases depend on it.

### 5.2 Public claimability is the next explicit human decision gate

Phases 1274 and 1275 completed local conversion/proof boundaries. They did not
authorize a public verifier, public API, wallet withdrawal, transfer, spend,
ECU mint, or ILC settlement. Phase 1283 should decide whether the next slice is
still preflight-only or whether the human explicitly authorizes a narrow
public-claimability activation path.

### 5.3 Claimability API work must avoid accidental public serving

If Phase 1284 introduces any helper or route scaffold, it must be internal by
default and marked `PUBLIC_RC_EXCLUDE` unless an explicit public-RC allowlist
review removes that marker later.

### 5.4 Public projection depends on TransportPrincipal lifecycle evidence

CDL-087 ratification is necessary but not sufficient. Public path still needs
TransportPrincipal lifecycle, revocation, replay, privacy, admission, ban, and
hostile-network hardening evidence before public P2P, public fetch serving, or
non-loopback sidecar/projection serving.

### 5.5 Release and signing remain prepublication gates

Phase 1279 recorded inventory only. Future release work must still keep source
publication, release artifact production, release keys, release envelopes,
Genesis Atlas mutation/signing, and v0.2 signing blocked until explicit
authorization and counsel/publication gates exist.

---

## 6. Open Questions To Prompt During The Window

The following questions should be raised to the human reviewer only when a
phase reaches the relevant decision point:

- Phase 1283: should public claimability remain preflight-only, or is a narrow
  public claimability activation path authorized?
- Phase 1284: what public verifier/API surface, if any, is acceptable for a
  public-RC package, and which helpers must remain `PUBLIC_RC_EXCLUDE`?
- Phase 1285: is TransportPrincipal public-path activation authorized, or only
  lifecycle/revocation/replay preflight?
- Phase 1286: is any non-loopback sidecar/projection serving authorized, or
  should it remain blocked pending privacy/public-path review?
- Phase 1287: are counsel/IP/publication, release key/envelope, Genesis Atlas,
  and v0.2 signing gates still deferred, or has explicit authority arrived?

## 7. Window Exit Criteria

Window 1281-1288 should not close as pass unless all of the following are true:

1. Phase 1281 sequence lock exists and records exact sensitive gates.
2. Capsule refresh status is explicit, or the reason for deferral is recorded.
3. Public claimability authority status is explicit: authorized narrow path,
   deferred, or blocked.
4. Claimability verifier/API boundary status is recorded without accidental
   public endpoint activation.
5. TransportPrincipal public-path activation status is recorded without public
   P2P or public fetch serving unless separately authorized.
6. Sidecar public projection/serving status is recorded without accidental
   listener, non-loopback bind, or public endpoint.
7. Release/publication/signing status is recorded without source publication,
   release artifact production, release-key generation, release envelope
   production, Genesis Atlas mutation, or v0.2 signing unless explicit
   authority exists.
8. Public-RC blocker classes remain honestly classified as closed, open, or
   carried forward.

---

## 8. Non-Claims

This guidance does not:

- open Window 1281-1288;
- execute Phase 1281;
- mutate any CDL row;
- open CDL-088;
- authorize public RC;
- authorize public repository publication;
- authorize public package publication;
- authorize public P2P exposure;
- authorize public fetch serving;
- authorize public sidecar/projection serving;
- activate public claimability;
- enable wallet withdrawal, transfer, or spend;
- authorize ECU minting;
- authorize ILC settlement or withdrawal runtime;
- generate release keys;
- produce release envelopes;
- produce public release artifacts;
- mutate signed Genesis v0.1;
- regenerate or sign Genesis Atlas v0.2+;
- mutate immutable diagnostic anchors;
- authorize v0.2 signing.

---

## 9. Carry-Forward Tokens

```text
window_1281_1288_candidate_phase_grouping_recorded_after_phase_1280
window_1281_1288_not_open_until_sequence_lock
context_capsule_refresh_window_candidate_after_phase_1280
public_claimability_authority_decision_window_candidate
public_claimability_verifier_api_boundary_window_candidate
transport_principal_public_path_activation_window_candidate
sidecar_public_projection_privacy_serving_window_candidate
release_publication_signing_authorization_window_candidate
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
public_rc_remains_blocked_after_phase_1280
capsule_v5_51_refresh_recommended_after_phase_1280
public_claimability_activation_requires_explicit_human_authorization_phase_1283
transport_principal_activation_required_before_public_projection_phase_1286
release_publication_and_v0_2_signing_still_authorization_gated_after_phase_1280
unknown_unknown_discovery_required_before_phase_execution
```
