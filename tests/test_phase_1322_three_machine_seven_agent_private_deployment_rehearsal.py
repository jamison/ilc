from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = (
    ROOT
    / "docs/specs/ilc_three_machine_seven_agent_private_deployment_rehearsal_1322_v0.1.json"
)
REPORT_MD = (
    ROOT
    / "docs/specs/ilc_three_machine_seven_agent_private_deployment_rehearsal_1322_v0.1.md"
)

REQUIRED_TOKENS = {
    "three_machine_seven_agent_private_deployment_rehearsal_phase_1322.v0.1",
    "essential_graph_native_sidecar_suite_private_deployment_rehearsed_phase_1322",
    "private_wiring_only_no_public_serving_phase_1322",
    "digitalocean_openclaw_private_test_evidence_recorded_phase_1322",
    "identity_artifact_creation_stop_guard_phase_1322",
    "phase_1323_openclaw_nemoclaw_claimable_profile_dry_run_next",
    "public_rc_remains_blocked_after_phase_1322",
}


def _load_report() -> dict[str, object]:
    with REPORT_JSON.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_phase_1322_report_tokens_and_canonical_json() -> None:
    report_text = REPORT_JSON.read_text(encoding="utf-8")
    md_text = REPORT_MD.read_text(encoding="utf-8")
    report = _load_report()

    for token in REQUIRED_TOKENS:
        assert token in report_text
        assert token in md_text

    canonical = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert report_text == canonical


def test_phase_1322_topology_is_private_three_machine_seven_agent() -> None:
    report = _load_report()
    topology = report["topology"]
    assert isinstance(topology, list)
    assert len(topology) == 7

    machine_roles = {entry["machine_role"] for entry in topology}
    agent_roles = {entry["agent_role"] for entry in topology}
    tailscale_ips = {entry["tailscale_ip"] for entry in topology}

    assert machine_roles == {
        "coordinator",
        "harness-adapter",
        "verifier/projection",
    }
    assert agent_roles == {
        "TransportPrincipal admission",
        "harness bridge",
        "projection",
        "sidecar registry",
        "value-path preflight",
        "verifier",
        "wallet-facing preflight",
    }
    assert tailscale_ips == {"100.112.32.42", "100.91.33.46", "100.72.17.38"}
    assert all(entry["network_mode"] == "tailscale_private_overlay" for entry in topology)
    assert all(entry["public_exposure"] == "none_for_ilc_role" for entry in topology)
    assert all(entry["secret_handling"] == "no secret read" for entry in topology)


def test_phase_1322_identity_guard_and_no_public_authority() -> None:
    report = _load_report()

    guard = report["identity_artifact_stop_guard"]
    assert guard["checked_before_execution"] is True
    assert guard["created_or_written_identity_artifacts"] == []
    assert guard["result"] == "pass_no_identity_artifact_created_or_written"
    assert guard["stop_required_if_artifact_identified"] is True

    floor = report["non_authorization_floor"]
    assert all(value is False for value in floor.values())

    live_execution = report["live_execution"]
    assert live_execution["commands_bound_to_public_interfaces"] == []
    assert live_execution["ilc_public_listener_enabled"] is False
    assert live_execution["public_ip_ilc_service_exposure_enabled"] is False
    assert live_execution["public_peer_discovery_enabled"] is False


def test_phase_1322_live_harness_boundary_and_firewall() -> None:
    report = _load_report()

    outcome = report["evidence_outcome"]
    assert outcome["outcome"] == "executed_live_private_droplet"
    assert outcome["live_private_droplet_evidence"] is True
    assert outcome["public_serving_evidence"] is False

    sidecar_suite = report["sidecar_suite"]
    assert sidecar_suite["openclaw_nemoclaw_are_protocol_substrates"] is False
    assert "openclaw_nemoclaw_local_bridge" in sidecar_suite["sidecars"]

    ufw = report["live_execution"]["ufw_after_hardening"]
    assert set(ufw) == {"ilc-node-2", "ilc-node-3", "ilc-node-6"}
    for rules in ufw.values():
        assert all("tailscale0" in rule for rule in rules)
        assert all("22/tcp" not in rule for rule in rules)


def test_phase_1322_remote_role_checks_preserve_local_only_nonclaims() -> None:
    report = _load_report()
    role_results = report["sidecar_suite"]["role_check_results"]

    node2 = role_results["ilc-node-2"]
    assert node2["admission_local_only"] is True
    assert node2["admission_public_p2p_enabled"] is False
    assert node2["admission_public_sidecar_serving_enabled"] is False

    node3 = role_results["ilc-node-3"]
    assert node3["verifier_local_only"] is True
    assert node3["verifier_public_api_enabled"] is False
    assert node3["projection_public_listener_enabled"] is False
    assert node3["projection_public_sidecar_projection_serving_enabled"] is False

    node6 = role_results["ilc-node-6"]
    assert node6["preview_binding"] == "local_import_only"
    assert node6["preview_public_p2p_enabled"] is False
    assert node6["wallet_write_authorized"] is False
    assert node6["value_ilc_settlement_authorized"] is False
