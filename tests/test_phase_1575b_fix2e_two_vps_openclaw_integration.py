from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from ilc_core.sidecars.openclaw_local_capture import raw_payload_sha256

RUNNER = Path("tools/openclaw_two_vps_integration_rehearsal.py")


def _run_fixture(tmp_path: Path) -> dict[str, object]:
    evidence_path = Path("out/block6_openclaw_two_vps_fix2e/evidence_records.json")
    if evidence_path.exists():
        evidence_path.unlink()
    subprocess.run([sys.executable, str(RUNNER), "--fixture"], check=True)
    return json.loads(evidence_path.read_text(encoding="utf-8"))


def test_fixture_mode_evidence_contains_required_named_gap_fields(tmp_path: Path) -> None:
    evidence = _run_fixture(tmp_path)
    assert evidence["cross_node_replay_prevention_gap"] == "redeemer_key_binding_required"
    assert evidence["distributed_task_reservation_gap"] == "shared_coordinator_required"
    assert evidence["semantic_duplicate_detection_gap"] == "future_graph_intelligence_required"


def test_evidence_writer_redacts_private_ips_and_invite_material(tmp_path: Path) -> None:
    _run_fixture(tmp_path)
    body = Path("out/block6_openclaw_two_vps_fix2e/evidence_records.json").read_text(encoding="utf-8")
    assert re.search(r"\b100\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", body) is None
    assert "private_invite_nonce" not in body
    assert "nonce_hex" not in body
    assert "mnemonic" not in body.lower()
    assert "bearer" not in body.lower()


def test_per_node_nullifier_persistence_is_represented_independently_for_two_nodes(tmp_path: Path) -> None:
    evidence = _run_fixture(tmp_path)
    nodes = evidence["nodes"]
    assert len(nodes) == 2
    labels = {node["node_label"] for node in nodes}
    assert labels == {"vps_a", "vps_b"}
    for node in nodes:
        assert node["bootstrap"]["bootstrap_allowed"] is True
        assert node["bootstrap"]["nullifier_persisted_after_restart"] is True
        assert node["bootstrap"]["replay_defect_token"] == "replayed_nullifier"


def test_cross_node_replay_is_not_claimed_as_prevented(tmp_path: Path) -> None:
    evidence = _run_fixture(tmp_path)
    assert evidence["cross_node_replay_gap"]["first_node_allowed"] is True
    assert evidence["cross_node_replay_gap"]["second_node_allowed_with_independent_store"] is True
    assert evidence["cross_node_replay_gap"]["cross_node_replay_prevented_by_local_nullifiers"] is False


def test_distributed_reservation_is_not_claimed_as_solved(tmp_path: Path) -> None:
    evidence = _run_fixture(tmp_path)
    scheduler = evidence["scheduler_checks"]
    assert scheduler["distributed_task_reservation_solved"] is False
    assert scheduler["distributed_task_reservation_gap"] == "shared_coordinator_required"
    for result in scheduler["node_results"]:
        assert result["allowed_local_offer"] is True
        assert result["cap_block_reason"] == "per_agent_idle_window_cap_exceeded"
        assert result["diversity_block_reason"] == "per_task_type_idle_window_cap_exceeded"


def test_exact_duplicate_suppression_only_for_identical_raw_payload_hashes(tmp_path: Path) -> None:
    evidence = _run_fixture(tmp_path)
    exact = evidence["capture_checks"]["exact_duplicate"]
    semantic = evidence["capture_checks"]["semantic_duplicate"]
    assert exact["identical_raw_hashes_equal"] is True
    assert semantic["semantic_duplicate_detection_solved"] is False
    assert semantic["similar_payload_hash_equal"] is False
    assert raw_payload_sha256(
        {
            "candidate_node_type": "claim_candidate",
            "text": "The same OpenClaw output bytes should hash identically across nodes.",
        }
    ) == exact["raw_payload_sha256"]


def test_ilc_status_records_are_node_scoped(tmp_path: Path) -> None:
    evidence = _run_fixture(tmp_path)
    statuses = evidence["capture_checks"]["status_records"]
    assert {status["node_label"] for status in statuses} == {"vps_a", "vps_b"}
    for status in statuses:
        assert status["status"]["local_queue_count"] == 1
        assert status["status"]["public_submission_performed"] is False
        assert status["local_agent_id"].endswith(status["node_label"])


def test_runner_refuses_real_vps_execution_without_explicit_targets() -> None:
    env = dict(os.environ)
    env.pop("ILC_FIX2E_VPS_A", None)
    env.pop("ILC_FIX2E_VPS_B", None)
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--real"],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )
    assert result.returncode == 2
    assert "fix2e_real_vps_targets_required" in result.stderr
