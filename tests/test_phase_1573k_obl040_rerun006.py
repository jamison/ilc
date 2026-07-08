import json
from pathlib import Path


EVIDENCE_PATH = Path("docs/sims/ilc_block6_obl040_rerun006_evidence_1573k_v0.1.json")
ROLLBACK_PATH = Path(
    "docs/sims/ilc_block6_obl040_rerun006_rollback_receipt_1573k_v0.1.json"
)
STATUS_PATH = Path("docs/phases/STATUS.md")

EXPECTED_SETTLEMENT_ROOT = (
    "settlement_sha256:b0e2ee04458f2de0578723cd42918f3aa50bc3966cf20c26ea4da83d688cb89d"
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_json_exists_and_roots_match() -> None:
    assert EVIDENCE_PATH.exists()
    evidence = _read_json(EVIDENCE_PATH)
    assert evidence["settlement_root"] == EXPECTED_SETTLEMENT_ROOT
    assert evidence["four_machine_replay"]["identical"] is True
    for machine in ("jamisons-imac", "ilc-node-2", "ilc-node-3", "ilc-node-6"):
        assert evidence["four_machine_replay"][machine] == EXPECTED_SETTLEMENT_ROOT


def test_omission_detection_is_clean() -> None:
    evidence = _read_json(EVIDENCE_PATH)
    assert evidence["omission_detection"]["omission_free"] is True
    assert evidence["omission_detection"]["missing_candidates"] == []


def test_genesis_tranche_confirmation_is_authorized_value_path() -> None:
    evidence = _read_json(EVIDENCE_PATH)
    confirmation = evidence["genesis_tranche_confirmation"]
    assert confirmation["lot_id"] == "genesis-fixed-tranche-001"
    assert confirmation["amount_ecu"] == "1296000"
    assert confirmation["genesis_tranche_treatment"] == "applied_by_authorized_value_path"


def test_candidate_schema_uses_1573j_fields() -> None:
    evidence = _read_json(EVIDENCE_PATH)
    assert len(evidence["candidate_list"]) == 5
    for candidate in evidence["candidate_list"]:
        assert "amount_ecu" in candidate
        assert "ecu_amount" not in candidate
        assert "maturation_epoch" not in candidate
        assert candidate["conversion_epoch"] >= candidate["deadline_epoch"]


def test_bft_quorum_source_is_recorded() -> None:
    evidence = _read_json(EVIDENCE_PATH)
    assert evidence["bft_quorum_threshold"] == "2*(N-1)/3+1 = 3 for N=4"
    assert "ilc_consensus/src/validator.rs" in evidence["bft_quorum_file_ref"]
    assert "ilc_consensus/src/epoch_settlement.rs" in evidence["bft_quorum_file_ref"]
    assert evidence["bft_quorum_result"]["required_signer_count_for_n4"] == 3


def test_rollback_receipt_is_complete() -> None:
    assert ROLLBACK_PATH.exists()
    receipt = _read_json(ROLLBACK_PATH)
    assert receipt["namespace_id"] == "block6_private_value_write_soft_rc_rerun006"
    assert receipt["namespace_wiped"] is True
    assert receipt["steps_completed"] == [1, 2, 3, 4, 5, 6, 7]
    assert receipt["production_atlas_registration_for_scratch_state"] is False


def test_status_tokens_record_phase_completion() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "obl_040_rerun_006_pass_phase_1573k",
        "obl_039_genesis_tranche_live_path_confirmed_phase_1573k",
        "four_machine_replay_settlement_root_confirmed_phase_1573k",
        "fix2s_namespace_wiped_phase_1573k",
        "public_path_remains_blocked_phase_1573k",
    ):
        assert token in status
    assert "four_machine_replay_settlement_root_mismatch_phase_1573k" not in status
    assert "four_machine_replay_precondition_failed_phase_1573k" not in status

