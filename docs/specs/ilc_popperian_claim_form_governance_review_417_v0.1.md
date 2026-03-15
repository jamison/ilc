# ILC Popperian Claim-Form Governance Review 417 v0.1

Status: Phase-417 governance review artifact  
Date: 2026-03-15  
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

Phase 417 is a non-ratifying governance review and does not open, amend, or ratify any CDL row.

This artifact reviews whether bounded-existential Popperian claim-form compliance introduces any
blocking defects into the current-window economic lanes. Scope is limited to the ratification-bound
language and dependency surfaces consumed by `CDL-047` and `CDL-048`, plus the already-ratified
`CDL-V7` runtime and governance texts that are the forward source of the bounded-existential issue.

## 2. Review corpus and methodology

The review standard is bounded-existential Popperian claim-form compliance, applied to current-window economic CDLs and relevant governance/runtime anchors.

Review corpus:
- `docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md`
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md`
- `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`
- `ilc_core/consensus/popperian_gate_runtime.py`

Method:
1. inspect the current-window prelock artifacts for unbounded existential formulations,
2. inspect the active `CDL-V7` governance and runtime surfaces for the currently admitted claim-form vocabulary,
3. apply the Phase-417 blocking rule from the Window 414-423 sequence lock,
4. classify any issue as `CDL-047`/`CDL-048` blocking or as a cross-window non-blocking obligation.

## 3. Window-414 blocking-rule application summary

Phase 417 applies the locked Window-414 blocking rule directly:
- `CRITICAL` findings specific to `CDL-047` or `CDL-048` would block ratification until the corresponding prelock is patched and re-reviewed,
- `CRITICAL` or `MODERATE` findings outside `CDL-047` and `CDL-048` become Window 424+ obligations.

No CDL-047-specific or CDL-048-specific CRITICAL findings were identified; Phase 418 and Phase 419 are not blocked by Phase 417.

## 4. CDL-047 bounded-existential review result

CDL-047 review verdict: CLEAN.

`CDL-047` is a bounded governance-parameter lane. Its prelock artifact fixes a treasury-governance
candidate, rejects two alternatives, and records bounded calibration anchors (`bounty_cap = 0.15 x B_e`,
`burn_floor = 0.05`, `velocity_alert_floor = 0.91`). It does not rely on an unbounded existential
claim form, because the lane concerns constitutional policy parameters and ratification readiness
constraints rather than free-form epistemic submissions.

The Popperian concern therefore does not attach to the text of `CDL-047` itself.

## 5. CDL-048 bounded-existential review result

CDL-048 review verdict: CLEAN.

`CDL-048` is a bounded lifecycle-deadline lane. Its prelock artifact fixes a governed conversion
deadline (`ecu_conversion_deadline = 4 issuance epochs`), anti-hoarding rationale, and explicit
non-goals. It does not rely on an unbounded existential claim form, because the lane specifies a
bounded lifecycle transition rule rather than an open-ended epistemic claim about the existence of
some unconstrained class of objects or events.

The Popperian concern therefore does not attach to the text of `CDL-048` itself.

## 6. Cross-window Popperian finding outside CDL-047 and CDL-048

MODERATE finding: CDL-V7 runtime and supporting governance text admit existential claim forms without an explicit bounded-existential qualifier.

The exact runtime vocabulary issue is narrow and identifiable:
- `ilc_core/consensus/popperian_gate_runtime.py` currently includes `_ADMISSIBLE_CLAIM_FORMS = {"singular", "existential", "falsifiable_positive"}`,
- `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md` preserves corpus and rubric language that still refers to singular and existential forms,
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md` likewise discusses singular and existential forms without the stricter bounded-existential qualifier now required by the Window 414+ carry-forward.

This is a real governance and runtime wording gap, but it is not a `CDL-047` or `CDL-048` defect.

## 7. Window-424+ disposition and CDL-049 forward pointer

Recommended disposition: designate CDL-049 as the first constitutional planning lane of Window 424+ to resolve bounded-existential claim-form wording and runtime tokenization.

This finding is outside CDL-047 and CDL-048 and therefore does not block Window 414-423 execution under the Phase-417 blocking rule.

CDL-049 is not opened in Phase 417 and remains a Window 424+ planning obligation only.

The proper follow-on is a constitutional and runtime alignment lane that narrows `existential` to a
bounded-existential form, updates the corresponding review corpus language, and then propagates the
revised tokenization into any later ratifying or runtime phases that consume `CDL-V7` semantics.

## 8. Non-goals and canonical anchors

Non-goals:
- no mutation to `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no patching of `docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md`,
- no patching of `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md`,
- no runtime mutation under `ilc_core/`,
- no opening of `CDL-049` in this phase.

Canonical anchors:
- `docs/specs/ilc_phase_414_423_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_402_413_handoff_413_v0.1.md`
- `docs/specs/ilc_cdl_047_treasury_governance_prelock_hardening_415_v0.1.md`
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_prelock_hardening_416_v0.1.md`
- `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`
- `ilc_core/consensus/popperian_gate_runtime.py`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
