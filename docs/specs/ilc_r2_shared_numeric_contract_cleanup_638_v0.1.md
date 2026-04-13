# ILC R2 Shared Numeric Contract Cleanup 638 v0.1

Status: implemented
Date: 2026-04-13
Window: 637-641
Phase: 638
Owner lane: G8 residual exact-numeric cleanup

## 1. Ratified dependency and cleanup target

Phase 638 consumes ratified `CDL-064` and cleans up the highest-risk residual
`R2` shared-contract leak paths left after the Tier-0 strike force.

The target is narrow:
- `ilc_core/types.py`
- `ilc_core/protocol/mapper.py`
- directly coupled helpers and tests required to keep those contracts coherent

No decision-log mutation occurs in Phase 638. No ADR mutation occurs in
Phase 638.

`r2_shared_numeric_contract_cleanup_638_locked`
`cdl_064_dependency_consumed_in_phase_638`

## 2. Primary shared contract files

The primary shared-contract files migrated in Phase 638 are:
- `ilc_core/types.py`
- `ilc_core/protocol/mapper.py`

Directly coupled coherence helpers and tests also updated:
- `ilc_core/consensus/engine.py`
- `tests/test_protocol_mapper.py`
- `tests/test_api.py`

## 3. Shared numeric contract changes

Phase 638 removes the float-bearing `net_stake` contract from both shared graph
types:
- `Node.net_stake`
- `ClaimRecord.net_stake`

The new bounded shared-contract behavior is:
- `net_stake` is parsed through the exact-numeric helper boundary rather than
  stored as binary float
- non-finite ingress is rejected by the shared `net_stake` parser
- Pydantic machine serialization for `net_stake` now emits CDL-064 canonical
  decimal strings

Protocol mapper cleanup applied in the same phase:
- claim/refute `net_stake` is emitted as a canonical decimal string
- task-outcome `stake_spent` and `reward_paid` are emitted as canonical decimal
  strings
- epoch-summary `total_ecu_spent`, `total_reward_paid`, and
  `clearing_price_ilc_per_ecu` stop coercing exact values through `float(...)`
  and now emit canonical decimal strings

One directly coupled runtime helper changed for coherence:
- `ilc_core/consensus/engine.py` now converts `node.net_stake` at the tax-rate
  arithmetic boundary rather than assuming the shared contract remains float

`shared_net_stake_float_contract_removed`
`protocol_mapper_float_projection_removed`

## 4. Compatibility and machine-legible boundary

The bounded compatibility posture after Phase 638 is:
- shared runtime objects may still accept legacy float ingress at creation time
  because the exact-numeric parser converts legacy values through `Decimal(str(value))`
- machine-legible outputs for the touched shared mapper surfaces now follow
  CDL-064 canonical decimal-string rules
- raw `Decimal` objects are not emitted by the touched mapper surfaces

The external numeric boundaries touched in this phase do not pass `NaN` or
`Infinity` through after parsing:
- `net_stake` on `Node` and `ClaimRecord` routes through the exact-numeric
  parser and rejects non-finite values
- mapper serialization only emits canonical decimal strings from already-validated
  exact numeric values

This phase follows CDL-064 exactly. It does not invent a new numeric contract.

`shared_numeric_contract_canonicalization_applied`

## 5. Verification and residual defers

Verification used for Phase 638:
- prompt validation
- Phase 637 sequence-lock gate
- direct shared-contract and protocol-mapper tests
- directly coupled claim-record, API, and consensus-engine compatibility tests

Residual defers left after this phase:
- non-commit event-log numeric validators and helper constructors are deferred
  to Phase 639
- settlement metrics and active-layer compatibility egress are deferred to
  Phase 639
- canon-export companion validators and scalar contracts are deferred to
  Phase 640

`phase_638_verification_defined`
`window_637_641_moves_to_protocol_runtime_adjacent_cleanup`
