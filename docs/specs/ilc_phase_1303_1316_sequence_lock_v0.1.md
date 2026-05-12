# ILC Phase 1303-1316 Sequence Lock v0.1

**Date:** 2026-05-11
**Window:** 1303-1316
**Phase:** 1303
**Status:** LOCKED
**Human authorization:** `GO Phase 1303`
**Token:** `window_1303_1316_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1303-1316 is opened after explicit human authorization:

```text
GO Phase 1303
```

Verdict:

```text
window_1303_1316_sequence_lock_committed
window_1303_1316_sequence_lock_verdict=pass
phase_1304_context_capsule_v5_53_refresh_next
window_1303_1316_no_public_rc_or_public_activation
rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate
human_question_escalation_required_for_uncertain_authority
```

This is a sequence lock only. It opens the implementation-hardening window and
records the locked phase order. It does not execute Phase 1304, implement any
sidecar, strip helpers, produce a public tree, activate any public path, or
claim public RC.

Phase 1304 is the next planned phase and is a non-sensitive docs/canon capsule
refresh after this lock. The user's authorization for this phase was only
`GO Phase 1303`, so execution stops after Phase 1303 unless the human reviewer
later authorizes Phase 1304 or a continue-through-non-sensitive instruction.

The `rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate`
token is retained because it is already recorded in the forward planning. This
lock narrows Phase 1313 to readiness-only inside Window 1303-1316. Any
activation-style public fetch/P2P phase requires a separate Rust public-P2P substrate ADR/integration gate before it can be executed.

---

## 2. Baseline Inputs And Canon

| Input | Window-entry role |
|-------|-------------------|
| `docs/PLANNING_INDEX.md` | Current planning frontier after Phase 1302 closure and draft Window 1303-1316 guidance. |
| `docs/specs/ilc_antigravity_context_capsule_v5.52.md` | Current capsule through Phase 1302 closure; v5.53 is next. |
| `docs/phases/STATUS.md` | Actual status through Phase 1302 before this sequence lock. |
| `docs/specs/ilc_window_1289_1302_handoff_1302_v0.1.md` | Closed-window baseline and carry-forward blocker list. |
| `docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md` | Candidate implementation-hardening guidance consumed by this lock. |
| `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | Forward plan for implementation hardening, release dry run, final RC, packaging, and signing gates. |
| `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md` | Materialized-public-tree rule and `PUBLIC_RC_EXCLUDE` disposition model. |
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | Harness-agnostic graph-native sidecar suite architecture. |
| `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md` | Private/local confidential coordination sidecar routing. |
| `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` | TransportPrincipal, Rust public-P2P, OpenClaw/NemoClaw host, and value-path planning basis. |
| `docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md` | Public-RC blocker classes and graph-native sidecar runway context. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Controlling public-RC blocker map. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL register; CDL-087 is ratified and CDL-088 is not opened. |

Standing retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

---

## 3. Entry Discovery Audit

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | Required Phase 1303 tokens were searched before this lock. Before this packet, the Phase 1303-specific tokens existed only in the Phase 1303 prompt and draft guidance/planning tests; they are now published in this lock, PLANNING_INDEX, STATUS, walkthrough, and focused tests. |
| Section 0b Concept-discovery search | Searched Window 1303, Window 1303-1316, implementation hardening, claimability verifier, receipt verifier, graph-native sidecar, `PUBLIC_RC_EXCLUDE`, TransportPrincipal, projection privacy, Rust public P2P, wallet-facing withdrawal requests, ECU minting, ILC settlement, and public RC. |
| Section 0c Contradiction and non-claim search | Searched blocked, deferred, not authorized, not enabled, local-only, no public, no listener, no release, no signing, `PUBLIC_RC_EXCLUDE`, no wallet, no ECU minting, and no ILC settlement. No source granted public activation, publication, signing, CDL mutation, Genesis mutation/signing, wallet/ECU/ILC economics, helper stripping, or public-RC claim authority. |
| Section 0d Source expansion | Direct-read the current planning index, Capsule v5.52, STATUS tail, Phase 1302 handoff, Window 1303-1316 guidance, forward packaging/signing plan, public-RC packaging architecture gate, graph-native sidecar suite architecture, CCSS forward plan, network/value-path planning, public-RC runway, roadmap, CDL register, and prompt/test scaffolding. |

