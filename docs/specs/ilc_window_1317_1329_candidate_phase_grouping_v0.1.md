# ILC Window 1317-1329 Candidate Phase Grouping v0.1

**Status:** Consumed by Phase 1317 sequence lock.
**Recorded:** 2026-05-12.
**Authority:** This document began as planning support only and is now consumed
by `docs/specs/ilc_phase_1317_1329_sequence_lock_v0.1.md`. The sequence lock
opens Window 1317-1329 through Phase 1317 only and assigns Phase 1318 as the
next non-sensitive capsule refresh. This guidance still does not execute source
export, publish a repository or package, produce release artifacts, generate
release keys or envelopes, mutate Genesis Atlas, sign v0.2, activate public
claimability, activate public P2P/fetch/sidecar serving, authorize public
confidential coordination serving, or authorize wallet/ECU/ILC economics. This
guidance itself does not open Phase 1318 or any later phase.

```text
window_1317_1329_candidate_phase_grouping_drafted_after_phase_1316
window_1317_1329_not_open_until_sequence_lock
phase_1317_window_1317_1329_sequence_lock_required
window_1317_1329_candidate_phase_grouping_consumed_by_phase_1317_sequence_lock
window_1317_1329_release_dry_run_public_rc_blocked
deterministic_source_allowlist_export_rehearsal_required_phase_1319
release_manifest_and_key_envelope_rehearsal_no_real_signing_phase_1320_1321
private_deployment_rehearsal_no_public_serving_phase_1322
openclaw_nemoclaw_claimable_profile_dry_run_public_claimability_gated_phase_1323
openclaw_skill_format_discovery_required_phase_1323
cli_first_skill_surface_recorded_phase_1323
python_import_bridge_surface_recorded_phase_1323
identity_seed_ux_public_bootstrap_blocker_phase_1323
identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323
openclaw_skill_not_published_or_installable_phase_1323
ccss_tail_routed_phase_1324_1328_without_atlas_g_compression
atlas_g_tail_carried_forward_not_hidden_inside_ccss_phase_1317_1329
window_1317_1329_prompt_drafts_registered
```

## 1. Confirmation

Window 1303-1316 closed with carry-forward through Phase 1316. The next
logical window is a release dry-run and confidential-coordination tail, not a
final RC/signing window. The purpose is to rehearse materialization, manifests,
signing procedure, private deployment, OpenClaw/NemoClaw claimable profile
operation, and the first Confidential Coordination Sidecar Suite slices while
preserving every public-RC non-claim.

The proposed Window 1317-1329 plan is consistent with current canon with these
guardrails:

- Phase 1317 is the sequence lock before any Phase 1318-1329 execution.
- Phase 1318 refreshes Capsule v5.54 and freezes the current blocker map before
  dry-run work.
- Phase 1319 is a dry-run materialization rehearsal only. It must fail on
  exported `PUBLIC_RC_EXCLUDE` markers, stripped-helper imports, or unreviewed
  legacy/private/patent-sensitive material.
- Phases 1320 and 1321 rehearse release manifest and signing procedure shapes
  without producing public artifacts, generating real release keys, producing
  release envelopes, or signing.
- Phases 1322 and 1323 rehearse private deployment and OpenClaw/NemoClaw
  claimable profile operation over private wiring only.
- Phase 1323 must distinguish the CLI-first OpenClaw skill surface from the
  deeper Python import bridge, discover the actual OpenClaw skill format before
  making any skill-surface claim, and record identity-seed UX as a public
  bootstrap blocker. The default identity rule is non-custodial: no
  seed/mnemonic/private-key material may be disclosed to an LLM, chat
  transcript, OpenClaw memory, walkthrough, or `STATUS.md`.
- Phases 1324-1328 are the CCSS tail only if the sequence lock keeps Atlas-G
  tail separate. Atlas-G-007 through ATLAS-G-010 remain required before signing
  but must not be hidden inside CCSS phases.
