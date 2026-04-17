from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_706_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v4.5.md")
CLOSURE_GATE_PATH = Path("docs/specs/ilc_window_701_706_closure_gate_706_v0.1.md")
TEST_PATH = Path("tests/test_phase_706_coherence_capsule_v4_5_and_window_701_706_closure_gate.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_706_g8_coherence_report_capsule_v4_5_and_window_701_706_closure_gate_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
COHERENCE_HEADINGS = (
    "## 1. Window 701-706 summary",
    "## 2. Item-by-item disposition",
    "## 3. Runtime implications and non-ratifications",
    "## 4. Carry-forward into later windows",
    "## 5. Final coherence statement",
)
COHERENCE_TOKENS = (
    "window_701_706_coherence_report_complete",
    "w_e_disposition_confirmed_doctrine_lock",
    "bal_profile_disposition_confirmed_spec_or_contract_lock",
    "post_banking_disposition_confirmed_doctrine_lock",
    "inverted_ecu_disposition_confirmed_spec_or_contract_lock_plus_doctrine_preservation",
    "no_ratification_of_cdl_066_cdl_017_cdl_067_in_window_701_706",
)
CLOSURE_HEADINGS = (
    "## 1. Window identity and closure basis",
    "## 2. Mandatory checklist confirmation",
    "## 3. Disposition summary",
    "## 4. Non-ratifications and exclusions",
    "## 5. Carry-forward into 707+",
    "## 6. MemPalace refresh disposition",
)
CLOSURE_TOKENS = (
    "window_701_706_closure_gate_706_complete",
    "phase_701_705_outputs_confirmed",
    "economic_doctrine_items_no_longer_gray_zone",
    "window_707_plus_carry_forward_explicit",
)
PHASE_706_SUBJECT = ("phase 706", "coherence report capsule v4.5 and window 701-706 closure gate")
PHASE_706_BACKFILL_SUBJECT = ("phase 706", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
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
    raise AssertionError("phase_706_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_coherence_report_exists_and_contains_required_structure() -> None:
    text = _read(COHERENCE_PATH)
    positions = [text.index(heading) for heading in COHERENCE_HEADINGS]
    assert positions == sorted(positions)
    for token in COHERENCE_TOKENS:
        assert token in text


def test_capsule_v45_contains_required_frontier_lines_and_dispositions() -> None:
    text = _read(CAPSULE_PATH)
    assert "Capsule v4.5 supersedes v4.4." in text
    assert "Window 701-706 is now closed as the foundational economic doctrine and kernel calibration lane." in text
    assert "Window 707-712 is the next planned continuation." in text
    assert "`W_e = ΔH / E_cost` is now `doctrine_lock`" in text
    assert "BAL-profile kernel calibration is now `spec_or_contract_lock`" in text
    assert 'the "ILC is post-banking" frame is now `doctrine_lock`' in text
    assert "inverted-ECU runtime traceability is now `spec_or_contract_lock_plus_doctrine_preservation`" in text


def test_capsule_records_open_cdl_carry_forward_and_live_track_b_state() -> None:
    text = _read(CAPSULE_PATH)
    assert "`CDL-066` remains `open` and unratified" in text
    assert "`CDL-017` remains `open` and unratified" in text
    assert "`CDL-067` remains `open` and unratified" in text
    assert "Track B status: `M-010 binary_complete; M-011 planned; SEC-001 implementation closed; CDL-066 ratification still open on Track A`" in text


def test_closure_gate_exists_and_contains_required_structure() -> None:
    text = _read(CLOSURE_GATE_PATH)
    positions = [text.index(heading) for heading in CLOSURE_HEADINGS]
    assert positions == sorted(positions)
    for token in CLOSURE_TOKENS:
        assert token in text


def test_closure_gate_confirms_checklist_and_non_ratifications() -> None:
    text = _read(CLOSURE_GATE_PATH)
    assert "Phase `701` sequence lock published" in text
    assert "Phase `702` `W_e` note published" in text
    assert "Phase `703` calibration contract published" in text
    assert "Phase `704` post-banking note published" in text
    assert "Phase `705` inverted-ECU note published" in text
    assert "capsule v4.5 published" in text
    assert "no ratification of `CDL-066`, `CDL-017`, or `CDL-067` in this window" in text
    assert "ratify the full historical inverted-ECU / `CDL-053` package" in text


def test_decision_log_and_runtime_paths_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_706_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_706_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
    )
    if main_commit and backfill_commit:
        for commit_ref in (main_commit, backfill_commit):
            changed_paths = _changed_paths_for_commit(commit_ref)
            assert str(DECISION_LOG_PATH) not in changed_paths
            assert not any(
                path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths
            )
            assert not any(
                path == "ilc_consensus" or path.startswith("ilc_consensus/")
                for path in changed_paths
            )
        return

    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0

    result_ilc_core = subprocess.run(
        ["git", "diff", "--exit-code", "--", "ilc_core/"],
        capture_output=True,
        text=True,
    )
    assert result_ilc_core.returncode == 0

    result_ilc_consensus = subprocess.run(
        ["git", "diff", "--exit-code", "--", "ilc_consensus/"],
        capture_output=True,
        text=True,
    )
    assert result_ilc_consensus.returncode == 0


def test_phase_706_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_706_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_706_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_706_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
