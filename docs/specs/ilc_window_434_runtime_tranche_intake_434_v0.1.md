# ILC Window 434 Runtime Tranche Intake 434 v0.1

Status: Phase-434 runtime-tranche intake artifact
Date: 2026-03-17
Owner lane: G8 Constitution Cluster A

## 1. Purpose and intake boundary

Phase 434 freezes the authorized runtime-tranche import candidates for the numbered Window 434+ baseline without importing or executing any runtime code.

These files are the only Phase-434-authorized release-track import candidates for the numbered runtime tranche baseline.

## 2. Release-track source anchor

Release-track source anchor: docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md

The frozen runtime-tranche set in this artifact is derived from the release-track runtime handoff and the associated merge note that separates runtime changes from packaging work.

## 3. Frozen runtime-tranche import set

Frozen Phase-434-authorized runtime-tranche import set:
- `ilc_core/network/peer.py`
- `ilc_core/cli/main.py`
- `ilc_core/node/node_dissemination_runtime_362.py`
- `tools/runtime_baseline.py`

Phase 435 and Phase 436 may import runtime-tranche content only from this frozen set unless a later amendment expands it.

## 4. Merge-timing rule and packaging separation

Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.

Runtime tranche imports must land on main with identifiable runtime commit messages and must not arrive as a bulk packaging merge.

Public export staging, allowlist updates, bootstrap method, and packaging checklists remain on the release-engineering administrative track.

## 5. Treasury P_e independence and non-goals

CDL-050 remains unopened and unaffected by Phase 434.

Treasury `P_e` carry-forward review remains deferred to Phase 438 and is independent of the Phase-434 intake freeze.

Non-goals:
- no runtime code import,
- no decision-log mutation,
- no public packaging merge,
- no rewrite of release-engineering policy.

## 6. Canonical anchors and next-phase pointer

Canonical anchors:
- `docs/specs/ilc_phase_434_440_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_424_433_handoff_433_v0.1.md`
- `docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md`
- `../ILC_release_track/docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md`

Next-phase pointer: Phase 435 is the next authorized phase.
