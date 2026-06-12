from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_preflight_blocker_recorded_without_completion_claims() -> None:
    spec = read("docs/specs/ilc_phase_1560_preflight_blocker_20260612_v0.1.md")
    assert "phase_1560_preflight_blocker_recorded" in spec
    assert "phase_1560_not_executed_preconditions_failed" in spec
    assert "no_agent_init_ceremony_live_executed_phase_1560" in spec
    assert "no_vps_agent_id_derived_phase_1560" in spec
    assert "No Live HTTPS Receivers" in spec
    assert "VPS ML-DSA-65 Key Custody Not Proven" in spec


def test_sequence_lock_marks_phase_1560_blocked_precondition() -> None:
    lock = read("docs/specs/ilc_phase_1556_1564_sequence_lock_v0.1.md")
    assert "Phase 1560 Preflight Blocker" in lock
    assert "Phase 1560 Receiver Remediation" in lock
    assert "BLOCKED_PRECONDITION - receiver-side remediation complete" in lock
    assert "renewed `GO Phase 1560`" in lock
    assert "phase_1560_preflight_blocked_missing_live_https_receivers" in lock
    assert "phase_1560_preflight_blocked_unproven_vps_mldsa_key_custody" in lock
    assert "phase_1560_key_custody_still_pending_human_go" in lock


def test_status_and_planning_index_frontier_updated_to_blocker() -> None:
    status = read("docs/phases/STATUS.md")
    index = read("docs/PLANNING_INDEX.md")
    assert "Phase 1560 Preflight Blocker" in status
    assert "phase_1560_preflight_blocker_recorded" in status
    assert "Phase 1560 receiver remediation" in index[:1400]
    assert "phase_1560_receiver_remediation_committed" in index[:1800]
    assert "Phase 1560 preflight blocker" in index
    assert "phase_1560_preflight_blocker_recorded" in index
    assert "⬅ CURRENT" in index[:1800]


def test_walkthrough_records_remediation_and_non_claims() -> None:
    walk = read(
        "docs/phases/phase_1560_agent_init_live_ceremony_preflight_blocker_walkthrough.md"
    )
    assert "BLOCKED_PRECONDITION - Phase 1560 not executed" in walk
    assert "Required Remediation" in walk
    assert "no_phase_1560_completion_token_emitted" in walk
    assert "phase_1560_agent_init_live_ceremony_requires_receiver_and_key_custody_remediation" in walk
