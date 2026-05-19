# ILC Forward Phase Windows 1303-1342 Packaging and Signing Plan v0.2

**Status:** Planning-only candidate guidance.
**Recorded:** 2026-05-10.
**Revised:** 2026-05-14 — comprehensive §5 rewrite (3-window post-1342 structure: issuance economics / public claimability governance / long-range); removed superseded single-Window-1343 section.
**Alignment addendum:** 2026-05-19 — Window 1391-1398 routing aligned to the J-series jury / epoch-work canonicalization prompts; the older Mode-2 refutation settlement section is preserved as a scoped input to the J-series, not the primary window label.
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
execute with explicit `GO Phase NNNN`, except where a later prompt explicitly
allows human `GO` for a non-sensitive planning-only phase. Phase 1391 / J-001
was executed under that narrower planning-only authority and did not open the
rest of Window 1391-1398.

```text
forward_phase_windows_post_1342_comprehensive_gap_closure_plan_revised_2026_05_14_v2
window_1343_1368_issuance_economics_validator_governance_cdl_v6_mysticeti_wiring
window_1369_1390_public_claimability_governance_cdl_006_009_external_audit
window_1391_1398_mode_2_refutation_adjudication_and_settlement
window_1391_1398_jury_epoch_work_canonicalization
window_1391_1398_mode_2_refutation_scope_preserved_inside_j_series
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
from CDL-053. Phase 1362 later opened CDL-089 as that non-CDL-053 vehicle.
Phase 1344 also binds Phase 1345 to the Phase 267
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

Runtime audit carry-forward status:
Phase 1366 failed closed with
`phase_1366_treasury_epoch_budget_binding_unverified` because
`treasury_epoch_budget_ilc` was caller-supplied in the Phase 1349 quote runtime.
Phase 1367 addressed this named blocker by deriving CDL-054
`treasury_epoch_budget_ilc` from the Phase 1345 capped epoch emission quote and
recording `phase_1366_treasury_epoch_budget_binding_verified`. Phase 1367 did
not re-run the full soft-RC gate or record `soft_rc_eligible=true`.

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

**Phase 1348 execution token carry-forward:** Phase 1348 added
`ilc_core/epoch/treasury_governance_runtime.py` and records
`cdl_047_treasury_governance_runtime_phase_1348.v0.1`,
`bounty_cap_0_15_b_e_runtime_phase_1348`,
`burn_floor_0_05_runtime_phase_1348`,
`velocity_alert_trigger_runtime_phase_1348`,
`velocity_alert_floor_0_91_runtime_phase_1348`,
`treasury_not_activated_phase_1348`,
`phase_1366_soft_rc_eligible_true_value_path_activation_required`, and
`no_direct_treasury_stub_found_phase_1348`. Production treasury behavior remains
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
Window 1391-1398  →  J-series jury / epoch-work canonicalization:
                      canon map, jury eligibility/assignment, public node review taxonomy,
                      jury incentive economics opening, epoch-start capability/maintenance contract,
                      default-off assignment quote runtime, shadow ingestion harness, activation gate.
                      The older Mode-2 refutation settlement scope remains preserved as input
                      to the taxonomy, incentive-economics, and activation-gate lanes.
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
| 1356 | CDL-013 governance weight live integration: connect `governance_weight.py` output to live governance decision surfaces | CDL-013 | COMPLETE; records `cdl_013_governance_weight_live_integration_phase_1356.v0.1`, `compute_governance_weights_in_call_path_phase_1356`, `production_governance_decisions_not_activated_phase_1356`, and `legacy_governance_weight_float_conversion_guard_phase_1356`; no production governance decision execution |
| 1357 | reputation.py H11 rewrite: Decimal float elimination throughout `reputation.py` and `governance_weight.py`; add `REPUTATION_RUNTIME_VERSION` + `CDL_013_DEPENDENCY` tokens; wire `compute_governance_weights()` output into governance call path | CDL-013 | COMPLETE; records `reputation_runtime_h11_float_kill_phase_1357.v0.1`, `reputation_no_float_arithmetic_phase_1357`, `governance_weight_no_float_arithmetic_phase_1357`, `production_reputation_scoring_not_activated_phase_1357`, and `routing_reputation_decimal_rewrite_deferred_pending_cdl_060_decimal_pipeline_phase_1357`; no production reputation scoring or governance execution |
| 1358 | `ilc_core/` → `ilc_consensus/` production bridge: gRPC read adapter in `ilc_core/` (`GetEpoch`, `GetBalance`, `GetEpochRecord`, `GetEpochChain`); QUIC ECU transfer submission path from `ilc_core/` production economic routines to `ilc_consensus/` fast path; gRPC service surface is `app_interface.rs`/`proto/ilc_app.proto` (NOT `fast_path.rs`); default-off adapter with lazy `grpcio` import; record `grpcio_dependency_explicit_phase_1358_or_later` prerequisite for Phase 1366 | ADR-0028 | COMPLETE; records `ilc_core_consensus_grpc_read_adapter_phase_1358.v0.1`, `quic_ecu_transfer_submission_path_phase_1358`, `testbed_stubs_replaced_production_path_phase_1358`, `live_ecu_transfer_not_activated_phase_1358`, and `adr_0028_production_bridge_partial_phase_1358`; default-off only; no live ECU transfer routing, settlement, wallet action, value-path activation, public serving, or production validator deployment; live Python-to-Rust gRPC proof remains a Phase 1360 deliverable and hard Phase 1366 prerequisite |
| 1359 | HIGH-001 two-layer defense: Python log-redaction runtime for plaintext AgentID log-write sites; Rust validator redaction reverified from Phase 776; default-off transfer mixing/k-anonymity activation facade over existing Row-5 PrivacyLane constants; log-layer blocker cleared, but no sender-privacy claim authorized | M-022 HIGH-001 | COMPLETE; records `high_001_log_redaction_runtime_phase_1359.v0.1`, `agent_id_plaintext_redacted_validator_logs_phase_1359`, `transfer_mixing_k_anonymity_framework_phase_1359`, `sender_privacy_claim_blocker_cleared_phase_1359`, and `mixing_framework_not_activated_production_phase_1359`; no production mixing activation, public serving, or sender-privacy claim |
| 1360 | Multi-operator non-loopback Mysticeti testnet: run 4-validator testnet across three VPS plus local control host (M-009 was loopback-only); SEC-007a/b dependency updates (tonic 0.13+ upgrade resolving `protoc-bin-vendored` and `rand 0.8.6` Dependabot alerts); **must prove live Python→`ilc_consensus/` gRPC path end-to-end using Phase 1358 adapter against testnet (records `grpc_end_to_end_python_to_rust_proven_phase_1360`)** and confirm `grpcio` as explicit dependency; M-022 proved subprocess/export path only — gRPC path proof is a hard Phase 1366 prerequisite | ADR-0028, M-022 | COMPLETE with Fix2a scope qualifier — SEC-007a/b done; tonic 0.14, rand@0.8.6 cleared from lockfile; `grpc_end_to_end_python_to_rust_proven_phase_1360` recorded via insecure-channel testnet proof over Tailscale (production TLS path not exercised; see 1386a); Fix2 later closed the Fix1 evidence gap only for directly-injected checkpoint/local commit across four validators, not durable peer-to-peer BFT consensus sessions |
| 1360 Fix1 | Four-validator epoch finalization diagnostic: verify validator 1 behavior, harden control script restart/cadence handling, re-run private testnet, and collect or honestly block consensus evidence | ADR-0028, M-022 | BLOCKED_WITH_FINDINGS; NON-SENSITIVE; no CDL mutation; no Rust source change; records `phase_1360_fix1_epoch_finalization_still_blocked`; startup reproduced, UFW/macOS firewall ruled out as primary blockers, VPS accept path still closes before receive/dispatch, and no finalization proof token was recorded |
| 1360 Fix2 | Four-validator epoch finalization follow-up: validator 1 reassigned from macOS to ilc-node-2; all four validators accepted a directly-injected `EpochCheckpointMsg` and committed locally | ADR-0028, M-022 | COMPLETE; NON-SENSITIVE; no CDL mutation; no Rust source change; records `phase_1360_fix2_four_validator_epoch_finalization_proven` and `phase_1360_fix2_validator_1_quic_diagnosis_documented`; macOS inbound QUIC unreachable, consistent with Tailscale/QUIC routing issue but exact cause unconfirmed without packet capture; proof scope is checkpoint injection and local commit, not durable peer-to-peer BFT round |
| 1360 Fix2a | Documentation/test hardening: narrow Fix2 proof language, record validator endpoint registry architecture, and route durable connectivity to Window 1369-1390 | Planning/test hardening | COMPLETE; NON-SENSITIVE; records `fix2a_doc_test_hardening_phase_1360.v0.1` and `phase_1360_fix2a_proof_scope_narrowed_injected_checkpoint_only`; adds `docs/research/ilc_validator_connectivity_production_model_v0.1.md`; adds phases 1386b and 1386c; no runtime source change, no CDL mutation, no production activation |
| 1361 | CDL-043/044 adaptive pruning completion: adaptive threshold logic per CDL-043 SIM-003 calibration anchors; CDL-044 `retention_epochs` as constitutionally-bound constant (not caller parameter); LMDB graph-level pruning path; CDL-071 Tier-2 epoch-scope enforcement | CDL-043, CDL-044 | COMPLETE; records `cdl_043_adaptive_pruning_threshold_runtime_phase_1361.v0.1`, `cdl_044_retention_epochs_constitutional_constant_phase_1361`, `lmdb_graph_level_pruning_path_phase_1361`, `cdl_071_tier_2_epoch_scope_enforcement_phase_1361`, and `production_pruning_not_activated_phase_1361`; no production pruning activation |
| 1362 | Blocking-authority vehicle opening: open CDL-089 as the Phase-1344-selected non-CDL-053 vehicle; preserve CDL-053 Werner-credit reservation and CDL-088 public-claimability reservation; keep `BLOCKING_AUTHORITY_DEFERRED = True` | CDL-089, CDL-057 | COMPLETE; CDL mutation executed after explicit `GO Phase 1362` and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1362`; no prelock, ratification, or runtime activation |
| 1363 | Blocking-authority deliberation/prelock: CDL-089 prelock resolves Phase 1362 carry-forward questions; locks blocking-authority scope and CDL-055/CDL-030 interaction clauses | CDL-089, CDL-057 | COMPLETE; CDL-089 remains open and not ratified; `BLOCKING_AUTHORITY_DEFERRED` remains True; no runtime activation |
| 1364 | Blocking-authority ratification + CDL-057 activation: ratify the selected vehicle; flip `BLOCKING_AUTHORITY_DEFERRED = True` -> `False` in `epoch_boundary_witness_runtime.py`; epoch-boundary witness lane becomes a blocking lane | CDL-089, CDL-057 | COMPLETE; CDL-089 ratified in `5a32b19b`; runtime flag flipped in `37440146`; records `blocking_authority_ratified_phase_1364.v0.1`, `blocking_authority_deferred_false_epoch_boundary_witness_phase_1364`, `cdl_057_blocking_authority_active_phase_1364`, and `cdl_doc_and_runtime_separate_commits_phase_1364`; no public or production infrastructure activation |
| 1365 | Capsule refresh (v5.57) + coherence report | — | COMPLETE; NON-SENSITIVE; records `context_capsule_v5_57_window_1343_coherence_snapshot_phase_1365.v0.1`, `capsule_v5_57_supersedes_v5_56`, `coherence_report_phases_1343_1364_phase_1365`, and `phase_1366_soft_rc_gate_next`; no runtime, CDL, or value-path activation |
| 1366 | Soft RC readiness gate: all issuance + validator + CDL-V6 + Mysticeti wire-up + CDL-043/044 + CDL-057 items must pass; verifies CDL-054/CDL-047 treasury budget binding; records `soft_rc_eligible=true` or explicit blockers | Readiness gate | COMPLETE; records `soft_rc_readiness_gate_phase_1366.v0.1` and `soft_rc_eligible=false_with_blockers: [phase_1366_treasury_epoch_budget_binding_unverified]`; 13 prerequisite lanes confirmed, but treasury-budget binding unverified; no production minting or public activation |
| 1367 | Reserved for pre-gate fix pass | — | COMPLETE; SENSITIVE; records `pre_gate_fix_pass_phase_1367.v0.1`, `phase_1366_blockers_addressed_or_clean_pass_phase_1367`, `no_new_scope_introduced_phase_1367`, and `phase_1366_treasury_epoch_budget_binding_verified`; addresses the Phase 1366 treasury-budget binding blocker; no CDL mutation, value-path activation, public activation, production minting, or full soft-RC re-gate |
| 1368 | Window 1343–1368 closure handoff: honest closure; records soft RC eligible status; conditionally implements the private soft-RC production minting runtime gate only after Phase 1366 `soft_rc_eligible=true` and Phase 1367 clean pass; otherwise records deferred activation | — | COMPLETE; records `window_1343_1368_closed_phase_1368.v0.1`, `soft_rc_eligible_final_status_recorded_phase_1368`, `production_minting_activation_deferred_phase_1368`, `window_1369_not_open_phase_1368`, and `go_phase_1369_required_next`; no runtime file modified; no production minting or public activation |

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

