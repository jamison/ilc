# ILC ECU Active Layer Runtime and Accounting Spec 628 v0.1

Status: runtime and accounting spec
Date: 2026-04-13
Window: 624-630
Phase: 628
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Authorization basis — CDL-063 ratified

Phase 628 consumes the ratified `CDL-063` constitutional boundary and
implements the bounded ECU active layer as live internal runtime.

`CDL_063_DEPENDENCY = "cdl_063_ratified_627.v0.1"`
`cdl_063_dependency_consumed`

Live bounded runtime implementation is required in this phase. No deferred
runtime disposition is permitted.

`ecu_active_layer_runtime_spec_628_locked`
`disposition_b_not_permitted_window_624_630`

## 2. Earmark state machine

The runtime defines all five earmark states:
- `proposed`
- `accepted`
- `delivered`
- `debited`
- `expired`

Valid transitions:
- `proposed -> accepted`
- `accepted -> delivered`
- `delivered -> debited`
- `proposed -> expired`
- `accepted -> expired`

Invalid transitions:
- `debited -> any`
- `expired -> any`
- `delivered -> expired`

Processing boundaries:
- proposal: immediate runtime reservation after oversubscription and cap checks
- acceptance: immediate runtime state transition only if the attempted
  acceptance epoch is not past `expiry_epoch`
- delivery: immediate runtime state transition after the bounded delivery
  signal only if the attempted delivery epoch is not past `expiry_epoch`
- debit: only at epoch-boundary processing when `commit_epoch > delivery_epoch`
- expiry: only at epoch-boundary processing when `commit_epoch >= expiry_epoch`
  for `proposed` or `accepted` earmarks

`earmark_state_machine_defined`

## 3. Epoch-settled accounting model

The earmark ledger record schema is:
- `earmark_id`
- `commission_id`
- `commissioning_agent_id`
- `performing_agent_id`
- `earmark_amount`
- `state`
- `proposal_epoch`
- `expiry_epoch`
- `acceptance_epoch`
- `delivery_epoch`
- `debit_epoch`
- `task_description_hash`
- `contribution_id`

The exact balance invariant is:

`spendable_ecu(A) = total_accrued_ecu(A) - sum(reserved_earmarks_by_A)`

where reserved means states `proposed`, `accepted`, or `delivered`.

Expiry release semantics:
- earmarks in `proposed` or `accepted` state transition to `expired` when
  `commit_epoch >= expiry_epoch`
- expired earmarks release their reservation back to spendable ECU by leaving
  the reserved-state set

Reserved-balance floor semantics:
- direct accrued-ECU resets that would drop an agent below currently reserved
  earmarks are rejected by the runtime
- the debit path assumes the reserved-balance invariant is preserved between
  proposal time and epoch-boundary settlement

Debit-at-commit semantics:
- `delivered` earmarks remain reserved until final settlement
- debit executes only when `commit_epoch > delivery_epoch`
- debit reduces the commissioning agent's accrued ECU by `earmark_amount`
- debit does not create any credit-side supplement for the performing agent

Runtime parameter defaults consumed from SIM-COMMISSION-01 and the Phase 627
ratification carry-forward are:
- `fixed_expiry_validation_epochs = 2880`
- `active_earmark_cap_per_agent = 8`

Phase 628 does not change the passive Phase 550 proxy values.

`epoch_settled_accounting_model_defined`

## 4. Machine-legible interfaces

`earmark_propose(...)`
- output shape:
  - `ok`
  - `token`
  - `data`
- success token: `earmark_proposed`
- failure tokens:
  - `same_key_self_commission_prohibited`
  - `oversubscribed_earmark_blocked`
  - `active_earmark_cap_exceeded`
  - `earmark_id_conflict`
  - `invalid_earmark_amount`
  - `invalid_earmark_amount_non_finite`

`earmark_accept(...)`
- output shape:
  - `ok`
  - `token`
  - `data`
- success token: `earmark_acceptance_recorded`
- failure tokens:
  - `earmark_not_found`
  - `performing_agent_mismatch`
  - `earmark_past_expiry`
  - `invalid_state_transition`

`earmark_deliver(...)`
- output shape:
  - `ok`
  - `token`
  - `data`
- success token: `earmark_delivery_recorded`
- failure tokens:
  - `earmark_not_found`
  - `performing_agent_mismatch`
  - `earmark_past_expiry`
  - `invalid_state_transition`

`earmark_status(...)`
- output shape:
  - `ok`
  - `token`
  - `data`
- success token: `earmark_status_found`
- failure token:
  - `earmark_not_found`

`earmark_history(agent_id)`
- output shape:
  - `ok`
  - `token`
  - `data.agent_id`
  - `data.history`
- success token: `earmark_history_returned`

Internal runtime guard:
- `set_accrued_ecu(...)` rejects non-finite amounts with
  `accrued_ecu_cannot_be_non_finite`

`machine_legible_interfaces_defined`

## 5. Runtime implementation surface

Concrete runtime file landed in Phase 628:
- `ilc_core/ledger/ecu_active_layer_runtime.py`

This runtime implements:
- bounded in-memory active-layer state
- earmark proposal with oversubscription and active-cap checks
- acceptance recording with named performing-agent verification and past-expiry
  rejection
- delivery recording with named performing-agent verification and past-expiry
  rejection
- epoch-bound debit processing
- expiry processing
- status and history queries
- spendable ECU computation against reserved earmarks
- rejection of direct accrued-balance resets below reserved earmark totals

No deferred-runtime disposition is offered in this phase.

`runtime_implementation_complete_in_phase_628`

## 6. AG-gate assessment

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Agents now have bounded internal economic agency beyond topology-only description. |
| AG-2 W_e increase | advance | Directed commission can now reserve and settle bounded internal effort-routing commitments. |
| AG-3 Epistemic integrity | pass | Runtime does not bypass authored-envelope submission or CDL-V7 validation. |
| AG-4 ECU-ILC separation | pass | ECU debit remains internal accounting only; `ecu_debit_not_ilc_payment_628`. |
| AG-5 Harness-agnostic | neutral | Runtime is protocol-side and machine-legible, not a harness-local convenience feature. |
| AG-6 Near-infinite scale | pass | Fixed expiry and active-earmark cap bound state growth. |
| AG-7 Machine-legible first | advance | All runtime interfaces return machine-legible dict payloads and failure tokens. |
| AG-8 Outbound economic loop | advance | The loop now has live bounded runtime enforcement for reservation, expiry, and debit-at-commit. |

## 7. Wallet boundary confirmation

The Phase 576 and Phase 581 wallet boundary remains unchanged in Phase 628.
This runtime creates no participant-visible wallet write surface, no
claimability widening, and no ILC transfer path.

`wallet_boundary_576_581_unchanged_in_628`
`ecu_debit_not_ilc_payment_628`
