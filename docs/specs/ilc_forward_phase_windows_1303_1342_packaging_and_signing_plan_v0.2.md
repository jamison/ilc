# ILC Forward Phase Windows 1303-1342 Packaging and Signing Plan v0.2

**Status:** Planning-only candidate guidance.
**Recorded:** 2026-05-10.
**Revised:** 2026-05-14 — comprehensive §5 rewrite (3-window post-1342 structure: issuance economics / public claimability governance / long-range); removed superseded single-Window-1343 section.
**Authority:** This document records forward planning only. It does not open
Window 1303+, assign an active sequence lock, execute source export, publish a repository or package, produce release artifacts, generate release keys or envelopes, mutate Genesis Atlas, sign v0.2, activate public claimability, activate public P2P/fetch/sidecar serving, or authorize wallet/ECU/ILC economics.

```text
forward_phase_windows_1303_1342_packaging_and_signing_plan_recorded
public_rc_exclude_helper_stripping_routed_to_phase_1308_1319_1333
source_allowlist_export_materialization_must_fail_on_public_rc_exclude_markers
public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution
legacy_untagged_docs_default_review_required_before_public_export
graph_native_sidecar_creation_routed_to_forward_windows_1303_1342
essential_openclaw_rc_sidecars_truth_projection_claimability_bridge
openclaw_nemoclaw_are_hosts_not_protocol_substrates
sidecar_suite_public_serving_remains_blocked_until_explicit_authority
confidential_coordination_sidecar_suite_forward_plan_recorded
confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329
	confidential_coordination_openclaw_droplet_dry_run_phase_1328_private_only
	confidential_coordination_not_public_rc_blocker_without_explicit_selection
window_1317_1329_closed_phase_1329
window_1317_1329_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1329_window_1317_1329_closure_complete
window_1330_plus_sequence_lock_required_before_next_phase_assignment
release_dry_run_ccss_atlas_g_blockers_classified_phase_1329
public_rc_remains_blocked_after_phase_1329
window_1330_1342_closed_phase_1342
window_1330_1342_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1342_window_1330_1342_closure_complete
window_1343_plus_sequence_lock_required_before_next_phase_assignment
final_rc_publication_and_signing_blockers_classified_phase_1342
public_rc_final_status_recorded_phase_1342
```

## 1. Purpose

This plan preserves the best current post-1302 phase sequence and attaches the
`PUBLIC_RC_EXCLUDE` helper stripping obligation to the correct future packaging
phases. It intentionally treats earlier recovered phase tables as planning
input, not as a binding format. The controlling architecture rule is recorded
in `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md`.
The graph-native sidecar-suite correction is recorded in
`docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md`.

The practical rule is simple: do not flip fail-closed helper flags from `False` to `True`. Those helpers are internal scaffolds. Public RC packaging must either
replace them with public-safe modules after their authority gates close or strip
them from the materialized public export. A public-source/package artifact must
fail closed if any `PUBLIC_RC_EXCLUDE` marker or import dependency on an
excluded helper remains.

The best current plan is:

1. implement and harden the public-safe surfaces first;
2. dry-run a deterministic materialized public tree and prove it is clean;
3. only then consider an explicitly authorized export/release/signing gate.

Source export must precede release artifact production. Release artifacts must
not become the mechanism that hides private helper scaffolds or converts a
false authorization flag into a public claim.

`PUBLIC_RC_EXCLUDE` is a deny marker, not an allowlist marker. Absence of the tag
does not make old docs, research notes, phase walkthroughs, whitepaper drafts,
or roadmap fragments exportable. Legacy untagged files must be excluded or
reviewed explicitly in the source export manifest.

The OpenClaw/NemoClaw path should also be corrected from "ordinary API wrapper"
to "graph-native sidecar suite." The essential first suite is a local registry
and manifest, truth primitive submission sidecar, local graph/memory projection
sidecar, offline claimability/receipt verifier sidecar, and OpenClaw/NemoClaw
bridge sidecar. OpenClaw/NemoClaw droplets are hosts for private deployment
testing of that suite, not protocol substrates.

The Confidential Coordination Sidecar Suite is routed as the next private/local
sidecar build-out after the essential OpenClaw-compatible suite is testable. It
is not a first-RC blocker by default. Its detailed routing is recorded in
`docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md`.

## 2. Window 1303-1316 - Implementation Hardening

| Phase | Scope | Blocker addressed | Task lane |
|-------|-------|-------------------|-----------|
| 1303 | Sequence lock for implementation hardening | Opens no public RC authority by itself | Planning/frontier |
| 1304 | Capsule v5.53 refresh | Prevents stale frontier before implementation work | Planning/frontier |
| 1305 | Offline/local claimability and receipt verifier sidecar/library, no API serving | Final public claimability verifier authority substrate | Gap 13 / graph-native sidecars |
| 1306 | Proof-binding, canonical hash, and negative-path tests | Forged receipts, replay, exact numeric and canonical JSON proof safety | Gap 13 |
| 1307 | Graph-native sidecar registry/manifest plus claimability package profile hardening | Essential sidecar manifest, OpenClaw-compatible local bridge profile, `confidential_coordination_local_preview` profile declaration, package-profile integrity, and source allowlist readiness | Gap 14 / graph-native sidecars / CCSS |
| 1308 | Helper pruning/replacement plan with `PUBLIC_RC_EXCLUDE` enforcement and truth-primitive sidecar boundary | Converts Phase 1293 keep-internal register into concrete replacement-or-strip decisions; records local truth-primitive sidecar boundary; no export yet | Gap 14 / packaging security / graph-native sidecars |
| 1309 | TransportPrincipal admission sidecar lifecycle implementation hardening | Public-path identity lifecycle blocker | Gap 10 / graph-native sidecars |
| 1310 | Revocation, replay, admission, and ban tests | Hostile-network public-path blocker | Gap 10 / Gap 11 |
| 1311 | Local graph/memory projection sidecar and public-safe projection implementation | Public-safe projection, private/gated shard header projection, encrypted coordination-node reference, and privacy-filter blocker | Gap 9 / graph-native sidecars / CCSS |
| 1312 | Projection privacy and field-filtering tests | Field disclosure, identifier leakage, bounded serving blocker, and confidential-coordination projection non-leakage | Gap 9 / CCSS |
| 1313 | Public fetch/P2P readiness candidate, default off with no activation | Public fetch/P2P readiness without activation in this implementation-hardening window | Gap 10 / CDL-087 |
| 1314 | Wallet-facing withdrawal, transfer, and spend request semantics preflight | Public claimability user action blocker; wallets remain adapters around ledger-truth objects | Gap 13 |
| 1315 | ECU minting and ILC settlement boundary preflight | ECU/ILC value-path activation blocker | Gap 12 / Gap 13 |
| 1316 | Window closure and implementation audit | Classifies implementation blockers closed/open/carried forward | Planning/frontier |

Phase 1308 is the first explicit stripping-planning point. It should produce an
inventory that maps each current `PUBLIC_RC_EXCLUDE` helper to one of:

| Disposition | Meaning |
|-------------|---------|
| `replace_before_export` | Implement a public-safe module and remove imports from the internal helper before any export materialization. |
| `strip_from_export` | Exclude the helper from public source/package/release artifacts and prove no exported code imports it. |
| `defer_public_rc` | Carry the blocker forward and do not claim public RC for the affected package profile. |

*Note on Scope and Prerequisites:* Phases 1309 and 1311 are candidate umbrella scopes that the future sequence lock may split into multiple integer phases to prevent scope blowout. Additionally, an explicit **Rust public-P2P substrate ADR/integration gate** is a strict prerequisite and must be formally inserted into the sequence *before* any Phase 1313-style public fetch/P2P activation candidate can be executed.

Essential graph-native sidecar ordering inside this window:

| Order | Sidecar | Candidate phase target |
|-------|---------|------------------------|
| 1 | Sidecar registry and deterministic manifest | 1307 |
| 2 | Offline claimability and receipt verifier sidecar | 1305/1306 |
| 3 | Truth primitive submission sidecar boundary | 1308 |
| 4 | TransportPrincipal admission sidecar substrate | 1309/1310 |
| 5 | Local graph/memory projection sidecar | 1311/1312 |
| 6 | Confidential coordination local preview profile | 1307 prerequisites, 1311/1312 projection prerequisites, 1324-1329 implementation/dry-run lane |

## 3. Window 1317-1329 - Release Dry Run and Confidential Coordination Tail

| Phase | Scope | Blocker addressed | Task lane |
|-------|-------|-------------------|-----------|
| 1317 | Sequence lock for release dry run and Atlas-G tail | Opens no publication/signing authority by itself | Planning/frontier |
| 1318 | Capsule v5.54 refresh | Freezes current blocker map before dry runs | Planning/frontier |
| 1319 | Deterministic source allowlist export rehearsal | Dry-run materialization must strip `PUBLIC_RC_EXCLUDE` helpers and fail on markers/imports in the exported tree | Phase 1255 / Gap 14 |
| 1320 | Release artifact manifest instance rehearsal | Proves release manifest shape without producing public artifacts | Phase 1213 / release |
| 1321 | Release key/envelope procedure rehearsal, no real signing by default | Rehearses signing procedure without key generation or envelope production | Release/signing |
| 1322 | Three-machine/seven-agent private deployment rehearsal with essential graph-native sidecar suite | Private deployment evidence; no public serving claim | RC operations / graph-native sidecars |
| 1323 | OpenClaw/NemoClaw claimable profile full dry run against graph-native sidecar suite | Final target profile rehearsal with public claimability still gated; skill-format discovery and identity-seed UX blockers recorded | Gap 13 / Gap 14 / graph-native sidecars / identity bootstrap |
| 1324 | CCSS-001 private/gated shard sidecar contract | Encrypted coordination-node envelope, shard-header projection, and private-to-public promotion evidence shape | Confidential Coordination Sidecar Suite |
| 1325 | CCSS-002 capability, membership, grant, revocation, and optional ZK interface boundary | Private shard access-control blocker without plaintext or membership disclosure | Confidential Coordination Sidecar Suite |
| 1326 | CCSS-003 sealed sender local delivery sidecar boundary | H-013/H-015 fixed-size payload and relay-seam integration without public P2P activation | Confidential Coordination Sidecar Suite / H-013/H-015 |
| 1327 | CCSS-004 gossip announce/pull, jitter, batching, cover-policy, and traffic-analysis tests | Metadata-correlation hardening and no-anonymity-overclaim evidence | Confidential Coordination Sidecar Suite / privacy |
| 1328 | CCSS-005 private OpenClaw/NemoClaw confidential coordination droplet dry run plus reproducibility pass | Private harness evidence over loopback, Tailscale, or equivalent private wiring; no public serving claim | Confidential Coordination Sidecar Suite / RC operations |
| 1329 | Window closure gate | Classifies dry-run, CCSS, Atlas-G, and release blockers closed/open/carried forward | Planning/frontier |

