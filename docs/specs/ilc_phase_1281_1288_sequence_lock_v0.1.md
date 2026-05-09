# ILC Phase 1281-1288 Sequence Lock v0.1

**Date:** 2026-05-09
**Window:** 1281-1288
**Phase:** 1281
**Status:** LOCKED
**Human authorization:** `GO Phase 1281 and continue through any subsequent non-sensitive phases, in order`
**Token:** `window_1281_1288_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1281-1288 is opened after explicit human authorization:

```text
GO Phase 1281
```

The "subsequent non-sensitive phases" clause is evaluated against this lock.
The next locked phase, Phase 1282, is non-sensitive and executable after this
sequence lock passes. Phase 1283 is sensitive, so execution must stop after
Phase 1282 unless a later explicit `GO Phase 1283` is issued.

Verdict:

```text
window_1281_1288_sequence_lock_verdict=pass
window_1281_1288_sequence_lock_committed
phase_1282_context_capsule_v5_51_refresh_next
window_1281_1288_no_public_rc_or_public_activation
human_question_escalation_required_for_uncertain_authority
```

This lock fixes the Window 1281-1288 phase order, sensitivity gates, capsule
refresh route, public claimability authority decision route, claimability
verifier/API boundary route, TransportPrincipal public-path activation preflight
route, sidecar public projection/privacy preflight route, release
publication/signing authorization preflight route, and closure gate. It does
not mutate runtime code, the CDL register, signed Genesis v0.1, Genesis Atlas
artifacts, release keys, public repository state, public P2P state, public
sidecar/projection serving, public claimability, wallet spend/transfer/withdrawal
authority, ECU minting, ILC settlement, public release artifacts, or v0.2
signing state.

---

## 2. Baseline Inputs and Canon

| Input | Window-entry role |
|-------|-------------------|
| `docs/PLANNING_INDEX.md` | Current planning frontier after Window 1273-1280 closure and Phase 1280 Fix1 hardening. |
| `docs/specs/ilc_antigravity_context_capsule_v5.50.md` | Current published capsule until Phase 1282 supersedes it; stale on CDL-087 and later window state. |
| `docs/phases/STATUS.md` | Actual status through Phase 1280 Fix1. |
| `docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md` | Closed-window baseline and carry-forward blocker list. |
| `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md` | Prior closed sequence lock and sensitive-gate precedent. |
| `docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md` | Planning-only candidate guidance consumed by this lock. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Current controlling public-RC roadmap and Phase 1280/Fix1 addenda. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL register; CDL-087 is ratified by Phase 1278 Fix1 and CDL-088 is not opened. |
| `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md` | CDL-087 ratification proof and public-path non-activation boundary. |
| `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md` | Prepublication inventory only; no publication, release artifacts, release keys, envelopes, Genesis mutation, or v0.2 signing. |
| `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md` | Local proof-binding boundary; no public/non-loopback claimability API. |
| `docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md` | Local conversion-sweeper skeleton; no public claimability, wallet spend, ECU minting, or settlement. |
| `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md` | Internal `PUBLIC_RC_EXCLUDE` TransportPrincipal public-path preflight helper; no public P2P or public fetch serving. |
| `docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md` | Internal `PUBLIC_RC_EXCLUDE` sidecar public-path preflight helper; no listener, bind, or public projection endpoint. |
| `docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md` | H-020..H-028 and IP-001..IP-006 planning registry; no IP filing, publication, or public-RC authority. |
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | Existing local conversion-sweeper runtime skeleton. |
| `ilc_core/ledger/claimability_proof_binding_runtime.py` | Existing local proof-binding helper; marked internal helper surface. |
| `ilc_core/network/d2d/transport_principal_public_path_preflight.py` | Existing internal public-path preflight helper; not a public-P2P activation. |
| `ilc_core/graph/sidecar_public_path_preflight.py` | Existing internal sidecar public-path preflight helper; not a public endpoint. |

Window 1273-1280 is CLOSED / PASS through Phase 1280 with:

```text
window_1273_1280_closed_phase_1280
window_1273_1280_closure_gate_verdict=pass
phase_1280_window_1273_1280_closure_complete
window_1281_plus_sequence_lock_required_before_next_phase_assignment
public_rc_remains_blocked_after_phase_1280
```

Phase 1280 Fix1 completed docs-only planning hardening:

```text
phase_1280_fix1_hypergraph_laplacian_docs_hardened
h_series_020_plus_registered_phase_1280_fix1
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
public_rc_candidate_standard_preserved_phase_1280_fix1
public_rc_remains_blocked_after_phase_1280_fix1
```

---

## 3. Entry Discovery Audit

The Phase 1281 discovery pass used exact-token search only as a
schema/completion check. Before writing this lock, context discovery also used
broader concept searches over Window 1281-1288, capsule v5.51, public
claimability, verifier/API boundary, TransportPrincipal, public path, sidecar,
public projection, release publication, v0.2 signing, public RC, and denial
terms such as `deferred`, `blocked`, `not authorized`, `local-only`, `no
public`, `PUBLIC_RC_EXCLUDE`, `superseded`, `must not`, `no ECU minting`, `no
ILC settlement`, and `no release artifact`.

Discovery result:

| Check | Result |
|-------|--------|
| Required-token audit | Required Phase 1281 tokens were present in the Phase 1281 prompt before execution and are now recorded in this sequence lock, PLANNING_INDEX, STATUS, and walkthrough. |
| Concept-discovery search | Confirmed the active lanes are capsule v5.51 refresh, public claimability authority decision preflight, claimability verifier/API boundary preflight, TransportPrincipal public-path activation preflight, sidecar public projection/privacy/serving preflight, release publication/signing authorization preflight, and closure. |
| Contradiction and non-claim search | Confirmed public claimability remains inactive, non-loopback claimability APIs remain blocked, public/non-loopback sidecar projection remains blocked, public P2P and public fetch serving remain blocked, publication and release artifact production remain blocked, Genesis Atlas mutation/signing remains blocked, and v0.2 signing remains deferred. |
| Source expansion | Direct-read the current planning index, capsule v5.50, STATUS tail, Phase 1280 handoff, Window 1281-1288 candidate guidance, Roadmap v1.1, CDL register, CDL-087 ratification evidence, Phase 1274/1275 claimability packets, Phase 1277/1278 public-path packets, Phase 1279 release preflight, and Phase 1280 Fix1 hardening packet before locking the window. |

Standing discovery tokens:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Every executable phase in this window must perform the same four-part
discovery pass before coding or drafting:

- §0a Known-token audit.
- §0b Concept-discovery search.
- §0c Contradiction and non-claim search.
- §0d Source expansion and newly discovered tokens.

MemPalace may be used only as advisory retrieval support. A MemPalace result is
not canon until the returned repo path is direct-read and reconciled against
current `docs/PLANNING_INDEX.md`, current capsule, current
`docs/phases/STATUS.md`, and this active window lock.

Exact-token `rg` is a schema/completion check only. It verifies that known
phase markers and required tokens exist; it must not be used as the sole
context retrieval method. For §0b and §0d, search token components, synonyms,
neighboring ideas, older names, code symbols, file/path variants, and denial
terms before concluding that a concept or blocker is absent.

---

## 4. Window Entry State

### Capsule Refresh

Capsule v5.50 remains the latest published capsule at Phase 1281 entry, but it
was produced at Phase 1239 and is stale on CDL-087 ratification, Window
1273-1280 closure, Phase 1280 Fix1, and the current public-RC blocker map.
Phase 1282 is locked as a non-sensitive docs/canon refresh to publish v5.51.

```text
capsule_v5_51_refresh_recommended_after_phase_1280
phase_1282_context_capsule_v5_51_refresh_next
```

### Claimability

Phases 1274 and 1275 recorded only local conversion/proof boundaries:

```text
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
```

Phase 1283 is locked as the public claimability authority decision preflight.
It is sensitive and must not be executed without explicit `GO Phase 1283`.

### CDL-087 and Public Fetch/Projection

CDL-087 is ratified:

```text
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
```

Ratification does not activate public fetch serving, public sidecar/projection
serving, public P2P, public claimability, public RC, CDL-088, release artifacts,
Genesis Atlas mutation, or v0.2 signing:

```text
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

