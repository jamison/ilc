from __future__ import annotations

import json
from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1322_g8_restore_vps_git_workflow_fix1.md"
)
REPORT_JSON = ROOT / "docs/specs/ilc_phase_1322_fix1_vps_git_workflow_restore_v0.1.json"
REPORT_MD = ROOT / "docs/specs/ilc_phase_1322_fix1_vps_git_workflow_restore_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md"

REQUIRED_TOKENS = {
    "phase_1322_fix1_restore_vps_git_workflow.v0.1",
    "remote_rsync_tree_provenance_blocker_resolved_phase_1322_fix1",
    "vps_git_clone_head_matches_local_commit_phase_1322_fix1",
    "sync_repo_git_workflow_restored_phase_1322_fix1",
    "phase_1323_remote_sync_precondition_cleared_phase_1322_fix1",
    "public_rc_remains_blocked_after_phase_1322_fix1",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _report() -> dict[str, object]:
    return json.loads(_text(REPORT_JSON))


def test_phase_1322_fix1_prompt_matches_schema() -> None:
    assert validate(PROMPT) == []


def test_phase_1322_fix1_tokens_and_canonical_json() -> None:
    report_text = _text(REPORT_JSON)
    md_text = _text(REPORT_MD)
    status = _text(STATUS)
    planning = _text(PLANNING)
    capsule = _text(CAPSULE)
    report = _report()

    for token in REQUIRED_TOKENS:
        assert token in report_text
        assert token in md_text
        assert token in status
        assert token in planning
        assert token in capsule

    canonical = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    assert report_text == canonical


def test_phase_1322_fix1_restores_git_workflow_on_all_nodes() -> None:
    report = _report()
    nodes = report["remote_nodes"]
    assert isinstance(nodes, list)
    assert len(nodes) == 3

    expected_hosts = {"ilc-node-2", "ilc-node-3", "ilc-node-6"}
    assert {node["hostname"] for node in nodes} == expected_hosts

    for node in nodes:
        assert node["git_dir_present"] is True
        assert node["head"] == report["local_commit"]["head"]
        assert node["head_matches_local_commit"] is True
        assert node["branch"] == "main"
        assert node["origin_url"] == "git@github.com:jamison/ilc-core.git"
        assert node["repo_status_short_count"] == 0
        assert node["sync_repo_ok"] is True
        assert node["backup_path"].startswith("/opt/ilc/current.rsync_backup_phase1322_fix1_")
        assert node["ahead_behind_origin_main"] == "0 3"
        assert node["venv_non_ilcops_owned_count"] == 0
        assert node["sidecars"] == 10
        assert node["sidecar_profiles"] == 3

    assert report["sync_repo_result"]["result"] == "pass"
    assert report["origin_state"]["local_main_ahead_of_origin_main_by_commits"] == 3
    assert report["local_commit"]["publication_to_github_authorized"] is False


def test_phase_1322_fix1_preserves_non_authorization_floor() -> None:
    report = _report()

    assert all(value is False for value in report["non_authorization_floor"].values())
    assert report["operator_scope"]["private_overlay_only"] is True
    assert report["operator_scope"]["phase_1323_authorized"] is False
    assert report["operator_scope"]["public_inbound_exposure_changed"] is False

    for path in (REPORT_MD, STATUS, PLANNING, CAPSULE):
        text = _text(path)
        assert "Phase 1323" in text
        assert "requires explicit `GO Phase 1323`" in text
        assert "public_rc_remains_blocked_after_phase_1322_fix1" in text
