import json
import re
from pathlib import Path


EVIDENCE = Path("out/phase_1591_fix4_adversarial_soak/adversarial_evidence.json")
WALKTHROUGH = Path("docs/phases/phase_1591_fix4_live_adversarial_network_soak_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
EPOCH_SETTLEMENT = Path("ilc_consensus/src/epoch_settlement.rs")
CONFIG = Path("ilc_consensus/src/config.rs")

TOKENS = {
    "live_adversarial_soak_complete_phase_1591_fix4",
    "validator_restart_mid_epoch_proven_phase_1591_fix4",
    "duplicate_proposal_replay_rejected_adversarial_phase_1591_fix4",
    "bad_cert_rejected_adversarial_phase_1591_fix4",
}

RAW_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def _load_evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_phase_1591_fix4_evidence_records_all_required_scenarios() -> None:
    evidence = _load_evidence()
    scenarios = evidence["scenarios"]

    expected = {
        "bad_client_cert_rejected",
        "delayed_validator_late_checkpoint",
        "duplicate_checkpoint_replay_rejected",
        "stale_endpoint_assertion_rejected",
        "validator_restart_mid_epoch",
        "validator_sigkill_two_epoch_rejoin",
    }
    assert set(scenarios) == expected
    assert all(item["passed"] is True for item in scenarios.values())


def test_phase_1591_fix4_final_lmdb_state_is_epoch_four_for_all_validators() -> None:
    evidence = _load_evidence()
    for state in evidence["final_lmdb_state"].values():
        assert state["sentinel_current_epoch"] == 4
        assert state["bls_verified_commits"] == "4/4"
        assert state["chain_complete"] is True
        assert state["sentinel_consistent"] is True
        assert state["verdict"] == "workload_d_replayability_pass"


def test_phase_1591_fix4_tokens_present_in_status_and_evidence() -> None:
    evidence_tokens = set(_load_evidence()["tokens"])
    status = STATUS.read_text(encoding="utf-8")

    assert TOKENS.issubset(evidence_tokens)
    for token in TOKENS:
        assert token in status


def test_phase_1591_fix4_artifacts_do_not_commit_raw_public_ips() -> None:
    evidence_text = EVIDENCE.read_text(encoding="utf-8")
    walkthrough_text = WALKTHROUGH.read_text(encoding="utf-8")

    assert RAW_IPV4_RE.search(evidence_text) is None
    assert RAW_IPV4_RE.search(walkthrough_text) is None
    assert "public-vps-a-validator-1" in walkthrough_text
    assert "public-vps-c-validator-4" in walkthrough_text


def test_testnet_epoch_override_is_guarded_and_default_off() -> None:
    config_text = CONFIG.read_text(encoding="utf-8")
    epoch_text = EPOCH_SETTLEMENT.read_text(encoding="utf-8")

    assert "testnet_min_epoch_duration_ms_requires_explicit_testnet_harness_role" in config_text
    assert 'cfg.network_id.contains("testnet")' in config_text
    assert 'role.contains("harness")' in config_text
    assert "min_epoch_duration_ms_override_or_default" in epoch_text
    assert "MIN_EPOCH_DURATION_MS" in epoch_text
