from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_receiver_remediation_records_cleared_receiver_blocker_and_remaining_key_blocker() -> None:
    spec = read("docs/specs/ilc_phase_1560_receiver_remediation_20260612_v0.1.md")
    assert "phase_1560_receiver_remediation_committed" in spec
    assert "private_tls_receivers_online_phase_1560_remediation" in spec
    assert "receiver_status_https_confirmed_phase_1560_remediation" in spec
    assert "phase_1560_key_custody_still_pending_human_go" in spec
    assert "phase_1560_live_ceremony_not_executed_receiver_remediation" in spec


def test_receiver_remediation_does_not_claim_phase_1560_completion() -> None:
    spec = read("docs/specs/ilc_phase_1560_receiver_remediation_20260612_v0.1.md")
    assert "no_agent_init_ceremony_live_executed_phase_1560_remediation" in spec
    assert "no_vps_agent_id_derived_phase_1560_remediation" in spec
    assert "no_serving_receipts_live_confirmed_phase_1560_remediation" in spec
    assert "no_public_rc_activation_phase_1560_remediation" in spec


def test_receiver_tool_is_public_rc_excluded() -> None:
    tool = read("tools/genesis_serving_receiver.py")
    assert "PUBLIC_RC_EXCLUDE: private_phase_1560_genesis_receiver" in tool
    assert "GENESIS_RECEIVER_STATUS_PATH" in tool
    assert "MAX_REQUEST_BYTES = 1_048_576" in tool


def test_frontier_docs_record_receiver_remediation() -> None:
    status = read("docs/phases/STATUS.md")
    index = read("docs/PLANNING_INDEX.md")
    lock = read("docs/specs/ilc_phase_1556_1564_sequence_lock_v0.1.md")
    assert "Phase 1560 Receiver Remediation" in status
    assert "phase_1560_receiver_remediation_committed" in status
    assert "Phase 1560 receiver remediation" in index[:1800]
    assert "phase_1560_receiver_remediation_committed" in index[:2200]
    assert "receiver-side precondition is remediated" in lock
