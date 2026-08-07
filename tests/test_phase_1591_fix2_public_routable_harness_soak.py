from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1591_fix2_public_routable_harness_soak_walkthrough.md"
EVIDENCE = ROOT / "out/phase_1591_fix2_public_harness_soak/soak_evidence.json"

BLOCKED_TOKEN = "public_routable_harness_soak_blocked_provider_firewall_phase_1591_fix2"
COMPLETION_TOKENS = {
    "public_routable_harness_soak_complete_phase_1591_fix2",
    "tailscale_overlay_not_required_for_consensus_phase_1591_fix2",
    "public_mtls_readback_verified_phase_1591_fix2",
}
EXPECTED_STATE_ROOT = (
    "6a53adb9ed1591db56e4a66f24dc69e5cc9dcaef9e3485e793623b366e1b99511591f200"
)
EXPECTED_SPECTRAL_HASH = (
    "1591f2001591f2001591f2001591f2001591f2001591f2001591f2001591f200"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _evidence() -> dict:
    payload = json.loads(_read(EVIDENCE))
    assert isinstance(payload, dict)
    return payload


def test_success_evidence_records_completion_tokens() -> None:
    evidence = _evidence()

    assert evidence["status"] == "COMPLETE"
    assert evidence["prior_blocked_token"] == BLOCKED_TOKEN
    assert set(evidence["output_tokens"]) == COMPLETION_TOKENS
    assert evidence["verdict"]["completion_tokens_emitted"] is True


def test_status_contains_success_tokens_and_historical_blocker() -> None:
    status = _read(STATUS)

    assert BLOCKED_TOKEN in status
    for token in COMPLETION_TOKENS:
        assert token in status


def test_evidence_confirms_tailscale_free_public_config_and_cleanup() -> None:
    evidence = _evidence()

    assert evidence["config"]["public_data_plane"] is True
    assert evidence["config"]["tailscale_overlay_required"] is False
    assert evidence["config"]["tailscale_ipv4_literal_regex_100_x_absent_from_tested_config"] is True
    assert evidence["cleanup"]["validators_stopped"] is True
    assert evidence["cleanup"]["phase_5125x_5126x_listeners_absent_after_cleanup"] is True


def test_public_readback_matches_on_all_four_validators() -> None:
    evidence = _evidence()
    readback = evidence["post_submit_readback"]

    assert len(readback) == 4
    assert {entry["validator_id"] for entry in readback} == {1, 2, 3, 4}
    for entry in readback:
        assert entry["current_epoch"] == 1
        assert entry["record_found"] is True
        assert entry["record_epoch"] == 1
        assert entry["state_root_hex"] == EXPECTED_STATE_ROOT
        assert entry["state_root_matches"] is True
        assert entry["spectral_hash_hex"] == EXPECTED_SPECTRAL_HASH
        assert entry["spectral_hash_matches"] is True
        assert entry["agg_sig_len"] == 96


def test_proposal_and_adversarial_checks_passed() -> None:
    evidence = _evidence()
    proposal = evidence["proposal_ingress"]

    assert proposal["status_token"] == "submit_epoch_proposal_accepted_phase_1586"
    assert proposal["accepted_epoch_number"] == 1
    assert proposal["accepted_state_root_hex"] == EXPECTED_STATE_ROOT
    assert evidence["duplicate_replay_rejection"]["rejected"] is True
    assert (
        evidence["duplicate_replay_rejection"]["error"]
        == "submit_epoch_proposal_duplicate_phase_1586"
    )
    assert evidence["bad_client_rejection"]["rejected"] is True


def test_lmdb_extractors_verified_all_four_stores() -> None:
    evidence = _evidence()
    extractors = evidence["state_extractor_readback"]

    assert len(extractors) == 4
    for entry in extractors:
        assert entry["verdict"] == "workload_d_replayability_pass"
        assert entry["sentinel_current_epoch"] == 1
        assert entry["chain_complete"] is True
        assert entry["sentinel_consistent"] is True
        assert entry["bls_verified_commits"] == "1/1"
        assert entry["state_root_hex"] == EXPECTED_STATE_ROOT


def test_walkthrough_records_success_without_public_rc_overclaim() -> None:
    walkthrough = _read(WALKTHROUGH)

    assert "**Status:** COMPLETE" in walkthrough
    for token in COMPLETION_TOKENS:
        assert token in walkthrough
    assert BLOCKED_TOKEN in walkthrough
    assert "No public RC activation" in walkthrough
    assert "mirror_disposition=no_new_includes" in walkthrough