### TransportPrincipal and Sidecar Public Path

Phases 1277 and 1278 added internal helper preflights only:

```text
transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1
transport_principal_public_p2p_not_activated_phase_1277
non_loopback_projection_still_blocked_phase_1277
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
sidecar_public_serving_not_enabled_phase_1278
no_new_public_listener_phase_1278
non_loopback_bind_not_enabled_phase_1278
public_projection_endpoint_not_enabled_phase_1278
```

Phase 1285 and Phase 1286 remain sensitive preflights. No public P2P, public fetch serving, non-loopback bind, socket listener, HTTP endpoint, peer
discovery, or public projection serving is authorized by this lock.

### Release, Publication, and Signing

Phase 1279 recorded prepublication inventory only:

```text
release_manifest_allowlist_publication_preflight_phase_1279.v0.1
public_repository_publication_not_authorized_phase_1279
release_artifact_production_not_authorized_phase_1279
v0_2_signing_not_authorized_phase_1279
source_allowlist_export_not_executed_phase_1279
release_keys_not_generated_phase_1279
release_envelope_not_produced_phase_1279
genesis_atlas_mutation_not_authorized_phase_1279
```

Phase 1287 remains a sensitive authorization preflight. Source publication,
release artifact production, release keys, release envelopes, Genesis Atlas
mutation/regeneration/signing, and v0.2 signing remain blocked until explicit authority exists.

---

## 5. Locked Phase Order

