# CDL-048 Genesis Tranche Treatment Amendment — Phase 1575c-Fix3e

**CDL:** CDL-048 (ECU Mandatory Conversion Deadline, ratified Phase 419)
**Amendment:** Phase 1575c-Fix3e
**Date:** 2026-07-16
**Sensitivity:** SENSITIVE

## Amendment

CDL-048 Genesis tranche treatment is hereby set to:

```text
genesis_tranche_treatment = "explicitly_applied_by_authorized_value_path"
```

## Meaning

The fixed 5% lifetime genesis tranche (CDL-048, 1,296,000 ILC =
`FIXED_GENESIS_TRANCHE_ILC`) is the constitutional lifetime settlement right
for Genesis Agent 1. It is realized via the cumulative CDL-029 genesis overhead
allocation (Surface 1 in the Fix3b reconciliation certificate) until the
accrual governor hard cap is reached. The tranche is not a separate payment
stream above Surface 1; it is the cap and settlement right for Surface 1
accumulations.

This treatment is NOT an activation of wallet writes, treasury writes, ILC
minting, or settlement. It is a governance decision that the value path is
defined and valid, pending the public-RC economic activation guard.

## Genesis Destination

The CDL-029 genesis overhead pool settles to:

```text
Genesis Agent 1 — agent_id: c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9
Key record: docs/genesis/genesis_agent1_pubkey_record_838a.txt
Ceremony: Phase 838a (2026-04-25)
```

## Non-Claims

This amendment does NOT:

- Activate production ILC minting, wallet writes, or settlement
- Authorize any value transfer before the public-RC economic activation guard clears
- Change any `NOT_ACTIVATED` or `production_*_authorized = False` guard
- Claim the CDL-028 genesis_burn_pool routes to Genesis Agent 1 (it does not)

## Token

```text
CDL048_TREATMENT_APPLIED_TOKEN = "cdl_048_genesis_tranche_treatment_applied_phase_1575c_fix3e.v0.1"
```
