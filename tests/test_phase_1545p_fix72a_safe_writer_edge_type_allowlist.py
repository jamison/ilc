from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    deterministic_edge_id,
)


def _node(candidate_id: str, *, node_kind: str = "support_node") -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "node_kind": node_kind,
        "tier": "support_candidate",
    }


def _edge(source: str, edge_type: str, target: str) -> dict[str, str]:
    return {
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "source": source,
        "target": target,
    }


def _writer(root: Path) -> AtlasLmdbSafeWriter:
    return AtlasLmdbSafeWriter(root / "atlas.lmdb")


def test_reject_unknown_edge_type(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("repo:file:abc:x"), _node("cdl:001", node_kind="cdl_node")],
            edges_to_add=[_edge("repo:file:abc:x", "MADE_UP_TYPE", "cdl:001")],
            dry_run=True,
        )
        with pytest.raises(ValueError, match="unknown_edge_type_rejected"):
            writer.validate_plan(plan)
    finally:
        writer.close()


def test_reject_repo_file_governs_authority(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("repo:file:abc:x"), _node("cdl:001", node_kind="cdl_node")],
            edges_to_add=[_edge("repo:file:abc:x", "GOVERNS", "cdl:001")],
            dry_run=True,
        )
        with pytest.raises(ValueError, match="governs_source_not_authority_like"):
            writer.validate_plan(plan)
    finally:
        writer.close()


def test_accept_authority_governs_support_node(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("cdl:001", node_kind="cdl_node"), _node("invariant:example")],
            edges_to_add=[_edge("cdl:001", "GOVERNS", "invariant:example")],
            dry_run=True,
        )
        receipt = writer.validate_plan(plan)
        assert receipt["status"] == "PASS"
        assert len(receipt["accepted_edges"]) == 1
    finally:
        writer.close()


def test_accept_file_ref_same_source_repo_file(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[
                _node("repo:file_ref:ilc_core_module_py"),
                _node("repo:file:abc123:ilc_core_module_py"),
            ],
            edges_to_add=[
                _edge(
                    "repo:file_ref:ilc_core_module_py",
                    "SAME_SOURCE",
                    "repo:file:abc123:ilc_core_module_py",
                )
            ],
            dry_run=True,
        )
        assert writer.validate_plan(plan)["status"] == "PASS"
    finally:
        writer.close()


def test_reject_same_source_reversed(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[
                _node("repo:file_ref:ilc_core_module_py"),
                _node("repo:file:abc123:ilc_core_module_py"),
            ],
            edges_to_add=[
                _edge(
                    "repo:file:abc123:ilc_core_module_py",
                    "SAME_SOURCE",
                    "repo:file_ref:ilc_core_module_py",
                )
            ],
            dry_run=True,
        )
        with pytest.raises(ValueError, match="same_source_requires_file_ref_to_repo_file"):
            writer.validate_plan(plan)
    finally:
        writer.close()


def test_accept_references_authority_to_cdl(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("repo:file:abc:x"), _node("cdl:042", node_kind="cdl_node")],
            edges_to_add=[_edge("repo:file:abc:x", "REFERENCES_AUTHORITY", "cdl:042")],
            dry_run=True,
        )
        assert writer.validate_plan(plan)["status"] == "PASS"
    finally:
        writer.close()


def test_reject_references_authority_to_repo(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("repo:file:abc:x"), _node("repo:file:def:y")],
            edges_to_add=[_edge("repo:file:abc:x", "REFERENCES_AUTHORITY", "repo:file:def:y")],
            dry_run=True,
        )
        with pytest.raises(ValueError, match="references_authority_target_must_not_be_repo"):
            writer.validate_plan(plan)
    finally:
        writer.close()


def test_override_requires_migration_phase(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("repo:file:abc:x"), _node("cdl:001", node_kind="cdl_node")],
            edges_to_add=[_edge("repo:file:abc:x", "GOVERNS", "cdl:001")],
            metadata={"allowlist_override": True},
            dry_run=True,
        )
        with pytest.raises(ValueError, match="allowlist_override_requires_migration_phase"):
            writer.validate_plan(plan)
    finally:
        writer.close()


def test_override_with_migration_phase_accepts_historical_repair(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("repo:file:abc:x"), _node("cdl:001", node_kind="cdl_node")],
            edges_to_add=[_edge("repo:file:abc:x", "GOVERNS", "cdl:001")],
            metadata={
                "allowlist_override": True,
                "allowlist_override_reason": "historical repair edge from pre-allowlist phase",
                "migration_phase": "phase_1545p_fix_historical",
            },
            dry_run=True,
        )
        assert writer.validate_plan(plan)["status"] == "PASS"
    finally:
        writer.close()


def test_classified_by_fanin_cap_enforced(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        hub = _node("policy:classification_hub", node_kind="policy_support_node")
        sources = [_node(f"repo:file:{index}:x") for index in range(101)]
        writer.store.put_nodes([hub, *sources])
        existing_edges = [
            _edge(source["candidate_id"], "CLASSIFIED_BY", hub["candidate_id"])
            for source in sources[:100]
        ]
        writer.store.put_edges(existing_edges)
        writer.store.put_graph_payload({"edges": existing_edges, "nodes": [hub, *sources]})
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[sources[100]],
            edges_to_add=[_edge(sources[100]["candidate_id"], "CLASSIFIED_BY", hub["candidate_id"])],
            dry_run=True,
        )
        with pytest.raises(ValueError, match="classified_by_fanin_cap_exceeded"):
            writer.validate_plan(plan)
    finally:
        writer.close()


def test_validate_blocks_apply_on_invalid_edge_before_mutation(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_node("repo:file:abc:x"), _node("cdl:001", node_kind="cdl_node")],
            edges_to_add=[_edge("repo:file:abc:x", "GOVERNS", "cdl:001")],
            dry_run=False,
        )
        with pytest.raises(ValueError, match="governs_source_not_authority_like"):
            writer.apply_plan(plan)
        assert writer.store.iter_edges() == []
        assert writer.store.iter_nodes() == []
    finally:
        writer.close()


def test_duplicate_semantic_edge_dedupe_keeps_richest_metadata(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    try:
        nodes = [_node("node:a"), _node("node:b")]
        sparse = {
            "edge_id": "edge:z_sparse",
            "edge_type": "TESTS",
            "source": "node:a",
            "target": "node:b",
        }
        rich = {
            "annotation_phase": "phase_test",
            "candidate_status": "canonical_test_edge",
            "confidence": "0.9",
            "edge_id": "edge:a_rich",
            "edge_type": "TESTS",
            "evidence": "tests/example.py:1",
            "source": "node:a",
            "target": "node:b",
        }
        writer.store.put_nodes(nodes)
        writer.store.put_edges([sparse, rich])
        writer.store.put_graph_payload({"edges": [sparse, rich], "nodes": nodes})
        receipt = writer.dedupe_semantic_edges(phase="1545p-Fix72a-test", dry_run=False)
        assert receipt["status"] == "PASS"
        assert receipt["removed_duplicate_rows"] == 1
        assert writer.store.iter_edges()[0]["edge_id"] == "edge:a_rich"
        assert writer.inspect()["duplicate_semantic_edge_extra_row_count"] == 0
    finally:
        writer.close()
