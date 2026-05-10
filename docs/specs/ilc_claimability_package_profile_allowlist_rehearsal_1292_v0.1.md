# ILC Claimability Package Profile Allowlist Rehearsal 1292 v0.1

**Phase:** 1292
**Date:** 2026-05-10
**Status:** verifier negative-path corpus recorded; package-profile boundary rehearsed; no source export, package publication, or public-RC claim
**Window lock:** `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`

```text
claimability_package_profile_allowlist_rehearsal_phase_1292.v0.1
source_allowlist_export_not_executed_phase_1292
public_package_publication_not_authorized_phase_1292
public_rc_exclude_helpers_preserved_phase_1292
public_rc_remains_blocked_after_phase_1292
verifier_negative_path_corpus_recorded_phase_1292
claimability_package_profile_boundary_verdict_phase_1292=pass_import_boundary_publication_blocked
ilc_logic_network_import_boundary_repaired_phase_1292
package_profile_ci_artifacts_refreshed_phase_1292
phase_1293_public_rc_exclude_helper_promotion_removal_register_next
```

## 1. Verdict

Phase 1292 reconciles two naming surfaces. The active Window 1289-1302 lock
names this scope as verifier negative-path corpus and package-profile boundary,
while the original prompt draft named the package-profile allowlist rehearsal.
Both are addressed here.

The current package-profile CI gate now passes after a narrow import-boundary
repair, but that pass is not publication authority:

```text
claimability_package_profile_boundary_verdict_phase_1292=pass_import_boundary_publication_blocked
```

No source allowlist export was executed. No public repository or package was
published. No release artifact, release key, release envelope, Genesis mutation,
Genesis signing, v0.2 signing, public verifier service, public claimability API,
wallet withdrawal, wallet transfer, wallet spend, ECU minting, or ILC settlement
was authorized or performed.

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Required Phase 1292 tokens are now recorded in this packet, prompt, tests, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.52, and Roadmap v1.1. |
| Section 0b Concept-discovery search | Direct searches covered package profile, allowlist, source export, `PUBLIC_RC_EXCLUDE`, `openclaw_skill_claimable`, release manifest, release artifact, publication, public package, public repository, verifier negative paths, replay, nullifier, duplicate claim, and claimability activation. |
| Section 0c Contradiction and non-claim search | Direct searches covered not authorized, not executed, not produced, blocked, deferred, no publication, no release, no artifact, no signing, public RC remains blocked, public API not enabled, and helper exclusion terms. |
| Section 0d Source expansion and newly discovered tokens | Source expansion found one live package-boundary regression: `ilc_core/graph/sidecar_public_path_preflight.py` imported `ilc_core.network.d2d.transport_principal_public_path_preflight`, violating the `ilc_logic` import boundary. Phase 1292 repairs that import edge and records `ilc_logic_network_import_boundary_repaired_phase_1292`. |

Direct-read basis:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md`
- `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
- `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md`
- `docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md`
- `ilc_core/rc/package_profiles.py`
- `ilc_core/rc/package_profile_ci_gate.py`
- `ilc_core/rc/package_boundary_inventory.py`
- `ilc_core/graph/sidecar_public_path_preflight.py`

## 3. Package-Profile Boundary Rehearsal

The current deterministic package-profile audit reports `audit_status=pass`.
That means the measured package roots pass import-boundary checks and size/hash
measurement constraints. It does not mean public export or publication is
authorized.

| Profile | Status | Files | Bytes | Lines | Public claimability declared | Runtime activated | Public package published | Public RC claimed |
|---------|--------|------:|------:|------:|------------------------------|-------------------|--------------------------|------------------|
| `openclaw_skill_local` | `pass` | 94 | 707967 | 20028 | `False` | `False` | `False` | `False` |
| `openclaw_skill_claimable` | `pass` | 97 | 732163 | 20698 | `True` | `False` | `False` | `False` |

Surface measurements after the Phase 1292 import-boundary repair:

| Profile | Surface | Boundary status | Files | Bytes | Lines |
|---------|---------|-----------------|------:|------:|------:|
| `openclaw_skill_local` | `ilc_cli` | `pass` | 25 | 174260 | 5131 |
| `openclaw_skill_local` | `ilc_harness_adapters` | `pass` | 7 | 136584 | 3534 |
| `openclaw_skill_local` | `ilc_logic` | `pass` | 62 | 397123 | 11363 |
| `openclaw_skill_local` | `local_sidecar` | `measurement_only` | 2 | 36388 | 1069 |
| `openclaw_skill_claimable` | `ilc_cli` | `pass` | 25 | 174260 | 5131 |
| `openclaw_skill_claimable` | `ilc_harness_adapters` | `pass` | 7 | 136584 | 3534 |
| `openclaw_skill_claimable` | `ilc_logic` | `pass` | 62 | 397123 | 11363 |
| `openclaw_skill_claimable` | `local_sidecar` | `measurement_only` | 2 | 36388 | 1069 |
| `openclaw_skill_claimable` | `public_claimability` | `measurement_only` | 6 | 46139 | 1233 |

