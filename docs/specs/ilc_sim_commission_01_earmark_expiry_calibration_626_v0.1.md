# ILC SIM-COMMISSION-01 Earmark Expiry Calibration 626 v0.1

Status: completed simulation synthesis
Date: 2026-04-13
Window: 624-630
Phase: 626
Owner lane: G8 ECU active economic layer runtime strike force

## 1. Simulation identity and question

SIM-COMMISSION-01 calibrates the earmark expiry horizon for `CDL-063`.

Question: What is the right earmark expiry horizon in validation epochs that
balances agent autonomy against ledger bloat?

`sim_commission_01_expiry_calibration_complete`

## 2. Parameters and assumptions

The calibration uses these bounded assumptions:
- validation epoch cadence: 1 minute
- issuance epoch cadence: approximately 43,200 validation epochs
- trivial commissioned task: 5-60 validation epochs
- normal commissioned task: 120-1440 validation epochs
- complex multi-step task: 1440-10080 validation epochs if left as one coarse
  commission, but v1 runtime should prefer decomposition into smaller
  commissions rather than week-scale single earmarks
- unresolved earmarks impose persistent reserved-balance state cost and reduce
  the commissioning agent's effective spendable ECU balance

The simulation is bounded to internal ECU runtime only. It does not model
public settlement, wallet widening, or external purchasing power.

## 3. Analysis

The floor must be long enough to avoid killing a legitimate single-contribution
commission that spans several hours because of asynchronous agent schedules or
normal validation lag. A floor below `240` validation epochs starts to make a
same-day commission unreliable.

The nominal value should support typical same-day work while still bounding
state growth. A fixed expiry of `2880` validation epochs keeps one earmark
alive for two days, which gives real buffer above the upper end of the normal
task band and absorbs asynchronous scheduling and validation lag without
collapsing into week-scale reserve locking.

The ceiling marks the point where earmarks start impairing the active layer's
usefulness by freezing too much spendable balance for too long. `10080`
validation epochs is about 23 percent of one issuance epoch, which is the
highest tolerable v1 reserve-lock boundary before earmarks start functioning as
quasi-long-duration locked reserves.

Tiered expiry was evaluated. It improves fit to task complexity in theory, but
it adds branch complexity to proposal validation, runtime state transitions, and
hardening. For v1, that complexity is not justified while the runtime lane is
still being established.

The volume-cap question was also evaluated. A bounded active layer needs a cap
on simultaneous active earmarks per commissioning agent per validation epoch
window to prevent high-volume low-quality commission spam from turning the
runtime into an unbounded reservation surface. A cap that is too low makes the
active layer unusable for legitimate parallel work; a cap that is too high
undoes the bounded-state goal. The v1 recommendation is a runtime cap of `8`
simultaneous active earmarks per commissioning agent per validation epoch
window.

## 4. Results

Minimum viable expiry floor:
- `240` validation epochs

Nominal recommended fixed expiry:
- `2880` validation epochs

Maximum sensible expiry ceiling:
- `10080` validation epochs

Recommended v1 rule:
- fixed expiry, not tiered
- `recommended_fixed_expiry_validation_epochs = 2880`
- `recommended_active_earmark_cap_per_agent = 8`

`sim_commission_01_minimum_expiry_validation_epochs: 240`
`sim_commission_01_nominal_expiry_validation_epochs: 2880`
`sim_commission_01_maximum_expiry_validation_epochs: 10080`
`sim_commission_01_active_earmark_cap_per_agent: 8`

## 5. Governance dispositions

Disposition on fixed vs tiered expiry:
- fixed expiry selected for v1 bounded runtime
- tiered expiry rejected in this window because it introduces avoidable runtime
  and hardening complexity before the first bounded active layer is proven

`sim_commission_01_tiered_expiry_disposition: reject_tiered_keep_fixed_v1`

## 6. Forward pointer

Phase 627 must lock the fixed-expiry direction into the CDL-063 ratification
evidence using `recommended_fixed_expiry_validation_epochs = 2880`.

Phase 628 runtime must implement expiry processing against the fixed horizon and
should consume `recommended_active_earmark_cap_per_agent = 8` as the bounded
runtime cap unless a stronger runtime-specific reason is documented. Phase 629
hardening must verify that expired earmarks release reserves correctly at the
epoch boundary and that the active-earmark cap is enforced.