Exact-token `rg` remains only a schema and completion check. Future phases in
this window must also search token components, synonyms, neighboring concepts,
older names, code symbols, file/path variants, historical literature, and
denial terms before treating a blocker or implementation concept as absent.

---

## 4. Locked Phase Order

| Order | Phase | Scope | Sensitivity | Authorization boundary |
|-------|-------|-------|-------------|------------------------|
| 1 | 1303 | Window 1303-1316 sequence lock | SENSITIVE | Executed by `GO Phase 1303`; opens no public RC authority. |
| 2 | 1304 | Context Capsule v5.53 frontier refresh | NON-SENSITIVE docs/canon refresh after Phase 1303 | Next planned phase; not executed by this lock. |
| 3 | 1305 | Offline/local claimability and receipt verifier sidecar/library, no API serving | SENSITIVE | No public API, no public claimability activation. |
| 4 | 1306 | Proof-binding, canonical hash, and negative-path tests | SENSITIVE | Proof safety tests only; no public verifier service. |
| 5 | 1307 | Graph-native sidecar registry/manifest plus claimability package profile hardening | SENSITIVE | Local/package metadata and profile hardening only; no publication. |
| 6 | 1308 | Helper pruning/replacement plan with `PUBLIC_RC_EXCLUDE` enforcement and truth-primitive sidecar boundary | SENSITIVE | Planning/disposition only; no helper promotion, marker removal, stripping, or export. |
| 7 | 1309 | TransportPrincipal admission sidecar lifecycle implementation hardening | SENSITIVE | Lifecycle substrate only; no public-path activation. |
| 8 | 1310 | Revocation, replay, admission, and ban tests | SENSITIVE | Hostile-network readiness tests only; public path remains blocked. |
| 9 | 1311 | Local graph/memory projection sidecar and public-safe projection implementation | SENSITIVE | Local/in-process or private projection substrate only; no public serving. |
| 10 | 1312 | Projection privacy and field-filtering tests | SENSITIVE | Privacy/filtering tests only; no public projection endpoint. |
| 11 | 1313 | Public fetch/P2P readiness candidate, default off with no activation | SENSITIVE | Readiness-only; no public P2P, public fetch serving, listener, or public transport claim. |
| 12 | 1314 | Wallet-facing withdrawal, transfer, and spend request semantics preflight | SENSITIVE | Preflight only; no wallet write/signing/ledger-write authority. |
| 13 | 1315 | ECU minting and ILC settlement boundary preflight | SENSITIVE | Preflight only; no ECU minting, settlement, or withdrawal runtime. |
| 14 | 1316 | Window closure and implementation audit | SENSITIVE | Closure/classification only. |

---

## 5. Scope Notes And Split Warnings

Phase 1308 is the first explicit `PUBLIC_RC_EXCLUDE` helper disposition
planning point in this window. It must map each current helper to one of:

| Disposition | Meaning |
|-------------|---------|
| `replace_before_export` | Implement a public-safe module and remove exported-code dependencies on the internal helper before any export materialization. |
| `strip_from_export` | Exclude the helper from public source/package/release artifacts and prove exported code has no import dependency on it. |
| `defer_public_rc` | Carry the blocker forward and do not claim public RC for the affected package profile. |

Phase 1308 must not execute source export, public package publication, helper
promotion, marker removal, or helper stripping. Dry-run materialization remains
routed to Phase 1319. Export execution remains routed to Phase 1333 if later
explicitly authorized.

