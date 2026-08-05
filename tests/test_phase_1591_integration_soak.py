from __future__ import annotations

import pytest

from ilc_core.consensus.production_bridge import (
    ConsensusBridgeConfig,
    build_epoch_settlement_proposal_submission,
    submit_ecu_transfer_via_quic,
)
from tools.phase1591_integration_soak import (
    EXPECTED_FINAL_CREDIT_MICRO_ECU,
    NETWORK_ID,
    SPECTRAL_HASH,
    DeterministicRustHarnessState,
    DeterministicRustProposalStub,
    build_mini_soak_record,
    build_read_adapter,
    run_phase1591_soak,
)


def test_e2e_python_to_rust_epoch_checkpoint_submission() -> None:
    result = run_phase1591_soak()

    assert result["verdict"] == "PASS"
    assert (
        result["bridge_submission"]["status_token"]
        == "submit_epoch_proposal_accepted_phase_1586"
    )
    assert result["bridge_submission"]["accepted_epoch_number"] == 1
    assert "submit_epoch_proposal_entered_bft_path" in result["process_log"]


def test_e2e_rust_bls_verification_passes_for_valid_checkpoint() -> None:
    result = run_phase1591_soak()

    assert "bls_verification_passed" in result["process_log"]
    assert "process_epoch_checkpoint_called" in result["process_log"]
    assert result["epoch_record"]["agg_sig_len"] == 96


def test_e2e_grpc_readback_matches_python_settled_balance() -> None:
    result = run_phase1591_soak()

    assert result["python_expected_micro_ecu"] == EXPECTED_FINAL_CREDIT_MICRO_ECU
    assert result["readback"]["amount_micro_ecu"] == str(EXPECTED_FINAL_CREDIT_MICRO_ECU)
    assert result["readback"]["amount_ecu"] == "1.234567"
    assert result["graph_binding_verified"] is True
    state = DeterministicRustHarnessState(
        epoch=1,
        balance_micro_ecu=EXPECTED_FINAL_CREDIT_MICRO_ECU,
        state_root=b"r" * 36,
        spectral_hash=SPECTRAL_HASH,
        agg_sig=b"s" * 96,
    )
    adapter = build_read_adapter(state)
    assert adapter.get_epoch_record(1).found is True
    assert adapter.get_epoch_record(1).found is True


def test_e2e_rust_rejects_duplicate_epoch_submission() -> None:
    agent_id = bytes.fromhex(
        "8fc76b0b897092833d575794290242b4dfd41a39eb59a08189c4dbd805612749a"
        "35b47b7a2dd7d31c9bfd353ebdfb833"
    )
    record_bytes, state_root, _record = build_mini_soak_record(agent_id.hex())
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=agent_id,
        epoch_number=1,
        state_root_cidv1=state_root,
        spectral_hash=SPECTRAL_HASH,
        settlement_record_bytes=record_bytes,
        not_before_unix_ms=0,
        network_id=NETWORK_ID,
    )
    state = DeterministicRustHarnessState()
    stub = DeterministicRustProposalStub(state, agent_id)
    config = ConsensusBridgeConfig(
        target="deterministic-rust-read.invalid:7101",
        proposal_ingress_endpoint="deterministic-rust-proposal.invalid:7102",
    )

    submit_ecu_transfer_via_quic(submission, config=config, stub=stub)
    with pytest.raises(ValueError, match="submit_epoch_proposal_duplicate_phase_1586"):
        submit_ecu_transfer_via_quic(submission, config=config, stub=stub)