Resolved by the Phase 1317 sequence lock:

```text
ccss_tail_routed_without_atlas_g_compression_phase_1317
atlas_g_tail_carried_forward_not_hidden_inside_ccss_phase_1317_1329
```

Phases 1324-1328 are the current CCSS-001 through CCSS-005 private/local lane.
They are not Atlas-G tail phases and must not execute ATLAS-G-007 through
ATLAS-G-010 as hidden scope. Atlas-G tail work remains required before signing,
but it is carried forward outside Phases 1324-1328 unless a later explicit
sequence lock reopens the route and moves the CCSS rows to a later dedicated
sidecar window.

| Atlas-G tail item | Current routing control |
|-------------------|-------------------------|
| ATLAS-G-007 unsigned v0.2 candidate regeneration | Carried forward outside Phases 1324-1328; candidate tie-in remains Phase 1339 or a dedicated Atlas-G tail window. |
| ATLAS-G-008 non-excisability review packet | Carried forward outside Phases 1324-1328; must not be hidden inside CCSS implementation. |
| ATLAS-G-009 signing root envelope prep | Carried forward outside Phases 1324-1328; no real envelope or signing material before explicit authority. |
| ATLAS-G-010 v0.2 signing ceremony gate | Phase 1340 explicit signing gate; no signing by default. |

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

Sidecar suite dry runs in this window should test the essential suite on
private DigitalOcean/OpenClaw or equivalent droplets where available. Those
tests must use loopback/private wiring such as Tailscale and must not claim
public P2P, public sidecar serving, public claim endpoints, source publication,
or release authority.

Phase 1323 must harden the OpenClaw/NemoClaw skill boundary before any future
public bootstrap claim:

```text
openclaw_skill_format_discovery_required_phase_1323
cli_first_skill_surface_recorded_phase_1323
python_import_bridge_surface_recorded_phase_1323
identity_seed_ux_public_bootstrap_blocker_phase_1323
identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323
openclaw_skill_not_published_or_installable_phase_1323
genesis_rooted_agent_birth_attestation_blocker_phase_1323
```

The dry run must treat ILC-internal package-profile labels as package metadata,
not as proof that an OpenClaw skill is already published, listed, accepted by
ClawHub, or installable. The preferred public-facing surface is CLI-first: a
thin `SKILL.md` or equivalent instructs the harness agent to call `ilc`
CLI/bootstrap commands. The deeper Python import bridge remains a private or
advanced harness surface through `TransportHarness` and `StorageHarness`
adapters. Identity bootstrap remains a carry-forward blocker until a later
ADR/CDL or equivalent spec defines a non-custodial default: one cryptographic
path, interactive and agent-mode ceremony modes, explicit secure output or
secure-store target for agent mode, no stdout fallback for secret material, and
no seed/mnemonic/private-key disclosure to LLM chat, OpenClaw transcript memory,
logs, walkthroughs, or `STATUS.md`. Public bootstrap must also preserve the
Genesis-rooted identity invariant: before any OpenClaw/NemoClaw user or agent is
claimed to be Genesis-rooted, a later ADR/CDL or equivalent identity-bootstrap
spec must define an agent birth attestation or equivalent Genesis-rooted
identity-origin proof. That proof should bind `agent_id` to a signed
Genesis/Atlas lineage anchor and optional private/local node commitments without
using private graph content as identity-seed entropy or recovery material.

Confidential Coordination Sidecar Suite build-out after the essential
OpenClaw-compatible suite is testable should route:

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

Phase 1324 completion note:

```text
ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1
encrypted_coordination_node_envelope_contract_recorded_phase_1324
shard_header_projection_contract_recorded_phase_1324
private_to_public_promotion_evidence_shape_recorded_phase_1324
ccss_public_serving_not_enabled_phase_1324
phase_1325_ccss_capability_membership_boundary_next
public_rc_remains_blocked_after_phase_1324
```

Phase 1324 added the local-only
`confidential_coordination_private_gated_shard` sidecar contract and preserved
the CCSS/Atlas-G split. It did not authorize ATLAS-G-007 through ATLAS-G-010,
public confidential coordination serving, public P2P, public promotion, source
publication, release authority, release signing, identity bootstrap, wallet
actions, ECU minting, ILC settlement, or value-path activation.

Phase 1324 Fix1 implementation-audit hardening:

```text
phase_1324_fix1_ccss_001_shard_contract_hardening.v0.1
ccss_001_epoch_zero_rejected_phase_1324_fix1
ccss_001_canonical_json_byte_cap_enforced_phase_1324_fix1
ccss_001_ref_list_count_prechecked_phase_1324_fix1
ccss_001_phase_1325_membership_ref_false_positive_removed_phase_1324_fix1
```

Fix1 rejects pre-Genesis epoch 0, caps canonical JSON bytes, counts mapping keys
in the untrusted-payload budget, pre-checks reference-list length before
per-item validation, manifests the canonical-size and promotion-ref bounds,
rejects zero-envelope shard headers, and preserves Phase 1325 membership-boundary
ref compatibility without authorizing Phase 1325 execution or public serving.

Phase 1325 completion note:

```text
ccss_002_capability_membership_grant_revocation_boundary_phase_1325.v0.1
private_shard_access_control_boundary_recorded_phase_1325
membership_plaintext_disclosure_forbidden_phase_1325
optional_zk_interface_boundary_recorded_phase_1325
phase_1326_ccss_sealed_sender_boundary_next
public_rc_remains_blocked_after_phase_1325
```

Phase 1325 added the local-only
`confidential_coordination_capability_membership_boundary` sidecar contract and
preserved the CCSS/Atlas-G split. It records capability policy, opaque
membership boundary, grant, revocation, optional ZK seam, and fail-closed access
decision surfaces. It does not authorize ATLAS-G-007 through ATLAS-G-010,
public confidential coordination serving, public membership directory, public
credential authority, public ZK verifier, public P2P, public promotion, source
publication, release authority, release signing, identity bootstrap, wallet
actions, ECU minting, ILC settlement, or value-path activation.

Phase 1325 Fix1 completion note:

```text
phase_1325_fix1_ccss_002_access_audit_hardening.v0.1
ccss_002_zk_record_kind_validated_phase_1325_fix1
ccss_002_revocation_precedes_zk_deferred_phase_1325_fix1
ccss_002_pre_serialization_payload_byte_budget_phase_1325_fix1
sidecar_del_control_character_rejected_cross_module_phase_1325_fix1
public_rc_remains_blocked_after_phase_1325_fix1
phase_1326_ccss_sealed_sender_boundary_next_after_fix1
```

Phase 1325 Fix1 makes matching revocation evidence precede optional ZK
deferral, validates that `zk_interface_record` is a matching
`zk_membership_interface_ref`, enforces a CCSS-002 pre-serialization payload
byte budget, and rejects ASCII DEL across audited sidecar text validators. It
does not authorize Phase 1326 execution or any public
serving, public P2P, publication, release, signing, identity, wallet, ECU, ILC
settlement, or value-path activation.

Phase 1325 Fix2 completion note:

```text
phase_1325_fix2_ccss_002_branch_and_integer_hardening.v0.1
ccss_002_oversized_raw_int_rejected_before_stringification_phase_1325_fix2
ccss_002_access_branch_coverage_expanded_phase_1325_fix2
ccss_002_payload_depth_node_limits_covered_phase_1325_fix2
public_rc_remains_blocked_after_phase_1325_fix2
phase_1326_ccss_sealed_sender_boundary_next_after_fix2
```

Phase 1325 Fix2 rejects oversized raw integer leaves before decimal
stringification in CCSS-002 canonical JSON traversal and expands focused
coverage for supersession, mismatch, invalid-window, zero-sequence, depth-limit,
and node-limit paths. It does not authorize Phase 1326 execution or any public
serving, public P2P, publication, release, signing, identity, wallet, ECU, ILC
settlement, or value-path activation.

Phase 1326 completion note:

```text
ccss_003_sealed_sender_local_delivery_boundary_phase_1326.v0.1
sealed_sender_fixed_size_payload_boundary_recorded_phase_1326
h013_h015_dependency_seams_recorded_phase_1326
public_p2p_not_activated_by_ccss_phase_1326
phase_1327_ccss_gossip_jitter_cover_policy_next
public_rc_remains_blocked_after_phase_1326
```

Phase 1326 added the local-only
`confidential_coordination_sealed_sender_local_delivery` sidecar contract and
preserved the CCSS/Atlas-G split. It records fixed-size H-013 sealed payload
classes, local delivery intents, local delivery receipts, and private delivery
projection states without public P2P, public relay serving, public confidential
coordination serving, or public messaging authority. H-013/H-015 are dependency
seams only. It does not authorize ATLAS-G-007 through ATLAS-G-010, source
publication, release authority, release signing, identity bootstrap, wallet
actions, ECU minting, ILC settlement, or value-path activation.

Phase 1327 completion note:

```text
ccss_004_gossip_jitter_cover_policy_tests_phase_1327.v0.1
gossip_announce_pull_jitter_policy_recorded_phase_1327
traffic_analysis_negative_tests_recorded_phase_1327
anonymity_guarantee_not_claimed_phase_1327
phase_1328_ccss_private_droplet_reproducibility_next
public_rc_remains_blocked_after_phase_1327
```

Phase 1327 added the local-only
`confidential_coordination_gossip_jitter_cover_policy` sidecar contract and
preserved the CCSS/Atlas-G split. It records bounded private/local announce
metadata, receiver-controlled pull, bounded jitter, bounded batching, idle
cover, deterministic test-fixture jitter, traffic-analysis rows, residual
metadata-correlation risk, and explicit no-anonymity/non-unlinkability/
non-Signal-equivalent claims. It does not authorize public P2P, public relay
serving, public confidential coordination serving, public messaging, ATLAS-G-007
through ATLAS-G-010, source publication, release authority, release signing,
identity bootstrap, wallet actions, ECU minting, ILC settlement, or value-path
activation.

Phase 1328 completion note:

```text
ccss_005_private_openclaw_nemoclaw_droplet_dry_run_phase_1328.v0.1
confidential_coordination_private_wiring_dry_run_recorded_phase_1328
reproducibility_pass_recorded_phase_1328
public_confidential_coordination_serving_not_enabled_phase_1328
phase_1329_window_1317_1329_closure_next
public_rc_remains_blocked_after_phase_1328
```