Phases 1309 and 1311 are umbrella implementation scopes. If direct code review
shows either slice is too large to execute safely in one phase, the phase must
stop and request a narrowed split rather than hiding multiple architectural
lifts in a single phase.

Phase 1313 is locked as readiness-only. The sequence does not insert a Rust
public-P2P substrate implementation into Window 1303-1316. It records that any
future activation-style public fetch/P2P candidate requires a separate Rust public-P2P substrate ADR/integration gate first.

---

## 6. Graph-Native Sidecar Ordering

| Order | Sidecar | Locked phase target |
|-------|---------|---------------------|
| 1 | Offline claimability and receipt verifier sidecar | 1305/1306 |
| 2 | Sidecar registry and deterministic manifest | 1307 |
| 3 | Truth primitive submission sidecar boundary | 1308 |
| 4 | TransportPrincipal admission sidecar substrate | 1309/1310 |
| 5 | Local graph/memory projection sidecar | 1311/1312 |
| 6 | Confidential coordination local preview profile prerequisites | 1307 and 1311/1312, with implementation/dry-run routed to 1324-1329 |

OpenClaw, NemoClaw, Codex-style agents, and future first-party ILC harnesses are
hosts or operators of the graph-native suite. They are not protocol substrates.
DigitalOcean/OpenClaw tests remain private deployment evidence until separate
public serving, publication, and release gates close.

---

## 7. Human Escalation Rule

If a phase discovers a decision that cannot be resolved from committed canon and
would widen authority, mutate a CDL row, open CDL-088, enable public exposure,
enable claimability/spend semantics, publish source, produce release artifacts,
generate or sign release material, mutate or sign Genesis Atlas, sign v0.2,
activate public confidential messaging or coordination serving, or choose
between conflicting mathematical/security evidence routes, the phase must stop and prompt the human reviewer.

```text
default_to_no_authorization_when_canon_is_ambiguous
human_question_escalation_required_for_uncertain_authority
```

---

## 8. Non-Authorization Boundary

Phase 1303 does not authorize public RC, public launch, public repository
publication, public package publication, source allowlist export execution,
source publication, materialized export manifest production, clean public
export tree production, release artifact production, release-key generation,
release envelope production, release signing material generation, public
claimability activation, public claimability API activation, public verifier
service activation, public claim endpoint activation, public P2P exposure,
public fetch serving, public sidecar/projection serving, non-loopback bind,
wildcard bind, public host bind, public listener, socket listener, HTTP route
activation, peer discovery, TransportPrincipal public-path activation, public
credential issuer authority, credential lifecycle policy activation, public
revocation registry activation, public replay cache activation, admission
policy activation, ban registry activation, public rate-limit state activation,
privacy policy activation, helper promotion, marker removal, helper stripping,
CDL mutation, CDL-088 opening, Genesis Atlas mutation, Genesis Atlas
regeneration, Genesis Atlas signing, v0.2 signing, IP filing, paper
publication, patent-sensitive public disclosure, public confidential messaging,
public confidential coordination serving, wallet-facing withdrawal requests,
wallet-facing transfer requests, wallet-facing spend requests,
wallet-provider signing authority, wallet-provider ledger-write authority, ECU
minting, ILC settlement, withdrawal runtime activation, immutable diagnostic
mutation, or production `commit.epoch` emission.

Exact non-authorization phrase guard:

```text
public RC claim
public claimability API activation
public verifier service activation
public P2P exposure
public fetch serving
public sidecar/projection serving
source allowlist export execution
release-key generation
release envelope production
helper promotion
marker removal
helper stripping
Genesis Atlas mutation/regeneration/signing
v0.2 signing
CDL-088 opening
wallet-facing withdrawal request
ECU minting
ILC settlement
public confidential messaging
public confidential coordination serving
```

---

## 9. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1303_window_1303_1316_sequence_lock.py -> validation
graph_delta=support_only:docs/phases/phase_1303_window_1303_1316_sequence_lock_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```
