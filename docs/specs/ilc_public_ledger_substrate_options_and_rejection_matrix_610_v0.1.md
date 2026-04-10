# ILC Public-Ledger Substrate Options and Rejection Matrix 610 v0.1

Status: locked
Date: 2026-04-10
Phase: 610
Owner lane: G8 settlement substrate reconciliation

## 1. Matrix target and inherited reconciliation state

Phase 610 compares the currently legitimate public-ledger substrate paths after
Phase 609 separated `ECU`, `ILC`, and the current RC/runtime posture.

`phase_610_options_matrix_evaluates_substrate_paths_without_selecting_runtime_implementation`.

This phase consumes the Phase 609 layer separation and the Phase 608 authority
hierarchy.

This phase compares substrate paths without selecting or implementing one.

Tier D historical strategy may inform option legitimacy only when explicitly
labeled as history.

`ADR-0026` remains the controlling accepted boundary surface and proposed ADRs
may not silently overrule it.

## 2. Evaluation criteria and non-goals

Phase 610 evaluates each option against the same bounded criteria.

The required evaluation criteria are:
- compatibility with the current locked runtime and wallet boundary,
- compatibility with the ECU/ILC separation established in Phase 609,
- compatibility with bounded current public-claims and evidence surfaces from
  Phases 600 and 602,
- compatibility with the accepted-boundary precedence established in Phase 608,
  with proposed ADRs treated as supporting inputs only,
- preservation of the distinction between public auditability and public
  identity exposure.

The non-goals of this phase are equally explicit:
- no implementation work,
- no wallet widening,
- no payment-lane widening,
- no governance-vehicle opening,
- no chain implementation or final-substrate ratification.

## 3. Option A - Internal-ledger-final posture

`internal_ledger_final_path_explicitly_evaluated`.

Path description:
- treat the current internal epoch-settled ledger posture as the permanent final
  substrate for `ILC` rather than as a bounded current implementation.

Benefits:
- lowest immediate implementation burden,
- maximum continuity with the current RC/testbed runtime,
- avoids near-term chain-integration complexity.

Risks/costs:
- conflicts with the December 2025 off-chain-first / later-chain historical
  strategy,
- weakens public-legitimacy posture for a hard settlement asset,
- risks silently promoting bounded RC runtime truth into permanent substrate
  closure without constitutional authorization.

Boundary-compatibility:
- compatible with current runtime continuity,
- incompatible with the Phase 607 and Phase 609 requirement that current runtime
  posture is not final substrate by implication,
- compatible with privacy preservation only in the narrow sense that nothing new
  is exposed, but it under-solves the later public auditability problem.

Keep/defer/reject rationale:
- reject. This path collapses bounded current runtime truth into forever
  substrate closure, which the Phase 607 lock and Phase 609 reconciliation
  explicitly forbid.

## 4. Option B - Custom minimal L1

`custom_minimal_l1_path_explicitly_evaluated`.

Path description:
- a later custom minimal L1 or equivalent chain-backed settlement layer designed
  around ILC's own auditability, privacy, and settlement semantics.

Benefits:
- strongest alignment with hard-settlement-asset framing,
- allows native design of auditability and privacy constraints together,
- preserves the December 2025 later-chain direction as a live strategic path.

Risks/costs:
- highest implementation and governance complexity,
- requires substantial engineering, validation, and legitimacy work before any
  public deployment,
- can overcommit the project too early if treated as already selected.

Boundary-compatibility:
- compatible with Phase 609's unresolved final-substrate posture,
- compatible with public auditability if identity/privacy separation is designed
  explicitly,
- not compatible with immediate execution because current wallet and runtime
  boundaries do not authorize implementation widening.

Keep/defer/reject rationale:
- defer. This remains a legitimate later path, but current authority does not
  justify selecting it now.

## 5. Option C - External rollup or L2 substrate

`external_rollup_or_l2_path_explicitly_evaluated`.

Path description:
- a later external rollup, L2, or comparable chain-backed substrate where `ILC`
  settlement anchors to a pre-existing ecosystem rather than a custom L1.

