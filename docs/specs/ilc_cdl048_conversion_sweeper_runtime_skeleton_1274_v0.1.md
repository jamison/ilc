# ILC CDL-048 Conversion Sweeper Runtime Skeleton 1274 v0.1

Status: runtime skeleton recorded
Date: 2026-05-09
Phase: 1274
Owner lane: G8 public-RC economic boundary

Required tokens:

- `cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1`
- `conversion_sweeper_no_public_claimability_activation_phase_1274`
- `ecu_lot_deadline_epoch_enforcement_recorded_phase_1274`
- `wallet_withdrawal_transfer_spend_still_blocked_phase_1274`

Verdict:

```text
phase_1274_cdl048_conversion_sweeper_runtime_skeleton_verdict=pass_skeleton_only_public_claimability_blocked
```

## 0. Canon Check

Phase 1274 used exact-token `rg` as a schema/completion check only. Broader
concept discovery searched CDL-048, conversion sweeper, claimability, ECU lot,
deadline, issuance epoch, wallet, withdrawal, transfer, spend, settlement,
Decimal, fixed point, receipt root, wallet state root, lifecycle, replay, double
conversion, no claimability, no ECU minting, and no ILC settlement terms.

| Check | Result |
|-------|--------|
| Required-token audit | The four Phase 1274 required tokens were present only in the Phase 1274 prompt before execution and are now recorded in the runtime, spec, walkthrough, STATUS, and planning frontier. |
| Concept-discovery search | Confirmed CDL-048 is ratified with `ecu_conversion_deadline = 4 issuance epochs`; Phase 1270 routed ECU lot accounting, deadline tracking, exact numeric boundaries, canonical JSON receipt/root binding, and replay/double-conversion prevention into this window. |
| Contradiction and non-claim search | Confirmed public claimability remains inactive, wallet withdrawal/transfer/spend remains disabled, ECU minting remains unauthorized, ILC settlement remains unauthorized, public RC remains blocked, and CDL-087 remains open/prelocked/not ratified. |
| Source expansion | Direct-read the Phase 1273 sequence lock, Window 1273-1280 guidance, Phase 1270 Gap 13 preflight, Phase 1252 public claimability boundary, Phase 576 wallet boundary, Phase 615 lifecycle contract, Phase 419 CDL-048 evidence, the CDL register, current lifecycle runtime, public wallet runtime, public receipt runtime, and adjacent tests. |

## 1. Runtime Skeleton

Phase 1274 adds `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` as an
isolated ledger helper. It does not widen `PublicWalletRuntime`, the lifecycle
runtime, FastAPI routes, public receipt classes, storage backends, or settlement
surfaces.

The skeleton records:

- ECU lots with `lot_id`, canonical `agent_id`, exact positive `amount_ecu`,
  `issue_epoch`, computed `deadline_epoch`, `origin`, funding provenance, and
  conversion status.
- CDL-048 deadline constant `CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS = 4`.
- Deadline status from epoch integers only: `open`, `deadline_epoch`, or
  `expired`.
- Internal conversion receipts with wallet-state root, settled-runtime root,
  conversion epoch, settled-runtime epoch, conversion transition, conversion
  key, and sweeper state root before conversion.
- State-root export using canonical JSON and SHA-256.

The runtime version is:

```text
cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1
```

## 2. Exact Numeric and Epoch Guards

The Phase 1274 boundary intentionally does not reuse legacy helpers that accept
Python floats. `amount_ecu` is accepted only as `Decimal`, integer, or string,
and the runtime rejects bool, float, malformed values, non-finite Decimal values,
zero, and negative values before any deadline or conversion arithmetic.

Epoch inputs are non-negative integers. Bool is rejected. Deadline arithmetic is
only:

```text
deadline_epoch = issue_epoch + 4
```

No wall-clock time, `datetime.now()`, `time.time()`, random source, socket, HTTP
call, or external I/O is used by the skeleton.

