from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from tools.graph_viz_live_server import build_live_graph_payload, render_live_html


def _seed_lmdb(root: Path) -> None:
    store = GenesisAtlasCandidateStore(root)
    try:
        store.put_nodes(
            [
                {
                    "candidate_id": "artifact:genesis_intent_attestation_init_authority_map",
                    "graph_projection": "genesis_core_star_map",
                    "label": "Node 0",
                    "node_kind": "artifact",
                    "tier": "genesis_core",
                },
                {
                    "candidate_id": "truth_primitive:test",
                    "graph_projection": "genesis_core_star_map",
                    "label": "Truth primitive test",
                    "node_kind": "truth_primitive",
                    "tier": "genesis_core",
                },
            ]
        )
        store.put_edges(
            [
                {
                    "edge_id": "edge:test",
                    "edge_type": "GOVERNS",
                    "source_candidate_id": "artifact:genesis_intent_attestation_init_authority_map",
                    "target_candidate_id": "truth_primitive:test",
                }
            ]
        )
    finally:
        store.close()


def test_live_graph_payload_reads_current_lmdb_without_intermediary_file(tmp_path: Path) -> None:
    lmdb_root = tmp_path / "atlas.lmdb"
    _seed_lmdb(lmdb_root)

    payload = build_live_graph_payload(lmdb_root=lmdb_root, view="all-local")

    assert payload["metadata"]["intermediary_file_used"] is False
    assert payload["metadata"]["lmdb_digest_scope"] == "live_nodes_edges_row_store"
    assert payload["metadata"]["node_count"] == 2
    assert payload["metadata"]["edge_count"] == 1
    assert {node["id"] for node in payload["nodes"]} == {
        "artifact:genesis_intent_attestation_init_authority_map",
        "truth_primitive:test",
    }


def test_live_graph_payload_reflects_lmdb_refresh(tmp_path: Path) -> None:
    lmdb_root = tmp_path / "atlas.lmdb"
    _seed_lmdb(lmdb_root)
    first = build_live_graph_payload(lmdb_root=lmdb_root, view="all-local")

    store = GenesisAtlasCandidateStore(lmdb_root)
    try:
        nodes = store.iter_nodes()
        nodes.append(
            {
                "candidate_id": "policy:added_after_first_read",
                "graph_projection": "genesis_core_star_map",
                "label": "Added policy",
                "node_kind": "policy",
                "tier": "genesis_core",
            }
        )
        store.replace_nodes(nodes)
    finally:
        store.close()

    second = build_live_graph_payload(lmdb_root=lmdb_root, view="all-local")

    assert first["metadata"]["node_count"] == 2
    assert second["metadata"]["node_count"] == 3
    assert first["metadata"]["lmdb_digest_sha256"] != second["metadata"]["lmdb_digest_sha256"]


def test_live_graph_html_exposes_refresh_and_api_links(tmp_path: Path) -> None:
    lmdb_root = tmp_path / "atlas.lmdb"
    _seed_lmdb(lmdb_root)
    payload = build_live_graph_payload(lmdb_root=lmdb_root, view="all-local")

    rendered = render_live_html(graph_payload=payload, view="all-local", max_nodes=100)

    assert "Live LMDB mode: no out/viz_exports JSON intermediary" in rendered
    assert "/graph?view=all-local&amp;max_nodes=100" in rendered
    assert "/api/graph?view=all-local&amp;max_nodes=100" in rendered
    assert "Source:" in rendered
