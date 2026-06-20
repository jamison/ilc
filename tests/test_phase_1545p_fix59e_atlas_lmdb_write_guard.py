from __future__ import annotations

import json
import re
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter


STATUS_PATH = Path("docs/phases/STATUS.md")
FIX59E_PROMPT = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1545p_fix59_g10_atlas_lmdb_phase_tool_migration_fix59e.md"
)
FIX60_PROMPT = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1545p_fix60_g10_edge_id_and_preimage_debt.md"
)
WRITER_PATH = Path("ilc_core/storage/genesis_atlas_lmdb_writer.py")
ATLAS_CLI_PATH = Path("ilc_core/cli/atlas_lmdb_cli.py")

RAW_WRITE_RE = re.compile(
    r"\.put_nodes\(|\.put_edges\(|\.put_graph_payload\(|\.put_meta\(|\.put_preimages\("
)

HISTORICAL_EXECUTED_TOOL_ALLOWLIST = {
    "tools/evaluators/sim_genesis_atlas_fix23_lmdb_materialization.py",
    "tools/evaluators/sim_genesis_atlas_lmdb_materialization_1545p_fix23.py",
    "tools/evaluators/sim_genesis_base_graph_lmdb_rematerialization_1545p_fix41.py",
    "tools/evaluators/sim_genesis_base_graph_unified_lmdb_materialization.py",
    "tools/evaluators/sim_genesis_atlas_fix55_lmdb_graph_projection_classification.py",
    "tools/evaluators/sim_genesis_atlas_fix57_fiedler_minority_manual_bridge_edges.py",
    "tools/evaluators/sim_genesis_atlas_fix58_fix48_residual_semantic_queue.py",
    "tools/evaluators/sim_genesis_atlas_fix59_missing_target_materialization.py",
    "tools/evaluators/sim_genesis_atlas_fix59a_deferred_repair_reconcile.py",
}


def _seed_missing_edge_id_lmdb(root: Path) -> None:
    nodes = [
        {
            "candidate_id": "node:a",
            "graph_delta": "support_only",
            "graph_projection": "support_candidate_graph",
            "node_kind": "support_node",
            "tier": "support_candidate",
        },
        {
            "candidate_id": "node:b",
            "graph_delta": "support_only",
            "graph_projection": "support_candidate_graph",
            "node_kind": "support_node",
            "tier": "support_candidate",
        },
    ]
    edge = {
        "edge_type": "TESTS",
        "source": "node:a",
        "src": "node:a",
        "target": "node:b",
        "tgt": "node:b",
    }
    store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
    try:
        store.put_nodes(nodes)
        store.put_edges([edge])
        store.put_graph_payload({"nodes": nodes, "edges": [edge]})
    finally:
        store.close()


def test_fix59e_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix59e_phase_tools_migrated_to_safe_writer" in text
    assert "fix59e_raw_lmdb_write_guard_committed" in text
    assert "fix59e_fix60_prompt_updated_for_safe_writer" in text
    assert "fix59e_complete" in text


def test_fix59e_prompt_and_writer_surface_are_present() -> None:
    prompt = FIX59E_PROMPT.read_text(encoding="utf-8")
    writer = WRITER_PATH.read_text(encoding="utf-8")
    assert "Fix59e Atlas LMDB Phase Tool Migration" in prompt
    assert "## LMDB Node Registration" in prompt
    assert "def repair_missing_edge_ids(" in writer
    assert "def write_preimages(" in writer
    assert "def write_metadata(" in writer


def test_fix60_prompt_requires_safe_writer_and_not_raw_adapter_writes() -> None:
    text = FIX60_PROMPT.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in text
    assert "writer.repair_missing_edge_ids" in text
    assert "writer.write_preimages" in text
    assert "writer.write_metadata" in text
    assert "store.put_edges(" not in text
    assert "store.put_preimages(" not in text
    assert "store.put_meta(" not in text


def test_future_evaluator_raw_lmdb_writes_are_allowlisted() -> None:
    offenders: set[str] = set()
    for path in sorted(Path("tools/evaluators").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if RAW_WRITE_RE.search(text):
            offenders.add(path.as_posix())
    assert offenders <= HISTORICAL_EXECUTED_TOOL_ALLOWLIST


def test_atlas_cli_does_not_call_raw_adapter_writes() -> None:
    text = ATLAS_CLI_PATH.read_text(encoding="utf-8")
    assert ".put_nodes(" not in text
    assert ".put_edges(" not in text
    assert ".put_graph_payload(" not in text
    assert ".put_meta(" not in text
    assert ".put_preimages(" not in text
    assert "AtlasLmdbSafeWriter" in text


def test_safe_writer_edge_id_repair_replaces_without_duplicate_rows(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_missing_edge_id_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        dry_run = writer.repair_missing_edge_ids(phase="1545p-Fix59e-test", dry_run=True)
        assert dry_run["mutated"] is False
        assert dry_run["repaired_edge_count"] == 1
        assert writer.inspect()["edge_count"] == 1

        receipt = writer.repair_missing_edge_ids(phase="1545p-Fix59e-test", dry_run=False)
        assert receipt["status"] == "PASS"
        assert receipt["mutated"] is True
        assert receipt["repaired_edge_count"] == 1
        inspection = writer.inspect()
        assert inspection["edge_count"] == 1
        assert inspection["edge_id_debt_count"] == 0
        assert inspection["invariants"]["payload_edge_count_matches_rows"] is True
    finally:
        writer.close()


def test_safe_writer_preimages_and_metadata_are_wrapped(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_missing_edge_id_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        node_preimage = {
            "canonical_sha256": "0" * 64,
            "fields": {"candidate_id": "node:a"},
            "node_id": "node:a",
            "preimage_version": "v0.4",
        }
        edge_preimage = {
            "canonical_sha256": "1" * 64,
            "edge_id": "edge:test",
            "fields": {"edge_id": "edge:test"},
            "preimage_version": "v0.4",
        }
        receipt = writer.write_preimages(
            [node_preimage, edge_preimage],
            phase="1545p-Fix59e-test",
            dry_run=False,
            metadata={"scope": "test"},
        )
        assert receipt["status"] == "PASS"
        assert receipt["post_preimage_count"] == 2
        assert writer.store.get_preimage("node:a") == node_preimage
        assert writer.store.get_preimage("edge:test") == edge_preimage

        meta_receipt = writer.write_metadata(
            "fix59e_test_metadata",
            {"ok": True},
            phase="1545p-Fix59e-test",
            dry_run=False,
        )
        assert meta_receipt["status"] == "PASS"
        assert writer.store.get_meta("fix59e_test_metadata") == {"ok": True}
    finally:
        writer.close()


def test_fix59e_walkthrough_exists_and_has_no_ellipses() -> None:
    path = Path("docs/phases/phase_1545p_fix59e_atlas_lmdb_phase_tool_migration_walkthrough.md")
    text = path.read_text(encoding="utf-8")
    assert "Raw Write Search Table" in text
    assert "historical_executed" in text
    assert "..." not in text