## 3. Replay, Double-Conversion, and Root Binding

The conversion key is SHA-256 over canonical JSON containing:

- conversion epoch
- canonical agent identity
- ECU lot id
- wallet-state root
- conversion state transition
- settled runtime root

The state records conversion keys and converted lot status. Replaying a recorded
conversion key fails closed with `cdl048_conversion_replay_detected`; converting
an already converted lot fails closed with `cdl048_conversion_duplicate_lot`.

Missing wallet-state roots and missing settled-runtime roots fail closed. A
settled-runtime root is accepted only when the supplied settled-runtime epoch
matches the conversion epoch; otherwise the runtime fails closed with
`cdl048_settled_runtime_root_stale`.

This is still a skeleton. It binds supplied roots and performs deterministic
freshness checks at the epoch-field level, but it does not yet prove wallet-root
membership, latest-balance receipt inclusion, public claim proof validity, or
non-loopback API authority. Those proof-binding duties remain routed to Phase
1275.

## 4. Canonical Receipt and State Export

Machine-verifiable payloads use:

```text
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

The sensitive-runtime guardrail now includes
`ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` in the strict machine
JSON scan, so future edits that remove `sort_keys=True` or `allow_nan=False`
from its canonical JSON helper fail the guardrail.

Receipts explicitly record:

```text
public_claimability_activated=false
wallet_withdrawal_enabled=false
wallet_transfer_enabled=false
wallet_spend_enabled=false
ecu_mint_authorized=false
ilc_settlement_authorized=false
```

## 5. Non-Claims

Phase 1274 does not authorize or perform:

- public claimability runtime activation
- public or non-loopback claimability API
- wallet withdrawal
- wallet transfer
- wallet spend
- wallet signing authority
- wallet ledger-write authority
- ECU minting
- ILC settlement or withdrawal runtime activation
- public RC claim
- public launch claim
- public repository publication
- public package publication
- public P2P exposure
- public fetch serving
- public sidecar/projection serving
- CDL mutation
- CDL-087 ratification
- release-key generation
- release envelope production
- public release artifact production
- v0.2 signing
- Genesis mutation, regeneration, or signing

The required non-claim tokens are:

```text
conversion_sweeper_no_public_claimability_activation_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
```

## 6. Closing Condition and Carry-Forward

Phase 1274 closes the narrow CDL-048 runtime-skeleton blocker:

```text
phase_1274_cdl048_conversion_sweeper_runtime_skeleton_verdict=pass_skeleton_only_public_claimability_blocked
ecu_lot_deadline_epoch_enforcement_recorded_phase_1274
```

It does not close public claimability. Remaining public-RC blockers include:

- public claimability proof binding over settled runtime root, wallet-state
  root, latest balance receipt, history digest, epoch identifier, and canonical
  agent identity
- CDL-087 ratification or explicit non-ratification disposition before public
  fetch/sidecar claims
- TransportPrincipal public-path integration and ADR hardening
- sidecar non-loopback/public projection authorization
- release manifest and source allowlist prepublication
- counsel/IP/publication authorization
- v0.2 signing authorization

Next planned phase:

```text
Phase 1275 - Public claimability proof-binding runtime boundary
phase_1275_claimability_proof_binding_runtime_requires_explicit_go
```

## 7. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/ledger/cdl048_conversion_sweeper_runtime.py -> ecu/ilc/public_rc
graph_delta=support_tests_added:tests/test_phase_1274_cdl048_conversion_sweeper_runtime_skeleton.py -> validation
graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier
graph_delta=support_guardrail_changed:tools/check_sensitive_runtime_coding_taboos.py -> validation/security
graph_delta=load_bearing_spec_added:docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md -> ecu/ilc/public_rc
graph_delta=support_only:docs/phases/phase_1274_cdl048_conversion_sweeper_runtime_skeleton_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
