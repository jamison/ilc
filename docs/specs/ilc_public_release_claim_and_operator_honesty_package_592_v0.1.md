# ILC Public Release-Claim and Operator Honesty Package 592 v0.1

Status: locked
Date: 2026-04-04
Phase: 592
Owner lane: G8 public-release integration

## 1. Public release-claim target

Phase 592 locks the bounded public release-claim and operator-honesty posture
for Window 585-594 after the runtime bridge packet in Phase 591.

This packet defines the claims that may be made about the current RC0.1 public
candidate, the non-claims that must remain explicit, and the machine-legible
disclosure surfaces that keep the candidate honest.

Required governance tokens:
- `public_release_claim_must_bind_to_phase_591_runtime_boundary`
- `bounded_public_rc_claim_not_mainnet_equivalence_claim`
- `candidate_manifest_release_claim_and_delta_must_remain_machine_legible`
- `operator_honesty_requires_explicit_pending_and_deferred_scope`
- `publication_pending_items_must_be_disclosed_not_implied_complete`
- `post_rc_deferred_scope_must_be_disclosed_not_silently_omitted`
- `economic_claim_summary_must_match_checked_runtime_evidence`
- `curated_operator_controlled_boundary_must_be_disclosed`
- `public_release_claim_must_not_overclaim_genesis_or_governance_closure`
- `public_release_claim_must_not_overclaim_hostile_internet_or_permissionless_admission`
- `harness_agnostic_boundary_must_be_preserved_in_public_claim_package`
- `operator_honesty_package_not_public_legitimacy_substitute`
- `phase_593_coherence_report_must_consume_phase_592_honesty_package`

## 2. Dependency tiers and bounded evidence inputs

Minimum dependency bundle carried by this packet:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`
- `docs/specs/ilc_public_runtime_integration_over_receipt_boundary_591_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `tools/run_rc0_1_release_candidate.py`
- `tools/run_rc0_1_release_claim.py`
- `tools/check_rc0_1_release_claim.py`
- `tools/render_rc0_1_readiness_delta.py`

Bounded evidence-context rule:
- the release-candidate, release-claim, and readiness-delta toolchain is bounded evidence tooling rather than public law by itself
- `tools/run_rc0_1_release_candidate.py`, `tools/run_rc0_1_release_claim.py`, `tools/check_rc0_1_release_claim.py`, and `tools/render_rc0_1_readiness_delta.py` remain machine-check surfaces over RC0.1 evidence rather than self-executing legitimacy sources
- the package inherits the frozen public identity, quorum, settlement, and Genesis-lineage boundary from Phase 591 rather than redefining any of those surfaces

## 3. Authorized bounded public claims

`public_release_claim_must_bind_to_phase_591_runtime_boundary`.

The bounded public release claim must bind to the Phase 591 runtime boundary.
No claim in this packet may outrun the frozen 587-590 law plus the 591 bridge
mapping.

`bounded_public_rc_claim_not_mainnet_equivalence_claim`.

The current RC0.1 package is a bounded public RC claim, not a mainnet
-equivalence claim.

`candidate_manifest_release_claim_and_delta_must_remain_machine_legible`.

The candidate manifest, release claim, and readiness delta must remain
machine-legible surfaces.

`economic_claim_summary_must_match_checked_runtime_evidence`.

The economic claim summary must match checked runtime evidence from the current
candidate lane.

`curated_operator_controlled_boundary_must_be_disclosed`.

The bounded public claims are tied to the current RC0.1 candidate surfaces only,
including deterministic substrate closure, release gate, release claim,
readiness delta, and the checked economic claim summary under curated,
operator-controlled conditions.

## 4. Mandatory non-claims and deferred scope

`operator_honesty_requires_explicit_pending_and_deferred_scope`.

Operator honesty requires explicit pending and deferred scope.

`publication_pending_items_must_be_disclosed_not_implied_complete`.

Publication-pending items must be disclosed and not implied complete.

`post_rc_deferred_scope_must_be_disclosed_not_silently_omitted`.

Post-RC deferred scope must be disclosed and not silently omitted.

`public_release_claim_must_not_overclaim_genesis_or_governance_closure`.

The public release claim must not overclaim Genesis or governance closure. The
remaining Genesis dilution, freshness, and accrual-governor provenance items are
still open carry-forward work.

`public_release_claim_must_not_overclaim_hostile_internet_or_permissionless_admission`.

The public release claim must not overclaim hostile-internet readiness,
permissionless admission, or the closure of later hardening and public-ingress
lanes.

The document also states that curated operator control, private testbed
assumptions, and bounded bootstrap inventory remain part of the current RC
posture.

## 5. Operator honesty and machine-legible disclosure rules

`harness_agnostic_boundary_must_be_preserved_in_public_claim_package`.

The package preserves the harness-agnostic boundary. It does not reopen
harness-specific packaging or product claims through release language.

`operator_honesty_package_not_public_legitimacy_substitute`.

The operator honesty package is not a public legitimacy substitute.

The honesty package preserves machine-legible references to the candidate
manifest, release claim, readiness delta, and checked evidence surfaces.

The honesty package distinguishes clearly between what the package proves, what
is deferred, and what still requires later constitutional or runtime closure.

## 6. Forbidden interpretations and exclusions

The following interpretations are forbidden:
- treating the RC0.1 package as a mainnet-equivalence claim
- treating publication-pending items as already complete merely because the package exists
- treating post-RC deferred items as silently in scope
- treating the honesty package as independent public legitimacy
- reopening harness-specific packaging or product surfaces through the claim language

## 7. Explicit deferrals to later phases

Deferred beyond Phase 592:
- coherence report and capsule update to Phase 593
- closure gate and handoff to Phase 594
- any remaining Genesis dilution, freshness, or accrual-law closure to dedicated later vehicles
- any inbound payment ingress, hostile-internet admission, or post-RC transport/security expansion to later windows

`phase_593_coherence_report_must_consume_phase_592_honesty_package`.