Phase 1328 completed the CCSS-005 private OpenClaw/NemoClaw-compatible droplet
dry run on real private DigitalOcean/Tailscale nodes `ilc-node-2`,
`ilc-node-3`, and `ilc-node-6`. The run used private Git-bundle sync, verified
full mesh reachability, clean remote Git state, UFW Tailscale-only inbound,
OpenClaw local workspace skill readiness on `ilc-node-6`, no OpenClaw gateway
listener on `18789` or `19001`, and deterministic CCSS-001 through CCSS-004
sample construction on all three nodes. It does not create public serving,
public P2P, public confidential coordination serving, public messaging, source
publication, OpenClaw skill publication, ClawHub listing, identity artifacts,
wallet writes, ECU minting, ILC settlement, value-path activation, release
authority, signing authority, or Atlas-G tail authority.

Phase 1329 completion note:

```text
window_1317_1329_closed_phase_1329
window_1317_1329_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1329_window_1317_1329_closure_complete
window_1330_plus_sequence_lock_required_before_next_phase_assignment
release_dry_run_ccss_atlas_g_blockers_classified_phase_1329
public_rc_remains_blocked_after_phase_1329
```

Phase 1329 closes Window 1317-1329 with handoff
`docs/specs/ilc_window_1317_1329_handoff_1329_v0.1.md`. CCSS is complete enough as private/local evidence and is not a first-RC blocker by default unless a
later Window 1330+ sequence lock explicitly selects public confidential
coordination serving as first-RC scope. `ATLAS-G-007 through ATLAS-G-010` remain
carried forward outside the CCSS lane. Source allowlist export execution, clean
materialized public tree production, release artifact production, release-key
generation, release envelope production, public claimability/API authority,
public P2P, public sidecar/projection serving, wallet-facing activation, ECU
minting, ILC settlement, identity bootstrap, counsel review, and publication
authority remain blocked.

## 4. Window 1330-1342 - Final RC and Signing Gate

| Phase | Scope | Blocker addressed | Task lane |
|-------|-------|-------------------|-----------|
| 1330 | Sequence lock for final RC and signing gate | Opens no final publication/signing authority by itself | Planning/frontier |
| 1331 | Capsule v5.55 release-candidate freeze | Freezes candidate frontier before final gates | Planning/frontier |
| 1332 | Final deterministic code/security audit | Last code/security blocker audit | Audit/release |
| 1333 | Source allowlist export execution gate | Executes or blocks clean source export; must strip `PUBLIC_RC_EXCLUDE` helpers and fail on remaining markers/imports | Phase 1255 / Gap 14 |
| 1334 | Release artifact production gate | Produces release artifacts only if export gate passes | Phase 1213 / release |
| 1335 | Release keys/envelopes generation gate | Generates keys/envelopes only with explicit authority | Release/signing |
| 1336 | Public claimability/API activation gate or explicit no-claim carry-forward | Final claimability authority decision | Gap 13 |
| 1337 | TransportPrincipal/sidecar public-path activation gate or explicit exclusion, including any confidential coordination public-serving claim | Public-path activation decision; local/private CCSS dry-run evidence is not public authority | Gap 9 / Gap 10 / CCSS |
| 1338 | Wallet/ECU/ILC activation gate or explicit carry-forward | Value-path activation decision | Gap 12 / Gap 13 |
| 1339 | Genesis Atlas mutation/regeneration finalization | Final Atlas mutation/regeneration decision | ATLAS-G-007/008 |
| 1340 | v0.2 signing ceremony gate | Signing only if explicitly authorized | ATLAS-G-009/010 |
| 1341 | Public RC publication/claim gate | Public RC claim only if all selected blockers are closed | Public RC |
| 1342 | Closure handoff and next-window routing if anything remains blocked | Honest closure and carry-forward | Planning/frontier |

Phase 1333 is the execution gate for stripping, if public export is authorized.
It must not carry dual-use internal helper scaffolds into the public package.
The gate should reject the candidate export if any of these are true:

- a `PUBLIC_RC_EXCLUDE` marker remains in the exported tree;
- an exported module imports a stripped helper;
- an exported package profile still requires an internal fail-closed helper;
- helper flags are flipped from false to true instead of replacing or removing
  the helper;
- the manifest omits marker-scan or import-scan evidence.
- untagged legacy docs/research/planning files are included without explicit
  legacy review evidence.

Phase 1337 is the execution-or-exclusion gate for any public graph-native
sidecar serving claim. If the selected public RC remains the OpenClaw/NemoClaw
skill-first no-public-P2P profile, the expected outcome may be explicit
exclusion of public sidecar serving while keeping local/private sidecar suite
operation. Public sidecar serving must not be inferred from successful local
OpenClaw droplet tests.

Phase 1337 executed on 2026-05-14 and selected explicit first-RC exclusion:

```text
public_path_sidecar_activation_or_exclusion_gate_phase_1337.v0.1
public_path_sidecar_activation_or_exclusion_gate_verdict=excluded_from_first_rc
phase_1337_status=complete_excluded_from_first_rc
phase_1338_wallet_ecu_ilc_activation_gate_next
public_rc_remains_blocked_after_phase_1337
```

The exclusion preserves the future public serving lane without implying any
current public TransportPrincipal path, public P2P/fetch, public sidecar
projection serving, public listener, peer discovery, non-loopback bind, or
public confidential coordination serving.

Phase 1341 must not imply a public confidential messaging or coordination
product unless Phase 1337 explicitly selected and passed that scope.

Phase 1341 must also not imply that public OpenClaw/NemoClaw users, digital
agents, or local ILC identities are Genesis-rooted unless a prior identity
bootstrap ADR/CDL or equivalent spec has defined and rehearsed the required
agent birth attestation or equivalent Genesis-rooted identity-origin proof.

Phase 1338 executed on 2026-05-14 and selected no-activation carry-forward:

```text
wallet_ecu_ilc_activation_or_carry_forward_gate_phase_1338.v0.1
wallet_ecu_ilc_activation_or_carry_forward_gate_verdict=carry_forward_no_activation
phase_1338_status=complete_carry_forward_no_activation
phase_1339_atlas_g_mutation_regeneration_finalization_next
public_rc_remains_blocked_after_phase_1338
```

The carry-forward preserves the future wallet/ECU/ILC lane without implying any
current wallet-facing withdrawal/transfer/spend request, wallet-provider
signing, wallet-provider ledger-write, wallet write, withdrawal runtime, ECU
minting, ILC settlement, settlement-root publication, public claim endpoint, or
value-path activation.

## 5. Post-1342 Phase Windows — Comprehensive Gap Closure Plan

**Recorded:** 2026-05-14 (revised same day, second pass: incorporates M-series
Mysticeti completion review, Window 1377+ item-by-item repo audit, and full
CDL/ADR gap audit). Planning-only guidance. This section supersedes all earlier
post-1342 drafts. The first revision (CDL/ADR gap audit) expanded scope from
public claimability governance only to three windows. This second revision
re-sequences based on the M-series findings (M-001 through M-022 complete;
`ilc_consensus/` Rust crate is the full ILC-native DAG-BFT implementation; the
earlier "20–30 phases" Mysticeti estimate was wrong — ~7 phases of production
wiring remain) and the Window 1377+ audit (CDL-043/044, CDL-057, CDL-006/009,
and reputation.py H11 all have more prior work than the 1377+ table implied and
can be moved to concrete windows).

**Mysticeti status:** M-series (M-001–M-022) is complete. `ilc_consensus/`
contains the full Rust DAG-BFT crate with 4-validator M-009 testnet config.
HIGH-002 fixed (Phase 842). CDL-067 ratified (Phase 709). Option B selected
(Phase 814). Remaining: `ilc_core/` production gRPC/QUIC bridge (~1 phase);
HIGH-001 two-layer defense (~1 phase); multi-operator non-loopback testnet
(~1 phase); SEC-007a/b updates; non-CDL-053 blocking-authority vehicle
selection plus CDL-057 activation review (~1 phase).
SEC-004 live rotation wiring is scaffolded in `fast_path.rs` and gates on
CDL-017 (already Phase 1353).

Window 1343-1368 opened through Phase 1343 after explicit `GO Phase 1343`.
Later windows in this section remain closed until their own sequence-lock phases
execute with explicit `GO Phase NNNN`.

```text
forward_phase_windows_post_1342_comprehensive_gap_closure_plan_revised_2026_05_14_v2
window_1343_1368_issuance_economics_validator_governance_cdl_v6_mysticeti_wiring
window_1369_1390_public_claimability_governance_cdl_006_009_external_audit
window_1391_1398_mode_2_refutation_adjudication_and_settlement
window_1399_plus_sovereign_substrate_long_range_genuine_deferrals_only
phase_1366_soft_rc_gate_replaces_earlier_phase_1358
phase_1389_public_claimability_activation_gate_replaces_earlier_phase_1375
mysticeti_m_series_complete_7_phases_remaining_not_20_30
window_1343_1368_sequence_lock_committed
context_capsule_v5_56_window_1343_sequence_lock_phase_1343.v0.1
phase_1344_issuance_stack_scoping_next
cdl_053_vehicle_collision_recorded_phase_1343
issuance_stack_scoping_phase_1344.v0.1
cdl_053_vehicle_collision_resolved_or_rerouted_phase_1344
blocking_authority_vehicle_must_not_be_cdl_053_phase_1344
phase_1345_emission_engine_next
cdl_025_emission_schedule_runtime_phase_1345.v0.1
cdl_026_cmax_cap_runtime_phase_1345.v0.1
cdl_027_epoch_length_runtime_phase_1345.v0.1
c_max_enforcement_runtime_phase_1345
devnet_production_transition_gate_recorded_phase_1345
production_minting_not_activated_phase_1345
cdl_028_fee_burn_split_runtime_phase_1346.v0.1
fee_burn_10_percent_genesis_pool_phase_1346
fee_burn_not_activated_phase_1346
phase_1366_soft_rc_eligible_true_value_path_activation_required
no_direct_fee_burn_stub_found_phase_1346
cdl_029_allocation_distributor_runtime_phase_1347.v0.1
allocation_80_15_5_routing_phase_1347
production_distribution_not_activated_phase_1347
no_direct_allocation_stub_found_phase_1347
genesis_overhead_cap_blocked_guard_phase_1347_fix1
genesis_overhead_cap_blocked_dust_routing_deferred
cdl_029_post_theta_hard_routing_implementation_deferred_pending_decimal_governor
split_quote_clarified_not_full_genesis_tranche_phase_1347_fix1
cdl_054_validator_reward_pool_routing_runtime_phase_1349.v0.1
cdl_047_treasury_dependency_phase_1349
validator_reward_distribution_not_activated_phase_1349
no_direct_validator_reward_stub_found_phase_1349
cdl_083_ejected_stake_treasury_distribution_phase_1350.v0.1
h_con_02_quorum_guard_phase_1350
epoch_attribution_settle_runtime_not_implemented_closed_phase_1350
ejected_stake_distribution_not_activated_phase_1350
cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1
p_min_p_max_bounds_cdl_027_derived_phase_1351
live_price_adjustment_not_activated_phase_1351
no_direct_price_clamp_stub_found_phase_1351
```

