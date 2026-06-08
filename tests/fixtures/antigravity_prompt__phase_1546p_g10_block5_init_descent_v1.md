# Phase 1546p-G10 — Block 5 Governance/Economic Edge Specs — Window Initialization

**Phase:** 1546p
**Window:** 1546p–1555p
**Date:** 2026-06-08
**Status:** pending
**Owner lane:** G10 private pre-public architecture

---

## Mission

Open Window 1546p and initialize the Block 5 governance/economic edge spec track.
Rebuild the MemPalace, refresh the open obligation register, and produce the
sequence lock for the window.

## Scope

This phase covers:
- MemPalace rebuild from current repo state
- OBL register refresh confirming OBL-023, OBL-024, OBL-028, OBL-029 remain open
- CDL-096 scope reconciliation (option A/B/C) — human decision point
- Sequence lock for Window 1546p–1555p

This phase does NOT:
- Open or ratify any CDL
- Write any runtime code
- Activate any production guard

## Required Inputs

- `docs/specs/ilc_window_1546p_1555p_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_open_obligation_register_v0.1.md`
- `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md`
- `docs/antigravity_context_capsule_v5.68p_private_block4b.md` (via MemPalace)

## Deliverables

1. `docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md` — new sequence lock
2. `docs/phases/phase_1546p_window_1546p_init_walkthrough.md` — phase walkthrough
3. Updated `docs/phases/STATUS.md` — mark Phase 1546p IN PROGRESS → COMPLETE
4. Updated `AGENTS.md` — reflect new window entry

## Commands to Run

```bash
bash tools/mempalace/build_active_working_set.sh
.venv/bin/python -m pytest tests/ -q --tb=short
python tools/check_sensitive_runtime_coding_taboos.py
```

## Walkthrough Requirements

Codex must:
- Read `docs/specs/ilc_window_1546p_1555p_candidate_phase_grouping_v0.1.md` in full
- Read `docs/specs/ilc_open_obligation_register_v0.1.md` and confirm OBL-023/024/028/029 status
- Read `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md` carry-forward section
- Search for all prior CDL-096 references
- Produce sequence lock artifact before any other deliverable
- Record tokens: `window_1546p_opened_phase_1546p`, `mempalace_rebuilt_phase_1546p`

No ellipses in walkthrough.

## Status Update Requirements

After each deliverable:
- Update `docs/phases/STATUS.md` with current phase status
- Emit the phase token for the completed deliverable

Tokens expected at completion:
- `window_1546p_opened_phase_1546p`
- `sequence_lock_phase_1546p_committed`
- `mempalace_rebuilt_phase_1546p`
- `obl_register_refreshed_phase_1546p`