Benefits:
- lower infrastructure burden than a sovereign custom L1,
- faster access to existing settlement and tooling ecosystems,
- can preserve the December 2025 chain-backed direction without full custom
  chain ownership.

Risks/costs:
- imports external trust, fee, and governance dependencies,
- increases risk that public identity exposure and wallet correlation leak into
  the settlement layer,
- may compromise protocol-boundary clarity if chosen for convenience rather than
  design fit.

Boundary-compatibility:
- compatible with unresolved final-substrate posture,
- conditionally compatible with auditability/privacy only if identity exposure is
  not silently inherited from the external substrate,
- not compatible with immediate execution because current protocol boundaries do
  not authorize external-chain implementation work.

Keep/defer/reject rationale:
- defer. This path remains viable enough to keep in the options set, but it is
  not selected and requires stronger privacy and dependency analysis first.

## 6. Option D - Deferred-substrate ledger-interface path

`deferred_substrate_ledger_interface_path_explicitly_evaluated`.

Path description:
- preserve a ledger-interface architecture in the near term so current protocol
  and runtime work stays substrate-agnostic while the eventual public settlement
  path remains explicitly open.

Benefits:
- best fit with the current Phase 609 separation,
- preserves the December 2025 off-chain-first / later-chain strategy without
  prematurely selecting a chain,
- keeps current runtime work productive while avoiding false permanent closure.

Risks/costs:
- can be misread as indecision if not governed clearly,
- delays final public-ledger commitment,
- still requires a later governance vehicle to decide what the eventual public
  substrate becomes.

Boundary-compatibility:
- strongly compatible with current locked runtime and wallet boundaries,
- strongly compatible with Phase 609's ECU / ILC / runtime separation,
- strongly compatible with preserving auditability/privacy distinction until it
  is explicitly designed into a later public-ledger path.

Keep/defer/reject rationale:
- keep. This is the only option that preserves current implementation momentum,
  respects present authority, and avoids falsely claiming final substrate
  closure.

## 7. Comparative matrix and keep/defer/reject rationale

`every_substrate_option_carries_keep_defer_or_reject_rationale`.

`public_auditability_and_identity_privacy_constraints_apply_to_every_option`.

| Option | Authority compatibility | Runtime-boundary compatibility | Auditability/privacy compatibility | Implementation risk | Public-legitimacy implications | Outcome |
|---|---|---|---|---|---|---|
| Internal-ledger-final posture | weak | weak | partial only | low immediate, high architectural | weak long-run legitimacy for hard settlement asset | reject |
| Custom minimal L1 | conditional | conditional | potentially strong if designed correctly | high | potentially strong but unproven | defer |
| External rollup or L2 substrate | conditional | conditional | conditional, external-correlation risk | medium to high | potentially credible but dependency-heavy | defer |
| Deferred-substrate ledger-interface path | strong | strong | strong for preserving distinction pending later design | low to medium | honest near-term posture, defers final legitimacy decision explicitly | keep |

Comparative outcome summary:
- the internal-ledger-final posture is rejected because it violates the locked
  non-closure posture,
- custom minimal L1 remains a deferred legitimate later path,
- external rollup or L2 remains a deferred legitimate later path,
- deferred-substrate ledger-interface remains the kept architectural posture for
  near-term continuity without false closure.

## 8. Carry-forward constraints into Phase 611

`phase_610_does_not_authorize_wallet_widening_chain_implementation_or_payment_runtime`.

`phase_611_must_choose_governance_vehicle_from_phase_610_outcome`.

Phase 611 remains the governance-vehicle selection lane only.

Phase 610 does not open or ratify any ADR or CDL.

Phase 610 does not authorize wallet widening, chain implementation, or payment runtime.

More than one final substrate candidate remains viable in the long run even
though only the deferred-substrate ledger-interface posture is kept for the
near-term architecture.

Phase 611 must therefore choose the governance vehicle without pretending the
substrate is already ratified.

If only one final substrate path later remains viable, Phase 611 must still
decide whether memo, ADR, or CDL routing is required before any implementation
window.
