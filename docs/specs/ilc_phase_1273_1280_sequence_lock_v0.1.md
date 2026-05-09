# ILC Phase 1273-1280 Sequence Lock v0.1

**Date:** 2026-05-09
**Window:** 1273-1280
**Phase:** 1273
**Status:** LOCKED
**Human authorization:** `GO Phase 1273 and any subsequent non-sensitive phases as well, in order`
**Token:** `window_1273_1280_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1273-1280 is opened after explicit human authorization:

```text
GO Phase 1273
```

The "subsequent non-sensitive phases" clause is evaluated against this lock.
The next locked phase, Phase 1274, is sensitive, so no later non-sensitive phase
is executable immediately after Phase 1273.

no later non-sensitive phase is executable immediately after Phase 1273.

Verdict:

```text
window_1273_1280_sequence_lock_verdict=pass
window_1273_1280_sequence_lock_committed
phase_1274_cdl048_conversion_sweeper_runtime_requires_explicit_go
window_1273_1280_no_public_rc_or_public_claimability_activation
human_question_escalation_required_for_uncertain_authority
```

This lock fixes the Window 1273-1280 phase order, sensitivity gates,
claimability/conversion-sweeper runtime route, proof-binding route, CDL-087
authorization-preflight route, TransportPrincipal public-path route, sidecar
public-path preflight route, release manifest/source allowlist prepublication
route, and closure gate. It does not mutate runtime code, the CDL register,
signed Genesis v0.1, Genesis Atlas artifacts, release keys, public repository
state, public P2P state, public sidecar/projection serving, public
claimability, wallet spend/transfer/withdrawal authority, ECU minting, ILC
settlement, public release artifacts, or v0.2 signing state.

---

## 2. Baseline Inputs and Canon

| Input | Window-entry role |
|-------|-------------------|
| `docs/PLANNING_INDEX.md` | Current planning frontier after Window 1265-1272 closure and Window 1273-1280 planning-package hardening. |
| `docs/phases/STATUS.md` | Actual status through Phase 1272, plus the Phase 1271 Fix1 audit-hardening entry. |
| `docs/specs/ilc_antigravity_context_capsule_v5.50.md` | Current capsule until superseded; it was produced before Phase 1278 Fix1 and its CDL-087 not-ratified statement is superseded by the current register. Public launch obligations and v0.2 signing remain deferred. |
| `docs/specs/ilc_window_1265_1272_handoff_1272_v0.1.md` | Closed-window baseline and carry-forward blocker list. |
| `docs/specs/ilc_phase_1265_1272_sequence_lock_v0.1.md` | Prior closed sequence lock and sensitive-gate precedent. |
| `docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md` | Planning-only candidate guidance consumed by this lock. |
| `docs/specs/ilc_window_1273_1280_prompt_package_outside_audit_2026_05_09_v0.1.md` | Outside audit and Session-Start Canon hardening record. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Current controlling public-RC roadmap and Phase 1272 closure addendum. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL register; CDL-048 is ratified and CDL-087 is ratified by Phase 1278 Fix1. |
| `docs/specs/ilc_cdl_087_sensitive_ratification_review_1266_v0.1.md` | CDL-087 review/no-ratification/no-register-mutation boundary. |
| `docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md` | Pre-public TransportPrincipal helper and non-loopback projection block. |
| `docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md` | No-new-listener and public/non-loopback sidecar projection block. |
| `docs/specs/ilc_werner_default_topology_pressure_profile_1269_v0.1.md` | Werner evidence-only profile; no economic activation. |
| `docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md` | Gap 13 and CDL-048 conversion-sweeper requirements; no public claimability activation. |
| `docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md` | ATLAS-G-006 graph gate pass without release authorization. |
| `docs/phases/phase_1271_fix1_atlas_g_006_manifest_profile_consistency_hardening_walkthrough.md` | Supplied-manifest profile mismatch fail-closed hardening. |
| `ilc_core/protocol/public_wallet_runtime.py` | Current wallet surfaces expose `claimability_state: deferred`. |
| `ilc_core/protocol/public_receipt_runtime.py` | Current receipt surface for future proof/root binding. |
| `ilc_core/rc/atlas_graph_discipline.py` | Current graph gate records release artifacts blocked. |
| `ilc_core/graph/sidecar_query_runtime.py` | Current in-process/local sidecar query runtime; no public server. |

Window 1265-1272 is CLOSED / PASS through Phase 1272 with:

```text
window_1265_1272_closed_phase_1272
window_1265_1272_closure_gate_verdict=pass
phase_1272_window_1265_1272_closure_complete
window_1273_plus_sequence_lock_required_before_next_phase_assignment
```

The Window 1273-1280 planning package was audited without authority expansion:

```text
window_1273_1280_candidate_phase_grouping_recorded_after_phase_1272
planning_index_session_start_frontier_hardened_after_audit
window_1273_1280_audit_no_authority_expansion
```

Public RC remains blocked after Phase 1272:

```text
public_rc_remains_blocked_after_phase_1272
```

---

## 3. Entry Discovery Audit

The Phase 1273 discovery pass used exact-token search only as a
schema/completion check. Before writing this lock, context discovery also used
broader concept searches over Window 1273-1280, claimability, conversion
sweeper, CDL-048, proof binding, CDL-087, ratification, TransportPrincipal,
sidecar, non-loopback projection, release manifest, source allowlist, public
RC, v0.2 signing, and denial terms such as `deferred`, `blocked`, `not
authorized`, `not ratified`, `prelocked`, `local-only`, `no public`, `does not
open`, `superseded`, `must not`, `no release artifact`, `no signing`, and `no
register mutation`.

Discovery result:

| Check | Result |
|-------|--------|
| Required-token audit | Required Phase 1273 tokens were present in the Phase 1273 prompt before execution and are now recorded in this sequence lock, PLANNING_INDEX, STATUS, and walkthrough. |
| Concept-discovery search | Confirmed the active lanes are CDL-048 conversion-sweeper runtime skeleton, claimability proof binding, CDL-087 authorization preflight, TransportPrincipal public-path ADR/runtime preflight, sidecar non-loopback/public preflight, release manifest/source allowlist prepublication, and closure. |
| Contradiction and non-claim search | Confirmed CDL-087 is not ratified, public/non-loopback sidecar projection remains blocked, public P2P remains blocked, public RC remains blocked, public claimability remains inactive, wallet spend/transfer/withdrawal remains disabled, ATLAS-G public release artifacts remain unauthorized, source publication remains unauthorized, and v0.2 signing remains deferred. |
| Source expansion | Direct-read the current planning index, phase status, capsule v5.50, Phase 1272 handoff, prior sequence lock, Window 1273-1280 candidate guidance, outside audit record, Roadmap v1.1, CDL register, Phase 1266-1271 lane artifacts, and relevant runtime surfaces before locking the window. |

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

### Claimability and CDL-048

CDL-048 is already ratified in the CDL register as the ECU mandatory conversion
deadline framework:

```text
CDL-048
ecu_conversion_deadline = 4 issuance epochs
```

Phase 1270 records requirements only:

```text
gap13_claimability_conversion_sweeper_preflight_phase_1270.v0.1
public_claimability_runtime_not_activated_phase_1270
cdl_048_conversion_sweeper_requirements_recorded_phase_1270
wallet_withdrawal_transfer_spend_not_enabled_phase_1270
```

The conversion sweeper runtime is not complete. Public claimability, wallet
withdrawal, wallet transfer, wallet spend, ECU minting, and ILC settlement
remain blocked. Phase 1274 may implement a bounded runtime skeleton only after
explicit GO and must preserve exact numeric, epoch-deadline, replay, double
conversion, and canonical JSON/root-binding guardrails.

Phase 1274 may implement a bounded runtime skeleton only after explicit GO.

### CDL-087

At initial Window 1273-1280 lock time, CDL-087 remained:

```text
OPEN / PRELOCKED / NOT RATIFIED
```

Phase 1266 records:

```text
cdl_087_ratification_decision_phase_1266=no_ratification_no_register_mutation
cdl_087_ratification_not_executed_by_default_phase_1266
cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1266
```

The sequence lock itself did not ratify CDL-087 and did not mutate the CDL
register. Phase 1276 was an authorization preflight by default; any later
register mutation required explicit human ratification authorization and a
fresh proof of all applicable conditions. Phase 1278 Fix1 later received that
explicit authorization and ratified CDL-087.

### TransportPrincipal, Sidecar, and Public Path

Phase 1267 is a pre-public helper only:

```text
transport_principal_runtime_identity_pre_public_path_phase_1267.v0.1
transport_principal_runtime_not_public_p2p_activation_phase_1267
requester_id_rate_limit_fallback_still_forbidden_phase_1267
non_loopback_projection_still_blocked_phase_1267
```

Phase 1268 records no listener and keeps public/non-loopback projection
blocked:

```text
sidecar_loopback_projection_endpoint_boundary_phase_1268.v0.1
sidecar_loopback_only_no_non_loopback_serving_phase_1268
sidecar_public_path_still_blocked_phase_1268
transport_principal_required_before_non_loopback_projection_phase_1268
```

No public P2P, public fetch serving, public sidecar/projection serving,
non-loopback bind, socket listener, or HTTP server is authorized by this lock.

### Release and Publication

ATLAS-G-006 selected-profile graph reachability passed, but only as a graph
gate:

```text
graph_reachability_verdict=pass_graph_gate_only_release_artifacts_blocked
public_release_artifact_not_authorized_phase_1271
no_genesis_atlas_mutation_phase_1271
atlas_g_006_manifest_profile_mismatch
```

Release manifest/source allowlist work may be prepared only as inventory and
validation unless a later phase receives explicit publication/signing
authorization. Public repository publication, public package publication,
public release artifacts, release-key generation, release envelope production,
Genesis Atlas mutation/regeneration/signing, and v0.2 signing remain blocked.

release manifest/source allowlist work may be prepared only as inventory.

---

## 5. Locked Phase Order

| Order | Phase | Topic | Sensitivity | Gate |
|-------|-------|-------|-------------|------|
| 1 | 1273 | Window 1273-1280 sequence lock | **SENSITIVE** | `GO Phase 1273` consumed |
| 2 | 1274 | CDL-048 conversion-sweeper runtime skeleton and exact ECU lot ledger boundary | **SENSITIVE** | Requires `GO Phase 1274`; no public claimability activation |
| 3 | 1275 | Public claimability proof-binding runtime boundary | **SENSITIVE** | Requires `GO Phase 1275`; no public API, withdrawal, transfer, or spend semantics |
| 4 | 1276 | CDL-087 ratification authorization preflight / decision packet | **SENSITIVE** | Requires `GO Phase 1276`; no register mutation by default |
| 5 | 1277 | TransportPrincipal public-path ADR and runtime integration preflight | **SENSITIVE** | Requires `GO Phase 1277`; no public P2P activation |
| 6 | 1278 | Sidecar non-loopback/public projection authorization preflight | **SENSITIVE** | Requires `GO Phase 1278`; no listener or public serving by default |
| 7 | 1279 | Release manifest and source allowlist pre-publication preflight | NON-SENSITIVE only if inventory/procedure docs and validation; no publication, signing, or release artifact production | After Phase 1278 |
| 8 | 1280 | Window coherence, blocker classification, and closure gate | **SENSITIVE** | Requires `GO Phase 1280` |

Sensitive phases require separate explicit human authorization even if adjacent
non-sensitive phases are requested. Because Phase 1274 is sensitive, the human
request to continue through subsequent non-sensitive phases cannot advance past
Phase 1273 under this lock.

---

## 6. Phase 1278 Fix1 Ratification Addendum

After Phase 1278 passed, the human reviewer explicitly authorized the planned
CDL-087 Fix phase:

```text
GO Phase 1278 Fix1. I authorize CDL-087 ratification and CDL register mutation
```

Phase 1278 Fix1 consumed that authorization, re-proved the six CDL-087
ratification conditions, and mutated only the CDL-087 row in
`docs/specs/ilc_constitutional_decision_log_v0.1.md` from `open` to
`ratified`.

```text
cdl087_ratification_evidence_phase_1278_fix1.v0.1
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

