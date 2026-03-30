# ILC CDL-058 re_admission_boundary Prelock Hardening 519 v0.1

Status: prelock hardening
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. Prelock scope

CDL-058 remains a narrow validator re_admission boundary lane.

The lane is limited to cooldown-based re-entry after:
- `liveness_miss`,
- `equivocation`,
- `voluntary_exit`.

## 2. Exit-reason enumeration lock

exit_reasons_locked: liveness_miss, equivocation, voluntary_exit

The exit-reason enumeration is closed for this window. No additional reasons are in scope for
Phase 520 ratification.

## 3. CDL-046 timed_out orthogonality lock

cdl_046_timed_out_orthogonal

`CDL-046 timed_out` remains a node lifecycle recovery lane. It does not govern validator
re-entry, validator cooldowns, or validator fault recovery semantics.

## 4. CDL-055 dep chain integrity

cdl_058_dep_chain_requires_cdl_055_staking

CDL-058 depends on CDL-055 for:
- liveness threshold semantics,
- liveness penalty semantics,
- equivocation slash semantics.

CDL-058 does not replace CDL-055 and does not add an alternate staking regime.

## 5. Rejected scope expansions

Rejected scope expansions:
- blocking authority overlap with `CDL-057`,
- `timed_out` amalgamation with `CDL-046`,
- automatic reputation carry-forward on re-admission.

## 6. Ratification readiness

CDL-058 remains status: open in Phase 519.

Phase 520 ratification may proceed only on the locked lane:
- cooldown period per exit reason,
- issuance-epoch cooldown constants from SIM-011,
- preserved CDL-046 orthogonality,
- preserved CDL-055 dependency chain.
