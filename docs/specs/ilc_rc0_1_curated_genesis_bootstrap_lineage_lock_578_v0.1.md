# ILC RC0.1 Curated Genesis/Bootstrap Lineage Lock 578 v0.1

Status: locked
Date: 2026-04-03
Phase: 578
Owner lane: G8 implementation cluster

## 1. Bounded RC target

Phase 578 locks the curated genesis/bootstrap lineage boundary for the RC0.1
operator-managed testnet.

This packet authorizes curated lineage and curated bootstrap governance for the
testnet fleet only. It does not claim public-release genesis governance,
permissionless admission, or public minting closure.

Required governance tokens:
- `curated_genesis_lineage_testnet_only`
- `bootstrap_inventory_not_admission_authority_by_itself`
- `candidate_discovery_not_active_peer_admission`
- `explicit_promotion_required_before_runtime_peer_use`
- `cdl_002_compromise_containment_revoke_recover_preserved`
- `rollback_and_tombstone_posture_explicit_for_curated_testnet`
- `validator_identity_binding_gap_not_silently_closed`
- `permissionless_public_admission_deferred_post_rc0_1`

## 2. Curated lineage scope

`curated_genesis_lineage_testnet_only`.

RC0.1 curated genesis/bootstrap lineage is for the operator-managed testnet
only and does not imply public-release genesis governance closure.

Canonical lineage and bootstrap authority in RC0.1 are curated control-plane
inputs, not autonomous admission authorities.

No permissionless public bootstrap or genesis-governance claim is made by this
packet.

## 3. Bootstrap admission and promotion contract

`bootstrap_inventory_not_admission_authority_by_itself`.

Bootstrap inventory is not admission authority by itself.

`candidate_discovery_not_active_peer_admission`.

Candidate discovery is not active-peer admission.

Accepted curated bootstrap sources remain bounded to:
- an operator-controlled genesis/bootstrap endpoint
- a curated GitHub-hosted bootstrap JSON file
- a local operator-managed override file

`explicit_promotion_required_before_runtime_peer_use`.

Explicit promotion is required before runtime peer use.

Approved runtime peer sets derive from approved inventory plus overrides minus
self and remain subject to TLS fingerprint verification.

Override or promotion policy must not silently admit unknown identities.

## 4. Key-compromise and rollback/tombstone posture

`cdl_002_compromise_containment_revoke_recover_preserved`.

The CDL-002 compromise trigger, containment, revocation, replacement, and
incident-audit contract remains preserved for the curated testnet lineage lane.

`rollback_and_tombstone_posture_explicit_for_curated_testnet`.

Rollback or tombstone posture for the curated testnet must remain explicit,
machine-auditable, and aligned with the CDL-007 supersession/clawback baseline.

Revoked or quarantined lineage state must not remain authoritative for runtime
admission or supersession authorization.

Compromise or rollback handling must not silently re-admit or silently
supersede compromised lineage state.

Bounded operator-managed tombstone posture for RC0.1 means:
- remove compromised or superseded identities from approved runtime promotion
  until explicit revoke/recover or supersession handling is complete
- require explicit replacement lineage or explicit deny/pin operator action
  before restored runtime use
- keep the resulting state auditable rather than implicit

This packet does not claim full public rollback/clawback governance
stabilization.

## 5. Validator identity-binding boundary

`validator_identity_binding_gap_not_silently_closed`.

The deferred CDL-052 binding gap between node-submission identity and canonical
validator identity is not silently treated as closed.

Selected bounded RC0.1 posture:
- operator-authorized curated non-validator submission identity model

Meaning:
- the RC0.1 agent/submission lane may use operator-authorized curated
  non-validator submission identities
- this packet does not claim that live submission identity is already bound to
  the canonical validator identity used by the genesis bootstrap runtime
- later runtime phases must not rely on silent validator-identity equivalence

## 6. Explicit deferrals to RC0.1+

Deferred beyond RC0.1:
- public genesis governance stabilization
- permissionless public bootstrap admission
- public validator join and recovery policy
- public minting, payout-traceability, and lineage-governance closure

`permissionless_public_admission_deferred_post_rc0_1`.
