# ILC CDL-029 Post-Theta-Hard Dust Routing Amendment Evidence 1351a v0.1

Status: Phase 1351a evidence
Date: 2026-05-14
Scope: CDL-029 sub-quantum residual routing at ILC issuance/conversion settlement boundary only

## Summary

Phase 1351a amends CDL-029 to close the sub-quantum residual routing edge case
surfaced by Phase 1347 and Phase 1347 Fix1. The amendment applies only after
the caller has already determined that Genesis overhead is permanently cap-blocked
and passes `genesis_overhead_cap_blocked=True`.

This amendment does not govern local ECU attribution, local refutation incentives,
aesthetic-panel rewards, non-settlement graph activity, or CDL-052 settlement-grade
Mode-2 adjudication semantics. It also does not authorize production distribution,
ledger writes, ILC settlement, ECU minting, public activation, or soft-RC eligibility.

## Required Tokens

```text
cdl_029_post_theta_hard_dust_routing_amendment_phase_1351a.v0.1
cdl_029_amendment_phase_1351a
cdl_083_upheld_refutation_recipients_primary_dust_route_phase_1351a
performer_pool_fallback_dust_route_phase_1351a
post_theta_hard_routing_implemented_phase_1351a
pre_theta_hard_routing_unchanged_phase_1351a
production_distribution_not_activated_phase_1351a
genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a
```

## Amendment Clause

After `theta_hard` is permanently reached, signalled by caller passing
`genesis_overhead_cap_blocked=True`, sub-quantum residual from CDL-029 allocation
rounding routes first to CDL-083 Q4 caller-filtered upheld-refutation recipients
when the caller provides an explicit deterministic non-empty recipient list, and
otherwise routes to the performer pool. This applies only to sub-quantum residuals
produced by CDL-029 allocation rounding at ILC issuance or conversion settlement
time; it does not govern local ECU attribution, local refutation incentives,
aesthetic-panel rewards, or non-settlement graph activity.

## Canon Checks

| Claim | Source checked | Result |
|-------|----------------|--------|
| CDL-029 is ratified and preserves `theta_hard = 1/20` | `docs/specs/ilc_constitutional_decision_log_v0.1.md` CDL-029 row | confirmed |
| CDL-029 had no prior amendment entry before Phase 1351a | `docs/specs/ilc_constitutional_decision_log_v0.1.md` pre-execution direct read | confirmed |
| CDL-083 Q4 is the upheld-refutation attribution interface | `docs/specs/ilc_constitutional_decision_log_v0.1.md` CDL-083 row | confirmed |
| CDL-083 Q4 is caller-filtered and uses `refuting_agent_id` | `docs/specs/ilc_cdl_083_h_con_02_ratification_evidence_1104_v0.1.md` | confirmed |
| CDL-V7 is admissibility-only for this phase, not the attribution interface | `docs/specs/ilc_constitutional_decision_log_v0.1.md` CDL-V7 row and CDL-083 Q4 row | confirmed |
| Allocator has no float governor import | `ilc_core/epoch/allocation_distributor_runtime.py` | confirmed |
| Production allocation distribution remains default-off | `ilc_core/epoch/allocation_distributor_runtime.py` | confirmed |

## Routing Table

| State | Caller input | Residual route | Full Genesis base tranche behavior |
|-------|--------------|----------------|------------------------------------|
| Pre-theta-hard | `genesis_overhead_cap_blocked=False` | Genesis overhead, unchanged from Phase 1347 | Normal CDL-029 quote, default-off |
| Post-theta-hard, residual-only, recipients supplied | `genesis_overhead_cap_blocked=True`, non-empty deterministic recipient list | CDL-083 Q4 caller-filtered upheld-refutation recipient pool | Only allowed when quantized Genesis base tranche is zero |
| Post-theta-hard, residual-only, no recipients | `genesis_overhead_cap_blocked=True`, `None` or empty list | Performer pool fallback | Only allowed when quantized Genesis base tranche is zero |
| Post-theta-hard, non-zero Genesis base tranche | `genesis_overhead_cap_blocked=True`, any recipient list | Not routed by this phase | Fail closed with `genesis_overhead_base_cap_blocked_full_tranche_deferred_phase_1351a` |

## Runtime Boundary

The runtime records the settlement-bound residual route in
`EpochAllocationDistributionQuote.residual_route`, the caller-filtered recipient
list in `upheld_refutation_recipients`, and the residual amount in one of:

- `rounding_residual_to_genesis_overhead_ilc`
- `rounding_residual_to_upheld_refutation_recipients_ilc`
- `rounding_residual_to_performer_pool_ilc`

For upheld-refutation recipient routing, Phase 1351a records a recipient pool
quote and deterministic sorted recipient list. It does not perform a ledger write
or define intra-recipient disbursement for multi-recipient residual pools.

## Non-Claims

Phase 1351a does not:

- Activate production allocation distribution.
- Write ledger state.
- Route non-zero full Genesis base tranches after cap-block.
- Activate CDL-052 Mode-2 settlement semantics.
- Govern local ECU attribution or local refutation rewards.
- Treat CDL-V7 as the upheld-refutation attribution interface.
- Claim soft-RC eligibility.

## Graph Delta

```text
graph_delta=load_bearing_artifact_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> cdl-029-post-theta-hard-residual-routing-amendment
graph_delta=load_bearing_artifact_changed:ilc_core/epoch/allocation_distributor_runtime.py -> cdl-029-post-theta-hard-residual-routing-runtime
```
