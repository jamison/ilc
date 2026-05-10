# ILC Antigravity Context Capsule v5.52

**Date:** 2026-05-10
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
**Produced:** Phase 1290, Window 1289-1302; updated by Phase 1291
**Frontier:** Window 1289-1302 is open through Phase 1291. Phase 1291 is a
sensitive contract preflight only. Phase 1292 is the next sensitive gate and
requires explicit `GO Phase 1292`.

```text
context_capsule_v5_52_frontier_refresh_phase_1290.v0.1
capsule_v5_52_supersedes_v5_51
window_1289_1302_sequence_lock_reflected_in_capsule_phase_1290
window_1289_1302_open_through_phase_1290
window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289
phase_1291_public_claimability_verifier_contract_preflight_requires_explicit_go
public_rc_blocker_map_refreshed_phase_1290
public_rc_remains_blocked_after_phase_1290
phase_1290_non_sensitive_docs_canon_refresh_no_activation
public_claimability_verifier_contract_preflight_phase_1291.v0.1
public_claimability_activation_not_authorized_by_default_phase_1291
claimability_verifier_public_api_not_enabled_phase_1291
wallet_withdrawal_transfer_spend_still_blocked_phase_1291
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
claimability_contract_no_runtime_helper_added_phase_1291
phase_1292_verifier_negative_path_corpus_package_boundary_next
public_rc_remains_blocked_after_phase_1291
```

---

## 1. Current State

Window 1273-1280 is closed with a pass verdict. Window 1281-1288 is closed
with a pass verdict through Phase 1288. Phase 1288 Fix1 runtime deep audit
hardening is complete. Phase 1288 Fix2 drafted the narrower Window 1289-1296
prompt package, and Phase 1289 superseded that draft by opening the active
Window 1289-1302 sequence lock.

Current active sequence lock:

- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`

Current active guidance:

- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`

Superseded prompt-draft source:

- `docs/specs/ilc_window_1289_1296_candidate_phase_grouping_v0.1.md`

Current closure handoff:

- `docs/specs/ilc_window_1281_1288_handoff_1288_v0.1.md`

Current launch roadmap:

- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`

The user's explicit `GO Phase 1291` authorized the public claimability verifier
contract preflight only. The next phase, Phase 1292, is sensitive because it
touches the verifier negative-path corpus and package-profile boundary and must
not proceed without explicit authorization.

---

## 2. Active Window Frontier

Phase 1289 records:

```text
window_1289_1302_sequence_lock_committed
window_1289_1302_sequence_lock_verdict=pass
phase_1290_context_capsule_v5_52_refresh_next
window_1289_1302_no_public_rc_or_public_activation
human_question_escalation_required_for_uncertain_authority
window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289
```

Phase 1290 records this capsule refresh:

```text
context_capsule_v5_52_frontier_refresh_phase_1290.v0.1
capsule_v5_52_supersedes_v5_51
window_1289_1302_sequence_lock_reflected_in_capsule_phase_1290
public_rc_blocker_map_refreshed_phase_1290
public_rc_remains_blocked_after_phase_1290
```

Historical Phase 1290 frontier phrase guard:

```text
Window 1289-1302 is open through Phase 1290
requires explicit `GO Phase 1291`
Phase 1290 does not close any of those blockers
```

Phase 1291 records the verifier contract preflight:

```text
public_claimability_verifier_contract_preflight_phase_1291.v0.1
public_claimability_activation_not_authorized_by_default_phase_1291
claimability_verifier_public_api_not_enabled_phase_1291
wallet_withdrawal_transfer_spend_still_blocked_phase_1291
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
claimability_contract_no_runtime_helper_added_phase_1291
phase_1292_verifier_negative_path_corpus_package_boundary_next
public_rc_remains_blocked_after_phase_1291
```

Locked Window 1289-1302 order:

| Phase | Scope | Sensitivity |
|-------|-------|-------------|
| 1289 | Window 1289-1302 sequence lock | SENSITIVE, complete |
| 1290 | Context Capsule v5.52 frontier refresh | NON-SENSITIVE, complete |
| 1291 | Public claimability verifier contract preflight | SENSITIVE, complete |
| 1292 | Verifier negative-path corpus and package-profile boundary | SENSITIVE, requires explicit `GO Phase 1292` |
| 1293 | `PUBLIC_RC_EXCLUDE` helper promotion/removal register | SENSITIVE |
| 1294 | Claimability package allowlist rehearsal | SENSITIVE |
| 1295 | TransportPrincipal lifecycle, revocation, replay preflight | SENSITIVE |
| 1296 | Hostile-network admission, ban, rate-limit, privacy plan | SENSITIVE |
| 1297 | Sidecar public-safe projection schema | SENSITIVE |
| 1298 | Sidecar bind, listener, peer-discovery authority preflight | SENSITIVE |
| 1299 | Release allowlist, artifact, Genesis readiness preflight | SENSITIVE |
| 1300 | Counsel, IP, publication clearance inventory | SENSITIVE |
| 1301 | Deep no-activation assertion audit | SENSITIVE |
| 1302 | Window 1289-1302 closure gate | SENSITIVE |

---

## 3. Governance Frontier

CDL-087 is ratified as of Phase 1278 Fix1:

```text
cdl087_ratification_evidence_phase_1278_fix1.v0.1
cdl087_ratified_phase_1278_fix1
cdl087_register_mutated_phase_1278_fix1
cdl087_conditions_1_to_6_reproved_phase_1278_fix1
cdl087_public_fetch_serving_not_enabled_phase_1278_fix1
cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1
no_cdl088_opening_phase_1278_fix1
```

CDL-088 remains unopened. Phase 1290 does not mutate the CDL register. Phase
1291 also does not mutate the CDL register and does not open any new
constitutional decision log entry.

Open counsel/public-release obligations remain:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
```

