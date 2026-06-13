"""Phase 1545p-Fix22 full repo Genesis Atlas candidate checks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_JSON = ROOT / "out/sim_full_repo_genesis_atlas_1545p_fix22.json"
GRAPH_JSON = ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
PREIMAGES_JSONL = ROOT / "out/genesis_atlas_full_repo_node_preimages_1545p_fix22.jsonl"
REPORT_MD = ROOT / "docs/sims/sim_full_repo_genesis_atlas_1545p_fix22_v0.1.md"
REVIEW_MD = ROOT / "docs/specs/ilc_full_repo_genesis_atlas_candidate_review_packet_1545p_fix22_v0.1.md"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_full_repo_candidate_outputs_exist_and_pass() -> None:
    for path in (SIM_JSON, GRAPH_JSON, PREIMAGES_JSONL, REPORT_MD, REVIEW_MD):
        assert path.exists(), path

    payload = _read_json(SIM_JSON)
    assert payload["status"] == "PASS"
    assert payload["sim_id"] == "SIM-FULL-REPO-GENESIS-ATLAS-01"
    assert payload["phase"] == "1545p-Fix22"


def test_full_repo_candidate_covers_every_tracked_file_in_snapshot() -> None:
    payload = _read_json(SIM_JSON)
    metrics = payload["metrics"]

    assert metrics["tracked_file_count"] > 9000
    assert metrics["file_node_count"] == metrics["tracked_file_count"]
    assert metrics["preimage_count"] == metrics["tracked_file_count"]
    assert metrics["endpoint_error_count"] == 0
    assert metrics["unreachable_node_count"] == 0
    assert metrics["root_reachable_ratio"] == f"{metrics['node_count']}/{metrics['node_count']}"
    assert all(metrics["sim_battery"].values())


def test_full_repo_candidate_keeps_public_private_and_generated_tiers() -> None:
    payload = _read_json(SIM_JSON)
    counts = payload["metrics"]["publish_status_counts"]

    assert counts["public_release_candidate_material"] > 0
    assert counts["generated_evidence_material"] > 0
    assert counts["genesis_private_or_public_rc_excluded"] > 0
    assert counts["genesis_private_historical_material"] > 0
    assert counts["agent_harness_private_material"] > 0


def test_full_repo_candidate_preimages_are_deterministic_and_unsigned() -> None:
    lines = PREIMAGES_JSONL.read_text(encoding="utf-8").splitlines()
    payload = _read_json(SIM_JSON)
    assert len(lines) == payload["metrics"]["tracked_file_count"]

    first = json.loads(lines[0])
    assert first["signature_status"] == "unsigned_candidate_preimage"
    assert "source_sha256" in first
    assert "source_path" in first


def test_full_repo_candidate_non_claim_boundary_is_explicit() -> None:
    graph = _read_json(GRAPH_JSON)
    joined_non_claims = "\n".join(graph["non_claims"])

    assert graph["candidate_status"] == "unsigned_support_only_not_canonical"
    assert graph["self_reference_boundary"].startswith("Fix22 generated artifacts")
    assert "no_genesis_v04_signing" in joined_non_claims
    assert "no_public_rc_activation" in joined_non_claims
    assert "no_canonical_genesis_mutation" in joined_non_claims
    assert "no_runtime_activation" in joined_non_claims