| Order | Phase | Topic | Sensitivity | Gate |
|-------|-------|-------|-------------|------|
| 1 | 1281 | Window 1281-1288 sequence lock | **SENSITIVE** | `GO Phase 1281` consumed |
| 2 | 1282 | Context Capsule v5.51 frontier refresh | NON-SENSITIVE docs/canon refresh only | Executable after Phase 1281 passes |
| 3 | 1283 | Public claimability authority decision preflight | **SENSITIVE** | Requires `GO Phase 1283`; activation requires explicit human authorization |
| 4 | 1284 | Public claimability verifier/API boundary preflight | **SENSITIVE** | Requires `GO Phase 1284`; no public endpoint by default |
| 5 | 1285 | TransportPrincipal public-path activation preflight | **SENSITIVE** | Requires `GO Phase 1285`; no public P2P or public fetch serving by default |
| 6 | 1286 | Sidecar public projection privacy/serving preflight | **SENSITIVE** | Requires `GO Phase 1286`; no listener or non-loopback bind by default |
| 7 | 1287 | Release publication and v0.2 signing authorization preflight | **SENSITIVE** | Requires `GO Phase 1287`; no publication/signing by default |
| 8 | 1288 | Window 1281-1288 closure gate | **SENSITIVE** | Requires `GO Phase 1288` |

Sensitive phases require separate explicit human authorization even if adjacent
non-sensitive phases are requested. Because Phase 1282 is non-sensitive, the
human request to continue through subsequent non-sensitive phases can advance
from Phase 1281 to Phase 1282 after this lock passes. Because Phase 1283 is
sensitive, no later phase is executable immediately after Phase 1282 without
explicit `GO Phase 1283`.

---

## 6. Human Escalation and Execution Rules

If a phase discovers a decision that cannot be resolved from committed canon and
would widen authority, mutate a CDL register row, enable public exposure,
enable claimability/spend semantics, produce public release artifacts, publish
source, generate/sign release material, mutate Genesis Atlas, or choose between
conflicting mathematical or security evidence routes, the phase must stop and prompt the human reviewer.

Do not silently choose broader authority. Default to the narrower
non-authorization path and record the unresolved question in the walkthrough,
STATUS entry, handoff, or carry-forward table.

```text
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
```

Phase-specific execution rules:

- Phase 1282 must be docs/canon refresh only and must not mutate runtime, CDL
  rows, Genesis, release artifacts, release keys, release envelopes, or public
  activation flags.
- Phase 1283 must record public claimability authority status and must default
  to no activation unless explicit human activation authority is present.
- Phase 1284 must not add a public/non-loopback claimability endpoint by
  default; any helper remains internal and `PUBLIC_RC_EXCLUDE` unless explicitly
  reviewed.
- Phase 1285 must not activate public P2P or public fetch serving by default.
- Phase 1286 must not add a listener, non-loopback bind, public host, wildcard
  bind, peer discovery, public fetch serving, or public sidecar/projection
  serving by default.
- Phase 1287 must not publish source, produce public release artifacts,
  generate release keys, produce release envelopes, mutate Genesis Atlas, or
  authorize v0.2 signing by default.
- Phase 1288 must close or carry forward each blocker honestly; it must not
  convert a preflight, graph pass, inventory pass, or capsule refresh into
  public-RC authority.

### Non-Claims

This sequence lock does not authorize:

- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- source allowlist export execution;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback sidecar/projection serving;
- public claimability activation;
- public claimability API activation;
- wallet withdrawal, wallet transfer, or wallet spend semantics;
- wallet signing authority or ledger-write authority;
- CDL mutation or CDL-088 opening;
- ECU mint authorization;
- direct Werner ECU creation;
- ILC settlement or withdrawal runtime activation;
- release-key generation;
- release envelope production;
- public release artifact production;
- v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- IP filing or paper publication;
- immutable diagnostic mutation;
- production `commit.epoch` emission.

---

## 7. Carry-Forward Tokens

```text
window_1281_1288_sequence_lock_committed
window_1281_1288_sequence_lock_verdict=pass
phase_1282_context_capsule_v5_51_refresh_next
window_1281_1288_no_public_rc_or_public_activation
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
window_1281_1288_candidate_phase_grouping_recorded_after_phase_1280
window_1281_1288_not_open_until_sequence_lock
public_rc_remains_blocked_after_phase_1280
public_rc_remains_blocked_after_phase_1280_fix1
capsule_v5_51_refresh_recommended_after_phase_1280
public_claimability_activation_requires_explicit_human_authorization_phase_1283
public_claimability_activation_not_authorized_by_default_phase_1283
transport_principal_activation_required_before_public_projection_phase_1286
release_publication_and_v0_2_signing_still_authorization_gated_after_phase_1280
phase_1280_fix1_hypergraph_laplacian_docs_hardened
h_series_020_plus_registered_phase_1280_fix1
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
public_rc_candidate_standard_preserved_phase_1280_fix1
unknown_unknown_discovery_required_before_phase_execution
```

---

## 8. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1281_window_1281_1288_sequence_lock_walkthrough.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1281_window_1281_1288_sequence_lock.py -> validation
graph_delta=support_tests_changed:tests/test_window_1281_1288_prompt_drafts.py -> validation/frontier
```
