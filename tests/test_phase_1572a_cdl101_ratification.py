from __future__ import annotations

import subprocess
from pathlib import Path


CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_DOC = Path(
    "docs/specs/ilc_cdl_101_d2d_signed_gossip_envelope_ratification_evidence_1572a_v0.1.md"
)
STATUS = Path("docs/phases/STATUS.md")


def _changed_paths_against_head() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
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
    changed_paths = _changed_paths_against_head()
    assert changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
