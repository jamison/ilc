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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_blocked_evidence_records_no_completion_claim() -> None:
    evidence = json.loads(_read(EVIDENCE))

    assert evidence["status"] == "BLOCKED"
    assert evidence["blocked_token"] == BLOCKED_TOKEN
    assert evidence["verdict"]["completion_tokens_emitted"] is False
    assert set(evidence["non_claims"]) == COMPLETION_TOKENS


def test_status_contains_blocked_token_only_for_fix2_runtime_claims() -> None:
    status = _read(STATUS)

    assert BLOCKED_TOKEN in status
    assert "**Blocked token:**" in status
    assert "**Completion tokens:** Not emitted." in status
    for token in COMPLETION_TOKENS:
        assert token not in status


def test_evidence_confirms_tailscale_free_tested_config_and_cleanup() -> None:
    evidence = json.loads(_read(EVIDENCE))

    assert evidence["config"]["tailscale_ipv4_literal_regex_100_x_absent_from_tested_config"] is True
    assert evidence["cleanup"]["validators_stopped"] is True
    assert evidence["cleanup"]["phase_5125x_5126x_listeners_absent_after_cleanup"] is True
    assert evidence["cleanup"]["phase_ufw_rules_absent_after_cleanup"] is True


def test_evidence_records_provider_firewall_reachability_blocker() -> None:
    evidence = json.loads(_read(EVIDENCE))
    blocker = evidence["verdict"]["blocker"]

    assert "cloud-provider firewall" in blocker
    assert evidence["reachability"]["temporary_broad_ufw_allow_on_public_vps_b_changed_result"] is False
    assert all(
        result["result"] == "timeout"
        for result in evidence["reachability"]["controller_to_public_grpc"]
    )


def test_walkthrough_does_not_overclaim_public_harness_success() -> None:
    walkthrough = _read(WALKTHROUGH)

    assert "**Status:** BLOCKED" in walkthrough
    assert BLOCKED_TOKEN in walkthrough
    assert "No completion tokens were emitted" in walkthrough
    assert "mirror_disposition=no_new_includes" in walkthrough