**Phase 1343 execution addendum:** Phase 1343 opened Window 1343-1368 through
Phase 1343 only and published Capsule v5.56. Phase 1344 is the next planned phase and is scoping-only.
The sequence lock confirmed the M-series and `ilc_consensus/`
status, but also recorded a vehicle collision: this plan's Phase 1362 currently
uses CDL-053 for blocking-authority activation, while older canon reserves
CDL-053 for Werner-credit architecture. Phase 1344 must resolve or reroute that
vehicle before any Phase 1362 prompt is executable.

**Phase 1344 execution addendum:** Phase 1344 published
`docs/specs/ilc_issuance_stack_scoping_window_1343_1368_v0.1.md` and records
`issuance_stack_scoping_phase_1344.v0.1`,
`cdl_053_vehicle_collision_resolved_or_rerouted_phase_1344`, and
`blocking_authority_vehicle_must_not_be_cdl_053_phase_1344`. Phase 1344 resolves
the vehicle collision by rerouting blocking-authority vehicle selection away
from CDL-053. Phase 1362 must choose or open a non-CDL-053 vehicle if blocking
authority is still desired. Phase 1344 also binds Phase 1345 to the Phase 267
CDL-025 evidence, Phase 273/275/298/600 `C_max` chain, and Phase 276 CDL-027
halving evidence, while preserving `production_minting_not_authorized_phase_1344`.

**Phase 1345 execution addendum:** Phase 1345 added the non-activating
`ilc_core/epoch/epoch_emission_runtime.py` quote engine and records
`cdl_025_emission_schedule_runtime_phase_1345.v0.1`,
`cdl_026_cmax_cap_runtime_phase_1345.v0.1`,
`cdl_027_epoch_length_runtime_phase_1345.v0.1`,
`c_max_enforcement_runtime_phase_1345`,
`devnet_production_transition_gate_recorded_phase_1345`, and
`production_minting_not_activated_phase_1345`. The runtime computes Decimal
emission quotes and cap-clamped budgets only. It does not write ledger state,
produce mint instructions, activate production mining, or mark soft-RC
eligibility.

**Phase 1345 Fix1 addendum:** Phase 1345 Fix1 repairs CDL-025/026/027 register
prose and hardens the Phase 1368 prompt. `C_max = 25,920,000 ILC` is recorded
without ambiguity as the Platonic Year/precessional-cycle constant (25,920 ×
1,000) carried through Phase 273/275/298/600 evidence and locked as
`C_MAX_ILC = Decimal("25920000")` in the Phase 1345 runtime. Phase 1368 is the
concrete production-minting activation-or-defer point: it may implement the
private soft-RC runtime gate only if Phase 1366 records `soft_rc_eligible=true`
and Phase 1367 records `phase_1366_blockers_addressed_or_clean_pass_phase_1367`;
otherwise it must record `production_minting_activation_deferred_phase_1368`.

**Phase 1346 execution addendum:** Phase 1346 added
`ilc_core/epoch/fee_burn_split_runtime.py` and records
`cdl_028_fee_burn_split_runtime_phase_1346.v0.1`,
`fee_burn_10_percent_genesis_pool_phase_1346`,
`fee_burn_not_activated_phase_1346`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_fee_burn_stub_found_phase_1346`. The runtime computes Decimal-only
CDL-028 fee-burn quotes: 10% of quantized per-epoch fees routes to
`genesis_burn_pool`, the remaining 90% remains in
`post_cdl_028_remaining_fee_pool`, and production fee collection remains
inactive. Phase 1346 Fix1 aligned the activation guard names to
`PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN = "fee_burn_not_activated_phase_1346"`
and `PRODUCTION_FEE_BURN_ACTIVATION_TOKEN =
"phase_1366_soft_rc_eligible_true_value_path_activation_required"`.

**Phase 1347 execution addendum:** Phase 1347 added
`ilc_core/epoch/allocation_distributor_runtime.py` and records
`cdl_029_allocation_distributor_runtime_phase_1347.v0.1`,
`allocation_80_15_5_routing_phase_1347`,
`production_distribution_not_activated_phase_1347`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_allocation_stub_found_phase_1347`. The runtime computes Decimal-only
CDL-029 allocation quotes: 80% routes to `performer_reward_pool`, 15% routes to
`auditor_reward_pool`, 5% routes to `genesis_overhead_pool`, sub-quantum
rounding residual routes to genesis overhead to preserve total balance, and
production distribution remains inactive.

**Phase 1349 execution addendum:** Phase 1349 added
`ilc_core/epoch/validator_reward_pool_routing_runtime.py` and records
`cdl_054_validator_reward_pool_routing_runtime_phase_1349.v0.1`,
`cdl_047_treasury_dependency_phase_1349`,
`validator_reward_distribution_not_activated_phase_1349`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_validator_reward_stub_found_phase_1349`. The runtime computes
Decimal-only CDL-054 validator reward-pool routing quotes: a `Decimal("0.02")`
SIM-010 validator reward fraction routes from the write-fee-burn pool through
the existing CDL-047 treasury cap/floor/velocity framework, and production
reward distribution remains inactive.

Runtime audit carry-forward for Phase 1366:
`treasury_epoch_budget_ilc` is caller-supplied in the Phase 1349 quote runtime.
This is acceptable while the runtime remains quote-only, but before any
soft-RC/value-path activation the Phase 1366 gate must verify
`phase_1366_treasury_epoch_budget_binding_verified`: the budget input must be
derived from the real epoch emission / treasury budget and must not be
caller-inflatable in a way that bypasses the CDL-047 `0.15 × B_e` bounty cap.
If unverified, Phase 1366 must fail closed with
`phase_1366_treasury_epoch_budget_binding_unverified`.

**Phase 1350 execution addendum:** Phase 1350 updated
`ilc_core/economics/epoch_attribution_settle_runtime.py`, repaired stale
`ilc_core/types.py` comments, and records
`cdl_083_ejected_stake_treasury_distribution_phase_1350.v0.1`,
`h_con_02_quorum_guard_phase_1350`,
`epoch_attribution_settle_runtime_not_implemented_closed_phase_1350`,
`ejected_stake_distribution_not_activated_phase_1350`, and
`phase_1366_soft_rc_eligible_true_value_path_activation_required`. Phase 1344
and current Phase 1350 discovery found no live CDL-083 `NotImplementedError`;
Phase 1350 therefore adds a default-off production quote boundary around the
already-ratified H-CON-02 evaluator. Production stake distribution remains
inactive.

**Phase 1351 execution addendum:** Phase 1351 added
`ilc_core/epoch/ecu_price_clamp_runtime.py` and records
`cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1`,
`p_min_p_max_bounds_cdl_027_derived_phase_1351`,
`live_price_adjustment_not_activated_phase_1351`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_price_clamp_stub_found_phase_1351`. CDL-030 bounds are
`P_min = 0.75` and `P_max = 1.30`, copied from Phase 277 ratification evidence
and anchored to CDL-027 `halving/H=48/1_month` schedule constants. Live price
adjustment remains inactive.

### ECU / ILC Layer Distinction — Standing Policy

**CDL-029 80/15/5 applies at ILC issuance/conversion settlement boundaries, not to local ECU
attribution events.** Local ECU generation for refutation, curation, productive work, or
aesthetic-panel rewards is governed by local operator policy and may be informed by
Werner-type productive-work attribution. CDL-081/083/084 settlement-grade attribution must be
checked only when a local event is promoted into an ILC conversion, epoch, or public-claim
path. The ILC layer is globally scarce, deterministic, and replay-safe; the ECU layer is
local, fast-moving, and context-sensitive by design. These two layers must not be conflated in
phase prompts or runtime contracts.

---

### Post-1342 window structure

```
Window 1343–1368  →  issuance economics + validator governance + CDL-V6
                      + Mysticeti production wire-up + CDL-043/044 + CDL-057 + reputation.py H11
                      → closes soft RC blockers; enables private VPS mining with BFT consensus
Window 1369–1390  →  public claimability governance + CDL-006/009 + external audit
                      CDL-088, identity bootstrap, activation gate — full public RC milestone (Phase 1389)
Window 1391-1398  →  Mode-2 refutation adjudication and settlement (opt-in CDL-052 path only:
                      local ECU incentive calibration, verdict/adjudication runtime, settlement-grade
                      recognition for cross-shard/ILC-facing refutations, epoch/ILC integration,
                      public-claim gate if RC claims active refutation rewards)
Window 1399+      →  sovereign substrate, long-range (CDL-021, CDL-031, ADR-0015, ADR-0016/0017)
                      genuine deferrals only — all items require live network data or post-soft-RC milestone
```

---

### Window 1343–1368 — Production Issuance Economics, Validator Governance, Mysticeti Wire-Up, and Soft RC Gate

**Purpose:** Close the soft RC blockers. After this window: ILC can be minted and
distributed on private VPSs per the CDL-025–031 schedule constants; validator
admission/ejection and topology shuffle VRF are live; CDL-V6 / Phase-597 Genesis
intervention enforcement runtime exists with the forward-plan hardening token
`cdl_v6_gov_b_to_gov_a_phase_1355`; `ilc_core/` routes production ECU
transfers through `ilc_consensus/` Mysticeti BFT fast path (the M-series built the
Rust crate — this window wires it into production `ilc_core/`); CDL-043/044
adaptive pruning is production-bound; CDL-057 blocking authority governance
ceremony is complete; reputation.py H11 float-kill is done.

