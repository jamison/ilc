# ILC Node Schema Implementation Readiness 356 v0.1

## 1. Scope

This artifact bridges the ratified node-schema constitutional stack to actionable implementation planning for Window 358+.

`Implementation readiness maps prerequisites and module targets only.`

This phase does not permit ilc_core work.

`Module-target identification in this phase is descriptive only, not implementation authorization.`

## 2. Ratified surfaces and immediate implementation prerequisites

`CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038`

Ratified surfaces and immediate prerequisites:
- `CDL-034 immediate implementation prerequisites: envelope parser separation, reserved-field enforcement, primitive taxonomy integration.`
- `CDL-035 immediate implementation prerequisites: validation_state state-machine attachment, gate_verdict reference handling, quarantine-state handling.`
- `CDL-036 immediate implementation prerequisites: header-first dissemination, payload fetch contract, signature scope enforcement.`
- `CDL-037 immediate implementation prerequisites: structured executable descriptor parsing, sandboxed runtime binding, safety-contract verification.`
- `CDL-038 immediate implementation prerequisites: successor-node promotion flow, promotion_receipt handling, no automatic reputation carry-forward.`

## 3. Relevant ilc_core module targets (no implementation in this phase)

Relevant module targets for later implementation planning:
- `ilc_core/node/node_v0.py`
- `ilc_core/schema/d2_schema_baseline_runtime.py`
- `ilc_core/protocol/schema.py`
- `ilc_core/network/gossip.py`
- `ilc_core/network/peer.py`
- `ilc_core/network/wire_transport_runtime.py`
- `ilc_core/security/signer_lineage_runtime.py`
- `ilc_core/security/key_compromise_runtime.py`
- `ilc_core/analysis/agent_profiles.py`

These module references are planning anchors only. They are not an authorization to modify `ilc_core/` in Phase 356.

## 4. Dependency ordering and cross-CDL coupling

`ADM-003 integration remains a Window 358+ implementation prerequisite.`

`CDL-035 lifecycle semantics constrain CDL-038 promotion continuity.`

`CDL-034 envelope placement constrains CDL-037 executable descriptor integration.`

`CDL-036 transport/header work remains downstream of CDL-034 and CDL-035 semantics.`

Implementation ordering must respect the ratified dependency chain. Parallelization is acceptable only where these dependency constraints are not violated.

## 5. Implementation boundary and Window-357 prerequisite

`Window 358+ may begin runtime implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.`

Phase 356 does not authorize runtime implementation.

No runtime implementation occurs in Phase 356.

No decision-log mutation occurs in Phase 356.
