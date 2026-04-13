from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.exceptions import EventLogValidationError
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.settlement_metrics import compute_settlement_metrics
from ilc_core.protocol.event_log import (
    make_epoch_summary_event,
    make_task_outcome_event,
    validate_epoch_summary_payload,
    validate_task_outcome_payload,
)
from ilc_core.ledger.backend import InMemoryLedgerBackend

SPEC_PATH = Path("docs/specs/ilc_r2_protocol_runtime_adjacent_numeric_cleanup_639_v0.1.md")
TEST_PATH = Path("tests/test_phase_639_r2_protocol_runtime_adjacent_numeric_cleanup.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_639_g8_r2_protocol_runtime_adjacent_numeric_cleanup_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_639_SUBJECT_TOKEN = "phase 639 r2 protocol runtime adjacent numeric cleanup"
PHASE_639_BACKFILL_SUBJECT_TOKEN = "phase 639 walkthrough and status backfill"
REQUIRED_HEADINGS = (
    "## 1. Ratified dependency and cleanup target",
    "## 2. Runtime-adjacent files migrated",
    "## 3. Numeric validator and metrics cleanup",
    "## 4. Compatibility boundary and residual float exposure",
    "## 5. Verification and carry-forward",
)
REQUIRED_TOKENS = (
    "r2_protocol_runtime_adjacent_numeric_cleanup_639_locked",
    "cdl_064_dependency_consumed_in_phase_639",
    "event_log_non_commit_numeric_validators_cleaned",
    "settlement_metrics_float_aggregation_removed",
    "active_layer_runtime_compatibility_egress_reviewed",
    "non_finite_numeric_boundary_rejection_applied_in_phase_639",
    "phase_639_verification_defined",
    "window_637_641_moves_to_r3_numeric_companion_cleanup",
)
REQUIRED_TARGETS = (
    "- `ilc_core/protocol/event_log.py`",
    "- `ilc_core/ledger/settlement_metrics.py`",
    "- `ilc_core/ledger/ecu_active_layer_runtime.py`",
)
ALLOWED_MAIN_PREFIXES = (
    "ilc_core/protocol/event_log.py",
    "ilc_core/ledger/settlement_metrics.py",
    "ilc_core/ledger/ecu_active_layer_runtime.py",
    "tests/test_event_log_validators.py",
    "tests/test_settlement_metrics.py",
    "tests/test_ecu_active_layer_runtime.py",
    "tests/test_ecu_active_layer_runtime_hardening.py",
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


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_cleanup_doc_exists_and_contains_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_cleanup_doc_contains_all_required_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_names_all_required_runtime_adjacent_targets() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_TARGETS:
        assert item in text


def test_section_three_records_event_log_and_settlement_metrics_cleanup() -> None:
    text = _read(SPEC_PATH)
    assert "task_outcome" in text
    assert "epoch_summary" in text
    assert "make_task_outcome_event(...)" in text
    assert "reward aggregation in `ilc_core/ledger/settlement_metrics.py` no longer uses" in text


def test_settlement_metrics_no_longer_aggregate_rewards_through_float_totals() -> None:
    text = _read(Path("ilc_core/ledger/settlement_metrics.py"))
    assert "float(" not in text

    ledger = InMemoryLedgerBackend()
    ledger.epoch_records["epoch-1"] = {
        "epoch_id": "epoch-1",
        "epoch_index": 1,
        "namespace_id": "ns",
        "created_at": "2026-01-01T00:00:00+00:00",
        "finalization_state": "committed",
        "summary": {"reward_total": "1.25", "task_count": 1, "agent_count": 1, "stake_total": "5"},
        "checksums": {"epoch_events_cid": "cid:1", "epoch_state_cid": "cid:2"},
        "status": "settled",
        "distribution_status": "distributed",
    }
    metrics = compute_settlement_metrics(ledger)
    assert metrics["total_rewards_distributed"] == "1.25"
    assert metrics["total_rewards_stubbed"] == "0"


def test_non_commit_numeric_validators_and_helper_constructors_reject_non_finite_values() -> None:
    event_log_text = _read(Path("ilc_core/protocol/event_log.py"))
    assert "reward: int | float | str | Decimal" in event_log_text
    assert "total_reward: int | float | str | Decimal" in event_log_text
    assert "reward: float" not in event_log_text
    assert "total_reward: float" not in event_log_text

    non_finite_values = ("NaN", "Infinity", "-Infinity", float("nan"), float("inf"), float("-inf"))
    for value in non_finite_values:
        with pytest.raises(EventLogValidationError):
            validate_task_outcome_payload(
                {
                    "agent_id": "agent_1",
                    "epoch_index": 10,
                    "namespace_id": "ns_1",
                    "task_type": "reasoning",
                    "reward": value,
                    "success": True,
                }
            )
        with pytest.raises(EventLogValidationError):
            validate_epoch_summary_payload(
                {
                    "epoch_index": 100,
                    "total_tasks": 50,
                    "total_reward": value,
                }
            )
        with pytest.raises(EventLogValidationError):
            make_task_outcome_event(
                agent_id="agent_1",
                epoch_index=10,
                namespace_id="ns_1",
                task_type="reasoning",
                reward=value,  # type: ignore[arg-type]
                success=True,
            )
        with pytest.raises(EventLogValidationError):
            make_epoch_summary_event(
                epoch_index=100,
                total_tasks=50,
                total_reward=value,  # type: ignore[arg-type]
            )


def test_phase_639_main_commit_touches_spec_test_and_bounded_code_paths_without_decision_log_mutation() -> None:
    _require_commit_or_skip(PHASE_639_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_639_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(SPEC_PATH) in changed_paths
    assert str(TEST_PATH) in changed_paths
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    unexpected = {
        path
        for path in changed_paths
        if path not in {str(SPEC_PATH), str(TEST_PATH)}
        and path not in ALLOWED_MAIN_PREFIXES
    }
    assert not unexpected


def test_phase_639_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_639_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_639_BACKFILL_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