**Sensitivity:** All phases SENSITIVE. CDL mutation phases require
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<N>`.

| Phase | Scope | CDL/ADR closed | Notes |
|-------|-------|----------------|-------|
| 1343 | Sequence lock + capsule v5.56 | — | SENSITIVE gate; explicit `GO Phase 1343` required |
| 1344 | Issuance stack scoping: production architecture for CDL-025/026/027/028/029 emission engine; design document before any implementation; CDL-053 collision rerouted away from blocking authority | CDL-025/026/027 design | COMPLETE; records `issuance_stack_scoping_phase_1344.v0.1`; no implementation or production minting authority |
| 1345 | Production epoch emission engine: CDL-025/026/027 non-activating quote runtime, C_max enforcement, devnet→production transition gate | CDL-025, CDL-026, CDL-027 | COMPLETE; records `production_minting_not_activated_phase_1345`; no ledger write or mint activation |
| 1346 | CDL-028 fee-burn split runtime (10% of per-epoch fees → genesis/burn) | CDL-028 | COMPLETE; records `fee_burn_not_activated_phase_1346`; gates future activation behind `phase_1366_soft_rc_eligible_true_value_path_activation_required`; no production fee collection or ledger write |
| 1347 | CDL-029 80/15/5 allocation distributor (per-epoch performer/auditor/genesis routing engine) | CDL-029 | COMPLETE; records `production_distribution_not_activated_phase_1347`; gates future activation behind `phase_1366_soft_rc_eligible_true_value_path_activation_required`; no production distribution or ledger write |
| 1347 Fix1 | Runtime-only theta-hard guard: clarify allocator as split quote, add Decimal `THETA_HARD_ILC`, fail closed when caller reports Genesis overhead cap-blocked | CDL-029 implementation guard | COMPLETE; records `genesis_overhead_cap_blocked_dust_routing_deferred`; no CDL mutation; post-theta_hard routing policy deferred to Phase 1351a |
| 1348 | CDL-047 treasury governance runtime (0.15×B_e bounty cap, 0.05 burn floor, 0.91 velocity alert floor monitoring) | CDL-047 | COMPLETE; records `treasury_not_activated_phase_1348`; gates future activation behind `phase_1366_soft_rc_eligible_true_value_path_activation_required`; no treasury activation or ledger write |
| 1349 | CDL-054 validator reward-pool routing runtime (governed routing through CDL-047 treasury framework) | CDL-054 | COMPLETE; records `validator_reward_distribution_not_activated_phase_1349`; gates future activation behind `phase_1366_soft_rc_eligible_true_value_path_activation_required`; no production reward distribution or ledger write |
| 1350 | CDL-083 ejected stake treasury distribution: default-off production boundary around existing H-CON-02 evaluator; stale `NotImplementedError` comments repaired | CDL-083 | COMPLETE; records `ejected_stake_distribution_not_activated_phase_1350`; gates future activation behind `phase_1366_soft_rc_eligible_true_value_path_activation_required`; no production stake distribution or ledger write |
| 1351 | CDL-030 ECU price clamp runtime (P_min/P_max bounds derived from CDL-027 schedule) | CDL-030 | COMPLETE; records `live_price_adjustment_not_activated_phase_1351`; gates future activation behind `phase_1366_soft_rc_eligible_true_value_path_activation_required`; no live price adjustment or ledger write |
| 1351a | CDL-029 post-theta_hard residual routing policy: two-tier sub-quantum residual routing — primary to CDL-083 Q4 caller-filtered upheld-refutation recipients; fallback to performer pool; non-zero full Genesis base tranche routing remains fail-closed | CDL-029 amendment; CDL-083 Q4 interaction | COMPLETE; records `cdl_029_post_theta_hard_dust_routing_amendment_phase_1351a.v0.1`, `post_theta_hard_routing_implemented_phase_1351a`, `production_distribution_not_activated_phase_1351a`, and `genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a`; CDL-052 full refutation economy semantics and local ECU attribution are out of scope — Window 1391-1398 |
| 1352 | Issuance economics integration gate: CDL-025–031/047/054/083 stack end-to-end, quote-level double-entry conservation, epoch-boundary test | Integration gate | COMPLETE; records `issuance_economics_integration_gate_pass`, `production_minting_not_activated_phase_1352`, and `phase_1352_quote_level_double_entry_conservation_not_live_ledger_settlement`; no ledger write or soft-RC eligibility |
| 1353 | CDL-017 validator admission/ejection: default-off `admit_validator` / `eject_validator` decision runtime; Phase 1353 binding tokens for existing SEC-004 `TransferCertificate.epoch` and historical validator-set rotation surface in `fast_path.rs` | CDL-017, SEC-004 | COMPLETE; records `production_validator_admission_not_activated_phase_1353`; first non-Genesis validator deployment and live ValidatorSet rotation remain behind later human gate |
| 1354 | CDL-068 topology shuffle runtime: epoch-hash v1 per-epoch shuffle quotes below the VRF threshold, `shuffle_cadence_epochs=1`, k-regular sizing, ≥10-validator VRF upgrade trigger | CDL-068 | COMPLETE; records `production_topology_shuffle_not_activated_phase_1354`, `epoch_hash_v1_posture_preserved_phase_1354`, and `vrf_upgrade_required_at_10_validators_phase_1354`; no production topology shuffle activation |
| 1355 | CDL-V6 / Phase-597 genesis intervention enforcement: `genesis_intervention_runtime.py`, persistent invocation counter (max 3 lifetime), one-invocation-per-proposal guard, one-epoch suspension guard, append-only log, epoch-60 ceiling enforcer, signed-audit-record reference, audit record writer; records `cdl_v6_gov_b_to_gov_a_phase_1355` as forward-plan hardening shorthand without CDL row mutation | CDL-V6, Phase 597 | COMPLETE; records `cdl_v6_genesis_intervention_runtime_phase_1355.v0.1`, `genesis_intervention_invocation_counter_max_3_phase_1355`, `append_only_invocation_log_phase_1355`, `epoch_ceiling_enforcer_phase_1355`, `cdl_v6_gov_b_to_gov_a_phase_1355`, `phase_597_bootstrap_suspensive_guardrail_bounds_phase_1355`, `cdl_v6_extraordinary_path_not_ordinary_governance_phase_1355`, `genesis_intervention_execution_not_authorized_phase_1355`, `signed_audit_record_required_for_real_invocation_phase_1355`, and `genesis_intervention_not_fired_in_tests_phase_1355`; no Genesis intervention execution or CDL mutation |
| 1356 | CDL-013 governance weight live integration: connect `governance_weight.py` output to live governance decision surfaces | CDL-013 | SENSITIVE; governance surface |
| 1357 | reputation.py H11 rewrite: Decimal float elimination throughout `reputation.py` and `governance_weight.py`; add `REPUTATION_RUNTIME_VERSION` + `CDL_013_DEPENDENCY` tokens; wire `compute_governance_weights()` output into governance call path | CDL-013 | SENSITIVE; blocked on Phase 1356; moves from prior 1391+ long-range bucket |
| 1358 | `ilc_core/` → `ilc_consensus/` production bridge: gRPC read adapter in `ilc_core/` (`GetEpoch`, `GetBalance`, `GetEpochRecord`, `GetEpochChain`); QUIC ECU transfer submission path from `ilc_core/` production economic routines to `ilc_consensus/` fast path (only `tools/testbed/` stubs exist today); gRPC service surface is `app_interface.rs`/`proto/ilc_app.proto` (NOT `fast_path.rs`); default-off adapter with lazy `grpcio` import; record `grpcio_dependency_explicit_phase_1358_or_later` prerequisite for Phase 1366 | ADR-0028 | SENSITIVE; first production Mysticeti wire-up; M-022 open item; moves from prior 1391+ long-range bucket; **NOTE: Phase 1358 builds default-off adapter only — live gRPC end-to-end proof is Phase 1360 deliverable** |
| 1359 | HIGH-001 two-layer defense: log-redaction runtime (replace plaintext AgentID in validator logs); transfer mixing/k-anonymity framework; required before any sender-privacy claim | M-022 HIGH-001 | SENSITIVE; security surface; moves from prior 1391+ long-range bucket |
| 1360 | Multi-operator non-loopback Mysticeti testnet: run 4-validator testnet across geographically distinct VPSs (M-009 was loopback-only); SEC-007a/b dependency updates (tonic 0.13+ upgrade resolving `protoc-bin-vendored` and `rand 0.8.6` Dependabot alerts); **must prove live Python→`ilc_consensus/` gRPC path end-to-end using Phase 1358 adapter against testnet (records `grpc_end_to_end_python_to_rust_proven_phase_1360`)** and confirm `grpcio` as explicit dependency; M-022 proved subprocess/export path only — gRPC path proof is a hard Phase 1366 prerequisite | ADR-0028, M-022 | SENSITIVE |
| 1361 | CDL-043/044 adaptive pruning completion: adaptive threshold logic per CDL-043 SIM-003 calibration anchors; CDL-044 `retention_epochs` as constitutionally-bound constant (not caller parameter); LMDB graph-level pruning path; CDL-071 Tier-2 epoch-scope enforcement | CDL-043, CDL-044 | SENSITIVE; moves from prior 1391+ long-range bucket |
| 1362 | Blocking-authority vehicle opening: Phase 1344 rerouted this away from CDL-053; select or open a non-CDL-053 vehicle if blocking authority remains desired | non-CDL-053 vehicle, CDL-057 | SENSITIVE; explicit `GO Phase 1362` required; CDL mutation; moves from prior 1391+ long-range bucket |
| 1363 | Blocking-authority deliberation/prelock: resolve open questions from Phase 1362; lock blocking-authority scope and any CDL-055/CDL-030 interaction clauses | TBD vehicle, CDL-057 | SENSITIVE |
| 1364 | Blocking-authority ratification + CDL-057 activation: ratify the selected vehicle; flip `BLOCKING_AUTHORITY_DEFERRED = True` -> `False` in `epoch_boundary_witness_runtime.py`; epoch-boundary witness lane becomes a blocking lane | TBD vehicle, CDL-057 | SENSITIVE; `ILC_CDL_MUTATION_AUTHORIZED=1` |
| 1365 | Capsule refresh (v5.57) + coherence report | — | NON-SENSITIVE after sequence lock |
| 1366 | Soft RC readiness gate: all issuance + validator + CDL-V6 + Mysticeti wire-up + CDL-043/044 + CDL-057 items must pass; verifies CDL-054/CDL-047 treasury budget binding; records `soft_rc_eligible=true` or explicit blockers | Readiness gate | SENSITIVE gate; explicit `GO Phase 1366` required; must record `phase_1366_treasury_epoch_budget_binding_verified` or blocker `phase_1366_treasury_epoch_budget_binding_unverified` |
| 1367 | Reserved for pre-gate fix pass | — | SENSITIVE |
| 1368 | Window 1343–1368 closure handoff: honest closure; records soft RC eligible status; conditionally implements the private soft-RC production minting runtime gate only after Phase 1366 `soft_rc_eligible=true` and Phase 1367 clean pass; otherwise records deferred activation | — | SENSITIVE; must record exactly one of `production_minting_activated_phase_1368` or `production_minting_activation_deferred_phase_1368` |

Phase 1348 execution addendum: `cdl_047_treasury_governance_runtime_phase_1348.v0.1`,
`bounty_cap_0_15_b_e_runtime_phase_1348`, `burn_floor_0_05_runtime_phase_1348`,
`velocity_alert_trigger_runtime_phase_1348`, `velocity_alert_floor_0_91_runtime_phase_1348`,
`treasury_not_activated_phase_1348`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_treasury_stub_found_phase_1348`.

