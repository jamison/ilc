from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


HANDOFF_PATH = Path("docs/specs/ilc_window_642_648_handoff_648_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v3.7.md")
PHASE_TEST_PATH = Path("tests/test_phase_648_window_642_648_closure_and_handoff.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_648_g8_window_642_648_closure_and_handoff_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")

PHASE_648_SUBJECT = "phase 648 window 642-648 closure and handoff"
PHASE_648_BACKFILL_SUBJECT = "phase 648 walkthrough and status backfill"

EXACT_MAIN_PATHS = {
    str(HANDOFF_PATH),
    str(CAPSULE_PATH),
    str(PHASE_TEST_PATH),
}
EXACT_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Window identity and closure basis",
    "## 2. Security issue summary",
    "## 3. Fix-induced regression summary",
    "## 4. Remaining-float carry-forward state",
    "## 5. Routing after closure",
    "## 6. MemPalace refresh disposition",
)
REQUIRED_TOKENS = (
    "window_642_648_handoff_648_closed",
    "window_642_648_closed_without_new_constitutional_vehicle",
    "live_security_boundary_issues_touched_in_642_648_closed",
    "remaining_float_follow_on_inventory_persists_after_648",
    "window_623_plus_priority_preserved_after_648",
    "option_d_posture_active_after_648",
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


def _find_commit_ref(subject_token: str) -> str | None:
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
        if subject_token in subject.lower():
            return commit_hash
    return None


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_handoff_exists_with_all_required_headings() -> None:
    text = _read(HANDOFF_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_handoff_contains_all_required_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_handoff_records_first_order_security_issues_closed() -> None:
    text = _read(HANDOFF_PATH)
    for required_line in (
        "canonical JSON/signature drift on the touched bundle, report, and CLI",
        "predictable PRNG usage on the touched runtime/security-sensitive selection",
        "unbounded NDJSON bundle aggregation on the touched ingress path",
        "flat timeout defaults on the touched HTTP wrappers",
    ):
        assert required_line in text


def test_handoff_records_fix_induced_regression_checks() -> None:
    text = _read(HANDOFF_PATH)
    for required_line in (
        "whitespace or separator drift",
        "new entropy-heavy runtime dependency",
        "new broad exception swallowing",
        "temporary-disk spooling",
        "recursive self-invocation",
    ):
        assert required_line in text


def test_handoff_records_remaining_float_carry_forward_state() -> None:
    text = _read(HANDOFF_PATH)
    assert "ilc_remaining_float_and_security_follow_on_inventory_643_v0.1.md" in text
    assert "TODO.txt" in text
    assert "shared/public contract float cleanup remains open in later lanes" in text


def test_capsule_v3_7_exists_and_references_window_642_648_and_surviving_follow_ons() -> None:
    text = _read(CAPSULE_PATH)
    assert "Capsule v3.7 supersedes v3.6." in text
    assert "Window 642-648 is closed as the bounded security boundary and remaining-float" in text
    assert "broader float cleanup outside the bounded 642-648 target set" in text
    assert "broader security hardening outside the bounded 642-648 touched paths" in text
    assert "Window 623+ remains the next broader runtime/interface continuation." in text


def test_decision_log_unchanged_in_main_commit() -> None:
    _require_commit_or_skip(PHASE_648_SUBJECT)
    commit_ref = _find_commit_ref(PHASE_648_SUBJECT)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_648_SUBJECT)
    _require_commit_or_skip(PHASE_648_BACKFILL_SUBJECT)
    main_commit_ref = _find_commit_ref(PHASE_648_SUBJECT)
    backfill_commit_ref = _find_commit_ref(PHASE_648_BACKFILL_SUBJECT)
    assert main_commit_ref is not None
    assert backfill_commit_ref is not None
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_MAIN_PATHS
    assert _changed_paths_for_commit(backfill_commit_ref) == EXACT_BACKFILL_PATHS
