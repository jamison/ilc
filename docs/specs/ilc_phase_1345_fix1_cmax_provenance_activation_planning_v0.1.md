# ILC Phase 1345 Fix1 Cmax Provenance and Activation Planning v0.1

Status: Fix-phase planning/provenance repair
Date: 2026-05-14
Window: 1343-1368

```text
phase_1345_fix1_cmax_provenance_activation_planning.v0.1
cmax_25920000_platonic_year_times_1000_confirmed_phase_1345_fix1
cdl_025_current_candidate_stale_text_repaired_phase_1345_fix1
cdl_026_cmax_numeric_binding_register_repaired_phase_1345_fix1
cdl_027_schedule_register_repaired_phase_1345_fix1
phase_1368_production_minting_activation_or_defer_prompt_hardened_phase_1345_fix1
production_minting_activation_requires_phase_1366_soft_rc_true_and_phase_1367_clean_pass
public_rc_remains_blocked_after_phase_1345_fix1
```

## 1. Purpose

Phase 1345 introduced the non-activating CDL-025/026/027 epoch-emission quote
runtime. Post-phase review found three planning/provenance issues:

- the CDL-025 decision-log row still carried stale "planning recommendation"
  wording despite Phase 267 ratification;
- the CDL-026 decision-log row did not expose the canonical numeric cap binding
  that Phase 1345 now enforces in runtime;
- Phase 1368 planning did not explicitly state how the default-off production
  minting gate becomes active or is carried forward.

This Fix1 records the repair without changing runtime behavior and without
activating production minting.

## 2. Cmax Provenance Resolution

`C_max = 25,920,000 ILC` is the canonical runtime cap for the current issuance
stack. The symbolic origin is the Platonic/precessional-cycle candidate recorded
in `docs/specs/ilc_cmax_symbolic_origin_and_numeric_binding_gap_274_fix2_v0.1.md`:
25,920 years multiplied by 1,000.

The early Phase 274 Fix2 memo correctly described a then-open numeric-binding
gap. Later closure artifacts consume `25,920,000` as the canonical runtime input:

| Evidence | Role |
|----------|------|
| `docs/specs/ilc_cmax_symbolic_origin_and_numeric_binding_gap_274_fix2_v0.1.md` | Recovered symbolic origin and historical candidate lineage |
| `docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md` | Uses locked cap baseline `C_max = 25,920,000` for schedule evidence |
| `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md` | Marks `C_max = 25,920,000 ILC` as canonical against CDL-026 |
| `docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md` | Uses the ratified supply cap in deterministic Genesis economics evidence |
| `ilc_core/epoch/epoch_emission_runtime.py` | Locks `C_MAX_ILC = Decimal("25920000")` in Phase 1345 runtime |

The older `1,000,000,000` and `100,000,000` values remain historical alternatives
only. They do not supersede the Phase 275/298/600 closure chain or Phase 1345
runtime binding.

## 3. CDL Register Repair

`docs/specs/ilc_constitutional_decision_log_v0.1.md` was repaired as follows:

- CDL-025 current candidate now records `fee-funded tail / Model B` without the
  stale "not ratified" qualifier.
- CDL-026 current candidate now records `C_max = 25,920,000 ILC`, the Platonic
  Year × 1,000 provenance, the Phase 273/275/298/600 binding chain, and the
  Phase 1345 runtime constant.
- CDL-027 current candidate now records `H=48` and monthly issuance epochs while
  explicitly separating issuance-epoch duration from validation-epoch duration.

This is a factual register repair against already-ratified rows. It does not
open a CDL, change a selected option, or ratify a new decision.

## 4. Phase 1368 Activation Route

Phase 1345 intentionally leaves production minting inactive. The forward plan now
routes the runtime gate to Phase 1368:

1. Phase 1366 must record `soft_rc_eligible=true`.
2. Phase 1367 must record `phase_1366_blockers_addressed_or_clean_pass_phase_1367`.
3. Phase 1368 must either implement the private soft-RC production minting gate
   in `ilc_core/epoch/epoch_emission_runtime.py` and record
   `production_minting_activated_phase_1368`, or leave the gate closed and record
   `production_minting_activation_deferred_phase_1368`.

This activation route does not authorize public claimability, public P2P,
wallet-facing flows, mint-instruction execution, ledger writes, or ILC
settlement. It only makes the Phase 1345 runtime gate concretely executable under
the later soft-RC authority path.

## 5. Non-Authorization Floor

This Fix1 does not authorize production minting, production mining,
production-minted ILC, ECU minting, ILC settlement, wallet-facing actions, public
activation, public RC publication, release signing, CDL opening, CDL mutation,
CDL-088 opening, Genesis/Atlas mutation, identity artifact creation, counsel
approval, patent filing, or legal conclusion.

Graph delta:
`graph_delta=support_only:docs/specs/ilc_phase_1345_fix1_cmax_provenance_activation_planning_v0.1.md -> planning/frontier`
