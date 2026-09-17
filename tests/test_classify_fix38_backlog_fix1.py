import json
from pathlib import Path

import lmdb
import pytest

from tools.materialize import classify_fix38_backlog as classifier


class _FakeAtlas:
    def __init__(self, path: Path) -> None:
        self.path = path

    def counts_and_manifest(self) -> tuple[int, int, str]:
        return 10, 20, "test-materialization"

    def node_ids_by_source_paths(self, source_paths: tuple[str, ...]) -> dict[str, list[str]]:
        return {
            path: ["node:registered"] if path.startswith("docs/registered") else []
            for path in source_paths
        }

    def close(self) -> None:
        return None


def _write_ledger(path: Path, annotations: list[dict]) -> None:
    path.write_text(json.dumps({"annotations": annotations}), encoding="utf-8")


def test_fix1_report_exposes_raw_unique_counts_and_merged_duplicate_edges(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(classifier, "ReadOnlyAtlas", _FakeAtlas)
    ledger_path = tmp_path / "ledger.json"
    _write_ledger(
        ledger_path,
        [
            {
                "annotation_batch": "batch-a",
                "repo_path": "docs/specs/a.md",
                "recommended_graph_action": "support_only",
                "proposed_semantic_edges": [
                    {"edge_type": "SOURCE_TREE_MEMBER", "target": "genesis:genesis_root_v0.4"},
                    {"edge_type": "EVIDENCES", "target": "phase:a"},
                ],
                "proposed_authority_trace_edges": [
                    {"edge_type": "REFERENCES_AUTHORITY", "target": "cdl:CDL-098"}
                ],
                "proposed_trace_roles": ["SOURCE_TREE_MEMBER", "EVIDENCES"],
            },
            {
                "annotation_batch": "batch-b",
                "repo_path": "docs/specs/a.md",
                "recommended_graph_action": "load_bearing_artifact_changed",
                "proposed_semantic_edges": [
                    {"edge_type": "SOURCE_TREE_MEMBER", "target": "genesis:genesis_root_v0.4"},
                    {"edge_type": "TESTS", "target": "tests/test_a.py"},
                ],
                "proposed_authority_trace_edges": [
                    {"edge_type": "REFERENCES_AUTHORITY", "target": "cdl:CDL-098"}
                ],
                "proposed_trace_roles": ["SOURCE_TREE_MEMBER", "TESTS"],
            },
            {
                "annotation_batch": "batch-c",
                "repo_path": "docs/registered/b.md",
                "recommended_graph_action": "support_only",
                "proposed_semantic_edges": [
                    {"edge_type": "SOURCE_TREE_MEMBER", "target": "genesis:genesis_root_v0.4"}
                ],
            },
            {
                "annotation_batch": "batch-d",
                "repo_path": "docs/registered/b.md",
                "recommended_graph_action": "support_only",
                "proposed_semantic_edges": [
                    {"edge_type": "SOURCE_TREE_MEMBER", "target": "genesis:genesis_root_v0.4"}
                ],
            },
            {
                "annotation_batch": "batch-e",
                "repo_path": "out/generated.json",
                "recommended_graph_action": "support_only",
                "proposed_semantic_edges": [],
            },
            {
                "annotation_batch": "batch-f",
                "repo_path": "out/generated.json",
                "recommended_graph_action": "support_only",
                "proposed_semantic_edges": [],
            },
        ],
    )

    report = classifier.classify(ledger_path, tmp_path / "atlas.lmdb")

    assert report["ledger_total_entries"] == 6
    assert report["ledger_unique_path_count"] == 3
    assert report["ledger_duplicate_entry_count"] == 3
    assert report["already_registered_count"] == 2
    assert report["already_registered_unique_count"] == 1
    assert report["already_registered_duplicate_entry_count"] == 1
    assert report["out_excluded_count"] == 2
    assert report["out_excluded_unique_count"] == 1
    assert report["out_excluded_duplicate_entry_count"] == 1
    assert report["not_registered_count"] == 2
    assert report["not_registered_unique_count"] == 1
    assert report["duplicate_entry_count"] == 1
    assert report["reconciliation_output_token"] == classifier.RECONCILIATION_OUTPUT_TOKEN

    [unique_entry] = report["not_registered_unique_entries"]
    assert unique_entry["repo_path"] == "docs/specs/a.md"
    assert unique_entry["annotation_batches"] == ["batch-a", "batch-b"]
    assert unique_entry["recommended_graph_actions"] == [
        "support_only",
        "load_bearing_artifact_changed",
    ]
    assert unique_entry["duplicate_metadata_conflict"] is True
    assert report["not_registered_duplicate_metadata_conflict_paths"] == ["docs/specs/a.md"]
    assert unique_entry["proposed_semantic_edges"] == [
        {"edge_type": "SOURCE_TREE_MEMBER", "target": "genesis:genesis_root_v0.4"},
        {"edge_type": "EVIDENCES", "target": "phase:a"},
        {"edge_type": "TESTS", "target": "tests/test_a.py"},
    ]


def _put_json(txn: lmdb.Transaction, db: object, key: str, payload: object) -> None:
    txn.put(key.encode("utf-8"), json.dumps(payload).encode("utf-8"), db=db)


def _atlas_env(path: Path) -> lmdb.Environment:
    env = lmdb.open(str(path), subdir=True, map_size=4 * 1024 * 1024, max_dbs=32)
    nodes = env.open_db(b"nodes")
    env.open_db(b"edges")
    meta = env.open_db(b"meta")
    env.open_db(b"nodes_by_source_path")
    with env.begin(write=True) as txn:
        _put_json(txn, meta, "materialization_manifest", {"materialization_phase": "test"})
        _put_json(txn, nodes, "node:present", {"candidate_id": "node:present"})
    return env


def test_readonly_atlas_rejects_malformed_source_path_index(tmp_path: Path) -> None:
    atlas_path = tmp_path / "atlas.lmdb"
    env = _atlas_env(atlas_path)
    source_path_db = env.open_db(b"nodes_by_source_path")
    with env.begin(write=True) as txn:
        _put_json(txn, source_path_db, "docs/specs/bad.md", ["node:present", 7])
    env.close()

    atlas = classifier.ReadOnlyAtlas(atlas_path)
    try:
        with pytest.raises(RuntimeError, match="source_path_index_contains_non_string"):
            atlas.node_ids_by_source_paths(("docs/specs/bad.md",))
    finally:
        atlas.close()


def test_readonly_atlas_rejects_dangling_source_path_index(tmp_path: Path) -> None:
    atlas_path = tmp_path / "atlas.lmdb"
    env = _atlas_env(atlas_path)
    source_path_db = env.open_db(b"nodes_by_source_path")
    with env.begin(write=True) as txn:
        _put_json(txn, source_path_db, "docs/specs/dangling.md", ["node:missing"])
    env.close()

    atlas = classifier.ReadOnlyAtlas(atlas_path)
    try:
        with pytest.raises(RuntimeError, match="source_path_index_dangling_node_id"):
            atlas.node_ids_by_source_paths(("docs/specs/dangling.md",))
    finally:
        atlas.close()
