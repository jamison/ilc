# ILC Censorship-Resistance Threat Model 672 v0.1

Status: criteria artifact
Date: 2026-04-15
Phase: 672
Owner lane: G8 censorship-resistance and independence strike force

## 1. Purpose and authority basis

Phase 672 defines the row-7 threat model for censorship against public
legitimacy surfaces.

This artifact operationalizes the Phase-671 lock that row-7 censorship is
broadly defined and that practical exclusion counts even when packet delivery
still works.

`broad_censorship_model_means_practical_exclusion_counts`

Authority basis:
- `docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md`
- `docs/specs/ilc_option_b_remaining_rows_closure_criteria_661_v0.1.md`
- `docs/specs/ilc_phase_671_676_sequence_lock_v0.1.md`
- `docs/specs/ilc_coupling_invariants_governance_lock_663_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md`

## 2. Public legitimacy surfaces in scope

The following are in-scope public legitimacy surfaces for row 7:
- public admission legitimacy
- canonical namespace and handle authority
- public quorum, panel, and evaluation authority
- public settlement legitimacy
- public reputation continuity
- public receipt lineage and public machine-legible queryability

`public_legitimacy_surfaces_include_admission_namespace_quorum_settlement_reputation_and_receipt_lineage`

These are the surfaces where practical exclusion matters constitutionally. A
system can be transport-live and still fail row 7 if these surfaces are
capturable or bottlenecked.

## 3. Threat actors and choke-point classes

Relevant threat actors include:
- hostile or censoring states
- hosting and cloud providers
- sequencer, validator, or settlement operators
- API providers and managed control-plane vendors
- dashboard or portal operators
- custody or wallet intermediaries
- protocol insiders attempting to re-center legitimacy in one shell or one
  operator path

Relevant choke-point classes include:
- network access chokepoints
- routing or relay chokepoints
- sequencing or ordering chokepoints
- admission or namespace chokepoints
- dashboard, shell, or API chokepoints
- custody or withdrawal chokepoints
- receipt publication or audit-surface chokepoints

## 4. Attack vectors that count as censorship

The row-7 censorship model includes the following attack families:

| Surface | Attack vector | Why it counts |
|---|---|---|
| network reachability | outright denial, blocking, targeted outage | participant cannot publish, observe, or contest legitimacy-relevant state |
| routing and relay | throttling, selective delay, relay suppression, traffic shaping | participant is practically excluded even without a total packet ban |
| sequencing / ordering | sequencer withholding, reorder privilege, finalize-only-if-approved path | outside actor can decide which legitimacy claims become effective |
| admission / namespace | refusal to admit, refusal to activate, namespace freeze or alias lockout | participant is denied entry into the public legitimacy surface itself |
| dashboard / shell / API | one hosted dashboard, one provider shell, one API gateway as ordinary path | a single operator can practically switch participation off |
| custody / exit | withdrawal refusal, balance hostage, custody lock-in | participant cannot exit or migrate despite nominal visibility |
| receipt / audit | refusal to publish or query receipts, machine access blocked behind one portal | public legitimacy cannot be independently checked or replayed |

`censorship_includes_denial_throttling_routing_namespace_custody_and_sequencing_surfaces`
`dashboard_provider_shell_and_hosted_api_chokepoints_are_in_scope`

## 5. Participant classes and harm model

Row 7 must protect more than one participant shape.

Affected classes include:
- agents participating directly in the protocol
- human operators acting through machine-legible tooling
- auditors and external verifiers
- migrating or exiting participants
- minority or dissenting participants contesting a legitimacy decision

The relevant harms are:
- inability to enter the public legitimacy surface
- inability to contest or refute
- inability to verify lineage or receipts
- inability to preserve continuity when moving away from a hostile operator path
- inability to replay public legitimacy state independently

## 6. Minimum anti-bottleneck interpretation for row 7

The minimum anti-bottleneck reading of row 7 is:
- one human operator may not be the ordinary source of public legitimacy access
- one dashboard may not be the ordinary source of public legitimacy access
- one provider-specific shell may not be the ordinary source of public
  legitimacy access
- one managed control plane may not be the ordinary place where admission,
  namespace, quorum, settlement, reputation, or receipts become effective

`one_operator_one_dashboard_one_provider_shell_not_acceptable_as_ordinary_public_legitimacy_posture`

Bounded bootstrap exception:
- Genesis-rooted lineage remains canonical
- Genesis-operated choke points may exist only where separately
  constitutionalized, documented, auditable, challengeable, and sunset-bound
- ordinary third-party dependence may not borrow Genesis bootstrap language as a
  loophole

## 7. What this artifact does not claim

This artifact does not claim:
- nation-state-proof censorship resistance is already implemented
- any specific substrate candidate already passes row 7
- row 7 runtime proof is complete at Phase 672
- row 5 privacy work is closed
- `CDL-062` is opened