This addendum does not alter the locked order for Phase 1279 or Phase 1280.
Phase 1279 remains a non-sensitive inventory/prepublication preflight unless a
later human instruction widens authority.

Phase 1278 Fix1 does not authorize public fetch serving, public
sidecar/projection serving, non-loopback bind, new listener, public P2P, public
claimability, public release artifacts, public RC, CDL-088 opening, Genesis
Atlas mutation, or v0.2 signing.

## 7. Human Escalation and Execution Rules

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

Phase-specific execution rules:

- Phase 1274 must use exact numeric boundaries, reject non-finite Decimal input
  before arithmetic, avoid float economic state, bind canonical JSON with
  `sort_keys=True` and `allow_nan=False`, and preserve no public claimability
  activation.
- Phase 1275 must remain a proof/root binding boundary and must not open a
  public claimability API or wallet spend/transfer/withdrawal semantics.
- Phase 1276 preserved no CDL register mutation because it lacked ratification
  authority. Phase 1278 Fix1 later received explicit authority and executed the
  narrow CDL-087 ratification/register mutation.
- Phase 1277 must not activate public P2P; JSON/body `requester_id`,
  `client_ip`, AgentID, and harness identity remain forbidden as public-path
  rate-limit, admission, ban, or replay keys.
- Phase 1278 must not add a listener, non-loopback bind, public host, wildcard
  bind, public fetch serving, or public sidecar/projection serving by default.
