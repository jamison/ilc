# ILC Issuance Stack Scoping — Window 1343-1368 v0.1

Status: Phase 1344 scoping artifact
Date: 2026-05-14
Owner lane: G8 Window 1343-1368

```text
issuance_stack_scoping_phase_1344.v0.1
cdl_053_vehicle_collision_resolved_or_rerouted_phase_1344
cdl_025_model_b_ratification_evidence_bound_phase_1344
cdl_026_cmax_25920000_bound_phase_1344
cdl_027_halving_h48_monthly_bound_phase_1344
phase_1345_emission_engine_next
issuance_stack_no_implementation_phase_1344
production_minting_not_authorized_phase_1344
public_rc_remains_blocked_after_phase_1344
```

## 1. Scope

Phase 1344 is a scoping and sequence-risk disposition phase. It does not
implement runtime code, open a CDL, ratify a CDL, activate mining, mint ILC,
mint ECU, settle ILC, or activate any public or wallet-facing value path.

This document defines the implementation surface for Phases 1345-1352 and
records the risk dispositions required by the Phase 1343 sequence lock:

- CDL-025 stale register wording versus ratification evidence.
- CDL-026 numeric `C_max` provenance.
- CDL-027 schedule constants.
- CDL-053 vehicle collision.
- Phase 1358 implementation versus activation boundary.
- Phase 1366 soft-RC eligibility standard.

## 2. Phase Claim Verification

