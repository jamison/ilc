"""Phase 1545p-Fix55 LMDB graph_projection classification checks."""

from __future__ import annotations

import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
REPORT = ROOT / "out/genesis_atlas_fix55_projection_classification_report_v0.1.json"
FIEDLER_REPORT = ROOT / "out/genesis_atlas_fix55_fiedler_projection_analysis_v0.1.json"
LMDB_ROOT = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _nodes() -> list[dict]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        return store.iter_nodes()
    finally:
        store.close()


def _graph_payload() -> dict:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        payload = store.get_graph_payload()
        assert isinstance(payload, dict)
        return payload
    finally:
        store.close()


def _meta() -> dict | None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        return store.get_meta("fix55_graph_projection_classification")
    finally:
        store.close()


def test_fix55_complete_token_in_status() -> None:
    text = STATUS.read_text(encoding="utf-8")

    assert "fix55_complete" in text


def test_fix55_report_exists_and_valid() -> None:
    payload = _read_json(REPORT)

    assert payload["status"] == "PASS"
    assert payload["phase"] == "1545p-Fix55"
    assert payload["total_nodes_classified"] == 15677
    assert set(payload["value_counts"]) == {
        "excluded_private_material",
        "genesis_core_star_map",
        "public_protocol_graph",
        "review_required",
        "support_candidate_graph",
    }


def test_fix55_zero_nodes_missing_graph_projection() -> None:
    nodes = _nodes()

    assert len(nodes) == 15677
    assert sum(1 for node in nodes if not node.get("graph_projection")) == 0


def test_fix55_all_nodes_classified() -> None:
    payload = _read_json(REPORT)

    assert payload["nodes_with_projection_after"] == 15677


def test_fix55_private_nodes_excluded() -> None:
    nodes = _nodes()
    private_nodes = [node for node in nodes if node.get("node_kind") == "genesis_private_material_node"]

    assert len(private_nodes) == 475
    assert all(node.get("graph_projection") == "excluded_private_material" for node in private_nodes)
    assert _read_json(REPORT)["private_node_count"] == 475


def test_fix55_legacy_core_star_map_migrated() -> None:
    nodes = _nodes()

    assert all(node.get("graph_projection") != "core_star_map" for node in nodes)


def test_fix55_genesis_core_star_map_is_not_empty() -> None:
    payload = _read_json(REPORT)

    assert payload["value_counts"]["genesis_core_star_map"] >= 54


def test_fix55_review_required_under_threshold() -> None:
    payload = _read_json(REPORT)

    assert payload["value_counts"]["review_required"] <= 500


def test_fix55_lmdb_node_count_unchanged() -> None:
    assert len(_nodes()) == 15677


def test_fix55_meta_entry_present() -> None:
    payload = _meta()

    assert isinstance(payload, dict)
    assert payload["status"] == "PASS"


def test_fix55_graph_payload_in_sync() -> None:
    payload = _graph_payload()
    nodes = payload["nodes"]

    assert len(nodes) == 15677
    assert all(isinstance(node.get("graph_projection"), str) and node["graph_projection"] for node in nodes)


def test_fix55_digest_proof_valid() -> None:
    payload = _read_json(REPORT)
    proof = payload["digest_proof"]

    assert proof["pre_post_differ"] is True
    assert proof["node_count_unchanged"] is True
    assert proof["edge_count_unchanged"] is True
    assert proof["only_graph_projection_field_changed"] is True


def test_fix55_fiedler_report_exists() -> None:
    payload = _read_json(FIEDLER_REPORT)
    projections = payload["projections"]

    assert payload["status"] == "PASS"
    assert set(projections) == {"all_local", "authority_only", "public_eligible"}
    assert projections["all_local"]["node_count"] == 15677
    assert projections["public_eligible"]["node_count"] == 15195
    assert projections["authority_only"]["fiedler_value_lambda2"] == 0.0
