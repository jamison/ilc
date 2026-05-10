# ILC PUBLIC_RC_EXCLUDE Helper Promotion/Removal Register 1293 v0.1

**Phase:** 1293
**Date:** 2026-05-10
**Status:** helper register recorded; all current public-RC-excluded runtime helpers kept internal; no promotion, marker removal, source export, package publication, or public-RC claim
**Window lock:** `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`

```text
public_rc_exclude_helper_promotion_removal_register_phase_1293.v0.1
public_rc_exclude_helpers_keep_internal_phase_1293
public_rc_exclude_helper_promotion_not_authorized_phase_1293
public_rc_exclude_helper_removal_not_authorized_phase_1293
public_rc_exclude_helper_replacement_required_before_public_export_phase_1293
source_allowlist_export_not_executed_phase_1293
public_package_publication_not_authorized_phase_1293
public_rc_remains_blocked_after_phase_1293
phase_1294_claimability_package_allowlist_rehearsal_next
```

## 1. Verdict

Phase 1293 closes the immediate helper-triage question opened by Phase 1292:
every current runtime helper marked `PUBLIC_RC_EXCLUDE` remains internal by
default. No helper is promoted, no marker is removed, and no source/package
export is executed.

```text
public_rc_exclude_helper_register_verdict_phase_1293=all_current_helpers_keep_internal_no_promotion
```

This is a register-only decision. It does not activate public claimability,
public verifier/API serving, public P2P, public fetch serving, public
sidecar/projection serving, wallet withdrawal, wallet transfer, wallet spend,
ECU minting, ILC settlement, Genesis mutation/signing, v0.2 signing, CDL-088,
source publication, package publication, release artifacts, release keys, or
release envelopes.

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Verified the active Phase 1293 authority against `docs/PLANNING_INDEX.md`, Capsule v5.52, STATUS, the 1289-1302 sequence lock, active 1289-1302 guidance, Phase 1292 packet, and the four helper headers. The active lock supersedes the earlier 1289-1296 draft prompt scope. |
| Section 0b Concept-discovery search | Searched `PUBLIC_RC_EXCLUDE`, helper promotion, marker removal, source allowlist, public package, public repository, release artifact, claimability, TransportPrincipal, sidecar public path, public path, publication, and package-profile terms. |
| Section 0c Contradiction and non-claim search | Searched blocked, not authorized, not enabled, no public, no listener, no publication, no release, no source export, local-only, public RC remains blocked, and marker-removal terms. No canon source grants helper promotion, marker removal, publication, or activation authority. |
| Section 0d Source expansion and newly discovered tokens | Found one stale historical surface: the Phase 1288 Fix2 prompt file for candidate 1289-1296 still used the old Phase 1293 TransportPrincipal scope. The active 1289-1302 lock and Capsule v5.52 control; this phase updates the Phase 1293 prompt body to the helper-register scope while preserving the superseded historical guidance as historical context. |

Direct-read basis:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md`
- `docs/specs/ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md`
- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`
- `ilc_core/ledger/claimability_proof_binding_runtime.py`
- `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
- `ilc_core/graph/sidecar_public_path_preflight.py`

## 3. Helper Register

| Helper | Register decision | Marker status | Public-export disposition | Required future route |
|--------|-------------------|---------------|---------------------------|-----------------------|
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | `keep_internal` | Retain `PUBLIC_RC_EXCLUDE` | Excluded from public source/package/release export by default. | Replace or promote only after public claimability authority, verifier/API hardening, replay/nullifier policy, duplicate-claim registry, field-disclosure review, and release allowlist review. |
| `ilc_core/ledger/claimability_proof_binding_runtime.py` | `keep_internal` | Retain `PUBLIC_RC_EXCLUDE` | Excluded from public source/package/release export by default. | Replace or promote only after public claimability verifier/API authority, public-safe disclosure schema, replay/nullifier policy, duplicate-claim registry, and release allowlist review. |
| `ilc_core/network/d2d/transport_principal_public_path_preflight.py` | `keep_internal` | Retain `PUBLIC_RC_EXCLUDE` | Excluded from public source/package/release export by default. | Replace or promote only after TransportPrincipal public-path authority, lifecycle/revocation/replay closure, hostile-network admission/ban/rate/privacy closure, and release allowlist review. |
| `ilc_core/graph/sidecar_public_path_preflight.py` | `keep_internal` | Retain `PUBLIC_RC_EXCLUDE` | Excluded from public source/package/release export by default. | Replace or promote only after sidecar public-safe projection schema, TransportPrincipal authority, bind/listener/peer-discovery authority, privacy review, and release allowlist review. |

No `remove` decision is made because each helper still guards an unresolved
public-RC blocker. No `promote` decision is made because each helper remains
either a local proof scaffold or an internal public-path preflight scaffold.
No `replace_with_public_safe_module` decision is executed because the required
public-safe verifier, disclosure, transport, sidecar, and release authorities
are not yet closed.

## 4. Header Evidence

Each registered helper carries the internal launch-surface exclusion marker:

```text
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

