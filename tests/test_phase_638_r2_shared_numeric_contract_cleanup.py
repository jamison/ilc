from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.protocol.mapper import (
    epoch_summary_to_protocol,
    node_to_protocol_claim,
    outcome_to_protocol_task_outcome,
)
from ilc_core.economics.outcome import TaskOutcome
from ilc_core.types import ClaimRecord, Node

SPEC_PATH = Path("docs/specs/ilc_r2_shared_numeric_contract_cleanup_638_v0.1.md")
TEST_PATH = Path("tests/test_phase_638_r2_shared_numeric_contract_cleanup.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_638_g8_r2_shared_numeric_contract_cleanup_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_638_SUBJECT_TOKEN = "phase 638 r2 shared numeric contract cleanup"
PHASE_638_BACKFILL_SUBJECT_TOKEN = "phase 638 walkthrough and status backfill"
REQUIRED_HEADINGS = (
    "## 1. Ratified dependency and cleanup target",
    "## 2. Primary shared contract files",
    "## 3. Shared numeric contract changes",
    "## 4. Compatibility and machine-legible boundary",
    "## 5. Verification and residual defers",
)
REQUIRED_TOKENS = (
    "r2_shared_numeric_contract_cleanup_638_locked",
    "cdl_064_dependency_consumed_in_phase_638",
    "shared_net_stake_float_contract_removed",
    "protocol_mapper_float_projection_removed",
    "shared_numeric_contract_canonicalization_applied",
    "phase_638_verification_defined",
    "window_637_641_moves_to_protocol_runtime_adjacent_cleanup",
)
REQUIRED_TARGETS = (
    "- `ilc_core/types.py`",
    "- `ilc_core/protocol/mapper.py`",
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


def test_section_two_names_types_and_mapper() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_TARGETS:
        assert item in text


def test_section_three_records_shared_contract_and_mapper_cleanup() -> None:
    text = _read(SPEC_PATH)
    assert "Node.net_stake" in text
    assert "ClaimRecord.net_stake" in text
    assert "claim/refute `net_stake` is emitted as a canonical decimal string" in text
    assert "epoch-summary `total_ecu_spent`, `total_reward_paid`, and" in text


def test_types_no_longer_define_float_bearing_net_stake_on_node_or_claim_record() -> None:
    text = _read(Path("ilc_core/types.py"))
    assert "net_stake: float" not in text
    node = Node(
        id="node:test",
        type="claim",
        content="x",
        agent_id="agent:test",
        signature="sig",
        net_stake=10.0,
    )
    claim = ClaimRecord(
        id="claim:test",
        type="claim",
        agent_id="agent:test",
        content="x",
        signature="sig",
        net_stake="1.2500",
    )
    assert node.model_dump(mode="json")["net_stake"] == "10"
    assert claim.model_dump(mode="json")["net_stake"] == "1.25"


def test_mapper_no_longer_uses_float_projection_and_emits_canonical_decimal_strings() -> None:
    mapper_text = _read(Path("ilc_core/protocol/mapper.py"))
    assert 'float(summary.get("total_ecu_spent", 0.0))' not in mapper_text
    assert 'float(summary.get("total_reward_paid", 0.0))' not in mapper_text
    assert 'float(' not in mapper_text

    node = Node(
        id="node:test",
        type="claim",
        content="mapper",
        agent_id="agent:test",
        signature="sig",
        net_stake="10.00",
    )
    claim_proto = node_to_protocol_claim(node)
    outcome_proto = outcome_to_protocol_task_outcome(
        TaskOutcome(
            task_type="claim.submit",
            domain="MEDIUM",
            stake_spent=0.1,
            reward_paid=2.0,
            success=True,
        ),
        epoch=3,
        agent_id="agent:test",
    )
    epoch_proto = epoch_summary_to_protocol(
        7,
        {
            "total_tasks": 10,
            "total_ecu_spent": "1.500",
            "total_reward_paid": 2.0,
            "clearing_price_ilc_per_ecu": "1.333300",
        },
    )
    assert claim_proto["net_stake"] == "10"
    assert outcome_proto["stake_spent"] == "0.1"
    assert outcome_proto["reward_paid"] == "2"
    assert epoch_proto["total_ecu_spent"] == "1.5"
    assert epoch_proto["total_reward_paid"] == "2"
    assert epoch_proto["clearing_price_ilc_per_ecu"] == "1.3333"


def test_phase_638_main_commit_touches_spec_test_and_bounded_code_paths_without_decision_log_mutation() -> None:
    _require_commit_or_skip(PHASE_638_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_638_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(SPEC_PATH) in changed_paths
    assert str(TEST_PATH) in changed_paths
    assert any(path.startswith("ilc_core/") for path in changed_paths)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)


def test_phase_638_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_638_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_638_BACKFILL_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
