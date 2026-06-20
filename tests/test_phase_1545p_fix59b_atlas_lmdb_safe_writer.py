from __future__ import annotations

from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    DEFAULT_PUBLIC_PATH_POLICY,
    deterministic_edge_id,
    repo_file_ref_id,
)


STATUS_PATH = Path("docs/phases/STATUS.md")
PROMPT_PATH = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1545p_fix59_g10_atlas_lmdb_safe_writer_contract_fix59b.md"
)


def _seed_lmdb(root: Path) -> None:
    store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
    try:
        nodes = [
            {
                "candidate_id": "node:a",
                "graph_projection": "support_candidate_graph",
                "node_kind": "support_node",
                "source_path": "a.md",
                "tier": "support_candidate",
            },
            {
                "candidate_id": "node:b",
                "graph_projection": "support_candidate_graph",
                "node_kind": "support_node",
                "source_path": "b.md",
                "tier": "support_candidate",
            },
        ]
        edge = {
            "edge_id": deterministic_edge_id("node:a", "REFERENCES_AUTHORITY", "node:b"),
            "edge_type": "REFERENCES_AUTHORITY",
            "source": "node:a",
            "src": "node:a",
            "target": "node:b",
            "tgt": "node:b",
        }
        store.put_nodes(nodes)
        store.put_edges([edge])
        store.put_graph_payload({"nodes": nodes, "edges": [edge]})
    finally:
        store.close()


def test_fix59b_prompt_validates_required_surface() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    assert "Fix59b Atlas LMDB Safe Writer Contract" in text
    assert "## LMDB Node Registration" in text
    assert "No ellipses in walkthrough." in text


def test_fix59b_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix59b_atlas_lmdb_safe_writer_committed" in text
    assert "fix59b_writer_rebuilds_payload_and_indexes" in text
    assert "fix59b_writer_rejects_dangling_edges" in text
    assert "fix59b_phase_file_registration_helper_committed" in text
    assert "fix59b_complete" in text


def test_safe_writer_dry_run_does_not_mutate(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                nodes_to_add=[
                    {
                        "candidate_id": "node:c",
                        "graph_projection": "support_candidate_graph",
                        "node_kind": "support_node",
                        "tier": "support_candidate",
                    }
                ],
                edges_to_add=[
                    {
                        "edge_type": "EVIDENCES",
                        "source": "node:c",
                        "target": "node:a",
                    }
                ],
                phase="1545p-Fix59b-test",
                dry_run=True,
            )
        )
        assert receipt["mutated"] is False
        assert receipt["accepted_node_count"] == 1
        assert receipt["accepted_edge_count"] == 1
        assert writer.inspect()["node_count"] == 2
        assert writer.inspect()["edge_count"] == 1
    finally:
        writer.close()


def test_safe_writer_rejects_dangling_edge_without_materialized_endpoint(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                edges_to_add=[
                    {
                        "edge_type": "TESTS",
                        "source": "node:a",
                        "target": "node:missing",
                    }
                ],
                phase="1545p-Fix59b-test",
                dry_run=False,
            )
        )
        assert receipt["rejected_edge_count"] == 1
        assert receipt["rejected_edges"][0]["reason"] == "target_node_missing"
        assert receipt["accepted_edge_count"] == 0
        assert writer.inspect()["edge_count"] == 1
        assert writer.inspect()["invariants"]["no_dangling_edges"] is True
    finally:
        writer.close()


def test_safe_writer_applies_edge_ids_and_rebuilds_payload_and_indexes(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        receipt = writer.apply_plan(
            AtlasLmdbWritePlan(
                nodes_to_add=[
                    {
                        "candidate_id": "node:c",
                        "graph_projection": "support_candidate_graph",
                        "node_kind": "test_file",
                        "source_path": "tests/test_c.py",
                        "tier": "support_candidate",
                    }
                ],
                edges_to_add=[
                    {
                        "edge_type": "TESTS",
                        "source": "node:c",
                        "target": "node:a",
                    }
                ],
                phase="1545p-Fix59b-test",
                dry_run=False,
            )
        )
        expected = deterministic_edge_id("node:c", "TESTS", "node:a")
        assert receipt["mutated"] is True
        assert receipt["accepted_edges"][0]["edge_id"] == expected
        inspection = writer.inspect()
        assert inspection["node_count"] == 3
        assert inspection["edge_count"] == 2
        assert inspection["invariants"]["payload_node_count_matches_rows"] is True
        assert inspection["invariants"]["payload_edge_count_matches_rows"] is True
        assert inspection["invariants"]["tier_index_matches_rows"] is True
        assert inspection["invariants"]["tier_group_index_matches_rows"] is True
        assert inspection["invariants"]["source_path_index_matches_rows"] is True
    finally:
        writer.close()


def test_phase_file_registration_helper_materializes_required_endpoints(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        receipt = writer.register_phase_files(
            "1545p-Fix59b",
            [
                AtlasPhaseFileRegistration(
                    path="docs/phases/example_walkthrough.md",
                    node_kind="phase_walkthrough",
                    graph_projection="support_candidate_graph",
                    required_edges=(("EVIDENCES", "phase:1545p_fix59b"),),
                )
            ],
            dry_run=False,
        )
        file_id = repo_file_ref_id("docs/phases/example_walkthrough.md")
        assert receipt["accepted_node_count"] == 3
        assert receipt["rejected_edge_count"] == 0
        store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
        try:
            nodes = {node["candidate_id"]: node for node in store.iter_nodes()}
            edges = {(edge["source"], edge["edge_type"], edge["target"]) for edge in store.iter_edges()}
        finally:
            store.close()
        assert file_id in nodes
        assert "phase:1545p_fix59b" in nodes
        assert DEFAULT_PUBLIC_PATH_POLICY in nodes
        assert (file_id, "CLASSIFIED_BY", DEFAULT_PUBLIC_PATH_POLICY) in edges
        assert (file_id, "EVIDENCES", "phase:1545p_fix59b") in edges
    finally:
        writer.close()


def test_phase_file_registration_can_skip_generic_carries_forward_edge(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        receipt = writer.register_phase_files(
            "1545p-Fix59b",
            [
                AtlasPhaseFileRegistration(
                    path="docs/phases/no_generic_carry_forward.md",
                    node_kind="phase_walkthrough",
                    graph_projection="support_candidate_graph",
                    required_edges=(("EVIDENCES", "phase:1545p_fix59b"),),
                    skip_carries_forward=True,
                )
            ],
            dry_run=False,
        )
        file_id = repo_file_ref_id("docs/phases/no_generic_carry_forward.md")
        assert receipt["rejected_edge_count"] == 0
        store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
        try:
            edges = {(edge["source"], edge["edge_type"], edge["target"]) for edge in store.iter_edges()}
        finally:
            store.close()
        assert (file_id, "EVIDENCES", "phase:1545p_fix59b") in edges
        assert (file_id, "CARRIES_FORWARD", "phase:1545p_fix59b") not in edges
    finally:
        writer.close()


def test_repo_file_ref_id_fully_collapses_repeated_underscores() -> None:
    assert repo_file_ref_id("docs//phases/weird--name..md") == (
        "repo:file_ref:docs_phases_weird_name_md"
    )
