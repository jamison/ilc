# ILC Phase 801-804 Sequence Lock — Verification Tooling Scoping Window

**Window:** 801-804
**Date:** 2026-04-23
**Status:** locked
**Author:** Local architectural reviewer

`verification_tooling_scoping_window_801_804_locked`
`no_cdl_mutation_in_window_801_804`
`no_option_b_selection_in_window_801_804`
`window_purpose=discharge_option_b_verification_tooling_condition_via_design_artifacts`

---

## 1. Purpose and Scope

This window produces the design artifacts necessary to discharge the
`verification_tooling_delivery_before_public_deployment` condition recorded in
Phase 785, Phase 786, Phase 788, and Phase 789.

That condition was attached because Phase 693 named a missing
"operator-facing verification CLI for DAG graph traversal" as the one
remaining practical obstacle to Pattern 5 (`external_constitutional_center_and_exclusion_matrix_673`) receiving a clean DOES NOT APPLY verdict. Until verification tooling exists, non-expert
public auditability relies on trusting the operator who ran the node.

This window does NOT implement the tooling. It scopes, designs, and
specifies the tooling precisely enough that a Codex implementation window
can follow without further design decisions.

---

## 2. Pre-Locked Decisions

Three decisions are locked before Phase 802 executes, to prevent scope drift.

### Decision 1: Minimum-Viable vs. Full Condition Discharge

The condition `verification_tooling_delivery_before_public_deployment`
will be interpreted as a **two-tier obligation**:

- **Tier 1 (minimum viable, required before public deployment):**
  Anyone holding an LMDB export and the genesis.json can
  cryptographically verify that the epoch chain is authentic — not merely
  structurally complete. This requires BLS aggregate signature verification
  against the validator public keys declared in genesis.

- **Tier 2 (full audit depth, deferred to post-deployment implementation):**
  An archive node mode that preserves full DAG vertex history (the
  round-by-round gossip graph) enabling deep censorship-resistance audit
  by expert third parties. This is not required before first public
  deployment; it is required before a production security audit engagement.

`verification_tooling_tier1=bls_verified_epoch_chain`
`verification_tooling_tier2=dag_vertex_archive_mode`
`tier1_required_before_public_deployment`
`tier2_required_before_production_security_audit`

### Decision 2: Scope of This Window

This window produces:

1. A gap analysis artifact (Phase 802): exact characterization of what
   `state_extractor` covers vs. what Tier 1 and Tier 2 require.
2. A CLI design specification (Phase 803): the `ilc_dag_audit` binary —
   commands, input contract, output schema, verification algorithm,
   and LMDB read path. Archive mode design is included as a Tier-2
   appendix.
3. A closure gate (Phase 804): records the condition discharge scope,
   produces a hand-off package for the Codex implementation window.

This window does NOT produce:
- Rust implementation of the CLI
- Tests for the CLI
- A new Codex sequence lock for the implementation window (that is Phase
  804's output, not an in-window deliverable)

`window_produces_design_artifacts_not_implementation`

### Decision 3: Relation to `state_extractor`

The Tier-1 verification CLI is a **new binary** (`ilc_dag_audit`), not an
extension of `state_extractor`. Rationale:

- `state_extractor` is scoped to M-016 Workload D (replayability), has its
  own exit-code contract, and its description in the M-022 handoff is stable.
  Changing its behavior would require updating test expectations across
  multiple M-phase test files.
- `ilc_dag_audit` has a distinct purpose (public auditability) and should
  carry its own versioned output schema independent of the replayability
  workload contract.
- Both binaries read the same `epoch_records` LMDB; they are complementary,
  not overlapping.

`ilc_dag_audit_is_new_binary_not_extension_of_state_extractor`

---

## 3. Phase Map

| Phase | Title | Deliverable |
|---:|---|---|
| 801 | Sequence lock acknowledgment | This document |
| 802 | Gap analysis: state_extractor vs. audit requirement | `ilc_verification_tooling_gap_analysis_802_v0.1.md` |
| 803 | CLI design specification: `ilc_dag_audit` | `ilc_dag_audit_cli_design_803_v0.1.md` |
| 804 | Closure gate and Codex hand-off package | Phase 804 walkthrough + `phase_804_window_801_804_verdict` |

---

## 4. Non-Claims

This window does not claim:

- that Option B is selected,
- that the verification tooling condition is discharged by design artifacts
  alone (implementation must follow),
- that human authorization for Option B is implied or imminent,
- that Tier-2 archive mode is in scope for the first public deployment.
