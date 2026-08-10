import json
from pathlib import Path


EVIDENCE = Path("out/phase_1591_fix5_mixed_economic_soak/mixed_economic_evidence.json")
WALKTHROUGH = Path("docs/phases/phase_1591_fix5_mixed_economic_graph_action_soak_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
HARNESS = Path("tools/testbed/phase1591_fix5_mixed_economic_graph_action_soak.py")

TOKENS = {
    "mixed_economic_graph_action_soak_complete_phase_1591_fix5",
    "ilc_transfer_live_roundtrip_proven_phase_1591_fix5",
    "ecu_fast_path_live_roundtrip_proven_phase_1591_fix5",
    "double_spend_rejected_live_phase_1591_fix5",
}


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_phase_1591_fix5_records_all_required_scenarios() -> None:
    evidence = _evidence()
    scenarios = evidence["scenarios"]

    assert evidence["verdict"] == "PASS"
    assert set(scenarios) == {
        "attribution_readback_after_multi_epoch_soak",
        "bounded_ecu_fast_path_transfer",
        "bounded_ilc_transfer",
        "concurrent_graph_submission_and_attribution_readback",
        "double_spend_nonce_rejection",
    }
    assert all(item["passed"] is True for item in scenarios.values())


def test_phase_1591_fix5_ilc_transfer_and_double_spend_are_real_lmdb_readback() -> None:
    evidence = _evidence()
    transfer = evidence["scenarios"]["bounded_ilc_transfer"]["result"]
    double_spend = evidence["scenarios"]["double_spend_nonce_rejection"]

    assert transfer["amount_ilc"] == "1"
    assert transfer["sender_balance_before_ilc"] == "10"
    assert transfer["sender_balance_after_ilc"] == "9"
    assert transfer["recipient_balance_after_ilc"] == "1"
    assert len(transfer["transfer_id"]) == 64
    assert double_spend["error_token"] == "nonce_replay_rejected"


def test_phase_1591_fix5_ecu_transfer_records_debit_credit_without_minting() -> None:
    ecu = _evidence()["scenarios"]["bounded_ecu_fast_path_transfer"]["result"]

    assert ecu["amount_micro_ecu"] == 500000
    assert ecu["bridge_payload_count"] == 1
    assert ecu["rust_payload_count"] == 1
    assert ecu["debit_agent_id"] == "a" * 96
    assert ecu["credit_agent_id"] == "b" * 96
    assert ecu["minted_ecu"] is False


def test_phase_1591_fix5_attribution_readback_has_cdl108_credit_entry() -> None:
    readback = _evidence()["scenarios"]["attribution_readback_after_multi_epoch_soak"]["readback"]
    entry = readback["first_credit_entry"]

    assert readback["backward_attribution_entry_count"] == 1
    assert len(readback["backward_attribution_batch_root"]) == 64
    assert readback["total_final_credit_ecu"] == "0.05"
    assert entry["edge_type"] == "PROVENANCE"
    assert entry["recipient_agent_id"] == "c" * 96
    assert entry["source_node_cid"] == "work:phase1591-fix5"


def test_phase_1591_fix5_activation_boundary_and_discovered_gap_are_explicit() -> None:
    evidence = _evidence()
    boundary = evidence["activation_boundary"]
    gap = evidence["discovered_execution_gap"]

    assert boundary["ilc_transfer_enabled"] is True
    assert boundary["ecu_fast_path_transfer_enabled"] is True
    assert boundary["additional_activation_flags_changed"] is False
    assert boundary["ecu_minting_authorized"] is False
    assert boundary["external_withdrawal_authorized"] is False
    assert boundary["wallet_spend_authorized"] is False
    assert "tools/testbed/phase1575h_ilc_transfer_submit.py" in gap["prompt_named_missing_scripts"]
    assert "without ilc_core changes" in gap["resolution"]


def test_phase_1591_fix5_substrate_reference_remains_passed() -> None:
    substrate = _evidence()["substrate_reference"]

    assert substrate["phase1591_soak_verdict"] == "PASS"
    assert "process_epoch_checkpoint_called" in substrate["process_log"]
    assert substrate["readback"]["amount_micro_ecu"] == "1234567"
    assert substrate["readback"]["production_bridge_active"] is True


def test_phase_1591_fix5_tokens_present_in_status_evidence_and_walkthrough() -> None:
    evidence_tokens = set(_evidence()["tokens"])
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert TOKENS.issubset(evidence_tokens)
    for token in TOKENS:
        assert token in status
        assert token in walkthrough


def test_phase_1591_fix5_harness_does_not_modify_core_or_activation_flags() -> None:
    source = HARNESS.read_text(encoding="utf-8")

    assert "ILC_TRANSFER_ENABLED =" not in source
    assert "ECU_FAST_PATH_TRANSFER_ENABLED =" not in source
    assert "PRODUCTION_BRIDGE_ACTIVE =" not in source
