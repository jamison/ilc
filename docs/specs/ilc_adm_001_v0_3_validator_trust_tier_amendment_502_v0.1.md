# ILC ADM-001 v0.3 Validator Trust-Tier Amendment 502 v0.1

Status: governance amendment companion document
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

## 1. Amendment authority

ADM-001 advances to v0.3 in Phase 502.
CDL-056 is the constitutional authority for validator trust-tier elevation.
No CDL mutation occurs in Phase 502.

## 2. Trust-tier elevation flag

The validator trust-tier elevation flag is:
- validator-specific,
- non-inheritable,
- visible for consensus-related dispute handling,
- revoked when the validator falls below the ratified CDL-055 liveness threshold.

## 3. Eligibility and revocation

Eligibility requires active validator status and satisfaction of the ratified CDL-055 liveness
threshold. Revocation is automatic on liveness-threshold failure or unresolved equivocation state.
This amendment does not create a second liveness system.

## 4. Dispute tiebreaker rule

The trust-tier signal may be used only as a bounded tiebreaker in consensus-related disputes. It is
not an extra seat, not a weighted-vote multiplier, and not a general-purpose governance privilege.

## 5. Non-changes to quorum ladder

The 7+1 panel quorum ladder is unchanged by this amendment.
L-tier requirements remain unchanged.
CDL-V3 diversity-floor protections remain unchanged.
