import json
from pathlib import Path


REPORT_PATH = Path(
    "docs/specs/ilc_ccss_005_private_openclaw_nemoclaw_droplet_dry_run_1328_v0.1.json"
)
REPORT_MD_PATH = Path(
    "docs/specs/ilc_ccss_005_private_openclaw_nemoclaw_droplet_dry_run_1328_v0.1.md"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1328_ccss_005_private_openclaw_nemoclaw_droplet_dry_run_walkthrough.md"
)

REQUIRED_TOKENS = [
    "ccss_005_private_openclaw_nemoclaw_droplet_dry_run_phase_1328.v0.1",
    "confidential_coordination_private_wiring_dry_run_recorded_phase_1328",
    "reproducibility_pass_recorded_phase_1328",
    "public_confidential_coordination_serving_not_enabled_phase_1328",
    "phase_1329_window_1317_1329_closure_next",
    "public_rc_remains_blocked_after_phase_1328",
]


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text())


def test_report_records_required_tokens_and_pass_status() -> None:
    report = _report()

    assert report["version"] == REQUIRED_TOKENS[0]
    assert report["required_tokens"] == REQUIRED_TOKENS
    assert report["status"] == "pass"
    assert report["execution_mode"] == "real_private_digitalocean_droplets_over_tailscale"
    assert report["dry_run_source_commit"] == "acc92d645055c4ea288aad947df0f54604975fc6"


def test_all_required_tokens_are_present_in_human_artifacts() -> None:
    report_md = REPORT_MD_PATH.read_text()
    walkthrough = WALKTHROUGH_PATH.read_text()

    for token in REQUIRED_TOKENS:
        assert token in report_md
        assert token in walkthrough


def test_private_droplet_mesh_and_git_state_are_recorded() -> None:
    report = _report()
    hosts = {entry["hostname"]: entry for entry in report["host_evidence"]}

    assert sorted(hosts) == ["ilc-node-2", "ilc-node-3", "ilc-node-6"]
    assert hosts["ilc-node-2"]["role"] == "coordinator"
    assert hosts["ilc-node-3"]["role"] == "verifier_projection"
    assert hosts["ilc-node-6"]["role"] == "harness_adapter"

    for host in hosts.values():
        assert host["repo_clean"] is True
        assert host["repo_head"] == report["dry_run_source_commit"]
        assert host["tailscale_ip_actual"] == host["tailscale_ip_expected"]
        assert host["python_version"] == "Python 3.10.12"
        assert host["ufw_tailscale_only_inbound"] is True
        assert host["openclaw_gateway_ports_18789_19001"] == []

    assert len(report["full_mesh_reachability"]) == 6
    assert {edge["result"] for edge in report["full_mesh_reachability"]} == {"ok"}


def test_openclaw_skill_is_local_only_and_no_public_gateway_is_running() -> None:
    report = _report()
    host6 = next(entry for entry in report["host_evidence"] if entry["hostname"] == "ilc-node-6")

    assert host6["openclaw_installed"] is True
    assert host6["openclaw_version"] == "OpenClaw 2026.5.7 (eeef486)"
    assert host6["openclaw_skill_ready"] is True
    assert host6["openclaw_skill_info"] == {
        "available_as_command": True,
        "path": "~/.openclaw/workspace/skills/ilc-local/SKILL.md",
        "source": "openclaw-workspace",
        "visible_to_model": True,
    }
    assert report["nemoclaw_status"]["installed"] is False

    call = report["harness_adapter_calls"][0]
    assert call["host"] == "ilc-node-6"
    assert call["harness"] == "OpenClaw"
    assert call["binding"] == "local_import_only"
    assert call["openclaw_dependency_required"] is False
    assert call["response_shape"]["transport_address"] is None
    assert call["response_shape"]["storage_key"] is None


def test_ccss_profile_and_sample_states_are_reproducible_private_local() -> None:
    report = _report()

    assert report["confidential_profile_required_sidecars"] == [
        "confidential_coordination_capability_membership_boundary",
        "confidential_coordination_gossip_jitter_cover_policy",
        "confidential_coordination_local_preview",
        "confidential_coordination_private_gated_shard",
        "confidential_coordination_sealed_sender_local_delivery",
        "local_graph_memory_projection",
        "openclaw_nemoclaw_local_bridge",
        "sidecar_registry_manifest",
    ]

    samples = report["ccss_sample_records"]
    assert samples["header_envelope_count"] == 1
    assert samples["access_state"] == "active_local"
    assert samples["access_allowed"] is True
    assert samples["sealed_delivery_state"] == "sealed_delivered_local"
    assert samples["gossip_decision_state"] == "announce_pending_local"
    assert samples["gossip_action_allowed"] is True
    assert samples["jitter_epoch"] == 1331


def test_public_and_sensitive_authority_remains_blocked() -> None:
    report = _report()

    assert report["registry_public_flags"] == {
        "public_confidential_coordination_serving_enabled": False,
        "public_confidential_messaging_claimed": False,
        "public_serving_enabled": False,
    }

    non_authorization = report["non_authorization"]
    for key, value in non_authorization.items():
        assert value is False, key
