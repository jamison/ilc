# Phase 1546p-G10 — Block 5 Governance/Economic Edge Specs — Window Initialization

**Phase:** 1546p
**Window:** 1546p–1555p
**Date:** 2026-06-08
**Status:** pending
**Owner lane:** G10 private pre-public architecture

---

## §0 — Pre-Execution Checks

### §0a — Known-token audit

**Input tokens (must already exist before this phase runs):**

| Token | Source |
|---|---|
| `window_1538p_closed_phase_1545p` | `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md` |
| `go_window_1546p_required_next` | `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md` |
| `block_4_all_obligations_closed_phase_1545p` | `docs/specs/ilc_open_obligation_register_v0.1.md` |

**Output tokens (must NOT yet exist before this phase executes):**

| Token | Will be created by |
|---|---|
| `window_1546p_opened_phase_1546p` | Sequence lock artifact |
| `sequence_lock_phase_1546p_committed` | Sequence lock artifact |
| `mempalace_rebuilt_phase_1546p` | MemPalace rebuild step |

**Term bindings:**

| Term used in this phase | Canonical meaning | Do NOT use to mean |
|---|---|---|
| node | Graph Node (content-addressed epistemic object) | serving peer, host, operator instance |
| CDL-096 | CDL reserved for Werner/global-tier scope (TBD option A/B/C) | any already-ratified CDL |
| Block 5 | OBL-023/024/028/029 governance/economic edge specs | Block 4 economic finality work |
| sequence lock | `docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md` | any prior window's sequence lock |

### §0b — Concept-discovery search

Search for the following before executing any deliverable:

1. `grep -r "CDL-096" docs/` — confirm current CDL-096 scope status
2. `grep -r "OBL-023\|OBL-024\|OBL-028\|OBL-029" docs/specs/ilc_open_obligation_register_v0.1.md`
3. `grep -r "go_window_1546p" docs/` — confirm the authorization token exists

**Pre-execution claim table:**

| Claim | File to check | Expected result |
|---|---|---|
| `go_window_1546p_required_next` exists | `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md` | Token present in §closure tokens |
| OBL-023 is open | `docs/specs/ilc_open_obligation_register_v0.1.md` | Row present, status=open |
| OBL-024 is open | `docs/specs/ilc_open_obligation_register_v0.1.md` | Row present, status=open |
| CDL-096 scope is unresolved | `docs/specs/ilc_window_1546p_1555p_candidate_phase_grouping_v0.1.md` | Option A/B/C not yet selected |

If MemPalace is used, direct-read every returned path.

### §0c — Contradiction and non-claim search

Search for:
- `deferred`, `blocked`, `not authorized`, `prelocked`, `superseded` near CDL-096
- `must not` near window 1546p authorization
- `public_path_remains_blocked` — confirm still active in Block 4 closure artifacts

Any hit that contradicts window opening must be surfaced before proceeding.

### §0d — Source expansion and newly discovered tokens

After §0b/§0c searches, direct-read:
- `docs/specs/ilc_window_1546p_1555p_candidate_phase_grouping_v0.1.md` §CDL-096
- `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md` §5 (next-window entry criteria)
- `docs/specs/ilc_pre_public_rc_no_deferral_strike_force_forward_plan_v0.1.md` Block 5 rows

Extract any newly discovered open tokens, blockers, or invariants before drafting deliverables.

If MemPalace is used, direct-read every returned path.

---

## Mission

Open Window 1546p and initialize the Block 5 governance/economic edge spec track.
Rebuild the MemPalace, refresh the open obligation register, and produce the
sequence lock for the window.

## Scope

This phase covers:
- MemPalace rebuild from current repo state
- OBL register refresh confirming OBL-023, OBL-024, OBL-028, OBL-029 remain open
- CDL-096 scope reconciliation (option A/B/C) — human decision point, recorded not resolved
- Sequence lock for Window 1546p–1555p

This phase does NOT:
- Open or ratify any CDL
- Write any runtime code
- Activate any production guard
- Pre-decide the CDL-096 scope option without human GO

## Required Inputs

- `docs/specs/ilc_window_1546p_1555p_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_open_obligation_register_v0.1.md`
- `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md`
- `docs/specs/ilc_pre_public_rc_no_deferral_strike_force_forward_plan_v0.1.md`
- `docs/PLANNING_INDEX.md`

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
- Perform all §0a-§0d checks before any deliverable
- Read `docs/specs/ilc_window_1546p_1555p_candidate_phase_grouping_v0.1.md` in full
- Read `docs/specs/ilc_open_obligation_register_v0.1.md` and confirm OBL-023/024/028/029 status
- Read `docs/specs/ilc_window_1538p_1545p_handoff_1545p_v0.1.md` carry-forward section
- Search for all prior CDL-096 references before writing the sequence lock
- Produce sequence lock artifact before any other deliverable
- Record tokens: `window_1546p_opened_phase_1546p`, `sequence_lock_phase_1546p_committed`

No ellipses in walkthrough.

Reference `docs/phases/STATUS.md` for current frontier status before updating.

## Status Update Requirements

After each deliverable:
- Update `docs/phases/STATUS.md` with current phase status
- Emit the phase token for the completed deliverable

Tokens expected at completion:
- `window_1546p_opened_phase_1546p`
- `sequence_lock_phase_1546p_committed`
- `mempalace_rebuilt_phase_1546p`
- `obl_register_refreshed_phase_1546p`

## LMDB Node Registration

This fixture models the current prompt schema. Any new files created by the
phase must be registered as candidate LMDB nodes in the same commit or the
walkthrough must record that no new LMDB-eligible files were created.

## Commit Message

```
phase(1546p): Window 1546p initialization — sequence lock + MemPalace rebuild

Window 1546p-1555p opened. Block 5 governance/economic edge spec track
initialized. Sequence lock committed. OBL-023/024/028/029 confirmed open.
CDL-096 scope reconciliation (A/B/C) recorded as pending human decision.

Tokens: window_1546p_opened_phase_1546p, sequence_lock_phase_1546p_committed,
mempalace_rebuilt_phase_1546p, obl_register_refreshed_phase_1546p
```
