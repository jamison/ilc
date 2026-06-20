"""Phase 1545p-Fix23 Genesis Atlas LMDB materialization checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION,
    GenesisAtlasCandidateStore,
)


ROOT = Path(__file__).resolve().parents[1]
SIM_JSON = ROOT / "out/sim_genesis_atlas_lmdb_materialization_1545p_fix23.json"
REPORT_MD = ROOT / "docs/sims/sim_genesis_atlas_lmdb_materialization_1545p_fix23_v0.1.md"
REVIEW_MD = ROOT / "docs/specs/ilc_genesis_atlas_lmdb_materialization_review_1545p_fix23_v0.1.md"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix23_materialization_evidence_passes_round_trip() -> None:
    payload = _read_json(SIM_JSON)
    assert payload["status"] == "PASS"
    assert payload["adapter_version"] == GENESIS_ATLAS_CANDIDATE_LMDB_ADAPTER_VERSION
    assert payload["sim_id"] == "SIM-GENESIS-ATLAS-LMDB-MATERIALIZATION-01"
    assert all(payload["materialization"]["round_trip"].values())


def test_fix23_materialization_counts_match_fix22_full_candidate() -> None:
    payload = _read_json(SIM_JSON)
    counts = payload["materialization"]["counts"]

    assert counts["source_node_count"] == 10029
    assert counts["source_edge_count"] == 27668
    assert counts["source_preimage_count"] == 9923
    assert counts["lmdb_node_count"] == counts["source_node_count"]
    assert counts["lmdb_edge_count"] == counts["source_edge_count"]
    assert counts["lmdb_preimage_count"] == counts["source_preimage_count"]
    assert counts["public_release_candidate_node_index_count"] == 6773
    assert counts["private_excluded_node_index_count"] == 804
    assert counts["generated_evidence_node_index_count"] == 2289


def test_fix23_materialization_digest_identity_is_recorded() -> None:
    payload = _read_json(SIM_JSON)
    source = payload["materialization"]["source_digests"]
    lmdb = payload["materialization"]["lmdb_digests"]

    assert source["nodes_digest"] == lmdb["nodes_digest"]
    assert source["edges_digest"] == lmdb["edges_digest"]
    assert source["preimages_digest"] == lmdb["preimages_digest"]


def test_genesis_atlas_candidate_store_indexes_nodes(tmp_path: Path) -> None:
    store = GenesisAtlasCandidateStore(tmp_path / "atlas")
    try:
        store.put_nodes(
            [
                {
                    "candidate_id": "node-a",
                    "source_path": "a.md",
                    "tier": "public_release_candidate_material",
                },
                {
                    "candidate_id": "node-b",
                    "source_path": "b.md",
                    "tier": "genesis_private_or_public_rc_excluded",
                },
            ]
        )
        store.put_edges([{"edge_id": "edge-a", "source": "node-a", "target": "node-b"}])
        store.put_preimages(
            [
                {"node_id": "node-a", "source_path": "a.md"},
                {"edge_id": "edge-a", "source": "node-a", "target": "node-b"},
            ]
        )

        assert store.get_node("node-a")["source_path"] == "a.md"
        assert store.get_edge("edge-a")["target"] == "node-b"
        assert store.get_preimage("node-a")["source_path"] == "a.md"
        assert store.get_preimage("edge-a")["target"] == "node-b"
        assert [row.get("node_id", row.get("edge_id")) for row in store.iter_preimages()] == [
            "node-a",
            "edge-a",
        ]
        assert store.node_ids_by_tier("public_release_candidate_material") == ["node-a"]
        assert store.node_ids_by_source_path("b.md") == ["node-b"]
    finally:
        store.close()


def test_genesis_atlas_candidate_store_fails_closed_on_missing_ids(tmp_path: Path) -> None:
    store = GenesisAtlasCandidateStore(tmp_path / "atlas")
    try:
        with pytest.raises(ValueError, match="genesis_atlas_candidate_node_missing_candidate_id"):
            store.put_nodes([{"tier": "public_release_candidate_material"}])
        with pytest.raises(ValueError, match="genesis_atlas_candidate_edge_missing_edge_id"):
            store.put_edges([{"source": "a", "target": "b"}])
        with pytest.raises(ValueError, match="genesis_atlas_candidate_preimage_missing_node_or_edge_id"):
            store.put_preimages([{"source_path": "a.md"}])
    finally:
        store.close()


def test_fix23_non_claim_boundary_docs_are_present() -> None:
    report = REPORT_MD.read_text(encoding="utf-8")
    review = REVIEW_MD.read_text(encoding="utf-8")

    assert "No Genesis v0.4 signing occurred." in report
    assert "No public graph publication occurred." in report
    assert "not canonical graph state" in review
