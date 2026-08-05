from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "out/phase1591_fix1_live_rust_harness_soak.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1591_fix1_live_rust_harness_soak_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PRODUCTION_BRIDGE = ROOT / "ilc_core/consensus/production_bridge.py"

EXPECTED_STATE_ROOT = (
    "d969a75b7b34096089c9382745c8147db93ff0a3dd6d0232da648db510a9bf6a15910001"
)
EXPECTED_SPECTRAL_HASH = (
    "1591159115911591159115911591159115911591159115911591159115911591"
)


def _evidence() -> dict[str, object]:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_live_rust_soak_evidence_records_four_vps_validator_readbacks() -> None:
    payload = _evidence()
    readback = payload["graph_bound_grpc_readback"]
    assert isinstance(readback, dict)
    validators = readback["validators"]
    assert isinstance(validators, list)
    assert len(validators) == 4
    assert {item["validator_id"] for item in validators} == {1, 2, 3, 4}
    assert readback["read_adapter_used"] == "ILCConsensusGrpcReadAdapter"
    assert readback["assertion_count"] == 4
    for item in validators:
        assert item["epoch"] == 1
        assert item["found"] is True
        assert item["state_root_hex"] == EXPECTED_STATE_ROOT
        assert item["spectral_hash_hex"] == EXPECTED_SPECTRAL_HASH
        assert item["agg_sig_len"] == 96


def test_live_rust_soak_evidence_records_remote_lmdb_commit_on_all_validators() -> None:
    payload = _evidence()
    extraction = payload["lmdb_remote_extraction"]
    assert isinstance(extraction, dict)
    assert extraction["expected_state_root_hex"] == EXPECTED_STATE_ROOT
    validators = extraction["validators"]
    assert isinstance(validators, list)
    assert len(validators) == 4
    for item in validators:
        assert item["sentinel_current_epoch"] == 1
        assert item["chain_complete"] is True
        assert item["sentinel_consistent"] is True
        assert item["bls_verified_commits"] == "1/1"
        assert item["verdict"] == "workload_d_replayability_pass"


def test_live_rust_soak_records_ingress_acceptance_and_replay_rejection() -> None:
    payload = _evidence()
    proposal = payload["proposal_ingress"]
    duplicate = payload["duplicate_replay"]
    assert isinstance(proposal, dict)
    assert isinstance(duplicate, dict)
    assert proposal["status_token"] == "submit_epoch_proposal_accepted_phase_1586"
    assert proposal["accepted_epoch_number"] == 1
    assert proposal["accepted_state_root_cidv1_hex"] == EXPECTED_STATE_ROOT
    assert duplicate["rejected"] is True
    assert duplicate["proposal_id"] == proposal["proposal_id"]
    assert duplicate["rejection_error"] == "submit_epoch_proposal_duplicate_phase_1586"


def test_read_side_mtls_patch_is_recorded_and_exported_in_code() -> None:
    source = PRODUCTION_BRIDGE.read_text(encoding="utf-8")
    assert "grpc_client_private_key: bytes | None = None" in source
    assert "grpc_client_certificate_chain: bytes | None = None" in source
    assert "grpc_client_certificate_pair_invalid_phase_1591_fix1" in source
    assert "private_key=config.grpc_client_private_key" in source
    assert "certificate_chain=config.grpc_client_certificate_chain" in source


def test_status_and_walkthrough_record_tokens_without_public_rc_overclaim() -> None:
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    for token in (
        "live_rust_harness_soak_complete_phase_1591_fix1",
        "live_rust_vps_proposal_readback_verified_phase_1591_fix1",
        "production_grpc_read_mtls_hardened_phase_1591_fix1",
    ):
        assert token in status
        assert token in walkthrough
    assert "No mainnet activation" in walkthrough
    assert "public RC flip" in walkthrough
    assert "old Phase 1360 validators" in walkthrough
