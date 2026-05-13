# ILC Forward Phase Windows 1303-1342 Packaging and Signing Plan v0.1

**Status:** Planning-only candidate guidance.
**Recorded:** 2026-05-10.
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
is not a first-public-RC blocker by default. Its detailed routing is recorded in
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

Phase 1341 must not imply a public confidential messaging or coordination
product unless Phase 1337 explicitly selected and passed that scope.

Phase 1341 must also not imply that public OpenClaw/NemoClaw users, digital
agents, or local ILC identities are Genesis-rooted unless a prior identity
bootstrap ADR/CDL or equivalent spec has defined and rehearsed the required
agent birth attestation or equivalent Genesis-rooted identity-origin proof.

## 5. Non-Claims

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