---

## 4. Public-RC Blocker Map

Public RC remains blocked after Phase 1291 by:

- Final public claimability verifier/API authority and public endpoint
  authorization.
- Verifier negative-path corpus and package-profile boundary.
- Public-safe disclosure schema, privacy filtering, replay/nullifier policy,
  and duplicate-claim registry.
- Actual TransportPrincipal public-path activation authority, including
  lifecycle, revocation, replay, admission, ban, rate-limit, and privacy
  controls.
- Actual public sidecar/projection serving authority, including public-safe
  field schema, filtering, bind/listener policy, and peer-discovery policy.
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

Phase 1291 does not close any of those blockers. It records the future
verifier contract envelope and denial conditions so Phase 1292 and later phases
can address them explicitly.

Exact blocker phrase guard:

```text
Final public claimability verifier/API authority
Verifier negative-path corpus and package-profile boundary
Public-safe disclosure schema
replay/nullifier policy
Actual TransportPrincipal public-path activation authority
Actual public sidecar/projection serving authority
Counsel/license/CLA/trademark/IP/publication clearance
Source allowlist export execution
Release artifact production
release-key generation
release envelope production
Genesis Atlas mutation/regeneration/signing
v0.2 signing authorization
CDL-088 opening
Wallet withdrawal/transfer/spend semantics
ECU minting
ILC settlement
```

---

## 5. Runtime Frontier

Public-path helper surfaces remain internal preflight helpers, not public RC
launch surfaces:

```text
transport_principal_public_path_adr_runtime_preflight_phase_1277.v0.1
transport_principal_public_p2p_not_activated_phase_1277
non_loopback_projection_still_blocked_phase_1277
sidecar_non_loopback_projection_authorization_preflight_phase_1278.v0.1
sidecar_public_serving_not_enabled_phase_1278
no_new_public_listener_phase_1278
non_loopback_bind_not_enabled_phase_1278
public_projection_endpoint_not_enabled_phase_1278
```

Claimability and conversion helper surfaces remain local/offline:

```text
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
conversion_sweeper_no_public_claimability_activation_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
phase_1282_fix1_claimability_runtime_audit_hardening
phase_1288_fix1_runtime_deep_audit_hardening
canonical_payload_float_rejection_hardened_phase_1288_fix1
untrusted_payload_cycle_depth_bounds_hardened_phase_1288_fix1
public_path_preflight_key_shape_hardened_phase_1288_fix1
```

No runtime code changes are made by Phase 1290.

Phase 1291 adds no runtime helper. Existing local helper surfaces remain
internal preflight helpers and retain their `PUBLIC_RC_EXCLUDE` launch-surface
exclusion:

```text
claimability_contract_no_runtime_helper_added_phase_1291
ilc_core/ledger/cdl048_conversion_sweeper_runtime.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
ilc_core/ledger/claimability_proof_binding_runtime.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

---

## 6. Non-Authorization Boundary

Phase 1291 does not authorize public RC, public launch, public repository
publication, public package publication, source allowlist export execution,
public release artifact production, release-key generation, release envelope
production, public P2P, public fetch serving, public sidecar/projection
serving, non-loopback sidecar/projection serving, public claimability API
activation, public verifier service, public claimability activation, wallet
withdrawal, wallet transfer, wallet spend, wallet signing authority, wallet
ledger-write authority, ECU minting, ILC settlement, withdrawal runtime
activation, CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration
or signing, v0.2 signing, IP filing, paper publication, immutable diagnostic
mutation, or production `commit.epoch` emission.

Exact non-authorization phrase guard:

```text
public claimability API activation
public verifier service
public P2P
public fetch serving
public sidecar/projection serving
source allowlist export execution
public release artifact production
release-key generation
release envelope production
wallet withdrawal
wallet transfer
wallet spend
CDL mutation
CDL-088 opening
Genesis Atlas mutation/regeneration
v0.2 signing
IP filing
paper publication
production `commit.epoch` emission
```

---

## 7. Phase 1291 Contract Boundary

Phase 1291 defines future `ClaimabilityVerifierInput` and
`ClaimabilityVerifierDecision` envelopes. It keeps all activation and economic
flags false, records mandatory future denial conditions, and leaves public-safe
field disclosure unresolved.

The Phase 1291 contract is a planning/spec boundary only:

```text
ClaimabilityVerifierInput
ClaimabilityVerifierDecision
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
```

No HTTP route, FastAPI route, socket listener, non-loopback bind, wildcard bind,
public host bind, peer discovery surface, public verifier service, public claim
endpoint, wallet withdrawal, wallet transfer, wallet spend, ECU mint endpoint,
or ILC settlement endpoint is added.

---

## 8. Next Gate

Next phase:

```text
Phase 1292 - Verifier negative-path corpus and package-profile boundary
```

Phase 1292 is sensitive. It requires explicit `GO Phase 1292` before execution.
Default authority stance remains no public endpoint, no public claimability API,
no wallet spend semantics, no ECU minting, and no ILC settlement.