**Phase 1360 / 1360 Fix1 / Fix2 / Fix2a carry-forward notes:**

- `grpc_end_to_end_python_to_rust_proven_phase_1360` was recorded via `grpc.insecure_channel()` against a plaintext testnet gRPC listener over private Tailscale. This satisfies the Phase 1366 gate prerequisite. The `build_secure_grpc_read_stub` TLS-only production constructor in `production_bridge.py` was NOT exercised in Phase 1360 — it requires a TLS-configured validator endpoint. Production TLS gRPC proof is a pre-production hardening item routed to Window 1369–1390 (see that window's carry-forward row). The Phase 1358 TLS-only path remains intact and unmodified.
- `phase_1360_fix2_four_validator_epoch_finalization_proven` was recorded. **Scope qualifier:** this token proves all four validators accepted a directly-injected `EpochCheckpointMsg` and committed locally. `handle_epoch_checkpoint_msg` (node.rs:816-844) does not gossip; each validator required a direct client send. This is not a durable peer-to-peer BFT round. The Phase 1366 gate reviewer should read this token as: "checkpoint ingestion and local commit path proven across four validators; persistent peer-to-peer consensus sessions not proven."
- `fix2a_doc_test_hardening_phase_1360.v0.1` and `phase_1360_fix2a_proof_scope_narrowed_injected_checkpoint_only` record the Fix2a proof-scope correction across the walkthrough, STATUS, forward plan, and tests. Durable production connectivity (direct QUIC + CDL-078 relay fallback + `QUIC_ENDPOINT` edge registry + persistent per-topology-epoch sessions) is scoped to phases 1386b and 1386c. See `docs/research/ilc_validator_connectivity_production_model_v0.1.md`.
- Epoch-0 sentinel reconciliation (`get_epoch_chain` from_epoch=0 / to_epoch=0 Rust vs. Python divergence) is still open from Phase 1358 Fix1 — routed to the production TLS/live-transfer hardening phase that exercises the TLS-configured Rust endpoint, not satisfied by Phase 1360 Fix1.

Phase 1368 closure addendum: Window 1343-1368 is CLOSED with carry-forward.
Phase 1368 records `window_1343_1368_closure_verdict_recorded_phase_1368` and
`window_1369_1390_entry_criteria_recorded_phase_1368`. The soft-RC final status
remains the inherited Phase 1366 verdict
`soft_rc_eligible=false_with_blockers: [phase_1366_treasury_epoch_budget_binding_unverified]`.
Phase 1367 fixed that named blocker, but did not re-run the full gate and did
not record `soft_rc_eligible=true`. Production minting remains deferred via
`production_minting_activation_deferred_phase_1368`. Window 1369-1390 is not
open until explicit `GO Phase 1369`.

**Stop conditions for any phase in this window:**
- Phase 1345 produces production-minted ILC without explicit activation authorization
- Phase 1352 or 1366 passes without all prior phases landed
- Phase 1355 fires the genesis intervention brake more than once in any test context
- Phase 1358 routes live ECU transfers through `ilc_consensus/` without explicit activation authorization
- Any phase implies "soft RC mining is now live" without Phase 1366 recording `soft_rc_eligible=true`
- Phase 1368 records production minting activation without both Phase 1366 `soft_rc_eligible=true` and Phase 1367 clean pass evidence
- HIGH-001 log-redaction not complete and a phase makes any sender-privacy claim

**Runtime hardening carry-forward (recorded 2026-05-16 — joint Codex + Claude Code audit):**

No production activation was found accidentally opened. Minting, fee burn, allocation, treasury, validator rewards, pruning, topology shuffle, transfer mixing, governance execution, and production bridge writes remain default-off/fail-closed. All canonical JSON surfaces use `sort_keys=True` and `allow_nan=False`. No float contamination, no bare `assert` in production paths, no PRNG, no missing timeouts. Eight implementation hardening items are carried forward into Window 1369:

| Sev | Finding | Location |
|-----|---------|----------|
| M | Huge but finite `Decimal` values (e.g. `Decimal("1e100")`) escape tokenized validation as raw `decimal.InvalidOperation` during `_quantize_*()` calls; input boundary rejects floats and non-finite values but does not cap magnitude/exponent | `fee_burn_split_runtime.py` line 87; `allocation_distributor_runtime.py` line 197; `treasury_governance_runtime.py` line 107; `ecu_price_clamp_runtime.py` line 105; `validator_reward_pool_routing_runtime.py` line 168; `epoch_attribution_settle_runtime.py` line 61 |
| M | Genesis intervention counter TOCTOU: read/evaluate/write is not atomic; concurrent accepted calls could push `lifetime_invocations` past 3; blast radius limited to extra audit log entries (execution is still unconditionally blocked by `require_genesis_intervention_execution_authorization()`) | `genesis_intervention_runtime.py` line 427 |
| M | Governance weight accepts unbounded `quality_score`, `base_weight`, `contribution_bonus`, and `genesis_baseline_weight`; one malformed or hostile input can dominate normalized shares; contract unclear: if pre-normalized trusted inputs, document it; if operator-supplied, add bounds (at minimum `quality_score <= 1`) | `governance_weight.py` lines 73, 109, 198 |
| L/M | Genesis intervention audit log append is non-atomic; concurrent writers can interleave log lines; pair the fix with the counter-lock fix above | `genesis_intervention_runtime.py` line 321 |
| L/M | LMDB adaptive pruning batch cap applies to total cursor entries scanned, not eligible tier-2 records; a large prefix of non-prunable records starves pruning indefinitely unless caller repeatedly resumes with a cursor/key | `lmdb_graph_pruning_runtime.py` line 154 |
| L | LMDB pruning opens a write transaction even when `dry_run=True`; no data is written (transaction is aborted), but an exclusive write lock is acquired unnecessarily | `lmdb_graph_pruning_runtime.py` line 154 |
| L | `get_epoch_chain()` materialized `records = list(...)` before bounding by `max_epoch_chain_records`; gRPC already decoded the response so this was not the primary memory boundary, but a receive-size/channel limit was required for production use | CLOSED Phase 1386a; `production_bridge.py` now sets `grpc.max_receive_message_length` and bounds record iteration before normalization |
| L | `_decimal_to_string()` dead branch: both branches return the same expression; no behavioral impact | Seven epoch/economic runtimes |

**Recommended fix sequencing for Window 1369:** Decimal magnitude hardening first (6 economic runtimes), then Genesis counter race (constitutional invariant, add file-lock wrapper around full read/evaluate/write in `record_genesis_intervention_guardrail_invocation`; audit log shares same lock), then governance input bounds/contract decision. LMDB improvements and `_decimal_to_string` cleanup can be bundled into a single low-risk cleanup phase. `get_epoch_chain` channel limits were closed by Phase 1386a (production TLS gRPC proof). None of these block opening Phase 1369; all should be recorded in the Phase 1369 sequence lock as carry-forward hardening.

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
The accepted ADR/CDL coverage audit and public-only economics admission firewall
are added as Phase 1387a: public RC must not proceed if any accepted ADR/CDL
functionality remains unrouted or if private/semi-private graph work can construct
public ECU, reputation, settlement, corroboration, or claimability events. Historical
"shadow economics" phrasing is operator-local advisory scoring only, not protocol
ECU generation.

This window supersedes the earlier draft labeled Window 1361–1376, renumbered
to accommodate the Mysticeti/CDL-043/044/057/H11 phases added to Window 1343–1368,
and expanded with CDL-006/009, external audit, TLA+ disposition, and key ceremony.

**Sensitivity:** All phases SENSITIVE. CDL mutation phases require
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<N>`.

| Phase | Scope | Blocker addressed | Notes |
|-------|-------|-------------------|-------|
| 1369 | Sequence lock + capsule v5.58 | — | COMPLETE: sequence lock committed `4a918075`; Fix1 numeric hardening committed `65531719`; records the 8 Window 1343-1368 runtime hardening carry-forward items as assigned to Fix1 or Phase 1386a |
| 1370 | Agent birth attestation ADR: Genesis-rooted identity-origin proof; `agent_id` bound to signed Genesis/Atlas lineage anchor; non-custodial default; no private graph content as entropy | Genesis-rooted agent birth attestation | COMPLETE: ADR-0038 committed `794df06e`; records `agent_birth_attestation_adr_0038_committed_phase_1370`; no identity artifact, seed generation, CDL mutation, or runtime activation |
| 1371 | Identity bootstrap CDL opening: non-custodial identity-seed path, ceremony modes (interactive + agent-mode), secure output target, no-stdout-fallback rule, Genesis-rooted birth attestation linkage | Identity bootstrap CDL | COMPLETE: CDL-only opening commit `580bf148`; support/backfill commit `ef1aebb9`; records `cdl_090_identity_bootstrap_opened_phase_1371`, `cdl_090_not_ratified_phase_1371`, and `cdl_090_non_custodial_seed_path_candidate_scope_phase_1371`; CDL-090 open only, no prelock/ratification/runtime change; CDL-088 remains unopened |
| 1372 | Identity bootstrap CDL deliberation/prelock: secure-output target contract, identity-seed non-rotation rule, recovery/rotation receipt chain, agent-mode no-secret-output contract, canonical attestation envelope, public artifact field contract, and environment-class distinction | Identity bootstrap CDL | COMPLETE: phase-close commit `9b62237f`; records `cdl_090_prelock_committed_phase_1372`, `cdl_090_not_ratified_phase_1372`, and `cdl_090_scope_constants_locked_phase_1372`; CDL-090 remains open/not ratified; no CDL register mutation or runtime change |
| 1373 | Identity bootstrap CDL ratification: ratify CDL-090 identity bootstrap governance contract while keeping identity artifact creation, runtime implementation, public identity activation, and public claimability separately gated | Identity bootstrap CDL | COMPLETE: CDL-only register commit `ff841ad2`; records `cdl_090_ratified_phase_1373`, `cdl_090_identity_bootstrap_ratification_evidence_committed`, and `cdl_090_historical_hardening_phase_1371_ref_asserted`; no runtime change; no CDL-088 opening |
| 1374 | CDL-088 opening: public claimability authority; bounded scope; reciprocal scoring if included; ECU-escrow admission if included | CDL-088 opening | COMPLETE: CDL-only opening commit `43bcddc0`; records `cdl_088_public_claimability_opened_phase_1374`, `cdl_088_not_ratified_phase_1374`, and `cdl_088_bounded_claimability_candidate_scope_phase_1374`; CDL-088 open only, no prelock/ratification/runtime change; no public claimability or claim endpoint activation |
| 1375 | CDL-088 deliberation/prelock: bounded public claimability condition, proof bundle, reciprocal identity/proof interlock, reciprocal formula deferral, ECU-escrow boundary, public-only economics claimability boundary, public verifier API prerequisites, and ratification-vs-activation split | CDL-088 | COMPLETE: phase-close commit `287cbcf5`; records `cdl_088_prelock_committed_phase_1375`, `cdl_088_not_ratified_phase_1375`, and `cdl_088_scope_constants_locked_phase_1375`; CDL-088 remains open/not ratified; no CDL register mutation, runtime change, public claimability, public verifier API, or claim endpoint activation |
| 1376 | CDL-088 ratification: ratify bounded public claimability authority, proof bundle, reciprocal identity/proof interlock, reciprocal formula deferral, conditional ECU-escrow boundary, public-only economics claimability boundary, public verifier API prerequisites, ratification-vs-activation split, and default-closed claim endpoint rule | CDL-088 | COMPLETE: CDL-only register commit `3d8ce11e`; records `cdl_088_ratified_phase_1376`, `cdl_088_public_claimability_ratification_evidence_committed`, and `cdl_088_historical_hardening_phase_1374_ref_asserted`; no runtime change; no public claimability, public verifier API, claim endpoint, wallet, ECU, ILC, value-path, public RC, or public launch activation; Phase 1377 next; Phase 1380 requires 1373+1376 both complete before dry-run wiring; Phase 1389 remains the first possible public claimability activation gate |
| 1377 | Replay/nullifier + duplicate-claim registry policy: defines replay as active public claim material reuse; defines `claim_nullifier_v1`, `claim_nullifier_registry_v1`, issuance-epoch expiry, and duplicate-claim rejection at public API admission before verifier or economic processing | Replay/nullifier policy | COMPLETE: phase-close commit `4f9715c6`; records `replay_nullifier_policy_committed_phase_1377`, `nullifier_epoch_bounded_expiry_policy_defined`, `duplicate_claim_rejection_policy_defined`, and `claim_endpoint_not_activated_phase_1377`; policy-only, no runtime change, no CDL mutation, no claim endpoint or public claimability activation; Phase 1378 next; Phase 1389 must still verify implementation/registry evidence before activation |
| 1378 | Legacy `/v1/public/*` FastAPI route cleanup: removed all Phase 1301 flagged `/v1/public/*` route handlers from `ilc_core/server.py`; underlying local runtimes remain local substrates only; default FastAPI app registers no `/v1/public/*` routes | Legacy FastAPI routes | COMPLETE: 29f11571; records `legacy_public_labeled_fastapi_routes_cleaned_phase_1378` and `no_unauthorized_public_labeled_route_exists_phase_1378`; no public claimability, public verifier API, claim endpoint, wallet, ECU, ILC, value-path, public RC, or public launch activation; Phase 1379 next |
| 1379 | ADR-0031 sidecar query runtime completeness: removed the residual `NotImplementedError` fallback from `sidecar_query_runtime.py`; direct-read discovery confirmed all locked query types (`ego_graph`, `centrality_metrics`, `convergence_trace`) already dispatch to read-only implementations | ADR-0031 partial | COMPLETE: 014f4664; records `adr_0031_sidecar_query_runtime_completeness_phase_1379` and `sidecar_query_no_mutation_authority_confirmed_phase_1379`; no sidecar mutation authority, write path, public serving, public projection endpoint, public claimability, wallet, ECU, ILC, value-path, public RC, or public launch activation; Phase 1380 next |
| 1380 | CDL-048 ECU-to-ILC conversion path dry-run wiring: wire sweeper runtime in gate-closed state (no live activation); prove ECU→ILC flow semantics and double-entry correctness; actual value-path activation gated behind Phase 1387 hardening gate and Phase 1388 | CDL-048 dry-run | COMPLETE: `2c7a32ed`; records `cdl_048_dry_run_wiring_phase_1380`, `cdl_048_not_activated_phase_1380`, `gate_closed_state_confirmed_phase_1380`, and `double_entry_conservation_proven_wire_level_phase_1380`; adds gate-closed dry-run quote path in `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`; no live conversion, ledger write, wallet write, public claimability, ECU minting, ILC settlement, or value-path activation |
| 1381 | CDL-006 challenge node spec: challenge record schema, multi-body (3-body) quorum logic, audit path writer, spec document (`challenge_node_runtime.py` stub) | CDL-006 spec/stub | COMPLETE: phase-close commit `ad1a7c50`; records `cdl_006_challenge_node_spec_phase_1381`, `cdl_006_challenge_node_runtime_stub_phase_1381`, and `cdl_006_multi_body_3_body_quorum_spec_committed`; stub only, no production quorum verification, audit-path write, CDL mutation, public serving, or governance activation |
| 1382 | CDL-006 challenge node runtime + tests: production `challenge_node_runtime.py`, quorum verification tests, audit-path record tests | CDL-006 | COMPLETE: phase-close commit `b46496bf`; records `cdl_006_challenge_node_runtime_phase_1382.v0.1`, `cdl_006_3_body_quorum_verification_implemented`, and `cdl_006_audit_path_record_writer_implemented`; runtime helper only, no challenge triggering, governance decision execution, graph state write, CDL mutation, public serving, public claimability, or governance activation |
| 1383 | CDL-009 fork legitimacy UX: badge schema + eligibility rules contract + CLI/operator surface for fork-signal inspection | CDL-009 | COMPLETE: phase-close commit `1992111e`; records `cdl_009_fork_legitimacy_ux_phase_1383.v0.1`, `cdl_009_signature_badge_schema_implemented`, and `cdl_009_eligibility_rules_contract_committed`; CLI/operator-only helper, no public API, graph write, CDL mutation, public serving, or governance activation |
| 1384 | Security review scope record: document review path (AI-assisted LLM review + open source community contributions; commercial audit firm NOT required due to funding and anonymity constraints); scope = `ilc_consensus/` BFT safety, `ilc_core/` economic surfaces, HIGH-001 defense review; Phase 1387 requires a project-authority disposition document for each known HIGH-severity finding (not a commercial signed report) | M-022 open item #6 | COMPLETE: `a51f8599`; records `security_review_scope_recorded_phase_1384`, `audit_scope_bft_safety_economic_surfaces_high_001`, and `phase_1387_requires_project_authority_security_disposition`; scope record only, not the Phase 1387 disposition; no commercial audit firm engagement, runtime change, CDL mutation, public activation, public RC, sender-privacy claim, or HIGH-finding closure |
| 1385 | TLA+ SafetyNoDualCert disposition: COMPLETE via `tla_plus_safetynodualcert_disposed_phase_1385` and `safetynodualcert_deferred_with_authority_phase_1385`; owned-object Spec B bounded TLC evidence preserved, epoch-checkpoint/shared-object dual-cert safety deferred to Spec D or equivalent with bounded carry-forward authority | M-022 open item #1 | NON-SENSITIVE disposition doc |
| 1386 | Multi-operator genesis key ceremony: distribute genesis validator keys across ≥2 operators; production ceremony record; required before any production genesis-signed artifact | M-022 open item #7 | SENSITIVE; Genesis authority surface |
| 1386a | Production TLS gRPC path proof: configure testnet validators with self-signed TLS certificates; run `build_secure_grpc_read_stub` from `ilc_core/consensus/production_bridge.py` with `tls_root_certificates` against the TLS-enabled validator endpoint; record `production_tls_grpc_path_proven_phase_1386a`; also verify epoch-0 sentinel reconciliation (Rust `from_epoch=0` / `to_epoch=0` semantics and Python bridge forwarding) before any live ECU transfer activation | ADR-0028; Phase 1358 carry-forward | COMPLETE; `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md`; records `production_tls_grpc_path_proven_phase_1386a`, `epoch_0_sentinel_reconciliation_verified_phase_1386a`, and `get_epoch_chain_channel_limit_added_phase_1386a`; no production activation |
| 1386b | Validator endpoint registry ADR: define `QUIC_ENDPOINT` as an epoch-scoped signed edge on existing `agent_id` nodes; specify direct endpoint form and CDL-078 relay endpoint form; bind epoch scoping to CDL-068 topology shuffle; define update propagation without genesis restart; require a bounded read-only projection/cache derived from signed graph edges only, limited to the current topology epoch's validator set, invalidated and rebuilt on each topology shuffle, and never allowed to acquire its own write path | Durable validator connectivity prerequisite | COMPLETE; ADR-0039 accepted at `docs/adr/ADR_0039_Validator_Endpoint_Registry.md`; records `validator_endpoint_registry_adr_ratified_phase_1386b`, `quic_endpoint_epoch_scoped_signed_edge_defined`, `read_only_projection_contract_defined_phase_1386b`, and `no_hardcoded_peer_list_production_activation_path_phase_1386b`; no CDL mutation or runtime change |
| 1386c | Persistent validator QUIC connectivity proof: implement/prove persistent per-topology-epoch QUIC sessions in `ilc_consensus/`; direct QUIC peer-to-peer first; CDL-078 relay pass-through fallback second; no hardcoded peer list in activation path; validator addresses read from the 1386b registry projection; record `persistent_validator_quic_sessions_proven_phase_1386c` | Durable validator connectivity proof | COMPLETE; `ilc_consensus/src/persistent_quic.rs` added; direct QUIC and CDL-078 relay fallback proven; `settlement_path=mysticeti_fast_path` requires `endpoint_projection_path`; projection write-path acceptance test passes; no CDL mutation, `ilc_core/` mutation, public P2P activation, production validator deployment, relay service activation, value-path activation, or public RC claim |
| 1387 | Pre-activation hardening gate: requires project-authority security disposition for every known HIGH-severity finding in the Phase 1384 scope; confirms HIGH-001 defense verified in non-loopback deployment; confirms production TLS gRPC path proven (Phase 1386a); confirms 1386b endpoint-registry ADR ratified and 1386c persistent sessions proven, or each explicitly deferred with authority and bounded carry-forward scope; records any remaining audit items as explicitly deferred with authority | Pre-activation gate | COMPLETE: RE-RUN PASS; original v0.1 report failed closed with `gate_failed_reason=project_authority_security_disposition_missing`; Phase 1387-Fix committed the missing disposition and the v0.2 re-run report records `pre_activation_hardening_gate_pass_phase_1387`; Phase 1387a next |
| 1387a | Accepted ADR/CDL coverage audit + public-economics admission firewall: produce repo-derived matrix classifying every accepted ADR and ratified CDL as implemented, covered before public RC, documentation/governance-only, explicitly deferred outside public RC, or public-RC blocking; implement/prove fail-closed admission guard so public ECU/reputation/settlement/claimability events require public node visibility, public graph admission evidence, eligible public evaluation/promotion state, and zero private promotion carry-forward; clarify historical "shadow economics" phrasing as operator-local advisory scoring only, not protocol ECU generation | Accepted-functionality coverage; private-shard economics gap | COMPLETE: PASS; records `accepted_adr_cdl_runtime_coverage_matrix_phase_1387a`, `public_economics_requires_public_node_admission_verified_phase_1387a`, `private_visibility_excluded_from_public_economics_phase_1387a`, and `no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a` |
| 1387b | SIM-GENESIS-COMPILE-02: genesis node compilation review — canonize dirty `out/` compiler outputs (+2 source files since Phase 1339; structural metrics unchanged); classify 15 basis-unreachable core nodes into four categories (A: 3 bootstrap axioms; B: 4 post-genesis architecture ADRs; C: 3 post-genesis governance CDLs; D: 5 governance-calibrated economic parameters); propose two-tier verdict (`genesis_derivable` / `governance_extended`) to replace misleading `PARTIAL_WITH_STRUCTURAL_GAPS` label; formally defer ADR-0035 (homoiconic type definition system) with 3 completion criteria | SIM research; genesis compilation | COMPLETE: NON-SENSITIVE SIM phase; commits `3b6b7fef` + `6e478f23`; records `sim_genesis_compile_02_phase_1387b`; 11 tests; 15-node classification with 4-category disposition; ADR-0035 formally deferred to post-RC architecture series; no CDL mutation, `ilc_core/` modification, or public activation |
| 1387c | Compiler transition basis expansion + two-tier verdict: add 3 Category A bootstrap axioms (`artifact:genesis_intent_attestation_init_authority_map`, `artifact:genesis_agent1_pubkey_record_838a`, `ceremony:genesis_agent1_keygen_838a`) to `_basis_roots()` in `tools/genesis_compile_coverage_diagnostic.py`; add `tier_analysis` output section; update verdict logic to emit `GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL` when all core nodes basis-reachable and source coverage remains partial | Genesis compiler; ATLAS-G | COMPLETE: NON-SENSITIVE Strike Force phase; commit `ecca6b9b`; 8 new tests; 3 Phase 1387b tests forward-ported to post-1387c state; compiler result: 32/32 basis-reachable, 0 basis-unreachable, verdict `GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL` |
| 1387d | ADR-0035 formal spec: write `docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md` resolving all three Phase 1387b deferral questions — (1) type regress stopped at hardcoded `type_definition` meta-type floor; (2) ADR-0030 `content_type` tokens are content-layer metadata; ADR-0035 type definitions are graph-structure-layer governance; (3) type-level claims use CDL constitutional amendment path; instance-level claims use standard Popperian evaluation path; definition nodes are non-attributable | ADR lane; homoiconic type governance | COMPLETE: NON-SENSITIVE Strike Force phase; commit `6b88e034`; records `adr_0035_homoiconic_type_definition_system_direction_accepted` and `adr_0035_formal_adr_written_phase_1387d`; 15 new tests; Phase 1387b test updated from "does not exist" to "exists with token"; implementation remains deferred pending a dedicated CDL |
| 1387e | Genesis core star map v0.1 expansion: promote 17 signature-pending v0.2_candidate nodes (ADR-0008/0012/0019/0020/0022/0023/0026/0028/0031/0037, CDL-085, CDL-V1/V2/V3/V7, `policy:edge_mint_phi_bound_0_60`, `policy:reuse_attribution_rate_0_20`) into the active compiler input; add 5 foundational governance spine ADRs (ADR-0001/0002/0003/0005/0006) with 23–32 observed mentions each; add 22 GOVERNS edges (attestation root → each new node); re-run compiler; promoted nodes carry `signature_status: "pending_signing"`, new ADR nodes carry `signature_status: "not_yet_in_manifest"` — future v0.1 signing ceremony required | ATLAS-G; star map governance | COMPLETE: NON-SENSITIVE Strike Force phase; commit `8fbcf6b7`; star map v0.1 expanded 32→54 nodes, 38→77 edges; compiler result: 54/54 basis-reachable, 53/54 authority-traceable (attestation root correctly not self-traceable), verdict `GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL` preserved; 12 new tests; 2 Phase 1387b tests forward-ported (32→54, 31→53); 46 tests passing across 1387b/c/d/e; NON-SENSITIVE: Phase 1340 signing covered `v0.2_candidate` not `v0.1`; expansion does not invalidate any prior signature |
| 1387f | SIM-GRAPHOPT-01: graph structure analysis — add `_graph_structure_analysis()` to compiler; compute BFS authority-trace depth from attestation root (GOVERNS/ATTESTATION only); detect duplicate recipe groups; detect orphan nodes; tally edges missing `decomposition_recipe` by type; result: max depth=2 (hub-and-spoke confirmed), 30 edges missing recipe (17 ATTESTATION + 13 PROVENANCE), 1 duplicate recipe group (GOVERNS/CONSTRAINS merge candidate), 37 orphan leaf nodes | SIM-GRAPHOPT-01; ATLAS-G compiler | COMPLETE: NON-SENSITIVE Strike Force phase; commit `504d46a8`; 12 new tests; 58 tests passing across 1387b–f |
| 1387g | SIM-GRAPHOPT-02: epistemic leverage analysis — add `_epistemic_leverage_analysis()` to compiler; for each non-root node remove it and recompute reachability from attestation root, count other nodes lost; result: 0 keystone nodes, all 39 non-root core nodes leverage=1 (removal isolates only self), 15 axiomatic roots leverage=undefined; hub-and-spoke confirmed maximally resilient | SIM-GRAPHOPT-01; ATLAS-G compiler | COMPLETE: NON-SENSITIVE Strike Force phase; commit `3ed04fed`; 9 new tests; 67 tests passing across 1387b–g |
| 1387h | SIM-GRAPHOPT-03: edge recipe canonicalization — patch all 30 ATTESTATION (17) and PROVENANCE (13) edges with canonical `decomposition_recipe`; ATTESTATION: `assert.truth ∘ link.claim`, scope=`agent_signing_endorsement`; PROVENANCE: `assert.truth ∘ link.claim`, scope=`derivation_origin_chain`; result: 0 of 77 edges missing recipe; second duplicate group surfaces (ATTESTATION/PRIMITIVE_INVOCATION/PROVENANCE — scope-distinguished, valid); GOVERNS/CONSTRAINS remain primary merge candidate | SIM-GRAPHOPT-01; star map canonicalization | COMPLETE: NON-SENSITIVE Strike Force phase; commit `afb46c44`; 11 new tests; 78 tests passing across 1387b–h |
| 1387i | SIM-GRAPHOPT-01 synthesis report — produce `docs/sims/sim_spectral_02/genesis_graphopt_01_synthesis_report_v0.1.md`; document all 1387f/g/h findings; record GOVERNS/CONSTRAINS merge CDL as forward obligation; record ATTESTATION/PROVENANCE scope-distinction as valid (no action required); record 37 orphan leaf nodes as architecturally expected; close SIM-GRAPHOPT-01 series | SIM-GRAPHOPT-01 synthesis | COMPLETE: NON-SENSITIVE Strike Force phase; commit `976ae6e9`; token `sim_graphopt_01_synthesis_complete_phase_1387i`; 9 new tests; 85 tests passing across 1387b–i |
| 1388 | CDL-048 public ECU-to-ILC conversion path activation + counsel clearance: unlock sweeper runtime (first live value-path activation) after Phase 1387 and Phase 1387a pass; simultaneous counsel sign-off on public verifier API surface | CDL-048 activation, Counsel clearance | SENSITIVE; first production value-path activation; blocks Phase 1389 |
| 1389 | **Public claimability/API activation gate** — re-executes Phase 1336 gate with all six blockers confirmed closed plus Phase 1387a accepted-functionality/public-economics proof; `result=public_claimability_activated` is the full public RC milestone | All six Phase 1336 blockers + accepted-functionality coverage | SENSITIVE; explicit `GO Phase 1389` required; fails closed if any predecessor open |
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
    → Phase 1383 CDL-009 fork legitimacy UX  [complete; CLI/operator only]
    → Phase 1384 security review scope  (parallel track; project-authority disposition gate 1387)
    → Phase 1385 TLA+ SafetyNoDualCert disposition  [complete; epoch-checkpoint/shared-object proof deferred with authority]
    → Phase 1386 multi-operator key ceremony
        → Phase 1386a production TLS gRPC proof  [complete]
            → Phase 1386b validator endpoint registry ADR  [complete]
                → Phase 1386c persistent QUIC connectivity proof
                    → Phase 1387 pre-activation hardening gate  (requires project-authority HIGH-finding disposition plus 1386a/1386b/1386c, or explicit defer-with-authority)
                        → Phase 1387a accepted ADR/CDL coverage + public-economics admission firewall
                        → Phase 1387b SIM-GENESIS-COMPILE-02  [complete; NON-SENSITIVE; parallel to main lane]
                            → Phase 1387c compiler basis expansion  [complete; Strike Force]
                                → Phase 1387d ADR-0035 formal spec  [complete; Strike Force]
                                    → Phase 1387e star map v0.1 expansion 32→54 nodes  [complete; Strike Force]
                        → Phase 1388 CDL-048 activation + counsel clearance  (first live value-path; requires GO Phase 1388)
                            → Phase 1389 public claimability activation gate
                                → Phase 1390 closure
```

**Stop conditions for any phase in this window:**
- Identity bootstrap CDL not ratified and a phase creates identity artifacts, seed commitments, mnemonics, private keys, or secret-store writes
- CDL-088 not ratified and a phase activates the public claimability API or claim endpoint
- Replay/nullifier policy not closed and a phase activates a live claim endpoint
- Any phase implies "public claimability is now active" without Phase 1389 producing explicit `result=public_claimability_activated`
- Any phase activates public ECU, reputation, settlement, or claimability paths before
  Phase 1387a proves private/semi-private nodes cannot construct public economic events
  and every accepted ADR/CDL public-RC obligation is either implemented, routed, or
  explicitly deferred outside the public-RC claim

---

### Window 1391-1398 — J-Series Jury / Epoch-Work Canonicalization

**2026-05-19 alignment addendum:** The committed J-series plan now assigns
Phases 1391-1398 to jury / panel / public-node-review / epoch-work
canonicalization. Phase 1391 / J-001 is complete and published
`docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md`. The older Mode-2 refutation
adjudication section below is preserved as scoped carry-forward context for
J-003 public node review taxonomy, J-004 jury incentive economics, and J-008
activation-gate boundary work. It is no longer the primary label for the whole
1391-1398 window.

| J phase | Numeric phase | Current routing |
|---------|---------------|-----------------|
| J-001 | 1391 | COMPLETE: jury / epoch-work canon map; no runtime, CDL, public ingestion, production jury, or reviewer-payment activation. |
| J-002 | 1392 | Jury eligibility, opt-in, randomized assignment, outsider-seat, diversity, and anti-capture ADR. |
| J-003 | 1393 | Public node review taxonomy, including the relationship between objective panels, subjective/aesthetic panels, structural submissions, and refutation/provenance claims. |
| J-004 | 1394 | Jury incentive economics CDL opening; must preserve approval-volume-bias controls and no reviewer-payment activation. |
| J-005 | 1395 | Epoch-start capability and maintenance-work contract. |
| J-006 | 1396 | Default-off jury assignment quote runtime, if still authorized by the J-series sequence. |
| J-007 | 1397 | Shadow public-ingestion jury harness; no public graph permanence or production rewards. |
| J-008 | 1398 | Production jury activation gate definition; reviewer payments and public canonical-node review remain later-gated. |

#### Preserved Mode-2 Refutation Carry-Forward Context

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
| Voice sidecar CDL — authenticated pseudonymous audio relay | New CDL (unopened; no number assigned) | **Recommended v1 stack:** Opus 20ms frames; QUIC streams (already in `ilc_consensus/`); Noise_XX / X25519 ECDH for session key agreement using agent keypairs; ChaCha20-Poly1305 for per-frame authenticated encryption (relay sees opaque ciphertext, not audio); ILC `agent_id` as pseudonymous session auth (no central server, no phone number); CDL-078 L5 relay for IP indirection (1 or 2 hops; relay earns CDL-078 credit). **Explicitly not used:** RTP, SRTP, STUN/TURN, SIP, WebRTC, Signal X3DH. HIGH-001 mixing is incompatible (deliberate delay destroys voice); the relay hop is IP indirection only, not mixing anonymity. Audio traffic type in CDL-078 may require CDL amendment or sibling CDL. Full research note: `docs/research/ilc_voice_sidecar_pseudonymous_audio_relay_v0.1.md`. | Prerequisites: Public RC (Phase 1389), CDL-078 L5 relay live in production, sidecar manifest/SDK stable, ADR-0038/CDL-090 identity bootstrap live, HIGH-001 landed. Phase assignment Window 1399+. |

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
1343. Phase 1391 / J-001 later executed as a non-sensitive planning-only direct
GO exception; it did not open the remainder of Window 1391-1398. Later windows
otherwise remain closed until their own sequence-lock phases execute.

```text
forward_phase_windows_post_1342_three_window_structure_finalized_2026_05_14
window_1343_1368_soft_rc_gate_phase_1366
window_1369_1390_public_claimability_gate_phase_1389
window_1391_1398_mode_2_refutation_adjudication_and_settlement
window_1391_1398_jury_epoch_work_canonicalization
window_1391_1398_mode_2_refutation_scope_preserved_inside_j_series
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
| Legacy `/v1/public/*` FastAPI routes not cleaned up | CLOSED in Phase 1378 (`legacy_public_labeled_fastapi_routes_cleaned_phase_1378`) |
| Counsel clearance for public verifier API surface | Provisional only; CDL-086 C1–C5 instruments pending |

The FastAPI route cleanup (Phase 1378) is complete. Remaining pre-Phase-1389
blockers include counsel clearance for the public verifier API surface,
Phase 1387/1387a hardening and accepted ADR/CDL/public-economics coverage,
implementation or registry evidence for replay/nullifier and duplicate-claim
enforcement, and the explicit Phase 1389 activation gate. Phase 1378 does not
authorize public claimability, public endpoint activation, value-path
activation, public RC publication, or public launch.

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
