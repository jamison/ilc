# ILC Claimability Package Allowlist Rehearsal 1294 v0.1

**Phase:** 1294
**Date:** 2026-05-10
**Status:** allowlist rehearsal recorded; package-profile CI pass preserved; source export, package publication, public claimability activation, and public-RC claim remain blocked
**Window lock:** `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`

```text
claimability_package_allowlist_rehearsal_phase_1294.v0.1
claimability_package_allowlist_verdict_phase_1294=rehearsal_pass_export_blocked
openclaw_skill_claimable_allowlist_rehearsed_phase_1294
public_rc_exclude_helpers_excluded_from_export_phase_1294
claimability_package_manifest_not_materialized_phase_1294
source_allowlist_export_not_executed_phase_1294
public_repository_publication_not_authorized_phase_1294
public_package_publication_not_authorized_phase_1294
public_claimability_activation_not_authorized_phase_1294
public_rc_remains_blocked_after_phase_1294
phase_1295_transport_principal_lifecycle_revocation_replay_preflight_next
```

## 1. Verdict

Phase 1294 rehearses the claimability package allowlist decision after Phase
1293 closed the helper register as keep-internal/no-promotion. The deterministic
package-profile CI gate still passes for the selected OpenClaw/NemoClaw local
and claimable profiles, but that pass is not export or publication authority.
This packet is governed by the active 1289-1302 sequence lock.

```text
claimability_package_allowlist_verdict_phase_1294=rehearsal_pass_export_blocked
```

The important boundary is sharper after Phase 1294: the raw measured
`openclaw_skill_claimable` profile is not directly exportable as a public source
package because the measured `ilc_logic` surface still includes
`ilc_core/graph/sidecar_public_path_preflight.py`, which carries
`PUBLIC_RC_EXCLUDE`. A future public export must either remove that file from
the exported profile, replace it with a public-safe module, or receive a later
explicit promotion authority. Phase 1294 grants none of those.
The raw measured `openclaw_skill_claimable` profile is not directly exportable
without that later exclusion, replacement, or promotion decision.

Phase 1294 does not materialize an export manifest, export source, publish a
repository, publish a package, activate public claimability, activate a public
verifier service, produce release artifacts, generate release keys, produce
release envelopes, mutate Genesis, sign v0.2, mutate the CDL register, open
CDL-088, authorize wallet withdrawal/transfer/spend, authorize ECU minting, or
authorize ILC settlement.

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Verified the active Phase 1294 authority against `docs/PLANNING_INDEX.md`, Capsule v5.52, STATUS, the 1289-1302 lock/guidance, Phase 1255 allowlist procedure, Phase 1279 prepublication inventory, Phase 1292 package-profile rehearsal, Phase 1293 helper register, and package-profile CI code. |
| Section 0b Concept-discovery search | Searched claimability package, package allowlist, source allowlist, `openclaw_skill_claimable`, `public_claimability`, package profile, source export, public repository, public package, `PUBLIC_RC_EXCLUDE`, release artifact, and helper promotion/removal terms. |
| Section 0c Contradiction and non-claim search | Searched blocked, not authorized, not enabled, not executed, no source export, no package publication, no public verifier, no public claimability, no release, no keys, no signing, no wallet spend, no ECU minting, no ILC settlement, and public RC remains blocked. |
| Section 0d Source expansion and newly discovered tokens | Source expansion confirmed that `openclaw_skill_claimable` is a target package profile with `public_claimability_declared=True` and `public_claimability_runtime_activated=False`. It also confirmed that the measured `ilc_logic` surface includes the sidecar public-path preflight helper, so any future materialized export must exclude, replace, or explicitly promote that helper before publication. |

