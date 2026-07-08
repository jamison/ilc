from __future__ import annotations

import subprocess
from pathlib import Path


CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_DOC = Path(
    "docs/specs/ilc_cdl_101_d2d_signed_gossip_envelope_ratification_evidence_1572a_v0.1.md"
)
STATUS = Path("docs/phases/STATUS.md")
PHASE_1572A_COMMIT_SUBJECT = "feat(block6): ratify CDL-101 signed D2D gossip envelope (Phase 1572a)"


def _phase_1572a_commit_ref() -> str:
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
        if subject.strip() == PHASE_1572A_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_1572a_commit_not_present_in_local_history")


def _changed_paths_for_commit(commit_ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def test_cdl_101_row_is_ratified() -> None:
    text = CDL_REGISTER.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| CDL-101 |"))
    assert "| ratified | phase_1572a | cdl_101_ratified |" in row
    assert "status_detail: ratified" in row
    assert "ratification_token: cdl_101_ratified" in row
    assert "dependency_token: cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1" in row


def test_ratification_evidence_doc_exists_and_contains_required_tokens() -> None:
    assert EVIDENCE_DOC.exists()
    text = EVIDENCE_DOC.read_text(encoding="utf-8")
    assert "cdl_101_ratified" in text
    assert "cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1" in text
    assert "test_invalid_packet_does_not_poison_replay_cache" in text
    assert "tla_plus_obligation_delegation_key_rotation_safety" in text
    assert "cdl061bis_successor" in text


def test_status_records_phase_1572a_tokens() -> None:
    text = STATUS.read_text(encoding="utf-8")
    assert "cdl_101_ratified" in text
    assert "cdl_101_ratification_evidence_committed_phase_1572a" in text
    assert "public_path_remains_blocked_phase_1572a" in text


def test_phase_1572a_does_not_modify_ilc_core_files() -> None:
    changed_paths = _changed_paths_for_commit(_phase_1572a_commit_ref())
    assert changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
