"""Phase 1145 — SIM-SPECTRAL-03 Run 01 evidence tests."""

from __future__ import annotations

import json
import pathlib
from collections import Counter


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/sim_spectral_03_run01_summary.json"
RAW_NOTES = ROOT / "docs/sims/sim_spectral_03/run01_raw_notes_1145.md"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.1.json"


def _summary() -> list[dict[str, object]]:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_r1_summary_exists_and_is_valid_json() -> None:
    data = _summary()
    assert len(data) == 333


def test_r2_track_a_contains_all_required_scenarios() -> None:
    data = _summary()
    track_a_scenarios = {row["scenario"] for row in data if row.get("track") == "A"}
    assert {"S1", "S2", "S3", "S4", "G1", "G2", "G3"} <= track_a_scenarios


def test_r3_raw_notes_exist_with_phase_token() -> None:
    text = RAW_NOTES.read_text(encoding="utf-8")
    assert "sim_spectral_03_run01_committed_phase_1145" in text
    assert "Authority-grounded Genesis nodes: 32/32" in text


def test_r4_s1_entries_use_signed_genesis_star_map() -> None:
    data = _summary()
    s1_rows = [row for row in data if row["scenario"] == "S1"]
    assert s1_rows
    assert all(row["s1_topology"] == "genesis-star-map" for row in s1_rows)
    assert all(row["laplacian_source"] == "genesis_star_map" for row in s1_rows)
    assert all(row["s1_topology_file"] == "out/genesis_core_star_map_v0.1.json" for row in s1_rows)
    assert all(row["node_count"] == 32 for row in s1_rows)
    assert all(row["topology_diagnostics"]["edge_count"] == 55 for row in s1_rows)


def test_r5_non_s1_entries_do_not_use_star_map_topology_file() -> None:
    data = _summary()
    non_s1_rows = [row for row in data if row["scenario"] != "S1"]
    assert non_s1_rows
    assert all(row["s1_topology_file"] is None for row in non_s1_rows)
    assert all(row["laplacian_source"] != "genesis_star_map" for row in non_s1_rows)


def test_r6_signed_star_map_still_has_32_signed_nodes() -> None:
    star_map = json.loads(STAR_MAP.read_text(encoding="utf-8"))
    nodes = star_map["nodes"]
    assert len(nodes) == 32
    assert len(star_map["edges"]) == 55
    assert all(node["genesis_attested"] is True for node in nodes)
    assert all(node["signature_status"] == "signed" for node in nodes)
    assert all(node["star_map_version"] == "v0.1" for node in nodes)


def test_r7_run_matrix_preserves_corrected_run02_scope() -> None:
    data = _summary()
    scenario_counts = Counter(row["scenario"] for row in data)
    assert scenario_counts == {
        "S1": 117,
        "S2": 54,
        "S3": 54,
        "S4": 54,
        "G1": 18,
        "G2": 18,
        "G3": 18,
    }
