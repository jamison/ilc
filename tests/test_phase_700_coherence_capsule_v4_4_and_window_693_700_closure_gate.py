from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_REPORT_PATH = Path("docs/specs/ilc_coherence_report_700_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.4.md")
CLOSURE_GATE_PATH = Path("docs/specs/ilc_window_693_700_closure_gate_700_v0.1.md")
TEST_PATH = Path("tests/test_phase_700_coherence_capsule_v4_4_and_window_693_700_closure_gate.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_700_g8_coherence_report_capsule_v4_4_and_window_693_700_closure_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
COHERENCE_HEADINGS = (
    "## 1. Window 693-700 summary",
    "## 2. Opened constitutional lanes",
    "## 3. Row-5 row-7 row-8 disposition coherence",
    "## 4. Track B implementation status",
    "## 5. Carry-forward into 701+",
)
COHERENCE_TOKENS = (
    "CDL-066 opened in Phase 694.",
    "CDL-017 opened in Phase 695.",
    "CDL-067 opened in Phase 696.",
    "No ratification of CDL-066, CDL-017, or CDL-067 occurred in Window 693-700.",
    "Mysticeti remains Tier 1 primary, not the final production selection.",
    "SEC-001 implementation is closed at Window 693-700 close; CDL-066 ratification remains open.",
)
CAPSULE_SECTION_1_LINES = (
    "Capsule v4.4 supersedes v4.3.",
    "Window 693-700 is now closed as the chosen-substrate legitimacy closure lane.",
    "Window 701+ is the next planned continuation.",
)
CLOSURE_GATE_HEADINGS = (
    "## 1. Window identity and closure basis",
    "## 2. Mandatory checklist confirmation",
    "## 3. Row disposition summary",
    "## 4. Track B status and non-authorizations",
    "## 5. Carry-forward into 701+",
    "## 6. MemPalace refresh disposition",
)
CLOSURE_GATE_TOKENS = (
    "window_693_700_closure_gate_700_complete",
    "cdl_066_017_067_openings_confirmed_in_decision_log",
    "track_b_m008_complete_sec_001_implementation_closed_m009_unblocked",
    "window_701_plus_carry_forward_explicit",
)
PHASE_700_SUBJECT = (
    "phase 700",
    "coherence report capsule v4.4 and window 693-700 closure gate",
)
PHASE_700_BACKFILL_SUBJECT = ("phase 700", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_REPORT_PATH),
    str(CAPSULE_PATH),
    str(CLOSURE_GATE_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError("phase_700_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_coherence_report_exists_with_required_headings_and_tokens() -> None:
    text = _read(COHERENCE_REPORT_PATH)
    positions = [text.index(heading) for heading in COHERENCE_HEADINGS]
    assert positions == sorted(positions)
    for token in COHERENCE_TOKENS:
        assert token in text


def test_capsule_v44_exists_and_contains_required_section_1_lines() -> None:
    text = _read(CAPSULE_PATH)
    for line in CAPSULE_SECTION_1_LINES:
        assert line in text


def test_capsule_v44_records_row_5_row_7_and_row_8_dispositions() -> None:
    text = _read(CAPSULE_PATH)
    assert "row 5 is now `spec_closed_runtime_pending`" in text
    assert "row 7 is now `spec_closed_runtime_pending`" in text
    assert "row 8 remains `closed` and was reconfirmed in sovereign Mysticeti mode" in text
    assert "`CDL-066` is now `open`" in text
    assert "`CDL-017` is now `open`" in text
    assert "`CDL-067` is now `open`" in text


def test_closure_gate_exists_with_required_headings_and_tokens() -> None:
    text = _read(CLOSURE_GATE_PATH)
    positions = [text.index(heading) for heading in CLOSURE_GATE_HEADINGS]
    assert positions == sorted(positions)
    for token in CLOSURE_GATE_TOKENS:
        assert token in text


def test_closure_gate_checklist_confirms_cdl_066_017_and_067() -> None:
    text = _read(CLOSURE_GATE_PATH)
    assert "| `CDL-066` opened | confirmed |" in text
    assert "| `CDL-017` opened | confirmed |" in text
    assert "| `CDL-067` opened | confirmed |" in text
    assert "| decision-log rows present | confirmed |" in text


def test_closure_gate_records_track_b_status_with_current_truth() -> None:
    text = _read(CLOSURE_GATE_PATH)
    assert "M-008 complete" in text
    assert "SEC-001 implementation closed" in text
    assert "M-009 unblocked" in text


def test_decision_log_is_not_mutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_700_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_700_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
    )
    if main_commit and backfill_commit:
        for commit_ref in (main_commit, backfill_commit):
            changed_paths = _changed_paths_for_commit(commit_ref)
            assert str(DECISION_LOG_PATH) not in changed_paths
        return

    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_no_ilc_core_or_ilc_consensus_paths_are_mutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_700_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_700_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
    )
    if main_commit and backfill_commit:
        for commit_ref in (main_commit, backfill_commit):
            changed_paths = _changed_paths_for_commit(commit_ref)
            assert not any(
                path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths
            )
            assert not any(
                path == "ilc_consensus" or path.startswith("ilc_consensus/")
                for path in changed_paths
            )
        return

    result_ilc_core = subprocess.run(
        ["git", "diff", "--exit-code", "--", "ilc_core/"],
        capture_output=True,
        text=True,
    )
    assert result_ilc_core.returncode == 0


def test_phase_700_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_700_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_700_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_700_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
