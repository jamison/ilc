"""Phase 1545p-Fix54 unified LMDB materialization checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.evaluators.sim_genesis_base_graph_unified_lmdb_materialization import (
    DEFAULT_CANDIDATE,
    _materialize,
)


ROOT = Path(__file__).resolve().parents[1]
DIGEST = ROOT / "out/genesis_base_graph_v0.4_unified_lmdb_digest.json"
COMPARISON = ROOT / "out/genesis_base_graph_v0.4_unified_lmdb_candidate_comparison.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix54_unified_lmdb_materialization_walkthrough.md"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix54_digest_records_fix53_source_candidate() -> None:
    payload = _read_json(DIGEST)

    assert payload["status"] == "PASS"
    assert payload["phase"] == "1545p-Fix54"
    assert payload["source_candidate"] == "fix53"
    assert payload["source_candidate_path"] == "out/atlas_research/genesis_atlas_enriched_candidate_fix53.json"
    assert payload["manifest"]["source_candidate"] == "fix53"
    assert payload["manifest"]["source_candidate_path"] == payload["source_candidate_path"]
    assert all(payload["round_trip"].values())


def test_fix54_counts_match_corrected_fix53_candidate() -> None:
    payload = _read_json(DIGEST)
    counts = payload["counts"]

    assert counts["source_node_count"] == 15677
    assert counts["source_edge_count"] == 74981
    assert counts["lmdb_node_count"] == counts["source_node_count"]
    assert counts["lmdb_edge_count"] == counts["source_edge_count"]
    assert counts["duplicate_explicit_edge_ids"] == 0
    assert sum(payload["tier_group_counts"].values()) == counts["source_node_count"]


def test_fix54_digest_identity_is_exact_for_canonical_reexport() -> None:
    payload = _read_json(DIGEST)
    digests = payload["digests"]

    assert digests["source_canonical_sha256"] == digests["reexport_canonical_sha256"]
    assert digests["source_file_sha256"] == digests["reexport_file_sha256"]


def test_fix54_comparison_marks_fix53_as_exact_source() -> None:
    comparison = _read_json(COMPARISON)
    rows = comparison["candidate_lineage_comparison"]
    source_rows = [row for row in rows if row["is_source_candidate"]]

    assert len(source_rows) == 1
    source = source_rows[0]
    assert source["candidate_path"] == "out/atlas_research/genesis_atlas_enriched_candidate_fix53.json"
    assert source["missing_nodes_from_unified"] == 0
    assert source["missing_semantic_edges_from_unified"] == 0
    assert source["unified_extra_nodes_vs_candidate"] == 0
    assert source["unified_extra_semantic_edges_vs_candidate"] == 0


def test_fix54_runner_regenerates_materialization_in_tmpdir(tmp_path: Path) -> None:
    if not DEFAULT_CANDIDATE.exists():
        pytest.skip("Fix54 source candidate is gitignored; regenerate Fix53 locally first")

    payload = _materialize(
        candidate_path=DEFAULT_CANDIDATE,
        lmdb_root=tmp_path / "genesis_base_graph_v0.4_unified.lmdb",
        reexport_path=tmp_path / "reexport.json",
        digest_path=tmp_path / "digest.json",
        comparison_path=tmp_path / "comparison.json",
        walkthrough_path=tmp_path / "walkthrough.md",
        map_size=512 * 1024 * 1024,
    )

    assert payload["status"] == "PASS"
    assert payload["counts"]["source_node_count"] == 15677
    assert payload["counts"]["source_edge_count"] == 74981
    assert payload["round_trip"]["canonical_digest_match"] is True
    assert (tmp_path / "digest.json").exists()
    assert (tmp_path / "comparison.json").exists()
    assert (tmp_path / "walkthrough.md").exists()


def test_fix54_walkthrough_preserves_boundaries() -> None:
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert "genesis_atlas_enriched_candidate_fix53.json" in walkthrough
    assert "not a signing authority" in walkthrough
    assert "No Genesis v0.4 signing occurred." in walkthrough
    assert "No canonical Atlas mutation occurred." in walkthrough