| Claim | File/symbol checked | Result |
|---|---|---|
| Window 1343-1368 is open through Phase 1343 and Phase 1344 is next. | `docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md`; `docs/phases/STATUS.md` | confirmed |
| CDL-025 is ratified, but its register `current_candidate` text still says "planning recommendation - not ratified". | `docs/specs/ilc_constitutional_decision_log_v0.1.md`; `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md` | confirmed contradiction; evidence doc controls for runtime scoping |
| CDL-025 selected Model B / fee-funded tail. | `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md` | confirmed |
| CDL-026 ratified explicit finite cap. | `docs/specs/ilc_constitutional_decision_log_v0.1.md`; `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md` | confirmed |
| `C_max = 25,920,000 ILC` is used by later canonical/evidence-closure artifacts. | `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md`; `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`; `docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md` | confirmed |
| Older Phase 274 Fix2 memo says numeric `C_max` was not yet constitutionally bound at that boundary. | `docs/specs/ilc_cmax_symbolic_origin_and_numeric_binding_gap_274_fix2_v0.1.md` | confirmed historical contradiction; later closure artifacts bound Phase 1345 scoping input |
| CDL-027 ratifies halving, `H = 48`, and monthly issuance epochs. | `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md` | confirmed |
| Validation epoch and issuance epoch are distinct time scales. | `docs/specs/ilc_antigravity_context_capsule_v1.2.md`; `docs/specs/ilc_cdl_071_temporal_tier_reconciliation_opening_850_v0.1.md` | confirmed context; CDL-027 itself ratifies monthly issuance epoch |
| CDL-028 ratifies 10 percent fee-burn split. | `docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md` | confirmed |
| CDL-029 ratifies 80/15/5 performer/auditor/genesis split and `theta_hard = 1/20` continuity. | `docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md` | confirmed |
| CDL-030 ratifies `P_min = 0.75`, `P_max = 1.30`. | `docs/specs/ilc_cdl_030_ecu_price_clamp_ratification_evidence_277_v0.1.md` | confirmed |
| CDL-031 ratifies dynamic ranking policy, but runtime was not implemented in Phase 288. | `docs/specs/ilc_cdl_031_dynamic_ranking_policy_ratification_evidence_288_v0.1.md` | confirmed |
| CDL-047 ratifies treasury governance constants. | `docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md` | confirmed |
| CDL-054 ratifies validator reward-pool routing through CDL-047. | `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md` | confirmed |
| CDL-083 ratifies H-CON-02 ejected-stake and REFUTATION quorum/attribution rules. | `docs/specs/ilc_cdl_083_h_con_02_ratification_evidence_1104_v0.1.md`; `docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |
| CDL-053 must not be used for blocking authority without resolving older Werner-credit reservation. | `docs/specs/ilc_epoch_boundary_cdl_vehicle_selection_508_v0.1.md`; `docs/specs/ilc_epoch_boundary_witness_ratification_evidence_511_v0.1.md`; `docs/phases/STATUS.md` | confirmed |
| No `NotImplementedError` stubs exist under `ilc_core/epoch`, `ilc_core/ledger`, or `ilc_core/economics`. | `rg -n "NotImplementedError|not implemented|Not implemented|TODO.*CDL|CDL_.*DEPENDENCY|DEPENDENCY" ilc_core/epoch ilc_core/ledger ilc_core/economics` | confirmed; dependency tokens remain but no direct stub exception |

## 3. Ratified Implementation Surface

| CDL vehicle | Ratified phase | Runtime/implementation phase | Current code surface | Closing token |
|---|---:|---:|---|---|
| CDL-025 terminal issuance model | 267 | 1345 | New `ilc_core/epoch/epoch_emission_runtime.py` quote engine | `cdl_025_emission_schedule_runtime_phase_1345.v0.1` |
| CDL-026 finite `C_max` cap | 273 | 1345 | New `ilc_core/epoch/epoch_emission_runtime.py` cap guard | `cdl_026_cmax_cap_runtime_phase_1345.v0.1` |
| CDL-027 halving schedule | 276 | 1345 | New `ilc_core/epoch/epoch_emission_runtime.py` schedule functions | `cdl_027_epoch_length_runtime_phase_1345.v0.1` |
| CDL-028 fee-burn split | 274 | 1346 | Future fee-burn runtime | `cdl_028_fee_burn_split_runtime_phase_1346.v0.1` |
| CDL-029 80/15/5 allocation | 272 | 1347 | Future allocation distributor | `cdl_029_allocation_distributor_phase_1347.v0.1` |
| CDL-047 treasury governance | 418 | 1348 | Future treasury governance runtime | `cdl_047_treasury_governance_runtime_phase_1348.v0.1` |
| CDL-054 validator reward pool | 491 | 1349 | Future validator reward routing runtime | `cdl_054_validator_reward_pool_routing_phase_1349.v0.1` |
| CDL-083 ejected stake treasury distribution | 1105 | 1350 | `ilc_core/economics/epoch_attribution_settle_runtime.py` | `cdl_083_ejected_stake_distribution_phase_1350.v0.1` |
| CDL-030 ECU price clamp | 277 | 1351 | Future ECU clamp runtime | `cdl_030_ecu_price_clamp_runtime_phase_1351.v0.1` |
| CDL-031 dynamic ranking policy | 288 | 1356-1357 | `governance_weight.py` and `reputation.py` lane | `cdl_031_runtime_deferred_to_governance_weight_lane_phase_1344` |

Phase 1352 is the first integration gate for the issuance/economics stack. It
must not pass unless Phases 1345-1351 have landed and tests prove the end-to-end
ledger invariant remains double-entry safe.

## 4. CDL-025/026/027 Dispositions for Phase 1345

### CDL-025

The decision log row is internally stale: it is marked `ratified` while the
`current_candidate` field still says "planning recommendation - not ratified".
Phase 1344 resolves this for implementation scoping by binding Phase 1345 to the
Phase 267 ratification evidence document, which formally declares Model B
fee-funded tail as the ratified option.

### CDL-026

`CDL-026` ratifies the explicit finite-cap class in Phase 273. The numeric value
`25,920,000 ILC` has a provenance wrinkle: Phase 274 Fix2 recorded that the
numeric value was not yet bound in that specific boundary, while later Phase
275, Phase 298, and Phase 600 artifacts consume `25,920,000` as the cap used by
the deterministic Genesis economics evidence matrix.

Phase 1345 may therefore use `C_max = Decimal("25920000")` only in a
non-activating runtime/quote engine. Any future attempt to produce production
minting instructions must still pass its activation gate and must cite the same
cap chain. This phase does not mutate the CDL register to repair the stale
CDL-026 prose.

### CDL-027

Phase 1345 must bind to the Phase 276 ratified schedule:

- formulation: `halving`
- schedule constant: `H = 48`
- issuance epoch duration: `1 month`

The older temporal architecture distinguishes validation epoch from issuance
epoch. Phase 1345 may expose `VALIDATION_EPOCH_SECONDS = 60` as context only,
but the issuance schedule itself is keyed by integer issuance epoch sequence
and monthly issuance-epoch semantics.

## 5. CDL-053 Vehicle Collision Disposition

Phase 1344 formally reroutes blocking-authority vehicle selection away from
CDL-053.

Disposition:

```text
cdl_053_vehicle_collision_resolved_or_rerouted_phase_1344
blocking_authority_vehicle_must_not_be_cdl_053_phase_1344
blocking_authority_vehicle_selection_deferred_to_phase_1362_phase_1344
```

Rationale:

- Phase 508 and Phase 511 explicitly preserve CDL-053 as reserved/unaffected.
- Phase 1343 confirmed the current CDL register has no CDL-053 row.
- Older canon repeatedly reserves CDL-053 for Werner-credit architecture.
- CDL-057 is ratified only as a provenance-only epoch-boundary witness lane and
  explicitly does not authorize blocking or settlement-veto semantics.

Phase 1362 must therefore open or select a non-CDL-053 vehicle if blocking
authority is still desired. Phase 1344 does not choose the new vehicle number,
does not open that vehicle, and does not activate CDL-057 blocking authority.

## 6. Phase 1358 Implementation Versus Activation Boundary

Phase 1358 may implement an inert/default-off `ilc_core/` to `ilc_consensus/`
bridge only. It must not route live ECU transfers through `ilc_consensus/`
unless a later activation gate explicitly authorizes live transfer submission.

Required boundary token:

```text
phase_1358_bridge_implementation_not_live_transfer_activation_phase_1344
```

## 7. Phase 1366 Soft-RC Eligibility Standard

Phase 1366 may record `soft_rc_eligible=true` only if all of these are true:

1. Phases 1345-1352 have landed and the issuance/economics integration gate
   passes with double-entry invariants.
2. Phases 1353-1361 have landed or have explicit non-blocking deferrals recorded
   by their own gates.
3. The Phase 1362 blocking-authority vehicle collision is resolved without
   reusing CDL-053.
4. HIGH-001 sender-identity leakage is not contradicted by any sender-privacy
   claim.
5. No public RC publication, public serving, public claimability, wallet,
   withdrawal, ECU mint, ILC settlement, or public value-path activation is
   implied by the soft-RC decision.
6. The soft-RC environment is private/operator-controlled until a later public
   RC/public path gate says otherwise.

If any item is ambiguous, Phase 1366 must block rather than emit
`soft_rc_eligible=true`.

## 8. NotImplementedError Survey

The required survey over `ilc_core/epoch`, `ilc_core/ledger`, and
`ilc_core/economics` found no direct `NotImplementedError` runtime stubs. The
remaining issuance/economics gap is absence of dedicated production issuance
runtime code, not a raised-stub cleanup.

Existing dependency-token surfaces discovered in the survey:

- `ilc_core/epoch/epoch_boundary_witness_runtime.py` keeps
  `BLOCKING_AUTHORITY_DEFERRED = True`.
- `ilc_core/economics/epoch_attribution_settle_runtime.py` carries CDL-081,
  CDL-083, CDL-084, and CDL-085 dependency tokens.
- `ilc_core/economics/passive_ecu_attribution_runtime.py` carries CDL-060
  dependency tokens.

## 9. Non-Authorization

Phase 1344 does not authorize production issuance implementation. It does not authorize production minting,
soft-RC eligibility, public RC claim, source publication, release
signing, public activation, public claimability/API activation, wallet-facing
activation, ECU minting, ILC settlement, value-path activation, Genesis
intervention execution, Genesis/Atlas mutation, CDL mutation, CDL opening,
CDL-053 opening, CDL-057 activation, CDL-088 opening, identity artifact
creation, seed or key generation, secret-store write, counsel approval, patent
filing, trademark-policy publication, or legal conclusion.
