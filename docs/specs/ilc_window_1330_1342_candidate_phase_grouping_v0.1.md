# ILC Window 1330-1342 Candidate Phase Grouping v0.1

**Status:** Consumed by Phase 1330 sequence lock. Active lock:
`docs/specs/ilc_phase_1330_1342_sequence_lock_v0.1.md`. This remains
candidate guidance and is not execution authority beyond the active lock.
**Recorded:** 2026-05-13.
**Authority:** This document drafts the next candidate window after Phase 1329
closure. It does not open Window 1330-1342, execute source export, publish a
repository or package, produce release artifacts, generate release keys or
envelopes, sign v0.2, mutate Genesis Atlas, activate public claimability,
activate public P2P/fetch/sidecar serving, authorize public confidential
coordination serving, activate wallet/ECU/ILC economics, or make a public RC
claim. Phase 1330 sequence lock is required before any phase in this window can
execute.

```text
window_1330_1342_candidate_phase_grouping_drafted_after_phase_1329
window_1330_1342_candidate_grouping_consumed_by_phase_1330_sequence_lock
window_1330_1342_not_open_until_sequence_lock
phase_1330_window_1330_1342_sequence_lock_required
final_rc_signing_gate_public_rc_still_blocked_by_default
source_allowlist_export_execution_gate_routed_phase_1333
release_artifact_production_gate_routed_phase_1334
release_key_envelope_generation_gate_routed_phase_1335
public_claimability_api_gate_or_carry_forward_phase_1336
public_path_sidecar_confidential_coordination_gate_or_exclusion_phase_1337
wallet_ecu_ilc_activation_gate_or_carry_forward_phase_1338
atlas_g_tail_routed_phase_1339_1340_before_signing
atlas_g_007_unsigned_v0_2_candidate_regeneration_routed_phase_1339
atlas_g_008_non_excisability_review_packet_routed_phase_1339
atlas_g_009_signing_root_envelope_prep_routed_phase_1340
atlas_g_010_v0_2_signing_ceremony_routed_phase_1340
public_rc_publication_claim_gate_routed_phase_1341
window_1330_1342_prompt_drafts_registered
```

## 1. Confirmation

Window 1317-1329 is closed by
`docs/specs/ilc_window_1317_1329_handoff_1329_v0.1.md`. The next logical window
is now locked by Phase 1330 through Phase 1330 only. This candidate grouping is
consumed planning input, not execution authority for Phase 1331 or later.

The proposed Window 1330-1342 plan is consistent with current canon under these
guardrails:

- Phase 1330 is the sequence lock and opens no public RC, publication, signing,
  release, public serving, identity-bootstrap, or economics authority by itself.
- Phase 1331 freezes Capsule v5.55 after the lock, so stale v5.54 frontier
  assumptions do not leak into final gates.
- Phase 1332 is the final deterministic code/security audit before any export or
  release gate.
- Phase 1333 is the source allowlist export execution gate or explicit block; it
  must fail closed on `PUBLIC_RC_EXCLUDE`, stripped-helper imports, unreviewed
  legacy/private/patent-sensitive material, missing license/counsel state, or
  incomplete manifest evidence.
- Phase 1334 is the release artifact production gate only if the source export
  gate passes; it must not hide private helper scaffolds or imply publication.
- Phase 1335 is the release key/envelope generation gate and requires explicit
  key-generation authority beyond ordinary queue position. The preferred
  authority phrase is `GO Phase 1335: authorize release key/envelope generation`.
- Phase 1336 either activates public claimability/API with explicit authority and
  all preconditions met, or records a no-claim carry-forward.
- Phase 1337 either activates or explicitly excludes TransportPrincipal,
  public-P2P, sidecar public-path, and public confidential coordination serving
  claims. Private CCSS droplet success is not public-serving authority.
- Phase 1338 either activates wallet/ECU/ILC value paths with explicit authority
  and all prerequisites met, or records a carry-forward. Wallets remain provider
  adapters around ledger-truth state, not independent truth sources.
- Phase 1339 handles Atlas-G mutation/regeneration finalization and must close
  or block ATLAS-G-007 unsigned v0.2+ candidate regeneration and ATLAS-G-008
  Genesis/ILC/ECU/hypergraph non-excisability review packet before signing can
  be considered.
- Phase 1340 handles ATLAS-G-009 signing root envelope prep and ATLAS-G-010
  v0.2 signing ceremony. It must require explicit signing authority for any
  signature production. The preferred authority phrase is
  `GO Phase 1340: authorize v0.2 signing ceremony`. It must not sign by default.
