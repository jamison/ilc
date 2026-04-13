from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

INVENTORY_PATH = Path("docs/specs/ilc_remaining_float_and_security_follow_on_inventory_643_v0.1.md")
TODO_PATH = Path("TODO.txt")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_643_remaining_float_and_security_inventory.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_643_g8_remaining_float_and_security_inventory_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_643_SUBJECT_TOKEN = "phase 643 remaining float and security inventory"
PHASE_643_BACKFILL_SUBJECT_TOKEN = "phase 643 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(INVENTORY_PATH),
    str(TODO_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Purpose and boundary",
    "## 2. Closed exact-numeric work to date",
    "## 3. Remaining float surface inventory",
    "## 4. Security follow-on inventory outside this window",
    "## 5. Prioritized carry-forward routing",
    "## 6. TODO registration summary",
)
REQUIRED_TOKENS = (
    "remaining_float_inventory_post_641_published",
    "remaining_float_inventory_runtime_critical_surface_closed_to_date",
    "remaining_float_inventory_runtime_adjacent_surface_still_open",
    "remaining_float_inventory_sim_and_analysis_surface_deferred",
    "security_follow_on_inventory_beyond_642_648_registered",
    "remaining_float_follow_on_todo_registered",
)
REQUIRED_RUNTIME_ADJACENT_PATHS = (
    "`ilc_core/server.py`",
    "`ilc_core/config.py`",
    "`ilc_core/cli/ep_task_cli.py`",
    "`ilc_core/protocol/params.py`",
    "`ilc_core/consensus/engine.py`",
    "`ilc_core/rc/economic_cycle_runtime.py`",
)
REQUIRED_DEFERRED_SURFACES = (
    "`ilc_core/sim/*`",
    "`ilc_core/analysis/*`",
    "`ilc_core/node/devnet.py`",
    "`ilc_core/mining/benchmark.py`",
    "`ilc_core/economics/rl_agents.py`",
)
TODO_HEADER = "[TODO – Post-641 Remaining Float and Security Follow-On]"
TODO_REQUIRED_ITEMS = (
    "Shared/public contract float cleanup",
    "Runtime-adjacent protocol and consensus float cleanup",
    "Lower-tier sim and analysis float cleanup",
    "Exact-numeric boundary review for any new runtime/public numeric surface",
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


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
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
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_inventory_doc_exists_and_contains_required_headings() -> None:
    text = _read(INVENTORY_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_inventory_doc_contains_required_tokens() -> None:
    text = _read(INVENTORY_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_closed_exact_numeric_work_is_recorded() -> None:
    text = _read(INVENTORY_PATH)
    assert "Window 631-636: Tier-0 runtime-critical economic, ledger, and staking surfaces" in text
    assert "Window 637-641: bounded residual `R2/R3` contract leakage" in text


def test_remaining_float_surface_inventory_classifies_multiple_tiers() -> None:
    text = _read(INVENTORY_PATH)
    for item in REQUIRED_RUNTIME_ADJACENT_PATHS:
        assert item in text
    for item in REQUIRED_DEFERRED_SURFACES:
        assert item in text


def test_todo_txt_contains_new_top_level_block_and_inventory_reference() -> None:
    text = _read(TODO_PATH)
    assert TODO_HEADER in text
    assert "docs/specs/ilc_remaining_float_and_security_follow_on_inventory_643_v0.1.md" in text


def test_todo_block_contains_required_carry_forward_items_with_status_and_trigger_language() -> None:
    text = _read(TODO_PATH)
    for item in TODO_REQUIRED_ITEMS:
        assert item in text
    assert "Status:" in text
    assert "Trigger:" in text


def test_phase_643_does_not_mutate_decision_log_or_ilc_core_in_main_commit() -> None:
    _require_commit_or_skip(PHASE_643_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_643_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_643_backfill_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_643_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_643_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
