# ILC CDL-053 Werner Local Productive Credit Opening 1407-Fix0 v0.1

Phase: 1407-Fix0
Date: 2026-05-20
Status: opening document; CDL register mutation occurs in a separate commit

Required token:

```text
cdl_053_werner_local_productive_credit_opened_phase_1407_fix0
```

## 1. Purpose

Phase 1407-Fix0 opens CDL-053 for a narrow Werner local productive-credit
architecture. This is the Werner local productive-credit architecture opening
for the maintenance-equivalent reviewed-work lane. The scope is reviewed
productive work that creates local,
non-settlement credit eligibility before any conversion into settlement-grade
ECU. This opening is needed so the later CDL-093 maintenance lottery lane can
reference a Werner local productive-credit source rather than treating the
maintenance pool as a CDL-047 treasury-governance quote candidate.

This phase does not prelock CDL-053, ratify CDL-053, mutate runtime code,
activate ECU creation, activate wallet behavior, activate ILC settlement,
activate maintenance lottery distribution, or change the J-008 gate verdict.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-053 row is absent before this opening | `docs/specs/ilc_constitutional_decision_log_v0.1.md`; historical `git show 9eaffd74:...` | confirmed |
| CDL-052 and CDL-054 bracket rows exist | `docs/specs/ilc_constitutional_decision_log_v0.1.md` rows `CDL-052` and `CDL-054` | confirmed |
| Phase 1263 rejected direct Werner ECU creation | `docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md` | confirmed |
| CDL-085 ratified `EDGE_MINT_PHI_BOUND = Decimal("0.60")` | `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` | confirmed |
| Phase 1407 prelock currently points CDL-093 funding to CDL-047 | `docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md` | confirmed |
| J-005 records maintenance task reward eligibility but no live lottery distribution | `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md` §6-§8 | confirmed |

MemPalace tier A was queried as an advisory recall net for CDL-053 / Werner
local productive credit context. Useful hits pointed back to Phase 1263 STATUS,
the CDL register, and prior Werner non-authorization language; those repo paths
were direct-read before use.

## 3. Narrow Opening Scope

CDL-053 opens the following narrow question set:

```text
cdl_053_werner_local_productive_credit_opened_phase_1407_fix0
```

CDL-053 scope:

- reviewed productive work creates local credit eligibility;
- local credit is non-wallet, non-transferable, and not settlement-grade ECU;
- maintenance-equivalent reviewed productive work is the first target lane;
- provenance-equivalent edge-mint work inherits the ratified CDL-085
  `EDGE_MINT_PHI_BOUND = Decimal("0.60")` boundary;
- conversion from local credit to settlement-grade ECU requires a later
  conversion gate and cannot bypass consensus-epoch or public-economics controls.

This opening is intentionally not a full Werner flow-governor CDL. It does not
authorize heat, topology pressure, cache pressure, route demand, or reputation
signals to directly create ECU.

## 4. Explicit Non-Scope

CDL-053 Fix0 does not govern or authorize:

- Werner flow-governor runtime policy;
- heat-to-ECU minting;
- topology-pressure-to-ECU minting;
- per-request ECU tolls;
- per-hop fetch or relay micropayments;
- validator rewards, which remain under CDL-054 and related runtime gates;
- treasury governance, which remains under CDL-047;
- wallet withdrawal, wallet transfer, wallet spend, or wallet signing behavior;
- ILC settlement or ILC transfer;
- live maintenance lottery distribution;
- public claimability or public economics admission;
- runtime mutation.

Phase 1263 remains binding for the excluded flow-governor path:

```text
direct_werner_ecu_creation_rejected_phase_1263
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
```

The Phase 1263 closing conditions for a future flow-governor CDL remain open:
default SIM-FETCH evidence profile, beta/noise decomposition or equivalent
productive-flow evidence, spectral trust thresholds, TransportPrincipal or
equivalent authenticated public-path identity, and separation from any direct
productive-credit authorization lane.

## 5. CDL-085 Inheritance

CDL-053 inherits the CDL-085 Werner phi-bound only for maintenance tasks that are
provenance-equivalent edge-mint work:

```text
EDGE_MINT_PHI_BOUND = Decimal("0.60")
```

This phase does not re-ratify CDL-085, change its value, or extend the bound to
non-provenance task classes without later CDL-053 prelock and ratification.

## 6. Deliberation Questions for Phase 1407-Fix1

### Q1 - Productive-Work Scope

Which task categories qualify for Werner local credit eligibility under CDL-053?
Starting candidate: review-lane-passed maintenance tasks per J-005 §6:
`star.map.embedding`, `contradiction.sweep`, `graph.compression`,
`stability.simulation`, and `custom_review_lane_assigned`.

Does any other productive-work category qualify, or are non-maintenance
productive-credit categories deferred to future CDL-053 amendments?

### Q2 - Local Credit Unit and Conversion Gate

What is the local credit unit designation? The unit must be non-ECU, non-wallet,
and non-transferable before conversion.

What gate converts local credit to settlement-grade ECU? Candidate:
`consensus_epoch_public_economics_gate_and_j008_production_activation`.

### Q3 - CDL-085 Phi-Bound Inheritance

For provenance-equivalent edge-mint work within the maintenance task category,
does CDL-053 directly inherit `EDGE_MINT_PHI_BOUND = Decimal("0.60")` from
CDL-085?

Which maintenance task classes count as provenance-equivalent edge-mint work,
and which task classes are non-provenance maintenance governed by other quality
filters?

### Q4 - Anti-Gaming and Anti-Inflation Boundary

What controls prevent local credit from inflating settlement-grade ECU supply
without a conversion gate?

Minimum controls to resolve in Phase 1407-Fix1:

- review-lane pass required;
- content-addressed task id required;
- duplicate task rejected;
- duplicate output hash collapsed;
- one-credit-per-agent-per-epoch cap;
- author/reviewer conflict checks;
- no settlement-grade ECU without conversion gate;
- no wallet mutation;
- no direct heat-to-ECU minting.

## 7. Historical Hardening

Historical hardening command:

```bash
git show 9eaffd74:docs/specs/ilc_constitutional_decision_log_v0.1.md | rg -n "^\\| CDL-053 \\|"
```

Result: no CDL-053 row exists at the Phase 1407 main commit. This confirms the
Fix0 opening is the first CDL-053 register insertion.

## 8. Non-Ratification and Non-Activation

CDL-053 is opened only after the separate CDL mutation commit. It is not
prelocked or ratified by Phase 1407-Fix0.

Phase 1407-Fix0 does not:

- prelock CDL-053;
- ratify CDL-053;
- mutate CDL-093;
- create or modify runtime code;
- create settlement-grade ECU;
- mint ECU;
- mint ILC;
- activate live maintenance lottery distribution;
- execute lottery draws;
- modify wallets;
- authorize public claimability;
- change the J-008 gate verdict.

## 9. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_053_werner_local_productive_credit_opening_1407_fix0_v0.1.md -> constitutional/cdl
```
