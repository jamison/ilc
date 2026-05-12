# ILC Window 1303-1316 Candidate Phase Grouping v0.1

**Status:** Guidance consumed and locked by Phase 1303 sequence lock.
**Recorded:** 2026-05-11.
**Authority:** This document recorded planning support until Phase 1303. Phase
1303 consumed it as guidance and opened the sequence lock in
`docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md`. This guidance does not open
any additional authority beyond that sequence lock, and does not itself
execute source export, publish a repository or package, produce release
artifacts, generate release keys or envelopes, mutate Genesis Atlas, sign v0.2,
activate public claimability, activate public P2P/fetch/sidecar serving, or
authorize wallet/ECU/ILC economics.

```text
window_1303_1316_candidate_phase_grouping_drafted_after_phase_1302
window_1303_1316_not_open_until_sequence_lock
phase_1303_window_1303_1316_sequence_lock_required
window_1303_1316_implementation_hardening_public_rc_blocked
rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate
graph_native_sidecar_essential_suite_routed_window_1303_1316
public_rc_exclude_helper_stripping_planning_phase_1308
confidential_coordination_local_preview_prereqs_routed_phase_1307_1311_1312
window_1303_1316_candidate_phase_grouping_consumed_by_phase_1303_sequence_lock
```

## 1. Confirmation

The proposed Window 1303-1316 plan is still consistent with the current
committed canon and is now consumed by the Phase 1303 sequence lock. Phase 1302
closed Window 1289-1302 with a pass-with-carry-forward verdict, not a public-RC
pass, and explicitly required a new Window 1303+ sequence lock before assigning
further phases. Phase 1303 now supplies that lock without granting public-RC,
publication, activation, signing, or economics authority.

The plan is correct with these guardrails:

- Phase 1303 is the sequence lock before any Phase 1304-1316 execution.
- Phase 1304 is the capsule refresh after the sequence lock.
- Phases 1305-1312 are the right implementation-hardening block for the local
  claimability verifier, graph-native sidecar registry, helper disposition,
  TransportPrincipal substrate, and projection privacy work.
- Phase 1308 is the first explicit `PUBLIC_RC_EXCLUDE` stripping-planning point,
  but it must not execute export or strip helpers from a public tree.
- Phase 1313 cannot become a real public P2P/fetch activation unless a Rust
  public-P2P substrate ADR/integration gate has already passed or the sequence
  lock explicitly narrows Phase 1313 to a default-off/no-public-transport
  candidate.
- Phases 1314 and 1315 are preflight-only value-path phases. Any future value
  activation must be a later gate outside this draft guidance.
- Phase 1316 closes the window and classifies blockers as closed, open, or
  carried forward.

## 2. Canon Basis

