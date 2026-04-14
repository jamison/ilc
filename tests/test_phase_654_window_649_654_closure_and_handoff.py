from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

COHERENCE_REPORT_PATH = Path("docs/specs/ilc_window_649_654_runtime_coherence_report_654_v0.1.md")
CHECKLIST_JSON_PATH = Path("docs/specs/ilc_option_b_graduation_checklist_state_654_v0.1.json")
GATE_SCRIPT_PATH = Path("tools/run_window_649_654_runtime_closure_gate_phase_654.sh")
TEST_PATH = Path("tests/test_phase_654_window_649_654_closure_and_handoff.py")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v3.8.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_649_654_handoff_654_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_654_g8_window_649_654_closure_and_handoff_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_654_SUBJECT_TOKENS = ("phase 654", "window 649-654 closure and handoff")
PHASE_654_BACKFILL_SUBJECT_TOKENS = ("phase 654", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_REPORT_PATH),
    str(CHECKLIST_JSON_PATH),
    str(GATE_SCRIPT_PATH),
    str(TEST_PATH),
    str(CAPSULE_PATH),
    str(HANDOFF_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HANDOFF_HEADINGS = (
    "## 1. Window identity and closure basis",
    "## 2. Runtime touchpoint closure summary",
    "## 3. Option-B checklist delta for rows 1-4",
    "## 4. Remaining blockers and still-open rows 5-9",
    "## 5. Next constitutional target",
    "## 6. Routing after closure",
    "## 7. MemPalace refresh disposition",
)
REQUIRED_HANDOFF_TOKENS = (
    "window_649_654_handoff_654_closed",
    "window_649_654_runtime_lane_status_pass",
    "mvp_touchpoints_rows_1_through_4_runtime_closed_after_654",
    "rows_5_through_9_remain_open_after_654",
    "coupling_invariants_governance_lock_is_next_constitutional_target_after_654",
    "option_d_posture_active_after_654",
    "no_cdl_062_or_option_b_selection_in_654",
)


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


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
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
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_tokens}")


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f"commit_not_yet_present:{subject_tokens}")


def test_coherence_report_exists_and_records_runtime_lane_pass() -> None:
    text = _read(COHERENCE_REPORT_PATH)
    assert "window_649_654_runtime_lane_status_pass" in text
    assert "Window 649-654 passes as the concrete runtime/interface closure" in text


def test_checklist_state_json_exists_and_records_all_nine_rows() -> None:
    payload = json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))
    assert payload["artifact"] == "ilc_option_b_graduation_checklist_state_654_v0.1"
    assert payload["window"] == "649-654"
    assert payload["option_b_selected"] is False
    assert payload["option_d_active"] is True
    assert len(payload["rows"]) == 9


def test_handoff_exists_with_all_required_headings() -> None:
    text = _read(HANDOFF_PATH)
    for heading in REQUIRED_HANDOFF_HEADINGS:
        assert heading in text


def test_handoff_contains_all_required_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text


def test_handoff_records_rows_1_through_4_as_runtime_closed() -> None:
    payload = json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))
    statuses = {row["row"]: row["status"] for row in payload["rows"]}
    assert statuses["1. public init/admission flow tied to canonical receipts"] == "runtime_closed"
    assert statuses["2. machine-legible public receipt issuance and query/runtime contract"] == "runtime_closed"
    assert statuses["3. user and agent visible ECU to ILC lifecycle contract"] == "runtime_closed"
    assert statuses["4. public wallet surface contract sufficient for a first participant-touch economic loop"] == "runtime_closed"


def test_handoff_records_rows_5_through_9_as_still_open() -> None:
    payload = json.loads(CHECKLIST_JSON_PATH.read_text(encoding="utf-8"))
    statuses = {row["row"]: row["status"] for row in payload["rows"]}
    assert statuses["5. privacy-preserving public legitimacy mechanism at the settlement layer"] == "not_started"
    assert statuses["6. coupling invariants that keep protocol truth and graph legitimacy upstream of settlement backend choice"] == "partial"
    assert statuses["7. censorship-resistance requirement for public legitimacy surfaces"] == "partial"
    assert statuses["8. independence from external constitutional centers as a future-substrate selection criterion"] == "partial"
    assert statuses["9. transport and discovery operational maturity threshold for public participant use"] == "partial"


def test_handoff_names_next_constitutional_target_without_reserving_cdl_number() -> None:
    text = _read(HANDOFF_PATH)
    assert "coupling-invariants governance lock" in text
    assert "does not reserve or recommend a CDL number" in text
    assert "next available cdl" not in text.lower()
    assert "recommended cdl" not in text.lower()


def test_capsule_v3_8_exists_and_references_window_649_654_and_later_lane_blockers() -> None:
    text = _read(CAPSULE_PATH)
    assert "ILC Antigravity Context Capsule v3.8" in text
    assert "Window 649-654 is now closed as the concrete runtime/interface closure of the" in text
    assert "rows 1-4 of the Phase 611 Option-B graduation checklist are now" in text
    assert "coupling-invariants governance lock" in text
    assert "transport and discovery operational maturity" in text


def test_decision_log_unchanged_and_gate_script_is_executable_and_non_recursive() -> None:
    assert DECISION_LOG_PATH.is_file()
    script_text = _read(GATE_SCRIPT_PATH)
    assert GATE_SCRIPT_PATH.is_file()
    assert os.access(GATE_SCRIPT_PATH, os.X_OK)
    assert "tests/test_phase_650_public_init_admission_runtime.py" in script_text
    assert "tests/test_phase_651_public_receipt_runtime.py" in script_text
    assert "tests/test_phase_652_ecu_ilc_lifecycle_runtime.py" in script_text
    assert "tests/test_phase_653_public_wallet_runtime_integration.py" in script_text
    assert "tests/test_phase_654_window_649_654_closure_and_handoff.py" in script_text
    assert "run_window_649_654_runtime_closure_gate_phase_654.sh" not in script_text


def test_phase_654_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_654_SUBJECT_TOKENS)
    main_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_654_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_REQUIRED_MAIN_PATHS
    if _find_commit_ref(subject_tokens=PHASE_654_BACKFILL_SUBJECT_TOKENS) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_654_BACKFILL_SUBJECT_TOKENS}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_654_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(backfill_commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