The important safety distinction is:

- `public_claimability_declared=True` for `openclaw_skill_claimable` is a
  package-profile target declaration.
- `public_claimability_runtime_activated=False` remains mandatory.
- `package_publication=False`, `public_repository_publication=False`, and
  `public_rc_claimed=False` remain mandatory.
- Package-profile CI pass is not source-publication authorization.
- Package-profile CI pass is not release artifact authorization.

## 4. Import-Boundary Repair

The package rehearsal first produced a fail-closed result because the pure
`ilc_logic` boundary detected this forbidden import:

```text
ilc_core/graph/sidecar_public_path_preflight.py
ilc_core.network.d2d.transport_principal_public_path_preflight
matched_rule=ilc_core.network
```

Phase 1292 repairs the edge by keeping `ilc_core/graph` independent of
`ilc_core.network`. The sidecar helper now validates the required
TransportPrincipal public-path preflight shape and hash locally before binding
the sidecar preflight reference.

This repair is a package-boundary correction only. The sidecar helper remains
header-marked `PUBLIC_RC_EXCLUDE` and remains an internal helper, not a public
RC launch surface.

The deterministic package audit artifacts were refreshed from the current
passing audit:

- `docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json`
- `docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md`

## 5. Verifier Negative-Path Corpus

Phase 1292 records the future negative-path corpus that any public
claimability verifier must deny before activation authority can be considered.
This corpus is not a public verifier implementation.

| ID | Negative path | Required disposition |
|----|---------------|----------------------|
| `NP-1292-001` | Any activation flag is `true`, including `public_claimability_activated`, `non_loopback_claimability_api_enabled`, `wallet_withdrawal_enabled`, `wallet_transfer_enabled`, `wallet_spend_enabled`, `ecu_mint_authorized`, or `ilc_settlement_authorized`. | Deny and fail closed. |
| `NP-1292-002` | Forged conversion receipt SHA-256 or conversion key SHA-256. | Deny and fail closed. |
| `NP-1292-003` | Wrong root namespace, including wallet root supplied as settled runtime root or settled root supplied as wallet root. | Deny and fail closed. |
| `NP-1292-004` | Stale or mismatched settled runtime root relative to conversion epoch. | Deny and fail closed. |
| `NP-1292-005` | Wallet-state root mismatch or missing wallet-state root. | Deny and fail closed. |
| `NP-1292-006` | Latest balance receipt ref mismatch, missing receipt, non-finite Decimal string, negative balance, or non-applied settlement status. | Deny and fail closed. |
| `NP-1292-007` | History digest mismatch or malformed digest. | Deny and fail closed. |
| `NP-1292-008` | Conversion key replay or duplicate converted lot. | Deny and fail closed. |
| `NP-1292-009` | Missing replay/nullifier policy or missing duplicate-claim registry. | Deny and keep public activation blocked. |
| `NP-1292-010` | CDL-048 conversion deadline violation. | Deny and fail closed. |
| `NP-1292-011` | Python float, `NaN`, `Infinity`, `-Infinity`, malformed Decimal, or mixed exact-numeric boundary. | Deny and fail closed before arithmetic. |
| `NP-1292-012` | non-string JSON keys, non-string keys, recursive cycles, excessive traversal depth, or excessive traversal node count in canonical payloads. | Deny and fail closed before hashing/export. |
| `NP-1292-013` | Full Phase 1275 proof-binding payload treated as public-safe before a field-level disclosure schema is ratified. | Deny public exposure and keep API blocked. |
| `NP-1292-014` | Any helper marked `PUBLIC_RC_EXCLUDE` included in a public source/package/release export without later explicit review. | Deny export and keep publication blocked. |
| `NP-1292-015` | Package-profile CI import boundary fails or package audit artifacts do not match the deterministic builder. | Deny publication and keep public RC blocked. |

## 6. Helper Exclusion Table

These helpers remain excluded from public RC by default:

