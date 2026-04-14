# ILC Option-B Remaining Rows Closure Criteria 661 v0.1

Status: closure-criteria sharpening artifact
Date: 2026-04-14
Phase: 661
Owner lane: G8 later-row sharpening sidecar

## 1. Purpose and status discipline

This artifact sharpens the remaining checklist rows into usable future-lane
criteria without pretending they are already solved.

`rows_5_7_8_9_sharpened_not_closed_in_661`
`row_5_remains_not_started_after_661`
`rows_7_8_9_remain_open_after_661`
`agent_suitability_and_machine_use_matter_for_opening_not_selection_only`
`row_9_evidence_families_locked_before_thresholds`
`row_9_thresholds_deferred_to_window_665_670`

Status discipline after Phase 661:
- row 5 remains `not_started`
- rows 7-9 remain open
- this phase improves future closure quality by naming evidence and routing,
  not by claiming closure

## 2. Row 5 closure criteria

Row 5 topic:
- privacy-preserving public legitimacy mechanism at the settlement layer

Closure criteria for row 5 should require:
- a narrowed threat model centered on correlation minimization and unlinkability
  for public submissions rather than "hide all private work"
- a candidate mechanism family that preserves public auditability and receipt
  lineage
- evidence that the mechanism does not destroy machine-legible participation
  or bounded human auditability
- simulation or red-team evidence on linkability leakage under realistic public
  participation patterns

Future-lane owner:
- Window 677-682, privacy-preserving public legitimacy prework

## 3. Row 7 closure criteria

Row 7 topic:
- censorship-resistance requirement for public legitimacy surfaces

Closure criteria for row 7 should require:
- an explicit threat model for denial, exclusion, throttling, and routing-level
  censorship against public legitimacy surfaces
- a clear minimum bar for participant exitability and replayability when
  censorship occurs
- a selection-criteria document that future substrate options must satisfy
- evidence that the chosen public legitimacy surfaces are not bottlenecked
  through one human operator, one dashboard, or one provider-specific shell

Future-lane owner:
- Window 671-676, censorship-resistance and independence criteria

## 4. Row 8 closure criteria

Row 8 topic:
- independence from external constitutional centers as a future-substrate
  selection criterion

Closure criteria for row 8 should require:
- an explicit definition of what counts as an external constitutional center
- exclusion criteria for later substrate families that make protocol
  legitimacy subordinate to an outside veto authority
- a decision record showing that future substrate selection criteria preserve
  protocol-side legitimacy roots
- evidence that agent participation and human auditability do not depend on one
  privileged external control plane

Future-lane owner:
- Window 671-676, censorship-resistance and independence criteria

## 5. Row 9 closure criteria

Row 9 topic:
- transport and discovery operational maturity threshold for public participant
  use

Closure criteria for row 9 should require:
- production-like multi-machine evidence rather than single-node reassurance
- proof that bounded metadata push remains bounded and that heavy canon/graph
  payloads remain pull-only and receiver-controlled
- evidence that churn, fallback, partition, and recovery paths are operational
  rather than theoretical
- operator-facing packaging and playbook evidence strong enough for public
  participant use

Future-lane owner:
- Window 665-670, transport and discovery maturity

## 6. Row 9 evidence starter pack

The future row-9 lane must produce this minimum starter pack:
- a multi-machine canary package
- a churn drill
- a partition/recovery drill
- an HTTP/2 fallback activation scenario
- static-peer bootstrap and operator playbook evidence
- a metrics-table template

The starter-pack purpose is to prevent the transport lane from reopening basic
questions about what evidence families are required.

## 7. Threshold work deferred to Window 665-670

The starter pack above is intentionally semi-prescriptive rather than fully
thresholded.

Window 665-670 must still decide:
- topology size
- run count
- success thresholds
- recovery budgets

These are deferred because they should be set against the first real canary
evidence, not guessed in advance inside the row-6 lane.

## 8. What this phase does not claim

This phase does not claim:
- row 5 is closed
- row 7 is closed
- row 8 is closed
- row 9 is closed
- the exact row-9 thresholds are already known
- the future substrate has already been selected
