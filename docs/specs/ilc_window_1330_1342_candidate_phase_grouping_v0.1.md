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

## 10. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1330_g8_window_1330_1342_sequence_lock.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1331_g8_context_capsule_v5_55_release_candidate_freeze.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1332_g8_final_deterministic_code_security_audit.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1333_g8_source_allowlist_export_execution_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1334_g8_release_artifact_production_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1335_g8_release_keys_envelopes_generation_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1336_g8_public_claimability_api_activation_or_carry_forward_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1337_g8_public_path_sidecar_activation_or_exclusion_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1338_g8_wallet_ecu_ilc_activation_or_carry_forward_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1339_g8_atlas_g_mutation_regeneration_finalization.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1340_g8_v0_2_signing_ceremony_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1341_g8_public_rc_publication_claim_gate.md -> planning/frontier
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1342_g8_window_1330_1342_closure_handoff.md -> planning/frontier
```
