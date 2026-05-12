from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = (
    ROOT
    / "docs/specs/ilc_openclaw_nemoclaw_claimable_profile_full_dry_run_1323_v0.1.json"
)
REPORT_MD = (
    ROOT
    / "docs/specs/ilc_openclaw_nemoclaw_claimable_profile_full_dry_run_1323_v0.1.md"
)
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1323_openclaw_nemoclaw_claimable_profile_full_dry_run_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md"

REQUIRED_TOKENS = {
    "openclaw_nemoclaw_claimable_profile_full_dry_run_phase_1323.v0.1",
    "claimable_profile_dry_run_public_claimability_still_gated_phase_1323",
    "graph_native_sidecar_suite_profile_integrity_rehearsed_phase_1323",
    "openclaw_nemoclaw_hosts_not_protocol_substrates_phase_1323",
    "openclaw_skill_format_discovery_required_phase_1323",
    "cli_first_skill_surface_recorded_phase_1323",
    "python_import_bridge_surface_recorded_phase_1323",
    "identity_seed_ux_public_bootstrap_blocker_phase_1323",
    "identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323",
    "openclaw_skill_not_published_or_installable_phase_1323",
    "genesis_rooted_agent_birth_attestation_blocker_phase_1323",
    "phase_1324_ccss_private_gated_shard_contract_next",
    "public_rc_remains_blocked_after_phase_1323",
}


def _report() -> dict[str, object]:
    return json.loads(REPORT_JSON.read_text(encoding="utf-8"))


def test_phase_1323_report_is_canonical_and_records_required_tokens() -> None:
    report_text = REPORT_JSON.read_text(encoding="utf-8")
    report = _report()

    assert report_text == json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert set(report["required_tokens"]) == REQUIRED_TOKENS
    assert report["schema_version"] == (
        "openclaw_nemoclaw_claimable_profile_full_dry_run_phase_1323.v0.1"
    )
    assert report["result"] == "pass_rehearsal_with_blockers"


def test_phase_1323_profile_integrity_preserves_public_claimability_gates() -> None:
    profile = _report()["profile_integrity"]

    assert profile["bridge_profile_id"] == "openclaw_claimable_local_bridge"
    assert profile["package_profile_id"] == "openclaw_skill_claimable"
    assert profile["package_profile_version"] == "public_rc_package_profiles_1307.v0.1"
    assert profile["claimable_profile_public_claimability_metadata"] is True
    assert profile["claimable_profile_public_claimability_runtime_activated"] is False
    assert profile["claimable_profile_public_p2p_activated"] is False
    assert profile["claimable_profile_public_serving_enabled"] is False
    assert profile["openclaw_nemoclaw_are_hosts_not_protocol_substrates"] is True
    assert profile["required_sidecars"] == [
        "offline_claimability_receipt_verifier",
        "openclaw_nemoclaw_local_bridge",
        "sidecar_registry_manifest",
        "value_path_activation_boundary_preflight",
        "wallet_action_semantics_preflight",
    ]


def test_phase_1323_remote_droplet_checks_are_private_and_non_activating() -> None:
    role_results = _report()["remote_role_results"]

    assert set(role_results) == {"ilc-node-2", "ilc-node-3", "ilc-node-6"}
    for node in role_results.values():
        assert node["git_head"] == "4ea3d0857764075b88775b25f1d31e1e252df855"
        assert node["openclaw_present"] is False
        assert node["clawhub_present"] is False
        assert node["local_skill_preview_binding"] == "local_import_only"
        assert node["local_skill_preview_openclaw_dependency_required"] is False
        assert node["local_skill_preview_public_claimability_enabled"] is False
        assert node["offline_verifier_local_only"] is True
        assert node["offline_verifier_public_api_enabled"] is False
        assert node["projection_local_only"] is True
        assert node["projection_public_listener_enabled"] is False
        assert node["projection_public_sidecar_projection_serving_enabled"] is False
        assert node["wallet_signing_authorized"] is False
        assert node["wallet_write_authorized"] is False
        assert node["value_ecu_mint_authorized"] is False
        assert node["value_ilc_settlement_authorized"] is False


def test_phase_1323_skill_and_bridge_surfaces_are_distinct() -> None:
    report = _report()
    surfaces = {entry["surface"]: entry for entry in report["surface_matrix"]}

    assert surfaces["cli_first_thin_skill"]["status"] == (
        "recorded_not_implemented_not_published_not_installable"
    )
    assert surfaces["cli_first_thin_skill"]["entry"] == (
        "SKILL.md guidance around ilc CLI commands"
    )
    assert surfaces["python_import_bridge"]["status"] == (
        "checked_in_and_remote_dry_run_passed"
    )
    assert surfaces["python_import_bridge"]["entry"] == (
        "execute_local_skill_preview with TransportHarness and StorageHarness protocols"
    )

    discovery = report["skill_format_discovery"]
    assert discovery["current_upstream_checked"] is True
    assert discovery["phase_1323_skill_artifact_created"] is False
    assert discovery["clawhub_publish_claimed"] is False
    assert "skill is a folder containing SKILL.md or skill.md" in discovery[
        "discovered_current_requirements"
    ]


def test_phase_1323_blockers_and_negative_checks_are_explicit() -> None:
    report = _report()

    assert report["public_rc_remains_blocked"] is True
    assert all(value is False for value in report["negative_checks"].values())

    identity = report["identity_seed_ux_blocker"]
    assert identity["blocker_token"] == "identity_seed_ux_public_bootstrap_blocker_phase_1323"
    assert identity["one_crypto_path_required"] is True
    assert identity["agent_mode_secret_output_required"] is True
    assert identity["llm_secret_visibility_allowed"] is False
    assert identity["secret_material_generated_in_phase_1323"] is False
    assert "genesis_record_schema.py currently computes bare sha384" in identity[
        "implementation_audit_note"
    ]

    birth = report["genesis_rooted_identity_origin_blocker"]
    assert birth["agent_birth_attestation_specified"] is False
    assert birth["genesis_rooted_public_bootstrap_claim_allowed"] is False
    assert birth["private_node_commitments_role"] == (
        "optional_birth_witnesses_not_identity_seed_entropy_or_recovery_material"
    )


def test_phase_1323_status_planning_capsule_and_walkthrough_record_tokens() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPORT_MD, WALKTHROUGH, STATUS, PLANNING, CAPSULE)
    )
    for token in REQUIRED_TOKENS:
        assert token in text

    assert "OpenClaw skill is already published" not in REPORT_MD.read_text(encoding="utf-8")
    assert "native OpenClaw skill installability" in REPORT_MD.read_text(encoding="utf-8")
