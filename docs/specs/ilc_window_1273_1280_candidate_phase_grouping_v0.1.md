# ILC Window 1273-1280 Candidate Phase Grouping v0.1

**Status:** Planning-only candidate guidance / prompt-draft registry.
**Recorded:** 2026-05-09.
**Authority:** This document does not open Window 1273-1280, assign official
phase authority, ratify CDL-087, mutate any CDL row, authorize public RC,
authorize public repository publication, expose public P2P, expose public
sidecar/projection serving, activate public claimability, enable wallet
withdrawal/transfer/spend, mint ECU, settle ILC, mutate Genesis, produce public
release artifacts, or authorize v0.2 signing. Exact execution authority must be
set by the future Phase 1273 sequence lock after explicit human `GO Phase 1273`.

```text
window_1273_1280_candidate_phase_grouping_recorded_after_phase_1272
window_1273_1280_not_open_until_sequence_lock
human_question_escalation_required_for_uncertain_authority
```

---

## 1. Purpose

Window 1265-1272 closed with selected-profile ATLAS-G-006 graph reachability
passing, but public RC still blocked by claimability/conversion-sweeper runtime,
CDL-087 ratification, TransportPrincipal/public-path integration, sidecar public
serving gates, release/publication authorization, and v0.2 signing
authorization.

This candidate grouping turns the Phase 1272 handoff into the next draft
execution window. The emphasis is to reduce the highest common public-RC
blockers without crossing authority boundaries:

```text
claimability_conversion_sweeper_runtime_window_candidate_after_phase_1272
claimability_proof_binding_window_candidate_after_phase_1272
cdl_087_ratification_authorization_preflight_window_candidate
cdl087_register_mutation_not_authorized_by_default_phase_1276
transport_principal_public_path_integration_window_candidate
sidecar_public_projection_authorization_preflight_window_candidate
release_manifest_allowlist_prepublication_window_candidate
```

No candidate phase below is a public-RC claim. The sequence lock must decide
which scopes are executable and which are still too sensitive or
under-evidenced.

---

## 2. Retrieval And Verification Basis

Direct current-canon inputs:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
3. `docs/phases/STATUS.md`
4. `docs/specs/ilc_window_1265_1272_handoff_1272_v0.1.md`
5. `docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md`
6. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
7. `docs/specs/ilc_constitutional_decision_log_v0.1.md`
8. `docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md`
9. `docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md`
10. `docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md`
11. `docs/specs/ilc_werner_default_topology_pressure_profile_1269_v0.1.md`
12. `docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md`
13. `docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md`
14. `docs/phases/phase_1271_fix1_atlas_g_006_manifest_profile_consistency_hardening_walkthrough.md`
15. `docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md`
16. `docs/specs/ilc_transport_principal_identity_spec_1253_v0.1.md`
17. `docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.json`
18. `ilc_core/protocol/public_wallet_runtime.py`
19. `ilc_core/protocol/public_receipt_runtime.py`
20. `ilc_core/rc/atlas_graph_discipline.py`
21. `ilc_core/graph/sidecar_query_runtime.py`

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
   `deferred`, `blocked`, `not authorized`, `not ratified`, `local-only`,
   `no public`, `superseded`, and domain-specific denial terms.
4. `### §0d — Source expansion and newly discovered tokens` to direct-read
   every relevant hit and carry newly discovered tokens/non-claims into the
   phase walkthrough, STATUS entry, or carry-forward docs.

MemPalace may be used as an advisory recall net in §0b/§0d, but returned paths
must be direct-read before any result is treated as canon.

Exact-token `rg` is a schema/completion check only. It confirms that a required
token appears somewhere; it does not prove that related historical wording,
runtime symbols, or blocker concepts have been found. Phase execution must also
search token components, synonyms, neighboring concepts, older names, code
symbols, and denial terms before concluding that a concept is absent.

---

## 3. Human Escalation Rule

If a phase discovers a decision that cannot be resolved from committed canon and
would widen authority, mutate a CDL register row, enable public exposure, enable
claimability/spend semantics, produce public release artifacts, publish source,
generate/sign release material, or choose between conflicting mathematical or
security evidence routes, the phase must stop and prompt the human reviewer.

Do not silently choose broader authority. Default to the narrower
non-authorization path and record the unresolved question in the walkthrough,
STATUS entry, handoff, or carry-forward table.

```text
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
```

---

## 4. Candidate Phase Order

