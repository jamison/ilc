"""Phase 434 sequence-lock and runtime-tranche intake tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_434_440_sequence_lock_v0.1.md")
INTAKE_PATH = Path("docs/specs/ilc_window_434_runtime_tranche_intake_434_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_434_COMMIT_SUBJECT = "docs(g8): phase 434 window sequence lock and runtime tranche intake"

EXPECTED_PHASE_ROWS = (
    "| 1 | 434 | Sequence lock + runtime tranche intake freeze | Foundation / Control | SENSITIVE |",
    "| 2 | 435 | Runtime tranche I: peer fanout integration | Runtime | SENSITIVE |",
    "| 3 | 436 | Runtime tranche II: benchmark harness + tranche completion | Runtime / Tooling | SENSITIVE |",
    "| 4 | 437 | Runtime tranche findings memo and regression hardening | Review / Stabilization | NON-SENSITIVE |",
    "| 5 | 438 | Treasury P_e prerequisite-satisfaction review | Governance review | NON-SENSITIVE |",
    "| 6 | 439 | Coherence + capsule v1.8 | Synthesis | NON-SENSITIVE |",
    "| 7 | 440 | Closure gate + next-window handoff | Gate | SENSITIVE |",
)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_434_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(SEQUENCE_LOCK_PATH),
        str(INTAKE_PATH),
        "tests/test_phase_434_window_434_440_sequence_lock_and_runtime_tranche_intake.py",
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_434_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_434_commit_subject_present_but_no_qualifying_commit")
    raise AssertionError("phase_434_commit_not_present_in_local_history")


def test_sequence_lock_exists_and_contains_required_headings_and_tokens() -> None:
    text = SEQUENCE_LOCK_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Window identity and scope",
        "## 2. Inputs and closure inheritance",
        "## 3. Runtime tranche authorization and release-engineering separation",
        "## 4. Locked phase table (434-440 baseline)",
        "## 5. Treasury P_e prerequisite-review boundary",
        "## 6. Extension rule for 441+",
        "## 7. Sensitivity mapping and merge-timing rule",
        "## 8. Canonical anchors and non-goals",
    ):
        assert heading in text
    for token in (
        "Window 434+ is the Runtime Tranche and Treasury P_e Prerequisite Review Block.",
        "This baseline locks a 7-phase window: 434-440.",
        "CDL-050 is not pre-authorized at Phase 434 entry.",
        "Window 434+ may advance the Treasury P_e constitutional lane only after satisfying at least one Phase 431 prerequisite.",
        "Release engineering packaging/bootstrap remains a parallel administrative track and does not consume numbered phases in this baseline.",
        "Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.",
        "Phase 438 is a non-ratifying Treasury P_e prerequisite-satisfaction review.",
        "Any move to Phases 441+ requires an explicit sequence-lock amendment after Phase 438.",
    ):
        assert token in text


def test_runtime_tranche_intake_exists_and_contains_required_headings_and_tokens() -> None:
    text = INTAKE_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Purpose and intake boundary",
        "## 2. Release-track source anchor",
        "## 3. Frozen runtime-tranche import set",
        "## 4. Merge-timing rule and packaging separation",
        "## 5. Treasury P_e independence and non-goals",
        "## 6. Canonical anchors and next-phase pointer",
    ):
        assert heading in text
    for token in (
        "These files are the only Phase-434-authorized release-track import candidates for the numbered runtime tranche baseline.",
        "Release-track source anchor: docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md",
        "ilc_core/network/peer.py",
        "ilc_core/cli/main.py",
        "ilc_core/node/node_dissemination_runtime_362.py",
        "tools/runtime_baseline.py",
        "Public export staging, allowlist updates, bootstrap method, and packaging checklists remain on the release-engineering administrative track.",
        "CDL-050 remains unopened and unaffected by Phase 434.",
        "Phase 435 and Phase 436 may import runtime-tranche content only from this frozen set unless a later amendment expands it.",
        "Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.",
        "Runtime tranche imports must land on main with identifiable runtime commit messages and must not arrive as a bulk packaging merge.",
    ):
        assert token in text


def test_sequence_lock_phase_table_contains_exact_434_440_baseline() -> None:
    text = SEQUENCE_LOCK_PATH.read_text(encoding="utf-8")
    for row in EXPECTED_PHASE_ROWS:
        assert row in text


def test_decision_log_inventory_still_shows_cdl_049_ratified_and_cdl_050_absent() -> None:
    rows = parse_decision_register_rows(DECISION_LOG_PATH.read_text(encoding="utf-8"))
    assert rows["CDL-049"]["status"] == "ratified"
    assert "CDL-050" not in rows


def test_phase_434_docs_keep_packaging_outside_numbered_window() -> None:
    sequence_text = SEQUENCE_LOCK_PATH.read_text(encoding="utf-8")
    intake_text = INTAKE_PATH.read_text(encoding="utf-8")
    assert "packaging/bootstrap remains outside numbered phases" in sequence_text
    assert "release-engineering administrative track" in intake_text
    assert "no public packaging merge" in intake_text


def test_phase_434_commit_did_not_mutate_decision_log() -> None:
    commit_ref = _resolve_phase_434_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_434_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_434_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
