# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1567 topology deployment record regression tests."""

from __future__ import annotations

import json
from pathlib import Path


RECORD_JSON = Path("docs/sims/ilc_block6_tailscale_topology_record_1567_v0.1.json")
RECORD_MD = Path("docs/sims/ilc_block6_tailscale_topology_record_1567_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")


def _record() -> dict[str, object]:
    return json.loads(RECORD_JSON.read_text(encoding="utf-8"))


def test_phase_1567_records_passing_four_node_topology() -> None:
    record = _record()

    assert RECORD_MD.exists()
    assert record["four_node_reachability"] == "PASS"
    assert record["topology_verdict"] == "PASS"
    assert len(record["nodes"]) == 4
    assert len(record["logical_agents"]) == 7
    assert record["phase_1560_identity_consistency"] == "confirmed"


def test_phase_1567_openclaw_refresh_is_confirmed_without_clawhub_publication() -> None:
    skill = _record()["openclaw_ilc_local_skill"]

    assert skill["refresh_status"] == "PASS"
    assert skill["eligible"] is True
    assert skill["model_visible"] is True
    assert skill["command_visible"] is True
    assert skill["user_invocable"] is True
    assert skill["clawhub_published"] is False
    assert len(skill["sha256"]) == 64


def test_phase_1567_codex_harness_is_rehearsal_only() -> None:
    harness = _record()["codex_local_harness"]

    assert harness["command_surface_recorded"] is True
    assert harness["rehearsal_namespace_only"] is True
    assert harness["private_key_access"] is False
    assert harness["wallet_write_access"] is False
    assert harness["production_endpoint_access"] is False


def test_phase_1567_non_authorization_boundary_is_preserved() -> None:
    non_authorization = _record()["non_authorization"]

    assert non_authorization["public_p2p"] is False
    assert non_authorization["public_rc"] is False
    assert non_authorization["production_economics"] is False
    assert non_authorization["wallet_write"] is False
    assert non_authorization["epoch_transition"] is False


def test_phase_1567_completion_tokens_are_emitted() -> None:
    status = STATUS.read_text(encoding="utf-8")

    for token in [
        "block6_tailscale_topology_recorded_phase_1567",
        "four_node_topology_verified_phase_1567",
        "seven_logical_agents_assigned_phase_1567",
        "openclaw_ilc_local_skill_refresh_confirmed_phase_1567",
        "user_facing_balance_report_command_reachable_phase_1567",
        "public_p2p_not_activated_phase_1567",
        "public_path_remains_blocked_phase_1567",
    ]:
        assert token in status
