from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

COHERENCE_PATH = Path("docs/specs/ilc_window_624_630_coherence_report_630_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v3.4.md")
HANDOFF_PATH = Path("docs/specs/ilc_window_624_630_handoff_630_v0.1.md")
PHASE_TEST_PATH = Path("tests/test_phase_630_window_624_630_coherence_and_closure.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_630_g8_window_624_630_coherence_and_closure_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_630_SUBJECT = "phase 630 window 624-630 coherence report capsule and handoff"
PHASE_630_BACKFILL_SUBJECT = "phase 630 walkthrough and status backfill"
EXPECTED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(HANDOFF_PATH),
    str(PHASE_TEST_PATH),
}
EXPECTED_BACKFILL_PATHS = {
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


def _find_commit_ref(*, subject_token: str) -> str | None:
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
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def _resolve_commit_ref(*, subject_token: str) -> str:
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
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def test_coherence_report_has_required_headings_and_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Window synthesis",
        "## 2. CDL-063 ratification verdict",
        "## 3. Runtime implementation and hardening verdict",
        "## 4. Agent capability delta",
        "## 5. Inherited boundary state confirmed unchanged",
        "## 6. Deferred and blocked items carried forward",
    ):
        assert heading in text
    for token in (
        "window_624_630_coherence_verdict_issued",
        "cdl_063_ratified_and_consumed_in_630",
        "agent_commissioning_loop_runtime_enforcement_active",
        "ecu_active_layer_runtime_and_hardening_complete",
        "window_624_630_parallel_to_623_plus_confirmed",
    ):
        assert token in text


def test_coherence_report_section_four_contains_before_after_delta() -> None:
    text = _read(COHERENCE_PATH)
    assert "Before this window:" in text
    assert "After this window:" in text
    assert "topology only, no debit-side runtime enforcement" in text
    assert "bounded live runtime for debit at epoch commit" in text


def test_capsule_v34_supersedes_v33_and_does_not_claim_option_b_or_ilc_transferability() -> None:
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v3.3.md" in text
    assert "`CDL-063` ratified" in text
    assert "bounded ECU active-layer runtime live and hardened" in text
    assert "Option B is selected" not in text
    assert "ILC transferability is active" not in text


def test_handoff_has_required_headings() -> None:
    text = _read(HANDOFF_PATH)
    for heading in (
        "## 1. Window identity and closure basis",
        "## 2. Inputs and closure inheritance",
        "## 3. Closure verdict summary",
        "## 4. Carry-forward items and residual blockers",
        "## 5. Next-window entry criteria and routing",
        "## 6. MemPalace refresh disposition",
        "## 7. AG-gate window assessment",
    ):
        assert heading in text


def test_handoff_contains_required_tokens() -> None:
    text = _read(HANDOFF_PATH)
    for token in (
        "window_624_630_handoff_630_v0_1_closed",
        "cdl_063_ratification_verdict_pass",
        "agent_commissioning_runtime_enforcement_active",
        "option_d_posture_active_after_630",
        "wallet_boundary_576_581_unchanged_after_630",
        "ecu_debit_not_ilc_payment_630",
        "window_623_plus_remains_highest_priority_continuation",
        "cdl_053_still_deferred_after_630",
    ):
        assert token in text


def test_handoff_section_three_states_runtime_enforcement_active_and_hardened() -> None:
    text = _read(HANDOFF_PATH)
    assert "Bounded runtime enforcement is active and hardened." in text
    assert "bounded debit at epoch commit" in text


def test_handoff_section_five_names_window_623_plus_as_highest_priority() -> None:
    text = _read(HANDOFF_PATH)
    assert "Window 623+ remains the highest-priority continuation." in text
    assert "does not advance Option-B checklist rows directly" in text
    assert "`CDL-062` remains not authorized" in text


def test_handoff_section_six_contains_required_mempalace_refresh_disposition() -> None:
    text = _read(HANDOFF_PATH)
    assert "Disposition: required" in text
    assert "Active working set impacted: yes" in text
    assert "Rebuild command: bash tools/mempalace/build_active_working_set.sh" in text


def test_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_630_SUBJECT)
    commit_ref = _resolve_commit_ref(subject_token=PHASE_630_SUBJECT)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXPECTED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_630_BACKFILL_SUBJECT)
    commit_ref = _resolve_commit_ref(subject_token=PHASE_630_BACKFILL_SUBJECT)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXPECTED_BACKFILL_PATHS
