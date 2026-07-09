# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from pathlib import Path

from tools.sim.sim_ccss_side_channel_1573q import (
    RECOMMENDED_POLICY_TOKEN,
    VERDICT_REQUIRES_COVER_BATCHING,
    run_simulation,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "docs" / "sims" / "ilc_ccss_side_channel_sim_1573q_v0.1.json"
MD_PATH = REPO_ROOT / "docs" / "sims" / "ilc_ccss_side_channel_sim_1573q_v0.1.md"
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"


def test_phase_1573q_sim_output_files_exist_and_match_schema() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["schema_version"] == "ilc_ccss_side_channel_sim_1573q.v0.1"
    assert data["phase"] == "1573q"
    assert data["seed"] == 1573
    assert data["verdict"] == VERDICT_REQUIRES_COVER_BATCHING
    assert data["summary"]["supports_1573o_boundary"] is True
    assert data["summary"]["supports_stronger_anonymity_claim"] is False
    assert data["summary"]["supports_configured_anonymity_set_claim_with_1573r_design"] is True
    assert data["summary"]["recommended_policy"] == RECOMMENDED_POLICY_TOKEN
    assert data["non_authorizations"]["public_rc"] is False
    assert data["non_authorizations"]["guard_clearance"] is False
    assert MD_PATH.read_text(encoding="utf-8").startswith(
        "# ILC CCSS Side-Channel SIM 1573q v0.1"
    )


def test_phase_1573q_sim_is_deterministic() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert run_simulation() == data


def test_phase_1573q_timing_batching_reduces_but_does_not_prove_anonymity() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    timing = data["surfaces"]["timing_correlation"]
    unbatched = [
        point for point in timing if point["n"] == 100 and point["batch_window_seconds"] == 0.0
    ]
    batched = [
        point
        for point in timing
        if point["n"] == 100 and point["batch_window_seconds"] == 120.0
    ]
    assert max(point["linking_probability"] for point in unbatched) >= max(
        point["linking_probability"] for point in batched
    )
    assert data["summary"]["requires_batching_or_mixing"] is True


def test_phase_1573q_size_and_route_purpose_leak_cohort_information() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    size_points = data["surfaces"]["message_size_class"]
    route_points = data["surfaces"]["route_purpose"]
    for n in data["parameter_grid"]["n_values"]:
        baseline = 1 / n
        size_visible = next(
            point
            for point in size_points
            if point["n"] == n and point["fixed_bundle"] is False
        )
        route_visible = next(
            point
            for point in route_points
            if point["n"] == n and point["purpose_visible"] is True
        )
        assert size_visible["linking_probability"] > baseline
        assert route_visible["linking_probability"] > baseline


def test_phase_1573q_relay_path_rotation_is_required_for_stronger_claims() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    relay_points = data["surfaces"]["relay_overlap"]
    stable = [
        point for point in relay_points if point["n"] == 100 and point["rotate_paths"] is False
    ]
    rotated = [
        point for point in relay_points if point["n"] == 100 and point["rotate_paths"] is True
    ]
    assert max(point["linking_probability"] for point in stable) > max(
        point["linking_probability"] for point in rotated
    )
    assert data["summary"]["requires_relay_path_rotation_or_path_hiding"] is True


def test_phase_1573q_recommended_policy_combines_all_required_controls() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    controls = data["recommended_controls_for_1573r"]
    assert controls == {
        "batch_window_seconds": 120,
        "claim_shape": "configured_anonymity_set_and_metadata_minimization_claim_only",
        "cover_ratio": 8,
        "fixed_bundle": True,
        "min_batch_anonymity_set": 128,
        "offline_mailbox_policy_required": True,
        "policy_token": RECOMMENDED_POLICY_TOKEN,
        "relay_path_rotation": True,
        "route_purpose_visible_to_relay": False,
        "ttl_required": True,
    }
    recommended = [
        point
        for point in data["surfaces"]["mitigation_candidates"]
        if point["candidate"] == RECOMMENDED_POLICY_TOKEN
    ]
    current = [
        point
        for point in data["surfaces"]["mitigation_candidates"]
        if point["candidate"] == "current_no_cover_no_batch"
    ]
    assert max(point["worst"] for point in recommended) < max(
        point["worst"] for point in current
    )
    assert data["summary"]["recommended_policy_worst_linking_probability"] == max(
        point["worst"] for point in recommended
    )


def test_phase_1573q_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "ccss_side_channel_sim_committed_phase_1573q" in text
    assert "ccss_timing_size_relay_overlap_sim_recorded_phase_1573q" in text
    assert "ccss_side_channel_nonproof_boundary_recorded_phase_1573q" in text
    assert "ccss_cover_batching_requirement_routed_phase_1573q" in text
    assert "public_path_remains_blocked_phase_1573q" in text