Phase 1347 Fix1 execution addendum: `genesis_overhead_cap_blocked_guard_phase_1347_fix1`,
`genesis_overhead_cap_blocked_dust_routing_deferred`,
`cdl_029_post_theta_hard_routing_implementation_deferred_pending_decimal_governor`,
and `split_quote_clarified_not_full_genesis_tranche_phase_1347_fix1`.
This repair is runtime-only. It does not mutate CDL-029, import the float-based
Genesis accrual governor, or implement the post-theta_hard recipient/fallback
policy now routed to Phase 1351a.

Phase 1349 execution addendum: `cdl_054_validator_reward_pool_routing_runtime_phase_1349.v0.1`,
`cdl_047_treasury_dependency_phase_1349`,
`validator_reward_distribution_not_activated_phase_1349`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_validator_reward_stub_found_phase_1349`. This phase is runtime-only
and default-off. It does not mutate CDL-054, activate reward distribution, or
write ledger state.

Phase 1350 execution addendum: `cdl_083_ejected_stake_treasury_distribution_phase_1350.v0.1`,
`h_con_02_quorum_guard_phase_1350`,
`epoch_attribution_settle_runtime_not_implemented_closed_phase_1350`,
`ejected_stake_distribution_not_activated_phase_1350`, and
`phase_1366_soft_rc_eligible_true_value_path_activation_required`. This phase is
runtime-only and default-off. It does not mutate CDL-083, activate stake
distribution, or write ledger state.

Phase 1351 execution addendum: `cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1`,
`p_min_p_max_bounds_cdl_027_derived_phase_1351`,
`live_price_adjustment_not_activated_phase_1351`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_price_clamp_stub_found_phase_1351`. This phase is runtime-only and
default-off. It does not mutate CDL-030, activate live price adjustment, or write
ledger state.

Phase 1351a execution addendum: `cdl_029_post_theta_hard_dust_routing_amendment_phase_1351a.v0.1`,
`cdl_029_amendment_phase_1351a`,
`cdl_083_upheld_refutation_recipients_primary_dust_route_phase_1351a`,
`performer_pool_fallback_dust_route_phase_1351a`,
`post_theta_hard_routing_implemented_phase_1351a`,
`pre_theta_hard_routing_unchanged_phase_1351a`,
`production_distribution_not_activated_phase_1351a`, and
`genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a`. This phase amends CDL-029
and implements only sub-quantum residual routing at the ILC issuance/conversion
settlement boundary. It does not govern local ECU attribution, activate CDL-052
settlement semantics, route non-zero full Genesis base tranches, activate
production distribution, or write ledger state.

**Stop conditions for any phase in this window:**
- Phase 1345 produces production-minted ILC without explicit activation authorization
- Phase 1352 or 1366 passes without all prior phases landed
- Phase 1355 fires the genesis intervention brake more than once in any test context
- Phase 1358 routes live ECU transfers through `ilc_consensus/` without explicit activation authorization
- Any phase implies "soft RC mining is now live" without Phase 1366 recording `soft_rc_eligible=true`
- Phase 1368 records production minting activation without both Phase 1366 `soft_rc_eligible=true` and Phase 1367 clean pass evidence
- HIGH-001 log-redaction not complete and a phase makes any sender-privacy claim

---

### Window 1369–1390 — Public Claimability Governance, CDL-006/009, and External Audit

