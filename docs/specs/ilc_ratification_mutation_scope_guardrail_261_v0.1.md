# ILC Ratification Mutation Scope Guardrail 261 v0.1

Status: Phase-261 infrastructure artifact
Date: 2026-02-22
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define a reusable guardrail that enforces field-bounded CDL row mutation during ratification phases.

This guardrail is a prerequisite for 260+ ratification lanes and exists to prevent unintended decision-log drift during governance mutations.

## 2. Allowed mutation fields

Only the following fields may change during ratification row mutation:
- `status`
- `ratified_phase`
- `ratified_date`
- `evidence_document`

Any other field change is unauthorized and must fail the verification lane.

## 3. Comparison algorithm and row identity rules

The guardrail compares two versions of the constitutional decision log:
1. Parse Decision Register rows by `decision_id`.
2. Parse extra ratification cells (`ratified_phase: ...`) into normalized key-value fields.
3. Enforce register identity equality (same CDL IDs before/after comparison).
4. Locate target CDL row in both versions.
5. Compute changed field set and subtract allowed mutation fields.
6. Fail if any unauthorized fields remain.

Row identity rules:
- Missing target CDL row in old or new register is a hard failure.
- Additional or removed CDL IDs between old/new registers is a hard failure.
- Positional row alignment is not used.

## 4. Negative-path examples

Forbidden drift example:
- Target: `CDL-032`
- Change applied: `current_candidate` text normalized during ratification
- Result: fail with deterministic unauthorized field message containing `current_candidate`.

Forbidden identity drift examples:
- Added synthetic `CDL-999` row in new register.
- Removed target row in new register.

Both fail before mutation-scope evaluation completes.

## 5. Usage pattern for future ratification phases

Recommended usage in a ratification test:
1. Snapshot pre-mutation decision-log content.
2. Apply ratification edit for one target CDL row.
3. Call `assert_only_allowed_row_mutations(pre, post, cdl_id="CDL-xxx")`.
4. Keep `enforce_register_identity=True` for ratification lanes.

This check is additive to phase-local ratification evidence tests and gate scripts.

## 6. Non-goals

This guardrail does not:
- ratify any CDL,
- validate economic parameter correctness,
- validate evidence sufficiency,
- alter `ilc_core` runtime behavior.

## 7. Canonical anchors

- `docs/specs/ilc_cdl_ratification_window_250_258_handoff_v0.1.md`
- `docs/specs/ilc_phase_260_269_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md`
- `docs/phases/review_methodology_refinement_opus_feedback_2026_02_21.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
