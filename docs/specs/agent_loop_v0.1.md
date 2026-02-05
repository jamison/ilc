# Agent Loop v0.1 (Prompt ⇄ Walkthrough)

**Version:** v0.1  
**Status:** Draft  
**Last Updated:** 2026-02-05

## Purpose
Establish a deterministic, low‑drift workflow between Codex (prompt author + review gate) and Antigravity (executor) using filesystem signals.

## High‑Level Loop
1) **Codex writes prompt** to `docs/antigravity_tasks/`.
2) **Antigravity waits** a configurable delay (e.g., 2–5 min), then executes the prompt.
3) **Antigravity writes walkthrough** to `docs/phases/`.
4) **Codex waits** a configurable delay (e.g., 2 min), then performs review gate:
   - read walkthrough
   - verify touched files
   - run required tests
   - fix ellipses / small issues
   - update STATUS/TODO
   - commit
5) **Codex drafts next prompt** and the loop repeats.

## Roles
- **Antigravity**: executes prompts, writes walkthroughs, runs initial tests.
- **Codex**: performs review gate and keeps repo consistent.
- **Human**: approval after each phase (optional but recommended).

## Guardrails
- **Phase scope**: one prompt at a time (no auto‑chaining).
- **Hard test gates**: phase‑specific tests + `tests/test_no_ellipses_in_walkthroughs.py`.
- **Auto‑halt** on failures (no next phase until resolved).
- **Stable output**: walkthrough requires commit hash filled post‑commit.

## Folder Signals
- **Prompt source**: `docs/antigravity_tasks/antigravity_prompt__phase_*.md`
- **Walkthrough source**: `docs/phases/phase_*_walkthrough.md`

## Delays (recommended defaults)
- **Prompt delay**: 2–5 minutes
- **Walkthrough delay**: 2 minutes

## Acceptance Criteria (per phase)
- Tests green
- Walkthrough updated and ellipses‑free
- STATUS/TODO updated
- Commit exists with correct hash in walkthrough

## Notes
- Avoid concurrent phase execution.
- If Antigravity or Codex can’t confirm file timestamps, pause for human review.
