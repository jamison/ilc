# ILC Phase 1325 Fix1 CCSS-002 Access Audit Hardening v0.1

**Phase:** 1325 Fix1
**Date:** 2026-05-13
**Status:** local/private audit hardening complete; no public serving

```text
phase_1325_fix1_ccss_002_access_audit_hardening.v0.1
ccss_002_zk_record_kind_validated_phase_1325_fix1
ccss_002_revocation_precedes_zk_deferred_phase_1325_fix1
ccss_002_pre_serialization_payload_byte_budget_phase_1325_fix1
sidecar_del_control_character_rejected_cross_module_phase_1325_fix1
public_rc_remains_blocked_after_phase_1325_fix1
phase_1326_ccss_sealed_sender_boundary_next_after_fix1
```

## Scope

Phase 1325 Fix1 disposes of the post-1325 audit findings against
`ilc_core/sidecars/confidential_coordination_capability.py` and sweeps the
shared DEL-character text-validation gap across the audited sidecar validator
surfaces.

## Fixes

The CCSS-002 local access decision now evaluates deterministic grant and
revocation facts before optional ZK deferral. A matching revocation therefore
returns `revoked` even when a valid ZK membership interface record is also
present. This preserves revocation audit semantics while remaining fail-closed.

The optional ZK seam now validates that `zk_interface_record` is specifically a
`zk_membership_interface_ref` record for the same private shard and membership
boundary. Passing a grant, revocation, policy, malformed record, or mismatched
ZK seam as `zk_interface_record` returns `zk_deferred` with
`malformed_zk_interface`; it never grants local access.

CCSS-002 canonical JSON validation now enforces a traversal-time byte budget for
payload keys, string values, and integer text before `json.dumps()` runs. This
prevents direct callers of `canonical_ccss_002_json()` from forcing large
char-by-char validation and serialization work only to fail at the post-dumps
10MB cap.

The sidecar text validators now reject the ASCII DEL character (`0x7f`) in
addition to control characters `0x00` through `0x1f`. The sweep covers:

- `ilc_core/sidecars/confidential_coordination_capability.py`
- `ilc_core/sidecars/confidential_coordination_shard.py`
- `ilc_core/sidecars/registry_manifest.py`
- `ilc_core/sidecars/claimability_receipt_verifier.py`
- `ilc_core/sidecars/transport_principal_admission.py`
- `ilc_core/sidecars/local_graph_memory_projection.py`
- `ilc_core/sidecars/public_fetch_p2p_readiness.py`

## Non-Claims

This fix does not authorize public RC, source export execution, source
publication, package publication, public serving, public P2P, public
confidential coordination serving, public membership directory, public
credential authority, public ZK verifier, public capability service, release
artifact production, release-key generation, release signing material, signing,
Genesis Atlas mutation/regeneration/signing, v0.2 signing, identity artifacts,
wallet writes, ECU minting, ILC settlement, value-path activation, or Phase 1326
execution.

## Next

Phase 1326 remains the next planned CCSS-003 sealed sender boundary and requires
explicit `GO Phase 1326`.