| Source | Relevance |
|--------|-----------|
| `docs/specs/ilc_window_1289_1302_handoff_1302_v0.1.md` | Current handoff: public RC remains blocked and Window 1303+ sequence lock is required. |
| `docs/specs/ilc_antigravity_context_capsule_v5.52.md` | Current capsule through Phase 1302 closure. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Public-RC blocker map, graph-native sidecar routing, and post-1302 carry-forward blockers. |
| `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | Candidate plan for 1303-1342 packaging, signing, graph-native sidecars, CCSS, and helper stripping. |
| `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md` | Materialized public-tree rule and `PUBLIC_RC_EXCLUDE` disposition model. |
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | Harness-agnostic graph-native sidecar suite architecture. |
| `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md` | Routes private/local confidential coordination prerequisites into Phases 1307 and 1311/1312. |
| `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` | TransportPrincipal, Rust public-P2P substrate, OpenClaw/NemoClaw host posture, and value-path split. |
| `docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md` | Public-RC route: graph-native sidecar suite hosted by OpenClaw/NemoClaw first, no public ILC P2P claim by default. |

Exact-token search is not enough for this window. Future execution prompts must
continue the known-token, concept-discovery, contradiction/non-claim, and source
expansion discipline recorded in the Phase 1289-1302 window.

## 3. Human Escalation Discipline

If any phase discovers uncertain authority, contradictory canon, a widening
decision, or a scope question that cannot be resolved from committed documents,
it must stop and prompt the human reviewer.

```text
human_question_escalation_required_for_uncertain_authority
```

Default to the narrower no-authorization route. This guidance does not activate
public serving. This document does not activate public claimability. It does
not authorize public sidecar/projection serving, authorize ECU minting,
authorize ILC settlement or withdrawal runtime, authorize source publication,
or authorize v0.2 signing.

## 4. Candidate Phase Order

| Phase | Scope | Sensitivity | Primary blocker or lane |
|-------|-------|-------------|--------------------------|
| 1303 | Sequence lock for implementation hardening | SENSITIVE | Opens no public RC authority by itself; consumes Phase 1302 handoff and this guidance. |
| 1304 | Capsule v5.53 refresh | NON-SENSITIVE after Phase 1303 lock | Prevents stale frontier before implementation work. |
| 1305 | Offline/local claimability and receipt verifier sidecar/library, no API serving | SENSITIVE | Gap 13 verifier substrate; no public API or public claimability activation. |
| 1306 | Proof-binding, canonical hash, and negative-path tests | SENSITIVE | Forged receipts, replay, exact numeric, and canonical JSON proof safety. |
| 1307 | Graph-native sidecar registry/manifest plus claimability package profile hardening | SENSITIVE | Gap 14 essential sidecar manifest, OpenClaw-compatible local bridge profile, `confidential_coordination_local_preview` declaration, package-profile integrity, source allowlist readiness. |
| 1308 | Helper pruning/replacement plan with `PUBLIC_RC_EXCLUDE` enforcement and truth-primitive sidecar boundary | SENSITIVE | Converts Phase 1293 keep-internal register into concrete replacement, stripping, or carry-forward decisions; no export. |
| 1309 | TransportPrincipal admission sidecar lifecycle implementation hardening | SENSITIVE | Gap 10 public-path identity lifecycle substrate; no public activation. |
| 1310 | Revocation, replay, admission, and ban tests | SENSITIVE | Gap 10/11 hostile-network readiness tests; public path remains blocked. |
| 1311 | Local graph/memory projection sidecar and public-safe projection implementation | SENSITIVE | Gap 9 local projection implementation, private/gated shard header projection, encrypted coordination-node reference, and privacy-filter blocker. |
| 1312 | Projection privacy and field-filtering tests | SENSITIVE | Field disclosure, identifier leakage, bounded serving blocker, and confidential-coordination projection non-leakage. |
| 1313 | Public fetch/P2P readiness candidate, default off with no activation | SENSITIVE | Gap 10 / CDL-087 readiness check only; real public activation remains outside this implementation-hardening window even if Rust public-P2P substrate evidence exists. |
| 1314 | Wallet-facing withdrawal, transfer, and spend request semantics preflight | SENSITIVE | Gap 13 public claimability user-action boundary; no wallet write authority; wallets remain adapters around ledger-truth objects. |
| 1315 | ECU minting and ILC settlement boundary preflight | SENSITIVE | Gap 12/13 value-path boundary; no minting or settlement activation. |
| 1316 | Window closure and implementation audit | SENSITIVE | Classifies implementation blockers closed/open/carried forward. |

## 5. `PUBLIC_RC_EXCLUDE` Disposition Rule

Phase 1308 is the first explicit stripping-planning point. It must produce an
inventory that maps each current `PUBLIC_RC_EXCLUDE` helper to one of:

| Disposition | Meaning |
|-------------|---------|
| `replace_before_export` | Implement a public-safe module and remove imports from the internal helper before any export materialization. |
| `strip_from_export` | Exclude the helper from public source/package/release artifacts and prove no exported code imports it. |
| `defer_public_rc` | Carry the blocker forward and do not claim public RC for the affected package profile. |

Phase 1308 must not execute source export, publish packages, strip helpers from
an exported public tree, remove markers, or promote helpers. Those decisions
remain dry-run materialization work in Phase 1319 and execution-gate work in
Phase 1333 if later explicitly authorized.

## 6. Essential Sidecar Ordering

| Order | Sidecar | Candidate phase target |
|-------|---------|------------------------|
| 1 | Sidecar registry and deterministic manifest | 1307 |
| 2 | Offline claimability and receipt verifier sidecar | 1305/1306 |
| 3 | Truth primitive submission sidecar boundary | 1308 |
| 4 | TransportPrincipal admission sidecar substrate | 1309/1310 |
| 5 | Local graph/memory projection sidecar | 1311/1312 |
| 6 | Confidential coordination local preview profile | 1307 prerequisites, 1311/1312 projection prerequisites, 1324-1329 implementation/dry-run lane |

OpenClaw/NemoClaw remain hosts or consumers for the graph-native suite, not
protocol substrates. DigitalOcean/OpenClaw tests remain private deployment
evidence and do not authorize public sidecar serving.

## 7. Scope Split Warnings

Phases 1309 and 1311 are candidate umbrella scopes. A future Phase 1303 sequence
lock may split either one into multiple integer phases if direct code review
shows the implementation is too broad for one phase.

Phase 1313 is also conditional. The sequence lock must either:

- insert an explicit Rust public-P2P substrate ADR/integration gate before
  Phase 1313; or
- keep Phase 1313 as a default-off readiness candidate with no public P2P,
  no public fetch serving, no listener, and no public transport claim.

## 8. Prompt Draft Registry

| Phase | Prompt draft |
|-------|--------------|
| 1303 | `docs/antigravity_tasks/antigravity_prompt__phase_1303_g8_window_1303_1316_sequence_lock.md` |
| 1304 | `docs/antigravity_tasks/antigravity_prompt__phase_1304_g8_context_capsule_v5_53_frontier_refresh.md` |
| 1305 | `docs/antigravity_tasks/antigravity_prompt__phase_1305_g8_offline_claimability_receipt_verifier_sidecar_library.md` |
| 1306 | `docs/antigravity_tasks/antigravity_prompt__phase_1306_g8_proof_binding_canonical_hash_negative_path_tests.md` |
| 1307 | `docs/antigravity_tasks/antigravity_prompt__phase_1307_g8_graph_native_sidecar_registry_manifest_profile_hardening.md` |
| 1308 | `docs/antigravity_tasks/antigravity_prompt__phase_1308_g8_public_rc_exclude_helper_pruning_replacement_plan.md` |
| 1309 | `docs/antigravity_tasks/antigravity_prompt__phase_1309_g8_transport_principal_admission_sidecar_lifecycle_hardening.md` |
| 1310 | `docs/antigravity_tasks/antigravity_prompt__phase_1310_g8_revocation_replay_admission_ban_tests.md` |
| 1311 | `docs/antigravity_tasks/antigravity_prompt__phase_1311_g8_local_graph_memory_projection_sidecar_public_safe_projection.md` |
| 1312 | `docs/antigravity_tasks/antigravity_prompt__phase_1312_g8_projection_privacy_field_filtering_tests.md` |
| 1313 | `docs/antigravity_tasks/antigravity_prompt__phase_1313_g8_public_fetch_p2p_activation_candidate_default_off.md` |
| 1314 | `docs/antigravity_tasks/antigravity_prompt__phase_1314_g8_wallet_withdrawal_transfer_spend_semantics_preflight.md` |
| 1315 | `docs/antigravity_tasks/antigravity_prompt__phase_1315_g8_ecu_minting_ilc_settlement_boundary_preflight.md` |
| 1316 | `docs/antigravity_tasks/antigravity_prompt__phase_1316_g8_window_1303_1316_closure_implementation_audit.md` |

## 9. Non-Claims

This grouping does not authorize public RC, public launch, public claimability,
public verifier/API serving, public P2P, public fetch serving, public
sidecar/projection serving, source export, source publication, package
publication, release artifact production, release keys, release envelopes,
Genesis mutation/signing, v0.2 signing, CDL mutation, CDL-088 opening, wallet
economics, ECU minting, ILC settlement, IP filing, paper publication, public
confidential messaging, or public confidential coordination serving.

It also does not authorize any public confidential messaging product claim.