| Phase | Candidate scope | Sensitivity | Prompt draft |
|-------|-----------------|-------------|--------------|
| 1273 | Window 1273-1280 sequence lock | **SENSITIVE** - requires `GO Phase 1273` | `docs/antigravity_tasks/antigravity_prompt__phase_1273_g8_window_1273_1280_sequence_lock.md` |
| 1274 | CDL-048 conversion-sweeper runtime skeleton and exact ECU lot ledger boundary | **SENSITIVE** - economic/public-claimability runtime; no activation | `docs/antigravity_tasks/antigravity_prompt__phase_1274_g8_cdl048_conversion_sweeper_runtime_skeleton.md` |
| 1275 | Public claimability proof-binding runtime boundary | **SENSITIVE** - claimability substrate; no public API or spend semantics | `docs/antigravity_tasks/antigravity_prompt__phase_1275_g8_claimability_proof_binding_runtime_boundary.md` |
| 1276 | CDL-087 ratification authorization preflight / decision packet | **SENSITIVE** - no register mutation by default; explicit human ratification authorization required for mutation | `docs/antigravity_tasks/antigravity_prompt__phase_1276_g8_cdl087_ratification_authorization_preflight.md` |
| 1277 | TransportPrincipal public-path ADR and runtime integration preflight | **SENSITIVE** - public-path identity semantics; no public P2P activation | `docs/antigravity_tasks/antigravity_prompt__phase_1277_g8_transport_principal_public_path_adr_runtime_integration.md` |
| 1278 | Sidecar non-loopback/public projection authorization preflight | **SENSITIVE** - no listener or public serving by default | `docs/antigravity_tasks/antigravity_prompt__phase_1278_g8_sidecar_non_loopback_public_path_preflight.md` |
| 1279 | Release manifest and source allowlist pre-publication preflight | NON-SENSITIVE only if inventory/procedure docs and validation; no publication, signing, or release artifact production | `docs/antigravity_tasks/antigravity_prompt__phase_1279_g8_release_manifest_allowlist_prepublication_preflight.md` |
| 1280 | Window 1273-1280 closure gate | **SENSITIVE** - requires `GO Phase 1280` | `docs/antigravity_tasks/antigravity_prompt__phase_1280_g8_window_1273_1280_closure_gate.md` |

---

## 5. Scope Rationale

### 5.1 Claimability should start with conversion sweeper and proof binding

Phase 1270 recorded requirements only. The next safe runtime sequence is to
implement exact ECU lot/deadline accounting and proof/root binding before any
public claimability API, withdrawal, transfer, spend, ECU mint, or ILC
settlement semantics.

### 5.2 CDL-087 is a human-authorized ratification question

Phase 1266 closed as review/no-ratification/no-register-mutation. The next
window may prepare a ratification authorization packet or recheck the evidence,
but actual CDL-087 register mutation requires explicit human ratification
authorization in the phase instruction. Without that authorization, the prompt
must preserve a no-mutation default.

### 5.3 Public path depends on authenticated TransportPrincipal semantics

Phase 1267 delivered only a pre-public helper. Full public-path work must cover
revocation, replay, privacy, abuse/rate-limit binding, and Rust/public-P2P
handoff before any public P2P or non-loopback projection serving is exposed.

### 5.4 Sidecar serving remains blocked until governance and identity close

Phase 1268 recorded no new listener and kept public/non-loopback sidecar
projection blocked. Phase 1278 should remain an authorization and gate preflight
unless the sequence lock and human instruction explicitly authorize a narrower
local implementation.

### 5.5 Release/publication remains a procedure gate, not a publication act

ATLAS-G-006 graph reachability passed, but release manifest, source allowlist,
counsel/IP/publication authorization, Genesis Atlas mutation/regeneration/signing,
and v0.2 signing remain blocked. Phase 1279 may prepare inventory and validation
only; it must not publish source, produce public release artifacts, generate
release keys, or sign v0.2.

---

## 6. Window Exit Criteria

Window 1273-1280 should not close as pass unless all of the following are true:

1. Phase 1273 sequence lock exists and records exact sensitive gates.
2. Claimability/conversion-sweeper runtime status is recorded with exact numeric
   and epoch/deadline boundaries.
3. Claimability proof/root binding status is recorded without public API or
   wallet spend semantics.
4. CDL-087 ratification or no-ratification status is explicit, and CDL register
   mutation status is explicit.
5. TransportPrincipal public-path status is recorded without public P2P exposure
   unless separately authorized by a future instruction.
6. Sidecar non-loopback/public projection status is recorded as blocked or
   authorized by explicit future scope; no accidental listener is introduced.
7. Release manifest/source allowlist status is recorded without publication,
   release-artifact production, Genesis Atlas mutation, or v0.2 signing.
8. Public-RC blocker classes remain honestly classified as closed, open, or
   carried forward.

---

## 7. Non-Claims

This guidance does not:

- open Window 1273-1280;
- execute Phase 1273;
- ratify CDL-087;
- mutate any CDL row;
- authorize public RC;
- authorize public repository publication;
- authorize public package publication;
- authorize public P2P exposure;
- authorize public sidecar/projection serving;
- activate public claimability;
- enable wallet withdrawal, transfer, or spend;
- authorize ECU minting;
- authorize ILC settlement or withdrawal runtime;
- generate release keys;
- produce release envelopes;
- produce public release artifacts;
- mutate signed Genesis v0.1;
- regenerate Genesis Atlas v0.2+;
- mutate immutable diagnostic anchors;
- authorize v0.2 signing.

---

## 8. Carry-Forward Tokens

```text
window_1273_1280_candidate_phase_grouping_recorded_after_phase_1272
window_1273_1280_not_open_until_sequence_lock
claimability_conversion_sweeper_runtime_window_candidate_after_phase_1272
claimability_proof_binding_window_candidate_after_phase_1272
cdl_087_ratification_authorization_preflight_window_candidate
transport_principal_public_path_integration_window_candidate
sidecar_public_projection_authorization_preflight_window_candidate
release_manifest_allowlist_prepublication_window_candidate
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
public_rc_remains_blocked_after_phase_1272
cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1276
public_claimability_runtime_still_requires_conversion_sweeper_after_phase_1272
transport_principal_required_before_public_projection_after_phase_1272
release_manifest_allowlist_publication_still_authorization_gated_after_phase_1272
unknown_unknown_discovery_required_before_phase_execution
```