**Purpose:** Close the full public RC blockers. Phase 1389 is the first realistic
phase where `result=public_claimability_activated` can legally appear. All carry-
forward blockers from Phase 1336 must be confirmed closed before Phase 1389 passes.
CDL-006 (challenge node governance — policy ratified Phase 993, spec/runtime
unbuilt) and CDL-009 (fork legitimacy UX — policy ratified Phase 993, UX unbuilt)
are included here as governance completeness prerequisites for a trustworthy public
RC. The external security audit (M-022 open item #6) and multi-operator genesis key
ceremony (M-022 open item #7) are also gated before Phase 1389.

This window supersedes the earlier draft labeled Window 1361–1376, renumbered
to accommodate the Mysticeti/CDL-043/044/057/H11 phases added to Window 1343–1368,
and expanded with CDL-006/009, external audit, TLA+ disposition, and key ceremony.

**Sensitivity:** All phases SENSITIVE. CDL mutation phases require
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<N>`.

| Phase | Scope | Blocker addressed | Notes |
|-------|-------|-------------------|-------|
| 1369 | Sequence lock + capsule v5.58 | — | SENSITIVE gate; explicit `GO Phase 1369` required |
| 1370 | Agent birth attestation ADR: Genesis-rooted identity-origin proof; `agent_id` bound to signed Genesis/Atlas lineage anchor; non-custodial default; no private graph content as entropy | Genesis-rooted agent birth attestation | Prerequisite for identity bootstrap CDL |
| 1371 | Identity bootstrap CDL opening: non-custodial identity-seed path, ceremony modes (interactive + agent-mode), secure output target, no-stdout-fallback rule, Genesis-rooted birth attestation linkage | Identity bootstrap CDL | SENSITIVE CDL opening |
| 1372 | Identity bootstrap CDL deliberation/prelock | Identity bootstrap CDL | SENSITIVE |
| 1373 | Identity bootstrap CDL ratification | Identity bootstrap CDL | SENSITIVE; `ILC_CDL_MUTATION_AUTHORIZED=1` |
| 1374 | CDL-088 opening: public claimability authority; bounded scope; reciprocal scoring if included; ECU-escrow admission if included | CDL-088 not opened | SENSITIVE; explicit `GO Phase 1374` required |
| 1375 | CDL-088 deliberation/prelock | CDL-088 | SENSITIVE |
| 1376 | CDL-088 ratification | CDL-088 | SENSITIVE; `ILC_CDL_MUTATION_AUTHORIZED=1` |
| 1377 | Replay/nullifier + duplicate-claim registry policy CDL or ADR: what counts as a replay; nullifier construction and storage; epoch-bounded expiry; duplicate-claim rejection at public API layer | Replay/nullifier policy | SENSITIVE; required before any live claim endpoint |
| 1378 | Legacy `/v1/public/*` FastAPI route cleanup: remove or replace all routes flagged Phase 1301; prove no public-labeled route exists outside authorized public verifier surface | Legacy FastAPI routes | Mechanical fix; SENSITIVE because public-facing server |
| 1379 | ADR-0031 sidecar query runtime completeness: close `NotImplementedError` for all query types in `sidecar_query_runtime.py` | ADR-0031 partial | SENSITIVE; required for sidecar completeness |
| 1380 | CDL-048 ECU-to-ILC conversion path dry-run wiring: wire sweeper runtime in gate-closed state (no live activation); prove ECU→ILC flow semantics and double-entry correctness; actual value-path activation gated behind Phase 1387 hardening gate and Phase 1388 | CDL-048 dry-run | SENSITIVE; no live value-path activation in this phase |
| 1381 | CDL-006 challenge node spec: challenge record schema, multi-body (3-body) quorum logic, audit path writer, spec document (`challenge_node_runtime.py` stub) | CDL-006 (spec unbuilt) | SENSITIVE; governance completeness; moves from prior 1391+ long-range bucket |
| 1382 | CDL-006 challenge node runtime + tests: production `challenge_node_runtime.py`, quorum verification tests, audit-path record tests | CDL-006 | SENSITIVE |
| 1383 | CDL-009 fork legitimacy UX: badge schema + eligibility rules contract + CLI/operator surface for fork-signal inspection | CDL-009 (UX unbuilt) | SENSITIVE; governance completeness; moves from prior 1391+ long-range bucket |
| 1384 | External security audit engagement: open engagement with Trail of Bits, Sigma Prime, or Zellic; scope = `ilc_consensus/` BFT safety, `ilc_core/` economic surfaces, HIGH-001 defense review; initiates and funds engagement; Phase 1387 cannot pass until a signed audit report or signed risk-acceptance letter for any HIGH-severity consensus or economic finding is received | M-022 open item #6 | NON-SENSITIVE to initiate; signed report or explicit risk-acceptance required at Phase 1387 |
| 1385 | TLA+ SafetyNoDualCert disposition: either complete formal proof or record explicit governance decision to defer with rationale and bounded carry-forward authority (empirical M-019 confirmation is current coverage) | M-022 open item #1 | NON-SENSITIVE disposition doc |
| 1386 | Multi-operator genesis key ceremony: distribute genesis validator keys across ≥2 operators; production ceremony record; required before any production genesis-signed artifact | M-022 open item #7 | SENSITIVE; Genesis authority surface |
| 1387 | Pre-activation hardening gate: requires signed audit report or risk-acceptance letter for all HIGH-severity audit findings (from Phase 1384 engagement); confirms HIGH-001 defense verified in non-loopback deployment; records any remaining audit items as explicitly deferred with authority | Pre-activation gate | SENSITIVE gate; blocks on signed audit report for HIGH findings |
| 1388 | CDL-048 public ECU-to-ILC conversion path activation + counsel clearance: unlock sweeper runtime (first live value-path activation) after Phase 1387 hardening gate passes; simultaneous counsel sign-off on public verifier API surface | CDL-048 activation, Counsel clearance | SENSITIVE; first production value-path activation; blocks Phase 1389 |
| 1389 | **Public claimability/API activation gate** — re-executes Phase 1336 gate with all six blockers confirmed closed; `result=public_claimability_activated` is the full public RC milestone | All six Phase 1336 blockers | SENSITIVE; explicit `GO Phase 1389` required; fails closed if any predecessor open |
| 1390 | Window closure handoff | — | SENSITIVE |

**Strict dependency order:**
```
Phase 1369 sequence lock
    → Phase 1370 agent birth attestation ADR
        → Phase 1371 identity bootstrap CDL opening
            → Phase 1372 deliberation/prelock
                → Phase 1373 ratification
    → Phase 1374 CDL-088 opening  (scope drafting may begin in parallel; execution phase-ordered)
        → Phase 1375 deliberation/prelock
            → Phase 1376 ratification
    → Phase 1377 replay/nullifier policy
    → Phase 1378 FastAPI cleanup
    → Phase 1379 ADR-0031 sidecar query
    → Phase 1380 CDL-048 dry-run wiring  (requires 1373 + 1376; no activation)
    → Phase 1381 CDL-006 spec
        → Phase 1382 CDL-006 runtime + tests
    → Phase 1383 CDL-009 fork legitimacy UX
    → Phase 1384 external audit engagement  (parallel track; findings gate 1387)
    → Phase 1385 TLA+ SafetyNoDualCert disposition
    → Phase 1386 multi-operator key ceremony
        → Phase 1387 pre-activation hardening gate  (requires signed audit report for HIGH findings)
            → Phase 1388 CDL-048 activation + counsel clearance  (first live value-path)
                → Phase 1389 public claimability activation gate
                    → Phase 1390 closure
```

**Stop conditions for any phase in this window:**
- Identity bootstrap CDL not ratified and a phase creates identity artifacts, seed commitments, mnemonics, private keys, or secret-store writes
- CDL-088 not ratified and a phase activates the public claimability API or claim endpoint
- Replay/nullifier policy not closed and a phase activates a live claim endpoint
- Any phase implies "public claimability is now active" without Phase 1389 producing explicit `result=public_claimability_activated`

---

### Window 1391-1398 — Mode-2 Refutation Adjudication and Settlement

**Purpose:** Complete the opt-in CDL-052 Mode-2 Popperian evaluation path for settlement-grade
use. CDL-052 is ratified (Phase 466) and a runtime skeleton exists
(`ilc_core/epistemic/refutation_runtime.py`, `ilc_core/epistemic/novelty_check_runtime.py`),
but the following remain deferred. This is a named concrete window, not vague long-range debt.

**Layer clarification:** CDL-029 allocation rules (including the Phase 1351a amendment) apply
at ILC issuance and conversion settlement boundaries only. Local ECU generation for refutation
or productive work does not need to satisfy CDL-029 split requirements. This window governs
only the Mode-2 formal path for refutations seeking cross-shard, ILC-facing, or globally
recognized settlement status. The vast majority of graph refutation/curation activity remains
local ECU, operator-policy-governed, and outside this window's scope.

| Lane | CDL/ADR | Description | Notes |
|------|---------|-------------|-------|
| Local refutation incentive calibration | Local operator policy / Werner productive-work attribution; CDL-052 context only | Calibrate ECU reward ranges and KPIs for encouraging local refutation work. No global settlement required. Helps operators tune reward levels to get the desired rate of graph improvement and productive refutation. | Does not require C(R) traversal, CDL-029 split rules, CDL-083 Q4 attribution, or global settlement machinery |
| Verdict/adjudication runtime | CDL-052 Mode 2 / Mode 3 escalation | Generic closeout machinery for disputes, audits, and adjudication records. Formal Mode-2 refutations proceed through staking + novelty + challenge mechanics first; Mode-3 anomaly-triggered panel is the escalation/dispute path for contested novelty or anomaly cases only — not invoked for every refutation. Completes `process_refutation_submission()` adjudication closeout flow and ratifies or rejects any `corroborated_reuse` designation rules. | Mode-3 panel is dispute/escalation, not universal jury; `corroborated_reuse` is proposed vocabulary until ratified |
| Settlement-grade refutation recognition | CDL-052 Mode 2 / novelty requirement | Opt-in path for refutations seeking cross-shard/ILC-facing/globally recognized status. Stake bond calibration (`SUBMISSION_STAKE_AMOUNT_TBD`, `REFUTATION_STAKE_AMOUNT_TBD` currently TBD). Novelty verification: C(R) traversal is a proof-witness boundary for settlement-grade claims, not a universal network obligation. | Requires soft RC production data for stake calibration; 5 novelty-spec open items must be resolved |
| Epoch/ILC integration | CDL-029 amendment / CDL-083 Q4 | Wire settlement-grade upheld refutations through CDL-029 allocation; Phase 1351a establishes policy narrowly (caller-filtered list at ILC settlement boundary); this lane completes the full integration. | After verdict/adjudication runtime completes |
| Public-claim gate | Phase 1389 public RC gate | Blocks Phase 1389 public RC only if the RC claim explicitly asserts active refuter mining/refutation rewards are live at global settlement layer. Does not block Phase 1366 or Phase 1352. | Conditional |

**Phase 1351a carry-forward note:** Phase 1351a establishes the narrow CDL-029 post-theta_hard
ILC settlement residual routing policy (CDL-083 caller-filtered upheld-refutation recipients →
performer pool fallback). It does not activate CDL-052 settlement semantics or govern local
ECU refutation incentives. This window completes the production path for settlement-grade cases.

Runtime audit carry-forward: in the Phase 1351a allocator, the post-theta_hard
recipient path records `rounding_residual_to_upheld_refutation_recipients_ilc`
as a distinct quote field rather than consolidating it into performer, auditor,
or Genesis pools. Conservation is explicit only if downstream settlement
consumers include this field in the settlement identity. Window 1391-1398 must
therefore define the settlement consumer contract for this residual field before
activating any settlement-grade refutation reward path.

#### Ordering conditional

Default: this window opens after Window 1390 closure. Exception: if Phase 1389 public RC
explicitly claims active refutation rewards are live at the global settlement layer, the
verdict/adjudication runtime and settlement-grade recognition lanes must move into Window
1369-1390 before Phase 1389. This determination is made at the Window 1369-1390 sequence
lock — not before. Phase 1389 scope is not yet defined.

#### Accumulated context (recorded 2026-05-14 — survives context compression)

This section records all design decisions, canon anchors, and key facts established during
Window 1343-1368 planning so they survive context window compressions before this window opens.

**What already exists (do not rebuild):**

- CDL-052 ratified Phase 466: "full three-mode epistemic evaluation architecture." Three
  modes: Mode 1 = default reuse-valuation (all nodes), Mode 2 = Popperian elevation path
  (opt-in via `refutation_criterion` authored-envelope field), Mode 3 = anomaly-triggered
  auditor panel (escalation only, not universal).
- `ilc_core/epistemic/refutation_runtime.py` (Phase 478): validates refutation submissions
  (target_cid, agent_id, authored_envelope, refutation_criterion fields); handles
  novelty_failed path (return stake), challenge_succeeds path (partial slash), default
  hold-pending. `SUBMISSION_STAKE_AMOUNT_TBD` and `REFUTATION_STAKE_AMOUNT_TBD` are
  explicitly TBD pending simulation.
- `ilc_core/epistemic/novelty_check_runtime.py` (Phase 478): currently a simple
  duplicate-CID check (`_KNOWN_DUPLICATE_CIDS` hardcoded set). NOT full C(R) traversal.
  This is intentionally bounded — full C(R) traversal is an open item for this window.
- `ilc_core/consensus/popperian_gate_runtime.py` (Phase 398): CDL-V7 admissibility gate.
  `_ADMISSIBLE_CLAIM_FORMS = {"singular", "bounded_existential", "falsifiable_positive"}`.
  This is a decomposition ADMISSIBILITY gate, NOT a refutation settlement mechanism.
  Do NOT conflate CDL-V7 (admissibility) with CDL-083 Q4 (upheld-refutation attribution).
- `ilc_core/epistemic/node_submission_runtime.py` (Phase 477): CDL-052 Part 1.

**Key specs (read before drafting phase prompts for this window):**

- `docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md` — canonical Mode 1/2/3
  routing model. Establishes: static epistemic type enum was dropped; epistemic status
  emerges from behavior not declaration; Mode 2 is opt-in via `refutation_criterion` field;
  `corroborated_reuse` designation is proposed vocabulary (not yet ratified).
- `docs/specs/ilc_refutation_novelty_requirement_v0.1.md` — full novelty requirement spec.
  Three types of valid novelty: (1) new empirical evidence, (2) new counter-example,
  (3) new logical derivation from graph-independent premises. "New" = not representable as
  a content-addressed node in C(R) at refutation submission time. Five open items for
  ratification: (1) C(R) traversal algorithm (depth, timestamp anchor, cycles), (2)
  submission-gate vs challenge-target tradeoff, (3) partial novelty, (4) temporal decay
  interaction, (5) friendly refutation detection threshold.
- `docs/specs/ilc_refutation_criterion_schema_specification_462_v0.1.md` — `refutation_criterion`
  authored-envelope field: requires claim, evidence_type, scope_boundary. Authored-envelope
  placement only (CDL-034 conformance). A node carrying both `refutation_criterion` and
  `normative: true` is rejected.
- `docs/specs/ilc_minimal_staking_contract_specification_463_v0.1.md` — staking mechanics.
  Novelty fail → full stake return. Novelty passes but challenge succeeds → partial slash.
  Survives challenge → earn reward. Reward is proportional to reuse centrality of refuted
  node at REFUTATION SUBMISSION TIME (not original creation time). Numeric stake params TBD
  pending simulation (follow CDL-050/SIM-009 precedent: SIM first, then constitutional lock).
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md` — canonical Popperian analysis.

**Key design decisions (recorded 2026-05-14):**

1. **ECU/ILC layering (standing policy):** Local ECU is free-wheeling — local, fast-moving,
   context-sensitive, operator-policy-governed. CDL-029 80/15/5 and all ILC allocation rules
   apply ONLY at ILC issuance/conversion settlement boundaries. Do not force local ECU
   refutation events through CDL-029 split requirements. Werner-type productive work
   attribution may inform local ECU policy; CDL-081/083/084 settlement-grade attribution must
   be checked only when a local event is promoted into a settlement, epoch, or public-claim path.

2. **C(R) traversal is not a universal network obligation.** It is a proof-witness boundary
   for settlement-grade claims only. For settlement-grade recognition, the submitting agent
   provides evidence that a verifier can check against C(R). This is not a runtime obligation
   the whole graph runs for every local refutation.

3. **"Encrusted node" reward mechanism:** Reward proportional to reuse centrality at
   refutation submission time. As a node ages and accumulates genuine reuse, its centrality
   grows, making it more economically valuable to successfully refute. There is no separate
   accumulating bounty pool per node — the reuse centrality score IS that value proxy.

4. **Staking is a bond, not a pure fee.** Novelty failure returns stake in full. Stake is
   at risk only if refutation passes novelty but is successfully challenged. This design
   discourages spam without penalizing genuine but unsuccessful refutation attempts.

5. **Mode-3 is escalation, not universal jury.** Formal Mode-2 refutations proceed through
   staking + novelty + challenge mechanics. Mode-3 anomaly-triggered auditor panel activates
   only on: centrality spike, citation cluster anomaly, new-agent heavy-citation pattern, or
   formal challenge against a novelty decision. Not every refutation goes through a jury.

6. **Aesthetic/subjective nodes are a separate lane (CDL-059).** CDL-059 ratifies a
   diversity-maximizing aesthetic panel for Register 2 expressive content — orthogonal to
   Mode-2 Popperian truth-claim governance. Do not route aesthetic/normative/subjective
   nodes through Mode-2. `normative: true` flag opts a node OUT of Popperian evaluation.

7. **CDL-V7 vs CDL-083 Q4:** CDL-V7 = admissibility gate (can this decomposition be
   challenged?). CDL-083 Q4 = attribution on upheld refutation (REUSE_ATTRIBUTION_RATE=0.20
   to refuting_agent_id from epoch mint; caller-filters upheld events). The Phase 1351a
   amendment uses CDL-083 Q4 for ILC settlement residual routing, NOT CDL-V7.

8. **CDL-049:** bounded-existential claim form alignment. The popperian_gate_runtime.py
   `_ADMISSIBLE_CLAIM_FORMS` set should use `bounded_existential` (not bare `existential`).
   Phase 417 identified this as a MODERATE finding; CDL-049 was the fix vehicle (ratified
   Phase 427). Verify `popperian_gate_runtime.py` uses `bounded_existential` before drafting
   any Mode-2 prompts.

**Runtime tokens already in codebase:**

```
EPISTEMIC_RUNTIME_PART2_VERSION = "epistemic_refutation_novelty_reuse_runtime_478.v0.1"
EPISTEMIC_PART1_DEPENDENCY = "epistemic_node_submission_runtime_477.v0.1"
CDL_V7_RUNTIME_VERSION = "cdl_v7_popperian_gate_runtime_398.v0.1"
CDL_V7_DEPENDENCY = "cdl_v7_popperian_gate_398.v0.1"
SUBMISSION_STAKE_AMOUNT_TBD = "submission_stake_amount_tbd"
REFUTATION_STAKE_AMOUNT_TBD = "refutation_stake_amount_tbd"
REUSE_ATTRIBUTION_RATE = Decimal("0.20")  # CDL-081 / CDL-083 Q4
HCON02_QUORUM_FLOOR = Decimal("0.50")
HCON02_QUORUM_MINIMUM_VOTERS = 2
```

**What this window must NOT do:**

- Do not claim local ECU refutation incentives are globally governed by CDL-029
- Do not treat C(R) traversal as a universal network runtime obligation
- Do not invoke Mode-3 panel for every Mode-2 refutation
- Do not conflate CDL-V7 admissibility with CDL-083 Q4 upheld-refutation attribution
- Do not build a single "refutation economy" as if it is one graph-wide economic machine
- Do not activate public settlement-grade refutation reward claim paths without the applicable
  Phase 1389 / Window 1391-1398 gate; do not use this section to alter Phase 1366/1368
  ordinary production-minting activation boundaries
- Do not consume `rounding_residual_to_upheld_refutation_recipients_ilc` without an
  explicit settlement consumer contract that preserves conservation across the separate
  upheld-refutation residual field

---

### Window 1399+ — Sovereign Substrate and Long-Range Lanes

**Purpose:** Post-public-RC completion. All items below have genuine reasons for
post-public-RC sequencing: they require live network data for calibration, depend
on a post-soft-RC milestone gate, or are multi-window governance tracks. Items
previously listed here that had existing prior work (CDL-043/044, CDL-057,
CDL-006/009, reputation.py H11, ADR-0028 production wiring) have been moved to
concrete phases in Windows 1343–1368 or 1369–1390. Phase assignments for Window
1399+ items will be made when Window 1398 closure handoff is done.

| Lane | CDL/ADR | Description | Notes |
|------|---------|-------------|-------|
| CDL-021 Rust kernel port ratification | CDL-021 (open, never ratified) | Open CDL-021 deliberation after Phase 1366 soft RC gate confirms ADR-0028 Option B in production; `ilc_consensus/` BFT crate is the first Rust milestone; `ilc_core/` Python kernel port is remaining scope | After Phase 1366 soft RC gate; CDL-017 must be live first |
| CDL-031 dynamic ranking runtime | CDL-031 (ratified deferred, Phase 288) | CDL-019 invariant floor runtime must be built (Phase 1356 unlocks the prerequisite); then SIM re-run; then dynamic ranking policy runtime implementation | After Phase 1356 CDL-013/019 integration; 6+ phases |
| ADR-0015 node transfer economics | ADR-0015 (disposition Phase 721; no CDL, no runtime) | Transfer-tax rate + cooling-period epoch calibration SIM; CDL opening; transfer-tax and cooling-period runtimes; leasehold/reversion SIM-dependent | After public RC; requires live network data for rate calibration |
| ADR-0016/0017 productive ECU expansion + post-issuance | ADR-0016, ADR-0017 (roadmap entries only; no spec, no sim) | Productive credit creation runtime (bounties, conditional ECU issuance, funding requests, Popperian gate as loan-officer) + post-issuance economic transition (fee-burn adaptation, velocity control) | Long-range; genuinely requires public RC data; no ADR spec or sim exists yet |

---

### Genesis Manifest / v0.2 Signing Dependency

The Genesis compile verdict as of Phase 1338 was `FAIL_CORE_INADEQUATE`.
Phase 1339 executed ATLAS-G-007 and ATLAS-G-008 and closed the recipe failure.
The regenerated v0.2 candidate now reports `PARTIAL_WITH_STRUCTURAL_GAPS`,
`core_nodes_total=49`, `authority_traceable_core_nodes=49`,
`authority_traceable_core_nodes_ratio=1.000000`, and
`missing_decomposition_recipe_count=0`.

Phase 1339 added the minimum pre-signing nodes and constants:

- ADR-0037 itself as a Genesis node (governs the signing lineage contract)
- CDL-V1, CDL-V2, CDL-V3, CDL-V7 as CDL artifact nodes
- CDL-085 as the Werner phi-bound governing artifact node
- `REUSE_ATTRIBUTION_RATE=0.20` and `EDGE_MINT_PHI_BOUND=0.60` as `policy_constant` nodes
- the four missing edge decomposition recipes

Residual basis-reachability gaps are explicitly classified as compiler-coverage
debt, not an ATLAS-G-007/008 signing blocker. Phase 1340 later executed after
exact authority phrase `GO Phase 1340: authorize v0.2 signing ceremony` and
recorded `v0_2_signed`. Phase 1341 later executed after exact authority phrase
`GO Phase 1341: authorize public RC publication/claim` and recorded
`blocked_with_findings`. **No public RC publication/claim occurred.** Phase
1342 closed Window 1330-1342 with carry-forward.

```text
genesis_manifest_compile_verdict_partial_with_structural_gaps_after_phase_1339
atlas_g_007_executed_phase_1339
atlas_g_008_executed_phase_1339
phase_1339_atlas_g_tail_finalized
phase_1340_v0_2_signed
phase_1341_publication_blocked_with_findings
public_rc_remains_blocked_after_phase_1341
window_1330_1342_closed_phase_1342
window_1330_1342_closure_gate_verdict=pass_or_blocked_with_carry_forward
phase_1342_window_1330_1342_closure_complete
window_1343_plus_sequence_lock_required_before_next_phase_assignment
final_rc_publication_and_signing_blockers_classified_phase_1342
public_rc_final_status_recorded_phase_1342
adr_0037_added_to_genesis_manifest_phase_1339
cdl_v_series_added_to_genesis_manifest_phase_1339
```

### Window 1330-1342 Closure Disposition

Window 1330-1342 is CLOSED / PASS with carry-forward through Phase 1342. The
closure handoff is:

```text
docs/specs/ilc_window_1330_1342_handoff_1342_v0.1.md
```

Public RC final status is:

```text
public_rc_final_status=not_published_blocked_with_findings
```

The final Phase 1341 publication blockers are:

- `publication_target_or_tag_not_selected`
- `counsel_publication_clearance_missing`
- `release_artifact_not_release_signed`
- `public_claimability_api_not_activated`
- `public_path_p2p_sidecar_serving_not_activated`
- `wallet_ecu_ilc_value_path_not_activated`

At Phase 1342 closure, Window 1343+ was not yet open and required a sequence
lock before the next phase assignment. Window 1343-1368 later opened via Phase
1343; later windows remain closed until their own sequence-lock phases execute.

```text
forward_phase_windows_post_1342_three_window_structure_finalized_2026_05_14
window_1343_1368_soft_rc_gate_phase_1366
window_1369_1390_public_claimability_gate_phase_1389
window_1391_1398_mode_2_refutation_adjudication_and_settlement
window_1399_plus_genuine_deferrals_only
cdl_088_opening_routed_window_1369_1390_phase_1374
identity_bootstrap_adr_cdl_routed_window_1369_1390_phases_1370_1373
agent_birth_attestation_spec_routed_window_1369_1390_phase_1370
replay_nullifier_duplicate_claim_policy_routed_window_1369_1390_phase_1377
legacy_fastapi_public_routes_cleanup_routed_window_1369_1390_phase_1378
public_claimability_activation_gate_phase_1389
public_rc_remains_blocked_until_window_1369_1390_blockers_closed
```

### Background and carry-forward basis

Phase 1336 (Window 1330-1342) recorded an explicit no-claim carry-forward
verdict:

```text
public_claimability_api_activation_or_carry_forward_gate_verdict=no_claim_carry_forward
phase_1336_status=complete_no_claim_carry_forward
```

The following blockers are confirmed open as of Phase 1336 and have no closure
phase assignment inside Window 1330-1342:

| Blocker | Carry-forward source |
|---------|---------------------|
| CDL-088 not opened (constitutional gate for public claimability) | CDL register; Phase 1336 carry-forward |
| Genesis-rooted agent birth attestation spec does not exist | Phase 1323 report; Window 1317-1329 handoff §7 |
| Identity bootstrap ADR/CDL not drafted | CDL-069 note; Phase 1323 Fix3; forward plan §3 |
| Replay/nullifier + duplicate-claim registry policy unwritten | Phase 1306; carried through Phase 1329 |
| Legacy `/v1/public/*` FastAPI routes not cleaned up | Phase 1301 (`legacy_public_labeled_fastapi_routes_carry_forward_phase_1301`) |
| Counsel clearance for public verifier API surface | Provisional only; CDL-086 C1–C5 instruments pending |

The FastAPI route cleanup (Phase 1378) is a mechanical fix, but all governance
blockers (CDL-088, agent birth attestation ADR, identity bootstrap CDL, replay/
nullifier policy, counsel clearance) require governance decisions, new specs, or
counsel engagement before activation is possible. Window 1369+ is the correct
venue for all of them.

## 6. Non-Claims

This plan does not authorize:

- Window 1303+ execution;
- helper promotion or marker removal;
- source allowlist export execution;
- publish a repository or package;
- public repository publication;
- public package publication;
- release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- public launch claim;
- public claimability activation;
- public P2P/fetch/sidecar serving;
- public graph-native sidecar serving;
- public confidential messaging or confidential coordination serving;
- OpenClaw/NemoClaw as protocol substrate;
- wallet-facing withdrawal/transfer/spend requests, ECU minting, or ILC settlement;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- CDL mutation or CDL-088 opening;
- IP filing or paper publication.