- Phase 1329 closes the window and classifies dry-run, CCSS, Atlas-G, and
  release blockers as closed, open, or carried forward.

## 2. Canon Basis

| Source | Relevance |
|--------|-----------|
| `docs/PLANNING_INDEX.md` | Current frontier after Phase 1317 sequence lock; Window 1317-1329 is open through Phase 1317 only. |
| `docs/specs/ilc_antigravity_context_capsule_v5.53.md` | Current capsule through Window 1303-1316 closure. |
| `docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md` | Carry-forward baseline for release dry-run, helper stripping, public RC blockers, and CCSS routing. |
| `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | Candidate Window 1317-1329 phase table and dry-run obligations. |
| `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md` | Materialized public-tree rule, `PUBLIC_RC_EXCLUDE` disposition, legacy untagged review, and fail-closed export checks. |
| `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md` | Source allowlist procedure that Phase 1319 rehearses without publication. |
| `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md` | Release artifact manifest schema that Phase 1320 rehearses without producing artifacts. |
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | Essential graph-native sidecar suite and harness-agnostic OpenClaw/NemoClaw path. |
| `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md` | CCSS-001 through CCSS-005 routing through Phases 1324-1328. |
| `docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md` | Atlas-G tail discipline; ATLAS-G-007 through ATLAS-G-010 remain future signing prerequisites. |
| `docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md` | Atlas-G tail candidate prompts and non-signing prerequisites. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Three-machine/seven-agent private deployment path and public-RC blocker map. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-087 is ratified; CDL-088 remains unopened. |

Exact-token search is not enough for this window. Every executable prompt must
repeat the four-part §0 discovery pass and direct-read relevant repo/MemPalace
hits before acting on a claim.

## 3. Human Escalation Discipline

If any phase discovers uncertain authority, contradictory canon, public exposure
risk, signing/release ambiguity, Atlas-G/CCSS priority conflict, private-droplet
credential or infrastructure risk, or a scope question that cannot be resolved
from committed documents, it must stop and prompt the human reviewer.

```text
human_question_escalation_required_for_uncertain_authority
```

Default to the narrower no-authorization route. This guidance does not activate
public serving, public claimability, public source export, release artifacts,
release signing, public confidential messaging, ECU minting, ILC settlement, or
wallet-facing value actions.

## 4. Candidate Phase Order

| Phase | Scope | Sensitivity | Primary blocker or lane |
|-------|-------|-------------|--------------------------|
| 1317 | Sequence lock for release dry run and CCSS tail | SENSITIVE | Opens no publication, signing, public-RC, public-serving, or value-path authority. |
| 1318 | Capsule v5.54 refresh | NON-SENSITIVE after Phase 1317 lock | Freezes current blocker map before dry runs. |
| 1319 | Deterministic source allowlist export rehearsal | SENSITIVE | Dry-run materialization; must fail on exported `PUBLIC_RC_EXCLUDE` markers/imports and unreviewed legacy/private material. |
| 1320 | Release artifact manifest instance rehearsal | SENSITIVE | Proves release manifest shape without public artifacts. |
| 1321 | Release key/envelope procedure rehearsal | SENSITIVE | Rehearses procedure without real key generation, envelope production, or signing. |
| 1322 | Three-machine/seven-agent private deployment rehearsal with essential graph-native sidecar suite | SENSITIVE | Private deployment evidence over private wiring; no public serving claim. |
| 1323 | OpenClaw/NemoClaw claimable profile full dry run against graph-native sidecar suite | SENSITIVE | Claimable profile rehearsal while public claimability remains gated. |
| 1324 | CCSS-001 private/gated shard sidecar contract | SENSITIVE | Encrypted coordination-node envelope, shard-header projection, and private-to-public promotion evidence shape. |
| 1325 | CCSS-002 capability, membership, grant, revocation, and optional ZK interface boundary | SENSITIVE | Private shard access-control boundary without plaintext or membership disclosure. |
| 1326 | CCSS-003 sealed sender local delivery sidecar boundary | SENSITIVE | H-013/H-015 fixed-size payload and relay-seam boundary without public P2P activation. |
| 1327 | CCSS-004 gossip announce/pull, jitter, batching, cover-policy, and traffic-analysis tests | SENSITIVE | Metadata-correlation hardening and no-anonymity-overclaim evidence. |
| 1328 | CCSS-005 private OpenClaw/NemoClaw confidential coordination droplet dry run plus reproducibility pass | SENSITIVE | Private harness evidence over loopback, Tailscale, or equivalent private wiring; no public serving claim. |
| 1329 | Window closure gate | SENSITIVE | Classifies dry-run, CCSS, Atlas-G, and release blockers closed/open/carried forward. |

## 5. Phase 1319 Materialization Rehearsal Rule

Phase 1319 is the first materialization rehearsal. Its dry-run export report
must prove:

- zero exported files contain `PUBLIC_RC_EXCLUDE`;
- zero exported files import or depend on stripped helper modules;
- `docs/antigravity_tasks/`, `docs/phases/`, raw chats, `out/`, local
  monitoring, private context material, and patent-sensitive material are
  excluded unless separately reviewed;
- the manifest records included files, excluded files, marker-scan results,
  import-scan results, legacy-untagged review results, file hashes, and
  non-claims with deterministic ordering.

This rehearsal is not public source export, public repository publication,
package publication, release artifact production, or a public-RC claim.

## 6. Release Dry-Run Boundaries

Phases 1320 and 1321 may rehearse manifest and signing procedure shapes only.
They must not generate real release keys, produce release envelopes, sign
anything, create release artifacts for public distribution, mutate Genesis
Atlas, sign v0.2, or imply that source export has passed.

Release artifact and signing rehearsals must reference clean-export evidence or
record the absence of that evidence as a blocker.

## 7. Private Deployment And OpenClaw/NemoClaw Boundaries

Sidecar suite dry runs in this window may use private DigitalOcean/OpenClaw,
NemoClaw, loopback, Tailscale, or equivalent private wiring where available.
Those tests must not claim:

- public P2P;
- public fetch serving;
- public sidecar/projection serving;
- public claim endpoints;
- public confidential messaging;
- public confidential coordination serving;
- source publication;
- public package publication;
- release authority.

OpenClaw and NemoClaw remain harness/deployment targets, not protocol
substrates.

Phase 1323 has an additional skill/bootstrap boundary:

- ILC-internal profile names such as `openclaw_skill_claimable` are package
  profile labels, not proof that a public OpenClaw skill is already listed,
  published, accepted by ClawHub, or installable.
- The public-facing integration target is CLI-first: an OpenClaw `SKILL.md` or
  equivalent should teach an agent to call `ilc` CLI/bootstrap commands.
- The deeper Python import bridge remains an advanced/private harness surface
  through `TransportHarness` and `StorageHarness` adapter wiring.
- Identity bootstrap must remain one cryptographic path with separate ceremony
  modes: interactive human ceremony and non-interactive agent-mode ceremony.
  Agent mode must require an explicit secure output or secure-store target and
  must fail closed rather than printing seed material to stdout or chat.
- The identity-seed UX path is a carry-forward blocker until a later ADR/CDL or
  equivalent identity-bootstrap spec defines path validation, permissions,
  recovery UX, and non-custodial defaults.

## 8. Confidential Coordination Tail Routing

| Sidecar | Candidate routing |
|---------|-------------------|
| Private/gated shard sidecar | Phase 1324 CCSS-001. |
| Capability/membership sidecar | Phase 1325 CCSS-002. |
| Sealed sender sidecar | Phase 1326 CCSS-003, local/private by default and no public P2P. |
| Gossip announce/pull and jitter/cover policy sidecar | Phase 1327 CCSS-004. |
| Confidential OpenClaw/NemoClaw bridge dry run | Phase 1328 CCSS-005. |
| Contributor sidecar SDK/conformance pack | Start after one private OpenClaw/NemoClaw dry run proves the generic sidecar manifest and bridge contract. |
| Wallet-facing/ECU/ILC value-action sidecar | Remains tied to Phase 1314/1315/1338 authority gates; wallets are provider adapters around ledger-truth value transitions; no economics by default. |
| Optional ILC wallet recipe profile | Compose provider-adapter, signing-intent, ledger-truth value-action, receipt/history, and recovery/export sidecars after Phase 1315 if explicitly selected; not a first-RC blocker by default. |

## 9. Atlas-G Tail Split

ATLAS-G-007 through ATLAS-G-010 remain required before signing. The current best
plan is not to compress Atlas-G tail implementation and CCSS implementation
into the same Phase 1324-1328 work. If Phase 1317 chooses Atlas-G tail as the
priority for Window 1317-1329, the CCSS rows must move to a later dedicated
sidecar window rather than being executed as hidden scope.

## 10. Prompt Draft Registry

| Phase | Prompt draft |
|-------|--------------|
| 1317 | `docs/antigravity_tasks/antigravity_prompt__phase_1317_g8_window_1317_1329_sequence_lock.md` |
| 1318 | `docs/antigravity_tasks/antigravity_prompt__phase_1318_g8_context_capsule_v5_54_frontier_refresh.md` |
| 1319 | `docs/antigravity_tasks/antigravity_prompt__phase_1319_g8_deterministic_source_allowlist_export_rehearsal.md` |
| 1320 | `docs/antigravity_tasks/antigravity_prompt__phase_1320_g8_release_artifact_manifest_instance_rehearsal.md` |
| 1321 | `docs/antigravity_tasks/antigravity_prompt__phase_1321_g8_release_key_envelope_procedure_rehearsal.md` |
| 1322 | `docs/antigravity_tasks/antigravity_prompt__phase_1322_g8_three_machine_seven_agent_private_deployment_rehearsal.md` |
| 1323 | `docs/antigravity_tasks/antigravity_prompt__phase_1323_g8_openclaw_nemoclaw_claimable_profile_full_dry_run.md` |
| 1324 | `docs/antigravity_tasks/antigravity_prompt__phase_1324_g8_ccss_001_private_gated_shard_sidecar_contract.md` |
| 1325 | `docs/antigravity_tasks/antigravity_prompt__phase_1325_g8_ccss_002_capability_membership_grant_revocation_boundary.md` |
| 1326 | `docs/antigravity_tasks/antigravity_prompt__phase_1326_g8_ccss_003_sealed_sender_local_delivery_boundary.md` |
| 1327 | `docs/antigravity_tasks/antigravity_prompt__phase_1327_g8_ccss_004_gossip_jitter_cover_policy_tests.md` |
| 1328 | `docs/antigravity_tasks/antigravity_prompt__phase_1328_g8_ccss_005_private_openclaw_nemoclaw_droplet_dry_run.md` |
| 1329 | `docs/antigravity_tasks/antigravity_prompt__phase_1329_g8_window_1317_1329_closure_gate.md` |

## 11. Non-Claims

This grouping does not authorize public RC, public launch, public claimability,
public verifier/API serving, public P2P, public fetch serving, public
sidecar/projection serving, public confidential messaging, public confidential
coordination serving, source export execution, source publication, package
publication, OpenClaw skill publication/listing/installability, release
artifact production, release keys, release envelopes, real signing, Genesis
mutation/signing, v0.2 signing, CDL mutation, CDL-088 opening, identity-seed
generation, mnemonic generation, secret-store writes, custodial agent-mode
activation, seed/mnemonic/private-key disclosure to an LLM or transcript, wallet
economics, ECU minting, ILC settlement, IP filing, paper publication, or
OpenClaw/NemoClaw as protocol substrates.