| Path | Current disposition | Future action |
|------|---------------------|---------------|
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | `PUBLIC_RC_EXCLUDE`; local conversion-sweeper helper. | Phase 1293 must keep, remove, replace, or promote by explicit register entry. |
| `ilc_core/ledger/claimability_proof_binding_runtime.py` | `PUBLIC_RC_EXCLUDE`; local proof-binding helper. | Phase 1293 must keep, remove, replace, or promote by explicit register entry. |
| `ilc_core/network/d2d/transport_principal_public_path_preflight.py` | `PUBLIC_RC_EXCLUDE`; internal public-path preflight helper. | Phase 1293 must keep, remove, replace, or promote by explicit register entry. |
| `ilc_core/graph/sidecar_public_path_preflight.py` | `PUBLIC_RC_EXCLUDE`; internal sidecar public-path preflight helper. | Phase 1293 must keep, remove, replace, or promote by explicit register entry. |

The current package-profile measurement roots may include internal helper files
for import-boundary accounting. That accounting is not public-source allowlist
execution. A future public export must still apply the Phase 1255 exclusion
rule: files carrying `PUBLIC_RC_EXCLUDE` are excluded unless a later explicit
allowlist review removes or supersedes the marker.

## 7. Allowlist Rehearsal Disposition

The Phase 1255 default exclusions remain active:

- `docs/antigravity_tasks/`
- `docs/phases/`
- `docs/research/patent_pending/`
- unpublished paper drafts and patent-sensitive research
- raw chats, memory corpora, local context packs, and private transcript derivatives
- `out/`
- local monitoring snapshots, generated diagnostics, caches, and scratch output
- `.env*`, private keys, TLS keys, release keys, local certificates, `.venv/`, editor state, and OS metadata
- any source, test, tool, or doc carrying `PUBLIC_RC_EXCLUDE`
- unsigned release envelopes, draft release manifests, signing ceremony material, and claimability artifacts until their independent gates close

No materialized export tree, manifest hash, clean public repository, package,
release artifact, release key, or release envelope is produced by Phase 1292.

## 8. Non-Claims

```text
source_allowlist_export_not_executed_phase_1292
public_package_publication_not_authorized_phase_1292
public_rc_exclude_helpers_preserved_phase_1292
public_rc_remains_blocked_after_phase_1292
```

Phase 1292 does not authorize:

- source allowlist export execution;
- public repository publication;
- public package publication;
- public release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- public launch claim;
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

## 9. Carry-Forward

Phase 1293 is the next locked sensitive gate:

```text
phase_1293_public_rc_exclude_helper_promotion_removal_register_next
```

Phase 1293 must produce an explicit helper promotion/removal register before
any future public source/package/release export can be considered. The register
must classify each `PUBLIC_RC_EXCLUDE` helper as keep-internal, remove,
replace-with-public-safe module, or promote after explicit public-RC review.

Public RC remains blocked after Phase 1292 by final public claimability
verifier/API authority, public-safe disclosure schema, replay/nullifier and
duplicate-claim registry, TransportPrincipal public-path activation authority,
sidecar public projection serving authority, counsel/IP/publication clearance,
source allowlist export execution, release artifact/key/envelope production,
Genesis/v0.2 signing authority, wallet/ECU/ILC activation, and CDL-088.

## 10. Graph Delta

```text
graph_delta=load_bearing_code_changed:ilc_core/graph/sidecar_public_path_preflight.py -> sidecar/public_path/import_boundary
graph_delta=support_artifact_changed:docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json -> package/public_rc
graph_delta=support_artifact_changed:docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md -> package/public_rc
graph_delta=support_only:docs/specs/ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md -> package/public_rc
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1292_g8_claimability_package_profile_allowlist_rehearsal.md -> planning/prompts
graph_delta=support_tests_added:tests/test_phase_1292_claimability_package_profile_allowlist_rehearsal.py -> validation
graph_delta=support_only:docs/phases/phase_1292_claimability_package_profile_allowlist_rehearsal_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

## 11. Verification

Planned verification:

```text
.venv/bin/python -m pytest tests/test_phase_1292_claimability_package_profile_allowlist_rehearsal.py tests/test_phase_1278_sidecar_non_loopback_public_path_preflight.py tests/test_phase_1250_gap14_adapter_extraction.py tests/test_phase_1251_gap14_package_ci_gate.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- ilc_core/graph/sidecar_public_path_preflight.py docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md docs/specs/ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md docs/antigravity_tasks/antigravity_prompt__phase_1292_g8_claimability_package_profile_allowlist_rehearsal.md docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/phases/phase_1292_claimability_package_profile_allowlist_rehearsal_walkthrough.md docs/specs/ilc_antigravity_context_capsule_v5.52.md docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md tests/test_phase_1292_claimability_package_profile_allowlist_rehearsal.py
```
