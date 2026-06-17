"""Phase 1545p-Fix41 LMDB rematerialization checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from tools.evaluators.sim_genesis_base_graph_lmdb_rematerialization_1545p_fix41 import (
    DEFAULT_CANDIDATE,
    _materialize,
)


ROOT = Path(__file__).resolve().parents[1]
DIGEST = ROOT / "out/genesis_base_graph_v0.4_lmdb_digest.json"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix41_lmdb_rematerialization_walkthrough.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix41_g10_lmdb_rematerialization.md"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix41_digest_records_fix41a_round_trip() -> None:
    payload = _read_json(DIGEST)

    assert payload["status"] == "PASS"
    assert payload["phase"] == "1545p-Fix41"
    assert payload["source_candidate"] == "fix41a"
    assert payload["source_candidate_path"] == "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
    assert payload["manifest"]["source_candidate"] == "fix41a"
    assert payload["manifest"]["candidate_phase"] == "1545p-Fix41a"
    assert payload["manifest"]["candidate_status"] == "unsigned_support_only_not_canonical_fix41a_authority_trace_candidate"
    assert all(payload["round_trip"].values())


def test_fix41_digest_counts_match_current_candidate() -> None:
    payload = _read_json(DIGEST)
    counts = payload["counts"]

    assert counts["source_node_count"] == 15676
    assert counts["source_edge_count"] == 75279
    assert counts["lmdb_node_count"] == counts["source_node_count"]
    assert counts["lmdb_edge_count"] == counts["source_edge_count"]
    assert counts["edge_ids_present"] == 49623
    assert counts["missing_edge_ids"] == 25656
    assert payload["tier_group_counts"] == {
        "canonical": 54,
        "private": 861,
        "support": 14761,
    }
    assert sum(payload["tier_group_counts"].values()) == counts["source_node_count"]


def test_fix41_digest_identity_is_exact_for_canonical_reexport() -> None:
    payload = _read_json(DIGEST)
    digests = payload["digests"]

    assert digests["source_canonical_sha256"] == digests["reexport_canonical_sha256"]
    assert digests["source_file_sha256"] == digests["reexport_file_sha256"]


def test_fix41_runner_regenerates_materialization_in_tmpdir(tmp_path: Path) -> None:
    payload = _materialize(
        candidate_path=DEFAULT_CANDIDATE,
        lmdb_root=tmp_path / "genesis_base_graph_v0.4.lmdb",
        reexport_path=tmp_path / "reexport.json",
        digest_path=tmp_path / "digest.json",
        walkthrough_path=tmp_path / "walkthrough.md",
        map_size=512 * 1024 * 1024,
    )

    assert payload["status"] == "PASS"
    assert payload["counts"]["source_node_count"] == 15676
    assert payload["counts"]["source_edge_count"] == 75279
    assert payload["round_trip"]["canonical_digest_match"] is True
    assert (tmp_path / "digest.json").exists()
    assert (tmp_path / "walkthrough.md").exists()


def test_genesis_atlas_candidate_store_synthetic_edge_keys_preserve_missing_edge_id_rows(tmp_path: Path) -> None:
    store = GenesisAtlasCandidateStore(tmp_path / "atlas", allow_synthetic_edge_keys=True)
    try:
        edges = [
            {"source": "node-a", "target": "node-b", "edge_type": "REFERENCES_AUTHORITY"},
            {"edge_id": "edge-explicit", "source": "node-b", "target": "node-c", "edge_type": "TESTS"},
        ]
        store.put_edges(edges)
        stored = store.iter_edges()
    finally:
        store.close()

    assert len(stored) == 2
    assert any("edge_id" not in edge for edge in stored)
    assert any(edge.get("edge_id") == "edge-explicit" for edge in stored)


def test_genesis_atlas_candidate_store_remains_strict_by_default(tmp_path: Path) -> None:
    store = GenesisAtlasCandidateStore(tmp_path / "atlas")
    try:
        with pytest.raises(ValueError, match="genesis_atlas_candidate_edge_missing_edge_id"):
            store.put_edges([{"source": "node-a", "target": "node-b"}])
    finally:
        store.close()


def test_fix41_prompt_and_walkthrough_preserve_boundaries() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert "genesis_atlas_enriched_candidate_fix41a.json" in prompt
    assert "post-Fix41a" in prompt
    assert "No Genesis v0.4 signing occurred." in walkthrough
    assert "No canonical Atlas mutation occurred." in walkthrough
    assert "not a signing authority" in walkthrough