Header reasons:

| Helper | Header reason |
|--------|---------------|
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | Phase 1274 CDL-048 conversion-sweeper skeleton; local verifier scaffold only. |
| `ilc_core/ledger/claimability_proof_binding_runtime.py` | Local Phase 1275 proof-binding scaffold only. |
| `ilc_core/network/d2d/transport_principal_public_path_preflight.py` | Phase 1277 public-path preflight scaffold; no listener or public transport activation. |
| `ilc_core/graph/sidecar_public_path_preflight.py` | Phase 1278 sidecar public-path preflight scaffold; no listener, bind, or serving surface. |

Phase 1293 does not edit these helper headers. The existing markers remain the
machine-visible default for later source allowlist, package, and release gates.

## 5. Allowlist Disposition

Phase 1255 still controls the default source-export rule: any source, test,
tool, or doc carrying `PUBLIC_RC_EXCLUDE` is excluded unless a later explicit
allowlist review removes or supersedes the marker.

Phase 1293 does not execute the Phase 1255 allowlist export procedure. It only
records the helper register needed before a later allowlist rehearsal or
materialized export can be considered.

```text
source_allowlist_export_not_executed_phase_1293
public_package_publication_not_authorized_phase_1293
```

## 6. Non-Register Exclusions

This register focuses on the four current runtime helper files carried forward
from Phase 1292. Other `PUBLIC_RC_EXCLUDE` material remains governed by its
own lane:

| Material | Current route |
|----------|---------------|
| IP/patent/publication-sensitive research docs | Phase 1280 Fix1 and future Phase 1300 counsel/IP/publication clearance inventory. |
| `docs/antigravity_tasks/`, `docs/phases/`, raw chats, `out/`, local monitoring, and private context material | Phase 1255 public-source allowlist export procedure exclusions. |
| Superseded prompt drafts from Window 1289-1296 | Historical planning context only; not active source-publication authority. |

Phase 1293 does not remove or supersede any non-runtime `PUBLIC_RC_EXCLUDE`
boundary.

## 7. Carry-Forward Blockers

Public RC remains blocked after Phase 1293 by:

- Final public claimability verifier/API authority and public endpoint
  authorization.
- Public-safe disclosure schema, privacy filtering, replay/nullifier policy,
  and duplicate-claim registry.
- Actual TransportPrincipal public-path activation authority, lifecycle,
  revocation, replay, admission, ban, rate-limit, and privacy controls.
- Actual public sidecar/projection serving authority, public-safe field schema,
  bind/listener policy, and peer-discovery policy.
- Counsel/license/CLA/trademark/IP/publication clearance.
- Source allowlist export execution and public source/package publication.
- Release artifact production, release-key generation, release envelope
  production, and release manifest instance production.
- Genesis Atlas mutation/regeneration/signing if needed and v0.2 signing
  authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- Wallet withdrawal/transfer/spend semantics, wallet signing authority,
  wallet ledger-write authority, ECU minting, ILC settlement, and withdrawal
  runtime activation.

The next locked phase remains sensitive:

```text
phase_1294_claimability_package_allowlist_rehearsal_next
```

## 8. Non-Claims

Phase 1293 does not authorize:

- helper promotion;
- `PUBLIC_RC_EXCLUDE` marker removal;
- source allowlist export execution;
- public repository publication;
- public package publication;
- release artifact production;
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

## 9. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_public_rc_exclude_helper_promotion_removal_register_1293_v0.1.md -> package/public_rc
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1293_g8_transport_principal_lifecycle_activation_blocker_preflight.md -> planning/prompts
graph_delta=support_tests_added:tests/test_phase_1293_public_rc_exclude_helper_register.py -> validation
graph_delta=support_only:docs/phases/phase_1293_public_rc_exclude_helper_register_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
