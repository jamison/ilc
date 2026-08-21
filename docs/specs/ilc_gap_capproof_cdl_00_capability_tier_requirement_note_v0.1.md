# ILC CapProof CDL-00 Capability Tier Requirement Note v0.1

Status: precondition note for GAP-CAPPROOF-CDL-00
Phase: GAP-SCHEMA-PREREQS-00
Date: 2026-08-21

## 1. Requirement

`capability_tier` MUST be a required derived field in the first CapProof
Capability Vector schema ratified by GAP-CAPPROOF-CDL-00.

This is a schema requirement from day one. It is not a post-compute label that
may be added later without migration.

## 2. Rationale

CapProof Capability Vectors are expected to be signed and content-addressed.
Adding `capability_tier` after public records exist would require a schema
version bump and migration of all existing CV records. Reserving it before
ratification has zero migration cost and gives later routing, scheduling, and
pricing logic a stable derived slot.

## 3. Derivation Boundary

The exact threshold table is a GAP-CAPPROOF-CDL-00 decision. The field must be
a canonical string derived from the five probe scores, for example one of:

- `baseline`
- `provisional`
- `standard`
- `advanced`

The final label set and thresholds must be ratified in the CapProof CDL. This
note only requires that the derived field exists and is signed as part of the
CV artifact.

## 4. Non-Claims

This note does not open or ratify the CapProof CDL, execute probes, activate
CapProof pricing, mint ILC, create ECU credit, authorize user-provided kernels,
or change any live epoch runner.