Direct-read basis:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md`
- `docs/specs/ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md`
- `docs/specs/ilc_public_rc_exclude_helper_promotion_removal_register_1293_v0.1.md`
- `ilc_core/rc/package_profiles.py`
- `ilc_core/rc/package_profile_ci_gate.py`
- `ilc_core/rc/package_boundary_inventory.py`

## 3. Package-Profile Snapshot

Package-profile CI remains a measurement gate only in Phase 1294.

The current package-profile audit still reports `audit_status=pass`.

| Profile | Status | Files | Bytes | Lines | Public claimability declared | Runtime activated | Public package published | Public RC claimed |
|---------|--------|------:|------:|------:|------------------------------|-------------------|--------------------------|------------------|
| `openclaw_skill_local` | `pass` | 94 | 707967 | 20028 | `False` | `False` | `False` | `False` |
| `openclaw_skill_claimable` | `pass` | 97 | 732163 | 20698 | `True` | `False` | `False` | `False` |

Surface snapshot for `openclaw_skill_claimable`:

| Surface | Boundary status | Files | Phase 1294 allowlist rehearsal disposition |
|---------|-----------------|------:|--------------------------------------------|
| `ilc_logic` | `pass` | 62 | Candidate package surface for measurement only; not exportable as a root without removing or replacing `PUBLIC_RC_EXCLUDE` material. |
| `ilc_cli` | `pass` | 25 | Candidate package surface after future CLI/license/secret review. |
| `ilc_harness_adapters` | `pass` | 7 | Candidate package surface after future public harness review. |
| `local_sidecar` | `measurement_only` | 2 | Candidate local preview surface only; no public sidecar serving. |
| `public_claimability` | `measurement_only` | 6 | Candidate-hold surface until public claimability verifier/API authority, disclosure, replay/nullifier, and duplicate-claim gates close. |

## 4. Allowlist Rehearsal Matrix

Phase 1294 does not produce a materialized export tree. It rehearses how the
Phase 1255 allowlist procedure would classify current claimability-package
surfaces if a later dry run were authorized.

| Class | Rehearsal disposition | Reason |
|-------|-----------------------|--------|
| Selected package-profile source surfaces | `candidate_include_after_review` | The package-profile CI gate passes, but publication still requires a future manifest, license review, secret scan, and explicit export authorization. |
| `public_claimability` surface files | `candidate_hold` | These files are package target inputs only; public claimability runtime and public verifier/API authority remain blocked. |
| Files carrying `PUBLIC_RC_EXCLUDE` | `exclude` | Phase 1255 deny rule and Phase 1293 helper register require exclusion unless a later explicit review removes or supersedes the marker. |
| `docs/antigravity_tasks/` and `docs/phases/` | `exclude_by_default` | Private execution records and prompt history are not public package payload by default. |
| `docs/research/patent_pending/` and patent/publication-sensitive drafts | `exclude_or_counsel_review` | Phase 1300/IP lane and counsel review must decide before disclosure. |
| `out/`, local monitoring, generated diagnostics, caches, and scratch outputs | `exclude_by_default` | Generated local outputs are not source package payload by default. |
| Release manifests, release keys, release envelopes, and signing ceremony material | `exclude_until_independent_authority` | Release and signing gates remain separate and blocked. |
| Selected tests and tools | `review_required` | Future export must remove private phase-history assertions, private-path assumptions, secrets, and internal-only harness assumptions. |

## 5. Claimability File Dispositions

The six files in the measured `public_claimability` surface are package-surface
candidates only. They are not public activation authority.

| Path | Phase 1294 disposition |
|------|------------------------|
| `ilc_core/ledger/ecu_active_layer_runtime.py` | `candidate_hold_no_public_claimability_activation` |
| `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py` | `candidate_hold_no_wallet_spend_or_settlement_activation` |
| `ilc_core/ledger/exact_numeric.py` | `candidate_include_after_license_and_boundary_review` |
| `ilc_core/protocol/public_init_admission_runtime.py` | `candidate_hold_no_public_endpoint_activation` |
| `ilc_core/protocol/public_receipt_runtime.py` | `candidate_hold_no_public_verifier_service_activation` |
| `ilc_core/protocol/public_wallet_runtime.py` | `candidate_hold_no_wallet_withdrawal_transfer_spend_activation` |

These `PUBLIC_RC_EXCLUDE` helper files are denied by default:

| Path | Phase 1294 disposition |
|------|------------------------|
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | `exclude_by_public_rc_exclude_marker` |
| `ilc_core/ledger/claimability_proof_binding_runtime.py` | `exclude_by_public_rc_exclude_marker` |
| `ilc_core/network/d2d/transport_principal_public_path_preflight.py` | `exclude_by_public_rc_exclude_marker` |
| `ilc_core/graph/sidecar_public_path_preflight.py` | `exclude_by_public_rc_exclude_marker` |

The sidecar helper is the material package-surface finding for Phase 1294: it
appears inside the measured `ilc_logic` surface, so the raw profile root is a
measurement input, not a publishable allowlist root.

## 6. Future Manifest Contract

A later authorized dry run may construct a manifest, but Phase 1294 does not.
If a future manifest is machine-verifiable JSON, it must use deterministic
serialization:

```text
json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))
```

Required future fields:

| Field | Rule |
|-------|------|
| `schema_version` | Use `ilc_claimability_package_allowlist_manifest.v0.1` or a later ratified successor. |
| `source_commit` | Full source commit hash selected for the future dry run. |
| `capsule` | Current capsule path/version at the future freeze point. |
| `mode` | `dry_run` by default; `authorized_publication` only with later explicit authority. |
| `profile_id` | Candidate profile, expected to be `openclaw_skill_claimable` for the claimable package path. |
| `include_rules` | Ordered repo-relative include selectors. |
| `exclude_rules` | Ordered deny selectors; deny wins over include. |
| `review_required` | Counsel, patent, trademark, Genesis, package, test, and tool review routes. |
| `file_hashes` | Full SHA-256 hashes after future materialization. |
| `non_claims` | Explicit statement that dry-run evidence is not publication, release, or public-RC authority. |

## 7. Carry-Forward

Phase 1294 closes the allowlist rehearsal as a classification pass only. It
does not execute export. Public RC remains blocked by:

- final public claimability verifier/API authority and public endpoint
  authorization;
- public-safe helper replacement or later explicit helper promotion
  prerequisites;
- public-safe disclosure schema, privacy filtering, replay/nullifier policy,
  and duplicate-claim registry;
- actual TransportPrincipal public-path activation authority;
- actual sidecar public projection serving authority;
- counsel/license/CLA/trademark/IP/publication clearance;
- source allowlist export execution and public source/package publication;
- release artifact production, release-key generation, release envelope
  production, and release manifest instance production;
- Genesis Atlas mutation/regeneration/signing if needed and v0.2 signing
  authorization;
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy;
- wallet withdrawal/transfer/spend semantics, wallet signing authority,
  wallet ledger-write authority, ECU minting, ILC settlement, and withdrawal
  runtime activation.

The next locked phase remains sensitive:

```text
phase_1295_transport_principal_lifecycle_revocation_replay_preflight_next
```

## 8. Non-Claims

```text
claimability_package_manifest_not_materialized_phase_1294
source_allowlist_export_not_executed_phase_1294
public_repository_publication_not_authorized_phase_1294
public_package_publication_not_authorized_phase_1294
public_claimability_activation_not_authorized_phase_1294
public_rc_remains_blocked_after_phase_1294
```

Phase 1294 does not authorize:

- materialized export manifest production;
- source allowlist export execution;
- public repository publication;
- public package publication;
- public release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- public launch claim;
- helper promotion;
- `PUBLIC_RC_EXCLUDE` marker removal;
- public claimability runtime activation;
- public claimability API activation;
- public verifier service;
- public claim endpoint;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback bind, wildcard bind, public host bind, listener, or peer discovery;
- wallet withdrawal, wallet transfer, or wallet spend;
- wallet signing authority or wallet ledger-write authority;
- ECU minting;
- ILC settlement or withdrawal runtime activation;
- CDL mutation;
- CDL-088 opening;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- IP filing or paper publication.

## 9. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_claimability_package_allowlist_rehearsal_1294_v0.1.md -> package/public_rc
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1294_g8_sidecar_public_safe_projection_schema_preflight.md -> planning/prompts
graph_delta=support_tests_added:tests/test_phase_1294_claimability_package_allowlist_rehearsal.py -> validation
graph_delta=support_only:docs/phases/phase_1294_claimability_package_allowlist_rehearsal_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
