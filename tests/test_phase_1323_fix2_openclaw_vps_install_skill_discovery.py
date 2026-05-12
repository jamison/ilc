from __future__ import annotations

import json
from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1323_g8_openclaw_vps_install_skill_discovery_fix2.md"
)
REPORT_JSON = (
    ROOT / "docs/specs/ilc_phase_1323_fix2_openclaw_vps_install_skill_discovery_v0.1.json"
)
REPORT_MD = (
    ROOT / "docs/specs/ilc_phase_1323_fix2_openclaw_vps_install_skill_discovery_v0.1.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1323_fix2_openclaw_vps_install_skill_discovery_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md"

REQUIRED_TOKENS = {
    "phase_1323_fix2_openclaw_vps_install_skill_discovery.v0.1",
    "openclaw_cli_installed_on_private_vps_phase_1323_fix2",
    "local_ilc_skill_draft_discovered_by_openclaw_phase_1323_fix2",
    "openclaw_gateway_not_started_phase_1323_fix2",
    "clawhub_publication_not_authorized_phase_1323_fix2",
    "ilc_runtime_not_modified_phase_1323_fix2",
    "public_rc_remains_blocked_after_phase_1323_fix2",
    "phase_1324_ccss_private_gated_shard_contract_next_after_fix2",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _report() -> dict[str, object]:
    return json.loads(_text(REPORT_JSON))


def test_phase_1323_fix2_prompt_matches_schema() -> None:
    assert validate(PROMPT) == []


def test_phase_1323_fix2_report_is_canonical_and_tokens_are_recorded() -> None:
    report_text = _text(REPORT_JSON)
    report = _report()

    assert report_text == json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert set(report["required_tokens"]) == REQUIRED_TOKENS
    assert report["fix2_version"] == "phase_1323_fix2_openclaw_vps_install_skill_discovery.v0.1"
    assert report["result"] == "pass_discovery_with_carry_forward"

    combined = "\n".join(_text(path) for path in (REPORT_MD, WALKTHROUGH, STATUS, PLANNING, CAPSULE))
    for token in REQUIRED_TOKENS:
        assert token in combined


def test_phase_1323_fix2_installs_openclaw_without_starting_gateway() -> None:
    report = _report()
    install = report["installation"]
    gateway = report["gateway_state"]
    remote = report["remote_node"]

    assert install["openclaw_cli_installed_on_private_vps_phase_1323_fix2"] is True
    assert install["openclaw_version"] == "OpenClaw 2026.5.7 (eeef486)"
    assert install["node_version"] == "v24.15.0"
    assert install["onboarding_skipped"] is True
    assert install["clawhub_present"] is False
    assert gateway["openclaw_gateway_not_started_phase_1323_fix2"] is True
    assert gateway["listening_on_18789_or_19001"] is False
    assert gateway["configured_as_loopback_only"] is True
    assert remote["hostname"] == "ilc-node-6"
    assert remote["git_head"] == "4ea3d0857764075b88775b25f1d31e1e252df855"
    assert remote["repo_status_short_count"] == 0


def test_phase_1323_fix2_local_skill_is_discovered_without_public_installability() -> None:
    skill = _report()["draft_skill"]

    assert skill["name"] == "ilc-local"
    assert skill["source"] == "openclaw-workspace"
    assert skill["eligible"] is True
    assert skill["model_visible"] is True
    assert skill["command_visible"] is True
    assert skill["user_invocable"] is True
    assert skill["requirements"]["bins"] == ["python3"]
    assert skill["requirements"]["env"] == []
    assert skill["install_actions"] == []
    assert skill["missing_requirements"] == {
        "anyBins": [],
        "bins": [],
        "config": [],
        "env": [],
        "os": [],
    }
    assert skill["public_installability_claimed"] is False
    assert skill["corrected_after_first_probe"] is True


def test_phase_1323_fix2_safe_ilc_preview_remains_non_activating() -> None:
    preview = _report()["ilc_preview_result"]

    assert preview["ilc_runtime_not_modified_phase_1323_fix2"] is True
    assert preview["preview_binding"] == "local_import_only"
    assert preview["preview_openclaw_dependency_required"] is False
    assert preview["profile_id"] == "openclaw_claimable_local_bridge"
    assert preview["package_profile_id"] == "openclaw_skill_claimable"
    assert preview["public_claimability_runtime_activated"] is False
    assert preview["public_p2p_activated"] is False
    assert preview["public_serving_enabled"] is False
    assert preview["registry_public_rc_claimed"] is False


def test_phase_1323_fix2_non_authorization_floor_blocks_public_and_identity_actions() -> None:
    floor = _report()["non_authorization_floor"]

    assert floor["clawhub_publication_not_authorized_phase_1323_fix2"] is True
    for key, value in floor.items():
        if key == "clawhub_publication_not_authorized_phase_1323_fix2":
            continue
        assert value is False

    for path in (REPORT_MD, WALKTHROUGH, STATUS, PLANNING, CAPSULE):
        text = _text(path)
        assert "public_rc_remains_blocked_after_phase_1323_fix2" in text
        assert "phase_1324_ccss_private_gated_shard_contract_next_after_fix2" in text
