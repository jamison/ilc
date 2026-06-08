# Idea-Descent Objective: Valid Phase Prompt for Window 1546p Initialization

**Objective ID:** phase_prompt_descent_window_1546p_init
**Evaluator:** tools/evaluators/phase_prompt_evaluator.py
**Candidate type:** ILC antigravity phase prompt (markdown)

## Goal

Produce a phase prompt for Phase 1546p-G10 (Window 1546p initialization) that:

1. Passes all `validate_phase_prompt.py` schema checks VALID
2. Has correct filename: `antigravity_prompt__phase_1546p_g10_<slug>.md`
3. Has correct H1: `# Phase 1546p-G10 — ...`
4. Contains all required structural sections:
   - §0a — Known-token audit (with term-binding table)
   - §0b — Concept-discovery search (with pre-execution claim table)
   - §0c — Contradiction and non-claim search
   - §0d — Source expansion (including MemPalace direct-read clause)
   - Mission
   - Scope
   - Required Inputs
   - Deliverables
   - Commands to Run
   - Walkthrough Requirements (with "No ellipses in walkthrough." rule)
   - Status Update Requirements
   - Commit Message
5. References `docs/phases/STATUS.md`
6. Does not overclaim: no production activation, no CDL mutation without authority

## Acceptance criterion

`validate_phase_prompt.py` exits 0 with output `VALID: <path>`.

## Non-goals

This descent loop does not evaluate semantic correctness of the prompt content,
only structural schema compliance. Content review is a separate human/Codex step.
