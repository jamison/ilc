# ILC refutation_criterion Schema Specification 462 v0.1

Status: completed schema specification
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Field definition

refutation_criterion is an optional field in the authored envelope.

It is the opt-in authored-envelope signal that routes a node into the Popperian evaluation path.
The field expresses the falsifiable claim boundary that a later challenger may target.

## 2. Authored envelope placement (CDL-034 conformance)

The field lives in the authored envelope only.
It is not a protocol-envelope control field and it is not a transport-envelope routing field.
This placement preserves CDL-034 envelope separation and keeps the refutation target coupled to the authored claim itself.

## 3. Required elements

A valid `refutation_criterion` must include at minimum:
- the claim being refuted,
- the type of evidence required for a valid refutation,
- the scope boundary of the claim.

The claim being refuted must be stated in falsifiable terms.
The evidence type must be classified as empirical, logical, or counter-example.
The scope boundary must state where the claim does not apply.

## 4. Validation rules

Validation occurs before authored-envelope acceptance into the Mode 2 path and before any downstream staking or refutation handling.
Malformed `refutation_criterion` payloads are rejected at submission time.
The authored envelope signature must cover the field, so structure validation occurs before the node is admitted and then the signed authored envelope is treated as the immutable claim surface.
The field must not collide with CDL-034 reserved-field rules; any reserved-field collision is a hard submission failure.

## 5. Interaction with normative: true metadata

A node carrying both `refutation_criterion` and `normative: true` is rejected at submission time unless an explicit future constitutional reconciliation clause authorizes the combination.
In Phase 462 there is no such reconciliation clause.
The current rule is conservative: a normative node may not simultaneously declare a Popperian refutation surface.

## 6. Gate 2 clearance statement

Gate 2 cleared.
No CDL-052 opening occurs in Phase 462.
refutation_criterion implementation in ilc_core/ is deferred until after CDL-052 ratification.