- Phase 1279 must not publish source, produce public release artifacts,
  generate release keys, produce release envelopes, mutate Genesis Atlas, or
  authorize v0.2 signing.
- Phase 1280 must close or carry forward each blocker honestly; it must not
  convert a preflight, graph pass, or inventory pass into public-RC authority.

### Non-Claims

This sequence lock does not authorize:

- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback sidecar/projection serving;
- public claimability activation;
- wallet withdrawal, wallet transfer, or wallet spend semantics;
- wallet signing authority or ledger-write authority;
- CDL mutation beyond the authorized CDL-087 Phase 1278 Fix1 register mutation,
  Werner CDL opening/prelock, or CDL-088 opening;
- ECU mint authorization;
- direct Werner ECU creation;
- ILC settlement or withdrawal runtime activation;
- release-key generation;
- release envelope production;
- public release artifact production;
- v0.2 signing;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission.

---

## 8. Carry-Forward Tokens

```text
window_1273_1280_sequence_lock_committed
window_1273_1280_sequence_lock_verdict=pass
phase_1274_cdl048_conversion_sweeper_runtime_requires_explicit_go
window_1273_1280_no_public_rc_or_public_claimability_activation
human_question_escalation_required_for_uncertain_authority
default_to_no_authorization_when_canon_is_ambiguous
window_1273_1280_candidate_phase_grouping_recorded_after_phase_1272
window_1273_1280_audit_no_authority_expansion
public_rc_remains_blocked_after_phase_1272
cdl_087_register_mutation_requires_explicit_ratification_authorization_phase_1276
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
public_claimability_runtime_still_requires_conversion_sweeper_after_phase_1272
transport_principal_required_before_public_projection_after_phase_1272
release_manifest_allowlist_publication_still_authorization_gated_after_phase_1272
unknown_unknown_discovery_required_before_phase_execution
```

---

## 9. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1273_window_1273_1280_sequence_lock_walkthrough.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1273_window_1273_1280_sequence_lock.py -> validation
```