- Phase 1341 is the public RC publication/claim gate. It must fail closed unless
  all selected gates are closed and counsel/publication authority is explicit.
  The preferred authority phrase is
  `GO Phase 1341: authorize public RC publication/claim`.
- Phase 1342 closes the window and honestly carries forward anything still
  blocked.

## 2. Canon Basis

| Source | Relevance |
|--------|-----------|
| `docs/PLANNING_INDEX.md` | Current frontier after Phase 1329 closure; no next phase assigned. |
| `docs/phases/STATUS.md` | Phase ledger through Phase 1329. |
| `docs/specs/ilc_antigravity_context_capsule_v5.54.md` | Current capsule through Phase 1329; stale after Phase 1331 should publish v5.55. |
| `docs/specs/ilc_window_1317_1329_handoff_1329_v0.1.md` | Carry-forward baseline for release dry-run, CCSS, Atlas-G, identity, economics, publication, and public RC blockers. |
| `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | Candidate Window 1330-1342 phase table and final gate ordering. |
| `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md` | Clean materialized public source tree rule, `PUBLIC_RC_EXCLUDE` disposition, legacy untagged review, and fail-closed export checks. |
| `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md` | Source allowlist export procedure; export not authorized until a future gate passes. |
| `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md` | Release artifact manifest schema and public-RC packaging carry-forward. |
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | Graph-native sidecar suite, OpenClaw/NemoClaw host posture, and wallet/value-path sidecar routing. |
| `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md` | CCSS private/local evidence and public-serving gate routing. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Controlling public-RC roadmap and blocker map through Phase 1329. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-087 ratified; CDL-088 remains unopened. |
| `ilc_core/identity/genesis_record_schema.py` and CDL-069 ratification evidence | Identity-seed commitment mismatch before any public identity bootstrap. |

Exact-token search is not enough for this window. Every executable prompt must
repeat the four-part §0 discovery pass and direct-read relevant repo/MemPalace
hits before acting on a claim.

## 3. Human Escalation Discipline

If any phase discovers uncertain authority, contradictory canon, stale capsule
state, public exposure risk, signing/release ambiguity, Genesis/Atlas mutation
ambiguity, identity bootstrap ambiguity, wallet/economics ambiguity, counsel/IP
uncertainty, or a scope question that cannot be resolved from committed docs, it
must stop and prompt the human reviewer.

```text
human_question_escalation_required_for_uncertain_authority
```

Default to the narrower no-authorization route. This guidance does not activate
public serving, public claimability, public source export, release artifacts,
release keys, release envelopes, release signing, public confidential messaging,
ECU minting, ILC settlement, wallet-facing value actions, Genesis mutation, or
v0.2 signing.

## 4. Candidate Phase Order

| Phase | Scope | Sensitivity | Primary blocker or lane |
|-------|-------|-------------|--------------------------|
| 1330 | Sequence lock for final RC and signing gate | SENSITIVE | Opens no publication, signing, release, public-serving, identity-bootstrap, or value-path authority by itself. |
| 1331 | Capsule v5.55 release-candidate freeze | NON-SENSITIVE after Phase 1330 lock | Freezes final-RC blocker map before execution gates. |
| 1332 | Final deterministic code/security audit | SENSITIVE | Last code/security blocker audit before export/release gates. |
| 1333 | Source allowlist export execution gate or explicit block | SENSITIVE | Executes or blocks clean source export; must fail on `PUBLIC_RC_EXCLUDE`, stripped-helper imports, or incomplete review. |
| 1334 | Release artifact production gate or explicit block | SENSITIVE | Produces release artifacts only if source export gate passes and authority is explicit. |
| 1335 | Release keys/envelopes generation gate or explicit block | SENSITIVE | Generates release keys/envelopes only with explicit key-generation authority. |
| 1336 | Public claimability/API activation gate or explicit no-claim carry-forward | SENSITIVE | Final claimability/API authority decision. |
| 1337 | TransportPrincipal, public sidecar/P2P, and confidential coordination public-path gate or explicit exclusion | SENSITIVE | Public-path activation decision; private CCSS evidence is not public authority. |
| 1338 | Wallet/ECU/ILC activation gate or explicit carry-forward | SENSITIVE | Value-path activation decision with provider-adapter boundary. |
| 1339 | Genesis Atlas mutation/regeneration finalization | SENSITIVE | ATLAS-G-007 unsigned v0.2+ candidate regeneration and ATLAS-G-008 non-excisability review packet. |
| 1340 | v0.2 signing ceremony gate | SENSITIVE | ATLAS-G-009 signing root envelope prep and ATLAS-G-010 v0.2 signing ceremony; no signature without explicit authority. |
| 1341 | Public RC publication/claim gate | SENSITIVE | Public RC claim only if all selected blockers are closed. |
| 1342 | Window closure handoff | SENSITIVE | Honest closure and carry-forward. |

## 5. Gate Dependencies

The default dependency order is strict:

1. Phase 1330 sequence lock.
2. Phase 1331 capsule freeze.
3. Phase 1332 final audit.
4. Phase 1333 source export gate.
5. Phase 1334 release artifact gate.
6. Phase 1335 key/envelope gate.
7. Phase 1336/1337/1338 public activation or explicit carry-forward decisions.
8. Phase 1339 Atlas-G mutation/regeneration finalization.
9. Phase 1340 v0.2 signing ceremony gate.
10. Phase 1341 public RC publication/claim gate.
11. Phase 1342 closure handoff.

Any prompt may block and carry forward its lane instead of activating it. No
later prompt may infer authority from a prior rehearsal; it must verify the
specific gate evidence.

## 6. Atlas-G Tail Routing

The Atlas-G tail is included in this candidate window as routed task work, not
as an implied signing grant:

| Atlas-G item | Canonical source name | Window route | Boundary |
|--------------|-----------------------|--------------|----------|
| ATLAS-G-007 | Unsigned Genesis Atlas v0.2+ candidate regeneration | Phase 1339 | May regenerate unsigned candidate only with explicit Atlas-G authority; no signing. |
| ATLAS-G-008 | Genesis/ILC/ECU/hypergraph non-excisability review packet | Phase 1339 | Must classify non-excisability evidence; CCSS evidence cannot substitute. |
| ATLAS-G-009 | Signing root envelope prep, no signing | Phase 1340 | May prepare root envelope/checklist only under explicit ceremony authority; no signature production by prep alone. |
| ATLAS-G-010 | v0.2 signing ceremony if explicitly authorized | Phase 1340 | Requires explicit signing authority; no signing by default. |

Phase 1340 must fail closed if Phase 1339 did not close or explicitly carry
forward ATLAS-G-007 and ATLAS-G-008 with a safe no-signing disposition. Phase
1341 must not claim a signed Genesis/Atlas v0.2 unless Phase 1340 records a
valid signing outcome.

## 7. Identity Bootstrap Stop Guard

Public bootstrap must not claim OpenClaw/NemoClaw users, digital agents, local
ILC identities, or any newly initialized agent identity are Genesis-rooted until
an identity-bootstrap ADR/CDL or equivalent spec exists and has been rehearsed.

Before any identity artifact is created, a future phase must resolve the
CDL-069 commitment mismatch:

Supersession note: Phase 1331 Fix1 later repaired this runtime formula. This
candidate grouping remains useful as historical guidance for the no-identity
artifact and no-public-Genesis-rooted-identity-claim boundary.

```text
identity_seed_commitment = sha384("ilc-seed-commit-v1:" || identity_seed)
```

versus the current runtime bare-hash path:

```text
sha384(identity_seed)
```

No prompt in this package authorizes identity artifact creation, seed or
mnemonic generation, private-key generation, secret-store writes, or dummy Agent
Birth artifacts unless a later explicitly authorized identity-bootstrap phase
supersedes this stop guard.

## 8. Non-Claims

This guidance does not authorize:

- Window 1330-1342 execution;
- public RC claim or public launch claim;
- source export execution;
- source publication, public repository publication, or public package publication;
- clean public tree production;
- release artifact production;
- release-key generation;
- release envelope production;
- release signing material generation;
- signature production or v0.2 signing;
- Genesis Atlas mutation, regeneration, or signing;
- CDL mutation or CDL-088 opening;
- public claimability/API activation, verifier service, or claim endpoint;
- public P2P, public fetch serving, public sidecar/projection serving, public
  confidential coordination serving, public confidential messaging, non-loopback
  bind, public listener, or peer discovery;
- identity artifact creation, seed commitment creation, `identity_seed_commitment`
  creation, mnemonic generation, private-key generation, or secret-store write;
- wallet-facing withdrawal, transfer, or spend activation;
- wallet-provider signing or ledger-write authority;
- wallet write authority, withdrawal runtime, ECU minting, ILC settlement, or
  value-path activation;
- counsel/IP/CLA/trademark/publication clearance.

## 9. Prompt Draft Registry

The candidate prompt drafts for this window are:

```text
docs/antigravity_tasks/antigravity_prompt__phase_1330_g8_window_1330_1342_sequence_lock.md
docs/antigravity_tasks/antigravity_prompt__phase_1331_g8_context_capsule_v5_55_release_candidate_freeze.md
docs/antigravity_tasks/antigravity_prompt__phase_1332_g8_final_deterministic_code_security_audit.md
docs/antigravity_tasks/antigravity_prompt__phase_1333_g8_source_allowlist_export_execution_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1334_g8_release_artifact_production_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1335_g8_release_keys_envelopes_generation_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1336_g8_public_claimability_api_activation_or_carry_forward_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1337_g8_public_path_sidecar_activation_or_exclusion_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1338_g8_wallet_ecu_ilc_activation_or_carry_forward_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1339_g8_atlas_g_mutation_regeneration_finalization.md
docs/antigravity_tasks/antigravity_prompt__phase_1340_g8_v0_2_signing_ceremony_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1341_g8_public_rc_publication_claim_gate.md
docs/antigravity_tasks/antigravity_prompt__phase_1342_g8_window_1330_1342_closure_handoff.md
```

## 11. Deferred Issues Register (Phase 1331 Fix1/Fix2/Fix3 post-audit)

Recorded 2026-05-14 after the pre-1332 deep audit and Fix1/Fix2/Fix3 hardening
passes. Each item is assigned to its target phase or carry-forward lane.

Phase 1332 completed the audit/enumeration gate and records:

```text
final_deterministic_code_security_audit_phase_1332.v0.1
runtime_guardrail_scope_revalidated_phase_1332
canonical_json_security_sweep_recorded_phase_1332
release_blocker_audit_no_activation_phase_1332
phase_1333_source_allowlist_export_execution_gate_next
public_rc_remains_blocked_after_phase_1332
phase_1333_status=blocked_pending_fix4_before_phase_1333
code_health_test_sim_exclusion_resolved_phase_1332
```

The one-line sim-harness code-health exclusion was closed before Phase 1332.
Phase 1332 confirmed that `test_code_health.py` still fails on non-sim runtime
hotspots and that private-address endpoint denial plus CBOR pre-load size caps
remain open Fix4 blockers before Phase 1333.

Phase 1332 Fix4 subsequently closed the six pre-Phase 1333 Fix4 blockers:

```text
phase_1332_fix4_pre_phase_1333_hardening.v0.1
private_address_endpoint_denial_phase_1332_fix4
cbor_preload_size_cap_phase_1332_fix4
package_profile_integrity_split_phase_1332_fix4
atlas_g_006_gate_split_phase_1332_fix4
source_allowlist_export_rehearsal_split_phase_1332_fix4
transport_principal_admission_params_dataclass_phase_1332_fix4
phase_1333_source_allowlist_export_execution_gate_unblocked_after_fix4
public_rc_remains_blocked_after_phase_1332_fix4
```

Phase 1333 subsequently executed after explicit `GO Phase 1333` and records:

```text
source_allowlist_export_execution_gate_phase_1333.v0.1
public_rc_exclude_marker_scan_required_phase_1333
stripped_helper_import_scan_required_phase_1333
legacy_untagged_review_required_phase_1333
source_publication_not_authorized_phase_1333
phase_1334_release_artifact_production_gate_next
public_rc_remains_blocked_after_phase_1333
```

Phase 1333 produced a local clean materialized source export candidate at
`out/public_rc/source_allowlist_export_phase_1333/tree` with binary verdict
`source_allowlist_export_execution_gate_verdict=pass`, 329 files, zero
`PUBLIC_RC_EXCLUDE` marker hits, zero stripped-helper dependency hits, zero
legacy-review ambiguities, and zero dirty included files. The export excludes
`ilc_core/sim/` as simulation harness material. Phase 1333 did not publish
source, publish a public repository, publish a package, produce release
artifacts, generate release keys/envelopes/signing material, sign, activate
public serving, mutate Genesis/Atlas, mutate CDLs, activate wallet/economics
paths, or claim public RC. Phase 1334 is next and remains sensitive.

### Phase 1332 Enumeration and Fix4 Closure

| ID | Finding | File:line | Target |
|----|---------|-----------|--------|
| H11 | `reputation.py` float/in-place-mutation/no-version-token rewrite | `ilc_core/consensus/reputation.py` | Window 1343+ (requires governance/CDL pass before Decimal/token decisions) |
| H12 | hash-before-ref helper centralization across CCSS modules | CCSS-001/002 inline vs. CCSS-003 `_verify_ref` | Carry-forward acceptable; Phase 1332 records file:line only |
| H14 | CCSS-004 `_require_non_negative_int` bakes in `_MAX_SEQUENCE` upper bound for unrelated count fields | `confidential_coordination_gossip_policy.py:938` | Phase 1332 disposition; likely carry-forward-with-note |
| M3–M12 | CCSS cross-module style/consistency items (guard ordering, dict return vs. normalized dict, etc.) | Various CCSS modules | Phase 1332 disposition per item |
| M13 | `_require_text` parameter order reversed in CCSS-004 vs. 001/002/003 | `confidential_coordination_gossip_policy.py:875` | Standalone CCSS-004 fix with search-and-replace; route post-Phase 1332 only if tests confirm no regressions |
| LOW-1 | `str(exc)` returns message in CCSS-001/002 but token in CCSS-003/004 | All four CCSS error classes | Fix-in-place alongside any CCSS touch |
| LOW-3 | CCSS-003/004 missing AST-walk `assert`-ban test | `tests/test_phase_1326_*.py`, `tests/test_phase_1327_*.py` | Fix-in-place alongside any CCSS-003/004 test touch |
| LOW-4 | CCSS-004 error token omits received `record_kind` in detail string | `confidential_coordination_gossip_policy.py:545` | Low priority; fix-in-place alongside any CCSS-004 touch |
| LOW-5 | CCSS-001 test mutates `_MAX_CANONICAL_JSON_BYTES` via try/finally not `monkeypatch` | `tests/test_phase_1324_ccss_001_*.py:337` | Fix-in-place alongside any CCSS-001 test touch |
| LOW-2 | CCSS-004 test uses path-relative `Path("ilc_core/...")` not repo-root-anchored path | `tests/test_phase_1327_ccss_004_*.py:287` | Fix-in-place alongside any CCSS-004 test touch |
| — | Private-address endpoint denial (SSRF via internal network targets) | `ilc_core/network/` HTTP clients | CLOSED by Phase 1332 Fix4 |
| — | CBOR pre-load size cap missing before `cbor2.loads` | `ilc_core/crypto/cbor_canonical.py:35` | CLOSED by Phase 1332 Fix4 |

### Phase 1332 Fix4 Closures

Network hardening items confirmed by Phase 1332 enumeration. Fix3 closed H6/H7/H8/H9.
Fix4 closed the following before Phase 1333:

| ID | Finding | File:line | Note |
|----|---------|-----------|------|
| — | Private-address SSRF denial on outbound HTTP (TOCTOU on IP range) | `ilc_core/network/` HTTP clients | CLOSED by `validate_peer_endpoint()` and `PeerManager` default-private denial; test/private opt-in remains explicit |
| — | CBOR pre-load size cap | `ilc_core/crypto/cbor_canonical.py:35` | CLOSED by `MAX_CANONICAL_CBOR_INPUT_BYTES` guard before `cbor2.loads` |

### Code health — `test_code_health.py` failures (2026-05-14)

Thresholds: `MAX_FUNC_LINES=150`, `MAX_CLASS_LINES=300`, `MAX_NESTING_DEPTH=4`, `MAX_FUNC_ARGS=10`, `MAX_FILE_LINES=1500`.

#### Immediate fix (test exclusion only — not protocol code)

| Action | Target | Rationale |
|--------|--------|-----------|
| Add `ilc_core/sim/` to `EXCLUDE_DIRS` in `test_code_health.py` | `sim_fetch_01_harness.py` (1694 lines, `run_sim_fetch_01()` 917 lines / nesting 6) | Simulation harnesses are legitimately monolithic; not protocol code |

#### Refactor candidates (route before Phase 1333 or as a code-health fix phase)

| Lines/Depth/Args | Function or Class | File | Priority |
|-----------------|-------------------|------|---------|
| 415 lines → 32 lines | `_validate_package_profile_integrity()` | `sidecars/registry_manifest.py` | CLOSED by Phase 1332 Fix4 per-lane validator split |
| 218 lines → 55 lines | `build_atlas_g_006_public_rc_graph_reachability_gate()` | `rc/atlas_graph_discipline.py` | CLOSED by Phase 1332 Fix4 helper split |
| 209 lines | `validate_public_fetch_p2p_readiness_candidate()` | `sidecars/public_fetch_p2p_readiness.py:283` | MED |
| 199 lines → 103 lines | `build_source_allowlist_export_rehearsal()` | `rc/source_allowlist_export_rehearsal.py` | CLOSED by Phase 1332 Fix4 helper split |
| 198 lines | `_build_parser()` | `cli/main.py:910` | LOW — argparse builder; split into subcommand groups or add to EXCLUDE_PATHS |
| 185 lines / **28 args** → 135 lines / 2 args | `build_transport_principal_admission_decision()` | `sidecars/transport_principal_admission.py` | CLOSED by Phase 1332 Fix4 `TransportPrincipalAdmissionParams` dataclass and helper split |
| 183 lines | `_normalize_claimability_proof()` | `sidecars/claimability_receipt_verifier.py:770` | MED |
| 182 lines | `validate_transport_principal_public_path_preflight()` | `network/d2d/transport_principal_public_path_preflight.py:316` | MED |
| 168 lines | `_normalize_conversion_receipt()` | `sidecars/claimability_receipt_verifier.py:600` | MED |
| 164 lines | `validate_sidecar_public_path_preflight()` | `graph/sidecar_public_path_preflight.py:435` | MED |
| 162 lines | `route()` | `network/d2d/spectral_routing_runtime.py:90` | MED |
| nesting 7 | `build_gossip_cover_policy_decision()` | `sidecars/confidential_coordination_gossip_policy.py:532` | MED — CCSS-004; split decision chain into helpers |
| 19 args | `build_value_path_activation_boundary_preflight_packet()` | `sidecars/value_path_activation_boundary_preflight.py:176` | MED — introduce params struct |
| 17 args | `build_public_fetch_p2p_readiness_candidate()` | `sidecars/public_fetch_p2p_readiness.py:146` | MED |
| 17 args | `build_wallet_action_semantics_preflight_packet()` | `sidecars/wallet_action_semantics_preflight.py:157` | MED |
| 16 args | `build_transport_principal_public_path_preflight()` | `network/d2d/transport_principal_public_path_preflight.py:180` | MED |
| 311 lines | `class ConsensusEngine` | `consensus/engine.py:129` | LOW — 11 lines over limit; split one method out |

#### Suggested routing for code health

1. **Resolved before Phase 1332:** `ilc_core/sim/` is now in `EXCLUDE_DIRS` in `test_code_health.py`, so simulation-only harness bulk no longer dominates the code-health report.
2. **Resolved by Phase 1332 Fix4:** `build_transport_principal_admission_decision()` now uses `TransportPrincipalAdmissionParams`; `_validate_package_profile_integrity()` is split into per-lane validators; `build_atlas_g_006_*` and `build_source_allowlist_export_rehearsal()` are split below the release-gate function threshold.
3. **Carry-forward after Fix4:** Remaining code-health violations outside the six Fix4 items remain recorded for future lane-specific fixes.

```text
deferred_issues_register_recorded_window_1330_1342_2026_05_14
code_health_test_sim_exclusion_required_before_phase_1332
code_health_test_sim_exclusion_resolved_phase_1332
code_health_refactor_candidates_recorded_window_1330_1342
reputation_py_rewrite_deferred_window_1343_plus
fix4_private_address_denial_cbor_size_cap_required_before_phase_1333
phase_1332_fix4_pre_phase_1333_hardening.v0.1
phase_1333_source_allowlist_export_execution_gate_unblocked_after_fix4
```

## 9.1 Phase 1334 Execution Addendum

Phase 1334 executed after explicit `GO Phase 1334` and closed the release
artifact production gate as unsigned local artifact evidence only:

```text
release_artifact_production_gate_phase_1334.v0.1
release_artifact_manifest_validated_phase_1334
clean_source_export_dependency_verified_phase_1334
release_artifacts_unsigned_by_default_phase_1334
phase_1335_release_keys_envelopes_generation_gate_next
public_rc_remains_blocked_after_phase_1334
```

The gate verified the Phase 1333 clean source export dependency and produced
one deterministic source-release tarball:

| Artifact | Hash | Signing |
|----------|------|---------|
| `out/release_artifacts/phase_1334/ilc-source-release-phase-1334.tar.gz` | `sha256:60a2f404576e5abbc45bc29ab4ae106368a764aa3d37f2ca458d35363cc45a47` | `unsigned` |

Phase 1334 does not authorize public repository publication, public package
publication, public RC claim, release-key generation, release-envelope
production, signing, v0.2 signing, public claimability/API activation, public
P2P/fetch/sidecar serving, Genesis mutation/signing, identity artifacts, wallet
actions, ECU minting, ILC settlement, or public confidential coordination
serving.

Phase 1335 executed after explicit key/envelope-generation authority:

```text
GO Phase 1335: authorize release key/envelope generation
```

## 9.2 Phase 1335 Execution Addendum

Phase 1335 executed after explicit `GO Phase 1335: authorize release
key/envelope generation` and closed the release key/envelope generation gate as
safe metadata plus external operator-local secret custody:

```text
release_keys_envelopes_generation_gate_phase_1335.v0.1
release_key_generation_requires_explicit_authority_phase_1335
release_envelope_generation_requires_explicit_authority_phase_1335
secret_material_not_written_to_repo_phase_1335
phase_1336_public_claimability_api_gate_next
public_rc_remains_blocked_after_phase_1335
```

Gate result: `keys_envelopes_generated`. Phase 1335 validated the Phase 1334
unsigned source-release artifact and generated or reused an Ed25519 release key
through the operator-local external keyfile provider boundary. Checked-in
metadata records only public identifiers, public key bytes, public key
fingerprint, release-key registration metadata, and unsigned release-envelope
metadata.

| Record | Value |
|--------|-------|
| Release key id | `ilc-release-key-phase-1335-rc-candidate` |
| Public key fingerprint | `sha256:4f2ca127b54872cff4010cfce3d0fbef617ca92cc97d8ef09be13bdfe3dea056` |
| Registration hash | `sha256:3a6b45b3cc45929c09930688c556e682c3166404d85201a6daae1ed31d20c1df` |
| Envelope id | `ilc-release-envelope-phase-1335-unsigned-candidate` |
| Envelope hash | `sha256:4b26d11a5ee9008d41ad8449907b359f241f8d8a7863940694aef639222ed135` |
| Signing status | `unsigned` |

No private key bytes, private key path, private key fingerprint, seed,
mnemonic, KMS secret, HSM credential, or operator credential value is recorded
in git. Phase 1335 does not authorize release signing, signature production,
v0.2 signing, public repository publication, public package publication, public
RC publication/claim, public serving, Genesis/Atlas mutation/signing, identity
artifacts, wallet actions, ECU minting, ILC settlement, CDL mutation, or
CDL-088 opening.

Phase 1336 is now the next sensitive gate and requires explicit future
`GO Phase 1336`.

## 9.3 Phase 1336 Execution Addendum

Phase 1336 executed after explicit `GO Phase 1336` and closed the public
claimability/API activation-or-carry-forward gate as an explicit no-claim
carry-forward:

```text
public_claimability_api_activation_or_carry_forward_gate_phase_1336.v0.1
public_claimability_requires_explicit_authority_phase_1336
claimability_replay_nullifier_policy_checked_phase_1336
wallet_value_actions_still_separate_gate_phase_1336
phase_1337_public_path_sidecar_activation_or_exclusion_gate_next
public_rc_remains_blocked_after_phase_1336
```

Gate result: `no_claim_carry_forward`; binary verdict:
`public_claimability_api_activation_or_carry_forward_gate_verdict=no_claim_carry_forward`;
status token: `phase_1336_status=complete_no_claim_carry_forward`. The gate
confirmed the local claimability verifier remains local-only, replay/nullifier
and duplicate-claim policy remain gated, CDL-088 is not opened, identity
bootstrap and Genesis-rooted agent birth attestation remain unspecified,
legacy `/v1/public/*` FastAPI routes remain a cleanup blocker, and public
verifier API counsel clearance is not recorded.

Phase 1336 did not activate a public claimability API, public verifier service,
public claim endpoint, public route, non-loopback bind, wallet value path, ECU
mint, ILC settlement, source publication, package publication, release signing,
public RC claim, identity bootstrap, CDL mutation, CDL-088 opening, Genesis/
Atlas mutation/signing, or v0.2 signing.

Phase 1337 is now the next sensitive gate and requires explicit future
`GO Phase 1337`.

## 9.4 Phase 1337 Execution Addendum

Phase 1337 executed after explicit `GO Phase 1337` and closed the public path,
sidecar, P2P, and confidential coordination serving activation-or-exclusion gate
as explicit first-RC exclusion:

```text
public_path_sidecar_activation_or_exclusion_gate_phase_1337.v0.1
transport_principal_public_path_requires_explicit_authority_phase_1337
public_sidecar_projection_serving_requires_explicit_authority_phase_1337
public_confidential_coordination_serving_requires_explicit_authority_phase_1337
phase_1338_wallet_ecu_ilc_activation_gate_next
public_rc_remains_blocked_after_phase_1337
```

Gate result: `excluded_from_first_rc`; binary verdict:
`public_path_sidecar_activation_or_exclusion_gate_verdict=excluded_from_first_rc`;
status token: `phase_1337_status=complete_excluded_from_first_rc`. The gate
confirmed TransportPrincipal public path remains local-only, public P2P/fetch
remains default-off, non-loopback bind/public listener/peer discovery remain not
enabled, sidecar projection serving remains local-only, sidecar registry public-
serving flags remain false, and CCSS private droplet evidence remains private/
local evidence only.

Phase 1337 did not activate TransportPrincipal public path, public P2P, public
fetch serving, public listener, peer discovery, non-loopback bind, public
sidecar/projection serving, public confidential coordination serving, public
claimability/API, wallet value paths, source publication, package publication,
release signing, public RC claim, identity bootstrap, CDL mutation, CDL-088
opening, Genesis/Atlas mutation/signing, or v0.2 signing.

Phase 1338 is now the next sensitive gate and requires explicit future
`GO Phase 1338`.

## 9.5 Phase 1338 Execution Addendum

Phase 1338 executed after explicit `GO Phase 1338` and closed the wallet/ECU/
ILC activation-or-carry-forward gate as no-activation carry-forward:

```text
wallet_ecu_ilc_activation_or_carry_forward_gate_phase_1338.v0.1
wallet_provider_adapter_boundary_preserved_phase_1338
ecu_minting_requires_explicit_authority_phase_1338
ilc_settlement_requires_explicit_authority_phase_1338
phase_1339_atlas_g_mutation_regeneration_finalization_next
public_rc_remains_blocked_after_phase_1338
```

Gate result: `carry_forward_no_activation`; binary verdict:
`wallet_ecu_ilc_activation_or_carry_forward_gate_verdict=carry_forward_no_activation`;
status token: `phase_1338_status=complete_carry_forward_no_activation`. The gate
confirmed wallet-facing withdrawal/transfer/spend semantics remain preflight-
only, wallets remain provider adapters around ledger-truth objects, ECU minting
and ILC settlement remain preflight-only and blocked, public wallet runtime
exposes read/status/export/summary-style methods only, claimability verifier
activation flags remain false, and the exact-numeric boundary rejects float and
non-finite Decimal inputs.

Phase 1338 did not activate wallet-facing requests, wallet-provider signing,
wallet-provider ledger-write, wallet writes, withdrawal runtime, ECU minting,
ECU creation, ILC settlement, ILC transfer, settlement-root publication, public
claim endpoint, value-path activation, source publication, package publication,
release signing, public RC claim, identity bootstrap, CDL mutation, CDL-088
opening, Genesis/Atlas mutation/signing, or v0.2 signing.

Phase 1339 is now the next sensitive gate and requires explicit future
`GO Phase 1339`.

## 10. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1330_g8_window_1330_1342_sequence_lock.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1331_g8_context_capsule_v5_55_release_candidate_freeze.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1332_g8_final_deterministic_code_security_audit.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1333_g8_source_allowlist_export_execution_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1334_g8_release_artifact_production_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1335_g8_release_keys_envelopes_generation_gate.md -> planning/frontier
graph_delta=load_bearing_artifact_added:docs/specs/ilc_release_keys_envelopes_generation_gate_1335_v0.1.json -> release-key-envelope-metadata
graph_delta=load_bearing_code_added:ilc_core/rc/release_keys_envelopes_generation_gate.py -> rc/release-key-envelope-generation-gate
graph_delta=support_tests_added:tests/test_phase_1335_release_keys_envelopes_generation_gate.py -> validation
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1336_g8_public_claimability_api_activation_or_carry_forward_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1337_g8_public_path_sidecar_activation_or_exclusion_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1338_g8_wallet_ecu_ilc_activation_or_carry_forward_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1339_g8_atlas_g_mutation_regeneration_finalization.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1340_g8_v0_2_signing_ceremony_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1341_g8_public_rc_publication_claim_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1342_g8_window_1330_1342_closure_handoff.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.json,docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1336_public_claimability_api_activation_or_carry_forward_gate.py -> validation
graph_delta=support_only:docs/phases/phase_1336_public_claimability_api_activation_or_carry_forward_gate_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_public_path_sidecar_activation_or_exclusion_gate_1337_v0.1.json,docs/specs/ilc_public_path_sidecar_activation_or_exclusion_gate_1337_v0.1.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1337_public_path_sidecar_activation_or_exclusion_gate.py -> validation
graph_delta=support_only:docs/phases/phase_1337_public_path_sidecar_activation_or_exclusion_gate_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_wallet_ecu_ilc_activation_or_carry_forward_gate_1338_v0.1.json,docs/specs/ilc_wallet_ecu_ilc_activation_or_carry_forward_gate_1338_v0.1.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1338_wallet_ecu_ilc_activation_or_carry_forward_gate.py -> validation
graph_delta=support_only:docs/phases/phase_1338_wallet_ecu_ilc_activation_or_carry_forward_gate_walkthrough.md -> planning/frontier
```
